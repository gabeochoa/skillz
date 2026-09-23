# Conditional concerns

Use the sections that match the game's declared targets and resume behavior.
These are decisions to resolve when applicable, not features to add to every game.

## Accounts, slots, and cloud

Separate slot identity from its display name and filename. Define what renaming,
copying, or importing a save means; do not classify all player edits as cheating.
Bind requests and previews to the captured owner and slot. For Steam accounts
sharing an OS login, scope local saves to the active Steam user and verify the
cloud configuration uses the corresponding ownership boundary. Specify offline
and signed-out behavior rather than accidentally falling back to another user.

Cloud synchronization replicates files; it does not reconcile game state.
Determine whether the platform syncs outside the game or exposes an in-game API.
Use the supported conflict flow, or preserve both branches and let the player
choose. Wall-clock timestamps and local revision counters cannot order divergent
progress reliably across devices. Do not merge inventories or quest state by
field without a domain-specific reconciliation rule.

When the game owns deletion synchronization, use a versioned deletion record or
the service's equivalent so a stale device cannot restore a deleted slot. Ensure
temporary candidates and backup rotation fit the platform's sync rules. A local
commit and a completed upload are different acknowledgement states.

Exercise account switching with a write pending, offline divergent progress,
delete followed by stale sync, and interruption during conflict resolution.
Reopen the selected result and verify both gameplay and slot preview.

## Platform storage and durability

Desktop filesystem helpers do not substitute for console user/storage APIs.
Use the target SDK's documented transactions, quotas, lifecycle notifications,
and completion semantics. Inspect required SDK documentation when available;
report inaccessible platform behavior as unverified instead of inventing calls.
Test full storage, denied access, detached storage, and interrupted commits where
the target supports those failures.

Afterhours' inspected Emscripten paths use in-memory `/save` and `/config`
directories. Files there do not survive browser restart by themselves. A browser
target needs persistent backing, an awaited initial load, and an awaited
persistence completion before reporting the corresponding guarantee. Test quota
failure and a fresh browser session; do not rely on unload to finish a save.

For multi-file worlds, write an immutable candidate generation and commit a
manifest or use the platform transaction facility. Load only a fully committed
generation. Keep its referenced files while backups or cloud clients need them.
Order cleanup after successful commit and recovery selection.

## Exact simulation continuation and safe resumption

Checkpoint games can intentionally rebuild enemies or restart actions. Exact
continuation must account for simulation time, timers, queued events, unfinished
transactions, RNG state, and subsystem state that affects future behavior.
Physics caches or navigation state may be rebuilt if the resulting behavior fits
the contract. A raw memory dump ties the save to pointers, build layout, and
external resources, so it is not a portable default.

Test equivalent future inputs after uninterrupted play and after save/restart/load
when deterministic continuation is promised. Compare the gameplay observations
the contract specifies; encoding equality alone is insufficient.

Validate the restored position against current world geometry and progression.
Choose a game-appropriate recovery checkpoint or reject the save if no safe
continuation exists. Consider death loops and incomplete actions when placing
autosaves; preserve a useful earlier checkpoint where the design calls for it.

## Content updates and external effects

Use durable content identifiers rather than vector positions or display names.
Define migration, substitution, or rejection for removed items, changed quest
stages, missing mods, and incompatible generator versions. Keep released fixtures
and test them through the complete restore path. Migrate a copy and retain the
original until a new save commits successfully. Avoid silently skipping unknown
required content and then saving the reduced world over the original.

Local replayable state can restore owned rewards without triggering grant code.
Server inventory, purchases, and external achievements need their authoritative
service's reconciliation or idempotency mechanism. A client save cannot provide
exactly-once external effects on its own.

Treat edited files as untrusted input at the parser boundary. Check sizes,
references, enums, and domain constraints before allocation or activation.
Checksums detect accidental changes, not authenticity. Add anti-cheat or
authentication only when the game requires it and can enforce the chosen trust
boundary; hiding a client-side key does not make a local save authoritative.
