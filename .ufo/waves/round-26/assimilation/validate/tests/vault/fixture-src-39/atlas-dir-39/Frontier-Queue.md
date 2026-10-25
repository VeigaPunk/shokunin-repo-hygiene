# Frontier queue — what's provably next per lane

## kaidoku (from r4-16 rescan + r5 lanes)

- `.jsc` → source mapping (Ignition disasm held; View8/jsc2js-style mapper next)
- >90MB targets: raise `REA_GHIDRA_STARTUP_TIMEOUT_MS`≈3.6M + `GHIDRA_HEADLESS_MAXMEM=6-8G` (r5-07 measuring)
- sasquatch build (AUR) → unblob squashfs recursion (7z fallback works today)
- RISC-V: gate bypassed r5-05 — `REA_GHIDRA_LANGUAGE_ID` env override + direct `analyzeHeadless` on carved `.fwimage` EXECs
- `capture-electron-scenario` handshake diagnosis (lane in flight)
- adb on a live device/emulator (22/24 verbs device-gated)
- process-capture verbs, managed verify/project ops, native call-target resolution
- IDA / Hopper / JEB — operator-gated, absent

## fleet-level

- kaidoku roster promotion: SHONEN gates closed since r3, 5 rounds trained — pending operator decision
- lanes' halted axes: revenger calibration (operator ruling), lore checker repair (declared r86)
