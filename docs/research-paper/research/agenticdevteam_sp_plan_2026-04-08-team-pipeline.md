# Team Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the reusable multi-agent pipeline from dev-team into `plugins/team-pipeline/`, then validate it with a "name-a-puppy" test team.

**Architecture:** Copy proven patterns from dev-team with terminology changes (cookbook → source). Pipeline provides agents, scripts, specs, and premade team-leads. User teams provide specialists, specialty-teams, and workflows.

**Tech Stack:** Python scripts, markdown definitions, pytest

**Deferred:** Dashboard service — currently coupled to dev-team's DB layer (excluded from team-pipeline). Needs a rewrite to read from arbitrator markdown sessions instead of SQLite. Will address after the core pipeline is proven.

---

### Task 1: Plugin scaffold and manifest

**Files:**
- Create: `plugins/team-pipeline/.claude-plugin/plugin.json`

- [ ] **Step 1: Create plugin manifest**

```json
{
  "name": "team-pipeline",
  "version": "0.1.0",
  "description": "Reusable multi-agent team pipeline for specialist-driven workflows",
  "author": {
    "name": "Mike Fullerton"
  },
  "license": "MIT",
  "agents": "./agents/"
}
```

- [ ] **Step 2: Commit**

```bash
git add plugins/team-pipeline/.claude-plugin/plugin.json
git commit -m "feat: scaffold team-pipeline plugin with manifest"
git push
```

---

### Task 2: Storage helpers

The foundation everything else depends on. Adapted from dev-team's `storage_helpers.py` — remove project-storage helpers and dev-team-specific defaults.

**Files:**
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/storage_helpers.py`
- Test: `testing/unit/tests/team-pipeline/storage-provider/conftest.py`
- Test: `testing/unit/tests/team-pipeline/storage-provider/test_storage_helpers.py`

- [ ] **Step 1: Write the test**

```python
# testing/unit/tests/team-pipeline/storage-provider/test_storage_helpers.py
"""Tests for team-pipeline storage helpers."""
import os
import sys
from pathlib import Path

import pytest

# Add the storage-provider markdown directory to sys.path
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
SP_DIR = REPO_ROOT / "plugins" / "team-pipeline" / "scripts" / "storage-provider" / "markdown"
sys.path.insert(0, str(SP_DIR))

from storage_helpers import (
    today_iso,
    now_iso,
    slugify,
    json_build,
    json_output,
    parse_flags,
    require_flag,
    new_session_id,
    session_dir,
    next_seq,
    SESSION_BASE,
)


def test_session_base_uses_env(tmp_path, monkeypatch):
    monkeypatch.setenv("TEAM_PIPELINE_SESSION_BASE", str(tmp_path / "custom"))
    # Reimport to pick up env change
    import importlib
    import storage_helpers
    importlib.reload(storage_helpers)
    assert storage_helpers.SESSION_BASE == tmp_path / "custom"


def test_slugify_basic():
    assert slugify("Hello World!") == "hello-world"


def test_slugify_strips_leading_trailing_hyphens():
    assert slugify("--test--") == "test"


def test_slugify_truncates_at_40():
    assert len(slugify("a" * 100)) <= 40


def test_today_iso_format():
    result = today_iso()
    assert len(result) == 10  # YYYY-MM-DD
    assert result[4] == "-" and result[7] == "-"


def test_now_iso_format():
    result = now_iso()
    assert "T" in result and result.endswith("Z")


def test_parse_flags_extracts_pairs():
    flags = parse_flags(["--session", "abc", "--specialist", "security"])
    assert flags["session"] == "abc"
    assert flags["specialist"] == "security"


def test_parse_flags_skips_unknown():
    flags = parse_flags(["--unknown", "val", "--session", "abc"])
    assert "unknown" not in flags
    assert flags["session"] == "abc"


def test_require_flag_returns_value():
    assert require_flag({"session": "abc"}, "session") == "abc"


def test_require_flag_exits_on_missing():
    with pytest.raises(SystemExit):
        require_flag({}, "session")


def test_new_session_id_format():
    sid = new_session_id()
    parts = sid.split("-")
    assert len(parts) == 3  # YYYYMMDD-HHMMSS-XXXX
    assert len(parts[0]) == 8
    assert len(parts[1]) == 6
    assert len(parts[2]) == 4


def test_session_dir_uses_base(tmp_path, monkeypatch):
    monkeypatch.setenv("TEAM_PIPELINE_SESSION_BASE", str(tmp_path))
    import importlib
    import storage_helpers
    importlib.reload(storage_helpers)
    d = storage_helpers.session_dir("test-123")
    assert d == tmp_path / "test-123"


def test_next_seq_starts_at_0001(tmp_path):
    seq = next_seq(tmp_path / "subdir")
    assert seq == "0001"


def test_next_seq_increments(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    (d / "0001.json").write_text("{}")
    seq = next_seq(d)
    assert seq == "0002"
```

- [ ] **Step 2: Write conftest**

```python
# testing/unit/tests/team-pipeline/storage-provider/conftest.py
import os
import sys
from pathlib import Path

import pytest

@pytest.fixture(autouse=True)
def isolated_session_dir(tmp_path):
    """Each test gets its own session directory."""
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    os.environ["TEAM_PIPELINE_SESSION_BASE"] = str(session_dir)
    yield session_dir
    os.environ.pop("TEAM_PIPELINE_SESSION_BASE", None)
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/storage-provider/test_storage_helpers.py -v`
Expected: FAIL — module not found

- [ ] **Step 4: Write storage_helpers.py**

Copy from `plugins/dev-team/scripts/storage-provider/markdown/storage_helpers.py` with these changes:

1. Change `ARBITRATOR_SESSION_BASE` env var to `TEAM_PIPELINE_SESSION_BASE`
2. Change default path from `~/.agentic-cookbook/dev-team/sessions` to `~/.team-pipeline/sessions`
3. Change `PROJECT_DIR_NAME` from `.dev-team-project` to `.team-pipeline-project`
4. Remove project-storage-specific helpers: `project_dir`, `require_project`, `next_id`, `read_frontmatter`, `read_body`, `_format_value`, `write_item`, `update_item`
5. Keep everything else: date helpers, string helpers, JSON helpers, flag parsing, session helpers

```python
#!/usr/bin/env python3
"""Shared helpers for the team-pipeline storage-provider markdown backend."""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from random import randint

SESSION_BASE = Path(
    os.environ.get(
        "TEAM_PIPELINE_SESSION_BASE",
        os.path.expanduser("~/.team-pipeline/sessions"),
    )
)


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
        "--description": "description",
        "--path": "path",
        "--title": "title",
        "--severity": "severity",
        "--status": "status",
        "--type": "type",
        "--name": "name",
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
# Session helpers
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
```

- [ ] **Step 5: Run tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/storage-provider/test_storage_helpers.py -v`
Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add plugins/team-pipeline/scripts/storage-provider/markdown/storage_helpers.py testing/unit/tests/team-pipeline/
git commit -m "feat: add team-pipeline storage helpers with tests"
git push
```

---

### Task 3: Storage-provider dispatcher and session resource

**Files:**
- Create: `plugins/team-pipeline/scripts/storage_provider.py`
- Create: `plugins/team-pipeline/scripts/arbitrator.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/session.py`
- Test: `testing/unit/tests/team-pipeline/storage-provider/test_session.py`
- Test: `testing/unit/tests/team-pipeline/storage-provider/tp_helpers.py`

- [ ] **Step 1: Write test helpers**

```python
# testing/unit/tests/team-pipeline/storage-provider/tp_helpers.py
"""Helper functions for team-pipeline storage-provider tests."""
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
ARBITRATOR = str(REPO_ROOT / "plugins" / "team-pipeline" / "scripts" / "arbitrator.py")


def run_arbitrator(*args):
    """Call arbitrator.py and return the CompletedProcess."""
    result = subprocess.run(
        ["python3", ARBITRATOR] + list(args),
        capture_output=True, text=True
    )
    return result


def run_ok(*args):
    """Call arbitrator.py, assert success, return stdout."""
    result = run_arbitrator(*args)
    assert result.returncode == 0, f"arbitrator failed: {result.stderr}"
    return result.stdout.strip()


def run_json(*args):
    """Call arbitrator.py, assert success, return parsed JSON."""
    stdout = run_ok(*args)
    return json.loads(stdout)


def make_session(**kwargs):
    """Create a test session and return its ID."""
    data = run_json(
        "session", "create",
        "--playbook", kwargs.get("playbook", "test"),
        "--team-lead", kwargs.get("team_lead", "test"),
        "--user", kwargs.get("user", "testuser"),
        "--machine", kwargs.get("machine", "testhost"),
    )
    return data["session_id"]
```

- [ ] **Step 2: Write session tests**

```python
# testing/unit/tests/team-pipeline/storage-provider/test_session.py
"""Contract tests for team-pipeline session resource."""
import pytest
from tp_helpers import run_arbitrator, run_ok, run_json, make_session


def test_session_create_returns_session_id():
    data = run_json(
        "session", "create",
        "--playbook", "interview",
        "--team-lead", "interview",
        "--user", "testuser",
        "--machine", "testhost",
    )
    assert data["session_id"]


def test_session_get_returns_all_fields():
    data = run_json(
        "session", "create",
        "--playbook", "test-workflow",
        "--team-lead", "analysis",
        "--user", "alice",
        "--machine", "devbox",
    )
    session_id = data["session_id"]

    result = run_json("session", "get", "--session", session_id)
    assert result["playbook"] == "test-workflow"
    assert result["team_lead"] == "analysis"
    assert result["user"] == "alice"
    assert result["machine"] == "devbox"
    assert result["creation_date"]


def test_session_list_filters_by_playbook():
    run_ok("session", "create", "--playbook", "lint", "--team-lead", "audit", "--user", "bob", "--machine", "ci")
    run_ok("session", "create", "--playbook", "lint", "--team-lead", "audit", "--user", "bob", "--machine", "ci")
    run_ok("session", "create", "--playbook", "interview", "--team-lead", "interview", "--user", "bob", "--machine", "ci")

    result = run_json("session", "list", "--playbook", "lint")
    assert len(result) >= 2


def test_session_list_returns_empty_for_no_matches():
    result = run_json("session", "list", "--playbook", "nonexistent")
    assert len(result) == 0


def test_session_add_path_stores_path():
    session_id = make_session()

    result = run_json(
        "session", "add-path",
        "--session", session_id,
        "--path", "/tmp/test-repo",
        "--type", "repo",
    )
    assert result["type"] == "repo"
    assert result["path"] == "/tmp/test-repo"


def test_session_create_missing_flags_fails():
    result = run_arbitrator("session", "create", "--playbook", "test")
    assert result.returncode == 1


def test_session_get_nonexistent_fails():
    result = run_arbitrator("session", "get", "--session", "nonexistent-id")
    assert result.returncode == 1
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/storage-provider/test_session.py -v`
Expected: FAIL — arbitrator.py not found

- [ ] **Step 4: Write storage_provider.py**

Copy from dev-team, remove project-storage env var fallback:

```python
#!/usr/bin/env python3
"""Unified storage-provider for the team-pipeline.

Single entry point for all data persistence. Backend-swappable via
STORAGE_PROVIDER_BACKEND env var (default: markdown).

Usage: storage_provider.py <resource> <action> [--flags]
"""
import importlib
import importlib.util
import os
import sys
from pathlib import Path


def dispatch(resource, action, flags, backend=None):
    """Dispatch a resource action to the configured backend."""
    if backend is None:
        backend = os.environ.get("STORAGE_PROVIDER_BACKEND", "markdown")

    module_name = resource.replace("-", "_")
    script_dir = Path(__file__).parent / "storage-provider" / backend
    module_path = script_dir / f"{module_name}.py"

    if not module_path.exists():
        print(f"Unknown resource: {resource}", file=sys.stderr)
        sys.exit(1)

    sys.path.insert(0, str(script_dir))
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Resource modules read from sys.argv directly
    sys.argv = [str(module_path), action] + flags
    mod.main()


def main():
    if len(sys.argv) < 3:
        print("Usage: storage_provider.py <resource> <action> [flags]", file=sys.stderr)
        sys.exit(1)

    resource = sys.argv[1]
    action = sys.argv[2]
    flags = sys.argv[3:]

    dispatch(resource, action, flags)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write arbitrator.py**

```python
#!/usr/bin/env python3
"""Arbitrator — communication conduit between pipeline participants.

Delegates all persistence to the storage-provider. Adds communication
semantics (session lifecycle, state transitions, message routing) on top.

Usage: arbitrator.py <resource> <action> [--flags]
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from storage_provider import dispatch


def main():
    if len(sys.argv) < 3:
        print("Usage: arbitrator.py <resource> <action> [flags]", file=sys.stderr)
        sys.exit(1)

    resource = sys.argv[1]
    action = sys.argv[2]
    flags = sys.argv[3:]

    backend = os.environ.get("STORAGE_PROVIDER_BACKEND", "markdown")
    dispatch(resource, action, flags, backend=backend)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Write session.py**

Copy from dev-team's `storage-provider/markdown/session.py` — identical logic, uses the team-pipeline storage_helpers:

```python
#!/usr/bin/env python3
"""Session resource for markdown storage-provider."""
import json
import sys
from pathlib import Path
from storage_helpers import (
    parse_flags, require_flag, require_session,
    new_session_id, session_dir, now_iso, json_output, SESSION_BASE,
)


def create(flags):
    playbook = require_flag(flags, "playbook")
    team_lead = require_flag(flags, "team_lead")
    user = require_flag(flags, "user")
    machine = require_flag(flags, "machine")

    session_id = new_session_id()
    d = session_dir(session_id)
    d.mkdir(parents=True, exist_ok=True)

    data = {
        "session_id": session_id,
        "playbook": playbook,
        "team_lead": team_lead,
        "user": user,
        "machine": machine,
        "creation_date": now_iso(),
    }
    (d / "session.json").write_text(json.dumps(data, ensure_ascii=False))

    json_output({"session_id": session_id})


def get(flags):
    session_id = require_flag(flags, "session")
    d = require_session(session_id)
    print((d / "session.json").read_text())


def list_all(flags):
    if not SESSION_BASE.is_dir():
        print("[]")
        return

    results = []
    for session_file in sorted(SESSION_BASE.glob("*/session.json")):
        if not session_file.is_file():
            continue
        data = json.loads(session_file.read_text())
        match = True

        playbook_filter = flags.get("playbook", "")
        if playbook_filter and data.get("playbook") != playbook_filter:
            match = False

        status_filter = flags.get("status", "")
        if status_filter and match:
            sid = data.get("session_id", "")
            state_dir = session_dir(sid) / "state"
            if state_dir.is_dir():
                state_files = sorted(state_dir.glob("*.json"))
                if state_files:
                    latest = json.loads(state_files[-1].read_text())
                    if latest.get("state") != status_filter:
                        match = False
                else:
                    match = False
            else:
                match = False

        if match:
            results.append(data)

    json_output(results)


def add_path(flags):
    session_id = require_flag(flags, "session")
    path = require_flag(flags, "path")
    type_ = require_flag(flags, "type")

    d = require_session(session_id)
    paths_file = d / "paths.jsonl"

    entry = {
        "session_id": session_id,
        "path": path,
        "type": type_,
        "creation_date": now_iso(),
    }
    with paths_file.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    json_output({"session_id": session_id, "path": path, "type": type_})


def main():
    if len(sys.argv) < 2:
        print("Usage: session.py <create|get|list|add-path> [flags]", file=sys.stderr)
        sys.exit(1)
    action = sys.argv[1]
    flags = parse_flags(sys.argv[2:])

    actions = {
        "create": create,
        "get": get,
        "list": list_all,
        "add-path": add_path,
    }
    if action not in actions:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)
    actions[action](flags)


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Run tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/storage-provider/test_session.py -v`
Expected: all PASS

- [ ] **Step 8: Commit**

```bash
git add plugins/team-pipeline/scripts/ testing/unit/tests/team-pipeline/
git commit -m "feat: add team-pipeline arbitrator, storage-provider, and session resource with tests"
git push
```

---

### Task 4: Remaining storage-provider resources

Copy the remaining 11 pipeline resources from dev-team. These are mechanical copies — same logic, same tests patterns, using team-pipeline's storage_helpers.

**Files:**
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/state.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/message.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/gate_option.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/result.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/finding.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/interpretation.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/artifact.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/reference.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/retry.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/team_result.py`
- Create: `plugins/team-pipeline/scripts/storage-provider/markdown/report.py`

Do NOT copy the project-storage resources (project, milestone, todo, issue, concern, dependency, decision) — those stay in dev-team.

Each resource file: copy from `plugins/dev-team/scripts/storage-provider/markdown/<name>.py`, change only the import path to use team-pipeline's storage_helpers. No logic changes.

- [ ] **Step 1: Copy all 11 resource files**

For each file, copy from dev-team's version. The only change is that they import from the local `storage_helpers` (which is already the team-pipeline version since they're in the team-pipeline directory).

- [ ] **Step 2: Write contract tests**

Create `testing/unit/tests/team-pipeline/storage-provider/test_state.py` through `test_report.py`, mirroring the dev-team arbitrator tests. Use `tp_helpers.py` for the helper functions.

Mirror the test files from `testing/unit/tests/arbitrator/` — the tests are identical except they use `tp_helpers` instead of `arbitrator_helpers`.

- [ ] **Step 3: Run all tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/storage-provider/ -v`
Expected: all PASS

- [ ] **Step 4: Commit**

```bash
git add plugins/team-pipeline/scripts/storage-provider/ testing/unit/tests/team-pipeline/storage-provider/
git commit -m "feat: add remaining storage-provider resources with contract tests"
git push
```

---

### Task 5: Manifest parser (run_specialty_teams.py)

**Files:**
- Create: `plugins/team-pipeline/scripts/run_specialty_teams.py`
- Test: `testing/unit/tests/team-pipeline/test_run_specialty_teams.py`

- [ ] **Step 1: Write tests**

```python
# testing/unit/tests/team-pipeline/test_run_specialty_teams.py
"""Tests for team-pipeline manifest parser."""
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
PARSER = str(REPO_ROOT / "plugins" / "team-pipeline" / "scripts" / "run_specialty_teams.py")


def write_specialist(tmp_path, manifest_entries, consulting_entries=None):
    """Write a minimal specialist file and return its path."""
    spec_file = tmp_path / "specialists" / "test-spec.md"
    spec_file.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Test Specialist",
        "",
        "## Role",
        "Test role.",
        "",
        "## Persona",
        "(coming)",
        "",
        "## Sources",
        "- `guidelines/test/`",
        "",
        "## Manifest",
    ]
    for entry in manifest_entries:
        lines.append(f"- {entry}")

    if consulting_entries:
        lines.append("")
        lines.append("## Consulting Teams")
        for entry in consulting_entries:
            lines.append(f"- {entry}")

    spec_file.write_text("\n".join(lines) + "\n")
    return spec_file


def write_team_file(tmp_path, rel_path, name, source, focus, verify):
    """Write a specialty-team file at the given relative path."""
    team_file = tmp_path / rel_path
    team_file.parent.mkdir(parents=True, exist_ok=True)
    content = f"""---
name: {name}
description: Test team
artifact: {source}
version: 1.0.0
---

## Worker Focus
{focus}

## Verify
{verify}
"""
    team_file.write_text(content)
    return team_file


def write_consulting_file(tmp_path, rel_path, name, source_list, focus, verify):
    """Write a consulting-team file at the given relative path."""
    team_file = tmp_path / rel_path
    team_file.parent.mkdir(parents=True, exist_ok=True)
    source_yaml = "\n".join(f"  - {s}" for s in source_list)
    content = f"""---
name: {name}
description: Test consultant
type: consulting
source:
{source_yaml}
version: 1.0.0
---

## Consulting Focus
{focus}

## Verify
{verify}
"""
    team_file.write_text(content)
    return team_file


def test_parses_specialty_teams(tmp_path):
    write_team_file(
        tmp_path,
        "specialty-teams/test/energy.md",
        "energy", "sources/test/energy.md",
        "Evaluate energy levels", "Energy levels assessed",
    )
    spec = write_specialist(tmp_path, ["specialty-teams/test/energy.md"])

    result = subprocess.run(
        ["python3", PARSER, str(spec)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert len(data["specialty_teams"]) == 1
    assert data["specialty_teams"][0]["name"] == "energy"
    assert data["specialty_teams"][0]["worker_focus"] == "Evaluate energy levels"
    assert data["specialty_teams"][0]["verify"] == "Energy levels assessed"


def test_parses_consulting_teams(tmp_path):
    write_team_file(
        tmp_path,
        "specialty-teams/test/energy.md",
        "energy", "sources/test/energy.md",
        "Evaluate energy", "Energy assessed",
    )
    write_consulting_file(
        tmp_path,
        "consulting-teams/test/safety.md",
        "safety", ["docs/safety.md"],
        "Check safety concerns", "Safety verified",
    )
    spec = write_specialist(
        tmp_path,
        ["specialty-teams/test/energy.md"],
        consulting_entries=["consulting-teams/test/safety.md"],
    )

    result = subprocess.run(
        ["python3", PARSER, str(spec)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert len(data["consulting_teams"]) == 1
    assert data["consulting_teams"][0]["name"] == "safety"


def test_missing_specialist_file_fails():
    result = subprocess.run(
        ["python3", PARSER, "/nonexistent/file.md"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1


def test_empty_manifest_fails(tmp_path):
    spec_file = tmp_path / "specialists" / "empty.md"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text("# Empty\n\n## Role\nTest\n\n## Manifest\n")

    result = subprocess.run(
        ["python3", PARSER, str(spec_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_run_specialty_teams.py -v`
Expected: FAIL

- [ ] **Step 3: Write run_specialty_teams.py**

Copy from `plugins/dev-team/scripts/run_specialty_teams.py` — identical logic. The parser reads `## Manifest` and `## Consulting Teams` sections. No terminology changes needed in the parser itself since it reads whatever frontmatter field names the files use.

```python
#!/usr/bin/env python3
# run_specialty_teams.py — Read specialty-team and consulting-team definitions for a specialist
#
# Reads the specialist's ## Manifest and ## Consulting Teams sections,
# resolves each path, parses frontmatter and body sections, and outputs JSON.
#
# Usage:
#   run_specialty_teams.py <specialist-file>
#
# Output: JSON object with specialty_teams and consulting_teams arrays.
# If no ## Consulting Teams section exists, consulting_teams is empty.

import sys
import json
from pathlib import Path


def parse_section_paths(specialist_file, section_heading):
    """Extract paths from a named ## section of a specialist file."""
    paths = []
    in_section = False

    with open(specialist_file) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(f"## {section_heading}"):
                in_section = True
                continue
            if in_section and line.startswith("## "):
                break
            if in_section and line.startswith("- "):
                paths.append(line[2:])

    return paths


def parse_frontmatter(lines):
    """Parse YAML frontmatter from lines, return (fields_dict, body_start_index)."""
    fields = {}
    in_frontmatter = False
    front_count = 0
    body_start = 0
    current_list_key = ""

    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if stripped == "---":
            front_count += 1
            if front_count == 1:
                in_frontmatter = True
                continue
            elif front_count == 2:
                in_frontmatter = False
                body_start = i + 1
                break
        if in_frontmatter:
            if stripped.startswith("  - ") and current_list_key:
                fields[current_list_key].append(stripped.strip().lstrip("- ").strip())
                continue
            current_list_key = ""
            if stripped.startswith("name:"):
                fields["name"] = stripped[len("name:"):].strip()
            elif stripped.startswith("artifact:"):
                fields["artifact"] = stripped[len("artifact:"):].strip()
            elif stripped.startswith("type:"):
                fields["type"] = stripped[len("type:"):].strip()
            elif stripped.startswith("source:"):
                value = stripped[len("source:"):].strip()
                if value:
                    fields["source"] = [value]
                else:
                    fields["source"] = []
                    current_list_key = "source"

    return fields, body_start


def parse_team_file(team_file):
    """Parse a specialty-team file and return its fields."""
    with open(team_file) as f:
        lines = f.readlines()

    fields, body_start = parse_frontmatter(lines)
    body_lines = [l.rstrip("\n") for l in lines[body_start:]]

    worker_focus = ""
    verify = ""
    current_section = ""

    for line in body_lines:
        if line == "## Worker Focus":
            current_section = "focus"
            continue
        if line == "## Verify":
            current_section = "verify"
            continue
        if line.startswith("## "):
            current_section = ""
            continue
        if not line.strip():
            continue
        if current_section == "focus" and not worker_focus:
            worker_focus = line.strip()
        elif current_section == "verify" and not verify:
            verify = line.strip()

    return {
        "name": fields.get("name", ""),
        "artifact": fields.get("artifact", ""),
        "worker_focus": worker_focus,
        "verify": verify,
    }


def parse_consulting_team_file(team_file):
    """Parse a consulting-team file and return its fields."""
    with open(team_file) as f:
        lines = f.readlines()

    fields, body_start = parse_frontmatter(lines)
    body_lines = [l.rstrip("\n") for l in lines[body_start:]]

    consulting_focus = ""
    verify = ""
    current_section = ""

    for line in body_lines:
        if line == "## Consulting Focus":
            current_section = "focus"
            continue
        if line == "## Verify":
            current_section = "verify"
            continue
        if line.startswith("## "):
            current_section = ""
            continue
        if not line.strip():
            continue
        if current_section == "focus" and not consulting_focus:
            consulting_focus = line.strip()
        elif current_section == "verify" and not verify:
            verify = line.strip()

    return {
        "name": fields.get("name", ""),
        "type": fields.get("type", ""),
        "source": fields.get("source", []),
        "consulting_focus": consulting_focus,
        "verify": verify,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: run_specialty_teams.py <specialist-file>", file=sys.stderr)
        sys.exit(1)

    specialist_file = sys.argv[1]

    if not Path(specialist_file).is_file():
        print(f"ERROR: Specialist file not found: {specialist_file}", file=sys.stderr)
        sys.exit(1)

    # Resolve repo root from specialist file location
    repo_root = Path(specialist_file).resolve().parent.parent

    # Parse specialty teams
    manifest_paths = parse_section_paths(specialist_file, "Manifest")
    if not manifest_paths:
        print(f"ERROR: No manifest entries found in {specialist_file}", file=sys.stderr)
        sys.exit(1)

    specialty_teams = []
    for team_path in manifest_paths:
        team_file = repo_root / team_path
        if not team_file.is_file():
            print(f"ERROR: Specialty-team file not found: {team_file}", file=sys.stderr)
            sys.exit(1)
        specialty_teams.append(parse_team_file(team_file))

    # Parse consulting teams (optional section)
    consulting_paths = parse_section_paths(specialist_file, "Consulting Teams")
    consulting_teams = []
    for team_path in consulting_paths:
        team_file = repo_root / team_path
        if not team_file.is_file():
            print(f"ERROR: Consulting-team file not found: {team_file}", file=sys.stderr)
            sys.exit(1)
        consulting_teams.append(parse_consulting_team_file(team_file))

    output = {
        "specialty_teams": specialty_teams,
        "consulting_teams": consulting_teams,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_run_specialty_teams.py -v`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/team-pipeline/scripts/run_specialty_teams.py testing/unit/tests/team-pipeline/test_run_specialty_teams.py
git commit -m "feat: add team-pipeline manifest parser with tests"
git push
```

---

### Task 6: Config loader

**Files:**
- Create: `plugins/team-pipeline/scripts/load_config.py`
- Test: `testing/unit/tests/team-pipeline/test_load_config.py`

- [ ] **Step 1: Write tests**

```python
# testing/unit/tests/team-pipeline/test_load_config.py
"""Tests for team-pipeline config loader."""
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
LOADER = str(REPO_ROOT / "plugins" / "team-pipeline" / "scripts" / "load_config.py")


def write_config(tmp_path, data):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(data))
    return config_file


def test_loads_valid_config(tmp_path):
    cfg = write_config(tmp_path, {
        "team_name": "test-team",
        "user_name": "alice",
        "data_dir": "/tmp/data",
    })
    result = subprocess.run(
        ["python3", LOADER, "--config", str(cfg)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["team_name"] == "test-team"
    assert data["user_name"] == "alice"
    assert data["data_dir"] == "/tmp/data"


def test_passes_through_extra_fields(tmp_path):
    cfg = write_config(tmp_path, {
        "team_name": "test-team",
        "user_name": "bob",
        "data_dir": "/tmp/data",
        "custom_field": "custom_value",
        "sources": ["/path/to/docs"],
    })
    result = subprocess.run(
        ["python3", LOADER, "--config", str(cfg)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["custom_field"] == "custom_value"
    assert data["sources"] == ["/path/to/docs"]


def test_missing_required_field_fails(tmp_path):
    cfg = write_config(tmp_path, {
        "team_name": "test-team",
        # missing user_name and data_dir
    })
    result = subprocess.run(
        ["python3", LOADER, "--config", str(cfg)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1


def test_nonexistent_config_fails():
    result = subprocess.run(
        ["python3", LOADER, "--config", "/nonexistent/config.json"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_load_config.py -v`
Expected: FAIL

- [ ] **Step 3: Write load_config.py**

```python
#!/usr/bin/env python3
# load_config.py — Load team-pipeline configuration
# Usage: load_config.py --config <path>
# Outputs: JSON config to stdout, errors to stderr
# Exit codes: 0 = success, 1 = config not found or invalid

import sys
import json
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", required=True)
    args, _ = parser.parse_known_args()

    config_path = Path(args.config)

    if not config_path.exists():
        print(f"Config not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    # Validate only team-pipeline required fields
    required = ["team_name", "user_name", "data_dir"]
    missing = [k for k in required if not config.get(k)]
    if missing:
        print(f"Config missing required fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_load_config.py -v`
Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/team-pipeline/scripts/load_config.py testing/unit/tests/team-pipeline/test_load_config.py
git commit -m "feat: add team-pipeline config loader with tests"
git push
```

---

### Task 7: Observer system

**Files:**
- Create: `plugins/team-pipeline/scripts/observers/dispatch.py`
- Create: `plugins/team-pipeline/scripts/observers/session_paths.py`
- Create: `plugins/team-pipeline/scripts/observers/stenographer.py`
- Create: `plugins/team-pipeline/scripts/observers/oslog.py`
- Test: `testing/unit/tests/team-pipeline/test_observers.py`

- [ ] **Step 1: Write tests**

```python
# testing/unit/tests/team-pipeline/test_observers.py
"""Tests for team-pipeline observer system."""
import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
OBSERVERS_DIR = REPO_ROOT / "plugins" / "team-pipeline" / "scripts" / "observers"
sys.path.insert(0, str(OBSERVERS_DIR))


@pytest.fixture(autouse=True)
def isolated_sessions(tmp_path, monkeypatch):
    monkeypatch.setenv("TEAM_PIPELINE_SESSION_BASE", str(tmp_path / "sessions"))
    # Force reimport to pick up env change
    for mod_name in list(sys.modules):
        if "session_paths" in mod_name:
            del sys.modules[mod_name]
    yield tmp_path / "sessions"


def make_event(session_id="test-session", **overrides):
    event = {
        "timestamp": "2026-04-08T12:00:00.000Z",
        "session_id": session_id,
        "agent_id": "agent-1",
        "agent_type": "specialty-team-worker",
        "agent_description": "test worker",
        "status": "completed",
        "duration_ms": 1000,
        "tools_used": ["Read", "Grep"],
        "tool_call_count": 5,
        "summary": "Did some work",
        "transcript_path": "",
    }
    event.update(overrides)
    return event


def test_dispatch_extract_event():
    from dispatch import extract_event
    hook_input = {
        "session_id": "test-123",
        "agent_id": "a1",
        "agent_type": "worker",
        "agent_description": "test",
        "last_assistant_message": "done",
        "agent_transcript_path": "",
    }
    event = extract_event(hook_input)
    assert event["session_id"] == "test-123"
    assert event["status"] == "completed"


def test_dispatch_discover_observers():
    from dispatch import discover_observers
    observers = discover_observers(OBSERVERS_DIR)
    names = [m.__name__ for m in observers]
    assert "stenographer" in names
    assert "oslog" in names
    assert "dispatch" not in names


def test_stenographer_writes_log(isolated_sessions):
    session_dir = isolated_sessions / "test-session"
    session_dir.mkdir(parents=True)

    import importlib
    import session_paths
    importlib.reload(session_paths)
    import stenographer
    importlib.reload(stenographer)

    event = make_event()
    stenographer.observe(event)

    log_file = session_dir / "session.log"
    assert log_file.exists()
    entry = json.loads(log_file.read_text().strip())
    assert entry["sid"] == "test-session"
    assert entry["agent"] == "specialty-team-worker"


def test_oslog_format_message():
    from oslog import format_message
    event = make_event()
    msg = format_message(event)
    assert "team-pipeline" in msg
    assert "specialty-team-worker" in msg
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_observers.py -v`
Expected: FAIL

- [ ] **Step 3: Write session_paths.py**

```python
"""Shared utilities for observer modules."""

import os
from pathlib import Path


SESSION_BASE = Path(
    os.environ.get(
        "TEAM_PIPELINE_SESSION_BASE",
        os.path.expanduser("~/.team-pipeline/sessions"),
    )
)


def get_session_log_path(session_id: str) -> Path:
    """Resolve the session.log path for a given session ID."""
    session_dir = SESSION_BASE / session_id
    if session_dir.is_dir():
        log_path = session_dir / "session.log"
    else:
        log_dir = SESSION_BASE / "_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "observer.log"
    return log_path
```

- [ ] **Step 4: Write dispatch.py**

Copy from dev-team — identical logic:

```python
#!/usr/bin/env python3
"""Observer dispatch — hook entry point.

Called by the SubagentStop hook. Reads hook input from stdin,
extracts a normalized event from the subagent transcript,
and dispatches to all auto-discovered observer modules.
"""

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def extract_event(hook_input: dict) -> dict:
    """Extract a normalized event from SubagentStop hook input."""
    transcript_path = hook_input.get("agent_transcript_path", "")
    tools_used = set()
    tool_call_count = 0

    if transcript_path and Path(transcript_path).is_file():
        try:
            with open(transcript_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if entry.get("type") == "tool_use":
                        tool_call_count += 1
                        name = entry.get("name", "")
                        if name:
                            tools_used.add(name)
        except (OSError, PermissionError):
            pass

    summary = hook_input.get("last_assistant_message", "")
    if len(summary) > 200:
        summary = summary[:197] + "..."

    return {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "session_id": hook_input.get("session_id", ""),
        "agent_id": hook_input.get("agent_id", ""),
        "agent_type": hook_input.get("agent_type", ""),
        "agent_description": hook_input.get("agent_description", ""),
        "status": "completed",
        "duration_ms": 0,
        "tools_used": sorted(tools_used),
        "tool_call_count": tool_call_count,
        "summary": summary,
        "transcript_path": transcript_path,
    }


def discover_observers(observers_dir: Path) -> list:
    """Auto-discover observer modules in the given directory."""
    skip = {"dispatch.py"}
    observers = []

    for py_file in sorted(observers_dir.glob("*.py")):
        if py_file.name in skip or py_file.name.startswith("_"):
            continue

        spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Observer {py_file.name} failed to load: {e}", file=sys.stderr)
            continue

        if hasattr(module, "observe"):
            observers.append(module)

    return observers


def run_observers(observers: list, event: dict) -> None:
    """Call observe(event) on each observer. Isolate failures."""
    for module in observers:
        try:
            module.observe(event)
        except Exception as e:
            print(f"Observer {module.__name__} failed: {e}", file=sys.stderr)


def main():
    """Entry point for SubagentStop hook."""
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        print("Failed to read hook input from stdin", file=sys.stderr)
        sys.exit(1)

    event = extract_event(hook_input)
    observers_dir = Path(__file__).parent
    observers = discover_observers(observers_dir)
    run_observers(observers, event)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Write stenographer.py**

```python
"""Stenographer observer — writes structured JSONL to session.log."""

import json
from session_paths import get_session_log_path


def observe(event: dict) -> None:
    """Append a log entry to the session log."""
    summary = event.get("summary", "")
    if len(summary) > 200:
        summary = summary[:197] + "..."

    log_entry = {
        "ts": event["timestamp"],
        "sid": event["session_id"],
        "agent": event["agent_type"],
        "desc": event.get("agent_description", ""),
        "status": event["status"],
        "duration_ms": event.get("duration_ms", 0),
        "tools": sorted(event.get("tools_used", [])),
        "calls": event.get("tool_call_count", 0),
        "summary": summary,
    }

    log_path = get_session_log_path(event["session_id"])
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
```

- [ ] **Step 6: Write oslog.py**

```python
"""System log observer — writes one-liners via POSIX logger CLI."""

import subprocess


def format_message(event: dict) -> str:
    """Format a human-readable one-liner for the system log."""
    desc = event.get("agent_description", "") or event["agent_type"]
    status = event["status"]
    duration = event.get("duration_ms", 0) // 1000
    calls = event.get("tool_call_count", 0)
    return f'[team-pipeline] {event["agent_type"]} "{desc}" {status} ({duration}s, {calls} calls)'


def observe(event: dict) -> None:
    """Write event to system log via logger CLI."""
    msg = format_message(event)
    try:
        subprocess.run(
            ["logger", "-t", "team-pipeline", "-p", "user.info", msg],
            timeout=5,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
```

- [ ] **Step 7: Run tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_observers.py -v`
Expected: all PASS

- [ ] **Step 8: Commit**

```bash
git add plugins/team-pipeline/scripts/observers/ testing/unit/tests/team-pipeline/test_observers.py
git commit -m "feat: add team-pipeline observer system with tests"
git push
```

---

### Task 8: Generic agents

The four core agents that power worker/verifier loops. Adapted from dev-team — terminology changes only ("cookbook artifact" → "source").

**Files:**
- Create: `plugins/team-pipeline/agents/specialty-team-worker.md`
- Create: `plugins/team-pipeline/agents/specialty-team-verifier.md`
- Create: `plugins/team-pipeline/agents/consulting-team-worker.md`
- Create: `plugins/team-pipeline/agents/consulting-team-verifier.md`
- Test: `testing/unit/tests/team-pipeline/test_agents.py`

- [ ] **Step 1: Write tests**

```python
# testing/unit/tests/team-pipeline/test_agents.py
"""Tests for team-pipeline agent definitions."""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
AGENTS_DIR = REPO_ROOT / "plugins" / "team-pipeline" / "agents"

EXPECTED_AGENTS = [
    "specialty-team-worker.md",
    "specialty-team-verifier.md",
    "consulting-team-worker.md",
    "consulting-team-verifier.md",
]


@pytest.mark.parametrize("agent_file", EXPECTED_AGENTS)
def test_agent_file_exists(agent_file):
    assert (AGENTS_DIR / agent_file).is_file()


@pytest.mark.parametrize("agent_file", EXPECTED_AGENTS)
def test_agent_has_frontmatter(agent_file):
    content = (AGENTS_DIR / agent_file).read_text()
    assert content.startswith("---")
    # Must have closing frontmatter
    assert content.count("---") >= 2


@pytest.mark.parametrize("agent_file", EXPECTED_AGENTS)
def test_agent_has_name_field(agent_file):
    content = (AGENTS_DIR / agent_file).read_text()
    assert "name:" in content


@pytest.mark.parametrize("agent_file", EXPECTED_AGENTS)
def test_agent_no_cookbook_references(agent_file):
    content = (AGENTS_DIR / agent_file).read_text().lower()
    assert "cookbook" not in content, f"{agent_file} still references 'cookbook'"


def test_worker_has_four_modes():
    content = (AGENTS_DIR / "specialty-team-worker.md").read_text()
    assert "### Mode: interview" in content
    assert "### Mode: analysis" in content
    assert "### Mode: generation" in content
    assert "### Mode: review" in content


def test_no_extra_agents():
    agent_files = sorted(f.name for f in AGENTS_DIR.glob("*.md"))
    assert agent_files == sorted(EXPECTED_AGENTS)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_agents.py -v`
Expected: FAIL

- [ ] **Step 3: Write specialty-team-worker.md**

Copy from dev-team's version. Replace all instances of:
- "cookbook artifact" → "source document"
- "Artifact path" → "Source path"
- "Cookbook repo path" → "Sources base path"
- "artifact's requirements" → "source's requirements"
- "Artifact Requirements Addressed" → "Source Requirements Addressed"
- "Read your cookbook artifact" → "Read your source document"
- Remove the parenthetical examples that reference cookbook paths like `(e.g., guidelines/security/authentication.md)`

Keep all four modes, all output formats, all guidelines. The structure is generic.

- [ ] **Step 4: Write specialty-team-verifier.md**

Copy from dev-team's version. Same terminology changes:
- "cookbook artifact" → "source document"
- "Artifact path" → "Source path"
- "Cookbook repo path" → "Sources base path"
- Remove cookbook-specific examples

- [ ] **Step 5: Write consulting-team-worker.md**

Copy from dev-team's version. Change:
- "cookbook artifact" → "source document" (one reference in the input section)
- Keep everything else — consulting agents are already fairly generic

- [ ] **Step 6: Write consulting-team-verifier.md**

Copy from dev-team. Already generic — no cookbook references to change.

- [ ] **Step 7: Run tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_agents.py -v`
Expected: all PASS

- [ ] **Step 8: Commit**

```bash
git add plugins/team-pipeline/agents/ testing/unit/tests/team-pipeline/test_agents.py
git commit -m "feat: add team-pipeline generic agents with tests"
git push
```

---

### Task 9: Team-lead definitions

New concept — premade team-lead definitions extracted from dev-team workflow patterns.

**Files:**
- Create: `plugins/team-pipeline/team-leads/interview.md`
- Create: `plugins/team-pipeline/team-leads/analysis.md`
- Test: `testing/unit/tests/team-pipeline/test_team_leads.py`

- [ ] **Step 1: Write tests**

```python
# testing/unit/tests/team-pipeline/test_team_leads.py
"""Tests for team-pipeline team-lead definitions."""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
TEAM_LEADS_DIR = REPO_ROOT / "plugins" / "team-pipeline" / "team-leads"

EXPECTED_LEADS = ["interview.md", "analysis.md"]

REQUIRED_SECTIONS = ["# ", "## Role", "## Persona", "## Phases", "## Interaction Style"]
REQUIRED_PERSONA_SUBS = ["### Archetype", "### Voice", "### Priorities"]


@pytest.mark.parametrize("lead_file", EXPECTED_LEADS)
def test_lead_file_exists(lead_file):
    assert (TEAM_LEADS_DIR / lead_file).is_file()


@pytest.mark.parametrize("lead_file", EXPECTED_LEADS)
def test_lead_has_required_sections(lead_file):
    content = (TEAM_LEADS_DIR / lead_file).read_text()
    for section in REQUIRED_SECTIONS:
        assert section in content, f"{lead_file} missing section: {section}"


@pytest.mark.parametrize("lead_file", EXPECTED_LEADS)
def test_lead_has_persona_subsections(lead_file):
    content = (TEAM_LEADS_DIR / lead_file).read_text()
    for sub in REQUIRED_PERSONA_SUBS:
        assert sub in content, f"{lead_file} missing persona sub-section: {sub}"


@pytest.mark.parametrize("lead_file", EXPECTED_LEADS)
def test_lead_title_ends_with_team_lead(lead_file):
    content = (TEAM_LEADS_DIR / lead_file).read_text()
    first_line = content.strip().split("\n")[0]
    assert first_line.startswith("# ")
    assert "Team-Lead" in first_line


@pytest.mark.parametrize("lead_file", EXPECTED_LEADS)
def test_lead_no_cookbook_references(lead_file):
    content = (TEAM_LEADS_DIR / lead_file).read_text().lower()
    assert "cookbook" not in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_team_leads.py -v`
Expected: FAIL

- [ ] **Step 3: Write interview.md**

```markdown
# Interview Team-Lead

## Role
Gather requirements and domain knowledge from the user through structured and exploratory questioning, backed by specialist expertise. The only team member who talks to the user.

## Persona

### Archetype
Seasoned project lead who has run many discovery sessions. Genuinely curious — asks "why" and "what if" — and knows that the story behind a project matters as much as the specification.

### Voice
Warm but focused. Starts wide (vision, goals, who is this person) and narrows methodically. Asks one question at a time. Attributes specialist questions clearly. Never overwhelms with jargon.

### Priorities
Completeness over speed. Would rather ask one more question than ship a gap. Catches contradictions early. Makes the user feel heard, not interrogated.

## Phases
- intro — establish context, understand the user's background and goals
- structured — systematic questioning driven by specialist manifests
- exploratory — follow threads, ask specialist-generated deep-dive questions
- synthesis — summarize findings, identify gaps, produce deliverables

## Interaction Style
- Only team member who talks to the user
- Passes specialist questions through verbatim with attribution ("Our security specialist wants to know...")
- Uses gates for decision points where work pauses until the user chooses
- Uses notifications for progress updates
- Asks one question at a time — never batches questions
```

- [ ] **Step 4: Write analysis.md**

```markdown
# Analysis Team-Lead

## Role
Dispatch specialists against a target (codebase, document, artifact), aggregate findings into a structured report. Presents findings to the user organized by specialist and severity.

## Persona

### Archetype
Technical program manager who has coordinated many cross-functional reviews. Organized, methodical, focused on surfacing what matters.

### Voice
Direct and structured. Leads with findings, not process. Uses severity to prioritize what the user sees first. Concise summaries, detailed drill-downs available on request.

### Priorities
Signal over noise. Would rather surface 5 critical findings clearly than 50 findings in a wall of text. Organizes by impact, not by specialist order. Flags contradictions between specialists.

## Phases
- scan — understand the target, determine which specialists are relevant
- dispatch — run specialists in parallel against the target
- aggregate — collect results, resolve contradictions, rank by severity
- report — present findings to the user with progressive disclosure

## Interaction Style
- Only team member who talks to the user
- Presents a summary first, then offers drill-down by specialist or severity
- Uses gates when specialist findings conflict and require user judgment
- Uses notifications for progress as specialists complete
```

- [ ] **Step 5: Run tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_team_leads.py -v`
Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add plugins/team-pipeline/team-leads/ testing/unit/tests/team-pipeline/test_team_leads.py
git commit -m "feat: add premade interview and analysis team-lead definitions with tests"
git push
```

---

### Task 10: Spec documents

File format specifications for user-provided content.

**Files:**
- Create: `plugins/team-pipeline/docs/specialist-spec.md`
- Create: `plugins/team-pipeline/docs/specialty-team-spec.md`
- Create: `plugins/team-pipeline/docs/consulting-team-spec.md`
- Create: `plugins/team-pipeline/docs/team-lead-spec.md`

- [ ] **Step 1: Write specialist-spec.md**

Adapt from dev-team's `specialist-spec.md`. Changes:
- "Cookbook Sources" → "Sources" throughout
- "cookbook repo" → "sources base path" or "knowledge base"
- Remove cookbook-specific validation rules (C03: artifact paths resolve in cookbook repo)
- Specialty-team frontmatter: `artifact:` field stays (it's the path to the source document the team works from — generic concept)
- Extract specialty-team and consulting-team specs into their own files (cross-reference only)
- Update parser contract to reference `plugins/team-pipeline/scripts/run_specialty_teams.py`

- [ ] **Step 2: Write specialty-team-spec.md**

Extract from dev-team's specialist-spec. Same format:
- Frontmatter: name, description, artifact (source document path), version
- Body: Worker Focus, Verify
- Validation rules for structure and content

- [ ] **Step 3: Write consulting-team-spec.md**

Extract from dev-team's specialist-spec. Same format:
- Frontmatter: name, description, type (consulting), source (list), version
- Body: Consulting Focus, Verify
- Verdict types: VERIFIED, NOT-APPLICABLE

- [ ] **Step 4: Write team-lead-spec.md**

New spec:
- Title: `# <Name> Team-Lead`
- Required sections in order: Role, Persona (with Archetype, Voice, Priorities sub-sections), Phases, Interaction Style
- Validation rules mirroring the specialist spec pattern

- [ ] **Step 5: Commit**

```bash
git add plugins/team-pipeline/docs/
git commit -m "feat: add team-pipeline file format specs"
git push
```

---

### Task 11: Name-a-Puppy test team — specialists and specialty-teams

**Files:**
- Create: `plugins/name-a-puppy/specialists/temperament.md`
- Create: `plugins/name-a-puppy/specialists/breed.md`
- Create: `plugins/name-a-puppy/specialists/lifestyle.md`
- Create: `plugins/name-a-puppy/specialty-teams/temperament/energy-level.md`
- Create: `plugins/name-a-puppy/specialty-teams/temperament/sociability.md`
- Create: `plugins/name-a-puppy/specialty-teams/breed/size-traits.md`
- Create: `plugins/name-a-puppy/specialty-teams/breed/name-traditions.md`
- Create: `plugins/name-a-puppy/specialty-teams/lifestyle/living-space.md`
- Create: `plugins/name-a-puppy/specialty-teams/lifestyle/activity-level.md`
- Test: `testing/unit/tests/team-pipeline/test_puppy_team.py`

- [ ] **Step 1: Write validation tests**

```python
# testing/unit/tests/team-pipeline/test_puppy_team.py
"""Tests for name-a-puppy test team — validates against team-pipeline specs."""
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
PUPPY_DIR = REPO_ROOT / "plugins" / "name-a-puppy"
PARSER = str(REPO_ROOT / "plugins" / "team-pipeline" / "scripts" / "run_specialty_teams.py")

SPECIALISTS = ["temperament.md", "breed.md", "lifestyle.md"]

EXPECTED_TEAMS = {
    "temperament": ["energy-level.md", "sociability.md"],
    "breed": ["size-traits.md", "name-traditions.md"],
    "lifestyle": ["living-space.md", "activity-level.md"],
}


@pytest.mark.parametrize("spec_file", SPECIALISTS)
def test_specialist_exists(spec_file):
    assert (PUPPY_DIR / "specialists" / spec_file).is_file()


@pytest.mark.parametrize("spec_file", SPECIALISTS)
def test_specialist_has_required_sections(spec_file):
    content = (PUPPY_DIR / "specialists" / spec_file).read_text()
    assert "# " in content
    assert "## Role" in content
    assert "## Sources" in content
    assert "## Manifest" in content


@pytest.mark.parametrize("category,teams", list(EXPECTED_TEAMS.items()))
def test_specialty_team_files_exist(category, teams):
    for team in teams:
        path = PUPPY_DIR / "specialty-teams" / category / team
        assert path.is_file(), f"Missing: {path}"


@pytest.mark.parametrize("category,teams", list(EXPECTED_TEAMS.items()))
def test_specialty_teams_have_frontmatter(category, teams):
    for team in teams:
        content = (PUPPY_DIR / "specialty-teams" / category / team).read_text()
        assert content.startswith("---")
        assert "name:" in content
        assert "version:" in content


@pytest.mark.parametrize("category,teams", list(EXPECTED_TEAMS.items()))
def test_specialty_teams_have_body_sections(category, teams):
    for team in teams:
        content = (PUPPY_DIR / "specialty-teams" / category / team).read_text()
        assert "## Worker Focus" in content
        assert "## Verify" in content


@pytest.mark.parametrize("spec_file", SPECIALISTS)
def test_manifest_parses_successfully(spec_file):
    spec_path = str(PUPPY_DIR / "specialists" / spec_file)
    result = subprocess.run(
        ["python3", PARSER, spec_path],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"Parser failed for {spec_file}: {result.stderr}"
    data = json.loads(result.stdout)
    assert len(data["specialty_teams"]) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_puppy_team.py -v`
Expected: FAIL

- [ ] **Step 3: Write temperament specialist**

```markdown
# Temperament Specialist

## Role
Dog temperament and personality — energy levels, sociability, trainability, anxiety tendencies, play style.

## Persona

### Archetype
Dog behaviorist who has evaluated thousands of dogs across breeds and backgrounds.

### Voice
Warm and knowledgeable. Uses specific behavioral terms but explains them in plain language. Asks questions that reveal what the owner actually experiences, not what they think they should say.

### Priorities
Honest match over wishful thinking. Would rather steer someone toward a calm breed than let them name an energetic dog "Zen." A name should fit who the dog actually is.

## Sources
- Reference materials on dog temperament and behavior

## Manifest
- specialty-teams/temperament/energy-level.md
- specialty-teams/temperament/sociability.md
```

- [ ] **Step 4: Write breed specialist**

```markdown
# Breed Specialist

## Role
Breed characteristics, lineage, physical traits, breed-specific naming traditions, and cultural associations.

## Persona

### Archetype
Experienced breeder and dog show judge who knows every breed's history and character.

### Voice
Enthusiastic and encyclopedic. Loves sharing breed history and trivia. Connects physical traits to personality. Always has a story about a dog they knew.

### Priorities
Breed authenticity matters — a Shiba Inu named "Bubba" misses an opportunity. Cultural respect in naming. Size and appearance should inform the name.

## Sources
- Reference materials on dog breeds and naming traditions

## Manifest
- specialty-teams/breed/size-traits.md
- specialty-teams/breed/name-traditions.md
```

- [ ] **Step 5: Write lifestyle specialist**

```markdown
# Lifestyle Specialist

## Role
Owner lifestyle compatibility — living space, activity level, family composition, work schedule, outdoor access.

## Persona

### Archetype
Experienced adoption counselor who has matched hundreds of dogs with families and knows what makes placements stick.

### Voice
Practical and empathetic. Asks about real daily routines, not ideal ones. Gently redirects when someone's lifestyle doesn't match their dream breed.

### Priorities
The dog's quality of life comes first. A name that reflects the dog's actual daily life (apartment vs. farm, solo vs. pack) helps set expectations.

## Sources
- Reference materials on dog-owner lifestyle matching

## Manifest
- specialty-teams/lifestyle/living-space.md
- specialty-teams/lifestyle/activity-level.md
```

- [ ] **Step 6: Write specialty-team files**

Create all 6 specialty-team files:

`specialty-teams/temperament/energy-level.md`:
```markdown
---
name: energy-level
description: Assess the dog's energy level and how it should influence naming
artifact: sources/temperament/energy-level.md
version: 1.0.0
---

## Worker Focus
Determine the dog's energy level — low, moderate, high, or extreme. Consider breed defaults, age, and owner observations. Explore how energy level should influence name choice (e.g., high-energy dogs suit dynamic names, calm dogs suit dignified names).

## Verify
Energy level clearly categorized with evidence. Connection between energy level and name style explicitly stated. Not a generic "consider energy level" — specific recommendations.
```

`specialty-teams/temperament/sociability.md`:
```markdown
---
name: sociability
description: Assess the dog's social behavior and how it should influence naming
artifact: sources/temperament/sociability.md
version: 1.0.0
---

## Worker Focus
Determine the dog's sociability — with people, other dogs, and strangers. Consider whether the dog is outgoing, reserved, protective, or anxious. Explore how social personality should influence name choice (e.g., a goofy social dog vs. a dignified independent dog).

## Verify
Social behavior clearly characterized. Connection to naming style explicit. Not generic advice — specific to this dog's observed or expected behavior.
```

`specialty-teams/breed/size-traits.md`:
```markdown
---
name: size-traits
description: Assess breed size and physical traits relevant to naming
artifact: sources/breed/size-traits.md
version: 1.0.0
---

## Worker Focus
Determine the dog's expected size (toy, small, medium, large, giant) and distinctive physical traits (coat color, ear shape, markings). Explore how physical characteristics traditionally influence naming — ironic names (tiny dog named "Tank"), descriptive names ("Shadow" for a black dog), or size-appropriate names.

## Verify
Size category and key physical traits identified. Naming implications of physical traits explicitly connected. Not just "consider size" — specific name-style recommendations tied to this dog's appearance.
```

`specialty-teams/breed/name-traditions.md`:
```markdown
---
name: name-traditions
description: Explore breed-specific and cultural naming traditions
artifact: sources/breed/name-traditions.md
version: 1.0.0
---

## Worker Focus
Research naming traditions for this breed's country/culture of origin. Consider: traditional names in the breed's language, famous dogs of this breed, kennel name conventions, cultural naming patterns. Explore whether the owner values heritage naming or prefers modern/creative names.

## Verify
Breed origin identified. At least 3 culturally appropriate name suggestions with explanation. Owner preference for traditional vs. modern naming explored. Not generic dog names — breed-specific traditions.
```

`specialty-teams/lifestyle/living-space.md`:
```markdown
---
name: living-space
description: Assess living environment and its influence on naming
artifact: sources/lifestyle/living-space.md
version: 1.0.0
---

## Worker Focus
Determine the dog's living environment — apartment, house with yard, rural property, etc. Consider how the environment shapes the dog's daily life and personality expression. Explore naming implications: an apartment dog that goes to dog parks vs. a farm dog that roams freely lead very different lives that could inspire different names.

## Verify
Living environment clearly described. Connection between environment and the dog's lifestyle established. Naming implications specific to this environment, not generic advice.
```

`specialty-teams/lifestyle/activity-level.md`:
```markdown
---
name: activity-level
description: Assess owner activity level and its compatibility with the dog
artifact: sources/lifestyle/activity-level.md
version: 1.0.0
---

## Worker Focus
Determine the owner's activity level and how the dog fits into it — runner who wants a trail companion, homebody who wants a lap dog, family with kids who need a patient playmate. Explore how the owner-dog activity dynamic should influence naming (e.g., a hiking companion might suit an adventurous name, a therapy dog might suit a calming name).

## Verify
Owner activity level characterized. Dog-owner activity compatibility assessed. Naming recommendations tied to specific activity patterns, not generic suggestions.
```

- [ ] **Step 7: Run tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/test_puppy_team.py -v`
Expected: all PASS

- [ ] **Step 8: Commit**

```bash
git add plugins/name-a-puppy/specialists/ plugins/name-a-puppy/specialty-teams/ testing/unit/tests/team-pipeline/test_puppy_team.py
git commit -m "feat: add name-a-puppy test team specialists and specialty-teams"
git push
```

---

### Task 12: Name-a-Puppy workflow and skill

**Files:**
- Create: `plugins/name-a-puppy/skills/name-a-puppy/SKILL.md`
- Create: `plugins/name-a-puppy/skills/name-a-puppy/workflows/interview.md`
- Create: `plugins/name-a-puppy/.claude-plugin/plugin.json`

- [ ] **Step 1: Write plugin manifest**

```json
{
  "name": "name-a-puppy",
  "version": "0.1.0",
  "description": "Name your puppy with help from a team of dog experts",
  "author": {
    "name": "Mike Fullerton"
  },
  "license": "MIT",
  "skills": "./skills/"
}
```

- [ ] **Step 2: Write SKILL.md**

```markdown
---
name: name-a-puppy
version: 0.1.0
description: Interview-driven puppy naming with specialist expertise. A test team for the team-pipeline.
allowed-tools: Read, Glob, Grep, Agent, Write, Edit, AskUserQuestion, Bash(python3 *)
argument-hint: [interview]
---

# Name a Puppy v0.1.0

## Startup

**First action**: Print `name-a-puppy v0.1.0` as the first line of output.

Set `TEAM_PIPELINE_ROOT` to the team-pipeline plugin directory (sibling of this plugin under `plugins/`).

## Routing

Parse the first positional argument from `$ARGUMENTS` as the subcommand.

| Subcommand | Workflow File |
|------------|--------------|
| `interview` | `${CLAUDE_SKILL_DIR}/workflows/interview.md` |

Read the workflow file and follow its instructions.

If no subcommand is provided, default to `interview`.
```

- [ ] **Step 3: Write interview workflow**

```markdown
<!-- Workflow: interview — loaded by /name-a-puppy router -->

# Puppy Naming Interview

## Overview

You are the **interview team-lead** for the name-a-puppy team. Your job is to help users find the perfect name for their puppy through structured questioning backed by specialist expertise.

Read your team-lead definition: `${TEAM_PIPELINE_ROOT}/team-leads/interview.md`. Adopt its persona and interaction style.

You are the only team member who talks to the user. You orchestrate a team of specialists behind the scenes.

## Session Start

Greet the user warmly:

"Hi! I'm here to help you find the perfect name for your puppy. I've got a team of dog experts behind me — a temperament specialist, a breed specialist, and a lifestyle specialist. Together, we'll find a name that really fits your dog. Let's start — tell me about your puppy!"

## The Interview Loop

### Phase 1: Intro
Get the basics:
- What kind of dog? (breed or mix)
- How old?
- Male or female?
- Any names you're already considering?

### Phase 2: Structured Questioning
For each specialist in `${CLAUDE_PLUGIN_ROOT}/specialists/`:

1. Read the specialist file
2. Parse its manifest using: `python3 ${TEAM_PIPELINE_ROOT}/scripts/run_specialty_teams.py <specialist-file>`
3. For each specialty-team, dispatch a worker subagent:
   - Agent definition: `${TEAM_PIPELINE_ROOT}/agents/specialty-team-worker.md`
   - Mode: `interview`
   - Pass the specialty-team's worker_focus
   - The worker produces one question
4. Present the question to the user with specialist attribution
5. Record the answer

### Phase 3: Exploratory
Based on what you've learned, ask follow-up questions. Use the specialists' exploratory prompts if available. Follow interesting threads — a story about how they got the dog, a cultural connection, a personality quirk.

### Phase 4: Synthesis
Synthesize everything into 3-5 name recommendations:
- Each name with a 2-3 sentence explanation of why it fits
- Consider temperament, breed heritage, lifestyle, physical traits
- Mix of traditional and creative options
- Present to the user and discuss

## Guidelines
- One question at a time
- Attribute specialist questions: "Our breed specialist wants to know..."
- Keep it fun — this is about naming a puppy, not filing a report
- If the user already has a name they love, validate it against the specialist input rather than pushing alternatives
```

- [ ] **Step 4: Commit**

```bash
git add plugins/name-a-puppy/
git commit -m "feat: add name-a-puppy skill, workflow, and plugin manifest"
git push
```

---

### Task 13: Full integration test

Run the complete test suite to validate everything works together.

- [ ] **Step 1: Run all team-pipeline tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/tests/team-pipeline/ -v`
Expected: all PASS

- [ ] **Step 2: Run manifest parser against all puppy specialists**

```bash
cd /Users/mfullerton/projects/active/dev-team
for spec in plugins/name-a-puppy/specialists/*.md; do
    echo "=== $spec ==="
    python3 plugins/team-pipeline/scripts/run_specialty_teams.py "$spec"
done
```
Expected: valid JSON output for each specialist

- [ ] **Step 3: Verify no dev-team tests broke**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest testing/unit/ -v`
Expected: all existing tests still PASS — dev-team is untouched

- [ ] **Step 4: Commit any fixes, final push**

If any tests needed fixing, commit and push the fixes.
