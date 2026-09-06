#!/usr/bin/env python3
"""Analyze speaker transcripts for reusable narration style hints.

Input: plain text transcript, one paragraph/utterance per line. If you have timestamped JSON,
pre-convert it into lines and optionally pass --dur-s for rough words/sec.

Usage:
  python3 analyze_speaker_style.py natural_stories.txt
  python3 analyze_speaker_style.py natural_stories.txt --dur-s 420
"""
import argparse, collections, json, re

COMMON = set("""the a an and or but if then so because to of in on for with at by from up out into over after before is are was were be been being this that these those it its you your we our they their i me my as not no yes do does did can could should would will just really actually like kind sort thing things stuff way get got make made use used show shows ship shipped fix fixed""".split())
VOWELS = "aeiouy"

def sentences(text):
    parts = re.split(r"[.!?]+", text)
    return [p.strip() for p in parts if p.strip()]

def words(text):
    return re.findall(r"[A-Za-z][A-Za-z']*", text.lower())

def syllables(word):
    word = word.lower().strip("'")
    if not word:
        return 0
    count = 0
    prev = False
    for ch in word:
        isv = ch in VOWELS
        if isv and not prev:
            count += 1
        prev = isv
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)

def fk_grade(text):
    s = max(1, len(sentences(text)))
    w = words(text)
    wc = max(1, len(w))
    syl = sum(syllables(x) for x in w)
    return 0.39 * (wc / s) + 11.8 * (syl / wc) - 15.59

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--dur-s", type=float, help="duration in seconds for rough words/sec")
    ap.add_argument("--json-out")
    args = ap.parse_args()
    text = open(args.transcript).read()
    w = words(text)
    sents = sentences(text)
    counts = collections.Counter(x for x in w if x not in COMMON and len(x) > 2)
    sent_lens = [len(words(s)) for s in sents]
    out = {
        "word_count": len(w),
        "sentence_count": len(sents),
        "avg_words_per_sentence": round(sum(sent_lens) / max(1, len(sent_lens)), 2),
        "median_words_per_sentence": sorted(sent_lens)[len(sent_lens)//2] if sent_lens else 0,
        "flesch_kincaid_grade_est": round(fk_grade(text), 2),
        "top_content_words": counts.most_common(40),
    }
    if args.dur_s:
        out["words_per_second"] = round(len(w) / args.dur_s, 2)
    print(json.dumps(out, indent=2))
    print("\nProfile hint: use grade level as a plain-language target, not a judgment. Keep technical nouns; simplify glue.")
    if args.json_out:
        json.dump(out, open(args.json_out, "w"), indent=2)

if __name__ == "__main__":
    main()
