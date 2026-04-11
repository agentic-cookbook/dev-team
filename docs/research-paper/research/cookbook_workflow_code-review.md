---
id: a5dc2751-9332-46be-86aa-649e51c237dc
title: "Code Review"
domain: agentic-cookbook://workflows/code-review
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
platforms: 
  - kotlin
  - python
  - swift
  - typescript
tags: 
  - code-review
depends-on: []
related: 
  - agentic-cookbook://guidelines/security/privacy
  - agentic-cookbook://principles/composition-over-inheritance
  - agentic-cookbook://principles/explicit-over-implicit
  - agentic-cookbook://principles/immutability-by-default
  - agentic-cookbook://principles/separation-of-concerns
  - agentic-cookbook://principles/simplicity
  - agentic-cookbook://principles/yagni
  - agentic-cookbook://guidelines/testing/flaky-test-prevention
  - agentic-cookbook://guidelines/testing/properties-of-good-tests
  - agentic-cookbook://guidelines/testing/test-doubles
  - agentic-cookbook://guidelines/testing/unit-test-patterns
references: []
---

# Code Review

---
version: 1.0.0
status: draft
created: 2026-03-27
last-updated: 2026-03-27
author: claude-code
copyright: 2026 Mike Fullerton / Temporal
audience: claude-code
scope: [review]
tags: [review, quality, security, best-practices]
dependencies:
  - workflow/guideline-checklist.md@1.0.0
  - workflow/branching-strategy.md@1.0.0
  - workflow/code-verification.md@1.0.0
---

## Overview

Defines the structured code review process for AI-generated code. Claude Code performs a self-review against platform best practices, guideline compliance, security, test quality, and overall code health before marking the PR as ready. This is the final quality gate before the PR leaves draft status.

Referenced from WF-1 (Branching Strategy) Phase 3 as the gate before marking a PR active. Runs after WF-4 (Code Verification) — verification checks that the code *works*; review checks that the code is *good*.

## Terminology

| Term | Definition |
|------|-----------|
| Self-review | Claude Code reviewing its own generated code against objective criteria |
| Best practices | Platform-specific coding standards from `~/.claude/guidelines/best-practices-references.md` and the platform guideline files |
| Code health | The overall quality of the code: readability, maintainability, correctness, simplicity |

## Inputs

- **Verification summary**: The output of WF-4 Phase 8, confirming all verification checks passed
- **Guideline decisions**: The opt-in/opt-out matrix from WF-2
- **Approved plan**: The plan from WF-2 for cross-referencing intent vs. implementation
- **Complete diff**: All changes in the branch compared to the base branch

## Phases

### Phase 1: Diff Review

**Entry criteria**: WF-4 (Code Verification) complete. Verification summary posted.

- **REQ-001**: Claude Code MUST review the complete diff (`git diff main...HEAD`) — not just individual files. The review should understand how all changes fit together.
- **REQ-002**: Claude Code MUST verify that every change in the diff is intentional and traceable to the plan. Flag any changes that appear unrelated to the task.
- **REQ-003**: Claude Code MUST check for common diff-level issues:
  - Accidentally committed debug code (`print`, `console.log`, `TODO`, `FIXME`)
  - Commented-out code that should be deleted
  - Files that were modified but shouldn't have been (e.g., unrelated formatting changes)
  - Merge conflict markers
  - Credentials, API keys, or secrets

**Exit criteria**: Diff reviewed. No unintentional changes or artifacts.

### Phase 2: Code Quality Review

**Entry criteria**: Phase 1 complete. Diff is clean.

- **REQ-004**: Claude Code MUST review new code against the platform-specific best practices for the project's language/framework. Check the relevant guideline file:
  - Swift: `~/.claude/guidelines/swift.md`
  - Kotlin: `~/.claude/guidelines/kotlin.md`
  - TypeScript: `~/.claude/guidelines/typescript.md`
  - Python: `~/.claude/guidelines/python.md`
  - C#: `~/.claude/guidelines/csharp.md`

- **REQ-005**: Claude Code MUST check for violations of the engineering principles (agentic-cookbook://principles/*):
  - Unnecessary complexity (agentic-cookbook://principles/simplicity)
  - Premature abstraction or speculative generality (agentic-cookbook://principles/yagni)
  - Implicit dependencies or hidden state (agentic-cookbook://principles/explicit-over-implicit)
  - Mixed concerns in a single module (agentic-cookbook://principles/separation-of-concerns)
  - Deep inheritance hierarchies (agentic-cookbook://principles/composition-over-inheritance)
  - Mutable shared state (agentic-cookbook://principles/immutability-by-default)

- **REQ-006**: Claude Code MUST verify naming quality:
  - Types, functions, and variables have descriptive names that reveal intent
  - Names match project conventions (casing, prefixes, suffixes)
  - No misleading names (a function named `getUser` should not have side effects)

- **REQ-007**: Claude Code MUST verify code readability:
  - Functions are focused and not excessively long
  - Complex logic has explanatory comments (but obvious code does not)
  - Control flow is straightforward — no deeply nested conditionals

**Exit criteria**: Code quality issues identified and fixed.

### Phase 3: Security Review

**Entry criteria**: Phase 2 complete.

- **REQ-008**: Claude Code MUST review new code for OWASP Top 10 vulnerabilities:
  1. Injection (SQL, command, XSS)
  2. Broken authentication
  3. Sensitive data exposure
  4. XML external entities (XXE)
  5. Broken access control
  6. Security misconfiguration
  7. Cross-site scripting (XSS)
  8. Insecure deserialization
  9. Using components with known vulnerabilities
  10. Insufficient logging and monitoring

- **REQ-009**: Claude Code MUST verify that user input is validated and sanitized at system boundaries (agentic-cookbook://guidelines/security/privacy).
- **REQ-010**: Claude Code MUST verify that credentials and tokens use platform secure storage (agentic-cookbook://guidelines/security/privacy), not plain text or UserDefaults/SharedPreferences.
- **REQ-011**: If the code handles network requests, Claude Code MUST verify TLS-only (agentic-cookbook://guidelines/security/privacy) and proper error handling of network failures.

**Exit criteria**: No security vulnerabilities in new code.

### Phase 4: Test Quality Review

**Entry criteria**: Phase 3 complete.

- **REQ-012**: Claude Code MUST review test quality, not just test existence:
  - Tests verify behavior, not implementation details (agentic-cookbook://guidelines/testing/properties-of-good-tests "behavioral")
  - Tests would survive a refactoring of internals (agentic-cookbook://guidelines/testing/properties-of-good-tests "structure-insensitive")
  - Tests are readable — a failing test tells you what broke (agentic-cookbook://guidelines/testing/properties-of-good-tests "readable", "specific")
  - No logic in tests — no `if`, `for`, `try/catch` (agentic-cookbook://guidelines/testing/unit-test-patterns)
  - Each test has one assertion concept (agentic-cookbook://guidelines/testing/unit-test-patterns)

- **REQ-013**: Claude Code MUST verify test coverage completeness:
  - Every public API method has at least one test
  - Every MUST requirement from the plan/spec has a test
  - Edge cases from the plan are tested
  - Error paths have tests (not just happy paths)

- **REQ-014**: Claude Code MUST verify that test doubles are used appropriately:
  - Fakes preferred over mocks (agentic-cookbook://guidelines/testing/test-doubles)
  - Third-party dependencies wrapped behind interfaces, not mocked directly (agentic-cookbook://guidelines/testing/test-doubles)
  - No shared mutable state between tests (agentic-cookbook://guidelines/testing/flaky-test-prevention)

**Exit criteria**: Tests are meaningful, comprehensive, and well-structured.

### Phase 5: Guideline Compliance Review

**Entry criteria**: Phase 4 complete.

- **REQ-015**: Claude Code MUST cross-reference the guideline decisions from WF-2 and verify each opted-in concern is fully and correctly implemented. This is a final check beyond WF-4 Phase 6 — review catches subtle issues that automated verification might miss.
- **REQ-016**: Claude Code MUST verify that the implementation matches the approved plan. Any deviations should already be documented (per WF-3 REQ-021), but review confirms nothing was missed.

**Exit criteria**: All opted-in guidelines confirmed. Implementation matches plan.

### Phase 6: Review Summary

**Entry criteria**: All previous phases complete.

- **REQ-017**: Claude Code MUST compile a review summary and post it as a PR comment. The summary MUST include:
  1. **Diff review**: Clean / issues found (list them)
  2. **Code quality**: Pass / issues found and fixed
  3. **Security**: Pass / findings (list severity and resolution)
  4. **Test quality**: Pass / gaps identified and filled
  5. **Guideline compliance**: Pass / deviations noted
  6. **Overall assessment**: Ready for review / needs changes

- **REQ-018**: If the review found issues that were fixed during this phase, Claude Code MUST commit those fixes per WF-1 REQ-005.
- **REQ-019**: If the review found issues that could not be fixed (e.g., architectural concerns requiring a plan change), Claude Code MUST note them in the summary and discuss with the user before proceeding.

**Exit criteria**: Review summary posted. All fixable issues resolved. PR ready for WF-1 Phase 3.

## Guideline Cross-Reference

This workflow references the shared [guideline-checklist.md](guideline-checklist.md).

| Phase | Checklist Items | Notes |
|-------|----------------|-------|
| Phase 2 | agentic-cookbook://principles/simplicity, agentic-cookbook://principles/composition-over-inheritance, agentic-cookbook://principles/immutability-by-default, agentic-cookbook://principles/yagni, agentic-cookbook://principles/explicit-over-implicit, agentic-cookbook://principles/separation-of-concerns | Engineering principles |
| Phase 3 | agentic-cookbook://guidelines/security/privacy (all subsections) | Privacy and security |
| Phase 4 | agentic-cookbook://guidelines/testing/properties-of-good-tests, agentic-cookbook://guidelines/testing/unit-test-patterns, agentic-cookbook://guidelines/testing/test-doubles, agentic-cookbook://guidelines/testing/flaky-test-prevention | Test quality |
| Phase 5 | All opted-in items from WF-2 | Final compliance check |

## Conformance Test Vectors

| ID | Requirements | Scenario | Expected |
|----|-------------|----------|----------|
| review-001 | REQ-001 | Branch has 12 commits | Review covers complete diff, not individual commits |
| review-002 | REQ-002 | Diff includes formatting change to unrelated file | Flagged and reverted |
| review-003 | REQ-003 | `console.log("debug")` in production code | Flagged and removed |
| review-004 | REQ-003 | API key hardcoded in source | Flagged, moved to secure storage |
| review-005 | REQ-005 | Class has 500 lines with 3 responsibilities | Flagged as violating separation of concerns |
| review-006 | REQ-006 | Variable named `data` with no context | Renamed to descriptive name |
| review-007 | REQ-008 | User input concatenated into SQL query | Flagged as SQL injection, fixed with parameterized query |
| review-008 | REQ-010 | Token stored in UserDefaults | Flagged, moved to Keychain |
| review-009 | REQ-012 | Test mocks internal method to verify call count | Flagged as testing implementation, rewritten to test behavior |
| review-010 | REQ-013 | Error path has no test | Test added for error case |
| review-011 | REQ-017 | Review complete | Summary posted with all 6 sections |
| review-012 | REQ-019 | Architectural issue found | User consulted before proceeding |

## Edge Cases

- **Self-review bias**: Claude Code reviewing its own code risks confirmation bias. Mitigate by using objective checklists (this spec) rather than subjective judgment. Each phase has concrete criteria.
- **Review finds too many issues**: If review reveals pervasive quality problems, this may indicate the implementation phase was rushed. Discuss with the user whether to fix incrementally or reconsider the approach.
- **Platform-specific guidelines not available**: If the project uses a language/framework without a guideline file, apply general engineering principles (agentic-cookbook://principles/*) and note the gap in the review summary.
- **No changes needed**: If review finds no issues, that's a valid outcome. Post the summary confirming all checks passed.

## Tool Notes

- **git**: Use `git diff main...HEAD` for the complete diff. Use `git log --oneline main..HEAD` to see all commits.
- **gh**: Use `gh pr comment` to post the review summary. Use `gh pr diff` as an alternative to `git diff`.
- **Claude Code**: Read the platform-specific guideline file for the project's language before starting the review. Use Grep to search for common anti-patterns (hardcoded strings, debug statements, etc.).

## Design Decisions

**Decision**: Review is a separate phase from verification.
**Rationale**: Verification (WF-4) checks that the code *works* — builds, tests pass, logs emit. Review (WF-5) checks that the code is *good* — readable, maintainable, secure, well-tested. These are complementary but distinct concerns. Separating them ensures neither is shortchanged.
**Approved**: pending

**Decision**: Self-review uses objective checklists, not subjective assessment.
**Rationale**: An AI reviewing its own output is inherently biased toward finding it acceptable. Objective checklists (OWASP Top 10, engineering principles, test quality criteria) provide a structured framework that reduces bias.
**Approved**: pending

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-27 | Initial spec |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial creation |
