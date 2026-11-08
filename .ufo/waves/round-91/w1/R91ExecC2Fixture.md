# R91ExecC2Fixture — C2 both arms + variant discrimination + KFF13 scan attack

Seat: R91ExecC2Fixture (executor, souji r91 w1). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin, read-only.
Owned write scope: this directory only. No git/jj mutation, no commit, no build/lint/test gate run (parent owns it).
Scratch: /fast/scratch/hyaku/souji-r91/R91ExecC2Fixture — deleted before yield; every receipt below is copied here.

## 0. Instrument bytes re-checked before use (all match the prereg)

```
21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c  tools/souji-record-agreement.py
d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561  census/round-91/controls/c2-before-tool.py
f815abbc8a6c1fa00ed55db196dc14799b29e3e54e95d505cb4cce4e3c980478  tests/fixtures/r91-k4-flagfail.py
0610c5d2ed6bd652e08106b8e7190efe05ce5a65dc0622630818f156cdeb597a  census/round-91/c2-variant-probe.py
24198d8e67c3fbc2197c4454fe94845d5e09ae494510f76779e9eec5e143a03a  census/round-91/variants/double-backslash-tool.py
f2f52510b26641f4134052d147b7a296af563b661f3d7b215df3bc3cb733d5c7  census/round-91/variants/raw-newline-tool.py
dfcbd0cc2fc1decd8dc8974d26bd4d8647620df2bd2c3056c7b3185d8493900f  census/round-91/variants/keep-helper-tool.py
4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e  census/round-87/c2-k4-counter.py
```
Every hash equals the value printed in `census/round-91/preregistration.txt`.

## 1. Arm A — after arm on the filed tool (VERDICT: reproduces exactly)

Command (cwd = lane root):
`python3 -B tests/fixtures/r91-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-91/controls/c2-before-tool.py --work <empty>`

Receipt: `receipt-armA-filed-tool.out` (stderr `receipt-armA-filed-tool.err`, empty). Exit **0**.

```
# tool path=/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-record-agreement.py sha256=21e5c7408fef10f20b503cc1dcb8ee9cd288f87da13b402655b0f0532acfea2c
# before path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-91/controls/c2-before-tool.py sha256=d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561
# fixture sha256=f815abbc8a6c1fa00ed55db196dc14799b29e3e54e95d505cb4cce4e3c980478
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
SUMMARY cases=15 tool_pass=15 before_pass=14
```

Predicate (a) `SUMMARY cases=15 tool_pass=15 before_pass=14` and EXIT 0: **met on committed bytes.** The delta is
exactly one case (KFF11), and the before arm fails it — the repaired cut is the only measured behaviour change.

## 2. Arm B — do-nothing control, the r90 tool as BOTH arms (VERDICT: reproduces exactly)

Command: `python3 -B tests/fixtures/r91-k4-flagfail.py --tool census/round-91/controls/c2-before-tool.py --before census/round-91/controls/c2-before-tool.py --work <empty>`

Receipt: `receipt-armB-r90-both-arms.out` / `.err`. Exit **1**; stderr `R91-FIXTURE-FAIL: the tool under test does not pass every case`.

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
CASE KFF11 tool=fail before=fail
CASE KFF12 tool=pass before=pass
CASE KFF13 tool=pass before=pass
SUMMARY cases=15 tool_pass=14 before_pass=14
```

Control sentence "prints `SUMMARY cases=15 tool_pass=14 before_pass=14`, KFF11 fails on both arms, EXIT 1": **met.**
No work does not reach 15, and the r90 tool still satisfies the other fourteen cases (no-harm on the r90 surface).

## 3. Variant probe (VERDICT: both directions reproduce exactly)

Receipts: `receipt-probe-r91.out` (EXIT 0), `receipt-probe-r90.out` (EXIT 0); stderr files empty.

```
=== r91 fixture ===
VARIANT double-backslash fixture=r91 cases=15 pass=14 failed=KFF9 detected=yes
VARIANT keep-helper fixture=r91 cases=15 pass=14 failed=KFF13 detected=yes
VARIANT raw-newline fixture=r91 cases=15 pass=14 failed=KFF12 detected=yes
SUMMARY variants=3 fixture=r91 detected=3
=== r90 fixture ===
VARIANT double-backslash fixture=r90 cases=12 pass=12 failed=- detected=no
VARIANT keep-helper fixture=r90 cases=12 pass=12 failed=- detected=no
VARIANT raw-newline fixture=r90 cases=12 pass=12 failed=- detected=no
SUMMARY variants=3 fixture=r90 detected=0
```

Variant table — variant → mutated site (from `diff` against the filed tool) → the ONE case it fails →
the exact conjunct that returns False (measured, `receipt-diag-variant-conjuncts.txt`, reproducer
`diag-variant-conjuncts.py`):

| variant | mutation | failing case | exact conjunct | measured cell |
|---|---|---|---|---|
| `double-backslash` | line 198 `out.append("\\u%04x" % o)` → `"\\\\u%04x"` | KFF9 (mode `nelchar`) | `rows[0].count(bs * 2 + "u0085") == 0` → **False** (the other two conjuncts, `count(bs+"u0085")==1` and `count(bs+"x85")==0`, are both True — the doubled spelling still *contains* the single-one, which is why the r90 fixture's single count passed it) | `'... (fatal: nel \\\\u0085 marker tailtkn\\n); tracked bytes are unverified'` |
| `raw-newline` | new `_one_line_bytes` wrapper: `.replace("marker", "marker\n", 1)` | KFF12 (mode `nelchar`) | `"tailtkn" in rows[0]` → **False**; the cell is truncated at the injected newline | `'the index-flag read failed (fatal: nel \\u0085 marker'` (tail lost; the remainder falls outside the `MISMATCH\tK4\t` prefix) |
| `keep-helper` | appended `def _one_line(text, limit=200)` with no caller | KFF13 (`decl`) | `src.count("def _one_line(") == 0` → **False** (also `_one_line(` count 1) | scan `(1, 1)` |

All three are *single-case* failures: 14/15 on the r91 fixture, 12/12 on the r90 fixture. Predicates (b)
`SUMMARY variants=3 fixture=r91 detected=3` EXIT 0 and control (ii) `SUMMARY variants=3 fixture=r90 detected=0`
EXIT 0 are **met on committed bytes**; the r90 fixture's blindness is confirmed to be about the fixture, not about a
generic tool difference (all three variants are byte-different from the filed tool and still pass it 12/12).

## 4. KFF11 control claim (item 3) — verified

Arm B above is exactly this run (r90 tool as `--tool` **and** as `--before`): `CASE KFF11 tool=fail before=fail`,
`SUMMARY cases=15 tool_pass=14 before_pass=14`, EXIT 1. The r90 tool does not render either spelling for the
straddling payload (`receipt-diag-variant-conjuncts.txt`, mode `nelcut` on the r90-derived variants:
`'fatal: nel' -> True | count(\x85)==0 -> True | count(\u0085)==0 -> True` holds only for the *repaired* tool; the
before arm's KFF11 fail is the orphan `\x85`). Control wording: **met.**

## 5. KFF13 source-scan attack (item 4) — the check is a literal-substring scan and fails in BOTH directions

Reproducer: `kff13-scan-attack.py` (lane root + scratch parent), receipt `receipt-kff13-scan-attack.txt`.
The filed tool's own scan counts are `def _one_line( = 0`, `_one_line( = 0`; its only `_one_line` text is line 261,
`` (`_one_line`, deleted in r90 as dead code) `` — note it does **not** match, because the next character is `,`.

### 5a. FALSE-GREEN (fail-open) — a real dead helper passes KFF13

Crafted tool = filed bytes **plus** `def _one_line (text: str) -> str: ...` (one space before the paren; legal
Python, binds the name — `_one_line('x')` returns `'x'`, verified). sha256 `d50d77b175941bf7fd2203de7eb377ef2c7b565617356eb6761a09a01d6b73e5`.

```
=== fixture --tool dead-helper -> EXIT 0 ===
CASE KFF13 tool=pass before=pass
SUMMARY cases=15 tool_pass=15 before_pass=14
```

Scan level: a spaced **call** `out = _one_line (raw)` is equally invisible (`_one_line( = 0`). The scan cannot
distinguish "the helper is deleted" from "the helper is spelled with a space".

### 5b. FALSE-FAIL (fail-closed) — a docstring that merely MENTIONS `_one_line(` fails KFF13

Crafted tool = filed bytes with **one character** changed: line 261 `(`_one_line`,` → `(`_one_line(`,`. Behaviourally
identical (all 14 other cases pass). sha256 `3b80b8369eaecda8e7c2c39840c0f734a06f70a3ca3174a1d0238e89440a5c19`.

```
=== fixture --tool mention -> EXIT 1 ===
CASE KFF13 tool=fail before=pass
SUMMARY cases=15 tool_pass=14 before_pass=14
stderr: R91-FIXTURE-FAIL: the tool under test does not pass every case
```

Scan level: `docstring mention ... _one_line(=1 KFF13=False`. A comment, a docstring, or a changelog line that
names the deleted helper with its call form turns the fixture red for a correct tool. The filed tool sits **one
character** from that state.

### 5c. Verdict on KFF13

- As a **limit** (narrow, acceptable-if-recorded): the case is a static substring scan, so it is neither sound nor
  complete for "no `_one_line(` definition or call"; it fails closed on documentation (5b) and fails open on a
  spaced definition/call (5a). 5b is harmless to the claim (it can only reject a good tool, never accept a bad one).
- As a **defect** (fail-open): 5a lets a tool that literally re-introduces the deleted helper pass the very case
  named "the dead escape-first helper stays deleted". This is not the residual the claim's stated limit (ii) names —
  limit (ii) says "a dynamic caller constructed outside the source text is not exhaustively excluded", while 5a is a
  definition **inside** the source text, in ordinary Python, never touching a dynamic construct.

### FALSIFIES-WORDING

The claim sentence

> "The r91 fixture enforces the four clauses the r90 wording claimed but did not measure: … and the tool source
> carries no `_one_line(` definition or call (KFF13)."

is falsified in its **enforcement** attribution: the r91 fixture does not enforce "no `_one_line(` definition or
call"; it enforces the literal byte string `_one_line(`. Reproducer:
`.ufo/waves/round-91/w1/R91ExecC2Fixture/kff13-scan-attack.py`, receipt
`.ufo/waves/round-91/w1/R91ExecC2Fixture/receipt-kff13-scan-attack.txt` — crafted tool sha256 `d50d77b1…` (filed
bytes + a real `def _one_line (` helper) scores `CASE KFF13 tool=pass` / `SUMMARY cases=15 tool_pass=15
before_pass=14` / EXIT 0. Scope of the falsification: it does **not** touch the claim's statements about the *filed*
tool's bytes (0 occurrences of either spelling, re-verified) nor predicates (a), (b), (c) or control (i)/(ii), all of
which re-derive. Suggested narrow amendment for the L1 to record (wording only, no instrument change):
stated limit (ii) also covers a definition or call that spells the name with whitespace before the paren
(`def _one_line (`), which the scan misses; KFF13 measures the literal `_one_line(` string, not the property.

## 6. Verdict summary

| arm | predicate as frozen | measured | verdict |
|---|---|---|---|
| A — fixture, filed tool vs r90 before | `SUMMARY cases=15 tool_pass=15 before_pass=14`, EXIT 0 | identical, EXIT 0 | PASS |
| B — control, r90 tool as both arms | `SUMMARY cases=15 tool_pass=14 before_pass=14`, KFF11 fail both, EXIT 1 | identical, EXIT 1 | PASS |
| probe — r91 fixture | `SUMMARY variants=3 fixture=r91 detected=3`, EXIT 0 | identical, EXIT 0 | PASS |
| probe — r90 fixture (control) | `SUMMARY variants=3 fixture=r90 detected=0`, EXIT 0 | identical, EXIT 0 | PASS |
| KFF13 scan attack | — (attack item) | false-fail on a one-character docstring mention; false-green on a real spaced `def _one_line (` | DEFECT (fail-open) + LIMIT (fail-closed); sentence-level FALSIFIES-WORDING recorded above |

Out of this seat's scope and not run here (no fabrication): predicate (c) the r87 12-row K4 regression, and C1's
battery. Everything above was executed read-only on lane bytes; the lane was not modified (`tools/`, `tests/`,
`census/` untouched — instrument hashes in §0 were re-computed at the end of the seat and re-match).

## 7. Files delivered

- `.ufo/waves/round-91/w1/R91ExecC2Fixture.md` (this report)
- `.ufo/waves/round-91/w1/R91ExecC2Fixture/receipt-armA-filed-tool.out` / `.err`
- `.ufo/waves/round-91/w1/R91ExecC2Fixture/receipt-armB-r90-both-arms.out` / `.err`
- `.ufo/waves/round-91/w1/R91ExecC2Fixture/receipt-probe-r91.out` / `.err`, `receipt-probe-r90.out` / `.err`
- `.ufo/waves/round-91/w1/R91ExecC2Fixture/receipt-diag-variant-conjuncts.txt`, `diag-variant-conjuncts.py`
- `.ufo/waves/round-91/w1/R91ExecC2Fixture/receipt-kff13-scan-attack.txt`, `kff13-scan-attack.py`

Scratch `/fast/scratch/hyaku/souji-r91/R91ExecC2Fixture` removed before yield (verified absent: `test ! -e` printed
`SCRATCH_GONE`). No tool install, upgrade or version change was made or needed. No file outside this seat dir and this
report was written; no `__pycache__`/`*.pyc` left behind (every run used `python3 -B`).

Lane state observed at the end of the seat (data, not authored by this seat — recorded so the L1 can separate the
wave's working-tree bytes from mine): `git -C <lane> status --porcelain` shows `M corpus/QUALITY.md`,
`M corpus/SOURCES.md`, `?? census/round-91/records/`, `?? corpus/knowledge/utf8-window-sequence-boundary.md`; no
instrument byte differs, and the C1 population/counter cross-check re-matches the prereg:
`fdc3d23839527fc1b67ef78945d0e537811ba28a8a2156fb9c598946a02bc460  census/round-91/c1-false-rows.tsv`,
`fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b  census/round-87/c1-pointer-counter.py`.
