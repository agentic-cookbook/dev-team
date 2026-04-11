# Claude Code Rule Optimization

**Date:** 2026-03-29
**Context:** Research into how Claude Code rule files impact context window usage, with guidelines for writing context-efficient rules. Applies to any project using `.claude/rules/` for behavioral enforcement.

---

## How Rules Consume Context

### Per-Turn Cost Model

Files in `.claude/rules/` are injected into the system prompt on **every turn** of a conversation — every user message, every tool call, every response. This is not a one-time cost at session start. In a 50-turn conversation, a 10KB rule file consumes ~500KB of context.

This per-turn cost stacks with everything else in the system prompt: the user's global `~/.claude/CLAUDE.md`, the project's `CLAUDE.md`, other rules files, plugin-injected context, MCP server instructions, and hook output.

### Per-Session Cost (On-Demand Reads)

Rules can reference external files that Claude reads via tool calls during the conversation. These reads consume context at the point of use but do not repeat on every turn. This makes on-demand reads significantly cheaper than inline content for large reference material.

**Rule of thumb:** If content is needed on every turn, it must be in the rule file (per-turn cost). If content is needed once during a specific workflow step, reference it as an external file read (per-session cost).

---

## Issues Found in Cookbook Rule Architecture

### Issue 1: Per-Turn Bloat

The cookbook installed 3 rule files totaling 381 lines / 17,689 bytes — loaded on every turn regardless of task.

| File | Lines | Bytes |
|------|-------|-------|
| authoring-ground-rules.md | 74 | 3,258 |
| cookbook.md | 267 | 12,789 |
| auto-lint.md | 40 | 1,642 |
| **Total** | **381** | **17,689** |

### Issue 2: Redundancy Between Rules

Two rule files covered the same concerns (scope, planning, verification, incremental progress). Only 3 items in the smaller file were unique. Claude processed overlapping instructions twice per turn.

### Issue 3: Frontmatter Waste in External Reads

The cookbook mandated reading 18 principle files before every plan. Each file was 31-37 lines, but only 10-16 lines were actual content — the rest was YAML frontmatter (UUID, domain, version, dates, author, copyright, license, etc.).

| Metric | Value |
|--------|-------|
| Total lines read | 611 |
| Frontmatter lines | 381 (62%) |
| Content lines | 230 (38%) |

When referencing external files, prefer files with high content-to-metadata ratios. If a file is mostly frontmatter, inline the content instead.

### Issue 4: Ungated Loading

A rule file relevant only when authoring Claude Code extensions (skills, agents, rules) loaded on every turn of every session — including sessions focused on application code.

### Issue 5: MUST NOT Duplication

15 MUST NOT items in one rule file, at least 5 of which restated constraints already expressed imperatively in the body text. Each redundant item consumed per-turn context without adding behavioral value.

### Issue 6: No Proportionality

The same process ran for every task regardless of size: read 18 files, walk through a 38-item checklist, search recipe directories, trace decisions to principles, plan three phases. No mechanism to right-size the process to the task.

---

## Guidelines for Writing Context-Efficient Rules

### 1. Minimize Per-Turn Size

Every byte in a rule file is paid on every turn. Target under 200 lines / ~8KB per rule file. If the rule exceeds this, consider whether content can move to an on-demand skill or external reference.

### 2. Inline Small, Reference Large

Content needed every turn: inline it. Content needed once per session: reference it as an external file. Content needed rarely: put it in a skill that's invoked on demand.

### 3. Don't Duplicate Across Rules

If two rules in the same `.claude/rules/` directory cover the same concept, Claude processes it twice per turn. Consolidate into one rule or extract shared content into a referenced file.

### 4. Use `globs` Frontmatter for Scoping

Rules that only apply to specific file patterns should use `globs` frontmatter:

```yaml
---
globs: .claude/**
---
```

This prevents the rule from loading when working on unrelated files. The feature is supported by Claude Code and already used in some projects (e.g., `globs: site/**` for site-specific design rules).

### 5. Deduplicate MUST NOT Sections

If a constraint is already stated imperatively in the body ("You MUST NOT skip this phase"), don't restate it in the MUST NOT section. Each MUST NOT item should add a unique constraint not expressed elsewhere in the rule.

### 6. Prefer Inline Summaries Over Mandatory File Reads

If external files are mostly metadata (frontmatter > 50% of content), inline the useful content as a summary table. Provide the file path for optional deep-dive reads when a specific item is relevant.

### 7. Avoid Unconditional Multi-File Reads

Rules that mandate reading more than 5 external files before any work begins create a high per-session entry cost. Consider whether summaries, on-demand reads, or iterative approaches can achieve the same behavioral outcome with lower context cost.

---

## Optimization Linter Checks

These checks are available in `/lint-rule` as the O-series (Optimization category):

| ID | Criterion | Severity |
|----|-----------|----------|
| O01 | Rule file under 200 lines / ~8KB | WARN |
| O02 | No content duplicated from another rule in same `.claude/rules/` directory | WARN |
| O03 | If rule applies to specific file patterns, `globs` frontmatter is present | WARN |
| O04 | MUST NOT items don't restate constraints already expressed imperatively in the body | WARN |
| O05 | External file references with >50% frontmatter-to-content ratio — suggest inlining | INFO |
| O06 | Rule does not mandate reading more than 5 external files unconditionally | WARN |
