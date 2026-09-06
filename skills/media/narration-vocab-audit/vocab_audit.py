#!/usr/bin/env python3
"""Lightweight first-pass vocab audit for narration scripts.

Usage:
  python3 vocab_audit.py script.txt [--profile profile.json]

profile.json shape (all optional):
{
  "banned_terms": {"utilize": "use", "leverage": "use"},
  "preferred_terms": ["shipping", "proof", "boring"],
  "must_keep_terms": ["ProductName"]
}

This catches obvious generic/formal words. It does not replace the author voice/profile skill.
"""
import argparse, json, re, sys

DEFAULT_REPLACEMENTS = {
    "utilize": "use",
    "leverage": "use",
    "facilitate": "help / make easier",
    "robust": "specific proof",
    "seamless": "specific behavior",
    "comprehensive": "full / complete, or cut it",
    "significant": "big / real, or quantify it",
    "demonstrates": "shows",
    "additionally": "also, or cut it",
    "furthermore": "also, or cut it",
    "in conclusion": "cut the wrap-up",
}
AI_TELLS = [
    "it is worth noting",
    "this is where it gets interesting",
    "let's dive in",
    "let's unpack",
    "at the end of the day",
    "in other words",
]

def words(text):
    return re.findall(r"[a-zA-Z][a-zA-Z']*", text.lower())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", help="one narration beat per line")
    ap.add_argument("--profile", help="optional profile JSON with banned_terms/preferred_terms/must_keep_terms")
    args = ap.parse_args()

    profile = {}
    if args.profile:
        profile = json.load(open(args.profile))
    replacements = dict(DEFAULT_REPLACEMENTS)
    replacements.update(profile.get("banned_terms", {}))

    lines = [l.strip() for l in open(args.script) if l.strip()]
    total_flags = 0
    for i, line in enumerate(lines, 1):
        low = line.lower()
        flags = []
        for term, repl in replacements.items():
            if re.search(r"\b" + re.escape(term.lower()) + r"\b", low):
                flags.append(f"'{term}' -> {repl}")
        for phrase in AI_TELLS:
            if phrase in low:
                flags.append(f"AI/product-copy tell: '{phrase}'")
        if len(words(line)) > 24:
            flags.append(f"long spoken beat: {len(words(line))} words")
        if flags:
            total_flags += len(flags)
            print(f"Beat {i:02d}: {line}")
            for f in flags:
                print(f"  - {f}")
    if total_flags == 0:
        print("No obvious vocab flags. Still run the author/profile review.")
    else:
        print(f"\n{total_flags} flag(s). Rewrite, then run the author/profile review.")

if __name__ == "__main__":
    main()
