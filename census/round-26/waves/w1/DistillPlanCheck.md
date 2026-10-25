# DistillPlanCheck — round 26 claim-set dedupe against prior rounds (C1 / C2 / C3)

## Status
STATUS: PASS — all three claims are distinct from every prior admitted claim; two of them (C2, C3) restate
previously *routed but unclaimed* items (so they extend, not duplicate), and one prior *recorded figure* that
C2's new row S132 supersedes is mis-scoped (finding 3, an accuracy defect in the round's own lesson/row).

## Evidence

Scope read this run (lane repo `/home/vgpnk/Projects/shokunin/souji-shokunin`, read-only):
`LOG.md` (1741 lines), `corpus/lessons/round-{1..26}*.md`, `corpus/QUALITY.md` (143 lines),
`corpus/SOURCES.md` (rows S001–S132), `corpus/README.md`, `corpus/knowledge/*`, `tools/*`,
`tests/fixtures/*`, `.ufo/waves/round-{22,23,24,25}/preregistration.txt` + wave reports,
`.ufo/waves/round-26/preregistration.txt` + amendments 1–2. Lane HEAD during this seat: `166baa1`
(`round-26: measurements block + r26 planned bullet (SCORECARD), lessons updates, Q59 criterion, R26-M1 mistakes row, wave w1 seat record`).

Searches executed (all against the lane repo, read-only):
- `grep -rn 'scaffold|generation block|template|bookkeeping match' LOG.md corpus/lessons/ corpus/QUALITY.md`
- `grep -rn 'trigger-set|trigger set|auto-maintenance' corpus/lessons/*.md corpus/SOURCES.md corpus/README.md`
- `grep -rn 'Insert the table below directly above|Optional same-landing correction'` (all history + working tree)
- `git log --oneline -S'Insert the table below directly above' -- SCORECARD.md` → `315422b` (r24 landing) introduced the block; `a529c76` (r26 C1) removed it
- `git grep -l '^ground: F1' 0eca7c8 -- corpus/knowledge/ | wc -l` → `0`; at tip → 2 files
- `git show 0eca7c8:corpus/SOURCES.md | grep -c '^| S[0-9]'` → `127`; tip `corpus/SOURCES.md` → `132`
- `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py` → `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0
- `bash census/round-26/c3-counter.sh` → `axis_check_tool=present / claims=3 flags=0 / axis_check_exit=0 / cases=12 pass=12 control=FALSE-GREEN-REJECTED`
- Base literals re-derived at `0eca7c8` (round-26 base): scaffold markers = 2 (`git show 0eca7c8:SCORECARD.md | grep -cE '^(Insert the table below directly above|Optional same-landing correction)'` → 2); headings `### Round (23|24|25) measurements` at lines 17 / 175 / 231.

External (read-only, never written): fleet `scripts/hyaku/lane-addendum.md` (claim-sizing §9), fleet
`templates/round-prompt.md` §2, fleet `AXES.md`; campaign package `/home/vgpnk/Projects/shokuknow/merge/souji/`
(staged `SOURCES.append.md` rows S109–S131, staged `knowledge/corpus/knowledge/git-auto-maintenance-trigger-set{,-r23}.md`),
campaign own-work evidence `lanes/souji/round2/evidence/r23-worktree-census.out`.

## Findings

1. **C1 (SCORECARD scaffold census + integration, calibration) — verdict: NEW claim; it closes a
   previously-*observed but never claimed* defect; no prior claim overlaps it.**
   - Prior SCORECARD-consistency claims are a different predicate family: r22 C1 is the declared-evidence
     audit (`tools/souji-declared-evidence.py`, docstring: "reads a self-assessment file (default SCORECARD.md) at a committed revision and re-derives its machine-checkable assertions"). r23 C1 is record-agreement (`tools/souji-record-agreement.py`), r24 C2 / r25 C1 is coverage-map agreement (`tools/souji-coverage-agreement.py`). None of them counts a leftover generation-template block or checks measurement-heading order, so C1's counter (`census/round-26/c1-counter.sh`: `markers=` + `headings=`) is a new instrument, not a re-run.
   - The normative family C1 mechanizes is QUALITY Q10, which was prose-only until now: "At the closing commit the bookkeeping matches the repo: SCORECARD prose equals its table numbers" (`corpus/QUALITY.md:34`). Q10 was previously "stated, never machine-checked" (r22 lesson M15).
   - The *defect* was already observed twice before r26 and never became a claim or a lesson defect row: r24 wave-2 recorded "The debris-census capability is not admitted in SCORECARD at the tip (`W2Trend` F3)" (`corpus/lessons/round-24.md:295`), and r25 wave 1 filed a full edit plan — "STRUCTURE (precondition): SCORECARD's r24 material was pasted as a draft, not integrated" (`.ufo/waves/round-25/w1/ScoutScorecardLines.md:26`) and "P0 — prerequisite: the r24 block is still a fenced draft" (`.ufo/waves/round-25/w1/scorecard-patch.md:17`). r25 never landed it (the r25 tip still carries the two markers). So C1 **extends** r25's unlanded wave work as the round's first *claim* on it; it is not a duplicate of any admitted round claim.
   - Collateral: the r24 verifier's axis-harm statement is now known to be wrong about the same bytes — "a 60-line addition to the Round 24 measurements block only" (`corpus/lessons/round-24-verifier-spotcheck.md:40`); the committed diff is a fenced *draft* paste (`git show 315422b -- SCORECARD.md` shows three ```markdown fences plus the instruction prose). C1's integration removes that mischaracterization's object but does not append a correction note to the r24 verifier file. Routed to the L1 as a residual, not a counter defect.

2. **C3 (axis-of-surface prereg checker, operability) — verdict: EXTENDS r25 routed defect #1
   (new instrument + new criterion Q59); it does NOT overlap the r25 kill-rule instrument and does NOT
   duplicate Q58.**
   - The r25 "kill-rule instrument" is a different surface entirely: `tools/souji-coverage-agreement.py`
     emits "KILL-RULE          (--base-rev only) entry grounded at base that at rev is not a blob" (`tools/souji-coverage-agreement.py:9`) — it re-derives coverage-map agreement for grounded entries. C3's `tools/souji-axis-check.py` reads only the preregistration MACHINE BLOCK plus the SCORECARD axes table (R1 axis-owned, R2 surface-class↔axis, R3 lowest-axis presence, R4 universal-clause-without-`enumerate:`). No shared input, no shared predicate. (C2's K4 *reuses* that r25 instrument; C3 does not.)
   - Q58's predicate is numeric-literal derivation at the named base — "A preregistered numeric target is derived at the named base revision, not copied from a prior round's different base." (`corpus/QUALITY.md:142`) — while C3's rules never read a numeric literal from the prereg. Same *family* (prereg-time criteria, adjacent rows), distinct predicate: C3 does not extend or re-test Q58, and Q58 does not cover axis attribution.
   - C3 is, however, not new normative ground: it mechanizes an existing fleet rule and an existing routed defect. Fleet §9 already states "Name the axis by the surface the round changes, not by the number it produces" (`scripts/hyaku/lane-addendum.md:295`) and "Use no universal clauses (\"all\", \"complete\", \"every\", \"no harm anywhere\") unless the counting command enumerates the full set" (`:280`); AXES.md already requires a claim on the lowest-scoring non-retired axis. r25's closure asked for exactly this deliverable: "validate the declared axis of each frozen claim against the class of surface being changed *before* freeze" (`corpus/lessons/round-25-verifier-spotcheck.md:71`). Verdict: **extends** routed defect #1; the new lane-level content is the criterion row "For each frozen claim, the declared axis must correspond to the actual class of surface the claim changes" (`corpus/QUALITY.md:143`).
   - Placement defect worth flagging (authorship, not predicate): Q59 landed *inside* the `## Round 25 criteria` block with no `## Round 26 criteria` heading (`corpus/QUALITY.md:137`–`:143`), i.e. a round-26 criterion is attributed to round 25. The wave's own placement note anticipated this: "that alternative attributes the criterion to r25" (`.ufo/waves/round-26/w1/axis-check-docs.md:44`). Routed to the L1 as a fix candidate.

3. **C2 (F1 trigger-set assimilation, coverage) — verdict: EXTENDS the admitted F1 frontier
   (README's own planned next step + the r12 F1 entry's explicitly stated gap); the theme is NOT new,
   and the two admitted entries are the first F1 entries carrying `ground: F1` front matter.**
   - The theme was already scoped and planned before r26: "does `fetch`/`merge`/`rebase` auto-maintenance prune on the fleet's live repos" (`corpus/README.md:46` at base `0eca7c8`), and the admitted r12 F1 entry left the gap open on its own face: "these are call sites only — whether each prunes was not fixture-run" (`corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:25`). The new Entry A (trigger set + per-command opt-out) and Entry B (measured prune for fetch/merge/rebase/pull) close exactly that gap at git 2.56.0. **Extends**, not duplicate.
   - No prior lane lesson adjudicated the staged trigger-set packages. `grep` over `corpus/lessons/round-{23,24,25}.md` finds no `trigger-set` / `Pro Git` / `Atlassian` / language-edition row, so C2's refusal of the staged S119–S121 (zh/ja docs + vendor page) is a **new** refusal decision, consistent with the r26 lesson's Gate.
   - Id handling follows established precedent rather than repeating a mistake: the collision procedure and
     the "document map is the disambiguator" rule were established in r22 — "lane S109–S114 (quarantine theme) versus staged S109–S114 (auto-maintenance theme) — different" (`corpus/lessons/round-22.md:428`) — and again in r24. C2 renumbers staged S109→S128, S110→S129, S111→S130, S123→S131, S131→S132, appends 5 net-new rows (127→132), and lands no duplicate document. New rows, no duplicate rows.
   - **Accuracy defect in the round's own artifacts (finding, not a counter defect):** the r12 census figure that S132 claims to supersede is mis-scoped and mis-dated. r12 measured a fleet-wide population — "22 repositories, 52 worktree registrations, 3 locked, 0 prunable" (`census/round-12/scout-surfaces.md:41`) — and for the fleet repo itself "worktrees=6 locked=0 prunable=0" (`census/round-12/scout-surfaces.md:15`). The campaign census S132 measures only the fleet repo, 5 registrations, 0 locked, and all 4 extra registrations are the campaign's own `/fast/scratch/hyaku/...` worktrees. So (a) for the same repo the count went 6 → 5, not "grew to 5"; (b) the "3 locked" belonged to `game-dev-2d-shokunin`, a different repo, so "the locked count fell to 0" is not a statement about this population; (c) the r26 lesson dates that figure to the wrong round — "The r25 \"0 prunable, 3 locked\" fleet census is history" (`corpus/lessons/round-26.md:32`) — it is the r12 census (`census/round-12/scout-surfaces.md`, cited from `corpus/README.md:46` at base). The same mis-scoped sentence is in the registry row: "so the round-12 \"0 prunable, 3 locked\" figure is stale: the count grew to 5 while the locked count fell to 0" (`corpus/SOURCES.md:153`). Correction candidate for the L1 (append-only, per lane convention): state that S132 is a fleet-repo-only census with 4 campaign scratch registrations, that the r12 fleet-wide figure (52/3/0) is not the same population and was not re-measured, and that r12's fleet-repo row was 6 registrations / 0 locked. This does not change any frozen counter (K1=2, K2 ok=2, K3 rc 0, K4 mismatches=0) — it changes a prose claim about a superseded prior figure, i.e. calibration of the coverage claim's own scope.
   - Neither new entry claims the keep-ref expiry or the fleet-wide exposure numerator; the r26 lesson's residual R-r26-3 and README:46's remaining items still hold that open.

4. **Cross-claim distinctness within round 26: holds.** C1 touches only `SCORECARD.md` (bookkeeping-file,
   calibration); C2 touches only `corpus/knowledge/*`, `corpus/SOURCES.md`, `corpus/README.md` (knowledge-entry
   + registry-append, coverage); C3 touches only `tools/` + `tests/fixtures/` (instrument-acquisition,
   operability). No two claims share a file, a counter, or a surface class. No prior round had three claims
   whose surface classes were this disjoint (r25's C1/C2 overlapped on coverage per its own lesson), so the
   round's own axis-misattribution risk (r25 R25-M1) is not reproduced — the r25 C2 failure mode was exactly
   "two claims on one axis", and r26 does not repeat it.

5. **Dedup verdict summary.**
   - C1 → **new** claim (extends r25 wave-1 observation + QUALITY Q10 family; no prior admitted claim).
   - C2 → **extends** (README F1 planned next step; r12 F1 entry's stated gap; r22/r24 renumber precedent). Registry rows S128–S132 are new; the zh/ja + vendor-page refusal is a new decision.
   - C3 → **extends** r25 routed defect #1 (new instrument `tools/souji-axis-check.py`, new criterion Q59). No overlap with the r25 kill-rule instrument (`souji-coverage-agreement.py`) or with Q58's numeric-literal predicate.
   - Nothing in the r26 claim set is a **duplicate** of any earlier admitted claim. Two residual defects are found and routed (C1: the r24 verifier's mischaracterization is uncorrected; C2: S132/r26-lesson mis-scope the superseded r12 figure; C3: Q59 sits under the Round 25 heading).

## Attack log
- Not an attack item (dedupe scout); findings are overlap/accuracy observations for the L1, none of which changes a frozen counter, a target, or a case set. No lane file other than this report was written; no git/jj mutation; no tool installed; no scratch directory created.
