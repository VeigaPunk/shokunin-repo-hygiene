# S90ExecC3 — instrument-integrity audit (souji r90, C1 + C2)

Seat: S90ExecC3 (executor, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` (id `souji`).
Round 90, one v1 wave. Lane base `bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2`; instruments P1 `1952c1c7`;
C2 repair `4cb3a06f`; P2 `e2a11c73`; prereg F `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (= HEAD, detached).
Prereg read first: `census/round-90/preregistration.txt` (150 lines).

**VERDICT: NO UNEXPECTED change found in any of the four inventories.**
C1's r90 delta is exactly the new population row LD2b plus the mechanical pin/docstring/comment/branch
wiring in the harness, the battery and the mutants note. C2's r90 delta is exactly the U+0085 spelling
change, four explanatory comment lines, one docstring rewrite, and the deletion of the dead `_one_line`
helper. The counter is byte-identical to the r87/r89 bytes. The UNEXPECTED list is empty.

## 0. Hash equality (all eight match the prereg verbatim)

| artifact | measured sha256 | prereg |
|---|---|---|
| `census/round-90/c1-false-rows.tsv` | `d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45` | match |
| `census/round-87/c1-pointer-counter.py` | `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b` | match |
| `census/round-90/c1-mutants.json` | `392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5` | match |
| `census/round-90/c1-clause-battery.py` | `e7265335e4458e68d2277dd0ad4f36e68999a7ba70363d60dc2155bd9cfa2d39` | match |
| `census/round-90/c1-false-row-harness.py` | `c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe` | match |
| `tests/fixtures/r90-k4-flagfail.py` | `d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa` | match |
| `tools/souji-record-agreement.py` | `d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561` | match |
| `census/round-90/controls/c2-before-tool.py` | `f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd` | match |

Counter at three revisions, `git show <rev>:census/round-87/c1-pointer-counter.py | sha256sum`:
`bd760432` = `master` = `HEAD` = `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b`.
`git diff --stat bd760432 HEAD -- census/round-87/ census/round-89/ census/round-77/` is EMPTY: no earlier
committed evidence moved.

`census/round-90/controls/c2-before-tool.py` is byte-identical to the r89 filed tool
(`git show bd760432:tools/souji-record-agreement.py | sha256sum` = `f6fce6d1…`; `cmp` against the control
= identical).

## 1. Inventory A — population `c1-false-rows.tsv` (r89 → r90)

Method: `git show bd760432:census/round-89/c1-false-rows.tsv` vs
`git show HEAD:census/round-90/c1-false-rows.tsv`, `diff -u` and `cmp`.
r89: 59 lines = 2 comment lines + 57 data rows. r90: 60 lines = 2 comment lines + 58 data rows.

Every changed line (exactly one addition, at the end, after LD2):

```
+LD2b	ledger	BASE	r77	ZZ9	-	-	LEDGER-REFUSED	1	r90 C1: the SAME malformed-row guard reached under an id ABSENT from the frozen r77 ledger. The appended row is `ZZ9<TAB>ABSENT` (2 columns); pristine refuses it on len(r)<3 and prints `LEDGER-REFUSED id=ZZ9`, while m17c (len guard dropped) writes ledger[ZZ9]=(r[1], r[2]) and raises IndexError with no marker. LD2 could not bind this guard because its id P02 is already in the ledger (r89 A1).
```

- Prefix proof: `head -n 59 <r90-file> | cmp - <r89-file>` → `PREFIX-57-ROWS-BYTE-IDENTICAL` (the first 59
  lines, comments included, are byte-identical; LD2b is the only added line).
- LD2b row shape: 10 tab-separated fields; `awk -F'\t' '!/^#/ && NF!=10'` finds none across all 58 rows.
- `ZZ9` is ABSENT from the frozen r77 ledger: `grep -n 'ZZ9' census/round-77/c2-pointer-ledger.tsv` →
  no match (exit 1). The ledger's own ids `P01` (line 2) and `P02` (line 3) are present, which is why
  r89 LD2 (id P02) could not reach the length guard.
- Ledger is unchanged since the lane base: `git diff --stat bd760432 HEAD -- census/round-77/` empty.

Unaccounted lines: NONE.

## 2. Inventory B — harness `c1-false-row-harness.py` (r89 448 lines → r90 458 lines)

`diff -U0` produced exactly four hunks; every changed/added line is listed:

| hunk (r90 lines) | lines | classification |
|---|---|---|
| `@@ -2 +2,8 @@` | new title line `souji r90 C1 counter: the r89 harness plus ONE pinned population … 58 rows =` + 6 explanatory docstring lines; the r89 docstring paragraph is retained verbatim | DOCSTRING |
| `@@ -118 +125,2 @@` | POP_SHA gains `"d64d7695…": 58` on a new line after the r89 pin line (which gains a comma) | PIN |
| `@@ -395,0 +404,2 @@` | two-line comment: `# r90: LD2b appends the same 2-column shape under an id ABSENT …` | COMMENT |
| `@@ -398 +408 @@` | `elif rid == "LD2":` → `elif rid in ("LD2", "LD2b"):` | LD2b BRANCH |

No judgment code, row scoring, summary line, revision list, kill rule or fixture builder changed. The LD2b
branch appends only `f"{item}\tABSENT\n"` (item = `ZZ9` from the row), which produces the 2-column ledger
row the claim states.

Unaccounted lines: NONE.

## 3. Inventory C — battery `c1-clause-battery.py` (r89 168 lines → r90 177 lines)

`diff -U0` produced exactly two hunks:

| hunk (r90 lines) | lines | classification |
|---|---|---|
| `@@ -2 +2,8 @@` | new r90 docstring paragraph (6 lines) + the r89 paragraph retained | DOCSTRING |
| `@@ -74,2 +81,4 @@` | PINS: r89 entry path changed from `os.path.join(HERE, "c1-false-rows.tsv")` to `os.path.join(FLEET, "souji-shokunin/census/round-89/c1-false-rows.tsv")` (same sha `04570a6…`, same 57), and a new r90 entry `(os.path.join(HERE, "c1-false-rows.tsv"), "d64d7695…", 58)` added | PIN (relocation + new entry) |

**Flagged line** (the only changed line outside "the pin value itself"): the r89 pin's LOCATION moved from
`HERE` to the explicit `census/round-89/` path. This is required because `HERE` is now `round-90`, was done
for r86 by the r87 battery for the same reason (the r87 docstring says so), and pins the SAME bytes
(`04570a6…`, 57 rows) that `git show bd760432:census/round-89/c1-false-rows.tsv` hashes to. Classification:
EXPECTED PIN RELOCATION, not a judgment change.

Observation for the L1 (not a falsification): the prereg's C1 stated limit (i) says "this round changes the
population and its harness only", while the battery bytes also change (docstring + PINS entry). The prereg
itself names the r90 battery sha and its own docstring says "one more PINS entry", and no arm, kill rule or
summary line changed, so the delta is pin metadata for the new population — but the sentence "population and
its harness only" is narrower than the file set (population + harness + battery pin/docstring + mutants note).
Record as an observation; nothing here alters the counter, kill rule, or predicate.

Runtime header (measured, `--only r90,foo` forces exit 2 after the header, no arm executed):

```
# counter path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-87/c1-pointer-counter.py sha256=fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b
# harness path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-90/c1-false-row-harness.py sha256=c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe
# mutants path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-90/c1-mutants.json sha256=392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5
# population r89 path=…/census/round-89/c1-false-rows.tsv sha256=04570a64855978bf697af71c161fe215945da5849f2f393fee15bb0d9f21e093 rows=57
# population r90 path=…/census/round-90/c1-false-rows.tsv sha256=d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45 rows=58
```

— i.e. the battery's own header prints the unchanged counter sha `fd0a8e24…` (the prereg's counter-sha
equality requirement), plus the r89 control pin and the r90 pin with their claimed row counts.

Unaccounted lines: NONE.

## 4. Inventory D — mutants `c1-mutants.json` (r89 112 lines → r90 112 lines)

`diff -u` shows exactly ONE changed line: the `"note"` value (line 2). The new note states the sixteen
members are byte-identical to `census/round-89/c1-mutants.json` and names r89 as the do-nothing control.

- Member count: 16 in both files; ids identical and in the same order:
  `m6-digest-blind, m7-round-blind, m8-w-only-shapes, m9-basename-only, m10-records-as-wave,
  m11-class-enum, c7-census-in-tree, m14-short-shape, m12-token-on-line, m16-nf6b-punct,
  m17-duplicate-id, m18-whole-before, m18b-alnum-before, m17b-target-keyed, m17c-no-malformed,
  m18d-first-only`.
- Members block byte-identity: with the `"note"` line removed, `cmp` of the two files →
  `MEMBERS-BLOCK-BYTE-IDENTICAL`. Canonical JSON equality also True.
- Every mutant's `old` occurs EXACTLY ONCE in `census/round-87/c1-pointer-counter.py` (verified for all 16;
  counts all `1`), so no edit can be invalid.
- `m17c-no-malformed` (verbatim, both files): `old = "            if len(r) < 3 or r[0] in ledger:\n"`,
  `new = "            if r[0] in ledger:  # m17c: malformed-row guard dropped\n"`. The counter's
  `_ledger` at `census/round-87/c1-pointer-counter.py:491` is `if len(r) < 3 or r[0] in ledger:` and line 494
  is `ledger[r[0]] = (r[1], r[2])`, so dropping the length guard on a 2-column row raises IndexError.

Unaccounted lines: NONE.

## 5. Inventory E — C2 fixture `tests/fixtures/r90-k4-flagfail.py` (r89 258 → r90 292 lines)

`diff -U0` gives 18 hunks; every one is classified here:

| hunk (r90 lines) | content | classification |
|---|---|---|
| `@@ -2,2 +2,7 @@` | docstring title r89→r90 + 5 lines stating the r90 change (pair spelling) | DOCSTRING |
| `@@ -23,0 +29,2 @@` | docstring case list gains KFF9/KFF10 lines | DOCSTRING |
| `@@ -25 +32 @@` | docstring "`--before` (the r87 tool bytes)" → "(the r89 tool bytes)" | DOCSTRING (correction) |
| `@@ -40 +47 @@` | FAKE_WRITER header comment `r89` → `r90` | COSMETIC COMMENT |
| `@@ -50 +57 @@` | `R89_STDERR_MODE` → `R90_STDERR_MODE` | MECHANICAL RENAME (fixture-internal; both arms use this fixture) |
| `@@ -61,0 +69,2 @@` | stderr map gains `"nelchar": b"fatal: nel \xc2\x85 marker\n"` and `"nelbyte": b"fatal: nel \x85 marker\n"` | NEW-CASE INPUT (r90) |
| `@@ -67 +76 @@` | `R89_REFUSED` → `R90_REFUSED` | MECHANICAL RENAME |
| `@@ -78,2 +87,2 @@` | git author/committer name+email `r89`/`r89.invalid` → `r90` | COSMETIC (fixture git identity) |
| `@@ -116 +125 @@` | seed commit message `r89 fixture seed` → `r90 fixture seed` | COSMETIC |
| `@@ -123,2 +132,2 @@` | run_case env names `R89_STDERR_MODE`/`R89_REFUSED` → `R90_*` | MECHANICAL RENAME |
| `@@ -181,0 +191,15 @@` | new `case_nelchar` (KFF9: exactly one `\u0085`, zero `\x85`, one line, head/tail text kept) and `case_nelbyte` (KFF10: exactly one `\x85`, zero `\u0085`) | NEW CHECKS (r90) |
| `@@ -197,0 +222,2 @@` | CASES table gains KFF9/KFF10 tuples | NEW CASES (r90) |
| `@@ -221 +247 @@` | fatal prefix `R89-FIXTURE-FATAL` → `R90-…` (work under /tmp guard) | COSMETIC string |
| `@@ -224 +250 @@` | fatal prefix (work-not-empty guard) | COSMETIC string |
| `@@ -235 +261 @@` | fatal prefix (fixture error) | COSMETIC string |
| `@@ -238,5 +264,13 @@` | pair checks now loop over BOTH arms (`for kit, arm in ((after_kit, after), (before_kit, old))`); KFF6/KFF7 pair applied to both arms; KFF9/KFF10 pair (`_r9 != _r10`, both one line) added and bound to both arms | DISCLOSED RULE CHANGE (prereg C2 stated limit iii) |
| `@@ -248 +282 @@` | fatal prefix (tool-does-not-pass) | COSMETIC string |
| `@@ -251 +285 @@` | fatal prefix (no measured delta) | COSMETIC string |

Ten r89 cases unchanged: AST source segments of `case_short, case_trace, case_long, case_controls,
case_empty, case_clean, case_refused, case_badbyte, case_literal, case_headctl` are IDENTICAL in the two
fixtures; the r89 CASES tuples (KFF1-KFF8, KFC1, KFC2) are unchanged; `score` and `make_kit` bodies are
unchanged (no hunk touches them; the only run_case change is the env-name rename above).

Pair checks on both arms: as tabled at `@@ -238,5 +264,13 @@`. The KFF9/KFF10 case checks are still the
case's own check ANDed with the pair check; for the r89 (before) bytes both KFF9 and KFF10 checks fail and
the pair also fails, so the before arm is scored by the same rule. Measured, both arms from the fixture
itself (`--tool tools/souji-record-agreement.py --before census/round-90/controls/c2-before-tool.py`):

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
CASE KFF9 tool=pass before=fail
CASE KFF10 tool=pass before=fail
SUMMARY cases=12 tool_pass=12 before_pass=10
EXIT 0
```

Unaccounted lines: NONE.

## 6. Inventory F — tool `tools/souji-record-agreement.py` (`git diff bd760432 master`)

31 lines changed: 10 insertions, 21 deletions. Five hunks, all classified; NO UNEXPECTED hunk:

1. `@@ -189 +189 @@` (inside `_escape_text`): `elif o < 0x20 or o == 0x7F or o == 0x85:` →
   `elif o < 0x20 or o == 0x7F:` — **U+0085 SPELLING** (the character leaves the `\xNN` branch).
2. `@@ -191 +191 @@`: `elif o in (0x2028, 0x2029):` → `elif o in (0x85, 0x2028, 0x2029):` —
   **U+0085 SPELLING** (the character joins the `\uNNNN` branch).
3. `@@ -193,0 +194,4 @@`: four comment lines explaining the r89 collision (U+DC85 surrogate vs U+0085
   character, UAX #14 NL, S353) — **COMMENT**.
4. `@@ -213,3 +217,4 @@`: `_one_line_bytes` docstring rewritten to call `_one_line` "deleted in r90 as dead
   code" and to re-wrap the raw-window explanation — **DOCSTRING** (no code outside the docstring changed).
5. `@@ -297,16 +301,0 @@`: deletion of `def _one_line(text: str, limit: int = 200) -> str:` and its body (16 lines
   including the docstring, the escape-first body and trailing blank lines) — **DEAD-CODE DELETION**.

Direct measurement of the spelling (module loaded from the committed bytes; no writes):

```
before (c2-before-tool.py): char U+0085 esc='\\x85'   raw U+DC85 esc='\\x85'   distinct: False
after  (HEAD tool):          char U+0085 esc='\\u0085' raw U+DC85 esc='\\x85'   distinct: True
after  one-line counts:      char cell splitlines=1, byte cell splitlines=1
```

(The doubled backslashes are `repr` output; the literal spellings are `\x85` and `\u0085`.) This matches the
claim's mechanism exactly: raw byte 0x85 → `\x85` in both revisions; CHARACTER U+0085 → `\u0085` only after
the repair; the pair is distinct only after the repair.

Dead-code proof: `grep -c 'def _one_line(' tools/souji-record-agreement.py` = `0`;
`grep -c '_one_line(' tools/souji-record-agreement.py` = `0` (the only `_one_line` hits are `_one_line_bytes`
and the docstring backtick mention). In the r89 bytes the helper existed at line 297 with ZERO callers: the
only `_one_line(`-shaped call is `_one_line_bytes(raw)` at line 417, plus the docstring mention at 213.
`ast.parse` + `importlib` execution of the committed module succeeds, and `_one_line_bytes` is present while
`_one_line` is absent.

`_escape_record` (path bytes) has no hunk: unchanged, as the prereg's stated limit (i) says.

Unaccounted lines: NONE.

## 7. Additional measured C1 binding evidence (line-level, beyond the diff)

The r90 change is claimed to be the population+harness only, and LD2b to be the load-bearing row. I ran the
committed r90 harness directly on the committed population (scratch only; no lane writes):

- Pristine counter, r90 population (58 rows):

```
ROW LD1  where=ledger rev=BASE item=P01 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD1b where=ledger rev=BASE item=P01 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD2  where=ledger rev=BASE item=P02 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD2b where=ledger rev=BASE item=ZZ9 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
SUMMARY rows=58 mismatches=0 accepted=0 refused_true=0 errors=0
EXIT 0
```

- `m17c-no-malformed` mutant (built in scratch from the frozen counter, edit count 1), SAME r90 population:

```
ROW LD1  … match=yes
ROW LD1b … match=yes
ROW LD2  … match=yes
ROW LD2b where=ledger rev=BASE item=ZZ9 class=- expect=LEDGER-REFUSED/1 got=- rc=1 match=no
SUMMARY rows=58 mismatches=1 accepted=0 refused_true=0 errors=0
EXIT 1
```

Only LD2b goes red under the mutant: the 57 r89 rows are still green under m17c, so the r90 kill is
attributable to LD2b alone (and the mutant crashes with rc=1 and no `LEDGER-REFUSED` marker, as the claim's
mechanism predicts). The mutant harness ran 76 s; output saved as a seat receipt.

- `m17c-no-malformed` on the r89 control population (57 rows), receipt
  `receipt-c1-harness-r89-m17c.out`:

```
ROW LD1  where=ledger rev=BASE item=P01 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD1b where=ledger rev=BASE item=P01 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
ROW LD2  where=ledger rev=BASE item=P02 class=- expect=LEDGER-REFUSED/1 got=LEDGER-REFUSED rc=1 match=yes
SUMMARY rows=57 mismatches=0 accepted=0 refused_true=0 errors=0
EXIT 0
```

m17c survives the whole r89 population (0 mismatches) and is killed by exactly LD2b on r90
(1 mismatch). The mutant was built from `census/round-87/c1-pointer-counter.py` with its single
`old`→`new` replacement applied exactly once (sha `c6b549a358e578ed5c230d2fd5d0aeef616acf28322ef00b868708a8107abb12`).

## 8. UNEXPECTED list

**EMPTY.** No changed line in population, harness, battery, mutants, fixture or tool falls outside the
categories the assignment enumerates (pin, LD2b branch/row, docstring, mutants note, U+0085 spelling,
dead-code deletion, comment) — with two items that I name explicitly rather than silently absorb:

1. `census/round-90/c1-clause-battery.py` PINS r89 entry: the LOCATION changed (`HERE` → explicit round-89
   path) while sha and row count are unchanged. Classified EXPECTED PIN RELOCATION (same pinned bytes; the
   r87 battery did the same for r86). It is not a judgment change.
2. `census/round-90/c1-mutants.json`: the file sha differs from r89 because of the note line only; the
   sixteen member texts are byte-identical (verified by `cmp` with the note line removed). The prereg's
   phrase "the r89 sixteen byte-identical" is true of the member block, not of the whole file.

Neither is a HIGH finding: no judgment code, kill rule, predicate, counter or case check moved.

## 9. What I could NOT check

- The full two-population 31-kill battery (`--only r89,r90 --expect-killed 31`): I launched it in scratch
  over the committed bytes and it exceeded the 300 s job cap after the pristine arm and five mutants. Exact
  partial state (receipt `receipt-c1-battery-r89-partial.out`, truncated by the kill, not by the battery):
  `ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0`, then m6, m7, m8, m9 and m10 each
  `pop=r89 killed=yes` (m8/m9 with 2/4 mismatches). This does NOT establish `killed_r89=15`,
  `killed_r90=16` or `killed_total=31`; those predicate values are the battery seat's to measure. My direct
  harness runs above establish the population/line-binding question independently. The header (with the
  counter sha) was separately captured in 0.1 s by the same code path and is receipted.
- Dynamic dispatch to `_one_line` beyond static grep + import (prereg C2 stated limit iv): excluded only
  statically; no `getattr`/string lookup was found in the module, but I do not claim exhaustive runtime
  exclusion.
- Universal injectivity of the escaping rule (prereg C2 stated limit ii): only the enumerated KFF9/KFF10
  pair was exercised.
- The r77 ledger's frozen status is not pinned by sha inside the instruments; I verified instead that
  `census/round-77/` is unchanged between `bd760432` and HEAD and that `ZZ9` is absent from it at HEAD.

## 10. Scratch and receipts

Scratch root `/fast/scratch/hyaku/souji-r90/S90ExecC3/` (never /tmp); deleted before yield. Receipts copied
into this seat dir before deletion:
`receipt-hashes.txt`, `receipt-c1-battery-header.out`,
`receipt-c1-harness-r90-pristine.out`, `receipt-c1-harness-r90-m17c.out`,
`receipt-c1-harness-r89-m17c.out`, `receipt-c1-battery-r89-partial.out`,
`receipt-c2-fixture-r90.out`, `receipt-diffs.txt`.
Receipt sha256 (in this seat dir):

```
3a6126c410d2407b84a8b8d221fab4df3af2d6a7aaff6176d944d053c7617abf  receipt-c1-battery-header.out
36b5526094074cef79b7d1f84f84670b0d44aae579b9adfcf6c15a645d3fcd53  receipt-c1-battery-r89-partial.out
063324c6be70068aa0d63ee03fc704d196c7300424adb5ebd0238bfc4a60d031  receipt-c1-harness-r89-m17c.out
f8b411e4acee0064dc407435db6d18cbbef754c3c0a785a859a7819eca1347b6  receipt-c1-harness-r90-m17c.out
a784edd22698b543d9f501ecc62791199831d7e7fcfcc09201f68eec157e3df6  receipt-c1-harness-r90-pristine.out
094605c1be19d64277d0c895b5c440570aa937234518394aeb26865c67a2db39  receipt-c2-fixture-r90.out
d9d6517a733363e4b50c5e65a0a3450f32be81d074593104a54de614d7d09bfc  receipt-diffs.txt
1d1268c86d9f730e870b58013548f81af621f725b0d52b3ec0635262ed57cf64  receipt-hashes.txt
```
No lane file outside this dir and the report was written; no git/jj mutation was run in the lane.

Tooling: none installed (pure stdlib python3, git read-only, coreutils). No host service, sysctl, pacman or
PATH directory touched.

## 11. Commands run (exact, with output tails)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse --show-toplevel && git rev-parse HEAD && git log --oneline -8
→ /home/vgpnk/Projects/shokunin/souji-shokunin
→ fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f
→ fd25bfc5 round-90: preregistration (F) — …
```

```
sha256sum census/round-90/c1-false-rows.tsv census/round-87/c1-pointer-counter.py census/round-90/c1-mutants.json \
  census/round-90/c1-clause-battery.py census/round-90/c1-false-row-harness.py tests/fixtures/r90-k4-flagfail.py \
  tools/souji-record-agreement.py census/round-90/controls/c2-before-tool.py
→ all eight equal to the prereg values in the table above
```

```
for r in bd760432 master HEAD; do git show $r:census/round-87/c1-pointer-counter.py | sha256sum; done
→ fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b (×3)
```

```
diff -u <(git show bd760432:census/round-89/c1-false-rows.tsv) <(git show HEAD:census/round-90/c1-false-rows.tsv)
→ @@ -57,3 +57,4 @@ ; one `+LD2b…` line only
head -n 59 <r90> | cmp - <r89>   → PREFIX-57-ROWS-BYTE-IDENTICAL
```

```
diff -U0 r89/r90 c1-false-row-harness.py   → 4 hunks (docstring, POP_SHA, comment, `rid in ("LD2","LD2b")`)
diff -U0 r89/r90 c1-clause-battery.py      → 2 hunks (docstring, PINS r89 path + r90 entry)
diff -u  r89/r90 c1-mutants.json           → 1 changed line (the "note")
grep -v '^ "note"' … | cmp - …             → MEMBERS-BLOCK-BYTE-IDENTICAL
```

```
git diff bd760432 master -- tools/souji-record-agreement.py
→ 5 hunks: -189, -191, +194,4 (comment), -213 docstring, -297,16 (delete _one_line); 10 insertions(+), 21 deletions(-)
grep -c 'def _one_line(' tools/souji-record-agreement.py → 0
grep -c '_one_line(' tools/souji-record-agreement.py     → 0
```

```
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --work <scratch>/work-header --only r90,foo
→ header lines (counter sha fd0a8e24…, r89 pin 04570a6…/57, r90 pin d64d7695…/58); EXIT 2 (deliberate bad --only)
```

```
python3 -B census/round-90/c1-false-row-harness.py --counter census/round-87/c1-pointer-counter.py \
  --lane …/souji-shokunin --fleet-root … --work <scratch>/work-h-r90-pristine \
  --population census/round-90/c1-false-rows.tsv
→ SUMMARY rows=58 mismatches=0 accepted=0 refused_true=0 errors=0 ; EXIT 0 ; LD2b match=yes rc=1

same harness --counter <scratch>/counter-m17c.py (m17c edit applied once)
→ SUMMARY rows=58 mismatches=1 accepted=0 refused_true=0 errors=0 ; EXIT 1 ; LD2b match=no got=- rc=1
```

```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-90/controls/c2-before-tool.py --work <scratch>/work-fixture
→ SUMMARY cases=12 tool_pass=12 before_pass=10 ; EXIT 0 (full CASE table in §5)
```

All fixture git activity was confined to the fixture's own repos under my scratch work dirs (the committed
fixture builds them); I ran no mutating git command in the lane.
