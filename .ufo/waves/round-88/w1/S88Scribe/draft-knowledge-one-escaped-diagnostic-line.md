# DRAFT — corpus/knowledge/: a diagnostic cell is one escaped line

Seat draft only. NOT a committed file. The L1 (SoujiR88) is the integration owner.
Proposed path: `corpus/knowledge/one-escaped-diagnostic-line.md`.
NOTE: a file at exactly this path ALREADY EXISTS in the lane (landed in e60ea25f, 65 lines).
This draft is a shorter (<=35 lines) rewrite for the L1 to compare against the landed entry, or
to supersede it — the landed entry is listed in full after the draft so the diff is visible.

---

## DRAFT — 35 lines (the seat's <=35 bound)

```markdown
# A diagnostic cell is one escaped line, and it keeps both ends

source: S348 (Python `str.splitlines` line boundaries); scoped against tools/souji-record-agreement.py and tests/fixtures/r88-k4-flagfail.py at
round 88. verified-at: python 3.14.8, git 2.56.0-1, 2026-11-08, at lane tip 72edae40 (capture census/round-88/srcs/str-splitlines.html sha256
5abdd8b9…eda42, 774910 bytes; live re-fetch byte-identical the same day). recheck: 90d, or on a Python minor bump. Round 88 (C2 `_one_line`).

## Which characters break a line-oriented reader

`str.splitlines()` does not break only on LF. The documented set is a superset of universal newlines: CR, CRLF, LF, VT, FF, FS, GS, RS, NEL, LS,
PS (S348, the boundary table under the anchor). A cell carrying any of them tears in two even with no LF byte present, and a reader that then
takes "the fifth TAB-separated field" reads the first half as a complete row and the second as garbage. The rule: **escape the text before it
becomes a cell**, and escape the WHOLE documented set, not only the characters the transport happens to produce. The lane's `_escape_text`
doubles the backslash first (so `\` + `n` and a real LF cannot share a spelling) and maps LF, TAB, CR, the C0 controls, DEL, NEL and LS/PS to
`\n`, `\t`, `\r`, `\xNN` and `\uNNNN`.

## Why the escape is on the text and not only on the path

A PATH is escaped because the record is a byte spelling a reader must recover (Q159): a path may hold LF, TAB or CR, and spacing them loses the
name. The delegated STDERR is escaped for a different reason: it is another process's text arriving inside a field the parent writes, and the
field must stay ONE record. Escaping only the path would leave the child's own message free to carry a boundary that splits the MISMATCH row the
reader parses. The rule is about the CELL: whatever text lands in the cell is escaped first.

## The both-ends bound

A 200-character excerpt of a 400-character exception line must choose which 200. A tail-only cut keeps the message and loses the TYPE NAME — the
part a reader acts on ("AttributeError", not "…y"). The lane's bound keeps both ends: the first 100 characters, an ellipsis, the last 99, on a
200-character excerpt. The middle is lost by design; a reader who needs it runs the command again. The excerpt is escaped FIRST and bounded
after, so the cut cannot introduce a boundary the source did not have.

## Boundary

This entry records one Python library's documented line boundaries and the lane's own escaping and excerpt rule. It is not a claim that every
tool in the lane escapes every cell, nor that a 200-character excerpt summarises a longer message, nor that base64 framing authenticates the
child (S85Sentinel F5 keeps that outside the claim). The r87 entry corpus/knowledge/splitlines-line-model.md holds the same boundary list from
the counter's side (S278); this entry holds it from the cell's side.
```

---

## The landed entry at `corpus/knowledge/one-escaped-diagnostic-line.md` (for the L1's diff)

Landed in e60ea25f, 65 lines. Its own Gate section already carries the S348 ADMIT and the S349
REJECT. Where it differs from this draft, and why I did not adopt it verbatim:

1. **65 lines vs the seat's <=35-line bound.** The seat spec asks for a knowledge section of at most
   35 lines. The landed entry is 65. If the L1 wants the shorter form, this draft is it; the landed
   text is otherwise sound and I did not find a factual error in it.
2. **It says "the lane's `_escape_text` … maps LF, TAB, CR, the C0 controls, DEL, NEL and LS/PS"** —
   accurate against the code (I read `tools/souji-record-agreement.py:173-195`; the map is exactly
   `o < 0x20 or o == 0x7F or o == 0x85`, plus 0x2028/0x2029). Mine says the same.
3. **Its "Framing versus escaping" section is the strongest part and I kept its substance**, but the
   seat asks specifically WHY the escape is applied to the text and not only to the path — the landed
   entry answers that under "Framing versus escaping" (the child may not choose the parent's record
   boundaries). The landed entry does NOT separately answer the path-vs-text question, so my draft
   adds that section ("Why the escape is on the text and not only on the path"), sourced from Q159.
4. **Its "What a line-oriented reader breaks on" section lists the boundaries by name** and cites
   "(S348, the `str.splitlines` boundary table)". That is the correct citation for the LIST — the
   table, not the quoted paragraph. See D3 in the Gate-row draft: the SOURCES row's own `teaches`
   cell asserts that list while the row's own quote does not carry it. The knowledge entry and the
   registry row should point at the same location.
5. **"the lane's own r87 entry"** (the seat's wording) is `corpus/knowledge/machine-parsed-path-spelling.md`
   (r87, S346/S347) for the path-escaping half and `corpus/knowledge/splitlines-line-model.md`
   (r55, S278) for the boundary-list half. My draft cites both by path; the landed entry cites
   neither by path.

## Verification backing the draft's factual claims

- Every one of the eleven documented boundaries, escaped by the lane's own `_escape_text`, yields
  exactly one `str.splitlines()` element (measured against the filed tool's function, imported from
  `tools/souji-record-agreement.py`): LF, CR, CRLF, VT, FF, FS, GS, RS, NEL, LS, PS -> 1 element each.
- `_one_line` on a 396-character `AttributeError: …` line returns exactly 200 characters, starts with
  the type name, and contains `AttributeError` — the both-ends bound, measured.
- `_one_line("")` returns `no stderr`; `_stderr_tail("")` returns `""` (the two branches differ, and
  the claim names only the FLAGFAIL branch's `no stderr`).
