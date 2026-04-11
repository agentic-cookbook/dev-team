---
id: a7f3c1d2-8e4b-4f9a-b5c6-2d1e8f3a4b7c
title: "Infrastructure: Global Plugin Cleanup — Move Project-Specific Plugins to Per-Project"
domain: agentic-cookbook://appendix/decisions/global-plugin-cleanup
type: reference
version: 1.0.0
status: accepted
language: en
created: 2026-03-29
modified: 2026-03-29
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Removed 19 plugins from global Claude Code config. Hook-heavy plugins were firing on every tool call across all projects. Project-specific plugins (LSPs, design, testing) add overhead in irrelevant projects."
platforms:
  - all
tags:
  - infrastructure
  - plugins
  - performance
depends-on: []
related: []
references: []
---

# Global Plugin Cleanup

## Decision

Reduce globally enabled Claude Code plugins from 32 to 13. Removed plugins fall into two categories:

1. **Hook-heavy plugins** (removed for performance) — firing hooks on every tool call, prompt, or file write across all projects, even where irrelevant
2. **Project-specific plugins** (removed for scope) — only useful in certain project types, adding overhead everywhere else

## Context

Analysis on 2026-03-29 found that 8 plugins registered hooks that fire continuously:

| Plugin | Hooks | Impact |
|--------|-------|--------|
| **vercel** | 13 hooks (PreToolUse, PostToolUse, UserPromptSubmit, SubagentStart, SubagentStop, SessionStart x3, SessionEnd) | Telemetry, skill injection, validation on every action |
| **hookify** | 4 hooks (PreToolUse, PostToolUse, UserPromptSubmit, Stop) | Fires on every tool call and prompt |
| **semgrep** | 3 hooks (PostToolUse on Write/Edit, UserPromptSubmit, SessionStart) | Failing every invocation — no SEMGREP_APP_TOKEN configured |
| **security-guidance** | 1 hook (PreToolUse on Edit/Write) | Python script on every file write |
| **railway** | 1 hook (PreToolUse on Bash) | Fires on every Bash command |
| **explanatory-output-style** | 1 hook (SessionStart) | Injects instructions at start |
| **learning-output-style** | 1 hook (SessionStart) | Injects instructions at start |

Additionally, project-specific plugins (LSPs, design tools, testing) were installed globally but only relevant to specific project types:

- **LSP plugins** (swift-lsp, typescript-lsp, kotlin-lsp, csharp-lsp) — only useful in projects using those languages
- **Design plugins** (frontend-design, figma, playground, accesslint) — only useful for web/UI projects
- **Dev tool plugins** (plugin-dev, agent-sdk-dev, skill-creator) — only useful when authoring Claude Code extensions
- **Testing** (playwright) — only useful for web projects
- **Communication** (telegram) — very niche

## Removed (19 plugins)

### Phase 1: Hook-heavy (6 removed)
- `security-guidance` — PreToolUse on every Write/Edit
- `hookify` — 4 hooks on everything
- `vercel` — 13 hooks + telemetry
- `railway` — PreToolUse on every Bash
- `explanatory-output-style` — SessionStart injection
- `learning-output-style` — SessionStart injection

### Phase 2: Project-specific (13 removed)
- `typescript-lsp`, `swift-lsp`, `kotlin-lsp`, `csharp-lsp` — LSPs for specific languages
- `frontend-design`, `figma`, `playground`, `accesslint` — design/frontend tools
- `plugin-dev`, `agent-sdk-dev`, `skill-creator` — extension authoring
- `playwright` — browser testing
- `telegram` — messaging

### Phase 3: Redundant third-party (1 removed)
- `coderabbit` — third-party AI code review with 40+ static analyzers. Overlaps with Anthropic's own code-review and pr-review-toolkit plugins; requires paid account for premium features.

## Remaining (12 plugins)

| Category | Plugins |
|----------|---------|
| Code Review (3) | code-review, code-simplifier, pr-review-toolkit |
| Workflow (5) | superpowers, feature-dev, commit-commands, claude-code-setup, claude-md-management |
| Source Control (1) | github |
| Search (1) | context7 |
| Docs (2) | document-skills, claude-api |

Only `superpowers` has a hook (SessionStart, fires once).

## How to re-enable per project

Install any removed plugin in a specific project when needed:

```bash
# In the project directory:
/plugin install typescript-lsp@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install playwright@claude-plugins-official
# etc.
```

Or add to the project's `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "typescript-lsp@claude-plugins-official": true
  }
}
```

## Change History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-03-29 | Initial decision — removed 19 plugins from global config |
| 1.1.0 | 2026-03-29 | Removed coderabbit — redundant with Anthropic's own review plugins |
