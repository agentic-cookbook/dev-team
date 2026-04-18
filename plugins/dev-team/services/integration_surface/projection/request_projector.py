"""Project human-addressed `Request` rows onto `question` events and
write answers back via the arbitrator.

Only requests whose `to_team` is the literal string `"user"` are
human-facing. Anything else stays an internal team-to-team call and is
skipped.
"""
from __future__ import annotations

from typing import Any, Iterable, Protocol
from uuid import UUID

from services.conductor.arbitrator.models import Request, RequestStatus

from ..protocol import Event

USER_TARGET = "user"


class _RequestAnswerer(Protocol):
    async def complete_request(
        self,
        request_id: str,
        response: dict[str, Any],
    ) -> Request: ...


def project_requests(
    rows: Iterable[Request],
    *,
    session_id: str,
    start_seq: int = 0,
) -> list[Event]:
    out: list[Event] = []
    seq = start_seq
    for row in rows:
        if row.to_team != USER_TARGET:
            continue
        if row.status in (RequestStatus.COMPLETED, RequestStatus.FAILED):
            continue
        prompt = _prompt_from(row.input_json)
        out.append(
            Event(
                type="question",
                session_id=session_id,
                seq=seq,
                payload={
                    "question_id": row.request_id,
                    "target": USER_TARGET,
                    "prompt": prompt,
                },
            )
        )
        seq += 1
    return out


def _prompt_from(input_json: dict[str, Any]) -> str:
    for key in ("prompt", "question", "body", "text"):
        value = input_json.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return str(input_json)


async def answer_request(
    arbitrator: _RequestAnswerer,
    request_id: str,
    content: str,
) -> Request:
    """Write a host-supplied answer back to the conductor.

    The response payload uses `{"answer": content}` — if a real consumer
    needs richer structure we grow the schema then; for v1 a single
    string is enough.
    """
    return await arbitrator.complete_request(
        request_id, {"answer": content}
    )
