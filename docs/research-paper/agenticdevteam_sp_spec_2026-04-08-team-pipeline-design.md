# Team Pipeline Design

## Goal

Extract the reusable multi-agent pipeline from dev-team into a standalone `plugins/team-pipeline/` plugin. Users define their own teams — team-leads, specialists, specialty-teams, workflows — and team-pipeline provides the orchestration machinery.

Dev-team stays untouched during this work. A test team ("name-a-puppy") validates the pipeline independently. Dev-team migrates to use team-pipeline later, as a separate effort.

## Principles

- The pipeline has zero domain coupling. It does not know about cookbooks, recipes, or software engineering.
- Specialists, specialty-teams, and workflows are user-provided content. The pipeline provides the execution patterns.
- File format specs from dev-team are proven and carry over with minimal changes (terminology cleanup only).

## Directory Structure

```
plugins/
  team-pipeline/
    .claude-plugin/          # Plugin manifest
    agents/
      specialty-team-worker.md
      specialty-team-verifier.md
      consulting-team-worker.md
      consulting-team-verifier.md
    team-leads/
      interview.md
      analysis.md
    scripts/
      arbitrator.py
      storage_provider.py
      storage-provider/
        markdown/            # 13 resource scripts
      run_specialty_teams.py
      load_config.py
      observers/
        dispatch.py
        stenographer.py
        oslog.py
    docs/
      specialist-spec.md
      specialty-team-spec.md
      consulting-team-spec.md
      team-lead-spec.md
    services/
      dashboard/             # Live workflow viewer
```

## Components

### Agents

Four generic agents that power the worker/verifier loops.

**specialty-team-worker**: Reads one source document and applies it to a target. Four modes:

- `interview` — produce questions based on the source material
- `analysis` — evaluate a target against the source's requirements
- `generation` — produce or modify output to satisfy the source's requirements
- `review` — evaluate an artifact against the source's requirements

Each mode has a consistent output format so verifiers, reporting, and aggregation work generically. Terminology change from dev-team: "cookbook artifact" becomes "source" throughout.

**specialty-team-verifier**: Checks worker output against the specialty-team's verify criteria. Returns PASS or FAIL with reasons. Unchanged from dev-team except terminology.

**consulting-team-worker**: Reviews a specialty-team's passed output through a cross-cutting lens. Produces VERIFIED or NOT-APPLICABLE. Unchanged from dev-team except terminology.

**consulting-team-verifier**: Checks consulting-worker output. Returns PASS or FAIL. Unchanged from dev-team.

All four agents: max retries is configurable (dev-team hardcodes 3). Default remains 3.

### Team-Leads

Standalone markdown definitions — new concept, extracted from what dev-team embeds in workflow files.

**File format:**

```markdown
# <Name> Team-Lead

## Role
<1-3 sentences — what kind of workflow this team-lead runs>

## Persona

### Archetype
<1 sentence — what kind of expert this is>

### Voice
<communication style>

### Priorities
<what this team-lead optimizes for>

## Phases
<list of phase names this team-lead progresses through>

## Interaction Style
<how this team-lead communicates with the user — gates, questions, notifications>
```

Two premade team-leads ship with team-pipeline:

**interview** — gathers information from the user through structured questioning, backed by specialist expertise. Phases: intro, structured, exploratory, synthesis. The only participant that talks to the user. Passes specialist questions through with attribution.

**analysis** — dispatches specialists against a target, aggregates findings into a structured report. Phases: scan, dispatch, aggregate, report. Presents findings to the user organized by specialist and severity.

### Scripts

Extracted from dev-team with terminology changes only.

**arbitrator.py** — communication conduit. Delegates to storage-provider. Resources: session, state, message, gate-option, result, finding, interpretation, artifact, reference, retry, report, team-result. Unchanged behavior.

**storage_provider.py + storage-provider/markdown/** — backend-swappable persistence. 13 resource scripts for the markdown backend. Unchanged.

**run_specialty_teams.py** — parses specialist manifests to JSON. Reads `## Manifest` and `## Consulting Teams` sections, resolves paths, parses frontmatter and body sections. Unchanged.

**load_config.py** — loads team config from JSON. Validates only team-pipeline fields: `team_name`, `user_name`, `data_dir`. Passes through all other fields for the team's own use.

**observers/** — subagent activity capture. dispatch.py (hook entry point), stenographer.py (JSONL session log), oslog.py (system log). Unchanged.

### Config

Generic config structure:

```json
{
  "team_name": "<name>",
  "user_name": "<user name>",
  "data_dir": "<where sessions/results are stored>",
  "sources": ["<paths to knowledge/reference material>"]
}
```

Team-pipeline requires `team_name`, `user_name`, `data_dir`. Everything else is the team's business.

### Specs

File format specifications for user-provided content:

**specialist-spec.md** — adapted from dev-team's `specialist-spec.md`. Changes:
- "Cookbook Sources" section renamed to "Sources"
- Artifact references in specialty-team files become "source" references
- All cookbook-specific language removed
- Validation rules carry over with updated terminology

**specialty-team-spec.md** — extracted from the specialty-team section of dev-team's specialist-spec. Same frontmatter (name, description, source, version), same body sections (Worker Focus, Verify).

**consulting-team-spec.md** — extracted from the consulting-team section. Same frontmatter (name, description, type, source, version), same body sections (Consulting Focus, Verify).

**team-lead-spec.md** — new spec for team-lead definition files.

### Services

**dashboard** — live workflow viewer. Flask app, port 9876. Carried over from dev-team. Needs to be parameterized to work with any team's session data rather than assuming dev-team paths.

## Path Resolution (Flagged for Later)

User workflows need to reference team-pipeline's agents and scripts. Current solution: user's SKILL.md sets a `TEAM_PIPELINE_ROOT` env var at startup. Known to be insufficient — better solution TBD.

## Test Team: Name-a-Puppy

Validates the full pipeline with zero domain complexity.

### Specialists (3)

**temperament** — dog temperament and personality. Specialty-teams: energy-level, sociability.

**breed** — breed characteristics and naming traditions. Specialty-teams: size-traits, name-traditions.

**lifestyle** — owner lifestyle fit. Specialty-teams: living-space, activity-level.

### Workflow

One workflow: `interview`. Uses the premade interview team-lead. Dispatches all 3 specialists. Interviews the user about their puppy, their living situation, and their preferences, then synthesizes a name recommendation.

### Structure

```
plugins/name-a-puppy/
  specialists/
    temperament.md
    breed.md
    lifestyle.md
  specialty-teams/
    temperament/
      energy-level.md
      sociability.md
    breed/
      size-traits.md
      name-traditions.md
    lifestyle/
      living-space.md
      activity-level.md
  skills/
    name-a-puppy/
      SKILL.md
      workflows/
        interview.md
```

No consulting-teams. No custom agents. Minimal viable team to prove the pipeline works end-to-end.

## What Is NOT Included

- DB layer (not working, not finished)
- Project-storage-provider (PM-specific)
- Dev-team-specific agents (recipe-writer, code-generator, transcript-analyzer, build-runner, smoke-tester, codebase-scanner, decomposition-synthesizer, project-assembler, project-scaffolder, artifact-reviewer, code-comparator, scope-matcher, specialist-aligner, specialist-interviewer, specialist-code-pass)
- Dev-team workflows
- Dev-team migration (separate effort)
