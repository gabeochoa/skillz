#!/usr/bin/env python3
"""STT-audit a rendered narration: transcribe it back and diff against the intended script to
catch mispronunciations/garbles the ear misses. The single highest-value QA trick for TTS.

Usage:
  python3 audit_narration.py narration.wav --script script.txt [--model medium]
  # script.txt: one intended sentence per line (the SCRIPT you rendered)

Prints a word-level diff (intended vs heard) and flags beats needing a reword.
Use --model medium to ADJUDICATE: when small & medium disagree, medium wins; when BOTH agree a
word is wrong, it's a real delivery flaw (not an STT artifact).
"""
import subprocess, json, os, sys, argparse, re, difflib

def norm(t):
    # Optional token normalization for brand/shortcut words the STT splits (e.g. "brandname" ->
    # "brand name"): set NORM_MAP="brandname=brand name;foo=f o o".
    for pair in os.environ.get("NORM_MAP", "").split(";"):
        if "=" in pair:
            a, b = pair.split("=", 1); t = t.lower().replace(a.strip(), b.strip())
    return re.sub(r"[^a-z0-9 ]", " ", t.lower()).split()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--script", help="file with one intended sentence per line")
    ap.add_argument("--text", help="intended text inline (alternative to --script)")
    ap.add_argument("--whisper", default=os.path.expanduser("~/whisper-venv/bin/whisper"))
    ap.add_argument("--model", default="medium", help="small=fast, medium=authoritative adjudicator")
    ap.add_argument("--outdir", default="/tmp/audit")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.audio))[0]
    jsonf = f"{args.outdir}/{base}.json"
    if not os.path.exists(jsonf):
        subprocess.run([args.whisper, args.audio, "--model", args.model, "--language", "en",
                        "--output_format", "json", "--output_dir", args.outdir], check=True)
    data = json.load(open(jsonf))
    heard = " ".join(s["text"].strip() for s in data["segments"])

    print("=== HEARD (%s model) ===" % args.model)
    for s in data["segments"]:
        print(f"[{s['start']:6.2f}-{s['end']:6.2f}] {s['text'].strip()}")

    intended = ""
    if args.script and os.path.exists(args.script):
        intended = " ".join(l.strip() for l in open(args.script) if l.strip())
    elif args.text:
        intended = args.text
    if not intended:
        print("\n(no --script/--text given; transcript only)")
        return

    print("\n=== WORD DIFF (intended vs heard) ===")
    sm = difflib.SequenceMatcher(None, norm(intended), norm(heard))
    bad = False
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            bad = True
            print(f"  {tag:8} intended={norm(intended)[i1:i2]}  heard={norm(heard)[j1:j2]}")
    if not bad:
        print("  CLEAN — transcript matches script (contraction/possessive tokenization aside).")
    else:
        print("\nFor each real mismatch: reword that beat's INPUT text and re-render just that beat.")
        print("Common fixes: drop hyphens; 'Here's X' -> 'Here is X'; add 'also' to force plural 's'.")

if __name__ == "__main__":
    main()
