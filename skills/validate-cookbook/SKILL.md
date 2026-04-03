---
name: validate-cookbook
version: "1.0.1"
description: "Validate cookbook integrity — frontmatter, cross-references, indexes, skills, rules, file placement. Run from cookbook or consuming project."
argument-hint: "[--category <name>] [--fix] [--version]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(find *), Bash(wc *), Bash(diff *), Agent
context: fork
---

## Version Check

If `$ARGUMENTS` is `--version`, respond with exactly:

> validate-cookbook v1.0.1

Then stop. Do not continue with the rest of the skill.

Otherwise, print `validate-cookbook v1.0.1` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (1.0.1), print:

> Warning: This skill is running v1.0.1 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

---

# Validate Agentic Cookbook

Validate the cookbook's integrity — frontmatter, cross-references, indexes, skills, rules, and file placement. Works from within the cookbook repo or from a consuming project.

## Usage

```
/validate-cookbook                          # run all checks
/validate-cookbook --category frontmatter   # run one category
/validate-cookbook --fix                    # auto-fix simple issues
```

## Guards

- **Read-only by default.** Only modify files when `--fix` is explicitly specified.
- **In consumer mode, never modify `../agentic-cookbook/`.** Consumer checks are read-only always.
- **Do not auto-fix complex issues** (duplicate sections, wrong file placement, structural problems). Report them for manual fix.

---

## Step 1: Detect Mode

Determine the operating mode:

1. If `../agentic-cookbook/` exists AND the current working directory is NOT inside the agentic-cookbook repo, set mode to **consumer**.
2. If `principles/` and `guidelines/` exist in the current working directory, set mode to **cookbook**.
3. Otherwise, print an error and **STOP**:
   ```
   ERROR: Cannot detect cookbook. Run from the cookbook repo or a consuming project with ../agentic-cookbook/ adjacent.
   ```

Print: `Mode: cookbook` or `Mode: consumer`

Set `$COOKBOOK_ROOT` to the absolute path of the cookbook repo root (either `.` in cookbook mode or `../agentic-cookbook` in consumer mode).

---

## Step 2: Parse Arguments

Parse `$ARGUMENTS` for these flags:

| Flag | Effect |
|------|--------|
| `--category <name>` | Run only the named category. Valid names: `frontmatter`, `content`, `references`, `indexes`, `skills`, `placement`, `consumer` |
| `--fix` | Enable auto-fix mode for simple issues |
| (none) | Run all categories |

If `--category` specifies an invalid name, print an error listing valid names and **STOP**.

If in consumer mode and no `--category` is specified, run only category 7 (Consumer Installation).

---

## Step 3: Run Validation

Read the full checklist from `${CLAUDE_SKILL_DIR}/references/validation-checks.md`.

Count the total number of `.md` files under `$COOKBOOK_ROOT/` (excluding `rules/`, `skills/`, `agents/`) using Glob.

Launch up to 3 agents in parallel. Each agent reads `${CLAUDE_SKILL_DIR}/references/validation-checks.md`, receives the `$COOKBOOK_ROOT` path, and runs its assigned categories.

**Agent 1 — Frontmatter & Content**
- Category 1: Frontmatter Integrity
- Category 2: Content Structure

**Agent 2 — References & Indexes**
- Category 3: Cross-References
- Category 4: Indexes and Documentation

**Agent 3 — Skills, Placement & Consumer**
- Category 5: Skills and Rules
- Category 6: File Placement
- Category 7: Consumer Installation (only if consumer mode)

If `--category` was specified, launch only the agent responsible for that category. Skip the others entirely.

Each agent returns results in this format per check:

```
[PASS] <ID> <check-name>: <brief summary>
[FAIL] <ID> <check-name>: <description of failure>
       -> <file>: <specific issue>
[WARN] <ID> <check-name>: <description>
       -> <file>: <specific issue>
```

---

## Step 4: Compile Report

Combine all agent results into a single structured report:

```
=== COOKBOOK VALIDATION ===
Mode: <cookbook|consumer>
Path: <$COOKBOOK_ROOT>
Files scanned: <count>

--- 1. FRONTMATTER INTEGRITY ---
<results from Agent 1>

--- 2. CONTENT STRUCTURE ---
<results from Agent 1>

--- 3. CROSS-REFERENCES ---
<results from Agent 2>

--- 4. INDEXES AND DOCUMENTATION ---
<results from Agent 2>

--- 5. SKILLS AND RULES ---
<results from Agent 3>

--- 6. FILE PLACEMENT ---
<results from Agent 3>

--- 7. CONSUMER INSTALLATION ---
<results from Agent 3, if consumer mode>

=== SUMMARY ===
Pass: <n> | Warn: <n> | Fail: <n>
Categories: <n>/7 passed clean

Top issues:
1. [FAIL] ...
2. [WARN] ...
```

Omit empty categories. In cookbook mode, omit category 7 unless `--category consumer` was specified.

---

## Permissions (--fix mode only)

If `--fix` was specified, present this prompt before making any changes:

```
=== Permissions Required (--fix mode) ===

Auto-fix will modify these files:
<list files that have fixable issues, with what will change>

Approve all fixes? (yes / no)
```

If the user says no, stop and report the issues without fixing them (read-only mode). If yes, apply all fixes.

In default read-only mode (no --fix), no permissions are needed — the skill only reads files.

---

## Step 5: Auto-Fix (if --fix)

If `--fix` was specified and there are fixable issues:

| Fixable issue | Auto-fix action |
|---------------|-----------------|
| Missing index entry | Add the file to `index.md` in the correct section |
| Domain mismatch | Update the `domain:` field in frontmatter to match the file path |
| Stale version in heading | Update the `# Title vX.Y.Z` heading to match frontmatter `version:` |
| Missing Change History section | Append a Change History template to the file |

For each fix applied, print:
```
[FIXED] <ID>: <file> — <what was changed>
```

After all fixes, re-run only the previously-failing checks to verify. Print updated results.

**Do not auto-fix:** duplicate IDs, wrong file placement, structural problems, missing required frontmatter fields (except domain). Report these for manual fix.

---

## Step 6: Done

Print the summary and stop. Do not modify any files unless `--fix` was specified.
