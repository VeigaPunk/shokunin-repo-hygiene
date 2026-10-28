source: S255 Python `inspect.cleandoc` — https://docs.python.org/3/library/inspect.html#inspect.cleandoc (snapshot census/round-40/sources/inspect.html sha256 9e740c60462d2648ecd5b9ae1cf5ee96f2fed5e312fb56cae639385c5415a0d6; opened 2026-10-28)
verified-at: 2026-10-28 — Python documentation page and installed Python 3.14.8 behavior opened/read; no lane tool executed through this source
recheck: 365d — reopen the inspect.cleandoc section and compare the quoted sentence: `grep -n 'Any leading whitespace' census/round-40/sources/inspect.html`
ground: F1 — worktree-drift instrument documentation reading (C2 source-quote correction)

# S255 corrects the inspect.cleandoc quotation, not the lane's join rule

S255 **supersedes S252's quotation and attribution**. The r40 source row S252 quoted the installed
interpreter's `inspect.cleandoc.__doc__` text as though it appeared verbatim in the cited
`docs.python.org` page. The page's actual wording at the `inspect.cleandoc` definition is:

> “Any leading whitespace that can be uniformly removed from the second line onwards is removed.”

The located text is `census/round-40/sources/inspect.html:1210-1211` (the anchor is
`id="inspect.cleandoc"` at line 1206). It is not a rule that logical entries must be joined, nor a
class-entry grammar. The C2 analyser's class-row/continuation join is a lane implementation choice;
its behavior is tested by `tests/fixtures/r40-docstring-joined.py`, not asserted by S255.

The older knowledge entry `docstring-class-continuation-lines-r40.md` remains as filed. Its explanation
of the analyser's behavior is local implementation evidence, but its attribution of the join principle
to the inspect docs is superseded by this source correction.

Limit: `cleandoc`'s indentation normalization does not prove that a particular refusal map groups
continuation lines under a specific class token; that relationship needs its own parser/fixture
contract.
