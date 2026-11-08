# Cut a bounded excerpt on UTF-8 sequence boundaries, not on raw byte counts alone

source: S354 (IETF RFC 3629 §3, UTF-8 definition; the octet-structure paragraph); the lane's own r89 entry
corpus/knowledge/decode-escape-order.md and r90 entry corpus/knowledge/nel-byte-character-pair.md; scored against
tools/souji-record-agreement.py and tests/fixtures/r91-k4-flagfail.py at round 91.
verified-at: RFC 3629 (Yergeau, November 2003), 2026-11-08, capture census/round-91/srcs/rfc3629.txt sha256
a2a3a39457d30420c812f87a38cc2b9194832f6982ef17e619de7d816879d6a6, 33856 bytes; the quoted sentence sits at capture
lines 183-185, occurrence count 1.
recheck: 365d, or if RFC 3629 is superseded (a new UTF-8 definition would be opened at its versioned URL).

Round 91 (C2, the K4 FLAGFAIL detail). Ground: S354 (the sequence unit), the r89 entry (raw-byte-first bounding and
`surrogateescape`), the r90 entry (the byte/character spelling pair).

## What a UTF-8 sequence is

RFC 3629 §3: "In a sequence of n octets, n>1, the initial octet has the n higher-order bits set to 1, followed by a
bit set to 0." The following octets all have the high bits 10. A multi-octet character is therefore ONE sequence:
its initial octet and its continuation octets are not independently meaningful, and a byte-level cut placed between
them does not land on a character boundary.

## Why a raw-byte window must respect it

The r89 bounding rule keeps the first 100 and last 99 raw bytes of an over-long stderr, then decodes the window with
`surrogateescape` and escapes the text. That order is right for content (the head carries an exception's type name),
but it left the cuts blind to sequence boundaries. A 201-byte stderr whose U+0085 (`C2 85`) straddles the tail cut
loses the `C2` in the elided middle, and the surviving `85` is decoded as the lone surrogate U+DC85 and printed
`\x85` — exactly the spelling the raw byte 0x85 takes. The character cell and the byte cell collapse again, one round
after the r90 repair separated them for payloads that fit inside the window (S90Reviewer2 F1).

## The repair

Move each cut to a boundary before decoding.

- **Head**: walk back over continuation bytes to the initial octet of the sequence touching the cut. If the sequence
  is valid and extends past the cut, start the head at the initial octet (drop the partial sequence entirely).
  If the byte at the cut is not a continuation whose lead the head holds, leave it: an invalid lead byte is data and
  keeps its `\xNN` spelling.
- **Tail**: if the first tail byte is a continuation, find its lead. If the lead is in the elided middle, advance
  past the remaining continuation bytes (the character is elided whole). A continuation byte with no lead in the
  bytes before it is invalid data and stays, again keeping `\xNN`.

The bound does not grow: head-100 plus a three-octet ellipsis plus tail-99 is 202 octets, and a moved cut only
shortens its side. A character that straddles a cut is elided whole, so the excerpt never prints half a character as
a byte.

## Boundary

This entry records the sequence structure and one lane tool's excerpt rule. It is not a claim that every lane cell
cuts on boundaries (other readers are unchanged), not a claim that an excerpt is a summary of the message, not a
claim that two payloads differing only inside the elided middle are distinguishable, and not a claim of universal
injectivity: the measured pair is the raw byte 0x85 against the character U+0085 at the tested cuts. A tool that
prints a hardcoded cell can still pass a fixture that reads only the cell; the fixture binds the public path, not
the tool's internals.
