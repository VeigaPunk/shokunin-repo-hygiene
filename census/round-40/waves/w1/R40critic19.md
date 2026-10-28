# R40critic19 — C1 calibration attack

**Distinct edge case: equality of `receipt_rev` and audited `--rev` (non-strict ancestry).**

## Evidence

- `census/round-39/c1-counter.py:155-184,242-259` delegates register validation to the reconciler and accepts its mismatch count of zero; its local `parse_register` only counts literal commit/receipt_rev differences.
- `tools/souji-citation-reconcile.py:204-211` defines ancestry via `git merge-base --is-ancestor`; this predicate is reflexive in Git, so a revision is its own ancestor.
- `tools/souji-citation-reconcile.py:300-320` checks that `receipt_rev` resolves and is an ancestor of audited `args.rev`, rejecting only ancestry status `no`/`error`. There is no inequality/strict-descendant condition in this r39 implementation.
- `census/round-39/c1-items.tsv` is the committed item register; its schema is anchored at lines 1-4 and demonstrates token/anchor item checks rather than revision-bound evidence pointers.

## Counterexample / verdict

The r39 control has no strictness guarantee: a register row with `receipt_rev == --rev` satisfies the implemented ancestry test (assuming the receipt exists and its summary matches). Thus the r39 control cannot establish the frozen r40 strict-descendant property. This is a concrete counterexample to treating r39 ancestry behavior as evidence that r40 enforces strictness; it does **not** falsify an unobserved r40 candidate. Verdict: **bounded attack; r39 control fails the strictness criterion by construction; candidate remains unmeasured**.

## Bounded measurement plan

Against the candidate counter, use an isolated disposable Git fixture with a valid receipt/register, pin `register_rev`, and run two cases: `receipt_rev == audited_rev` and `receipt_rev` a strict ancestor. Require equality to produce a mismatch and strict ancestor to pass. Retain stdout/stderr, exit statuses, fixture HEAD, and exact candidate/base revisions in the receipt. Keep the forged token-only probe separate from the valid all-closed register so the expected OPEN result does not contradict the all-closed count.

## Commands actually run

- `read /home/vgpnk/.omp/agent/RULES.md` — read required tooling rules.
- `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt` — read frozen claims.
- `ls /home/vgpnk/Projects/shokunin/souji-shokunin/ && ls /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/ 2>/dev/null; ls /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/ 2>/dev/null` — listed lane and round artifacts.
- Read `census/round-39/c1-counter.py`, `census/round-39/c1-items.tsv`, `tools/souji-citation-reconcile.py` at the ranges cited above — inspected committed r39 source and register.

No fixture execution or candidate measurement was run. No installs performed.
