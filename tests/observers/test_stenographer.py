"""Tests for stenographer observer — session.log JSONL writer."""

import json
import os
import sys
import pytest
from pathlib import Path

OBSERVERS_DIR = Path(__file__).parent.parent.parent / "plugins" / "dev-team" / "scripts" / "observers"
sys.path.insert(0, str(OBSERVERS_DIR))


def test_stenographer_writes_jsonl_line(tmp_session_dir, sample_event):
    os.environ["ARBITRATOR_SESSION_BASE"] = str(tmp_session_dir)

    session_dir = tmp_session_dir / sample_event["session_id"]
    session_dir.mkdir()

    import importlib
    import _lib
    importlib.reload(_lib)
    import stenographer
    importlib.reload(stenographer)

    stenographer.observe(sample_event)

    log_path = session_dir / "session.log"
    assert log_path.exists()

    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["sid"] == sample_event["session_id"]
    assert entry["agent"] == "general-purpose"
    assert entry["desc"] == "Implement Task 4"
    assert entry["status"] == "completed"
    assert entry["calls"] == 16
    assert entry["tools"] == ["Bash", "Read", "Write"]

    os.environ.pop("ARBITRATOR_SESSION_BASE", None)


def test_stenographer_appends_multiple_entries(tmp_session_dir, sample_event):
    os.environ["ARBITRATOR_SESSION_BASE"] = str(tmp_session_dir)

    session_dir = tmp_session_dir / sample_event["session_id"]
    session_dir.mkdir()

    import importlib
    import _lib
    importlib.reload(_lib)
    import stenographer
    importlib.reload(stenographer)

    stenographer.observe(sample_event)
    stenographer.observe(sample_event)

    log_path = session_dir / "session.log"
    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 2

    os.environ.pop("ARBITRATOR_SESSION_BASE", None)


def test_stenographer_truncates_summary(tmp_session_dir, sample_event):
    os.environ["ARBITRATOR_SESSION_BASE"] = str(tmp_session_dir)

    session_dir = tmp_session_dir / sample_event["session_id"]
    session_dir.mkdir()

    import importlib
    import _lib
    importlib.reload(_lib)
    import stenographer
    importlib.reload(stenographer)

    sample_event["summary"] = "x" * 500
    stenographer.observe(sample_event)

    log_path = session_dir / "session.log"
    entry = json.loads(log_path.read_text().strip())
    assert len(entry["summary"]) <= 200

    os.environ.pop("ARBITRATOR_SESSION_BASE", None)


def test_stenographer_falls_back_to_general_log(tmp_session_dir, sample_event):
    os.environ["ARBITRATOR_SESSION_BASE"] = str(tmp_session_dir)

    import importlib
    import _lib
    importlib.reload(_lib)
    import stenographer
    importlib.reload(stenographer)

    stenographer.observe(sample_event)

    fallback_log = tmp_session_dir / "_logs" / "observer.log"
    assert fallback_log.exists()

    os.environ.pop("ARBITRATOR_SESSION_BASE", None)
