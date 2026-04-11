# Memory and Context Tools for Claude Code

**Date:** 2026-03-29
**Context:** Tools and strategies for persisting memory, managing context, and maintaining continuity across Claude Code sessions.

---

## Built-in Claude Code Memory

Claude Code has a native auto-memory system that persists knowledge across conversations without any plugins or configuration.

### How It Works

When Claude learns something important during a session (project conventions, user preferences, discovered facts), it can save that knowledge to a structured memory store. These memories are automatically loaded at the start of every conversation, giving Claude persistent awareness of what it has learned.

### Memory File Structure

Memory is stored as markdown files in a dedicated directory:

| Location | Scope | Purpose |
|----------|-------|---------|
| `~/.claude/projects/<project-path>/memory/MEMORY.md` | Per-project | Project-specific context loaded for that project |
| `~/.claude/memory/MEMORY.md` | Global (user-level) | Context loaded for all projects |

`MEMORY.md` serves as an index file with links to individual memory files in the same directory. Each individual file covers a single topic (e.g., `project_purpose.md`, `user_profile.md`, `test_infrastructure.md`).

### Memory Types

| Type | What It Captures | Example |
|------|-----------------|---------|
| **Project** | Architecture, structure, conventions | "Site uses Vite + React + Tailwind on Cloudflare Workers" |
| **User** | Personal preferences, workflow habits | "Multi-platform developer, prefers direct commits on dotfiles" |
| **Feedback** | Corrections and behavioral adjustments | "Don't ask too early — let user frame the problem first" |
| **Reference** | Facts discovered during work | "Skills use version field in frontmatter" |

### Saving Memories

- **Automatic**: Claude decides to save when it encounters information likely to be useful in future sessions.
- **Manual**: Tell Claude "remember this" or "save this to memory" to explicitly persist something.
- **Editing**: You can directly edit the markdown files in the memory directory.

### When to Use

- Always available — no setup required.
- Best for: project conventions, user preferences, behavioral corrections, discovered facts.
- Limitation: memory files are loaded into context at session start, so very large memory stores consume context window space.

---

## Plugins

### `remember` Plugin

**Source:** `remember@claude-plugins-official`

A plugin that provides continuous, compressed memory across sessions. It goes beyond the built-in memory system by actively processing full conversation transcripts into structured summaries.

#### What It Does

- Extracts key decisions, code changes, and context from each conversation.
- Summarizes and compresses conversations into tiered daily logs (detailed recent, compressed older).
- Injects relevant context into future sessions based on what you are working on.
- Maintains a rolling window of compressed history rather than individual memory files.

#### How It Differs from Built-in Memory

| Aspect | Built-in Memory | `remember` Plugin |
|--------|----------------|-------------------|
| Granularity | Individual facts and preferences | Full conversation summaries |
| Storage | Individual markdown files | Tiered daily logs (detailed to compressed) |
| Trigger | Explicit save or auto-detection | Continuous — processes every conversation |
| What's captured | Specific facts Claude decides to save | Everything: decisions, code changes, discussions |
| Context injection | All memories loaded at start | Selectively injects relevant history |

#### Install

```bash
claude plugin add remember@claude-plugins-official
```

#### When to Use

- Long-running projects where conversation history matters.
- Teams where decisions made in past sessions need to be reliably recalled.
- When built-in memory misses important context because it was not explicitly saved.

---

### `claude-mem` Community Plugin

**Source:** `thedotmack/claude-mem`

A community plugin that captures everything Claude does during sessions and compresses it for future use.

#### What It Does

- Records all actions, tool calls, and outputs during a session.
- Compresses session data using AI summarization.
- Injects relevant compressed context into future sessions automatically.
- Provides a more exhaustive capture than built-in memory (which is selective).

#### Install

```bash
claude plugin add thedotmack/claude-mem
```

#### When to Use

- When you need total recall of what happened in prior sessions.
- Debugging workflows where you need to trace what Claude did and why.
- Projects where the built-in memory's selective approach misses operational details.

---

### `goodmem` Plugin

**Source:** `goodmem@claude-plugins-official`

Memory infrastructure designed for agents, providing structured memory storage and retrieval.

#### What It Does

- Provides a memory infrastructure layer purpose-built for agentic workflows.
- Stores and retrieves structured memories with metadata (timestamps, tags, relevance scores).
- Designed for multi-agent scenarios where different agents need access to shared memory.
- Supports semantic search over stored memories.

#### Install

```bash
claude plugin add goodmem@claude-plugins-official
```

#### When to Use

- Multi-agent workflows where agents need shared, structured memory.
- When you need more sophisticated memory retrieval than keyword matching (semantic search).
- Projects that require memory with metadata (timestamps, categories, relevance).

---

## Context Management Strategies

These are built-in mechanisms and patterns for managing what Claude knows during and across sessions.

### Compaction (API-Level, Beta)

When a conversation approaches the context window limit, Claude Code can trigger server-side compaction.

#### What It Does

- Summarizes the conversation so far into a compressed representation.
- Preserves key facts, decisions, and state while discarding verbose intermediate output.
- Fires the `PreCompact` hook event before compaction (useful for backing up the transcript).
- Fires `SessionStart` after compaction (hooks can re-inject critical context).

#### How to Use

Compaction is automatic when context usage gets high. You can influence it:

- **`PreCompact` hook**: Back up the full transcript before it gets summarized.
- **`SessionStart` hook**: Re-inject critical context after compaction.
- **CLAUDE.md files**: Content in CLAUDE.md is always reloaded after compaction, so put must-not-forget rules there.

#### When to Use

- Long sessions with extensive tool output.
- Sessions that generate large amounts of code or search results.
- The `PreCompact` hook is particularly useful for archiving full transcripts.

---

### CLAUDE.md Files

Project and user instructions that are loaded at the start of every session and reloaded after compaction.

#### File Locations

| Location | Scope | Loaded When |
|----------|-------|-------------|
| `~/.claude/CLAUDE.md` | Global (user-level) | Every session, every project |
| `<project>/.claude/CLAUDE.md` | Project-level | Sessions in that project |
| `<project>/CLAUDE.md` | Project root | Sessions in that project |
| `<project>/.claude/rules/*.md` | Project rules | Sessions in that project |

#### What It Does

- Defines coding standards, project conventions, and behavioral rules.
- Survives compaction — always present in context.
- Can reference other files, define workflows, and set constraints.

#### When to Use

- Anything that must be true for every session: coding style, commit conventions, architectural rules.
- Project-specific instructions that every contributor (human or AI) should follow.
- Critical rules that must survive context compaction.

---

### Session Resumption

Continue a previous session instead of starting fresh.

#### How to Use

```bash
# Resume most recent session
claude --resume

# Resume a specific session by ID
claude --resume <session-id>

# Continue most recent conversation (alias)
claude --continue
```

#### What It Does

- Reloads the prior session's context (messages, tool results, decisions).
- No re-explanation needed — Claude remembers what was discussed.
- Subject to context window limits; very long prior sessions may be compacted on resume.

#### When to Use

- Returning to a task after a break.
- Multi-step work that spans hours or days.
- When re-explaining context would waste significant time.

---

### Task Files

A pattern (not a built-in feature) for tracking multi-session work using plain files.

#### How It Works

Create a markdown file (e.g., `TASKS.md`, `.claude/tasks/current.md`) that tracks:

- Current objectives and status.
- Decisions made in prior sessions.
- Blockers and open questions.
- What was completed and what remains.

Reference it in your CLAUDE.md so Claude loads it every session, or ask Claude to read it at the start of a session.

#### When to Use

- Multi-day feature work spanning many sessions.
- Complex tasks with many sub-steps.
- When you need a human-readable record of progress that is not buried in conversation history.

---

## MCP Memory Servers

### Memory Server (Knowledge Graph)

**Source:** `@modelcontextprotocol/server-memory`
**Repository:** [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)

A knowledge graph-based persistent memory system that stores entities, relationships, and observations.

#### What It Does

- Stores structured knowledge as entities with observations (facts about them).
- Maintains relationships between entities (e.g., "ProjectX uses React", "UserA prefers dark mode").
- Persists to a local JSONL file.
- Tools: `create_entities`, `create_relations`, `add_observations`, `delete_entities`, `delete_observations`, `delete_relations`, `search_nodes`, `open_nodes`, `read_graph`.

#### Install

```bash
claude mcp add memory -s user -- npx -y @modelcontextprotocol/server-memory
```

Or in `.mcp.json`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "/path/to/memory.jsonl"
      }
    }
  }
}
```

#### When to Use

- When you need structured, queryable memory (not just flat text).
- Tracking relationships between concepts, people, projects, and decisions.
- Building a knowledge base that grows over time.

---

### Sequential Thinking Server

**Source:** `@modelcontextprotocol/server-sequential-thinking`
**Repository:** [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)

A reflective problem-solving tool that helps Claude think through complex problems step by step.

#### What It Does

- Provides a structured tool for breaking down complex problems into sequential thought steps.
- Supports revision — Claude can go back and revise earlier thoughts as understanding deepens.
- Supports branching — exploring alternative solution paths.
- Not strictly "memory" but enhances context utilization during complex reasoning.
- Tool: `sequentialthinking` with parameters for thought content, step number, total steps, and revision/branching flags.

#### Install

```bash
claude mcp add sequential-thinking -s user -- npx -y @modelcontextprotocol/server-sequential-thinking
```

Or in `.mcp.json`:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

#### When to Use

- Complex architectural decisions requiring multi-step reasoning.
- Debugging scenarios where the root cause is not obvious.
- Planning tasks where exploring and comparing alternatives matters.
- Any problem where "think step by step" benefits from structured revision.

---

## Comparison Matrix

| Tool | Type | Persistence | Granularity | Setup |
|------|------|-------------|-------------|-------|
| **Built-in Memory** | Native | Markdown files | Individual facts | None |
| **`remember` Plugin** | Plugin | Tiered daily logs | Full conversations | `claude plugin add` |
| **`claude-mem` Plugin** | Plugin | Compressed sessions | All actions and outputs | `claude plugin add` |
| **`goodmem` Plugin** | Plugin | Structured store | Agent-oriented memories | `claude plugin add` |
| **CLAUDE.md** | File convention | Markdown files | Rules and instructions | Create file |
| **Session Resumption** | Native | Session state | Full conversation | `--resume` flag |
| **Task Files** | File pattern | Markdown files | Work tracking | Create file |
| **Memory MCP Server** | MCP Server | JSONL knowledge graph | Entities and relations | `claude mcp add` |
| **Sequential Thinking** | MCP Server | Per-session | Thought chains | `claude mcp add` |

---

## Recommended Combinations

### Solo Developer

- **Built-in Memory** for project conventions and preferences.
- **CLAUDE.md** for must-not-forget rules.
- **Session Resumption** for multi-step tasks.
- **Task Files** for tracking progress on long-running work.

### Team Project

- **CLAUDE.md** (committed to repo) for shared conventions.
- **Built-in Memory** (per-developer) for individual preferences.
- **Memory MCP Server** for shared knowledge graph across the team.

### Complex Architecture Work

- **Sequential Thinking MCP** for structured reasoning during planning.
- **Memory MCP Server** for capturing architectural decisions as entities.
- **Task Files** for tracking what has been decided and what remains.

### High-Context Long Sessions

- **Compaction** (automatic) with `PreCompact` hooks to archive transcripts.
- **`remember` Plugin** to ensure nothing is lost across sessions.
- **CLAUDE.md** for rules that must survive compaction.

---

## Sources

- [Claude Code Memory Documentation](https://docs.anthropic.com/en/docs/claude-code/memory)
- [Claude Code MCP Documentation](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [modelcontextprotocol/servers — Memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
- [modelcontextprotocol/servers — Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking)
- [Claude Code Plugin Registry](https://registry.modelcontextprotocol.io)
