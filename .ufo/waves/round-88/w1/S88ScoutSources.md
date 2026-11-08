# S88ScoutSources — round 88 wave 1: the source C2 rests on, opened live

Seat: S88ScoutSources (leaf; no dispatch). Lane base 7defe9c5fee3df07e403666bdeccfb88428ef729.
Access date for every fetch below: **2026-11-08**. Host interpreter: **Python 3.14.8**
(`python3 --version`), so the /3.14/ page is the host-matching page.

Verdict: **the source C2 rests on is sound and reproduces byte-for-byte; the escape rule it
grounds is exactly the rule the tool implements.** One reproducer-backed finding: the tool's
escape set is *narrower* than the frozen C2 wording's phrase "C0/C1 controls", so a C1 control
that is **not** a `str.splitlines` boundary (e.g. U+009F) still lands raw in the K4 detail.
That is a wording-scope finding for `plans/round-88.md`, not a kill: the frozen kill rule
names SOH / NEL / U+2028, all three of which the tool escapes, and the record stays ONE
physical line. Details and repro below.

Companion file (the candidates file the acceptance asks for):
`.ufo/waves/round-88/w1/S88ScoutSources/candidates.md`.
Receipts: `.ufo/waves/round-88/w1/S88ScoutSources/receipts/`.

---

## 1. The source C2 rests on: S348, re-opened live and verified

**S348** — Python 3.14 `str.splitlines` line boundaries —
`https://docs.python.org/3.14/builtins/stdtypes.html#str.splitlines`
(`census/round-88/srcs/str-splitlines.html`, anchor `#str.splitlines`).

**Live access record.** Request `https://docs.python.org/3.14/library/stdtypes.html` →
**HTTP 200**, 1 redirect, final URL `https://docs.python.org/3.14/builtins/stdtypes.html`,
**774910 bytes**, sha256
`5abdd8b9ceeda2c3e94d8f95e32d9853d6f35d35844514727aa440cac98eda42`. Requesting the final
URL directly gives HTTP 200, 774910 bytes, the same sha256 (no redirect).

**The filed capture reproduces byte-for-byte.** `census/round-88/srcs/str-splitlines.html`
hashes to the same `5abdd8b9…eda42` at the same 774910 bytes — the filed capture is a
faithful copy of the live page, not a re-render.

**Located quote (18 words), verified against the capture.**
> "This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines."

Verified with the **lane's own recipe** (`census/round-55/wave/w1/S55scribe01/receipts/
verify_quotes.py`: strip `<script>`/`<style>`, strip tags with the **empty** replacement,
`html.unescape`, collapse whitespace runs). Under that recipe the quote **is** a verbatim
substring of the capture and `len(q.split()) == 18`, matching the row's stated count.

**Rendered text at the anchor** (tag-stripped, whitespace-collapsed):
> `str.splitlines(keepends=False)¶ Return a list of the lines in the string, breaking at line boundaries. Line breaks are not included in the resulting list unless keepends is given and true. This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines.`

**The boundary table, as rendered in the capture** — the row's actual scope:
> `Representation Description \n Line Feed \r Carriage Return \r\n Carriage Return + Line Feed \v or \x0b Line Tabulation \f or \x0c Form Feed \x1c File Separator \x1d Group Separator \x1e Record Separator \x85 Next Line (C1 Control Code) \u2028 Line Separator \u2029 Paragraph Separator Changed in version 3.2: \v and \f added to list of line boundaries.`

That is LF, CR, CRLF, VT, FF, FS/GS/RS, NEL, LS, PS — the ten distinct characters a
`str.splitlines()` reader breaks on. **This is the source C2 rests on, opened live, and it
grounds the rule exactly.**

---

## 2. Duplicate-URL / duplicate-scope check (the registry's W04 concern)

The `stdtypes.html` family already carries **five** rows before this seat's candidate:

| row | URL | scope | distinct from the splitlines boundary list? |
|---|---|---|---|
| S061 | `/3/library/stdtypes.html#str.lstrip` | strip-character semantics vs prefix removal | yes — a different method |
| S105 | `/3/builtins/stdtypes.html` | why ordinary equality is insufficient for typed counter expectations (the `bool` type) | yes — a different type |
| S266 / S267 | `/3/builtins/stdtypes.html#common-sequence-operations` | tuple equality underlying R45 register identity | yes — a different section |
| **S278** | `/3.12/library/stdtypes.html#str.splitlines` | the line-boundary set the frozen C1 v4 counter's hidden-line numbering must agree with (the r54 sentinel S1 mechanism) | **NO — same fact** |
| **S348** | `/3.14/builtins/stdtypes.html#str.splitlines` | which byte sequences a `str.splitlines()` reader treats as line boundaries | **NO — same fact** |

**The finding the seat-spec asks for ("state whether this row's scope is distinct and cite
the existing rows' scopes") has a sharper answer than "distinct": S278, S348 and this
seat's candidate are the SAME DOCUMENTED FACT.** I re-fetched both captures and the rendered
boundary tables are **byte-identical**, and the r55 located-quote file
`census/round-55/sources/s278-located-quote.txt` records the same 18-word sentence that
S348's row quotes. S278 (3.12) and S348 (3.14) differ only in the version segment and the
`/library/` → `/builtins/` 301.

**The scopes are distinct only in the CONSUMER, not in the fact.** S278 grounds the set for
a *hidden-line numbering* that must agree with an LF-only counter; S348 grounds it for an
*escaping rule* that must keep a record cell one physical line. Two different decisions,
one identical documented boundary list.

**This seat proposes no supersession and does not edit `corpus/SOURCES.md`** — under
contract rule 2 a correction is a new row whose `teaches` opens `supersedes S0NN —`, and
under rule 4 "Expansion is knowledge, not rows … there is no row quota". Whether the
registry keeps one row for this page-content (S278) or one per version (S278/S348), and
whether a new row is warranted at all, is the L1's call. **The overlap is reported here so
the L1 does not add a third row for the same fact without knowing about the first two.**

Registry-wide census (the contract's own commands, run on the live `corpus/SOURCES.md`):
272 rows; **0** malformed rows (all NF=13); tiers A=259 B=10 C=3; statuses mined=227
queued=14 rejected=31; **0** duplicate ids; **0** enum violations; **0** tier inflation;
**0** `mined` rows with a missing `used-by` path.

---

## 3. The one additional reject this seat proposes

**S351 — Python 3.14 `pathlib`** — https://docs.python.org/3.14/library/pathlib.html#pathlib.Path.write_text
— tier A, `docs`, status `rejected`, used-by `—`.

> **quote (10 words):** "The optional parameters have the same meaning as in open()."

**Live access record.** HTTP 200, 0 redirects, 272107 bytes, sha256
`c5f1f5268f7887a38c2747dbb3ca1541ce6c55ec4bf04359d59ef8f66134a165`. Quote verified as a
verbatim substring under the lane recipe, `len(q.split()) == 10`.

**Reason.** The page states that `Path.write_text`'s optional parameters inherit `open()`'s
meaning and that the `newline` parameter was added in 3.10. It says nothing about how a
record *cell* must be escaped, and **the tool under test never uses pathlib**:
`grep -c "pathlib\|Path(" tools/souji-record-agreement.py` → **0**; its imports are
argparse, base64, binascii, hashlib, json, os, re, subprocess, sys. The enforceable one-line
rule is S348's boundary list plus the lane's own `_escape_text`, so this row would add
registry weight rather than a decision for this surface. The `open()` newline contract the
quote points at is already held by **S272**.

**Flip condition:** a round that must decide a record's *on-disk* newline translation —
i.e. an artifact written through `Path.write_text` whose reader splits the file's bytes,
where `open()`'s newline semantics rather than the escape rule would decide the outcome.

**Screened but NOT filed (counted, not admitted):** the `base64` module docs (HTTP 200,
61731 bytes, sha256 `09b0682d…43f984`) — already held as **S349**, rejected, with a flip
condition, and the filed capture is byte-identical to this live fetch; **no new row, this
would duplicate S349.** The `subprocess` docs (HTTP 200, 207155 bytes, sha256
`2633e602…369a`) — already held twice as **S067** and **S074**; the `capture_output` clause
C2 leans on ("If capture_output is true, stdout and stderr will be captured.", 10 words,
verified) is transport plumbing the lane's own code already fixes.

---

## 4. FINDING (reproducer-backed): the escape set is narrower than the frozen C2 wording's "C0/C1 controls"

### The wording, quoted

`census/round-88/preregistration.txt:84-85` (C2, stated wording):
> "`_escape_text` first (backslash doubled; LF/TAB/CR, **C0/C1 controls**, NEL and U+2028/U+2029 printed as escapes — the boundaries a `str.splitlines()` reader breaks on, S348)"

`census/round-88/preregistration.txt:89`: "a control byte / NEL / U+2028 is never emitted raw".

`.ufo/waves/round-88/claims.json` (C2): "a control byte / NEL / U+2028 is never emitted raw".

### What the tool actually escapes

`tools/souji-record-agreement.py:173-197`, `_escape_text`. Sweeping every byte value
0x00–0xFF through it and asking which values come back **unchanged**:

- escaped: `\` `\\`, LF, TAB, CR, **every** C0 control (o < 0x20), DEL (0x7F), **NEL (0x85)**
  only, LS (0x2028), PS (0x2029);
- **left raw: 31 of the 32 C1 controls** — 0x80, 0x81, 0x82, 0x83, 0x84, 0x86–0x9F.
  (0x85 is the one C1 control the tool escapes.)

**The set of boundaries S348 names is fully covered** — I checked each of the ten against
`_escape_text`: LF→`\n`, CR→`\r`, VT→`\x0b`, FF→`\x0c`, FS→`\x1c`, GS→`\x1d`, RS→`\x1e`,
NEL→`\x85`, LS→`\u2028`, PS→`\u2029`. **All ten are escaped.** The tool's rule and the
source it rests on agree exactly.

**But the frozen wording says "C0/C1 controls", and 31 C1 controls are not escaped.**

### The reproducer

`.ufo/waves/round-88/w1/S88ScoutSources/repro-c1-control.py` (receipt:
`receipts/repro-c1-control.txt`). It drives the tool's **own public path** — a tool copy
beside a fake writer, exactly as `tests/fixtures/r88-k4-flagfail.py` does — with a writer
whose `git()` stderr carries SOH (0x01), NEL (0x85), U+2028 and **U+009F** (a C1 control
that is *not* a `str.splitlines` boundary). Output:

```
K4 rows: 1
detail repr: 'the index-flag read failed (fatal: \\x01 \\\\x85 \\u2028 \x9f marker\\n); tracked bytes are unverified'
raw SOH  in output: False   (escaped as \x01: True)
raw NEL  in output: False   (escaped as \x85: True)
raw U+2028 in output: False   (escaped as \u2028: True)
raw U+009F (C1, NOT a splitlines boundary) in output: True
detail splitlines count: 1  -> the cell is still ONE physical line
```

### What this does and does not falsify

**It does NOT falsify the frozen kill rule.** The kill rule
(`preregistration.txt`, C2) fails the claim on "any raw **SOH / NEL / U+2028** byte in the
tool's output". All three are escaped (`\x01`, `\x85`, `\u2028`); the fixture's KFF4 case
asserts exactly those three and passes. The record also stays **one physical line**
(`detail.splitlines count: 1`), because U+009F is not a `splitlines` boundary — the
one-line property the claim actually asserts is intact.

**It DOES narrow the stated wording.** "C0/C1 controls" and "a control byte … is never
emitted raw" are both broader than what `_escape_text` does and broader than what S348
grounds. S348's list contains exactly **one** C1 control (NEL, 0x85) — the other 31 are
not boundaries and the doc says nothing about them. Under Amendment 59 a claim verifies only
if no artifact produced by this round's own wave falsifies its **stated wording**; this
reproducer is such an artifact, and the wording it contradicts is the escape-set sentence,
not the one-line sentence.

**Suggested narrowing for `plans/round-88.md` (the L1 owns the file; this seat edits nothing):**
replace "C0/C1 controls" with the set S348 actually names — "LF/TAB/CR, the C0 controls, DEL,
NEL and LS/PS" — and scope "a control byte is never emitted raw" to "a control byte that is
a `str.splitlines()` boundary is never emitted raw", or state the residual explicitly the
way the r87 lesson already does ("a control byte outside the escaped set can still land raw
in a record the lane does not own" — `corpus/knowledge/one-escaped-diagnostic-line.md`).

Note the *knowledge entry* filed at P already states the correct, narrower rule ("the C0
controls, DEL, NEL and LS/PS"); it is the **preregistration and claims.json wording** that
is over-broad. That is a wording defect, not a tool defect.

### Severity read

Low, and *not* a claim kill: no frozen kill-rule arm fires, the ONE-physical-line property
holds, the escape set is exactly complete against its source S348, and the raw byte that
survives (U+009F) is not a record separator for any reader this lane uses. The finding
matters because the frozen wording over-claims relative to both the source and the code, and
this round's own artifact demonstrates the gap.

---

## 5. Other measurements this seat took (all re-derived, none a finding)

- **All twelve instrument hashes named in the seat brief match the frozen list exactly** —
  `c1-false-rows.tsv` `b710e368…`, `c1-mutants.json` `baec8026…`, `c1-mutants-dead.json`
  `e7963787…`, `c1-false-row-harness.py` `1ae0cd39…`, `c1-clause-battery.py` `6842ca47…`,
  `c1-pointer-counter.py` `fd0a8e24…` (UNCHANGED r87 bytes), `c1-items.tsv` `ce80195d…`
  (UNCHANGED r87 bytes), `r88-k4-flagfail.py` `aa79133a…`,
  `tools/souji-record-agreement.py` `c0604b4a…`, `controls/c2-before-tool.py` `e1b00e8a…`,
  `controls/c2-before.txt` `28e5ad68…`, `controls/c1-before.txt` `ce1352d2…`. **No
  mismatch.**
- **`_one_line` behaviour re-measured** (via the module, no lane file touched): empty input
  → `no stderr`; a three-line traceback → one physical line with `\n` escapes and no raw
  newline; a 400-character `AttributeError: …` → exactly 200 characters, keeps
  `AttributeError`, head-100 + `…` + tail-99; a 200-char excerpt is 100 + 1 + 99.
- **Truncation does not split an escape sequence** in the sampled offsets (0 of 60 head cuts
  landed inside an escape), though a cut can leave a **dangling trailing backslash** at the
  head boundary (offset 99). This does not break the one-line property and is not a claim
  term; noted for completeness only.
- **`_escape_text` is injective in the backslash-first sense** the docstring claims: `\` is
  doubled before any other mapping, so `\`+`n` and a real LF cannot share a spelling.

## 6. Minor registry observation (not this seat's to fix)

**S349's filed quote word count is off by one.** Its row and the knowledge file's Gate both
say "(16 words)"; the quote "Decode the Base64 encoded bytes-like object or ASCII string s
and return the decoded bytes." has **15** words by `len(q.split())` — the counting method
the lane's own `verify_quotes.py` uses. I swept every quoted word count in the registry
(3 rows carry one): **S349 is the only mismatch.** The quote itself is present verbatim in
the capture and is 15 words. This is a `teaches`-cell correction, so under contract rule 2
it is a new row (`supersedes S349 —`), not an in-place edit. **Reported, not fixed** — this
seat writes only its own seat dir.

## 7. Scratch and residue

Scratch root `/fast/scratch/hyaku/souji-r88/S88ScoutSources/` — **deleted before yield**
(`trap 'rm -rf -- "$S"' EXIT`). No fixture repo was created (this seat writes no code that
needs one; the reproducer's git repo is created *inside* its own `--work` dir under the
scratch root and removed with it). **Nothing left behind.** No `git`/`jj` mutation, no
commit, no push, no fleet-root or sibling-lane file touched, no `MANIFEST.json`,
`.ufo/state/*`, `.scratch/*` or `.ufo/watchdog.log` edit. The only writes are
`.ufo/waves/round-88/w1/S88ScoutSources/` (this seat's own directory: `candidates.md`,
`repro-c1-control.py`, `receipts/`) and this report file.
