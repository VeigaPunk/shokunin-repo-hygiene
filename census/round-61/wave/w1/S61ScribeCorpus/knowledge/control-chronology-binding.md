# Control chronology binding — a control receipt's adding commit must strictly precede the freeze

ground: F1 — git-native housekeeping vs receipts (the chronology a frozen claim's `Control:` receipt path must have before its red exit can be read as prefreeze evidence; extends `knowledge/freeze-record-substance-binding.md`)
source: S290 — git-log(1) `--diff-filter` (https://git-scm.com/docs/git-log, OPTIONS `--diff-filter`; accessed 2026-11-05; located quote QUOTE-PLACEHOLDER-2 in `corpus/SOURCES.md`); S251 — git-merge-base(1) `--is-ancestor` exit-status contract (r40; `knowledge/git-strict-descendant-relation-r40.md`)
verified-at: 2026-11-05 — S290 opened this round; its located quotes are pending the scout capture (QUOTE-PLACEHOLDER-1, QUOTE-PLACEHOLDER-2)
recheck: 180d — `MANWIDTH=100 man git-log | grep -n -A8 -- '--diff-filter=\['` after a git release

# The adding commit of a receipt path, not the receipt's content, is what the chronology rule reads

## Claim (F1, sourced in part)

QUALITY Q120 requires a successor claim's controls to be committed strictly before the predicate
freeze. The r60 substance arm (`knowledge/freeze-record-substance-binding.md`) binds the revision a
receipt NAMES (`rev=`, strict ancestor of the freeze). It does not read when the receipt FILE first
entered history. The r60 critic (`census/round-60/wave/w1/S60CriticRound/S60CriticRound.md`, Finding 1)
found the control receipts added by the freeze commit itself, while the frozen preregistration said
they were committed earlier. No r60 arm refused that.

The round-61 rule, per preregistration claim:

    git log --diff-filter=A --no-renames --full-history --format=%H -- <control-receipt-path>

Refuse with `CONTROL-ADDED-NOT-BEFORE-FREEZE` unless the result is a full-40-hex commit, distinct from
the freeze commit, and `git merge-base --is-ancestor <add> <freeze>` exits 0.

- `--diff-filter=A` selects only paths that are Added (S290), so the query names the commit that
  created the path, not every commit that touched it. The base helper `freeze_rev` in
  `tools/souji-freeze-check.py` already uses this flag set (observed at base c7228424c3919ecf142bab1aec8181722d86467b).
- `--no-renames`: [INFERENCE] its manual wording is outside S290's captured scope; the L1 confirms it.
- A path added, removed and re-added returns several commits; the base helper takes the oldest.
  [INFERENCE] the frozen rule must name the add it reads, or a re-added path cannot be audited.

## What the binding still cannot prove

- **Ancestry is not wall-clock time.** `--is-ancestor` (S251) is a graph relation. A receipt file
  committed early and filled with a control run late passes. The rule shows when the FILE entered
  history, not when the control RAN.
- **Only the first add is read.** A later rewrite of the receipt is not checked here; its content at
  the freeze is the r60 arm's job (digest, `rev=`, command).
- **Commit timestamps are not read.** Identity and ancestry only; a committer date is not evidence of order.
- **A truthful forgery passes.** A receipt with a real ancestor revision, the real counter digest and an
  early add is accepted. This raises the cost of a late control; it is not an authenticity proof.

## Decision rule

A Control receipt is chronologically bound when its path has an adding commit that is a full-40 commit
and a strict ancestor of the freeze commit. Otherwise the arm reports `CONTROL-ADDED-NOT-BEFORE-FREEZE`.
Bound is still not authenticity; a bound red result is evidence only of the named counter at the named revision.

## Round evidence

- `census/round-61/` — the frozen 10-case chronology matrix (eight r60 shapes with pinned finding classes,
  an orphan-commit non-ancestor case, two new chronology forgeries, one chrono-ancestor positive control)
  and the real-record arm on `census/round-60/preregistration.txt` at `d05a00019835dee5b9bb8fe738add080434c4d67`.
- No measured result is stated here; the result is whatever the landed `census/round-61/` bytes show when
  the L1 re-runs the arm.
