# Consulting-Team Pipeline Feature Design

## Summary

Add consulting teams to the dev-team pipeline — a new type of specialty team that acts as a required verification gate for every specialty-team's output within a specialist. Consulting teams catch cross-cutting concerns that no single specialty team owns, ensuring interdependent decisions are consistent across the full specialist pipeline.

## Motivation

Most specialists have independent concerns — the accessibility team's findings don't constrain the security team's findings. But some specialists (notably `platform-database`) have deeply interdependent concerns where a decision in one specialty team cascades into others. A primary key choice affects sync, performance, schema evolution, and type mapping simultaneously. Without a mechanism to catch these cross-cutting interactions, the team-lead would have to manually synthesize — and miss things.

Consulting teams solve this by reviewing every specialty-team's output through a cross-cutting lens, flagging conflicts, enriching with context, and ensuring consistency.

## Design Principles

- **Same worker/verifier structure** — consulting teams are not a special case. They follow the same worker → verifier → retry loop as specialty teams.
- **Required gate, not optional** — every specialty-team's output passes through every consulting team. The consultant either adds value (VERIFIED) or explicitly says nothing is relevant (NOT-APPLICABLE).
- **Backwards compatible** — specialists without consulting teams work exactly as before. The consulting-team section is optional.
- **Accumulated context** — because consulting runs per-specialty-team, each consultant builds context across the pipeline and can reference its own prior findings.

## Architecture

### Pipeline Change

**Before (current):**
```
For each specialty-team in manifest:
  → Worker → Verifier (max 3 retries) → Record result
After all teams: aggregate
```

**After:**
```
For each specialty-team in manifest:
  → Worker → Verifier (max 3 retries) → Passed output
  → For each consulting-team:
      → Consulting worker reviews → VERIFIED or NOT-APPLICABLE
      → Consulting verifier checks (max 3 retries)
  → Record result (specialty-team output + consulting annotations)
After all teams: aggregate (includes consulting findings)
```

### New Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `consulting-team-worker.md` | `agents/` | Agent: reviews specialty-team output through cross-cutting lens |
| `consulting-team-verifier.md` | `agents/` | Agent: verifies the consulting worker's assessment |
| `consulting-teams/<category>/` | New top-level directory | Consulting-team definition files |
| `## Consulting Teams` | In specialist `.md` files | New optional section listing consulting-team paths |

### Consulting Worker vs Specialty-Team Worker

| | Specialty-Team Worker | Consulting Worker |
|---|---|---|
| **Input** | Cookbook artifact + target (code/transcript/recipe) + mode | Consulting-team definition + specialty-team's passed output + accumulated context |
| **Job** | Apply artifact requirements to target | Evaluate specialty-team output through cross-cutting lens |
| **Output** | Findings per requirement | VERIFIED (with findings) or NOT-APPLICABLE (with explanation) |
| **Scope** | One cookbook artifact | One cross-cutting concern |
| **Modifies target** | Yes (in generation mode) | Never — read-only annotation |

### Accumulated Context

Each consulting worker receives its own prior VERIFIED findings from earlier specialty-teams in the session. This enables:

- Referencing earlier decisions: "As noted in my review of data-types, we're using BLOB UUIDv7 — this team's recommendation is consistent"
- Flagging conflicts: "This contradicts my finding from normalization where we decided against denormalization for synced tables"
- Building progressive understanding across the pipeline

Accumulated context is scoped per-consultant — `sync-impact`'s history is separate from `cross-database-compatibility`'s history.

## File Formats

### Consulting-Team Definition File

Location: `consulting-teams/<category>/<name>.md`

```markdown
---
name: <kebab-case-name>
description: <what this consultant checks for>
type: consulting
source:
  - <path to research doc or section>
  - <path to research doc or section>
version: <semver>
---

## Consulting Focus
<what this consultant evaluates in every specialty-team's output — mode-independent>

## Verify
<acceptance criteria for the consulting verifier>
```

**Differences from specialty-team files:**

| Field | Specialty-Team | Consulting-Team |
|-------|---------------|-----------------|
| `artifact` | Single cookbook file path | N/A — not present |
| `source` | N/A | List of research doc paths (can be multiple) |
| `type` | Implied (absent) | `consulting` (explicit, required) |
| Body heading | `## Worker Focus` | `## Consulting Focus` |

The `source` field is a list because consulting teams are cross-cutting — they draw from multiple research documents simultaneously.

### Specialist File — New Section

New optional `## Consulting Teams` section after `## Manifest`:

```markdown
## Manifest
- specialty-teams/platform-database/naming-conventions.md
- specialty-teams/platform-database/data-types.md
- ...

## Consulting Teams
- consulting-teams/platform-database/cross-database-compatibility.md
- consulting-teams/platform-database/sync-impact.md
- consulting-teams/platform-database/access-pattern-coherence.md

## Exploratory Prompts
...
```

If the section is absent, the specialist has no consulting teams and the pipeline runs as before.

### Specialist Spec Validation Rules (New)

| ID | Rule | Severity |
|----|------|----------|
| S07 | Each consulting-team path in `## Consulting Teams` resolves to a file with valid frontmatter (name, description, type, source, version) and body sections (Consulting Focus, Verify) | FAIL |
| S08 | `type: consulting` present in every consulting-team file's frontmatter | FAIL |
| C09 | `source` field is a non-empty list in every consulting-team file | WARN |

## Agent Definitions

### consulting-team-worker.md

```markdown
---
name: consulting-team-worker
description: Reviews a specialty-team's passed output through a cross-cutting lens.
  Produces VERIFIED (with findings) or NOT-APPLICABLE (with explanation).
tools:
  - Read
  - Glob
  - Grep
permissionMode: plan
maxTurns: 12
---
```

**Input:**
1. **Consulting focus** — from the consulting-team definition file
2. **Source material paths** — the research docs this consultant draws from
3. **Specialty-team name** — which team's output is being reviewed
4. **Specialty-team output** — the passed worker output (post-verifier)
5. **Specialty-team artifact** — what cookbook artifact the team was working from
6. **Mode** — interview/analysis/generation/review
7. **Accumulated context** — this consultant's VERIFIED findings from prior specialty-teams in this session (empty for the first team)

**Output format — VERIFIED:**
```markdown
## Verdict: VERIFIED

## Specialty-Team Reviewed
<team name> — <artifact>

## Findings

| Concern | Assessment | Recommendation |
|---------|-----------|----------------|
| <cross-cutting concern> | <what the consultant found> | <specific adjustment or confirmation> |

## Cross-References
<references to prior consulting findings in this session, if relevant>

## Summary
<1-2 sentences — the key takeaway for downstream teams>
```

**Output format — NOT-APPLICABLE:**
```markdown
## Verdict: NOT-APPLICABLE

## Specialty-Team Reviewed
<team name> — <artifact>

## Explanation
<why this specialty-team's output has no concerns within this consultant's purview>
```

**Behavioral constraints:**
- Must always produce exactly one of the two verdict types
- Must reference accumulated context when relevant (consistency across teams)
- Read-only — never modifies code or recipes, only annotates
- Must reference specific content from the specialty-team's output (not vague)

### consulting-team-verifier.md

```markdown
---
name: consulting-team-verifier
description: Checks a consulting worker's assessment for completeness and correctness.
  Verifies VERIFIED findings are substantive and NOT-APPLICABLE judgments are correct.
tools:
  - Read
  - Glob
  - Grep
permissionMode: plan
maxTurns: 8
---
```

**Input:**
1. **Consulting focus** — from the consulting-team definition file
2. **Verify criteria** — from the consulting-team definition file
3. **Source material paths** — the research docs
4. **Specialty-team output** — the original passed output being reviewed
5. **Consultant worker output** — the worker's VERIFIED or NOT-APPLICABLE response

**Verification rules for VERIFIED:**
- Every concern raised must be within the consultant's stated focus
- Findings must reference specific content from the specialty-team's output
- Recommendations must be actionable
- Cross-references to prior findings must be accurate
- No findings that belong to a different consultant's domain

**Verification rules for NOT-APPLICABLE:**
- The explanation must demonstrate the consultant actually reviewed the output (not a blind pass-through)
- If the specialty-team's output contains anything within the consultant's focus, NOT-APPLICABLE is wrong — FAIL

**Output format:**
```markdown
## Verdict: PASS | FAIL

## Assessment Type Reviewed
VERIFIED | NOT-APPLICABLE

## Checks

| Check | Status | Detail |
|-------|--------|--------|
| Verdict type is valid | OK/FAIL | ... |
| Findings within consultant scope | OK/FAIL | ... |
| Findings reference specific output | OK/FAIL | ... |
| NOT-APPLICABLE justified | OK/FAIL | ... |

## Failures (if any)
1. <what's wrong and what the worker must fix>
```

Same retry mechanics as specialty-team verifier — max 3 retries, then escalate.

## Script Changes

### run_specialty_teams.py

Currently reads `## Manifest` and outputs a JSON array of specialty-teams. Updated to also read `## Consulting Teams`.

**New output format:**

```json
{
  "specialty_teams": [
    { "name": "naming-conventions", "artifact": "...", "worker_focus": "...", "verify": "..." }
  ],
  "consulting_teams": [
    { "name": "cross-database-compatibility", "source": ["..."], "consulting_focus": "...", "verify": "..." }
  ]
}
```

If `## Consulting Teams` is absent, `consulting_teams` is an empty array. Backwards compatible.

### Orchestration Logic

Workflows that dispatch specialists add the consulting loop after the specialty-team worker/verifier loop:

```python
consulting_context = {}  # keyed by consultant name, values are list of prior findings

for team in specialty_teams:
    # Existing: specialty-team worker/verifier loop
    output = run_worker(team, target, mode)
    verdict = run_verifier(team, output)
    # retry loop (max 3)...

    # New: consulting-team review loop
    consulting_annotations = []
    for consultant in consulting_teams:
        prior_findings = consulting_context.get(consultant.name, [])

        annotation = run_consulting_worker(
            consultant=consultant,
            specialty_team_name=team.name,
            specialty_team_output=output,
            specialty_team_artifact=team.artifact,
            mode=mode,
            accumulated_context=prior_findings
        )
        consulting_verdict = run_consulting_verifier(
            consultant=consultant,
            specialty_team_output=output,
            consulting_worker_output=annotation
        )
        # retry loop (max 3)...

        consulting_annotations.append(annotation)

        # Accumulate VERIFIED findings for this consultant
        if annotation.verdict == "VERIFIED":
            consulting_context.setdefault(consultant.name, []).append({
                "team": team.name,
                "findings": annotation.findings,
                "summary": annotation.summary
            })

    record_result(team, output, consulting_annotations)
```

## Arbitrator Changes

### Extend team-result resource

The team-result resource gets a new `consulting_annotations` field:

```json
{
  "id": "tr-001",
  "team": "primary-keys",
  "status": "passed",
  "output": "...",
  "consulting_annotations": [
    {
      "consultant": "cross-database-compatibility",
      "verdict": "VERIFIED",
      "findings": [
        { "concern": "...", "assessment": "...", "recommendation": "..." }
      ],
      "summary": "BLOB UUIDv7 confirmed compatible with PostgreSQL UUID type"
    },
    {
      "consultant": "sync-impact",
      "verdict": "NOT-APPLICABLE",
      "explanation": "Primary key strategy has no sync-specific implications beyond what sync-schema-design will cover"
    }
  ]
}
```

Existing team-results without consulting annotations continue to work — the field is optional (empty array default).

## Crash Recovery

Extends the existing crash recovery model:

- If a session crashes mid-consulting-review, on resume the orchestrator checks which consultants have completed for the current team
- Consultants with recorded annotations are skipped
- Consultants without annotations re-run
- The specialty-team's passed output is preserved — no need to re-run the specialty-team itself
- If the session crashed mid-consulting-verifier-retry, the consulting worker's output is preserved and the verifier re-runs

## Aggregation

The specialist's final aggregation report includes a new section:

```markdown
## Consulting Findings

### cross-database-compatibility
- **VERIFIED on 14 teams, NOT-APPLICABLE on 8 teams**
- Key findings: <aggregated summary>

### sync-impact
- **VERIFIED on 11 teams, NOT-APPLICABLE on 11 teams**
- Key findings: <aggregated summary>

### access-pattern-coherence
- **VERIFIED on 9 teams, NOT-APPLICABLE on 13 teams**
- Key findings: <aggregated summary>
```

## Scope

### In scope
- Consulting-team definition file format and directory structure
- Two new agent definitions (consulting-team-worker, consulting-team-verifier)
- Specialist spec update (new optional section, new validation rules)
- run_specialty_teams.py update (parse consulting teams)
- Orchestration logic change (consulting loop after specialty-team loop)
- Arbitrator team-result extension (consulting_annotations field)
- Crash recovery extension
- Aggregation report extension
- Specialist guide and specialist spec documentation updates

### Out of scope
- Creating actual consulting-team definition files (that's the database specialist implementation)
- Modifying any existing specialist to use consulting teams
- Dashboard changes (can display consulting annotations later)
- Database schema changes (consulting annotations are stored in the team-result payload)

## Implementation Order

1. Create `consulting-teams/` directory
2. Write `agents/consulting-team-worker.md`
3. Write `agents/consulting-team-verifier.md`
4. Update `scripts/run_specialty_teams.py` to parse `## Consulting Teams`
5. Update orchestration logic in workflows to include consulting loop
6. Update arbitrator team-result to support `consulting_annotations`
7. Update crash recovery to handle mid-consulting interrupts
8. Update specialist aggregation to include consulting findings
9. Update `docs/specialist-spec.md` with new section and validation rules
10. Update `docs/specialist-guide.md` with consulting-team documentation
11. Update `docs/architecture.md` terminology and pipeline description
12. Test with a minimal specialist that has one specialty-team and one consulting-team

## Testing

- **Unit**: run_specialty_teams.py correctly parses specialists with and without consulting teams
- **Contract**: consulting-team-worker output matches expected VERIFIED/NOT-APPLICABLE format
- **Contract**: consulting-team-verifier correctly PASS/FAIL for valid and invalid consulting outputs
- **Integration**: full pipeline run with a test specialist that has consulting teams
- **Backwards compatibility**: existing specialists without consulting teams run unchanged
- **Crash recovery**: resume works correctly when interrupted mid-consulting-review
