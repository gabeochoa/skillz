#!/usr/bin/env bash
# Idempotently install skills into $HOME/.claude/skills/<slug>.
# Atomic per skill: stage in a temp dir on the destination filesystem, back up
# whatever is currently there (if different), then move the staged copy in.
#
# Usage:
#   bin/install.sh                    # install every skill under skills/
#   bin/install.sh --only slug1,slug2
#   bin/install.sh --with-overlay     # also merge .local/skills over the tracked tree
#   bin/install.sh --dry-run          # print what would happen, change nothing
#   bin/install.sh --dest ~/.codex/skills  # choose another installation directory
#   HOME=/tmp/scratch bin/install.sh  # install into a scratch HOME (testing)
#
# Layout: a skill is any directory holding a SKILL.md, flat (skills/<slug>/) or
# grouped (skills/<group>/<slug>/). Both install to $DEST_ROOT/<slug>; the group
# directory categorizes the source tree only and is not part of the installed name.
#
# Overlay: .local/skills/<slug>/ is an optional, untracked, machine-local
# layer. With --with-overlay its files are merged over the tracked skill of the
# same name (overlay wins on a filename collision), and an overlay-only skill
# that carries its own SKILL.md is installed too. Without the flag the overlay is
# ignored entirely, which is what makes a tracked-only install the default.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
OVERLAY_SRC="$REPO_ROOT/.local/skills"
DEST_ROOT="${HOME}/.claude/skills"
BACKUP_ROOT="$REPO_ROOT/backups"
ONLY=""
DRY_RUN=0
WITH_OVERLAY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dest)
      [ $# -ge 2 ] && [ -n "$2" ] || { echo '--dest needs a directory' >&2; exit 2; }
      DEST_ROOT="$2"; shift 2 ;;
    --only) ONLY="$2"; shift 2 ;;
    --only=*) ONLY="${1#*=}"; shift ;;
    --with-overlay) WITH_OVERLAY=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help)
      sed -n '2,20p' "$0"
      exit 0
      ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

[ -d "$SKILLS_SRC" ] || { echo "no skills/ dir found at $SKILLS_SRC" >&2; exit 1; }

if [ "$WITH_OVERLAY" -eq 1 ] && [ ! -d "$OVERLAY_SRC" ]; then
  echo "--with-overlay given but no overlay at $OVERLAY_SRC" >&2
  exit 1
fi

if [ "$DRY_RUN" -eq 0 ]; then mkdir -p "$DEST_ROOT"; fi
installed=0
skipped=0
overlaid=0

TMPDIR_WORK="$(mktemp -d -t skillz-install)"
SKILL_LIST="$TMPDIR_WORK/skills.txt"
trap 'rm -rf "$TMPDIR_WORK"' EXIT

# slug<TAB>tracked_dir_or_-<TAB>overlay_dir_or_-
find "$SKILLS_SRC" -mindepth 1 -maxdepth 2 -type d -exec test -f '{}/SKILL.md' ';' -print \
  | sort | while read -r d; do printf '%s\t%s\n' "$(basename "$d")" "$d"; done \
  > "$TMPDIR_WORK/tracked.tsv"

: > "$SKILL_LIST"
while IFS=$'\t' read -r slug dir; do
  ov="-"
  if [ "$WITH_OVERLAY" -eq 1 ] && [ -d "$OVERLAY_SRC/$slug" ]; then ov="$OVERLAY_SRC/$slug"; fi
  printf '%s\t%s\t%s\n' "$slug" "$dir" "$ov" >> "$SKILL_LIST"
done < "$TMPDIR_WORK/tracked.tsv"

# Overlay-only skills: present in the overlay, carrying a SKILL.md, with no
# tracked skill of that name.
if [ "$WITH_OVERLAY" -eq 1 ]; then
  find "$OVERLAY_SRC" -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/SKILL.md' ';' -print \
    | sort | while read -r d; do
      slug="$(basename "$d")"
      if ! cut -f1 "$TMPDIR_WORK/tracked.tsv" | grep -qx "$slug"; then
        printf '%s\t%s\t%s\n' "$slug" "-" "$d" >> "$SKILL_LIST"
      fi
    done
fi

sort -o "$SKILL_LIST" "$SKILL_LIST"

while IFS=$'\t' read -r slug skill_dir overlay_dir; do
  [ -n "$slug" ] || continue
  if [ -n "$ONLY" ]; then
    case ",$ONLY," in
      *",$slug,"*) : ;;
      *) continue ;;
    esac
  fi

  # Stage tracked, then overlay on top, before comparing with the installed copy.
  stage="$TMPDIR_WORK/stage-$slug"
  rm -rf "$stage"; mkdir -p "$stage"
  if [ "$skill_dir" != "-" ]; then cp -R "$skill_dir/." "$stage/"; fi
  if [ "$overlay_dir" != "-" ]; then cp -R "$overlay_dir/." "$stage/"; overlaid=$((overlaid + 1)); fi
  [ -f "$stage/SKILL.md" ] || { echo "skip $slug: no SKILL.md" >&2; rm -rf "$stage"; continue; }

  dest="$DEST_ROOT/$slug"
  if [ -d "$dest" ] && diff -qr "$stage" "$dest" >/dev/null; then
    echo "up to date: $slug"
    skipped=$((skipped + 1))
    rm -rf "$stage"
    continue
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    if [ "$overlay_dir" != "-" ]; then
      echo "would install: $slug -> $dest (tracked + overlay)"
    else
      echo "would install: $slug -> $dest"
    fi
    installed=$((installed + 1))
    rm -rf "$stage"
    continue
  fi

  # Move the staged copy onto the destination filesystem before the swap, so the
  # swap itself is a rename and never leaves a half-written skill reachable.
  tmp="$DEST_ROOT/.install-tmp-$slug-$$"
  rm -rf "$tmp"
  cp -R "$stage" "$tmp"
  rm -rf "$stage"

  if [ -e "$dest" ] || [ -L "$dest" ]; then
    mkdir -p "$BACKUP_ROOT"
    backup="$(mktemp -d "$BACKUP_ROOT/${slug}.XXXXXXXX")/skill"
    mv "$dest" "$backup"
    echo "backed up existing $slug -> $backup"
  fi

  mv "$tmp" "$dest"
  echo "installed: $slug -> $dest"
  installed=$((installed + 1))
done < "$SKILL_LIST"

echo "---"
echo "installed=$installed skipped=$skipped overlaid=$overlaid dest=$DEST_ROOT dry_run=$DRY_RUN with_overlay=$WITH_OVERLAY"
