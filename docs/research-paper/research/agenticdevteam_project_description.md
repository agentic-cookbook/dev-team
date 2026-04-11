# Dev Team

A Claude Code plugin providing a multi-agent platform for product discovery, analysis, and project building with 20+ specialists and 232 specialty teams.

## Purpose

The Agentic Cookbook Dev Team is a distributed AI team collaboration system. It combines structured specialist expertise with flexible interview workflows to help users scope, plan, and build software. Distributed via the agentic-cookbook marketplace as a Claude Code plugin. Not yet ready for general use.

## Key Features

- 20+ specialist agent definitions with deep domain expertise
- 232 specialty teams for cross-functional collaboration
- Arbitrator system for routing questions to appropriate specialists
- Interview workflows for product discovery and scoping
- Project storage with SQLite backend
- Web dashboard for visualization
- 122+ contract tests with deterministic test runner

## Tech Stack

- **Language:** Python 3.10+
- **Database:** SQLite 3 (shared backend, v2 storage-provider unification in progress)
- **Agents:** Markdown definitions for specialists and specialty teams
- **Dashboard:** HTML/JavaScript, GitHub Pages
- **Testing:** pytest (122+ contract tests)

## Architecture

Plugin architecture with an arbitrator that routes user queries to appropriate specialist agents. Specialists are defined as markdown manifests with expertise domains, interview protocols, and output formats. A project-storage layer persists context across sessions in SQLite.

## Status

Active development — not yet ready for general use.

## Related Projects

- [Cookbook](../../cookbook/docs/project/description.md) — knowledge base consumed by the dev team agents
- [Tools](../../tools/docs/project/description.md) — companion skills and rules
- [Roadmaps](../../roadmaps/docs/project/description.md) — feature planning system
