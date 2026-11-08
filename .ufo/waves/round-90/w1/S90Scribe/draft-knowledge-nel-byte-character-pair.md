# Draft — corpus/knowledge/nel-byte-character-pair.md (souji r90, seat S90Scribe)

Target path in the lane: `corpus/knowledge/nel-byte-character-pair.md`. **The L1 has landed an entry at that path
(66 lines, untracked); this draft is the <=35-line version the brief bounds** — see "Status vs the L1's landed
entry" below before using it. Schema follows the r89 entry `corpus/knowledge/decode-escape-order.md`.

**The entry block below is exactly 35 lines** (`wc -l` on the extracted block). Long lines are deliberate: the
brief's bound is on LINES, and the lane's own entries wrap at ~116 columns, so a 35-line entry at the lane's wrap
width cannot carry this much content. **If the L1 prefers the lane's ~116-column wrap, take the landed 66-line entry
instead.**

## The entry (paste-ready)

````markdown
# A raw byte and the character that decodes to it need different spellings

source: S353 (Unicode UAX #14 § NL: Next Line — U+0085's line-break class); S351 (Python `codecs` `surrogateescape`); S348 (Python `str.splitlines` boundaries);
scored against tools/souji-record-agreement.py and tests/fixtures/r90-k4-flagfail.py at round 90.
verified-at: python 3.14.8, git 2.56.0-1, 2026-11-08, against the tool bytes of commit 4cb3a06f (capture census/round-90/srcs/tr14.html sha256 296df533…acc7c0, 226166 bytes; the quote verified once). 226166 bytes; the quote verified once, 18 words).
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
````

## Status vs the L1's landed entry

The L1 landed `corpus/knowledge/nel-byte-character-pair.md` (66 lines, untracked) while this seat was drafting. The
landed entry carries two things this draft does not: the `LineBreak.txt` corroboration inside the Gate bullet, and
the S87Sentinel F4 citation for the U+2028/U+2029 precedent. **Recommendation: keep the landed entry** — it is the
L1's own file and it is richer; treat the <=35-line bound as the brief's guidance for a NEW draft rather than a hard
gate on the L1's richer entry. This 35-line version is on file as the fallback if the bound must be honoured
verbatim.

**One thing NOT to carry over from this draft: the offset 82360.** It appears twice here (the `verified-at:` line
and the Gate bullet). The offset is ambiguous — it depends on both the stripper rule and whether the offset is a
character or a byte offset (see `draft-sources-row-S353.md` § "How the stripper rule was pinned") — and the L1's
landed S353 row resolves this by quoting **no offset** at all, keeping the section, the capture lines, the
occurrence count and the word count. **The landed entry's no-offset form is the safer one; do not paste this
draft's offset mentions over it.**

## Facts each claim rests on (re-measured this seat, committed bytes)

| claim | how it was measured | result |
|---|---|---|
| the capture's digest and size | `sha256sum census/round-90/srcs/tr14.html`; `stat -c '%s bytes'` | `296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0`, 226166 bytes |
| the quote is in the capture, once, 18 words | `python3 -B .ufo/waves/round-90/w1/S90Scribe/verify_quote.py` (run from the lane root) | `quote_whitespace_tolerant_match: True`, `occurrence_count: 1`, `words: 18`, `tag_stripped_char_offset: 82360` |
| the class-table row's capture lines | `awk 'NR>=2870 && NR<=2881 {printf "%d: %s\n", NR, $0}' census/round-90/srcs/tr14.html` | 2870 = the `NL: Next Line (Non-tailorable)` heading; 2874 = `0085`; 2875 = `NEXT LINE (NEL)`; 2878-2879 = the quoted sentence |
| the LineBreak data line agrees | `grep -n "^0085" census/round-90/srcs/LineBreak.txt` | line 95: `0085           ; NL # Cc         <control-0085>` |
| the byte path and the character path used to collide | `census/round-90/controls/c2-before-tool.py` (the r89 bytes), `_escape_text`: `elif o < 0x20 or o == 0x7F or o == 0x85: out.append("\\x%02x" % o)` | the r89 rule maps BOTH the character U+0085 and (via the surrogate arm) the raw byte 0x85 to `\x85` |
| the filed tool now separates them | `tools/souji-record-agreement.py` sha256 `d095b52f…8561`, `_escape_text`: `elif o in (0x85, 0x2028, 0x2029): … out.append("\\u%04x" % o)` and the surrogate arm `0xDC80 <= o <= 0xDCFF -> "\\x%02x" % (o - 0xDC00)` | the character takes `\u0085`; the byte keeps `\x85` |
| the pair is MEASURED, not asserted | `python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-90/controls/c2-before-tool.py --work <empty>` | `SUMMARY cases=12 tool_pass=12 before_pass=10`, EXIT 0 (KFF9/KFF10 `tool=pass before=fail`; the fixture's pair check requires the two details to be different cells) |
| `_one_line` is gone | `grep -c 'def _one_line(' tools/souji-record-agreement.py` -> 0; `grep -n "_one_line" tools/souji-record-agreement.py` -> only `_one_line_bytes` (the live helper) and a docstring naming the deleted one | dead code deleted, no caller remains |

**The one qualification this seat must carry:** per the L1's landed `plans/round-90.md` A1, the fixture's substring
counts do **NOT** certify the word "injective" on their own (a mutant that doubles the U+0085 branch's backslash
passes the fixture 12/12 — S90Sentinel H1). The injectivity evidence is the independent direct comparison
(`_escape_text("\u0085")` = `\u0085` vs `_escape_text("\udc85")` = `\x85`), which is why the landed Q165
criterion requires a discriminating measurement. **This draft's "the pair is measured (KFF9/KFF10)" line in the
Boundary section should be read as "the pair is exercised by the KFF9/KFF10 cases", not as "the fixture certifies
injectivity".**

## What this seat did NOT check

- The live re-fetch of the Unicode page (no network call by this seat; the scout's own receipt re-fetches it live
  and confirms the capture is byte-identical).
- Whether the L1 prefers this 35-line entry or the landed 66-line entry — the recommendation is to keep the landed one.
- The `used-by` path's E11 census state after landing — the entry exists at the path, so E11 does not fire.
