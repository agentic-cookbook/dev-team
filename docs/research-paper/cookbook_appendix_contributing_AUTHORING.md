---
id: 5d312abc-9bf5-4766-9e85-60fdf1a0d7a8
title: "Authoring Guide"
domain: agentic-cookbook://appendix/contributing/AUTHORING
type: reference
version: 1.0.0
status: accepted
language: en
created: 2026-03-27
modified: 2026-03-27
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "How to create, modify, and contribute specs to the Litterbox repo."
platforms: 
  - ios
  - kotlin
  - macos
  - swift
  - typescript
  - web
  - windows
tags: 
  - authoring
depends-on: []
related: 
  - recipe.app.lifecycle
  - recipe.infrastructure.logging
  - recipe.ui.component.empty-state
  - recipe.ui.panel.file-tree-browser
  - recipe.ui.panel.inspector-panel
  - recipe.ui.window.project-window
references: []
---

# Authoring Guide

How to create, modify, and contribute specs to the Litterbox repo.

This guide is for Claude Code sessions and external contributors working in a consuming project that references `../litterbox/`. Follow these rules exactly — a spec that doesn't meet these requirements will not be merged.

## Quick Start

1. Read this guide and `ui/_template.md`
2. Create a worktree: `git worktree add ../litterbox-wt/<branch> -b spec/<name>`
3. Copy `ui/_template.md` to `ui/<name>.md` (component) or `ui/Recipes/<name>.md` (recipe)
4. Fill in every section — omit only sections that genuinely do not apply
5. Update `ui/INDEX.md` and the CLAUDE.md numbering table
6. Commit, push, open a PR

## Where Specs Live

| Type | Directory | Description |
|------|-----------|-------------|
| Component | `ui/` | Self-contained, reusable UI building blocks (buttons, badges, status bars) |
| Recipe | `ui/Recipes/` | Composite flows that combine components into a feature (windows, panels, lifecycle patterns) |
| Workflow | `workflow/` | Development process recipes for Claude Code AI sessions |
| Template | `ui/_template.md` | Starting point for new UI specs — copy, don't edit |
| Workflow Template | `workflow/_template.md` | Starting point for new workflow specs — copy, don't edit |

**Components** are leaf nodes — they have no dependencies on other specs in this repo (though they may reference platform controls). **Recipes** compose components and may depend on other specs. **Workflows** describe development processes, not software artifacts — they use `WF-` numbering and a workflow-specific template with Inputs, Phases, and Guideline Cross-Reference sections instead of Appearance and States.

## File Naming

- Use **kebab-case**: `collapsible-pane-header.md`, `file-tree-browser.md`
- Name should describe what the thing **is**, not what it does: `status-bar.md` not `show-progress.md`
- Recipes that describe a window: `<name>-window.md`
- Recipes that describe a panel/pane: `<name>-panel.md` or `<name>-pane.md`

## Frontmatter

Every spec starts with a YAML frontmatter block. All fields are required unless noted.

```yaml
---
version: 1.0.0
status: draft
created: 2026-03-26
last-updated: 2026-03-26
author: claude-code
copyright: 2026 Mike Fullerton / Temporal
platforms: [macOS, iOS, watchOS, tvOS, visionOS, Android, Web]
tags: [category, feature-area]
dependencies:
  - ui/other-spec.md@1.0.0
---
```

### Field rules

- **version**: Semver. Start at `1.0.0` for new specs. Bump patch for clarifications, minor for new requirements, major for breaking changes.
- **status**: New specs start as `draft`. Set to `review` when opening the PR. Only the repo owner sets `accepted`.
- **created**: The date you create the spec. Never change this after initial creation.
- **last-updated**: Update every time the spec changes.
- **author**: Use `claude-code` for AI-authored specs, or your name.
- **copyright**: Always `YYYY Mike Fullerton / Temporal` with the current year.
- **platforms**: Use Apple sub-platforms, not the generic "Apple": `[macOS, iOS, watchOS, tvOS, visionOS, Android, Web]`. List only platforms this spec targets.
- **tags**: 2-5 lowercase tags for discoverability.
- **dependencies**: Relative paths within this repo with version pins: `ui/color-profile.md@1.0.0`. Omit the field entirely (don't leave it empty) if there are no dependencies.

## Required Sections

Every spec MUST include these sections in this order. Omit a section only if it genuinely does not apply (e.g., a non-visual infrastructure pattern may omit Appearance and States).

### 1. Overview

One paragraph explaining what this component/recipe is and when to use it. Include scope boundaries — what is and isn't covered.

### 2. Terminology (if needed)

A table defining domain-specific terms used in this spec.

### 3. Behavioral Requirements

The heart of the spec. Every behavioral statement uses RFC 2119 keywords:

- **MUST** / **MUST NOT**: Absolute requirement. Every MUST needs at least one test vector.
- **SHOULD** / **SHOULD NOT**: Recommended but not mandatory.
- **MAY**: Optional behavior.

Number requirements sequentially: `REQ-001`, `REQ-002`, `REQ-003`. Never reuse a number, even if a requirement is removed — leave gaps.

```markdown
- **REQ-001**: The component MUST display a loading indicator while data is being fetched.
- **REQ-002**: The component SHOULD animate the transition between states.
- **REQ-003**: The component MAY support a custom icon override.
```

### 4. Appearance

Concrete visual values — not vague descriptions. Specify:
- Corner radius, padding, font weight/size, colors, borders, shadows
- Min/max size constraints
- Spacing between elements (use exact point values)

Bad: "The button should look prominent."
Good: "Background: system accent color. Corner radius: 8pt. Padding: 12pt vertical, 20pt horizontal. Font: Body weight semibold."

### 5. States

A table of visual states with what changes in each:

```markdown
| State | Appearance change |
|-------|------------------|
| Default | — |
| Pressed | Background opacity 0.7 |
| Disabled | Opacity 0.4, interaction disabled |
| Focused | 2pt focus ring, accent color |
| Loading | Replace content with indeterminate spinner |
```

### 6. Accessibility

Required for every visual component:
- Role/trait (button, heading, text field, etc.)
- Label requirements
- State change announcements
- Minimum tap target: 44x44pt (iOS), 48x48dp (Android)
- Keyboard navigation order
- Contrast requirements (WCAG AA: 4.5:1 text, 3:1 large text)

### 7. Conformance Test Vectors

Input/output pairs linked to REQ-NNN numbers. Every MUST requirement needs at least one test vector.

```markdown
| ID | Requirements | Input | Expected |
|----|-------------|-------|----------|
| component-001 | REQ-001 | Data fetch initiated | Loading indicator visible |
| component-002 | REQ-001 | Data fetch completes | Loading indicator removed, content shown |
```

### 8. Edge Cases

Boundary conditions, error states, unexpected input. Think about:
- Empty/null data
- Extremely long text
- Network failures
- Rapid repeated interactions
- Concurrent state changes

### 9. Deep Linking

URL patterns for each platform. Use `{{placeholder}}` tokens for app-specific values.

### 10. Localization

Table of string keys with English defaults. Every user-visible string must be here — no hardcoded strings.

### 11. Accessibility Options

How the component responds to system accessibility settings:

```markdown
| Option | Behavior |
|--------|----------|
| Reduce Motion | Disable all animations, use instant transitions |
| Increase Contrast | Use high-contrast color variants |
| Bold Text | Respect system bold text setting |
```

### 12. Feature Flags

The flag key that gates this feature. Format: `{{app_prefix}}.feature_name`.

### 13. Analytics

Events fired by this component. Include event name, properties, and trigger condition.

### 14. Privacy

What data is collected, where it's stored, whether it leaves the device, and retention policy. If none, state "No data collected."

### 15. Logging

Exact log messages for every significant event. These are used for automated verification (grep the output, don't inspect the UI).

```markdown
Subsystem: `{{bundle_id}}` | Category: `ComponentName`

| Event | Level | Message |
|-------|-------|---------|
| Loaded | debug | `ComponentName: loaded with {count} items` |
| Error | error | `ComponentName: failed to load ({error})` |
```

### 16. Platform Notes

Implementation guidance per platform. Reference native controls and APIs:

- **SwiftUI**: Which views, modifiers, and system controls to use
- **Compose**: Which composables and Material components to use
- **React/Web**: Which HTML elements and CSS patterns to use

### 17. Design Decisions

Document every subjective choice. Each decision should be approved by the repo owner before the spec is accepted. Format:

```markdown
**Decision**: Use sidebar navigation instead of tab bar.
**Rationale**: Sidebar scales to more categories without scrolling.
**Approved**: pending
```

### 18. Changelog

Version history table. Every spec starts with:

```markdown
| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-26 | Initial spec |
```

## Template Variables

Use `{{placeholder}}` tokens for values that vary per consuming app. Never hardcode app-specific values.

| Variable | Example | Purpose |
|----------|---------|---------|
| `{{app_name}}` | `Temporal` | Application name (PascalCase) |
| `{{app_name_lower}}` | `temporal` | Application name (lowercase) |
| `{{org_package}}` | `company.temporal` | Package/bundle identifier root |
| `{{bundle_id}}` | `com.company.app` | Bundle/package identifier |
| `{{app_scheme}}` | `temporal` | URL scheme for deep links |
| `{{app_prefix}}` | `temporal` | Prefix for feature flag keys |
| `{{api_base_url}}` | `https://api.temporal.today` | Production API URL |
| `{{db_name}}` | `temporal.db` | Local database filename |

## Writing Recipes

Recipes follow the same format as components, plus these additional rules:

1. **List dependencies** in frontmatter: every component or recipe this one references must be listed with a version pin.
2. **Describe composition**: explain how the referenced components are arranged — layout hierarchy, navigation flow, data flow between components.
3. **Don't redefine components**: reference the component spec for visual details. The recipe describes how components work together, not what they look like individually.
4. **Include a layout description**: use a text diagram or bullet hierarchy showing the spatial arrangement.

Example layout description:
```
Window
├── Sidebar (NavigationSplitView detail)
│   └── Category list
└── Content panel
    └── Settings form for selected category
```

## Recipe Domain Naming

Recipes use path-derived domain identifiers. The domain is derived from the filesystem path:

1. Start from the `recipes/` directory
2. Replace `/` with `.`
3. Drop the `.md` extension
4. Prepend `recipe.`

Example: `recipes/ui/panel/file-tree-browser.md` → `recipe.ui.panel.file-tree-browser`

| Category | Path prefix | Example domain |
|----------|------------|----------------|
| UI Components | `recipes/ui/component/` | `recipe.ui.component.empty-state` |
| Panels & Panes | `recipes/ui/panel/` | `recipe.ui.panel.inspector-panel` |
| Windows | `recipes/ui/window/` | `recipe.ui.window.project-window` |
| Infrastructure | `recipes/infrastructure/` | `recipe.infrastructure.logging` |
| App-Level | `recipes/app/` | `recipe.app.lifecycle` |

When adding a new recipe, place it in the appropriate category folder (create new subcategories as needed). Update both:
- `recipes/INDEX.md` — add the row to the correct category table
- `CLAUDE.md` — add the row to the recipe domain table

Cross-reference other recipes using the domain: "See `recipe.ui.window.project-window`".

## Contribution Workflow

This repo uses a branch + PR workflow for all non-owner contributions.

### Branch naming

| Change type | Pattern | Example |
|---|---|---|
| New spec | `spec/<kebab-name>` | `spec/toolbar-buttons` |
| Spec revision | `revise/<kebab-name>` | `revise/settings-window` |
| Multi-spec change | `feature/<description>` | `feature/accessibility-audit` |

### Step by step

1. **Create a worktree** (keeps `../litterbox/` on main for consuming projects):
   ```
   git worktree add ../litterbox-wt/<branch-name> -b <branch>
   ```

2. **Write the spec** in the worktree directory. Copy `ui/_template.md` as your starting point.

3. **Update the index**: add your recipe to `recipes/INDEX.md` and the CLAUDE.md recipe domain table.

4. **Set status to `review`** in frontmatter before opening the PR.

5. **Commit and push**:
   ```
   git add -A && git commit -m "Add <name> <component|recipe> spec"
   git push -u origin <branch>
   ```

6. **Open a PR**:
   ```
   gh pr create --title "Add <name> spec" --body "..."
   ```

7. **After merge**, clean up:
   ```
   git worktree remove ../litterbox-wt/<branch-name>
   git -C /Users/mfullerton/projects/litterbox pull
   ```

### PR checklist

Before opening a PR, verify:

- [ ] Copied from `ui/_template.md` (not written from scratch)
- [ ] All 18 sections present (or explicitly noted as N/A)
- [ ] Every MUST requirement has at least one test vector
- [ ] REQ numbers are sequential with no gaps (except for removed requirements)
- [ ] Appearance values are concrete (exact points, colors, weights — no vague descriptions)
- [ ] All user-visible strings are in the Localization table
- [ ] `ui/INDEX.md` updated with new row
- [ ] CLAUDE.md numbering table updated
- [ ] Frontmatter status set to `review`
- [ ] Dependencies listed with version pins
- [ ] No hardcoded app-specific values (use `{{placeholder}}` tokens)
- [ ] Changelog entry added

### Merge strategy

All PRs are squash-merged to main. Commit message conventions:
- New spec: `Add <name> <component|recipe> spec`
- Revision: `Bump <name> to v<X.Y.Z>: <description>`

## Common Mistakes

**Vague appearance values**: "Use a nice blue" — specify the exact color or reference a system color.

**Missing test vectors for MUST requirements**: Every MUST needs a testable input/output pair.

**Hardcoded strings**: All user-facing text goes in the Localization table with string keys.

**Redefining components in recipes**: A recipe should reference `ui/empty-state.md`, not rewrite the empty state spec inline.

**Forgetting INDEX.md**: Every new or modified spec requires an INDEX.md update on the same branch.

**Using "Apple" as a platform**: Use the sub-platforms: `macOS`, `iOS`, `watchOS`, `tvOS`, `visionOS`.

**Empty dependency list**: Omit the `dependencies:` field entirely if there are none. Don't write `dependencies: []`.

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial creation |
