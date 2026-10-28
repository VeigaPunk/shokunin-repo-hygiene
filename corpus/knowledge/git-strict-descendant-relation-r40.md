source: S251 git-merge-base(1) § OPERATION MODES `--is-ancestor` (https://git-scm.com/docs/git-merge-base; installed man page git 2.56.0-1, snapshot census/round-40/sources/git-merge-base.1.txt)
verified-at: 2026-10-28 — git 2.56.0-1 on kernel 7.2.11-arch1-1; read-only (`git merge-base --is-ancestor` only, no write, no history rewrite)
recheck: 365d — re-check the man page's `--is-ancestor` exit-status contract after a git release: `MANWIDTH=100 man git-merge-base | grep -A3 -- '--is-ancestor'`
ground: F1 — git-native housekeeping vs receipts (the receipt-revision ordering a register row's `commit` must have over its `receipt_rev`)

# A register row's `commit` must be a STRICT descendant of its `receipt_rev`

## Claim (F1, sourced)

`git merge-base --is-ancestor A B` exits 0 when A is an ancestor of B, 1 when it is not, and any
other non-zero status signals an error (S251, `§ OPERATION MODES --is-ancestor`, installed man page
git 2.56.0-1 lines 41-43, snapshot `census/round-40/sources/git-merge-base.1.txt`, sha256
`45f91e37e113df8651fb125c93e293bb48d8cc46140e4ac95c553547c9ddb043`).

A commit is an ancestor of **itself** under that predicate — reachability is reflexive — so the
ancestor test alone cannot express "the verifying commit came AFTER the commit that created the
receipt". A register row whose `commit` equals its `receipt_rev` satisfies `--is-ancestor` and is
therefore accepted by any arm that only asks "is the commit an ancestor of the audited revision?".

## What the lane does with it

The round-40 C1 register arm (`census/round-40/c1-counter.py`) therefore requires all three of:

1. `commit` resolves to a commit (`git cat-file -e <commit>^{commit}`),
2. `commit` differs from `receipt_rev` (strictness — S251's reflexive case),
3. `git merge-base --is-ancestor <receipt_rev> <commit>` exits 0 (direction), and
   `git merge-base --is-ancestor <commit> <rev>` exits 0 (the commit is inside the audited history).

A row that fails (2) or (3) is a `REGISTER … BACKWARDS` violation and the counter exits 1. The
counter's own fixture proves the three arms separately:
`tests/fixtures/r40-c1-evidence.py` → `case-register-equal-rejected` and
`case-register-backwards-rejected` (`census/round-40/records/c1-fixture.txt`).

## Limits

- The relation is a property of the commit graph, not of the receipts: it says nothing about whether
  the receipt's CONTENT is the one the row claims. That arm is the citation reconciler's
  (`tools/souji-citation-reconcile.py`), and the r40 counter runs it unchanged.
- The strictness rule is the lane's own; S251 grounds the predicate and the exit statuses, not the
  choice to exclude the equal case. The choice is recorded in
  `census/round-40/preregistration.txt` (C1 predicate) and is falsified by the fixture.
- Only ancestry through the first parent chain is tested; a merge commit's other parent is not
  examined.
