"""Transport-neutral Session API + typed events.

The `TeamSession` ABC is the only thing hosts talk to. Transports
(in-process, stdio NDJSON, WebSocket) each implement it.
"""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Event:
    type: str
    session_id: str
    seq: int
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SessionOptions:
    allowed_tools: tuple[str, ...] = ()
    disallowed_tools: tuple[str, ...] = ()
    max_turns: int | None = None
    permission_mode: str = "default"


@dataclass(frozen=True)
class SessionHandle:
    session_id: str
    team: str


class TeamSession(ABC):
    @abstractmethod
    async def start(
        self,
        team: str,
        prompt: str | None = None,
        options: SessionOptions | None = None,
    ) -> SessionHandle: ...

    @abstractmethod
    async def send(self, session_id: str, user_turn: str) -> None: ...

    @abstractmethod
    def events(self, session_id: str) -> AsyncIterator[Event]: ...

    @abstractmethod
    async def answer(
        self, session_id: str, question_id: str, content: str
    ) -> None: ...

    @abstractmethod
    async def resume(self, session_id: str) -> SessionHandle: ...

    @abstractmethod
    async def close(
        self, session_id: str, reason: str | None = None
    ) -> None: ...


class TurnIO:
    """Helper a TeamRunner uses to emit events and ask HITL questions."""

    def __init__(
        self,
        session_id: str,
        queue: "asyncio.Queue[Event | None]",
        pending_questions: dict[str, "asyncio.Future[str]"],
        next_seq: Callable[[], int],
    ) -> None:
        self._session_id = session_id
        self._queue = queue
        self._pending = pending_questions
        self._next_seq = next_seq

    async def emit(self, type_: str, payload: dict[str, Any]) -> None:
        await self._queue.put(
            Event(
                type=type_,
                session_id=self._session_id,
                seq=self._next_seq(),
                payload=payload,
            )
        )

    async def ask(self, question_id: str, target: str, prompt: str) -> str:
        loop = asyncio.get_event_loop()
        fut: asyncio.Future[str] = loop.create_future()
        self._pending[question_id] = fut
        await self.emit(
            "question",
            {"question_id": question_id, "target": target, "prompt": prompt},
        )
        return await fut
