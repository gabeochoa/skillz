# personal-agent-skills

Gabe's personally-maintained agent skills, kept separate from platform/vendor
skill bundles so they survive machine resets and eventually live in their own
git history.

## Purpose

`~/.claude/skills/` on any given machine is a mix of:

1. **Personal skills** — authored or curated by Gabe, meant to travel with him.
2. **Platform/vendor skills** — bundled by the agent tooling itself (agentcloud's
   own catalog, Claude Code's default skill pack, third-party skill packs
   installed via `npx skills add ...`). These are reproducible from their
   source and don't need personal backup.

This repo is the source of truth for class (1) only. Class (2) is inventoried,
never copied in wholesale — see `INVENTORY.md` for what was seen and excluded,
and why.

## Source-of-truth rule

- `skills/<slug>/SKILL.md` (+ any referenced assets/scripts) here is canonical.
- The installed copy at `~/.claude/skills/<slug>/` is a **deployment target**,
  not a source. Edit here, then run `bin/install.sh` to sync out.
- `manifest.json` records the hash of each skill's tree as last verified. If
  the installed copy diverges from the manifest hash, `bin/check.sh` reports
  drift — reconcile by hand, then re-verify.
- No secrets, credentials, serials, or other PII belong in this repo. Skills
  are prose/config, not data.

## Layout

```
personal-agent-skills/
  README.md
  CONTRIBUTING.md
  manifest.json          # slug -> source path, installed paths, hash, status
  .gitignore
  skills/<slug>/SKILL.md # canonical skill source, one dir per skill
  bin/install.sh         # idempotent: skills/ -> ~/.claude/skills/
  bin/check.sh           # verify manifest hashes + drift vs installed copies
```

## Install / sync flow

```bash
# Install everything in skills/ into ~/.claude/skills/ (atomic, backs up
# anything it would overwrite):
bin/install.sh

# Install one skill only:
bin/install.sh --only customer-obsession

# Dry run (prints what it would do, changes nothing):
bin/install.sh --dry-run

# Test against a scratch HOME instead of touching the real one:
HOME=/tmp/scratch-home bin/install.sh
```

```bash
# Verify manifest hashes match skills/ source, and (read-only) report any
# drift against what's actually installed at $HOME/.claude/skills:
bin/check.sh
```

## Status as of this pass (2026-09-05)

`skills/customer-obsession/` is seeded, hash-verified against the installed
copy at `~/.claude/skills/customer-obsession/` (it landed partway through this
session — the folder didn't exist for the first ~10 minutes). Everything else
in `~/.claude/skills/` was inventoried but left out as platform/vendor/bundled;
see `INVENTORY.md` for the full list and reasoning.

## Next step (not run by this pass)

```bash
cd ~/p/personal-agent-skills && git init && git add -A && \
  git commit -m 'seed personal-agent-skills repo'
```
# skillz
