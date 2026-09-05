# Third-party notices

Most of `skills/` is vendored rather than authored here. This file records where
each piece came from, which files it covers, and what is known about its licence.

Nothing below is a guess. Every licence claim names the artifact it was read
from. Where something could not be established, it says so, and `PUSH_BLOCKED.md`
says what is left to decide.

## Summary

| Origin | Files covered | Licence | Proven from |
|---|---|---|---|
| pstack (`cursor/plugins`) | 44 skills | MIT, © 2026 Lauren Tan | `pstack/LICENSE` at a pinned commit, read from a local clone and re-read from the GitHub API |
| ponytail | `skills/coding/ponytail-lazy-coding/` | MIT, © 2026 DietrichGebert | upstream `LICENSE` file, read from two independent local copies |
| tropes.fyi taxonomy | part of `skills/writing/gabe-writing/references/ai-tells.md` | no terms published | the public site, checked this pass |
| repo owner | `skills/writing/gabe-writing/`, `skills/writing/in-my-voice/`, `skills/product-ux/customer-obsession/`, `skills/coding/value-oriented-programming/`, all of `bin/`, and the repo's own docs | the owner's own work | authorship |

44 + 1 + 4 = 49 tracked skills. `manifest.json` carries the same facts per skill
under `provenance`, and is the machine-readable version of this file.

## pstack

Covers the 44 skills whose `manifest.json` entry records
`"upstream_repo": "https://github.com/cursor/plugins"`. List them with:

```bash
jq -r '.skills[] | select(.provenance.upstream_repo // "" | contains("cursor/plugins")) | .slug' manifest.json
```

| Fact | Value |
|---|---|
| Upstream repository | `https://github.com/cursor/plugins` (public) |
| Path within it | `pstack/skills/<slug>` |
| Pinned commit | `46125561306434d8a1d7745d540d8932ab0cd2a2`, dated 2026-08-21T03:10:04Z |
| Plugin version at that commit | `0.14.2`, from `pstack/.cursor-plugin/plugin.json` |
| Licence | MIT |
| Copyright | (c) 2026 Lauren Tan |
| Full text | `licenses/pstack-MIT.txt`, sha256 `bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e` |

How it was established, after an earlier pass recorded it as unprovable:

1. A shell-history line recorded a clone of `cursor/plugins`, followed by a `cd`
   into `plugins/pstack`. That clone is still on the machine, clean, at commit
   `4612556`.
2. `pstack/LICENSE` was read from it directly: MIT, © 2026 Lauren Tan.
3. `cursor/plugins` was confirmed to be a public repository, and the same
   `LICENSE` blob was re-read from the GitHub contents API pinned to that exact
   commit. Both reads agree, 1067 bytes, blob
   `6b5400237fdf6545be0b8fae370d6f2fcff8fb25`.
4. `pstack/.cursor-plugin/plugin.json` at the same commit independently declares
   `"license": "MIT"`.
5. `licenses/pstack-MIT.txt` is a verbatim copy, diffed byte-identical against
   both the clone and the API read.

MIT requires the copyright notice and permission notice to travel with copies and
substantial portions, which `licenses/pstack-MIT.txt` does.

**Which copies are verbatim.** 42 of the 44 are byte-identical to the pinned
commit, verified by tree hash. Two are modified here:

| Skill | Change |
|---|---|
| `automate-me` | one bullet in the preferences list, disambiguated |
| `poteto-mode` | the principle-group heading in `SKILL.md`, and one line in `playbooks/eval.md` |

Both changes exist because a bare capitalized word meaning "meta-level" was
indistinguishable from an employer name to the publishability scanner. MIT
permits modified copies. Each skill's `manifest.json` entry records
`matches_upstream_at_pinned_commit` so the two are never mistaken for verbatim.

## ponytail

Covers `skills/coding/ponytail-lazy-coding/SKILL.md`, a condensed derivative, not
a verbatim copy.

- Upstream: `github.com/DietrichGebert/ponytail`
- Licence: MIT, copyright (c) 2026 DietrichGebert
- Read from: the `LICENSE` file of a local clone at commit
  `45f7d2f83fb430a65fd512a98ad7b14d79e06636`, whose `.claude-plugin/plugin.json`
  reads `4.7.0` and whose `package.json` reads `"license": "MIT"`.
- Corroborated by: the separately installed marketplace copy of the same plugin
  on this machine, version `4.8.4` at commit
  `16f29800fd2681bdf24f3eb4ccffe38be3baec6b`.
- The `LICENSE` file is byte-identical in both, sha256
  `fb1bc6909ac3ef82d5c22106e32ef682b0cff66788fa915fb9b53b15c9d2f3ab`, and
  `licenses/ponytail-MIT.txt` matches that hash.

The skill body names the upstream project and its licence.

## tropes.fyi

`skills/writing/gabe-writing/references/ai-tells.md` uses the public tropes.fyi
taxonomy of AI writing tells, restated rather than copied.

Checked this pass: the site publishes no terms. `/terms`, `/about`, and
`/license` all return 404, and the served page carries no licence statement. So
the taxonomy is attributed-but-unlicensed, and the mitigation is the one already
in place: the reference keeps the restatement, never the original wording. That
is why this is not a blocker.

## in-my-voice

`skills/writing/in-my-voice/` is the owner's own text. It was written after
reading a same-named skill served by an agent platform's skill loader, whose
source lives in the employer's monorepo and is therefore proprietary and
unpublishable. The unsanitized loader body is kept out of the tracked tree, under
`.local-meta/`.

Measured against that retained source this pass:

| Measure | Result |
|---|---|
| Sentences shared verbatim | 0, across `SKILL.md` and both reference files |
| Longest shared run in `SKILL.md` | 66 characters, the list of literal routing keywords a user types |
| Other shared runs | the slash-command name and its argument line, and one config file path |
| Share of tracked bytes in runs of 40+ characters | 2.8% of `SKILL.md`, 0% of `post-types.md`, 1.4% of `profile-fields.md` |

Two example lines and one sentence that still echoed the source were reworded in
this pass, which removed every remaining prose run. What is left is functional:
a command name, its arguments, the words a user types to trigger a route, and a
path. The prose is the owner's.

What is not eliminated is the idea and the shape: compile a voice profile from
past writing, then draft to it, with post types and a change-summary workflow.
That is a residual judgment call for the owner, recorded in `PUSH_BLOCKED.md`,
not an unproven fact.

## value-oriented-programming

`skills/coding/value-oriented-programming/SKILL.md` is the owner's own
distillation of two public C++Now talks by Tony Van Eerd, "You Say You Want to
Write a Function" (Part 1, 2023) and "Return of the Values" (Part V, 2024). The
talks are attributed in the skill body. It is not part of pstack or any other
bundled pack.

The installed copy on the owner's machine also carries `excerpts-part1.md` and
`excerpts-part5.md`: roughly 28KB of verbatim auto-generated caption transcript
from those two talks. That is substantial verbatim third-party content with no
licence granting redistribution, so it is not tracked. It lives in the untracked
local overlay instead, and `OVERLAY.md` records what it is and how to re-obtain
it. `SKILL.md` does not reference those files and is complete without them.

## The owner's own work

Authored here and covered by whatever licence the repo itself adopts:

- `skills/writing/gabe-writing/`, built on the tropes.fyi taxonomy noted above
- `skills/writing/in-my-voice/`
- `skills/product-ux/customer-obsession/`
- `skills/coding/value-oriented-programming/`
- `bin/` in full, including `public_check.py`, `install.sh`, `check.sh`,
  `tree_hash.py`, and the tests
- `README.md`, `CONTRIBUTING.md`, `MANIFEST.md`, `INVENTORY.md`, `CONFLICTS.md`,
  `OVERLAY.md`, `LICENSE_DECISION.md`, this file, and `PUSH_BLOCKED.md`

This repo carries no `LICENSE` file. Until the owner chooses one, that work is
all rights reserved by default. See `LICENSE_DECISION.md`.
