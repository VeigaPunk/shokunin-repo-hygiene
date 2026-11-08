# S88MutCounter — r88 C1: do the two new rows bind their clause, and what else is reachable?

Seat: `S88MutCounter` (r88 w1, lane `souji`). Assignment: attack the new population
(`census/round-88/c1-false-rows.tsv`, +NF6g +LD1) and the twelve-member mutant set — is each new row load-bearing,
does it bind more than one spelling, what else is reachable but unrowed. Lane base
`7defe9c5fee3df07e403666bdeccfb88428ef729`; P `e60ea25f6dc6d988bbdd713a2d00718f5915e29d`; F `f74092b24bbddf2e5259977c254c91b7a6b71160`.

Nothing in the lane was written by this seat: every counter and harness tested below is a scratch copy under
`/fast/scratch/hyaku/souji-r88/S88MutCounter/` (deleted at yield). No git/jj state touched. Write scope used: this
report and `.ufo/waves/round-88/w1/S88MutCounter/` only.

## 0. Instruments re-measured — every pin matches

| file | sha256 | verdict |
|---|---|---|
| `census/round-88/c1-false-rows.tsv` (53 rows) | `b710e368de862a72bc430610003d3cdf1499bea1b6e4ff2325417a1d388a68c3` | MATCH |
| `census/round-88/c1-mutants.json` (12) | `baec8026a847cc28283c945374bcfe693f18b28c4580bd78508747dbc66cec9c` | MATCH |
| `census/round-88/c1-mutants-dead.json` (13) | `e7963787e92451ffba20f8025dae8cf62f0bdecc3f395160fa46e0525b015281` | MATCH |
| `census/round-88/c1-false-row-harness.py` | `1ae0cd39db962f804776b49c02c17fbf87324552ec9ee4fdbc734fe72814042b` | MATCH |
| `census/round-88/c1-clause-battery.py` | `6842ca47c4c7cf0dd42f5ba67df2060e4a56556ddd837b2238329a24fa2c5ff7` | MATCH |
| `census/round-87/c1-pointer-counter.py` | `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b` | MATCH (unchanged r87 bytes) |
| `census/round-87/c1-items.tsv` | `ce80195de8b978e5ed00a03c22c3f9911d841c9f277a2a736c730c455178d2e9` | MATCH (unchanged r87 bytes) |
| `tests/fixtures/r88-k4-flagfail.py` | `aa79133a7ed302b84abda3c194974b9e38250fd82be55743d9bc909f43e8335d` | MATCH |
| `tools/souji-record-agreement.py` | `c0604b4abf10a45dfcf6eb9f7bb2ad8efb805321c24677e45a192e9a73e4fdef` | MATCH |
| `census/round-88/controls/c2-before-tool.py` | `e1b00e8ae14f7059cb5d649dd9ae6e3a3a0498813beb22427af2473c8ac67ccc` | MATCH |
| `census/round-88/controls/c2-before.txt` | `28e5ad688b23af86d8f91872d0c81a5fdaff39f95ab5d30f97090a37c8133dc2` | MATCH |
| `census/round-88/controls/c1-before.txt` | `ce1352d228f6b8bc1e456c41eead51ba5f70a5422c7e63edf22575ac19b35c7f` | MATCH |

## 1. Arms reproduced

Every cell below is the frozen harness (`census/round-88/c1-false-row-harness.py`) scoring a scratch copy of the
frozen r87 counter on a pinned population, one fresh fixture per run, kill rule = the battery's
(`rc != 0 or mismatches > 0 or errors > 0`). Driver: `scorep.py` (per-variant and per-filed-mutant modes), logs
`probes2.txt`, `probes3.txt`, `probes4.txt`, `after2.txt`, `before.txt`.

### 1a. Pristine arms (green on both pinned populations)

```
ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0
ARM pristine pop=r88 rows=53 mismatches=0 errors=0 exit=0
```

Observed twice independently (frozen battery `after2.txt`; variant driver `probes2.txt`). Same in the L1 receipt
`records/c1-after.txt`.

### 1b. The twelve filed mutants, both populations — the after arm's content, reproduced

| mutant | r87 | r88 | red row(s) (r87 and r88 identical) |
|---|---|---|---|
| `m6-digest-blind` | killed (m=1) | killed (m=1) | `NF-L` |
| `m7-round-blind` | killed (m=1) | killed (m=1) | `NF-L2` |
| `m8-w-only-shapes` | killed (m=2) | killed (m=2) | `TF9`, `TF10` |
| `m9-basename-only` | killed (m=4) | killed (m=4) | `TF8`, `TF9`, `TF10`, `NF-P` |
| `m10-records-as-wave` | killed (m=1) | killed (m=1) | `NF-M` |
| `m11-class-enum` | killed (m=1) | killed (m=1) | `NF-S` |
| `c7-census-in-tree` | killed (m=1) | killed (m=1) | `NF-W` |
| `m14-short-shape` | killed (m=1) | killed (m=1) | `NF-Y` |
| `m12-token-on-line` | killed (m=1) | killed (m=1) | `NE1` (lane rev) |
| `m16-nf6b-punct` | killed (m=1) | killed (m=1) | `TQ1` |
| `m17-duplicate-id` | **survived** (m=0, rc=0) | **killed** (m=1) | `LD1` |
| `m18-whole-before` | **survived** (m=0, rc=0) | **killed** (m=1) | `NF6g` |

Counts: `killed_r87=10`, `killed_r88=12`, `killed_total=22`; `m17`/`m18` are the only two survivors on r87, and the
only two rows that change between the sets. Every mismatch count above is cell-identical to the L1's filed receipt
`census/round-88/records/c1-after.txt` (`m6` 1, `m7` 1, `m8` 2, `m9` 4, `m10` 1, `m11` 1, `c7` 1, `m14` 1, `m12` 1,
`m16` 1, `m17` r87 0 / r88 1, `m18` r87 0 / r88 1).

**Both new rows are load-bearing**: their kills are the delta and the only red rows on r88 are `NF6g` and `LD1`
respectively; no other row goes red under either filed mutant.

### 1c. The before arm

The frozen before command (`--only r87 --expect-killed 10`) was run and reached six mutants before the wall-clock
stop recorded below; every cell reproduced the filed control `census/round-88/controls/c1-before.txt` exactly:

```
ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0
MUTANT-PAIR m6-digest-blind   pop=r87 killed=yes mismatches=1 exit=1
MUTANT-PAIR m7-round-blind    pop=r87 killed=yes mismatches=1 exit=1
MUTANT-PAIR m8-w-only-shapes  pop=r87 killed=yes mismatches=2 exit=1
MUTANT-PAIR m9-basename-only  pop=r87 killed=yes mismatches=4 exit=1
MUTANT-PAIR m10-records-as-wave pop=r87 killed=yes mismatches=1 exit=1
MUTANT-PAIR m11-class-enum    pop=r87 killed=yes mismatches=1 exit=1
```

The remaining six r87 cells (`c7`, `m14`, `m12`, `m16`, `m17`, `m18`) were completed by the same harness in
`probes4.txt` + `probes2.txt`: four killed (`m=1` each), `m17`/`m18` survived. So the before arm's content is
`killed_r87=10` with `m17` and `m18` alive, exactly as filed.

### 1d. Belt

`m19-len-half` survives both sets (`probes3.txt`: r87 `m=0 e=0 rc=0`, r88 `m=0 e=0 rc=0`) — the
`_capture_ok` `len` half is a belt, not a row, as the prereg records and `records/c1-dead-belt.txt` shows.

### 1e. Disclosure (wall-clock, not a claim change)

The frozen battery is sequential and the fleet was at load 100+ during this seat's window (32 cores); a single
harness run cost 3–5 minutes. The sequential after command completed `m6` (both cells) and `m7` (r87) and the
sequential before command completed six mutants (`after2.txt`, `before.txt`) before this seat stopped them for
wall-clock. **The seat did not observe the frozen battery's own `SUMMARY killed_total=22 / EXIT=0` line** — the L1's
filed receipt does. The seats' cells above were completed by a parallel driver invoking the same frozen harness,
counter bytes and pinned populations with the same kill rule; the two arms' numbers therefore reproduce as the sum of
their cells, not as a single-process transcript.

## 2. The two new rows and alternate single edits of their clauses

Method: one substitution applied to a scratch copy of the frozen counter (asserted to occur exactly once), scored on
both pinned populations through the frozen harness. Variant files `variants.json` / `variants2.json`; variant sha256s
are in the `VARIANT` lines of `probes2.txt` / `probes3.txt` and every `RUN` line carries the cell.

| edit (single) | clause | killed r87 | killed r88 | classification | row that would bind it |
|---|---|---|---|---|---|
| `m17-filed`: drop `r[0] in ledger` | `_ledger` duplicate id | no | **yes** (`LD1`) | filed mutant; `LD1` load-bearing | — |
| `m17b`: refuse a duplicate only when the target repeats (`ledger[r[0]][1] == r[2]`) | `_ledger` duplicate id | **no** | **no** | **SURVIVOR — `LD1` binds only the target-equal spelling** | `LD1b`: a duplicate `P01` whose target differs from the frozen `-` |
| `m17c`: drop the `len(r) < 3` half | `_ledger` malformed row | **no** | **no** | **SURVIVOR — the sibling half is unrowed** | `LD2`: a `where=ledger` row appending a 2-column row |
| `m17d`: refuse only when class **and** target repeat (`ledger[r[0]] == (r[1], r[2])`) | `_ledger` duplicate id | no | **yes** (`LD1`) | killed — `LD1`'s duplicate differs in class | — |
| `m18-filed`: `before_ok = True` | `_whole` before byte | no | **yes** (`NF6g`) | filed mutant; `NF6g` load-bearing | — |
| `m18b`: before guard narrowed to letters+digits (`not line[i-1:i].isalnum()`) | `_whole` before byte | **no** | **no** | **SURVIVOR — `NF6g` binds only the alnum predecessor** | `NF6h`: declaration naming the token after `/` |
| `m18c`: before guard narrowed to `/` (`!= b"/"`) | `_whole` before byte | no | **yes** (`NF6g`) | killed — the row refuses a `/`-only guard | — |
| `m18d`: only the first occurrence examined (`i = line.find(needle, i + 1)` → `i = -1`) | `_whole` search loop | **no** | **no** | **SURVIVOR — the multi-occurrence leg is unrowed** | `NF6i`: a line whose first token occurrence is a non-whole suffix and a later one is whole |

The `_whole` pair is the finding: `m18b` (refuse letters, accept `/`) **passes** `NF6g`; `m18c` (refuse `/`, accept
letters) **fails** it. `NF6g`'s predecessor is `x`, so the row only asks whether an *alphanumeric* predecessor is
refused.

## 3. NF6g: which spelling of the before-byte half does the row bind?

Direct measurement of `_whole` imported from a scratch copy of the frozen counter, one declaration line
`- <prefix><TOKEN>; slot <TARGET>.` (TOKEN = the L06 token; TARGET = the R11 quarantine leaf):

```
before=line-start pristine=True  m18b-alnum-only=True
before=tab        pristine=True  m18b-alnum-only=True
before=space      pristine=True  m18b-alnum-only=True
before=slash      pristine=False m18b-alnum-only=True
before=dot        pristine=False m18b-alnum-only=True
before=underscore pristine=False m18b-alnum-only=True
before=dash       pristine=False m18b-alnum-only=True
before=at         pristine=False m18b-alnum-only=True
before=plus       pristine=False m18b-alnum-only=True
before=tilde      pristine=False m18b-alnum-only=True
before=alnum      pristine=False m18b-alnum-only=False
PATHCH = b'+-./0123456789@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~'
```

Pristine refuses **all eight** PATHCH predecessor classes (alnum, `/`, `.`, `_`, `-`, `@`, `+`, `~`) and accepts line
start, tab, space. `m18b` flips **seven of the eight** and keeps only the alnum class. The filed R11 declaration
precedes the L06 token with `x` (alnum), so `m18b` refuses the row and survives both sets.

Row-level counterfactual (scratch copy of the harness, one fixture line changed: `xtests/` → `vendor/tests/`, i.e.
the token preceded by `/`; counter bytes and population pins untouched; harness sha `c34057b4…`):

```
CF nf6g-slash  pristine          summary=('53','0','0','0','0') exit=0
CF nf6g-slash  m18-filed         summary=('53','1','1','0','0') exit=1 red=ROW NF6g … got=QUARANTINED match=no
CF nf6g-slash  m18b-alnum-only   summary=('53','1','1','0','0') exit=1 red=ROW NF6g … got=QUARANTINED match=no
```

So a declaration with a `/` predecessor binds `m18b`; the filed `x` declaration does not. **`NF6g` binds one
predecessor class (alnum); the other seven PATHCH classes are unrowed.** Answering the shape question directly: token
at line start or after a tab makes `_whole` true, which makes the declaration true (the row would resolve
QUARANTINED and go red), so those shapes destroy the row's falsity rather than bind the clause. For each of the eight
PATHCH predecessors `_whole` is false, so the row stays false; of those, only the alnum one discriminates a narrowed
guard (the `/` case is measured at row level by the counterfactual above; the other six are function-level only — a
row-level test per class would need one fixture revision per class).

## 4. LD1: which duplicate does the row refuse?

The frozen counter run directly with hand-built ledgers over the frozen r77 population (frozen ledger + one appended
row; `--rev` = BASE `e65538e7`):

```
CASE dup_same_class_same_target   cols=4 rc=1 markers=['LEDGER-REFUSED id=P01 why=unknown or duplicate id'] refused=1
CASE dup_same_class_diff_target   cols=4 rc=1 markers=['LEDGER-REFUSED id=P01 why=unknown or duplicate id'] refused=1
CASE dup_diff_class_same_target   cols=4 rc=1 markers=['LEDGER-REFUSED id=P01 why=unknown or duplicate id'] refused=1
CASE dup_diff_class_diff_target   cols=4 rc=1 markers=['LEDGER-REFUSED id=P01 why=unknown or duplicate id'] refused=1
CASE dup_row_2col                 cols=2 rc=1 markers=['LEDGER-REFUSED id=P02 why=unknown or duplicate id'] refused=1
CASE newid_2col_malformed         cols=2 rc=1 markers=['LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id'] refused=1
CASE newid_3col                   cols=3 rc=1 markers=['LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id'] refused=1
CASE dup_3col                     cols=3 rc=1 markers=['LEDGER-REFUSED id=P01 why=unknown or duplicate id'] refused=1
CASE dup_3col_p02                 cols=3 rc=1 markers=['LEDGER-REFUSED id=P02 why=unknown or duplicate id'] refused=1
CASE dup_1col                     cols=1 rc=1 markers=['LEDGER-REFUSED id=P09 why=unknown or duplicate id'] refused=1
```

- A duplicate id with the **same class and same target** still fails closed (`LEDGER-REFUSED`, exit 1). So does every
  other duplicate combination: the pristine refusal is class- and target-blind.
- A **2-column row** (malformed), a **3-column duplicate**, a **3-column unknown id** and a **1-column row** all print
  the identical `LEDGER-REFUSED id=… why=unknown or duplicate id` line and exit 1. A 3-column row is *not* malformed
  (`len(r) < 3` fails); it takes the duplicate leg when the id repeats and the unknown-id leg when it is new — the same
  output path either way.

The filed `LD1` duplicate is `P01  ABSENT  -`: different **class** (`FLEET`→`ABSENT`), same **target** (`-`).
Therefore `m17b` (duplicate refused only when the target repeats) **survives** the filed row while `m17d` (class
**and** target equality) is **killed**, and the counterfactual `ld1-diff-target` (harness copy appends
`P01 ABSENT census/nowhere/…`) turns `m17b` red:

```
CF ld1-diff-target  pristine          summary=('53','0','0','0','0') exit=0
CF ld1-diff-target  m17-filed         summary=('53','1','0','0','0') exit=1 red=ROW LD1 … got=- match=no
CF ld1-diff-target  m17b-same-target  summary=('53','1','0','0','0') exit=1 red=ROW LD1 … got=- match=no
```

**`LD1` binds one spelling too**: an id-only duplicate whose target happens to repeat. A class/target-pair-keyed
reader survives the filed row.

## 5. The four carried survivors on the r88 population

| carried clause | probe (single edit) | killed r87 | killed r88 | verdict |
|---|---|---|---|---|
| p2 basename granularity | token-on-line guard at basename (`token.rsplit("/",1)[-1] in line`) | no | **no** | SURVIVED — still unrowed, as the prereg's limits name |
| p3 punctuation lookahead | `.`-member kept, `after[1] not in PATHCH` lookahead dropped | no | **no** | SURVIVED — still unrowed, as named |
| p7 `_regular` symlink leg | mode whitelist dropped (`typ == b"blob"` only) | no | **no** | SURVIVED — still unrowed, as named |
| p8 `token_ok` hyphen marker | `">\\-"` → `">\\"` | no | **no** | SURVIVED — still unrowed, as named |

All four are named in the prereg's stated limits, so none is a new HIGH finding: the r88 population still proves
nothing about them. (Byte-level check: `m16` is still killed by `TQ1`; `p3` does not become bound by `NF6g` because
`NF6g`'s token is preceded by a path byte and its target's `.` sits at line end.)

## 6. Other reachable-but-unrowed probes

| probe | edit (single) | killed r87 | killed r88 | classification | row that would bind it |
|---|---|---|---|---|---|
| `x2` fleet symlink leg | `_regular`'s `fleet:` branch drops `not os.path.islink(p)` | **no** | **no** | SURVIVOR — second spelling of carried p7 | a TOKEN row whose target is `fleet:<a symlink>` |
| `x9` class enum | drop `cls not in CLASSES` in `judge` (byte-identical to filed `m11`) | yes (`NF-S`) | yes (`NF-S`) | control — agrees with the filed matrix | — |
| `x1` punctuation members | `after[:1] in (b".", b",", b";", b":")` → `(b".",)` | no | no | EQUIVALENT mutant (see below), not a coverage gap | none — no row can bind a no-op |
| `m19` `_capture_ok` len half | drop `len(want) <= len(have)` | no | no | belt, as the prereg records | — |

`x1` is an **equivalent mutant**: the disjunct is evaluated only when `after[0] ∈ PATHCH`, and `,` `;` `:` are not
PATHCH bytes (the first disjunct `after[0] not in PATHCH` already accepts them). Only the `.` member is live, and
`TQ1` binds it. The `,` `;` `:` members are dead code, not an unrowed clause.

## 7. Findings for the L1 (no claim wording changed by this seat)

**F1 — HIGH, C1 binding gap (`NF6g`).** `NF6g`'s predecessor is `x` (alnum), so the row binds **one** predecessor
class. `m18b` (the before-guard narrowed to alphanumerics — the classic word-boundary spelling, a single edit of the
same line) survives both pinned populations (`r87 m=0 e=0 rc=0`, `r88 m=0 e=0 rc=0`) while the filed `m18` is killed.
Direct `_whole` measurement: pristine refuses 8/8 PATHCH classes, `m18b` flips 7/8 and keeps only alnum; the
`/`-predecessor counterfactual turns `m18b` red. The C1 wording says the binding is "the `_whole` before-byte half";
measured, it is the alnum spelling of that half. The prereg's limits name "not every declaration shape", not this
narrowing, so this is a survivor the limits do not carry.
**Row that binds it:** `NF6h` (fixture revision R11b): a `QUARANTINED`/`REFUSED` false row for L06 whose declaration
is `- retired copy: vendor/tests/vault/vadv54-run/p/p6repo/.git; quarantine slot <q6>slash-stub.` — the token
preceded by `/` — plus the disk-only `slash-stub` leaf. Measured: pristine green, `m18` red, `m18b` red.

**F2 — HIGH, C1 binding gap (`LD1`).** The filed duplicate is class-different (`FLEET`→`ABSENT`) but target-equal
(`-`). `m17b` (duplicate refused only when the target repeats) survives both sets (`r87 rc=0`, `r88 rc=0`) while
`m17d` (class+target equality) is killed; the different-target counterfactual turns `m17b` red. So `LD1` binds an
id-only duplicate whose target happens to repeat, not the duplicate-id refusal as a class/target-blind rule. The
limits do not name this narrowing.
**Row that binds it:** `LD1b` (`where=ledger`, item `P01`) whose harness append is
`P01\tABSENT\tcensus/nowhere/ld1b\t<note>` — same row type as `LD1`, only the appended target differs. Measured:
pristine green, `m17` red, `m17b` red.

**F3 — MEDIUM, unrowed sibling half.** The `_ledger` malformed guard `len(r) < 3` is unrowed: `m17c` drops it and
survives both sets. Direct probes: a 2-column row is refused through that leg with the same marker and exit 1, and
the mutant then raises `IndexError` (fail-closed by crash, not by the refusal). **Row that binds it:** `LD2`
(`where=ledger`, item `P02`) whose harness append is a 2-column `P02\tABSENT`; pristine prints
`LEDGER-REFUSED id=P02` / exit 1, `m17c` prints no marker → red. Not named in the limits.

**F4 — MEDIUM, unrowed search leg.** `_whole`'s occurrence loop is unrowed: `m18d` (only the first occurrence is
examined) survives both sets. **Row that binds it:** `NF6i`, a true `QUARANTINED` row whose declaration line carries
the token twice — first as a suffix of a longer path, later whole. Not named in the limits.

**F5 — LOW, carried-family spelling.** `_regular`'s `fleet:` symlink leg: `x2` survives both. This is the same
clause as carried p7 (a member must be a regular non-symlink file), different spelling; p7 is named in the limits, so
this stays a carried spelling rather than a new clause.

**F6 — INFO, dead code.** `_whole`'s punctuation disjunct keeps `,` `;` `:` members that are unreachable (only `.`
is in `PATHCH`); `x1` is an equivalent mutant, so no row can bind them. `TQ1` binds the live `.` member. Not a
coverage gap; a comment-level cleanup at most.

**F7 — INFO, `LD1`'s marker is ambiguous.** `LEDGER-REFUSED id=… why=unknown or duplicate id` is emitted by three
different legs (malformed `len(r) < 3`, duplicate id, unknown id), and the harness asserts only the prefix plus
`rc == 1`. The filed `LD1` append is 4-column, so only the duplicate leg can fire today, but a counter that refused
the same id for another reason would pass the row. If the reason is to be bound, the marker must distinguish the legs
(counter change, out of this round's scope).

**Positive results.** Both new rows are load-bearing on the 53-row population and their kills are the entire delta
(§1b); the twelve-mutant matrix reproduces `killed_r87=10 / killed_r88=12` cell for cell; the belt (`m19`) survives
both sets; the four carried survivors stay unrowed exactly as the limits say.

## 8. Restoration and scratch

Every edit was applied to a scratch copy; the lane counter was never modified. Re-hash after the runs:
`census/round-87/c1-pointer-counter.py` = `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b` (the
pin, unchanged). Scratch root `/fast/scratch/hyaku/souji-r88/S88MutCounter/` is removed before yield; the driver
scripts, variant files, run logs, `_whole` table, ledger table and the two counterfactual harness diffs are copied to
`.ufo/waves/round-88/w1/S88MutCounter/`.
