# SwarmCritic22 — K24 falsification (C1 item, SCORECARD.md:424)

## Status
STATUS: PASS — all four attack legs executed at the measured revision; verdict **LAX-PREDICATE** (scoped: faithful to the evidence cell's narrow outcome, reproduced lax against the row's measurement claim).

## Evidence

Measured revision `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`; base `6017a482e7068d5afb7617640198fbb0fe743357`. Scratch clone `/fast/scratch/hyaku/souji-r33/AuditK24/c` (`git rev-parse --show-toplevel` printed the clone; origin removed at once). Toolchain: `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`, `git version 2.56.0`.

Cell under audit (SCORECARD.md:424, read at base, 952 bytes, one line):
> `| jj dropped-keep-ref object-clock fixture (r31) | a real jj 0.45.1 + git 2.56.0 fixture measuring what keeps an abandoned commit's object present … ; the record's 17 `RESULT` lines replay identically, a PATH shim logs 26 jj and 111 git calls … and neutering either remover changes the outcome | `TMPDIR=<scratch> bash tests/fixtures/r31-jj-object-clock.sh` -> `jj-version: jj 0.45.1-…`, `git-version: git version 2.56.0`, 17 … lines byte-identical to `census/round-31/records/jj-object-clock-run.txt`; counter readings v1 `legs=11 fail=10` -> `legs=11 fail=0` …, v2 …, v3 … | r31 |`

Frozen item (`census/round-33/c1-items.tsv:38`): exit `0`, predicate `RESULTS:census/round-31/records/jj-object-clock-run.txt:17 && jj-version: jj 0\.45\.1 && git-version: git version 2\.56\.0`, argv `TMPDIR={SCRATCH} bash tests/fixtures/r31-jj-object-clock.sh`.

1) Determinism (fixture run twice with fresh TMPDIR, once with TMPDIR unset):
```
run1 rc=0   run2 rc=0   run3(no TMPDIR) rc=2
19 /…/run1.out   19 /…/run2.out   0 /…/run3.out
diff run1.out run2.out                       -> IDENTICAL
diff run1.out <record at 2d9bca5>            -> RECORD-IDENTICAL
run3.err: ERROR: TMPDIR is unset or empty; refusing to run
run1.out:1  jj-version: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5
run1.out:2  git-version: git version 2.56.0
run1.out:19 RESULT arm=reflog-only step=reflog-expire-then-prune keep_refs=6 target_keep=no reflog_hits=0 object_present=no
```
Record at 2d9bca5 holds 17 `RESULT ` lines (line 17 = `RESULT arm=reflog-only step=drop-keep-refs-naming-target keep_refs=6 target_keep=no reflog_hits=1 object_present=yes`). Item files unchanged base→list-rev: `git diff --stat 6017a48 2d9bca5 -- tests/fixtures/r31-jj-object-clock.sh census/round-31/records/jj-object-clock-run.txt` empty.

2) Out-of-set residuals re-derived (not in the frozen predicate, all current at 2d9bca5):
```
PATH-shim run: rc=0  jj_calls=26 git_calls=111  RESULT-LINES-EQUAL
markers: abandon=7 util_gc=5 reflog_expire=3 ' gc '=18 cat-file_-e=17
mutant M1 (reflog expire neutered): rc=0 results=17 object_present_no=0 vs_record=differ
mutant M2 (gc/prune neutered):       rc=0 results=17 object_present_no=0 vs_record=differ
record object_present=no count: 4
```
Cell's counter-reading pointers resolve: `census/round-31/records/c3-after-c3-counter.txt` `legs=11 fail=0`; `…-v2.txt` `legs=12 fail=0`; `…-v3.txt` `legs=13 fail=0`; before-readings `fail=10`/`fail=11` are `census/round-31/records/controls.tsv:4-5` (`C3-do-nothing(base) c3` / `c3v2`).

3) Counter, verbatim:
```
$ python3 -B census/round-33/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
    --scratch /fast/scratch/hyaku/souji-r33/AuditK24/cnt --only K24
ITEM	K24	AGREE	original	rc=0 expect_exit=0 predicate holds (RESULT lines 17/17 equal) last=RESULT arm=reflog-only step=reflog-expire-then-prune keep_refs=6 target_keep=no reflog_hits=0 object_present=no
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
counter rc=0
```

4) Counterexample (scratch clone only; lane untouched): replaced the fixture with `cat census/round-31/records/jj-object-clock-run.txt; exit 0` (no jj, no git, no measurement), committed as scratch rev `f0fa1fcc39d79e834611020543b22e059ad678bb`, re-ran the same counter:
```
ITEM	K24	AGREE	original	rc=0 expect_exit=0 predicate holds (RESULT lines 17/17 equal) …
SUMMARY items=1 agree=1 mismatches=0 restated=0 partial=1 rev=f0fa1fcc39d79e834611020543b22e059ad678bb
```

## Findings

1. **K24 AGREE at base is reproducible and deterministic.** Two fresh-TMPDIR runs are byte-identical to each other and to `census/round-31/records/jj-object-clock-run.txt`; rc=0 both. TMPDIR unset exits 2 with the fixture's own refusal, which is the frozen argv's `{SCRATCH}` contract, not nondeterminism. (Location: `tests/fixtures/r31-jj-object-clock.sh:60-83`, `census/round-33/c1-items.tsv:38`.)
2. **The frozen predicate is lax against the row's capability claim (reproduced).** A fixture that only cats the record — the exact fake r31's L12 leg was built to reject (`census/round-31/c3-counter-v3.py` header, L12: "a fixture that prints or copies a record without running jj and git fails") — still prints `AGREE` for K24. The predicate covers versions + `RESULT` byte-equality only; the row's measurement sentence ("a real jj 0.45.1 + git 2.56.0 fixture measuring …"), the shim counts and the neutering outcome sit in the row's *second* column, and the enumeration rule reads outcomes from the *evidence* cell (`census/round-33/c1-items.tsv:1-9`). So K24's AGREE certifies byte-equality, not that the fixture measures anything. (Location: `SCORECARD.md:424`; `census/round-33/c1-items.tsv:3-9`; counter `results_pred` at `census/round-33/c1-counter.py:117-131`.)
3. **No out-of-set residual is stale.** Re-derived at 2d9bca5: shim logs 26 jj / 111 git calls (r31 record `c3-after-c3-counter-v3.txt:13` states the same at 1baf4da0), both remover mutants change the outcome with `object_present=no` falling 4→0, and every counter-reading pointer in the cell resolves to a committed record with the stated numbers. (Location: `census/round-31/records/c3-after-c3-counter.txt`, `…-v2.txt`, `…-v3.txt`, `census/round-31/records/controls.tsv:4-5`.)
4. **Minor strict element: exit `0` is not stated by the row.** `c1-items.tsv` header reserves `*` for "the row states none and the tool's exit is not a pass claim"; :424 states no exit code, yet K24 requires 0. Non-material here (the run exits 0), but it is stricter than the row's stated outcome. (Location: `census/round-33/c1-items.tsv:10-12` vs `:38`.)

## Attack log

- Counterexample: cat-only fixture (`cat census/round-31/records/jj-object-clock-run.txt; exit 0`) at scratch rev `f0fa1fcc39d79e834611020543b22e059ad678bb` → counter prints `ITEM K24 AGREE`, `mismatches=0`.
- Evidence: runs above (determinism, shim 26/111, both mutants, record pointers, counter verbatim).
- Impacted axes: calibration only (C1 item K24, `SCORECARD.md:424`). No target, item, leg or counter changed; no lane file written outside this report.
- Verdict: **LAX-PREDICATE** — faithful to the evidence cell's literal outcome (versions + byte-identical `RESULT` lines), lax against the row's own measurement/anti-fake claim, which the frozen item cannot see.
- Smallest safe correction: none required for K24's AGREE as the frozen item defines it (byte-equality holds at base, and the row's out-of-set guards also hold). If the L1 wants the measurement claim in scope, that is a stricter-only amendment and the L1's alone; the preregistration's Amendments clause bars a rule change after a seat has scored, so the correct action here is to record the boundary in the round lesson, not to re-score K24.

## Deliveries

- `.ufo/waves/round-33/w1/SwarmCritic22.md` (this report).
- Scratch `/fast/scratch/hyaku/souji-r33/AuditK24` removed after the receipts above were copied here. No tool installs. Lane repo unmodified (`git status` untouched; only read-only `git log/show/diff/rev-parse/cat-file` used).
