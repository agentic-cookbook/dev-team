# Claude Integration & Customization Guide

## Ways to Integrate with Claude

### Direct API Access

The Claude API (Messages API at `api.anthropic.com`) is the core integration point. It supports text, vision, tool use, streaming, and batching.

- **Messages API** — Primary conversational endpoint for all Claude interactions
- **Message Batches API** — Async bulk processing at 50% cost reduction
- **Token Counting API** — Cost and rate limit management
- **Models API** — List and query available Claude models
- **Files API** — Upload and manage files for use in conversations

### Official SDKs

Anthropic ships SDKs in **Python, TypeScript, Java, Go, Ruby, C#, and PHP** — all with streaming, retries, and type safety built in.

### Claude Agent SDK

A higher-level SDK for building autonomous agents with built-in tools (bash, file editing, web search, etc.) and multi-agent orchestration. This is the foundation for building custom agentic products.

### Client Applications

- **Claude.ai** — Web and mobile chat interface
- **Claude Desktop App** — Native macOS and Windows application
- **Claude Code** — CLI tool for agentic coding workflows
- **Cowork Mode** — Desktop app's automation layer for file and task management
- **Claude in Chrome** — Browser automation agent (beta)
- **Claude in Excel** — Spreadsheet agent (beta)

### Model Context Protocol (MCP)

An open standard for connecting Claude to external tools and data sources. Supported across Claude Desktop, Claude.ai, Claude Code, and the API. The ecosystem has 1,000+ community servers, with Anthropic shipping reference servers for filesystem, PostgreSQL, Brave Search, GitHub, Puppeteer, and Google Maps.

---

## Ways to Augment & Guide Claude

### System Prompts

The foundational way to shape Claude's behavior, persona, and constraints for any API integration. Define tone, role, rules, and output format.

### Tool Use (Function Calling)

Define custom tools/functions that Claude can invoke, letting it take actions in your systems. This is the backbone of agentic workflows.

### MCP Servers

Extend Claude's reach to external services (databases, APIs, SaaS tools) via the standardized Model Context Protocol. You can build custom MCP servers for your own services and distribute them.

### Skills

Markdown files (`SKILL.md`) that teach Claude repeatable workflows, invoked as slash commands. Think of them as reusable prompt templates with structured instructions. They can be bundled and shared.

### Hooks

Scripts that fire deterministically at lifecycle events (before/after tool calls, session start/end). These aren't AI-driven — they're for guaranteed actions like linting, logging, or validation.

### Plugins

The packaging format that bundles skills, MCP server configs, hooks, subagents, and slash commands into a single installable unit. Plugins can be distributed through marketplaces.

### Subagents / Agent Teams

Within Claude Code and the Agent SDK, you can spawn child agents with specific roles and tool access, enabling multi-agent architectures for complex workflows.

### CLAUDE.md / Project Context Files

Markdown files at the project or user level that give Claude persistent context about your codebase, conventions, and preferences. These are read automatically at session start.

### Custom Slash Commands

User-defined commands that trigger specific skills or workflows within Claude Code and Cowork.

### Prompt Caching

A cost and latency optimization that caches frequently reused prompt prefixes (system prompts, large documents) across API calls.

### Computer Use (Beta)

Claude can see and interact with desktop UIs via screenshots and mouse/keyboard control, enabling GUI automation workflows.

---

## Sources

- [Claude API Docs](https://platform.claude.com/docs/en/home)
- [Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Client SDKs](https://platform.claude.com/docs/en/api/client-sdks)
- [Create Plugins — Claude Code Docs](https://code.claude.com/docs/en/plugins)
- [MCP Setup Guide](https://generect.com/blog/claude-mcp/)
