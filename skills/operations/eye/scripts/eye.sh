#!/bin/bash
set -euo pipefail
CD="$HOME/.cache/eye"; SD="$(cd "$(dirname "$0")" && pwd)"; SV="$SD/eye-server.mjs"; PF="$CD/eye-server.pid"
case "${1:-help}" in
  start)
    [ -d "$CD/node_modules/playwright" ] || { mkdir -p "$CD"; cd "$CD"; npm init -y --silent >/dev/null 2>&1; npm install playwright pixelmatch pngjs --silent >/dev/null 2>&1; npx playwright install chromium >/dev/null 2>&1; }
    curl -sf http://localhost:9222/json/version >/dev/null 2>&1 || { local b=""; [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ] && b="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; [ -z "$b" ] && command -v google-chrome >/dev/null && b=google-chrome; "$b" --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-eye" --no-first-run --window-size=2400,1350 &>/dev/null &; for i in $(seq 1 30); do curl -sf http://localhost:9222/json/version >/dev/null 2>&1 && break; sleep 0.5; done; }
    kill "$(lsof -ti :9223 2>/dev/null)" 2>/dev/null || true; sleep 1
    NODE_PATH="$CD/node_modules" node "$SV" &; echo $! > "$PF"
    for i in $(seq 1 20); do curl -sf http://localhost:9223/health >/dev/null 2>&1 && { echo "eye-server v3 started"; exit 0; }; sleep 0.25; done;;
  stop) kill "$(lsof -ti :9223 2>/dev/null)" 2>/dev/null; echo stopped;;
  stop-all) kill "$(lsof -ti :9223 2>/dev/null)" 2>/dev/null; kill "$(lsof -ti :9222 2>/dev/null)" 2>/dev/null; echo stopped;;
  health) curl -sf http://localhost:9223/health;;
  *) echo "eye start|stop|stop-all|health";;
esac
