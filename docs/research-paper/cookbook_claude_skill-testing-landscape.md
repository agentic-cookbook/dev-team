# Skill Testing Landscape

**Date**: 2026-03-30

## Problem

20+ skills and 9 rules with no automated behavioral testing. Linters cover structure; nothing covers "does the skill actually work?"

## Tools Evaluated

### cc-plugin-eval
- **What**: 4-stage pipeline for testing Claude Code plugin triggering
- **Verdict**: Doesn't work — requires `.claude-plugin/plugin.json` marketplace format. Our skills are project-local.
- **Worth borrowing**: programmatic tool capture, session batching, file change rewinding, cost estimation
- **Repo**: https://github.com/sjnims/cc-plugin-eval

### vitest-evals (Sentry)
- **What**: Vitest extension adding `describeEval()` with scorers (0-1 grading)
- **Verdict**: Possible but overkill for filesystem assertions. Better suited for text quality grading.
- **Repo**: https://github.com/getsentry/vitest-evals

### promptfoo
- **What**: Declarative YAML-based prompt testing framework
- **Verdict**: Not skill-specific. Good for prompt comparison, not behavioral testing.
- **Repo**: https://github.com/promptfoo/promptfoo

### Anthropic Eval Tool
- **What**: Web UI in Claude Console for testing prompts
- **Verdict**: Click-based only, no programmatic API, no CI integration.

### skill-creator eval.json
- **What**: Native skill testing built into skill-creator plugin
- **Verdict**: Closed format, only tests trigger detection, limited reporting.

### Braintrust / LangSmith
- **What**: Commercial eval platforms
- **Verdict**: Not Claude Code specific, expensive, more than we need.

## Chosen Approach

**Plain Vitest + Agent SDK** in a disposable sandbox.

- Cookbook owns tests, fixtures, harness code
- `tests/run.sh` copies everything to `../agentic-cookbook-tests/` (disposable)
- Agent SDK runs skills in temp directories with synthetic fixtures
- Assertions are filesystem-based (binary: did this file get created?) — not LLM-judged
- Haiku by default (cheapest), configurable via TEST_MODEL env var
- ~$0.01-0.05 per test, ~$1-3 for full suite

## Key Design Decisions

1. **Separate test repo is just a sandbox** — nothing checked in, populated at test time
2. **Cookbook owns everything** — tests, fixtures, harness, config
3. **No cc-plugin-eval** — requires plugin format we don't have
4. **No vitest-evals** — scorers are for text quality; we need filesystem assertions
5. **Agent SDK over CLI** — more control (model, budget, tools, turns)
6. **Synthetic fixtures only** — never test against real cookbook content

## Non-Determinism Strategy

LLM output varies between runs. Handle by:
- Assert on **outcomes** (files exist, contain keywords) not exact text
- Use **pattern matching** for output assertions (regex, contains)
- Set **budget and turn caps** to prevent runaway sessions
- Accept that some tests may flake — use retries if needed

## Sources

- cc-plugin-eval: https://github.com/sjnims/cc-plugin-eval
- vitest-evals: https://github.com/getsentry/vitest-evals
- Agent SDK: https://platform.claude.com/docs/en/agent-sdk/overview
- Anthropic eval guidance: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
