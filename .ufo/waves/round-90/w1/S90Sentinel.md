# S90Sentinel — souji r90, security/robustness attack on the C2 repair and the K4 record

Seat: S90Sentinel (leaf; no subagents, no sibling-lane contact, no git/jj mutation, no
commits). Lane: `souji-shokunin`, lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2`.
Lane HEAD at the time of this report: `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (commit F,
the preregistration). Tool under test: `tools/souji-record-agreement.py`
sha256 `d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561` (matches the
prereg's filed sha). Before tool: `census/round-90/controls/c2-before-tool.py`
sha256 `f6fce6d147165d1baf3d8d0347f46c1ab913b23947f3edaa28b61cdd6caa18dd` (matches; and
byte-identical to the r89 filed tool at `bd760432` — verified with
`git show bd760432:tools/souji-record-agreement.py | sha256sum` →
`f6fce6d1…`, then `diff` against the control → IDENTICAL).

**Verdict in one line: the C2 claim's STATED WORDING holds on the filed tool, but the
round's own counter (the r90 KFF9/KFF10 pair) does NOT bind the word "injective", and the
repair is arm-local — the byte/character distinction the claim makes is NOT established
for the K4 record as a whole. Two HIGH findings, both with reproducers.**

Tool versions: Python 3.14.8 (main, Oct 2 2026) [GCC 16.2.1 20260810]; git 2.56.0;
GNU/Linux 7.2.11-arch1-1. No tools were installed or upgraded for this seat, so the
generic-rules install log is empty.

---

## 0. Evidence durability

This file was created first (skeleton) and appended to as the seat worked; the same
content is the seat's yield. All scratch lived under
`/fast/scratch/hyaku/souji-r90/S90Sentinel/` and was deleted before yielding
(see §7). No lane file outside my seat's scope was written; the lane `census/`,
`corpus/`, `tools/`, `tests/` trees were read only.

---

## 1. The claim under attack, quoted

From `census/round-90/preregistration.txt` (commit F, frozen before any after-data):

> **C2 — axis operability 8.** CLAIM. The K4 FLAGFAIL detail's escaping rule is injective
> on the byte/character pair the r89 repair left colliding: the raw byte 0x85 (arriving as
> the surrogate U+DC85 through `surrogateescape`) keeps the `\x85` spelling, and the
> CHARACTER U+0085 (NEL), whose UTF-8 encoding the r89 tool also rendered `\x85`, now
> takes the `\u0085` spelling; the dead escape-first helper `_one_line` (zero callers) is
> deleted.

> STATED LIMITS. (i) The repair covers `_escape_text` (the delegated stderr cell) only;
> `_escape_record` (path bytes) is unchanged and byte-based, so a path's U+0085 bytes
> already print `\xc2\x85` and were never ambiguous. (ii) The injectivity measured is the
> enumerated KFF9/KFF10 pair; no universal injectivity is claimed, and a stderr that
> differs from another only inside the elided middle still renders identically. (iii) The
> pair check's binding to KFF10 is this round's rule; the r89 fixture bound only KFF6/KFF7
> to a pair. (iv) The `_one_line` deletion is dead-code removal by static grep plus import;
> runtime dispatch is not exhaustively excluded. (v) The before tool is the r89 filed bytes;
> the r88 and older bytes are not arms of this claim.

Amendment 59 applies: a claim verifies only if no artifact produced by this round's own
wave falsifies its STATED WORDING. My artifacts therefore attack the wording, and I
separate "the wording is false" from "the wording is true but the measurement does not
bind it".

---

## 2. Baseline: the round's own counter, re-run on the committed bytes

```
$ python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py \
    --before census/round-90/controls/c2-before-tool.py --work <scratch>
# tool path=.../tools/souji-record-agreement.py sha256=d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561
# before path=.../census/round-90/controls/c2-before-tool.py sha256=f6fce6d147165d1baf3d8d0347f46c1ab913b23947f3edaa28b61cdd6caa18dd
# fixture sha256=d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa
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
CASE KFF9 tool=pass before=fail
CASE KFF10 tool=pass before=fail
SUMMARY cases=12 tool_pass=12 before_pass=10
EXIT 0
```

The C2 predicate as stated (`cases=12 tool_pass=12 before_pass=10`, EXIT 0) reproduces
**exactly**. The r87 12-row K4 counter on the filed tool also reproduces:
`SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0. The r89 fixture's ten cases all still
pass on the filed tool (`SUMMARY cases=10 tool_pass=10 before_pass=8`, EXIT 0) — the
repair is not a trade against r89.

**No-work control:** the do-nothing control is not reachable to the target — the before
arm reads `before_pass=10` and `tool_pass` is 12 only with the filed tool. There is no
arm on which the counter reaches the target without the repair.

---

## 3. Injection table (task item 1)

All rows produced by driving the **filed tool through its public path** (a copy beside a
fake receipt writer in a hermetic scratch repo — the same shape as the r90 fixture), with
the delegated `git ls-files -v -z` failing and its stderr carrying the payload. The
reader shown is the one the r90 fixture itself uses (`line.split("\t", 4)`, take `cells[4]`).

| # | Injection | Exact K4 record (detail cell) | Line-oriented reader fooled? |
|---|---|---|---|
| I0 | baseline `fatal: cannot read index\n` | `the index-flag read failed (fatal: cannot read index\n); tracked bytes are unverified` | no |
| I1 | stderr with **both** raw byte 0x85 and CHARACTER U+0085 | `the index-flag read failed (fatal: nel \x85 and \u0085 marker\n); tracked bytes are unverified` | **no** — the two spellings coexist and are distinguishable; the pair check holds |
| I1b | stderr with CHARACTER U+0085 only | `the index-flag read failed (fatal: nel \u0085 marker\n); tracked bytes are unverified` | no |
| I1c | stderr with raw byte 0x85 only | `the index-flag read failed (fatal: nel \x85 marker\n); tracked bytes are unverified` | no |
| I2 | stderr carrying the **literal text** `\u0085` | `the index-flag read failed (fatal: nel \\u0085 marker\n); tracked bytes are unverified` | no for the reader; **yes for the counter** — see H1 |
| I2b | stderr carrying the literal text `\x85` | `the index-flag read failed (fatal: nel \\x85 marker\n); tracked bytes are unverified` | no for the reader; **yes for the counter** — see H1 |
| I3 | forged writer prints its own `\u0085` | `writer forged a detail with \\u0085 inside` | no |
| I4 | stderr carrying a forged `MISMATCH\tK4\t.\tforged\tinjected` line | `the index-flag read failed (fatal: oops\nMISMATCH\tK4\t.\tforged\tinjected\n); tracked bytes are unverified` | **no** — one physical line, one MISMATCH row; the injected text is escaped, not a second row |
| I4b | same, TAB-separated only | `…(fatal: oops\tMISMATCH\tK4\t.\tforged\tinjected\n); …` | no |
| I4c | same, CR-separated | `…(fatal: oops\rMISMATCH\tK4\t.\tforged\tinjected\n); …` | no |
| I4d | same, U+2028-separated | `…(fatal: oops\u2028MISMATCH\tK4\t.\tforged\tinjected\n); …` | no |
| I4e | same, U+2029-separated | `…(fatal: oops\u2029MISMATCH\tK4\t.\tforged\tinjected\n); …` | no |
| I4f | same, NUL-separated | `…(fatal: oops\x00MISMATCH\tK4\t.\tforged\tinjected\n); …` | no |
| I6 | **path** cell holding U+0085 vs a raw 0x85 byte | `MISMATCH\tK4\tchar-u0085-\xc2\x85.txt\tuncommitted-path\t??` and `MISMATCH\tK4\traw-0x85-\x85.txt\tuncommitted-path\t??` | no — four distinct spellings (§5) |

The FLAGFAIL arm is sound: the raw TAB/LF/CR/NEL/U+2028/U+2029/NUL in the delegated
stderr are all escaped, so **no injection produces a second physical MISMATCH row** —
I verified the row count stays 1 in every case, and the r87 K4 counter's own regex
`^MISMATCH\tK4\t([^\t]*)\t([^\t]*)\t(.*)$` parses exactly one row.

**But the FLAGFAIL arm is not the only arm that produces a K4 detail.** There are five:
FLAGFAIL, FORGED, REFUSED, no-verdict and status-failed. The r90 repair touches only the
FLAGFAIL arm (and `_escape_record` is not touched at all). The other three are where a
reader can be fooled — see H2.

---

## 4. H1 — HIGH: the round's counter does not bind the word "injective"

**Severity: HIGH. This is a defect in the round's own instrument, not in the filed tool.**

The prereg's KILL RULE says KFF9 "requires the detail to carry exactly one `\u0085`
spelling and no `\x85` spelling". The fixture implements that as a **substring count**:

```python
# tests/fixtures/r90-k4-flagfail.py
rows[0].count(bs + "u0085") == 1 and rows[0].count(bs + "x85") == 0     # KFF9
rows[0].count(bs + "x85") == 1 and rows[0].count(bs + "u0085") == 0     # KFF10
```

A substring count cannot tell the *character* U+0085 from the *literal text* `\u0085`,
because the escaped literal `\\u0085` **contains** the substring `\u0085` starting at
index 1. Measured on the filed tool (probe8, T1):

```
literal-\u0085 cell : 'fatal: nel \\u0085 marker\\n'
  KFF9 on it (the payload carries NO character U+0085) : True
literal-\x85   cell : 'fatal: nel \\x85 marker\\n'
  KFF10 on it (the payload carries NO raw byte 0x85)   : True
```

So **KFF9 passes on a payload that contains no U+0085 character at all, and KFF10 passes
on a payload that contains no raw 0x85 byte at all.** The claim's word "injective" is
not what the counter measures.

The r89 fixture already had this right, and the r90 fixture dropped it. r89's KFF6
explicitly demands the doubled-backslash form be ABSENT and KFF7 demands it be PRESENT:

```
r89 KFF6: rows[0].count(bs + "xff") == 1 and rows[0].count(bs*2 + "xff") == 0   -> literal text REJECTED
r89 KFF7: rows[0].count(bs*2 + "xff") == 1 and rows[0].count(bs + "xff") == 1
```

### Reproducer: a mutant that survives the whole round

`mut/mutant.py` — one-token change to the filed tool, the U+0085 branch emits a
DOUBLED backslash (`"\\\\u%04x" % o` instead of `"\\u%04x" % o`):
sha256 `5ec2e925de2822ebc46081bb0d4a6350fcd1ed92bc59a3486a12e4d67e2174a6`.

```
$ python3 -B tests/fixtures/r90-k4-flagfail.py --tool mut/mutant.py --before <before> --work <scratch>
CASE KFF1..KFF8 tool=pass before=pass
CASE KFF9 tool=pass before=fail
CASE KFF10 tool=pass before=fail
SUMMARY cases=12 tool_pass=12 before_pass=10
EXIT 0
```

**The mutant passes the round's own counter 12/12 with EXIT 0.** And it also survives
the r89 fixture:

```
$ python3 -B tests/fixtures/r89-k4-flagfail.py --tool mut/mutant.py --before <r89 before> --work <scratch>
SUMMARY cases=10 tool_pass=10 before_pass=8
EXIT 0
```

and the r87 12-row K4 counter (with the receipt writer correctly beside it):

```
$ python3 -B census/round-87/c2-k4-counter.py --tool mut1fix/tools/souji-record-agreement.py --work <scratch>
SUMMARY rows=12 mismatches=0 errors=0
EXIT 0
```

(Control: an UNMUTATED copy of the filed tool in the same directory also reads
`mismatches=8` — that is a layout artifact of running the counter on a copy, not a kill.
Re-run with the writer beside it, the control is `mismatches=0 errors=0` and so is the
mutant.)

The mutant destroys exactly what the claim asserts (probe10, R10d):

```
FILED  : char==literal(\u0085)? False   byte==literal(\x85)? False   <- injective
MUTANT1: char==literal(\u0085)? True    byte==literal(\x85)? False   <- injectivity GONE
```

and it breaks reversibility of the escape (probe9, H2b): decoding `\\u0085` under the
r87 backslash rule yields the six characters `\u0085`, not the character U+0085 —
`round-trips ? False` (the filed tool: `True`).

**Exploit path.** A tool that renders the character U+0085 with a doubled backslash is
accepted by every counter this round filed, while a reader of the K4 record can no longer
recover the exact bytes: the cell `\\u0085` is ambiguous between "the character U+0085"
and "the literal text `\u0085`". The reader is the r87 K4 counter and the r90 fixture
themselves.

**Smallest remediation** (one clause per case, mirroring the r89 KFF6/KFF7 discipline the
round already had for the analogous 0xFF pair):

```
KFF9  += (rows[0].count(bs * 2 + "u0085") == 0)
KFF10 += (rows[0].count(bs * 2 + "x85")  == 0)
```

Measured effect (probe10, R10b):

```
arm                                | KFF9 char KFF9 lit | KFF10 byte KFF10 lit
FILED  (d095b52f)                  |      True    False |       True      False
BEFORE (f6fce6d1)                  |     False    False |       True      False
MUTANT1 (doubled U+0085 branch)    |     False    False |       True      False   <- now KILLED
MUTANT2 (doubled surrogate branch) |      True    False |      False      False   <- now KILLED
```

The tightening keeps the filed tool green, keeps the before arm red on KFF9 (the round's
measured delta is preserved), and kills both mutants. Note the mirror mutant
(`mut2/mutant.py`, sha256 `a49220146a0f74119214654cb47bcc7ba58238ae82625b4fbb26a22e72a407ae`,
doubling the surrogate branch) is *already* caught by the as-filed fixture
(`tool_pass=11`, EXIT 1) — so the gap is specific to the U+0085 branch.

**Does this falsify the claim's stated wording?** No. On the **filed bytes** the wording
is TRUE: `_escape_text("\u0085")` is `\u0085` and `_escape_text("\udc85")` is `\x85`,
and they differ; brute force over the 14-character alphabet (backslash, LF, TAB, CR,
C0 edges, DEL, U+0085, U+2028, U+2029, U+DC85, U+DCFF, `A`, U+00FF) found **zero**
collisions among single characters and **zero** among all 2-char strings (probe6, R6).
What H1 shows is that the round's counter cannot *certify* the wording, i.e. the KILL
RULE as frozen does not bind the property the CLAIM states. That is a defect in the
instrument, and it is the L1's call whether to amend the fixture or narrow the claim —
I am not repairing it (the fixture is committed evidence).

---

## 5. H2 — HIGH: the byte/character distinction is arm-local; the K4 record as a whole is not injective

**Severity: HIGH. Reader-visible ambiguity in the K4 record. The claim's wording survives
only because the claim is explicitly scoped to "the K4 FLAGFAIL detail's escaping rule"
and limit (i) scopes the repair to `_escape_text`; the record-level property the claim
implies is not established.**

The repair changed `_escape_text` only. But three of the five K4 detail arms never reach
`_escape_text`, or reach it after the distinction has already been destroyed:

### H2a — FORGED arm: real LF, U+0085, U+2028 and U+2029 all render identically

The parent's own `out.splitlines()` runs **before** `_escape_text`:

```python
out = proc.stdout.strip()
lines = out.splitlines()
if lines and lines[0].startswith("WRITER "):
    out = "\n".join(lines[1:]).strip()
...
if out.startswith("FORGED "):
    return _escape_text(out[len("FORGED "):])
```

`str.splitlines()` splits on NEL, LS and PS as well as LF. Measured end to end
(probe5, FORGED arm — the writer's message is read from a file so the bytes are exact):

```
msg A real LF           -> detail = 'a\nb'
msg B CHAR U+0085 (NEL) -> detail = 'a\nb'
msg C U+2028 (LS)       -> detail = 'a\nb'
msg D U+2029 (PS)       -> detail = 'a\nb'
--> COLLISIONS in this arm: {'a\nb': ['A real LF', 'B CHAR U+0085 (NEL)', 'C U+2028 (LS)', 'D U+2029 (PS)']}
```

A writer that says `FORGED <msg with NEL>` and one that says `FORGED <msg with a
newline>` produce the **byte-identical** K4 detail cell. The r90 repair cannot reach
this arm: the distinction is destroyed before `_escape_text` is called.

### H2b — REFUSED arm: a NEL silently truncates the refusal reason

```python
return (f"the receipt writer refused the tree (exit {_escape_text(out.split(' ', 1)[-1].splitlines()[0])}); …")
```

`.splitlines()[0]` keeps only the first line, so a NEL in the refusal code drops
everything after it:

```
plain  -> 'refused: bad'
NEL    -> 'refused: bad'      (the tail after the NEL is silently GONE)
LF     -> 'refused: bad'
```

### H2c — no-verdict arm: `_stderr_tail` is not escaped at all, and a NEL drops the type name

`_stderr_tail` picks the **last** `splitlines()` line. Since NEL is a `splitlines()`
separator, a NEL inside an exception message makes the detail the text AFTER the NEL —
**the exception type name, the very thing the detail exists for, is lost**:

```
stderr lines : ['Traceback (most recent call last):', '  File "w", line 1', 'ValueError: boom\x85AND-THEN-A-TAIL']
_stderr_tail : 'AND-THEN-A-TAIL'
'ValueError' survives ? False
```

And this arm's detail is emitted **unescaped**, so a raw TAB in the delegated stderr
lands raw in the cell:

```
emitted row : 'MISMATCH\tK4\t.\tstat-cache-concealed\tValueError: boom\tMISMATCH\tK4\t.\tforged\tinjected'
unbounded split('\t') -> 10 fields
cells[2] (the detail the r87 byte-arm reader sees): 'MISMATCH'
```

The r87 byte-arm reader (`census/round-87/c2-byte-arm.py:166`,
`lines = [l.split(b"\t") for l in out.split(b"\n") if l.startswith(K4)]`) splits
**unbounded**, so it reads `MISMATCH` as the detail. Raw ESC and raw CSI also survive:
`'ValueError: boom\x1b[31mRED\x1b[0m'`, `'ValueError: boom\x9b[31mRED'`.

Note the r87 K4 counter's regex tolerates this (`(.*)$` with `re.M` captures the whole
tail), so the counter still reads one row — but a field-splitting reader does not.

### H2d — the byte/character pair collides at the FLAGFAIL window boundary

This is the sharpest form, and it is inside the arm the repair DID touch. `_one_line_bytes`
bounds the RAW bytes to 200 and then decodes the window. When the character's 2-byte
encoding lands on the head/tail junction, the lead byte is elided and only the
continuation byte survives, so **the CHARACTER renders with the RAW BYTE's spelling**:

```
A source bytes at L-100..L-99 : c285  (0xc2 0x85 = the CHARACTER U+0085, adjacent in the source)
B source bytes at L-100..L-99 : 6885  (0x68 0x85 = 'h' then a lone RAW byte 0x85)
A cell == B cell (BYTE-IDENTICAL) ? True
A cell contains '\x85' (the BYTE's spelling) ? True
A cell contains '\u0085' (the CHAR's spelling) ? False
```

End to end through the public path, the two K4 rows are byte-identical:

```
THE TWO K4 ROWS ARE BYTE-IDENTICAL ? True
```

Sweeping the character across every offset of a 300-byte stderr: at **102 of the 298
offsets tried** the KFF9 predicate as written is FALSE for a payload that genuinely
carries the character U+0085 (offsets 99–200), and at **101 of those 298 offsets** the
char payload and the raw-byte payload render identically (offsets 100–200: the whole
character is elided, or only its continuation byte survives). Outside that junction
region the pair is correctly distinguished (`'hhhhh\u0085hhhh…'` vs `'hhhhhh\x85hhh…'`).
A lone raw byte 0x85 fails the KFF10 predicate at the same 101 offsets for the mirror
reason (the byte is elided), which is the case prereg limit (ii) already discloses.

**Is H2d falsifying?** Partially — and the honest reading is a **narrowing**, not a kill.
Prereg limit (ii) says "a stderr that differs from another only inside the elided middle
still renders identically", which discloses the *elided-middle* case. H2d is adjacent but
not identical: the surviving byte is the **continuation byte of a character**, so the
cell says `\x85` for material that was a character, and the char/byte pair is
indistinguishable *in the arm the claim names*. The claim's wording — "the CHARACTER
U+0085 … now takes the `\u0085` spelling" — is not universally true of the FLAGFAIL arm;
it is true of the fixture's 28-byte payload. The L1 should treat this as a narrowing
amendment candidate for limit (ii), not as a silent repair.

### Classification: regression or pre-existing?

I ran every arm on the before tool and the filed tool (probe6, R2–R4). H2a, H2b and H2c
are **byte-identical before and after** — they are PRE-EXISTING gaps in arms the r90
repair does not touch, not r90 regressions. H2d is the only one that touches the repaired
arm; the before tool has the same boundary behaviour (it just spells both `\x85`).

---

## 6. The r89 escapes still hold on the filed tool (task item 2)

Measured on the filed tool (probe A3/A4/A9, probe12 R6):

- **0xFF vs literal (KFF6/KFF7 pair):** `bad \udcff tail` → `'bad \xff tail'`
  (`count('\xff')==1`, `count('\\xff')==0`); `literal \xff tail` → `'literal \\xff tail'`
  (`count('\\xff')==1`). Details differ. The pair holds; the r89 fixture reads KFF6/KFF7
  `tool=pass` on the filed tool.
- **Raw window 202 bytes:** the window is `raw[:100] + "…" (3 bytes) + raw[-99:]` =
  **202 raw bytes**, and the output is byte-for-byte `_escape_text(_decode_record(window))`
  (verified `True`).
- **Head/tail preservation:** head preserved (first 100 bytes intact), tail preserved
  (last 99 bytes intact), the middle elided with `…`, and the KFF8 headctl case keeps
  both the type name (`AttributeError`) and the message (`boom`).
- **`str.splitlines()` breakers are all escaped** — LF→`\n`, CR→`\r`, VT→`\x0b`,
  FF→`\x0c`, FS/GS/RS→`\x1c`/`\x1d`/`\x1e`, NEL→`\u0085`, LS→`\u2028`, PS→`\u2029`;
  **no raw breaker leaks into the cell in any case**.

One residual, not a regression: `_escape_text` leaves the C1 range (U+0080…U+009F) and
all other non-ASCII **raw** (`U+009B` → `'\x9b'` raw in the cell; that is CSI, an ANSI
control). The tool's own docstring only promises "below 0x20 or equal to 0x7f" is
escaped, so this is within the documented contract, but it is the same shape as the NEL
hole the r90 repair closed and it is unescaped in the no-verdict arm.

---

## 7. Deletion audit (task item 3)

`_one_line` is gone from the filed tool and nothing references it.

- `grep -c 'def _one_line(' tools/souji-record-agreement.py` → **0** (the prereg's own check).
- The only three occurrences of the token `_one_line` in the filed tool are
  `_one_line_bytes` (the live helper, lines 216 and 406) and one **docstring mention**
  (line 218) recording that `_one_line` was deleted in r90.
- **AST walk** of the module (`ast.parse` + `ast.walk`) for every `ast.Name`,
  `ast.Attribute`, `ast.alias`, `ast.keyword` and `ast.Constant` mentioning the name:
  **no load of `_one_line` exists** — the single hit is the `StrConst` docstring at
  line 217. Module-level defs after the deletion: `Report, _decode_record,
  _escape_record, _escape_text, _one_line_bytes, _stderr_tail, counts_of, git,
  git_bytes, git_env, main, paragraphs, read_at, resolve_rev, tally_of, truth_refusal,
  writer_binding`.
- **Dynamic-reference audit:** `getattr` / `eval` / `exec` calls, `str.format` /
  `format_map` with the name, and every `Subscript` — **none**. No `globals()`/
  `locals()` lookup can reach the name because it is not defined at all.
- **Import audit:** scanned 4357 non-tool `.py/.sh/.cfg/.toml/.json` files in the lane.
  **No test, fixture or module imports `_one_line` from the tool.** The only hits are
  (a) `census/round-89/controls/c2-before-tool.py:268` and
  (b) `census/round-90/controls/c2-before-tool.py:297` — the two **before-tool control
  copies**, which are self-contained snapshots of the r89 bytes that still *define*
  `_one_line` (they are the control arms, not importers of the tool); and
  (c) `census/round-40/*`, where the token is part of the unrelated identifier
  `missed_by_one_line` and the string `census/round-40/c2-counter.py:300`.
- **The module still imports cleanly** (`ast.parse` + `importlib` load; `hasattr(m,
  "_one_line")` is `False`, `hasattr(m, "_one_line_bytes")` is `True`).
- **The deletion was safe at the time it was made:** an AST walk of the *before* tool
  (`census/round-90/controls/c2-before-tool.py`, sha256 `f6fce6d1…`) finds **zero
  `Call` nodes** to `_one_line` — the helper was already dead code in the r89 bytes, so
  the deletion removed nothing live. This confirms the prereg's "zero callers" wording
  against the actual before bytes rather than against a grep.

Prereg limit (iv) says runtime dispatch is not exhaustively excluded. My audit agrees:
the AST and grep evidence is complete for the filed module and the lane, and the
dynamic-lookup audit found no route. I found **no dynamic reference**.

---

## 8. The path cell is not weakened (task item 4)

`_escape_record` is byte-based and unchanged (prereg limit (i)). The two path shapes are
**distinguishable**, and so are their literal-text twins:

```
char U+0085 (utf-8 c2 85)  -> '\xc2\x85'
raw byte 0x85              -> '\x85'
literal text \xc2\x85      -> '\\\\xc2\\\\x85'
literal text \x85          -> '\\\\x85'
all four distinct ? True
the path cell NEVER prints \u0085 : True
```

Confirmed end to end on the filed tool, with real untracked files in a hermetic repo:

```
MISMATCH\tK4\tchar-u0085-\xc2\x85.txt\tuncommitted-path\t??
MISMATCH\tK4\tliteral-\\\\u0085.txt\tuncommitted-path\t??
MISMATCH\tK4\traw-0x85-\x85.txt\tuncommitted-path\t??
```

The path cell keeps the **byte** spelling throughout and never emits `\u0085`, so the
r90 change to `_escape_text` cannot have introduced a path/char ambiguity. This half of
the claim is sound.

---

## 9. Findings summary

| ID | Severity | Finding | Artifact | Claim impact |
|---|---|---|---|---|
| **H1** | HIGH | The round's KFF9/KFF10 predicates are substring counts; a literal-text payload with no U+0085 / no 0x85 satisfies them. A one-token mutant that doubles the U+0085 branch (destroying injectivity and reversibility) **survives the r90 fixture 12/12, the r89 fixture 10/10 and the r87 12-row counter** with EXIT 0. | `mut/mutant.py` sha256 `5ec2e925…`; probe8/9/10 | The filed bytes satisfy the wording; the **frozen KILL RULE does not bind the word "injective"**. Remediation: add `count(bs*2+"u0085")==0` to KFF9 and `count(bs*2+"x85")==0` to KFF10 (mirrors the r89 KFF6/KFF7 discipline). |
| **H2a** | HIGH | FORGED arm: real LF, U+0085, U+2028, U+2029 all render the identical cell `a\nb`. The parent's `out.splitlines()` runs before `_escape_text`, so the r90 repair cannot reach this arm. | probe5 FORGED arm | Pre-existing (identical before/after). Out of the claim's FLAGFAIL scope; a K4-record-level reader ambiguity. |
| **H2b** | HIGH | REFUSED arm: a NEL in the refusal code silently truncates the reason (`splitlines()[0]`). | probe3 P4 | Pre-existing. |
| **H2c** | HIGH | no-verdict arm: `_stderr_tail` is unescaped — a raw TAB lands raw in the cell (the r87 byte-arm reader reads `MISMATCH` as the detail), a NEL drops the exception type name, raw ESC/CSI survive. | probe12 R1–R3 | Pre-existing. |
| **H2d** | HIGH | FLAGFAIL arm: at the 200-byte window junction the CHARACTER U+0085 renders with the RAW BYTE's spelling `\x85`; char and byte payloads produce **byte-identical** K4 rows. 102/298 offsets fail the KFF9 predicate for a genuine U+0085. | probe9 H1/H1b, probe11 | **Inside the arm the claim names.** Narrowing candidate for limit (ii). |
| M1 | MEDIUM | `_escape_text` leaves the C1 range (U+0080–U+009F, incl. CSI U+009B) and all non-ASCII raw. Within the tool's documented contract, unescaped in the no-verdict arm. | probe12 R6 | Pre-existing. |
| — | PASS | Deletion audit clean: `_one_line` absent, no AST load, no dynamic route, no importer in 4357 files; already dead in the before bytes (0 `Call` nodes). | §7 | Satisfies the claim's second half. |
| — | PASS | Path cell unchanged and injective on U+0085 vs raw 0x85 vs both literal twins; never prints `\u0085`. | §8 | Satisfies limit (i). |
| — | PASS | r89 escapes hold on the filed tool: 0xFF vs literal, 202-byte raw window, head/tail preservation, all `splitlines()` breakers escaped; r87 12-row counter `mismatches=0 errors=0`; r89 fixture 10/10. | §6 | The repair is not a trade. |

**No-work control:** none of the arms reaches the target without the repair — the before
arm reads `before_pass=10` and `tool_pass=12` requires the filed bytes. There is no
no-work path to `tool_pass=12`.

---

## 10. What I could NOT check

- I did not run the C1 counter or any C1 instrument; C1 is not my seat's scope.
- I did not verify the C2 arm against the r88-or-older tool bytes; prereg limit (v)
  excludes them and they are not filed.
- The r87 K4 counter's `mismatches=8` on a tool copy in a directory without the receipt
  writer beside it is a **layout artifact**, not a verdict on the bytes; I re-ran it with
  the writer correctly placed (`mut1fix/tools/`) and read `mismatches=0 errors=0`. I did
  not chase the artifact further.
- I did not attempt to run the tool against the real lane's `souji-receipt-write.py`
  with a hostile writer; all injections used a synthetic fake writer in a hermetic
  scratch repo, which is the same public path the fixture exercises.
- `_stderr_tail`'s treatment of U+2028/U+2029 (they also split `splitlines()`) I observed
  but did not exhaustively enumerate; the NEL case is the representative one.
- I did not attempt to verify the S353 capture or the Unicode source claim; I read the
  prereg's citation only.
- I made **no edits** to any lane file: the fixture, the tool and the controls are
  committed evidence and remain exactly as filed. The proposed remediation in H1 is
  **stated, not applied** — applying it is the L1's call, and it would change a frozen
  instrument.

---

## 11. Scratch and cleanup

All work was done under `/fast/scratch/hyaku/souji-r90/S90Sentinel/`:
`probe_escapes.py`, `probe3_arms.py`, `probe4_surrogate.py`, `probe5_forged.py`,
`probe6_diff.py`, `probe7_final.py`, `probe8_predicates.py`, `probe9_final.py`,
`probe10_remediation.py`, `probe11_kff9.py`, `probe12_reader.py`, `audit_deletion.py`,
`inject.py`, `inject2.py`, their `.out` receipts, the two mutant copies (`mut/`,
`mut2/`) and the fixture work dirs. **The whole scratch directory was removed before
this report was finalized; no scratch remains.** Receipts of the load-bearing runs are
quoted verbatim in this report. The only file I wrote in the lane is this report
(`.ufo/waves/round-90/w1/S90Sentinel.md`) and my seat dir
(`.ufo/waves/round-90/w1/S90Sentinel/`). No git/jj command was run in a mutating mode
anywhere; no fixture repository was created (all hermetic repos were plain `git init`
directories under my scratch, and no `git -C` was issued with an empty or unchecked
variable).
