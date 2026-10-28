# R40w2reviewer06 — C2 fixture attack

**Verdict: SAFE for the scoped fixture-level discrimination claim; not every individual case is load-bearing.** The fixture passes on landed joined analyzer bytes, fails on `--one-line`, and fails under both requested bad-analyzer stubs. Several individual assertions remain green under those bad analyzers, so the fixture's guarantee comes from the aggregate failure, not every case independently detecting every defect.

## Target and evidence

Attacked `tests/fixtures/r40-docstring-joined.py` at landed commit `128e412b0ced3c243dc27c3dd3332054a611bc2e` (not the checked-out HEAD). It is the nine `case(...)` assertions at lines 64–94; analyzer loading and mode selection are lines 41–58. Relevant behavior: line 57 chooses `first` for `--one-line` and `joined` otherwise; lines 70–72 directly assert the real first-line reader omits the synthetic continuation trigger; lines 88–94 compare the two maps. Frozen trigger checks are lines 73–87.

The archived landed inputs had SHA-256:
- `census/round-40/docstring-classes.py`: `bc418a58e751a69f00d5d9c207d5c174f486e759418f52367eb7fe0a339105ba`
- `tests/fixtures/r40-docstring-joined.py`: `0dc6c789a7419de19c39b6ab4ed130254bf68eb36d4a55b28397373616e455eb`
- `tools/souji-worktree-drift.py`: `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76`

I exported those three paths with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive --format=tar 128e412b0ced3c243dc27c3dd3332054a611bc2e census/round-40/docstring-classes.py tests/fixtures/r40-docstring-joined.py tools/souji-worktree-drift.py | tar -xf - -C "$S/src"`, where `S=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06` and `TMPDIR="$S"`. No tools were installed. LSP was unavailable (`read xd://lsp` returned “No such tool: xd://lsp”), so no LSP semantic checks were possible.

## Commands and actual output

All four commands used the archived commit inputs and explicit analyzer/tool paths. Exact invocations and output:

```text
$ TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06 python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/tests/fixtures/r40-docstring-joined.py --analyzer /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/census/round-40/docstring-classes.py --tool /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/tools/souji-worktree-drift.py
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
EXIT=0

$ TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06 python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/tests/fixtures/r40-docstring-joined.py --analyzer /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/census/round-40/docstring-classes.py --tool /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/tools/souji-worktree-drift.py --one-line
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
EXIT=1

$ TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06 python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/tests/fixtures/r40-docstring-joined.py --analyzer /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/empty-map.py --tool /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/tools/souji-worktree-drift.py
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
EXIT=1

$ TMPDIR=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06 python3 -B /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/tests/fixtures/r40-docstring-joined.py --analyzer /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/one-line-map.py --tool /fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/tools/souji-worktree-drift.py
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
EXIT=1
```

## Interpretation / rerun details

The empty-map stub implemented `docstring_of` using `ast.get_docstring(ast.parse(source), clean=False) or ""`, with `class_entries` and `first_line_entries` both returning `{}`. The one-line-map stub delegated `docstring_of` to the archived analyzer and delegated **both** map methods to its `first_line_entries`. These are intentionally faulty analyzer substitutes, not edits to landed files.

The fixture as a whole is load-bearing: the joined analyzer gets 9/9 and exit 0; the legacy mode gets 3 failures and exit 1; empty-map and one-line-map analyzers get 6 and 4 failures respectively. The one-line map is caught by the synthetic joined assertion and the real wrapped `--root` checks. Empty-map is caught by positive-content assertions.

Not every case can fail against the requested attacks: `synthetic-one-line-misses-trigger` passes with both stubs because it checks a negative property of `first_line_entries` (and the empty map trivially satisfies it); `class-sets-equal` and `joined-not-shorter` pass for empty maps because both sides are empty, and also pass for the one-line-map stub because the two methods intentionally return the same map. These are individually non-discriminating for those mutants. This is not an aggregate vacuous pass: each faulty analyzer is rejected.

To rerun after scratch cleanup: create `$S/src`, perform the stated `git archive` command, and recreate the two stubs as follows (all under the assigned scratch root):

```python
# empty-map.py
import ast
def docstring_of(source): return ast.get_docstring(ast.parse(source), clean=False) or ""
def class_entries(doc): return {}
def first_line_entries(doc): return {}
```

```python
# one-line-map.py
import importlib.util
BASE = "/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06/src/census/round-40/docstring-classes.py"
spec = importlib.util.spec_from_file_location("base_docstring_classes", BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
def docstring_of(source): return base.docstring_of(source)
def class_entries(doc): return base.first_line_entries(doc)
def first_line_entries(doc): return base.first_line_entries(doc)
```

The scratch directory `/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer06` was removed before yielding. Report file: `.ufo/waves/round-40/w2/R40w2reviewer06.md`.
