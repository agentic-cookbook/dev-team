"""Summarize dispatcher attempts as protocol `tool_call` lifecycles.

The live arbitrator schema does **not** yet have standalone
`dispatch` / `attempt` tables (see
`docs/planning/todo.md` — "Dispatch / attempt tables on the live
conductor schema"). Until those land, we derive the same view from the
existing `event` table: every row with a `dispatch_id` belongs to one
attempt, ordered by `sequence`.

Each dispatch is projected as:

* a `running` `tool_call` (emitted on the first event seen),
* followed by a terminal `succeeded` or `failed` event keyed on the
  presence of a `result` kind (or a `failed=True` marker in the last
  payload).

If the attempt tables ship later we can swap `project_dispatches` to
read them directly — the output protocol shape stays identical.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from services.conductor.arbitrator.models import Event as ArbEvent

from ..protocol import Event


@dataclass(frozen=True)
class DispatchAttempt:
    dispatch_id: str
    agent_id: str | None
    first_sequence: int
    last_sequence: int
    terminated: bool
    succeeded: bool
    final_payload: dict


def _collect_attempts(rows: Iterable[ArbEvent]) -> list[DispatchAttempt]:
    by_dispatch: dict[str, list[ArbEvent]] = {}
    for row in rows:
        if row.dispatch_id is None:
            continue
        by_dispatch.setdefault(row.dispatch_id, []).append(row)

    out: list[DispatchAttempt] = []
    for dispatch_id, events in by_dispatch.items():
        events.sort(key=lambda e: e.sequence)
        first = events[0]
        last = events[-1]
        terminated = any(_is_terminal(e) for e in events)
        succeeded = terminated and not _is_failed(last)
        out.append(
            DispatchAttempt(
                dispatch_id=dispatch_id,
                agent_id=first.agent_id,
                first_sequence=first.sequence,
                last_sequence=last.sequence,
                terminated=terminated,
                succeeded=succeeded,
                final_payload=last.payload_json or {},
            )
        )
    out.sort(key=lambda a: a.first_sequence)
    return out


def _is_terminal(e: ArbEvent) -> bool:
    if e.kind == "result":
        return True
    payload = e.payload_json or {}
    return bool(payload.get("terminated")) or bool(payload.get("failed"))


def _is_failed(e: ArbEvent) -> bool:
    payload = e.payload_json or {}
    if payload.get("failed"):
        return True
    if payload.get("is_error"):
        return True
    return False


def project_dispatches(
    rows: Iterable[ArbEvent],
    *,
    session_id: str,
    start_seq: int = 0,
) -> list[Event]:
    attempts = _collect_attempts(rows)
    out: list[Event] = []
    seq = start_seq
    for attempt in attempts:
        out.append(
            Event(
                type="tool_call",
                session_id=session_id,
                seq=seq,
                payload={
                    "tool_use_id": attempt.dispatch_id,
                    "name": attempt.agent_id or "agent_dispatch",
                    "status": "running",
                },
            )
        )
        seq += 1
        if attempt.terminated:
            out.append(
                Event(
                    type="tool_call",
                    session_id=session_id,
                    seq=seq,
                    payload={
                        "tool_use_id": attempt.dispatch_id,
                        "name": attempt.agent_id or "agent_dispatch",
                        "status": "succeeded" if attempt.succeeded else "failed",
                        "output": attempt.final_payload,
                    },
                )
            )
            seq += 1
    return out
