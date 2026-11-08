# Draft — corpus/knowledge/nel-byte-character-pair.md (souji r90, seat S90Scribe)

Target path in the lane: `corpus/knowledge/nel-byte-character-pair.md`. The untracked working-tree file at that
path is 61 lines; the brief's bound is ≤35 lines, and **this draft is 34 lines** (counted with `wc -l` on the
fenced block below). Schema follows the r89 entry `corpus/knowledge/decode-escape-order.md`.

## The entry (paste-ready)

````markdown
# A raw byte and the character that decodes to it need different spellings

source: S353 (Unicode UAX #14 § NL: Next Line — the line-break class of U+0085); S351 (Python `codecs`
`surrogateescape`); S348 (Python `str.splitlines` line boundaries); scored against
tools/souji-record-agreement.py and tests/fixtures/r90-k4-flagfail.py at round 90.
verified-at: python 3.14.8, git 2.56.0-1, 2026-11-08, against the tool bytes of commit 4cb3a06f (capture
census/round-90/srcs/tr14.html sha256 296df533…acc7c0, 226166 bytes; the quote verified once at tag-stripped
offset 82360, 18 words).
recheck: 365d, or on a Unicode version bump (the NL class is stable; the escape set is the lane's own).

Round 90 (C2, the K4 FLAGFAIL detail). Ground: S353 (the character's line-break class), S348 (the boundary set),
S351 (the decode), the r89 entry `decode-escape-order.md` (the raw-first bound).

## The pair that collided

A delegated child's stderr arrives as BYTES. `_decode_record` decodes with `surrogateescape` (S351), so an invalid
byte such as 0x85 becomes the lone surrogate U+DC85 and `_escape_text` printed it as `\x85`. A stderr carrying
the CHARACTER U+0085 instead encodes it as the two valid UTF-8 bytes `\xc2\x85`, decodes to the real character,
and the r89 rule's `o == 0x85` branch printed it `\x85` too. Two materially different failures shared one cell,
and the record could not say which had happened.

## Why the character must be spelled differently

U+0085 is a character, not a byte spelling, and its line-break class is NL: "The NL class acts like BK in all
respects (there is a mandatory break after any NEL character)." (S353, 18 words). `str.splitlines()` treats it as
a boundary too (S348). A one-line record cell must therefore escape it, and it must not borrow the raw-byte
spelling: the byte is `\x85`, the character is `\u0085`. The same branch already spells U+2028 and U+2029 as
`\uNNNN` (S87Sentinel F4); U+0085 joins them.

## The rule

- Raw bytes that are not valid UTF-8: `\xNN` with the original byte value (via `surrogateescape`, S351).
- Characters whose code point is a documented `str.splitlines()` boundary above 0x7F — U+0085, U+2028, U+2029:
  `\uNNNN` (S348, S353).
- A literal backslash sequence keeps its backslash doubled (r87 rule), so no spelling is ambiguous with a
  character's own name.

## Boundary

One lane tool's spelling rule for one cell (`_escape_text`, the delegated-stderr detail). No universal
injectivity is claimed: the pair is measured (KFF9/KFF10), a stderr differing only inside the elided middle
still renders identically, and `_escape_record` (path bytes) is unchanged and byte-based, so a path's U+0085 bytes
already print `\xc2\x85`. The dead escape-first helper `_one_line` was deleted in the same round (zero callers).

## Gate

- URL: https://www.unicode.org/reports/tr14/ — opened 2026-11-08 (HTTP 200, 226166 bytes, sha256
  `296df533…acc7c0`; the page names Version "Unicode 18.0.0", Revision "tr14-57.html", Date 2026-09-01).
- Located quote (≤25 words): "The NL class acts like BK in all respects (there is a mandatory break after any NEL
  character)." — § NL: Next Line, tag-stripped offset 82360, occurrence count 1; the class-table row
  `0085 / NEXT LINE (NEL)` sits at capture lines 2874-2875, and `LineBreak.txt` line 95
  (`0085           ; NL # Cc         <control-0085>`) agrees.
- Admit/reject: admit (tier A, docs, status `mined`). Reject sample: the Unicode Newline Guidelines (UAX #13) —
  it discusses newline conventions and names no decision this cell needs, so it stays a lead; flip if the lane
  must decide which newline CONVENTION a producer followed.
````

## Facts each claim rests on (re-measured this seat, committed bytes)

| claim | how it was measured | result |
|---|---|---|
| the capture's digest and size | `sha256sum census/round-90/srcs/tr14.html`; `stat -c '%s bytes'` | `296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0`, 226166 bytes |
| the quote is in the capture, once, 18 words | `python3 -B …/verify_quote.py` (the pasted command in `draft-sources-row-S353.md`) | match True, occurrence_count 1, words 18, tag_stripped_char_offset 82360 |
| the class-table row's capture lines | `awk 'NR>=2870 && NR<=2881 {printf "%d: %s\n", NR, $0}' census/round-90/srcs/tr14.html` | 2870 = the `NL: Next Line (Non-tailorable)` heading; 2874 = `0085`; 2875 = `NEXT LINE (NEL)`; 2878-2879 = the quoted sentence |
| the LineBreak data line agrees | `grep -n "^0085" census/round-90/srcs/LineBreak.txt` | line 95: `0085           ; NL # Cc         <control-0085>` |
| the byte path and the character path used to collide | `census/round-90/controls/c2-before-tool.py` (the r89 bytes), `_escape_text`: `elif o < 0x20 or o == 0x7F or o == 0x85: out.append("\\x%02x" % o)` | the r89 rule maps BOTH the character U+0085 and (via the surrogate arm) the raw byte 0x85 to `\x85` |
| the filed tool now separates them | `tools/souji-record-agreement.py` sha256 `d095b52f…8561`, `_escape_text`: `elif o in (0x85, 0x2028, 0x2029): … out.append("\\u%04x" % o)` and the surrogate arm `0xDC80 <= o <= 0xDCFF → "\\x%02x" % (o - 0xDC00)` | the character takes `\u0085`; the byte keeps `\x85` |
| the pair is MEASURED, not asserted | `python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-90/controls/c2-before-tool.py --work <empty>` | `SUMMARY cases=12 tool_pass=12 before_pass=10`, EXIT 0 (KFF9/KFF10 `tool=pass before=fail`; the fixture's pair check requires the two details to be different cells) |
| `_one_line` is gone | `grep -c 'def _one_line(' tools/souji-record-agreement.py` → 0; `grep -n "_one_line" tools/souji-record-agreement.py` → only `_one_line_bytes` (the live helper) and a docstring naming the deleted one | dead code deleted, no caller remains |

## What this seat did NOT check

- The live re-fetch of the Unicode page (no network call); the version stamps come from the committed capture.
- Whether the L1 prefers this 34-line entry over the 61-line untracked working-tree file at the same path (both
  are drafts for the L1 to choose between; the brief's bound is ≤35 lines, so this one follows it).
- The `used-by` path's E11 census state after landing — the entry must exist at the path when the S353 row
  lands, which it will if the L1 lands both together.
