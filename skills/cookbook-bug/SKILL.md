---
name: cookbook-bug
version: "1.0.0"
description: "File a bug report against the agentic cookbook. Guides the user through describing the issue, then creates a GitHub issue. Triggers on 'report a bug', 'cookbook bug', 'file a bug', or /cookbook-bug."
argument-hint: "[description] [--version]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(gh *), Bash(which *), Bash(git *), AskUserQuestion
model: sonnet
---

# Cookbook Bug v1.0.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `cookbook-bug v1.0.0` and stop.

Otherwise, print `cookbook-bug v1.0.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (1.0.0), print:

> ⚠ This skill is running v1.0.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

Walks the user through filing a bug report against the agentic cookbook. Collects structured information about the problem, previews the issue, and submits it to GitHub via `gh issue create`.

## Usage

```
/cookbook-bug
/cookbook-bug broken link in test-pyramid guideline
```

- With text after the command — use it as the initial bug description and skip the free-form description prompt.
- No arguments — ask the user to describe the bug.

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

## Step 1: Gather Bug Details

Collect the following. If `$ARGUMENTS` (beyond flags) is non-empty, use it as the initial description and skip prompt 1c.

### 1a. Category

Ask the user (use `AskUserQuestion`):

```
What area is the bug in?

 1. Recipe        — incorrect or incomplete recipe content
 2. Guideline     — wrong or misleading guideline
 3. Principle     — issue with a principle
 4. Skill         — a skill doesn't work correctly
 5. Rule          — a rule file has problems
 6. Frontmatter   — metadata, domain, version, or format issue
 7. Cross-reference — broken link or reference
 8. Other
```

### 1b. Affected file(s)

Ask: "Which file(s) are affected? (path relative to cookbook root, or 'not sure')"

If the user says "not sure", that's fine — note it in the issue body and move on.

If the user names a file, verify it exists under `$COOKBOOK_REPO`. If it doesn't, let the user know and ask them to confirm or correct.

### 1c. Description

If not already provided via `$ARGUMENTS`, ask: "Describe the bug — what's wrong and what you expected instead."

### 1d. Severity

Ask:

```
How severe is this?

 1. Cosmetic  — typo, formatting, minor wording
 2. Minor     — incorrect but not misleading, missing optional content
 3. Major     — factually wrong, broken references, missing required content
```

## Step 2: Preview the Issue

Build the issue title and body, then show the preview to the user.

**Title format**: `Bug: <concise summary>` (under 70 characters)

**Body format**:

```markdown
## Category
<category from 1a>

## Affected file(s)
<file paths from 1b, or "Not identified">

## Description
<description from 1c>

## Severity
<severity from 1d>

---
Filed via `/cookbook-bug`
```

Print the preview:

```
=== Issue Preview ===

Title: <title>

<body>

Submit this issue to <$GH_REPO>? (yes / edit / cancel)
```

- **yes** — proceed to Step 3.
- **edit** — ask what to change, update the title/body, and preview again.
- **cancel** — stop with "Issue cancelled."

## Step 3: Submit the Issue

Determine the label based on severity:
- Cosmetic → `bug`, `cosmetic`
- Minor → `bug`
- Major → `bug`, `priority`

Run:

```
gh issue create --repo $GH_REPO --title "<title>" --body "<body>" --label "<labels>"
```

If label creation fails because the label doesn't exist, retry without labels:

```
gh issue create --repo $GH_REPO --title "<title>" --body "<body>"
```

If the command fails for any other reason, print the error and stop.

## Step 4: Confirm

Print the issue URL returned by `gh issue create`:

```
Issue created: <URL>
```

## Guards

- **Always preview before submitting.** Never create an issue without the user confirming the preview.
- **One issue per invocation.** If the user has multiple bugs, tell them to run `/cookbook-bug` again.
- **Do not modify any files.** This skill only creates GitHub issues.
- **Do not guess content.** If the user's description is vague, ask for clarification rather than filling in details.
