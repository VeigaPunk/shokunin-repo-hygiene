# CritNoHarm — r26 w1 attack: "no axis is harmed" + fence byte-identity

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`. Reviewed at lane HEAD `166baa18f808071bc385187691713044a26bd663`
(SCORECARD.md 271 lines); lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; frozen prereg
`89e0fceeefcf28db313c94120be6d25e03c60094` + amendments 1–2. Read-only seat; no lane writes besides this file.

## Status

STATUS: PARTIAL — the r24 fence→section surgery loses **no payload** and C2/C3 reproduce their frozen
counters, but **"no axis is harmed" fails on calibration**: the same round appends Round 26 measurements
below Round 23 (`SCORECARD.md:264`), so the measurement sections are ordered 25, 24, 23, 26 — neither
newest-first (the ordering C1's K2 enforces) nor oldest-first (the file's observed history) — and the
frozen K2 cannot see it. Two further calibration defects (stale post-C1 mapping column; `c1-after` bound
to a pre-tip rev) and one coverage defect (incomplete `used-by`). Operability itself is not harmed.

## Evidence

All commands run from the lane root unless a path is absolute.

**C1 counters at reviewed HEAD** (`166baa1`):

```
$ bash census/round-26/c1-counter.sh
markers=0
headings=17 44 78
$ git show 166baa1:SCORECARD.md | grep -n '^### Round'
17:### Round 25 measurements (2026-10-25; base a6d2d157…)
27:### Round 25 append-only corrections
44:### Round 24 measurements (2026-10-25, lane base a65fac98…)
78:### Round 23 measurements (2026-10-25, lane base 1208bfb4…)
239:### Round 26 append-only corrections
264:### Round 26 measurements (2026-10-25; lane base 89e0fcee…)
```

**Fence payload vs landing** (`0eca7c8` lines 173–228 → `166baa1`). 45 non-blank fenced lines; 12 absent
at tip, all of them fence markers or instruction/meta text; exact-span matches at tip:

```
S1 base 1-16      -> 1      S3 base 175-207 (r24 table) -> 44
S2 base 231-254   -> 17     S4 base 17-62              -> 78
S5 base 63-91     -> 124    base 213-214 (2 cap rows)  -> immediately after record-agreement row (154)
S6 base 95-136    -> 158    base 225-226 (2 bullets)   -> 201-202
S7 base 138-169   -> 204
```

**Fence vs independent canonical:** `diff <(sed -n '174,206p' a6d2d15:SCORECARD.md) <(sed -n '175,207p' 0eca7c8:SCORECARD.md)`
→ empty (`IDENTICAL-TABLE`); same for tip 44–76. But the fence is the *only* committed r24 table: at the
r24 measured rev `778747e` the file has **one** measurement heading (`23@17`), and the scaffold first
appears in `315422b` ("round-24: final — post-wave-2 repairs"), already fenced.

**r24 row vs its receipt** (fence table, spot check of every claim row):

```
census/round-24/records/c1-after.tsv  cases=8 pass=8 control=FALSE-GREEN-REJECTED …   (rev 778747e)
census/round-24/records/c2-after.tsv  grounded=6 mapped=6 dangling=0 mismatches=0     (rev 778747e)
census/round-24/records/c3-after.tsv  cases=8 pass=8 refusals=2/2 regress=5/5          (rev 778747e)
census/round-24/records/r13-recheck-receipt.tsv  selftest=PASS ids=5/5                (rev 778747e)
$ git cat-file -e a65fac9:tests/fixtures/r24-size-census.py   # fails, as the row states
```

**C2 counters at HEAD:** `git grep -l '^ground: F1' HEAD -- corpus/knowledge/ | wc -l` → `2`;
`python3 -B tools/souji-gate-check.py … ` → `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0`, rc 0;
`bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ rc 0, `ok …/corpus/SOURCES.md`, 132 `S` rows; `python3 -B tools/souji-coverage-agreement.py --root . --rev 166baa1 --base-rev 0eca7c8a…`
→ `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc 0. S128–S132 rows:
12 `|` each (11 columns, no literal/escaped pipe). Own-work digests match: `sha256sum evidence/r23-worktree-census.out`
→ `1ac71c4f…`, `fixtures/r23-trigger-prune.sh` → `11c136aa…`.

**C3:** `python3 -B tools/souji-axis-check.py --prereg .ufo/waves/round-26/preregistration.txt --scorecard SCORECARD.md`
→ `claims=3 flags=0`, rc 0; `python3 -B tests/fixtures/r26-axis-check.py --tool tools/souji-axis-check.py`
→ `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0. Receipt revs: `c3-after.tsv` rev `c594901`
(c3 artifacts byte-identical `c594901`…`166baa1`); `c1-before` rev `12fd90bc`, `c1-after` rev `07f83e6`,
`c2-after` rev `e0f8dcd`, `c2-gate`/`c2-k4-after` rev `33e6807`.

No tool was installed or upgraded for this seat. Scratch `/var/tmp/souji-r26-CritNoHarm` removed.

## Findings

1. **Fence loses no payload** (`SCORECARD.md` base 173–228 vs tip). Every payload fragment landed verbatim
   at the exact spans listed above: r24 table (base 175–207) at tip 44, both capability rows (base 213–214)
   immediately after the `record agreement audit (r23)` row, both planned bullets (base 225–226) at 201–202.
   The 12 absent lines are fence markers and the three instruction paragraphs — meta, not measurement.
   Removing the fence therefore loses **nothing** measurable versus keeping it.

2. **The fence's own instruction was defective and was not followed literally — correctly.** Base 172 reads:
   "Insert the table below directly above `### Round 23 measurements` (newest first, matching the file's order)."
   Applied to the base, Round 25 stays last (`17 50 204`, per `w1/c1-verify.md` §c) and the frozen K2 fails;
   amendment 2 authorizes the reorder actually performed. Verdict: the fence could not have been trusted as
   a recipe, only as a payload.

3. **The fenced r24 copy carries two known defects, both disclosed; one is still live and wrong.**
   `SCORECARD.md:51` (assimilation row) says "slice 7 accepted + 1 unverifiable (S118)", while
   `census/round-24/records/slice-verdicts.tsv` has eight `accepted` rows and `S118` is `accepted`. The
   superseded-by line at `SCORECARD.md:36` names exactly this row and the authoritative count (`8 accepted`);
   the mapped target `:51` resolves. `SCORECARD.md:50` (r24 C3 title "receipt verify/run symmetry") is the
   second disclosed overclaim, pointer `:37` → `:50`, resolves. So the defects are **not silent**; the
   information-loss risk is in the pointers, not the payload.

4. **CALIBRATION HARM — the round re-breaks the layout contract C1 fixed, and K2 is blind to it.**
   `SCORECARD.md:264` adds `### Round 26 measurements` below Round 23 (`:78`); the corrections note (`:239`)
   is likewise below Round 23. Heading order is 17(R25), 44(R24), 78(R23), 264(R26): neither newest-first
   (what C1's K2 enforces for 23/24/25 and what the claim calls "the file's own contract") nor oldest-first
   (what every prior revision actually had: `315422b`/`a6d2d15`/`728b2ce` appended newer rounds below;
   `778747e` had `23@17` only). `census/round-26/c1-counter.sh` matches only `Round (23|24|25)`, so it prints
   `17 44 78` and scores conformant at a tip whose newest measurements are last. The C1 claim's normative
   assertion is false at the landing tip even though its counter is green.

5. **Stale mapping column.** `SCORECARD.md:250-256` maps `SCORECARD.md:224`→`199` and `:225`→`200` under the
   header "post-C1 = `a529c76`". At the reviewed tip the two planned bullets are at **201/202**, because
   `07f83e6` inserted the two capability rows (28 insertions, before `## Planned`) after `d6fe8a1` wrote the
   note. Three of five cells (`51`, `50`, `153`) still resolve; the last two do not. The class of defect is
   the same one C1 exists to remove.

6. **`c1-after` does not bind the landing tip.** Receipt `census/round-26/records/c1-after.tsv` has
   `rev=07f83e6…`, but SCORECARD.md changed afterwards at `166baa1` (+10 lines). The frozen claim says the
   after value is "run at the landing tip in a clean tree"; the counter's output still reproduces at the tip
   (`markers=0`, `headings=17 44 78`), but the receipt binds an earlier tree.

7. **`c1-before` rev ≠ frozen rev.** Frozen red-before names `--rev 0eca7c8a…`; receipt rev is `12fd90bc…`
   (the prereg-freeze commit). `SCORECARD.md` blob is `4b564bc6…` at `0eca7c8`, `12fd90bc` and `89e0fce`, so
   the measured bytes are identical and the value is unaffected — but the frozen argv was not the one run.

8. **COVERAGE — `used-by` is not "exactly the admitted entries citing it" for S131.**
   `corpus/SOURCES.md` S131 `used-by` names only `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md`,
   yet `corpus/knowledge/git-auto-maintenance-trigger-set.md:45` cites it: "closed by the sibling entry …
   (S131), not here." The census validator checks that named paths exist, not completeness, so K3 stays green.

9. **OPERABILITY/overclaim — R4 never sees a real claim's text.** `tools/souji-axis-check.py` parses only the
   `## MACHINE BLOCK … END` span; `raw[cid]` therefore contains just the `axis:`/`surface-class:`/`enumerate:`
   lines. Probe: a prereg whose claim prose (outside the block) says "covers all entries and every case" and
   whose block has no `enumerate:` → **no R4 flag**; the same universal word *inside* the block → R4 fires.
   Fixture case 8 ("`text: every bookkeeping counter is complete`") tests a key real preregs never contain.
   This round's own three claim texts are all outside the block, so `claims=3 flags=0` carries **zero** R4
   evidence.

10. **R2 silently neutralizes unknown surface-class values.** `SURFACE_AXIS` is consulted only for exact
    membership; `NEUTRAL_SURFACES = {"receipt-binding", "measurement"}` is defined and never used. Probe:
    C3 mutated to `surface-class: bookkeeping` on `operability` → `claims=3 flags=0`, rc 0. A typo or a new
    class name bypasses R2 while R1/R3 stay satisfied.

11. **Round 26 table "measured commit" cells are inconsistent.** C1 names the receipt's rev (`07f83e6`);
    C2 names `9a6e0f1` and C3 names `0c92c2e`, which are the commits that *landed the receipts* (their
    receipts measure `e0f8dcd`/`33e6807` and `c594901`). One column, two meanings.

## Attack log

| # | claim / axis | counterexample tried | result | smallest safe correction |
|---|---|---|---|---|
| A-1 | C1 / calibration | count every `### Round <n> measurements` heading at the landing tip, not just 23–25 | order 25,24,23,**26** — Round 26 below Round 23; K2 still green | move the Round 26 block (`SCORECARD.md:262-271`) above Round 25, re-derive K2 (becomes `27 54 88`, still ordered) and refresh the C1 row's heading quote; this is new bytes, not a protected span |
| A-2 | C1 / calibration | resolve the five mapped cells at the tip instead of at `a529c76` | `:224→199` and `:225→200` land on the r25 bullet and a blank; content is at 201/202 | append one dated line to `## Round 26 append-only corrections` giving landing-tip targets (or re-derive after A-1 is applied) |
| A-3 | C1 / calibration | run the frozen green-after at the tip the claim names | receipt `rev=07f83e6`, tip `166baa1` changed SCORECARD.md | regenerate `c1-after.tsv` at the landing tip after A-1; values unchanged |
| A-4 | C1 counter design (ATTACK, not a re-score) | K2's ordering predicate as a permanent guard | the predicate is a three-round window; any round can append below and it stays 0-flag — this round did | record as residual: next round's prereg must scope K2 to `^### Round [0-9]+ measurements$` and require the monotone order over **all** headings; no change allowed now (predicate frozen, data scored) |
| A-5 | C2 / coverage | recompute `used-by` from every citing entry | S131 omits `git-auto-maintenance-trigger-set.md`, which cites it at :45 | add that path to S131's `used-by` cell (or drop the row-id from entry A:45) and re-run K3 |
| A-6 | C3 / operability (indirect calibration) | put a universal clause in real claim prose; keep `enumerate:` absent | no R4 flag — R4 only reads the machine block; fixture case 8 proves a shape no real prereg has | either widen the parser to the `CLAIM Cn —` prose blocks or state in the tool docstring + Q59 text that R4 is machine-block-only; add a 13th case with prose-only universal text |
| A-7 | C3 / operability | declare an unknown surface-class on an owned axis | `bookkeeping`/operability → 0 flags; `NEUTRAL_SURFACES` dead | flag any `surface-class` not in `SURFACE_AXIS ∪ NEUTRAL_SURFACES` (unknown ⇒ finding) and delete the dead constant |
| A-8 | C1 / calibration | read the r26 table's "measured commit" column | three cells, two meanings | use the receipt `rev=` for all three cells, or add a "receipt-landing commit" column |

**Answers to the posed questions.** *Does moving the table out of the fence lose information?* No — all
payload bytes land, byte-identical, in the required order; only fence/meta text is dropped (F1). *Is the
fenced copy byte-identical to a correct r24 table?* Unprovable from provenance: it is the only copy ever
committed (`315422b`, already fenced; `778747e` has no r24 heading). It is byte-identical to the r25-base
copy (`a6d2d15` 174–206) and receipt-consistent on four rows plus the r13 row, with the fifth row carrying
the disclosed slice-count defect (F3). So the L1 may propagate the payload **only together with** the
`superseded by SCORECARD.md:51` / `:50` pointers — which is what landed, except that A-2's two pointers do
not resolve at the tip.

**Axis verdicts.** calibration: harmed by A-1 (and A-2/A-3/A-8 are the same class at smaller scale).
coverage: not harmed; A-5 is an accuracy defect, not a coverage loss. operability: not harmed (tool runs,
12/12, stub rejected); A-6/A-7 are false negatives that let the instrument bless future bad claims, so
they harm the *protection* the instrument advertises, not the axis it declares.
