# DRAFT — round-55 lesson `## Gate` block for S278 (for the L1 to integrate)

Drafted by seat S55scribe01 (scribe), 2026-11-03. This is a **fragment** for the L1 to
integrate into `corpus/lessons/round-55.md` (`## Gate`). No corpus file was written by this
seat. Every fact below was re-measured by this seat on 2026-11-03 from the live page and the
committed bytes; the receipts are `../receipts/`.

---

- Admitted: **S278** — Python 3.12 library reference, `str.splitlines`.
  URL https://docs.python.org/3.12/library/stdtypes.html#str.splitlines; access date
  2026-11-03; `curl -sSL -o s278.html -w '%{http_code} %{url_effective}\n'` →
  `200 https://docs.python.org/3.12/library/stdtypes.html#str.splitlines` (no redirect:
  `num_redirects=0` on both the follow and the no-follow request), 648964 bytes, sha256
  `0b10fb9e7e5b8db1d1283835b98b6a9c167871bf6475937aa5d0e1467956a352` — byte-equal to the
  committed capture `census/round-55/sources/s278-python-stdtypes.html` (`cmp` exit 0).
  Capture: `census/round-55/sources/s278-python-stdtypes.html`. Located quotes (≤25 words
  each), in `census/round-55/sources/s278-located-quote.txt`:
  - section `str.splitlines(keepends=False)`, 18 words — "This method splits on the following
    line boundaries. In particular, the boundaries are a superset of universal newlines"
  - section `str.splitlines(keepends=False)`, 15 words — "Line breaks are not included in the
    resulting list unless keepends is given and true."
  - section `str.splitlines(keepends=False)`, 25 words — "\v or \x0b Line Tabulation \f or
    \x0c Form Feed \x1c File Separator \x1d Group Separator \x1e Record Separator \x85 Next
    Line (C1 Control Code)"
  - section `str.splitlines(keepends=False)`, 13 words — "Changed in version 3.2: \v and \f
    added to list of line boundaries"
  Tier A docs. Scope: the line-boundary superset that makes `splitlines()`-based line
  numbering diverge from LF-only numbering. Status `mined`. Used-by:
  `corpus/knowledge/splitlines-line-model.md`.
  <!-- L1 note: the drafted S278 row's scope cell in the working tree reads
       "the line-boundary set that the frozen C1 v4 counter's hidden-line numbering must
       agree with (the r54 sentinel S1 mechanism)". That is not the wording this seat was
       asked to carry. The wording above is the seat's assignment wording; the L1 picks one
       and makes the row and the Gate agree. -->
  Independent re-check by this seat (the r53 S276 / r54 S277 tag-strip recipe: strip
  `script`/`style`, strip tags, `html.unescape`, collapse whitespace runs): all four lines of
  `census/round-55/sources/s278-located-quote.txt` read `substring=True` and the word counts
  match (18 / 15 / 25 / 13). The page heading `Python 3.12.` is present (full heading
  `Python 3.12.16 documentation`). The seat's own check and the committed file agree.
  The mechanism the quote grounds is re-measured from the frozen counter bytes:
  `census/round-54/c1-counter.py` (sha256 `f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e`)
  numbers its hidden-line set with `text.splitlines()`, while the frozen
  `census/round-55/c1-counter.py` (sha256 `944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2`)
  numbers it with `text.split('\n')` — one line model for the hidden set and the correction's
  own line number, which is what the r54 HIGH sentinel S1 defect was.
