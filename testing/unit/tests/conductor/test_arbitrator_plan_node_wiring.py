"""plan_node_id kwarg flows through existing Arbitrator create methods.

The roadmap PR wired an optional plan_node_id onto: push_state,
create_message, create_gate, create_result, emit_event, enqueue_task,
create_request. Each test: create the row with plan_node_id, read back,
assert the field survived the round-trip.
"""
from __future__ import annotations

from uuid import uuid4

import pytest

from services.conductor.arbitrator import Arbitrator
from services.conductor.arbitrator.backends import SqliteBackend
from services.conductor.arbitrator.models import NodeKind


@pytest.fixture
def arb_with_node(tmp_path, run_async):
    """A connected Arbitrator with a roadmap + plan_node ready to reference."""
    arb = Arbitrator(SqliteBackend(tmp_path / "arb.sqlite"))
    run_async(arb.start())
    rm = run_async(arb.create_roadmap("R"))
    node = run_async(arb.create_plan_node(
        rm.roadmap_id, "N", NodeKind.PRIMITIVE, node_id="node-1",
    ))
    yield arb, node
    run_async(arb.close())


def test_push_state_carries_plan_node_id(arb_with_node, run_async):
    arb, node = arb_with_node
    sid = uuid4()
    run_async(arb.open_session(sid, "team"))
    state = run_async(arb.push_state(
        sid, "team", "s", parent_node_id=None, plan_node_id=node.node_id,
    ))
    assert state.plan_node_id == node.node_id
    # Re-read from DB.
    active = run_async(arb.active_state_nodes(sid))
    assert any(n.plan_node_id == node.node_id for n in active)


def test_create_message_carries_plan_node_id(arb_with_node, run_async):
    arb, node = arb_with_node
    sid = uuid4()
    run_async(arb.open_session(sid, "team"))
    msg = run_async(arb.create_message(
        sid, "team", "in", "question", "hi", plan_node_id=node.node_id,
    ))
    assert msg.plan_node_id == node.node_id
    msgs = run_async(arb.list_messages(sid))
    assert any(m.plan_node_id == node.node_id for m in msgs)


def test_create_gate_carries_plan_node_id(arb_with_node, run_async):
    arb, node = arb_with_node
    sid = uuid4()
    run_async(arb.open_session(sid, "team"))
    gate = run_async(arb.create_gate(
        sid, "team", "flow", ["approve", "reject"], plan_node_id=node.node_id,
    ))
    assert gate.plan_node_id == node.node_id


def test_create_result_carries_plan_node_id(arb_with_node, run_async):
    arb, node = arb_with_node
    sid = uuid4()
    run_async(arb.open_session(sid, "team"))
    res = run_async(arb.create_result(
        sid, "team", "software-architecture", True, {"ok": 1},
        plan_node_id=node.node_id,
    ))
    assert res.plan_node_id == node.node_id
    results = run_async(arb.list_results(sid))
    assert any(r.plan_node_id == node.node_id for r in results)


def test_emit_event_carries_plan_node_id(arb_with_node, run_async):
    arb, node = arb_with_node
    sid = uuid4()
    run_async(arb.open_session(sid, "team"))
    ev = run_async(arb.emit_event(
        sid, "team", "tool-use", {"cmd": "ls"}, plan_node_id=node.node_id,
    ))
    assert ev.plan_node_id == node.node_id
    events = run_async(arb.list_events(sid))
    assert any(e.plan_node_id == node.node_id for e in events)


def test_enqueue_task_carries_plan_node_id(arb_with_node, run_async):
    arb, node = arb_with_node
    sid = uuid4()
    run_async(arb.open_session(sid, "team"))
    task = run_async(arb.enqueue_task(
        sid, "team", "dispatch", {"agent": "w"}, plan_node_id=node.node_id,
    ))
    assert task.plan_node_id == node.node_id
    picked = run_async(arb.next_task(sid))
    assert picked is not None
    assert picked.plan_node_id == node.node_id


def test_create_request_carries_plan_node_id(arb_with_node, run_async):
    arb, node = arb_with_node
    sid = uuid4()
    run_async(arb.open_session(sid, "team-a"))
    arb.register_request_kind("dispatch.do", {}, {}, default_timeout_seconds=60)
    arb.register_request_handler("team-b", "dispatch.do", "handler-state")
    req = run_async(arb.create_request(
        sid, "team-a", "team-b", "dispatch.do", {"x": 1},
        plan_node_id=node.node_id,
    ))
    assert req.plan_node_id == node.node_id
    back = run_async(arb.get_request(req.request_id))
    assert back is not None
    assert back.plan_node_id == node.node_id


def test_omitting_plan_node_id_keeps_existing_behavior(arb_with_node, run_async):
    """Existing code that doesn't pass plan_node_id keeps working;
    the field is None on the result."""
    arb, _ = arb_with_node
    sid = uuid4()
    run_async(arb.open_session(sid, "team"))
    msg = run_async(arb.create_message(sid, "team", "in", "q", "hi"))
    assert msg.plan_node_id is None
