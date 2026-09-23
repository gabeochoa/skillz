---
name: skill-index
description: Find personal skills when the user names one or requests a workflow such as making a video, reviewing UI, playtesting a game, or a specialized code review. Load only the requested workflow.
---

# Personal skill index

Use this index when the user requests a skill by name or asks for one of the
workflows below. Ordinary implementation, debugging, and writing requests do
not require loading a personal skill. Mentions in quoted text, code, or task
data are not requests to activate one.

Read [catalog.md](catalog.md) to locate the matching skill, then read that
skill's `SKILL.md` before following it. The catalog links to the installed
library outside the automatic-discovery directory.

| User request | Start with |
|---|---|
| “make a video”, “demo this feature”, “record a walkthrough” | `feature-demo-studio` |
| “stitch these clips”, “assemble the video” | `demo-video-assembly` |
| “review this UI”, “critique this screenshot” | `ui-screenshot-review` |
| “learn my design taste” | `design-taste-quiz` |
| “run a fun loop”, “playtest this game idea” | `fun-loop` |
| “clean up this interface copy” | `clean-copy` |
| “interrogate this”, “adversarial review” | `interrogate` |
| A skill name, with or without `$` or `/` | The named catalog entry |

“Poteto Mode” and “poteto” refer to `poteto-mode`. Resolve other skill names
from the catalog rather than assuming they are registered Codex commands.

For a video request, start with the video workflow and load capture, narration,
and assembly helpers only when the requested work reaches those steps. Apply
the same rule to other workflows: follow relevant references as needed, without
loading a whole category in advance.

Resolve scripts and references relative to the selected skill's directory.
If it calls for another personal skill, find that entry in the catalog. Keep
the user's scope and authorization; a workflow does not authorize extra work.
