# Game / immediate-mode UI checklist

Read with the shared spine in `SKILL.md`, not instead of it. This file covers what game UI has
that web UI doesn't: a moving background, a viewing distance, a resolution that isn't yours, and
a player who is busy.

## A. Screen safety (check first — these are CRITICALs)

- **Safe area.** Keep interactive and readable content inside a 5% inset on every edge for TV
  overscan. Purely decorative fills may bleed.
- **Clipping.** Anything cut by the frame edge. Look hardest at the corners, where HUD elements
  cluster.
- **Off-screen.** Elements laid out past the viewport entirely. `analyze.py` reports these as
  `laid-out-offscreen` with exact deltas — use its numbers.
- **Aspect ratios.** A layout tuned at 16:9 has to survive 16:10, 21:9, and 4:3. Edge-anchored
  elements are the ones that break. Ask what happens to this shot at another ratio.
- **Anchoring vs scaling.** Does the element hold its corner, or does it scale with the window?
  Text that scales with the window becomes unreadable at small sizes; text anchored without
  scaling becomes a speck at 4K.

## B. Container integrity

- Children rendered outside their parent's box (`child-escapes-parent`).
- Overflow that breaks structure rather than scrolling.
- Sizing specs that promise space and resolve to zero (`sizing-collapsed-to-zero`).
- Flow siblings overlapping (`flow-siblings-overlap`) — nearly always a solver bug, not a design
  choice.
- Containers that don't visually communicate their own bounds, so grouping reads wrong.

## C. Readability under load

Game UI is read at a distance, in peripheral vision, while something else demands attention.

- **Distance.** Would this be legible from a couch, at 1/3 the apparent size? Body text that
  works in a screenshot at 100% zoom often fails on a TV.
- **Peripheral.** Health, ammo, timers, and alerts get read without a direct look. They need
  silhouette and position constancy — an element that moves or resizes as its value changes
  cannot be read peripherally.
- **Over motion.** The background moves. Text over a rendered scene needs its own backing:
  a plate, a scrim, an outline, or a shadow. Contrast against one frame is not contrast.
- **Through VFX.** Explosions, bloom, and camera shake wash out low-contrast overlays. Critical
  values must survive the worst frame, not the calm one.
- **Cognitive load.** During active play, how many things ask to be read at once? Menus can be
  dense; a combat HUD cannot.

## D. Menus and controls

From the house rules in `~/p/wm_afterhours/prompts/design_rules.md`:

- **Text-first.** Actions are labelled with words. Icons assist, they don't replace.
- **Icons are opt-in.** Only when the icon carries meaning the text can't. If an icon can't be
  identified without its label, it shouldn't exist.
- **Standard marks only.** Checkmark = current selection. Dash = partial. Ellipsis = needs more
  input before it executes. No arbitrary symbols.
- **Fixed icon column.** If any menu item has an icon, reserve the column for all of them, or
  the vertical scan line breaks.
- **Dialog titles** match the menu item that opened them, minus the ellipsis.
- **Vertical scan lines** in lists and menus survive. This is what mixed iconed/iconless items
  destroy.
- **Grouping over separators.** Dividers are a last resort; whitespace groups first.
- **Modeless when possible.** A modal takes control away; earn it.
- **Feedback for anything slow.** No silent long-running action.

## E. Iconography

- One action, one icon. Never reuse an icon for two meanings.
- Consistent family: stroke weight, perspective, lighting, and optical size all match.
- Designed small first — clear silhouette, minimal interior detail, pixel-aligned.
- No text inside icons. It doesn't localize and it doesn't scale.
- Paired actions get mirrored metaphors (undo/redo, prev/next).
- Deviations from the icon registry need a stated rationale.

## F. Genre convention

Players arrive with expectations from the genre. Match them or justify the deviation explicitly —
"this is a racer, so the speedometer belongs bottom-right" is a real constraint. Novelty in the
HUD costs the player learning time they'd rather spend playing.

`~/p/wm_afterhours/inspiration/` holds reference shots from shipped games (Ace Combat, Mini
Motorways, PowerWash, Kirby Air Riders, Deadspace, and others). When a convention question comes
up, look at how they solved it before inventing.
