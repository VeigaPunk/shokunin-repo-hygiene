# SwarmReviewer02 — round 31 wave 2 — C1 supersession rows L01–L12 audit

## Status
STATUS: PASS — all 12 rows in my range are HONEST: every `run:` argv re-run at the C1 landing commit 24f343c8ffc820c0f89b4252cbdc94ab9a673aab exits 0 and prints the row literal in the last digit-bearing stdout line; every `record:` occurrence opened at that commit is the measurement its cell states (same capability, same run, same count); every reason sentence's writing-commit and record-path claims verify. One minor wording imprecision on L06 (finding 1) that does not change its verdict.

## Evidence
- Scratch: /fast/scratch/hyaku/souji-r31/w2-SwarmReviewer02/c — `git clone -q --no-local` of the lane, origin removed, checkout 24f343c8ffc820c0f89b4252cbdc94ab9a673aab, `rev-parse --show-toplevel` verified, clean tree.
- Rows L01–L12 (SCORECARD.md:367–378) byte-identical at tip 2c16d018e40db7c23420a2c3bb546b52957bcc25 and at 24f343c8; SCORECARD.md has no commits after 24f343c8.
- Base cells read at 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc:152–161; all row `<line>` fields and base literals match census/round-31/c1-cells.tsv (read at prereg 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525).
- Run rows, serially, in the clone at 24f343c8 (rc / last digit-bearing line / row literal):
  - L01 `bash tests/fixtures/r12-maintenance-guard.sh --selftest` → 0 / `selftest=PASS ids=6/6` / 6/6 ✓
  - L02 `python3 tools/souji-cert-evidence.py --selftest` → 0 / `selftest: 36/36 passed` / 36/36 ✓
  - L04 `bash tests/fixtures/r13-quarantine-bounds.sh` → 0 / `SUMMARY	total=5	failed=0	hung=0` / total=5 failed=0 ✓
  - L05 `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` → 0 / `selftest=PASS ids=7/7` / ids=7/7 ✓
  - L06 `python3 tools/souji-landing-gate.py --selftest` → 0 / `SELFTEST	pass=65	fail=0` / pass=65 fail=0 ✓
  - L07 `python3 tests/fixtures/r16-landing-gate.py` → 0 / `SUMMARY	total=15	failed=0` / total=15 failed=0 ✓
  - L11 `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` → 0 / `SUMMARY	total=29	failed=0` / total=29 failed=0 ✓
  - L12 `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` → 0 / `SUMMARY	total=35	failed=0	skipped=2` / total=35 failed=0 ✓
- Record rows, opened at 24f343c8 (occurrence file:line / quote / cell):
  - L03 census/round-13/verification.json:57 — `results[2]` `evidence-external-fixture` (command `python3 tests/fixtures/r13-cert-evidence.py`), stdout ends `ok frozen-tampered\nfixture: 5/5 checks passed\n` — cell "external fixture 5/5" (r13 declared-evidence). The blob's other 5/5 (line 74) is `structure-selftest`, a different capability; the row cites the correct entry.
  - L08 census/round-21/read-fixture-after.txt:34 — `SUMMARY	total=32	pass=32	fail=0	base_discriminating=14`; COMMAND line 1 runs `tests/fixtures/r21-read-root.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py` — cell read32/32; lesson round-21.md:7 pairs "baseline18/32 versus changed32/32".
  - L09 census/round-21/read-fixture-before.txt:34 — `SUMMARY	total=32	pass=18	fail=14	base_discriminating=14`; COMMAND line 1 runs the same fixture with `--tool /var/tmp/souji-r21-base-auditor.py --base-tool /var/tmp/souji-r21-base-auditor.py` — the base auditor named in the COMMAND line, as the reason states — cell base18/32.
  - L10 census/round-21/render-edges-after.txt:5 — `SUMMARY	total=4	pass=4	fail=0`; the four CASE names are exactly `tests/fixtures/r21-read-render-edges.py`'s four cases (fixture lines 15–16); before arm render-edges-before.txt:5 reads `SUMMARY	total=4	pass=0	fail=4`; lesson round-21.md:131–132 pairs the captures — cell renderer4/4.
- Writing commits: d7266c5e9493a3c78687af68d438c2584f75b3c0 wrote the r12 fixture + `tests/results/r12-maintenance-guard.txt` (line 27 `selftest=PASS ids=6/6`) + the 6/6 cell; 23014d40e48e52031939f124ce0ed215ca932c6f wrote the r13 cells and census/round-13/verification.json whose `evidence-selftest` / `evidence-external-fixture` / `structure-selftest` (ids=5/5) / `quarantine-bounds` entries exist there with the stated stdout counts; 163158a706352f1c0ee3521c4da2e5289970db57 wrote the r16 landing-gate cell with 18/18 and 15/15.
- Transcript-only claims: at 24f343c8, `git grep '18/18' -- census/round-16 ':(exclude)census/round-16/transcripts/*'` and the same for '15/15' both return zero hits.
- Blob stability base↔24f343c8 (rev-parse equality): all four record blobs SAME; 7 of 8 run-row scripts SAME; tools/souji-landing-gate.py CHANGED (C2's 8024b540 landed before C1) — the --base blob written over the REV copy re-run: rc=0, same last digit line `SELFTEST	pass=65	fail=0`, so L06 also satisfies A4(c)'s base-blob rule.
- A4(a): all 8 basecmd-bearing items are run rows; all 4 record rows have empty basecmd. A4(d): no shared (record, literal) pair in range.

## Findings
1. (minor, wording; axis calibration) SCORECARD.md:372 (L06 reason) says "the only committed round-16 mentions of that count are under census/round-16/transcripts/" — corpus/lessons/round-16.md:21 also states "Self-test 18/18" (blob unchanged base↔landing). Operative conclusion unaffected: the lesson is outside census/round-16/ (ineligible as a record by the round-set rule) and contains no `pass=65`, so it could not bind the row literal; the run reproduces at both the REV and --base blobs. L06 verdict stays HONEST.

No other findings in L01–L12.

## Attack log
- Tried to break the record rows as WRONG-OCCURRENCE: for each, checked whether the located occurrence belongs to another capability or contradicts the cell. L03's blob carries a second 5/5 (`structure-selftest`, line 74) — the row's reason names `evidence-external-fixture`, so the cited occurrence is the right one; no cross-capability binding. L08/L09 are the before/after arms of the same r21 read-root measurement (lesson round-21.md:7 confirms the pairing and the 14 base-discriminating cases); L10's capture matches the render-edges fixture's exact case list and has a red before arm (0/4). No contradiction found.
- Tried FALSE-REASON on the writing commits: d7266c5, 23014d4, 163158a all exist and each wrote the file(s) its row's reason names, with the stated counts present at those commits (verified in the commit blobs, not just at the landing).
- Tried NOT-REPRODUCED via A4(c): the only changed script in range is tools/souji-landing-gate.py; ran its --base blob over the REV copy — same rc and same literal line, so the row does not depend on the in-round C2 edit.
- Checked A4(a)/(d) shape by hand against c1-cells.tsv: no record row hides a base command; no shared (record, literal) occurrence.

## Deliveries
- .ufo/waves/round-31/w2/deliver-c1-audit-L01-L12.md — full per-row audit (12/12 HONEST), cross-row checks, findings.
- .ufo/waves/round-31/w2/SwarmReviewer02.md — this report.
