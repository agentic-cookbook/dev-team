"""name-a-puppy v2 playbook — richer prototype.

Shape: 4 specialists × 2 specialties. Same state-machine grammar as v1
(start → gather_traits ⟳ → dispatch_specialists → aggregate → present →
done), but with a denser manifest that exercises the specialist →
specialty fan-out two levels deep.

Specialists:
    heritage     → breed-inspired-names,        ancestry-inspired-names
    appearance   → coat-color-inspired-names,   physical-feature-inspired-names
    personality  → temperament-inspired-names,  quirk-inspired-names
    identity     → gender-style-names,          general-classic-names
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
    JudgmentSpec,
    Manifest,
    PresentResults,
    SpecialistSpec,
    SpecialtySpec,
    State,
    TeamPlaybook,
    Transition,
)


# ---------------------------------------------------------------------------
# Shared schema — every name-producing specialty returns the same shape.
# ---------------------------------------------------------------------------

_CANDIDATE_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "candidates": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 5,
        }
    },
    "required": ["candidates"],
}


def _specialty(
    name: str, worker_agent: str, instruction: str
) -> SpecialtySpec:
    return SpecialtySpec(
        name=name,
        worker_agent=worker_agent,
        worker_prompt_template=(
            f"{instruction} Base the names on what is known about the "
            "puppy so far (breed, gender, coloring, physical features, "
            "temperament, quirks, family history). Return JSON: "
            '{{"candidates": ["name1", "name2", ...] }} with 3 to 5 items.'
        ),
        response_schema=_CANDIDATE_LIST_SCHEMA,
        logical_model="fast-cheap",
    )


# ---------------------------------------------------------------------------
# Specialists
# ---------------------------------------------------------------------------

HERITAGE_SPECIALIST = SpecialistSpec(
    name="heritage",
    specialties=[
        _specialty(
            "breed-inspired-names",
            "breed-name-worker",
            "Suggest puppy names inspired by the breed(s) the puppy resembles.",
        ),
        _specialty(
            "ancestry-inspired-names",
            "ancestry-name-worker",
            "Suggest puppy names that reference the puppy's family or lineage.",
        ),
    ],
)

APPEARANCE_SPECIALIST = SpecialistSpec(
    name="appearance",
    specialties=[
        _specialty(
            "coat-color-inspired-names",
            "coat-color-name-worker",
            "Suggest puppy names inspired by coat color and markings.",
        ),
        _specialty(
            "physical-feature-inspired-names",
            "physical-feature-name-worker",
            "Suggest puppy names inspired by size, ears, tail, or other physical features.",
        ),
    ],
)

PERSONALITY_SPECIALIST = SpecialistSpec(
    name="personality",
    specialties=[
        _specialty(
            "temperament-inspired-names",
            "temperament-name-worker",
            "Suggest puppy names matching the puppy's temperament.",
        ),
        _specialty(
            "quirk-inspired-names",
            "quirk-name-worker",
            "Suggest puppy names inspired by the puppy's unusual behaviors or quirks.",
        ),
    ],
)

IDENTITY_SPECIALIST = SpecialistSpec(
    name="identity",
    specialties=[
        _specialty(
            "gender-style-names",
            "gender-style-name-worker",
            "Suggest puppy names that read as clearly matching the puppy's gender.",
        ),
        _specialty(
            "general-classic-names",
            "general-classic-name-worker",
            "Suggest classic, timeless dog names that fit the overall profile.",
        ),
    ],
)


# ---------------------------------------------------------------------------
# Judgment specs
# ---------------------------------------------------------------------------

GATHER_TRAITS_JUDGMENT = JudgmentSpec(
    prompt_template=(
        "We are helping the user name a puppy. Decide whether we have "
        "enough about the puppy to name it, or we should ask another "
        "question. We want to know: breed, gender, coloring, physical "
        "features, temperament / behaviors / quirks, and family history. "
        "Session: {session_id}. "
        'Return JSON: {{"next_state": "gather_traits" | "dispatch_specialists", '
        '"question": "optional follow-up question"}}.'
    ),
    response_schema={
        "type": "object",
        "properties": {
            "next_state": {
                "type": "string",
                "enum": ["gather_traits", "dispatch_specialists"],
            },
            "question": {"type": "string"},
        },
        "required": ["next_state"],
    },
    legal_next_states=["gather_traits", "dispatch_specialists"],
    logical_model="balanced",
    agent_name="team-lead-gather",
)

RANK_JUDGMENT = JudgmentSpec(
    prompt_template=(
        "Eight specialties proposed candidate puppy names (~24-40 total). "
        "Read the result rows and return a single ranked list of the top 8 "
        "names. Favor fit to the puppy, memorability, and variety across "
        "categories. "
        'Return JSON: {{"ranked_candidates": ["name1", "name2", ...], '
        '"next_state": "present"}}.'
    ),
    response_schema={
        "type": "object",
        "properties": {
            "ranked_candidates": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "maxItems": 12,
            },
            "next_state": {"type": "string", "enum": ["present"]},
        },
        "required": ["ranked_candidates", "next_state"],
    },
    legal_next_states=["present"],
    logical_model="balanced",
    agent_name="team-lead-aggregator",
)


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------

STATES = [
    State(
        name="start",
        entry_actions=(
            EmitMessage(
                "Let's find a name for your puppy.",
                type="notification",
            ),
        ),
    ),
    State(
        name="gather_traits",
        entry_actions=(
            EmitMessage(
                "Tell me about your puppy — breed, gender, coloring, "
                "physical features, temperament, quirks, family history.",
                type="question",
            ),
        ),
        judgment="ask_next_question",
    ),
    State(
        name="dispatch_specialists",
        entry_actions=(
            DispatchSpecialist("heritage"),
            DispatchSpecialist("appearance"),
            DispatchSpecialist("personality"),
            DispatchSpecialist("identity"),
        ),
    ),
    State(
        name="aggregate",
        entry_actions=(),
        judgment="rank_candidates",
    ),
    State(
        name="present",
        entry_actions=(PresentResults("Top candidate names:"),),
    ),
    State(name="done", terminal=True),
]

TRANSITIONS = [
    Transition("start", "gather_traits"),
    Transition("gather_traits", "gather_traits"),  # loop
    Transition("gather_traits", "dispatch_specialists"),
    Transition("dispatch_specialists", "aggregate"),
    Transition("aggregate", "present"),
    Transition("present", "done"),
    Transition("present", "gather_traits"),  # refine
]

JUDGMENT_SPECS = {
    "ask_next_question": GATHER_TRAITS_JUDGMENT,
    "rank_candidates": RANK_JUDGMENT,
}

MANIFEST = Manifest(
    specialists=[
        HERITAGE_SPECIALIST,
        APPEARANCE_SPECIALIST,
        PERSONALITY_SPECIALIST,
        IDENTITY_SPECIALIST,
    ]
)

PLAYBOOK = TeamPlaybook(
    name="name-a-puppy-v2",
    states=STATES,
    transitions=TRANSITIONS,
    judgment_specs=JUDGMENT_SPECS,
    manifest=MANIFEST,
    initial_state="start",
)
