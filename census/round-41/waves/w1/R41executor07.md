# R41executor07 — C2 candidate: souji-freeze-check.py

Candidate: `.ufo/waves/round-41/w1/R41executor07/souji-freeze-check.py` (dest `tools/souji-freeze-check.py`)
- sha256 `3c3e80baedd8774848fb9ac786bbda0c07c47250a14884abf1409f328fc3340b`, 9447 bytes (`sha256sum` / `wc -c`).
- Python stdlib only, no network, read-only on --root (only `git log/cat-file/rev-parse/merge-base`; prereg and all blobs read via `git cat-file blob REV:PATH`, never the work tree).

## Behavior
- Parses `## C<digits>` blocks (to next `## `), column-0 key lines Base/Counter/Population/Control/Target/Kill (first occurrence wins).
- FREEZE-REV = oldest commit from `git log --diff-filter=A --reverse REV -- PATH`.
- Emits all 14 documented classes into a list, prints sorted `FINDING <claim> <CLASS> <detail>`, then `SUMMARY claims=n findings=m`; exit 0/1.
- Exit 2 with `REFUSAL COULD-NOT-EVALUATE: ...` on stderr for non-full40/unresolved --rev, absent PATH at --rev, or no add commit.
- Missing Counter/Population path suppresses digest/frozen checks for that path (single class per defect); FROZEN-EDITED compares blob at --rev vs at FREEZE-REV.
- DISPATCH-BEFORE-FREEZE: files `*-dispatch.json`/`*.ready` under `.ufo/waves/round-<N>/` (N from `Round:`), first-added at FREEZE-REV or an ancestor.

## Command run (exact)
```
cd /fast/scratch/hyaku/souji-r41/R41executor07 && bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41executor07 tools/souji-freeze-check.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor07/souji-freeze-check.py; echo EXIT=$?
```
Observed: 21 lines `case-<name>=PASS` (all 19 synthetic cases plus unresolved-rev, absent-prereg), then
```
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=3c3e80baedd8
EXIT=0
```
Passed on the first run; no iteration needed. Scratch dir deleted after the run. No tools installed.

## Verdict
Target SUMMARY met, exit 0 (seat score is advice; L1 measures). Limits: a malformed Counter/Population value (no `sha256=`) is reported as `*-DIGEST`, and a non-hex/short Base as BASE-UNRESOLVED — grammar docs do not name these; per-file DISPATCH findings (one per file) rather than per prereg. Not exercised: octopus/merge-heavy histories beyond `--full-history`.
