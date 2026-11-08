# A diagnostic cell is one escaped line, and a long one keeps its head

source: S348 (Python `str.splitlines` line boundaries); scored against tools/souji-record-agreement.py and
tests/fixtures/r88-k4-flagfail.py at round 88.
verified-at: python 3.14.8 (the lane's interpreter), git 2.56.0-1, 2026-11-08.
recheck: 90d, or on any Python minor bump (the boundary list is stable; the escape set is the lane's own).

Round 88 (C2 `_one_line`, the FLAGFAIL branch). Ground: S348.

## What a line-oriented reader breaks on

A reader that collects a tool's records with `str.splitlines()` does not break only on LF. The documented boundary
list is a superset of universal newlines: CR, CRLF and LF, plus VT (`\x0b`), FF (`\x0c`), FS/GS/RS (`\x1c`-`\x1e`),
NEL (`\x85`), LS (`\u2028`) and PS (`\u2029`) (S348, the `str.splitlines` boundary table). So a cell that carries
one of the non-LF boundaries tears a record in two even though no LF byte is present, and a reader that then parses
"the fifth TAB-separated field" reads the first half as a complete row and the second half as garbage. A tab, a CR
and a backslash tear or re-spell a record in the same way for a tab- or escape-aware reader.

The consequence for a diagnostic cell is one rule: **escape the text before it becomes a cell**, and escape the
whole documented set, not only the two characters the transport happens to produce. The lane's `_escape_text`
doubles the backslash first (so `\` + `n` and a real LF cannot share a spelling) and maps LF, TAB, CR, the C0
controls, DEL, NEL and LS/PS to `\n`, `\t`, `\r`, `\xNN` and `\uNNNN`; `_escape_record` applies the same injective
spelling to a path's raw bytes.

## Why the head matters

A 200-character excerpt of a 400-character exception line has to choose which 200. A tail-only cut keeps the
message and loses the type name — and the type name is the part a reader acts on ("AttributeError", not "…y").
The lane's bound therefore keeps both ends: the first 100 characters, an ellipsis, the last 99, on a 200-character
excerpt. The middle is lost by design; a reader who needs it runs the command again. The excerpt is then escaped,
so the ellipsis and the cut cannot introduce a boundary the source did not have.

## Framing versus escaping

The FLAGFAIL branch is a child process's stderr, and the parent parses the child's stdout as records. Making the
child print the raw stderr would let the child choose the parent's record boundaries (a forged writer can print
`MISMATCH\tK4\t…` and it parses as a real row); escaping it in the child would duplicate the escape rule in a
bootstrap that cannot import the parent's helpers. The lane's answer is a frame: the child ships the raw bytes
base64-framed (an ASCII alphabet with no boundary characters), and the parent owns the single escaping rule on the
decoded text. The frame is transport, not knowledge; the rule it protects is S348's.

## Boundary

This entry records one Python library's documented line boundaries and the lane's own escaping and excerpt rule.
It is not a claim that every tool in the lane escapes every cell (the r87 limit stands: a control byte outside the
escaped set can still land raw in a record the lane does not own), not a claim that a 200-character excerpt is a
summary of a longer message, and not a claim that base64 framing authenticates the child: a forged writer inside the
audited tree can still print a forged `WRITER`/`FLAGFAIL` payload (S85Sentinel F5 keeps that outside the claim).

## Gate

- **S348 — Python 3.14 `str.splitlines` line boundaries** (https://docs.python.org/3.14/builtins/stdtypes.html#str.splitlines,
  requested `/3.14/library/stdtypes.html` and served after one 301; HTTP 200, 774910 bytes, sha256
  `5abdd8b9…`, capture `census/round-88/srcs/str-splitlines.html`, opened 2026-11-08). Quote, the paragraph under
  the anchor: "This method splits on the following line boundaries. In particular, the boundaries are a superset of
  universal newlines." (18 words). **ADMIT**, `docs`, tier A, `mined` — it grounds C2's one-physical-line rule and
  names every boundary the escape set must cover. Duplicate-URL check: `stdtypes.html` is cited by S061
  (`str.lstrip`) and S105 (boolean numeric equality) for other scopes; this row names the `splitlines` boundary list
  only.
- **Rejected — Python 3.14 `base64`** (https://docs.python.org/3.14/library/base64.html, HTTP 200, 61731 bytes,
  sha256 `09b0682d…`, capture `census/round-88/srcs/base64.html`, opened 2026-11-08). Quote, `b64decode` entry:
  "Decode the Base64 encoded bytes-like object or ASCII string s and return the decoded bytes." (15 words).
  **REJECTED** on scope: the frame is the lane's own transport choice; the page states the encoding and its
  `validate` parameter, not a record-format rule the lane reuses, and S348 carries the enforceable property.
  **Flip:** a round that must decide padding or validation semantics for an untrusted *external* base64 payload.
