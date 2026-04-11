# Tools

User-facing Claude Code skills, guidance rules, and scripts for interacting with the Agentic Cookbook ecosystem.

## Purpose

Companion repository to the Agentic Cookbook, providing the installable skills and rules that projects use to interact with the cookbook workflow. Delivers reusable Claude Code skills for project authoring, linting, planning, and cookbook integration.

## Key Features

- 20 Claude Code skills (invoked via slash commands)
- 8 guidance rules for authoring standards and workflow
- Scripts for cookbook integration and maintenance
- No build system required — pure markdown skill definitions and shell scripts

## Tech Stack

- **Format:** Markdown skill definitions (SKILL.md files), markdown rules
- **Runtime:** Claude Code (skills invoked via slash commands)
- **No build system** — no package.json, pyproject.toml, or other build configuration

## Status

Recently completed / stable.

## Related Projects

- [Cookbook](../../cookbook/docs/project/description.md) — the knowledge base these tools operate on
- [Dev Team](../../dev-team/docs/project/description.md) — multi-agent platform
- [Roadmaps](../../roadmaps/docs/project/description.md) — feature planning system
