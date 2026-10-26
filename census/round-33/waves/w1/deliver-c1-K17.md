# C1 K17 — SCORECARD.md:174 restatement (value drift, growth)

Item: K17, SCORECARD.md:174 at base 6017a482e7068d5afb7617640198fbb0fe743357; frozen exit `0`;
frozen predicate `\b8/8\b && control=FALSE-GREEN-REJECTED && lost_found=WRITE-DETECTED || \bcases=8 pass=8\b && control=FALSE-GREEN-REJECTED && lost_found=WRITE-DETECTED`;
files tests/fixtures/r24-size-census.py,tools/souji-size-census.py;
frozen argv `python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py`.

Kind: VALUE DRIFT. The stated outcome (`8/8` / `cases=8 pass=8`) held at the cause's parent and stopped holding at the
cause, which added four cases. The argv is unchanged and correct (`same`).

## Row (append under `### Round 33 capability currency`)

ROW-BEGIN
| K17 | SCORECARD.md:174 | restated | 0 | same | `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | 679e2d02f46ec06447d679d9395d6592c5e35f5c | selftest grew from 8 to 12 cases at the round-25 bare and refusal edge-case commit: cases 9-12 added, all pass |
ROW-END

Full appended block as proved in scratch (header + table header + row):

```
### Round 33 capability currency (C1, appended)

| id | row | status | exit | run | statement | cause | reason |
|---|---|---|---|---|---|---|---|
| K17 | SCORECARD.md:174 | restated | 0 | same | `cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | 679e2d02f46ec06447d679d9395d6592c5e35f5c | selftest grew from 8 to 12 cases at the round-25 bare and refusal edge-case commit: cases 9-12 added, all pass |
```

Placement constraint for the L1: the counter requires SCORECARD.md at `--rev` to START WITH its `--list-rev` bytes,
so the whole appended section must sit at EOF (any insertion before the end breaks the prefix check). The heading
`### Round 33 capability currency (C1, appended)` starts with the counter's `SECTION` constant, so the suffix is
accepted.

## Receipts

Scratch: `/fast/scratch/hyaku/souji-r33/RestateK17/` (`TMPDIR=/fast/scratch/hyaku/souji-r33/RestateK17/tmp`, fresh
subdir per run). Clone: `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin
/fast/scratch/hyaku/souji-r33/RestateK17/c`, origin removed at once, `rev-parse --show-toplevel` ->
`/fast/scratch/hyaku/souji-r33/RestateK17/c`, detached at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`.

### 1. Frozen argv, 3 runs at 2d9bca55, fresh TMPDIR each (cwd = clone root, GIT_CONFIG_NOSYSTEM=1)

`python3 -B tests/fixtures/r24-size-census.py --tool tools/souji-size-census.py`

rc run 1 = 0, rc run 2 = 0, rc run 3 = 0. All three printed byte-identical stdout; digit-bearing lines (run 1,
verified identical in runs 2 and 3):

```
CASE 1 clean PASS exit=0 counts=0,0,0,0 manifest_changed=0
CASE 2 dangling PASS exit=0 counts=0,0,1,0 manifest_changed=0 lost_found_dir=False
CASE 3 garbage PASS main[exit=0 counts=1,2,0,0 manifest_changed=0] linked[exit=0 counts=1,2,0,0 manifest_changed=0]
CASE 4 linked PASS exit=0 counts=0,0,0,0 manifest_changed=0 raw_linked_garbage=1
CASE 5 alternates PASS exit=0 counts=0,0,3,1 manifest_changed=0 alt_manifest_changed=0
CASE 6 refusal PASS lost_found_argv[exit=2 counts=none manifest_changed=0] partial_clone[exit=2 counts=none manifest_changed=0] promisor_unset[exit=2 counts=none manifest_changed=0]
CASE 7 detector PASS fsck_exit=0 manifest_changed=4 lost_found_other_oid=True
CASE 8 control PASS stub_failed=dangling,garbage,alternates
CASE 9 bare-nonempty PASS exit=0 counts=0,0,0,0 manifest_changed=0 invoked_from_bare=True
CASE 10 bare-empty PASS exit=1 counts=none manifest_changed=0 stderr_git_failure=True stderr_no_default_references=True stdout_counts_line=False
CASE 11 subdir PASS exit=2 counts=none manifest_changed=0 stderr_must_name_repo=True
CASE 12 partialClone-only PASS exit=2 counts=none manifest_changed=0 stderr_partial_clone=True
cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
```

The complete line carrying the row's claim is the summary: `cases=12 pass=12 control=FALSE-GREEN-REJECTED
lost_found=WRITE-DETECTED` — it holds both `cases=`/`pass=` digits and the two control facts the old row stated.
The old row's `8/8` and `cases=8` no longer occur anywhere in the output.

### 2. First commit where the original outcome stops holding

Commit list for the two frozen files (`log --reverse --format=%H %s -- <files>`) has five entries:
`1efe406`, `778747e`, `315422b`, `679e2d0`, `98e5203`. The argv was executed at each entry and at the cause's first
parent `7e4dbef` (a commit that does not touch either file):

| rev | subject | rc | summary line | holds frozen (exit 0 + `8/8`/`cases=8` + control) |
|---|---|---|---|---|
| 1efe406e7f39b8fe736be2a566053703a571ffc0 | round-24: instruments | 0 | `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` | True |
| 778747eb671f8e85ef5387bc3d7023337b30467c | round-24: after-state | 0 | `cases=8 pass=8 ...` | True |
| 315422ba9970f03c27f8a9184446783b7fcdf0a7 | round-24: final | 0 | `cases=8 pass=8 ...` | True |
| 7e4dbef94061578fca2f58621f87908c886cc431 | (cause's first parent; does not touch the files) | 0 | `cases=8 pass=8 ...` | True |
| 679e2d02f46ec06447d679d9395d6592c5e35f5c | round-25: exercise size-census bare and refusal edge cases | 0 | `cases=12 pass=12 ...` | **False** |
| 98e5203d45b4e419a9e72801733d93303acc7ebd | round-32: C2 scratch discipline | 0 | `cases=12 pass=12 ...` | False |
| 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 | preregistration | 0 | `cases=12 pass=12 ...` | False |

`679e2d0` is the FIRST failing commit; nothing earlier stops the statement holding. It names
`tests/fixtures/r24-size-census.py` in `git show --name-only` (an item file), so the value-drift branch applies.
Its fixture header at that commit reads: "with the refusal-surface cases 9-12 (bare-nonempty, bare-empty, subdir,
partialClone-only)".

### 3. Scratch landing + counter (the proof)

Appended the block above to SCORECARD.md at 2d9bca55 in the scratch clone (6 inserted lines, nothing else changed);
committed with throwaway identity: scratch landing commit `4a2d2ca1c33fa303b2ebb3c01074c92fa4d4b2a3`.

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
  --root /fast/scratch/hyaku/souji-r33/RestateK17/c \
  --rev 4a2d2ca1c33fa303b2ebb3c01074c92fa4d4b2a3 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --scratch /fast/scratch/hyaku/souji-r33/RestateK17/cnt --only K17
ITEM	K17	AGREE	restated	rc=0 expect_exit=0 statement is an output line last=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=4a2d2ca1c33fa303b2ebb3c01074c92fa4d4b2a3
counter rc=0
```

Do-nothing control on the same clone (no appended row, `--rev` = base):

```
--rev 6017a482e7068d5afb7617640198fbb0fe743357 --only K17
ITEM	K17	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED
SUMMARY items=1 agree=0 mismatches=1 restated=0 partial=1 rev=6017a482e7068d5afb7617640198fbb0fe743357
counter rc=1
```

## Growth or regression?

GROWTH, not a regression. Case count rose 8 -> 12 with `pass=12`, `control=FALSE-GREEN-REJECTED` kept, and
`lost_found=WRITE-DETECTED` kept: the four added cases (bare-nonempty, bare-empty, subdir, partialClone-only) are
new refusal/bare surfaces, and cases 1-8 still pass unchanged with identical counts. No capability lost, no figure
withdrawn. The row is therefore corrected to the current 12-case summary, not restated as a defeat. The only
stale prose is in the row's own description cell ("over 8 frozen cases"), which is NOT edited (append-only); the
appended row supersedes the number.

## Risks noted for the L1

- The row's justification text (description cell) still says "8 frozen cases". The counter only judges the stated
  outcome, so this is out of the counter's reach; it is recorded here rather than silently left.
- The section must be the LAST bytes of SCORECARD.md (prefix rule above) and the K17 row must be the only K17 row in
  it (a duplicate is BAD-ROW).

## Scratch cleanup

`/fast/scratch/hyaku/souji-r33/RestateK17` removed after these receipts were copied out (the counter self-removes
its own `--scratch` work dir).
