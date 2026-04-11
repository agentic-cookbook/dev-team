"""Golden replay regression guard.

Runs name-a-puppy deterministically against MockDispatcher, dumps the
resulting row state from every resource table, normalizes volatile fields
(UUIDs, timestamps, auto-generated IDs), and diffs against a committed
golden fixture at `testing/fixtures/golden_sessions/name_a_puppy.json`.

If the golden file is missing, the first run writes it and fails loudly —
the author then reviews the generated file and commits it. Subsequent
runs diff against it. Any drift in conductor row state (new columns,
changed ordering, renamed events) makes this test fail with a printed
diff, forcing a conscious golden refresh.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from conftest import GOLDEN_DIR, PLAYBOOK_PATH  # type: ignore[import-not-found]

from services.conductor.arbitrator import Arbitrator
from services.conductor.arbitrator.backends import SqliteBackend
from services.conductor.conductor import Conductor
from services.conductor.dispatcher import MockDispatcher
from services.conductor.playbook import load_playbook
from services.conductor.team_lead import TeamLead


GOLDEN_PATH = GOLDEN_DIR / "name_a_puppy.json"

TABLES = [
    "session",
    "state",
    "message",
    "gate",
    "result",
    "event",
    "task",
    "request",
]

UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?")
DISPATCH_ID_RE = re.compile(r"(?:disp|judg)_[0-9a-f]{8}")
VOLATILE_KEYS = {
    "session_id",
    "node_id",
    "parent_node_id",
    "result_id",
    "finding_id",
    "message_id",
    "gate_id",
    "event_id",
    "task_id",
    "request_id",
    "dispatch_id",
    "created_at",
    "updated_at",
    "started_at",
    "ended_at",
    "enqueued_at",
    "resolved_at",
    "responded_at",
    "entered_at",
    "exited_at",
}


def _build_dispatcher() -> MockDispatcher:
    return MockDispatcher(
        {
            "team-lead-gather": {"next_state": "dispatch_specialists"},
            "team-lead-aggregator": {
                "ranked_candidates": [
                    "Luna",
                    "Scout",
                    "Rex",
                    "Daisy",
                    "Biscuit",
                ],
                "next_state": "present",
            },
            "breed-name-worker": {
                "candidates": ["Rex", "Dash", "Biscuit"]
            },
            "lifestyle-name-worker": {
                "candidates": ["Scout", "River", "Sage"]
            },
            "temperament-name-worker": {
                "candidates": ["Luna", "Daisy", "Ollie"]
            },
        }
    )


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        v = UUID_RE.sub("<uuid>", value)
        v = TS_RE.sub("<ts>", v)
        v = DISPATCH_ID_RE.sub("<dispatch_id>", v)
        return v
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def _scrub_row(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in row.items():
        if k in VOLATILE_KEYS:
            out[k] = "<redacted>" if v is not None else None
        else:
            out[k] = _normalize(v)
    return out


def _sort_key(row: dict) -> str:
    return json.dumps(row, sort_keys=True)


async def _dump_session(backend: SqliteBackend, session_id) -> dict:
    snapshot: dict[str, list] = {}
    for table in TABLES:
        rows = await backend.fetch_all(
            table, where={"session_id": str(session_id)}
        )
        scrubbed = [_scrub_row(r) for r in rows]
        # Parallel dispatches produce non-deterministic insertion order.
        # Sort by a canonical serialization so the golden diff is stable.
        # `event.sequence` is still preserved inside the row, so ordering
        # regressions are still detectable via field comparison.
        scrubbed.sort(key=_sort_key)
        snapshot[table] = scrubbed
    # finding has no session_id — join via result.result_id.
    result_rows = await backend.fetch_all(
        "result", where={"session_id": str(session_id)}
    )
    findings: list = []
    for r in result_rows:
        for f in await backend.fetch_all(
            "finding", where={"result_id": r["result_id"]}
        ):
            findings.append(_scrub_row(f))
    findings.sort(key=_sort_key)
    snapshot["finding"] = findings
    return snapshot


def test_golden_session_replay(tmp_path):
    async def _t():
        playbook = load_playbook(PLAYBOOK_PATH)
        backend = SqliteBackend(tmp_path / "arb.sqlite")
        arb = Arbitrator(backend)
        await arb.start()
        dispatcher = _build_dispatcher()
        team_lead = TeamLead(playbook)
        session_id = uuid4()
        conductor = Conductor(arb, dispatcher, team_lead, session_id)
        await conductor.run()
        snapshot = await _dump_session(backend, session_id)
        await arb.close()
        return snapshot

    snapshot = asyncio.run(_t())

    if not GOLDEN_PATH.exists():
        GOLDEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN_PATH.write_text(
            json.dumps(snapshot, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        pytest.fail(
            f"Golden fixture did not exist and was generated at "
            f"{GOLDEN_PATH}. Review it and commit, then rerun."
        )

    expected = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    if snapshot != expected:
        # Produce a compact diff for debugging.
        diff_lines: list[str] = []
        for table in TABLES:
            got = snapshot.get(table, [])
            want = expected.get(table, [])
            if got != want:
                diff_lines.append(
                    f"{table}: expected {len(want)} rows, got {len(got)}"
                )
                for i, (g, w) in enumerate(zip(got, want)):
                    if g != w:
                        diff_lines.append(f"  row {i}: {g!r} != {w!r}")
                if len(got) > len(want):
                    for i, g in enumerate(got[len(want):], start=len(want)):
                        diff_lines.append(f"  extra row {i}: {g!r}")
                elif len(want) > len(got):
                    for i, w in enumerate(want[len(got):], start=len(got)):
                        diff_lines.append(f"  missing row {i}: {w!r}")
        pytest.fail(
            "Golden session drift — regenerate by deleting "
            f"{GOLDEN_PATH} and rerunning if the change is intentional.\n"
            + "\n".join(diff_lines)
        )
