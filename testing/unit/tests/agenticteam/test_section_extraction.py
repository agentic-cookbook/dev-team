"""Section extractors in tree_to_agenticteam.py carve authored markdown
into the structured fields that schema v2 expects."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = REPO_ROOT / "plugins" / "dev-team" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tt = _load("tree_to_agenticteam")


SPECIALIST_MD = """\
---
name: platform-database
description: Database specialist.
---
# Database Specialist

## Role
Schema design and indexing.

## Persona

### Archetype
Methodical DBA.

### Voice
Direct.

### Priorities
Correctness over speed.

## Cookbook Sources
- `guidelines/database-design/indexing.md`
- `guidelines/database-design/normalization.md`

## Manifest
- specialities/indexing.md

## Exploratory Prompts

1. What's your weakest index?

2. What happens under network partition?
"""


TEAM_LEAD_MD = """\
# Analysis Lead

## Role
Coordinate specialist dispatch.

## Persona

### Archetype
TPM.

### Voice
Structured.

### Priorities
Signal over noise.

## Phases
- scan — survey the target
- dispatch — run specialists
- report — summarise findings

## Interaction Style
- Only member who talks to the user
- Presents summary first
"""


SPECIALTY_MD = """\
---
name: indexing
description: Index strategy review.
artifact: guidelines/database-design/indexing.md
---

## Worker Focus
Review composite vs partial indexes.

## Verify
Query plans use the proposed indexes.
"""


def test_specialty_extracts_worker_focus_and_verify(tmp_path: Path):
    p = tmp_path / "indexing.md"
    p.write_text(SPECIALTY_MD)
    out = tt._specialty(p)
    assert out["name"] == "indexing"
    assert out["worker_focus"].startswith("Review composite")
    assert out["verify"].startswith("Query plans")
    assert "body" not in out
    assert out["frontmatter"]["artifact"] == "guidelines/database-design/indexing.md"


def test_specialist_extracts_role_persona_sources_prompts(tmp_path: Path):
    sp_dir = tmp_path / "platform-database"
    sp_dir.mkdir()
    (sp_dir / "specialist.md").write_text(SPECIALIST_MD)
    (sp_dir / "specialities").mkdir()
    (sp_dir / "specialities" / "indexing.md").write_text(SPECIALTY_MD)

    out = tt._specialist(sp_dir)
    assert out["role"].startswith("Schema design")
    assert out["persona"] == {
        "archetype": "Methodical DBA.",
        "voice": "Direct.",
        "priorities": "Correctness over speed.",
    }
    assert out["sources"] == [
        "guidelines/database-design/indexing.md",
        "guidelines/database-design/normalization.md",
    ]
    assert len(out["exploratory_prompts"]) == 2
    assert out["exploratory_prompts"][0].startswith("What's your weakest index")
    assert len(out["specialties"]) == 1


def test_team_lead_extracts_phases_and_interaction_style(tmp_path: Path):
    p = tmp_path / "analysis.md"
    p.write_text(TEAM_LEAD_MD)
    out = tt._team_lead(p)
    assert out["role"] == "Coordinate specialist dispatch."
    assert out["persona"]["voice"] == "Structured."
    assert out["phases"] == [
        {"name": "scan", "description": "survey the target"},
        {"name": "dispatch", "description": "run specialists"},
        {"name": "report", "description": "summarise findings"},
    ]
    assert out["interaction_style"] == [
        "Only member who talks to the user",
        "Presents summary first",
    ]


def test_persona_with_unstructured_placeholder(tmp_path: Path):
    md = """\
# X
## Role
Does a thing.

## Persona
(coming)
"""
    p = tmp_path / "x" / "specialist.md"
    p.parent.mkdir()
    p.write_text(md)
    out = tt._specialist_like(p.parent, "specialist.md")
    assert out["persona"] == {"archetype": "(coming)"}


def test_specialty_body_field_is_dropped(tmp_path: Path):
    p = tmp_path / "indexing.md"
    p.write_text(SPECIALTY_MD)
    out = tt._specialty(p)
    assert "body" not in out


def test_schema_version_is_2(tmp_path: Path):
    # Minimal valid team tree.
    team = tmp_path / "toy"
    (team / "team-leads").mkdir(parents=True)
    (team / "specialists" / "alpha" / "specialities").mkdir(parents=True)
    (team / "team.md").write_text("# Toy\n## Role\nDoes toys.")
    (team / "team-leads" / "lead.md").write_text("# Lead\n## Role\nLeads.")
    (team / "specialists" / "alpha" / "specialist.md").write_text(
        "# Alpha\n## Role\nAlpha work."
    )
    (team / "specialists" / "alpha" / "specialities" / "one.md").write_text(
        "## Worker Focus\nDo.\n\n## Verify\nOk."
    )
    doc = tt.convert_team(team)
    assert doc["schema_version"] == 2
    assert doc["kind"] == "agenticteam"
    assert doc["role"] == "Does toys."
    assert doc["specialists"][0]["role"] == "Alpha work."
    assert doc["team_leads"][0]["role"] == "Leads."
