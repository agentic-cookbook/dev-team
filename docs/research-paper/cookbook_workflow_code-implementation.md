---
id: f4f25f6d-cb87-428d-9140-f2bf97aa420a
title: "Code Implementation"
domain: agentic-cookbook://workflows/code-implementation
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
  - code-implementation
depends-on: []
related: 
  - agentic-cookbook://guidelines/testing/testing
  - agentic-cookbook://guidelines/concurrency/concurrency
  - agentic-cookbook://principles/native-controls
  - agentic-cookbook://principles/dependency-injection
  - agentic-cookbook://principles/explicit-over-implicit
  - agentic-cookbook://principles/fail-fast
  - agentic-cookbook://principles/immutability-by-default
  - agentic-cookbook://principles/make-it-work-make-it-right-make-it-fast
  - agentic-cookbook://principles/separation-of-concerns
  - agentic-cookbook://principles/tight-feedback-loops
  - agentic-cookbook://guidelines/testing/flaky-test-prevention
  - agentic-cookbook://guidelines/testing/test-data
  - agentic-cookbook://guidelines/testing/test-doubles
  - agentic-cookbook://guidelines/testing/the-testing-workflow
  - agentic-cookbook://guidelines/testing/unit-test-patterns
references: []
---

# Code Implementation

---
version: 1.0.0
status: draft
created: 2026-03-27
last-updated: 2026-03-27
author: claude-code
copyright: 2026 Mike Fullerton / Temporal
audience: claude-code
scope: [implementation]
tags: [implementation, coding, testing, phased-delivery]
dependencies:
  - workflow/guideline-checklist.md@1.0.0
  - workflow/branching-strategy.md@1.0.0
  - workflow/code-planning.md@1.0.0
---

## Overview

Defines the write-heavy execution phase where the approved plan from WF-2 (Code Planning) is turned into working code. Claude Code follows the plan systematically, builds in disciplined phases (work → right → fast), writes tests alongside code, commits continuously per WF-1, and applies all opted-in guidelines from the checklist.

This phase produces production-ready code that is then validated by WF-4 (Code Verification) and WF-5 (Code Review).

## Terminology

| Term | Definition |
|------|-----------|
| Approved plan | The plan document from WF-2 that the user has explicitly approved |
| Phase 1/2/3 | The Make It Work / Make It Right / Make It Fast phases from agentic-cookbook://principles/make-it-work-make-it-right-make-it-fast |
| Plan deviation | Any change to the implementation that differs from the approved plan |

## Inputs

- **Approved plan**: The plan from WF-2 Phase 5, approved by the user
- **Guideline decisions**: The opt-in/opt-out matrix from the planning phase
- **Active worktree**: The worktree and draft PR from WF-1
- **Existing code context**: The codebase exploration results from WF-2 Phase 2

## Phases

### Phase 1: Make It Work

**Entry criteria**: Plan approved by the user (WF-2 complete). Worktree active (WF-1).

- **REQ-001**: Claude Code MUST follow the approved plan. Do not re-decide architecture, file structure, or design choices that were already resolved in planning. If the plan says to use a specific pattern, use it.
- **REQ-002**: Claude Code MUST implement the core functionality first — the "happy path" that makes the feature work for the common case. Defer edge cases, error handling refinements, and optimizations to Phase 2.
- **REQ-003**: Claude Code MUST write unit tests alongside implementation — not after. For each function or method, write the test before or immediately after writing the implementation.
- **REQ-004**: Claude Code MUST commit after each meaningful change per WF-1 REQ-005. A meaningful change during Phase 1 is typically: one function/method implemented with its test, one file completed, or one logical unit of the plan delivered.
- **REQ-005**: Claude Code MUST apply all "Always" guidelines from the [guideline-checklist.md](guideline-checklist.md) during implementation. These are non-negotiable.
- **REQ-006**: Claude Code MUST apply all opted-in guidelines from the planning phase. If logging was opted in, every component gets logging. If accessibility was opted in, every view gets accessibility attributes.
- **REQ-007**: Claude Code MUST use existing code, utilities, and patterns identified during planning (WF-2 REQ-004, REQ-007). Do not reinvent what already exists.
- **REQ-008**: Claude Code MUST build and run tests after implementing each logical unit. Do not accumulate untested code.

**Exit criteria**: Core functionality works for the common case. Tests pass. All code committed.

### Phase 2: Make It Right

**Entry criteria**: Phase 1 complete. Core functionality works and tests pass.

- **REQ-009**: Claude Code MUST handle edge cases identified in the plan and any new ones discovered during Phase 1 implementation.
- **REQ-010**: Claude Code MUST refactor for clarity — apply separation of concerns (agentic-cookbook://principles/separation-of-concerns), clean up naming, ensure the code is readable and maintainable.
- **REQ-011**: Claude Code MUST add error handling appropriate to each boundary: user input validation, network error handling, missing data fallbacks.
- **REQ-012**: Claude Code MUST add tests for edge cases and error paths added in this phase.
- **REQ-013**: Claude Code SHOULD review the code for guideline compliance at this point — verify all opted-in concerns are addressed before moving to Phase 3.

**Exit criteria**: Edge cases handled, error paths tested, code refactored for clarity. All tests pass.

### Phase 3: Make It Fast (Conditional)

**Entry criteria**: Phase 2 complete. Code is correct, clean, and well-tested.

- **REQ-014**: Claude Code MUST NOT enter Phase 3 unless there is evidence of a performance problem. "Evidence" means: a test with measurable latency, a user report of slowness, or a known algorithmic concern (e.g., O(n²) with large n).
- **REQ-015**: If optimization is warranted, Claude Code MUST measure before and after. State the metric, the baseline, and the target.
- **REQ-016**: Optimizations MUST NOT sacrifice correctness or readability without explicit user approval.
- **REQ-017**: Claude Code MUST add performance tests or benchmarks for any optimization to prevent regression.

**Exit criteria**: Performance meets the stated target, or Phase 3 is skipped (the common case).

### Phase 4: Plan Deviation Handling

This phase is not sequential — it activates whenever the implementation reveals that the plan needs to change.

- **REQ-018**: If the implementation reveals that the plan is incorrect, incomplete, or needs significant changes, Claude Code MUST stop and inform the user before continuing.
- **REQ-019**: For minor deviations (a function name change, an extra parameter, a small structural adjustment), Claude Code MAY proceed and note the deviation in the next commit message and PR comment.
- **REQ-020**: For major deviations (different architecture, new dependencies, scope change, dropped features), Claude Code MUST return to WF-2 for a plan update. The updated plan MUST be approved before continuing.
- **REQ-021**: Claude Code MUST document all plan deviations — minor and major — as PR comments per WF-1 REQ-010.

## Behavioral Requirements

- **REQ-022**: Claude Code MUST NOT introduce code that is not in the plan or requested by the user. Do not add "bonus" features, refactor unrelated code, or "improve" things outside the scope.
- **REQ-023**: Claude Code MUST follow the project's existing code style, naming conventions, and file organization patterns. Match what's already there.
- **REQ-024**: Claude Code MUST NOT skip writing tests to save time. Tests are a deliverable, not an afterthought.
- **REQ-025**: If a build or test fails, Claude Code MUST fix the failure before continuing to the next unit of work. Do not accumulate broken state.

## Guideline Cross-Reference

This workflow references the shared [guideline-checklist.md](guideline-checklist.md).

| Phase | Checklist Items | Notes |
|-------|----------------|-------|
| Phase 1 | agentic-cookbook://principles/native-controls (native controls), agentic-cookbook://guidelines/concurrency/concurrency (no blocking main thread), agentic-cookbook://principles/dependency-injection (DI), agentic-cookbook://principles/immutability-by-default (immutability) | Core engineering during implementation |
| Phase 1 | agentic-cookbook://guidelines/testing/testing (unit testing), agentic-cookbook://guidelines/testing/unit-test-patterns (test patterns), agentic-cookbook://guidelines/testing/flaky-test-prevention (no flaky tests), agentic-cookbook://guidelines/testing/test-data (test data) | Tests written alongside code |
| Phase 1 | All opted-in items from WF-2 | Logging, accessibility, deep linking, feature flags, etc. |
| Phase 2 | agentic-cookbook://principles/fail-fast (fail fast), agentic-cookbook://principles/separation-of-concerns (separation of concerns), agentic-cookbook://principles/explicit-over-implicit (explicit over implicit) | Refactoring and error handling |
| Phase 3 | agentic-cookbook://principles/tight-feedback-loops (tight feedback loops) | Performance measurement and optimization |

## Conformance Test Vectors

| ID | Requirements | Scenario | Expected |
|----|-------------|----------|----------|
| impl-001 | REQ-001 | Plan says use Repository pattern | Claude Code uses Repository pattern, does not switch to Active Record |
| impl-002 | REQ-002 | Feature with 3 edge cases | Phase 1 implements happy path only; edge cases deferred to Phase 2 |
| impl-003 | REQ-003 | New function implemented | Unit test written for the function in the same commit or immediately after |
| impl-004 | REQ-004 | Function and test completed | Commit created with descriptive message |
| impl-005 | REQ-006 | Logging opted in during planning | Every component includes structured logging |
| impl-006 | REQ-006 | Accessibility opted out during planning | No accessibility attributes added |
| impl-007 | REQ-007 | Utility function exists in codebase | Claude Code imports and uses it, does not create a duplicate |
| impl-008 | REQ-008 | Three functions implemented | Build and tests run after each, not just at the end |
| impl-009 | REQ-009 | Edge case: empty input | Phase 2 adds handling and test for empty input |
| impl-010 | REQ-014 | No performance evidence | Phase 3 skipped entirely |
| impl-011 | REQ-018 | Plan assumes API returns JSON, but it returns XML | Claude Code stops and informs user |
| impl-012 | REQ-019 | Function name changed from plan | Deviation noted in commit message and PR comment |
| impl-013 | REQ-020 | Feature needs a new dependency not in plan | Claude Code returns to WF-2 for plan update |
| impl-014 | REQ-022 | Unrelated code noticed during implementation | Claude Code does not refactor it |
| impl-015 | REQ-025 | Test fails after implementation | Claude Code fixes the failure before moving on |

## Edge Cases

- **Plan references outdated code**: If the plan references a function or file that was modified since planning, Claude Code MUST check the current state and adapt. If the change is significant, treat it as a plan deviation (REQ-018).
- **Circular dependency discovered**: If implementing the plan creates a circular dependency, stop and raise it with the user. This is a major plan deviation.
- **Test infrastructure missing**: If the project lacks test infrastructure (no test runner, no test directory), set it up before writing tests. This is part of delivering working code, not scope creep.
- **External service unavailable**: If the implementation depends on an external service that is unavailable during development, use a fake/stub (agentic-cookbook://guidelines/testing/test-doubles) and note this in the PR.

## Tool Notes

- **Claude Code**: Exit plan mode before writing code. Use file write/edit tools for implementation. Run builds and tests via Bash after each logical unit.
- **git**: Commit after each meaningful change. Push regularly. Verify clean working tree after each commit (WF-1 REQ-006).
- **Build tools**: Run the project's build command after each logical unit. Fix errors immediately — do not accumulate.

## Design Decisions

**Decision**: Tests written alongside code, not in a separate phase after implementation.
**Rationale**: Writing tests after all implementation is done creates a temptation to skip or rush them. Writing tests alongside code catches bugs earlier, serves as design feedback (hard-to-test code = bad design), and ensures no code ships untested. Aligns with agentic-cookbook://guidelines/testing/the-testing-workflow (testing workflow).
**Approved**: pending

**Decision**: Phase 3 (Make It Fast) is conditional on evidence, not automatic.
**Rationale**: Premature optimization wastes time and harms readability (agentic-cookbook://principles/make-it-work-make-it-right-make-it-fast). Most code is fast enough without optimization. Phase 3 only activates when measurement proves a problem exists.
**Approved**: pending

**Decision**: Minor plan deviations can proceed; major ones require returning to WF-2.
**Rationale**: Requiring re-planning for every small adjustment would create excessive friction. But allowing major changes without user approval risks building the wrong thing. The distinction is: does this deviation change what the user will receive?
**Approved**: pending

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-27 | Initial spec |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial creation |
