# W1RevC3Fixture — r39 w1: case independence of `tests/fixtures/r39-citation-rev.py`

Role: reviewer (advisory; the L1 integrates). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Round 39 wave 1, hyaku run 11. Frozen contract read first:
`census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`), C2 L5 and
amendment A1. Lane base `ed30b7f5b77939c9073348d810730bc4f355708d`; worktree and report measured at
`HEAD = 2201778e7736af82e7d8a42dec2494f115bf3923` (`git diff HEAD` on the two instruments is empty,
so worktree bytes == HEAD bytes).

Instruments under test (sha256, measured):

```
7ab7c3d85a81bfa175262af1f756d697276876f666e00eefa86a787104202e55  tests/fixtures/r39-citation-rev.py
59f1e57d7af02cac675757066fb6fa2629a0153f21c98a62e04b6d3b301d2b73  tools/souji-citation-reconcile.py
```

Scratch (still on disk at finish): `/fast/scratch/hyaku/souji-r39/W1RevC3Fixture` — reduced
one-case fixtures under `reduced/`, the pristine/base/mutant tools, the stubs, and
`reversed-fixture.py`. Nothing outside the lane report path and that scratch dir was written; no
git/jj mutation was run (read-only `git show`, `git rev-parse`, `git diff`, `git log` only).

## Instruments built for this check

`cit-pristine.py` = `tools/souji-citation-reconcile.py` at HEAD.
`cit-base.py` = `git show ed30b7f...:tools/souji-citation-reconcile.py` (the frozen L5 mutant arm).
Eight single-defect mutants of the pristine bytes (`diff -u` against `cit-pristine.py` printed for
each; every one is a single hunk):

| id | single defect | targets |
|---|---|---|
| M1 `cit-m1-anyobject.py` | `cat-file -e "$rev"` instead of `"$rev^{commit}"` (accepts blob/tree) | rev-blob, rev-tree |
| M2 `cit-m2-noregrev.py` | `--register-rev` resolution block deleted | register-rev-gone |
| M3 `cit-m3-shortrev.py` | `REV` regex `{40}` -> `{7,40}` | rev-short |
| M4 `cit-m4-noformat.py` | `--rev` format gate deleted | rev-symbolic, rev-short |
| M5 `cit-m5-absentfallback.py` | register absent at `--register-rev` falls back to the working file | register-absent |
| M6 `cit-m6-dirty.py` | `mismatches += 1` on a clean repo | clean |
| M7 `cit-m7-norows.py` | `rows = []` before the audit loop (audits zero rows) | none (see F1) |
| M8 `cit-m8-norevresolution.py` | `--rev` resolution block deleted, `--register-rev` block kept | rev-unknown, rev-blob, rev-tree |

Stubs: `stub-rc0.py` (prints `SUMMARY cells=0 mismatches=0`, exit 0), `stub-rc0-silent.py` (exit 0,
no output), `stub-rc2-usage.py` (prints `REFUSAL USAGE: stub`, exit 2), `stub-rc2-silent.py` (exit 2,
no output), `stub-rc2-alltokens.py` (prints USAGE + REV-UNRESOLVED + `not at`, exit 2).

## Check 1 — per-case isolation (the assigned matrix)

Command (lane root; one reduced fixture per case, every other `case(...)` call deleted by block
range 106-116 of the fixture):

```
python3 -B reduced/one-<case>.py --tool <instrument> --work /fast/scratch/hyaku/souji-r39/W1RevC3Fixture
```

Full-fixture arms for context, exact output:

```
$ TMPDIR=$S python3 -B tests/fixtures/r39-citation-rev.py --tool $PWD/tools/souji-citation-reconcile.py --work $S
case-rev-unknown=PASS ... case-register-absent=PASS
SUMMARY cases=8 pass=8 fail=0
rc=0

$ TMPDIR=$S python3 -B tests/fixtures/r39-citation-rev.py --tool $S/cit-base.py --work $S
case-rev-unknown=FAIL rc=1 want=2 missing=['REV-UNRESOLVED'] out='MISMATCH K1 FILE-ABSENT doc.md at 1111...'
case-rev-blob=FAIL rc=1 want=2 missing=['REV-UNRESOLVED'] out='MISMATCH K1 FILE-ABSENT doc.md at 0caa...'
case-rev-tree=FAIL rc=1 want=2 missing=['REV-UNRESOLVED'] out='MISMATCH K1 RECEIPT-REV-NOT-ANCESTOR ... SUMMARY cells=1 mismatches=1'
case-rev-short=PASS
case-rev-symbolic=PASS
case-clean=PASS
case-register-rev-gone=FAIL rc=2 want=2 missing=['REV-UNRESOLVED'] out='REFUSAL USAGE: register .../register.tsv is not at 1111...'
case-register-absent=PASS
SUMMARY cases=8 pass=4 fail=4
rc=1
```

Reduced one-case matrix (cell = `case-<name>=PASS|FAIL` / fixture rc; SUMMARY in every reduced run
was `cases=1`, confirming the deletion took effect):

| case | pristine | base | M1 | M2 | M3 | M4 | M5 | M6 | M7 | stub-rc0 | rc0-silent | rc2-usage | rc2-silent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rev-unknown | PASS/0 | **FAIL/1** | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | FAIL/1 | FAIL/1 | FAIL/1 | FAIL/1 |
| rev-blob | PASS/0 | **FAIL/1** | **FAIL/1** | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | FAIL/1 | FAIL/1 | FAIL/1 | FAIL/1 |
| rev-tree | PASS/0 | **FAIL/1** | **FAIL/1** | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | FAIL/1 | FAIL/1 | FAIL/1 | FAIL/1 |
| rev-short | PASS/0 | PASS/0 | PASS/0 | PASS/0 | **FAIL/1** | **FAIL/1** | PASS/0 | PASS/0 | PASS/0 | FAIL/1 | FAIL/1 | PASS/0 | FAIL/1 |
| rev-symbolic | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | **FAIL/1** | PASS/0 | PASS/0 | PASS/0 | FAIL/1 | FAIL/1 | PASS/0 | FAIL/1 |
| clean | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | **FAIL/1** | **PASS/0** | **PASS/0** | FAIL/1 | FAIL/1 | FAIL/1 |
| register-rev-gone | PASS/0 | **FAIL/1** | PASS/0 | **FAIL/1** | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | FAIL/1 | FAIL/1 | FAIL/1 | FAIL/1 |
| register-absent | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | PASS/0 | **FAIL/1** | PASS/0 | PASS/0 | FAIL/1 | FAIL/1 | FAIL/1 | FAIL/1 |

Per-case kill attribution with only that case present (the check the seat asked for):

| case | mutant it is supposed to kill | reduced pristine | reduced mutant | kill observed in isolation |
|---|---|---|---|---|
| rev-unknown | M8 (or base) | PASS | FAIL (`missing=['REV-UNRESOLVED']`, rc 1) | yes |
| rev-blob | M1 (also base, M8) | PASS | FAIL (rc 1) | yes |
| rev-tree | M1 (also base, M8) | PASS | FAIL (rc 1) | yes |
| rev-short | M3 (also M4) | PASS | FAIL `rc=0 want=2 missing=['USAGE'] out='SUMMARY cells=1 mismatches=0 '` | yes |
| rev-symbolic | M4 | PASS | FAIL `rc=2 want=2 missing=['USAGE'] out='REFUSAL REV-UNRESOLVED: --rev v1 does not resolve to a commit '` | yes |
| clean | M6 | PASS | FAIL `rc=1 want=0 missing=['mismatches=0'] out='SUMMARY cells=1 mismatches=1 '` | yes |
| register-rev-gone | M2 (also base) | PASS | FAIL `rc=2 want=2 missing=['REV-UNRESOLVED'] out='REFUSAL USAGE: register .../register.tsv is not at 1111...'` | yes |
| register-absent | M5 | PASS | FAIL `rc=0 want=2 missing=['not at'] out='SUMMARY cells=1 mismatches=0 '` | yes |

No case's kill needs another case. No case passes under the mutant it targets. Full-fixture verdicts
are reproduced exactly by the isolated runs (pristine 8/8 pass; base fails exactly the four cases in
the same four rows).

Order independence (shared `build()`, shared register, no per-case state):

```
$ python3 -B reversed-fixture.py --tool cit-pristine.py --work $S   -> SUMMARY cases=8 pass=8 fail=0   rc=0
$ python3 -B reversed-fixture.py --tool cit-base.py     --work $S   -> SUMMARY cases=8 pass=4 fail=4   rc=1
```

## Check 2 — control arm (seat: `good` must fail under an always-0 / always-2 stub)

The fixture has no case named `good`; the only positive case is `clean` (`--rev <commit>`, want rc 0
+ `mismatches=0`), so `clean` is the control arm measured here.

```
$ python3 -B reduced/one-clean.py --tool stub-rc0.py --work $S
case-clean=PASS
SUMMARY cases=1 pass=1 fail=0
rc=0

$ python3 -B reduced/one-clean.py --tool stub-rc0-silent.py --work $S
case-clean=FAIL rc=0 want=0 missing=['mismatches=0'] out=''
SUMMARY cases=1 pass=0 fail=1
rc=1

$ python3 -B reduced/one-clean.py --tool stub-rc2-usage.py --work $S
case-clean=FAIL rc=2 want=0 missing=['mismatches=0'] out='REFUSAL USAGE: stub '
SUMMARY cases=1 pass=0 fail=1
rc=1

$ python3 -B reduced/one-clean.py --tool stub-rc2-silent.py --work $S
case-clean=FAIL rc=2 want=0 missing=['mismatches=0'] out=''
SUMMARY cases=1 pass=0 fail=1
rc=1
```

`clean` fails the silent always-0 stub and both always-2 stubs, but **passes an always-exit-0 stub
whose only act is printing the expected token** (F1). The full fixture still rejects that stub
(`SUMMARY cases=8 pass=1 fail=7 rc=1`), because the other seven cases require rc 2.

Class-token cheat:

```
$ python3 -B tests/fixtures/r39-citation-rev.py --tool stub-rc2-alltokens.py --work $S
case-rev-unknown=PASS ... case-register-absent=PASS
case-clean=FAIL rc=2 want=0 missing=['mismatches=0'] ...
SUMMARY cases=8 pass=7 fail=1
rc=1
```

Seven of eight cases are satisfied by a constant rc-2 stub that emits the three class tokens; only
`clean` rejects it. `rev-short` and `rev-symbolic` pass under `stub-rc2-usage` individually.

## Check 3 — fixture-level mutant survival

```
$ python3 -B reduced/one-clean.py --tool cit-m7-norows.py --work $S
case-clean=PASS
SUMMARY cases=1 pass=1 fail=0
rc=0

$ python3 -B tests/fixtures/r39-citation-rev.py --tool cit-m7-norows.py --work $S
case-rev-unknown=PASS ... case-register-absent=PASS
SUMMARY cases=8 pass=8 fail=0
rc=0
```

M7 keeps the two refusal gates and audits zero register rows (`SUMMARY cells=0 mismatches=0`). It
passes all eight cases: no case pins the cell count, so the fixture cannot distinguish "audited the
one register row and found no mismatch" from "audited nothing". This is the seat's control-arm
requirement stated as a fixture property.

Strengthened predicate (verified, not applied — the L1 decides):

```
$ sed 's/\["mismatches=0"\], results)/["mismatches=0", "cells=1"], results)/' reduced/one-clean.py > reduced/one-clean-cells1.py
$ python3 -B reduced/one-clean-cells1.py --tool cit-pristine.py --work $S  -> case-clean=PASS  cases=1 pass=1 fail=0
$ python3 -B reduced/one-clean-cells1.py --tool cit-m7-norows.py --work $S -> case-clean=FAIL missing=['cells=1'] cases=1 pass=0 fail=1
$ python3 -B reduced/one-clean-cells1.py --tool stub-rc0.py --work $S      -> case-clean=FAIL missing=['cells=1'] cases=1 pass=0 fail=1
```

## Check 4 — `register-absent` input actually exercised

`case()` appends `--register <scratch>/register.tsv` after the case argv, and `register-absent`'s
argv already carries `--register no-such-register.tsv`; argparse keeps the last value, so the
case's own `--register` is dead. Proof on a fresh synthetic repo (`D=$(mktemp -d ...); git -C "$D"
init -q -b main`; `toplevel` asserted equal to `$D` before the first commit):

```
$ python3 -B tools/souji-citation-reconcile.py --root $D --rev $R --register-rev $R \
      --register no-such-register.tsv --register $S/reg.tsv
REFUSAL USAGE: register /fast/scratch/hyaku/souji-r39/W1RevC3Fixture/reg.tsv is not at 5d58c5d...
rc=2

$ ... --register-rev $R --register no-such-register.tsv
REFUSAL USAGE: register no-such-register.tsv is not at 5d58c5d...
rc=2

$ ... --register-rev $R --register $S/reg.tsv --register no-such-register.tsv
REFUSAL USAGE: register no-such-register.tsv is not at 5d58c5d...
rc=2
```

The case still reaches the `not at` branch and still kills M5, because the substituted path is an
absolute scratch path absent from the tree; it is correct by accident, not by construction.

## Check 5 — frozen C2 predicate at HEAD (context, not my claim)

```
$ python3 -B census/round-39/c2-counter.py --root . --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
      --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch $S
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
rc=0
```

## Findings (by severity)

**F1 — Medium-High. The control arm is satisfied by a no-op auditor; the fixture never asserts
`cells=1`.** `clean`'s predicate is `rc == 0` plus the substring `mismatches=0`. A stub that prints
`SUMMARY cells=0 mismatches=0` and exits 0 passes it, and M7 (a single-line `rows = []` mutant that
audits zero rows while keeping both refusal gates) passes **all eight** cases (`cases=8 pass=8
fail=0 rc=0`). The seat's control requirement ("`good` must fail if the tool is replaced by a stub
that always exits 0") is therefore not met. It does not falsify C2's frozen L5 predicate — the base
bytes still fail 4/8, above the `>=2` floor — but the positive arm does not pin that any row was
audited. Adding `cells=1` to `clean`'s tokens closes the M7 and token-stub escapes (evidence in
Check 3) and costs nothing on the pristine tool.

**F2 — Low. `register-absent`'s own `--register` argument is dead.** `case()` appends the harness
register after argv, so `--register no-such-register.tsv` is overridden (argparse last-wins).
Observed output names `/fast/scratch/.../register.tsv`, not `no-such-register.tsv`. The case's
documented input is not the one executed; the verdict is right only because both paths are absent
at `--register-rev`. Fix: insert the harness `--register` before the case argv, or skip the append
when argv already carries `--register`.

**F3 — Low. `build()` does not assert the fixture repo's toplevel and ignores every git exit
status.** It runs `git init -q -b main <path>` with a path argument (not `-C`), then `-C` for later
calls, and never checks `git -C repo rev-parse --show-toplevel` equals the scratch repo before the
commit. This is the round's own fixture hard rule; a failed init or commit would surface only as a
confusing case failure. `sh()` results are discarded throughout `build()`.

**F4 — Informational. Base-arm coverage is 4/8, as the counter reports.**
`rev-short`, `rev-symbolic`, `clean`, `register-absent` pass on the base bytes; they are guards
against other single defects (M3/M4/M6/M5), not base discriminators. `rev-unknown`, `rev-blob`,
`rev-tree` share one guard, so no single-defect mutant kills exactly one of them (M1 separates
blob/tree from unknown; M8 kills all three). That is expected class structure, not coupling: each
case still fails on its own instrument with all other cases deleted.

## Verdict per check

- **Case independence (pristine arm): PASS** — every case passes in a one-case fixture; the full
  fixture's 8/8 is not carried by any other case.
- **Case independence (mutant arm): PASS** — every case fails in isolation against the mutant it
  targets; no kill requires another case; reversed case order leaves both arms unchanged.
- **Control arm: FAIL** — `clean` passes an always-0 stub that emits its token, and the whole
  fixture passes a zero-row no-op tool (M7). See F1.
- **Frozen C2 L5 predicate at HEAD: PASS** — `new=(8,8,0,0) old=(8,4,4,1)`, base arm fails 4
  (`>=2`), counter `legs=6 pass=6 fail=0 harm=0`.
- **Fixture hygiene: FAIL (low)** — dead `--register` in `register-absent` (F2), unasserted
  toplevel and ignored git statuses in `build()` (F3).

## Residual risk / verification gaps

- My mutant set is hand-built (8 single-defect mutants). It is not exhaustive: a mutant that
  resolves a tree as a commit only in the commit arm, or one that special-cases the fixture's
  synthetic token, was not built. The per-case attribution table is therefore "has a killer", not
  "kills every defect of its class".
- The C2 counter reads the fixture from the worktree (`lane_root_of` returns the worktree root;
  only the two tools come from `--rev`). L5 is therefore not revision-bound to the fixture bytes;
  my numbers are at `HEAD = 2201778` where worktree == HEAD. A landing revision later than HEAD was
  not measured.
- I did not run the C3 battery or the C1 counter; out of this seat's scope.
- Scratch tree kept: `/fast/scratch/hyaku/souji-r39/W1RevC3Fixture` (tools, reduced fixtures,
  stubs, `reversed-fixture.py`, `reg.tsv`). No clone of the lane was made. No mutating git/jj
  command touched the lane or the fleet repo; the only `git init/add/commit` calls ran inside
  mktemp scratch repos under that scratch root, with `git -C "$D" rev-parse --show-toplevel`
  asserted equal to `$D` before the first commit.
