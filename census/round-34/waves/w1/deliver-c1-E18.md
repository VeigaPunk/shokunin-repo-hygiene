# C1 delivery — E18 (SCORECARD.md:71, tests/fixtures/r13-repo-structure.sh + tools/souji-repo-structure.sh)

Verdict: **MISMATCH at base — genuinely stale, one restatement row drafted (`same` argv, value drift).**

## Counter ITEM line (verbatim)

```
ITEM	E18	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=selftest=PASS ids=7/7 load=5.87
```

## Command (executed)

```
export TMPDIR=/fast/scratch/hyaku/souji-r34/RestateC1s9/tmp
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 9c76c7222a8abff027af42e37f0d160d52526bba \
  --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 \
  --scratch /fast/scratch/hyaku/souji-r34/RestateC1s9/cnt --only E16,E17a,E17b,E18,E19
```

Exit 0 (the counter exits 0 because every listed run completed; the item verdict is MISMATCH).
Load before/after: `3.94 3.11 2.10` / `5.87 3.52 2.24`. Serialization: counter's own Q77 flock at `<scratch>/c1.lock`.
Counter bytes at `--list-rev`: sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20`.
Lane HEAD at read time: `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`.

## The stale cell (base SCORECARD.md:71)

```
| r13 structure entry recheck (freshness; not a claim) | — | `git-repo-structure-readonly.md` verified on git 2.55.0 only, r16 note "pending recheck" | `selftest=PASS ids=5/5` on git 2.56.0 (`census/round-24/records/r13-recheck-receipt.tsv`) | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | fixture sha256 `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` |
```

The row's own argv now exits 0 but prints `selftest=PASS ids=7/7` as its last line, so the stated
`selftest=PASS ids=5/5` no longer describes the run: exit matches, predicate does not.

## Prior-correction / supersession sweep (Q76) — no row binds this cell

```
grep -n -F 'SCORECARD.md:71' <base SCORECARD.md>                 → no match
grep -n 'r13-repo-structure|ids=5/5|ids=7/7' <base SCORECARD.md> → 42, 71, 155, 325, 371, 502
grep -n '^| E1[6789]' <base SCORECARD.md>                        → no match
```

The six hits are: line 42 (a round-25 measurement row that *documents* the growth at the r25 candidate), line 71 (the
stale r24 cell itself), line 155 (the **r13 capability** row `repository structure census … → 5/5`), line 325
(`R30-CORRECTION SCORECARD.md:155 R04 rc=0 observed=selftest=PASS ids=7/7`), line 371 (`| L05 | SCORECARD.md:155 | ids=7/7 | …`),
line 502 (`| K04 | SCORECARD.md:155 | restated | 0 | same | selftest=PASS ids=7/7 | 728b2ce… | …`).
Every correction binds **SCORECARD.md:155**, not 71. Because c1-items.tsv deduplicates by (argv, statement) and K04's
restated statement is `ids=7/7`, the r24 row's `(argv, ids=5/5)` pair survived enumeration as its own item — and that
cell is still uncorrected. So this is a genuine stale cell, not a Q76 carry.

## Cause commit (walked and executed)

History of the item's files at base (`git -C <lane> log --reverse --format=%H -- tests/fixtures/r13-repo-structure.sh tools/souji-repo-structure.sh`):

```
6ed10a7cd6c7b26f8068dd6e02497e860f9c4317   round-13: bounded quarantine, declared-evidence gate and F2 census
728b2ce71acbe574ae3036b456724d0a3d6f8f08   round-25: integrate claims, sources, lessons and wave evidence
98e5203d45b4e419a9e72801733d93303acc7ebd   round-32: C2 scratch discipline …
```

`6ed10a7` cannot be the cause (its parent does not carry the fixture, so the original could not hold there). One scratch
clone per revision (`git clone -q --no-local --no-checkout`, detached, origin removed, toplevel asserted =
`/fast/scratch/hyaku/souji-r34/RestateC1s9/runs/<rev>/c`; `env -i PATH=<jj symlink dir>:/usr/bin:/bin TMPDIR=<fresh>
GIT_CONFIG_NOSYSTEM=1 HOME LANG=C.UTF-8`), item argv executed from the clone root:

```
=== rev=679e2d02f46e (parent) rc=0 load=12.34
git_version=git version 2.56.0
probe_mode=tool:tools/souji-repo-structure.sh
fixture_repo=/var/tmp/souji-r13-repo-structure.AA8fuu/repo
...
id=SOUJI-R13-STRUCT-promisor-refusal case=promisor-refusal promisor_rc=2 partial_rc=2 verdict=PASS
selftest=PASS ids=5/5                 ← original (exit 0, predicate ids=5/5) HOLDS

=== rev=728b2ce71acb (cause) rc=0 load=12.34
git_version=git version 2.56.0
probe_mode=tool:tools/souji-repo-structure.sh
fixture_repo=/var/tmp/souji-r13-repo-structure.o9vHmf/repo
...
id=SOUJI-R13-STRUCT-linked-common-dir case=linked-common-dir rc=0 common_entries=53 private_entries=9 checks=8 control=PASS verdict=PASS
id=SOUJI-R13-STRUCT-colocated-vs-plain case=colocated-vs-plain plain_rc=0 colocated_rc=0 others_plain=0 others_colocated=2 commits_plain=1 commits_colocated=2 differing_keys=8 precondition=colocated-not-interchangeable-with-plain-baseline verdict=PASS
selftest=PASS ids=7/7                 ← original FAILS

=== rev=2b0171e2071f (list-rev) rc=0 load=6.21
LASTDIGIT: selftest=PASS ids=7/7

=== rev=9c76c7222a8a (base) rc=0 load=6.21
LASTDIGIT: selftest=PASS ids=7/7
```

Cause full40: `728b2ce71acbe574ae3036b456724d0a3d6f8f08` (parent `679e2d02f46ec06447d679d9395d6592c5e35f5c`;
ancestor of `--list-rev` verified: `git merge-base --is-ancestor 728b2ce… 2b0171e2…` → true).
It touches the item's file `tests/fixtures/r13-repo-structure.sh` (1 of 181 paths in `git show --name-only --format=`), whose
diff adds the `SOUJI-R13-STRUCT-linked-common-dir` and `SOUJI-R13-STRUCT-colocated-vs-plain` probe cases and renumbers the
header comment from `ids=5/5` (`--probe`) to `ids=7/7`.

## Statement binding (A1(c))

The restated statement is the run's collapsed **LAST** digit-bearing line, identical at base and at `--list-rev`:
`selftest=PASS ids=7/7`. Exit is 0. The corrected argv cell is `same` — the frozen argv already names the row's own
script (`tests/fixtures/r13-repo-structure.sh`), so no argv correction is involved.

## Proposed restatement row (verbatim, for `### Round 34 registry restatements`)

```
| E18 | SCORECARD.md:71 | restated | 0 | same | `selftest=PASS ids=7/7` | 728b2ce71acbe574ae3036b456724d0a3d6f8f08 | round-25 728b2ce added the linked-common-dir and colocated-vs-plain probe cases, so the same argv prints ids=7/7 and the r24 recheck cell kept the ids=5/5 literal |
```

L1 note: the heading `### Round 34 registry restatements` does **not** yet exist in SCORECARD.md (grep at tip and in the
worktree: no match). It must be appended together with this row, or the counter's `load_restatements` sees no section.

## Row verification (executed end-to-end, scratch clone)

Appended the heading + the row above to a `--no-local` clone of the lane checked out at list-rev
`2b0171e2071fdc9c16a69bed12b0d040e574d8c8` (toplevel asserted = `/fast/scratch/hyaku/souji-r34/RestateC1s9/sim/c`),
committed with a throwaway identity (`128fe31c1299e6255b5ddd261ad54ede63a564f0`), then ran the counter against it:

```
ITEM	E18	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=selftest=PASS ids=7/7 load=7.84
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=128fe31c1299e6255b5ddd261ad54ede63a564f0
```

Negative control on the same clone — the **later** file-touching commit as cause
(`98e5203d45b4e419a9e72801733d93303acc7ebd`) is refused, which proves 728b2ce is the first failing file-touching commit:

```
ITEM	E18	MISMATCH	restated	BAD-CAUSE(original at parent=False at cause=False; need True/False)
SUMMARY items=1 agree=0 mismatches=1 restated=1 partial=1 rev=798bee8cc7e363f3f91135b5f386735a8abea973
```

## Proposed restatement row

See the verbatim row above; nothing else proposed. No frozen predicate, target, item or leg is proposed for change.
