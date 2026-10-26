## Status
STATUS: PASS — the attack ran: the C1 corrections block (`/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:320-338` at `7b16731fcd8ab9b95220b50603314aa8dc92b2ec`, byte-identical at `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`) is substantively honest and every correction line still holds at the tip, but its frozen SUMMARY is reproducible only when no second evaluator runs the R14 fixture, and two prose quantifiers overstate their own cited sources.

## Evidence
- Block under attack: `/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:320-338` at `7b16731`; `git diff 7b16731 9dcd367 -- SCORECARD.md` is empty.
- "The capability cells above stay as written; each line below records what the named command prints at the measured revision." (`SCORECARD.md:322`).
- "7 are notation (the stated numbers equal the printed numbers, in another shape: R03 R06 R07 R08 R09 R10 R11)" (`SCORECARD.md:322`).
- "under A3 the row matches on its stdout line and the banner is refused as an observation" (`SCORECARD.md:338`).
- Stale cells at base and tip, unchanged: `:158` "`python3 tools/souji-landing-gate.py --selftest` 18/18; `python3 tests/fixtures/r16-landing-gate.py` 15/15"; `:173` "`tests/fixtures/r23-record-agreement.py` 9/9"; `:174` "`tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py` 8/8"; `:175` "`python3 -B tests/fixtures/r24-coverage-agreement.py` 9/9"; `:155` "external fixture 5/5".
- Counters (receipts R1-R4): v1 base `k1=13`; A3 base `k1=12` (R18 MATCH); v1 and A3 at `7b16731` `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10`; both at `9dcd367` the same.
- Race (receipts R5-R6): v1 full run at `7b16731` while a second R14 fixture ran: `ROW R14 ... rc=1 observed=selftest=14/15 MISMATCH kind=rc`, `SUMMARY k1=1`. Two concurrent fixture runs both `rc=1` (git add: not a git repository / unable to create temporary file).
- R14 fixture: `SCRATCH_ROOT = "/var/tmp/souji-r23-ExecFixtureAgreement"` (`/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r23-record-agreement.py:67`), `shutil.rmtree(SCRATCH_ROOT, ignore_errors=True)` (`:105`), `os.makedirs(SCRATCH_ROOT, exist_ok=True)` (`:584`); the counter docstring says "TMPDIR is a fresh per-row directory under" (`tools/souji-capability-agreement.py` v1 blob `d4928ec`, `:11`) and sets it (`:149-150`).
- Provenance: 10 of 13 rows in `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/waves/w1/deliver-c1-literal-history.tsv` say "never the printed literal (shorthand)"; `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/waves/w1/SwarmRevenger34.md` STATUS says "all 13 stated counts were accurate when written (0 fabricated)".
- Cited R18 record header: "round-30 L1 (routed r29 closure defect D3): observed full output of" (`/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/d3-green-r28-wave-evidence-capture.txt:1`).
- R08 documentation exists at base and tip: "the two J6 identity cases SKIP without `--baseline-dir`" (`/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/jj-colocation-receipts.md:3`).
- Unchanged base→tip: `r28-wave-evidence-capture.sh`, `r23-record-agreement.py`, `r13-repo-structure.sh`, `census/round-24/records/c2-fixture-after.tsv`, `jj-colocation-receipts.md`; the live `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv` is byte-identical to the committed capture (`sha256 9cb2306…`).

## Findings
1. **The frozen target is not stable under the round's own parallel evaluation** — BROKEN (instrument/reproducibility; the block's sentences are true of the serial measurement). `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r23-record-agreement.py:67` hard-codes `/var/tmp/souji-r23-ExecFixtureAgreement`, ignores the counter's fresh `TMPDIR` (`tools/souji-capability-agreement.py` v1 `:149-150`), and deletes that shared tree at start (`:105`), so any second evaluator deletes the first's repos. Observed twice: a full v1 run at `7b16731` scored `k1=1` (R14 `selftest=14/15`, rc=1) while the same command serial scored `k1=0`; two concurrent fixture instances both exited rc=1; a serial history probe also died once and passed on retry. Axes hit: calibration (claim reproducibility) and operability. Smallest safe correction: append one sentence to the block that the values were measured serially and that R14 depends on a fixed `/var/tmp` path, and route the fixture fix (unique dir or honour `TMPDIR`) to r31 — do not change the counter or any literal under C1.
2. **The provenance parenthetical overstates its cited TSV** — `SCORECARD.md:322`: "all 13 literals were accurate when written". The cited TSV labels 10 of the 13 "never the printed literal (shorthand)", and its author's STATUS says "stated counts", not literals. The numbers were accurate; the strings were not printed. Correction: say "all 13 stated counts were accurate when written" (10 as condensed forms).
3. **"13 base mismatches" belongs to v1, but the instrument named in the same sentence is A3** — `SCORECARD.md:322`. A3 at base scores `k1=12` (R18 matches on stdout; `ROW R18 ... MATCH`), so a reader running the named command at base gets 12. Correction: "the 13 v1 base mismatches (A3 scores 12 at base: R18 matches on stdout)".
4. **The R18 green-tally citation is a combined-stream record** — `SCORECARD.md:322` cites `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/d3-green-r28-wave-evidence-capture.txt`, whose header says "observed full output" and which interleaves the usage banner before case-14/15. The claim "stdout ends cases=15 pass=15" is true (fixture `printf` at `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r28-wave-evidence-capture.sh:537`; A3 observes exactly that line), but the cited record does not by itself separate the streams. Correction: cite the split-stream run (Revenger34 Evidence) or add "last line of the run".

## Attack log
| attacked item | verdict |
|---|---|
| Arithmetic and split: 7 notation + 4 grown + R16 + R18 = 13 | HOLDS — v1 base `k1=13`; A3 base diagnostic `value=4 shape=7 rc=1`, R18 natively MATCH; exactly 13 correction lines, all for mismatching rows, none for R01/R02/R12/R13/R17 |
| Notation list R03 R06 R07 R08 R09 R10 R11 | HOLDS — each stated number occurs in its printed line; 5/5 and 15/15 are "N of N" = `total=N failed=0`, 29/0 etc. are pass/fail; no cell was a fabricated number |
| "4 are counts that grew" endpoints | HOLDS — re-ran at the named commits: R04 5/5→7/7 at `728b2ce` (r25); R05 18→65 at `005f3d3` (r19), with 28 at `ddb7347` and 61 at `4800fd7`; R14 9→11→12→15 at `728b2ce` (r25); R15 8→12 at `679e2d0` (r25). "by r19"/"at r25" are endpoints; growth began earlier (R05 r17, R14 r23 w2) |
| R16 omits required `--tool` | HOLDS — base row exits 2 with "the following arguments are required: --tool"; with `--tool` it prints `cases=9 pass=9`; the cited record `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-24/records/c2-fixture-after.tsv` is unchanged base→tip |
| R18 is a v1 stdout+stderr artifact | HOLDS — v1 concatenates the streams (`tools/souji-capability-agreement.py` v1 `:155`); case 14 of the fixture deliberately invokes a bad round argument, whose usage banner on stderr becomes v1's last digit-bearing line; counterfactual at base: v1 MISMATCH, A3 MATCH |
| R08 `skipped=2` documented | HOLDS — the knowledge recheck line is present at base and tip and names the two J6 skips without `--baseline-dir` |
| "The capability cells above stay as written" | HOLDS — `SCORECARD.md` is unchanged after `7b16731`; lines 155/158/173/174/175 still state 5/5, 18/18, 9/9, 8/8, 9/9 |
| Calibration or mere annotation (cells still 18/18 etc.) | HOLDS as **instrument-checked annotation, not a table repair** — a wrong `observed=` fails (junk control `C1-junk1` `k1=2`), so each line is measured, but no cell became true; the block says so, claims no score, and the lane's own axis cell calls record accuracy "not a scored axis move". "C1 met" therefore means every divergence is documented, not that capability counts are correct |
| Does the R18 line, accepted only by v1, misrepresent? | HOLDS in context — the line alone records stderr, but the adjacent sentence scopes it to v1; under A3 it is not consulted (row MATCH) and a banner observation is refused (`BANNER` at A3 `:55`, stdout-first at `:165`) |
| Anything false at `9dcd367`? | HOLDS — no false sentence found: counters `k1=0` under both instruments, cells as stated, cited fixtures/records/knowledge unchanged, provenance capture identical and capture-mapped; only Finding 1's concurrency caveat applies |
| "each line below records what the named command prints" | DEFECT-NOT-FATAL — true serially, falsified by a concurrent evaluator (R14) |

### Per-sentence verdicts (block `SCORECARD.md:320-338`)
- S1 heading `R30 append-only corrections (round 30, C1: capability-table literals vs committed output)` — HOLDS.
- S2 "Measured at base 9420341… by … (v1 bytes at d4928ec; stricter amendment A3 in the current file)." — HOLDS; the named file is A3, which scores 12 at base (Finding 3).
- S3 "The capability cells above stay as written" — HOLDS.
- S4 "each line below records what the named command prints at the measured revision." — DEFECT-NOT-FATAL: true serially; a concurrent evaluator flips R14 (Finding 1); for R16 the named command is its `cmd=` extension.
- S5 "Of the 13 base mismatches, 7 are notation (… R03 R06 R07 R08 R09 R10 R11)" — HOLDS (v1 count; A3 caveat Finding 3).
- S6 "4 are counts that grew after the row was written (…)" — HOLDS (all four endpoints re-run at the named commits).
- S7 "R16's cell omits the required `--tool` argument (the r24 invocation … still prints 9 of 9)" — HOLDS.
- S8 "R18 is a v1 counter artifact: its stdout ends … a usage banner the fixture provokes on purpose." — HOLDS (citation nuance Finding 4).
- S9 "The R18 line satisfies only the frozen v1 reading; under A3 … refused as an observation." — HOLDS.
- S10 "R08's `skipped=2` is the documented invocation without `--baseline-dir` …" — HOLDS.
- S11 "Literal provenance per row: … (SwarmRevenger34: all 13 literals were accurate when written)." — DEFECT-NOT-FATAL (Finding 2; the `.ufo` pointer is gitignored but capture-mapped at tip, identical bytes).
- S12 the 13 `R30-CORRECTION` lines — HOLDS: 12 are accepted with equal `rc=`/`observed=` at `7b16731` and `9dcd367` under both instruments; R18's line is v1-only, as S9 states, and A3 matches the row natively.

No installs or upgrades; pacman untouched. Read-only git on the lane; clone and all counters under `/fast/scratch/hyaku/souji-r30/SwarmCritic16` (removed after the receipts copy).

## Deliveries
- Report: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w2/SwarmCritic16.md`
- Receipts: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w2/SwarmCritic16-receipts.txt`
