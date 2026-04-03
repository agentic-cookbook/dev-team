---
name: install-cookbook
version: "12.0.0"
description: "Install the agentic cookbook into your project. Sets up a minimal always-on rule, pipeline skills, and recommended plugins."
argument-hint: "[--version]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(cp *), Bash(mv *), Bash(mkdir *), Bash(ls *), Bash(wc *), Bash(date *), Bash(claude *), Bash(chmod *), Skill
model: sonnet
---

# Install Agentic Cookbook v12.0.0

> **Breaking change in v11.0.0**: No prompts — installs everything with sensible defaults. Use `/configure-cookbook` to adjust preferences afterward.

> **IMPORTANT**: This skill has ZERO permission prompts. Do NOT present a permissions audit. Do NOT ask the user to approve files, commands, or actions. The permissions rule does not apply here — this skill's steps are the plan. Proceed directly through all steps without stopping.

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `install-cookbook v12.0.0` and stop — do not run the skill.

Otherwise, print `install-cookbook v12.0.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (12.0.0), print:

> ⚠ This skill is running v12.0.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

Import the agentic cookbook into your project. This skill installs:

1. **Minimal always-on rule** (~10 lines, ~500 bytes) — behavioral guardrails loaded every turn
2. **Pipeline skills** (`/cookbook-start`, `/cookbook-next`) — iterative planning and implementation, loaded on-demand

The always-on rule contains only guardrails. All workflow content (principles, guidelines, planning pipeline, implementation pipeline, verification) is loaded on-demand by the pipeline skills.

## Usage

```
/install-cookbook
```

Run from your project directory. The cookbook must be cloned at `../agentic-cookbook/`.

## Step 1: Verify Prerequisites

1. Check that `../agentic-cookbook/` exists (use `ls ../agentic-cookbook/cookbook/`). If not found, print:
   ```
   Cookbook not found. Clone it first:
   git clone git@github.com:agentic-cookbook/cookbook.git ../agentic-cookbook
   ```
   Then stop.

2. Check that the current directory is a project — it has a `CLAUDE.md` or is a git repo (`.git/` exists). If neither, print: "This does not appear to be a project directory. Navigate to your project root and try again." Then stop.

## Step 2: Write Preferences

If `.cookbook/preferences.json` already exists, leave it as-is (user may have customized it via `/configure-cookbook`). Otherwise:

Create `.cookbook/` if it doesn't exist: `mkdir -p .cookbook`

Write `.cookbook/preferences.json` with all features enabled:

```json
{
  "show_recipe_prompts": true,
  "show_contribution_prompts": true
}
```

## Step 3: Generate Minimal Rule File

Create `.claude/rules/` if it doesn't exist.

Write `.claude/rules/cookbook.md` with exactly this content:

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

Count lines and bytes with `wc -l -c .claude/rules/cookbook.md` and report the size.

## Step 4: Write Generation Manifest

Write `.cookbook/manifest.json`:

```json
{
  "generated": "<ISO 8601 timestamp>",
  "generator_version": "12.0.0",
  "source_cookbook": "../agentic-cookbook",
  "rule_type": "minimal",
  "preferences": {
    "show_recipe_prompts": true,
    "show_contribution_prompts": true
  }
}
```

## Step 5: Update CLAUDE.md

Add or update an `## Agentic Cookbook` section in the project's `CLAUDE.md`.

- If `CLAUDE.md` does not exist, create it with `# <directory name>` as the heading, followed by the section below.
- If `CLAUDE.md` exists but has no `## Agentic Cookbook` section, append the section to the end.
- If the section already exists, replace it in place using the Edit tool.

The section content:

```markdown
## Agentic Cookbook

This project uses the [agentic-cookbook](https://github.com/agentic-cookbook/cookbook).

- **Cookbook path**: `../agentic-cookbook/`
- **Rule**: `cookbook.md` (minimal, ~10 lines — guardrails only)
- **Pipeline**: `/cookbook-start` to begin, `/cookbook-next` to advance one step
- **Preferences**: Recipe prompts [enabled/disabled], contribution prompts [enabled/disabled]
- **Available skills**: /configure-cookbook, /contribute-to-cookbook, /cookbook-bug, /cookbook-help, /cookbook-next, /cookbook-start, /cookbook-suggestion, /install-cookbook, /install-recommended-tools, /install-worktree-rule, /lint-agent, /lint-compliance, /lint-project-with-cookbook, /lint-recipe, /lint-rule, /lint-skill, /optimize-rules, /plan-cookbook-recipe, /port-swiftui-to-appkit, /uninstall-cookbook, /validate-cookbook

Run `/configure-cookbook` to manage preferences.
```

## Step 6: Install Recommended Plugins

Read `${CLAUDE_SKILL_DIR}/references/recommended-plugins.md` for the full list.

Before installing, check which plugins are already installed: `claude plugin list --scope user`. Only install plugins that are not already present.

Install all recommended plugins globally using `claude plugin install <plugin-name> --scope user`:

- playwright
- context7
- figma
- frontend-design
- superpowers
- code-review
- pr-review-toolkit
- security-guidance
- document-skills
- plugin-dev
- agent-sdk-dev
- hookify
- playground

For LSP plugins, detect which languages the project uses by checking file extensions in the project directory, then install the matching LSP plugins:

| Extensions | Plugin |
|------------|--------|
| `.swift` | swift-lsp |
| `.ts`, `.tsx`, `.js`, `.jsx` | typescript-lsp |
| `.kt` | kotlin-lsp |
| `.cs` | csharp-lsp |

If no source files are found, skip LSP plugins.

If any plugin fails to install, note the failure and continue with the rest.

Print: `Installed N plugins (M already installed, skipped). Failures: <list or "none">`

## Step 7: Print Summary

```
=== Agentic Cookbook Installed ===
CLAUDE.md: updated
Rule: cookbook.md (<N> lines, <B> bytes) — minimal guardrails
Manifest: .cookbook/manifest.json
Preferences: .cookbook/preferences.json
Plugins: N installed, M skipped (already installed)

Pipeline workflow:
  /cookbook-start planning <task>  — begin planning
  /cookbook-next                   — advance one step
  /cookbook-start implementation   — begin implementation
  /cookbook-next                   — advance one step

To manage preferences: /configure-cookbook
```

## Guards

- **Do not modify the cookbook repo.** Only read from `../agentic-cookbook/`.
- **Plugin installs are global (--scope user).** They are not project-specific.
- **The generated rule MUST be under 15 lines.** It is guardrails only — no workflow content.
