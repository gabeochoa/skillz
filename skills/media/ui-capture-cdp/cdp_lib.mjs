// Reusable raw-CDP helper over a launched Chrome (default port 9222). No dependencies.
// Node 18+ has built-in fetch + WebSocket. Do NOT use Playwright's own browser.
//
// Launch the target Chrome first:
//   PROF=$(mktemp -d /tmp/ui-capture-profile.XXXX)
//   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
//     --remote-debugging-port=9222 --user-data-dir="$PROF" \
//     --no-first-run --no-default-browser-check --window-size=1280,860 "https://YOURAPP" &
//
// This raw Chrome is NOT subject to any agent browser-node allowlist, so Fetch.* / Network.*
// interception is fully available (the whole reason for this path).
import fs from 'node:fs';

const PORT = process.env.CDP_PORT || '9222';

export async function connect() {
  const ver = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json();
  const ws = new WebSocket(ver.webSocketDebuggerUrl);
  let msgId = 0;
  const pending = new Map();
  const handlers = [];
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) {
      const { resolve, reject } = pending.get(m.id); pending.delete(m.id);
      if (m.error) reject(new Error(m.method + ': ' + JSON.stringify(m.error))); else resolve(m.result);
    } else if (m.method) { for (const h of handlers) h(m); }
  };
  function raw(method, params = {}, sessionId) {
    const id = ++msgId; const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    ws.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
  }
  return { ws, raw, onEvent: (fn) => handlers.push(fn) };
}

// Attach to an existing page target whose URL contains `match`, or create a fresh tab.
export async function attach(raw, { match, fresh, url } = {}) {
  let targetId;
  if (fresh) {
    ({ targetId } = await raw('Target.createTarget', { url: url || 'about:blank' }));
  } else {
    const { targetInfos } = await raw('Target.getTargets', {});
    const t = targetInfos.find(x => x.type === 'page' && (!match || x.url.includes(match)));
    if (!t) throw new Error('no matching page target for: ' + match);
    targetId = t.targetId;
  }
  const { sessionId } = await raw('Target.attachToTarget', { targetId, flatten: true });
  const S = (m, p) => raw(m, p, sessionId);
  return { targetId, sessionId, S };
}

export const sleep = ms => new Promise(r => setTimeout(r, ms));
export function saveShot(path, b64) { fs.writeFileSync(path, Buffer.from(b64, 'base64')); }

// Convenience: full-page PNG screenshot on an attached session.
export async function screenshot(S, path) {
  const shot = await S('Page.captureScreenshot', { format: 'png' });
  saveShot(path, shot.data);
  return path;
}

// Convenience: click at (x,y) via CDP Input events (works on background/launched Chrome).
export async function click(S, x, y) {
  await S('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
  await sleep(120);
  await S('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
  await S('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
}

// Convenience: eval expression, returns the value.
export async function evalJS(S, expression) {
  const r = await S('Runtime.evaluate', { expression, returnByValue: true });
  return r.result.value;
}
