# Contributing (compact rules)

- One directory per skill under `skills/<slug>/`, `SKILL.md` at its root.
  `slug` matches the installed directory name under `~/.claude/skills/`.
- `SKILL.md` keeps its YAML frontmatter (`name`, `description`) intact —
  `bin/check.sh` reads it to confirm the slug matches the directory.
- Referenced assets/scripts live alongside `SKILL.md` in the same skill
  directory, not inlined into it, unless they're a few lines.
- No secrets, tokens, serials, fbids, or other PII in any skill file.
- After editing a skill here, run `bin/install.sh --only <slug>` to sync it
  out, then `bin/check.sh` to confirm the manifest hash was updated to match.
- A skill only belongs in `skills/` if it's personally authored/curated —
  platform, vendor, and third-party bundled skills go in `INVENTORY.md`
  instead, not copied in.
