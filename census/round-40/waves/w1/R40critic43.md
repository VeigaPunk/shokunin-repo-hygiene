# R40critic43 — C1 calibration attack (souji round 40, wave 1)

- seat: critic (leaf, no subagent dispatch); lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- frozen contract read first: `census/round-40/preregistration.txt` (C1 calibration paragraph)
- r40 prereg base revision: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (round-39 verified tip); lane HEAD during this attack: `be4cb61` (one spot-check commit on top; `census/round-40/` untracked, no r40 counter exists yet)
- r39 counter under attack (the frozen C1 control): `census/round-39/c1-counter.py` (working tree == blob at `0242085` for every cited file; `c1-items.tsv` sha256 prefix `d892b74f83587a79` identical working tree vs `0242085` blob)
- scratch: `/fast/scratch/hyaku/souji-r40/R40critic43` (removed before yield; `TMPDIR` set per run)
- tool installs/upgrades: none. No lane byte written except this report. No git/jj mutation anywhere except throwaway fixture commits inside scratch (toplevel asserted before first commit).

## Named distinct edge case: the ITEM arm's pointer-relation and table-binding gap

The frozen C1 predicate requires each anchored item line to carry "a resolvable, revision-bound evidence pointer". Two properties are unfrozen and attackable:

1. **Pointer relation.** "Resolvable" nowhere says the pointer's revision must lie **inside the audited revision's history** (`pointer_rev ∈ ancestors(--rev)`). Resolvable-but-elsewhere evidence (a parallel or future commit in the same repo) is exactly what the r39 control demonstrably accepts — measured today, F2 below.
2. **Table binding.** The items table that carries the new pointer predicate is itself read from an unbound path: `census/round-39/c1-counter.py:203` does `with open(args.items, encoding="utf-8")` — no `--items-rev`, no `git show`. The register input IS revision-bound (`:198`, `register_rev = args.register_rev or args.rev`); the items input is not. The only binding is the manually compared `items_sha=` print (`:209`, `:251-252`).

**Distinctness from sibling attacks** (their reports read before writing): R40critic19 attacks register-side `receipt_rev == --rev` reflexivity; R40critic31 attacks semantically irrelevant pointers (linkage vs truth); R40critic55 attacks merge second-parent reachability in the register arm. r39's own waves own the evidence-ABSENT forgery (`census/round-39/waves/w1/W1RevC1Forge.md` §2: bare token-only lines close) and the backwards-commit-green register (`W1RevC1Register.md` A5). This seat's case is **evidence-PRESENT, relation-forged** (the pointed-to object exists and resolves, but outside the audited history), plus the predicate-carrier (items table) being unbound — measured, not speculative.

## Evidence

### E1 — committed control facts (r39 bytes)

- `census/round-39/c1-counter.py:203` items read from any filesystem path; `:209` + `:251-252` `items_sha=` is the sole table fingerprint; `:198` register blob is rev-bound. Nothing dereferences a pointer-shaped token: the close predicate is `anchor in line` + whole-token `must`/`mustnot` on one line (`:226-233`).
- `tools/souji-citation-reconcile.py` (blob `bece1700…`, identical at `0242085` and HEAD): `ancestor_status` `:204-211`; receipt_rev arms `:300-320` (resolve + ancestor-of-`--rev`); commit arm `commit_checks` `:218-243` (resolve + ancestor-of-`--rev` + named on line + receipt carries expected). **No arm compares `commit` with `receipt_rev`** — the exact discrimination r40 C1 adds.
- `census/round-39/cells.tsv` (landed `9440270`): all six rows `receipt_rev=5230a341…`, `commit=a8e6d75b…`. Measured in-lane: `git merge-base --is-ancestor 5230a341… a8e6d75b…` → rc 0, hashes differ → the live register's rows are already strict-descendant. So an honest r40 strict-descendant arm accepts the existing rows; the kill condition "existing valid row rejected" is decidable, and **equality (`commit == receipt_rev`) is the exact boundary the r39 control passes** (`is_ancestor` reflexive; reconciler A3-shape clean; only the `distinct>=2` floor refuses).
- `census/round-39/c1-counter.py:253-258`: `ok` requires `open_count == 0` (`:254`). Any permanently-OPEN forged probe carried in the measured table forces exit 1.
- Receipt context: `census/round-39/records/c1-after.txt` measured at `2f6e981a…`; verified `git merge-base --is-ancestor 2f6e981a… 0242085…` → rc 0 (receipt revision is an ancestor of the r40 base — consistent, no defect).

### E2 — F0 control replay (harness honesty)

```
python3 -B <lane>/census/round-39/c1-counter.py --root <lane> \
  --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --items <lane>/census/round-39/c1-items.tsv \
  --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r40/R40critic43/tmp0
```

`ITEM R39-C1-01…16 CLOSED` (all 16), `REGISTER cells=6 mismatches=0 commit_distinct=6`, `SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=d892b74f8358`, rc=0 — reproduces the committed `records/c1-after.txt` shape at the prereg-named base.

### E3 — F1 falsifier: the audited revision does not fix the receipt; the unbound table does

`items-ptr.tsv` = committed table with ONE token appended to R39-C1-01's `must` (`ptr@be4cb61` — a resolvable revision, the current lane tip). Same command, same `--rev`, `--items <scratch>/items-ptr.tsv`:

```
ITEM R39-C1-01 OPEN PREDICATE-MISSING corpus/lessons/round-38.md missing=['ptr@be4cb61'] hits=1
… R39-C1-02..16 CLOSED …
SUMMARY items=16 open=1 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=2588bec3b79c   rc=1
```

Same audited revision, one input cell changed → verdict flips CLOSED→OPEN and the receipt fingerprint moves `d892b74f8358 → 2588bec3b79c`. The r39 control has no authority to prefer either table; the r40 C1 target ("every item closed, zero unbound evidence pointers") is **a property of table bytes the frozen text does not bind** to any revision. Post-measurement, pointer cells can be rewritten and a fresh receipt regenerated — "zero unbound pointers" is then unfalsifiable. The kill condition "any existing valid row is rejected" is equally table-relative: E3 "rejects" a valid row using nothing but an edited input file.

### E4 — F2 falsifier: pointer to a resolvable commit OUTSIDE the audited history is accepted today

Scratch fixture (toplevel asserted, all commits inside `/fast/scratch`): trunk `A → B`; side branch `future` at `A` carrying `F`. `F=3c505debc8df86aa309cf2740d76fd7b2790ebdc`, `B=b122638af69bd143d6eda0c6c5b1f60a4e0c270f`. `B` adds `lane/lesson.md`:

```
R40-F2 evidence=census/round-39/records/c1-after.txt@3c505debc8df86aa309cf2740d76fd7b2790ebdc ptr-rev-not-ancestor
R40-F2-BARE ptr-rev-not-ancestor (no pointer token on this line)
```

Asserts measured in the fixture: `git -C $D cat-file -e F^{commit}` rc=0 (resolvable); `git -C $D merge-base --is-ancestor F B` rc=1 (**not** an ancestor of the audited revision).

```
python3 -B <lane>/census/round-39/c1-counter.py --root $D --rev b122638af69bd143d6eda0c6c5b1f60a4e0c270f \
  --items <scratch>/f2-items.tsv --register census/round-39/cells.tsv --scratch <scratch>/tmp2
ITEM R40-F2 CLOSED            ← line carries a pointer whose revision is resolvable but NOT in B's history
ITEM R40-F2-BARE CLOSED       ← no-pointer line (reproduces W1RevC1Forge §2 in this fixture)
REFUSAL COULD-NOT-EVALUATE: tools/souji-citation-reconcile.py absent at b122638af…   rc=2
```

The rc=2 is the register leg refusing (fixture has no reconciler bytes — expected, orthogonal); both ITEM verdicts printed before it. **The r39 control closes a pointer-forged line whose evidence revision is not an ancestor of the audited revision.** "Resolvable, revision-bound" without a history constraint accepts evidence that does not exist in the audited state; conversely a pointer to an ancestor revision whose bytes do NOT contain the anchored line is equally accepted (the control never dereferences — same mechanism as F2; r40 must add the identity check, not just resolvability).

### E5 — the frozen target sentence vs the counter's exit contract (derived, no run)

Target: "the counter reports every item closed, … and the forged token-only item remains OPEN." Under the committed exit contract (`:253-258`, `open_count == 0`), a forged probe that remains OPEN inside the measured table forces `open>=1` and rc 1 — contradicting "every item closed" as a SUMMARY literal — while a probe in a separate table has no frozen SUMMARY field, table path, or expected exit code anywhere in the C1 paragraph. As frozen, the target is satisfiable only by an unspecified placement choice; the receipt cannot be judged against it without that choice being pinned.

## Falsifier summary (what the r40 candidate must survive; none measurable today — `census/round-40/` has no counter)

- A counter that implements "resolvable" as `cat-file -e` (or any blob existence test) on a pointer-shaped cell, with tokens unchanged, passes every frozen target clause while accepting F2's outside-history pointer — the control (E4) cannot discriminate it from the honest reading, so the C1 claim's discrimination would rest entirely on implementation choices the frozen text leaves open.
- A counter whose items input stays working-tree-bound (the r39 shape) makes "zero unbound evidence pointers" a property of an attacker-editable file (E3); `items_sha` is printed but not pinned by the frozen predicate string.

## Bounded measurement plan for the r40 C1 receipt (each probe: exact stdout, stderr, rc, fixture HEAD, and both revisions recorded; fixture commits only in scratch with toplevel asserted)

- **P0 pristine:** committed r40 items table at the landing rev via a frozen command string; SUMMARY literal and exit code **pinned in the predicate**, including the forged-probe placement (resolves E5: either the probe rides its own named table with its own SUMMARY field, or the predicate states `open=1` explicitly).
- **P1 probe isolation:** forged token-only row → OPEN in the placement P0 pinned; the honest table alone reads all-closed.
- **P2 pointer arms (all must read UNBOUND / mismatch):** (a) pointer unresolvable; (b) pointer resolvable but not an ancestor of `--rev` (F2 fixture shape, `merge-base --is-ancestor` rc 1); (c) pointer resolvable ancestor but the bytes at `pointer_rev:pointer_path` do not contain the anchored line/expected value (identity, not existence); (d) pointer resolving to a blob, not a commit. Accept classes should mirror the reconciler's precedent (`RECEIPT-REV-NOT-ANCESTOR`, `COMMIT-UNRESOLVED`, `COMMIT-ANCESTOR-ERROR`) so errors are could-not-evaluate, not silent passes.
- **P3 table binding:** run the candidate twice at one `--rev` with two tables; require the receipt to carry `items_sha` AND the revision/path the table was read from; freeze the table identity in the predicate (an `--items-rev` reading `git show <rev>:census/round-40/c1-items.tsv`, or the items path+sha pinned in the frozen command string).
- **P4 register strict-descendant matrix (the NEW arm; each must produce a mismatch):** (i) `commit == receipt_rev` (the boundary the kill rule names; `is_ancestor` is reflexive so a naive arm passes it); (ii) commit strict ancestor of receipt_rev (backwards; receipt bytes and citation line agree so every existing r39 arm passes — only the new arm fires); (iii) commit unresolvable; (iv) receipt_rev unresolvable; (v) unrelated roots; (vi) critic55's second-parent-only merge — record which descent semantics the candidate enforces. Control row: the live r39 pair `5230a341… → a8e6d75b…` must stay ACCEPTED (verified strict-descendant in-lane, E1).
- **P5 floors:** `--min-cells` / `--min-commit-distinct` must be pinned inside the frozen command string (r39 residue: `W1RevC1Forge.md` §4 — rc 0 with `register_cells=0` when lowered).

## Impacted axes and smallest safe correction

- **Calibration (primary):** the C1 claim is attackable as frozen on pointer-relation and table-binding unless the receipt pins: pointer grammar + `pointer_rev ∈ ancestors(--rev)` + pointer-byte identity, and table identity (`--items-rev` or sha-in-predicate). No post-freeze wording change is permitted; these become receipt/plan requirements (P0-P5), reported honestly if the candidate ships without them.
- **Operability (secondary):** the receipt shape is underspecified while E5 stands; P0 resolves it.
- **Coverage / C2 / C3:** no conclusion drawn; not attacked by this seat.

## Verdict

**Bounded attack — control falsified on two measured points, candidate unmeasured (does not exist yet).** F0 shows the harness reproduces the committed control honestly. F1 (E3) shows the audited revision does not determine the C1 receipt — the unbound items table does. F2 (E4) shows the r39 control closes a line whose evidence pointer names a resolvable commit outside the audited revision's history. The frozen C1 predicate therefore discriminates against the r39 control **only if** the r40 candidate enforces pointer-history-membership + pointer-byte identity + table binding + pinned probe placement; none of the four is forced by the frozen text. Kill conditions ("forged line closes", "backwards/equal commit passes", "existing valid row rejected") remain measurable and, per E1, the live register rows are already strict-descendant, so an honest candidate can satisfy them — this is an instrumentation-gap finding, not a doomed claim.

## Commands actually run

- `read /home/vgpnk/.omp/agent/RULES.md`; `read census/round-40/preregistration.txt`; `read skill://godspeed` — required reads.
- `read census/round-39/c1-counter.py` (ranges 1-277), `census/round-39/preregistration.txt`, `census/round-39/c1-items.tsv`, `census/round-39/cells.tsv`, `census/round-39/make-cells.py`, `census/round-39/records/c1-after.txt`, `census/round-39/waves/w1/W1RevC1Forge.md`, `census/round-39/waves/w1/W1RevC1Register.md`, `.ufo/waves/round-40/w1/R40critic19.md`, `R40critic31.md`, `R40critic55.md`, `.ufo/waves/round-39/w1/W1CritC1Axis.md` (via sibling report citations).
- `git -C <lane> show 0242085…:tools/souji-citation-reconcile.py > <scratch>/reconciler-at-base.py`; source read (blob `bece1700…`, verified identical at HEAD via `git rev-parse HEAD:tools/...`).
- `git ls-tree -r --name-only 0242085… -- census/round-39`; `git log --oneline --all -- census/round-39/cells.tsv`; `sha256sum census/round-39/c1-items.tsv` (== `0242085` blob: `d892b74f83587a79…`).
- Ancestry checks (lane): `git merge-base --is-ancestor 5230a341… a8e6d75b…` rc 0; `git merge-base --is-ancestor 2f6e981a… 0242085…` rc 0.
- F0/F1/F2 counter runs with exact commands and outputs quoted above (E2/E3/E4); fixture toplevel asserted (`test "$(git -C $D rev-parse --show-toplevel)" = "$D"`) before any commit; no `set -e` aborts touched the lane.
- No installs (pacman paused; none needed). Scratch tree removed before yield: `rm -rf -- /fast/scratch/hyaku/souji-r40/R40critic43`.
