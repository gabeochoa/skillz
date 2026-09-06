#!/usr/bin/env python3
"""Audit tts-narration beat timing for cadence/pacing problems.

Usage:
  python3 check_pacing.py narration_beats.json
  python3 check_pacing.py narration_beats.json --min-wps 1.5 --max-wps 3.2
"""
import argparse, json, re

def count_words(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9']*", text))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("beats_json")
    ap.add_argument("--min-wps", type=float, default=1.4)
    ap.add_argument("--target-min-wps", type=float, default=1.7)
    ap.add_argument("--target-max-wps", type=float, default=3.0)
    ap.add_argument("--max-wps", type=float, default=3.3)
    ap.add_argument("--max-words", type=int, default=22)
    ap.add_argument("--max-duration", type=float, default=7.5)
    ap.add_argument("--min-gap", type=float, default=0.18)
    ap.add_argument("--max-gap", type=float, default=0.90)
    args = ap.parse_args()

    data = json.load(open(args.beats_json))
    beats = data.get("beats", [])
    any_flags = False
    print("beat words dur_s wps gap_after flags text")
    for idx, b in enumerate(beats):
        text = b.get("text", "")
        wc = count_words(text)
        dur = max(0.001, float(b["end"]) - float(b["start"]))
        wps = wc / dur
        gap = None
        if idx + 1 < len(beats):
            gap = float(beats[idx + 1]["start"]) - float(b["end"])
        flags = []
        if wc > args.max_words:
            flags.append(f"SPLIT>{args.max_words}w")
        if dur > args.max_duration:
            flags.append(f"LONG>{args.max_duration}s")
        if wps < args.min_wps:
            flags.append("SLOW")
        elif wps < args.target_min_wps:
            flags.append("slightly-slow")
        if wps > args.max_wps:
            flags.append("RUSHED")
        elif wps > args.target_max_wps:
            flags.append("slightly-fast")
        if gap is not None and gap < args.min_gap:
            flags.append("CRAMPED_GAP")
        if gap is not None and gap > args.max_gap:
            flags.append("LONG_GAP")
        any_flags = any_flags or bool(flags)
        gap_s = "" if gap is None else f"{gap:.2f}"
        print(f"{b.get('i', idx):>4} {wc:>5} {dur:>5.2f} {wps:>4.2f} {gap_s:>8} {','.join(flags) or 'ok':<24} {text}")
    if any_flags:
        print("\nFix cadence by splitting/merging/rewording beats or adjusting GAP_S, then re-render.")
    else:
        print("\nPacing checks passed under current thresholds.")

if __name__ == "__main__":
    main()
