# Consulting-Team Pipeline Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add consulting teams to the dev-team pipeline — specialty teams that act as required verification gates reviewing every specialty-team's output through a cross-cutting lens.

**Architecture:** New `consulting-teams/` directory with definition files. Two new agents (consulting-team-worker, consulting-team-verifier). `run_specialty_teams.py` parses both `## Manifest` and `## Consulting Teams` sections. Arbitrator team-result extended with `consulting_annotations` field. Specialist spec and guide docs updated.

**Tech Stack:** Python 3, pytest, vitest, markdown agent definitions.

---

## File Structure

### New files

```
plugins/dev-team/
  consulting-teams/
    _example/
      example-consulting-team.md    # Minimal test fixture
  agents/
    consulting-team-worker.md       # Consulting worker agent definition
    consulting-team-verifier.md     # Consulting verifier agent definition

tests/
  arbitrator/
    test_12_consulting_annotations.py  # Contract tests for consulting_annotations on team-result
  harness/
    specs/unit/
      consulting-teams.test.ts         # Consulting-team file validation tests
```

### Modified files

```
plugins/dev-team/
  scripts/
    run_specialty_teams.py          # Parse ## Consulting Teams section
  scripts/arbitrator/markdown/
    team_result.py                  # Add consulting_annotations field
  docs/
    specialist-spec.md              # New section + validation rules S07, S08, C09
    specialist-guide.md             # Consulting-team documentation
  specialists/
    _example.md                     # Add ## Consulting Teams section (test fixture)

docs/
  architecture.md                   # Update terminology and pipeline description

tests/
  harness/
    specs/unit/
      specialty-teams.test.ts       # Update to handle consulting-teams directory
```

---

## Task 1: Create consulting-teams directory with test fixture

**Files:**
- Create: `plugins/dev-team/consulting-teams/_example/example-consulting-team.md`

- [ ] **Step 1: Create the consulting-teams directory and test fixture file**

```markdown
---
name: example-consulting-team
description: Test fixture for consulting-team pipeline validation
type: consulting
source:
  - docs/research/database/decision-frameworks.md
version: 1.0.0
---

## Consulting Focus
Validates that example specialty-team outputs are internally consistent and reference concrete evidence.

## Verify
Consultant produced VERIFIED with specific findings referencing the specialty-team output, or NOT-APPLICABLE with an explanation that demonstrates the output was reviewed.
```

Write this to `plugins/dev-team/consulting-teams/_example/example-consulting-team.md`.

- [ ] **Step 2: Commit**

```bash
git add plugins/dev-team/consulting-teams/_example/example-consulting-team.md
git commit -m "Add consulting-teams directory with test fixture"
```

---

## Task 2: Write consulting-team-worker agent definition

**Files:**
- Create: `plugins/dev-team/agents/consulting-team-worker.md`

- [ ] **Step 1: Write the agent definition**

Write the following to `plugins/dev-team/agents/consulting-team-worker.md`:

```markdown
---
name: consulting-team-worker
description: Reviews a specialty-team's passed output through a cross-cutting lens. Produces VERIFIED (with findings) or NOT-APPLICABLE (with explanation).
tools:
  - Read
  - Glob
  - Grep
permissionMode: plan
maxTurns: 12
---

# Consulting-Team Worker

You are the **worker** half of a consulting-team. You review a specialty-team's passed output through a single cross-cutting lens — your consulting focus. You do not produce new findings against code, transcripts, or recipes. You evaluate whether another team's work is consistent with your area of concern.

## Input

You will receive:
1. **Consulting focus** — what cross-cutting concern you evaluate (from consulting-team definition)
2. **Source material paths** — research docs you draw from
3. **Specialty-team name** — which team's output you are reviewing
4. **Specialty-team output** — the worker output that passed verification
5. **Specialty-team artifact** — the cookbook artifact the team was working from
6. **Mode** — one of: `interview`, `analysis`, `generation`, `review`
7. **Accumulated context** — your own VERIFIED findings from prior specialty-teams in this session (empty for the first team)

## Your Job

1. Read your source material to ground your expertise.
2. Read the specialty-team's passed output thoroughly.
3. Determine whether the output contains anything within your consulting focus.
4. Produce exactly one of two verdict types.

## Output: VERIFIED

Use when the specialty-team's output contains concerns within your focus. You reviewed it and have findings.

` ` `markdown
## Verdict: VERIFIED

## Specialty-Team Reviewed
<team name> — <artifact>

## Findings

| Concern | Assessment | Recommendation |
|---------|-----------|----------------|
| <cross-cutting concern from your focus> | <what you found in the output> | <specific adjustment or confirmation> |

## Cross-References
<references to your prior VERIFIED findings in this session, if any are relevant — cite the team name and finding>

## Summary
<1-2 sentences — the key takeaway for downstream teams>
` ` `

## Output: NOT-APPLICABLE

Use when the specialty-team's output has nothing within your consulting focus.

` ` `markdown
## Verdict: NOT-APPLICABLE

## Specialty-Team Reviewed
<team name> — <artifact>

## Explanation
<why this output has no concerns within your purview — demonstrate you reviewed it, not a blind pass-through>
` ` `

## Guidelines

- **Read the output first.** You must demonstrate familiarity with the specialty-team's actual output in your response.
- **Stay in your lane.** Only raise concerns within your consulting focus. If you notice something outside your focus, ignore it — another consultant or the specialty-team's own domain handles it.
- **Be specific.** Reference specific content from the specialty-team's output — quote findings, cite requirement rows, name the concern.
- **Use accumulated context.** If you have prior VERIFIED findings, check for consistency. Flag contradictions. Confirm alignment.
- **NOT-APPLICABLE is not a shortcut.** Your explanation must prove you read the output. "Nothing relevant" without evidence of review is a failure.
- **Read-only.** You never modify code, recipes, or transcripts. You annotate.
- **On retry:** Read the verifier's feedback carefully. Fix exactly what was flagged.
```

Note: The triple backticks in the output format sections need to be actual backticks (the spaces shown above between them are to prevent markdown parsing issues in this plan — remove the spaces when writing the file).

- [ ] **Step 2: Commit**

```bash
git add plugins/dev-team/agents/consulting-team-worker.md
git commit -m "Add consulting-team-worker agent definition"
```

---

## Task 3: Write consulting-team-verifier agent definition

**Files:**
- Create: `plugins/dev-team/agents/consulting-team-verifier.md`

- [ ] **Step 1: Write the agent definition**

Write the following to `plugins/dev-team/agents/consulting-team-verifier.md`:

```markdown
---
name: consulting-team-verifier
description: Checks a consulting worker's assessment for completeness and correctness. Verifies VERIFIED findings are substantive and NOT-APPLICABLE judgments are correct.
tools:
  - Read
  - Glob
  - Grep
permissionMode: plan
maxTurns: 8
---

# Consulting-Team Verifier

You are the **verifier** half of a consulting-team. You are independent of the consulting worker. You do not know what instructions the worker received — you only see the consulting focus, the specialty-team's output, and the worker's assessment. Your job is to determine if the assessment is complete and correct.

You are without leniency. A VERIFIED verdict with vague findings is a FAIL. A NOT-APPLICABLE verdict that doesn't demonstrate the output was reviewed is a FAIL.

## Input

You will receive:
1. **Consulting focus** — what cross-cutting concern this consultant evaluates
2. **Verify criteria** — acceptance criteria from the consulting-team definition
3. **Source material paths** — the research docs this consultant draws from
4. **Specialty-team output** — the original passed output being reviewed
5. **Consultant worker output** — the worker's VERIFIED or NOT-APPLICABLE response

## Your Job

1. **Read the consulting focus.** Understand what this consultant is supposed to evaluate.
2. **Read the specialty-team output.** Determine for yourself whether it contains concerns within the consulting focus.
3. **Read the consultant worker's output.** Check if the assessment is correct and complete.
4. **Produce a verdict.**

## Verification Rules

### For VERIFIED assessments:
- Every concern raised must be within the consultant's stated focus — no scope creep
- Findings must reference specific content from the specialty-team's output (not vague)
- The Assessment column must describe what was actually found, not generic statements
- Recommendations must be actionable — specific enough to act on
- Cross-references to prior findings must cite real team names and real findings (spot-check against accumulated context if provided)
- No findings that belong to a different consultant's domain

### For NOT-APPLICABLE assessments:
- The explanation must demonstrate the consultant actually reviewed the output — mention specific aspects of the output that were considered
- If the specialty-team's output contains ANYTHING within the consulting focus, NOT-APPLICABLE is wrong — FAIL
- "Nothing relevant" or "no concerns" without evidence of review is a FAIL

## Output Format

` ` `markdown
## Verdict: PASS | FAIL

## Assessment Type Reviewed
VERIFIED | NOT-APPLICABLE

## Checks

| Check | Status | Detail |
|-------|--------|--------|
| Verdict type is valid (VERIFIED or NOT-APPLICABLE) | OK/FAIL | ... |
| Findings within consultant scope (VERIFIED only) | OK/FAIL | ... |
| Findings reference specific output (VERIFIED only) | OK/FAIL | ... |
| Recommendations are actionable (VERIFIED only) | OK/FAIL | ... |
| Cross-references are accurate (VERIFIED only, if present) | OK/FAIL | ... |
| NOT-APPLICABLE justified with evidence of review (NOT-APPLICABLE only) | OK/FAIL | ... |
| No missed concerns within focus | OK/FAIL | ... |

## Failures (if any)
1. <what's wrong and what the worker must fix>
2. ...
` ` `

## Guidelines

- **You cannot see the worker's instructions.** Judge only by the consulting focus, the specialty-team output, and the worker's assessment.
- **Check for missed concerns.** Read the specialty-team output yourself and identify anything within the consulting focus. If the worker missed it, FAIL.
- **No leniency.** A concern is either addressed with specifics or it's not. "Seems fine" is not an assessment.
- **Be precise in failures.** Tell the worker exactly what was missed and what a passing response looks like.
- **PASS means complete.** Every concern within scope addressed, every finding specific, every NOT-APPLICABLE justified.
```

Note: Same backtick escaping note as Task 2.

- [ ] **Step 2: Commit**

```bash
git add plugins/dev-team/agents/consulting-team-verifier.md
git commit -m "Add consulting-team-verifier agent definition"
```

---

## Task 4: Update run_specialty_teams.py to parse consulting teams

**Files:**
- Modify: `plugins/dev-team/scripts/run_specialty_teams.py`
- Test: `tests/harness/specs/unit/specialty-teams.test.ts` (later, Task 8)

- [ ] **Step 1: Write failing test for consulting-team parsing**

Create a test specialist fixture first. Write to `plugins/dev-team/specialists/_example.md`:

```markdown
# Example Specialist

## Role
Test fixture specialist for pipeline validation.

## Persona
(coming)

## Cookbook Sources
- `guidelines/example/widget-design.md`

## Manifest
- specialty-teams/_example/example-team.md

## Consulting Teams
- consulting-teams/_example/example-consulting-team.md

## Exploratory Prompts

1. Is this a test?
```

Create `plugins/dev-team/specialty-teams/_example/example-team.md`:

```markdown
---
name: example-team
description: Test fixture specialty team
artifact: guidelines/example/widget-design.md
version: 1.0.0
---

## Worker Focus
Test fixture worker focus content.

## Verify
Test fixture verify content.
```

Now add a test to the existing test file. In `tests/harness/specs/unit/specialty-teams.test.ts`, add after the existing `run_specialty_teams.py` describe block:

```typescript
describe("run_specialty_teams.py consulting teams", () => {
  const RUN_SCRIPT = join(PLUGIN_ROOT, "scripts", "run_specialty_teams.py");

  it("outputs consulting_teams for specialist with consulting teams", () => {
    const result = execFileSync(
      "python3",
      [RUN_SCRIPT, join(SPECIALISTS_DIR, "_example.md")],
      { encoding: "utf-8" }
    );
    const data = JSON.parse(result);
    expect(data).toHaveProperty("consulting_teams");
    expect(data.consulting_teams.length).toBe(1);
    expect(data.consulting_teams[0].name).toBe("example-consulting-team");
  });

  it("outputs specialty_teams for specialist with consulting teams", () => {
    const result = execFileSync(
      "python3",
      [RUN_SCRIPT, join(SPECIALISTS_DIR, "_example.md")],
      { encoding: "utf-8" }
    );
    const data = JSON.parse(result);
    expect(data).toHaveProperty("specialty_teams");
    expect(data.specialty_teams.length).toBe(1);
  });

  it("consulting team has required fields", () => {
    const result = execFileSync(
      "python3",
      [RUN_SCRIPT, join(SPECIALISTS_DIR, "_example.md")],
      { encoding: "utf-8" }
    );
    const data = JSON.parse(result);
    const ct = data.consulting_teams[0];
    expect(ct).toHaveProperty("name");
    expect(ct).toHaveProperty("source");
    expect(ct).toHaveProperty("consulting_focus");
    expect(ct).toHaveProperty("verify");
    expect(ct).toHaveProperty("type", "consulting");
  });

  it("backwards compatible — specialist without consulting teams returns array", () => {
    const result = execFileSync(
      "python3",
      [RUN_SCRIPT, join(SPECIALISTS_DIR, "accessibility.md")],
      { encoding: "utf-8" }
    );
    const data = JSON.parse(result);
    // Old format: plain array. New format: object with specialty_teams.
    // Must support both — but new format is preferred.
    if (Array.isArray(data)) {
      expect(data.length).toBe(2); // accessibility has 2 teams
    } else {
      expect(data.specialty_teams.length).toBe(2);
      expect(data.consulting_teams.length).toBe(0);
    }
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/mfullerton/projects/active/dev-team && npx vitest run tests/harness/specs/unit/specialty-teams.test.ts`
Expected: FAIL — `run_specialty_teams.py` doesn't parse consulting teams yet.

- [ ] **Step 3: Update run_specialty_teams.py**

Replace the full content of `plugins/dev-team/scripts/run_specialty_teams.py` with:

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
            if stripped.startswith("name:"):
                fields["name"] = stripped[len("name:"):].strip()
            elif stripped.startswith("artifact:"):
                fields["artifact"] = stripped[len("artifact:"):].strip()
            elif stripped.startswith("type:"):
                fields["type"] = stripped[len("type:"):].strip()
            elif stripped.startswith("source:"):
                # source is a YAML list — collect subsequent lines starting with "  - "
                fields["source"] = []
            elif stripped.startswith("  - ") and "source" in fields and isinstance(fields["source"], list):
                fields["source"].append(stripped.strip().lstrip("- ").strip())

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

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/mfullerton/projects/active/dev-team && npx vitest run tests/harness/specs/unit/specialty-teams.test.ts`
Expected: The new consulting-team tests PASS. Some existing tests may fail because the output format changed from array to object — fix in next step.

- [ ] **Step 5: Update existing tests for new output format**

In `tests/harness/specs/unit/specialty-teams.test.ts`, update the existing `run_specialty_teams.py` describe block. The tests that call `JSON.parse(result)` and expect an array now get an object. Update these tests:

Change `expect(Array.isArray(teams)).toBe(true)` to `expect(data).toHaveProperty("specialty_teams")` and access via `data.specialty_teams` instead of `teams`. Specifically:

- `"outputs valid JSON for a specialist with manifest"` — parse as object, check `data.specialty_teams` is array with length 2
- `"each team has required fields"` — iterate `data.specialty_teams`
- `"outputs correct team count for security specialist"` — check `data.specialty_teams.length` is 15
- `"team fields match file content"` — find in `data.specialty_teams`

Also update the `"has the expected number of team files"` test to exclude the `_example` directory, and the `"every category corresponds to a specialist"` test to skip `_example`.

- [ ] **Step 6: Run full test suite to verify everything passes**

Run: `cd /Users/mfullerton/projects/active/dev-team && npx vitest run tests/harness/specs/unit/specialty-teams.test.ts`
Expected: All tests PASS.

- [ ] **Step 7: Commit**

```bash
git add plugins/dev-team/specialists/_example.md plugins/dev-team/specialty-teams/_example/example-team.md plugins/dev-team/scripts/run_specialty_teams.py tests/harness/specs/unit/specialty-teams.test.ts
git commit -m "Add consulting-team parsing to run_specialty_teams.py"
```

---

## Task 5: Extend arbitrator team-result with consulting_annotations

**Files:**
- Modify: `plugins/dev-team/scripts/arbitrator/markdown/team_result.py`
- Test: `tests/arbitrator/test_12_consulting_annotations.py`

- [ ] **Step 1: Write failing tests**

Create `tests/arbitrator/test_12_consulting_annotations.py`:

```python
"""Contract tests for consulting_annotations on team-result resource."""
import json
import pytest
from arbitrator_helpers import run_arbitrator, run_ok, run_json, make_session


def _make_session():
    return make_session(playbook="generate", team_lead="review")


def _make_result(session_id, specialist):
    return run_json("result", "create", "--session", session_id, "--specialist", specialist)["result_id"]


def test_team_result_create_has_empty_consulting_annotations():
    session_id = _make_session()
    result_id = _make_result(session_id, "security")

    run_ok(
        "team-result", "create",
        "--session", session_id, "--result", result_id,
        "--specialist", "security", "--team", "authentication",
    )

    result = run_json(
        "team-result", "get",
        "--session", session_id, "--specialist", "security", "--team", "authentication",
    )
    assert result["consulting_annotations"] == []


def test_team_result_update_adds_consulting_annotation():
    session_id = _make_session()
    result_id = _make_result(session_id, "security")

    run_ok(
        "team-result", "create",
        "--session", session_id, "--result", result_id,
        "--specialist", "security", "--team", "token-handling",
    )

    annotation = json.dumps({
        "consultant": "cross-database-compatibility",
        "verdict": "NOT-APPLICABLE",
        "explanation": "Token handling has no cross-database implications",
    })

    run_ok(
        "team-result", "update",
        "--session", session_id, "--specialist", "security", "--team", "token-handling",
        "--add-consulting-annotation", annotation,
    )

    result = run_json(
        "team-result", "get",
        "--session", session_id, "--specialist", "security", "--team", "token-handling",
    )
    assert len(result["consulting_annotations"]) == 1
    assert result["consulting_annotations"][0]["consultant"] == "cross-database-compatibility"
    assert result["consulting_annotations"][0]["verdict"] == "NOT-APPLICABLE"


def test_team_result_update_appends_multiple_annotations():
    session_id = _make_session()
    result_id = _make_result(session_id, "security")

    run_ok(
        "team-result", "create",
        "--session", session_id, "--result", result_id,
        "--specialist", "security", "--team", "cors",
    )

    annotation1 = json.dumps({
        "consultant": "cross-database-compatibility",
        "verdict": "NOT-APPLICABLE",
        "explanation": "CORS has no cross-database implications",
    })
    annotation2 = json.dumps({
        "consultant": "sync-impact",
        "verdict": "VERIFIED",
        "findings": [{"concern": "CORS preflight", "assessment": "reviewed", "recommendation": "none"}],
        "summary": "CORS config compatible with sync endpoints",
    })

    run_ok(
        "team-result", "update",
        "--session", session_id, "--specialist", "security", "--team", "cors",
        "--add-consulting-annotation", annotation1,
    )
    run_ok(
        "team-result", "update",
        "--session", session_id, "--specialist", "security", "--team", "cors",
        "--add-consulting-annotation", annotation2,
    )

    result = run_json(
        "team-result", "get",
        "--session", session_id, "--specialist", "security", "--team", "cors",
    )
    assert len(result["consulting_annotations"]) == 2
    assert result["consulting_annotations"][0]["consultant"] == "cross-database-compatibility"
    assert result["consulting_annotations"][1]["consultant"] == "sync-impact"


def test_existing_team_results_without_annotations_still_work():
    """Backwards compatibility — team-results created before this feature."""
    session_id = _make_session()
    result_id = _make_result(session_id, "security")

    run_ok(
        "team-result", "create",
        "--session", session_id, "--result", result_id,
        "--specialist", "security", "--team", "input-validation",
    )
    run_ok(
        "team-result", "update",
        "--session", session_id, "--specialist", "security", "--team", "input-validation",
        "--status", "passed", "--iteration", "1",
    )

    result = run_json(
        "team-result", "get",
        "--session", session_id, "--specialist", "security", "--team", "input-validation",
    )
    assert result["status"] == "passed"
    assert result["consulting_annotations"] == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest tests/arbitrator/test_12_consulting_annotations.py -v`
Expected: FAIL — `consulting_annotations` field doesn't exist yet.

- [ ] **Step 3: Update team_result.py**

In `plugins/dev-team/scripts/arbitrator/markdown/team_result.py`, make these changes:

In the `create` function, add `"consulting_annotations": []` to the `data` dict, after `"verifier_feedback": ""`:

```python
    data = {
        "team_result_id": team_result_id,
        "session_id": session_id,
        "result_id": result_id,
        "specialist": specialist,
        "team_name": team,
        "status": "running",
        "iteration": 0,
        "verifier_feedback": "",
        "consulting_annotations": [],
        "creation_date": ts,
        "modification_date": ts,
    }
```

In the `update` function, add handling for `--add-consulting-annotation` after the `verifier_feedback` block:

```python
    add_annotation = flags.get("add_consulting_annotation", "")
    if add_annotation:
        annotation = json.loads(add_annotation)
        if "consulting_annotations" not in data:
            data["consulting_annotations"] = []
        data["consulting_annotations"].append(annotation)
```

In the `get` function, add backwards compatibility — after reading the file, ensure the field exists:

```python
    data = json.loads(team_file.read_text())
    if "consulting_annotations" not in data:
        data["consulting_annotations"] = []
    print(json.dumps(data, ensure_ascii=False))
```

Similarly in `list_all`, add the same backwards-compat check before appending to output:

```python
        data = json.loads(team_file.read_text())
        if "consulting_annotations" not in data:
            data["consulting_annotations"] = []
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest tests/arbitrator/test_12_consulting_annotations.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Run existing team-result tests to verify no regressions**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest tests/arbitrator/test_11_team_results.py -v`
Expected: All existing tests PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/dev-team/scripts/arbitrator/markdown/team_result.py tests/arbitrator/test_12_consulting_annotations.py
git commit -m "Add consulting_annotations to team-result resource"
```

---

## Task 6: Add consulting-team file validation tests

**Files:**
- Create: `tests/harness/specs/unit/consulting-teams.test.ts`

- [ ] **Step 1: Write the test file**

Create `tests/harness/specs/unit/consulting-teams.test.ts`:

```typescript
/**
 * Consulting-team file validation — verifies every file in consulting-teams/
 * has valid frontmatter and required sections.
 */

import { describe, it, expect } from "vitest";
import { readdirSync, readFileSync, statSync, existsSync } from "fs";
import { join, basename } from "path";

const REPO_ROOT = join(__dirname, "../../../..");
const PLUGIN_ROOT = join(REPO_ROOT, "plugins", "dev-team");
const CONSULTING_TEAMS_DIR = join(PLUGIN_ROOT, "consulting-teams");

function getAllConsultingTeamFiles(): {
  category: string;
  name: string;
  path: string;
}[] {
  const files: { category: string; name: string; path: string }[] = [];
  if (!existsSync(CONSULTING_TEAMS_DIR)) return files;

  for (const category of readdirSync(CONSULTING_TEAMS_DIR)) {
    const categoryPath = join(CONSULTING_TEAMS_DIR, category);
    if (!statSync(categoryPath).isDirectory()) continue;

    for (const file of readdirSync(categoryPath)) {
      if (!file.endsWith(".md")) continue;
      files.push({
        category,
        name: basename(file, ".md"),
        path: join(categoryPath, file),
      });
    }
  }
  return files;
}

function parseFrontmatter(
  content: string
): { fields: Record<string, string | string[]>; body: string } | null {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return null;

  const fields: Record<string, string | string[]> = {};
  const lines = match[1].split("\n");
  let currentListKey = "";

  for (const line of lines) {
    if (line.startsWith("  - ") && currentListKey) {
      const list = fields[currentListKey];
      if (Array.isArray(list)) {
        list.push(line.trim().replace(/^- /, ""));
      }
      continue;
    }
    currentListKey = "";
    const colonIdx = line.indexOf(":");
    if (colonIdx === -1) continue;
    const key = line.slice(0, colonIdx).trim();
    const value = line.slice(colonIdx + 1).trim();
    if (value === "") {
      // Start of a YAML list
      fields[key] = [];
      currentListKey = key;
    } else {
      fields[key] = value;
    }
  }
  return { fields, body: match[2] };
}

const consultingTeamFiles = getAllConsultingTeamFiles();

describe("consulting-teams directory structure", () => {
  it("consulting-teams directory exists", () => {
    expect(existsSync(CONSULTING_TEAMS_DIR)).toBe(true);
  });

  it("has at least one consulting-team file", () => {
    expect(consultingTeamFiles.length).toBeGreaterThan(0);
  });
});

describe.each(consultingTeamFiles)(
  "consulting-teams/%s",
  ({ category, name, path }) => {
    const content = readFileSync(path, "utf-8");
    const parsed = parseFrontmatter(content);

    it("has valid frontmatter", () => {
      expect(parsed, "Missing or malformed frontmatter").not.toBeNull();
    });

    it("has required frontmatter fields", () => {
      expect(parsed!.fields).toHaveProperty("name");
      expect(parsed!.fields).toHaveProperty("description");
      expect(parsed!.fields).toHaveProperty("type");
      expect(parsed!.fields).toHaveProperty("source");
      expect(parsed!.fields).toHaveProperty("version");
    });

    it("type is consulting", () => {
      expect(parsed!.fields.type).toBe("consulting");
    });

    it("name field matches filename", () => {
      expect(parsed!.fields.name).toBe(name);
    });

    it("name is kebab-case", () => {
      expect(name).toMatch(/^[a-z][a-z0-9]*(-[a-z0-9]+)*$/);
    });

    it("source is a non-empty list", () => {
      expect(Array.isArray(parsed!.fields.source)).toBe(true);
      expect((parsed!.fields.source as string[]).length).toBeGreaterThan(0);
    });

    it("version is semver", () => {
      expect(parsed!.fields.version).toMatch(/^\d+\.\d+\.\d+$/);
    });

    it("description is non-empty", () => {
      expect(
        (parsed!.fields.description as string).length
      ).toBeGreaterThan(0);
    });

    it("has Consulting Focus section", () => {
      expect(parsed!.body).toContain("## Consulting Focus");
    });

    it("has Verify section", () => {
      expect(parsed!.body).toContain("## Verify");
    });

    it("Consulting Focus section is non-empty", () => {
      const match = parsed!.body.match(
        /## Consulting Focus\n([\s\S]*?)(?=\n## |\n*$)/
      );
      expect(match, "Consulting Focus section not found").not.toBeNull();
      expect(match![1].trim().length).toBeGreaterThan(0);
    });

    it("Verify section is non-empty", () => {
      const match = parsed!.body.match(
        /## Verify\n([\s\S]*?)(?=\n## |\n*$)/
      );
      expect(match, "Verify section not found").not.toBeNull();
      expect(match![1].trim().length).toBeGreaterThan(0);
    });
  }
);
```

- [ ] **Step 2: Run test to verify it passes with the test fixture**

Run: `cd /Users/mfullerton/projects/active/dev-team && npx vitest run tests/harness/specs/unit/consulting-teams.test.ts`
Expected: All tests PASS (using the `_example/example-consulting-team.md` fixture).

- [ ] **Step 3: Commit**

```bash
git add tests/harness/specs/unit/consulting-teams.test.ts
git commit -m "Add consulting-team file validation tests"
```

---

## Task 7: Update specialist-spec.md

**Files:**
- Modify: `plugins/dev-team/docs/specialist-spec.md`

- [ ] **Step 1: Add Consulting Teams section to the spec**

In `plugins/dev-team/docs/specialist-spec.md`, after the `### 5. Manifest` section and before `### 6. Exploratory Prompts`, add:

```markdown
### 5b. Consulting Teams (optional)

` ` `markdown
## Consulting Teams
- consulting-teams/<category>/<team-name>.md
- consulting-teams/<category>/<team-name>.md
` ` `

- Markdown list of paths to consulting-team files, relative to the repo root
- Each path MUST resolve to an existing file in `consulting-teams/`
- If absent, the specialist has no consulting teams — pipeline runs as before
- When present, every specialty-team's output passes through all listed consulting teams as a required verification gate
```

Add to the `## Consulting-Team File Specification` section after the `## Specialty-Team File Specification` section:

```markdown
## Consulting-Team File Specification

Each consulting-team is a standalone markdown file in `consulting-teams/<category>/<name>.md`.

### File Location

`consulting-teams/<category>/<name>.md` where:
- `<category>` matches a specialist filename in `specialists/` (e.g., `platform-database`)
- `<name>` is lowercase kebab-case

### Frontmatter

` ` `yaml
---
name: <kebab-case-name>
description: <human-readable description of what this consultant checks>
type: consulting
source:
  - <path to research doc>
  - <path to research doc>
version: <semver>
---
` ` `

| Field | Format | Description |
|-------|--------|-------------|
| name | `[a-z][a-z0-9]*(-[a-z0-9]+)*` | Unique within category, matches filename |
| description | Free text, ~120 chars | Human-readable summary for discovery |
| type | `consulting` | Must be exactly `consulting` |
| source | YAML list of paths | Research documents this consultant draws from |
| version | `N.N.N` semver | Tracks changes to this consulting-team definition |

### Body Sections

` ` `markdown
## Consulting Focus
<text>

## Verify
<text>
` ` `

| Section | Description |
|---------|-------------|
| Consulting Focus | What cross-cutting concern this consultant evaluates (mode-independent). Guides the consulting worker agent. |
| Verify | Concrete acceptance criteria. The consulting verifier uses this to determine PASS/FAIL of the consultant's assessment. |

### Verdict Types

Consulting teams produce one of two verdicts:
- **VERIFIED** — output was reviewed, findings within the consultant's focus were found and assessed
- **NOT-APPLICABLE** — output was reviewed, nothing within the consultant's focus was found (with evidence of review)
```

Add to the validation rules table:

```markdown
| S07 | Each consulting-team path in `## Consulting Teams` resolves to a file with valid frontmatter (name, description, type, source, version) and body sections (Consulting Focus, Verify) | FAIL |
| S08 | `type: consulting` present in every consulting-team file's frontmatter | FAIL |
| C09 | `source` field is a non-empty list in every consulting-team file | WARN |
```

Update the Parser Contract section to add:

```markdown
`scripts/run_specialty_teams.py` also reads the `## Consulting Teams` heading (if present) using the same pattern. For each referenced consulting-team file: YAML frontmatter for `name`, `type`, and `source`, `## Consulting Focus` and `## Verify` body sections for content. Outputs one JSON object per consulting-team with fields: name, type, source, consulting_focus, verify.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/dev-team/docs/specialist-spec.md
git commit -m "Add consulting-team section to specialist spec"
```

---

## Task 8: Update specialist-guide.md

**Files:**
- Modify: `plugins/dev-team/docs/specialist-guide.md`

- [ ] **Step 1: Add consulting-team documentation**

In `plugins/dev-team/docs/specialist-guide.md`, after the `### Key Principle` section, add:

```markdown
### Consulting-Teams

Some specialists have **consulting-teams** — a special kind of specialty-team that acts as a required verification gate for every specialty-team's output. Consulting teams catch cross-cutting concerns that no single specialty team owns.

```
Specialist (role + persona)
  └── manages N specialty-teams, one at a time
        └── Specialty-Team (focused on ONE guideline/principle/rule)
              ├── Worker — does the work for this artifact
              ├── Verifier — checks the work, independent of worker
              ├── Loop until verifier signs off
              └── Consulting review (if specialist has consulting-teams)
                    └── For each consulting-team:
                          ├── Consulting Worker — reviews output through cross-cutting lens
                          ├── Consulting Verifier — checks the review
                          └── Loop until verifier signs off
```

**When to use consulting teams:** When a specialist's concerns are deeply interdependent — where a decision in one specialty team cascades into others. Most specialists don't need consulting teams. Use them when cross-cutting consistency matters more than speed.

**Verdict types:** Each consulting review produces VERIFIED (concerns found and assessed) or NOT-APPLICABLE (nothing within the consultant's purview, with evidence of review). Both go through the consulting verifier.

**Accumulated context:** Consulting reviews run per-specialty-team. Each consultant builds context as the pipeline progresses and can reference its own prior findings for consistency checking.
```

In the `## Execution Flow` section, after step 3d (`If PASS: record result`), add:

```markdown
   e. If specialist has consulting-teams: for each consulting-team:
      - Spawn consulting worker with: specialty-team output, consulting focus, accumulated context
      - Spawn consulting verifier with: consulting focus, specialty-team output, consulting worker output
      - If FAIL and iterations < 3: feed failure back to consulting worker, retry
      - If PASS: record consulting annotation on team-result
      - If FAIL after 3: record escalation
```

In the `## Adding a New Specialist` section, add after step 3:

```markdown
3b. (Optional) Create `consulting-teams/<domain>/` directory with one consulting-team file per cross-cutting concern
3c. Add the consulting-team file paths to the specialist's `## Consulting Teams` section
```

- [ ] **Step 2: Commit**

```bash
git add plugins/dev-team/docs/specialist-guide.md
git commit -m "Add consulting-team documentation to specialist guide"
```

---

## Task 9: Update architecture.md

**Files:**
- Modify: `docs/architecture.md`

- [ ] **Step 1: Update terminology table**

In the Terminology table in `docs/architecture.md`, add after the Specialty-Verifier row:

```markdown
| **Consulting-Team** | Standalone file defining a consulting worker-verifier pair focused on one cross-cutting concern. Reviews every specialty-team's output within a specialist. Lives in `consulting-teams/`. |
| **Consulting-Worker** | LLM agent. Reviews a specialty-team's passed output through a cross-cutting lens. Produces VERIFIED or NOT-APPLICABLE. |
| **Consulting-Verifier** | LLM agent. Checks consulting-worker output for completeness. Returns PASS/FAIL. Max 3 retries before escalation. |
```

- [ ] **Step 2: Update pipeline diagram**

Update the pipeline section to show consulting teams:

```
User invokes /dev-team <command>
  → Skill router (SKILL.md) loads config, inits DB, routes to workflow
    → Team-lead runs the workflow, talks to user
      → Team-lead dispatches specialists via arbitrator
        → Specialist script reads assignment
          → Specialty-teams run (worker-verifier loop, max 3 retries)
          → Consulting-teams review (if any — worker-verifier loop per consultant)
          → Specialist-persona writes interpretations
        → Specialist returns result (result_id + pass/fail) via arbitrator
      → Team-lead aggregates results
    → Team-lead presents report to user
```

- [ ] **Step 3: Update component counts**

Update the Agents line to reflect the new count (18 + 2 = 20):
```
18 agent definitions in `agents/`. → 20 agent definitions in `agents/`.
```

Update the file map to include consulting-teams:
```
    consulting-teams/         # Consulting-team files (cross-cutting verification)
```

- [ ] **Step 4: Commit**

```bash
git add docs/architecture.md
git commit -m "Add consulting-team terminology and pipeline to architecture docs"
```

---

## Task 10: Run full test suite and verify

**Files:** None (verification only)

- [ ] **Step 1: Run arbitrator contract tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 -m pytest tests/arbitrator/ -v`
Expected: All tests PASS, including new test_12_consulting_annotations.py.

- [ ] **Step 2: Run specialty-teams validation tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && npx vitest run tests/harness/specs/unit/specialty-teams.test.ts`
Expected: All tests PASS, including new consulting-team parsing tests.

- [ ] **Step 3: Run consulting-teams validation tests**

Run: `cd /Users/mfullerton/projects/active/dev-team && npx vitest run tests/harness/specs/unit/consulting-teams.test.ts`
Expected: All tests PASS.

- [ ] **Step 4: Manual verification — run_specialty_teams.py with _example specialist**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 plugins/dev-team/scripts/run_specialty_teams.py plugins/dev-team/specialists/_example.md`

Expected output:
```json
{
  "specialty_teams": [
    {
      "name": "example-team",
      "artifact": "guidelines/example/widget-design.md",
      "worker_focus": "Test fixture worker focus content.",
      "verify": "Test fixture verify content."
    }
  ],
  "consulting_teams": [
    {
      "name": "example-consulting-team",
      "type": "consulting",
      "source": [
        "docs/research/database/decision-frameworks.md"
      ],
      "consulting_focus": "Validates that example specialty-team outputs are internally consistent and reference concrete evidence.",
      "verify": "Consultant produced VERIFIED with specific findings referencing the specialty-team output, or NOT-APPLICABLE with an explanation that demonstrates the output was reviewed."
    }
  ]
}
```

- [ ] **Step 5: Manual verification — run_specialty_teams.py with existing specialist (backwards compat)**

Run: `cd /Users/mfullerton/projects/active/dev-team && python3 plugins/dev-team/scripts/run_specialty_teams.py plugins/dev-team/specialists/accessibility.md`

Expected: JSON object with `specialty_teams` (2 items) and `consulting_teams` (empty array).
