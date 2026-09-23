---
name: ui-screenshot-review
description: Reviews a UI screenshot and returns ranked, specific design findings with fixes. Detects whether the shot is game/immediate-mode UI or web UI and applies the matching checklist, grounded in numeric thresholds (spacing scale, contrast ratios, type scale, safe areas) rather than taste words. Reads the recorded preference profile so findings match this user's style instead of generic defaults. Use when given a screenshot, mockup, or render to critique, when asked "review this UI / what's wrong with this menu / does this layout look right", and when checking a UI change before shipping it. Skip for code-only review with no visual artifact.
---

# UI screenshot review

Look at the image. Say what is wrong, where, and how to fix it. Every finding names a
threshold or a recorded preference — never "feels cluttered" on its own.

## 0. Before looking: load taste

Read `taste-profile.md` next to this file. It is split into a `## product` and a `## game`
section, because taste isn't one thing — tight and heavily skinned is right for a game and wrong
for a settings screen. Read **only** the section matching the mode you detect in step 1. Rules:

- A finding that touches a recorded axis **cites it**.
- Where a generic rule and a recorded preference conflict, **the preference wins**, and you say
  so out loud rather than quietly dropping the rule. "Spacing here is 8px, below the usual 16px
  minimum — but tight density is a recorded preference, so this is fine" is a complete thought.
- Never apply the other context's section. A product answer says nothing about a HUD.
- If your section is still uncalibrated, say so once at the top, then review on the checklists
  alone. Do not stall. Suggest `/design-taste-quiz` for product; for game, note that its axes are
  filled from real screenshots rather than a quiz.

## 1. Pick a mode

State the detected mode in the first line of output so a wrong guess costs one word to correct.

- **game** — fullscreen or letterboxed, no browser chrome, HUD or menu over a rendered scene,
  non-system widgets. This is the default when ambiguous; most of this user's projects are the
  `afterhours` immediate-mode family.
- **web** — browser chrome, document scroll, native form controls, hyperlink affordances.

`--game` / `--web` override detection.

Then read exactly one: `references/game-ui.md` or `references/web-ui.md`. Not both.

## 2. Don't eyeball geometry that a script can measure

Screenshots are bad at pixel arithmetic and good at showing colour, contrast, hierarchy, and
type. Split the work accordingly.

If the project can dump layout trees — `afterhours` projects can; see
`~/p/wm_afterhours/mocks/trees/*.json` — run the existing analyzer first and quote its numbers:

```
python3 ~/p/wm_afterhours/mocks/analyze.py
```

It already checks child-escapes-parent, laid-out-offscreen, flow-siblings-overlap,
gap-not-applied, justify-content-ignored, sizing-collapsed-to-zero, and label-box-has-no-size,
with exact pixel deltas. Never re-derive by squinting what it reports exactly. If no tree dump
exists, fall back to visual estimation and **mark the numbers as approximate** (`~12px`).

For a batch of screens, `~/p/wm_afterhours/run_layout_audit.py` already fans out an audit; use it
rather than looping by hand.

## 3. The shared spine

Both modes check these. Mode files add to this list, they don't replace it.

1. **Focal point** — squint. What reads first? Is that what should read first? Exactly one
   element should dominate; if two compete, that is the finding.
2. **Spacing scale** — values should land on one scale (2/4/8/12/16/20/24/32/48). A lone 13px or
   51px gap is drift, not a decision. Related things sit closer than unrelated things.
3. **Alignment** — count distinct left edges. Every extra one needs a reason.
4. **Type scale** — three text styles is plenty. Sizes should step by a ratio, not by 1px.
5. **Colour** — a limited palette with accents reserved for state (selected, alert, focus).
   Colour is never the only carrier of meaning; there must be a redundant cue.
6. **States** — default, hover, focus, active, disabled, selected, error. Missing states are a
   finding even when the screenshot only shows one.
7. **Consistency** — two elements are identical or clearly different. Near-identical is the bug:
   corner radii that differ by 2px, two grays a hair apart, icons at 22px and 24px.
8. **Anti-slop** (below).

## 4. Anti-slop

Defaults masquerading as decisions. Flag these unless the design explicitly argues for them:

- Every card identical, rounded, same radius, same padding — a kit, not a layout.
- One highlighted word in a headline; ALL-CAPS tracked-out eyebrow labels; a superfluous label
  sitting above content that already says what it is.
- Arrows tacked onto buttons that don't navigate.
- Tinted near-blacks and mono data labels used as decoration.
- The stock palettes: cream + high-contrast serif + terracotta; near-black + one acid accent.
- Gradient behind a big number behind a stat row. The default treatment.
- Motion nobody triggered — per-section fade-ins, hover lift on every card. One orchestrated
  moment beats twelve ambient ones.
- Numbering things that aren't a sequence.

Restraint is the rule underneath all of these: concentrate boldness in one element and keep the
rest quiet.

## 5. Output

Lead with the mode and a one-sentence overall read. Then findings, most severe first:

```
[CRITICAL] Timer clipped at right edge
  where:  top-right HUD, 12px from frame edge
  why:    inside the 5% overscan margin; last digit cuts on 16:10
  rule:   safe-area (game-ui.md); taste-profile density=tight allows small gaps, not past safe area
  fix:    anchor to the safe-area rect, not the window rect
```

Severity:

| | |
|---|---|
| **CRITICAL** | unreadable, clipped, off-screen, or functionally blocked |
| **HIGH** | contrast below AA, broken hierarchy, a missing interactive state |
| **MEDIUM** | spacing or scale drift, near-identical inconsistency |
| **LOW** | polish |

Close with **what works** — two or three specifics, not flattery. Naming what to preserve stops
the next change from breaking it.

No numeric score. A score gets argued with instead of the findings.

## Rules

- Every finding needs a location. "The spacing is off" is not a finding; "16px between the label
  and field, 6px between field and helper text — the field is grouped with the wrong neighbour"
  is.
- Quote measured numbers when a tree dump exists; mark estimates as estimates otherwise.
- No more than ~8 findings. Past that, rank and cut — an unranked wall gets ignored wholesale.
- If the screenshot is a `*_diff.png` from a visual regression suite, the subject is the delta.
  Review what changed, not the whole screen.
- Don't propose a redesign when a fix will do. Don't propose a design system for one screen.
