# R40simplifier58 — C1 attack: unbound items authority + register commit-direction

role: simplifier (leaf; no subagent dispatch)
lane: /home/vgpnk/Projects/shokunin/souji-shokunin
frozen claim attacked: `census/round-40/preregistration.txt` §C1 (calibration)
base under audit: `0242085909fb6a4ee041c5443d76316ac6d59d4b` (round-39 verified tip)
counter bytes audited: `census/round-39/c1-counter.py`, sha256 `65e42904ea78c88aa0eeb711f5399da3600eddaef771e6dc229e2830a16340ff` — byte-identical in worktree and at base (`git show 0242085…:census/round-39/c1-counter.py | sha256sum` == `sha256sum` worktree).
scratch: `/fast/scratch/hyaku/souji-r40/R40simplifier58` (removed before yield; all commands reproduce from this report)

## Distinct item-58 edge cases (named)

1. **Unbound items authority.** The r39 counter reads `--items` with plain `open(args.items)` (c1-counter.py:201-204) — the one input NOT read through `git_show` at a revision (register: `git_show(root, register_rev, register)`; audited files: `git_show(root, args.rev, row["file"])`). Its docstring claims "This counter re-derives one predicate per routed defect from committed bytes only" (c1-counter.py:5-6). In r40 the evidence-pointer column will live in this items table; nothing in the frozen predicate binds the table itself to a revision.
2. **Register commit-direction discrimination.** No committed r39 artifact or byte of r39 code ever tests `commit` against `receipt_rev` for direction: `parse_register` counts `commit and commit != parts[6]` as `distinct` (c1-counter.py:143-146 — a backwards commit *feeds the floor*), and the reconciler's commit arm tests ancestry against `--rev` only (`ancestor_status(root, commit, rev)`, tools/souji-citation-reconcile.py:219). Demonstrated end-to-end below (E3).

Coordination: R40simplifier34 confirmed disjoint by IRC — theirs: pointer-target vacuity (pointer resolving into pre-round bytes) and the 7-hex-prefix resolution trap in a naive strict-descendant check; mine: items-table provenance and the direction census incl. the equal-commit-via-is-ancestor trap. No overlap.

## 0. Verified base (all commands run this seat)

```
git -C $L cat-file -e 0242085…^{commit}                      # resolves
TMPDIR=$S python3 -B $L/census/round-39/c1-counter.py --root $L --rev 0242085… \
  --items $L/census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch $S
```
rc=0; `SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=d892b74f8358` — byte-equal to the committed receipt `census/round-39/records/c1-after.txt` final SUMMARY. Control baseline reproduces from committed bytes.

## E1 — control confirmed: a token-only forged line closes (r39)

Committed items + one appended row (scratch copy; `diff` vs `git show 0242085…:census/round-39/c1-items.tsv` shows exactly the appended line):

```
R39-C1-99<TAB>corpus/lessons/round-38.md<TAB>R39-C1-01<TAB>S246,SOURCES-rows=170<TAB>-
```

Run as in §0 with `--items $S/items-forged.tsv`:

```
ITEM R39-C1-99 CLOSED
SUMMARY items=17 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=fdbed95faa5a
rc=0
```

No pointer concept exists in r39, so a token-only line closes. Matches the frozen control ("r39 counter accepts a token-only forged line").

## E2 — falsifier: the items bytes the counter consumed are in no commit

```
git -C $L hash-object $S/items-forged.tsv   # 991ee47b26eeffbdec414269f4db771719c6e8f6
git -C $L cat-file -e 991ee47b…             # rc=1, ABSENT from the object db
git -C $L log --all --oneline --find-object=991ee47b…   # 0 commits
git -C $L cat-file -e $(git -C $L hash-object $L/census/round-39/c1-items.tsv)  # present (committed blob)
```

E1's rc=0 receipt was derived from bytes that exist nowhere in git history. The r39 docstring's "from committed bytes only" is false for the items input; `items_sha=fdbed95faa5a` in the SUMMARY records uncommitted bytes a verifier cannot re-derive from the repo. This is the r37 A2.6 cheat class (uncommitted input authority) closed for the register by `--register-rev` pinning, still open for items.

## E3 — falsifier: a backwards and an equal commit both pass, end-to-end

Git fixture (private repo under scratch; `mktemp -d`, toplevel asserted equal before first commit; script kept verbatim in this seat's scratch as `fixture-direction.sh`, removed at cleanup — content summarized):

- 3 commits G → P → T; `tools/souji-citation-reconcile.py` copied from the lane into the fixture (the counter extracts it at `--rev`).
- `rec.txt` at G: `SUMMARY cases=1`; at P: `SUMMARY cases=1 cases=2`.
- `doc.md` at T (receipt named per r37 A1.2 backtick convention):
  `R1 cites <G-short> `rec.txt` receipt cases=1` / `R2 cites <P-short> `rec.txt` receipt cases=2`
- register.tsv (8-col) at T: `F1 … receipt_rev=P commit=G` (G is ancestor of P → **backwards**) and `F2 … receipt_rev=P commit=P` (**equal**).
- items.tsv: one row, `I1 doc.md R1 cites -`.

```
TMPDIR=$S python3 -B $L/census/round-39/c1-counter.py --root $D --rev $T \
  --items $D/items.tsv --register register.tsv --register-rev $T \
  --min-cells 2 --min-commit-distinct 1 --scratch $S
```

```
ITEM I1 CLOSED
REGISTER cells=2 mismatches=0 commit_distinct=1
SUMMARY items=1 open=0 register_cells=2 register_mismatches=0 commit_distinct=1 items_sha=cc2ec8902735
rc=0
```

rc=0 with F1's commit a strict ancestor of its receipt_rev and F2's commit equal to it. Two mechanisms, both measured:
- F1 backwards: `parse_register` counts `commit != receipt_rev` as `distinct` → the backwards row *contributes* `commit_distinct=1` and satisfies the floor.
- F2 equal: `merge-base --is-ancestor` treats equality as ancestry (`git -C $D merge-base --is-ancestor P P` → yes), and no r39 code compares `commit` to `receipt_rev` for direction, so the equal row sails through the reconciler commit arm.
This is the frozen kill condition "a backwards/equal commit passes", reproduced against the committed r39 counter bytes.

## E4 — census of the only committed register: strict-descendant is satisfiable, no valid row at risk

`census/round-39/cells.tsv`: 6 rows, all `commit=a8e6d75b3183849129fca01f959dbe5a69cf066c`; receipt_revs `5230a341…` (REG-07..11) and `f8ba3f3b…` (REG-12).

```
git -C $L merge-base --is-ancestor 5230a341… a8e6d75b…   # yes (both pairs)
git -C $L merge-base --is-ancestor a8e6d75b… 5230a341…   # no  → commit strictly AFTER receipt_rev
git -C $L merge-base --is-ancestor a8e6d75b… 0242085…    # yes (register sits inside r39 history)
```

All 6 committed rows are strict descendants of their receipt_rev, none equal → a correct strict-descendant check rejects **zero** existing valid rows. The r40 kill condition "any existing valid row is rejected" is avoidable; conversely the committed register provides no negative direction coverage — the r40 fixture must synthesize backwards/equal rows itself (E3 is a ready-made shape).

## Incidental dead path (simplifier finding, r40-relevant)

`register_leg` early-returns `(0, 0, "REGISTER-ABSENT")` when its own `git_show(register_rev, register)` misses — my first fixture run (register committed one commit after the audited rev) printed `REGISTER cells=0 mismatches=0 commit_distinct=0` with no diagnostic; the run failed only via the `--min-cells` floor. A silently-empty register and an absent register are indistinguishable in the output. The r40 strict-descendant arm should emit its own per-row mismatch class (e.g. `COMMIT-NOT-DESCENDANT <commit> not a strict descendant of receipt_rev <receipt_rev>`), never fold direction failures into `cells=0` or the floor.

## Verdict on the frozen C1 claim

- **Control: CONFIRMED by my own runs** — r39 accepts a token-only forged line (E1, rc=0) and has no strict-descendant test anywhere in code or committed data (E3, rc=0 with backwards+equal rows).
- **Concrete falsifier for the r40 counter as frozen:** the predicate requires each anchored item line to carry "a resolvable, revision-bound evidence pointer", but the items table carrying those pointers is itself revision-unbound. If r40 keeps `open(args.items)`, the forged-line test stays green while the entire measurement (anchors, must/mustnot, pointer column) is evaluated against attacker-chosen bytes bound to no revision, and no verifier can re-derive the after-receipt from committed bytes alone — the same defect class C1 exists to police, present in the counter itself.
- **Bounded measurement plan (one mirror of an existing leg, no second convention):**
  1. Read items through `git_show(root, items_rev, items_path)` with `--items-rev` defaulting to `--rev` — exact precedent: `--register-rev` (r37 A1.1). Docstring's "committed bytes only" becomes true.
  2. Add to the r40 forged battery an items file whose bytes exist in no commit (`git cat-file -e $(git hash-object FILE)` must fail) and require rc != 0; require `--items-rev` named explicitly in the frozen measurement command, as `--register-rev` already is.
  3. Strict descendant = `commit != receipt_rev` (40-hex byte comparison, NOT `is-ancestor` alone — E3/F2 shows equality passes is-ancestor) AND `git merge-base --is-ancestor receipt_rev commit`. Per-row mismatch class, not a floor contribution (today a backwards row *raises* `commit_distinct`, E3/F1). Sibling R40simplifier34's 7-hex-prefix trap applies to the same comparison: require 40-hex before comparing.
  4. Satisfiability is proven on committed data (E4): the r40 target state rejects no existing valid row.

## Hygiene

- Lane writes: this report only. `git -C $L status --short` before and after: `?? census/round-40/` and this report's untracked path; no tracked byte modified, no git/jj/index mutation, no commit, no push. Counter and items files re-hash unchanged after all runs.
- Fixtures: private git repos under `/fast/scratch/hyaku/souji-r40/R40simplifier58`; `git rev-parse --show-toplevel` asserted equal to the fixture dir before every commit; fixture dirs removed (final run via trap; earlier kept run deleted explicitly).
- Scratch removed before yield; nothing installed (python3/git/sha256sum only); no PATH-directory writes; no `.ufo/state`, fleet, sibling-lane, watchdog, or template writes.
