---
name: contribute-to-cookbook
version: "2.2.0"
description: "Create a PR to contribute a new recipe or enhancement to the agentic cookbook. Auto-detects admin (push access) vs external (fork-based) workflows. Triggers on 'contribute to cookbook', 'add a recipe', or /contribute-to-cookbook."
argument-hint: "[new|enhance] [recipe-name] [--version]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(git *), Bash(gh *), Bash(ls *), Bash(mkdir *), Bash(which *), Agent, AskUserQuestion
context: fork
---

# Contribute to Agentic Cookbook v2.2.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `contribute-to-cookbook v2.2.0` and stop.

Otherwise, print `contribute-to-cookbook v2.2.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (2.2.0), print:

> ⚠ This skill is running v2.2.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

You walk the user through contributing to the agentic cookbook — either a new recipe or an enhancement to an existing one. The result is a PR targeting `agentic-cookbook/cookbook`, created from a worktree.

The skill supports two contributor paths, detected automatically:

- **Admin** (push access): worktree + branch in the upstream repo, PR within the same repo.
- **External** (no push access): worktree + branch in a fork, PR from fork to upstream.

You never merge the PR or modify the consuming project.

## Usage

```
/contribute-to-cookbook new status-indicator
/contribute-to-cookbook enhance empty-state
```

- `new <recipe-name>` — create a new recipe from scratch
- `enhance <recipe-name>` — improve an existing recipe
- No arguments — ask the user what they want to do

The skill auto-detects whether the cookbook is the current directory or at `../agentic-cookbook/`, and whether the user is an admin or external contributor.

## Step 0: Environment Detection

Run this entire step before doing anything else. It sets variables used throughout the skill.

### 0a. Locate the cookbook (`$COOKBOOK_DIR`)

1. Check if cwd contains `introduction/conventions.md`. If yes, set `$COOKBOOK_DIR` to `.` (cwd is the cookbook).
2. If not, check if `../agentic-cookbook/introduction/conventions.md` exists. If yes, set `$COOKBOOK_DIR` to `../agentic-cookbook`.
3. If neither, stop with:

```
Cookbook repo not found. Expected introduction/conventions.md in the current directory or ../agentic-cookbook/.
Clone it: git clone https://github.com/agentic-cookbook/cookbook.git ../agentic-cookbook
```

**Worktree check**: If `$COOKBOOK_DIR` is inside a git worktree (check `git -C $COOKBOOK_DIR rev-parse --git-common-dir`), resolve to the main repo for worktree creation later.

### 0b. Read required files

1. Read `$COOKBOOK_DIR/introduction/conventions.md` for format rules.
2. Read `$COOKBOOK_DIR/appendix/contributing/AUTHORING.md` for contribution guidelines.

If either file is missing, stop and inform the user.

### 0c. Fork or upstream? (`$IS_FORK`)

```
git -C $COOKBOOK_DIR remote get-url origin
```

- If the origin URL contains `agentic-cookbook/cookbook` (substring match — handles HTTPS, SSH, with or without `.git` suffix): this is the upstream repo. Set `$IS_FORK = false`.
- Otherwise: this is a fork. Set `$IS_FORK = true`. Then check for an `upstream` remote:

```
git -C $COOKBOOK_DIR remote get-url upstream 2>/dev/null
```

- If `upstream` exists and contains `agentic-cookbook/cookbook`: good, proceed.
- If `upstream` is missing or points elsewhere: configure it in sub-step 0e.

### 0d. Determine push access (`$HAS_PUSH_ACCESS`)

**Only runs if `$IS_FORK = false`** (working on the upstream repo directly).

1. Check if `gh` is available: `which gh 2>/dev/null`
2. If `gh` is available, check permissions:

```
gh repo view agentic-cookbook/cookbook --json viewerPermission --jq '.viewerPermission'
```

- Result is `ADMIN`, `MAINTAIN`, or `WRITE`: set `$HAS_PUSH_ACCESS = true`.
- Result is `READ`, `NONE`, or the command fails (not authenticated, network error): set `$HAS_PUSH_ACCESS = false`.

3. If `gh` is not available, ask the user:

```
Do you have push access to agentic-cookbook/cookbook? (yes/no)
If unsure, say no — we'll use the safer fork-based workflow.
```

Set `$HAS_PUSH_ACCESS` based on the response.

### 0e. Fork setup (if needed)

**Runs when**: `$IS_FORK = false` and `$HAS_PUSH_ACCESS = false` (user is on upstream but can't push), OR `$IS_FORK = true` but the `upstream` remote is missing or misconfigured.

**Case 1: On upstream, no push access, need to fork.**

Check if `gh` is available.

If `gh` is available, offer to fork:

```
You don't have push access to agentic-cookbook/cookbook.
I can fork it for you using gh repo fork. This will:
  - Create a fork under your GitHub account
  - Set origin to your fork and upstream to agentic-cookbook/cookbook

Proceed? (yes/no)
```

If yes: run `gh repo fork --remote=true` in `$COOKBOOK_DIR`. This reconfigures the remotes automatically. Set `$IS_FORK = true`.

If no: stop with a message that the user needs to fork manually.

If `gh` is not available, print manual instructions and stop:

```
You need a fork to contribute. Steps:

1. Visit https://github.com/agentic-cookbook/cookbook and click "Fork"
2. Clone your fork:
   git clone https://github.com/<your-username>/agentic-cookbook.git ../agentic-cookbook
3. Add upstream remote:
   git -C ../agentic-cookbook remote add upstream https://github.com/agentic-cookbook/cookbook.git
4. Re-run /contribute-to-cookbook
```

**Case 2: On a fork, `upstream` remote missing or wrong.**

Add or fix the upstream remote:

```
git -C $COOKBOOK_DIR remote add upstream https://github.com/agentic-cookbook/cookbook.git
```

If the remote already exists but points to the wrong URL:

```
git -C $COOKBOOK_DIR remote set-url upstream https://github.com/agentic-cookbook/cookbook.git
```

### 0f. Sync fork with upstream (fork path only)

**Only runs if `$IS_FORK = true`.**

```
git -C $COOKBOOK_DIR fetch upstream
git -C $COOKBOOK_DIR checkout main
git -C $COOKBOOK_DIR merge upstream/main --ff-only
```

If the fast-forward merge fails, warn the user:

```
Your fork's main branch has diverged from upstream.
You may need to reset it: git -C $COOKBOOK_DIR reset --hard upstream/main
Proceed with current state? (yes/no)
```

If no, stop and let the user resolve manually.

### 0g. Resolve GitHub username (`$GITHUB_USER`, fork path only)

**Only runs if `$IS_FORK = true`.**

1. If `gh` is available: `gh api user --jq '.login'`
2. If `gh` is not available: parse the username from the origin URL.
   - HTTPS: `https://github.com/<user>/...` → extract `<user>`
   - SSH: `git@github.com:<user>/...` → extract `<user>`

### 0h. Set contributor path and print status

- If `$IS_FORK = false` and `$HAS_PUSH_ACCESS = true`: set `$CONTRIBUTOR_PATH = "admin"`.
- Otherwise: set `$CONTRIBUTOR_PATH = "external"`.

Derive `$WORKTREE_BASE` from `$COOKBOOK_DIR`:
- If `$COOKBOOK_DIR` is `.`: use `../agentic-cookbook-wt`
- If `$COOKBOOK_DIR` is `../agentic-cookbook`: use `../agentic-cookbook-wt`
- Otherwise: use `$COOKBOOK_DIR/../agentic-cookbook-wt`

Print:

```
Contributor path: admin (push access to agentic-cookbook/cookbook)
```

or:

```
Contributor path: external (fork: $GITHUB_USER/agentic-cookbook → agentic-cookbook/cookbook)
```

---

## Step 1: Determine Contribution Type

Parse `$ARGUMENTS`:

- **Starts with `new`**: Creating a new recipe. The rest of the argument is the recipe name (kebab-case).
- **Starts with `enhance`**: Enhancing an existing recipe. Search `$COOKBOOK_DIR/recipes/` for a file matching the name.
- **Empty**: Ask the user: "New recipe or enhance an existing one? And what's the recipe name?"

## Step 2: New Recipe Flow

1. **Check for duplicates.** Search filenames in `$COOKBOOK_DIR/recipes/` for files containing the recipe name in their filename. Do not read file contents for duplicate detection. If a match exists, tell the user and ask whether to enhance it instead or proceed with a new recipe.

2. **Create a branch and worktree** in the cookbook repo:
   ```
   git -C $COOKBOOK_DIR worktree add $WORKTREE_BASE/<recipe-name> -b feature/<recipe-name>
   ```
   If the worktree creation fails (branch already exists, unclean state), ask the user whether to reuse the existing branch or pick a new name.

3. **Design the recipe.** Invoke `/plan-cookbook-recipe <recipe-name>` to walk through the interactive recipe design. If that skill is not available, do the recipe planning inline — go section by section following `recipes/_template.md`, asking the user about each section.

4. **Verify completeness.** Check every item from the Recipe Completeness Checklist:
   - [ ] YAML frontmatter with UUID, domain matching file path, title, version, all required fields
   - [ ] Behavioral requirements with descriptive kebab-case names
   - [ ] States table — every visual/behavioral state
   - [ ] Appearance values — exact dimensions, colors, fonts, spacing
   - [ ] Conformance test vectors — linked to requirement names
   - [ ] Logging messages — exact message strings
   - [ ] Edge cases
   - [ ] Accessibility requirements
   - [ ] Compliance section — applicable checks evaluated
   - [ ] Change History section

   Do not proceed until every item passes.

   **Compliance evaluation**: Read the compliance categories from `compliance/INDEX.md`. For each applicable category, evaluate the recipe against the checks and populate the `## Compliance` section. If the recipe was authored with `/plan-cookbook-recipe` (v2.2.0+), the compliance section should already be present — verify it's complete. If missing, run the evaluation inline following the same process as `/lint-compliance`.

5. **Update the index.** Add the new recipe to `index.md` in the worktree.

6. **Ask fix preference.** Before creating the PR, ask the contributor:

   ```
   After submission, an automated review pipeline will check your PR.
   If it finds fixable issues, how would you like them handled?

   1. Fix automatically (default) — the pipeline fixes issues and pushes commits directly
   2. Review each change — the pipeline posts suggested changes for you to accept or reject
   ```

   Store the answer as `$FIX_PREFERENCE` (`auto` or `review`). Default to `auto` if the user doesn't answer or picks option 1.

   This preference will be embedded in the PR body as an HTML comment: `<!-- fix-preference: auto -->` or `<!-- fix-preference: review -->`.

7. **Commit, push, and create PR.**

   Commit (both paths):
   ```
   git -C $WORKTREE_BASE/<recipe-name> add -A
   git -C $WORKTREE_BASE/<recipe-name> commit -m "Add <recipe-name> recipe"
   ```

   **Admin path** (`$CONTRIBUTOR_PATH = "admin"`):
   ```
   git -C $WORKTREE_BASE/<recipe-name> push -u origin feature/<recipe-name>
   ```
   If `gh` is available:
   ```
   gh pr create --repo agentic-cookbook/cookbook --head feature/<recipe-name> --title "Add <recipe-name> recipe" --body "New recipe: <recipe-name>\n\n<one-line summary>\n\n<!-- fix-preference: $FIX_PREFERENCE -->"
   ```
   If `gh` is not available, print:
   ```
   Commit pushed. Create the PR manually:
     https://github.com/agentic-cookbook/cookbook/compare/feature/<recipe-name>
   ```

   **External path** (`$CONTRIBUTOR_PATH = "external"`):
   ```
   git -C $WORKTREE_BASE/<recipe-name> push -u origin feature/<recipe-name>
   ```
   If `gh` is available:
   ```
   gh pr create --repo agentic-cookbook/cookbook --head $GITHUB_USER:feature/<recipe-name> --title "Add <recipe-name> recipe" --body "New recipe: <recipe-name>\n\n<one-line summary>\n\n<!-- fix-preference: $FIX_PREFERENCE -->"
   ```
   If `gh` is not available, print:
   ```
   Commit pushed to your fork. Create the PR manually:
     https://github.com/agentic-cookbook/cookbook/compare/main...$GITHUB_USER:cookbook:feature/<recipe-name>
   ```

   Verify the output contains a valid PR URL (or that the manual URL was printed). If a `gh` command fails, print the error and fall back to the manual URL.

7. **Print the PR URL** (or manual URL).

## Step 3: Enhancement Flow

1. **Find the recipe.** Search `$COOKBOOK_DIR/recipes/` for the named recipe. If not found, list available recipes and ask the user to pick one.

2. **Read the existing recipe** and present a brief summary to the user.

3. **Ask what to change.** "What do you want to enhance? (e.g., add states, fix requirements, improve accessibility, update appearance values)"

4. **Create a branch and worktree:**
   ```
   git -C $COOKBOOK_DIR worktree add $WORKTREE_BASE/<recipe-name> -b revise/<recipe-name>
   ```
   If the worktree creation fails (branch already exists, unclean state), ask the user whether to reuse the existing branch or pick a new name.

5. **Make the changes** in the worktree copy of the recipe file.

6. **Bump the version** in the frontmatter (patch for fixes, minor for additions).

7. **Update the Change History** section with today's date and a description of what changed.

8. **Verify completeness** using the same checklist from Step 2.

9. **Ask fix preference.** Same as Step 2, step 6 — ask the contributor their fix preference and store as `$FIX_PREFERENCE`.

10. **Commit, push, and create PR.**

   Commit (both paths):
   ```
   git -C $WORKTREE_BASE/<recipe-name> add -A
   git -C $WORKTREE_BASE/<recipe-name> commit -m "Revise <recipe-name> recipe: <brief description>"
   ```

   **Admin path** (`$CONTRIBUTOR_PATH = "admin"`):
   ```
   git -C $WORKTREE_BASE/<recipe-name> push -u origin revise/<recipe-name>
   ```
   If `gh` is available:
   ```
   gh pr create --repo agentic-cookbook/cookbook --head revise/<recipe-name> --title "Revise <recipe-name> recipe" --body "Enhancement: <description>\n\n<!-- fix-preference: $FIX_PREFERENCE -->"
   ```
   If `gh` is not available, print:
   ```
   Commit pushed. Create the PR manually:
     https://github.com/agentic-cookbook/cookbook/compare/revise/<recipe-name>
   ```

   **External path** (`$CONTRIBUTOR_PATH = "external"`):
   ```
   git -C $WORKTREE_BASE/<recipe-name> push -u origin revise/<recipe-name>
   ```
   If `gh` is available:
   ```
   gh pr create --repo agentic-cookbook/cookbook --head $GITHUB_USER:revise/<recipe-name> --title "Revise <recipe-name> recipe" --body "Enhancement: <description>\n\n<!-- fix-preference: $FIX_PREFERENCE -->"
   ```
   If `gh` is not available, print:
   ```
   Commit pushed to your fork. Create the PR manually:
     https://github.com/agentic-cookbook/cookbook/compare/main...$GITHUB_USER:cookbook:revise/<recipe-name>
   ```

   Verify the output contains a valid PR URL (or that the manual URL was printed). If a `gh` command fails, print the error and fall back to the manual URL.

10. **Print the PR URL** (or manual URL).

## Step 4: Post-PR Verification

After PR creation, verify:

1. The worktree has no uncommitted changes (`git -C $WORKTREE_BASE/<branch-name> status` shows clean).
2. If `gh` is available, verify the PR exists: `gh pr view <branch-name> --repo agentic-cookbook/cookbook`.
3. `index.md` was updated if adding new content.
4. **External path only**: confirm the branch was pushed to `origin` (the fork), not to `upstream`.

If any check fails, fix the issue before proceeding.

## Step 5: Cleanup Guidance

After the PR is created, always print:

**Admin path:**

```
PR created: <url>

After merge, clean up:
  git worktree remove $WORKTREE_BASE/<branch-name>
  cd $COOKBOOK_DIR && git pull
```

**External path:**

```
PR created: <url>

After merge, clean up:
  git worktree remove $WORKTREE_BASE/<branch-name>
  cd $COOKBOOK_DIR && git fetch upstream && git checkout main && git merge upstream/main --ff-only
```

## Guards

- **Do not merge the PR.** That is the user's choice.
- **Do not modify the consuming project.** This skill only touches the cookbook repo.
- **All work happens in a worktree.** Never commit directly to the cookbook's main branch.
- **Do not skip reading conventions.md and AUTHORING.md.** Stop if they are missing.
- **Do not submit incomplete recipes.** Every checklist item must pass before creating the PR.
- **Never push to upstream if external.** If `$CONTRIBUTOR_PATH = "external"`, all pushes go to `origin` (the fork). Never push to the `upstream` remote.
- **Always sync before branching (fork path).** Fetch upstream and fast-forward main before creating a worktree branch.
- **Never hard-fail on missing `gh`.** If `gh` is not available, fall back to manual instructions. The skill must remain functional without `gh`, even if some automation is lost.
- **Verify remote before push.** Before the first push, confirm that `git remote get-url origin` matches expectations (upstream for admin, fork for external).
