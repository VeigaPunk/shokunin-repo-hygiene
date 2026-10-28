# R40w2critic01 — attack on the frozen C1 predicate's satisfiability

Seat: R40w2critic01 (critic, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Landed instrument commit: `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Lane HEAD at measurement: `549d9ec53a1f5932337ff14438fcd22b0621828d`.
Preregistration (frozen, unedited): `census/round-40/preregistration.txt`, sha256 `7218101a24a48ce8648e9625c992af1aa972d0e4274f17044e185ac0b3b4758c`, identical at 128e412 and the working tree.

## Frozen sentence under attack

`census/round-40/preregistration.txt`, line 4 (C1 Predicate/Target): the counter "reports every item closed, zero unbound evidence pointers, zero register mismatches, and the forged token-only item remains OPEN"; kill if "the forged line closes, a backwards/equal commit passes, or any existing valid row is rejected".

## Bytes checked

- `census/round-40/c1-counter.py` at 128e412 is byte-identical to the HEAD working tree (`git diff --quiet 128e412 HEAD -- census/round-40/c1-counter.py` rc=0; both sha256 prefix `f1f9b3d8c8d22225`). Commits after landing (`8a5fbdb`, `556c24a`, `6ded124`, `549d9ec`) touch records and items only, not the counter.
- Counter line anchors below are the 128e412 bytes.

## Answer to the question

The frozen sentence IS satisfiable in one run of the landed counter, and the two halves are carried by different fields:

| half | where it is reported | gate that enforces it |
|---|---|---|
| every real item CLOSED | `ITEM <id> CLOSED` lines; `SUMMARY ... items=N open=0` | `open_count == 0` (c1-counter.py:336) |
| forged token-only item stays OPEN | `FORGED <id> OPEN EVIDENCE-NOT-BOUND ...` lines; `SUMMARY ... forged=M forged_open=K forged_closed=0` | `forged_closed == 0` only (c1-counter.py:337) |

The forged half must be supplied through `--forged` (a separate file). If the forged row is placed in `--items`, it is counted in `open=` and the run exits 1 (command T4 and probe C below). So the two-file split is required, and it is the only layout in which both halves can be true in one run.

The forged half is NOT enforced when the forged set is absent or empty of forgeries, and it is NOT enforced by reason. Both are falsifiers (probes B and D).

## Commands and real output

Setup (scratch paths are the seat scratch, deleted at end; item files reproduced here so the L1 can recreate them). `B=0242085909fb6a4ee041c5443d76316ac6d59d4b`, `R=128e412b0ced3c243dc27c3dd3332054a611bc2e`, `L=/home/vgpnk/Projects/shokunin/souji-shokunin`, `S=<any absolute scratch dir>`:

```
printf 'id\tfile\tanchor\tmust\tmustnot\tevidence\nPRE-BASE\tcensus/round-40/preregistration.txt\tBase branch revision\tround-39,verified,tip\t-\tcensus/round-39/preregistration.txt@%s\n' "$B" > "$S/items-real.tsv"
printf 'id\tfile\tanchor\tmust\tmustnot\tevidence\nFORGE-C1\tcensus/round-40/preregistration.txt\t## C1\tcalibration\t-\tcensus/round-39/preregistration.txt@%s\n' "$B" > "$S/forged.tsv"
printf 'id\tfile\tanchor\tmust\tmustnot\tevidence\nPRE-BASE\tcensus/round-40/preregistration.txt\tBase branch revision\tround-39,verified,tip\t-\tcensus/round-39/preregistration.txt@%s\nFORGE-C1\tcensus/round-40/preregistration.txt\t## C1\tcalibration\t-\tcensus/round-39/preregistration.txt@%s\n' "$B" "$B" > "$S/single-file.tsv"
printf 'id\tfile\tanchor\tmust\tmustnot\tevidence\nFORGE-TYPO\tcensus/round-40/preregistration.txt\t## C1\tcalibrationXX\t-\tcensus/round-39/preregistration.txt@%s\n' "$B" > "$S/forged-typo.tsv"
C="python3 -B $L/census/round-40/c1-counter.py --root $L --rev $R --register census/round-39/cells.tsv --register-rev $R --min-cells 1 --min-commit-rows 1 --scratch $S"
```

(`--scratch` must be an existing directory; the counter writes only there and `rmtree`s it.)

A. Two-file, real items + forged file (satisfiability):
```
$C --items $S/items-real.tsv --forged $S/forged.tsv; echo rc=$?
ITEM PRE-BASE CLOSED
FORGED FORGE-C1 OPEN EVIDENCE-NOT-BOUND 0242085909fb6a4ee041c5443d76316ac6d59d4b
REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok
SUMMARY items=1 open=0 forged=1 forged_open=1 forged_closed=0 register_cells=6 register_mismatches=0 register_violations=0 commit_rows=6 commit_hashes=1 items_sha=819d52274694 forged_sha=5b24ac481c7e
rc=0
```
Result: satisfiable. `open=0` and `forged_closed=0` with `forged_open=1`, rc 0.

B. Real items only, no `--forged` (VACUOUS PASS):
```
$C --items $S/items-real.tsv; echo rc=$?
ITEM PRE-BASE CLOSED
REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok
SUMMARY items=1 open=0 forged=0 forged_open=0 forged_closed=0 ... forged_sha=-
rc=0
```
Result: exit 0 with zero forged rows examined. The sentence's "forged token-only item remains OPEN" is never tested. Nothing in the gate (c1-counter.py:335-343) requires `forged >= 1`. A harness reading rc=0 as "forged stayed OPEN" is wrong.

C. Single file holding both rows:
```
$C --items $S/single-file.tsv; echo rc=$?
ITEM PRE-BASE CLOSED
ITEM FORGE-C1 OPEN EVIDENCE-NOT-BOUND 0242085909fb6a4ee041c5443d76316ac6d59d4b
SUMMARY items=2 open=1 forged=0 forged_open=0 forged_closed=0 ...
rc=1
```
Result: the forged row is counted in `open=`. The sentence cannot be satisfied in one file (expected; this is why `--forged` exists).

D. Forged row that is OPEN for the WRONG reason (VACUOUS PASS on the reason):
```
$C --items $S/items-real.tsv --forged $S/forged-typo.tsv; echo rc=$?
ITEM PRE-BASE CLOSED
FORGED FORGE-TYPO OPEN PREDICATE-MISSING missing=['calibrationXX'] hits=1
SUMMARY items=1 open=0 forged=1 forged_open=1 forged_closed=0 ...
rc=0
```
Result: a row that is not token-only (its predicate fails) satisfies `forged_open=1`, rc 0. The gate counts any OPEN reason; it never checks that the forged row is OPEN with `EVIDENCE-NOT-BOUND`. A typo in a forged row makes the forged half pass. (The forged-half closure gate is correct: a closed forged row gives rc 1, see T4's sibling logic at line 337.)

E. Forged-only file as `--items` (control shape check):
```
$C --items $S/forged.tsv; echo rc=$?
ITEM FORGE-C1 OPEN EVIDENCE-NOT-BOUND 0242085909fb6a4ee041c5443d76316ac6d59d4b
SUMMARY items=1 open=1 forged=0 ...
rc=1
```

F. Same file as `--items` and `--forged` (the shape recorded in `census/round-40/records/c1-control.txt:11-14`):
```
$C --items $S/same.tsv --forged $S/same.tsv; echo rc=$?
ITEM FORGE-C1 OPEN EVIDENCE-NOT-BOUND ...
FORGED FORGE-C1 OPEN EVIDENCE-NOT-BOUND ...
SUMMARY items=1 open=1 forged=1 forged_open=1 forged_closed=0 ...
rc=1
```
Result: the recorded control receipt is rc 1 by construction (`open=1`), and it names `--rev 0242085909fb6a4ee041c5443d76316ac6d59d4b` (the BASE), not an after revision.

### Real and forged sets committed later (lane HEAD)

The round's actual two-file set exists only at HEAD (`549d9ec`, added after landing): `census/round-40/c1-items.tsv` (`R40-CLAIM-D1..D3`) and `census/round-40/c1-forged.tsv` (`R40-FORGE-UNCITED`, `-UNRESOLVED`, `-NONANCESTOR`). The landed tree has neither file (`git cat-file -e 128e412:census/round-40/c1-items.tsv` fails).

T1. Landed counter, two-file real + forged, at HEAD, register at HEAD:
```
python3 -B $S/c1-counter-landed.py --root $L --rev 549d9ec53a1f5932337ff14438fcd22b0621828d --items $S/c1-items.tsv --forged $S/c1-forged.tsv --register census/round-39/cells.tsv --register-rev 549d9ec53a1f5932337ff14438fcd22b0621828d --min-cells 1 --min-commit-rows 1 --scratch $S
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND 8a5fbdbddaab24c5ba43fc6a133499efb405f214
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-ANCESTOR 002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0
REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 ... items_sha=8f97b0097e09 forged_sha=915b1184e9c6
rc=0
```
Result: satisfiable on the round's real set. The token-only forgery (`R40-FORGE-UNCITED`, line `LOG.md` `R39-REG-11` with `cases=7`) reaches the evidence arm, so its token predicate passed; it stays OPEN for the right reason. Note `forged_open=3` counts all three forgeries, not only the token-only one; the token-only row cannot be isolated from the SUMMARY.

T2. Same counter at the LANDED revision `128e412`:
```
... --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e ...
ITEM R40-CLAIM-D1 OPEN ANCHOR-ABSENT
ITEM R40-CLAIM-D2 OPEN ANCHOR-ABSENT
ITEM R40-CLAIM-D3 OPEN ANCHOR-ABSENT
... SUMMARY items=3 open=3 forged=3 forged_open=3 forged_closed=0 ...
rc=1
```
Result: the real set cannot be evaluated at the landed revision (its anchors and evidence postdate it). The "after" revision is HEAD, not 128e412. The preregistration requires the base and after revisions to be named; no receipt in the lane names an after revision for C1 (`git grep` for `items=3`/`c1-items` in `census/round-40/records` returns nothing).

T3. Real set at HEAD without `--forged`:
```
... --items c1-items.tsv (no --forged) ...
SUMMARY items=3 open=0 forged=0 forged_open=0 forged_closed=0 ...
rc=0
```
Same vacuous pass as B on the real set.

T4. Forged file passed as `--items`: `SUMMARY items=3 open=3 forged=0 ...`, rc 1. Fine (the forged rows cannot pass as items).

## Additional attack: existence-only evidence arm (strength, not literal falsifier)

Fixture repo under scratch (`git -C "$D" rev-parse --show-toplevel` asserted equal to `$D` before every commit). `claims.md` at C1 carries `R40-CLAIM-X rows=178 measured below (see <C0>)`; the evidence pointer is `unrelated.txt@<C0>` where `unrelated.txt` reads `nothing to do with any count`. Counter item line: `EXIST-ONLY  claims.md  R40-CLAIM-X  rows=178  -  unrelated.txt@<C0>`.
Output: `ITEM EXIST-ONLY CLOSED`.
Result: `evaluate_item` (c1-counter.py:254-259) checks the evidence path only for existence at the evidence revision and that the revision string appears on the line; it never checks that the cited file supports the claim. The frozen wording "resolvable, revision-bound" is met literally. The round's own lesson (`corpus/lessons/round-40.md`, Frontier) admits a related gap: the ancestor check at line 254 is non-strict ("accepts any resolvable ancestor"). Recorded as a strength gap, not a frozen-predicate falsifier.

## Fixture gap (for the fixture's own assertion)

`tests/fixtures/r40-c1-evidence.py:158-161` (`forged_open`) asserts only the substring `" OPEN "`. It does not check `EVIDENCE-NOT-BOUND`. Probe D (wrong-reason OPEN passes rc 0) is therefore not caught by the fixture's `forged-token-only-open` case (line 164). Fixture run at 128e412 with the landed counter: `case-...=PASS` for all 8 cases, `SUMMARY cases=8 pass=8 fail=0`, rc 0 (command `python3 -B $L/tests/fixtures/r40-c1-evidence.py --counter <landed counter copy> --base-counter $L/census/round-39/c1-counter.py --work <scratch>`).

## Register leg (checked only as a precondition; not attacked further)

`register_leg` at c1-counter.py:179; equal check line 221, strict-descendant check line 225. The fixture's `register-equal-rejected` and `register-backwards-rejected` cases pass. Not independently re-attacked here.

## Verdict

**FALSIFIED** (the frozen sentence is satisfiable, but the landed counter does not enforce its forged half):

- SAFE part: satisfiability in one run with two files (probe A; T1). `open=0` carries "every real item closed"; `forged_open=N forged_closed=0` carries "forged stays OPEN"; rc 0.
- FALSIFIED part: the exit gate (c1-counter.py:335-343) does not require any forged row (probe B; T3: rc 0 with `forged=0`), and does not require the forged row's reason to be `EVIDENCE-NOT-BOUND` (probe D: rc 0 with `PREDICATE-MISSING`).
- Measurement gap: no receipt in the lane measures the real two-file set at an after revision (T2 vs T1); the recorded control (`census/round-40/records/c1-control.txt`) is at the base revision and has `open=1` by construction.

Kill-condition status: "forged line closes" is caught (forged_closed gate) when a forged row is supplied. "Forged stays OPEN" is not caught when it is absent or wrong-reason.

Smallest safe correction (for the next round, not applied): require `forged >= 1` and `forged_open >= 1` in the gate, and assert the `EVIDENCE-NOT-BOUND` reason for the token-only row in the fixture.

## Hygiene

- Read-only against the lane: `git show`, `git cat-file`, `git merge-base`, `git grep`, `git diff`, `git ls-tree` only. Counter runs wrote only to seat scratch.
- Fixture repo: `git init` in seat scratch, toplevel asserted before commits, identity supplied by env only.
- Installs: none. No pacman. No `~/.local/bin` writes.
- Scratch dir `/fast/scratch/hyaku/souji-r40/w2/R40w2critic01` removed: YES (verified `test ! -e`).
- No write to counters, fixtures, preregistration, SCORECARD.md, LOG.md, corpus/, or any committed file.
