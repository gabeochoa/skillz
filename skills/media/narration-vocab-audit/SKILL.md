---
name: narration-vocab-audit
description: >
  Audit and rewrite narrated demo scripts so the words match the intended author/speaker's natural
  language, vocabulary, register, communication ladder, rhetorical habits, and humor level before
  TTS. Use when a demo should "sound like me", match an author's vocabulary, avoid generic product
  marketing voice, adapt a script to a speaker, or when the user says "vocab check", "vocabulary
  audit", "author voice", "speaker voice", "natural language", "communication ladder", "register",
  "tone check", "does this sound like me", or "make the narration sound like <person>". Pairs with
  feature-demo-studio and narration-pacing-audit.
node: cli
---

# Narration Vocab Audit

Make the script sound like the intended speaker before rendering audio. A voice clone gives you the
speaker's sound; this skill protects the speaker's **word choice**.

## What this skill checks

| Check | Question |
|-------|----------|
| Author profile loaded? | Did we identify whose language this should mirror? |
| Register / communication ladder | Is the wording calibrated to the audience and stakes? |
| Lexicon | Are these words the speaker would naturally use? |
| Rhetorical habits | Does the sentence structure match the speaker's usual moves? |
| Humor / warmth | Is the joke density or informality right for the context? |
| Product truth | Did style edits preserve the claim and technical meaning? |

## Required inputs

- Script, one narration beat per line.
- Intended speaker/author.
- Audience and surface (internal demo, launch post, exec review, customer-facing, etc.).
- Any must-keep technical terms.
- An author/speaker voice profile if one exists.

## Step 1: trigger or build the author profile

Use this exact internal intent before auditing:

> Find the author/speaker voice profile for this narration: vocabulary, communication
> ladder/register, rhetorical habits, humor level, and cadence defaults.

If a private/person-specific style skill exists, it can enrich the profile, but it is not required.
If no profile exists, use **speaker-style-setup** or ask for a small one instead of guessing:

```text
Who is the speaker, who is the audience, and what should the default register be?
Give me 3-5 phrases they say and 3-5 phrases they would never say.
```

Do **not** add one person's private preferences to this public skill. The public skill owns the
method; private/user skills own the actual voice profile.

## Step 2: line-by-line audit

For each beat, classify it:

| Verdict | Meaning | Action |
|---------|---------|--------|
| KEEP | Sounds like the speaker and fits the audience | leave it |
| DOWNSHIFT | Too formal, polished, or generic | use simpler words / more direct syntax |
| UPSHIFT | Too casual for the audience | raise register without losing the speaker's voice |
| REPHRASE | Meaning is right, voice is wrong | rewrite in speaker's vocabulary |
| ASK | Missing profile or sensitive claim | ask before rendering |

Output format:

```text
Beat 03 — REPHRASE
Why: "utilize" and "comprehensive" sound generic/formal for this speaker.
Before: The dashboard utilizes comprehensive session metadata.
After: The dashboard uses the session data we already have.
```

## Common generic-demo tells

| Tell | Usually better |
|------|----------------|
| "leverage", "utilize", "facilitate" | use, help, make easier |
| "seamlessly", "powerful", "robust" | show the specific thing it does |
| "This innovative solution" | name the feature or cut the phrase |
| Long setup before the point | start with the point |
| Three polished clauses in a row | split into smaller spoken beats |
| Marketing superlatives | concrete proof or a joke, depending on speaker profile |

## Clean criteria

A script passes when:

- Every beat is something the intended speaker plausibly would say out loud.
- Register matches the communication ladder for the audience.
- The script avoids generic AI/product-marketing filler.
- Technical meaning is preserved.
- Any uncertain line is flagged for the user before TTS.

## Companion files

- `vocab_audit.py` — lightweight CLI helper for obvious generic/formal terms and optional
  profile JSON checks. It is a first pass only; the author profile review is the real audit.
