
## Seat-reported failures

Appended in round 30 wave 2: the round-30 landing gate reads the committed wave capture at
`census/round-30/waves/`, so these two seat-reported failure lines are carried here before the
round closes. Each entry quotes that report's STATUS paragraph verbatim (bytes as committed at lane tip
`9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`) and marks it open: no `resolved@` receipt exists for either
in `corpus/lessons/round-30.md` or `census/round-30/records/`.

- `census/round-30/waves/w1/SwarmReviewer22.md` line 7 — open: STATUS: PARTIAL — six of the seven audited checks verify clean against committed bytes and my own base re-runs; one ATTACK is filed: C1's accepted-correction rule is gameable via a `cmd=` substitute that never exercises the stated count (empirically reproduced on two rows, rc 0, `k1=0`). A stricter-only amendment is needed before data.

- `census/round-30/waves/w1/SwarmSimplifier35.md` line 4 — open: STATUS: PARTIAL — the rendered plan is dispatchable and six of eight enumerated checks hold (distinct ids/prompts, allowed roles, flash and attack shares, unique deliver paths, scratch prefix, role mix), but two mandated rules fail at five sites: the absolute-path rule (shared context plus three items, one undefined placeholder) and the write-scope rule (two items name lane-relative write targets). Findings 1-5 are the violations; 6-10 are spec defects the L1 should reconcile; the non-violations list closes the remaining checks.
