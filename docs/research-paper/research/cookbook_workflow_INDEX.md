---
id: 922655fa-e37c-44e3-828f-4799c1b83ff4
title: "Workflow Index"
domain: agentic-cookbook://workflows/INDEX
type: workflow
version: 1.0.0
status: accepted
language: en
created: 2026-03-27
modified: 2026-03-27
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Process-oriented recipes describing how Claude Code AI sessions should develop code in consuming projects. These work..."
platforms: []
tags: []
depends-on: []
related: []
references: []
---

# Workflow Index

Process-oriented recipes describing how Claude Code AI sessions should develop code in consuming projects. These workflows complement the [guide.* guidelines](~/.claude/guidelines/) by providing orchestration: *when* and *in what order* to apply those guidelines.

Cross-reference using `WF-` notation: "See WF-2" means code-planning.md. "See WF-2.3" means code-planning.md Phase 3. `WF-` numbers are stable — never reuse a number, even if a workflow is removed.

**Maintenance**: This index MUST be updated on the same branch as any workflow change. The CLAUDE.md `WF-` numbering table must stay in sync.

## Development Lifecycle

The five workflows form a pipeline. Every coding session flows through them in order:

```
WF-1 Branching Strategy (wraps all phases)
 ├── WF-2 Code Planning
 ├── WF-3 Code Implementation
 ├── WF-4 Code Verification
 └── WF-5 Code Review
```

WF-1 establishes the worktree and draft PR. WF-2 through WF-5 execute inside that worktree. When WF-5 passes, WF-1 marks the PR ready and merges.

## Shared Resources

| File | Description |
|------|-------------|
| [_template.md](_template.md) | Starting point for new workflow specs — copy, don't edit |
| [guideline-checklist.md](guideline-checklist.md) | Shared opt-in/opt-out cross-reference for all guide.* guidelines |

## Workflows

| ID | Spec | Version | Description |
|----|------|---------|-------------|
| WF-1 | [branching-strategy.md](branching-strategy.md) | 1.0.0 | Worktree + draft PR lifecycle for AI sessions |
| WF-2 | [code-planning.md](code-planning.md) | 1.0.0 | Pre-implementation decision-making and guideline applicability |
| WF-3 | [code-implementation.md](code-implementation.md) | 1.0.0 | Disciplined phased execution of the plan |
| WF-4 | [code-verification.md](code-verification.md) | 1.0.0 | Post-implementation validation and testing |
| WF-5 | [code-review.md](code-review.md) | 1.0.0 | Structured review process for AI-generated code |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial creation |
