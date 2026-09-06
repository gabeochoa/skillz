---
name: eye
description: >
  Browser automation for AI agents — navigate, observe, and interact with web pages via Chrome CDP.
  Primary observation uses accessibility tree snapshots (fast, structured, LLM-native).
  Secondary observation uses screenshots (visual verification).
  All Playwright calls race against hard timeouts — the server never hangs, even on SPA navigation.
  Use when asked to interact with web UIs, create dashboards, fill forms, verify visual changes,
  test frontend behavior, or browse internal tools. Also applies when user says
  "verify in browser", "take a screenshot", "check the page", "does it look right",
  "visual diff", "inspect the DOM", "click the button", "fill the form", "navigate to",
  "open in browser", "browser test", "check localhost", "create a dashboard",
  or asks you to visually confirm any frontend change. Requires a CLI node with Chrome running.
  Auto-installs Chromium on remote dev boxes where no system Chrome is available.
---

# Eye v3 — Browser Automation for AI Agents

Navigate, observe, and interact with web pages through Chrome CDP. Built for reliability on
complex single-page apps: dashboards, admin consoles, and internal tools.

## Key Design Principles

1. **Accessibility snapshots first, screenshots second.** `ariaSnapshot()` returns the full page
   structure in ~3KB of text — buttons, labels, disabled states, expanded menus. No image transfer.
2. **Every Playwright call races against a hard timeout.** If a click triggers SPA navigation and
   destroys the execution context, the server responds with a timeout instead of hanging forever.
3. **Auto-reconnect.** If the browser disconnects, the next request reconnects automatically.
4. **No sessions.** One current page at a time. Simple. Switch tabs explicitly with `/tab`.

## Setup

### Step 1: Ensure Chrome is running with CDP

```bash
curl -sf http://localhost:9222/json/version && echo "Chrome ready"

# If not running, start Chrome (Mac):
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --user-data-dir=$HOME/.chrome-eye \
  --no-first-run --window-size=2400,1350 &
```

### Step 2: Install deps (first time only)

```bash
mkdir -p ~/.cache/eye && cd ~/.cache/eye
npm init -y && npm install playwright pixelmatch pngjs
npx playwright install chromium
```

### Step 3: Deploy and start the server

Copy `eye-server.mjs` to `~/.eye/eye-server.mjs` on the machine with Chrome, then:

```bash
NODE_PATH=~/.cache/eye/node_modules node ~/.eye/eye-server.mjs > /tmp/eye.log 2>&1 &
curl -s http://localhost:9223/health
```

## API Reference

All endpoints accept POST with JSON body. Use `curl -s http://localhost:9223/<endpoint>` directly.

### /navigate — Go to a URL
```bash
curl -s http://localhost:9223/navigate -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","wait":"load"}'
```
Returns: `{ ok, url, title, snapshot }` — includes accessibility snapshot of the loaded page.

### /snapshot — Get accessibility tree (PRIMARY observation)
```bash
curl -s http://localhost:9223/snapshot -H 'Content-Type: application/json' -d '{}'
```
Returns the full ARIA tree. **Use this 90% of the time instead of screenshots.**

The snapshot format:
```
- button "Submit" [disabled]
- textbox "Email": user@example.com
- heading "Dashboard" [level=1]
- link "Settings":
  - /url: /settings
```

Optional: `{"selector":"[role=dialog]"}` to snapshot a specific element.

### /click — Click an element (SPA-safe)
```bash
curl -s http://localhost:9223/click -H 'Content-Type: application/json' \
  -d '{"ref":"label:Submit"}'
```

Ref formats:
- `label:Submit` — find by aria-label
- `text:Click me` — find by text content
- `role:button[name=Edit]` — find by role + name
- `button.my-class` — CSS selector

Options:
- `"jsClick": true` — use JS `el.click()` to bypass overlay interception or Playwright hangs
- `"force": true` — skip actionability checks

Returns: `{ clicked, url, snapshot }` — includes post-click snapshot.

### /type — Type into an input
```bash
curl -s http://localhost:9223/type -H 'Content-Type: application/json' \
  -d '{"ref":"input[placeholder=Search]","text":"query","submit":true}'
```
Uses Playwright `fill()` which properly triggers React change events.

### /eval — Evaluate JavaScript (8s hard timeout)
```bash
curl -s http://localhost:9223/eval -H 'Content-Type: application/json' \
  -d '{"expression":"document.title"}'
```
If eval triggers navigation and context is destroyed, returns `{navigated: true}` gracefully.

### /press — Press a keyboard key
```bash
curl -s http://localhost:9223/press -H 'Content-Type: application/json' \
  -d '{"key":"Escape"}'
```

### /screenshot — Take a screenshot (secondary observation)
```bash
curl -s http://localhost:9223/screenshot -H 'Content-Type: application/json' \
  -d '{"name":"my-screenshot"}'
```

### /tabs — List browser tabs
### /tab — Switch to a tab by URL match or index
```bash
curl -s http://localhost:9223/tab -H 'Content-Type: application/json' \
  -d '{"url":"dashboard"}'
```

### /health — Server status

## Workflow Pattern

1. `/navigate` → read the snapshot in the response
2. `/snapshot` to understand page structure (buttons, inputs, disabled states, menus)
3. `/click`, `/type`, or `/press` to interact → read the post-action snapshot
4. `/snapshot` to verify. `/screenshot` only for visual proof.

## Common Patterns

**Overlay blocking click:** `{"ref":"label:Edit","jsClick":true}`

**React inputs:** `/type` uses Playwright `fill()` — handles React properly

**Finding menu items after dropdown opens:**
```bash
curl -s http://localhost:9223/eval -H 'Content-Type: application/json' \
  -d '{"expression":"JSON.stringify(Array.from(document.querySelectorAll(\"[role=menuitem]\")).filter(e=>e.offsetHeight>0).map(e=>e.textContent.trim()))"}'
```

**Closing dialogs:** `/press` with `{"key":"Escape"}` or eval to click `[aria-label=Close]`

**Click triggers navigation (context destroyed):** Server catches it automatically and returns `{navigated: true}`. Use `/snapshot` to see new page state.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Server timeout (408) | Page navigated during operation. Use `/snapshot` to see current state |
| "No element: ref" | Element doesn't exist. Use `/snapshot` to see what's on the page |
| "Ambiguous: N matches" | Multiple elements match. Be more specific |
| "intercepts pointer events" | Overlay blocking click. Use `jsClick: true` |
| Browser disconnected | Chrome crashed. Restart Chrome, then any request auto-reconnects |

## Important

- **Use /snapshot as your eyes.** Fast, structured, tells you exactly what's clickable.
- **Use jsClick for buttons that might trigger navigation.** Safer than Playwright click.
- **The server NEVER hangs.** Every operation has a hard timeout.
- **Don't use /eval for clicking.** Use /click with jsClick — it handles errors properly.

### /hover — Hover over an element
```bash
curl -s http://localhost:9223/hover -H 'Content-Type: application/json' \
  -d '{"ref":"label:Settings"}'
```
Use to trigger hover menus, tooltips, or reveal hidden action buttons.

### /slow-type — Type character by character (for search/autocomplete)
```bash
curl -s http://localhost:9223/slow-type -H 'Content-Type: application/json' \
  -d '{"ref":"input[role=combobox]","text":"search query","submit":true}'
```
Uses `pressSequentially()` — fires individual key events. Required for React autocomplete inputs where `fill()` doesn't trigger search.

### /dialog — Handle browser dialogs (alert/confirm/prompt)
```bash
curl -s http://localhost:9223/dialog -H 'Content-Type: application/json' \
  -d '{"accept":true}'
```

## v4 Improvements (from Playwright MCP research)

- **`waitForCompletion` pattern**: After every click, monitors network requests and waits for them to settle (navigation → wait for load, XHR/fetch → wait for all responses). No more fixed timeouts.
- **`/slow-type`**: For React autocomplete/search inputs that need key-by-key typing.
- **`/hover`**: For triggering hover menus and revealing action buttons.
- **`/dialog`**: For handling alert/confirm/prompt dialogs that block other interactions.
