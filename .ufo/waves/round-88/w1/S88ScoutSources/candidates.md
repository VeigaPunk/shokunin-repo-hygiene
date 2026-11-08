# S88ScoutSources — source candidates for round 88 (C2)

Contract: `SOURCES-CONTRACT-v1` (kaika, frozen 2026-10-19), read at
`/home/vgpnk/Projects/shokunin/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`.
Row shape (11 columns): `id | source | kind | tier | scope | anchor | teaches |
status | opened | recheck | used-by`.
Access date for every fetch below: **2026-11-08**. Host interpreter: **Python 3.14.8**
(`python3 --version`), so the /3.14/ page is the host-matching page.

Highest existing id when this seat read the registry: **S349**. This seat proposes
**S350** (admit) and **S351** (reject). Neither id is taken.

---

## S350 — Python 3.14 `str.splitlines` line boundaries — ADMIT

| field | value |
|---|---|
| **id** | S350 (proposed; next unused after S349) |
| **title / source** | Python 3.14 `str.splitlines` line boundaries — https://docs.python.org/3.14/builtins/stdtypes.html#str.splitlines |
| **url** | https://docs.python.org/3.14/builtins/stdtypes.html#str.splitlines |
| **access date** | 2026-11-08 |
| **tier** | A (primary — the official Python reference for the host interpreter's major version) |
| **class / kind** | `docs` |
| **status** | `mined` |
| **used-by** | corpus/knowledge/one-escaped-diagnostic-line.md |
| **anchor** | § `str.splitlines(keepends=False)`, anchor `#str.splitlines`, in the capture `census/round-88/srcs/str-splitlines.html` |
| **quote (18 words)** | "This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines." |

**scope.** Which byte sequences a Python `str.splitlines()` reader treats as line
boundaries (scope: the boundary list under `str.splitlines`; `keepends` behaviour and
the other `str` methods are out of scope).

**teaches.** The boundary list adds VT, FF, FS/GS/RS, NEL and LS/PS to LF/CR/CRLF, so a
diagnostic cell carrying any of them is two lines to a `splitlines` reader even when no LF
byte is present; escaping must cover the whole list, not only LF.

**Live access record.** Request `https://docs.python.org/3.14/library/stdtypes.html` →
**HTTP 200**, 1 redirect, final URL `https://docs.python.org/3.14/builtins/stdtypes.html`,
**774910 bytes**, sha256
`5abdd8b9ceeda2c3e94d8f95e32d9853d6f35d35844514727aa440cac98eda42`.
Requesting the final URL directly gives HTTP 200, 774910 bytes, the same sha256 (no
redirect). The filed capture `census/round-88/srcs/str-splitlines.html` is
**byte-identical to this round's live fetch** (same sha256, same 774910 bytes) — the
capture is a faithful copy of the live page, not a re-render.

**Located quote verification.** Recipe = the lane's own (census/round-55/wave/w1/
S55scribe01/receipts/verify_quotes.py): strip `<script>`/`<style>`, strip tags with the
**empty** replacement, `html.unescape`, collapse whitespace runs. Under that recipe the
18-word quote **is** a verbatim substring of the capture and `len(q.split()) == 18`,
matching the stated count.

**Rendered text at the anchor** (tag-stripped, whitespace-collapsed):
`str.splitlines(keepends=False)¶ Return a list of the lines in the string, breaking at
line boundaries. Line breaks are not included in the resulting list unless keepends is
given and true. This method splits on the following line boundaries. In particular, the
boundaries are a superset of universal newlines.`

**The boundary table, as rendered in the capture** (the row's actual scope):
`Representation Description \n Line Feed \r Carriage Return \r\n Carriage Return + Line
Feed \v or \x0b Line Tabulation \f or \x0c Form Feed \x1c File Separator \x1d Group
Separator \x1e Record Separator \x85 Next Line (C1 Control Code) \u2028 Line Separator
\u2029 Paragraph Separator Changed in version 3.2: \v and \f added to list of line
boundaries.`

**Duplicate-URL check.** The `stdtypes.html` family already carries four rows, and none
holds this scope:
- **S061** — `https://docs.python.org/3/library/stdtypes.html#str.lstrip` — scope: *strip-
  character semantics vs prefix removal* (a different method entirely).
- **S105** — `https://docs.python.org/3/builtins/stdtypes.html` — scope: *why ordinary
  Python equality is insufficient for typed counter expectations* (the `bool` type).
- **S266 / S267** — `https://docs.python.org/3/builtins/stdtypes.html#common-sequence-
  operations` — scope: *tuple equality underlying R45 register identity*.
- **S278** — `https://docs.python.org/3.12/library/stdtypes.html#str.splitlines` — scope:
  *the line-boundary set the frozen C1 v4 counter's hidden-line numbering must agree
  with (the r54 sentinel S1 mechanism)*; used by `corpus/knowledge/splitlines-line-model.md`.

**S348 is the row this seat's seat-spec asks about, and it is the closest relative — so
the duplicate-URL check must state the distinction, not assert it away.** S278 (3.12) and
S348 (3.14) quote the *same* sentence: I re-fetched both captures live and the rendered
boundary tables are **byte-identical** (`Representation Description \n Line Feed \r
Carriage Return \r\n Carriage Return + Line Feed \v or \x0b Line Tabulation \f or \x0c Form
Feed \x1c File Separator \x1d Group Separator \x1e Record Separator \x85 Next Line (C1
Control Code) \u2028 Line Separator \u2029 Paragraph Separator Changed in vers…`), and the
r55 located-quote file `census/round-55/sources/s278-located-quote.txt` records the same
18-word sentence as S348's quote. The two rows are therefore **not distinct facts**: S348
is the same boundary list re-opened at the host interpreter's version, and S278 already
grounds "the boundary list is wider than LF and CRLF".

**S350's scope is distinct from S278's only in the CONSUMER, not the fact**: S278 grounds
the set for a *hidden-line numbering* that must agree with an LF-only counter; S350
grounds it for an *escaping rule* that must keep a record cell one physical line. Two
different decisions cite one identical documented boundary list. Whether the registry
carries one row or two for the same page-content is the L1's call under contract rule 2
(a correction is a new row whose `teaches` opens `supersedes S0NN —`) and rule 4
("Expansion is knowledge, not rows … there is no row quota"). **This seat does not
propose superseding S278 or S348; it reports the overlap and the version distinction
(3.12 vs 3.14, and the /library/ → /builtins/ 301) and leaves the decision to the L1.**

**Duplicate-URL check, stated for the registry's W04 convention.** S350's URL
(`/3.14/builtins/stdtypes.html#str.splitlines`) is not shared with S061, S105, S266 or
S267 (different anchors/sections). It differs from S278 by version segment
(`/3.12/library/` vs `/3.14/builtins/`) and from S348 by nothing at all in the served
bytes.

**Capture.** `census/round-88/srcs/str-splitlines.html`, sha256
`5abdd8b9ceeda2c3e94d8f95e32d9853d6f35d35844514727aa440cac98eda42`, 774910 bytes.
Already present in the lane and byte-identical to the live page.

---

## S351 — Python 3.14 `pathlib` — REJECT (the one reject this seat proposes)

| field | value |
|---|---|
| **id** | S351 (proposed; next unused after S349) |
| **title / source** | Python 3.14 `pathlib` — https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.write_text |
| **url** | https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.write_text |
| **access date** | 2026-11-08 |
| **tier** | A (primary — official Python reference) |
| **class / kind** | `docs` |
| **status** | `rejected` (kept — a rejection is evidence of taste) |
| **used-by** | — |
| **anchor** | § `Path.write_text(data, encoding=None, errors=None, newline=None)`, anchor `#pathlib.Path.write_text` |
| **quote (10 words)** | "The optional parameters have the same meaning as in open()." |

**teaches.** REJECTED: the page states that `Path.write_text`'s optional parameters
inherit `open()`'s meaning and that the `newline` parameter was added in 3.10; it says
nothing about how a *record cell* must be escaped, and the tool under test never uses
`pathlib` (`grep -c "pathlib\|Path(" tools/souji-record-agreement.py` → **0**; its imports
are argparse, base64, binascii, hashlib, json, os, re, subprocess, sys). The enforceable
one-line rule is S348/S350's boundary list plus the lane's own `_escape_text`, so this row
would add registry weight rather than a decision for this surface. **Flip:** a round that
must decide a record's *on-disk* newline translation — i.e. a round whose artifact is
written through `Path.write_text` and whose reader splits the file's bytes — where
`open()`'s newline semantics, not the escape rule, would decide the outcome.

**Live access record.** Request `https://docs.python.org/3.14/library/pathlib.html` →
**HTTP 200**, 0 redirects, **272107 bytes**, sha256
`c5f1f5268f7887a38c2747dbb3ca1541ce6c55ec4bf04359d59ef8f66134a165`.

**Located quote verification.** Same lane recipe; the 10-word quote **is** a verbatim
substring of the capture, `len(q.split()) == 10`.

**Rendered text at the anchor:** `Path.write_text(data, encoding=None, errors=None,
newline=None)¶ Open the file pointed to in text mode, write data to it, and close the
file: … The optional parameters have the same meaning as in open(). Added in version 3.5.
Changed in version 3.10: The newline parameter was added.`

**Duplicate-URL check.** `pathlib.html` already carries **S040**
(`https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve`, scope: *pure path
computation vs filesystem-aware resolution*, used by `corpus/lessons/round-14.md`). S351
is a different anchor (`#pathlib.Path.write_text`) on a different version segment, so it
is not a URL duplicate — but it is on a page whose family the registry already reads, and
the proposed scope is **rejected on its merits**, not on duplication. S272
(`https://docs.python.org/3/library/functions.html`, the `open()` newline-parameter
description) already holds the `open()` newline contract that S351's quote points at, so
S351 would restate a scope S272 owns.

---

## Rejected-on-scope, NOT filed as a row (screened, counted, not admitted)

- **`base64` module docs** — https://docs.python.org/3.14/library/base64.html — HTTP 200,
  0 redirects, 61731 bytes, sha256
  `09b0682de6052bc8a77eb14655add2f2a80e286b08a60a51050da750ea43f984`. The lane already
  carries this decision as **S349** (rejected, with a flip condition) and the capture
  `census/round-88/srcs/base64.html` is byte-identical to this live fetch. **No new row:
  this would duplicate S349.** (S349's filed quote count is **16**; the quote itself has
  **15** words by `len(q.split())` — see the finding below.)
- **`subprocess` docs** — https://docs.python.org/3.14/library/subprocess.html — HTTP 200,
  0 redirects, 207155 bytes, sha256
  `2633e6027afa228b63b067fc6c930e3d42c88b8ef89c99df4faac6089c69369a`. Already held twice:
  **S067** (`/3/library/subprocess.html`, `start_new_session` and what a timeout does to
  the child) and **S074** (`/3.14/library/subprocess.html`, child-scoped documentation
  and session creation). A third scope would add weight without a decision: the
  `capture_output` clause the C2 claim leans on ("If capture_output is true, stdout and
  stderr will be captured.", 10 words, verified) is transport plumbing the lane's own
  code already fixes.

---

## Capture sha256 summary and word counts

| candidate | URL | HTTP | bytes | sha256 (live) | quote words |
|---|---|---|---|---|---|
| S350 stdtypes splitlines | /3.14/builtins/stdtypes.html | 200 | 774910 | `5abdd8b9…eda42` | 18 |
| S351 pathlib write_text | /3.14/library/pathlib.html | 200 | 272107 | `c5f1f526…4a165` | 10 |
| base64 (S349, dup) | /3.14/library/base64.html | 200 | 61731 | `09b0682d…43f984` | 15 (row says 16) |
| subprocess (screened) | /3.14/library/subprocess.html | 200 | 207155 | `2633e602…369a` | 10 |
