# Dev-Team Planning Todo

## In Progress

- **Cookbook sources for project-manager** — filling in guidelines, principles, compliance in the agentic-cookbook repo (see `planning/cookbook-requests.md`)

## Blocked

- **DB schema finalization** — requirements doc at `docs/planning/2026-04-03-initial-database-design.md`, waiting on DB specialist to produce final schema
- **Specialist script design** — how specialists execute in v2 (extend `run-specialty-teams.sh` or new script), blocked on DB
- **Database arbitrator backend** — `scripts/arbitrator/database/`, blocked on DB schema

## Todo

- **Recipe-reviewer disposition** — decide if it stays as standalone agent, becomes team-lead capability, or specialist mode
- **Absorbed agents cleanup** — `agents/specialist-interviewer.md` and `agents/specialist-code-pass.md` still exist, referenced by current workflows; can't delete until v2 replacements are built
- **Wire workflows to arbitrator** — update skill workflows to use `arbitrator.sh` instead of `db-*.sh` directly
- **Wire project-manager to project-storage** — connect the specialist's specialty-teams to call `project-storage.sh`
- **Update project-manager specialty-teams** — add cookbook artifact references once cookbook sources exist
- **Replace planning/ with .dev-team-project** — move this tracking to the project-storage-provider when ready

## Done (this session — 2026-04-04)

- DB schema v2 requirements doc
- DB schema design rules
- Terminology rename (workflow_runs → sessions, agent_runs → session_state)
- Arbitrator abstraction (markdown backend, 58 tests)
- Project-storage-provider (markdown backend, 64 tests)
- Project-manager specialist + 6 specialty-team files
- Cookbook requests doc
