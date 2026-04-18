"""In-process reference transport.

Implements `TeamSession` via direct method calls and an async queue per
session. The runtime that knows how to execute a turn is pluggable:
pass a `TeamRunner` coroutine to the constructor.
"""
from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field

from .protocol import (
    Event,
    SessionHandle,
    SessionOptions,
    TeamSession,
    TurnIO,
)


TeamRunner = Callable[[TurnIO, str, "_SessionContext"], Awaitable[None]]
"""Runner signature: (io, user_turn, context) -> None.

The runner emits events via `io.emit(...)`, asks HITL questions via
`io.ask(...)`, and returns when the turn is complete. The session stays
open for more turns; close is driven by the host.
"""


@dataclass
class _SessionContext:
    team: str
    options: SessionOptions


@dataclass
class _Session:
    team: str
    options: SessionOptions
    queue: "asyncio.Queue[Event | None]" = field(
        default_factory=lambda: asyncio.Queue()
    )
    pending_questions: dict[str, "asyncio.Future[str]"] = field(
        default_factory=dict
    )
    seq: int = 0
    turn_tasks: list[asyncio.Task[None]] = field(default_factory=list)

    def next_seq(self) -> int:
        s = self.seq
        self.seq = s + 1
        return s


class InProcessSession(TeamSession):
    def __init__(self, runner: TeamRunner) -> None:
        self._runner = runner
        self._sessions: dict[str, _Session] = {}

    async def start(
        self,
        team: str,
        prompt: str | None = None,
        options: SessionOptions | None = None,
    ) -> SessionHandle:
        sid = uuid.uuid4().hex
        self._sessions[sid] = _Session(
            team=team, options=options or SessionOptions()
        )
        if prompt is not None:
            await self.send(sid, prompt)
        return SessionHandle(session_id=sid, team=team)

    async def send(self, session_id: str, user_turn: str) -> None:
        sess = self._require(session_id)
        io = TurnIO(
            session_id=session_id,
            queue=sess.queue,
            pending_questions=sess.pending_questions,
            next_seq=sess.next_seq,
        )
        ctx = _SessionContext(team=sess.team, options=sess.options)
        task = asyncio.create_task(self._runner(io, user_turn, ctx))
        sess.turn_tasks.append(task)

    async def events(self, session_id: str) -> AsyncIterator[Event]:
        sess = self._require(session_id)
        while True:
            item = await sess.queue.get()
            if item is None:
                return
            yield item

    async def answer(
        self, session_id: str, question_id: str, content: str
    ) -> None:
        sess = self._require(session_id)
        fut = sess.pending_questions.pop(question_id, None)
        if fut is None or fut.done():
            return
        fut.set_result(content)

    async def resume(self, session_id: str) -> SessionHandle:
        sess = self._require(session_id)
        return SessionHandle(session_id=session_id, team=sess.team)

    async def close(
        self, session_id: str, reason: str | None = None
    ) -> None:
        sess = self._sessions.pop(session_id, None)
        if sess is None:
            return
        for t in sess.turn_tasks:
            if not t.done():
                t.cancel()
        await sess.queue.put(None)

    def _require(self, session_id: str) -> _Session:
        sess = self._sessions.get(session_id)
        if sess is None:
            raise KeyError(f"unknown session: {session_id}")
        return sess
