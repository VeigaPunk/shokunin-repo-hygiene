source: S278 — Python 3.12 library reference, str.splitlines (https://docs.python.org/3.12/library/stdtypes.html#str.splitlines; section "str.splitlines(keepends=False)"; page heading "Python 3.12.16 documentation"; served bytes sha256 0b10fb9e7e5b8db1d1283835b98b6a9c167871bf6475937aa5d0e1467956a352, 648964 bytes, curl -sSL HTTP 200, accessed 2026-11-03; capture census/round-55/sources/s278-python-stdtypes.html; located quotes census/round-55/sources/s278-located-quote.txt). The fence grammar this entry extends is corpus/knowledge/correction-filing-fence-grammar.md.
verified-at: 2026-11-03 — the page re-fetched live (HTTP 200, 648964 bytes, sha256 0b10fb9e…a352, byte-equal to the capture); the four located quotes re-checked as verbatim substrings of the tag-stripped capture; the S1 mechanism re-measured in a single-commit scratch fixture under the frozen r54 counter (exit 0, both corrections filed) and the r55 counter (exit 1, CORRECTION-IN-FENCE x2); the v4 counter sha256 944feafa94c2cbd9cb71f13b35bfd719eaeb34c91c4f2a541761e38cedd921a2 (census/round-55/c1-counter.py), frozen at census/round-55/preregistration.txt.
recheck: python3 -B census/round-55/c1-counter.py --root LANE --rev FULL40 --base f056aaa031bb65de27e7fa5daa38b0d4a443aedc --record-sha256 2b90a262c29772d4a9a7bd5ab29ce06b9d8f350832f0d0cd5114d52b0f6dad30 --sources-rev-before f778b9d131574d3ff09c0cc8a077643c0fc84bb4 --sources-rev-after 9bf9234ae4d11c7b31706354302a9e95ad0d1f81 --scratch DIR (the real lane exits 0 with `alias=0 pairinert=0 unfiled=0`); and re-check the S278 quotes against a fresh fetch (every quote substring=True).

# One line model for the correction-filing counter

## What this entry is

A line counter has two numberings that must agree. The filing counter (`census/round-55/c1-counter.py`) computes the hidden-line set (fences, HTML comments) and the line number a correction names from the same text. If the two use different line breakers, a refusal can go dark without any finding.

## The mechanism (the r54 HIGH, sentinel S1)

S278 states that `str.splitlines()` breaks on a superset of universal newlines: `\n`, `\r`, `\r\n`, `\v` (or `\x0b`), `\f` (or `\x0c`), `\x1c`, `\x1d`, `\x1e`, `\x85`, `\u2028`, `\u2029`. The v3 counter numbered the hidden set with `splitlines()` but numbered each correction with `count('\n')`. Two form-feed lines above a `~~~` fence therefore moved the fence off the correction lines: the correction sat outside the fence in the hidden-set numbering, and the refusal went silent.

Measured (single-commit scratch fixture, rev equal to base, so DELETED-LINES cannot fire):

- frozen v3 counter (`census/round-54/c1-counter.py`): exit 0, `filed=2 unfiled=0 fenced=0`, both corrections accepted;
- v4 counter (`census/round-55/c1-counter.py`): exit 1, `FINDING CORRECTION-IN-FENCE` at SCORECARD.md:10 and :11, `fenced=2`.

## The rule

Every line number in the filing counter is LF-based: the hidden set (`text.split('\n')`), the correction's own line number, the site line, the pair scan and the record count all use one split. A correction is therefore located on the same line its fence grammar was read from. The rule is a fixed property of the counter, so it does not depend on which exotic separators a file happens to carry.

## What this entry does not establish

- Git's numstat output is parsed with `splitlines()` on its own records. Under the counter's scrubbed environment (default `core.quotePath`) git C-quotes path names carrying control or non-ASCII bytes, and each affected record stays one line: measured in a scratch repository, `"vt\vname"` and `"nel\302\205name"`, three fields each, all counted. A REPOSITORY-LOCAL `core.quotePath=false` is not neutralized (the counter disables only global and system git config), and then a raw U+0085 in a path splits its record under `splitlines()`: measured, `splitlines records: 3 counted (3 fields): 2`, the NEL-named deletion uncounted. This is a named limit of the frozen v4 bytes (DELETED-LINES blind for that path under that repo setting), routed to r56 as a counter version that parses numstat on `\n` only, with a red-before fixture.
- CR-only line endings (no LF anywhere) are one line to this counter, so a CR-only file is not split into filings. This is a named limit of the one-line model, not a refusal.
- S278 does not establish how a Markdown renderer breaks lines; the counter's model is a fixed reading of the file bytes, chosen for re-derivability, not a claim about any renderer.
- The HTML comment class stays the line-level `<!--`/`-->` grammar (CommonMark 0.31.2 HTML blocks, S277, are wider; the divergence is named in the S277 entry).
