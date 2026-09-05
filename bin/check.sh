#!/usr/bin/env bash
# Verify manifest.json against skills/ source, and (read-only) report drift
# against whatever is actually installed at $HOME/.claude/skills.
#
# Usage:
#   bin/check.sh                  # tracked tree only
#   bin/check.sh --with-overlay   # expect installed copies to carry the local overlay
#
# The manifest always records the hash of the TRACKED source. An installed copy
# that also carries the machine-local overlay from .local-meta/skills/ therefore
# hashes differently by design. With --with-overlay the expected installed hash
# is computed from a staged tracked+overlay merge, so a correct overlay install
# reports OVERLAY instead of a misleading DRIFT.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
OVERLAY_SRC="$REPO_ROOT/.local-meta/skills"
MANIFEST="$REPO_ROOT/manifest.json"
DEST_ROOT="${HOME}/.claude/skills"
WITH_OVERLAY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --with-overlay) WITH_OVERLAY=1; shift ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

command -v jq >/dev/null 2>&1 || { echo "check.sh needs jq" >&2; exit 2; }
[ -f "$MANIFEST" ] || { echo "no manifest.json at $MANIFEST" >&2; exit 1; }

WORK="$(mktemp -d -t skillz-check)"
trap 'rm -rf "$WORK"' EXIT

tree_hash() {
  local dir="${1%/}"
  {
    find "$dir" -type f | sort | while read -r f; do
      h=$(shasum -a 256 "$f" | awk '{print $1}')
      rel="${f#"$dir"/}"
      echo "F:$rel:$h"
    done
    find "$dir" -type l | sort | while read -r l; do
      t=$(readlink "$l")
      rel="${l#"$dir"/}"
      echo "L:$rel:$t"
    done
  } | sort | shasum -a 256 | awk '{print $1}'
}

# Hash of what an install would actually place: tracked, with the overlay merged
# over it when the caller asked for that.
expected_installed_hash() {
  local slug="$1" src_dir="$2"
  if [ "$WITH_OVERLAY" -eq 1 ] && [ -d "$OVERLAY_SRC/$slug" ]; then
    local stage="$WORK/stage-$slug"
    rm -rf "$stage"; mkdir -p "$stage"
    cp -R "$src_dir/." "$stage/"
    cp -R "$OVERLAY_SRC/$slug/." "$stage/"
    tree_hash "$stage"
  else
    tree_hash "$src_dir"
  fi
}

fail=0
seeded=0
pending=0
overlay_seen=0

slugs=$(jq -r '.skills[].slug' "$MANIFEST")
if [ -z "$slugs" ]; then
  echo "manifest has no skill entries"
fi

while IFS= read -r slug; do
  [ -n "$slug" ] || continue
  status=$(jq -r --arg s "$slug" '.skills[] | select(.slug==$s) | .status' "$MANIFEST")

  if [ "$status" = "pending_not_found" ]; then
    pending=$((pending + 1))
    echo "PENDING  $slug (no source bytes yet — see manifest note)"
    continue
  fi

  # Grouped entries carry source_path (skills/<group>/<slug>); flat ones fall
  # back to skills/<slug>.
  src_rel=$(jq -r --arg s "$slug" \
    '.skills[] | select(.slug==$s) | .source_path // ("skills/" + $s)' "$MANIFEST")
  src_dir="$REPO_ROOT/$src_rel"
  if [ ! -d "$src_dir" ]; then
    echo "FAIL     $slug: status=$status but $src_dir is missing" >&2
    fail=1
    continue
  fi
  if [ ! -f "$src_dir/SKILL.md" ]; then
    echo "FAIL     $slug: no SKILL.md in $src_dir" >&2
    fail=1
    continue
  fi

  # frontmatter name (if present) should match the slug
  fm_name=$(sed -n '/^---$/,/^---$/p' "$src_dir/SKILL.md" | sed -n 's/^name: *//p' | head -1 | tr -d '"')
  if [ -n "$fm_name" ] && [ "$fm_name" != "$slug" ]; then
    echo "WARN     $slug: SKILL.md frontmatter name '$fm_name' != directory slug"
  fi

  expected_hash=$(jq -r --arg s "$slug" '.skills[] | select(.slug==$s) | .sha256' "$MANIFEST")
  actual_hash=$(tree_hash "$src_dir")
  if [ "$expected_hash" != "$actual_hash" ]; then
    echo "FAIL     $slug: manifest sha256 stale (manifest=$expected_hash actual=$actual_hash)" >&2
    fail=1
  else
    echo "OK       $slug: manifest hash matches source"
  fi
  seeded=$((seeded + 1))

  if [ -d "$DEST_ROOT/$slug" ]; then
    installed_hash=$(tree_hash "$DEST_ROOT/$slug")
    want_hash=$(expected_installed_hash "$slug" "$src_dir")
    if [ "$installed_hash" = "$want_hash" ]; then
      if [ "$WITH_OVERLAY" -eq 1 ] && [ -d "$OVERLAY_SRC/$slug" ]; then
        overlay_seen=$((overlay_seen + 1))
        echo "OVERLAY  $slug: installed copy matches tracked source plus local overlay"
      fi
    else
      echo "DRIFT    $slug: installed copy at $DEST_ROOT/$slug differs from source (run bin/install.sh)"
    fi
  else
    echo "NOTE     $slug: not installed at $DEST_ROOT/$slug yet"
  fi
done <<< "$slugs"

# An overlay-only skill has no manifest entry by design; say so rather than
# letting it look like the overlay was ignored.
if [ "$WITH_OVERLAY" -eq 1 ] && [ -d "$OVERLAY_SRC" ]; then
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    slug="$(basename "$d")"
    if ! jq -e --arg s "$slug" '.skills[] | select(.slug==$s)' "$MANIFEST" >/dev/null 2>&1; then
      echo "NOTE     $slug: overlay-only skill, untracked by design (no manifest entry)"
    fi
  done < <(find "$OVERLAY_SRC" -mindepth 1 -maxdepth 1 -type d -exec test -f '{}/SKILL.md' ';' -print | sort)
fi

echo "---"
echo "seeded=$seeded pending=$pending overlay_matched=$overlay_seen with_overlay=$WITH_OVERLAY"
exit $fail
