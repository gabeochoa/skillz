---
name: ui-capture-cdp
description: >
  Capture pixel-perfect, real UI screenshots and animated transient states from a web app by
  driving a launched Chrome over raw Chrome DevTools Protocol (CDP). This bypasses the
  agent browser-node allowlist (which blocks Fetch.*/Network.*), enabling request interception to
  FREEZE sub-second loading/transient states and photograph them — or burst-capture a running
  CSS animation (e.g. a spinner) into a loopable frame set. Use when building product/feature
  demo videos, capturing UI states for docs, photographing loading/skeleton/transient states,
  or automating clean UI screenshots without touching the user's real browser. Also applies when
  the user says "capture the UI", "screenshot the app", "freeze the loading state", "capture the
  spinner", "record the flow", "launched chrome", "CDP capture", "Fetch.requestPaused", "demo
  frames", or "capture that transient state". Companion to demo-video-assembly and
  feature-demo-studio. Runs on a CLI node (the machine with Chrome).
node: cli
---

# UI Capture via Launched-Chrome CDP

The reliable way to capture **real, high-quality UI frames** — including states that flash for
milliseconds — for demo videos and docs. No synthetic mockups.

## Why launched Chrome (not the browser node)

Agent browser-extension nodes commonly block `Fetch.*` and `Network.*` CDP methods (safety policy:
it drives your *real* logged-in Chrome). That makes it impossible to pause a request and
photograph a transient loading state.

A Chrome **you launch yourself** with `--remote-debugging-port` is a plain CDP target — the
allowlist never applies. Full `Fetch.*` interception is available. Using a throwaway
`--user-data-dir` means no personal tabs/DMs are present (this is also why macOS `screencapture`
is banned — it can leak private windows). Page-scoped CDP screenshots only ever see the target page.

## Core capabilities

| Goal | Tool | Technique |
|------|------|-----------|
| Launch capture Chrome | `launch_chrome.sh` | isolated profile, debug port |
| Freeze a transient state | `freeze_capture.mjs` | `Fetch.requestPaused` holds the API call; screenshot; `continueRequest` |
| Animate a transient (spinner) | `burst_capture.mjs` | CSS animation keeps running while frozen → N rapid screenshots = one loop cycle |
| Drive clicks / navigation | `cdp_lib.mjs` (`click`, `evalJS`) | `Input.dispatchMouseEvent`, `Runtime.evaluate` |

## Workflow

### 1. Launch the capture Chrome
```bash
bash launch_chrome.sh "https://your-app.example.com" 9222 1280,860
```
The window opens with a fresh profile — **log in once** (the user does this; ask them).
Server-side UI (sidebars, workspaces) rebuilds identically to their normal session.

### 2. Verify login state
```bash
curl -s http://127.0.0.1:9222/json | python3 -c "import sys,json;[print(t['title'],'|',t['url'][:80]) for t in json.load(sys.stdin) if t.get('type')=='page']"
```

### 3a. Freeze a one-shot transient
```bash
node freeze_capture.mjs \
  --url "https://app/?param=..." \
  --pattern "*/api/the/slow/endpoint*" \
  --wait-text "Loading…" \
  --out ~/frames/loading.png
```

### 3b. Burst-capture an animation (spinner)
```bash
node burst_capture.mjs \
  --url "https://app/?param=..." \
  --pattern "*/api/the/slow/endpoint*" \
  --wait-text "Determining…" \
  --outdir ~/frames/spinner --n 16 --gap 70
```
Loop the resulting `frame_00..15.png` in the video to show a live-spinning state instead of a
frozen one. (A `lucide` `animate-spin` = 1s/rev, so ~16 frames over ~1.1s = a smooth loop.)

### 3c. Drive a flow (click toggles, dialogs, send buttons)
Use `cdp_lib.mjs` in a small script: `connect()` → `attach({match|fresh})` → `evalJS` to locate
an element's center coords → `click(S,x,y)` → screenshot each state.

## Key rules

- **Real UI only.** Capture genuine app states. The only acceptable composited pixels are true
  *browser chrome* (address bar) that is not itself a product UI state.
- **Never macOS `screencapture`** — risks capturing the wrong window / private content.
- **Actually perform side-effecting actions** (e.g. sending a message to capture the result)
  only after confirming with the user.
- **Watch retina scaling.** CDP screenshots may return 2× (e.g. 2560×1483 vs 1280×773).
  Normalize all frames to one resolution before stitching (see demo-video-assembly).
- **Tab-ID churn / node drops**: the launched Chrome is stable; prefer it over the extension
  node for any multi-step capture.
- **Node 18+ built-ins**: `cdp_lib.mjs` uses built-in `fetch`+`WebSocket` — no Playwright needed.
  If Playwright exists, use `chromium.connectOverCDP` to the ALREADY-launched Chrome; never let
  it download/launch its own browser.

## Cleanup
```bash
pkill -f "remote-debugging-port=9222" || true
rm -rf "$(cat /tmp/ui-capture-profile-path.txt)"
```

## Companion files
- `launch_chrome.sh` — start isolated debuggable Chrome
- `cdp_lib.mjs` — raw-CDP helper (connect/attach/click/evalJS/screenshot)
- `freeze_capture.mjs` — freeze + shoot one transient
- `burst_capture.mjs` — burst-capture an animation cycle
