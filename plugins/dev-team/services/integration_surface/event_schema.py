"""Event schema + linter for the integration surface.

Five violation kinds, mirroring the design doc:
  1. unknown event type
  2. missing required payload field
  3. invalid payload field (unknown key or bad value for constrained fields)
  4. seq gap within a session
  5. duplicate seq within a session
"""
from __future__ import annotations

from dataclasses import dataclass

from .protocol import Event


# (required_fields, optional_fields) per event type
SCHEMA: dict[str, tuple[set[str], set[str]]] = {
    "text": ({"text"}, {"delta", "role"}),
    "thinking": ({"text"}, set()),
    "tool_call": (
        {"tool_use_id", "name", "status"},
        {"input", "output"},
    ),
    "question": (
        {"question_id", "target", "prompt"},
        {"schema"},
    ),
    "result": (
        {"stop_reason"},
        {"usage", "cost_usd", "num_turns"},
    ),
    "error": ({"kind", "message", "retryable"}, set()),
    "state": ({"phase"}, {"detail"}),
}

VALID_TOOL_STATUS = {"running", "succeeded", "failed"}
VALID_STATE_PHASE = {
    "starting",
    "running",
    "awaiting_input",
    "parked",
    "closed",
}


@dataclass(frozen=True)
class Violation:
    kind: int
    message: str
    seq: int | None = None
    session_id: str | None = None


def validate_event(event: Event) -> list[Violation]:
    out: list[Violation] = []
    spec = SCHEMA.get(event.type)
    if spec is None:
        out.append(
            Violation(
                1,
                f"unknown event type: {event.type!r}",
                seq=event.seq,
                session_id=event.session_id,
            )
        )
        return out
    required, optional = spec
    keys = set(event.payload.keys())
    missing = required - keys
    if missing:
        out.append(
            Violation(
                2,
                f"{event.type}: missing required {sorted(missing)}",
                seq=event.seq,
                session_id=event.session_id,
            )
        )
    extra = keys - required - optional
    if extra:
        out.append(
            Violation(
                3,
                f"{event.type}: unknown fields {sorted(extra)}",
                seq=event.seq,
                session_id=event.session_id,
            )
        )
    if event.type == "tool_call":
        status = event.payload.get("status")
        if status is not None and status not in VALID_TOOL_STATUS:
            out.append(
                Violation(
                    3,
                    f"tool_call: status {status!r} not in {sorted(VALID_TOOL_STATUS)}",
                    seq=event.seq,
                    session_id=event.session_id,
                )
            )
    if event.type == "state":
        phase = event.payload.get("phase")
        if phase is not None and phase not in VALID_STATE_PHASE:
            out.append(
                Violation(
                    3,
                    f"state: phase {phase!r} not in {sorted(VALID_STATE_PHASE)}",
                    seq=event.seq,
                    session_id=event.session_id,
                )
            )
    return out


def validate_stream(events: list[Event]) -> list[Violation]:
    out: list[Violation] = []
    for e in events:
        out.extend(validate_event(e))
    per_session: dict[str, list[int]] = {}
    for e in events:
        per_session.setdefault(e.session_id, []).append(e.seq)
    for sid, seqs in per_session.items():
        seen: set[int] = set()
        for s in seqs:
            if s in seen:
                out.append(
                    Violation(5, f"duplicate seq {s}", seq=s, session_id=sid)
                )
            seen.add(s)
        sorted_seqs = sorted(seen)
        for i in range(1, len(sorted_seqs)):
            prev, cur = sorted_seqs[i - 1], sorted_seqs[i]
            if cur != prev + 1:
                out.append(
                    Violation(
                        4,
                        f"seq gap {prev} → {cur}",
                        seq=cur,
                        session_id=sid,
                    )
                )
    return out
