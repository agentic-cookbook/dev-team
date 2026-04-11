"""Stress — arbitrator event sequence is a strict 1..N permutation under load.

Spawns 100 concurrent `emit_event` coroutines on a single session. The
arbitrator serializes inserts under its async lock; the sequence counter
must assign a distinct integer to every event with no gaps and no
duplicates even under full concurrency.
"""
from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from services.conductor.arbitrator import Arbitrator
from services.conductor.arbitrator.backends import SqliteBackend

pytestmark = pytest.mark.stress


def test_concurrent_emit_event_yields_strict_monotonic_sequence(tmp_path):
    async def _t():
        backend = SqliteBackend(tmp_path / "stress.sqlite")
        arb = Arbitrator(backend)
        await arb.start()
        session_id = uuid4()
        await arb.open_session(session_id, initial_team_id="t")

        N = 100

        async def emit(i: int):
            await arb.emit_event(
                session_id=session_id,
                team_id="t",
                kind="stress",
                payload={"i": i},
            )

        await asyncio.gather(*(emit(i) for i in range(N)))

        events = await arb.list_events(session_id)
        sequences = sorted(e.sequence for e in events)
        assert sequences == list(range(1, N + 1)), (
            f"non-contiguous sequence under concurrency: {sequences[:10]}..."
        )
        assert len(sequences) == N
        assert len(set(sequences)) == N  # no duplicates
        await arb.close()

    asyncio.run(_t())
