# Pin an excerpt cut's POSITION with a reference written from the decoder algorithm, not only its faithfulness

source: S356 (WHATWG Encoding Standard, §8.1.1 UTF-8 decoder); S355 (The Unicode Standard 18.0.0, §3.9 Table 3-7)
and the lane's r92 entry corpus/knowledge/utf8-window-well-formed-cut.md; scored against
tools/souji-record-agreement.py and tests/fixtures/r93-k4-flagfail.py at round 93.
verified-at: WHATWG Encoding Standard, Last Updated 19 October 2026, opened 2026-11-09, capture
census/round-93/srcs/encoding.html sha256 e1421f1791b202717883c452a6267129ce5fb3ca13652e5022a2b6d2a11fc262 (591022
bytes); the quoted sentence occurs once in the whitespace-normalized tag-stripped text.
recheck: 365d, or when the Living Standard changes §8.1.1.

Round 93 (C2, the K4 FLAGFAIL detail's verification coverage). Ground: S356 (the decoder algorithm), S355
(well-formedness), the r92 entry (a cut moves only across one well-formed sequence).

## Why faithfulness alone does not pin the cut

The r92 fixture's sweep (KFF18) required the excerpt's head to be a prefix and its tail a suffix of the payload's own
rendering. Any cut that lands on a character boundary satisfies that, wherever it lands. Three one-edit forgeries of
the r92 tool kept it and still passed 20/20 (R92MutC2): deciding the straddling sequence with Python's
`surrogatepass` handler (an ED A0..BF surrogate encoding, ill-formed per Table 3-7, is moved across as one
sequence), accepting a span of several characters (`len(...) >= 1`), and moving the head cut forward past the
sequence instead of back to its start. Each emits a different excerpt from the filed tool; none respells a byte.

## The reference

S356 states the UTF-8 decoder as a byte-at-a-time algorithm: a lead 0xC2..0xDF needs one continuation, 0xE0..0xEF
two, 0xF0..0xF4 three, any other lead is an error; the first continuation's range is 0x80..0xBF except "If byte is
0xE0, then set UTF-8 lower boundary to 0xA0. If byte is 0xED, then set UTF-8 upper boundary to 0x9F." (and 0x90 for
0xF0, 0x8F for 0xF4); every later continuation is 0x80..0xBF. A byte outside the current boundaries ends the attempt.
Written from those steps, the reference finds the one well-formed sequence starting at most three bytes before a cut
and ending after it (a well-formed sequence starts on a byte that is never a continuation, so at most one can
straddle a cut). The head cut moves back to its start, the tail cut forward to its end; otherwise the cut stays.

The reference shares no code with the tool (no `bytes.decode`), so agreement on a sweep is evidence about the tool,
not about Python's codec. On the r93 boundary-class sweep (33 tokens: every Table 3-7 row at its low and high second
byte, plus C0/C1 leads, E0/F0 overlongs, ED surrogates, F4 beyond U+10FFFF, F5.., bare continuations and truncated
sequences; pairwise, at every offset that puts a cut inside or at the edge of the pair; both cuts; 14,586 payloads)
the filed tool's excerpt equals the reference cell on every payload, the r91 tool on 11,490 of them.

## How to apply

When an instrument checks a cut, check where it lands against an independent reference, not only that the pieces
are faithful: a faithfulness property is satisfied by every boundary-respecting cut, so it cannot tell a cut that
moved too far, not far enough or across ill-formed bytes from the right one. Build the reference from the
specification's algorithm (S356) or table (S355), never by calling the same library routine the tool calls.

## Limits

- The sweep is finite (14,586 payloads, one payload length, filler `a`); equality there is measured, not proven for
  every payload.
- The reference covers where a cut lands; the escaping of the bytes on each side is the tool's own
  `_escape_text(_decode_record(...))` and is checked by the other cases (KFF4-KFF16).
- U+FFFD substitution of maximal subparts is out of scope: the tool escapes ill-formed bytes and never substitutes.
