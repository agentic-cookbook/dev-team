# YOLO Per-Session Architecture Design

**Date:** 2026-03-30
**Status:** Research complete, implementation pending

---

## Problem

YOLO mode is currently global — once enabled, it applies to ALL sessions across ALL projects. It should be per-session so each Claude Code session independently opts in.

## Key Findings

### Session ID availability

- The PermissionRequest hook receives `session_id` in its JSON input on stdin
- The `${CLAUDE_SESSION_ID}` variable is available in SKILL.md templates
- SessionStart and SessionEnd hooks also receive session context
- There is NO CLI command to list active sessions (`claude session list` doesn't exist)
- Session data is stored per-project directory, not centrally

### Proposed Architecture

**Session marker files** stored outside `~/.claude/` (user preference — keep YOLO state separate from Claude config):

```
/tmp/claude-yolo/           # or ~/.local/state/claude-yolo/
  {session-id}.json         # one file per active YOLO session
```

Each session file:
```json
{
  "session_id": "550e8400-...",
  "enabled_at": "2026-03-30T14:23:00Z",
  "project": "/Users/.../agentic-cookbook",
  "deny_list": "~/.claude/yolo-deny.json"
}
```

### Flow

1. **`/yolo on`** — writes session marker file using `${CLAUDE_SESSION_ID}`
2. **PermissionRequest hook** — checks if marker file exists for `session_id` from stdin JSON
   - Exists: apply deny-list logic, approve non-denied items
   - Missing: exit 1 (fall through to normal prompt — YOLO not active for this session)
3. **`/yolo off`** — deletes the session marker file
4. **SessionEnd hook** — auto-cleanup: deletes the session marker file
5. **Stale cleanup** — on SessionStart, delete any marker files older than 24h

### Hook Installation

The PermissionRequest hook stays in `~/.claude/settings.json` permanently — it's lightweight. When no session marker file exists, the hook exits immediately (exit 1 = fall through to normal prompt). Zero overhead for non-YOLO sessions.

This means `/yolo on` no longer needs to modify settings.json to add/remove the hook. Install it once, leave it forever.

### Settings.json Change

One-time installation:
```json
{
  "hooks": {
    "PermissionRequest": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "$HOME/.claude/hooks/yolo-approve-all.sh"
      }]
    }],
    "SessionEnd": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "$HOME/.claude/hooks/yolo-session-cleanup.sh"
      }]
    }]
  }
}
```

### Deny List Layering

1. Project-level: `.claude/yolo-deny.json` (checked first)
2. Global: `~/.claude/yolo-deny.json` (fallback)
3. Built-in defaults (if neither exists)

### Status Line

The status line script checks for the session marker file. Since it receives session data on stdin, it can check if the current session has an active YOLO marker.

### Open Questions

- **Marker file location**: `/tmp/claude-yolo/` (ephemeral, auto-cleans on reboot) vs `~/.local/state/claude-yolo/` (persists, needs manual/hook cleanup)
- **Should the hook be pre-installed or installed by /yolo on?** Pre-installed is simpler (no settings.json modification needed), but adds a hook that fires for every session even when YOLO is off
- **Multiple deny lists per session**: Should the session marker reference which deny list to use, or always use the global one?

## Current State (v3.0.0)

- Global on/off via PermissionRequest hook in `~/.claude/settings.json`
- Configurable deny list at `~/.claude/yolo-deny.json`
- Hook script at `~/.claude/hooks/yolo-approve-all.sh` with bash-based pattern matching
- `/yolo configure` for editing deny rules
- Status line indicator at `~/.claude/scripts/statusline.sh`
- Dragon warning art at `.claude/skills/yolo/references/warning.txt`
