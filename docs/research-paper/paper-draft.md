# Designing an Autonomous Multi-Agent Development System
## Seven Design Drivers from Building a Claude Code Devteam

*A practitioner's essay on what I learned co-designing a multi-agent orchestration system with Claude.*

---

## 1. Introduction

I've spent the last several months building a thing I've come to call my "devteam." It's a Claude Code plugin — a long-running Python process that orchestrates dozens of specialized Claude agents through structured workflows, building features and analyzing code on command. I co-designed it with Claude itself, iterating daily, throwing away drafts, restarting whole subsystems, and (more than once) staring at the billing dashboard with an increasingly nervous expression.

What started as "let me wire a few agents together" turned into an education in constraints. The devteam today is shaped by a set of non-negotiable requirements I didn't know I needed when I started:

- It must be **flexible** enough to run under different hosts — a Claude Code conversation today, a headless daemon tomorrow, something else after that.
- It must be **extensible**, because the domains I care about keep expanding and I refuse to rewrite the core every time I want a new specialist.
- It must be **efficient** in its use of Claude, because I pay $200 a month for Claude Max and there is no universe in which that stretches to cover naive context accumulation across a hundred-turn pipeline.
- It must leverage a **large, scalable corpus of criteria** — principles, guidelines, specs — that grows over time and serves as the shared vocabulary of all the agents.

And, because I've now watched Claude succeed and fail in enough different ways to have opinions, I've arrived at three observations about the model itself:

- **Claude needs guardrails.** Left to govern itself, it will invent features, skip steps, retry unbounded loops, and occasionally hallucinate the existence of files.
- **Claude needs clear tasks.** Vague instructions ("review this") produce vague output; bounded instructions ("check whether this matches the contrast-ratio requirement in the accessibility cookbook") produce usable findings.
- **Claude can be overwhelmed by too much input.** Dump the whole codebase into one prompt and the agent loses the plot within three turns.

Taken together, these form what I think of as the **seven design drivers** of the devteam: flexibility, extensibility, Claude-efficiency, scalable criteria, guardrails, clear tasks, and avoiding overwhelm. Everything I built is traceable to one or more of them — and every time I've violated one, something has broken, usually expensively.

This paper is my attempt to write down what I've learned. It's grounded in a case study — the devteam — but the deeper argument is that these seven drivers are not specific to my project. Anyone building an autonomous multi-agent system on top of a large language model will meet the same pressures. The question is whether you design for them deliberately or discover them the hard way.

---

## 2. Background: Why Multi-Agent Systems on Claude Are Hard

Before the design choices make sense, it's worth saying plainly why this is a hard problem. Reading Anthropic's docs, you'd be forgiven for thinking multi-agent orchestration is a solved problem — spawn a subagent, wire up a few tools, delegate work. And for simple tasks it is. But "multi-agent" in any interesting sense — long-running pipelines, cross-cutting verification, shared state between participants — runs into three structural problems that compound each other.

**Context accumulation kills token budgets.** This is the one I hit first, and hardest. Every turn of a Claude Code conversation re-sends everything you've put in front of the model: system prompt, CLAUDE.md files, rule files in `.claude/rules/`, prior tool results, prior assistant messages. A 10KB rule file is cheap on turn 1 and catastrophic by turn 50 — you've now paid for that same 10KB fifty times. In the span of six weeks earlier this year my Claude usage went from a comfortable $100 a month to a projected $600+ a month, entirely because I was accumulating context in conversations that should have been short-lived. The economics don't work if you don't treat context as a scarce resource.

**LLM drift is the default.** If you don't bound what a Claude agent can do, it will do things you didn't ask for. It will invent a helper function. It will add error handling you didn't request. It will try a "quick fix" that rewrites three unrelated files. My favorite genre of drift is what I call *task inflation*: I ask for a bug fix, the agent delivers a bug fix plus a refactor plus a test plus a documentation update plus a commit with a 12-line message explaining the philosophy behind the change. Sometimes this is wonderful. Usually it's a nightmare, because the agent hasn't understood the actual task well enough to know when to stop.

**Coordination is not free.** Any system with more than one agent — even two — has to answer questions about how they communicate, who validates whose work, and how findings get aggregated. The naive answer is "put them in the same conversation." This is wrong. Sharing a conversation merges their contexts and defeats the whole point of having specialists. The right answer involves schema-validated messages, shared state persisted outside any conversation, and a deliberate choice about who is allowed to speak to the user. All of that is infrastructure, and it's infrastructure you have to build yourself because Claude Code (sensibly) does not prescribe it.

These three problems interact. Context accumulation makes it expensive to run long pipelines. LLM drift makes short pipelines unreliable. Coordination failures make multi-agent pipelines incoherent. You can fix one by worsening another — e.g., add more guardrails to prevent drift, but now your rule files are 400 lines and your context budget is blown. Any solution that survives contact with real work has to hit all three at once. That's the design problem the devteam is a response to.

---

## 3. Architecture Overview: The Devteam

Let me briefly describe what the devteam actually is, because the rest of the paper will repeatedly reference it.

At the top, there's a **conductor**: a long-running Python process, one per active session. The conductor is not an LLM. It runs a main loop that picks up work, asks a team-lead what to do next, dispatches LLM work, streams events to persistence, and handles user input. Critically, the conductor is *not a Claude Code conversation*. It runs outside any chat. This is the single most important architectural choice in the system and we'll come back to it in §4.3.

The conductor talks to the LLM through a **dispatcher**. The dispatcher is the one place in the system that knows anything about Claude. The default implementation (`ClaudeCodeDispatcher`) spawns a `claude -p` subprocess — the same `claude` CLI I use by hand — with a specific agent definition, a specific prompt, and (optionally) a JSON schema for the expected response. It drains the subprocess stream, parses the final message, validates against the schema, and returns a structured result. Because the dispatcher is pluggable, a future `LocalDispatcher` could run an on-prem open-source model with no changes to the conductor.

The conductor also talks to an **arbitrator**: a single API facade over a shared database. The arbitrator defines 21 resource types — session, state, message, gate, result, finding, interpretation, event, task, request, and so on — and every inter-component write is schema-validated at the boundary. All coordination between participants happens through the arbitrator. No participant talks directly to another.

Inside the conductor, work is organized by a **team-lead**. A team-lead is a state machine with a manifest of specialists and specialty-teams. Most transitions are pure Python. But at specific points — what I call **judgment nodes** — the team-lead asks the LLM a single focused question (prompt + response schema + legal successors) and incorporates the answer as the next state. The FSM decides *that* a decision needs to be made; the LLM decides *what* the decision is.

The actual work is done by **specialists**. A specialist is a role (e.g., "security," "accessibility," "code quality") with a manifest of **specialty-teams**. Each specialty-team focuses on exactly one cookbook artifact. A specialty-team consists of two agents: a **worker** that produces findings, and a **verifier** that checks them against the artifact's requirements. If the verifier fails the worker's output, the loop retries — up to three times — then escalates. Independently, some specialists invoke **consulting teams**: cross-cutting reviewers that check every specialty-team's output for concerns like security or accessibility.

Finally, the devteam depends on a large shared knowledge base called the **cookbook**. The cookbook is organized as a three-tier hierarchy: **ingredients** (atomic component specs), **recipes** (compositions that assemble ingredients into features), and **cookbooks** (whole-application definitions that assemble recipes). Everything an agent needs to know about "what good looks like" for a given domain lives in this corpus. As of writing, the cookbook includes 242 research files, ~203,000 words, and 20+ engineering principles. Specialists and specialty-teams don't duplicate this content — they reference it by path.

That's the system. Seven drivers, one conductor, one arbitrator, one cookbook, many teams. The rest of the paper explains why it ended up this shape.

---

## 4. The Seven Design Drivers

Here's where the requirements meet the mechanisms. I'll take each driver in turn, state the claim, trace the requirement back to a concrete pressure I hit while building, and describe the mechanism the devteam uses to answer it.

### 4.1 Flexibility — Running Anywhere, Evolving Anywhere

**Claim**: the system must adapt to new runtime hosts and new domains without touching core code.

This requirement started as a hedge. I began building inside a Claude Code conversation, where the "team-lead" was just me typing into chat. Then I realized I wanted the devteam to run unattended, in the background, while I did other things. Then I started thinking about a web UI. Then I wondered if I could run the whole thing against an open-source model, either for privacy or to hedge against Anthropic's pricing. Each of these would have been a rewrite if I'd baked Claude Code assumptions into the core.

The answer is a pluggable **dispatcher abstraction**. The conductor never calls an LLM directly. Instead, it calls `dispatcher.dispatch(request)` and receives a `DispatchResult`. Concrete implementations — `ClaudeCodeDispatcher` today, `LocalDispatcher` tomorrow — slot in at startup via a config flag. The dispatcher is also the only place that knows about concrete Claude model IDs. Team-playbooks reference **logical model names** (`high-reasoning`, `balanced`, `fast-cheap`, `local`) which the dispatcher resolves to whatever concrete model makes sense for the current runtime.

The same pattern applies to persistence. The arbitrator delegates all storage to a **storage-provider** dispatcher that currently has a markdown backend and is slated for SQLite in production. The arbitrator itself doesn't know which backend is running. A new backend is a new file, not a core rewrite.

Why this matters: I've already pivoted twice since starting. First from "specialists as subagents inside a chat" to "specialists as subprocesses dispatched by the chat." Then, more recently, from "chat as the outer loop" to "headless Python process as the outer loop." Neither pivot required me to rewrite what a specialist *does* — only where it runs. The seam between "what" and "where" is the dispatcher, and it's the seam I'm most grateful for.

### 4.2 Extensibility — Adding Without Rewriting

**Claim**: new specialists, specialty-teams, skills, and consulting teams are files, not code.

Early on, adding a new specialist meant modifying the conductor: register the role, wire in the manifest, extend a config. This was fine when I had three specialists. By the time I had ten, it was painful. By the time I had twenty-two, it would have been unusable.

The devteam now treats specialists and specialty-teams as **declarative files**. A specialist lives at `specialists/<domain>.md`. Its frontmatter declares the role. Its body contains a `## Manifest` section that lists the specialty-team files it runs, a `## Cookbook Sources` section that lists the principles it references, and an optional `## Consulting Teams` section. A specialty-team lives at `specialty-teams/<category>/<name>.md`, with frontmatter for the artifact path and a body with two sections: `## Worker Focus` and `## Verify`. Adding a new specialty-team is six steps: copy the template, fill in the artifact, write the focus, write the verify criteria, reference it from a specialist manifest, and run the orchestrator. No code touched. No conductor rebuild.

The same philosophy applies to **skills**. A Claude Code skill is distributed as a triad — `SKILL.md` (the behavior), a checklist (the validation steps), and a structure-reference (the format contract). Adding a skill means dropping a new directory. The conductor discovers it. Rules, principles, ingredients — all files.

The payoff has been real. The devteam currently organizes 22 specialists across 13 domain categories, 6 platform categories, and a handful of meta categories (project management, codebase decomposition, recipe quality). Between them, they reference over 230 specialty-teams. None of that count required a core rewrite. The spec for how you add one sits in a single file — `specialist-guide.md` — and the procedure is short enough to follow at 11pm.

Consulting teams deserve a specific mention because they're a clean example of backwards-compatible extension. Consulting teams were added after the specialist pipeline was already running. Because the `## Consulting Teams` section is optional, every existing specialist kept working. New specialists that needed cross-cutting verification picked it up just by adding the section. No core code changed. That's the test I apply to any new feature: can it be added by editing files in the existing structure?

### 4.3 Claude Usage Efficiency — Scaling Under Claude Max

**Claim**: long pipelines must run under a $200 a month Claude Max subscription, not per-token API billing.

This is the driver that drove the most expensive architectural decision in the whole project: the conductor pivot.

Until recently, the outer loop of the devteam ran inside a Claude Code conversation. The "team-lead" was an agent with extensive system prompts that orchestrated specialists by spawning subagents. It worked — for small runs. It broke for large runs, and it broke because of a problem that was invisible during development and obvious in retrospect: **context accumulation**.

Here's the math. A Claude Code conversation re-sends the full system prompt, CLAUDE.md files, and all prior messages on every turn. In a 50-turn conversation, a 10KB rule file isn't 10KB of context — it's 500KB, because the model sees it on every single turn. My rule files weren't 10KB. The cookbook's always-on rules started at 381 lines, 17,689 bytes per turn. Spread across a long session with heavy subagent dispatch, that meant I was paying hundreds of thousands of tokens just to remind the model what it was already told.

The billing trajectory was instructive. January: $100/month, comfortable. March: $323.80. April through the 9th: $517. Projected full-month April: $600–700. This with a "Max 20x" subscription (the $200/mo tier), which means those dollars aren't coming out of my pocket but *are* coming out of my rate limits — I was hitting usage caps daily. At that point I had two choices: stop running long pipelines or change the architecture.

I changed the architecture. Three things happened.

**First**, the conductor became headless. The outer loop is now a Python process — not a conversation, not a subagent, not anything that accumulates context. Every time it needs the LLM, it spawns a `claude -p` subprocess with a fresh prompt and a fresh agent definition. That subprocess lives for exactly one dispatch and then dies. No conversation, no context buildup. The 50-turn pipeline becomes 50 independent one-shot dispatches. Total context cost is linear in dispatches, not quadratic in conversation length.

**Second**, the always-on rule files got ruthlessly trimmed. The 381-line cookbook global rule became a **10-line** pointer to an on-demand skill. The skill contains the same checklist, but it's loaded only when invoked — not on every turn. That's a **97% reduction** in per-turn context. The principle that emerged: if content isn't needed on every single turn, it doesn't belong in a rule file. Rules are for one-line directives and pointers. Details live in skills, loaded on demand. Progressive disclosure isn't a nice-to-have; it's a budget constraint.

**Third**, the hybrid judgment model. Not every decision needs an LLM. Most of the conductor main loop is deterministic Python — retry logic, routing, state transitions, event streaming. The LLM is invoked only at **explicit judgment nodes** where a human-like decision is required: "is this finding novel or duplicate?", "which specialist should handle this?", "does this user answer resolve the open question?". Each judgment node carries a prompt template, a response schema, and a list of legal successor states. The conductor invokes the dispatcher, validates the response, and advances the state machine. Everything outside judgment nodes is pure code.

The result, when I finished this rewrite, was a system where I could run the same pipeline I used to run and pay a fraction of the token cost. The conductor itself is free. The rules are tiny. The dispatches are short. The math works again. And it works because the system was designed around the assumption that Claude usage is expensive and has to be rationed. Efficiency isn't an optimization you bolt on at the end. It's the shape of the thing.

### 4.4 Scalable Criteria Dataset — The Cookbook as Vocabulary

**Claim**: a growing corpus of principles, guidelines, and specs must become first-class agent input, not prose embedded in prompts.

The first version of my specialty-team prompts had the checklists inline. "Check the following: contrast ratios must meet WCAG AA for normal text; contrast ratios for large text must be 3:1…" and so on, for forty lines. This worked when I had one checklist. By the time I had twenty, I had copy-pasted content everywhere, and when I updated a guideline, I had to find every prompt that referenced it and update them all.

The cookbook is the answer to that problem. It's a separate corpus of markdown files organized as a three-tier hierarchy. **Ingredients** are atomic specs — "a button component," "a contrast-ratio guideline," "a retry policy." They define requirements, appearance, states, accessibility, test vectors, configuration. **Recipes** compose configured ingredients into features — "a sign-in form" recipes a button ingredient with specific configuration, a text-field ingredient, a password ingredient, and a layout. **Cookbooks** assemble recipes into whole applications.

Specialty-teams reference this corpus by path. A specialty-team file's frontmatter contains an `artifact` field — a path to one cookbook file. The worker agent is given: the artifact, the target (whatever is being checked), and the mode (interview, analysis, generation, or review). The `## Worker Focus` section tells the agent what this specialty-team cares about within the artifact — a mode-independent excerpt, small enough to fit in a short prompt. If the worker needs more than the focus gives it, it reads the artifact via the Read tool — on demand, once, not on every turn.

This is progressive disclosure applied to content. The worker doesn't need to know all 38 items in an accessibility guideline before it starts; it needs the focus for its specific specialty-team ("navigation contrast and focus-visible states"). If it hits something it needs to verify against the broader guideline, it reads the guideline file. This keeps the worker's per-dispatch context cost small and makes the cookbook the canonical source — the single place where "what accessibility means to this system" is defined.

The scaling property is important. Adding a new ingredient doesn't require modifying any specialty-team. Adding a new specialty-team that references it is six files. The cookbook grows without the prompt-writing cost growing with it. The 230-team count isn't a count of 230 independent hand-written prompts; it's 230 template instances pointing at 230 cookbook artifacts. The vocabulary scales linearly in files and stays constant in prompt complexity.

### 4.5 Guardrails — Constraining the Model

**Claim**: assume the LLM will drift unless explicitly constrained at every boundary.

I started the devteam with an optimistic view of LLM agency. I assumed Claude would mostly do the right thing if I asked clearly. I was partially right — Claude usually *tries* to do the right thing — and partially wrong — trying isn't the same as succeeding. Along the way I discovered failure modes that forced me to design defensively at every interface.

The devteam has four load-bearing guardrail mechanisms.

**Schema-validated responses.** Every LLM invocation carries a JSON schema for the expected response shape. The dispatcher passes `--json-schema <path>` to the `claude -p` subprocess, parses the final message, and validates structurally before returning. If the response is malformed — missing required fields, wrong types, off-schema enum values — the dispatcher surfaces the error instead of silently accepting it. This sounds obvious; it is not how you would design it if you're in a hurry. "Just parse whatever the model gives us" is the default, and the default will eventually give you data that makes no sense to whatever consumes it.

**Worker-verifier adversarial pairing.** A specialty-team has two agents, not one. The worker produces findings. The verifier, invoked separately with a different prompt, checks the worker's output against the `## Verify` section of the specialty-team file. Critically, the verifier cannot see the worker's instructions. It only sees the worker's output and its own verification criteria. This matters because if the worker had a weak understanding of its own task, it will produce weak output that rationalizes to itself — and an independent verifier, armed with the spec, can catch that. The verifier returns PASS or FAIL with reasons. The retry loop is Python: if FAIL and iterations < 3, feed the failure reasons back to the worker and retry. After three iterations, escalate to the specialist. The LLM does not decide to retry. Python decides, bounded, deterministically.

**User-facing communication funneled through the team-lead.** Specialists and workers never talk directly to the user. They write structured findings to the arbitrator. The team-lead reads those findings, aggregates them, and produces the final user-facing message. Why? Because workers are narrow and worker prose reflects narrow context. If a worker spoke directly to the user, the user would get twenty-three fragmented narratives with inconsistent voices. The team-lead's job — using one LLM call at a specific judgment node — is to be the voice that owns the session.

**Judgment nodes are enumerated, not ambient.** The team-lead doesn't "decide" whether to consult the LLM; its state machine has explicit judgment nodes, and only those nodes invoke the dispatcher. Between judgment nodes, transitions are pure Python. This means you can read a team-playbook and see exactly where judgment happens. The model never gets the chance to insert extra judgment calls.

The theme across all four: the LLM is treated as a narrow oracle, not as a coworker. You give it a small, specific question. It gives you a small, specific answer, validated at the boundary. Everything else is code.

### 4.6 Clear Tasks — Bounded Work Product

**Claim**: a worker must know exactly what to produce and what success means, without ambient judgment calls.

This driver is closely related to guardrails, but it's not the same thing. Guardrails are about preventing bad outputs. Clear tasks are about defining good outputs so specifically that "bad" becomes a non-question. The first is defensive; the second is generative.

The mechanism is a discipline I call **one artifact, one target, one mode**. Every specialty-team focuses on exactly one cookbook artifact. Not "review the code for accessibility issues" — the artifact is specific, "check this component against the accessibility/contrast-ratios ingredient." Not "review the whole project" — the target is one file, one component, one PR. And the worker runs in exactly one mode at a time: **interview** (extract requirements from the user), **analysis** (assess the current state), **generation** (produce new content), or **review** (verify an existing artifact).

Those four modes are fixed. They're part of the system, not chosen per specialty-team. A specialty-team worker receives (artifact, target, mode) as its three inputs, and its prompt resolves the `## Worker Focus` plus a mode-specific preamble ("you are now in review mode; check this target against the requirements in the artifact's verify section"). The worker never has to decide what kind of work it's doing. The mode is set at dispatch time by the orchestrator.

I can't overstate how much this eliminates. Before this discipline, my workers would sometimes do interview work during generation mode ("let me ask a clarifying question"), sometimes do review work during analysis mode ("I'll go ahead and fix this too"), sometimes just meander. After it, they produce the output their mode demands. When they don't, the verifier catches it. When they do, I get usable structured findings.

The other half of clarity is **manifest-driven execution**. A specialist file explicitly lists its specialty-teams in a `## Manifest` section. The orchestrator reads this manifest and runs them as a deterministic sequence — no filesystem discovery, no "run all the teams in the category," no LLM deciding which teams to skip. If a team isn't in the manifest, it doesn't run. If it's in the manifest, it runs. Nothing is implicit.

Why this matters: every source of runtime ambiguity is a source of drift. If the orchestrator discovers teams from the filesystem, someone might drop in a new team and break the pipeline. If the LLM decides which teams to run, that decision is opaque and unbounded. An explicit manifest is a guarantee. It's also a test surface: if I want to check whether a specialist is doing the right work, I read the manifest. The rest is mechanical.

### 4.7 Avoiding Overwhelm — Context Budget as First-Class Constraint

**Claim**: every input and output must be sized against a context budget, or the system collapses under its own weight.

This driver is the most subtle of the seven because it never causes an explicit error. Nothing ever says "context overflow." Instead, the symptoms are drift, incoherence, dropped instructions, and mysteriously bad output. The model *has* the context — it just can't use it effectively when there's too much. I have come to think of this as the agentic equivalent of working memory limits: beyond some size, additional context doesn't help, it hurts.

The devteam manages this in four ways.

**One-shot dispatcher calls.** A specialty-team worker produces its output in a single LLM invocation. There is no "talk to the user, get a follow-up, iterate" loop inside a worker call. The worker receives all the input it will ever get — artifact, target, mode, focus — and must produce a structured response in one turn. If more information is needed, the verifier fails the output and the retry loop injects the missing context into a fresh worker call. This prevents the slow-motion context accumulation that happens inside multi-turn agent loops.

**Parallel specialists without context merging.** When the conductor needs to run five specialists concurrently, it dispatches them via separate `claude -p` subprocesses. Their outputs don't land in a shared conversation. They land as structured rows in the arbitrator. The team-lead reads those rows and aggregates them in Python. Five parallel specialists cost five parallel dispatches — not a merged context that grows with the sum of their outputs.

**Rule files capped at 200 lines.** Every rule file in `.claude/rules/` is subject to a hard cap: target under 200 lines, ~8KB per file. The cap isn't aesthetic; it's the only way to keep per-turn context costs from ballooning. Rules are for one-line directives and pointers; details belong in on-demand skills. When I enforce this cap across the whole project, the total always-on context stays under a budget I can reason about. When I relax it, I eventually get back into a $600/month month.

**Judgment prompts scoped to one question.** A team-lead judgment node doesn't load "everything the team-lead might need to decide anything." It loads only what's needed for the specific decision: the current state, the user's most recent input, references to findings so far (not the full findings, just pointers). The prompt is typically under 2K tokens. When a decision requires additional context, the team-lead reads it — once, via the Read tool, not as a standing load.

The philosophy across all four: treat context as a scarce resource whose allocation has to be planned. Don't hand the model a pile of stuff and hope for the best. Hand it exactly what it needs for one specific decision, and nothing more. Overwhelm is what happens when you ignore this. The system works when you don't.

---

## 5. Cross-Cutting Tensions and Conflicts

The seven drivers are not always compatible. This section is where I acknowledge the places they pull in different directions — some resolved, some still under debate in my own research notes.

**Team-lead runtime location.** For a long time the devteam assumed the team-lead was a Claude Code conversation — a long-running chat with extensive system prompt and the ability to spawn subagents. Most of my older planning docs still reflect that assumption. The recent conductor pivot moved the team-lead out of the conversation and into a headless Python process: the team-lead is now a state machine running inside the conductor, not a chat. This was the right call — it's what makes the efficiency story in §4.3 work. But the conflict between "team-lead as chat" and "team-lead as FSM" is still visible in the corpus. If you read specs from before the pivot, you'll find references to things the current system doesn't have. If you read newer specs, you'll find things older ones don't describe. I've chosen to move forward with the newer model and retrofit the older docs as they become relevant, rather than freeze everything until every reference is updated.

**Consulting-team obligation.** Consulting teams are technically optional — specialists without a `## Consulting Teams` section work fine. In practice, certain specialists (security is the canonical example) require a consulting team because their decisions cascade through everything else: a security concern found in one specialty-team's output is a concern for every other specialty-team's output too. So the answer to "are consulting teams optional or required?" is "optional by construction, required in specific cases." This looks like a contradiction. It isn't — it's a deliberate trade-off between backwards compatibility (optional) and correctness in the domains that need it (required). I flag it because reading only one half of the design docs will leave you with a wrong mental model.

**Shell vs. Python scripting.** My performance guideline says "use shell scripts for deterministic work — git, build, lint, metrics collection." My global CLAUDE.md says "NEVER write bash/shell scripts; always use Python." Both statements exist in the same repo. Both are technically correct from the perspective of their author (me). The deeper principle — "deterministic work should be scripts, not LLM calls" — is satisfied either way. The tool choice is the open question. For now, new scripts are Python, old shell scripts stay shell, and I have stopped trying to enforce conversion. I'd rather have the principle right and the tool choice ambiguous than have consistent tooling and model-invoked deterministic work.

**Terminology drift.** The research corpus contains both "specialty-team" and "specialty" for the same concept. Both "cookbook" and "concoction" for the same top-level artifact (briefly; the rename was never completed). Different docs give the specialty-team count as 229, 230, or ~252. These are the kinds of conflicts that look like bugs but are actually the normal state of a project that has been iterating for months and has not frozen its vocabulary. I'm flagging them not because they're catastrophic but because if you're reading the research alongside this paper, you'll notice them, and you should know I know.

The honest takeaway is: a system designed for flexibility will, over time, evolve in ways that outrun its documentation. The choice is between freezing the docs (which makes iteration slow) and accepting drift (which makes the docs lossy). I've chosen the second. This paper is my attempt to re-align them.

---

## 6. Lessons Learned

Stepping back from the specific drivers, a few patterns have emerged that I think generalize beyond my project.

**Intelligence at the edges, deterministic plumbing in the middle.** This is the most compact statement of the design philosophy, and it's the one I return to when I'm stuck. The LLM should be invoked where human-like judgment is genuinely needed: at the point of a decision, at the point of generation, at the point of evaluation. Everything else — routing, retry, aggregation, persistence, parallelism — should be code. The mistake I made repeatedly in early versions was letting the LLM own too much of the plumbing, reasoning that "it's smart, it can figure it out." It can, but at ruinous cost. A conventional program that calls the LLM at specific points is cheaper, more predictable, and easier to debug than an LLM-orchestrated program. This isn't about distrusting the LLM; it's about putting it where it pays.

**The FSM decides *that* a decision needs to be made; the LLM decides *what* the decision is.** This is the same lesson as above, phrased as a pattern. State machines are great at determining structure — which steps have to happen, in which order, with what fallbacks. Language models are great at filling in the semantic content — which option to choose, how to phrase the finding, which concern applies. Combining them is better than either alone. A pure FSM can't handle open-ended judgment; a pure LLM can't handle bounded structure. The hybrid is what works, and it generalizes to any system where you need structured orchestration of open-ended work.

**Cookbook-as-vocabulary scales better than ad-hoc prompts.** This one surprised me. I thought the value of the cookbook would be "I only have to write each guideline once." That's true but small. The larger value is that the cookbook becomes the *shared vocabulary* of the system. When two specialty-teams both reference the same ingredient, they have a common definition of what that ingredient means. When the team-lead aggregates their findings, it can reason about them at the ingredient level — not by matching prose. When I want to update how the system thinks about accessibility, I update the ingredient, and every specialty-team that references it is automatically updated. The cookbook is not a knowledge base — it's a type system for agent work.

**Design for deletion.** Every architectural choice should be easy to remove. The dispatcher abstraction is easy to remove — you replace the abstract type with the concrete one. The cookbook is easy to remove — you inline the references. The consulting-team mechanism is easy to remove — you drop the optional section. This discipline has saved me multiple times when I've needed to pivot. The opposite — architecture that's hard to remove — calcifies quickly and takes the whole project down with it.

**Progressive disclosure is a budget constraint, not an aesthetic.** When I started, I thought rule files should contain "everything the agent might need to know." That gives you 400-line rule files that burn through your context budget in a long session. The shift to progressive disclosure — one-line directives in rules, details in on-demand skills — wasn't a stylistic preference. It was the only way to keep long sessions viable. The per-turn cost model is the thing to internalize: if content appears on every turn, it must be tiny. If content can be loaded once, it can be large. Designing to this constraint is what the 97% reduction story is really about.

---

## 7. Open Problems

I don't want to pretend the system is done. Here are the places I'm still stuck.

**Context budgeting holistically.** I know rule files should be under 200 lines. I know judgment prompts should be under 2K tokens. I know specialty-team worker prompts should be under 3K tokens. What I don't know is how to compute the *total* per-turn cost across rules + prompt + agent definition + prior tool results. I don't have a single-number budget for "this turn will cost X tokens of context." That makes it hard to preempt context blowups — I can only catch them after they happen, when performance degrades. I'd love a linter that reports per-turn context cost the way my static analyzer reports complexity.

**LLM portability across vendors.** The dispatcher abstraction exists. I can see how `LocalDispatcher` would work. I have not actually built it. All current testing is against Claude (Opus, Sonnet, Haiku). I don't know whether my prompts would work on an open-source model. I don't know whether the schema validation discipline catches the same classes of drift across vendors. I don't know whether logical model names map cleanly to non-Claude models. Until I build `LocalDispatcher` and run a full pipeline through it, the portability claim is theoretical.

**Multi-user / shared-session orchestration.** The current design assumes one user per conductor. There's no notion of two users sharing a session, or two conductors sharing an arbitrator, or a user's work flowing into another user's inbox. I don't know what the primitives look like. I don't know whether the arbitrator's resource model is rich enough to express "this finding is owned by user A but visible to user B." This matters for anything beyond a solo project.

**Verifier self-verification.** The worker-verifier pattern catches worker drift. It doesn't catch verifier drift. If the verifier has a wrong understanding of the verify criteria, it will cheerfully PASS bad worker output. I currently mitigate this with occasional manual spot-checks, but a more principled answer — meta-verification, verifier testing, verifier schema validation — is an open design problem.

**Graceful handling of cookbook versioning.** Specialty-teams reference cookbook artifacts by path. When I update an artifact, all specialty-teams that reference it automatically pick up the change — usually what I want, sometimes not. I don't yet have a story for "pin this specialty-team to this version of this artifact." When I need it — and I will — I'll have to retrofit.

None of these are blockers. They're places where the system's reach exceeds its current grasp. I expect to hit each of them in the next few months.

---

## 8. Conclusion

The seven drivers aren't orthogonal. They amplify each other. Flexibility without guardrails gives you a system that can run anywhere but produces garbage everywhere. Guardrails without clear tasks gives you a system that constrains garbage without improving it. Efficiency without a scalable criteria dataset gives you a cheap system that can't grow. Miss any one and the others lose half their value.

That interdependence is the deeper claim of this paper. Building an autonomous multi-agent development system is not primarily a prompt-engineering problem. It's an architecture problem, and the architecture has to be shaped around a small number of constraints that I don't think are specific to my project: the LLM drifts unless constrained, the context budget is scarce, the criteria dataset needs shared vocabulary, and the orchestration has to be code while the judgment is the model.

If you take away one thing from this paper, take this: building agentic systems is less about writing better prompts than it is about designing constraints and vocabulary. The prompts are the surface. The constraints are what keep them from unraveling. The vocabulary is what makes them coherent across many agents.

The devteam is a work in progress. I expect to pivot again before the year is out — probably more than once. But the seven drivers, and the patterns they've produced, feel stable in a way that my specific mechanisms don't. I can imagine the dispatcher abstraction being replaced, the arbitrator being rewritten, the cookbook being reorganized. I can't imagine the drivers themselves going away. They are, I think, a small enough set to remember and a large enough set to be load-bearing. I commend them to anyone else trying to build something similar.
