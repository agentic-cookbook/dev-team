# Claude Cost Optimization & Hybrid LLM Routing
### Complete Research from April 11, 2026

> **Context:** Mike Fullerton, Claude Max 20x subscriber ($200/month), Mac Studio M2 Ultra 64GB  
> **Problem:** Extra usage costs spiraling to $500-700+/month and accelerating  
> **Goal:** Reduce costs through hybrid routing, local models, and token efficiency

---

## Table of Contents

1. [The Billing Problem](#the-billing-problem)
2. [Claude Plans & Account Types](#claude-plans--account-types)
3. [Usage Limit Crisis (March-April 2026)](#usage-limit-crisis-march-april-2026)
4. [Extra Usage System](#extra-usage-system)
5. [Hybrid LLM Routing Strategy](#hybrid-llm-routing-strategy)
6. [Routing Tools](#routing-tools)
7. [Local Models Overview](#local-models-overview)
8. [Ollama Setup & Testing](#ollama-setup--testing)
9. [The Context Size Problem](#the-context-size-problem)
10. [Graphify — Token Reduction via Knowledge Graphs](#graphify--token-reduction-via-knowledge-graphs)
11. [Key Findings & Conclusions](#key-findings--conclusions)
12. [Action Plan](#action-plan)

---

## The Billing Problem

### Actual Billing History (from screenshots)

| Month | Subscription | Extra Usage | Total |
|-------|-------------|-------------|-------|
| Jan 2026 | $100.00 | — | $100.00 |
| Feb 2026 | $155.52 | — | $155.52 |
| Mar 2026 | $200.00 | $123.80 | $323.80 |
| Apr 2026 (9 days in) | $200.00 | $317.28 spent (79% of $400 limit) | $517.28+ |

**April trajectory: $600-700+ for the full month at current burn rate.**

The acceleration is driven by:
- Heavy Claude Code agentic use (file reads, grep, glob, refactors)
- All tasks routing to Opus 4.6 regardless of complexity
- 10KB+ global CLAUDE.md + 16 active plugins prepended to every request
- Context window burn on each session start

### Two Accounts — Why It Doesn't Work

Running two Max 20x accounts ($400/month total) was considered and rejected:
- No way to pool usage between accounts
- Manual context switching between two separate Claude Code instances
- Same cost as current overage situation, with added complexity
- Terms of service designed for "ordinary, individual usage" — two accounts for quota doubling is a gray area
- The math doesn't change the underlying problem

---

## Claude Plans & Account Types

### Individual Plans

| Plan | Cost | Usage vs Free |
|------|------|---------------|
| Free | $0 | Baseline |
| Pro | $20/mo | 5x Free |
| Max 5x | $100/mo | 25x Free |
| **Max 20x** | **$200/mo** | **100x Free ← current** |

### Business Plans

- **Team Standard:** $25/seat/month (annual) / $30 month-to-month, 5-seat minimum
- **Team Premium:** $150/seat/month — includes Claude Code
- **Enterprise:** Custom pricing — SSO, SCIM, audit logs, compliance APIs, dedicated support

### Key Policy Points

- Max 20x is the ceiling for individual plans — no higher individual tier exists
- Extra usage is billed at standard API rates on top of subscription
- OAuth tokens (Max subscription) are only permitted for Claude Code and Claude.ai — not third-party harnesses
- Advertised limits assume "ordinary, individual usage" — heavy agentic use burns quota faster than expected
- Enterprise is the next step if solo power-user needs exceed Max 20x + extra usage

---

## Usage Limit Crisis (March-April 2026)

### What Happened

Claude experienced a massive user surge in March 2026 after the OpenAI/Pentagon controversy drove users to Claude. Web traffic jumped 30%+ month-over-month, Claude hit #1 on the US App Store.

Anthropic's response was to **tighten** peak-hour limits, not expand them:

> "To manage growing demand for Claude we're adjusting our 5-hour session limits for free/Pro/Max subs during peak hours. Your weekly limits remain unchanged."  
> — Thariq Shihipar, Anthropic engineer, March 26, 2026

**Peak hours (slower limits):** 5am–11am PT / 1pm–7pm GMT on weekdays

**Impact:** ~7% of users hit limits they never hit before. Max 20x subscribers reported quota exhaustion in as little as 19 minutes instead of the expected 5 hours. Single prompts jumping usage from 21% to 100%.

### The Opacity Problem

Anthropic does not publish exact token limits. Plans are described only as relative multipliers ("20x Pro usage"). Users have no way to plan ahead — they only discover limits by hitting them.

### The March 2026 Promotion (Expired)

A temporary 2x off-peak usage promotion ran March 13–28, 2026. It has expired. The $200 credit that appeared in Mike's account was likely related to this promotion or goodwill credit from limit complaints.

---

## Extra Usage System

### How It Works

Extra usage is a pay-as-you-go overlay on top of your subscription. When you hit your plan's session/weekly limits, Claude Code continues by billing at standard API rates against a prepaid balance.

**Setup:**
1. Settings → Usage → Extra Usage → Enable toggle
2. Set a monthly spend limit (the cap before extra usage stops)
3. Buy prepaid balance ("Buy extra usage")
4. Enable auto-reload to automatically top up when balance runs low

### Key Settings (from screenshots)

- **Monthly spend limit:** Was $100 → raised to $400
- **Amount spent (April):** $317.28 (79% of $400 limit, 9 days into month)  
- **Current balance:** $11.97 (nearly empty, auto-reload on)
- **Balance resets:** May 1

### The $100 Monthly Limit Bug

The initial problem was that the extra usage monthly spend limit was set to $100, which was hit and blocked further usage. The fix was to raise the limit via "Adjust limit" — but this just allows more spending, it doesn't solve the underlying consumption problem.

### Extra Usage Pricing

Billed at standard API rates:
- Claude Opus 4.6: $5/$25 per million tokens (input/output)  
- Claude Sonnet 4.6: $3/$15 per million tokens
- Claude Haiku 4.5: Significantly cheaper

The Sonnet 1M context option in Claude Code's `/model` menu is explicitly flagged as "Billed as extra usage at $3/$15 per Mtok."

---

## Hybrid LLM Routing Strategy

### The Core Concept

Claude Code reads a single environment variable — `ANTHROPIC_BASE_URL` — to determine where to send requests. Point it at a local proxy instead of Anthropic, and that proxy routes each request to the optimal backend automatically.

```
Claude Code (terminal)
        │
        │  ANTHROPIC_BASE_URL=http://localhost:3456
        ▼
┌──────────────────────┐
│   Local Router/Proxy │  ← CCR, LiteLLM, or Bifrost
└──────────┬───────────┘
           │
    ┌──────┴──────────────────────┐
    │                             │
    ▼                             ▼
Local Model                 Anthropic API
(Qwen, Devstral, etc.)     (Claude Opus/Sonnet)
```

### Recommended Routing Map

| Task Type | Model | Cost |
|-----------|-------|------|
| File reads, glob, grep | Local Qwen/Devstral | Free |
| Boilerplate, simple edits | Local Qwen/Devstral | Free |
| Mid-complexity coding | DeepSeek V3.2 via OpenRouter | ~$0.27/MTok |
| Bug diagnosis, cross-file reasoning | Claude Sonnet (subscription) | Quota |
| Architecture, hard problems | Claude Opus (subscription) | Quota |

### The Fundamental Tension Discovered

**Your setup is optimized for Opus, not local models.**

- 10KB global CLAUDE.md
- 16 active plugins (each injects context)
- Extensive hooks (whippet, session-tracker, repo-hygiene, yolo scripts)
- `"model": "opus"` hardcoded in settings.json

All of this gets prepended to every request. Opus handles it instantly via Anthropic's infrastructure. A local Qwen model processing 10,000+ tokens of context before a "reverse a string" request will always be slow.

**Direct curl to Ollama (no Claude Code overhead):** 7 seconds for Swift string reversal  
**Via Claude Code with full context:** 2m 40s+ for the same task

The overhead is Claude Code's system prompt, not the model.

---

## Routing Tools

### Tool 1: Claude Code Router (CCR)

**GitHub:** https://github.com/musistudio/claude-code-router  
**Best for:** Automatic task-based routing, drop-in replacement

CCR is a local proxy that intercepts Claude Code requests and routes by task type — file reads go local, complex reasoning goes to Anthropic. No manual switching.

```bash
npm install -g claude-code-router
claude-code-router start
export ANTHROPIC_BASE_URL="http://localhost:3456"
```

**⚠️ Known bug:** CCR disables prompt caching with non-Anthropic APIs. Fix:  
https://github.com/musistudio/claude-code-router/pull/1220

**⚠️ Billing mode switch:** When routing to non-Anthropic providers, Claude Code switches from subscription billing to API billing. Watch for "API Usage Billing" vs "Claude Max" at startup.

### Tool 2: LiteLLM Proxy

**GitHub:** https://github.com/BerriAI/litellm  
**Docs:** https://docs.litellm.ai  
**Best for:** Multi-provider routing, format translation, Docker deployment

LiteLLM translates between API formats — it can make Ollama look like Anthropic to Claude Code, and route different model names to different backends.

```bash
pip install litellm[proxy]
litellm --config litellm_config.yaml --port 4000
export ANTHROPIC_BASE_URL="http://localhost:4000"
```

### Tool 3: Bifrost Gateway

**Guide:** https://dev.to/debmckinney/claude-code-with-any-llm-a-step-by-step-guide-using-bifrost-2l9d  
**Best for:** Teams, automatic failover, semantic caching, MCP passthrough

Key features:
- Automatic failover (Anthropic down → Gemini → local)
- Semantic caching with vector similarity (saves money on repeated context)
- MCP tool passthrough — tools configured in Bifrost available to any routed model

### Tool 4: OpenRouter

**URL:** https://openrouter.ai  
**Best for:** Cloud fallback for mid-tier tasks without local hardware

Aggregates 50+ providers with automatic failover. Pay per token, no subscription. Good mid-tier option when local quality isn't enough but Anthropic quota is precious.

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1/anthropic"
export ANTHROPIC_API_KEY="YOUR_OPENROUTER_KEY"
```

---

## Local Models Overview

### The Landscape (April 2026)

The open-source model ecosystem has closed the gap with proprietary models significantly. Current best open-source models perform roughly at the level of frontier models from 2024-2025. For most coding tasks the gap is imperceptible — complex multi-file reasoning and novel architecture decisions still favor Claude.

### Top Coding Models (Runnable on M2 Ultra 64GB)

| Model | Size | VRAM (Q4) | Tool Calling | Notes |
|-------|------|-----------|-------------|-------|
| **Qwen2.5-Coder 32B** | 32B | ~20GB | ✅ | Best practical choice, strong agentic coding |
| **Qwen2.5-Coder 72B** | 72B | ~45GB | ✅ | Near-Sonnet quality, fits in 64GB |
| **Devstral** | ~24B | ~16GB | ✅ | Mistral's coding specialist, agentic-first |
| **GLM-4.7-Flash** | 7B | ~5GB | ✅ | Fast, cheap, simple tasks |
| **Gemma 4 26B** | 26B MoE | ~8GB active | ✅ | Good generalist, runs on MacBook Pro |

### Cloud-Only (Too Large for Local)

| Model | Notes | API Cost |
|-------|-------|---------|
| DeepSeek V3.2 | Strong reasoning, MIT license, agentic workloads | ~$0.27/MTok input |
| Kimi K2.5 | Between Sonnet 4.5 and Opus 4.5 in real-world use | ~$0.50/MTok input |
| GLM-5 | Leads benchmarks, 744B params total, needs multi-GPU | Via API only |

### Critical Requirements for Claude Code

1. **Tool calling is non-negotiable** — Claude Code relies on native tool calling for file reads, bash, edits. Models without it fail silently.
2. **Minimum 32K context window** — Claude Code's system prompt alone is ~20K tokens.
3. **Qwen3-Coder and DeepSeek V3 both meet both requirements** — most smaller/older models don't.

### Download Links

- Qwen2.5-Coder GGUF: https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-GGUF
- Devstral via Ollama: `ollama pull devstral`
- All Ollama models: https://ollama.com/library
- Unsloth GGUF collection: https://huggingface.co/unsloth

---

## Ollama Setup & Testing

### Installation

```bash
brew install ollama
ollama serve          # starts server (may auto-start as macOS service)
ollama pull qwen2.5-coder:32b    # ~20GB download
ollama pull devstral              # Mistral coding specialist
```

### Verify GPU Usage

```bash
ollama ps
# Should show: 100% GPU for M2 Ultra
```

### Point Claude Code at Ollama

```bash
export ANTHROPIC_BASE_URL="http://localhost:11434"
export ANTHROPIC_API_KEY="ollama"
claude --model qwen2.5-coder:32b
```

### Shell Aliases (Add to ~/.zshrc)

```bash
# Local model - free, no quota burn
alias claude-local='ANTHROPIC_BASE_URL="http://localhost:11434" ANTHROPIC_API_KEY="ollama" claude --model qwen2.5-coder:32b'

# Anthropic subscription - full Opus power
alias claude-anthropic='unset ANTHROPIC_BASE_URL && unset ANTHROPIC_API_KEY && claude'
```

### The Critical Attribution Header Fix

Claude Code prepends an attribution header that **invalidates the KV cache**, making local inference ~90% slower. This **must** be set in `~/.claude/settings.json` — an environment variable export does NOT work:

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  }
}
```

**Common mistake:** Placing this inside `"permissions"` instead of at the top level of the JSON. It must be a top-level key.

### Test Ollama Directly (Bypasses Claude Code)

```bash
time curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder:32b",
  "messages": [{"role": "user", "content": "write a swift function to reverse a string"}],
  "stream": false
}'
```

**Result on M2 Ultra:** 7 seconds — fast and correct.

### Ollama Logging

```bash
# Real-time log stream
log stream --predicate 'process == "ollama"' --level info

# Filtered for inference events
log stream --predicate 'process == "ollama"' --level info 2>/dev/null | grep -E "prompt|token|generated|request|model"
```

---

## The Context Size Problem

### What Was Discovered

Direct Ollama curl: **7 seconds**  
Via Claude Code (same task, same model): **2m 40s+**

The difference is **not** the model. It's Claude Code's system prompt overhead:

- Global `~/.claude/CLAUDE.md`: 10,168 characters (~2,500 tokens)
- 16 active plugins, each injecting their own instructions
- Whippet hooks, session-tracker, repo-hygiene scripts firing on every event
- `"model": "opus"` hardcoded in settings.json causing model mismatch errors

### The settings.json Issues Found

```json
// WRONG - env fix inside permissions, not top level
"permissions": {
    "env": { "CLAUDE_CODE_ATTRIBUTION_HEADER": "0" }
}

// WRONG - hardcoded model overrides --model flag
"model": "opus"
```

### Minimal Test Settings.json

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  },
  "model": "qwen2.5-coder:32b",
  "permissions": {
    "allow": [
      "Bash(*)",
      "Edit(*)",
      "Write(*)"
    ]
  },
  "skipDangerousModePermissionPrompt": true
}
```

### Implication for Local Routing

**Your current Claude Code environment is too rich for local models.** The setup that makes it powerful with Opus (deep CLAUDE.md, 16 plugins, extensive hooks) is exactly what makes local models slow.

Options:
1. **Separate local profile** with stripped-down settings for local model sessions
2. **Use Ollama directly** (via curl or simple scripts) for throwaway tasks outside Claude Code
3. **Graphify** to reduce token consumption within Claude Code sessions

---

## Graphify — Token Reduction via Knowledge Graphs

**GitHub:** https://github.com/safishamsi/graphify  
**Stars:** 19.8k | **Last release:** April 10, 2026 (v0.4.0)

### What It Does

Graphify builds a persistent knowledge graph of your codebase, then Claude navigates the graph instead of grepping raw files. The result: **71.5x fewer tokens per query** on a 52-file mixed corpus.

**Three-pass approach:**
1. **AST pass** — deterministic tree-sitter extraction of classes, functions, imports, call graphs. No LLM, no cost, no data leaves your machine.
2. **Whisper pass** — local transcription of video/audio files (if any)
3. **Claude pass** — parallel subagents extract concepts and relationships from docs, papers, images

Every relationship tagged: `EXTRACTED` (found directly), `INFERRED` (confidence score), or `AMBIGUOUS`.

### Why This Matters for Your Costs

Right now Claude Code starts every session by reading and searching raw source files to understand your codebase. With graphify installed:

- A PreToolUse hook fires before every Glob and Grep call
- Claude sees: *"Knowledge graph exists. Read GRAPH_REPORT.md before searching raw files."*
- Claude navigates the compact graph (~1 page) instead of grepping through your codebase

**First run:** Costs tokens (Claude subagents build the graph)  
**Every subsequent session:** Reads compact graph — dramatically fewer tokens

### Installation

```bash
pip install graphifyy
graphify install                    # installs Claude Code skill
```

Then in your project:
```bash
/graphify .                         # build the graph (one-time, costs tokens)
graphify claude install             # installs PreToolUse hook in settings.json
```

### Output Files

```
graphify-out/
├── graph.html          # interactive visual graph
├── GRAPH_REPORT.md     # god nodes, surprising connections, suggested questions
├── graph.json          # persistent graph - queryable later
└── cache/              # SHA256 cache - re-runs only process changed files
```

### Querying the Graph

```bash
graphify query "show the auth flow"
graphify query "what connects DigestAuth to Response?"
graphify path "AuthManager" "APIClient"
```

### MCP Server Mode

```bash
python -m graphify.serve graphify-out/graph.json
# Exposes: query_graph, get_node, get_neighbors, shortest_path
```

### Watch Mode (Auto-sync)

```bash
/graphify ./src --watch
# Code saves → instant AST rebuild
# Doc changes → notifies you to run --update
```

### Token Benchmark Results

| Corpus | Files | Token Reduction |
|--------|-------|----------------|
| Karpathy repos + 5 papers + 4 images | 52 | **71.5x** |
| graphify source + Transformer paper | 4 | 5.4x |
| Small synthetic library | 6 | ~1x |

Token reduction scales with corpus size. The savings compound over time via the SHA256 cache — re-runs only process changed files.

---

## Key Findings & Conclusions

### What Works

1. **Ollama on M2 Ultra is fast** when called directly — 7 seconds for coding tasks
2. **100% GPU utilization** confirmed via `ollama ps`
3. **The attribution header fix** is real and important (must be top-level in settings.json)
4. **The two-alias approach** (`claude-local` / `claude-anthropic`) is the pragmatic manual routing solution

### What Doesn't Work (Yet)

1. **Automatic local routing via CCR** with your current rich Claude Code setup — context overhead makes local models too slow for agentic use
2. **Drop-in replacement** — Qwen can't transparently replace Opus when it's receiving 20K+ tokens of context per request

### The Right Mental Model

Your Claude Code environment is a **finely tuned Opus machine**. Local models are a **different tool** that requires a different context profile. The hybrid routing vision is achievable, but needs:

- A stripped-down settings profile for local sessions OR
- Graphify to reduce per-session token consumption OR  
- Both

### The Biggest Lever

**Graphify is likely more impactful than local routing for your specific situation.** Your costs are driven by Claude Code's file-reading and search behavior within sessions — exactly what graphify addresses. Local routing helps with generation tokens; graphify helps with the context tokens that are burning your quota on every session start.

---

## Action Plan

### Immediate (Stop the Bleeding)

- [x] Raise extra usage monthly spend limit to a comfortable ceiling
- [ ] Lower it again once routing is in place
- [ ] Add `claude-local` and `claude-anthropic` aliases to `~/.zshrc`

### Short Term (This Week)

- [ ] Install graphify on your highest-token-burn project
  ```bash
  pip install graphifyy && graphify install
  cd ~/projects/your-main-project
  /graphify .
  graphify claude install
  ```
- [ ] Measure token reduction over one week of normal use
- [ ] Consider pulling Devstral alongside Qwen for comparison
  ```bash
  ollama pull devstral
  ```

### Medium Term

- [ ] Create a stripped-down `~/.claude/settings.local.json` for local model sessions
- [ ] Set up CCR with simple routing rules (local for file ops, Anthropic for complex reasoning)
- [ ] Configure OpenRouter as mid-tier fallback for DeepSeek V3.2

### Ongoing

- [ ] Monitor via Settings → Usage dashboard
- [ ] Track whether graphify meaningfully reduces session token counts
- [ ] Revisit local routing once graphify reduces baseline context size

---

## Reference Links

| Resource | URL |
|----------|-----|
| Claude Code Router | https://github.com/musistudio/claude-code-router |
| CCR prompt caching fix | https://github.com/musistudio/claude-code-router/pull/1220 |
| LiteLLM | https://github.com/BerriAI/litellm |
| LiteLLM docs | https://docs.litellm.ai |
| Bifrost guide | https://dev.to/debmckinney/claude-code-with-any-llm-a-step-by-step-guide-using-bifrost-2l9d |
| Graphify | https://github.com/safishamsi/graphify |
| Ollama | https://ollama.com |
| Ollama model library | https://ollama.com/library |
| Unsloth GGUF models | https://huggingface.co/unsloth |
| OpenRouter | https://openrouter.ai |
| Qwen2.5-Coder GGUF | https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-GGUF |
| Unsloth Claude Code guide | https://unsloth.ai/docs/basics/claude-code |
| Claude Code hooks reference | https://code.claude.com/docs/en/hooks-guide |
| Claude extra usage docs | https://support.claude.com/en/articles/12429409-manage-extra-usage-for-paid-claude-plans |
| Claude Max plan docs | https://support.claude.com/en/articles/11049741-what-is-the-max-plan |
| DataCamp CCR tutorial | https://www.datacamp.com/tutorial/claude-code-router |
| Open LLM leaderboard | https://benchlm.ai/blog/posts/best-open-source-llm |
| Open source coding LLMs guide | https://pinggy.io/blog/best_open_source_self_hosted_llms_for_coding/ |

---

## Appendix: Settings Files

### Minimal Test Settings (No Plugins, No Hooks)

```json
{
  "env": {
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  },
  "model": "qwen2.5-coder:32b",
  "permissions": {
    "allow": [
      "Bash(*)",
      "Edit(*)",
      "Write(*)"
    ]
  },
  "skipDangerousModePermissionPrompt": true
}
```

### Shell Aliases for ~/.zshrc

```bash
# Hybrid routing aliases
alias claude-local='ANTHROPIC_BASE_URL="http://localhost:11434" ANTHROPIC_API_KEY="ollama" claude --model qwen2.5-coder:32b'
alias claude-anthropic='unset ANTHROPIC_BASE_URL && unset ANTHROPIC_API_KEY && claude'

# Check which mode Claude Code is using
alias claude-mode='echo "BASE_URL: ${ANTHROPIC_BASE_URL:-not set (using Anthropic)}"'
```

### Direct Ollama Test Command

```bash
# Bypass Claude Code entirely - test model directly
time curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5-coder:32b",
  "messages": [{"role": "user", "content": "your prompt here"}],
  "stream": false
}'
```

---

*This document covers research from an April 11, 2026 session. Candidate recipe for the [Agentic Cookbook](https://github.com/agentic-cookbook) — consider adding as `cookbook/recipes/claude-cost-optimization.md`.*
