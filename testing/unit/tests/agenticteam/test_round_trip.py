"""tree → bundle → tree preserves the team's structural content."""
from __future__ import annotations

import json
from pathlib import Path


def _relpaths(root: Path) -> set[str]:
    return {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and not p.name.startswith(".")
    }


def test_round_trip_preserves_markdown_layout(
    tree_to_agenticteam, agenticteam_to_tree, mini_team, mini_refs, tmp_path
):
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    tree_to_agenticteam.seal_bundle(doc, mini_refs, bundle)

    restored = tmp_path / "restored"
    team_doc = json.loads((bundle / "team.json").read_text())
    agenticteam_to_tree.write_tree(team_doc, restored)

    tracked_src = {
        p for p in _relpaths(mini_team)
        if not p.startswith("index.md") and "team-leads/index.md" not in p
    }
    tracked_dst = _relpaths(restored)
    for path in tracked_src:
        assert path in tracked_dst, f"missing after round-trip: {path}"


def test_round_trip_preserves_specialty_frontmatter_and_sections(
    tree_to_agenticteam, agenticteam_to_tree, mini_team, mini_refs, tmp_path
):
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    tree_to_agenticteam.seal_bundle(doc, mini_refs, bundle)

    restored = tmp_path / "restored"
    team_doc = json.loads((bundle / "team.json").read_text())
    agenticteam_to_tree.write_tree(team_doc, restored)

    specialty = (
        restored / "specialists" / "alpha" / "specialities" / "one.md"
    ).read_text(encoding="utf-8")
    assert "artifact: guidelines/toys.md" in specialty
    assert "## Worker Focus" in specialty
    assert "## Verify" in specialty
