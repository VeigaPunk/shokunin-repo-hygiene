# CritQ57Criterion — Q57 criterion review (round 25, wave 2)

STATUS: PARTIAL — motivating lesson exists and is genuine; criterion text and its
check contain correctness/coverage defects (overstatement through a pointer that is
never resolved to an existing file, a documented check command that cannot enforce
"both tables", and no absence sweep behind "quoted anywhere"). Calibration claim is
independent of Q57 (verified in SCORECARD bytes).

## Evidence (revision a6d2d15..6deb535; working tree at 6deb535 + W1 integration draft)

- Criterion bytes: `.ufo/waves/round-25/w1/quality-q57.md:16` (raw) — the Q57 table row
  drafted for `corpus/QUALITY.md`. QUALITY.md at working tree does NOT yet contain Q57
  (grep Q57 → 0 matches; file ends at Q56, line 135).
- Check script: `tests/fixtures/r25-q57-check.sh` (installed bytes, sha256 in draft §5
  `9b3d8f58dac13b0d506de859d1052a493ccdd4d00182e46eaad7a5a434237e3a`).
- Lesson: `corpus/lessons/round-24.md:170` = R24-M22 (## Mistakes table). D6 routed
  defect: `corpus/lessons/round-24-verifier-spotcheck.md:101-102`.
- Authoritative/detail tables with appended pointer comments (working tree):
  `census/round-24/records/slice-verdicts.tsv:11` and
  `.ufo/waves/round-24/assimilation/slice-verdicts.tsv:11`.

## Findings

1. **Motivating lesson exists and shows R24-M22 — PASS.** R24-M22 at round-24.md:170
   is class "calibration", evidence: "`census/round-24/records/slice-verdicts.tsv` vs
   `.ufo/waves/round-24/assimilation/slice-verdicts.tsv`: 7 of 8 rows differ, with no
   mapping; S118 `unverifiable` vs its own evidence cell and its scout's `present`; S126
   and S138 `present`→`accepted` unexplained", failure witness "**SHOWN by W2Slice**
   (class-swap stays rc 0)". That is exactly the defect Q57 addresses (one authority,
   mapping both files point to, membership-only gate green). D6 (spot-check :101) names
   the same defect. Grounding is real, not circular.

2. **Overstatement: a pointer is treated as proving the disagreement is closed (dangling
   target undetected).** The criterion's disagreement clause is "ships a mapping that
   both files point to; a mapping named by only one artifact does not close the
   disagreement", and the check cell implements it as `grep -F "corpus/lessons/round-25.md"`
   over the two TSVs. Nothing stats the mapping target or verifies the section
   `§ Quarantine-slice vocabulary` exists. Currently `corpus/lessons/round-25.md` does
   NOT exist in the lane tree (`ls` → No such file), while the substantive mapping was
   appended instead to `corpus/lessons/round-24.md:377-388` ("Round 25 append-only
   correction — D6 / R24-M22"). The TSV pointer comments, `corpus/README.md:555`,
   `SCORECARD.md:244` and the Q57 check all name the phantom round-25.md. Running the
   checker on the working tree yields POINTS for both TSVs (the literal is present) even
   though the named mapping file is absent — i.e., the pointer half of the check passes
   while the artifact it points to is missing. This is the precise overstatement flagged:
   a mention of the mapping substitutes for its existence/content. The draft's known
   limits disclose "check does not verify that the mapping text itself is consistent with
   the detail table" but not the dangling-target risk.

3. **Documented check command cannot enforce "must match both".** The criterion cell's
   command `grep -F "corpus/lessons/round-25.md" census/round-24/records/slice-verdicts.tsv .ufo/waves/round-24/assimilation/slice-verdicts.tsv`
   is one grep over two files; it exits 0 if *any* file matches, so it passes when only
   one table names the mapping — directly contradicting the criterion's own sentence and
   the script's correct per-file loop (`for f in "$table" "$detail"` → POINTS /
   NO-POINTER). The admitted text of the check is weaker than the rule it claims to test.

4. **No absence sweep; "quoted anywhere" overstates the enumerated 4-site list.** The
   runnable check tests exactly the SITE arguments: round-24.md:240, round-24.md:232:S118,
   LOG.md:1692, SCORECARD.md:181. The criterion text ("A slice tally quoted anywhere") and
   applies-to ("lessons, LOG, SCORECARD, README and round evidence") are universal; the
   criterion row does not state the sweep is site-enumerated (contrast Q52/Q53's "of N
   listed mutants", never exhaustive). Unenumerated real tally-quote sites exist:
   `corpus/README.md:440` ("5 accepted with corrected quotes, 2 present, 0 refused, 1
   unverifiable" — a slice-class tally inside an applies-to document), `LOG.md:1510`,
   `LOG.md:1540`. None is swept; README:440 could drift with no check firing. The
   non-automaticity is disclosed only in the draft's §5 known limits, not in the admitted
   criterion row.

5. **D6 not yet complete at the integrated tree: LOG.md:1692 carries no superseded-by
   note.** Working tree: round-24.md:387-388 and SCORECARD.md:250 got appended
   "superseded by … recount 8 accepted / recount S118 accepted" notes, but LOG.md:1692
   ("Quarantine slice 8 rows: 7 accepted, 1 unverifiable (S118)") has none (LOG.md is
   unmodified in `git status`). So the Q57 check on the current tree is still red at
   LOG.md:1692 (STALE), and "S118 re-classed accepted everywhere" is not met. The
   criterion's own failure witness therefore is not yet satisfied by the integrated bytes.

6. **Calibration claim is independent — PASS.** Q57 is a routed fix (preregistration
   "Routed fixes (not claims; land with evidence)"); the SCORECARD Round 25 measurements
   table lists only C1 (calibration 7, verdict "unprovable"), C2 (operability 8), C3
   (coverage 8), and no Q57 row or axis score. C1 rests solely on the coverage-agreement
   kill-rule tool/fixture. Nothing in Q57 feeds calibration scoring; score delta 0.

## Counterexample (strongest)

Build a synthetic tree where both TSVs contain the string `corpus/lessons/round-25.md`
(a comment line), but no such file exists. `r25-q57-check.sh` prints POINTS for both
tables and, with the four superseded sites noted, q57=PASS — the disagreement is
"closed" by a pointer to nothing. Likewise, mutate `corpus/README.md:440` to a wrong
tally ("8 accepted, 0 present"): no check fires because README is not in the SITE list.
Both show the criterion overstates what its check proves.

## Smallest safe corrections

- Require the mapping target to exist and to contain the named section: e.g. prepend
  `test -s "$root/$mapping"` and `grep -qF "Quarantine-slice vocabulary" "$root/$mapping"`
  to the POINTS loop (fail on NO-POINTER / MISSING-MAPPING-FILE).
- Replace the one-grep command in the check cell with a per-file construction that
  actually requires both matches (two greps, or `grep -l … | wc -l` = 2), and make the
  script itself the cited command.
- Qualify the criterion text with the enumerated sweep: "for each site in the recorded
  SITE list, and for any newly added tally quote site, …", or state "the sweep is
  site-enumerated; a quote at an unlisted site is not checked" (Q52/Q53 style).
- Append the LOG.md:1692 superseded-by note (and any other tally-quote site) before the
  criterion's failure witness can be considered closed; align all pointers on the file
  that actually carries the mapping (create round-25.md or re-point comments/README/
  SCORECARD to round-24.md).

## Attack log

- Read: QUALITY.md (full), preregistration + amendments, round-24.md lesson, spot-check
  D6, Q57 draft, r25-q57-check.sh, both TSVs, SCORECARD/README/SOURCES diffs, LOG 1692.
- Ran: grep Q57 across repo (0 in QUALITY.md); `ls` for round-25.md (absent); tally-quote
  scan over corpus/SCORECARD/LOG/README; git diff for integration bytes.
- No writes other than this report. No tools installed. Scratch not created.
