# R41executor11 — C2 candidate tools/souji-freeze-check.py

Candidate: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-41/w1/R41executor11/souji-freeze-check.py
sha256 b9ed293cee386a75532938c8ca4d2f6cb0347a093bb4713a9eadb188a689890d, 10460 bytes (python stdlib only; git cat-file/log/merge-base read-only; never writes --root; blobs read at --rev, parsed as data).

## Command run
TMPDIR=/fast/scratch/hyaku/souji-r41/R41executor11 bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41executor11 tools/souji-freeze-check.py=<candidate>

Observed: all 21 `case-*=PASS`, then
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=18 summary=(3, 18)
SUMMARY cases=21 pass=21 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red tool_sha=b9ed293cee38
EXIT=0

## Robustness probe (not a frozen measurement)
Ran the counter's own 21 cases with its prereg_text monkeypatched to emit CRLF line endings, trailing spaces/tabs on every line and a non-ASCII trailer (café — 日本語 ✓): result (21, 21), all PASS, rc=0. CRLF/trailing space/non-ASCII therefore change no finding class.

## Design notes
- FREEZE-REV = first of `git log --no-renames --topo-order --reverse --diff-filter=A -- PATH` at --rev; exit 2 + `REFUSAL COULD-NOT-EVALUATE:` for non-full40/unresolved --rev, absent PATH, or no adding commit.
- Missing key -> FIELD-MISSING only; present-but-blank (any key) -> FIELD-EMPTY only, dependent checks skipped. Counter/Population without a valid `sha256=` token -> *-DIGEST. FROZEN-EDITED compares raw blobs at --rev vs FREEZE-REV (a blob deleted at --rev counts as edited).
- DISPATCH-BEFORE-FREEZE: one C0 finding (count + first file) when any `.ufo/waves/round-<N>/**/*-dispatch.json|*.ready` was added at FREEZE-REV or an ancestor.
- Unspecified-by-spec choices (limits): duplicate keys -> first wins; CONTROL-NOT-RED accepts negative nonzero ints; Round line must be `Round: <digits>` (absent -> no dispatch check).

## Tooling
No installs. Scratch /fast/scratch/hyaku/souji-r41/R41executor11 deleted. Verdict: PASS — target SUMMARY met, exit 0.
