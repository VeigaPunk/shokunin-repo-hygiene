# MutPath — C1 counter mutation probe (round 22, attempt 2)

Executed 2026-10-25. Read-only against the lane; no repo copy, index, `.ufo/state`,
`.ufo/watchdog.log`, or sibling repo was written. No tool installed.

## Target

Assignment named `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/souji-declared-evidence.py`
(else `impl-b`). At probe time **neither** `evidence/impl-a/` nor `evidence/impl-b/` existed
(`ls` -> `No such file or directory`, twice: 03:45 and at mutation time). Baseline bytes were
therefore taken from the candidate that is committed in the lane:

    tools/souji-declared-evidence.py
    sha256 58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2
    git log -1: a211e4d1bf6ea592670d16269f34e9f67f33e8b3 round-22: declared-evidence audit tool, assimilation entries and gate checker

Copied byte-identically (verified with `cmp`, `CMP-IDENTICAL`) to
`evidence/MutPath-work/baseline.py`. All mutation happened only on copies; the repo file was
never edited (post-probe `git status --porcelain tools/souji-declared-evidence.py` is empty).

## Detector

The tool's own frozen detector: `python3 -B <tool> --selftest` (the 5 frozen fixtures of the
preregistration plus its correct-digest control, the always-zero FALSE-GREEN control, and the
skipped-accounting fixture). Baseline must be green first.

### Baseline (pristine bytes) — PASS, rc=0

```
PASS fixture1 all-good -> 0 [assertions=2 resolved=2 skipped=0 mismatches=0]
PASS fixture2 absent path -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture3 dangling rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture4 wrong digest -> mismatch [assertions=3 resolved=2 skipped=0 mismatches=1]
PASS fixture5 path only at other rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture6 correct digest -> resolved [assertions=3 resolved=3 skipped=0 mismatches=0]
PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
PASS fixture7 command span -> skipped, not asserted [assertions=0 resolved=0 skipped=1 mismatches=0]
selftest=8/8
```

Baseline is green, so any mutant failure below is attributable to the mutation.

## M1 — class A accepts a path absent at `--rev`

Smallest behaviour-bearing point: the terminal `mismatch:path-absent` return of class A's
non-glob branch in `evaluate()` (baseline line 155). Mutation diff
(`m1.diff`, baseline `58ddbff…` -> mutant `8b22175aba78e11607063d01b6341a84d941795893a137f9f91a2c58f3a2929b`):

```diff
--- baseline.py
+++ m1.py
@@ -152,7 +152,7 @@
                 else ("mismatch:path-absent", "glob matches nothing at %s" % a["rev"])
         if repo.path_present(a["rev"], a["path"]):
             return "resolved", "present at %s" % a["rev"]
-        return "mismatch:path-absent", "not in tree at %s" % a["rev"]
+        return "resolved", "not in tree at %s" % a["rev"]
     if cls == "B":
         if repo.rev_ok(a["token"]):
```

Detector run — `rc=1`, `selftest=6/8`:

```
PASS fixture1 all-good -> 0 [assertions=2 resolved=2 skipped=0 mismatches=0]
FAIL fixture2 absent path -> mismatch [assertions=2 resolved=2 skipped=0 mismatches=0]
PASS fixture3 dangling rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture4 wrong digest -> mismatch [assertions=3 resolved=2 skipped=0 mismatches=1]
FAIL fixture5 path only at other rev -> mismatch [assertions=2 resolved=2 skipped=0 mismatches=0]
PASS fixture6 correct digest -> resolved [assertions=3 resolved=3 skipped=0 mismatches=0]
PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
PASS fixture7 command span -> skipped, not asserted [assertions=0 resolved=0 skipped=1 mismatches=0]
selftest=6/8
```

**Verdict: KILLED.** The required detector fires exactly on `fixture2 absent path` (mismatches
collapsed 1 -> 0, rc 1 -> 0). Fixture 5 (path only at the other revision) fires as collateral,
so the class-A false-green is anchored twice.

## M2 — `skipped` absorbs the digest mismatch

Mutated the `run()` tally so a `mismatch:digest` increments the skipped counter instead of the
mismatch counter (baseline lines 179-180). Diff (`m2.diff`, mutant
`51ed8bf0589b9be1db9dd3d7cca0df2aaae49f8cf9845a38e97350e458723f8e`):

```diff
--- baseline.py
+++ m2.py
@@ -177,7 +177,10 @@
         if observed == "resolved":
             resolved += 1
         elif observed.startswith("mismatch"):
-            mism += 1
+            if observed == "mismatch:digest":
+                skipped += 1
+            else:
+                mism += 1
         else:
             skipped += 1
         if fmt == "tsv":
```

Detector run — `rc=1`, `selftest=7/8`:

```
PASS fixture1 all-good -> 0 [assertions=2 resolved=2 skipped=0 mismatches=0]
PASS fixture2 absent path -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture3 dangling rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
FAIL fixture4 wrong digest -> mismatch [assertions=3 resolved=2 skipped=1 mismatches=0]
PASS fixture5 path only at other rev -> mismatch [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS fixture6 correct digest -> resolved [assertions=3 resolved=3 skipped=0 mismatches=0]
PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
PASS fixture7 command span -> skipped, not asserted [assertions=0 resolved=0 skipped=1 mismatches=0]
selftest=7/8
```

**Verdict: KILLED.** `fixture4 wrong digest -> mismatch` catches it: it requires
`rc == 1 and "mismatches=1" in line`, while the mutant prints
`assertions=3 resolved=2 skipped=1 mismatches=0` and would exit 0. **No coverage hole**: the
exact fixture the task asked for already exists (fixture 4) and fires.

## Direct counter probe (independent fixture, same shape as `_fixture_repo`)

Built a throwaway git repo under `/var/tmp` outside the lane, ran the real `--format counts`
entry point for each tool on three declarations, then removed the fixture. Transcript
(`direct-counter-probe.txt`):

```
baseline  absent      rc=1  assertions=2 resolved=1 skipped=0 mismatches=1
baseline  digest-bad  rc=1  assertions=3 resolved=2 skipped=0 mismatches=1
baseline  digest-good rc=0  assertions=3 resolved=3 skipped=0 mismatches=0
m1        absent      rc=0  assertions=2 resolved=2 skipped=0 mismatches=0
m1        digest-bad  rc=1  assertions=3 resolved=2 skipped=0 mismatches=1
m1        digest-good rc=0  assertions=3 resolved=3 skipped=0 mismatches=0
m2        absent      rc=1  assertions=2 resolved=1 skipped=0 mismatches=1
m2        digest-bad  rc=0  assertions=3 resolved=2 skipped=1 mismatches=0
m2        digest-good rc=0  assertions=3 resolved=3 skipped=0 mismatches=0
```

This confirms both false-greens at the counter level (exit 0 on a bad declaration), i.e. the
mutations are not cosmetic: they would green-light C1.

## Corroboration on real bytes (read-only)

    python3 -B baseline.py --root . --file SCORECARD.md --rev HEAD --format counts
    assertions=56 resolved=56 skipped=36 mismatches=0
    rc=0

## Restoration evidence

Mutant copies deleted (`rm -f m1.py m2.py`); workdir retains only baseline + transcripts + diffs.

    sha256sum tools/souji-declared-evidence.py evidence/MutPath-work/baseline.py
    58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2  tools/souji-declared-evidence.py
    58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2  evidence/MutPath-work/baseline.py
    git status --porcelain tools/souji-declared-evidence.py SCORECARD.md   # empty

Baseline bytes are identical to the committed tool before and after the probe; the repo copy
was never modified.

### Untracked `tools/__pycache__/` (not produced here)

At 03:46 an untracked `tools/__pycache__/` appeared holding
`souji-declared-evidence.cpython-314.pyc` (03:46:11) and
`souji-landing-gate.cpython-314.pyc` (03:46:49). It is not attributable to this probe: every
invocation used `python3 -B`, and a control run in a temp dir confirms `-B` and plain script
execution both write no bytecode:

```
after -B run: somescript.py
after plain run: somescript.py
after -B import: modx.py
```

A `.pyc` named after the module (not `__main__`) requires a non-`-B` *import*; this probe never
imported either tool. Left untouched.

## Bounded findings

1. Both mutants preserve `assertions == resolved + skipped + mismatches` (M1: 2=2+0+0;
   M2: 3=2+1+0). The printed counter line is therefore **not self-verifying**: an accounting
   mass-balance check cannot detect either defect. The `--selftest` semantic fixtures are the
   only detector, which is what the frozen kill rule assumes.
2. M1 is caught by two fixtures (2 and 5); M2 by one (4). Coverage of the digest class rests on
   a single fixture, but it does fire, so no fixture needs adding.
3. `fixture4` asserts both the exit code and the literal `mismatches=1`, so an escape that only
   moves the count (exactly M2) is still caught. It would *not* catch a mutant that kept
   `mismatches=1` but exited 0 — no such mutant was in scope.
4. The assignment's named target (`impl-a`/`impl-b` under `evidence/`) was absent; the probe used
   the committed lane tool instead. If those executor copies later diverge from `58ddbff…`,
   this kill result does not transfer and the probe must be re-run on the diverged bytes.
