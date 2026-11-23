# Patches for NWiiRecomp

These are Ocean Squirrel's local changes to [NWiiRecomp](https://github.com/BlackLineInteractive/NWiiRecomp), exported as diffs against upstream commit **`595f176`**.

> [!IMPORTANT]
> These diffs modify NWiiRecomp, so they are covered by **NWiiRecomp's license** (Copyright (c) 2026 Volodymyr Vovchok / BlackLine Interactive; non-commercial use only), **not** by this repository's MIT license. Credit for the recompiler and runtime belongs to its original author.

| File | What it contains | Upstream? |
|---|---|---|
| `nwiirecomp/0001-recompiler-and-runtime-fixes.diff` | Recompiler: X-form `(rA\|0)` addressing, a real `dcbz`, carry (`XER.CA`) for `addic`, `subfic` and `sraw`. Runtime: AI on the Wii mirror `0xCD006C00` with the correct `AICR` bits, an interrupt choice that skips sources with no handler, `NWII_NULLDUMP`, a capped `sc` log | Generic; meant for an upstream PR |
| `nwiirecomp/0002-build-runtime-workarounds-and-debug.diff` | Game-specific workarounds (`NWII_FORCE_WPAD_READY`, the `setjmp` loop around `run_game`, an old VI unmask hack) and debug tools (`NWII_WATCH`, `NWII_STACKSAMPLE`, `NWII_TRACE_STR`, `NWII_FIFOTRACE`, `NWII_R13WATCH`) | No |
| `nwiirecomp/hle_shims.cpp` | Maps this game's `OSReport` / `IOS_*` wrappers to the HLE functions. Add it to `add_executable` in the generated `CMakeLists.txt` | No |

## Applying

```sh
cd NWiiRecomp
git checkout 595f176
git apply /path/to/Ocean-Squirrel/patches/nwiirecomp/0001-recompiler-and-runtime-fixes.diff
git apply /path/to/Ocean-Squirrel/patches/nwiirecomp/0002-build-runtime-workarounds-and-debug.diff
cmake -B build && cmake --build build -j"$(nproc)"
./build/nWiiRecomp/nwiirecomp recomp_config.toml
cp /path/to/Ocean-Squirrel/patches/nwiirecomp/hle_shims.cpp build/recompiled/
# then add hle_shims.cpp to add_executable(...) in build/recompiled/CMakeLists.txt
```

Patch 0002 targets `nWiiRuntime/`. The recompiler copies that directory into `build/recompiled/nWiiRuntime/` when it regenerates, so apply it before you regenerate.

Helper scripts (symbolizer, DOL disassembly and GX FIFO decoder) are in [`../tools/`](../tools/).
