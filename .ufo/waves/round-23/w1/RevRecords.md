# RevRecords — r22 C1/C2 record reconstruction (round 23, w1)

## Status

STATUS: PASS — all four records read at `1208bfb` (committed bytes only); every r22 C1 4-tuple and
every r22 C2 tally occurrence is located, quoted and attributed to a receipt or to `none`.
Reproduction was executed for the C1 counts line at five revisions. Two frozen-counter blind spots
(K2 reference choice, K3 file scope) are reported as ATTACK, not edited.

## Evidence

Revision: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (lane base, `git rev-parse HEAD`).
All reads via `git show HEAD:<path>` / `git grep <pat> HEAD`; no worktree bytes used for any record.

E1 — tool digests by revision (`git show <rev>:<tool> | sha256sum`, first 16 hex):

```
HEAD       decl=65817d0d0d4874e8 gate=d5ed0805b10f283f
9301d98    decl=65817d0d0d4874e8 gate=d5ed0805b10f283f
4edb25d    decl=e3b0c44298fc1c14 gate=e3b0c44298fc1c14   (both ABSENT; git cat-file -e fails)
c9f1fe3    decl=65817d0d0d4874e8 gate=5b8025a83f16957c
ee1aef2    decl=05b53b7d419c2315 gate=5b8025a83f16957c
8680755    decl=65817d0d0d4874e8 gate=5b8025a83f16957c
```

E2 — blob ids (`git rev-parse <rev>:<path>`, first 8 hex):

```
rev      gate-check  slice-verdicts  before    before-final  instrument-digests
c1664fc  f26aa728    f6131eac        26db2196  (absent)      b76e39bf
7bc458c  f26aa728    f6131eac        26db2196  (absent)      b76e39bf
8680755  f26aa728    36bf7ed9        26db2196  (absent)      b76e39bf
9301d98  63ac63b8    e12665c6        26db2196  184b4001      8a60b89f
HEAD     63ac63b8    e12665c6        26db2196  184b4001      8a60b89f
```

E3 — commit order (`git log --oneline`, oldest first): `5fdd5d5 ee1aef2 4a6ee90 c9f1fe3 f8f0b4a
8990ae4 c1664fc 7bc458c 8680755 9fcc4f7 dd8a6b7 9301d98 77d6595 1208bfb`.

E4 — counts line re-derived by this seat with the digest-pinned instrument
(`python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev <rev> --format counts`;
read-only, `-B`, no scratch, no worktree write):

```
4edb25df rc=1 assertions=55 resolved=52 skipped=33 mismatches=3
8990ae4  rc=0 assertions=62 resolved=62 skipped=39 mismatches=0
c1664fc  rc=0 assertions=62 resolved=62 skipped=39 mismatches=0
7bc458c  rc=0 assertions=62 resolved=62 skipped=39 mismatches=0
8680755  rc=0 assertions=62 resolved=62 skipped=39 mismatches=0
9fcc4f7  rc=0 assertions=62 resolved=62 skipped=39 mismatches=0
dd8a6b7  rc=1 assertions=63 resolved=62 skipped=40 mismatches=1
9301d98  rc=0 assertions=63 resolved=63 skipped=40 mismatches=0
77d6595  rc=0 assertions=63 resolved=63 skipped=40 mismatches=0
```

E5 — the SCORECARD blob at the revision the row names as tip is not the blob that carries the row:
`git show 9301d98:SCORECARD.md | sed -n 14p` names `tip 8990ae4c6284005d42e6edeb9bf0060a2450f566`
and carries `assertions=62 resolved=62 skipped=39 mismatches=0`; the row at `77d6595` and at HEAD
names `tip 9301d98c1c689c79741f0f1ba1f171138d20af07` with `assertions=63 resolved=63 skipped=40
mismatches=0`.

E6 — receipts present at HEAD under `census/round-22/attempt2/`: `declared-evidence-before.tsv`,
`declared-evidence-before-final.tsv`, `instrument-digests.txt`, `slice-verdicts.tsv`,
`quarantine-slice`, `sources/` (13 snapshots). There is **no** `declared-evidence-after.tsv`, no
gate-check receipt, and no counter `.txt` under `census/`.

E7 — `git grep -nE '^(rev|tool_sha256)=' HEAD -- census` → zero hits. No committed census receipt
carries a `rev=` or `tool_sha256=` header.

E8 — `slice-verdicts.tsv` (blob `e12665c6`) rows 2-9: `S114 accepted, S118 unverifiable, S123
accepted, S124 accepted, S126 present, S131 accepted, S133 accepted, S138 present` → tally
accepted=5, present=2, unverifiable=1, refused=0. Line 1 is a comment: ids are campaign register
ids, not lane registry ids.

E9 — `git show HEAD:LOG.md | grep -n 'superseded by'` → zero hits in the whole file.

E10 — working tree (for the C1 K4 neighbourhood only, not this item): 13 porcelain paths, of which
5 are ` M .ufo/waves/round-22/attempt2/w1/{CritC1Axis,DraftScorecard,ImplDeclaredA}.md` plus their
`evidence/` twins, and 2 are `?? .ufo/waves/round-22/attempt2/w1/evidence/impl-a/head-c9f1fe3.*`.
D1 reproduces as routed. `tools/__pycache__/` (05:11/05:12) was written by another seat, not by
this one (all runs used `-B`).

## C1 — every 4-tuple occurrence in the four records

| # | location | value as quoted | revision / digest token on the line | receipt binding |
|---|---|---|---|---|
| C1-a | SCORECARD.md:14, byte 353 of the line | `assertions=55 resolved=52 skipped=33 mismatches=3` | rev `4edb25dfe262515d0da63224bbba71e02e36cba5` (base); tool digest `65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4` via `census/round-22/attempt2/instrument-digests.txt:1`, which names no revision | **BOUND** to `declared-evidence-before-final.tsv:56`, byte-equal counts line. Caveat: that file does not exist at the named base rev; its rows carry `4edb25dfe262515d0da63224bbba71e02e36cba5` inside the detail cell, and there is no `rev=` header (E7) |
| C1-b | SCORECARD.md:14, byte 451 | `assertions=63 resolved=63 skipped=40 mismatches=0` | rev `9301d98c1c689c79741f0f1ba1f171138d20af07` (tip); same digest | **NONE**. No committed receipt states this tuple (E6). Reproduced by this seat at that rev, rc=0 (E4) |
| C1-c | SCORECARD.md:14, byte 552 | `67/67/40/0`, abbreviated, described as a wider span-inclusive class-B reading, attributed to the residual seat | no revision token; no digest | **NONE**. The receipted wider reading is `66/66/40/0` (`ResDeclaredEvidence.md:132`), measured at the 62-tip |
| C1-d | SCORECARD.md:14, byte 1393 (evidence column) | `assertions=63 resolved=63 skipped=40 mismatches=0`, after the command `--rev <tip> --format counts` and exit 0 | `<tip>` is a literal placeholder, not hex | **NONE** (self-assertion of C1-b) |
| C1-e | SCORECARD.md:14, byte 1613 (evidence column) | `assertions=55 resolved=52 skipped=33 mismatches=3`, introduced as the same pinned instrument | measured-at cell `4edb25dfe262515d0da63224bbba71e02e36cba5` | **BOUND** to `declared-evidence-before-final.tsv:56` |
| C1-f | SCORECARD.md:14 (evidence column, abbreviated) | `56/53`, attributed to `census/round-22/attempt2/declared-evidence-before.tsv` as the pre-hardening reading kept as history | none | **BOUND** in value to `declared-evidence-before.tsv:57` (`assertions=56 resolved=53 skipped=33 mismatches=3`); the abbreviation carries no skipped/mismatches |
| C1-g | LOG.md:1484-1485 (tuple split across the line break) | `assertions=56 resolved=53 skipped=33 mismatches=3` | rev `4edb25d` (7-hex, inside `--rev 4edb25d --file SCORECARD.md`) | **BOUND** to the receipt named in the same sentence, `declared-evidence-before.tsv:57`, byte-equal. No later LOG line carries the marker `superseded by` (E9) |
| C1-h | corpus/lessons/round-22.md:314 | `assertions=56 resolved=53 skipped=33 mismatches=3`, labelled the pre-hardening instrument | rev `4edb25d` (M15 text, line 307) | **BOUND** to `declared-evidence-before.tsv:57`, named in the same sentence |
| C1-i | corpus/lessons/round-22.md:314 | `55/52/33/3`, labelled the pinned instrument at the same revision | same rev | **NONE named**. The file that carries it (`declared-evidence-before-final.tsv:56`) appears nowhere in round-22.md; only SCORECARD:14 and `round-22-verifier-spotcheck.md:105` name it |

Digest/revision tokens attached to C1 outside the tuples:
`instrument-digests.txt:1-2` (two sha256 values, no revision; line 3 defers the revision to
SCORECARD and the round report) and `instrument-digests.txt:3` `round=22 attempt=2 date=2026-10-25`.

## C2 — every accepted/present/unverifiable/refused tally occurrence in the four records

| # | location | value as quoted | revision / digest token on the line | receipt binding |
|---|---|---|---|---|
| C2-a | corpus/lessons/round-22.md:351-355 | `5 accepted`, `2 present` (S126, S138), `1 unverifiable` (S118), `0 refused` | none; receipt named at :349 as `census/round-22/attempt2/slice-verdicts.tsv` | **BOUND** and agrees with the 8 rows of blob `e12665c6` (E8) |
| C2-b | corpus/lessons/round-22.md:459 | `(5/2/1/0)` | none | **BOUND** in value to the same file |
| C2-c | corpus/README.md:440-441 | `5 accepted`, `1 present`, `1 refused` (wrong-source citation), `1 unverifiable` (unreachable DOI) | none; pointer at :442 to `../census/round-22/attempt2/slice-verdicts.tsv` | **CONTRADICTED** by that file (5/2/1/0). D4 reproduces |
| C2-d | LOG.md:1508-1510 | `5 accepted`, `1 present`, `1 refused` (S123 wrong-source citation), `1 unverifiable` (S118) | none | **CONTRADICTED** by the same file; `slice-verdicts.tsv:4` classes S123 `accepted`. No receipt is named in this LOG section |
| C2-e | corpus/README.md:427 | `2/2 entries, 8/8 register-slice verdicts` | none | after-half **BOUND** to `residual/evidence/counter.txt:30` and `ResSliceVerdicts-gate-counter.txt:10` (`entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`), both measured with gate blob `f26aa728` (sha256 `5b8025a83f16957c`), not the pinned `d5ed0805b10f283f` |
| C2-f | corpus/lessons/round-22.md:374 | `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0`, exit 0 | command at :368-373 | same as C2-e |
| C2-g | corpus/lessons/round-22.md:375-376 | before `entries=2 ok=0 slice_verdicts=0 slice_total=8 fail=10`, exit 1 | none | **NONE**. `fail=10` appears only in LOG:1512, round-22.md:375 and the spot-check:145 — no receipt file |
| C2-h | LOG.md:1511-1513 | before `entries=2 ok=0 slice_verdicts=0/8 fail=10 exit1`; after `entries=2 ok=2 slice_verdicts=8/8 fail=0 exit0`; `selftest 9/9` | none | after **BOUND** (`counter.txt:30`); selftest **BOUND** (`counter.txt:26`, `selftest=9/9`); before **NONE** |
| C2-i | SCORECARD.md (whole file) | no `<n> accepted` / `present` / `unverifiable` / `refused` tally occurrence at all | — | the calibration row does not restate C2; the only near-miss words are r21/r17 rows (`:15`, `:63`, `:73`) |

Other C2 tokens attached: `round-22.md:333` and `LOG.md:1502` give the vendored payload digest
truncated as `1634d206…8bb5`; `round-22.md:345` attaches full rev
`a211e4d1bf6ea592670d16269f34e9f67f33e8b3` to the census validate exit 0.

## Findings

1. **The r22 C1 after-value is reproducible but unreceipted (D2).** SCORECARD:14 (C1-b) states
   `63/63/40/0` at `9301d98`; this seat re-derived exactly that with the pinned instrument
   (`65817d0d`), rc=0 (E4). No file under `census/round-22/attempt2/` records it (E6). The only
   committed measurement of a 63-assertion declaration is `ResClaims.md:24`, `63/61/39/2`, rc=1, at
   `f8f0b4a` — a different revision and a different, non-zero mismatch count.

2. **The named tip was two commits behind when the row was written, and the row now names a
   revision whose own bytes carry the older numbers.** `9301d98:SCORECARD.md:14` names tip
   `8990ae4` with `62/62/39/0` (E5); the `77d6595`/HEAD row names `9301d98` with `63/63/40/0`. The
   62 values are receipted three times over (`ResDeclaredEvidence-counts-matrix.txt:4-16`); the 63
   values are receipted nowhere. The `9fcc4f7`→`9301d98` interval also contains an intermediate
   `dd8a6b7` state of `63/62/40/1` rc=1 (E4), which no record mentions.

3. **`67/67/40/0` (C1-c) is unbound and contradicted by the receipted wider reading.** The residual
   evidence's wider enumeration is `66/66/40/0` (`ResDeclaredEvidence.md:132`). The `67` in the
   residual's dropped-token list (`ResDeclaredEvidence.md:136`) is a SCORECARD *line number*
   (`67 4800fd7 B`), not a count. `[INFERENCE]` the parenthetical is 63 plus the four dropped
   class-B tokens, which arithmetically yields 67 at the new tip — but no receipt states it.

4. **D5 reproduces, and its occurrence is invisible to the frozen K2 predicate.** LOG:1484-1485
   (C1-g) is byte-equal to `declared-evidence-before.tsv:57`, the very file K2 compares against, so
   K2 finds no disagreement. The superseding value is the *other* receipt's `55/52/33/3`. LOG carries
   no `superseded by` line at all (E9).

5. **D4 reproduces in two records, not one.** README:440-441 (C2-c) and LOG:1508-1510 (C2-d) both
   say 1 present / 1 refused; the lesson (:351-355, :459) and `slice-verdicts.tsv` say 5/2/1/0. LOG
   additionally attributes `refused` to S123, which `slice-verdicts.tsv:4` classes `accepted` with a
   stated correction.

6. **No census receipt carries a `rev=` or `tool_sha256=` header (E7).** Revision binding in the r22
   receipts is carried only inside detail-cell prose (`present at 4edb25d…`) or in the records'
   own text. This is the before-state for C2's r23 counter: `grep -rlE '^tool_sha256=[0-9a-f]{64}$'
   census/ | wc -l` = 0.

7. **D3 reproduces on both C2 halves.** The digest pin (`instrument-digests.txt:2`) records
   `d5ed0805…` = blob `63ac63b8`, which exists only from `9fcc4f7` onward. Both committed gate
   counter receipts (`counter.txt:6,30`; `ResSliceVerdicts-gate-counter.txt:10`) were measured with
   blob `f26aa728` = `5b8025a8…`, the pre-`9fcc4f7` tool. No receipt binds the reported
   `entries=2 ok=2 …` line to the digest-pinned tool.

8. **The gate counter's declared inputs no longer match the tree.** `counter.txt:10` pins
   `slice-verdicts.tsv` at blob `f6131eac`; the committed blob is `e12665c6` (S118 cell rewritten at
   `8680755`, id-space header added at `dd8a6b7`) (E2).

9. **The base end of "same instrument, both ends" is a cross-revision measurement.**
   `tools/souji-declared-evidence.py` and `tools/souji-gate-check.py` are both absent at `4edb25d`
   (E1); the tool first lands at `a211e4d`. `declared-evidence-before-final.tsv` is likewise absent
   at the base rev (E2). The instrument identity holds for the tool *blob*, not for tool presence at
   the base revision.

10. **The lesson's pinned-instrument base value names no file (C1-i).** `declared-evidence-before-final.tsv`
    is named only in SCORECARD:14 and the spot-check (:105); `round-22.md` names only the
    pre-hardening receipt.

11. **The vendored payload digest is truncated wherever the records state it** (`LOG.md:1502`,
    `round-22.md:333` → `1634d206…8bb5`). The full 64-hex value survives only in residual evidence
    (`ResSources-checks.tsv:29`, `content.txt:49`) and the spot-check (:131).

12. **SCORECARD carries no C2 tally (C2-i).** A reader of the calibration row alone cannot see the
    slice tally that two other records get wrong; the C1 row is silent on C2.

## Attack log

Frozen counters are not edited. These are predicate defects visible from the reconstruction.

- **A1 — K2 compares against the wrong receipt.** K2 requires every LOG attempt-2 4-tuple that
  disagrees with `census/round-22/attempt2/declared-evidence-before.tsv` to be named by a later
  `superseded by` line. The occurrence D5 actually routes (LOG:1484-1485) is *equal* to that file,
  so K2 reports no mismatch; and the value the record now endorses (`55/52/33/3`) lives in a
  different file. With the key set as frozen, a correct D5 repair is not detectable and an
  uncorrected D5 is not reported.

- **A2 — K3's file scope omits LOG.md.** K3 reads only `corpus/README.md` and
  `corpus/lessons/round-22.md`. LOG:1508-1510 carries the same wrong tally (1 present, 1 refused)
  and no key covers it. A round that repairs README alone reaches `mismatches=0` while LOG still
  disagrees with `slice-verdicts.tsv`.

- **A3 — K3's occurrence form is narrower than the records' own notation.** K3 matches `<n> <class>`.
  The correct lesson form at :459 is `(5/2/1/0)`, which the predicate cannot match; a README repair
  written in that compact form would produce zero occurrences and could trip K3's "each record must
  carry at least one occurrence of each class" clause.

- **A4 — the base-end control depends on a tool that does not exist at base.** K1's control rule
  requires the same instrument to run at `1208bfb`'s base revision and report `mismatches>=1`. At
  `4edb25d` the pinned tool blob is absent (E1), so any implementation that resolves the tool at
  `--rev` will error rather than report a non-zero mismatch count, and the control will look
  unmet for a reason unrelated to the claim. The instrument must take its tool bytes from a
  revision where the tool exists while taking declaration bytes from the base rev — exactly the
  cross-revision shape of E4.
