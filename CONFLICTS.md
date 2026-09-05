# Merge conflicts, variants, and deferred items

Three passes so far: the payload merge of 2026-09-05 (`20260905T111700`), the
public-cleanup pass the same day, and the reconciliation pass that follows them.

Rollback material, all gitignored:

- `.merge-backups/20260905T111700/` — snapshots and originals from the merge.
- `.local-meta/originals/pre-public-cleanup/` — preimages from the cleanup pass.
- `.local-meta/originals/pre-reconcile/` — preimages from the reconciliation pass.

## File-level collisions

None, in any pass. The merge compared 137 incoming files by sha256 against the
destination before writing; no incoming path matched an existing file with
different content, so nothing was quarantined under `.incoming/` and nothing was
overwritten. The cleanup pass added one skill directory and moved another. The
reconciliation pass added one skill directory that did not exist
(`skills/coding/value-oriented-programming/`) and edited only files it had
already snapshotted.

## Structural merges

These paths existed already and were merged rather than replaced.

| Path | How it was merged |
|---|---|
| `.gitignore` | Existing blocks kept verbatim and first. New blocks appended for `.local-meta/`, local rule files, `.merge-backups/`, `.incoming/`, Python, Node, and editor noise. Entries already present were not duplicated. |
| `manifest.json` | Existing schema kept, because `bin/check.sh` reads `.skills[].slug`, `.status`, and `.sha256`. Later passes added keys rather than replacing the shape: `tree_sha256`, `group`, `files`, `bytes`, `description`, `tags`, `provenance`, and then the proven upstream pin, `variants`, `hosts`, and `overlay`. |
| `README.md` | The merge appended sections, leaving two titles and a stale "next step: git init" block. The cleanup pass rewrote it as one document. The reconciliation pass corrected its remote-visibility claim and its counts. |
| `bin/install.sh` | Discovery generalized from `skills/*/` to any directory holding a `SKILL.md` at depth 1 or 2, so flat and grouped entries both install. The reconciliation pass added `--with-overlay` and moved staging so the hash compared is the hash installed. Install target is unchanged: `~/.claude/skills/<slug>`. |
| `bin/check.sh` | Source lookup reads `source_path` from the manifest and falls back to `skills/<slug>`. The reconciliation pass added `--with-overlay`, so an overlay install is reported as `OVERLAY` rather than as misleading drift. |

Both scripts were changed only where the layout would otherwise make them
misbehave. Originals are under the rollback paths above.

## Variants: tracked deliberately differs from installed

Recorded, not reconciled. Overwriting either side would lose information, so both
stand and `manifest.json` carries the pair under `variants`.

| Skill | Difference | Why it stands |
|---|---|---|
| `automate-me` | One bullet in the preferences list. Upstream uses a bare ambiguous word; the tracked text disambiguates it. | The tracked wording is what lets the repo pass its own publishability scan. A reinstall of upstream must not silently undo it. |
| `poteto-mode` | Two files: the principle-group heading in `SKILL.md`, and one line in `playbooks/eval.md`. Same cause. | Same. |
| `customer-obsession` | None in content. `SKILL.md` is byte-identical. The installed directory also holds `SKILL.md.bak.20260905_112041`. | Not drift. The stray file is a backup this repo's own installer wrote, and it sits under a directory this pass treats as read-only. |

MIT permits the two modified copies. `manifest.json` records
`matches_upstream_at_pinned_commit: false` for both so they are never mistaken
for verbatim.

## Resolved: `customer-obsession`

Deferred by the merge, resolved by the cleanup pass, re-verified this pass.

The merge left the skill flat at `skills/customer-obsession/` because another
updater owned it. That updater's version landed, and the cleanup pass verified
the installed copy's sha256, staged it on the same filesystem, renamed it into
`skills/product-ux/customer-obsession/`, re-verified the landed bytes, confirmed
the preserved preimage matched the flat copy, and only then removed the flat one.

This pass re-hashed it: the tracked copy still matches the installed `SKILL.md`
exactly (`ff3841d75401…`).

## Resolved: pstack provenance

Two passes recorded the pstack licence as unprovable, and the second concluded
that nothing on the machine could establish it. That was wrong, and the specific
error was not looking at shell history.

A history line recorded the clone (`cursor/plugins`, then `cd plugins/pstack`).
That clone was still on disk, clean, at the commit the skills were copied from.
`pstack/LICENSE` reads MIT, © 2026 Lauren Tan, and the same blob re-read from the
GitHub API at the same commit agrees byte for byte. Details in
`THIRD_PARTY_NOTICES.md`.

The lesson worth keeping: "no provenance on this machine" is a claim about where
you looked. Installed bytes have an install history, and that history is a file.

## Named skills that were reported missing

| Name | Finding |
|---|---|
| `poteto-agent` | Not a skill directory, correctly. It is a subagent routing target that `poteto-mode` dispatches to, named in `skills/agent-workflow/poteto-mode/SKILL.md` and `references/plan.md`. Confirmed again this pass against the pinned upstream: there is no such directory in `pstack/skills/`, and adding one would invent a skill that does not exist. |
| `in-my-voice` | Genuinely absent until the cleanup pass imported it. Tracked at `skills/writing/in-my-voice/`. It is not a rename of `gabe-writing`: that one is a house style standard, this one compiles a personal voice profile and drafts to it. The reference runs one way, from `in-my-voice` to `gabe-writing`. |

`poteto-mode` (45 files), `ponytail-lazy-coding`, `gabe-writing`, `automate-me`,
and the updated `customer-obsession` are all present and hash-verified.

## Ungrouped skills

None. Every tracked skill sits in one of the seven groups.

## Publishability

The strict check passes over the whole trackable surface with zero errors and
zero warnings, across 51 rules. Findings are fixed by generalizing text, never by
allowlisting a value.

Licensing is now largely settled: `THIRD_PARTY_NOTICES.md` records each upstream
with the artifact its licence was read from. What remains is two owner decisions,
in `PUSH_BLOCKED.md`, and they are decisions rather than unknowns.
