---
name: cookbook-next
version: "2.0.0"
description: "Advance the cookbook pipeline by one step. Loads one concern, evaluates it, records the result, and exits."
argument-hint: "[skip]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash(ls *), Bash(wc *), Bash(date *), Bash(git diff *), Bash(git status *), Bash(git add *), Bash(git commit *), AskUserQuestion
---

# Cookbook Next v2.0.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `cookbook-next v2.0.0` and stop — do not run the skill.

Otherwise, print `cookbook-next v2.0.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (1.0.0), print:

> ⚠ This skill is running v2.0.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

Advance the cookbook pipeline by one step. Each invocation:

1. Reads the current step from `.cookbook/pipeline.json`
2. Loads one concern from `pipeline-concerns.json`
3. Reads the referenced guideline file
4. Evaluates the concern against the current task (planning) or code (implementation)
5. Records the result
6. Exits — the user invokes `/cookbook-next` again for the next step

This keeps per-step context minimal (~10 lines of pipeline data + one guideline file).

## Usage

```
/cookbook-next          — advance to the next step
/cookbook-next skip     — mark the current step as N/A and advance
```

## Step 1: Load Pipeline State

Read `.cookbook/pipeline.json`. If it does not exist, print: "No active pipeline. Run /cookbook-start first." and stop.

Extract: `phase`, `current_step`, `total_steps`, `steps`, `task_description`, `results`.

## Step 2: Check Completion

Find the current step number from the `steps` array using the index `current_step - 1`.

If `current_step` exceeds the length of `steps`, the pipeline is complete. Print the summary and stop:

```
=== Pipeline Complete ===
Phase: <phase>
Task: <task description>
Results:
  Applicable: <count> concerns
  N/A: <count> concerns

Applicable concerns:
<numbered list with step number, concern name, and notes>

State saved to .cookbook/pipeline.json.
```

If phase is `planning`, also print: "Run /cookbook-start implementation to begin the implementation pipeline."

Stop after printing the summary.

## Step 3: Load Current Concern

Read `../agentic-cookbook/workflows/pipeline-concerns.json`. Find the entry whose `step` field matches the current step number from the `steps` array.

If the file does not exist, print: "Pipeline concerns file not found." and stop.

Print the concern header:

```
--- Step <current_step>/<total_steps>: <concern name> (<category>) ---
Summary: <summary>
```

## Step 4: Handle Skip

If `$ARGUMENTS` contains `skip`, record the result as N/A and go to Step 7.

## Step 5: Load Guideline

Read the guideline file at the path specified in the concern's `guideline_path`. If the file does not exist, print: "Guideline file not found: <path>. Marking as N/A." and record as N/A, then go to Step 7.

Strip the YAML frontmatter — only present the content section to save context.

## Step 6: Evaluate

### Planning Phase

**For "always" concerns** (core-engineering, testing categories):

Present the guideline content, then evaluate:

- Does this concern apply to the task described as: "<task_description>"?
- If **applicable**: explain how it applies and what the plan should include for this concern. Ask the user to confirm or adjust.
- If **not applicable**: explain why and mark as N/A. Ask the user to confirm.

**For "ask" concerns** (opt-in category):

Present the concern's `prompt` to the user. Based on their response:

- If opted in: read the guideline file, evaluate applicability, add to plan with specifics
- If opted out: record as N/A with reason "user opted out"

### Implementation Phase

The concern was already evaluated during planning. Now review the code:

1. Present the guideline content
2. Review the current code against this concern (use `git diff` or read relevant files)
3. If changes are needed: make them, then commit with a message referencing the concern
4. If no changes needed: note as "verified — already compliant"

Ask the user to confirm the assessment before recording.

## Step 7: Record Result

Append to the `results` array in `.cookbook/pipeline.json`:

```json
{
  "step": <step number>,
  "concern": "<concern name>",
  "status": "applicable" | "na",
  "notes": "<brief explanation>",
  "timestamp": "<ISO 8601>"
}
```

Increment `current_step` by 1. Write the updated state to `.cookbook/pipeline.json`.

## Step 8: Print Next Action

```
Step <current_step - 1>/<total_steps>: <concern> — <applicable/N/A>

Run /cookbook-next to continue, or /cookbook-next skip to skip the next step.
<remaining> steps remaining.
```

## Guards

- **Do not modify any files in `../agentic-cookbook/`.** Only read from it.
- **Load only one concern per invocation.** Do not read ahead or batch.
- **Do not read the full pipeline-concerns.json into context.** Read only the entry for the current step.
- **Always write updated state to disk.** The pipeline must be resumable.
- **Ask for user confirmation** before recording a result in planning phase. In implementation phase, confirm before committing code changes.
