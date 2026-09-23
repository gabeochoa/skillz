# Skill manifest

Updated 2026-09-20. `manifest.json` records source paths and provenance.

| Group | Skills |
|---|---|
| agent-workflow | 10 |
| build-test-release | 9 |
| coding | 19 |
| media | 7 |
| operations | 5 |
| product-ux | 7 |
| research-data | 2 |
| writing | 7 |
| **total** | **66** |

## Skills

| Skill | Group | Files |
|---|---|---|
| `arena` | agent-workflow | 1 |
| `automate-me` | agent-workflow | 1 |
| `figure-it-out` | agent-workflow | 1 |
| `poteto-mode` | agent-workflow | 45 |
| `principle-encode-lessons-in-structure` | agent-workflow | 1 |
| `principle-guard-the-context-window` | agent-workflow | 1 |
| `principle-never-block-on-the-human` | agent-workflow | 1 |
| `recall` | agent-workflow | 1 |
| `reflect` | agent-workflow | 5 |
| `swarm` | agent-workflow | 1 |
| `blast-radius` | build-test-release | 1 |
| `create-verification-skill` | build-test-release | 4 |
| `interrogate` | build-test-release | 5 |
| `layout-qa` | build-test-release | 3 |
| `maintain-verification-skill` | build-test-release | 1 |
| `principle-build-the-lever` | build-test-release | 1 |
| `principle-prove-it-works` | build-test-release | 1 |
| `principle-sequence-verifiable-units` | build-test-release | 1 |
| `tdd` | build-test-release | 1 |
| `afterhours-save-load` | coding | 4 |
| `architect` | coding | 4 |
| `no-comments` | coding | 1 |
| `ponytail-lazy-coding` | coding | 1 |
| `principle-boundary-discipline` | coding | 1 |
| `principle-fix-root-causes` | coding | 1 |
| `principle-foundational-thinking` | coding | 1 |
| `principle-laziness-protocol` | coding | 1 |
| `principle-make-operations-idempotent` | coding | 1 |
| `principle-migrate-callers-then-delete-legacy-apis` | coding | 1 |
| `principle-minimize-reader-load` | coding | 1 |
| `principle-model-the-domain` | coding | 1 |
| `principle-outcome-oriented-execution` | coding | 1 |
| `principle-redesign-from-first-principles` | coding | 1 |
| `principle-separate-before-serializing-shared-state` | coding | 1 |
| `principle-subtract-before-you-add` | coding | 1 |
| `principle-type-system-discipline` | coding | 1 |
| `typescript-best-practices` | coding | 2 |
| `value-oriented-programming` | coding | 1 |
| `demo-video-assembly` | media | 5 |
| `feature-demo-studio` | media | 1 |
| `narration-audit` | media | 3 |
| `narration-pacing-audit` | media | 2 |
| `narration-vocab-audit` | media | 2 |
| `speaker-style-setup` | media | 3 |
| `ui-capture-cdp` | media | 5 |
| `eye` | operations | 3 |
| `file-transfer` | operations | 2 |
| `setup-pstack` | operations | 1 |
| `show-me-your-work` | operations | 3 |
| `skill-evaluator` | operations | 1 |
| `customer-obsession` | product-ux | 1 |
| `design-taste-quiz` | product-ux | 2 |
| `fun-loop` | product-ux | 3 |
| `interface-design` | product-ux | 4 |
| `principle-exhaust-the-design-space` | product-ux | 1 |
| `principle-experience-first` | product-ux | 1 |
| `ui-screenshot-review` | product-ux | 4 |
| `how` | research-data | 5 |
| `why` | research-data | 13 |
| `bro` | writing | 1 |
| `clean-copy` | writing | 1 |
| `gabe-writing` | writing | 5 |
| `in-my-voice` | writing | 3 |
| `teach` | writing | 1 |
| `technical-writing` | writing | 1 |
| `unslop` | writing | 1 |

## Added during the move into dotfiles

Preserved `design-taste-quiz`, `fun-loop`, and `ui-screenshot-review` from the
standalone checkout, including its calibrated taste profile. Imported
`clean-copy` from the local Claude installation.

## Imported from a personal machine (2026-09-06)

A second, independently-built 98-skill checkout was found at
`~/p/skillz-local-98skill-20260906` on a personal machine — unrelated git history,
never pushed anywhere, materialized in one ~34-minute session on 2026-09-06.
It was preserved as-is (not merged) and diffed against this repo by slug.

Of its skills not already covered here, 12 were self-authored, provenance-clear,
had no dependency on anything not imported, and needed no rewrite — imported
verbatim on the `import-local-skills` branch: `interface-design`,
`layout-qa`, `eye`, `file-transfer`, `skill-evaluator`, and all 7 `media/*`
skills (a video-narration production pipeline: `feature-demo-studio` is the
orchestrator over `ui-capture-cdp`, `demo-video-assembly`, the three
`narration-*-audit` skills, and `speaker-style-setup`).

Not imported, left in the preserved build pending an owner decision:
- `audit-design`, `audit-google-design`, `audit-sun-design`, `audit-win95-design`,
  `multi-audit` — each audit skill ships its own 500-900 line reproduction of a
  vendor HIG (Apple/Google/Sun/Microsoft) with no licence established for the
  copy; `multi-audit` only orchestrates the other four.
- `benny/setup-benny`, `benny/triage-issue-reports`, `benny/reproduce-and-fix-issues`
  — genuinely pstack-licensed (MIT) per their own SKILL.md, but structured as a
  non-invocable Cursor automation pack (`disable-model-invocation: true`,
  external Slack/tracker config), a different consumption model than every
  other skill here.

Not imported as duplicates of what this repo already carries: the 6-way
`ponytail/*` split (same MIT source as the already-tracked, consolidated
`ponytail-lazy-coding`) and `ai-tells` (same tropes.fyi taxonomy already
embedded as a reference inside `skills/writing/gabe-writing/`).

Not imported, internal-sourced per the preserved build's own README
("adapted from an internal write-up"): `gdoc-writing-tips`,
`how-to-write-a-skill`. The 24 employer-specific skills were also excluded.

Full delta matrix and counts: see knot `gabeochoa/manager` for this task.

## Resolved this pass

| Skill | Resolution |
|---|---|
| `customer-obsession` | moved to `skills/product-ux/customer-obsession`; the updated installed copy superseded the flat repo copy after verifying that its contents matched, and the flat copy was removed only afterwards. `pending_move` cleared. |

`in-my-voice` was imported from the agent platform's skill loader and generalized
before it was tracked. Its unsanitized source is kept ignored under `.local/`.

## Pending hosts

| Host | State |
|---|---|
| workstation-b | Offline for every attempt in this pass and the one before it. Not reachable, so no inventory is claimed. This is the only host-side gap left in the repo. |

Conflict and deferral detail is in `CONFLICTS.md`.
