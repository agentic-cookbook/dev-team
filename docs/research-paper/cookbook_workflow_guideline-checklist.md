---
id: 6b29562c-4185-4411-aa66-092206d6bfa5
title: "Guideline Applicability Checklist"
domain: agentic-cookbook://workflows/guideline-checklist
type: workflow
version: 1.1.0
status: accepted
language: en
created: 2026-03-27
modified: 2026-03-27
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Shared checklist of 38 guideline concerns for planning and implementation pipelines"
platforms: []
tags: 
  - guideline-checklist
depends-on: []
related: 
  - agentic-cookbook://guidelines/feature-management/ab-testing
  - agentic-cookbook://guidelines/accessibility/accessibility
  - agentic-cookbook://guidelines/ui/always-show-progress
  - agentic-cookbook://guidelines/logging/analytics
  - agentic-cookbook://guidelines/testing/testing
  - agentic-cookbook://guidelines/feature-management/debug-mode
  - agentic-cookbook://guidelines/platform/deep-linking
  - agentic-cookbook://guidelines/feature-management/feature-flags
  - agentic-cookbook://guidelines/logging/logging
  - agentic-cookbook://guidelines/code-quality/linting
  - agentic-cookbook://guidelines/internationalization/localization
  - agentic-cookbook://guidelines/concurrency/concurrency
  - agentic-cookbook://guidelines/testing/post-generation-verification
  - agentic-cookbook://principles/native-controls
  - agentic-cookbook://guidelines/security/privacy
  - agentic-cookbook://guidelines/accessibility/accessibility
  - agentic-cookbook://guidelines/internationalization/rtl-support
  - agentic-cookbook://guidelines/platform/shortcuts-and-automation
  - agentic-cookbook://guidelines/code-quality/atomic-commits
  - agentic-cookbook://introduction/conventions
  - agentic-cookbook://principles/dependency-injection
  - agentic-cookbook://principles/design-for-deletion
  - agentic-cookbook://principles/explicit-over-implicit
  - agentic-cookbook://principles/fail-fast
  - agentic-cookbook://principles/immutability-by-default
  - agentic-cookbook://principles/make-it-work-make-it-right-make-it-fast
  - agentic-cookbook://principles/separation-of-concerns
  - agentic-cookbook://principles/simplicity
  - agentic-cookbook://principles/yagni
  - agentic-cookbook://guidelines/testing/flaky-test-prevention
  - agentic-cookbook://guidelines/testing/mutation-testing
  - agentic-cookbook://guidelines/testing/properties-of-good-tests
  - agentic-cookbook://guidelines/testing/property-based-testing
  - agentic-cookbook://guidelines/testing/security-testing
  - agentic-cookbook://guidelines/testing/test-data
  - agentic-cookbook://guidelines/testing/test-pyramid
  - agentic-cookbook://guidelines/testing/the-testing-workflow
  - agentic-cookbook://guidelines/testing/unit-test-patterns
  - agentic-cookbook://guidelines/database-design/sqlite-best-practices
references: []
---

# Guideline Applicability Checklist

---
version: 1.1.0
status: draft
created: 2026-03-27
last-updated: 2026-03-27
author: claude-code
copyright: 2026 Mike Fullerton / Temporal
audience: claude-code
scope: [planning, implementation, verification, review]
tags: [checklist, guidelines, cross-reference]
---

## Overview

A shared checklist of all guide.* guidelines that Claude Code MUST evaluate for applicability during a development session. Each workflow recipe (WF-1 through WF-5) references this checklist rather than duplicating it. When guidelines change, only this file needs updating.

During the **Code Planning** phase (WF-2), Claude Code MUST walk through this checklist with the user, asking them to opt in or opt out of each applicable concern. The decisions are recorded and carried forward through implementation (WF-3), verification (WF-4), and review (WF-5).

## Terminology

| Term | Definition |
|------|-----------|
| Opt-in default | The concern is assumed applicable unless the user explicitly opts out |
| Opt-out default | The concern is assumed not applicable unless the user explicitly opts in |
| Ask | Claude Code MUST ask the user — no default assumption |
| Always | The concern is always applicable and cannot be opted out of |

## Checklist

### Core Engineering (Always Apply)

These guidelines are always applicable. Claude Code MUST follow them without asking. They cannot be opted out of.

| File | Guideline | Summary | Workflow Phases |
|------|-----------|---------|-----------------|
| `../agentic-cookbook/cookbook/principles/native-controls.md` | Native controls | Prefer platform built-in frameworks | WF-3 |
| `../agentic-cookbook/cookbook/guidelines/code-quality/scope-discipline.md` | Surface design decisions | Note and get approval for all behavioral/structural choices | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/concurrency/concurrency.md` | No blocking main thread | All lengthy work on background threads | WF-3 |
| `../agentic-cookbook/cookbook/guidelines/code-quality/atomic-commits.md` | Small atomic commits | One logical change per commit | WF-1, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/testing/post-generation-verification.md` | Post-generation verification | Build, test, lint, log verify, a11y audit, code review | WF-4 |
| `../agentic-cookbook/cookbook/guidelines/code-quality/linting.md` | Linting from day one | Linter configured, runs on build or pre-commit | WF-3, WF-4 |
| `../agentic-cookbook/cookbook/principles/simplicity.md` | Simplicity | No interleaving of concerns | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/principles/make-it-work-make-it-right-make-it-fast.md` | Work, Right, Fast | Three sequential phases — never skip phase 2 | WF-3 |
| `../agentic-cookbook/cookbook/principles/dependency-injection.md` | Dependency injection | Receive dependencies from outside | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/principles/immutability-by-default.md` | Immutability by default | Default to immutable values | WF-3 |
| `../agentic-cookbook/cookbook/principles/fail-fast.md` | Fail fast | Detect invalid state at point of origin | WF-3 |
| `../agentic-cookbook/cookbook/principles/design-for-deletion.md` | Design for deletion | Build disposable, not reusable | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/principles/yagni.md` | YAGNI | Build for today's known requirements | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/principles/explicit-over-implicit.md` | Explicit over implicit | Visible dependencies, clear intent | WF-3 |
| `../agentic-cookbook/cookbook/principles/separation-of-concerns.md` | Separation of concerns | One reason to change per module | WF-2, WF-3 |

### Testing (Always Apply)

Testing guidelines are always applicable when writing code. The scope and depth may vary based on the task.

| File | Guideline | Summary | Workflow Phases |
|------|-----------|---------|-----------------|
| `../agentic-cookbook/cookbook/guidelines/testing/testing.md` | Comprehensive unit testing | Prioritize unit tests, test state transitions and edge cases | WF-3, WF-4 |
| `../agentic-cookbook/cookbook/guidelines/testing/test-pyramid.md` | Test pyramid | 80% unit / 15% integration / 5% E2E | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/testing/properties-of-good-tests.md` | Properties of good tests | Isolated, deterministic, fast, behavioral, readable | WF-3, WF-4 |
| `../agentic-cookbook/cookbook/guidelines/testing/unit-test-patterns.md` | Unit test patterns | Arrange-Act-Assert, one concept per test | WF-3 |
| `../agentic-cookbook/cookbook/guidelines/testing/flaky-test-prevention.md` | Flaky test prevention | No shared state, no timing, no real network in unit tests | WF-3 |
| `../agentic-cookbook/cookbook/guidelines/testing/test-data.md` | Test data | Builder pattern, no magic fixtures | WF-3 |
| `../agentic-cookbook/cookbook/guidelines/testing/the-testing-workflow.md` | Testing workflow | Write tests alongside code, validate with mutation testing | WF-3, WF-4 |

### Opt-In Concerns (Ask the User)

These concerns apply to many but not all features. Claude Code MUST ask the user about each one during planning. The "Default" column indicates the starting assumption, but the user's answer overrides it.

| File | Guideline | Summary | Default | Prompt Template | Workflow Phases |
|------|-----------|---------|---------|-----------------|-----------------|
| `../agentic-cookbook/cookbook/guidelines/ui/always-show-progress.md` | Show progress | Determinate or indeterminate progress for async work | Opt-in | "Does this feature involve async operations that need progress indication?" | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/logging/logging.md` | Instrumented logging | Structured logging for all components and flows | Opt-in | "This feature will include structured logging. Any components that should be excluded?" | WF-2, WF-3, WF-4 |
| `../agentic-cookbook/cookbook/guidelines/platform/deep-linking.md` | Deep linking | All significant views must be deep linkable | Ask | "Should the views in this feature be deep linkable?" | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/platform/shortcuts-and-automation.md` | Scriptable/automatable | Components scriptable via platform mechanisms | Opt-out | "Does this feature need scripting/automation support (Shortcuts, intents)?" | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/accessibility/accessibility.md` | Accessibility | Platform accessibility APIs from day one | Opt-in | "This feature will include full accessibility support. Any constraints?" | WF-2, WF-3, WF-4 |
| `../agentic-cookbook/cookbook/guidelines/internationalization/localization.md` | Localizability | All user-facing strings localizable | Opt-in | "This feature will use localized strings. Confirm or opt out." | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/internationalization/rtl-support.md` | RTL layout | Support right-to-left languages | Opt-in | "This feature will support RTL layouts. Confirm or opt out." | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/accessibility/accessibility.md` | Accessibility display options | Respond to reduced motion, high contrast, etc. | Opt-in | "This feature will respect accessibility display options. Confirm or opt out." | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/security/privacy.md` | Privacy/security | Data minimization, secure storage, no PII logging | Opt-in | "Does this feature collect, store, or transmit user data?" | WF-2, WF-3, WF-5 |
| `../agentic-cookbook/cookbook/guidelines/feature-management/feature-flags.md` | Feature flags | All features gated behind feature flags | Opt-in | "This feature will be gated behind a feature flag. Confirm or opt out." | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/logging/analytics.md` | Analytics | Significant user actions instrumented | Ask | "Which user actions in this feature should be tracked for analytics?" | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/feature-management/ab-testing.md` | A/B testing | Variant assignment support | Opt-out | "Does this feature need A/B testing / experimentation support?" | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/feature-management/debug-mode.md` | Debug mode | Debug panel entries for flags, analytics, experiments | Opt-in | "This feature will include debug panel entries. Confirm or opt out." | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/testing/property-based-testing.md` | Property-based testing | For parsers, serializers, data transformers | Ask | "Does this feature include data transformations that would benefit from property-based testing?" | WF-2, WF-3 |
| `../agentic-cookbook/cookbook/guidelines/testing/mutation-testing.md` | Mutation testing | Validate tests catch bugs | Ask | "Should we run mutation testing to validate test quality?" | WF-4 |
| `../agentic-cookbook/cookbook/guidelines/testing/security-testing.md` | Security testing | SAST, dependency scanning | Ask | "Should we run security scans (Semgrep, dependency audit)?" | WF-4 |
| `../agentic-cookbook/cookbook/guidelines/database-design/sqlite-best-practices.md` | SQLite best practices | Schema design, performance, sync, PRAGMA settings | Ask | "Does this feature use SQLite? If so, the SQLite best practices guideline covers schema design, performance, sync, and operations." | WF-2, WF-3 |

## How to Use This Checklist

### During Code Planning (WF-2)

1. Claude Code reads this checklist
2. For each "Always" item: note it as applicable without asking
3. For each "Opt-in" item: inform the user it will be included, ask for confirmation or opt-out
4. For each "Opt-out" item: ask the user if they want to opt in
5. For each "Ask" item: ask the user the prompt template question
6. Record all decisions in the plan document

### During Code Implementation (WF-3)

1. Apply all "Always" items automatically
2. Apply all opted-in items from the planning phase
3. Skip all opted-out items
4. If a new concern surfaces during implementation, ask the user before proceeding

### During Code Verification (WF-4)

1. Verify all "Always" items are correctly implemented
2. Verify all opted-in items are correctly implemented
3. Confirm opted-out items were not accidentally included
4. Run applicable testing tools (mutation testing, security scanning) based on opt-in decisions

### During Code Review (WF-5)

1. Review against all applicable guidelines
2. Flag any opted-in items that appear missing or incomplete
3. Flag any guideline violations in "Always" items

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-27 | Initial checklist |
| 1.1.0 | 2026-03-29 | Replace domain URLs with file paths |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial creation |
| 1.1.0 | 2026-03-29 | Mike Fullerton | Replace domain URLs with file paths for pipeline compatibility |
