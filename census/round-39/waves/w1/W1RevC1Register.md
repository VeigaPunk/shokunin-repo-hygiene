# W1RevC1Register — review: the C1 register leg (souji round 39, wave 1)

Seat: W1RevC1Register (reviewer, leaf; no subagent dispatch). Lane:
`/home/vgpnk/Projects/shokunin/souji-shokunin`. Base
`ed30b7f5b77939c9073348d810730bc4f355708d`, audit tip
`2201778e7736af82e7d8a42dec2494f115bf3923`. Frozen contract read first:
`census/round-39/preregistration.txt` (freeze commit `b769bfb8`). All commands used absolute paths; no
mutating git/jj command was run in the lane or anywhere else — the only commits below are inside a
throwaway fixture under my own scratch dir.

Scratch: `/fast/scratch/hyaku/souji-r39/W1RevC1Register` (removed at the end of this seat; see
§Scratch).

Verdict key: PASS / FAIL / NOTE (informational, no contract breach).

---

## Skeleton of the leg under attack

`census/round-39/c1-counter.py` splits the register arm in two independent halves:

1. `parse_register(raw)` — the counter's **own** parse of the register blob fetched with
   `git show <register_rev>:<register>`. It counts `cells` (every data row with ≥7 tab fields) and
   `distinct` — *rows whose 8th field (the `commit` cell) is a non-empty string unequal to the 7th
   field (`receipt_rev`)*. No resolution, no ancestry, no receipt read: string inequality only.
2. `register_leg(...)` — extracts `tools/souji-citation-reconcile.py` **at `--rev`** into scratch and
   runs it with `--rev`, `--register`, `--register-rev`; only the child's `SUMMARY cells=N
   mismatches=M` line is consumed (the child's exit code is not). `mismatches` is the reconciler's.

Exiting 0 needs `open==0 and cells>=6 and mismatches==0 and distinct>=2`. So "the leg refuses" can
mean three different things: a **mismatch** (rc 1, reconciler findings), a **floor miss** (rc 1,
counter's own arithmetic), or a **refusal** (rc 2, could-not-evaluate). The attacks below separate
them.

The frozen reconciler's per-row arms at `--rev` are worth stating because they bound the attack
surface: citation line — exactly one line carries the anchor, carries `expected` as a whole token,
contains `` `receipt` `` and does not carry `stale`; `receipt_rev` — resolves, is an ancestor of
`--rev`, its receipt blob has a `SUMMARY` line carrying `expected`; `commit` — resolves, is an
ancestor of `--rev`, is named on the anchored line (full hash or 7-hex prefix), and its receipt blob
has a `SUMMARY` line carrying `expected`. **No arm compares `commit` with `receipt_rev`**, and **no
arm checks that `stale` ever existed**.

## Fixture

`/fast/scratch/hyaku/souji-r39/W1RevC1Register/build.py` builds `repo/` with
`git -C "$D" init -q` and asserts `git rev-parse --show-toplevel` equals the fixture before the first
commit:

```
$ python3 -B build.py
A=3fa11caca3d9b5ed72227234eb4f25cdba9b9672
B=13caa5092f761e35335918a5231727d010d924a7
C=9fdd9b55a481e5ecafca83219b55ce37e3f4d0ff
E=de57baa2f1a41a0a5ab03d83018291afda418c22
D=35c436dab843603f7409fb3d6b68c5f8d5c36000
T=eaadf6c78a8e305ee7d557d08efe7030e4e8989c
toplevel=/fast/scratch/hyaku/souji-r39/W1RevC1Register/repo
```

A → B → C → E → T on the trunk; D on a side branch from A. `census/r.txt` reads `SUMMARY legs=6` at
A, B, E and on D, and `SUMMARY legs=7` at C. `SCORECARD.md` at T carries 36 single-line citations
(one anchor per row of every register below) plus the items anchor. One extra commit `U` copies the
lane's frozen reconciler into `tools/`, so the counter's `git show <rev>:tools/...` finds it:

```
$ git -C $D rev-parse 6a0f1d60fee53d1330b1ed99efbefaa59676d6c2:tools/souji-citation-reconcile.py
bece17001065b7cc4f4be48551a3b2a8d1ec866f
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 2201778:tools/souji-citation-reconcile.py
bece17001065b7cc4f4be48551a3b2a8d1ec866f
```

Byte-identical to the lane tool at the audit tip. All six registers have a header + 6 rows and are
committed at `U`; every run is
`python3 -B <lane>/census/round-39/c1-counter.py --root $D --rev 6a0f1d6 --items $D/items.tsv
--register regs/<variant>.tsv --scratch $S/tmp` (defaults `--min-cells 6 --min-commit-distinct 2`).

Control (baseline register, 3 rows `receipt_rev=A commit=B`, 3 rows `receipt_rev=B commit=E`):

```
ITEM IT-01 CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=40949065fede
rc=0
```
**Verdict: PASS (fixture is sound).** A green baseline exists, so every refusal below is caused by the
injected defect and not by the harness.

## A1 — `commit` is an ancestor but its receipt blob reads a different token

Rows: 5 baseline rows + `REG-06  receipt_rev=A  commit=C`, and C's `census/r.txt` is
`SUMMARY legs=7` while `expected=legs=6`. C is an ancestor of the audited rev (trunk A→B→C→E→T).

The reconciler alone (frozen bytes extracted from the fixture's `U`):
```
MISMATCH REG-06 COMMIT-RECEIPT-DISAGREES census/r.txt expected='legs=6' (no SUMMARY line at 9fdd9b5 carries it)
SUMMARY cells=6 mismatches=1
rc=1
```
Through the counter:
```
ITEM IT-01 CLOSED
REGISTER cells=6 mismatches=1 commit_distinct=6
SUMMARY items=1 open=0 register_cells=6 register_mismatches=1 commit_distinct=6 items_sha=40949065fede
rc=1
```
**Verdict: PASS — refused, as a mismatch (rc 1).** `COMMIT-RECEIPT-DISAGREES` is exactly the class
that stops "ancestor commit, unrelated receipt token". Note the counter still reports
`commit_distinct=6`: the distinct metric counted the bad row before the reconciler judged it, so
`commit_distinct` on its own is never a verdict.

## A2 — `receipt_rev` is not an ancestor

Rows: 5 baseline rows + `REG-06  receipt_rev=D  commit=A`, D being the side-branch commit
(`git merge-base --is-ancestor D U` → rc 1). D's receipt blob does read `legs=6`, so only the
ancestry arm can catch this.

```
$ git -C $D merge-base --is-ancestor 35c436dab843603f7409fb3d6b68c5f8d5c36000 $U ; echo rc=$?
rc=1
```
Reconciler alone:
```
MISMATCH REG-06 RECEIPT-REV-NOT-ANCESTOR census/r.txt at 35c436dab843603f7409fb3d6b68c5f8d5c36000
SUMMARY cells=6 mismatches=1
rc=1
```
Through the counter:
```
ITEM IT-01 CLOSED
REGISTER cells=6 mismatches=1 commit_distinct=6
SUMMARY items=1 open=0 register_cells=6 register_mismatches=1 commit_distinct=6 items_sha=40949065fede
rc=1
```
**Verdict: PASS — refused, as a mismatch (rc 1), class `RECEIPT-REV-NOT-ANCESTOR`.**

## A3 — every row carries `commit == receipt_rev`

Six rows, all `receipt_rev=A commit=A`. Each row satisfies both arms (A resolves, is an ancestor,
is named on its line, its receipt carries `legs=6`), so the reconciler is clean and only the floor can
refuse.

```
ITEM IT-01 CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=0
SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=0 items_sha=40949065fede
rc=1
```
**Verdict: PASS — refused, as a floor miss (rc 1), not as a mismatch.** This is the shape the r38
limit named, and the exact shape of the lane's live r38 register (§L2). The refusal is correct, and
it is the counter's own arithmetic (`distinct>=2`) that supplies it.

## A4 — `commit_distinct` is a **row** count, not a count of distinct commit values

Six rows, all `receipt_rev=A commit=B` — one single commit value.

```
$ git -C $D show $U:regs/d-one-commit-value.tsv | awk -F'\t' 'NR>1 && NF>=8 {print $8}' | sort -u | wc -l
1
```
```
ITEM IT-01 CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=40949065fede
rc=0
```
**Verdict: FAIL (metric name vs metric).** `commit_distinct=6` is produced by six rows sharing one
commit. The counter never builds a set, so the field named `commit_distinct` — and quoted verbatim in
the frozen predicate's `SUMMARY ... commit_distinct>=2` — means "rows whose commit cell differs from
their receipt_rev cell". The prereg's prose ("at least two rows whose `commit` differs from
`receipt_rev`") matches the implementation; the *name* and the r38 limit's phrasing ("distinguish the
commit arm from the receipt arm") read as two distinct commits, which this metric does not measure.
**Concrete consequence for this round:** `census/round-39/make-cells.py` writes the *same*
`args.commit` into every row (`table.append(... revs[key], args.commit)`), so the planned register
will report `commit_distinct=6` with exactly one commit value. The floor is met; the number should
never be read as "six distinct commits".

## A5 — `commit` **older** than `receipt_rev`, receipt bytes identical, still green

Six rows, all `receipt_rev=B commit=A` (A is B's parent).

```
$ git -C $D merge-base --is-ancestor $A $B ; echo A-ancestor-of-B rc=$?
A-ancestor-of-B rc=0
$ git -C $D merge-base --is-ancestor $B $A ; echo B-ancestor-of-A rc=$?
B-ancestor-of-A rc=1
$ git -C $D diff --stat $A $B -- census/r.txt     # (no output: identical blob)
$ git -C $D show $A:census/r.txt | sha256sum
8ce19ba5784c1bc9c7606cb7338a4e291970de5d90f14c5f6827b31d58efb787  -
$ git -C $D show $B:census/r.txt | sha256sum
8ce19ba5784c1bc9c7606cb7338a4e291970de5d90f14c5f6827b31d58efb787  -
```
```
ITEM IT-01 CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=40949065fede
rc=0
```
**Verdict: FAIL against the round's own rationale (green register, zero discriminating content).**
Neither the counter nor the frozen reconciler compares `commit` with `receipt_rev`, so a register
whose every `commit` *predates* its `receipt_rev`, whose receipt blob is byte-identical at both
revisions, and whose citation lines claim a re-verification "at" a commit that changed nothing,
satisfies the frozen C1 predicate (`cells>=6 mismatches=0 distinct>=2`, exit 0). `make-cells.py`'s
own docstring asserts the property this attack violates — "Every row here names a `commit` strictly
later than its `receipt_rev`" — and nothing in the frozen predicate tests it. In the actual lane the
property happens to hold (both `--late` and `--commit` are post-base commits, and `--commit` is
expected to be the landing commit), but it holds by the L1's discipline, not by measurement.

## A6 — an invented `stale` token passes

Same shape as A5 with `stale=legs=3`, a token that appears in no citation or receipt blob in the
fixture's history:

```
$ git -C $D grep -n 'legs=3' $(git -C $D rev-list --all) -- census/r.txt SCORECARD.md LOG.md SIDE.md
rc=1     (no match in any citation or receipt blob at any revision)
```
Counter: `SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 ... rc=0`.

**Verdict: FAIL (predicate does not test its own prose).** `stale` is only checked for *absence on
the citation line*; it is never looked up in a pre-repair blob. A citation line asserting "the stale
reading `X` belongs to the pre-repair bytes" is therefore unfalsifiable by the register leg — see
§L3, where five of the six planned lane rows assert exactly such a token.

## L1 — the lane register at the audit tip: absent, and "clean" is indistinguishable from "not evaluated"

```
$ git -C <lane> log --all --oneline -- census/round-39/cells.tsv
(no output)
$ git -C <lane> cat-file -e 2201778:census/round-39/cells.tsv
fatal: path 'census/round-39/cells.tsv' does not exist in '2201778'
$ git -C <lane> cat-file -e ed30b7f5b77939c9073348d810730bc4f355708d:census/round-39/cells.tsv
fatal: path 'census/round-39/cells.tsv' does not exist in 'ed30b7f5b77939c9073348d810730bc4f355708d'
```
Frozen predicate, register path as written in the prereg, at the tip:
```
ITEM R39-C1-01 CLOSED
ITEM R39-C1-02 CLOSED
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
ITEM R39-C1-05 CLOSED
ITEM R39-C1-06 CLOSED
ITEM R39-C1-07 CLOSED
ITEM R39-C1-08 CLOSED
ITEM R39-C1-09 CLOSED
ITEM R39-C1-10 CLOSED
ITEM R39-C1-11 CLOSED
ITEM R39-C1-12 CLOSED
ITEM R39-C1-13 CLOSED
ITEM R39-C1-14 CLOSED
ITEM R39-C1-15 CLOSED
ITEM R39-C1-16 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```
**Verdict: FAIL (not yet green) + NOTE (misleading zero).** C1 is not closed at the audit tip:
`open=2` (R39-C1-03/04 name `census/round-39/records/waves-wait.txt` and `waves-capture.txt`, both
absent at `2201778`) and `register_cells=0` because `census/round-39/cells.tsv` has never been
committed. `parse_register`/`register_leg` treat an absent register as **zero cells and zero
mismatches** (`register_leg` returns `0, 0, "REGISTER-ABSENT"` without running the reconciler), so
`register_mismatches=0` is printed for a register that does not exist. Isolated proof — one CLOSED
item, absent register, floors at their frozen defaults, then relaxed:

```
ITEM R39-C1-10 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=1 open=0 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=2cddf1519712
rc=1                       # refused only by cells>=6

(same command, --min-cells 0 --min-commit-distinct 0)
ITEM R39-C1-10 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=1 open=0 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=2cddf1519712
rc=0                       # rc=0 with no register at all
```
The frozen predicate cannot be reached this way (its floors are the defaults), so this is a
**counting/reading** defect, not a hole: the control receipt `census/round-39/records/c1-before.txt`
already publishes `REGISTER cells=0 mismatches=0 commit_distinct=0`, and a reader who quotes
`register_mismatches=0` from it as "register clean" is quoting a leg that never ran. Any receipt or
report line that cites `register_mismatches=0` MUST also cite `register_cells>=6` (or the exit code)
beside it.

## L2 — the lane's only committed 8-column register reproduces the r38 limit

```
$ python3 -B <lane>/census/round-39/c1-counter.py --root <lane> --rev 2201778 \
    --items <lane>/census/round-39/c1-items.tsv --register census/round-38/cells.tsv --scratch $S/tmp
ITEM R39-C1-16 CLOSED
REGISTER cells=10 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=10 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```
`git show 2201778:census/round-38/cells.tsv` shows ten 8-column rows whose 8th field repeats the 7th
verbatim (`... 02b43398... → 02b43398...`, `... bbefcee6... → bbefcee6...`, `... b4915964... →
b4915964...`, `... 861c2ba2... → 861c2ba2...`).
**Verdict: PASS (the metric separates the arms it was built for).** The r38 register is clean under
the reconciler and reads `commit_distinct=0` — precisely the r38 named limit, now measurable. So
A3's refusal and the r38 reading agree, and the C1 register must beat `0`, which it can only do by
carrying non-equal cells (A4/A5/A6 show how weak that is).

## L3 — the planned register's two unlanded dependencies and five ungrounded `stale` tokens

`census/round-39/make-cells.py` (unlanded) emits six rows whose receipts are
`census/round-39/records/c2-after.txt`, `c3-after.txt` (rows REG-01..05) and `c1-before.txt`
(REG-06). At the audit tip:

```
$ git -C <lane> cat-file -e 2201778:census/round-39/records/c2-after.txt    → absent (untracked)
$ git -C <lane> cat-file -e 2201778:census/round-39/records/c3-after.txt    → absent (untracked)
$ git -C <lane> cat-file -e 2201778:census/round-39/records/c1-before.txt   → present
```
Working-tree SUMMARY lines (the tokens `make-cells.py` expects do exist there):
```
c2-after.txt:SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=7ab7c3d85a81
c3-after.txt:SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
c1-before.txt:SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```
**Verdict: NOTE (forward hazard, not yet a defect).** If `cells.tsv` lands before or without those
two receipts, the register leg reads five `RECEIPT-ABSENT` mismatches and the predicate fails. The
receipts must land in the same commit or earlier.

Now the `stale` claim. `make-cells.py`'s line template asserts "the stale reading `{stale}` belongs to
the pre-repair bytes". Whole-token probe (`has_token` reused from the counter) against the named
pre-repair receipt at the audit tip, and at the base revision:

```
$ python3 -B $S/stale_probe.py
== rev 2201778e7736
  REG-01 stale=legs=2    pre-repair blob census/round-39/records/c2-before.txt present, whole-token=False
  REG-02 stale=harm=3    pre-repair blob census/round-39/records/c2-before.txt present, whole-token=False
  REG-03 stale=fail=4    pre-repair blob census/round-39/records/c2-before.txt present, whole-token=True
  REG-04 stale=killed=1  pre-repair blob census/round-39/records/c3-before.txt present, whole-token=False
  REG-05 stale=cases=9   pre-repair blob census/round-39/records/c3-before.txt present, whole-token=False
  REG-06 stale=open=1    pre-repair blob census/round-39/records/c1-before.txt present, whole-token=False
== rev ed30b7f5b779
  ... all six: pre-repair blob ABSENT at rev
```
The committed pre-repair receipts read:
```
c2-before.txt:SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=... fixture_sha=...
c3-before.txt:SUMMARY mutants=4 killed=0 survived=4 pristine=ok base_killed=0 cases=10 tool_sha=... fixture_sha=...
c1-before.txt:SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```
**Verdict: FAIL (planned prose is false for 5 of 6 rows, and the predicate cannot catch it).**
`legs=2`, `harm=3`, `killed=1`, `cases=9` and `open=1` never appear in the receipts they are claimed
to pre-date (`legs=6`/`harm=0` are unchanged between before and after; `cases` moved 10→7, `killed`
0→4; `open=1` is a substring of `open=16`, not a token). Only `fail=4` is grounded. Because `stale`
is tested only for absence on the citation line (§A6), the register will go green with five citation
lines that state a pre-repair reading that never existed — a fresh instance of the exact calibration
defect class C1 exists to close (a self-assessment cell stating a value the observed repo state
contradicts). **Recommendation to the L1:** either ground each `stale` token in the named pre-repair
receipt, or drop the "belongs to the pre-repair bytes" clause for rows whose field did not move
(REG-01 `legs` and REG-02 `harm` are unchanged before→after and should not be cited as repairs at
all).

## L4 — the register leg is revision-bound (no working-tree fallback)

```
$ python3 -B <lane>/census/round-39/c1-counter.py --root $D --rev eaadf6c (T: tree has no tools/)
ITEM IT-01 CLOSED
REFUSAL COULD-NOT-EVALUATE: tools/souji-citation-reconcile.py absent at eaadf6c78a8e305ee7d557d08efe7030e4e8989c
rc=2
$ git -C $D cat-file -e eaadf6c:tools/souji-citation-reconcile.py → tool ABSENT at T (worktree copy exists: yes)
```
**Verdict: PASS.** Tool bytes come from `--rev`; the working-tree copy is ignored. A malformed register
also refuses as rc 2 rather than mis-scoring:
```
$ python3 -B ... --register regs/f-9col.tsv
ITEM IT-01 CLOSED
REFUSAL COULD-NOT-EVALUATE: register leg produced no SUMMARY (rc=2 stderr='REFUSAL USAGE: register regs/f-9col.tsv has no header line before line 1\n')
rc=2
```

---

## What `commit_distinct>=2` proves, and what it does not

**Proves, given exit 0** (i.e. `open=0`, `register_cells>=6`, `register_mismatches=0`,
`commit_distinct>=2`, all over `git show` bytes only):

1. At `--register-rev` the register parses, has a header and ≥6 data rows.
2. Every row passes the frozen reconciler at `--rev`: the anchor occurs exactly once in its file and
   that line carries `expected` as a whole token, backticks its `receipt`, and does not carry `stale`;
   `receipt_rev` resolves, is an ancestor of `--rev`, and its receipt blob has a `SUMMARY` line
   carrying `expected`; a non-empty `commit` cell resolves, is an ancestor of `--rev`, appears on the
   anchored line (full or 7-prefix), and **its** receipt blob has a `SUMMARY` line carrying
   `expected`.
3. At least two rows have a `commit` string that is not the `receipt_rev` string.

That is: the register is internally consistent, the commit cell is not a copy of the receipt cell, and
the named commit still carries the cited token. It also proves the effective tool bytes are the ones
at `--rev` and the register bytes the ones at `--register-rev`.

**Does not prove:**

1. **Temporal order.** Nothing compares `commit` with `receipt_rev`; `commit` may be an *ancestor*
   of `receipt_rev` (A5) and the register stays green, contradicting `make-cells.py`'s "strictly
   later than its `receipt_rev`".
2. **Change.** The `expected` token must be present at *both* revisions, so a row whose receipt blob
   is byte-identical at `commit` and `receipt_rev` passes (A5, identical sha256). The arm shows the
   later rev did not regress the token; it shows nothing about repair.
3. **Distinct commit count.** The metric counts rows, not values; six rows on one commit give
   `commit_distinct=6` (A4) — and the planned `make-cells.py` register is exactly that shape.
4. **Closure of the r38 limit.** The r38 limit was that the register could not distinguish the commit
   arm from the receipt arm. A3 is refused and L2 reproduces `commit_distinct=0` for r38, so the
   *string-equality* half is closed; but because no row needs the two revisions to differ in content,
   the arm's discriminating *power* is not established by this metric (A4/A5/A6).
5. **`stale` grounding.** The stale token is never looked up anywhere; A6 passes with a token absent
   from all history, and L3 shows five of six planned lane rows assert an ungrounded one.
6. **Coverage of the routed defects.** `cells>=6` is a count of syntactically valid rows, not a check
   that the six rows are the six planned cells; a register of six arbitrary valid citations would
   satisfy the leg (the routed-defect binding lives in the separate `--items` arm only).
7. **Anything about the working tree** — all reads are `git show`; an uncommitted or rewritten
   register is invisible.

## Residual risk and verification gaps

- **The one real hole is reading, not scoring.** `register_mismatches=0` is emitted for an absent
  register (L1). The frozen predicate is safe because of its floors, but every downstream quote of
  that field is only honest next to `register_cells` and the exit code.
- **`commit_distinct` name.** Renaming is out of scope (frozen counter bytes); the report and receipts
  should gloss it once as "rows whose commit cell differs from its receipt_rev cell" so the number is
  not read as distinct commits — especially since `make-cells.py` gives it one value.
- **`make-cells.py` is unlanded and its `stale` template is unsound for 5 of 6 rows** (L3). This is the
  single most actionable finding: as generated, the register will publish false pre-repair readings
  and still pass.
- **Not verified by me (out of this seat's scope):** the `--items` arm's 16 anchors, C2's six legs,
  C3's four mutants, and the after-receipts' own numbers. I also did not test a `COMMIT-NOT-ANCESTOR`
  row through the counter (the class is documented in `commit_checks` and is the mirror of A2, which I
  did test); a row whose `commit` is a *descendant* of `--rev` would need a register committed after
  the audited rev and `--register-rev`, which the frozen predicate never passes.
- **Fixture-only limitation:** the reconciler's `COMMIT-UNNAMED` test is substring containment of
  `commit[:7]`; an anchored line naming a *different* commit that shares the 7-hex prefix would pass.
  I did not construct a 7-prefix collision (≈2×10⁻⁹ per pair at this fixture size); it is a residual
  theoretical weakness, not a measured one.

## Tooling and scratch

- No tool was installed or upgraded; nothing was written outside my scratch dir and this report. No
  mutating git/jj command was issued in the lane (only `log`, `show`, `cat-file -e`, `rev-parse`,
  `merge-base --is-ancestor`, `status`).
- Scratch `/fast/scratch/hyaku/souji-r39/W1RevC1Register` (fixture repo + probes) was **removed** at
  the end of this seat: `rm -rf -- /fast/scratch/hyaku/souji-r39/W1RevC1Register`; no leftover tree.
