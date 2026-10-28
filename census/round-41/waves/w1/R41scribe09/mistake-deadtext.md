# Round 41 — mistake candidate (R41scribe09): dead-seat error text without a committed location

Proposed id: M41-n (the L1 numbers it on landing). Scope: calibration of a filed cause attribution. Read-only evidence; no lane file edited.

### M41-n — the round-40 dead-seat provider error text was filed as fact with no committed occurrence

- **class:** calibration / record-provenance defect. A specific failure cause is written into a lane record as the cause of two dead seats, and the committed seat results contain neither the text nor any failure record that carries it. Filed statement: `LOG.md:1909` — "2 dead seats (R40w2reviewer01/04, provider error `Codex error event: Invalid prompt: your prompt was flagged as potentially violating our usage policy`)". The same sentence is in the fleet report `.ufo/reports/round-40/souji.md:79` (fleet root, read-only, cited for provenance only).
- **evidence pointer:**
  - Zero committed occurrences of the text under `census/round-40/waves/` at `bffcc0f660ff36eb8add3f61582748a7af019a5b`. `git grep` over the whole lane at that commit finds the phrase only at `LOG.md:1909`, which is the filed claim itself.
  - `census/round-40/waves/w2-results.json` holds the two dead seats' outputs. `R40w2reviewer01` (output 2310 bytes) ends mid-reasoning with no verdict; `R40w2reviewer04` (output 6852 bytes) is a `<think>` block with no verdict. Neither output contains `flagged as potentially`, `Codex error`, or `usage policy`. Across all 64 results the phrase occurs 0 times.
  - No `R40w2reviewer01` or `R40w2reviewer04` report file exists in `census/round-40/waves/w2/`.
  - `.ufo/waves/round-40/w2-run.err` is 0 bytes and is not tracked at `bffcc0f` (`git cat-file -t` fails), so it cannot be the source either.
  - The only committed Codex error text in the lane is a different message, `Codex is at capacity, please try again later (code=turn_rate_limit_exceeded)` (`census/round-20/recovery-seat-outcomes.json`, `corpus/lessons/round-22.md:187`). It is not the filed text.
  - Reading: committed bytes do not show the cause of the two dead seats. The filed attribution may match the orchestrator's live transcript, but that transcript is not a committed receipt. [INFERENCE — unobserved in committed bytes.]
- **captured-by:** the sweep of `corpus/QUALITY.md` (commands and results are in `.ufo/waves/round-41/w1/R41scribe09.md`).
  - `corpus/QUALITY.md:8` carries the fleet floor "a quote its location". The filed error text is a quote with no located source in committed bytes, so it fails the floor.
  - Q25(c) and Q68 are the criteria that should carry seat failures into the lesson. The landing gate (`tools/souji-landing-gate.py --rev bffcc0f660ff36eb8add3f61582748a7af019a5b --round 40`) reports `status_lines=0 carry_heading=0 checked_reports=117`. Its seat-carry check is therefore vacuous for round 40: it reads only `STATUS:` lines and `## Seat-reported failures` sections, and round 40 has neither. `corpus/lessons/round-40.md` has no `## Seat-reported failures` heading (its headings are `## Gate`, `## Mistakes`, `## Frontier`).
  - Q55 does not apply: the filed text is a cause, not a count.
- **fix:** append-only correction of item I4 in `corpus/lessons/round-41.md`. The filed `LOG.md` line is not rewritten. The line below must match the frozen counter's `LINE` grammar and carry the counter's own derived value (`occurrences=0`) at the measured revision:

CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=bffcc0f660ff36eb8add3f61582748a7af019a5b source=-

- **routed to L1 (not part of this fix, not a claim):** the round-40 seat failures were never carried into a lesson section, and the gate's seat-carry check cannot see JSON-verdict or result-only seats. A future seat-failure rule needs to read `census/round-N/waves/*-results.json` rather than only `STATUS:` lines.
