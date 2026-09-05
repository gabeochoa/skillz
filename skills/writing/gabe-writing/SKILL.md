---
name: gabe-writing
description: House writing standard for anything a person reads, including short chat replies and status lines. Use before drafting prose, a report, a status update, a change summary, a doc, or a post. Cuts AI tells, puts the conclusion first, and bans the constructions that make writing sound generated.
---

# gabe-writing

Conclusion in the first sentence. Everything after it earns its place or gets cut.

This is a personal house standard, not a general style guide. It governs every register:
docs, posts, reports, change summaries, status rows, and one-line chat replies. Short
surfaces get a smaller word budget, never a rules exemption.

## The checklist

Run this before sending anything.

Shape
1. Conclusion first. No preamble ("as requested", "I looked into", "here is a summary").
2. Delete test on every sentence. If cutting it loses no fact, leave it cut. Closing
   sentences almost always fail.
3. Numbers: a table at three or more, one per sentence below that. Re-derive every number
   with a script, never copy one by hand.
4. State the corrected fact. Do not narrate having been wrong.
5. Hedging is undone work. Say it is unresolved and go resolve it, or validate both paths.

Banned constructions
6. Em dashes. Use commas, or split the sentence. Parentheses are fine.
7. Negative parallelism: "not X, it's Y", "the question isn't X, it's Y", "Not X. Just Y."
   State the true thing and delete the negated half.
8. Self-posed question then answer: "The result? Devastating."
9. False suspense: "here's the thing", "here's the kicker", "here's where it gets interesting".
10. Pedagogy: "let's break this down", "let's unpack", "think of it as", "imagine a world where".
11. Filler transitions: "it's worth noting", "importantly", "interestingly", "notably".
12. False ranges ("from X to Y" with no real middle), tricolon runs, anaphora,
    listicle-as-prose ("The first... The second...").
13. Fragment paragraphs used for manufactured emphasis.
14. Signposted conclusions ("in conclusion", "to sum up"), fractal summaries, one point
    restated several ways.
15. "Despite these challenges", and the rest of the acknowledge-then-dismiss family.

Words
16. AI vocabulary: delve, utilize, leverage as a verb, robust, streamline, harness, tapestry,
    landscape, paradigm, synergy, ecosystem.
17. Magic adverbs: quietly, deeply, fundamentally, remarkably, arguably.
18. Fancy copula: serves as, stands as, represents, marks. Write "is".
19. Coined jargon and invented concept labels. Use words already in the code, the change, the
    ticket, or the domain. If a term genuinely recurs, introduce it once as "call this X".
20. Benefit claims: trivial, simply, just a, one-line, cheap, "no migration needed". Name the
    variable and stop.
21. Invented time estimates. Size work by files, callsites, reversibility, blast radius, and
    what decision is blocked. A resourcing ask names the resource, not the duration.
22. Puffery and stakes inflation. "The truth is simple", "history is clear". Prove it instead.
23. Vague attribution. Name the person or drop the claim. Never inflate one source into "several".
24. Trailing "-ing" pseudo-analysis: "highlighting its importance", "reflecting broader trends".

Format
25. Plain list lead-ins, not bold-first bullets. Bold nothing, or bold one thing.
26. Straight quotes. Write `->`, not the arrow glyph.
27. Emoji: none in prose. A status row may use one leading emoji as a scannable marker.
28. No single metaphor beaten flat, no stacked historical analogies.

## The four worth remembering without opening the file

1. No coined jargon. The failure is inventing a compact term mid-explanation and then using it
   as if it were shared vocabulary.
2. No benefit claims. A summary is not an ad.
3. The delete test. Closing sentences almost always fail it.
4. No invented time estimates for engineering work.

## Precedence

1. An explicit format the reader asked for in the moment beats everything below.
2. The voice profile plus the AI-tells list. Those two are the gate.
3. The supporting references: local exceptions, plain-language rules, technical-writing mode.

Anything going out under a person's own name follows their voice profile even where a style
rule disagrees.

## Simplified technical English does not apply to everything

Apply controlled-language rules (short sentences, one instruction per sentence, approved
vocabulary) to specs, runbooks, change summaries, test plans, and notes a stranger reads
without context.

Do not apply them to writing in a specific person's voice. A personal register with lowercase
starts, dropped apostrophes, and parenthetical asides breaks controlled language by
construction, and that is correct.

## References

- `references/voice-profile.md` -- how to compile and apply a personal voice profile.
- `references/ai-tells.md` -- the tell taxonomy, worst first, with the fix for each.
- `references/precedence.md` -- which rule wins when two disagree, and the standing exceptions.
- `references/durable-lessons.md` -- rulings that settled a real disagreement, with the reason.

## Enforcement

A checklist that lives only in prose gets followed one session and forgotten the next. Encode
the mechanical rules as a script that scans a draft and reports violations by line, and run it
as a pre-send gate. Regex catches the banned constructions, the AI vocabulary, and the format
rules. The judgment rules (delete test, conclusion first) need a model pass, so run them at
suggestion tier where they never block.
