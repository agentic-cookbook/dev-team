# Agentic Interview Team

A multi-agent product discovery interview system. Helps users fully scope products they want to build through structured and exploratory questioning.

## Architecture

Three repos:
- **This repo** — the interview system (agents, skills, specialist research)
- **agentic-cookbook** — upstream knowledge (principles, guidelines, compliance)
- **User's interview repo** — per-user data (profiles, transcripts, analyses, knowledge)

## Repository Structure

```
agents/                  # Subagent definitions
  transcript-analyzer.md   # Recommends specialists, identifies gaps
  specialist-interviewer.md # Generates domain-specific questions
  specialist-analyst.md     # Deep analysis of answers
skills/
  interview/
    SKILL.md               # The meeting leader — main entry point
rules/
research/
  specialists/             # 18 specialist question sets (12 domain + 6 platform)
  cookbook-specialist-mapping.md
  agent-patterns.md
  conversational-patterns.md
planning/
  design-spec.md           # Full design specification
```

## Local Testing

Symlinks in `.claude/` point to top-level dirs for local testing. These are gitignored.

To test: `cd` into this repo and invoke `/interview`.

## Config

System config: `~/.agentic-interviewer/config.json`

```json
{
  "interview_repo": "<path to user's interview repo>",
  "cookbook_repo": "<path to agentic-cookbook>",
  "interview_team_repo": "<path to this repo>",
  "user_name": "<user name>",
  "authorized_repos": []
}
```
