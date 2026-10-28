# R40simplifier46 — C1 calibration attack

## Distinct edge case: independent `--register-rev` permits a receipt/register provenance split

**Verdict: bounded measurement plan; r39 is a valid negative control, not evidence that the new ancestry predicate is sound.** The specific edge is an otherwise-resolvable `--register-rev` that is not the item-evidence `--rev` and is not in its strict-descendant relationship. This exercises a separate revision-selection boundary from the token-only forged item and must be represented in the r40 counter tests.

### Evidence

- Frozen claim: `census/round-40/preregistration.txt`, C1 says anchored item lines need resolvable, revision-bound evidence, and register `commit` must be a **strict descendant** of `receipt_rev`; equal/backwards commit kills the claim.
- Committed r39 negative control: `census/round-39/c1-counter.py:187-200` independently resolves `args.rev` and `args.register_rev`, defaulting the latter to the former. It does not require either revision to be ancestor/descendant of the other.
- `census/round-39/c1-counter.py:218-240` evaluates item anchors and tokens solely against `args.rev`; at lines 241-248 it invokes the reconciler with the separately chosen `register_rev`. Thus the two legs can read different histories while both hashes/commits resolve.
- `census/round-39/c1-counter.py:136-152` only counts register commits that differ textually from `receipt_rev` (`commit != parts[6]`); it does not establish graph ancestry. The committed control receipt `census/round-39/records/c1-after.txt:19-21` reports `commit_distinct=6`, not an ancestry result.

### Commands actually run

1. `read /home/vgpnk/.omp/agent/RULES.md` — returned the required tooling rules.
2. `read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt` — returned frozen C1/C2/C3 predicates.
3. `glob` on `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39` — located the committed C1 record and wave artifacts.
4. `read` on `census/round-39/records/c1-after.txt` and `census/round-39/waves/w1/W1SimpC1.md` — confirmed recorded r39 output and documented r39 control limitations.
5. `read` on `census/round-39/c1-counter.py` and range `187-259` — inspected its revision checks, item loop, register leg, and acceptance predicate.

No counter execution, git/jj command, install, or production edit was performed. Scratch directory was created at `/fast/scratch/hyaku/souji-r40/R40simplifier46` with `TMPDIR` directed to its `tmp` subdirectory; no fixture was needed.

### Bounded falsification matrix for r40

Use a scratch copy of the committed fixture/repository; keep item `--rev` fixed and vary only register revision/row history. For each case capture exact argv, stdout, stderr, exit status, and whether the register row was accepted:

1. `commit == receipt_rev`: reject strict-descendant predicate (equality is not strict).
2. `commit` is an ancestor of `receipt_rev`: reject.
3. `commit` is a strict descendant: accept if all other row predicates pass.
4. `commit` is unrelated but resolvable: reject; this specifically detects a textual inequality implementation masquerading as ancestry.
5. `--register-rev` resolves but is not the item `--rev`'s ancestor/descendant: ensure its explicit semantics cannot silently substitute evidence history; report whether the claim requires a relation between these selected revisions. Repeat with an unresolved `--register-rev` as a refusal control.
6. Preserve the frozen forged token-only item: it must remain OPEN even when the register leg is otherwise valid.

The decisive falsifier is any equal, backwards, or unrelated commit accepted as satisfying strict-descendant; a second independent falsifier is a token-only line closing. An observed valid descendant row rejected also kills calibration per preregistration. The r39 control is expected to lack these guarantees by design; do not count its behavior as candidate evidence.

### Preserved contract / tradeoff

This finding does not recommend deleting or simplifying the new ancestry check. It identifies the separate `--register-rev` selection axis that could let a revision-bound implementation prove the wrong history. The frozen preregistration does not explicitly state a relation required between `--register-rev` and item `--rev`; case 5 should therefore be reported as an ambiguity/measurement, not silently promoted to a new acceptance condition.