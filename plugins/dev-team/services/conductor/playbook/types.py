"""Team-playbook declarative types — spec §5.5.

Declarations, not programs. Authors express a team as data: states,
transitions, judgment specs, manifest, actions. No imperative business logic
in state declarations; actions are first-class value objects the conductor
executes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Action objects — executed by the conductor when a state is entered.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Action:
    """Marker base class. Every action is an immutable value object."""


@dataclass(frozen=True)
class EmitMessage(Action):
    """Write a `message` row to the arbitrator.

    direction: "out" (team-lead → user). type: "notification" | "question".
    """

    body: str
    type: str = "notification"


@dataclass(frozen=True)
class WaitForUserInput(Action):
    """Pause the state machine until the next user-direction message arrives."""

    prompt: str | None = None


@dataclass(frozen=True)
class JudgmentCall(Action):
    """Invoke a named JudgmentSpec via the dispatcher.

    The response's `next_state` field drives the transition. The judgment
    spec's legal_next_states guards the transition's legality.
    """

    spec_name: str


@dataclass(frozen=True)
class DispatchSpecialist(Action):
    """Dispatch a specialist by manifest name. Push a child state node."""

    specialist_name: str


@dataclass(frozen=True)
class PresentResults(Action):
    """Aggregate result rows for this session and emit a final notification."""

    header: str = "Results"


# ---------------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class State:
    name: str
    entry_actions: tuple[Action, ...] = ()
    judgment: str | None = None  # name of a JudgmentSpec invoked on entry
    terminal: bool = False


@dataclass(frozen=True)
class Transition:
    from_state: str
    to_state: str


@dataclass
class JudgmentSpec:
    prompt_template: str
    response_schema: dict[str, Any]
    legal_next_states: list[str]
    logical_model: str = "balanced"
    agent_name: str = "team-lead-judgment"


# ---------------------------------------------------------------------------
# Manifest — specialists and specialties the team uses
# ---------------------------------------------------------------------------


@dataclass
class SpecialtySpec:
    name: str
    worker_agent: str  # AgentDefinition.name
    worker_prompt_template: str
    response_schema: dict[str, Any]
    logical_model: str = "balanced"


@dataclass
class SpecialistSpec:
    name: str
    specialties: list[SpecialtySpec]


@dataclass
class Manifest:
    specialists: list[SpecialistSpec] = field(default_factory=list)

    def get(self, specialist_name: str) -> SpecialistSpec:
        for s in self.specialists:
            if s.name == specialist_name:
                return s
        raise KeyError(f"Specialist {specialist_name!r} not in manifest")


# ---------------------------------------------------------------------------
# TeamPlaybook
# ---------------------------------------------------------------------------


@dataclass
class TeamPlaybook:
    name: str
    states: list[State]
    transitions: list[Transition]
    judgment_specs: dict[str, JudgmentSpec]
    manifest: Manifest
    initial_state: str

    def state(self, name: str) -> State:
        for s in self.states:
            if s.name == name:
                return s
        raise KeyError(f"State {name!r} not declared")

    def legal_successors(self, from_state: str) -> list[str]:
        return [t.to_state for t in self.transitions if t.from_state == from_state]

    def is_legal_transition(self, from_state: str, to_state: str) -> bool:
        return to_state in self.legal_successors(from_state)
