# R40w2scout03 — `parse_record` fixture coverage sweep

**Verdict: FALSIFIED (coverage gap remains).** The r40 fixture covers the three round-targeted topics, but does not assert multiple file-open refusal branches or the nonblocking FIFO guarantee. It also leaves several older parser branches covered only by pre-r40 fixtures, not r40 itself. Scope is `tools/souji-worktree-drift.py::parse_record` at landed commit `128e412b0ced3c243dc27c3dd3332054a611bc2e`; that blob is unchanged at HEAD.

## Branch inventory and fixture assertions

“Asserted” means a fixture outcome would fail if the specific behavior were changed (tested by the named mutant where available), not merely that the fixture happens to execute `parse_record`.

| Branch / source lines | Behavior | Committed fixture assertion(s) | Coverage status |
|---|---|---|---|
| `try os.open` / `except OSError` / `exc.errno == ENOENT` / `else` (`124`, `131–136`) | Missing record is classified `RECORD-MALFORMED`; other open errors classify `RECORD-MISSING` | r38 `missing-record` (`tests/fixtures/r38-drift-record.py:119`): ENOENT. r38 write-envelope static docstring case checks class wording, not actual EACCES/ELOOP behavior. | ENOENT asserted; non-ENOENT `RECORD-MISSING` behavior **unasserted**. |
| `fstat` non-regular refusal (`137–140`) | Directory/FIFO/device record rejected as `RECORD-MALFORMED` | None of r36–r40 passes a non-regular object as `--record`. | **Unasserted.** |
| read loop: EOF break, chunk append; decode (`141–149`) | Reads chunks until EOF, joins bytes, decodes UTF-8 using `replace`, always closes fd | r40 `invalid-utf8-in-repo-name` and `invalid-utf8-in-comment` (`r40-drift-record-branches.py:114–120`) assert replacement-decoding behavior. Ordinary fixture records exercise the successful read/EOF path. No fixture forces a multi-chunk record or read error. | Invalid UTF-8 asserted; chunk boundary/read-error/close behavior **unasserted**. |
| `if not line.strip() or line.startswith('#')` / `continue` (`152–154`) | Blank and column-0 comment lines skipped; indented comment is not skipped | r38 `comments-and-blanks` (`r38-drift-record.py:120–122`); r39 `indented-comment` (`r39-drift-record-rules.py:108–109`); r40 invalid-byte comment is skipped (`r40-drift-record-branches.py:117–120`). | Asserted across fixtures. |
| ROW match / duplicate-name check / append / continue (`155–161`) | Valid REPO row is parsed; duplicate name refused | r38 `duplicate-name` (`r38-drift-record.py:111–113`); all fixtures’ successful records assert ordinary row parsing. | Asserted across fixtures. |
| TOTAL match / assign / continue (`162–165`) | TOTAL accepted in any position; last TOTAL wins (then validated) | r39 `total-before-rows` (`r39-drift-record-rules.py:92–93`); r40 `total-duplicate-identical` and `total-conflicting-second` (`r40-drift-record-branches.py:102–106`). | Asserted. |
| neither ROW nor TOTAL (`166`) | Schema-invalid line refused | r36 `malformed` (`r36-worktree-drift.py:174–179`); r38 `bad-line` (`r38-drift-record.py:116–118`); r39 trailing-space and indented-comment (`r39-drift-record-rules.py:89–91,108–109`). | Asserted. |
| no rows (`167–168`) | `RECORD-EMPTY`, even if comments/TOTAL exist | r36 `empty` (`r36-worktree-drift.py:187–192`); r38 `empty-record` (`r38-drift-record.py:118`); r39 `comments-total-only` (`r39-drift-record-rules.py:110–111`). | Asserted. |
| TOTAL repos/regs/prunable comparisons (`169–178`) | Each aggregate must agree with rows | r36 total mismatch hits repos; r38 `total-repos-mismatch`, `total-regs-mismatch`, `total-prunable-mismatch` (`r38-drift-record.py:102–110`); r40 repos disagreement (`r40-drift-record-branches.py:107–109`). | Asserted. |

The main residual gap is **actual open/read refusal behavior**: non-ENOENT `OSError` (`RECORD-MISSING`), non-regular path refusal (`RECORD-MALFORMED`), and specifically the FIFO nonblocking guarantee. The older r39 branch inventory also listed splitlines terminators beyond LF/CRLF; the fixtures never pin that broader terminator set (r39 only asserts CRLF). Multi-chunk reads are likewise not asserted. These are concrete coverage gaps even though they are not all part of the r40 frozen C3 predicate.

## Reproduction evidence (commands and actual output)

Commit identity and source stability:

```text
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
549d9ec53a1f5932337ff14438fcd22b0621828d
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -1 --format='%H %s' 128e412b0ced3c243dc27c3dd3332054a611bc2e
128e412b0ced3c243dc27c3dd3332054a611bc2e round-40: instruments, sources, knowledge — C1 evidence-bound counter, C2 joined docstring classes, C3 record-branch battery
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor 128e412b0ced3c243dc27c3dd3332054a611bc2e HEAD && echo ANCESTOR_OK
ANCESTOR_OK
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD:tools/souji-worktree-drift.py 128e412b0ced3c243dc27c3dd3332054a611bc2e:tools/souji-worktree-drift.py
5a2b32941bc5c3da628ee92f75be1c33192ca311
5a2b32941bc5c3da628ee92f75be1c33192ca311
```

All fixture commands below used `S=/fast/scratch/hyaku/souji-r40/w2/R40w2scout03`, `mkdir -p "$S"`, `export TMPDIR="$S"`, and `--work "$S"`; each command used the committed worktree fixture and tool files, which are identical to the landed instrument revision for the parser.

```text
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r36-worktree-drift.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work "$S"
control=STUB-REJECTED
case-match=PASS 
case-regs-changed=PASS 
case-prunable-changed=PASS 
case-absent=PASS 
case-malformed=PASS 
case-total-mismatch=PASS 
case-empty=PASS 
case-unrecorded=PASS 
case-read-only=PASS 
case-json-inside-tree=PASS 
case-trace-env=PASS 
case-live-repos-non-negative=PASS 
SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED

$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r37-drift-discrimination.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work "$S"
case-match-exact=PASS
case-regs-understated=PASS
case-prunable-live=PASS
case-absent-vs-unreachable=PASS
case-unrecorded-exact=PASS
case-unrecorded-unreachable=PASS
SUMMARY cases=6 pass=6 fail=0

$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r38-drift-record.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work "$S"
case-total-ok=PASS
case-total-repos-mismatch=PASS
case-total-regs-mismatch=PASS
case-total-prunable-mismatch=PASS
case-duplicate-name=PASS
case-no-total-row=PASS
case-bad-line=PASS
case-empty-record=PASS
case-missing-record=PASS
case-comments-and-blanks=PASS
SUMMARY cases=10 pass=10 fail=0

$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r39-drift-record-rules.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work "$S"
case-good=PASS
case-trailing-space=PASS
case-total-before-rows=PASS
case-crlf=PASS
case-outside-root=PASS
case-indented-comment=PASS
case-comments-total-only=PASS
SUMMARY cases=7 pass=7 fail=0

$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r40-drift-record-branches.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py --work "$S"
case-good=PASS
case-total-duplicate-identical=PASS
case-total-conflicting-second=PASS
case-total-repos-disagrees=PASS
case-skip-unrecorded-suppresses=PASS
case-unrecorded-without-flag=PASS
case-invalid-utf8-in-repo-name=PASS
case-invalid-utf8-in-comment=PASS
SUMMARY cases=8 pass=8 fail=0
```

The r40 C3 battery at the landed revision (`--rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch "$S"`) produced:

```text
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-conflicting-second base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=good,total-duplicate-identical,skip-unrecorded-suppresses,invalid-utf8-in-comment base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=invalid-utf8-in-repo-name base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=total-repos-disagrees base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
```

I independently probed several branches using an import of the committed parser and scratch record files. Actual output:

```text
duplicate-identical-total PARSED ([{'name': 'a', 'regs': 0, 'prunable': 0}], {'repos': 1, 'regs': 0, 'prunable': 0})
duplicate-conflicting-total Refusal RECORD-MALFORMED: TOTAL repos=2 but 1 REPO rows
cr-alone PARSED ([{'name': 'a', 'regs': 0, 'prunable': 0}, {'name': 'b', 'regs': 0, 'prunable': 0}], None)
vt PARSED ([{'name': 'a', 'regs': 0, 'prunable': 0}, {'name': 'b', 'regs': 0, 'prunable': 0}], None)
ff PARSED ([{'name': 'a', 'regs': 0, 'prunable': 0}, {'name': 'b', 'regs': 0, 'prunable': 0}], None)
nel PARSED ([{'name': 'a', 'regs': 0, 'prunable': 0}, {'name': 'b', 'regs': 0, 'prunable': 0}], None)
unicode-ls PARSED ([{'name': 'a', 'regs': 0, 'prunable': 0}, {'name': 'b', 'regs': 0, 'prunable': 0}], None)
directory Refusal RECORD-MALFORMED: /fast/scratch/hyaku/souji-r40/w2/R40w2scout03/directory is not a regular file
fifo Refusal RECORD-MALFORMED: /fast/scratch/hyaku/souji-r40/w2/R40w2scout03/fifo is not a regular file
```

A targeted mutation matrix showed which fixtures assert selected branches; `N4-strict-decode` was run separately with a unique exact decode anchor. Results:

```text
MUTANT N2-fstat anchor_count 1
r36 rc 0 fails 0 cases -
r37 rc 0 fails 0 cases -
r38 rc 0 fails 0 cases -
r39 rc 0 fails 0 cases -
r40 rc 0 fails 0 cases -
MUTANT N3-no-nonblock anchor_count 1
r36 rc 0 fails 0 cases -
r37 rc 0 fails 0 cases -
r38 rc 0 fails 0 cases -
r39 rc 0 fails 0 cases -
r40 rc 0 fails 0 cases -
MUTANT N4-strict-decode anchor_count 1
r36 rc 0 SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED []
r37 rc 0 SUMMARY cases=6 pass=6 fail=0 []
r38 rc 0 SUMMARY cases=10 pass=10 fail=0 []
r39 rc 0 SUMMARY cases=7 pass=7 fail=0 []
r40 rc 1 SUMMARY cases=8 pass=6 fail=2 ['case-invalid-utf8-in-repo-name', 'case-invalid-utf8-in-comment']
MUTANT N5-first-total anchor_count 1
r36 rc 0 fails 0 cases -
r37 rc 0 fails 0 cases -
r38 rc 0 fails 0 cases -
r39 rc 0 fails 0 cases -
r40 rc 1 fails 1 cases case-total-conflicting-second
MUTANT N7-lf-crlf-only anchor_count 1
r36 rc 0 fails 0 cases -
r37 rc 0 fails 0 cases -
r38 rc 0 fails 0 cases -
r39 rc 1 fails 1 cases case-crlf
r40 rc 0 fails 0 cases -
MUTANT N8-no-blank-skip anchor_count 1
r36 rc 0 fails 0 cases -
r37 rc 0 fails 0 cases -
r38 rc 1 fails 1 cases case-comments-and-blanks
r39 rc 0 fails 0 cases -
r40 rc 0 fails 0 cases -
MUTANT N9-no-comment-skip anchor_count 1
r36 rc 0 fails 0 cases -
r37 rc 0 fails 0 cases -
r38 rc 1 fails 2 cases case-empty-record,case-comments-and-blanks
r39 rc 1 fails 1 cases case-comments-total-only
r40 rc 1 fails 1 cases case-invalid-utf8-in-comment
```

Interpretation: M15/M16/M17/M18 are killed by r40 as expected; B2 and B3 survived all five fixtures when mutated, and the FIFO open-flag mutation also survived because the fixtures do not hand the parser a FIFO. N5 (“first TOTAL wins”) is killed by r40's conflicting duplicate case; its identical duplicate case exercises that the input is accepted, although it does not reject identical duplicates. The wider `splitlines()` terminator set is not fully specified by the fixture matrix: the observed parser accepts CR, VT, FF, NEL, and U+2028 separators. Mutation replacing `splitlines()` with LF-only splitting is killed only by r39's CRLF case; it does not show that the remaining accepted separators are intended or protected.

## Files and lines attacked

- `tools/souji-worktree-drift.py:124–179`: complete parser and all branch outcomes above; `run()` calls it at `:281`.
- `tests/fixtures/r36-worktree-drift.py:174–192`: malformed, repos-mismatch, empty, and nearby record cases.
- `tests/fixtures/r38-drift-record.py:102–122`: TOTAL aggregates, duplicate name, optional TOTAL, schema error, empty, missing path, comments/blanks.
- `tests/fixtures/r39-drift-record-rules.py:88–111`: trailing-space, TOTAL ordering, CRLF, containment, indented comment, TOTAL-only empty.
- `tests/fixtures/r40-drift-record-branches.py:99–120`: duplicate TOTAL, `--skip-unrecorded`, and invalid UTF-8 cases.
- `census/round-40/c3-counter.py:55–69,96–120`: declared M15–M18 mutants and scoring behavior.

Scratch was removed: `rm -rf -- /fast/scratch/hyaku/souji-r40/w2/R40w2scout03`; actual check printed `SCRATCH_REMOVED=yes`. No tools were installed or updated.