# R99Reviewer1 — C1 correctness review: `census/round-99/declared-shapes.py`

Seat owns only `.ufo/waves/round-99/w1/R99Reviewer1.md` and
`.ufo/waves/round-99/w1/R99Reviewer1/`. Scratch: `/fast/scratch/hyaku/souji-r99/R99Reviewer1/`
(deleted before yield; reproducers are mirrored under `R99Reviewer1/cases/`).
Baseline: lane base `c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b` (= HEAD, read-only git).
The candidate under review is the executor's new `census/round-99/declared-shapes.py`
(sha256 `7f6a0816c34eec167016253b7f3d82fedf14aa408c5fab98cc60f3e5d0711816`)
and `census/round-99/shapes.tsv` (sha256 `8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14`).
The r99 hook is a byte copy of the r98 hook (sha256
`e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1` both).

## Scope and method

Target (from seat spec): every way the runner's mismatched count can reach 0 without the
hook's behaviour being correct — a relabelled freeze row, a shape missing from the freeze
file, a freeze-file row ordering change, a missing-file path. Expected mechanism per claim
C1: kinds read from the L1-frozen `census/round-99/shapes.tsv`, no hard-coded kind table,
so a relabelled copy of the file (same hook) moves the count; the frozen file's hash is
part of the claim.

Method: read the r98 runner (`census/round-98/declared-shapes.py`, hard-coded SHAPES) as
baseline, run it against the r99 hook to establish the known-good baseline, then attack the
actual candidate runner with freeze-file mutations — each mutation is a runnable reproducer
under `R99Reviewer1/cases/` (`cand_run.sh <freeze-copy> <empty-workdir>`), and every
observed `SHAPES-SUMMARY` line is recorded verbatim in the outputs next to it. An
independent reference implementation of the stated contract
(`R99Reviewer1/cases/check_kind.py`) was written from the claim text alone; it agrees with
the candidate on all 7 single-defect cases, so all findings below are properties of the
design, not of one implementation's quirks.

Commands and results below are for the candidate runner copied byte-identical to
`R99Reviewer1/cases/cand_runner.py` (verified: same sha256 as the file in `census/round-99/`,
`diff -q` clean). Exit codes are the process exit codes. I did not run the L1's freeze
verification or edit any predicate; where the report says "the claim must …" that is a
finding about the claim/runner contract, not a proposal to change the shape semantics.

## Baseline (no attack)

Command:
```
python3 -B cand_runner.py --freeze census/round-99/shapes.tsv \
  --search census/round-99/c1-survivor-search.py \
  --scripts census/round-98/shapes --work <empty dir>
```
Exit 0. Output (full, `R99Reviewer1/cases/cand_base.out`):
```
FREEZE sha256=8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14
SHAPE a1-sys-exit-helper.py kind=declared plain=3 hooked=3 ok
SHAPE a5-exit-builtin.py kind=declared plain=3 hooked=3 ok
SHAPE a5b-quit-builtin.py kind=declared plain=3 hooked=3 ok
SHAPE a4-caught-then-return.py kind=declared plain=3 hooked=3 ok
SHAPE a12-module-raise.py kind=declared plain=3 hooked=3 ok
SHAPE v1-module-raise.py kind=declared plain=3 hooked=3 ok
SHAPE v3-func-args-pattern.py kind=crash plain=3 hooked=70 ok
SHAPE w1-init-helper.py kind=crash plain=3 hooked=70 ok
SHAPE w2-main-raise-helper.py kind=crash plain=3 hooked=70 ok
SHAPE a3b-try-finally-sysexit.py kind=crash plain=3 hooked=70 ok
SHAPE t1-catch-module-falloff.py kind=declared plain=0 hooked=0 ok
SHAPE t4-reraise-at-module.py kind=declared plain=0 hooked=0 ok
SHAPE x1-module-finally-term.py kind=crash plain=1 hooked=70 ok
SHAPE x2-module-reraise-term.py kind=crash plain=1 hooked=70 ok
SHAPE q1o-save-then-bare-raise.py kind=crash plain=1 hooked=70 ok
SHAPE q1q-caught-then-direct.py kind=crash plain=1 hooked=70 ok
SHAPE q1i-finally-then-catch.py kind=declared plain=0 hooked=0 ok
SHAPES-SUMMARY shapes=17 mismatched=0
```
The r98 hard-coded runner gives the identical table on the same hook and scripts
(`SHAPES-SUMMARY shapes=17 mismatched=0`, exit 0) — the candidate preserves the r98 verdict
semantics and the r99 hook is byte-identical to the r98 hook, so this is a pure
mechanism review.

## Findings

### F1 (HIGH) — Dropping a row reaches 0 without the hook being checked on that shape

Reproducer: `R99Reviewer1/cases/cand_run.sh drop_q1q.tsv <work>` — freeze copy with the
q1q row deleted (the hardest shape: the r98 spot-check group that the object-keyed latch
was built to fix; hook gives plain=1 hooked=70). Observed:

```
FREEZE sha256=132ef7f9d411663798126bfd61f533484201b85910e9b7c7b45578e090e3182c
SHAPES-SUMMARY shapes=16 mismatched=0
```
exit 0. The runner has no completeness invariant: it runs exactly the rows present in the
freeze file, whatever they are. A claim that prints `shapes=16 mismatched=0` is not
distinguishable from the real claim without reading the `shapes=` field, and the C1 claim
as stated ("prints `SHAPES-SUMMARY shapes=17 mismatched=0`") depends on the reader tying
the `17` to the frozen population — which today is only enforced by eyeballing the
summary line. The FREEZE line identifies the file, but nothing in the run checks the file's
population against the 17 scripts in `census/round-98/shapes/` (no set comparison, no
`len(shapes) == len(dir)`). Any subset of the shapes, including the empty set, prints
`mismatched=0`. This is the "shape missing from the freeze file" case named in the seat
spec, and it passes.

Frozen-hash mitigation note: the FREEZE line does print the truncated file's hash, so a
verifier who pins `8bc642c4…` detects this. The claim statement makes that pinning the
user's job, not the runner's. The r98 runner had the same subset weakness in principle
(its SHAPES tuple) but the tuple was in the audited runner; now the population is in an
unvalidated data file. The reviewer recommends the L1 freeze the population by also
comparing the freeze file's name set to the scripts directory, or at minimum state the pin
as part of the claim. (This is a finding, not an edit — predicates are L1-frozen.)

### F2 (HIGH) — Two defects cancel: a broken hook plus a flipped file prints 0

Reproducer: `R99Reviewer1/cases/cand_run.sh` with a deliberately broken hook
(`cand_cases/broken_search.py`: the `_souji_atexit` EH leg — "declare iff the live foreign
object's last stamp is EH" — deleted, so every foreign termination crashes to 70) and a
freeze copy flipping `t1-catch-module-falloff.py`, `t4-reraise-at-module.py`,
`q1i-finally-then-catch.py` from `declared` to `crash`
(`cand_cases/flip_t1t4q1i.tsv`, sha256
`59dc65efb1ad57b59b22e8eca769b718221789fed6b1667c6e6d270c77e751eb`). Observed:

```
FREEZE sha256=59dc65efb1ad57b59b22e8eca769b718221789fed6b1667c6e6d270c77e751eb
SHAPE t1-catch-module-falloff.py kind=crash plain=0 hooked=70 ok
SHAPE t4-reraise-at-module.py kind=crash plain=0 hooked=70 ok
SHAPE q1i-finally-then-catch.py kind=crash plain=0 hooked=70 ok
SHAPES-SUMMARY shapes=17 mismatched=0
```
exit 0. Control: the same broken hook against the frozen file disagrees on exactly those
three shapes (`shapes=17 mismatched=3`, exit 1, `cand_brokenonly.out`) — so the frozen
file alone is what hides the hook defect, and the hash line alone is what exposes the
file defect. The claim says "the frozen file hash is part of the claim", which covers
this attack **iff** a verifier actually pins `8bc642c4…`; the runner itself does not and
cannot (it has no independent source of truth — that is the M6 design). This finding is
therefore not a bug in the runner but the statement that the C1 claim's security reduces
entirely to the verifier comparing the FREEZE line against the pinned hash, and the report
should say so explicitly rather than letting `mismatched=0` stand alone. (Compare: the
hard-coded r98 runner made this attack require editing the runner, which the lane's
review process catches; here only the hash catches it.)

### F3 (MEDIUM) — Duplicate rows and unknown shapes are not validated symmetrically

Reproducers (all against the candidate, all recorded):
- Duplicate q1q row appended (`cand_cases/dup_q1q.tsv`): exit 0,
  `SHAPES-SUMMARY shapes=18 mismatched=0` — a second row for the same name runs the
  shape twice, inflating the population without any error. The claim's `shapes=17` is the
  only thing that would catch it, same as F1.
- Extra unknown shape row (`zz-nope.py`, `cand_cases/extra.tsv`): exit 2,
  `SHAPE zz-nope.py missing` — correctly refused. This path exists only because the
  script file is missing; a duplicate name for a *real* script is not checked.
A name-uniqueness invariant (17 unique names, exactly the scripts in the directory) closes
both.

### F4 (MEDIUM) — Row ordering is (correctly) irrelevant; the claim does not say so

Reproducer `cand_cases/rev.tsv` (all data rows reversed): exit 0,
`SHAPES-SUMMARY shapes=17 mismatched=0`, with per-shape lines in file order. A verifier
comparing full outputs line-by-line against a reference run would see every line moved.
The summary is order-insensitive (correct), but the per-shape lines are order-sensitive
(file order, not sorted), so a strict diff is not the right check; this should be called
out in the claim note to avoid a future false alarm — and, conversely, it means "the file
was reordered" cannot be detected from the output either. Benign, but the reordering case
named in the seat spec behaves correctly only at the summary level.

### F5 (LOW) — Malformed input handling (all observed, all refused)

- Relabelled single row (q1q crash→declared, the named M6 test): exit 1,
  `SHAPES-SUMMARY shapes=17 mismatched=1`, `MISMATCH q1q-caught-then-direct.py` — the
  mechanism works: the count moves. FREEZE prints the new hash
  `d8947183ab5076c1bee43cda2c32a5ebeaacbfbe3366f62ef4cb2248120ffc0e`.
- Whitespace kind (`' crash'`): exit 1, `ValueError: unknown kind ' crash' for
  q1q-caught-then-direct.py` — the exclusive `declared`/`crash`/else-raise branch (verified
  in source) correctly refuses silent misclassification. (The r98 runner's
  `else: hooked == 70` would have treated an unknown kind as crash — a real improvement
  in the candidate.)
- Header removed: exit 1, `ValueError: bad header` — refused.
- Short row (<4 tab fields): `ValueError: bad row` — refused. (Not exercised with a
  reproducer; confirmed from source lines 23-27; the reference impl agreed.)
- Missing file path: `FileNotFoundError`, exit 1, no SHAPES-SUMMARY printed — refused,
  but via an uncaught traceback rather than a `SHAPES-FATAL` message. Cosmetic; a future
  runner could wrap it, but nothing passes by accident here.

### F6 (INFO) — The runner reads the file, genuinely

Checked mechanically: the candidate contains no shape names or kind table
(`grep` for any of the 17 script names in the source finds none), and `load_shapes`
parses `name\tkind` from the freeze file with header validation. The `plain` column of the
frozen file is parsed-length-checked but otherwise ignored (the runner derives plain rc by
running the script — correct; a wrong `plain` cell in a freeze copy cannot affect the
verdict, which I verified by inspection since the column is never read beyond field count).

## Attack matrix (candidate runner)

| Freeze mutation | Exit | SHAPES-SUMMARY | Verdict |
|---|---|---|---|
| frozen file (base) | 0 | shapes=17 mismatched=0 | claim holds |
| q1q crash→declared | 1 | shapes=17 mismatched=1 | count moves (M6 ✓) |
| q1q row dropped | 0 | shapes=16 mismatched=0 | **0 without checking q1q (F1)** |
| rows reversed | 0 | shapes=17 mismatched=0 | ok (F4) |
| q1q row duplicated | 0 | shapes=18 mismatched=0 | **0, wrong population (F3)** |
| unknown shape row | 2 | (missing, fatal) | refused |
| kind `' crash'` | 1 | (ValueError) | refused |
| header removed | 1 | (ValueError) | refused |
| freeze path missing | 1 | (FileNotFoundError) | refused (unclean) |
| broken hook + 3 rows flipped | 0 | shapes=17 mismatched=0 | **two defects cancel (F2)** |

## What the claim needs to be sound

1. Pin `8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14` as the file's
   sha256 (the runner prints it; the verifier must compare it) — without this, F2 is a
   live false-clean path.
2. Require the exact summary `shapes=17` (not just `mismatched=0`) and treat any other
   population as a failure — without this, F1/F3 pass.
3. Recommended (not blocking, since predicates are L1-frozen): a uniqueness/completeness
   invariant in the runner (unique names == directory listing). Findings are reported as
   findings with reproducers; this seat does not edit the runner.

## Verification actually exercised

- Baseline candidate run (above): exit 0, `shapes=17 mismatched=0`, all 17 per-shape lines
  `ok`. Full output: `R99Reviewer1/cases/cand_base.out`.
- r98 hard-coded runner vs r99 hook: exit 0, `shapes=17 mismatched=0` (independent baseline).
- Each attack above run against the candidate: exit codes and summary lines as tabulated;
  full outputs `R99Reviewer1/cases/cand_*.out`.
- The same 7 single-defect mutations run against the independent reference implementation
  (`R99Reviewer1/cases/check_kind.py`, written from the claim text): identical conclusions
  in every case (`R99Reviewer1/cases/*.out` for the reference runs, `RUN.md` indexes them).
- Source checks: no hard-coded shape names/kinds in the candidate; exclusive kind branch;
  header/column validation; hash printed before any shape runs. The `plain` column is
  length-checked only and never used for the verdict (F6).
- Lane state: read-only git throughout (`git rev-parse HEAD` = `c94d678c…`, HEAD ===
  0 debug, `git status` shows only the executor's untracked `census/round-99/`); no commit,
  no mutation of any lane file by this seat. The run scripts and fixture copies live only
  under `R99Reviewer1/` and scratch.

## Residual risk and gaps

- F1/F3 are open until the L1 acknowledges the population invariant or the runner gains
  it: `mismatched=0` alone does not imply the 17 frozen shapes were run. Mitigated today only
  by the printed hash + the `shapes=17` in the claim text.
- F2 is inherent to the M6 design: neither the runner nor the hook can detect a
  coordinated hook+file change; the pinned hash is the only control, and this review cannot
  verify the L1's pinning procedure — it only records that the pin must be
  `8bc642c4…` for the file on disk now.
- This review used the shape scripts in `census/round-98/shapes/` as the scripts input.
  If the L1 passes a different `--scripts` directory for the claim run, the population
  question (F1) reopens: a directory with fewer scripts and a freeze file matching them
  would print 17/0 with a different shape set. The hash check covers the file, not the
  directory.
- No judgement is passed on the hook's semantics (t1/t4/q1i declared, x1/x2/q1o/q1q
  errored) beyond noting the declared-shapes.expected reasoning and the r98 spot-check
  group; the baseline run confirms the hook agrees with all 17 frozen labels as written,
  and the mechanism review confirms the count moves when a label moves.

## L0 questions

None. No tool was installed or updated (python3 only, no host sysctl needed, no pacman).
