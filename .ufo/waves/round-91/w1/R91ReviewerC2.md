# R91ReviewerC2 — C2 falsification review (souji round 91, wave w1)

Seat: `R91ReviewerC2` (reviewer). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, id `souji`.
Lane HEAD at review time: `a703bcb760ecdb22ec7df06af3059f219ebb95cf` (F — the preregistration alone).
`git status --porcelain -- tools census tests` is empty except `?? census/round-91/records/` (untracked, another
seat's); the sibling scribe/connector seats were writing `corpus/` while this review ran, and no instrument path is
touched. Every instrument below is a committed blob at `a703bcb7`, so this review is on committed bytes.

Instruments seen (sha256, all match the prereg's pins byte for byte):

```
21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c  tools/souji-record-agreement.py
d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561  census/round-91/controls/c2-before-tool.py
f815abbc8a6c1fa00ed55db196dc14799b29e3e54e95d505cb4cce4e3c980478  tests/fixtures/r91-k4-flagfail.py
24198d8e67c3fbc2197c4454fe94845d5e09ae494510f76779e9eec5e143a03a  census/round-91/variants/double-backslash-tool.py
f2f52510b26641f4134052d147b7a296af563b661f3d7b215df3bc3cb733d5c7  census/round-91/variants/raw-newline-tool.py
dfcbd0cc2fc1decd8dc8974d26bd4d8647620df2bd2c3056c7b3185d8493900f  census/round-91/variants/keep-helper-tool.py
0610c5d2ed6bd652e08106b8e7190efe05ce5a65dc0622630818f156cdeb597a  census/round-91/c2-variant-probe.py
4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e  census/round-87/c2-k4-counter.py
```

All work below ran with `cwd=/home/vgpnk/Projects/shokunin/souji-shokunin`, scratch under
`/fast/scratch/hyaku/souji-r91/R91ReviewerC2/` (deleted before this yield), receipts copied into this seat dir.
No lane file was written; no git/jj state was mutated.

---

## 1. Independent predicate re-derivation

### 1.1 Predicate (a) — the r91 fixture, after arm

```
python3 -B tests/fixtures/r91-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-91/controls/c2-before-tool.py --work <empty>
```

Receipt: `after.out`. EXIT **0**.

```
SUMMARY cases=15 tool_pass=15 before_pass=14
```

Per-case (verbatim):

```
CASE KFF1 tool=pass before=pass
CASE KFF2 tool=pass before=pass
CASE KFF3 tool=pass before=pass
CASE KFF4 tool=pass before=pass
CASE KFF5 tool=pass before=pass
CASE KFC1 tool=pass before=pass
CASE KFC2 tool=pass before=pass
CASE KFF6 tool=pass before=pass
CASE KFF7 tool=pass before=pass
CASE KFF8 tool=pass before=pass
CASE KFF9 tool=pass before=pass
CASE KFF10 tool=pass before=pass
CASE KFF11 tool=pass before=fail
CASE KFF12 tool=pass before=pass
CASE KFF13 tool=pass before=pass
```

The header line of the same receipt pins the exact bytes measured:
`tool sha256=21e5c740…`, `before sha256=d095b52f…`, `fixture sha256=f815abbc…`.

Thus `before_pass=14` is the r90 tool's own score and its **only** failed case is KFF11. The delta is exactly one
case, and it is the boundary case the claim names.

### 1.2 Predicate (b) — the variant probe, both fixtures

```
python3 -B census/round-91/c2-variant-probe.py --fixture r91 --work <empty>   # receipt probe-r91.out
python3 -B census/round-91/c2-variant-probe.py --fixture r90 --work <empty>   # receipt probe-r90.out
```

r91: EXIT **0**

```
VARIANT double-backslash fixture=r91 cases=15 pass=14 failed=KFF9 detected=yes
VARIANT keep-helper fixture=r91 cases=15 pass=14 failed=KFF13 detected=yes
VARIANT raw-newline fixture=r91 cases=15 pass=14 failed=KFF12 detected=yes
SUMMARY variants=3 fixture=r91 detected=3
```

r90: EXIT **0**

```
VARIANT double-backslash fixture=r90 cases=12 pass=12 failed=- detected=no
VARIANT keep-helper fixture=r90 cases=12 pass=12 failed=- detected=no
VARIANT raw-newline fixture=r90 cases=12 pass=12 failed=- detected=no
SUMMARY variants=3 fixture=r90 detected=0
```

Each variant is caught by exactly one new case, and each still passes the r90 fixture 12/12 — so the r91 detections
are this round's fixture, not a generic difference.

### 1.3 Predicate (c) — the r87 K4 regression

```
python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <empty>
```

Receipt: `k4.out`. EXIT **0**.

```
SUMMARY rows=12 mismatches=0 errors=0
```

(Twelve `ROW` lines, all `match=yes`, including KN2's `writer_sha=70bbf1c2a92e appended_sha=1b8ecf328ed3`.)

### 1.4 Do-nothing control (i) — the r90 tool as BOTH arms

```
python3 -B tests/fixtures/r91-k4-flagfail.py --tool census/round-91/controls/c2-before-tool.py \
  --before census/round-91/controls/c2-before-tool.py --work <empty>
```

Receipts: `ctlboth.out`, `ctlboth.err`. EXIT **1**.

```
CASE KFF11 tool=fail before=fail          (every other case pass/pass)
SUMMARY cases=15 tool_pass=14 before_pass=14
R91-FIXTURE-FAIL: the tool under test does not pass every case
```

Exactly as the prereg states: 14/14, KFF11 fails on both arms, EXIT 1.

### 1.5 Extra no-harm arm (not in the predicate) — the r90 fixture on the filed tool

```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-91/controls/c2-before-tool.py --work <empty>
```

Receipt: `r90flat.out`. EXIT **1** — but that exit is the r90 fixture's own no-delta rule, not a failing case:

```
SUMMARY cases=12 tool_pass=12 before_pass=12
R90-FIXTURE-FAIL: the do-nothing control passes as many cases (no measured delta)
```

The filed tool still passes all 12 r90 cases (the ten KFF cases plus the two controls) and the r90 tool still passes
them too: no r90 behaviour changed. Exit 1 here is expected and is not a predicate failure.

---

## 2. Byte-level boundary derivation

Reproducer: `c2-boundary-derivation.py` (this seat dir), output `boundary-derivation.out`. It reconstructs the
fixture's `nelcut` payload byte for byte, re-runs both tools' cut arithmetic, and reads the public K4 cell back
through the frozen fixture's own `make_kit`/`run_case`.

### 2.1 The payload

```
PAYLOAD len=201 sha256_sha=7a016b6613641735233bc3401bd88aeb7ee459ed91949b063132415fc632486d
INDEX 0xc2=101 0x85=102 first_s=103
BYTES[99:104]=b'xx\xc2\x85s'
```

Construction (fixture `FAKE_WRITER` `"nelcut"` mode, verbatim):
`b"fatal: nel " (11) + b"x"*90 (→ indices 11..100) + b"\xc2\x85" (101,102) + b"s"*98 (103..200)`. Length **201**.
The U+0085 encoding is `C2 85` at indices **101, 102**.

### 2.2 The r90 cut (before tool's own expression: `raw[:100] + "…".encode() + raw[-99:]`)

```
R90 head=100 keep=99 tail_start=102 window_len=202
R90 window_tail_first=85 tail_is_continuation=True
R90 decoded_tail0=U+DC85 (surrogate)
```

- Head-100 = `raw[:100]` = indices 0..99; its last byte is index 99 = `0x78` `'x'`. **The head cut does not touch
  the sequence at all** — the sequence straddles the *tail* cut, exactly as the claim says.
- Tail-99 = `raw[102:]`: its first byte is index 102 = `0x85`, a continuation octet whose lead `0xC2` (index 101)
  lies in the elided middle `raw[100:102]`. `surrogateescape` maps the lone `0x85` to U+DC85.
- Cell (public, receipt `PUBLIC r90`):
  `'the index-flag read failed (fatal: nel xxx…x…\\x85sss…s); tracked bytes are unverified'`
  — contains `\x85`, does **not** contain `\u0085`.

### 2.3 The filed cut

```
AFTER _cut_head(payload,100)=100  _cut_tail(payload,102)=103 (t0-1=0xc2 at0=0x85 at1=0x73)
AFTER head_end=0x78 head_is_lead=False head_is_cont=False
AFTER elided_middle=b'x\xc2\x85' len=3
AFTER window_len=201
```

- `_cut_head` correctly does nothing (it is handed a boundary: index 99 is `'x'`).
- `_cut_tail` is handed `t0 = 201-99 = 102`, i.e. index 102 = `0x85`; it scans back to the lead `0xC2` at 101, sees
  a two-octet sequence shape, `end = 101+2 = 103 > 102`, and returns **103** — past the continuation. The elided
  middle grows to `b'x\xc2\x85'` (3 bytes: the `x` at 100, the whole `C2 85`).
- Cell (public, receipt `PUBLIC r91`):
  `'the index-flag read failed (fatal: nel xxx…x…sss…s); tracked bytes are unverified'`
  — contains **neither** `\x85` nor `\u0085`. The byte bound shortens 202 → **201** because the cut moved, which is
  the behaviour the claim states.

### 2.4 The "two materially different delegated failures share a cell" sentence, made exact

The claim's mechanism is a *sharing* claim about the r90 tool. Constructed pair, same head, same tail suffix:

- A = the fixture payload: valid UTF-8 `C2 85` at 101-102 (character U+0085), 201 bytes.
- D = `b"fatal: nel " + b"x"*89 + b"AB" + b"\x85" + b"s"*98`, 201 bytes: the **invalid raw octet 0x85** at index 102.

```
PAIR D len=201 r90_identical_to_nelcut=True r91_identical=False
```

Under the r90 tool A and D produce the **same** cell (both `…\x85sss…`); under the filed tool they differ (D keeps
`\x85`, A keeps neither spelling). So the sentence holds as written, and the repair separates the pair.

### 2.5 "A continuation byte with no lead stays and keeps its `\xNN` spelling"

Payload: 201 ASCII bytes with a bare `0x85` at index 102, preceded by `'y'` (no lead anywhere to the left).

```
ORPHAN t0=102 at=0x85 prev=0x79 _cut_tail=102 cell='fatal: nel yyy…y…\\x85yyy…y'
```

`_cut_tail` returns 102 unchanged (`_utf8_seq_need(0x79) == 0`), and the cell keeps `\x85`. Stated behaviour holds.

### 2.6 Sweep of the cut positions (attack item, not part of the predicate)

480 payloads: `fatal: nel ` + ASCII + one multi-byte character (U+0085 2-oct. / U+00E9 2-oct. / U+2028 3-oct. /
U+1F600 4-oct.) + ASCII, total lengths 201..206, character starts swept across 95..105 (head cut) and
`total-106 .. total-97` (tail cut). A payload made only of valid UTF-8 must never render a byte spelling
(`\xNN`) in its cell.

```
SWEEP checked=480 head_moved=73 tail_moved=80 raw_byte_spellings_or_bad=0
SWEEP r90_arm_raw_byte_spellings=151
```

Both cuts are exercised (73 head moves, 80 tail moves), the filed tool never emits a raw-byte spelling for valid
UTF-8, and the r90 arm emits 151 — the claim's sentence 1 and sentence 3 hold at every swept position, not only at
the fixture's one position. The window octet bound also holds: a no-move 201-byte payload gives
`100 + 3 + 99 = 202`; moved cuts give 201 or less (`_cut_head` backs off, `_cut_tail` advances; `t >= t0 >= 102 > h`
so the `t < h` clamp cannot trigger for any `len(raw) > 200`).

---

## 3. Clause-by-clause

The four clauses the claim says the r91 fixture enforces, and the cases that carry them:

| clause (claim wording) | case(s) | filed tool | r90 tool | measured by |
|---|---|---|---|---|
| doubled-backslash spellings rejected | KFF9 `nelchar`, KFF10 `nelbyte` | pass | pass | `count(bs+"u0085")==1 and count(bs*2+"u0085")==0` (KFF9), same for `x85` (KFF10), plus the cell-inequality pair check on both arms |
| the boundary case renders neither spelling | KFF11 `nelcut` | **pass** | **fail** | `"\\x85" not in cell and "\\u0085" not in cell` after `"fatal: nel"` |
| the cell keeps the text after `marker` and carries no raw line separator | KFF12 `nelchar` | pass | pass | `"marker" and "tailtkn" in cell`; no `\n \r \u2028 \u2029 \u0085` in the cell |
| the tool source carries no `_one_line(` definition or call | KFF13 `decl` | pass | pass | `src.count("def _one_line(")==0 and src.count("_one_line(")==0` |

Answers to the four questions this seat was asked:

1. **Is `before_pass=14` the r90 tool's own score, failing only KFF11?** Yes — §1.1, the before column is
   `fail` on KFF11 and `pass` on all fourteen others. KFF13 passes on the r90 arm because the r90 tool has no
   literal `_one_line(` either (it was deleted in r90).
2. **Does KFF12 test a property the r90 tool passes, and does the newline variant fail it?** Yes and yes.
   KFF12's mode is `nelchar` (31 bytes — no cut), and the r90 tool already escapes U+0085 to `\u0085` and keeps
   `marker tailtkn` on one physical line, so the before arm passes it (§1.1). The `raw-newline` variant fails
   **only** KFF12 on the r91 fixture (probe, §1.2) and passes the r90 fixture 12/12 — the case is load-bearing for
   exactly the property the r90 fixture did not measure.
3. **Is the doubled-spelling clause enforced?** Yes on the committed bytes: the `double-backslash` variant (which
   doubles the U+0085 branch's backslash) is caught by **KFF9** on r91 and survives r90 12/12 (§1.2). That is the
   r90 A1 gap (the r90 substring count accepted `\\u0085` because it contains `\u0085`) now closed.
4. **Is KFF13's static scan sound for the stated sentence?** Sound for the *literal substring*, **not** for the
   plain clause. Details and the refuting artifact are in §4.

KFF11's payload exercises the **tail** cut only (the head-100 cut lands on `'x'`; §2.2). `BOTH cuts` is therefore
not exercised by any committed case; §2.6 exercises the head cut (73 moved positions) and it passes. This is
covered by the prereg's limit (iii) — recorded as a verification gap, not a falsification.

---

## 4. FALSIFIES-WORDING

### FALSIFIES-WORDING 1 — KFF13 enforces only the literal token, not "no `_one_line(` definition or call"

**Exact sentence (preregistration, C2 CLAIM):**

> The r91 fixture enforces the four clauses the r90 wording claimed but did not measure: … and the tool source
> carries no `_one_line(` definition or call (KFF13).

**Refuted under the plain reading** ("no definition or call of `_one_line`"). KFF13 is
`src.count("def _one_line(") == 0 and src.count("_one_line(") == 0` — a literal substring count. Python allows
whitespace between a name and `(`, so a real definition and a real call can be written without the substring
`_one_line(`.

**Reproducer:** `.ufo/waves/round-91/w1/R91ReviewerC2/kff13-spaced-name-tool.py` — a byte-for-byte copy of the
filed tool plus:

```python
def _one_line (text, limit=200):
    """R91ReviewerC2 probe: a real `_one_line` definition with a space before the paren."""
    return text[:limit]


def _r91_reviewer_probe(value):
    """R91ReviewerC2 probe: a real `_one_line` call with a space before the paren (never executed)."""
    return _one_line (value)
```

`ast.parse` on that file: `defs_named_one_line = 1`, `calls_named_one_line = 1`; literal counts
`def _one_line(` = 0, `_one_line(` = 0. Scored by the frozen fixture (`kff13-probe.out`):

```
CASE KFF13 tool=pass before=pass
SUMMARY cases=15 tool_pass=15 before_pass=14
EXIT=0
```

So a source that carries a real `_one_line` definition *and* a real `_one_line` call scores 15/15 and EXIT 0.

**Which sentence survives:** the filed tool itself carries no `_one_line` definition or call of any spelling
(AST check: 0 defs, 0 calls, 0 bare references outside the docstring text), so the *tool* sentence is true. What
fails is the *enforcement* clause. The prereg's stated limit (ii) excludes only "a dynamic caller constructed
outside the source text"; an in-source definition/call spelled with a space before the paren is inside the source
text and is not covered by that limit, so the limit does not rescue the clause.

**Suggested narrowing (for the L1's amendment):** *KFF13 enforces the literal absence of the substrings
`def _one_line(` and `_one_line(`; a definition or call spelled with whitespace before the paren is not detected
(in-source, outside limit (ii)'s dynamic-caller exclusion).*

Severity: **low**. No claim number moves; the filed tool's behaviour is unaffected. It is an instrument-precision
narrowing of the same class as r90 A5(c) (which measured the deletion with `grep -c 'def _one_line('` — the same
literal technique this round inherited).

No other sentence of the C2 claim is refuted by any artifact this seat produced. In particular:

- sentence 1 (r90 bounded raw bytes at head-100/tail-99 with no boundary regard) — confirmed by the before tool's
  code and by 151 raw-byte spellings in the sweep's r90 arm;
- sentence 2 (the 201-byte straddle, U+DC85, `\x85`, two failures sharing a cell) — confirmed in §2.1-2.4;
- sentence 3 (both cuts moved to sequence boundaries; head backs off; tail advances; no-lead continuation stays) —
  confirmed by code reading, the nelcut derivation and the 480-payload sweep;
- every instrument hash, `cases=15`, `detected=3` / `detected=0`, `rows=12 mismatches=0 errors=0`, `tool_pass=15
  before_pass=14`, the control `14/14` EXIT 1 — all numbers re-derive exactly.

**FALSIFIES-NUMBER:** none.

---

## 5. Residual risk and verification gaps

1. **KFF13 is a literal scan** (§4). The filed tool is clean under every reading, but the fixture's kill power
   against a whitespace-spelled helper is nil. Low impact on this round.
2. **The head cut is not exercised by any committed case.** KFF11's payload cuts only the tail (§2.2). The claim
   sentence "moves BOTH cuts" is verified here by §2.6 (73 head moves, 0 raw spellings) and by the code, but the
   predicate itself would pass a tool that never moved the head cut (as long as its tail cut moved and no case put a
   multi-byte character at index 100 of a >200-byte stderr). Stated limit (iii) discloses the single-payload scope;
   this is the residual part of that limit that a future row should close.
3. **`_cut_tail` on a structurally invalid lead can advance past a non-continuation.** If `raw[t]` is a
   continuation and the first non-continuation to its left is a lead whose declared width runs past `t` but whose
   intermediate octets are not all continuations, the function returns `lead+need` without re-checking those
   octets, so it elides one or more valid bytes of the tail. It cannot split a *valid* UTF-8 sequence (a valid
   sequence's continuations run to `lead+need-1 >= t`, and the returned start is its end, a boundary), and the
   window only shortens, so this is within stated limit (iv); it is a precision note on the docstring's
   "advances past continuations", not a boundary defect. No committed or swept case reaches it.
4. **`_utf8_seq_need` accepts `0xC0`/`0xC1` and `0xF5`–`0xF7` as leads** (RFC 3629 forbids both). Used only to
   move cuts; the effect is conservative (keeps such invalid runs whole and spells them `\xNN`), never a
   character/byte spelling collision. Grounding sentence (RFC 3629 §3) is slightly wider than the tool's table.
5. **Fixture copy semantics:** the fixture copies the tool into `--work` and runs the copy; the KFF13 read is on the
   `--tool` path (the original), not the copy. They are the same bytes in every run here (the fixture copies with
   `shutil.copyfile`); not a defect, but the two paths are worth knowing when reading the receipts.
6. **Not in this seat's scope:** C1's calibration predicates and the C2 claims about `_escape_record` /
   `_stderr_tail` (limit (i)) were not audited here.

---

## 6. Reproducer inventory (this seat dir, `.ufo/waves/round-91/w1/R91ReviewerC2/`)

| file | what |
|---|---|
| `after.out` | predicate (a) full output, `SUMMARY cases=15 tool_pass=15 before_pass=14`, EXIT 0 |
| `ctlboth.out` / `ctlboth.err` | control (i), `SUMMARY cases=15 tool_pass=14 before_pass=14`, EXIT 1 |
| `probe-r91.out` | probe r91, `SUMMARY variants=3 fixture=r91 detected=3`, EXIT 0 |
| `probe-r90.out` | probe r90, `SUMMARY variants=3 fixture=r90 detected=0`, EXIT 0 |
| `k4.out` | r87 K4 regression, `SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0 |
| `r90flat.out` | extra no-harm arm: r90 fixture on the filed tool, `cases=12 tool_pass=12 before_pass=12`, EXIT 1 (no-delta rule) |
| `c2-boundary-derivation.py` / `boundary-derivation.out` | byte-level derivation, public cells, sharing pair, orphan, 480-payload sweep |
| `kff13-spaced-name-tool.py` / `kff13-probe.out` | FALSIFIES-WORDING 1 reproducer: real spaced `_one_line` def+call, `SUMMARY cases=15 tool_pass=15 before_pass=14`, EXIT 0 |

Tooling: no install or upgrade was performed (none was needed); no host state was touched. Scratch
`/fast/scratch/hyaku/souji-r91/R91ReviewerC2/` was removed before this report was finalised.
