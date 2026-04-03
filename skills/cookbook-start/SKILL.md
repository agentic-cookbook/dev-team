---
name: cookbook-start
version: "2.0.0"
description: "Initialize a cookbook planning or implementation pipeline. Creates the pipeline state file and prints instructions for /cookbook-next."
argument-hint: "<planning|implementation> [task description]"
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash(ls *), Bash(wc *), Bash(date *), AskUserQuestion
---

# Cookbook Start v2.0.0

## Startup

**First action**: If `$ARGUMENTS` is `--version`, print `cookbook-start v2.0.0` and stop — do not run the skill.

Otherwise, print `cookbook-start v2.0.0` as the first line of output, then proceed.

**Version check**: Read `${CLAUDE_SKILL_DIR}/SKILL.md` from disk and extract the `version:` field from frontmatter. If it differs from this skill's version (1.0.0), print:

> ⚠ This skill is running v2.0.0 but vA.B.C is installed. Restart the session to use the latest version.

Continue running — do not stop.

## Overview

Initialize a pipeline session for iterating through the cookbook's 38 guideline concerns one at a time. This creates a state file on disk so progress is tracked between invocations and sessions.

## Usage

```
/cookbook-start planning <task description>
/cookbook-start implementation <task description>
```

The first argument MUST be `planning` or `implementation`. Everything after it is the task description.

If no arguments are provided, ask the user:
1. Phase: planning or implementation?
2. What is the task?

## Step 1: Validate Arguments

Parse `$ARGUMENTS`:
- First word: phase (`planning` or `implementation`)
- Remaining words: task description

If the phase is not `planning` or `implementation`, print: "Phase must be 'planning' or 'implementation'." and stop.

If no task description is provided, ask the user: "What task are you planning/implementing?"

## Step 2: Check for Existing Pipeline

Check if `.cookbook/pipeline.json` exists.

If it exists, read it and print:

```
⚠ An existing pipeline was found:
  Phase: <phase>
  Task: <task description>
  Progress: step <current_step> of <total_steps>
  Completed: <N> applicable, <M> N/A

Resume the existing pipeline with /cookbook-next, or continue to overwrite it.
Overwrite? (yes/no)
```

If the user says no, stop. If yes, continue.

## Step 3: Load Concern Count

Read `../agentic-cookbook/workflows/pipeline-concerns.json`. If the file does not exist, print: "Pipeline concerns file not found at ../agentic-cookbook/workflows/pipeline-concerns.json. Is the cookbook repo available?" and stop.

Count the total number of entries.

## Step 4: Determine Step Range

**Planning phase**: All 38 steps (1–38).

**Implementation phase**: Check if a completed planning pipeline exists (`.cookbook/pipeline.json` with phase `planning` and `current_step > total_steps`). If it does:
- Extract only the steps marked as `applicable` from the planning results
- These become the implementation steps
- Print: "Loaded <N> applicable concerns from the completed planning session."

If no completed planning session exists:
- Ask the user: "No completed planning session found. Run all 38 steps, or provide a list of step numbers to review?"
- If the user provides step numbers, use those
- Otherwise, use all 38

## Step 5: Create Pipeline State

Write `.cookbook/pipeline.json`:

```json
{
  "phase": "<planning|implementation>",
  "current_step": 1,
  "total_steps": <N>,
  "steps": [<list of step numbers to process>],
  "task_description": "<what the user described>",
  "started": "<ISO 8601 timestamp>",
  "results": []
}
```

For planning, `steps` is `[1, 2, 3, ..., 38]`. For implementation with a completed plan, `steps` contains only the applicable step numbers.

## Step 6: Print Summary

```
=== Cookbook Pipeline Started ===
Phase: <planning|implementation>
Task: <task description>
Steps: <N> concerns to evaluate
State: .cookbook/pipeline.json

Run /cookbook-next to begin step 1.

Core Engineering (steps 1–15): always apply
Testing (steps 16–22): always apply
Opt-in Concerns (steps 23–38): ask per concern
```

## Guards

- **Do not modify any files in `../agentic-cookbook/`.** Only read from it.
- **Do not start evaluating concerns.** This skill only initializes the pipeline. `/cookbook-next` does the evaluation.
- **Do not read guideline files.** The pipeline skills load one file per step — not here.
