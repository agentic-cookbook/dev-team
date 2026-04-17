"""End-to-end: run the full name-a-puppy-v2 flow against MockDispatcher.

Covers: parallel specialist dispatch (4 specialists), each running two
specialties in parallel, judgment-driven transitions, state-tree push/pop
discipline across a denser fan-out, aggregation ranking, gate resolution,
session completion.
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
    / "name_a_puppy_v2.py"
)


RANKED_TOP_8 = [
    "Luna",
    "Scout",
    "Rex",
    "Daisy",
    "Biscuit",
    "Cocoa",
    "Pepper",
    "Sage",
]


def _build_dispatcher() -> MockDispatcher:
    return MockDispatcher(
        {
            "team-lead-gather": {"next_state": "dispatch_specialists"},
            "team-lead-aggregator": {
                "ranked_candidates": RANKED_TOP_8,
                "next_state": "present",
            },
            # Heritage
            "breed-name-worker": {"candidates": ["Rex", "Dash", "Biscuit"]},
            "ancestry-name-worker": {"candidates": ["Sage", "Echo", "Juno"]},
            # Appearance
            "coat-color-name-worker": {"candidates": ["Cocoa", "Shadow", "Snow"]},
            "physical-feature-name-worker": {
                "candidates": ["Tiny", "Floppy", "Patch"]
            },
            # Personality
            "temperament-name-worker": {"candidates": ["Luna", "Daisy", "Ollie"]},
            "quirk-name-worker": {"candidates": ["Goofy", "Ziggy", "Pip"]},
            # Identity
            "gender-style-name-worker": {"candidates": ["Scout", "Rosie", "Max"]},
            "general-classic-name-worker": {
                "candidates": ["Pepper", "Charlie", "Bailey"]
            },
        }
    )


def test_full_name_a_puppy_v2_end_to_end(tmp_path):
    async def _t():
        playbook = load_playbook(PLAYBOOK_PATH)
        backend = SqliteBackend(tmp_path / "arb.sqlite")
        arbitrator = Arbitrator(backend)
        await arbitrator.start()
        dispatcher = _build_dispatcher()
        team_lead = TeamLead(playbook)
        session_id = uuid4()
        conductor = Conductor(arbitrator, dispatcher, team_lead, session_id)

        await conductor.run()

        row = await backend.fetch_one(
            "session", {"session_id": str(session_id)}
        )
        assert row is not None
        assert row["status"] == SessionStatus.COMPLETED.value

        # Four specialists → four aggregated results (each folds two
        # specialties' candidates into summary_json.findings).
        results = await arbitrator.list_results(session_id)
        assert {r.specialist_id for r in results} == {
            "heritage",
            "appearance",
            "personality",
            "identity",
        }
        assert len(results) == 4
        assert all(r.passed for r in results)
        # Each specialist's result aggregates both specialties' 3 candidates.
        for r in results:
            findings = r.summary_json.get("findings", [])
            assert len(findings) == 6, (
                f"{r.specialist_id}: expected 6 aggregated findings, got {len(findings)}"
            )

        # Ranked list appears in the final present notification.
        messages = await arbitrator.list_messages(session_id)
        bodies = [m.body for m in messages]
        present_body = bodies[-1]
        assert "Top candidate names:" in present_body
        for i, name in enumerate(RANKED_TOP_8, 1):
            assert f"{i}. {name}" in present_body

        # Gate resolved accept → done.
        gate_rows = await backend.fetch_all(
            "gate", where={"session_id": str(session_id)}
        )
        assert len(gate_rows) == 1
        assert gate_rows[0]["verdict"] == "accept"
        assert gate_rows[0]["verdict_date"] is not None

        # State tree: every node popped.
        active = await arbitrator.active_state_nodes(session_id)
        assert active == []

        # 4 specialist nodes, 8 specialty nodes.
        all_state_rows = await backend.fetch_all(
            "state", where={"session_id": str(session_id)}
        )
        specialist_nodes = [
            r for r in all_state_rows if r["state_name"].startswith("specialist:")
        ]
        assert len(specialist_nodes) == 4
        specialty_nodes = [
            r for r in all_state_rows if r["state_name"].startswith("specialty:")
        ]
        assert len(specialty_nodes) == 8
        specialist_ids = {n["node_id"] for n in specialist_nodes}
        for sn in specialty_nodes:
            assert sn["parent_node_id"] in specialist_ids

        # Top-level state enters hit every declared state.
        events = await arbitrator.list_events(session_id)
        state_enters = [e for e in events if e.kind == "state_enter"]
        entered = [e.payload_json["state"] for e in state_enters]
        assert entered == [
            "start",
            "gather_traits",
            "dispatch_specialists",
            "aggregate",
            "present",
            "done",
        ]

        await arbitrator.close()

    asyncio.run(_t())


def test_v2_parallel_dispatch_is_concurrent(tmp_path):
    """Four DispatchSpecialist × two specialties each run concurrently."""

    async def _t():
        import time

        playbook = load_playbook(PLAYBOOK_PATH)
        backend = SqliteBackend(tmp_path / "arb.sqlite")
        arbitrator = Arbitrator(backend)
        await arbitrator.start()

        # If fully serial: 8 × 0.1 = 0.80s. If concurrent: ~0.10s.
        class SlowMock(MockDispatcher):
            async def dispatch(self, *args, **kwargs):  # type: ignore[override]
                agent = kwargs.get("agent") or args[0]
                if agent.name.endswith("-name-worker"):
                    await asyncio.sleep(0.1)
                return await super().dispatch(*args, **kwargs)

        slow = SlowMock(
            {
                "team-lead-gather": {"next_state": "dispatch_specialists"},
                "team-lead-aggregator": {
                    "ranked_candidates": ["A", "B", "C"],
                    "next_state": "present",
                },
                "breed-name-worker": {"candidates": ["A"]},
                "ancestry-name-worker": {"candidates": ["B"]},
                "coat-color-name-worker": {"candidates": ["C"]},
                "physical-feature-name-worker": {"candidates": ["D"]},
                "temperament-name-worker": {"candidates": ["E"]},
                "quirk-name-worker": {"candidates": ["F"]},
                "gender-style-name-worker": {"candidates": ["G"]},
                "general-classic-name-worker": {"candidates": ["H"]},
            }
        )
        team_lead = TeamLead(playbook)
        session_id = uuid4()
        conductor = Conductor(arbitrator, slow, team_lead, session_id)
        start = time.monotonic()
        await conductor.run()
        elapsed = time.monotonic() - start
        # Generous bound: concurrent should be well under 0.4s; fully
        # serial would be > 0.80s.
        assert elapsed < 0.4, (
            f"Expected concurrent dispatch; took {elapsed:.2f}s"
        )
        await arbitrator.close()

    asyncio.run(_t())
