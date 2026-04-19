"""team.json conforms to agenticteam.schema.json. Stdlib-only checks to
avoid pulling in jsonschema as a dependency."""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA = json.loads(
    (REPO_ROOT / "plugins" / "dev-team" / "schemas" / "agenticteam.schema.json")
    .read_text(encoding="utf-8")
)


def _required(obj, keys, label):
    missing = [k for k in keys if k not in obj]
    assert not missing, f"{label} missing {missing}"


def test_generated_team_json_has_required_top_level_fields(
    tree_to_agenticteam, mini_team, mini_refs, tmp_path
):
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    tree_to_agenticteam.seal_bundle(doc, mini_refs, bundle)

    data = json.loads((bundle / "team.json").read_text())
    _required(data, SCHEMA["required"], "team.json")
    assert data["kind"] == SCHEMA["properties"]["kind"]["const"]
    assert data["schema_version"] == SCHEMA["properties"]["schema_version"]["const"]


def test_every_specialty_has_name(tree_to_agenticteam, mini_team, mini_refs, tmp_path):
    bundle = tmp_path / "toy.agenticteam"
    doc = tree_to_agenticteam.convert_team(mini_team)
    tree_to_agenticteam.seal_bundle(doc, mini_refs, bundle)
    data = json.loads((bundle / "team.json").read_text())
    for sp in data["specialists"]:
        _required(sp, ["name", "specialties"], f"specialist {sp.get('name')}")
        for st in sp["specialties"]:
            _required(st, ["name"], f"specialty in {sp['name']}")
