"""Scripted team runner for tests.

`FakeTeam` is a `TeamRunner`: given a `TurnIO` + the user turn, it emits
a scripted sequence of events. Reaction rules let tests express "when
the host sends X, reply with Y and then ask a question." No real LLM,
no conductor.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from services.integration_surface import TurnIO
from services.integration_surface.in_process import _SessionContext


@dataclass
class Reply:
    events: list[tuple[str, dict[str, Any]]]
    match: Callable[[str], bool] = field(default=lambda _t: True)
    ask: tuple[str, str, str] | None = None  # (question_id, target, prompt)
    after_answer: list[tuple[str, dict[str, Any]]] = field(default_factory=list)


class FakeTeam:
    """Scripted runner.

    Call `.reply(...)` (possibly multiple times) to register responses;
    the first matching reply wins for each user turn. The resulting
    instance is itself callable as a `TeamRunner`.
    """

    def __init__(self) -> None:
        self._replies: list[Reply] = []

    def reply(
        self,
        *events: tuple[str, dict[str, Any]],
        when: Callable[[str], bool] | None = None,
    ) -> "FakeTeam":
        self._replies.append(
            Reply(
                events=list(events),
                match=when or (lambda _t: True),
            )
        )
        return self

    def reply_with_question(
        self,
        pre_events: list[tuple[str, dict[str, Any]]],
        ask: tuple[str, str, str],
        post_events: list[tuple[str, dict[str, Any]]],
        when: Callable[[str], bool] | None = None,
    ) -> "FakeTeam":
        self._replies.append(
            Reply(
                events=pre_events,
                ask=ask,
                after_answer=post_events,
                match=when or (lambda _t: True),
            )
        )
        return self

    async def __call__(
        self, io: TurnIO, user_turn: str, ctx: _SessionContext
    ) -> None:
        reply = next(
            (r for r in self._replies if r.match(user_turn)), None
        )
        if reply is None:
            await io.emit("text", {"text": f"ack: {user_turn}"})
            await io.emit("result", {"stop_reason": "end_turn"})
            return
        for t, p in reply.events:
            await io.emit(t, p)
        if reply.ask is not None:
            qid, target, prompt = reply.ask
            answer = await io.ask(qid, target, prompt)
            await io.emit("text", {"text": f"heard: {answer}"})
            for t, p in reply.after_answer:
                await io.emit(t, p)
