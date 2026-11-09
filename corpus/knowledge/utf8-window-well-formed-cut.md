# Move an excerpt cut only across a WELL-FORMED UTF-8 sequence, never on the lead byte's bit pattern

source: S355 (The Unicode Standard 18.0.0, Chapter 3, §3.9 D84a–D86 and Table 3-7 Well-Formed UTF-8 Byte Sequences);
S354 (RFC 3629 §3, the sequence unit) and the lane's r91 entry corpus/knowledge/utf8-window-sequence-boundary.md;
scored against tools/souji-record-agreement.py and tests/fixtures/r92-k4-flagfail.py at round 92.
verified-at: Unicode 18.0.0 core spec chapter 3, 2026-11-08, capture census/round-92/srcs/unicode-ch3.html sha256
f9e158a640c88cb0aebf60e5f724ea4f957eca539c620fb1e161cb6c8f8fb22e (428731 bytes, fetched twice this round,
byte-identical); the quoted sentence occurs once in the whitespace-normalized tag-stripped text.
recheck: 365d, or when a new Unicode version changes §3.9 (the `latest` URL redirects to the versioned page).

Round 92 (C2, the K4 FLAGFAIL detail). Ground: S355 (well-formedness), S354 (the sequence unit), the r91 entry
(cuts on sequence boundaries).

## What is well-formed, and what an ill-formed byte may not do

Table 3-7 lists the well-formed UTF-8 byte sequences row by row. It is stricter than the lead byte's bit pattern:
C0, C1 and F5..FF never start a sequence; after E0 the second byte must be A0..BF (80..9F would be an overlong
encoding); after ED it must be 80..9F (A0..BF would encode a surrogate); after F0 it must be 90..BF; after F4 it
must be 80..8F (beyond U+10FFFF otherwise). §3.9 D86 then states the partition rule: "Ill-formed code unit
subsequences do not overlap with minimal well-formed code unit subsequences." A byte that is not part of a
well-formed sequence stands alone; it never owns the bytes of the well-formed sequence after it.

## What the r91 cut did wrong

The r91 helpers read the lead byte's structural length (C0..DF two octets, E0..EF three, F0..F7 four) and moved the
tail cut to the end of that declared length. When an ill-formed lead (a truncated `F0 80`, an overlong `E0 80 80`)
sat just before the tail cut, the declared length reached INTO the next, well-formed sequence, the cut landed after
that sequence's lead, and its continuation byte was printed with the raw byte's spelling. Two materially different
payloads — one carrying the character U+0085, one carrying the raw byte 0x85 at the same place — rendered the same
cell (R91ExecC2Tool repro, payloads A and B). That is exactly the overlap D86 forbids: the ill-formed lead was
treated as owning bytes of a minimal well-formed subsequence.

## The repair

A cut moves only when the bytes on both sides of it form ONE well-formed sequence: the candidate bytes must decode
strictly to exactly one character, which applies every row of Table 3-7 at once (Python's strict UTF-8 decoder
rejects overlongs, surrogates, leads C0/C1/F5..FF and code points beyond U+10FFFF). Otherwise the cut stays and every
byte near it keeps its own `\xNN` spelling. With that rule the excerpt's head is a prefix, and its tail a suffix, of
the whole payload's own rendering `_escape_text(_decode_record(raw))` — no byte is respelled by where the 200-octet
window happens to fall. The byte bound does not grow (head-100, a three-octet ellipsis, tail-99; a moved cut only
shortens its side).

## Boundary

This entry records one tool's excerpt rule and the Table 3-7 / D86 facts it rests on. The prefix/suffix property is
measured on a finite deterministic sweep (fixture case KFF18: 15 byte tokens, pairwise, at offsets 84–117, lengths
205/210/214), not proven for every payload. It is not a claim about U+FFFD substitution (the tool escapes, it does
not substitute), not a claim that other lane readers cut on well-formed boundaries, and not a claim that two
payloads that differ only inside the elided middle can be told apart.
