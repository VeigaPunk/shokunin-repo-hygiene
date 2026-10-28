# W1ScoutAst — ast.get_docstring (r39 C2 L4)

Seat: W1ScoutAst. Advisory only. No lane bytes other than this report. No installs.
Access date: 2026-10-28.
Axes checked: signature, None-on-missing, clean, located quote, URL, r39 grounding, SOURCES-row duplication.

## Verdicts

| check | verdict |
| --- | --- |
| Documented signature | `ast.get_docstring(node, clean=True)`. Installed `inspect.signature` is `(node, clean=True)`. |
| Returns None when there is no docstring | Yes. Docs and the installed docstring both say so. A module whose body is not a string expression returns `None`. A node that cannot have a docstring raises `TypeError` instead. |
| `clean` affects behaviour | Yes. Default `clean=True` runs `inspect.cleandoc`. `clean=False` returns the raw string. |
| Located quote (17 words) | "(which must be a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None if it has no docstring." |
| URL | https://docs.python.org/3.14/library/ast.html#ast.get_docstring |
| Access date | 2026-10-28 |
| r39 fact grounded | Yes: C2 L4 reads the module docstring through `ast.parse` + `ast.get_docstring`, not by slicing source. |
| Duplicates an existing SOURCES row | Yes. Same scope as S248 (`corpus/SOURCES.md` registry row; Gate in `corpus/lessons/round-39.md`). Not a new row. |

## Commands and output

### 1. Installed docstring and signature

Command:

```
python3 -c "import ast,inspect,sys; print('VERSION', sys.version); print('---DOC---'); print(ast.get_docstring.__doc__); print('---SIG---'); print(inspect.signature(ast.get_docstring)); print('---FILE---'); print(inspect.getfile(ast))"
```

Output:

```
VERSION 3.14.8 (main, Oct  2 2026, 10:23:31) [GCC 16.2.1 20260810]
---DOC---

Return the docstring for the given node or None if no docstring can
be found.  If the node provided does not have docstrings a TypeError
will be raised.

If *clean* is `True`, all tabs are expanded to spaces and any whitespace
that can be uniformly removed from the second line onwards is removed.
---SIG---
(node, clean=True)
---FILE---
/usr/lib/python3.14/ast.py
```

Installed body at `/usr/lib/python3.14/ast.py:294-315`: a node other than FunctionDef, AsyncFunctionDef, ClassDef, or Module raises TypeError. Otherwise the first body statement must be an Expr whose value is a string Constant, else None. If clean is true, the text passes through inspect.cleandoc.

### 2. Docs page for the installed series

Opened https://docs.python.org/3.14/library/ast.html#ast.get_docstring on 2026-10-28.
Page title observed: `ast — Abstract syntax trees — Python 3.14.10 documentation`.
The /3.14/ manual is the 3.14.10 docs build. The interpreter on this host is 3.14.8. The section text below is what that page returned.

Located section, heading `ast.get_docstring(node, clean=True)`:

```
Return the docstring of the given node (which must be a FunctionDef, AsyncFunctionDef, ClassDef,
or Module node), or None if it has no docstring.
If clean is true, clean up the docstring's indentation with inspect.cleandoc().
```

Changed-in note on the same entry: "Changed in version 3.5: AsyncFunctionDef is now supported."

The next entry on the same page is `ast.get_source_segment(source, node, *, padded=False)`: "Get source code segment of the source that generated node". That function takes source text. get_docstring does not.

Located quote, 17 words, from the first sentence of that section:

> (which must be a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None if it has no docstring.

Second located sentence, 11 words, for the clean check:

> If clean is true, clean up the docstring's indentation with inspect.cleandoc().

### 3. Behaviour probe (installed 3.14.8)

Command (python3 stdin):

```
import ast, inspect, sys
print("version", sys.version.split()[0])
print("signature", inspect.signature(ast.get_docstring))
src = "def f():\n\t\"\"\"\n\thello\n\t\"\"\"\n"
mod = ast.parse(src)
print("clean True repr", repr(ast.get_docstring(mod.body[0], clean=True)))
print("clean False repr", repr(ast.get_docstring(mod.body[0], clean=False)))
empty = ast.parse("x = 1\n")
print("no docstring", ast.get_docstring(empty))
try:
    ast.get_docstring(ast.Pass())
except TypeError as e:
    print("typeerror", type(e).__name__, str(e))
```

Output:

```
version 3.14.8
signature (node, clean=True)
clean True repr 'hello'
clean False repr '\n\thello\n\t'
no docstring None
typeerror TypeError 'Pass' can't have docstrings
```

clean=True and clean=False differ. A missing docstring is None, not an exception. A node type outside the four named classes is TypeError.

## r39 fact

Fact: the C2 L4 docstring read is ast-only, not source slicing.

Ground: `census/round-39/c2-counter.py` `docstring_classes` (lines 133-137) says "ast only, no source slicing", does `tree = ast.parse(...)`, then `doc = ast.get_docstring(tree, clean=False) or ""`. The call passes the Module node. It does not call `ast.get_source_segment` and does not slice the file text for the docstring. clean=False keeps indentation out of the class-line match. clean still changes the returned string when left at its default, which this leg does not do.

get_docstring grounds that fact because its documented inputs are the node and clean, and a missing docstring is None. It does not ground a claim about source spans. That is get_source_segment, which the round-39 Gate already rejects for this check (`corpus/lessons/round-39.md` Gate reject row).

## SOURCES duplication

Registry row S248 (`corpus/SOURCES.md`, opened 2026-10-28, tier A, mined):

- source: Python docs, ast.get_docstring — https://docs.python.org/3/library/ast.html#ast.get_docstring
- scope: the ast-only module-docstring read the r39 C2 L4 analyser uses; not source text slicing, not ast.get_source_segment
- quote recorded in the row and in `corpus/lessons/round-39.md` Gate: "(which must be a FunctionDef, AsyncFunctionDef, ClassDef, or Module node), or None if it has no docstring."

No other registry row names ast.get_docstring. S248's scope is this seat's question. Opening another row would duplicate it.

Locator difference, not a new scope: S248's anchor says the unversioned /3 URL was the Python 3.15.2 page. This seat did not re-fetch /3. It opened /3.14/ for the installed 3.14.8 interpreter. That page's title is the 3.14.10 documentation, and the None-sentence matches S248's quote.

## Unresolved

- Whether the live /3 page is still the 3.15.2 build S248 recorded. Not re-fetched here.
- Patch-level identity of the 3.14.10 docs build versus the 3.14.8 Lib/ast.py docstring. Wording of the clean sentence differs (docs: inspect.cleandoc; installed __doc__: tabs expanded and uniform whitespace removed from line 2 on). Signature, None, and "clean changes the string" agree on both.
