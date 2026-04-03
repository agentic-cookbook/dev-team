---
name: uninstall-cookbook
version: "1.0.0"
description: "Remove the agentic cookbook from your project. Removes rules, state files, CLAUDE.md section, and optionally global plugins and status line."
argument-hint: "[--version]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Edit, Bash(rm *), Bash(ls *), Bash(claude *), Bash(cat *), AskUserQuestion
model: haiku
---

# Uninstall Agentic Cookbook v1.0.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `uninstall-cookbook v1.0.0` and stop — do not run the skill.

Otherwise, print `uninstall-cookbook v1.0.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (1.0.0), print:

> ⚠ This skill is running v1.0.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

Remove the agentic cookbook from your project. This reverses what `/install-cookbook` installed:

- Cookbook state directory (`.cookbook/`)
- Rule files (`.claude/rules/cookbook.md`, `.claude/rules/committing.md`)
- CLAUDE.md section (`## Agentic Cookbook`)
- Optionally: global plugins and status line configuration

## Usage

```
/uninstall-cookbook
```

Run from your project directory.

## Step 1: Detect Installation State

Check the current project for installed cookbook components:

1. **New-location state**: Does `.cookbook/` exist? List its contents.
2. **Old-location state**: Do any `.claude/cookbook-*` files exist? (`cookbook-manifest.json`, `cookbook-preferences.json`, `cookbook-pipeline.json`, `cookbook-statusline.sh`)
3. **Rule files**: Does `.claude/rules/cookbook.md` exist? Does `.claude/rules/committing.md` exist?
4. **CLAUDE.md**: Does `CLAUDE.md` contain an `## Agentic Cookbook` section?
5. **Status line**: Does `~/.claude/settings.json` contain a `statusLine` entry referencing `.cookbook/statusline.sh` or `.claude/cookbook-statusline.sh`?

If none of these are found, print: "Cookbook does not appear to be installed in this project." and stop.

Print the detected state:

```
=== Cookbook Installation Detected ===
State directory (.cookbook/): found / not found
Legacy state files (.claude/cookbook-*): found / not found
Rule: .claude/rules/cookbook.md — found / not found
Committing: .claude/rules/committing.md — found / not found
CLAUDE.md section: found / not found
Status line config: found / not found
```

## Step 2: Present Removal Plan

Show the user what will be removed and ask for confirmation:

```
=== Cookbook Uninstall Plan ===

Will remove:
  • .cookbook/ directory (manifest, preferences, pipeline state, statusline)
  • .claude/rules/cookbook.md
  • .claude/rules/committing.md (if present)
  • "## Agentic Cookbook" section from CLAUDE.md

Will also ask about:
  • Global plugins installed by the cookbook
  • Status line configuration in ~/.claude/settings.json

Proceed? (yes / no)
```

Only list items that were actually detected in Step 1. If an item was not found, omit it from the list.

If the user says no, stop.

## Step 3: Remove State Directory

Remove the `.cookbook/` directory if it exists: `rm -rf .cookbook/`

Also remove any old-location files if they exist:
- `rm -f .claude/cookbook-manifest.json`
- `rm -f .claude/cookbook-preferences.json`
- `rm -f .claude/cookbook-pipeline.json`
- `rm -f .claude/cookbook-statusline.sh`

Print which items were removed.

## Step 4: Remove Rule Files

Remove cookbook rule files if they exist:

- `rm -f .claude/rules/cookbook.md`
- `rm -f .claude/rules/committing.md`

Print which files were removed.

## Step 5: Remove CLAUDE.md Section

If `CLAUDE.md` contains an `## Agentic Cookbook` section:

1. Read the file
2. Identify the section: starts at `## Agentic Cookbook` and ends just before the next `## ` heading or at end of file
3. Remove the entire section using the Edit tool
4. If removing the section leaves trailing blank lines at the end of the file, trim them

Do not delete `CLAUDE.md` itself, even if the section was the only content besides the title heading.

Print: "Removed ## Agentic Cookbook section from CLAUDE.md"

If the section was not found, print: "No cookbook section found in CLAUDE.md — skipped."

## Step 6: Prompt About Global Plugins

The following plugins may have been installed by `/install-cookbook`. Present them to the user grouped by category.

Run `claude plugin list --scope user` to see what is currently installed. Only show plugins that are actually installed.

**Core:**
- playwright
- context7
- figma
- semgrep
- frontend-design

**Development Workflow:**
- superpowers
- code-review
- pr-review-toolkit
- security-guidance
- document-skills

**Skill & Plugin Authoring:**
- plugin-dev
- agent-sdk-dev
- hookify
- playground

**LSP:**
- swift-lsp
- typescript-lsp
- kotlin-lsp
- csharp-lsp

Present only the plugins that are currently installed:

```
=== Global Plugins ===

⚠ These plugins are shared across ALL projects. Removing them
  affects every project, not just this one.

The following installed plugins may have been added by the cookbook:

  Core:
    1. playwright
    2. context7
    ...

  Development Workflow:
    3. superpowers
    ...

Remove cookbook-installed plugins?

  1. Remove all listed plugins
  2. Pick which to remove
  3. Keep all (skip)
```

- **Remove all**: Run `claude plugin uninstall <name> --scope user` for each listed plugin. Print results.
- **Pick**: Present a numbered list. User enters numbers (comma-separated or space-separated) of plugins to remove. Run `claude plugin uninstall <name> --scope user` for each selected plugin.
- **Keep all**: Skip.

If no cookbook-recommended plugins are currently installed, print: "No cookbook-recommended plugins found — skipped." and move on.

## Step 7: Offer Status Line Removal

If `~/.claude/settings.json` exists and contains a `statusLine` entry referencing `.cookbook/statusline.sh` or `.claude/cookbook-statusline.sh`:

```
Status line in ~/.claude/settings.json references the cookbook statusline.
Remove it? (yes / no)
```

If yes: Remove the `statusLine` key from `~/.claude/settings.json` using the Edit tool.

If no: Print "Status line kept. You may want to update it manually since the cookbook files have been removed."

If no cookbook-related statusLine was found, skip this step silently.

## Step 8: Print Summary

```
=== Cookbook Uninstalled ===
State directory: removed / was not present
Legacy state files: removed / were not present
Rule (.claude/rules/cookbook.md): removed / was not present
Committing (.claude/rules/committing.md): removed / was not present
CLAUDE.md section: removed / was not present
Global plugins: N removed / kept / no cookbook plugins found
Status line: removed / kept / was not configured

The agentic cookbook has been removed from this project.
To reinstall: /install-cookbook
```

## Guards

- **Do not modify the cookbook repo.** Only modify the consuming project.
- **Do not remove `.claude/` itself** — only cookbook-specific files within it.
- **Do not remove `CLAUDE.md`** — only the `## Agentic Cookbook` section.
- **Do not remove plugins without user confirmation.** Always ask first and warn about global scope.
- **Do not modify `~/.claude/settings.json`** beyond the `statusLine` key without user approval.
- **Handle both old and new paths.** Users may have installed before the v9.0.0 migration.
