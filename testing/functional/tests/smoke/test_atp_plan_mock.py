"""Functional smoke — `atp plan devteam --dispatcher mock` end-to-end.

Spawns the CLI as a subprocess and asserts it emits a roadmap_id and
writes plan_nodes into the arbitrator. No real LLM involved.
"""
from __future__ import annotations

import asyncio
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
ATP_CLI = REPO_ROOT / "skills" / "atp" / "scripts" / "atp_cli.py"
TEAMS_ROOT = REPO_ROOT / "teams"

ROADMAP_ID_RE = re.compile(r"^rm_[a-f0-9]+$")


def test_atp_plan_devteam_mock_writes_roadmap(tmp_path):
    db = tmp_path / "atp.sqlite"
    r = subprocess.run(
        [
            sys.executable,
            str(ATP_CLI),
            "--teams-root",
            str(TEAMS_ROOT),
            "plan",
            "devteam",
            "--goal",
            "tiny calculator",
            "--dispatcher",
            "mock",
            "--db",
            str(db),
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert r.returncode == 0, r.stderr
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    assert len(lines) == 1, f"expected roadmap_id on stdout, got {r.stdout!r}"
    roadmap_id = lines[-1]
    assert ROADMAP_ID_RE.match(roadmap_id), roadmap_id

    sys.path.insert(0, str(REPO_ROOT / "plugins" / "dev-team"))
    from services.conductor.arbitrator import Arbitrator
    from services.conductor.arbitrator.backends import SqliteBackend

    async def _count() -> int:
        backend = SqliteBackend(db)
        arb = Arbitrator(backend)
        await arb.start()
        try:
            return len(await arb.list_plan_nodes(roadmap_id))
        finally:
            await arb.close()

    assert asyncio.run(_count()) >= 1
