# S57scribe01 (souji r57) — SOURCES registry rows, draft for Main to integrate

Eleven columns, matching the `## Registry` header of `corpus/SOURCES.md`:
`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.
No cell contains a pipe character. The located quote in each `teaches` cell is
wrapped in a code span on purpose, and the reason is measured, not assumed
(`rows-render-check.txt`; markdown-it-py 4.2.0 with the table rule): in a
rendered table an inline HTML comment token is consumed as a comment node and
leaves no visible text. The S280 row currently in the working tree renders its
located quote as `An HTML comment consists of  ,  , or  , and -->` — all three
comment tokens gone (190 visible characters against 390 in this draft). A cell
that carries a `<!--` but no `-->` is escaped instead and renders literally, so
the failure needs both in one cell. Reading the row as text (the census parser,
grep) is unaffected either way.

```markdown
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S279 | WHATWG HTML Living Standard — 13.1.6 Comments — https://html.spec.whatwg.org/multipage/syntax.html | spec | A | HTML comment authoring grammar: the restrictions a complete comment's TEXT must satisfy (an authoring rule, not a visibility rule) | §13.1.6 Comments; Living Standard served 2026-11-03, curl -sSL HTTP 200 (no redirect), 89196 bytes, sha256 ad4bdaca53226b0c6f5962786f309fea3ca4e59bec86b026cb3fc5d641b25ff1 (capture census/round-57/sources/s279-whatwg-html-syntax.html; located quotes census/round-57/records/source-quotes.txt, 11 and 19 words) | `Comments must have the following format: The string " <!-- ".` (located quote, 11 words) — it constrains a complete comment's text, so it cannot decide where a markdown renderer opens a comment or which lines stay hidden; the line-start-only opener v5 applied is the CommonMark HTML-block start condition (§4.6), which this page does not state | mined | 2026-11-03 | 180d | corpus/knowledge/inline-html-comment-visibility-r57.md |
| S280 | CommonMark spec 0.31.2 — 6.6 Raw HTML — https://spec.commonmark.org/0.31.2/ | spec | A | inline raw-HTML comment grammar a markdown renderer applies (the grammar the C1 v6 inline hidden class implements) | §6.6 Raw HTML; page states "Version 0.31.2 (2024-01-28)"; served 2026-11-03, curl -sSL HTTP 200 (no redirect), 514698 bytes, sha256 c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d (capture census/round-57/sources/s280-commonmark-0.31.2.html; located quote census/round-57/records/source-quotes.txt, 24 words) | `An HTML comment consists of <!--> , <!---> , or <!-- , a string of characters not including the string --> , and -->` (located quote, 24 words) — an inline comment needs only a later closer and no line position, so a mid-line or NBSP-prefixed opener hides its span (the r56 B4/C4 over-acceptance); the `<!-->` and `<!--->` forms close on their own line, and a `<!--` with no closer is literal text | mined | 2026-11-03 | on-release | corpus/knowledge/inline-html-comment-visibility-r57.md |
| S281 | MDN — Using HTML comments — https://developer.mozilla.org/en-US/docs/Web/HTML/Comments | docs | B | secondary restatement of the HTML comment authoring restriction; no statement about markdown rendering | body section "Using HTML comments"; effective URL /en-US/docs/Web/HTML/Guides/Comments after a redirect; served 2026-11-03, curl -sSL HTTP 200, 175824 bytes, sha256 2bca88c20599aa7f3c1bc12dc4d041f156b526ed7dee68c0b08b9fc1ca60d9ba (capture census/round-57/sources/s281-mdn-comments.html; located quote census/round-57/records/source-quotes.txt, 25 words) | REJECTED: it restates only the HTML authoring restriction (in one sentence) and is silent on the markdown inline grammar the C1 v6 counter reads, while the A-tier S279 already holds that rule; nothing in the page bounds where a renderer opens or closes a comment; flip: a markdown-renderer statement about inline comment extent, or a scope change to raw HTML authoring where MDN would be the doc-of-record; the single sentence it adds is quoted in the entry as the rejected sample | rejected | 2026-11-03 | 180d | corpus/knowledge/inline-html-comment-visibility-r57.md |
```

Notes for the integrating commit:

- S280's `kind` is `spec` per the seat assignment; the row currently in the
  working tree says `docs` and its URL duplicates S277's (different scope → a
  W04 warning, not a finding).
- S279/S280 `status=mined` because the entry cites both; S281 `status=rejected`
  with a long `teaches` cell so W02 (thin reject) does not fire.
- The word counts in the `anchor` cells are re-derived this session
  (`.ufo/waves/round-57/w1/S57scribe01/quotes.txt`): 11 and 19 for S279, 24 for
  S280, 25 for S281. The committed record's "17" for S279 quote-2 does not
  reproduce as a whitespace-token count.
