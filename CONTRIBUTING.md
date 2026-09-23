# Contributing (compact rules)

- One directory per skill under `skills/<group>/<slug>/`, `SKILL.md` at its root.
  `slug` matches the installed directory name under `~/.claude/skills/`.
- `SKILL.md` keeps its YAML frontmatter (`name`, `description`) intact.
  Keep the description short so it fits the agent's skill list.
- Referenced assets/scripts live alongside `SKILL.md` in the same skill
  directory, not inlined into it, unless they're a few lines.
- No secrets, tokens, serials, fbids, or other PII in any skill file.
- After editing a skill, run `bin/install.sh --dry-run --only <slug>` to
  compare it with the installed copy, then omit `--dry-run` to install it.
  Add source paths and provenance to the manifest when adding a new skill.
- A skill only belongs in `skills/` if it's personally authored/curated —
  platform, vendor, and third-party bundled skills go in `INVENTORY.md`
  instead, not copied in.
