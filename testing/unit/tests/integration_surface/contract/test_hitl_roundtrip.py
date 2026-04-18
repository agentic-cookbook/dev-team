"""HITL: team emits question → host answers → team continues."""
from __future__ import annotations

import asyncio

from ..fixtures.fake_team import FakeTeam


def test_question_target_preserved_and_answer_reaches_team(
    transport_factory, run_async
):
    fake = FakeTeam().reply_with_question(
        pre_events=[("text", {"text": "let me ask"})],
        ask=("q1", "user", "what is your name?"),
        post_events=[("result", {"stop_reason": "end_turn"})],
    )
    session = transport_factory(fake)

    async def scenario():
        h = await session.start(team="t")
        await session.send(h.session_id, "go")

        collected = []
        async for e in session.events(h.session_id):
            collected.append(e)
            if e.type == "question":
                assert e.payload["target"] == "user"
                assert e.payload["question_id"] == "q1"
                await session.answer(
                    h.session_id, e.payload["question_id"], "Alice"
                )
            if e.type == "result":
                break

        types = [e.type for e in collected]
        assert types == ["text", "question", "text", "result"]
        # The post-answer text echoes the answer (per FakeTeam convention).
        assert "Alice" in collected[2].payload["text"]

        await session.close(h.session_id)

    run_async(scenario())


def test_unknown_answer_is_silently_dropped(transport_factory, run_async):
    """Answering a question_id the team doesn't know about is a no-op.

    Protects hosts from blowing up on stale answers (user hits reply
    after a timeout, for example).
    """
    session = transport_factory(FakeTeam())

    async def scenario():
        h = await session.start(team="t")
        # No pending question — this should not raise.
        await session.answer(h.session_id, "nonexistent", "hello")
        await session.close(h.session_id)

    run_async(scenario())
