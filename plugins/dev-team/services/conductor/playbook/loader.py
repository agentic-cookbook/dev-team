"""Load a team-playbook Python module by file path or dotted name."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from .types import TeamPlaybook


def load_playbook(path: str | Path) -> TeamPlaybook:
    """Load a playbook module and return its `PLAYBOOK` export."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Playbook not found: {p}")
    spec = importlib.util.spec_from_file_location(p.stem, p)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load playbook at {p}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    playbook = getattr(module, "PLAYBOOK", None)
    if not isinstance(playbook, TeamPlaybook):
        raise TypeError(
            f"Playbook module {p} does not export a TeamPlaybook as PLAYBOOK"
        )
    return playbook
