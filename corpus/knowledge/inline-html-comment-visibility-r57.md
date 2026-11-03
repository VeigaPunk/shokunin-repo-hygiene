---
source: S279 (WHATWG HTML Living Standard, §13.1.6 Comments, https://html.spec.whatwg.org/multipage/syntax.html, served 2026-11-03) and S280 (CommonMark 0.31.2, §6.6 Raw HTML, https://spec.commonmark.org/0.31.2/, served 2026-11-03); captures census/round-57/sources/s279-whatwg-html-syntax.html (sha256 ad4bdaca53226b0c6f5962786f309fea3ca4e59bec86b026cb3fc5d641b25ff1) and census/round-57/sources/s280-commonmark-0.31.2.html (sha256 c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d)
verified-at: 2026-11-03, revision d749f7ee081ec1b382b2f92577eb22bfba1c7761 (round-57 freeze)
recheck: `curl -sSL https://spec.commonmark.org/0.31.2/ | sha256sum` must print c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d, and the §6.6 located quote in `census/round-57/records/source-quotes.txt` must remain a verbatim substring of the served page
---

# Inline HTML comments decide visibility in markdown source, and the authoring rule is not the renderer's rule

## The two rules

- **WHATWG HTML, §13.1.6 Comments** — a comment is `<!--` + optional text + `-->`; the *text* must not
  start with `>` or `->`, must not contain `<!--`, `-->` or `--!>`, and must not end with `<!-`. This is
  an **authoring** restriction on a complete comment's text.
  Located quote (11 words, verified substring of the served page): "Comments must have the following
  format: The string " <!-- "."
  Second located quote (17 words): the text must not start with the string " > ", nor start with the
  string " -> ".
- **CommonMark 0.31.2, §6.6 Raw HTML** — an inline HTML comment is `<!-->` or `<!--->` or else `<!--`
  followed by "a string of characters not including the string `-->`" and then `-->`. This is a
  **renderer** grammar: it says nothing about where the opener sits on a line and restricts the text
  only against the closer.
  Located quote (24 words): "An HTML comment consists of <!--> , <!---> , or <!-- , a string of
  characters not including the string --> , and -->"

The consequence that matters to a hygiene counter: **a `<!--` that does not start a line still opens a
comment**, and the comment ends at the first later `-->` — possibly several lines below. Every line the
span covers is not rendered as text. A counter that only recognises openers at line start (v5) counts a
correction filing inside such a span as filed, because it never sees the span.

## Measured visibility (independent renderer, round 57)

`markdown-it-py 4.2.0` (`MarkdownIt('commonmark')`), rendered output with comment spans removed, token
count of `R52-CORRECTION` in the visible text:

| fixture shape | source | visible tokens | v5 verdict | v6 verdict |
|---|---|---|---|---|
| B4 NBSP-prefixed opener, closer two lines later | `\xc2\xa0<!-- …` (U+00A0 is a character, not indentation) | 0 | files them (exit 0) — **harm** | refuses (CORRECTION-IN-FENCE, hidden_by=inline) |
| C4 closed multi-line inline comment | `prose … <!-- opens`, closer on a later line | 0 | files them (exit 0) — **harm** | refuses (hidden_by=inline) |
| C6 complete one-line inline comment | `prose <!-- same line --> stays inline` | 2 | accepts (exit 0) | accepts (exit 0); the span covers only its own line |
| F29 mention with no closer anywhere | `mentions the token <!-- inside a sentence` | 2 | accepts (exit 0) | accepts (exit 0); no closer means literal text |

Fixtures: `census/round-57/fixtures/build-fixtures.py` (B4-INLINE-NBSP-OPENER,
C4-INLINE-CLOSED-COMMENT, C6-INLINE-SAME-LINE, F29-PROSE-COMMENT-MENTION); matrices
`census/round-57/records/matrix-dryrun/c1-matrix-v{5,6}.tsv`; render reproduction: the round lesson
`corpus/lessons/round-57.md` `## Wave findings` (reviewer01 receipts).

## Named limits of the line-level approximation

- The counter marks a **whole line** hidden when any part of an inline span covers it, and does not mark
  a partially covered line as partially visible.
- A `<!--` on a line with four or more leading spaces is treated as indented code and opens nothing; a
  lazy paragraph continuation with that indentation is not modelled.
- Other HTML block types (CDATA, processing instructions, declarations) are not comments and are not
  modelled; HTML block type 2 (line-start opener) is.
- Validity beyond "a closer exists" is not judged. The two specs disagree about what text is legal
  (WHATWG restricts text; CommonMark only excludes the closer); the counter follows the **renderer**
  (S280) because it grades markdown source, so a WHATWG-invalid comment with a later closer is still
  hidden here. A future entry that grades raw HTML authoring would have to follow S279 instead.
- `<!-->` / `<!--->` close on their own line and hide only that line; the counter special-cases both.

## Why this matters for a filing counter

A "correction filed" claim is a claim about a reader seeing a line. A hidden span is a property of the
rendered document, not of the source line's first character, so the grammar that decides it is the
renderer's. r56 shipped the opposite narrowing — line-start openers only — to repair an over-hide
(prose mentions), and that repair created the B4/C4 over-acceptance the non-author closure caught.
Both directions have to be pinned by a fixture in the same frozen set: an over-hide control (F29) and a
hidden-span control (B4/C4).
