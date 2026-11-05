# S61ExecChronoArm: round-61 C1 control-chronology (exec seat)

Delivery dir: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-61/w1/S61ExecChronoArm/`

Report location: the seat spec asks for `.ufo/waves/round-61/w1/S61ExecChronoArm.md`, which is outside the
seat dir. The hard write scope is the seat dir only, so this report lives here. The L1 may move it.

## Delivered (sha256)

| file | sha256 |
|---|---|
| candidate-freeze-check.py | 7ef43b8f174fec50717858441822cd83e443bc83be57da8038ef7f3f3bc94828 |
| build-matrix.py | cda5c481c0ade726a3a54f86bd37458431104b9f45833c398010d197bfb50fed |
| c1-counter.py | 8b5a993f15d8d14bbca3be6120ec14ab5ad950a692197308a31b884188a10c76 |
| c1-matrix.tsv | 25b70aa14edae8f022ba090e73c2eeb3bcf7a1ab49d86b717318b32802a89600 |
| matrix/<11 cases>/ (pre.txt, counter.py, pop.tsv, ctl*.txt, expected.txt, notes.txt where used) | per file in the delivery dir |
| matrix/stubs/stub-accept.py, stub-refuse.py | 607cd7eb…, bd918189… |
| receipts/*.txt (13 receipts) and receipts/candidate-vs-base.diff | per file |

(The counter receipts pin the c1-counter.py digest in `instrument_sha256=` and the candidate or base bytes in `tool_sha256=`.)

## Candidate change (vs base c7228424c3919ecf142bab1aec8181722d86467b)

- New `control_red(blob)` (same EXIT rule as the existing CONTROL-NOT-RED check; that check now calls it,
  behaviour unchanged).
- New `control_chronology(repo, freeze, label, path)`: `git log --diff-filter=A --no-renames --full-history
  --format=%H FREEZE -- PATH`, oldest entry (last id). Refuses with `CONTROL-ADDED-NOT-BEFORE-FREEZE` when no
  adding commit resolves, when the id is not full 40-hex, when it equals FREEZE, or when it is not a strict
  ancestor of FREEZE. Detail names the receipt path, the resolved commit and the freeze commit.
- Called only under `--substance`, only when the Control blob is present at FREEZE, not a symlink, and red.
- Selftest: `selftest_case` gained `ctl_commit` (`freeze` | `ancestor` | `child`). Plain default stays
  `freeze` (unchanged plain fixtures). Substance default is now `ancestor`, so the 12 existing substance cases
  put their receipt in a strict-ancestor commit. Without that, the new arm would refuse their honest fixture.
  Their verdicts and expected classes are unchanged. Three new substance cases: at-freeze add (refuse,
  chronology class), child-of-freeze add (refuse, CONTROL-MISSING, since the blob is absent at FREEZE), and a
  strict-ancestor add (accept).

## Commands and observed output

All commands ran with absolute paths. Lane git calls were read-only (`show`, `rev-parse`, `log`, `cat-file`,
`merge-base`, `ls-tree`). Fixture repos lived under scratch, with `git -C` and a toplevel check. No git
mutation, no pacman, no tool installs. Tools used: git 2.56.0, Python 3.14.8 (both already present).

1. Base tool bytes: `git show c7228424…:tools/souji-freeze-check.py` → sha256 05e9a591…. Base `--selftest`: `SELFTEST cases=41 pass=41 fail=0`, EXIT=0. Base `--selftest --substance`: `SELFTEST cases=12 pass=12 fail=0`, EXIT=0.
2. Candidate `--selftest`: `SELFTEST cases=41 pass=41 fail=0`, EXIT=0. Byte-identical to base output (`cmp` OK).
3. Candidate `--selftest --substance`: `SELFTEST cases=15 pass=15 fail=0`, EXIT=0.
4. Real record, default (no --substance), rev d05a00019835dee5b9bb8fe738add080434c4d67, prereg census/round-60/preregistration.txt:
   base `SUMMARY claims=2 findings=0` EXIT=0; candidate identical output, EXIT=0. Byte-identical.
5. Real record, `--substance`:
   base `SUMMARY claims=2 findings=0` EXIT=0.
   candidate:
   ```
   FINDING C1 CONTROL-ADDED-NOT-BEFORE-FREEZE census/round-60/controls/c1-do-nothing.txt added at 2670e96af1b8, not a strict ancestor of freeze 2670e96af1b8
   FINDING C2 CONTROL-ADDED-NOT-BEFORE-FREEZE census/round-60/controls/c2-do-nothing.txt added at 2670e96af1b8, not a strict ancestor of freeze 2670e96af1b8
   SUMMARY claims=2 findings=2
   ```
   EXIT=1. The receipts are the r60 controls, which the prereg says were committed at 3b55250; git log shows
   they were ADDED by the freeze commit 2670e96a itself.
6. Matrix build (final): `python3 -B build-matrix.py --out DELIVERY --scratch SCRATCH` → EXIT=0. Rebuilds
   each case and verifies pinned hashes.
7. Counter, after arm: `python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv --base-tool-rev c7228424… --rev c7228424… --work WORK`
   → `SUMMARY matrix=11 base_forgeries=1 base_honest=4 new_forgeries=0 new_honest=4 class_mismatches=0 stubs=REJECTED`, EXIT=0.
8. Counter, do-nothing (`--new-arm plain`, base bytes in the new slot):
   → `SUMMARY matrix=11 base_forgeries=1 base_honest=4 new_forgeries=1 new_honest=4 class_mismatches=1 stubs=REJECTED`, EXIT=1.
   The spec expected new_forgeries=2. See deviation D1.
9. Stub as NEW tool: stub-accept → `new_forgeries=7 class_mismatches=7 stubs=REJECTED` EXIT=1;
   stub-refuse → `new_forgeries=0 new_honest=0 class_mismatches=7 stubs=REJECTED` EXIT=1. Both fail the matrix.
10. Default-output identity over the 11 rebuilt case repos (base vs candidate, no --substance): 11/11 identical
    stdout and exit code.

## Observed per-case class table (candidate --substance, rebuilt case repos)

| case | expect | base | candidate verdict | candidate finding classes (= pinned expected_class) |
|---|---|---|---|---|
| honest-1 | accept | accept | accept | - |
| honest-2 | accept | accept | accept | - |
| honest-3 | accept | accept | accept | - |
| forgery-kind-only | refuse | refuse | refuse | CONTROL-COMMAND-MISSING, CONTROL-INSTRUMENT-MISSING, CONTROL-REV-MISSING |
| forgery-digest | refuse | refuse | refuse | CONTROL-INSTRUMENT-MISMATCH |
| forgery-rev-missing | refuse | refuse | refuse | CONTROL-REV-MISSING |
| forgery-command-other | refuse | refuse | refuse | CONTROL-COMMAND-MISMATCH |
| forgery-rev-orphan | refuse | refuse | refuse | CONTROL-REV-NOT-BEFORE-FREEZE |
| chrono-at-freeze | refuse | **accept** | refuse | CONTROL-ADDED-NOT-BEFORE-FREEZE |
| chrono-after | refuse | refuse | refuse | CONTROL-MISSING |
| chrono-ancestor | accept | accept | accept | - |

## Matrix design (11 cases)

- honest-1/2/3 and chrono-ancestor: the receipt is added by a strict-ancestor commit. honest-3 uses rev = a
  non-base ancestor. chrono-ancestor adds a filler commit between the receipt and the freeze.
- forgery-kind-only, -digest, -rev-missing, -command-other: r60 shapes, receipt added by a strict ancestor so
  that each row fails for one cause.
- forgery-rev-orphan: rev names a parentless `commit-tree` on the empty tree, unreferenced, not reachable from
  the freeze. Replaces the r60 tag case.
- chrono-at-freeze: pre.txt and ctl.txt in the same freeze commit (the r60 rejection shape).
- chrono-after: ctl.txt added by a child of the freeze (see D1).

## Deviations and conflicts with the spec

- D1 (chrono-after, do-nothing count). The spec expects the base arm to accept both chrono rows
  (new_forgeries=2 in the do-nothing control). That cannot hold. The base tool reads the Control blob at
  FREEZE. A receipt added by a child of the freeze is absent at FREEZE, so the base refuses with
  CONTROL-MISSING. The observed do-nothing result is new_forgeries=1, class_mismatches=1, EXIT=1. The
  candidate also refuses chrono-after, with CONTROL-MISSING. A present-at-FREEZE receipt can only ever be
  added at FREEZE or at a strict ancestor of it, because git log is bounded to FREEZE. So the chronology
  arm cannot catch an after-freeze receipt. The L1 should decide whether to keep the row, and what the
  do-nothing expectation should say.
- D2 (honest and forgery shapes). The spec says the honest and forgery rows use the r60 shapes with the
  receipt added by a strict ancestor. In r60 the receipt was in the freeze commit. Kept as a strict-ancestor
  add here, otherwise every refuse row would also pick up CONTROL-ADDED.
- D3 (selftest substance fixture placement). The 12 existing substance selftest cases now place the receipt in
  a strict-ancestor commit, so the candidate stays green. Verdicts and expected classes are unchanged.
- D4 (plain arm invocation). `--new-arm plain` runs the base bytes with `--substance`, the same invocation as
  the candidate. Without `--substance` the base accepts most forgeries, which makes the do-nothing count
  meaningless. The base arm also runs with `--substance`.
- D5 (matrix size). 11 rows, as the spec's shape list. The `expected_class` column is the observed finding-id
  set, sorted and comma-joined, not a single id. Only forgery-kind-only has more than one class.
- D6 (`--rev`). Logged only, as in r60. The base bytes come from `--base-tool-rev`, and the new bytes from the
  candidate file (the candidate is not committed; its digest is pinned in the receipts).
- D7 (C2). The C2 instruments (r60 receipt-writer fixture, honest writer, mutants) are not in this seat's target
  and are not touched or delivered.

## Limits

- The `ids[]` empty branch and the non-full-40 branch of `control_chronology` are defensive and are not exercised
  by any selftest or matrix case. The equal-to-freeze and not-strict-ancestor branches are exercised (chrono-at-freeze
  and its selftest).
- The chronology arm is bounded to ancestors of FREEZE by construction. It cannot see receipts added after FREEZE
  (D1).
- Byte binding only: `counter.py` and the Population/Counter digests are compared as bytes. The counter is never run.
- The counter's `--rev` is logged only; the matrix proves nothing about the measured revision itself.
- The real-record receipts (r60 controls) show the chronology defect the r60 spot-check named. Whether that record
  is re-frozen is for the L1.

## Checks the L1 should run

- `python3 -B tools/souji-freeze-check.py --selftest` (expect 41/41) and `--selftest --substance` (expect 15/15).
- Real record, `--substance`, candidate: expect EXIT=1 with 2 CONTROL-ADDED-NOT-BEFORE-FREEZE findings.
- The counter, after arm: expect `new_forgeries=0 new_honest=4 class_mismatches=0 stubs=REJECTED` EXIT=0.
- The counter, `--new-arm plain`: expect `new_forgeries=1` (see D1), EXIT=1.
