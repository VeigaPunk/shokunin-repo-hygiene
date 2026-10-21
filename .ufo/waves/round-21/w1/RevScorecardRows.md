# RevScorecardRows — SCORECARD axis + capability rows vs cited r20 evidence, and required r21 changes

Seat: SoujiR21.RevScorecardRows-3 (reviewer, leaf, read-only). 2026-10-21.
Scope: SCORECARD.md axis rows (coverage/calibration/operability) and the capabilities rows
'process-residue observations' and 'seat transcript audit', each against the r20 evidence it
cites (named files only), plus the changes the frozen r21 preregistration requires in those rows.
Method: named-file reads only; nothing executed; no fixture, census, auditor or runner was run.
No tools installed.

NOTE: SCORECARD.md was rewritten by L1 integration **during this review** (my first read caught
the r20-state rows; the current bytes carry r21-measured rows). Findings below are against the
current bytes re-read after that change; the pre-rewrite drift is recorded as verified history.

## Findings by severity

### F1 (HIGH) — C1 row claims "C1 measured" but the measured corpus omits the preregistered `recovery/` transcript directory

- Preregistration C1 measure: count-read-root.py "over **every** committed transcript in
  `census/round-20/transcripts/{final,recovery,recovery-final}`". The committed transcript set is
  192 files: 64 in `final/`, 64 in `recovery/`, 64 in `recovery-final/` (directory listings).
- The calibration row's counting command names only two dirs:
  `python3 -B census/round-21/count-read-root.py --tool <tool> --transcripts census/round-20/transcripts/final --transcripts census/round-20/transcripts/recovery-final` (SCORECARD.md:14).
- The receipt confirms the omission: `census/round-21/read-count-after.txt` ends
  `SUMMARY files=128 calls=2317 read_root=2` — 128 = 64 (final) + 64 (recovery-final); the 64
  `recovery/` transcripts were never counted. `recovery/` is not a duplicate export: its bytes
  differ from `recovery-final/` (e.g. `OracleCallerCases.txt` 32.5KB vs 49.1KB), so skipping it
  skips real, distinct committed calls.
- The verdict text compounds this: "actual committed**128** transcripts2317 calls gain2 named
  minor flags" (SCORECARD.md:14) presents the partial corpus as the whole committed corpus.
  The omitted directory is precisely the recovery wave that produced the routed "implicit
  root-namespace reads by 5+ seats".
- Required change: add `--transcripts census/round-20/transcripts/recovery` to the counting
  command, re-measure, and restate the row with the true 192-file denominator (per-dir counts
  if read_root changes). Until then the row is author-measured on 2/3 of the preregistered
  corpus, not "C1 measured".

### F2 (HIGH) — preregistered per-call oracle equality is absent from rows and receipts

- Preregistration C1: "the after set must EQUAL an independent per-call oracle
  (`census/round-21/read-root-oracle.tsv`) labelled by non-implementing seats (precision and
  recall both exact; any disagreement falsifies)."
- `census/round-21/` (working-tree listing) contains `read-count-{before,after}.{txt,json}` but
  **no `read-root-oracle.tsv`**. Neither receipt contains an `ORACLE` line
  (`read-count-after.txt` shows only ROW/CLASS/SUMMARY, exit=0), and the row's counting command
  passes no `--oracle`. The tool already supports it (`count-read-root.py --oracle` checks
  tp/fp/fn and unlabelled/extra-labelled calls, exiting nonzero on any mismatch).
- Required change: land the labelled oracle TSV, add `--oracle census/round-21/read-root-oracle.tsv`
  to the row's command, and record the `ORACLE tp=… fp=0 fn=0 missing=0 extra=0` receipt before
  the calibration row and the 'seat transcript audit' capability row carry C1 as measured.

### F3 (MEDIUM) — sibling row 'seat-audit delivery and signal classes (r19)' cites counts the committed fixture no longer has

- Row (SCORECARD.md capabilities): "`tools/souji-seat-audit.py --selftest` 73/0;
  `tests/fixtures/r19-seat-audit-shapes.py` 5/0".
- The committed fixture has grown to 17 cases with 12 baseline discriminators: r20 acceptance
  record `census/round-20/final-acceptance-5ff7565.json` step `r19-seat-audit-shapes` →
  `SUMMARY total=17 failed=0 base_discriminating=12`; r20 closure rechecks agree ("17/0 (12 base-disc)").
  Older r17/r18 rows keep historical counts of fixtures that did not change; this fixture DID
  change, so "5/0" no longer describes any committed bytes. Checkable false statement in the
  same table my two rows live in.
- Required change: cite 17/0 base 12 (or annotate 5/0 as the r19-era count of the since-extended
  fixture, with 17/0 as current).

### F4 (LOW) — capability-row evidence nits

- 'seat transcript audit' row evidence "r21 fixture32/32 (base18/32)" never names the fixture
  (`tests/fixtures/r21-read-root.py`, named only in the axis-row command) and does not say what
  base18/32 means. The fixture's expectations are literal with positive/negative cases; prereg
  requires "every positive case base-discriminating", so the checkable form is "baseline passes
  only the 18 negative controls; 14/14 positives discriminate". Say that, and name the fixture.
- Operability row counting command uses placeholders (`--lane <local-source> --work
  <new-var-tmp-dir>`). Acceptable for an any-source runner, but the receipt
  (`census/round-21/replay-matrix-integrated.json` / `final-matrix.json`) is what pins the actual
  sources; consider citing it alongside `replay-{before,integrated}.txt`.

### F5 (VERIFIED HISTORY — pre-rewrite drift, now repaired; recorded so closure can check the repair)

1. Admission status: both axis rows said "r20 measured, **not admitted**"/"outside admission
   pending" while r20 closed **admitted** (`census/round-21/r20-closure-excerpt.json`:
   `"admitted": true`, verdict "admitted"; prereg line 2). Now fixed (SCORECARD.md:17-19 prose,
   "R20 is now independently admitted"; Planned r20 row "— admitted").
2. Stale counting command (both axis rows): the recorded r20 command
   `python3 -B census/round-20/run-acceptance.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 5ff75657427c4793fbf1f124d794f1c99359d74e --output census/round-20/final-acceptance-5ff7565.json`
   is no longer replayable for three independent source-verified reasons:
   (a) `census/round-20/run-acceptance.py` main() refuses any root besides the hardcoded LANE
   ("root must be the lane path…"); (b) it refuses `--rev != HEAD` ("--rev must be the committed
   current HEAD…"), and the lane tip moved past 5ff7565 at r20 closure (6ff3413b, now r21 work);
   (c) `write_exclusive` opens the output O_EXCL, and the recorded output path exists. The r20
   closure recheck concedes exactly this ("a non-author cannot replay it at 6ff3413 without
   mutating the lane checkout"). Now replaced by `census/round-21/run-acceptance.py` +
   `replay-matrix.sh` with the preregistered S1/S2/S3 shapes 0/3→3/3 — matches prereg C2
   (non-lane different-HEAD clone, bare source, lane source).
3. 'seat transcript audit' row was stale: selftest "20/20" (r16-era; current pinned 118/0 in the
   r20 acceptance record step `auditor-selftest`, and prereg harm guard keeps 118/0), class list
   missing the r19 delivery/signal and r20 grant/receipt/drift classes, and "no probe class"
   overstated after R20-M15 (truncated-inside-scratch writes → V-WRITE-UNPARSED) and R20-M17
   (root-read red-before control; Q45 exact root reads → V-RECURSIVE). Rewritten row now says
   "r20 118/0 selftest preserved", "r21 supplements absolute-root recursion with visible
   outside-lane relative/implicit reads", and keeps "Truncation and Bash-generated writes remain
   limits, not clean evidence" — matches prereg C1's disclosed lower bound (truncated targets
   never flagged).
4. The old precision caveat "4 of 20 wave-1 rows were not violations" was real but its cited
   evidence was wrong: `census/round-16/seat-audit-w1.json`/`w2.json` contain only raw counts
   (w1: 1 major + 19 minor = 20 calls; grep finds no adjudication markers in either). The
   adjudication lives in `corpus/lessons/round-16.md` ("4 of the 20 rows are not violations (two
   exact-file greps, one bounded glob, one aborted write)", and the resolved
   `RevengeSeatViolations.md:260` entry). The rewrite dropped the stale caveat; if the number is
   ever re-cited, cite round-16.md, not the JSONs.

### F6 (verified consistent — no drift found)

- Coverage axis row vs `census/round-20/source-census-final.json`: sources 88→99, A84→95/B3/C1,
  mined 69→78, queued 15, rejected 4→6, admitted_entries 7, F2_entry 1, evidence_gate 1 — all
  match the recorded before/after counter outputs. Current C3 additions (6/27→27/27, leaks 19→0,
  max reason 454→160, sinks 1/2→2/2, S100/S101) match prereg C3, the F5 knowledge entry's r21
  section, and existing receipts (`census/round-21/reason-oracle-before.txt`, `reason-after.txt`,
  `cmd-compatibility.json`).
- 'process-residue observations' row (current): "list-only historical scanner; current cmd/reason
  output share secret patterns and 160-byte bounds… No live measurement, unknown-pattern or
  historical-exposure proof; never signal inherited processes" + "r18 live-proc fixture not run"
  — exactly the prereg C3 boundary (synthetic-only repair; historical exposure stays operator
  L0; Q49 supersedes Q46's source-only disposition, keeping the cmd-only-canary caution). Its
  historical evidence also checks out: "original 19/0 proc fixture" = `corpus/lessons/round-18.md`
  "proc fixture P1–P19 is 19/0"; "two 66=66 agreement pairs" = same lesson, named
  `census/round-18/proc-agreement-final.json` / `proc-agreement-counterfix.json`.
- C1 before/after harm guard: `read-count-before.txt` and `read-count-after.txt` show identical
  non-new class counts (V-EXEC 18, V-RECURSIVE 9, V-WRITE-RELATIVE 30, V-WRITE-SCOPE 179,
  V-WRITE-UNPARSED 38; V-READ-ROOT 0→2) — matches "no existing class verdict changes".
  Both flagged calls are true positives under the prereg rules (relative targets resolving at
  the fleet cwd outside the lane): `final/ReopenHistoryReject.txt:54 read .ufo/waves/round-20/final/ReopenHistoryReject.md`,
  `recovery-final/CorpusAdmission.txt:45 glob corpus/lessons`.
- Coverage axis row (pre-rewrite) carried one unbacked clause: "(same source inventory at final
  code 5ff7565…)" had no counting command/output at 5ff7565 in `source-census-final.json` (only
  12516f7 and b7b606b1 runs) — contradicted SCORECARD's own header rule. The rewritten row no
  longer makes that claim; noted so it is not reintroduced.

## What the r21 rows must still change (summary)

1. Calibration row + 'seat transcript audit' row (C1): add `--transcripts
   census/round-20/transcripts/recovery` (true 192-file denominator), land
   `census/round-21/read-root-oracle.tsv` and add `--oracle` with a 0-FP/0-FN/fully-labelled
   receipt; only then "C1 measured". Name `tests/fixtures/r21-read-root.py` and gloss
   base18/32 = 18 negative controls passed, 14/14 positives discriminating.
2. 'seat-audit delivery and signal classes (r19)' row: 73/0 and 5/0 are superseded by the
   committed fixture's 17/0 (base 12) and selftest 118/0.
3. Coverage + 'process-residue observations' + operability rows: no change required against the
   prereg as written; F6 items stand as verified.

## Residual risk / verification gaps

Read-only seat: nothing was executed; every count above comes from committed receipts/records,
not a rerun (static expectation is labelled as such). I did not clause-audit the new
`census/round-21/run-acceptance.py` (30.6KB) against every prereg C2 refusal (short rev,
output-inside-clone, write-into-SRC) — out of row scope; the S1/S2/S3 receipts exist and the
axis row matches the prereg scenario wording. The oracle TSV may be in flight from the
non-implementing seats labelling it; F2 states the gap in the current bytes, not intent.
Tool anomaly: a directory listing served for `census/round-18/` matched no real directory
content; reported to `xd://report_issue`; no finding relies on it.
