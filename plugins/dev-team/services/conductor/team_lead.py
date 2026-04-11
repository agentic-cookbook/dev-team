"""Team-lead — state machine driver (spec §5.4).

A team-lead is an instantiation of a playbook. The conductor asks it
"given the current state, what's next?" and it returns the entry actions
for that state plus its name. Judgment calls are executed by the conductor
and the resulting `next_state` is validated against the playbook's
legal successors before the transition is committed.
"""
from __future__ import annotations

from dataclasses import dataclass

from .playbook.types import Action, State, TeamPlaybook


@dataclass
class StepPlan:
    state: State
    actions: tuple[Action, ...]


class TeamLead:
    def __init__(self, playbook: TeamPlaybook):
        self._playbook = playbook

    @property
    def playbook(self) -> TeamPlaybook:
        return self._playbook

    @property
    def initial_state(self) -> str:
        return self._playbook.initial_state

    def plan_for(self, state_name: str) -> StepPlan:
        state = self._playbook.state(state_name)
        return StepPlan(state=state, actions=state.entry_actions)

    def validate_transition(self, from_state: str, to_state: str) -> None:
        if not self._playbook.is_legal_transition(from_state, to_state):
            legal = self._playbook.legal_successors(from_state)
            raise ValueError(
                f"Illegal transition {from_state!r} → {to_state!r}; "
                f"legal successors: {legal}"
            )
