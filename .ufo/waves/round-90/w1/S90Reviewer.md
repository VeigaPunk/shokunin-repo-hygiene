# S90Reviewer — souji round 90 independent re-measure (C1, C2, S353)

seat: S90Reviewer (leaf; no subagents). lane: /home/vgpnk/Projects/shokunin/souji-shokunin (id souji).
base bd760432df2cc3ba6c5f1ccc540b050fe2ac09e2; P e2a11c73b7d2bc9108a293486a31f137e4cbb7db; F fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f.
All numbers below were re-measured by this seat from committed bytes on 2026-11-08; no lane file was edited.
Scratch: /fast/scratch/hyaku/souji-r90/S90Reviewer (removed before yield; receipts copied here).

## Verdicts (short)

- **C1 (calibration 7): PASS — the frozen predicate re-derives cell for cell** (see §2 for the two official lines).
  The LD2b row is load-bearing: reconstructing the r90 file as `r89 bytes + LD2b line` reproduces sha256 d64d7695… exactly;
  on the appended `ZZ9<TAB>ABSENT` ledger row pristine/`m17`/`m17b` print `LEDGER-REFUSED id=ZZ9` and exit 1, while
  `m17c` raises `IndexError` with no marker (direct probe, §2.5).
- **C2 (operability 8): PASS — 12/12 vs 10/12, EXIT 0; control 10/10, EXIT 1**; the KFF9/KFF10 pair is independently
  failable in both directions (constructed mutants: 11/12 failing exactly KFF9, and 11/12 failing exactly KFF10, §4.3).
  `_one_line` has zero call sites in the r89 bytes, is gone from the filed tool, and nothing imports it (§5).
- **S353: capture byte-identical to the live page; version/revision as stated; quote present once, 18 words**; one
  LOW citation-precision issue (§7.3): the offset is normalization-dependent — 82360 is the sentence start under
  strip-tags-then-unescape (the convention that reproduces it) but 82615 under plain tag-strip without entity
  decoding, 82199/82357 (char/byte) under the `\n\t`->`' '` convention the scout used, and 82360 there is the
  sentence minus its first word. The quote is not a contiguous raw-HTML substring (tags split `BK` from `in`).
  No claim logic depends on the offset.

No HIGH or MEDIUM finding. One LOW (S353 offset, §7.3). No falsifying artifact found for either claim's stated wording.

## 1. Bytes measured (all committed at HEAD unless noted)

| artifact | sha256 | claimed |
|---|---|---|
| census/round-90/c1-false-rows.tsv | d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45 | same |
| census/round-87/c1-pointer-counter.py | fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b | same (UNCHANGED) |
| census/round-90/c1-clause-battery.py | e7265335e4458e68d2277dd0ad4f36e68999a7ba70363d60dc2155bd9cfa2d39 | same |
| census/round-90/c1-false-row-harness.py | c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe | same |
| census/round-90/c1-mutants.json | 392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5 | same |
| tests/fixtures/r90-k4-flagfail.py | d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa | same |
| tools/souji-record-agreement.py (HEAD:worktree) | d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561 | same |
| census/round-90/controls/c2-before-tool.py | f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd | same |
| census/round-90/srcs/tr14.html | 296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0 | same |

Provenance checks: `git show 755a46cb:tools/souji-record-agreement.py` = f6fce6d1… (the r89 filed bytes, i.e. the
C2 `--before` arm); `git show HEAD:tools/souji-record-agreement.py` = worktree = d095b52f…. The r90 tool is one
commit (4cb3a06f), `git show --stat` = 1 file, +10/−21. The committed pre-freeze receipts
(`prefreeze-c1-control.txt`, `prefreeze-c2-control.txt`, `prefreeze-c2-k4-regression.txt`) hash equal to HEAD blobs.

## 2. C1 — re-measure

### 2.1 Official after command (this seat)

```
python3 -B census/round-90/c1-clause-battery.py \
  --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90Reviewer/c1a2 --only r89,r90 --expect-killed 31
```

output (final lines; full 62-line stdout in `c1-after-official.txt` in this seat dir):

```
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0
…
MUTANT m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
MUTANT m17c-no-malformed pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT m18d-first-only pop=r89 killed=yes mismatches=1 errors=0 exit=1
MUTANT m18d-first-only pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m18d-first-only pop=r89 killed=yes mismatches=1 errors=0 exit=1 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31
```

This is cell for cell the prereg's required after line: `mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok
killed_r89=15 killed_r90=16 killed_total=31`, service exit status **0**; both pristine arms green on 57/58 rows
with 0 mismatches and 0 errors. The other 15 `MUTANT`/`MUTANT-PAIR` lines are killed=yes on both populations.

The 62-line stdout saved here has sha256
**d584dabb42326c352867595dfa11696f16a6133c0e96d9152dd1369a65915ce9** — identical to the L1's official after
receipt `census/round-90/records/c1-after.txt` and to the pre-freeze feasibility receipt
`census/round-90/records/prefreeze-c1-both.txt` (same command, all three byte-identical). Measurement note: the
service log line-wraps at ~100 columns and drops a space at the wrap on some long `MUTANT-PAIR` lines; the saved
file is the unwrapped, whitespace-repaired decode (`c1-after-official.raw.txt` keeps the raw log). The repair only
inserts the space at `errors=<n>exit=`; no field value was changed, and the result matches the two independent
receipts byte-for-byte.

### 2.2 Official do-nothing control (this seat)

```
python3 -B census/round-90/c1-clause-battery.py \
  --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90Reviewer/c1c2 --only r89 --expect-killed 15
```

captured stdout (this seat, `c1-control-official.txt`):

```
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
…
MUTANT m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15
```

service exit status **0**. `killed_r89=15`, `m17c` alive — the no-work arm cannot reach 31 (a control reaching the
target would be a HIGH finding; it does not). The captured stdout is **byte-identical** (sha256
d0e06880e58a5e6a691b2f8f3b49b74286864a83ef6f6ce2a75ff3773cad2127) to the committed
`census/round-90/records/prefreeze-c1-control.txt` / `controls/c1-before-r89-population.txt` pair; the file saved
here is the battery's 45 output lines only (my shell wrapper's `EXIT=` marker line removed, exit status shown above).

### 2.3 Population byte-level identity

- `tail -n +3 census/round-90/c1-false-rows.tsv | head -57` vs `tail -n +3 census/round-89/c1-false-rows.tsv`
  → byte-identical (diff empty); 57 rows.
- `cat census/round-89/c1-false-rows.tsv <last line of r90>` → sha256 **d64d7695…** = the committed r90 file.
  So r90 is exactly r89 plus the one appended LD2b line (the 2 comment/header lines are unchanged).
- Row counts: 57 + 1 = 58 data rows (`tail -n +3 | wc -l` = 58). LD2b row, tab-visible:
  `LD2b<TAB>ledger<TAB>BASE<TAB>r77<TAB>ZZ9<TAB>-<TAB>-<TAB>LEDGER-REFUSED<TAB>1<TAB>r90 C1: …`
- Frozen r77 ledger `census/round-77/c2-pointer-ledger.tsv` (sha256 011faa0e…): `ZZ9` absent; `P02` present at
  line 3 (`P02<TAB>ABSENT<TAB>-<TAB>…`). The r89 LD2 row's id could not reach the length guard; LD2b's can.
- Mutants: 16 members; the member objects (`id`, `old`, `new`) are equal to census/round-89/c1-mutants.json's
  16; `m17c-no-malformed` replaces `if len(r) < 3 or r[0] in ledger:` with `if r[0] in ledger:`.
- Battery/harness deltas vs r89 (diff): only the r90 PINS entry and `elif rid in ("LD2", "LD2b"):` plus docstrings;
  no arm, kill rule or summary line changed.

### 2.4 Harness ledger-append code (read)

`census/round-90/c1-false-row-harness.py:404-413`: for `rid in ("LD2","LD2b")` it appends
`f"{item}\tABSENT\n"` to the frozen ledger bytes; LD2b's `item` is `ZZ9`. Marker expected:
`LEDGER-REFUSED id=ZZ9`, row exit 1. No judgement code changed for lane/fixture rows.

### 2.5 Mechanism probe (direct, not via the battery)

Appending `ZZ9\tABSENT` to a scratch copy of the r77 ledger and running the counter on the r77 population:

```
pristine  rc=1  LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id
m17       rc=1  LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id   (length guard kept)
m17b      rc=1  LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id   (length guard kept)
m17c      rc=1  IndexError: list index out of range                 (no marker)
```

Exactly the prereg's MECHANISM paragraph: pristine/`m17`/`m17b` refuse, `m17c` executes
`ledger[r[0]] = (r[1], r[2])` on the 2-column row and raises. The marker proves refusal, not the branch; the branch
is attributed by the four mutants, as stated.

### 2.6 Cell-for-cell compare with the L1 receipt

`census/round-90/records/c1-after.txt` was untracked while I measured (the L1 was writing it); by the time my
official run finished it was complete at 62 lines. `diff` of my `c1-after-official.txt` against it: **no output —
byte-identical**, sha256 d584dabb… for both. The same 62 lines are also byte-identical to
`census/round-90/records/prefreeze-c1-both.txt` (the pre-freeze feasibility run of the same command, disclosed in
plan A0.3). Every header, both pristine arms, all 16 `MUTANT`/`MUTANT-PAIR` lines and the SUMMARY match; no
differing number exists to report.

## 3. C2 — re-measure

### 3.1 Official after command

```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-90/controls/c2-before-tool.py --work <scratch>
```

```
CASE KFF1 tool=pass before=pass
…
CASE KFF9  tool=pass before=fail
CASE KFF10 tool=pass before=fail
SUMMARY cases=12 tool_pass=12 before_pass=10
```

process exit status **0**. `diff` of my run against `census/round-90/records/c2-after.txt`: **no output — identical**
(sha256 094605c1be19d64277d0c895b5c440570aa937234518394aeb26865c67a2db39 for both, including headers, all 12 CASE
lines and SUMMARY; my captured file is `c2-after-mine.txt`).

### 3.2 Do-nothing control (r89 bytes as BOTH arms)

```
python3 -B tests/fixtures/r90-k4-flagfail.py \
  --tool census/round-90/controls/c2-before-tool.py \
  --before census/round-90/controls/c2-before-tool.py --work <scratch>
```

```
CASE KFF9  tool=fail before=fail
CASE KFF10 tool=fail before=fail
SUMMARY cases=12 tool_pass=10 before_pass=10
R90-FIXTURE-FAIL: the tool under test does not pass every case
```

process exit status **1**. `diff` against `census/round-90/records/prefreeze-c2-control.txt`: **no output —
identical** (sha256 a27f1cca476d9c17bd09497f64f6f94b331682e50ff32349f19b2b6f1f224806 for both; my captured file is
`c2-control-mine2.txt`). The control cannot reach 12/12.

### 3.3 Regression on the r87 12-row K4 counter

```
python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <scratch>
```

`SUMMARY rows=12 mismatches=0 errors=0`, EXIT 0; all 12 ROW lines `match=yes` (KH1/KH2, KU1/KU2, KF1-KF3, KG1/KG2,
KN1-KN3). Diff against `census/round-90/records/prefreeze-c2-k4-regression.txt`: identical except the scratch clone
path printed in the header (a scratch-path field, not a measurement).

### 3.4 The ten r89 cases

AST comparison of `tests/fixtures/r89-k4-flagfail.py` vs `tests/fixtures/r90-k4-flagfail.py`: the ten check
functions `case_short/trace/long/controls/empty/badbyte/literal/headctl/clean/refused` are AST-identical; only
`case_nelchar`/`case_nelbyte` are added. `run_case`/`make_kit`/`main` differ only by the R89->R90 environment
variable rename, the added cases and the both-arms pair block (confirmed by `diff -u`). Running the actual r89
fixture against the filed tool: `SUMMARY cases=10 tool_pass=10 before_pass=8`, EXIT 0 — every r89 case passes on
the r90 bytes.

## 4. Kill-rule reading (C2)

### 4.1 Source (r90 fixture lines 192-203, 264-276)

- `case_nelchar` (KFF9): one row; `"fatal: nel"`, `"marker"`; `count("\u0085") == 1`; `count("\x85") == 0`.
- `case_nelbyte` (KFF10): one row; `"fatal: nel"`, `"marker"`; `count("\x85") == 1`; `count("\u0085") == 0`.
- Pair block: for BOTH arms (after and before), `_nel_ok = _r9 != _r10 and len(_r9)==1 and len(_r10)==1`; then
  `KFF9 = KFF9 and _nel_ok`, `KFF10 = KFF10 and _nel_ok`. KFF6/KFF7 get the same treatment with their own pair.
  Each of KFF9/KFF10 therefore passes only when its own check AND the pair check pass, on each arm independently.

### 4.2 What the before tool actually does (measured, fixture functions imported from a scratch copy)

```
BEFORE own KFF9: False  own KFF10: True  pair differ: False
  nelchar row: ['the index-flag read failed (fatal: nel \\x85 marker\\n); tracked bytes are unverified']
  nelbyte row: ['the index-flag read failed (fatal: nel \\x85 marker\\n); tracked bytes are unverified']
AFTER  own KFF9: True   own KFF10: True  pair differ: True
  nelchar row: ['the index-flag read failed (fatal: nel \\u0085 marker\\n); tracked bytes are unverified']
  nelbyte row: ['the index-flag read failed (fatal: nel \\x85 marker\\n); tracked bytes are unverified']
```

So on the control the raw-byte case's OWN check passes (`\x85`), and KFF10 fails only through the pair check because
the two details are identical. That is exactly the prereg's sentence "KFF9 and KFF10 fail on both arms (their
details are identical)" — a control failure that is real, not a case-check failure. No number is overstated: the
control's `before_pass=10` does not count a case the before bytes actually satisfy.

### 4.3 Can each case fail independently? Yes — constructed mutants

Built two tool variants in scratch (from the filed bytes, one edit each) and ran the fixture's own `score()`:

- variant A (U+0085 printed twice): **passes 11/12, fails exactly KFF9** (KFF10 passes).
- variant B (byte 0x85 printed twice in the surrogate branch): **passes 11/12, fails exactly KFF10** (KFF9 passes).

So neither case is a duplicate of the other; the pair check does not collapse them into one predicate.

## 5. `_one_line` deletion

- Before tool (`census/round-90/controls/c2-before-tool.py`, r89 filed bytes): one `def _one_line(`, **zero call
  nodes** (AST walk: `calls 0 defs 1`); the only other occurrence is inside a docstring.
- Filed tool: `grep -c 'def _one_line('` = 0; no `_one_line(` call; AST `calls 0 defs 0`; the only remaining
  `_one_line` token is `_one_line_bytes` (a different function) plus a docstring mention.
- Nothing imports the symbol: repo-wide grep for `_one_line` finds only wave-artifact variants, old census
  control snapshots and the docstring; no `from tools.… import`, no `import` of the tool module anywhere in
  `tests/`/`tools/`/`census/` (fixtures execute it as a subprocess).
- No dynamic dispatch: AST walk for `getattr`/`setattr`/`globals`/`eval`/`exec`/`__import__` = 0 call nodes, and no
  string literal in the module is used to look the name up. Module `exec_module` succeeds; `_one_line` absent,
  `_escape_text` present.
- Stated limit (iv) is honoured: runtime dispatch is not exhaustively excluded by a static grep; I add the AST
  negative above, not a proof against reflection outside the module.

## 6. Tool diff audit (behavior beyond the claim)

`diff -u census/round-90/controls/c2-before-tool.py tools/souji-record-agreement.py` has exactly three hunks:

1. `_escape_text`: `0x85` removed from the `\x%02x` branch and added to the `\u%04x` branch (with a comment).
2. `_one_line_bytes` docstring reworded (the deleted helper named in prose).
3. the `def _one_line(...)` block deleted.

Direct probes on the filed bytes:

```
_escape_text("a\u0085b")   -> 'a\\u0085b'
_escape_text("a\udc85b")   -> 'a\\x85b'
_escape_text("a\u2028b")   -> 'a\\u2028b'
_escape_text("a\\x85b")    -> 'a\\\\x85b'
_escape_record("\u0085".encode()) -> '\\xc2\\x85'
```

`_escape_record` (path bytes) is byte-based and unchanged; a path's U+0085 already printed `\xc2\x85`, so stated
limit (i) holds. The pair is injective: character `\u0085`, raw byte `\x85`, literal text `\\x85`, path bytes
`\xc2\x85`.

**Scope note (INFO, not a verdict change):** `_escape_text` is shared by three cells — the delegated stderr tail
(the FLAGFAIL cell), the receipt-writer-refused exit line (`_escape_text(out.split(...))`) and the FORGED/REFUSED
payload (`_escape_text(out[len("FORGED "):])`). A U+0085 inside those two other messages also changes spelling from
`\x85` to `\u0085`. No committed fixture or check asserts the old spelling in those cells (repo-wide grep for
`\x85`/`0085` finds only the K4 fixtures' literal-escape controls case, which is literal backslash text and
unchanged), and both spellings remain single-line, so I found no line that changes a VERDICT outside the FLAGFAIL
cell. Stated limit (i) says the repair "covers `_escape_text`"; that is accurate; it should not be read as "the
FLAGFAIL cell only".

## 7. S353 source re-fetch

### 7.1 Bytes

`curl -sS -D headers https://www.unicode.org/reports/tr14/` on 2026-11-08:
HTTP/2 200, 226166 bytes, sha256 **296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0**.
`cmp` with `census/round-90/srcs/tr14.html`: identical. Headers report `last-modified: Tue, 01 Sep 2026 21:01:07 GMT`.

### 7.2 Version/revision named by the capture

Header block: Version **Unicode 18.0.0**; Date 2026-09-01; This Version `tr14-57.html`; Revision **57** (also
`Revision 57:` in the change log at line 4603). Matches the prereg/S353 row. Supporting data file:
`census/round-90/srcs/LineBreak.txt` re-fetched live (HTTP 200, 266206 bytes, sha256
ae8cf1970c73f3f1a12d77852df96c4b2b1723ca8b388e36bb5739250c6849de) is byte-identical, and its line 95 reads
`0085 ; NL # Cc <control-0085>`.

### 7.3 Quote, occurrence count, offset, words

Quote: `The NL class acts like BK in all respects (there is a mandatory break after any NEL character).`

- Raw HTML bytes: **0** occurrences (the page wraps it in `<a class="charclass">` tags: `…like <a…>BK</a>` newline
  tab `in all respects…`).
- Tag-stripped text with `'\n\t' -> ' '` (the convention the S90ScoutSources receipt defines): **1** occurrence,
  at **char offset 82199 / byte offset 82357**; 18 words (whitespace split).
- Without the `\n\t` collapse (plain `re.sub(r'<[^>]+>','',html)`): 0 exact occurrences; the prefix
  `The NL class acts like BK` is at char 82615.
- `strip-then-html.unescape` (entity decode after tag removal): the prefix `The NL class acts like BK` is at char
  82360 (entity decoding shifts the text); the exact single-space quote still occurs 0 times. `unescape-then-strip`
  places the prefix at char 82266. In neither variant is 82360 the start of the *quoted sentence with its original
  internal whitespace*.

**LOW finding (citation precision, not substance):** the prereg (and S353's row, and the untracked knowledge note)
state "tag-stripped offset 82360" for the quote. That number is **normalization-dependent**: it is exactly right
under strip-tags-then-unescape (the prefix/sentence start lands at char 82360 there), but plain tag-strip gives
82615, and the `'\n\t' -> ' '` byte-offset convention used by S90ScoutSources puts the sentence at 82357, with
82360 being the offset of `" NL class acts like BK …"` (sentence minus its first word, leading space kept). The
quote is not a contiguous raw-HTML substring (the `<a>` tags split `BK` from `in all respects`). The quote is
present, occurs exactly once after whitespace normalization, and is 18 words, so the source row's substance —
U+0085 is classed NL and a break after NEL is mandatory — is present verbatim and unchanged; no claim number
depends on the offset. Record the normalization with the offset when the source row is next edited.

## 8. Findings by severity

- **HIGH:** none. No artifact produced by this seat falsifies either claim's stated wording.
- **MEDIUM:** none.
- **LOW — S353 offset convention (§7.3):** `tag-stripped offset 82360` is reproducible only if the tag strip also
  entity-decodes; plain tag-strip places the sentence start at 82615, and the scout's `\n\t`->`' '` byte convention
  at 82357 (82360 there = sentence minus `The`). The quote is not a contiguous raw-HTML substring. Record the
  normalization; the quote's presence, uniqueness and 18-word count are unaffected.
- **INFO — shared-helper scope (§6):** the spelling change reaches the refusal/REFUSED cells as well as the
  FLAGFAIL cell; no verdict change found in any committed check.
- **INFO — inherited BASE:** the C1 harness judges lane/ledger rows at `BASE = e65538e7…` (r78), unchanged from
  r87-r89; not a r90 change, but the C1 claim's "lane" rows are not judged at the r90 base.
- **INFO —** the after receipts (`records/c1-after.txt`, `c2-after.txt`, `prefreeze-c1-both.txt`) were untracked
  while I measured; the L1 owns committing them. My re-runs are the check that they are reproducible.

## 9. What I could NOT check

- Reflection/external dispatch: a caller outside this repo could import a deleted `_one_line`; repo-wide grep +
  AST find none, and the module has no `getattr` dispatch. Stated limit (iv) remains.
- The r90 after receipts' eventual committed blobs: measured from the working tree while the L1 was writing them;
  my own re-runs are quoted in full, so a post-file edit would be visible as a diff.
- Universal injectivity of the escape rule: only the enumerated KFF9/KFF10 (and KFF6/KFF7) pairs were measured, as
  the claim's stated limit (ii) says.
- Other lanes' tools/consumers: none import this tool; no parsing of the NEL spelling outside the K4 fixtures.
- Canonical runtime / same-identity rerouting / saturation claims: C1 and C2 have no such object (no runtime, no
  routing, no saturation metric). The analogous identity property is the byte-level artifact pinning; all nine
  pinned hashes matched their stated values, and the after runs reproduce the receipts byte-for-byte.

## 10. Commands (all from the lane root unless noted)

```
sha256sum census/round-90/c1-false-rows.tsv census/round-87/c1-pointer-counter.py \
  census/round-90/c1-clause-battery.py census/round-90/c1-false-row-harness.py \
  census/round-90/c1-mutants.json tests/fixtures/r90-k4-flagfail.py \
  tools/souji-record-agreement.py census/round-90/controls/c2-before-tool.py \
  census/round-90/srcs/tr14.html
git log --oneline -12 ; git status --porcelain ; git show --stat fd25bfc5 e2a11c73 1952c1c7 4cb3a06f
diff -u census/round-90/controls/c2-before-tool.py tools/souji-record-agreement.py
diff -u census/round-89/c1-false-row-harness.py census/round-90/c1-false-row-harness.py
diff -u census/round-89/c1-clause-battery.py census/round-90/c1-clause-battery.py
diff <(tail -n +3 census/round-90/c1-false-rows.tsv | head -57) <(tail -n +3 census/round-89/c1-false-rows.tsv)
cat census/round-89/c1-false-rows.tsv <(tail -1 census/round-90/c1-false-rows.tsv) | sha256sum   # d64d7695…
grep -n '^ZZ9\|^P02' census/round-77/c2-pointer-ledger.tsv
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90Reviewer/c1a2 --only r89,r90 --expect-killed 31
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90Reviewer/c1c2 --only r89 --expect-killed 15
python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-90/controls/c2-before-tool.py --work <empty>
python3 -B tests/fixtures/r90-k4-flagfail.py --tool census/round-90/controls/c2-before-tool.py \
  --before census/round-90/controls/c2-before-tool.py --work <empty>
python3 -B tests/fixtures/r89-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-89/controls/c2-before-tool.py --work <empty>
python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <empty>
python3 -B -c '…ast walk: _one_line calls/defs, getattr count…'
python3 -B -c '…import filed tool; _escape_text/_escape_record probes…'
curl -sS -D headers -o tr14-live.html https://www.unicode.org/reports/tr14/   # 200, 226166, sha 296df533…
python3 -B -c '…tag-strip/offset/occurrence/word-count over the fetched bytes…'
```

Scratch receipts kept in this seat dir: `c1-after-official.txt` (62-line battery stdout, sha d584dabb…) and
`c1-after-official.raw.txt` (the service log before unwrapping), `c1-control-official.txt` (sha d0e06880…),
`c2-after-mine.txt` (sha 094605c1…), `c2-control-mine2.txt` (sha a27f1cca…), `k4-regression-mine.txt`,
`probe-source-offsets.txt`, `probe-kill-independence.txt`, `probe-ld2b-mutants.txt`, `probe-escape-cells.txt`,
`probe-live-fetch.txt` (tr14/LineBreak sha, sizes, cmp and HTTP headers).
Scratch dir `/fast/scratch/hyaku/souji-r90/S90Reviewer` removed before yield; nothing was written to the lane outside
this seat dir and this report.

## 11. Exact tails for the structural checks

- `sha256sum` on the nine artifacts of §1: every line equals the claimed hash (table above).
- `grep -c 'def _one_line(' tools/souji-record-agreement.py` → `0`; `grep -n '_one_line(' tools/souji-record-agreement.py`
  → no output, rc 1. The before tool has one definition line and no call.
- AST walks: `census/round-90/controls/c2-before-tool.py calls 0 defs 1`; `tools/souji-record-agreement.py calls 0
  defs 0`; `_one_line` name in loaded module: False; dynamic-dispatch call nodes (`getattr/setattr/globals/eval/
  exec/__import__`): 0.
- `diff -u census/round-90/controls/c2-before-tool.py tools/souji-record-agreement.py` → exactly three hunks
  (`_escape_text` 0x85 branch; `_one_line_bytes` docstring; `def _one_line` deletion), rc 1 (differences).
- `diff <(tail -n +3 census/round-90/c1-false-rows.tsv | head -57) <(tail -n +3 census/round-89/c1-false-rows.tsv)`
  → no output, rc 0. `cat census/round-89/c1-false-rows.tsv <ld2b-line> | sha256sum` → d64d7695….
- r89 fixture on the filed tool: `SUMMARY cases=10 tool_pass=10 before_pass=8`, process rc 0.
- r87 K4 counter: `SUMMARY rows=12 mismatches=0 errors=0` and its own `EXIT=0` line, process rc 0.
- `cmp` live tr14 vs capture → identical; `cmp` live LineBreak.txt vs capture → identical.
- `git status --porcelain` at end: `M SCORECARD.md`, `M corpus/README.md`, `M corpus/SOURCES.md`,
  `?? census/round-90/records/{c1-after,c2-after,prefreeze-c1-both}.txt`, `?? census/round-90/srcs/tr13.html`,
  `?? corpus/knowledge/nel-byte-character-pair.md`, `?? corpus/lessons/round-90.md`, `?? plans/round-90.md` —
  all L1/other-seat files; this seat wrote only its seat dir and this report.
