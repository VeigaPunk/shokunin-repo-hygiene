# R43mutationtester01 — C1 instrument sensitivity

## Verdict

19 independent single-expression mutants: **10 KILLED, 9 SURVIVORS, 0 inconclusive**. The frozen discrimination fixture does not detect nine changed C1 behaviors. This attacks fixture sensitivity, not the validity of the frozen contract; no instrument fixes or candidate integrations were made.

Axes: discrimination sensitivity; mutation isolation; exact-byte restoration. Four bounded fixture executions ran concurrently, each in its own disposable work directory. Instruments were extracted from `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`; every r43 fixture clone was pinned to `13de0e84b45efd1113f077d58fc1e89bc586a013`. The frozen fixture's existing r42 revision selection was unchanged.

Evidence directory (all links relative to lane): `.ufo/waves/round-43/w1/R43mutationtester01/`.

## Commands and receipts

Executed from the evidence directory:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43mutationtester01/run_probe.py
```

Observed exit 0; runtime 359.81 seconds. The driver is preserved verbatim in the evidence directory. It ran these three read-only extractions (each PATH is one literal argument listed below):

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:PATH
PATH=census/round-43/c1-counter.py
PATH=tests/fixtures/r43-correction-prose.py
PATH=census/round-42/c1-counter.py
```

Each detector command was the following exact argv pattern; substitutions below exhaust all 21 invocations:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43mutationtester01/frozen-fixture.py --work /fast/scratch/hyaku/souji-r43/R43mutationtester01/LABEL-work --lane-root /home/vgpnk/Projects/shokunin/souji-shokunin --rev43 13de0e84b45efd1113f077d58fc1e89bc586a013 --counter42 /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43mutationtester01/frozen-counter42.py --counter43 COUNTER
```

- LABEL=`baseline`, `restored`: COUNTER=`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43mutationtester01/pristine-counter.py`.
- LABEL=`M01`, `M02`, `M03`, `M04`, `M05`, `M06`, `M07`, `M08`, `M09`, `M10`, `M11`, `M12`, `M13`, `M14`, `M15`, `M16`, `M17`, `M18`, `M19`: COUNTER=`/fast/scratch/hyaku/souji-r43/R43mutationtester01/LABEL-active.py`.
- Every invocation used cwd `/fast/scratch/hyaku/souji-r43/R43mutationtester01` and explicit TMPDIR equal to that directory. Fixture clones assert their own git toplevel before commits and use fixture-local author/committer environment variables.

Unabridged evaluated command arrays, actual exits, summaries, failed-case names, and per-mutant hashes are in `.ufo/waves/round-43/w1/R43mutationtester01/results.json`. Actual stdout/stderr are preserved as `baseline.stdout.txt`, `baseline.stderr.txt`, `M01.stdout.txt` through `M19.stdout.txt` (and corresponding stderr), and `restored.stdout.txt` / `restored.stderr.txt`, all in that same evidence directory. Original bytes are `pristine-counter.py`; archived mutated bytes are `M01-counter.py` through `M19-counter.py`. Scratch paths above document commands only: the durable evidence is entirely inside the seat directory.

Pristine and restored detector output, both exit 0:

```text
SUMMARY43 cases=10 pass=10 fail=0
SUMMARY42 cases=10 pass=10 fail=0
```

Every mutant's r42 column also printed `SUMMARY42 cases=10 pass=10 fail=0`. SURVIVOR means SUMMARY43 remains 10/10; KILLED means at least one r43 fixture expectation fails, with an initially green baseline. All killed runs exited 1; all surviving runs exited 0.

## Kill table

All changes are to `census/round-43/c1-counter.py`, applied independently to frozen bytes, never accumulated. The column shows exact observed SUMMARY43 fields.

| Mutant | Change | SUMMARY43 | Verdict |
|---|---|---|---|
| M01 | Tag enum `(R39\|DE\|SC\|SRC)` becomes `([A-Z]+)`; rejects R39 and permits arbitrary alphabetic tags | cases=10 pass=2 fail=8 | KILLED |
| M02 | Permit repeated spaces before `field=` | cases=10 pass=10 fail=0 | SURVIVOR |
| M03 | Remove tilde alternative from fence regex | cases=10 pass=9 fail=1 | KILLED |
| M04 | Fence toggle becomes unconditional true | cases=10 pass=8 fail=2 | KILLED |
| M05 | Omit URL fragment stripping in W04 mirror | cases=10 pass=7 fail=3 | KILLED |
| M06 | Drop W04 `(url, scope)` novelty guard | cases=10 pass=10 fail=0 | SURVIVOR |
| M07 | Rows rederivation ignores stale-token presence in receipt | cases=10 pass=10 fail=0 | SURVIVOR |
| M08 | W04 rederivation ignores stale-token presence in receipt | cases=10 pass=10 fail=0 | SURVIVOR |
| M09 | Header rederivation ignores derived-revision presence in receipt | cases=10 pass=10 fail=0 | SURVIVOR |
| M10 | Header rederivation ignores unrelated changed paths | cases=10 pass=10 fail=0 | SURVIVOR |
| M11 | Unknown rederive kind returns success | cases=10 pass=10 fail=0 | SURVIVOR |
| M12 | New-mismatch boundary becomes `> base_lines + 1` | cases=10 pass=9 fail=1 | KILLED |
| M13 | Valid RETRACT increments by zero | cases=10 pass=9 fail=1 | KILLED |
| M14 | RETRACT validation omits required-id membership | cases=10 pass=10 fail=0 | SURVIVOR |
| M15 | Dispatch RETRACT only on full regex match, silently skipping malformed lines | cases=10 pass=10 fail=0 | SURVIVOR |
| M16 | Duplicate correction increments by zero | cases=10 pass=9 fail=1 | KILLED |
| M17 | Misspell census-rows dispatch kind | cases=10 pass=7 fail=3 | KILLED |
| M18 | Misspell census-w04 dispatch kind | cases=10 pass=7 fail=3 | KILLED |
| M19 | Misspell receipt-header-rev dispatch kind | cases=10 pass=7 fail=3 | KILLED |

M01's machine-readable short description says “Accept arbitrary uppercase correction tags”; the actual replacement also rejects the digit-containing R39 tag. This table states the complete effect; its kill does not establish unknown-tag coverage.

## Survivors and missing cases

These are proposed additional cases, not executed tests or changes to frozen instruments. Each finding attacks `tests/fixtures/r43-correction-prose.py` sensitivity to the named counter defect.

| Survivor | Missing-case name | Needed discriminatory input / expectation |
|---|---|---|
| M02 | `double-space-correction` | Otherwise correct correction with two spaces before `field=`; expect junk=1 and missing=1, not registration. |
| M06 | `w04-same-scope-repeat` | Synthetic committed SOURCES rows repeating one normalized URL in the same scope; expect no extra W04 warning. Pair with a distinct-scope repeat to preserve the positive case. |
| M07 | `rows-stale-token-absent` | Matching row/correction points to a committed receipt without the declared `rows=<stale>` token while the source count matches derived; expect rederive_failed=1. |
| M08 | `w04-stale-token-absent` | Matching row/correction points to a committed receipt without `W04=<stale>` while the mirrored count matches derived; expect rederive_failed=1. |
| M09 | `header-derived-revision-absent` | Valid derived commit and otherwise allowed diff, but receipt lacks its derived SHA; expect rederive_failed=1. |
| M10 | `header-revision-unrelated-path` | Receipt includes valid derived SHA but the revision interval also changes another census/tools/tests path; expect rederive_failed=1. |
| M11 | `unknown-rederive-kind` | Replace one required row's kind with an unknown kind while preserving a matching correction and existing receipt blob; expect rederive_failed=1. |
| M14 | `unknown-id-retraction` | Append `RETRACT-CORRECTION id=R43-NOT-REQUIRED`; assert junk=1 and retracted=0. Both implementations remain red: this is a field-classification coverage gap, not a demonstrated false-green. |
| M15 | `malformed-retraction` | Append malformed `RETRACT-CORRECTION id=`; expect junk=1 and exit 1 instead of silently passing. |

Synthetic rederivation cases must commit their supporting receipt/SOURCES revisions and update matching required rows/corrections coherently, preserving exactly three required corrections, to isolate the changed predicate. These case designs are inferences from the counter branches; survival itself is measured.

## Restoration and boundaries

Original SHA-256, lane before/after SHA-256, and every scratch probe's restored SHA-256 are identical:

```text
fe2a8d4afe414ab96a21f08b717f578c36d680d3848921caf59531d9706d4e4d
```

Every mutant has a different SHA-256 recorded in `results.json` and its individual `Mxx.json` receipt. Each active scratch copy was restored in `finally` immediately after the mutant detector; the common restored pristine bytes were then run through the same full fixture once, returning 10/10 in both columns. Archived mutant files remain intentionally mutated as requested. No lane source bytes were modified.

The driver's outer `finally` removed the complete owned scratch tree. Cleanup command executed afterward:

```sh
test ! -e /fast/scratch/hyaku/souji-r43/R43mutationtester01
```

Observed exit 0, no output. No tools installed or upgraded. No commits outside disposable fixture clones, no lane git/jj mutation, and no subagents.

Self-check: accuracy 4/5 (M01 short-label ambiguity explicitly corrected above); completeness 5/5 (19 probes, both controls, all nine survivor cases, hashes, cleanup); clarity 4/5 (full command arrays live in linked JSON rather than repeated here); actionability 4/5 (missing cases specified but intentionally unimplemented under frozen-instrument rules); conciseness 4/5 (required kill/evidence tables retained). Mean 4.2/5. Highest-value L1 action is adding negative rederivation and malformed/unknown RETRACT cases in a subsequent instrument revision, not changing this round's frozen scoring.
