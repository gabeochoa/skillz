# Licence decision

**This repo has no `LICENSE` file, and this pass did not add one. Choosing a
licence is the owner's decision and nobody else's.**

This note records what that means today, so the absence reads as a pending
decision rather than an oversight.

## What is true without a licence

- The owner's own work in this repo is **all rights reserved** by default. That
  is the legal default for an original work with no licence grant, not a
  statement of intent.
- Nobody else may copy, modify, or redistribute the owner's parts, even if the
  repository is visible to them.
- **Public redistribution is blocked until a licence is chosen.** Not by policy
  here, by the default above.
- Backup to the current private remote is unaffected. A private backup is not a
  distribution.

## What is already settled, and is not waiting on this

The third-party content is cleared and does not depend on the licence choice:

| Content | Status |
|---|---|
| 44 pstack skills | MIT, © 2026 Lauren Tan. Text at `licenses/pstack-MIT.txt`. |
| `ponytail-lazy-coding` | MIT, © 2026 DietrichGebert. Text at `licenses/ponytail-MIT.txt`. |
| tropes.fyi taxonomy | No published terms. Restated, not reproduced. |
| Unlicensed verbatim material | Held in the untracked overlay. See `OVERLAY.md`. |

So the licence question is only about the owner's own work:
`skills/writing/gabe-writing/`, `skills/writing/in-my-voice/`,
`skills/product-ux/customer-obsession/`,
`skills/coding/value-oriented-programming/`, all of `bin/`, and the repo's docs.

## What the decision has to account for

A licence chosen here sits alongside MIT-licensed vendored content that keeps its
own terms regardless. Two consequences worth knowing before choosing:

1. **The MIT notices travel either way.** Whatever licence covers the owner's
   work, `licenses/pstack-MIT.txt` and `licenses/ponytail-MIT.txt` must ship with
   the repo and keep their copyright lines. A licence for the owner's work does
   not relicense vendored content.
2. **A copyleft choice would be the awkward one.** MIT content can be combined
   with almost anything, but a strong copyleft licence over the repo as a whole
   invites confusion about which terms cover which directory. Whatever is chosen,
   say plainly in the `LICENSE` file or the README which parts it covers.

## What to do

Add a `LICENSE` file, then:

1. Note the choice in `README.md` under Attribution.
2. Say in `THIRD_PARTY_NOTICES.md` that the owner's own work is now covered by
   it, replacing the closing paragraph that says it is not.
3. Remove decision 1 from `PUSH_BLOCKED.md`.
4. Delete this file. Its only job is to hold the question open until it is
   answered.

If the answer is "this stays private", record that here instead of adding a
`LICENSE`, and the question is equally closed.
