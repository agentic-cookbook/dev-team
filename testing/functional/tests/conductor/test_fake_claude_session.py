"""Run a full name-a-puppy session through ClaudeCodeDispatcher + fake binary.

This is the only test in the suite that exercises the dispatcher subprocess
lifecycle end-to-end against a real playbook. It proves the dispatcher
abstraction boundary: the conductor does not know the subprocess is a fake.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest

from conftest import FAKE_BIN, PLAYBOOK_PATH  # type: ignore[import-not-found]

from services.conductor.arbitrator import Arbitrator, SessionStatus
from services.conductor.arbitrator.backends import SqliteBackend
from services.conductor.conductor import Conductor
from services.conductor.dispatcher.claude_code import ClaudeCodeDispatcher
from services.conductor.playbook import load_playbook
from services.conductor.team_lead import TeamLead


def _agent_map() -> dict:
    def script(payload: dict) -> dict:
        return {
            "events": [
                {"type": "progress", "text": "thinking"},
                {"type": "result", "structured_output": payload},
            ]
        }

    return {
        "team-lead-gather": script({"next_state": "dispatch_specialists"}),
        "team-lead-aggregator": script(
            {
                "ranked_candidates": [
                    "Luna",
                    "Scout",
                    "Rex",
                    "Daisy",
                    "Biscuit",
                ],
                "next_state": "present",
            }
        ),
        "breed-name-worker": script({"candidates": ["Rex", "Dash", "Biscuit"]}),
        "lifestyle-name-worker": script(
            {"candidates": ["Scout", "River", "Sage"]}
        ),
        "temperament-name-worker": script(
            {"candidates": ["Luna", "Daisy", "Ollie"]}
        ),
    }


def test_name_a_puppy_against_fake_claude_subprocess(tmp_path):
    agent_map_path = tmp_path / "agents.json"
    agent_map_path.write_text(json.dumps(_agent_map()), encoding="utf-8")

    env_backup = dict(os.environ)
    os.environ["FAKE_CLAUDE_AGENT_MAP"] = str(agent_map_path)

    async def _t():
        playbook = load_playbook(PLAYBOOK_PATH)
        backend = SqliteBackend(tmp_path / "arb.sqlite")
        arb = Arbitrator(backend)
        await arb.start()
        dispatcher = ClaudeCodeDispatcher(claude_bin=str(FAKE_BIN))
        team_lead = TeamLead(playbook)
        session_id = uuid4()
        conductor = Conductor(arb, dispatcher, team_lead, session_id)

        await conductor.run()

        row = await backend.fetch_one(
            "session", {"session_id": str(session_id)}
        )
        assert row["status"] == SessionStatus.COMPLETED.value

        # Three specialist result rows landed.
        results = await arb.list_results(session_id)
        assert {r.specialist_id for r in results} == {
            "breed",
            "lifestyle",
            "temperament",
        }
        assert all(r.passed for r in results)

        # Final presentation message contains the ranked names.
        messages = await arb.list_messages(session_id)
        body = messages[-1].body
        for name in ["Luna", "Scout", "Rex", "Daisy", "Biscuit"]:
            assert name in body

        # Gate resolved accept → done.
        gates = await backend.fetch_all(
            "gate", where={"session_id": str(session_id)}
        )
        assert len(gates) == 1
        assert gates[0]["verdict"] == "accept"

        # State tree balanced.
        assert await arb.active_state_nodes(session_id) == []

        # Each subprocess dispatch emits one `progress` + one `result`
        # event to the arbitrator. We expect 5 dispatches:
        # gather + 3 specialty workers + aggregator.
        events = await arb.list_events(session_id)
        kinds = [e.kind for e in events]
        assert kinds.count("progress") == 5
        assert kinds.count("result") == 5

        await arb.close()

    try:
        asyncio.run(_t())
    finally:
        os.environ.clear()
        os.environ.update(env_backup)
