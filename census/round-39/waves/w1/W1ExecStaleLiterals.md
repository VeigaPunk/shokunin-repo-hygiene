# W1ExecStaleLiterals — R13: exact bytes behind LOG:1855, LOG:1862, QUALITY:209

Seat: executor (leaf). Item: R13 residual stale literals, C1 items `R39-C1-11`, `R39-C1-12`,
`R39-C1-13`.
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base: `ed30b7f5b77939c9073348d810730bc4f355708d` (prereg). Freeze: `b769bfb84a264d8b284c09bc211d99f39a3e9126`
(`git cat-file -t` = commit; `git merge-base --is-ancestor b769bfb HEAD` → yes; base ancestor of freeze → yes).
Observed lane tip during this seat: `790d16b6492f67a8c8a7d13a596d92d3f01af4fe`, whose only working-tree
delta was four untracked `census/round-39/records/*-after.txt` files (`git status --porcelain`).

Advisory seat: I ran no fixture, installed nothing, created no scratch directory (no file was written
outside this report), and ran only read-only git.

---

## 0. Commands

All run from the fleet root with an absolute lane path; recorded verbatim below with their output.

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
790d16b6492f67a8c8a7d13a596d92d3f01af4fe
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR==1855||NR==1862{printf "LOG.md:%d: %s\n", NR, $0}' LOG.md; awk 'NR==209{printf "QUALITY.md:%d: %s\n", NR, $0}' corpus/QUALITY.md
```
(printed the three lines quoted in §1; long lines were also read byte-exactly with
`read ... LOG.md:raw:1855-1855`, `LOG.md:raw:1862-1862`, `corpus/QUALITY.md:raw:209-209`)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in census/round-37/records/c2-before.txt census/round-37/records/c2-after.txt census/round-37/records/c1-after.txt census/round-38/records/c1-before.txt; do echo "=== $f ==="; git log --format='%H %h %ad %s' --date=short -- "$f" | head -5; done
=== census/round-37/records/c2-before.txt ===
861c2ba268883d271d0b5d0e4884a0948a9c354c 861c2ba 2026-10-28 round-37: final receipt set at 4c257b7 (C1 11/0; C2 12 cases base_fail=9 escapes=9; C3 6/6)
8edcb04212b641203862921297655a1d329808e4 8edcb04 2026-10-28 round-37: regenerate before receipts with final instruments; S236 line/scope correction; honest live-run label; new named limits
d30476d25e999d0db93ec2619b44ea7dc221a653 d30476d 2026-10-28 round-37 A1/A2: pin the register, receipt-bound citations, selftest-arm cells; drift hardlink/parent-swap nofollow walk, property env-witness, measured case
d5c6498c5f72a63c9df32b26ee143e8d775eebbd d5c6498 2026-10-28 round-37: freeze claims, counters, register and before-control receipts (C1 citation reconcile, C2 escape fixture, C3 mutant battery)
=== census/round-37/records/c2-after.txt ===
02b43398ffd295a399c7097ab0d8b2eb70fb490a 02b4339 2026-10-28 round-37: lesson shape (S238 row, locators, M2 fail-proof, final landing) and receipts with headers
93a10b656e132af785817e06b823e7f2cce643b4 93a10b6 2026-10-28 round-37: receipts at e91c0a1018150366396959ef3833ca46f13626d4
40bbd2e03d763cc1e5a7c67e3a9e79c5bbfa4bca 40bbd2e 2026-10-28 round-37: receipts at the final tip
bbefcee6e011d9b4225e057bac346a9f42e0bf68 bbefcee 2026-10-28 round-37: final receipt set at e6be059 (C1 11/0, fixture 16/16, C2 12/9/9, C3 6/6)
861c2ba268883d271d0b5d0e4884a0948a9c354c 861c2ba 2026-10-28 round-37: final receipt set at 4c257b7 (C1 11/0; C2 12 cases base_fail=9 escapes=9; C3 6/6)
=== census/round-37/records/c1-after.txt ===
02b43398ffd295a399c7097ab0d8b2eb70fb490a 02b4339 2026-10-28 round-37: lesson shape (S238 row, locators, M2 fail-proof, final landing) and receipts with headers
40bbd2e03d763cc1e5a7c67e3a9e79c5bbfa4bca 40bbd2e 2026-10-28 round-37: receipts at the final tip
b491596491ed4057c11e298cdde0ab813a58b0b5 b491596 2026-10-28 round-37: C1 receipts at the final tip
bbefcee6e011d9b4225e057bac346a9f42e0bf68 bbefcee 2026-10-28 round-37: final receipt set at e6be059 (C1 11/0, fixture 16/16, C2 12/9/9, C3 6/6)
861c2ba268883d271d0b5d0e4884a0948a9c354c 861c2ba 2026-10-28 round-37: final receipt set at 4c257b7 (C1 11/0; C2 12 cases base_fail=9 escapes=9; C3 6/6)
=== census/round-38/records/c1-before.txt ===
4090ee5b04ca3205d61c044b89fd9f318cf9850c 4090ee5 2026-10-28 round-38: freeze claims, commit-arm reconciler, drift write-envelope and record fixtures, do-nothing controls
```
(Last commit touching each receipt: `c2-before.txt` → `861c2ba`; `c2-after.txt` and `c1-after.txt` →
`02b4339`; the r38 control → `4090ee5`. Both r37 receipts are therefore **frozen before the r38
corrections** that cite them.)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in census/round-37/records/c2-before.txt census/round-37/records/c2-after.txt census/round-37/records/c1-after.txt; do echo "=== $f ==="; grep -n 'SUMMARY' "$f"; done
=== census/round-37/records/c2-before.txt ===
14:SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
=== census/round-37/records/c2-after.txt ===
15:SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
=== census/round-37/records/c1-after.txt ===
3:SUMMARY cells=11 mismatches=0
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== c2-before @861c2ba =="; git show 861c2ba:census/round-37/records/c2-before.txt | grep -n SUMMARY; echo "== c2-before @02b4339 =="; git show 02b4339:census/round-37/records/c2-before.txt | grep -n SUMMARY; echo "== c2-after @02b4339 =="; git show 02b4339:census/round-37/records/c2-after.txt | grep -n SUMMARY; echo "== c1-after @02b4339 =="; git show 02b4339:census/round-37/records/c1-after.txt | grep -n SUMMARY; echo "== c1-before @861c2ba =="; git show 861c2ba:census/round-37/records/c1-before.txt | grep -n SUMMARY
== c2-before @861c2ba ==
14:SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
== c2-before @02b4339 ==
14:SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
== c2-after @02b4339 ==
15:SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
== c1-after @02b4339 ==
3:SUMMARY cells=11 mismatches=0
== c1-before @861c2ba ==
14:SUMMARY cells=11 mismatches=11
21:SUMMARY cells=9 mismatches=3
32:SUMMARY cells=9 mismatches=9
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in census/round-37/records/c2-before.txt census/round-37/records/c2-after.txt census/round-37/records/c1-after.txt; do printf '%s 861c2ba=%s 02b4339=%s HEAD=%s\n' "$f" "$(git rev-parse 861c2ba:$f)" "$(git rev-parse 02b4339:$f)" "$(git rev-parse HEAD:$f)"; done
census/round-37/records/c2-before.txt 861c2ba=ac576bdf07e54bcc385d2ddc187d5e62092c9386 02b4339=ac576bdf07e54bcc385d2ddc187d5e62092c9386 HEAD=ac576bdf07e54bcc385d2ddc187d5e62092c9386
census/round-37/records/c2-after.txt 861c2ba=44ff9472bde3fbb30346cbb123a30be6093d52d2 02b4339=688da31281e287ded7b720ab72eb46db8f0c2636 HEAD=688da31281e287ded7b720ab72eb46db8f0c2636
census/round-37/records/c1-after.txt 861c2ba=969329b069f8e8d2ef915f2a85656d4be3dcdc8a 02b4339=ae17e61062c17f5a892f61585555c0974cc1e7dd HEAD=ae17e61062c17f5a892f61585555c0974cc1e7dd
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== c2-before 10-16 =="; sed -n '10,16p' census/round-37/records/c2-before.txt
case-json-gitfile-write=FAIL
case-json-symlink-child=FAIL
case-record-symlink=FAIL
case-measured=PASS
SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
rc=1
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git grep -n -e 'cases=9' -e 'pass=3' -e 'fail=6' -e 'escapes=9' ed30b7f -- .      # 538 distinct (path,line) carriers, §4
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git grep -n -F 'escapes=4' ed30b7f -- . ; git grep -n -F 'escapes=4' HEAD -- .
ed30b7f:census/round-38/cells.tsv:2:R38-C1-1	SCORECARD.md	| R38-C1-1 |	escapes=9	escapes=4	census/round-37/records/c2-after.txt	02b4339...
ed30b7f:census/round-38/cells.tsv:11:R38-C1-10	corpus/QUALITY.md	R38-C1-10	escapes=9	escapes=4	census/round-37/records/c2-before.txt	861c2ba...
(HEAD: the same two lines, and nothing else)
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --all --oneline -S'escapes=4' | head -5
4090ee5 round-38: freeze claims, commit-arm reconciler, drift write-envelope and record fixtures, do-nothing controls
0cd4ecd
9dc6f9a
```
(`0cd4ecd` and `9dc6f9a` are distinct commits whose diff is the r38 freeze content: each adds only
`census/round-38/cells.tsv` and never a receipt.)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 02b4339:census/round-37/preregistration.txt | grep -n -e 'cases=6' -e 'base_fail>=3' -e 'cells=9'
18:  Target (frozen): `SUMMARY cells=9 mismatches=0`, rc 0, where each register row's
27:           line exists -> cells=9 mismatches=9.
39:  Target (frozen): `SUMMARY cases=6 pass=6 fail=0 base_fail>=3
51:           -> cases=6 pass=2 fail=4 base_fail=4 control=ESCAPE-REPRODUCED.
71:  C1 = "souji-citation-reconcile prints cells=9 mismatches=0 at the landing
73:  C2 = "the r37 escape fixture prints cases=6 pass=6 fail=0 base_fail>=3
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git grep -n -F 'cases=9 base_fail=6' ed30b7f -- .
ed30b7f:LOG.md:1862:- The frozen predicate sentences were superseded ... against receipts at `cells=11` / `cases=9 base_fail=6`; ...
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && a=$(git show ed30b7f:corpus/QUALITY.md | sed -n '209p' | sha256sum); b=$(sed -n '209p' corpus/QUALITY.md | sha256sum); echo "base=$a"; echo "head=$b"; git show ed30b7f:LOG.md | sed -n '1855p;1862p' | sha256sum; sed -n '1855p;1862p' LOG.md | sha256sum; git diff -U0 ed30b7f HEAD -- LOG.md corpus/QUALITY.md | grep -E '^@@'
base=12ede8ea1a654bc77bd7db545db2d760cb9a7cf7e6361672b23b368d5bb31b50  -
head=12ede8ea1a654bc77bd7db545db2d760cb9a7cf7e6361672b23b368d5bb31b50  -
1add82028708fa1956207231bec056429ed63a675030ad78c1d61a848dd9fdec  -
1add82028708fa1956207231bec056429ed63a675030ad78c1d61a848dd9fdec  -
@@ -1871,0 +1872,6 @@ Owned axis scores unchanged (calibration 7, coverage 8, operability 8). No tools
@@ -218,0 +219,4 @@ R38-C1-10 the Q84 evidence cell's ...
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git blame -L 1875,1877 --date=short LOG.md | cut -c1-90; git blame -L 222,222 --date=short corpus/QUALITY.md | cut -c1-90
c0b007b (souji-shokunin 2026-10-28 1875) R39-C1-11 — LOG-line-1855 (the r37 C2 bullet) s
c0b007b (souji-shokunin 2026-10-28 1876)
c0b007b (souji-shokunin 2026-10-28 1877) R39-C1-12 — LOG-line-1862 states the superseded
c0b007b (souji-shokunin 2026-10-28 222) R39-C1-13 — QUALITY-line-209's "(0)" reads the d
```

---

## 1. The three target lines, bytes

`LOG.md:1855` (byte-identical at base and at HEAD, sha256 pair above):

> - C2 operability: `tools/souji-worktree-drift.py` gets a whitelisted child env (`GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL/SYSTEM=/dev/null`, no inherited `GIT_*`), `--root` containment (`RECORD-OUTSIDE-ROOT`), and an `--json` guard over every measured path with an `O_NOFOLLOW` write on the resolved path. New fixture `tests/fixtures/r37-drift-escapes.py` reproduces six escapes on the r36 blob (`cases=9 pass=3 fail=6 base_fail=6`, rc 1) and none on the landing (`cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0); r36 consumers stay green (drift 12/12, report gate 21/21, r27 gate 4/4). Sources S236 (GIT_TRACE_REFS) and S237 (GIT_CONFIG_NOSYSTEM) ground the W2/W3 env-scrub repair; the `trace2-event` regression case has no admitted source (disclosed in the lesson Gate).

`LOG.md:1862` (byte-identical at base and at HEAD):

> - The frozen predicate sentences were superseded append-only in the same round (block after the FROZEN PREDICATE SENTENCE in the prereg, naming `0be9bd0bf0c8143483bc4da609a6225b2c47ab64`) after wave-1 connector seat W1ConnOverlap showed the original letters still read `cells=9` / `cases=6 base_fail>=3` against receipts at `cells=11` / `cases=9 base_fail=6`; the target strings that bind are the amended ones in A1.3/A2.3/A2.4, now stated in the same file.

`corpus/QUALITY.md:209` (byte-identical at base and at HEAD), evidence cell only:

> `corpus/lessons/round-37.md` `## Claims` C2; `census/round-37/records/c2-before.txt` (4 escapes) vs `c2-after.txt` (0)

Q84 criterion text (unchanged): "... the base must reproduce >=3 escapes and the candidate must show none".

Verdict §1: **PASS** — all three lines are present at the stated numbers in both the base revision and
the audited tip; neither file was rewritten in place (both diffs are pure additions at `+1872,6` and
`+219,4`).

---

## 2. Receipts that hold the values (path, revision, blob, SUMMARY)

| ref | path | revision (commit the blob is last written at) | blob | line | SUMMARY / observed |
|---|---|---|---|---|---|
| R-a | `census/round-37/records/c2-before.txt` | `861c2ba268883d271d0b5d0e4884a0948a9c354c` | `ac576bdf…` (== HEAD) | 14–15 | `SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` / `rc=1` |
| R-b | `census/round-37/records/c2-after.txt` | `02b43398ffd295a399c7097ab0d8b2eb70fb490a` | `688da312…` (== HEAD) | 15–16 | `SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` / `rc=0` |
| R-c | `census/round-37/records/c1-after.txt` | `02b4339…` | `ae17e610…` (== HEAD) | 3 | `SUMMARY cells=11 mismatches=0` |
| R-d | `census/round-37/records/c1-before.txt` | `861c2ba…` | — | 14 / 21 / 32 | `SUMMARY cells=11 mismatches=11` (final counter+register) / `SUMMARY cells=9 mismatches=3` (A1.1, 9-cell register) / `SUMMARY cells=9 mismatches=9` |
| R-e | `census/round-37/records/consumers-after.txt` | `bbefcee6e011d9b4225e057bac346a9f42e0bf68` (header: measured at `e6be059d1e341375f367335c3deac456afb4f65e`) | — | 15 / 40 / 51 | `SUMMARY cases=12 pass=12 fail=0 control=STUB-REJECTED` (drift 12/12) / `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED` (report gate 21/21) / `cases=4 pass=4 control=FALSE-GREEN-REJECTED` (r27 gate 4/4) |
| R-f | `census/round-38/records/c2-before.txt` (and `c2-after*.txt`, `c2-base-composition*.txt`, `a1-docstring-variants.txt`) | r38 freeze/landing commits | — | 21 | `SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6` — the **r38 write-envelope** fixture, a different instrument |
| R-g | `census/round-38/cells.tsv` | r38 freeze | — | 2, 11 | rows `R38-C1-1`/`R38-C1-10`: `escapes=9` vs `escapes=4` — `escapes=4` occurs **only** in the register's `stale` column, never in a receipt |

`escapes` semantics (grounded in `tests/fixtures/r37-drift-escapes.py:311-317`):
`escapes = sum(1 for v in base_escaped.values() if v)` — it counts *base-tool* escapes, so the same
value appears on both arms by construction; the arm difference is in `pass`/`fail`/`base_fail`.

---

## 3. What each line should have carried, and who carries it

### 3.1 `LOG.md:1855` — item `R39-C1-11`

| fragment as written | value it should carry | carrier |
|---|---|---|
| base arm `cases=9` | `cases=12` | R-a |
| base arm `pass=3` | `pass=3` — **already correct** | R-a |
| base arm `fail=6` | `fail=9` | R-a |
| base arm `base_fail=6` | `base_fail=9` | R-a |
| "reproduces six escapes" | nine escapes, `escapes=9` | R-a (and the criterion's own `>=3` is met by 9) |
| landing arm `cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0 | **exact match, no correction needed** | R-b |
| "drift 12/12, report gate 21/21, r27 gate 4/4" | **exact match** | R-e |

No r37 or r38 receipt **SUMMARY** carries `cases=9` or `fail=6` for this fixture. Nuance the correction
must respect: `census/round-37/records/c1-before.txt:13` *does* carry the string `cases=9` — as a
register expectation, `MISMATCH C1-11 EXPECTED-MISSING SKILL.md expected='cases=9'` — and
`census/round-37/citation-cells.tsv:3,10-12` carry it in expected/stale cells. `base_fail=6` is carried
by the r38 write-envelope receipts (R-f); citing it for the escape fixture would be a misbind.

Verdict §3.1: the line is **stale on three integers** (`cases=9`, `fail=6`, `base_fail=6`) plus the
count word "six"; `pass=3` and the whole landing arm are correct.

### 3.2 `LOG.md:1862` — item `R39-C1-12`

| fragment as written | status | carrier |
|---|---|---|
| `cells=9` in "the original letters still read `cells=9`" | **faithful quotation** of the frozen r37 target, not a stale measurement: `census/round-37/preregistration.txt:18` @ `02b4339` — `Target (frozen): SUMMARY cells=9 mismatches=0` (also `:27`, `:71`) | r37 prereg |
| `cases=6 base_fail>=3` | **faithful quotation** of the frozen r37 C2 target: `census/round-37/preregistration.txt:39` @ `02b4339` — `Target (frozen): SUMMARY cases=6 pass=6 fail=0 base_fail>=3` (also `:51`, `:73`) | r37 prereg |
| `cells=11` (claimed receipt reading) | correct | R-c |
| `cases=9 base_fail=6` (claimed receipt reading) | **wrong**; should be `cases=12` … `base_fail=9` | R-b (landing) / R-a (base arm) |
| `0be9bd0bf0c8143483bc4da609a6225b2c47ab64` | resolves (`git cat-file -t` = commit; r37 prereg `:149` @ `02b4339`: "Measured at 0be9bd0bf0c8143483bc4da609a6225b2c47ab64; receipts c1-after.txt and c2-after.txt.") | — |

Hero check: `git grep -F 'cases=9 base_fail=6' ed30b7f -- .` returns **exactly one line — `LOG.md:1862`
itself**. No receipt anywhere carries that pair. `cases=9` is carried as `cells=9` (not `cases=9`) by
R-d lines 21 and 32, which are control readings of the *citation* counter, a different instrument.

Verdict §3.2: the line's two quotations are faithful; its "against receipts at …" clause is **stale on
`cases=9 base_fail=6`** (should be `cases=12 … base_fail=9`), and the `cells=9` half of that clause is a
quotation, not a claim.

### 3.3 `corpus/QUALITY.md:209` — item `R39-C1-13`

| fragment as written | value it should carry | carrier |
|---|---|---|
| `census/round-37/records/c2-before.txt` **(4 escapes)** | `escapes=9` | R-a |
| `c2-after.txt` **(0)** | the `0` is the **`fail`** field; the escape field is `escapes=9` | R-b |
| check column "base must reproduce >=3 escapes and the candidate must show none" | satisfied by 9 / by `fail=0`; no numeric correction needed | R-a, R-b |

**No receipt carries `escapes=4` — at any revision.** `git grep -F 'escapes=4'` at base and at HEAD
returns only `census/round-38/cells.tsv:2` and `:11`, i.e. the register's own `stale` column; the
pickaxe `-S'escapes=4'` over all history returns only the three refs of the r38 freeze commit that adds
that register. Consequence: `corpus/QUALITY.md:214` (R38-C1-10) says the "(4 escapes)" reading
"belongs to the six-case draft" — **that attribution has no committed carrier**: no committed r37 draft
receipt, and no committed r37 report, ever contained `escapes=4`. The correction block must not restate
the draft claim as fact.

Second point, why the literal survived: `QUALITY.md:209` carries **none of the four sweep tokens**
(`cases=9`, `pass=3`, `fail=6`, `escapes=9`) — it says "4 escapes" and "0" in prose. A token grep cannot
find it; only an anchor like `QUALITY-line-209` or a search for the word `escapes` can.

Verdict §3.3: the evidence cell is **stale on both quoted values** (`4` → `9`; `0` → `9` with the note
that 0 is the fail count), and the one receipt the cell names does not contain the number it quotes.

---

## 4. Token sweep at base

Command: `git -C <lane> grep -n -F -e 'cases=9' -e 'pass=3' -e 'fail=6' -e 'escapes=9' ed30b7f -- .`
(538 distinct `(path,line)` carriers; no deletions were needed to explain any of them.)

### 4.1 Totals and the tokenizer caveat

| token | line hits | whole-token occurrences | lines with 0 whole-token hits | lines with >1 |
|---|---:|---:|---:|---:|
| `cases=9` | 207 | 220 | 8 | 21 |
| `pass=3` | 268 | 199 | 79 | 8 |
| `fail=6` | 53 | 57 | 0 | 4 |
| `escapes=9` | 24 | 25 | 0 | 1 |

Tokenizer used = the one the frozen counter uses (`census/round-39/c1-counter.py:86-95`,
`not before.isalnum() and not after.isalnum()`). Two consequences that matter for the correction block:

- `pass=32`, `pass=30`, `pass=35` do **not** satisfy `pass=3` (79 of the 268 grep hits are such
  substring-only lines; a plain `grep -F pass=3` overstates the carrier set by 79 lines, 29 %).
- `_` is not alphanumeric, so **`base_fail=6` DOES satisfy the token `fail=6`**. That is why 53 lines
  carry `fail=6`: most are r38 write-envelope `base_fail=6` SUMMARYs.

### 4.2 Policy surfaces — every line (root documents + `corpus/`)

`LOG.md`
| line | tokens | what the numbers are |
|---|---|---|
| 1667 | cases=9 | r24 coverage-agreement fixture (9/9) quoted in r26 history |
| 1800 | pass=3 | r31 landing-gate base-tool arm `cases=10 pass=3` |
| 1825 | pass=3 | r33 C2 counter `SUMMARY legs=11 pass=3 fail=2 harm=0` |
| 1855 | cases=9, pass=3, fail=6, escapes=9 | **target line** (§3.1) |
| 1862 | cases=9, fail=6 | **target line** (§3.2) |
| 1867 | escapes=9 | r38 corrected row: c2-after @02b4339 carries `escapes=9` — correct |
| 1875 | cases=9, pass=3, fail=6, escapes=9 | **landed r39 correction** for 1855 (§4.5) |
| 1877 | cases=9, fail=6 | **landed r39 correction** for 1862 (§4.5) |

`SCORECARD.md`
| line | tokens | instrument |
|---|---|---|
| 68 | cases=9 | r24 fixture 9/9 |
| 335 | cases=9 | r30 correction run `observed=cases=9 pass=9` |
| 374 | pass=3 | L08 `total=32\tpass=32` (substring `pass=3` inside `pass=32`) |
| 400 | cases=9 | L35 r24 fixture 9/9 |
| 406 | pass=3 | L41 r30 `cases=7 pass=3` |
| 413 | pass=3 | r31 base tool `cases=10 pass=3` |
| 423 | pass=3 | r31 base tool `cases=10 pass=3` |
| 466 | pass=3 | N38 withdrawn row (`pass=3`) |
| 506 | cases=9 | K18 r24 fixture 9/9 |
| 513 | pass=3 | r33 C2 `legs=11 pass=3 fail=2` |
| 564 | cases=9 | r36 C3 `cases=9 pass=9 fail=0` |
| 597 | cases=9 | r36→r37 C3 before/after 9/9 → 12/12 |
| 616 | cases=9 | R37-C1-10 (`cases=9 pass=9`, r36 c2-after @1e771ed) |
| 617 | cases=9 | R37-C1-11 (same value) |
| 629 | pass=3, escapes=9 | **r37 C2 row: `cases=12 pass=3 fail=9 base_fail=9 escapes=9`, rc 1** — this is the in-lane precedent for the corrected letters |
| 655 | escapes=9 | R38-C1-1 text: c2-after @02b4339 carries `escapes=9` |
| 667 | fail=6 | R38 C2 row, `base_fail=6` of the write-envelope fixture |
| 674 | escapes=9 | r38 C2 receipt summary `base_fail=9 escapes=9` |
| 681 | fail=6 | write-envelope gate row `base_cases=12 base_fail=6` |
| 700, 710, 722, 732 | fail=6 | write-envelope receipts `c2-after4..7.txt` `base_fail=6 behavioral_fail=3` |

`SKILL.md`
| line | tokens | instrument |
|---|---|---|
| 247 | cases=9 | r36 report-contract selftest 9/9 |
| 252 | escapes=9 | r37-drift-escapes gate row (`escapes=9 control=ESCAPE-REPRODUCED`) — correct |
| 259 | pass=3 | r30 base gate `cases=7 pass=3` |
| 262 | pass=3 | r31 base tool `cases=10 pass=3` |
| 268 | fail=6 | r32 C3 junk control `legs=14 fail=6` |
| 271 | pass=3 | r34 junk fixture `cases=3 pass=3` |
| 279 | fail=6 | **r38 write-envelope gate row** — it is `base_fail=6` (substring satisfies the token), and the value is correct for that fixture |

`corpus/QUALITY.md`
| line | tokens | instrument |
|---|---|---|
| 135 | cases=9 | Q56 evidence, r24 fixture 9/9 |
| 159 | pass=3 | Q64 evidence, r30 base gate `pass=3` |
| 168 | pass=3 | Q68 evidence, r31 `cases=10 pass=3` |
| 209 | *(none)* | **target line — carries no sweep token** (§3.3) |
| 214 | escapes=9 | R38-C1-10 correction (quotes 861c2ba → `escapes=9`) |
| 216 | fail=6 | Q86 evidence, `base_fail=6 behavioral_fail=3` (r38 write envelope) |
| 222 | escapes=9 | **landed r39 correction** for 209 (§4.5) |

`corpus/lessons/*`
| line | tokens | instrument |
|---|---|---|
| round-24.md:19, :81, :261 | cases=9 | r24 coverage-agreement 9/9 (three separate statements) |
| round-30-verifier-spotcheck.md:67 | pass=3 | r30 redarm base `pass=3` |
| round-31-verifier-spotcheck.md:53 | pass=3 | `total=32\tpass=32` (substring) |
| round-32.md:80 | fail=6 | r32 C3 sourceless-entry control `fail=6` |
| round-33-verifier-spotcheck.md:74, :108 | pass=3 | r33 C2 `legs=11 pass=3 fail=2` |
| round-33-verifier-spotcheck.md:120 | cases=9 | K18 r24 fixture 9/9 |
| round-33.md:12 | pass=3 | r33 C2 landing `pass=3` |
| round-36-verifier-spotcheck.md:36, :60 | cases=9 | r36 report-contract selftest 9/9 and the superseded-letter list |
| round-37-verifier-spotcheck.md:55, :67, :105 | cases=9, escapes=9 | r36 selftest 9/9; c2-after `escapes=9`; "C2 evidence-verified 12/12 base_fail=9 escapes=9" |
| round-37-verifier-spotcheck.md:152, :153 | escapes=9, cases=9, pass=3, fail=6 | spot-check finding **quoting the defect** (`LOG.md` C2: "six escapes … `cases=9 pass=3 fail=6 base_fail=6`") — a quotation of the stale line, not a fresh claim |
| round-37.md:29 | escapes=9 | r37 C2 landing arm `SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0 |
| round-37.md:32 | pass=3, escapes=9 | r37 C2 base arm `cases=12 pass=3 fail=9 base_fail=9 escapes=9`, rc 1 — the same letters R-a carries |
| round-38-verifier-spotcheck.md:63 | fail=6 | r38 base arm `base_fail=6` (write envelope) |
| round-38-verifier-spotcheck.md:198, :199, :202 | cases=9, pass=3, fail=6, escapes=9 | **R13 finding itself** — quotes `cases=9 pass=3 fail=6` and `escapes=9` |
| round-38.md:33 | fail=6 | r38 C2 `base_fail=6 behavioral_fail=3` |
| round-38.md:194 | escapes=9 | r38 C1-1..6 re-cite `escapes=9` |
| round-38.md:289 | escapes=9 | **landed r39 correction** R39-C1-14 (vacuity needs every `escapes=9` row) |

### 4.3 `census/round-37`, `-38`, `-39` — every line

| line | tokens | content |
|---|---|---|
| `census/round-37/citation-cells.tsv:3` | cases=9 | C1-2 row: expected `cases=12 pass=12`, stale `cases=9 pass=9` |
| `…:10` | cases=9 | C1-9 row: stale `cases=9` |
| `…:11` | cases=9 | C1-10 row: expected `cases=9 pass=9`, stale `cases=8 pass=8` |
| `…:12` | cases=9 | C1-11 row: expected `cases=9 pass=9`, stale `cases=8` |
| `census/round-37/preregistration.txt:11` | cases=9 | "quote cases=11/cases=9 against" (the pre-amendment letters) |
| `…:101` | cases=9 | `'cases=9 pass=9' to '9/9'` |
| `census/round-37/records/c1-before.txt:13` | cases=9 | `MISMATCH C1-11 EXPECTED-MISSING SKILL.md expected='cases=9'` (register expectation, **not** a measurement; the control SUMMARYs at :21 and :32 read `cells=9`, a different token) |
| `census/round-37/records/c2-before.txt:14` | **pass=3, escapes=9** | **R-a: the base-arm SUMMARY** — `cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` |
| `census/round-37/records/c2-after.txt:15` | escapes=9 | **R-b: the landing SUMMARY** |
| `census/round-38/cells.tsv:2` | escapes=9 | R38-C1-1: expected `escapes=9`, stale `escapes=4` |
| `…:3` | fail=6* | R38-C1-2: `base_fail=9` vs stale `base_fail=6` |
| `…:8` | escapes=9 | R38-C1-7: expected `escapes=9`, stale `escapes=6` |
| `…:9` | fail=6* | R38-C1-8 |
| `…:10` | fail=6* | R38-C1-9: `fail=0` vs stale `fail=6` |
| `…:11` | escapes=9 | R38-C1-10: expected `escapes=9`, stale `escapes=4` |
| `census/round-38/preregistration.txt:144, :177` | fail=6* | `base_fail=6 behavioral_fail=3` (write envelope) |
| `census/round-38/records/a1-docstring-variants.txt:17` | fail=6* | write-envelope SUMMARY |
| `census/round-38/records/c2-after.txt:21`, `c2-after2.txt:21`, `c2-after3..7.txt:4/3`, `c2-base-composition.txt:22`, `c2-base-composition2.txt:10`, `c2-before.txt:21` | fail=6* | ten write-envelope SUMMARYs `SUMMARY cases=12 pass=12 fail=0 base_cases=12 base_fail=6[ behavioral_fail=3]` |
| `census/round-38/records/consumers-after2..6.txt:15` | escapes=9 | five consumer receipts `base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` |
| `census/round-39/c1-items.tsv:17` | cases=9, fail=6 | frozen item `R39-C1-11 LOG-line-1855,cases=9,fail=6` |
| `census/round-39/c1-items.tsv:19` | escapes=9 | frozen item `R39-C1-13 QUALITY-line-209,escapes=9` |

`fail=6*` = the hit is inside `base_fail=6`; it satisfies the counter's token rule (`_` is not
alphanumeric) but is a different field.

At the **base** revision `census/round-39/` is absent (`git ls-tree ed30b7f:census/round-39` → absent);
the two item rows above enter at the freeze commit `b769bfb`.

### 4.4 Everything else (frozen history, 49 files / 80 lines)

`census/round-10` 2 (`seat-01.json`), `round-20` 10 (transcripts), `round-21` 6, `round-24` 2,
`round-30` 6, `round-31` 7, `round-32` 10, `round-33` 7, `round-34` 4, `round-35` 5, `round-36` 3,
`round-4` 1; `tests/` 5 (`results/*.json` 3, `fixtures/r37-citation-reconcile.py:108,186` — the
`cases=99`/`cases=9` synthetic expectations); `tools/` 3 (`souji-capability-cells.py:31,41` prose,
`souji-citation-reconcile.py:6` docstring listing `cases=9` as an example receipt reading).
Wave artifacts: `.ufo/waves/**` 80 lines, `census/round-N/waves/**` (captured waves) 284 lines —
frozen seat reports and dispatch JSON, never edited by a correction block.

### 4.5 What the landed correction block adds (base → HEAD delta)

`git grep` at `HEAD` yields 546 carriers vs 538 at base; **no line disappeared** (0 deletions, so no
in-place rewrite of LOG.md/QUALITY.md — confirmed by the `sha256sum` pairs and the pure-addition diff):

| new line | tokens | value check |
|---|---|---|
| `LOG.md:1875` (R39-C1-11, commit `c0b007b`) | cases=9, pass=3, fail=6, escapes=9 | quotes R-a **character-exact**, including `control=ESCAPE-REPRODUCED`; quotes R-b as a prefix `cases=12 pass=12 fail=0 base_fail=9 escapes=9` — the receipt's line continues ` control=ESCAPE-REPRODUCED`, so the quotation is an unmarked truncation (defect D2 below) |
| `LOG.md:1877` (R39-C1-12, `c0b007b`) | cases=9, fail=6 | `cells=11` = R-c ✓; `cases=12 ... base_fail=9` = R-b ✓ with an explicit ellipsis ✓ |
| `SKILL.md:279` | fail=6 | `base_fail=6` of the r38 write-envelope gate row — correct for its own fixture |
| `corpus/QUALITY.md:222` (R39-C1-13, `c0b007b`) | escapes=9 | "the escape count is `escapes=9` on both arms (…c2-before.txt and c2-after.txt)" ✓ (R-a, R-b); "the 0 … is the post-repair failure count" ✓ (R-b `fail=0`) |
| `corpus/lessons/round-38.md:289` (R39-C1-14) | escapes=9 | "`mismatches=9` needs every `escapes=9` row (three-rows: R38-C1-1, R38-C1-7 and R38-C1-10)" ✓ matches `census/round-38/cells.tsv:2,8,11` |

Therefore the correction block creates **no new numeric stale literal**: every integer it prints either
matches a receipt blob at the named revision or is a quoted stale token.

---

## 5. Verdicts

| check | verdict | evidence |
|---|---|---|
| Target lines exist at the frozen numbers in base and HEAD | **PASS** | §1; sha256 pairs identical, diff pure additions |
| `LOG.md:1855` base arm: which receipt carries the right value | **PASS (mapped)** — R-a `c2-before.txt` @ `861c2ba268883d271d0b5d0e4884a0948a9c354c`, `SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc=1 | §3.1 |
| `LOG.md:1855` landing arm and consumer counts | **PASS** — R-b @ `02b43398…`; R-e @ `bbefcee6…` (12/12, 21/21, 4/4) | §3.1 |
| `LOG.md:1855` no-carrier claim | **PASS for measurement SUMMARYs, over-broad as prose** — no r37/r38 SUMMARY carries `cases=9`/`fail=6` for the escape fixture, but `c1-before.txt:13` carries the string `cases=9` as a register expectation and `pass=3` *is* carried by R-a (defect D1) | §3.1 |
| `LOG.md:1862` first half | **PASS** — `cells=9` and `cases=6 base_fail>=3` are faithful quotations of the frozen r37 target at `census/round-37/preregistration.txt:18,39` @ `02b4339` | §3.2 |
| `LOG.md:1862` second half | **PASS (mapped)** — `cases=9 base_fail=6` has **no receipt carrier anywhere**; correct pair is `cells=11` (R-c) / `cases=12 … base_fail=9` (R-b) | §3.2 |
| `QUALITY.md:209` "(0)" | **PASS (mapped)** — `0` is `fail=0` of R-b; escapes are 9 on both arms | §3.3 |
| `QUALITY.md:209` "(4 escapes)" | **FAIL — no receipt carries `escapes=4`** at any revision; only the `stale` column of `census/round-38/cells.tsv:2,11`. R38-C1-10's "belongs to the six-case draft" is ungrounded in committed bytes (defect D3) | §3.3 |
| Sweep completeness at base | **PASS** — 538 carriers enumerated; four token totals and the zero-whole-token lines are stated; policy-surface and round-37..39 carriers are listed line by line | §4 |

---

## 6. Residual defects the integrator should weigh

- **D1 — `LOG.md:1875` "no r37 receipt carries those integers" is falsifiable as written.**
  `census/round-37/records/c1-before.txt:13` is an r37 receipt and carries `expected='cases=9'`;
  `census/round-37/citation-cells.tsv:3,10-12` carry it as expected/stale cells. Also `pass=3` — one
  of the three integers in `cases=9 pass=3 fail=6` — *is* carried by R-a. Tighter wording: "no r37/r38
  receipt **SUMMARY** carries `cases=9` or `fail=6` for the escape fixture; `pass=3` is correct."
  (The item's `must` tokens still close on this line, so this is prose accuracy, not counter risk.)
- **D2 — `LOG.md:1875` truncates R-b without an ellipsis.** It prints
  `cases=12 pass=12 fail=0 base_fail=9 escapes=9`; the receipt line ends
  `… escapes=9 control=ESCAPE-REPRODUCED`. The base-arm quotation on the same line *does* include
  `control=`, so the line is internally inconsistent. Add the trailing field or an ellipsis (the
  `0be9bd0` style already used on line 1862/1877).
- **D3 — `QUALITY.md:209` "(4 escapes)" is still uncorrected and by construction invisible to a token
  grep.** R39-C1-13 only addresses the "(0)" half; R38-C1-10 (line 214) explains the 4 as a six-case
  draft, but no committed receipt or report ever contained `escapes=4` (pickaxe over all history
  returns only the r38 register commit). The correction must either name a real carrier or say the
  value has none.
- **D4 — `LOG.md:1877` calls `cells=9` a "superseded letter".** In line 1862 that token is a *quotation*
  of the frozen target (`preregistration.txt:18` @ `02b4339`), not a claimed measurement; only the
  "against receipts at …" clause is stale. Not fatal (`R39-C1-12` requires only its anchor), but a
  reader can take it as a second stale reading.
- **D5 — semantics of the `escapes` field.** Both arms report `escapes=9` (`r37-drift-escapes.py:311`
  counts *base*-tool escapes), so any future sentence of the form "the after arm shows no escapes"
  would be false. The truthful discriminator is `pass 3→12` / `fail 9→0`.
- **D6 — token rule to reuse.** Any new check over these values must use the counter's alnum-boundary
  tokenizer, not `grep -F`: `grep -F pass=3` overstates carriers by 79 lines (all `pass=32/30/35`),
  while `base_fail=6` legitimately satisfies `fail=6`.

No harness, counter or fixture was run by this seat; the counter verdicts for C1 remain the L1's
measurement. Scratch: none created (nothing on disk to reclaim).
