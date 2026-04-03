# Cookbook Rule (Generated)

This is the reference template for the minimal always-on rule installed in consuming projects. `/install-cookbook` produces this file; `/configure-cookbook` regenerates it when preferences change. The always-on rule contains only behavioral guardrails — all workflow content (principles, planning pipeline, implementation pipeline, verification) is loaded on-demand by the `/cookbook-start` and `/cookbook-next` pipeline skills.

---

## Template

The generated `.claude/rules/cookbook.md` file contains:

```markdown
# Cookbook

1. Confirm you are in the correct project before making changes.
2. Investigate unfamiliar content before overwriting.
3. Fix only what was asked — no unauthorized additions.
4. Do not skip Phase 2 (Make It Right).
5. Do not skip writing tests.
6. Do not optimize without evidence.

When planning or implementing features, use /cookbook-start.
```

## Notes

- **Per-turn cost**: ~500 bytes (down from 17,689 bytes in the original 3-file installation)
- **No mandatory file reads**: The rule itself does not trigger any file reads. File reads happen on-demand when `/cookbook-start` or `/cookbook-next` is invoked.
- **Pipeline skills**: `/cookbook-start` initializes a pipeline session (planning or implementation). `/cookbook-next` advances one step, loading one concern from `../agentic-cookbook/workflows/pipeline-concerns.json`.
- **Conditional content**: Previously included conditional sections (auto-lint, committing, recipes, contributions) are now handled as pipeline concerns or preferences — they do not appear in the always-on rule.
