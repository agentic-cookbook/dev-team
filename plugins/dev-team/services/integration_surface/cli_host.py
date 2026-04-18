"""Reference CLI host.

A tiny renderer that consumes any `TeamSession` and drives it from a
terminal: starts a session, prints protocol events as they arrive,
prompts the user on `question` events, and exits cleanly on `result`
or `error`. Hosts that need richer rendering (web UIs, dashboards)
should implement their own consumer — this file is the reference
shape.
"""
from __future__ import annotations

import asyncio
import sys
from typing import IO

from .protocol import Event, SessionOptions, TeamSession


async def run_cli(
    session: TeamSession,
    team: str,
    *,
    prompt: str | None = None,
    options: SessionOptions | None = None,
    input_stream: IO[str] | None = None,
    output_stream: IO[str] | None = None,
) -> int:
    """Host one TeamSession from the terminal.

    Returns the process-style exit code: 0 on clean `result`, 2 if any
    `error` event is seen. `prompt` is passed through to `session.start`
    as the first user turn; if omitted, no turn is sent until a question
    prompts one.
    """
    out = output_stream or sys.stdout
    inp = input_stream or sys.stdin

    handle = await session.start(team=team, prompt=prompt, options=options)
    saw_error = False

    async def pump_events() -> int:
        nonlocal saw_error
        async for ev in session.events(handle.session_id):
            code = await _render_event(session, handle.session_id, ev, out, inp)
            if code is not None:
                return code
            if ev.type == "error":
                saw_error = True
        return 2 if saw_error else 0

    try:
        return await pump_events()
    finally:
        await session.close(handle.session_id)


async def _render_event(
    session: TeamSession,
    session_id: str,
    ev: Event,
    out: IO[str],
    inp: IO[str],
) -> int | None:
    """Render one event. Returns an exit code to stop the loop, or None
    to keep going."""
    if ev.type == "text":
        text = ev.payload.get("text", "")
        if text:
            out.write(text)
            if not text.endswith("\n"):
                out.write("\n")
            out.flush()
        return None
    if ev.type == "thinking":
        text = ev.payload.get("text", "")
        if text:
            out.write(f"\x1b[2m[thinking] {text}\x1b[0m\n")
            out.flush()
        return None
    if ev.type == "tool_call":
        name = ev.payload.get("name", "?")
        status = ev.payload.get("status", "?")
        out.write(f"\x1b[2m[tool:{name}] {status}\x1b[0m\n")
        out.flush()
        return None
    if ev.type == "state":
        phase = ev.payload.get("phase", "?")
        out.write(f"\x1b[2m[{phase}]\x1b[0m\n")
        out.flush()
        return None
    if ev.type == "question":
        await _ask_user(session, session_id, ev, out, inp)
        return None
    if ev.type == "error":
        msg = ev.payload.get("message", "error")
        out.write(f"\x1b[31m[error] {msg}\x1b[0m\n")
        out.flush()
        return 2
    if ev.type == "result":
        stop = ev.payload.get("stop_reason", "")
        if stop and stop != "end_turn":
            out.write(f"\x1b[2m[result: {stop}]\x1b[0m\n")
            out.flush()
        return 0
    return None


async def _ask_user(
    session: TeamSession,
    session_id: str,
    ev: Event,
    out: IO[str],
    inp: IO[str],
) -> None:
    question_id = ev.payload.get("question_id") or ""
    prompt = ev.payload.get("prompt", "")
    options = ev.payload.get("options") or []
    target = ev.payload.get("target")

    label = f"? {prompt}"
    if target:
        label = f"? [{target}] {prompt}"
    out.write(f"\n{label}\n")
    if options:
        out.write(f"  (options: {'/'.join(options)})\n")
    out.write("> ")
    out.flush()

    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, inp.readline)
    answer = (answer or "").strip()
    if not answer and options:
        answer = options[0]
    await session.answer(session_id, question_id, answer)
