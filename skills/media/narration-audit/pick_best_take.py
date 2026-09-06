#!/usr/bin/env python3
"""Given several REWORDED variant WAVs for one beat, STT each and pick the variant that
transcribes cleanest against the required key words. (TTS is deterministic, so variants must
differ in INPUT TEXT — not re-rolls of the same text.)

Usage:
  python3 pick_best_take.py --glob '/tmp/fix/beat08_v*.wav' \
    --require handles sessions search results [--model medium]
"""
import subprocess, json, os, sys, argparse, re, glob as globmod

def norm(t): return re.sub(r"[^a-z0-9 ]", " ", t.lower()).split()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", required=True)
    ap.add_argument("--require", nargs="+", required=True, help="key words that MUST appear")
    ap.add_argument("--whisper", default=os.path.expanduser("~/whisper-venv/bin/whisper"))
    ap.add_argument("--model", default="medium")
    ap.add_argument("--outdir", default="/tmp/audit_takes")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    rows = []
    for wav in sorted(globmod.glob(args.glob)):
        base = os.path.splitext(os.path.basename(wav))[0]
        jsonf = f"{args.outdir}/{base}.json"
        if not os.path.exists(jsonf):
            subprocess.run([args.whisper, wav, "--model", args.model, "--language", "en",
                            "--output_format", "json", "--output_dir", args.outdir], check=True)
        txt = json.load(open(jsonf))["text"].strip()
        words = norm(txt)
        hits = sum(1 for kw in args.require if kw.lower() in words)
        rows.append((hits, wav, txt))
    rows.sort(key=lambda r: -r[0])
    print("=== VARIANTS (best first) ===")
    for hits, wav, txt in rows:
        clean = "CLEAN" if hits == len(args.require) else f"{hits}/{len(args.require)}"
        print(f"  [{clean}] {os.path.basename(wav)}: {txt}")
    best = rows[0]
    print(f"\nPICK: {os.path.basename(best[1])}  ({best[0]}/{len(args.require)} key words)")

if __name__ == "__main__":
    main()
