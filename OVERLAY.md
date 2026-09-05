# The local overlay

`skills/` is the tracked, portable, redistributable tree. The overlay is the
untracked layer beside it, at `.local-meta/skills/<slug>/`, for material that is
worth keeping on a machine but must not be redistributed from this repo.

This file is tracked. Its contents are not. That is deliberate: a backup story is
only honest if the tracked tree admits what it is missing and says how to get it
back.

## Why anything is held out

One rule decides it: **the tracked tree carries no verbatim third-party content
whose licence does not permit redistribution.** Content that fails that rule is
not deleted, because it is genuinely useful locally. It moves here.

Content that passes stays tracked. That is why all 44 pstack skills are tracked
in full (MIT), and why `ponytail-lazy-coding` is tracked (MIT derivative).

## What is in the overlay right now

| Skill | Files | What it is | Why not tracked |
|---|---|---|---|
| `value-oriented-programming` | `excerpts-part1.md`, `excerpts-part5.md` | ~28KB of verbatim auto-generated caption transcript from two public C++Now talks by Tony Van Eerd | substantial verbatim transcript of a third party's recorded talk, with no licence granting redistribution |

Nothing else. There are no overlay-only skills: every skill installable from this
repo has a tracked `SKILL.md`.

### Re-obtaining it

The two excerpt files are pulled from the auto-generated captions of these talks,
both public:

- *Value Oriented Programming Part 1: You Say You Want to Write a Function*,
  C++Now 2023, `https://www.youtube.com/watch?v=b4p_tcLYDV0`
- *Value Oriented Programming Part V: Return of the Values*, C++Now 2024,
  `https://www.youtube.com/watch?v=sc1guyo5Rso`

Each file quotes the passages the skill relies on, under headings matching the
skill's sections, as unpunctuated transcriber output kept for checkability. To
rebuild: pull the captions for each talk and excerpt the passages behind the
claims in `skills/coding/value-oriented-programming/SKILL.md`.

Losing them costs nothing but the ability to check a quotation. The tracked
`SKILL.md` does not reference them and is complete on its own.

## Installing with the overlay

```bash
bin/install.sh                 # tracked skills only. The default.
bin/install.sh --with-overlay  # tracked, with the overlay merged over it
```

The overlay merges per skill, file by file, over the tracked copy of the same
name; an overlay file wins a filename collision. A skill that exists only in the
overlay and carries its own `SKILL.md` is installed too. Both modes are atomic
per skill and idempotent, and the staged copy is hashed before it is moved into
place, so the hash compared is the hash installed.

Without the flag the overlay is ignored entirely. A machine that has never seen
`.local-meta/` installs the whole tracked tree and nothing is missing except the
excerpts above.

## Checking an overlay install

```bash
bin/check.sh                 # expects installed copies to match the tracked tree
bin/check.sh --with-overlay  # expects them to match tracked plus overlay
```

`manifest.json` always records the hash of the **tracked** source. An installed
copy carrying the overlay therefore hashes differently by design, and plain
`bin/check.sh` will honestly call that DRIFT. Pass `--with-overlay` and the
expected hash is computed from a staged tracked-plus-overlay merge, which reports
`OVERLAY` instead. Both answers are true; they answer different questions.

## Adding to the overlay

1. Put it at `.local-meta/skills/<slug>/`, mirroring the installed layout.
2. Add a row to the table above, with what it is, why it cannot be tracked, and
   how to re-obtain it.
3. Record it under `overlay.contents` in `manifest.json`.
4. Re-run the strict public check. The overlay is gitignored, and
   `bin/public_check.py` refuses to scan `.local-meta/`, so a mistake there will
   not be caught for you.

Do not add anything to the overlay merely because it is private. Private
originals belong in `.local-meta/originals/`, employer-specific instructions in
`.local-meta/adapters/`. The overlay is only for installable skill content.
