---
source: S279 (WHATWG HTML Living Standard, §13.1.6 Comments — https://html.spec.whatwg.org/multipage/syntax.html, anchor §13.1.6, re-opened live 2026-11-03) and S280 (CommonMark 0.31.2, §6.6 Raw HTML — https://spec.commonmark.org/0.31.2/, anchor §6.6, re-opened live 2026-11-03); captures census/round-57/sources/s279-whatwg-html-syntax.html (89196 bytes, sha256 ad4bdaca53226b0c6f5962786f309fea3ca4e59bec86b026cb3fc5d641b25ff1) and census/round-57/sources/s280-commonmark-0.31.2.html (514698 bytes, sha256 c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d), each byte-identical to this session's live re-fetch; S281 (MDN — Using HTML comments, tier B — https://developer.mozilla.org/en-US/docs/Web/HTML/Comments, served /en-US/docs/Web/HTML/Guides/Comments) was re-opened the same way and is carried only as the rejected secondary restatement
verified-at: 2026-11-03 — three sources re-fetched this session with `curl -sSL` (HTTP 200 each; all three byte-identical to the committed captures, S281 included, 175824 bytes, sha256 2bca88c20599aa7f3c1bc12dc4d041f156b526ed7dee68c0b08b9fc1ca60d9ba); the four located quotes re-checked as verbatim substrings of the tag-stripped, entity-decoded, whitespace-collapsed page using a normalizer written for this draft (11, 19, 24 and 25 words — the committed record's "17" for S279 quote-2 does not reproduce as a whitespace-token count, see .ufo/waves/round-57/w1/S57scribe01/quotes.txt); the four comment shapes independently rendered with markdown-it-py 4.2.0 (`commonmark` preset) — visible filing tokens 0, 0, 2, 2 against a 2-token control (receipt .ufo/waves/round-57/w1/S57scribe01/render-probe.txt); the counter verdicts read from the frozen dry-run matrices census/round-57/records/matrix-dryrun/c1-matrix-v{5,6}.tsv and the frozen expected file census/round-57/records/c1-selftest-expected.tsv, which this seat did not re-run
recheck: `curl -sSL https://spec.commonmark.org/0.31.2/ | sha256sum` must print c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d — a different hash means the pinned §6.6 text moved and the quote in census/round-57/records/source-quotes.txt must be re-located before this entry is trusted. S279 is a Living Standard, so its pinned sha256 (ad4bdaca…) identifies the bytes this entry was written against and is expected to drift: re-open §13.1.6 and re-verify the quote as a substring instead of comparing bytes
---

# Inline HTML comments hide markdown text, and the authoring rule is not the renderer's rule

A `<!--` that does not begin a line still opens an HTML comment in a markdown
renderer, and that comment runs to the first later `-->` — possibly several
lines down. Every line the span covers renders as nothing, so a correction
"filed" inside it is invisible to a reader even though the file contains it.
Two specifications are involved and they answer different questions: WHATWG
§13.1.6 says what text a *complete, well-formed* HTML comment may carry
(authoring); CommonMark §6.6 says what a *renderer* consumes (visibility). A
counter over markdown source is asked the second question, so it follows S280.
Confusing the two produced the round-56 over-acceptance: v5 opened a comment
only on a line that *begins* with `<!--` (the HTML **block** start condition,
CommonMark §4.6 type 2) and therefore missed mid-line openers, which §6.6
governs; the r56 non-author closure recorded v5's rule as
`indent <= 3 and stripped.startswith('<!--')`
(`corpus/lessons/round-56-verifier-spotcheck.md`).

## The two rules, verbatim

**S279, WHATWG HTML Living Standard §13.1.6 Comments** (11 words, verified):

> `Comments must have the following format: The string " <!-- ".`

and the restriction on the comment's text (19 words, verified; the page
continues `... nor contain the strings " <!-- ", " --> ", or " --!> ", nor end
with the string " <!- ".`):

> `the text must not start with the string " > ", nor start with the string " -> "`

This is an **authoring** grammar. Its three prohibitions constrain the text a
finished comment may contain. It says nothing about where the opener sits on a
source line, and nothing about which text a renderer paints.

**S280, CommonMark 0.31.2 §6.6 Raw HTML** (24 words, verified):

> `An HTML comment consists of <!--> , <!---> , or <!-- , a string of characters not including the string --> , and -->`

This is a **renderer** grammar. It carries strictly fewer restrictions on the
text than S279 (an embedded `<!--`, `--!>` or a leading `>` is allowed) and
exactly one structural condition: a later `-->`. It states no line-position
requirement at all, so an inline comment has the same standing whether it
starts the line or sits after prose.

**S281, MDN — Using HTML comments** (25 words, verified; rejected row):

> `This text cannot start with the string > or -> , cannot contain the strings --> or --!> , nor end with the string <!-`

It restates the authoring restriction in one sentence, says nothing about the
markdown inline grammar, and is not a doc-of-record where S279 exists. The
sentence continues `, though <! is allowed.`, which the located quote cuts
before — the allowance is real and this entry does not rely on the cut.

### Where the two disagree

The renderer's grammar accepts strictly more than the authoring grammar. A
markdown-hidden comment that WHATWG would refuse: `<!-- a --!> b -->` — the text
contains `--!>`, which S279 forbids, while §6.6 only excludes `-->`, so the
first `-->` closes it and everything inside is hidden. A visibility counter
over markdown source must therefore follow S280; following S279 would import
prohibitions the renderer does not enforce in either direction. Neither page
justifies a line-start-only opener: that is the HTML *block* start condition
(§4.6 type 2), a different production from the inline one.

## Measured visibility of the four round-57 shapes

Source lines as the frozen builder emits them
(`census/round-57/fixtures/build-fixtures.py`; `U+00A0` is an NBSP character,
not indentation; `LINE` stands for the substituted line number):

| shape | correction block, as the frozen builder emits it | renderer-visible filings | v5 (r56) | v6 (r57) |
|---|---|---|---|---|
| B4-INLINE-NBSP-OPENER | `[U+00A0]<!-- inline comment opened after an NBSP` / two `R52-CORRECTION` lines / `-->` | 0 | exit 0, `filed=2 unfiled=0` — the harm | exit 1, `CORRECTION-IN-FENCE,CORRECTION-IN-FENCE`, `unfiled=2` |
| C4-INLINE-CLOSED-COMMENT | `- prose: an inline note <!-- opens here` / two `R52-CORRECTION` lines / `and closes here -->` | 0 | exit 0, `filed=2 unfiled=0` — the harm | exit 1, `CORRECTION-IN-FENCE,CORRECTION-IN-FENCE`, `unfiled=2` |
| C6-INLINE-SAME-LINE | `- prose: a closed inline note <!-- same line --> stays inline.` / two `R52-CORRECTION` lines | 2 | exit 0 | exit 0, `filed=2` |
| F29-PROSE-COMMENT-MENTION | `- prose: a mention of the token <!-- inside a sentence opens no comment region.` / two `R52-CORRECTION` lines | 2 | exit 0 | exit 0, `filed=2` |
| control (no comment) | two `R52-CORRECTION` lines | 2 | n/a | n/a |

Evidence classes, kept separate:

- **Renderer (live, this session):** markdown-it-py 4.2.0, `MarkdownIt('commonmark')`;
  text/code tokens counted, `html_inline`/`html_block` tokens dropped — a browser
  paints no comment node. B4 and C4 emit one `html_inline` token that swallows
  both filings; C6's span closes on its own line, so the filings survive; F29
  has no closer, so the `<` is escaped and the page literally paints
  `&lt;!--` — literal text, nothing hidden.
- **Counter (frozen dry-runs, read not re-run):** `census/round-57/records/matrix-dryrun/c1-matrix-v5.tsv`
  and `c1-matrix-v6.tsv` (36 rows each) plus `census/round-57/records/c1-selftest-expected.tsv`
  rows 34–37. The exit-0 population moves 10 of 36 → 8 of 36; the only rows
  whose exit code or finding list change are B4 and C4, and the change is exit
  0 → 1 with `CORRECTION-IN-FENCE` emitted twice (once per hidden filing).

## What the counter does with this (read from the frozen v6 bytes)

`census/round-57/c1-counter.py` keeps three hidden classes and labels them in
the finding detail (`hidden_by=fence|block|inline`, emitted at the
`CORRECTION-IN-FENCE` site; every carry-over finding id is unchanged): `fence`
for fenced code, `block` for the line-start HTML block rule, `inline` for a
`<!--` anywhere on a visible line, closed at the first `-->` after it (not
necessarily on the same line). `<!-->` and `<!--->` close on their own line; a
`<!--` with no closer hides nothing, which is why F29 stays visible. The
selftest compares the full ordered finding list against the frozen expected
file rather than only the first finding, so a secondary emission cannot
survive.

## Named limits

1. **Whole-line granularity.** A line touched by any part of a span is marked
   hidden as a whole. A filing placed on the same source line *after* a closing
   `-->` is refused although a renderer paints it.
2. **Inline code spans are not modelled.** In CommonMark a `<!--` inside a
   backtick code span is literal text, not raw HTML; the line scanner still
   treats it as an opener and hides the span to the next `-->` (over-hide).
   Demonstrated on a scratch fixture by the L1's own v6 run
   (`census/round-57/records/probe-code-span-overhide.txt`: two
   `CORRECTION-IN-FENCE` findings with `hidden_by=inline`, `EXIT=1`, against a
   render that paints both filings).
3. **Four-space indentation is not scanned.** Lines with four or more leading
   spaces are skipped, so an indented `<!--` that is a lazy paragraph
   continuation — inline raw HTML in a renderer — opens nothing here
   (under-hide).
4. **The tail of a closer line is not re-scanned.** After an inline span ends,
   scanning resumes on the following line, so a second opener later on the
   closer line is missed (under-hide); the same tail is also marked hidden
   (limit 1). Demonstrated by the L1's second probe
   (`census/round-57/records/probe-second-opener-harm.txt`: `filed=2 unfiled=0`,
   `EXIT=0`, against `visible=0` in a markdown-it render).
5. **A line-start `<!-->` opens a block to end of document.** The inline class
   special-cases `<!-->` and `<!--->`, but the block class does not: for
   `<!--> …` at line start, `ln[4:]` contains no `-->`, so the block stays open
   through the last line (over-hide). Read from the frozen bytes; the round
   lesson records the same asymmetry.
6. **Only the comment production is modelled.** `<?`, `<!DOCTYPE` and
   `<![CDATA[` raw HTML are outside the instrument's grammar.
7. **First closer wins, no nesting** — this agrees with §6.6, so it is a
   property, not a defect.
8. **The instrument grades markdown source, not HTML validity.** A
   WHATWG-invalid comment with a reachable closer is still hidden here; a
   future instrument that grades HTML *authoring* would have to follow S279
   instead.
9. **Evidence limits of this entry.** The frozen expected file and the frozen
   matrices record finding ids, not detail strings: no B4/C4 receipt in the
   freeze commit exhibits a `hidden_by=inline` line, and the label is read from
   the frozen counter bytes (the later probe receipts above do show the
   rendered form, for other fixtures). The render receipt reproduces the
   builder's four correction blocks, not a full fixture repository. The
   matrices are pre-freeze dry-runs; this seat did not re-run the counters, and
   no claim receipt is asserted here.

## What this entry does not claim

No claim receipt and no verdict on C1: whether the amendment passes is judged
by the wave's closure against the frozen predicate, not by this entry. Nothing
here asserts that the counter is CommonMark-correct — it is a line-level
approximation whose divergences are the named limits above. The registry rows
S279 and S280 ground the two grammars; S281 is recorded as rejected and grounds
nothing.
