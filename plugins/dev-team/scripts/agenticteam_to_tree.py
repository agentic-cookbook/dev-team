"""Inverse of tree_to_agenticteam: write a .agenticteam bundle back as a
teams/<name>/ markdown tree. Used by round-trip tests; not part of the
loader path.

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


def write_tree(team_doc: dict, team_root: Path) -> None:
    team_root.mkdir(parents=True, exist_ok=True)
    if team_doc.get("identity"):
        _write_md(team_root / "team.md", {}, team_doc["identity"])
    if team_doc.get("index"):
        _write_md(team_root / "index.md", {}, team_doc["index"])
    for lead in team_doc.get("team_leads", []):
        _write_md(
            team_root / "team-leads" / f"{lead['name']}.md",
            lead.get("frontmatter") or {},
            lead.get("body") or "",
        )
    for sp in team_doc.get("specialists", []):
        sp_dir = team_root / "specialists" / sp["name"]
        if sp.get("description"):
            _write_md(
                sp_dir / "specialist.md",
                sp.get("frontmatter") or {},
                sp["description"],
            )
        if sp.get("index"):
            _write_md(sp_dir / "index.md", {}, sp["index"])
        for st in sp.get("specialties", []):
            _write_md(
                sp_dir / "specialities" / f"{st['name']}.md",
                st.get("frontmatter") or {},
                st.get("body") or "",
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
