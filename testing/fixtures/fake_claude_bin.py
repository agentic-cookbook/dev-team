#!/usr/bin/env python3
"""Fake `claude -p` binary for dispatcher tests.

Emulates the subset of behavior `ClaudeCodeDispatcher` depends on: reads
argv, optionally records it to a side-channel file, emits newline-delimited
stream-json events to stdout, honors an optional scripted scenario loaded
from FAKE_CLAUDE_SCRIPT env var.

Scripts are JSON files with this shape:

    {
        "events": [                # stream-json events to emit in order
            {"type": "progress", "text": "thinking"},
            {"type": "result", "structured_output": {"candidates": ["X"]}}
        ],
        "stderr": "optional stderr text before exit",
        "exit_code": 0,            # default 0
        "sleep_before_result": 0,  # seconds (float); used for timeout tests
        "emit_bad_json_line": false  # if true, emit "not json" before events
    }

Environment:
    FAKE_CLAUDE_SCRIPT  — path to the script JSON (required)
    FAKE_CLAUDE_ARGV_OUT — optional path; argv written here as JSON

Kept deliberately dumb: this is a test double, not a real CLI.
"""
from __future__ import annotations

import json
import os
import sys
import time


def main() -> int:
    argv = sys.argv[:]
    argv_out = os.environ.get("FAKE_CLAUDE_ARGV_OUT")
    if argv_out:
        with open(argv_out, "w", encoding="utf-8") as f:
            json.dump(argv, f)

    script_path = os.environ.get("FAKE_CLAUDE_SCRIPT")
    if not script_path:
        sys.stderr.write("fake_claude_bin: FAKE_CLAUDE_SCRIPT not set\n")
        return 2

    with open(script_path, "r", encoding="utf-8") as f:
        script = json.load(f)

    if script.get("emit_bad_json_line"):
        sys.stdout.write("this is definitely not json\n")
        sys.stdout.flush()

    events = script.get("events", [])
    sleep_before_result = float(script.get("sleep_before_result", 0) or 0)

    for evt in events:
        if (
            sleep_before_result > 0
            and evt.get("type") == "result"
        ):
            time.sleep(sleep_before_result)
        sys.stdout.write(json.dumps(evt) + "\n")
        sys.stdout.flush()

    stderr_text = script.get("stderr")
    if stderr_text:
        sys.stderr.write(stderr_text)
        sys.stderr.flush()

    return int(script.get("exit_code", 0) or 0)


if __name__ == "__main__":
    sys.exit(main())
