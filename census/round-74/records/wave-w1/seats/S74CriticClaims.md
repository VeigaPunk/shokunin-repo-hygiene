# S74CriticClaims — r74 w1 critic (claims): C1 operability / C2 calibration

Basis HEAD 8fe48c86. C1 candidate ec13ba7 tools/souji-pre-report-gate.sh=3162de98 (committed writer 70bbf1c2 beside it; the worktree gate is now 062b6d39 from an in-flight repair and is not judged); C2 candidate ac57303 census/round-74/c1-counter.py=e3fc47c2; matrix f2ced976; base slot 8b9345b writer=118597e0.

## C1 pre-report gate byte truth (operability)
**(i) STANDS.** `python3 -B census/round-74/c1-gate-counter.py --gate <ec13ba7 gate copy + writer> --work <SCR>/c1/cand-commit` → `SUMMARY rows=9 mismatches=0 errors=0` / `EXIT=0`; lane-base gate copy → `mismatches=3` (GF1/GF2/GF3 `clean=PASS`, `EXIT=1`). Committed records/c1-after.txt and controls/c1-K-a match.
**(ii) STANDS.** K-b variant → `mismatches=4`; K-c → `mismatches=1`; both `EXIT=1`; variant sha256 42bd98…/6c0071… match the committed receipts.
**(iii) FALLS (missing evidence).** No `census/round-74/records/c1-domain-trial.txt` at HEAD (ls + grep; only preregistration.txt:42 names it). The gate over the lane now prints `check-clean=FAIL` (`detail-clean:  M SCORECARD.md` + 8 more in-flight paths) and the final tip/round report do not exist yet, so the only operability conjunct is unmeasured. **HIGH.**
**Axis:** STANDS by corpus/QUALITY.md:143 (Q59: a gate on an input edge class is an operability surface), but the label is unearned while (iii) is absent.
**Matrix fairness: QUALIFIED.** Omitted shapes built in S74CriticClaims/c1-shapes.py: E1 exec-bit+index-mode forge, E2 symlink→regular same bytes, E4 deleted+stat forge are all caught by the index-vs-HEAD comparison (both gates FAIL → harmless omission); E3 repo-local `core.fileMode=false`+exec-bit flip (no index forge) is PASSed by BOTH gates: gate status clean, `_truth_refusal`'s pinned status lists `M run.sh` but skips every status-listed path (tools/souji-receipt-write.py:283) → returns None. **MEDIUM**: same defect family, config residual absent from the named limits; the in-flight worktree repair targets it.
**Sourced claim: STANDS.** S317 capture sha256 c8aca940… matches corpus/SOURCES.md:276; quote at offset 2194 of gitformat-index.txt; the concealment inference is S315 and the hash remedy S316, both cited. The fix compares only the object name, not the entry's mode/type field S317 also names — the E3 residual.

## C2 counter witness + survivor kills (calibration)
**(i) STANDS 3/3.** `python3 -B <edited r74 counter> --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b… --rev 43cd74b… --tool tools/souji-receipt-write.py --work <SCR>/c2/main-D6|D7|D8` → each `base_unwitnessed=1 base_forgeries=14`, `EXIT=1`; edited row `CASE FWw|FC1|FC2 … base_witness=no`, all other forged rows `yes`.
**(ii) STANDS 5/5.** D1..D5 arms: `base_unwitnessed=1`; FWr/FWi/FWp/FWs/FC3 `base_witness=no`, others `yes`.
**(iii) STANDS.** pristine → `base_forgeries=15 base_unwitnessed=0`, `EXIT=0`; r73-Kblanket variant → `base_unwitnessed=15`, `EXIT=1`; r73 pristine → 15/0, `EXIT=0`.
**(iv) STANDS 4/4.** M08/M14/M15/M17 selftests → `fail=1/1/2/1`, `EXIT=1`; the same edits on the r73 counter → `52/52` (0 of 4 killed).
**(v) STANDS.** pristine selftest → `cases=62 pass=62 fail=0`, `EXIT=0`.
**Do-nothing: STANDS (target not reachable).** r73 counter + D6/D7/D8 → `base_unwitnessed=0`, `EXIT=0` (0 of 3).
**Circularity: QUALIFIED.** `hack2.py` = candidate + 6 lines declaring FWw/FC1/FC2 unwitnessed from their own spec (worktree read ignored for them; frozen b_wit/n_wit lines intact): (i) 3/3, (ii) 5/5, (iii) 15/0, (v) 62/62, (iv) all four mutants killed — all five conjuncts pass. Conjunct (iii) rejects only an unconditional hard-code. The claim actually rests on code (counter:1468-1472 row_scope∘tree_divergence) and the pre-freeze probe (row-scope-pristine 15/15; my D8 replay `row_witness=no tree_witness=yes`), not on the predicate. **MEDIUM.**
**(iv) unconditional-fail attack: FALLS (attack fails).** (v) blocks it; the four failures are the specific property checks at counter:2004/2019/2129/2130. The only `__file__` hash (counter:1730) is a printed header, not a pass/fail.

## Universal clauses
Order 43cd74b→bcdf2d16→ac573032→ec13ba7f→8fe48c86; r73 counter unamended (3809ee7d; no diff 43cd74b..HEAD); gate↔counter references 0/0; all 16 committed receipts start `# command=`; missing-writer fails closed (`clean=FAIL`). **LOW:** gate check 4 now depends on writer bytes (`_truth_refusal`, gate:45-50), so C1 is gate+writer bytes; the helper's `path in listed` skip assumes the caller had the writer's pinned status — that contract gap is the E3 hole.

Files: .ufo/waves/round-74/w1/S74CriticClaims/{c1-runs.txt,c1-shapes.py,c2-runs.txt,c2-attack.txt}. Scratch /fast/scratch/hyaku/souji-r74/S74CriticClaims removed before yield.
