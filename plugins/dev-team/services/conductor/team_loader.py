"""Load a team definition from `teams/<team-name>/` markdown.

Produces a `TeamManifest`: team name + dict of specialists, each with
a dict of specialties (name, description, worker_prompt, verifier_prompt,
logical_model). A generic realizer (see `generic_realizer.py`) consumes
this manifest so we don't hand-author one per team.

Expected layout:
    teams/<team>/
        team.md                            (optional — team-level prose)
        specialists/
            <specialist>/
                specialist.md              (optional)
                specialities/
                    <specialty>.md         (YAML frontmatter + Worker/Verify sections)

Specialty file format:
    ---
    name: <specialty-name>
    description: <short>
    logical_model: fast-cheap | balanced | high-reasoning  (optional)
    ---

    ## Worker Focus
    <paragraph — becomes worker prompt body>

    ## Verify
    <paragraph — becomes verifier prompt body>
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SpecialtyDef:
    name: str
    description: str
    worker_focus: str
    verify: str
    logical_model: str = "balanced"


@dataclass
class SpecialistDef:
    name: str
    specialties: dict[str, SpecialtyDef] = field(default_factory=dict)


@dataclass
class TeamManifest:
    name: str
    team_root: Path
    specialists: dict[str, SpecialistDef] = field(default_factory=dict)

    def get_specialty(
        self, specialist_name: str, specialty_name: str
    ) -> SpecialtyDef | None:
        spec = self.specialists.get(specialist_name)
        if spec is None:
            return None
        return spec.specialties.get(specialty_name)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Minimal YAML frontmatter parser. Only supports flat key: value
    pairs, no nested structures. Returns (frontmatter_dict, body)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    header = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in header.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip()
    return meta, body


def _extract_section(markdown: str, heading: str) -> str:
    """Return the content under an H2 heading (## Worker Focus) up to the
    next heading of the same or higher level. Trimmed."""
    prefix = f"## {heading}"
    idx = markdown.find(prefix)
    if idx < 0:
        return ""
    start = idx + len(prefix)
    newline_after = markdown.find("\n", start)
    if newline_after < 0:
        return markdown[start:].strip()
    rest = markdown[newline_after + 1 :]
    # stop at next ## heading
    next_heading = rest.find("\n## ")
    section = rest if next_heading < 0 else rest[:next_heading]
    return section.strip()


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_team(team_root: Path) -> TeamManifest:
    """Build a TeamManifest from a team directory.

    Accepts either the markdown-tree shape (teams/<name>/...) or the
    bundle shape (<name>.agenticteam/ with team.json at the root). When
    a team.json is present at the root, `_load_from_agenticteam` is used.

    For markdown trees: directory names are authoritative identifiers
    when frontmatter fields are absent. Specialties without a
    well-formed specialty.md YAML frontmatter are skipped.
    """
    team_root = team_root.resolve()
    if team_root.suffix == ".agenticteam" or (team_root / "team.json").is_file():
        return _load_from_agenticteam(team_root)
    name = team_root.name
    team_md = team_root / "team.md"
    if team_md.is_file():
        meta, _ = _parse_frontmatter(team_md.read_text())
        if meta.get("name"):
            name = meta["name"]

    manifest = TeamManifest(name=name, team_root=team_root)

    specialists_dir = team_root / "specialists"
    if not specialists_dir.is_dir():
        return manifest

    for sp_dir in sorted(specialists_dir.iterdir()):
        if not sp_dir.is_dir():
            continue
        specialist = SpecialistDef(name=sp_dir.name)
        sp_md = sp_dir / "specialist.md"
        if sp_md.is_file():
            meta, _ = _parse_frontmatter(sp_md.read_text())
            if meta.get("name"):
                specialist.name = meta["name"]

        # Specialty files live in specialities/ (project uses British spelling)
        # but we accept specialties/ for future-proofing.
        for candidate in ("specialities", "specialties"):
            spec_dir = sp_dir / candidate
            if spec_dir.is_dir():
                for md in sorted(spec_dir.iterdir()):
                    if md.suffix != ".md" or md.name == "index.md":
                        continue
                    _ingest_specialty(md, specialist)
                break

        if specialist.specialties:
            manifest.specialists[specialist.name] = specialist

    return manifest


def _ingest_specialty(md_path: Path, specialist: SpecialistDef) -> None:
    text = md_path.read_text()
    meta, body = _parse_frontmatter(text)
    name = meta.get("name") or md_path.stem
    description = meta.get("description", "")
    logical_model = meta.get("logical_model", "balanced")
    worker_focus = _extract_section(body, "Worker Focus")
    verify = _extract_section(body, "Verify")
    if not worker_focus:
        # Not machine-readable; skip rather than build a junk manifest.
        return
    specialist.specialties[name] = SpecialtyDef(
        name=name,
        description=description,
        worker_focus=worker_focus,
        verify=verify,
        logical_model=logical_model,
    )


def _load_from_agenticteam(bundle_root: Path) -> TeamManifest:
    """Build a TeamManifest from a <name>.agenticteam/ bundle (team.json)."""
    team_json = bundle_root / "team.json"
    doc = json.loads(team_json.read_text(encoding="utf-8"))
    if doc.get("kind") != "agenticteam":
        raise ValueError(
            f"{team_json}: expected kind=agenticteam, got {doc.get('kind')!r}"
        )
    if doc.get("schema_version") != 2:
        raise ValueError(
            f"{team_json}: expected schema_version=2, got {doc.get('schema_version')!r}"
        )
    manifest = TeamManifest(name=doc["name"], team_root=bundle_root)
    for sp in doc.get("specialists", []):
        sd = SpecialistDef(name=sp["name"])
        for st in sp.get("specialties", []):
            fm = st.get("frontmatter") or {}
            worker_focus = st.get("worker_focus", "")
            if not worker_focus:
                continue
            sd.specialties[st["name"]] = SpecialtyDef(
                name=st["name"],
                description=fm.get("description", ""),
                worker_focus=worker_focus,
                verify=st.get("verify", ""),
                logical_model=fm.get("logical_model", "balanced"),
            )
        if sd.specialties:
            manifest.specialists[sp["name"]] = sd
    return manifest
