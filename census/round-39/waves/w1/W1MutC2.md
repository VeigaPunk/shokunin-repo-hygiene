# W1MutC2 — mutation probe of `census/round-39/c2-counter.py` (r39 C2)

Seat: mutation-tester, lane `souji-shokunin`. Advisory: the L1 integrates.
Instruction: mutate `census/round-39/c2-counter.py` at four points (L1 rc-only, L5 base-arm floor
dropped, L6 harm check removed, L4 class token case-insensitive), run each mutant at base
`ed30b7f5b77939c9073348d810730bc4f355708d`, and report which legs change verdict.

Scratch: `/fast/scratch/hyaku/souji-r39/W1MutC2` (created with `mkdir -p`, passed as `--scratch` and
`TMPDIR`; removed at the end of this seat — see §7). No lane byte was mutated: every mutant is a
copy in scratch; the lane counter's sha256 is identical before and after (§7).

## 1. Instrument identity

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum census/round-39/c2-counter.py
326caa16224605bb0cbfc9a62f0d9ce39f6c9df729b0829a589a1a0bee39a781  census/round-39/c2-counter.py
$ git show b769bfb:census/round-39/c2-counter.py | sha256sum
326caa16224605bb0cbfc9a62f0d9ce39f6c9df729b0829a589a1a0bee39a781  -
$ git status --porcelain census/round-39/c2-counter.py tools/ tests/fixtures/     # empty
$ git log --oneline -1 -- census/round-39/c2-counter.py
b769bfb round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
$ git cat-file -e ed30b7f5b77939c9073348d810730bc4f355708d:census/round-39/c2-counter.py
fatal: path 'census/round-39/c2-counter.py' exists on disk, but not in 'ed30b7f5b77939c9073348d810730bc4f355708d'
rc=128
```

Verdict: the counter under test is byte-identical to the freeze commit's bytes
(`326caa16…`), and it does not exist at the base revision — so the instrument is carried by the
freeze commit while the *audited tool bytes* come from `--rev`. Mutating the worktree copy is
therefore equivalent to mutating the frozen instrument. **PASS.**

Lane state read-only: `git rev-parse HEAD` = `2201778e7736af82e7d8a42dec2494f115bf3923` (landing
candidate); `git status --porcelain --untracked-files=no` empty.

## 2. Control arms (pristine bytes) — the two-arm baseline

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && cp census/round-39/c2-counter.py \
    /fast/scratch/hyaku/souji-r39/W1MutC2/pristine.py && sha256sum "$S/pristine.py"
326caa16224605bb0cbfc9a62f0d9ce39f6c9df729b0829a589a1a0bee39a781  .../pristine.py
$ TMPDIR=$S python3 -B "$S/pristine.py" --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) \
  r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=7ab7c3d85a81
rc=1
```

```
$ TMPDIR=$S python3 -B "$S/pristine.py" --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) \
  r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
rc=0
```

Base arm = `pass=2 fail=4` (matches the frozen control's verdict shape and its kill rule: the base
arm is *not* `pass=6`). Landing arm = `pass=6 fail=0 harm=0`, rc 0.

Two deviations from the frozen receipt `census/round-39/records/c2-before.txt` are recorded, not
scored here (fixture bytes are the instrument's inputs, not its claims):

```
$ cat census/round-39/records/c2-before.txt
... LEG L5 FAIL new=(8, 5, 3, 1) old=(8, 5, 3, 1)
... SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=c142c1bc28b8
$ git log --oneline -- tests/fixtures/r39-citation-rev.py
bbd9b97 round-39: C2 — resolve --rev/--register-rev (exit 2), drift RECORD-MISSING/MALFORMED contract, r39-citation-rev fixture
b769bfb round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
$ git show b769bfb:tests/fixtures/r39-citation-rev.py | sha256sum ; sha256sum tests/fixtures/r39-citation-rev.py
c142c1bc28b8292fec936257074608ff62d92035b84c5db4be7884c6971a7ea2  -
7ab7c3d85a81bfa175262af1f756d697276876f666e00eefa86a787104202e55  tests/fixtures/r39-citation-rev.py
$ git diff --stat b769bfb..HEAD -- census/round-39 tools | tail -3
 census/round-39/preregistration.txt |  9 +++++++++
 tools/souji-citation-reconcile.py   | 38 ++++++++++++++++++++++++++++++++++---
 tools/souji-worktree-drift.py       |  8 +++++---
```

Observation (operability, non-blocking): the receipt's L5 tuple `(8,5,3,1)` and `fixture_sha=c142c1bc28b8`
were measured against the freeze fixture; amendment A1 (`bbd9b97`) rewrote that fixture (now
`7ab7c3d85a81…`), so the same base bytes now read `(8,4,4,1)`. C2's L5 floor (`old_f[2] >= 2`) still
holds at 4, so the claim is unaffected; the receipt just no longer reproduces digit-for-digit. The
receipt itself is frozen and was not edited (`sha256 d75d8c63…` == committed bytes).

## 3. Mutants (single behaviour-bearing point each)

Built by copy + one exact-string replacement in scratch, asserting exactly one occurrence:

```
$ diff -U0 pristine.py <mutant>            (rc 1 = differences present, expected)
--- m1-l1-rc-only.py      @@ -189 +189 @@
-        new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr
+        new_ok = new_p.returncode == 2
--- m2-l5-base-floor.py   @@ -245 +245 @@
-            and old_f is not None and old_f[2] >= 2
+            and old_f is not None and old_f[2] >= 0
--- m3-l6-no-harm.py      @@ -268,3 +267,0 @@
-            if new_r[1] < old_r[1]:
-                harm += 1
-                consumer_ok = False
--- m4-l4-ci-class.py     @@ -142 +142 @@
-            if stripped.startswith(cls) and cls not in out:
+            if stripped.lower().startswith(cls.lower()) and cls not in out:
```

| id | sha256 | point |
|---|---|---|
| M1 `m1-l1-rc-only.py` | `6045b72c92a361f85abda392d4ac3bf0ec4bcb598dfdb36a3923ad7814e86265` | L1 `new_ok` drops the class check |
| M2 `m2-l5-base-floor.py` | `cc3c5cf4dad61e5bcf9fda6e862d51b3da3f48d8322956c99ab59ae30bc98196` | L5 base arm floor `>= 2` → `>= 0` |
| M3 `m3-l6-no-harm.py` | `505e91da09b55ae08657ab12312d8b774835885261cdd7c66dbc89494cb91adf` | L6 harm counter removed |
| M4 `m4-l4-ci-class.py` | `0fdef3e731e0690fb5dbb0a342aa641718fa69470c1877881406fc1d2b17ba3b` | L4 class-token match made case-insensitive |

## 4. Assigned run — each mutant at base `ed30b7f`

Exact command per mutant:

```
$ TMPDIR=$S python3 -B "$S/<mutant>.py" --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"
```

Observed, all four mutants (each ran to completion; output identical between mutants):

```
LEG L1 FAIL new rc=1 class=False old rc=1 class=False
LEG L2 FAIL new rc=1 class=False old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=False old_maps=False
LEG L5 FAIL new=(8, 4, 4, 1) old=(8, 4, 4, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=56866ea8f832/14e9c0f77d7e fixture_sha=7ab7c3d85a81
rc=1
```

**Verdict at the base arm: 0 of 4 mutants killed; no leg changes verdict.** L1, L2, L4, L5 already
read FAIL at the base revision (the base tool bytes are the defect), L3 and L6 already read PASS.
The four mutations all *loosen* a predicate, and loosening cannot flip an already-FAIL leg, so the
base arm is structurally blind to them. `SUMMARY pass=2 fail=4 harm=0` is byte-equal to the pristine
base control, so a mutant counter is indistinguishable from the frozen one on this arm.

## 5. Complementary arm — same mutants at the landing revision

Added because §4 is a null result: an all-green arm is where loosening is cheapest to hide.

```
$ TMPDIR=$S python3 -B "$S/<mutant>.py" --root /home/vgpnk/Projects/shokunin/souji-shokunin \
    --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --base-rev ed30b7f5b77939c9073348d810730bc4f355708d --scratch "$S"
```

Observed, all four mutants identical to the pristine landing arm:

```
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=False
LEG L5 PASS new=(8, 8, 0, 0) old=(8, 4, 4, 1)
LEG L6 PASS ... r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
rc=0
```

**Verdict: 0 of 4 mutants killed; no leg changes verdict, neither exit status (rc 0) nor any
SUMMARY digit changes.** All four mutants therefore **survive both frozen arms**. This is a
coverage finding about the frozen instrument, not a permission to change the contract.

## 6. Discriminating probe — the property each mutant violates

Each mutant was tested against the crafted input that its loosened predicate admits and the frozen
predicate rejects, by extracting the exact predicate / function / loop body from each file and
executing it with that input (`/fast/scratch/hyaku/souji-r39/W1MutC2/probe.py`, sha256
`5c1896252f0cd2f240eee5fa88fe810a79e14a9f28076953d7d29d4d2259f78a`; it re-uses `ast` source segments
of the file under test, so the executed code is the mutant's own bytes, not a paraphrase):

```
$ cd "$S" && python3 "$S/probe.py" "$S/pristine.py" "$S/m1-l1-rc-only.py" "$S/m2-l5-base-floor.py" "$S/m3-l6-no-harm.py" "$S/m4-l4-ci-class.py"
=== pristine.py
  P1 L1 predicate: new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr    -> new_ok=False (rc=2, no REV-UNRESOLVED token)
  P2 L5 ok with base arm green (old_f=8/8) -> ok=False
  P4 docstring_classes('RECORD-MISSING: the record path cannot be read') -> {'RECORD-MISSING': 'RECORD-MISSING: the record path cannot be read'}
  P4 docstring_classes('record-missing: the record path cannot be read') -> {}
  P3 L6 new=(10, 10, 0, 0) base=(10, 10, 0, 0) -> consumer_ok=True harm=0
  P3 L6 new=(10, 9, 1, 1) base=(10, 10, 0, 0) -> consumer_ok=False harm=1
=== m1-l1-rc-only.py
  P1 L1 predicate: new_ok = new_p.returncode == 2                                         -> new_ok=True (rc=2, no REV-UNRESOLVED token)
  P2 L5 ok with base arm green (old_f=8/8) -> ok=False
  P4 docstring_classes('RECORD-MISSING: the record path cannot be read') -> {'RECORD-MISSING': 'RECORD-MISSING: the record path cannot be read'}
  P4 docstring_classes('record-missing: the record path cannot be read') -> {}
  P3 L6 new=(10, 10, 0, 0) base=(10, 10, 0, 0) -> consumer_ok=True harm=0
  P3 L6 new=(10, 9, 1, 1) base=(10, 10, 0, 0) -> consumer_ok=False harm=1
=== m2-l5-base-floor.py
  P1 L1 predicate: new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr    -> new_ok=False (rc=2, no REV-UNRESOLVED token)
  P2 L5 ok with base arm green (old_f=8/8) -> ok=True
  P4 docstring_classes('RECORD-MISSING: the record path cannot be read') -> {'RECORD-MISSING': 'RECORD-MISSING: the record path cannot be read'}
  P4 docstring_classes('record-missing: the record path cannot be read') -> {}
  P3 L6 new=(10, 10, 0, 0) base=(10, 10, 0, 0) -> consumer_ok=True harm=0
  P3 L6 new=(10, 9, 1, 1) base=(10, 10, 0, 0) -> consumer_ok=False harm=1
=== m3-l6-no-harm.py
  P1 L1 predicate: new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr    -> new_ok=False (rc=2, no REV-UNRESOLVED token)
  P2 L5 ok with base arm green (old_f=8/8) -> ok=False
  P4 docstring_classes('RECORD-MISSING: the record path cannot be read') -> {'RECORD-MISSING': 'RECORD-MISSING: the record path cannot be read'}
  P4 docstring_classes('record-missing: the record path cannot be read') -> {}
  P3 L6 new=(10, 10, 0, 0) base=(10, 10, 0, 0) -> consumer_ok=True harm=0
  P3 L6 new=(10, 9, 1, 1) base=(10, 10, 0, 0) -> consumer_ok=False harm=0
=== m4-l4-ci-class.py
  P1 L1 predicate: new_ok = new_p.returncode == 2 and "REV-UNRESOLVED" in new_p.stderr    -> new_ok=False (rc=2, no REV-UNRESOLVED token)
  P2 L5 ok with base arm green (old_f=8/8) -> ok=False
  P4 docstring_classes('RECORD-MISSING: the record path cannot be read') -> {'RECORD-MISSING': 'RECORD-MISSING: the record path cannot be read'}
  P4 docstring_classes('record-missing: the record path cannot be read') -> {'RECORD-MISSING': 'record-missing: the record path cannot be read'}
  P3 L6 new=(10, 10, 0, 0) base=(10, 10, 0, 0) -> consumer_ok=True harm=0
  P3 L6 new=(10, 9, 1, 1) base=(10, 10, 0, 0) -> consumer_ok=False harm=1

Per leg, the property a correct implementation must hold that the mutant does not:

- **L1** — the leg must require the *refusal class* on stderr (`REFUSAL REV-UNRESOLVED`), not merely
  exit status 2. Exit 2 is the tool's generic could-not-evaluate code and is also reached by other
  refusal classes (L3 itself requires rc 2 for `--register-rev`); a rc-only predicate passes a tool
  that exits 2 for an unrelated refusal without ever resolving `--rev`. Evidence: with
  `rc=2, stderr="REFUSAL REGISTER-UNRESOLVED: …"` frozen → `False`, M1 → `True`.
- **L5** — the leg must require that the *base* bytes fail the new fixture (frozen floor `>= 2`).
  A fixture the do-nothing implementation already passes cannot discriminate anything; the frozen
  kill rule exists for exactly this. Evidence: with `new_f=(8,8,0,0)` and `old_f=(8,8,0,0)` (base arm
  green) frozen → `False`, M2 → `True`.
- **L6** — the leg must count a consumer that loses *passing* cases against base as harm and refuse
  to certify (`harm += 1`). Evidence: with `new=(10,9,1,1)`, `base=(10,10,0,0)` frozen → `harm=1`,
  M3 → `harm=0`. Same-run limit worth recording: in this harness `consumer_ok` is `False` in both
  versions (the green check `new_r[0] == new_r[1] and new_r[2] == 0` also fires, and any pair with
  `new_r[1] < old_r[1]` shares the same case count so it is never green), so M3 cannot change any
  leg verdict or the exit status; its only observable is the `harm=` digit in `SUMMARY`. The
  property the frozen instrument does *not* enforce at verdict level: harm must be independently
  fatal, or the redundancy must be declared — as written, deleting it costs no verdict.
- **L4** — the leg's class-token match must stay case-sensitive, because the tool emits the
  uppercase class constants and the documented mapping is about that literal token. A
  case-insensitive match certifies a docstring that never spells the class as emitted
  (`record-missing: …`), i.e. a renamed or re-cased class still returns `new_maps=True`. Evidence:
  `docstring_classes("record-missing: …")` frozen → `{}` (L4 `new_maps=False`), M4 →
  `{'RECORD-MISSING': 'record-missing: …'}` (L4 `new_maps=True`).

## 7. Restoration evidence

The mutation was never applied to lane bytes; mutants live only in scratch. Verification after all
runs:

```
$ sha256sum census/round-39/c2-counter.py
326caa16224605bb0cbfc9a62f0d9ce39f6c9df729b0829a589a1a0bee39a781  census/round-39/c2-counter.py   # == pre-run, == freeze commit
$ git status --porcelain --untracked-files=no
                                          # empty: no tracked lane byte changed
$ git rev-parse HEAD
2201778e7736af82e7d8a42dec2494f115bf3923  # unchanged
$ git status --porcelain | grep '^??'
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
                                          # pre-existing untracked files, not created by this seat
```

Scratch removed at the end of the seat:

```
$ rm -rf -- /fast/scratch/hyaku/souji-r39/W1MutC2 ; ls /fast/scratch/hyaku/souji-r39/W1MutC2
ls: cannot access '/fast/scratch/hyaku/souji-r39/W1MutC2': No such file or directory
rc=2
```

Tree not left on disk (sibling seat dirs under `souji-r39/` are not mine and were untouched).
No git/jj mutating command was run anywhere; the only git calls were `log`, `show`, `status`,
`rev-parse`, `cat-file`, `diff --stat` inside the lane.

## 8. Verdicts

| check | verdict |
|---|---|
| Instrument identity vs freeze bytes `326caa16…` | PASS |
| Pristine base arm reproduces control verdict shape `pass=2 fail=4` | PASS |
| Pristine landing arm `legs=6 pass=6 fail=0 harm=0`, rc 0 | PASS |
| M1 (L1 rc-only) at base → no leg changes verdict | **SURVIVED** (coverage finding) |
| M2 (L5 base floor dropped) at base → no leg changes verdict | **SURVIVED** (coverage finding) |
| M3 (L6 harm removed) at base → no leg changes verdict | **SURVIVED** (coverage finding; verdict-invisible even with a regression pair) |
| M4 (L4 token case-insensitive) at base → no leg changes verdict | **SURVIVED** (coverage finding) |
| M1–M4 at landing → `pass=6 fail=0 harm=0`, rc 0 unchanged | **SURVIVED** (all four) |
| Discriminating probe separates every mutant from pristine (P1–P4) | PASS |
| Lane bytes restored / untouched | PASS |

Findings for the L1 (advisory):

1. The frozen C2 predicate cannot kill any of these four loosened implementations on either arm:
   the base arm is already FAIL on L1/L2/L4/L5, and the landing arm is all-green, so both arms are
   invariant under loosening. If the round wants the four predicates themselves certified, it needs
   a *third* arm — crafted inputs (this seat's P1–P4) — or the claims must be narrowed to "the
   before/after pair differs as stated", which is all the two arms actually establish.
2. M3 is weaker than the other three: removing L6's harm counter changes no verdict at all, only the
   `harm=` digit, because `new_r[1] < old_r[1]` can never co-occur with a green new arm. The L6 harm
   clause is currently decorative; either it becomes independently fatal or the redundancy is
   declared in the docstring.
3. Receipt non-reproduction: `records/c2-before.txt` records `L5 new=(8,5,3,1) fixture_sha=c142c1bc28b8`;
   the same command today reads `(8,4,4,1) fixture_sha=7ab7c3d85a81` because amendment A1 rewrote the
   fixture at `bbd9b97`. The claim's floor (`>= 2` base failures) still holds (4), but the frozen
   receipt is no longer a reproducible digit-for-digit control — A1 should be accompanied by the
   re-measured base tuple if the L1 wants the receipt to be re-runnable.
