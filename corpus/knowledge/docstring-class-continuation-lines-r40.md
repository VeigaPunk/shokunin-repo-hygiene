source: S252 Python `inspect.cleandoc` (https://docs.python.org/3/library/inspect.html#inspect.cleandoc; snapshot census/round-40/sources/inspect.html, sha256 9e740c60462d2648ecd5b9ae1cf5ee96f2fed5e312fb56cae639385c5415a0d6; installed interpreter Python 3.14.8, snapshot census/round-40/sources/inspect-cleandoc.txt, sha256 aab0711daa22215875bf559d3ce8d641062646d9946ad232dee70484e7b9a093)
verified-at: 2026-10-28 — Python 3.14.8 on kernel 7.2.11-arch1-1; read-only (`inspect.getdoc` on the installed module, no import of the lane's tools)
recheck: 365d — re-read the `inspect.cleandoc` documentation after a Python release: `python3 -c "import inspect; print(inspect.getdoc(inspect.cleandoc))"`
ground: F1 — git-native housekeeping vs receipts (the refusal-class contract the lane's F1 worktree-drift detector documents)

# A docstring's continuation lines belong to the entry they are indented under

## Claim (F1, sourced)

The lines of a docstring after the first are continuations of one logical block, and the uniform
indentation is what marks them as such. Python's own `inspect.cleandoc` documents exactly this
reading: "Any whitespace that can be uniformly removed from the second line onwards is removed"
(S252, `inspect.cleandoc`, installed interpreter Python 3.14.8, snapshot
`census/round-40/sources/inspect-cleandoc.txt`).

A refusal class documented over two physical lines is therefore ONE entry, not two, and a trigger
that the tool names on the second line is part of that entry's contract.

## The defect this repaired

`tools/souji-worktree-drift.py` documents its refusal classes over aligned lines:

    RECORD-OUTSIDE-ROOT    a record row, or the gitdir it resolves to, escapes
                           --root

The round-39 C2 leg read ONE physical line per class (`docstring_classes()`), so the trigger that
names the condition — `--root` — lived on a continuation line the analyser could not see, and the leg
could only ever check the classes whose trigger happened to sit on the first line. The round-40
analyser (`census/round-40/docstring-classes.py`) joins the continuation lines into one entry and
reads the docstring through `ast` only (`ast.get_docstring(..., clean=False)`), never by slicing the
source text.

## Evidence

- `python3 -B tests/fixtures/r40-docstring-joined.py` → `SUMMARY cases=9 pass=9 fail=0` at the
  audited revision; the same fixture with `--one-line` (the r39 reading) →
  `SUMMARY cases=9 pass=6 fail=3`, so the old reading misses the wrapped trigger
  (`census/round-40/records/c2-after-d.txt`, `census/round-40/records/fixtures-after.txt`).
- The C2 counter's L4 leg re-derives the class/trigger pairs at run time — each pair's trigger must
  actually be raised by the audited tool — so a pair the tool no longer raises fails the leg instead
  of passing vacuously.

## Limits

- The join rule is the lane's reading of the class-entry layout (an upper-case hyphenated token
  followed by two or more spaces); it is not a PEP 257 parser and does not claim to be one.
- `cleandoc` removes the uniform indentation; the analyser JOINS the lines instead, because the
  trigger has to be searchable inside one entry. The two are complementary, not equivalent.
- A class entry whose trigger is named nowhere in its text is a documentation defect the analyser
  reports as a missing trigger; it does not guess the trigger from the runtime behaviour.

## Round 40 wave-2 source correction (append-only)

S252's short quote was verbatim only in the installed interpreter docstring, not in the cited
Python documentation page. S255 carries the exact page wording and its limit: `inspect.cleandoc`
documents indentation normalization; the lane's class-entry continuation join is an implementation
choice measured by the fixture, not a rule stated by this source. W2 also found the frozen C2
pair/probe set was authored after dispatch; see lesson M40-3. This entry remains a record of the
implementation reading, not proof that the C2 claim was frozen completely.
