"""Unit tests for the dispatch-attempt → tool_call projector."""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from services.conductor.arbitrator.models import Event as ArbEvent
from services.integration_surface.event_schema import validate_stream
from services.integration_surface.projection import project_dispatches


def _row(
    sequence: int,
    *,
    kind: str = "assistant",
    dispatch_id: str | None = "disp_1",
    agent_id: str | None = "breed-name-worker",
    payload: dict | None = None,
) -> ArbEvent:
    return ArbEvent(
        event_id=f"evt_{sequence}",
        session_id=uuid4(),
        team_id="team",
        agent_id=agent_id,
        dispatch_id=dispatch_id,
        sequence=sequence,
        kind=kind,
        payload_json=payload or {},
        event_date=datetime.utcnow(),
    )


def test_successful_dispatch_emits_running_then_succeeded():
    rows = [
        _row(1, kind="assistant"),
        _row(2, kind="result", payload={"output": "ok"}),
    ]
    events = project_dispatches(rows, session_id="s1")
    assert [e.type for e in events] == ["tool_call", "tool_call"]
    assert events[0].payload["status"] == "running"
    assert events[0].payload["tool_use_id"] == "disp_1"
    assert events[0].payload["name"] == "breed-name-worker"
    assert events[1].payload["status"] == "succeeded"
    assert events[1].payload["output"] == {"output": "ok"}


def test_failed_dispatch_emits_failed_status():
    rows = [
        _row(1, kind="assistant"),
        _row(2, kind="result", payload={"failed": True, "error": "boom"}),
    ]
    events = project_dispatches(rows, session_id="s1")
    assert events[-1].payload["status"] == "failed"


def test_unterminated_dispatch_emits_only_running():
    rows = [_row(1, kind="assistant")]
    events = project_dispatches(rows, session_id="s1")
    assert len(events) == 1
    assert events[0].payload["status"] == "running"


def test_multiple_dispatches_ordered_by_first_sequence():
    rows = [
        _row(5, dispatch_id="disp_b", kind="assistant"),
        _row(6, dispatch_id="disp_b", kind="result"),
        _row(1, dispatch_id="disp_a", kind="assistant", agent_id="worker-a"),
        _row(2, dispatch_id="disp_a", kind="result", agent_id="worker-a"),
    ]
    events = project_dispatches(rows, session_id="s1")
    tool_ids = [e.payload["tool_use_id"] for e in events]
    assert tool_ids == ["disp_a", "disp_a", "disp_b", "disp_b"]


def test_non_dispatch_rows_ignored():
    rows = [
        _row(1, kind="whats_next_decision", dispatch_id=None, agent_id=None),
        _row(2, kind="assistant"),
        _row(3, kind="result"),
    ]
    events = project_dispatches(rows, session_id="s1")
    assert len(events) == 2
    assert events[0].payload["tool_use_id"] == "disp_1"


def test_output_passes_schema_linter():
    rows = [
        _row(1, kind="assistant"),
        _row(2, kind="result", payload={"ok": True}),
    ]
    events = project_dispatches(rows, session_id="s1")
    assert validate_stream(events) == []
