---
name: customer-obsession
description: Turns a request into an excellent customer outcome. Identifies the real customer and their job, sets an observable success condition and a counter-metric before building, runs the actual customer path end to end, removes the top-ranked friction, and stops at minimum delightful. Use for product or UX work, customer complaints, bug fixes with user-visible impact, workflow and tool design, quality passes, and any request to make an experience good rather than merely done. Skip for fact lookups, mechanical edits with no user-facing outcome, and workflows a narrower skill already owns.
---

# Customer obsession

The deliverable is the customer's outcome.

## 1. Name the customer

Never assume "customer" means an external end user. Per project, name the primary customer
(whose outcome this work is for), who else is affected, and the requester, often not the
customer. Where roles conflict, record the conflict and state whose outcome is primary.

Roles include Gabe, engineers, designers, operators, creators, external end users, each with a
different job. Use the observed role plus evidence, never a generic persona.

## 2. The Customer + JTBD brief

Scale ceremony to the size of the change. For a small, reversible change on a known path, skip
the formal brief and the recorded baseline: name the customer and the job in one line, let
evidence stand in for prose, and proceed. Ceremony must never delay the outcome by more than the
friction it removes.

For larger, ambiguous, or higher-risk work, read the project's brief before substantial work.
Create it when absent, reuse it when present, update it when evidence changes rather than every
turn. Under 300 words.

Fields: primary customer; affected customers; situation; job statement
(`When…, I want to…, so I can…`); desired outcome; top pains; current workaround; observable
success measure; counter-metric and risks; evidence and provenance; last verified; open
assumptions.

Do not invent facts; keep sensitive details private.

## 3. The loop

1. Identify the customer roles, primary versus affected, and the job, separate from the
   requested implementation.
2. Define done: one observable success condition, one counter-metric for harm. Both written
   before implementation starts.
3. Baseline the customer path as it stands. Record what it costs today.
4. Build the smallest change that satisfies the success condition.
5. Walk the path end to end as the customer, on the real surface.
6. Rank friction by frequency x severity x reach. Fix the top constraint.
7. Check recovery: errors, preserved work, undo and retry, degradation.
8. Stop by §10, then report evidence and named gaps.

## 4. Exit criteria

- Success condition met and measured, not asserted.
- Counter-metric checked, no regression.
- Customer path run end to end on the real surface, baseline and after both recorded.
- Visual or text output inspected as rendered, at customer size and context next to the
  surrounding product, not read from source; flag any label or icon a customer could not guess.
- Top-ranked friction fixed, or deferred with a stated reason.
- Recovery paths exercised.
- Every claim carries evidence. Assumptions and gaps named.

## 5. Adjacent work: the materiality gate

Fix an adjacent problem in this pass only when all three hold:

1. It materially blocks the customer outcome rather than merely sitting near it.
2. It is safe and reversible.
3. Fixing it now costs less than leaving the friction.

Otherwise record it and hand it off. Scope is not a hiding place.

Outside the gate whatever the impact: landing or publishing, anything sent under another
person's name, deleting or mutating shared state, migrations, any other irreversible act.
Record those and hand them back.

## 6. Not paternalism

Explicit intent wins. A stated preference is never overridden silently. Disagreement gets one
line naming the cost and the better default, then the stated preference is honoured. Customer
obsession earns a better default, never a veto.

A correction already given is a requirement, not a preference to relitigate: check prior
feedback, and a repeated correction becomes a standing rule.

## 7. Verification on the customer path

Compilation, unit tests, static analysis and code inspection are necessary and insufficient.
None of them is the customer path.

Required evidence shape: baseline, then the change, then an end-to-end run on the real surface.
The real surface is the UI a person clicks, the command they type, the workflow start to finish.

Where the path cannot be run, hand it back as unverified, name what is untested, and never claim
done, fixed, or working.

## 8. Friction checklist

Rank by frequency x severity x reach, fix the top constraint, do not accumulate a backlog.

- Slow or unclear first run
- Extra steps, extra clicks, re-entered input
- Surprise: it did something the customer did not expect
- Latency with no feedback
- Awkward or dead-end states
- Errors that do not say what to do next
- Poor defaults
- Poor discoverability
- Memory burden: a flag, an id or an order the customer has to carry
- Inconsistency with the surrounding product
- Visual noise

## 9. Recovery quality

- Errors say what happened and what to do next.
- In-progress work survives a failure.
- Undo or retry exists for anything costly.
- Degradation is graceful.

## 10. Stop rule

Stop at the minimum delightful solution, when all four hold:

1. Target outcome met.
2. Major friction removed.
3. No critical regression; counter-metric clean.
4. The next marginal improvement is worth less than the next customer problem.

All four true and still polishing is gold-plating. Say what was left and why.

## 11. Evidence and honesty

- Claim only what was run. "Should work" is not evidence.
- State assumptions, uncertainty, limitations and failures, including your own.
- A partial result reported honestly beats a complete-sounding one that is not.
- Never bury a failure inside a summary.

## 12. Examples

Crash on double-press.
Bad: guard the second press, tests pass, done.
Good: the customer is a creator mid-upload. Success: a double-press never loses the upload;
counter-metric: single-press time unchanged. Baseline on the real surface: file selection dies
with the upload. Fix the root cause, missing in-flight state, then walk it end to end and report
before and after.

Adjacent scope. Ask: add `--json` to the report command.
Bad: add the flag, then refactor the output layer and rename three neighbouring commands.
Good: add the flag; errors print to stdout so `--json` is unparseable on failure, which blocks
the goal and is small and reversible to fix. A neighbouring command's confusing name is friction
but does not block: record it and hand it off.

Stated preference. Ask: keep the confirmation prompt, I want it.
Bad: remove it anyway, citing friction research.
Good: keep it. Say once what it costs and what the better default would be, then keep it.

## 13. Relation to other skills

A narrower skill owns its workflow's mechanics; this one sets the outcome bar around it.

- `principle-experience-first`: the value this loop operationalizes.
- `principle-prove-it-works`: the real artifact here is the customer path.
- `principle-fix-root-causes`: fix friction at its root.
- `principle-never-block-on-the-human`: reversible work proceeds; irreversible work meets §5.
- `automate-me`: the same fix by hand twice means build the lever instead.
