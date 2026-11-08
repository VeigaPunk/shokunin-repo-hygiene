# S87ExecC1 — C1 dual-arm independent re-derivation (souji round 87, w1)

Seat scope: re-derive **both C1 arms** on committed bytes, attribute the two new rows by hand, and enumerate the
instrument delta. Lane `souji-shokunin`, base `5e288bb3`, instruments `P=77ccef7c`, prereg `F=6ed2d368`, lane tip at my
runs `6e502c5c05fd3ca4193883921ef0c9b79a7d36a7` (read with `git rev-parse refs/heads/master`).
I changed no lane file, ran no git/jj mutation, and did not touch C2.

Every run reads the working tree, so both receipts re-assert the measured bytes at run time in their own headers
(`# counter … sha256=fd0a8e24…`, `# harness … sha256=d6f4e612…`, `# mutants … sha256=9368b342…`, plus every population
pin) — a lane-tip move during the wave cannot have changed what I measured, since the instrument shas match the ticket
list in every header.

## 1. Verdict

**C1 is NOT falsified by anything I produced.** Both arms reproduce on committed bytes, both SUMMARY lines match the
prereg's wording word for word, each new row is killed by exactly its own mutant and survives the other nine, and each
new mutant survives every one of the 49 r86 rows (so the delta is not vacuous).

### Arm A — before: `--only r86 --expect-killed 8`

```
ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0
MUTANT-PAIR m12-token-on-line pop=r86 killed=no mismatches=0 errors=0 exit=0
MUTANT-PAIR m16-nf6b-punct pop=r86 killed=no mismatches=0 errors=0 exit=0
SUMMARY mutants=10 sets=r86 pristine_r86=ok killed_r86=8 killed_total=8
BEFORE-EXIT:0
```

The other eight `MUTANT-PAIR` lines are `pop=r86 killed=yes` (m8 `mismatches=2`, m9 `mismatches=4`, the rest `=1`).
Receipt: `r86-only-expect8.txt`. `diff <(tail -n +3 r86-only-expect8.txt) census/round-87/controls/c1-before.txt` is
**empty** — my re-derivation is byte-identical to the filed control receipt.

### Arm B — after: `--only r86,r87 --expect-killed 18`

```
ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0
ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0
SUMMARY mutants=10 sets=r86,r87 pristine_r86=ok pristine_r87=ok killed_r86=8 killed_r87=10 killed_total=18
AFTER-EXIT:0
```

Ten `MUTANT-PAIR` lines: **10/10 `pop=r87 killed=yes`**, **8 `pop=r86 killed=yes`**, **2 `pop=r86 killed=no`**
(`m12-token-on-line`, `m16-nf6b-punct`). Receipt: `r86-r87-expect18.txt`.

Independence check: while my arm was running, the L1 produced the same command's receipt at
`census/round-87/records/c1-after.txt`, and `diff <(tail -n +3 r86-r87-expect18.txt) census/round-87/records/c1-after.txt`
is **empty** — two independent runs, same bytes, same SUMMARY.

## 2. Population and item facts re-verified against the pins

| artefact | sha256 measured | pin in ticket | rows |
|---|---|---|---|
| census/round-87/c1-false-rows.tsv | b066fa0f…869220 | match | 51 data rows (2 comment lines, `wc -l` 53) |
| census/round-86/c1-false-rows.tsv | 79db70f6…e140f561 | match (prereg) | 49 |
| census/round-87/c1-items.tsv | ce80195d…178d2e9 | match | 5 |
| census/round-87/c1-mutants.json | 9368b342…0338d132 | match (`members` = 10) | 10 |
| census/round-87/c1-pointer-counter.py | fd0a8e24…a755220b | match | |
| census/round-87/c1-false-row-harness.py | d6f4e612…c86fabaef | match | |
| census/round-87/c1-clause-battery.py | b0c1472b…d3c1aaeb | match | |
| controls/c2-before-base-tool.py | cf875367…425cbddc | match | |
| controls/souji-receipt-write.py | 70bbf1c2…61bcdefa | match | |

- Composition: the first 49 data rows of the r87 population are **byte-identical and in the same order** as the r86
  population (`grep -v '^#' | head -49` vs the r86 file: empty diff); `TQ1` and `NE1` are appended last (lines 52–53).
- `c1-items.tsv` = the r86 four items byte-for-byte plus one appended line (`I87E<TAB>LOG.md<TAB>3166<TAB>…`); base
  `705fa138` unchanged. The counter's r86 POPS entry (`5abf3b01… → ("r86", 705fa138…, 4)`) is byte-identical in the
  r87 counter; harness `BASE` (`e65538e7`) unchanged.
- `c1-ledger.tsv` sha256 `7cbb28c9…82abce` in **both** rounds (byte-for-byte, as the prereg states).
- The battery's r86 `PINS` entry is retargeted from `HERE/…` to `census/round-86/…` — necessary because `HERE` moved to
  round-87; the printed header confirms `# population r86 path=…/census/round-86/c1-false-rows.tsv … rows=49`.

## 3. Per-row attribution (driven by hand, one forged row at a time)

Fixture built by importing the filed harness's `build_fixture` into my own scratch and asserting
`git -C <fx> rev-parse --show-toplevel == <fx>`; each cell is **one forged row judged by a counter binary I invoke
myself** — no harness scoring in the loop (`byhand-matrix.py`, in this seat dir, is the driver).

Row × counter matrix, 2 rows × (pristine + all ten mutants) = **22 cells, 2 mismatching**:

| row | clause | mutant | pristine `got` | mutant `got` | match |
|---|---|---|---|---|---|
| TQ1 | `_whole` sentence-end punctuation disjunct (`.`/`,`/`;`/`:` then non-path byte) | `m16-nf6b-punct` | `QUARANTINED` | `REFUSED` | **no** |
| NE1 | R0 guard's token-on-line half | `m12-token-on-line` | `ERROR` | `REFUSED` | **no** |

Every other of the 20 cells matches. The counter's own lines, verbatim:

```
CELL row=TQ1 variant=pristine       expect=QUARANTINED/- forge=REFUSED got=QUARANTINED rc=1 match=yes | ITEM L06 LOG.md:946 status=QUARANTINED
CELL row=NE1 variant=pristine       expect=ERROR/-      forge=ERROR   got=ERROR       rc=1 match=yes | ITEM I87E LOG.md:3166 status=ERROR token not on the base line
CELL row=TQ1 variant=m16-nf6b-punct expect=QUARANTINED/- forge=REFUSED got=REFUSED     rc=1 match=no  | ITEM L06 LOG.md:946 status=QUARANTINED
CELL row=NE1 variant=m12-token-on-line expect=ERROR/-   forge=ERROR   got=REFUSED     rc=1 match=no  | ITEM I87E LOG.md:3166 status=UNRESOLVED
```

(For TQ1 the `ITEM` line reports the item under its **unforged** ledger row and stays `QUARANTINED`; the flip is on the
forged cell, i.e. exactly the R10 sentence-final declaration. For NE1 the item's own row is `UNRESOLVED`; pristine the
R0 guard fires first with its diagnostic, under m12 the item falls through.)

Attribution in the other direction — each new mutant over the whole population:

| counter | population | cells (pristine+mutant) | mismatching rows |
|---|---|---|---|
| m12-token-on-line | r87 (51) | 102 | **NE1 only** |
| m16-nf6b-punct | r87 (51) | 102 | **TQ1 only** |
| m12-token-on-line | r86 (49) | 98 | **none** |
| m16-nf6b-punct | r86 (49) | 98 | **none** |

Attribution table:

| row | clause | sole killer mutant | sole killer? | evidence |
|---|---|---|---|---|
| TQ1 | `_whole` punctuation disjunct | `m16-nf6b-punct` | **yes** — m16 flips no other row of either population; TQ1 flips under no other mutant | `matrix-TQ1-NE1.txt`, `scan-m16-population-r87.txt`, `scan-m12-population-r87.txt` |
| NE1 | R0 token-on-line | `m12-token-on-line` | **yes** — m12 flips no other row of either population; NE1 flips under no other mutant | same receipts, `scan-m12-population-r87.txt` |
| (both) | — | non-vacuity | **yes** — both mutants are green on all 49 r86 rows | `scan-m12-population-r86.txt`, `scan-m16-population-r86.txt` |

## 4. Instrument delta, r86 predecessor → r87 filed bytes

Every changed line, out of a line-set comparison (not a re-read of the docstrings). Line numbers are **new-file** lines.

### census/round-87/c1-pointer-counter.py (3 hunks)
| hunk | lines | content | class |
|---|---|---|---|
| replace | 2–7 / old 2 | new r87 docstring preamble, r86 header demoted to line 7 | docstring |
| insert | 146–152 | comment block + POPS pin `ce80195d… → ("r87", 705fa138…, 5)` | pin |
| replace | 561 / old 549 | `r[4] not in ("REFUSED","MISMATCH")` → `(… , "ERROR")` | ERROR expectation |

### census/round-87/c1-false-row-harness.py (7 hunks)
| hunk | lines | content | class |
|---|---|---|---|
| replace | 2–8 / old 2 | r87 docstring preamble, r84 header demoted | docstring |
| replace | 103–104 / old 97 | `POP_PINS` gains `b066fa0f…: 51` (r86 line gains a comma) | pin |
| replace | 112–113 / old 105 | `POPS` gains `"r87": (census/round-87/c1-items.tsv, c1-ledger.tsv)` | pin |
| insert | 280–287 | **R10 fixture block**: append the sentence-final declaration to `corpus/lessons/round-79-collision.md`, `git add`, `git commit`, `revs["R10"]` | R10 fixture block |
| replace | 294 / old 278 | leaf loop gains `"lemma-stub"` (the disk-only quarantine leaf the R10 line names) | R10 fixture support — **outside the commit block, flagged** |
| replace | 326–327 / old 310 | accepted rev-label tuple gains `"R10"` (judging-side population validation) | R10 support — **outside the commit block, flagged** |
| replace | 348–349 / old 331 | forge expectation cell: `'ERROR' if exp_got == 'ERROR' else (…)` | ERROR expectation |

### census/round-87/c1-clause-battery.py (3 hunks)
| hunk | lines | content | class |
|---|---|---|---|
| replace | 2–8 / old 2 | r87 docstring preamble | docstring |
| replace | 56–59 / old 50–51 | `PINS` r86 path retargeted to `census/round-86/…`; new `"r87": (HERE/c1-false-rows.tsv, b066fa0f…, 51)` | pin |
| replace | 90 / old 82 | argparse `--only` **help string** gains `, r87` | **FLAGGED** — help text only, not a pin / R10 / ERROR-expectation / docstring; zero behavioural effect |

**Verdict on the delta: no unexpected code change.** The only line outside the four named categories is the battery's
`--help` wording (new line 90); the two harness lines at 294 and 326–327 are R10 support that sits physically outside
the R10 commit block. No rule, class, message, branch, arm, kill rule or summary line changed — verified by reading each
hunk, and corroborated by the fact that the r86 arm's per-mutant mismatch counts are identical across the two rounds
(m8=2, m9=4, rest=1).

## 5. Third candidate (`_capture_ok` suffix) independently re-derived

The prereg says the candidate row was measured and **not** added because r86 row `NF12c` already kills it. I built that
mutant myself from the clause text — drop `have[-len(want):] == want` from `_capture_ok` (line 360) — and ran the
**filed** r87 harness on the **filed** 49-row r86 population:

```
ROW NF12c where=fixture rev=R5 item=P04 class=MOVED expect=REFUSED/- got=MOVED rc=1 match=no
SUMMARY rows=49 mismatches=1 accepted=1 refused_true=0 errors=0
```

Exactly the shape the record claims (`rows=49 mismatches=1`, NF12c the mismatching row). The sentence holds; adding a
row would have been padding. Receipt `c8-candidate-filed-harness.txt`, mutant `c8-capture-suffix.py`.

Stronger check, after the wave filed the mutant as a control: `census/round-87/controls/c1-mutant-c8-capture-suffix.py`
(sha256 `55a5f46f…`, the same counter bytes the record's `# counter … sha256=` names) differs from my reconstruction in
**one comment word on line 360 and nothing else**. Running that filed control through the **filed** harness on the
filed r86 population reproduces the record **byte for byte, headers included** against the current working-tree
`records/c1-c8-measured.txt` (itself a modified file at my read time). Receipt `c8-filed-control-filed-harness.txt`.

## 6. Findings and risks

1. **LOW (receipt provenance of the third-candidate record; not a falsifier, and already repaired in the working
   tree).** The **committed** `census/round-87/records/c1-c8-measured.txt` names `# harness sha256=4e29500a…` — neither
   the r86 harness (`2dac2e81…`) nor the filed r87 harness (`d6f4e612…`) — a counter at a scratch path
   (`/fast/scratch/hyaku/souji-r87/c8.py`), and fixture `R10=369d49ce…`, which no filed harness builds (the filed
   harness's R10 is `e5c9ebc5…`). Its **body**, however, is byte-identical to the current working-tree version of the
   record and is reproduced exactly by the filed control + filed harness (§5). No r86 row is judged at R10 (rev
   distribution: 4 BASE, 6 F0, 5 R1, 1 R2, 3 R3, 13 R5, 4 R6, 8 R7, 3 R8, 2 R9 = 49 rows), so the stale header is a
   provenance flaw with no effect on the judged rows. The working tree already carries the corrected header
   (`d6f4e612…`, the filed control path, `R10=e5c9ebc5…`), repaired by the L1 during my run; **the L1 must commit that
   repair** — at my read time it was ` M` (committed blobs still show `4e29500a…`).
2. **INFO.** `census/round-87/records/c1-after.txt` was untracked and mid-write while my arm ran; it is now complete,
   carries the SUMMARY line, and is byte-identical to my receipt. The claim cites the command for the after arm, not
   that receipt, so nothing turns on it; filing/committing it is the L1's call.
3. **INFO.** Over the r87 item population every counter invocation exits `1` **by design** (`I87E` is an `ERROR` item, so
   `resolved == N` can never hold). All 22 attribution cells show `rc=1` for pristine and mutant alike, and both new
   rows carry `exp_rc='-'`, so the harness compares only `got` and the battery scores the *harness's* rc — no kill can be
   manufactured out of that rc.
4. **INFO.** The r86 arm's `m8` (2) and `m9` (4) mismatch counts are pre-existing rows and are unchanged between the
   two populations; no new row rides on them.

## 7. Files written (all inside this seat dir) and limits

`S87ExecC1.md` (this report) plus: `byhand-matrix.py` (driver), `r86-only-expect8.txt`, `r86-r87-expect18.txt`,
`matrix-TQ1-NE1.txt`, `scan-m12-population-r87.txt`, `scan-m16-population-r87.txt`, `scan-m12-population-r86.txt`,
`scan-m16-population-r86.txt`, `c8-candidate-filed-harness.txt`, `c8-capture-suffix.py`,
`c8-filed-control-filed-harness.txt`.

No lane file, MANIFEST, `.ufo/state`, `.ufo/watchdog.log` or sibling-lane file was written; the lane tip was
`89d36922` at the end of my seat (it moved from `6e502c5c` during my run — another member's commit, not mine).
C2 was not run (other seat).
Scratch `/fast/scratch/hyaku/souji-r87/S87ExecC1` (17 G of fixture clones) is **removed**; no counter `--work` dir
remains.
Stated limits I did not exceed: the ten mutants are the frozen ten, not a generated battery; the fixture is the filed
harness's own; my first reconstruction of the c8 candidate is my reading of the clause text — it turned out to differ
from the filed control (`census/round-87/controls/c1-mutant-c8-capture-suffix.py`) only in a comment, and the filed
control is what my final reproduction uses.
