# --dangerously-skip-permissions Known Bugs & Workaround

**Date:** 2026-03-30
**Claude Code version:** 2.1.87 (bugs present since ~2.1.80)
**Status:** Open bugs, workaround available

---

## Summary

`--dangerously-skip-permissions` (equivalent to `--permission-mode bypassPermissions`) is broken in Claude Code v2.1.x. Permission prompts appear despite the flag being passed. The root cause is a combination of two bugs:

1. **Bypass doesn't propagate to subagents** — the Agent tool spawns processes that don't inherit the parent's permission mode
2. **Bypass breaks after exiting Plan Mode** — the flag is silently lost when transitioning out of plan mode

A `PermissionRequest` hook workaround reliably bypasses all prompts where the CLI flag fails.

---

## Bug 1: Subagent Permission Propagation

**Issue:** [anthropics/claude-code#40241](https://github.com/anthropics/claude-code/issues/40241)
**Platform:** macOS (confirmed), likely all platforms
**Has repro:** Yes

When running with `--dangerously-skip-permissions`, subagents spawned via the Agent tool still prompt for permission on every Edit/Write/Bash tool call. The bypass flag only applies to the parent session.

**Impact:** Any workflow using plugins, skills, or explicit Agent tool calls will see permission prompts for every tool call in every subagent. With 10+ plugins enabled (superpowers, code-review, feature-dev, etc.), this creates a flood of prompts.

**Reproduction:**
1. Run `claude --dangerously-skip-permissions`
2. Ask Claude to spawn a subagent via the Agent tool that makes Edit calls
3. Every Edit call in the subagent prompts for permission

---

## Bug 2: Plan Mode Permission Reset

**Issue:** [anthropics/claude-code#40136](https://github.com/anthropics/claude-code/issues/40136)
**Platform:** Windows (confirmed), macOS (confirmed in practice)
**Has repro:** Yes

Entering and exiting Plan Mode causes the `--dangerously-skip-permissions` flag to stop working. After returning to normal execution mode, Claude prompts for permissions on all tool calls.

**Reproduction:**
1. Start Claude Code with `--dangerously-skip-permissions`
2. Use the session normally (no permission prompts, as expected)
3. Enter Plan Mode
4. Exit Plan Mode back to normal execution
5. Permission prompts now appear for all tool calls

---

## Related Issues

| Issue | Title | Status |
|-------|-------|--------|
| [#37903](https://github.com/anthropics/claude-code/issues/37903) | --dangerously-skip-permissions sometimes still asks for permissions | Open |
| [#36192](https://github.com/anthropics/claude-code/issues/36192) | --dangerously-skip-permissions does not bypass Edit permission prompts | Open |
| [#40328](https://github.com/anthropics/claude-code/issues/40328) | --dangerously-skip-permissions does not bypass runtime tool execution prompts | Open (dup) |
| [#39608](https://github.com/anthropics/claude-code/issues/39608) | --worktree flag results in downgrade from --dangerously-skip-permissions | Open |
| [#39588](https://github.com/anthropics/claude-code/issues/39588) | Single-dash -dangerously-skip-permissions is silently ignored | Open |
| [#30216](https://github.com/anthropics/claude-code/issues/30216) | AskUserQuestion Tool Regression with --dangerously-skip-permissions | Open |

---

## Workaround: PermissionRequest Hook

A `PermissionRequest` hook auto-approves all permission prompts. Unlike the CLI flag:
- Hooks are inherited by subagents (they read the same `settings.json`)
- Hooks persist across mode changes (plan mode → normal mode)
- Hooks fire on every permission dialog regardless of session state

### Hook Script

Create `~/.claude/hooks/yolo-approve-all.sh`:

```bash
#!/bin/bash
echo '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
exit 0
```

Make executable: `chmod +x ~/.claude/hooks/yolo-approve-all.sh`

### Settings Configuration

Add to `~/.claude/settings.json` under `hooks`:

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

### Selective Approval

For more controlled bypass (only specific tools):

```bash
#!/bin/bash
TOOL=$(cat | jq -r '.tool_name // empty' 2>/dev/null)
case "$TOOL" in
    Edit|Write|Bash)
        echo '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
        ;;
esac
exit 0
```

### Toggling

The `/yolo` skill (in `.claude/skills/yolo/`) wraps this workaround as a toggleable command:
- `/yolo on` — installs the hook with a safety warning
- `/yolo off` — removes the hook
- `/yolo status` — reports current state

---

## Notes

- The `skipDangerousModePermissionPrompt` setting in `settings.json` only suppresses the startup warning dialog — it does NOT bypass permissions. It is a legacy setting.
- v2.1.83+ added "protected directory" prompts for `.git`, `.claude`, `.vscode`, `.idea` that fire even in bypass mode. This is intentional (not a bug).
- `--dangerously-skip-permissions` and `--permission-mode bypassPermissions` are equivalent.
- The hook may require a session restart to take effect, depending on whether Claude Code hot-reloads hooks from settings.json.

---

## Official Documentation

- Permission modes: https://code.claude.com/docs/en/permission-modes
- Hooks: https://code.claude.com/docs/en/hooks
