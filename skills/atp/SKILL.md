---
name: atp
version: 0.4.0
description: Agentic Team Pipeline — load a team from teams/<name>/ and drive it through the conductor. Subcommands: list, describe, plan, run, rollcall. Wider discovery roots are a follow-up.
argument-hint: <subcommand> [team] — list | describe <team> | plan <team> --goal <text> [--dispatcher mock|claude-code] [--db <path>] | run <team> [--dispatcher mock|claude-code] [--db <path>] | rollcall [team] [--format table|json]
---

# atp v0.4.0

## Status

Phase 1 — subcommands wired end-to-end against `teams/devteam/`, `teams/puppynamingteam/`, and `teams/projectteam/`. Wider discovery (`~/.agentic-teams/`, `~/.claude/plugins/cache/`) is follow-up work.

## Startup

If `$ARGUMENTS` is `--version`, print `atp v0.4.0` and stop.

Otherwise, shell out to the CLI with the remaining arguments and stream its output verbatim:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/atp/scripts/atp_cli.py $ARGUMENTS
```

## Subcommands

- `atp list` — print discovered teams in `./teams/`.
- `atp describe <team>` — print a team's manifest (specialists + specialties).
- `atp plan <team> --goal <text> [--dispatcher mock|claude-code] [--db <path>]` — drive the team's `planner` team-lead to emit a roadmap for `<goal>`. Dispatches one planner per speciality under agent name `<specialist>-<speciality>-planner`; each returns `{plan_nodes, depends_on}` which land in the arbitrator as `plan_node` rows + `node_dependency` edges. Prints the `roadmap_id` on stdout (one line). Requires `team-leads/planner.md` on the team.
- `atp run <team> [--dispatcher mock|claude-code] [--db <path>]` — build a one-node-per-specialty demo roadmap for the team and run it through the conductor. `--dispatcher mock` uses canned responses; `--dispatcher claude-code` shells out to the real CLI.
- `atp rollcall [team] [--format table|json] [--concurrency N] [--timeout S]` — discover every team-lead, specialist-worker, and specialist-verifier under `./teams/` (or under a single `team` if given) and ping each one through the integration surface. Prints a table (default) or one NDJSON line per role. Exit code is `0` if every role responds, `2` if any role errors or times out. v1 uses a scripted in-process runner that proves discovery + integration surface + formatting without an LLM; the real-LLM variant lives under `testing/functional/tests/rollcall/` and is gated by `AGENTIC_REAL_LLM_SMOKE=1`.

The mock dispatcher auto-generates a response for every worker in the team's manifest plus the scheduler pair, so `atp run` always has a complete canned response set regardless of team size. `atp plan --dispatcher mock` similarly fabricates one stub plan_node per speciality so mock planning is a no-LLM smoke test.

## Follow-ups

- Discovery beyond `./teams/` — `~/.agentic-teams/`, `~/.claude/plugins/cache/`.
- `required_atp_version` gate on team.md frontmatter.
- `atp execute <roadmap>` — run a previously-planned roadmap end-to-end, closing the plan → execute loop.
- Interactive planner team-lead — v1 planner is non-interactive. Follow-up allows the planner to ask clarifying questions mid-plan.
