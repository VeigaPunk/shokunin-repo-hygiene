# R40w2revenger04 — falsify r40 C1/C2/C3 and the r39 routed defects D1–D3

Seat: `R40w2revenger04` (revenger, leaf, no dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Preregistration (frozen, not edited): `census/round-40/preregistration.txt`. Routed defects: `corpus/lessons/round-39-verifier-spotcheck.md` lines 135 (D1), 141 (D2), 147 (D3).

## Verdicts

| target | verdict | one-line reason |
|---|---|---|
| C1 calibration | **FALSIFIED** | At the tip the counter closes an item whose cited evidence file does not contain the claimed value (`ITEM ID-X CLOSED`, §C1-2; real repo `ITEM ATT-D3-RECEIPT CLOSED`, §C1-3). At the landed instrument commit a line carrying only a bare revision id closed (`ITEM ID-Y CLOSED`, §C1-1). The landed hole was repaired at `994de3b`; the content hole was not. |
| C2 operability | **SAFE** on the frozen predicate; the broader kill clause is **FALSIFIED** by a documented-class mismatch outside the frozen pairs (ENOTDIR, §C2-3) | L4/L4b/L5/L6 pass at the tip; the joined analyser is not the r39 bytes (control arm is a re-implementation, §C2-4). |
| C3 coverage | **SAFE** | pristine 8/8, 4/4 mutants killed, `base_killed=0`, at both `128e412` and `994de3b`. |
| D1 "after" census receipt stale by one row | **PARTLY CLOSED** | Numbers now match the live registry (`rows=178`, `W04=49`), but the receipt's stated command (`validate`) cannot print `rows`, and its `SUMMARY` line is not script output (§D1). |
| D2 final-tip re-measure names an unmeasured revision | **CLOSED** | `c2-after.txt` names `8a5fbdb` and reproduces byte-for-byte at `994de3b` (§D2). Nit: `<scratch>` placeholder in its header. |
| D3 `commit_distinct` reads as distinct commits | **PARTLY CLOSED** | The r40 counter prints separate `commit_rows=` / `commit_hashes=` (closed as an instrument label). Its own closure line for D3 is backed by counter source text and a C3 receipt that contains no `commit_rows` token, and the C1 gate accepts that (§D3). |

Round-level: the C1 instrument is FALSIFIED. C2 and C3 hold on their frozen predicates. No consumer fixture regressed (C2 L6 pass at the tip).

## Pins and measurement discipline

- Base (prereg): `0242085909fb6a4ee041c5443d76316ac6d59d4b`.
- Landed instrument commit: `128e412b0ced3c243dc27c3dd3332054a611bc2e`.
- Commits after landing: `8a5fbdbddaab24c5ba43fc6a133499efb405f214` (counter fixes), `6ded1248b6d0005ac31ff2e1c867ecb0a075ab39` (receipts), `556c24a5cacf208c5144c459838712594a43e1f2` (QUALITY), `549d9ec53a1f5932337ff14438fcd22b0621828d` (closure cells), `994de3b447e9a7bea2abfbd80c4736f6215d3e47` (path binding, **tip measured**).
- The lane moved during this run: HEAD went from `549d9ec` to `994de3b` at 17:13, and `census/round-40/c1-counter.py` and `tests/fixtures/r40-c1-evidence.py` changed in the working tree at 17:13:30 and 17:13:57. My first C1 runs (before pinning) therefore mixed a new counter with old items and are not used as evidence, except where stated. Every number below comes from `git archive <rev>` copies of pinned revisions (`$S/t-<rev>`), never from the working tree. Uncommitted working-tree edits (`corpus/knowledge/*-r40.md`, untracked `records/*-d.txt`, `records/c1-before.txt`, `waves/`) are outside every measurement.

```
L=/home/vgpnk/Projects/shokunin/souji-shokunin
S=/fast/scratch/hyaku/souji-r40/w2/R40w2revenger04
H=994de3b447e9a7bea2abfbd80c4736f6215d3e47
LAND=128e412b0ced3c243dc27c3dd3332054a611bc2e
BASE=0242085909fb6a4ee041c5443d76316ac6d59d4b
TIP549=549d9ec53a1f5932337ff14438fcd22b0621828d
for r in $H $LAND $TIP549 $BASE; do mkdir -p $S/t-$r && git -C $L archive $r | tar -x -C $S/t-$r; done
git -C $L diff --stat 8a5fbdb $H -- census/round-40/c2-counter.py census/round-40/c3-counter.py census/round-40/docstring-classes.py tools tests/fixtures
#  -> only tests/fixtures/r40-c1-evidence.py (1 file, 8 insertions, 1 deletion) changed since 8a5fbdb
git -C $L diff --stat 128e412 $H -- corpus/SOURCES.md   # -> empty (registry unchanged since landing)
```

Lane-level commit history: `git -C $L log --oneline -6` gives `994de3b, 549d9ec, 556c24a, 6ded124, 8a5fbdb, 128e412`.

## C1 — calibration (`census/round-40/c1-counter.py`)

Predicate under attack: anchored item line must carry a resolvable, revision-bound pointer `PATH@REVISION`; a register row whose `commit` is not a strict descendant of `receipt_rev` is rejected; the forged token-only item stays OPEN.

### C1-0 Tip measurement (pinned `994de3b`, archived counter bytes, lane items)

```
$ python3 -B $S/t-$H/census/round-40/c1-counter.py --root $L --rev $H --items $S/t-$H/census/round-40/c1-items.tsv --forged $S/t-$H/census/round-40/c1-forged.tsv --register census/round-40/cells.tsv --min-cells 3 --min-commit-rows 3 --scratch $S/c1h
ITEM R40-CLAIM-D1 CLOSED
ITEM R40-CLAIM-D2 CLOSED
ITEM R40-CLAIM-D3 CLOSED
FORGED R40-FORGE-UNCITED OPEN EVIDENCE-NOT-BOUND census/round-40/c1-counter.py@8a5fbdbddaab24c5ba43fc6a133499efb405f214
FORGED R40-FORGE-UNRESOLVED OPEN EVIDENCE-REV-UNRESOLVED 0000000000000000000000000000000000000000
FORGED R40-FORGE-NONANCESTOR OPEN EVIDENCE-NOT-ANCESTOR 002d6a2478b271c7f4c9b5ba1a9d4fe16ab49fe0
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=3 open=0 forged=3 forged_open=3 forged_closed=0 register_cells=3 register_mismatches=0 register_violations=0 commit_rows=3 commit_hashes=1 items_sha=8f97b0097e09 forged_sha=915b1184e9c6
rc=0
```

The counter's own tests at the tip (`$S/t-$H/tests/fixtures/r40-c1-evidence.py --work $S/fx`): `case-forged-path-uncited-open=PASS` and `SUMMARY cases=9 pass=9 fail=0`, rc 0. That case is the repair of C1-1 below.

Control: at `128e412` (landed) the same counter bytes were run with `--rev 128e412`. Items and register did not exist at that revision (`git cat-file -e 128e412:census/round-40/c1-items.tsv` → rc 128, `… cells.tsv` → rc 128), so the landed instrument was never measured against its own items. The 549d9ec SCORECARD (`R40-CLAIM-D3` line) is `OPEN EVIDENCE-NOT-BOUND` under the tip counter (`--rev 549d9ec`, archived tip counter), because the D3 line then did not name its evidence path in backticks. The tip SCORECARD (`994de3b`) does, so the closure is now satisfiable.

### C1-1 Landed bytes (`128e412`): a bare revision id closes an item — FALSIFIED, repaired at `994de3b`

Scratch repo `$S/att-c1` (fixture, `git -C $D rev-parse --show-toplevel` = `$D` asserted before the first commit; throwaway identity `att <att@example.invalid>` used only here). Commit A holds `receipts/empty.txt` ("nothing was measured here") and `receipts/r0.txt` ("SUMMARY rows=178 pass=1"); commit B adds `ledger.md`, `cells.tsv` (one row naming `receipts/r0.txt@A`), and `tools/souji-citation-reconcile.py` (byte-identical to `$H`).

`ledger.md` lines:
```
CLAIM-X rows=178 measured; evidence `receipts/empty.txt` at <A>; receipt receipts/r0.txt
CLAIM-Y rows=178 measured; evidence pointer names only <A>; receipt receipts/r0.txt
```
`att-c1-items.tsv` rows: `ID-X ledger.md CLAIM-X rows=178 - receipts/empty.txt@A` and `ID-Y ledger.md CLAIM-Y rows=178 - receipts/empty.txt@A`.

Run with the landed bytes (`$S/t-$LAND/census/round-40/c1-counter.py`) → **FALSIFIED**:
```
ITEM ID-X CLOSED
ITEM ID-Y CLOSED
REGISTER ROW1 BACKWARDS no-commit
SUMMARY items=2 open=0 ... (rc=1 from the register row I wrote without a commit cell; not the item predicate)
```
Here `ID-Y` cites `A` only as a bare 40-hex on its line, with no `PATH` on the line. The landed closure check (`census/round-40/c1-counter.py` at `128e412`, the line `if not any(evidence_rev.lower() in line.lower() for line in good)`) accepts it. Same run with the tip counter: `ITEM ID-X CLOSED` / `ITEM ID-Y OPEN EVIDENCE-NOT-BOUND receipts/empty.txt@d4a7c7d0…`. So the landed hole is closed at `994de3b` (`census/round-40/c1-counter.py:258-263`, which requires `` `PATH` `` on the line as well as the revision).

### C1-2 Tip (`994de3b`): the evidence content is never checked — FALSIFIED (open)

Same scratch repo, run with the tip counter bytes (`$S/t-$H/census/round-40/c1-counter.py`), `--rev B`:
```
ITEM ID-X CLOSED
ITEM ID-Y OPEN EVIDENCE-NOT-BOUND receipts/empty.txt@d4a7c7d00c2f259743d672c912a6ce9f3f66c41c
```
`ID-X` closes although `receipts/empty.txt@A` does not contain `rows=178`, the value the line claims. The only test on the evidence file is existence at the evidence revision (`census/round-40/c1-counter.py:256-257`, `if git_show(root, evidence_rev, row["evidence_path"]) is None`). The must tokens are checked against the anchored line only, never against the cited file. The forged control (`c1-forged.tsv`) cannot detect this, because its forgeries all fail for other reasons. Consequence: Q89/the prereg's "resolvable, revision-bound" predicate is satisfied by a pointer to unrelated evidence.

### C1-3 Real repo at the tip: a D3 closure backed by a receipt with no `commit_rows` token — FALSIFIED

Items file `$S/att-real-items.tsv`:
```
id	file	anchor	must	mustnot	evidence
ATT-D3-RECEIPT	SCORECARD.md	R40-CLAIM-D3	commit_rows=,commit_hashes=	commit_distinct=	census/round-40/records/c3-after.txt@6ded1248b6d0005ac31ff2e1c867ecb0a075ab39
CTL-D1-UNNAMED-PATH	SCORECARD.md	R40-CLAIM-D1	rows=178,W04=49	rows=173	census/round-40/records/c3-after.txt@6ded1248b6d0005ac31ff2e1c867ecb0a075ab39
```
```
$ python3 -B $S/t-$H/census/round-40/c1-counter.py --root $L --rev $H --items $S/att-real-items.tsv --register census/round-40/cells.tsv --min-cells 1 --min-commit-rows 1 --scratch $S/att-real-work
ITEM ATT-D3-RECEIPT CLOSED
ITEM CTL-D1-UNNAMED-PATH OPEN EVIDENCE-NOT-BOUND census/round-40/records/c3-after.txt@6ded1248b6d0005ac31ff2e1c867ecb0a075ab39
REGISTER cells=3 mismatches=0 commit_rows=3 commit_hashes=1 violations=0 ok
SUMMARY items=2 open=1 ... rc=1
$ git -C $L show 6ded1248b6d0005ac31ff2e1c867ecb0a075ab39:census/round-40/records/c3-after.txt | grep -c commit_rows
0
```
`ATT-D3-RECEIPT` closes on `c3-after.txt` (the C3 receipt, zero `commit_rows` tokens) because the D3 line (`SCORECARD.md:785`) happens to name that path in backticks and the `6ded` id. The control shows the path-on-line rule is enforced; the content rule is not. The D3 closure therefore does not prove the field: the field-bearing receipt is `census/round-40/records/c1-control.txt` (lines 6–7, `commit_rows=6 commit_hashes=1`), which the D3 line does not cite.

### C1-4 Register leg (strict descendant) — SAFE (for this leg)

- Code: `census/round-40/c1-counter.py:221-228` (`commit == receipt_rev` → BACKWARDS; `is_ancestor(receipt_rev, commit)` → BACKWARDS), `:229-231` (`NOT-ANCESTOR-OF-REV`).
- Fixture (tip): `case-register-equal-rejected=PASS`, `case-register-backwards-rejected=PASS`, `case-register-clean-accepted=PASS`.
- Live rows (`census/round-40/cells.tsv`): 3 rows, `commit` `556c24a…` strict descendant of `receipt_rev` `6ded1248…` (`violations=0`).
- The reconciler reads the register from the committed tree at `--register-rev` (`tools/souji-citation-reconcile.py:38-39`, `:263-264`), so the token leg is revision-bound too. I found no falsifier here.

### C1-5 Receipt gaps (not a falsifier, but owed)

- No committed C1 "after" receipt exists. `git ls-files census/round-40/records` → `c1-control.txt, c2-after.txt, c3-after.txt, census-after.txt, fixtures-after.txt`. The only after-receipt is untracked `census/round-40/records/c1-after-d.txt` measured at `549d9ec` (not the tip). The prereg requires "r40 counter receipt, with base and after revisions explicitly named".
- `census/round-40/records/c1-control.txt` lines 2–4 use placeholders `<items5.tsv>` / `<items6.tsv>`; those files are not committed, so the control cannot be re-run from committed bytes as written. The r40 fixture does re-run the same control (`case-r39-control-closes-forged=PASS`).

## C2 — operability (`census/round-40/docstring-classes.py`, `census/round-40/c2-counter.py`)

### C2-1 Tip (`994de3b`, archived counter, `--base-rev 0242085`) — frozen predicate holds

```
$ python3 -B $S/t-$H/census/round-40/c2-counter.py --root $L --rev $H --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/c2h
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
rc=0
```
Fixtures at the tip: `tests/fixtures/r40-docstring-joined.py` → `SUMMARY cases=9 pass=9 fail=0`; the same with `--one-line` → `SUMMARY cases=9 pass=6 fail=3` rc 1 (`case-frozen-pairs-present=FAIL missing=['RECORD-OUTSIDE-ROOT(--root)']`, `case-outside-root-trigger-primary=FAIL`), so the joined reading is load-bearing.

Wrapped-trigger mechanism checked: `census/round-40/docstring-classes.py:34` (`CLASS_LINE`), `:43-70` (`_entries`: a blank line ends an entry, a non-indented line ends an entry, indented lines are joined). `tools/souji-worktree-drift.py:50-51` documents `RECORD-OUTSIDE-ROOT` with `--root` on the continuation line; the joined map gives `RECORD-OUTSIDE-ROOT | a record row, or the gitdir it resolves to, escapes --root`.

### C2-2 Landed bytes (`128e412`) could not run — harm, repaired at `8a5fbdb`

```
$ python3 -B $S/t-$LAND/census/round-40/c2-counter.py --root $L --rev $LAND --base-rev $BASE --scratch $S/c2h
Traceback (most recent call last):
  File ".../census/round-40/c2-counter.py", line 46, in <module>
    import docstring_classes as dc  # noqa: E402  (the joined analyser, same directory)
ModuleNotFoundError: No module named 'docstring_classes'
rc=1
```
The analyser file is `docstring-classes.py` (hyphen), so the landed counter could not import it. Repair at `8a5fbdb` loads it by path (`census/round-40/c2-counter.py:128-142`). The c2 receipt was produced at `8a5fbdb`, so the receipt is unaffected.

### C2-3 Scope falsifier — documented class vs runtime, outside the frozen pairs

Probes (tip tool `$S/t-$H/tools/souji-worktree-drift.py`, `$S/c2probe`, scratch only):

```
RECORD-MALFORMED ENOENT            rc=2 :: REFUSAL RECORD-MALFORMED: .../absent.tsv is not a regular file
RECORD-MISSING EACCES              rc=2 :: REFUSAL RECORD-MISSING: [Errno 13] Permission denied: .../locked.tsv
RECORD-MALFORMED dir (non-regular) rc=2 :: REFUSAL RECORD-MALFORMED: .../adir is not a regular file
ENOTDIR (component is a file)      rc=2 :: REFUSAL RECORD-MISSING: [Errno 20] Not a directory: .../plainfile.tsv/x.tsv
RECORD-EMPTY no REPO rows          rc=2 :: REFUSAL RECORD-EMPTY: no REPO rows in .../empty.tsv
JSON-INSIDE-MEASURED-TREE          rc=2 :: REFUSAL JSON-INSIDE-MEASURED-TREE: .../root/o.json is under .../root
JSON-IS-RECORD                     rc=2 :: REFUSAL JSON-IS-RECORD: .../ok.tsv is the record file
JSON-NOT-REGULAR (FIFO)            rc=2 :: REFUSAL JSON-NOT-REGULAR: .../fifo.json is not a regular file
JSON-HARDLINKED                    rc=2 :: REFUSAL JSON-HARDLINKED: .../hl.json has 2 links
JSON-UNWRITABLE (missing dir)      rc=2 :: REFUSAL JSON-UNWRITABLE: [Errno 2] No such file or directory: 'nodir'
USAGE --timeout 0                  rc=2 :: REFUSAL USAGE: --timeout must be >= 1
```
ENOTDIR is a missing path, so under the tool's own `RECORD-MALFORMED` entry (`tools/souji-worktree-drift.py:46-48`, "a missing (ENOENT) or non-regular record path") it should be MALFORMED. The runtime says MISSING (`tools/souji-worktree-drift.py:133-136`: `if exc.errno == errno.ENOENT: MALFORMED` else `MISSING`). The `RECORD-MISSING` entry (`:44-45`, "EACCES or ELOOP … the path exists") does not name ENOTDIR either. No leg checks it: the frozen pairs are only `RECORD-MALFORMED/ENOENT`, `RECORD-MISSING/EACCES`, `RECORD-OUTSIDE-ROOT/--root` (`census/round-40/c2-counter.py:74-78`). Every other probe agrees with its documented class.

### C2-4 Control arm is not the r39 bytes

The L4 "one-line" arm is `analyzer.first_line_entries(...)` from the NEW module (`census/round-40/c2-counter.py:281-283`, `:295`), not the r39 bytes. The r39 one-line extractor is `census/round-39/c2-counter.py:133-146` `docstring_classes(tool)`, which only reads `RECORD-MISSING` and `RECORD-MALFORMED` (it never extracts `RECORD-OUTSIDE-ROOT`). The control therefore is a reimplementation of the first-line reading, not the r39 artefact. The prereg's control clause ("r39 `docstring_classes` extracts only the first class line") is only approximately tested.

### C2-5 Analyser limit (not exercised by any leg)

`_entries` ends an entry on a non-indented line (`docstring-classes.py:68-69`). A trigger the tool writes at column 0 under a class is silently missed. The synthetic probe (`c2-counter.py` `SYNTHETIC_DOC`) uses an indented continuation only.

## C3 — coverage (`tests/fixtures/r40-drift-record-branches.py`, `census/round-40/c3-counter.py`)

```
$ python3 -B $S/t-$H/census/round-40/c3-counter.py --root $L --rev $H --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch $S/c3h
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
rc=0
```
Same at `128e412` (archived `c3-counter.py`, `SUMMARY … killed=4 … base_killed=0 cases=8`, rc 0); the landed counter printed `failing=-` for every kill, which the `8a5fbdb` fix corrected (`census/round-40/c3-counter.py:116-117`). Fixture at the tip: `SUMMARY cases=8 pass=8 fail=0`, rc 0.

Attack notes, none of which flips the verdict:
- Mutant anchors are each unique (no `ANCHOR-COUNT` line). Declared set is M15–M18 only; C3's coverage claim is limited to those four.
- `M16` (`if True:`) is also killed by the `good` and `total-duplicate-identical` cases, so the kill is not attributable to `skip-unrecorded-suppresses` alone. The paired `unrecorded-without-flag` case still exercises the flag's other arm.
- The crash probe (`c3-counter.py:115-118`) scores a mutant that crashes the fixture as SURVIVED. That is conservative and cannot produce a false pass.
- The invalid-UTF-8-in-comment case kills nothing (M17 is killed only by the repo-name case). Fine for the predicate, which requires the case to exist, not to kill.

## D1 — "after" census receipt (r39 defect: `rows=173 W04=47` against a 174/48 registry)

Registry bytes are identical at `6ded1248`, `128e412` and `994de3b` (`git rev-parse <rev>:corpus/SOURCES.md` → `3698b1daa8ad85499870373bb333cff0d23533e6` at all three; `git diff --stat 128e412 HEAD -- corpus/SOURCES.md` empty).

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
... 49 lines matching W04 ...
rc=0
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin --file $S/t-$H/corpus/SOURCES.md | grep -P '\trows\t'
file	rows	178
FLEET	rows	178
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin --file $S/SOURCES-6ded.md | grep -c W04
49
```
The receipt `census/round-40/records/census-after.txt:4` reads `SUMMARY rows=178 W04=49 rc=0 measured_at=8a5fbdb…`. The numbers reproduce, so the r39 defect (173/47) is gone.

Still owed:
- `census/round-40/records/census-after.txt:2` names `validate`. `validate` prints no `rows` figure (`grep -c rows` on its output = 0). The `rows=178` comes from `census` mode, which the receipt does not name.
- `:4` is not script output: `grep -n SUMMARY scripts/sources-census.sh` returns nothing. The line was composed by hand. The receipt should carry the verbatim outputs of the two commands, or label the `SUMMARY` line as composed.

Verdict: **PARTLY CLOSED**.

## D2 — final-tip re-measure names a revision it did not measure (r39 defect: report says `0242085`, receipt says `5441045`)

```
$ git -C $L show 6ded1248:census/round-40/records/c2-after.txt | head -3
# souji round 40 — C2 operability receipt
# command: python3 -B census/round-40/c2-counter.py --root . --rev 8a5fbdbddaab24c5ba43fc6a133499efb405f214 --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch <scratch>
# measured_at: 8a5fbdbddaab24c5ba43fc6a133499efb405f214
$ git -C $L show 6ded1248:census/round-40/records/c2-after.txt | grep SUMMARY
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
```
The receipt names the revision it measured (`8a5fbdb`), and the counter bytes at `8a5fbdb` equal those at `994de3b` for every C2/C3 artefact (`git diff --stat 8a5fbdb 994de3b -- census/round-40/c2-counter.py census/round-40/c3-counter.py census/round-40/docstring-classes.py tools tests/fixtures` shows only `tests/fixtures/r40-c1-evidence.py`). The tip run (C2-1) reproduces `SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741` exactly.

Owed (nit): the header command has a literal `<scratch>` placeholder; it is not re-runnable as written. The SCORECARD D2 line (`SCORECARD.md:784`) correctly names `8a5fbdb`.

Verdict: **CLOSED**.

## D3 — `commit_distinct` reads as distinct commits (r39 defect)

Instrument label: `census/round-40/c1-counter.py:174` (`distinct_rows` = rows whose commit differs from receipt_rev) and `:175` (`distinct_hashes`), printed as `commit_rows=` / `commit_hashes=` on the `REGISTER` and `SUMMARY` lines. Live tip output (C1-0): `REGISTER cells=3 … commit_rows=3 commit_hashes=1`. Committed receipt with the separated fields: `census/round-40/records/c1-control.txt:6-7`: `REGISTER cells=6 mismatches=0 commit_rows=6 commit_hashes=1 violations=0 ok`. `commit_distinct` no longer appears in any r40 counter, fixture or receipt. It survives only in the r39 SCORECARD rows (`SCORECARD.md:761`, `:771`), the r39-counter run inside `c1-control.txt` (lines 6–7), and the r40 lesson's quotation of the r39 defect (`corpus/lessons/round-40.md:82`).

Owed: the D3 closure is mis-wired.
- `SCORECARD.md:785` (`R40-CLAIM-D3`) cites `census/round-40/c1-counter.py` at `8a5fbdb` (pre-`994de3b` bytes, no path check) and `census/round-40/records/c3-after.txt` (a C3 receipt with zero `commit_rows` tokens). `census/round-40/c1-items.tsv:4` binds D3 to the counter. The C1 gate accepts the closure on that basis (C1-3).
- `R40-CELL-03` (`cells.tsv:4`) is a C3 cell (`killed=4`) on the same line as the C1 claim. The two claims are conflated on `SCORECARD.md:785`.
- Fix: re-point D3's evidence to `census/round-40/records/c1-control.txt@6ded1248…` (which prints `commit_rows=6 commit_hashes=1`) and split the C3 cell onto its own line.

Verdict: **PARTLY CLOSED**.

## Owed, by target

1. C1 (FALSIFIED): bind the evidence content. Require the item's must tokens (or the cell's `expected` value) to occur as whole tokens in `git show <evidence_rev>:<evidence_path>`, and add a control with a line that names `` `PATH` `` and the revision where the file lacks the value (the `ID-X`/`ATT-D3-RECEIPT` shape). Without that, the C1 forged control cannot tell a citation from a coincidence.
2. C1 receipt: commit a C1 "after" receipt at the tip naming base `0242085` and after `994de3b`. Replace `c1-control.txt`'s `<items5.tsv>`/`<items6.tsv>` placeholders with committed input files.
3. D1: rewrite `census/round-40/records/census-after.txt` to carry the verbatim output of `sources-census.sh census --root … souji` (rows) and `validate` (W04), or label line 4 as composed.
4. D2: replace `<scratch>` in `c2-after.txt:2` and `c3-after.txt` with a runnable scratch path.
5. D3: re-point `SCORECARD.md:785` / `c1-items.tsv:4` to `census/round-40/records/c1-control.txt@6ded1248…`; split `R40-CELL-03` from the D3 line.
6. C2 scope: ENOTDIR is classed RECORD-MISSING by runtime (`tools/souji-worktree-drift.py:133-136`) but is a "missing path" under the MALFORMED entry (`:46-48`). Fix the docstring or the code, and add an ENOTDIR (or a fully general `errno`) probe to the frozen pairs. Make the L4 control use the r39 extractor bytes (`census/round-39/c2-counter.py:133`), not the new module's first-line mode.
7. C2 analyser: a column-0 continuation line is silently dropped (`docstring-classes.py:68-69`). Add a probe or document the indentation rule as a contract.
8. C3: none for the declared battery. The declared set is four mutants.

## Harm check

- C2 landed bytes crashed (C2-2) and were repaired at `8a5fbdb`; no consumer fixture regressed at the tip (`L6 … pass`).
- The C1 landed bytes closed on a bare revision id (C1-1), repaired at `994de3b`. The repair itself also reopened D3 under the new check at `549d9ec` (`ITEM R40-CLAIM-D3 OPEN EVIDENCE-NOT-BOUND`), since the D3 line did not name its path; the tip SCORECARD does name it.
- Registry unchanged since landing; census numbers unchanged.

## Tools

No installs. Read-only tooling only: `git` (`show`, `archive`, `rev-parse`, `cat-file`, `diff --stat`, `log`, `ls-files`), `python3 -B` (counters, fixtures, tool probes), `sha256sum -c`, and `scripts/sources-census.sh` (`validate`, `census`; read-only per its header). Nothing was written to the fleet repo, a sibling lane, `.ufo/state`, the watchdog log, operator config, or templates. Lane writes: this report and the scratch dir only.

## Scratch

`/fast/scratch/hyaku/souji-r40/w2/R40w2revenger04` (pinned archives `t-*`, `att-c1` repo, `att-real-*`, `c2probe*`, counter `--scratch` dirs). Removed at the end of this run; see the last line of this file.

Scratch removal: **yes**. `rm -rf -- /fast/scratch/hyaku/souji-r40/w2/R40w2revenger04` ran after this file was written and the check `[ -e … ]` reported the path gone. Nothing outside the scratch dir and this report was written.
