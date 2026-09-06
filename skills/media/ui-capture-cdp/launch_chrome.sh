#!/usr/bin/env bash
# Launch an isolated, CDP-debuggable Chrome for UI capture.
# The resulting Chrome is a RAW CDP target — NOT subject to an agent browser node allowlist —
# so Fetch.* / Network.* interception is available. Throwaway profile = no personal tabs/DMs.
#
# Usage: bash launch_chrome.sh [START_URL] [PORT] [WIDTHxHEIGHT]
set -euo pipefail
URL="${1:-about:blank}"
PORT="${2:-9222}"
SIZE="${3:-1280,860}"

# macOS Chrome path; adjust for Linux (google-chrome / chromium).
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || CHROME="$(command -v google-chrome || command -v chromium || true)"
[ -n "$CHROME" ] || { echo "Chrome not found" >&2; exit 1; }

PROF="$(mktemp -d /tmp/ui-capture-profile.XXXX)"
echo "$PROF" > /tmp/ui-capture-profile-path.txt
nohup "$CHROME" \
  --remote-debugging-port="$PORT" \
  --user-data-dir="$PROF" \
  --no-first-run --no-default-browser-check \
  --window-size="$SIZE" \
  "$URL" > /tmp/ui-capture-chrome.log 2>&1 &
echo "launched pid $! (profile: $PROF)"
sleep 3
echo "=== CDP check ==="
curl -s "http://127.0.0.1:${PORT}/json/version" | head -c 300
echo
echo ""
echo "NOTE: fresh profile = NOT logged in. Log in once in the launched window, then capture."
