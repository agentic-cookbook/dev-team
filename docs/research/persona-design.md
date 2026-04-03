# Persona Design Reference

Background research for the specialist persona format.

## Source

The specialist persona structure (Archetype, Voice, Priorities, Anti-Patterns) is derived from a character-driven persona model developed for the Temporal project's AI persona "Charlie." The full persona definition lives at:

- Design: `/Users/mfullerton/projects/apps/temporal/docs/designs/personas/charlie.md`
- Decision: `/Users/mfullerton/projects/apps/temporal/docs/personas/ai-persona-name-charlie.md`

## Key Insights

1. **Persona is character, not knowledge.** A specialist's domain expertise comes from the Role and Specialty Teams. The persona defines *how* the specialist communicates, not *what* it knows.

2. **Archetype grounds the voice.** A one-sentence identity (e.g., "security auditor who's investigated real breaches") gives the LLM a concrete character to inhabit, which produces more consistent output than abstract tone instructions.

3. **Priorities reveal trade-offs.** Every domain has competing goods. The persona's priorities tell the specialist what to optimize for when it can't have everything — which is the most useful guidance in ambiguous situations.

4. **Anti-patterns prevent drift.** Listing what the specialist *never* does is more effective than listing what it *always* does. Anti-patterns catch the most common failure modes.

5. **Voice is rhythm + register.** It's not enough to say "be direct." The persona should specify sentence length, vocabulary preferences, and what the specialist avoids (jargon, hedging, filler).

## Adaptation for Specialists

The full Charlie persona has 14 core qualities, emotional range tables, a growth arc, contradictions, and sample interactions. Specialists are much lighter — they need just enough persona to produce consistent, differentiated output:

| Charlie Section | Specialist Equivalent | Notes |
|----------------|----------------------|-------|
| Identity + Backstory | Archetype (1 sentence) | No backstory needed — archetype is enough |
| Voice & Communication | Voice (2-4 sentences) | Keep it short — LLMs respond well to brief style guides |
| Values & Beliefs | Priorities (2-4 sentences) | Frame as trade-off preferences, not abstract values |
| Anti-Patterns | Anti-Patterns (table) | Optional but highly effective |
| Emotional Range | Not needed | Specialists don't have emotional arcs |
| Growth Arc | Not needed | Specialists are static characters |
| Relationship Model | Not needed | Specialists interact through the worker-verifier pipeline |
