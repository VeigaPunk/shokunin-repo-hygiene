# A raw byte and the character that decodes to it need different spellings

source: S353 (Unicode UAX #14 § NL: Next Line — U+0085's line-break class); S351 (Python `codecs` `surrogateescape`); S348 (Python `str.splitlines` boundaries);
scored against tools/souji-record-agreement.py and tests/fixtures/r90-k4-flagfail.py at round 90.
verified-at: python 3.14.8, git 2.56.0-1, 2026-11-08, against the tool bytes of commit 4cb3a06f (capture census/round-90/srcs/tr14.html sha256 296df533…acc7c0,
226166 bytes; the quote verified once, 18 words).
recheck: 365d, or on a Unicode version bump (the NL class is stable; the escape set is the lane's own).

Round 90 (C2, the K4 FLAGFAIL detail). Ground: S353 (the class), S348 (the boundaries), S351 (the decode).

## The pair that collided, and the rule

A delegated child's stderr arrives as BYTES. `_decode_record` decodes with `surrogateescape` (S351), so an invalid byte such as 0x85 becomes the lone surrogate
U+DC85 and `_escape_text` printed it as `\x85`. A stderr carrying the CHARACTER U+0085 instead encodes it as the two valid UTF-8 bytes `\xc2\x85`, decodes to
the real character, and the r89 rule's `o == 0x85` branch printed it `\x85` too: two materially different failures shared one cell. The character now takes
`\u0085`: it is a character, not a byte spelling, and its line-break class is NL — "The NL class acts like BK in all respects (there is a mandatory break after
any NEL character)." (S353, 18 words) — so `str.splitlines()` breaks on it too (S348), and a one-line cell must escape it without borrowing the byte's spelling.

- Raw bytes that are not valid UTF-8: `\xNN` with the original byte value (via `surrogateescape`, S351).
- Characters whose code point is a documented `str.splitlines()` boundary above 0x7F — U+0085, U+2028, U+2029: `\uNNNN` (S348, S353).
- A literal backslash sequence keeps its backslash doubled (r87 rule), so no spelling is ambiguous with a character's own name.

## Boundary

One lane tool's spelling rule for one cell (`_escape_text`, the delegated-stderr detail). No universal injectivity is claimed: the pair is measured
(KFF9/KFF10), a stderr differing only inside the elided middle still renders identically, and `_escape_record` (path bytes) is unchanged and byte-based, so a
path's U+0085 bytes already print `\xc2\x85`. The dead escape-first helper `_one_line` was deleted in the same round (zero callers).

## Gate

- URL: https://www.unicode.org/reports/tr14/ — opened 2026-11-08 (HTTP 200, 226166 bytes, sha256 `296df533…acc7c0`; Version "Unicode 18.0.0", Revision
  "tr14-57.html", Date 2026-09-01).
- Located quote (≤25 words): "The NL class acts like BK in all respects (there is a mandatory break after any NEL character)." — § NL: Next Line, tag-stripped
  offset 82360, occurrence count 1; the class-table row `0085 / NEXT LINE (NEL)` sits at capture lines 2874-2875.
- Admit/reject: admit (tier A, docs, status `mined`). Reject sample: the Unicode Newline Guidelines (UAX #13) — it names no decision this cell needs, so it
  stays a lead; flip if the lane must decide which newline CONVENTION a producer followed.
