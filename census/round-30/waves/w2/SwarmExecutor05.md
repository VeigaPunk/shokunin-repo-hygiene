# SwarmExecutor05 — souji r30 w2, lane fleet repository & workspace hygiene

## Status
STATUS: PASS — the no-harm attack ran over committed bytes at base 9420341d and tip 9dcd3676; C1's "met" reading was attacked directly and holds serially, but the no-harm set found one counter that got worse (declared-evidence 21→22) and one instrument that reports a false C1 miss when two seats run it at once.

## Evidence
Read-only over committed bytes (`git -C <lane> cat-file`/`ls-tree`); `sources-census.sh validate` on the live tree (SOURCES.md unmodified there). Python 3.14.8, git 2.56.0, jj 0.45.1-7c41cdeb. No installs or updates (pacman paused host-wide; nothing needed).

Full receipt table with raw outputs: `.ufo/waves/round-30/w2/deliver-no-harm-records.txt` (checks C1–C9, receipts R1–R3).

| instrument | base 9420341d | tip 9dcd3676 | verdict |
|---|---|---|---|
| `tools/souji-registry-agreement.py --list-rev b8cb4b31` | `k1=0 k2=0 mismatches=0` rc=0 | same, rc=0 | HOLDS; registry rows 143→145 |
| `tools/souji-coverage-agreement.py` | `grounded=15 mapped=15 dangling=0 mismatches=0` | `grounded=16 mapped=16 dangling=0 mismatches=0` | HOLDS; +1 grounded |
| `tools/souji-declared-evidence.py --rev` | `assertions=175 resolved=154 skipped=278 mismatches=21` rc=1 | `assertions=181 resolved=159 skipped=283 mismatches=22` rc=1 | **WORSE by 1** (F1) |
| `census/round-29/c2-counter.py` | `manifests=4 failed=0 uncovered=0 floor_violations=0` rc=0 (r26 1381 / r27 124 / r28 75 / r29 131) | `manifests=5 …` rc=0 (r30 150) | HOLDS; r26–r29 still verify |
| `souji-wave-evidence-capture.sh 30 --verify --rev 9dcd3676` | — | `records=150 failed=0 uncovered=0` rc=0 | HOLDS |
| `scripts/sources-census.sh validate --root … souji` | 36 W04 by bytes (`--file`) | rc=0, `ok`, 36 W04, identical id set | HOLDS |
| `tools/souji-capability-agreement.py` (C1) | A3: `mismatches=12` (v1 recorded 13; gap = R18) | A3 `k1=0 k2=0 mismatches=0 rows=18 pointers=10`; v1 identical; also 0 at 7b16731 | HOLDS serially; concurrency defect (F2) |
| `tools/souji-axis-check.py` | — | `claims=3 flags=0` rc=0 | HOLDS |
| SCORECARD.md:13–15 axes | calibration 7, coverage 8, operability 8 | identical | HOLDS |

## Findings
1. **declared-evidence mismatch added by the C1 landing — `SCORECARD.md:322`, introduced at 7b16731** (calibration surface, DEFECT-NOT-FATAL). The only tip-only non-resolving assertion is ``.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv``, class A `mismatch:path-absent`. It is gitignored (`.gitignore:1:.ufo/waves/`) and therefore absent from every commit; `git log -S` names 7b16731 as the sole commit that added the token. Quote (SCORECARD.md:322, blob at 9dcd3676): "Literal provenance per row: `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`". Content is durable, not lost: `census/round-30/waves/w1/deliver-c1-literal-history.tsv` is committed, sha256 `9cb230679d3756956eb8cde1d3b0465824d5a63df52d483742d65ecac474b03d`, byte-equal to the live file, and carries the matching committed manifest record. This is the defect class C2 removed from the gate, reappearing on a claim surface the gate never reads.
2. **The frozen C1 counter is not concurrency-safe — `tests/fixtures/r23-record-agreement.py:67`** (calibration-instrument operability, DEFECT-NOT-FATAL; target literals untouched). Quote: `SCRATCH_ROOT = "/var/tmp/souji-r23-ExecFixtureAgreement"`, with `:105  shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)`. Two *identical* full C1 runs at 9dcd3676, launched concurrently with separate `--scratch` and separate TMPDIR, returned `mismatches=1` (R14, `rc=1`, `observed=case=1 expect=rc=0 mismatches=0 keys=4 json-bound got=rc=0 …`) and `mismatches=0`. Serial `--only R14` is `rc=0 … CORRECTED`. Same fixed-root pattern at `tests/fixtures/r29-registry-agreement.py:18` (`BASE = '/var/tmp/souji-r29-c1-fixture'`, row R17); row R18's root is shared but its runs use `mktemp -d …/run.XXXXXX`, and R01/R04 already use `mktemp`. Consequence: two wave-2 seats (or L1 plus a seat) evaluating C1 simultaneously can read a false `mismatches=1` against a target that demands exactly 0.
3. **Post-claim stale frontier text still present at tip — `corpus/README.md:46` and `:216`** (coverage bookkeeping, DEFECT-NOT-FATAL). Quotes: "remaining: keep-ref expiry unmeasured, fleet exposure numerator re-census." (:46) versus "F1 — keep-ref expiry is now measured (the entry above; jj 0.45.1, eight `RESULT` steps," (:623), in the same committed file, while :39/:604 name `knowledge/jj-keep-ref-expiry.md`. Wave 1 routed it as an L1 act (`census/round-30/waves/w1/deliver-sources-rows.md:168`: "flipping that line is a C3/L1 act, not a rows act — noted, not done"); it is still unfixed. No counter leg reads :46, so no frozen SUMMARY moves.
4. **Not a defect, recorded so it is not "corrected" wrongly:** the 13 `R30-CORRECTION` lines at tip vs 12 rows the A3 counter reports `CORRECTED` is by design. `SCORECARD.md:314 R18 … observed=Usage: bash tools/souji-wave-evidence-capture.sh …` is load-bearing for the frozen v1 instrument (v1 `--only R18` → banner observation, `CORRECTED`) and inert under A3 (R18 `MATCH` on stdout). It also explains v1 base 13 vs A3 base 12: R18 is the one-row gap.

## Attack log
- **L1 reading "C1 met at 7b16731 and at tip under v1 and A3"** — attacked by rerunning the frozen counter serially at 7b16731 (A3: `mismatches=0`), at tip under A3 (`0`) and at tip under the v1 bytes extracted from d4928ec (`0`). Verdict: **HOLDS**. Non-vacuity: A3 at base reads 12 mismatches, `KINDS value=4 shape=7 rc=1`, and `controls.tsv` records v1 base 13 — the counter discriminates.
- **Same reading under concurrent evaluation** — attacked by running two identical counters at once: `mismatches=1` vs `0`. Verdict: **BROKEN (instrument, not the claim)**; see F2.
- **Calibration no-harm (registry agreement, base vs tip)** — HOLDS (`0/0/0` both; rows grew 143→145, so the zero is not vacuous).
- **Coverage no-harm (coverage agreement, base vs tip)** — HOLDS (`dangling=0 mismatches=0` both; grounded 15→16).
- **Coverage no-harm (sources-census validate)** — HOLDS (rc=0, 36 W04 at both byte sets, identical id set; the `--file`-mode E11 delta of 4 is a missing-fleet-tree artifact, real-root validate shows 0 E11 and the four ids all name the new existing entry).
- **Operability records (r29 C2 counter, r26–r29 receipts)** — HOLDS (`failed=0 uncovered=0 floor_violations=0` at base and tip; tip adds r30 `records=150`).
- **Committed wave capture** — HOLDS (`records=150 failed=0 uncovered=0` at 9dcd3676).
- **declared-evidence no-harm** — **BROKEN**: 21→22, one new assertion, F1.
- **Axis declarations (axis-check) and SCORECARD axis scores** — HOLDS (`claims=3 flags=0`; 7/8/8 identical at both revs).
- **All three axes untouched by these findings** — calibration 7, coverage 8, operability 8 unchanged; the two defects are record/instrument, not axis-score, moves.
- **C3's used-by wiring (S054, S063, S220, S221 → the new entry)** — observed resolving at real root (0 E11); HOLDS.

## Deliveries
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w2/deliver-no-harm-records.txt` — check table, raw outputs, receipts R1–R3, no-change summary.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w2/SwarmExecutor05.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r30/NoHarmRecords` removed after the deliverable was written. Nothing in the lane, the fleet root, sibling lanes, jj or any index was written, moved or signalled; all generated paths stayed under the scratch dir and the two delivery files above.
