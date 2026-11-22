# Contributing to Ocean Squirrel

Thanks for helping! This project recompiles a commercial Wii game, so a few rules matter more than usual.

## Ground rules

1. **Never commit game data.** That includes disc images (ISO, WBFS, RVZ, …), `main.dol`, extracted `sys/` and `files/`, frame dumps and the generated `output.cpp`. They are git-ignored; keep it that way.
2. **Never copy code from incompatible licenses.** Emulators such as Dolphin (GPL) are fine as a *behavioral reference*, but do not paste or adapt their source.
3. **Keep the recompiler game-neutral.** Addresses and behavior specific to SpongeBob belong in the game's TOML (`[hle_hooks]`) or game-specific runtime code, not in the generic recompiler.

## Recompiler changes

Changes to the recompiler affect all of `output.cpp` and force a full regeneration and rebuild (about 46 minutes). **Open an issue or draft PR describing the change before implementing it**, with:

- the instruction pattern or analysis gap,
- the generated C++ before and after,
- how you verified it (a game run, a log, a comparison with a reference).

General-purpose fixes should also be offered upstream to [NWiiRecomp](https://github.com/BlackLineInteractive/NWiiRecomp).

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/) with a scope:

```
fix(ios): complete oh1 Bluetooth IOCTLV requests
feat(vi): register the retrace handler from VIInit
docs: document the frame counter at +0x6C08
```

Common scopes: `recomp`, `runtime`, `ios`, `ipc`, `vi`, `gx`, `di`, `audio`, `input`, `debug`.

Explain the *why* in the body: which address, what the game expected, what you observed.

## Reverse-engineering notes

When you identify a function or structure, write down the guest address and what it does, and add it to the README's engineering notes. Named, understood code is what will make enhancements and co-op possible.

## Reporting bugs

Use the issue templates. Include the commit, your distro and GPU, the environment variables you used and the relevant log. A run with `NWII_SAMPLE=1` is the most useful log for hangs.
