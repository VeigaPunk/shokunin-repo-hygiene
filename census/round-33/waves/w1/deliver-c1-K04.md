# C1 K04 — SCORECARD.md:155 restatement (value drift)

Item: K04, SCORECARD.md:155 at base 6017a482e7068d5afb7617640198fbb0fe743357; frozen exit `0`;
frozen predicate `\b5/5\b || \btotal=5\b && \bfailed=0\b`;
files `tests/fixtures/r13-repo-structure.sh,tools/souji-repo-structure.sh`;
frozen argv `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`.

Kind: **VALUE DRIFT** (the row's own argv still runs and still exits 0; its selftest count moved 5/5 → 7/7).
Not an argv correction.

## Row (append under `### Round 33 capability currency`)

ROW-BEGIN
| K04 | SCORECARD.md:155 | restated | 0 | same | `selftest=PASS ids=7/7` | 728b2ce71acbe574ae3036b456724d0a3d6f8f08 | selftest grew from 5 to 7 cases at 728b2ce: round-25 added the linked-common-dir and colocated-vs-plain probe cases, all PASS |
ROW-END

Full appended block as proved in scratch (header + table header + row, one section for the whole wave; the table
header matches the K18 delivery already in this wave):

```
### Round 33 capability currency

Restatements of capability rows above whose stated outcome no longer reproduces. Original rows are unchanged (append-only); each cause commit is executed by `census/round-33/c1-counter.py`.

| id | row | status | exit | run | statement | cause | reason |
|---|---|---|---|---|---|---|---|
| K04 | SCORECARD.md:155 | restated | 0 | same | `selftest=PASS ids=7/7` | 728b2ce71acbe574ae3036b456724d0a3d6f8f08 | selftest grew from 5 to 7 cases at 728b2ce: round-25 added the linked-common-dir and colocated-vs-plain probe cases, all PASS |
```

## Receipts

Scratch: `/fast/scratch/hyaku/souji-r33/RestateK04/` (`TMPDIR=$D/tmp`, a fresh `tmp/rN` per run).
Clone: `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin $D/c`, origin removed at once,
`git -C $D/c rev-parse --show-toplevel` → `/fast/scratch/hyaku/souji-r33/RestateK04/c`,
detached at `2d9bca55a9f042a2c9ed60a797a8069e74c41f46` (preregistration commit; its SCORECARD.md is byte-identical
to base `6017a48` — `cmp` clean, 494 lines, so line 155 is the same row at both revisions).

### 1. Frozen argv, 3 runs, fresh TMPDIR each (cwd = clone root, GIT_CONFIG_NOSYSTEM=1)

`bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh`

run 1: `rc=0`; stdout (every line, `$TMPDIR/tmp/r1`):
```
git_version=git version 2.56.0
probe_mode=tool:tools/souji-repo-structure.sh
fixture_repo=/fast/scratch/hyaku/souji-r33/RestateK04/tmp/r1/souji-r13-repo-structure.sCoVec/repo
fixture_git_dir=/fast/scratch/hyaku/souji-r33/RestateK04/tmp/r1/souji-r13-repo-structure.sCoVec/repo/.git
id=SOUJI-R13-STRUCT-manifest-control case=manifest-control content_delta=seen stat_delta=seen mtime_delta=seen restore=equal verdict=PASS
id=SOUJI-R13-STRUCT-write-free case=write-free rc=0 manifest_entries=41 verdict=PASS
id=SOUJI-R13-STRUCT-object-metrics case=object-metrics checks=29 verdict=PASS
id=SOUJI-R13-STRUCT-bogus-repo case=bogus-repo plain_dir_rc=2 missing_rc=2 verdict=PASS
id=SOUJI-R13-STRUCT-promisor-refusal case=promisor-refusal promisor_rc=2 partial_rc=2 verdict=PASS
id=SOUJI-R13-STRUCT-linked-common-dir case=linked-common-dir rc=0 common_entries=53 private_entries=9 checks=8 control=PASS verdict=PASS
id=SOUJI-R13-STRUCT-colocated-vs-plain case=colocated-vs-plain plain_rc=0 colocated_rc=0 others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8 precondition=colocated-not-interchangeable-with-plain-baseline verdict=PASS
selftest=PASS ids=7/7
```
stderr: empty.

run 2 (`tmp/r2`, mkdtemp suffix `UK0XOq`): `rc=0`, identical 8 lines, `selftest=PASS ids=7/7`.
run 3 (`tmp/r3`, mkdtemp suffix `GdiXiu`): `rc=0`, identical 8 lines, `selftest=PASS ids=7/7`.

Predicate check on each run (whitespace-collapsed stdout+stderr):
`\b5/5\b` False, `\btotal=5\b` False, `\bfailed=0\b` False → the frozen predicate fails on all three runs.
The row states `→ 5/5`; the run states `selftest=PASS ids=7/7`. Exit still 0, so the only stale part is the count.

The line that carries the row's claim (the claim is "the selftest passes N/N") is the summary line
`selftest=PASS ids=7/7` — chosen as the statement.

### 2. Cause: first commit at which the original outcome stops holding

Only three commits in the lane touch either frozen file:

```
git -C $D/c log --reverse --format='%H %ad %s' --date=short -- tests/fixtures/r13-repo-structure.sh tools/souji-repo-structure.sh
6ed10a7cd6c7b26f8068dd6e02497e860f9c4317 2026-10-20 round-13: bounded quarantine, declared-evidence gate and F2 census
728b2ce71acbe574ae3036b456724d0a3d6f8f08 2026-10-25 round-25: integrate claims, sources, lessons and wave evidence
98e5203d45b4e419a9e72801733d93303acc7ebd 2026-10-26 round-32: C2 scratch discipline — 26 tools and fixtures take scratch from TMPDIR ...
```

Run at each (same argv, fresh TMPDIR):

| rev | rc | summary line | frozen predicate |
|---|---|---|---|
| 6ed10a7 (row's own round) | 0 | `selftest=PASS ids=5/5` | holds |
| 679e2d0 = first parent of 728b2ce | 0 | `selftest=PASS ids=5/5` | holds |
| 728b2ce (cause) | 0 | `selftest=PASS ids=7/7` | **fails** |
| 98e5203 | 0 | `selftest=PASS ids=7/7` | fails |

So the first failure is `728b2ce71acbe574ae3036b456724d0a3d6f8f08`; it holds at its first parent
`679e2d02f46ec06447d679d9395d6592c5e35f5c` ("round-25: exercise size-census bare and refusal edge cases") and stops
holding at the cause — the counter's value-drift shape (True/False).

Cause touches an item file: `git show --name-only --format= -- 728b2ce` names
`tests/fixtures/r13-repo-structure.sh` (plus a wave copy `.ufo/waves/round-25/w1/r13-repo-structure.sh`), diffstat
`1 file changed, 242 insertions(+), 7 deletions(-)` — `tools/souji-repo-structure.sh` is unchanged.
Ancestry: `git merge-base --is-ancestor 728b2ce 2d9bca5` → true.

What the cause did, from its own diff: it added two probe cases and their emits —
`emit SOUJI-R13-STRUCT-linked-common-dir linked-common-dir …` and
`emit SOUJI-R13-STRUCT-colocated-vs-plain colocated-vs-plain …` — plus the expected-id list, whose own new comment
states the two final lines: `selftest=PASS ids=6/6` (baseline mode) or `selftest=PASS ids=7/7` (`--probe` mode).
The row's argv passes `--probe`, hence 7/7.

### 3. Scratch landing + counter (the proof)

Canonical block appended at 2d9bca55 in the scratch clone, committed with a throwaway identity:
scratch landing commit `4f7fd6370106022f20dad3fe9d1d11b020e13e6e` (working tree clean afterwards).

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
  --root /fast/scratch/hyaku/souji-r33/RestateK04/c \
  --rev 4f7fd6370106022f20dad3fe9d1d11b020e13e6e \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --scratch /fast/scratch/hyaku/souji-r33/RestateK04/cnt --only K04
ITEM	K04	AGREE	restated	rc=0 expect_exit=0 statement is an output line last=selftest=PASS ids=7/7
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=4f7fd6370106022f20dad3fe9d1d11b020e13e6e
counter rc=0
```

The same row was also proved under the alternative heading `### Round 33 capability currency (C1, appended)`
(scratch commit `2b41f5fd6cb4eb06a247af2ff2830100565857a0`): same `AGREE` line, `partial=1`, rc=0.

### 4. Falsifiers run in scratch (the row is not gameable)

* Do-nothing at list-rev (no restatement row at all):
  `--rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46` → `ITEM K04 MISMATCH original rc=0 expect_exit=0 predicate fails last=selftest=PASS ids=7/7`, `SUMMARY items=1 agree=0 mismatches=1`, rc=1. The row is necessary.
* Non-causal commit (cause = `98e5203`, which touches the fixture but where the outcome was already 7/7 at its
  parent): `ITEM K04 MISMATCH restated BAD-CAUSE(original at parent=False at cause=False; need True/False)`, rc=1.
* Substring statement (`` `ids=7/7` `` instead of the complete line): `ITEM K04 MISMATCH restated rc=0 expect_exit=0
  statement is not a digit-bearing output line last=selftest=PASS ids=7/7`, rc=1.
* Incidental: the counter's append-only gate fired (exit 2, `SCORECARD.md at --rev does not start with its
  --list-rev bytes`) on an intermediate falsifier commit that had rewritten an earlier `728b2ce` occurrence; the
  gate is live.

## Growth or regression?

**GROWTH.** The fixture's own selftest went from 5 to 7 cases and all seven pass (`ids=7/7`, exit 0, every
`verdict=PASS`). The five cases the row originally certified are all still present and still PASS
(`manifest-control`, `write-free`, `object-metrics`, `bogus-repo`, `promisor-refusal` — the same five ids, in the
same order, as the 5/5 run at 6ed10a7); the two added ones (`linked-common-dir`, `colocated-vs-plain`) are additional coverage of
common-store identity and colocated/plain divergence. No capability was lost, so nothing is reported as a regression;
the stale part is only the stated count in the row.

## Scratch cleanup

`/fast/scratch/hyaku/souji-r33/RestateK04` removed after these receipts were copied (the counter's own `--scratch`
work tree is self-removed; `cnt/` held only that work tree).
