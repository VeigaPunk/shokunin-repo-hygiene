# W1RevC1Forge — C1 instrument forgery (round 39, wave 1)

- seat: reviewer (leaf, no subagent dispatch)
- lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- frozen contract: `census/round-39/preregistration.txt` (read first)
- lane base: `ed30b7f5b77939c9073348d810730bc4f355708d`
- lane HEAD during audit: `2201778e7736af82e7d8a42dec2494f115bf3923` (mid-wave; not the landing)
- counter under attack: `census/round-39/c1-counter.py` (working tree == `git show HEAD:` bytes; sha256 `f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed`)
- items under attack: `census/round-39/c1-items.tsv` (sha256 `d892b74f83587a79a83b0c39aff89d1e93a0f8ac0d523f5d02b8a55c76769f34`)
- scratch root: `/fast/scratch/hyaku/souji-r39/W1RevC1Forge` (removed after capture; see Cleanup)
- tool installs/upgrades: none

**Method note (required by the reviewer role).** This seat has no `lsp` device mounted
(`xd://lsp` absent from the tool set), so `references`/`definition`/`diagnostics` could not be
run. Caller discovery for the C1 instrument used text `grep` over `tools/`, `tests/`, `SKILL.md`
and the round-39 lesson as the literal fallback, and no grep result is presented as semantic
proof. No lane byte was edited; every mutation below happened in `/fast/scratch`.

## 0. Baseline: the frozen do-nothing control reproduces exactly

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev ed30b7f5b77939c9073348d810730bc4f355708d \
  --items /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-items.tsv \
  --register census/round-39/cells.tsv \
  --scratch /fast/scratch/hyaku/souji-r39/W1RevC1Forge/tmp16   # rc=1
diff -u <lane>/census/round-39/records/c1-before.txt <scratch>/replay-control2.txt
```

Observed (tail; the full 18-line output is byte-identical to the committed receipt):

```
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
IDENTICAL
```

Verdict: **PASS** — the control is honest and reproducible; `open=16` and `items_sha` match the
committed `census/round-39/records/c1-before.txt`. The instrument's do-nothing arm is not the
weak point.

Instrument facts established by reading `census/round-39/c1-counter.py` (lines 119-249) and
confirmed by the runs below:

1. `--items` is read with a plain `open(args.items)` from the **working tree** (line ~190); only the
   register blob is revision-bound (`git_show(root, register_rev, register)`).
2. An item closes on `anchor in line` plus whole-token `must`/`mustnot` on **that same line**
   (`has_token`, alnum boundaries). Nothing binds the line to a receipt, a commit, a path, a round,
   or the item id.
3. `anchor` need only be non-empty; it is never required to be unique, id-shaped, or round-authored.
4. The register leg runs the frozen `tools/souji-citation-reconcile.py` bytes at `--rev` and takes
   its `SUMMARY cells=/mismatches=`; `commit_distinct` comes from the counter's own parse of the
   register blob. Both are sound, but **no register row references any item id** — the two arms are
   disjoint.
5. The two register floors are caller-settable (`--min-cells`, default 6;
   `--min-commit-distinct`, default 2) and the frozen command does not pin them.

## 1. Check — one forged row whose anchor already exists at base

Items copy: `census/round-39/c1-items.tsv` plus four extra rows (`items-forged.tsv` in scratch).

```
F1       LOG.md         cases=9   fail=6                 -
F2       SCORECARD.md   6ff3413   repair4d5bf7...b7e3     -
F3-NEG   SCORECARD.md   repair4d5bf7...b7e3  coverage    8
F4       LOG.md         e         cases=9,fail=6         -
```

The anchors and `must` tokens come from lines that exist at the base revision, e.g.:

```
git -C <lane> show ed30b7f:LOG.md | grep -n 'cases=9'
1667:cases=9 pass=9 control=FALSE-GREEN-REJECTED (c2-fixture-after.tsv). The
1855:- C2 operability: ... cases=9 pass=3 fail=6 base_fail=6 ...
1862:- The frozen predicate sentences ... cells=9 ... cases=9 base_fail=6 ...
git -C <lane> show ed30b7f:SCORECARD.md | grep -n '6ff3413'
13:| coverage | 8 | R21 admitted bounded sink repair: ... repair4d5bf7...b7e3 ...
```

Run (same command as §0 with `--items <scratch>/items-forged.tsv`, `--register census/round-38/cells.tsv`,
rc=1):

```
ITEM F1 CLOSED
ITEM F2 OPEN PREDICATE-MISSING SCORECARD.md missing=['repair4d5bf7'] hits=1
ITEM F3-NEG OPEN PREDICATE-MISSING SCORECARD.md missing=[] hits=1
ITEM F4 CLOSED
REGISTER cells=10 mismatches=0 commit_distinct=0
SUMMARY items=20 open=18 register_cells=10 register_mismatches=0 commit_distinct=0 items_sha=aaf8339225ec
```

`F1` and `F4` close at the base revision with no round work. `F3-NEG` is the non-vacuity control:
its `mustnot` token `8` is present on the anchored line, so it reads OPEN (`missing=[]` is the
mustnot branch), which shows the predicate does evaluate `mustnot`. `F2` initially read
PREDICATE-MISSING because `repair4d5bf7` is not a **whole** token of
`repair4d5bf78432de7f4afe38e6bf195fd7843bdcb7e3`; rerun with the full hex it reads:

```
ITEM F1 CLOSED
ITEM F2 CLOSED
ITEM F4 CLOSED
REGISTER cells=10 mismatches=0 commit_distinct=0
SUMMARY items=3 open=0 register_cells=10 register_mismatches=0 commit_distinct=0 items_sha=d8ed0496960a
```

(`items-forged-only.tsv`, rc=1 only because the r38 register reads `commit_distinct=0`.)

Verdict: **FORGERY SUCCEEDS at the item level.** A row closes without any round work whenever its
anchor already exists at base; the whole-token boundary is the only real check, and it is honest.
`F4` shows the anchor may be a single letter (`e`), so "line-unique anchors keep the predicate
re-derivable" (items header, line 5) is an unenforced comment.

## 2. Check — the hardest forgery: a correction line that cites nothing

Scratch git fixture (created only inside `/fast/scratch`, toplevel asserted equal to the fixture):

```
D=$(mktemp -d -p /fast/scratch/hyaku/souji-r39/W1RevC1Forge)
git -C "$D" init -q
test "$(git -C "$D" rev-parse --show-toplevel)" = "$D"
# c1: tools/souji-citation-reconcile.py (base bytes) + receipts/c1.txt "SUMMARY cases=3 fail=0"
#     + receipts/c2.txt "SUMMARY cases=4 fail=0"
# c2: evidence.md with six register rows' anchor lines and two bare lines
# c3: census/round-39/cells.tsv (6 rows, 4 with commit != receipt_rev)
```

The two bare lines committed at `c2` / visible at `c3` `728e42eb40d4a8d6edf84d3ce9a9ca0bb52e9401`:

```
R39-C1-06 r38-citation-commit r38-drift-write-envelope r38-drift-record r38-drift-mutants
R39-C1-10 fcdecaa measured-revision
```

Neither line names a receipt, a receipt revision, a path, or a commit: they are the exact `must`
token sets of frozen rows `R39-C1-06` and `R39-C1-10` written on their own line. Items file
(`items-fixture-forge.tsv`) spoofs those two ids with those anchors.

```
python3 -B <lane>/census/round-39/c1-counter.py --root "$D" \
  --rev 728e42eb40d4a8d6edf84d3ce9a9ca0bb52e9401 \
  --items <scratch>/items-fixture-forge.tsv \
  --register census/round-39/cells.tsv --scratch <scratch>/tmp7
```

Observed (rc=0):

```
ITEM F6 CLOSED
ITEM F10 CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=4
SUMMARY items=2 open=0 register_cells=6 register_mismatches=0 commit_distinct=4 items_sha=aa11fa637b86
```

At `c1` (before the two lines were written) the same command reads:

```
ITEM F6 OPEN FILE-ABSENT evidence.md
ITEM F10 OPEN FILE-ABSENT evidence.md
SUMMARY items=2 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=aa11fa637b86
```

`fcdecaa` does **not** resolve in the fixture, and the row still closes:

```
git -C "$D" rev-parse 'fcdecaa^{commit}'
fatal: ambiguous argument 'fcdecaa^{commit}': unknown revision or path not in the working tree.
rc=128
```

Verdict: **FORGERY SUCCEEDS end-to-end; the counter CANNOT detect an evidence-free correction
line.** It detects only token presence. The commit-looking `must` token `fcdecaa` is never
resolved, never checked for ancestry, and never tied to a receipt carrying the expected value — the
item arm has none of the r37 register arm's machinery (`RECEIPT-UNNAMED`, `COMMIT-UNRESOLVED`,
`COMMIT-RECEIPT-DISAGREES`).

## 3. Check — the whole 16-id table can be forged at the base revision

Three variants at the lane base `ed30b7f...`:

```
16 rows R39-C1-01..16, all: file=LOG.md anchor=cases=9 must=fail=6 mustnot=-
```

```
# defaults
SUMMARY items=16 open=0 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=58a112d3590d   rc=1
# --register census/round-38/cells.tsv --min-commit-distinct 0
SUMMARY items=16 open=0 register_cells=10 register_mismatches=0 commit_distinct=0 items_sha=58a112d3590d  rc=0
# --register census/round-39/cells.tsv --min-cells 0 --min-commit-distinct 0
SUMMARY items=16 open=0 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=58a112d3590d   rc=0
```

Every one of the 16 ids reads CLOSED at the base revision. The frozen kill rule
("`--rev ed30b7f...` ... reads `open=0`") is therefore satisfied by a swapped items table: the
control only tests the items bytes it is handed, and `items_sha` is the sole tell.

The same construction against the fixture, with the fixture's own clean 6-cell register, reaches
the frozen SUMMARY **shape** with exit 0 and zero round work (16 real ids, anchor `A`, must
`cases=3`, rc=0):

```
SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=4 items_sha=eda5614d28e2
```

Verdict: **FORGERY SUCCEEDS.** Item ids are labels only; the counter never validates that
`R39-C1-NN`'s anchor is on the line that corrects routed defect NN, that anchors are distinct, or
that the row set is the frozen one. `items=16` is reproduced by repeating one row 16 times.

## 4. Check — the floors are part of the attacker's command line

`SKILL.md` line 273 publishes `[--min-cells N] [--min-commit-distinct N]`; the frozen predicate
does not pin them. Run F2 above exits **0** with `register_cells=0` when both are lowered. The
printed SUMMARY still betrays `register_cells=0`, so a string-matching reader catches it, but the
exit status does not. Verdict: **real, medium**, because the frozen predicate is a string match by
an honest reader, yet every automated consumer sees rc 0.

## 5. Disclosure check — what the lane already says at HEAD

`git show 2201778:corpus/lessons/round-39.md` lines 104-110 (committed):

```
- The C1 counter reads its item list and fixtures from the working tree and prints `items_sha=`;
  the audited bytes are `--rev`-bound. A reader must compare `items_sha` to the committed
  `census/round-39/c1-items.tsv` to know which list produced a reading.
- A C1 item binds one anchored line to token presence. An author who writes the tokens on a line
  that cites nothing satisfies the item; the counter cannot police authorship, as r38's
  `W1CritC1` showed for the register arm.
```

`git show 2201778:SKILL.md` line 273, registry row `c1-counter (r39)`:

```
... Reads committed bytes only and prints `items_sha=`; the item list is an instrument read from the working tree. ...
```

The lesson discloses both limits honestly, and the SKILL row carries the qualifying clause. Two
residual self-description problems:

1. The frozen prereg `COUNTER:` sentence says the counter runs "over committed bytes only
   (`git show`)" — false for `--items`, which is the arm every one of the 16 claims rides on. The
   only correction is in the lesson (not frozen); the prereg has no amendment for it.
2. `SKILL.md`'s first clause ("Reads committed bytes only") contradicts its own last clause between
   semicolons; the row is accurate only if the reader keeps both halves.

Verdict: **DISCLOSED, not enforced.** The lane knows the forgery; no counter or gate in the lane
tests it. r37 closed exactly this class for the register with a receipt arm (`RECEIPT-UNNAMED`) and
r38 added the commit arm; the r39 item leg did not adopt either.

## Findings (by severity)

1. **HIGH (calibration) — C1's item arm is forgeable and the items table is revision-unbound.**
   A bare line carrying only the `must` tokens closes a row (§2, rc 0 with clean register); a
   swapped 16-row table reads `items=16 open=0` at the base revision (§3). The counter cannot detect
   it; the only guard is a human comparing `items_sha` to `git show <rev>:census/round-39/c1-items.tsv`.
   Cite: `census/round-39/c1-counter.py` (items read via `open()`, close predicate = anchor +
   `must`/`mustnot` on one line).
2. **MEDIUM — the register floors are caller-settable and unpinned.** §4: rc 0 with
   `register_cells=0`. Freeze the floors in the predicate command, or remove the flags.
3. **MEDIUM — the frozen prereg `COUNTER:` sentence misdescribes the instrument** ("committed bytes
   only" while `--items` is working-tree). Lesson disclosure exists; append-only correction or a
   report erratum is owed.
4. **LOW — anchors are neither unique nor id-bound.** §1 `F4` (anchor `e`) and §3 (16 identical rows)
   close; the items header's "line-unique anchors" claim is a comment, not a check. This also
   defeats the frozen base kill rule under a swapped table.
5. **LOW — commit-looking `must` tokens are never resolved.** §2: `fcdecaa` does not resolve in the
   fixture and the row still closes. In the lane, `fcdecaa` does resolve and is an ancestor of the
   base (`git merge-base --is-ancestor fcdecaa ed30b7f` rc 0), so the honest landing is not wrong —
   the instrument simply never checks.
6. **POSITIVE — checks that do hold:** whole-token boundaries (`F2` first read), `mustnot`
   (`F3-NEG`), file/anchor absence, revision refusal (exit 2), and the register leg through the
   repaired reconciler: at the fixture, `SUMMARY cells=6 mismatches=0`; a register not present at
   `--register-rev` was refused (`REFUSAL USAGE: register ... is not at 1d56d6e...` rc 2).

## Honest limit

The counter proves token co-occurrence on one committed line per row. It does not, and by its bytes
cannot, distinguish a correction that names its evidence from a line that concatenates the required
tokens. For `R39-C1-06` the honest landing line (`SKILL.md:283`, prose plus four fixture names) and
the forged line (`R39-C1-06 r38-citation-commit ...`) are the same object to the counter. So:

- **Detectable by the counter:** nothing at the item level; the register arm is sound but disjoint
  from the 16 items.
- **Detectable by an auditor, not the counter:** `items_sha` vs the committed blob
  (`d892b74f8358` at HEAD), and reading each anchored line to see whether its evidence exists and
  carries the claimed value. The `c1-before.txt` receipt already carries the correct
  `items_sha=d892b74f8358`, so the honest path is auditable.
- **What would actually close it:** an item-level receipt/commit arm (each item names a receipt blob
  and revision whose `SUMMARY` carries a round-specific token), a register row per item, an
  `--items-rev` that reads the table with `git show`, and an anchor-uniqueness/id check.

## Residual risk and verification gaps

- I did not forge the lane's real landing bytes (no lane write permitted, and the landing does not
  exist yet). The fixture reproduces the mechanism exactly with the frozen `R39-C1-06`/`R39-C1-10`
  token sets; fixture commit hashes will differ on reproduction because they embed timestamps.
- No `lsp` server was available in this seat, so the caller/definition/diagnostic checks were text
  `grep` only; the grep found no other consumer of `census/round-39/c1-items.tsv` in `tools/` or
  `tests/` (only `SKILL.md`, the prereg and the counter reference it), so no second gate re-checks
  the anchored lines.
- I did not run C2 or C3 (out of this seat's scope). No claim is made about their instruments.
- The fixture's `.git` and all scratch files are outside the lane; nothing in the fleet repo, a
  sibling lane, `.ufo/state/`, or `~/.config` was written.

## Commands run (exact, all with absolute paths)

1. `git -C <lane> rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin`
2. `git -C <lane> rev-parse ed30b7f...^{commit}` → `ed30b7f5b77939c9073348d810730bc4f355708d`
3. `git -C <lane> show ed30b7f:census/round-39/c1-items.tsv` → fatal, path not at base (items is a
   round-39 file; the counter still read it from the working tree, which is the finding)
4. `git -C <lane> cat-file -e ed30b7f:census/round-39/cells.tsv` → absent at base
5. `sha256sum <lane>/census/round-39/c1-items.tsv` → `d892b74f83587a79a83b0c39aff89d1e93a0f8ac0d523f5d02b8a55c76769f34`
6. `sha256sum <lane>/census/round-39/c1-counter.py` → `f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed`
7. control replay (§0) and `diff -u` against `records/c1-before.txt` → `IDENTICAL`
8. forged-rows run (§1) ×2 with `--items items-forged.tsv` / `items-forged-only.tsv`
9. fixture build: `git -C "$D" init -q`, `git -C "$D" rev-parse --show-toplevel` asserted, three
   commits `c1`/`c2`/`c3` inside `/fast/scratch` only
10. fixture runs (§2, §3): `--rev 1d56d6e...` (c2), `--rev 728e42e...` (c3), `--rev cb04a69...` (c1)
11. base forged-table runs (§3, §4) with and without the floor flags
12. `git -C <lane> show 2201778:corpus/lessons/round-39.md | sed -n '95,125p'` and
    `git show 2201778:SKILL.md | sed -n '271,275p'` (disclosure check)
13. `git -C <lane> merge-base --is-ancestor fcdecaa ed30b7f` → rc 0
14. `python3 -B <lane>/census/round-39/c1-counter.py --root <lane> --rev $(git -C <lane> rev-parse HEAD)
    --items <lane>/census/round-39/c1-items.tsv --register census/round-39/cells.tsv` → mid-wave
    context: `SUMMARY items=16 open=2 register_cells=0 ... items_sha=d892b74f8358` rc 1 (not a claim
    reading; recorded only to show the honest bytes are the same table)

## Cleanup

`/fast/scratch/hyaku/souji-r39/W1RevC1Forge` (232K incl. the fixture `.git`) was removed after
capture with `rm -rf -- /fast/scratch/hyaku/souji-r39/W1RevC1Forge`; the scratch tree is not on
disk at hand-off.
