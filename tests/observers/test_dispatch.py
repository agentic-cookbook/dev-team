"""Tests for observer dispatch — event extraction and auto-discovery."""

import json
import sys
import os
import pytest
from pathlib import Path

# Add the observers directory to sys.path so we can import dispatch
OBSERVERS_DIR = Path(__file__).parent.parent.parent / "plugins" / "dev-team" / "scripts" / "observers"
sys.path.insert(0, str(OBSERVERS_DIR))


def test_extract_event_from_hook_input(sample_transcript_jsonl):
    from dispatch import extract_event

    hook_input = {
        "session_id": "20260406-160200-a1b2",
        "agent_id": "abc123",
        "agent_type": "general-purpose",
        "agent_transcript_path": str(sample_transcript_jsonl),
        "last_assistant_message": "Done. Updated the parser.",
        "hook_event_name": "SubagentStop",
        "cwd": "/Users/test/projects/dev-team",
    }

    event = extract_event(hook_input)

    assert event["session_id"] == "20260406-160200-a1b2"
    assert event["agent_id"] == "abc123"
    assert event["agent_type"] == "general-purpose"
    assert event["status"] == "completed"
    assert event["tool_call_count"] == 2
    assert set(event["tools_used"]) == {"Read", "Write"}
    assert event["transcript_path"] == str(sample_transcript_jsonl)
    assert "timestamp" in event
    assert "summary" in event


def test_extract_event_counts_tools_correctly(tmp_path):
    from dispatch import extract_event

    transcript = tmp_path / "transcript.jsonl"
    lines = [
        {"type": "tool_use", "name": "Read"},
        {"type": "tool_use", "name": "Read"},
        {"type": "tool_use", "name": "Grep"},
        {"type": "tool_use", "name": "Write"},
    ]
    transcript.write_text("\n".join(json.dumps(l) for l in lines) + "\n")

    hook_input = {
        "session_id": "test",
        "agent_id": "test",
        "agent_type": "general-purpose",
        "agent_transcript_path": str(transcript),
        "last_assistant_message": "Done.",
        "hook_event_name": "SubagentStop",
    }

    event = extract_event(hook_input)
    assert event["tool_call_count"] == 4
    assert sorted(event["tools_used"]) == ["Grep", "Read", "Write"]


def test_extract_event_handles_missing_transcript(tmp_path):
    from dispatch import extract_event

    hook_input = {
        "session_id": "test",
        "agent_id": "test",
        "agent_type": "general-purpose",
        "agent_transcript_path": str(tmp_path / "nonexistent.jsonl"),
        "last_assistant_message": "Done.",
        "hook_event_name": "SubagentStop",
    }

    event = extract_event(hook_input)
    assert event["tool_call_count"] == 0
    assert event["tools_used"] == []
    assert event["status"] == "completed"


def test_extract_event_truncates_summary():
    from dispatch import extract_event

    hook_input = {
        "session_id": "test",
        "agent_id": "test",
        "agent_type": "general-purpose",
        "agent_transcript_path": "/nonexistent",
        "last_assistant_message": "x" * 500,
        "hook_event_name": "SubagentStop",
    }

    event = extract_event(hook_input)
    assert len(event["summary"]) <= 200


def test_discover_observers(tmp_path):
    from dispatch import discover_observers

    # Create mock observer modules
    (tmp_path / "stenographer.py").write_text("def observe(event): pass\n")
    (tmp_path / "oslog.py").write_text("def observe(event): pass\n")
    (tmp_path / "_lib.py").write_text("# private\n")
    (tmp_path / "dispatch.py").write_text("# self\n")
    (tmp_path / "not_python.txt").write_text("nope\n")

    observers = discover_observers(tmp_path)
    names = [o.__name__ for o in observers]
    assert "stenographer" in names
    assert "oslog" in names
    assert "_lib" not in names
    assert "dispatch" not in names
    assert len(observers) == 2


def test_discover_observers_skips_modules_without_observe(tmp_path):
    from dispatch import discover_observers

    (tmp_path / "has_observe.py").write_text("def observe(event): pass\n")
    (tmp_path / "no_observe.py").write_text("def something_else(): pass\n")

    observers = discover_observers(tmp_path)
    assert len(observers) == 1


def test_run_observers_isolates_failures(tmp_path, sample_event):
    from dispatch import discover_observers, run_observers

    (tmp_path / "failing.py").write_text("def observe(event): raise ValueError('boom')\n")
    (tmp_path / "passing.py").write_text(
        "results = []\ndef observe(event): results.append(event['agent_id'])\n"
    )

    observers = discover_observers(tmp_path)
    # Should not raise — failures are isolated
    run_observers(observers, sample_event)
