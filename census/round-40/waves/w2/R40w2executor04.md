# R40w2executor04 — r40 C2 joined-docstring fixture, default and `--one-line`

Verdict: SAFE for the assigned run. The fixture behaves as the C2 claim says. Notes on weak cases are below and are not falsifiers.

## Attacked
- `tests/fixtures/r40-docstring-joined.py:1-126`. The cases are at :64-94 and the summary and exit code at :117-122.
- `census/round-40/docstring-classes.py:34-80`. This is the joined reading (`class_entries`) and `first_line_entries`.
- `tools/souji-worktree-drift.py:44-50`. This is the docstring class map the fixture reads.

## Revision
- Landed commit: 128e412b0ced3c243dc27c3dd3332054a611bc2e. Lane HEAD at run time was 549d9ec.
- `git diff --stat 128e412 HEAD -- tools/souji-worktree-drift.py tests/fixtures/r40-docstring-joined.py census/round-40/docstring-classes.py` printed nothing and exited 0, so those three files are byte-identical to the landed revision.
- I ran the fixture twice: from a `git archive 128e412` extract in scratch, and from the working tree.
- Commands used `TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2executor04 PYTHONDONTWRITEBYTECODE=1`.

## Commands and real output

Run from the landed-revision archive at `/fast/scratch/hyaku/souji-r40/w2/R40w2executor04/landed`.

`python3 -B tests/fixtures/r40-docstring-joined.py`, default mode:
```
case-synthetic-joined-has-trigger=PASS
case-synthetic-primary-has-trigger=PASS
case-synthetic-one-line-misses-trigger=PASS
case-frozen-pairs-present=PASS
case-outside-root-trigger-primary=PASS
case-record-missing-eacces=PASS
case-record-malformed-enoent=PASS
case-class-sets-equal=PASS
case-joined-not-shorter=PASS
SUMMARY cases=9 pass=9 fail=0
exit=0
```

`python3 -B tests/fixtures/r40-docstring-joined.py --one-line`:
```
case-synthetic-joined-has-trigger=PASS
case-synthetic-primary-has-trigger=FAIL primary='the first physical line of this entry'
case-synthetic-one-line-misses-trigger=PASS
case-frozen-pairs-present=FAIL missing=['RECORD-OUTSIDE-ROOT(--root)']
case-outside-root-trigger-primary=FAIL primary='a record row, or the gitdir it resolves to, escapes'
case-record-missing-eacces=PASS
case-record-malformed-enoent=PASS
case-class-sets-equal=PASS
case-joined-not-shorter=PASS
SUMMARY cases=9 pass=6 fail=3
exit=1
```

The same two commands run from the lane working tree gave identical SUMMARY lines and exit codes:
- default: `SUMMARY cases=9 pass=9 fail=0`, exit 0.
- `--one-line`: `SUMMARY cases=9 pass=6 fail=3`, exit 1.

The one-line failures are the expected result. The one-line reading misses the wrapped `--root` trigger of RECORD-OUTSIDE-ROOT and the synthetic wrapped trigger. That matches the C2 predicate: the joined reading detects a wrapped trigger and the one-line reading misses it.

Runtime probe, for the "mapping agrees with runtime" kill clause:
- `python3 -B tools/souji-worktree-drift.py --root $S --record $S/nope.tsv` printed `REFUSAL RECORD-MALFORMED: .../nope.tsv is not a regular file` and exited 2.
- That matches the documented class for a missing (ENOENT) record path.

## Observations (not falsifiers)
1. This fixture reads docstring text only, and never runs the tool. The "mapping disagrees with runtime" kill clause is therefore not exercised by this fixture. I covered one class by hand: ENOENT gives RECORD-MALFORMED, above. The other frozen pairs have no runtime check here. EACCES to RECORD-MISSING and `--root` to RECORD-OUTSIDE-ROOT may be covered by `c2-counter.py`; I did not run it.
2. The "r39 one-line analyser" in this fixture is `first_line_entries` (`docstring-classes.py:78-80`). It is a reimplementation sharing the r40 regex and loop, not the r39 bytes. The control is faithful only if that reimplementation matches r39.
3. `case-synthetic-primary-has-trigger` (:67) duplicates `case-synthetic-joined-has-trigger` in default mode. It adds information only under `--one-line`.
4. `case-joined-not-shorter` (:90-94) cannot fail. `_entries` only appends continuation text, so the joined text is never shorter than the first line.
5. `case-class-sets-equal` (:88) fails only if the joined and first-line class sets diverge. Both come from the same `CLASS_LINE` loop, so this too is near-tautological.
6. `--one-line` exits 1 by design. A harness that treats a non-zero exit as a fixture defect would misread it; the counter or L1 must expect exit 1 there.

## Scratch
- `/fast/scratch/hyaku/souji-r40/w2/R40w2executor04` was removed. `ls -d` after the `rm` reported "No such file or directory".
- No install was made, no committed file was edited, and no git or jj mutation was run. The only git use was read-only `diff --stat` and `archive`.
