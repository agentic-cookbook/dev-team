---
id: 7f72dfc4-21aa-458d-8b3f-590b735cfc4f
title: "Branching Strategy"
domain: agentic-cookbook://workflows/branching-strategy
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
  - branching-strategy
depends-on: []
related: 
  - agentic-cookbook://guidelines/code-quality/atomic-commits
references: []
---

# Branching Strategy

---
version: 1.0.0
status: draft
created: 2026-03-27
last-updated: 2026-03-27
author: claude-code
copyright: 2026 Mike Fullerton / Temporal
audience: claude-code
scope: [branching]
tags: [git, worktree, pr, branching, source-control]
dependencies:
  - workflow/code-review.md@1.0.0
---

## Overview

Defines the source control mechanics for Claude Code AI sessions in consuming projects. Every coding session operates in a git worktree with a draft PR opened immediately, commits made continuously, progress documented in PR comments, and the PR marked active only after code review (WF-5) passes.

This workflow wraps all other workflow phases — planning (WF-2), implementation (WF-3), verification (WF-4), and review (WF-5) all happen inside the worktree lifecycle defined here.

## Terminology

| Term | Definition |
|------|-----------|
| Worktree | A git worktree — a separate working directory linked to the same repository, allowing concurrent branch work without stashing or switching |
| Draft PR | A GitHub pull request in draft state — visible for discussion but not mergeable until marked ready |
| Session | A single Claude Code interaction that produces code changes |

## Inputs

- **Git repository**: The consuming project must be a git repo with a remote on GitHub
- **Main branch**: The branch to base work on (typically `main` or `master`)
- **Task description**: A clear description of the work to be done (issue, feature request, bug report)

## Phases

### Phase 1: Session Setup

**Entry criteria**: User has described the work to be done. The repo is clean on the main branch.

- **REQ-001**: Claude Code MUST create a new git worktree for each coding session using the pattern `../{project}-wt/{branch-name}`.
- **REQ-002**: Claude Code MUST create a descriptive branch name using the conventions:

  | Change type | Branch pattern | Example |
  |---|---|---|
  | New feature | `feature/<kebab-description>` | `feature/user-auth` |
  | Bug fix | `fix/<kebab-description>` | `fix/login-crash` |
  | Refactor | `refactor/<kebab-description>` | `refactor/auth-module` |
  | Spec/docs | `spec/<kebab-name>` | `spec/toolbar-buttons` |

- **REQ-003**: Claude Code MUST push the branch and open a draft PR on GitHub immediately after creating the worktree. The draft PR body MUST include:
  - Summary of the planned work
  - Reference to the originating issue (if any)
  - A note that this is an AI-assisted session

- **REQ-004**: All subsequent work MUST happen in the worktree directory, not the main working tree.

**Exit criteria**: Worktree exists, branch is pushed, draft PR is open on GitHub.

### Phase 2: Continuous Work

**Entry criteria**: Phase 1 complete. Worktree and draft PR exist.

- **REQ-005**: Claude Code MUST commit after every meaningful change. A meaningful change is one that brings the codebase from one consistent state to another — adding a function, fixing a test, updating a config file. Do not batch unrelated changes into a single commit.
- **REQ-006**: Claude Code MUST NOT leave uncommitted changes or untracked new files at any point during the session. After every tool invocation that modifies files, verify the working tree is clean.
- **REQ-007**: Commit messages MUST be descriptive and follow the project's commit message conventions. If no convention exists, use imperative mood: "Add user authentication endpoint", not "Added" or "Adding".
- **REQ-008**: Claude Code MUST push commits to the remote regularly — at minimum after every phase transition (planning complete, implementation milestone, verification pass) and SHOULD push after every commit.
- **REQ-009**: Claude Code MUST document progress as PR comments at significant milestones:
  - When planning is complete (WF-2 output)
  - When a major implementation milestone is reached
  - When blockers or design changes are discovered
  - When verification results are available (WF-4 output)
  - Comments SHOULD include context: what was decided, why, and what's next

- **REQ-010**: Claude Code SHOULD use PR comments to record design decisions, trade-offs considered, and rationale for non-obvious choices. This creates an audit trail for reviewers.

**Exit criteria**: All changes committed and pushed. PR comments document the session's progress.

### Phase 3: Review Gate

**Entry criteria**: Implementation (WF-3) and verification (WF-4) are complete. All changes committed and pushed.

- **REQ-011**: Claude Code MUST perform code review per WF-5 before marking the PR as ready.
- **REQ-012**: Claude Code MUST post a review summary as a PR comment, including:
  - Guideline checklist compliance status
  - Test coverage summary
  - Any issues found and how they were resolved
- **REQ-013**: After review passes, Claude Code MUST update the PR:
  - Update the PR description with a final summary of all changes
  - Mark the PR as ready for review (remove draft status)
- **REQ-014**: Claude Code SHOULD request human review if the project has designated reviewers.

**Exit criteria**: PR is marked ready for review with a complete description and review summary.

### Phase 4: Merge and Cleanup

**Entry criteria**: PR is approved (or auto-mergeable per project policy).

- **REQ-015**: Claude Code MUST use squash merge to main unless the project explicitly uses a different merge strategy.
- **REQ-016**: The squash commit message MUST summarize the entire change set, not just the last commit.
- **REQ-017**: After merge, Claude Code MUST clean up:
  1. Remove the worktree: `git worktree remove ../{project}-wt/{branch-name}`
  2. Pull main in the original working tree: `git -C /path/to/project pull`
  3. Delete the remote branch if not auto-deleted: `git push origin --delete {branch-name}`

**Exit criteria**: Main branch updated, worktree removed, remote branch deleted.

## Behavioral Requirements

- **REQ-018**: If the worktree creation fails (e.g., directory already exists), Claude Code MUST inform the user and suggest remediation (remove stale worktree, choose a different branch name).
- **REQ-019**: If a push fails due to remote rejection, Claude Code MUST NOT force-push without explicit user permission.
- **REQ-020**: If the session is interrupted (user ends the conversation), all work MUST already be committed and pushed — the zero-uncommitted-work policy (REQ-006) ensures no work is lost.

## Guideline Cross-Reference

This workflow references the shared [guideline-checklist.md](guideline-checklist.md).

| Phase | Checklist Items | Notes |
|-------|----------------|-------|
| Phase 2 | agentic-cookbook://guidelines/code-quality/atomic-commits (atomic commits) | Every commit is one logical change |
| Phase 3 | All opted-in items from WF-2 | Review verifies compliance |
| Phase 4 | agentic-cookbook://guidelines/code-quality/atomic-commits (atomic commits) | Squash merge produces one clean commit on main |

## Conformance Test Vectors

| ID | Requirements | Scenario | Expected |
|----|-------------|----------|----------|
| branch-001 | REQ-001 | New coding session starts | Worktree created at `../{project}-wt/{branch}` |
| branch-002 | REQ-003 | Worktree created | Draft PR opened on GitHub within the same phase |
| branch-003 | REQ-005 | Function added to a file | Commit created immediately with descriptive message |
| branch-004 | REQ-006 | After any file modification | `git status` shows clean working tree |
| branch-005 | REQ-006 | New file created | File is staged and committed, not left untracked |
| branch-006 | REQ-009 | Planning phase completes | PR comment posted summarizing the plan |
| branch-007 | REQ-009 | Design decision made during implementation | PR comment posted with decision and rationale |
| branch-008 | REQ-011, REQ-013 | All work complete, review passes | PR status changed from draft to ready |
| branch-009 | REQ-015 | PR approved | Squash merge to main |
| branch-010 | REQ-017 | After merge | Worktree removed, main pulled, remote branch deleted |
| branch-011 | REQ-018 | Worktree directory already exists | User informed, remediation suggested |
| branch-012 | REQ-019 | Push rejected by remote | User asked for permission before force-push |
| branch-013 | REQ-020 | Session interrupted mid-work | All changes already committed and pushed |

## Edge Cases

- **Stale worktree from previous session**: If `../{project}-wt/{branch}` already exists, check if it has uncommitted work. If yes, ask the user how to proceed. If clean, offer to remove and recreate.
- **Merge conflicts on main**: If main has advanced and the PR has conflicts, rebase the branch onto main. If conflicts are complex, ask the user before resolving.
- **Multiple concurrent sessions**: Different sessions MUST use different branch names. Branch naming conventions prevent collisions.
- **No GitHub remote**: If the project doesn't use GitHub, skip PR-related requirements (REQ-003, REQ-009, REQ-010, REQ-012, REQ-013, REQ-014) and commit locally only. Inform the user.

## Tool Notes

- **git**: Use `git worktree add` for isolation. Use `git status` after every file operation to verify clean state. Use `git push -u origin {branch}` on first push to set upstream tracking.
- **gh**: Use `gh pr create --draft` for draft PRs. Use `gh pr ready` to mark as ready. Use `gh pr comment` for progress notes. Use `gh pr merge --squash` for squash merge.
- **Claude Code**: The worktree is the working directory for the entire session. All file paths in tool calls should be relative to or within the worktree.

## Design Decisions

**Decision**: Use worktrees rather than branch switching.
**Rationale**: Worktrees keep the main working tree clean and available for other processes (e.g., consuming projects that read `../project/`). Branch switching risks leaving the main tree in a dirty state if a session is interrupted.
**Approved**: pending

**Decision**: Draft PR opened immediately, not after implementation.
**Rationale**: A draft PR from the start creates a place for documentation, discussion, and progress tracking. It also makes work visible to collaborators immediately.
**Approved**: pending

**Decision**: Zero uncommitted work policy enforced continuously.
**Rationale**: AI sessions can be interrupted at any time (context limit, user disconnect, error). If work is always committed and pushed, no code is ever lost.
**Approved**: pending

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-27 | Initial spec |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial creation |
