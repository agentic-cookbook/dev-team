"""pet-coach team — trivial second team used to exercise cross-team requests.

Declares a single handler kind `pet_coach.suggest_theme` whose handler
state uses a RespondToRequest action to return a pre-baked theme. Step 3
wires this against a caller team that consumes the response before
dispatching its own specialists.
"""
from __future__ import annotations

import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[3]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from services.conductor.playbook.types import (  # noqa: E402
    Manifest,
    RespondToRequest,
    State,
    TeamPlaybook,
)


HANDLE_SUGGEST_THEME = State(
    name="handle_suggest_theme",
    entry_actions=(
        RespondToRequest(
            response_data={
                "theme": "outdoor-adventure",
                "hints": ["hiking", "rivers", "campfire"],
            }
        ),
    ),
)


PLAYBOOK = TeamPlaybook(
    name="pet-coach",
    states=[HANDLE_SUGGEST_THEME],
    transitions=[],
    judgment_specs={},
    manifest=Manifest(),
    initial_state="handle_suggest_theme",
    request_handlers={"pet_coach.suggest_theme": "handle_suggest_theme"},
)
