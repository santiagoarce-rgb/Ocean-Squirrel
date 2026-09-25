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
Overall Pipeline Progress: [████████████████████░░░░░] ~82%
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
| **PI IPC IRQ 27 (fire)** | `100%` | `[IPC] irq raised` confirmed **17+ times** during boot. |
| **PI IPC IRQ 27 (dispatch)** | `30%` | **Only the first dispatch reaches the handler.** Subsequent IRQs are skipped. |
| **Paired-Single (`ps_*`) SIMD** | `95%` | `XO 6` (`psq_lx`) already implemented; rebuild succeeded, no more `UNIMPLEMENTED Opcode 4`. |
| **IOS State Machine (`+1614` flag)** | `10%` | Flag expected to reach `5`; currently stuck at `0`. |
| **Game Reaches First Render** | `0%` | Blocked by the spin (see below). |

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

### 3. Active Bottleneck: IOS State Machine Busy-Wait at `0x805189B0`

The runtime now boots deep into IOS initialization, but execution blocks on a **busy-wait spin**:

```text
Spinning at PC: 0x805189B0 LR: 0x805189AC
  call stack: 0x805189AC ← 0x80598D50 ← 0x80586EC8 ← 0x8055E5CC ← 0x801DDBDC ← 0x801DD824
  intmr=0x40F8  intsr=0x100  msr=0x8032
```

**Decoded logic:**

```c
// Pseudocode of the spin at 0x805189B0
while (byte[0x807D43EE] != 5) {     // byte at IOS state struct 0x807D3D98 + 0x64E
    process_pending_callbacks(ctx);
    // "yield" at 0x800075C0 is literally `blr` — a no-op
}
```

The flag at `0x807D43EE` is written by the IOS state machine (`func_805211D8`, `func_80521288`, `func_80521324`) and is expected to reach `5` once the USB/IPC initialization completes.

### 4. Root Cause: IRQ 27 Dispatches Only Once

Instrumentation confirms:

```text
[IPC] irq raised ... pc=0x805759b8
[HLE PI] Dispatching interrupt 27 to handler 0x80558FB0   ← only the first time
[IPC] irq raised ... pc=0x805759b8                        ← 16 more, never dispatched
[IPC] irq raised ... pc=0x8057247c                        ← ...
...
[Heartbeat] intmr=0x40F8  intsr=0x100                     ← bit 0x4000 already cleared
```

The PI pending bit `0x4000` is consumed after the first dispatch and never re-observed by the dispatcher on subsequent IRQs. Investigation is focused on three candidate paths inside `nWiiRuntime/src/hle/ios.cpp`:

1. **DEC exception block** (~line 1060–1160) potentially `return false` / `longjmp`s *before* the `active_ints` block runs.
2. **`clear_pi_interrupt(0x4000)`** in `hw_ipc.cpp` (via `IPC_ARMCTRL` writes from the guest) racing ahead of the dispatcher.
3. **`ctx.in_callback` / `handler_in_flight`** flags not being reset after the first handler invocation.

### 5. Paired-Single SIMD (`ps_*`) — Resolved

Earlier builds halted with:

```text
UNIMPLEMENTED Opcode 4 (ps_*) XO 6 XO_10 6 at 0x80221818
```

After inspecting `nWiiRecomp/src/recompiler.cpp`, the `XO 6` case (`psq_lx`) was already implemented. A clean rebuild of the generated `output.cpp` removed the error. Current `ps_*` coverage is sufficient for this game's boot path.

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
cmake --build build -j(nproc)
```

### 4. Running

```fish
./build/SpongeBobTruthOrSquare "/path/to/unpacked/game/files"
```

Optional environment variables for debugging:

| Variable | Purpose |
| --- | --- |
| `NWII_SAMPLE=1` | Enables periodic sampling, heartbeat thread dumps, IRQ/exception traces. |
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
- [x] Fire PI IPC IRQ 27 correctly
- [ ] **Fix repeated IRQ 27 dispatch** ← *current blocker*
- [ ] IOS state flag reaches `5`, spin exits
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
