# S56mutation02 — C2 kill power (mutation-run-revert over the v5 capture counter)

Round 56, wave w1, seat S56mutation02 (mutation-tester). Lane:
`/home/vgpnk/Projects/shokunin/souji-shokunin` (read-only to this seat).
Measured revision `cce21b555a617cadda782613ec1e9d3a0c12ac83`, base
`fafe371694fea41c5d23f63083865d5ccf3f1d36`. Scratch:
`/fast/scratch/hyaku/souji-r56/S56mutation02` (deleted after this report;
receipts copied to `./evidence/`).

## Frozen pins (verified on committed bytes at cce21b55, all 8 OK)

| path | sha256 (git show cce21b55:path) | frozen pin | match |
|---|---|---|---|
| census/round-56/c1-counter.py | 975d35201075b71affcd106b46341c7300e87e200b04c6c44864d636bcbbf179 | 975d3520…bbf179 | OK |
| census/round-56/c2-counter.py | 5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8 | 56082011…259cb8 | OK |
| census/round-56/fixtures/build-fixtures.py | 2f26d6aa68ce44cfd9e4afdeaa4ef04837db7622c5ed5213429d8bda1c30b85a | 2f26d6aa…30b85a | OK |
| census/round-56/fixtures/run-matrix.sh | a7e1a8924b9e3fd636f9882e368306faad8908638677e83fa395878211962de3 | a7e1a892…962de3 | OK |
| census/round-56/records/c1-selftest-expected.tsv | 48a7cc0e869773b493b0b5f01446f70b9016595f1c307602912317aa3f7c5bfb | 48a7cc0e…7c5bfb | OK |
| census/round-56/records/c2-selftest-expected.tsv | 90517c4d4c6b7542229d1df85287bbfdf3fef631e2e18e279ad62c4c926841b3 | 90517c4d…6841b3 | OK |
| census/round-55/c1-counter.py | 944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2 | 944feafa…d921a2 | OK |
| census/round-55/c2-counter.py | e4eb34e6375d16a8c7a8842ac43ef26f262167d85eb4615c1ab07e1c994a568c | e4eb34e6…a568c | OK |

C2 population bytes at the measured revision (re-hashed here): capture
`census/round-55/records/fleet-root-census.tsv` = `088aaa26…6f73d40`, receipt
`census/round-55/records/fleet-root-census-run.txt` = `479b2715…4bab45`,
tool `tools/souji-fleet-root-census.py` = `e7e79952…067a5b` — all three equal
the prereg pins.

Lane-tip observation (not a claim input): the tip advanced mid-run from
`cce21b55` to `148f39a6` ("round-56: post-freeze receipts …"). The frozen C2
bytes are unchanged at the new tip (c2-counter, builder and expected TSV hash
identically), and the only working-tree modification in the C2 surface is
`census/round-56/records/landing-suite-standing.txt` (not written by this
seat, not read by the C2 counter). All probes below pass `--rev cce21b55`
explicitly, so the tip move does not touch this evidence.

## Method

Base bytes copied with `git show cce21b55:census/round-56/c2-counter.py` into a
scratch tree mirroring `census/round-56/` (so the counter's HERE-relative
`fixtures/build-fixtures.py` and `records/c2-selftest-expected.tsv` resolve).
Builder and expected TSV were copied byte-identical and asserted against their
frozen pins by the generator before any run. Each mutant is an exact
single-occurrence text edit of the base (the generator asserts `count == 1`
per edit and writes a unified diff to `evidence/<id>.diff`); no frozen byte was
edited and nothing was committed anywhere.

Two bounded detectors, run on pristine, mutant, and restored bytes:

- **D1 selftest** — `python3 -B <tree>/census/round-56/c2-counter.py --selftest
  --work <scratch>/st-<id> --builder-sha256 2f26d6aa…30b85a --expected-sha256
  90517c4d…6841b3`. PASS iff exit 0 **and** `SELFTEST pass cases=18`.
- **D2 real lane** — `python3 -B <tree>/census/round-56/c2-counter.py --root
  /home/vgpnk/Projects/shokunin/souji-shokunin --rev
  cce21b555a617cadda782613ec1e9d3a0c12ac83 --capture
  census/round-55/records/fleet-root-census.tsv --receipt
  census/round-55/records/fleet-root-census-run.txt --tool-sha256
  e7e79952f7830d75c5b0eee35c2369716053f40121c7d3be370f7abdda067a5b --scratch
  <scratch>/rl-<id>`. PASS iff exit 0 **and** stdout byte-identical to the
  pristine counter's stdout (sha256 `40fbb8b8…63b8`).

`TMPDIR` and cwd were the scratch dir; every run is a read-only `git show`
through the counter's scrubbed environment. No mutating git/jj command was run
anywhere; the lane was never written.

### Baseline (pristine bytes)

```
$ python3 -B base-tree/census/round-56/c2-counter.py --selftest --work …/st-base \
    --builder-sha256 2f26d6aa…30b85a --expected-sha256 90517c4d…6841b3
SELFTEST pass cases=18
EXIT=0
```

```
$ python3 -B base-tree/census/round-56/c2-counter.py --root …/souji-shokunin \
    --rev cce21b555a617cadda782613ec1e9d3a0c12ac83 \
    --capture census/round-55/records/fleet-root-census.tsv \
    --receipt census/round-55/records/fleet-root-census-run.txt \
    --tool-sha256 e7e79952…067a5b --scratch …/rl-base
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=cce21b555a61
EXIT=0
```

Baseline outputs: `evidence/base-selftest.out` (sha256 `e0a0df77…b2169`,
ends `EXIT=0`), `evidence/rl-base.out` (sha256 `40fbb8b8…63b8`).

## Mutant table

`D1` / `D2` are the detectors above; a mutant is KILLED when either detector
rejects it. Full per-mutant stdout is in `evidence/<id>-selftest.out` and
`evidence/<id>-real.out` (both end with `EXIT=<rc>`); restore receipts in
`evidence/<id>-restore.txt`; post-restore probes in `evidence/<id>-postrestore.txt`.

| id | single defect (exact edit of the frozen bytes) | mutant sha256 | D1 | D2 | verdict — killer |
|---|---|---|---|---|---|
| N1 | `RECEIPT_KV` first key class `[A-Za-z0-9_]` → `[A-Za-z]` (r55 RD-A regression) | f633a4fe…f9d8 | FAIL rc=1 | pass | **KILLED** — `FC1-UNDERSCORE-KEY`, `FC2-DIGIT-KEY` (rc 0 vs want 1, finding `-` vs `RECEIPT-UNKNOWN-KEY`) |
| N2 | `RECEIPT_KV` value group `(\S*)` → `(\S+)` (empty value ignored, S55-S5) | 1f15f3bf…3e32 | FAIL rc=1 | pass | **KILLED** — `FC3-EMPTY-VALUE-KEY` (rc 0 vs 1, `-` vs `RECEIPT-UNKNOWN-KEY`) |
| N3 | `SELFTEST-ROW-MISMATCH` loops removed (row-set assertion off) | 13e05ec7…73b8 | pass rc=0 | pass | **SURVIVED** — no fixture detects a missing assertion (see N3 analysis) |
| N4 | `FA9-WRONG-TOOL-PIN` removed from the selftest run list | 0def1425…32d2 | FAIL rc=1 | pass | **KILLED** — `SELFTEST-ROW-MISMATCH expected row did not run: FA9-WRONG-TOOL-PIN` |
| N5 | `FB4-PIN-SHAPE` removed from the selftest run list | 7dc3bcd0…059c | FAIL rc=1 | pass | **KILLED** — `SELFTEST-ROW-MISMATCH expected row did not run: FB4-PIN-SHAPE` |
| N6 | `COMMENT-AMBIGUOUS-NAME` back to v3 (`>= 5` tabs only) | 2b55d346…ce0 | FAIL rc=1 | pass | **KILLED** — `FB1-TAB4-ROW` (rc 0 vs 1, `-` vs `COMMENT-AMBIGUOUS-NAME`); the 5-tab fixtures `FA2`/`FA4` still pass under the v3 rule |
| N7 | unknown-receipt-key check dropped entirely | e880e6c3…2ac9 | FAIL rc=1 | pass | **KILLED** — `FA5-EXTRA-KEY`, `FB2-LOWER-KEY`, `FB3-NOSPACE-KEY`, `FC1`, `FC2`, `FC3` (all rc 0 vs 1) |
| N8 | `ROWS-UNSORTED` check dropped | ccab6381…3dc5 | FAIL rc=1 | pass | **KILLED** — `FA1-UNSORTED` (rc 0 vs 1, `-` vs `ROWS-UNSORTED`) |
| N9 | `CAPTURE-CRLF` check dropped | bbd5aa78…7147 | FAIL rc=1 | pass | **KILLED** — `FA6-CRLF` by **finding identity**: rc stays 1, finding becomes `CAPTURE-RECEIPT-MISMATCH` instead of `CAPTURE-CRLF` |
| N10 | whole `--tool-sha256` pin branch dropped (malformed + mismatch) | b6c0b78b…3788 | FAIL rc=1 | pass | **KILLED** — `FA9-WRONG-TOOL-PIN` (rc 0 vs 1) and `FB4-PIN-SHAPE` (rc 0 vs 2) |
| N11 | over-strict name rule: a leading `.` is a bad name | 172f9c57…1174 | pass rc=0 | **FAIL rc=1** | **KILLED** — **real lane only**: 9 `bad or duplicate name '.…'` findings + `COUNT … recomputed` drift (see N11 note) |
| N3N4 | composed probe: N3 + N4 (loops removed **and** FA9 arm removed) | 35ef1006…bea7 | exit 0, `cases=17` (D1's exact `cases=18` string is the only deviation) | pass | **SURVIVED on the row-set check** — proves N4's kill depends solely on the removed assertion |

Exact kill lines (quoted from the receipts):

```
N1: SELFTEST-CASE FC1-UNDERSCORE-KEY fail rc=0 want_rc=1 finding=- want_finding=RECEIPT-UNKNOWN-KEY
    SELFTEST-CASE FC2-DIGIT-KEY fail rc=0 want_rc=1 finding=- want_finding=RECEIPT-UNKNOWN-KEY
N2: SELFTEST-CASE FC3-EMPTY-VALUE-KEY fail rc=0 want_rc=1 finding=- want_finding=RECEIPT-UNKNOWN-KEY
N4: SELFTEST-ROW-MISMATCH expected row did not run: FA9-WRONG-TOOL-PIN
    SELFTEST fail cases=17   EXIT=1
N5: SELFTEST-ROW-MISMATCH expected row did not run: FB4-PIN-SHAPE
    SELFTEST fail cases=17   EXIT=1
N6: SELFTEST-CASE FB1-TAB4-ROW fail rc=0 want_rc=1 finding=- want_finding=COMMENT-AMBIGUOUS-NAME
N8: SELFTEST-CASE FA1-UNSORTED fail rc=0 want_rc=1 finding=- want_finding=ROWS-UNSORTED
N9: SELFTEST-CASE FA6-CRLF fail rc=1 want_rc=1 finding=CAPTURE-RECEIPT-MISMATCH want_finding=CAPTURE-CRLF
N10: SELFTEST-CASE FA9-WRONG-TOOL-PIN fail rc=0 want_rc=1 finding=- want_finding=TOOL-SHA-ARG-MISMATCH
     SELFTEST-CASE FB4-PIN-SHAPE fail rc=0 want_rc=2 finding=- want_finding=TOOL-SHA-ARG-MALFORMED
N3: SELFTEST pass cases=18   EXIT=0
N3N4: SELFTEST pass cases=17   EXIT=0
```

D2 for N1–N10 and N3N4 is byte-identical to the pristine real-lane stdout
(exit 0): the mutations weaken defect detection only, and the real capture is
honest, so they are invisible there by construction. N11 is the reverse case.

## N3 analysis — the row-set check

N3 removes both `SELFTEST-ROW-MISMATCH` loops and nothing else. The committed
selftest population cannot detect that removal: all 18 arms still run, every
expected row exists, every case passes, and the selftest prints
`SELFTEST pass cases=18`, `EXIT=0`. **No committed fixture can kill N3** — a
fixture is an input to the counter, and N3 removes an assertion about the
fixture *set*, so the detector for N3 would have to be a meta-test that
deliberately deletes an arm (i.e. the T6/T9 probe itself).

That is exactly what the composed probe shows. With the loops present, an arm
removal is caught by the row-set check alone:

```
N4 (FA9 arm removed):  SELFTEST-ROW-MISMATCH expected row did not run: FA9-WRONG-TOOL-PIN
                       0 per-case failures; SELFTEST fail cases=17; EXIT=1
N5 (FB4 arm removed):  SELFTEST-ROW-MISMATCH expected row did not run: FB4-PIN-SHAPE
                       0 per-case failures; SELFTEST fail cases=17; EXIT=1
```

With N3 applied on top of the same arm removal, the failure disappears:

```
N3N4: SELFTEST pass cases=17   EXIT=0
```

So C2's T6/T9 ("one expected arm removed from the run list → fails with
`SELFTEST-ROW-MISMATCH`, exit 1") **holds** on the frozen bytes — N4 and N5
confirm it twice, for both arms, with zero per-case failures. The survivor is a
self-coverage gap, not a falsification: the guard that implements T6 has no
test of its own. The only visible trace of an arm removal under N3 is the final
count (`cases=17` instead of `cases=18`), which is a printed number, not an
assertion — a consumer that compares the exact prereg string `SELFTEST pass
cases=18` would notice, the counter's own exit status would not.

Finding for the L1: this is a named limit of the instrument, not a C2 kill.
If the row-set guard is to be protected, a future counter would need an
explicit arm-count assertion (e.g. `len(names) == len(exp)`) or a selftest
arm that runs the selftest recursively — neither exists in the frozen v5 bytes.

## N11 — real-lane-only kill and population coverage finding

N11 adds `or name.startswith('.')` to the bad-name condition. The committed
selftest population has no name beginning with a dot, so all 18 arms pass
(`SELFTEST pass cases=18`, exit 0). The real capture has nine dotfiles, and the
real-lane detector kills it:

```
FINDING bad or duplicate name '.devin'
FINDING bad or duplicate name '.gitignore'
FINDING bad or duplicate name '.jj'
FINDING bad or duplicate name '.local'
FINDING bad or duplicate name '.omp'
FINDING bad or duplicate name '.ruff_cache'
FINDING bad or duplicate name '.scratch'
FINDING bad or duplicate name '.tower'
FINDING bad or duplicate name '.ufo'
FINDING COUNT tracked declared 22 recomputed 17
FINDING COUNT ignored declared 22 recomputed 21
FINDING COUNT untracked-stray declared 5 recomputed 2
SUMMARY entries=49 rows=49 unclassified=9 class_mismatch=0 counts=FAIL tool_sha=ok removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=cce21b555a61
EXIT=1
```

This is a coverage finding for the C2 fixture population (16 C2 fixtures + 2
selftest arms, none with a dotfile name), not a counter defect: the frozen
counter's name rule is correct, and the real lane catches the over-strict
variant. It also shows the real-lane detector's role is to catch
**over-strict** mutants; **under-strict** mutants are caught by D1.

## Restoration

Every mutant tree's `c2-counter.py` was overwritten with the frozen base bytes
after its two runs and re-hashed: 12/12 `restored_sha256 =
5608201124fa4df9f378a95dda6472077bca249bf8bdf51a4a24e0d59c259cb8`,
`RESTORE ok` (`evidence/<id>-restore.txt`). Both detectors were then re-run on
each restored copy: 12/12 `sha_ok=True D1_restored=True D2_restored=True`
(selftest and real-lane stdout byte-identical to the pristine baseline;
`evidence/postrestore.tsv`, `evidence/<id>-postrestore.txt`). The base tree was
re-hashed after all runs and is unchanged. The scratch tree is deleted after
this report; the receipts above are copied into `./evidence/`.

## Named limits / notes

- N9's kill is by finding identity only: the exit code stays 1. A claim check
  that compared exit codes alone would let this mutant survive; the committed
  expected TSV's `expect_finding` column is what kills it.
- N6's kill is exactly the four-tab boundary (`FB1-TAB4-ROW`); `FA2-COMMENT`
  and `FA4-SPACE-NAME` carry five tabs and remain refused under the v3 rule,
  so they cannot distinguish the two rules.
- The real-lane detector is a no-false-positive check on an honest input; it
  cannot kill under-strict mutants (N1–N10 all pass D2). Both detectors are
  reported separately above.
- No frozen byte was edited, no lane write, no commit, no subagent dispatch.
  No tool installs were needed (python3 3.14 / git present); nothing was added
  to PATH.
- L1 bounds clarification (IRC, this wave): committed builder/helpers may
  `git init`/config/add/commit only inside asserted scratch fixture roots.
  Complied, no contradiction: the committed builder (unmodified, pin
  `2f26d6aa…30b85a`) creates and commits only under
  `/fast/scratch/hyaku/souji-r56/S56mutation02/{st,rst}-*/` fixture dirs and
  asserts `git -C <fixture> rev-parse --show-toplevel == <fixture>` before any
  commit (`init_repo`); no lane/fleet/sibling mutation was performed.
- Receipt inventory in `./evidence/`: `base-selftest.out`, `rl-base.out`,
  `results.tsv`, `mutants.tsv`, `postrestore.tsv`, `<id>.diff` ×12,
  `<id>-selftest.out` ×12, `<id>-real.out` ×12, `<id>-restore.txt` ×12,
  `<id>-postrestore.txt` ×12. Every `.out`/`.txt` receipt ends with `EXIT=<rc>`.

VERDICT: SURVIVORS
SURVIVORS: N3 (SELFTEST-ROW-MISMATCH assertion removal — no committed fixture can detect a missing assertion; the composed N3N4 probe confirms the arm-removal kill depends entirely on the removed loops). All seven behavioral mutants (N1, N2, N6, N7, N8, N9, N10) are killed by named fixtures, N4/N5 by the row-set check (so C2 T6/T9 holds), and N11 by the real lane only.
BOUNDS-VOCABULARY MAPPING: ATTACK-FOUND (a mutant survived the frozen detector set: the row-set guard has no self-coverage). No DISAGREE on C2's frozen targets — T1–T5 were not the object of this seat; T6/T9 hold on the frozen bytes (N4/N5).
