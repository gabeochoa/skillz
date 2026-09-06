#!/usr/bin/env bash
# Normalize all frames to one resolution (fixes retina 2x mismatch) with top-left anchor pad.
# Usage: bash normalize_frames.sh SRC_DIR DST_DIR WIDTH HEIGHT [bgcolor]
set -euo pipefail
SRC="${1:?src dir}"; DST="${2:?dst dir}"; W="${3:-1280}"; H="${4:-773}"; BG="${5:-0x171717}"
mkdir -p "$DST"
for f in "$SRC"/*.png; do
  b="$(basename "$f")"
  ffmpeg -y -loglevel error -i "$f" -vf "scale=${W}:-1,pad=${W}:${H}:0:0:color=${BG}" "$DST/$b"
done
echo "normalized $(ls "$DST"/*.png | wc -l) frames to ${W}x${H}"
