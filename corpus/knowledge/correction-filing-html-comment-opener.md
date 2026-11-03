source: S277 — CommonMark spec 0.31.2, §4.6 HTML blocks (https://spec.commonmark.org/0.31.2/; located quotes "The block begins with a line that meets a start condition (after up to three optional spaces of indentation)." and "Start condition: line begins with the string <!--"; capture census/round-56/sources/s277-commonmark-0.31.2.html, sha256 c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d)
verified-at: 2026-11-03 — S277 re-opened live this round (curl -sSL HTTP 200, no redirect, 514698 bytes, sha256 equal to the capture); both located quotes re-checked as verbatim substrings of the tag-stripped capture (see corpus/lessons/round-56.md ## Gate)
recheck: python3 -B -c "import re,html;t=re.sub(r'<[^>]+>',' ',open('census/round-56/sources/s277-commonmark-0.31.2.html',encoding='utf-8').read());t=re.sub(r'\s+',' ',html.unescape(t));print('Start condition: line begins with the string <!--' in t, 'after up to three optional spaces of indentation' in t)"  (expected: True True); re-run the round-56 C1 counter over committed fixtures with run-matrix.sh

# The HTML comment opener in the correction-filing counter

## What this entry is

The correction-filing counter (`census/round-56/c1-counter.py`, v5) hides lines that are
not filings: fenced code, and HTML comment regions. Its comment rule decides which lines
open a region. This entry records the CommonMark 0.31.2 rule the v5 rule follows and the
two over-hide and under-hide failures the rule used to produce.

## The rule

CommonMark §4.6 says an HTML block begins with a line that meets a start condition, "after
up to three optional spaces of indentation". For type 2 (comments) the start condition is
"line begins with the string `<!--`". So a comment region opens only on a line whose
non-space text begins with `<!--`, indented by at most three spaces.

Two consequences for the counter:

- A four-space-indented `<!--` is indented code, not a comment. v4 treated it as a comment
  opener and hid a real overstatement behind it (round-55 sentinel S55-S2, a v3→v4
  regression). v5 refuses that hide: the pair scan sees the overstatement and refuses it
  (fixture F26).
- A prose sentence that mentions the token `<!--` mid-line is not a comment. v4 opened a
  region at that mention and hid every later line, so an honest correction filed after the
  sentence read as "in a fence" (a false positive; fixture F29). The real `SCORECARD.md`
  in this lane carries such a mention (round-55 R55-CORRECTION line), so the defect was
  live, not only a fixture.

## What is not claimed

The rule is line-level. A region still runs to the first line that contains `-->`, and a
mid-line opener that also closes on the same line hides only its own line. CommonMark's full
HTML block types 1, 3, 4, 5, 6 and 7 are not modelled: the counter only reads type 2.

## Pointers

- Fixtures: census/round-56/fixtures/build-fixtures.py F26-INDENT4-COMMENT-OPENER and F29-PROSE-COMMENT-MENTION
- Dry-run receipts: census/round-56/records/matrix-dryrun/c1-matrix-v4.tsv and c1-matrix-v5.tsv
- Frozen predicate: census/round-56/preregistration.txt, C1 T1 and T4

## Round-56 source-review correction (append-only)

S56scribe01 verified the source and recheck command, but found the sentence at
lines 35–36 wrong: a genuine mid-line mention hides **nothing** under v5.
Only a line-begin self-closing comment hides its own line. The original sentence
remains above as the corrected record. “Non-space text” means stripping at most
three ASCII spaces, not arbitrary whitespace. The “four spaces is code” description
requires the surrounding block context; the sourced negative rule here is only
that four leading spaces do not satisfy this HTML-block start condition.
Evidence: `census/round-56/wave/w1/S56scribe01/S56scribe01-report.md`.
