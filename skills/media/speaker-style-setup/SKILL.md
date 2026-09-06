---
name: speaker-style-setup
description: >
  Initialize a reusable speaker/author voice profile for narrated demos by gathering natural
  storytelling samples, preferred vocabulary, reading-level targets, cadence/pacing evidence, and
  voice-clone recording artifacts. Use before feature-demo-studio when the user wants demos to
  sound like them, mirror their natural language, match their cadence, infer vocabulary from small
  samples, analyze reading level, or says "setup my speaker style", "author voice setup", "voice
  profile setup", "learn how I talk", "match my pacing", "match my vocabulary", "reading level",
  "natural language sample", "storytelling sample", or "initialize demo narration voice".
node: cli
---

# Speaker Style Setup

Build the reusable profile that lets demo narration sound like the intended speaker, not just the
speaker's cloned timbre.

Voice cloning answers: **what does the speaker sound like?**
This setup answers: **what would the speaker actually say, how simply, and how fast?**

## Outputs

Create a speaker profile artifact with:

| Artifact | Purpose |
|----------|---------|
| service voice lookup | canonical `voice_name` + `client_id` in PlayAI VoiceCloningService |
| resolved `voice_id` | runtime output from the service lookup, not the primary stored handle |
| natural-language transcript samples | vocabulary, phrasing, rhetorical habits |
| read-aloud corpus | phonetics + clean voice clone input |
| cadence stats | words/sec, pause patterns, average beat length |
| reading-level target | how simple/complex the speaker naturally sounds |
| vocabulary profile | preferred words, banned tells, technical shorthand |
| communication ladder | how register changes by audience/stakes |
| sample demo rewrites | examples of generic copy rewritten into speaker voice |

Store the resulting profile in the user's private context (USER.md, MEMORY.md, or a private skill),
not in a public/shared skill.

## Setup flow

### 1. Identify target use
Ask:

```text
Who is the speaker, what surfaces will this voice narrate, and who is the usual audience?
Should this sound like a whiteboard walkthrough, launch post, exec review, customer demo, or something else?
```

### 2. Gather natural storytelling samples
Do not only ask the user to read fixed phonetic copy. Fixed scripts help cloning, but they do not
teach vocabulary or rhetorical defaults.

Ask the user to record or dictate 5-10 short, natural stories:

```text
Tell me, in your normal words:
1. A thing you shipped recently and why it mattered.
2. A bug or failure that annoyed you and what the real lesson was.
3. A feature you like, explained to a teammate at a whiteboard.
4. A feature you like, explained to a skeptical exec.
5. Something overcomplicated that you would simplify.
6. A funny or gruff aside you would actually say in a demo.
7. How you explain the same idea to a new hire.
8. How you explain the same idea to someone already deep in the project.
```

If the user has existing recordings, transcripts, posts, or talks, use those too. Prefer human-authored
or spontaneous material over polished AI-written text.

### 3. Gather read-aloud material and publish the service voice
Run **voice-clone-studio** for phonetic coverage and clean source audio, then **voice-service-registry**
to publish or normalize the reusable PlayAI VoiceCloningService entry. The read-aloud corpus is
still needed, but treat it as only one input:

- Read-aloud corpus -> timbre/articulation/phonetic coverage.
- VoiceCloningService entry -> canonical reusable TTS voice lookup for demos.
- Natural story corpus -> vocabulary, simplicity, pacing, rhetoric.

### 4. Transcribe and segment
Use Whisper or available STT to transcribe the natural stories and read-aloud samples. Preserve word
timestamps when possible; they are useful for pacing.

Segment into:

- natural story beats (speaker chose the words)
- read-aloud beats (speaker did not choose the words)
- audience variants (same idea for different audiences)
- jokes/asides
- technical explanations

### 5. Analyze vocabulary and simplicity
Compute a rough reading-level profile from natural story transcripts, not read-aloud passages.
Use grade-level metrics as a **style proxy**, not a school-grade judgment.

Recommended checks:

| Metric | Why |
|--------|-----|
| Flesch-Kincaid grade | rough sentence/word complexity |
| average words per sentence | spoken breath length |
| syllables per word | simplicity / plain-language bias |
| jargon density | how much technical shorthand the speaker uses |
| filler/formality tells | words the speaker rarely uses |
| preferred verbs/nouns | reusable lexicon for unseen scripts |

Interpretation:

- A lower grade level is often a feature for demos: clear, fast, and hard to misunderstand.
- Do not force childish language; keep the speaker's technical nouns and simplify the glue around them.
- For unseen topics, infer style from patterns: sentence length, verb choice, directness, use of analogies,
  and how the speaker introduces jargon.

### 6. Analyze cadence and pacing
Use natural story recordings where possible. If you only have text, infer a weaker pacing profile
from sentence length and punctuation, then update it once audio exists.

Capture:

| Signal | Profile field |
|--------|---------------|
| words per second | target speaking rate |
| pause after sentence | default inter-beat gap |
| long-pause patterns | dramatic/comedic beat timing |
| beat word count | comfortable spoken beat size |
| clause density | when to split sentences |
| correction style | whether speaker restarts, jokes, or bulldozes forward |

### 7. Build the communication ladder
For each common audience, define the register:

```text
working session: <how casual?>
team demo: <default register?>
exec review: <what gets cleaner or more explicit?>
external/customer: <ask first or default?>
```

Also capture:

- humor level
- gruffness/directness
- how much context to assume
- phrases to use
- phrases to avoid

### 8. Produce the profile
Use this shape:

```json
{
  "speaker": "username",
  "voice_lookup": {"voice_name": "...", "client_id": "feature_demo_studio"},
  "voice_resolution": "Resolve voice_id at render time via VoiceCloningService.get_voices exact lookup.",
  "default_register": "casual-professional",
  "communication_ladder": {
    "working_session": "...",
    "team_demo": "...",
    "exec_review": "...",
    "external": "ask first"
  },
  "reading_level": {
    "target_grade": 6.5,
    "notes": "Simple glue words, technical nouns allowed."
  },
  "cadence": {
    "target_wps": [1.8, 2.7],
    "beat_words": [6, 18],
    "default_gap_s": 0.35,
    "pause_notes": "..."
  },
  "vocabulary": {
    "preferred": ["use", "show", "ship"],
    "avoid": ["utilize", "seamless", "robust"],
    "technical_shorthand": ["..."],
    "rhetorical_patterns": ["..."]
  },
  "examples": [
    {"generic": "...", "speaker_voice": "...", "why": "..."}
  ]
}
```

## Lightweight inference from a small sample

If you only have a small corpus, still extract useful constraints:

- reading level / simplicity target
- average sentence length
- preferred verb style
- direct vs hedged claims
- joke/asides pattern
- taboo/formal words to avoid

Be honest about confidence. Mark low-confidence profile fields as guesses and ask the user to
correct them after the first rendered demo.

## Handoff to demo pipeline

After setup:

1. **feature-demo-studio** uses the profile in its author/speaker placeholder step.
2. **narration-vocab-audit** checks the script against vocabulary + communication ladder.
3. **narration-pacing-audit** checks script and beat JSON against cadence.
4. **voice-service-registry** resolves `{voice_name, client_id}` to exactly one service row.
5. **tts-narration** renders using the resolved service `voice_id`.
6. First demo cut becomes another sample; update the profile from user feedback.

## Companion files

- `analyze_speaker_style.py` — text/transcript analyzer for reading level, common words, sentence
  lengths, and rough cadence if timestamps are present.
- `story_prompts.md` — prompts to elicit natural storytelling samples.
