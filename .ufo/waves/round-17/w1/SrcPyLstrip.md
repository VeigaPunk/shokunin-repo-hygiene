STATUS: DONE — the served Python page states the char-set rule verbatim; no contradiction; draft row ready, one landing precondition (round-17 lesson absent).

# SrcPyLstrip — Python `str.lstrip(chars)` is a character set, not a prefix (C2 source)

## Access record (opened 2026-10-20)

- Requested: `https://docs.python.org/3/library/stdtypes.html#str.lstrip` and `#str.removeprefix`.
- The site answers **HTTP/2 301**:
  `location: https://docs.python.org/3/builtins/stdtypes.html`
  (`curl -sSI https://docs.python.org/3/library/stdtypes.html`, 2026-10-20 16:33 UTC).
  The canonical URL for the row is therefore `/3/builtins/stdtypes.html`, not `/3/library/…`.
- Served page: title **“Built-in Types — Python 3.15.0 documentation”**; footer
  **“Last updated on Oct 20, 2026 (13:43 UTC).”** (Sphinx 8.2.3). No other version stamp on the
  `str.lstrip` section; `str.removeprefix` carries “Added in version 3.9.”
- Sections: `## Text Sequence Type — str` (`#text-sequence-type-str`) ›
  `### String Methods` (`#string-methods`) › definition `str.lstrip` (`#str.lstrip`);
  `str.removeprefix` (`#str.removeprefix`).

## (1) Located quote (verbatim, 15 words)

> “The *chars* argument is not a prefix; rather, all combinations of its values are stripped:”

— `https://docs.python.org/3/builtins/stdtypes.html#str.lstrip`, § String Methods ›
`str.lstrip`, first paragraph, fourth (final) sentence (`chars` italic in the source; the page
ends the sentence with a colon before its two examples). Word count: 15. The preceding sentence
is “The *chars* argument is a string specifying the set of characters to be removed.”

Corroborating quotes in the same `str.lstrip` entry, same page:

> “The *chars* argument is a string specifying the set of characters to be removed.”

> “See `str.removeprefix()` for a method that will remove a single prefix string rather than all
> of a set of characters.” (20 words)

with examples `'   spacious   '.lstrip()` → `'spacious   '`,
`'www.example.com'.lstrip('cmowz.')` → `'example.com'`, and
`'Arthur: three!'.lstrip('Arthur: ')` → `'ee!'` (the set eats `t h r e` from the next word).

At `#str.removeprefix`:

> “If the string starts with the *prefix* string, return `string[len(prefix):]`. Otherwise,
> return a copy of the original string.”

## (2) Drafted SOURCES row (11 columns, registry order; `S0??` — L1 numbers it)

```
| S0?? | Python Built-in Types documentation: str.lstrip, str.removeprefix — https://docs.python.org/3/builtins/stdtypes.html#str.lstrip | docs | A | str.lstrip(chars) character-set semantics and its removeprefix contrast on the served Python 3.15.0 page; not bytes.lstrip and not audit-tool behaviour | § String Methods › str.lstrip (#str.lstrip) and str.removeprefix (#str.removeprefix); page title "Built-in Types — Python 3.15.0 documentation", footer "Last updated on Oct 20, 2026 (13:43 UTC)"; /3/library/stdtypes.html 301s to this canonical URL (curl -sSI 2026-10-20) | lstrip(chars) strips any combination of the characters in chars from the leading run, not a prefix, while removeprefix removes one prefix string; so target.lstrip("./") drops .ufo's leading dot — the r16 seat-audit V-WRITE-SCOPE false positive | mined | 2026-10-20 | on-release | corpus/lessons/round-17.md |
```

Notes for integration (all observed):

- **Next unused id is S051**: `corpus/SOURCES.md` holds 50 rows, ids S001–S050 (count command
  below). `S0??` above is deliberately unnumbered; substitute S051 if the table is unchanged.
- **Status `mined` has one landing precondition.** `corpus/lessons/round-17.md` is **absent**
  at 2026-10-20 (`test -e corpus/lessons/round-17.md` → absent). The frozen census check
  (“mined rows whose used-by paths do not exist — must print nothing”) will print
  `missing: corpus/lessons/round-17.md` until the lesson exists. Land the row **with or after**
  the round-17 lesson; if L1 lands it earlier, use `queued` / `used-by —` and flip
  `queued → mined` with an old→new line in the lesson, per contract rule 2.
- Why `mined` rather than `queued`: the page grounds a lane change this round — the C2/D4
  seat-audit precision fix (the `.ufo` false positive named at
  `corpus/lessons/round-16-verifier-spotcheck.md:138`). The row does **not** ground the other two
  r16 w2 `V-WRITE-SCOPE` false positives (first-comma `write_target` prose split), which are
  grounded by the seat-audit transcripts, not by this page.
- `tier A` is scoped to Python string-method semantics (official language docs). `on-release`
  recheck: the page moves with the Python release; its last-updated line now tracks the
  3.15.0 development docs.
- `kind docs`; no `|` inside any cell (verified by eye and by the census `NF!=13` awk shape).
- Existing Python rows are S040 (`pathlib`, `/3/library/pathlib.html`) and S050 (`compile()`,
  `/3/library/functions.html`); this row is not a duplicate and adds the first string-method
  source. Only the `stdtypes` redirect was tested this round (301 to `/3/builtins/`); the other
  two rows' URLs were not re-tested and are left untouched (append-only).

## (3) Contradiction check against the context's claim

**No statement on the page contradicts** the claim “`str.lstrip(chars)` strips any combination
of the given characters, not a prefix”. The page states exactly that rule
(“is not a prefix; rather, all combinations of its values are stripped”), and its own example
strips a `.` that is not a prefix position in the usual sense
(`'www.example.com'.lstrip('cmowz.')` → `'example.com'`).

Two non-contradictions worth naming so they are not mistaken for conflicts:

1. The page says “combinations of its **values**”, the claim says “given **characters**”; the
   preceding sentence defines `chars` as “the set of characters to be removed”, so the two are
   the same rule in different words.
2. The request named `/3/library/stdtypes.html`; the served canonical is
   `/3/builtins/stdtypes.html` (301). A location correction, not a semantic one.

Boundary worth keeping, not a contradiction: “all combinations” operates on the **contiguous
leading run** of characters drawn from the set. The examples show removal stopping at the first
character outside the set (`'www.example.com'.lstrip('cmowz.')` → `'example.com'`, stopping at
`e`), so set characters after a non-set character survive. The `.ufo` dot is leading, so it is
removed; the claim's wording is bounded by this, not contradicted.

[INFERENCE] For the lane's concrete string: because `.` is in the set `"./"`,
`'.ufo/x'.lstrip('./')` yields `'ufo/x'` — the dot is removed. I did not execute Python (a
`python3 -c` probe is outside this seat's ALLOWED-EXEC list); the inference follows from the
quote plus the page's dot-stripping example, and the r16 spotcheck already records the observed
misread at `tools/souji-seat-audit.py:76-82`.

## Smallest fix (advisory, for C2/D4)

Replace the character-set call with a single-prefix removal, e.g.
`target[2:] if target.startswith("./") else target`, or `target.removeprefix("./")`
(the page's own recommendation; `removeprefix` is 3.9+, host Python 3.14). If the input can
carry repeated `./` segments, loop the single-prefix removal rather than returning to `lstrip`.

## Verdict

**holds** — the docs answer the question directly and in the strongest form (“not a prefix”),
support the r16 FP classification, and contradict nothing in the claim text.

## Commands run (exact)

```
curl -sSI https://docs.python.org/3/library/stdtypes.html | sed -n '1,12p'
# HTTP/2 301 … location: https://docs.python.org/3/builtins/stdtypes.html … date: Tue, 20 Oct 2026 16:33:26 GMT

# page capture (read tool) then:
grep -n "str.lstrip\|removeprefix\|lstrip(" <captured page>      # anchors 1448-1449, 2043-2134, 3128-3424
sed -n '2043,2075p' <captured page>                              # lstrip entry, quote + examples
sed -n '2103,2120p' <captured page>                              # removeprefix entry
sed -n '5990,6036p' <captured page>                              # footer: last updated / version
grep -n "Changed in version" <captured page> | awk -F: '$1>2040 && $1<2140'   # none for lstrip

cd /home/vgpnk/Projects/shokunin/souji-shokunin
grep -nE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md | cut -d'|' -f2 | tr -d ' ' | sort | sed -n '1p;$p'
# S001 … S050
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
# 50
test -e corpus/lessons/round-17.md && echo EXISTS || echo ABSENT
# ABSENT
grep -n "docs.python.org" corpus/SOURCES.md
# :54 S040 pathlib, :64 S050 compile
grep -n "lstrip" corpus/lessons/round-16-verifier-spotcheck.md
# :138 the .ufo dot misread at tools/souji-seat-audit.py:76-82
test -d .ufo/waves/round-17/w1 && echo EXISTS
# EXISTS
```

Probe compliance: no `jj`, no git write, no lane census/verify tool run against a real
directory; reads limited to the named files (`CORPUS.md` § SOURCES, `corpus/SOURCES.md`,
`corpus/lessons/round-16-verifier-spotcheck.md`) plus existence checks. No tool installs, no
pacman transactions. Nothing written outside this report.
