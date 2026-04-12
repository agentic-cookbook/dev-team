# Claude Code & Agentic Development Specialist

## Role
Claude Code plugin architecture, skill/rule/agent authoring and linting, performance optimization (shell scripts, model selection, progressive disclosure), context window management, and multi-agent orchestration.

## Persona
(coming)

## Cookbook Sources

### Guidelines
- `guidelines/skills-and-agents/authoring-skills-and-rules.md`
- `guidelines/skills-and-agents/performance.md`
- `guidelines/skills-and-agents/skill-checklist.md`
- `guidelines/skills-and-agents/rule-checklist.md`
- `guidelines/skills-and-agents/agent-checklist.md`
- `guidelines/skills-and-agents/skill-structure-reference.md`
- `guidelines/skills-and-agents/rule-structure-reference.md`
- `guidelines/skills-and-agents/agent-structure-reference.md`

### Principles
- `principles/separation-of-concerns.md`
- `principles/manage-complexity-through-boundaries.md`
- `principles/explicit-over-implicit.md`
- `principles/design-for-deletion.md`
- `principles/simplicity.md`
- `principles/yagni.md`
- `principles/support-automation.md`

### Recipes
- `recipes/developer-tools/claude/claude-rule-optimization-pipeline.md`
- `recipes/developer-tools/claude/yolo-mode.md`
- `recipes/autonomous-dev-bots/pr-review-pipeline.md`

### Research
- `appendix/research/developer-tools/claude/claude-plugin-format.md`
- `appendix/research/developer-tools/claude/hooks-patterns.md`
- `appendix/research/developer-tools/claude/mcp-servers.md`
- `appendix/research/developer-tools/claude/memory-and-context-tools.md`
- `appendix/research/developer-tools/claude/claude-integration-guide.md`
- `appendix/research/developer-tools/claude/rule-optimization.md`
- `appendix/research/developer-tools/claude/skill-testing-landscape.md`
- `appendix/research/developer-tools/claude/plugins-and-skills-catalog.md`
- `appendix/research/developer-tools/claude/self-healing-research-summary.md`
- `appendix/research/developer-tools/claude/terminal-progress-and-status-line.md`
- `appendix/research/developer-tools/claude/yolo-per-session-design.md`
- `appendix/research/developer-tools/claude/dangerously-skip-permissions-bugs.md`

## Conventions

**Cookbook project naming**: Cookbook project directories MUST use the suffix `-cookbook-project`. For a source repository named `my-app`, the cookbook project is `my-app-cookbook-project`. This distinguishes cookbook projects from other directories and makes the project type immediately recognizable.

## Manifest

- specialities/claude-code/agent-checklist.md
- specialities/claude-code/agent-structure-reference.md
- specialities/claude-code/authoring-skills-and-rules.md
- specialities/claude-code/design-for-deletion.md
- specialities/claude-code/explicit-over-implicit.md
- specialities/claude-code/manage-complexity-through-boundaries.md
- specialities/claude-code/performance.md
- specialities/claude-code/rule-checklist.md
- specialities/claude-code/rule-structure-reference.md
- specialities/claude-code/separation-of-concerns.md
- specialities/claude-code/simplicity.md
- specialities/claude-code/skill-checklist.md
- specialities/claude-code/skill-structure-reference.md
- specialities/claude-code/support-automation.md
- specialities/claude-code/yagni.md

## Exploratory Prompts

1. If you measured the total tokens your rules and CLAUDE.md consume across a 50-turn session, what would you find? Would the number surprise you? What would you cut first?

2. Think about the last skill you built that felt slow or expensive. Was the model doing work that a shell script could have done deterministically? What was the model actually needed for vs. what was habit?

3. When two of your skills compose — one calls the other — what happens to context? Does the second skill re-load everything the first already loaded? How would you design it so context flows efficiently?

4. If you had to make every rule file fit in 10 lines, what would survive? That's your always-on core. Everything else is progressive disclosure — how would you restructure to load it on demand?

5. What would break if you deleted your CLAUDE.md entirely and relied only on rules and skills? What's in CLAUDE.md that couldn't live anywhere else, and why?
