# ScoutScorecardLines — round 25 w1: exact edit targets for the non-claim fixes

## Status

STATUS: PASS — every named target located at tip a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe with line number, current wording and a suggested replacement. Two structural preconditions and two ATTACKs on the routed-fix wording are reported below (findings 1, 2, 9, 12).

## Evidence

- Revision: SCORECARD.md, LOG.md and corpus/README.md are byte-identical at a6d2d15, at 6e4737e (lane HEAD) and in the worktree (`git show <rev>:<f> | cmp`: SC-same, LOG-same, README-same, all three wt-same). So every line number below holds at all three. Lengths at tip: SCORECARD 228 lines, LOG 1713, README 536.
- Phrase sweep (`git grep -nE 'verify/run symmetry|verify symmetry|run symmetry' a6d2d15`): lane-record hits are SCORECARD:180, :224; LOG:1628; README:504, :519; lessons/round-24.md:1, :20, :79, :173; round-24-verifier-spotcheck.md:38, :88.
- R3 sweep (`git grep -nE 'bytes the command (actually )?ran against' a6d2d15`): SCORECARD:92, :217 (draft note), LOG:1588, README:472, plus wave reports.
- Counter sweep (`git grep -nE "tool_sha256=\[0-9a-f\]" a6d2d15`): SCORECARD:22; LOG:1591; README:457; QUALITY.md:129 (Q55 check cell); lessons/round-23.md:30.
- A read-only `verify` re-count at tip (git 2.56.0; runner `tools/souji-receipt-run.py` worktree==tip, `cmd_verify` only reads git objects, tip:tools/souji-receipt-run.py:305-338). I extracted each file to /var/tmp scratch with `git show a6d2d15:<f>` and ran `python3 -B tools/souji-receipt-run.py verify --root . <copy>`:
  - `git grep -lE '^tool_sha256=[0-9a-f]{64}$' a6d2d15 -- census/` → 21 files.
  - 19 → `verify=ok` rc 0. That covers all 5 under `census/round-23/records/` and 14 under `census/round-24/records/`.
  - 2 → `RECEIPT-MALFORMED` rc 2: `census/round-24/records/r23-agreement-regress.out` and `census/round-24/size-census-lane.txt`.
  - (LOG:1700 recorded "15 files … 14 verify=ok" at r24 time. The `*-final.tsv` receipts landed after that sentence.)
- Provenance of the SCORECARD/LOG r24 blocks: SCORECARD:170-228 and LOG:1627-1713 each occur verbatim inside `.ufo/waves/round-24/w2/W2ScorecardDraft.md` (python `a.strip() in b` → True for both). That draft has the headings "## Draft A — SCORECARD.md append" (:75) and "## Draft B — LOG.md append" (:136). The commit that introduced them is 315422ba9970f03c27f8a9184446783b7fcdf0a7 (`git log -S'Insert the table below directly above' -- SCORECARD.md`).
- Tools that parse these files (constraints on any edit):
  - Coverage-agreement splits cells with `(?<!\\)\|`, so escaped pipes do not split (tip:tools/souji-coverage-agreement.py:28). A map row needs a ground cell matching `^F([0-9]+)(?=[ \-]|$)` (:26).
  - Record-agreement K1 scans SCORECARD lines matching `\br22\b|round-22` that carry a 4-tuple (tip:tools/souji-record-agreement.py:47-48).
  - Record-agreement K3 scans EVERY line of corpus/README.md for `<n> accepted|present|unverifiable|refused`. Each count must equal the r22 slice tally (:61, :72, :314-321).

## Findings

1. **STRUCTURE (precondition): SCORECARD's r24 material was pasted as a draft, not integrated.** The draft starts after `## Retired` / "None." (SCORECARD:166-168). It is introduced by the instruction prose at SCORECARD:171: "Insert the table below directly above `### Round 23 measurements` (newest first, matching the file's order)." It then has three ```` ```markdown ```` fences:
   - :173-207: the Round 24 measurements table plus limits.
   - :211-214: two capabilities rows.
   - :223-226: the Planned r24-done and r25-planned lines.

   Between the fences sit the R3 note (:216-219) and the Planned instruction (:221), and the block ends with `---` (:228). Consequences:
   - The real `## Planned` section (:95-135) ends with r23-done (:133), r24-planned (:134) and r22 (:135). The r24-done and r25-planned lines exist only inside the fence at :224-225.
   - The r24 capabilities rows are not in `## Capabilities` (:63-93).
   - "see Findings 6" (:171) points at the draft's findings, not at anything in SCORECARD.

   Any "replace the r25 line" edit targets :225 inside a code fence. The L1 must decide one of two things:
   - (a) leave :170-228 as filed history and append r25 material after :228, with a note naming the fence paste; or
   - (b) move the fenced content under its headings. That is an in-place restructure, and it shifts every line number below.
2. **STRUCTURE (precondition): LOG's Round24 entry is also the draft paste.** LOG:1627 opens ```` ```text ````, LOG:1711 closes it and LOG:1713 is `---`. Both come verbatim from W2ScorecardDraft Draft B. The Round23 entry (LOG:1563) is unfenced, with a `=` underline. LOG is append-only by precedent ("appended; the entry above stands as written", LOG:886). So corrections land after :1713.
3. **SCORECARD:180 — r24 C3 claim title (Round 24 measurements row, inside the fence).**
   - Current claim cell: "C3 receipt verify/run symmetry".
   - Suggested (append-only note after :228, or an in-cell marker if L1 chooses (b)): `C3 receipt verify: non-durable rev refused (r23 R1, closed) and tool= label bound to argv membership (r23 R2, narrowed) — retitled r25 (R24-M25); filed title "receipt verify/run symmetry" retained as history`.
4. **SCORECARD:224 — the same title in the r24-done Planned line (inside the fence).**
   - Current: "C3 receipt verify/run symmetry (refusals 0/2 → 2/2, regress 5/5)".
   - Suggested: the same retitle as finding 3, carried in the same appended r25 note. Do not rewrite :224, because it already quotes "1 of 20 closed (verify durability), 6 narrowed, 12 open", which agrees with the retitle.
5. **SCORECARD:92 — `blob-bound receipts (r23)` capabilities row, R3.**
   - Current: "emit a receipt binding rev, tool path, tool sha256 of the bytes the command ran against, argv, exit code and redacted output".
   - The draft instruction at SCORECARD:219 already says "Append a dated note to the row; do not rewrite the r23 sentence."
   - Suggested in-cell append (no pipes): `*(r25 note, r23 residual R3: the recorded digest is the sha256 of the committed blob at rev= of the path labelled tool=; run refuses when the checked-out bytes differ (TOOL-CHECKOUT-DIFFERS), and since r24 verify requires that label to be an argv element of cmd= (RECEIPT-TOOL-NOT-IN-ARGV). It does not bind the program that executed.)*`
   - Grounding: tip:tools/souji-receipt-run.py:244-254 ("the digest is taken from the tree the command runs in") and :321-336 (verify compares `blob_sha_bytes(root, rev, tool)` and checks `tool not in argv`).
6. **SCORECARD:22 — r23 C2 counter (Round 23 measurements row).**
   - Current before cell: "0 receipts carrying `tool_sha256=` under `census/`". Current command cell starts "`grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/" and then "then `python3 tools/souji-receipt-run.py verify --root . <receipt>` for each".
   - Suggested in-cell append to the counting-command cell: `*(r25: the counted quantity is receipts under census/round-23/records/ for which python3 -B tools/souji-receipt-run.py verify --root . <receipt> prints verify=ok — 5 of 5 at a6d2d15; the tool_sha256= grep is a file filter, not the count: at a6d2d15 it matches 21 files under census/, 19 verify=ok, 2 RECEIPT-MALFORMED non-receipts)*`
   - The before cell needs no change (0 files means 0 verify=ok).
   - Same counter, same treatment (append, do not rewrite): LOG:1591 "grep -rlE '^tool_sha256=[0-9a-f]{64}$' census/" … "0 before, 5 after"; README:457; QUALITY.md:129 (Q55 check cell, outside this item's scope, flagged only).
7. **SCORECARD `## Planned` r25 line — SCORECARD:225 (inside the fence).**
   - Current: "**r25 (planned r24):** (a) calibration: make C2's per-entry kill rule (base-grounded entry absent or re-grounded at tip) a tool row instead of a hand `git diff`; …".
   - Do NOT replace it. The file's convention keeps planned/done pairs (SCORECARD:117-129, r16-r19). The draft's own instruction (:221) says "append after the existing … line, keeping it, as the r16–r19 pairs do". Append a done-entry instead.
   - Suggested skeleton (scribes fill the values from receipts): `- **r25 (planned r24) — done, see corpus/lessons/round-25.md:** C1 kill-rule tool row (kill_tested=<K> kill_violations=<V>; fixture cases=<C> pass=<P>), C2 size-census refusal surfaces (cases=<n>/12), C3 structure probe under the common-dir envelope (ids=<n>/7), as measured in the Round 25 table. Of the planned list: README :40 marked superseded; the r23 C2 counter reworded to a verify=ok count; the r23 record-agreement counter receipted at <tip>; R3 note appended; R7 fixture note in the lesson; R15/R17 docstring and cases. Not done: <enumerate — see finding 9>. Certification OFF, K5 HELD; F5 reap and NAMESPACE holds unchanged.`
8. **LOG:1628 — r24 title line (inside the ```` ```text ```` fence).**
   - Current: "Round24 (2026-10-25) — F2 debris census, coverage-map agreement, receipt verify symmetry".
   - The C3 paragraph itself, LOG:1672 "C3 operability (8). tools/souji-receipt-run.py verify now refuses a", carries no claim-name title. The title exists only in the :1628 header, so the "paragraph title" target is :1628.
   - Suggested appended block after LOG:1713, unfenced, in the r23 shape: `Round25 corrections to Round24 (appended; the Round24 entry above stands as written)` followed by a `=` underline line, then three numbered items:
     - **1. Title.** "receipt verify symmetry" (LOG:1628) asserts more than the C3 counter witnessed (R24-M25; verify refuses 19 of 36 run-written argv shapes). Retitled: receipt verify — non-durable rev refused (r23 R1, closed); tool= bound to argv membership (r23 R2, narrowed — an operand-only label still verifies). Remaining run/verify shapes are preregistered as future counter cases in corpus/lessons/round-25.md.
     - **2. R3.** LOG:1588 "tool sha256 of the bytes the command ran against" is superseded by: the sha256 of the committed blob at rev= of the path labelled tool=; not a binding of the executed program.
     - **3. Counter.** LOG:1591's grep counts files carrying a tool_sha256= line; superseded by the verify=ok count: 5 of 5 r23 receipts at a6d2d15 (whole census/: 21 files, 19 verify=ok, 2 RECEIPT-MALFORMED).
   - "superseded by" outside the `Round22 attempt2` section does not affect K2 (K2 scans only that section).
9. **ATTACK (calibration) — the prereg's D1 wording says "the two named r23 residuals closed (R1 non-durable rev, R2 tool= argv binding)" (preregistration "Routed fixes", D1).** The r24 record says otherwise:
   - RevR23Residuals.md:91 says C3 "**partially closes**" R2 ("Case b's predicate … is met by a command where the tool appears only as an operand while a different program runs").
   - SCORECARD:224 reads "1 of 20 closed (verify durability), 6 narrowed".
   - A retitle that says R2 is "closed" would re-create the R24-M25 overstatement on the lowest axis. The suggested titles above say "R1 closed, R2 narrowed".
   - Also flagged for the done-entry's "Not done" list: these r25-planned items (SCORECARD:225) have no counter or routed fix in the preregistration:
     - `size-census-lane.txt` → v1 receipt or relabel. It is named in prereg inbound, absent from "Routed fixes", and still `RECEIPT-MALFORMED` at tip.
     - The `census.warning=` / exit-1-on-other-stderr case and the not-a-repository exit-2 case.
     - The ctime / read-only-`.git` arm. D3 is disclosure only.
     - The re-verification of the two git-2.55.0 entries.
     - Item (c), program-position binding.
     - The LEARNING.md fleet route.
10. **README:40 — F2 status cell (r12 coverage map).**
    - Current status cell: "frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: …→ 0, 2026-10-19)". The entries cell is "—".
    - The row parses as 3 cells because the inner pipes are escaped (`\|`), and the tool honors the escape.
    - Suggested in-cell append (keep the existing text, add before the closing ` | — |`): ` — *superseded by the Round 24 F2 row (:517) for entries; this cell is r12 history (r25, R24-M2)*`
    - Constraints:
      - Introduce no unescaped `|`, or the row's entries column shifts.
      - Add no line, because :40/:42/:68/:217/:233-234 are cited by line at README:506-508, :526, SCORECARD:196, :225 and in the preregistration.
      - Include no `<n> accepted/present/unverifiable/refused` text (K3 scans every README line).
11. **README:517 — Round 24 F2 row, entries column.**
    - Current entries cell: "`knowledge/git-repo-structure-readonly.md` (S035–S037); `knowledge/repo-size-census-readonly.md` (S115–S117); `knowledge/count-objects-garbage-readings-r25.md` (S118–S119); `knowledge/count-objects-linked-worktree-garbage.md` (r24, assimilated); `../tools/souji-size-census.py`; `../tests/fixtures/r24-size-census.py`; `../census/round-24/size-census-lane.txt`".
    - Suggested: do not mutate :517. Append a `## Round 25 — …` section after README:536 with a map table: header `| ground | status | entries / runnable evidence |`, plus an F2 row.
    - That row's entries cell should name all five F2 entries: the four above plus `knowledge/git-repo-structure-common-dir.md` (S124/S125), with `../tests/fixtures/r13-repo-structure.sh`. Then the newest F2 row stays the single complete entries list. That avoids the r23 prose/table class README:531-536 says "can recur undetected".
    - The new section's prose says it supersedes :517 for the entries column only, in the same form as README:506.
12. **Is README:40 the only in-place mutation needed? Conditionally yes; as worded, no.**
    - Rules found:
      - README:27 "appended; sections above stand, corrections below".
      - README:506 "Appended; the sections above stand."
      - README:495-496: the one sanctioned in-place correction was justified as a departure ("This departs from this file's \"corrections below\" convention deliberately").
      - LOG:886 "appended; the entry above stands as written".
      - QUALITY Q55 (:129): "filed receipts are append-only".
    - The preregistration itself makes README:40 the one in-place edit (D4: "status cell gains an append-only … marker"). An in-cell suffix keeps the old words, so it matches the r9 SCORECARD precedent (:140 "this prose formerly said 6/7 — corrected r9").
    - A second in-place mutation appears only if scribes follow the prereg C3 sentence literally ("README F2 row entries column gains the entry (Q56)") by editing :517. Q56 is satisfied by any F<k> map row, so an appended Round 25 row (finding 11) avoids it.
    - README also carries copies of the other routed defects that the prereg names only for SCORECARD/LOG. Fix them by appended notes in the Round 25 section, never in place:
      - The r24 title at :504 (heading) and :519 (ground cell "Receipt verify/run symmetry (r23 residuals)").
      - R3 at :470-472 ("the sha256 of the bytes the command actually ran against").
      - The r23 grep counter at :457.
    - The SCORECARD edits (findings 3-7) are in-place only if L1 picks option (b) of finding 1.

## Attack log

- A1 (finding 9, calibration): the D1 retitle wording "R1 … R2 … closed" overstates R2. r24's own residual review records it as partially closed. Target the "narrowed" wording or the lowest axis is harmed.
- A2 (findings 1/2, operability): the integration targets the task names ("the `## Planned` r25 line", the "Round 24 measurements row") sit inside committed ```` ```markdown ```` / ```` ```text ```` fences pasted from W2ScorecardDraft. Any scribe edit keyed to "the section" will miss or duplicate. L1 must choose append-after-:228 / after-:1713 versus restructure before scribes draft.
- A3 (finding 7): "replace the r25 line by a done-entry" contradicts SCORECARD's kept-pair convention and the draft's own :221 instruction. Append instead.
- A4 (finding 9, coverage of the planned list): six r25-planned items have no preregistered counter or routed fix. A done-entry that omits them would overstate completion.

Scratch `/var/tmp/souji-r25-ScoutScorecardLines/` removed after writing. No tools installed. No lane file other than this report was written.
