# R40w2critic02 — C1 causal separability (falsify)

Seat: R40w2critic02 (role critic, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Landed instrument commit: `128e412b0ced3c243dc27c3dd3332054a611bc2e`. Base: `0242085909fb6a4ee041c5443d76316ac6d59d4b`.
Lane HEAD read at report time: `549d9ec` (later than the landed instrument; it adds the r40 C1 item set).
Frozen predicate read first: `census/round-40/preregistration.txt` (C1 section; not edited).

## Question attacked

C1 (`census/round-40/c1-counter.py` + `tests/fixtures/r40-c1-evidence.py`) must be verifiable WITHOUT C2
(`census/round-40/c2-counter.py`, `census/round-40/docstring-classes.py`, `tests/fixtures/r40-docstring-joined.py`)
and C3 (`census/round-40/c3-counter.py`, `tests/fixtures/r40-drift-record-branches.py`) having landed.
Built a revision holding only the C1 files, ran the C1 arm there, and checked the C1 item set as committed.

## Verdict

- **A. The C1 instrument (counter + fixture) is causally separable: SAFE.** At a revision whose only r40 files are the
  C1 files, the counter closes the honest bound item, keeps the forged token-only item OPEN, reports a clean register,
  and the fixture reports `SUMMARY cases=8 pass=8 fail=0`. Neither C1 file reads any C2/C3 file (§1, §3a, §3b).
- **B. The C1 MEASUREMENT as committed is NOT separable: FALSIFIED.** The C1 item set landed in `549d9ec`
  (`census/round-40/c1-items.tsv`, `SCORECARD.md` lines 783–785). All three items close at HEAD only because their
  evidence pointers name C2/C3-era receipts and commits: D1 and D2 pin `6ded1248…`, the commit that adds
  `records/c2-after.txt` and `records/c3-after.txt`; D2 is itself a C2 claim (`legs=7`); D3 pins `8a5fbdb…`, which
  changes `census/round-40/c2-counter.py` and `c3-counter.py`. With C2/C3 absent, D2 and D3 cannot close (evidence
  revision not an ancestor / path absent). §4 has the commands and output.
- **C. Incidental FALSIFIED (C1 calibration):** the "bound" predicate is a substring test; a token-only line that merely
  mentions an ancestor's 40-hex CLOSES (§5).

## 1. What the C1 arm reads (file:line, bytes at `128e412`)

`census/round-40/c1-counter.py`:
- `:181` `git_show(root, rev, "tools/souji-citation-reconcile.py")` — frozen reconciler from `--rev` (a base file).
- `:184` `git_show(root, register_rev, register)` — the register TSV at `register_rev` (defaults to `--rev`).
- `:191-204` one subprocess: the reconciler, with the same repo and register. Its output is parsed at `:205`.
- `:237` `git_show(root, rev, row["file"])` — each item's file at `--rev`.
- `:252-256` evidence revision resolves, is an ancestor of `--rev` (`merge-base --is-ancestor`), and the evidence path exists at it.
- `:258-259` the bound check: `any(evidence_rev.lower() in line.lower() for line in good)` (substring, see §5).
- `:221,225,229` register: equal / not strict descendant / not ancestor of `--rev`.
- `:297` scratch defaults to `$TMPDIR`, else `/var/tmp`.
- Caller-supplied inputs: `--items`, `--forged`, `--register`. No other repo path is named.

`tests/fixtures/r40-c1-evidence.py`:
- `:44` `RECONCILER = "tools/souji-citation-reconcile.py"`; `:75-77` reads the reconciler from the LANE WORKING TREE
  (`os.path.join(lane_root, RECONCILER)`), not committed bytes.
- `:78-94` builds its own synthetic repo in scratch.
- `:216-217` reads `census/round-40/c1-counter.py` and the base `census/round-39/c1-counter.py`.
- `:191-203` the r39 control runs `census/round-39/c1-counter.py` (present at base).

Checks: `git show 128e412:census/round-40/c1-counter.py | grep -nE 'docstring|c2-|c3-|r40-drift|round-40/'` matches only
the docstring (`:2`, `:37`). The fixture grep matches only `:44`, `:76-77`, `:216-217`. The base reconciler names no
`census/`, `round-` or `.ufo` path: `git show 0242085:tools/souji-citation-reconcile.py | grep -nE 'round-|census|\.ufo|/tmp'` → no output.

## 2. Scratch C1-only revision

Clone of the lane at base; C1 files committed on top. The commit uses a throwaway fixture identity
(`fixture@example.invalid`) and exists only in the scratch clone. Check: `git -C "$D" rev-parse --show-toplevel` == `$D`.

```
S=/fast/scratch/hyaku/souji-r40/w2/R40w2critic02; D=$S/c1only
L=/home/vgpnk/Projects/shokunin/souji-shokunin
LAND=128e412b0ced3c243dc27c3dd3332054a611bc2e; BASE=0242085909fb6a4ee041c5443d76316ac6d59d4b
git clone -q --no-hardlinks $L $D && git -C $D rev-parse --show-toplevel && git -C $D checkout -q --detach $BASE
mkdir -p $D/census/round-40 $D/tests/fixtures
git -C $D show $LAND:census/round-40/c1-counter.py > $D/census/round-40/c1-counter.py
git -C $D show $LAND:census/round-40/preregistration.txt > $D/census/round-40/preregistration.txt
git -C $D show $LAND:tests/fixtures/r40-c1-evidence.py > $D/tests/fixtures/r40-c1-evidence.py
printf '# scratch C1-only closure lines (critic-made test input, not a lane artifact)\nR40-C1-01 CLOSED cases=7 bound to %s\nR40-FORGE cases=7\n' $BASE > $D/census/round-40/c1-closures.txt
git -C $D add census/round-40/c1-counter.py census/round-40/preregistration.txt census/round-40/c1-closures.txt tests/fixtures/r40-c1-evidence.py
git -C $D -c user.name=fixture -c user.email=fixture@example.invalid commit -q -m "scratch: C1-only revision"
```
Result: `C1REV=c7199fa721fc64431725baff9f878453357db999`; `git diff --stat $BASE $C1REV` → 4 files, 613 insertions.
`ls` of `census/round-40` and `tests/fixtures` shows no c2/c3/docstring/branches file. `git status --short` → clean.

Items fed to the counter:
- `items-honest.tsv`: `R40-C1-01 | census/round-40/c1-closures.txt | R40-C1-01 | CLOSED,cases=7 | - | census/round-39/c1-items.tsv@0242085…`
- `items-forge.tsv`: `R40-FORGE | census/round-40/c1-closures.txt | R40-FORGE | cases=7 | - | census/round-39/c1-items.tsv@0242085…`
- `items-r39-6col.tsv`: the 16 rows of `census/round-39/c1-items.tsv` (base), evidence column set to `census/round-39/c1-items.tsv@0242085…`
  (converted by a scratch python one-liner).
- Register: `census/round-39/cells.tsv` (base, 6 rows).

## 3. Commands and real output

### 3a. C1-only revision: honest bound item + forged token-only item
```
TMPDIR=$S/scr-c1 python3 -B $D/census/round-40/c1-counter.py --root $D --rev $C1REV --items $S/items-honest.tsv --forged $S/items-forge.tsv --register census/round-39/cells.tsv --scratch $S/scr-c1 --min-cells 1 --min-commit-rows 1; echo "rc=$?"
```
```
ITEM R40-C1-01 CLOSED
FORGED R40-FORGE OPEN EVIDENCE-NOT-BOUND 0242085909fb6a4ee041c5443d76316ac6d59d4b
REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok
SUMMARY items=1 open=0 forged=1 forged_open=1 forged_closed=0 register_cells=6 register_mismatches=0 register_violations=0 commit_rows=6 commit_hashes=1 items_sha=095977cbaae6 forged_sha=3ea9baba9552
rc=0
```

### 3b. C1-only fixture (no C2/C3 file present)
```
TMPDIR=$S/work-c1 python3 -B $D/tests/fixtures/r40-c1-evidence.py --work $S/work-c1
```
```
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
The fixture removed its own scratch (`ls $S/work-c1 | wc -l` → 0).

### 3c. C1-only revision, the 16 r39 item rows (no closure lines at that rev)
```
TMPDIR=$S/scr-c1 python3 -B $D/census/round-40/c1-counter.py --root $D --rev $C1REV --items $S/items-r39-6col.tsv --register census/round-39/cells.tsv --scratch $S/scr-c1 --min-cells 1 --min-commit-rows 1; echo "rc=$?"
```
```
ITEM R39-C1-01 OPEN EVIDENCE-NOT-BOUND 0242085909fb6a4ee041c5443d76316ac6d59d4b
… (all 16 rows identical in form)
REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok
SUMMARY items=16 open=16 forged=0 forged_open=0 forged_closed=0 register_cells=6 register_mismatches=0 register_violations=0 commit_rows=6 commit_hashes=1 items_sha=67a13472e088 forged_sha=-
rc=1
```
Same result against the landed rev (`$S/bin/c1-counter-landed.py`, extracted from `git show 128e412:census/round-40/c1-counter.py`):
`python3 -B $S/bin/c1-counter-landed.py --root $L --rev $LAND --items $S/items-r39-6col.tsv --register census/round-39/cells.tsv --scratch $S/scr-lane --min-cells 1 --min-commit-rows 1` → `SUMMARY items=16 open=16 … rc=1`.
Per-item run at `$LAND` with each row's own in-line 40-hex ancestor (where one exists on its anchor line): `R39-C1-04`→`2f6e981…`,
`R39-C1-11`→`861c2ba…`, `R39-C1-12`→`02b43398…`, `R39-C1-13`→`861c2ba…` CLOSE; the other 12 stay `OPEN EVIDENCE-NOT-BOUND`
(`SUMMARY items=16 open=12 … rc=1`).

### 3d. The C1 item set as committed at HEAD (`549d9ec`): the coupling test
`git -C $L show --stat --format='%h %s' 549d9ec` →
```
549d9ec round-40: C1 closure cells and bound register
 SCORECARD.md                  | 6 ++++++
 census/round-40/c1-forged.tsv | 4 ++++
 census/round-40/c1-items.tsv  | 4 ++++
 census/round-40/cells.tsv     | 4 ++++
 4 files changed, 18 insertions(+)
```
The committed items (`git -C $L show HEAD:census/round-40/c1-items.tsv`):
```
R40-CLAIM-D1  SCORECARD.md  R40-CLAIM-D1  rows=178,W04=49  rows=173  census/round-40/records/census-after.txt@6ded1248b6d0005ac31ff2e1c867ecb0a075ab39
R40-CLAIM-D2  SCORECARD.md  R40-CLAIM-D2  8a5fbdbddaab24c5ba43fc6a133499efb405f214,legs=7  legs=6  census/round-40/records/c2-after.txt@6ded1248b6d0005ac31ff2e1c867ecb0a075ab39
R40-CLAIM-D3  SCORECARD.md  R40-CLAIM-D3  commit_rows=,commit_hashes=  commit_distinct=  census/round-40/c1-counter.py@8a5fbdbddaab24c5ba43fc6a133499efb405f214
```
The SCORECARD lines (`SCORECARD.md:783-785`) say D2 is "the C2 leg receipt `census/round-40/records/c2-after.txt`" and D1/D2 are committed at `6ded124`.
Forged items (`census/round-40/c1-forged.tsv`): `R40-FORGE-UNCITED` (evidence `c1-counter.py@8a5fbdb`), `R40-FORGE-UNRESOLVED` (`@000…0`), `R40-FORGE-NONANCESTOR` (`@002d6a2…`).

Run at HEAD, the committed bytes (`git -C $L show HEAD:census/round-40/c1-counter.py > $S/bin/c1-counter-head.py`; `c1-counter.py` unchanged `128e412..HEAD`):
```
python3 -B $S/bin/c1-counter-head.py --root $L --rev 549d9ec… --items <HEAD c1-items.tsv> --forged <HEAD c1-forged.tsv> --register census/round-39/cells.tsv --scratch $S/scr-lane --min-cells 1 --min-commit-rows 1
```
```
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND 8a5fbdbddaab24c5ba43fc6a133499efb405f214
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-ANCESTOR 002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0
REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=6 register_mismatches=0 register_violations=0 commit_rows=6 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6
rc=0
```
Same committed items on the C1-only revision (`--rev $C1REV`): all three `ANCHOR-ABSENT` (their SCORECARD lines post-date it), forged `EVIDENCE-NOT-ANCESTOR` / `ANCHOR-ABSENT`, `rc=1`.

Ancestry facts used in the coupling argument:
- `git -C $L merge-base --is-ancestor 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39 128e412…` → **no** (6ded124 is a descendant of the instrument commit).
- `git -C $L merge-base --is-ancestor 8a5fbdbddaab24c5ba43fc6a133499efb405f214 128e412…` → **no**.
- `git -C $L show --stat --format= 8a5fbdb` → `census/round-40/c2-counter.py | 59 …`, `census/round-40/c3-counter.py | 4 +--`.
- `git -C $L show --stat 6ded124` (per `census/round-40/records/` listing) adds `c2-after.txt`, `c3-after.txt`, `census-after.txt`, `fixtures-after.txt`, `c1-control.txt`.

### 3e. Landed rev holds no r40 record or item file
`git -C $L ls-tree -r --name-only 128e412b0ced3c243dc27c3dd3332054a611bc2e -- census/round-40/records | wc -l` → `0`.
The r40 records and the C1 item set are later commits (`6ded124`, `549d9ec`).

## 4. Findings (file:line)

- **F1 — counter/fixture separability: SAFE.** §3a/§3b: C1-only revision, C2/C3 absent, all C1 assertions hold. The arm reads
  only the items/forged/register TSVs, `tools/souji-citation-reconcile.py` at `--rev` (base), `census/round-39/cells.tsv`, the
  git object store (`c1-counter.py:181,184,191-204,237,252-256`), and (fixture only) the base r39 counter (`r40-c1-evidence.py:216-217`).
- **F2 — the C1 measurement is coupled to C2/C3 artifacts: FALSIFIED.** §3d: the committed C1 items at `549d9ec` close only
  against `6ded124` (C2 leg receipt, C3-era receipts) and `8a5fbdb` (a commit that changes the C2 and C3 counters). D2 is a
  C2 claim whose only closing evidence is the C2 receipt. The preregistration requires the claims to be "independently
  measurable"; with C2/C3 receipts and commits absent, D1/D2/D3 cannot close. The counter's code does not read C2/C3 files;
  the coupling lives in the item rows' evidence pointers and in the choice of evidence revision.
- **F3 — the r39 item set at landed rev: 16/16 OPEN with base evidence; 4/16 with each row's own in-line 40-hex** (§3c). The
  preregistration's "every item closed" target is met only by the r40 item set at HEAD (§3d), not by the r39 rows.
- **F4 — fixture reads the reconciler from the working tree** (`r40-c1-evidence.py:75-77`). Minor: a dirty lane changes what
  the fixture tests.
- **F5 — hardcoded scratch fallback** `c1-counter.py:297` → `/var/tmp`. Minor; the preregistration asks for no hardcoded `/tmp`.
- **F6 — bound check is substring, not claim binding (FALSIFIED, §5).** `c1-counter.py:258-259`. The fixture's forged cases
  (`r40-c1-evidence.py:80`, `:139-146`) contain no 40-hex, so the fixture cannot see this.

## 5. Falsifier for F6 (reproduced in scratch)

Commit `5354f780b36378b60a8d6153cad5d5fd0f5957dc` (scratch clone only) appends one line to `census/round-40/c1-closures.txt`:
`R40-STAMP cases=7 unrelated sentence that only mentions the base revision 0242085909fb6a4ee041c5443d76316ac6d59d4b`
```
python3 -B $D/census/round-40/c1-counter.py --root $D --rev 5354f780b36378b60a8d6153cad5d5fd0f5957dc --items $S/items-stamp.tsv --register census/round-39/cells.tsv --scratch $S/scr-c1 --min-cells 1 --min-commit-rows 1; echo "rc=$?"
```
(`items-stamp.tsv`: `R40-STAMP | census/round-40/c1-closures.txt | R40-STAMP | cases=7 | - | census/round-39/c1-items.tsv@0242085…`)
```
ITEM R40-STAMP CLOSED
REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok
SUMMARY items=1 open=0 forged=0 forged_open=0 forged_closed=0 register_cells=6 register_mismatches=0 register_violations=0 commit_rows=6 commit_hashes=1 items_sha=7144a7ba5f5a forged_sha=-
rc=0
```
The fixture still reports `SUMMARY cases=8 pass=8 fail=0` at this commit.

## 6. Scope notes

- No lane file was edited; no lane commit was made; no git mutation in the lane. Scratch commits (`c7199fa…`, `5354f78…`) are
  throwaway; the `git commit` calls used the fixture identity `fixture@example.invalid` inside the scratch clone only.
- Installs: none. No tool installed or updated; no pacman transaction.
- C2 and C3 arms were not attacked (outside this seat's question).

## 7. Re-run (for the L1)

Rebuild `$D` per §2 with a fresh `S`, then run §3a, §3b, §3c, §3d (HEAD items via `git show HEAD:…`) and §5. Each run takes about two seconds.

## 8. Scratch

`/fast/scratch/hyaku/souji-r40/w2/R40w2critic02/` removed by this seat before yield (`rm -rf -- "$S"`).
