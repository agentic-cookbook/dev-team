"""name-a-puppy variant that consults the pet-coach team before dispatching.

Exercises the cross-team `request` resource from spec §7. The caller sends
a `pet_coach.suggest_theme` request, receives a theme, stores it into
context, and then runs its specialists as usual.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[3]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from services.conductor.playbook.types import (  # noqa: E402
    DispatchSpecialist,
    EmitMessage,
    Manifest,
    PresentResults,
    SendRequest,
    SpecialistSpec,
    SpecialtySpec,
    State,
    TeamPlaybook,
    Transition,
)


_THEMED_SCHEMA = {
    "type": "object",
    "properties": {
        "candidates": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        }
    },
    "required": ["candidates"],
}

THEMED_SPECIALTY = SpecialtySpec(
    name="themed-name-suggester",
    worker_agent="themed-name-worker",
    worker_prompt_template=(
        'Suggest names matching the theme. Return JSON: {{"candidates": [...] }}.'
    ),
    response_schema=_THEMED_SCHEMA,
    logical_model="fast-cheap",
)

THEMED_SPECIALIST = SpecialistSpec(
    name="themed-breed", specialties=[THEMED_SPECIALTY]
)


STATES = [
    State(
        name="start",
        entry_actions=(
            EmitMessage("Consulting the pet-coach team..."),
            SendRequest(
                kind="pet_coach.suggest_theme",
                to_team="pet-coach",
                input_data={"reason": "name-a-puppy"},
                response_context_key="coach_response",
            ),
        ),
    ),
    State(
        name="dispatch_specialists",
        entry_actions=(DispatchSpecialist("themed-breed"),),
    ),
    State(
        name="present",
        entry_actions=(PresentResults("Themed candidate names:"),),
    ),
    State(name="done", terminal=True),
]

TRANSITIONS = [
    Transition("start", "dispatch_specialists"),
    Transition("dispatch_specialists", "present"),
    Transition("present", "done"),
]


PLAYBOOK = TeamPlaybook(
    name="name-a-puppy-with-coach",
    states=STATES,
    transitions=TRANSITIONS,
    judgment_specs={},
    manifest=Manifest(specialists=[THEMED_SPECIALIST]),
    initial_state="start",
)
