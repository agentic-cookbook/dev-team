---
name: plan-cookbook-recipe
version: 2.3.0
description: Interactively design a new cookbook recipe through guided discussion
disable-model-invocation: true
context: fork
allowed-tools: Read, Glob, Grep, Agent, Write, Edit, AskUserQuestion, Bash(git *), Bash(mkdir *), Bash(ls *)
argument-hint: [recipe-name] [--version]
---

# Plan Agentic Cookbook Recipe v2.3.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `plan-cookbook-recipe v2.3.0` and stop.

Otherwise, print `plan-cookbook-recipe v2.3.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (2.3.0), print:

> ⚠ This skill is running v2.3.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

You are guiding the user through designing a new recipe for the agentic cookbook. This is a conversational, interactive process — you ask questions, propose options, surface design decisions, and ultimately produce a complete recipe file.

## Usage

```
/plan-cookbook-recipe status-bar
```

Starts an interactive conversation to design a new `status-bar` recipe. The skill walks through each recipe section — overview, requirements, appearance, states, platforms, accessibility, logging — proposing drafts and refining with the user.

**ABSOLUTE RULE: NO IMPLEMENTATION CODE.** This skill produces recipe markdown files only. Never write Swift, Kotlin, TypeScript, or any other implementation code.

## Before starting

1. Read `${CLAUDE_SKILL_DIR}/references/section-guide.md` for authoring guidance
2. Read the recipe template at `recipes/_template.md`
3. Read `CLAUDE.md` and `introduction/conventions.md` for format rules
4. Scan existing recipes: recursively list `recipes/`

If any of these files are missing (template, conventions, or cookbook directory), inform the user and stop. Do not proceed with incomplete references.

## Phase 1: Discovery & Discussion

This phase is conversational. Ask questions, don't assume.

### Step 1: Identify the recipe

If `$ARGUMENTS` is not empty (and not `--version`), use it as the recipe name. Otherwise ask: "What component or feature do you want to create a recipe for?"

### Step 2: Check for overlap

Search existing recipes for anything similar:
- Grep recipe filenames and Overview sections for related keywords
- If a similar recipe exists, tell the user: "There's an existing recipe `{name}` that covers {description}. Should we extend that one, or is this genuinely different?"

### Step 3: Categorize the recipe

#### 3a. Discover existing categories

Scan `recipes/` to build the list of existing categories dynamically. Walk the directory tree and collect every leaf directory that contains `.md` files (excluding `_template.md` and `INDEX.md`). Each unique directory path relative to `recipes/` is a category.

Also read `recipes/INDEX.md` to get the description of each category section.

Present the discovered categories to the user with their descriptions and example recipes. For example:

> **Existing recipe categories:**
> 1. **ui/component** — Reusable visual building blocks (empty-state, status-bar, ...)
> 2. **ui/panel** — Content areas that compose into windows (file-tree-browser, terminal-pane, ...)
> 3. **ui/window** — Top-level window layouts (project-window, settings-window, ...)
> 4. **infrastructure** — Non-visual architecture patterns (logging, directory-sync, ...)
> 5. **app** — Application lifecycle, menus, commands (lifecycle, menu-commands)
> 6. **None of these fit — propose a new category**

#### 3b. If an existing category fits

Use it. Set the recipe path to `recipes/{category}/{kebab-case-name}.md`.

#### 3c. If no existing category fits

Walk the user through creating a new category:

1. **Name the category.** Ask: "What should this category be called? Use kebab-case (e.g., `tooling`, `claude`, `testing`)."
   - Categories can be top-level (`recipes/{name}/`) or nested (`recipes/{parent}/{name}/`).
   - Propose a name based on the recipe being designed and explain your reasoning.

2. **Describe the category.** Ask: "In one sentence, what kinds of recipes belong in this category?" This description will be used in INDEX.md.

3. **Create the directory.** The directory will be created when the recipe file is written (in Phase 2). Note the new path for later.

4. **Plan INDEX.md update.** A new section must be added to `recipes/INDEX.md` following the existing pattern:
   - A `## {category}` heading (using dot notation matching the directory path, e.g., `## tooling` or `## claude`)
   - A one-line description paragraph
   - A markdown table with columns: Domain, File, Version, Description
   - Place the new section in alphabetical order among existing sections (before the Change History section)

Record the new category details for use in Phase 2 and Phase 3.

### Step 4: Walk through each section

For each recipe section, have a brief focused discussion. Don't try to cover everything at once — go section by section.

**Overview** — "In one or two sentences, what does this component do and when would you use it?"

**Behavioral Requirements** — "What are the hard rules? What MUST this component do? What SHOULD it do? What MAY it optionally do?"
- Propose requirements as you understand them, with descriptive kebab-case names (e.g., `ordered-list`, `scroll-to-bottom`)
- Use RFC 2119 keywords: MUST (required), SHOULD (recommended), MAY (optional)
- After proposing, ask: "Does this capture the requirements? Anything missing or wrong?"

**Appearance** — "What does it look like?"
- Offer to sketch an ASCII mockup if it's a visual component
- Ask about: dimensions, colors, fonts, spacing, corner radius, shadows
- For recipes: ask about layout (split view? tabs? stack?)

**States** — "What states can it be in?"
- Propose a states table based on the requirements discussion
- Common states: default, pressed, disabled, focused, loading, error, empty

**Platforms** — "Which platforms does this target?"
- Default to all platforms unless the user specifies otherwise
- For each platform, ask if there are platform-specific considerations
- Propose native control equivalents where they exist (see principles/native-controls.md)

**Dependencies** — "Does this compose or depend on other cookbook recipes?"
- Check the existing recipe inventory
- For composite recipes: identify which component recipes are used

**Edge Cases** — "What could go wrong? What are the boundary conditions?"
- Propose edge cases based on the requirements (empty data, very long text, RTL, rapid interaction)

**Accessibility** — "How should this work with VoiceOver/TalkBack/keyboard?"
- Propose accessibility requirements based on the component type (see guidelines/general.md — Accessibility from day one)
- Include: roles, labels, keyboard navigation, Dynamic Type support

**Logging** — "What events should be logged?"
- Propose log events based on the requirements and state transitions (see guidelines/general.md — Instrumented logging)
- Use the standard format: subsystem `{{bundle_id}}`, category matching component name

**All remaining sections** — For Deep Linking, Localization, Accessibility Options, Feature Flags, Analytics, Privacy: propose sensible defaults and ask if the user wants to customize. Many components will use the template defaults.

### Step 5: Surface design decisions

Throughout the discussion, whenever you make a choice (icon selection, layout approach, animation style, default value), explicitly flag it:

> **Design Decision**: I'm proposing {X} because {Y}. Is that the right call?

Record all decisions for the Design Decisions section.

## Permissions

Before writing any files, present this prompt to the user:

```
=== Permissions Required ===

This skill will:
- Write <recipe-path> — the new recipe file
- Edit index.md — add the new recipe to the index (if applicable)
- Run git add/commit — commit the new recipe

Approve all? (yes / no)
```

If the user says no, stop and ask what they want to change. If yes, proceed without further permission prompts.

### Step 6: Compliance guidance

After covering all recipe sections and before drafting, walk the author through applicable compliance checks. This is proactive guidance — surface considerations the author may not have thought of.

#### Compliance Delegation

Before running inline compliance evaluation, check if the dev-team plugin is available by checking whether `/dev-team-lint` is listed in the available skills.

**If dev-team is available:**
1. Invoke `/dev-team-lint <recipe-path> --compliance-only`
2. Use the lint report's compliance findings as the basis for the compliance discussion
3. Present each finding to the user for confirmation/adjustment
4. Skip the inline compliance evaluation below

**If dev-team is NOT available:**
Proceed with the inline compliance evaluation as described below.

#### Inline compliance evaluation (fallback)

1. Read the compliance categories from `compliance/INDEX.md`.
2. For each of the 10 categories, read the compliance file and determine which checks apply to this recipe based on the discussion so far.
3. For each applicable check, briefly explain what it requires and ask whether the recipe addresses it:

   > **Compliance check — secure-log-output (Security):** Log messages must not contain credentials or PII. Your Logging section looks good here — the log events don't include sensitive data. Marking as passed.

   > **Compliance check — data-minimization (Privacy & Data):** This recipe collects user input. Have you considered what data is strictly necessary? The Privacy section should document what's collected and why.

4. For checks that surface gaps, help the author address them by updating the relevant recipe section.
5. After all applicable checks are reviewed, build the Compliance table for inclusion in the recipe.

**Key principle:** This is not a rubber stamp. The goal is to surface things the author may have missed — "Your recipe handles passwords but doesn't mention secure storage. Here's what the security compliance check requires..."

## Phase 2: Draft the recipe

Once the discussion is complete:

1. Determine the filename from the category chosen in Step 3: `recipes/{category}/{kebab-case-name}.md`
   - If this is a new category (Step 3c), create the directory with `mkdir -p`.

2. Write the complete recipe file with ALL 17 sections:
   - Frontmatter: id (UUID), domain (path-derived), type recipe, version 1.0.0, status draft, language en, today's date for created/modified, author (user's name or claude-code), copyright "YYYY Mike Fullerton", license MIT, summary, platforms, tags, depends-on, related, references
   - Every section from the template populated from the discussion
   - No empty sections — if a section doesn't apply, include it with "Not applicable — {reason}"
   - All requirements with unique kebab-case names
   - Conformance test vectors linked to requirement names
   - Logging messages per instrumented logging guidelines (see guidelines/general.md)
   - `{{placeholder}}` tokens for app-specific values

3. Read the file back to verify completeness.

## Phase 3: Verification & Commit

1. **Completeness check**: Verify every section is present and populated. No TODOs or placeholder text.
2. **Requirement count**: Summarize: "This recipe has N requirements (X MUST, Y SHOULD, Z MAY), N test vectors, N log events."
3. **Dependency check**: Verify all referenced recipes exist in the cookbook repo.
4. **Format check**: Verify frontmatter is valid YAML, requirement numbering is sequential, test vector IDs are unique.
5. **INDEX.md update**: If a new category was created in Step 3c, add the new section to `recipes/INDEX.md` following the pattern described in Step 3c. Also add the new recipe entry to the appropriate table (new or existing category). Update the INDEX.md `related` frontmatter list to include the new recipe's domain.
6. **Present summary**: Show the user a brief overview of what was created. If a new category was added, highlight it.
7. **Commit**: Commit the new recipe with message: "Add {name} recipe\n\n{one-line description}"

## Important notes

- **This is a conversation, not a form.** Don't dump all questions at once. Go section by section, propose drafts, and refine.
- **Propose, then refine.** For each section, offer your best draft based on what you've learned, then let the user adjust.
- **Check the native controls principle (principles/native-controls.md).** If the component maps to a native platform control, note it. The recipe should say "use the native control" and document the configuration, not reinvent it.
- **Recipes are for LLMs.** The primary consumer is an LLM implementing the recipe. Be precise, concrete, and unambiguous. Use exact values, not vague descriptions.
- **Design Decisions are first-class.** Every subjective choice needs to be surfaced, approved, and recorded. This ensures cross-platform consistency.
