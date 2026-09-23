# Harness: the sim contract, the bots, the metrics

Everything here is small on purpose. If the harness gets big, the prototype got big, and that's the
bug.

## The contract

One module, no DOM, no canvas, no timers, no globals. Pure functions over an explicit state.

```js
export const sim = {
  init(seed),                  // -> state.  Same seed, same run. No Math.random anywhere.
  legalActions(state),         // -> [action].  Never empty unless isOver.
  step(state, action),         // -> state.  New object; do not mutate the argument.
  score(state),                // -> number.  Higher is better. The thing a player is trying to max.
  isOver(state),               // -> bool
  won(state),                  // -> bool.  For the loss-rate gate.
  summary(state),              // -> {}.  Design-specific readouts the judge reads in traces.
}
```

Render is a separate file that imports `sim` and does nothing but draw `state` and turn input into
an `action`. If render can't be deleted without breaking the bots, the split is wrong.

**Real-time designs.** Still discrete. `step` advances one fixed tick (1/60s), and an action is the
input state held during that tick. A "beat" for metrics purposes is then a *change* in held input,
not every tick — otherwise action-frequency numbers measure framerate instead of decisions.

**Seeded RNG.** `Math.random` makes runs unreproducible and the metrics meaningless. Use a small
PRNG carried in the state:

```js
// mulberry32
function rng(s) { return () => (s = s + 0x6D2B79F5 | 0, ((t => (t = Math.imul(t ^ t >>> 15, t | 1),
  t ^= t + Math.imul(t ^ t >>> 7, t | 61), ((t ^ t >>> 14) >>> 0) / 4294967296))(s))) }
```

## The bots

```js
const bots = {
  random: (s, r) => pick(sim.legalActions(s), r),

  greedy: (s) => best(sim.legalActions(s), a => sim.score(sim.step(s, a))),

  considered: (s) => { /* the hypothesis, implemented */ },
}
```

`considered` is the whole experiment. It plays the way the design doc says a good player plays —
read the prediction out of `hypothesis.md` and encode exactly that, nothing smarter. If you find
yourself improving it, you are changing the hypothesis; go update `hypothesis.md` and say so.

Break ties by seeded RNG, not by array order — array order makes the first-listed action look
dominant and poisons G4.

## Running them

```js
const SEEDS = Array.from({length: 200}, (_, i) => i)   // same seeds for all three bots: paired
const run = (bot, seed) => {
  let s = sim.init(seed), beats = [], guard = 0
  while (!sim.isOver(s)) {
    if (++guard > 100000) return {hung: true, seed}       // G1 needs this
    const opts = sim.legalActions(s), a = bot(s, rngFor(seed))
    beats.push({t: beats.length, sum: sim.summary(s), opts: opts.length, took: a, score: sim.score(s)})
    s = sim.step(s, a)
  }
  return {seed, score: sim.score(s), won: sim.won(s), beats}
}
```

Runs in node, no browser. `node bots.mjs > .fun-loop/round-N/metrics.json`.

## The metrics

```js
const mean = xs => xs.reduce((a,b)=>a+b,0) / xs.length
const sd   = xs => Math.sqrt(mean(xs.map(x => (x - mean(xs))**2)))
// Cohen's d, pooled
const d = (a, b) => (mean(a) - mean(b)) / Math.sqrt((sd(a)**2 + sd(b)**2) / 2) || 0
```

| Gate | Computation | Passes |
|---|---|---|
| **G1** | any run with `hung`, a thrown error, or `beats.length === 0` | zero of them |
| **G2** | `d(considered.scores, random.scores)` | ≥ 0.8 |
| **G3** | `considered.filter(r => !r.won).length / N` | in (0.05, 0.95) |
| **G4** | histogram of `took` over all considered beats | max share ≤ 0.6 **and** ≥2 actions above 0.10 |
| **G5** | `d(greedy, random)` and `d(considered, greedy)` | both ≥ 0.5, and means monotone |
| **G6** | run length vs. the doc's stated band; plus *decidedness* | see below |

**Decidedness (G6).** Truncate each considered run at 20% of its beats, then rank the seeds by score
at that point and by final score. Spearman correlation ≥ 0.9 means the run was over before it
started. Pass when it's below 0.9 and run length sits in the band the design doc claims.

Cohen's d thresholds: 0.5 is a real but modest effect, 0.8 is large. They're the conventional
cutoffs and they're arbitrary — but a fixed arbitrary line the judge can't argue with is the whole
point. Move them only if the design genuinely calls for it, and say so in `REPORT.md`.

## metrics.json

```json
{
  "round": 3,
  "seeds": 200,
  "gates": {
    "G1": {"pass": true,  "hung": 0, "errors": 0},
    "G2": {"pass": true,  "d_considered_vs_random": 1.42},
    "G3": {"pass": false, "loss_rate": 0.02, "note": "considered almost never loses"},
    "G4": {"pass": true,  "top_action": ["redirect", 0.44], "above_10pct": 3},
    "G5": {"pass": true,  "d_greedy_vs_random": 0.71, "d_considered_vs_greedy": 0.63},
    "G6": {"pass": false, "median_beats": 34, "band": [60, 120], "decidedness": 0.61}
  },
  "tier": 1,
  "cap": 3,
  "scores": {"random": {...}, "greedy": {...}, "considered": {...}},
  "action_histogram": {"redirect": 0.44, "shove": 0.31, "wait": 0.19, "call": 0.06}
}
```

`tier` is the highest band with all gates passing, `cap` its ceiling. Both are computed here, before
the judge sees anything — that's what makes them binding.

## Traces

3-5 runs, picked to be informative rather than representative: the best considered run, the worst,
one where considered and greedy diverged most, and one random run for contrast. Label which is
which. Truncate to ~40 beats with an elision marker if longer; the judge needs shape, not every
tick.

## Common failure

**"All gates pass but the game is boring."** Expected. The gates prove there is a decision worth
making, not that making it feels good. Feel is Tier 4-5 and it's why the user plays at the end. Don't
add gates trying to measure it — you'll measure something else and believe it.
