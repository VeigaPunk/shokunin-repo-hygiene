# S88Scribe — souji round 88, wave 1 (scribe)

Seat: S88Scribe. Lane: souji-shokunin. Lane base `7defe9c5fee3df07e403666bdeccfb88428ef729`;
read tip `git rev-parse refs/heads/master` = `72edae4045cfa2b8c74f176bf690d7583bcceecb`
(`72edae40`, the L1's C2 docstring repair, landed DURING this seat's run — see F7).
Instrument commit P = `e60ea25f6dc6d988bbdd713a2d00718f5915e29d`; prereg F = `f74092b2`.
Interpreter: python 3.14.8; git 2.56.0-1; host Arch x64.

I am a leaf member: no subagent dispatch. I committed nothing, pushed nothing, and touched no
git/jj state, no fleet or sibling-lane file, no MANIFEST.json, no `.ufo/state/*`, no `.scratch/*`,
no `.ufo/watchdog.log`. Every byte I wrote is under `.ufo/waves/round-88/w1/S88Scribe/` plus this
report file.

## Deliverables (all drafts, all for SoujiR88 to integrate)

| file | what it is |
|---|---|
| `.ufo/waves/round-88/w1/S88Scribe/draft-s348-gate-row.md` | the S348 `## Gate` row in the registry schema of the newest corpus/SOURCES.md rows, with a cell-by-cell audit and the deltas the L1 must decide |
| `.ufo/waves/round-88/w1/S88Scribe/draft-knowledge-one-escaped-diagnostic-line.md` | the 35-line knowledge section for corpus/knowledge/ (at the seat's <=35 bound), with the landed entry listed alongside for the diff |
| `.ufo/waves/round-88/w1/S88Scribe/draft-quality-criterion-Q164.md` | the next-free-Q QUALITY criterion (Q164) with its test cell and lesson pointer |
| `.ufo/waves/round-88/w1/S88Scribe/quote-verification-receipt.txt` | the quote-verification receipt: capture lines, quote, byte-check command + output, word counts |

## The single most important thing for the L1 to know

**S348, Q163 and `corpus/knowledge/one-escaped-diagnostic-line.md` are already in the lane.** They
landed at commit `e60ea25f` (P) — the instruments commit, before the preregistration F. The lesson
`corpus/lessons/round-88.md` is also already written (it is UNTRACKED in git; the L1 has not
committed it). So my seat is not drafting three new artifacts from nothing: it is auditing three
artifacts that already exist and correcting what is wrong in them. My drafts are the corrected
versions, plus the evidence for each correction.

## Findings

### F1 — the round's provenance paragraph claims a check the bytes do not support

`corpus/SOURCES.md:316` (the Round-88 source-opening paragraph) says of S348:

> the quote was checked byte-for-byte against the capture.

The quote is **not** a byte-substring of the capture. Measured:

```
python3 -B -c "import io;q='This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines.';print(q.encode() in io.open('census/round-88/srcs/str-splitlines.html','rb').read())"
-> False
```

The capture is HTML: the sentence spans capture lines 2806-2807 with the anchor's `<a>`/`<span>`
markup inline, so only the RENDERED text (tags stripped, whitespace collapsed) carries the quote.
The verifiable statement is `True 18` against the rendered capture — which is what the receipt
records. This is the lane's own r50 mistake class ("a quote-count command whose tag-stripping
substitutes a space for every removed tag turns a verbatim displayed quote into a non-substring"),
and the r55 recipe (`census/round-55/sources/s278-located-quote.txt`) already states the correct
method: strip script/style, strip tags, unescape, collapse whitespace.

**Scope note:** the SOURCES row's own cells are honest — its `anchor` cell says "(rendered quote)".
The overclaim is in the provenance paragraph, one line above the row, not in the row. One sentence
to fix. S349 has the same property (raw containment `False`, rendered `True 15`).

### F2 — S349's word count is 15, not 16 — **FIXED IN THE WORKING TREE, uncommitted**

`corpus/SOURCES.md:310` (S349's `anchor` cell) and `corpus/lessons/round-88.md` both say the
quote is "(16 words)". The lane's own count command gives **15**:

```
python3 -B -c "import re,io;t=re.sub(r'<[^>]+>','',io.open('census/round-88/srcs/base64.html',encoding='utf-8').read());t=re.sub(r'\s+',' ',t);s='Decode the Base64 encoded bytes-like object or ASCII string s and return the decoded bytes.';print(s in t, len(s.split()))"
-> True 15
```

Under either tokenizer it is not 16 by the lane's convention: `len(s.split())` = 15 (the convention
the r49 erratum's command uses), `len(re.findall(r'\w+', s))` = 16 — the filed number is a `\w+`
count, and `\w+` counts `bytes-like` as two words where the lane's `.split()` counts it as one.
This is the r49 S271 erratum class exactly ("17 words" for a 16-word quote), and the r45 Gate
erratum before it. S349 is `rejected`, so no knowledge rests on the count, but the number is in a
filed cell and in the lesson. **S348's 18-word count is correct** (verified `True 18`).

### F3 — S348's `teaches` cell is not carried by S348's own quote

S348's `teaches` cell asserts a boundary LIST:

> the boundary list adds VT, FF, FS/GS/RS, NEL and LS/PS to LF/CR/CRLF …

but the row's quote is only:

> This method splits on the following line boundaries. In particular, the boundaries are a superset of universal newlines.

which names **no** boundary beyond universal newlines. The six extra boundaries live in the
capture's TABLE (capture lines 2808-2849), not in the quoted paragraph. The `teaches` cell is true
of the page; it is not what the row's own quote locates. The lane's precedent for exactly this
class is r40 wave-2 (S255-S257 superseded quote attributions) and the r50 quote row.

Two one-cell closures, both in `draft-s348-gate-row.md` as D1:
- **(a) widen the quote** to the 25-word table quote that does carry the boundaries —
  `\v or \x0b Line Tabulation \f or \x0c Form Feed \x1c File Separator \x1d Group Separator \x1e
  Record Separator \x85 Next Line (C1 Control Code)` — verified `True 25` against the r88 capture.
  This is the r55 S278 receipt's own third quote, so it is the lane's model, and it sits exactly on
  the ≤25 bound.
- **(b) narrow `teaches`** to what the 18-word quote carries and point the list at the table.

I recommend (a). The claim's load-bearing fact IS the six extra boundaries.

### F4 — Q161's "keeps the tail" clause contradicts the lane's own bytes; Q164 is the correction

The seat asked for one criterion in the lane's numbering style. The next free Q is **Q164**
(`corpus/QUALITY.md` tops out at Q163; `Q164` occurs nowhere in the file).

While drafting it I found that Q161's second clause is stale. Q161 says a delegated detail
"prints that tail, bounded, with a leading ellipsis when the line itself is cut", and the tool's
own `_stderr_tail` docstring (`tools/souji-record-agreement.py:254`) repeats it. But the code has
kept BOTH ends since the r87 wave repair:

| revision | cut expression | both ends? |
|---|---|---|
| `6e502c5c` | `tail = "…" + tail[-(limit - 1):]` | no |
| `7defe9c5` (lane base) | `tail = tail[:head] + "…" + tail[-keep:]` | **yes** |
| `89d36922` | `tail = tail[:head] + "…" + tail[-keep:]` | **yes** |
| `749c7829` (Q161 filed here) | `tail = tail[:head] + "…" + tail[-keep:]` | **yes** |
| `HEAD` `486826df` | `tail = tail[:head] + "…" + tail[-keep:]` | **yes** |

Q161 was filed at `749c7829` describing a leading-ellipsis tail-only cut while the bytes in that
same commit kept both ends. Q163 (already landed) states the both-ends rule correctly but says
"Extends Q161 and Q159 (they stand)" — Q161's tail-only clause does not stand.

My drafted Q164 therefore extends Q163 and Q159 and **corrects that one clause of Q161 by naming
it**, per the `corpus/QUALITY.md` header rule ("a criterion is superseded by a new row that names
the row it replaces, never rewritten"). Its content is the seat's ask: one escaped line, keeps the
head, a tail-only excerpt that drops the type name is a defect, the `splitlines()` boundary set
(S348), and why the escape is on the text and not only on the path.

The stale **docstring** in `tools/souji-record-agreement.py:254` is a code comment in a file whose
bytes C2's kill rule freezes (changing it changes the tool's sha256 and invalidates the round's
after receipts). I did not touch it; the L1 should route it as it sees fit.

### F5 — a scope check I could not close: S278 vs S348

S278 (r55) holds the same page family, the same anchor `#str.splitlines`, the same 18-word sentence
(S278's copy lacks the trailing full stop), and its used-by entry `corpus/knowledge/splitlines-line-model.md`
lists the identical boundary set. S348's scope is narrower and its used-by is a different entry, so
it is not a bare duplicate — but the lane's duplicate-URL detector is blind to this pair, because
the version path differs (`/3.12/library/` vs `/3.14/builtins/`): **neither S348 nor S278 has a
single W04 line** in `census/round-88/records/sources-census-after.txt` (the only stdtypes-family
warnings are S266/S267 at `docs.python.org/3/builtins/stdtypes.html`). The Round-88 Gate's
duplicate-URL note names S061 and S105 and does not mention S278. I verified the 18-word sentence
and the 25-word table quote are present in the r55 (3.12) capture too, so the quote is a page fact,
not a 3.14-specific wording. The L1 should decide: scope-narrowing row on S278 (the r40 wave-2
pattern) or an independent admit.

### F7 — the tool's bytes changed mid-round; the lesson still cites the pre-change hash

**This is a race I observed, not a defect the L1 planted.** The seat brief listed
`tools/souji-record-agreement.py` at `c0604b4abf10a45dfcf6eb9f7bb2ad8efb805321c24677e45a192e9a73e4fdef`.
At the start of my run the tool measured exactly that. Mid-run, the L1 committed `72edae40`
("round-88: C2 docstring names the escape set it has (C0/DEL/NEL/LS/PS), receipts re-run on the new
bytes"), and the tool now measures **`3e1fc0307715c69ee6218c665b4e727f74eb47a7341ea45125ae741dd95ca2bb`**.

The change is a **docstring-only** edit to `_one_line` (the diff touches one `"""` block and nothing
else — verified by reading the full diff of `72edae40` on the file). The L1 correctly re-ran both
affected receipts on the new bytes:
`census/round-88/records/c2-after.txt` and `census/round-88/records/c2-k4-regression.txt` now carry
the `3e1fc030…` digest in their header lines, and the verdicts are unchanged
(`SUMMARY cases=7 tool_pass=7 before_pass=3`, EXIT 0; `SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0).

**The defect that survives: `corpus/lessons/round-88.md` (untracked, the L1's file) still cites the
PRE-change hash at line 46-47:**

> tool under test `tools/souji-record-agreement.py` sha256 `c0604b4a…`

`c0604b4a…` is no longer the tool's digest at the tip. The lesson is the round's public record of
what was measured; a reader who re-measures the "tool under test" against the lesson's digest gets a
mismatch. The lesson has no other stale digest — `aa79133a…` (fixture), `e1b00e8a…` (before bytes)
and `fd0a8e24…` (the r87 counter) all still match. This is a one-cell fix in the L1's own file.

I re-measured EVERY finding in this report at the new tip `72edae40` after the change: F1, F2, F3,
F4 and F5 all still hold, and the escape/behaviour measurements are unchanged (all eleven boundaries
still escape to one `splitlines()` element; `_one_line` on a 396-char `AttributeError:` line still
returns 200 chars beginning with the type name; `_one_line("")` still returns `no stderr`).

### F6 — what I checked and found clean

- **Instrument hashes.** I re-measured the C2 and C1 hashes named in my seat brief. All match
  (the tool's own digest moved after my run started — F7 — so I list it separately):
  `census/round-88/c1-false-rows.tsv` `b710e368…a68c3`, `c1-mutants.json` `baec8026…cec9c`,
  `c1-mutants-dead.json` `e7963787…15281`, `c1-false-row-harness.py` `1ae0cd39…14042b`,
  `c1-clause-battery.py` `6842ca47…c5ff7`, `c1-pointer-counter.py` `fd0a8e24…55220b`,
  `c1-items.tsv` `ce80195d…8d2e9`, `tests/fixtures/r88-k4-flagfail.py` `aa79133a…e8335d`,
  `controls/c2-before-tool.py` `e1b00e8a…c67ccc`, `controls/c2-before.txt` `28e5ad68…33dc2`, `controls/c1-before.txt`
  `ce1352d2…b35c7f`. No mismatch.
- **Capture integrity.** `census/round-88/srcs/str-splitlines.html` sha256
  `5abdd8b9ceeda2c3e94d8f95e32d9853d6f35d35844514727aa440cac98eda42`, 774910 bytes — and a live
  re-fetch on 2026-11-08 (`curl -sSL https://docs.python.org/3.14/library/stdtypes.html`, one 301 to
  `/3.14/builtins/stdtypes.html`, HTTP 200, 774910 bytes) is **byte-identical** to the filed
  capture. `census/round-88/srcs/base64.html` sha256 `09b0682d…f984`, 61731 bytes, matches the row.
- **The claim's boundary list is the documented one.** I extracted the capture's table: LF, CR,
  CRLF, VT (`\v`/`\x0b`), FF (`\f`/`\x0c`), FS (`\x1c`), GS (`\x1d`), RS (`\x1e`), NEL (`\x85`),
  LS (`\u2028`), PS (`\u2029`) — eleven, exactly the set the prereg's wording names.
- **The escape covers all eleven.** Against the filed tool's own `_escape_text`, each of the eleven
  boundaries escapes to a string with exactly one `str.splitlines()` element. The claim's
  one-physical-line rule is not widened by anything I found.
- **The both-ends bound.** `_one_line("AttributeError: " + "x"*380)` returns exactly 200 characters,
  begins with `AttributeError`, and contains `AttributeError`. `_one_line("")` -> `"no stderr"`.
- **Registry counts.** `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` = 272 at
  HEAD and 272 at P; 270 at the lane base `7defe9c5`. The lesson's "270 -> 272" is right. W04 count
  is 87 in both the before and after receipts, as the lesson states.
- **The anchors exist.** `id="str.splitlines"` occurs exactly once in the str-splitlines capture
  (line 2801); `id="base64.b64decode"` exactly once in the base64 capture (line 17794).

## Concurrency disclosure (the L1 integrated against my findings mid-run)

The L1 was committing and editing while this seat ran. Observed, in order:

1. `72edae40` — the tool's `_one_line` docstring repaired; both C2 receipts re-run on the new bytes
   (F7).
2. The L1 then edited `corpus/SOURCES.md` and `corpus/knowledge/one-escaped-diagnostic-line.md` in the
   WORKING TREE (uncommitted): the S349 word count `16` -> `15` in BOTH files. That is exactly my
   **F2** finding, applied. `git diff` at my last check shows those two one-word changes and nothing
   else in either file.

So **F2 is already fixed in the working tree** (uncommitted as of my last check). **F1, F3, F4 and F5
remain open** — I re-verified each against the working tree: the "byte-for-byte against the capture"
phrase is still present at `corpus/SOURCES.md:316`; S348's `anchor` cell still carries the 18-word
paragraph quote (not the 25-word table quote) and still carries no capture line numbers; S348's
`teaches` cell still asserts the boundary list its own quote does not name; the tool's `_stderr_tail`
docstring still says "leading ellipsis"; and S348 still does not mention S278.

I did not make any of these edits. The L1's own file, the L1's call.

## Concurrency disclosure

The L1 (SoujiR88) committed `72edae40` into the lane while this seat was running, changing
`tools/souji-record-agreement.py`'s `_one_line` docstring and re-filing the two affected receipts on
the new bytes. I did not participate in that commit, did not modify the tool, and did not re-run the
round's counting commands. I re-measured every finding against the post-commit tip and report the
post-commit state. `corpus/lessons/round-88.md` and `plans/round-88.md` are UNTRACKED in the working
tree (the L1's in-progress files); `LOG.md` and `SCORECARD.md` show as modified. I touched none of
them.

## Out of scope, and what I did not do

- I did **not** re-run the C1 battery, the C2 fixture, or the r87 counter: those are other seats'
  evidence and the round's contract binds them. My C2 contribution is the corpus side only.
- I did **not** edit any committed file, including the three artifacts this seat was asked to
  draft. `corpus/SOURCES.md`, `corpus/QUALITY.md` and `corpus/knowledge/` are untouched by me.
- I did **not** touch `corpus/lessons/round-88.md` (untracked, L1's file).
- I did **not** chase the r87 spot-check's routed defects D4 (a rejected Gate row not written) and
  D6 (a roff line mis-citation) as new findings: they are r87 carry items and this round does not
  re-declare them. F1's sibling risk is noted above only because it sits in a file this round edits.
- I did not install or upgrade any tool: the lane's own python 3.14.8, git 2.56.0-1, `curl` and
  `grep` covered every check, so there was no tooling need to record.

## Scratch

`/fast/scratch/hyaku/souji-r88/S88Scribe/` — created, used for the live re-fetch and for scratch
scripts, and **deleted before this yield** (`rm -rf`). Nothing left behind. No `/tmp` use.
