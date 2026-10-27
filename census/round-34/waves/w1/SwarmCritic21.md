## Status
STATUS: PARTIAL — target substitution is falsified; the two full restatement paths were not both reproduced as commits.

## Evidence
- Read frozen contract `census/round-34/preregistration.txt` and counter `census/round-34/c1-counter.py` at lane tip `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.
- `python3 -B .../c1-counter.py --root ... --rev 51acb5fb6fa38a6b593b3badb674cec559d7eb2c --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/AttackC1Reachability --only G01,E18` → G01 AGREE/original; E18 MISMATCH/original; `SUMMARY items=2 agree=1 mismatches=1 restated=0 partial=1` (exit 1). Load recorded immediately before run: `26.77 14.18 6.99 ...`; ITEM load was 30.52.
- Frozen base control receipt `census/round-34/records/controls-c1-do-nothing.txt:3-4,46,63` records G01 agreeing, E18 mismatching (`selftest=PASS ids=7/7` vs expected 5/5), and 25 mismatches overall.
- Counter `judge()` at `census/round-34/c1-counter.py:172-251,253-315` validates cause independently, then emits only AGREE/MISMATCH and status original/restated. `main()` increments `restated` for every row and reports the count, not whether it repaired a prior mismatch.

## Findings
1. A row for an already-agreeing item cannot substitute for repairing a stale item: `judge()` selects rows by item id; a row changes only that item's verdict. The observed G01/E18 pair demonstrates an agreeing and stale item under the same frozen counter. E18 remains a mismatch absent a valid E18 row; an extra valid G01 row cannot change it. **Impacted axis:** C1 calibration; no reachability attack on `mismatches=0` by padding agreeing ids.
2. The counter does not distinguish a legitimately restated already-agreeing item from a repaired stale item. For `same`, it requires a touched item file and a genuine parent-holds/cause-fails transition, but does not require the item to have mismatched at the frozen base. If such a G01 cause exists, the end verdict is still AGREE/restated. `SUMMARY ... restated=N` counts rows only, and the frozen target expressly does not constrain that count. This is observable padding, not target bypass: stale items still need their own valid correction or to agree at measurement. **Impacted axis:** calibration/provenance interpretation.
3. Cost comparison: [INFERENCE] an agreeing-item row adds a full cause search/validation (two historical item executions for `same`) plus one measured execution, but reduces zero mismatches. An honest stale-item `same` row uses the same validation and measured-run work while reducing one mismatch; so padding is strictly dominated for achieving the target. I did not reproduce committed-row versions of both paths; only the original G01/E18 readings were executed.
4. No landing/tip-only row window: each named revision is separately evaluated, and `SCORECARD.md` must retain the frozen list-revision bytes (append-only). A row added after landing cannot repair the landing reading; a later row must also pass at tip. A row present only at one measurement cannot satisfy both. **Impacted axis:** C1 measurement integrity.
5. Cause plausibility anchor: preregistration's C1 contract requires an executed cause; the E18 historical cause is named in amendment A5 (`728b2ce71acbe574ae3036b456724d0a3d6f8f08`). I did not claim a reproduction of its row-level acceptance.

## Attack log
- Candidate attack: add `same` restatement for G01 with a real transition cause, while leaving E18 stale. Reproduced underlying state, not the candidate row: G01 agrees and E18 mismatches. The frozen per-item judge means target remains unreachable by this substitution. No counter/predicate modification proposed.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-c1-reachability.txt`
