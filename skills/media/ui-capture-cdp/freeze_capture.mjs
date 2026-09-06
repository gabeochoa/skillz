// Freeze a sub-second transient UI state by pausing an API request, screenshot it, then resume.
// Usage:
//   node freeze_capture.mjs \
//     --url "https://app/route?..." \
//     --pattern "*/api/some/endpoint*" \
//     --wait-text "Loading state text" \
//     --out /path/frame.png
//
// Requires a launched Chrome on CDP_PORT (default 9222) — see cdp_lib.mjs header.
import { connect, attach, sleep, saveShot, evalJS } from './cdp_lib.mjs';

function arg(name, def) {
  const i = process.argv.indexOf('--' + name);
  return i >= 0 ? process.argv[i + 1] : def;
}
const URL = arg('url');
const PATTERN = arg('pattern');            // Fetch urlPattern to pause, e.g. */api/workspaces/classify*
const WAIT_TEXT = arg('wait-text');        // DOM text that indicates the transient is on screen
const OUT = arg('out', '/tmp/frozen.png');
const HOLD_MS = parseInt(arg('hold', '400'), 10); // settle time before shot

const { raw, onEvent } = await connect();
const { targetId, S } = await attach(raw, { fresh: true });
await S('Page.enable', {});
await S('Runtime.enable', {});
await S('Fetch.enable', { patterns: [{ urlPattern: PATTERN, requestStage: 'Request' }] });

let paused = null;
onEvent(m => { if (m.method === 'Fetch.requestPaused' && m.sessionId) paused = m.params; });

await S('Page.navigate', { url: URL });
for (let i = 0; i < 120 && !paused; i++) await sleep(50);
console.log('request paused?', !!paused);

if (WAIT_TEXT) {
  let seen = false;
  for (let i = 0; i < 60; i++) {
    seen = await evalJS(S, `[...document.querySelectorAll('*')].some(e=>(e.textContent||'').includes(${JSON.stringify(WAIT_TEXT)}))`);
    if (seen) break; await sleep(80);
  }
  console.log('wait-text visible?', seen);
}
await sleep(HOLD_MS);

const shot = await S('Page.captureScreenshot', { format: 'png' });
saveShot(OUT, shot.data);
console.log('WROTE', OUT);

if (paused) await S('Fetch.continueRequest', { requestId: paused.requestId });
await S('Fetch.disable', {});
await sleep(300);
await raw('Target.closeTarget', { targetId });
process.exit(0);
