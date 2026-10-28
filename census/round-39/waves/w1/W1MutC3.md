# W1MutC3 — C3 battery kill-rule mutation test (r39 wave 1)

Role: mutation-tester. Target: the C3 kill rule in `census/round-39/c3-counter.py`, scored
against the pristine drift tool and the four C3 mutants at base
`ed30b7f5b77939c9073348d810730bc4f355708d`.

Contract read first: `census/round-39/preregistration.txt` (freeze b769bfb84a264d8b284c09bc211d99f39a3e9126).
C3 predicate under test: `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases>=6`.
KILL RULE quoted from the frozen contract: *"a kill needs the fixture's own `fail>0`, no traceback,
exit 1"*; *"missed if any mutant survives the candidate fixture, if any mutant is killed by the base
fixture (`base_killed` must stay 0), if the pristine control fails, or if the candidate fixture
carries fewer than six cases."*

Scratch (still on disk at finish): `/fast/scratch/hyaku/souji-r39/W1MutC3`.
Tooling: none installed (python3 3.14.8, git present). No `pacman`, no network.

## 0. Byte provenance (and a concurrent landing)

| counter bytes | sha256 | where |
|---|---|---|
| pre-change | `ff18d64c09f48a2ee8fd9502ad8e6d549a92466fd7aad777b31ba7b513d3bcd1` | commit `2201778` |
| tip at finish | `7f934c50b19a5e77562756e8e0467a65942536fdbb0cd12e80f4619151dba7b4` | commit `d4c1755` (working tree == HEAD) |

The first matrix ran on `ff18d64…`; while it ran, the L1 landed
`d4c1755 round-39: C3/scratch — honour the caller's TMPDIR in c3-counter git children …`.
`git diff 2201778 d4c1755 -- census/round-39/c3-counter.py` touches only `child_env()` and the two
`git` call sites (TMPDIR plumbing); `score()`, `MUTANTS`, the pristine arm and the base arm are
byte-identical. The full matrix was therefore re-run from the tip bytes (`c3b-*`) and every output
was compared against the pre-change run (section 5). No lane file was modified by this seat; the
tip counter is reproduced exactly as `c3b-original.py` (same sha256).

Pinned inputs (working tree, unchanged by this seat):

```
567c37a679f52f700ea6d4a001e79e73be2ba1af3b97bd6210849b7b34432a4d  tests/fixtures/r39-drift-record-rules.py
ac0be0e7a49e683cd324ffa485fecb15d11c5636fde55f3244d9776020b021d6  tests/fixtures/r38-drift-record.py
14e9c0f77d7e817df96b8ed656bfc18c879bb838a5036d1b7fc2f864c510d194  tools/souji-worktree-drift.py @ ed30b7f
```

Mutant anchors occur exactly once in the base tool bytes (`grep -Fc` → `1` for the skip line, the
`splitlines` line and the `RECORD-OUTSIDE-ROOT` raise), so M11–M14 apply as the counter intends; no
run printed `MUTANT … ANCHOR-COUNT`.

## 1. The four kill-rule mutations (single-line each, on scratch copies only)

```
$ diff -u c3b-original.py c3b-<variant>.py
```

```
== rc1          (a kill needs only rc==1)
-    killed = proc.returncode == 1 and fails > 0 and not crash
+    killed = proc.returncode == 1
== traceback    (a kill accepts a traceback)
-    killed = proc.returncode == 1 and fails > 0 and not crash
+    killed = proc.returncode == 1 and fails > 0
== nobase       (base_killed is not computed)
-            base_killed, base_detail, _ = score(base_fixture, path, scratch)
+            base_killed, base_detail = False, "not-computed"
== nopristine   (the pristine arm is skipped)
-        if not pristine_ok:
+        if False and not pristine_ok:  # pristine arm skipped
```

Variant hashes: `c3b-rc1.py f7eff1c1b80e…`, `c3b-traceback.py b36912d6da07…`,
`c3b-nobase.py ffdf9ca487fb…`, `c3b-nopristine.py d692bb956350…`; original `7f934c50b19a…`.
The counter's `NO-SUMMARY` early return is left intact in all variants: a fixture that crashes
before printing its `SUMMARY` is `NO-SUMMARY`/not-killed under every rule, including `rc1`.

## 2. The commanded run: pristine tool + four mutants at base

Command (run once per variant, `v` ∈ original, rc1, traceback, nobase, nopristine):

```
S=/fast/scratch/hyaku/souji-r39/W1MutC3
L=/home/vgpnk/Projects/shokunin/souji-shokunin
TMPDIR="$S" python3 -B "$S/c3b-$v.py" --root "$L" \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --base-rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --fixture "$L/tests/fixtures/r39-drift-record-rules.py" \
  --base-fixture "$L/tests/fixtures/r38-drift-record.py" --scratch "$S"
```

Baseline (`c3b-original.py`, rc 0) — this is the C3 after-state measured against the **base** tool:

```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
```

The pristine tool is scored by the same fixture in the pristine arm: `rc=0 fails=0 crash=False`
(all seven cases pass), so no variant kills the pristine arm here.

### Check A — `killed = proc.returncode == 1` (rc1)

Output rc 0, and **byte-identical** to the baseline (`sha256(out2-original.txt) == sha256(out2-rc1.txt)
== 35b3c3632762…`): killed=4, survived=0, base_killed=0, cases=7, same four `MUTANT` lines.
No mutant becomes falsely killed; no control line changes.

Verdict: **SURVIVED by the battery's own output.** The `fails>0` conjunct and the traceback guard
are both dead weight for every input the packaged battery produces.

### Check B — `killed = proc.returncode == 1 and fails > 0` (traceback)

Output rc 0, **byte-identical** to the baseline (`… 35b3c3632762…`). No false kill, no changed line.

Verdict: **SURVIVED by the battery's own output.** The traceback guard alone is undiscriminated.

### Check C — `base_killed` not computed (nobase)

Output rc 0; the four `MUTANT` detail lines change, the `SUMMARY` does **not**:

```
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:not-computed
MUTANT M12 killed=yes base_killed=no rc=1 fails=1 crash=False base:not-computed
MUTANT M13 killed=yes base_killed=no rc=1 fails=1 crash=False base:not-computed
MUTANT M14 killed=yes base_killed=no rc=1 fails=1 crash=False base:not-computed
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=14e9c0f77d7e fixture_sha=567c37a679f5
```

Verdict: **SURVIVED by the frozen predicate** (`base_killed=0` and exit 0 unchanged); the only
observable is the per-mutant `base:` field, which a summary-only reader does not see. Material
falsification in section 4: a base arm that genuinely kills all four is reported as `base_killed=0`.

### Check D — pristine arm skipped (nopristine)

Output rc 0, **byte-identical** to the baseline (`… 35b3c3632762…`). With a pristine that passes,
the gate is unobservable.

Verdict: **SURVIVED by the battery's own output.** Material falsification in section 4: an
always-failing candidate fixture yields `pristine=ok killed=4` and exit 0.

## 3. Which packaged inputs could ever notice? (none)

```
$ grep -rn "c3-counter" "$L" --include=*.py --include=*.sh --include=*.md --include=*.txt --include=*.json --include=*.tsv \
    | grep -v 'census/round-39/c3-counter.py' | grep -v 'corpus/lessons'
```

No round-39 hit: no fixture, test, runner or gate mutates or re-derives the counter; only the
preregistration predicate and the `c3-after.txt` receipt read it, and both read the `SUMMARY` line
and exit code. There is **no self-mutation check of the kill rule** anywhere in the lane.

## 4. Falsification probes: each mutation *can* flip a verdict

### 4a. rc1 / traceback — a crashing fixture after a printed SUMMARY

Fixtures `crash-on-mutant-fail0.py` / `crash-on-mutant-fail1.py`: pass the pristine base tool
(sha256 match), print a green / red `SUMMARY` for any other `--tool` bytes, then raise
(`RuntimeError` → rc 1 + real traceback). Commands as in section 2 with
`--fixture "$S/crash-on-mutant-fail<N>.py"`.

```
counter=original  fixture=fail0  rc=1
MUTANT M11 killed=no base_killed=no rc=1 fails=0 crash=True base:rc=0 fails=0 crash=False
MUTANT M12 killed=no base_killed=no rc=1 fails=0 crash=True base:rc=0 fails=0 crash=False
MUTANT M13 killed=no base_killed=no rc=1 fails=0 crash=True base:rc=0 fails=0 crash=False
MUTANT M14 killed=no base_killed=no rc=1 fails=0 crash=True base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=7 … fixture_sha=68daf4a2e7b3

counter=rc1       fixture=fail0  rc=0
MUTANT M11 killed=yes base_killed=no rc=1 fails=0 crash=True base:rc=0 fails=0 crash=False
… M12/M13/M14 identical …
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 … fixture_sha=68daf4a2e7b3

counter=original  fixture=fail1  rc=1   → killed=no ×4, survived=4 (fixture_sha=c1d2d0b572c5)
counter=rc1       fixture=fail1  rc=0   → killed=yes ×4, survived=0
counter=traceback fixture=fail0  rc=1   → killed=no ×4, survived=4
counter=traceback fixture=fail1  rc=0   → killed=yes ×4, survived=0
```

Result: under `rc1`, **M11–M14 are all falsely killed** by a fixture that prints a green summary
and then crashes; under `traceback`, **M11–M14 are all falsely killed** by a fixture that prints a
red summary and then crashes. The original rule rejects both. (These fixtures are adversarial; the
packaged candidate and base fixtures never crash — every real run shows `crash=False`.)

### 4b. nobase — a base arm that really kills

`--base-fixture "$L/tests/fixtures/r39-drift-record-rules.py"` (the candidate itself, which kills
all four — see `c3-before.txt`: the base control is the r38 fixture bytes `ac0be0e7a49e`, 10 cases,
`killed=0`; the candidate is the one that kills them):

```
counter=original  rc=1
MUTANT M11 killed=yes base_killed=yes rc=1 fails=1 crash=False base:rc=1 fails=1 crash=False
… M12/M13/M14 identical …
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=4 cases=7 …

counter=nobase    rc=0
MUTANT M11 killed=yes base_killed=no rc=1 fails=1 crash=False base:not-computed
… M12/M13/M14 identical …
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 …
```

Result: a genuine `base_killed=4` refusal (exit 1) becomes `base_killed=0` (exit 0). The mutation
does not invent a false *kill*; it erases the base-arm control entirely, so a mutant killed by the
old fixture would be accepted as a clean coverage win.

### 4c. nopristine — a candidate that fails everything

`--fixture "$S/always-fail.py"` (prints `SUMMARY cases=7 pass=0 fail=7`, exit 1, for every tool):

```
counter=original    rc=1
SUMMARY mutants=0 killed=0 survived=0 pristine=FAIL base_killed=0 cases=7

counter=nopristine  rc=0
MUTANT M11 killed=yes base_killed=no rc=1 fails=7 crash=False base:rc=0 fails=0 crash=False
MUTANT M12 killed=yes base_killed=no rc=1 fails=7 crash=False base:rc=0 fails=0 crash=False
MUTANT M13 killed=yes base_killed=no rc=1 fails=7 crash=False base:rc=0 fails=0 crash=False
MUTANT M14 killed=yes base_killed=no rc=1 fails=7 crash=False base:rc=0 fails=0 crash=False
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 … fixture_sha=f2e887afa586
```

Result: **M11–M14 are all falsely killed** by a fixture that fails every tool including the
pristine one; the frozen predicate's green line is printed and exit is 0.

### 4d. Direct `score()` probe (both crash classes, one table)

```
$ python3 -B "$S/probe-kill-rule.py"
c3-original.py | crash0 killed=no rc=1 fails=0 crash=True | crash1 killed=no rc=1 fails=1 crash=True
c3-rc1.py | crash0 killed=yes rc=1 fails=0 crash=True | crash1 killed=yes rc=1 fails=1 crash=True
c3-traceback.py | crash0 killed=no rc=1 fails=0 crash=True | crash1 killed=yes rc=1 fails=1 crash=True
c3-nobase.py | crash0 killed=no rc=1 fails=0 crash=True | crash1 killed=no rc=1 fails=1 crash=True
c3-nopristine.py | crash0 killed=no rc=1 fails=0 crash=True | crash1 killed=no rc=1 fails=1 crash=True
pristine-tool tests/fixtures/r39-drift-record-rules.py killed=no rc=0 fails=0 crash=False cases=7
pristine-tool tests/fixtures/r38-drift-record.py killed=no rc=0 fails=0 crash=False cases=10
```

Isolates the conjunct each mutation removes: `fails>0` is the only guard on `crash0`; the traceback
guard is the only guard on `crash1`; the real fixtures and the pristine tool hit neither branch.

## 5. Stability across the concurrent counter landing

Every real-input and adversarial output was re-run from the tip bytes and compared with the
pre-change run:

```
original   35b3c3632762 == 35b3c3632762 IDENTICAL
rc1        35b3c3632762 == 35b3c3632762 IDENTICAL
traceback  35b3c3632762 == 35b3c3632762 IDENTICAL
nobase     17cfcb3acae4 == 17cfcb3acae4 IDENTICAL
nopristine 35b3c3632762 == 35b3c3632762 IDENTICAL
adv-fail0-original 52fa15104f5d == 52fa15104f5d IDENTICAL
adv-fail0-rc1      22f676a1beed == 22f676a1beed IDENTICAL
adv-fail0-traceback 52fa15104f5d == 52fa15104f5d IDENTICAL
adv-fail1-original da67cc994855 == da67cc994855 IDENTICAL
adv-fail1-rc1      41b37f44be4e == 41b37f44be4e IDENTICAL
adv-fail1-traceback 41b37f44be4e == 41b37f44be4e IDENTICAL
```

The `d4c1755` TMPDIR change does not move any C3 kill-rule verdict.

## 6. Restoration evidence

This seat never wrote lane bytes; the mutations exist only in scratch copies.

```
$ sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c3-counter.py
7f934c50b19a5e77562756e8e0467a65942536fdbb0cd12e80f4619151dba7b4
$ git diff --quiet HEAD -- census/round-39/c3-counter.py && echo "counter: working tree == HEAD (d4c1755)"
counter: working tree == HEAD (d4c1755)
$ git status --porcelain   # unchanged pre-existing entries only
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
```

`c3b-original.py` (scratch) is byte-identical to the lane counter (`7f934c50b19a…`), i.e. the
mutation baseline is the packaged bytes. No counter scratch dirs were left behind
(`ls -d "$S"/souji-r39-c3.*` → none).

## Verdict table

| # | kill-rule mutation | pristine | M11–M14 on the packaged fixtures | SUMMARY/exit | noticed by the battery? |
|---|---|---|---|---|---|
| A | kill = `rc==1` only | pass | killed (correct) | identical, rc 0 | **no** — output byte-identical; false-kills all four only under a crashing fixture |
| B | kill accepts a traceback | pass | killed (correct) | identical, rc 0 | **no** — byte-identical; false-kills all four only under a crashing fixture |
| C | `base_killed` not computed | pass | killed (correct) | SUMMARY identical, rc 0 | **no** by predicate; only `base:not-computed` in the detail line; erases a real `base_killed=4` refusal |
| D | pristine arm skipped | (not run) | killed (correct) | identical, rc 0 | **no** — byte-identical; accepts an always-failing fixture as `killed=4` |

Coverage finding (advisory, not a contract change): the C3 battery cannot detect any of the four
weakenings with its own output. The frozen predicate `SUMMARY … base_killed=0 cases>=6` plus exit 0
is invariant under A, B, C and D; the counter carries no self-test that mutates its kill rule, so
the r38 A5 scoring contract is asserted by code that no in-lane instrument falsifies. The three
false-green paths are (i) a crashing fixture with `fails=0` under A, (ii) a crashing fixture with
`fails>0` under B, (iii) any always-failing fixture under D; and C removes the base-arm control
that `base_killed=0` is supposed to represent.
