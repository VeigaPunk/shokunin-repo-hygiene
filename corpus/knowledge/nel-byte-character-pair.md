# A raw byte and the character it decodes to need different spellings

source: S353 (Unicode UAX #14, the NL class for U+0085); S348 (Python `str.splitlines` line boundaries); S351
(Python `codecs` `surrogateescape`); scored against tools/souji-record-agreement.py and
tests/fixtures/r90-k4-flagfail.py at round 90.
verified-at: python 3.14.8, git 2.56.0-1, 2026-11-08, against the tool bytes of commit 4cb3a06f (capture
census/round-90/srcs/tr14.html sha256 296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0, 226166
bytes; the quote verified once, with no offset quoted because the lane's r63 stripper and the drop-tags normalizer
place the same sentence at different offsets; the section and capture lines are the locator).
recheck: 365d, or on a Unicode version bump (the NL class is stable; the escape set is the lane's own).

Round 90 (C2, the K4 FLAGFAIL detail). Ground: S353 (the character's line-break class), S348 (the boundary set),
S351 (the decode), the r89 entry `decode-escape-order.md` (the raw-first bound).

## The pair that collided

A delegated child's stderr arrives as BYTES. `_decode_record` decodes with `surrogateescape` (S351), so an invalid
byte such as 0x85 becomes the lone surrogate U+DC85, and `_escape_text` prints it as `\x85` with its byte value. A
stderr that carries the CHARACTER U+0085 instead encodes it as the two valid UTF-8 bytes `\xc2\x85`, decodes to the
real character, and the r89 rule's `o == 0x85` branch also printed it `\x85`. Two materially different failures
therefore shared one cell, and the record could not say which one happened.

## Why the character must be spelled differently

U+0085 is not a byte spelling; it is a character, and its line-break class is NL: "The NL class acts like BK in all
respects (there is a mandatory break after any NEL character)." (S353, 18 words). `str.splitlines()` treats it as a
boundary too (S348). So a one-line record cell must escape it, and it must not borrow the raw-byte spelling: the
byte is `\x85`, the character is `\u0085`. The same branch already spells U+2028 and U+2029 as `\uNNNN` (S87Sentinel
F4); U+0085 joins them.

## The rule

- Raw bytes that are not valid UTF-8: `\xNN` with the original byte value (via `surrogateescape`, S351).
- Characters whose code point is a documented `str.splitlines()` boundary above 0x7F — U+0085, U+2028, U+2029:
  `\uNNNN` (S348, S353).
- A literal backslash sequence keeps its backslash doubled (r87 rule), so no spelling is ambiguous with a
  character's own name.

## Boundary

This entry records one lane tool's spelling rule for one cell (`_escape_text`, the delegated-stderr detail). It does
not claim universal injectivity of the pipeline: the pair is measured (KFF9/KFF10), a stderr that differs from
another only inside the elided middle still renders identically, and `_escape_record` (path bytes) is unchanged and
byte-based, so a path's U+0085 bytes already print `\xc2\x85`. The dead escape-first helper `_one_line` was deleted
in the same round (zero callers).

## Gate

- URL: https://www.unicode.org/reports/tr14/ — opened 2026-11-08 (HTTP 200, 226166 bytes, sha256
  `296df533…acc7c0`; the page names Version "Unicode 18.0.0", Revision "tr14-57.html", Date 2026-09-01).
- Located quote (≤25 words): "The NL class acts like BK in all respects (there is a mandatory break after any NEL
  character)." — § NL: Next Line, occurrence count 1; the class-table row `0085 / NEXT LINE (NEL)` sits at capture
  lines 2873-2876, the quoted paragraph at 2878-2879 (no offset is quoted: the lane's r63 stripper and the
  drop-tags normalizer place the same sentence at different offsets, S90Scribe § "the stripper rule");
  `LineBreak.txt` line `0085           ; NL # Cc         <control-0085>` agrees.
- Admit/reject: admit (tier A, docs, status `mined`). Reject sample for the round: UAX #13, Unicode Newline
  Guidelines — https://www.unicode.org/reports/tr13/ opened 2026-11-08 (HTTP 200, 6348 bytes, sha256
  `bfa7f97b…a667c78`, capture census/round-90/srcs/tr13.html): the URL now serves a supersession notice, not the
  guideline — "The material formerly covered by UAX #13: Unicode Newline Guidelines has been incorporated into the
  Core Specification of the Unicode Standard, starting with Version 4.0" (25 words). REJECT: no actionable content
  for this cell beyond what S353's NL class and S348's boundary list already carry; flip if this lane ever has to
  decide which newline CONVENTION a producer followed, and then open the Core Specification §5.8 at its versioned
  URL rather than this stub. The archived guideline it points at
  (https://www.unicode.org/reports/tr13/tr13-9.html, HTTP 200, 21897 bytes, sha256
  `6f38841a…70333a`, opened 2026-11-08 by S90ScoutSources) confirms the reject: its text says to *treat* CR, LF,
  CRLF and NEL the same on input, the opposite of the distinction this cell needs.
