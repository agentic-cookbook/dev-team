"""tree_to_agenticteam produces a bundle dir with team.json + sealed refs."""
from __future__ import annotations

import json


def test_bundle_has_team_json_and_required_fields(
    tree_to_agenticteam, mini_team, mini_refs, tmp_path
):
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    tree_to_agenticteam.seal_bundle(doc, mini_refs, bundle)

    data = json.loads((bundle / "team.json").read_text())
    assert data["kind"] == "agenticteam"
    assert data["schema_version"] == 2
    assert data["name"] == "toyteam"
    assert len(data["specialists"]) == 1
    assert data["specialists"][0]["specialties"][0]["artifact_kind"] == "reference_resolved"


def test_bundle_copies_referenced_files_at_declared_paths(
    tree_to_agenticteam, mini_team, mini_refs, tmp_path
):
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    stats = tree_to_agenticteam.seal_bundle(doc, mini_refs, bundle)

    assert stats["resolved"] == 1
    assert stats["unresolved"] == 0
    assert stats["files_copied"] == 1
    assert (bundle / "guidelines" / "toys.md").is_file()


def test_unresolved_artifact_marked_and_no_file_copied(
    tree_to_agenticteam, mini_team, tmp_path
):
    """Empty ref pool → artifact unresolvable → marked, no file copy."""
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    stats = tree_to_agenticteam.seal_bundle(doc, [], bundle)
    assert stats["unresolved"] == 1
    assert stats["files_copied"] == 0
    assert not (bundle / "guidelines").exists()
    kinds = [
        s["artifact_kind"]
        for sp in doc["specialists"] for s in sp["specialties"]
    ]
    assert kinds == ["reference_unresolved"]
