# Skill inventory

What each machine holds, what was brought into `skills/`, and what was left out
and why. Machines are referred to by alias throughout the tracked tree, because
personal machine names are private data. The alias map is in
`.local-meta/host-aliases.md`, which is not tracked.

Three machines are in scope. Two are reconciled. One is not reachable.

| Host | Installed skills | Status | Reconciled |
|---|---|---|---|
| `workstation-a` | 45 | inventoried, merged | 2026-09-05 |
| `workstation-b` | unknown | **pending, offline** | never |
| `workstation-c` | 46 | inventoried, reconciled by tree hash | 2026-09-05 |

## workstation-c, the machine holding this repo

Reconciled this pass by comparing the full tree hash of every installed skill
against the tracked tree. Not by name, and not by spot check: all 46, hashed
whole.

| Result | Count | Detail |
|---|---|---|
| Identical to the tracked copy | 42 | nothing to do |
| Explained variant | 3 | see below and `CONFLICTS.md` |
| Installed but untracked | 1 | `value-oriented-programming`, imported this pass |
| Tracked but not installed here | 3 | `gabe-writing`, `in-my-voice`, `ponytail-lazy-coding` |

The three variants are all benign and none is upstream drift:

- `automate-me` and `poteto-mode`: the tracked copies carry this repo's own
  wording change, made so a bare ambiguous word would not read as an employer
  name. The installed copies are upstream's. Both are recorded under `variants`
  in `manifest.json` and neither side was overwritten.
- `customer-obsession`: `SKILL.md` is byte-identical in both places. The
  installed directory additionally holds `SKILL.md.bak.20260905_112041`, a backup
  this repo's own installer wrote. Not drift, and left alone: the installed
  skills directory is read-only to this pass.

The three tracked-but-not-installed skills are the ones authored or derived in
this repo rather than installed from a pack. `bin/install.sh` would place them;
nothing requires it to.

### Imported this pass: `value-oriented-programming`

Flagged by the previous pass as needing a human call, on the grounds that it
might be a pre-packaged skill rather than personal work. Resolved by checking:
it is in no bundled pack, including the pstack upstream, and it is the owner's
own distillation of two public conference talks.

`SKILL.md` is now tracked at `skills/coding/value-oriented-programming/`. Its two
`excerpts-*.md` companions are not: they are roughly 28KB of verbatim caption
transcript from those talks, so they moved to the untracked overlay. See
`OVERLAY.md`. `SKILL.md` does not reference them and is complete without them.

## workstation-a, the source of the merge payload

45 installed skills, inventoried and merged in the earlier pass. 44 of them are
the pstack pack, all now tracked with a proven MIT licence and a pinned upstream
commit. The 45th is `customer-obsession`, the owner's own.

None of the 45 named an employer, an internal system, a host, or a person. The
scan's seven marker hits were all benign and are recorded privately.

## workstation-b: not inventoried

**This is the one open gap in the repo.** The machine was offline for every
attempt in this pass and the one before it, so nothing is claimed about what it
holds: not a count, not a list, not an assertion that it holds nothing new.

**Next action:** bring it online and run the same reconciliation used on
`workstation-c`. Tree-hash every directory under its `~/.claude/skills/`, compare
against `manifest.json`, import anything missing into the right group, and record
any variant instead of overwriting it.

Do not fill this section in from memory. Fill it in from a hash-backed run on the
machine itself.

## Adjacent, and deliberately not included

`~/p/jkubkrehel-skills/` is a git clone of a third-party public skill pack
(`jakubkrehel/skills`: better-interface, better-ui, better-typography,
better-colors, better-accessibility, better-layout, better-writing). It is not
installed into `~/.claude/skills` on any machine in scope, so it is not an
installed skill, and it is somebody else's package maintained upstream. It stays
out of `skills/`, exactly as the platform bundles do.

No manifest or README file exists directly under `~/.claude/skills/` on any host
inspected. The directory holds only skill subdirectories.
