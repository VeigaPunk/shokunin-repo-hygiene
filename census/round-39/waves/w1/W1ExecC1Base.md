# W1ExecC1Base — re-measure the C1 control at base, freeze, and lane tip

Seat: W1ExecC1Base (executor, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Role: re-derive the frozen C1 control from committed bytes only, compare it byte-for-byte with
`census/round-39/records/c1-before.txt`, then run the same counter bytes at the freeze revision and
at the then-current lane tip, and classify every item that reads OPEN at the freeze.
No lane bytes were written by this seat. Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecC1Base`
(retained on disk; see §6).

## 0. Revision pins measured

```
$ git rev-parse HEAD                       # first measurement
bbd9b9746ba9e3c5d640bf095bbad18a00c80e83
$ git rev-parse HEAD                       # tip re-measure, after a sibling landed a C2 commit
601195a0cebafa74fedb598e3f55da1708ae63f1
$ git cat-file -e ed30b7f5b77939c9073348d810730bc4f355708d^{commit} && echo base-ok
base-ok
$ git cat-file -e b769bfb84a264d8b284c09bc211d99f39a3e9126^{commit} && echo freeze-ok
freeze-ok
$ git merge-base --is-ancestor ed30b7f5b77939c9073348d810730bc4f355708d b769bfb84a264d8b284c09bc211d99f39a3e9126 && echo base-is-ancestor-of-freeze
base-is-ancestor-of-freeze
$ git merge-base --is-ancestor b769bfb84a264d8b284c09bc211d99f39a3e9126 HEAD && echo freeze-is-ancestor-of-HEAD
freeze-is-ancestor-of-HEAD
```

Commit chain between base and the first measured tip:

```
$ git log --oneline ed30b7f5b77939c9073348d810730bc4f355708d..bbd9b9746ba9e3c5d640bf095bbad18a00c80e83
bbd9b97 round-39: C2 — resolve --rev/--register-rev (exit 2), drift RECORD-MISSING/MALFORMED contract, r39-citation-rev fixture
b769bfb round-39: freeze — prereg C1/C2/C3, counters, fixtures, base controls
```

Verdict: **PASS** — base, freeze and tip are a linear chain; both named revisions resolve to commits.

## 1. Clean checkout state at measurement time

```
$ git status --porcelain --untracked-files=no | wc -l
0
$ sha256sum census/round-39/c1-items.tsv
d892b74f83587a79a83b0c39aff89d1e93a0f8ac0d523f5d02b8a55c76769f34  census/round-39/c1-items.tsv
$ git show HEAD:census/round-39/c1-items.tsv | sha256sum
d892b74f83587a79a83b0c39aff89d1e93a0f8ac0d523f5d02b8a55c76769f34  -
$ sha256sum census/round-39/c1-counter.py
f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed  census/round-39/c1-counter.py
$ git show bbd9b9746ba9e3c5d640bf095bbad18a00c80e83:census/round-39/c1-counter.py | sha256sum
f908590d46234ac3b7da3983f0f76dfef7cb189f13a8c3b30926fc3bef6849ed  -
```

Per-revision byte hashes (sha256, first 12 hex; `cells` = size of `git show rev:census/round-39/cells.tsv`, 0 = blob absent):

```
ed30b7f5b77939c9073348d810730bc4f355708d items=e3b0c44298fc counter=e3b0c44298fc cells=0
b769bfb84a264d8b284c09bc211d99f39a3e9126 items=d892b74f8358 counter=f908590d4623 cells=0
bbd9b9746ba9e3c5d640bf095bbad18a00c80e83 items=d892b74f8358 counter=f908590d4623 cells=0
```

`e3b0c44298fc` is sha256 of the empty byte string: the items table and the counter **do not exist** at
the base revision. The control is therefore necessarily `same items + same counter bytes` taken from
the frozen (working-tree == freeze == HEAD) bytes and pointed at `--rev ed30b7f...`, which is what the
preregistration's CONTROL line states. On-disk items and counter are byte-identical to the freeze and
HEAD blobs, so that clause holds.

Verdict: **PASS** — tracked tree clean; items table and counter bytes on disk are exactly the frozen ones.

## 2. Base-revision control vs the frozen receipt

Exact command (from the seat spec):

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ mkdir -p /fast/scratch/hyaku/souji-r39/W1ExecC1Base
$ TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecC1Base python3 -B census/round-39/c1-counter.py \
    --root . --rev ed30b7f5b77939c9073348d810730bc4f355708d \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv \
    --scratch /fast/scratch/hyaku/souji-r39/W1ExecC1Base
ITEM R39-C1-01 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-01'
ITEM R39-C1-02 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-02'
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
ITEM R39-C1-05 OPEN FILE-ABSENT corpus/lessons/round-39.md
ITEM R39-C1-06 OPEN ANCHOR-ABSENT SKILL.md anchor='R39-C1-06'
ITEM R39-C1-07 OPEN FILE-ABSENT corpus/lessons/round-39.md
ITEM R39-C1-08 OPEN ANCHOR-ABSENT census/round-38/preregistration.txt anchor='R39-C1-08'
ITEM R39-C1-09 OPEN ANCHOR-ABSENT census/round-38/preregistration.txt anchor='R39-C1-09'
ITEM R39-C1-10 OPEN ANCHOR-ABSENT SCORECARD.md anchor='R39-C1-10'
ITEM R39-C1-11 OPEN ANCHOR-ABSENT LOG.md anchor='R39-C1-11'
ITEM R39-C1-12 OPEN ANCHOR-ABSENT LOG.md anchor='R39-C1-12'
ITEM R39-C1-13 OPEN ANCHOR-ABSENT corpus/QUALITY.md anchor='R39-C1-13'
ITEM R39-C1-14 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-14'
ITEM R39-C1-15 OPEN FILE-ABSENT corpus/lessons/round-39.md
ITEM R39-C1-16 OPEN ANCHOR-ABSENT corpus/lessons/round-36.md anchor='R39-C1-16'
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
RC=1
```

The run was repeated with stdout captured to `$S/base-run.txt` and diffed against the frozen receipt:

```
$ diff -u census/round-39/records/c1-before.txt /fast/scratch/hyaku/souji-r39/W1ExecC1Base/base-run.txt \
    && echo "DIFF-CLEAN: base run byte-identical to c1-before.txt"
DIFF-CLEAN: base run byte-identical to c1-before.txt
$ sha256sum census/round-39/records/c1-before.txt /fast/scratch/hyaku/souji-r39/W1ExecC1Base/base-run.txt
d5c3a21acef64d3a63de29198229a233e349ed68ae885ef8d12eb233bcb184a8  census/round-39/records/c1-before.txt
d5c3a21acef64d3a63de29198229a233e349ed68ae885ef8d12eb233bcb184a8  /fast/scratch/hyaku/souji-r39/W1ExecC1Base/base-run.txt
```

Class histogram of the base run:

```
$ awk '{print $4}' .../base-run.txt | grep -v '^$' | sort | uniq -c
     11 ANCHOR-ABSENT
      1 commit_distinct=0
      5 FILE-ABSENT
      1 register_cells=0
```

(i.e. 11 ANCHOR-ABSENT + 5 FILE-ABSENT = 16 items; the two trailing lines are the REGISTER and
SUMMARY tails matched by the crude awk field selector.)

Verdict: **PASS** — `items=16 open=16`, `items_sha=d892b74f8358`, whole stdout byte-identical
(sha256 `d5c3a21a…`) to `census/round-39/records/c1-before.txt`. Exit code 1 is the counter's documented
"any OPEN item" exit, so the control also fails its own predicate — it is not a do-nothing-satisfiable
state, and it is not the `open=0` state the C1 kill rule forbids.

## 3. Same counter bytes at the freeze revision

```
$ TMPDIR=/fast/scratch/hyaku/souji-r39/W1ExecC1Base python3 -B census/round-39/c1-counter.py \
    --root . --rev b769bfb84a264d8b284c09bc211d99f39a3e9126 \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv \
    --scratch /fast/scratch/hyaku/souji-r39/W1ExecC1Base
ITEM R39-C1-01 OPEN ANCHOR-ABSENT corpus/lessons/round-38.md anchor='R39-C1-01'
… (all 16 lines identical to §2 in id, class, file and anchor) …
ITEM R39-C1-16 OPEN ANCHOR-ABSENT corpus/lessons/round-36.md anchor='R39-C1-16'
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1

$ diff -u .../base-run.txt .../freeze-run.txt && echo "BASE==FREEZE byte-identical"
BASE==FREEZE byte-identical
```

**Difference base → freeze: none.** All 16 items, their classes, the REGISTER line, the SUMMARY line,
`items_sha`, and the exit code are identical. The freeze revision changes the measurement by zero bytes.

Why that is the expected result, verified rather than assumed:

```
$ git diff --stat ed30b7f5b77939c9073348d810730bc4f355708d b769bfb84a264d8b284c09bc211d99f39a3e9126
 census/round-39/c1-counter.py            | 265 ++++++++++++++++++++++++++++
 census/round-39/c1-items.tsv             |  22 +++
 census/round-39/c2-counter.py            | 286 +++++++++++++++++++++++++++++++
 census/round-39/c3-counter.py            | 187 ++++++++++++++++++++++++
 census/round-39/preregistration.txt      | 114 ++++++++++++
 census/round-39/records/c1-before.txt    |  18 ++
 census/round-39/records/c2-before.txt    |   7 +
 census/round-39/records/c3-before.txt    |   5 +
 tests/fixtures/r39-citation-rev.py       | 128 ++++++++++++++
 tests/fixtures/r39-drift-record-rules.py | 141 +++++++++++++++++
 10 files changed, 1173 insertions(+)
```

Ten added instrument files, 1173 insertions, **no deletions and no modification of any item target
file**. The 10 item target files are:

```
LOG.md
SCORECARD.md
SKILL.md
census/round-38/preregistration.txt
census/round-39/records/waves-capture.txt
census/round-39/records/waves-wait.txt
corpus/QUALITY.md
corpus/lessons/round-36.md
corpus/lessons/round-38.md
corpus/lessons/round-39.md
```

Intersection with the freeze delta's 10 paths:

```
$ comm -12 item-targets.txt freeze-paths.txt | sed 's/^/TOUCHED: /'
(empty)
```

Verdict: **PASS** — the freeze commit adds instruments only; the item-target intersection is empty and
the counter output at the freeze is byte-identical to the base control.

## 4. Every item OPEN at the freeze, by class

`items=16 open=16` at `b769bfb84a264d8b284c09bc211d99f39a3e9126`, all classes reported by the counter:

**FILE-ABSENT (5)** — the named file does not exist at the freeze:

| id | file |
|---|---|
| R39-C1-03 | `census/round-39/records/waves-wait.txt` |
| R39-C1-04 | `census/round-39/records/waves-capture.txt` |
| R39-C1-05 | `corpus/lessons/round-39.md` |
| R39-C1-07 | `corpus/lessons/round-39.md` |
| R39-C1-15 | `corpus/lessons/round-39.md` |

**ANCHOR-ABSENT (11)** — file exists at the freeze, no line carries the anchor:

| id | file | anchor |
|---|---|---|
| R39-C1-01 | `corpus/lessons/round-38.md` | `R39-C1-01` |
| R39-C1-02 | `corpus/lessons/round-38.md` | `R39-C1-02` |
| R39-C1-06 | `SKILL.md` | `R39-C1-06` |
| R39-C1-08 | `census/round-38/preregistration.txt` | `R39-C1-08` |
| R39-C1-09 | `census/round-38/preregistration.txt` | `R39-C1-09` |
| R39-C1-10 | `SCORECARD.md` | `R39-C1-10` |
| R39-C1-11 | `LOG.md` | `R39-C1-11` |
| R39-C1-12 | `LOG.md` | `R39-C1-12` |
| R39-C1-13 | `corpus/QUALITY.md` | `R39-C1-13` |
| R39-C1-14 | `corpus/lessons/round-38.md` | `R39-C1-14` |
| R39-C1-16 | `corpus/lessons/round-36.md` | `R39-C1-16` |

**PREDICATE-MISSING (0)** — no item reaches the predicate stage at the freeze; 16/16 fail earlier
(absent file or absent anchor). The r38-side items the seat spec singled out
(`R39-C1-08`, `R39-C1-09` on `census/round-38/preregistration.txt`; `R39-C1-16` on
`corpus/lessons/round-36.md`; `R39-C1-01`, `R39-C1-02`, `R39-C1-14` on `corpus/lessons/round-38.md`)
are all OPEN — nothing the freeze added touches those files.

Verdict: **PASS** — 5 FILE-ABSENT + 11 ANCHOR-ABSENT = 16 OPEN at the freeze, matching the receipt.

## 5. Instrument discrimination — the control is not vacuous

A control that reads `open=16` is only meaningful if the same bytes can also print `CLOSED`. Probe
items (scratch only, no lane bytes) against the base revision:

```
$ cat > $S/items-probe.tsv <<'EOF'
id	file	anchor	must	mustnot
TEST-CLOSED	SKILL.md	souji	souji	-
TEST-PRED	SKILL.md	souji	souji	souji
TEST-FILE	scratch-only/absent.txt	zzz	zzz	-
TEST-ANCHOR	SKILL.md	ZZZ-not-in-base-bytes	ZZZ-not-in-base-bytes	-
EOF
$ TMPDIR=$S python3 -B census/round-39/c1-counter.py --root . --rev ed30b7f... \
    --items $S/items-probe.tsv --register census/round-39/cells.tsv --scratch $S
ITEM TEST-CLOSED CLOSED
ITEM TEST-PRED OPEN PREDICATE-MISSING SKILL.md missing=[] hits=94
ITEM TEST-FILE OPEN FILE-ABSENT scratch-only/absent.txt
ITEM TEST-ANCHOR OPEN ANCHOR-ABSENT SKILL.md anchor='ZZZ-not-in-base-bytes'
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=4 open=3 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=6012164d2338
RC=1
```

All four code paths — CLOSED, PREDICATE-MISSING, FILE-ABSENT, ANCHOR-ABSENT — are reachable with the
frozen counter bytes, so `open=16` is a measured absence, not an instrument that cannot close.

Verdict: **PASS** — the counter discriminates; the control's 16 OPENs are genuine.

## 6. Tip re-measure (state drift during this seat's window)

A sibling landed a commit between my first and second tip read:

```
$ git log --oneline bbd9b9746ba9e3c5d640bf095bbad18a00c80e83..HEAD
601195a round-39: C2 — drift docstring puts each trigger on its class line (single-line rule)
$ git diff --name-status bbd9b9746ba9e3c5d640bf095bbad18a00c80e83..HEAD
M	tools/souji-worktree-drift.py
$ comm -12 item-targets.txt tip-delta.txt | sed 's/^/TOUCHED-ITEM-FILE: /'
(empty)
```

C1 re-measured at the advanced tip:

```
$ TMPDIR=$S python3 -B census/round-39/c1-counter.py --root . --rev 601195a0cebafa74fedb598e3f55da1708ae63f1 \
    --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch $S
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1

$ diff -u .../freeze-run.txt .../tip-run.txt && echo "FREEZE==TIP byte-identical"
FREEZE==TIP byte-identical
```

Verdict: **PASS** — C1 before-state is unchanged at tip `601195a0`; no C1 after-data has landed yet,
so the control remains valid for the C1 landing arm.

## 7. Observations and risks for the L1 (not verdicts I can close)

1. **`items_sha` is disk-derived, not revision-derived.** The counter reads `--items` from the working
   tree (`open(args.items)`), so `items_sha` fingerprints the on-disk table, while every per-item read
   is `git show <rev>:<file>` (counter line 196 `open(args.items, …)`, line 202 the sha, line 207
   `git_show(root, args.rev, row["file"])`). Proven: the probe run's
   `items_sha=6012164d2338` is sha256 of `$S/items-probe.tsv`, not of anything at `--rev`. Today disk ==
   freeze == HEAD (`d892b74f8358`), so the control is sound, but any sibling write to the
   working-tree `c1-items.tsv` would silently move the SUMMARY sha without touching `--rev` bytes.
   Recommendation for the C1 landing seat: re-assert `sha256sum census/round-39/c1-items.tsv` equals
   `d892b74f8358…` in the same shell as the landing run.
2. **The register leg short-circuits at the control.** `census/round-39/cells.tsv` does not exist at
   base, freeze, HEAD (`bbd9b97`) or tip (`601195a`) — `git show` on it fails at all four
   (`find` over the lane shows only `./census/round-38/cells.tsv`). The counter returns
   `0, 0, "REGISTER-ABSENT"` before it invokes the reconciler (committed counter lines 154-155), so
   `REGISTER cells=0` is evidence of register absence, **not** of reconciler behaviour. The control
   receipt carries no information about the `register_cells>=6` / `commit_distinct>=2` floors — those
   are only exercised by the landing arm.
3. **`PREDICATE-MISSING` diagnostic is lossy.** Probe `TEST-PRED` prints `missing=[]` because the must
   token is present on the line and it is the `mustnot` token that blocks it; the diagnostic only lists
   absent `must` tokens. The predicate verdict is correct; only the message is uninformative. Affects no
   frozen quantity (no item reaches this path at base/freeze).
4. **Transient untracked file during measurement.** At 14:51:39 one `git status --porcelain` line
   appeared and was gone on the next invocation; `--untracked-files=no` stayed 0 and the tracked blobs
   did not move. Recorded because calibration claims are about state; the measurement reads committed
   bytes only (`git show`) and is unaffected.
5. Lane tip is moving under this wave (`bbd9b97` → `601195a` during this seat's window). Re-pin the C1
   landing measurement to the tip that actually carries the landing commit, not to any rev quoted here.

## 8. Scratch state

`/fast/scratch/hyaku/souji-r39/W1ExecC1Base` is **still on disk** (retained deliberately so the L1 can
re-run/diff):

```
base-run.txt      1292 B   sha256 basis for §2
freeze-run.txt    1292 B   §3
head-run.txt      1292 B   run at bbd9b97
tip-run.txt       1292 B   run at 601195a
items-probe.tsv    211 B   §5
item-targets.txt   245 B   §3
freeze-paths.txt   345 B   §3
tip-delta.txt               §6
```

No `souji-r39-c1.*` temp dirs were left behind (the counter `shutil.rmtree`s its own scratch).
No tool installs or upgrades were performed by this seat.

## Overall verdict

**C1 control CONFIRMED.** `python3 -B census/round-39/c1-counter.py` with the frozen bytes and the
frozen items table, pointed at `ed30b7f5b77939c9073348d810730bc4f355708d`, reproduces
`census/round-39/records/c1-before.txt` byte-for-byte (sha256 `d5c3a21acef6…`), reading
`items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358` with
exit 1. At the freeze revision `b769bfb84a264d8b284c09bc211d99f39a3e9126` the output is byte-identical
(zero difference), because the freeze commit adds 10 instrument files and no item target file; all 16
items stay OPEN — 5 FILE-ABSENT (R39-C1-03, -04, -05, -07, -15) and 11 ANCHOR-ABSENT (R39-C1-01, -02,
-06, -08, -09, -10, -11, -12, -13, -14, -16), none PREDICATE-MISSING. The control is not
do-nothing-satisfiable (exit 1, `open=16`) and the counter demonstrably discriminates CLOSED from the
three OPEN classes on base bytes.
