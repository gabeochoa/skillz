# Web UI checklist

Read with the shared spine in `SKILL.md`, not instead of it. This file covers what web UI has
that game UI doesn't: an accessibility floor with legal teeth, a viewport the user resizes, and
native controls that already work if you leave them alone.

## A. Contrast — WCAG AA is the floor, not the goal

| Target | AA | AAA |
|---|---|---|
| Body text | 4.5:1 | 7:1 |
| Large text (18pt / 14pt bold) | 3:1 | 4.5:1 |
| UI components, focus rings, icons carrying meaning | 3:1 | — |

Placeholder text and disabled controls fail this constantly — check them specifically. Failing AA
on body text is HIGH, not MEDIUM.

Colour is never the only cue. A red border alone doesn't say "error" to everyone; pair it with an
icon, a mark, or text.

## B. Typography

- 16px minimum body text. Smaller is a finding, not a style.
- Line height 130–150%, set explicitly rather than inherited.
- Measure 45–75 characters. Over 80 and the eye loses its place returning to the next line.
- Three text styles across a page is plenty. Every extra one needs a job.

## C. Keyboard and focus

- Every interactive element is reachable by Tab and shows a visible focus ring at 3:1.
- Tab order follows visual order.
- No focus traps. Escape closes anything that opened.
- Focus returns to the trigger when a modal closes.
- Nothing hover-only — if it only appears on hover, it doesn't exist for keyboard or touch.

## D. Responsive

- Reflow at 320px wide without horizontal scroll.
- Touch targets 44×44 minimum.
- Grid: mobile 2 columns with 16px margins; desktop 12 columns with 32–60px margins.
- Check the breakpoint boundaries, not just the comfortable middle. Layouts break at 768px, not
  at 1440px.

## E. Forms

- Labels above or beside fields, never a placeholder standing in for a label — it vanishes on
  focus and fails every screen reader.
- Validate inline, on blur, next to the field that's wrong.
- Errors say what to do, not that something is invalid. "Password needs 8+ characters", not
  "Invalid input".
- Required vs optional marked consistently, one way, whichever way.
- Group related fields; the visual grouping should match the semantic grouping.

## F. Navigation and IA

- Roughly three levels of hierarchy. Deeper means the structure is wrong, not that you need
  better breadcrumbs.
- Current location is always visible.
- Groups of 3–5 items scan best; 9 flat items don't.

## G. Feedback and heuristics

Nielsen's list, the ones that show up in screenshots:

- **System status visible** — loading, saved, syncing. Skeletons over spinners; optimistic
  updates where the operation almost always succeeds.
- **Match the user's language** — "manage notifications", not "webhook configuration".
- **User control** — undo and escape hatches on anything destructive.
- **Recognition over recall** — don't make the user remember what was on the previous screen.
- **Error prevention** over error messages — a constrained input beats a validation rule.
- **Empty states invite action.** An empty list showing nothing is a bug; showing what to do
  next is the design.

## H. Microcopy

- CTA names its outcome: "Save changes", not "Submit". "Delete 3 files", not "OK".
- Sentence case. Conversational. Active voice.
- Consistent vocabulary across a flow — the thing called a "project" on one screen is not a
  "workspace" on the next.
- Errors don't apologize and don't blame.

## I. House HIGs

`~/p/wm_afterhours/prompts/` holds vendored guidelines worth consulting when a specific question
comes up — don't read them wholesale, grep for the topic:

| File | Use for |
|---|---|
| `apple_hig.md` | platform conventions, controls, touch |
| `google_hig.md` | Material patterns, motion, elevation |
| `atlassian_design_foundations.md` | tokens, spacing, colour systems |
| `uswds_design_principles.md` | plain language, accessibility, forms |
| `microsoft_win95_hig.md`, `sun_java_look_and_feel_hig.md` | classic desktop idioms; useful when
  a design is deliberately retro, which several of this user's projects are |
