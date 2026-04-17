"""Stress — 100 PM requests preserve FIFO order through the serial queue.

A caller team chains 100 states, each issuing one SendRequest to the
project-management team to create a todo row. The arbitrator's serial
request queue (spec §7.4) must keep at most one root request in_flight
and deliver them in enqueue order. Verify by reading the todo rows
back in creation_date order and comparing to the original titles.
"""
from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from services.conductor.arbitrator import (
    Arbitrator,
    RequestStatus,
    SessionStatus,
)
from services.conductor.arbitrator.backends import SqliteBackend
from services.conductor.conductor import Conductor
from services.conductor.dispatcher import MockDispatcher
from services.conductor.playbook import load_playbook
from services.conductor.playbook.types import (
    Manifest,
    SendRequest,
    State,
    TeamPlaybook,
    Transition,
)
from services.conductor.team_lead import TeamLead

pytestmark = pytest.mark.stress

N_REQUESTS = 100
PM_PLAYBOOK_PATH = (
    __import__("pathlib").Path(__file__).resolve().parents[5]
    / "plugins"
    / "dev-team"
    / "services"
    / "conductor"
    / "playbooks"
    / "project_management.py"
)


def _caller_playbook() -> TeamPlaybook:
    states: list[State] = []
    transitions: list[Transition] = []
    for i in range(N_REQUESTS):
        name = f"send_{i}"
        states.append(
            State(
                name=name,
                entry_actions=(
                    SendRequest(
                        kind="pm.todo.create",
                        to_team="project-management",
                        input_data={
                            "title": f"todo-{i:03d}",
                            "status": "open",
                        },
                    ),
                ),
            )
        )
        next_name = f"send_{i + 1}" if i + 1 < N_REQUESTS else "done"
        transitions.append(Transition(name, next_name))
    states.append(State(name="done", terminal=True))
    return TeamPlaybook(
        name="pm-stress-caller",
        states=states,
        transitions=transitions,
        judgment_specs={},
        manifest=Manifest(),
        initial_state="send_0",
    )


def test_hundred_pm_requests_preserve_fifo_order(tmp_path):
    async def _t():
        caller = _caller_playbook()
        pm = load_playbook(PM_PLAYBOOK_PATH)

        backend = SqliteBackend(tmp_path / "stress.sqlite")
        arb = Arbitrator(backend)
        await arb.start()

        session_id = uuid4()
        conductor = Conductor(
            arbitrator=arb,
            dispatcher=MockDispatcher(),
            team_lead=TeamLead(caller),
            session_id=session_id,
            aux_team_leads=[TeamLead(pm)],
            max_steps=N_REQUESTS * 3 + 50,
        )

        await conductor.run()

        session_row = await backend.fetch_one(
            "session", {"session_id": str(session_id)}
        )
        assert session_row["status"] == SessionStatus.COMPLETED.value

        # All 100 requests completed.
        request_rows = await backend.fetch_all(
            "request", where={"session_id": str(session_id)}
        )
        assert len(request_rows) == N_REQUESTS
        assert all(
            r["status"] == RequestStatus.COMPLETED.value
            for r in request_rows
        )

        # Serial queue invariant: sorted by creation_date, request N's
        # start_date must be >= request (N-1)'s completion_date. Under
        # the root-only serial queue, at most one request is in flight
        # at any time.
        sorted_by_creation = sorted(
            request_rows, key=lambda r: r["creation_date"]
        )
        for i in range(1, len(sorted_by_creation)):
            prev = sorted_by_creation[i - 1]
            curr = sorted_by_creation[i]
            assert prev["completion_date"] is not None
            assert curr["start_date"] is not None
            assert curr["start_date"] >= prev["completion_date"], (
                f"request {i} went in-flight before previous completed "
                f"— serial queue violation"
            )

        # 100 todo rows landed, FIFO title order preserved.
        todo_rows = await backend.fetch_all(
            "todo", where={"session_id": str(session_id)}
        )
        assert len(todo_rows) == N_REQUESTS
        todo_rows.sort(key=lambda r: r["creation_date"])
        titles = [r["title"] for r in todo_rows]
        assert titles == [f"todo-{i:03d}" for i in range(N_REQUESTS)], (
            "todo rows not in FIFO creation order"
        )

        await arb.close()

    asyncio.run(_t())
