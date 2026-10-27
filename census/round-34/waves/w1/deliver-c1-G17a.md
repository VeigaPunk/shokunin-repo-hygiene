## Item G17a — MISMATCH at base and at the tip; genuinely stale; the honest restatement is NOT admissible under the frozen contract (see Attack log)

Frozen item (census/round-34/c1-items.tsv @ 2b0171e2):
`G17a	SKILL.md:241	0	SUMMARY total=1 pass=1 fail=0	tests/fixtures/r21-source-refs.py,census/round-21/run-acceptance.py	{REV}	python3 tests/fixtures/r21-source-refs.py --runner census/round-21/run-acceptance.py --root {CLONE} --rev {REV} --work {SCRATCH}/srefs`

### Counter reading (base 9c76c7222a8abff027af42e37f0d160d52526bba)

```
ITEM	G17a	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY total=1 pass=0 fail=1 load=4.15
SUMMARY items=1 agree=0 mismatches=1 restated=0 partial=1 rev=9c76c7222a8abff027af42e37f0d160d52526bba
EXIT=1
```
Command: `flock <scratch>/tmp/c1s3.lock python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/RestateC1s3/cnt --only G17a`; exit 1; `cat /proc/loadavg` = 4.15 3.13 2.09.

### Counter reading (tip 51acb5fb6fa38a6b593b3badb674cec559d7eb2c)

```
ITEM	G17a	MISMATCH	original	rc=1 expect_exit=0 predicate fails last=SUMMARY total=1 pass=0 fail=1 load=38.86
```
Same argv, `--rev 51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; exit 1.

### Prior correction / supersession check (SCORECARD.md @ base)

```
grep -c 'G17a' SCORECARD.md@base = 0
grep -c 'SKILL.md:241' SCORECARD.md@base = 0
grep -c 'r21-source-refs' SCORECARD.md@base = 0
grep -c 'run-acceptance' SCORECARD.md@base = 1   # line 494, r33 trend row, not a correction row
git show 9c76c722...:SCORECARD.md | grep -n '^###.*restate'  -> no match
```
No prior correction or supersession binds the cell (Q76 does not discharge it).

### Why it is stale (executed)

Manual runs of the frozen argv at one clone per commit (fresh TMPDIR per commit, `env -i PATH=/usr/bin:/bin`, `GIT_CONFIG_NOSYSTEM=1`, clone toplevel asserted):

| commit | role | reading |
| --- | --- | --- |
| 7a6667cd27652baf8d704b5cdb8e3200bd6e27a1 | parent of the drift cause | `CASE pass refs/remotes/synthetic/main runner_exit=0 matched=18` / `SUMMARY total=1 pass=1 fail=0` / EXIT=0 (load 11.53) |
| 98e5203d45b4e419a9e72801733d93303acc7ebd | drift cause (round-32 C2 scratch discipline) | `CASE FAIL ... runner_exit=1 matched=16` / `SUMMARY total=1 pass=0 fail=1` / EXIT=1, stderr `bwrap: Can't chdir to /var/tmp/souji-r21-replay-pxvgwvzs/src: No such file or directory` (load 11.65) |
| a416d0b26495ce78b76ea82316533bd8a9ef368c | parent of a7c35c24 (r33 C1) | matches 16, the same two steps red (load 7.91) |
| a7c35c24bdd8bae5cff9766ace02a81915756701 | latest writer of census/round-21/run-acceptance.py | matches 16, the same two steps red (load 7.83) |
| 4eb2fda51c9917abd734c7e411f98cbb59c5c0fe | author of the SKILL.md:242 row text | matches 18, EXIT=0 (load 16.19) |
| 54eb2d0fb81e9cb5cf5b30430bcfa4b67ddc84ec | author of the SKILL.md:241 line text | fixture absent: `can't open file .../tests/fixtures/r21-source-refs.py`, EXIT=2 (load 30.82) |

Red steps in the 16/18 reading: `r20-audit-contract`, `r20-input-binding`; both carry `returncode=1` and stderr `bwrap: Can't chdir to /var/tmp/souji-r21-replay-<rand>/src`. Their `_private_var_tmp()` guard (added by 98e5203d) binds a private dir over `/var/tmp`, then `--chdir os.getcwd()` where the cwd is the r21 runner's replay clone under `/var/tmp/souji-r21-replay-*/src`; inside the new namespace that path is gone, so bwrap refuses before the fixture runs. The row's documented alternate arm still works: `--keep-only` at base prints `SUMMARY total=1 pass=1 fail=0`, EXIT=0 (load 26.50).

`git show --name-only --format= 98e5203d...` names `tests/fixtures/r20-audit-contract.py` and `tests/fixtures/r20-input-binding.py`; it names neither `tests/fixtures/r21-source-refs.py` nor `census/round-21/run-acceptance.py` (grep rc=1).

### Honest proposed row (correct reading of the stale claim)

| G17a | SKILL.md:241 | restated | 1 | same | `SUMMARY total=1 pass=0 fail=1` | 98e5203d45b4e419a9e72801733d93303acc7ebd | r21 replay: round-32 scratch discipline gave the replayed r20 fixtures a private-/var/tmp bwrap re-exec; bwrap cannot chdir to the runner's /var/tmp replay clone, so 16/18 steps match |

Executed shape: exit 1, statement is the run's collapsed LAST digit-bearing line, cause is an ancestor of --list-rev, original holds at the cause's parent (7a6667cd) and fails at the cause (98e5203d).

**Admissibility probe (executed, scratch clone only):** appending exactly this row to SCORECARD.md in a throwaway clone of the lane (tree at 2b0171e2) and running the frozen counter gives

```
ITEM	G17a	MISMATCH	restated	BAD-ROW(cause touches none of the item files)
SUMMARY items=1 agree=0 mismatches=1 restated=1 partial=1 rev=c083dd70e4c4a82bcf8877fcb6b168e0812ffec6
```
i.e. the frozen `files` column omits the two fixtures that actually drifted, so the true cause cannot bind. An r33 cause cannot substitute: cause a7c35c24 → `BAD-CAUSE(original at parent=False at cause=False; need True/False)` (reproduced, rev d2a1c5fb38be002079f6303ee56e53df63b682de).

**No honest row is deliverable.** Any admissible argv-correction row must cite `54eb2d0f` (the only writer of
the line the counter reads for this item), and that cause is causally false: SKILL.md:241 is not the
r21-source-refs row, it is the r21-source-head row, written before the fixture existed. Reproduced:

```
ITEM	G17a	AGREE	restated	rc=0 expect_exit=0 statement is the run's last digit-bearing line last=SUMMARY total=1 pass=1 fail=0 load=32.08
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=d72724aaa60c2f50dbe3bc35548da41b52b4943c
```
(row `| G17a | SKILL.md:241 | restated | 0 | \`python3 tests/fixtures/r21-source-refs.py ... --keep-only\` | \`SUMMARY total=1 pass=1 fail=0\` | 54eb2d0f... | keep-only arm of the row |`). This is reported as an ATTACK, not delivered as a fix: it leaves the row's red remote-only claim in place and credits an unrelated commit.

### Line-number note

The frozen `where` (SKILL.md:241) is one below the 1-based row: line 241 is `r21-source-head`; `r21-source-refs` is line 242. The off-by-one is what lets the argv-correction path bind the neighbouring row's line.

### Do-nothing contrast

The counter's do-nothing control at `--rev <base>` prints `mismatches>0`; this item alone contributes the mismatch, and it is unchanged at the tip, so it is not a control artifact.
