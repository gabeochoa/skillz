---
name: fun-loop
description: Turns a game design doc into a playable prototype by running an autonomous build-playtest-judge loop against a wall-clock budget. Extracts a falsifiable claim from the doc, builds the smallest thing that tests it, playtests it with three bots, and gates a scoring ladder on computed metrics so the judge cannot inflate its way past a mechanic with no real decision in it. Use when asked to prototype a game idea, test whether a mechanic is fun, run a fun loop or dream loop on a design doc, or turn a GDD into something playable. Skip for visual fidelity work, for building a finished game, and for prototypes where a human will be watching every round anyway.
---

# Fun loop

Build a prototype from a design doc, unattended, until the clock runs out. Hand back something the
user can play.

Adapted from `achimala/dream-loop` (MIT), which does this for graphics. That loop works because a
screenshot is a cheap complete artifact its judge can *see*. Fun has no screenshot, and an LLM asked
to score fun will inflate — so here **the harness computes the tier cap and the judge scores inside
it**. Numbers gate the ladder; the judge only interprets them and writes directives.

The loop is a filter, not a verdict. It exists to stop an unattended hour from converging on
something with no decision in it. The verdict is the user, playing.

## 0. Set up

Need a design doc. If given a project, find it (`gdd.md`, `DESIGN.md`, `idea.md`, `notes/*.md`). If
given a bare idea, write a 20-line doc first and say you did.

Wall-clock budget from the invocation (`/fun-loop 90m`), default **60m**. Record the start time.
Check the clock between rounds. Never start a round that can't finish. Don't degrade the build to
beat the clock — stopping mid-ladder with something real beats rushing a broken round in.

Working state goes in `.fun-loop/` inside the prototype folder, gitignored. Never in the source
game's repo, and never in this skill's directory.

**Never write to a real game repo.** Prototypes are disposable and land in their own folder. If the
design doc lives in a real project, read it and leave that project untouched.

## 1. Extract the hypothesis

This replaces dream-loop's concept-art step. Nothing is generated — it's extraction. Write
`.fun-loop/hypothesis.md`:

- **Core verb** — what the player does. One word.
- **The beat** — the decision the player makes, and how often they make it.
- **The tension** — what can go wrong, and how the player sees it coming.
- **Win / loss** — how a run ends.
- **The fun claim** — one sentence on why this is fun.
- **The prediction** — *"a player who X will outscore one who doesn't."* Must be falsifiable. This
  is the thing the considered bot implements and the whole loop tests.
- **Cut list** — everything in the doc not needed to test the claim. Should be most of the doc. Be
  ruthless; a 400-line GDD usually has one testable claim in it.

If the doc supports no falsifiable prediction, that is the finding. Write it up and stop. A design
that can't say what a good player does differently is not ready to prototype.

## 2. Build

The smallest thing that tests the prediction. Everything on the cut list stays cut. No art, no
menus, no juice — none of it can move a gate below Tier 4.

**Sim and render must be separate.** See `references/harness.md` for the contract. This is
non-negotiable: it's what makes thousands of headless runs cost a second, which is the only reason
an unattended loop is affordable.

Target a **single-file web mock** by default — no build step, instant reload, trivially scriptable.
This matches the existing `mocks/` convention in `~/p/template/PROJECT_TEMPLATE.md` ("single-file
HTML prototypes used for design/fun validation before committing to C++"). Serve with
`python3 -m http.server`.

`afterhours`/C++ is the eventual target for ideas that survive, and the harness contract is written
to port there. Don't build it that way unless asked. `~/p/kart-afterhours` already ships an MCP
automation interface (screenshot/key/mouse) — that's the precedent when the time comes.

**Every round ends human-playable.** The user plays whatever exists when the clock stops, so the
render layer is a deliverable, not polish: real input, visible state, readable feedback on the one
decision the hypothesis names. Copy the last working build to `.fun-loop/last-good/` after every
round that runs, so an expiry mid-round never hands over something broken.

## 3. Playtest

Three bots, N seeded runs each (N=200 default, more if variance is high). Same seed set for all
three so the comparison is paired.

| Bot | Plays |
|---|---|
| **random** | uniform over `legalActions` |
| **greedy** | one-step lookahead on `score` |
| **considered** | the strategy the design doc's prediction names |

The considered bot is the experiment. It plays the way the doc says a good player plays. If it can't
beat random, the design's own claim about what makes it fun is false, and no amount of tuning fixes
that.

Write `.fun-loop/round-N/metrics.json` and 3-5 annotated traces (per beat: state summary, options,
choice, outcome). Bot code and metric definitions are in `references/harness.md`.

## 4. Gates

Computed from the metrics. Not opinions, not negotiable, not the judge's call.

| Gate | Passes when | Caps score at |
|---|---|---|
| **G1 Loop closes** | every run terminates; no crash, no deadlock, no unreachable end | 3 |
| **G2 Real decision** | considered separates from random — Cohen's d ≥ 0.8 on final score | 5 |
| **G3 Losable** | considered's loss rate strictly inside (0.05, 0.95) | 5 |
| **G4 Live options** | no action >60% of considered's choices; ≥2 actions above 10% | 7 |
| **G5 Skill curve** | random < greedy < considered, monotone, each gap d ≥ 0.5 | 7 |
| **G6 Shape** | run length in the doc's stated band; outcome not determined in the first 20% of beats | 9 |

Tier = the highest band whose gates all pass. The cap is the ceiling on this round's score, full
stop.

G2 is the one that matters. An always-win game fails G3, a one-button game fails G4, a game where
thinking doesn't pay fails G5 — but a game with no decision in it fails G2, and that is the failure
no polish can recover.

## 5. Judge

Fresh subagent, clean context, every round. Give it `metrics.json`, the annotated traces,
`hypothesis.md`, and from round 2 on the previous round's metrics and verdict. Prompt verbatim in
`references/judge-prompt.md`.

It returns a score (clamped to the cap), the tier, a LANDED/PARTIAL/NOT DONE pass over the previous
round's directives, the blocking items for the next gate, and at most four further directives.

Before you submit: check the build yourself. Run it, read the metrics, and write an honest line in
`.fun-loop/round-N/self-check.md` on whether this is worth a judge round. Rounds are the expensive
unit. Don't spend one on work you already know is half-baked.

## 6. Act

Address the blocking items and as many high-value directives as the round allows. Not just the top
one — rounds are expensive, make each count.

Only revert if the score dropped a full point or more. Small dips are noise; reverting a whole round
throws out the good with the bad. If one specific change caused a regression, undo that change.

**Stall approaching** — no full-point gain in 2 rounds, or the same gate blocks 3 times. Stop
tuning. The numbers aren't the problem, the mechanic is. Make one structural change this round:

- change the core verb
- change the scarce resource
- change what failure means
- change the time pressure
- remove a system entirely and see if the gate moves

Parameter tuning is banned in this branch unless you can say why it moves the gate this time when it
didn't last time.

## 7. Stop and hand over

Stop on: clock expired, score ≥ 8, or stalled (structural change already tried, still nothing in 3
rounds — stop early rather than burn the remaining clock).

Copy `.fun-loop/last-good/` to the prototype root. Write and print `.fun-loop/REPORT.md`:

1. **How to run it and what the controls are.** First line. The user should be playing within ten
   seconds of reading.
2. The claim being tested, and the gate table with actual numbers.
3. If it stalled: which gate never passed, and the specific reason the prediction failed. This is
   often worth more than the prototype — a documented "this mechanic doesn't work, here's why"
   beats a mediocre build.
4. What was cut, so a flat first impression doesn't get blamed on a feature that was cut on purpose.

## Rules

- The judge never scores above the computed cap and never disputes the metrics. It explains them.
- The considered bot implements the doc's prediction, not your idea of good play. If you improve the
  strategy, you've changed the hypothesis — say so and update `hypothesis.md`.
- A directive names an element and a magnitude. "The shove action is 81% of choices because it
  strictly dominates redirect below density 4; add a 2s cooldown" is a directive. "The options feel
  unbalanced" is not.
- Never tune the bots to make a gate pass. That's fabricating the experiment.
- No human checkpoint. If you want to ask something, write the assumption in `REPORT.md` and keep
  going.
