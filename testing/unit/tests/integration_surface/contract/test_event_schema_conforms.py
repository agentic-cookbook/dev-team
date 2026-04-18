"""Schema linter: 5 violation kinds + clean-run assertion."""
from __future__ import annotations

from services.integration_surface import Event, validate_event, validate_stream

from ..fixtures.fake_team import FakeTeam


# -- Lint-level tests (don't need a transport) ---------------------------------


def test_unknown_type_kind_1():
    violations = validate_event(
        Event(type="nope", session_id="s", seq=0, payload={})
    )
    assert [v.kind for v in violations] == [1]


def test_missing_required_kind_2():
    violations = validate_event(
        Event(type="text", session_id="s", seq=0, payload={})
    )
    assert [v.kind for v in violations] == [2]


def test_extra_field_kind_3():
    violations = validate_event(
        Event(
            type="text",
            session_id="s",
            seq=0,
            payload={"text": "hi", "bogus": 1},
        )
    )
    assert [v.kind for v in violations] == [3]


def test_bad_tool_status_kind_3():
    violations = validate_event(
        Event(
            type="tool_call",
            session_id="s",
            seq=0,
            payload={
                "tool_use_id": "t1",
                "name": "Bash",
                "status": "exploded",
            },
        )
    )
    assert any(v.kind == 3 and "status" in v.message for v in violations)


def test_bad_state_phase_kind_3():
    violations = validate_event(
        Event(
            type="state",
            session_id="s",
            seq=0,
            payload={"phase": "gargling"},
        )
    )
    assert any(v.kind == 3 and "phase" in v.message for v in violations)


def test_seq_gap_kind_4():
    stream = [
        Event(type="text", session_id="s", seq=0, payload={"text": "a"}),
        Event(type="text", session_id="s", seq=2, payload={"text": "b"}),
    ]
    violations = validate_stream(stream)
    assert any(v.kind == 4 for v in violations)


def test_duplicate_seq_kind_5():
    stream = [
        Event(type="text", session_id="s", seq=0, payload={"text": "a"}),
        Event(type="text", session_id="s", seq=0, payload={"text": "b"}),
    ]
    violations = validate_stream(stream)
    assert any(v.kind == 5 for v in violations)


def test_clean_stream_has_no_violations():
    stream = [
        Event(type="text", session_id="s", seq=0, payload={"text": "ok"}),
        Event(
            type="result",
            session_id="s",
            seq=1,
            payload={"stop_reason": "end_turn"},
        ),
    ]
    assert validate_stream(stream) == []


# -- Transport-parameterized: real emitted streams conform -------------------


def test_fake_team_stream_conforms(
    transport_factory, run_async, collect_events
):
    fake = FakeTeam().reply(
        ("text", {"text": "hello"}),
        ("tool_call", {
            "tool_use_id": "t1",
            "name": "Bash",
            "status": "running",
        }),
        ("tool_call", {
            "tool_use_id": "t1",
            "name": "Bash",
            "status": "succeeded",
            "output": "ok",
        }),
        ("result", {"stop_reason": "end_turn"}),
    )
    session = transport_factory(fake)

    async def scenario():
        h = await session.start(team="t")
        await session.send(h.session_id, "go")
        events = await collect_events(session, h.session_id)
        await session.close(h.session_id)
        return events

    events = run_async(scenario())
    assert validate_stream(events) == []
