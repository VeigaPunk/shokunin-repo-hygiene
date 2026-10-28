# R41scribe08 — scribe report (souji round 41, wave 1, role scribe)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Freeze tip read: `e2a74312af4233963e44e4dbb38838ece07b8bd2`.
Draft row: `.ufo/waves/round-41/w1/R41scribe08/mistake-freeze.md`. Receipts: `.ufo/waves/round-41/w1/R41scribe08/`.
No frozen file, lane file outside this seat directory, or tracked file was written. No git or jj mutation was run. No tool was installed or upgraded.

## 1. Mistake mined

The r40 pre-data-freeze failure (M40-3, M40-4, M40-5 in `corpus/lessons/round-40.md`), class **scope** with a stale-premise facet. The r40 preregistration referenced a "frozen list" (C2), a per-item population (C1), and "the r39 base fixture" (C3) without committing any of those as bytes. Fix: C2's runnable freeze check. The full row is in `mistake-freeze.md`.

## 2. Captured-by sweep

Command (at the freeze tip):
```
grep -n -iE 'freez|frozen|pre-?data|before (any|data|dispatch|scor)|population|preregist|pre-dispatch' corpus/QUALITY.md
```
Result: 27 matching lines. Rows that name this class: Q93 (line 241), Q94 (line 242), Q95 (line 244). Adjacent rows Q58, Q59, Q70, Q76-Q78, Q80 were read and do not freeze a population or pair list.

Commit order:
```
$ git log --format='%h %s' -S'| Q94 |' -- corpus/QUALITY.md
994de3b round-40: bind evidence path as well as revision; add path-substitution control
$ git log --format='%h %s' -- census/round-40/preregistration.txt
128e412 2026-10-28 round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery
$ git merge-base --is-ancestor 128e412 994de3b && echo yes
yes
```
So Q93-Q95 post-date the r40 freeze. The row therefore records `captured-by: none (runnable)`; the prose rules exist but no command enforces them.

Runnable sweep: `grep -n -iE 'population|digest|sha256|pair|freez' tools/souji-axis-check.py` → no match (exit 1). `tools/souji-freeze-check.py` does not exist at the tip (`test -f` → ABSENT).

The r40 preregistration (`census/round-40/preregistration.txt`, sha256 `7218101a…b4758c`, identical at `128e412`): `grep -n -iE 'sha256|digest'` returns nothing. Line 8 names "the frozen list" and line 11 names "the r39 base fixture"; neither is in the file.

## 3. C2 measurements (counter spec `census/round-41/c2-counter.py`)

Frozen digests re-checked against the committed blobs:
```
dd4efc80…  census/round-41/preregistration.txt
4854335a…  census/round-41/c2-cases.tsv    (matches prereg Population sha256=4854335a…)
85ffe263…  census/round-41/c2-counter.py   (matches prereg Counter sha256=85ffe263…)
5ccb4fb2…  census/round-41/controls/c2-stub-clean.py
```

**(a) Always-clean stub, scored through the only supported path.** Command:
```
bash census/round-41/score-candidate.sh c2 /fast/scratch/hyaku/souji-r41/R41scribe08 tools/souji-freeze-check.py=census/round-41/controls/c2-stub-clean.py
```
Output (receipt `.ufo/waves/round-41/w1/R41scribe08/c2-stub-clean-score.txt`), abridged to the final lines:
```
case-clean=PASS
case-clean-dispatch-after=PASS
case-no-claims=FAIL ... (17 finding-class cases FAIL; each shows rc=0 findings=[] summary=(1, 0))
case-unresolved-rev=FAIL rc/refusal check
case-absent-prereg=FAIL rc/refusal check
real FAIL rc=0 findings=0 summary=(1, 0)
retro FAIL rc=0 findings=0 summary=(1, 0)
SUMMARY cases=21 pass=2 fail=19 control_clean=REJECTED control_findings=REJECTED real=FAIL retro=FAIL tool_sha=5ccb4fb2705b
EXIT=1
```
The stub passes the 2 clean cases and fails 19: 17 finding-class cases and 2 refusal cases. Its `control_clean` is REJECTED. The counter also reports `control_findings=REJECTED` for the always-findings stub. The 21 cases are 19 tuples (2 clean, 17 finding-class) plus 2 refusal checks.

**(b) Counter at the freeze tip with no candidate.** Command:
```
python3 -B census/round-41/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev e2a74312af4233963e44e4dbb38838ece07b8bd2 --scratch /fast/scratch/hyaku/souji-r41/R41scribe08
```
Output (receipt `c2-tip-tool-absent.txt`):
```
PRISTINE FAIL TOOL-ABSENT tools/souji-freeze-check.py at e2a74312af4233963e44e4dbb38838ece07b8bd2
SUMMARY cases=21 pass=0 fail=21 control_clean=n/a control_findings=n/a real=FAIL retro=FAIL tool_sha=absent
EXIT=1
```

## 4. Limits

- C2 checks the preregistration's shape, digests, and freeze order. It does not read a Population file's contents. A pair list or a base-fixture path+digest is covered only if the claim names that artifact as its Population or Counter. The Q94 TOTAL-ordering and Q93 probe-byte requirements stay prose until a counter enforces them.
- The fix counts only after a candidate `tools/souji-freeze-check.py` passes all 21 cases with both stubs rejected and real/retro legs green. None of that exists at the tip.
- I ran no candidate tool; the only scoring was the always-clean stub (the control, not a candidate).

## 5. Verdict

- Mistake row drafted with class `scope` (stale-premise facet), evidence pointers into `census/round-40/preregistration.txt`, `census/round-40/waves/w1/*`, `corpus/lessons/round-40.md` M40-3..M40-5 and the spot-check lines 35/44/74, `captured-by: none (runnable)` with the sweep, and fix = C2.
- The C2 instrument is shown able to fail: the always-clean stub is REJECTED (19 of 21 failing). The fix itself is **not yet shown**: at the tip, the tool is absent and the counter reports `pass=0`. Status for the fix: pending the C2 candidate.
- No defect found in the frozen C2 counter or population during this read; no frozen-file edit was proposed.

## 6. Cleanup

Scratch `/fast/scratch/hyaku/souji-r41/R41scribe08/` is removed before yield. Receipts are copied into this seat directory (see section 3).
