---
name: cookbook-help
version: "2.0.0"
description: "Interactive guide to the agentic cookbook — tier status, content overview, skills, searching, contributing, and troubleshooting."
argument-hint: "[topic] [--version]"
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Cookbook Help v2.0.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `cookbook-help v2.0.0` and stop — do not run the skill.

Otherwise, print `cookbook-help v2.0.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (1.0.0), print:

> ⚠ This skill is running v2.0.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

Interactive guide to the agentic cookbook. Answers questions about setup, content, skills, and workflow. Detects the user's context (tier, installed rules, cookbook location) and tailors responses accordingly.

## Usage

```
/cookbook-help
/cookbook-help setup
/cookbook-help recipes
/cookbook-help troubleshooting
```

With no argument, present the topic menu. With a topic name, jump directly to that topic.

## Step 1: Detect Context

Before presenting anything, silently gather context:

1. **Cookbook location**: Check if `introduction/conventions.md` exists (running from within cookbook repo) or `../agentic-cookbook/` exists (running from a consuming project). Set `$COOKBOOK_PATH` accordingly. If neither, set `$COOKBOOK_PATH` to `(not found)`.

2. **Installation detection**: Check `.claude/rules/` for `cookbook.md`. If present: installed. If absent but old tier files exist (`principles.md`, etc.): legacy installation, suggest `/configure-cookbook` to migrate. If none: not installed.

3. **Optional rules**: Check for `committing.md` and `auto-lint.md` in `.claude/rules/`.

4. **CLAUDE.md**: Check if the current project has an `## Agentic Cookbook` section in `CLAUDE.md`.

## Step 2: Route to Topic

If `$ARGUMENTS` matches a topic keyword (case-insensitive), jump directly to that topic. Valid keywords and their aliases:

| Keyword | Aliases | Topic |
|---------|---------|-------|
| `setup` | `my-setup`, `status`, `tier` | My Setup |
| `recipes` | `recipe` | Recipes |
| `guidelines` | `guideline`, `guide` | Guidelines |
| `principles` | `principle` | Principles |
| `rules` | `rule` | Rules |
| `contributing` | `contribute` | Contributing |
| `website` | `site`, `web` | Website |
| `troubleshooting` | `troubleshoot`, `help`, `fix` | Troubleshooting |
| `skills` | `skill`, `commands` | Skills |
| `search` | `find`, `lookup` | Searching |

If no argument or unrecognized argument, present the topic menu using `AskUserQuestion`:

```
What would you like help with?

 1. My setup        — installation status, preferences, available skills
 2. Recipes         — what they are, how to find and use them
 3. Guidelines      — what they cover, how to review against them
 4. Principles      — the 18 engineering principles
 5. Rules           — how rule files work in your project
 6. Skills          — all available skills with usage examples
 7. Searching       — how to find specific content in the cookbook
 8. Contributing    — how to add recipes
 9. Website         — the online cookbook reference
10. Troubleshooting — common issues and fixes
```

After the user picks a topic, show the corresponding section below.

---

## Topic: My Setup

Print a status card with the context gathered in Step 1:

```
=== Your Cookbook Setup ===

Status: Installed / Not installed / Legacy (needs migration)
Cookbook path: <$COOKBOOK_PATH>
CLAUDE.md section: present / missing

Rule: cookbook.md — ✅ installed (or ➖ not installed)
Optional:
  committing.md  — ✅ / ➖ (git workflow)
  auto-lint.md   — ✅ / ➖ (auto-lint)

Preferences:
  Recipe prompts: enabled / disabled
  Contribution prompts: enabled / disabled

Available skills:
  /configure-cookbook         — manage preferences and optional rules
  /install-cookbook            — re-run onboarding
  /lint-project-with-cookbook         — lint against guidelines or recipe
  /plan-cookbook-recipe       — design a new recipe
  /contribute-to-cookbook     — create a cookbook PR
  /validate-cookbook          — validate cookbook integrity
  /cookbook-help              — this guide
  /cookbook-bug               — file a bug report
  /cookbook-suggestion        — suggest content or improvements

To manage preferences: /configure-cookbook
```

Read `.cookbook/preferences.json` to show current preference state. All skills are available to everyone — no tier gates.

---

## Topic: Recipes

```
=== Recipes ===

Recipes are concrete specs for UI components, panels, windows, and
infrastructure patterns. They tell an LLM exactly what to build.

Each recipe includes:
  • Behavioral requirements (MUST/SHOULD/MAY)
  • States table — every visual and behavioral state
  • Appearance values — exact dimensions, colors, fonts, spacing
  • Conformance test vectors — how to verify the implementation
  • Logging messages — exact strings to emit
  • Edge cases and accessibility requirements

Categories:
  recipes/ui/components/   — buttons, indicators, status bars
  recipes/ui/panels/       — file browsers, inspectors, terminals
  recipes/ui/windows/      — project windows, settings windows
  recipes/infrastructure/ — logging, sync, persistence
  recipes/app/            — lifecycle, menus

Browse all: index.md → Recipes section
```

Then count and list the recipe files:
- Use Glob to find `$COOKBOOK_PATH/recipes/**/*.md` (exclude `_template.md`)
- Print: `<count> recipes available`
- List them grouped by category (component, panel, window, infrastructure, app)

```
Usage examples:
  /lint-project-with-cookbook recipe empty-state ./Sources/EmptyState/
  /lint-project-with-cookbook recipe status-bar
```

---

## Topic: Guidelines

```
=== Guidelines ===

Guidelines are topic-organized rules for how to build well. They cover
testing, security, UI, accessibility, logging, feature management, and more.

The main file is guidelines/general.md — it covers:
  • Unit testing, atomic commits, verification
  • Accessibility, localization, RTL
  • Logging, feature flags, analytics
  • Privacy, security, debug mode
  • Deep linking, scriptability

Topic-specific guidelines are in subdirectories:
  guidelines/testing/        — test pyramid, patterns, mutation testing
  guidelines/security/       — auth, tokens, CORS, secure storage
  guidelines/ui/             — typography, spacing, color, layout
  guidelines/accessibility/  — screen readers, keyboard, Dynamic Type
  guidelines/i18n/           — localization, RTL support
  guidelines/concurrency/    — background work, main thread safety
  guidelines/logging/        — structured logging
  guidelines/features/       — feature flags, A/B testing, debug mode
  guidelines/quality/        — linting, code quality

Browse all: guidelines/INDEX.md
```

Then count guidelines:
- Use Glob to find `$COOKBOOK_PATH/guidelines/**/*.md` (exclude INDEX.md)
- Print: `<count> guidelines available`

```
Usage examples:
  /lint-project-with-cookbook guidelines recipes/ui/components/empty-state.md ./Sources/EmptyState/
```

---

## Topic: Principles

```
=== Engineering Principles ===

18 foundational principles that guide all technical decisions.
Located in principles/.

```

Read `$COOKBOOK_PATH/principles/` and list each principle file with its title (extracted from the `# Title` heading or `title:` frontmatter):

```
  1. Simplicity
  2. Make It Work, Then Right, Then Fast
  3. Composition over Inheritance
  4. Dependency Injection
  5. Immutability by Default
  6. Fail Fast
  7. Idempotency
  8. Design for Deletion
  9. YAGNI
 10. Explicit over Implicit
 11. Small, Reversible Decisions
 12. Tight Feedback Loops
 13. Separation of Concerns
 14. Least Astonishment
 15. Manage Complexity Through Boundaries
 16. Native Controls
 17. Open Source Preference
 18. Optimize for Change
```

Print: `Read any principle: ask me about a specific one, or read principles/<name>.md`

---

## Topic: Rules

```
=== Rules ===

Rules are terse, LLM-optimized markdown files installed into your
project's .claude/rules/ directory. They activate automatically — Claude
reads them at the start of every conversation and follows them during
planning and implementation.

Main rule:
  cookbook.md — the full cookbook: principles, guidelines, recipes, contribution prompts

Optional rules (independent of the cookbook):
  committing.md  — structured git workflow (worktree → PR → merge)
  auto-lint.md   — auto-lint skills/agents/rules on create/modify

How they work:
  1. /install-cookbook copies cookbook.md from the cookbook into .claude/rules/
  2. Claude Code loads .claude/rules/*.md at session start
  3. The rule enforces cookbook content during planning and implementation
  4. /configure-cookbook manages preferences and optional rules

Your installed rules: (refer to the tier detected in Step 1)
```

List the user's installed rules with ✅, and rules they don't have with ➖.

---

## Topic: Skills

```
=== Available Skills ===

All skills follow the /command-name pattern. Run any skill by typing
its command in the Claude Code prompt.
```

Print this table, marking each skill as available or requires a higher tier based on the detected tier:

```
Setup & Configuration:
  /install-cookbook            — first-time onboarding
  /configure-cookbook         — manage preferences and optional rules
  /cookbook-help              — this interactive guide

Linting & Review:
  /lint-project-with-cookbook         — lint against guidelines or recipe
    Usage: /lint-project-with-cookbook guidelines <recipe> <impl-path>
           /lint-project-with-cookbook recipe <recipe> [impl-path]
  /lint-recipe               — lint a recipe file against the template
  /lint-compliance           — evaluate a recipe against compliance checks

Authoring:
  /plan-cookbook-recipe       — interactive recipe design
    Usage: /plan-cookbook-recipe status-bar
  /contribute-to-cookbook     — create a PR to the cookbook
    Usage: /contribute-to-cookbook new status-indicator
           /contribute-to-cookbook enhance empty-state

Validation:
  /validate-cookbook          — validate cookbook integrity (any tier)
    Usage: /validate-cookbook
           /validate-cookbook --category frontmatter
           /validate-cookbook --fix

Feedback:
  /cookbook-bug               — file a bug report (any tier, requires gh CLI)
    Usage: /cookbook-bug
           /cookbook-bug broken link in test-pyramid guideline
  /cookbook-suggestion        — suggest new content or improvements (any tier, requires gh CLI)
    Usage: /cookbook-suggestion
           /cookbook-suggestion add a recipe for dark mode toggle
```

---

## Topic: Searching

```
=== Searching the Cookbook ===

Finding specific content in the cookbook:

By index:
  index.md              — master table of contents
  guidelines/INDEX.md   — guideline index by topic

By keyword (from your project):
  Search guidelines:  grep -r "keyword" ../agentic-cookbook/guidelines/
  Search recipes:     grep -r "keyword" ../agentic-cookbook/recipes/
  Search principles:  grep -r "keyword" ../agentic-cookbook/principles/

By domain URL:
  Every cookbook file has a domain identifier like:
    agentic-cookbook://guidelines/testing/test-pyramid
    agentic-cookbook://recipes/ui/components/empty-state

  Search by domain: grep -r "agentic-cookbook://recipes/ui" ../agentic-cookbook/

By file pattern:
  All recipes:     ls ../agentic-cookbook/recipes/**/*.md
  All guidelines:  ls ../agentic-cookbook/guidelines/**/*.md
  All principles:  ls ../agentic-cookbook/principles/*.md
```

If `$COOKBOOK_PATH` is available, replace `../agentic-cookbook/` with the actual path in the output.

---

## Topic: Contributing

```
=== Contributing ===

Everyone has full contributor access.

Workflow:
  1. /plan-cookbook-recipe <name>        — design the recipe interactively
  2. /contribute-to-cookbook new <name>  — creates a branch, worktree, and PR
     /contribute-to-cookbook enhance <name> — improve an existing recipe

The contribute skill handles the full workflow:
  • Checks for duplicates
  • Creates a worktree branch (feature/<name> or revise/<name>)
  • Invokes the recipe planner
  • Verifies completeness
  • Updates index.md
  • Commits, pushes, creates PR

Guidelines:
  • Read introduction/conventions.md for format rules
  • Read appendix/contributing/AUTHORING.md for authoring guidance
  • Every recipe needs all 17 sections — no empty sections
  • Start from recipes/_template.md
```

---

## Topic: Website

```
=== Cookbook Website ===

The agentic cookbook has a companion website at:

  🌐 https://agentic-cookbook.com

The site provides a browsable, searchable version of the cookbook content
with a sidebar navigation mirroring the cookbook directory structure.

Status: Under construction — some sections may be incomplete.

The canonical source of truth is always the markdown files in the
cookbook repository. The website is generated from these files.
```

---

## Topic: Troubleshooting

```
=== Troubleshooting ===
```

Print the following based on detected issues:

**If cookbook not found:**
```
❌ Cookbook not found

  The cookbook should be at ../agentic-cookbook/ relative to your project.

  Fix:
    git clone git@github.com:agentic-cookbook/cookbook.git ../agentic-cookbook

  Then re-run: /install-cookbook
```

**If no tier installed:**
```
⚠️ No tier configured

  No cookbook rule files found in .claude/rules/.

  Fix: /configure-cookbook
```

**If CLAUDE.md missing cookbook section:**
```
⚠️ CLAUDE.md missing cookbook section

  Your CLAUDE.md doesn't have an ## Agentic Cookbook section.

  Fix: /install-cookbook
```

**Always show these common issues:**
```
Common issues:

  "Skill not found" or "Unknown command"
    → Skills must be globally installed (symlinked from ~/.claude/skills/)
      to work outside the cookbook repo. Check:
      ls ~/.claude/skills/

  "Version mismatch" warning at skill startup
    → The skill loaded from cache is older than what's on disk.
      Fix: restart your Claude Code session.

  Rules not activating
    → Rules must be in .claude/rules/ (not .claude/rules/subfolder/).
      Check: ls .claude/rules/

  Cookbook repo out of date
    → Pull latest: git -C ../agentic-cookbook pull

  Stale global symlinks after skill rename
    → If skills were symlinked to ~/.claude/skills/, the old names
      may still be there. Remove stale symlinks and re-link:
      ls -la ~/.claude/skills/ | grep agentic-cookbook
```

---

## After Any Topic

After printing a topic, ask:

```
Anything else? Pick another topic or ask a question.
```

If the user asks a follow-up question about the current topic, answer it using the cookbook content (read files as needed). If they pick a new topic, show that topic. If they say no or indicate they're done, print "Happy cooking!" and stop.

## Guards

- **Read-only** — do not modify any files.
- **Console only** — all output goes to stdout.
- **Stay in scope** — answer questions about the cookbook, its content, and its tooling. For questions outside this scope, suggest the appropriate resource.
