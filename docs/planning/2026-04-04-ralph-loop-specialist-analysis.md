# Ralph-Loop in Specialist Execution: Pros and Cons Analysis

## Context

The dev-team plugin uses a **worker-verifier loop** to execute specialty-teams: for each team, spawn an independent worker agent, spawn an independent verifier agent, retry up to 3 times on failure. The **ralph-loop** plugin is a stop-hook-based iteration system that repeats the same prompt until a completion promise is met or max iterations are reached. This analysis evaluates whether ralph-loop could replace or augment the specialist execution loop.

## Four Integration Models Evaluated

### Model 1: Ralph-loop wraps the entire specialist run

One ralph-loop per specialist (e.g., security with 15 teams).

| Pros | Cons |
|------|------|
| Session crash recovery via file state | Destroys parallelism (ralph-loop is single-threaded, one state file) |
| Cross-team self-correction (can revisit earlier teams) | Extreme token cost (30-50 iterations re-reading full context) |
| Simple dispatch (one loop per specialist) | Loses worker-verifier independence (same agent plays both roles) |
| | Claude must reconstruct progress from files each iteration — drift risk |
| | Completion promise requires self-assessing 15 teams — fragile |

**Verdict: Poor fit.** Scope too large, parallelism lost, token cost extreme.

### Model 2: Ralph-loop wraps each worker-verifier pair

One ralph-loop per specialty-team. Claude acts as both worker and verifier.

| Pros | Cons |
|------|------|
| Eliminates subagent dispatch overhead | **Breaks the independence principle** — same agent writes and verifies |
| File-based crash recovery per team | Self-verification is weaker than independent verification (confirmation bias) |
| Simpler orchestrator logic | Combined prompt doubles in size or loses specificity |
| Flexible iteration count (not hard-coded to 3) | Parallelism constrained (one state file per session) |
| | If stuck, max-iterations fires but produces no useful output |

**Verdict: Architecturally dubious.** The independence principle is the core quality mechanism — replacing it with self-verification trades correctness for simplicity.

### Model 3: Ralph-loop replaces just the retry loop

Worker and verifier remain separate subagents. Ralph-loop manages the retry/re-dispatch.

| Pros | Cons |
|------|------|
| Preserves worker-verifier independence | Architecturally redundant — the orchestrator already does this in 5 lines |
| Adds persistence for retry state | **Impedance mismatch** — stop hook fires at session-exit, not between subagent calls |
| Removes hard-coded 3-retry limit | Prompt describes orchestration procedure, not direct work (fighting ralph-loop's design) |
| | Token overhead from re-reading orchestration prompt each iteration |
| | State reconciliation fragile (prompt says "run worker" but files show it already ran twice) |

**Verdict: Impedance mismatch.** Ralph-loop operates at session-exit granularity; the retry loop operates at subagent-dispatch granularity. Different levels of abstraction.

### Model 4: Ralph-loop as an outer quality loop

Run the current flow unchanged. Ralph-loop checks the aggregated output afterward.

| Pros | Cons |
|------|------|
| Cross-specialist conflict detection (security vs accessibility suggestions) | Cannot re-run a specific specialist — can only flag problems |
| Does not interfere with existing architecture | Adds latency on top of already-long pipeline |
| Low token cost (reads summary files, not full pipeline) | Diminishing returns — 180+ inner quality checks already ran |
| Ralph-loop's strengths align (well-defined task, clear criterion) | May become a rubber stamp (fires VERIFIED on iteration 1) |
| Compatible with parallel specialist execution | |

**Verdict: Best fit of the four**, but marginal practical value given extensive inner quality controls.

## Cross-Cutting Concerns

### Token Cost
| Model | Relative to current |
|-------|-------------------|
| Current (subagent dispatch) | Baseline — each agent gets only the context it needs |
| Model 1 (whole specialist) | 10-20x — re-reads all prior results every iteration |
| Model 2 (per team) | 1.5-2x — combined prompt, no context scoping |
| Model 3 (retry wrapper) | 1.2-1.5x — orchestration prompt overhead |
| Model 4 (outer quality) | Negligible — reads small summary files |

### Parallelism
Current system runs 2-3 specialists concurrently via Agent tool. Ralph-loop uses a single state file per session — **no concurrent loops possible**. Models 1-3 break parallelism. Model 4 runs after parallelism completes, so it's compatible.

### Independence Principle
Worker and verifier are separate agents that cannot influence each other — an **architectural guarantee**. In any ralph-loop model where one Claude instance plays both roles, this degrades to a prompt instruction ("now pretend you didn't just do the worker's thinking"). Prompt-based role separation is fundamentally weaker.

### Observability
Current system: orchestrator sees every verdict, failure reason, and retry count in conversation context. Integrates with DB layer (`db-finding.sh`, `db-message.sh`). Ralph-loop: limited to iteration count in state file + whatever Claude writes to disk. No structured reporting, no DB integration.

### Recoverability
Ralph-loop's one clear advantage: crash recovery via persistent state file. Current system mitigates this through aggressive persistence (reviews written to disk after each specialist completes), so crash loses at most one specialist's in-progress work.

## Recommendation

**Do not replace the worker-verifier loop with a ralph-loop.** They solve different problems:

- **Ralph-loop**: single-agent iterative refinement with file-based persistence. Paradigm: "do work, check files, iterate."
- **Worker-verifier loop**: multi-agent quality control with architectural independence. Paradigm: "dispatch, verify, retry with feedback."

These are complementary, not competitive. The worker-verifier loop is an orchestration pattern; ralph-loop is an iteration pattern.

### Higher-value alternatives to consider
1. **Add crash recovery** to the orchestrator (persist retry state to disk, not just conversation context)
2. **Add cross-specialist conflict detection** as a post-processing subagent (achieves Model 4's goal without ralph-loop)
3. **Make retry limit configurable** per specialty-team (some teams need more iterations)

### Where ralph-loop could fit in dev-team
Best suited for a different layer — wrapping a top-level `/dev-team generate` invocation for unattended iterative improvement of an entire project. But user approval gates in the generate workflow make unattended loops impractical today.
