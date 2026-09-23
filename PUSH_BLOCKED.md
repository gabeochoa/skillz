# Publication status

Historical assessment from the standalone skillz repository. As of 2026-09-19,
these files live in `dotfiles/skillz/` and use the dotfiles repository's remote.
The visibility check below describes the former remote, not the current parent
repository. Licensing notes remain applicable to the imported content.

The remote is **private**, measured this pass, not inferred from the SSH URL:

```
$ gh repo view gabeochoa/skillz --json visibility,isPrivate,licenseInfo
{"isPrivate":true,"licenseInfo":null,"visibility":"PRIVATE"}
```

That splits this file in two. Backing the repo up to its private remote and
making it public are different questions with different answers.

## Backup to the private remote: ready

Nothing blocks a push. The remote is private, the tracked tree carries no
employer-internal content, and the strict publishability scan passes with zero
errors and zero warnings over the whole trackable surface. Private originals,
rollback snapshots, and the local overlay are gitignored and stay on the machine.

## Public redistribution: two owner decisions

Both are decisions, not unknowns. The facts each one needs are settled and
recorded in `THIRD_PARTY_NOTICES.md`.

### 1. This repo has no licence

Without a `LICENSE` file the owner's own work is all rights reserved by default,
which blocks anyone else from using a public copy. The third-party content is
already cleared; this is about the owner's own.

No licence has been chosen and this pass did not choose one. See
`LICENSE_DECISION.md` for what the decision covers and what it does not.

**Next action, owner only:** pick a licence, or decide the repo stays private.

### 2. `in-my-voice` is a rewrite of an employer-internal skill

The tracked text is the owner's own, and that is measured, not asserted: zero
sentences shared with the retained source, and after this pass's rewording, no
shared prose run at all. What remains shared is functional (a command name, its
arguments, the literal routing keywords, one config path).

What a rewrite cannot remove is the shape: compile a voice profile from past
writing, then draft to it, with the same post types and change-summary workflow.
The source is the employer's proprietary skill. Whether publishing an
independently written skill of the same name and shape is acceptable is a
judgment the owner makes, not a fact this repo can prove.

**Next action, owner only:** keep it, or delete `skills/writing/in-my-voice/`
before flipping the repo public. Removing it costs nothing else: no tracked file
references it. The reference runs the other way, from `in-my-voice` to
`gabe-writing`, and goes with it.

## Cleared this pass

- **pstack, 44 skills.** Was the largest blocker: upstream unknown, licence
  unreadable. Now proven MIT, © 2026 Lauren Tan, from `cursor/plugins` (a public
  repository) at commit `46125561306434d8a1d7745d540d8932ab0cd2a2`. Licence text
  vendored to `licenses/pstack-MIT.txt`, byte-identical to both a local clone and
  the GitHub API read at that commit. 42 of the 44 are byte-identical to
  upstream; the 2 modified ones are recorded as modified, which MIT permits.
- **`in-my-voice` terms.** The source was identified as an employer-internal
  skill, so its text can never be published. Verbatim overlap with the tracked
  version was measured at zero sentences and reduced to functional strings only.
  What is left is the judgment call above, not an unknown.
- **`value-oriented-programming` excerpts.** Roughly 28KB of verbatim third-party
  talk transcript was shipping inside a skill directory. Moved out of the
  trackable set into the untracked overlay, with `OVERLAY.md` recording what it
  is and how to get it back.
- **tropes.fyi.** Checked directly: the site publishes no terms (`/terms`,
  `/about`, `/license` all 404). The existing mitigation, restating the taxonomy
  rather than reproducing its wording, is the right one and stays.

## Not a blocker, still incomplete

- **One host is not inventoried.** `workstation-b` was offline for every attempt
  in this pass and the previous one, so no claim is made about what it holds.
  This affects completeness of the backup, not the licence status of anything
  tracked. **Next action:** bring that machine online and run the same directory
  comparison used on the other two.

## Clearing this file

Replace it with a one-line note once a licence is chosen and the `in-my-voice`
call is made. Do not delete it because the remaining items look likely to pass:
they are decisions waiting on a person, and the file is where they are written
down.
