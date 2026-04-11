"""project-management team — standalone PM handlers (spec §6.1, step 4).

Exposes three request kinds for creating PM resources:

- ``pm.schedule.create`` — insert a row into ``schedule``
- ``pm.todo.create`` — insert a row into ``todo``
- ``pm.decision.create`` — insert a row into ``decision``

Each handler state uses a ``WriteProjectResource`` action that reads the
active request's ``input_json`` as kwargs to the matching arbitrator
``create_*`` method and responds with the inserted row. No LLM call — PM
data capture is mechanical.

This team is *new* and does not refactor the existing dev-team (per user
instruction for step 4). A future step will retire the old
project-manager specialist in favor of sending requests here.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[3]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from services.conductor.playbook.types import (  # noqa: E402
    Manifest,
    State,
    TeamPlaybook,
    WriteProjectResource,
)


HANDLE_SCHEDULE_CREATE = State(
    name="handle_schedule_create",
    entry_actions=(WriteProjectResource(resource_type="schedule"),),
)

HANDLE_TODO_CREATE = State(
    name="handle_todo_create",
    entry_actions=(WriteProjectResource(resource_type="todo"),),
)

HANDLE_DECISION_CREATE = State(
    name="handle_decision_create",
    entry_actions=(WriteProjectResource(resource_type="decision"),),
)


PLAYBOOK = TeamPlaybook(
    name="project-management",
    states=[
        HANDLE_SCHEDULE_CREATE,
        HANDLE_TODO_CREATE,
        HANDLE_DECISION_CREATE,
    ],
    transitions=[],
    judgment_specs={},
    manifest=Manifest(),
    initial_state="handle_schedule_create",
    request_handlers={
        "pm.schedule.create": "handle_schedule_create",
        "pm.todo.create": "handle_todo_create",
        "pm.decision.create": "handle_decision_create",
    },
)
