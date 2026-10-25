# W2C2Calib — souji r24 w2 (FALSIFY): is C2's coverage map a calibration surface?

## Status
STATUS: PASS — attack complete. Ruling: **survives-narrow.** The coverage map counts as a self-assessment surface under fleet closure practice, so C2 is on the calibration axis. But C2's counter reads only the map's index column, never the status column where the map's coverage claims and gaps are written. Four miscalibrated maps all score `mismatches=0`. The lane's own pinned SCORECARD instrument stays at `mismatches=2` before and after r24. C2 is acceptable as the lowest-axis claim only if it is worded as entries-column agreement over grounded entries. Any wider wording is overreach.

## Evidence
Lane revisions: base `a65fac98964b445758e94c805728c9a19d302ff8`, after-state `778747eb671f8e85ef5387bc3d7023337b30467c`, master tip `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`. All runs used `python3 -B`, read-only against the lane. Scratch was `/var/tmp/souji-r24-W2C2Calib/` (removed; `test -e` → `removed`). No tools installed.

**Contract texts (opened this run):**
- `/home/vgpnk/Projects/shokunin/scripts/hyaku/lane-addendum.md:220-221` (§9): "A calibration claim must count mismatches between the lane's self-assessment (SCORECARD/SHONEN) and observed repo state."
- `/home/vgpnk/Projects/shokunin/AXES.md:15` (calibration): "Self-assessment quality: gaps named honestly, confidence graded, overreach caught". Signal: "SHONEN.md/SCORECARD entries match observed repo state".
- `/home/vgpnk/Projects/shokunin/CORPUS.md:11`: "README.md — index: what's here, coverage map, known gaps, frontier".
- `/home/vgpnk/Projects/shokunin/LEARNING.md:33` judges expansion against "ground the coverage map did not hold" and requires "each citing its coverage-map row".
- Amendment-1 `:30-31`: "Mapping requires a backticked `knowledge/<name>` span in an entries-column cell (status-column mentions never map)".

**C2 receipts.** `souji-receipt-run.py verify` on each receipt:
- `c2-control-base.tsv` → `verify=ok`, records `grounded=4 mapped=2 dangling=0 mismatches=2`.
- `c2-after.tsv` → `verify=ok`, records `grounded=6 mapped=6 dangling=0 mismatches=0`.
- `c2-fixture-after.tsv` → `verify=ok`, records `cases=9 pass=9 control=FALSE-GREEN-REJECTED`.
- Tool sha256 `71b89eb3…` matches in all of them.

**The §9-named surfaces, untouched by r24:**
- `git diff --quiet a65fac9 c3ca7ad -- SCORECARD.md SHONEN.md` → unchanged.
- `souji-declared-evidence.py --file SCORECARD.md --format counts` (the r22 pinned instrument) at base, after-state and tip → `assertions=82 resolved=80 skipped=69 mismatches=2` at all three, exit 1.
  - TSV at the after-state, row 14: `65817d0d … mismatch:rev-unresolved`.
  - TSV at the after-state, row 23: `git-repo-structure-readonly.md … mismatch:path-absent`.
- On SHONEN.md the same instrument reads `assertions=0` at all three revisions: it extracts nothing from that file.
- `souji-record-agreement.py --no-worktree` → `mismatches=0` at all three revisions.
- `souji-coverage-agreement.py` → base `mismatches=2`, after-state `mismatches=0`, tip `mismatches=0`.

**Mutation replay.** Method: `git archive 778747e` (corpus/README.md, corpus/knowledge, SCORECARD.md) into a scratch repo, using the tool copied from the lane (sha256 prefix `71b89eb3c7ce4179`, equal to the committed blob). Each mutation is one commit off the unchanged copy, scored by the frozen C2 CLI.

| mutation | diff | C2 counts line |
|---|---|---|
| M0 unchanged copy | — | `grounded=6 mapped=6 dangling=0 mismatches=0` |
| M1 overclaim: the r24 F2 row's status becomes "CORE, held: whole-workspace size attribution and fleet size figure measured, no gaps remain" | 1 line | `mismatches=0` |
| M2 understate: the F4 row's status becomes "frontier, no entry, nothing held" | 1 line | `mismatches=0` |
| M3 negation: the r24 F2 status becomes "WITHDRAWN: none of the entries listed here is admitted or verified" | 1 line | `mismatches=0` |
| M4 false SCORECARD coverage number: SCORECARD:23 "F2 holds three entries" becomes "F2 holds nine entries, F2 is core" | 1 line | `mismatches=0` |

**Base content.** `git show a65fac9:corpus/README.md`:
- Line 68's status cell already says "r23: the read side now holds three entries** (`git-repo-structure-readonly.md`, `repo-size-census-readonly.md`, `count-objects-garbage-readings-r25.md`)".
- Line 40 says "frontier, no entry (r12 candidate deferred". The same text is still at the after-state, line 40. The r24 note at line 507 reads "their status prose stays as history".
- The after-state's README line 517 labels the row itself "Coverage-map agreement (calibration of this file; not a ground)".

**Entry counts.** `git ls-tree` → 12 `.md` entries at base, 13 at the after-state. Grounded entries: 4 at base, 6 at the after-state. The two additions are the new `count-objects-linked-worktree-garbage.md` and `git-repo-structure-readonly.md`, which gained a `ground: F2` line. All four entries grounded at base keep the same F<k> at the after-state.

## Findings

1. **For: the map is a self-assessment surface, and §9's parenthetical is not exhaustive in practice.**
   - The map is where the lane names held ground, gaps and frontier (CORPUS.md:11). That is calibration's "gaps named honestly" (AXES:15).
   - Closures judge expansion against the map (LEARNING:33), so mapping an entry to a ground row is a coverage declaration. MISSING-FROM-MAP therefore means held ground that was never declared, i.e. understated coverage.
   - Precedents where the counted surface was not SCORECARD/SHONEN and calibration was admitted `improved`:
     - kaidoku r25, `kaidoku-shokunin/corpus/lessons/round-25-verifier-spotcheck.md:74-96`: items I2 (LOG.md) and I3 (QUALITY.md), verdict "**Verdict: calibration improved.**". That closure also recounted the README coverage map as its cross-check.
     - kengaku r30, `kengaku-shokunin/corpus/lessons/round-30-verifier-spotcheck.md:129`: routed record defects (receipt paths, word counts), the C2 row's verdict cell reads "**improved**" on the calibration axis, with the reason "`defects=5` exit 1 → `checks=5 defects=0` exit 0 with a self-guard".
   - C2's base mismatches are exactly the defect the non-author r23 closure routed. `corpus/lessons/round-23-verifier-spotcheck.md:41`: "Next round should reconcile the current map table with its own “read side now holds three” prose."
   - The control was red at base (`mismatches=2`, receipt verified) and the fixture rejects the always-zero emitter.
2. **Against: the counter is blind to the map's self-assessment content (M1–M4).**
   - Amendment-1 excludes the status column. That column is where the map writes "frontier", "held", "no entry" and "no fleet figure", i.e. the graded-confidence and overreach half of AXES:15.
   - An overclaiming status (M1), an understating one (M2), a negated one (M3) and a false SCORECARD coverage number (M4) all read `mismatches=0`.
   - The stale "F2 … frontier, no entry" at README:40 coexists with four F2 entries and C2 = 0 at the after-state.
   - DANGLING-MAP-PATH, the counter's only overreach class, is 0 at both ends. The whole 2→0 move is understatement repair.
3. **Against: at base, the self-assessment text was already correct.**
   - README:68's status cell named both "missing" entries at base. The 2 mismatches come from the column placement the counter itself defines, not from a false statement.
   - The lane's declared coverage did not change truth value from 2 to 0. What changed is the index layout (an appended r24 table). This is the r22 closure's pattern: `corpus/lessons/round-22-verifier-spotcheck.md:152`, "zero verdict-bearing cells changed, so no scored move — matches the report's own \"bookkeeping-only\"".
   - Fleet precedent for README-map mismatch counters puts them under **quality**, not calibration: revenger r64, `revenger-shokunin/corpus/lessons/round-64-verifier-spotcheck.md:71`, "quality: **improved** — M36 (legend drift) mined with a counter shown failing at base". Revenger's calibration credit that round came from a different claim (`:52`).
4. **Against: a literal-§9 counter existed, was red at base, and r24 left it red.**
   - The lane's pinned SCORECARD instrument reads `mismatches=2` (exit 1) at base, after-state and tip. r24 changes zero SCORECARD/SHONEN bytes.
   - [INFERENCE] Both rows look like instrument-enumeration artifacts on r23-added text: a `tool_sha256` prefix read as a revision, and a bare basename read as a repository path. Even so, a closure applying §9 literally would see the round's lowest-axis claim leave SCORECARD calibration exactly where it was.
   - SCORECARD's own C2-adjacent statement ("F2 holds three entries", SCORECARD:23) is never read by C2 (M4).
5. **Population is a subset that the lane controls.**
   - `mismatches=0` covers 6 of 13 `.md` entries at the after-state. The other 7 carry no `ground:` line and are invisible to MISSING-FROM-MAP.
   - The kill rule prevents un-grounding entries but not leaving new entries ungrounded. This was already flagged as A2 in `.ufo/waves/round-24/w1/ReviewAxesTrend.md`. Not exploited here: both entries added to the grounded set carry `ground: F2`.

## Attack log
- **Counterexample:** four one-line miscalibrations of the coverage map or SCORECARD (M1–M4) keep C2 at `mismatches=0`. The lane's §9-literal SCORECARD instrument reads 2 → 2 → 2 across the round.
- **Impacted axis:** calibration (the claim's wording and whether it scores). No other axis is affected.
- **Fixable defect or tradeoff:**
  - The frozen predicate is legitimate for what it counts: a red-at-base control, a routed defect, and on-axis by kaidoku r25 and kengaku r30 practice. That part is not a defect.
  - Stating C2 as "the coverage map agrees with repo state", or as SCORECARD/SHONEN calibration, would be overreach, and the judge should reject it in that form.
- **Smallest safe correction:** wording and disclosure only. No predicate, target or case-set change.
  1. Word C2 as "coverage-map entries-column agreement for grounded entries: MISSING-FROM-MAP + DANGLING-MAP-PATH 2 → 0; grounded 4 → 6 of 13 `.md` entries".
  2. Name the status-column blindness as a limit, citing M1–M4.
  3. Disclose that SCORECARD/SHONEN are unchanged and that `souji-declared-evidence.py --file SCORECARD.md` reads `mismatches=2` at base and tip. State the two rows and route them, so the result is not read as SCORECARD calibration improving.
  4. Disclose the README:40 "frontier, no entry" status kept at the after-state as residual calibration debt.
  5. Do not claim the calibration score moves 7 → 8. Leave the score and verdict to the non-author closure, expecting `improved` (bounded) at best and a quality/bookkeeping reading (r22, revenger r64) at worst.
  6. Next round: a status-column or SCORECARD-statement predicate (state token vs entry/evidence existence) would make the map's actual self-assessment countable.
