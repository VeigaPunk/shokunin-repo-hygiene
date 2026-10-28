# R41executor10 — C2 candidate tools/souji-freeze-check.py

Candidate: .ufo/waves/round-41/w1/R41executor10/souji-freeze-check.py
sha256 25048ab435d57c6786e7ee38b737a4d2137abf365ec79a972af312f98571329e, 11178 bytes. Python stdlib only; no network; never writes into --root (git run with GIT_OPTIONAL_LOCKS=0, GIT_NO_REPLACE_OBJECTS=1, config isolated).

## Command run
TMPDIR=/fast/scratch/hyaku/souji-r41/R41executor10/w bash census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41executor10 tools/souji-freeze-check.py=<candidate>

## Output (tail)
all 21 case-*=PASS (clean ... two-claims-one-bad, unresolved-rev, absent-prereg)
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=25048ab435d5
EXIT=0

## Git plumbing choices
- Prereg and frozen blobs: `git cat-file blob REV:PATH` (never the work tree); a non-blob/missing -> *-MISSING finding; path with `..`/absolute -> missing/could-not-evaluate.
- FREEZE-REV: `git log --diff-filter=A --no-renames --full-history --no-merges -z -- :(literal)PATH` from --rev; several candidates -> minimal ones (no candidate ancestor), then earliest committer time. Merges are not diffed (no phantom adds); rename-in = add of the new path.
- Ancestry: `merge-base --is-ancestor` (rc 0/1; any other rc -> exit 2, never a guess); Base == freeze is NOT-ANCESTOR (strict).
- DISPATCH-BEFORE-FREEZE: adds under `.ufo/waves/round-<N>/` (N from `Round:` line) reachable from FREEZE-REV with basename `*-dispatch.json` or `*.ready`.
- Unresolved --rev, absent PATH, non-repo root, git failure, unexpected exception -> stderr `REFUSAL COULD-NOT-EVALUATE: ...`, exit 2, no traceback.

## Extra ad-hoc probe (scratch fixture, deleted)
Prereg added on a side branch, merged with --no-ff, then renamed in main: freeze found, no crash (NO-CLAIMS rc=1 as the file had no claims). /nonexistent root, `../x` path, short --rev: each rc=2 with REFUSAL line.

## Verdict
Target SUMMARY reached, exit 0. Seat score is advice; L1 measures. No tool installs. Scratch dir removed.
