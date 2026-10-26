# SwarmReviewer10 — C2 patch review: souji-declared-evidence.py, souji-gate-check.py, souji-rev-pin.py

## Status

STATUS: PASS — the landed C2 change to these three files is exactly the scratch-root fix; guards, refusals, selftest semantics and full stdout are byte-identical to base under both TMPDIR set and unset, and cleanup removes everything it creates (verified empirically).

## Evidence

Diff (only change in scope; `git diff --stat`: 3 files, +7/−4):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 85b61a151923986e7e6b48f7084b9122561b5f3d 98e5203d45b4e419a9e72801733d93303acc7ebd -- tools/souji-declared-evidence.py tools/souji-gate-check.py tools/souji-rev-pin.py
```
- tools/souji-declared-evidence.py:18 docstring: "Exit 0 iff M == 0.  Read-only: git plumbing only, scratch under $TMPDIR." (was "scratch under /var/tmp"); :265-266 `base = tempfile.mkdtemp(prefix="souji-declared-evidence-")` (was `dir="/var/tmp"`).
- tools/souji-gate-check.py:231-232 same shape (`prefix="souji-gate-check-"`).
- tools/souji-rev-pin.py:253-254 same shape (`prefix="souji-rev-pin-selftest-"`).
No other hunk exists in the diff; residual literal `/tmp`/`/var/tmp`/TMPDIR references at 98e5203 in these files are docstring/comments only (`git grep -nE '/var/tmp|/tmp|TMPDIR' 98e5203 -- <files>`: 8 hits, none executable scratch).

Run matrix — clones `/fast/scratch/hyaku/souji-r32/ReviewC2Decl/{base,rev}` (origin removed; `rev-parse --show-toplevel` verified = each clone; HEADs = 85b61a1… and 98e5203…). Per command, TMPDIR=/fast/scratch/hyaku/souji-r32/ReviewC2Decl/tmp and `env -u TMPDIR`:

| item | command (cwd = clone) | base rc / last line | C2 rc / last line |
|---|---|---|---|
| T03 | python3 -B tools/souji-declared-evidence.py --root . --rev 85b61a151923986e7e6b48f7084b9122561b5f3d | 1 / assertions=252 resolved=229 skipped=401 mismatches=23 | 1 / identical |
| T04 | python3 -B tools/souji-declared-evidence.py --selftest | 0 / selftest=8/8 | 0 / identical |
| T05 | python3 -B tools/souji-gate-check.py --selftest | 0 / selftest=9/9 | 0 / identical |
| T06 | python3 -B tools/souji-rev-pin.py --selftest | 0 / SUMMARY total=11 failed=0 | 0 / identical |

All 8 result pairs identical with TMPDIR set AND unset. Stronger: full stdout+stderr captured per command at both revs (`> out 2>&1`), `diff -q` base-vs-C2: T03, T04, T05, T06 FULL OUTPUT IDENTICAL in both envs (outputs 1/9/10/12 lines).

Cleanup:
- TMPDIR-set runs: `ls -A …/ReviewC2Decl/tmp/` → 0 entries after all runs.
- TMPDIR-unset runs: /tmp listing before vs after → no new `souji-declared-evidence-*`, `souji-gate-check-*`, `souji-rev-pin-selftest-*` dirs (base and C2 runs).
- Live catch during an unset T06 run: `/tmp/souji-rev-pin-selftest-boeae76l` observed mid-run, absent after (`ls -d /tmp/souji-rev-pin-selftest-*` → none left).

No tools installed this run (none needed); pacman untouched.

## Findings

1. PASS (check 1) — Only behavioural change is the scratch root. The complete diff is 3 `mkdtemp(dir="/var/tmp")` → `mkdtemp()` calls plus docstring/comment lines; every other byte identical. Proof beyond text: full outputs identical for all four commands at both revs, both envs. tools/souji-declared-evidence.py:266, tools/souji-gate-check.py:232, tools/souji-rev-pin.py:254.
2. PASS (check 2) — No guard widened. No path-check, refusal or policy line appears in the diff. rev-pin's refusal cases (path-escape, unknown-rev, historical tree-check) still present at 98e5203 (tools/souji-rev-pin.py:351-368) and pass (total=11 failed=0, both revs/envs). The only "widening" is where scratch may live — that is the fix itself, not a check.
3. PASS (check 3) — TMPDIR unset: identical (rc, last line, full output) to base at both revs; scratch falls back to Python's tempfile default (/tmp), observed live and fully removed. Note: with TMPDIR unset the scratch location moves from /var/tmp (base) to /tmp (C2) — intended consequence of the standard tempfile precedence; fixture trees are tiny (<50 MB), and the frozen C2 predicate always runs with TMPDIR set to a scratch dir, so this is outside the claim, not a defect.
4. PASS (check 4) — Cleanup intact and equivalent: tools/souji-declared-evidence.py:311 `subprocess.run(["rm", "-rf", base], check=False)` and tools/souji-gate-check.py:287 (same) inside `finally:`; tools/souji-rev-pin.py:373 `shutil.rmtree(top, ignore_errors=True)` inside `finally:`. Empirically zero residue in TMPDIR and /tmp across 16 runs.
5. Observation, no defect — T03's `mismatches=23` (rc 1) is identical at base and C2 and matches the base-anchor property; the count itself is C1-domain (SCORECARD declared evidence at the fixed base rev, pre-binding) and out of this item's scope.

## Attack log

None — this seat is a review item, not an attack. No counter gameability found in scope: the mkdtemp change cannot mask a selftest failure (failure counting and nonzero exits unchanged; anchors compare base vs REV outputs, which are byte-identical).

## Deliveries

- .ufo/waves/round-32/a2w1/SwarmReviewer10.md (this report)
