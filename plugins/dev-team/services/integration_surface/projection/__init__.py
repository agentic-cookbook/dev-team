"""Conductor → protocol projection layer.

Each module under `projection/` is a pure function (or small class) that
maps a conductor resource type onto a list of protocol `Event`s. They
take already-fetched rows as input — no DB access here. The host is
responsible for ordering the output streams and assigning monotonically
increasing `seq` values.
"""
from __future__ import annotations

from .dispatch_projector import (
    project_dispatches,
    DispatchAttempt,
)
from .event_projector import project_events
from .request_projector import (
    answer_request,
    project_requests,
)
from .state_projector import project_node_state_events

__all__ = [
    "DispatchAttempt",
    "answer_request",
    "project_dispatches",
    "project_events",
    "project_node_state_events",
    "project_requests",
]
