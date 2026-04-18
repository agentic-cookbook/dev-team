"""Integration surface test fixtures.

`transport_factory` is parametrized over available transports. For this
vertical slice only the in-process transport is registered; stdio and
WebSocket are added in their respective plan tasks.
"""
from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncIterator, Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "dev-team"))

from services.integration_surface import (  # noqa: E402
    InProcessSession,
    TeamSession,
)


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


@pytest.fixture(params=["in_process"])
def transport_factory(request) -> Callable[[object], TeamSession]:
    """Returns a factory callable: (runner) -> TeamSession."""
    kind = request.param
    if kind == "in_process":
        return lambda runner: InProcessSession(runner)
    raise AssertionError(f"unknown transport: {kind}")


@pytest.fixture
def collect_events():
    """Helper: consume `events(session_id)` until a terminator.

    Accepts either a single event type ("result") or a sentinel function.
    """
    async def _collect(
        session: TeamSession,
        session_id: str,
        until_type: str = "result",
    ) -> list:
        out = []
        async for ev in session.events(session_id):
            out.append(ev)
            if ev.type == until_type:
                return out
        return out

    return _collect
