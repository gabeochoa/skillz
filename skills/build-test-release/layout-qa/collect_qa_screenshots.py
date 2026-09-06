#!/usr/bin/env python3
"""
Collect QA screenshots for layout audit.

Phase 1 of the layout QA pipeline:
1. Capture idle screenshots of all screens via screenshot_all_screens.py
2. Parse .e2e files to build screen-to-test mapping
3. Run matching e2e tests to capture interaction screenshots
4. Organize everything into per-screen directories with a manifest

Portable across UI projects -- auto-discovers executable, e2e tests, and runner.
"""

import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time


def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", file=sys.stderr)


def find_executable(explicit_path=None):
    """Discover the UI executable."""
    candidates = []
    if explicit_path:
        candidates.append(explicit_path)
    candidates.append("./output/ui_tester.exe")

    for d in ["./output", "./build"]:
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".exe"):
                    candidates.append(os.path.join(d, f))

    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            log(f"Found executable: {c}")
            return c

    return None


def find_e2e_files(explicit_dir=None, project_root="."):
    """Discover all .e2e test files."""
    if explicit_dir:
        search_dir = explicit_dir
    else:
        search_dir = project_root

    e2e_files = []
    for root, _dirs, files in os.walk(search_dir):
        for f in sorted(files):
            if f.endswith(".e2e"):
                e2e_files.append(os.path.join(root, f))

    log(f"Found {len(e2e_files)} e2e test files")
    return e2e_files


def find_runner(explicit_runner=None, executable=None):
    """Discover how to run e2e tests."""
    if explicit_runner and os.path.isfile(explicit_runner):
        return {"type": "script", "path": explicit_runner}

    script = "scripts/run_e2e.sh"
    if os.path.isfile(script):
        return {"type": "script", "path": script}

    if executable:
        return {"type": "direct", "path": executable}

    return None


def get_screen_names(executable):
    """Get available screen names from the executable.
    Falls back to returning None if --list-screens isn't supported."""
    try:
        result = subprocess.run(
            [executable, "--list-screens"],
            capture_output=True, text=True, timeout=10
        )
        names = []
        for line in result.stdout.split("\n"):
            match = re.search(r"--screen=(\S+)", line)
            if match:
                names.append(match.group(1))
        if names:
            names.sort()
            log(f"Found {len(names)} screens via --list-screens")
            return names
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        log(f"--list-screens not available: {e}")
    return None


def discover_screens_from_e2e(e2e_files):
    """Discover screen names from e2e test files (goto_screen commands)."""
    screens = set()
    for filepath in e2e_files:
        with open(filepath, "r") as f:
            for line in f:
                match = re.match(r"\s*goto_screen\s+(\S+)", line.strip())
                if match:
                    screens.add(match.group(1))
    if screens:
        log(f"Discovered {len(screens)} screens from e2e files")
    return sorted(screens)


def parse_e2e_mapping(e2e_files):
    """Parse e2e files to build screen -> [test_files] and test -> [screenshot_names] maps."""
    screen_to_tests = {}
    test_to_screenshots = {}

    for filepath in e2e_files:
        screens_in_test = set()
        screenshots_in_test = []
        current_screen = None

        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue

                goto_match = re.match(r"goto_screen\s+(\S+)", line)
                if goto_match:
                    current_screen = goto_match.group(1)
                    screens_in_test.add(current_screen)

                screenshot_match = re.match(r"screenshot\s+(\S+)", line)
                if screenshot_match:
                    name = screenshot_match.group(1)
                    screenshots_in_test.append({
                        "name": name,
                        "screen": current_screen,
                    })

        for screen in screens_in_test:
            if screen not in screen_to_tests:
                screen_to_tests[screen] = []
            screen_to_tests[screen].append(filepath)

        test_to_screenshots[filepath] = screenshots_in_test

    return screen_to_tests, test_to_screenshots


def capture_idle_screenshots(executable, screen_names, output_dir):
    """Capture idle screenshots using screenshot_all_screens.py if available,
    otherwise fall back to running the app directly."""
    idle_dir = os.path.join(output_dir, "_idle")
    os.makedirs(idle_dir, exist_ok=True)

    script = "screenshot_all_screens.py"
    if os.path.isfile(script):
        log("Capturing idle screenshots via screenshot_all_screens.py --quick...")
        result = subprocess.run(
            [sys.executable, script, "--quick"],
            capture_output=True, text=True, timeout=600
        )
        if result.returncode != 0:
            log(f"WARNING: screenshot_all_screens.py exited with {result.returncode}")
            log(result.stderr[-500:] if result.stderr else "(no stderr)")

        src_dir = "/tmp/ui_showcase_screenshots"
        if os.path.isdir(src_dir):
            count = 0
            for screen in screen_names:
                src = os.path.join(src_dir, f"{screen}_720p.png")
                if os.path.isfile(src):
                    dst = os.path.join(idle_dir, f"{screen}_idle_720p.png")
                    shutil.copy2(src, dst)
                    count += 1
            log(f"Copied {count}/{len(screen_names)} idle screenshots")
            return True

    log("screenshot_all_screens.py not available, capturing via e2e fallback...")
    capture_e2e = []
    for screen in screen_names:
        capture_e2e.append(f"goto_screen {screen}")
        capture_e2e.append("wait 0.5")
        capture_e2e.append(f"screenshot {screen}_idle_720p")

    tmpfile = os.path.join(output_dir, "_idle_capture.e2e")
    with open(tmpfile, "w") as f:
        f.write("\n".join(capture_e2e) + "\n")

    result = subprocess.run(
        [executable, "--test-script", tmpfile, "--timeout", "3000",
         "-w", "1280", "-h", "720"],
        capture_output=True, text=True, timeout=600
    )

    if result.returncode != 0:
        log(f"WARNING: idle capture exited with {result.returncode}")

    count = 0
    for screen in screen_names:
        src = f"/tmp/e2e_screenshot_{screen}_idle_720p.png"
        if os.path.isfile(src):
            dst = os.path.join(idle_dir, f"{screen}_idle_720p.png")
            shutil.copy2(src, dst)
            count += 1

    os.remove(tmpfile)
    log(f"Captured {count}/{len(screen_names)} idle screenshots via fallback")
    return count > 0


def run_e2e_tests(runner, e2e_files, test_to_screenshots, output_dir):
    """Run e2e tests and collect their screenshots."""
    tests_run = 0
    screenshots_collected = 0
    already_run = set()

    for filepath in e2e_files:
        if filepath in already_run:
            continue
        already_run.add(filepath)

        basename = os.path.basename(filepath)
        log(f"Running e2e test: {basename}")

        try:
            if runner["type"] == "script":
                result = subprocess.run(
                    ["bash", runner["path"], "--script", filepath,
                     "--timeout", "600"],
                    capture_output=True, text=True, timeout=120
                )
            else:
                result = subprocess.run(
                    [runner["path"], "--test-script", filepath,
                     "--timeout", "600", "-w", "1280", "-h", "720"],
                    capture_output=True, text=True, timeout=120
                )

            if result.returncode != 0:
                log(f"  WARNING: {basename} exited with {result.returncode}")

            tests_run += 1
        except subprocess.TimeoutExpired:
            log(f"  WARNING: {basename} timed out")
            continue
        except Exception as e:
            log(f"  ERROR running {basename}: {e}")
            continue

        for shot in test_to_screenshots.get(filepath, []):
            src = f"/tmp/e2e_screenshot_{shot['name']}.png"
            if os.path.isfile(src) and shot["screen"]:
                screen_dir = os.path.join(output_dir, shot["screen"])
                os.makedirs(screen_dir, exist_ok=True)
                dst = os.path.join(screen_dir, f"{shot['name']}.png")
                shutil.copy2(src, dst)
                screenshots_collected += 1

    log(f"Ran {tests_run} e2e tests, collected {screenshots_collected} screenshots")
    return tests_run, screenshots_collected


def organize_idle_into_screens(output_dir, screen_names):
    """Move idle screenshots from _idle/ into per-screen directories."""
    idle_dir = os.path.join(output_dir, "_idle")
    if not os.path.isdir(idle_dir):
        return

    for screen in screen_names:
        src = os.path.join(idle_dir, f"{screen}_idle_720p.png")
        if os.path.isfile(src):
            screen_dir = os.path.join(output_dir, screen)
            os.makedirs(screen_dir, exist_ok=True)
            dst = os.path.join(screen_dir, "idle_720p.png")
            shutil.copy2(src, dst)


def write_manifest(output_dir, screen_names):
    """Write manifest.json mapping each screen to its screenshot paths."""
    manifest = {}
    for screen in screen_names:
        screen_dir = os.path.join(output_dir, screen)
        if not os.path.isdir(screen_dir):
            continue
        shots = sorted(
            f for f in os.listdir(screen_dir) if f.endswith(".png")
        )
        if shots:
            manifest[screen] = [
                os.path.join(screen_dir, s) for s in shots
            ]

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    log(f"Wrote manifest: {len(manifest)} screens, "
        f"{sum(len(v) for v in manifest.values())} total screenshots")
    return manifest_path


def main():
    parser = argparse.ArgumentParser(
        description="Collect QA screenshots for layout audit"
    )
    parser.add_argument("--exe", help="Path to UI executable")
    parser.add_argument("--e2e-dir", help="Directory containing .e2e test files")
    parser.add_argument("--runner", help="Path to e2e runner script")
    parser.add_argument("--screen", help="Collect for a single screen only")
    parser.add_argument("--output", default="/tmp/ui_qa_audit",
                        help="Output directory (default: /tmp/ui_qa_audit)")
    parser.add_argument("--skip-idle", action="store_true",
                        help="Skip idle screenshot capture")
    parser.add_argument("--skip-e2e", action="store_true",
                        help="Skip e2e test execution")
    args = parser.parse_args()

    log("=" * 60)
    log("Layout QA Screenshot Collection")
    log("=" * 60)

    executable = find_executable(args.exe)
    if not executable:
        log("ERROR: No executable found. Use --exe to specify.")
        return 1

    e2e_files = find_e2e_files(args.e2e_dir)
    screen_to_tests, test_to_screenshots = parse_e2e_mapping(e2e_files)

    screen_names = get_screen_names(executable)
    has_list_screens = screen_names is not None

    if not has_list_screens:
        screen_names = discover_screens_from_e2e(e2e_files)
        if not screen_names:
            screen_names = ["_default"]
            log("No screens discovered, using '_default' bucket for all screenshots")

    if args.screen:
        if args.screen not in screen_names:
            log(f"ERROR: Screen '{args.screen}' not found. "
                f"Available: {', '.join(screen_names)}")
            return 1
        screen_names = [args.screen]
        log(f"Single screen mode: {args.screen}")

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    if args.screen:
        relevant_tests = set(screen_to_tests.get(args.screen, []))
        e2e_files = [f for f in e2e_files if f in relevant_tests]

    runner = find_runner(args.runner, executable)

    log(f"Executable: {executable}")
    log(f"Screens: {len(screen_names)} ({'--list-screens' if has_list_screens else 'e2e discovery'})")
    log(f"E2E tests: {len(e2e_files)}")
    log(f"Output: {output_dir}")
    log("=" * 60)

    if not args.skip_idle and has_list_screens:
        log("\n--- Pass 1: Idle screenshots ---")
        capture_idle_screenshots(executable, screen_names, output_dir)
    elif not args.skip_idle and not has_list_screens:
        log("Skipping idle screenshots (--list-screens not supported)")

    if not args.skip_e2e and e2e_files and runner:
        log("\n--- Pass 2: E2E test screenshots ---")
        if has_list_screens:
            tests_to_run = set()
            for screen in screen_names:
                for test in screen_to_tests.get(screen, []):
                    tests_to_run.add(test)
            run_e2e_tests(runner, sorted(tests_to_run),
                          test_to_screenshots, output_dir)
        else:
            run_e2e_tests(runner, sorted(e2e_files),
                          test_to_screenshots, output_dir)
    elif not runner:
        log("WARNING: No e2e runner found, skipping e2e tests")

    log("\n--- Organizing ---")
    if has_list_screens:
        organize_idle_into_screens(output_dir, screen_names)
    manifest_path = write_manifest(output_dir, screen_names)

    log("")
    log("=" * 60)
    log(f"Collection complete. Manifest: {manifest_path}")
    log("Next step: python3 run_layout_audit.py --backend claude --parallel 10")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
