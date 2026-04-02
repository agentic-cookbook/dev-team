# Test Mode Contract v1.0

All skills in the agentic interview team support `--test-mode` for automated testing. This document defines the shared contract that all skills follow.

## Common Flags

- `--test-mode` — activates automated testing mode
- `--target <path>` — specifies the input (repo path for analyze, cookbook project path for generate/build)
- `--config <path>` — path to test config file (must pre-exist, no setup flow)

### Interview-specific flags
- `--persona <path>` — path to a persona file for the simulated user
- `--max-exchanges <n>` — stop after N question-answer exchanges

## Common Behavior

When `--test-mode` is active:

1. **Auto-approve all prompts.** Every `AskUserQuestion` call is auto-approved — proceed with the first/default option. Do not wait for user input.
2. **Exception: interview skill.** The interview skill uses the `simulated-user` agent with `--persona <path>` instead of auto-approve, since it needs realistic conversational answers.
3. **Write test log.** Write structured events to `test-log.jsonl` in the project output directory. One JSON object per line.
4. **No profile updates.** Don't modify user profiles or persist learning — test data is ephemeral.
5. **Config must pre-exist.** If the config file doesn't exist at the `--config` path, fail immediately with a clear error.
6. **Bounded execution.** For interview: stop after `--max-exchanges`. For other skills: run to completion.

## Unified Log Schema

Every log line is a JSON object with these base fields:

```json
{
  "skill": "<skill-name>",
  "phase": "<phase-name>",
  "event": "<event-type>",
  "timestamp": "<ISO 8601>"
}
```

Plus event-specific fields documented below.

### Common Events (All Skills)

| Event | Additional Fields | When |
|-------|------------------|------|
| `phase_started` | — | A skill phase begins |
| `phase_completed` | `duration_ms` | A skill phase finishes |
| `agent_spawned` | `agent`, `recipe`?, `specialist`? | A subagent is launched |
| `agent_completed` | `agent`, `recipe`?, `specialist`?, `status` | A subagent returns |
| `file_written` | `path`, `file_type` | An artifact is persisted |
| `error` | `message`, `agent`?, `recoverable` | Something went wrong |
| `test_complete` | `phases_completed`, `agents_spawned`, `files_written`, `errors` | Final summary |

### interview Events

| Event | Additional Fields |
|-------|------------------|
| `specialist_invoked` | `specialist`, `mode` |
| `question_asked` | `specialist`, `question_id` |
| `answer_received` | `transcript_file` |
| `analysis_written` | `analysis_file`, `transcript_id` |
| `checklist_updated` | `topic`, `action` |

### analyze-project Events

| Event | Additional Fields |
|-------|------------------|
| `architecture_scanned` | `tech_stack`, `platforms`, `module_count` |
| `scopes_matched` | `count`, `high_confidence`, `medium_confidence`, `low_confidence` |
| `recipe_generated` | `scope`, `output_path`, `needs_review_count` |
| `project_assembled` | `component_count`, `manifest_path` |

### generate-project Events

| Event | Additional Fields |
|-------|------------------|
| `reviewer_spawned` | `recipe_scope`, `specialist` |
| `review_completed` | `recipe_scope`, `specialist`, `suggestion_count`, `gap_count` |
| `suggestion_approved` | `recipe_scope`, `specialist`, `title` |
| `suggestion_rejected` | `recipe_scope`, `specialist`, `title` |
| `recipe_updated` | `recipe_scope`, `changes_applied`, `new_version` |

### build-project Events

| Event | Additional Fields |
|-------|------------------|
| `scaffold_created` | `build_system`, `file_count`, `build_command` |
| `code_generated` | `recipe_scope`, `files_written`, `must_implemented`, `must_total` |
| `specialist_pass_complete` | `recipe_scope`, `specialist`, `changes_count` |
| `code_review_complete` | `recipe_scope`, `issues_found`, `issues_fixed` |
| `build_attempted` | `attempt`, `error_count`, `fixed_count` |
| `build_result` | `success`, `total_attempts`, `remaining_errors` |
| `smoke_test_result` | `launch_pass`, `conformance_passed`, `conformance_failed`, `conformance_skipped` |

## How to Emit Events

Skills write test log events by appending a JSON line to `test-log.jsonl` in the project output directory using the Write tool. Example:

At each phase boundary:
- Before starting Phase 1: write `{"skill": "analyze-project", "phase": "architecture-scan", "event": "phase_started", "timestamp": "<now>"}`
- After completing Phase 1: write `{"skill": "analyze-project", "phase": "architecture-scan", "event": "phase_completed", "duration_ms": <elapsed>, "timestamp": "<now>"}`

At each agent interaction:
- Before spawning: write `{"skill": "analyze-project", "phase": "architecture-scan", "event": "agent_spawned", "agent": "codebase-scanner", "timestamp": "<now>"}`
- After return: write `{"skill": "analyze-project", "phase": "architecture-scan", "event": "agent_completed", "agent": "codebase-scanner", "status": "success", "timestamp": "<now>"}`

At each file write:
- After persisting: write `{"skill": "analyze-project", "phase": "recipe-generation", "event": "file_written", "path": "app/ui/file-tree-browser.md", "file_type": "recipe", "timestamp": "<now>"}`

At the end:
- Write `{"skill": "analyze-project", "phase": "summary", "event": "test_complete", "phases_completed": 5, "agents_spawned": 8, "files_written": 12, "errors": 0, "timestamp": "<now>"}`
