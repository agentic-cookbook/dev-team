"""Fixtures for agenticteam conversion tests."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = REPO_ROOT / "plugins" / "dev-team" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(
        name, SCRIPTS / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def tree_to_agenticteam():
    return _load("tree_to_agenticteam")


@pytest.fixture
def agenticteam_to_tree():
    return _load("agenticteam_to_tree")


@pytest.fixture
def mini_team(tmp_path: Path) -> Path:
    """Build a minimal valid teams/<name>/ tree on disk."""
    root = tmp_path / "toyteam"
    (root / "team-leads").mkdir(parents=True)
    (root / "specialists" / "alpha" / "specialities").mkdir(parents=True)
    (root / "team.md").write_text("# Toy Team\nWe do toys.", encoding="utf-8")
    (root / "team-leads" / "lead.md").write_text(
        "---\nrole: lead\n---\n# Lead\nLeads.", encoding="utf-8",
    )
    (root / "specialists" / "alpha" / "specialist.md").write_text(
        "---\nname: alpha\n---\nAlpha specialist.", encoding="utf-8",
    )
    (root / "specialists" / "alpha" / "specialities" / "one.md").write_text(
        "---\nname: one\nartifact: guidelines/toys.md\n---\n"
        "## Worker Focus\nBuild toys.\n\n## Verify\nToys pass.",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def mini_refs(tmp_path: Path) -> list[Path]:
    """Reference pool containing one guideline file."""
    g = tmp_path / "refs" / "guidelines"
    g.mkdir(parents=True)
    (g / "toys.md").write_text("# Toys\nAll about toys.", encoding="utf-8")
    return [tmp_path / "refs"]
