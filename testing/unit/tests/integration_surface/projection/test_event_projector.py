"""Unit tests for the event → state projector."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from services.conductor.arbitrator.models import Event as ArbEvent
from services.integration_surface.event_schema import validate_stream
from services.integration_surface.projection import project_events


def _row(
    kind: str,
    *,
    dispatch_id: str | None = None,
    payload: dict | None = None,
    team_id: str | None = "team",
    plan_node_id: str | None = None,
    sequence: int = 1,
) -> ArbEvent:
    return ArbEvent(
        event_id=f"evt_{sequence}",
        session_id=uuid4(),
        team_id=team_id,
        agent_id=None,
        dispatch_id=dispatch_id,
        sequence=sequence,
        kind=kind,
        payload_json=payload or {},
        event_date=datetime.utcnow(),
        plan_node_id=plan_node_id,
    )


def test_dispatch_rows_are_skipped():
    rows = [
        _row("assistant", dispatch_id="disp_1", sequence=1),
        _row("whats_next_decision", payload={"action": "advance-to"}, sequence=2),
    ]
    events = project_events(rows, session_id="s1")
    assert len(events) == 1
    assert events[0].type == "state"
    assert events[0].payload["detail"]["kind"] == "whats_next_decision"


def test_whats_next_decision_surfaces_action_and_reason():
    rows = [
        _row(
            "whats_next_decision",
            payload={
                "action": "advance-to",
                "node_id": "n1",
                "reason": "mock picks n1",
            },
            sequence=5,
        )
    ]
    events = project_events(rows, session_id="s1", start_seq=10)
    assert len(events) == 1
    ev = events[0]
    assert ev.seq == 10
    assert ev.payload["phase"] == "running"
    detail = ev.payload["detail"]
    assert detail["action"] == "advance-to"
    assert detail["node_id"] == "n1"
    assert detail["reason"] == "mock picks n1"


def test_unknown_kinds_are_surfaced_as_breadcrumbs():
    rows = [_row("mystery_kind", payload={"x": 1}, sequence=3)]
    events = project_events(rows, session_id="s1")
    assert len(events) == 1
    assert events[0].payload["detail"]["kind"] == "mystery_kind"


def test_output_passes_schema_linter():
    rows = [
        _row("whats_next_decision", payload={"action": "done"}, sequence=1),
        _row("whats_next_decision", payload={"action": "done"}, sequence=2),
    ]
    events = project_events(rows, session_id="s1")
    violations = validate_stream(events)
    assert violations == []
