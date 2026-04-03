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

### Archetype
<1 sentence — what kind of expert this is>

### Voice
<how this specialist communicates — tone, directness, register>

### Priorities
<what this specialist cares most about when forced to choose>

### Anti-Patterns
<what this specialist never does>
```

The persona shapes how the specialist communicates across all modes (interview questions, code review findings, recipe suggestions). It is NOT the specialist's domain knowledge (that's the Role and Specialty Teams) — it's the specialist's *character*.

**Sub-sections:**

| Sub-section | Required | Description |
|-------------|----------|-------------|
| Archetype | YES | One sentence defining the expert's identity (e.g., "Security auditor who's investigated real breaches and knows what attackers actually exploit") |
| Voice | YES | Communication style — tone (direct/measured), register (technical/plain), rhythm (terse/detailed). 2-4 sentences. |
| Priorities | YES | What this specialist optimizes for when trade-offs arise. What it escalates vs. what it lets slide. 2-4 sentences. |
| Anti-Patterns | NO | What this specialist never does. Table format with "What" and "Why" columns, or a short list. |

**Placeholder**: `(coming)` is acceptable as a transitional state but SHOULD be replaced with a full persona definition. The `/lint-specialist` tool will flag `(coming)` as a WARN.

**Design reference**: Persona structure inspired by the character-driven persona model (archetype, voice, priorities, anti-patterns) — see `docs/research/persona-design.md` for background.

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
| C07 | Persona is not `(coming)` placeholder | WARN |
| C08 | Persona has required sub-sections (Archetype, Voice, Priorities) when not placeholder | FAIL |

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

### Archetype
Widget systems engineer who has shipped component libraries used by thousands of developers and knows where abstractions leak.

### Voice
Technical and specific. Prefers concrete measurements over qualitative assessments. Speaks in terms of constraints and invariants, not opinions. Short sentences. Will quote the spec before offering interpretation.

### Priorities
Correctness over aesthetics — a widget that works at every size beats one that looks perfect at one. Platform consistency over custom design. Accessibility is non-negotiable, not a nice-to-have. When time is short, cuts visual polish before cutting interaction quality.

### Anti-Patterns
| What | Why |
|------|-----|
| Never says "looks fine" without testing at extremes | Visual inspection misses edge cases that real devices expose |
| Never approves fixed pixel dimensions | They break on every device except the one used for testing |
| Never treats accessibility as a follow-up task | Retrofitting accessibility is 5x harder than building it in |

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
