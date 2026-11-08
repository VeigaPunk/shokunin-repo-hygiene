# Cut a bounded raw excerpt on UTF-8 sequence boundaries, never inside a sequence

source: S354 (IETF RFC 3629 §3, the octet structure of a UTF-8 sequence); the r89 entry decode-escape-order.md
(raw bytes bounded before escaping) and the r90 entry nel-byte-character-pair.md (the byte/character pair);
scored against tools/souji-record-agreement.py and tests/fixtures/r91-k4-flagfail.py at round 91 (C2).
verified-at: RFC 3629 (Yergeau, November 2003; STD 63) re-opened 2026-11-08, HTTP 200, 33856 bytes, sha256
a2a3a39457d30420c812f87a38cc2b9194832f6982ef17e619de7d816879d6a6, byte-identical to capture
census/round-91/srcs/rfc3629.txt; quote at capture lines 183-185, occurrence count 1; recheck 365d or on supersession.

## The sequence is the unit

RFC 3629 §3: "In a sequence of n octets, n>1, the initial octet has the n higher-order bits set to 1, followed by
a bit set to 0." Its continuation octets all begin `10` (the §3 table gives the 2-, 3- and 4-octet rows); a
character is the whole sequence, so a cut between a lead octet and its continuations is not a character boundary.

## Why a raw-byte window must cut on boundaries

The r89 rule bounds the RAW bytes first (head-100, `…`, tail-99), then decodes with `surrogateescape`; that order
is right for content, but a cut inside a sequence hands the orphan continuation to `surrogateescape`, which maps
it to a lone surrogate U+DC80–U+DCFF, and `_escape_text` prints it `\xNN` — the raw byte's own spelling. KFF11's
payload `b"fatal: nel " + b"x"*90 + b"\xc2\x85" + b"s"*98` (201 bytes) cuts at index 102, the `0x85` continuation;
the r90 tool prints `…\x85sss…`, so a U+0085 straddling the cut spells exactly like a raw 0x85 (receipt .ufo/waves/round-91/w1/R91Scribe/kff11-before-vs-after.txt).

## The repair: move both cuts before decoding

- Head (`_cut_head`): walk back over continuation bytes to the initial octet; if that sequence is valid and the cut would split it, end the head BEFORE the initial octet (the character is elided whole); an invalid lead stays.
- Tail (`_cut_tail`): if the first tail byte is a continuation, find its lead; if the lead is in the elided middle, start the tail after the sequence's last continuation; a continuation with no lead stays, as `\xNN`.
- The bound is unchanged: head-100 + three-octet `…` + tail-99 = 202 octets; a moved cut only shortens its side.

Boundary: one cell (`_one_line_bytes`) in one tool; `_escape_record` and other readers are unchanged, payloads
differing only inside the elided middle still render identically, and a hardcoded-cell tool is not excluded. Measured residual (r91): `_cut_tail` advances once and does not re-check the new start, so an invalid multi-octet lead followed by a valid sequence at the cut can still start the tail on a continuation (case 2 of .ufo/waves/round-91/w1/R91Scribe/cut-edge-probe.txt renders `\x85`); the bullets above are the rule, not the r91 tool's full behaviour.

## Gate

- URL: https://www.rfc-editor.org/rfc/rfc3629.txt — opened 2026-11-08 (HTTP 200, 33856 bytes, sha256
  `a2a3a394…79d6a6`, byte-identical to capture `census/round-91/srcs/rfc3629.txt`).
- Located quote (≤25 words): "In a sequence of n octets, n>1, the initial octet has the n higher-order bits set
  to 1, followed by a bit set to 0." — §3 UTF-8 definition, capture lines 183-185, occurrence count 1, 25 words
  by `printf '%s\n' "$q" | wc -w`; the §3 octet table is at capture lines 195-201.
- Admit: tier A, docs, status `mined`, id S354.
