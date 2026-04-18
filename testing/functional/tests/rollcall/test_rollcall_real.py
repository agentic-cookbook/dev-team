"""Real-LLM rollcall smoke against teams/puppynamingteam/.

Gated by AGENTIC_REAL_LLM_SMOKE=1. When the gate is set and the `claude`
CLI is on PATH, this spawns `claude -p` once per discovered role and
verifies that every role responds without error. The rollcall
orchestrator and integration surface are exercised against a real
subprocess runner; no LLM response content is asserted — a non-empty
response plus a clean exit is the smoke.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from services.integration_surface import InProcessSession
from services.rollcall import (
    RollCallResult,
    discover_team,
    roll_call,
)


def _make_claude_runner(claude_bin: str):
    """Return a TeamRunner that shells out to `claude -p <prompt>`.

    Emits `state: starting`, one `text` event containing claude's stdout,
    and a terminal `result` event. On non-zero exit, emits an `error`
    event with the stderr tail so the rollcall orchestrator surfaces it.
    """

    async def _runner(io, user_turn, ctx):
        await io.emit("state", {"phase": "starting"})
        proc = await asyncio.create_subprocess_exec(
            claude_bin,
            "-p",
            user_turn,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_b, stderr_b = await proc.communicate()
        stdout = stdout_b.decode("utf-8", errors="replace").strip()
        stderr = stderr_b.decode("utf-8", errors="replace").strip()
        if proc.returncode != 0:
            await io.emit(
                "error",
                {
                    "kind": "subprocess",
                    "message": f"claude exit {proc.returncode}: {stderr[-200:]}",
                    "retryable": False,
                },
            )
            return
        if stdout:
            await io.emit("text", {"text": stdout})
        await io.emit("result", {"stop_reason": "end_turn"})

    return _runner


def test_rollcall_real_puppy_team(claude_bin: str, puppy_team_root: Path):
    roles = discover_team(puppy_team_root)
    assert roles, "expected at least one role in puppynamingteam"

    runner = _make_claude_runner(claude_bin)
    session = InProcessSession(runner)
    results: list[RollCallResult] = asyncio.run(
        roll_call(session, roles, concurrency=2, timeout=120.0)
    )

    assert len(results) == len(roles)
    failures = [r for r in results if r.error is not None]
    assert not failures, (
        "rollcall failures: "
        + "; ".join(
            f"{r.role.kind}:{r.role.name} -> {r.error.kind}: {r.error.message}"
            for r in failures
        )
    )
    for r in results:
        assert r.response.strip(), (
            f"empty response from {r.role.kind}:{r.role.name}"
        )
