"""Inverse of tree_to_agenticteam: write a .agenticteam bundle (schema v2)
back as a teams/<name>/ markdown tree. Used by round-trip tests; not part
of the loader path.

Run:
    agenticteam_to_tree.py <bundle_dir> <team_root>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _fmt_frontmatter(fm: dict) -> str:
    if not fm:
        return ""
    lines = [f"{k}: {v}" for k, v in fm.items()]
    return "---\n" + "\n".join(lines) + "\n---\n"


def _write_md(path: Path, frontmatter: dict, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = _fmt_frontmatter(frontmatter or {})
    payload = fm + (body or "")
    path.write_text(payload, encoding="utf-8")


def _persona_md(persona: dict) -> str:
    if not persona:
        return ""
    lines = ["## Persona", ""]
    for key, label in (("archetype", "Archetype"), ("voice", "Voice"), ("priorities", "Priorities")):
        val = persona.get(key)
        if val:
            lines.extend([f"### {label}", val, ""])
    return "\n".join(lines).rstrip() + "\n"


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) + "\n"


def _phases_md(phases: list[dict]) -> str:
    out = []
    for p in phases:
        name = p.get("name", "")
        desc = p.get("description")
        out.append(f"- {name} — {desc}" if desc else f"- {name}")
    return "\n".join(out) + "\n"


def _numbered(items: list[str]) -> str:
    return "\n\n".join(f"{i}. {item}" for i, item in enumerate(items, 1)) + "\n"


def _team_lead_body(lead: dict) -> str:
    parts: list[str] = []
    name_title = lead["name"].replace("-", " ").title()
    parts.append(f"# {name_title} Team-Lead\n")
    if lead.get("role"):
        parts.append(f"## Role\n{lead['role']}\n")
    if lead.get("persona"):
        parts.append(_persona_md(lead["persona"]))
    if lead.get("phases"):
        parts.append(f"## Phases\n{_phases_md(lead['phases'])}")
    if lead.get("interaction_style"):
        parts.append(f"## Interaction Style\n{_bullets(lead['interaction_style'])}")
    return "\n".join(parts)


def _specialist_body(sp: dict) -> str:
    parts: list[str] = []
    name_title = sp["name"].replace("-", " ").title()
    parts.append(f"# {name_title} Specialist\n")
    if sp.get("role"):
        parts.append(f"## Role\n{sp['role']}\n")
    if sp.get("persona"):
        parts.append(_persona_md(sp["persona"]))
    if sp.get("sources"):
        paths = [f"`{p}`" for p in sp["sources"]]
        parts.append(f"## Sources\n{_bullets(paths)}")
    if sp.get("exploratory_prompts"):
        parts.append(f"## Exploratory Prompts\n\n{_numbered(sp['exploratory_prompts'])}")
    return "\n".join(parts)


def _specialty_body(st: dict) -> str:
    parts: list[str] = []
    if st.get("worker_focus"):
        parts.append(f"## Worker Focus\n{st['worker_focus']}\n")
    if st.get("verify"):
        parts.append(f"## Verify\n{st['verify']}\n")
    return "\n".join(parts)


def _team_body(doc: dict) -> str:
    name_title = doc["name"].replace("-", " ").title()
    parts = [f"# {name_title}\n"]
    if doc.get("role"):
        parts.append(f"## Role\n{doc['role']}\n")
    return "\n".join(parts)


def write_tree(team_doc: dict, team_root: Path) -> None:
    team_root.mkdir(parents=True, exist_ok=True)
    _write_md(
        team_root / "team.md",
        {"description": team_doc["description"]} if team_doc.get("description") else {},
        _team_body(team_doc),
    )
    for lead in team_doc.get("team_leads", []):
        _write_md(
            team_root / "team-leads" / f"{lead['name']}.md",
            lead.get("frontmatter") or {},
            _team_lead_body(lead),
        )
    for sp in team_doc.get("specialists", []):
        sp_dir = team_root / "specialists" / sp["name"]
        _write_md(
            sp_dir / "specialist.md",
            sp.get("frontmatter") or {},
            _specialist_body(sp),
        )
        for st in sp.get("specialties", []):
            _write_md(
                sp_dir / "specialities" / f"{st['name']}.md",
                st.get("frontmatter") or {},
                _specialty_body(st),
            )


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: agenticteam_to_tree.py <bundle_dir> <team_root>",
            file=sys.stderr,
        )
        return 2
    bundle_dir = Path(sys.argv[1]).resolve()
    team_root = Path(sys.argv[2])
    team_doc = json.loads(
        (bundle_dir / "team.json").read_text(encoding="utf-8")
    )
    write_tree(team_doc, team_root)
    print(f"  wrote tree: {team_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
