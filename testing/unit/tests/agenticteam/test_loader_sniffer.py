"""`load_team` picks the agenticteam loader when the root is a bundle."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "dev-team"))

from services.conductor.team_loader import load_team  # noqa: E402


def test_load_team_reads_bundle(
    tree_to_agenticteam, mini_team, mini_refs, tmp_path
):
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    tree_to_agenticteam.seal_bundle(doc, mini_refs, bundle)

    manifest = load_team(bundle)
    assert manifest.name == "toyteam"
    assert "alpha" in manifest.specialists
    assert "one" in manifest.specialists["alpha"].specialties
    assert manifest.specialists["alpha"].specialties["one"].worker_focus \
        == "Build toys."


def test_load_team_still_reads_markdown_tree(mini_team):
    manifest = load_team(mini_team)
    assert "alpha" in manifest.specialists
