# S77Reviewer — round-77 falsification (lane souji-shokunin, base d4f5156, tip ef04ca6)

## Verdicts
1. Gate nonreg_sources + timeout wrapping (a9979807..9b496b08): **DEFECT** (MEDIUM-1; LOW-1..3)
2. census/round-77/c1-nonreg-counter.py: **SOUND**
3. census/round-77/c2-pointer-counter.py: **SOUND** (LOW-5)
4. preregistration.txt vs controls/ + records/: **SOUND — zero mismatches** (domain-trial receipt still owed at the report tip)

## Re-derived numbers (all runs from the lane root; blobs copied from the named revs)
W gate 28a5135..: `SUMMARY rows=16 mismatches=0 errors=0 hangs=0` EXIT=0 — matches claim.
Base gate 90bdd8c..: n1-n7,n10 `clean=HANG secs=30.0`; n8 `clean=PASS`; `SUMMARY rows=16 mismatches=9 errors=0 hangs=8` EXIT=1 — matches.
r76 `rows=30 mismatches=0` rc=0; r36 `cases=21 pass=21` rc=0; r27 `cases=4 pass=4` rc=0 — match.
C1 controls re-run from controls/variants (sha == receipt binds): K-b 7/0, K-c 11/8, K-d 7/4, all EXIT=1 — match prereg brackets.
C2 base: `resolved=0 unresolved=35` EXIT=1; at L: `resolved=35 unresolved=0 refused=0 mismatched=0 errors=0` EXIT=0.
pointer-check missing=35 (base) -> 31 (L) -> 31 (A); set diff = SCORECARD.md:1713/1714/1743 + SKILL.md:857 (P09/P10/P11/P18), nothing new.
Population tokens == pointer-check MISSING set at base (LC_ALL=C comm, empty). C2 K-b 4/31, K-c 4 refused/31, K-d 4 mismatched/31, K-e 3 refused/32 — all red.
freeze-check --substance --chronology at F and at A: `SUMMARY claims=2 findings=0` EXIT=0; prereg's four instrument digests match sha256sum.
Independent bytes: P04 sha256 == blob at L; P31 `git archive|diff -r` clean; .ufo/quarantine 0 files/0 links; ABSENT tokens have no history.

## Findings
MEDIUM-1 tools/souji-pre-report-gate.sh:70 — the git dir is `rev-parse --absolute-git-dir`, but git reads `$GIT_COMMON_DIR/info/{exclude,attributes}`. Linked worktree + FIFO at the common info/exclude: base HANGs, W gate does **not** print RECEIPT-NONREGULAR-SOURCE — it hangs to the 300 s backstop (gate copy with gate_timeout=2: `check-clean=FAIL / detail-clean: git status failed or timed out:` at 2.0 s). No false PASS, but the claimed refusal does not fire and a 300 s stall replaces it; the 16 rows cannot see it (all fixtures are non-linked). Lane itself: absolute-git-dir == common dir, so operability holds here.
LOW-1 gate:82-83 — `f=$(find … | wc -l) || { echo -1; }`: pipeline status is wc's, so the -1 path is unreachable (probe: find rc=1 -> f=0). A failed find silently reads as "0 non-regular sources".
LOW-2 gate:82 vs gate:64 — the find branch uses `! -type f`, so any work-tree symlink (even to a regular file) is refused, contradicting the stated "a symlink counts by its target" (info/config branches use -f at :72/:80). No verdict change: git itself opens pattern files with PATTERN_NOFOLLOW (srcs/git-dir.c-v2.56.0:1164,1779), so base already fails such a tree.
LOW-3 gate:80 — `core.excludesFile=/dev/null` on an honest tree: base `PASS`, W `FAIL RECEIPT-NONREGULAR-SOURCE`. Compliant with the frozen rule's letter, but it refuses the standard way to disable global excludes.
LOW-4 population — no row exercises the XDG-default, relative-path or `~`-expansion branches the diff adds. Behaviour is correct (probes: base HANG(10 s) -> W REFUSED in all three), but it is unpinned by the frozen 16.
LOW-5 c2-pointer-counter.py:47 — POLICY_LOCAL prefix lacks a separator (`.ufo/quarantine` also matches `.ufo/quarantine-foo`); digest equality still gates the item.

## Notes (no action)
18/35 C2 items resolve by class (FLEET 8, ABSENT 3, TOKEN 6, QUARANTINED 1), 17 by verified bytes; preregistration.txt states this, the round prose "resolves to bytes" overstates it.
Domain trial at A: `check-tip/report/shonen/prereg=PASS`, `check-clean=FAIL` only from in-flight writes (` M SKILL.md`, ` M corpus/*`, `?? corpus/lessons/round-77.md`); the nonreg scan does not fire on the lane. Must be re-run on a clean worktree at the report tip.

## Files written
.ufo/waves/round-77/w1/S77Reviewer.md, S77Reviewer/evidence.txt (commands + full outputs), S77Reviewer/domain-report.md (throwaway --report input for the domain trial).
