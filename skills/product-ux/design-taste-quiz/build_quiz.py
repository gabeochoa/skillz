#!/usr/bin/env python3
"""Build a self-contained A/B taste quiz page for product UI.

Each axis holds the content constant and varies exactly one thing, so an answer
means something specific.

Product UI only, deliberately. A static HTML panel cannot ask a real game-UI
question — HUD layout, diegetic framing, legibility over motion, and screen-edge
anchoring don't survive being a <div>, and a dark-themed settings panel is a
product artifact wearing game colours. Game taste gets elicited from real
screenshots instead; see SKILL.md.

  ./build_quiz.py [-o OUT]

The page is disposable output, so it lands in /tmp rather than in the skill
directory, which is content-hashed by bin/check.sh.
"""
import argparse, sys

C = dict(
    page="#eef0f4", panel="#ffffff", sunk="#f7f8fa", fg="#171a21", muted="#6b7280",
    line="#dfe3ea", rule="#c3cad6", edge="#9aa4b5", accent="#2563eb", onaccent="#fff",
    title="Notifications", ok="Save changes",
    rows=[("Email digest", "Weekly"), ("Mentions", "On"), ("Product updates", "Off")],
    nav=["Dashboard", "Projects", "Team", "Settings"],
    states=[("Billing", "Active"), ("Storage", "88% used"), ("API key", "Expired")],
)


def bodies():
    rows = "".join(f'<div class="row"><span class="label">{a}</span>'
                   f'<span class="value">{b}</span></div>' for a, b in C["rows"])
    nav = "".join(f'<div class="row nav"><span class="ico">&#9635;</span>'
                  f'<span class="label">{m}</span></div>' for m in C["nav"])
    st = "".join(f'<div class="row st {k}"><span class="mark"></span>'
                 f'<span class="label">{a}</span><span class="value">{b}</span></div>'
                 for k, (a, b) in zip(("ok", "warn", "bad"), C["states"]))
    return dict(
        PANEL=f'<div class="panel"><h3 class="title">{C["title"]}</h3>'
              f'<div class="rows">{rows}</div>'
              f'<div class="actions"><button class="btn primary">{C["ok"]}</button>'
              f'<button class="btn">Cancel</button></div></div>',
        NAV=f'<div class="panel"><div class="rows">{nav}</div></div>',
        STATES=f'<div class="panel"><div class="rows">{st}</div></div>')


BASE = """
.panel {{ width:300px; background:{panel}; color:{fg}; padding:20px;
          font:15px/1.45 system-ui, sans-serif; }}
.title {{ font-size:19px; font-weight:600; margin:0 0 14px; }}
.rows {{ display:flex; flex-direction:column; gap:10px; }}
.row {{ display:flex; justify-content:space-between; gap:10px; padding:6px 0; }}
.label {{ color:{fg}; }}
.value {{ color:{muted}; }}
.actions {{ display:flex; gap:10px; margin-top:18px; }}
.btn {{ font:inherit; padding:9px 16px; border:1px solid {line}; border-radius:4px;
        background:transparent; color:{fg}; cursor:pointer; }}
.btn.primary {{ background:{accent}; border-color:{accent}; color:{onaccent}; }}
.ico {{ width:18px; display:inline-block; color:{muted}; }}
.row.nav {{ justify-content:flex-start; }}
.mark {{ width:9px; height:9px; border-radius:50%; flex:0 0 auto; align-self:center; }}
.st.ok .mark {{ background:#2f8f5b; }} .st.warn .mark {{ background:#a8761a; }}
.st.bad .mark {{ background:#c2413e; }}
"""

# (slug, question, A label, A css, B label, B css, body)
AXES = [
    ("density", "Which spacing feels right?",
     "tight", ".panel{{padding:12px}}.rows{{gap:2px}}.row{{padding:3px 0}}"
              ".actions{{margin-top:10px}}",
     "airy", ".panel{{padding:32px}}.rows{{gap:20px}}.row{{padding:10px 0}}"
             ".actions{{margin-top:30px}}", "PANEL"),

    ("grouping", "How should a group be bounded?",
     "bordered box", ".panel{{border:1px solid {edge}}}",
     "whitespace only", ".panel{{border:none;background:transparent}}", "PANEL"),

    ("radius", "Corners:",
     "sharp", ".panel{{border-radius:0}}.btn{{border-radius:0}}",
     "rounded", ".panel{{border-radius:14px}}.btn{{border-radius:10px}}", "PANEL"),

    ("type-scale", "How much size contrast between heading and body?",
     "modest (19/15)", ".title{{font-size:19px}}",
     "dramatic (30/15)", ".title{{font-size:30px;letter-spacing:-0.5px}}", "PANEL"),

    ("hierarchy-signal", "Hierarchy carried by:",
     "weight", ".title{{font-size:15px;font-weight:800}}",
     "size", ".title{{font-size:26px;font-weight:400}}", "PANEL"),

    ("palette", "Palette breadth:",
     "mono + one accent", ".value{{color:{muted}}}",
     "multi-hue functional",
     ".rows .row:nth-child(1) .value{{color:#2f8f5b}}"
     ".rows .row:nth-child(2) .value{{color:#a8761a}}"
     ".rows .row:nth-child(3) .value{{color:#1f8ba8}}"
     ".btn.primary{{background:#9333ea;border-color:#9333ea}}", "PANEL"),

    ("depth", "Depth:",
     "flat", ".panel{{box-shadow:none;border:1px solid {line};background:{sunk}}}",
     "raised", ".panel{{box-shadow:0 16px 34px rgba(20,24,40,.20);border:none}}"
               ".btn{{box-shadow:0 2px 6px rgba(20,24,40,.16)}}", "PANEL"),

    ("button-emphasis", "Primary action:",
     "solid fill", ".btn.primary{{background:{accent};border-color:{accent};"
                   "color:{onaccent}}}",
     "outline", ".btn.primary{{background:transparent;border-color:{accent};"
                "color:{accent}}}", "PANEL"),

    ("alignment", "Alignment:",
     "left, values right", "",
     "everything centred", ".panel{{text-align:center}}.row{{justify-content:center;"
                           "gap:8px}}.actions{{justify-content:center}}", "PANEL"),

    ("nav-icons", "Nav items:",
     "icon + text", "",
     "text only", ".ico{{display:none}}", "NAV"),

    ("state-signal", "How is state signalled?",
     "colour only", ".mark{{display:none}}",
     "colour + shape", ".st.warn .mark{{border-radius:0;transform:rotate(45deg)}}"
                       ".st.bad .mark{{border-radius:0}}", "STATES"),

    ("dividers", "Separating list rows:",
     "visible rules", ".row{{border-bottom:1px solid {rule};padding-bottom:8px}}"
                      ".rows{{gap:0}}",
     "implicit spacing", ".rows{{gap:16px}}", "PANEL"),

    ("chrome", "Overall treatment:",
     "neutral / system-like", ".panel{{border:1px solid {line};background:{panel}}}",
     "branded / expressive",
     ".panel{{border:none;border-top:4px solid #7c3aed;"
     "box-shadow:0 2px 10px rgba(20,24,40,.10)}}"
     ".title{{font-family:Georgia,serif;font-size:22px;color:#4c1d95}}"
     ".btn{{border-radius:999px}}"
     ".btn.primary{{background:#7c3aed;border-color:#7c3aed}}", "PANEL"),

    ("label-case", "Labels:",
     "sentence case", "",
     "ALL CAPS tracked", ".label{{text-transform:uppercase;letter-spacing:1.4px;"
                         "font-size:12px}}.title{{text-transform:uppercase;"
                         "letter-spacing:2px;font-size:13px}}", "PANEL"),
]

PAGE = """<!doctype html><meta charset=utf-8><title>taste quiz &mdash; product</title>
<style>
body {{ margin:0; padding:28px; background:{page}; color:{muted};
        font:15px/1.5 system-ui, sans-serif; }}
h1 {{ font-size:20px; margin:0 0 4px; color:{fg}; }}
.hint {{ margin:0 0 16px; }}
#out {{ width:100%; box-sizing:border-box; height:56px; background:{panel}; color:{fg};
        border:1px solid {line}; border-radius:6px; padding:10px;
        font:14px/1.4 ui-monospace, monospace; }}
.axis {{ border-top:1px solid {line}; padding:22px 0 4px; }}
.q {{ margin:0 0 14px; }} .q b {{ color:{fg}; }}
.pair {{ display:flex; gap:22px; align-items:flex-start; flex-wrap:wrap; }}
.opt {{ border:2px solid transparent; border-radius:8px; padding:10px; cursor:pointer; }}
.opt:hover {{ border-color:{edge}; }}
.opt.picked {{ border-color:{accent}; }}
.cap {{ margin-top:8px; text-align:center; font-size:13px; }}
.opt.picked .cap {{ color:{accent}; font-weight:600; }}
{base}
</style>
<h1>Design taste quiz &mdash; product UI</h1>
<p class=hint>Answering for <b>product</b> UI only &mdash; web apps, tools, settings screens.
Game UI isn't asked here; a static panel can't pose that question honestly. Same content on both
sides of each row, one thing different. Copy the box below back into chat; skipping a row is fine.
</p>
<textarea id=out readonly placeholder="answers appear here"></textarea>
{axes}
<script>
const picks = {{}};
document.querySelectorAll('.opt').forEach(o => o.onclick = () => {{
  const n = o.dataset.n;
  o.parentElement.querySelectorAll('.opt').forEach(s => s.classList.remove('picked'));
  o.classList.add('picked');
  picks[n] = o.dataset.pick;
  document.getElementById('out').value = 'product: ' +
    Object.keys(picks).sort((a, b) => a - b).map(k => k + picks[k]).join(' ');
}});
</script>
"""

AXIS = """<div class=axis>
<p class=q>{n}. <b>{q}</b> &mdash; {slug}</p>
<div class=pair>
  <div class=opt data-n="{n}" data-pick="A"><style>{acss}</style>
    <div id="m{n}a">{body}</div><div class=cap>A &middot; {alab}</div></div>
  <div class=opt data-n="{n}" data-pick="B"><style>{bcss}</style>
    <div id="m{n}b">{body}</div><div class=cap>B &middot; {blab}</div></div>
</div></div>
"""


def scope(css, sel):
    """Prefix each rule with the mock's id so the two sides can't bleed into each
    other, and so the override outranks BASE on specificity."""
    out = []
    for rule in css.split("}"):
        if not rule.strip():
            continue
        head, _, body = rule.partition("{")
        out.append(", ".join(f"{sel} {h.strip()}" for h in head.split(",")) + "{" + body + "}")
    return "\n".join(out)


def build():
    body_by_name = bodies()
    axes = [AXIS.format(n=i, q=q, slug=slug, body=body_by_name[bname], alab=alab, blab=blab,
                        acss=scope(acss.format(**C), f"#m{i}a"),
                        bcss=scope(bcss.format(**C), f"#m{i}b"))
            for i, (slug, q, alab, acss, blab, bcss, bname) in enumerate(AXES, 1)]
    return PAGE.format(base=BASE.format(**C), axes="\n".join(axes), **C)


def self_check(html):
    """Every axis must render two sides that actually differ."""
    for i, (slug, _, _, acss, _, bcss, _) in enumerate(AXES, 1):
        assert f'data-n="{i}"' in html, f"{slug}: missing from page"
        assert acss.strip() != bcss.strip(), f"{slug}: A and B are identical"
    assert html.count("class=opt") == len(AXES) * 2
    return len(AXES)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    # /tmp, not tempfile.gettempdir(): macOS points that at a per-user $TMPDIR,
    # which makes the path unguessable for the "open it" step.
    p.add_argument("-o", "--out", default="/tmp/quiz.html")
    a = p.parse_args()
    html = build()
    n = self_check(html)
    open(a.out, "w").write(html)
    print(f"wrote {a.out} — {n} axes (product)", file=sys.stderr)
