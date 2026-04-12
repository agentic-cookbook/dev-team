# claude-code — Specialities

- [agent-checklist](agent-checklist.md) — Structure checks (frontmatter present with name+description, kebab-case filename
- [agent-structure-reference](agent-structure-reference.md) — Agents are `.md` files in `.claude/agents/` with YAML frontmatter; body is the s
- [authoring-skills-and-rules](authoring-skills-and-rules.md) — Skill design rules — check inventory first, version from day one, session versio
- [design-for-deletion](design-for-deletion.md) — Build skills and rules that are easy to remove without affecting others; treat l
- [explicit-over-implicit](explicit-over-implicit.md) — Make dependencies visible — skills that need files should read them explicitly, 
- [manage-complexity-through-boundaries](manage-complexity-through-boundaries.md) — Well-defined interfaces between subsystems — skills expose clear input/output co
- [performance](performance.md) — Three principles — (1) shell scripts for deterministic work (scaffolding, git, b
- [rule-checklist](rule-checklist.md) — Content quality (single responsibility, actionable/specific, no conflicting inst
- [rule-structure-reference](rule-structure-reference.md) — Rules are plain `.md` files (no required frontmatter schema), lowercase kebab-ca
- [separation-of-concerns](separation-of-concerns.md) — Each skill, rule, and agent should have one reason to change; if describing what
- [simplicity](simplicity.md) — Simple means no interleaving of concerns — not just "familiar"; optimizing for e
- [skill-checklist](skill-checklist.md) — Structure checks (frontmatter present, name kebab-case ≤64 chars, description pr
- [skill-structure-reference](skill-structure-reference.md) — Directory layout (`.claude/skills/<name>/SKILL.md` + optional references/scripts
- [support-automation](support-automation.md) — Skills and agents should expose capabilities through scriptable interfaces — not
- [yagni](yagni.md) — Build skills and agents for today's known requirements; speculative generality i
