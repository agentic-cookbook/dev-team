---
globs: agents/*.md,skills/*/SKILL.md
---

# Bump Versions on Change

When you modify an agent or skill file, bump its version:

- **Skills**: Increment the `version:` field in SKILL.md frontmatter (patch for fixes, minor for new behavior, major for breaking changes). Update the version string in the Startup section to match.
- **Agents**: If the agent has a version comment or field, increment it. If it doesn't, no action needed.

One version bump per logical change. Don't bump if the file wasn't meaningfully changed (e.g., whitespace-only edits).
