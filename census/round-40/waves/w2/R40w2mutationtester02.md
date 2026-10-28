# R40w2mutationtester02 — C2 analyzer mutation probe

**Target:** landed `census/round-40/docstring-classes.py` at commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`; detector `tests/fixtures/r40-docstring-joined.py`. The five isolated source mutations were made only in the seat scratch directory, then scored with the fixture. The landed worktree HEAD was `556c24a5cacf208c5144c459838712594a43e1f2`; analyzer and fixture bytes were read from that checkout. No installs.

## Attack points

- `docstring-classes.py:65-66`: do not join continuation lines.
- `docstring-classes.py:58-62`: treat blank lines as continuation lines.
- `docstring-classes.py:34`: require one whitespace after class token rather than two or more.
- `docstring-classes.py:40`: extract text by slicing source instead of `ast.get_docstring`.
- `docstring-classes.py:34`: remove `(?:-[A-Z0-9]+)+` from the class token regex.

Fixture checks live at `tests/fixtures/r40-docstring-joined.py:64-94`; its nine-case summary is emitted at lines 119-122.

## Commands and actual output

Pristine and mutation probe used:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r40-docstring-joined.py --analyzer /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester02/<variant>.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py
```

Pristine (`<variant>=pristine`), rc 0:

```text
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
```

Mutation variants used the same command. Actual detector output:

```text
=== never-join rc 1 ===
case-synthetic-joined-has-trigger=FAIL joined='the first physical line of this entry'
case-synthetic-primary-has-trigger=FAIL primary='the first physical line of this entry'
case-synthetic-one-line-misses-trigger=PASS
case-frozen-pairs-present=FAIL missing=['RECORD-OUTSIDE-ROOT(--root)']
case-outside-root-trigger-primary=FAIL primary='a record row, or the gitdir it resolves to, escapes'
case-record-missing-eacces=PASS
case-record-malformed-enoent=PASS
case-class-sets-equal=PASS
case-joined-not-shorter=PASS
SUMMARY cases=9 pass=5 fail=4
=== blank-continuation rc 0 ===
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
=== one-space rc 1 ===
case-synthetic-joined-has-trigger=FAIL joined='the first physical line of this entry'
case-synthetic-primary-has-trigger=FAIL primary='the first physical line of this entry'
case-synthetic-one-line-misses-trigger=PASS
case-frozen-pairs-present=PASS
case-outside-root-trigger-primary=PASS
case-record-missing-eacces=PASS
case-record-malformed-enoent=PASS
case-class-sets-equal=PASS
case-joined-not-shorter=PASS
SUMMARY cases=9 pass=7 fail=2
=== source-docstring rc 0 ===
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
=== drop-hyphen-group rc 1 ===
case-synthetic-joined-has-trigger=FAIL joined=None
case-synthetic-primary-has-trigger=FAIL primary=None
case-synthetic-one-line-misses-trigger=PASS
case-frozen-pairs-present=FAIL missing=['RECORD-MALFORMED(ENOENT)', 'RECORD-MISSING(EACCES)', 'RECORD-OUTSIDE-ROOT(--root)']
case-outside-root-trigger-primary=FAIL primary=None
case-record-missing-eacces=FAIL primary=None
case-record-malformed-enoent=FAIL primary=None
case-class-sets-equal=PASS
case-joined-not-shorter=PASS
SUMMARY cases=9 pass=3 fail=6
```

## Verdict

**FALSIFIED — two declared defect mutants survive.** The blank-line mutant survived (rc 0, 9/9) because the fixture contains no blank line inside a class entry: its blank line precedes the entry (line 34) and prose follows a blank after the entry. The source-slicing mutant survived (rc 0, 9/9) because this fixture's source starts with a conventional triple-double-quoted module docstring, so the simplistic slice returns equivalent content for exercised inputs. Neither detector case discriminates these behaviors. The other three mutants were killed (never-join, one-space, drop-hyphen-group).

Scratch directory removed: yes (`rm -rf -- /fast/scratch/hyaku/souji-r40/w2/R40w2mutationtester02` executed by EXIT trap). No committed files were modified.
