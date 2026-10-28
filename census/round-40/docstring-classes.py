#!/usr/bin/env python3
"""census/round-40/docstring-classes.py — read a refusal-class map out of a module docstring.

The r39 C2 L4 leg extracted a class map with one docstring line per class, so a trigger that the
tool documents on a *continuation* line was invisible to the analyser. `tools/souji-worktree-drift.py`
documents `RECORD-OUTSIDE-ROOT` over two lines:

    RECORD-OUTSIDE-ROOT    a record row, or the gitdir it resolves to, escapes
                           --root

The trigger `--root` lives on the continuation line, so the one-line analyser can never see it and the
L4 leg could only ever check the classes whose trigger happened to sit on the first line.

This module joins a class entry's continuation lines into one entry, so a class is described by its
whole documentation, not by its first physical line. The docstring is read through `ast` only
(`ast.get_docstring(..., clean=False)`) — never by slicing the source text (the r38 M5 finding).

PEP 257 (S252, opened 2026-10-28) is the shape this analyser follows: a multi-line docstring is one
logical line whose continuation lines are indented under it, and "the continuation lines ... should be
joined" to form the summary.

Functions:
  docstring_of(source)        -> the module docstring of Python source text ("" when there is none)
  class_entries(doc)          -> ordered dict: class token -> joined entry text
  first_line_entries(doc)     -> ordered dict: class token -> first physical line only (the r39 read)
  classes_from_source(source) -> class_entries(docstring_of(source))
"""
import ast
import re

# A class entry: an upper-case hyphenated token, then two or more spaces, then the description.
# The tool's docstring indents its refusal list by two spaces and aligns the description under it;
# a single space after the class token is not an entry.
CLASS_LINE = re.compile(r"^\s*(?P<cls>[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)\s{2,}(?P<text>.*)$")


def docstring_of(source):
    """The module docstring of Python source text, through `ast` only."""
    tree = ast.parse(source)
    return ast.get_docstring(tree, clean=False) or ""


def _entries(doc, join):
    out = {}
    order = []
    current = None
    for line in doc.split("\n"):
        match = CLASS_LINE.match(line)
        if match:
            current = match.group("cls")
            if current not in out:
                out[current] = match.group("text").strip()
                order.append(current)
            continue
        if current is None:
            continue
        stripped = line.strip()
        if not stripped:
            # A blank line ends the entry: the docstring separates the refusal list from the prose
            # that follows it, and a blank line is not a continuation.
            current = None
            continue
        if line[:1].isspace() and stripped:
            # A continuation line: indented under the entry it belongs to.
            if join:
                out[current] = (out[current] + " " + stripped).strip()
            continue
        # A non-indented, non-class line ends the entry.
        current = None
    return out


def class_entries(doc):
    """Class token -> the entry's full text, continuation lines joined with one space."""
    return _entries(doc, True)


def first_line_entries(doc):
    """Class token -> the entry's first physical line only (the r39 reading)."""
    return _entries(doc, False)


def classes_from_source(source):
    return class_entries(docstring_of(source))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("usage: docstring-classes.py PATH\n")
        raise SystemExit(2)
    with open(sys.argv[1], encoding="utf-8") as handle:
        src = handle.read()
    for cls, text in classes_from_source(src).items():
        print("%s\t%s" % (cls, text))
