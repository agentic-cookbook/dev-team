# Storage-Provider Unification and Data Model

## Summary

Unify the two separate storage dispatchers (`arbitrator.py`'s markdown backend and `project_storage.py`) into a single `storage-provider` abstraction. Define the complete data model as a flat type catalog for the database specialist to design a schema from.

## Current State

Two separate implementations of the same pattern:
- `arbitrator.py` → `arbitrator/markdown/` (13 resource modules, `session_store.py` shared lib)
- `project_storage.py` → `project-storage/markdown/` (8 resource modules, `project_store.py` shared lib)

Both use identical dispatcher logic: read a `BACKEND` env var, load a module from `<backend>/<resource>.py`, call `main(action, flags)`.

## Target Architecture

```
Arbitrator (participant, persona, communication semantics)
  └── uses storage-provider

Project-Manager (participant, persona, project management)
  └── uses storage-provider

storage-provider.py              Single dispatcher
  storage-provider/
    markdown/                    Markdown backend (current)
      storage_helpers.py         Shared utilities (merge of session_store + project_store)
      session.py
      state.py
      message.py
      gate_option.py
      result.py
      finding.py
      interpretation.py
      artifact.py
      reference.py
      retry.py
      team_result.py
      report.py
      project.py
      milestone.py
      todo.py
      issue.py
      concern.py
      dependency.py
      decision.py
    database/                    Database backend (future)
```

The arbitrator remains its own script but delegates all persistence to the storage-provider. It adds communication semantics (session lifecycle, state machine transitions, message routing) on top.

## Data Model

Every type the storage-provider persists. No normalization, no table design — just types, fields, and relationships. The database specialist reads this to design a schema.

### Pipeline Communication Types

Written by the arbitrator during pipeline execution.

#### Session

The runtime instance of a playbook being executed.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | yes | Unique identifier (sortable: YYYYMMDD-HHMMSS-xxxx) |
| playbook | string | yes | Which playbook is running (interview, generate, etc.) |
| team_lead | string | yes | Team-lead role for this session |
| user | string | yes | User identifier |
| machine | string | yes | Machine identifier |
| creation_date | timestamp | yes | ISO 8601 |

#### Session Path

Files and directories associated with a session.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_id | string | yes | References Session |
| path | string | yes | File or directory path |
| type | string | yes | Path type classification |
| creation_date | timestamp | yes | ISO 8601 |

#### State

A state transition in a session's lifecycle.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Composite: {session_id}:state:{seq} |
| session_id | string | yes | References Session |
| changed_by | string | yes | Who made the transition |
| state | string | yes | State value |
| description | string | no | Reason for transition |
| creation_date | timestamp | yes | ISO 8601 |

#### Message

A communication record between participants.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Composite: {session_id}:message:{seq} |
| session_id | string | yes | References Session |
| type | string | yes | Message type (finding, gate, etc.) |
| changed_by | string | yes | Sender |
| content | string | yes | Message body |
| specialist | string | no | Specialist context |
| category | string | no | Content category |
| severity | string | no | Severity level |
| creation_date | timestamp | yes | ISO 8601 |

#### Gate Option

A choice presented to the user at a decision gate.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Composite: {message_id}:option:{sort_order} |
| message_id | string | yes | References Message |
| option_text | string | yes | Display text for the option |
| is_default | boolean | yes | Whether this is the default choice |
| sort_order | integer | yes | Display ordering |

#### Result

A specialist's overall result for a session.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| result_id | string | yes | Composite: {session_id}:result:{specialist} |
| session_id | string | yes | References Session |
| specialist | string | yes | Specialist name |
| creation_date | timestamp | yes | ISO 8601 |

#### Finding

A specific finding produced by a specialist.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| finding_id | string | yes | Composite: {session_id}:finding:{specialist}:{seq} |
| result_id | string | yes | References Result |
| session_id | string | yes | References Session |
| specialist | string | yes | Specialist name |
| category | string | yes | Finding category |
| severity | string | yes | Severity level |
| title | string | yes | Short summary |
| detail | string | yes | Full description |
| linked_artifacts | list of string | yes | References to Artifact IDs (initially empty) |
| creation_date | timestamp | yes | ISO 8601 |

#### Interpretation

A specialist persona's interpretation of a finding.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| interpretation_id | string | yes | Composite: {session_id}:interpretation:{specialist}:{finding_seq} |
| finding_id | string | yes | References Finding |
| session_id | string | yes | References Session |
| specialist | string | yes | Specialist name |
| interpretation | string | yes | The interpretation text |
| creation_date | timestamp | yes | ISO 8601 |

#### Artifact

A file or code artifact referenced during the session.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| artifact_id | string | yes | Composite: {session_id}:artifact:{seq} |
| session_id | string | yes | References Session |
| artifact | string | yes | Artifact content or path |
| message | string | no | Associated message |
| description | string | no | Human description |
| linked_states | list of string | yes | References to State IDs (initially empty) |
| creation_date | timestamp | yes | ISO 8601 |

#### Reference

A cookbook reference cited by a specialist result.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| reference_id | string | yes | Composite: {result_id}:reference:{seq} |
| result_id | string | yes | References Result |
| path | string | yes | Path to referenced resource |
| type | string | yes | Reference type (guideline, principle, compliance) |
| creation_date | timestamp | yes | ISO 8601 |

#### Retry

A record of a retry attempt after a failure.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| retry_id | string | yes | Composite: {session_id}:retry:{seq} |
| session_id | string | yes | References Session |
| session_state_id | string | yes | References State that triggered the retry |
| reason | string | yes | Why the retry was needed |
| creation_date | timestamp | yes | ISO 8601 |

#### Team Result

The result of a single specialty-team's worker-verifier loop.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| team_result_id | string | yes | Composite: {session_id}:team-result:{specialist}:{team} |
| session_id | string | yes | References Session |
| result_id | string | yes | References Result |
| specialist | string | yes | Specialist name |
| team_name | string | yes | Specialty-team name |
| status | string | yes | running, passed, failed, escalated |
| iteration | integer | yes | Current retry iteration (starts at 0) |
| verifier_feedback | string | yes | Latest verifier feedback (empty if not yet verified) |
| consulting_annotations | list of object | yes | Consulting-team verdicts (initially empty) |
| creation_date | timestamp | yes | ISO 8601 |
| modification_date | timestamp | yes | ISO 8601 |

### Project Management Types

Written by the project-manager specialist.

#### Project

The project manifest — metadata and linked cookbook projects.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | Project name |
| description | string | yes | Project description |
| cookbook_projects | list of string | yes | Linked cookbook project paths (initially empty) |
| created | date | yes | ISO 8601 date |
| modified | date | yes | ISO 8601 date |

#### Milestone

A schedule target with a target date.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Generated ID (milestone-NNNN) |
| name | string | yes | Milestone name |
| status | string | yes | Status value |
| target_date | date | no | Target completion date |
| dependencies | string | no | Dependency references |
| description | string | yes | Body text |
| created | date | yes | ISO 8601 date |
| modified | date | yes | ISO 8601 date |

#### Todo

A task with assignment and priority.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Generated ID (todo-NNNN) |
| title | string | yes | Task title |
| status | string | yes | Status value |
| priority | string | yes | Priority level |
| assignee | string | no | Who is assigned |
| milestone | string | no | References Milestone ID |
| blocked_by | string | no | References blocking item(s) |
| description | string | yes | Body text |
| created | date | yes | ISO 8601 date |
| modified | date | yes | ISO 8601 date |

#### Issue

A problem, blocker, or risk.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Generated ID (issue-NNNN) |
| title | string | yes | Issue title |
| status | string | yes | Status value |
| severity | string | yes | Severity level |
| source | string | no | Where the issue was found |
| related_findings | string | no | References to Finding IDs |
| description | string | yes | Body text |
| created | date | yes | ISO 8601 date |
| modified | date | yes | ISO 8601 date |

#### Concern

An item needing attention, raised by a participant.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Generated ID (concern-NNNN) |
| title | string | yes | Concern title |
| status | string | yes | Status value |
| raised_by | string | yes | Who raised it |
| related_to | string | no | References related item |
| description | string | yes | Body text |
| created | date | yes | ISO 8601 date |
| modified | date | yes | ISO 8601 date |

#### Dependency

An internal or external dependency.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Generated ID (dependency-NNNN) |
| name | string | yes | Dependency name |
| status | string | yes | Status value |
| type | string | yes | Dependency type (internal, external) |
| description | string | yes | Body text |
| created | date | yes | ISO 8601 date |
| modified | date | yes | ISO 8601 date |

#### Decision

A choice made with rationale.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | yes | Generated ID (decision-NNNN) |
| title | string | yes | Decision title |
| rationale | string | yes | Why this choice was made |
| alternatives | string | no | Other options considered |
| made_by | string | yes | Who decided |
| date | date | yes | When decided |
| description | string | yes | Body text |
| created | date | yes | ISO 8601 date |
| modified | date | yes | ISO 8601 date |

### Relationship Map

```
Session
  ├── State (many, ordered by creation)
  ├── Message (many, ordered by creation)
  │     └── Gate Option (many per message, ordered by sort_order)
  ├── Result (one per specialist)
  │     ├── Finding (many per result)
  │     │     ├── Interpretation (one per finding)
  │     │     └── linked_artifacts → Artifact (many-to-many)
  │     ├── Reference (many per result)
  │     └── Team Result (one per specialty-team)
  │           └── consulting_annotations (embedded list)
  ├── Retry (many, references State)
  ├── Artifact (many, references State via linked_states)
  └── Session Path (many)

Project
  ├── Milestone (many)
  ├── Todo (many, optionally references Milestone, optionally blocked by other items)
  ├── Issue (many, optionally references Finding)
  ├── Concern (many, optionally references other items)
  ├── Dependency (many)
  └── Decision (many)
```

### Cross-Domain Links

- Issue.related_findings → Finding.finding_id (project management references pipeline findings)
- This is the only cross-domain relationship. All other references are within their domain.

## Migration Path

1. Create `storage-provider.py` as the single dispatcher
2. Merge `session_store.py` and `project_store.py` into `storage_helpers.py`
3. Move all resource modules into `storage-provider/markdown/`
4. Update `arbitrator.py` to call `storage-provider.py` instead of loading backends directly
5. Update `project_storage.py` to be a thin alias to `storage-provider.py` (for backwards compat during transition)
6. Update all tests to use the new paths
7. Remove `project_storage.py` alias and old directories once all callers are migrated

## Constraints

- The storage-provider is a dumb CRUD tool. No business logic, no validation beyond "required field missing."
- The arbitrator adds communication semantics on top. It will grow — state machine enforcement, message routing rules, etc.
- The markdown backend remains the default. A database backend is planned but not part of this spec.
- The data model here is the input for the database specialist. It defines WHAT is stored, not HOW.
