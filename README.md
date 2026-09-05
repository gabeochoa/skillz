# skillz

Gabe's personally-maintained agent skills, kept separate from platform and vendor
skill bundles so they survive machine resets and live in their own git history.

## Purpose

`~/.claude/skills/` on any given machine is a mix of:

1. Personal skills, authored or curated here, meant to travel between machines.
2. Vendor and platform skill packs, installed by the agent tooling itself.

This repo tracks both, but not on the same terms. Personal work is the point of
the repo. Vendored packs are tracked only where their licence permits it, with
the upstream, the licence, and the exact commit recorded per skill.
`THIRD_PARTY_NOTICES.md` says what came from where.

## Remote and visibility

The remote is **private**, measured with `gh repo view`, not inferred from the
SSH URL:

```
$ gh repo view gabeochoa/skillz --json visibility,isPrivate,licenseInfo
{"isPrivate":true,"licenseInfo":null,"visibility":"PRIVATE"}
```

The tracked tree is nonetheless written to be publishable on its own, so that
flipping it public is a decision rather than a cleanup project. Backup readiness
and public-redistribution readiness are tracked separately in `PUSH_BLOCKED.md`.

## Categories

Skills are grouped by what they are for. The group directory categorizes the
source tree only: every skill installs flat to `~/.claude/skills/<slug>`, so the
group name is not part of a skill's installed identity.

| Group | Skills | What lives here |
|---|---|---|
| `coding` | 18 | How code gets written: design discipline and the principle set |
| `agent-workflow` | 10 | How an agent runs a job: playbooks, delegation, reflection, recall |
| `build-test-release` | 8 | Proving a change works before and after it ships |
| `writing` | 6 | Voice, plain language, and stripping AI tells out of prose |
| `product-ux` | 3 | Design-space, experience-first, and customer-outcome judgment |
| `research-data` | 2 | Explaining how something works and why it came to be |
| `operations` | 2 | Environment setup and keeping an auditable decision log |
| **total** | **49** | no ungrouped skills |

By origin: 44 vendored from pstack under MIT, 4 the owner's own work, 1 derived
from an MIT-licensed upstream.

`manifest.json` is the index: per skill, its `source_path`, group, both tree
hashes, and full provenance including upstream commit and licence.
`MANIFEST.md` is the readable version of the same table.

## Source-of-truth rule

- `skills/<group>/<slug>/SKILL.md` (plus any referenced assets and scripts) here
  is canonical.
- The installed copy at `~/.claude/skills/<slug>/` is a deployment target, not a
  source. Edit here, then run `bin/install.sh` to sync out.
- `manifest.json` records the hash of each skill's tracked tree as last verified.
  `bin/check.sh` reports drift between manifest, source, and installed copies.
- Where the tracked copy deliberately differs from what upstream ships, the
  difference is recorded under `variants` in `manifest.json` rather than being
  silently reconciled in either direction.
- No secrets, credentials, serials, or other private data belong in this repo.
  Skills are prose and config, not data.

## Layout

```
skillz/
  README.md
  CONTRIBUTING.md
  MANIFEST.md               # readable skill table
  INVENTORY.md              # what each machine holds, and what was excluded
  CONFLICTS.md              # merge collisions, variants, and deferred items
  THIRD_PARTY_NOTICES.md    # upstream origins, licences, and pinned commits
  OVERLAY.md                # the untracked local layer, and how to rebuild it
  LICENSE_DECISION.md       # why there is no LICENSE file yet
  PUSH_BLOCKED.md           # backup readiness vs public readiness
  manifest.json             # slug -> source path, installed paths, hashes, provenance
  .gitignore
  skills/<group>/<slug>/SKILL.md
  licenses/                 # full text of every bundled third-party licence
  bin/install.sh            # idempotent: skills/ (+ optional overlay) -> ~/.claude/skills/
  bin/check.sh              # verify manifest hashes + drift vs installed copies
  bin/public_check.py       # fail content that is not safe to publish
  bin/tree_hash.py          # the canonical tree-hash recipe
  bin/tests/                # unit tests for the public check
```

## Install and sync

```bash
# Install everything in skills/ into ~/.claude/skills/ (atomic per skill, backs
# up anything it would overwrite):
bin/install.sh

# Install one skill only:
bin/install.sh --only customer-obsession

# Also merge the machine-local overlay (see OVERLAY.md):
bin/install.sh --with-overlay

# Dry run (prints what it would do, changes nothing):
bin/install.sh --dry-run

# Test against a scratch HOME instead of touching the real one:
HOME=/tmp/scratch-home bin/install.sh
```

```bash
# Verify manifest hashes match skills/ source, and (read-only) report drift
# against what is actually installed at $HOME/.claude/skills:
bin/check.sh

# Same, for a machine that installed the overlay too:
bin/check.sh --with-overlay
```

`bin/check.sh` warns that `poteto-mode`'s frontmatter `name` does not match its
directory slug. That is upstream's own spelling, kept deliberately so the tracked
copy stays byte-identical to the pinned commit. The warning is expected.

## Portable by default

Nothing tracked here names an employer, an internal system, a host, a machine, or
a colleague, and nothing tracked here is verbatim third-party content the repo
has no right to redistribute.

- `.local-meta/` holds the private originals that generic skills were derived
  from, the employer-specific adapters, the private denylist, and the local
  overlay. It is gitignored and `bin/public_check.py` refuses to scan it.
- A generic-only install is the default. Overlay material is opt-in and never
  required to use anything in `skills/`.

`bin/public_check.py` enforces this. Run all three before publishing:

```bash
python3 -m unittest discover -s bin/tests      # rule tests
python3 bin/public_check.py                    # generic rules
python3 bin/public_check.py --rules .local-meta/rules/internal_denylist.txt --strict
```

The third is the one that matters, and it only runs on a machine that has
`.local-meta/`. The scanner reads the working tree, not history: anything already
committed is out of its reach.

## Attribution

Most of `skills/` is vendored rather than authored here.
`THIRD_PARTY_NOTICES.md` records each origin, the files it covers, its licence,
and the artifact that licence was read from. Every vendored licence's full text
is in `licenses/`.

This repo has no `LICENSE` file of its own. Until one is chosen, the owner's own
work is all rights reserved by default and public redistribution is blocked. See
`LICENSE_DECISION.md`.
