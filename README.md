# Agentic Interview Team

A multi-agent product discovery interview system that helps users fully scope products they want to build through structured and exploratory questioning.

## How It Works

A meeting leader skill orchestrates a team of specialists — domain experts (security, accessibility, UI/UX, architecture, etc.) and platform experts (iOS, Windows, Android, web, database). Each specialist has a paired analyst that deeply analyzes every answer to surface insights, gaps, and new questions.

The system produces a folder of timestamped markdown transcripts and analyses that an LLM consumes when planning and building the product.

## Architecture

```
┌──────────────────────────────────────────┐
│          Meeting Leader (Skill)          │
│  Orchestrates, talks to user, writes     │
│  transcripts, maintains checklist        │
└──────────┬──────────┬──────────┬─────────┘
           │          │          │
    ┌──────▼──┐ ┌─────▼────┐ ┌──▼──────────┐
    │Transcript│ │Specialist│ │ Specialist  │
    │Analyzer  │ │Interviewer│ │  Analyst   │
    │          │ │(per domain)│ │(per domain)│
    └──────────┘ └──────────┘ └─────────────┘
```

## Three Repos

| Repo | Purpose |
|------|---------|
| **agentic-interview-team** (this) | The system — agents, skills, specialist research |
| **agentic-cookbook** | Upstream knowledge — principles, guidelines, compliance |
| **User's interview repo** | Per-user data — profiles, transcripts, analyses, knowledge |

## Specialists

### Domain (12)
Security, Accessibility, Reliability, UI/UX & Design, Software Architecture, Testing & QA, Networking & API, Code Quality, DevOps & Observability, Localization & I18n, Development Process, Data & Persistence

### Platform (6)
iOS / Apple Platforms, Windows, Android, Web Frontend, Web Backend / Services, Database

## Getting Started

1. Clone this repo and the agentic-cookbook as peers
2. Create a personal interview repo
3. Run `/interview` from any project directory
4. On first run, the skill creates `~/.agentic-interviewer/config.json`

## Repository Structure

```
agents/                    # Subagent definitions
skills/interview/          # The meeting leader skill
rules/                     # (future)
research/
  specialists/             # 18 specialist question sets
  cookbook-specialist-mapping.md
  agent-patterns.md
  conversational-patterns.md
planning/
  design-spec.md           # Full design specification
```
