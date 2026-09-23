---
name: design-taste-quiz
description: Elicits the user's visual design preferences and records them as a durable taste profile that ui-screenshot-review reads before every review. Product UI is elicited with side-by-side A/B mockups where each pair holds content constant and varies exactly one thing (density, corner radius, button emphasis, palette breadth, depth, dividers). Game UI is elicited from real game screenshots instead, since a static HTML panel cannot pose a HUD question honestly. Use when asked to learn or calibrate design taste, when the user wants to say "A or B" on design choices, when a review came back too generic, and when adding preference axes after the first round. Skip when the user wants a design produced rather than their preferences recorded.
---

# Design taste quiz

Generic design advice is worthless. This turns "I'll know it when I see it" into a file the
review skill can cite.

The durable artifact is `../ui-screenshot-review/taste-profile.md`, split into `## product` and
`## game`. The quiz page is disposable — rebuild it whenever.

**The two contexts are elicited differently and must never be merged.** Tight, sharp, heavily
skinned is a defensible answer for a game and the wrong one for a settings screen.

---

## Product UI — the A/B quiz

```bash
python3 skills/product-ux/design-taste-quiz/build_quiz.py && open /tmp/quiz.html
```

Stdlib only. 14 rows, A and B side by side, same content both sides, one property different.
Clicking fills a box at the top reading `product: 1A 2B 3A ...`. Then wait — the user answers in
the browser and pastes that string back.

It writes to `/tmp` on purpose: the skill directory is content-hashed by `bin/check.sh`, so
generated files don't belong in it. `/tmp` rather than `tempfile.gettempdir()` because macOS
points that at a per-user `$TMPDIR`, which makes the path unguessable for the "open it" step.

### Verify the render before sending it over

You write this page but never see it. Check it once per axis change:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --hide-scrollbars --window-size=1100,6000 \
  --screenshot=/tmp/quizshot.png "file:///tmp/quiz.html"
```

`Read` that PNG. Every row's A and B must be **obviously** different at a glance. The script's
assert only catches identical CSS; it cannot catch a distinction too subtle to answer honestly.
A pair the user has to squint at produces a coin flip, and a coin flip recorded as a preference
is worse than no data. Raise the contrast of the varied property and re-shoot. Three of the
original fourteen needed this.

### Adding axes

Append a tuple to `AXES`: `(slug, question, a_label, a_css, b_label, b_css, body)`. CSS is
`str.format`-ed against the palette dict `C` — so write `{line}`, `{accent}`, `{muted}` rather
than hex literals, and double every literal brace: `.panel{{padding:12px}}`. Selectors get scoped
to the mock automatically, so write them plain. Three bodies exist — `PANEL`, `NAV`, `STATES`.

Numbering is positional, so **append, never insert**. Inserting renumbers every later axis and
silently invalidates previously recorded answers.

Good axis: one variable, both options defensible, two reasonable people would disagree. Bad axis:
one side is just worse. "Legible vs illegible" teaches nothing.

---

## Game taste — real screenshots, not mocks

Do not build an HTML quiz for this. HUD layout, diegetic framing, legibility over motion, and
screen-edge anchoring don't survive being a `<div>`; a dark-themed settings panel is a product
artifact wearing game colours. It would collect confident answers to the wrong questions.

Use real artifacts:

- `~/p/wm_afterhours/inspiration/` — 14 shots from shipped games (Ace Combat, Mini Motorways,
  PowerWash, Kirby Air Riders, Deadspace, Angry Birds, Rubber Bandits, Rematch, and others).
- `~/p/wm_afterhours/baseline_screenshots/` — the user's own current output.

`open` the two files so the user can actually see them — `Read` puts an image in your context,
not on their screen. `Read` them too, so you can frame the question accurately.

### Anchor to one project. Never compare across genres.

This was learned the hard way: a Kirby-vs-Dead-Space pair got "I prefer A, but it depends on the
type of game — these aren't really easy to compare." That is right. Kirby is bright because it's
Kirby; Dead Space is dark because it's survival horror. Genre is a **constraint** the design has
to satisfy (`../ui-screenshot-review/references/game-ui.md` §F), not a dimension of taste. A
cross-game pick measures genre, then gets mistaken for preference.

So: name a target project first — `pharmasea`, `kart-afterhours`, `wm_afterhours` — and ask
"which of these is closer to what you want **for this one**". Better still, compare two variants
of the *same* screen from that project. Record under `### <project> / <axis>`.

Also note the corpus: `inspiration/` is game **settings menus**, not HUDs. Menu axes are the ones
these references can actually answer. HUD questions — screen footprint, legibility over motion,
edge anchoring — need in-game captures that don't exist here yet.

### Asking well

Pick pairs that differ on roughly one thing, and **name what you think that thing is** when you
ask. If the user disagrees with your framing, that is the more valuable answer — it tells you
which variable they were actually looking at.

Worth asking, within a project: opaque plates behind text vs raw on the scene · diegetic framing
vs clean overlay · icon-led vs text-led · list vs grid · how much of the screen a menu may take ·
how loud selection is allowed to be.

Record as `### <axis>` under `## game`, naming the files compared. These are noisier per answer
than a controlled mock, since many variables move at once — so record them as direction, not
rule, list the confounds explicitly, and mark weakly-held picks as leans.

---

## Recording answers

Parse `product: 1A 2B ...` against the `AXES` list order. Skipped numbers are skipped, not
guessed. Write into the matching context section of `../ui-screenshot-review/taste-profile.md`:

```markdown
### density
**tight** (2026-09-06) — picked compact rows over airy ones
```

- Re-answering an axis **replaces** its entry. If the pick reversed, keep one line noting it.
- Remove that section's `**Status: uncalibrated.**` line once its first answers land.
- Don't editorialize taste into rules the user didn't pick. "tight density" does not license
  "prefers cramped UI".
- `taste-profile.md` lives inside the `ui-screenshot-review` skill, so writing it changes that
  skill's tree hash. Regenerate its `sha256` and `tree_sha256` in `manifest.json` afterwards, or
  `bin/check.sh` reports a false FAIL.
