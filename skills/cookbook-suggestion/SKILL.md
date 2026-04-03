---
name: cookbook-suggestion
version: "1.0.0"
description: "Suggest new content or improvements for the agentic cookbook. Guides the user through the idea, then creates a GitHub issue. Triggers on 'suggest', 'cookbook suggestion', 'request a recipe', 'cookbook idea', or /cookbook-suggestion."
argument-hint: "[description] [--version]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(gh *), Bash(which *), Bash(git *), AskUserQuestion
model: sonnet
---

# Cookbook Suggestion v1.0.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `cookbook-suggestion v1.0.0` and stop.

Otherwise, print `cookbook-suggestion v1.0.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (1.0.0), print:

> ⚠ This skill is running v1.0.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

Walks the user through suggesting new content or improvements for the agentic cookbook. Collects structured information about the idea, previews the issue, and submits it to GitHub via `gh issue create`.

## Usage

```
/cookbook-suggestion
/cookbook-suggestion add a recipe for dark mode toggle
```

- With text after the command — use it as the initial suggestion description and skip the free-form description prompt.
- No arguments — ask the user to describe their suggestion.

## Prerequisites

Before doing anything else:

1. **Check `gh` CLI.** Run `which gh`. If the command fails or returns empty, stop with:

   > `gh` is not installed. Install it from https://cli.github.com/ then run `gh auth login`.

2. **Check `gh` authentication.** Run `gh auth status`. If it reports not logged in, stop with:

   > `gh` is installed but not authenticated. Run `gh auth login` first.

3. **Detect cookbook repo.** Check in order:
   - If `introduction/conventions.md` exists in the current directory, the current directory is the cookbook. Set `$COOKBOOK_REPO` to `.`.
   - Else if `../agentic-cookbook/introduction/conventions.md` exists, set `$COOKBOOK_REPO` to `../agentic-cookbook`.
   - Else stop with: "Cannot locate the cookbook repo. Expected `introduction/conventions.md` here or `../agentic-cookbook/`."

4. **Detect GitHub repo identifier.** Run `git -C $COOKBOOK_REPO remote get-url origin` and extract the `owner/repo` slug (strip `.git` suffix and any `https://` or `git@` prefix). Store as `$GH_REPO`.

## Step 1: Gather Suggestion Details

Collect the following. If `$ARGUMENTS` (beyond flags) is non-empty, use it as the initial description and skip prompt 1c.

### 1a. Type

Ask the user (use `AskUserQuestion`):

```
What kind of suggestion is this?

 1. New recipe         — a component, panel, window, or infrastructure pattern
 2. New guideline      — a topic area not currently covered
 3. New principle      — a foundational engineering principle
 4. Enhance existing   — improve or expand something already in the cookbook
 5. Tooling            — skills, rules, validation, or workflow improvement
 6. Other
```

### 1b. Scope

Based on the type selected:

- **New recipe/guideline/principle**: Ask "What should it be called? (brief name, e.g., 'dark-mode-toggle', 'error-recovery')"
- **Enhance existing**: Ask "Which existing content should be improved?" Then search `$COOKBOOK_REPO/` for matching files and confirm with the user. If no match, note the user's description and move on.
- **Tooling/Other**: Ask "Which part of the tooling? (skills, rules, validation, workflow, or describe)"

### 1c. Description

If not already provided via `$ARGUMENTS`, ask: "Describe your suggestion — what should it do or cover, and why is it useful?"

### 1d. Priority

Ask:

```
How important is this to you?

 1. Nice to have  — would be useful but not blocking anything
 2. Important     — would meaningfully improve cookbook coverage
 3. Critical      — a significant gap that affects real work
```

## Step 2: Check for Duplicates

Search existing issues to avoid duplicates:

```
gh issue list --repo $GH_REPO --state open --search "<key terms from description>" --limit 5
```

If matches are found, show them to the user:

```
These open issues look related:

  #12 — Add dark mode recipe
  #34 — Request: toggle component patterns

Is your suggestion already covered? (new / duplicate / related)
```

- **new** — proceed to Step 3.
- **duplicate** — stop with "Looks like this is already tracked. Add a comment on the existing issue if you have additional context."
- **related** — note the related issue number(s) and include them as references in the issue body. Proceed to Step 3.

If no matches found, proceed to Step 3.

## Step 3: Preview the Issue

Build the issue title and body, then show the preview to the user.

**Title format**: `Suggestion: <concise summary>` (under 70 characters)

**Body format**:

```markdown
## Type
<type from 1a>

## Scope
<scope from 1b>

## Description
<description from 1c>

## Priority
<priority from 1d>

## Related issues
<related issue numbers, or "None">

---
Filed via `/cookbook-suggestion`
```

Print the preview:

```
=== Issue Preview ===

Title: <title>

<body>

Submit this issue to <$GH_REPO>? (yes / edit / cancel)
```

- **yes** — proceed to Step 4.
- **edit** — ask what to change, update the title/body, and preview again.
- **cancel** — stop with "Suggestion cancelled."

## Step 4: Submit the Issue

Determine the label based on type:
- New recipe/guideline/principle → `enhancement`, `content`
- Enhance existing → `enhancement`
- Tooling → `enhancement`, `tooling`
- Other → `enhancement`

Run:

```
gh issue create --repo $GH_REPO --title "<title>" --body "<body>" --label "<labels>"
```

If label creation fails because the label doesn't exist, retry without labels:

```
gh issue create --repo $GH_REPO --title "<title>" --body "<body>"
```

If the command fails for any other reason, print the error and stop.

## Step 5: Confirm

Print the issue URL returned by `gh issue create`:

```
Issue created: <URL>
```

## Guards

- **Always preview before submitting.** Never create an issue without the user confirming the preview.
- **One suggestion per invocation.** If the user has multiple ideas, tell them to run `/cookbook-suggestion` again.
- **Do not modify any files.** This skill only creates GitHub issues.
- **Do not guess content.** If the user's description is vague, ask for clarification rather than filling in details.
- **Check for duplicates.** Always search existing issues before creating a new one.
