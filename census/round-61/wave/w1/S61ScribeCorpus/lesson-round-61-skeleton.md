# Round 61 — control-chronology binding and receipt-writer mutant kill-power

Skeleton for `corpus/lessons/round-61.md`. Placeholders (`L1-FILL`, `SPOTCHECK-RESULT`, `QUOTE-PLACEHOLDER-<n>`) are filled by the L1 from the landed evidence; none may land unfilled.

Two claims, both declared by the L1 and frozen before any after-data:
- C1 calibration (lowest legacy axis 7): `tools/souji-freeze-check.py --substance` refuses a control receipt whose adding commit is not a strict ancestor of the freeze commit (`CONTROL-ADDED-NOT-BEFORE-FREEZE`); base and candidate measured on the frozen matrix and on `census/round-60/preregistration.txt` at `d05a00019835dee5b9bb8fe738add080434c4d67`.
- C2 operability: `tools/souji-receipt-write.py` passes the extended ten-case fixture; `tests/fixtures/r60-receipt-write.py` passes both mutants (the worktree-digest writer and the direct-chunk writer).

Base `c7228424c3919ecf142bab1aec8181722d86467b`. Freeze `L1-FILL`. Predicate `census/round-61/preregistration.txt`.

## Gate

- C1 sourced evidence: S290 (git-log `--diff-filter`, opened 2026-11-05) supports the add-commit query. Located quote (access record): QUOTE-PLACEHOLDER-1. Located quote (teaches): QUOTE-PLACEHOLDER-2. Admitted `queued` → `mined` on the L1's capture check: L1-FILL.
- C2 sourced evidence: S291 (git-update-index `--skip-worktree`, opened 2026-11-05) supports the concealment mechanism. Located quotes: QUOTE-PLACEHOLDER-3 (access record), QUOTE-PLACEHOLDER-4 (bit goal). Status: L1-FILL.
- Knowledge entries: `corpus/knowledge/control-chronology-binding.md` (on S290) and `corpus/knowledge/skip-worktree-concealment.md` (on S291). Both are bounded: neither states a measured result.
- Rejected inferences: L1-FILL (candidates: S290 cannot establish execution time; S291 does not state that status hides content changes).
- Assimilation: L1-FILL.
- Verifier spot-check: SPOTCHECK-RESULT (written by the non-author closure, never by the author).

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| unsurfaced rejection-ground finding (self-assessment overreach) | `census/round-60/wave/w1/S60CriticRound/S60CriticRound.md` Finding 1 (Q120 VIOLATES: the control receipts were added by the freeze commit `2670e96a`, while the frozen preregistration said they were committed earlier); `corpus/lessons/round-60-verifier-spotcheck.md` (rejected-harmed on the same ground; the r60 report and lesson surfaced five other critic limits and not this one) | none (no rule required surfacing every critic finding that contradicts a filed assertion) | new QUALITY criterion Q121: every reviewer or critic finding that contradicts a filed assertion appears in the round lesson's `## Mistakes` or `## Named limits` with its disposition; this round's sweep is its first use |
| L1-FILL | L1-FILL | L1-FILL | L1-FILL |

## Named limits

- L1-FILL — C1 binds the add commit's graph position and a strict ancestor relation. It does not bind execution time, and a truthful forgery with an early add passes (`corpus/knowledge/control-chronology-binding.md`).
- L1-FILL — C1 reads only the first add of a receipt path; a later rewrite is not read by the chronology rule.
- L1-FILL — C2 kill-power is measured for the two named mutants only. Other mutants are unmeasured; name the survivors the extended fixture does not kill.
- L1-FILL — the `concealed-divergence` case tests the skip-worktree route only; assume-unchanged is a different bit with a different goal (`corpus/knowledge/skip-worktree-concealment.md`).
- L1-FILL — the status-silence reading of skip-worktree is a round probe result, not a sourced fact.
- L1-FILL — any residual from the r60 limits that this round does not close (named, not rewritten).

## Integrated verification

- L1-FILL — the commands the L1 runs once after all seats settle, with the exit code and the measured output for each.
