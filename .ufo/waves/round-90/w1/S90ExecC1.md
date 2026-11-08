# S90ExecC1 — C1 independent re-derivation (souji r90 w1)

Seat: S90ExecC1 (executor, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Lane HEAD measured: `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (F, the preregistration alone — `git show --stat` = 1 file, 150 insertions).
Instrument provenance: P1 `1952c1c7` (population/harness/battery/mutants), P2 `e2a11c73` (control receipts).
Scratch: /fast/scratch/hyaku/souji-r90/S90ExecC1 (deleted before yield; receipts copied to ./receipts/).

## 0. Verdict

(to be completed with the two battery SUMMARY lines)

## 1. Pin table — battery-printed vs prereg

Pins as PRINTED by the battery header (`# counter path=...` etc.) and as independently hashed by me:

| instrument | prereg pin | measured sha256 | rows | match |
|---|---|---|---|---|
| census/round-87/c1-pointer-counter.py | fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b | same | – | yes |
| census/round-90/c1-clause-battery.py | e7265335e4458e68d2277dd0ad4f36e68999a7ba70363d60dc2155bd9cfa2d39 | same (self, sha256sum) | – | yes |
| census/round-90/c1-false-row-harness.py | c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe | same (battery header + sha256sum) | – | yes |
| census/round-90/c1-mutants.json | 392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5 | same | 16 members | yes |
| census/round-90/c1-false-rows.tsv | d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45 | same | 58 | yes |
| census/round-89/c1-false-rows.tsv (control pop) | 04570a64… (battery PINS/COPY pin) | 04570a64855978bf697af71c161fe215945da5849f2f393fee15bb0d9f21e093 | 57 | yes |
| census/round-77/c2-pointer-ledger.tsv (frozen ledger) | "frozen r77 ledger" | 011faa0e96333b28af0418df8f56a5cbb169ed71aa0e9f688ee6d97d7aa39ba5 | 31 ids + header | ids used |

No pin mismatch found.

Two precision notes (neither is a mismatch to a stated number):
- The prereg says the r90 mutant file is "(…; the r89 sixteen byte-identical)". The FILE is not byte-identical
  (r89 sha bc7e6bb1…, r90 sha 39252248…; they differ only in the top-level `note` field, char 20). The sixteen
  MEMBERS are identical: same ids in the same order and `json.dumps(members, sort_keys=True)` hashes equal
  (1a93a7b6…) for both files. The claim's parenthetical is about the sixteen mutants, so this is consistent, but
  "byte-identical" is true of the members, not of the file.
- r90 battery diff vs r89 battery: docstring + PINS only (r89 path retargeted to census/round-89 at the same sha,
  one r90 entry added; the r89 file used to live at `HERE`). r90 harness diff vs r89 harness: docstring + POP_PINS
  entry + `elif rid in ("LD2", "LD2b")` (the r89 branch was `rid == "LD2"`). No judgement/exit/summary code changed.

## 2. Population diff — r89 vs r90

- `cmp census/round-89/c1-false-rows.tsv census/round-90/c1-false-rows.tsv` → `EOF on …r89… after byte 14187` (exit 1: r89 is a strict prefix).
- prefix check: `head -c 14187 census/round-90/c1-false-rows.tsv | sha256sum` = 04570a64855978bf697af71c161fe215945da5849f2f393fee15bb0d9f21e093 = the r89 file's sha256. Byte-for-byte, in order.
- sizes: r89 14187 B / 59 physical lines (2 `#` comment lines + 57 data rows); r90 14628 B / 60 physical lines (58 data rows). Appended bytes = 441, exactly one line, ending in `\n`; r89 already ended in `\n` (tail hexdump …`6f72 2e0a`).
- appended line = `LD2b\tledger\tBASE\tr77\tZZ9\t-\t-\tLEDGER-REFUSED\t1\t<source>` (10 columns).
- parsed: r90 has 58 rows, 58 unique ids, all rows exactly 10 columns; `r90_rows[:57] == r89_rows` (Python list equality) = True.
- The only differing line is the appended 58th, LD2b. `ZZ9` does not occur in the frozen r77 ledger (`grep -c '^ZZ9'` → 0, exit 1), so the appended harness row lands on an id ABSENT from the ledger.

## 3. LD2b by hand — counter level (exactly the harness's ledger-row invocation)

Replicated the harness branch for `where=ledger`: `dup = r77 ledger bytes (+'\n' if absent) + "ZZ9\tABSENT\n"`,
then `counter --root <lane> --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root /home/vgpnk/Projects/shokunin
--population census/round-77/c2-population.tsv --ledger dup`, cwd=lane. Mutant texts produced in scratch from
c1-mutants.json with `src.count(old) == 1` asserted.

| counter | rc | stdout marker | stderr | row verdict |
|---|---|---|---|---|
| pristine | 1 | `LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id`; SUMMARY items=35 resolved=35 refused=1 | empty | green (expect LEDGER-REFUSED/1) |
| m17-duplicate-id | 1 | same marker; SUMMARY refused=1 | empty | green |
| m17b-target-keyed | 1 | same marker; SUMMARY refused=1 | empty | green |
| m17c-no-malformed | 1 | NO stdout at all (crash inside `_ledger`, before the header prints) | `File ".../counter-m17c.py", line 494, in _ledger / ledger[r[0]] = (r[1], r[2]) / IndexError: list index out of range` | RED (got `-` vs expect `LEDGER-REFUSED`) |

All 16 member edits apply exactly once (`src.count(old)` = 1 each; verified for every id).

Contrast that proves LD2b is the load-bearing shape: the r89 LD2 row (`P02`, present in the frozen ledger) driven
under m17c is still REFUSED via the duplicate leg — m17c prints `LEDGER-REFUSED id=P02` and rc=1, so LD2 does not
score it red. ZZ9's absence is what removes the duplicate leg and exposes `len(r) < 3`.
(`receipts/ld2-contrast.txt`, `receipts/ld2b-handdrive-counter.out.txt`.)

## 4. LD2b by hand — harness level (census/round-90/c1-false-row-harness.py, r90 population)

Four full harness runs, fresh work dirs, `--population census/round-90/c1-false-rows.tsv`.

| counter | ROW LD1 | ROW LD1b | ROW LD2 | ROW LD2b | harness SUMMARY | exit |
|---|---|---|---|---|---|---|
| pristine | yes | yes | yes | yes | rows=58 mismatches=0 accepted=0 refused_true=0 errors=0 | 0 |
| m17-duplicate-id | NO | NO | yes | yes | rows=58 mismatches=2 … | 1 |
| m17b-target-keyed | yes | NO | yes | yes | rows=58 mismatches=1 … | 1 |
| m17c-no-malformed | yes | yes | yes | **NO** | rows=58 mismatches=1 … | 1 |

The m17c mismatch is exactly one row and it is `LD2b` (`got=- rc=1 match=no`): LD2b is the sole killer of m17c.
m17 and m17b each stay green on LD2b (they are killed elsewhere, by LD1/LD1b), so the attribution table names LD2b
and only LD2b for the malformed-guard clause.

## 5. Battery arms

(pending — command, SUMMARY lines, exits)
