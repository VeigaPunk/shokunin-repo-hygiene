# S71Reviewer: souji round 71 correctness review (base 8b9345b1 → 52e8c3fa; candidate a1db6c85)

## Verdicts
1. Writer `_filter_drivers` / pins / placement
   - check-attr -z parse (triples; spaces, newline, dotted, uppercase names; empty index): SOUND.
   - `git config --get filter.<name>.<key>` for dotted/uppercase names: SOUND (subsection case matches git).
   - Pinned env (GIT_CONFIG_GLOBAL=/dev/null): SOUND. A driver only in global/system config is invisible to the status read and to the filter check alike, so it cannot make the writer's witness disagree with itself. Note: `git status` run by a human under global config can differ (LOW, informational).
   - Pre-run check before the dirty read; post-run check before any receipt byte: SOUND.
   - `-c core.fileMode=true` on every writer git call: SOUND for carried rows. Base→candidate verdicts differ only on AS1 AS2 FC1 FC2 FC3 FM1 FM2 (the 7 forgeries).
   - Literal filter values `set`, `unset`, `unspecified` exempted from the driver lookup: **DEFECT, HIGH** (see F1).
2. Counter: SOUND. Carried rows: the r70→r71 diff removes only the docstring line, COUNTER_REL, and the ROW-list tail (extended); CASE_SPECS and _row_env are additive. make-controls.py and mk-counter.py reproduce committed bytes. Selftest section (8) kills X6-X10 (receipt lines identical). Gap: no selftest or matrix row exercises the literal-name route (F1).
3. Harness: killed = rc≠0 AND fail≥1 (c2-harness.py:fate_of); crashed counts as survived; CF1 shows the positive gate. SOUND. Label regex and work checks: SOUND. LOW issues below.
4. Preregistration vs receipts: every number reproduced byte-for-byte (see Evidence). F1–F3 and CF1 numbers are read from their receipts and not rerun; their variant bytes are reproduced by make-controls.py.
5. SKILL.md r71 rows: commands use the frozen flags; verdict maps match code (fatal() → EXIT=2, c2-harness.py:1331-1334 and rc logic). SOUND.

## Findings
- **F1 HIGH, writer:** `tools/souji-receipt-write.py:153` `values - {b"unspecified", b"unset", b"set"}` drops those attribute values before the driver lookup. git-check-attr prints the same text for bare `filter`/`-filter`/`filter=<v>`, so the exemption is not a sound discriminator. Filter `set`, `unset` and `unspecified` with a configured `filter.<name>.clean` are applied by git (`status=[]` over forged bytes), and the candidate writes a receipt (rc=0). The base writer also writes it; the candidate's refusal does not cover it. Controls: `filter=t` refused RECEIPT-FILTER-DRIVER-SET; no-driver `filter=set` gives ` M` (no clean applied). Covered by no matrix row and no selftest case; prereg named limits and the knowledge file do not mention it. Fix: remove the exemption (look up every value; the lookup of `filter.unspecified.clean` is harmless).
- **F2 LOW, harness:** c2-harness.py:119 forbids /tmp, /var/tmp and the root but not $TMPDIR (the counters and the writer do). `subprocess.run(timeout=1800)` (line 79) is not caught: a hung mutant raises a traceback with no SUMMARY (a miss under the kill rule, not a false kill).
- **F3 LOW, harness:** a pre-existing symlink at `work/<label>` makes rmtree fail silently and os.makedirs raise (traceback, no escape).
- **F4 LOW, prereg:** named limits omit the literal-spelling route (F1) and mention global drivers only implicitly.

## Commands run (cwd = lane root)
- `python3 -B census/round-71/c1-counter.py --root <lane> --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev a1db6c8514771c0a0321c29741831606d09cc2a5 --tool tools/souji-receipt-write.py --work /fast/scratch/hyaku/souji-r71/S71Reviewer/c1`
  → `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` / `EXIT=0`
- `python3 -B census/round-71/c1-counter.py --root <lane> --matrix ... --base-rev 8b9345… --new-tool <basewriter.py> --work .../c1dn` → `SUMMARY … new_forgeries=7 … class_mismatches=7 … regress=PASS` / `EXIT=1`
- `python3 -B census/round-71/c1-counter.py --selftest --root <lane> --matrix … --base-rev 8b9345… --work .../st` → `SELFTEST cases=39 pass=39 fail=0` / `EXIT=0`
- `python3 -B census/round-71/c2-harness.py --label c2-after-r71 --counter census/round-71/c1-counter.py --matrix … --root <lane> --base-rev 8b9345… --mutants census/round-71/c2-mutants.json --work .../c2a` → `SUMMARY label=c2-after-r71 positive_selftest=PASS x_mutants=5 x_killed=5 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0` / `EXIT=0`
- `python3 -B census/round-71/c2-harness.py --label c2-before-r70 --counter census/round-70/c1-counter.py --matrix census/round-70/c1-matrix.tsv --root <lane> --base-rev e063a2fc… --mutants … --work .../c2b` → `SUMMARY … x_killed=0 x_survived=5 cm_killed=4 cm_survived=0 score=5` / `EXIT=1`
- `python3 -B tools/souji-receipt-write.py --selftest --work .../wst` → `SELFTEST cases=40 pass=40 fail=0` / `EXIT=0`
- F1 repro: `sh .ufo/waves/round-71/w1/S71Reviewer/evidence/repro-filter-set-forgery.sh <writer> <scratch>` → `status=[]`, `RECORD … rc=0`
- Writer: `git show a1db6c85:tools/souji-receipt-write.py` to scratch; all fixture repos asserted with `rev-parse --show-toplevel`.

## Evidence
- Matrix counts: r71 accept 19 / refuse 51; r70 accept 15 / refuse 44 (carried rows unchanged).
- Re-run outputs match `census/round-71/records/c1-after.txt`, `controls/c1-do-nothing.txt`, `records/c2-after.txt`, `controls/c2-before-r70.txt`, `records/writer-selftest.txt` and `records/counter-selftest.txt` (the only differences are my wrapper's duplicated `EXIT=` line).
- Mutant SHAs: CM1–CM4 in c2-before-r70 equal the r70 receipt (6d7fbf0c…, 4fc11293…, d3a6a825…, c18efbc6…).
- X6–X10: `c2-mutants.json` edits reproduce the S70MutCounter mutant files byte for byte.
- make-controls.py reproduces F1, F2, F3, CF1 byte-for-byte; mk-counter.py reproduces c1-counter.py byte-for-byte.
- F2 forgeries: FC1 FC2 FC3 FM1 FM2; F3: AS1 AS2 FC1 FC2 FC3; F1 over-refusal: ASh FCh2 FMh.
- S306–S308, S310 quote offsets in census/round-71/srcs/ match (17513, 13322, 82016, 40119, 53875).

## Tools
No installs. Used git 2.56.0, python3 (host).

## Files written (seat)
- .ufo/waves/round-71/w1/S71Reviewer.md (this report)
- .ufo/waves/round-71/w1/S71Reviewer/evidence/{c1-candidate-rerun.txt, c1-do-nothing-rerun.txt, c2-after-rerun.txt, c2-before-r70-rerun.txt, writer-selftest-rerun.txt, counter-selftest-rerun.txt, writer-base-to-candidate.diff, counter-r70-to-r71.diff, repro-filter-set-forgery.sh}
- Scratch /fast/scratch/hyaku/souji-r71/S71Reviewer removed.
