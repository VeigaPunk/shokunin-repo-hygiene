# R42scribe01 — C1 register verification, chunk1 (13 resolved rows)

Scope: verify the 13 `resolved` rows of `.ufo/waves/round-42/w1/inputs/c1-chunk1.tsv` against SCORECARD.md at base `bf618f6c5c09d302994871c94903abbea2deb60d` and the committed `resolved_to` file. Read-only. The register was not edited. No candidate file was written. Nothing was committed.

Base: `bf618f6c5c09d302994871c94903abbea2deb60d`. Freeze: `afe17f416eec04dcf3f480b580a8f928de61d19d`.

## Commands run (all read-only)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show bf618f6c5c09d302994871c94903abbea2deb60d:SCORECARD.md   (saved to scratch, then sed -n 'Np' per row and nearest heading)
git -C <lane> show <base>:<resolved_to>            (per row; grep -n for quoted tokens)
git -C <lane> ls-tree -r --name-only <base>        (same-name candidate enumeration)
git -C <lane> show afe17f4:census/round-42/c1-items.tsv | awk ...   (population result for each row)
python3 (read-only): R2 context = nearest "Round <C>" heading above the SCORECARD line, as in census/round-42/c1-counter.py derive()/context
git -C <lane> show <base>:corpus/knowledge/<f> vs ...census/round-26/waves/assimilation/validate/corpus/knowledge/<f>  (cmp; 4 files IDENTICAL)
```

Chunk parity check: the chunk has 13 rows (`68` appears twice); `c1-register-candidate.tsv` carries the identical `resolved_to` for each of the 13. The `population` rows at `afe17f4` for all 13 are `mismatch:path-absent` (the `68` digest rows are other items on that line and are not in this chunk).

## Per-row table

Key: "ctx" = nearest `Round N` heading above the SCORECARD line (heading line in parentheses). "R#" = rule from c1-counter.py docstring that selects the resolved_to.

| line | token | verdict | evidence |
|---|---|---|---|
| 21 | c1-after.tsv | agree | SCORECARD:21 cell names `census/round-28/records/c1-after.tsv` and `measured at de478b48…`. Resolved file L1 `revision=de478b483db66a8d8ff2d627cde1ccce6e21a014` (matches). L3 `SUMMARY	findings=0	checked_reg=52`. Cell "findings=0, checked_reg=52" matches. ctx=28 (SCORECARD:17), R2 unique. |
| 22 | c2-after.tsv | agree | SCORECARD:22 cell names `census/round-28/records/c2-after.tsv`, `measured at ed270c42…`. Resolved L1 `revision=ed270c42161cd62829783a5e5d2ef4e27089331c`. L2 `SOURCES_rows=139`, L3 `grounded_F4_entries=6 (before=4)`, L4 `coverage_agreement=grounded=13 mapped=13 dangling=0 mismatches=0`, L5 `gate=entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`. All cell numbers match. ctx=28, R2 unique. |
| 23 | c3-after.tsv | agree | SCORECARD:23 cell names `census/round-28/records/c3-after.tsv`, `measured at ed270c42…`. Resolved L1 same revision. L6 `fixture=cases=6 pass=6 control=TAMPER-REJECTED exit=0`; L7 `round26_sha256sum_check=rc0; 1380 OK; WARNING 2 improperly formatted newline-path records`. Cell "cases=6 pass=6 control=TAMPER-REJECTED" and "warns 2 malformed newline-path records (rc 0)" match. ctx=28, R2 unique. |
| 31 | c1-after.tsv | agree | SCORECARD:31 cell names `census/round-27/records/c1-after.tsv`, "after at `6cb22dc2…`". Resolved L1 header `rev gate_sha256 findings checked_reg rc`; L2 `6cb22dc20c9fdb3c7a49eaa1accabca339054c17 02b58f81… 2 52 2` (rev matches; findings=2, rc=2 match the cell "findings=2, rc 2"). ctx=27 (SCORECARD:27), R2 unique. Note: the round-28 file of the same name is a different record; R2 chose round-27 correctly. |
| 50 | w2/RevR3Counter.md | agree | SCORECARD:50 bullet "R3 (dated 2026-10-25) … At base a6d2d15 there were 21 tracked grep candidates, 19 verify=ok and 2 malformed non-receipts; reproduced by W2 report `w2/RevR3Counter.md`". Resolved `.ufo/waves/round-25/w2/RevR3Counter.md` L14 `| a6d2d15 (base) | 21 | 19 | 2× RECEIPT-MALFORMED |`; L8 `lane base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`. Numbers match. Only tree path ending in `/w2/RevR3Counter.md`; ctx=25 ("### Round 25 append-only corrections", SCORECARD:46). Caveat outside the token: the same W2 report L26 finds the SCORECARD R3 evidence pointer `census/round-25/records/verify-ok-at-base.tsv` dangling; the line-50 cell does not cite that pointer, so this row still agrees. |
| 68 | count-objects-garbage-readings-r25.md | agree | SCORECARD:68 (C2 coverage-map row) names the two entries as "MISSING-FROM-MAP (named only in a status cell)". Resolved `corpus/knowledge/count-objects-garbage-readings-r25.md` L5 `ground: F2 — repository size census (what the two target-language communities say garbage counts…)`. Three same-name paths exist in the tree (`census/round-26/waves/assimilation/validate/corpus/knowledge/…`, `.ufo/waves/round-26/assimilation/validate/corpus/knowledge/…`, and the canonical one). Canonical copy is byte-identical to the round-26 validate copy (cmp IDENTICAL), so the choice does not change content. R2 has no round-24 match; R3 ambiguous (3); R4 selects canonical. Correct. |
| 68 | repo-size-census-readonly.md | agree | Same cell (SCORECARD:68). Resolved `corpus/knowledge/repo-size-census-readonly.md` L6 `ground: F2 — repository size census (the census instruments and the write side effect a write-safety fixture must fence)`. Same 3-path ambiguity, canonical selected by R4; copy IDENTICAL. |
| 71 | git-repo-structure-readonly.md | agree | SCORECARD:71 (r13 recheck row): "`git-repo-structure-readonly.md` verified on git 2.55.0 only, r16 note 'pending recheck'" and "selftest=PASS ids=5/5 on git 2.56.0 (`census/round-24/records/r13-recheck-receipt.tsv`)". Resolved file L2 `first verified 2026-10-20 on Git 2.55.0`; L47 `this entry was verified on 2.55.0 and has not been re-verified on 2.56.0. Treat it as pending recheck`. Receipt `census/round-24/records/r13-recheck-receipt.tsv` L9 `git_version=git version 2.56.0`, L18 `selftest=PASS ids=5/5`. All match. ctx=24; R4 selects canonical; copy IDENTICAL. |
| 103 | git-repo-structure-readonly.md | agree | SCORECARD:103 (C3 F2 read side, round 23): "F2 held one entry (`git-repo-structure-readonly.md`)". Resolved `corpus/knowledge/git-repo-structure-readonly.md` L4 `ground: F2 — repository size census (structure census of refs-rooted reachable objects)`. The entry's F2 ground matches the cell. ctx=23 (SCORECARD:97); R4 selects canonical. |
| 174 | c1-control-stub.tsv | agree | SCORECARD:174 (debris census r24 row) cell: "stub control 4/8 (`c1-control-stub.tsv`)". Only tree path ending `/c1-control-stub.tsv`: `census/round-24/records/c1-control-stub.tsv`. Its L17 `cases=8 pass=4 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`; L6 `rc=1`. Matches. Resolved by R3 (unique), not R2 (ctx=23 is the row's nearest round heading, a different round); the R3 result is nevertheless the correct file. |
| 175 | c2-fixture-after.tsv | agree | SCORECARD:175 (coverage-map agreement r24 row) cell: "`tests/fixtures/r24-coverage-agreement.py` 9/9 (`c2-fixture-after.tsv`)". Only tree path: `census/round-24/records/c2-fixture-after.tsv`; L27 `cases=9 pass=9 control=FALSE-GREEN-REJECTED`. Matches. R3 unique. |
| 220 | git-repo-structure-readonly.md | agree | SCORECARD:220 (r24 bullet): "`git-repo-structure-readonly.md` re-verified on git 2.56.0". Resolved L49 `Re-verification (r24, 2026-10-25): … run unchanged on host Git 2.56.0 … printed selftest=PASS ids=5/5`. Matches. R4. |
| 221 | git-auto-maintenance-prunes-worktrees.md | agree | SCORECARD:221 (r25 planned bullet): "re-verify the two remaining git-2.55.0 entries (`git-auto-maintenance-prunes-worktrees.md`, `git-grace-periods-and-expire-to.md`) on 2.56.0". Resolved L2 `verified-at: 2026-10-19 — host git 2.55.0`; L27 `this entry was verified on 2.55.0 and has not been re-verified on 2.56.0`. The cell describes exactly this entry as still on 2.55.0. R4. |

## Counts

Per-row verdicts for the 13 chunk rows:

agree=13 disagree=0 cannot-tell=0

## Finding that matters (outside this chunk, for L1)

I did not get this from my rows; it came from re-running the R2 context logic over the whole line set while checking my rows. Not a disagreement in chunk1.

- SCORECARD:175 also carries the shorthand `c2-after.tsv (0)` (a second item on that line, in another chunk). The candidate register marks it `unresolved -`. My recomputation: nearest `Round N` heading above line 175 is SCORECARD:97 (`### Round 23 measurements`), so ctx=23. The tree has `c2-after.tsv` only under rounds 24–28 (five paths), so R2 finds no round-23 match, R3 is ambiguous (5), R4 does not apply, and the item falls to `unresolved`. The derivation rule takes the nearest round heading and ignores the row's own `(r24)` label and the sibling path `census/round-24/records/c2-control-base.tsv` in the same cell. The cell's referent is almost certainly `census/round-24/records/c2-after.tsv`, which exists at base. Under the frozen rule this yields a CORRECTION-DE `derived=path-absent` line that would be wrong. The item's population result is `mismatch:path-absent`. I did not run the frozen counter on this item (scoring goes only through score-candidate.sh), so whether it is a real derivation defect is `[INFERENCE]` from the rule text and the base tree.
- The same class of problem: any shorthand on a `## Capabilities` / `## Planned` or other non-round section takes ctx from the most recent `Round N` heading, not from the row's own `(rN)` label. Rows 174 and 175 (`c1-control-stub.tsv`, `c2-fixture-after.tsv`) only resolve because R3 is unique; the same logic would fail for any non-unique token in such a row.

## Verdict

All 13 chunk1 rows agree with the SCORECARD cell and the committed file they resolve to. The derivation rule selected the file the cell names for all 13. The 4 same-name knowledge files and their round-26 validate copies are byte-identical, so the R4 choice of the canonical `corpus/knowledge/` path does not change content. One derivation defect was found outside this chunk (SCORECARD:175 `c2-after.tsv`); it is reported for L1 and was not fixed here (register is frozen).

Scratch dir `/fast/scratch/hyaku/souji-r42/R42scribe01` removed after the report was written.
