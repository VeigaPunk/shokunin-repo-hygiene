STATUS: PASS

# MutPath — C1 counter mutation probe

Lane: round 22 / attempt 2 (hyaku), workspace/repo hygiene. Scope: challenge the C1
declared-evidence counter with one plausible defect per mutation, run the same bounded detector
on pristine/mutated/restored bytes. All actions read-only against the lane; no repo file, index,
`.ufo/state`, `.ufo/watchdog.log`, or credential was written. No tool installed.

Target resolution (executed): the assignment's named copy
`.ufo/waves/round-22/attempt2/w1/evidence/impl-a/souji-declared-evidence.py` (else `impl-b`) did
**not exist** at either check:

    ls: cannot access '.../evidence/impl-a': No such file or directory
    ls: cannot access '.../evidence/impl-b': No such file or directory

Baseline therefore = the committed lane candidate, copied byte-identically to my evidence dir
(`cmp` -> `CMP-IDENTICAL`):

    tools/souji-declared-evidence.py   sha256 58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2
    git log -1: a211e4d1bf6ea592670d16269f34e9f67f33e8b3 round-22: declared-evidence audit tool, ...

## Detector baseline (pristine) — PASS

`python3 -B baseline.py --selftest` -> rc=0, `selftest=8/8`
(fixture1 all-good 0; fixture2 absent path 1; fixture3 dangling rev 1; fixture4 wrong digest 1;
fixture5 path only at other rev 1; fixture6 correct digest 0; control FALSE-GREEN-REJECTED;
fixture7 skipped accounting). A green baseline is the precondition for attributing kills.

## M1 — class A accepts a path absent at `--rev` — **KILLED**

Diff (baseline 58ddbff… -> mutant 8b22175a…), one line, `evaluate()` terminal class-A return:

```diff
-        return "mismatch:path-absent", "not in tree at %s" % a["rev"]
+        return "resolved", "not in tree at %s" % a["rev"]
```

Detector: `rc=1`, `selftest=6/8`:

    PASS fixture1 all-good -> 0             [assertions=2 resolved=2 skipped=0 mismatches=0]
    FAIL fixture2 absent path -> mismatch   [assertions=2 resolved=2 skipped=0 mismatches=0]
    PASS fixture3 dangling rev -> mismatch  [assertions=2 resolved=1 skipped=0 mismatches=1]
    PASS fixture4 wrong digest -> mismatch  [assertions=3 resolved=2 skipped=0 mismatches=1]
    FAIL fixture5 path only at other rev -> [assertions=2 resolved=2 skipped=0 mismatches=0]
    PASS fixture6 correct digest -> resolved[assertions=3 resolved=3 skipped=0 mismatches=0]
    PASS control always-zero -> FALSE-GREEN-REJECTED
    PASS fixture7 command span -> skipped
    selftest=6/8

The required `nonexistent path` detector fires (mismatches 1 -> 0, rc 1 -> 0); fixture5 fires as
collateral. Killed.

## M2 — digest mismatch counted as `skipped` — **KILLED, no coverage hole**

Diff (baseline 58ddbff… -> mutant 51ed8bf0…), in `run()`:

```diff
         elif observed.startswith("mismatch"):
-            mism += 1
+            if observed == "mismatch:digest":
+                skipped += 1
+            else:
+                mism += 1
```

Detector: `rc=1`, `selftest=7/8`:

    FAIL fixture4 wrong digest -> mismatch  [assertions=3 resolved=2 skipped=1 mismatches=0]
    (all other checks PASS)  selftest=7/8

`fixture4` requires `rc == 1 and "mismatches=1" in line`; the mutant prints
`skipped=1 mismatches=0` and exits 0. **The frozen fixture already exists and catches it**, so no
fixture needs adding.

Independent counter-level confirmation (same-shape fixture repo outside the lane, removed after):
`m1` on an absent path -> `rc=0 assertions=2 resolved=2 skipped=0 mismatches=0`; `m2` on a bad
digest -> `rc=0 assertions=3 resolved=2 skipped=1 mismatches=0`; baseline -> `rc=1` on both. Both
mutations would green-light C1, so neither is cosmetic.

## Restoration

Mutants deleted; baseline hash unchanged (58ddbff…), repo copy untouched
(`git status --porcelain tools/souji-declared-evidence.py` empty).
An untracked `tools/__pycache__/` did appear at 03:46 during the wave (pycs for
`souji-declared-evidence` and `souji-landing-gate`); it is **not** mine — every invocation here
used `python3 -B`, and an executed script never caches its own module, so those pycs come from
another seat importing the tools without `-B`. Left in place, untouched. Workdir retains
`baseline.py`, `baseline-selftest.txt`, `m1-selftest.txt`, `m2-selftest.txt`, `m1.diff`,
`m2.diff`, `direct-counter-probe.txt`. Full transcript: `evidence/MutPath.md`.

## Findings (bounded)

1. **Executed**: both mutants preserve `assertions == resolved + skipped + mismatches`
   (M1 2=2+0+0, M2 3=2+1+0). The counter line is not self-verifying; a downstream
   mass-balance check would pass both. Only the semantic `--selftest` fixtures detect them —
   which is exactly what the frozen kill rule relies on.
2. **Executed**: class A is double-anchored (fixtures 2 and 5); the digest class is anchored by
   exactly one fixture (4), but that one fires, so coverage is adequate as frozen.
3. **Executed (read-only corroboration)**: on real bytes at HEAD,
   `baseline.py --root . --file SCORECARD.md --rev HEAD --format counts` ->
   `assertions=56 resolved=56 skipped=36 mismatches=0`, rc=0.
4. **Scope caveat**: the assignment's `impl-a`/`impl-b` copies were absent; the probe used the
   committed tool. If those executor copies land with different bytes than `58ddbff…`, this kill
   result does not transfer and must be re-run against them.
5. **Source-inferred**: fixture4 checks both rc and the literal `mismatches` token, so a mutant
   keeping `mismatches=1` while exiting 0 would survive — out of scope for the two assigned
   mutations and not exercised.

No run was skipped; no verdict beyond killed/survived/inconclusive is asserted. Nothing was
cleaned up outside my evidence dir; no deletion authority was created.

Report: .ufo/waves/round-22/attempt2/w1/MutPath.md
