
---

# SpongeBob SquarePants: Truth or Square (Wii) — Native PC Static Recompilation

A static recompilation project that translates PowerPC (Gekko/Broadway) assembly from *SpongeBob SquarePants: Truth or Square* (Wii - NTSC `R8IE78`) into native C++ code to produce a standalone PC executable.

> [!NOTE]
> **Project Pivot Notice:** This repository previously focused on manual static analysis and Ghidra-assisted decompilation of the PSP version. It has now transitioned to a full static recompilation of the Wii version using **NWiiRecomp**.
> **A note from the developer:** A quick note regarding the use of AI in this project, as a full-time university student with limited free time (my career has nothing to do with programming and I am very far from being a tech guy), AI tools have helped me bridge technical gaps and accelerate learning. This project is purely a labor of love driven by nostalgia for a favorite childhood game, curiosity, and fun. Thank you for checking it out! If time permits in the future, I’d love to explore adding a co-op feature.

---

##  Legal Disclaimer

This repository **does NOT contain** any copyrighted game assets, ISOs, `.rvz` images, or original game binaries.

This project is strictly for educational, research, and reverse-engineering purposes to study GameCube/Wii hardware virtualization and static recompilation techniques. All trademarks belong to their respective owners (Nickelodeon / Paramount / THQ / Heavy Iron Studios / Nintendo).

---

##  Environment & Toolchain

* **Target Game:** *SpongeBob SquarePants: Truth or Square* (Wii NTSC - `R8IE78`)
* **Host OS:** CachyOS (Arch Linux) x86_64
* **Shell Environment:** Fish shell (`fish 4.x`)
* **Core Toolchain:** [NWiiRecomp](https://www.google.com/search?q=https://github.com/NWiiRecomp&utm_source=gemini) (PowerPC-to-C++ Static Recompiler)
* **Compiler & Build System:** GCC 16, CMake 3.5+, C++20
* **Graphics/Audio Runtime:** SDL2 (PipeWire support disabled for native build compatibility)

---

##  Current Status & Pipeline Progress

```text
Overall Pipeline Progress: [██████████████████░░░░░░░] ~72%

```

| Component / Subsystem | Status | Details |
| --- | --- | --- |
| **Static Code Analysis** | `100%` | Analyzed and extracted **25,352 PowerPC functions** from `main.dol`. |
| **C++ Code Emission** | `100%` | Full C++ translation exported to `build/recompiled`. |
| **Compilation & Linking** | `100%` | Native binary links successfully using CMake + GCC 16. |
| **Runtime & HLE Stability** | `100%` | Applied `setjmp` fix in `cpu_thread_func` (resolved IRQ 27 SIGSEGV). |
| **IOS / ES / DVD Emulation** | `85%` | `IOS_Open`, ES (`Title ID`, `TicketView`), and `DVDLowInquiry` fully responsive. |
| **PPC Instruction Coverage** | `70%` | Core PPC instruction set implemented; active work on Gekko extensions. |
| **Paired-Single (`ps_*`) SIMD** | `10%` | **Current Bottleneck:** Implementing missing Opcode 4 sub-opcodes (`XO 6`). |

---

##  Technical Highlights & Engineering Notes

### 1. IRQ 27 & Runtime Exception Fix

During early execution, IRQ 27 dispatches caused a kernel segmentation fault (`SIGSEGV`). This was resolved by fixing context preservation with `setjmp` inside `cpu_thread_func` (`main.cpp`), allowing the runtime thread dispatcher to handle high-frequency interrupt requests smoothly.

### 2. High-Level Emulation (HLE) Subsystems

The static runtime accurately stubs and responds to fundamental Wii system calls:

* **ES (Executable Seamless):** Returns valid `Title ID` and parses `TicketView` blocks.
* **DVD Subsystem:** Responds properly to `DVDLowInquiry` commands with standard `RVL-DI` signatures.
* **Callback Dispatcher:** Correctly schedules and executes asynchronous event callbacks.

### 3. Active Focus: Gekko Paired-Single SIMD (`ps_*`)

The current roadblock occurs at PC address `0x80221818` (`0x805189b0` spin loop), triggering:

```text
UNIMPLEMENTED Opcode 4 (ps_*) XO 6 XO_10 6 at 0x80221818

```

The Gekko/Broadway processor uses **Opcode 4** for 64-bit paired-single floating-point operations. Work is underway in `nWiiRecomp/src/recompiler.cpp` to decode and implement the missing sub-opcode handlers into equivalent C++ vector operations.

---

##  Building & Running

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
