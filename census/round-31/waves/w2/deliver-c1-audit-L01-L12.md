# deliver-c1-audit-L01-L12 — SwarmReviewer02, round 31 wave 2

Scope: C1 supersession rows L01–L12 of `### Round 31 capability-cell supersessions` (SCORECARD.md:367–378 at tip 2c16d018e40db7c23420a2c3bb546b52957bcc25; byte-identical at C1 landing 24f343c8ffc820c0f89b4252cbdc94ab9a673aab). Base cells read at 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc lines 152–161. All `run:` argvs executed serially in a scratch clone at 24f343c8 (origin removed); all `record:` occurrences opened at 24f343c8.

**Verdict: 12/12 HONEST.** No WRONG-OCCURRENCE, no FALSE-REASON, no NOT-REPRODUCED. One wording imprecision on L06 (finding 1) that does not change its verdict.

## Per-row audit

### L01 — SCORECARD.md:152 — literal `6/6` — run: `bash tests/fixtures/r12-maintenance-guard.sh --selftest` — HONEST
- Base cell (base:152): "`bash tests/fixtures/r12-maintenance-guard.sh --selftest` → 6/6 PASS, exit 0; `tests/results/r12-maintenance-guard.txt`" (r12).
- Re-run at 24f343c8: rc=0, last digit line `selftest=PASS ids=6/6` — literal present.
- Reason: written at d7266c5e9493a3c78687af68d438c2584f75b3c0 — verified: that commit adds `tests/fixtures/r12-maintenance-guard.sh` (241 lines) and `tests/results/r12-maintenance-guard.txt` (40 lines) and the SCORECARD cell. `tests/results/r12-maintenance-guard.txt:27` records `selftest=PASS ids=6/6`; blob unchanged base→landing (`9f17a1e…:tests/results/r12-maintenance-guard.txt` = `24f343c8…:…`, verified by rev-parse).
- Script blob unchanged base→landing, so the re-run is the base-blob run (A4(c) trivially satisfied).

### L02 — SCORECARD.md:153 — literal `36/36` — run: `python3 tools/souji-cert-evidence.py --selftest` — HONEST
- Base cell (base:153): "`python3 tools/souji-cert-evidence.py --selftest` → 36/36; external fixture 5/5; …" (r13).
- Re-run at 24f343c8: rc=0, last digit line `selftest: 36/36 passed`.
- Reason: written at 23014d40e48e52031939f124ce0ed215ca932c6f — verified: that commit edits SCORECARD.md and census/round-13/verification.json; its SCORECARD diff introduces the declared-evidence cell with 36/36; the `evidence-selftest` entry exists at 23014d4 with last digit line `selftest: 36/36 passed`.
- Script blob unchanged base→landing.

### L03 — SCORECARD.md:153 — literal `5/5` — record: `census/round-13/verification.json` — HONEST
- Base cell (base:153): "external fixture 5/5" (declared-evidence integrity, r13).
- Occurrence: census/round-13/verification.json:57 (at 24f343c8), the `results[2]` entry named `evidence-external-fixture`, command `python3 tests/fixtures/r13-cert-evidence.py`, stdout ending `ok frozen-tampered\nfixture: 5/5 checks passed\n`. Quote (≤25 words): `ok frozen-tampered\nfixture: 5/5 checks passed\n`.
- IS the measurement: yes — same capability (r13 declared-evidence external fixture), same run (the entry's recorded stdout written by the same commit 23014d4 that wrote the cell), same count (5/5). The other `5/5` in the blob (line 74, `selftest=PASS ids=5/5`) belongs to `structure-selftest` (repository-structure capability) and is NOT the occurrence this row cites; the row's reason names the correct entry, so no cross-capability binding.
- Record blob unchanged base→landing; path under census/round-13/ (round set {13}); no waves/transcripts component; basecmd empty so a record row is allowed under A4(a).

### L04 — SCORECARD.md:154 — literal `total=5 failed=0` — run: `bash tests/fixtures/r13-quarantine-bounds.sh` — HONEST
- Base cell (base:154): "`bash tests/fixtures/r13-quarantine-bounds.sh` → 5/5; same corrected fixture baseline red, …" (r13).
- Re-run at 24f343c8: rc=0, last digit line `SUMMARY	total=5	failed=0	hung=0` — literal present.
- Reason: written at 23014d4 citing the `quarantine-bounds` entry — verified: entry exists at 23014d4, last digit line `SUMMARY	total=5	failed=0	hung=0`.
- Script blob unchanged base→landing.

### L05 — SCORECARD.md:155 — literal `ids=7/7` — run: `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` — HONEST
- Base cell (base:155): "…`bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` → 5/5; …" (r13).
- Re-run at 24f343c8: rc=0, last digit line `selftest=PASS ids=7/7` — the grown count, restated in the fixture's notation (A2 effective-statement reading; the reason sentence says exactly this).
- Reason: written at 23014d4 citing the `structure-selftest` entry as ids=5/5 — verified: entry exists at 23014d4 with last digit line `selftest=PASS ids=5/5`.
- Script blob unchanged base→landing.

### L06 — SCORECARD.md:158 — literal `pass=65 fail=0` — run: `python3 tools/souji-landing-gate.py --selftest` — HONEST (one wording nit, finding 1)
- Base cell (base:158): "`python3 tools/souji-landing-gate.py --selftest` 18/18; `python3 tests/fixtures/r16-landing-gate.py` 15/15; …" (r16).
- Re-run at 24f343c8: rc=0, last digit line `SELFTEST	pass=65	fail=0` — literal present.
- A4(c) robustness: tools/souji-landing-gate.py CHANGED base→landing (C2's 8024b540 reading-precision work landed before C1). I re-ran the --base blob written over the REV copy: rc=0, same last digit line `SELFTEST	pass=65	fail=0`. So the binding holds under the counter's base-blob rule, not only against the changed REV copy.
- Reason: written at 163158a706352f1c0ee3521c4da2e5289970db57 as 18/18 — verified: that commit's SCORECARD diff introduces the landing-claim-gate cell with "`python3 tools/souji-landing-gate.py --selftest` 18/18; `python3 tests/fixtures/r16-landing-gate.py` 15/15". At 24f343c8, `git grep '18/18' -- census/round-16 ':(exclude)census/round-16/transcripts/*'` returns zero hits: every census/round-16 occurrence of 18/18 is under transcripts/, which the record rule excludes. A record row was impossible anyway: the record rule requires the row literal's integer multiset to equal the base literal's ({18,18}); the row literal `pass=65 fail=0` is {65,0}, so only a run row can carry the grown count. Operative reasoning sound.
- Nit: corpus/lessons/round-16.md:21 (blob unchanged base→landing) also says "Self-test 18/18", so "the only committed round-16 mentions of that count are under census/round-16/transcripts/" is overbroad if "round-16 mentions" is read beyond census/round-16/. The lesson is outside census/round-16/ (ineligible as a record by the round-set rule) and contains no `pass=65`, so it could not have served as the record either — the conclusion stands.

### L07 — SCORECARD.md:158 — literal `total=15 failed=0` — run: `python3 tests/fixtures/r16-landing-gate.py` — HONEST
- Base cell (base:158): "`python3 tests/fixtures/r16-landing-gate.py` 15/15" (r16).
- Re-run at 24f343c8: rc=0, last digit line `SUMMARY	total=15	failed=0` — literal present; same count as the cell (15/15) in the fixture's notation.
- Reason: written at 163158a as 15/15 — verified (same diff line as L06). At 24f343c8, `git grep '15/15' -- census/round-16 ':(exclude)census/round-16/transcripts/*'` returns zero hits — "the count appears in no committed census/round-16 record outside transcripts/" is true.
- Script blob unchanged base→landing.

### L08 — SCORECARD.md:159 — literal `total=32	pass=32` — record: `census/round-21/read-fixture-after.txt` — HONEST
- Base cell (base:159): "r21 read32/32 (base18/32), renderer4/4; …" (seat transcript audit).
- Occurrence: census/round-21/read-fixture-after.txt:34 (at 24f343c8): `SUMMARY	total=32	pass=32	fail=0	base_discriminating=14`. Quote (≤25 words): `SUMMARY	total=32	pass=32	fail=0	base_discriminating=14`.
- IS the measurement: yes — COMMAND line 1 runs `tests/fixtures/r21-read-root.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py` (the changed auditor), i.e. the r21 read-root measurement of the repaired classifier; corpus/lessons/round-21.md:7 pairs it: "Initial same-fixture baseline18/32 versus changed32/32 (14 base-discriminating), `census/round-21/read-fixture-{before,after}.txt`". Same capability (seat transcript audit read-root class), same run, same count (32/32 = cell's read32/32).
- Record blob unchanged base→landing; under census/round-21/ (round set {16,20,21}); basecmd empty so record row allowed.

### L09 — SCORECARD.md:159 — literal `total=32	pass=18` — record: `census/round-21/read-fixture-before.txt` — HONEST
- Base cell (base:159): "base18/32".
- Occurrence: census/round-21/read-fixture-before.txt:34 (at 24f343c8): `SUMMARY	total=32	pass=18	fail=14	base_discriminating=14`. Quote (≤25 words): `SUMMARY	total=32	pass=18	fail=14	base_discriminating=14`.
- IS the measurement: yes — COMMAND line 1 runs the same fixture `tests/fixtures/r21-read-root.py` with `--tool /var/tmp/souji-r21-base-auditor.py --base-tool /var/tmp/souji-r21-base-auditor.py`, i.e. against the base auditor, which the COMMAND line names exactly as the reason states. 18+14=32 consistent. Same capability, same run family (the before arm of the same r21 measurement), same count (base18/32).
- Record blob unchanged base→landing.

### L10 — SCORECARD.md:159 — literal `total=4	pass=4` — record: `census/round-21/render-edges-after.txt` — HONEST
- Base cell (base:159): "renderer4/4".
- Occurrence: census/round-21/render-edges-after.txt:5 (at 24f343c8): `SUMMARY	total=4	pass=4	fail=0`. Quote (≤25 words): `SUMMARY	total=4	pass=4	fail=0`.
- IS the measurement: yes — the capture's four CASE lines (`uri-mixed`, `uri-upper`, `conflicts`, `raw-conflicts`) are exactly the four cases of `tests/fixtures/r21-read-render-edges.py` (fixture lines 15–16 define the same four names), and corpus/lessons/round-21.md:131–132 pairs the captures: "`tests/fixtures/r21-read-render-edges.py` goes0/4→4/4 (`render-edges-before.txt`, `render-edges-after.txt`)". The before arm (render-edges-before.txt:5) reads `SUMMARY	total=4	pass=0	fail=4` — the red arm the after count supersedes. Same capability (renderer edge cases), same run, same count (renderer4/4).
- Record blob unchanged base→landing.

### L11 — SCORECARD.md:160 — literal `total=29 failed=0` — run: `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` — HONEST
- Base cell (base:160): "`python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` 29/0; …" (r17).
- Re-run at 24f343c8: rc=0, last digit line `SUMMARY	total=29	failed=0` — literal present; same count as the cell's 29/0 in the fixture's notation.
- Reason claims only the re-run ("Re-running the base cell command at the measured revision prints SUMMARY total=29 failed=0") — true.
- Script blob unchanged base→landing.

### L12 — SCORECARD.md:161 — literal `total=35 failed=0` — run: `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` — HONEST
- Base cell (base:161): "`bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` 35/0 (5fa6017 tools: 13 fail); …" (r17).
- Re-run at 24f343c8: rc=0, last digit line `SUMMARY	total=35	failed=0	skipped=2` — literal present; the reason's "prints SUMMARY total=35 failed=0 skipped=2" matches byte-for-byte including the skip count.
- Reason claims only the re-run — true.
- Script blob unchanged base→landing.

## Cross-row checks
- Row `<line>` fields all equal the items' base lines in census/round-31/c1-cells.tsv (L01→152 … L12→161); base literals match the enumeration (6/6, 36/36, 5/5, 5/5, 5/5, 18/18, 15/15, 32/32, 18/32, 4/4, 29/0, 35/0).
- A4(a): every item with a non-empty basecmd (L01, L02, L04, L05, L06, L07, L11, L12) is a run row; every record row (L03, L08, L09, L10) has an empty basecmd in the enumeration.
- A4(d): no two of my rows share a (record path, literal) pair — three distinct records, three distinct literals.
- Record rule: all four record blobs are byte-identical base↔landing (rev-parse equality verified); all paths under census/round-<K>/ with K in the item's round set; no waves/transcripts components.
- Run rule: all eight argvs exit 0 and print the row literal in the last digit-bearing stdout line; all eight scripts are blob-identical base↔landing except tools/souji-landing-gate.py (L06), whose --base blob was additionally run and prints the same literal (A4(c) satisfied).

## Findings
1. (minor, wording; would harm calibration only if the reason were read as a broad fact) L06 reason "the only committed round-16 mentions of that count are under census/round-16/transcripts/" — corpus/lessons/round-16.md:21 also states "Self-test 18/18" (blob unchanged base→landing). The operative conclusion is unaffected: the lesson is outside census/round-16/ so it is not an eligible record, and it contains no `pass=65`, so it could not bind the row literal; the run reproduces. Verdict stays HONEST. Location: SCORECARD.md:372 (row), corpus/lessons/round-16.md:21.

No other findings in L01–L12.
