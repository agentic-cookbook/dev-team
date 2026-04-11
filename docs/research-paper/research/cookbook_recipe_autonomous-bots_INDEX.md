---
id: b8e2c4a1-7f3d-4e9b-a6c8-2d1e5f4b3a7c
title: "Autonomous Dev Bots"
domain: agentic-cookbook://recipes/autonomous-dev-bots/INDEX
type: reference
version: 1.0.0
status: accepted
language: en
created: 2026-03-28
modified: 2026-03-28
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Recipes for autonomous agent processes that run continuously, triggered by development events, using the cookbook as their source of truth."
platforms: []
tags:
  - automation
  - agents
  - ci
  - review
depends-on: []
related:
  - agentic-cookbook://workflows/code-review
references: []
---

# Autonomous Dev Bots

Recipes for long-running, event-driven agent processes that serve the development lifecycle. These are daemons — they run continuously in the background, watch for events (webhooks, polls), and respond autonomously until they need a human decision.

**Common traits:**
- Event-triggered (webhook, cron, or poll)
- Multi-phase with sequential gating (pass/fail between phases)
- Tool-using (CLI tools, APIs, linters)
- Structured output (PR reviews, reports, comments)
- Human escalation point (runs autonomously but knows when to stop and ask)
- Runs on daemon infrastructure (OpenClaw, launchd, systemd, CI)
- Distinct bot personas (GitHub Apps)

## Recipes

| Recipe | Status | Summary |
|--------|--------|---------|
| [PR Review Pipeline](pr-review-pipeline.md) | wip | Three-phase automated review of cookbook contributions |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-28 | Mike Fullerton | Initial creation |
