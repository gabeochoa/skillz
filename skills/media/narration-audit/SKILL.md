---
name: narration-audit
description: >
  Quality-assure TTS narration by transcribing the rendered audio back to text (Whisper STT) and
  diffing it against the intended script to catch mispronunciations and garbles the ear glosses
  over — then fix them by REWORDING (since this TTS is deterministic) and re-auditing candidate
  phrasings. The single highest-value QA step for any generated voiceover. Use after rendering
  narration, when a voiceover "sounds off", to verify pronunciation, or when the user says "check
  the audio", "audit the narration", "scrub for pronunciations", "did it say that right", "verify
  the voiceover", "the audio has a glitch", "STT the output", or "make sure the narration is
  clean". Pairs with tts-narration and feature-demo-studio. Runs on a CLI node with a Whisper venv.
node: cli
---

# Narration Audit (STT verify + reword-fix loop)

TTS lies to your ear. The only reliable QA is to **transcribe the output and diff it against the
script**. This catches the flaws that ruin an otherwise-polished demo.

## The loop

```diagram
render → STT transcribe → diff vs script → mismatch? → reword input → re-render beat → re-audit
                                              │
                                              └─ clean → ship
```

## Steps

### 1. Audit the render
```bash
python3 audit_narration.py narration.wav --script script.txt --model medium
```
Prints the heard transcript (with timestamps) and a word-level diff. `medium` is the
authoritative adjudicator.

### 2. Distinguish real flaws from STT artifacts
- Run both `--model small` and `--model medium`. When they **disagree**, medium wins (small has
  its own artifacts, e.g. "Say"→"Stay" on clean audio). When **both agree** a word is wrong,
  it's a REAL delivery flaw worth fixing.
- Sanity-check with `ffmpeg silencedetect` that the audio isn't actually truncated before
  assuming a delivery flaw.

### 3. Fix by rewording (NOT re-rolling)
This TTS is deterministic — identical input → identical audio. So generate several **reworded
variants** of the broken sentence, then auto-pick the cleanest:
```bash
python3 pick_best_take.py --glob '/tmp/fix/beat08_v*.wav' \
  --require handles sessions search results --model medium
```
Common, proven fixes:
| Symptom | Fix |
|---------|-----|
| "auto-routing" → "auto recommending"/"action" | drop the hyphen → "auto routing" |
| "Here's Ember's" → "embers" | "Here **is** Ember's" |
| "handles" → "handle" (dropped s) | "also handles" / "the sessions" |
| end word garbled ("you just ask" → "we're just out") | re-punctuate: "no folders, no filing, you just ask" |

### 4. Re-render only the fixed beats and splice
Re-render the reworded sentences, swap them into the beat set, reconcatenate, and **re-audit the
full assembled track** to confirm 100% clean before shipping.

## What counts as "clean"
Ignore benign tokenization diffs: possessive `'s` split off, contractions ("isn't"→"isn t").
Everything else that differs from the intended words must be fixed.

## Companion files
- `audit_narration.py` — STT transcribe + word-diff vs script
- `pick_best_take.py` — STT several reworded variants, pick the cleanest by required key words
