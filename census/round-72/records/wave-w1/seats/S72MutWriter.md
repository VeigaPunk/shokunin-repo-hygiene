# S72MutWriter — writer protections vs the 75-row r72 matrix (souji r72, w1)

Verdict: 6 of 11 single-edit writer mutants survive the r72 matrix (EXIT=0, 0 deviating rows); 5 are killed only by the writer's own selftest (selftest-only protections), and W9 (pre-run witness ordering) survives BOTH → uncovered defect (MEDIUM). The five FW rows are real: base=accept/new=refuse `RECEIPT-FILTER-DRIVER-SET` for FWr FWi FWp FWw FWs, and C2(ii) reproduces: `SUMMARY matrix=75 base_forgeries=12 base_honest=19 base_mismatches=0 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0` (19 == 19 accept rows). Writer at lane base and HEAD: sha256 b7790001…244d (unchanged).

| id | edit (tools/souji-receipt-write.py line) | r72 main arm | writer selftest | verdict |
|---|---|---|---|---|
| W1 | :195 filter half dead (`_filter_drivers(top, set())`) | new_forgeries=8 class_mismatches=8 EXIT=1; FC1 FC2 FC3 FWr FWi FWp FWw FWs accept | 42→40 (filter-driver, wave-repairs) | KILLED |
| W2 | :200 ident tests b"unset" | unchanged EXIT=0, 0 rows | 42→41 (checkin-conversions; rc=0 accepted) | SELFTEST-ONLY |
| W3 | :202 wte tests b"set" | unchanged EXIT=0, 0 rows | 42→41 (checkin-conversions; rc=0 accepted) | SELFTEST-ONLY |
| W4 | :147 pin core.checkStat=default removed | unchanged EXIT=0, 0 rows | 42→41 (wave-repairs; rc=0 accepted) | SELFTEST-ONLY |
| W5 | :147 pin core.trustctime=true removed | unchanged EXIT=0, 0 rows | 42→41 (wave-repairs; rc=0 accepted) | SELFTEST-ONLY |
| W6 | :146 pin core.fileMode=true removed | new_forgeries=2 EXIT=1; FM1 FM2 accept | 42→41 (filemode-pin) | KILLED |
| W7 | :136 GIT_ATTR_SOURCE kept in git() env | class_mismatches=2 EXIT=1; AS1 AS2 refuse FILTER (expected dirty/STATE-CHANGED) | 42→41 (filter-driver) | KILLED |
| W8 | :602-604 post-run witness moved after post-run status | unchanged EXIT=0, 0 rows | 42→41 (wave-repairs; self-unlinking in-run filter rc=0) | SELFTEST-ONLY |
| W9 | :492-494 pre-run witness moved after pre-run status | unchanged EXIT=0, 0 rows | 42/42 PASS | SURVIVED BOTH (MEDIUM) |
| W10 | :498 pre-run status loses showUntrackedFiles=all | class_mismatches=1 new_honest=18 EXIT=1; V1 class -, SY1 over-refusal | 42→39 (in-run-untracked-dir, untracked-visibility, symlink-record) | KILLED |
| W11 | :610 post-run status byte compare dropped | new_forgeries=5 EXIT=1; T2 T3 T5 AS2 FM2 accept | 42→40 (in-run-edit, filemode-pin) | KILLED |

Commands (from the lane root; scratch /fast/scratch/hyaku/souji-r72/S72MutWriter):
- `python3 -B census/round-72/c1-counter.py --root <lane> --matrix census/round-72/c1-matrix.tsv --base-rev 8b9345b1… --rev 0bf098dd… --tool tools/souji-receipt-write.py --work <S>/wfrozen` → the SUMMARY above / EXIT=0 (also with `--new-tool <S>/base.py`).
- per mutant: the same with `--new-tool <S>/W<n>.py --work <S>/wW<n>`; per copy: `TMPDIR=<S>/stW<n> python3 -B <S>/W<n>.py --selftest --work <S>/stW<n>`.
- W9 probe: fixture repo, `.git/info/attributes` `tracked.txt filter=u`, `filter.u.clean` maps v2→v1 and unlinks the attribute when the pre-run status read runs it; wrapped command writes a marker.

Findings:
- MEDIUM: W9 — pre-run witness ordering is measured nowhere. Probe: base writer `rc=2 ... RECEIPT-FILTER-DRIVER-SET`, marker_exists=False; W9 `rc=2 ... RECEIPT-STATE-CHANGED-DURING-RUN`, marker_exists=True — the wrapped command executes before the refusal and the class changes. FWr's filter is `sed s/v2/v1/` (never unlinks), and selftest case_41(b) covers only the in-run ordering.
- MEDIUM: W2/W3/W4/W5/W8 are selftest-only protections; the matrix has no ident, working-tree-encoding, core.checkStat, core.trustctime or self-unlinking-filter row (`grep -n 'checkStat\|trustctime' census/round-72/c1-counter.py` → no match; no fixture writes ident/working-tree-encoding; `FILTER_CLEAN = "sed s/v2/v1/"`). Next-round row candidates (5).
- LOW: the suggested `_witness_attrs` empty-`ls-files` early return is already present (tools/souji-receipt-write.py:165-166); that proposed mutant is a no-op, not a defect.
- C1 and C2(i) were not re-run here (sibling seats own them; S72ExecC2 already reproduced C2(i)/(ii)).

Files written: `.ufo/waves/round-72/w1/S72MutWriter.md`, `.ufo/waves/round-72/w1/S72MutWriter/{mutants.tsv,mutant-diffs.txt,probe-W9.txt,base.py,W1.py…W11.py,main/*-main.txt,selftest/*-selftest.txt}`. No tool installs; no lane tracked file touched.
