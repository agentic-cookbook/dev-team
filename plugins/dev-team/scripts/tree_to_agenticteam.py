"""Convert a teams/<name>/ markdown tree into a <name>.agenticteam/ bundle.

Bundle layout:
    <team>.agenticteam/
        team.json               (schema v2 — structured section fields)
        guidelines/...          (real markdown files at declared paths)
        compliance/...
        principles/...

Run:
    tree_to_agenticteam.py <team_root> <bundle_dir> <ref-root>...
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
SECTION_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SECTION_H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*?)\s*$", re.MULTILINE)
NUMBERED_RE = re.compile(r"^\s*\d+\.\s+(.*?)(?=\n\s*\d+\.|\Z)", re.DOTALL | re.MULTILINE)


def parse_markdown(path: Path) -> tuple[dict, str]:
    if not path.is_file():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text.strip()
    fm_raw, body = m.group(1), m.group(2)
    fm: dict = {}
    for line in fm_raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip()
    return fm, body.strip()


def _split(body: str, heading_re: re.Pattern) -> dict[str, str]:
    out: dict[str, str] = {}
    matches = list(heading_re.finditer(body))
    if not matches:
        return out
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out[m.group(1).strip()] = body[start:end].strip()
    return out


def split_sections(body: str) -> dict[str, str]:
    return _split(body, SECTION_H2_RE)


def split_subsections(text: str) -> dict[str, str]:
    return _split(text, SECTION_H3_RE)


def _extract_bullets(text: str) -> list[str]:
    return [m.group(1).strip() for m in BULLET_RE.finditer(text)]


def _extract_numbered(text: str) -> list[str]:
    return [m.group(1).strip() for m in NUMBERED_RE.finditer(text)]


def _strip_inline_code(s: str) -> str:
    return s.strip().strip("`")


def _persona(text: str) -> dict:
    subs = split_subsections(text)
    if subs:
        out: dict = {}
        for key, label in (("Archetype", "archetype"), ("Voice", "voice"), ("Priorities", "priorities")):
            if key in subs:
                out[label] = subs[key]
        return out
    # Unstructured persona (e.g. "(coming)") — fold into archetype slot.
    return {"archetype": text.strip()} if text.strip() else {}


def _phases(text: str) -> list[dict]:
    out: list[dict] = []
    for bullet in _extract_bullets(text):
        if " — " in bullet:
            name, _, desc = bullet.partition(" — ")
            out.append({"name": name.strip(), "description": desc.strip()})
        elif " - " in bullet:
            name, _, desc = bullet.partition(" - ")
            out.append({"name": name.strip(), "description": desc.strip()})
        else:
            out.append({"name": bullet.strip()})
    return out


def _specialty(path: Path) -> dict:
    fm, body = parse_markdown(path)
    sections = split_sections(body)
    out = {
        "name": path.stem,
        "frontmatter": fm,
        "worker_focus": sections.get("Worker Focus", ""),
        "verify": sections.get("Verify", ""),
    }
    return out


def _specialist_like(sp_dir: Path, intro_filename: str) -> dict:
    fm, body = parse_markdown(sp_dir / intro_filename)
    sections = split_sections(body)
    out: dict = {"name": sp_dir.name, "frontmatter": fm}
    if "Role" in sections:
        out["role"] = sections["Role"]
    if "Persona" in sections:
        persona = _persona(sections["Persona"])
        if persona:
            out["persona"] = persona
    sources_section = sections.get("Cookbook Sources") or sections.get("Sources")
    if sources_section:
        out["sources"] = [_strip_inline_code(b) for b in _extract_bullets(sources_section)]
    if "Exploratory Prompts" in sections:
        prompts = _extract_numbered(sections["Exploratory Prompts"])
        if prompts:
            out["exploratory_prompts"] = prompts
    return out


def _specialist(sp_dir: Path) -> dict:
    out = _specialist_like(sp_dir, "specialist.md")
    specialties: list[dict] = []
    for cand in ("specialities", "specialties"):
        d = sp_dir / cand
        if not d.is_dir():
            continue
        for md in sorted(d.iterdir()):
            if md.suffix != ".md" or md.name == "index.md":
                continue
            specialties.append(_specialty(md))
        break
    out["specialties"] = specialties
    return out


def _team_lead(path: Path) -> dict:
    fm, body = parse_markdown(path)
    sections = split_sections(body)
    out: dict = {"name": path.stem, "frontmatter": fm}
    out["role"] = sections.get("Role", "")
    if "Persona" in sections:
        persona = _persona(sections["Persona"])
        if persona:
            out["persona"] = persona
    if "Phases" in sections:
        phases = _phases(sections["Phases"])
        if phases:
            out["phases"] = phases
    if "Interaction Style" in sections:
        bullets = _extract_bullets(sections["Interaction Style"])
        if bullets:
            out["interaction_style"] = bullets
    return out


def _consulting(node: Path) -> list[dict]:
    """Consulting folder is a parallel specialist tree — reuse _specialist_like
    when the entry is a directory with a specialist.md, otherwise treat it as
    a single consulting unit with just frontmatter + role."""
    out: list[dict] = []
    for entry in sorted(node.iterdir()):
        if entry.is_dir():
            if (entry / "specialist.md").is_file():
                out.append(_specialist(entry))
            else:
                out.append({"name": entry.name, "children": _consulting(entry)})
        elif entry.is_file() and entry.suffix == ".md" and entry.name != "index.md":
            fm, body = parse_markdown(entry)
            sections = split_sections(body)
            out.append({
                "name": entry.stem,
                "frontmatter": fm,
                "role": sections.get("Role", body),
            })
    return out


def convert_team(team_root: Path) -> dict:
    fm, body = parse_markdown(team_root / "team.md")
    sections = split_sections(body)
    leads: list[dict] = []
    lead_dir = team_root / "team-leads"
    if lead_dir.is_dir():
        for md in sorted(lead_dir.iterdir()):
            if md.suffix != ".md" or md.name == "index.md":
                continue
            leads.append(_team_lead(md))
    specialists: list[dict] = []
    sp_root = team_root / "specialists"
    if sp_root.is_dir():
        for sp_dir in sorted(sp_root.iterdir()):
            if not sp_dir.is_dir():
                continue
            specialists.append(_specialist(sp_dir))
    consulting_root = team_root / "consulting"
    consulting = _consulting(consulting_root) if consulting_root.is_dir() else []
    doc: dict = {
        "kind": "agenticteam",
        "schema_version": 2,
        "name": team_root.name,
    }
    if fm.get("description"):
        doc["description"] = fm["description"]
    if "Role" in sections:
        doc["role"] = sections["Role"]
    doc["team_leads"] = leads
    doc["specialists"] = specialists
    if consulting:
        doc["consulting"] = consulting
    return doc


def index_reference_roots(roots: list[Path]) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = defaultdict(list)
    for root in roots:
        if not root.is_dir():
            continue
        for f in root.rglob("*.md"):
            rel = f.relative_to(root.parent)
            parts = rel.parts
            for i in range(len(parts)):
                index["/".join(parts[i:])].append(f)
    return index


def resolve_artifact(path: str, index: dict[str, list[Path]]) -> Path | None:
    if path.endswith("/"):
        return None
    hits = index.get(path)
    if hits:
        return hits[0]
    parts = path.split("/")
    for i in range(1, len(parts)):
        hits = index.get("/".join(parts[i:]))
        if hits:
            return hits[0]
    return None


def seal_bundle(
    team_doc: dict,
    reference_roots: list[Path],
    bundle_dir: Path,
) -> dict[str, int]:
    stats = {k: 0 for k in (
        "specialties_total", "with_artifact", "output_locations",
        "resolved", "unresolved", "files_copied",
    )}
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True)
    index = index_reference_roots(reference_roots)
    copied: set[str] = set()
    for specialist in team_doc.get("specialists", []):
        for specialty in specialist.get("specialties", []):
            stats["specialties_total"] += 1
            artifact = (specialty.get("frontmatter") or {}).get("artifact")
            if not artifact:
                specialty["artifact_kind"] = "inline"
                continue
            stats["with_artifact"] += 1
            if artifact.endswith("/"):
                stats["output_locations"] += 1
                specialty["artifact_kind"] = "inline"
                continue
            resolved = resolve_artifact(artifact, index)
            if resolved is None:
                stats["unresolved"] += 1
                specialty["artifact_kind"] = "reference_unresolved"
                continue
            stats["resolved"] += 1
            specialty["artifact_kind"] = "reference_resolved"
            if artifact in copied:
                continue
            dest = bundle_dir / artifact
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(resolved, dest)
            copied.add(artifact)
            stats["files_copied"] += 1
    (bundle_dir / "team.json").write_text(
        json.dumps(team_doc, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return stats


def main() -> int:
    if len(sys.argv) < 4:
        print(
            "usage: tree_to_agenticteam.py <team_root> <bundle_dir> <ref-root>...",
            file=sys.stderr,
        )
        return 2
    team_root = Path(sys.argv[1]).resolve()
    bundle_dir = Path(sys.argv[2])
    roots = [Path(p).resolve() for p in sys.argv[3:]]
    team_doc = convert_team(team_root)
    stats = seal_bundle(team_doc, roots, bundle_dir)
    print(f"  bundle: {bundle_dir}")
    for k, v in stats.items():
        print(f"    {k:22s} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
