---
name: narration-pacing-audit
description: >
  Audit narrated demo scripts and rendered TTS beat metadata for pacing, cadence, sentence length,
  words per second, pauses, breathability, and rhythm. Use before TTS to split/merge beats and
  after TTS to inspect narration_beats.json. Trigger phrases include "pacing check", "cadence",
  "speaking cadence", "too fast", "too slow", "beat timing", "words per second", "pause length",
  "breath", "rhythm", "make it sound natural", and "match my cadence". Pairs with
  feature-demo-studio, narration-vocab-audit, tts-narration, and demo-video-assembly.
node: cli
---

# Narration Pacing Audit

Cadence is not just an audio property. The voice sample teaches the model some prosody, but the
script controls most of the pacing: sentence length, punctuation, beat boundaries, and pauses.

Run this twice:

1. **Before TTS** — fix the script so each beat is speakable.
2. **After TTS** — inspect `narration_beats.json` and fix timing problems before assembly.

## Defaults (override from the author voice profile)

| Metric | Default target | Flag when |
|--------|----------------|-----------|
| Beat length | 6-18 words | >22 words or <3 words repeatedly |
| Beat duration | 1.5-6.5s | >7.5s unless intentionally dramatic |
| Words per second | 1.7-3.0 wps | <1.4 slow, >3.3 rushed |
| Inter-beat pause | 250-600ms | <180ms cramped, >900ms draggy |
| Structure | one idea per beat | multiple clauses or topic jumps |

The target speaker's private style profile wins over these defaults. Some speakers are clipped and
fast; others need longer pauses. Do not normalize everyone to the same announcer voice.

## Pre-render script audit

For each beat:

- Read it out loud once. If you need a second breath, split it.
- Keep one idea per beat.
- Use punctuation to tell TTS where to breathe.
- Split long technical sentences before acronyms or proof points.
- Merge repeated tiny fragments unless the speaker profile calls for punchy fragments.
- Preserve intentional comedic or dramatic pauses, but mark them as intentional.

Output format:

```text
Beat 06 — SPLIT
Why: 31 words, two ideas, likely rushed.
Before: ...
After:
  06a: ...
  06b: ...
```

## Post-render timing audit

Run the helper against `narration_beats.json`:

```bash
python3 check_pacing.py narration_beats.json
```

Then fix problems by changing input text, beat boundaries, punctuation, or `GAP_S` in the TTS
renderer. Do not try to repair bad cadence in video assembly unless the audio itself is already
right.

## Fix patterns

| Symptom | Fix |
|---------|-----|
| Beat is too fast | split it, add punctuation, or simplify the words |
| Beat is too slow | remove filler or merge with neighboring beat |
| Beat is long but wps is normal | split for visual sync and breathability |
| Pauses feel robotic | vary punctuation/beat boundaries; adjust `GAP_S` only after script fixes |
| Visuals lag narration | split the spoken beat to match visual state changes |
| Joke lands flat | add a tiny pause before/after the punch line, or shorten the setup |

## Clean criteria

A narration passes when:

- Every beat can be spoken in one comfortable breath.
- Timing matches the target speaker's cadence, not generic announcer pacing.
- Pauses feel intentional.
- Visual transitions can map cleanly to beat boundaries.
- Any timing exceptions are intentional and documented.

## Companion files

- `check_pacing.py` — reads `narration_beats.json` and flags long beats, rushed/slow delivery,
  and awkward inter-beat pauses.
