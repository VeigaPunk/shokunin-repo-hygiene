# SwarmScribe30 — round-29 scorecard/LOG skeleton

## Status

STATUS: PASS — all four skeleton parts drafted from frozen before values and the exact target table shapes; every after value, receipt path that does not yet exist and measured commit is a bracketed placeholder.

## Evidence

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`, branch `master`, HEAD `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (preregistration/controls commit). All commands below run read-only from the fleet cwd with `-C`-style absolute lane paths; no git/jj mutation, no scratch directory created, no tool installed.

1. Frozen contract read: `census/round-29/records/preregistration.txt` lines 5–10 (`C1`, `C2`, `C3` clauses) plus `census/round-29/records/controls.tsv`:
   ```
   C1-do-nothing(base)  c1  SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e
   C2-do-nothing(base)  c2  SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e
   C3-do-nothing(base)  c3  F3_entries=0 rows=139
   ```
2. Claim-freeze revision:
   `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -1 --format='%H %s' -- census/round-29/records/preregistration.txt`
   → `b8cb4b31ce80e2e3314b88e85d40ea9873180804 round-29: freeze claims, counters, controls and start census`
3. Frozen stale statements still sit at their declared lines (phrase search per TSV row, committed file bytes):
   ```
   LOG.md:1758                  phrase=PRESENT line_len=546
   SCORECARD.md:23              phrase=PRESENT line_len=539
   corpus/lessons/round-28.md:22 phrase=PRESENT line_len=638
   corpus/lessons/round-28.md:40 phrase=PRESENT line_len=179
   ```
4. Table shapes and anchors:
   `grep -n '^## Capabilities\|^## Planned\|^## Saturation' SCORECARD.md` → `143:## Capabilities`, `177:## Planned`, `224:## Saturation / stagnation`; last Capabilities row `175` (`coverage-map agreement (r24)`); last Planned bullet `223` (`- **r28 (planned r27):** …`). Round 28 measurements heading `SCORECARD.md:17`, column header `SCORECARD.md:19` (`claim | axis | before | after | counting command | measured commit`), separator `:20`, rows `:22`–`:24`.
   `wc -l LOG.md SCORECARD.md` → `1767 291`; last LOG heading `LOG.md:1752`; file text ends at `LOG.md:1767`.
5. Base capability literal: `grep -n 'cases=6' tests/fixtures/r28-wave-evidence-capture.sh` → `6:` (docstring) and `149:printf 'cases=6 pass=%s control=TAMPER-REJECTED\n' "$pass"`.
6. Round-29 record contents at HEAD: `ls census/round-29/records/` → `axis-check-before.txt census-start.txt controls.tsv frozen-digests.txt preregistration.txt` — no after-receipt exists yet, so none was cited as an existing file.
   `tools/souji-registry-agreement.py` and `census/round-29/c2-counter.py` exist (read for the C1 capability row); `tests/fixtures/r29-registry-agreement.py` does not (`ls` rc 2), so its pointer is bracketed.
7. `git status --porcelain` at start of work → ` M .ufo/waves/round-26/w1/ScribeGateDraft.md` (pre-existing seat edit, not mine; untouched).

## Findings

1. Round 29 measurements table anchors: insert above `SCORECARD.md:17`; six-column layout comes from `SCORECARD.md:19-20`, axis cells in the `axis <score>` style of `SCORECARD.md:22-24`. Skeleton cites `C1`/`C2`/`C3` before cells literally from `controls.tsv` (k1=6 k2=4 mismatches=10; failed=152 uncovered=14 with manifests=3 floor_violations=0; F3_entries=0 rows=139).
2. Capabilities rows anchor after `SCORECARD.md:175` within the table starting at `SCORECARD.md:145`; both rows carry the literal marker `<enters only if the demonstration passes>` in the `first-working round` cell, and the C2 row does not claim a case count above the base six (`tests/fixtures/r28-wave-evidence-capture.sh:149`).
3. LOG appendix point is `LOG.md:1767` (current end of file) with the fixed heading `## 2026-10-25 — Round 29 attempt 1: declared-record agreement, committed-bytes wave evidence, F3 duplicate verdicts`, in the paragraph/bullet style of the Round 28 entry at `LOG.md:1752`.
4. r30 Planned bullet anchor is `SCORECARD.md:223` (last bullet before `SCORECARD.md:224`); it takes the r28 routed defect 3 (`.ufo/waves/` gitignored ⇒ `tools/souji-landing-gate.py` report check permanently rc 2 `COULD-NOT-EVALUATE`; point it at committed `census/round-<N>/waves/`) and names the stale-sweep remainder by committed locations only — `LOG.md:1748`, `LOG.md:1758`, `corpus/lessons/round-28.md:21`, `:22` — because `.ufo/waves/` references would themselves be dangling in a committed file. [INFERENCE] the disagreement verdicts on those four remainder statements are the round-29 sweep's; this seat only confirmed the quoted text exists at those lines.
5. The frozen K2 phrase set is exactly the four TSV rows, and each phrase was found at its declared line, so the skeleton's C1 row can require an appended `R29-CORRECTION` marker without re-pointing any line number.
6. `census/round-29/records/` has no after receipts yet; the skeleton therefore leaves after-cell receipt names bracketed (`<census/round-29/records/c1-after.tsv>` etc.) plus a generic `<stale-sweep receipt>` placeholder, rather than naming files that do not exist.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-scorecard-log-skeleton.md` — parts (1) Round 29 measurements table, (2) two conditional Capabilities rows, (3) LOG entry skeleton, (4) r30 Planned bullet, each with its insertion anchor and filler notes.
- `.ufo/waves/round-29/w1/SwarmScribe30.md` — this report.
