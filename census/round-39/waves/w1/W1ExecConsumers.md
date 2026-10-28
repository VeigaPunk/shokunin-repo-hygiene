# W1ExecConsumers — consumer fixtures at the current worktree bytes

Role: executor (leaf). Assignment: re-run every consumer fixture the round harm-checks, record
counts. No lane byte was edited by this seat; measurement only.

## Environment / provenance

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Lane HEAD at measurement: `c0b007b42af9a03d7edc32533bcac27484223997`
  (`round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows`)
- Frozen base: `ed30b7f5b77939c9073348d810730bc4f355708d`
- Audited tool bytes in the worktree equal HEAD (`git diff --quiet HEAD -- tools/souji-worktree-drift.py tools/souji-citation-reconcile.py` → rc 0, `WORKTREE==HEAD for both audited tools`):
  - `tools/souji-worktree-drift.py` sha256 `4e07f1df2a61c2bffdc1108fc97fe86feb6c6cc96bfdfa9c14415736877018be`
  - `tools/souji-citation-reconcile.py` sha256 `59f1e57d7af02cac675757066fb6fa2629a0153f21c98a62e04b6d3b301d2b73`
- Base tool bytes extracted with `git show ed30b7f5...:tools/<name>` into scratch:
  - `base/souji-worktree-drift.py` sha256 `14e9c0f77d7e817df96b8ed656bfc18c879bb838a5036d1b7fc2f864c510d194`
  - `base/souji-citation-reconcile.py` sha256 `56866ea8f832332c2f69dcba4ddcd9ba5d7894bf9a2e82715962e2fb19bfcbe8`
  - `base/souji-pre-report-gate.sh` sha256 `acdb88160fb8dea93f06b3276b5dc2d5fa5e85031852e8b3fbb4e76998b7ae66`
    — identical to the worktree tool (`sha256sum tools/souji-pre-report-gate.sh` →
    `acdb8816...7ae66`); `git diff --stat ed30b7f5..HEAD -- tools/souji-pre-report-gate.sh` is empty.
- The six instrument fixtures are byte-identical at base and at the measured worktree
  (`git diff --quiet ed30b7f5 -- <fixture>` → rc 0 for each; blob hashes equal, e.g.
  `3b771eb6052e 3b771eb6052e tests/fixtures/r38-drift-record.py`,
  `5a1c7bb522fe 5a1c7bb522fe tests/fixtures/r27-pre-report-gate.sh`). So a base-arm run and a
  current-arm run use the same instrument, and a count difference can only come from the tool.
- Scratch: `S=/fast/scratch/hyaku/souji-r39/W1ExecConsumers` (retained, see last section).
- Sibling seats were concurrently editing unrelated lane paths during the run
  (`git status --porcelain` at end: ` M corpus/lessons/round-39.md`, plus untracked
  `census/round-39/records/{c2-after,c3-after,census-after,census-before}.txt`). None of those
  paths is read by the six fixtures; the audited tool and fixture bytes were verified equal to
  HEAD/base as recorded above.
- Tooling installed: none.

## Current-arm results (worktree bytes, HEAD c0b007b4)

### 1. `tests/fixtures/r38-drift-record.py` — tool `tools/souji-worktree-drift.py`

```
TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecConsumers python3 -B tests/fixtures/r38-drift-record.py --tool tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r39/W1ExecConsumers
```

rc=0, stdout (stderr empty):

```
case-total-ok=PASS
case-total-repos-mismatch=PASS
case-total-regs-mismatch=PASS
case-total-prunable-mismatch=PASS
case-duplicate-name=PASS
case-no-total-row=PASS
case-bad-line=PASS
case-empty-record=PASS
case-missing-record=PASS
case-comments-and-blanks=PASS
SUMMARY cases=10 pass=10 fail=0
```

Verdict: PASS — 10/10, no failure detail line.

### 2. `tests/fixtures/r36-worktree-drift.py` — tool `tools/souji-worktree-drift.py`

```
TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecConsumers python3 -B tests/fixtures/r36-worktree-drift.py --tool tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r39/W1ExecConsumers
```

rc=0, stdout (stderr empty):

```
control=STUB-REJECTED
case-match=PASS 
case-regs-changed=PASS 
case-prunable-changed=PASS 
case-absent=PASS 
case-malformed=PASS 
case-total-mismatch=PASS 
case-empty=PASS 
case-unrecorded=PASS 
case-read-only=PASS 
case-json-inside-tree=PASS 
case-trace-env=PASS 
case-live-repos-non-negative=PASS 
SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED
```

(The trailing space on the `case-*=PASS ` lines is the fixture's own `check()` formatting,
confirmed with `cat -A`: `case-match=PASS $`.)

Verdict: PASS — 12/12, false-green control rejected.

### 3. `tests/fixtures/r38-drift-write-envelope.py` — tool `tools/souji-worktree-drift.py`

```
TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecConsumers python3 -B tests/fixtures/r38-drift-write-envelope.py --tool tools/souji-worktree-drift.py --work /fast/scratch/hyaku/souji-r39/W1ExecConsumers
```

rc=0, stdout (stderr empty):

```
case-fifo-json-refused=PASS
case-fifo-json-with-reader=PASS
case-record-alias-refused=PASS
case-record-hardlink-refused=PASS
case-docstring-enum=PASS
case-json-written-regular=PASS
case-json-inside-tree=PASS
case-json-hardlinked=PASS
case-json-symlink-resolved=PASS
case-json-directory=PASS
case-record-outside-root=PASS
case-summary-still-exact=PASS
SUMMARY cases=12 pass=12 fail=0
```

Verdict: PASS — 12/12. In particular `case-docstring-enum=PASS`, the case that reads the drift
docstring the C2 repair touched.

### 4. `tests/fixtures/r37-citation-reconcile.py` — tool `tools/souji-citation-reconcile.py`

```
TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecConsumers python3 -B tests/fixtures/r37-citation-reconcile.py --tool tools/souji-citation-reconcile.py --work /fast/scratch/hyaku/souji-r39/W1ExecConsumers
```

rc=0, stdout (stderr empty):

```
case-ok=PASS
case-anchor-missing=PASS
case-anchor-duplicated=PASS
case-expected-missing=PASS
case-stale-present=PASS
case-receipt-absent=PASS
case-receipt-disagrees=PASS
case-receipt-unnamed=PASS
case-register-pinned=PASS
case-boundary=PASS
case-receipt-is-file=PASS
case-worktree-tamper=PASS
case-empty-register=PASS
case-duplicate-id=PASS
case-stale-dash=PASS
case-missing-header=PASS
control=FALSE-GREEN-REJECTED
SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED
```

Verdict: PASS — 16/16, false-green control rejected.

### 5. `tests/fixtures/r38-citation-commit.py` — tool `tools/souji-citation-reconcile.py`

```
TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecConsumers python3 -B tests/fixtures/r38-citation-commit.py --tool tools/souji-citation-reconcile.py --work /fast/scratch/hyaku/souji-r39/W1ExecConsumers
```

rc=0, stdout (stderr empty):

```
case-commit-ok=PASS
case-commit-unresolved=PASS
case-commit-not-ancestor=PASS
case-commit-unnamed=PASS
case-commit-receipt-absent=PASS
case-commit-receipt-disagrees=PASS
case-legacy-7col=PASS
case-register-rev=PASS
case-stale-present=PASS
case-expected-missing=PASS
case-receipt-unnamed=PASS
case-anchor-count=PASS
case-receipt-arm-disagrees=PASS
case-malformed-commit=PASS
SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED
```

Verdict: PASS — 14/14, false-green control rejected.

### 6. `tests/fixtures/r27-pre-report-gate.sh` (bash) — tool `tools/souji-pre-report-gate.sh`

```
TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecConsumers bash tests/fixtures/r27-pre-report-gate.sh
```

rc=0, stdout:

```
case-clean-pass=PASS
case-remote-mismatch=PASS
case-missing-shonen=PASS
case-dirty-tree=PASS
control=FALSE-GREEN-REJECTED
cases=4 pass=4 control=FALSE-GREEN-REJECTED
```

stderr (four identical lines, one per `setup`, from `git clone` of a bare repo with no refs):

```
warning: You appear to have cloned an empty repository.
warning: You appear to have cloned an empty repository.
warning: You appear to have cloned an empty repository.
warning: You appear to have cloned an empty repository.
```

Verdict: PASS — 4/4, false-green control rejected; the stderr lines are git's empty-clone
advisory on the fixture's own bare origin, not a failure.

## Base-arm control (same instrument, `ed30b7f5` tool bytes)

Each fixture was re-run with `--tool $S/base/<tool>` (r27 with a scratch lane root
`$S/baselane/{tools,tests/fixtures}` holding the base gate bytes), same `TMPDIR`:

| fixture | base SUMMARY | current SUMMARY | pass delta |
|---|---|---|---|
| r38-drift-record.py | `SUMMARY cases=10 pass=10 fail=0` (rc 0) | `cases=10 pass=10 fail=0` | 0 |
| r36-worktree-drift.py | `SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` (rc 0) | `cases=12 pass=12 fail=0 control=STUB-REJECTED` | 0 |
| r38-drift-write-envelope.py | `SUMMARY cases=12 pass=12 fail=0` (rc 0) | `cases=12 pass=12 fail=0` | 0 |
| r37-citation-reconcile.py | `SUMMARY cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` (rc 0) | `cases=16 pass=16 fail=0 control=FALSE-GREEN-REJECTED` | 0 |
| r38-citation-commit.py | `SUMMARY cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED` (rc 0) | `cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED` | 0 |
| r27-pre-report-gate.sh | `cases=4 pass=4 control=FALSE-GREEN-REJECTED` (rc 0) | `cases=4 pass=4 control=FALSE-GREEN-REJECTED` | 0 |

Commands run, with `S=/fast/scratch/hyaku/souji-r39/W1ExecConsumers`, cwd
`/home/vgpnk/Projects/shokunin/souji-shokunin`:

```
TMPDIR=$S python3 -B tests/fixtures/r38-drift-record.py --tool "$S/base/souji-worktree-drift.py" --work "$S"
TMPDIR=$S python3 -B tests/fixtures/r36-worktree-drift.py --tool "$S/base/souji-worktree-drift.py" --work "$S"
TMPDIR=$S python3 -B tests/fixtures/r38-drift-write-envelope.py --tool "$S/base/souji-worktree-drift.py" --work "$S"
TMPDIR=$S python3 -B tests/fixtures/r37-citation-reconcile.py --tool "$S/base/souji-citation-reconcile.py" --work "$S"
TMPDIR=$S python3 -B tests/fixtures/r38-citation-commit.py --tool "$S/base/souji-citation-reconcile.py" --work "$S"
TMPDIR=$S bash "$S/baselane/tests/fixtures/r27-pre-report-gate.sh"
```

`baselane` was built as `mkdir -p $S/baselane/{tools,tests/fixtures}` plus
`cp $S/base/souji-pre-report-gate.sh $S/baselane/tools/souji-pre-report-gate.sh` and
`cp tests/fixtures/r27-pre-report-gate.sh $S/baselane/tests/fixtures/`, so the fixture resolves
`$ROOT/tools/souji-pre-report-gate.sh` to the base bytes. Its stdout also carried the same four
`warning: You appear to have cloned an empty repository.` lines (interleaved before each
`case-*=PASS`), rc 0.

Verdict: no consumer regresses against its base reading — every fixture has the same case count,
the same pass count and the same control tag on both tool revisions; pass delta 0 on all six. This
is also the positive control for the C2 harm leg: the repairs (`--rev` resolution, drift docstring)
changed no consumer verdict, and no consumer gained a pass only because a case was weakened (the
fixture bytes are identical at base and HEAD).

## Advisory finding for the L1 (no bytes changed by this seat)

The frozen C2 predicate says: "L6 six consumer fixtures stay green", and this seat's assignment
enumerates the same six (the five `--tool` fixtures plus `tests/fixtures/r27-pre-report-gate.sh`).
The counter that scores L6 measures **five**:

```
$ sed -n '19p;55,59p' census/round-39/c2-counter.py
  L6  five consumer fixtures stay green and none loses a passing case against the base bytes.
    ("r38-drift-record", "tests/fixtures/r38-drift-record.py", DRIFT, "--tool"),
    ("r36-worktree-drift", "tests/fixtures/r36-worktree-drift.py", DRIFT, "--tool"),
    ("r38-drift-envelope", "tests/fixtures/r38-drift-write-envelope.py", DRIFT, "--tool"),
    ("r37-citation", "tests/fixtures/r37-citation-reconcile.py", CITATION, "--tool"),
    ("r38-citation-commit", "tests/fixtures/r38-citation-commit.py", CITATION, "--tool"),
```

`r27-pre-report-gate.sh` has no `CONSUMERS` row and no `--tool` flag, so L6 can print
`pass=6` while never executing the sixth fixture the frozen predicate names. The counter's own
docstring agrees with the code ("five") and therefore disagrees with the frozen prereg ("six").
This is a calibration gap between the frozen leg text and the counter that scores it, not a
fixture failure: the sixth fixture is green by hand (section 6, and base-arm row 6, whose tool is
byte-identical to HEAD's `tools/souji-pre-report-gate.sh`, sha256 `acdb8816...7ae66`). Whether the
counter is amended or the prereg reading is corrected is the L1's call; this seat did not edit
`census/round-39/c2-counter.py`.

## Risks / blockers

- None for the six measurements; all six are green and all six are unchanged against base.
- The lane worktree was being written concurrently by sibling seats during the run. My readings are
  pinned to the tool bytes hashed above (worktree == HEAD c0b007b4) and to the fixture blobs whose
  base and worktree hashes are equal; re-running after further sibling edits to
  `tools/souji-{worktree-drift,citation-reconcile}.py` would need a fresh hash check.
- Scratch tree still on disk: `/fast/scratch/hyaku/souji-r39/W1ExecConsumers` (contains
  `base/`, `baselane/`, and the `.out`/`.err` receipts quoted above). Retained deliberately as
  evidence; safe to delete.

## Checks the L1 should run post-integration

```
python3 -B census/round-39/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev <landing> --base-rev ed30b7f5b77939c9073348d810730bc4f355708d
```

and, to confirm the sixth consumer the counter omits:

```
TMPDIR=/fast/scratch/hyaku/souji-r39/<seat> bash tests/fixtures/r27-pre-report-gate.sh
```
