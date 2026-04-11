# Terminal Progress & Status Line Research

Research into displaying real-time progress from Claude Code rules/skills, covering the status line API, ANSI escape sequences, and terminal rendering limitations.

## Status Line API

### Configuration

```json
// ~/.claude/settings.json (global) or .claude/settings.json (project)
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/scripts/statusline.sh",
    "padding": 2
  }
}
```

- `type`: must be `"command"` (only type available)
- `command`: path to script or inline shell command
- `padding`: optional horizontal spacing in characters

### Stdin JSON Fields

The status line script receives structured JSON via stdin with these fields:

**Model & Config**: `model.id`, `model.display_name`, `output_style.name`

**Workspace**: `cwd`, `workspace.current_dir`, `workspace.project_dir`, `session_id`, `transcript_path`, `version`

**Context Window**: `context_window.total_input_tokens`, `context_window.total_output_tokens`, `context_window.context_window_size`, `context_window.used_percentage`, `context_window.remaining_percentage`, `context_window.current_usage.input_tokens`, `context_window.current_usage.output_tokens`, `context_window.current_usage.cache_creation_input_tokens`, `context_window.current_usage.cache_read_input_tokens`, `exceeds_200k_tokens`

**Costs & Duration**: `cost.total_cost_usd`, `cost.total_duration_ms`, `cost.total_api_duration_ms`, `cost.total_lines_added`, `cost.total_lines_removed`

**Rate Limits** (Claude.ai Pro/Max only): `rate_limits.five_hour.used_percentage`, `rate_limits.five_hour.resets_at`, `rate_limits.seven_day.used_percentage`, `rate_limits.seven_day.resets_at`

**Vim Mode**: `vim.mode` (`"NORMAL"` or `"INSERT"`, absent if disabled)

**Agent & Worktree**: `agent.name`, `worktree.name`, `worktree.path`, `worktree.branch`, `worktree.original_cwd`, `worktree.original_branch`

### Capabilities

- **Multi-line**: each `echo` creates a separate row
- **ANSI colors**: 8/16 color SGR codes supported (e.g., `\033[32m`)
- **OSC 8 hyperlinks**: clickable links (requires iTerm2/Kitty/WezTerm, not Terminal.app)
- **Any language**: bash, python, node, zsh — anything that reads stdin and writes stdout

### Refresh Triggers

Status line updates **only** on these events:
- After each new assistant message
- When permission mode changes
- When vim mode toggles
- Debounced at 300ms

**Critical limitation**: does NOT update mid-turn. If Claude is reading 18 files in one turn, the status line won't refresh until the turn ends.

### File-Based Progress Pattern

A rule can write progress to a temp file and the status line can read it, but updates only appear between turns:

```bash
#!/bin/bash
# statusline script
PROGRESS_FILE="/tmp/cookbook-progress.txt"
if [ -f "$PROGRESS_FILE" ]; then
  cat "$PROGRESS_FILE"
fi
```

Rule instructs Claude to write `/tmp/cookbook-progress.txt` at each step. Lag: only updates between turns, not during.

## ANSI Escape Sequences for Sticky Status Lines

### The DECSTBM Technique

Used by `apt`, `docker build`, `npm install` — confines scrolling to upper rows, keeps bottom line(s) fixed.

#### Key Escape Sequences

| Sequence | Name | Purpose |
|---|---|---|
| `\033[<top>;<bottom>r` | DECSTBM | Set scroll region (1-based rows) |
| `\0337` | DECSC | Save cursor position |
| `\0338` | DECRC | Restore cursor position |
| `\033[<row>;<col>H` | CUP | Move cursor to absolute position |
| `\033[K` | EL | Erase to end of line |
| `\033[2K` | EL | Erase entire line |
| `\033[r` | DECSTBM reset | Reset scroll region to full terminal |

#### Complete Working Example

```bash
#!/usr/bin/env bash
# sticky-status-demo.sh

cleanup() {
    printf '\0337'
    printf '\033[0;%dr' "$LINES"
    printf '\033[%d;0f' "$LINES"
    printf '\033[K'
    printf '\0338'
    printf '\033[?25h'
}
trap cleanup EXIT INT TERM

LINES=$(tput lines)
COLS=$(tput cols)

# Reserve bottom line
echo ""
printf '\0337'
printf '\033[1;%dr' "$((LINES - 1))"
printf '\0338'
printf '\033[1A'

update_status() {
    local msg="$1"
    printf '\0337'
    printf '\033[%d;1H' "$LINES"
    printf '\033[K'
    printf '\033[7m %-*s\033[0m' "$((COLS - 1))" "$msg"
    printf '\0338'
}

# Usage
total=18
for i in $(seq 1 $total); do
    update_status "Reading principle $i/$total: item-$i"
    echo "Processing principle $i..."
    sleep 0.3
done
```

### How APT Does It

From Julien Palard's blog ("How APT does its fancy progress bar"):

1. Print newline to make space
2. Save cursor (`\0337`)
3. Set scroll region to rows 1..(LINES-1) (`\033[0;Nr`)
4. Restore cursor (`\0338`)
5. Move up one line (`\033[1A`)
6. For each update: save cursor, jump to last row, clear line, write status, restore cursor

### Libraries by Language

**Python**:
- [bottombar](https://github.com/evalf/bottombar) — purpose-built, zero dependencies, context manager API, handles SIGWINCH resize
- [rich](https://github.com/Textualize/rich) — `Progress` with `console.print` above (not true scroll region)
- [pdanford/TerminalScrollRegionsDisplay](https://github.com/pdanford/TerminalScrollRegionsDisplay) — multiple scroll regions
- curses stdlib — `setscrreg()` method

**Node.js**:
- [terminal-kit](https://www.npmjs.com/package/terminal-kit) — full TUI with scroll regions
- [blessed](https://github.com/chjj/blessed) — curses-like TUI with `smartCSR`
- [ink](https://github.com/vadimdemedes/ink) — React-based terminal UI (what Claude Code uses)
- [bottom-bar](https://www.npmjs.com/package/bottom-bar) — bottom bar display

**Rust**:
- [indicatif](https://github.com/console-rs/indicatif) — `MultiProgress` with `println!` above
- [status-line](https://github.com/pkolaczk/status-line) — generalized status display

**Shell/Go**:
- [shox](https://github.com/liamg/shox) — ANSI proxy, intercepts and adjusts coordinates
- `tput csr` — portable scroll region: `tput csr 0 $((LINES-2))`

## Claude Code Terminal Rendering

### Architecture

Claude Code is built with React + Ink. Bash tool commands run via `child_process.spawn` with **piped stdio (not a PTY)**. Commands see `isatty(stdout) == false`.

### ANSI Support Matrix

| Escape type | Works in Claude Code? |
|---|---|
| Basic 8/16 colors (SGR 30-37, 40-47, 90-97) | Yes |
| 256 color (SGR 38;5;N) | Partial |
| True color 24-bit (SGR 48;2;R;G;B) | No — stripped, shows literal brackets |
| Bold, italic, underline | Yes |
| Cursor positioning (CUP, CUU, etc.) | No — ignored or causes corruption |
| Scroll regions (DECSTBM) | No — ignored |
| Alternate screen buffer | No — corrupts session on resume |
| Mouse tracking | No — corrupts terminal |

### Known Issues

- [#18728](https://github.com/anthropics/claude-code/issues/18728) — basic ANSI colors DO work (confirmed by reporter)
- [#16790](https://github.com/anthropics/claude-code/issues/16790) — true color escape sequences stripped
- [#13441](https://github.com/anthropics/claude-code/issues/13441) — line wrapping breaks ANSI codes mid-sequence
- [#18418](https://github.com/anthropics/claude-code/issues/18418) — CSI sequences stored in session JSONL, corrupt terminal on resume
- [#9881](https://github.com/anthropics/claude-code/issues/9881) — feature request for PTY support (227+ upvotes)
- [#16786](https://github.com/anthropics/claude-code/issues/16786) — stack overflow parsing complex ANSI output
- [#32632](https://github.com/anthropics/claude-code/issues/32632) — escape codes leak into git commit messages

### Why Cursor Positioning Doesn't Work

Ink owns the terminal and manages all cursor positioning itself. Raw cursor/scroll codes from Bash output conflict with Ink's rendering. The output pipeline:

1. Child process stdout captured via pipes (not TTY)
2. Text processed by Ink's layout engine
3. Basic SGR preserved, cursor/scroll codes stripped or cause corruption
4. Escape sequences stored in session JSONL — replay corrupts terminal

### Hook Output

Hook stdout is parsed as JSON (control decisions) or plain text context. stderr goes to verbose mode only (`Ctrl+O`). No mechanism for hooks to write ANSI codes that reach the terminal.

## Practical Solutions for Rule Progress

### What Works Today

1. **Inline text output** — rule instructs Claude to print progress lines that scroll with conversation. Simple, universal, no infrastructure. This is what we implemented in `rules/cookbook.md`.

2. **Status line + temp file** — rule writes to temp file, status line reads it. Only updates between turns, not mid-turn.

### What Doesn't Work

- ANSI scroll regions from Bash tool — ignored/corrupts Claude Code
- Cursor positioning from hooks — output captured, not rendered
- Mid-turn status line updates — no refresh trigger during a turn

### Future Possibilities

- **Custom terminal app with skill progress hook** — a native terminal hosting Claude Code could provide an API for skills to update a dedicated progress area. This bypasses all ANSI/Ink limitations since the terminal app controls rendering.
- **PTY support in Claude Code** ([#9881](https://github.com/anthropics/claude-code/issues/9881)) — if added, would enable ANSI scroll regions from Bash commands.

## References

- [How APT does its fancy progress bar](https://mdk.fr/blog/how-apt-does-its-fancy-progress-bar.html) — Julien Palard
- [Build your own Command Line with ANSI escape codes](https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html) — Li Haoyi
- [VT102 User Guide Chapter 5](https://vt100.net/docs/vt102-ug/chapter5.html) — DEC specification for DECSTBM
- [ANSI Escape Sequences cheat sheet](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797)
- [Claude Code statusLine docs](https://code.claude.com/docs/en/statusline)
- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- [Ink - React for interactive CLI apps](https://github.com/vadimdemedes/ink)
- [ccstatusline npm package](https://github.com/sirmalloc/ccstatusline) — community statusline formatter
