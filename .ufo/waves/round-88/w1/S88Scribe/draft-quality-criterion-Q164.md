# S88Scribe — DRAFT: one QUALITY.md criterion (next free Q)

Seat draft only. NOT a committed file. The L1 (SoujiR88) is the integration owner.
Numbering: the lane's next free Q is **Q164** (`corpus/QUALITY.md` ends its Round-88 section at
Q163; `grep -oE '\bQ[0-9]+\b'` over the file tops out at 163, and `Q164` occurs nowhere in the file).
The draft therefore takes Q164 and lands in the existing `## Round 88 criteria` table, after Q163.

## DRAFT — the Q164 row, in the lane's pipe-table schema

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q164 | Extends Q163 and Q159 (they stand), and corrects one clause of Q161 (the rest of Q161 stands): the "keeps the tail" half of Q161 describes the bound the r87 bytes had, not the bound the lane's bytes have. A delegated failure detail is ONE escaped physical line that keeps BOTH ends: the first 100 characters, an ellipsis, the last 99, of a 200-character excerpt. A tail-only excerpt that drops an exception's type name is a defect, not a formatting choice — the type name is the part a reader acts on ("AttributeError", not "…y"). "One line" is decided by a `str.splitlines()` reader, not by an LF-only one: the documented boundary set is CR, CRLF, LF, VT, FF, FS, GS, RS, NEL, LS and PS (S348), so a cell carrying any of them is two lines to that reader even when no LF byte is present, and escaping must cover the whole set rather than only the characters the transport happens to produce. The escape is applied to the delegated TEXT and not only to the path: a path is escaped so a reader can recover the name (Q159), but the child's stderr is escaped because it lands inside a field the parent writes and must not be able to split the record the reader parses. | every lane tool whose record detail carries another process's stderr or error text, and every record field a reader parses by line | `python3 -B tests/fixtures/r88-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-88/controls/c2-before-tool.py --work <scratch>` must print `SUMMARY cases=7 tool_pass=7 before_pass=3`; the before bytes must fail KFF2/KFF3/KFF4/KFF5 and pass exactly KFF1/KFC1/KFC2; a K4 detail cell must span one physical line, must contain `AttributeError` on the KFF2/KFF3 arms, and must print `no stderr` on the empty arm | corpus/lessons/round-88.md (M2 — the first KFF2 predicate asserted a raw-traceback marker that the CORRECT escaped detail still spells, so the fixture measured the escape instead of the rule); `census/round-88/records/c2-after.txt`, `census/round-88/controls/c2-before.txt` |

---

## Notes for the L1

**1. Why this is Q164 and not a rewrite of Q161.** The lane's rule (the `corpus/QUALITY.md` header)
is that "a criterion is superseded by a new row that names the row it replaces, never rewritten".
Q161's first clause — "the last non-empty stderr line is where an exception names itself, while the
first 200 characters of a traceback are the frame list" — is still true and is about WHICH LINE to
take. Its second clause — "prints that tail, bounded, with a leading ellipsis when the line itself
is cut" — describes a bound the lane's bytes no longer have. The draft therefore extends Q161
explicitly rather than editing it.

**2. The defect this names, measured.** I traced `_stderr_tail` through the lane's revisions:

| revision | cut expression | keeps both ends? |
|---|---|---|
| `6e502c5c` (r87 first repair) | `tail = "…" + tail[-(limit - 1):]` | no — leading ellipsis, tail only |
| `7defe9c5` (lane base) | `tail = tail[:head] + "…" + tail[-keep:]` | yes |
| `89d36922` (r87 wave repair 2) | `tail = tail[:head] + "…" + tail[-keep:]` | yes |
| `749c7829` (r87 evidence, Q161 filed) | `tail = tail[:head] + "…" + tail[-keep:]` | yes |
| `HEAD` `72edae40` | `tail = tail[:head] + "…" + tail[-keep:]` | yes |

So Q161 was filed at `749c7829` describing a leading-ellipsis tail-only cut, while the bytes in
that very commit kept both ends. The tool's own `_stderr_tail` docstring
(`tools/souji-record-agreement.py:254` (still stale at the tip `72edae40`, where the L1 repaired
`_one_line`'s docstring but not this one)) still says "over-long line keeps its tail and is marked with
a leading ellipsis" — the same stale sentence, in the same lane, since the lane base. That
docstring is a code comment, not a committed-file edit I may make; it is a candidate carry for the
L1 to route (it is a one-line comment in a tool the round already touches, but the tool's bytes are
frozen by C2's kill rule, so changing the docstring changes the tool's sha256 and would invalidate
the round's after receipts — the L1 should decide, not me).

**3. Measured behaviour that backs the criterion's test cell.** Against the filed tool's own
functions (`tools/souji-record-agreement.py`):
- `_one_line("AttributeError: " + "x"*380)` -> 200 chars, starts with `AttributeError`, contains
  `AttributeError` (the both-ends bound keeps the type name).
- `_one_line("")` -> `"no stderr"`; `_stderr_tail("")` -> `""`. The two branches differ, and the
  criterion's test names only the FLAGFAIL branch's `no stderr`.
- Every one of the eleven documented boundaries, escaped by `_escape_text`, yields exactly one
  `str.splitlines()` element — LF, CR, CRLF, VT, FF, FS, GS, RS, NEL, LS, PS each -> 1 element.

**4. The lesson pointer.** The row cites `corpus/lessons/round-88.md` M2, which is the round's own
recorded mistake and the direct teacher of the criterion's shape: the first KFF2 predicate asserted
`"  File " not in out`, which is FALSE on the correct escaped detail, because the escaped traceback
still spells `  File` — so the fixture was measuring the escape instead of the rule, and the
predicate was narrowed to `"\n  File " not in out` (no RAW traceback line). A criterion whose test
can fail on a correct artifact is the defect M2 records, and the criterion should name it.

**5. What I did not claim.** I did not re-run the r88 fixture: the C2 after/before receipts are
another seat's evidence (`census/round-88/records/c2-after.txt`,
`census/round-88/controls/c2-before.txt`) and the round's contract binds them. My contribution to
C2 is the corpus side only — the S348 Gate row, the knowledge section, and this criterion.
