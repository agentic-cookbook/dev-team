"""Map `NodeStateEvent` rows onto protocol `state` events.

Only five protocol phases are valid (`starting`, `running`,
`awaiting_input`, `parked`, `closed`). The roadmap lifecycle has six
states: PLANNED / READY / RUNNING / DONE / FAILED / SUPERSEDED. The
projection folds terminal states onto `closed` and carries the roadmap
state in `detail` so hosts that care can still tell `done` from
`failed`.
"""
from __future__ import annotations

from typing import Iterable

from services.conductor.arbitrator.models import (
    NodeStateEvent,
    NodeStateEventType,
)

from ..protocol import Event

_PHASE_MAP: dict[NodeStateEventType, str] = {
    NodeStateEventType.PLANNED: "starting",
    NodeStateEventType.READY: "starting",
    NodeStateEventType.RUNNING: "running",
    NodeStateEventType.DONE: "closed",
    NodeStateEventType.FAILED: "closed",
    NodeStateEventType.SUPERSEDED: "closed",
}


def project_node_state_events(
    rows: Iterable[NodeStateEvent],
    *,
    session_id: str,
    start_seq: int = 0,
) -> list[Event]:
    out: list[Event] = []
    seq = start_seq
    for row in rows:
        phase = _PHASE_MAP[row.event_type]
        out.append(
            Event(
                type="state",
                session_id=session_id,
                seq=seq,
                payload={
                    "phase": phase,
                    "detail": {
                        "node_id": row.node_id,
                        "node_state": row.event_type.value,
                        "actor": row.actor,
                    },
                },
            )
        )
        seq += 1
    return out
