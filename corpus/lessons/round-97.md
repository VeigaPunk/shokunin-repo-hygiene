# Round 97 — the latch does not close the trade, the reap is unsafe, and both claims are withdrawn from admission

Lane base `210084b24de1dd1f1fd499f49b0c70744f099f5f` (r96 closed `ok`). Instruments P1 `053287d4`, controls P2 `677a6cbb`,
freeze F `5314d01d`, wave w1 (13 seats, attempt 1, SoujiR97). Amendments: `plans/round-97.md` A0 and A7–A17.

## Claims

- **C1 (calibration 7).** The RERAISE-aware latch keeps the 14-shape declared-exit table at `mismatched=0`. Verdict:
  **harmed (trade)**. The table moves 2 → 0, but the caught-then-terminating shape q1q moves 70 → 1 (r96 → r97), and the
  saved-then-bare-raise shape q1o is still declared (A9). Not admitted; score stays 7.
- **C2 (operability 8).** The r97 probe caps output and the counter reaps the T1 grandchild by argv identity, printing
  `survivors=0`. Verdict: **not admitted**. The reap signals own-uid processes it did not plant (A12, HIGH, measured
  30 of 42 decoys). The reap is a refusal-boundary violation, so the claim cannot verify. The hang and output-cap legs
  are real but not separable from the reap in the measured predicate.

## Gate

Source rows this round (URL · access date · located quote, ≤25 words · location):

| row | URL | access | located quote | location |
|---|---|---|---|---|
| S372 (new, tier A) | https://docs.python.org/3/library/sys.monitoring.html | 2026-11-09 | "An exception is re-raised, for example at the end of a finally block." (13 words) | § Events, RERAISE; capture `census/round-97/srcs/monitoring.html` sha256 2b281793…, occurrence 1 |

Re-verified live by the scout seat (`R97ScoutSources.md` §1): the capture is byte-identical to the live page; the quote
occurs once. S368 (setsid(2)) and S365–S371 are carried from r96 and re-verified by the scout seat (occurrence 1 each).

Discernment spot-check (LEARNING.md; non-author seats, reviewers and critic; not the lane's own seats):
- Admit, S372 RERAISE row: **agree** (`R97ScoutSources.md` §2: "The r97 material does not inherit the superseded over-claims").
- Reject: the write(2) EAGAIN candidate was **admitted** by the scout seat (tier A, scope narrowed to the errno clause).
  Not appended this round: the L1 did not take the candidate into the registry (see §Frontier). Recorded as a lead.
- Disagreements: the reviewers and critic disagree with the lane's C1 closure sentence and C2 ownership sentence
  (A9–A12). Those become mistakes below and QUALITY criteria, not silent edits.

Sources-census before/after (`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`):
before 293 rows (lane base, EXIT 0); after 294 rows (S372 added; its row repaired to 11 cells in the same round, A16);
EXIT 0 after repair, no E01. Malformed rows (NF≠13) at round end: 0.

Knowledge entries touched: `corpus/knowledge/crash-channels-beyond-excepthook.md` (r97 section plus appended correction);
`corpus/knowledge/deadline-owned-reaping.md` (r97 section plus appended correction). Both cite S372 or earlier rows.

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## Mistakes

- **M1 — a clear scoped by a frame name, then a "fix" scoped by a global pending flag.** Class: a rule whose eligibility
  names a site (`<module>`, or a flag not keyed to the exception object) instead of the event that decides termination.
  Evidence: `plans/round-97.md` A9; `.ufo/waves/round-97/w1/R97ReviewerC1.md` Q1 (q1o, q1q, receipts `q1o.py`, `q1q.py`).
  Captured-by: none. The 14-shape table had no caught-then-terminating or bare-raise shape, and the predicate summary is
  the same under r96 and r97 (errored=7 killed=2 survived=1). Fix (routed r98): a successor latch keyed on the exception
  object's own state; add q1i/q1o/q1q to the table. **Shown able to fail:** the reviewer's reproducers run under the frozen
  r97 hook print `hooked 1` on q1q and q1o where r96 prints 70 on q1q.
- **M2 — a safety sentence (ownership) written from intent, not measured.** Class: a stated-limit about another process's
  fate. Evidence: `.ufo/waves/round-97/w1/R97Sentinel.md` Finding 1 (decoys killed, `planted-killed 31`). Captured-by:
  none. The printed `survivors=0` and the T1 predicate cannot see a foreign kill. Fix: A12 (C2 not admitted; L0 question).
  Routed r98: ownership by recorded spawn pid and ppid chain. **Shown able to fail:** the continuous-decoy run kills 30 of
  42 foreign decoys under the frozen counter.
- **M3 — a registry row committed with a missing cell block; the lane's own census gate failed closed.** Class: a row
  written in the shape the author had in mind, not the contract shape. Evidence: `corpus/SOURCES.md` S372 at P1
  (7 of 11 cells); `scripts/sources-census.sh validate` exit 1 (`E01 S372 fields=7`). Captured-by: the census script,
  run at round end only. Fix: A16 (repair to 11 cells, 13-word anchor, EXIT 0). **Shown able to fail:** the pre-repair
  census exits 1 with the row named.
- **M4 — a mechanism sentence describing a reorder the code does not perform.** Class: prose describing an implementation
  the bytes do not contain (the r95 M2 class, recurring). Evidence: `plans/round-97.md` A11; `R97ScoutSources.md` §5;
  r96 stderr carries a Traceback on the excepthook channel and r97 does not. Captured-by: none. Fix: A11 (wording
  narrowed; restore-print routed to r98). **Shown able to fail:** the r96-vs-r97 hook stderr comparison.
- **M5 — a control number expected, not measured, and a control run against bytes not in the freeze.** Class: a
  predicate's before-number written from an expectation; a control receipt produced by a counter file that differs from the
  frozen bytes. Evidence: `plans/round-97.md` A7 and A7-correction; `R97ExecC2.md` H-2 (`b460c6f4…` vs frozen `da30593c…`).
  Captured-by: none. The P2 r96-control receipt was run before the reap snapshot edit, and the freeze commit was not
  re-verified against the control's counter hash. Fix: A7-correction (control re-labelled; before-side = r96 committed
  counter receipt). **Shown able to fail:** the ExecC2 pin table compares the control's counter hash to the frozen bytes
  and finds the mismatch.

## Wave findings (summary; full verdicts in the seat reports)

- C1 reviewers: q1o and q1q (FALSIFIES-WORDING, narrowing-grade); Q2 (signal-safe write), Q3, Q4 hold. Shapes reviewer:
  a4 limit false (A10). Critic: predicate strength, basename-table hook is possible in principle (A10). MutC1: 21 mutants,
  7 survive (unbound/equivalent; no falsified sentence). ExecCensus: 278 generated mutants, 0 verdict changes, survivor
  sets byte-identical (no-harm on the population).
- C2 reviewers/critic/sentinel: the sentinel's foreign-kill finding (HIGH) and the critic's basename cheat (A12, A15). The
  reviewer's C2 check reports NO-FALSIFICATION on its own questions, which did not include the ownership sentence.
  ExecC2: GD not refused, GC syntax-error refusal, r96 control counter provenance (A14, A7-correction). Scribe F-2: signal
  exit rendering (A13). MutC2: 9 surviving mutants; CM8 gives the r96 probe 20/20 under a broken counter (A15).
- Connector: sibling overlap and lane-pattern scan (no sibling owns the crash-sentinel or probe-timeout surface per its
  report; `R97Connector.md`).

## Trend verdicts (lane)

- expansion: **unchanged**. One registry row (S372, tier A) and two knowledge entries cited it; no new admitted knowledge
  entry on uncovered ground.
- quality: **harmed**. Two knowledge entries shipped with falsified sentences (corrected by appended notes in this round,
  A9/A11/A12/A13). A withdrawn claim is not a quality gain.
- discernment: **harmed**. The lane's wording overclaimed in three places (C1 closure, C2 ownership, A8 signal exit) and
  its pre-freeze gate did not catch them. Disagreements were recorded, not left unlearned: M1–M5 and Q173.

## Mistakes captured — QUALITY criterion

Q173 (below) is added to `corpus/QUALITY.md` because no existing criterion caught M1 or M2 (Q172 required a shape table of
ordinary exits but not the straddling shapes, nor a count that moves on the rule's own terms).
</content>
