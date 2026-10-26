# C1 K05 — SCORECARD.md:158 restatement (value drift)

Item: K05, SCORECARD.md:158 at base 6017a482e7068d5afb7617640198fbb0fe743357; frozen exit `0`;
frozen predicate `\b18/18\b || \bpass=18\b && \bfail=0\b`; files `tools/souji-landing-gate.py`;
frozen argv `python3 tools/souji-landing-gate.py --selftest`.

Kind: **VALUE DRIFT** (the row's own argv still runs and still exits 0; the selftest count moved 18 -> 65,
the first break at 28). Not an argv correction: the row's own command and its form of success are unchanged.

## Row (append under `### Round 33 capability currency`)

ROW-BEGIN
| K05 | SCORECARD.md:158 | restated | 0 | same | `SELFTEST pass=65 fail=0` | ddb73474433977ff54b015ac3e77669ff2537353 | selftest grew from 18 to 28 cases at ddb7347 (round-17 D6 gate exact ids and replays; the fenced-and-table-ignored case was renamed benign-status-words with a stricter status_lines count), and to 65 cases by 2d9bca55, all passing |
ROW-END

The statement is the run's summary line, quoted whitespace-collapsed. The raw line separates fields with tabs
(`SELFTEST\tpass=65\tfail=0\n`, verified with `od -c`); the counter collapses both sides, so this row and a
tab-separated spelling judge identically (the L1 feasibility row at `records/feasibility.txt` uses tabs and agrees).

## Full appended block as proved in scratch

Byte-for-byte the block committed at scratch commit `12cdd87b84e94d2863c6c64dd43dd923535faf56` (header text and
table header follow the wave's existing deliveries, `deliver-c1-K04.md` / `deliver-c1-K18.md`):

```
### Round 33 capability currency

Restatements of capability rows above whose stated outcome no longer reproduces. Original rows are unchanged (append-only); each cause commit is executed by `census/round-33/c1-counter.py`.

| id | row | status | exit | run | statement | cause | reason |
|---|---|---|---|---|---|---|---|
| K05 | SCORECARD.md:158 | restated | 0 | same | `SELFTEST pass=65 fail=0` | ddb73474433977ff54b015ac3e77669ff2537353 | selftest grew from 18 to 28 cases at ddb7347 (round-17 D6 gate exact ids and replays; the fenced-and-table-ignored case was renamed benign-status-words with a stricter status_lines count), and to 65 cases by 2d9bca55, all passing |
```

## Receipts

Scratch: `/fast/scratch/hyaku/souji-r33/RestateK05/`, `export TMPDIR=$D/tmp` (created), a fresh `tmp-run<N>` per run.
Clone: `git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin $D/c && git -C $D/c remote remove origin`;
`git -C $D/c rev-parse --show-toplevel` -> `/fast/scratch/hyaku/souji-r33/RestateK05/c`; detached at
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Tools: `Python 3.14.8`, `git version 2.56.0`; no installs this seat.
`SCORECARD.md` at base and at the list-rev is byte-identical (`cmp` clean, 494 lines), and line 158 is the same
K05 row at both revisions (sha256 of the line `3e567d0351a5aaac…` in both).

### 1. Frozen argv, 3 runs, fresh TMPDIR each (cwd = clone root, GIT_CONFIG_NOSYSTEM=1)

`python3 tools/souji-landing-gate.py --selftest`

run 1 (`TMPDIR=$D/tmp-run1`): `rc=0`, 66 stdout lines, stderr empty. Every digit-bearing line
(whitespace-collapsed; trailing blanks trimmed; `… — …` is the em dash the tool prints):

```
CASE pass dangling-skill-pointer exit=1 ids=['LG-DANGLING-PTR'] paths=['census/round-18/missing.json'] fleet=[] err=None
CASE pass pointer-without-wave-reports exit=2 ids=['LG-DANGLING-PTR'] paths=['census/round-18/missing.json'] fleet=[] err=no .md reports under .ufo/waves/round-18/ or census/round-18/waves/ at f822f82d22c00c7020c979b3376bb383dcdcac94
CASE pass relative-pointer-normalization exit=1 ids=['LG-DANGLING-PTR'] paths=['census/round-18/missing.json'] fleet=[] err=None
CASE pass relative-pointer-escape exit=1 ids=['LG-DANGLING-PTR'] paths=['../census/round-18/missing.json'] fleet=[] err=None
CASE pass extended-pointer-sources exit=1 ids=['LG-DANGLING-PTR'] paths=['census/round-18/shonen-missing.json', 'corpus/spotcheck-missing.md'] fleet=[] err=None
CASE pass brace-pointer-expansion exit=1 ids=['LG-DANGLING-PTR'] paths=['tools/missing.sh'] fleet=[] err=None
CASE pass pointer-line-suffix exit=1 ids=['LG-DANGLING-PTR'] paths=['corpus/missing.md'] fleet=[] err=None
CASE pass pointer-comma-line-suffix exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass pointer-brace-line-suffix exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass pointer-interior-dot-segments exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass pointer-placeholder-skip exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass pointer-round-range exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass pointer-log-round-section exit=1 ids=['LG-DANGLING-PTR'] paths=['census/round-18/log-correction-missing.json'] fleet=[] err=None
CASE pass pointer-exemption exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass quarantine-path-exemption exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass quarantine-path-absent exit=1 ids=['LG-DANGLING-PTR'] paths=['.ufo/quarantine/round-18/absent-stub'] fleet=[] err=None
CASE pass pointer-stale-exemptions exit=1 ids=['LG-DANGLING-PTR-EXEMPT-STALE'] paths=['corpus/not-cited.md', 'tools/good.sh'] fleet=[] err=None
CASE pass pointer-bad-exemption-exit2 exit=2 ids=[] paths=[] fleet=[] err=corpus/pointer-exemptions.tsv:1 malformed exemption row (expected unique path<TAB>reason)
CASE pass cli-unknown-rev-exit2 rc=2
CASE pass cli-bad-exemption-exit2 rc=2
CASE pass pointer-fleet-only exit=0 ids=[] paths=[] fleet=['.ufo/waves/hyaku/fleet-direct.md', '.ufo/waves/hyaku/fleet-only.md'] err=None
CASE pass pointer-fleet-json rc=0
CASE pass pointer-lane-fleet-collision exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass pointer-exemption-prefix exit=1 ids=['LG-DANGLING-PTR'] paths=['corpus/runtime-extra'] fleet=[] err=None
CASE pass pointer-round-17-disabled exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass dangling-measured-commit exit=1 ids=['LG-FROZEN-MEASURED'] paths=['tests/fixtures/r9-frozen/expected.json'] fleet=[] err=None
CASE pass measured-record-placeholder-exemption exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass measured-record-wrong-value exit=1 ids=['LG-DANGLING-PTR-EXEMPT-STALE', 'LG-FROZEN-MEASURED'] paths=['tests/fixtures/r14-cache-frozen/expected.json', 'tests/fixtures/r14-cache-frozen/record.json'] fleet=[] err=None
CASE pass clean-pass exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass clean-measured exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass cli-summary-exact rc=0
CASE pass nonparsing-cited-sh exit=1 ids=['LG-PARSE-REG'] paths=['tools/good.sh'] fleet=[] err=None
CASE pass nonparsing-cited-py exit=1 ids=['LG-PARSE-REG'] paths=['tools/good.py'] fleet=[] err=None
CASE pass missing-cited-path exit=1 ids=['LG-MISSING-REG'] paths=['tools/gone.sh'] fleet=[] err=None
CASE pass changed-nonparsing-with-base exit=1 ids=['LG-PARSE-CHANGED'] paths=['tools/new.sh'] fleet=[] err=None
CASE pass changed-paths-exact exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass uncited-nonparsing-not-flagged exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass pin-mismatch exit=1 ids=['LG-FROZEN-PIN'] paths=['tests/fixtures/r9-frozen/expected.json'] fleet=[] err=None
CASE pass pin-missing-file exit=1 ids=['LG-FROZEN-PIN'] paths=['tests/fixtures/r9-frozen/expected.json'] fleet=[] err=None
CASE pass record-sha256-mismatch exit=1 ids=['LG-FROZEN-PIN'] paths=['tests/fixtures/r9-frozen/expected.json'] fleet=[] err=None
CASE pass frozen-measured exit=1 ids=['LG-FROZEN-MEASURED'] paths=['tests/fixtures/r9-frozen/expected.json'] fleet=[] err=None
CASE pass frozen-measured-absent exit=1 ids=['LG-FROZEN-MEASURED'] paths=['tests/fixtures/r9-frozen/expected.json'] fleet=[] err=None
CASE pass measured-tree-path-exit2 exit=2 ids=[] paths=[] fleet=[] err=git cat-file blob failed (rc=128): fatal: git cat-file 0479003445f4e5a5ff25360c607ca79ffe4e4ea1: bad file
CASE pass files-null-exit2 exit=2 ids=[] paths=[] fleet=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: None
CASE pass files-empty-exit2 exit=2 ids=[] paths=[] fleet=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: {}
CASE pass files-nonobject-exit2 exit=2 ids=[] paths=[] fleet=[] err=tests/fixtures/r9-frozen/expected.json: 'files' is absent, falsy or not an object: 'not-a-dict'
CASE pass expected-nonobject-exit2 exit=2 ids=[] paths=[] fleet=[] err=tests/fixtures/r9-frozen/expected.json: expected.json is not an object: [1, 2, 3]
CASE pass expected-unreadable-exit2 exit=2 ids=[] paths=[] fleet=[] err=tests/fixtures/r9-frozen/expected.json: expected.json unreadable: Expecting property name enclosed in double quotes: line 1 column 3 (char 2)
CASE pass uncarried-marker exit=1 ids=['LG-SEAT-UNCARRIED'] paths=['.ufo/waves/round-16/w1/SeatA.md'] fleet=[] err=None
CASE pass bold-uncarried exit=1 ids=['LG-SEAT-UNCARRIED'] paths=['.ufo/waves/round-16/w1/SeatA.md'] fleet=[] err=None
CASE pass status-in-fence exit=1 ids=['LG-SEAT-UNCARRIED'] paths=['.ufo/waves/round-16/w1/SeatA.md'] fleet=[] err=None
CASE pass status-in-table exit=1 ids=['LG-SEAT-UNCARRIED'] paths=['.ufo/waves/round-16/w1/SeatA.md'] fleet=[] err=None
CASE pass carried-open exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass carried-resolved exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass open-admitted exit=1 ids=['LG-OPEN-ADMITTED'] paths=['.ufo/waves/round-16/w1/SeatA.md'] fleet=[] err=None
CASE pass wrap-unmarked exit=1 ids=['LG-SEAT-UNCARRIED'] paths=['.ufo/waves/round-18/w1/SeatWrap.md'] fleet=[] err=None
CASE pass wrap-marked exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass wrap-complete exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass wrap-bullet-wrapped exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass no-wave-dir-exit2 exit=2 ids=[] paths=[] fleet=[] err=no .md reports under .ufo/waves/round-16/ or census/round-16/waves/ at e458a9f03396e6fc4b96ca42886bb7b7b1db6ba6
CASE pass benign-status-words exit=0 ids=[] paths=[] fleet=[] err=None
CASE pass bad-rev-exit2 exit=2 ids=[] paths=[] fleet=[] err=cannot resolve revision '0000000000000000000000000000000000000000': git rev-parse --verify failed (rc=1):
CASE pass no-skill-exit2 exit=2 ids=[] paths=[] fleet=[] err=no SKILL.md at de63483895e844287f0cadee78374c911d9d4fe4
CASE pass ambient-git-dir exit=0 resolved=e47fc4ee8f8d
CASE pass cli-ambient-git-dir rc=0
SELFTEST pass=65 fail=0
```

run 2 (`TMPDIR=$D/tmp-run2`): `rc=0`. run 3 (`TMPDIR=$D/tmp-run3`): `rc=0`. Both byte-identical to run 1 —
`sha256sum run1.out run2.out run3.out` -> `088846868fb5d85ede739ca1c075da6a5723e05556268a260169b195828abd0c`
three times; `diff -q` clean for 1-vs-2 and 1-vs-3.

Predicate check on each run (whitespace-collapsed stdout+stderr): `\b18/18\b` absent, `\bpass=18\b` absent,
`\bfail=0\b` present -> the frozen predicate fails on all three runs. Exit is still 0, so the only stale part is
the count. `grep -c 'CASE\tFAIL' run1.out` = 0 (every case passes).

The line that carries the row's claim ("the selftest passes N/N") is the summary line `SELFTEST pass=65 fail=0`;
it is chosen as the statement.

### 2. Cause: first commit at which the original outcome stops holding

Every commit in the lane that touches `tools/souji-landing-gate.py`, run in order with the frozen argv and a fresh
TMPDIR (holds = exit 0 and (`18/18` or `pass=18` + `fail=0`)):

| rev | subject | rc | summary line | frozen predicate |
|---|---|---|---|---|
| 7a79dc2d6e28 | round-16: landing gate, its held-out fixture, … | 0 | `SELFTEST pass=18 fail=0` | holds |
| a6ec7810e9b5 | round-16: narrow the gate's failure channel … | 0 | `SELFTEST pass=18 fail=0` | holds |
| **ddb734744339** | **round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, … D6 gate exact ids + replays …** | **0** | **`SELFTEST pass=28 fail=0`** | **fails** |
| 4f4834390ad4 | round-17: wave-2 fixes … | 0 | `SELFTEST pass=33 fail=0` | fails |
| 3f822e85c6a5 | round-18: build … | 0 | `SELFTEST pass=53 fail=0` | fails |
| 2fc5f33d0b00 | round-18: gate comma line-lists … | 0 | `SELFTEST pass=53 fail=0` | fails |
| 4800fd79488e | round-18: falsifier fixes … | 0 | `SELFTEST pass=61 fail=0` | fails |
| 005f3d376e5b | round-19: wrap-aware carry gate … | 0 | `SELFTEST pass=65 fail=0` | fails |
| 68447afef62e | round-30: C2 landing gate reads the committed census capture … | 0 | `SELFTEST pass=65 fail=0` | fails |
| 8024b540b04d | round-31: C2 landing-gate reading precision … | 0 | `SELFTEST pass=65 fail=0` | fails |
| 98e5203d45b4 | round-32: C2 scratch discipline … | 0 | `SELFTEST pass=65 fail=0` | fails |

The first failure is `ddb73474433977ff54b015ac3e77669ff2537353`. Counter's value-drift shape, executed directly:

```
$ git -C $D/c rev-parse ddb73474433977ff54b015ac3e77669ff2537353^1
5fa6017ddcae9f6bd4412df44765f6360cb16294
$ (cd $D/c && git checkout -q --detach 5fa6017ddcae … && TMPDIR=$D/tp python3 tools/souji-landing-gate.py --selftest | tail -1)
SELFTEST	pass=18	fail=0            # rc=0  -> holds at the cause's first parent
$ (cd $D/c && git checkout -q --detach ddb734744339 … && TMPDIR=$D/tc python3 tools/souji-landing-gate.py --selftest | tail -1)
SELFTEST	pass=28	fail=0            # rc=0  -> fails at the cause
$ git -C $D/c show --name-only --format= ddb734744339 | grep landing-gate
tools/souji-landing-gate.py
$ git -C $D/c merge-base --is-ancestor ddb734744339 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 && echo YES
YES
```

Cause diffstat for the item file: `1 file changed, 323 insertions(+), 88 deletions(-)`.
I derived this independently (full history walk above); it coincides with the cause named in
`census/round-33/records/feasibility.txt`, and the walk adds what that receipt omits (the 28 -> 65 continuation and
the one rename).

### 3. Scratch landing + counter (the proof)

Canonical block appended at `2d9bca55` in the scratch clone, committed with a throwaway identity:
scratch landing commit `12cdd87b84e94d2863c6c64dd43dd923535faf56` (SCORECARD.md +8 lines; working tree clean after).

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-33/c1-counter.py \
  --root /fast/scratch/hyaku/souji-r33/RestateK05/c \
  --rev 12cdd87b84e94d2863c6c64dd43dd923535faf56 \
  --list-rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46 \
  --scratch /fast/scratch/hyaku/souji-r33/RestateK05/cnt3 --only K05
ITEM	K05	AGREE	restated	rc=0 expect_exit=0 statement is an output line last=SELFTEST pass=65 fail=0
SUMMARY items=1 agree=1 mismatches=0 restated=1 partial=1 rev=12cdd87b84e94d2863c6c64dd43dd923535faf56
counter rc=0
```

The same row was also proved under the heading `### Round 33 capability currency (C1, appended)` with a
different (also ignored) table header — scratch commit `194a939342d931388d88ad4f1676ba95f7ac5936`, run twice
(fresh `--scratch` each): same `ITEM K05 AGREE` line, `SUMMARY items=1 agree=1 mismatches=0`, rc=0 both times.

### 4. Falsifiers run in scratch (the row is not gameable)

* Do-nothing at the list-rev (no restatement row):
  `--rev 2d9bca55 … --only K05` -> `ITEM K05 MISMATCH original rc=0 expect_exit=0 predicate fails last=SELFTEST pass=65 fail=0`,
  `SUMMARY items=1 agree=0 mismatches=1 restated=0`, rc=1. The row is necessary.
* Non-causal commit (cause = `4f4834390ad4`, a later gate commit where the outcome already failed at its parent):
  `ITEM K05 MISMATCH restated BAD-CAUSE(original at parent=False at cause=False; need True/False)`, rc=1.
  The cause field is load-bearing, and my cause is the first break, not any later one.

## Growth or regression?

**GROWTH.** No capability was lost, so nothing is reported as a regression.

* Parent `5fa6017`: 18 `CASE` lines, every one `pass`, `SELFTEST pass=18 fail=0`, rc 0.
* Cause `ddb7347`: 28 `CASE` lines, every one `pass`, `SELFTEST pass=28 fail=0`, rc 0. Name-set arithmetic against
  the parent: 11 names added and 1 name removed — `fenced-and-table-ignored` (18 - 1 + 11 = 28). The removed name is a
  **rename**, not a lost case: at the cause the identical fixture literals
  (`"# SeatA\n\nSTATUS: none\n\n```\nsyntax error inside a fenced block\n```\n"`,
  `"| note | snapshot_tampered quoted in a table |\n"`, `"STATUS — done\n"`) are driven by
  `check("benign-status-words", repo, 0, rev=rev, expect_counts={"status_lines": 2})` — same exit-0 expectation, plus a
  stricter `status_lines` count. The 11 additions are the D6 gate-precision cases (`ambient-git-dir`,
  `benign-status-words`, `bold-uncarried`, `clean-measured`, `files-*-exit2`, `frozen-measured-absent`,
  `measured-tree-path-exit2`, `status-in-fence`, `status-in-table`).
* At `2d9bca55`: 65 `CASE` lines, 0 `CASE FAIL`, `SELFTEST pass=65 fail=0`, rc 0. 17 of the 18 parent-era names are
  present; the 18th is the rename above; 48 names are new. The 28 -> 65 growth happens at `4f4834` (33),
  `3f822e85` (53), `4800fd79` (61), `005f3d37` (65), with no count decrease at any commit in the table.

## Notes for the L1 (integration)

1. The statement binds to the count at the landing revision. It is `pass=65 fail=0` at `2d9bca55` (three identical
   runs). If anything edits `tools/souji-landing-gate.py` before the C1 landing commit, re-derive the summary line at
   that revision — the cause stays `ddb73474`.
2. The counter accepts the row only under a heading whose line starts with `### Round 33 capability currency`
   (`load_restatements` uses `startswith`), i.e. the canonical heading or a suffixed variant of it.
3. The original row's prose "18/18" was never this tool's output shape: from its first commit `7a79dc2` the tool
   prints `SELFTEST pass=N fail=0`. The frozen predicate accepted either spelling, so only the count is stale; the
   restatement quotes the real line.
4. K06 (same line 158, `python3 tests/fixtures/r16-landing-gate.py` 15/15) is a separate item and is not touched here.

## Scratch cleanup

`/fast/scratch/hyaku/souji-r33/RestateK05` (203 MB) removed after these receipts were copied; the counter's own
`--scratch` work trees are self-removed.
