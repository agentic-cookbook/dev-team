---
name: configure-cookbook
version: "5.0.0"
description: "Manage agentic cookbook preferences and rule file. Toggle committing workflow, recipe prompts, contribution prompts."
argument-hint: "[--version]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(rm *), Bash(cp *), Bash(ls *), Bash(mkdir *), Bash(wc *), Bash(date *), AskUserQuestion
---

# Configure Agentic Cookbook v5.0.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `configure-cookbook v5.0.0` and stop — do not run the skill.

Otherwise, print `configure-cookbook v5.0.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (4.0.0), print:

> ⚠ This skill is running v5.0.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

Manage your cookbook preferences and rule installation. Use this to:

- Toggle committing workflow, recipe prompts, or contribution prompts
- Migrate from legacy static-copy installation to the minimal rule
- View pipeline status if a session is in progress
- Reinstall the rule after cookbook updates

## Usage

```
/configure-cookbook
```

## Step 1: Detect Current State

Check the current project for:

1. **Minimal rule**: Is `.claude/rules/cookbook.md` present? Is it the minimal version (~10 lines)?
2. **Manifest**: Does `.cookbook/manifest.json` exist? Read it for current state.
3. **Preferences**: Read `.cookbook/preferences.json` if it exists.
4. **Legacy files**: Are any old files present? (`authoring-ground-rules.md`, `auto-lint.md`, `PRINCIPLES-RULE.md`, `GUIDELINE-CONSUMER-RULE.md`, `RECIPE-CONSUMER-RULE.md`, `CONTRIBUTOR-RULE.md`, `skill-versioning.md`)
5. **Committing rule**: Is `.claude/rules/committing.md` present?
6. **Pipeline state**: Does `.cookbook/pipeline.json` exist? If so, read it.

Print the current state:

```
=== Cookbook Status ===
Rule: cookbook.md — minimal (<N> lines) / not installed / legacy detected
Committing: committing.md — installed / not installed
Preferences:
  Recipe prompts: enabled / disabled
  Contribution prompts: enabled / disabled
  Committing workflow: included / not included
```

If `.cookbook/pipeline.json` exists, also print:

```
Pipeline: <phase> — step <N> of <M> (<X> applicable, <Y> N/A so far)
Task: <task description>
```

**If legacy static files detected**: print a migration notice and proceed to Step 2.

**If cookbook.md is not installed and no legacy files exist**: print "Cookbook not installed. Run /install-cookbook first." and stop.

## Step 2: Migration (if needed)

If old static rule files are detected:

```
Legacy installation detected. The cookbook now uses a minimal rule (~10 lines)
plus on-demand pipeline skills. I'll remove old files and install the new rule.
```

Remove old files (only those that exist):
- `.claude/rules/authoring-ground-rules.md`
- `.claude/rules/auto-lint.md`
- `.claude/rules/PRINCIPLES-RULE.md`
- `.claude/rules/GUIDELINE-CONSUMER-RULE.md`
- `.claude/rules/RECIPE-CONSUMER-RULE.md`
- `.claude/rules/CONTRIBUTOR-RULE.md`
- `.claude/rules/skill-versioning.md`

Print which files were removed, then proceed to Step 3.

## Step 3: Preferences

Present current preferences and ask if the user wants to change them:

```
=== Cookbook Preferences ===

1. Recipe prompts: [enabled/disabled]
   During planning, search for matching recipes and ask if you want to see them.

2. Contribution prompts: [enabled/disabled]
   After implementation, ask if you want to contribute reusable patterns.

3. Committing workflow: [included/not included]
   Structured git workflow: worktrees, draft PRs, incremental commits.

Change any? (enter numbers to toggle, or "done" to skip)
```

Record all changes.

## Step 4: Apply Changes

### Committing workflow toggle

If the committing workflow preference changed:

- **Newly included**: Verify `../agentic-cookbook/` exists (use `ls ../agentic-cookbook/rules/committing.md`). If not found, print: "Cookbook not found at ../agentic-cookbook/. Cannot install committing rule." and skip this change. Otherwise, copy `../agentic-cookbook/rules/committing.md` to `.claude/rules/committing.md`.
- **Newly excluded**: Remove `.claude/rules/committing.md` if it exists.

### Rule file check

If `.claude/rules/cookbook.md` does not exist or is a legacy (non-minimal) version:

Write the minimal rule:

```markdown
# Cookbook

1. Confirm you are in the correct project before making changes.
2. Investigate unfamiliar content before overwriting.
3. Fix only what was asked — no unauthorized additions.
4. Do not skip Phase 2 (Make It Right).
5. Do not skip writing tests.
6. Do not optimize without evidence.

When planning or implementing features, use /cookbook-start.
```

## Step 5: Update Manifest and Preferences

Write `.cookbook/manifest.json`:

```json
{
  "generated": "<ISO 8601 timestamp>",
  "generator_version": "5.0.0",
  "source_cookbook": "../agentic-cookbook",
  "rule_type": "minimal",
  "preferences": {
    "show_recipe_prompts": true/false,
    "show_contribution_prompts": true/false,
    "committing_workflow": true/false
  }
}
```

Write `.cookbook/preferences.json` with the user's current preferences.

## Step 6: Update CLAUDE.md

If `CLAUDE.md` has an `## Agentic Cookbook` section, update it:

```markdown
## Agentic Cookbook

This project uses the [agentic-cookbook](https://github.com/agentic-cookbook/cookbook).

- **Cookbook path**: `../agentic-cookbook/`
- **Rule**: `cookbook.md` (minimal, ~10 lines — guardrails only)
- **Pipeline**: `/cookbook-start` to begin, `/cookbook-next` to advance one step
- **Preferences**: Recipe prompts [enabled/disabled], contribution prompts [enabled/disabled], committing [included/not included]
- **Available skills**: /configure-cookbook, /install-cookbook, /cookbook-start, /cookbook-next, /lint-project-with-cookbook, /plan-cookbook-recipe, /contribute-to-cookbook

Run `/configure-cookbook` to manage preferences.
```

## Step 7: Print Summary

```
=== Cookbook Configuration ===
Rule: cookbook.md (<N> lines) — reinstalled / unchanged
Committing: installed / removed / unchanged
Recipe prompts: enabled / disabled — changed / unchanged
Contribution prompts: enabled / disabled — changed / unchanged
Legacy files removed: <list or "none">
CLAUDE.md: updated / unchanged
```

## Guards

- **Do not modify any files in `../agentic-cookbook/`.** Only read from it.
- **Verify `../agentic-cookbook/` exists** before reading source files.
- **Do not remove cookbook.md.** Reinstall it if needed, never delete it.
- **The rule MUST be under 15 lines.** It is guardrails only.
