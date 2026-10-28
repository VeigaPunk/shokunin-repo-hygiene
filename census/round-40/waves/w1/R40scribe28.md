# R40scribe28 — calibration attack: receipt-pointer substitution / aliasing

## Verdict

**Bounded measurement plan; no r40 counter or after-data was executed or observed in this seat.** The distinct edge case is *pointer substitution*: a C1 item line carries a syntactically valid receipt/revision pointer, but the pointer resolves to an unrelated receipt (or a receipt at a different path/revision) that does not substantiate the anchored claim. Merely requiring a resolvable, revision-bound pointer is not sufficient unless the counter binds the pointer to the item’s claimed evidence and expected value. This is a falsifiable boundary of C1, not a claim that r40 currently fails it.

## Frozen contract

Read `census/round-40/preregistration.txt` first. Its C1 predicate (line 5) requires evidence pointers on anchored item lines and rejects a register row whose commit is not a strict descendant of `receipt_rev`; it says the forged token-only line remains OPEN. The control is r39, whose counter accepted token-only lines and lacks strict-descendant testing.

## Evidence inspected

- `census/round-39/waves/w1/W1RevC1Forge.md:43-55,114-175,177-208` documents the r39 item arm as same-line anchor/token presence, independent of the register arm; the reported fixture forged evidence-free lines and got `ITEM F6 CLOSED`, `ITEM F10 CLOSED`, `SUMMARY items=2 open=0 ...`, rc 0. It also reports that a repeated/swapped 16-row item table could close all rows.
- `census/round-39/c1-counter.py` at committed revision `2f6e981a105fc759205767d2a749a5f7d4fd0b8a` reads the item table from `open(args.items)`; item evidence is checked by `git_show(root,args.rev,row["file"])` and line-level anchor/token tests. The independent register arm parses `receipt_rev`/`commit` and invokes the reconciler. This confirms the old architecture did not bind an item to a receipt.
- `census/round-39/records/c1-after.txt:1-21` records all 16 rows closed, `open=0`, register `cells=6 mismatches=0 commit_distinct=6`, rc 0. The committed item table and register bytes at that revision were read directly; register rows reference `SCORECARD.md`/`LOG.md` and receipt records, rather than mapping each C1 item id to its own receipt.

## Commands actually run

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2f6e981a105fc759205767d2a749a5f7d4fd0b8a:census/round-39/c1-items.tsv` — exit 0; printed the committed 16-row table.
2. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2f6e981a105fc759205767d2a749a5f7d4fd0b8a:census/round-39/cells.tsv` — exit 0; printed six register rows.
3. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 2f6e981a105fc759205767d2a749a5f7d4fd0b8a:census/round-39/c1-counter.py` — exit 0; printed committed counter source.

No fixture, counter, test, or r40 measurement was run. No tools installed or upgraded. No scratch was created. Only this report was written.

## Bounded falsification procedure for the r40 receipt

Use the r40 counter’s documented interface and scratch convention, without changing the frozen claim:

1. Record exact base/candidate revisions and counter/fixture hashes from the r40 receipt; verify the receipt names both revisions.
2. Run the pristine candidate and frozen base with explicit, existing scratch directories. Confirm candidate closes all legitimate rows and base behaves per its control.
3. Construct two single-defect item-line variants in an isolated fixture: (a) token-only line without pointer, and (b) anchored line with a resolvable pointer to an unrelated receipt/revision whose content lacks the row’s expected claim. Keep the pointer syntactically valid and reachable; vary no other bytes. Run each against candidate and base.
4. Inspect whether (a) remains OPEN as promised and whether (b) is rejected specifically because the evidence does not substantiate that item, rather than merely because the pointer fails to resolve. Also check equal and ancestor commit cases against the strict-descendant rule.
5. Preserve exact stdout/stderr/exit statuses and hashes; report an open result for any unrun case. A candidate that accepts (b) falsifies evidence-binding completeness, even if the token-only case remains open.

This plan is deliberately limited to pointer-to-claim binding. It does not assert the pointer-substitution case is included in the preregistered acceptance set, nor does it treat r39 findings as execution evidence for r40.

## Out of scope / limitations

No r40 candidate counter, receipt, fixture, or after-data was available among inspected artifacts, and this seat did not execute r39 probes anew. Thus there is no observed r40 pass/fail verdict. No production files, frozen claims, git/jj state, or sibling-owned files were changed.