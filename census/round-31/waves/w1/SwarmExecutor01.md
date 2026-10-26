## Status

STATUS: PASS — all seven assigned cells L01-L07 are bound by accepted supersession rows (6 run, 1 record); acceptance counter reads `mismatches=0` for the seven ids twice from a scratch clone, full-enumeration delta is exactly 34→29 mismatches with the other 34 ITEM lines byte-identical.

## Evidence

All lane git calls are reads against `/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, list-rev `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, lane tip `1b811368461785040e955f41f9c97e62f61fd67c` (SCORECARD.md bit-identical to base: `git diff --stat 9f17a1e 1b81136 -- SCORECARD.md` empty). Scratch `/fast/scratch/hyaku/souji-r31/C1BindA/` (clone `c1`, origin removed, toplevel verified `c1`; throwaway identity only inside scratch); scratch removed after delivery.

1. Writing commits (`git blame 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc -L152,158 -- SCORECARD.md`): 152 `d7266c5`, 153-155 `23014d4`, 158 `163158a`.
2. Base state of the seven (`python3 -B tools/souji-capability-cells.py --root <lane> --rev 1b81136… --base 9f17a1e… --list-rev 1d45496… --only L01,…,L07`): `bound_run=2 bound_record=0 unbound=1 mismatches=5`; L01/L02 MATCH at base cell, L03 UNBOUND, L04-L07 RUN-MISMATCH. Full 41-item base run at the same rev: `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34`, identical to the frozen do-nothing row in `census/round-31/records/controls.tsv`.
3. Acceptance, scratch commit `b19a3510d22041e0d65ca0d3d9679c13f6aa25a4` (lane tip tree + appended rows only), two invocations of `--only L01,L02,L03,L04,L05,L06,L07`, `diff` of the outputs empty:

```
ITEM	L01	SCORECARD.md:152	literal=6/6	superseded	binding=run	MATCH	bash tests/fixtures/r12-maintenance-guard.sh --selftest rc=0 observed=selftest=PASS ids=6/6
ITEM	L02	SCORECARD.md:153	literal=36/36	superseded	binding=run	MATCH	python3 tools/souji-cert-evidence.py --selftest rc=0 observed=selftest: 36/36 passed
ITEM	L03	SCORECARD.md:153	literal=5/5	superseded	binding=record	MATCH	census/round-13/verification.json
ITEM	L04	SCORECARD.md:154	literal=total=5 failed=0	superseded	binding=run	MATCH	bash tests/fixtures/r13-quarantine-bounds.sh rc=0 observed=SUMMARY total=5 failed=0 hung=0
ITEM	L05	SCORECARD.md:155	literal=ids=7/7	superseded	binding=run	MATCH	bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh rc=0 observed=selftest=PASS ids=7/7
ITEM	L06	SCORECARD.md:158	literal=pass=65 fail=0	superseded	binding=run	MATCH	python3 tools/souji-landing-gate.py --selftest rc=0 observed=SELFTEST pass=65 fail=0
ITEM	L07	SCORECARD.md:158	literal=total=15 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r16-landing-gate.py rc=0 observed=SUMMARY total=15 failed=0
SUMMARY items=7 bound_run=6 bound_record=1 unbound=0 mismatches=0 partial=1 rev=b19a3510d22041e0d65ca0d3d9679c13f6aa25a4
```

4. Full enumeration with the rows: `SUMMARY items=41 bound_run=11 bound_record=1 unbound=21 mismatches=29 rev=b19a3510…`; the L08-L41 ITEM lines are byte-identical to the base full run (`grep`-selected, `diff` empty, 34 lines each).
5. L03 negative probe (clone `c1x`, commit `9a51467f65e996223f1cbeb73dca894d6da60942`, forced run row): `ITEM L03 … binding=run BAD-ROW(run-shape) python3 tests/fixtures/r13-cert-evidence.py`, `mismatches=1`.
6. Record-byte checks at base: `census/round-13/verification.json` blob `879d96b42867dff04e02c5f08636081d1a8ca00f` at both base and measured rev (last change `15d95e3`, round 13); line 57 stdout ends `fixture: 5/5 checks passed`; entries `evidence-selftest` (17), `evidence-external-fixture` (49), `structure-selftest` (63), `quarantine-bounds` (97). `tests/results/r12-maintenance-guard.txt` blob `03c3d11…` at both `d7266c5` and base, containing `selftest=PASS ids=6/6`.
7. Round-16 sweep: `git grep -l -E '(^|[^0-9])(18/18|15/15)([^0-9]|$)' 9f17a1e -- census/round-16/ | grep -v '/transcripts/'` returns nothing (rc=1).

## Findings

1. **L01/L02 need no change of count but do need an explicit binding only for the record.** Cell 152 (`SCORECARD.md:152`) was written at `d7266c5` with `tests/results/r12-maintenance-guard.txt`, whose selftest section holds the literal at bounds (`selftest=PASS ids=6/6`); the command still prints it. Cell 153 was written at `23014d4`; `tools/souji-cert-evidence.py --selftest` still prints `selftest: 36/36 passed`. Both were already base-cell MATCH, so the appended rows pin the observable at the revision instead of relying on the base cell's implicit command.
2. **L03 (external fixture 5/5) has no run binding.** `SCORECARD.md:153` names no 5/5 command and its bytes do not contain `r13-cert-evidence` (`grep -c` → 0), so the script that produces 5/5 (`tests/fixtures/r13-cert-evidence.py`) cannot be a run row under the counter's stem rule (`tools/souji-capability-cells.py`, run-shape branch); the forced probe is refused as BAD-ROW(run-shape). The honest binding is the unchanged round-13 record the cell cites: `census/round-13/verification.json` entry `evidence-external-fixture` gives command `python3 tests/fixtures/r13-cert-evidence.py` and the stdout line `fixture: 5/5 checks passed` — the record is the evidence, not a digit grep hit.
3. **L04/L05 cells state stale literals, and the fixtures restate them in their own notation.** Cell 154's 5/5 now prints `SUMMARY total=5 failed=0 hung=0` (count unchanged); cell 155's 5/5 has grown to `selftest=PASS ids=7/7` (round-13 record entry `structure-selftest` shows the old `selftest=PASS ids=5/5`). Restatements keep the literal out of the argv and carry two integers, so the counter accepts them.
4. **L06/L07 counts are stale and have no committable record.** Cell 158 was written at `163158a` as 18/18 (selftest) and 15/15 (fixture); the commands now print `SELFTEST pass=65 fail=0` and `SUMMARY total=15 failed=0`. No file under `census/round-16/` outside `transcripts/` carries either count, so a run binding is the only observable.
5. **Rows are isolated and effective.** Full enumeration moves exactly 5 mismatches (L03 record, L04-L07 run) and leaves the other 34 ITEM lines unchanged; the counter keys rows by item id with last-row-wins, so these must be the only L01-L07 rows in the appended tail.

## Attack log

Not an attack item. Instrument observation only, disclosed for the L1: the row parser accepts a reason cell that restates a different count than the base cell for `run:` rows (the integer-multiset rule applies only to `record:` rows), which is what makes an honest "grown count" restatement expressible; that is the preregistration's own design and was exercised, not widened, here.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-c1-bind-L01-L07.md` — the seven verbatim rows for the L1 to append, per-item provenance (writing commit, cited record, re-run), the L03 negative probe, both acceptance outputs, the 41-item delta and isolation diff, and the risk list.
- `.ufo/waves/round-31/w1/SwarmExecutor01.md` — this report.

No file in the lane was modified (rows were exercised only in scratch); no tool was installed or upgraded, no pacman transaction, no `git add/commit/push` in the lane, no jj call in the lane.
