import { createServer } from "node:http";
import { resolve, join } from "node:path";
import { mkdir } from "node:fs/promises";
const P = parseInt(process.env.EYE_PORT || "9223", 10);
const AD = resolve(process.env.EYE_ARTIFACTS || ".artifacts/eye");
const CD = join(process.env.HOME, ".cache", "eye");
const OT = 8000;
let chromium;
async function ld() { const pw = await import(join(CD, "node_modules", "playwright", "index.mjs")); chromium = pw.chromium; }
function race(p, ms = OT, l = "op") { let t; const b = new Promise((_, r) => { t = setTimeout(() => r(new Error("[timeout] " + l + " " + ms + "ms")), ms); }); return Promise.race([p, b]).finally(() => clearTimeout(t)); }

// === waitForCompletion (from Playwright MCP) ===
async function wfc(pg, callback) {
  const reqs = [];
  const listener = r => reqs.push(r);
  pg.on('request', listener);
  try { await callback(); await new Promise(r => setTimeout(r, 500)); }
  finally { pg.off('request', listener); }
  const isNav = reqs.some(r => { try { return r.isNavigationRequest(); } catch { return false; } });
  if (isNav) { await pg.mainFrame().waitForLoadState('load', { timeout: 10000 }).catch(() => {}); return; }
  const pending = reqs.filter(r => { try { return ['document','stylesheet','script','xhr','fetch'].includes(r.resourceType()); } catch { return false; } })
    .map(r => r.response().then(res => res?.finished()).catch(() => {}));
  await Promise.race([Promise.all(pending), new Promise(r => setTimeout(r, 5000))]);
  if (reqs.length) await new Promise(r => setTimeout(r, 500));
}

let br = null, cn = false;
async function gB() {
  if (br) { try { br.contexts(); return br; } catch { br = null; } }
  if (cn) { for (let i = 0; i < 30; i++) { await new Promise(r => setTimeout(r, 100)); if (br) return br; } throw new Error("timeout"); }
  cn = true;
  try { br = await chromium.connectOverCDP("http://localhost:9222"); br.on("disconnected", () => { br = null; }); console.log("[eye] Connected (" + br.contexts().flatMap(c => c.pages()).length + " tabs)"); return br; }
  finally { cn = false; }
}
let cp = null;
async function gP() { if (cp && !cp.isClosed()) return cp; const b = await gB(); const pp = b.contexts().flatMap(c => c.pages()).filter(p => !p.isClosed()); if (pp.length) { cp = pp[0]; return cp; } cp = await (b.contexts()[0] || await b.newContext()).newPage(); return cp; }
async function rP() { if (cp && !cp.isClosed()) { try { await race(cp.title(), 2000); return cp; } catch {} } cp = null; return gP(); }
async function nav(url, w = "load") {
  const b = await gB();
  if (!cp || cp.isClosed()) { const pp = b.contexts().flatMap(c => c.pages()).filter(p => !p.isClosed()); cp = pp[0] || await (b.contexts()[0] || await b.newContext()).newPage(); }
  try { await race(cp.goto(url, { waitUntil: w, timeout: 20000 }), 22000, "nav"); }
  catch (e) { if (!e.message.includes("[timeout]")) { try { await race(cp.waitForLoadState("domcontentloaded", { timeout: 3000 }), 4000); } catch {} } }
  return cp;
}
async function sn(pg, sel = "body") {
  try { return await race(pg.locator(sel).ariaSnapshot({ timeout: 8000 }), 10000, "snap"); }
  catch (e) { if (e.message.includes("destroyed") || e.message.includes("detached")) { const p = await rP(); try { return await race(p.locator(sel).ariaSnapshot({ timeout: 5000 }), 7000); } catch {} } return "[err: " + e.message + "]"; }
}
async function safeClick(pg, ref, opts = {}) {
  const { jsClick = false, force = false } = opts;
  let loc;
  if (ref.startsWith("role:")) { const m = ref.match(/^role:(\w+)\[name=(.+)\]$/); loc = m ? pg.getByRole(m[1], { name: m[2] }) : pg.locator(ref); }
  else if (ref.startsWith("text:")) loc = pg.getByText(ref.slice(5));
  else if (ref.startsWith("label:")) loc = pg.getByLabel(ref.slice(6));
  else loc = pg.locator(ref);
  const count = await race(loc.count(), 3000, "count");
  if (count === 0) throw new Error("No element: " + ref);
  if (count > 1) { const items = []; for (let i = 0; i < Math.min(count, 5); i++) { const t = await loc.nth(i).textContent().catch(() => ""); items.push({ i, text: t?.trim()?.substring(0, 60) }); } throw new Error("Ambiguous: " + count + ": " + JSON.stringify(items)); }
  try {
    if (jsClick) await wfc(pg, () => race(loc.evaluate(el => el.click()), 5000, "jsClick"));
    else await wfc(pg, () => race(loc.click({ noWaitAfter: true, force, timeout: 5000 }), 6000, "click"));
  } catch (e) {
    if (e.message.includes("destroyed") || e.message.includes("detached") || e.message.includes("closed")) { await new Promise(r => setTimeout(r, 1000)); await rP(); return { clicked: ref, navigated: true, url: cp?.url?.() || "?" }; }
    throw e;
  }
  return { clicked: ref, url: pg.url() };
}
async function ss(pg, name, sel) { await mkdir(AD, { recursive: true }); const f = (name || "ss-" + Date.now()) + ".png"; const p = join(AD, f); if (sel) await race(pg.locator(sel).screenshot({ path: p }), 10000, "ss"); else await race(pg.screenshot({ path: p, fullPage: true }), 10000, "ss"); return p; }
function parseBody(req) { return new Promise((res, rej) => { let d = ""; req.on("data", c => d += c); req.on("end", () => { try { res(d ? JSON.parse(d) : {}); } catch { rej(new Error("Bad JSON")); } }); }); }
function json(res, obj, status = 200) { if (res.headersSent) return; res.writeHead(status, { "Content-Type": "application/json" }); res.end(JSON.stringify(obj)); }
function H(fn, maxMs = 25000) { return async (req, res) => { const timer = setTimeout(() => { console.error("[eye] Timeout: " + req.url); json(res, { error: "Server timeout. Page may have navigated." }, 408); }, maxMs); try { await fn(req, res); } catch (e) { console.error("[eye] " + req.url + ": " + e.message); json(res, { error: e.message }, 500); } finally { clearTimeout(timer); } }; }
const R = {};
R["GET /health"] = H(async (_, res) => { const b = await gB().catch(() => null); const n = b ? b.contexts().flatMap(c => c.pages()).filter(p => !p.isClosed()).length : 0; json(res, { ok: true, browser: !!b, currentPage: cp?.url?.() || null, tabs: n }); }, 5000);
R["POST /navigate"] = H(async (req, res) => { const { url, wait } = await parseBody(req); if (!url) return json(res, { error: "url required" }, 400); const pg = await nav(url, wait || "load"); await new Promise(r => setTimeout(r, 1500)); const s = await sn(pg); json(res, { ok: true, url: pg.url(), title: await race(pg.title(), 2000).catch(() => "?"), snapshot: s.substring(0, 4000) }); }, 30000);
R["POST /snapshot"] = H(async (req, res) => { const { selector } = await parseBody(req); const pg = await gP(); const s = await sn(pg, selector || "body"); json(res, { ok: true, url: pg.url(), title: await race(pg.title(), 2000).catch(() => "?"), snapshot: s }); });
R["POST /screenshot"] = H(async (req, res) => { const { name, selector } = await parseBody(req); const pg = await gP(); const path = await ss(pg, name, selector); json(res, { ok: true, path }); });
R["POST /click"] = H(async (req, res) => { const { ref, jsClick, force } = await parseBody(req); if (!ref) return json(res, { error: "ref required" }, 400); const pg = await gP(); const result = await safeClick(pg, ref, { jsClick, force }); const p = await rP(); const s = await sn(p); json(res, { ...result, snapshot: s.substring(0, 3000) }); });
R["POST /type"] = H(async (req, res) => { const { ref, text, submit } = await parseBody(req); if (!ref || text === undefined) return json(res, { error: "ref and text required" }, 400); const pg = await gP(); await race(pg.locator(ref).fill(text), 8000, "fill"); if (submit) await race(pg.locator(ref).press("Enter"), 5000, "enter"); json(res, { ok: true }); });
R["POST /press"] = H(async (req, res) => { const { key, ref } = await parseBody(req); if (!key) return json(res, { error: "key required" }, 400); const pg = await gP(); if (ref) await race(pg.locator(ref).press(key), 5000, "press"); else await race(pg.keyboard.press(key), 3000, "press"); json(res, { ok: true }); });
R["POST /eval"] = H(async (req, res) => { const { expression } = await parseBody(req); if (!expression) return json(res, { error: "expression required" }, 400); const pg = await gP(); try { const result = await race(pg.evaluate(expression), OT, "eval"); json(res, { ok: true, result }); } catch (e) { if (e.message.includes("destroyed") || e.message.includes("detached") || e.message.includes("closed")) { await new Promise(r => setTimeout(r, 1000)); await rP(); json(res, { ok: true, result: "[context destroyed]", navigated: true }); } else throw e; } }, 12000);
R["GET /tabs"] = H(async (_, res) => { const b = await gB(); const all = b.contexts().flatMap(c => c.pages()).filter(p => !p.isClosed()); const tabs = []; for (const p of all) { tabs.push({ url: p.url(), title: await race(p.title(), 1000).catch(() => "?"), current: p === cp }); } json(res, { tabs }); });
R["POST /tab"] = H(async (req, res) => { const { url, index } = await parseBody(req); const b = await gB(); const all = b.contexts().flatMap(c => c.pages()).filter(p => !p.isClosed()); let t; if (typeof index === "number") t = all[index]; else if (url) t = all.find(p => p.url().includes(url)); if (!t) return json(res, { error: "Tab not found" }, 404); cp = t; const s = await sn(cp); json(res, { ok: true, url: t.url(), title: await race(t.title(), 1000).catch(() => "?"), snapshot: s.substring(0, 3000) }); });

R["POST /hover"] = H(async (req, res) => { const { ref } = await parseBody(req); if (!ref) return json(res, { error: "ref required" }, 400); const pg = await gP(); const loc = ref.startsWith("label:") ? pg.getByLabel(ref.slice(6)) : ref.startsWith("text:") ? pg.getByText(ref.slice(5)) : pg.locator(ref); await race(loc.hover(), 5000, "hover"); json(res, { ok: true }); });

R["POST /dialog"] = H(async (req, res) => { const { accept, text } = await parseBody(req); const pg = await gP(); pg.once("dialog", async d => { if (accept !== false) await d.accept(text); else await d.dismiss(); }); json(res, { ok: true, note: "Will handle next dialog" }); });

R["POST /slow-type"] = H(async (req, res) => { const { ref, text, submit } = await parseBody(req); if (!ref || text === undefined) return json(res, { error: "ref and text required" }, 400); const pg = await gP(); const loc = pg.locator(ref); await loc.click(); await race(loc.pressSequentially(text, { delay: 50 }), 15000, "slow-type"); if (submit) await race(pg.keyboard.press("Enter"), 5000, "enter"); json(res, { ok: true }); });

async function main() { await ld(); await gB(); const server = createServer(async (req, res) => { const key = req.method + " " + req.url.split("?")[0]; const h = R[key] || (req.method === "GET" && R["POST " + req.url.split("?")[0]]); if (h) await h(req, res); else json(res, { error: "Not found", routes: Object.keys(R) }, 404); }); server.listen(P, "127.0.0.1", () => { console.log("eye-server v4 on 127.0.0.1:" + P); console.log("All ops race against hard timeout. Server never hangs."); }); process.on("SIGINT", () => { br?.disconnect(); process.exit(0); }); process.on("SIGTERM", () => { br?.disconnect(); process.exit(0); }); }
main();
