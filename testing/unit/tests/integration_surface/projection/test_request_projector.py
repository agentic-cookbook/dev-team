"""Unit tests for the request → question projector."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from services.conductor.arbitrator.models import Request, RequestStatus
from services.integration_surface.event_schema import validate_stream
from services.integration_surface.projection import (
    answer_request,
    project_requests,
)


def _req(
    *,
    to_team: str = "user",
    status: RequestStatus = RequestStatus.PENDING,
    input_json: dict | None = None,
    request_id: str = "req_1",
) -> Request:
    now = datetime.utcnow()
    return Request(
        request_id=request_id,
        session_id=uuid4(),
        from_team="devteam",
        to_team=to_team,
        kind="ask_user",
        input_json=input_json or {"prompt": "what's your name?"},
        status=status,
        response_json=None,
        parent_request_id=None,
        creation_date=now,
        start_date=None,
        completion_date=None,
        timeout_date=now + timedelta(seconds=60),
    )


def test_user_request_becomes_question_event():
    events = project_requests([_req()], session_id="s1")
    assert len(events) == 1
    ev = events[0]
    assert ev.type == "question"
    assert ev.payload["target"] == "user"
    assert ev.payload["question_id"] == "req_1"
    assert ev.payload["prompt"] == "what's your name?"


def test_internal_requests_are_skipped():
    events = project_requests(
        [_req(to_team="devteam"), _req(to_team="projectteam")],
        session_id="s1",
    )
    assert events == []


def test_completed_requests_are_skipped():
    events = project_requests(
        [_req(status=RequestStatus.COMPLETED)], session_id="s1"
    )
    assert events == []


def test_prompt_falls_back_across_common_keys():
    for key in ("prompt", "question", "body", "text"):
        ev = project_requests(
            [_req(input_json={key: "ask me"})], session_id="s1"
        )[0]
        assert ev.payload["prompt"] == "ask me"


def test_output_passes_schema_linter():
    events = project_requests(
        [
            _req(request_id="req_1"),
            _req(request_id="req_2", input_json={"prompt": "again?"}),
        ],
        session_id="s1",
    )
    assert validate_stream(events) == []


class _FakeArbitrator:
    def __init__(self):
        self.calls: list[tuple[str, dict]] = []

    async def complete_request(self, request_id: str, response: dict):
        self.calls.append((request_id, response))
        return _req(request_id=request_id, status=RequestStatus.COMPLETED)


def test_answer_request_writes_through_arbitrator():
    arb = _FakeArbitrator()
    asyncio.run(answer_request(arb, "req_1", "Rex"))
    assert arb.calls == [("req_1", {"answer": "Rex"})]
