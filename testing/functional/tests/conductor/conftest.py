"""Conductor functional-test fixtures.

Adds the plugin's `dev-team` services package to sys.path so tests can
import `services.conductor.*` like the unit tests do.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "plugins" / "dev-team"))

FAKE_BIN = REPO_ROOT / "testing" / "fixtures" / "fake_claude_bin.py"
GOLDEN_DIR = REPO_ROOT / "testing" / "fixtures" / "golden_sessions"
PLAYBOOK_PATH = (
    REPO_ROOT
    / "plugins"
    / "dev-team"
    / "services"
    / "conductor"
    / "playbooks"
    / "name_a_puppy.py"
)
