#!/usr/bin/env python3
"""Dev-Team Dashboard lifecycle management.

Usage: server.py start|stop|status|restart [--port PORT]
"""

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = Path.home() / ".agentic-cookbook" / "dev-team"
PID_FILE = DATA_DIR / "dashboard.pid"
LOG_FILE = DATA_DIR / "dashboard.log"
DEFAULT_PORT = 9876


def get_port(args: list[str]) -> int:
    """Extract --port value from args, or use env/default."""
    for i, arg in enumerate(args):
        if arg == "--port" and i + 1 < len(args):
            return int(args[i + 1])
    return int(os.environ.get("DEVTEAM_DASHBOARD_PORT", str(DEFAULT_PORT)))


def is_running() -> tuple[bool, int]:
    """Check if the dashboard is running. Returns (running, pid)."""
    if not PID_FILE.exists():
        return False, 0
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return True, pid
    except (ValueError, OSError):
        return False, 0


def start(port: int) -> None:
    running, pid = is_running()
    if running:
        print(f"Dashboard already running (PID {pid}) on port {port}")
        print(f"  http://127.0.0.1:{port}")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Starting dev-team dashboard on port {port}...")
    env = os.environ.copy()
    env["DEVTEAM_DASHBOARD_PORT"] = str(port)

    with open(LOG_FILE, "w") as log:
        proc = subprocess.Popen(
            [sys.executable, "-m", "services.dashboard"],
            cwd=str(PROJECT_ROOT),
            stdout=log,
            stderr=log,
            env=env,
        )

    PID_FILE.write_text(str(proc.pid))
    time.sleep(1)

    try:
        os.kill(proc.pid, 0)
        print(f"Dashboard running (PID {proc.pid})")
        print(f"  http://127.0.0.1:{port}")
        if shutil.which("open"):
            subprocess.Popen(
                ["open", f"http://127.0.0.1:{port}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except OSError:
        print(f"Failed to start. Check {LOG_FILE}", file=sys.stderr)
        PID_FILE.unlink(missing_ok=True)
        sys.exit(1)


def stop() -> None:
    running, pid = is_running()
    if not running:
        print("Dashboard not running.")
        PID_FILE.unlink(missing_ok=True)
        return

    print(f"Stopping dashboard (PID {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
    PID_FILE.unlink(missing_ok=True)
    print("Stopped.")


def status(port: int) -> None:
    running, pid = is_running()
    if running:
        print(f"Dashboard running (PID {pid})")
        print(f"  http://127.0.0.1:{port}")
    else:
        print("Dashboard not running.")
        PID_FILE.unlink(missing_ok=True)


def main():
    args = sys.argv[1:]
    port = get_port(args)

    # Extract command (first non-flag argument)
    cmd = "status"
    for arg in args:
        if arg in ("start", "stop", "status", "restart"):
            cmd = arg
            break

    if cmd == "start":
        start(port)
    elif cmd == "stop":
        stop()
    elif cmd == "status":
        status(port)
    elif cmd == "restart":
        stop()
        time.sleep(1)
        start(port)
    else:
        print(f"Usage: {Path(__file__).name} start|stop|status|restart [--port PORT]")
        sys.exit(1)


if __name__ == "__main__":
    main()
