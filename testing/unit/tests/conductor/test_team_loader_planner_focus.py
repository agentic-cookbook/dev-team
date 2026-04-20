"""team_loader must expose a `planner_focus` on SpecialtyDef.

When the speciality markdown has a `## Planner Focus` section, the
loader should populate the field verbatim. When absent, the loader
should fall back to `worker_focus` so planner dispatches never get
an empty prompt.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "dev-team"))

from services.conductor.team_loader import load_team  # noqa: E402


FIXTURE = REPO_ROOT / "testing" / "fixtures" / "teams" / "plan_fixture"


def test_planner_focus_populated_from_section():
    manifest = load_team(FIXTURE)
    design = manifest.specialists["architect"].specialties["design"]
    assert design.planner_focus == (
        "Enumerate plan_nodes for architecture design work needed to "
        "reach the goal."
    )


def test_planner_focus_falls_back_to_worker_focus():
    manifest = load_team(FIXTURE)
    draft = manifest.specialists["writer"].specialties["draft"]
    assert draft.planner_focus == draft.worker_focus
    assert draft.planner_focus == "Draft the documentation."
