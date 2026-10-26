# SwarmScout11 — gate root cause (C2 base failures)

## Status
STATUS: PASS — all assigned questions answered from bytes read this run; delivery written.

## Evidence
- Command (scratch /fast/scratch/hyaku/souji-r30/GateRootCause/, TMPDIR set there): `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b --round 29 --fleet-root /home/vgpnk/Projects/shokunin` → rc=2, `SUMMARY findings=3 checked_reg=58 … checked_reports=0`, 3 LG-DANGLING-PTR + `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-29/` (full output pasted in the delivery).
- `--selftest` on the committed tool: `SELFTEST pass=65 fail=0`.
- Revision: base 9420341d9a81; lane HEAD df6afe81 (gate file unchanged between them per `git diff --stat`).

## Findings
1. The 3 LG-DANGLING-PTR lines come from `check_pointers` souji-landing-gate.py:985-991 (def 905-992); existence test 957-958 is tree-only. COULD-NOT-EVALUATE from `check_carry` 469-474, caught in `evaluate` 1117-1132.
2. `census/round-` and `corpus/lessons/round-` are string-literal fragments in the Python one-liner in QUALITY.md:150 (Q60 check cell: `pre=g("census/round-"+rd+"/records/preregistration.txt");les=g("corpus/lessons/round-"+rd+".md")`). `POINTER_PATH_RE` (141-146) stops at `"`; the `_pointer_paths` filter (823-862) only skips `…`, `<>*`, `round-N`, unbalanced braces. Probed: `round-%s`, `round-{N}`, `round-$R` are also flagged; `round-<N>` is already skipped.
3. `.ufo/waves/round-29/` is cited at corpus/lessons/round-29-verifier-spotcheck.md:132 and is absent from the tree (round-29 is captured at `census/round-29/waves/w1/*.md`, 86 .md; `.ufo/waves/round-13..26` are tracked).
4. `checked_reg=58` is not the pointer set: it counts SKILL.md-cited scripts parsed (line 1046; 29 tests/fixtures + 15 tools + 14 census). Pointer scan (1012 tokens) reads SKILL.md, SHONEN.md, SCORECARD.md, PROVINCE.md, corpus/QUALITY.md, corpus/README.md, lessons round-N.md and round-N-verifier-spotcheck.md, 22 corpus/knowledge/*.md, and LOG.md round-N sections (916-948).
5. Other `.ufo/waves/round-N/` assumptions: only `check_carry` 469-474 functionally, plus `POINTER_ROOTS` 136-139, `POINTER_PATH_RE` 144, `.ufo/waves/hyaku/` fleet rule 967; docs/comments 13, 33, 114. No selftest fixture contains `census/round-N/waves/`; a fallback gated on "no .ufo reports AND capture present" changes no selftest case [INFERENCE, patched gate not run]. Cases to keep intact: `pointer-without-wave-reports` (1396-1407) and `no-wave-dir-exit2` (2174-2178) need the `no .md reports under` message; the `hyaku` fleet cases (1612-1658) need the fleet rule left alone.

## Deliveries
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/deliver-gate-root-cause.md

Scratch dir /fast/scratch/hyaku/souji-r30/GateRootCause/ removed at finish. No tools installed.
