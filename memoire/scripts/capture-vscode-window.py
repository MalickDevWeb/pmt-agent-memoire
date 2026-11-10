#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

from PIL import ImageGrab


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def check_output(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True)


def current_windows() -> set[str]:
    try:
        raw = check_output(["wmctrl", "-lx"])
    except Exception:
        raw = ""
    return {line.split()[0] for line in raw.splitlines() if line.strip()}


def wait_for_new_window(before: set[str], timeout_s: float) -> str:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        raw = check_output(["wmctrl", "-lx"])
        for line in raw.splitlines():
            if "code.Code" not in line:
                continue
            window_id = line.split()[0]
            if window_id not in before:
                return window_id
        time.sleep(0.3)
    raise RuntimeError("VS Code window not found")


def read_geometry(window_id: str) -> tuple[int, int, int, int]:
    info = check_output(["xwininfo", "-id", window_id])
    abs_x = abs_y = width = height = None
    for line in info.splitlines():
        line = line.strip()
        if line.startswith("Absolute upper-left X:"):
            abs_x = int(line.split(":", 1)[1].strip())
        elif line.startswith("Absolute upper-left Y:"):
            abs_y = int(line.split(":", 1)[1].strip())
        elif line.startswith("Width:"):
            width = int(line.split(":", 1)[1].strip())
        elif line.startswith("Height:"):
            height = int(line.split(":", 1)[1].strip())
    if None in (abs_x, abs_y, width, height):
        raise RuntimeError(f"Could not read geometry for {window_id}")
    return abs_x, abs_y, width, height


def close_window(window_id: str) -> None:
    run(["wmctrl", "-ic", window_id], check=False)


def ensure_profile(profile_dir: Path) -> None:
    user_dir = profile_dir / "User"
    user_dir.mkdir(parents=True, exist_ok=True)
    settings = {
        "workbench.colorTheme": "Default Dark Modern",
        "workbench.startupEditor": "none",
        "workbench.activityBar.location": "hidden",
        "workbench.statusBar.visible": False,
        "window.commandCenter": False,
        "breadcrumbs.enabled": False,
        "editor.minimap.enabled": False,
        "editor.stickyScroll.enabled": False,
        "editor.wordWrap": "off",
        "editor.glyphMargin": False,
        "editor.lineNumbers": "on",
        "editor.fontSize": 13,
        "editor.lineHeight": 21,
        "window.zoomLevel": 0,
    }
    (user_dir / "settings.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--line", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=1760)
    parser.add_argument("--height", type=int, default=1100)
    parser.add_argument("--x", type=int, default=70)
    parser.add_argument("--y", type=int, default=40)
    parser.add_argument("--display", default=":0")
    parser.add_argument("--profile-dir", default="/tmp/vscode_capture_profile")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    os.environ["DISPLAY"] = args.display

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    profile_dir = Path(args.profile_dir).resolve()
    ensure_profile(profile_dir)

    before = current_windows()
    proc = run(
        [
            "code",
            "--user-data-dir",
            str(profile_dir),
            "--disable-extensions",
            "--new-window",
            "--goto",
            f"{source}:{args.line}:1",
        ]
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "Failed to launch VS Code")

    window_id = wait_for_new_window(before, args.timeout)
    run(["wmctrl", "-ir", window_id, "-e", f"0,{args.x},{args.y},{args.width},{args.height}"])
    run(["wmctrl", "-ia", window_id])
    time.sleep(1.8)

    abs_x, abs_y, width, height = read_geometry(window_id)
    bbox = (abs_x + 1, abs_y + 1, abs_x + width - 1, abs_y + height - 1)
    image = ImageGrab.grab(bbox=bbox)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    close_window(window_id)

    print(output)


if __name__ == "__main__":
    main()
