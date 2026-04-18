"""Reference CLI host smoke tests.

Feeds scripted `FakeTeam` scripts through `run_cli(InProcessSession(...))`
and asserts that rendered output contains the expected lines. Covers:
text, tool_call, state, question (with stdin reply), error, and
result events.
"""
from __future__ import annotations

import asyncio
import io

import pytest

from services.integration_surface import (
    InProcessSession,
    run_cli,
)

from .fixtures.fake_team import FakeTeam


@pytest.fixture
def run_async():
    def runner(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    return runner


def test_text_and_result_render(run_async):
    fake = FakeTeam().reply(
        ("text", {"text": "hello"}),
        ("result", {"stop_reason": "end_turn"}),
    )
    session = InProcessSession(fake)
    out = io.StringIO()
    inp = io.StringIO("")

    rc = run_async(
        run_cli(
            session, team="t", prompt="hi",
            input_stream=inp, output_stream=out,
        )
    )
    assert rc == 0
    assert "hello" in out.getvalue()


def test_error_exits_with_code_2(run_async):
    fake = FakeTeam().reply(("error", {"message": "boom"}))
    session = InProcessSession(fake)
    out = io.StringIO()
    inp = io.StringIO("")

    rc = run_async(
        run_cli(
            session, team="t", prompt="hi",
            input_stream=inp, output_stream=out,
        )
    )
    assert rc == 2
    assert "boom" in out.getvalue()


def test_question_is_prompted_and_answered(run_async):
    fake = FakeTeam().reply_with_question(
        [("text", {"text": "thinking..."})],
        ("q1", "user", "what's your name?"),
        [("text", {"text": "nice"}),
         ("result", {"stop_reason": "end_turn"})],
    )
    session = InProcessSession(fake)
    out = io.StringIO()
    inp = io.StringIO("Mike\n")

    rc = run_async(
        run_cli(
            session, team="t", prompt="hi",
            input_stream=inp, output_stream=out,
        )
    )
    assert rc == 0
    rendered = out.getvalue()
    assert "what's your name?" in rendered
    assert "nice" in rendered


def test_tool_call_and_state_events_render(run_async):
    fake = FakeTeam().reply(
        ("state", {"phase": "starting"}),
        ("tool_call", {"name": "Read", "status": "running"}),
        ("tool_call", {"name": "Read", "status": "succeeded"}),
        ("result", {"stop_reason": "end_turn"}),
    )
    session = InProcessSession(fake)
    out = io.StringIO()
    inp = io.StringIO("")

    rc = run_async(
        run_cli(
            session, team="t", prompt="hi",
            input_stream=inp, output_stream=out,
        )
    )
    assert rc == 0
    rendered = out.getvalue()
    assert "starting" in rendered
    assert "Read" in rendered
