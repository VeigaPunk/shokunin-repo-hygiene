STATUS: PASS

# MutQuote — C2 gate-check mutation probe (round 22, attempt 2)

Scope: mutate `tools/souji-gate-check.py` (the C2 counter named in
`.ufo/waves/round-22/attempt2/preregistration.txt`, C2 "Counter") in an isolated
copy under `.ufo/waves/round-22/attempt2/w1/evidence/mutquote-work/`, one mutation
per run per tasking (M1/M2/M3), detected by the frozen fixture set
(`--selftest`). Lane repo otherwise read-only.

Source artifact: the tasking names
`.ufo/waves/round-22/attempt2/w1/evidence/impl-gate/souji-gate-check.py`, but that
staging directory **does not exist** as of execution
(`ls: cannot access '.../evidence/impl-gate/': No such file or directory`, checked
twice several minutes apart). The probe therefore copied the committed counter at
the lane root, which `git status --porcelain -- tools/` reports unmodified:

```
d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00  tools/souji-gate-check.py
```

Copied byte-exact (`cp -p`) to `mutquote-work/pristine.py`, same sha256.

## Baseline detector (unmutated copy)

Command:
```
python3 -B .ufo/waves/round-22/attempt2/w1/evidence/mutquote-work/pristine.py --selftest
```
Output (rc=0):
```
PASS fixture good -> ok [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-date -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture long-quote -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture quote-absent -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture dangling-source -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-reject -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-gate -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture partial-verdicts -> fail [entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=1]
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=9/9
```
Baseline passes, so every later red line is attributable to the mutation.

## M1 — check 4 becomes substring-of-anything

Change (`diff -u pristine.py m1-quote-anywhere.py`):
```
-            if squash(q) not in body:
+            if squash(q) not in squash(q):  # M1: quote need only be a substring of anything
```
Semantics: the quote is tested for containment in itself, never in the snapshot
named by `snapshot:`, so any quote "appears verbatim" by construction. Snapshot
existence and under-`--snapshot-dir` checks are untouched.

Mutant sha256: `09410e618a79ce85d5bacc1365c81eb624bc28624a3d353ae03121ec4f1cac92`
Command: `python3 -B m1-quote-anywhere.py --selftest` (rc=1)
```
PASS fixture good -> ok [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-date -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture long-quote -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
FAIL fixture quote-absent -> fail [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture dangling-source -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-reject -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-gate -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture partial-verdicts -> fail [entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=1]
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=8/9
```
Verdict: **KILLED** by fixture `quote-absent` (preregistration kill rule fixture 3);
the fixture expected `ok=0`, the mutant reported `ok=1`.

## M2 — check 6 accepts a Gate with zero REJECT rows

Change:
```
-    if not REJECT_RE.search(gate):
+    if not REJECT_RE.search(gate) and False:  # M2: accept a Gate with zero REJECT rows
```
Semantics: the `check6-no-reject` failure is unreachable; the ADMIT requirement and
the per-REJECT-line reason loop are untouched (a Gate with no REJECT lines never
enters that loop).

Mutant sha256: `f3917cf4fde36d3d4785528a419d49c5157abee1f845c7cf717fd06b0ec34f5b`
Command: `python3 -B m2-zero-reject.py --selftest` (rc=1)
```
PASS fixture good -> ok [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-date -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture long-quote -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture quote-absent -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture dangling-source -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
FAIL fixture no-reject -> fail [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-gate -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture partial-verdicts -> fail [entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=1]
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=8/9
```
Verdict: **KILLED** by fixture `no-reject` (preregistration kill rule fixture 5);
expected `ok=0`, mutant reported `ok=1`.

## M3 — a missing verdict row counts as verified

Change:
```
-    verified = sum(1 for i in ids if i in rows)
-    for i in ids:
-        if i not in rows:
-            fails.append("verdict-missing:%s" % i)
+    verified = len(ids)  # M3: a missing verdict row is counted as verified
```
Semantics: `slice_verdicts` equals `slice_total` by construction and the
`verdict-missing:*` failure class disappears, so a partial TSV can reach
`v == t` and `fail == 0`.

Mutant sha256: `efa5bb79544ea3c83b8289a800085aa30ad967a551291f3d7d5f5259bbe55fbf`
Command: `python3 -B m3-missing-counts-verified.py --selftest` (rc=1)
```
PASS fixture good -> ok [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-date -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture long-quote -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture quote-absent -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture dangling-source -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-reject -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-gate -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
FAIL fixture partial-verdicts -> fail [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=8/9
```
Verdict: **KILLED** by the `partial-verdicts` fixture. The mutant's inner `run()`
returned the green line and rc=0 for `verdicts-partial.tsv`; the fixture assertion
requires rc=1 and `slice_verdicts=1` in the line, so the mutant is caught by the
fixture harness rather than by the counter's own exit code.

## Restoration

Mutants were separate copies; the counter and the lane repo were never written.
Post-run verification:
```
d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00  tools/souji-gate-check.py
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=9/9
RESTORE_RC=0
```
`git status --porcelain -- tools/` printed nothing (exit 0), i.e. the committed
counter is byte-identical to the pre-probe state and still scores 9/9.

## Survivors

None. All three mutants were killed by the frozen fixture set; no fixture is
missing for a survivor.

Marked [INFERENCE] (source-read of the fixture bodies, not exercised by a run):
the frozen fixture set contains no case isolating
`check4-snapshot-outside-dir`, `check4-snapshot-missing`,
`check4-no-snapshot-named`, `check3-no-locator`, or
`check6-reject-without-reason`, and every fixture feeds a single entry
(`entries=1`). Mutating those branches alone would therefore not turn any of the
9 fixture lines red. These are coverage observations for a future fixture-set
revision, not survivors of the three assigned mutants, and they do not change any
frozen predicate.

## Observed, not produced by this seat

`git status --porcelain -- tools/` after cleanup reports `?? tools/__pycache__/`
containing only `souji-declared-evidence.cpython-314.pyc`, mtime
2026-10-25 03:46:11.527. Every execution in this probe used `python3 -B`, and the
subject script imports nothing from `souji-declared-evidence.py`, so the bytecode
cache came from another seat running the C1 counter without `-B`. Left in place:
deleting another seat's artifact is outside this seat's authority.

## Non-actions

No tool installed or upgraded. No git/jj write, no commit, no index or `.ufo/state`
write, no process signalling, no deletion outside `mutquote-work/` (which was
removed after this file and the lane report were written).
