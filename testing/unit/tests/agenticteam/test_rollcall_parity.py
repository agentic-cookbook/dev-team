"""Tree-loaded vs bundle-loaded manifests must agree on every specialty.

Guards against silent drift between the markdown-tree path and the
bundle path in services/conductor/team_loader.load_team.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "dev-team"))

from services.conductor.team_loader import load_team  # noqa: E402


def _flatten(manifest):
    """Return a stable dict keyed by (specialist, specialty) for diffing."""
    out = {}
    for sp in manifest.specialists.values():
        for st in sp.specialties.values():
            out[(sp.name, st.name)] = (
                st.description, st.worker_focus, st.verify, st.logical_model,
            )
    return out


def test_tree_and_bundle_manifests_agree(
    tree_to_agenticteam, mini_team, mini_refs, tmp_path
):
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    tree_to_agenticteam.seal_bundle(doc, mini_refs, bundle)

    tree_manifest = load_team(mini_team)
    bundle_manifest = load_team(bundle)

    assert tree_manifest.name == bundle_manifest.name
    assert _flatten(tree_manifest) == _flatten(bundle_manifest)


def test_live_devteam_tree_and_bundle_agree():
    """Smoke: the sealed devteam bundle matches its source tree. Skips if
    either shape is missing (e.g. running on a checkout that hasn't
    generated the bundle yet)."""
    tree = REPO_ROOT / "teams" / "devteam"
    bundle = REPO_ROOT / "teams" / "devteam.agenticteam"
    if not tree.is_dir() or not bundle.is_dir():
        import pytest
        pytest.skip("devteam tree or bundle not present")

    tree_manifest = load_team(tree)
    bundle_manifest = load_team(bundle)
    assert _flatten(tree_manifest) == _flatten(bundle_manifest)
