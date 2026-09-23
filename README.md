# skillz

Personal and vendored agent skills. The source of truth is `dotfiles/skillz/`,
a regular folder in the private dotfiles repository; this tree is mirrored to
the standalone `skillz` repository for sharing.

## Install

From the dotfiles root, install the dotfiles and all skills for both Claude Code
and Codex:

```sh
./install.sh --dry-run
./install.sh
```

Claude Code receives the individual skills in `~/.claude/skills/`.
Codex receives the full files in `~/.codex/skill-library/`, outside automatic
discovery, plus one small `skill-index` entry in `~/.codex/skills/`.

Say “make a video” to load the video workflow, “review this UI” to load the UI
review skill, or name a skill directly. The index reads only the relevant skill
and its references as the work needs them. Ordinary tasks do not require a
personal workflow. Restart Codex after switching an existing installation to
this layout so the old skill list leaves the session context.

The installer archives existing individual Codex skill copies under
`skillz/backups/`. Extra personal skills move into the library and appear in the
catalog. System skills and plugin installations stay intact.

To update one skill for Claude Code:

```sh
cd skillz
./bin/install.sh --only clean-copy
```

To update one skill in the Codex library and refresh its index:

```sh
./bin/install.sh --dest ~/.codex/skill-library --only clean-copy
python3 bin/install_index.py
```

Add `--dry-run` to preview either installer. Matching directories are skipped
using direct comparisons. Edit source files under `skills/`, then reinstall.
The index instructions live in `index/SKILL.md`; its catalog is generated from
the installed library, so there is no second skill list to maintain by hand.

## Collection

The collection contains 66 skills across eight categories:

| Category | Skills |
|---|---:|
| agent-workflow | 10 |
| build-test-release | 9 |
| coding | 19 |
| media | 7 |
| operations | 5 |
| product-ux | 7 |
| research-data | 2 |
| writing | 7 |

Recent additions include `design-taste-quiz`, `ui-screenshot-review`, `fun-loop`,
`clean-copy`, and `afterhours-save-load`. The collection also retains the twelve
earlier imports for interface design, layout checks, file transfer, skill
evaluation, and video production.

[MANIFEST.md](MANIFEST.md) lists every skill. [manifest.json](manifest.json)
records source paths and provenance. The separate ponytail variants
remain outside this collection; the portable
`ponytail-lazy-coding` skill is included.

## Verify and update

From this folder:

```sh
./bin/install.sh --dry-run
python3 -m unittest discover -s bin/tests
python3 bin/public_check.py
```

The dry run reports `up to date` for identical skills and `would install` for
missing or changed copies. Add `--dest ~/.codex/skill-library` to check Codex instead
of Claude Code. It does not write to either installation.

After adding a skill, add its source path and provenance to `manifest.json`,
update the counts and `MANIFEST.md`, and record any attribution in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Editing a skill does not
require regenerating checksums.

Run `python3 tests/verify.py` from the dotfiles root to exercise the full
installation into a temporary home, including both skill destinations.

## Local overlays

`.local/` is an ignored, machine-specific overlay. It is preserved locally
when moving an existing checkout, but is not required for a normal install.
To merge it over the portable skills for a particular destination:

```sh
./bin/install.sh --with-overlay --dest ~/.claude/skills
./bin/install.sh --dry-run --with-overlay
```

See [OVERLAY.md](OVERLAY.md) for its layout. Backups and local overlays stay
untracked. The dotfiles installer uses the portable collection by default.

## Attribution and history

Vendored material retains its upstream terms and notices in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and `licenses/`.
No new collection-wide licence is granted by moving these files into dotfiles.
`clean-copy` was imported from the local installation without an upstream
licence declaration.

[INVENTORY.md](INVENTORY.md), [CONFLICTS.md](CONFLICTS.md), and
[PUSH_BLOCKED.md](PUSH_BLOCKED.md) retain the earlier collection and licensing
assessments. Statements there about the standalone repository's remote or
visibility are historical; the parent dotfiles repository now owns these files.
