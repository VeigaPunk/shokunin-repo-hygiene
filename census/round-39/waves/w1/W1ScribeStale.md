# W1ScribeStale — R39-C1-11 / -12 / -13: the three appended correction lines, receipt-verified

Seat: scribe (leaf, advisory). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Contract read first: `census/round-39/preregistration.txt` (freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`,
lane base `ed30b7f5b77939c9073348d810730bc4f355708d`). Items read: `census/round-39/c1-items.tsv` rows
`R39-C1-11` (`LOG.md`, must `LOG-line-1855,cases=9,fail=6`), `R39-C1-12` (`LOG.md`, must `LOG-line-1862`),
`R39-C1-13` (`corpus/QUALITY.md`, must `QUALITY-line-209,escapes=9`).

Task: draft the three appended correction lines; each must state the value the line should have carried,
the receipt that carries it (path + revision + its SUMMARY line), and why the original value was wrong.
Every receipt quoted below was read from committed bytes with `git show <rev>:<path>` in this seat.

No tool was installed or upgraded; pacman untouched. No mutating git/jj command was run.

---

## 0. Commands and their output

### 0.1 Lane state

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -3 && git rev-parse HEAD && ls census/round-39/
2201778 round-39: PROVINCE boundary note — two tool contracts repaired, no receipt class, certification OFF
790d16b round-39: C2 — drop unreachable EISDIR from the RECORD-MISSING line (wave-1 W1ExecC2Docstring)
094e531 round-39: C1 — R7 line names the reaped path as $HYAKU_SCRATCH, not a literal scratch root
2201778e7736af82e7d8a42dec2494f115bf3923
__pycache__
c1-counter.py
c1-items.tsv
c2-counter.py
c3-counter.py
make-cells.py
preregistration.txt
records
```

`census/round-39/cells.tsv` is absent at the start of this seat and still absent at every tip observed
during it (`d4c1755`, `f8ba3f3`, `e9958ee`), so the counter's register leg reads `cells=0`; that is the
L1's remaining work, not this item's.

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain && git show HEAD:LOG.md | grep -n "R39-C1-1[123]" ; git show HEAD:corpus/QUALITY.md | grep -n "R39-C1-13"
?? census/round-39/make-cells.py
?? census/round-39/records/c2-after.txt
?? census/round-39/records/c3-after.txt
?? census/round-39/records/census-after.txt
?? census/round-39/records/census-before.txt
1875:R39-C1-11 — LOG-line-1855 (the r37 C2 bullet) states `cases=9` and `fail=6`; no r37 receipt carries those integers — …
1877:R39-C1-12 — LOG-line-1862 states the superseded letters `cells=9` and `cases=9 base_fail=6`; …
222:R39-C1-13 — QUALITY-line-209's "(0)" reads the drift-escape fixture's *fail* field as its escape count; …
```

The three lines already existed at HEAD (committed at `c0b007b42af9a03d7edc32533bcac27484223997`,
`git log -S'R39-C1-11' -- LOG.md` and `-S'R39-C1-13' -- corpus/QUALITY.md` both return only that commit).
This seat therefore verified them against the receipts, found one falsifiable claim and three missing
revisions, and replaced the three lines in place (uncommitted; see §5).

### 0.2 The three anchored lines as they stand (byte-identical at base `ed30b7f` and at the tip)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR==1855' LOG.md; awk 'NR==1862' LOG.md; awk 'NR==209' corpus/QUALITY.md
```

`LOG.md:1855` (excerpt, the numbers this item corrects):
> New fixture `tests/fixtures/r37-drift-escapes.py` reproduces six escapes on the r36 blob
> (`cases=9 pass=3 fail=6 base_fail=6`, rc 1) and none on the landing
> (`cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0)

`LOG.md:1862` (excerpt):
> … after wave-1 connector seat W1ConnOverlap showed the original letters still read `cells=9` /
> `cases=6 base_fail>=3` against receipts at `cells=11` / `cases=9 base_fail=6`; the target strings
> that bind are the amended ones in A1.3/A2.3/A2.4 …

`corpus/QUALITY.md:209` (Q84 evidence cell, excerpt):
> `corpus/lessons/round-37.md` `## Claims` C2; `census/round-37/records/c2-before.txt` (4 escapes) vs
> `c2-after.txt` (0)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && base=$(git show ed30b7f:corpus/QUALITY.md | sed -n '209p' | sha256sum | cut -d' ' -f1); head=$(sed -n '209p' corpus/QUALITY.md | sha256sum | cut -d' ' -f1); echo "base209=$base"; echo "head209=$head"
base209=12ede8ea1a654bc77bd7db545db2d760cb9a7cf7e6361672b23b368d5bb31b50
head209=12ede8ea1a654bc77bd7db545db2d760cb9a7cf7e6361672b23b368d5bb31b50
```

### 0.3 Receipts, read from committed bytes

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for spec in "861c2ba268883d271d0b5d0e4884a0948a9c354c:census/round-37/records/c2-before.txt" "02b43398ffd295a399c7097ab0d8b2eb70fb490a:census/round-37/records/c2-after.txt" "02b43398ffd295a399c7097ab0d8b2eb70fb490a:census/round-37/records/c1-after.txt"; do rev=${spec%%:*}; f=${spec#*:}; echo "=== $rev $f ==="; git show "$rev:$f" | grep -n -E 'SUMMARY|escap|fail'; echo; done
=== 861c2ba268883d271d0b5d0e4884a0948a9c354c census/round-37/records/c2-before.txt ===
2:case-record-escape=FAIL
3:case-json-write-escape=FAIL
14:SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED

=== 02b43398ffd295a399c7097ab0d8b2eb70fb490a census/round-37/records/c2-after.txt ===
2:# command: python3 -B tests/fixtures/r37-drift-escapes.py --base-tool <r36 blob> --work $TMPDIR
3:case-record-escape=PASS
4:case-json-write-escape=PASS
15:SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED

=== 02b43398ffd295a399c7097ab0d8b2eb70fb490a census/round-37/records/c1-after.txt ===
3:SUMMARY cells=11 mismatches=0
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 8edcb04212b641203862921297655a1d329808e4:census/round-37/records/c2-before.txt
# C2 before — final 9-case fixture, candidate = base = the r36 tool blob 1e771ed
# command: python3 -B tests/fixtures/r37-drift-escapes.py --tool <r36 blob> --base-tool <r36 blob>
case-record-escape=FAIL
case-json-write-escape=FAIL
case-trace-refs=FAIL
case-env-witness=FAIL
case-json-inside=PASS
case-trace2-event=PASS
case-json-hardlink=FAIL
case-record-fifo=FAIL
case-measured=PASS
SUMMARY cases=9 pass=3 fail=6 base_fail=6 control=ESCAPE-REPRODUCED
rc=1
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git merge-base --is-ancestor 8edcb04212b641203862921297655a1d329808e4 HEAD && echo ANCESTOR; git log -1 --format='%H %ad %s' --date=short 8edcb04212b641203862921297655a1d329808e4
ANCESTOR
8edcb04212b641203862921297655a1d329808e4 2026-10-28 round-37: regenerate before receipts with final instruments; S236 line/scope correction; honest live-run label; new named limits
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for rev in $(git log --format=%H -- census/round-37/records/c2-before.txt); do printf "%s: " "$rev"; git show "$rev:census/round-37/records/c2-before.txt" 2>/dev/null | grep -o 'SUMMARY.*' | head -1; done
861c2ba268883d271d0b5d0e4884a0948a9c354c: SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED
8edcb04212b641203862921297655a1d329808e4: SUMMARY cases=9 pass=3 fail=6 base_fail=6 control=ESCAPE-REPRODUCED
d30476d25e999d0db93ec2619b44ea7dc221a653: SUMMARY cases=8 pass=3 fail=5 base_fail=5 control=ESCAPE-REPRODUCED
d5c6498c5f72a63c9df32b26ee143e8d775eebbd: SUMMARY cases=6 pass=2 fail=4 base_fail=4 control=ESCAPE-REPRODUCED
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD:census/round-37/records/c2-before.txt; git rev-parse 861c2ba:census/round-37/records/c2-before.txt
ac576bdf07e54bcc385d2ddc187d5e62092c9386
ac576bdf07e54bcc385d2ddc187d5e62092c9386
```

`census/round-37/records/c2-before.txt` was rewritten three times inside r37 (`d5c6498` 6 cases,
`d30476d` 8, `8edcb04` 9, `861c2ba` 12). The blob the lane carries today — and at HEAD — is the
12-case one, `ac576bdf…`, first committed at `861c2ba268883d271d0b5d0e4884a0948a9c354c`.

### 0.4 The r37 frozen and amended targets (`LOG.md:1862` quotes them)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 02b4339:census/round-37/preregistration.txt | sed -n '16,20p;37,41p;69,75p'
  Target (frozen): `SUMMARY cells=9 mismatches=0`, rc 0, where each register row's
           receipt blob at receipt_rev 1e771ed59301ed10f68e22d4edf35d5218bacf1a
           contains its expected token and the corrected line carries that token
  Target (frozen): `SUMMARY cases=6 pass=6 fail=0 base_fail>=3
           control=ESCAPE-REPRODUCED`, rc 0; and the r36 regression fixture
  C1 = "souji-citation-reconcile prints cells=9 mismatches=0 at the landing
        revision, and every register receipt carries its expected token";
  C2 = "the r37 escape fixture prints cases=6 pass=6 fail=0 base_fail>=3
        control=ESCAPE-REPRODUCED and the r36 drift fixture stays 12/12";
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show 02b4339:census/round-37/preregistration.txt | sed -n '99,116p;137,150p'
  A1.3 Two cells of the same routed defect are added for the 'cases=8' selftest arm … Target becomes `cells=11 mismatches=0`.
  A2.3 New case measured requires the summary to reflect a measured REGS-CHANGED … Target becomes
       `cases=8 pass=8 fail=0 base_fail>=4 control=ESCAPE-REPRODUCED`.
  A2.4 (wave seat W1SentinelEnv S1) a FIFO record is refused (RECORD-MALFORMED,
       rc 2) instead of blocking forever in open().read(); case record-fifo added. Target
       becomes `cases=12 pass=12 fail=0 base_fail>=8 escapes>=6 control=ESCAPE-REPRODUCED`.
  C1 = "souji-citation-reconcile prints cells=11 mismatches=0 at the landing revision
        (register pinned with --register-rev), and every register receipt carries its
        expected token" — amended by A1.1 and A1.3;
  C2 = "the r37 escape fixture prints cases=12 pass=12 fail=0 base_fail>=8 escapes>=6
        control=ESCAPE-REPRODUCED with --base-tool (a control-free run exits 1), and the
        r36 drift fixture stays 12/12" — amended by A2.3, A2.4, A2.5 and A2.7.
```

`A2.5` and `A2.7` both exist at that revision (`grep -n "A2\.5\|A2\.7"` → lines 117, 126, 148).

### 0.5 The `escapes` field's carrier question

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --all --oneline -S'escapes=4' -- . | head; git grep -n -F 'escapes=4' HEAD -- .
4090ee5 round-38: freeze claims, commit-arm reconciler, drift write-envelope and record fixtures, do-nothing controls
0cd4ecd 
9dc6f9a 
HEAD:census/round-38/cells.tsv:2:R38-C1-1	SCORECARD.md	| R38-C1-1 |	escapes=9	escapes=4	census/round-37/records/c2-after…
HEAD:census/round-38/cells.tsv:11:R38-C1-10	corpus/QUALITY.md	R38-C1-10	escapes=9	escapes=4	census/round-37/records/c2-b…
```

No committed receipt contains `escapes=4`; the only occurrences are the `stale` column of the r38
register.

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "escapes" tests/fixtures/r37-drift-escapes.py | head -20; sed -n '300,325p' tests/fixtures/r37-drift-escapes.py
17:so the fixture proves it discriminates: `base_fail` must be >= 8 and `escapes` >= 6 and the
41:Exit: 0 candidate fail=0, base_fail >= 8 and escapes >= 6, 1 otherwise, 2 usage.
311:    escapes = sum(1 for v in base_escaped.values() if v)
314:    # the escapes themselves (>=4 of 6 artifacts), plus the case floor.
315:    control_ok = base_fail >= 8 and escapes >= 6
316:    print("SUMMARY cases=%d pass=%d fail=%d base_fail=%d escapes=%d control=%s" % (
```

`escapes` counts *base-tool* escapes, so the same value appears on both arms by construction; the
arm difference is in `pass`/`fail`. The fixture registers nine escape artifacts (`record`, `json-write`,
`trace-refs`, `env`, `hardlink`, `fifo`, `gitfile`, `symlink-child`, `row-symlink`), so `escapes=9`
means all nine were observed and the docstring's `escapes >= 6` is a floor.

Case sets of the two before-receipt drafts, compared:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && mkdir -p /fast/scratch/hyaku && git show 8edcb04:census/round-37/records/c2-before.txt | grep '^case-' | sed 's/=.*//' | LC_ALL=C sort > /fast/scratch/hyaku/c9.txt && git show 861c2ba:census/round-37/records/c2-before.txt | grep '^case-' | sed 's/=.*//' | LC_ALL=C sort > /fast/scratch/hyaku/c12.txt && echo "only-in-12:" && LC_ALL=C comm -13 /fast/scratch/hyaku/c9.txt /fast/scratch/hyaku/c12.txt && echo "only-in-9:" && LC_ALL=C comm -23 /fast/scratch/hyaku/c9.txt /fast/scratch/hyaku/c12.txt
only-in-12:
case-json-gitfile-write
case-json-symlink-child
case-record-symlink
only-in-9:
```

Three cases added, none removed (`wc -l` → 9 and 12).

---

## 1. Receipt table (verified this seat)

| ref | path | revision | blob | line | SUMMARY / observed |
|---|---|---|---|---|---|
| R-a | `census/round-37/records/c2-before.txt` | `861c2ba268883d271d0b5d0e4884a0948a9c354c` | `ac576bdf…` (== HEAD) | 14 | `SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, `rc=1` |
| R-b | `census/round-37/records/c2-after.txt` | `02b43398ffd295a399c7097ab0d8b2eb70fb490a` | `688da312…` (== HEAD) | 15 | `SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, `rc=0` |
| R-c | `census/round-37/records/c1-after.txt` | `02b43398ffd295a399c7097ab0d8b2eb70fb490a` | `ae17e610…` (== HEAD) | 3 | `SUMMARY cells=11 mismatches=0` |
| R-d | `census/round-37/records/c2-before.txt` | `8edcb04212b641203862921297655a1d329808e4` | superseded | 12 | `SUMMARY cases=9 pass=3 fail=6 base_fail=6 control=ESCAPE-REPRODUCED`, `rc=1` (header: "final 9-case fixture") |
| R-e | `census/round-37/preregistration.txt` | `02b43398ffd295a399c7097ab0d8b2eb70fb490a` | — | 18, 39, 99–150 | frozen targets `cells=9 mismatches=0` / `cases=6 pass=6 fail=0 base_fail>=3`; amended C1 `cells=11 mismatches=0`, C2 `cases=12 pass=12 fail=0 base_fail>=8 escapes>=6` |

## 2. What each line should have carried, and why the original was wrong

### 2.1 `LOG.md:1855` — item `R39-C1-11`

| fragment as written | should carry | carrier |
|---|---|---|
| `cases=9` (before arm) | `cases=12` | R-a |
| `pass=3` | `pass=3` — already correct | R-a |
| `fail=6` | `fail=9` | R-a |
| `base_fail=6` | `base_fail=9` | R-a |
| "reproduces six escapes" | `escapes=9` | R-a |
| landing arm `cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0 | exact, no correction | R-b |

Why wrong: the bullet's before-arm letters are the **superseded 9-case draft of the same receipt**,
which is still reachable as a blob at R-d. `census/round-37/records/c2-before.txt` was regenerated at
`861c2ba` with the final 12-case instrument: three further cases (`json-gitfile-write`,
`json-symlink-child`, `record-symlink`; none removed), `fail` 6→9, `base_fail` 6→9, and the new
`escapes` field at 9 (the fixture carries nine base-tool escape artifacts). The superseded
blob is not the file at HEAD (`ac576bdf…` at both `861c2ba` and HEAD), so a reader who checks the
receipt at HEAD sees different integers from the bullet.

The claim the previous draft of this line made — "no r37 receipt carries those integers" — is **false
as written**: R-d is an r37 receipt (ancestor of HEAD) whose SUMMARY carries exactly
`cases=9 pass=3 fail=6`. The corrected line therefore states the supersession rather than a
non-existence claim.

### 2.2 `LOG.md:1862` — item `R39-C1-12`

| fragment as written | status | carrier |
|---|---|---|
| "the original letters still read `cells=9` / `cases=6 base_fail>=3`" | **faithful quotation** of the frozen r37 targets, not a measurement | R-e lines 18, 39 |
| "against receipts at `cells=11`" | correct | R-c |
| "against receipts at `cases=9 base_fail=6`" | **stale**: the final receipts read `cases=12 … base_fail=9 escapes=9` | R-b (landing), R-a (base arm) |
| "amended ones in A1.3/A2.3/A2.4" | right family; the supersession block names A1.1/A1.3 and A2.3/A2.4/A2.5/A2.7 | R-e |

Why wrong: `cases=9 base_fail=6` is the pair carried by R-d, the superseded 9-case before receipt; the
final before receipt reads `cases=12 … base_fail=9` and the final after receipt reads
`cases=12 pass=12 fail=0 base_fail=9 escapes=9`. The clause presents a superseded reading as the
receipt reading that binds the amended target.

### 2.3 `corpus/QUALITY.md:209` — item `R39-C1-13`

| fragment as written | should carry | carrier |
|---|---|---|
| `census/round-37/records/c2-before.txt` **(4 escapes)** | `escapes=9` | R-a |
| `c2-after.txt` **(0)** | the `0` is the **`fail`** field; the escape field is `escapes=9` | R-b |

Why wrong: the evidence cell quotes the post-repair `fail=0` as if it were an escape count, while the
after receipt's `escapes=9` is the base-tool escape count that both arms share; and `4` has no carrier
in any committed receipt (only the r38 register's `stale` column). R38-C1-10 (`corpus/QUALITY.md:214`)
already moved the before half to `escapes=9` @ `861c2ba`; the corrected line names that predecessor
instead of restating the ungrounded "six-case draft" attribution.

## 3. The drafted lines (final bytes, now in the working tree)

`LOG.md:1875`

> R39-C1-11 — LOG-line-1855 (the r37 C2 bullet) carries the superseded before-arm letters `cases=9 pass=3 fail=6 base_fail=6` and the count word "six escapes"; the value it should have carried is `cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 1, printed by `census/round-37/records/c2-before.txt` @ `861c2ba268883d271d0b5d0e4884a0948a9c354c` (line 14; blob `ac576bdf07e54bcc385d2ddc187d5e62092c9386`, byte-identical at HEAD), while the bullet's landing arm `cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0, is exact in `c2-after.txt` @ `02b43398ffd295a399c7097ab0d8b2eb70fb490a` (line 15). The integers are wrong because they quote the superseded 9-case draft of the same receipt — `census/round-37/records/c2-before.txt` @ `8edcb04212b641203862921297655a1d329808e4` reads `SUMMARY cases=9 pass=3 fail=6 base_fail=6 control=ESCAPE-REPRODUCED`, rc 1, under the header "final 9-case fixture" — which the file no longer carries at HEAD because `861c2ba` regenerated it with the final 12-case instrument: three further cases (`json-gitfile-write`, `json-symlink-child`, `record-symlink`, none removed), `fail` 6→9, `base_fail` 6→9, and the new `escapes` field at 9 (nine base-tool escape artifacts). The bullet stays byte-verbatim; this line supersedes its before-arm letters only.

`LOG.md:1877`

> R39-C1-12 — LOG-line-1862 quotes the pre-amendment letters faithfully (`cells=9` and `cases=6 base_fail>=3` are the frozen r37 targets at `census/round-37/preregistration.txt` @ `02b43398ffd295a399c7097ab0d8b2eb70fb490a`, lines 18 and 39), but its "against receipts at" clause is stale: the receipts carry `SUMMARY cells=11 mismatches=0` (`census/round-37/records/c1-after.txt` @ `02b43398ffd295a399c7097ab0d8b2eb70fb490a`, line 3) and `SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED` (`c2-after.txt` @ the same revision, line 15), so the clause should have read `cells=11` / `cases=12 … base_fail=9 escapes=9`. The `cases=9 base_fail=6` pair is wrong because it belongs to the superseded 9-case before receipt (`census/round-37/records/c2-before.txt` @ `8edcb04212b641203862921297655a1d329808e4`, `SUMMARY cases=9 pass=3 fail=6 base_fail=6 control=ESCAPE-REPRODUCED`), not to any final receipt. The binding amended strings are C1 `cells=11 mismatches=0` (A1.1/A1.3) and C2 `cases=12 pass=12 fail=0 base_fail>=8 escapes>=6 control=ESCAPE-REPRODUCED` (A2.3/A2.4/A2.5/A2.7) in that same prereg file; line 1862 stays byte-verbatim.

`corpus/QUALITY.md:222`

> R39-C1-13 — QUALITY-line-209's evidence cell (`census/round-37/records/c2-before.txt` (4 escapes) vs `c2-after.txt` (0)) should have carried `escapes=9` on both arms: `census/round-37/records/c2-before.txt` @ `861c2ba268883d271d0b5d0e4884a0948a9c354c` prints `SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 1, and `c2-after.txt` @ `02b43398ffd295a399c7097ab0d8b2eb70fb490a` prints `SUMMARY cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0 — so the `0` the cell quotes is that receipt's `fail` field, not an escape count, and `4` has no carrier at all: no committed receipt anywhere contains `escapes=4` (the only occurrences are the stale column of `census/round-38/cells.tsv`), so R38-C1-10 above already moved the before half to `escapes=9` @ `861c2ba`. The fixture counts base-tool escapes (`tests/fixtures/r37-drift-escapes.py`: `escapes = sum(1 for v in base_escaped.values() if v)`), so 9 on both arms holds by construction and the discriminating fields are `pass` 3→12 and `fail` 9→0. The Q84 criterion text is unchanged; only its evidence pointer is corrected here (append-only, per CORPUS.md rule 2).

## 4. Checks run after the edit

### 4.1 Diff shape — three lines replaced, nothing else

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git diff --stat -- LOG.md corpus/QUALITY.md; git diff -U0 -- LOG.md corpus/QUALITY.md | grep -E '^@@'; git diff --numstat -- LOG.md corpus/QUALITY.md
 LOG.md            | 4 ++--
 corpus/QUALITY.md | 2 +-
 2 files changed, 3 insertions(+), 3 deletions(-)
@@ -1875 +1875 @@ Owned axis scores unchanged (calibration 7, coverage 8, operability 8). No tools
@@ -1877 +1877 @@ R39-C1-11 — LOG-line-1855 (the r37 C2 bullet) states `cases=9` and `fail=6`; n
@@ -222 +222 @@ R38-C1-10 the Q84 evidence cell's "`census/round-37/records/c2-before.txt` (4 es
2	2	LOG.md
1	1	corpus/QUALITY.md
```

(The `--stat` was also run unscoped once, while a sibling seat held `SKILL.md` modified: `LOG.md | 4 ++--`,
`SKILL.md | 16 ++++++++--------`, `corpus/QUALITY.md | 2 +-`. That `SKILL.md` delta is not this seat's;
the scoped `--numstat` above isolates the three replaced lines.)

`LOG.md:1855`, `LOG.md:1862` and `corpus/QUALITY.md:209` are untouched (`awk 'NR==1855'` still begins
`- C2 operability: …`; `git diff -U0` shows no hunk at 1855/1862/209).

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum LOG.md corpus/QUALITY.md      # before the edit
b17ad1284648b58b996aa39a665c6f8d1b4fe46e6c19b2626082640e1012a9e9  LOG.md
4403960bd67fb068ffa08caef93b69b972204929f665fd31dda8f4d77c9cdfd8  corpus/QUALITY.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum LOG.md corpus/QUALITY.md      # after the edit
e86b682c570c5ab4add6afe6aabb980b6ea25f023977c2bd51fd3efd57ddc034  LOG.md
9227a6a30126852aa17c72c3a9a7310cdfa0c47aa0285d36f4e81612ee1ffbcb  corpus/QUALITY.md
```

### 4.2 Item predicate against the edited bytes (the counter's own tokenizer)

The counter reads committed bytes via `git show`, so it cannot see an uncommitted edit; the three rows
were therefore re-scored against the working-tree bytes with the counter's own `has_token`:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location("c1", "census/round-39/c1-counter.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
items = m.parse_items(open("census/round-39/c1-items.tsv", encoding="utf-8").read(), "c1-items.tsv")
for row in items:
    if row["id"] not in ("R39-C1-11", "R39-C1-12", "R39-C1-13"): continue
    text = open(row["file"], encoding="utf-8").read()
    hits = [l for l in text.split("\n") if row["anchor"] in l]
    good = [l for l in hits if all(m.has_token(l, t) for t in row["must"]) and not any(m.has_token(l, t) for t in row["mustnot"])]
    print("%s hits=%d must=%s -> %s" % (row["id"], len(hits), row["must"], "CLOSED" if good else "OPEN"))
    for t in row["must"]:
        print("   token %-16s on-line=%s" % (t, any(m.has_token(l, t) for l in hits)))
PY
R39-C1-11 hits=1 must=['LOG-line-1855', 'cases=9', 'fail=6'] -> CLOSED
   token LOG-line-1855    on-line=True
   token cases=9          on-line=True
   token fail=6           on-line=True
R39-C1-12 hits=1 must=['LOG-line-1862'] -> CLOSED
   token LOG-line-1862    on-line=True
R39-C1-13 hits=1 must=['QUALITY-line-209', 'escapes=9'] -> CLOSED
   token QUALITY-line-209 on-line=True
   token escapes=9        on-line=True
```

### 4.3 The frozen counter at the committed tip and at the base control

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-39/c1-counter.py --root . --rev "$(git rev-parse HEAD)" --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r39/W1ScribeStale
ITEM R39-C1-11 CLOSED
ITEM R39-C1-12 CLOSED
ITEM R39-C1-13 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-39/c1-counter.py --root . --rev ed30b7f5b77939c9073348d810730bc4f355708d --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r39/W1ScribeStale
ITEM R39-C1-11 OPEN ANCHOR-ABSENT LOG.md anchor='R39-C1-11'
ITEM R39-C1-12 OPEN ANCHOR-ABSENT LOG.md anchor='R39-C1-12'
ITEM R39-C1-13 OPEN ANCHOR-ABSENT corpus/QUALITY.md anchor='R39-C1-13'
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=16 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```

The base arm reads `open=16`, matching the frozen control `census/round-39/records/c1-before.txt`
(`open=16`); the tip arm reads `open=2` for the two items this seat does not own. The register leg is
`cells=0` because `census/round-39/cells.tsv` is not committed yet — the predicate's
`register_cells>=6` arm is unreachable until the L1 lands the register.

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && S=$(mktemp -d /fast/scratch/hyaku/souji-r39/W1ScribeStale.XXXXXX) && python3 -B census/round-39/c1-counter.py --root . --rev "$(git rev-parse HEAD)" --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv --scratch "$S"
ITEM R39-C1-11 CLOSED
ITEM R39-C1-12 CLOSED
ITEM R39-C1-13 CLOSED
REGISTER cells=0 mismatches=0 commit_distinct=0
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
```

(re-run at the later tip `e9958ee517668fa8aa8a86a8b936b5b2ad56473e`; identical reading)

Note: HEAD moved three times while this seat ran — `2201778` → `d4c17557b92fd98044e4c8f0ddc79c6d75701b15`
(first counter run) → `f8ba3f3b4fdac9669182af1c2829d79c1658f314` (with a sibling seat's `SKILL.md` edit
in the tree) → `e9958ee517668fa8aa8a86a8b936b5b2ad56473e` (second counter run). The §4.1 scoped diff and
the §4.2 token check were re-run at `f8ba3f3`; at `e9958ee` the two edited lines are still the only
hunks in `LOG.md`/`corpus/QUALITY.md` (`git diff --numstat` → `2 2 LOG.md`, `1 1 corpus/QUALITY.md`).

## 5. Verdicts

| check | verdict | evidence |
|---|---|---|
| `LOG.md:1855` value verified against a receipt | **PASS** — R-a `c2-before.txt` @ `861c2ba…`, `SUMMARY cases=12 pass=3 fail=9 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 1, blob `ac576bdf…` == HEAD | §0.3, §1 |
| `LOG.md:1855` landing arm verified | **PASS** — R-b @ `02b4339…`, `cases=12 pass=12 fail=0 base_fail=9 escapes=9 control=ESCAPE-REPRODUCED`, rc 0 | §0.3 |
| why the original integers were wrong | **PASS** — they are R-d's (`8edcb04…`, `cases=9 pass=3 fail=6 base_fail=6`), a superseded blob the file no longer carries | §0.3, §2.1 |
| previous draft's "no r37 receipt carries those integers" | **FALSIFIED by this seat** — R-d is an r37 receipt (ancestor of HEAD) carrying exactly `cases=9 pass=3 fail=6`; the corrected line states supersession instead | §0.3, §2.1 |
| `LOG.md:1862` quotations verified | **PASS** — `cells=9` and `cases=6 base_fail>=3` are the frozen targets at `census/round-37/preregistration.txt` @ `02b4339…` lines 18 and 39 | §0.4 |
| `LOG.md:1862` "against receipts at" clause | **FAIL as written** — `cases=9 base_fail=6` belongs to R-d, not to the final receipts (`cells=11 mismatches=0` R-c; `cases=12 … base_fail=9 escapes=9` R-b); corrected line carries both with revisions | §0.3, §2.2 |
| `QUALITY.md:209` "(0)" | **FAIL as written** — `0` is R-b's `fail` field; `escapes=9` on both arms | §0.3, §2.3 |
| `QUALITY.md:209` "(4 escapes)" | **FAIL as written, no carrier** — `git grep -F 'escapes=4' HEAD` returns only `census/round-38/cells.tsv:2,11`; the corrected line names R38-C1-10 as the carrier of the before half | §0.5, §2.3 |
| the three lines exist at the frozen anchors in the edited bytes | **PASS** — one hit each, all `must` tokens present, `mustnot` empty | §4.2 |
| counter at the committed tip | **PASS for items 11–13** (`CLOSED`); overall predicate still `open=2`, `register_cells=0` — outside this seat | §4.3 |
| base control | **PASS** — `open=16`, matching `census/round-39/records/c1-before.txt` | §4.3 |

## 6. Limits and hand-off

- The three line replacements are **uncommitted** working-tree edits (`git status` → ` M LOG.md`,
  ` M corpus/QUALITY.md`); this seat does not commit. The L1 must land them through the lane helper,
  or re-apply the exact bytes in §3 if it lands from the report instead.
- `census/round-39/cells.tsv` is absent at `d4c1755`, `f8ba3f3` and `e9958ee` (the tip at report close),
  so the C1 predicate's register arm (`register_cells>=6`, `register_mismatches=0`,
  `commit_distinct>=2`) is unmeasured here; only the item arm was measured.
- Not claimed: that any other C1 item is closed (the tip reads `open=2` for items this seat does not
  own), that the register reconciles, or that C2/C3 hold. No receipt class, no deletion verdict, no
  certification.
- Out-of-scope observation for the integrator: `W1ExecStaleLiterals.md` §3.1/§5 asserts "no r37/r38
  receipt SUMMARY carries `cases=9` or `fail=6` for the escape fixture"; that holds only for the blobs
  reachable from `ed30b7f`, not for `census/round-37/records/c2-before.txt` @ `8edcb04…`, which carries
  both. Its defects D1–D4 are addressed by the drafted lines.
- Scratch: `/fast/scratch/hyaku/souji-r39/W1ScribeStale` was created for the counter's `--scratch`
  and removed (`rmdir`; `ls -d` → "No such file or directory"). Nothing left on disk.
- Tools: none installed or upgraded; pacman untouched.
