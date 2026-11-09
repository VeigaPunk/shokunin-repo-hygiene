# R93ReviewerC2 — C2 falsification (committed bytes)

Seat: R93ReviewerC2. Lane: souji-shokunin. Scope: C2 stated wording only (falsify, Amendment 59).
Receipts: `.ufo/waves/round-93/w1/R93ReviewerC2/probe-after.txt`, `probe-r92.txt`, `fixture-after.txt`.
All commands run with cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`, `python3 -B`, `--work` under
`/fast/scratch/hyaku/souji-r93/R93ReviewerC2/`.

## 1. Probe re-derived (after arm + r92-fixture control)

After (r93 fixture, filed tool `tools/souji-record-agreement.py` sha256
`fc0e35c208331de8…`, before `census/round-92/controls/c2-before-tool.py` sha256
`21e5c7408fef10f2…`, fixture sha256 `ed15094e9ff17c15…`, probe sha256 `f3c84c49ac32cef4…`):

```
PROBE-AFTER EXIT=0
POSITIVE tool exit=0 tool_pass=22/22 pass
FORGERY F5 … exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY F6 … exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY F7 … exit=1 tool_pass=21/22 rejected=yes failed=KFF19
FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass
```

Fixture after:

```
SUMMARY cases=22 tool_pass=22 before_pass=16 EXIT=0
# KFF19 tool=…/souji-record-agreement.py payloads=14586 inexact=0
# KFF19 tool=…/c2-before-tool.py payloads=14586 inexact=3096
```

r92-fixture control (same probe, `--fixture tests/fixtures/r92-k4-flagfail.py`):

```
PROBE-R92 EXIT=1
POSITIVE tool exit=0 tool_pass=20/20 pass
FORGERY F5 … exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY F6 … exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY F7 … exit=0 tool_pass=20/20 rejected=no failed=-
FORGERY-SUMMARY forgeries=8 rejected=5 positive=pass
```

This matches prereg C2 PREDICATE and CONTROL verbatim, and matches filed
`census/round-93/records/c2-forgery-after.txt` / `c2-after.txt` /
`census/round-93/controls/c2-control-r92-fixture-probe.txt` (same shas, same lines).

## 2. Spec-vs-code: `_ref_len` / `_ref_straddle` / `ref_cuts` vs S356 and Table 3-7

### 2a. WHATWG S356 §8.1.1 (filed `census/round-93/srcs/encoding.txt`, bytes 62,000–66,000)

```
If UTF-8 bytes needed is 0, based on byte:
  0x00 to 0x7F Return a code point whose value is byte.
  0xC2 to 0xDF Set UTF-8 bytes needed to 1. … byte & 0x1F.
  0xE0 to 0xEF If byte is 0xE0, then set UTF-8 lower boundary to 0xA0.
              If byte is 0xED, then set UTF-8 upper boundary to 0x9F.
              Set UTF-8 bytes needed to 2. … byte & 0xF.
  0xF0 to 0xF4 If byte is 0xF0, then set UTF-8 lower boundary to 0x90.
              If byte is 0xF4, then set UTF-8 upper boundary to 0x8F.
              Set UTF-8 bytes needed to 3. … byte & 0x7.
  Otherwise Return error.
If byte is not in the range UTF-8 lower boundary to UTF-8 upper boundary, inclusive: … Return error.
Set UTF-8 lower boundary to 0x80 and UTF-8 upper boundary to 0xBF. …
UTF-8 code point to (UTF-8 code point << 6) | (byte & 0x3F).
```

Initial state: "UTF-8 lower boundary A byte, initially 0x80. UTF-8 upper boundary A byte, initially 0xBF."

### 2b. Unicode Table 3-7 (filed `census/round-92/srcs/unicode-ch3.txt`, §3.9.3)

```
Table 3-7. Well-Formed UTF-8 Byte Sequences
U+0000..U+007F  00..7F
U+0080..U+07FF  C2..DF  80..BF
U+0800..U+0FFF  E0  A0..BF  80..BF
U+1000..U+CFFF  E1..EC  80..BF  80..BF
U+D000..U+D7FF  ED  80..9F  80..BF
U+E000..U+FFFF  EE..EF  80..BF  80..BF
U+10000..U+3FFFF F0  90..BF  80..BF  80..BF
U+40000..U+FFFFF F1..F3  80..BF  80..BF  80..BF
U+100000..U+10FFFF F4 80..8F 80..BF 80..BF
"…the following byte values are disallowed in UTF-8: C0–C1, F5–FF."
```

### 2c. Table: code (`tests/fixtures/r93-k4-flagfail.py:370–406`) vs spec

| Lead / case | Code `_ref_len` (r93:374–379) | WHATWG §8.1.1 | Table 3-7 | Verdict |
|---|---|---|---|---|
| 0x00–0x7F | `return 1` (:373) | "0x00 to 0x7F … Return a code point" | 00..7F | exact |
| 0xC2–0xDF | `need,lo,hi = 1,0x80,0xBF` | "0xC2 to 0xDF … bytes needed to 1" (initial bounds) | C2..DF 80..BF | exact |
| 0xE0 | `need=2, lo=0xA0` | "If byte is 0xE0, lower boundary to 0xA0" | E0 A0..BF | exact |
| 0xED | `hi=0x9F` | "If byte is 0xED, upper boundary to 0x9F" | ED 80..9F | exact |
| 0xE1–0xEC,0xEE–0xEF | `need=2, 0x80..0xBF` | E0..EF branch minus E0/ED specials | E1..EC / EE..EF 80..BF | exact |
| 0xF0 | `need=3, lo=0x90` | "If byte is 0xF0, lower boundary to 0x90" | F0 90..BF | exact |
| 0xF4 | `hi=0x8F` | "If byte is 0xF4, upper boundary to 0x8F" | F4 80..8F | exact |
| 0xF1–0xF3 | `need=3, 0x80..0xBF` | F0..F4 branch minus specials | F1..F3 80..BF | exact |
| C0,C1,F5–FF, 0x80–0xBF | `else: return None` (:381) | "Otherwise Return error" (incl. bare continuation) | "C0–C1, F5–FF disallowed"; isolated 80 has no standalone interpretation | exact |
| Later continuations | `lo,hi = 0x80,0xBF` after first (:385) | "Set UTF-8 lower boundary to 0x80 and UTF-8 upper boundary to 0xBF" before each subsequent byte | "These exceptions … occur only in the second byte" | exact |
| Truncation | `if s+k >= len(raw) …: return None` (:383) | end-of-queue with bytes needed ≠ 0 → error | sequence must be complete | exact |

Spot-checked all 16 boundary rows by executing `_ref_len` on each token above: 16/16 agree
(`c280→2, dfbf→2, e0a080→3, e09fbf→None, ed9fbf→3, eda080→None, f0908080→4, f08fbfbf→None,
f48fbfbf→4, f4908080→None, c0af→None, c1bf→None, f580→None, 85→None, 61→1, 7f→1`).

`_ref_straddle` (:389–396) searches starts `cut-1 … cut-3` (`range(cut-1, max(cut-4,-1), -1)`)
for a well-formed seq with `s < cut < s+n`. Only a seq of length ≤4 starting at ≥`cut-3` can
straddle; at most one can (docstring, correct: a byte that is a continuation cannot start a seq,
so straddling seqs cannot overlap). `ref_cuts` (:399–406): `head=limit//2=100`,
`keep=limit-head-1=99`, head moves to `seq[0]` (back), tail moves to `seq[1]` (forward),
`return h, max(t,h)` — mechanically identical to the filed tool's
`_cut_head`/`_cut_tail` calls in `tools/souji-record-agreement.py:274–278`
(`_one_line_bytes`), which take `_straddling_sequence` (strict-decode oracle) instead.
The reference needs no codec: it implements the decoder's state transitions directly.
One nuance (below, not a wording falsification): the filed tool's "well-formed" oracle is
`len(raw[start:end].decode("utf-8","strict"))==1` over `start ∈ [cut-3,cut-1]`,
`end ∈ [cut+1, start+4]`, which is extensionally equal to `_ref_straddle` on the sweep
(byte-identical cells, KFF19 `inexact=0` on filed tool) but not syntactically the spec text.

## 3. KFF18 truth, F5/F6/F7 on r92 fixture, and "fail ONLY KFF19"

### 3a. "the r92 fixture checks only prefix/suffix faithfulness" — true of KFF18, not of the fixture as a whole

KFF18 (`case_sweep`, r93:348–364; r92 identical) checks ONLY:

```
full = mod._escape_text(mod._decode_record(raw))
head, sep, tail = cell.partition("\u2026")
bad += not (sep and full.startswith(head) and full.endswith(tail))
```

i.e. head must be SOME prefix of `full`, tail SOME suffix of `full` (length ≤200: `cell == full`).
It never pins where the cut lands. The prereg sentence "The r92 fixture checks that the excerpt's
head is SOME prefix and its tail SOME suffix" is predicated on KFF18 as the cut-position gate;
read literally as "every case in the r92 fixture checks only prefix/suffix" it would be false
(KFF1–KFF17/KFC1–2 check escape spellings, counts, pair distinctness, source). I record this as a
wording-precision note, not a falsification: the claim's operative content — KFF18 is the only
cut-position case and it is prefix/suffix-only — is exact. F5/F6/F7 all pass KFF18 on the r92
sweep (their cuts still move whole-`_straddling_sequence` spans, so head stays a prefix and tail
a suffix).

### 3b. F5/F6/F7 pass r92 fixture 20/20 (control receipt)

From §1, independently re-run: `F5 tool_pass=20/20 rejected=no failed=-`,
`F6 20/20 rejected=no`, `F7 20/20 rejected=no`. No case-specific receipt was needed; KFF18
`unfaithful=0` for each (their `.out` has no KFF18 fail).

### 3c. On r93 fixture each of F5/F6/F7 fails ONLY KFF19 — confirmed from probe `failed=` lists

```
FORGERY F5 … failed=KFF19
FORGERY F6 … failed=KFF19
FORGERY F7 … failed=KFF19
```

("ONLY KFF19" is the full `failed=` list; by contrast F1 fails KFF16,KFF18,KFF19,KFF20 etc.)

### 3d. One distinguishing payload per forgery (filed vs forgery vs reference cells)

All from `exact_payloads()` (EXACT_LEN=230, head cut 100, tail cut 131), executed in-process.
"filed" = `tools/souji-record-agreement.py`, "ref" = `ref_cuts` + filed `_decode_record`/`_escape_text`.

**F5 (`surrogatepass`) — first mismatch payload #110.** Payload is `a`*230 with non-`a`
bytes at offsets 98–100: `ED A0 80` (ill-formed: ED needs 80..9F next). Cut 100 sits inside it
(`98 < 100 < 101`).
- filed straddle@100: `None`; F5 straddle: `(98, 101)` — `b'\xed\xa0\x80'.decode('utf-8','surrogatepass')`
  is one "character" (surrogate U+D800), strict raises.
- ref cell: `aaa…(98 a)\xed\xa0…aaa` (EC0/80 escapes kept, cut stays at 100).
- filed cell = ref cell: `'a'*98 + '\\xed\\xa0' + '…' + 'a'*99`.
- F5 cell: `'a'*98 + '…' + 'a'*99` — cut moved to 98, swallowing the surrogate encoding as one
  sequence. Cause: cut POSITION moved across bytes that are not one well-formed sequence.
  Prefix/suffix still hold (F5's head is a shorter prefix, tail the same suffix) — hence KFF18 passes.

**F6 (`>= 1`) — first mismatch payload #1 (all-`a`, 230 bytes).** Cut 100, tail 131.
- filed straddle@100: `None` (candidate `raw[99:101]=b'aa'` decodes strict to 2 chars, `==1` fails).
- F6 straddle: `(99, 101)` — `len('aa')==2 >= 1`.
- ref cell: `'a'*100 + '…' + 'a'*99`; filed head 100/tail 131.
- F6 cell: `'a'*99 + '…' + 'a'*99` with head 99, tail 132 — both cuts moved by one byte
  (span of two characters treated as one "sequence"). Still prefix/suffix — KFF18 passes.
  This is the purest witness that KFF18 cannot see position: the forgery disagrees with the
  reference on a payload with no multibyte byte at all.

**F7 (head forward) — first mismatch payload #8.** Bytes at 99–100: `C2 80`
(well-formed U+0080), cut 100 inside it.
- filed straddle `(99,101)`, head → 99; ref `(99, 131)`.
- ref/filed cell: `'a'*99 + '…' + 'a'*99` (whole U+0080 elided, no `\x80` spelling).
- F7 cell: `'a'*99 + '�'-as-'\\x80' + '…' + …` i.e. head → 101, leaving orphan continuation
  `0x80` rendered `\x80`. Cause: head cut moved forward to seq end instead of back to seq start.
  Prefix/suffix still hold (head is a longer prefix that respells nothing the full rendering
  spells differently — `\x80` vs `�` — wait: `full` spells it `\u0080`; F7's head `\x80` is NOT a
  prefix of `full`). Correction: F7 still passes KFF18 because `head` = F7's head partition
  `a*99+\x80` — hmm, that is not a prefix of `full` (`a*99+\u0080…`). Re-check: KFF19 is what
  fails F7; KFF18 payloads (offsets 84–117) also contain C2 80 pairs, and F7 passes KFF18
  (`failed=KFF19` only, so KFF18 `unfaithful=0` for F7 in probe). The reason: F7's `_straddling_sequence`
  spans `start ∈ [cut-3,cut-1], end ∈ [cut+1,start+4]` with strict `==1` — for the KFF18 sweep
  tokens the moved head still starts on a sequence boundary, so head remains a prefix; payload #8
  here shows the exact-position failure. (Logged honestly; both statements verified by the probe
  `failed=` lists.)

## 4. KFF20 derivation (byte offsets)

Payload (FAKE_WRITER `headill`, r93:122): `b"fatal: hil " + b"h"*87 + b"\xe0\x80\x80" + b"t"*110`
= 211 bytes. Prefix `fatal: hil ` is 11 bytes, plus 87 `h` = 98. Hence:

```
offset 98: 0xE0
offset 99: 0x80   (first 0x80)
offset 100: 0x80  (second 0x80)
offset 101: 0x74  ('t')
```

Tool: `limit=200, head=100, keep=99`, tail cut `len-keep = 112` (in `t` run, no straddle).
Head cut **100 lands between the two 0x80 bytes** (between offsets 99 and 100, i.e. the boundary
at byte index 100 splits `…80|80…`). E0 80 80 is ill-formed (E0 needs A0..BF; §2 Table 3-7:
"E0 9F 80 is ill-formed because 9F is not well-formed as a second byte" — same row, 80 < A0).
- Filed tool: `_straddling_sequence(payload,100) = None` (no well-formed seq straddles),
  ref: same `None`, `ref_cuts=(100,112)`, cell =
  `'fatal: hil h*87' + '\\xe0\\x80' + '…' + 't'*99`.
  `case_headill` requires `rows[0].count(bs+"xe0")==1 and count(bs+"x80")==1`: filed 1/1 pass.
- r91 tool (`c2-before-tool.py`, `_utf8_seq_need` C0–DF/2,E0–EF/3,F0–F7/4 + cont-only check):
  `_cut_head(payload,100) = 98` (lead length 3, `end=101>100`, bytes 98..100 all "continuations
  after lead" per its check `all(0x80<=b<=0xBF for b in raw[i:end])` where `i=98` — raw[98]=E0
  fails the cont check… observed behavior: it DOES move to 98, because its while loop backs to
  `i=98` and the check passes on the continuation tail. Direct execution: `_cut_head → 98`,
  cell = `'fatal: hil h*87…ttt…'` with **0× `\xe0`, 0× `\x80`** → `case_headill` fails.
- F2 (r91 tail cont-only, base=`before`): its head is r91's head (98) → fails KFF20
  (`CASE KFF20 tool=fail` in F2 `.out`). F2 alone (tail-only) would pass a head-only check,
  but F2's base already fails the head — recorded, not a separate "F2-fails-KFF20" claim.
  F3/F4/F5/F6/F7 pass KFF20 in probe (head unchanged / tail-only).
- A "lead-length cut" (trust declared length, ignore E0 lower boundary) moves head 100→98,
  eliding E0+first-80, leaving second 80 elided too → 0 escapes → fails KFF20. That is exactly
  what the r91 head does, closing the "would fail it" question constructively.

`KFF20` is a genuine head-side mirror of KFF16 (tail E0 80 80), and it is the only r93 case that
splits E0/80/80 between the two continuations rather than before/after the lead.

## 5. 14,586 count and EXACT_N literal

```
EXACT_N literal 14586 computed 14586 match True
EXACT_TOKENS 33 EXACT_LEN 230
hand tot 14586
EXACT_N is Constant literal: True 14586 (AST Constant, no computation)
```

Derivation: `exact_payloads()` (r93:424–431) iterates cuts (100, 131) × 33×33 pairs ×
`len(a+b)+1` offsets (`s ∈ [cut-len(pair), cut]`). Sum over cuts/pairs of `(len(a)+len(b)+1)`
= 14,586; `len(list(exact_payloads())) = 14586`. `case_exact` requires
`n == EXACT_N and bad == 0`; receipt prints `payloads=14586`. So the count is what
`exact_payloads()` yields, and `EXACT_N = 14586` is a literal (AST `Constant`), not computed.
KFF18's 29,700 likewise re-derived (`len(list(sweep_payloads())) == 29700`).

## 6. FALSIFICATION list

**NO-FALSIFICATION** of C2's stated wording on committed bytes. All of: probe/after/fixture
SUMMARYs and exits (§1), F5/F6/F7 pass-r92-fail-r93-only-KFF19 (§3), spec-vs-code equality
(§2, 16/16 boundary rows + truncation + later-continuation reset), KFF20 offsets and fail modes
(§4), 14,586/`EXACT_N` literal (§5) re-derived by execution, not by reading receipts.

One wording-precision note (not a falsification, recorded for L1): the sentence "The r92 fixture
checks that the excerpt's head is SOME prefix and its tail SOME suffix" is true only as a
description of KFF18, the fixture's sole cut-position case. Other r92 cases (KFF6/KFF9/KFF14
pairs, KFF13 source scan, etc.) check spellings/counts. If the L1 wants zero ambiguity it can
narrow to "KFF18, the r92 fixture's cut-position case, checks only …". No predicate, number,
or exit changes under that narrowing.

Tried and found non-falsifying: (a) ran `_ref_len` on all 16 Table-3-7 boundary tokens —
all agree; (b) compared filed-tool straddle vs reference straddle on KFF19 payloads — identical
cells (`inexact=0`); (c) built F5/F6/F7 modules from probe edit text and found first distinguishing
payload each — all three diverge only in cut position; (d) executed r91 `_cut_head` on KFF20
payload — 98, eliding both escapes; (e) AST-checked `EXACT_N` — `Constant(14586)`.

## 7. Residual risk / verification gaps (scoped)

- KFF19 equivalence between filed strict-decode oracle and reference decoder is exact-position
  on the 14,586 sweep (measured), not a proof for all payloads — matches stated limit (i).
- F7/KFF18 reasoning in §3d has a self-correction inline; the checkable claim (F7 passes KFF18,
  fails KFF19) is probe-derived either way.
- No tool install needed or performed. Scratch deleted after receipt copy (see yield note).
