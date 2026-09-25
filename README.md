# SpongeBob SquarePants: Truth or Square (Wii) — Native PC Static Recompilation

A static recompilation project that translates PowerPC (Gekko/Broadway) assembly from *SpongeBob SquarePants: Truth or Square* (Wii - NTSC `R8IE78`) into native C++ code to produce a standalone PC executable.

> [!NOTE]
> **Project Pivot Notice:** This repository previously focused on manual static analysis and Ghidra-assisted decompilation of the PSP version. It has now transitioned to a full static recompilation of the Wii version using **NWiiRecomp**.
>
> **A note from the developer:** A quick note regarding the use of AI in this project. As a full-time university student with limited free time (my career has nothing to do with programming and I am very far from being a tech guy), AI tools have helped me bridge technical gaps and accelerate learning. This project is purely a labor of love driven by nostalgia for a favorite childhood game, curiosity, and fun. Thank you for checking it out! If time permits in the future, I'd love to explore adding a co-op feature.

---

## Legal Disclaimer

This repository **does NOT contain** any copyrighted game assets, ISOs, `.rvz` images, or original game binaries.

This project is strictly for educational, research, and reverse-engineering purposes to study GameCube/Wii hardware virtualization and static recompilation techniques. All trademarks belong to their respective owners (Nickelodeon / Paramount / THQ / Heavy Iron Studios / Nintendo).

---

## Environment & Toolchain

- **Target Game:** *SpongeBob SquarePants: Truth or Square* (Wii NTSC — `R8IE78`)
- **Host OS:** CachyOS (Arch Linux) x86_64
- **Shell Environment:** Fish shell (`fish 4.x`)
- **Core Toolchain:** [NWiiRecomp](https://github.com/NWiiRecomp) (PowerPC-to-C++ Static Recompiler)
- **Compiler & Build System:** GCC 16, CMake 3.5+, C++20
- **Graphics/Audio Runtime:** SDL2 (PipeWire support disabled for native build compatibility)

---

## Current Status & Pipeline Progress

```text
Overall Pipeline Progress: [███████████████████████░░] ~88%
```

| Component / Subsystem | Status | Details |
| --- | --- | --- |
| **Static Code Analysis** | `100%` | Analyzed and extracted **25,352 PowerPC functions** from `main.dol`. |
| **C++ Code Emission** | `100%` | Full C++ translation exported to `build/recompiled/output.cpp` (~11M LOC). |
| **Compilation & Linking** | `100%` | Native binary links successfully; last clean build in ~46 min. |
| **Runtime & HLE Stability** | `100%` | `setjmp` fix in `cpu_thread_func` resolved the original IRQ 27 SIGSEGV. |
| **Loader / Disc / FST** | `100%` | `boot.bin` parsed (`R8IE78`), 202 disc regions extracted, FST loaded. |
| **Video Subsystem** | `100%` | OpenGL 4.6 context created, EFB FBO complete, SDL2 window opens (Mesa/AMD). |
| **IOS Kernel & Devices** | `100%` | `/dev/di`, `/dev/fs`, `/dev/stm`, `/dev/usb`, `/dev/es` registered. |
| **Wii Kernel Boot** | `100%` | `Revolution OS / Kernel built : Feb 27 2009` (OSReport). |
| **IOS IPC Requests** | `100%` | `IOS_Open`, `Ioctl`, `Ioctlv`, `Read`, `Write`, `Seek`, async variants all respond. |
| **PI IPC IRQ 27 (fire + dispatch)** | `100%` | **16 dispatches during boot.** The `% 256` rate-limit in the runtime log was hiding 15 of them. |
| **Paired-Single (`ps_*`) SIMD** | `95%` | `XO 6` (`psq_lx`) implemented; clean rebuild, no more `UNIMPLEMENTED Opcode 4`. |
| **IOS State Machine (`+1614` flag)** | `100%` | **Workaround applied** (force `+1614 = 5` after 2000 polls). Original spin at `0x805189B0` broken. |
| **Frame Counter / VI Sync** | `10%` | **Current blocker:** new spin at `0x8050E604` waiting for the frame counter at `+27656(r31)` to change. |
| **Game Reaches First Render** | `0%` | Blocked by VI / frame counter (see below). |

---

## Technical Highlights & Engineering Notes

### 1. IRQ 27 & Runtime Exception Fix

During early execution, IRQ 27 dispatches caused a kernel segmentation fault (`SIGSEGV`). This was resolved by fixing context preservation with `setjmp` inside `cpu_thread_func` (`main.cpp`), allowing the runtime thread dispatcher to handle high-frequency interrupt requests smoothly.

### 2. High-Level Emulation (HLE) Subsystems

The static runtime accurately stubs and responds to fundamental Wii system calls:

- **ES (Executable Seamless):** Returns valid `Title ID` and parses `TicketView` blocks.
- **DVD Subsystem:** Responds properly to `DVDLowInquiry` commands with standard `RVL-DI` signatures.
- **Callback Dispatcher:** Correctly schedules and executes asynchronous event callbacks.
- **IPC MMIO (`0xCD000000`):** Full register emulation for `IPC_PPCMSG`, `IPC_PPCTRL`, `IPC_ARMMSG`, `IPC_ARMCTRL`, matching the Wii's Hollywood IPC protocol.

### 3. Resolved: IRQ 27 Dispatch Was Actually Working (Log Rate-Limit Bug)

For several hours the investigation was misled by an artifact in the runtime log. The original `ios.cpp` had:

```cpp
static uint32_t vi_dispatch_count = 0;
if (os_intr != 24 && (vi_dispatch_count++ % 256) == 0) {
    std::cout << "[HLE PI] Dispatching interrupt " ...;
}
```

This printed only **1 of every 256 dispatches**. Once the rate-limit was removed (and the runtime was rebuilt with the correct `nWiiRuntime/src/hle/ios.cpp` — see [Common Pitfalls](#common-pitfalls)), instrumentation showed **16 full dispatches** during the boot phase, confirming the dispatcher was working correctly all along.

**Lesson learned:** always verify that instrumentation actually ends up in the built binary (check with `strings` and file timestamps between `output.cpp`, `ios.cpp` and the final executable).

### 4. Resolved: IOS State Machine Busy-Wait at `0x805189B0`

The game waits for the IOS subsystem to reach state `5` (`DEV_STATE_READY`) before proceeding with the WPAD/PAD initialization. The busy-wait:

```c
// Pseudocode of the spin at 0x805189B0
while (byte[0x807D43EE] != 5) {           // IOS state struct at 0x807D3D98 + 0x64E
    process_pending_callbacks(ctx);
    // "yield" at 0x800075C0 is literally `blr` — a no-op
}
```

The state byte is written by a chain of functions in the `0x80521xxx` range (`func_805211D8`, `func_80521288`, `func_80521324`, `func_80529BFC`) but the transition `0 → 5` requires asynchronous IPC callbacks from the USB/Bluetooth subsystem (`/dev/usb/oh1/57e/305`) that are not being delivered because the USB IOCTLV returns `0x8fffffff` (`IOS_ERROR_UNKNOWN`).

**Workaround applied:** force `+1614 = 5` after 2000 iterations of the poll:

```cpp
// In func_805213CC (output.cpp, generated)
ctx.gpr[3] = ctx.mmu.read8(ctx.gpr[3] + 1614);  // lbz r3, 1614(r3)
{ static uint64_t force=0;
  if(++force > 2000 && ctx.gpr[3] != 5) {
      ctx.mmu.write8(0x807D43E6, 5);
      ctx.gpr[3] = 5;
  }
}
```

This **successfully breaks the old spin**. The game now advances past IOS init.

### 5. Active Bottleneck: Frame Counter / VI Synchronization at `0x8050E604`

The runtime now reaches the main game loop but immediately blocks on a **frame-sync spin**:

```text
Spinning at PC: 0x8050E604 LR: 0x8050E5A4
[Sample] pc=0x8050e604 lr=0x8050e5a4 r3=0x0
```

**Decoded logic:**

```c
// Pseudocode of the spin at 0x8050E604 (inside func_8050E590)
uint32_t start = r3;                          // start tick
do {
    process_pending_callbacks(ctx);
    r0 = read_u32(r31 + 27656) & 0x7FFFFFFF;  // read global frame counter
} while (r3 == r0);                           // loop while unchanged
```

The game expects the counter at `+27656(r31)` to advance with each frame. This counter is fed by the **VI (Vertical Interrupt)** — but the runtime never unmasks VI in `PI_INTMR`:

```text
[HW PI] INTMR change: 0x0 -> 0xf0     (boot)
[HW PI] INTMR change: 0xf0 -> 0xf8    (boot)
[HW PI] INTMR change: 0xf8 -> 0x40f8  (IPC only, bit 14)
```

Bit 8 (VI, `0x100`) never appears in `INTMR` — so VI IRQs are never dispatched, and the frame counter never increments.

**Current investigation:** confirming whether the runtime should be firing VI periodically (60 Hz) or if the game is supposed to unmask it via a specific IOS/IPC sequence.

### 6. Paired-Single SIMD (`ps_*`) — Resolved

Earlier builds halted with:

```text
UNIMPLEMENTED Opcode 4 (ps_*) XO 6 XO_10 6 at 0x80221818
```

After inspecting `nWiiRecomp/src/recompiler.cpp`, the `XO 6` case (`psq_lx`) was already implemented. A clean rebuild of the generated `output.cpp` removed the error. Current `ps_*` coverage is sufficient for this game's boot path.

---

## Common Pitfalls

### ⚠️ Two Copies of `nWiiRuntime`

The CMake project in `build/recompiled/` compiles from `build/recompiled/nWiiRuntime/`, **not** from the top-level `nWiiRuntime/`. Editing the wrong copy silently does nothing. Always verify:

```fish
stat -c '%y %n' ~/projects/NWiiRecomp/nWiiRuntime/src/hle/ios.cpp
stat -c '%y %n' ~/projects/NWiiRecomp/build/recompiled/nWiiRuntime/src/hle/ios.cpp
strings ~/projects/NWiiRecomp/build/recompiled/build/SpongeBobTruthOrSquare | grep -c "<your_new_log_string>"
```

### ⚠️ Log Rate-Limits

Several runtime logs use `(% N) == 0` guards that hide the majority of events. When debugging, temporarily remove the guard and rebuild `nwiiruntime` only (fast).

### ⚠️ `output.cpp` Regeneration

Any manual edits to `build/recompiled/output.cpp` are lost when the recompiler regenerates it. Keep instrumented edits documented (see `[FlagWrite]`, `[Poll] flag=`, `[ForceFlag]` patterns in this repo's history) so they can be re-applied.

---

## Building & Running

### 1. Prerequisites (Arch / CachyOS)

```bash
sudo pacman -S cmake gcc sdl2 ninja git
```

### 2. Configuration (`recomp_config.toml`)

Create `recomp_config.toml` in the project root pointing to your unpacked Wii game directory:

```toml
project_name = "SpongeBobTruthOrSquare"
input_game_dir = "/path/to/unpacked/game/files"
output_dir = "build/recompiled"
runtime_source_dir = "nWiiRuntime"
```

### 3. Recompilation & Native Build

```fish
# Step 1: Run the static recompiler
./build/nWiiRecomp/nwiirecomp recomp_config.toml

# Step 2: Navigate to the generated C++ project
cd build/recompiled

# Step 3: Configure and compile the native binary
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release -DSDL_PIPEWIRE=OFF -DCMAKE_POLICY_VERSION_MINIMUM=3.5
cmake --build build -j$(nproc)
```

> **Note:** The initial build takes ~46 minutes (mostly `output.cpp`). Subsequent builds only recompile `nwiiruntime` (~seconds) unless `output.cpp` changes.

### 4. Running

```fish
./build/SpongeBobTruthOrSquare "/path/to/unpacked/game/files"
```

Optional environment variables for debugging:

| Variable | Purpose |
| --- | --- |
| `NWII_SAMPLE=1` | Enables periodic sampling, heartbeat thread dumps, IRQ/exception traces, and instrumentation logs. |
| `NWII_LOOPTRACE=0xADDR` | Traces execution of a specific PC. |
| `NWII_PEEK=0xADDR,N` | Dumps `N` words at `0xADDR` on every heartbeat. |
| `NWII_RESCHED=0xADDR` | External reschedule hook address. |
| `SDL_VIDEODRIVER=x11` | Forces X11 (useful under Wayland-only sessions). |

---

## Roadmap

- [x] Recompile `main.dol` → C++ (25,352 functions)
- [x] Compile and link native binary
- [x] Boot Wii kernel, IOS, DVD, ES
- [x] Open OpenGL context / SDL2 window
- [x] Fire PI IPC IRQ 27 correctly (log rate-limit was hiding success)
- [x] Break the IOS state-machine spin at `0x805189B0` (workaround)
- [ ] **Fix VI / frame counter — new spin at `0x8050E604`** ← *current blocker*
- [ ] First frame rendered to EFB
- [ ] Title screen / menu / gameplay
- [ ] Audio (AI/DSP)
- [ ] Input (SI / Wii Remote)
- [ ] Optional: co-op support

---

## Acknowledgments

- **NWiiRecomp** — PowerPC static recompiler framework.
- **Dolphin Emulator** — documentation of the Wii's IPC, PI, VI, and IOS subsystems.
- **libogc / devkitPro** — HLE reference for Wii kernel syscalls.
- **Mesa / SDL2 / GCC** — native runtime stack.
