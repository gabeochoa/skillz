#!/usr/bin/env python3
"""
Run layout audit on collected QA screenshots.

Phase 2 of the layout QA pipeline:
1. Read manifest.json from collect_qa_screenshots.py
2. Split screens into batches
3. Fan out to AI auditors (Claude CLI, Cursor, or manual)
4. Consolidate findings

Supports --backend claude (Claude CLI), cursor (Cursor subagents), manual (prompt files).
"""

import argparse
import json
import math
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed


def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", file=sys.stderr)


DEFAULT_FOCUS = """Focus exclusively on LAYOUT correctness. For each screenshot:

1. CORNERS: Are container corners clean? No content bleeding past rounded corners or border edges.
2. CONTAINER BOUNDS: Are containers sized correctly? No unexpected expansion pushing elements off-screen.
3. OVERFLOW: Does any content overflow its parent container? Check text, images, and child elements.
4. OVERLAP: Are any elements overlapping unintentionally? Check for z-order issues and misaligned siblings.

Do NOT flag color, contrast, font choice, or accessibility concerns. Only report layout/spatial issues."""


def build_audit_prompt(screen_name, screenshot_paths, focus, output_path):
    """Build the prompt for a single screen audit."""
    screenshot_list = "\n".join(f"  - {p}" for p in screenshot_paths)

    return f"""You are auditing the UI layout of the screen "{screen_name}".

Read and examine each of these screenshot images:
{screenshot_list}

{focus}

For each issue found, provide:
- Type (corners | container_bounds | overflow | overlap)
- Which screenshot shows it
- Specific location in the screenshot
- Suggested fix

If no issues are found, state that the screen passes layout QA.

Rank issues from most impactful to least impactful.

Write your findings in markdown format to: {output_path}

Use this format:

# Layout QA: {screen_name}

**Screenshots analyzed:** {len(screenshot_paths)}

## Issues Found

### 1. {{Title}}
**Type:** {{type}}
**Screenshot:** {{filename}}
**Detail:** {{Specific observation}}
**Suggested fix:** {{Actionable recommendation}}

(or "## No Issues Found" if the screen passes)
"""


def build_batch_prompt(batch, focus, output_dir):
    """Build a combined prompt for a batch of screens."""
    sections = []
    for screen_name, screenshot_paths in batch:
        output_path = os.path.join(output_dir, f"{screen_name}_layout_qa.md")
        sections.append(build_audit_prompt(
            screen_name, screenshot_paths, focus, output_path
        ))

    return "\n\n---\n\n".join(sections)


def run_claude_batch(batch_info):
    """Run a single batch through Claude CLI. Called in subprocess."""
    batch_id, batch, focus, output_dir, project_root = batch_info

    screen_names = [s[0] for s in batch]
    log(f"[Batch {batch_id}] Starting: {', '.join(screen_names)}")

    prompt = build_batch_prompt(batch, focus, output_dir)

    screenshot_dirs = set()
    for _, paths in batch:
        for p in paths:
            screenshot_dirs.add(os.path.dirname(p))

    cmd = [
        "claude", "-p",
        "--allowedTools", "Read,Write",
        "--dangerously-skip-permissions",
    ]
    for d in screenshot_dirs:
        cmd.extend(["--add-dir", d])
    cmd.extend(["--add-dir", output_dir])

    cmd.append(prompt)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            timeout=300,
            cwd=project_root,
        )

        if result.returncode != 0:
            log(f"[Batch {batch_id}] WARNING: claude exited with {result.returncode}")
            if result.stderr:
                log(f"[Batch {batch_id}] stderr: {result.stderr[:200]}")

        written = []
        for screen_name, _ in batch:
            out_file = os.path.join(output_dir, f"{screen_name}_layout_qa.md")
            if os.path.isfile(out_file):
                written.append(screen_name)

        if not written:
            for screen_name, _ in batch:
                out_file = os.path.join(output_dir, f"{screen_name}_layout_qa.md")
                with open(out_file, "w") as f:
                    content = result.stdout if result.stdout else "(no output from claude)"
                    f.write(f"# Layout QA: {screen_name}\n\n{content}\n")
                written.append(screen_name)

        log(f"[Batch {batch_id}] Done: wrote {len(written)}/{len(batch)} reports")
        return batch_id, written

    except subprocess.TimeoutExpired:
        log(f"[Batch {batch_id}] ERROR: timed out after 300s")
        return batch_id, []
    except Exception as e:
        log(f"[Batch {batch_id}] ERROR: {e}")
        return batch_id, []


def run_cursor_batch(batch, focus, output_dir):
    """Write prompt files for Cursor subagents to pick up."""
    prompts_dir = os.path.join(output_dir, "_prompts")
    os.makedirs(prompts_dir, exist_ok=True)

    for screen_name, screenshot_paths in batch:
        output_path = os.path.join(output_dir, f"{screen_name}_layout_qa.md")
        prompt = build_audit_prompt(screen_name, screenshot_paths, focus, output_path)
        prompt_file = os.path.join(prompts_dir, f"{screen_name}_prompt.md")
        with open(prompt_file, "w") as f:
            f.write(prompt)

    return prompts_dir


def run_manual_batch(batch, focus, output_dir):
    """Write a combined prompt file for manual copy-paste."""
    prompt = build_batch_prompt(batch, focus, output_dir)
    manual_file = os.path.join(output_dir, "_manual_prompt.md")
    with open(manual_file, "w") as f:
        f.write(prompt)
    return manual_file


def consolidate_reports(output_dir, screen_names):
    """Read per-screen reports and produce a consolidated report."""
    all_issues = []

    for screen in screen_names:
        report_path = os.path.join(output_dir, f"{screen}_layout_qa.md")
        if not os.path.isfile(report_path):
            continue

        with open(report_path, "r") as f:
            content = f.read()

        if "No Issues Found" in content or "passes layout QA" in content.lower():
            continue

        issues_in_screen = []
        current_issue = None
        for line in content.split("\n"):
            if line.startswith("### "):
                if current_issue:
                    issues_in_screen.append(current_issue)
                current_issue = {"title": line.lstrip("# ").strip(),
                                 "screen": screen, "lines": []}
            elif current_issue:
                current_issue["lines"].append(line)
                if line.startswith("**Type:**"):
                    current_issue["type"] = line.replace("**Type:**", "").strip()

        if current_issue:
            issues_in_screen.append(current_issue)
        all_issues.extend(issues_in_screen)

    type_counts = {}
    type_screens = {}
    for issue in all_issues:
        t = issue.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        if t not in type_screens:
            type_screens[t] = set()
        type_screens[t].add(issue["screen"])

    sorted_types = sorted(type_counts.keys(), key=lambda t: type_counts[t], reverse=True)

    report = ["# Layout QA Consolidated Report\n"]
    report.append(f"**Screens audited:** {len(screen_names)}")
    report.append(f"**Total issues found:** {len(all_issues)}")
    report.append(f"**Screens with issues:** "
                  f"{len(set(i['screen'] for i in all_issues))}\n")

    report.append("| Type | Count | Screens Affected |")
    report.append("|------|-------|-----------------|")
    for t in sorted_types:
        report.append(f"| {t} | {type_counts[t]} | {len(type_screens[t])} |")
    report.append("")

    for t in sorted_types:
        report.append(f"## {t.replace('_', ' ').title()} Issues ({type_counts[t]})\n")
        for issue in all_issues:
            if issue.get("type") == t:
                report.append(f"### {issue['screen']}: {issue['title']}")
                report.append("\n".join(issue["lines"]))
                report.append("")

    consolidated_path = os.path.join(output_dir, "consolidated_layout_qa.md")
    with open(consolidated_path, "w") as f:
        f.write("\n".join(report))

    log(f"Consolidated report: {consolidated_path}")
    log(f"  {len(all_issues)} issues across "
        f"{len(set(i['screen'] for i in all_issues))} screens")
    return consolidated_path


def main():
    parser = argparse.ArgumentParser(
        description="Run layout audit on collected QA screenshots"
    )
    parser.add_argument("--manifest", default="/tmp/ui_qa_audit/manifest.json",
                        help="Path to manifest.json from collection phase")
    parser.add_argument("--backend", choices=["claude", "cursor", "manual"],
                        default="claude",
                        help="Audit backend (default: claude)")
    parser.add_argument("--parallel", type=int, default=10,
                        help="Number of parallel audit processes (default: 10)")
    parser.add_argument("--screen", help="Audit a single screen only")
    parser.add_argument("--focus", default=DEFAULT_FOCUS,
                        help="Custom audit focus prompt")
    parser.add_argument("--output", default="docs/layout_qa",
                        help="Output directory for reports (default: docs/layout_qa)")
    args = parser.parse_args()

    log("=" * 60)
    log("Layout QA Audit")
    log(f"Backend: {args.backend} | Parallel: {args.parallel}")
    log("=" * 60)

    if not os.path.isfile(args.manifest):
        log(f"ERROR: Manifest not found at {args.manifest}")
        log("Run collect_qa_screenshots.py first.")
        return 1

    with open(args.manifest, "r") as f:
        manifest = json.load(f)

    if args.screen:
        if args.screen not in manifest:
            log(f"ERROR: Screen '{args.screen}' not in manifest. "
                f"Available: {', '.join(sorted(manifest.keys()))}")
            return 1
        manifest = {args.screen: manifest[args.screen]}

    log(f"Screens: {len(manifest)}")
    log(f"Total screenshots: {sum(len(v) for v in manifest.values())}")

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    screens = sorted(manifest.items())
    project_root = os.getcwd()

    if args.backend == "claude":
        batch_size = max(1, math.ceil(len(screens) / args.parallel))
        batches = []
        for i in range(0, len(screens), batch_size):
            batch = screens[i:i + batch_size]
            batches.append((len(batches) + 1, batch, args.focus,
                            output_dir, project_root))

        log(f"Split into {len(batches)} batches of ~{batch_size} screens")

        workers = min(args.parallel, len(batches))
        log(f"Launching {workers} Claude processes...\n")

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(run_claude_batch, b): b[0] for b in batches
            }
            completed = 0
            for future in as_completed(futures):
                batch_id, written = future.result()
                completed += 1
                log(f"Progress: {completed}/{len(batches)} batches complete")

    elif args.backend == "cursor":
        batch_size = max(1, math.ceil(len(screens) / args.parallel))
        for i in range(0, len(screens), batch_size):
            batch = screens[i:i + batch_size]
            prompts_dir = run_cursor_batch(batch, args.focus, output_dir)

        log(f"Wrote prompt files to {prompts_dir}")
        log("Open each prompt file in Cursor and run as a subagent.")

    elif args.backend == "manual":
        manual_file = run_manual_batch(screens, args.focus, output_dir)
        log(f"Wrote manual prompt to {manual_file}")
        log("Copy the prompt and paste into your preferred AI tool.")

    log("\n--- Consolidating ---")
    screen_names = [s[0] for s in screens]
    consolidated = consolidate_reports(output_dir, screen_names)

    log("")
    log("=" * 60)
    log(f"Audit complete. Report: {consolidated}")
    log("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
