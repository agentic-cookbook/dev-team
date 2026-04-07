"""Shared helpers for the storage-provider markdown backend."""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from random import randint

SESSION_BASE = Path(
    os.environ.get(
        "ARBITRATOR_SESSION_BASE",
        os.path.expanduser("~/.agentic-cookbook/dev-team/sessions"),
    )
)

PROJECT_DIR_NAME = ".dev-team-project"


# ---------------------------------------------------------------------------
# Date/time helpers
# ---------------------------------------------------------------------------

def today_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# String helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:40]


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def json_build(**kwargs) -> None:
    """Build a JSON object from kwargs and print it to stdout."""
    print(json.dumps(kwargs, ensure_ascii=False))


def json_output(obj) -> None:
    """Print a JSON object to stdout."""
    print(json.dumps(obj, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Flag parsing
# ---------------------------------------------------------------------------

def parse_flags(argv: list[str]) -> dict[str, str]:
    """Parse --flag value pairs from argv into a dict."""
    flags: dict[str, str] = {}
    flag_map = {
        # arbitrator flags
        "--session": "session",
        "--specialist": "specialist",
        "--state": "state",
        "--changed-by": "changed_by",
        "--content": "content",
        "--category": "category",
        "--detail": "detail",
        "--playbook": "playbook",
        "--team-lead": "team_lead",
        "--user": "user",
        "--machine": "machine",
        "--result": "result",
        "--finding": "finding",
        "--message": "message",
        "--artifact": "artifact",
        "--interpretation": "interpretation",
        "--option-text": "option_text",
        "--is-default": "is_default",
        "--sort-order": "sort_order",
        "--reason": "reason",
        "--team": "team",
        "--iteration": "iteration",
        "--verifier-feedback": "verifier_feedback",
        "--add-consulting-annotation": "add_consulting_annotation",
        # project-storage flags
        "--project": "project",
        "--name": "name",
        "--id": "id",
        "--priority": "priority",
        "--assignee": "assignee",
        "--milestone": "milestone",
        "--blocked-by": "blocked_by",
        "--target-date": "target_date",
        "--dependencies": "dependencies",
        "--source": "source",
        "--related-findings": "related_findings",
        "--raised-by": "raised_by",
        "--related-to": "related_to",
        "--rationale": "rationale",
        "--alternatives": "alternatives",
        "--made-by": "made_by",
        "--date": "date",
        # shared flags (present in both — one canonical entry each)
        "--description": "description",
        "--path": "path",
        "--title": "title",
        "--severity": "severity",
        "--status": "status",
        "--type": "type",
    }
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in flag_map and i + 1 < len(argv):
            flags[flag_map[arg]] = argv[i + 1]
            i += 2
        else:
            i += 1
    return flags


def require_flag(flags: dict[str, str], name: str) -> str:
    """Require a flag is present and non-empty."""
    val = flags.get(name, "")
    if not val:
        print(f"Missing required flag: --{name.replace('_', '-')}", file=sys.stderr)
        sys.exit(1)
    return val


# ---------------------------------------------------------------------------
# Session helpers (arbitrator)
# ---------------------------------------------------------------------------

def new_session_id() -> str:
    """Generate a human-readable, sortable, collision-resistant session ID."""
    now = datetime.now(timezone.utc)
    return f"{now.strftime('%Y%m%d-%H%M%S')}-{randint(0, 65535):04x}"


def session_dir(session_id: str) -> Path:
    return SESSION_BASE / session_id


def require_session(session_id: str) -> Path:
    d = session_dir(session_id)
    if not d.is_dir():
        print(f"Session not found: {session_id}", file=sys.stderr)
        sys.exit(1)
    return d


def next_seq(directory: Path) -> str:
    """Get next zero-padded sequence number for a directory."""
    directory.mkdir(parents=True, exist_ok=True)
    count = sum(
        1
        for f in directory.iterdir()
        if f.suffix in (".json", ".jsonl") and f.is_file()
    )
    return f"{count + 1:04d}"


# ---------------------------------------------------------------------------
# Project helpers (project-storage)
# ---------------------------------------------------------------------------

def project_dir(project_path: str) -> Path:
    return Path(project_path) / PROJECT_DIR_NAME


def require_project(project_path: str) -> Path:
    d = project_dir(project_path)
    if not d.is_dir():
        print(f"No dev-team project at: {project_path}", file=sys.stderr)
        sys.exit(1)
    return d


def next_id(item_type: str, directory: Path) -> str:
    """Return next ID e.g. 'todo-0001'."""
    directory.mkdir(parents=True, exist_ok=True)
    count = sum(1 for f in directory.iterdir() if f.suffix == ".md" and f.is_file())
    return f"{item_type}-{count + 1:04d}"


# ---------------------------------------------------------------------------
# Markdown / frontmatter I/O (project-storage)
# ---------------------------------------------------------------------------

def read_frontmatter(file: Path) -> dict:
    """Parse YAML frontmatter from a markdown file into a dict."""
    text = file.read_text()
    lines = text.splitlines()
    in_frontmatter = False
    yaml_lines = []
    for line in lines:
        if line == "---":
            if in_frontmatter:
                break
            else:
                in_frontmatter = True
                continue
        if in_frontmatter:
            yaml_lines.append(line)

    result = {}
    for line in yaml_lines:
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)", line)
        if not m:
            continue
        key = m.group(1)
        val = m.group(2).rstrip()
        if val == "null" or val == "":
            result[key] = None
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1]
            if inner.strip() == "":
                result[key] = []
            else:
                result[key] = [item.strip() for item in inner.split(",")]
        else:
            result[key] = val
    return result


def read_body(file: Path) -> str:
    """Return everything after the second --- delimiter."""
    text = file.read_text()
    lines = text.splitlines()
    found_first = False
    past_frontmatter = False
    body_lines = []
    for line in lines:
        if line == "---":
            if found_first:
                past_frontmatter = True
                continue
            else:
                found_first = True
                continue
        if past_frontmatter:
            body_lines.append(line)
    return "\n".join(body_lines)


def _format_value(val) -> str:
    """Format a Python value as a YAML scalar."""
    if val is None:
        return "null"
    if isinstance(val, list):
        if not val:
            return "[]"
        return "[" + ", ".join(str(item) for item in val) + "]"
    return str(val)


def write_item(file: Path, body: str, metadata: dict) -> None:
    """Write a markdown file with YAML frontmatter."""
    lines = ["---"]
    for key, val in metadata.items():
        lines.append(f"{key}: {_format_value(val)}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    file.write_text("\n".join(lines) + "\n")


def update_item(file: Path, updates: dict) -> None:
    """Read existing file, merge updates, add modified date, rewrite."""
    current = read_frontmatter(file)
    body = read_body(file)
    current.update(updates)
    current["modified"] = today_iso()
    write_item(file, body, current)
