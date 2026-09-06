// Capture an ANIMATED transient (e.g. a spinner) as a frame burst while an API request is frozen.
// CSS animations keep running while the request is paused, so N rapid screenshots capture a
// full animation cycle you can loop in the final video.
// Usage:
//   node burst_capture.mjs --url "..." --pattern "*/api/...*" --wait-text "Determining" \
//     --outdir /path/spinner --n 16 --gap 70
import { connect, attach, sleep, saveShot, evalJS } from './cdp_lib.mjs';
import fs from 'node:fs';

function arg(name, def) { const i = process.argv.indexOf('--' + name); return i >= 0 ? process.argv[i + 1] : def; }
const URL = arg('url');
const PATTERN = arg('pattern');
const WAIT_TEXT = arg('wait-text');
const OUTDIR = arg('outdir', '/tmp/burst');
const N = parseInt(arg('n', '16'), 10);
const GAP = parseInt(arg('gap', '70'), 10);
fs.mkdirSync(OUTDIR, { recursive: true });

const { raw, onEvent } = await connect();
const { targetId, S } = await attach(raw, { fresh: true });
await S('Page.enable', {});
await S('Runtime.enable', {});
await S('Fetch.enable', { patterns: [{ urlPattern: PATTERN, requestStage: 'Request' }] });
let paused = null;
onEvent(m => { if (m.method === 'Fetch.requestPaused' && m.sessionId) paused = m.params; });

await S('Page.navigate', { url: URL });
for (let i = 0; i < 120 && !paused; i++) await sleep(50);
console.log('paused?', !!paused);
if (WAIT_TEXT) {
  let seen = false;
  for (let i = 0; i < 60; i++) { seen = await evalJS(S, `[...document.querySelectorAll('*')].some(e=>(e.textContent||'').includes(${JSON.stringify(WAIT_TEXT)}))`); if (seen) break; await sleep(80); }
  console.log('wait-text?', seen);
}
for (let i = 0; i < N; i++) {
  const shot = await S('Page.captureScreenshot', { format: 'png' });
  saveShot(`${OUTDIR}/frame_${String(i).padStart(2, '0')}.png`, shot.data);
  await sleep(GAP);
}
console.log('captured', N, 'frames to', OUTDIR);
if (paused) await S('Fetch.continueRequest', { requestId: paused.requestId });
await S('Fetch.disable', {});
await sleep(300);
await raw('Target.closeTarget', { targetId });
process.exit(0);
