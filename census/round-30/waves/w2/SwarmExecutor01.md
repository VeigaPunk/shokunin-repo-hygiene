## Status
STATUS: PASS — I re-ran C1's instrument myself (v1 and A3, at the landing commit and the lane tip) and attacked its enumeration, its receipts and its determinism. The target reproduces exactly and serially; the instrument is not concurrency-safe and two of its acceptance paths are contestable (both disclosed). C1's reported result stands as recorded; nothing here voids the target.

## Evidence
All runs read-only against the lane; scratch `/fast/scratch/hyaku/souji-r30/RerunC1/`, `python3 -B`, TMPDIR under that scratch; tools extracted with `git show` (v1 `d4928ec` sha256 `af71db1e…`, 232 lines; A3 at `9dcd36` sha256 `88ffa768…`, 246 lines; A3 at `7b16731` = `9b74d734…`, byte-identical to `9dcd36` by `diff`, rc=0). Argv for every run: `--root <lane> --rev <REV> --base 9420341d… --list-rev d4928ec86b… --scratch /fast/scratch/hyaku/souji-r30/RerunC1/s`.

| run | rc | SUMMARY |
|---|---|---|
| v1 @7b1673 (landing) | 0 | `k1=0 k2=0 mismatches=0 rows=18 pointers=10 rev=7b1673…` |
| A3 @7b1673 | 0 | `k1=0 k2=0 mismatches=0 rows=18 pointers=10 rev=7b1673…` |
| v1 @9dcd36 (tip) | 0 | `k1=0 k2=0 mismatches=0 rows=18 pointers=10 rev=9dcd36…` |
| A3 @9dcd36 | 0 | `k1=0 k2=0 mismatches=0 rows=18 pointers=10 rev=9dcd36…` |
| v1 @base 9420341 (control) | 1 | `k1=13 k2=0 mismatches=13 rows=18 pointers=10` |

`KINDS value=0 shape=0 rc=0` in all four after-runs. My v1 and A3 outputs at the landing commit are line-for-line identical to `census/round-30/records/c1-after-v1.txt` and `c1-after-a3.txt` (28 ROW/PTR lines + SUMMARY + KINDS; the receipts carry one extra trailing `rc=0` annotation line). The base control reproduces `c1-before.txt` row for row, including `R18` observed as the usage banner and `R16` rc=2 — the claim is not vacuous. Serial determinism: 6 serial runs, or 2 identical v1 runs at the landing commit (`out-v1-7b1673.txt` vs `-run2.txt`, byte-identical).

Independent checks opened this run: (a) the 13 `R30-CORRECTION` lines at `SCORECARD.md:324-336` each re-run by the counter; I hand-ran `tools/souji-landing-gate.py --selftest` ("SELFTEST pass=65 fail=0"), `tests/fixtures/r23-record-agreement.py` ("selftest=15/15"), `tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` ("cases=9 pass=9 control=FALSE-GREEN-REJECTED") and the R18 fixture (stdout ends "cases=15 pass=15 control=TAMPER-REJECTED", stderr ends in the usage banner) in private clones at base and at `7b16731` — every recorded `observed=` string is real. (b) A rule scan of `SCORECARD.md` at base: all 18 enumerated pairs map to a real command+count cell, and none of the 8 excluded lines (`147,151,159,163,164,165,168,170`) carries a command beside a count. (c) An independent SHONEN reconstruction: exactly 10 path-like tokens at base, each a blob at both revs (`LOG.md:362` → 1784 lines), matching `pointers=10`. No normalized token (`<TMP>`, `<HEX>`, `<DUR>`) appears in any serial `observed=` field, so no observation is masked.

## Findings
1. **Concurrency race flips R14 — the frozen kill rule is trip-able by a peer, not by the claim** (`tests/fixtures/r23-record-agreement.py:67`, `:105`; row R14 → `SCORECARD.md:173`). Two A3 instances at `7b16731` in parallel: A rc=0 `k1=0`, B rc=1 `k1=1`, R14 `MISMATCH kind=rc` observed `case=1 expect=rc=0 mismatches=0 keys=4 json-bound got=rc=0 …`. Three in parallel: run2 rc=0, run1 and run3 rc=1 (`observed=tool_sha256=<HEX>`). Cause: the fixture hard-codes one scratch root — `:67 "SCRATCH_ROOT = \"/var/tmp/souji-r23-ExecFixtureAgreement\""` — and `:105 "shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)"`, documented at `:11` as "a synthetic lane repo under /var/tmp (hard-coded; never /tmp), trap-cleaned on exit,". A concurrent instance deletes the other's tree mid-run. Only R14 moves; no other row moved in either test. Consequence: with many wave seats re-running C1, a serial pair of receipts cannot be reproduced while a sibling runs the same counter, and the prereg's "Kill rule: any other SUMMARY at either revision … is a miss" can fire on environment, not defect.
2. **The target's second measurement point has no committed receipt** (`census/round-30/records/c1-after-v1.txt:1`, `c1-after-a3.txt:1`). Both headers say "measured at … 7b16731…" and no file under `census/round-30/records` names `rev=9dcd367…`; the prereg requires the target "at the C1 landing commit and again at the final lane tip". I supply that point: v1 and A3 at `9dcd36` both print the frozen SUMMARY with rc=0. Non-fatal at this rev (the tip is not final), but the evidence set is currently one revision short.
3. **R16 was repaired, not reported** (`SCORECARD.md:335` vs the frozen text). The correction is `R30-CORRECTION SCORECARD.md:175 R16 cmd=python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py rc=0 …` — the row's own argv fails with rc=2 (`error: the following arguments are required: --tool`), and the prereg says "a row whose command now fails is corrected with its failing rc and reported as an operability limit, not repaired under C1." The land instead completed the argv and recorded the success. This is disclosed at `SCORECARD.md:322` ("R16's cell omits the required `--tool` argument … still prints 9 of 9"), the frozen K1 admits `cmd=`, and A3's prefix rule accepts the extension, so the verdict is `CORRECTED` under both tools either way (k1 unaffected).
4. **The enumeration rule's text admits more pairs than the 18** (`census/round-30/c1-rows.tsv:5`, `SCORECARD.md`). The header says "One row per (command, literal) pair." Reading that literally, four trailing counts on enumerated lines also pair with a command in the same cell: `:153` `external fixture 5/5`, `:174` `stub control 4/8`, `:313` `(v1 tool 8/20)`, `:314` `(base tool 8/15)`; none is in the 8-line exclusion list, and under that reading k1 would not be 0. The shipped reading is adjacency (count immediately beside the command), which is the only sane one and matches the exclusion-list gloss, and `rows=18` is frozen — but the rule text and the tsv disagree, so the next calibration move should rewrite the rule, not the rows. Same class: the frozen scope `lines 147-175 and 313-314` leaves four command+count cells in the historical measurement tables (`:67`, `:69`, `:101`, `:102`) outside the set without naming them.
5. **One correction line is v1-only** (`SCORECARD.md:336`, disclosed `:338`). R18's correction records `observed=Usage: bash tools/souji-wave-evidence-capture.sh …`, which A3 refuses as an observation and which only the v1 stdout+stderr concatenation produces; under A3 the row reaches `MATCH` on the stdout line instead. Both readings meet the target, and `SCORECARD.md:338` says so ("The R18 line satisfies only the frozen v1 reading; under A3 the row matches on its stdout line and the banner is refused as an observation."). Not fatal: if v1 is retired the line becomes inert.
6. **Causal separability holds at the tip.** R05/R06 (the rows C2 must not move) read `CORRECTED` with identical observations at `7b1673` and `9dcd36` under both tools, and no row changes verdict between the two revisions.
7. **Observation, no verdict:** `git -C <lane> status --porcelain` at check time = `M SKILL.md`, `M corpus/QUALITY.md`, `?? corpus/lessons/round-30.md` — the L1's unintegrated wave work; C1 is commit-scoped so its measurement is unaffected.

## Attack log
| attacked | method | verdict |
|---|---|---|
| C1 v1 at the landing commit | extracted the `d4928ec` blob, ran the frozen argv | **HOLDS** — exact SUMMARY, rc=0, receipt-identical |
| C1 A3 at the landing commit | extracted the `9dcd36` blob | **HOLDS** — exact SUMMARY, rc=0, receipt-identical |
| C1 at the lane tip (v1 and A3) | ran both tools at `9dcd36` | **HOLDS** — target met; no committed receipt exists (Finding 2) |
| base control non-vacuity | v1 at `9420341` | **HOLDS** — `mismatches=13`, row-identical to `c1-before.txt` |
| enumeration fidelity | rule scan of `SCORECARD.md` at base against the 18 pairs + 8 exclusions | **HOLDS** for the 18; **DEFECT-NOT-FATAL** for the rule text (Finding 4) |
| SHONEN pointer set | independent token extraction + `cat-file` per token at both revs | **HOLDS** — 10 tokens, all resolve |
| honesty of recorded observations | hand-ran R05, R14, R16 (both argv forms), R18 in private clones at base and `7b16731` | **HOLDS** — every `observed=` string real, no normalization masking |
| v1 vs A3 verdicts | 18-row matrix at both revs | **DEFECT-NOT-FATAL** — R18 only, disclosed (Finding 5) |
| serial determinism | repeat run at `7b16731` | **HOLDS** — byte-identical |
| concurrent determinism | 2 then 3 simultaneous A3 instances at `7b16731` | **BROKEN** for R14 — `k1=1` in 3 of 5 concurrent instances (Finding 1) |
| R16 acceptance path | read the land's correction against the frozen text | **DEFECT-NOT-FATAL** — repaired, disclosed, target unmoved (Finding 3) |

## Deliveries
- `.ufo/waves/round-30/w2/SwarmExecutor01.md` (this report)
- `.ufo/waves/round-30/w2/deliver-c1-rerun.txt`
- receipts: `.ufo/waves/round-30/w2/SwarmExecutor01-c1-{v1-7b1673,a3-7b1673,v1-tip,a3-tip,v1-base,v1-7b1673-run2,conc-A,conc-B,tri1,tri2,tri3}.txt`
- scratch `/fast/scratch/hyaku/souji-r30/RerunC1/` removed after the receipts were copied; no tool installed or updated this run.
