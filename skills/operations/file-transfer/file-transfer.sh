#!/usr/bin/env bash
set -euo pipefail
die() { echo "error: $*" >&2; exit 1; }
: "${TRANSFER_API_KEY:?TRANSFER_API_KEY is not set}"
: "${TRANSFER_API_BASE_URL:?TRANSFER_API_BASE_URL is not set}"

cmd_upload() {
  local file="${1:?Usage: file-transfer upload <file>}"
  [ -f "$file" ] || die "file not found: $file"
  local resp
  resp=$(curl -sf -X POST "${TRANSFER_API_BASE_URL}/api/upload" \
    -H "x-api-key: ${TRANSFER_API_KEY}" \
    -F "file=@${file}") || die "upload request failed"
  echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['handle'])" \
    || die "upload failed: $resp"
}

cmd_download() {
  local handle="${1:?Usage: file-transfer download <handle> [dest]}"
  local dest="${2:--}"
  local enc
  enc=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1],safe=''))" "$handle")
  if [ "$dest" = "-" ]; then
    curl -sfL "${TRANSFER_API_BASE_URL}/api/download?handle=${enc}" \
      -H "x-api-key: ${TRANSFER_API_KEY}" \
      || die "download failed: $handle"
  else
    curl -sfL "${TRANSFER_API_BASE_URL}/api/download?handle=${enc}" \
      -H "x-api-key: ${TRANSFER_API_KEY}" \
      -o "$dest" || die "download failed: $handle"
    echo "$dest"
  fi
}

case "${1:-}" in
  upload)   shift; cmd_upload "$@" ;;
  download) shift; cmd_download "$@" ;;
  *)        echo "Usage: file-transfer <upload|download> [args...]"
            echo "  upload <file>              Upload file, prints a handle"
            echo "  download <handle> [dest]   Download handle to dest (default: stdout)"
            exit 1 ;;
esac
