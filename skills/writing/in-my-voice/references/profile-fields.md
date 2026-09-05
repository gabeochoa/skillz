# Profile fields

Two profiles, two files, two sample requirements. They are not interchangeable: the way
someone writes a team post says almost nothing about how they write a change summary.

| Profile | File | Minimum sample |
|---|---|---|
| Post voice | `~/.claude/voice-profile.md` | 5 posts, spanning types |
| Change-summary voice | `~/.claude/change-summary-profile.md` | 10 merged or approved changes |

Both files are the author's own material, so they stay on their machine. Never copy either
into a shared repository.

## Post voice

Structure

1. How they open. Summary line, a header, a numbered list, or straight into prose.
2. Which sections they use, and in what order.
3. How they close. A credit line, a notify list, a sign-off, or nothing.
4. How they format. Bold, code spans, tables, links, and how heavily.

Tone

5. Confidence. Assertive against hedged, and whether that changes by type.
6. Formality, and whether it drops for short posts.
7. Superlatives: which ones they use, and which they never do.
8. Technical depth. Whether they write for their own team or for a stranger.
9. Humor. Present, dry, or absent.

Vocabulary

10. Recurring openers and phrases, quoted verbatim.
11. Verbs they favor: shipped, landed, fixed, addressed, cut.
12. Words they avoid, which is the half a model gets wrong.
13. How they name teams, tools, and projects. Full name, abbreviation, or nickname.

Per type

14. What differs per post type, recorded against the table in `post-types.md`. A profile with
    one section order in it is a profile of one post.

## Change-summary voice

Structure

1. Typical length. One line, a short paragraph, or multiple sections. Record the range.
2. Headers or no headers, and which ones.
3. Bullets against prose.
4. Whether a ticket or issue link is always present.

Content

5. Whether they lead with the what or the why.
6. How much background they give someone who has not seen the ticket.
7. Whether they reference other changes, incidents, or tickets.
8. Whether testing notes belong in the description itself or stay in the test plan.

Test plan

9. Detail level: one line, or step by step.
10. Recurring phrases, quoted verbatim.
11. Whether they paste commands, output, or screenshots.

Tone

12. Terse against descriptive.
13. Depth: symbol-level detail against a one-sentence description.
14. Verb tense and mood, which must be consistent across every line of the draft.

## Keeping a profile honest

Re-derive a profile when a draft written from it gets edited heavily twice in a row. Two heavy
edits means the profile describes an older register, and every draft after that inherits the
same wrongness.

Record the sample the profile was built from, with a date. A profile with no provenance cannot
be checked, and an unverifiable profile is indistinguishable from a persona, which is the
thing this skill exists to avoid.
