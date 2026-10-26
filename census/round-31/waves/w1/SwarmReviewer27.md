# SwarmReviewer27 — independent C1 base re-derivation (souji r31 wave 1)

## Status

STATUS: PASS — my base-clone re-derivation of L02/L06/L11/L22/L33/L35/L40 agrees with the frozen counter's do-nothing ITEM lines on exit code and last digit-bearing stdout line, item for item; two runs of each are byte-identical (no nondeterminism observed). L08/L16 name one record observable each (neither blob shows its literal); L24 names no observable at all.

## Evidence

Setup: `git clone -q --no-local` of the lane into `/fast/scratch/hyaku/souji-r31/ReDeriveC1Base/c`, origin removed, detached at base; `git rev-parse --show-toplevel` → `/fast/scratch/hyaku/souji-r31/ReDeriveC1Base/c`; HEAD = `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`. Base commands were run from the clone root with a fresh `TMPDIR` and `GIT_CONFIG_NOSYSTEM=1`, `GIT_DIR`/`GIT_WORK_TREE` unset, mirroring the counter's `run()` (tools/souji-capability-cells.py:117-141) and its normalization (tmp→`<TMP>`, 12+ hex→`<HEX>`, `N.Ns`→`<DUR>`, whitespace collapsed; stderr fallback only when stdout has none).

Counter command (both runs):
`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-capability-cells.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --only L02,L06,L11,L22,L33,L35,L40 --scratch /fast/scratch/hyaku/souji-r31/ReDeriveC1Base/cnt`

Per-item agreement (mine = independent run in base clone; counter = its ITEM line at rev `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`):

| item | basecmd (census/round-31/c1-cells.tsv) | mine rc / last digit-bearing stdout line | counter rc / line | verdict both |
|---|---|---|---|---|
| L02 | `python3 tools/souji-cert-evidence.py --selftest` | 0 / `selftest: 36/36 passed` | 0 / same | MATCH |
| L06 | `python3 tools/souji-landing-gate.py --selftest` | 0 / `SELFTEST pass=65 fail=0` | 0 / same | RUN-MISMATCH |
| L11 | `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` | 0 / `SUMMARY total=29 failed=0` | 0 / same | RUN-MISMATCH |
| L22 | `python3 tools/souji-rev-pin.py --selftest` | 0 / `SUMMARY total=11 failed=0` | 0 / same | RUN-MISMATCH |
| L33 | `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` | 0 / `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | 0 / same | RUN-MISMATCH |
| L35 | `python3 -B tests/fixtures/r24-coverage-agreement.py` | 2 / `r24-coverage-agreement.py: error: the following arguments are required: --tool` | 2 / same | RUN-MISMATCH |
| L40 | `python3 -B tests/fixtures/r30-landing-gate-discovery.py --tool tools/souji-landing-gate.py` | 0 / `cases=7 pass=7 control=FALSE-GREEN-REJECTED` | 0 / same | MATCH |

Counter SUMMARY (both runs): `items=7 bound_run=2 bound_record=0 unbound=0 mismatches=5 partial=1 rev=1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`; exit code 1 both runs, consistent with the frozen docstring: "Exit 0 iff mismatches=0; 1 otherwise; 2 could-not-evaluate." (tools/souji-capability-cells.py:22). My two independent runs: byte-identical output. Counter run 1 vs run 2: `diff` empty (COUNTER-RUNS-IDENTICAL), rc1=rc2=1.

Equivalence of my base run to the counter's rev run: `git diff --stat 9f17a1e..1d45496 -- . ':(exclude)census/round-31' ':(exclude).ufo'` shows exactly one file, `tools/souji-capability-cells.py` (+285); full diff is 10 files, all `census/round-31/*` plus that counter. None of the seven commanded scripts differ base↔prereg, so the base-clone runs exercise the same bytes the counter ran at the prereg rev.

L08/L16/L24 base lines (SCORECARD.md at base, evidence cell):

- :159 (L08, literal 32/32): "r21 read32/32 (base18/32), renderer4/4; oracle2372 keys over192 files, tp3/fp0/fn0; all401 old tuples identical; `census/round-21/oracle-acceptance.json`" — one named observable: the committed record `census/round-21/oracle-acceptance.json` (round 21 ∈ rounds {16,20,21}; no `waves`/`transcripts` component; blob unchanged base↔prereg, oid `8c03a568052172e6aadb413b596aea9063b87db9`). No command in the cell. That blob does NOT contain `32/32` at digit boundaries (`grep -coE '(^|[^0-9])32/32([^0-9]|$)'` → 0), so this record alone cannot show L08 under the frozen record rule.
- :164 (L16, literal 61/0): "`census/round-18/final-verification-4800fd7.json` (selftest 61/0, pointer fixture 11/0, r16 fixture 15/0); S078" — one named observable: the record `census/round-18/final-verification-4800fd7.json` (round 18 ∈ {16,18}; unchanged blob `0d37a0567b0e87e8407fff24c68800bd4cd4251d`). No command in the cell. The blob does NOT contain `61/0` at digit boundaries (grep count 0).
- :168 (L24, literal 118/0): "final r21 18-step receipts: auditor selftest118/0; r19-seat-audit-shapes17/0 (base12); r20-audit-contract78/0 (base11)" — NO observable named: no command (no python3/bash argv), no path (the tokens `r19-seat-audit-shapes` and `r20-audit-contract` are bare fixture stems, not `tools/`- or `tests/fixtures/`-rooted paths and not `census/round-K/` records). The cell offers nothing a binding could cite without importing an observable from outside the cell text.

## Findings

1. Counter agreement (tools/souji-capability-cells.py run at rev `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`): all 7 re-derived items agree on rc, normalized last digit-bearing stdout line, and verdict. No discrepancy found in the checked slice; no sign the counter inflates or deflates the do-nothing state.
2. Determinism: two counter runs byte-identical (empty diff, same exit 1); two independent base-clone runs byte-identical. No nondeterminism observed. [INFERENCE] stability beyond these two runs per command is likely but not proven.
3. The five do-nothing mismatches are genuine pre-round state, not counter artifacts: L06's gate selftest now prints `SELFTEST pass=65 fail=0` (cell says 18/18); L33's fixture prints `cases=12 pass=12` (cell says 8/8); L35's enumerated basecmd lacks `--tool` and exits 2; L11/L22 print `total=N failed=0`, which does not contain the literal string `N/0` at digit boundaries (the frozen MATCH rule is a string occurrence, tools/souji-capability-cells.py:96-98). L02 and L40 already MATCH from the base cell, matching the full-run base figure `bound_run=7` (the other five pre-bound items are outside my slice).
4. L08 (SCORECARD.md:159): cell names exactly one observable — record `census/round-21/oracle-acceptance.json` — but that blob never states `32/32` at digit boundaries, so the only observable the cell names cannot itself show the literal; a binding row must supply a different observable.
5. L16 (SCORECARD.md:164): same shape — record `census/round-18/final-verification-4800fd7.json` named, unchanged since base, but it does not contain `61/0` at digit boundaries.
6. L24 (SCORECARD.md:168): the cell names no observable at all (no command, no record path); only bare fixture stems in prose. It is the purest UNBOUND case of the three.
7. Equivalence guard: base↔prereg diff touches only `census/round-31/*` and the counter itself, so base-run ≡ rev-run for all seven commanded scripts (per-diff file list above).

## Attack log

None — my item is verification, not an attack. No counter defect, gaming vector, or frozen-contract violation surfaced in the checked slice.

## Deliveries

- `.ufo/waves/round-31/w1/SwarmReviewer27.md` (this report; the only lane write).

Tooling record: no tools installed or upgraded this run (operator 2026-10-19 authorization unused). Scratch `/fast/scratch/hyaku/souji-r31/ReDeriveC1Base/` removed after writing this report; nothing was delivered from scratch. Lane touched read-only plus this one delivery file; no git/jj mutations in the lane.
