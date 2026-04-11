# Claude Code Hook Patterns

**Date:** 2026-03-29
**Context:** Common hook patterns for automating the development loop in Claude Code.

---

## Hook System Overview

Hooks are user-defined commands that execute automatically at specific points in Claude Code's lifecycle. They provide deterministic control: instead of hoping the LLM remembers to lint after edits or avoid destructive commands, hooks guarantee these behaviors happen every time.

### Event Types

Claude Code supports 25 hook events. The most important for development workflows:

| Event | When It Fires | Can Block? | Common Use |
|-------|---------------|-----------|------------|
| `SessionStart` | Session begins, resumes, or context compacts | No | Environment setup, context injection |
| `PreToolUse` | Before a tool executes | **Yes** | Security gates, command validation |
| `PostToolUse` | After a tool succeeds | No | Auto-format, lint, type-check |
| `PostToolUseFailure` | After a tool fails | No | Error logging |
| `Stop` | When Claude finishes responding | **Yes** | Task completion verification |
| `Notification` | Claude sends a notification | No | Desktop alerts, Slack messages |
| `UserPromptSubmit` | User submits a prompt | **Yes** | Context injection, prompt validation |
| `PermissionRequest` | Permission dialog appears | **Yes** | Auto-approval of safe operations |
| `SubagentStop` | Subagent finishes | **Yes** | Quality validation of subagent output |
| `TaskCompleted` | Task marked complete | **Yes** | Quality gates before completion |
| `ConfigChange` | Settings file changes | **Yes** | Audit logging |
| `CwdChanged` | Working directory changes | No | Direnv-style env reloading |
| `FileChanged` | Watched file changes on disk | No | Hot-reload env vars |
| `PreCompact` | Before context compaction | No | Transcript backup |
| `SessionEnd` | Session terminates | No | Cleanup |

### Configuration Format

Hooks live in `settings.json` at three scopes:

| Location | Scope | Shared? |
|----------|-------|---------|
| `~/.claude/settings.json` | All projects (user-level) | No |
| `.claude/settings.json` | Single project | Yes (commit to repo) |
| `.claude/settings.local.json` | Single project | No (gitignored) |

Basic structure:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "regex_pattern",
        "hooks": [
          {
            "type": "command",
            "command": "your-script-or-command",
            "timeout": 600
          }
        ]
      }
    ]
  }
}
```

### Matcher Patterns

Matchers are regex strings that filter when hooks fire:

- **Tool events** (`PreToolUse`, `PostToolUse`): match on tool name -- `Bash`, `Edit|Write`, `mcp__github__.*`
- **SessionStart**: match on source -- `startup`, `resume`, `compact`
- **Notification**: match on type -- `permission_prompt`, `idle_prompt`
- **FileChanged**: match on filename -- `.envrc`, `.env`
- **ConfigChange**: match on source -- `user_settings`, `project_settings`

Matchers are case-sensitive. An empty string or omitted matcher fires on every occurrence.

### The `if` Field (v2.1.85+)

For finer filtering, the `if` field uses permission rule syntax to match both tool name and arguments:

```json
{
  "type": "command",
  "if": "Bash(git *)",
  "command": ".claude/hooks/check-git-policy.sh"
}
```

This spawns the hook process only when the Bash command starts with `git`. Other Bash commands skip it entirely.

### Exit Codes

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| `0` | Success | Action proceeds; stdout parsed as JSON |
| `2` | Block | Action blocked; stderr fed to Claude as feedback |
| Other | Non-blocking error | Action proceeds; stderr logged in verbose mode |

**Critical:** Exit code 1 is a non-blocking warning. The action still executes. Security hooks must use exit 2.

### Hook Types

1. **`command`** -- shell script (most common). Receives JSON on stdin, returns via exit code + stdout/stderr.
2. **`prompt`** -- single-turn LLM evaluation. Returns `{"ok": true/false, "reason": "..."}`.
3. **`agent`** -- spawns a subagent with tool access (Read, Bash, etc.) for multi-step verification.
4. **`http`** -- POSTs event JSON to a URL. Returns decisions via response body.

### Environment Variables

Available in command hooks:
- `$CLAUDE_PROJECT_DIR` -- project root directory
- `$CLAUDE_ENV_FILE` -- path to persist environment variables (SessionStart, CwdChanged, FileChanged only)
- `$CLAUDE_CODE_REMOTE` -- `"true"` in web mode, unset in CLI

### JSON Input

Every hook receives common fields on stdin:

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  }
}
```

PostToolUse hooks also receive `tool_response` with the tool's output.

---

## Verification Hooks (loop phase: verify)

### Auto-Lint on File Edit

Run your linter automatically after every file Claude edits. Catches issues immediately rather than discovering them at commit time.

**Event:** `PostToolUse`
**Matcher:** `Edit|Write`
**Phase:** verify

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/auto-lint.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/auto-lint.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

case "$FILE_PATH" in
  *.ts|*.tsx|*.js|*.jsx)
    RESULT=$(npx eslint --fix "$FILE_PATH" 2>&1)
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
      echo "{\"systemMessage\": \"Lint errors in $FILE_PATH: $RESULT\"}"
    fi
    ;;
  *.py)
    RESULT=$(ruff check --fix "$FILE_PATH" 2>&1)
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
      echo "{\"systemMessage\": \"Lint errors in $FILE_PATH: $RESULT\"}"
    fi
    ;;
  *.swift)
    RESULT=$(swiftlint lint --path "$FILE_PATH" 2>&1)
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
      echo "{\"systemMessage\": \"Lint warnings in $FILE_PATH: $RESULT\"}"
    fi
    ;;
esac

exit 0
```

### Auto-Format on File Edit

Run Prettier, Black, gofmt, or your formatter of choice after every write. Format is always consistent without Claude needing to remember.

**Event:** `PostToolUse`
**Matcher:** `Edit|Write`
**Phase:** verify

Inline version (simple, single formatter):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write 2>/dev/null"
          }
        ]
      }
    ]
  }
}
```

Multi-language script version (`.claude/hooks/auto-format.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

case "$FILE_PATH" in
  *.ts|*.tsx|*.js|*.jsx|*.json|*.css|*.md)
    npx prettier --write "$FILE_PATH" 2>/dev/null
    ;;
  *.py)
    ruff format "$FILE_PATH" 2>/dev/null
    ;;
  *.go)
    gofmt -w "$FILE_PATH" 2>/dev/null
    ;;
  *.swift)
    swift-format format -i "$FILE_PATH" 2>/dev/null
    ;;
  *.rs)
    rustfmt "$FILE_PATH" 2>/dev/null
    ;;
esac

exit 0
```

### Screenshot Capture on UI File Edit

Capture a screenshot after Claude edits UI files so you can visually verify changes. Requires a running dev server and Playwright (or similar).

**Event:** `PostToolUse`
**Matcher:** `Edit|Write`
**Phase:** verify

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/screenshot-ui.sh",
            "timeout": 30,
            "statusMessage": "Capturing screenshot..."
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/screenshot-ui.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only trigger on UI-related files
echo "$FILE_PATH" | grep -qE '\.(tsx|jsx|vue|svelte|css|scss|html)$' || exit 0

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SCREENSHOT_DIR="$CLAUDE_PROJECT_DIR/.claude/screenshots"
mkdir -p "$SCREENSHOT_DIR"

# Capture via Playwright (assumes dev server on :3000)
npx playwright screenshot \
  --browser chromium \
  "http://localhost:3000" \
  "$SCREENSHOT_DIR/capture-$TIMESTAMP.png" 2>/dev/null

if [ $? -eq 0 ]; then
  echo "{\"systemMessage\": \"Screenshot saved to $SCREENSHOT_DIR/capture-$TIMESTAMP.png\"}"
fi

exit 0
```

**Alternative approach:** Use an agent hook that spawns a subagent with Playwright MCP access to take a screenshot and evaluate it visually.

### Run Tests Before Completion

Prevent Claude from declaring "done" when tests are failing. The Stop hook fires when Claude finishes responding and can force continuation.

**Event:** `Stop`
**Phase:** verify

Using a prompt hook (lightweight, asks LLM to evaluate):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if all tasks are complete. If the user asked for code changes, verify tests were mentioned or run. If not, respond with {\"ok\": false, \"reason\": \"Tests have not been run. Run the test suite before completing.\"}."
          }
        ]
      }
    ]
  }
}
```

Using an agent hook (heavyweight, actually runs tests):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. If tests fail, respond with {\"ok\": false, \"reason\": \"Tests are failing. Fix them before completing.\"}. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

Using a command hook (deterministic, runs specific test command):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/verify-tests.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/verify-tests.sh`):

```bash
#!/bin/bash
INPUT=$(cat)

# CRITICAL: Check if we're already in a forced continuation to prevent infinite loops
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0
fi

# Run tests
TEST_OUTPUT=$(npm test 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  SUMMARY=$(echo "$TEST_OUTPUT" | tail -20)
  echo "{\"decision\": \"block\", \"reason\": \"Tests are failing. Fix before completing:\\n$SUMMARY\"}"
  exit 0
fi

exit 0
```

**Important:** Always check `stop_hook_active` in Stop hooks. When `true`, Claude is already in a forced continuation from a previous block. Skipping this check causes infinite loops.

### Security Scan on Code Changes

Run a security scanner after code edits to catch vulnerabilities early.

**Event:** `PostToolUse`
**Matcher:** `Edit|Write`
**Phase:** verify

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/security-scan.sh",
            "timeout": 60,
            "statusMessage": "Running security scan..."
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/security-scan.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Run Semgrep on the edited file
RESULT=$(semgrep scan --config auto "$FILE_PATH" --json 2>/dev/null)
FINDINGS=$(echo "$RESULT" | jq '.results | length')

if [ "$FINDINGS" -gt 0 ]; then
  SUMMARY=$(echo "$RESULT" | jq -r '.results[] | "- \(.check_id): \(.extra.message) at line \(.start.line)"' | head -10)
  echo "{\"systemMessage\": \"Security findings in $FILE_PATH:\\n$SUMMARY\"}"
fi

exit 0
```

### Accessibility Check on UI Changes

Run an accessibility audit after edits to component files.

**Event:** `PostToolUse`
**Matcher:** `Edit`
**Phase:** verify

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/a11y-check.sh",
            "timeout": 60,
            "statusMessage": "Checking accessibility..."
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/a11y-check.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only check component files
echo "$FILE_PATH" | grep -q 'components/' || exit 0
echo "$FILE_PATH" | grep -qE '\.(tsx|jsx|vue|svelte)$' || exit 0

# Run axe-core against dev server (assumes localhost:3000)
RESULT=$(npx axe-cli http://localhost:3000 --exit 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  SUMMARY=$(echo "$RESULT" | grep -E '(violation|Violation|impact)' | head -10)
  echo "{\"systemMessage\": \"Accessibility issues found after editing $FILE_PATH:\\n$SUMMARY\"}"
fi

exit 0
```

### TypeScript Type-Check on Edit

Run the TypeScript compiler after every `.ts`/`.tsx` edit and report type errors back to Claude.

**Event:** `PostToolUse`
**Matcher:** `Edit|Write`
**Phase:** verify

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/typecheck.sh",
            "timeout": 30,
            "statusMessage": "Type-checking..."
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/typecheck.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$FILE_PATH" != *.ts && "$FILE_PATH" != *.tsx ]]; then
  exit 0
fi

RESULT=$(npx tsc --noEmit 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  # Send first 20 lines of errors to Claude
  SUMMARY=$(echo "$RESULT" | head -20)
  echo "{\"systemMessage\": \"Type errors found after editing $FILE_PATH:\\n$SUMMARY\"}"
fi

exit 0
```

---

## Safety Hooks (loop phase: implement)

### Block Dangerous Commands

The highest-value safety hook. Intercepts Bash commands before execution and blocks destructive patterns.

**Event:** `PreToolUse`
**Matcher:** `Bash`
**Phase:** implement

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/block-dangerous.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/block-dangerous.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command')

# Destructive filesystem operations
if echo "$CMD" | grep -qE 'rm\s+-rf\s+(/|~|\$HOME)'; then
  echo "BLOCKED: Recursive delete at root/home level" >&2
  exit 2
fi

# Force push to main/master
if echo "$CMD" | grep -qE 'git\s+push\s+(-f|--force)\s+(origin\s+)?(main|master)'; then
  echo "BLOCKED: Force push to main/master is not allowed" >&2
  exit 2
fi

# Hard reset
if echo "$CMD" | grep -qE 'git\s+reset\s+--hard'; then
  echo "BLOCKED: git reset --hard can destroy work. Use git stash or create a backup branch first." >&2
  exit 2
fi

# Destructive SQL
if echo "$CMD" | grep -qiE 'DROP\s+(TABLE|DATABASE)'; then
  echo "BLOCKED: Destructive SQL operation" >&2
  exit 2
fi

# Fork bomb
if echo "$CMD" | grep -qE ':\(\)\s*\{.*\}'; then
  echo "BLOCKED: Fork bomb detected" >&2
  exit 2
fi

# Curl piped to shell
if echo "$CMD" | grep -qE 'curl.*\|\s*(bash|sh|zsh)'; then
  echo "BLOCKED: Piping curl output to shell is risky. Download first, review, then execute." >&2
  exit 2
fi

exit 0
```

Python version for more complex pattern matching (`.claude/hooks/security-validator.py`):

```python
#!/usr/bin/env python3
"""Security validator hook for Claude Code."""
import json, sys, re

BLOCKED_PATTERNS = [
    (r'\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\s+[/~]',
     "rm -rf at root/home level is blocked"),
    (r'git\s+push\s+(-f|--force)\s+(origin\s+)?(main|master)',
     "Force push to main/master is blocked"),
    (r'git\s+reset\s+--hard',
     "git reset --hard is blocked. Use git stash instead."),
    (r'DROP\s+(TABLE|DATABASE)',
     "Destructive SQL is blocked"),
    (r'curl.*\|\s*(bash|sh|zsh)',
     "Piping curl to shell is blocked"),
    (r':\(\)\s*\{.*\}',
     "Fork bomb detected"),
    (r'chmod\s+777',
     "chmod 777 is overly permissive"),
]

def main():
    input_data = json.load(sys.stdin)
    if input_data.get("tool_name") != "Bash":
        sys.exit(0)

    command = input_data.get("tool_input", {}).get("command", "")

    for pattern, message in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"SECURITY BLOCK: {message}", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Prevent Force Push

A focused variant that only blocks force push operations. Lighter weight than the full dangerous commands hook.

**Event:** `PreToolUse`
**Matcher:** `Bash`
**Phase:** implement

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git push*)",
            "command": "bash -c 'INPUT=$(cat); CMD=$(echo \"$INPUT\" | jq -r \".tool_input.command\"); if echo \"$CMD\" | grep -qE \"(-f|--force)\"; then echo \"BLOCKED: Force push is not allowed. Use regular push or --force-with-lease.\" >&2; exit 2; fi'"
          }
        ]
      }
    ]
  }
}
```

The `if` field ensures the hook process only spawns for `git push` commands, not every Bash invocation.

### Require Tests Before Commit

Block `git commit` until the linter or test suite passes.

**Event:** `PreToolUse`
**Matcher:** `Bash`
**Phase:** implement

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(git commit*)",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-commit-check.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/pre-commit-check.sh`):

```bash
#!/bin/bash

# Run linter
LINT_OUTPUT=$(npx eslint . --quiet 2>&1)
if [ $? -ne 0 ]; then
  echo "LINT FAILED -- fix before committing:" >&2
  echo "$LINT_OUTPUT" | head -20 >&2
  exit 2
fi

# Run tests
TEST_OUTPUT=$(npm test 2>&1)
if [ $? -ne 0 ]; then
  echo "TESTS FAILED -- fix before committing:" >&2
  echo "$TEST_OUTPUT" | tail -20 >&2
  exit 2
fi

exit 0
```

### Protect Sensitive Files

Block edits to `.env`, lock files, `.git/`, and other files that should not be modified by the agent.

**Event:** `PreToolUse`
**Matcher:** `Edit|Write`
**Phase:** implement

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/protect-files.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_PATTERNS=(
  ".env"
  ".env.local"
  ".env.production"
  "package-lock.json"
  "pnpm-lock.yaml"
  "yarn.lock"
  ".git/"
  "node_modules/"
  "credentials"
  "secrets"
)

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0
```

### Validate Environment Variables

Check that required environment variables are set before allowing deployment-related commands.

**Event:** `PreToolUse`
**Matcher:** `Bash`
**Phase:** implement

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(npm run deploy*)",
            "command": "bash -c 'for var in AWS_REGION NODE_ENV API_KEY; do if [ -z \"${!var}\" ]; then echo \"BLOCKED: Required env var $var is not set\" >&2; exit 2; fi; done'"
          }
        ]
      }
    ]
  }
}
```

### Enforce Package Manager

Block the wrong package manager in monorepos (e.g., block `npm` when the project uses `pnpm`).

**Event:** `PreToolUse`
**Matcher:** `Bash`
**Phase:** implement

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/enforce-pkg-manager.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/enforce-pkg-manager.sh`):

```bash
#!/bin/bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command')

# Detect project package manager
if [ -f "$CLAUDE_PROJECT_DIR/pnpm-lock.yaml" ]; then
  if echo "$CMD" | grep -qE '^npm\s+(install|add|remove|run|ci)'; then
    echo "BLOCKED: This project uses pnpm. Use pnpm instead of npm." >&2
    exit 2
  fi
elif [ -f "$CLAUDE_PROJECT_DIR/yarn.lock" ]; then
  if echo "$CMD" | grep -qE '^npm\s+(install|add|remove|run|ci)'; then
    echo "BLOCKED: This project uses yarn. Use yarn instead of npm." >&2
    exit 2
  fi
fi

exit 0
```

### Block PR Creation if Tests Fail

Prevent creating pull requests when the test suite is not passing.

**Event:** `PreToolUse`
**Matcher:** `mcp__github__create_pull_request` (or `Bash` with `if` filter)
**Phase:** implement

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(gh pr create*)",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-pr-tests.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/pre-pr-tests.sh`):

```bash
#!/bin/bash
TEST_OUTPUT=$(npm test 2>&1)
if [ $? -ne 0 ]; then
  echo "BLOCKED: Tests must pass before creating a PR." >&2
  echo "$TEST_OUTPUT" | tail -15 >&2
  exit 2
fi

exit 0
```

---

## Workflow Hooks (loop phase: all)

### Session Start Setup

Configure environment variables, inject context, or show project status when a session begins.

**Event:** `SessionStart`
**Phase:** all

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-setup.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`.claude/hooks/session-setup.sh`):

```bash
#!/bin/bash

# Set environment variables for the session
if [[ -n "$CLAUDE_ENV_FILE" ]]; then
  echo 'export NODE_ENV=development' >> "$CLAUDE_ENV_FILE"
  echo 'export PATH="$PATH:./node_modules/.bin"' >> "$CLAUDE_ENV_FILE"
fi

# Output context that Claude will see
echo "Project status:"
git status --short 2>/dev/null
echo "---"
git log --oneline -5 2>/dev/null

exit 0
```

### Re-inject Context After Compaction

When context compaction summarizes the conversation, important details can be lost. Re-inject critical reminders.

**Event:** `SessionStart`
**Matcher:** `compact`
**Phase:** all

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use pnpm, not npm. Run pnpm test before committing. Current sprint: auth refactor. Do not modify files in packages/legacy/.'"
          }
        ]
      }
    ]
  }
}
```

Any text written to stdout is added to Claude's context. Replace the `echo` with a script that produces dynamic output for more complex needs.

### Notification on Long Tasks

Get a desktop notification when Claude needs your attention, so you can switch to other work.

**Event:** `Notification`
**Phase:** all

macOS:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

Linux:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Claude Code needs your attention'"
          }
        ]
      }
    ]
  }
}
```

Slack webhook:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt|idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "curl -s -X POST \"$SLACK_WEBHOOK_URL\" -H 'Content-type: application/json' -d '{\"text\": \"Claude Code needs your attention\"}'"
          }
        ]
      }
    ]
  }
}
```

### Auto-Stage Changes

Automatically `git add` files after Claude modifies them. Keeps the staging area current without manual intervention.

**Event:** `PostToolUse`
**Matcher:** `Edit|Write`
**Phase:** all

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs git add 2>/dev/null"
          }
        ]
      }
    ]
  }
}
```

### Session File Tracking

Track every file modified by Edit or Write during a session. Creates a per-session changes file that can be cross-referenced with `git status` to find uncommitted files changed by the current session — something git alone can't tell you (git doesn't know which process made an uncommitted change).

**Event:** `PostToolUse`
**Matcher:** `Edit|Write`
**Phase:** all

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/session-file-tracker.sh"
          }
        ]
      }
    ]
  }
}
```

Script (`~/.claude/hooks/session-file-tracker.sh`):

```bash
#!/bin/bash
# Track files modified by Edit/Write tools per session
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
[ -z "$SESSION_ID" ] || [ -z "$FILE_PATH" ] && exit 0
CHANGES_DIR="$HOME/.claude-sessions"
CHANGES_FILE="${CHANGES_DIR}/${SESSION_ID}.changes"
mkdir -p "$CHANGES_DIR"
# Deduplicate
grep -qxF "$FILE_PATH" "$CHANGES_FILE" 2>/dev/null || echo "$FILE_PATH" >> "$CHANGES_FILE"
exit 0
```

**Querying:** Find files this session touched that are still uncommitted:

```bash
comm -12 \
  <(sort ~/.claude-sessions/$SESSION_ID.changes) \
  <(git status --porcelain | awk '{print $2}' | sort)
```

**Cleanup:** Add a SessionEnd hook to delete stale changes files:

```bash
# In yolo-session-cleanup.sh or a dedicated cleanup hook
rm -f "$HOME/.claude-sessions/${SESSION_ID}.changes"
find "$HOME/.claude-sessions" -name "*.changes" -mtime +1 -delete 2>/dev/null
```

**Scope:** Install at `~/.claude/settings.json` (user-level) so it tracks across all projects. The changes file uses `session_id` as the filename, so concurrent sessions don't conflict.

### Log All Bash Commands

Append every command Claude runs to a log file for compliance or debugging.

**Event:** `PostToolUse`
**Matcher:** `Bash`
**Phase:** all

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' | while read cmd; do echo \"$(date -u +%Y-%m-%dT%H:%M:%SZ) $cmd\" >> $CLAUDE_PROJECT_DIR/.claude/bash-commands.log; done"
          }
        ]
      }
    ]
  }
}
```

### Audit Configuration Changes

Track when settings or skills files change during a session.

**Event:** `ConfigChange`
**Phase:** all

```json
{
  "hooks": {
    "ConfigChange": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "jq -c '{timestamp: now | todate, source: .source, file: .file_path}' >> ~/claude-config-audit.log"
          }
        ]
      }
    ]
  }
}
```

### Reload Environment on Directory Change

Integrate with direnv or similar tools to update environment variables when Claude changes directories.

**Event:** `CwdChanged`
**Phase:** all

```json
{
  "hooks": {
    "CwdChanged": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "direnv export bash >> \"$CLAUDE_ENV_FILE\""
          }
        ]
      }
    ]
  }
}
```

### Auto-Approve Safe Operations

Skip the permission dialog for operations you always allow, like exiting plan mode.

**Event:** `PermissionRequest`
**Matcher:** `ExitPlanMode`
**Phase:** all

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"PermissionRequest\", \"decision\": {\"behavior\": \"allow\"}}}'"
          }
        ]
      }
    ]
  }
}
```

**Warning:** Keep the matcher as narrow as possible. Matching `.*` or leaving it empty auto-approves every permission prompt, including file writes and shell commands.

### Backup Transcript Before Compaction

Save the full transcript before context compaction discards details.

**Event:** `PreCompact`
**Phase:** all

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); TRANSCRIPT=$(echo \"$INPUT\" | jq -r \".transcript_path\"); cp \"$TRANSCRIPT\" \"$CLAUDE_PROJECT_DIR/.claude/backups/$(date +%Y%m%d-%H%M%S)-transcript.jsonl\" 2>/dev/null'"
          }
        ]
      }
    ]
  }
}
```

---

## The Hookify Plugin

Hookify is an official Claude Code plugin that creates hooks from natural language descriptions or by analyzing conversation patterns. It eliminates the need to hand-write `settings.json` entries and shell scripts.

### Installation

Hookify is available through the Claude Code plugin marketplace. It auto-discovers when the marketplace is installed.

### Usage

**Create from explicit instruction:**

```
/hookify Don't use console.log in TypeScript files
```

**Analyze conversation for patterns:**

```
/hookify
```

(Without arguments, hookify scans recent conversation for behaviors you corrected or were frustrated by and generates rules automatically.)

### Commands

| Command | Purpose |
|---------|---------|
| `/hookify <description>` | Create a rule from a description |
| `/hookify` | Analyze conversation, suggest rules |
| `/hookify:list` | List all configured rules |
| `/hookify:configure` | Enable/disable rules interactively |
| `/hookify:help` | Get help |

### Rule File Format

Hookify stores rules as markdown files with YAML frontmatter:

**Location:** `.claude/hookify.<name>.local.md`

```markdown
---
name: block-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
action: block
---

**Dangerous rm command detected!**

This command could delete important files. Please:
- Verify the path is correct
- Consider using a safer approach
- Make sure you have backups
```

### Frontmatter Fields

| Field | Values | Description |
|-------|--------|-------------|
| `name` | string | Unique rule identifier |
| `enabled` | `true`/`false` | Whether rule is active |
| `event` | `bash`, `file`, `stop`, `prompt`, `all` | Event type to trigger on |
| `pattern` | regex | Pattern to match (single) |
| `action` | `warn`, `block` | `warn` = allow with message, `block` = prevent |
| `conditions` | array | Multiple conditions (all must match) |

### Conditions (Advanced Rules)

For multi-field matching, use the `conditions` array instead of a single `pattern`:

```markdown
---
name: warn-sensitive-files
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$|credentials|secrets
  - field: new_text
    operator: contains
    pattern: KEY
---

**Sensitive file edit detected!**

Ensure credentials are not hardcoded and file is in .gitignore.
```

**Operators:** `regex_match`, `contains`, `equals`, `not_contains`, `starts_with`, `ends_with`

**Fields by event type:**
- **bash:** `command`
- **file:** `file_path`, `new_text`, `old_text`, `content`
- **prompt:** `user_prompt`
- **stop:** general session state matching

### Hookify vs. Manual Hooks

| Aspect | Hookify | Manual Hooks |
|--------|---------|--------------|
| Setup | Natural language | JSON + shell scripts |
| Flexibility | Pattern matching on fields | Full shell/Python scripting |
| Maintenance | Edit markdown files | Edit scripts + settings.json |
| Sharing | Local `.local.md` files | Commit settings.json to repo |
| Complexity | Simple rules | Arbitrary logic |

Use hookify for quick, simple rules. Use manual hooks for complex validation logic, multi-step scripts, or hooks that need to be shared with a team via version control.

---

## Configuration Reference

### Complete Settings.json Example

A realistic project configuration combining multiple patterns:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-setup.sh"
          }
        ]
      },
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: use pnpm. Run tests before committing.'"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/block-dangerous.sh"
          },
          {
            "type": "command",
            "if": "Bash(git commit*)",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/pre-commit-check.sh"
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/protect-files.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/auto-format.sh"
          },
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/auto-lint.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/verify-tests.sh"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

### Matcher Syntax Summary

| Pattern | Meaning |
|---------|---------|
| `"Bash"` | Exact tool name |
| `"Edit\|Write"` | Either tool (pipe = regex OR) |
| `"mcp__github__.*"` | All tools from a specific MCP server |
| `""` or omitted | Match everything |
| `"compact"` | Match specific session start reason |
| `".envrc\|.env"` | Match specific filenames (FileChanged) |

### Hook Fields Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `command\|prompt\|agent\|http` | required | Hook execution type |
| `command` | string | -- | Shell command to run (command type) |
| `prompt` | string | -- | Prompt text (prompt/agent type) |
| `url` | string | -- | Endpoint URL (http type) |
| `if` | string | -- | Permission rule filter (tool events only) |
| `timeout` | number | 600 (cmd), 30 (prompt), 60 (agent) | Seconds before timeout |
| `statusMessage` | string | -- | Custom spinner message while running |
| `async` | boolean | `false` | Run without blocking Claude |
| `once` | boolean | `false` | Run once per session then remove (skills only) |
| `shell` | string | default shell | Shell to use for command hooks |

### PreToolUse JSON Output

The structured output format for PreToolUse hooks that need finer control than exit codes:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "explanation shown to Claude",
    "updatedInput": {"command": "modified command"},
    "additionalContext": "extra context for Claude"
  }
}
```

- `allow` -- skip permission prompt (deny rules still apply)
- `deny` -- cancel the tool call
- `ask` -- show the permission prompt as normal

### PostToolUse JSON Output

```json
{
  "decision": "block",
  "reason": "explanation",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "context added to Claude's view"
  }
}
```

### Stop Hook JSON Output

```json
{
  "decision": "block",
  "reason": "Why Claude should continue working"
}
```

### Script Permissions

Scripts must be executable:

```bash
chmod +x .claude/hooks/*.sh
```

### Debugging

- Toggle verbose mode with `Ctrl+O` to see hook output in the transcript
- Run `claude --debug` for full execution details
- Test scripts manually: `echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | .claude/hooks/your-script.sh; echo $?`
- Use `/hooks` in Claude Code to browse all configured hooks

### Performance Notes

- Keep hooks under 500ms execution time; under 200ms when running on every tool use
- Multiple matching hooks run in parallel
- Identical hook commands are automatically deduplicated
- Use the `if` field to avoid spawning hook processes unnecessarily
- Use `async: true` for hooks that don't need to block (e.g., background test runs)

### Common Pitfalls

1. **Exit 1 vs Exit 2:** Exit 1 is a non-blocking warning. Only exit 2 actually blocks. Security hooks that use exit 1 provide no enforcement.
2. **Stop hook infinite loops:** Always check `stop_hook_active` in Stop hooks. When `true`, allow Claude to stop.
3. **Shell profile noise:** If your `~/.zshrc` or `~/.bashrc` has unconditional `echo` statements, they corrupt hook JSON output. Wrap them in `if [[ $- == *i* ]]; then ... fi`.
4. **Missing jq:** Many hook scripts depend on `jq` for JSON parsing. Install it: `brew install jq` (macOS), `apt-get install jq` (Linux).
5. **Case sensitivity:** Matchers are case-sensitive. `"bash"` does not match the `Bash` tool.
6. **PermissionRequest in headless mode:** `PermissionRequest` hooks do not fire in non-interactive mode (`-p`). Use `PreToolUse` for automated permission decisions.

---

## Sources

- [Hooks Reference -- Claude Code Docs](https://code.claude.com/docs/en/hooks)
- [Automate Workflows with Hooks -- Claude Code Docs](https://code.claude.com/docs/en/hooks-guide)
- [Claude Code Hooks: Configuration Guide -- Anthropic Blog](https://claude.com/blog/how-to-configure-hooks)
- [Hookify Plugin -- GitHub (anthropics/claude-code)](https://github.com/anthropics/claude-code/tree/main/plugins/hookify)
- [Claude Code Hooks Tutorial: 5 Production Hooks -- Blake Crosley](https://blakecrosley.com/blog/claude-code-hooks-tutorial)
- [Claude Code Hook Examples -- Steve Kinney](https://stevekinney.com/courses/ai-development/claude-code-hook-examples)
- [Automating Your Workflow with Claude Code Hooks -- Gunnar Grosch (DEV Community)](https://dev.to/gunnargrosch/automating-your-workflow-with-claude-code-hooks-389h)
- [Claude Code Hooks Collection -- karanb192 (GitHub)](https://github.com/karanb192/claude-code-hooks)
- [Claude Code Security Hook -- sgasser (GitHub Gist)](https://gist.github.com/sgasser/efeb186bad7e68c146d6692ec05c1a57)
- [Claude Code Security Guardrails -- mafiaguy (GitHub)](https://github.com/mafiaguy/claude-security-guardrails)
- [Awesome Claude Code -- hesreallyhim (GitHub)](https://github.com/hesreallyhim/awesome-claude-code)
- [Giving Claude Code Eyes: Round-Trip Screenshot Testing -- Tal Rotbart (Medium)](https://medium.com/@rotbart/giving-claude-code-eyes-round-trip-screenshot-testing-ce52f7dcc563)
