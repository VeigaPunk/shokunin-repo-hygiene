# S88Scribe — DRAFT: the `## Gate` row for S348 (registry schema, newest corpus/SOURCES.md rows)

Seat draft only. NOT a committed file. The L1 (SoujiR88) is the integration owner.
Verified against the lane at the tip `72edae4045cfa2b8c74f176bf690d7583bcceecb`
(`git rev-parse refs/heads/master`), where S348 already exists as corpus/SOURCES.md line 309.
(The L1 committed `72edae40` — a C2 docstring repair — DURING this seat's run; all checks
below were re-measured at that tip and every finding still holds. The one thing that moved
is the tool's own sha256: `c0604b4a…` -> `3e1fc030…`. See F7 in the report.)
This draft is the row the L1 should file; the deltas against the landed row are listed after it.

## DRAFT A — the SOURCES.md registry row (pipe-table form, 11 cells)

Filed as a new row after S349 (i.e. becomes S350), or — if the L1 prefers to keep the id —
as a correction to S348's `anchor`/`teaches` cells. See "DELTAS" below for which.

| S348 | Python 3.14 `str.splitlines` line boundaries — https://docs.python.org/3.14/builtins/stdtypes.html#str.splitlines (request ran /3.14/library/stdtypes.html, 301 to builtins/stdtypes.html; HTTP 200, 774910 bytes, sha256 5abdd8b9ceeda2c3e94d8f95e32d9853d6f35d35844514727aa440cac98eda42, capture census/round-88/srcs/str-splitlines.html, opened 2026-11-08) | docs | A | which byte sequences a Python `str.splitlines()` reader treats as line boundaries (scope: the boundary list under `str.splitlines`; `keepends` behaviour and the other `str` methods are out of scope) | § str.splitlines, anchor `#str.splitlines` in the capture (rendered quote, capture lines 2806-2807): "This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines." (18 words, counted by the pasted command in `quote-verification-receipt.txt`) | the boundary list adds VT, FF, FS/GS/RS, NEL and LS/PS to LF/CR/CRLF, so a diagnostic cell carrying any of them is two lines to a `splitlines` reader even when no LF byte is present; escaping must cover the whole list, not only LF | mined | 2026-11-08 | 90d | corpus/knowledge/one-escaped-diagnostic-line.md |

## Cell-by-cell audit of the landed row (corpus/SOURCES.md:309)

| cell | landed value | verdict |
|---|---|---|
| id | S348 | ok — continues the registry after S347 |
| source (title+URL) | Python 3.14 `str.splitlines` line boundaries — https://docs.python.org/3.14/builtins/stdtypes.html#str.splitlines | ok — the 301 path is disclosed; live re-fetch reproduces the capture byte-for-byte (HTTP 200, 774910 bytes, sha256 5abdd8b9…eda42) |
| kind | `docs` | ok |
| tier | `A` | ok — an official language reference, the same tier S278 holds for the same page family |
| scope | "which byte sequences a Python `str.splitlines()` reader treats as line boundaries (scope: the boundary list under `str.splitlines`; `keepends` behaviour and the other `str` methods are out of scope)" | ok — one named scope, exclusions named, no widening |
| anchor | "§ str.splitlines, anchor `#str.splitlines` in the capture (rendered quote): "…"" (18 words) | **ok on the quote; the word count is right.** The anchor `#str.splitlines` occurs exactly once in the capture (line 2801). The quote's own paragraph is capture lines 2806-2807. Recommend adding "capture lines 2806-2807" so a reader can locate it without a search. |
| teaches | "the boundary list adds VT, FF, FS/GS/RS, NEL and LS/PS to LF/CR/CRLF, so a diagnostic cell carrying any of them is two lines to a `splitlines` reader even when no LF byte is present; escaping must cover the whole list, not only LF" | **F3 — the quote does not carry this.** The filed quote names NO boundary beyond universal newlines; the six extra boundaries live in the capture's TABLE (lines 2808-2849), not in the quoted sentence. The `teaches` cell is true of the page, but it is not what the row's own quote locates. |
| status | `mined` | ok — the quote is verified present in the capture (True 18) |
| opened | 2026-11-08 | ok — matches the capture's mtime and the live re-fetch date |
| recheck | 90d | ok — the boundary list has been stable since Python 3.2 (the capture's own "Changed in version 3.2" note) |
| used-by | corpus/knowledge/one-escaped-diagnostic-line.md | ok — that entry exists (landed in the same commit e60ea25f) and cites S348 in its `source:` line and its Gate |

## DELTAS — what the L1 must decide

**D1 (F3, the substantive one). `teaches` vs. the quote.** The landed row's `teaches` cell asserts a
boundary LIST (VT, FF, FS/GS/RS, NEL, LS/PS) while its quote says only "a superset of universal
newlines". Two ways to close it; both are one-cell edits, and the lane's own precedent (r40
wave-2 S255-S257, r50 M-row) is to fix the row, not the quote:

  (a) widen the quote to the 25-word table quote that DOES carry the boundaries —
      `\v or \x0b Line Tabulation \f or \x0c Form Feed \x1c File Separator \x1d Group Separator
      \x1e Record Separator \x85 Next Line (C1 Control Code)` (verified `True 25` against the r88
      capture; it is the r55 S278 receipt's own third quote, so it is the lane's model). At 25 words
      it sits exactly on the ≤25 bound, and it drops the paragraph sentence.
  (b) keep the 18-word quote and narrow `teaches` to what it carries — "the boundary set is a
      superset of universal newlines, so a `splitlines` reader breaks on more than LF; the full
      list is in the capture's table under the anchor" — and point the claim at the table.

  My recommendation: (a). The claim's load-bearing fact is the six extra boundaries, and (b)
  leaves the `teaches` cell asserting something the row does not locate. If the L1 takes (a), the
  `anchor` cell should also carry the table's capture lines (2825-2840) so the location is exact.

**D2 (F1, the wording one). `corpus/SOURCES.md:316`.** The Round-88 provenance paragraph says the
quote "was checked byte-for-byte against the capture". For an HTML capture that phrase is false:
the quote is NOT a byte-substring of `str-splitlines.html` (verified `False`; the sentence spans
capture lines 2806/2807 with anchor markup inline). The verified statement is "checked against the
capture's rendered text, tags stripped and whitespace collapsed (the r55 recipe), `True 18`". The
lane's own r50 mistake row is this exact class of overclaim. Note this is in `corpus/SOURCES.md`,
not in the row's own cells — the row says "(rendered quote)" and is honest.

**D3 (F2, the arithmetic one). S349's word count.** `corpus/SOURCES.md:310` and
`corpus/lessons/round-88.md` both say the S349 quote is "(16 words)". The lane's own count command
gives **15** (`True 15`). This is the r49 S271 erratum class exactly ("17 words" for a 16-word
quote) and the r45 Gate erratum before it. S349 is a `rejected` row, so no knowledge rests on it,
but the number is in a filed cell and in the lesson. Under either tokenizer it is wrong:
`len(s.split())` = 15, `len(re.findall(r'\w+', s))` = 16 — the filed 16 is a `\w+` count, which is
not the lane's convention (the r49 erratum's command is `len(s.split())`).

**D4 (a scope check I could not close). S278 vs S348.** S278 (r55) already holds the same page
family, the same anchor (`#str.splitlines`), the same 18-word sentence (S278's copy lacks the
trailing full stop; S348's is that sentence plus `.`), and the same used-by entry
(`corpus/knowledge/splitlines-line-model.md` lists the identical boundary set). S348's scope is
narrower — "which byte sequences a `str.splitlines()` reader treats as line boundaries" — and its
used-by is a different entry, so it is not a bare duplicate. But the census emits NO W04 for either
id (S348 and S278 both have zero W04 lines in `census/round-88/records/sources-census-after.txt`;
the only stdtypes-family warnings are S266/S267 at `docs.python.org/3/builtins/stdtypes.html`), so
the lane's own duplicate-URL detector is blind to this pair because the version path differs
(`/3.12/library/` vs `/3.14/builtins/`). The Round-88 Gate's own duplicate-URL note names S061
and S105 and does NOT mention S278. The L1 should decide whether S348 is a scope-narrowing row on
S278 (the r40 wave-2 pattern: a new row names the older row it narrows) or an independent admit.

## What I did NOT find

- The claim's wording — "the boundaries a `str.splitlines()` reader breaks on, S348" — is not
  widened by anything in this round's artifacts: the tool's `_escape_text` demonstrably escapes
  every one of the eleven documented boundaries to a single line (measured: LF, CR, CRLF, VT, FF,
  FS, GS, RS, NEL, LS, PS each yield exactly one `splitlines()` element).
- The live re-fetch reproduces the filed capture byte-for-byte, so the capture's integrity is not
  in question; only the phrase used to describe the check is.
