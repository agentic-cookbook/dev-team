---
name: devteam
version: 0.1.0
description: Hand a goal to the Dev Team. One prompt in, one roadmap out. Wraps `atp plan devteam` so the user never sees /atp. Example — `/devteam build a macOS markdown app with side-by-side preview and JSON-based themes`.
argument-hint: <free-text goal — what you want the dev team to build or analyze>
---

# devteam v0.1.0

## What this does

Forwards `$ARGUMENTS` to the Dev Team as a planning goal. Under the
hood this is `atp plan devteam --goal "$ARGUMENTS"` — the Dev Team's
`planner` team-lead asks every speciality what plan_nodes its scope
needs, and stitches the results into a roadmap. The roadmap lives in
the arbitrator and can be executed later.

The user does not need to know about `atp`.

## Startup

If `$ARGUMENTS` is `--version`, print `devteam v0.1.0` and stop.

If `$ARGUMENTS` is empty, print:

```
devteam: missing goal. Describe what you want built — e.g.
  /devteam build a macOS markdown app with side-by-side preview
```

…and stop with a non-zero exit.

Otherwise, shell out to `atp plan` and stream its output verbatim:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/atp/scripts/atp_cli.py plan devteam --goal "$ARGUMENTS"
```

`atp plan` prints the `roadmap_id` on stdout. Relay that line back to
the user unchanged. Do not paraphrase — the caller may want to pipe
the id into a later `atp execute <roadmap>` invocation.

## Dispatcher

Defaults to the real `claude-code` dispatcher (the goal is to plan for
real, not smoke-test). If the user explicitly appends `--mock`, rewrite
it as `--dispatcher mock` when building the `atp plan` invocation so
the mock path runs without an LLM.

## What this is not

- Not execution. v1 ends at a roadmap. `atp execute <roadmap>` (which
  will run the plan end-to-end) is a follow-up. Until it ships, the
  user takes the `roadmap_id` and runs `atp run devteam` or inspects
  the arbitrator directly.
- Not a conversation. The v1 `planner` team-lead is non-interactive —
  the planner does not ask clarifying questions. If the goal is
  ambiguous, the resulting roadmap will reflect the planner's best
  interpretation. Interactive planning is a follow-up.
