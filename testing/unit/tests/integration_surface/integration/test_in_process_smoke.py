"""End-to-end smoke: run the puppy conductor, project its rows onto the
protocol event stream, and assert the stream is schema-clean + stable.

A golden file under `fixtures/recorded_sessions/in_process_puppy.ndjson`
captures the normalized projected stream. IDs and timestamps are
rewritten so the golden is deterministic; if the projection output shape
shifts intentionally, regenerate with:

    pytest -q testing/unit/tests/integration_surface/integration \
      --override-ini="addopts=" -p no:cacheprovider \
      -k test_in_process_smoke \
      --update-recorded

(No `--update-recorded` flag is wired — set `UPDATE_RECORDED=1` instead.)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from uuid import UUID, uuid4

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "dev-team"))

from services.conductor.arbitrator import Arbitrator  # noqa: E402
from services.conductor.arbitrator.backends import SqliteBackend  # noqa: E402
from services.conductor.arbitrator.models import (  # noqa: E402
    Event as ArbEvent,
    NodeStateEvent,
    NodeStateEventType,
    Request,
    RequestStatus,
)
from services.conductor.conductor import Conductor  # noqa: E402
from services.conductor.dispatcher import MockDispatcher  # noqa: E402
from services.conductor.playbooks.name_a_puppy_roadmap import (  # noqa: E402
    TEAM_ID,
    build_roadmap,
    realize,
)
from services.conductor.specialty import WhatsNextSpecialty  # noqa: E402
from services.integration_surface.event_schema import validate_stream  # noqa: E402
from services.integration_surface.projection import (  # noqa: E402
    project_dispatches,
    project_events,
    project_node_state_events,
    project_requests,
)

from datetime import datetime  # noqa: E402


GOLDEN = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "recorded_sessions"
    / "in_process_puppy.ndjson"
)


def _build_dispatcher() -> MockDispatcher:
    return MockDispatcher(
        {
            "whats-next-worker": {
                "action": "advance-to",
                "node_id": "breed-names",
                "reason": "batch",
                "deterministic": False,
            },
            "whats-next-verifier": {"verdict": "pass", "reason": "ok"},
            "breed-name-worker": {"candidates": ["Biscuit"]},
            "lifestyle-name-worker": {"candidates": ["Scout"]},
            "temperament-name-worker": {"candidates": ["Luna"]},
            "aggregator-worker": {"ranked_candidates": ["Luna", "Biscuit", "Scout"]},
        }
    )


async def _run_and_project(tmp_path: Path) -> list[dict]:
    backend = SqliteBackend(tmp_path / "arb.sqlite")
    arb = Arbitrator(backend)
    await arb.start()

    roadmap_id = await build_roadmap(arb)
    session_id = uuid4()
    await arb.open_session(
        session_id,
        initial_team_id=TEAM_ID,
        metadata={"roadmap_id": roadmap_id},
    )
    conductor = Conductor(
        arbitrator=arb,
        dispatcher=_build_dispatcher(),
        team_lead=None,
        session_id=session_id,
    )
    await conductor.run_roadmap([WhatsNextSpecialty()], realize_primitive=realize)

    event_rows = await arb.list_events(session_id)
    request_rows_raw = await arb.list_requests(session_id)
    request_rows = [_hydrate_request(r) for r in request_rows_raw]
    nse_rows = await _list_node_state_events(arb, roadmap_id)

    await arb.close()

    sid = "SESSION"
    dispatches = project_dispatches(event_rows, session_id=sid, start_seq=0)
    events = project_events(
        event_rows, session_id=sid, start_seq=len(dispatches)
    )
    states = project_node_state_events(
        nse_rows, session_id=sid, start_seq=len(dispatches) + len(events)
    )
    questions = project_requests(
        request_rows,
        session_id=sid,
        start_seq=len(dispatches) + len(events) + len(states),
    )
    stream = dispatches + events + states + questions

    violations = validate_stream(stream)
    assert violations == [], violations

    return [_normalize(e) for e in stream]


def _hydrate_request(row: dict) -> Request:
    return Request(
        request_id=row["request_id"],
        session_id=UUID(row["session_id"]),
        from_team=row["from_team"],
        to_team=row["to_team"],
        kind=row["kind"],
        input_json=json.loads(row["input_json"] or "{}"),
        status=RequestStatus(row["status"]),
        response_json=(
            json.loads(row["response_json"]) if row.get("response_json") else None
        ),
        parent_request_id=row.get("parent_request_id"),
        creation_date=_dt(row["creation_date"]),
        start_date=_dt(row.get("start_date")),
        completion_date=_dt(row.get("completion_date")),
        timeout_date=_dt(row["timeout_date"]),
        plan_node_id=row.get("plan_node_id"),
    )


def _dt(v):
    return datetime.fromisoformat(v) if v else None


async def _list_node_state_events(arb, roadmap_id: str) -> list[NodeStateEvent]:
    nodes = await arb.list_plan_nodes(roadmap_id)
    out: list[NodeStateEvent] = []
    for node in nodes:
        rows = await arb._storage.fetch_all(
            "node_state_event",
            where={"node_id": node.node_id},
            order_by="event_id ASC",
        )
        for r in rows:
            out.append(
                NodeStateEvent(
                    event_id=r["event_id"],
                    node_id=r["node_id"],
                    session_id=(
                        UUID(r["session_id"]) if r.get("session_id") else None
                    ),
                    event_type=NodeStateEventType(r["event_type"]),
                    actor=r["actor"],
                    event_date=_dt(r["event_date"]),
                )
            )
    out.sort(key=lambda e: e.event_id)
    return out


def _normalize(event) -> dict:
    """Strip non-deterministic IDs so the golden is reproducible."""
    payload = _scrub(event.payload)
    return {
        "type": event.type,
        "session_id": event.session_id,
        "seq": event.seq,
        "payload": payload,
    }


def _scrub(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in {"tool_use_id", "dispatch_id", "plan_node_id", "event_id"}:
                out[k] = "<id>" if v is not None else None
            elif k == "output":
                # Dispatcher output contains cost/timestamp junk; collapse.
                out[k] = "<output>"
            else:
                out[k] = _scrub(v)
        return out
    if isinstance(obj, list):
        return [_scrub(v) for v in obj]
    return obj


def test_in_process_smoke(tmp_path):
    stream = asyncio.run(_run_and_project(tmp_path))

    assert stream, "expected at least one projected event"
    assert any(e["type"] == "tool_call" for e in stream), (
        "expected some tool_call events from puppy dispatches"
    )
    assert any(e["type"] == "state" for e in stream), (
        "expected state events from node_state projection"
    )

    serialized = "\n".join(json.dumps(e, sort_keys=True) for e in stream) + "\n"
    if os.environ.get("UPDATE_RECORDED") == "1":
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(serialized)
        pytest.skip("regenerated golden")
    assert GOLDEN.is_file(), (
        f"missing golden {GOLDEN}. Regenerate with UPDATE_RECORDED=1."
    )
    expected = GOLDEN.read_text()
    assert serialized == expected, (
        "projected stream drifted from golden; regenerate with UPDATE_RECORDED=1"
    )
