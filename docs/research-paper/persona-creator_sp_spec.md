# persona-creator — Design Spec

**Date**: 2026-04-08
**Status**: Draft
**Author**: Mike Fullerton + Claude

## Overview

A Python library and Claude Code skill for generating AI personas. Takes minimal seed input (name, role, personality hints) and produces a fully fleshed-out persona using LLM-assisted generation. Outputs markdown files and JSON, compatible with the official-agent-registry and internal projects (dev-team, temporal).

## Goals

- Generate personas at three tiers: Full, Lightweight, Specialist
- Encode persona design research (from cookbook and official-agent-registry) into reusable generation prompts
- Produce both markdown (with YAML frontmatter) and JSON output
- Work as a standalone library and as a Claude Code skill
- Serve agent builders and internal projects equally

## Non-Goals

- No direct registry API integration (output-compatible only)
- No persona management (listing, updating, deleting)
- No database, server, or web UI
- No LLM provider lock-in — the library produces prompts, callers send them

## Persona Tiers

### Full Persona

Based on `official-agent-registry/docs/research/ai-persona-template.md`. For ongoing user-facing agents with emotional range and growth arcs. 14 sections:

1. **Identity** — narrative prose (1-3 paragraphs)
2. **Purpose** — functional role (1-3 sentences)
3. **Desire** — deeper driving motivation
4. **Backstory** — origin story, inspiration, formative experiences
5. **Values & Beliefs** — 3-7 core stable values
6. **Personality Traits** — 8-15 behavioral attributes with "as persona" notes
7. **Contradictions & Complexity** — 2-5 internal tensions
8. **Emotional Range** — emotion/intensity/when/how table
9. **Flaws & Limitations** — 2-5 genuine weaknesses flowing from strengths
10. **Voice & Communication** — tone, vocabulary, rhythm, signature moves, adaptations
11. **Relationship Model** — posture, power dynamic, trust arc, boundaries
12. **Growth Arc** — early, middle, mature stages
13. **Anti-Patterns** — explicit "what this character is NOT"
14. **Sample Interactions** — 2-4 representative exchanges

Reference implementation: Charlie (`temporal/docs/personas/charlie.md`).

### Lightweight Persona

Based on the quick recipe from `official-agent-registry/docs/research/ai-persona-research.md`. For task-specific AI roles. 7 sections:

1. **Identity** — name, personality adjectives, role, background (one sentence)
2. **Personality** — traits with why they matter for output
3. **Focus Areas** — domain concerns
4. **Communication** — tone, signature phrases, flagging style
5. **Output Format** — structured steps
6. **Constraints** — what they don't do
7. **Sample Interaction** — one representative exchange

Reference implementation: Biff (`cookbook/appendix/research/developer-tools/claude/claude-persona-prompting.md`).

### Specialist Persona

Based on the dev-team specialist format from `dev-team/docs/research/persona-design.md`. For pipeline specialists that interact through structured workflows, not direct user conversation. 4 sections:

1. **Archetype** — one-sentence identity
2. **Voice** — 2-4 sentences on communication style
3. **Priorities** — 2-4 sentences framed as trade-off preferences
4. **Anti-Patterns** — table of label + description

Reference implementations: dev-team specialists (`dev-team/plugins/dev-team/specialists/`).

## Architecture

### Library Structure

```
persona_creator/
    __init__.py
    models.py          — dataclasses for all three tiers + shared metadata
    generator.py       — builds LLM prompts from seed input, parses responses
    serializers.py     — to_markdown(), to_json(), from_markdown(), from_json()
    prompts/
        full.md        — generation prompt template for full personas
        lightweight.md — generation prompt template for lightweight personas
        specialist.md  — generation prompt template for specialist personas
```

### models.py

Shared metadata envelope used by all tiers:

```python
@dataclass
class PersonaMetadata:
    name: str
    tier: Literal["full", "lightweight", "specialist"]
    version: str = "1.0.0"
    status: str = "draft"
    created: str = ""   # ISO date, set at creation
    modified: str = ""  # ISO date, set at creation/update
    author: str = ""
```

Each tier is a dataclass containing `metadata` plus tier-specific fields. Fields mirror the section structures described above. Lists of structured items (traits, values, anti-patterns, etc.) use nested dataclasses.

### generator.py

The generator's job is to produce a prompt string, not to call an LLM.

```python
def generate_prompt(seed: PersonaSeed, tier: str) -> str:
    """Build an LLM generation prompt from seed input and tier template."""
```

`PersonaSeed` is a simple dataclass:

```python
@dataclass
class PersonaSeed:
    name: str
    role: str           # what the persona does
    hints: list[str]    # 2-3 personality hints from the user
    domain: str = ""    # optional domain context
```

The generation prompts (in `prompts/`) encode the research principles:
- Persona serves function — traits shape output quality, not just tone
- Explicit non-behaviors are more effective than always-do rules
- Voice = rhythm + register, not just "be direct"
- Archetype grounds the voice — one concrete identity produces better consistency
- Sample interactions show the model the exact register to hit

Each prompt template takes the seed input and instructs the LLM to produce a structured response that can be parsed into the tier's dataclass.

### serializers.py

Four functions:

- `to_markdown(persona) -> str` — produces markdown matching existing file formats (YAML frontmatter + headed sections). Full personas match `ai-persona-template.md` format. Lightweight personas match the quick recipe format. Specialist personas match the dev-team specialist format.
- `to_json(persona) -> dict` — produces JSON. For the registry, maps to the `config.persona` shape. For other uses, a full structured representation.
- `from_markdown(text) -> Persona` — parses an existing persona markdown file into the model.
- `from_json(data) -> Persona` — parses JSON into the model.

### LLM Response Parsing

The generation prompts instruct the LLM to output structured sections with clear delimiters. `generator.py` includes a `parse_response(text, tier) -> Persona` function that extracts sections from the LLM output and constructs the appropriate dataclass. This is deliberately simple string parsing — no complex grammar, just heading-based section extraction.

## Claude Code Skill

Installed as `/create-persona`. The skill:

1. **Asks one question**: name, role, and tier choice (via AskUserQuestion)
2. **Asks one more**: 2-3 personality hints — adjectives, inspirations, or behavioral notes
3. **Generates**: builds the prompt using the library, then uses the LLM (which is the skill's own Claude context) to produce the persona
4. **Presents**: shows the generated persona to the user
5. **Iterates**: user can request changes (the skill regenerates or edits specific sections)
6. **Writes**: saves the final persona as a markdown file in the current project

The skill imports the library's models and serializers but doesn't call `generate_prompt` in the typical sense — since the skill *is* an LLM conversation, it embeds the generation principles directly in its own instructions and produces output that maps to the library's models.

## Output Formats

### Markdown

Matches existing conventions:

```yaml
---
name: Charlie
archetype: "The Body Man"
tier: full
version: 1.0.0
status: draft
created: 2026-04-08
modified: 2026-04-08
author: Mike Fullerton
---
```

Followed by headed sections matching the tier's structure. Full personas use `##` headings and `###` subheadings per `ai-persona-template.md`. Lightweight personas use the quick recipe format. Specialist personas use the dev-team specialist format.

### JSON

```json
{
  "metadata": {
    "name": "Charlie",
    "tier": "full",
    "version": "1.0.0",
    "status": "draft",
    "created": "2026-04-08",
    "modified": "2026-04-08",
    "author": "Mike Fullerton"
  },
  "identity": "...",
  "purpose": "...",
  "values": [
    {"name": "Reliability over brilliance", "description": "..."}
  ],
  ...
}
```

For registry compatibility, `to_json()` can also produce the minimal `config.persona` shape:

```json
{
  "persona": {
    "personality": "...",
    "backstory": "...",
    "interests": ["...", "..."]
  }
}
```

## Dependencies

- Python 3.11+
- `pyyaml` — for frontmatter parsing/generation
- `dataclasses` (stdlib)
- `json` (stdlib)
- No LLM SDK dependency — the library produces prompt strings

## Testing

- Unit tests for models (construction, validation)
- Unit tests for serializers (round-trip: model -> markdown -> model, model -> json -> model)
- Unit tests for prompt generation (correct template interpolation)
- Unit tests for response parsing (structured text -> model)
- Integration test: seed -> prompt -> (mock LLM response) -> model -> markdown -> model round-trip

## File Inventory

Files to create:

| File | Purpose |
|------|---------|
| `persona_creator/__init__.py` | Package init, public API exports |
| `persona_creator/models.py` | Dataclasses for all tiers + metadata + seed |
| `persona_creator/generator.py` | Prompt building + response parsing |
| `persona_creator/serializers.py` | Markdown and JSON serialization |
| `persona_creator/prompts/full.md` | Full persona generation prompt template |
| `persona_creator/prompts/lightweight.md` | Lightweight generation prompt template |
| `persona_creator/prompts/specialist.md` | Specialist generation prompt template |
| `tests/test_models.py` | Model unit tests |
| `tests/test_serializers.py` | Serializer round-trip tests |
| `tests/test_generator.py` | Prompt generation + response parsing tests |
| `pyproject.toml` | Package configuration |
| `skill/SKILL.md` | Claude Code skill definition |
| `skill/references/` | Skill reference files (research excerpts, examples) |

Files to update:

| File | Change |
|------|--------|
| `README.md` | Project description, usage, installation |
| `.claude/CLAUDE.md` | Tech stack, build commands, architecture |
| `.gitignore` | Python patterns (__pycache__, .egg-info, etc.) |
| `docs/project/description.md` | Updated project description |
