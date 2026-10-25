# RevPreregFreeze — freeze ordering verification (round 26)

## Status
STATUS: PASS — freeze clean. Preregistration freeze (12fd90b) and amendment 1 (89e0fce) both precede every claim commit; base→freeze diff on claim surfaces (SCORECARD.md, corpus, tools, tests) is empty; counters re-run at 89e0fce reproduce all declared base literals.

## Evidence
- `git -C <lane> log --format='%h %ad %cd %s' --date=iso-local`:
  - `12fd90b 2026-10-25 10:50:58` preregistration freeze (cd 14:04:30)
  - `89e0fce 2026-10-25 14:04:30` amendment 1 + red-before receipts (cd 14:07:27)
  - `bd6588c 2026-10-25 14:07:27` wave evidence (cd 14:15:40)
  - `965b869 2026-10-25 14:15:40` amendment 2 (cd 14:17:59)
  - `a529c76 14:17:59` C1 integrate · `0833de9 14:19:16` C3 tool · `e0f8dcd 14:29:25` C3 receipts
  Freeze and both amendments are strict ancestors of every claim commit.
- `git -C <lane> diff 0eca7c8 89e0fce -- SCORECARD.md corpus tools tests` → empty (no output). Claim surfaces byte-identical from base through amendment 1.
- `git -C <lane> diff --stat 0eca7c8 89e0fce` → only `.ufo/waves/round-26/(preregistration.txt, preregistration-amendment-1.txt, census-before.txt)` + `census/round-26/{c1,c2,c3-counter.sh, records/c{1,2,3}-before.tsv, records/c2-k4-base.tsv, records/empty-slice, records/empty-verdicts}`. Matches contract scope (prereg + counters + receipts).
- First claim-surface commit after base: `a529c76` (C1) — all three claim commits are post-freeze and post-amendment.
- Amendment 1 content (preregistration-amendment-1.txt, 19 lines): C2 K4 literal corrected grounded=6→7 / kill_tested=6→7, "No seat had scored any claim data at amendment time"; K4 receipt `c2-k4-base.tsv` shows `grounded=7 mapped=7 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`.
- Counters re-run in private clone at 89e0fce (Δvar/tmp/souji-r26-RevPreregFreeze/clone, rev-parse HEAD = 89e0fce…):
  - `bash census/round-26/c1-counter.sh` → `markers=2` `headings=17 175 231` (declared K1=2, K2 triple "17 175 231").
  - `bash census/round-26/c2-counter.sh` → `grounded_f1=0` `registry_rows=127` (declared K1=0, K3 count 127).
  - `bash census/round-26/c3-counter.sh` → `axis_check_tool=absent` rc=0 (declared absent at base).
  - `python3 -B tools/souji-coverage-agreement.py --root . --rev 0eca7c8… --base-rev 0eca7c8…` → `grounded=7 …` rc=0, matches c2-k4-base.tsv.

## Findings
1. Freeze ordering clean — preregistration freeze (12fd90b) is the first round-26 commit after base and precedes all claim work; `git log --first-parent 0eca7c8..89e0fce` lists exactly freeze + amendment 1. [path: .ufo/waves/round-26/preregistration.txt, commit 12fd90b]
2. Claim-surface freeze holds — diff base→89e0fce on SCORECARD.md/corpus/tools/tests empty; first surface change is a529c76 (C1) at 14:17:59. [commit a529c76]
3. Amendment 1 precedes all scored data in the committed DAG (89e0fce → bd6588c wave evidence → 965b869 amendment 2 → a529c76 first claim). Amendment 2 also predates all claim commits. [commit 89e0fce]
4. Base literals reproduce exactly at the frozen rev for all three counters and C2 K4 — no literal mismatch. [evidence above]
5. RESIDUAL RISK — red-before receipts `records/c2-before.tsv` (utc=2026-10-25T17:29:54Z) and `records/c3-before.tsv` (utc=2026-10-25T17:29:28Z) carry run timestamps AFTER the final claim commit `e0f8dcd` (cd 2026-10-25T17:29:25Z); c1-before.tsv reports rev=12fd90b (freeze commit) rather than lane base 0eca7c8 contrary to prereg wording "red, at base". Commit-graph placement is pre-claim, but physical execution of the red-before runs postdates the claim commits — consistent with history rewrite/amending (cd chain: each commit cd = next ad), not with the literal "BEFORE after-data" run order. No claim-surface or literal impact; flag as observation, not contamination.
6. No axis/predicate/case-set changed pre-amendment-2; amendment 1 is stricter-only (literal correction + receipt). [amendment-1.txt lines 5-17]

## Attack log
(none — no counter/predicate/gameability attack identified; amendment 1 is a correct stricter literal fix.)
