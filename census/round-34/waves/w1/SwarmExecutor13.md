# SwarmExecutor13 — r34 w1: independent C1 do-nothing control

## Status
STATUS: PASS — the frozen do-nothing claim reproduces exactly: `SUMMARY items=60 agree=35 mismatches=25 restated=0 rev=9c76c72…`, rc 1, and every one of the 60 ITEM verdicts is identical to the L1's committed reading; all 25 mismatching ids checked against base SCORECARD.md for prior correction rows (Q76).

## Evidence

Item: re-run the C1 do-nothing control (base `9c76c7222a8abff027af42e37f0d160d52526bba`, frozen list `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`) and confirm the L1's committed reading.

```
flock /fast/scratch/hyaku/souji-r34/RunC1DoNothing//c1.lock \
  python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
    --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
    --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
    --scratch /fast/scratch/hyaku/souji-r34/RunC1DoNothing/cnt
```

- counter bytes: `sha256sum census/round-34/c1-counter.py` = `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`, equal to `git show 2b0171e2:census/round-34/c1-counter.py | sha256sum` (the run used the freeze bytes).
- `git show 2b59192…:census/round-34/c1-items.tsv` vs `2b0171e2…` and the counter blob: `git diff --stat 2b591924f607940febbb99f922cc9bb090508eb6 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 -- census/round-34/c1-items.tsv census/round-34/c1-counter.py` printed nothing, so the attempt-1 and A6 list revisions carry identical items and counter bytes.
- load before: `6.21 3.97 2.47 8/4906 4022075`; load after: `32.34 38.59 28.41 18/8381 646277` (32 CPUs); wall 1126.38 s; per-item loads recorded by the counter, max `44.14` at E28.
- SUMMARY: `SUMMARY items=60 agree=35 mismatches=25 restated=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba`, `rc=1`.
- verdict diff vs `census/round-34/records/controls-c1-do-nothing.txt` (id, verdict, status columns): `diff` empty → `VERDICTS-IDENTICAL`. Raw output at `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt`.
- Q76 sweep inputs at base: `git show 9c76c72…:SCORECARD.md` (525 lines) and `git show 9c76c72…:SKILL.md`; pointers searched with `grep -cE "SCORECARD\.md:<n>([^0-9]|$)"` and `grep -oE 'SKILL\.md:[0-9]+'` (0 matches in either file for every G item).

## Findings

1. **The control reproduces byte-for-byte in verdicts.** 60 items, 35 AGREE / 25 MISMATCH, rc 1, same 25 ids as the committed reading (`census/round-34/records/controls-c1-do-nothing.txt`). A round that changes nothing cannot reach `mismatches=0`; the claim is reachable only by appended restatements.
2. **Mismatch ids (25):** G05 G11 G17a G17b G21 G23 G24 E04 E05 E07 E08b E09a E14a E14b E15c E18 E23a E23b E24 E25 E26 E27 E29 E31 E32.
3. **Q76: exactly one mismatch cell already carries a same-cell correction row.** E05 (`SCORECARD.md:23`) is bound by three `R29-CORRECTION` rows at base `SCORECARD.md:295-297`; line 297 names the fixture line `cases=6 pass=6 control=TAMPER-REJECTED` but restates neither the row's argv nor its exit, so the bare-argv Usage mismatch stands. For the other 24 cells `grep -nE "SCORECARD\.md:<line>([^0-9]|$)"` returns 0 hits, and no `SKILL.md:<line>` pointer exists anywhere in SKILL.md or SCORECARD.md at base.
4. **Three same-argv corrections exist for different cells (Q76 near-misses, not same-cell):** G21 ↔ L36 (`SCORECARD.md:401`, cell :313, `cases=20 pass=20`); E18 ↔ L05 (`:371`, cell :155, `ids=7/7` for the identical argv); E05 ↔ `R30-CORRECTION SCORECARD.md:314 R18` (`:336`), which already records the same `Usage: bash tools/souji-wave-evidence-capture.sh …` line. A r34 restatement must cite the item's own cell, not these.
5. **Mismatch classes by observed last digit-bearing line:** value drift — G11 (`total=45 pass=45` vs 36/36), G23/E23a (`manifests=8 uncovered=1` vs 7/0), E08b (`0` vs 4), E18 (`ids=7/7` vs 5/5), E24 (`fail=1`), E26 (`dangling=0 other=0`), E27 (`fail=2 f1_entries=5`), E29 (`fail=4 f1_entries=5`); exit-only (predicate holds, rc differs) — E23b, E31; missing/unresolvable pinned revision — G24 (`tools/souji-capability-agreement.py` absent at its `at` 9420341), E14a, E15c (`a65fac…` unresolvable); predicate/notation binding — E14b (sha256sum's trailing ` -`), E25 (tool now prints a later `KINDS … (diagnostic; …)` line), E09a (git wording differs from `path .* does not exist`); fixture/environment — G05 (pin lives in the written JSON only), G17a, G17b, G21 (hardcoded `/var/tmp/souji-r29-c1-fixture`), E04, E07, E05.
6. **E32 is load-sensitive (Q77).** My run's last line was `SUMMARY items=27 pass=25 fail=2` (per-item load 32.35) where the committed low-load reading had `pass=26 fail=1`; the verdict is MISMATCH either way, but the row's restated statement must quote the exact line of the run that is bound, so any E32 restatement needs its recorded load beside it.
7. **Instrument detail inconsistency (no target impact).** The committed record's E32 ITEM line reads `predicate fails last=SUMMARY items=27 pass=26 fail=1`, but replaying the frozen predicate against that exact line returns `(True, 'predicate holds')` (`frozen_pred("SUMMARY items=27 pass=26 fail=1", [line], …)` via importlib). The MISMATCH verdict is still correct because rc=1 ≠ stated exit 0; only the printed "why" is inconsistent. Reproduction is in the Evidence command block's counter bytes.
8. **Load did not move the claim.** Verdicts are identical to the committed run despite the 1-min load rising from 6.21 to 32.34 (max per-item 44.14); the do-nothing property (mismatches>0) holds a fortiori.

### Mismatch table (Q76 checked)

| id | cell (base) | stated (exit; outcome) | observed (rc; last digit-bearing line) | prior correction row |
|---|---|---|---|---|
| G05 | SKILL.md:219 | 0; 5 pinned replay rows | 0; `gate-replays: wrote record to …/g5.json` | none |
| G11 | SKILL.md:234 | 0; total=36 pass=36 | 0; `SUMMARY total=45 pass=45 fail=0 blocked=0 inventory=exact baseline_mismatches=not-requested` | none |
| G17a | SKILL.md:241 | 0; total=1 pass=1 | 1; `SUMMARY total=1 pass=0 fail=1` | none |
| G17b | SKILL.md:235 | 0; 3× SCENARIO exit=0 matched=18/18 | 1; `Note: switching to '9c76c72…'` | none |
| G21 | SKILL.md:245 | 0; cases=20 pass=20 | 1; `FAIL rev-not-40-hex … /var/tmp/souji-r29-c1-fixture/…: No such file` | L36 for cell :313 only |
| G23 | SKILL.md:247 | 0; manifests=7 failed=0 uncovered=0 | 1; `SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0` | none |
| G24 | SKILL.md:249 | 0; k1=12 k2=0 mismatches=12 | 2; `can't open file '…/tools/souji-capability-agreement.py'` | none |
| E04 | SCORECARD.md:21 | 2; findings=0 checked_reg=52 | 1; `SUMMARY findings=19 checked_reg=52 …` | none |
| E05 | SCORECARD.md:23 | 0; cases=6 pass=6 | 0; `Usage: bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> …` | R29-CORRECTION :295-297 (line 297 names the fixture only) |
| E07 | SCORECARD.md:31 | 2; SUMMARY findings=2 | 2; `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-27/ …` | none |
| E08b | SCORECARD.md:32 | 0; `^4$` | 0; `0` | none |
| E09a | SCORECARD.md:33 | 128; `path .* does not exist` | 128; `fatal: path 'tools/souji-pre-report-gate.sh' exists on disk, but not in 'e78ac7c…'` | none |
| E14a | SCORECARD.md:67 | 128; `path .* does not exist` | 128; `fatal: invalid object name 'a65fac…'` | none |
| E14b | SCORECARD.md:67 | 0; `^09bb8e0d…ed6d$` | 0; `09bb8e0d…ed6d -` | none |
| E15c | SCORECARD.md:68 | 0; 2 `+ground:` / 0 `-ground:` | 128; `fatal: bad revision 'a65fac…'` | none |
| E18 | SCORECARD.md:71 | 0; selftest=PASS ids=5/5 | 0; `selftest=PASS ids=7/7` | L05 for cell :155 only |
| E23a | SCORECARD.md:304 | 0; manifests=3 failed=0 uncovered=0 | 1; `SUMMARY manifests=8 failed=0 uncovered=1 floor_violations=0` | none |
| E23b | SCORECARD.md:304 | 0; lost=0 fidelity=0 tool_unchanged=0 | 1; predicate holds | none |
| E24 | SCORECARD.md:305 | 0; legs=9 fail=0 | 1; `SUMMARY legs=9 fail=1` | none |
| E25 | SCORECARD.md:344 | 0; k1=0 k2=0 mismatches=0 rows=18 pointers=10 | 0; `KINDS value=0 shape=0 rc=0 (diagnostic; not part of the target)` | none |
| E26 | SCORECARD.md:345 | 0; dangling=1 other=7 | 0; `SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same` | none |
| E27 | SCORECARD.md:346 | 0; legs=9 fail=0 f1_entries=3 | 1; `SUMMARY legs=9 fail=2 f1_entries=5` | none |
| E29 | SCORECARD.md:414 | 0; legs=11 fail=0 f1_entries=4 | 1; `SUMMARY legs=11 fail=4 f1_entries=5` | none |
| E31 | SCORECARD.md:477 | 0; items=44 … mismatches=6 | 1; predicate holds | none |
| E32 | SCORECARD.md:478 | 0; items=27 pass=26 fail=1 | 1; `SUMMARY items=27 pass=25 fail=2` | none |

## Attack log

Not an attack seat. No frozen predicate, target, counter, item or leg is disputed here; finding 7 is an inconsistency in the L1's *record text* at E32 (verdict unaffected), and finding 6 is a load sensitivity the lane must record when it restates E32. No frozen bytes were modified; nothing committed.

## Deliveries

- `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt` — provenance header plus the raw wrapper output (date, `/proc/loadavg` before, 60 ITEM lines, SUMMARY, rc, date, `/proc/loadavg` after), byte-identical raw block verified.
- `.ufo/waves/round-34/w1/SwarmExecutor13.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r34/RunC1DoNothing/` was removed after the receipts above were written. No tools installed or upgraded; no git/jj mutation; nothing outside the lane was touched.
