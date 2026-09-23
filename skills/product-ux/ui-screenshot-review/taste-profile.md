# Taste profile

Recorded design preferences, split by context. `ui-screenshot-review` reads the section matching
its detected mode before every review.

Split because taste isn't one thing. Tight, sharp-cornered, and heavily skinned is a defensible
answer for `pharmasea`; the same answer on a settings screen would be wrong. A single averaged
profile would be wrong for both.

## How to read this file

One `###` heading per axis under its context. The bold word is the pick. Re-answering an axis
replaces its entry; keep a one-line note if the pick reversed, since a changed mind is
information.

A preference recorded here **outranks** a generic rule in the checklists. When they conflict, the
review names the rule it is setting aside and why.

---

## product

Web apps, tools, settings screens, dashboards.

Calibrated 2026-09-06, 14/14 axes, from the A/B quiz.

**The shape of it:** compact, bounded, rounded, lifted. Content packed tight inside a card that
is clearly a card — border plus shadow — but with nothing dividing it internally. Restraint in
type and colour: one accent, modest size steps, weight doing the hierarchy work. System-neutral,
not branded.

### density
**tight** (2026-09-06) — compact rows over airy ones

### grouping
**bordered box** (2026-09-06) — an explicit border over whitespace-only grouping

### radius
**rounded** (2026-09-06) — 14px panel / 10px control over sharp corners

### type-scale
**modest** (2026-09-06) — 19/15 heading-to-body over a dramatic 30/15

### hierarchy-signal
**weight** (2026-09-06) — bold at body size over a larger, lighter heading

### palette
**mono + one accent** (2026-09-06) — over multi-hue functional colour

### depth
**raised** (2026-09-06) — drop shadow over flat-with-border

### button-emphasis
**solid fill** (2026-09-06) — over an outline primary

### alignment
**left, values right** (2026-09-06) — over fully centred

### nav-icons
**icon + text** (2026-09-06) — over text-only nav

### state-signal
**colour only** (2026-09-06) — over colour + shape.
**Bounded by accessibility, and this is the one axis that does not fully outrank its rule.**
Colour as the sole carrier of meaning fails WCAG 1.4.1 for colorblind users. Applied as: don't
add a redundant mark where the *text beside it already says the state* ("Expired", "88% used") —
the label is the redundant cue, so the dot can stay plain. Where a dot or fill is genuinely the
only signal, the review still calls for a second cue and cites this line.

### dividers
**implicit spacing** (2026-09-06) — 16px gaps over visible rules

### chrome
**neutral / system-like** (2026-09-06) — over branded / expressive

### label-case
**sentence case** (2026-09-06) — over ALL CAPS tracked

### tension to watch
`density=tight` and `dividers=implicit spacing` pull against each other: tight packing removes
the whitespace that implicit grouping depends on. Where both apply, spacing between groups has
to stay visibly larger than spacing within them, or the grouping stops reading at all. Flag rows
where inner and outer gaps have converged.

---

## game

HUDs, menus, and anything drawn over a rendered scene.

**Status: uncalibrated, and not quiz-able.** A static HTML panel can't pose a real game-UI
question — HUD layout, diegetic framing, legibility over motion, and screen-edge anchoring don't
survive being a `<div>`, and a dark-themed settings panel is a product artifact wearing game
colours. Rendering the quiz that way would collect confident answers to the wrong questions.

Fill this from real artifacts instead: `~/p/wm_afterhours/inspiration/` (14 shots from shipped
games) and the user's own `baseline_screenshots/`. See `design-taste-quiz` → "Game taste".

**Note on the corpus:** `inspiration/` turned out to be game **settings menus**, not HUDs. The
original "a static panel can't pose a game question" framing was too broad — menus are exactly
what these references are about. HUD-specific axes (screen footprint, legibility over motion,
edge anchoring) remain unasked and unrecorded.

Calibration in progress. These are whole-image picks, so they move several variables at once —
recorded as **direction, not rule**, with the compared files named.

### text backing over a scene
**strongly prefers backing plates** (2026-09-06) — `example_mini_motorways.jpg` over
`example_ace_combat.jpg`, stated as a clear preference.
Mini Motorways gives every menu label an opaque chip (solid orange for the selected tab, pale
blue-gray otherwise), so the game world never shows through behind text. Ace Combat gives none:
cyan text sits raw on the rendered scene, legible only because that region happens to be dark
and quiet, with diegetic HUD lines and a lens flare marking selection.
Confounded with: type size (~60px/7 items vs ~24px/9 items), light vs dark palette, and
diegetic vs clean framing. A follow-up pair was run to separate these — see below.

### light/playful vs dark/technical
**leans light** (2026-09-06) — `example_kirby_airriders.jpg` over `example_deadspace.jpg`,
**weakly held**. Backing plates were constant across this pair, so the pick isn't about those.
Recorded as a lean, not a preference, because of the next entry.

### genre gates taste — method rule, not a style pick
**Cross-game pairs don't isolate taste** (2026-09-06). Stated directly while comparing Kirby to
Dead Space: the two aren't really comparable, because the right answer depends on the kind of
game. That is correct and it matches `game-ui.md` section F — genre convention is a *constraint*
the design has to satisfy or explicitly justify, not a dimension of personal preference. Kirby is
bright because it's Kirby; Dead Space is dark because it's survival horror. Neither reveals what
this user would want for a given project of their own.

**How this changes reviews:** never carry a preference from one game reference onto an unrelated
project. In game mode, establish the project's genre first and treat convention as the baseline;
only deviations from that baseline are worth a finding. A cross-game "they liked X once" is not
evidence about the screen in front of you.

**How this changes calibration:** anchor to one project at a time. Ask which references are close
to the target *for `pharmasea`*, or compare variants of the same screen — never "Kirby or Dead
Space" in the abstract.

<!-- game axes below -->
