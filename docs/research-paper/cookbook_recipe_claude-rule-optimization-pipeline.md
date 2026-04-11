---
id: aa81d10d-38d1-40d4-8be4-212b043e6410
title: "Claude Rule Optimization Pipeline"
domain: agentic-cookbook://recipes/developer-tools/claude/claude-rule-optimization-pipeline
type: recipe
version: 1.0.0
status: draft
language: en
created: 2026-03-30
modified: 2026-03-30
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Four-phase pipeline for auditing, optimizing, validating, and reporting on Claude Code rule file context efficiency."
platforms:
  - macos
  - linux
  - windows
tags:
  - claude-code
  - rules
  - optimization
  - context-efficiency
  - pipeline
depends-on: []
related:
  - agentic-cookbook://ingredients/developer-tools/claude/yolo-mode
  - agentic-cookbook://recipes/autonomous-dev-bots/pr-review-pipeline
references:
  - https://code.claude.com/docs/en/best-practices
approved-by: "approve-artifact v1.0.0"
approved-date: "2026-04-04"
---

# Claude Rule Optimization Pipeline

## Overview

Claude Code rule files in `.claude/rules/` are injected into the system prompt on every turn — not just at session start. A 200-line rule costs 200 lines × N turns per session. The agentic-cookbook's own rules went from 381 lines / 17,689 bytes per turn to 10 lines / 358 bytes — a 97% reduction — by applying a systematic optimization pipeline.

This recipe codifies that pipeline into four repeatable phases:

1. **Audit** — inventory rules, measure per-turn cost, detect waste
2. **Optimize** — propose and apply context-reduction strategies
3. **Validate** — verify behavioral preservation and run lint checks
4. **Report** — produce before/after metrics

The pipeline is sequential: each phase gates the next. Phase 2 (Optimize) requires explicit user confirmation before modifying any files — rule files are behavioral guardrails and MUST NOT be changed autonomously.

## Behavioral Requirements

### Phase 1: Audit

- **audit-inventory-all-rules**: The pipeline MUST inventory every `.md` file in `.claude/rules/` (and `rules/` if present), recording the file path, line count, and byte size of each.
- **audit-measure-per-turn-cost**: The pipeline MUST calculate the aggregate per-turn cost: the sum of lines and bytes across all rule files that load without `globs` restrictions. Rules with `globs` frontmatter that would not match a generic file context MUST be excluded from the per-turn total.
- **audit-detect-duplication**: The pipeline MUST compare all rule files pairwise and identify paragraphs, list items, or sections that express the same constraint. A finding MUST include the overlapping text and both file locations.
- **audit-detect-ungated-rules**: The pipeline MUST flag any rule file that applies only to a specific file pattern (identifiable by content referencing specific directories or file types) but lacks `globs` frontmatter.
- **audit-detect-mandatory-reads**: The pipeline MUST identify every instruction in rule files that mandates reading external files (patterns: "read", "load", "review", "check" followed by a file path or glob). Each finding MUST record the rule file, the instruction, and the referenced file paths.

### Phase 2: Optimize

- **optimize-propose-before-apply**: The pipeline MUST present all proposed optimizations to the user and wait for explicit confirmation before modifying any files. Each proposal MUST state what will change, the expected per-turn cost reduction, and any behavioral impact.
- **optimize-consolidate-overlaps**: When audit-detect-duplication found overlapping content, the pipeline MUST propose consolidating into a single rule file or extracting shared content to a referenced file. The proposal MUST specify which file retains the content and which files get trimmed.
- **optimize-add-globs-scoping**: For each rule flagged by audit-detect-ungated-rules, the pipeline MUST propose adding `globs` frontmatter with the narrowest pattern that covers the rule's intended scope.
- **optimize-extract-to-skills**: When a rule file exceeds 200 lines or contains workflow content (multi-step procedures, checklists, evaluation criteria), the pipeline SHOULD propose extracting that content to an on-demand skill, replacing it with a one-line skill pointer in the rule.
- **optimize-deduplicate-must-nots**: The pipeline MUST scan each rule's MUST NOT section and flag items that restate constraints already expressed imperatively in the rule body. The proposal MUST list each redundant item with the body line it duplicates.
- **optimize-inline-summaries**: When audit-detect-mandatory-reads found external files with a frontmatter-to-content ratio exceeding 50%, the pipeline SHOULD propose replacing the mandatory read with an inline summary and an optional file path for reference.

### Phase 3: Validate

- **validate-behavioral-preservation**: After optimizations are applied, the pipeline MUST verify that every behavioral constraint from the original rules is present in the optimized output. The pipeline MUST enumerate each original MUST, MUST NOT, and SHOULD constraint and confirm its presence (exact or equivalent) in the optimized files.
- **validate-lint-each-rule**: The pipeline MUST run the lint-rule checklist (all C-series, B-series, R-series, and O-series checks) against each optimized rule file. Any FAIL result MUST block the pipeline from proceeding to Phase 4 until resolved.
- **validate-measure-reduction**: The pipeline MUST re-measure per-turn cost using the same method as audit-measure-per-turn-cost and calculate the percentage reduction from the audit baseline.

### Phase 4: Report

- **report-produce-artifact**: The pipeline MUST produce a report file at `.claude/rule-optimization-report.md` containing: timestamp, before metrics (from Phase 1), after metrics (from Phase 3), percentage reduction, list of changes applied, lint results per file, and any constraints that could not be optimized further.
- **report-idempotent**: Running the pipeline again on already-optimized rules MUST produce a report showing no changes needed rather than making unnecessary modifications.

### Cross-Phase

- **sequential-gating**: Phases MUST execute in order: 1 → 2 → 3 → 4. A phase MUST NOT start until the previous phase completes successfully.
- **human-gate-before-writes**: The pipeline MUST NOT modify any rule file without explicit user confirmation. Phases 1 and 4 are read-only. Phase 2 requires confirmation. Phase 3 re-validates after writes.

## Pipeline Outcomes

| Outcome | Description | Next Action |
|---------|-------------|-------------|
| Optimized | Rules had measurable waste; optimizations applied, validated, reported | User reviews report, commits changes |
| Already Optimal | All rules pass audit with no actionable findings | Report confirms current state is clean |
| Partially Optimized | Some optimizations applied, others declined or infeasible | Report lists applied and skipped items |
| Validation Failed | Optimizations broke a behavioral constraint or lint check | Pipeline halts; user must fix or revert |

## Metrics

| Metric | ID | Unit | Collected In |
|--------|----|------|-------------|
| Per-turn cost (lines) | `per-turn-lines` | integer | Audit, Validate |
| Per-turn cost (bytes) | `per-turn-bytes` | integer | Audit, Validate |
| Rule file count | `rule-count` | integer | Audit, Validate |
| Mandatory external reads | `mandatory-reads` | integer | Audit, Validate |
| Duplication ratio | `duplication-ratio` | percentage | Audit |
| Ungated rule count | `ungated-count` | integer | Audit |
| Redundant MUST NOT count | `redundant-must-nots` | integer | Audit |
| Frontmatter-heavy refs | `high-metadata-refs` | integer | Audit |
| Reduction percentage | `reduction-pct` | percentage | Validate |

## Appearance

The pipeline's visible output is the report file at `.claude/rule-optimization-report.md`:

- **Heading structure**: H1 title, H2 per section (Timestamp, Before Metrics, After Metrics, Reduction, Changes Applied, Lint Results, Notes)
- **Metrics tables**: Markdown tables with columns: Metric | Before | After | Change
- **Changes list**: Bulleted list, one item per optimization applied, with file path and description
- **Lint results**: One H3 per rule file, followed by the lint-rule checklist results (PASS/WARN/FAIL per check)

## States

| State | How to detect | Behavior |
|-------|---------------|----------|
| Auditing | Phase 1 output being produced | Read-only inventory and measurement; no user interaction required |
| Awaiting Confirmation | Phase 2 proposals presented | Pipeline paused; user must confirm, decline, or selectively approve optimizations |
| Optimizing | User confirmed; files being modified | Rule files updated per approved proposals |
| Validating | Phase 3 checks running | Behavioral preservation enumeration and lint-rule checks; read-only |
| Reporting | Phase 4 report being written | Report file created at `.claude/rule-optimization-report.md` |
| Complete | Report file exists; pipeline finished | No further action; user reviews report |
| Failed | Validation found missing constraint or lint FAIL | Pipeline halted; user must fix or revert before re-running |

## Accessibility

Not applicable — CLI pipeline, no visual UI.

## Conformance Test Vectors

| ID | Requirements | Input | Expected |
|----|-------------|-------|----------|
| rop-001 | audit-inventory-all-rules | `.claude/rules/` with 3 files (50, 100, 200 lines) | Inventory lists all 3 with correct line/byte counts |
| rop-002 | audit-measure-per-turn-cost | 2 ungated rules (100 lines each), 1 globs-scoped rule (50 lines) | Per-turn cost = 200 lines (only ungated rules counted) |
| rop-003 | audit-detect-duplication | 2 rules with identical "Do not skip testing" paragraph | Finding identifies the duplicate with both file paths and matching text |
| rop-004 | audit-detect-ungated-rules | Rule containing "When editing files in `.claude/skills/`" but no globs frontmatter | Flagged as ungated; suggested glob: `.claude/**` |
| rop-005 | audit-detect-mandatory-reads | Rule with "Read ALL 18 principle files before planning" | Finding lists the instruction and identifies 18 referenced files |
| rop-006 | optimize-propose-before-apply | Phase 2 with 3 optimization proposals | All 3 presented to user; no files modified until user confirms |
| rop-007 | optimize-consolidate-overlaps | 2 rules with 40% overlapping content | Proposal specifies which rule retains content, which gets trimmed, expected line reduction |
| rop-008 | optimize-add-globs-scoping | Rule for skill authoring without globs | Proposal adds `globs: .claude/skills/**` frontmatter |
| rop-009 | optimize-extract-to-skills | Rule with 250 lines including a 150-line evaluation checklist | Proposal extracts checklist to a skill, replaces with 1-line pointer |
| rop-010 | optimize-deduplicate-must-nots | Rule body says "You MUST NOT skip Phase 2"; MUST NOT section repeats "Do not skip Phase 2" | Redundant MUST NOT item flagged with body line reference |
| rop-011 | optimize-inline-summaries | Rule mandating read of file that is 65% frontmatter | Proposal replaces mandatory read with inline summary |
| rop-012 | validate-behavioral-preservation | Original has 8 MUST constraints; optimized has 8 equivalent constraints | All 8 mapped and confirmed |
| rop-013 | validate-behavioral-preservation | Original has 8 MUST constraints; optimized has 7 | Validation fails; missing constraint identified |
| rop-014 | validate-lint-each-rule | Optimized rule with vague directive "handle errors appropriately" | Lint FAIL on R04; pipeline blocks until fixed |
| rop-015 | validate-measure-reduction | Before: 381 lines / 17,689 bytes; After: 10 lines / 358 bytes | Reduction: 97.4% lines, 98.0% bytes |
| rop-016 | report-produce-artifact | Completed pipeline run | `.claude/rule-optimization-report.md` exists with all required sections |
| rop-017 | report-idempotent | Pipeline run on rules that already pass all checks | Report says "No optimizations needed"; zero files modified |
| rop-018 | sequential-gating | Attempt to run Phase 3 before Phase 2 completes | Pipeline refuses; error indicates Phase 2 must complete first |
| rop-019 | human-gate-before-writes | Phase 2 with proposals; user declines all | Zero files modified; pipeline proceeds to Phase 4 with "no changes applied" report |

## Edge Cases

- **Empty rules directory**: `.claude/rules/` exists but contains no `.md` files. The pipeline MUST complete Phase 1 with zero metrics and skip Phases 2–3, producing a Phase 4 report that says "No rules found."
- **Single rule, already optimal**: One rule file under 50 lines, no duplication, has globs, clean MUST NOTs. The pipeline MUST complete all 4 phases, with Phase 2 reporting "No optimizations proposed."
- **Non-markdown files**: `.claude/rules/` may contain `.json`, `.yaml`, `.sh`, or other files. The pipeline MUST ignore non-`.md` files during inventory.
- **Broken file references**: A rule mandates reading a file that no longer exists. The audit MUST flag this as a separate finding (broken reference) distinct from optimization concerns.
- **Overly broad globs**: A rule has `globs: **` (matches everything, effectively ungated). The pipeline MUST treat this the same as no globs and suggest narrowing.
- **Circular references**: Rule A says "see rule B" and rule B says "see rule A." The deduplication check MUST handle this without infinite loops.
- **Custom rule paths**: Some projects put rules in non-standard paths referenced from `CLAUDE.md`. The pipeline SHOULD accept an optional path argument to scan additional directories.
- **Very large single rule (500+ lines)**: The pipeline MUST still complete successfully and SHOULD propose splitting into a minimal always-on section plus one or more skills, identifying natural section boundaries.
- **User declines all optimizations**: Phase 2 proposes changes, user declines everything. Pipeline MUST proceed to Phase 4 with a report documenting the proposals and the decision to decline.
- **Sensitive content in rules**: The report MUST NOT include literal file content that might expose credentials or internal paths beyond what is necessary to describe the optimization.

## Deep Linking

Not applicable — CLI pipeline, not a navigable resource.

## Localization

Not applicable — CLI pipeline with no user-facing strings.

## Accessibility Options

Not applicable — CLI pipeline.

## Feature Flags

Not applicable — the pipeline is invoked explicitly, not gated.

## Analytics

Not applicable — local CLI pipeline, no telemetry.

## Privacy

- **Data collected**: None
- **Storage**: Report file stored locally at `.claude/rule-optimization-report.md`
- **Transmission**: No data leaves the device
- **Retention**: Report persists until manually deleted or overwritten by next pipeline run

## Logging

Not applicable — the pipeline produces its output via the report file, not log messages.

## Platform Notes

- **macOS/Linux**: Rule files in `.claude/rules/` follow standard POSIX paths. File size measured with `wc -c`, line count with `wc -l`.
- **Windows**: Rule files use the same `.claude/rules/` path relative to the project root. File operations work via Git Bash, WSL, or any POSIX-compatible shell.

## Design Decisions

- **Guided pipeline with human gate, not fully autonomous**: Rule files are behavioral guardrails — they control what Claude does and does not do. Autonomously modifying guardrails risks weakening safety constraints. The pr-review-pipeline is autonomous because it only reads and comments; this pipeline writes, so user confirmation is required before any modification. **Approved**: pending
- **Report file as primary output, not PR comment**: The report is useful as a standalone artifact that can be committed alongside optimized rules. Not all optimization runs happen in a PR context (e.g., local development, initial setup). A future extension can post the report as a PR comment when the pipeline runs in CI. **Approved**: pending
- **Reuse lint-rule O-series checks rather than defining new validation logic**: The O-series checks already encode optimization criteria from the rule-optimization research. Reusing them avoids duplication and ensures the pipeline and linter stay in sync. **Approved**: pending
- **Measure per-turn cost in both lines and bytes**: Lines are human-readable and easy to reason about. Bytes are the actual context window cost. Both metrics appear throughout the optimization research. Reporting both gives complementary perspectives. **Approved**: pending
- **Enumeration-based behavioral validation**: Each original MUST/MUST NOT/SHOULD constraint gets mapped to its optimized equivalent. If a constraint cannot be mapped, validation fails with a specific gap identified. This is more reliable than abstract semantic comparison. **Approved**: pending
- **Pipeline state in conversation context, not on disk**: Unlike `/cookbook-next` which spans many turns and benefits from disk-persisted state, this pipeline runs in a single focused session (typically 10–20 turns). Conversation context is sufficient. If interrupted, the pipeline restarts from Phase 1 — safe because Phase 1 is read-only and Phase 2 requires re-confirmation. **Approved**: pending

## Compliance

| Check | Status | Category |
|-------|--------|----------|
| [safe-defaults](agentic-cookbook://compliance/user-safety#safe-defaults) | passed | User Safety — pipeline defaults to confirmation before modifying rules |
| [data-minimization](agentic-cookbook://compliance/privacy-and-data#data-minimization) | passed | Privacy — report contains only metrics and optimization descriptions, no PII |
| [secure-log-output](agentic-cookbook://compliance/security#secure-log-output) | passed | Security — report does not include sensitive rule content verbatim |
| [idempotent-operations](agentic-cookbook://compliance/reliability#idempotent-operations) | passed | Reliability — re-running on optimized rules produces same result |
| [fault-tolerance](agentic-cookbook://compliance/reliability#fault-tolerance) | passed | Reliability — handles missing directories, empty rules, malformed frontmatter |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-30 | Mike Fullerton | Initial creation |
