# R92ExecC1Cause — C1 kill attribution (the LD4r sole-killer check)

Seat: R92ExecC1Cause. Method: for each sampled target, apply `old`→`new` once to a
copy of `census/round-87/c1-pointer-counter.py`, run the pinned r92 harness
(`census/round-92/c1-false-row-harness.py --population census/round-92/c1-false-rows.tsv`,
64 rows) in a fresh `--work` dir (deleted after scoring; ≤2 trees at once — ran
serially), and record every `ROW ... match=no`. ITEM-line diffs come from direct
counter runs on the r77 base (`census/round-77/c2-population.tsv` +
`census/round-77/c2-pointer-ledger.tsv` at rev e65538e73), the same base run
LD4r asserts. Scripts and full outputs: `R92ExecC1Cause/attribute.py`,
`R92ExecC1Cause/attribute.log`, `R92ExecC1Cause/results.json` (seat dir).
Each harness run rebuilt its own fixture; one work tree per mutant.

Population note: the harness ROW field order is `rc=... match=...`; during
parsing the stored fields were initially swapped (rc↔match). The table below
corrects this from `results.json` (true failing = stored `rc` field ≠ `yes`);
every mutant had exactly one corrected failing row.

## Verdict up front

**LD4r is the SOLE failing row for every sampled target (14/14): each mutant
score-failed exactly one of 64 rows, and that row is `LD4r` — `rc=1 match=no`,
all other 63 rows `match=yes`.** Each of the 14 also had harness exit 1
(`SUMMARY rows=64 mismatches=1 accepted=0 refused_true=0 errors=0`), i.e. only
the harness-level exit code was non-zero among the LD4r assertions for the
exit-polarity class; for the resolution class the LD4r base ITEM run itself
left the all-resolved shape. No sampled mutant failed any row OTHER than LD4r
on the r92 population, so none of the 14 would have failed any row on the r91
63-row population either (LD4r is the deltas; the other 63 rows are shared
byte-for-byte) — consistent with the filed control `killed=0 survived=47`.
Sample = 14 targets spread across counter lines 214–574, including all 7
required (a552c28, a574c11, h-exit-always-1, a214c12, a323c41, a468c44, a541c27).

## Table

Legend. "Class" per the assignment: `exit-polarity` = the mutant breaks only
the success return/test/tally (all rung ITEMs still resolve; LD4r kills via
rc=1); `resolution` = the mutant makes distinct r77 items REFUSED/MISMATCH in
the LD4r base run (so the run is not all-resolved; LD4r kills via the
all-resolved assertion as well as rc). LD4r storage: `match` field holds the
counter rc, `rc` field holds match=yes/no — the "failing" column shows the
correct LD4r line. Pristine r77 base: `SUMMARY items=35 resolved=35 ... rc=0`,
P04 `status=MOVED`.

| target | line | failing rows (corrected) | changed r77 ITEM lines (base run, pristine → mutant) | class |
|---|---|---|---|---|
| a214c12-==-to-!= | 214 | LD4r rc=1 match=no (only) | P11 CAPTURED→MISMATCH (digest differs); P18 CAPTURED→MISMATCH; P31 MOVED→REFUSED (target absent at rev) | resolution |
| a287c38-==-to-!= | 287 | LD4r rc=1 match=no (only) | P19 TOKEN→REFUSED (range member not regular file); P27 TOKEN→REFUSED (same) | resolution |
| a294c33-not-to-drop | 294 | LD4r rc=1 match=no (only) | P06,P19,P21,P22,P23,P27 TOKEN→REFUSED (no target) | resolution |
| a323c41-==-to-!= | 323 | LD4r rc=1 match=no (only) | P19 TOKEN→REFUSED (range endpoints carry no digits); P27 TOKEN→REFUSED (same) | resolution |
| a344c15-!=-to-== | 344 | LD4r rc=1 match=no (only) | P19 TOKEN→REFUSED (targets not exactly the range expansion, 5/5); P27 TOKEN→REFUSED (same) | resolution |
| a396c41-==-to-!= | 396 | LD4r rc=1 match=no (only) | P09,P10,P11,P18 CAPTURED→MISMATCH (digest differs) | resolution |
| a468c44-not-to-drop | 468 | LD4r rc=1 match=no (only) | P01,P08,P12,P13,P17,P20,P32,P33 FLEET→REFUSED (not under fleet root) | resolution |
| a539c13-0-to-1 | 539 | LD4r rc=1 match=no (only) | none (base run: `SUMMARY resolved=35 refused=31` — counts-only distortion via `unknown`) | exit-polarity* |
| a541c27-0-to-1 | 541 | LD4r rc=1 match=no (only) | none (base run: `SUMMARY resolved=36` — tally pre-seeded +1) | exit-polarity |
| a545c43-1-to-0 | 545 | LD4r rc=1 match=no (only) | none (base run: `SUMMARY resolved=0` — resolved tally no-ops) | exit-polarity |
| a552c28-==-to-!= | 552 | LD4r rc=1 match=no (only) | none (base run: `SUMMARY resolved=35 ... rc=1` — `ok` test inverted, ITEMs all-resolved) | exit-polarity |
| a574c11-0-to-1 | 574 | LD4r rc=1 match=no (only) | none (base run all-resolved, `rc=1` — `return 1 if ok else 1`) | exit-polarity |
| h-exit-always-1 | 574 | LD4r rc=1 match=no (only) | none (base run all-resolved, `rc=1` — `return 1`) | exit-polarity |
| a239c28-1-to-0 | 239 | LD4r rc=1 match=no (only) | P22 TOKEN→REFUSED (target continuation not in source); P23 TOKEN→REFUSED (same) | resolution |

* a539c13 (`ids = {r[1] for r in pop}`) breaks the *tally/unknown* bookkeeping,
not the judge: every ITEM still resolves, but `unknown` is non-empty
(`SUMMARY refused=31`), so the run is not counted all-resolved and exits 1.
It is tally-class, not a judge-resolution mutant — classified exit-polarity
(tally/ok shape), not resolution; the kill still comes from the LD4r
expect_rc=0 assertion.

### Why the resolution class still dies on LD4r alone (and what "the stated
reason" is)

The claim sentence under test: "no r91 row asserts the counter's exit code 0
on a successful run" (CLAIM) — and STATED LIMIT (iii): "LD4r binds by exit
code: a kill may come from any r77 item turning unresolved, not only P04; the
row asserts that the whole r77 run succeeds."

Each sampled resolution mutant breaks a **different** r77 item (never only
P04): a214c12 breaks P11/P18/P31, a287c38 breaks P19/P27, a294c33 breaks
P06/P19/P21/P22/P23/P27, a323c41 breaks P19/P27, a344c15 breaks P19/P27,
a396c41 breaks P09/P10/P11/P18, a468c44 breaks eight FLEET items, a239c28
breaks P22/P23. On the r92 population those ITEM breaks show up in **no**
FORGE row of the harness and **no** LEDGER row — only LD4r, whose base run
rewalks all 35 r77 items and asserts `expect=MOVED / expect_rc=0` (row text:
"with the frozen 4-column r77 ledger the base run is all-resolved (35/35) and
the pristine counter exits 0"). That is why the control (r91 population, no
LD4r) is exactly `killed=0 survived=47`: the 63 shared rows never include an
all-resolved-r77-run assertion, so a mutant that leaves every forge/ledger row
green but de-resolves some r77 items survives them.

Two precise points for the invitation in (iii):

1. "Turning unresolved" in (iii) is the umbrella: the measured ITEM verbs are
   REFUSED (range/token/fleet guards) and MISMATCH (digest comparisons), not
   the literal status `UNRESOLVED`. `SUMMARY unresolved=0` in every mutant
   base run above. The LD4r assertion catches any of those equally, because
   it requires `resolved == 35`.
2. For the resolution class, LD4r kills on **both** halves of its assertion:
   the base run is not all-resolved *and* the counter exits 1 (`rc=1` in the
   LD4r line). The exit-polarity class (6/14) kills on the rc half alone
   (base ITEMs `resolved=35`, `rc=1`). The CLAIM sentence ("no r91 row asserts
   exit code 0") is therefore true but incomplete as the stated reason: only
   6 of the 14 sampled kills are pure exit-polarity; the other 8 kill because
   LD4r is also the only 64-row-population row that re-certifies the whole
   r77 base run. STATED LIMIT (iii) already says exactly that and is the
   accurate reason; the CLAIM sentence alone would predict kills only for the
   pure-polarity subset.

The falsification invitation for the r91 population is closed by the
results: for every sampled target the single non-matching harness row is
LD4r (present only in r92), so the r91 control (`killed=0`) is forced, not
assumed. Full per-row dumps for all 64 rows × 14 mutants: `results.json`
`rows` arrays.

## Checking what I did not do (and why)

- I did not run the full 47-target search (the waiver binds: ≤2 work trees,
  delete each after scoring; the search itself would re-run the harness 47
  times at ~15 s + ~0.7 GB clone each — the seat spec asked for "at least 12",
  sampled 14, and the pass recipe is in `attribute.py` for the L1 to extend).
- I did not re-derive the r91 124/260 survivor counts (out of seat scope;
  `records/c1-search-r91-full.txt` is the filed receipt).
- Scratch (`mutants/`, `hwork/`, `attribute.*`) is cleaned after copying
  receipts (silent receipt copy below); the mutant sources are byte-exact
  `old→new` single substitutions, reproducible from `c1-targets.json` + the
  builder in `attribute.py`.

## Falsification verdict

- `FALSIFIES-NUMBER`: **none**. No sampled target failed a row other than
  LD4r on the r92 population; the r91 `killed=0 survived=47` control is
  exactly what these per-target results entail.
- `FALSIFIES-WORDING`: **none against the CLAIM as written** — the sentence
  "no r91 row asserts the counter's exit code 0 on a successful run" is
  accurate for the 63 shared rows (every shared row either expects REFUSED/
  ERROR/LEDGER-REFUSED verdicts or the LD4 `ledger-resolve` verdict without
  an rc assertion). But as the invitation in (iii) anticipates, it is not the
  *whole* reason for the 47 kills: 8 of 14 sampled kills are judge-resolution
  mutants (r77 items → REFUSED/MISMATCH) that die on LD4r's all-resolved half
  of the assertion, not on pure exit polarity. The prereg already states
  this in LIMIT (iii) ("a kill may come from any r77 item turning
  unresolved ... the row asserts that the whole r77 run succeeds"), so the
  claim as a whole is not falsified — the CLAIM sentence alone would be
  misleading if read as the sole mechanism.
- `FALSIFIES-*`: `NO-FALSIFICATION` — with the mechanism refinement above
  (partly disclosed in (iii), but worth amending: "unresolved" should read
  "REFUSED/MISMATCH", since literal `UNRESOLVED` never appears).

Refs: receipts `R92ExecC1Cause/results.json` (per-row + ITEM diffs),
`R92ExecC1Cause/attribute.py` (one-substitution builder + harness runner +
field-swap correction documented in `attribute.log` header bytes),
`R92ExecC1Cause/attribute.log` (14 SUMMARY lines). Pins: counter
`fd0a8e24...`, harness `818f84d9...`, r92 population `f66341fc...` (64 rows),
targets `5a8f6087...` (47). Lane base `5339b2ac...`; fleet root
`/home/vgpnk/Projects/shokunin`. Scratch is deleted at yield (receipts copied
into the seat dir first, text/JSON only — no clones).
