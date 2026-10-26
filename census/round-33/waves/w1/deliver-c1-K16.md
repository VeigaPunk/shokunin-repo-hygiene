# C1 K16 — SCORECARD.md:173 restatement (value drift, growth)

Item K16, base `6017a482e7068d5afb7617640198fbb0fe743357`; frozen exit `0`; frozen predicate
`\b9/9\b && control=FALSE-GREEN-REJECTED`; frozen files `tests/fixtures/r23-record-agreement.py,tools/souji-record-agreement.py`;
frozen argv `python3 tests/fixtures/r23-record-agreement.py`.

Kind: **VALUE DRIFT**. At 2d9bca55 the row's own command exits 0 and prints `selftest=15/15`, so `\b9/9\b` no longer
occurs anywhere in stdout+stderr and the frozen predicate fails: the count the row states is stale, the command is not.
The argv is unchanged and correct (`same`). The count stopped being true at `1dd8b1e3…` (9 → 11 cases); later growth
(`c872eec3…` 11 → 12, `728b2ce7…` 12 → 15) took the base run to 15.

## Row (append under `### Round 33 capability currency`)

ROW-BEGIN
| K16 | SCORECARD.md:173 | restated | 0 | same | `selftest=15/15` | 1dd8b1e30a971e662480b49bedf1000667fbddea | selftest grew from 9 to 11 cases at 1dd8b1e (K3 class-missing and K2 tally-stale-log fixtures added; r25 growth took the base run to 15), all 15 pass and the control line still reads FALSE-GREEN-REJECTED |
ROW-END

Row bytes as proved (line + newline, 317 bytes): `sha256 2ef9bd2732a9e4d44102093295109475a511b82e8005269c10a8e6d1cebbeaff`; the line above was
diffed against `git show 78d8c912…:SCORECARD.md | grep '^| K16 |'` in the scratch clone and is byte-identical (md5
`856eff999e37a2ef83f4e48dca5524bc` on both sides).

Full appended block as proved in scratch (header + table header + row):

```
### Round 33 capability currency (C1, appended)

| item | row | kind | exit | run | statement | cause | reason |
|---|---|---|---|---|---|---|---|
| K16 | SCORECARD.md:173 | restated | 0 | same | `selftest=15/15` | 1dd8b1e30a971e662480b49bedf1000667fbddea | selftest grew from 9 to 11 cases at 1dd8b1e (K3 class-missing and K2 tally-stale-log fixtures added; r25 growth took the base run to 15), all 15 pass and the control line still reads FALSE-GREEN-REJECTED |
```

SIBLING-MERGE: one `### Round 33 capability currency` header and one table header serve every K-row of the round; if the
section is already open, append only the row line. Column names are free (the counter matches only `| Kxx |` rows); the
seven cells after `Kxx` must stay in the order row-kind-exit-run-statement-cause-reason, split by ` | `, and no cell may
contain a pipe character.

Placement constraint for the L1: the counter requires SCORECARD.md at `--rev` to start with its `--list-rev` bytes, so the
section must sit at EOF (an insertion before the end breaks the prefix check). The heading
`### Round 33 capability currency (C1, appended)` starts with the counter's `SECTION` constant, so the suffix is accepted.

Statement choice: the row's other fact, `control=FALSE-GREEN-REJECTED`, is on its own stdout line and carries no digit, so
it cannot be the quoted statement (the counter requires a digit-bearing line); the summary line `selftest=15/15` is the
complete digit-bearing line that carries the row's count claim, and the control fact is carried in the reason cell and in
the receipts below.

## Receipts

Scratch: `/fast/scratch/hyaku/souji-r33/RestateK16/` (`TMPDIR=/fast/scratch/hyaku/souji-r33/RestateK16/tmp`, fresh subdir
per run); removed after this delivery was written. Clone:
`git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /fast/scratch/hyaku/souji-r33/RestateK16/c`, origin
removed at once, `git -C <clone> rev-parse --show-toplevel` -> `/fast/scratch/hyaku/souji-r33/RestateK16/c`, detached at
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46`.

### 1. Frozen argv, three runs at 2d9bca55, fresh TMPDIR each (cwd = clone root, `GIT_CONFIG_NOSYSTEM=1`)

`python3 -B tests/fixtures/r23-record-agreement.py` — rc 0, 0, 0; stderr 0 bytes; the three stdouts are byte-identical
except the `scratch=` line (t1/t2/t3). All digit-bearing stdout lines (run 1, 20 lines total):

```
tool=/fast/scratch/hyaku/souji-r33/RestateK16/c/tools/souji-record-agreement.py
tool_sha256=ec5b809d5e21134b38340d7e200463cdcc5ae5eb3cffcfc90ba088ace788d32c
scratch=/fast/scratch/hyaku/souji-r33/RestateK16/t1/souji-r23-ExecFixtureAgreement
case=1 expect=rc=0 mismatches=0 keys=4 json-bound got=rc=0 mismatches=0 keys=4
case=2 expect=rc!=0 K1 receipt-absent>=1 got=rc=1 mismatches=1 keys=4 [K1/receipt-absent]
case=3 expect=rc!=0 K1 value-disagree>=1 rev-disagree=0 got=rc=1 mismatches=1 keys=4 [K1/value-disagree]
case=4 expect=rc!=0 K1 rev-disagree>=1 got=rc=1 mismatches=2 keys=4 [K1/occurrence-absent,K1/rev-disagree]
case=5 expect=rc!=0 K1 unbound-tuple>=1 got=rc=1 mismatches=2 keys=4 [K1/occurrence-absent,K1/unbound-tuple]
case=6 expect=rc!=0 K2 uncorrected*>=1 got=rc=1 mismatches=3 keys=4 [K2/uncorrected]
case=7 expect=rc!=0 K2 filed*>=1 got=rc=1 mismatches=4 keys=4 [K2/filed-occurrence-missing]
case=8 expect=rc!=0 K3 tally-disagree>=1 got=rc=1 mismatches=1 keys=4 [K3/tally-disagree]
case=9 expect=rc!=0 K4 uncommitted-path naming the stray round path got=rc=1 mismatches=1 keys=4 [K4/uncommitted-path]
case=10 expect=K4 rows=0 (exempted operator path is not a mismatch) got=rc=0 mismatches=0 keys=4
case=11 expect=rc!=0 K3 class-absent>=1 got=rc=1 mismatches=1 keys=4 [K3/class-absent]
case=12 expect=rc!=0 K2 uncorrected>=1 (tally arm) got=rc=1 mismatches=2 keys=4 [K2/uncorrected]
case=13 expect=rc!=0 K1 value-disagree>=1 against the stdout tuple (mismatches=7) got=rc=1 mismatches=1 keys=4 [K1/value-disagree]
case=14 expect=rc=0 mismatches=0 keys=4 json-bound got=rc=0 mismatches=0 keys=4
case=15 expect=rc!=0 K1 receipt-rev-object>=1 got=rc=1 mismatches=1 keys=4 [K1/receipt-rev-object]
selftest=15/15
control=FALSE-GREEN-REJECTED
```

`9/9` does not occur anywhere in the base or the cause run (`grep -n '9/9'` -> no match in either); it occurs only in
runs before the cause — at the cause's parent the only match is `selftest=9/9`. `selftest={passed}/{total}` is printed by
the fixture itself
(`tests/fixtures/r23-record-agreement.py:607-608` at 2d9bca55: `print(f"selftest={passed}/{total}")` then
`print("control=" + ("FALSE-GREEN-REJECTED" if control_observed else "NOT-REJECTED"))`), so `15/15` = 15 cases passed of
15 cases, and the always-zero control is still rejected.

### 2. Cause search (`git -C <clone> log --reverse --format=%H -- tests/fixtures/r23-record-agreement.py tools/souji-record-agreement.py`, argv run at each commit, fresh TMPDIR per run)

| commit | subject | rc | summary line | control line | frozen predicate |
|---|---|---|---|---|---|
| 476525026cdb179f2d49441e1cb6c6f7316f3124 | round-23: record-agreement and blob-bound-receipt instruments, … | 0 | `selftest=9/9` | FALSE-GREEN-REJECTED | HOLDS |
| **1dd8b1e30a971e662480b49bedf1000667fbddea** | round-23: wave-2 falsification fixes, final instruments and records | 0 | `selftest=11/11` | FALSE-GREEN-REJECTED | **FAILS (no 9/9)** |
| 53780181aa0f9969eb16b96086c6638acedde1e7 | round-23: r22 section ends at the correction header (K2) | 0 | `selftest=11/11` | FALSE-GREEN-REJECTED | fails |
| c872eec3e1da167ee3ec8a23df88f63cc3657d0d | round-23: wave-2 falsification closure … | 0 | `selftest=12/12` | FALSE-GREEN-REJECTED | fails |
| 315422ba9970f03c27f8a9184446783b7fcdf0a7 | round-24: final — post-wave-2 repairs … | 0 | `selftest=12/12` | FALSE-GREEN-REJECTED | fails |
| 728b2ce71acbe574ae3036b456724d0a3d6f8f08 | round-25: integrate claims, sources, lessons and wave evidence | 0 | `selftest=15/15` | FALSE-GREEN-REJECTED | fails |
| 98e5203d45b4e419a9e72801733d93303acc7ebd | round-32: C2 scratch discipline — 26 tools and fixtures take scratch from TMPDIR | 0 | `selftest=15/15` | FALSE-GREEN-REJECTED | fails |

First-parent check (the counter's value-drift rule uses the cause's first parent, not the previous commit that touched the
file):

```
git rev-list --parents -n1 1dd8b1e30a971e662480b49bedf1000667fbddea
 -> 1dd8b1e30a971e662480b49bedf1000667fbddea 102690017115cb202f292828c90b72705f69bf09
run at 102690017115cb202f292828c90b72705f69bf09 -> rc=0, selftest=9/9, control=FALSE-GREEN-REJECTED  => HOLDS
run at 1dd8b1e30a971e662480b49bedf1000667fbddea -> rc=0, selftest=11/11, control=FALSE-GREEN-REJECTED, no `9/9` => FAILS
git show --name-only --format= 1dd8b1e3… names tests/fixtures/r23-record-agreement.py and tools/souji-record-agreement.py
git merge-base --is-ancestor 1dd8b1e30a971e662480b49bedf1000667fbddea 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 -> YES
```

Cause diff (9 → 11 cases): `tests/fixtures/r23-record-agreement.py` gains two CASES entries plus their predicates —
`("class-missing", case_k3_class, True)` (K3 class-absent) and `("tally-stale-log", case_k2_tally, True)` (K2 tally arm,
labeled `K2 uncorrected>=1 (tally arm)` in the output) — and, in the same commit, the K4 exemption file moves from
`corpus/pointer-exemptions.tsv` to `census/round-23/records/uncommitted-exemptions.tsv`, which is a fixture-internal
rename, not a case-count change.

### 3. Counter proof (append + commit in scratch, then counter)

Scratch commit holding base bytes + the section: `78d8c9121f250adbb61e3315cbb2f2eb33f415c0`
(parent `2d9bca55a9f042a2c9ed60a797a8069e74c41f46`).

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
  --root /fast/scratch/hyaku/souji-r33/RestateK16/c --rev 78d8c9121f250adbb61e3315cbb2f2eb33f415c0 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --scratch /fast/scratch/hyaku/souji-r33/RestateK16/cnt2 --only K16
ITEM	K16	AGREE	restated	rc=0 expect_exit=0 statement is an output line last=selftest=15/15
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=78d8c9121f250adbb61e3315cbb2f2eb33f415c0
rc=0
```

Do-nothing control (same counter, no appended row):

```
--rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46
ITEM	K16	MISMATCH	original	rc=0 expect_exit=0 predicate fails last=selftest=15/15
SUMMARY items=1 agree=0 mismatches=1 restated=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
rc=1
```

Surgical check (all 24 items, same counter): at scratch commit `56045a572eeeee972c93bca523f1ea7a8936285d`
(`--scratch …/cntall`) `SUMMARY items=24 agree=20 mismatches=4 restated=1`, mismatches exactly K04 K05 K17 K18 — K16
flipped to AGREE and no other item's verdict moved. A repeat full run at `78d8c9121f250adbb61e3315cbb2f2eb33f415c0`
(`--scratch …/cntfinal`) read `SUMMARY items=24 agree=19 mismatches=5 restated=1`, the fifth being K22
(`bound_run=19 … mismatches=2` instead of the item's stated `bound_run=20 … mismatches=1`) — a K22 reading that moved
between two trees differing only in this row's reason wording, i.e. a K22 stability question outside K16's claim; reported
to the L1 separately, with the item's frozen row untouched.

### 4. Growth, not regression

GROWTH. Every run from 9/9 to 15/15 exits 0, prints `passed/total` with passed = total, and prints
`control=FALSE-GREEN-REJECTED`; the two fixture files are present and exercised at every revision; the counter's own run at
the scratch commit reproduces 15/15. No case was dropped and no capability was lost: `selftest=` grew 9 → 11 → 12 → 15 at
`1dd8b1e3`, `c872eec3`, `728b2ce7`, and each intermediate reading is all-pass.

## Notes for the L1

1. Row prose in SCORECARD.md:173 also says "reject an always-zero emitter on eight of nine fixture cases". That prose is
   stale too — at base the fixture runs 15 cases: 1 target (`case=1`, green-on-clean), 2 further green-on-clean cases
   (`case=10 exempted-dirty`, `case=14 stdout-two-line`) and 12 cases that require >=1 mismatch. Excerpt, byte-quoted from
   `tests/fixtures/r23-record-agreement.py:527` at 2d9bca55: `# case 1 is the target (green-on-clean); every other case
   requires >=1 mismatch`. The item's frozen statement is only the count (`9/9` + control), and a restatement may quote
   only one output line, so this prose staleness is not restatable by a K16 row; logged as a finding, not restated away.
2. The frozen predicate `\b9/9\b` is a substring test over the whole collapsed output, so `selftest=19/9` would also match;
   no current run produces such a line ([INFERENCE], not reproduced), and this is reported, not amended.
