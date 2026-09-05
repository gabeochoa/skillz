---
name: in-my-voice
description: Write an announcement post or a change summary that sounds like the author instead of like a model. Compiles a reusable voice profile from their own past writing, then drafts to it. Use for /in-my-voice, "write a post", "draft an announcement", "write in my voice", or "suggest a summary for this change".
---

# in-my-voice

Draft in the author's voice, compiled from what they actually wrote, not from a persona.

This skill is the empirical layer. `gabe-writing` is the house standard that says what never
to write; this one says what this particular person sounds like when they write well. Where
the two disagree on anything going out under a person's own name, the profile wins.

## Invocation

```text
/in-my-voice <what the post or summary is about>
```

Examples:

```text
/in-my-voice announce that the import pipeline shipped
/in-my-voice heads-up that the onboarding guide moved
/in-my-voice feedback on a tool that keeps timing out
/in-my-voice suggest a summary for the change I have open
```

## Routing

Decide which of the two artifacts is being asked for.

- Post: "post", "announce", "launch", "FYI", "update", "feedback". Go to Post workflow.
- Change summary: "summary", "description", "summarize this change", a change or PR
  reference. Go to Change-summary workflow.

Ask only when the words fit both.

## Post workflow

### 1. Load or build the profile

Read `~/.claude/voice-profile.md`. It exists, use it and go to step 2. It does not, build it:

1. Ask how to source samples: search the author's own published posts on whatever archive
   this environment can reach, or have them paste 3 to 5 links.
2. Gather 5 posts spanning the types in `references/post-types.md`, not five of one kind.
3. Extract the fields in `references/profile-fields.md`.
4. Write the whole profile to `~/.claude/voice-profile.md` so the next run skips this.

Three samples of one type produces a profile that is wrong about the other three types.

### 2. Identify the post type

Launch, FYI, feedback, or update. `references/post-types.md` carries the signals and the
section order for each. A launch structure applied to a feedback post reads as a press
release about someone else's bug.

### 3. Gather the content

Pull from the links, notes, or conversation given. Ask for the specifics that a post of this
type needs and cannot be inferred: the measure, the ticket, the people who did the work, the
audience. Never invent a number or a name to fill a section.

### 4. Draft to the profile

Follow the profile on every axis it records: how they order sections, how they write
headers, how they format lists, which words they reach for, how they sign off. Match
confidence level exactly: an assertive writer gets "this fixes X", not
"this should help address X".

### 5. Hand it back

Present the finished post as markdown and iterate on their edits. Once they call it final,
put it wherever they keep drafts (a snippet or paste surface, a file, or the reply itself) and
give them the link. Do not publish it. Anything going out under a person's name is their send.

## Change-summary workflow

### 1. Load or build the summary profile

Read `~/.claude/change-summary-profile.md`. Absent, build it from at least 10 of the author's
own merged or approved changes, using the fields in `references/profile-fields.md`, and save
it there.

Ten is the floor because summary style varies far more per change than post style does per
post, and a small sample reads the noise as the pattern.

### 2. Read the change

Take the referenced change, or the working tree if they meant the one in front of them. Read
the actual diff. A summary written from the branch name describes a change nobody made.

### 3. Draft to the profile

Match length first, and length is the rule people break most: a one-line author gets one line.
Then match structure, whether it opens with the what or the why, verb tense and mood
("Add X" against "Added X" against "Adds X"), and whether a test plan is expected.

### 4. Hand it back

Present the summary and the test plan, iterate, then hand the final text back for the author
to paste into the change description themselves. Do not post it as a review comment unless
they asked for exactly that: review comments are public, attributed, and permanent.

## Common mistakes

| Mistake | Fix |
|---|---|
| Generic model voice | Re-read the profile. Use their phrases, not the neutral synonym. |
| Superlatives they never use | Check the vocabulary fingerprint. They do not say "amazing", so neither do you. |
| Wrong structure for the type | A launch post is not a feedback post. Check `references/post-types.md`. |
| Vague credit | Name what each person did. A bare thanks line credits nobody. |
| Dropping their opener | They always lead with a summary line, so you always do. |
| Hedging an assertive writer | Match their confidence, do not soften it. |
| Inventing sections | Write only the sections they actually use. |
| A long summary from a terse author | Match their length. |
| Wrong verb tense in a summary | Pick their tense and hold it across every line. |

## References

- `references/post-types.md` -- the four post types, their signals, and their section order.
- `references/profile-fields.md` -- what to extract for each profile, and where each is saved.
