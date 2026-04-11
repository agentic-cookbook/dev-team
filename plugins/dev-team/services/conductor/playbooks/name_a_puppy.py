"""name-a-puppy team playbook — walking skeleton.

The simplest possible end-to-end flow: greet, dispatch a single `breed`
specialist with a single specialty that produces breed-based name
candidates, present the aggregated names, done.

Step 2 will expand this to three specialists running in parallel plus a
user-facing judgment node.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow this playbook to be loaded via absolute file path (which is how the
# loader finds it) without requiring the caller to have the package on sys.path.
_PKG_ROOT = Path(__file__).resolve().parents[3]  # plugins/dev-team
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from services.conductor.playbook.types import (  # noqa: E402
    DispatchSpecialist,
    EmitMessage,
    JudgmentSpec,
    Manifest,
    PresentResults,
    SpecialistSpec,
    SpecialtySpec,
    State,
    TeamPlaybook,
    Transition,
)


_BREED_SCHEMA = {
    "type": "object",
    "properties": {
        "candidates": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 10,
        }
    },
    "required": ["candidates"],
}

_BREED_PROMPT = (
    "Suggest 5 puppy names inspired by popular dog breeds. "
    "Return JSON matching the schema: "
    '{{"candidates": ["name1", "name2", ...]}}.'
)


BREED_SPECIALTY = SpecialtySpec(
    name="breed-name-suggester",
    worker_agent="breed-name-worker",
    worker_prompt_template=_BREED_PROMPT,
    response_schema=_BREED_SCHEMA,
    logical_model="fast-cheap",
)

BREED_SPECIALIST = SpecialistSpec(
    name="breed",
    specialties=[BREED_SPECIALTY],
)


STATES = [
    State(
        name="start",
        entry_actions=(
            EmitMessage("Let's find a name for your puppy.", type="notification"),
        ),
    ),
    State(
        name="dispatch_specialists",
        entry_actions=(DispatchSpecialist("breed"),),
    ),
    State(
        name="present",
        entry_actions=(PresentResults("Candidate names:"),),
    ),
    State(name="done", terminal=True),
]

TRANSITIONS = [
    Transition("start", "dispatch_specialists"),
    Transition("dispatch_specialists", "present"),
    Transition("present", "done"),
]

JUDGMENT_SPECS: dict[str, JudgmentSpec] = {}

MANIFEST = Manifest(specialists=[BREED_SPECIALIST])

PLAYBOOK = TeamPlaybook(
    name="name-a-puppy",
    states=STATES,
    transitions=TRANSITIONS,
    judgment_specs=JUDGMENT_SPECS,
    manifest=MANIFEST,
    initial_state="start",
)
