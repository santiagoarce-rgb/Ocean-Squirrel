# PSP Memory Map & Relocation Notes

> [!NOTE]
> Archived. These notes are from the earlier PSP-version study and do not apply to the current Wii recompilation.

## Base Configuration
- **Executable Format:** PSP `EBOOT.BIN` / `EBOOT.ELF`
- **Default Load Address:** `0x00000000` (requires relocation)
- **Rebased Image Address:** `0x08804000` (or `0x08800000`)

## PSP RAM Layout (Standard User Space)
- `0x08800000 - 0x08803FFF`: Reserved / Kernel / PSP SDK Header
- `0x08804000 - ...`: `.text` section (game code)
- Global variables and BSS mapped within standard user RAM range (`0x08800000 - 0x0A000000`).
