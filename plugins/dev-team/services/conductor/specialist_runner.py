"""Specialist runner — dispatches the worker/verifier pair for each specialty.

Walking skeleton: worker-only. Verifier is wired in step 2 of the build
order. For now, a specialist runs each specialty's worker once, collects
structured findings, writes a result row, and returns `{result_id, passed}`
to the team-lead.
"""
from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from .arbitrator import Arbitrator, Result
from .dispatcher import (
    AgentDefinition,
    DispatchCorrelation,
    DispatchError,
    Dispatcher,
)
from .playbook.types import SpecialistSpec


async def run_specialist(
    arbitrator: Arbitrator,
    dispatcher: Dispatcher,
    session_id: UUID,
    team_id: str,
    specialist: SpecialistSpec,
    context: dict[str, Any],
    parent_state_node_id: str | None,
) -> Result:
    """Run every specialty in the specialist and write a result row."""
    state_node = await arbitrator.push_state(
        session_id=session_id,
        team_id=team_id,
        state_name=f"specialist:{specialist.name}",
        parent_node_id=parent_state_node_id,
    )

    all_findings: list[dict[str, Any]] = []
    passed = True

    for specialty in specialist.specialties:
        child_node = await arbitrator.push_state(
            session_id=session_id,
            team_id=team_id,
            state_name=f"specialty:{specialty.name}",
            parent_node_id=state_node.node_id,
        )
        dispatch_id = f"disp_{uuid.uuid4().hex[:8]}"
        prompt = specialty.worker_prompt_template.format(**context)
        agent = AgentDefinition(
            name=specialty.worker_agent,
            prompt="You are a focused worker. Respond with valid JSON only.",
            logical_model=specialty.logical_model,
        )
        correlation = DispatchCorrelation(
            session_id=session_id,
            team_id=team_id,
            agent_id=specialty.worker_agent,
            dispatch_id=dispatch_id,
        )

        async def sink(evt: dict[str, Any]) -> None:
            await arbitrator.emit_event(
                session_id=session_id,
                team_id=team_id,
                kind=evt.get("kind", evt.get("type", "event")),
                payload=evt,
                agent_id=specialty.worker_agent,
                dispatch_id=dispatch_id,
            )

        try:
            result = await dispatcher.dispatch(
                agent=agent,
                prompt=prompt,
                logical_model=specialty.logical_model,
                response_schema=specialty.response_schema,
                correlation=correlation,
                event_sink=sink,
            )
        except DispatchError as e:
            passed = False
            await arbitrator.emit_event(
                session_id=session_id,
                team_id=team_id,
                kind="specialty_failed",
                payload={"specialty": specialty.name, "error": str(e)},
            )
            await arbitrator.pop_state(child_node.node_id)
            continue

        findings_payload = _extract_findings(result.response)
        all_findings.extend(findings_payload)
        await arbitrator.pop_state(child_node.node_id)

    result_row = await arbitrator.create_result(
        session_id=session_id,
        team_id=team_id,
        specialist_id=specialist.name,
        passed=passed,
        summary={"findings": all_findings},
    )
    for f in all_findings:
        await arbitrator.create_finding(
            result_id=result_row.result_id,
            kind=f.get("kind", "note"),
            severity=f.get("severity", "info"),
            body=f.get("body", str(f)),
            source_artifact=f.get("source_artifact"),
        )

    await arbitrator.pop_state(state_node.node_id)
    return result_row


def _extract_findings(response: Any) -> list[dict[str, Any]]:
    """Coerce a specialty's structured response into a list of findings."""
    if isinstance(response, dict):
        if "findings" in response and isinstance(response["findings"], list):
            return [
                f if isinstance(f, dict) else {"body": str(f)}
                for f in response["findings"]
            ]
        if "candidates" in response and isinstance(response["candidates"], list):
            return [
                {"kind": "candidate", "severity": "info", "body": str(c)}
                for c in response["candidates"]
            ]
        return [{"kind": "note", "severity": "info", "body": str(response)}]
    if isinstance(response, list):
        return [
            f if isinstance(f, dict) else {"body": str(f)}
            for f in response
        ]
    return [{"kind": "note", "severity": "info", "body": str(response)}]
