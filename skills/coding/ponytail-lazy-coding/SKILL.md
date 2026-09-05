---
name: ponytail-lazy-coding
description: Laziness-as-efficiency coding judgment. Use when picking how to implement something, reviewing a diff for unnecessary code, or deciding whether code needs to exist at all. Walks a ladder from "skip it" to "write the minimum", and fixes bugs at the root instead of per caller.
---

# ponytail-lazy-coding

The best code is the code never written. Laziness applies to the solution, never to
understanding the problem.

Upstream: the ponytail ruleset, `github.com/DietrichGebert/ponytail`, MIT licensed. This is a
condensed reasoning guide, not an installed plugin or hook.

## Principles

- Lazy means efficient, not careless.
- Read the task and trace the real flow first, then pick the smallest fix. A confident wrong
  fix with a small diff is the failure mode this guards against.
- A bug fix goes to the root cause. Check every caller of the touched function and fix the
  shared function once. One guard upstream beats N guards per caller.

## The ladder

Stop at the first rung that holds.

1. Does this need to exist at all? If it is speculative, skip it and say so in one line.
2. Is it already in this codebase? Reuse the existing helper or pattern.
3. Does the standard library do it? Use it.
4. Does a native platform feature cover it? Use it. A native date input beats a picker library.
5. Does an already-installed dependency solve it? Use it. Never add a dependency for a few
   lines of logic.
6. Can it be one line? Make it one line.
7. Only then, write the minimum code that works.

When two rungs both work, take the higher one.

## Dos

- No abstraction, interface, factory, or config value that was not asked for and has one
  implementation or one consumer.
- Deletion over addition. Boring over clever. Fewest files, shortest diff, but only once the
  problem is actually understood.
- Two equal-size standard-library options: pick the one that is correct on edge cases. Lazy is
  not flimsy.
- A complex or ambiguous ask ships the small version plus one line questioning scope. Do not
  stall for an answer you can default.
- A deliberate corner-cut with a known ceiling gets recorded with its upgrade trigger, for
  example a global lock or an O(n^2) scan. Record it where the project records such things:
  the change description if the project bans comments, an inline marker if it does not.
- Non-trivial logic (a branch, loop, parser, money path, or security path) ships with one
  runnable check. Trivial one-liners need none.

## Do not simplify these away

- Input validation at a trust boundary.
- Error handling that prevents data loss.
- Security and accessibility.
- Anything explicitly requested.
- Hardware and calibration handling. A real clock drifts and a real sensor reads off, so keep
  the tuning knob.

## Review mode

One line per finding, prefixed with the action: `delete:`, `stdlib:`, `native:`, `yagni:`, or
`shrink:`, plus what replaces it. End with a net line, for example `net: -140 lines, -1 dep`.

Correctness, security, and performance are out of scope for this review flavour. Run a
different review for those.

## Output discipline

Code first, then at most three lines on what was skipped and when to add it. No essays, no
design notes, no unrequested prose. An explicitly requested walkthrough or report is exempt.

## Scope limit

This is coding judgment. It says nothing about when to act, how to communicate, where work is
tracked, or what needs sign-off. Where a project's own process rules speak, those win.
