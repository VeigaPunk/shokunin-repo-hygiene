# SwarmReviewer06 — r34 w2 seat report (AttackG23)

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9c76c7222a8abff027af42e37f0d160d52526bba`;
frozen list `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; lane HEAD at review `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.
Read-only seat; full detail and raw probe outputs in `.ufo/waves/round-34/w2/AttackG23.md`.

## Status

Adversarial falsification of W1's G23 finding: **the finding and its proposed correction are upheld
(reproduced); W1's sibling "unreachable" verdict on G23 is falsified (reproduced); the accepted route
is the unique honest route (no route missed).**

## Evidence

- Frozen item `2b0171e:census/round-34/c1-items.tsv:39`: `G23 / SKILL.md:247 / exit 0 /
  SUMMARY manifests=7 failed=0 uncovered=0 floor_violations=0 / census/round-29/c2-counter.py / {REV} /
  python3 -B census/round-29/c2-counter.py --root . --rev {REV}`.
- Base do-nothing: `census/round-34/records/controls-c1-do-nothing.txt:23` — `ITEM G23 MISMATCH original
  rc=1 … manifests=8 failed=0 uncovered=1 …` (committed summary `records/controls.txt:3`, landed at
  `51acb5f`; record ran against attempt-1 freeze `2b59192…`, whose G23 row is identical).
- SKILL.md byte-identical at base and list revision; rows at base: :245 pre-report-gate,
  :246 registry-agreement, :247 evidence-capture v2, :248 r29-c2-counter → where cell one low (W1 A1 true).
- `git log -S` at base: both row texts (:247 and :248) have exactly one introducer,
  `1dc678500c92164b0b2bea82b934dd03d1dfbf38`; at its parent `b862007…` neither row exists → the
  argv-correction cause W1 chose wrote **both** the where-cell line and the item's own row.
- Value drift impossible: item file `census/round-29/c2-counter.py` has the single commit `b8cb4b31…`
  and is absent at `b8cb4b31^`; true drift commits `d65a5c4…` (92 files) and `af7fd25…` touch no item
  file (`git diff-tree --name-only … -- SKILL.md census/round-29/c2-counter.py` empty).
- No measurement artifact: `census/round-33/waves/manifest.sha256` at base = 89 records, no
  `w1-results` entry; tree contains `census/round-33/waves/w1-results.json` (added `af7fd25`) →
  `uncovered=1` is genuine per the r29 counter's contract (`census/round-29/c2-counter.py:7-10`).
- Q76: no prior correction row binds G23 — no `### Round 34 registry restatements` at base
  (do-nothing `restated=0`); base `R29-CORRECTION` rows (`SCORECARD.md:295-297`) bind the round-29
  claim cell `SCORECARD.md:23`, not this registry row.

## Findings

1. **REPRODUCED — W1's proposed G23 restatement row is valid and engine-accepted.** Independent probe
   commit `9d3fb8730e934a4a7fffd88a8d99e283190f09f4` (parent = lane tip `51acb5f…`, append-only
   SCORECARD.md, W1's row verbatim) with the frozen counter `--only G23`:
   `ITEM G23 AGREE restated rc=1 expect_exit=1 statement is the run's last digit-bearing line …`,
   `SUMMARY items=1 agree=1 mismatches=0 restated=1`, rc 0. Cause/argv/exit/statement/Q76 rules all
   satisfied under the frozen bytes (`c1-counter.py:267-268, 292-300, 311-313`; prereg :48-57, :138-145).
2. **REPRODUCED — the route is unique and honest.** Negative control: same row with cause `b8cb4b31…`
   (wrote the script, not the row) → `BAD-CAUSE(cause did not write the row's line)` (probe
   `98d2129c…`). Only `1dc6785` qualifies, and it authored the item's real row too — unlike G21, no
   foreign-cause bypass. Value-drift and Q76 alternatives are impossible; no rule-conforming route was
   missed and no other exists.
3. **REPRODUCED — W1's executed readings reproduce**: at cause `1dc6785` → `manifests=3 … rc=0`
   (frozen predicate already failed at the row's authoring commit); at `4d9bf02` → `manifests=7 … rc=0`
   (enumeration-time value honest); at base → `manifests=8 uncovered=1 rc=1`.
4. **REPRODUCED — W1's classification report is falsified for G23.**
   `w1/deliver-c1-mismatch-classification.md:53` ("same-value | no | unreachable"), :56 ("0 of the 7
   mismatches has an honest restatement…"), :148-149 (G23 among six unreachable SKILL items) are wrong
   for G23: the report analyzed only the value-drift branch and never tested the argv-correction
   branch. W1 is internally inconsistent; `deliver-c1-G23.md` is the correct deliverable. Per-item
   verdicts for G05/G11/G17a/G17b/G21/G24 are not reopened here.
5. **INFERENCE — the off-by-one `where` cell is harmless for G23's cause binding** because one commit
   authored both lines 247 and 248; the gameable accept is a G21-shaped problem, not a G23 one.

## Attack log

Attacks on W1's finding, all repelled by the frozen bytes (probes executed read-only in
`/fast/scratch/hyaku/souji-r34/AttackG23/SwarmReviewer06/`, now cleaned to 648 KB; plumbing-only probe
commits with throwaway identity; no lane file touched):

- Q76 prior-binding hunt: none exists (grep + do-nothing `restated=0`) — fails.
- Value-drift cause hunt: no qualifying commit (script born at `b8cb4b31`, absent at its parent; drift
  commits touch no item file) — fails.
- Alternate cause (script author `b8cb4b31`): `BAD-CAUSE(cause did not write the row's line)` — fails.
- Statement/exit shortcut (e.g. wildcard `*`): unnecessary; the honest concrete exit 1 + exact last
  digit line passes. Counter's `*`-exit acceptance remains a counter-level hole (W1
  `deliver-c1-attacks.txt`), not used here.
- Measurement-artifact hypothesis: refuted by committed bytes (manifest 89 records vs tree containing
  `w1-results.json`).

Exact reproduction commands and outputs for probes A (AGREE, commit `9d3fb873…`), B (BAD-CAUSE,
commit `98d2129c…`) and C (r29 counter at `1dc6785` and `4d9bf02`) are in
`.ufo/waves/round-34/w2/AttackG23.md` (## Attack log).

## Deliveries

- `.ufo/waves/round-34/w2/AttackG23.md` — full falsification report for target G23.
- `.ufo/waves/round-34/w2/SwarmReviewer06.md` — this seat summary.

Residual risk / gaps: only `--only G23` was run (full-target reachability is other seats' scope); lane
worktree is dirty (`M SKILL.md`, untracked `records/*`) but all probes read committed bytes; no tool
installs; no frozen artifact altered.
