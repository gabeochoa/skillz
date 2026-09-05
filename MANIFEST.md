# Skill manifest

Regenerated 2026-09-05 by the public-cleanup pass. Tree hashes use the recipe in
`bin/tree_hash.py`: sha256 over sorted `sha256 relpath` lines. The `sha256` field in
`manifest.json` uses the older recipe `bin/check.sh` reads; both are recorded per
skill. Provenance and licence status are in `THIRD_PARTY_NOTICES.md`.

| Group | Skills |
|---|---|
| writing | 6 |
| product-ux | 3 |
| coding | 18 |
| build-test-release | 8 |
| research-data | 2 |
| operations | 2 |
| agent-workflow | 10 |
| **total** | **49** |

No ungrouped skills remain.

## Skills

| Skill | Group | Files | Tree hash | Source |
|---|---|---|---|---|
| `bro` | writing | 1 | `e4a4874c6c26` | vendored, verbatim |
| `gabe-writing` | writing | 5 | `c311fcfd3c90` | derived here |
| `teach` | writing | 1 | `2840771b9007` | vendored, verbatim |
| `technical-writing` | writing | 1 | `265eff18c696` | vendored, verbatim |
| `unslop` | writing | 1 | `ad04b95988c3` | vendored, verbatim |
| `in-my-voice` | writing | 3 | `6d40d4b9d400` | derived here |
| `customer-obsession` | product-ux | 1 | `a2e5c6c6a816` | personal, verbatim |
| `principle-exhaust-the-design-space` | product-ux | 1 | `0a85f973dac4` | vendored, verbatim |
| `principle-experience-first` | product-ux | 1 | `2153269b1257` | vendored, verbatim |
| `architect` | coding | 4 | `fb1a84b3f09a` | vendored, verbatim |
| `no-comments` | coding | 1 | `cac6a19f326e` | vendored, verbatim |
| `ponytail-lazy-coding` | coding | 1 | `96fc660c1da4` | derived here |
| `principle-boundary-discipline` | coding | 1 | `17634f49174c` | vendored, verbatim |
| `principle-fix-root-causes` | coding | 1 | `63e7923deb7b` | vendored, verbatim |
| `principle-foundational-thinking` | coding | 1 | `bb9f571a079f` | vendored, verbatim |
| `principle-laziness-protocol` | coding | 1 | `d5de59c0dccc` | vendored, verbatim |
| `principle-make-operations-idempotent` | coding | 1 | `2b2c07adf886` | vendored, verbatim |
| `principle-migrate-callers-then-delete-legacy-apis` | coding | 1 | `a17e6098cef2` | vendored, verbatim |
| `principle-minimize-reader-load` | coding | 1 | `287bd8118f75` | vendored, verbatim |
| `principle-model-the-domain` | coding | 1 | `7f6eb9542101` | vendored, verbatim |
| `principle-outcome-oriented-execution` | coding | 1 | `51934aef31d2` | vendored, verbatim |
| `principle-redesign-from-first-principles` | coding | 1 | `28f8b0b31f49` | vendored, verbatim |
| `principle-separate-before-serializing-shared-state` | coding | 1 | `18c0a29f9c34` | vendored, verbatim |
| `principle-subtract-before-you-add` | coding | 1 | `e5ffe2f3df07` | vendored, verbatim |
| `principle-type-system-discipline` | coding | 1 | `6ab29198f49f` | vendored, verbatim |
| `typescript-best-practices` | coding | 2 | `ab12421b3c56` | vendored, verbatim |
| `value-oriented-programming` | coding | 1 | `e1dae94b5e5c` | derived here |
| `blast-radius` | build-test-release | 1 | `6f0c8411506d` | vendored, verbatim |
| `create-verification-skill` | build-test-release | 4 | `a03b38d81153` | vendored, verbatim |
| `interrogate` | build-test-release | 5 | `3d48009cbe21` | vendored, verbatim |
| `maintain-verification-skill` | build-test-release | 1 | `563bc2166275` | vendored, verbatim |
| `principle-build-the-lever` | build-test-release | 1 | `3ecc0d308dfc` | vendored, verbatim |
| `principle-prove-it-works` | build-test-release | 1 | `488e0bbae265` | vendored, verbatim |
| `principle-sequence-verifiable-units` | build-test-release | 1 | `6b584ce1f073` | vendored, verbatim |
| `tdd` | build-test-release | 1 | `ab7381679f86` | vendored, verbatim |
| `how` | research-data | 5 | `2ad3455f9573` | vendored, verbatim |
| `why` | research-data | 13 | `1aeb0f67b285` | vendored, verbatim |
| `setup-pstack` | operations | 1 | `37c437344763` | vendored, verbatim |
| `show-me-your-work` | operations | 3 | `1ef3f5377609` | vendored, verbatim |
| `arena` | agent-workflow | 1 | `4e03e7f49568` | vendored, verbatim |
| `automate-me` | agent-workflow | 1 | `aebf66dce388` | derived here |
| `figure-it-out` | agent-workflow | 1 | `64d361beefd8` | vendored, verbatim |
| `poteto-mode` | agent-workflow | 45 | `6b3089e6cb30` | derived here |
| `principle-encode-lessons-in-structure` | agent-workflow | 1 | `366540ef8296` | vendored, verbatim |
| `principle-guard-the-context-window` | agent-workflow | 1 | `91c049dc9838` | vendored, verbatim |
| `principle-never-block-on-the-human` | agent-workflow | 1 | `c5c22e1eebe4` | vendored, verbatim |
| `recall` | agent-workflow | 1 | `d6d0d726dabe` | vendored, verbatim |
| `reflect` | agent-workflow | 5 | `d996e0d51741` | vendored, verbatim |
| `swarm` | agent-workflow | 1 | `671f494eef90` | vendored, verbatim |

## Resolved this pass

| Skill | Resolution |
|---|---|
| `customer-obsession` | moved to `skills/product-ux/customer-obsession`; the updated installed copy superseded the flat repo copy after a sha256 match, and the flat copy was removed only afterwards. `pending_move` cleared. |

`in-my-voice` was imported from the agent platform's skill loader and generalized 
before it was tracked. Its unsanitized source is kept ignored under `.local-meta/`.

## Pending hosts

| Host | State |
|---|---|
| workstation-b | Offline for every attempt in this pass and the one before it. Not reachable, so no inventory is claimed. This is the only host-side gap left in the repo. |

Conflict and deferral detail is in `CONFLICTS.md`.
