---
name: layout-qa
description: "Automated layout QA pipeline. Captures screenshots via e2e tests, fans out to AI auditors checking corners, container bounds, overflow, and element overlap. Works with any project that has an executable and .e2e test files."
---

# Layout QA: Automated Visual Layout Audit

Capture screenshots via e2e tests and audit them for layout correctness: corners, container bounds, overflow, and element overlap.

## When to Use

- `/layout-qa` -- Full layout audit of all screens
- `/layout-qa:screen <name>` -- Audit a single screen
- `/layout-qa:collect` -- Phase 1 only (capture screenshots, write manifest)
- `/layout-qa:audit` -- Phase 2 only (run audit on existing manifest)
- After adding or modifying screens, components, or layout logic
- Before a release to catch layout regressions

## Prerequisites

Scripts are located at `~/.claude/skills/layout-qa/`:
- `collect_qa_screenshots.py` -- Phase 1: screenshot collection
- `run_layout_audit.py` -- Phase 2: AI-powered audit

The project needs:
- An executable in `./output/` or `./build/` (or pass `--exe`)
- `.e2e` test files somewhere in the project tree

Optional (enhances coverage):
- `--list-screens` support on the executable (for idle screenshots)
- `screenshot_all_screens.py` in project root (for bulk idle capture)

## The Process

### Step 1: Collect Screenshots (Phase 1)

```bash
python3 ~/.claude/skills/layout-qa/collect_qa_screenshots.py
```

This will:
1. Discover the executable (auto-searches `./output/*.exe`, `./build/*.exe`)
2. Try `--list-screens` for screen discovery; falls back to parsing `.e2e` files
3. Capture idle screenshots if `--list-screens` is supported
4. Run all matching e2e tests to capture interaction-state screenshots
5. Organize into `/tmp/ui_qa_audit/{screen_name}/`
6. Write `/tmp/ui_qa_audit/manifest.json`

For a single screen:

```bash
python3 ~/.claude/skills/layout-qa/collect_qa_screenshots.py --screen forms
```

### Step 2: Run Layout Audit (Phase 2)

```bash
# Via Claude CLI (10 parallel processes)
python3 ~/.claude/skills/layout-qa/run_layout_audit.py --backend claude --parallel 10

# Via Cursor (writes prompt files for subagents)
python3 ~/.claude/skills/layout-qa/run_layout_audit.py --backend cursor

# Manual mode (writes prompts for copy-paste)
python3 ~/.claude/skills/layout-qa/run_layout_audit.py --backend manual
```

### Step 3: Review Consolidated Report

- **Consolidated:** `docs/layout_qa/consolidated_layout_qa.md`
- **Per-screen:** `docs/layout_qa/{screen_name}_layout_qa.md`

## Running from Cursor (Manual Fallback)

When the project doesn't support `--list-screens` or the automated pipeline isn't feasible, do a manual layout QA:

1. Run existing e2e tests that capture screenshots
2. Read each screenshot image
3. Check for the four layout concerns (corners, bounds, overflow, overlap)
4. Write findings to `docs/layout_qa/`

## Audit Focus

| Check | What it catches |
|-------|----------------|
| **Corners** | Content bleeding past rounded corners or border edges |
| **Container bounds** | Containers expanding unexpectedly, pushing elements off-screen |
| **Overflow** | Text, images, or child elements overflowing their parent container |
| **Overlap** | Unintentional element overlap, z-order issues, misaligned siblings |

The audit explicitly ignores color, contrast, font choice, and accessibility.

## Portability

Both scripts auto-discover project structure:

| What | Discovery order |
|------|----------------|
| Executable | `--exe` > `./output/ui_tester.exe` > `./output/*.exe` > `./build/*.exe` |
| Screens | `--list-screens` > `goto_screen` commands in `.e2e` files > `_default` bucket |
| E2E tests | `--e2e-dir` > recursive `*.e2e` search from project root |
| E2E runner | `--runner` > `scripts/run_e2e.sh` > direct executable invocation |

No project-specific paths are hardcoded.

## Output Format

**Per-screen** (`docs/layout_qa/{screen}_layout_qa.md`):

```markdown
# Layout QA: {screen_name}

**Screenshots analyzed:** N

## Issues Found

### 1. {Title}
**Type:** overflow
**Screenshot:** idle_720p.png
**Detail:** The email input extends ~12px past its card boundary.
**Suggested fix:** Add max-width constraint on the input container.
```

**Consolidated** (`docs/layout_qa/consolidated_layout_qa.md`):

```markdown
# Layout QA Consolidated Report

| Type             | Count | Screens Affected |
|------------------|-------|-----------------|
| Overflow         | 12    | 8               |
| Corner bleed     | 4     | 3               |
| Overlap          | 2     | 2               |
```
