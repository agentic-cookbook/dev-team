---
id: c3f7a9e2-1b5d-4c8e-a2d6-9e4f1c3b7a5d
title: "PR Review Pipeline"
domain: agentic-cookbook://recipes/autonomous-dev-bots/pr-review-pipeline
type: recipe
version: 0.1.0
status: wip
language: en
created: 2026-03-28
modified: 2026-03-28
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Three-phase automated review pipeline for cookbook contributions — review, refactoring, evaluate — running on OpenClaw with GitHub App bot personas."
platforms: []
tags:
  - automation
  - review
  - ci
  - github
depends-on: []
related:
  - agentic-cookbook://workflows/code-review
  - agentic-cookbook://compliance/best-practices
references:
  - https://docs.github.com/en/rest/checks/runs
  - https://docs.github.com/en/apps/creating-github-apps
  - https://vale.sh
  - https://github.com/DavidAnson/markdownlint-cli2
  - https://docs.openclaw.ai
approved-by: "approve-artifact v1.0.0"
approved-date: "2026-04-04"
---

# PR Review Pipeline

An autonomous dev bot that reviews pull requests to the agentic cookbook. Three sequential phases — Review, Refactoring & Scoping, Evaluate — each run by a distinct GitHub App bot persona. The pipeline runs on OpenClaw, triggered by GitHub webhooks, and posts structured PR reviews that gate merging.

## Overview

When a contributor submits a PR to the cookbook (via `/contribute-to-cookbook` or manually), this pipeline runs automatically:

1. **Phase 1: Review** — structural validation, prose quality, content completeness, convention compliance. Fixes what it can (up to 3 iterations), rejects what it cannot.
2. **Phase 2: Refactoring & Scoping** — placement analysis, granularity assessment, overlap detection against all cookbook content, refactoring proposals.
3. **Phase 3: Evaluate** — value scoring, risk assessment, ecosystem research, recommendation to human reviewer.

Phases run **sequentially**. If a phase rejects, subsequent phases do not run. Each phase posts a GitHub PR review (Approve or Request Changes) under its own bot identity.

The PR is unmergeable until all three phase bots approve AND a human reviewer approves.

## Behavioral Requirements

### Trigger & Execution

- **webhook-trigger**: The pipeline MUST trigger when a GitHub `pull_request` event (opened, synchronize, reopened) is received at the OpenClaw webhook endpoint (`POST /hooks/agent`).
- **poll-fallback**: The pipeline SHOULD fall back to polling via `gh pr list` on a cron schedule if webhooks are unavailable.
- **isolated-session**: Each pipeline run MUST execute in an isolated OpenClaw agent session to prevent cross-contamination between PR reviews.
- **sequential-phases**: Phases MUST run sequentially: Phase 1 → Phase 2 → Phase 3.
- **short-circuit**: The pipeline MUST stop and not run subsequent phases if a phase posts "Request Changes".
- **rerun-on-update**: The pipeline MUST rerun from Phase 1 when new commits are pushed to the PR branch.

### Contributor Preferences

- **fix-preference-prompt**: The `/contribute-to-cookbook` skill MUST ask the contributor before PR submission: "If the review pipeline finds fixable issues, would you like us to fix them automatically, or review each change?"
- **fix-preference-default**: The default preference MUST be "fix automatically".
- **fix-preference-storage**: The preference MUST be stored in the PR body as metadata (e.g., `<!-- fix-preference: auto -->` or `<!-- fix-preference: review -->`).
- **fix-preference-honored**: The refactoring agent MUST honor the stored preference — committing directly for "auto", posting suggested changes for "review".

### Phase 1: Review

- **structural-validation**: Phase 1 MUST run all applicable checks from `/validate-cookbook` (frontmatter integrity, content structure, cross-references, indexes, file placement).
- **markdownlint**: Phase 1 MUST run markdownlint-cli2 and auto-fix fixable issues.
- **vale-cookbook-style**: Phase 1 MUST run Vale with the custom Cookbook style checking for: vague terms, ambiguous quantifiers, hedging, implicit references, casual RFC 2119 keywords, double negatives, ambiguous pronouns.
- **llm-clarity-pass**: Phase 1 MUST run an LLM-based clarity analysis checking for: ambiguous antecedents, implicit assumptions, terminology inconsistency across sections, self-containment of sections, unresolved references.
- **content-completeness**: Phase 1 MUST verify all required sections are present and non-empty (or explicitly N/A with reason), MUST requirements have test vectors, appearance values are concrete, logging messages are exact strings, platform notes cover all declared platforms.
- **convention-compliance**: Phase 1 MUST verify named requirements use kebab-case, RFC 2119 keywords are used correctly, domain identifiers match file paths, template variables are used where appropriate.
- **fix-loop**: Phase 1 MUST attempt to fix issues in a loop, max 3 iterations. Each iteration: fix auto-fixable issues (markdownlint, frontmatter), attempt LLM fixes (prose rewrites, inferrable values), re-validate. After 3 iterations, remaining issues are flagged as unfixable.
- **fix-categorization**: Each issue MUST be categorized as: auto-fixable (deterministic tool fix), LLM-fixable (LLM can infer the correction), or human-required (needs contributor or reviewer decision).

### Phase 2: Refactoring & Scoping

- **placement-analysis**: Phase 2 MUST verify the recipe is in the correct directory for its type and that the domain identifier matches the file path.
- **granularity-check**: Phase 2 MUST assess whether the recipe covers exactly one coherent concept. Flag recipes with more than 15 MUST requirements or more than 8 states as potentially too broad. Flag recipes with fewer than 3 requirements as potentially too narrow.
- **overlap-detection**: Phase 2 MUST compare the new/changed content against ALL existing cookbook content (principles, guidelines, and recipes) for conceptual overlap. This includes: identical or near-identical requirement names, duplicate behavioral descriptions, redefinition of concepts that have their own specs.
- **ecosystem-fit**: Phase 2 MUST check whether existing recipes should reference the new content (backlinks), whether new terminology conflicts with established terms, and whether relevant guidelines are referenced.
- **refactoring-proposal**: When overlap or scope issues are found, Phase 2 MUST produce a concrete refactoring proposal specifying exact changes: which requirements to move, merge, or split, and which files are affected.
- **granular-assessment**: Refactoring proposals MUST be per-requirement/section, not per-recipe. A recipe with 10 parts where 2 are valuable MUST have a proposal that extracts those 2.

### Phase 3: Evaluate

- **value-scoring**: Phase 3 MUST score the contribution on: novelty (fills a gap), demand signal (multiple projects would use this), quality (how clean was the Phase 1/2 pass), completeness (platform coverage, test vector thoroughness), ecosystem integration (quality of depends-on/related links).
- **risk-scoring**: Phase 3 MUST assess: breaking changes to existing content, conflicts with engineering principles, scope appropriateness for the cookbook, contributor track record (first-time vs established).
- **external-research**: Phase 3 MUST research beyond the repo: search GitHub for similar patterns, check platform SDK documentation to see if the concept is built-in, assess whether the pattern is well-established or novel.
- **recommendation**: Phase 3 MUST produce a structured recommendation: value (HIGH/MEDIUM/LOW), confidence (HIGH/MEDIUM/LOW), recommendation (ACCEPT/ACCEPT WITH REFACTORING/PARTIAL ACCEPT/REJECT), with per-section rationale.
- **human-escalation**: Phase 3 MUST post its recommendation as a PR review. The human reviewer makes the final decision — Phase 3 recommends but never merges.

### Rejection & Appeal

- **rejection-format**: A rejecting phase MUST post a PR review with "Request Changes" status, including per-issue explanation of what failed and why.
- **branch-protection**: The repository MUST be configured to require approval from all three phase bot GitHub Apps plus a human reviewer before merging is allowed.
- **appeal-process**: If a contributor replies to a rejection comment disputing the decision, the pipeline MUST flag the PR for human review rather than re-running automatically.
- **rerun-after-fix**: After the refactoring agent applies fixes, the pipeline MUST rerun from Phase 1 on the updated content.

### Refactoring Agent

- **dedicated-persona**: All automated fixes and refactoring MUST be applied by a single dedicated refactoring agent with its own GitHub App identity, distinct from the three phase bots.
- **fix-or-suggest**: The refactoring agent MUST commit directly if the contributor chose "fix automatically", or post GitHub suggested changes if the contributor chose "review each change".
- **scope-of-fixes**: The refactoring agent handles fixes from all phases: structural fixes from Phase 1, refactoring proposals approved by the human reviewer from Phase 2.

## Pipeline Outcomes

| Outcome | Description | Next action |
|---------|-------------|-------------|
| Accept | Passes all phases, high value | Human reviewer approves, PR is mergeable |
| Accept with refactoring | Has value, needs structural changes | Refactoring agent applies changes, pipeline reruns |
| Partial accept | Some parts valuable, others not | Proposal extracts good parts, rejects rest. Human decides. |
| Reject | No parts meet the bar | Detailed per-section rationale posted. Contributor can appeal. |
| Reject with appeal | Contributor disputes rejection | Human reviewer evaluates the appeal |

## GitHub Apps

Four GitHub App identities are required:

| App | Purpose | Posts as |
|-----|---------|---------|
| Cookbook Review Bot | Phase 1: structural, prose, completeness, conventions | `@cookbook-review-bot[bot]` |
| Cookbook Scope Bot | Phase 2: placement, granularity, overlap, ecosystem fit | `@cookbook-scope-bot[bot]` |
| Cookbook Eval Bot | Phase 3: value, risk, recommendation | `@cookbook-eval-bot[bot]` |
| Cookbook Fix Bot | Refactoring agent: applies all automated fixes | `@cookbook-fix-bot[bot]` |

Each app requires:
- `checks:write` permission (to create check runs)
- `pull_requests:write` permission (to post reviews and suggested changes)
- `contents:write` permission (Fix Bot only — to push commits)
- Private key PEM stored on the execution Mac
- Installation tokens generated per run via `gh-token` extension

## Execution Platform

### OpenClaw Configuration

- **Trigger**: GitHub webhook configured to POST `pull_request` events to `http://<mac-ip>:18789/hooks/agent`
- **Fallback**: OpenClaw cron job polling `gh pr list --repo agentic-cookbook/cookbook --state open` every 5 minutes
- **Session**: Isolated session per PR review run
- **Model**: Claude Opus for Phase 2 (overlap/scoping requires strong reasoning) and Phase 3 (evaluation). Sonnet for Phase 1 (structural checks are more mechanical).
- **Timeout**: 48 hours max per run
- **Tools**: Shell access to `gh`, `git`, `vale`, `markdownlint-cli2`

### Conversational Control

The pipeline is controllable via chat (any connected channel — Slack, Discord, iMessage):

- "What's the status of PR #42?" → shows current phase, findings so far
- "Re-run review on PR #42" → triggers a fresh pipeline run
- "Show open PRs waiting for my review" → lists PRs that passed all phases and need human approval
- "Approve refactoring on PR #42" → human approves the refactoring proposal, triggers refactoring agent

### External Tools

| Tool | Purpose | Installation |
|------|---------|-------------|
| `gh` | GitHub CLI for PR operations, reviews, comments | `brew install gh` |
| `vale` | Prose linting with custom Cookbook style | `brew install vale` |
| `markdownlint-cli2` | Structural markdown linting | `npm install -g markdownlint-cli2` |
| `gh-token` | GitHub App installation token generation | `gh extension install Link-/gh-token` |

## Custom Vale Style: Cookbook

A custom Vale style (`vale/styles/Cookbook/`) with rules optimized for LLM readability:

| Rule | What it flags |
|------|---------------|
| `VagueTerms.yml` | "appropriate", "suitable", "reasonable", "as needed", "standard", "proper", "adequate" |
| `AmbiguousQuantifiers.yml` | "some", "most", "usually", "often", "sometimes", "generally", "typically", "normally" |
| `Hedging.yml` | "might want to", "consider using", "it may be helpful", "you could", "perhaps", "arguably" |
| `ImplicitReferences.yml` | "as mentioned above", "the usual approach", "handle this correctly", "see above", "as before" |
| `CasualRFC2119.yml` | Lowercase "must", "should", "shall" in requirement sections that are not bolded RFC 2119 keywords |
| `DoubleNegatives.yml` | "must not fail to", "should not avoid", "do not prevent" |
| `AmbiguousPronouns.yml` | "it should", "this must", "that will" at sentence start without clear antecedent in requirement sections |

## LLM Clarity Pass

Beyond Vale's deterministic rules, the LLM clarity pass checks for:

- **Ambiguous antecedents**: pronouns whose referent requires re-reading prior context
- **Implicit assumptions**: statements that assume knowledge not present in the document
- **Terminology drift**: a concept called X in one section and Y in another
- **Section isolation**: can each section be understood without reading the others?
- **Unresolved references**: mentions of concepts not defined or linked
- **Vague quantification in requirements**: "handle multiple items" (how many?) vs "handle 1-1000 items"

## Appearance

Not applicable — this is an automated pipeline with no visual UI.

## States

Not applicable — pipeline state is tracked through GitHub PR status checks and bot comments, not a visual state model.

## Accessibility

Not applicable — this pipeline interacts through GitHub's PR interface, which provides its own accessibility. Bot-posted review comments use plain markdown, inheriting GitHub's accessible rendering.

## Conformance Test Vectors

| ID | Requirements | Input | Expected |
|----|-------------|-------|----------|
| prp-001 | recipe-validation, frontmatter-check | PR adding a recipe with missing `id` field | Phase 1 rejects, posts review requesting fix |
| prp-002 | overlap-detection | PR adding a recipe with requirements duplicating an existing recipe | Phase 2 flags overlap, suggests consolidation |
| prp-003 | cross-reference-integrity | PR modifying a recipe domain without updating references | Phase 3 detects broken cross-references |
| prp-004 | short-circuit-rejection | PR failing Phase 1 | Phase 2 and 3 do not run |
| prp-005 | auto-fix-preference | PR with auto-fix enabled, fixable Phase 1 issue | Fix bot pushes corrected commit |

## Edge Cases

- **PR with multiple recipes**: run the pipeline once per changed recipe file, aggregate results into a single review per phase
- **PR modifying existing content only**: skip Phase 2 overlap detection for sections that didn't change; still check that modifications don't introduce new overlap
- **PR touching non-recipe files** (guidelines, principles): run Phase 1 and Phase 3 only; skip Phase 2 (scoping/refactoring is recipe-specific)
- **Contributor pushes during pipeline run**: cancel current run, restart from Phase 1 on the latest commit
- **GitHub App rate limits**: implement exponential backoff; if rate-limited during review posting, retry up to 3 times then log failure
- **OpenClaw goes offline**: GitHub webhook delivery retries for up to 8 hours; pending PRs will be picked up by the cron fallback when the Mac comes back online

## Logging

Subsystem: `pr-review-pipeline` | Category: `Pipeline`

| Event | Level | Message |
|-------|-------|---------|
| Pipeline started | info | `Pipeline: started for PR #{{pr_number}} on {{repo}}` |
| Phase completed | info | `Pipeline: phase {{phase}} completed — {{result}}` |
| Phase short-circuited | info | `Pipeline: skipping phase {{phase}} — prior phase rejected` |
| Fix bot committed | info | `Pipeline: fix bot pushed commit {{sha}} for PR #{{pr_number}}` |
| Rate limit hit | warning | `Pipeline: GitHub API rate limited — retrying in {{seconds}}s` |
| Pipeline failed | error | `Pipeline: failed for PR #{{pr_number}} — {{error}}` |

## Platform Notes

This pipeline runs on macOS via OpenClaw. It is not platform-portable — it depends on OpenClaw's daemon infrastructure, GitHub App webhooks, and Claude Code CLI availability on the host Mac.

## Design Decisions

**Decision**: Use OpenClaw as the execution platform rather than GitHub Actions or a standalone launchd script.
**Rationale**: OpenClaw is already installed on the execution Mac, provides daemon infrastructure (cron, webhooks, sessions), Claude integration, and conversational control. Avoids building custom daemon management.
**Approved**: yes

**Decision**: Four GitHub Apps (3 phase bots + 1 fix bot) rather than a single bot or GitHub Actions identity.
**Rationale**: Distinct bot personas make PR reviews visually clear — each phase appears as a different reviewer. The fix bot is separate because it writes code while the phase bots are read-only reviewers.
**Approved**: yes

**Decision**: Sequential phase execution (1 → 2 → 3) with short-circuit on rejection.
**Rationale**: Phase 1 fixes content before Phase 2 analyzes it (better to compare clean content). Phase 3 needs findings from both prior phases. Running all phases on content that fails basic structural checks wastes resources.
**Approved**: yes

**Decision**: LLM readability over human readability (no Flesch-Kincaid).
**Rationale**: Cookbook content is consumed by LLMs, not casual human readers. LLM readability means: explicit, unambiguous, no hedging, consistent terminology, self-contained sections. Traditional readability metrics penalize the precision that LLMs need.
**Approved**: yes

**Decision**: Fix preference asked before PR submission, default auto-fix.
**Rationale**: Most contributors want hands-off after submission. Power users who want control can opt into review-each. The choice is per-PR, stored as PR metadata.
**Approved**: yes

**Decision**: Contributor can appeal rejections by commenting on the PR.
**Rationale**: Automated review can be wrong. A simple appeal process (comment → human reviews) prevents valid contributions from being permanently blocked by false positives.
**Approved**: yes

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 0.1.0 | 2026-03-28 | Mike Fullerton | Initial recipe — captures all design decisions from planning session |
