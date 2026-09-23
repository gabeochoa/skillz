---
name: afterhours-save-load
description: Design, implement, and verify gameplay save/load in Afterhours games. Use when adding checkpoints, persistent runs, save slots, or world restoration, or reviewing an existing Afterhours save system.
---

# Afterhours save/load

Build a save system that lets the player resume a coherent game from acknowledged
progress. Serialization is one part of that contract. Choose the guarantees the
game needs, implement them, and exercise failures before declaring completion.

## Establish the contract

Inspect the game's Afterhours revision, ECS lifecycle, storage code, gameplay
state, and executable test paths. Read [Afterhours integration](references/afterhours.md)
before choosing engine APIs. Treat its observations as a starting point to
verify against the checkout, not a promise about every engine revision.

Record a short contract in the game's existing design notes or implementation
summary. Resolve these decisions from the project first; ask about consequential
product choices that remain unknown.

| Decision | What to establish |
|---|---|
| Resume behavior | Checkpoint restart, persistent run, or exact simulation continuation; what resets intentionally |
| Progress | Save triggers and safe boundaries; maximum progress loss; manual saves and autosave retention |
| Ownership | Supported platforms, local profiles or platform accounts, slot identity, storage location |
| Completion | What "saved" guarantees; what happens on write failure, quit, suspend, and failed recovery |
| Compatibility | Which released saves remain supported; content changes and newer save versions |
| Cost | Main-thread time and peak-memory budgets on target hardware; acceptable loading transitions |

Checkpoint-only games can save at a paused transition with a small synchronous
write if measurements meet the contract. Add threads, compression, binary
formats, or storage abstractions when the game requires them. Keep an existing
format that fits; JSON is a valid choice.

Read the applicable sections of [conditional concerns](references/conditional-concerns.md)
for cloud, account switching, browser/console storage, exact continuation, or
external rewards. Record unsupported capabilities without building them.

## Capture a coherent state

List authoritative saved values, derived values to rebuild, and deliberately
transient state. Check relationships as well as individual fields: spending
money and acquiring an item must appear together; quest completion must agree
with its world changes and reward ownership.

Use owned value records for snapshots. Encode persistent entity and content
identities explicitly; exclude pointers, GPU resources, callbacks, and raw ECS
memory. Decide how references resolve after entities are recreated. Record a
format version and enough identity to reject saves for the wrong game or slot
when applicable. Keep previews tied to the same committed snapshot.

Capture at a defined update boundary after relevant gameplay transactions finish.
Settle or represent pending entity creation, destruction, and unfinished actions.
If capture spans frames, use a proven consistency mechanism; walking a changing
world over several frames does not create a coherent snapshot. Give workers an
owned, immutable snapshot and keep them away from the live ECS.

## Commit without losing acknowledged progress

Choose one writer per destination. When saves overlap, preserve commit order or
discard superseded requests before they can replace newer state. Bind each
request to its captured slot, account, and world generation. Loading, deleting,
or switching slots must settle or invalidate pending work so it cannot commit
later into the wrong session or resurrect a deleted save.

Synchronize invalidation with final replacement; a generation check followed by
an unguarded rename leaves a race. Ignore stale completion callbacks. Slot
deletion must also retire its recovery generations so loading cannot revive it.

Write a candidate without truncating the last committed save, then replace it
using the target platform's supported operation. Preserve a validated previous
generation when recovery is part of the contract. A backup update must not
destroy the only good copy before the new commit succeeds. Multi-file saves need
a coherent generation commit; independent atomic writes do not provide one.

Separate snapshot capture, encoding, storage commit, and UI acknowledgement.
Report "saved" only after the selected guarantee succeeds. Progress made after
capture remains unsaved even when that write completes. A failed write keeps
dirty state and exposes a useful retry or exit choice. Distinguish local commit
from cloud upload. Do not promise power-loss durability from an atomic rename.

## Restore before activating

Read into a candidate, check format and supported version, migrate in memory,
then validate gameplay constraints and references. Bound file sizes, counts,
and allocations at the input boundary. Handle missing content and unsafe spawn
locations according to the contract, with explicit recovery or rejection.

Build and validate the replacement state before activation. If the game cannot
stage a separate world, make the apply step non-failing after validation or
provide a tested rollback. Do not clear the live world and then discover that
half the saved state cannot load.

Recreate entities, resolve references, rebuild derived state, then activate at a
controlled update boundary. Restore reward ownership and world changes without
replaying purchase, quest-completion, or achievement side effects. Repeated
loading must not accumulate state or grant duplicate rewards.

Keep the original file when load, migration, or recovery fails. A corrupt or
unsupported save is different from a missing save: starting defaults must not
silently overwrite it on the next autosave. Validate backups through the same
load path. Reject unsupported newer versions without rewriting them.

## Verify the game, then report

Use isolated save directories and the project's executable test path. Add
rerunnable fault injection at the storage boundary where needed. Do not test on
the player's real saves. Select cases by the contract and assert game behavior,
not merely that encoded bytes round-trip.

| Case | Required observation |
|---|---|
| Save, exit, restart, load, continue | The actual player path resumes the promised state and remains playable |
| Transaction boundary and repeated load | Money/items, quests/rewards, and references remain consistent; state does not accumulate |
| Failed or interrupted write | Inject open, partial-write, flush, or replacement failure and terminate at commit boundaries; reopening yields a complete committed save and no false success |
| Corrupt save or restore failure | The original file and running world survive; recovery succeeds or reports failure without overwriting evidence |
| Version compatibility | Fixtures for each supported released version migrate correctly; newer versions are rejected without modification |
| Overlapping work, when supported | Save/load/switch/delete races cannot replace newer progress, target another account, or resurrect a slot |
| Representative maximum state | Capture time, frame-time spikes, encoding/I/O cost, load cost, and peak memory meet the chosen budgets |

Process termination tests prove interruption behavior, not power-loss durability.
For stronger durability claims, verify the platform commit API and use suitable
fault tests. Measure the main-thread snapshot and locking cost even when I/O is
asynchronous; the source discussion's hitch threshold is not a universal budget.

Deliver the implemented contract, commands and observed results, the storage
location and recovery behavior, and remaining platform or compatibility limits.
If hardware or SDK access prevents a check, name the unverified guarantee. Keep
game-specific schema and policy in the game; promote engine helpers only when
their shared responsibility is demonstrated.
