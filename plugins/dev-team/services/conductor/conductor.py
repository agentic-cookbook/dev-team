"""Conductor main loop — spec §5.1.

One conductor instance per session. Drives a TeamLead through its state
machine, executing each state's entry actions via the arbitrator and
dispatcher. The state tree is persisted on every push/pop so a restart
with the same session_id resumes from the last completed state.

Walking skeleton: single-team, linear advance. The full main loop from
§5.1 (task queue pull, parallel dispatches) lands in step 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from .arbitrator import Arbitrator, SessionStatus
from .dispatcher import Dispatcher
from .playbook.types import (
    Action,
    DispatchSpecialist,
    EmitMessage,
    JudgmentCall,
    PresentResults,
    WaitForUserInput,
)
from .specialist_runner import run_specialist
from .team_lead import TeamLead


@dataclass
class ConductorContext:
    """Ephemeral runtime context passed into action executors."""

    session_id: UUID
    team_id: str
    parent_state_node_id: str | None
    user_inputs: list[str]
    specialty_context: dict[str, Any]


class Conductor:
    def __init__(
        self,
        arbitrator: Arbitrator,
        dispatcher: Dispatcher,
        team_lead: TeamLead,
        session_id: UUID,
    ):
        self._arb = arbitrator
        self._dispatcher = dispatcher
        self._team_lead = team_lead
        self._session_id = session_id
        self._team_id = team_lead.playbook.name
        self._ctx = ConductorContext(
            session_id=session_id,
            team_id=self._team_id,
            parent_state_node_id=None,
            user_inputs=[],
            specialty_context={},
        )

    async def run(self) -> None:
        """Run the session from the initial state to a terminal state."""
        await self._arb.open_session(
            self._session_id, initial_team_id=self._team_id
        )
        current = self._team_lead.initial_state
        while True:
            state = self._team_lead.playbook.state(current)
            node = await self._arb.push_state(
                session_id=self._session_id,
                team_id=self._team_id,
                state_name=state.name,
                parent_node_id=self._ctx.parent_state_node_id,
            )
            prev_parent = self._ctx.parent_state_node_id
            self._ctx.parent_state_node_id = node.node_id
            await self._arb.emit_event(
                session_id=self._session_id,
                team_id=self._team_id,
                kind="state_enter",
                payload={"state": state.name},
            )
            for action in state.entry_actions:
                await self._execute_action(action)
            await self._arb.pop_state(node.node_id)
            self._ctx.parent_state_node_id = prev_parent
            if state.terminal:
                await self._arb.close_session(
                    self._session_id, SessionStatus.COMPLETED
                )
                return
            successors = self._team_lead.playbook.legal_successors(current)
            if not successors:
                await self._arb.close_session(
                    self._session_id, SessionStatus.FAILED
                )
                raise RuntimeError(
                    f"Non-terminal state {current!r} has no successors"
                )
            current = successors[0]
            self._team_lead.validate_transition(state.name, current)

    async def _execute_action(self, action: Action) -> None:
        if isinstance(action, EmitMessage):
            await self._arb.create_message(
                session_id=self._session_id,
                team_id=self._team_id,
                direction="out",
                type=action.type,
                body=action.body,
            )
            return
        if isinstance(action, WaitForUserInput):
            return
        if isinstance(action, DispatchSpecialist):
            spec = self._team_lead.playbook.manifest.get(action.specialist_name)
            await run_specialist(
                arbitrator=self._arb,
                dispatcher=self._dispatcher,
                session_id=self._session_id,
                team_id=self._team_id,
                specialist=spec,
                context=self._ctx.specialty_context,
                parent_state_node_id=self._ctx.parent_state_node_id,
            )
            return
        if isinstance(action, PresentResults):
            results = await self._arb.list_results(self._session_id, self._team_id)
            lines = [action.header]
            for r in results:
                findings = r.summary_json.get("findings", [])
                for f in findings:
                    lines.append(f"- {f.get('body', f)}")
            await self._arb.create_message(
                session_id=self._session_id,
                team_id=self._team_id,
                direction="out",
                type="notification",
                body="\n".join(lines),
            )
            return
        if isinstance(action, JudgmentCall):
            # Judgment calls land in step 2. For the walking skeleton, a
            # judgment action is a no-op so playbooks can declare it without
            # the conductor stumbling.
            return
        raise TypeError(f"Unknown action type: {type(action).__name__}")
