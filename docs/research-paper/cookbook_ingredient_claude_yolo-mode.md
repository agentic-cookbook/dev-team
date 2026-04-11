---
id: 92daec8c-4388-4a34-bc0c-d3ce0ab8c724
title: "Yolo Mode (Permission Bypass Hook)"
domain: agentic-cookbook://ingredients/developer-tools/claude/yolo-mode
type: ingredient
version: 1.0.0
status: accepted
language: en
created: 2026-03-30
modified: 2026-04-05
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Toggleable PermissionRequest hook that auto-approves all Claude Code tool calls — a workaround for broken --dangerously-skip-permissions."
platforms:
  - macos
  - linux
  - windows
tags:
  - claude-code
  - permissions
  - hooks
  - workaround
depends-on: []
related: []
references:
  - https://github.com/anthropics/claude-code/issues/40241
  - https://github.com/anthropics/claude-code/issues/40136
  - https://code.claude.com/docs/en/permission-modes
  - https://code.claude.com/docs/en/hooks
approved-by: "approve-artifact v1.0.0"
approved-date: "2026-04-04"
---

# Yolo Mode (Permission Bypass Hook)

## Overview

A toggleable `PermissionRequest` hook that auto-approves all Claude Code tool calls without user confirmation. This is a workaround for `--dangerously-skip-permissions` being broken in Claude Code v2.1.x, where the flag fails to propagate to subagents ([anthropics/claude-code#40241](https://github.com/anthropics/claude-code/issues/40241)) and silently stops working after exiting Plan Mode ([anthropics/claude-code#40136](https://github.com/anthropics/claude-code/issues/40136)).

Unlike the CLI flag, the hook approach works because hooks are inherited by subagents (they read the same `settings.json`) and persist across mode transitions.

## Security Warning

```
╔══════════════════════════════════════════════════╗
║                                                  ║
║           ☠  HERE BE DRAGONS  ☠                  ║
║                                                  ║
║  Yolo mode auto-approves ALL permission prompts  ║
║  with zero safety checks.                        ║
║                                                  ║
║  This means Claude can:                          ║
║    • Run any shell command                       ║
║    • Edit or delete any file                     ║
║    • Push to any remote                          ║
║    • Do anything — without asking                ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

This recipe provides the same security posture as `--dangerously-skip-permissions`: **none**. It is intended for trusted local development environments where the user is actively monitoring Claude's output. It offers no protection against prompt injection, destructive commands, or unintended side effects.

**Do not use this in:**
- Shared CI/CD environments
- Production systems
- Environments with access to sensitive credentials or infrastructure
- Sessions where untrusted content (PRs, issues, external files) will be processed

## Behavioral Requirements

- **hook-auto-approves-all**: The PermissionRequest hook MUST return `{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}` for every permission prompt, unconditionally.
- **hook-propagates-to-subagents**: The hook MUST be installed in `~/.claude/settings.json` (user scope) so that all sessions and subagents inherit it.
- **toggle-on-installs-hook**: Enabling yolo mode MUST create the hook script at `~/.claude/hooks/yolo-approve-all.sh`, make it executable, and add the `PermissionRequest` entry to `~/.claude/settings.json` under `hooks`.
- **toggle-off-removes-hook**: Disabling yolo mode MUST remove the `PermissionRequest` key from `hooks` in `~/.claude/settings.json`. It SHOULD leave the hook script on disk (harmless, avoids recreation).
- **preserve-existing-hooks**: Toggling on or off MUST NOT modify any other hook entries in `settings.json` (e.g., `SessionStart`, `UserPromptSubmit`, `PostToolUse`, `Stop`, `SessionEnd`).
- **warn-before-enable**: Enabling MUST display a security warning and require explicit user confirmation before proceeding.
- **status-check**: The skill MUST be able to report whether yolo mode is currently active by inspecting the `PermissionRequest` key in `~/.claude/settings.json`.
- **idempotent-toggle**: Enabling when already enabled, or disabling when already disabled, SHOULD print a message and stop without modifying files.

## Components

### Hook Script

**Path:** `~/.claude/hooks/yolo-approve-all.sh`

```bash
#!/bin/bash
echo '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
exit 0
```

The script:
- Receives permission request JSON on stdin (ignored — approves unconditionally)
- Returns the PermissionRequest hook-specific output with `"behavior": "allow"`
- Exits with code 0 (success — action proceeds)

### Settings.json Hook Entry

**Location:** `~/.claude/settings.json` → `hooks.PermissionRequest`

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/yolo-approve-all.sh"
          }
        ]
      }
    ]
  }
}
```

- **matcher**: Empty string matches all tool types
- **type**: `command` — executes a shell script
- **command**: Uses `$HOME` for portability across environments

### Scope

| Scope | Affected? | Why |
|-------|-----------|-----|
| Current session | Yes | Hook fires on every permission prompt in the active session |
| Subagents (Agent tool) | Yes | Subagents read the same `~/.claude/settings.json` |
| Plan mode transitions | Yes | Hooks persist across mode changes (unlike the CLI flag) |
| New sessions | Yes | Hook is in user-level settings, applies to all future sessions |
| Headless mode (`-p`) | No | `PermissionRequest` does not fire in non-interactive mode — use `PreToolUse` with `permissionDecision` instead |
| Other users | No | User-level `~/.claude/settings.json` is per-user |
| Project-level overrides | No | Only installed at user scope; project `.claude/settings.json` is not modified |

### Commands

An implementation MUST provide these operations:

| Operation | Effect |
|-----------|--------|
| Enable | Show warning, confirm, install hook script and settings entry |
| Disable | Remove `PermissionRequest` from settings, print confirmation |
| Status | Check settings and report whether yolo mode is active |

## Appearance

Not applicable — YOLO mode is a CLI configuration tool with terminal text output only.

## States

| State | How to detect | Behavior |
|-------|---------------|----------|
| Enabled | `hooks.PermissionRequest` exists in `~/.claude/settings.json` with `yolo-approve-all.sh` | All permission prompts auto-approved |
| Disabled | `hooks.PermissionRequest` absent or does not reference `yolo-approve-all.sh` | Normal permission prompts shown |

## Accessibility

Not applicable — this is a CLI tool with no visual UI.

## Conformance Test Vectors

| ID | Requirements | Input | Expected |
|----|-------------|-------|----------|
| yolo-001 | hook-auto-approves-all | Pipe any JSON to the hook script | stdout contains `"behavior":"allow"`, exit code 0 |
| yolo-002 | toggle-on-installs-hook | Run enable operation and confirm | Hook script exists, is executable; `~/.claude/settings.json` has `hooks.PermissionRequest` |
| yolo-003 | toggle-off-removes-hook | Run disable operation | `hooks.PermissionRequest` removed from `~/.claude/settings.json`; other hooks intact |
| yolo-004 | preserve-existing-hooks | Run enable then disable | `hooks.SessionStart`, `hooks.UserPromptSubmit`, etc. unchanged throughout |
| yolo-005 | status-check | Run status when enabled | Output indicates enabled |
| yolo-006 | status-check | Run status when disabled | Output indicates disabled |
| yolo-007 | idempotent-toggle | Run enable twice | Second invocation reports already enabled, no settings change |
| yolo-008 | warn-before-enable | Run enable | Security warning displayed before confirmation prompt |
| yolo-009 | hook-propagates-to-subagents | Enable, then spawn Agent tool subagent that runs Edit | Edit proceeds without permission prompt |

## Edge Cases

- **settings.json does not exist**: The skill should create it with the hooks entry. This is unlikely in practice — Claude Code creates this file on first run.
- **hooks key does not exist**: The skill should create the `hooks` object and add `PermissionRequest` to it.
- **Malformed settings.json**: If the file is not valid JSON, the skill should warn the user and stop without modifying it.
- **Hook script deleted but settings entry remains**: The hook will fail silently (command not found). The status operation should check both the settings entry and script existence.
- **Multiple PermissionRequest entries**: If someone manually added other PermissionRequest hooks, the disable operation removes the entire `PermissionRequest` key. This is acceptable — custom PermissionRequest hooks are rare and the user can re-add them.
- **Session restart needed**: Hook changes may not take effect in the current session. The skill should note this in the enable confirmation.

## Configuration

This ingredient has no configurable options.

## Deep Linking

Not applicable — CLI skill, not a navigable resource.

## Localization

| String Key | Default (en) | Context |
|-----------|-------------|---------|
| yolo.warning.title | HERE BE DRAGONS | Warning box header |
| yolo.enabled | Yolo mode enabled. All permission prompts will be auto-approved. | Enable confirmation |
| yolo.disabled | Yolo mode disabled. Permission prompts restored. | Disable confirmation |
| yolo.status.on | Yolo mode is ON. All permission prompts are auto-approved. | Status when enabled |
| yolo.status.off | Yolo mode is OFF. Normal permission prompts are active. | Status when disabled |
| yolo.already.enabled | Yolo mode is already enabled. | Idempotent enable |
| yolo.already.disabled | Yolo mode is already disabled. | Idempotent disable |

## Accessibility Options

Not applicable — CLI tool.

## Feature Flags

Not applicable — the hook itself is the toggle mechanism.

## Analytics

Not applicable — local CLI tool, no telemetry.

## Privacy

- **Data collected**: None
- **Storage**: Hook script stored at `~/.claude/hooks/yolo-approve-all.sh`; configuration in `~/.claude/settings.json`
- **Transmission**: No data leaves the device
- **Retention**: Persists until the disable operation is run

## Logging

Not applicable — the hook script produces no log output. The skill prints status messages to stdout.

## Platform Notes

- **macOS/Linux**: Hook script uses `#!/bin/bash` shebang and `chmod +x`. Works on any POSIX system with bash.
- **Windows**: Hook script requires Git Bash, WSL, or another bash-compatible shell. The `$HOME` variable in the settings command path resolves correctly in these environments. Native PowerShell is not supported.

## Design Decisions

- **PermissionRequest hook over PreToolUse**: PermissionRequest fires specifically on permission dialogs. PreToolUse fires on every tool call and requires returning `permissionDecision` — more complex, but also works in headless mode. We chose PermissionRequest for simplicity since the primary use case is interactive sessions.
- **User-level scope only**: The hook is installed in `~/.claude/settings.json` (not project-level) because permission bypass is a personal environment choice, not a project setting that should be committed to a repo.
- **Leave hook script on disk after disable**: Deleting the script saves nothing meaningful and means it must be recreated on next enable. Leaving it avoids unnecessary file I/O.
- **Remove entire PermissionRequest key on disable**: Simpler than surgically removing a single entry. Custom PermissionRequest hooks are rare enough that this trade-off is acceptable.

## Compliance

| Check | Status | Category |
|-------|--------|----------|
| [secure-log-output](agentic-cookbook://compliance/security#secure-log-output) | passed | Security — no credentials or PII in output |
| [data-minimization](agentic-cookbook://compliance/privacy-and-data#data-minimization) | passed | Privacy — no user data collected |
| [destructive-action-guard](agentic-cookbook://compliance/user-safety#destructive-action-guard) | passed | Safety — warning + confirmation before enable |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-30 | Mike Fullerton | Initial creation |
