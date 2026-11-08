# R91ExecC2Tool — C2 boundary repair, unit level + regression surface

Seat: R91ExecC2Tool (executor, souji round 91, lane `souji-shokunin`).
Scope: read the lane, write only `.ufo/waves/round-91/w1/R91ExecC2Tool/` and this report. No commit, no git/jj
mutation, no fleet/lane file edited, no frozen instrument copied or changed.

## VERDICT

- The named r90 defect is repaired on **valid UTF-8** payloads: a 1137-row sweep (lengths 201-260, 1/2/3/4-octet
  characters at every cut position) produces **0** surrogate escapes, **0** `\x85` spellings, **0** `\u0085`
  spellings, **0** cut bytes that are a continuation of a declared sequence, and a raw window never above **202**
  octets (max 202, min 198).
- The before/after pair for the claim's own payload (`101p + C2 85 + 98s`, 201 bytes) is reproduced: r90 prints the
  orphan `\x85`, the filed tool prints neither spelling.
- Raw-byte spellings survive: a lone `0x85`, an invalid `0xC2`/`0xE2 0x82` lead at the head cut and a `0xFF` at the
  tail cut all keep their `\xNN` spelling; a whole `C2 85` retained in the window spells `\u0085`.
- r87 K4 12-row regression on the filed tool: `SUMMARY rows=12 mismatches=0 errors=0`, `EXIT=0`.
- Tool diff: exactly **one** hunk, `@@ -213,22 +213,73 @@`, **+59/-8**; everything outside it is byte-identical.
  Hunk inventory: 3 boundary helpers (+43 with separators), 1 docstring block (+7), 1 body refactor (+9/-8).
  **UNEXPECTED: none.**
- **One sentence of the C2 claim is FALSIFIED as worded** on a payload that carries an invalid lead octet before the
  tail cut: `_cut_tail` advances by the *declared* sequence length instead of to the end of the continuation run, so
  the tail can start **inside** a later valid sequence and print its continuation as `\x85` — the exact r90 defect.
  Reproducer: `.ufo/waves/round-91/w1/R91ExecC2Tool/repro-cut-tail-split.txt` (see `FALSIFIES-WORDING` below).
  The three C2 predicates are NOT affected by this payload; only the mechanism sentence is.

## Instruments read (sha256 verified in-run)

| path | sha256 | matches prereg |
|---|---|---|
| `tools/souji-record-agreement.py` | `21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c` | yes |
| `census/round-91/controls/c2-before-tool.py` | `d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561` | yes |
| `census/round-87/c2-k4-counter.py` | `4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e` | (instrument) |
| `tests/fixtures/r91-k4-flagfail.py` | `f815abbc8a6c1fa00ed55db196dc14799b29e3e54e95d505cb4cce4e3c980478` | yes |

Corroboration (read-only): `git show 681f6c72b242d410d0e8654efadb2a1553fb111d:tools/souji-record-agreement.py |
sha256sum` = `d095b52f…` = the control file, i.e. the before arm really is the lane-base r90 tool. `git status
--porcelain` for `tools/` and the control path was empty.

Environment: Python 3.14.8, `python3 -B`, driver also sets `sys.dont_write_bytecode = True`. `tools/__pycache__`
kept its four pre-existing `.pyc` files with unchanged mtimes (11:39:04 for `souji-record-agreement.cpython-314.pyc`
vs. my runs at 13:22-13:24) — the imports wrote nothing into the lane.

## 1. Cut matrix (payload -> cut -> cell -> length -> orphan check)

Driver: `.ufo/waves/round-91/w1/R91ExecC2Tool/exec-c2-tool.py` (imports the filed tool via `importlib`, exposes
`_one_line_bytes`, `_cut_head`, `_cut_tail`, `_utf8_seq_need`).
Run log: `matrix-run.txt` (EXIT=0). Data: `matrix.tsv` (1152 rows + header), `matrix.json`.

Families (payloads 201-260 bytes; cuts `h=100`, `t=L-99`; wide characters `A`/`U+0085`(C2 85)/`€`(E2 82 AC)/
`𝄞`(F0 9D 84 9E)):

| family | rows | max window octets | cell UTF-8 max | surrogate rows | `\x85` rows | `\u0085` rows | head SPLIT | tail SPLIT | recon mismatch |
|---|---|---|---|---|---|---|---|---|---|
| head-adjacent (1-octet at 99 / 100) | 120 | 202 | 202 | 0 | 0 | 0 | 0 | 0 | 0 |
| head-straddle (split 1..w-1 at 100) | 360 | 201 | 201 | 0 | 0 | 0 | 0 | 0 | 0 |
| tail-adjacent (1-octet at t-1 / t) | 120 | 202 | 202 | 0 | 0 | 0 | 0 | 0 | 0 |
| tail-straddle (split 1..w-1 at t) | 360 | 201 | 201 | 0 | 0 | 0 | 0 | 0 | 0 |
| both-straddle | 177 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 |
| **valid-payload total** | **1137** | **202** | **202** | **0** | **0** | **0** | **0** | **0** | **0** |
| preserve (hand) | 6 | 202 | 208 | 6 | 3 | 0 | 0 | 0 | 0 |
| whole (hand) | 3 | 202 | 206 | 0 | 0 | 1 | 0 | 0 | 0 |
| attack (hand) | 6 | 202 | 208 | 5 | 3 | 1 | 0 | **4** | 0 |

`reconstruction_exact` = the cell equals `_escape_text(_decode_record(raw[:h]) + "…" + _decode_record(raw[t:]))` for
the helper-returned `h,t`: 0 mismatches in 1152 rows.

"Raw byte length" is the **raw window** (`raw[:h] + ellipsis(3) + raw[t:]`): max **202**, never above. The cell's
UTF-8 length is a different quantity and can be larger only because escaping expands a byte to `\xNN`/`\uNNNN`
(max 208 in the preserve/attack rows, e.g. a 4-byte expansion of `\xff`); the claim's bound is on the raw window.

Orphan check (literal reading of the seat brief — `\x85`/`\u0085` spelled although the payload carries no
corresponding whole sequence): **0 rows** in all 1137 valid-payload rows. Retained-window reading (a `\x85` whose
`C2` lead sits in the elided middle): 0 rows in the valid families; **4 rows in the attack family** (see
`FALSIFIES-WORDING`).

Sample rows (verbatim from `matrix.tsv`, columns family/length/width/align/h/t/head_boundary/tail_boundary/
window/cell-bytes/x85/u0085):

```
head-straddle 201 2 head:lead=99:split=1    99 102 boundary boundary 201 201 0 0
head-straddle 201 3 head:lead=98:split=2    98 102 boundary boundary 200 200 0 0
head-straddle 260 4 head:lead=97:split=3    97 161 boundary boundary 199 199 0 0
tail-straddle 260 2 tail:lead=160:split=1  100 162 boundary boundary 201 201 0 0
tail-straddle 260 4 tail:lead=158:split=3  100 162 boundary boundary 201 201 0 0
both-straddle 201 2 head:lead=99:split=1|tail:lead=101:split=1 99 105 boundary boundary 198 198 0 0
```

Reading of the head column: a split at `h` backs the head off to the sequence's lead (99 / 98 / 97), so the head
keeps whole sequences only; the tail column advances past a split to the byte after the sequence.

## 2. Before / after on the claim's payload (`101p + C2 85 + 98s`, 201 bytes, sha256 `f7776ac2…`)

```
BEFORE (r90 control) t=102  window=202  x85=1  surrogates=['U+DC85']
        cell='pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp…\x85ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss'
AFTER  (filed tool)  t=103  window=201  x85=0  u0085=0  surrogates=[]
        cell='pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp…ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss'
```

Written as constructions (the `\x85` above is the four literal characters backslash x 8 5):

- before: `"p"*100 + "…" + "\\x85" + "s"*98` (203 characters, 202 raw window octets)
- after:  `"p"*100 + "…" + "s"*98` (199 characters, 201 raw window octets)

The elided middle is `C2 85` in both payloads; r90 keeps the `0x85` continuation and spells it `\x85`, the filed
tool moves the tail start to 103, drops the pair whole and prints neither spelling. Both cells were also checked in
`hand-payloads.txt`/`matrix-run.txt`; cell text is identical to `_one_line_bytes`'s own return value.

## 3. Raw-byte spelling preservation (filed tool)

| payload (210 or 201 bytes) | cut | cell fragment | expected |
|---|---|---|---|
| `a*111 + 0x85 + b*98` | t=111, `orphan-no-lead` | `…` **`\x85`** `bbbb…` | lone 0x85 keeps `\x85` |
| `a*99 + 0x85 + b*101` | h=100, `\x85` is the last kept head byte | `aaa…a` **`\x85`** `…` | lone 0x85 keeps `\x85` |
| `a*99 + 0xC2 + z*101` | h=100, next byte not a continuation | `aaa…a` **`\xc2`** `…` | invalid lead keeps `\xc2` |
| `a*98 + E2 82 + z*101` | h=100 | `aa…a` **`\xe2\x82`** `…` | truncated 3-octet lead keeps both bytes |
| `a*111 + 0xFF + b*98` | t=111 | `…` **`\xff`** `bbbb…` | invalid byte keeps `\xff` |
| `a*108 + C2 85 85 85 + b*98` | t=111, `orphan-beyond` | `…` **`\x85`** `bbbb…` | the pair's lead is elided; the surviving 0x85 is an orphan and keeps `\x85` |
| `a*111 + C2 85 + b*97` | t=111 (cut on the lead) | `…` **`\u0085`** `bbbb…` | whole character → `\u0085`, no `\x85` |
| `a*99 + C2 85 + b*100` | h backs 100→99 | `aaa…a` `…` `bbbb…` | straddling the head: whole sequence elided, neither spelling |
| `a*100 + C2 85 + b*100` | t=103 | `aaa…a` `…` `bbbb…` | wholly in the elided middle, neither spelling |

Full cells of the two classes the brief names (filed tool, verbatim):

```
# lone 0x85 at the tail cut  (a*111 + 0x85 + b*98)
cell='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa…\x85bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
# invalid 0xC2 at the head cut  (a*99 + 0xC2 + z*101)
cell='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\xc2…zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
```

Full cells and payload hex: `hand-payloads.txt`; run log `matrix-run.txt`.

## 4. r87 K4 regression + tool diff

```
$ python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py \
      --work /fast/scratch/hyaku/souji-r91/R91ExecC2Tool/k4-work
...
ROW KN3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['bad\\nname2.txt|uncommitted-path']
SUMMARY rows=12 mismatches=0 errors=0
EXIT=0
```

12 `ROW` lines, `match=yes` on every row (KH1/KH2 clean; KU1/KU2/KF1/KF2/KF3/KG1/KG2/KN1/KN3 flag and name the
forged path; KN2 header `writer_sha=70bbf1c2…` vs `appended_sha=1b8ecf32…`). Full log `k4-regression.txt`.

Diff of `census/round-91/controls/c2-before-tool.py` (700 lines) → `tools/souji-record-agreement.py` (751 lines),
saved as `tool-diff.patch`:

- one hunk only: `@@ -213,22 +213,73 @@`; `diff --unchanged` outside it: lines 1-212 of both files identical,
  old 235-700 vs new 286-751 identical → +59 / -8 net +51.
- classification (every line accounted for):
  - `+_utf8_seq_need` (9 lines) + 2 blank separators → boundary helper
  - `+_cut_head` (13 lines) + 2 blanks → boundary helper
  - `+_cut_tail` (15 lines) + 2 blanks → boundary helper
  - `_one_line_bytes` docstring: -1 / +7 (the r91 paragraph; the old final docstring line is replaced)
  - `_one_line_bytes` body: -7 / +9 (`if len(raw) <= limit` early return identical in behaviour; `h = _cut_head(...)`,
    `t = _cut_tail(...)`, `if t < h: t = h`, then the same `_escape_text(_decode_record(...))` composition)
  - **UNEXPECTED: none** (no other function, constant or import touched; `_escape_record`, `_escape_text`,
    `_decode_record`, `_stderr_tail`, `git*`, `Report` all byte-identical).

Behavioural equivalence outside the repaired path holds: for every payload with no split and no orphan the filed
tool's window equals r90's (`h=100`, `t=L-99`), and the `len(raw) <= limit` branch returns the same value.

## FALSIFIES-WORDING

Exact sentence (prereg C2 CLAIM):

> "The filed tool moves BOTH cuts to sequence boundaries before decoding (`_cut_head` backs off a valid partial
> sequence; `_cut_tail` advances past continuations whose lead the middle elided; a continuation byte with no lead
> stays and keeps its `\xNN` spelling), grounded on S354 (RFC 3629 §3: a sequence is an initial octet plus its
> continuation octets)."

What falsifies it: `_cut_tail` does **not** validate the continuation bytes it advances over (unlike `_cut_head`,
which does). It takes the declared length of the first lead octet it finds and returns `lead_index + need`, even when
the continuation run before the cut is *shorter* than `need - 1` (i.e. the lead's sequence is invalid/truncated). The
returned index can therefore land **inside** a later, valid sequence, and that sequence's continuation is printed
with the raw byte's spelling — the r90 defect class, from a different entry.

Reproducer (executable, prints the cells; lane read-only, no bytecode):
`.ufo/waves/round-91/w1/R91ExecC2Tool/repro-cut-tail-split.py`, output
`.ufo/waves/round-91/w1/R91ExecC2Tool/repro-cut-tail-split.txt`, payloads in full in `hand-payloads.txt`
(family `attack`, rows 1-2).

```
A = b"a"*110 + b"\xf0" + b"\x80" + b"a" + b"\xc2\x85" + b"b"*95      # 210 bytes, sha256 f639d877…
    bytes[108:116] = 61 61 f0 80 61 c2 85 62
    head_cut=100  tail_cut=114  raw[tail_cut]=0x85  window_octets=199  tail_boundary=SPLIT
    cell='…' + '\x85' + 'bbbb…'        ← U+0085's lead C2 sits in the elided middle
B = b"a"*110 + b"\xf0" + b"\x80" + b"a" + b"b" + b"\x85" + b"b"*95   # 210 bytes, sha256 b53080a7…
    cell='…' + '\x85' + 'bbbb…'        ← the 0x85 here is a RAW byte, no lead at all
CELLS_EQUAL=True
```

So: (a) the tail cut is not at a sequence boundary (`raw[114]` is `U+0085`'s continuation), (b) `_cut_tail` did **not**
advance past a continuation whose lead the middle elided, and (c) two materially different delegated failures — a
stderr carrying the UTF-8 encoding of U+0085 versus a stderr carrying a raw `0x85` byte — share one cell, which is
the collision the r90 sentence says the repair removes. The same over-advance splits 3- and 4-octet characters
(`attack` rows 3-4: cells show `\x82\xac` and `\x9d\x84\x9e`; row 5 shows the same with a truncated `E2 80` lead).

Condition and scope: the payload must carry an **invalid** lead (a truncated `F0 80` / `E2 80`) immediately before the
cut. Every 1137 valid-UTF-8 row in the sweep cuts at a boundary with no orphan spelling, so the repair is exact on
valid payloads and the r91 fixture's KFF11 case (valid 201-byte payload) is unaffected; predicate (a) 15/15, (b)
3/3, (c) 12/0/0 are not reached by this input. I did not modify the frozen tool or fixture. Suggested L1 amendments
(Amendment 59: narrow, never repair silently): either
(i) narrow the sentence to payloads whose bytes are valid UTF-8 around the cuts (with this payload named as an
unrowed residual, like STATED LIMITS (iii)), or
(ii) record the defect and fix `_cut_tail` to require, as `_cut_head` already does, that the whole declared sequence
`raw[i-1 : i-1+need]` lies within the payload and is made of continuation octets (`end <= len(raw) and
all(0x80 <= b <= 0xBF for b in raw[i:end])`) before moving the cut — after that, the 6 attack rows change cell and
the valid sweep should stay at 0 splits.

## Observations (no wording impact, recorded for the L1)

1. `_cut_head` is annotated `-> str` but returns an `int` (line 227 of the filed tool); cosmetic, no behaviour.
2. `_utf8_seq_need` treats `0xC0`/`0xC1` (overlong) and `0xF5`-`0xF7` (beyond U+10FFFF) as initial octets, which
   RFC 3629 §3 (the claim's source S354) does not. Consequence is bounded: such a lead makes `_cut_tail` elide two or
   three bytes it calls part of the sequence; nothing is printed with an orphan spelling, so no cell collision is
   created. Not a falsifier, but it is the same non-validating surface as the finding above and would be closed by
   the same fix.
3. `_escape_text`'s `\u0085` vs `\x85` injectivity (r89/r90) is intact in every retained-whole-sequence row: cell
   `\u0085` appears exactly once (whole family), and the matrix's 1152 rows never contain both spellings.

## Evidence index (all under `.ufo/waves/round-91/w1/R91ExecC2Tool/`)

- `exec-c2-tool.py` — matrix + named-payload + preservation driver (imports the filed tool)
- `matrix.tsv`, `matrix.json` — 1152 rows (payload sha256, cuts, boundary class, window octets, cell, orphan counts)
- `matrix-run.txt` — driver output, EXIT=0
- `hand-payloads.txt` — hand-built payload hex + cells (preserve/whole/attack)
- `repro-cut-tail-split.py`, `repro-cut-tail-split.txt` — the FALSIFIES-WORDING reproducer
- `k4-regression.txt` — r87 12-row counter on the filed tool
- `tool-diff.patch` — `diff -u` before→after (one hunk)

Scratch `/fast/scratch/hyaku/souji-r91/R91ExecC2Tool/` was created with `mkdir -p` and deleted after the runs (the
counter's clone was removed by the counter itself). `/tmp` unused. No tool install or upgrade was needed; no pacman,
uv, npx or cargo invocation. No git/jj mutation anywhere; no `$v`/`git -C` call with an unset variable.
