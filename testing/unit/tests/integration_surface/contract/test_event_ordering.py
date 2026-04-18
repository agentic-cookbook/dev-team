"""Seq is monotonic, zero-based, no gaps, no duplicates within a session."""
from __future__ import annotations

from ..fixtures.fake_team import FakeTeam


def test_seq_starts_at_zero_and_increments(
    transport_factory, run_async, collect_events
):
    fake = FakeTeam().reply(
        ("text", {"text": "a"}),
        ("text", {"text": "b"}),
        ("text", {"text": "c"}),
        ("result", {"stop_reason": "end_turn"}),
    )
    session = transport_factory(fake)

    async def scenario():
        h = await session.start(team="t")
        await session.send(h.session_id, "go")
        events = await collect_events(session, h.session_id)
        seqs = [e.seq for e in events]
        assert seqs == list(range(len(events)))
        await session.close(h.session_id)

    run_async(scenario())


def test_seq_continues_across_turns(
    transport_factory, run_async, collect_events
):
    fake = FakeTeam().reply(
        ("text", {"text": "one"}),
        ("result", {"stop_reason": "end_turn"}),
    )
    session = transport_factory(fake)

    async def scenario():
        h = await session.start(team="t")
        await session.send(h.session_id, "first")
        first = await collect_events(session, h.session_id)
        await session.send(h.session_id, "second")
        second = await collect_events(session, h.session_id)
        all_seqs = [e.seq for e in first + second]
        assert all_seqs == list(range(len(all_seqs)))
        await session.close(h.session_id)

    run_async(scenario())


def test_all_events_tagged_with_session_id(
    transport_factory, run_async, collect_events
):
    fake = FakeTeam().reply(
        ("text", {"text": "x"}),
        ("result", {"stop_reason": "end_turn"}),
    )
    session = transport_factory(fake)

    async def scenario():
        h = await session.start(team="t")
        await session.send(h.session_id, "hi")
        events = await collect_events(session, h.session_id)
        assert all(e.session_id == h.session_id for e in events)
        await session.close(h.session_id)

    run_async(scenario())
