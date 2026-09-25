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
