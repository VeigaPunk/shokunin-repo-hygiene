# R40critic07 — C1 calibration attack (distinct item 7)

- seat: R40critic07 (critic, leaf, no subagent dispatch); axis: calibration
- lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`; frozen claim: `census/round-40/preregistration.txt` (read first; not altered)
- r40 base: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (prereg base). Chain verified: `git merge-base --is-ancestor 544104503a3ad70687ba399fcafd12bd30648169 0242085…` rc 0 and `2f6e981a105fc759205767d2a749a5f7d4fd0b8a` → `5441045…` rc 0, so the base is a strict descendant of the r39 final tip and audited rev. Provenance intact.
- instrument bytes pinned at base: `census/round-39/c1-counter.py` sha256 prefix `65e42904ea78`, `tools/souji-citation-reconcile.py` `59f1e57d7af0`; `base==worktree: True` for both (diff check in Exp A). All runs read-only on the lane; every write was under `/fast/scratch/hyaku/souji-r40/R40critic07` with `TMPDIR` set to it. Tool installs: none.

## Distinct named failure modes (this item's assignment)

Sibling attacks already filed: receipt_rev == --rev equality (R40critic19), semantically irrelevant pointer (R40critic31), merge/first-parent ancestry semantics (R40critic55). This item names and executes four different ones:

- **FM-1 "receipt-preexisting backwards commit" (source: r39 reconciler commit arm, `tools/souji-citation-reconcile.py:commit_checks`).** The r39 stack catches a backwards commit only *content-dependently*: if the receipt blob first exists AT `receipt_rev`, a commit pointing backwards is masked by `COMMIT-RECEIPT-ABSENT`, not by any ordering rule. Plant the receipt before the backwards commit and nothing in the r39 bytes fires. Demonstrated in Exp B4.
- **FM-2 "resolvable-but-unrelated pointer forgery" (provenance forgery).** A forged item row whose anchored line carries a fully resolvable, revision-bound pointer (real path + real 40-hex rev, both resolvable at base, rev an ancestor of base) that evidences nothing about the item. "Resolvable, revision-bound" as frozen admits it; only provenance binding (pointer must name the item's own round receipt / post-base revision) keeps it OPEN. Demonstrated CLOSED in Exp A.
- **FM-3 "forged-row membership in the counted item set."** The frozen target sentence "reports every item closed … and the forged token-only item remains OPEN" is unsatisfiable in one counted table under the r39 SUMMARY shape (`open` counts every row). The r40 counter must exclude the forged control from `items=/open=` or emit a separate control receipt; the prereg's singular "r40 counter receipt" under-specifies this.
- **FM-4 "equal-commit retroactive invalidation of the r38 register shape."** All 10 committed `census/round-38/cells.tsv` rows carry `commit == receipt_rev` (checked per row). The frozen predicate rejects equal commits (kill: "a backwards/equal commit passes"), so the entire r38 register shape becomes invalid if the r40 counter is ever pointed at it. "Any existing valid row is rejected" must be scoped to the r40 register input, and the r38 shape recorded as superseded semantics.

## Exp A — control arm executed at the r40 base (committed r39 counter bytes over the lane)

Forged items table (scratch `items-forged.tsv`): `FORGE-TOKEN` (LOG.md, anchor `cases=9`, must `fail=6`), `FORGE-TOKEN2` (LOG.md, `cases=9`/`pass=9`), `FORGE-POINTER` (census/round-39/records/c1-after.txt, anchor `c1-counter.py --root`, must `2f6e981a105fc759205767d2a749a5f7d4fd0b8a` — the line is the receipt's own command header carrying path+rev).

```
python3 -B <base c1-counter.py> --root <lane> --rev 0242085… \
  --items <scratch>/items-forged.tsv --register census/round-39/cells.tsv --scratch <scratch tmp>
→ rc 0
ITEM FORGE-TOKEN CLOSED
ITEM FORGE-TOKEN2 CLOSED
ITEM FORGE-POINTER CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY items=3 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=c271c94028b3
```

Verdict: the frozen control clause "r39 counter accepts a token-only forged line" is **verified by execution**, and FM-2 shows a pointer-carrying forgery closes under the same bytes — the r40 forged-control set must include a provenance-forgery row, else "the forged token-only item remains OPEN" is a weak single control. `python3 -B tools/souji-citation-reconcile.py --root <lane> --rev 0242085… --register census/round-39/cells.tsv --register-rev 0242085…` → rc 0, `SUMMARY cells=6 mismatches=0` (committed register clean at base).

## Exp B — equal + backwards commit rows vs the committed r39 counter (scratch git fixture)

Fixture `/fast/scratch/hyaku/souji-r40/R40critic07/expB-fixture.67y6re1t` (mktemp under seat TMPDIR; every git call `-C` the fixture root; `rev-parse --show-toplevel` asserted equal before commits). DAG: C0 commits the base reconciler bytes at `tools/souji-citation-reconcile.py` **and the receipt `rec.txt` (`SUMMARY cases=3 pass=3`) — planted before any register activity (FM-1's load-bearing detail)**; C1 adds the citation line naming both measured commits; C2 "updates" the receipt; C4 commits `cells.tsv` with `ROW-EQ` (commit == receipt_rev == C1) and `ROW-BACK` (commit = C0, the **parent** of its receipt_rev C2); C6 is the audited rev.

```
python3 -B <base c1-counter.py> --root <fixture> --rev C6 --items <scratch>/items-fixture.tsv \
  --register cells.tsv --scratch <scratch tmp>
→ rc 1 (only because cells=2 < default --min-cells 6)
ITEM FORGE-TOK CLOSED
REGISTER cells=2 mismatches=0 commit_distinct=1
SUMMARY items=1 open=0 register_cells=2 register_mismatches=0 commit_distinct=1 items_sha=746156fbb248
```

`git merge-base --is-ancestor C0 C2` rc 0 (backwards relation present), `C2 C0` rc 1. Verdict: **equal and backwards register rows both pass the r39 stack with `mismatches=0`** — "has no strict-descendant test; it cannot reach the predicate" verified by execution, and FM-1 established: the receipt must be planted before the backwards commit or the r40 kill fixture passes vacuously through `COMMIT-RECEIPT-ABSENT` instead of through the new rule.

## Committed-data compatibility of the frozen strict-descendant predicate (kill clause "any existing valid row is rejected")

Per row of `census/round-39/cells.tsv` (commands: `git merge-base --is-ancestor <receipt_rev> <commit>`; equality by string compare; commit→base ancestry likewise):

| row | receipt_rev | commit | strict_descendant | equal | commit ancestor of base |
|---|---|---|---|---|---|
| REG-07/08/09/10/11 | `5230a341…` ×5 | `a8e6d75b…` | true | false | true |
| REG-12 | `f8ba3f3b…` | `a8e6d75b…` | true | false | true |

All 6 rows satisfy the frozen predicate; implementing it rejects no existing valid r39 row. Falsifier **does not fire** on committed r39 data. Boundary (FM-4): the same commands over `census/round-38/cells.tsv` give 10/10 `equal` rows — out of the r40 counter's input scope, but the r40 measurement command must name its register explicitly.

## Falsifier outcome and bounded measurement plan for the r40 counter

No kill fired on committed artifacts. Remaining falsifiable surface is the unbuilt candidate; bounded plan (all runnable at base + after, scratch-only):

1. Control receipt (r39 bytes, forged rows included): token-only row must read CLOSED (as Exp A) — the frozen control as written.
2. Add the FM-2 provenance-forgery row to the same control: under a resolvability-only pointer grammar it closes (defect); a provenance-bound grammar (pointer must name the round-40 receipt path and a rev that is not an ancestor of base) keeps it OPEN.
3. Kill fixture per Exp B4 shape: receipt planted at/below the backwards commit; equal row and backwards row must each produce a register mismatch under the r40 counter while the r39 counter prints `mismatches=0` (regression arm committed).
4. FM-3: the all-closed target and the forged-OPEN control must be two receipts (or the forged row excluded from `items=/open=`); the prereg's single-receipt wording cannot express both in one SUMMARY.
5. Pin `--min-cells`/`--min-commit-distinct` in the receipt command (Exp B4's rc 1 was floor noise; Exp A's rc 0 rode unpinned defaults) and name the register path (FM-4).

## Verdict

**Bounded attack, no falsifier on committed data; control arm and committed-row compatibility both verified by execution; four named claim gaps (FM-1..FM-4) handed to the candidate with exact fixtures.** The frozen C1 claim survives contact with every r39 artifact I could run it against; its residual exposure is in control-set completeness and measurement wording, not in the predicate itself.

Scratch `/fast/scratch/hyaku/souji-r40/R40critic07` removed after capture. No lane byte outside this report was written; no frozen claim altered; no installs.
