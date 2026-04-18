"""Map conductor `Event` rows onto protocol events.

The conductor's `event` table is a generic audit log; the `kind` column
holds either conductor-internal labels (e.g. `whats_next_decision`) or
forwarded Claude CLI stream-json kinds (`assistant`, `tool_use`,
`tool_result`, `result`, …).

Projection rules:

* An event with a `dispatch_id` is part of an agent dispatch and is
  handled by `dispatch_projector`. This projector **skips** those rows.
* `whats_next_decision` → `state` with `phase="running"` and the
  payload summary in `detail`.
* Any other dispatch-less event → `state` with `phase="running"` and
  the raw `kind` as `detail`. Unknown kinds therefore surface as
  observability breadcrumbs instead of getting silently dropped.
"""
from __future__ import annotations

from typing import Iterable

from services.conductor.arbitrator.models import Event as ArbEvent

from ..protocol import Event


def project_events(
    rows: Iterable[ArbEvent],
    *,
    session_id: str,
    start_seq: int = 0,
) -> list[Event]:
    out: list[Event] = []
    seq = start_seq
    for row in rows:
        if row.dispatch_id is not None:
            continue
        payload = _payload_for(row)
        out.append(
            Event(
                type="state",
                session_id=session_id,
                seq=seq,
                payload=payload,
            )
        )
        seq += 1
    return out


def _payload_for(row: ArbEvent) -> dict:
    detail: dict = {
        "kind": row.kind,
        "team_id": row.team_id,
        "plan_node_id": row.plan_node_id,
    }
    if row.kind == "whats_next_decision":
        decision = row.payload_json or {}
        detail["action"] = decision.get("action")
        detail["node_id"] = decision.get("node_id")
        detail["reason"] = decision.get("reason")
    return {"phase": "running", "detail": detail}
