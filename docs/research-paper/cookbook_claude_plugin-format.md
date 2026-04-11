# Claude Code Plugin Format

**Date**: 2026-03-30

## What Is a Plugin?

A distributable package that extends Claude Code with skills, agents, commands, hooks, and MCP servers. Installed via `claude plugin install name@marketplace`. Skills get namespaced: `/plugin-name:skill-name`.

## Plugin Structure

```
my-plugin/
  .claude-plugin/
    plugin.json               # REQUIRED: metadata manifest
  skills/                     # auto-discovered
    my-skill/SKILL.md
  agents/                     # optional
  hooks/hooks.json            # optional
  .mcp.json                   # optional
  settings.json               # optional defaults
```

Only `plugin.json` goes in `.claude-plugin/`. Everything else at root.

## Plugin vs Project-Local Skills

| Aspect | Project-local (.claude/skills/) | Plugin |
|--------|--------------------------------|--------|
| Scope | Single project | Any project |
| Naming | `/skill-name` | `/plugin-name:skill-name` |
| Distribution | Manual copy / git clone | `claude plugin install` |
| Updates | Manual | Automatic via marketplace |
| Can include rules? | Yes (.claude/rules/) | **No** |

## What Plugins Cannot Do

- **Cannot distribute rules** — rules are project/user-specific by design
- Cannot include `.claude/` directory, CLAUDE.md, or settings overrides
- Cannot modify the consuming project's configuration

## Distribution

- Official marketplace: `anthropics/claude-plugins-official`
- Custom marketplaces: any GitHub repo with `marketplace.json`
- Direct: `claude --plugin-dir ./path` for local development
- npm: `npm install @scope/plugin-name`

## Should the Agentic Cookbook Be a Plugin?

**Partial fit.** The 20+ skills could be a plugin, but:
- Cookbook content (principles, guidelines, recipes) can't travel with a plugin
- Skills that READ cookbook content (like `/cookbook-start`) would fail without a local checkout
- Rules can't be in a plugin — `/install-cookbook` must still copy rule templates

**Conclusion**: Not converting now. The cookbook is a body of content + tools, not just tools. The current distribution model (clone + `/install-cookbook`) is the right fit for what it is.

## Sources

- https://code.claude.com/docs/en/plugins-reference
- https://code.claude.com/docs/en/plugins
- https://code.claude.com/docs/en/discover-plugins
- https://github.com/anthropics/claude-plugins-official
