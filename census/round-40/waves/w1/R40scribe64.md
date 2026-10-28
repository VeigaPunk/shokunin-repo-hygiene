# R40scribe64 — independent C1 calibration claim attack

- Seat: scribe, leaf member; no subagent dispatch.
- Frozen source read first: `census/round-40/preregistration.txt`, C1 at lines 4–5.
- Distinct edge case: **a valid revision-bound receipt can still be unrelated to the anchored correction line / item** (receipt-to-item binding gap). This is separate from token-only forgery and strict-descendant ancestry.
- No lane writes other than this assigned report; no scratch, fixture, tool install, or git/jj mutation used.

## Evidence and commands

Commands actually run (all read-only file inspection through the repository reader; no shell commands were run):

1. Read `/home/vgpnk/.omp/agent/RULES.md`.
2. Read `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt`.
3. Read `census/round-39/c1-counter.py` lines 86–184 and 187–259.
4. Read `census/round-39/c1-items.tsv`.
5. Read `census/round-39/records/c1-before.txt`.
6. Read `census/round-39/waves/w1/W1RevC1Forge.md` lines 1–300.

Evidence pointers:

- Frozen C1 contract: `census/round-40/preregistration.txt:4-5`; requires resolvable revision-bound evidence pointers per anchored item line plus strict-descendant `commit` vs `receipt_rev`; token-only line must stay open.
- r39 item predicate: `census/round-39/c1-counter.py:218-240`; obtains hits by anchor containment and closes if a single hit line contains `must` tokens and no `mustnot`; no item/receipt association is consulted in this predicate.
- r39 register operation is disjoint: `census/round-39/c1-counter.py:155-184,241-248`; it reconciles a register independently, then reports counts, without joining register rows to item identifiers/anchors.
- Historical concrete control: `census/round-39/waves/w1/W1RevC1Forge.md:114-175` describes the bare-line fixture forgery; `:177-208` documents row-set substitution; `:275-290` records the honest limit and the missing item-level receipt/commit arm. This corroborates that the distinct relationship gap is a known mechanism, not evidence that r40 retains it.
- r39 baseline receipt: `census/round-39/records/c1-before.txt:1-21`, with all 16 open and rc=1; does not exercise receipt-to-item binding.

## Verdict

**BOUNDED / NOT MEASURED against r40 candidate.** The r39 committed implementation provides a concrete falsifiable failure mode for the C1 design: even if a candidate validates that a referenced receipt resolves at a revision and that its commit is a strict descendant of `receipt_rev`, an item can remain falsely closed unless the referenced receipt is bound to that specific item/line (e.g. item identity or expected anchored evidence is verified in the receipt). In r39, the item closure and register reconciliation are separate arms, so register validity cannot establish that relationship.

This is a design-level attack plan, not an observed r40 failure: the candidate counter, r40 receipt, and its actual evidence schema were not read or executed here. No claim is made that the frozen predicate itself requires a specific receipt-to-item schema beyond its stated per-line resolvable revision-bound pointer. To falsify the candidate, construct two items with valid, resolvable receipts and strict-descendant commits, then swap their receipt references while preserving each item line's token text; require both to remain open or report a mismatch. Also test a receipt that resolves but lacks the item's anchor/identity. The r39 material does not establish whether r40 rejects these cases.

No checks, tests, or counters were run; none should be read as passed. No installs or upgrades.
