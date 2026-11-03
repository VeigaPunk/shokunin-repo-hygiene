# S56scribe01 — scoped findings (round 56, w1)

VERDICT: VERIFIED

Full report: `.ufo/waves/round-56/w1/S56scribe01/S56scribe01-report.md`
Receipts: `.ufo/waves/round-56/w1/S56scribe01/S56scribe01-receipts.txt`
Revision: cce21b555a617cadda782613ec1e9d3a0c12ac83 (base fafe371694fea41c5d23f63083865d5ccf3f1d36).

## What was checked

1. **Live source** — `curl -sSL https://spec.commonmark.org/0.31.2/` twice: HTTP 200, `num_redirects=0`,
   url_effective equal to the request URL, 514698 bytes, sha256
   `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`; `cmp` against the committed capture
   `census/round-56/sources/s277-commonmark-0.31.2.html` (extracted with `git show` at cce21b55) is
   byte-identical. Page states "Version 0.31.2 (2024-01-28)".
2. **Located quotes** — in the tag-stripped, entity-decoded, whitespace-collapsed live text both are verbatim
   substrings: Q1 19 words (Gate states 19), Q2 8 words (Gate states 8).
3. **Gate block** in `corpus/lessons/round-56.md` at cce21b55 states the access date (2026-11-03), URL, status
   (200, no redirect), byte count, digest and capture path correctly.
4. **Knowledge entry** `corpus/knowledge/correction-filing-html-comment-opener.md`: `source:` cites S277 with
   URL and anchor §4.6 HTML blocks (live page has `id="html-blocks"`, heading `4.6 HTML blocks`);
   `verified-at:` and `recheck:` present; the recheck command runs verbatim from the lane root → `True True`,
   rc 0.
5. **Registry row** S277 in `corpus/SOURCES.md`: character diff base→freeze is a single insert,
   `, corpus/knowledge/correction-filing-html-comment-opener.md` at the end of the `used-by` cell. id S277,
   kind `docs`, tier `A`, status `mined` unchanged; `used-by` now lists both knowledge entries.

## Claims in the entry not supported by the two located quotes

- "A four-space-indented `<!--` **is indented code**" — the negative (no comment region) follows from Q1; the
  positive classification is §4.4, absent from the located quotes.
- "A region still runs to the first line that contains `-->`" — end condition is on the page but not in either
  located quote.
- "type 2" / "types 1, 3, 4, 5, 6 and 7" — numbering is page context, not in the quotes.
- "non-space text begins with `<!--`" — looser than the spec's "line begins with the string `<!--`" after up to
  three optional spaces; admits tab-indented openers the frozen counter rejects. The task's example contrast
  ("at most three" vs "up to three") is **not** a discrepancy: the bounds are identical.
- "a mid-line opener that also closes on the same line hides only its own line" — for a genuine mid-line
  mention v5 hides nothing; the sentence is true only for a line-begin self-closing comment (counter docstring
  says "a one-line comment hides only its own line"). Wording defect, routed for r57.

No source-level discrepancy. No lane file edited; no git/jj mutation; no counters or matrices run by this seat.
Nothing installed. Scratch deleted.

EXIT=0
