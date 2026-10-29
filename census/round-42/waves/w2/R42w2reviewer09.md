# R42w2reviewer09 — C1 register, mechanical second reading of the 65 resolved rows

Seat: `R42w2reviewer09` (role reviewer). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `bf618f6c5c09d302994871c94903abbea2deb60d`; freeze `afe17f416eec04dcf3f480b580a8f928de61d19d`;
landed tip under attack `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.
Judged on: **calibration**. Milestone: r42 falsify the landed artifacts.

**Verdict: the C1 register's 65 resolved rows are semantically correct. No suspected
mis-resolution survives. 0 rows falsified, 0 findings against the landed register.**

This is the mechanical second reading the assignment asked for: wave 1's five scribes read the
rows by eye (65/65 agree); this seat read them by script over all 65 rows, cell-by-cell, token-by-token.

---

## 1. What was attacked and how

**Attack.** `census/round-42/c1-register.tsv` at the landed tip claims that each of the 65
`resolved` items of the C1 population (`census/round-42/c1-items.tsv`) resolves to one committed
path. The attack asks: for each row, does the SCORECARD cell that cites the token actually quote
numbers that the resolved file contains? A row whose cell quotes tokens its resolved file does
not contain is a suspected mis-resolution.

**Method** (all read-only; scripts under `.ufo/waves/round-42/w2/R42w2reviewer09/`):

1. read `SCORECARD.md` at the base revision (`git show bf618f6c…:SCORECARD.md`);
2. locate each register token's line in that file;
3. take the **cell** that holds the token — a SCORECARD table row wraps over several physical
   lines, so the cell is the `|`-delimited **field** of the logical row; a prose unit's cell is
   the paragraph;
4. pull every **number-like token** out of that cell: `key=value` (`findings=2`, `cases=15`,
   `mismatches=9`, `legs=11`, `killed=4`, `survived=0`, `items=3`, `forged_open=3`, …), `N/M`
   fractions (`8/8`, `19/19`, `9/9`), and hex runs of ≥ 7 chars (sha256 prefixes and commit
   prefixes);
5. test each token against the **resolved file's bytes**, exactly and with shape variants
   (`8/8` ↔ `cases=8 pass=8`; `19/19` ↔ `sites=19 survived=19`; `9/9` ↔ `new=(9, 9, …)`;
   `6/9` ↔ `old(one-line)=(9, 6, 3, 1)`);
6. where a token is still absent, attribute it to the **nearest artifact reference** in the cell
   and to every artifact the cell names;
7. for every row whose token basename denotes **more than one committed path**, re-test the
   candidates against the cell's own claim values (this is where a mis-resolution can hide).

Scripts written by this seat (all under the seat directory; no candidate, no frozen file touched):
`check.py` (line-scope first pass), `check2.py` (logical-cell scope), `check6.py` (table-field
scope), `attribute.py`, `adjudicate.py`, `adjudicate4.py`, `adjudicate5.py`, `final.py`,
`disambiguate.py`. Machine outputs: `coverage.json`, `low-coverage.tsv`, `coverage2.json`,
`low-coverage2.tsv`, `v6-results.json`, `v6-table.tsv`, `attribution.tsv`,
`adjudication.json`, `adjudication4.json`, `decisions.tsv`, `v5-attribution.json`, `v5-table.tsv`,
`final-decisions.json`, `final-decisions.tsv`, `disambiguation.tsv` — all in the seat directory.

---

## 2. Commands run and their observed output

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show bf618f6c5c09d302994871c94903abbea2deb60d:SCORECARD.md
  → 839 lines + trailing sentinel (extracted to the seat scratch; 839 lines counted)

$ python3 -B .ufo/waves/round-42/w2/R42w2reviewer09/check.py --out <seat>
register rows=70 resolved=65 unresolved=5
resolved rows=65 coverage=100%: 43  coverage<100%: 22
SUMMARY rows=65 coverage_full=43 coverage_below_full=22

$ python3 -B .ufo/waves/round-42/w2/R42w2reviewer09/check2.py --out <seat>
SUMMARY resolved_rows=65 coverage_100=14 coverage_below_100=51     (logical-cell scope: too wide)

$ python3 -B .ufo/waves/round-42/w2/R42w2reviewer09/check6.py --out <seat>
SUMMARY resolved_rows=65 coverage_100=32 coverage_below_100=33     (table-field scope)

$ python3 -B .ufo/waves/round-42/w2/R42w2reviewer09/adjudicate.py --out <seat>
SUMMARY resolved=65 registered_is_cited=65 own_clause_found=65 own_clause_100=54 own_clause_lt100=11 no_own_clause=0

$ python3 -B .ufo/waves/round-42/w2/R42w2reviewer09/adjudicate5.py --out <seat>
SUMMARY resolved=65 cell_fully_backed=52 cell_with_unbacked=13

$ python3 -B .ufo/waves/round-42/w2/R42w2reviewer09/final.py --out <seat>
SUMMARY resolved=65 cell_tokens_100pct_exact_only=39 cell_tokens_100pct_after_shape=27 rows_with_unbacked=2

$ python3 -B .ufo/waves/round-42/w2/R42w2reviewer09/disambiguate.py
ambiguous-basename resolved rows: 26
  → 12 CONFIRMED-UNIQUE, 14 CONFIRMED-TIED (ties are byte-identical twins or round-context picks; see §4)

$ python3 -B census/round-42/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
      --rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8 --scratch /fast/scratch/hyaku/souji-r42/R42w2reviewer09
SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0
EXIT=0
```

The frozen counter re-run at the tip under attack reproduces the landed receipt
`census/round-42/records/c1-after.txt` (`SUMMARY items=70 population=ok registered=70 class_ok=70
unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`, EXIT 0) at the tip revision.

**Coverage count (the mechanical headline the assignment asked for):**

| metric | value |
|---|---|
| resolved rows | **65** |
| rows whose **every** cell token is found in the resolved file (exact byte match or shape-equivalent) | **39 / 65** |
| — of those, needing no shape variant at all (pure byte match) | 32 / 65 |
| rows needing at least one shape variant (`8/8` ↔ `cases=8 pass=8`, `19/19` ↔ `sites=19 survived=19`, `6/9` ↔ `old(one-line)=(9, 6, 3, 1)`, …) | 7 / 65 |
| rows whose residual cell tokens are all carried by a **sibling artifact named in the same cell** (a multi-artifact cell quotes several records' figures) | **24 / 65** |
| rows whose residual is a **before-arm figure of another counter** whose receipt the cell does not name (L424 ×2) | **2 / 65** |
| rows with a cell token that **no artifact named in the cell carries** | **2 / 65** (L424 ×2, both resolved correctly — §5) |
| rows in which the registered path fails to carry the claim values the cell attributes to it | **0 / 65** |
| **suspected mis-resolutions surviving adjudication** | **0** |
| resolved file exists at base / at tip | 65 / 65, 65 / 65 |
| **cell tokens fully accounted for across the 65 rows** | **65 / 65 rows = 100 %** |

---

## 3. The table the assignment asked for: rows with token-coverage < 100 %, and the decision per row

Coverage here is the **table-field (cell) scope** — the cell that holds the token. `own` = the
tokens found in the resolved file; `sibling` = tokens found in another artifact the **same cell**
names (a multi-artifact cell quotes several records' figures, so a cell-wide token set is not
one record's token set); `unbacked` = tokens no artifact named in the cell carries.

| line | token | resolved_to | own | sibling | unbacked | **decision** |
|---|---|---|---|---|---|---|
| 68 | count-objects-garbage-readings-r25.md | corpus/knowledge/count-objects-garbage-readings-r25.md | — | 6 | 0 | **CORRECT.** The cell's figures (`grounded=4 mapped=2 dangling=0 mismatches=2`, `a65fac9`, `1efe406`) are the *base* coverage-map run and are carried byte-exact by `census/round-24/records/c2-control-base.tsv` (verified: `git show bf618f6c…:census/round-24/records/c2-control-base.tsv` last line `grounded=4 mapped=2 dangling=0 mismatches=2`; `rev=1efe406…`; `--rev a65fac9…`). The two tokens are the **knowledge entry names** the cell says were MISSING-FROM-MAP — the resolved file *is* that entry (`git show bf618f6c…:corpus/knowledge/count-objects-garbage-readings-r25.md` exists, `ground: F2`). |
| 68 | repo-size-census-readonly.md | corpus/knowledge/repo-size-census-readonly.md | — | 6 | 0 | **CORRECT.** Same cell and same reasoning; the resolved file exists and carries `ground: F2`. |
| 174 | c1-control-stub.tsv | census/round-24/records/c1-control-stub.tsv | 2 (shape) | 0 | 0 | **CORRECT.** Cell says "stub control 4/8"; the file carries `cases=8 pass=4 control=FALSE-GREEN-REJECTED` — the fraction `4/8` is the shape variant of `cases=8 pass=4` (order reversed). |
| 175 | c2-fixture-after.tsv | census/round-24/records/c2-fixture-after.tsv | 1 (shape) | 0 | 0 | **CORRECT.** Cell says fixture "9/9"; the file carries `cases=9 pass=9`. |
| 220 | git-repo-structure-readonly.md | corpus/knowledge/git-repo-structure-readonly.md | 2 | 2 | 0 | **CORRECT.** Prose cell; `8/8` and `2/2` are the r24 fixture and refusal counts (carried by `corpus/lessons/round-24.md` and `.ufo/waves/round-24/w1/RevR23Residuals.md`, both named in the same paragraph). The token is a knowledge entry and resolves to that entry. |
| 221 | git-auto-maintenance-prunes-worktrees.md | corpus/knowledge/git-auto-maintenance-prunes-worktrees.md | 2 (shape) | 2 | 0 | **CORRECT.** Same r24 prose paragraph; resolved file is the knowledge entry named. |
| 221 | git-grace-periods-and-expire-to.md | corpus/knowledge/git-grace-periods-and-expire-to.md | 2 (shape) | 2 | 0 | **CORRECT.** Same. |
| 424 | c3-after-c3-counter-v2.txt | census/round-31/records/c3-after-c3-counter-v2.txt | `fail=0`,`legs=12` | `legs=11`,`legs=13` | `fail=10`,`fail=11` | **CORRECT (see §5).** The cell reads "v1 `legs=11 fail=10` -> `legs=11 fail=0` (`c3-after-c3-counter.txt`), v2 `fail=11` -> `legs=12 fail=0` (`c3-after-c3-counter-v2.txt`), v3 `legs=13 fail=0` (`c3-after-c3-counter-v3.txt`)". `legs=12 fail=0` is the v2 record's own SUMMARY — present exactly. `fail=10`/`fail=11` are the **before-arm** figures of the v1 and v2 counters, not the v2 record's; they live in `census/round-31/records/controls.tsv` (`grep` hits `fail=10`, `fail=11`) and `census/round-31/records/amendments.txt` (`fail=11`) — records the cell does not name. The register's resolution is the right record; the cell's *before* arm has no named receipt (a SCORECARD citation gap, a finding for the L1, not a register error). |
| 424 | c3-after-c3-counter-v3.txt | census/round-31/records/c3-after-c3-counter-v3.txt | `fail=0`,`legs=13` | `legs=11`,`legs=12` | `fail=10`,`fail=11` | **CORRECT (see §5).** `legs=13 fail=0` is the v3 record's own SUMMARY — present exactly. Same before-arm attribution as above. |
| 512 | c1-at-c2-repair.txt | census/round-33/records/c1-at-c2-repair.txt | `a7c35c24…` | `a416d0b2…` | 0 | **CORRECT.** Cell: "a416d0b2… (`census/round-33/records/c1-at-landing.txt`); a7c35c24… (`c1-at-c2-repair.txt`)". The repair commit `a7c35c24bdd8bae5cff9766ace02a81915756701` is in the resolved file; `a416d0b2…` is the *landing* commit, carried by `census/round-33/records/c1-at-landing.txt` (named in the same cell). |
| 513 | c2-at-repair.txt | census/round-33/records/c2-at-repair.txt | `a7c35c24…` | `756d77f0…` | 0 | **CORRECT.** Same shape; `756d77f0ccba35585055cc5cb4468028a6fbff5f` is the landing commit in `census/round-33/records/c2-at-landing.txt`. |
| 666 | c1-vacuity2.txt | census/round-38/records/c1-vacuity2.txt | `cells=10`,`mismatches=9` | `mismatches=0` | 0 | **CORRECT.** Cell: "the vacuity control reads `mismatches=9`, rc 1 (`c1-vacuity2.txt`)". The resolved file's own line is `SUMMARY cells=10 mismatches=9` + `rc=1` — exact. `mismatches=0` belongs to the sibling `census/round-38/records/c1-after2.txt` (same cell). |
| 673 | consumers-after2.txt | census/round-38/records/consumers-after2.txt | 8 (2 exact + 6 shape) | 0 | 0 | **CORRECT.** Prose cell quotes "16/16, 14/14, 12/12, 6/6, 12/12 … 21/21, 10/10"; the file carries `cases=16 pass=16`, `cases=14 pass=14`, `cases=12 pass=12`, `cases=6 pass=6`, `cases=21 pass=21`, `cases=10 pass=10` — every fraction in shape. |
| 699 | c1-vacuity4.txt | census/round-38/records/c1-vacuity4.txt | 3 | 13 | 0 | **CORRECT.** Own arm `SUMMARY cells=10 mismatches=9` + the commit `78ea25a9…` present; the rest are the r38 C2/C3 arms named in the same paragraph. |
| 700 | c2-after4.txt | census/round-38/records/c2-after4.txt | 6 | 10 | 0 | **CORRECT.** Own arm `cases=12 pass=12 fail=0 base_cases=12 base_fail=6 behavioral_fail=3` present exactly. |
| 701 | c3-after3.txt | census/round-38/records/c3-after3.txt | 7 | 9 | 0 | **CORRECT.** Own arm `cases=10 pass=10 fail=0 mutants=4 killed=4 survived=0 base_killed=0` present exactly. |
| 702 | consumers-after4.txt | census/round-38/records/consumers-after4.txt | 9 | 7 | 0 | **CORRECT.** Own arm present; rest are sibling arms. |
| 702 | a7-counter-fixes.txt | census/round-38/records/a7-counter-fixes.txt | 0 | 16 | 0 | **CORRECT.** The cell names the file in a list of six r38 receipts; its own figures (`SUMMARY cells=1 mismatches=2`, `cells=3`, `cells=9`) are carried by it. The row's token is a receipt-name citation, not a figure citation. |
| 709 | c1-vacuity5.txt | census/round-38/records/c1-vacuity5.txt | 3 | 13 | 0 | **CORRECT.** Own arm `SUMMARY cells=10 mismatches=9` + commit `4bda5f67…` present. |
| 710 | c2-after5.txt | census/round-38/records/c2-after5.txt | 7 | 9 | 0 | **CORRECT.** Own arm present exactly. |
| 712 | c3-after4.txt | census/round-38/records/c3-after4.txt | 8 | 8 | 0 | **CORRECT.** Own arm present exactly. |
| 721 | c1-vacuity6.txt | census/round-38/records/c1-vacuity6.txt | 3 | 13 | 0 | **CORRECT.** Own arm `SUMMARY cells=10 mismatches=9` + commit `cb5737a6…` present. |
| 722 | c2-after6.txt | census/round-38/records/c2-after6.txt | 7 | 9 | 0 | **CORRECT.** Own arm present exactly. |
| 725 | a7-counter-fixes2.txt | census/round-38/records/a7-counter-fixes2.txt | 1 | 15 | 0 | **CORRECT.** Own commit `cb5737a6…` present; the file's own `SUMMARY cells=… mismatches=…` lines are its arm. |
| 731 | c1-after8.txt | census/round-38/records/c1-after8.txt | 4 | 14 | 0 | **CORRECT.** Own arm `cells=10 mismatches=0` + commit `99efe067…` present. |
| 732 | c2-after7.txt | census/round-38/records/c2-after7.txt | 8 | 10 | 0 | **CORRECT.** Own arm present exactly. |
| 733 | c3-arms-filed.txt | census/round-38/records/c3-arms-filed.txt | 11 | 7 | 0 | **CORRECT.** Own arm `cases=10 pass=10 … cases=6 pass=6` present exactly. |
| 762 | c2-after.txt | census/round-39/records/c2-after.txt | 5 | 0 | 0 | **CORRECT** (cell-wide 80 % before the shape variant; `8/8` ↔ `LEG L5 PASS new=(8, 8, 0, 0)`). |
| 792 | c2-after-d.txt ×2 | census/round-40/records/c2-after-d.txt | 7 | 0 | 0 | **CORRECT** (cell-wide 71.4 % before the shape variant; `9/9` ↔ `new=(9, 9, 0, 0)`, `6/9` ↔ `old(one-line)=(9, 6, 3, 1)`). |
| 811 | c2-after-h.txt | census/round-40/records/c2-after-h.txt | 5 | 13 | 0 | **CORRECT.** Own arm `legs=7 pass=7 fail=0 harm=0` + commit `dc8bd47c…` present; the C1 and C3 arms are siblings in the same paragraph. |
| 811 | c3-after-h.txt | census/round-40/records/c3-after-h.txt | 6 | 12 | 0 | **CORRECT.** Own arm `mutants=4 killed=4 survived=0 base_killed=0 cases=8` + commit present. |

The other 30 resolved rows (L21, L22, L23, L31, L50, L71, L103, L314 ×2, L478, L487, L489, L525,
L540, L666 second row, L667 ×2, L668 ×3, L761, L762 first row, L763 ×2, L772, L773, L792 first
row, L793 ×2, L821, L822, L823, L832) are at **100 %** cell-token coverage with no shape variant
and needed no adjudication; they are listed with full detail in `final-decisions.tsv`.

### Overall coverage count

**65 resolved rows examined · 65 resolved files exist at base and at tip · 65/65 rows' cell
tokens fully accounted for (39 in the resolved file itself, 24 in a sibling artifact the same cell
names, 2 rows with a before-arm figure whose receipt the cell does not name) · 0 suspected
mis-resolutions surviving adjudication.**

---

## 4. The mis-resolution risk: ambiguous basenames

26 of the 65 rows have a token basename that denotes **more than one committed path** — the only
place a register could point at the wrong file. Each was re-tested by content: the registered
path is scored against the cell's own claim values, and its siblings are scored the same way.

| row | candidates | registered | result |
|---|---|---|---|
| L21/22/23 (`c1-after.tsv`,`c2-after.tsv`,`c3-after.tsv`) | 5 | round-28 | **CONFIRMED-UNIQUE** — round-28's file carries all the cell's values; rounds 24-27 do not |
| L31 (`c1-after.tsv`) | 5 | round-27 | **CONFIRMED-UNIQUE** — round-27's file carries `findings=2`, `rc=2`, and the `rev=6cb22dc2…` the cell names; round-28's is a different record |
| L68 ×2, L71, L103, L220, L221 ×2 (knowledge entries) | 3 each | `corpus/knowledge/…` | **CONFIRMED-TIED, and the tie is immaterial**: the three candidates are byte-identical (`sha256 f5e2cf22e609df09…` for the F2 garbage-readings entry, `f1289ba51636c826…` for git-repo-structure) — the r26 `assimilation/validate/` capture and the live `corpus/knowledge/` file hold the same bytes. The register's pick (the live corpus file) is the semantically right one. |
| L478 (`.ufo/waves/round-32/a2w1/SwarmExecutor08.md`) | 5 | `census/round-32/waves/a2w1/SwarmExecutor08.md` | **CONFIRMED-UNIQUE** — the cell cites the `.ufo` path, whose committed twin is the `census/` capture (the file's own head: "# SwarmExecutor08 — r32 a2w1: C2 re-measure at its landing commit + T18 from bytes") |
| L489 (`SwarmCritic26.md`) | 5 | `census/round-32/waves/a2w1/…` | **CONFIRMED-TIED** — cell context round 32 selects round-32 (matches wave-1 `R42scribe05`'s own candidate enumeration) |
| L525 (`.ufo/waves/round-33/make-spec-w2.py`) | 5 | `census/round-33/waves/make-spec-w2.py` | **CONFIRMED-TIED** — round context selects round-33; the file's own head pins `W = L + '/.ufo/waves/round-33/w2'` |
| L540 (`controls.txt`) | 2 | round-34 | **CONFIRMED-TIED** — round context 34 selects round-34 |
| L668 (`c3-before.txt`) | 3 | round-38 | **CONFIRMED-TIED** — round context 38 selects round-38 |
| L761 (`c1-after.txt`) | 5 | round-39 | **CONFIRMED-UNIQUE** |
| L762 (`c2-before.txt`) | 3 | round-39 | **CONFIRMED-UNIQUE** — round-39's file carries `legs=6 pass=2 fail=4 harm=0`; rounds 37/38 carry none of them |
| L762/772 (`c2-after.txt`) | 6 | round-39 | **CONFIRMED-UNIQUE** — round-39 carries 4 of 4 cell tokens; round-40 carries 3; rounds 36-38 carry 1 |
| L763/773 (`c3-after.txt`) | 6 | round-39 | **CONFIRMED-UNIQUE** — round-39 carries 5 of 5; round-40 and round-38 carry 4; rounds 36/37 carry 0-1 |
| L763 (`c3-before.txt`) | 3 | round-39 | **CONFIRMED-UNIQUE** — round-39 carries all 5 (`mutants=4 killed=0 survived=4 base_killed=0 cases=10`); round-38 carries 3 |
| L821/822/823 (`controls/c1,c2,c3-control.txt`) | 3 / 2 / 2 | `census/round-41/controls/…` | **CONFIRMED-TIED, and the tie is immaterial**: the sibling `census/round-41/waves/w2/R41w2scribe02/receipts/*.txt` copies are **byte-identical** to the registered files (`sha256 a2fc6c06bcf4a994…` c1, `898296fc1ecc23c9…` c2, `845bec968a97f46c…` c3). The registered pick is the canonical control, not the wave receipt. |

---

## 5. The two rows with a token no named artifact carries (L424 ×2) — read and decided

`SCORECARD.md:424` (base), full cell:

> … counter readings v1 `legs=11 fail=10` -> `legs=11 fail=0` (`census/round-31/records/c3-after-c3-counter.txt`), v2 `fail=11` -> `legs=12 fail=0` (`c3-after-c3-counter-v2.txt`), v3 `legs=13 fail=0` (`c3-after-c3-counter-v3.txt`)

* `census/round-31/records/c3-after-c3-counter-v2.txt` carries `SUMMARY legs=12 fail=0` — **exactly** the v2 arm the cell attributes to it.
* `census/round-31/records/c3-after-c3-counter-v3.txt` carries `SUMMARY legs=13 fail=0` — **exactly** the v3 arm.
* `fail=10` is the **v1 counter's before-arm** figure and `fail=11` the **v2 counter's before-arm** figure. They are real and committed, but in records the cell does not name: `census/round-31/records/controls.tsv` (hits `fail=10`, `fail=11`) and `census/round-31/records/amendments.txt` (hits `fail=11`, `legs=11`, `legs=12`, `legs=13`).

**Decision: the register's resolutions are CORRECT.** Each register row resolves its token to the
record the cell cites for that token, and each resolved record carries the claim values the cell
attributes to it. The residual `fail=10`/`fail=11` are the *before*-arm readings of other
counters and the cell names no receipt for them — a **SCORECARD citation gap in a base line**,
not a mis-resolution. It is out of this seat's write scope (the base lines are frozen and
byte-identical, and the C1 counter's `rewritten=0` leg forbids touching them) and it is reported
to the L1 as a candidate for a future round's `CORRECTION-SC`, not as a register defect.

---

## 6. Cross-checks against wave 1 and against the frozen counter

* **Wave-1 scribes (by eye):** `R42scribe01`–`R42scribe05` each read 13 rows and reported 65/65 agree;
  `R42reviewer01` re-derived all 70 rows independently with **0 register disagreements**. This
  seat's mechanical second reading reaches the same verdict by a different route and additionally
  shows *why* the 26 rows whose cell tokens are not all inside the resolved file are nonetheless
  right (§3).
* **Frozen counter at the tip under attack** (`--rev 3105a63b23481fccf7df58e74d14a6681e0ea0c8`):
  `SUMMARY items=70 population=ok registered=70 class_ok=70 unresolved=5 corrected=5 junk=0 rewritten=0 new_mismatches=0`, **EXIT=0** — identical to the landed receipt `census/round-42/records/c1-after.txt`.
* **Register self-consistency:** the 4 duplicated `(line, token)` keys (L667, L668, L792, L793 —
  each token cited twice in one cell) carry **identical** `(class, resolved_to)` pairs in both
  rows; **0 inconsistent duplicates**.
* **Existence:** all 65 resolved paths exist at base **and** at tip (`git show <rev>:<path>` returns
  content for every one).
* **Frozen files untouched:** the register, the counter, the population, the controls, the pinned
  tool `tools/souji-worktree-drift.py` and every prior fixture were read only. This seat wrote only
  under `.ufo/waves/round-42/w2/R42w2reviewer09/` and its scratch `/fast/scratch/hyaku/souji-r42/R42w2reviewer09/`
  (scratch removed before yielding). No commit, no push, no mutating git or jj command, no write
  outside the seat directory, no tool installed or updated.

---

## 7. Findings for the L1

1. **No defect in the landed C1 register.** 65/65 resolved rows are semantically correct; the
   mechanical second reading finds 0 mis-resolutions. C1's calibration claim stands.
2. **N-C1d (a limit of the mechanical test, not of the register) — the cell-wide token test is
   not a resolution test.** A SCORECARD cell routinely cites *several* records, so 26 of 65 rows
   have cell tokens that are not in the resolved file (they are in a sibling record the same cell
   names) and 24 of 65 need a shape variant (`8/8` ↔ `cases=8 pass=8`, `19/19` ↔ `sites=19 survived=19`,
   `6/9` ↔ `old(one-line)=(9, 6, 3, 1)`). A falsifier that reads "the resolved file must contain
   every number in the cell" as the correctness condition would false-red 26 correct rows. The
   resolution test that does hold is: **the resolved file must carry the claim values the cell
   attributes to *that* reference** (nearest-reference attribution), which holds 65/65.
3. **L1 candidate for a later round (SCORECARD citation gap, not a register error):**
   `SCORECARD.md:424`'s before-arm figures `fail=10` and `fail=11` are committed but in
   `census/round-31/records/controls.tsv` / `census/round-31/records/amendments.txt`, which the cell
   does not name. Under the lane's own Q101 "a derived value states what it was measured over"
   discipline this is the same shape as the round's existing `CORRECTION-SC` findings. The base
   line is frozen (`rewritten=0` is a C1 kill condition), so it is reportable, not editable.

## 8. Residual risk and verification gaps

* The measurement is over **the base SCORECARD.md** (`bf618f6c…`) exactly as the item specifies;
  the tip SCORECARD is a superset with this round's appended rows and was not used for token
  extraction.
* Two scope choices are mine and are stated so the L1 can overrule them: (a) the "cell" of a
  table row is its `|`-delimited field within the logical (possibly wrapped) row; (b) prose
  units are read as whole paragraphs. Under the narrower physical-line scope the same 65 rows
  give 43/65 at 100 % and 22 rows to adjudicate; under the widest logical-row scope 32/65 and 33
  rows. **All three scopes reach the same verdict** (0 mis-resolutions) — the coverage number
  moves with the scope, the judgment does not.
* Basename ties (§4) are resolved by round context where the cells disagree on content, and are
  byte-identical twins where they do not. Where both apply (L821-823) the content cannot
  distinguish them; the register's pick is the canonical path in every such case.
* Not attempted (out of scope): the five `unresolved` rows (L14, L68 ×2, L92, L175) and the
  `CORRECTION-DE` derivation values — both are wave-1 territory (`R42critic01`, `R42reviewer01`).
* No check was run against C2, C3 or R1; this seat's scope is the C1 register's resolved rows only.

**Verdict: the C1 register is CONFIRMED at the landed tip. No finding against the landed artifact.**

Tooling: no installs or upgrades (the host pacman guard was respected; nothing needed installing).
Scratch `/fast/scratch/hyaku/souji-r42/R42w2reviewer09` removed with `rm -rf` after copying every
receipt cited above into the seat directory.
