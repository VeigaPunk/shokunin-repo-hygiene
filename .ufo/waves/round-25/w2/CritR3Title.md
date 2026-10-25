# CritR3Title — adversarial review of the r24 C3 title correction (W2)

`STATUS: PARTIAL`

Seat: `L1Souji25.CritR3Title` (critic, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Scan date: 2026-10-25 (round 25, wave 2). Read-only; no lane file edits beyond this report.

## Target

D1 / R24-M25: the r24 C3 claim must be retitled to the two named r23 residuals — **R1
closed (non-durable rev) and R2 narrowed (tool= argv label presence)** — never general
verify/run symmetry. Scan SCORECARD.md, LOG.md, corpus/README.md and the lessons for any
**surviving current overclaim** and report exact locations. Historical records are not to be
rewritten.

## Verdict

The corrective statement exists and is worded correctly in two places, but it is incompletely
landed and several old-title / overclaim texts survive unmarked in all four scanned documents,
including one assertion that *contradicts* the correction. Hence PARTIAL.

## Positive control (the correction itself is correct)

- `SCORECARD.md:243` (Round 25 append-only corrections): "R24-M25: C3's old title
  \"receipt verify/run symmetry\" overclaimed. At r24, R1 closed and R2 narrowed (label
  present in argv); general symmetry remains unproved."
- `corpus/README.md:553`: "closes R1 (non-durable `verify` revision) and narrows R2
  (`tool=` occurs in `cmd=` argv)" + "it does not establish general `run`/`verify` symmetry".

Both say exactly what the task requires: R1 closed, R2 narrowed (argv label presence), not
general symmetry.

## Surviving overclaim / old-title locations (findings)

### F1 — SCORECARD.md:181 and :225: the old title survives in a live, fenced, unintegrated insert block
The whole r24 measurements block is still a **fenced markdown draft** sitting under `## Retired`
(`SCORECARD.md:172-227`), with its scribe instructions intact ("Insert the table below directly
above `### Round 23 measurements` ..."). The w1 patch draft (`scorecard-patch.md` P0/H2)
confirms this was a known defect and specifies the retitle. At inspection the block is unchanged:
- `SCORECARD.md:181` (table row claim cell): "C3 receipt verify/run symmetry"
- `SCORECARD.md:225` (r24 done line in the planned pair): "C3 receipt verify/run symmetry
  (refusals 0/2 → 2/2, regress 5/5)"

The append-only correction at :243 names the old title but does not touch or mark these two rows;
the file's own trailing note (`:250`) still cites `SCORECARD.md:181` as the authority location,
so the overclaiming title remains the referenced text.

### F2 — LOG.md:1628: the r24 section header still overclaims, and LOG carries no correction at all
- `LOG.md:1628`: "Round24 (2026-10-25) — F2 debris census, coverage-map agreement, receipt verify symmetry"
- No `R24-M25`, "retitle", "overclaim" or "receipt verify durability" text exists anywhere in
  LOG.md (grep: no matches). D1's "retitle ... in SCORECARD/LOG" is therefore unmet on the LOG
  half; the LOG entry's body (:1673-1685) is honest (named limits, "1 closed, 6 narrowed"), but
  the header and claim title remain uncorrected and unmarked.

### F3 — corpus/README.md:504 and :519: old title in section header and row title cell
- `corpus/README.md:504`: "## Round 24 — F2 write-safety census, coverage-map agreement, receipt verify symmetry"
- `corpus/README.md:519` title cell: "Receipt verify/run symmetry (r23 residuals)".

The correction exists later at :553, but the two earlier occurrences are unmarked; a reader
reaching the table first sees the old title.

### F4 — corpus/README.md:519: an unsupported "mirrors" assertion contradicts the correction
Within the same row :519: "`verify` mirrors run's command refusals (`RECEIPT-COMMAND-REFUSED`)"
is stated as current runner behavior, while the row itself says the run-side refusal shapes are
"Not counted by the fixture". No counter case exercises run-side refusals, so this asserted
mirroring is not witnessed by the frozen fixture and directly conflicts with :553
("does not establish general `run`/`verify` symmetry").

### F5 — the r23 "bytes the command ran against" wording survives (R2/R3 family)
The same argv-label narrowing concern persists in the current r23 records:
- `SCORECARD.md:92` (capabilities row `blob-bound receipts (r23)`): "tool sha256 of the bytes the command ran against" — no appended dated note, despite the "Optional same-landing correction" instruction at :217-220.
- `corpus/README.md:471-472` (Round 23 C2): "the sha256 of the bytes the command actually ran against".
- `LOG.md:1588` (Round 23 C2): "tool sha256 of the bytes the command ran against".

### F6 — lesson titles and verdict tables keep the old title (historical, internally falsified)
- `corpus/lessons/round-24.md:1` (title): "receipt verify/run symmetry"; `:20` table row title: "C3 receipt verify/run symmetry". The lesson body falsifies it (`:79-83`: "**The title \"verify/run symmetry\" is falsified.** ... Report C3 as \"two named r23 residuals closed (`refusals=2/2`)\", never as symmetry.") and `:249` limits the claim to R1/R2. So this is a historical record with intrinsic falsification, but the title itself remains unmarked.
- `corpus/lessons/round-24-verifier-spotcheck.md:38`: re-check table row "| C3 receipt verify/run symmetry | operability (8) | ... improved |" — the non-author spot-check's own D1 (:88-91) routes the retitle, so the row is historical and routed, but still presents the old title with an "improved" verdict.

### F7 — references to `corpus/lessons/round-25.md` dangle: the file does not exist
`SCORECARD.md:136,:244`, `corpus/README.md:544,:553,:555` reference `corpus/lessons/round-25.md`
(for the survivor disclosure, Q57 check, vocabulary mapping). At inspection that file is absent
(`read` → not found). The preregistered future symmetry counter cases (the remaining run/verify
shapes) are supposed to be named there; they are not yet on record anywhere findable.

## Attack log (evidence)

- Read: round-25 prompt, preregistration + amendments state (read), SCORECARD.md (full + raw
  170-250), LOG.md (grep + 1585-1603, 1627-1713), corpus/README.md (full + raw 515-555),
  lessons round-24.md, round-24-verifier-spotcheck.md, w1 patch drafts (scorecard-patch.md,
  readme-patch.md, readme-patch-2.md).
- Greps (case-insensitive) over target docs: `symmetry|verify/run|run/verify|R24-M25|retitl|overclaim|mirrors?|19 of 36|argv` — hit list: SCORECARD 181/225 (fenced), LOG 1628/1588, README 504/519/471, lessons round-24 1/20/79/82, spotcheck 38/88. No other occurrence.
- Confirmed absence: `corpus/lessons/round-25.md` (not found); LOG has no R24-M25/retitle/overclaim text.
- No commands executed (read-only review; no scratch needed).

## Smallest safe corrections (advisory; L1 decides; history not rewritten)

1. Execute the already-drafted P0 + H2 content-preserving move: integrate the fenced r24 block
   and retitle the two claim cells to "C3 receipt verify durability + tool= argv binding (r23
   residuals R1/R2)" with the append-only "filed as ..." marker (exact replacement text is in
   `scorecard-patch.md` H2). If the block stays inert, mark it append-only as
   "superseded by Round 25 corrections" instead.
2. LOG: append an R24-M25 entry (same wording as SCORECARD:243) after the round-24 block; do
   not touch LOG:1628 itself.
3. README: append the :553-style marker note to the :504 header / :519 title cell (or rely on
   :553 but state it covers the headers), and delete or qualify the unwitnessed
   "`verify` mirrors run's command refusals" clause at :519.
4. Append the dated R3 note to SCORECARD:92, README:471-472, LOG:1588 (the instruction at
   SCORECARD:217-220 already prescribes the exact note).
5. Land `corpus/lessons/round-25.md` with the named future symmetry counter cases so the
   references at SCORECARD:136/:244 and README:544/:553/:555 resolve.

## Impacted axes

- Calibration (7): self-assessment docs still carry an overclaiming claim title in current reading
  positions (F1-F3, F5-F6).
- Operability (8): the unsupported "verify mirrors run's command refusals" assertion (F4)
  overstates tool behavior beyond fixture coverage.
- Coverage (8): no direct impact; dangling lesson reference (F7) is a conformance/operability
  defect.

No axis harmed by this review; findings are advisory.
