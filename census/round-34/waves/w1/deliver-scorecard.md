# SCORECARD.md additions — round 34 (draft for the L1, SoujiR34a2)

Append-only additions for the round-34 landing. The `after` cells and the restatement rows are the
L1's to complete; the frozen targets and the committed do-nothing readings are pre-filled below.

### Round 34 measurements (2026-10-27; base 9c76c7222a8abff027af42e37f0d160d52526bba; preregistration 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 with amendments A1-A6; freeze 2b591924f607940febbb99f922cc9bb090508eb6, counter repair re-pin 2b0171e2)

| claim | axis | before | after | counting command | measured commit |
|---|---|---|---|---|---|
| C1 registry-and-measurement-row agreement (60 items, `census/round-34/c1-items.tsv`) | calibration 7 | `SUMMARY items=60 agree=35 mismatches=25 restated=0`, rc 1 (do-nothing, `census/round-34/records/controls-c1-do-nothing.txt`) | target `SUMMARY items=60 agree=60 mismatches=0`, rc 0 at the C1 landing commit and at the tip — L1 to fill the observed reading | `python3 -B census/round-34/c1-counter.py --root <lane> --rev <full40> --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch <dir>`; junk control `python3 -B tests/fixtures/r34-c1-junk.py --counter census/round-34/c1-counter.py --scratch <dir>` -> `cases=3 pass=3 control=STUB-REJECTED` (`records/junk-c1.txt`) | before `9c76c7222a8abff027af42e37f0d160d52526bba` (`records/controls-c1-do-nothing.txt`, run at list-rev `2b591924f607940febbb99f922cc9bb090508eb6`; the `c1-items.tsv`, `SCORECARD.md` and `SKILL.md` blobs are byte-identical at `2b0171e2`, so the reading transfers); after — landing commit and tip, L1 |
| C2 sandbox-nt measurement hardening (13 legs: W1-W4, N3, N4, J1, G1-G6) | operability 8 | `COULD-NOT-EVALUATE legs absent at --list-rev`, rc 2 (do-nothing, `census/round-34/records/controls-c2-do-nothing.txt`; `c2-legs.tsv` absent at base) | target `SUMMARY legs=13 pass=13 fail=0 harm=0`, rc 0 at the C2 landing commit and at the tip — L1 to fill the observed reading | `python3 -B census/round-34/c2-counter.py --root <lane> --rev <full40> --base 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch <dir>` | before base `9c76c7222a8abff027af42e37f0d160d52526bba` (`records/controls-c2-do-nothing.txt`); after — landing commit and tip, L1 |

### Round 34 registry restatements

| id | where | restated | exit | run | statement | cause | reason |
|---|---|---|---|---|---|---|---|

### Planned (appended at round 34)

- **r35 (planned r34):** calibration: the frozen `where` cells sit one row low for 21 of the 22 SKILL.md registry items (only G24 is exact), so an argv-correction row on those cells is validated against the neighbouring row's text (w1 `SwarmExecutor01.md` finding 6); round 34 also lands with no committed pre-landing control that exercises an appended restatement row — the first reading of a landed row is the landing measurement itself (w1 `SwarmExecutor09.md` state note). operability: unless the landing closes them, the C2 feasibility failures stay open — W2 `SUMMARY total=20 failed=1` under bwrap, W3 base/rev last-line mismatch (rc 1/1), N3 `cases=12` with `summary=False`, J1 a 900 s timeout (`census/round-34/records/junk-c2-final.txt` is a `TimeoutExpired`; `junk-c2.txt` and `junk-c2-repaired.txt` are empty) — together with the five semantic attacks in `.ufo/waves/round-34/w1/deliver-c2-leg-attacks.txt` (witness scope, `strace` matcher blind spots, N4 equality instead of load stability, N3 run-time non-modification, invocation-aware junk). Carried from `census/round-34/records/closure-sweep.txt`: the C2 oracle envelope, the letters-only prose blind spot, gate mutants M4/M10, the uncarried r15/r19/r23/r24/r25 seat failures, the landing gate's `/var/tmp` snapshots, N-item adjudication (N25 re-adjudication, N28-N34 binding), the S223 placeholder-id parenthetical, r19-rev-pin's literal `/var/tmp`, and r32 items 1/3/4/5 plus T18; the 37 r33 wave-2 items re-aimed at the r34 tip stay open unless round-34 w2 runs them. Certification OFF, K5 HELD, NAMESPACE hold unchanged.

---

## L1 fill-ins and notes (not for SCORECARD.md)

1. **After cells.** Both counters exit 1 on any mismatch/fail and 0 only on a clean summary
   (`census/round-34/c1-counter.py` `return 0 if mism == 0 else 1`; `census/round-34/c2-counter.py`
   `return 0 if failed == 0 else 1`), so each `after` reading needs the line *and* rc 0 at both the landing
   commit and the tip. The frozen targets are `SUMMARY items=60 agree=60 mismatches=0` and
   `SUMMARY legs=13 pass=13 fail=0 harm=0`; the C1 summary may carry a non-zero `restated=` count at either point.
2. **Heading and rows must land together.** `load_restatements` only reads rows inside a line that starts with
   `### Round 34 registry restatements`, and any later `#`-heading closes the section. Append the heading and the
   E18 row (verbatim in `deliver-c1-E18.md`) in the same commit, and keep that section last.
3. **Row shape.** Seven cells after the id — `where | restated | exit | run | statement | cause | reason`; only lines
   whose first cell matches `E\d{2}[a-z]?` or `G\d{2}[a-z]?` are parsed, so the column header row above is ignored.
4. **Do-nothing provenance.** The committed C1 do-nothing record was taken at list-rev `2b591924`, not the frozen
   `2b0171e2`. The transfer is byte-level: `c1-items.tsv` blob `ef76faef005df7dffb6478bd88833d82c863c198`,
   `SCORECARD.md` blob `a5381e99b70cf14b015107061ded0f5af8d6bf3b` and `SKILL.md` blob
   `77f36874b1714da1c02b8ab60d0b51ad71b54265` are identical at both revisions, and the counter's only other inputs
   are `--rev` (unchanged base) and the restatement section (absent in both). A byte-exact re-run at the frozen
   list-rev is optional, not required by the contract.
5. **Mid-round readings, not target readings.** `census/round-34/records/feasibility-final.txt` reads
   `SUMMARY legs=13 pass=9 fail=4 harm=0` at `60def78d16017be528ba6b439e350918587cb80b` and is a feasibility record,
   not a landing or tip reading; do not put it in the `after` cell.
6. **Closing sentence.** The owned-score sentence (calibration 7, coverage 8, operability 8) is the L1's, and depends
   on whether the two targets are met at both points.
