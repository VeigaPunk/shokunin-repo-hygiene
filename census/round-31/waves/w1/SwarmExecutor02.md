# SwarmExecutor02 — C1 bindings for L08–L12 (round 31, wave 1)

## Status

STATUS: PASS — all five assigned literals (L08/L09/L10 on SCORECARD.md:159, L11 on :160, L12 on :161) have supersession rows the frozen counter reads MATCH at proof revision `60d8f14` (`bound_run=2 bound_record=3 unbound=0 mismatches=0`), twice byte-identical, rc=0.

## Evidence

Base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; enumeration `census/round-31/c1-cells.tsv` at list-rev
`1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; lane tip `1b811368461785040e955f41f9c97e62f61fd67c` with
`git diff --stat 9f17a1e..1b81136 -- SCORECARD.md` empty (0 lines), so base line numbers are the tip's.

1. Baseline for the five items, measured (`--only L08,L09,L10,L11,L12 --rev 9f17a1e…`, counter at
   `tools/souji-capability-cells.py`):
   `SUMMARY items=5 bound_run=0 bound_record=0 unbound=3 mismatches=5` — L08/L09/L10 `UNBOUND`;
   L11/L12 `RUN-MISMATCH` with `observed=SUMMARY total=29 failed=0` and
   `observed=SUMMARY total=35 failed=0 skipped=2`.
2. Provenance: `git log -L159,159:SCORECARD.md` → `4eb2fda` (r21), `af73b8b` (r22, 2026-10-25, word change
   only); `git log -L160,161:SCORECARD.md` → `d98065d` (r17).
3. Stem rule (why L08–L10 are records): at base, 231 paths under `tools/`+`tests/fixtures/`, **0** basename
   stems occur on SCORECARD.md:159; `r17-census-hygiene` occurs on :160 and `r17-jj-receipts` on :161.
4. Record blobs unchanged base→tip: `read-fixture-after.txt` 63ed0ae4…, `read-fixture-before.txt` 3bfe37c1…,
   `render-edges-after.txt` 41998d40… (all under `census/round-21/`, no `waves`/`transcripts` component).
5. Acceptance proof: origin-less `--no-local` clone at `/fast/scratch/hyaku/souji-r31/C1BindB/r.1skKGk/c`,
   rows appended and committed as `60d8f14301c6d314816988c594d62934a61e5b78`; counter run twice:

```
ITEM	L08	SCORECARD.md:159	literal=total=32	pass=32	superseded	binding=record	MATCH	census/round-21/read-fixture-after.txt
ITEM	L09	SCORECARD.md:159	literal=total=32	pass=18	superseded	binding=record	MATCH	census/round-21/read-fixture-before.txt
ITEM	L10	SCORECARD.md:159	literal=total=4	pass=4	superseded	binding=record	MATCH	census/round-21/render-edges-after.txt
ITEM	L11	SCORECARD.md:160	literal=total=29 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh rc=0 observed=SUMMARY total=29 failed=0
ITEM	L12	SCORECARD.md:161	literal=total=35 failed=0	superseded	binding=run	MATCH	bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools rc=0 observed=SUMMARY total=35 failed=0 skipped=2
SUMMARY items=5 bound_run=2 bound_record=3 unbound=0 mismatches=0 partial=1 rev=60d8f14301c6d314816988c594d62934a61e5b78
```

6. Negative control (same clone, tabs replaced by spaces, commit
   `db93191858e245289d0bc82468a1d0e4cd02e0e7`): L08/L09/L10 `RECORD-MISMATCH`,
   `mismatches=3` — the tab bytes are load-bearing, not incidental.

## Findings

1. **SCORECARD.md:159 cites a record that does not show its own counts.** The cell cites
   `census/round-21/oracle-acceptance.json`, which holds the oracle figures (`tp=3 fp=0 fn=0`), while
   `read32/32`, `base18/32` and `renderer4/4` are the read/render fixtures' SUMMARY totals
   (`census/round-21/read-fixture-after.txt:34`, `read-fixture-before.txt:34`, `render-edges-after.txt:5`).
   The three counts are bound to those captures, which are byte-equal blocks of the `read32`/`render4`
   command stdout in `census/round-21/final-code-verification.json` — the record `corpus/lessons/round-21.md:192`
   names as the holder of those numbers.
2. **SCORECARD.md:159's counts can never take a run binding.** At base no `tools/` or `tests/fixtures/`
   basename stem occurs on that line (231 candidates, 0 hits), so the frozen counter's stem rule forces the
   record path for L08–L10. Location: `git ls-tree -r --name-only 9f17a1e -- tools tests/fixtures` vs
   `git show 9f17a1e:SCORECARD.md | sed -n 159p`.
3. **SCORECARD.md:160's cited matrix records the count in JSON keys, not as `29/0`.** In
   `census/round-17/c1-matrix-4f48343.json`, `arms.changed["r17-hygiene"]` has `total` 29, `failed` 0 and 29
   PASS case verdicts; the literal appears nowhere, so only the fixture re-run shows it (`SUMMARY total=29
   failed=0`).
4. **SCORECARD.md:161's record and the current fixture disagree on `skipped`.** The row's record
   `census/round-17/jj-receipts-4f48343.txt` ends `SUMMARY total=35 failed=0 skipped=0`; the same fixture now
   prints `skipped=2` with total and failed unchanged. Disclosed in the delivery; the row literal states the
   unchanged pair only.
5. **Tab bytes inside three row literals.** The `record` branch compares raw bytes, so L08/L09/L10 literals
   must keep one literal TAB between `total=…` and `pass=…`; expansion to spaces turns all three into
   `RECORD-MISMATCH` (measured at `db93191`). Integration note is in the delivery.

## Deliveries

- `.ufo/waves/round-31/w1/deliver-c1-bind-L08-L12.md` — exact rows (byte-verified, 3 tabs), provenance,
  record hashes, baseline, acceptance proof, negative control, L1 risks.
- `.ufo/waves/round-31/w1/SwarmExecutor02.md` — this report.

Scope note: these are 5 of the 41 enumerated items; the global C1 target also needs the other seats' rows
(sibling `deliver-c1-bind-L30-L41.md` covers L30–L41; no overlap with L08–L12). No tool install or upgrade,
no `pacman` transaction, no lane git/jj mutation; scratch `/fast/scratch/hyaku/souji-r31/C1BindB` removed.
