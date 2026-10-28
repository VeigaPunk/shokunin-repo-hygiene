# R40w2critic03 — C1 do-nothing control (falsify)

Seat: R40w2critic03 (role critic, leaf, no subagent dispatch). Milestone: r40 falsify.
Scratch: `/fast/scratch/hyaku/souji-r40/w2/R40w2critic03/` (clone, landed-tree extract, mutant copies, stub counter). Removed at the end of this seat (see §8).

## Verdict

**FALSIFIED** — the C1 counter's discrimination is not what the round claims.

1. A do-nothing stub that hard-codes item verdicts passes **all 8/8** cases of the frozen C1 fixture `tests/fixtures/r40-c1-evidence.py` (§3.1).
2. The frozen counter `census/round-40/c1-counter.py` **closes an item whose claimed value is false** (`rows=999` against a receipt that reads `rows=178`) when the line carries any 40-hex string that resolves and whose path exists (§3.2). The items arm never reads the value or the receipt.
3. The fixture cannot kill the evidence rules that name *resolvable* and *ancestor* and *path present*: with those three rules deleted the fixture is still 8/8 (§3.3).
4. With an absent register and floors `--min-cells 0 --min-commit-rows 0` the frozen counter returns rc 0 `ok` with `REGISTER-ABSENT` (§3.4).

Not falsified (SAFE, measured): the strict-descendant arm rejects equal and backwards commits, and a token-only forged line with no hash stays OPEN (§4).

## 0. Scope and bytes

- Landed instrument commit: `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Current lane HEAD: `549d9ec53a1f5932337ff14438fcd22b0621828d` (chain `128e412 → 8a5fbdb → 6ded124 → 556c24a → 549d9ec`).
- `git diff --stat 128e412 HEAD` does not list `census/round-40/c1-counter.py`, `tests/fixtures/r40-c1-evidence.py`, or `tools/souji-citation-reconcile.py`, so the landed C1 bytes are the HEAD C1 bytes.
- The C1 items (`census/round-40/c1-items.tsv`), forged set (`census/round-40/c1-forged.tsv`) and register (`census/round-40/cells.tsv`) first appear at `549d9ec`. **The landed commit `128e412` carries no C1 items and no C1 register**; §3.5 shows what it does alone.
- Lane `git status --porcelain` shows untracked `census/round-40/records/c{1,2,3}-after-d.txt` (not mine, not read, not touched).

Extraction (read-only, from the lane object store):

```
S=/fast/scratch/hyaku/souji-r40/w2/R40w2critic03
LANE=/home/vgpnk/Projects/shokunin/souji-shokunin
mkdir -p $S/landed-tree $S/fixwork $S/work
git -C $LANE archive 128e412b0ced3c243dc27c3dd3332054a611bc2e | tar -x -C $S/landed-tree
git clone -q --no-checkout --no-hardlinks $LANE $S/clone        # fixture clone, scratch only
git -C $S/clone show 549d9ec53a1f5932337ff14438fcd22b0621828d:census/round-40/c1-items.tsv  > $S/items.tsv
git -C $S/clone show 549d9ec53a1f5932337ff14438fcd22b0621828d:census/round-40/c1-forged.tsv > $S/forged.tsv
```

`git -C $S/clone rev-parse --show-toplevel` → `/fast/scratch/hyaku/souji-r40/w2/R40w2critic03/clone` (checked before the fixture commit).

## 1. Axes attacked

- A. Items arm of the C1 counter (value, evidence path, evidence revision).
- B. The C1 fixture as the discrimination test for the counter's predicates (rules 3–6 and the register arm).
- C. Register floors / absent-register handling.

## 2. Baseline: landed fixture and frozen counter on the committed round-40 items

```
$ TMPDIR=$S/fixwork python3 -B $S/landed-tree/tests/fixtures/r40-c1-evidence.py \
    --counter $S/landed-tree/census/round-40/c1-counter.py \
    --base-counter $S/landed-tree/census/round-39/c1-counter.py --work $S/fixwork
case-bound-item-closed=PASS
case-forged-token-only-open=PASS
case-forged-unresolved-rev-open=PASS
case-forged-non-ancestor-open=PASS
case-register-clean-accepted=PASS
case-register-equal-rejected=PASS
case-register-backwards-rejected=PASS
case-r39-control-closes-forged=PASS
SUMMARY cases=8 pass=8 fail=0
rc=0

$ TMPDIR=$S/work python3 -B $S/landed-tree/census/round-40/c1-counter.py --root $S/clone \
    --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items $S/items.tsv --forged $S/forged.tsv \
    --register census/round-40/cells.tsv --register-rev 549d9ec53a1f5932337ff14438fcd22b0621828d \
    --min-cells 1 --min-commit-rows 1 --scratch $S/work
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND 8a5fbdbddaab24c5ba43fc6a133499efb405f214
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-ANCESTOR 002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6
rc=0
```

Baseline is clean. The attacks below are on what this baseline cannot see.

## 3. Attacks

### 3.1 The do-nothing control: a stub counter that passes the frozen fixture 8/8 — FALSIFIED

The stub (`$S/stub-counter.py`, same CLI as the frozen counter, source reproduced in §6) does none of the claimed work: it prints every item row `CLOSED` and every forged row `OPEN` by fiat, never reads an anchored line or an evidence pointer, and implements only the register arm's strict-descendant test (`git merge-base --is-ancestor` plus equality). Run through the frozen fixture:

```
$ TMPDIR=$S/fixwork/stub python3 -B $S/landed-tree/tests/fixtures/r40-c1-evidence.py \
    --counter $S/stub-counter.py --base-counter $S/landed-tree/census/round-39/c1-counter.py --work $S/fixwork/stub
case-bound-item-closed=PASS
case-forged-token-only-open=PASS
case-forged-unresolved-rev-open=PASS
case-forged-non-ancestor-open=PASS
case-register-clean-accepted=PASS
case-register-equal-rejected=PASS
case-register-backwards-rejected=PASS
case-r39-control-closes-forged=PASS
SUMMARY cases=8 pass=8 fail=0
rc=0
```

The stub also prints the expected receipt shape for the lane's committed items:

```
$ python3 -B $S/stub-counter.py --root $S/clone --rev 549d9ec53a1f5932337ff14438fcd22b0621828d \
    --items $S/items.tsv --forged $S/forged.tsv --register census/round-40/cells.tsv \
    --register-rev 549d9ec53a1f5932337ff14438fcd22b0621828d --min-cells 1 --min-commit-rows 1
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-NOT-BOUND
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-BOUND
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=- forged_sha=-
rc=0
```

Why the fixture accepts it: `tests/fixtures/r40-c1-evidence.py:154-156` checks only `"ITEM BOUND-1 CLOSED" in out`; `:158-169` checks only that a `FORGED <tag> ` line contains ` OPEN `; `:173-175` checks only `rc` and the `register_violations` / `register_mismatches` SUMMARY fields; `:177-182` and `:184-189` check only `rc == 1` and `violations >= 1` for the equal and backwards registers. Nothing in the fixture requires the item verdict to come from the item's evidence. Its 8 cases are satisfiable by hard-coded output plus the register ancestry test.

### 3.2 The frozen counter closes a false value — FALSIFIED

Scratch clone commit `fddaadfbc2b651a80e0c24236d356486524690d2` (fixture identity `critic03-fixture`, scratch only) adds `STUB.md`:

```
R40-STUB-VALUE cell expected rows=999 per `census/round-40/records/census-after.txt` at 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39
```

The receipt it cites says the opposite:

```
$ git -C $S/clone show 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39:census/round-40/records/census-after.txt | grep -n '^SUMMARY'
4:SUMMARY rows=178 W04=49 rc=0 measured_at=8a5fbdbddaab24c5ba43fc6a133499efb405f214 registry=corpus/SOURCES.md
```

Items row (`$S/stub-items-only.tsv`): `R40-STUB-VALUE  STUB.md  R40-STUB-VALUE  rows=999  -  census/round-40/records/census-after.txt@6ded1248b6d0005ac31ff2e1c867ecb0a075ab39`

```
$ TMPDIR=$S/work python3 -B $S/landed-tree/census/round-40/c1-counter.py --root $S/clone \
    --rev fddaadfbc2b651a80e0c24236d356486524690d2 --items $S/stub-items-only.tsv \
    --register $S/ok-register.tsv --register-rev fddaadfbc2b651a80e0c24236d356486524690d2 \
    --min-cells 1 --min-commit-rows 1 --scratch $S/work
ITEM R40-STUB-VALUE CLOSED
...
SUMMARY items=1 open=0 forged=0 forged_open=0 forged_closed=0 ... items_sha=0ecc69ab2449 forged_sha=-
```

(The `rc=1` in that run came from the register file, not the item: `$S/ok-register.tsv` was passed as a working-tree path, not a committed blob, so `REGISTER-ABSENT`. The item line is the finding.)

Same stub, same counter, same rev, with the register in committed bytes (`census/round-40/stub-register.tsv`, row `R40-STUB-REG` expecting `rows=999` at receipt_rev `6ded124`, commit `556c24a`):

```
ITEM R40-STUB-VALUE CLOSED
REGISTER cells=1 mismatches=3 commit_rows=1 commit_hashes=1 violations=0 ok
...
rc=1
```

The register arm (`tools/souji-citation-reconcile.py`, run at the stub rev) catches the same false value three ways:

```
MISMATCH R40-STUB-REG COMMIT-UNNAMED 556c24a is not named on the anchored line
MISMATCH R40-STUB-REG COMMIT-RECEIPT-DISAGREES census/round-40/records/census-after.txt expected='rows=999' (no SUMMARY line at 556c24a carries it)
MISMATCH R40-STUB-REG RECEIPT-DISAGREES census/round-40/records/census-after.txt expected='rows=999' (no SUMMARY line carries it)
SUMMARY cells=1 mismatches=3
```

So the two arms of the same instrument disagree. The register arm checks the value against the receipt (`tools/souji-citation-reconcile.py:284` expected token on the anchored line; `:303-318` receipt carries `expected` on a SUMMARY line). The items arm (`census/round-40/c1-counter.py:235-260`) does not: it tests the anchor and the `must` tokens on one line (`:240-250`), then rules 3–6 (`:252-259`), and none of those reads the token's value against the evidence blob. The r40 predicate text says "each anchored item line must carry a resolvable, revision-bound evidence pointer", and that predicate is implemented; the calibration intent (the cell's value is the receipt's value) is not.

Evidence pointer is decorative too (same run family): evidence path only has to exist at the evidence revision (`c1-counter.py:256-257`), not be the receipt the line names, and a directory is accepted because `git show <rev>:<dir>` returns rc 0:

```
$ TMPDIR=$S/work python3 -B $S/landed-tree/census/round-40/c1-counter.py --root $S/clone --rev fddaadfbc2b651a80e0c24236d356486524690d2 --items $S/unrelated-items.tsv --register census/round-40/stub-register.tsv --register-rev fddaadfbc2b651a80e0c24236d356486524690d2 --min-cells 1 --min-commit-rows 1 --scratch $S/work
ITEM R40-DIR CLOSED          # evidence census/round-40/sources@6ded124 (a tree)
ITEM R40-UNRELATED CLOSED    # evidence census/round-40/sources/SHA256SUMS@6ded124 (unrelated to rows=)
```

(`git -C $S/clone show 6ded124:census/round-40/sources` → `tree 6ded124…:census/round-40/sources`, rc 0 on the tree path.)

### 3.3 The fixture cannot kill rules 3, 4, 5 — FALSIFIED

Mutants are copies of the landed counter in scratch with lines deleted (`CUT` equivalents):

- `mut-rules345.py`: delete `:252-257` (rules 3, 4, 5: resolve, ancestor, path present).
- `mut-rule3.py`: delete `:252-253` (resolve).
- `mut-rule5.py`: delete `:256-257` (path present).
- `mut-rule6.py`: delete `:258-259` (bound-to-line) — control, should be killed.

```
$ for m in rules345 rule3 rule5 rule6; do echo "== $m"; python3 -B $S/landed-tree/tests/fixtures/r40-c1-evidence.py --counter $S/mut-$m.py --base-counter $S/landed-tree/census/round-39/c1-counter.py --work $S/fixwork/$m; echo rc=$?; done

== rules345
... 8/8 PASS ...  SUMMARY cases=8 pass=8 fail=0   rc=0
== rule3
... 8/8 PASS ...  SUMMARY cases=8 pass=8 fail=0   rc=0
== rule5
... 8/8 PASS ...  SUMMARY cases=8 pass=8 fail=0   rc=0
== rule6
case-forged-token-only-open=FAIL out='... FORGED FORGE-TOKEN CLOSED (must stay OPEN) ...'
case-register-clean-accepted=FAIL rc=1 violations=0 mismatches=0
SUMMARY cases=8 pass=6 fail=2   rc=1
```

Reading: the fixture kills the bound-to-line rule (rule 6) and nothing else in the evidence chain. `case-forged-unresolved-rev-open` and `case-forged-non-ancestor-open` pass with rules 3–5 deleted because the forged line does not contain the evidence hash, so rule 6 returns OPEN with `EVIDENCE-NOT-BOUND` first. Those two cases pass for the wrong reason. Rule 4 alone was not separately mutated; the combined `:252-257` removal (which includes it) survives, so rule 4 is not discriminated either.

### 3.4 Absent register + zero floors is a vacuous pass — FALSIFIED (flag-level)

`register_leg` returns `(0,0,0,0,0,"REGISTER-ABSENT")` when the register is not at `--register-rev` (`c1-counter.py:186`), and the verdict (`:335-342`) does not refuse on it; it only compares `cells >= min_cells` and `commit_rows >= min_commit_rows`.

```
$ TMPDIR=$S/work python3 -B $S/landed-tree/census/round-40/c1-counter.py --root $S/clone \
    --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items $S/items.tsv \
    --register census/round-40/no-such-register.tsv --register-rev 549d9ec53a1f5932337ff14438fcd22b0621828d \
    --min-cells 0 --min-commit-rows 0 --scratch $S/work
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
REGISTER cells=0 mismatches=0 commit_rows=0 commit_hashes=0 violations=0 REGISTER-ABSENT
SUMMARY items=3 open=0 ... register_cells=0 ... register_violations=0 ...
rc=0
```

With the default floors (1) the same command is rc 1. The default protects the measurement; a caller passing `--min-cells 0 --min-commit-rows 0` receives `ok`. The fixture always passes floors 1 (`tests/fixtures/r40-c1-evidence.py:112`), so this path is untested.

### 3.5 The landed bytes alone cannot produce a C1 receipt

```
$ TMPDIR=$S/work python3 -B $S/landed-tree/census/round-40/c1-counter.py --root $S/clone \
    --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --items $S/items.tsv \
    --register census/round-40/cells.tsv --register-rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --scratch $S/work
ITEM R40-CLAIM-D1 OPEN ANCHOR-ABSENT
ITEM R40-CLAIM-D2 OPEN ANCHOR-ABSENT
ITEM R40-CLAIM-D3 OPEN ANCHOR-ABSENT
REGISTER cells=0 mismatches=0 commit_rows=0 commit_hashes=0 violations=0 REGISTER-ABSENT
SUMMARY items=3 open=3 ... 
rc=1
```

Expected: the items and register are later commits. The measurement is only reproducible at `549d9ec`.

Also: the committed C1 record `census/round-40/records/c1-control.txt` runs the counter with `--items <items6.tsv>` and `--items <items5.tsv>` placeholders. Those TSVs are not committed; the record cannot be re-run from committed bytes. There is no committed "after" C1 receipt (`records/` has `c2-after`, `c3-after`, `census-after`, `fixtures-after`, `c1-control` only). The preregistration's measurement ("r40 counter receipt, with base and after revisions explicitly named") is therefore not satisfied by a committed artifact.

## 4. Controls that held (SAFE, measured)

Backwards and equal commits are rejected by the frozen counter (strict-descendant arm):

```
$ TMPDIR=$S/work python3 -B $S/landed-tree/census/round-40/c1-counter.py --root $S/clone --rev 6060412c19e889f869fc46b93588f387cdc09540 \
    --items $S/items.tsv --register census/round-40/bw-register.tsv --register-rev 6060412c19e889f869fc46b93588f387cdc09540 \
    --min-cells 1 --min-commit-rows 1 --scratch $S/work
REGISTER R40-BACK BACKWARDS commit-not-descendant 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39
REGISTER R40-EQ BACKWARDS commit-equals-receipt_rev 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39
REGISTER cells=2 mismatches=0 commit_rows=1 commit_hashes=1 violations=2 ok
rc=1
```

A token-only forged line with no hash stays OPEN (the committed `c1-forged.tsv` rows and the fixture's `FORGE-TOKEN`): `FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND …` at the baseline.

The strict-descendant equality and ancestry branches (`c1-counter.py:221`, `:225`) are the arms that reject the equal and backwards fixture rows. Their mutation kill status was not measured in this seat.

## 5. Counter-facing defects to route (not edited)

1. **Items arm is value-blind** (`census/round-40/c1-counter.py:240-259`). It never checks the `must` values against the evidence blob at `evidence_rev:evidence_path`. A cell can say `rows=999` and close against a receipt that says `rows=178` (§3.2).
2. **Evidence pointer is not tied to the line's claim** (`:258-259`): any 40-hex on the anchored line closes; `evidence_path` need not be named on the line (the reconciler requires a backticked receipt name on the line, `tools/souji-citation-reconcile.py:287`), need not be a blob, and a directory is accepted (§3.2).
3. **Fixture cannot kill rules 3–5** (`tests/fixtures/r40-c1-evidence.py:166-168`, `:144`): the two forged cases are decided by rule 6 (§3.3).
4. **Fixture is satisfiable by a do-nothing stub** (§3.1).
5. **Absent register is not a refusal** (`c1-counter.py:186`, `:335-342`), and `--min-cells 0 --min-commit-rows 0` yields rc 0 (§3.4).
6. **No committed C1 receipt; items/register live at a later commit than the landed instrument; the control record is not re-runnable** (§3.5). The lesson's own frontier line already states the evidence binding "accepts any resolvable ancestor as the evidence revision" (`corpus/lessons/round-40.md`, Frontier); this report adds the value-blind and fixture-vacuity findings to that.

Smallest safe correction (for the L1, after the falsify round): in `evaluate_item`, require each `must` token to occur on the evidence blob `git show <evidence_rev>:<evidence_path>` (a blob, `git cat-file -t`), and require the anchored line to name the evidence path in backticks; add fixture cases that (a) close a `rows=999`-vs-`rows=178` item and expect OPEN, (b) keep the hash-carrying unresolved/non-ancestor forged rows so rules 3–5 are the decisive reason, (c) a do-nothing stub case; make `REGISTER-ABSENT` a refusal.

## 6. Reproduction (the L1 can re-run)

Stub counter (`stub-counter.py`, verbatim; scratch only, never committed):

```python
#!/usr/bin/env python3
import argparse, os, subprocess, sys
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True); ap.add_argument("--rev", required=True)
ap.add_argument("--items", required=True); ap.add_argument("--forged")
ap.add_argument("--register", required=True); ap.add_argument("--register-rev")
ap.add_argument("--min-cells", type=int, default=1); ap.add_argument("--min-commit-rows", type=int, default=1)
ap.add_argument("--scratch")
args = ap.parse_args(sys.argv[1:])
env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C"}
def rows_of(path, text=None):
    if text is None:
        with open(path, encoding="utf-8") as h: text = h.read()
    out = []
    for line in text.split("\n"):
        if not line.strip() or line.startswith("#"): continue
        p = line.split("\t")
        if p[0] == "id": continue
        out.append(p)
    return out
items = rows_of(args.items)
forged = rows_of(args.forged) if args.forged else []
for p in items: print("ITEM %s CLOSED" % p[0])
for p in forged: print("FORGED %s OPEN EVIDENCE-NOT-BOUND" % p[0])
rr = args.register_rev or args.rev
raw = subprocess.run(["git", "-C", args.root, "show", "%s:%s" % (rr, args.register)],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env).stdout.decode("utf-8", "replace")
cells = violations = commit_rows = 0; hashes = set()
for p in rows_of(args.register, raw):
    cells += 1; receipt_rev = p[6]; commit = p[7] if len(p) > 7 else ""
    if commit: hashes.add(commit)
    if not commit or commit == receipt_rev:
        violations += 1; print("REGISTER %s BACKWARDS" % p[0]); continue
    commit_rows += 1
    if subprocess.run(["git", "-C", args.root, "merge-base", "--is-ancestor", receipt_rev, commit], env=env).returncode != 0:
        violations += 1; print("REGISTER %s BACKWARDS" % p[0])
print("REGISTER cells=%d mismatches=0 commit_rows=%d commit_hashes=%d violations=%d ok" % (cells, commit_rows, len(hashes), violations))
print("SUMMARY items=%d open=0 forged=%d forged_open=%d forged_closed=0 register_cells=%d register_mismatches=0 register_violations=%d commit_rows=%d commit_hashes=%d items_sha=- forged_sha=-" % (len(items), len(forged), len(forged), cells, violations, commit_rows, len(hashes)))
sys.exit(0 if violations == 0 and cells >= args.min_cells else 1)
```

Mutants: `python3 -B -c` slicing of a scratch copy (delete the named 1-based inclusive line ranges, e.g. for rules 3–5 delete 252–257), then pass `--counter` to the fixture. Fixture clone: `git clone --no-checkout --no-hardlinks <lane> $S/clone`, `git -C $S/clone checkout -q --detach <rev>`, `-c user.name=critic03-fixture -c user.email=fixture@example.invalid commit` inside the clone only.

## 7. Tools

No tools installed or updated. No pacman. Python 3 and git only (host).

## 8. Scratch

Scratch dir `/fast/scratch/hyaku/souji-r40/w2/R40w2critic03/` (clone, landed-tree, mutants, stub, fixwork, work) was removed by this seat after the last measurement (`rm -rf`, verified by `test -e`).

Lane: no file was written in the lane except this report. No git mutation in the lane (archive, clone, show, merge-base, ls-tree and rev-parse only).
