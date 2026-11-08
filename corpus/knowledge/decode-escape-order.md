# Bound the raw bytes before the escaping rule runs, and decode with the handler that cannot collide

source: S351 (Python `codecs` § Error Handlers, the `surrogateescape` entry); S348 (Python `str.splitlines` line
boundaries); the lane's own r87 entry corpus/knowledge/machine-parsed-path-spelling.md and r55 entry
corpus/knowledge/splitlines-line-model.md; scored against tools/souji-record-agreement.py and
tests/fixtures/r89-k4-flagfail.py at round 89.
verified-at: python 3.14.8, git 2.56.0-1, 2026-11-08, at lane tip a3c7cb1f (capture census/round-89/srcs/codecs.html
sha256 62a3d3da…fea6f, 181610 bytes; the quote verified `True 13` against the capture's rendered text).
recheck: 90d, or on any Python minor bump (the handler's contract is stable; the escape set is the lane's own).

Round 89 (C2, the FLAGFAIL detail). Ground: S351 (the decode), S348 (the boundaries), the r87 entry (the escaping
rule for a path), the r55 entry (the same boundary list from the counter's side).

## Which characters break a line-oriented reader

`str.splitlines()` does not break only on LF. The documented set is a superset of universal newlines: CR, CRLF, LF,
VT, FF, FS, GS, RS, NEL, LS, PS (S348, the boundary table under the anchor). A cell carrying any of them tears in
two even with no LF byte present, and a reader that then takes "the fifth TAB-separated field" reads the first half
as a complete row and the second as garbage. The rule: **escape the text before it becomes a cell**, and escape the
WHOLE documented set, not only the characters the transport happens to produce. The lane's `_escape_text` doubles
the backslash first (so `\` + `n` and a real LF cannot share a spelling) and maps LF, TAB, CR, the C0 controls,
DEL, NEL and LS/PS to `\n`, `\t`, `\r`, `\xNN` and `\uNNNN`.

## Why the escape is on the text and not only on the path

A PATH is escaped because the record is a byte spelling a reader must recover (Q159, the r87 entry): a path may
hold LF, TAB or CR, and spacing them loses the name. The delegated STDERR is escaped for a different reason: it is
another process's text arriving inside a field the parent writes, and the field must stay ONE record. Escaping
only the path would leave the child's own message free to carry a boundary that splits the MISMATCH row the reader
parses. The rule is about the CELL: whatever text lands in the cell is escaped first.

## Bound raw bytes first, then escape — and decode with the handler that cannot collide

A 200-byte excerpt of a long stderr must choose which raw bytes to keep. If the escaping rule runs first, each
control byte costs four characters, so 25 leading control bytes consume a 100-character head entirely and an
exception's type name — the reason the head exists — falls outside both ends (S88Sentinel F2). Bounding the RAW
bytes first (head-100 / `…` / tail-99 of raw content) and escaping the window means the head is spent on content.
The escaped rendering of a control-heavy input can reach ~800 characters (each control byte costs four); the
bound is on the bytes.

The decode matters as much as the order. `surrogateescape` "On decoding, replace byte with individual surrogate
code ranging from U+DC80 to U+DCFF." (S351). The escaping rule then prints each surrogate as `\xNN` with its
original byte value, while a literal backslash sequence gets its backslash doubled — so a bad byte and its
literal spelling stay distinct. `backslashreplace` turns the bad byte into the four literal characters `\xff`,
which the escaping rule then doubles — the SAME output as the literal spelling. Two materially different
delegated failures become indistinguishable in the record.

## Boundary

This entry records one Python library's documented line boundaries and the lane's own escaping and excerpt rule.
It is not a claim that every tool in the lane escapes every cell (the r87 limit stands: a control byte outside the
escaped set can still land raw in a record the lane does not own), not a claim that a 200-byte excerpt is a
summary of a longer message, and not a claim that base64 framing authenticates the child (S85Sentinel F5 keeps that
outside the claim). The decode is injective for the bad-byte/literal pair; a raw 0x85 byte and the NEL character
(U+0085) still render identically because `_escape_text` spells both `\x85` — a measured r89 limitation, not
a property this entry claims.
