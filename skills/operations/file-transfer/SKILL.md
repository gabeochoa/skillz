---
name: file-transfer
description: >
  Move files between machines without the model touching file content. Uploads to a blob
  endpoint on the source machine and downloads on the target; only a short handle passes
  through the conversation. Use when you need to copy a file from one machine to another —
  laptop to remote box, remote box to laptop, or between two remote boxes — or when a task
  needs a script that exists on one machine but must run on another.
---

# File transfer between machines

Separate machines have separate filesystems. To move a file, upload from the source and
download on the target. Only the short handle passes through the model — never the bytes.

## Two transports

| Situation | Use |
|---|---|
| Both machines reachable over SSH | `scp` / `rsync -avz` — no setup, no service |
| No direct route between them (agent sandboxes, NAT, different networks) | the blob endpoint below |

## Blob endpoint setup

`file-transfer.sh` needs two environment variables on every machine that uses it:

```bash
export TRANSFER_API_BASE_URL=https://your-blob-service.example.com
export TRANSFER_API_KEY=...
```

The service must expose `POST /api/upload` (multipart `file=@...`, returns JSON with a
`handle` field) and `GET /api/download?handle=<urlencoded>`. Any signed-URL object store
behind a thin wrapper works; so does a self-hosted one.

## Upload

```bash
handle=$(bash file-transfer.sh upload /path/to/file.py)
```

Prints a short handle (~100 chars).

## Download

```bash
bash file-transfer.sh download "$handle" /path/to/dest.py
```

Omit the destination to write to stdout.

## Complete example: laptop to remote box

```bash
# on the laptop
handle=$(bash file-transfer.sh upload scripts/digest.py)

# on the remote box
bash file-transfer.sh download "$handle" /tmp/digest.py
```

## Size limits

- Treat 25 MB as the nominal ceiling.
- Uploads fail transiently well below that; a failed upload is not always a size cap.
- Zero-byte files are rejected.

## Reliable large or binary transfer

Prefer doing the work on the machine where the data and tools already live. If a direct
transfer fails or the artifact is large:

1. Split into 1-3 MB chunks — more reliable than one big upload.
2. Upload chunks with retries; record every handle.
3. Download all chunks on the target.
4. Reassemble with `cat part-* > artifact.ext`.
5. Verify with `shasum` and a format probe (`ffprobe`, `tar -tzf`).

Do not blindly retry a whole large upload. One failed shard can be retried on its own.

## When not to transfer

- **Under 2 KB**: use a heredoc directly on the target.
- **You only need the logic**: rewrite it inline on the target.

## Common mistakes

### Do not base64 and paste through tool calls
The model becomes the transport and burns thousands of tokens on gibberish.

### Do not assume shared paths
`/tmp/file.py` on one machine is not `/tmp/file.py` on another.

### Create the destination directory first
`curl -o /nonexistent/dir/file.py` fails quietly. `mkdir -p` first.
