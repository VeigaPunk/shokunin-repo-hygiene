# SwarmReviewer10 — C1 re-derivation at 7b16731f, without the lane counter

## Status
STATUS: PASS — the attack ran to completion: 18 row commands plus R16's `cmd=` argv executed at the landing commit, 18 again at base, byte-level prefix and token checks, independent correction parsing. C1 re-derives to the frozen target with one non-fatal normalization finding. (PASS = my attack ran; it does not assert the lane's claim beyond what is evidenced below.)

## Evidence
Scratch clone /fast/scratch/hyaku/souji-r30/RerunC1AtLanding/c (origin removed, detached HEAD 7b16731fcd8ab9b95220b50603314aa8dc92b2ec, clean tree before and after every run). The lane counter was never executed; every verdict below comes from my own runs and my own parsing of committed bytes.

Re-derived SUMMARY equivalent at 7b16731f: k1=0 k2=0 mismatches=0 rows=18 pointers=10 — equals the frozen target in /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/preregistration.txt:5.

K1, per row (stated literals from census/round-30/c1-rows.tsv bytes; sha256-identical across prereg d4928ec, landing 7b16731f, tip 9dcd3676, and the lane worktree):
- Direct MATCH (stated literal at digit boundaries in the last digit-bearing stdout line, rc=0), under both v1 (substring) and A3 (boundary): R01 `selftest=PASS ids=6/6`, R02 `selftest: 36/36 passed`, R12 `selftest=8/8`, R13 `selftest=8/8`, R17 `cases=20 pass=20 control=FALSE-GREEN-REJECTED`.
- CORRECTED (13): R03 R04 R05 R06 R07 R08 R09 R10 R11 R14 R15 R16 R18. Every correction's `rc=0` and `observed=` text equals what my runs produced under both instruments' observation semantics (A3 stdout-first; v1 stdout+stderr concat). Example correction, verbatim from /home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:324: `R30-CORRECTION SCORECARD.md:154 R03 rc=0 observed=SUMMARY total=5 failed=0 hung=0`.
- R16's enumerated row command exits 2 (argparse requires `--tool`); its recorded `cmd=` argv extends the row argv (row argv is a prefix), adds no `-c`/`-h`/`--help`/`--version`, keeps the script path, and its run prints `cases=9 pass=9 control=FALSE-GREEN-REJECTED` with rc=0 — accepted under v1 (first-path-token identity) and A3 (prefix extension) alike.
- R18 duality: stdout ends `cases=15 pass=15 control=TAMPER-REJECTED` (A3 direct match); v1's concat observation is the usage banner the fixture provokes on stderr, which the recorded correction equals and v1 accepts (the v1 blob at d4928ec has no banner refusal). This is exactly what the appended note says: "under A3 the row matches on its stdout line and the banner is refused" (/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:338).

K2: SHONEN.md is byte-identical base↔7b167; all 10 pointer tokens resolve at 7b167 (LOG.md:362 has ≥362 lines). k2=0, pointers=10.

Append-only: SCORECARD.md at 7b167 begins byte-for-byte with base 9420341 (54403-byte prefix; 20 appended lines; the 13 correction lines sit at SCORECARD.md:324-336, and `R30-CORRECTION` occurs zero times in the base bytes). SHONEN.md identical.

Non-vacuous before: the same 18 commands at base 9420341 mismatch 13/18 under v1 semantics and 12/18 under A3 semantics (R18 matches on stdout under A3) — both nonzero, satisfying the kill rule that a base value of mismatches=0 would be a miss. This matches the appended prose "Of the 13 base mismatches" (/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:322), which is the v1 count.

Enumeration fidelity: all 18 stated literals appear in their base SCORECARD cells; all script paths appear (six tsv commands add the interpreter prefix, per the tsv header rule "A bare .py path is run with `python3`, a bare .sh path with `bash`" — /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c1-rows.tsv:3). Correction line numbers all equal their c1-rows.tsv line numbers; the 13 (line,row-id) keys are distinct, so there is no duplicate-correction cherry-pick surface.

## Findings
1. DEFECT-NOT-FATAL — recorded observations are whitespace-normalized, not raw bytes. Six corrections (R03 R05 R06 R07 R08 R11) record space-joined text where the raw stdout line uses tab separators (R03 stdout is `SUMMARY\ttotal=5\tfailed=0\thung=0`; the recorded text is `SUMMARY total=5 failed=0 hung=0`). Byte equality with the raw stdout line therefore fails; equality holds after the instruments' documented observation step, "whitespace runs collapsed to one space" (/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-agreement.py:14, same collapse in `summary_line` at :86-89 and in the v1 blob at d4928ec:76-81). The frozen acceptance rule is "rc and observed must equal what the counter observes" (/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/preregistration.txt:5), and the counter's observation IS the collapsed line, so the corrections are faithful and k1=0 stands. Token sequences and rc are faithful; only separator style differs.
2. Tool inconsistency (this seat's instrumentation, not the lane) — my first read of /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c1-rows.tsv rendered R03's stated as 6/6 and R15's as 9/9; the bytes are 5/5 and 8/8 (worktree == prereg == landing == tip blobs). A re-read renders 5/5 correctly. Filed to report_issue. No verdict impact: neither 6/6 nor 9/9 appears in either row's observed line, and both rows are accepted via corrections under either literal.
3. Residual env note [INFERENCE] — my runs used the ambient environment (TMPDIR pointed at my scratch) without the counter's `GIT_CONFIG_NOSYSTEM=1`; all 13 recorded observations reproduced exactly, so no environment sensitivity is observable for these tallies.
4. Scope note — the frozen target's second leg, "at the C1 landing commit and again at the final lane tip" (/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/preregistration.txt:5), is only half covered here: this item pins 7b16731f; the tip 9dcd3676 re-check is not attacked in this report.

## Attack log
- K1 rows R01-R18 at 7b167 (18 row commands + R16 `cmd=` argv; stdout/stderr/rc captured separately) → HOLDS: 5 direct match under v1 and A3; 13 accepted corrections with rc and observed equal to both instruments' observations; R16 via the in-rule `cmd=` extension; R18 via A3 stdout match and v1 banner correction.
- Correction observed-text equality vs the last digit-bearing stdout line → 7/13 byte-equal raw; 6/13 equal only after the documented whitespace-run collapse → DEFECT-NOT-FATAL (Finding 1); the prereg rule ("equal what the counter observes") is satisfied.
- Append-only SCORECARD.md base→7b167 byte prefix → HOLDS (startswith true; corrections only in the appended tail; none in base bytes).
- SHONEN.md append-only + 10 token resolutions at 7b167 → HOLDS (byte-identical file; 10/10 resolve, including LOG.md:362 depth).
- Base non-vacuity control (kill rule: base mismatches=0 is a miss) → HOLDS (13 v1 / 12 A3 mismatches at base, nonzero).
- Frozen enumeration stability (c1-rows.tsv unchanged prereg→landing→tip→worktree) → HOLDS (byte-identical, sha256 checked per revision).
- A3 stricter checks on the single `cmd=` correction (R16): argv extension, no `-c`/`-h`/`--help`/`--version`, script identity, banner refusal → HOLDS.
- v1-vs-A3 duality for R18 (stderr banner shadows the green tally in v1's concat) → HOLDS, matching the appended note and the literal-history delivery (census/round-30/waves/w1/deliver-c1-literal-history.tsv, R18 row: "the MISMATCH is a counter stderr-concatenation artifact").

## Deliveries
- Report: .ufo/waves/round-30/w2/SwarmReviewer10.md (this file; absolute path /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w2/SwarmReviewer10.md)
- Receipts: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w2/SwarmReviewer10-receipts.txt (per-row argv/rc/raw-last-digit-line/A3-S/v1-S, prefix byte counts and sha256s, SHONEN resolutions, base control, tsv hashes)
- Tool report filed: read render inconsistency on c1-rows.tsv (xd://report_issue)
- Scratch /fast/scratch/hyaku/souji-r30/RerunC1AtLanding/ removed after receipts were copied.
