# Afterhours integration

Locate the engine checkout through the game's build configuration or submodule.
Paths below are relative to that checkout. These observations came from a local
revision identified as `d094d47` plus its working tree. Read the current code
before relying on them. No engine source is reproduced here.

## Storage

`src/plugins/files.h` exposes `files::get_save_path()`, `get_config_path()`,
`write_string_atomic()`, and `read_string()`. Path initialization is implemented
in `src/plugins/files.cpp`; consumers of those definitions must link that file.
Use the initialized save path for gameplay and the config path for preferences.
Do not depend on the working directory, resource directory, or executable being
writable. The native path is game-specific; it does not itself isolate Steam
accounts sharing an OS login.

The inspected atomic writer creates a sibling file with `TEMP_SUFFIX`, writes
and closes it, then calls `std::filesystem::rename`. Its temporary filename is
fixed per destination. Concurrent writers can interfere; temporary-file sweeping
must also be excluded while writes are active. Serialize access before reusing
this helper. Verify overwriting an existing destination on every target platform
and filesystem; preserve the original if replacement is unsupported or fails.

The helper returns `bool`, with no durable flush of the file or directory. Its
success does not establish survival across power loss. If the contract requires
that guarantee, implement and test the appropriate platform commit operation.
Do not delete the destination first as a replacement workaround.

`sweep_temp_files()` discards temporary files, including potentially complete
but uncommitted candidates. It does not recover backups. `read_string()` returns
the entire file or `nullopt`; add bounded reads and distinguish missing,
unreadable, malformed, and unsupported input where gameplay recovery needs it.
Use errors that let the caller choose a recovery action; preserve native error
details in diagnostics where the backend provides them.

`src/plugins/settings.h` demonstrates format selection and file persistence.
Its callbacks, default behavior, and mutation of provider state are not a
game-world restore protocol. Reuse appropriate helpers without forcing gameplay
through settings initialization.

## ECS capture and activation

Inspect `src/core/system.h` to place capture relative to gameplay systems,
`merge_entity_arrays()`, and cleanup. Pending entities and cleanup-marked entities
need a deliberate policy. Do not infer a safe point solely from "end of frame."

`EntityCollection` owns entities, handle slots, singleton mappings, and indexes.
Copying its shared pointers does not create an independent snapshot. Capture
explicit game records while the owning thread has a coherent view.

`EntityHelper::set_default_collection()` changes a thread-local pointer; an unset
pointer falls back to the global collection. This is not thread-safety for shared
entities or a complete world swap. If using a staging collection, retain its
lifetime, scope and restore any collection binding, and inspect systems for
cached references or global side effects before activation. Rebuild singleton
registrations and indexes, and replace cached runtime handles that refer to the
old world. UI, audio, and other permanent services need explicit ownership.

`EntityHandle` stores a slot and generation. It detects stale references within
a collection; its fixed-width fields do not establish identity across restarts.
Prefer save-specific IDs with a saved-ID-to-new-handle map: create entities first,
then resolve relationships. Persisting runtime IDs instead requires a complete,
tested allocator/identity restoration scheme. Do not use runtime component type
numbers as durable schema identifiers without proving their stability.

`src/core/pointer_policy.h` checks whether the template arguments themselves are
pointer-like. It does not recursively inspect their members. Audit nested records
and containers even if `static_assert_pointer_free_types()` passes.

## Random state

`src/plugins/random.h` exposes the run seed through `HasRandomSeed`.
`src/random_engine.h` exposes the generator through `RandomEngine::engine()`.
The seed restarts a sequence; it does not capture its current position. Exact
continuation needs the advanced generator state and any stateful distribution
state, or another proven reconstruction mechanism.

The inspected string-seed path uses `std::hash<std::string>`. Do not promise the
same sequence across toolchains from that path. Distribution behavior and game
update order also matter. Limit deterministic continuation claims to tested
builds/platforms unless a portable algorithm and format are defined.

## Test entry points

Look for `tests/files_atomic_write_test.cpp` and `tests/settings_save_test.cpp`
as storage examples, then inspect the current build targets before running them.
Add gameplay tests in the consuming game. Existing storage tests do not prove
world restoration, slot ordering, backup policy, or cross-platform durability.
