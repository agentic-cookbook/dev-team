---
id: 6fba028d-fe54-48cc-9868-538b36916d72
title: "Code Planning"
domain: agentic-cookbook://workflows/code-planning
type: workflow
version: 1.0.0
status: accepted
language: en
created: 2026-03-27
modified: 2026-03-27
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "version: 1.0.0"
platforms: []
tags: 
  - code-planning
depends-on: []
related: 
  - agentic-cookbook://principles/simplicity
  - agentic-cookbook://principles/small-reversible-decisions
  - agentic-cookbook://principles/yagni
references: []
---

# Code Planning

---
version: 1.0.0
status: draft
created: 2026-03-27
last-updated: 2026-03-27
author: claude-code
copyright: 2026 Mike Fullerton / Temporal
audience: claude-code
scope: [planning]
tags: [planning, design, guidelines, checklist]
dependencies:
  - workflow/guideline-checklist.md@1.0.0
  - workflow/branching-strategy.md@1.0.0
---

## Overview

Defines the read-only decision-making phase before any code is written. Claude Code systematically evaluates the task, checks for existing patterns and code, runs the guideline applicability checklist with the user, asks all clarifying questions upfront, and produces an approved plan. No code is written during this phase.

This phase happens inside a worktree established by WF-1 (Branching Strategy) and produces the plan that WF-3 (Code Implementation) executes.

## Terminology

| Term | Definition |
|------|-----------|
| Guideline checklist | The shared [guideline-checklist.md](guideline-checklist.md) listing all guide.* guidelines with opt-in/opt-out defaults |
| Plan document | The output of this phase — a structured description of what will be built, how, and which guidelines apply |
| Applicability scan | The process of evaluating each checklist item for relevance to the current task |

## Inputs

- **Task description**: Clear description of the work from the user (issue, feature request, bug report, or verbal description)
- **Worktree**: An active worktree with a draft PR, established by WF-1
- **Codebase access**: Read access to the project's source code, specs, tests, and configuration

## Phases

### Phase 1: Understand the Request

**Entry criteria**: User has described the work. Worktree is active (WF-1 Phase 1 complete).

- **REQ-001**: Claude Code MUST read and restate the user's request in its own words to confirm understanding. Do not proceed until the user confirms the restatement is accurate.
- **REQ-002**: Claude Code MUST identify the scope boundaries — what is and is not included in this task. State these explicitly and get user confirmation.
- **REQ-003**: If the task references an existing recipe (from the cookbook or the project), Claude Code MUST read the recipe before proceeding.

**Exit criteria**: User has confirmed Claude Code's understanding of the request and scope.

### Phase 2: Explore Existing Code

**Entry criteria**: Phase 1 complete. Task understood and scoped.

- **REQ-004**: Claude Code MUST search the codebase for existing implementations, patterns, utilities, and abstractions that are relevant to the task. Specifically look for:
  - Existing code that does something similar
  - Shared utilities, helpers, or base classes that should be reused
  - Established patterns (naming conventions, file organization, dependency injection setup)
  - Test infrastructure and existing test patterns
- **REQ-005**: Claude Code MUST check for existing recipes in `cookbook/recipes/` that cover the component or feature being built. If a recipe exists, it MUST be followed.
- **REQ-006**: Claude Code SHOULD identify code that would be affected by the change — callers, dependents, tests that might break.
- **REQ-007**: Claude Code MUST NOT propose creating new utilities, abstractions, or patterns when suitable ones already exist in the codebase. Reuse first.

**Exit criteria**: Claude Code has a clear picture of the existing codebase landscape relevant to the task.

### Phase 3: Run the Guideline Checklist

**Entry criteria**: Phase 2 complete. Codebase explored.

- **REQ-008**: Claude Code MUST read the [guideline-checklist.md](guideline-checklist.md) and evaluate every item for applicability to the current task.
- **REQ-009**: For each "Always" item, Claude Code MUST note it as applicable without asking the user.
- **REQ-010**: For each "Opt-in" item, Claude Code MUST inform the user it will be included and ask for confirmation or opt-out.
- **REQ-011**: For each "Opt-out" item, Claude Code MUST ask the user if they want to opt in.
- **REQ-012**: For each "Ask" item, Claude Code MUST ask the user the prompt template question from the checklist.
- **REQ-013**: Claude Code MUST present all checklist items in a single consolidated prompt rather than asking about them one at a time. Group by category (core engineering, testing, opt-in concerns).
- **REQ-014**: Claude Code MUST record all opt-in/opt-out decisions for reference during implementation and verification.

**Exit criteria**: All guideline applicability decisions recorded. User has confirmed the checklist.

### Phase 4: Ask Clarifying Questions

**Entry criteria**: Phase 3 complete. Guidelines scoped.

- **REQ-015**: Claude Code MUST ask all clarifying questions in this phase — not during implementation. Questions SHOULD cover:
  - Ambiguous requirements
  - Platform-specific behavior (if multi-platform)
  - Error handling strategy
  - Edge cases the user may not have considered
  - Dependencies or prerequisites
- **REQ-016**: Claude Code SHOULD batch questions into a single consolidated prompt, organized by topic, rather than asking one at a time.
- **REQ-017**: If the task involves UI, Claude Code SHOULD ask about visual design preferences, layout expectations, and interaction patterns not covered by the spec.

**Exit criteria**: All questions answered. No remaining ambiguity.

### Phase 5: Produce the Plan

**Entry criteria**: Phase 4 complete. No remaining ambiguity.

- **REQ-018**: Claude Code MUST produce a structured plan document that includes:
  1. **Summary**: One-paragraph description of what will be built
  2. **Files**: List of files to create, modify, or delete — with brief notes on what changes in each
  3. **Architecture**: Key design decisions, patterns used, dependency flow
  4. **Guideline decisions**: The recorded opt-in/opt-out matrix from Phase 3
  5. **Test strategy**: What will be tested, at which level (unit/integration/E2E), key test cases
  6. **Dependencies**: External libraries or internal modules needed
  7. **Risks**: Known risks, unknowns, or areas likely to need iteration

- **REQ-019**: The plan MUST be concrete enough that another developer (or AI session) could execute it without asking follow-up questions.
- **REQ-020**: Claude Code MUST present the plan to the user and get explicit approval before proceeding to implementation (WF-3).
- **REQ-021**: If the user requests changes to the plan, Claude Code MUST update the plan and re-present it for approval. Do not proceed with a plan the user has not approved.
- **REQ-022**: Claude Code MUST post the approved plan as a PR comment on the draft PR (per WF-1 REQ-009).

**Exit criteria**: Plan approved by the user and posted to the PR.

## Guideline Cross-Reference

This workflow references the shared [guideline-checklist.md](guideline-checklist.md).

| Phase | Checklist Items | Notes |
|-------|----------------|-------|
| Phase 3 | All items | Full checklist scan — this is the primary phase for checklist evaluation |
| Phase 5 | agentic-cookbook://principles/simplicity (Simplicity), agentic-cookbook://principles/yagni (YAGNI) | Plan should reflect simplest viable approach |

## Conformance Test Vectors

| ID | Requirements | Scenario | Expected |
|----|-------------|----------|----------|
| plan-001 | REQ-001 | User describes a feature | Claude Code restates the request and waits for confirmation |
| plan-002 | REQ-002 | Feature with ambiguous scope | Claude Code explicitly states what is and isn't included |
| plan-003 | REQ-004 | Feature similar to existing code | Claude Code finds and references existing implementation |
| plan-004 | REQ-005 | Feature has a cookbook recipe | Claude Code reads the recipe before planning |
| plan-005 | REQ-007 | Utility function already exists in codebase | Claude Code proposes reusing it, not creating a new one |
| plan-006 | REQ-008, REQ-013 | Planning begins | Claude Code presents full checklist in one consolidated prompt |
| plan-007 | REQ-010 | Opt-in item (e.g., logging) | Claude Code informs user it's included, asks to confirm or opt out |
| plan-008 | REQ-011 | Opt-out item (e.g., A/B testing) | Claude Code asks user if they want to opt in |
| plan-009 | REQ-014 | Checklist complete | All decisions recorded in plan document |
| plan-010 | REQ-015, REQ-016 | Multiple ambiguities exist | Claude Code asks all questions in one batch, not one at a time |
| plan-011 | REQ-018 | Planning complete | Plan includes all 7 required sections |
| plan-012 | REQ-019 | Plan reviewed | Plan is concrete enough to execute without follow-up questions |
| plan-013 | REQ-020 | Plan presented | Claude Code waits for explicit user approval |
| plan-014 | REQ-021 | User requests plan changes | Plan updated, re-presented, re-approved |
| plan-015 | REQ-022 | Plan approved | Plan posted as PR comment |

## Edge Cases

- **Trivial task**: If the task is genuinely trivial (typo fix, one-line change), Claude Code MAY abbreviate the planning phase but MUST still confirm the change with the user before proceeding.
- **No existing code to explore**: For greenfield features in new projects, Phase 2 focuses on understanding project conventions and tech stack rather than existing implementations.
- **Conflicting guidelines**: If two guidelines conflict for the current task (e.g., simplicity vs. accessibility requirements), surface the conflict to the user and record the resolution in the plan.
- **User declines all opt-in items**: This is valid. Record the decisions and proceed. The "Always" items still apply.
- **Recipe doesn't exist**: If a cookbook recipe should exist but doesn't, offer to create one (using `cookbook/recipes/_template.md`) before or alongside the implementation.

## Tool Notes

- **Claude Code**: Use plan mode (`EnterPlanMode`) during this phase. Do not write or edit code files. Read-only exploration only.
- **git**: No commits during planning — the plan is a conversation artifact, not a file in the repo (though it is posted as a PR comment per REQ-022).
- **gh**: Use `gh pr comment` to post the plan to the draft PR.

## Design Decisions

**Decision**: Run the full guideline checklist in a single consolidated prompt rather than one item at a time.
**Rationale**: Asking about 15+ items one at a time creates excessive back-and-forth. A consolidated prompt respects the user's time while ensuring nothing is missed.
**Approved**: pending

**Decision**: Planning is strictly read-only — no code or file modifications.
**Rationale**: Separating planning from implementation prevents premature commitment to an approach. It's cheaper to change a plan than to rewrite code. This mirrors the principle of small, reversible decisions (agentic-cookbook://principles/small-reversible-decisions).
**Approved**: pending

**Decision**: Plan must be approved before implementation begins.
**Rationale**: Getting explicit sign-off prevents wasted work on approaches the user doesn't want. This is the "measure twice, cut once" principle applied to AI-assisted development.
**Approved**: pending

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-27 | Initial spec |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial creation |
