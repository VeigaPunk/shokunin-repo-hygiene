# SimplPlan — round 26 W1 simplifier sweep (read-only)

## Status

STATUS: PASS — all four redundancy questions resolved against byte-pinned locations
(HEAD `9a6e0f1` — observed `0c92c2e`→`9a6e0f1` while writing, re-measured at close; base
`0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`).
Zero deletions: this seat is read-only and nothing under the fleet root, the lane, or
`/home/vgpnk/Projects/shokuknow` was written, moved or classified. Scratch `/var/tmp/souji-r26-SimplPlan`
was created and removed (verified absent). No tool installs were needed.

## Evidence

| check | command (lane root) | result |
|---|---|---|
| base layout | `git show 0eca7c8:SCORECARD.md \| awk '/^### Round (23\|24\|25) measurements/{printf "%s ", NR} END{print ""}'` | `17 175 231 ` — r25 is LAST, not first |
| tip layout | same awk on working tree | `17 44 78 ` — r25 < r24 < r23 |
| contract prose | `git show 0eca7c8:SCORECARD.md \| sed -n '172p'` | "Insert the table below directly above `### Round 23 measurements` (newest first, matching the file's order)." |
| counters vs receipts | `sha256sum census/round-26/c{1,2,3}-counter.sh` vs `tool_sha256` in `records/c{1,2,3}-after.tsv` | 3/3 match: `c8dbb76c…`, `e3f7a677…`, `fcf954f0…` |
| counter sizes | `wc -l census/round-26/c{1,2,3}-counter.sh` | 10 / 10 / 17 lines |
| C3 tip | `cat census/round-26/records/c3-after.tsv` | `claims=3 flags=0`, `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, `fixture_exit=0` |
| fixture set | `sed -n '117,262p' tests/fixtures/r26-axis-check.py` | 11 named cases + case 12 control arm = frozen list (1)-(12) |
| Q59 | `git grep -c 'Q59' -- corpus/QUALITY.md` | 0 (file is 142 lines, ends at Q58) |
| R26-M1 | `git grep -c 'R26-M1' -- corpus/` ; `grep -c '^## Mistakes' corpus/lessons/round-26.md` | 0 ; 0 |
| SKILL rows | `git grep -c 'axis-check' -- SKILL.md` | 0 |
| C2 receipts | `ls census/round-26/records/` | `c2-k4-after.tsv` + `c2-gate.tsv` absent at `0c92c2e`, landed at `9a6e0f1` |
| wave record | `git ls-tree -r --name-only HEAD .ufo/waves/round-26/w1/ \| wc -l` ; `git status --porcelain .ufo/waves/round-26/w1/ \| wc -l` | 1 tracked ; 83 untracked |
| tool probes (own /var/tmp scratch) | `python3 -B tools/souji-axis-check.py --prereg <probe> --scorecard SCORECARD.md` | universal-without-enumerate → `FLAG C1 R4`; universal-with-enumerate → `flags=0`; r25-C2 replica → `FLAG C1 R2 … allowed only on 'coverage'` |

The tree moved during this sweep (`d6fe8a1` → `0c92c2e` → `9a6e0f1`); the C3 gaps I observed at
`d6fe8a1` (11-case fixture, R4 proxying the `enumerate:` value, absent frozen cases 1/5/6/9) closed
at `c594901`, and C2's `c2-k4-after.tsv`/`c2-gate.tsv` landed at `9a6e0f1`. Everything below is
stated at `9a6e0f1` unless a base revision is named.

## Findings

1. **(a) Three counters vs one — KEEP three.** `census/round-26/c1-counter.sh` (10 lines),
   `c2-counter.sh` (10), `c3-counter.sh` (17) share only `cd "$(dirname "$0")/../.."` and
   `export LC_ALL=C`. Merging is not a size win but a receipt regression: each after-receipt binds
   its own labelled file's `tool_sha256` (`records/c1-after.tsv`, `c2-after.tsv`, `c3-after.tsv`),
   so one file would put three claims behind one hash and one broken arm would strand all three.
   `c3-counter.sh:9-15` already shows the correct aggregation axis is *per claim*, not per round:
   it runs the tool verdict and the 12-case fixture inside the C3 instrument. If r27 wants a
   single entry point it must be a **new** instrument with its own receipts; rewriting a frozen
   counter is out of bounds.
   Note, keep with eyes open: `c2-counter.sh:8` prints `registry_rows`, a second implementation of
   the row count that K3 owns (`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate`).
   Both read 132 today; K3 stays authoritative, the counter line is only its own before/after echo.

2. **(b) SCORECARD surgery — KEEP the move; the contract is the prose, the awk counter restates it.**
   The premise "r25-at-end may already satisfy newest-first" is false at the frozen base:
   `SCORECARD.md:172` at `0eca7c8` defines the rule and 0eca7c8's own heading triple is
   `17 175 231`, i.e. Round 25 last — a violation carried in since the r24 padding landed.
   `corpus/lessons/round-26.md` § Findings records the same reading: "The r25 heading order
   therefore violated the file's own newest-first contract". Minimal-move argument: any
   K2-satisfying layout (prereg `:46-48`, n25 < n24 < n23) needs r25's heading to have the
   smallest line number, and at base it has the largest, so *some* block must move; the landed
   choice relocates only the 24-line r25 block (base 231-254, corrections included) and lets the
   46-line r23 block merely shift. Moving r23+r24 below r25 is strictly larger. No simplification
   exists; do not re-open.
   Residual (no action): the ordering rule lost its prose home in `SCORECARD.md` (tip `grep -n
   'newest' SCORECARD.md` → none). It survives only in `corpus/lessons/round-26.md`; an r27 seat
   adding a round must read the lesson or run `c1-counter.sh` to learn the order.
   Dead weight, not worth a commit: in the r26 EOF note (`SCORECARD.md:250-256`) the
   `r25 base a6d2d15` column equals the `cited` column in all five rows (181/180/92/224/225) —
   five redundant cells; trimming revisions after landing would cost more than it saves.

3. **(c) Q59 vs the C3 tool — KEEP both; they are phases, not synonyms.** The criterion is
   design-time: the frozen prereg itself cites Q58 as the mechanism that caught amendment 1
   ("All base literals below were re-derived at the base revision 0eca7c8 (Q58)"), and Q58's text
   (`corpus/QUALITY.md:142`) is "A preregistered numeric target is derived at the named base
   revision, not copied from a prior round's different base." The tool is freeze-time enforcement
   of the same rule set (R1-R4). The routed defect names the criterion as an artifact
   (prereg `:151`), so Q59 is a deliverable, not a duplicate. Delete neither.
   Concrete second-authority *inside* the tool, candidate for r27 only: `tools/souji-axis-check.py:34`
   hardcodes `OWNED_AXES = ("calibration", "operability", "coverage")` while R3 already derives the
   roster from the SCORECARD `## Axes` table (rows `SCORECARD.md:13-15`) — and `parse_scores`
   filters those rows through the same constant, so the constant is self-confirming. One authority
   could serve R1 and R3. Not this round: the tool bytes and the 12-case fixture are the C3
   evidence and changing them after c3-after would invalidate the frozen claim. Also note the
   `## Axes` slice that `parse_scores` reads runs to the next `^## ` line (`SCORECARD.md:124`), so a
   naive de-hardcoding must first narrow the parse to the table itself.

4. **(d) Deliverables a seat produced that are not landed at `9a6e0f1` — land or explicitly drop:**

   | # | artifact | where the draft is | evidence of absence |
   |---|---|---|---|
   | 4.1 | QUALITY `Q59` row + `## Round 26 criteria` block | `w1/axis-check-docs.md` §(a) | `QUALITY.md` 142 lines, ends `Q58`; `git grep Q59 -- corpus/QUALITY.md` → 0 |
   | 4.2 | `R26-M1` mistakes row | (draft inside `w1/axis-check-docs.md`) | `round-26.md` has no `## Mistakes`; `git grep R26-M1 -- corpus/` → 0; prereg `:227` names R26-M1 |
   | 4.3 | SKILL gate-registry rows for the two instruments | `w1/axis-check-docs.md` §(b) | `git grep axis-check -- SKILL.md` → 0 (r25 precedent: `SKILL.md:223` last row) |
   | 4.4 | the wave record itself | `w1/` | only `w1/swarm-registry.json` is tracked; 83 w1 entries untracked, vs ≈40 tracked files in the r25 w1 precedent |

   Landed since this sweep began (verified present at `9a6e0f1`, no action): `records/c2-k4-after.tsv`
   and `records/c2-gate.tsv` (commit `9a6e0f1`), which satisfies prereg `:142-143`. The
   stale-gate mitigation `w1/ExecScratchMirror.md:124` asked for must still be checked inside that
   receipt (compare landed bytes to `rows_sha256`/`entry_sha256`), not by its mere existence.

   Items 4.1-4.3 are the routed-defect half of C3 and cannot be inferred from a green counter
   (see Attack log A1). Item 4.4 is the close-out evidence the r25 precedent commits.

5. **Evidence copies that must not become authority (keep, do not land twice):**
   `w1/r26-axis-check.py` is byte-identical to the landed fixture (`220eed2e…`, 16,119 B) and
   `w1/souji-axis-check.py` (`0805afff…`, 8,288 B) is a superseded divergent draft of the landed
   `tools/souji-axis-check.py` (`1d1c7f5a…`, 5,740 B). Keeping them is the precedent (r25 w1 commits
   instrument drafts), but they are seat output, not instruments: the receipts and case set bind
   the landed bytes. Same class: `w1/c1-new-scorecard-head.md` (43.3 KB) is a near-copy of
   `SCORECARD.md` (69 diff lines) — the surgery input, not a second scorecard.

6. **Closed during the sweep (recorded so it is not re-opened):** at `d6fe8a1` the fixture was an
   11-case set with R4 applied to the `enumerate:` *value* and no instantiation of frozen cases
   1/5/6/9, and `c3-after.tsv` did not carry a fixture line. At `0c92c2e` the frozen 12-case set is
   implemented (`tests/fixtures/r26-axis-check.py:117-262`, case 12 = always-green stub with the
   r25-C2 discriminator) and R4 scans raw claim text only when `enumerate:` is absent
   (`tools/souji-axis-check.py:125-130`). My probes at the current bytes confirm all three
   behaviours. No finding remains on C3's instrument.

## Attack log

- **A1 — the C3 counter cannot see half of what C3 claims.** Prereg `:151` routes a defect that
  requires "a QUALITY criterion beside Q58 covering axis-of-surface, and a mistakes-table row for
  the misattribution itself", yet C3's ARTIFACTS list only the tool and fixture, and neither K1
  (`claims=3 flags=0`) nor K2 (`cases=12 pass=12 …`) observes QUALITY.md or the lesson. At
  `0c92c2e` both Q59 and R26-M1 are absent while both counters are green: the claim can score
  complete with its routed defect undelivered. Reported as an ATTACK, not a proposed edit — no
  predicate, target, case set or axis changed here, and post-data relaxation is forbidden; the
  remedy (a stricter-only, logged amendment or an explicit scope statement that Q59/R26-M1 are
  r27 work) is the L1's call.
