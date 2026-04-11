"""End-to-end: run the name-a-puppy walking skeleton against MockDispatcher.

Success: session reaches `done` state, a single breed result exists with
findings, and the user-facing `present` message contains the candidates.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "dev-team"))

from services.conductor.arbitrator import Arbitrator, SessionStatus  # noqa: E402
from services.conductor.arbitrator.backends import SqliteBackend  # noqa: E402
from services.conductor.conductor import Conductor  # noqa: E402
from services.conductor.dispatcher import MockDispatcher  # noqa: E402
from services.conductor.playbook import load_playbook  # noqa: E402
from services.conductor.team_lead import TeamLead  # noqa: E402


PLAYBOOK_PATH = (
    REPO_ROOT
    / "plugins"
    / "dev-team"
    / "services"
    / "conductor"
    / "playbooks"
    / "name_a_puppy.py"
)


def test_walking_skeleton_runs_end_to_end(tmp_path):
    async def _t():
        playbook = load_playbook(PLAYBOOK_PATH)
        backend = SqliteBackend(tmp_path / "arb.sqlite")
        arbitrator = Arbitrator(backend)
        await arbitrator.start()
        dispatcher = MockDispatcher(
            {
                "breed-name-worker": {
                    "candidates": ["Luna", "Scout", "Rex", "Daisy", "Biscuit"]
                }
            }
        )
        team_lead = TeamLead(playbook)
        session_id = uuid4()
        conductor = Conductor(arbitrator, dispatcher, team_lead, session_id)

        await conductor.run()

        # Session closed successfully.
        row = await backend.fetch_one("session", {"session_id": str(session_id)})
        assert row is not None
        assert row["status"] == SessionStatus.COMPLETED.value

        # Exactly one result, marked passed, with 5 candidate findings.
        results = await arbitrator.list_results(session_id)
        assert len(results) == 1
        r = results[0]
        assert r.specialist_id == "breed"
        assert r.passed is True
        findings_rows = await backend.fetch_all(
            "finding", where={"result_id": r.result_id}
        )
        assert len(findings_rows) == 5
        assert {f["body"] for f in findings_rows} == {
            "Luna",
            "Scout",
            "Rex",
            "Daisy",
            "Biscuit",
        }

        # Three messages: greet, present, (no follow-up in skeleton).
        messages = await arbitrator.list_messages(session_id)
        bodies = [m.body for m in messages]
        assert bodies[0].startswith("Let's find a name")
        present_body = bodies[-1]
        assert "Candidate names:" in present_body
        for candidate in ("Luna", "Scout", "Rex", "Daisy", "Biscuit"):
            assert candidate in present_body

        # Every state was entered and exited (none still active).
        active = await arbitrator.active_state_nodes(session_id)
        assert active == []

        # Events were emitted for state transitions and dispatches.
        events = await arbitrator.list_events(session_id)
        state_enters = [
            e for e in events if e.kind == "state_enter"
        ]
        assert {e.payload_json["state"] for e in state_enters} == {
            "start",
            "dispatch_specialists",
            "present",
            "done",
        }

        await arbitrator.close()

    asyncio.run(_t())
