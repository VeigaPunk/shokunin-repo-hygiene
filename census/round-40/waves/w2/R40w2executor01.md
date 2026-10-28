# R40w2executor01 — C1 counter + fixture at the landed bytes (executor, falsify)

Landed instrument commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Lane HEAD at run time `549d9ec53a1f5932337ff14438fcd22b0621828d`
(descendant: `c1-items.tsv`, `c1-forged.tsv`, `cells.tsv` and the SCORECARD `R40-CLAIM-*` lines exist only at/after 549d9ec; `c1-counter.py` bytes are unchanged-from-landing in what I read at `census/round-40/c1-counter.py`, header C710).
Scratch: `/fast/scratch/hyaku/souji-r40/w2/R40w2executor01` (TMPDIR and --work/--scratch always this path). L=/home/vgpnk/Projects/shokunin/souji-shokunin.

## 1. Real commands (items/forged/register files DO exist)
```
python3 -B $L/census/round-40/c1-counter.py --root $L --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items $L/census/round-40/c1-items.tsv --forged $L/census/round-40/c1-forged.tsv --register census/round-40/cells.tsv --scratch $S
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
Same command with `--rev 128e412b…` (landed instrument commit; claims/register not yet there): rc=1, `items=3 open=3` (ANCHOR-ABSENT), `REGISTER … REGISTER-ABSENT`, forged all OPEN. With `--rev 556c24a5…`: rc=1, items OPEN ANCHOR-ABSENT, REGISTER-ABSENT. Items are therefore only closable at 549d9ec (HEAD), not at the SCORECARD's stated "verified commit" 556c24a (the register `cells.tsv` landed at 549d9ec; items cite 556c24a as the register commit — fine, but a reader running at 556c24a gets rc=1; note, not a defect).

Fixture:
```
mkdir -p $S/fx; python3 -B $L/tests/fixtures/r40-c1-evidence.py --work $S/fx
case-bound-item-closed=PASS … case-r39-control-closes-forged=PASS   (8 cases)
SUMMARY cases=8 pass=8 fail=0      rc=0
```
(`--work` must pre-exist: nonexistent dir -> `usage: --work must name an existing directory`, rc=2 — I hit this first.)

## 2. Attacks
Attacked: `c1-counter.py:235-260 evaluate_item` (esp. 253-258), `:158-176 parse_register`, `:179-232 register_leg`, fixture `tests/fixtures/r40-c1-evidence.py:66-100 build_repo`, `:130-206 run_cases`.

### A1 — evidence pointer is never checked for content (wrong/weak contract) — FINDING, not a prereg falsifier
`evaluate_item` only requires: evidence rev resolves, is ancestor of --rev, `git show rev:path` returns 0, and the 40-hex appears on the closing line. Synthetic repo `$S/fix` (HEAD ce2791f, claims.md line `FORGE-A cases=7 (made up) <c0 hash>`), items with evidence `receipts/unrelated.txt@c0`, `dirpath@c0` (a DIRECTORY), `claims.md@c0` (file lacking the token):
```
python3 -B $L/census/round-40/c1-counter.py --root $S/fix --rev ce2791f1ee4887f515e18d9e6f41ed3dea05edb4 --items $S/items.tsv --register reg.tsv --scratch $S
ITEM A-UNRELATED CLOSED
ITEM A-DIR CLOSED
ITEM A-SELF CLOSED
```
All three close with a made-up claim and a real ancestor hash. `git show rev:<dir>` succeeds on trees, so a directory counts as "path exists" (`c1-counter.py:257`). The prereg literal ("forged token-only item remains OPEN"; "resolvable, revision-bound evidence pointer") is met by the letter, but the pointer need not support the claim. The shipped real items do (rows=178 in census-after.txt@6ded124, legs=7 in c2-after.txt, commit_hashes= in c1-counter.py@8a5fbdb: grep counts 1,1,2) but the counter does not enforce it.

### A2 — fixture's resolve/ancestor/path cases are masked by NOT-BOUND (vacuous cases) — FALSIFIED (fixture cannot fail on those checks)
All three fixture forged items anchor on `FORGED-CLAIM`, whose line cites only c0, so FORGE-UNRESOLVED / FORGE-NONANCESTOR end OPEN via `EVIDENCE-NOT-BOUND` whatever the earlier checks do. Mutants of the counter (copies in `$S/mut`), run through the fixture:
```
python3 -B $L/tests/fixtures/r40-c1-evidence.py --counter $S/mut/<m>.py --work $S/fx2 | grep -E "FAIL|SUMMARY"
m1 no strict-descendant test      -> fail=1 (killed)     m2 no equal test       -> fail=1 (killed)
m3 no EVIDENCE-NOT-BOUND test     -> fail=2 (killed)
m4 no evidence-ancestor check     -> SUMMARY cases=8 pass=8 fail=0  SURVIVES
m5 no evidence-resolve check      -> pass=8  SURVIVES (fail-safe equivalent: merge-base on unresolved rev still rejects)
m6 no evidence-path-exists check  -> pass=8  SURVIVES
m7 no commit-ancestor-of-rev (register) -> pass=8 SURVIVES
m8 empty-commit row not rejected  -> pass=8  SURVIVES
m9 mustnot ignored                -> pass=8  SURVIVES
```
Concrete harm demo for m4: claim line citing a side-branch hash, evidence `claims.md@SIDE`:
```
== c1-counter.py (landed)        ITEM NA OPEN EVIDENCE-NOT-ANCESTOR d538c322…
== m4-no-ancestor-ev.py          ITEM NA CLOSED
```
So the claim "forged non-ancestor stays OPEN" is only tested through the wrong mechanism; deleting the ancestor test is undetected by the committed fixture (on the real forged.tsv, m4 still OPEN via PATH-ABSENT, m5/m6 OPEN via other legs — the real control is also not discriminating for those legs). Neither the real-lane `c1-forged.tsv` nor the fixture has a forged item that cites its own hash on the closing line yet fails only on resolve/ancestor/path.

### A3 — checked and SAFE
Strict-descendant rejection: fixture cases register-equal / register-backwards pass, and mutants m1/m2 are killed. Any git error on `merge-base --is-ancestor` (rc 128) counts as not-ancestor (fail-safe). Register leg re-runs the frozen reconciler which itself requires 40-hex receipt_rev (reconcile.py:163), so symbolic receipt_rev cannot slip through.

## 3. Verdict
- C1 prereg predicate as literally stated on the shipped control/items: SAFE (command in §1, rc=0; forged_closed=0).
- C1 instrument quality: FALSIFIED in two respects — (A1) evidence content/type is unchecked: a directory or unrelated path with any real ancestor hash closes a made-up claim; (A2) the fixture and the shipped forged set do not isolate resolve/ancestor/path checks (mutants m4,m6,m7,m8,m9 survive the fixture; m4 closes an item with a non-ancestor evidence rev).

## 4. Install log / hygiene
No installs. No pacman. Wrote only this report and scratch. Scratch `/fast/scratch/hyaku/souji-r40/w2/R40w2executor01`: see removal line below.
Scratch removed: yes (rm -rf, verified absent).
