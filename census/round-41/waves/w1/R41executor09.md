# R41executor09 — C2 candidate `souji-freeze-check.py`

Candidate: `.ufo/waves/round-41/w1/R41executor09/souji-freeze-check.py` (destination `tools/souji-freeze-check.py`)
- sha256 `e0bec95b77a08c7cab1d45a7c4d4d1fa7f1f15e5191d95bdde15fbe39661f7ba`, 9561 bytes. Python stdlib only, read-only on `--root`.
- Reads the prereg blob at `--rev` via `git cat-file blob`. All regexes are anchored at column 0. A malformed key line counts as the key being absent (FIELD-MISSING). Unresolvable `--rev`, an absent prereg or a non-repo root gives exit 2 with `REFUSAL COULD-NOT-EVALUATE`. No input crashes the tool (utf-8 decoded with replace).
- FREEZE-REV: oldest commit adding PATH (`git log --topo-order --reverse --no-renames --diff-filter=A`).
- Dispatch check: scans `.ufo/waves/round-<N>/` at `--rev` for `*-dispatch.json` and `*.ready`. A finding is raised when the file's first-add commit is FREEZE-REV or one of its ancestors. N comes from the prereg's `Round:` line; with no `Round:` line the check is skipped.

## Command run (exact)
```
cd /fast/scratch/hyaku/souji-r41/R41executor09 && TMPDIR=/fast/scratch/hyaku/souji-r41/R41executor09 \
 bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41executor09 \
 tools/souji-freeze-check.py=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor09/souji-freeze-check.py
```
Observed: 21 `case-*=PASS` lines, then
```
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=e0bec95b77a0
EXIT=0
```
The scratch dir was removed by trap on exit.

## Verdict
Target SUMMARY reached with exit 0 on the shared-clone score. This is a seat score, not the L1's measurement. Risks: none found. Not built or run beyond the counter.
