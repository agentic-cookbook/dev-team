"""Unit tests for the node-state → state projector."""
from __future__ import annotations

from datetime import datetime

import pytest

from services.conductor.arbitrator.models import (
    NodeStateEvent,
    NodeStateEventType,
)
from services.integration_surface.event_schema import validate_stream
from services.integration_surface.projection import project_node_state_events


def _ev(event_type: NodeStateEventType, node_id: str = "n1", actor: str = "conductor", eid: int = 1) -> NodeStateEvent:
    return NodeStateEvent(
        event_id=eid,
        node_id=node_id,
        event_type=event_type,
        actor=actor,
        event_date=datetime.utcnow(),
    )


@pytest.mark.parametrize(
    "event_type,expected_phase",
    [
        (NodeStateEventType.PLANNED, "starting"),
        (NodeStateEventType.READY, "starting"),
        (NodeStateEventType.RUNNING, "running"),
        (NodeStateEventType.DONE, "closed"),
        (NodeStateEventType.FAILED, "closed"),
        (NodeStateEventType.SUPERSEDED, "closed"),
    ],
)
def test_each_node_state_maps_to_protocol_phase(event_type, expected_phase):
    rows = [_ev(event_type)]
    events = project_node_state_events(rows, session_id="s1")
    assert len(events) == 1
    ev = events[0]
    assert ev.payload["phase"] == expected_phase
    assert ev.payload["detail"]["node_state"] == event_type.value


def test_detail_carries_node_id_and_actor():
    rows = [_ev(NodeStateEventType.RUNNING, node_id="plan.step.1", actor="conductor")]
    events = project_node_state_events(rows, session_id="s1")
    detail = events[0].payload["detail"]
    assert detail["node_id"] == "plan.step.1"
    assert detail["actor"] == "conductor"


def test_seq_numbers_are_monotonic_from_start_seq():
    rows = [_ev(t, eid=i) for i, t in enumerate(
        [NodeStateEventType.PLANNED, NodeStateEventType.READY, NodeStateEventType.RUNNING]
    )]
    events = project_node_state_events(rows, session_id="s1", start_seq=7)
    assert [e.seq for e in events] == [7, 8, 9]


def test_output_passes_schema_linter():
    rows = [
        _ev(NodeStateEventType.PLANNED, eid=1),
        _ev(NodeStateEventType.RUNNING, eid=2),
        _ev(NodeStateEventType.DONE, eid=3),
    ]
    events = project_node_state_events(rows, session_id="s1")
    violations = validate_stream(events)
    assert violations == []
