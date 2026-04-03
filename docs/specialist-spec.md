# Specialist File Specification

Version: 1.0.0

The formal specification for specialist definition files in `specialists/`. This is the machine-referenceable contract — for architecture context and usage guidance, see `specialist-guide.md`.

## File Location

`specialists/<domain>.md` where `<domain>` is lowercase kebab-case (e.g., `security`, `platform-ios-apple`).

## Required Sections

Sections MUST appear in this order. No other `##` headings may appear between them except where noted.

### 1. Title

```markdown
# <Name> Specialist
```

- Exactly one `#` heading
- MUST end with ` Specialist`
- `<Name>` is the human-readable specialist name (title case, spaces allowed)
- Examples: `# Security Specialist`, `# iOS / Apple Platforms Specialist`

### 2. Role

```markdown
## Role
<prose>
```

- 1-3 sentences defining the specialist's domain scope
- Plain prose, no markdown lists or sub-headings
- Comma-separated keywords are the conventional style
- MUST be non-empty

### 3. Persona

```markdown
## Persona
<prose or placeholder>
```

- Describes how the specialist communicates and prioritizes
- Placeholder `(coming)` is acceptable

### 4. Cookbook Sources

```markdown
## Cookbook Sources
- `<path>`
- `<path>` (<N> files)
```

- Markdown list of backtick-wrapped paths relative to the cookbook repo root
- Directory references MAY include a file count: `(N files)`
- Sub-headings (`### Guidelines`, `### Principles`, etc.) are allowed for organization
- Each path MUST be either a file or directory that exists in the cookbook repo
- Every path listed here MUST have corresponding specialty-team(s)

### 5. Specialty Teams

```markdown
## Specialty Teams

### <team-name>
- **Artifact**: `<path>`
- **Worker focus**: <text>
- **Verify**: <text>
```

- One or more team entries
- See **Specialty Team Entry** below for field specifications

### 6. Exploratory Prompts (optional)

```markdown
## Exploratory Prompts

1. <question>?
2. <question>?
```

- Numbered list of domain-specific questions
- Each prompt SHOULD end with `?`
- Used for interview mode's exploratory phase

## Optional Sections

These MAY appear between Specialty Teams and Exploratory Prompts:

### Conventions

```markdown
## Conventions
<prose>
```

- Domain-specific naming, formatting, or structural rules
- Free-form prose

## Specialty Team Entry

Each team is a `###` heading inside `## Specialty Teams` with exactly 3 fields.

### Team Name

- `### <name>` where `<name>` is lowercase kebab-case
- Pattern: `[a-z][a-z0-9]*(-[a-z0-9]+)*`
- Derived from the artifact filename (e.g., `authentication` from `authentication.md`)

### Fields

Fields MUST appear in this order, one per line:

| Field | Format | Description |
|-------|--------|-------------|
| Artifact | `- **Artifact**: \`<path>\`` | Path to one cookbook artifact, relative to cookbook root, wrapped in backticks |
| Worker focus | `- **Worker focus**: <text>` | What this team cares about (mode-independent). Single line. |
| Verify | `- **Verify**: <text>` | Concrete acceptance criteria for the verifier. Single line. |

### Field Constraints

- **Artifact path**: MUST be backtick-wrapped. MUST be a single file path (not a directory).
- **Worker focus**: MUST be a single line. MUST NOT contain unescaped double quotes (breaks JSON output from `run-specialty-teams.sh`).
- **Verify**: Same constraints as Worker focus.
- **Line prefix**: Each field line MUST start with `- **` (no leading spaces).

## Validation Rules

### Structure (S-series)

| ID | Rule | Severity |
|----|------|----------|
| S01 | Title matches `# <Name> Specialist` pattern | FAIL |
| S02 | All required sections present in correct order: Role, Persona, Cookbook Sources, Specialty Teams | FAIL |
| S03 | Every specialty-team has all 3 required fields (Artifact, Worker focus, Verify) | FAIL |
| S04 | Team names are lowercase kebab-case | FAIL |
| S05 | Artifact paths are backtick-wrapped | FAIL |
| S06 | Worker focus and Verify are single-line (no continuation on next line) | WARN |
| S07 | No unescaped double quotes in Worker focus or Verify fields | FAIL |

### Content (C-series)

| ID | Rule | Severity |
|----|------|----------|
| C01 | Every file path in Cookbook Sources has a corresponding specialty-team | FAIL |
| C02 | Every specialty-team artifact appears in Cookbook Sources (or its parent directory) | WARN |
| C03 | Artifact paths resolve to real files in the cookbook repo | WARN |
| C04 | At least one specialty-team defined | FAIL |
| C05 | Exploratory Prompts (if present) are numbered and end with `?` | WARN |
| C06 | Role section is non-empty | FAIL |

## Parser Contract

`scripts/run-specialty-teams.sh` parses specialist files and outputs a JSON array. It relies on:

- `## Specialty Teams` heading to enter parsing mode
- `### <name>` headings to delimit teams
- `- **Artifact**:`, `- **Worker focus**:`, `- **Verify**:` prefixes to extract fields
- Backtick delimiters around artifact paths
- Next `## ` heading or EOF to exit parsing mode

Any deviation from these patterns causes silent data loss in the JSON output.

## Example

```markdown
# Example Specialist

## Role
Example domain coverage description.

## Persona
(coming)

## Cookbook Sources
- `guidelines/example/`

## Specialty Teams

### widget-design
- **Artifact**: `guidelines/example/widget-design.md`
- **Worker focus**: Widget sizing, responsive layout, platform-appropriate rendering
- **Verify**: Widgets render correctly at all supported sizes; no fixed pixel dimensions; platform controls used

### widget-accessibility
- **Artifact**: `guidelines/example/widget-accessibility.md`
- **Worker focus**: Screen reader labels, keyboard navigation, minimum touch targets
- **Verify**: All interactive elements have accessibility labels; touch targets meet platform minimums (44pt iOS, 48dp Android)

## Exploratory Prompts

1. If a user couldn't see your widgets, could they still use them?
2. What happens to your widget layout on the smallest supported screen?
```
