# Memory

## Project Clones (`~/projects/`)

See [project-clones.md](project-clones.md) for full details.

Key points:
- **QualityTime1-4** are all clones of `QualityTimeStudios/QualityTime`
- **temporal1-4** are all clones of `temporal-company/temporal`
- When modifying a shared repo, only modify one clone then pull the rest
- **mikefullerton.com** uses `gh-pages` as default branch (not `main`)
- **market-research** is a Python CLI tool for evaluating indie project ideas (Anthropic API + Tavily)

## Dotfiles (Google Drive)

- Repo: `Shared-Project-Helpers/dotfiles` — lives on Google Drive at `~/Library/CloudStorage/GoogleDrive-.../My Drive/dotfiles/`
- `claude/scripts/lib/common.sh` — shared functions (get_repo_name, load_prompt, send_notification)
- `docs/code-review-pipeline.md` — pipeline architecture docs
- Workflow rules live in global `~/.claude/CLAUDE.md` — projects should NOT duplicate them
- `claude/memory/` — symlinked to `~/.claude/memory/` via `install.sh`

## New Machine Setup

```bash
# Clone to Google Drive (or anywhere — install.sh derives paths automatically)
git clone git@github.com:Shared-Project-Helpers/dotfiles.git "<Google Drive>/dotfiles"
<Google Drive>/dotfiles/install.sh   # symlinks CLAUDE.md, settings.json, scripts, memory
brew install terminal-notifier jq
# Then clone all projects — see project-clones.md for full list
```

## Code Review Pipeline

8 agents: General Reviewer, Perf Reviewer, Safety Reviewer, Test Reviewer, Fix Agent, Issue Fix Agent, Merge Checker, Test Runner. Reusable workflows in `Shared-Project-Helpers/workflows`. Full architecture in `dotfiles/docs/code-review-pipeline.md`.
