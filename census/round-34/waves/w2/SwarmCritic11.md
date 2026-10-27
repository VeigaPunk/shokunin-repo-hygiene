# SwarmCritic11 — souji r34 w2 seat report (AttackE08b falsification)

## Status

Assignment complete. Adversarial review of W1's E08b finding executed read-only against the frozen
list (list-rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`), base `9c76c7222a8abff027af42e37f0d160d52526bba`,
and W1 receipts. Outcome: W1's formal MISMATCH verdict for E08b stands, but W1's "value drift"
classification is falsified; the defect is a frozen-argv transcription defect (dropped `-r`), with
an honest argv-correction restatement route open under the frozen rules.

## Evidence

- Frozen row: `souji-shokunin/census/round-34/c1-items.tsv:49` (also at list-rev, line 49): argv
  `bash -c "grep -lE '^ground: F4' corpus/knowledge/ | wc -l"`, predicate `^4$`, pin
  `6cb22dc20c9fdb3c7a49eaa1accabca339054c17`, cell `SCORECARD.md:32`.
- Row's own recorded command, base `9c76c72:SCORECARD.md:32`: `grep -rlE '^ground: F4' corpus/knowledge/ | wc -l`,
  measured "grounded F4 `4`" at the same pin.
- r33 enumeration `.ufo/waves/round-33/w1/deliver-c1-enumeration-misses.md:21` (E08 row): argv
  recorded with `-rlE`; "at 6cb22dc: 135 rows, F4 4".
- W1 do-nothing record `.ufo/waves/round-34/w1/deliver-c1-do-nothing.txt:38`: E08b MISMATCH,
  rc=0, last=0.
- Bounded probes run (scratch `/fast/scratch/hyaku/souji-r34/E08b/probe`, git-archive extraction of
  the pin tree, <1 MB): frozen argv → `0` ("Is a directory" on stderr); row's recursive argv → `4`.
  Same frozen argv re-run in the lane working tree → `0`, confirming revision-invariance of the
  defective output.
- Q76 same-cell check reproduced: 0 correction rows reference `SCORECARD.md:32` in base
  SCORECARD.md and SKILL.md (W1's Q76 claim confirmed).

## Findings

1. E08b's mismatch mechanism is a frozen-list transcription defect (`grep -lE` for recorded
   `grep -rlE`), not value drift; the pinned measurement still yields `4` and matches predicate
   `^4$` with the row's own command.
2. The argv-correction restatement route (frozen rules: "an argv-correction restatement must run
   the row's own script") is open and restores AGREE at the pin; W1's do-nothing framing should
   not count E08b among content-drifting cells.
3. Q76: no same-cell correction; not a Q76 false positive.
4. Adjacent integrity defects flagged in the item report: frozen header comment (`c1-items.tsv:9`)
   names E08b as excluded while row 49 freezes it; E08a/E08b share cell `SCORECARD.md:32`.

## Attack log

- Executed probes (exact commands/output): see `.ufo/waves/round-34/w2/AttackE08b.md` ## Evidence.
- No lane file modified; no commits; no fixture execution; scratch well under the 50 MB ceiling.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE08b.md`
- `.ufo/waves/round-34/w2/SwarmCritic11.md` (this file)
