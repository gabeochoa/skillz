---
name: feature-demo-studio
description: >
  Orchestrator for producing high-quality product/feature demo videos with narration in the
  intended speaker's own voice. Delegates to focused component skills — speaker-style-setup
  (initialize the reusable speaker profile), narration-vocab-audit (match the author's natural
  language, register, and vocabulary), narration-pacing-audit (match cadence and beat timing),
  narration-audit (speech-to-text verify + reword-fix pronunciations), ui-capture-cdp (real,
  pixel-perfect UI frames including frozen/animated transient states via launched-Chrome CDP),
  and demo-video-assembly (frame-accurate stitch + cursor annotation + mux).
  Use whenever the user wants to make/update a demo video for a feature, produce
  marketing/launch footage, show a workflow end to end, or says "make a demo video", "demo this
  feature", "record a walkthrough", "product demo", "feature showcase", "narrated demo",
  "screen recording with voiceover", "update the demo", "re-render the demo", "demo in my voice",
  "sound like me", "learn how I talk", "match my vocabulary", "match my cadence", "reading
  level", or "high quality demo".
  Coordinates a capture machine (browser/audio/ffmpeg) and whatever voice-cloning and
  text-to-speech service you use.
---

# Feature Demo Studio (orchestrator)

Produce a demo where **the visuals are real UI, the narration sounds like the intended speaker,
and every cut lands on the spoken word.** This skill sequences the component skills; read each one
when you reach its phase.

## Component skills (delegate to these)

| Phase | Skill | Produces |
|-------|-------|----------|
| Speaker setup (once per user) | **speaker-style-setup** | reusable private profile: vocabulary, reading level, cadence, communication ladder, samples |
| Voice clone (once per user) | your voice-cloning service | a clean cloned voice created from curated audio |
| Voice registry (once per user, verify every render) | your voice service's catalogue | a stable voice handle you can resolve to a voice id |
| Vocabulary/style QA | **narration-vocab-audit** | script rewritten to match the author's natural language |
| Pacing/cadence QA | **narration-pacing-audit** | pre-render beat/cadence fixes + post-render timing checks |
| Script to audio | your text-to-speech service | `narration.wav` + `narration_beats.json` |
| Audio correctness QA | **narration-audit** | verified-clean pronunciation/transcript (reworded fixes) |
| Visuals | **ui-capture-cdp** | real UI frames, including frozen/animated transients |
| Assembly | **demo-video-assembly** | final beat-synced `demo.mp4` |
| Move files across machines | **file-transfer** | render on the laptop, process on a remote box (and back) |

## End-to-end flow

### 0. Speaker setup (skip if the user already has a reusable profile)
If this is the first narrated demo for a speaker, run **speaker-style-setup**. It gathers natural
storytelling samples, reading-level/simplicity targets, vocabulary, cadence, communication ladder,
and voice-clone artifacts into a private speaker profile.

This setup is separate from voice cloning: the same audio sample is not enough to learn what words
the speaker would naturally choose for topics that were never in the training corpus.

### 0b. Corpus and registry readiness gates
Before cloning from existing audio:

- If source audio might include multiple speakers, run speaker identification and build a
  high-confidence speaker-only corpus.
- Do not pad with lossy or wrong-speaker material just to increase duration.
- Preserve natural pauses; avoid aggressive silence removal.
- Audition raw include/exclude samples with the user when the corpus was harvested from existing
  media.

Before rendering demos, check the voice catalogue: the lookup must be unique, the sample audio
must exist, and a short audition render should sound right.

### 1. Voice clone (skip if the user already has a clone)
If the user wants narration "in my voice" and has no clone yet: record, analyse flubs, curate,
clean, clone, then A/B the result. The clone is not ready for demos until it is published to your
voice service, lookup by a stable handle returns exactly one entry, its sample audio is present,
and a short audition render sounds right. Store that handle in the speaker profile. Do not store a
demo-only hardcoded voice id as the primary reference.

Assume future demos reuse the catalogue entry. If they have no voice and don't want to record, fall
back to an existing stock voice only after resolving it through the same flow.

Important: a voice clone captures **timbre, pronunciation, articulation, and some prosody** from
the speech sample. It does **not** reliably capture vocabulary, communication ladder, joke density,
reading-level preference, or what the speaker would naturally choose to say. Treat those as
separate setup/profile checks.

### 2. Identify the author/speaker voice profile
Before drafting copy, identify whose voice the narration should use. This is intentionally a
placeholder, not a hardcoded person:

> Find the author/speaker voice profile for this narration: vocabulary, communication
> ladder/register, rhetorical habits, cadence, and pacing defaults.

That phrasing may activate an installed private or person-specific style skill if one exists. If
not, use the **speaker-style-setup** profile or ask the user for a lightweight profile. Do not put
one person's private voice rules in this shared skill. Either way, the audio voice still comes from
the voice service, not from the style/profile layer.

### 3. Write the script (beats)
Draft a tight narration script — one natural sentence per beat, active voice, no hyphens in
tricky compounds. Cover the full story: how the feature is ENABLED (not just used), the trigger,
the payoff, and where it applies.

Then run **narration-vocab-audit** before rendering. The test is: would the intended speaker
actually say this sentence, in this register, to this audience? Rewrite anything that sounds like
generic product marketing, generic AI copy, or someone else's voice. Confirm wording with the user
before rendering when the speaker voice matters.

### 4. Check pacing before render
Run **narration-pacing-audit** on the script before synthesis. Split sentences that are too long
for one breath, merge tiny fragments that sound choppy, and set inter-beat silence to match the
target cadence. Pacing is part of the script, not just the audio file.

### 5. Capture the visuals (parallelizable with steps 3-6)
Use **ui-capture-cdp**: launch an isolated Chrome, have the user log in once, then drive the flow
and capture REAL frames — including freezing sub-second transients (`Fetch.requestPaused`) and
burst-capturing animations (spinners). Actually perform side-effecting actions (e.g. sending a
message to capture the result) only with user confirmation.

### 6. Render + audit narration
Resolve the voice handle in your voice catalogue, then render the voiceover and beat timings from
the returned voice id. The beat JSON should record how the voice was resolved, so a bad render is
traceable. Then run two audits:

1. **narration-audit** — transcribe the output, diff against the script, and reword+re-render any
   garbled beats until the full track is clean.
2. **narration-pacing-audit** — inspect `narration_beats.json` for words/second, long beats, and
   awkward pauses. Fix cadence problems by splitting/merging/rewording beats or changing the gap,
   then re-render.

(Run capture and audio as two parallel tracks — they're independent until assembly.)

### 7. Assemble
Use **demo-video-assembly**: normalize frames, composite cursor-click annotations where you want
to show interactions, map frames to beat timings, stitch, and mux. Spot-check with a contact
sheet before shipping.

### 8. Review, publish, clean up
Show the user the video for feedback at the video level (not intermediate decisions unless they
ask). On approval, publish where it belongs — the team's video host, the docs page, the release
post. Keep the clip small (about 1 MB, under a minute) so the upload is fast, and post a draft
first if the user wants to review before it goes live.

Then revert any uncommitted scratch edits on the machines you touched, and tear down the capture
Chrome and its temp profile.

## Conversational / multi-host demo cuts
When creating a demo with two speakers:

- Avoid alternating every sentence. Let one host drive and the other add one or two meaningful
  interjections.
- Use longer clean pauses between real speaker changes, but remove noisy tails that sound like
  laughs or missed cues.
- Make humor earn the reaction. Do not keep laugh-like artifacts after non-jokes.
- Audit each generated beat and the final mixed narration. If the final mix has new artifacts,
  replace the offending beat rather than only trimming the gap.

## Principles (why the output is high quality)

- **Real UI, never synthetic** — only true browser chrome (address bar) may be composited.
- **The voice service is the audio source of truth** — demos resolve voices by a stable handle,
  never through local notes or person-specific skills.
- **A voice clone is not an author voice** — timbre comes from the service voice; vocabulary,
  reading level, communication ladder, and cadence come from speaker-style-setup plus the
  vocab/pacing audits.
- **Verify all audio by transcript** — the ear misses what the transcript catches.
- **Deterministic synthesis means reword, don't re-roll** — fix pronunciations by changing the
  input text.
- **Frame-accurate sync** — drive frame durations from narration beat timings.
- **Show enablement, not just usage** — start the story earlier (how you turn the feature on).
- **Animate transients** — freeze and burst-capture so loaders aren't frozen stills.
- **Version everything** — voice clones, corpora, scripts, and video cuts, so you can iterate and
  roll back. Reuse the same voice and pipeline for each new feature.

## Machine topology
- **Capture machine (the user's laptop)**: Chrome capture, ffmpeg, transcription, image
  compositing.
- **Wherever your voice service runs**: cloning and synthesis.
- Move files between them with the **file-transfer** skill (many small files, not one big tarball —
  upload endpoints tend to reject large payloads).
