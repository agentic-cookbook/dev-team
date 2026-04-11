---
title: "AI Persona Design — Research"
type: research
status: complete
created: 2026-04-02
modified: 2026-04-05
summary: "Generalized research on designing AI personas for LLM-powered products. Covers prompting techniques, structural ingredients, adaptation for different scales, and key principles."
tags: [persona, research, ai, prompting]
---

# AI Persona Design Research

*April 2026*

---

## What Makes a Great Persona

The best approach is to use the **system prompt** to define the character's personality, background, and specific traits — this sets a strong foundation for consistent responses. You can also prepare the model for common scenarios and expected responses to "train" it in-session.

Be detailed and specific: provide background, personality traits, and priorities for the role. If the persona should only respond in certain ways, include that explicitly.

> Modern Claude models are sophisticated enough that heavy-handed role prompting is often unnecessary. Being explicit about the *perspective* you want is often more effective than an elaborate character setup. The best personas work because their traits directly shape output *quality*, not just tone.

### Key Structural Ingredients

1. **Who they are** — name, background, vibe
2. **What they care about** — values, obsessions, standards
3. **How they communicate** — tone, quirks, vocabulary
4. **What they won't do** — constraints that keep them useful
5. **A sample interaction** — shows the model the target behavior

---

## Key Principles

| Principle | What it means |
|---|---|
| Persona serves function | Traits should shape output quality, not just tone. Curiosity forces better questions; thoroughness forces better coverage. |
| Constrained output format | Structured sections produce consistent, scannable output |
| Explicit non-behaviors | Listing what the persona *never* does is more effective than listing what it *always* does. Anti-patterns catch the most common failure modes. |
| Sample interaction | Shows the model the exact register and rhythm to hit |
| Emotional tone as a feature | Tone choices (affability, restraint, directness) make functional differences in how output lands |

---

## Insights from Charlie (Full Persona)

These insights emerged from building the full Charlie persona for the Temporal project:

1. **Persona is character, not knowledge.** Domain expertise comes from the role definition. The persona defines *how* the character communicates, not *what* it knows.

2. **Archetype grounds the voice.** A one-sentence identity (e.g., "President's personal aide who anticipates everything") gives the LLM a concrete character to inhabit, which produces more consistent output than abstract tone instructions.

3. **Priorities reveal trade-offs.** Every domain has competing goods. The persona's priorities tell the character what to optimize for when it can't have everything — the most useful guidance in ambiguous situations.

4. **Anti-patterns prevent drift.** Listing what the character *never* does catches failure modes before they happen.

5. **Voice is rhythm + register.** "Be direct" isn't enough. Specify sentence length, vocabulary preferences, and what the character avoids (jargon, hedging, filler).

---

## Full vs. Lightweight Personas

A full persona (like Charlie) has 14+ qualities, emotional range, growth arcs, contradictions, and sample interactions. Lightweight personas (like task-specific specialists) need much less:

| Full Persona Section | Lightweight Equivalent | Notes |
|---|---|---|
| Identity + Backstory | Archetype (1 sentence) | No backstory needed — archetype is enough |
| Voice & Communication | Voice (2-4 sentences) | Brief style guides work well |
| Values & Beliefs | Priorities (2-4 sentences) | Frame as trade-off preferences, not abstract values |
| Anti-Patterns | Anti-Patterns (table) | Optional but highly effective |
| Emotional Range | Not needed | Specialists don't have emotional arcs |
| Growth Arc | Not needed | Specialists are static characters |
| Relationship Model | Not needed | Only needed for ongoing user-facing personas |

---

## Quick Recipe: Lightweight Persona

```
You are [NAME], a [PERSONALITY ADJECTIVES] [ROLE] with [BACKGROUND].

## Personality
- [trait 1 + why it matters for the output]
- [trait 2 + why it matters for the output]

## What you focus on
- [domain concern 1]
- [domain concern 2]

## How you communicate
- [tone]
- [signature phrases]
- [what you flag and how]

## Output format
1. [step 1]
2. [step 2]
3. [closing move]

## What you don't do
- [constraint 1]
- [constraint 2]

## Sample interaction
User: [representative input]
[NAME]: [ideal response showing voice + format]
```

---

## Example: Biff (iOS Code Reviewer)

A worked example showing these principles in action.

**Archetype**: Warm, enthusiastic iOS code reviewer with 15 years of Swift/Obj-C. Worked at a scrappy startup acquired by Apple — deep platform respect without stuffiness.

**Key traits**:
- Genuinely curious — understands *why* before suggesting changes
- Affable — opens every review with something genuine they liked
- Thorough — traces data flow, checks edge cases, looks at call sites
- Asks before declaring: "Hey, was this intentional or did this slip in?"

**Voice**: Conversational, never condescending. "I'm curious about...", "One thing I'd love to understand...", "This is totally fine, but I wonder if..."

**Anti-patterns**: Never rewrites the entire function unprompted. Doesn't nitpick naming unless genuinely confusing. Max 3 major points per review.

**Closing move**: Vibe check — "Ship it", "Almost there", or "Let's talk before this merges."

---

## Reference Links

| Resource | Description |
|---|---|
| Anthropic — Keep Claude in character | Role prompting techniques |
| Anthropic — Prompting best practices (Claude 4.x) | General prompt engineering |
| Anthropic — Prompt engineering overview | Foundation concepts |

---

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-04-05 | Mike Fullerton | Consolidated from agentic-cookbook research files |
