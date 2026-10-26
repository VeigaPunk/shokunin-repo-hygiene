# SwarmScout11 — C2 false-positive map

## Status
STATUS: PASS — all 13 base LANE-FP pointers mapped to gate lines with quoted lane sources; minimal suppressing rules found and measured on scratch copies of the base gate; selftest and fixture impact listed. One open decision (G8 text form) flagged for the L1.

## Evidence
- `python3 -B census/round-31/c2-counter.py --root <lane> --rev 9f17a1ef...c871fc --base same --fleet-root /home/vgpnk/Projects/shokunin --scratch /fast/scratch/hyaku/souji-r31/SwarmScout11/cnt` -> `SUMMARY fp=13 real=2 cne=0 r26=466 fixture=fail redarm=fail regress=same` (13 LANE-FP: r19 x4, r20 x6, r24 x1, r28 x2; REAL: `census/round-3/garbage-census.out`, `tools/__pycache__/`).
- Per-line tokenisation: scratch probe importing the base gate (`git show <base>:tools/souji-landing-gate.py`) and printing `POINTER_PATH_RE` raw matches and `_pointer_paths` yields for each of the 11 source lines.
- Patched scratch copies (R1 ellipsis, R2 en dash, R3 `:text`+`.captured`, R4 `%d`, R5 extensionless whole-span `E1` / lexical `E0`): `--selftest` base 65/0, E1 65/0, E0 63/2; lane rounds 18-30 base vs E1 diff = exactly 13 LG-DANGLING-PTR removed, none added; fixtures r16/r18-landing-pointers/r19/r30 green under E0 and E1; synthetic G4-G9 repo: patched emits exactly the six G9 paths (E1 fails G8 only if the fixture backticks the bare tokens).
- Tools: no installs. Scratch: /fast/scratch/hyaku/souji-r31/SwarmScout11 (removed at end). Lane tree untouched.

## Findings
1. 13 FPs fall in 4 groups: ASCII `...` (2; gate filter at `tools/souji-landing-gate.py:853` tests only `…`), en-dash ranges (3; `_trim_pointer_token` regex line 822 is ASCII `-`), prose/quoted extensionless slash tokens (7: `tools/tests/census/corpus`, `corpus/authority`, `corpus/helper`, `corpus/source/QUALITY`, `tools/kill/killpg`, `corpus/census/tools`, `corpus/knowledge/registry`; no stage rejects them), `.gitignore:fixture/` (1; `:text` suffix at 822 and no `.captured` twin at 1002-1006). Full table with quotes: `.ufo/waves/round-31/w1/deliver-c2-fp-map.md`.
2. Zero-hit-at-base but needed for G7: `TEMPLATE_POINTER_RE` (line 156) lacks `%d`/`%02d`.
3. Extensionless prose rule must be whole-span-only (E1) or the selftest cases `quarantine-path-absent` (1596-1604) and `pointer-exemption-prefix` (1745-1755) fail (pass 65 -> 63, breaking C2's REGRESS equality and C1's `SELFTEST pass=65` binding). The skip must sit after the exemption check (1007-1009) or the lane exemption for `dot-git-empty-stub` turns stale.
4. Open decision: G8 wording "(no extension, no trailing slash, absent)" reads lexical; whole-span E1 passes G8 only for unbackticked tokens. If the fixture backticks them, use E0 and edit those two selftest inputs (keeps 65) — L1/fixture-author call.
5. G6/G9 text uses `round-N`; the gate skips `round-N` tokens (lines 149, 855), so the fixture must use a concrete N.
6. Adding G1-G10 to the gate selftest table would change `SELFTEST pass=65` (REGRESS leg); put them in a separate fixture file.

## Deliveries
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w1/deliver-c2-fp-map.md
