---
id: 7a3e1f2c-8b4d-4e6a-9c5f-1d2e3f4a5b6c
title: "Conventions"
domain: agentic-cookbook://introduction/conventions
type: reference
version: 1.4.0
status: accepted
language: en
created: 2026-03-27
modified: 2026-04-06
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "All conventions for file format, naming, cross-referencing, and authoring in this repository."
platforms: []
tags:
  - conventions
  - naming
  - frontmatter
  - format
depends-on: []
related: []
references:
  - https://datatracker.ietf.org/doc/html/rfc8141
  - https://go.dev/doc/modules/layout
  - https://docs.oracle.com/javase/tutorial/java/package/namingpkgs.html
  - https://maven.apache.org/guides/mini/guide-naming-conventions.html
  - https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/understanding_utis/understand_utis_conc/understand_utis_conc.html
  - https://semver.org
  - https://spdx.org/licenses/
  - https://www.dublincore.org/specifications/dublin-core/dces/
  - https://schema.org/CreativeWork
---

# Conventions

All conventions for file format, naming, cross-referencing, and authoring in this repository.

## File Format

Every markdown file starts with a YAML frontmatter block containing these fields:

```yaml
---
id: <uuid>
title: <human readable title>
domain: <path-derived identifier>
type: principle | guideline | ingredient | recipe | cookbook | workflow | reference
version: 1.0.0
status: wip | draft | review | accepted | deprecated
language: en
created: YYYY-MM-DD
modified: YYYY-MM-DD
author: <name>
copyright: YYYY Mike Fullerton
license: MIT
summary: <one-line description for search and tooltips>
platforms: []
tags: []
depends-on: []
related: []
references: []
approved-by: ""
approved-date: ""
---
```

### Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | UUID, globally unique, stable across renames |
| `title` | Yes | Human-readable title |
| `domain` | Yes | Path-derived identifier (see Naming below). Validated against actual path at build time. |
| `type` | Yes | One of: `principle`, `guideline`, `ingredient`, `recipe`, `cookbook`, `workflow`, `reference`, `compliance` |
| `version` | Yes | Semver. Major for breaking changes, minor for new content, patch for clarifications. Immutable once on main — changes require a version bump. |
| `status` | Yes | `wip` (actively being built — LLM consumers skip this content), `draft` (complete first pass, awaiting review), `review` (ready for feedback), `accepted` (stable), `deprecated` (superseded) |
| `language` | Yes | BCP 47 language tag. Default: `en` |
| `created` | Yes | ISO 8601 date. Immutable after creation. |
| `modified` | Yes | ISO 8601 date. Updated on every change. |
| `author` | Yes | Primary author name |
| `copyright` | Yes | `YYYY Mike Fullerton` |
| `license` | Yes | SPDX license identifier. Default: `MIT` |
| `summary` | Yes | One-line description (~120 chars). Used in search results, tooltips, and index pages. |
| `platforms` | Yes | List of platforms this content applies to. Empty list `[]` if universal. Values: `swift`, `kotlin`, `typescript`, `csharp`, `python`, `windows`, `macos`, `ios`, `web` |
| `tags` | Yes | 1-5 lowercase tags for discoverability. Empty list `[]` if none. |
| `depends-on` | Yes | Domain identifiers of content that should be read first. Empty list `[]` if none. |
| `related` | Yes | Domain identifiers of related content ("see also"). Empty list `[]` if none. |
| `references` | Yes | External URLs referenced by this content. Empty list `[]` if none. |
| `ingredients` | Recipe only | List of ingredient domain identifiers this recipe composes. Required when `type` is `recipe`. |
| `approved-by` | Yes | Approval stamp from `/approve-artifact`. Format: `"approve-artifact <version>"`. Empty string `""` if not yet approved. |
| `approved-date` | Yes | ISO 8601 date when the artifact was last approved. Empty string `""` if not yet approved. |

### Change History

Every file ends with a Change History section:

```markdown
## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | Name | Initial creation |
```

Each row corresponds to a version bump. Once a version is on main, it is immutable.

### Compliance Section

Recipes and guidelines include a `## Compliance` section listing the compliance checks that were evaluated and their results. Compliance checks are defined in `cookbook/compliance/` — see `cookbook/compliance/INDEX.md` for the full list.

**Format:**

```markdown
## Compliance

| Check | Status | Category |
|-------|--------|----------|
| [secure-log-output](agentic-cookbook://compliance/security#secure-log-output) | passed | Security |
| [keyboard-navigable](agentic-cookbook://compliance/accessibility#keyboard-navigable) | passed | Accessibility |
```

**Rules:**
- Only list checks that are applicable — omit entire categories that don't apply
- Status values: `passed`, `failed`, `partial`
- Each check name is a link to its definition in the compliance category file
- The Compliance section appears after Design Decisions and before Change History

**Architecture:** Recipes → compliance checks → guidelines → external standards. Each layer is one level of indirection. Compliance checks reference guidelines; guidelines reference external standards (OWASP, WCAG, etc.).

### Standards Alignment

This format is aligned with:
- **Dublin Core** (ISO 15836): `id` → `dc:identifier`, `title` → `dc:title`, `author` → `dc:creator`, `summary` → `dc:description`, `tags` → `dc:subject`
- **Schema.org CreativeWork**: `version`, `dateCreated`, `dateModified`, `creativeWorkStatus`, `keywords`
- **SPDX** (ISO/IEC 5962): `license` field uses SPDX identifiers
- **SemVer 2.0.0**: `version` field

## Naming

### URL-Based Domain Identifiers

Every document has a globally unique URL-based domain identifier. The scheme identifies the source, the path maps directly to the filesystem, and fragments address sections within a document.

**Format**: `<scheme>://<path>#<fragment>`

| Component | Description |
|-----------|-------------|
| **Scheme** | Identifies the source repo (`agentic-cookbook`, `temporal`, `my-company`) |
| **Path** | Filesystem path from content root, without `.md` extension |
| **Fragment** | Section or item within the document, `/`-delimited (optional) |

**Derivation rules:**
1. Scheme is the repo/project name (kebab-case)
2. Path starts from the content root directory (e.g., `ingredients/ui/panels/file-tree-browser`)
3. Drop the `.md` extension
4. Fragment addresses sections within the document

| File path | Domain |
|-----------|--------|
| `cookbook/principles/simplicity.md` | `agentic-cookbook://principles/simplicity` |
| `cookbook/guidelines/testing/test-pyramid.md` | `agentic-cookbook://guidelines/testing/test-pyramid` |
| `cookbook/ingredients/ui/components/empty-state.md` | `agentic-cookbook://ingredients/ui/components/empty-state` |
| `cookbook/recipes/ui/windows/settings-window.md` | `agentic-cookbook://recipes/ui/windows/settings-window` |

**Cross-repo references:**

```
agentic-cookbook://ingredients/ui/components/empty-state
temporal://recipes/ui/server-config-window
```

### Fragments — Addressing Sections Within a Document

Use `#` fragments to reference sections and items within a document:

```
agentic-cookbook://recipes/ui/windows/workspace-window#requirements/ordered-list
agentic-cookbook://recipes/ui/windows/workspace-window#platforms/swift
agentic-cookbook://recipes/ui/windows/workspace-window#states/error
```

Within the same document, use the short form:

```
#requirements/ordered-list
#states/error
```

| Section | Fragment pattern |
|---------|-----------------|
| Overview | `#overview` |
| Requirements | `#requirements/<name>` |
| Appearance | `#appearance/<property>` |
| States | `#states/<state-name>` |
| Platforms | `#platforms/<platform>` |
| Accessibility | `#accessibility/<item>` |
| Test vectors | `#test-vectors/<id>` |
| Configuration | `#configuration/<option>` |
| Edge cases | `#edge-cases/<name>` |
| Logging | `#logging/<event>` |
| Localization | `#localization/<key>` |
| Feature flags | `#feature-flags/<flag>` |
| Analytics | `#analytics/<event>` |
| Privacy | `#privacy` |
| Ingredients | `#ingredients/<name>` |
| Integration requirements | `#integration-requirements/<name>` |
| Layout | `#layout` |
| Shared state | `#shared-state/<state>` |
| Integration test vectors | `#integration-test-vectors/<id>` |
| Design decisions | `#design-decisions/<name>` |
| Change history | `#change-history/<version>` |

### Named Requirements

Requirements use descriptive kebab-case names, not sequential numbers. Format: `**<name>**: <description>`

```markdown
- **ordered-list**: The control MUST maintain an ordered list of messages.
- **scroll-to-bottom**: The control MUST auto-scroll to the newest message.
```

Constraints:
- Names MUST be unique within the requirements section of a file
- Names MUST be kebab-case (URL-safe)
- Names SHOULD be descriptive of the requirement's subject

**Cross-referencing requirements:**

Between documents: `See agentic-cookbook://ingredients/ui/components/ai-chat-control#requirements/ordered-list`

Within the same document: `Validates: #requirements/ordered-list`

### File Naming Rules

- **kebab-case** for all filenames: `file-tree-browser.md`
- **Descriptive names**: the filename describes what the thing **is**, not what it does
- **No numeric prefixes**: the path provides the hierarchy
- **`.md` extension** for all content files
- **`index.md`** for landing pages (lowercase)

### Cookbook Directory Naming

Cookbook directories MUST use the suffix `-cookbook`. For a source repository named `my-app`, the cookbook directory is `my-app-cookbook/`. This distinguishes cookbooks from other directories and makes the project type immediately recognizable.

```
my-app-cookbook/
├── cookbook.json
├── app/
│   └── ...specs...
└── context/
    └── ...research...
```

### Cross-Referencing

Use the full URL for cross-document references: `See agentic-cookbook://guidelines/testing/test-pyramid`

Use short-form fragments for within-document references: `See #requirements/ordered-list`

In frontmatter `depends-on` and `related` fields, use full URLs:

```yaml
depends-on:
  - agentic-cookbook://ingredients/ui/components/empty-state
  - agentic-cookbook://ingredients/ui/components/status-bar
related:
  - agentic-cookbook://guidelines/testing/test-pyramid
```

## RFC 2119 Keywords

Use RFC 2119 keywords for all behavioral requirements:

- **MUST** / **MUST NOT**: Absolute requirements.
- **SHOULD** / **SHOULD NOT**: Recommendations.
- **MAY**: Optional behavior.

## Template Variables

Content uses `{{placeholder}}` tokens for consumer-specific values. Never hardcode app-specific values.

| Variable | Example | Purpose |
|----------|---------|---------|
| `{{app_name}}` | `MyApp` | Application name (PascalCase) |
| `{{app_name_lower}}` | `myapp` | Application name (lowercase) |
| `{{org_package}}` | `company.myapp` | Package/bundle identifier root |
| `{{bundle_id}}` | `com.company.app` | Bundle/package identifier |
| `{{app_scheme}}` | `myapp` | URL scheme for deep links |
| `{{app_prefix}}` | `myapp` | Prefix for feature flag keys |
| `{{api_base_url}}` | `https://api.example.com` | Production API URL |
| `{{db_name}}` | `myapp.db` | Local database filename |

## Design Decisions

Any choice that affects behavior or structure must be explicitly noted and approved. Record approved decisions in the relevant file's **Design Decisions** section so all implementations stay consistent.

Format:
```markdown
**Decision**: Description of the choice.
**Rationale**: Why this choice was made.
**Approved**: yes | pending
```

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial consolidation from 5 separate convention files |
| 1.2.0 | 2026-04-04 | Mike Fullerton | Add approved-by and approved-date frontmatter fields |
| 1.4.0 | 2026-04-06 | Mike Fullerton | Rename concoction to cookbook; add cookbook type to enum |
| 1.3.0 | 2026-04-05 | Mike Fullerton | Add ingredient, recipe (composition), and concoction types; rename cookbook-project to concoction |
| 1.1.0 | 2026-04-02 | Mike Fullerton | Add cookbook project directory naming convention (-cookbook-project suffix) |
