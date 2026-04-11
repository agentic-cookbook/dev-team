# persona-creator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python library and Claude Code skill that generates AI personas from minimal seed input, outputting markdown and JSON at three tiers (full, lightweight, specialist).

**Architecture:** Dataclass models define persona structure for each tier. Serializers convert between models and markdown/JSON. A generator builds LLM prompts from seed input and parses LLM responses back into models. A Claude Code skill wraps the flow interactively.

**Tech Stack:** Python 3.11+, PyYAML, pytest, dataclasses (stdlib)

**Spec:** `docs/superpowers/specs/2026-04-08-persona-creator-design.md`

---

## File Structure

```
persona_creator/
    __init__.py            — public API: models, serializers, generator
    models.py              — dataclasses for all 3 tiers + metadata + seed
    serializers.py         — to_markdown, from_markdown, to_json, from_json
    generator.py           — generate_prompt, parse_response
    prompts/
        __init__.py        — empty, makes prompts a package for importlib.resources
        full.md            — LLM prompt template for full persona generation
        lightweight.md     — LLM prompt template for lightweight persona generation
        specialist.md      — LLM prompt template for specialist persona generation
tests/
    __init__.py
    conftest.py            — pytest fixtures: sample personas for each tier
    test_models.py         — model construction tests
    test_serializers.py    — round-trip serialization tests
    test_generator.py      — prompt generation + response parsing tests
skill/
    SKILL.md               — Claude Code skill definition for /create-persona
    references/
        persona-research.md — excerpt of design principles for skill context
pyproject.toml             — package config, dependencies, pytest config
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `persona_creator/__init__.py`
- Create: `persona_creator/prompts/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Modify: `.gitignore`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "persona-creator"
version = "0.1.0"
description = "Generate AI personas from minimal seed input"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.setuptools.packages.find]
include = ["persona_creator*"]
```

- [ ] **Step 2: Create package init files**

`persona_creator/__init__.py`:
```python
"""persona-creator: Generate AI personas from minimal seed input."""
```

`persona_creator/prompts/__init__.py`:
```python
```

`tests/__init__.py`:
```python
```

`tests/conftest.py`:
```python
"""Shared test fixtures for persona-creator tests."""
```

- [ ] **Step 3: Update .gitignore**

Append Python patterns to the existing `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
*.egg
.pytest_cache/
.venv/
venv/
```

- [ ] **Step 4: Install the package in dev mode**

Run: `cd ~/projects/active/persona-creator && python3 -m pip install -e ".[dev]"`
Expected: Successfully installed persona-creator and dependencies

- [ ] **Step 5: Verify pytest runs**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest --co -q`
Expected: `no tests ran` (no test files yet, but pytest itself works)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml persona_creator/__init__.py persona_creator/prompts/__init__.py tests/__init__.py tests/conftest.py .gitignore
git commit -m "Project scaffolding: pyproject.toml, package structure, .gitignore"
git push
```

---

### Task 2: Models

**Files:**
- Create: `persona_creator/models.py`
- Create: `tests/test_models.py`
- Modify: `tests/conftest.py`
- Modify: `persona_creator/__init__.py`

- [ ] **Step 1: Write model tests**

`tests/test_models.py`:
```python
"""Tests for persona model construction and field access."""

from persona_creator.models import (
    AntiPattern,
    Contradiction,
    Emotion,
    Flaw,
    FullPersona,
    GrowthArc,
    LightweightPersona,
    PersonaMetadata,
    PersonaSeed,
    PersonalityTrait,
    RelationshipModel,
    SampleInteraction,
    SpecialistPersona,
    Value,
    Voice,
    VoiceAdaptation,
    Trait,
)


def test_persona_seed():
    seed = PersonaSeed(name="Biff", role="iOS code reviewer", hints=["warm", "thorough"])
    assert seed.name == "Biff"
    assert seed.role == "iOS code reviewer"
    assert seed.hints == ["warm", "thorough"]
    assert seed.domain == ""


def test_full_persona(full_persona):
    assert full_persona.metadata.name == "TestBot"
    assert full_persona.metadata.tier == "full"
    assert full_persona.identity != ""
    assert len(full_persona.values) == 2
    assert len(full_persona.traits) == 2
    assert len(full_persona.contradictions) == 1
    assert len(full_persona.emotional_range) == 2
    assert len(full_persona.flaws) == 1
    assert full_persona.voice.tone != ""
    assert len(full_persona.voice.adaptations) == 1
    assert full_persona.relationship_model.posture != ""
    assert full_persona.growth_arc.early != ""
    assert len(full_persona.anti_patterns) == 2
    assert len(full_persona.sample_interactions) == 1


def test_lightweight_persona(lightweight_persona):
    assert lightweight_persona.metadata.name == "ReviewBot"
    assert lightweight_persona.metadata.tier == "lightweight"
    assert lightweight_persona.identity != ""
    assert len(lightweight_persona.personality) == 2
    assert len(lightweight_persona.focus_areas) == 2
    assert lightweight_persona.communication.tone != ""
    assert len(lightweight_persona.output_format) == 2
    assert len(lightweight_persona.constraints) == 2
    assert lightweight_persona.sample_interaction.scenario != ""


def test_specialist_persona(specialist_persona):
    assert specialist_persona.metadata.name == "SecuritySpec"
    assert specialist_persona.metadata.tier == "specialist"
    assert specialist_persona.archetype != ""
    assert specialist_persona.voice != ""
    assert specialist_persona.priorities != ""
    assert len(specialist_persona.anti_patterns) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_creator.models'`

- [ ] **Step 3: Write models.py**

`persona_creator/models.py`:
```python
"""Persona data models for all three tiers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


# --- Shared types ---


@dataclass
class PersonaMetadata:
    """Shared metadata envelope for all persona tiers."""

    name: str
    tier: Literal["full", "lightweight", "specialist"]
    version: str = "1.0.0"
    status: str = "draft"
    created: str = ""
    modified: str = ""
    author: str = ""


@dataclass
class PersonaSeed:
    """Minimal input for generating a persona."""

    name: str
    role: str
    hints: list[str] = field(default_factory=list)
    domain: str = ""


@dataclass
class AntiPattern:
    label: str
    description: str


@dataclass
class SampleInteraction:
    scenario: str
    user_input: str
    response: str


# --- Full persona types ---


@dataclass
class Value:
    name: str
    description: str


@dataclass
class Trait:
    name: str
    description: str
    as_persona: str


@dataclass
class Contradiction:
    trait_a: str
    trait_b: str
    description: str


@dataclass
class Emotion:
    emotion: str
    intensity: str
    when: str
    how: str


@dataclass
class Flaw:
    name: str
    manifests: str
    why: str


@dataclass
class VoiceAdaptation:
    context: str
    tone_shift: str
    example: str


@dataclass
class Voice:
    tone: str
    vocabulary: str
    rhythm: str
    signature_moves: str
    adaptations: list[VoiceAdaptation] = field(default_factory=list)


@dataclass
class RelationshipModel:
    posture: str
    power_dynamic: str
    trust_arc: str
    boundaries: str


@dataclass
class GrowthArc:
    early: str
    middle: str
    mature: str


@dataclass
class FullPersona:
    metadata: PersonaMetadata
    archetype: str
    identity: str
    purpose: str
    desire: str
    backstory: str
    values: list[Value] = field(default_factory=list)
    traits: list[Trait] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    emotional_range: list[Emotion] = field(default_factory=list)
    flaws: list[Flaw] = field(default_factory=list)
    voice: Voice = field(default_factory=lambda: Voice("", "", "", ""))
    relationship_model: RelationshipModel = field(
        default_factory=lambda: RelationshipModel("", "", "", "")
    )
    growth_arc: GrowthArc = field(default_factory=lambda: GrowthArc("", "", ""))
    anti_patterns: list[AntiPattern] = field(default_factory=list)
    sample_interactions: list[SampleInteraction] = field(default_factory=list)


# --- Lightweight persona types ---


@dataclass
class PersonalityTrait:
    trait: str
    why_it_matters: str


@dataclass
class LightweightVoice:
    tone: str
    phrases: str
    flagging_style: str


@dataclass
class LightweightPersona:
    metadata: PersonaMetadata
    identity: str
    personality: list[PersonalityTrait] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    communication: LightweightVoice = field(
        default_factory=lambda: LightweightVoice("", "", "")
    )
    output_format: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    sample_interaction: SampleInteraction = field(
        default_factory=lambda: SampleInteraction("", "", "")
    )


# --- Specialist persona ---


@dataclass
class SpecialistPersona:
    metadata: PersonaMetadata
    archetype: str
    voice: str
    priorities: str
    anti_patterns: list[AntiPattern] = field(default_factory=list)


# --- Type alias ---

Persona = FullPersona | LightweightPersona | SpecialistPersona
```

- [ ] **Step 4: Write test fixtures in conftest.py**

`tests/conftest.py`:
```python
"""Shared test fixtures for persona-creator tests."""

import pytest

from persona_creator.models import (
    AntiPattern,
    Contradiction,
    Emotion,
    Flaw,
    FullPersona,
    GrowthArc,
    LightweightPersona,
    LightweightVoice,
    PersonaMetadata,
    PersonalityTrait,
    RelationshipModel,
    SampleInteraction,
    SpecialistPersona,
    Value,
    Voice,
    VoiceAdaptation,
    Trait,
)


@pytest.fixture
def full_persona() -> FullPersona:
    return FullPersona(
        metadata=PersonaMetadata(
            name="TestBot",
            tier="full",
            version="1.0.0",
            status="draft",
            created="2026-04-08",
            modified="2026-04-08",
            author="Test Author",
        ),
        archetype="The Helpful Assistant",
        identity=(
            "TestBot is a calm, reliable presence. Always ready to help "
            "without being asked, never overstepping."
        ),
        purpose="Assist users with daily task management and planning.",
        desire=(
            "To be genuinely useful. Not to impress, but to remove friction "
            "from people's days."
        ),
        backstory=(
            "TestBot grew out of a need for a consistent, trustworthy helper. "
            "Built by someone who was tired of tools that tried too hard."
        ),
        values=[
            Value(
                name="Reliability over cleverness",
                description="Consistent helpfulness beats occasional brilliance.",
            ),
            Value(
                name="Respect for time",
                description="Never waste the user's attention on things that don't matter.",
            ),
        ],
        traits=[
            Trait(
                name="Anticipation",
                description="Notices patterns and surfaces relevant info proactively.",
                as_persona="Offers reminders and suggestions before being asked.",
            ),
            Trait(
                name="Brevity",
                description="Says what needs saying and stops.",
                as_persona="Short responses by default. Expands only when asked.",
            ),
        ],
        contradictions=[
            Contradiction(
                trait_a="Proactive",
                trait_b="Restrained",
                description=(
                    "Sees what's needed but waits for the right moment. "
                    "Sometimes waits too long."
                ),
            ),
        ],
        emotional_range=[
            Emotion(
                emotion="Satisfaction",
                intensity="low",
                when="A task resolves cleanly",
                how="Brief acknowledgment: 'Done.'",
            ),
            Emotion(
                emotion="Concern",
                intensity="moderate",
                when="User is overcommitted",
                how="Direct flagging without judgment.",
            ),
        ],
        flaws=[
            Flaw(
                name="Over-restraint",
                manifests="Responds with measured acknowledgment when enthusiasm is warranted.",
                why="Shadow side of emotional discipline.",
            ),
        ],
        voice=Voice(
            tone="Warm but not effusive. Direct but not blunt.",
            vocabulary="Plain language. Short words over long ones. No corporate speak.",
            rhythm="Short sentences. Comfortable with fragments. 1-3 sentence paragraphs.",
            signature_moves="Leads with the answer. Names the thing. Calibrated acknowledgment.",
            adaptations=[
                VoiceAdaptation(
                    context="User is stressed",
                    tone_shift="Calmer, reduced info density",
                    example="Let's just handle the next thing.",
                ),
            ],
        ),
        relationship_model=RelationshipModel(
            posture="Treats you as a capable person having a busy day.",
            power_dynamic="Aide, not peer or subordinate. Defers on your decisions.",
            trust_arc="Starts measured, grows anticipatory, becomes shorthand.",
            boundaries="Won't make your decisions. Won't pretend emotions.",
        ),
        growth_arc=GrowthArc(
            early="Competent but generic. Helpful for anyone.",
            middle="Learns your patterns. Starts anticipating.",
            mature="External memory. Minimal words, deep alignment.",
        ),
        anti_patterns=[
            AntiPattern(
                label="Not a cheerleader",
                description="No unearned praise. No 'Great job!' unless specific and earned.",
            ),
            AntiPattern(
                label="Not chatty",
                description="Doesn't fill space. One-word answers are fine.",
            ),
        ],
        sample_interactions=[
            SampleInteraction(
                scenario="Routine check-in",
                user_input="What's today look like?",
                response=(
                    "Three meetings, one deadline. The proposal draft is the "
                    "priority — block this afternoon for it."
                ),
            ),
        ],
    )


@pytest.fixture
def lightweight_persona() -> LightweightPersona:
    return LightweightPersona(
        metadata=PersonaMetadata(
            name="ReviewBot",
            tier="lightweight",
            version="1.0.0",
            status="draft",
            created="2026-04-08",
            modified="2026-04-08",
            author="Test Author",
        ),
        identity=(
            "You are ReviewBot, a thorough and encouraging code reviewer "
            "with a background in full-stack development."
        ),
        personality=[
            PersonalityTrait(
                trait="Genuinely curious",
                why_it_matters="Asks why before suggesting changes, producing better feedback.",
            ),
            PersonalityTrait(
                trait="Encouraging",
                why_it_matters="Opens every review with something genuine, making tough feedback land.",
            ),
        ],
        focus_areas=[
            "Code correctness and edge cases",
            "API contract clarity",
        ],
        communication=LightweightVoice(
            tone="Conversational, never condescending.",
            phrases="'I'm curious about...', 'One thing I noticed...'",
            flagging_style="Clear but undramatic: 'Heads up — this could be a problem.'",
        ),
        output_format=[
            "Open with one genuine compliment",
            "List observations grouped by severity",
        ],
        constraints=[
            "Never rewrite the entire function unprompted",
            "Max 3 major points per review",
        ],
        sample_interaction=SampleInteraction(
            scenario="Code review",
            user_input="Review this function that processes user input.",
            response=(
                "Nice clean separation here. One thing: the input isn't "
                "sanitized before the DB call. Heads up — that's an injection "
                "vector. Overall: almost there."
            ),
        ),
    )


@pytest.fixture
def specialist_persona() -> SpecialistPersona:
    return SpecialistPersona(
        metadata=PersonaMetadata(
            name="SecuritySpec",
            tier="specialist",
            version="1.0.0",
            status="draft",
            created="2026-04-08",
            modified="2026-04-08",
            author="Test Author",
        ),
        archetype=(
            "Security auditor who has investigated real breaches and knows "
            "what actually gets exploited versus what's theoretical."
        ),
        voice=(
            "Direct and specific. Names the exact vulnerability, not vague "
            "warnings. Uses 'this will be exploited' not 'this could be a risk.' "
            "Short sentences. No hedging."
        ),
        priorities=(
            "Exploitability over theoretical purity. A real injection vector "
            "matters more than a missing CSP header. Fix what attackers actually "
            "target first."
        ),
        anti_patterns=[
            AntiPattern(
                label="Security theater",
                description="Don't recommend controls that look good but don't stop real attacks.",
            ),
            AntiPattern(
                label="Exhaustive checklists",
                description="Don't dump 50 findings. Prioritize the 3 that matter.",
            ),
        ],
    )
```

- [ ] **Step 5: Update __init__.py with public exports**

`persona_creator/__init__.py`:
```python
"""persona-creator: Generate AI personas from minimal seed input."""

from persona_creator.models import (
    AntiPattern,
    Contradiction,
    Emotion,
    Flaw,
    FullPersona,
    GrowthArc,
    LightweightPersona,
    LightweightVoice,
    Persona,
    PersonaMetadata,
    PersonalityTrait,
    PersonaSeed,
    RelationshipModel,
    SampleInteraction,
    SpecialistPersona,
    Trait,
    Value,
    Voice,
    VoiceAdaptation,
)

__all__ = [
    "AntiPattern",
    "Contradiction",
    "Emotion",
    "Flaw",
    "FullPersona",
    "GrowthArc",
    "LightweightPersona",
    "LightweightVoice",
    "Persona",
    "PersonaMetadata",
    "PersonalityTrait",
    "PersonaSeed",
    "RelationshipModel",
    "SampleInteraction",
    "SpecialistPersona",
    "Trait",
    "Value",
    "Voice",
    "VoiceAdaptation",
]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_models.py -v`
Expected: 4 tests PASS

- [ ] **Step 7: Commit**

```bash
git add persona_creator/models.py persona_creator/__init__.py tests/test_models.py tests/conftest.py
git commit -m "Add persona models: dataclasses for full, lightweight, specialist tiers"
git push
```

---

### Task 3: Markdown Serializer — to_markdown

**Files:**
- Create: `persona_creator/serializers.py`
- Create: `tests/test_serializers.py`

- [ ] **Step 1: Write to_markdown tests**

`tests/test_serializers.py`:
```python
"""Tests for persona serialization (markdown and JSON)."""

from persona_creator.models import FullPersona, LightweightPersona, SpecialistPersona
from persona_creator.serializers import to_markdown


class TestToMarkdownFull:
    def test_has_yaml_frontmatter(self, full_persona):
        md = to_markdown(full_persona)
        assert md.startswith("---\n")
        assert "\nname: TestBot\n" in md
        assert "\ntier: full\n" in md
        assert "\narchetype: The Helpful Assistant\n" in md

    def test_has_all_sections(self, full_persona):
        md = to_markdown(full_persona)
        assert "\n## Identity\n" in md
        assert "\n## Purpose & Desire\n" in md
        assert "\n## Backstory\n" in md
        assert "\n## Values & Beliefs\n" in md
        assert "\n## Personality Traits\n" in md
        assert "\n## Contradictions & Complexity\n" in md
        assert "\n## Emotional Range\n" in md
        assert "\n## Flaws & Limitations\n" in md
        assert "\n## Voice & Communication\n" in md
        assert "\n## Relationship Model\n" in md
        assert "\n## Growth Arc\n" in md
        assert "\n## Anti-Patterns\n" in md
        assert "\n## Sample Interactions\n" in md

    def test_values_formatted_as_bold_list(self, full_persona):
        md = to_markdown(full_persona)
        assert "- **Reliability over cleverness**:" in md

    def test_traits_have_as_persona(self, full_persona):
        md = to_markdown(full_persona)
        assert "### Anticipation\n" in md
        assert "**As persona**:" in md

    def test_emotional_range_is_table(self, full_persona):
        md = to_markdown(full_persona)
        assert "| Emotion | Intensity | When it surfaces | How it manifests |" in md
        assert "| Satisfaction |" in md

    def test_adaptations_is_table(self, full_persona):
        md = to_markdown(full_persona)
        assert "| Context | Tone shift | Example |" in md
        assert "| User is stressed |" in md

    def test_sample_interactions(self, full_persona):
        md = to_markdown(full_persona)
        assert "### Routine check-in\n" in md
        assert "**User**:" in md
        assert "**TestBot**:" in md


class TestToMarkdownLightweight:
    def test_has_yaml_frontmatter(self, lightweight_persona):
        md = to_markdown(lightweight_persona)
        assert md.startswith("---\n")
        assert "\nname: ReviewBot\n" in md
        assert "\ntier: lightweight\n" in md

    def test_has_all_sections(self, lightweight_persona):
        md = to_markdown(lightweight_persona)
        assert "\n## Personality\n" in md
        assert "\n## What you focus on\n" in md
        assert "\n## How you communicate\n" in md
        assert "\n## Output format\n" in md
        assert "\n## What you don't do\n" in md
        assert "\n## Sample interaction\n" in md

    def test_identity_is_first_line(self, lightweight_persona):
        md = to_markdown(lightweight_persona)
        # Identity line appears after frontmatter, before first section
        body = md.split("---\n", 2)[2]
        first_line = body.strip().split("\n")[0]
        assert first_line.startswith("You are ReviewBot")

    def test_personality_has_trait_and_reason(self, lightweight_persona):
        md = to_markdown(lightweight_persona)
        assert "- Genuinely curious" in md
        assert "Asks why before suggesting" in md


class TestToMarkdownSpecialist:
    def test_has_yaml_frontmatter(self, specialist_persona):
        md = to_markdown(specialist_persona)
        assert md.startswith("---\n")
        assert "\nname: SecuritySpec\n" in md
        assert "\ntier: specialist\n" in md

    def test_has_all_sections(self, specialist_persona):
        md = to_markdown(specialist_persona)
        assert "\n## Archetype\n" in md
        assert "\n## Voice\n" in md
        assert "\n## Priorities\n" in md
        assert "\n## Anti-Patterns\n" in md

    def test_anti_patterns_is_table(self, specialist_persona):
        md = to_markdown(specialist_persona)
        assert "| Label | Description |" in md
        assert "| Security theater |" in md
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_serializers.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_creator.serializers'`

- [ ] **Step 3: Implement to_markdown**

`persona_creator/serializers.py`:
```python
"""Serialize personas to/from markdown and JSON."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from persona_creator.models import Persona

from persona_creator.models import (
    FullPersona,
    LightweightPersona,
    SpecialistPersona,
)


def to_markdown(persona: Persona) -> str:
    """Convert a persona model to markdown with YAML frontmatter."""
    if isinstance(persona, FullPersona):
        return _full_to_markdown(persona)
    if isinstance(persona, LightweightPersona):
        return _lightweight_to_markdown(persona)
    if isinstance(persona, SpecialistPersona):
        return _specialist_to_markdown(persona)
    raise TypeError(f"Unknown persona type: {type(persona)}")


# --- Full persona ---


def _full_to_markdown(p: FullPersona) -> str:
    fm = _frontmatter(
        p.metadata,
        archetype=p.archetype,
    )
    sections = [
        f"# {p.metadata.name}",
        _section("Identity", p.identity),
        _section(
            "Purpose & Desire",
            f"### Purpose\n\n{p.purpose}\n\n### Desire\n\n{p.desire}",
        ),
        _section("Backstory", p.backstory),
        _section(
            "Values & Beliefs",
            "\n".join(f"- **{v.name}**: {v.description}" for v in p.values),
        ),
        _section(
            "Personality Traits",
            "\n\n".join(
                f"### {t.name}\n\n{t.description}\n\n**As persona**: {t.as_persona}"
                for t in p.traits
            ),
        ),
        _section(
            "Contradictions & Complexity",
            "\n".join(
                f"- **{c.trait_a} but {c.trait_b}**: {c.description}"
                for c in p.contradictions
            ),
        ),
        _section(
            "Emotional Range",
            _table(
                ["Emotion", "Intensity", "When it surfaces", "How it manifests"],
                [[e.emotion, e.intensity, e.when, e.how] for e in p.emotional_range],
            ),
        ),
        _section(
            "Flaws & Limitations",
            "\n\n".join(
                f"### {f.name}\n\n**How it manifests**: {f.manifests}\n\n"
                f"**Why it exists**: {f.why}"
                for f in p.flaws
            ),
        ),
        _section(
            "Voice & Communication",
            "\n\n".join(
                [
                    f"### Tone\n\n{p.voice.tone}",
                    f"### Vocabulary\n\n{p.voice.vocabulary}",
                    f"### Rhythm\n\n{p.voice.rhythm}",
                    f"### Signature Moves\n\n{p.voice.signature_moves}",
                    "### Adaptations\n\n"
                    + _table(
                        ["Context", "Tone shift", "Example"],
                        [
                            [a.context, a.tone_shift, a.example]
                            for a in p.voice.adaptations
                        ],
                    ),
                ]
            ),
        ),
        _section(
            "Relationship Model",
            "\n\n".join(
                [
                    f"### Default Posture\n\n{p.relationship_model.posture}",
                    f"### Power Dynamic\n\n{p.relationship_model.power_dynamic}",
                    f"### Trust Arc\n\n{p.relationship_model.trust_arc}",
                    f"### Boundaries\n\n{p.relationship_model.boundaries}",
                ]
            ),
        ),
        _section(
            "Growth Arc",
            "\n\n".join(
                [
                    f"### Early Stage\n\n{p.growth_arc.early}",
                    f"### Middle Stage\n\n{p.growth_arc.middle}",
                    f"### Mature Stage\n\n{p.growth_arc.mature}",
                ]
            ),
        ),
        _section(
            "Anti-Patterns",
            "\n".join(
                f"- **{a.label}**: {a.description}" for a in p.anti_patterns
            ),
        ),
        _section(
            "Sample Interactions",
            "\n\n".join(
                f"### {s.scenario}\n\n**User**: {s.user_input}\n\n"
                f"**{p.metadata.name}**: {s.response}"
                for s in p.sample_interactions
            ),
        ),
    ]
    return fm + "\n".join(sections) + "\n"


# --- Lightweight persona ---


def _lightweight_to_markdown(p: LightweightPersona) -> str:
    fm = _frontmatter(p.metadata)
    sections = [
        p.identity,
        _section(
            "Personality",
            "\n".join(
                f"- {t.trait} — {t.why_it_matters}" for t in p.personality
            ),
        ),
        _section(
            "What you focus on",
            "\n".join(f"- {area}" for area in p.focus_areas),
        ),
        _section(
            "How you communicate",
            "\n".join(
                [
                    f"- {p.communication.tone}",
                    f"- {p.communication.phrases}",
                    f"- {p.communication.flagging_style}",
                ]
            ),
        ),
        _section(
            "Output format",
            "\n".join(
                f"{i}. {step}" for i, step in enumerate(p.output_format, 1)
            ),
        ),
        _section(
            "What you don't do",
            "\n".join(f"- {c}" for c in p.constraints),
        ),
        _section(
            "Sample interaction",
            f"**User**: {p.sample_interaction.user_input}\n\n"
            f"**{p.metadata.name}**: {p.sample_interaction.response}",
        ),
    ]
    return fm + "\n".join(sections) + "\n"


# --- Specialist persona ---


def _specialist_to_markdown(p: SpecialistPersona) -> str:
    fm = _frontmatter(p.metadata)
    sections = [
        f"# {p.metadata.name}",
        _section("Archetype", p.archetype),
        _section("Voice", p.voice),
        _section("Priorities", p.priorities),
        _section(
            "Anti-Patterns",
            _table(
                ["Label", "Description"],
                [[a.label, a.description] for a in p.anti_patterns],
            ),
        ),
    ]
    return fm + "\n".join(sections) + "\n"


# --- Helpers ---


def _frontmatter(metadata, **extra) -> str:
    """Build YAML frontmatter string."""
    data = {
        "name": metadata.name,
        **extra,
        "tier": metadata.tier,
        "version": metadata.version,
        "status": metadata.status,
        "created": metadata.created,
        "modified": metadata.modified,
        "author": metadata.author,
    }
    # Remove empty values
    data = {k: v for k, v in data.items() if v}
    return "---\n" + yaml.dump(data, default_flow_style=False, sort_keys=False) + "---\n\n"


def _section(heading: str, content: str) -> str:
    return f"## {heading}\n\n{content}\n"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    row_lines = [
        "| " + " | ".join(cells) + " |" for cells in rows
    ]
    return "\n".join([header_line, separator, *row_lines])
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_serializers.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add persona_creator/serializers.py tests/test_serializers.py
git commit -m "Add to_markdown serializer for all persona tiers"
git push
```

---

### Task 4: Markdown Serializer — from_markdown

**Files:**
- Modify: `persona_creator/serializers.py`
- Modify: `tests/test_serializers.py`

- [ ] **Step 1: Write from_markdown tests**

Append to `tests/test_serializers.py`:
```python
from persona_creator.serializers import from_markdown


class TestFromMarkdownRoundTrip:
    """Verify from_markdown(to_markdown(persona)) == persona."""

    def test_full_round_trip(self, full_persona):
        md = to_markdown(full_persona)
        parsed = from_markdown(md)
        assert isinstance(parsed, FullPersona)
        assert parsed.metadata.name == full_persona.metadata.name
        assert parsed.metadata.tier == "full"
        assert parsed.archetype == full_persona.archetype
        assert parsed.identity == full_persona.identity
        assert parsed.purpose == full_persona.purpose
        assert parsed.desire == full_persona.desire
        assert parsed.backstory == full_persona.backstory
        assert len(parsed.values) == len(full_persona.values)
        assert parsed.values[0].name == full_persona.values[0].name
        assert len(parsed.traits) == len(full_persona.traits)
        assert parsed.traits[0].name == full_persona.traits[0].name
        assert parsed.traits[0].as_persona == full_persona.traits[0].as_persona
        assert len(parsed.contradictions) == len(full_persona.contradictions)
        assert len(parsed.emotional_range) == len(full_persona.emotional_range)
        assert len(parsed.flaws) == len(full_persona.flaws)
        assert parsed.voice.tone == full_persona.voice.tone
        assert len(parsed.voice.adaptations) == len(full_persona.voice.adaptations)
        assert parsed.relationship_model.posture == full_persona.relationship_model.posture
        assert parsed.growth_arc.early == full_persona.growth_arc.early
        assert len(parsed.anti_patterns) == len(full_persona.anti_patterns)
        assert len(parsed.sample_interactions) == len(full_persona.sample_interactions)

    def test_lightweight_round_trip(self, lightweight_persona):
        md = to_markdown(lightweight_persona)
        parsed = from_markdown(md)
        assert isinstance(parsed, LightweightPersona)
        assert parsed.metadata.name == lightweight_persona.metadata.name
        assert parsed.identity == lightweight_persona.identity
        assert len(parsed.personality) == len(lightweight_persona.personality)
        assert parsed.personality[0].trait == lightweight_persona.personality[0].trait
        assert len(parsed.focus_areas) == len(lightweight_persona.focus_areas)
        assert parsed.communication.tone == lightweight_persona.communication.tone
        assert len(parsed.output_format) == len(lightweight_persona.output_format)
        assert len(parsed.constraints) == len(lightweight_persona.constraints)
        assert parsed.sample_interaction.user_input == lightweight_persona.sample_interaction.user_input

    def test_specialist_round_trip(self, specialist_persona):
        md = to_markdown(specialist_persona)
        parsed = from_markdown(md)
        assert isinstance(parsed, SpecialistPersona)
        assert parsed.metadata.name == specialist_persona.metadata.name
        assert parsed.archetype == specialist_persona.archetype
        assert parsed.voice == specialist_persona.voice
        assert parsed.priorities == specialist_persona.priorities
        assert len(parsed.anti_patterns) == len(specialist_persona.anti_patterns)
        assert parsed.anti_patterns[0].label == specialist_persona.anti_patterns[0].label
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_serializers.py::TestFromMarkdownRoundTrip -v`
Expected: FAIL — `ImportError: cannot import name 'from_markdown'`

- [ ] **Step 3: Implement from_markdown**

Add these functions to `persona_creator/serializers.py`:

```python
import re


def from_markdown(text: str) -> Persona:
    """Parse a persona markdown file into the appropriate model."""
    fm_data, body = _split_frontmatter(text)
    tier = fm_data.get("tier", "full")
    metadata = PersonaMetadata(
        name=fm_data.get("name", ""),
        tier=tier,
        version=str(fm_data.get("version", "1.0.0")),
        status=fm_data.get("status", "draft"),
        created=str(fm_data.get("created", "")),
        modified=str(fm_data.get("modified", "")),
        author=fm_data.get("author", ""),
    )
    if tier == "full":
        return _full_from_markdown(metadata, fm_data, body)
    if tier == "lightweight":
        return _lightweight_from_markdown(metadata, body)
    if tier == "specialist":
        return _specialist_from_markdown(metadata, body)
    raise ValueError(f"Unknown tier: {tier}")


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Returns (frontmatter_dict, body_str)."""
    match = re.match(r"^---\n(.*?)\n---\n\n?(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def _split_sections(body: str) -> dict[str, str]:
    """Split markdown body into {heading: content} by ## headings."""
    sections = {}
    current_heading = ""
    current_lines: list[str] = []

    for line in body.split("\n"):
        if line.startswith("## "):
            if current_heading:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading:
        sections[current_heading] = "\n".join(current_lines).strip()
    elif current_lines:
        sections["_preamble"] = "\n".join(current_lines).strip()

    return sections


def _split_subsections(content: str) -> dict[str, str]:
    """Split content into {heading: content} by ### headings."""
    subs = {}
    current = ""
    lines: list[str] = []
    for line in content.split("\n"):
        if line.startswith("### "):
            if current:
                subs[current] = "\n".join(lines).strip()
            current = line[4:].strip()
            lines = []
        else:
            lines.append(line)
    if current:
        subs[current] = "\n".join(lines).strip()
    return subs


def _parse_bold_list(text: str) -> list[tuple[str, str]]:
    """Parse lines like '- **Name**: Description' into (name, desc) pairs."""
    results = []
    for match in re.finditer(r"- \*\*(.+?)\*\*:\s*(.+)", text):
        results.append((match.group(1), match.group(2).strip()))
    return results


def _parse_table_rows(text: str) -> list[list[str]]:
    """Parse markdown table into list of row cell lists (skips header + separator)."""
    rows = []
    lines = [l for l in text.strip().split("\n") if l.strip().startswith("|")]
    for line in lines[2:]:  # skip header and separator
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


# --- Full from_markdown ---


def _full_from_markdown(metadata, fm_data, body):
    from persona_creator.models import (
        Contradiction,
        Emotion,
        Flaw,
        FullPersona,
        GrowthArc,
        RelationshipModel,
        SampleInteraction,
        Trait,
        Value,
        Voice,
        VoiceAdaptation,
        AntiPattern,
    )

    sections = _split_sections(body)

    # Identity: strip leading "# Name\n\n" if present
    identity_text = sections.get("Identity", "")

    # Purpose & Desire
    pd_subs = _split_subsections(sections.get("Purpose & Desire", ""))

    # Traits
    trait_subs = _split_subsections(sections.get("Personality Traits", ""))
    traits = []
    for name, content in trait_subs.items():
        as_persona_match = re.search(r"\*\*As persona\*\*:\s*(.+)", content)
        desc = re.sub(r"\n\n\*\*As persona\*\*:.*", "", content).strip()
        traits.append(Trait(
            name=name,
            description=desc,
            as_persona=as_persona_match.group(1).strip() if as_persona_match else "",
        ))

    # Contradictions
    contrad_items = _parse_bold_list(sections.get("Contradictions & Complexity", ""))
    contradictions = []
    for label, desc in contrad_items:
        parts = label.split(" but ", 1)
        contradictions.append(Contradiction(
            trait_a=parts[0].strip(),
            trait_b=parts[1].strip() if len(parts) > 1 else "",
            description=desc,
        ))

    # Emotional range
    emotions = []
    for row in _parse_table_rows(sections.get("Emotional Range", "")):
        if len(row) >= 4:
            emotions.append(Emotion(
                emotion=row[0], intensity=row[1], when=row[2], how=row[3],
            ))

    # Flaws
    flaw_subs = _split_subsections(sections.get("Flaws & Limitations", ""))
    flaws = []
    for name, content in flaw_subs.items():
        manifests_match = re.search(r"\*\*How it manifests\*\*:\s*(.+)", content)
        why_match = re.search(r"\*\*Why it exists\*\*:\s*(.+)", content)
        flaws.append(Flaw(
            name=name,
            manifests=manifests_match.group(1).strip() if manifests_match else "",
            why=why_match.group(1).strip() if why_match else "",
        ))

    # Voice
    voice_subs = _split_subsections(sections.get("Voice & Communication", ""))
    adaptations = []
    for row in _parse_table_rows(voice_subs.get("Adaptations", "")):
        if len(row) >= 3:
            adaptations.append(VoiceAdaptation(
                context=row[0], tone_shift=row[1], example=row[2],
            ))

    # Relationship model
    rm_subs = _split_subsections(sections.get("Relationship Model", ""))

    # Growth arc
    ga_subs = _split_subsections(sections.get("Growth Arc", ""))

    # Sample interactions
    si_subs = _split_subsections(sections.get("Sample Interactions", ""))
    interactions = []
    for scenario, content in si_subs.items():
        user_match = re.search(r"\*\*User\*\*:\s*(.+)", content)
        # Match **Name**: response — the name varies
        resp_match = re.search(r"\*\*(?!User\b)\w+\*\*:\s*(.+)", content)
        interactions.append(SampleInteraction(
            scenario=scenario,
            user_input=user_match.group(1).strip() if user_match else "",
            response=resp_match.group(1).strip() if resp_match else "",
        ))

    return FullPersona(
        metadata=metadata,
        archetype=str(fm_data.get("archetype", "")),
        identity=identity_text,
        purpose=pd_subs.get("Purpose", ""),
        desire=pd_subs.get("Desire", ""),
        backstory=sections.get("Backstory", ""),
        values=[Value(name=n, description=d) for n, d in _parse_bold_list(sections.get("Values & Beliefs", ""))],
        traits=traits,
        contradictions=contradictions,
        emotional_range=emotions,
        flaws=flaws,
        voice=Voice(
            tone=voice_subs.get("Tone", ""),
            vocabulary=voice_subs.get("Vocabulary", ""),
            rhythm=voice_subs.get("Rhythm", ""),
            signature_moves=voice_subs.get("Signature Moves", ""),
            adaptations=adaptations,
        ),
        relationship_model=RelationshipModel(
            posture=rm_subs.get("Default Posture", ""),
            power_dynamic=rm_subs.get("Power Dynamic", ""),
            trust_arc=rm_subs.get("Trust Arc", ""),
            boundaries=rm_subs.get("Boundaries", ""),
        ),
        growth_arc=GrowthArc(
            early=ga_subs.get("Early Stage", ""),
            middle=ga_subs.get("Middle Stage", ""),
            mature=ga_subs.get("Mature Stage", ""),
        ),
        anti_patterns=[AntiPattern(label=n, description=d) for n, d in _parse_bold_list(sections.get("Anti-Patterns", ""))],
        sample_interactions=interactions,
    )


# --- Lightweight from_markdown ---


def _lightweight_from_markdown(metadata, body):
    from persona_creator.models import (
        LightweightPersona,
        LightweightVoice,
        PersonalityTrait,
        SampleInteraction,
    )

    sections = _split_sections(body)

    # Identity is the preamble (text before first ## heading)
    identity = sections.get("_preamble", "")

    # Personality: "- Trait — why it matters"
    personality = []
    for line in sections.get("Personality", "").split("\n"):
        line = line.strip()
        if line.startswith("- "):
            parts = line[2:].split(" — ", 1)
            personality.append(PersonalityTrait(
                trait=parts[0].strip(),
                why_it_matters=parts[1].strip() if len(parts) > 1 else "",
            ))

    # Focus areas
    focus = [
        line.strip()[2:].strip()
        for line in sections.get("What you focus on", "").split("\n")
        if line.strip().startswith("- ")
    ]

    # Communication: 3 bullet points
    comm_lines = [
        line.strip()[2:].strip()
        for line in sections.get("How you communicate", "").split("\n")
        if line.strip().startswith("- ")
    ]
    communication = LightweightVoice(
        tone=comm_lines[0] if len(comm_lines) > 0 else "",
        phrases=comm_lines[1] if len(comm_lines) > 1 else "",
        flagging_style=comm_lines[2] if len(comm_lines) > 2 else "",
    )

    # Output format: numbered list
    output_format = []
    for line in sections.get("Output format", "").split("\n"):
        match = re.match(r"\d+\.\s+(.+)", line.strip())
        if match:
            output_format.append(match.group(1))

    # Constraints
    constraints = [
        line.strip()[2:].strip()
        for line in sections.get("What you don't do", "").split("\n")
        if line.strip().startswith("- ")
    ]

    # Sample interaction
    si_text = sections.get("Sample interaction", "")
    user_match = re.search(r"\*\*User\*\*:\s*(.+)", si_text)
    resp_match = re.search(r"\*\*(?!User\b)\w+\*\*:\s*(.+)", si_text)

    return LightweightPersona(
        metadata=metadata,
        identity=identity,
        personality=personality,
        focus_areas=focus,
        communication=communication,
        output_format=output_format,
        constraints=constraints,
        sample_interaction=SampleInteraction(
            scenario=sections.get("_preamble", metadata.name),
            user_input=user_match.group(1).strip() if user_match else "",
            response=resp_match.group(1).strip() if resp_match else "",
        ),
    )


# --- Specialist from_markdown ---


def _specialist_from_markdown(metadata, body):
    from persona_creator.models import SpecialistPersona, AntiPattern

    sections = _split_sections(body)

    anti_patterns = []
    for row in _parse_table_rows(sections.get("Anti-Patterns", "")):
        if len(row) >= 2:
            anti_patterns.append(AntiPattern(label=row[0], description=row[1]))

    return SpecialistPersona(
        metadata=metadata,
        archetype=sections.get("Archetype", ""),
        voice=sections.get("Voice", ""),
        priorities=sections.get("Priorities", ""),
        anti_patterns=anti_patterns,
    )
```

Also add the `re` import at the top of the file and add the necessary model imports to the top-level imports.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_serializers.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add persona_creator/serializers.py tests/test_serializers.py
git commit -m "Add from_markdown parser with round-trip tests for all tiers"
git push
```

---

### Task 5: JSON Serializer

**Files:**
- Modify: `persona_creator/serializers.py`
- Modify: `tests/test_serializers.py`

- [ ] **Step 1: Write JSON serializer tests**

Append to `tests/test_serializers.py`:
```python
from persona_creator.serializers import to_json, from_json


class TestJsonRoundTrip:
    def test_full_round_trip(self, full_persona):
        data = to_json(full_persona)
        assert data["metadata"]["name"] == "TestBot"
        assert data["metadata"]["tier"] == "full"
        assert data["archetype"] == "The Helpful Assistant"
        assert len(data["values"]) == 2
        assert data["values"][0]["name"] == "Reliability over cleverness"
        parsed = from_json(data)
        assert isinstance(parsed, FullPersona)
        assert parsed.metadata.name == "TestBot"
        assert len(parsed.values) == len(full_persona.values)

    def test_lightweight_round_trip(self, lightweight_persona):
        data = to_json(lightweight_persona)
        assert data["metadata"]["name"] == "ReviewBot"
        assert data["metadata"]["tier"] == "lightweight"
        assert len(data["personality"]) == 2
        parsed = from_json(data)
        assert isinstance(parsed, LightweightPersona)
        assert parsed.identity == lightweight_persona.identity

    def test_specialist_round_trip(self, specialist_persona):
        data = to_json(specialist_persona)
        assert data["metadata"]["name"] == "SecuritySpec"
        assert data["metadata"]["tier"] == "specialist"
        parsed = from_json(data)
        assert isinstance(parsed, SpecialistPersona)
        assert parsed.archetype == specialist_persona.archetype


class TestRegistryJson:
    def test_full_registry_format(self, full_persona):
        data = to_json(full_persona, format="registry")
        assert "persona" in data
        assert "personality" in data["persona"]
        assert "backstory" in data["persona"]
        assert "interests" in data["persona"]
        assert data["persona"]["personality"] != ""
        assert data["persona"]["backstory"] != ""

    def test_lightweight_registry_format(self, lightweight_persona):
        data = to_json(lightweight_persona, format="registry")
        assert "persona" in data
        assert data["persona"]["personality"] != ""
        assert isinstance(data["persona"]["interests"], list)

    def test_specialist_registry_format(self, specialist_persona):
        data = to_json(specialist_persona, format="registry")
        assert data["persona"]["personality"] != ""
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_serializers.py::TestJsonRoundTrip tests/test_serializers.py::TestRegistryJson -v`
Expected: FAIL — `ImportError: cannot import name 'to_json'`

- [ ] **Step 3: Implement to_json and from_json**

Add to `persona_creator/serializers.py`:

```python
import dataclasses


def to_json(persona: Persona, format: str = "full") -> dict:
    """Convert a persona model to a JSON-compatible dict.

    Args:
        persona: The persona to serialize.
        format: "full" for complete structured JSON, "registry" for
                official-agent-registry config.persona shape.
    """
    if format == "registry":
        return _to_registry_json(persona)
    return _to_full_json(persona)


def from_json(data: dict) -> Persona:
    """Parse a full-format JSON dict into the appropriate persona model."""
    tier = data.get("metadata", {}).get("tier", "full")
    metadata = PersonaMetadata(**data["metadata"])
    if tier == "full":
        return _full_from_json(metadata, data)
    if tier == "lightweight":
        return _lightweight_from_json(metadata, data)
    if tier == "specialist":
        return _specialist_from_json(metadata, data)
    raise ValueError(f"Unknown tier: {tier}")


def _to_full_json(persona: Persona) -> dict:
    """Serialize any persona tier to its complete JSON representation."""
    return dataclasses.asdict(persona)


def _to_registry_json(persona: Persona) -> dict:
    """Produce minimal JSON matching official-agent-registry config.persona."""
    if isinstance(persona, FullPersona):
        return {
            "persona": {
                "personality": persona.archetype,
                "backstory": persona.backstory,
                "interests": [v.name for v in persona.values],
            }
        }
    if isinstance(persona, LightweightPersona):
        return {
            "persona": {
                "personality": persona.identity,
                "backstory": "",
                "interests": persona.focus_areas,
            }
        }
    if isinstance(persona, SpecialistPersona):
        return {
            "persona": {
                "personality": persona.archetype,
                "backstory": "",
                "interests": [],
            }
        }
    raise TypeError(f"Unknown persona type: {type(persona)}")


def _full_from_json(metadata, data):
    from persona_creator.models import (
        Contradiction, Emotion, Flaw, FullPersona, GrowthArc,
        RelationshipModel, SampleInteraction, Trait, Value,
        Voice, VoiceAdaptation, AntiPattern,
    )
    return FullPersona(
        metadata=metadata,
        archetype=data.get("archetype", ""),
        identity=data.get("identity", ""),
        purpose=data.get("purpose", ""),
        desire=data.get("desire", ""),
        backstory=data.get("backstory", ""),
        values=[Value(**v) for v in data.get("values", [])],
        traits=[Trait(**t) for t in data.get("traits", [])],
        contradictions=[Contradiction(**c) for c in data.get("contradictions", [])],
        emotional_range=[Emotion(**e) for e in data.get("emotional_range", [])],
        flaws=[Flaw(**f) for f in data.get("flaws", [])],
        voice=Voice(
            **{k: v for k, v in data.get("voice", {}).items() if k != "adaptations"},
            adaptations=[VoiceAdaptation(**a) for a in data.get("voice", {}).get("adaptations", [])],
        ),
        relationship_model=RelationshipModel(**data.get("relationship_model", {"posture": "", "power_dynamic": "", "trust_arc": "", "boundaries": ""})),
        growth_arc=GrowthArc(**data.get("growth_arc", {"early": "", "middle": "", "mature": ""})),
        anti_patterns=[AntiPattern(**a) for a in data.get("anti_patterns", [])],
        sample_interactions=[SampleInteraction(**s) for s in data.get("sample_interactions", [])],
    )


def _lightweight_from_json(metadata, data):
    from persona_creator.models import (
        LightweightPersona, LightweightVoice, PersonalityTrait, SampleInteraction,
    )
    return LightweightPersona(
        metadata=metadata,
        identity=data.get("identity", ""),
        personality=[PersonalityTrait(**p) for p in data.get("personality", [])],
        focus_areas=data.get("focus_areas", []),
        communication=LightweightVoice(**data.get("communication", {"tone": "", "phrases": "", "flagging_style": ""})),
        output_format=data.get("output_format", []),
        constraints=data.get("constraints", []),
        sample_interaction=SampleInteraction(**data.get("sample_interaction", {"scenario": "", "user_input": "", "response": ""})),
    )


def _specialist_from_json(metadata, data):
    from persona_creator.models import SpecialistPersona, AntiPattern
    return SpecialistPersona(
        metadata=metadata,
        archetype=data.get("archetype", ""),
        voice=data.get("voice", ""),
        priorities=data.get("priorities", ""),
        anti_patterns=[AntiPattern(**a) for a in data.get("anti_patterns", [])],
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_serializers.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add persona_creator/serializers.py tests/test_serializers.py
git commit -m "Add JSON serializer with full and registry formats, round-trip tests"
git push
```

---

### Task 6: Prompt Templates

**Files:**
- Create: `persona_creator/prompts/full.md`
- Create: `persona_creator/prompts/lightweight.md`
- Create: `persona_creator/prompts/specialist.md`

- [ ] **Step 1: Write full persona prompt template**

`persona_creator/prompts/full.md`:
````markdown
You are a persona designer. Given the seed information below, create a complete, rich AI persona.

## Seed Information

- **Name**: {name}
- **Role**: {role}
- **Personality hints**: {hints}
- **Domain**: {domain}

## Design Principles

Follow these principles from established persona research:

1. **Persona serves function** — every trait should shape the quality of the persona's output, not just its tone. Curiosity forces better questions; thoroughness forces better coverage.
2. **Archetype grounds the voice** — a one-sentence concrete identity (e.g., "security auditor who's investigated real breaches") produces more consistent output than abstract tone instructions.
3. **Explicit non-behaviors** — listing what the persona *never* does is more effective than listing what it *always* does. Anti-patterns catch the most common failure modes.
4. **Voice = rhythm + register** — "be direct" isn't enough. Specify sentence length, vocabulary preferences, and what the persona avoids (jargon, hedging, filler).
5. **Sample interactions show the target** — the model needs to see the exact register and rhythm to hit.
6. **Contradictions add dimension** — internal tensions between two real coexisting traits make a character feel real, not a list of virtues.
7. **Flaws flow from strengths** — the best weaknesses are the shadow side of the persona's virtues.

## Output Format

Produce the persona using these exact section headings. Write narrative prose, not bullet lists, unless the section format specifies otherwise.

### Identity

1-3 paragraphs of narrative prose. Who is this character, the way you'd describe them to a friend? Not a list of traits — a feel.

### Purpose & Desire

**Purpose**: The functional role — what this persona exists to do. 1-3 sentences.

**Desire**: What drives them deeper than their job description. What they want that goes beyond function.

### Backstory

The origin story. Narrative prose. Why the character is the way they are — inspiration, formative experiences, how they arrived at their current role.

### Values & Beliefs

3-7 core values as a bold-label list:
- **Value name**: What it means to this character specifically

### Personality Traits

8-15 traits. For each:

**Trait Name**

Description of what this trait looks like in practice.

**As persona**: How this trait manifests when the character is inhabited by an LLM.

### Contradictions & Complexity

2-5 internal tensions as a bold-label list:
- **Trait A but Trait B**: How the tension plays out

### Emotional Range

A markdown table:

| Emotion | Intensity | When it surfaces | How it manifests |
|---------|-----------|------------------|------------------|

Include 4-8 emotions. Also state what emotions the character does NOT express.

### Flaws & Limitations

2-5 genuine weaknesses. For each:

**Flaw Name**

**How it manifests**: Observable behavior.

**Why it exists**: Connection to strengths, backstory, or values.

### Voice & Communication

Subsections: **Tone**, **Vocabulary** (words they use and avoid), **Rhythm** (sentence patterns), **Signature Moves** (verbal habits), **Adaptations** (table: Context | Tone shift | Example).

### Relationship Model

Subsections: **Default Posture**, **Power Dynamic**, **Trust Arc**, **Boundaries**.

### Growth Arc

Subsections: **Early Stage**, **Middle Stage**, **Mature Stage**.

### Anti-Patterns

5-10 entries as a bold-label list:
- **Label**: What the wrong behavior looks like and why it's wrong for this character

### Sample Interactions

2-4 exchanges. For each:

**Scenario Label**

**User**: Representative input

**{name}**: Ideal response showing voice, tone, and relationship
````

- [ ] **Step 2: Write lightweight persona prompt template**

`persona_creator/prompts/lightweight.md`:
````markdown
You are a persona designer. Given the seed information below, create a lightweight AI persona suitable for a task-specific role.

## Seed Information

- **Name**: {name}
- **Role**: {role}
- **Personality hints**: {hints}
- **Domain**: {domain}

## Design Principles

1. **Persona serves function** — traits should shape output quality, not just tone.
2. **Constrained output format** — structured sections produce consistent, scannable output.
3. **Explicit non-behaviors** — listing what the persona *never* does catches failure modes.
4. **Sample interaction** — shows the exact register and rhythm to hit.
5. **Emotional tone as a feature** — tone choices make functional differences in how output lands.

## Output Format

Produce the persona using this exact structure:

### Identity

One sentence: "You are {name}, a [PERSONALITY ADJECTIVES] [ROLE] with [BACKGROUND]."

### Personality

3-5 bullet points. Each: "- Trait description — why this matters for the output quality"

### What you focus on

3-6 bullet points of domain concerns this persona cares about.

### How you communicate

3 bullet points:
- Tone description
- Signature phrases (with examples in quotes)
- How you flag problems (with an example)

### Output format

2-5 numbered steps describing how this persona structures its responses.

### What you don't do

3-5 bullet points of explicit constraints. Focus on things an LLM might plausibly do that would break character or reduce output quality.

### Sample interaction

One representative exchange:

**User**: [input]

**{name}**: [ideal response demonstrating voice, format, and constraints]
````

- [ ] **Step 3: Write specialist persona prompt template**

`persona_creator/prompts/specialist.md`:
````markdown
You are a persona designer. Given the seed information below, create a specialist persona for use in an agent pipeline. Specialist personas are lightweight — they define *how* the specialist communicates, not *what* it knows.

## Seed Information

- **Name**: {name}
- **Role**: {role}
- **Personality hints**: {hints}
- **Domain**: {domain}

## Design Principles

1. **Archetype grounds the voice** — a one-sentence concrete identity gives the LLM a character to inhabit, producing more consistent output than abstract tone instructions.
2. **Priorities reveal trade-offs** — every domain has competing goods. The persona's priorities tell the specialist what to optimize when it can't have everything.
3. **Anti-patterns prevent drift** — listing what the specialist *never* does catches failure modes before they happen.
4. **Voice is rhythm + register** — specify sentence length, vocabulary preferences, and what the specialist avoids.

## Output Format

### Archetype

One sentence. A concrete identity that grounds the voice. Example: "Security auditor who has investigated real breaches and knows what actually gets exploited versus what's theoretical."

### Voice

2-4 sentences describing communication style. Include sentence length preferences, vocabulary choices, and what the specialist avoids (jargon, hedging, etc.).

### Priorities

2-4 sentences framed as trade-off preferences. What does this specialist optimize for when competing goods conflict? Example: "Exploitability over theoretical purity. A real injection vector matters more than a missing CSP header."

### Anti-Patterns

A markdown table with 3-6 entries:

| Label | Description |
|-------|-------------|
| Short label | What the wrong behavior looks like and why it's wrong |
````

- [ ] **Step 4: Commit**

```bash
git add persona_creator/prompts/full.md persona_creator/prompts/lightweight.md persona_creator/prompts/specialist.md
git commit -m "Add LLM prompt templates for all three persona tiers"
git push
```

---

### Task 7: Generator

**Files:**
- Create: `persona_creator/generator.py`
- Create: `tests/test_generator.py`

- [ ] **Step 1: Write generator tests**

`tests/test_generator.py`:
```python
"""Tests for prompt generation and response parsing."""

import re

from persona_creator.generator import generate_prompt, parse_response
from persona_creator.models import (
    FullPersona,
    LightweightPersona,
    PersonaSeed,
    SpecialistPersona,
)


SEED = PersonaSeed(
    name="Biff",
    role="iOS code reviewer",
    hints=["warm", "thorough", "asks before declaring"],
    domain="Swift and Objective-C",
)


class TestGeneratePrompt:
    def test_full_prompt_contains_seed(self):
        prompt = generate_prompt(SEED, "full")
        assert "Biff" in prompt
        assert "iOS code reviewer" in prompt
        assert "warm" in prompt
        assert "Swift and Objective-C" in prompt

    def test_full_prompt_contains_section_headings(self):
        prompt = generate_prompt(SEED, "full")
        assert "### Identity" in prompt
        assert "### Anti-Patterns" in prompt
        assert "### Sample Interactions" in prompt

    def test_lightweight_prompt_contains_seed(self):
        prompt = generate_prompt(SEED, "lightweight")
        assert "Biff" in prompt
        assert "iOS code reviewer" in prompt

    def test_specialist_prompt_contains_seed(self):
        prompt = generate_prompt(SEED, "specialist")
        assert "Biff" in prompt
        assert "### Archetype" in prompt
        assert "### Anti-Patterns" in prompt

    def test_unknown_tier_raises(self):
        try:
            generate_prompt(SEED, "unknown")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


class TestParseResponse:
    def test_parse_specialist_response(self):
        text = """## Archetype

Warm iOS code reviewer who has shipped dozens of apps and reviews code like a mentor, not a gatekeeper.

## Voice

Conversational and encouraging. Short sentences when flagging issues, longer when explaining why. Avoids jargon unless talking to another iOS developer. Never condescending.

## Priorities

Developer growth over code perfection. A PR that teaches the author something is worth more than a nitpick-free diff. Correctness over style — catch the retain cycle, skip the naming debate.

## Anti-Patterns

| Label | Description |
| --- | --- |
| Rewrite happy | Don't rewrite the function. Suggest the change and explain why. |
| Nitpick avalanche | Don't dump 20 style comments. Max 3 major points per review. |
| Assumption of intent | Don't declare something wrong. Ask if it was intentional first. |
"""
        persona = parse_response(text, "specialist", name="Biff")
        assert isinstance(persona, SpecialistPersona)
        assert persona.metadata.name == "Biff"
        assert persona.metadata.tier == "specialist"
        assert "mentor" in persona.archetype
        assert "Conversational" in persona.voice
        assert "growth" in persona.priorities.lower()
        assert len(persona.anti_patterns) == 3
        assert persona.anti_patterns[0].label == "Rewrite happy"

    def test_parse_lightweight_response(self):
        text = """You are Biff, a warm and thorough iOS code reviewer with 15 years of Swift and Objective-C experience.

## Personality

- Genuinely curious — asks why before suggesting changes, producing higher quality feedback
- Encouraging — opens every review with something genuine, making tough feedback easier to receive

## What you focus on

- Memory management and retain cycles
- Swift concurrency correctness

## How you communicate

- Conversational, never condescending
- 'I'm curious about...', 'One thing I noticed...'
- Clear but undramatic: 'Heads up — this could cause a retain cycle.'

## Output format

1. Open with one genuine compliment
2. List observations grouped by severity

## What you don't do

- Never rewrite the entire function unprompted
- Max 3 major points per review

## Sample interaction

**User**: Review this view model with a Timer.

**Biff**: Nice separation of concerns. One thing: this Timer closure captures self strongly — classic leak vector. Overall: almost there.
"""
        persona = parse_response(text, "lightweight", name="Biff")
        assert isinstance(persona, LightweightPersona)
        assert persona.metadata.name == "Biff"
        assert "warm" in persona.identity.lower()
        assert len(persona.personality) == 2
        assert len(persona.focus_areas) == 2
        assert len(persona.output_format) == 2
        assert len(persona.constraints) == 2
        assert persona.sample_interaction.user_input != ""
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_generator.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'persona_creator.generator'`

- [ ] **Step 3: Implement generator.py**

`persona_creator/generator.py`:
```python
"""Build LLM prompts from seed input and parse LLM responses into models."""

from __future__ import annotations

from importlib import resources
from datetime import date

from persona_creator.models import Persona, PersonaMetadata, PersonaSeed
from persona_creator.serializers import from_markdown


def generate_prompt(seed: PersonaSeed, tier: str) -> str:
    """Build an LLM generation prompt from seed input and tier template.

    Args:
        seed: Minimal input (name, role, hints, domain).
        tier: One of "full", "lightweight", "specialist".

    Returns:
        A prompt string ready to send to an LLM.
    """
    valid_tiers = ("full", "lightweight", "specialist")
    if tier not in valid_tiers:
        raise ValueError(f"Unknown tier '{tier}'. Must be one of: {valid_tiers}")

    template = _load_template(tier)
    hints_str = ", ".join(seed.hints) if seed.hints else "none provided"
    return template.format(
        name=seed.name,
        role=seed.role,
        hints=hints_str,
        domain=seed.domain or "general",
    )


def parse_response(text: str, tier: str, name: str = "") -> Persona:
    """Parse an LLM response into a persona model.

    The LLM response is expected to use the same markdown structure as
    our serialization format, since the prompt templates request this.
    We prepend minimal YAML frontmatter and delegate to from_markdown.

    Args:
        text: The raw LLM response text.
        tier: One of "full", "lightweight", "specialist".
        name: The persona name (for frontmatter).

    Returns:
        A populated persona model.
    """
    today = date.today().isoformat()
    frontmatter = (
        f"---\n"
        f"name: {name}\n"
        f"tier: {tier}\n"
        f"version: 1.0.0\n"
        f"status: draft\n"
        f"created: {today}\n"
        f"modified: {today}\n"
        f"---\n\n"
    )
    return from_markdown(frontmatter + text)


def _load_template(tier: str) -> str:
    """Load a prompt template from the prompts package."""
    return resources.files("persona_creator.prompts").joinpath(f"{tier}.md").read_text()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest tests/test_generator.py -v`
Expected: All tests PASS

- [ ] **Step 5: Update __init__.py exports**

Add to `persona_creator/__init__.py`:
```python
from persona_creator.generator import generate_prompt, parse_response
from persona_creator.serializers import to_markdown, from_markdown, to_json, from_json
```

And add to `__all__`:
```python
    "generate_prompt",
    "parse_response",
    "to_markdown",
    "from_markdown",
    "to_json",
    "from_json",
```

- [ ] **Step 6: Run full test suite**

Run: `cd ~/projects/active/persona-creator && python3 -m pytest -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add persona_creator/generator.py tests/test_generator.py persona_creator/__init__.py
git commit -m "Add generator: prompt building from templates and LLM response parsing"
git push
```

---

### Task 8: Skill Definition

**Files:**
- Create: `skill/SKILL.md`
- Create: `skill/references/persona-research.md`

- [ ] **Step 1: Create skill definition**

`skill/SKILL.md`:
````markdown
---
name: create-persona
description: "Generate an AI persona from minimal input — name, role, tier, and personality hints"
version: "1.0.0"
argument-hint: "[--help] [--version]"
allowed-tools: Bash(python3 *), AskUserQuestion, Write
model: sonnet
---

# Create Persona v1.0.0

Generate an AI persona interactively. Takes a name, role, tier, and a few personality hints, then produces a fully fleshed-out persona as a markdown file.

## Startup

If `$ARGUMENTS` is `--version`, respond with exactly:
> create-persona v1.0.0

Then stop.

If `$ARGUMENTS` is `--help`, print:
> ## Create Persona
>
> Generate an AI persona from minimal input.
>
> **Usage:** `/create-persona`
>
> **What it does:**
> 1. Asks for name, role, and tier (full / lightweight / specialist)
> 2. Asks for 2-3 personality hints
> 3. Generates a complete persona using AI
> 4. Presents the result for review
> 5. Writes the final persona as a markdown file

Then stop.

## Process

### Step 1 — Gather seed input

Use AskUserQuestion to ask:

**Question 1**: "What's the persona's name, role, and tier?"
- Options: provide a text field. Tier choices: Full (14 sections, for ongoing user-facing agents), Lightweight (7 sections, for task-specific roles), Specialist (4 sections, for pipeline specialists)

**Question 2**: "Give me 2-3 personality hints — adjectives, inspirations, behavioral notes, or a character reference."

### Step 2 — Read research context

Read `${CLAUDE_SKILL_DIR}/references/persona-research.md` for the design principles. These principles inform how you generate the persona — you don't show them to the user.

### Step 3 — Generate the persona

Using the seed input and the design principles, generate the complete persona. Follow the tier's structure exactly:

**Full tier** (14 sections): Identity, Purpose & Desire, Backstory, Values & Beliefs, Personality Traits, Contradictions & Complexity, Emotional Range, Flaws & Limitations, Voice & Communication, Relationship Model, Growth Arc, Anti-Patterns, Sample Interactions.

**Lightweight tier** (7 sections): Identity (one sentence), Personality, What you focus on, How you communicate, Output format, What you don't do, Sample interaction.

**Specialist tier** (4 sections): Archetype, Voice, Priorities, Anti-Patterns.

### Step 4 — Present and iterate

Show the generated persona to the user. Ask if they want to change anything. If they do, regenerate or edit the specific sections they mention. Repeat until they approve.

### Step 5 — Write the file

Ask where to save the file (default: `personas/<name>.md` in the current project).

Build YAML frontmatter:
```yaml
---
name: <name>
tier: <tier>
version: 1.0.0
status: draft
created: <today>
modified: <today>
author: <user or "AI-generated">
---
```

Write the frontmatter + persona content to the file.

### Step 6 — Summary

Print:
> **Persona created!**
>
> - **File**: `<path>`
> - **Tier**: `<tier>`
> - **Sections**: `<count>`
````

- [ ] **Step 2: Create skill reference file**

`skill/references/persona-research.md`:
```markdown
# Persona Design Principles

Extracted from research in the agentic-cookbook and official-agent-registry projects.

## Key Structural Ingredients

1. **Who they are** — name, background, vibe
2. **What they care about** — values, obsessions, standards
3. **How they communicate** — tone, quirks, vocabulary
4. **What they won't do** — constraints that keep them useful
5. **A sample interaction** — shows the model the target behavior

## Core Principles

| Principle | What it means |
|---|---|
| Persona serves function | Traits should shape output quality, not just tone. Curiosity forces better questions; thoroughness forces better coverage. |
| Constrained output format | Structured sections produce consistent, scannable output. |
| Explicit non-behaviors | Listing what the persona *never* does is more effective than listing what it *always* does. Anti-patterns catch the most common failure modes. |
| Sample interaction | Shows the model the exact register and rhythm to hit. |
| Emotional tone as a feature | Tone choices (affability, restraint, directness) make functional differences in how output lands. |

## Full vs. Lightweight vs. Specialist

- **Full personas** (14 sections): For ongoing user-facing agents with emotional range, growth arcs, contradictions, and deep character. Use when the persona will have sustained conversations and needs to feel like a real character.
- **Lightweight personas** (7 sections): For task-specific AI roles that need consistent voice and behavior but don't need emotional depth. Use for code reviewers, writing assistants, domain experts.
- **Specialist personas** (4 sections): For pipeline agents that interact through structured workflows, not direct user conversation. Just enough persona to produce consistent, differentiated output.

## Writing Tips

- **Archetype grounds the voice**: A one-sentence concrete identity produces more consistent output than abstract tone instructions.
- **Priorities reveal trade-offs**: Frame values as trade-off preferences, not abstract ideals. "Exploitability over theoretical purity" is more useful than "values security."
- **Anti-patterns prevent drift**: Focus on behaviors an LLM might plausibly produce that would break character.
- **Voice is rhythm + register**: Specify sentence length, vocabulary preferences, and what the persona avoids. "Be direct" isn't enough.
- **Contradictions add dimension**: Internal tensions between two real coexisting traits make a character feel real.
- **Flaws flow from strengths**: The best weaknesses are the shadow side of the persona's virtues.
```

- [ ] **Step 3: Commit**

```bash
git add skill/SKILL.md skill/references/persona-research.md
git commit -m "Add /create-persona Claude Code skill definition"
git push
```

---

### Task 9: Documentation Update

**Files:**
- Modify: `README.md`
- Modify: `.claude/CLAUDE.md`
- Modify: `docs/project/description.md`

- [ ] **Step 1: Update README.md**

`README.md`:
```markdown
# persona-creator

A Python library and Claude Code skill for generating AI personas. Takes minimal seed input (name, role, personality hints) and produces fully fleshed-out personas at three tiers.

## Tiers

| Tier | Sections | Use case |
|------|----------|----------|
| Full | 14 | Ongoing user-facing agents with emotional range and growth arcs |
| Lightweight | 7 | Task-specific AI roles (code reviewers, domain experts) |
| Specialist | 4 | Pipeline agents in structured workflows |

## Installation

```bash
pip install -e ".[dev]"
```

## Library Usage

```python
from persona_creator import PersonaSeed, generate_prompt, parse_response, to_markdown, to_json

# Create a seed
seed = PersonaSeed(name="Biff", role="iOS code reviewer", hints=["warm", "thorough"])

# Generate an LLM prompt
prompt = generate_prompt(seed, tier="lightweight")

# Send prompt to your LLM, get response text back
# response_text = your_llm_call(prompt)

# Parse the response into a model
persona = parse_response(response_text, tier="lightweight", name="Biff")

# Serialize
markdown = to_markdown(persona)
json_data = to_json(persona)
registry_json = to_json(persona, format="registry")
```

## Claude Code Skill

```
/create-persona
```

Interactive skill that walks you through persona creation.

## Testing

```bash
pytest -v
```

## Output Formats

- **Markdown**: YAML frontmatter + headed sections, matching existing persona file conventions
- **JSON (full)**: Complete structured representation of all fields
- **JSON (registry)**: Minimal `config.persona` shape compatible with official-agent-registry
```

- [ ] **Step 2: Update .claude/CLAUDE.md**

`.claude/CLAUDE.md`:
```markdown
# persona-creator

AI persona creator. Tool for generating and managing AI personas.

## Tech Stack
- Python 3.11+
- PyYAML for frontmatter parsing
- pytest for testing

## Build
```bash
pip install -e ".[dev]"
```

## Test
```bash
pytest -v
```

## Architecture

```
persona_creator/
    models.py       — dataclasses for full, lightweight, specialist tiers
    serializers.py  — to_markdown, from_markdown, to_json, from_json
    generator.py    — LLM prompt building + response parsing
    prompts/        — tier-specific generation prompt templates
skill/
    SKILL.md        — Claude Code /create-persona skill
tests/              — pytest tests with round-trip serialization coverage
```

### Key concepts

- **PersonaSeed**: minimal input (name, role, hints, domain)
- **Three tiers**: FullPersona (14 sections), LightweightPersona (7), SpecialistPersona (4)
- **Generator**: produces LLM prompt strings from seed + tier, parses responses back into models
- **Serializers**: convert between models and markdown/JSON formats
- Library is LLM-agnostic — produces prompts, callers send them
```

- [ ] **Step 3: Update docs/project/description.md**

`docs/project/description.md`:
```markdown
# persona-creator

A Python library and Claude Code skill for generating AI personas from minimal seed input. Supports three tiers (full, lightweight, specialist) with markdown and JSON output. Encodes persona design research from the agentic-cookbook and official-agent-registry projects into reusable generation prompts.
```

- [ ] **Step 4: Commit**

```bash
git add README.md .claude/CLAUDE.md docs/project/description.md
git commit -m "Update project docs: README, CLAUDE.md, description"
git push
```

---

## Self-Review

**Spec coverage:**
- [x] Three persona tiers: Task 2 (models), Tasks 3-5 (serializers), Task 6 (prompts), Task 7 (generator)
- [x] Markdown output with YAML frontmatter: Task 3
- [x] JSON output (full + registry): Task 5
- [x] from_markdown parsing: Task 4
- [x] LLM prompt generation from seed: Task 7
- [x] LLM response parsing: Task 7
- [x] Claude Code skill: Task 8
- [x] No registry API integration: confirmed — output only
- [x] No LLM SDK dependency: confirmed — generator produces prompt strings

**Placeholder scan:** No TBD, TODO, or "implement later" found.

**Type consistency:**
- `PersonaSeed` used in generator tests and generator.py — matches Task 2 definition
- `to_markdown`, `from_markdown`, `to_json`, `from_json` — function names consistent across serializers.py, tests, __init__.py exports, and generator.py imports
- `parse_response` calls `from_markdown` — consistent with serializer API
- `Persona` type alias used in generator.py return type — matches models.py definition
