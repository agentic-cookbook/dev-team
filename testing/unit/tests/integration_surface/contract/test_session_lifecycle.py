"""Session API contract: start / send / events / close / resume."""
from __future__ import annotations

import asyncio

from ..fixtures.fake_team import FakeTeam


def test_start_returns_handle_with_session_id(transport_factory, run_async):
    session = transport_factory(FakeTeam())

    async def scenario():
        handle = await session.start(team="t")
        assert handle.session_id
        assert handle.team == "t"
        await session.close(handle.session_id)

    run_async(scenario())


def test_send_triggers_event_stream(transport_factory, run_async, collect_events):
    fake = FakeTeam().reply(
        ("text", {"text": "hello world"}),
        ("result", {"stop_reason": "end_turn"}),
    )
    session = transport_factory(fake)

    async def scenario():
        h = await session.start(team="t")
        await session.send(h.session_id, "hi")
        events = await collect_events(session, h.session_id)
        types = [e.type for e in events]
        assert types == ["text", "result"]
        assert events[0].payload == {"text": "hello world"}
        await session.close(h.session_id)

    run_async(scenario())


def test_close_stops_event_stream(transport_factory, run_async):
    session = transport_factory(FakeTeam())

    async def scenario():
        h = await session.start(team="t")

        async def drain():
            events = []
            async for e in session.events(h.session_id):
                events.append(e)
            return events

        drainer = asyncio.create_task(drain())
        await asyncio.sleep(0)  # let task start
        await session.close(h.session_id)
        events = await asyncio.wait_for(drainer, timeout=1.0)
        assert isinstance(events, list)

    run_async(scenario())


def test_resume_returns_handle_for_open_session(transport_factory, run_async):
    session = transport_factory(FakeTeam())

    async def scenario():
        h = await session.start(team="t")
        again = await session.resume(h.session_id)
        assert again.session_id == h.session_id
        assert again.team == "t"
        await session.close(h.session_id)

    run_async(scenario())
