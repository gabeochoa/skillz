#!/usr/bin/env python3
"""Print the tree hash of a directory, using the repo's canonical recipe.

    python3 bin/tree_hash.py path/to/skill

The hash is sha256 over sorted "sha256 relpath" lines, so it is stable across
machines, copy order, and mtimes. Use it to decide whether an incoming skill
is the same content as one already here.
"""
import hashlib
import os
import sys

SKIP_DIRS = {".git", "node_modules", "__pycache__"}
SKIP_FILES = {".DS_Store"}


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(root):
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if fn in SKIP_FILES:
                continue
            full = os.path.join(dirpath, fn)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            entries.append((os.path.relpath(full, root), file_sha256(full)))
    entries.sort()
    src = "\n".join("%s %s" % (d, p) for p, d in entries)
    return hashlib.sha256(src.encode()).hexdigest(), entries


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    root = argv[1]
    if not os.path.isdir(root):
        print("not a directory: %s" % root)
        return 2
    digest, entries = tree_hash(root)
    print("%s  %s  (%d files)" % (digest, root, len(entries)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
