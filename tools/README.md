# Debugging tools

Small Python 3 scripts used to chase the boot blockers. None of them contain game data; each one reads files from your own copy.

| Script | Use |
|---|---|
| `sym.py` | Name guest PCs or return addresses with the [ToS-Decomp-Wii](https://github.com/spongeis5/ToS-Decomp-Wii) symbol map: `python sym.py config/R8IE78/symbols.txt 801e43f8 80446d40` → `Function+0xOFF` |
| `dol2asm.py` | Split `main.dol` into per-section binaries/ELFs (writes `sections.txt`): `python dol2asm.py main.dol outdir/`, then `llvm-objdump -d --triple=powerpc --adjust-vma=0x<section addr> outdir/sN.elf` |
| `gxdecode.py` | Decode a GX FIFO dump made with `NWII_GXDUMP=<file>`. It tracks VCD/VAT so it can skip vertex data, and prints an opcode histogram, the first primitives and the first decode error |
