#!/usr/bin/env python3
"""capture-screenshots — Build a macOS app, launch it, capture window screenshots.

Usage: capture_screenshots.py <project-path> <output-dir>
Requires: Xcode command line tools, screencapture (macOS)
Outputs: PNG screenshots in <output-dir>/
"""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def build_app(project_path: Path) -> str:
    """Build the app and return the path to the built artifact."""
    build_dir = project_path / ".build" / "release"

    if (project_path / "Package.swift").exists():
        subprocess.run(
            ["swift", "build", "-c", "release"],
            cwd=str(project_path), check=True,
            capture_output=True, text=True,
        )
        # Try to get app name from package description
        try:
            result = subprocess.run(
                ["swift", "package", "describe", "--type", "json"],
                cwd=str(project_path), capture_output=True, text=True,
            )
            app_name = json.loads(result.stdout)["name"]
        except Exception:
            app_name = project_path.name

        # Look for .app bundle first, fall back to executable
        app_bundles = list(build_dir.glob("*.app"))
        if app_bundles:
            return str(app_bundles[0])
        return str(build_dir / app_name)

    elif (project_path / "Makefile").exists():
        subprocess.run(
            ["make", "release"],
            cwd=str(project_path), check=True,
            capture_output=True, text=True,
        )
        app_bundles = list(project_path.rglob("*.app"))
        if app_bundles:
            return str(app_bundles[0])
        print("Build succeeded but no .app bundle found", file=sys.stderr)
        sys.exit(1)

    else:
        print(f"Cannot determine build system for {project_path}", file=sys.stderr)
        sys.exit(1)


def launch_app(app_path: str) -> int:
    """Launch the app and return its PID."""
    if Path(app_path).is_dir():
        proc = subprocess.Popen(
            ["open", "-a", app_path, "--args", "--screenshot-mode"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        proc.wait()
        # open(1) returns immediately; find the actual app process
        time.sleep(1)
        return proc.pid
    else:
        proc = subprocess.Popen(
            [app_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return proc.pid


def wait_for_window(pid: int, timeout: float = 10.0) -> int:
    """Wait for the app to show a window. Returns window count."""
    script = (
        f'tell application "System Events" to count windows of '
        f'(first process whose unix id is {pid})'
    )
    elapsed = 0.0
    while elapsed < timeout:
        time.sleep(0.5)
        elapsed += 0.5
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True,
            )
            count = int(result.stdout.strip())
            if count > 0:
                return count
        except (ValueError, subprocess.SubprocessError):
            continue
    return 0


def capture_window(pid: int, output_path: str) -> bool:
    """Capture the main window of a process. Returns True on success."""
    window_id_script = (
        f'tell application "System Events" to get id of first window of '
        f'(first process whose unix id is {pid})'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", window_id_script],
            capture_output=True, text=True,
        )
        window_id = result.stdout.strip()
        if window_id:
            subprocess.run(
                ["screencapture", "-l", window_id, output_path],
                check=True, capture_output=True,
            )
            return True
    except subprocess.SubprocessError:
        pass

    # Fallback: interactive window capture
    try:
        subprocess.run(
            ["screencapture", "-w", output_path],
            check=True, capture_output=True,
        )
        return True
    except subprocess.SubprocessError:
        return False


def get_process_name(pid: int) -> str:
    """Get the process name via AppleScript."""
    script = (
        f'tell application "System Events" to get name of '
        f'(first process whose unix id is {pid})'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True,
        )
        return result.stdout.strip()
    except subprocess.SubprocessError:
        return ""


def capture_menus(pid: int, process_name: str, output_dir: Path) -> int:
    """Capture screenshots of each menu. Returns number of captures."""
    if not process_name:
        return 0

    menu_script = (
        f'tell application "System Events"\n'
        f'  tell process "{process_name}"\n'
        f'    get name of every menu bar item of menu bar 1\n'
        f'  end tell\n'
        f'end tell'
    )
    try:
        result = subprocess.run(
            ["osascript", "-e", menu_script],
            capture_output=True, text=True,
        )
        menus = [m.strip() for m in result.stdout.strip().split(",") if m.strip()]
    except subprocess.SubprocessError:
        return 0

    num = 2
    for menu in menus:
        if menu == "Apple":
            continue

        click_script = (
            f'tell application "System Events"\n'
            f'  tell process "{process_name}"\n'
            f'    click menu bar item "{menu}" of menu bar 1\n'
            f'  end tell\n'
            f'end tell'
        )
        try:
            subprocess.run(["osascript", "-e", click_script], capture_output=True)
        except subprocess.SubprocessError:
            continue

        time.sleep(0.5)
        output_path = str(output_dir / f"{num:02d}-menu-{menu}.png")
        try:
            subprocess.run(["screencapture", output_path], capture_output=True)
        except subprocess.SubprocessError:
            pass
        num += 1

        # Press Escape to close menu
        try:
            subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to key code 53'],
                capture_output=True,
            )
        except subprocess.SubprocessError:
            pass
        time.sleep(0.3)

    return num - 2


def kill_app(pid: int) -> None:
    """Terminate the app process."""
    try:
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)
    except (OSError, ChildProcessError):
        pass


def main():
    if len(sys.argv) < 3:
        print("Usage: capture_screenshots.py <project-path> <output-dir>", file=sys.stderr)
        sys.exit(1)

    project_path = Path(sys.argv[1]).resolve()
    output_dir = Path(sys.argv[2]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build
    print(f"Building app at {project_path}...", file=sys.stderr)
    app_path = build_app(project_path)

    if not Path(app_path).exists():
        print("Build succeeded but no app found at expected location", file=sys.stderr)
        sys.exit(1)

    # Launch
    print(f"Launching {app_path}...", file=sys.stderr)
    pid = launch_app(app_path)

    # Wait for window
    window_count = wait_for_window(pid)
    if window_count == 0:
        print("App launched but no windows appeared after 10 seconds", file=sys.stderr)
        kill_app(pid)
        sys.exit(1)

    # Capture main window
    print("Capturing launch state...", file=sys.stderr)
    time.sleep(1)
    capture_window(pid, str(output_dir / "01-launch-state.png"))

    # Capture menus
    process_name = get_process_name(pid)
    capture_menus(pid, process_name, output_dir)

    # Quit
    print("Quitting app...", file=sys.stderr)
    kill_app(pid)

    screenshots = list(output_dir.glob("*.png"))
    print(f"Captured screenshots in {output_dir}", file=sys.stderr)
    print(f"Total screenshots: {len(screenshots)}", file=sys.stderr)


if __name__ == "__main__":
    main()
