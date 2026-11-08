# S87MutCounter — C1 mutant set and population attack (r87 w1)

Seat: S87MutCounter (mutation-tester). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Frozen contract: `census/round-87/preregistration.txt` (F `6ed2d368…`), P `77ccef7c…`, lane base
`5e288bb3…`. This seat owns only `.ufo/waves/round-87/w1/S87MutCounter/`; all clones, mutant copies and
harness `--work` dirs live under `/fast/scratch/hyaku/souji-r87/S87MutCounter/` (deleted before yield;
receipts copied to `receipts/` beside this file). The filed counter, populations, mutants, battery and
harness were only ever read; every mutation was written as a separate scratch file.

## 0. Verdict

- The claim's numbers reproduce exactly. Before: `pristine 49/0`, `killed_r86=8`, m12 and m16
  `killed=no`, EXIT 0. After: `pristine r86 49/0`, `pristine r87 51/0`, all ten `killed=yes` on r87,
  m12/m16 `killed=no` on r86, `killed_r86=8 killed_r87=10 killed_total=18`, EXIT 0. An independent run of
  the frozen harness per mutant attributes every r87 kill to its named row; the filed after receipt
  `records/c1-after.txt` (42 lines at final read) is arm-line-identical to my run.
- Both new rows are load-bearing: NE1 is the unique r87 killer of m12, TQ1 the unique r87 killer of m16,
  and both mutants are alive on the 49-row population (delta not vacuous).
- **No falsification of the literal ten-mutant sentence or the before/after split.** The certification
  reading is narrowed: four measured survivors of *single edits* on those two clauses and on two further
  r85-survivor clauses are not carried by the prereg's limits (section 6). Two of them are alternative
  spellings of the very clauses TQ1/NE1 are said to bind.

## 1. Instruments re-measured (all pinned hashes)

| instrument | pinned | measured | verdict |
|---|---|---|---|
| c1-false-rows.tsv (51 rows) | b066fa0fc686…69220 | same | match |
| c1-items.tsv (5 items, base 705fa138) | ce80195de8b9…d2e9 | same | match |
| c1-mutants.json (10 members) | 9368b34234bf…d132 | same | match |
| c1-pointer-counter.py | fd0a8e244a5e…220b | same | match |
| c1-false-row-harness.py | d6f4e612f08f…baef | same | match |
| c1-clause-battery.py | b0c1472be3d0…aaeb | same | match |
| c2-k4-counter.py | 4e2b7c060625…f9e | same | match |
| controls/c2-before-base-tool.py | cf8753673b56…ddc | same | match |
| controls/souji-receipt-write.py | 70bbf1c2a92e…defa | same | match |

Re-measured again after all probes (`receipts/final-remeasure.txt`): unchanged. No mismatch.
Population shape: the r86 49 data rows are r87[0:49] **byte-for-byte**; appended rows `TQ1`, `NE1`.
Items: r86 four rows are r87[0:4] byte-for-byte; appended `I87E`. Ledger: r86/r87 byte-identical
(`sha256 7cbb28c9…abce`). Diff audits (r86→r87): counter changed only by docstring + the r87 `POPS` pin +
`("REFUSED","MISMATCH")`→`(…,"ERROR")`; battery only docstring/help/`PINS`; harness only docstring,
`POP_PINS`/`POPS`, the R10 fixture + rev label and the forge expectation cell carrying `ERROR`. No
resolution rule, judgement line, arm or kill rule changed.

## 2. Arms reproduced

Commands (cwd = lane):
```
before: python3 -B census/round-87/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
          --work <scratch> --only r86 --expect-killed 8            # EXIT=0
after:  python3 -B census/round-87/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
          --work <scratch> --only r86,r87 --expect-killed 18        # EXIT=0
```
Before arm (`receipts/before-arm.txt`): `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`;
m6..m11,c7,m14 `killed=yes`; `m12-token-on-line … killed=no mismatches=0`; `m16-nf6b-punct … killed=no
mismatches=0`; `SUMMARY mutants=10 sets=r86 pristine_r86=ok killed_r86=8 killed_total=8`. Arm lines are
identical to `controls/c1-before.txt` (that receipt additionally carries `BEFORE-EXIT:0`).

After arm (`receipts/after-arm.txt`): `ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0`;
`ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0`; ten `MUTANT-PAIR … killed=yes` on r87;
m12/m16 `pop=r86 killed=no`; `SUMMARY mutants=10 sets=r86,r87 pristine_r86=ok pristine_r87=ok
killed_r86=8 killed_r87=10 killed_total=18`; shell EXIT=0. Arm/SUMMARY lines are identical to
`census/round-87/records/c1-after.txt`.

Load-bearing attribution, one frozen-harness run per (mutant, population) in separate fixture builds:
| mutant | r86 | r87 | red row(s) on r87 |
|---|---|---|---|
| m6-digest-blind | 49/0 | 51/1 | NF-L |
| m7-round-blind | (r86 kill in before receipt) | 51/1 | NF-L2 |
| m8-w-only-shapes | " | 51/2 | TF9, TF10 |
| m9-basename-only | " | 51/4 | TF8, TF9, TF10, NF-P |
| m10-records-as-wave | " | 51/1 | NF-M |
| m11-class-enum | " | 51/1 | NF-S |
| c7-census-in-tree | " | 51/1 | NF-W |
| m14-short-shape | " | 51/1 | NF-Y |
| m12-token-on-line | 49/0 (alive) | 51/1 | **NE1 only** (`got=REFUSED`) |
| m16-nf6b-punct | 49/0 (alive) | 51/1 | **TQ1 only** (`got=REFUSED`, refused_true=1) |

## 3. Alternative spellings of the two clauses

Probe set: `receipts/probe-mutants.json` (sha256 `8935c650…cd9`), 8 single edits, each applied exactly
once; scored by the same battery (`--only r86,r87`) and by direct cells on the frozen fixture/lane.

| edit | killed r86 | killed r87 | classification | row that would bind it |
|---|---|---|---|---|
| m12 filed (drop `token in blob[int(line)-1]`) | no | yes | row binds | NE1 |
| p1 m12-offbyone (`blob[int(line)-2]`, previous line) | yes (49/49) | yes (51/51) | killed; a broad R0 break, not a spelling gap. NE1 also flips (cell: `got=REFUSED`) | every nominal row |
| p2 m12-basename (`os.path.basename(token) in …`) | **no** | **no** | **survivor: row binds only the full-token spelling** | new NE1-class item (line carries the basename, not the token; expect ERROR) |
| m16 filed (drop punctuation disjunct) | no | yes | row binds | TQ1 |
| p3 m16-lookahead (keep `. , ; :`, drop `after[1] not in PATHCH`) | **no** | **no** | **survivor: the after-byte half is bound by no row** | false row at a fixture rev with a both-legs `.bak` declaration (PX1 shape, expect REFUSED) |
| p4 m16-noperiod (drop only the `.` member) | no | yes | killed by TQ1 (cell `got=REFUSED`) | TQ1 — binds the period member specifically |

Details:
- **p2.** NE1's declared line LOG.md:3166 at base 705fa138 carries neither the token nor its basename, so
  p2 still reports ERROR on NE1 (cell: pristine `got=ERROR`, p2 `got=ERROR`, filed m12 `got=REFUSED`). A
  rule-level differential with a synthetic blob line carrying only `/x/y/c1-after.txt` gives pristine
  `('ERROR','token not on the base line')` vs p2 `('UNRESOLVED','')`; control line with the full token
  gives UNRESOLVED in both. The granularity is reachable and unrowed; the population's items all carry
  the full token on their declared lines, so no frozen row distinguishes it.
- **p3.** TQ1's period is at line end (`after = b"."`), so the lookahead clause is not exercised:
  `FORGE TQ1 … got=QUARANTINED` under p3 and `REFUSED` under the filed m16. NF6b does not bind it either:
  under p3 NF6b is still `REFUSED` because its token occurrence `.gitignore-p6repo` is followed by a path
  byte (the *first* disjunct fails, not the lookahead). Reachability measured on the pristine fixture plus
  one scratch commit (`198b3361…`) whose authority line names `…/other-stub.bak` and the L06 token at a
  sentence end: pristine `FORGE PX1 … got=REFUSED match=yes`, p3 `got=QUARANTINED match=no`, filed m16
  `got=REFUSED match=yes`. So a false PX1-style row would bind p3 — and the declaration p3 accepts is a
  prefix collision the counter should refuse.

## 4. Four further single-edit drops (r85 survivor list)

Each applies exactly once, survives both pinned populations (`receipts/probe-battery.txt`:
p5/p6/p7/p8 all `killed=no` on r86 and r87; battery pristine `49/0` and `51/0`), and each got a
differential probe:

| id | clause dropped | differential probe (actual output) | classification |
|---|---|---|---|
| p5 m17-dupid | `_ledger` `r[0] in ledger` | lane, r87 items + ledger with `I85R` twice: pristine `LEDGER-REFUSED id=I85R`, `SUMMARY … refused=1`, rc 1; mutant no refusal, `refused=0`, rc 1 | reachable-unrowed; **carried** by the prereg limits (m17). No row can supply a duplicate: the harness passes the frozen ledger and replaces one row |
| p6 authbool | `bool(want)` in `_capture_ok` | 161 472 round-qualified token/target pairs (all frozen cells, synthetic capture shapes, 120k seeded random): 0 differences; no `CAPTURE` match over 181 945 probes yields an empty component list (`(.+)` tail cannot end in `/` after the rstrip) | **dead**; retire the suspicion (not the carried `len(want) <= len(have)` half) |
| p7 regularmode | `_regular` mode whitelist `mode in (100644,100755)` | clone at `d4f51563…`, `census/round-73/records/c2-after-D3.txt` replaced by a symlink (mode 120000), committed (`344cff2c…`): range item `P19` pristine `REFUSED … why=range member is not a regular file: …D3.txt`, mutant `TOKEN`; control at the base commit (regular file) both `TOKEN` | reachable-unrowed; **NOT carried** in the prereg limits (NF8's row binds only the directory leg: a tree entry still fails `typ == b"blob"`) |
| p8 tokenmarker | `token_ok` trailing marker `">\\-"` → `">\\"` (drop `-`) | lane, r87 items + filed ledger at `5e288bb3…`: pristine `I85T … status=TOKEN`; mutant `I85T … status=REFUSED why=no parse artefact`. Proposed binding row measured: `L13 TOKEN census/round-49/sources/s272-python-open-located-quote.txt` at harness BASE gives pristine `got=TOKEN`, p8 `got=REFUSED` | reachable-unrowed; **NOT carried** in the prereg limits (NF-S deliberately forges I85T with class `BOGUS`, refused by the class enum before `token_ok`) |

## 5. Can TQ1's row be satisfied by a declaration the counter should refuse?

YES — measured. TQ1's `got=QUARANTINED` is invariant under p3 (lookahead dropped), and under p3 the
counter resolves a declaration the filed counter refuses: `…/other-stub.bak` (prefix collision) plus the
token at a sentence end (`PX1`: pristine `REFUSED`, p3 `QUARANTINED`, filed m16 `REFUSED`). TQ1 certifies
only that the `.` member of the punctuation set at line end makes the token whole; it does not certify the
after-byte lookahead (no row does, NF6b included), and it does not certify that the line is a real
declaration — `_declared` is co-occurrence of the two whole paths on one authority line, a documented
stated limit. A false PX1-style row (expect REFUSED) would bind the lookahead half; TQ1 cannot, because a
true row only ever exercises acceptances.

## 6. Survivors not carried by the prereg's limits

Carried by the frozen limits: m17 duplicate-id (p5), the `_whole` before-byte half, the
`len(want) <= len(have)` half. Not carried, measured surviving both populations:

1. **p2 — token-on-line granularity.** A rule that only requires the token's basename on the declared
   line passes both populations and is not killed by NE1. Binds: a new item whose declared line carries
   the basename but not the token (expect ERROR).
2. **p3 — `_whole` after-byte lookahead.** No row binds the `after[1] not in PATHCH` half; TQ1's period
   is at line end and NF6b fails on the first disjunct. Binds: a false row with the PX1 declaration.
3. **p7 — `_regular` symlink leg.** NF8 binds only the directory leg; a symlink (120000) range member is
   accepted by p7 and refused by the filed counter. Binds: NF8-class false row at a rev where a range
   member is a symlink.
4. **p8 — `token_ok` hyphen marker.** I85T's trailing `-` is only forged with class `BOGUS`, so the
   marker leg is not exercised. Binds: the L13-class TOKEN true row (wrapped continuation).

Do not read the claim's "two clauses get rows" as binding either clause whole: each new row binds one
spelling (NE1: full token absent; TQ1: period at line end). That is a narrowing of the certification
sentence, not of the ten-mutant numbers, which reproduce exactly.

Also note: the battery's `--expect-killed 18` gate checks only the total. The claim's per-population split
(`killed_r86=8`; the two new mutants alive on r86) is enforced only by the printed lines and the receipt,
not by the exit code; this reproduction checks the split explicitly (above).

## 7. Evidence index (`receipts/`)

- `after-arm.txt`, `before-arm.txt` — the two battery runs (full stdout).
- `probe-battery.txt` — the 8-member probe set scored on both populations (`killed_r86=1`,
  `killed_r87=2`; p2/p3/p5/p6/p7/p8 survive both).
- `probe-mutants.json` — the eight single edits (sha256 `8935c650…cd9`); per-file sha256 in
  `instrument-hashes.txt`.
- `shards/*.txt` — one frozen-harness run per (filed mutant, population), with `ROW … match=no` lines
  naming the killers.
- `cells-ne1.txt`, `cells-tq1-nf6b.txt`, `cells-px1.txt`, `cells-l13-p8row.txt` — direct one-row forge
  cells (pristine vs variant) on the lane BASE / frozen fixture revs.
- `dup-pristine.txt`, `dup-mutant.txt`, `dup-ledger.tsv` — p5 duplicate-id probe.
- `p19-ctrl-*.txt`, `p19-sym-*.txt`, `p19-ledger.tsv` — p7 symlink range probe + regular-file control.
- `instrument-hashes.txt`, `final-remeasure.txt` — pinned instruments and every mutant file hash.
- `pristine-r87.txt` — pristine 51-row arm (51/0/0) and the fixture rev table.

Scratch: `/fast/scratch/hyaku/souji-r87/S87MutCounter/` removed after copying; nothing left behind. No
lane file outside this seat's directory was written; `census/round-87/records/c1-after.txt` was observed
mid-write at 06:56 (untracked, 25 lines) and complete at final read (42 lines) — read-only throughout.

## 8. Scope limits of this seat

One mutation probe per listed clause; probes are hand single edits, not a generated battery. The p7 row
proposal was measured on a scratch clone at the r77 base, not on a frozen fixture rev (no rev carries a
symlink range member). The p2 item proposal is a rule-level differential plus an NE1-cell control, not a
frozen row. TQ1's declaration semantics (`_declared` co-occurrence) remain the prereg's stated limit.
