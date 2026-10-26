# SwarmCritic04 — audit of C1 rows N20–N26 (landed 9e8982b)

## Status

STATUS: PARTIAL — six of the seven withdrawals hold under the frozen rules (exhaustive sweep finds no
admissible observable), but **N25 is a wrong-withdrawal**: the glued literal `k13` MATCHes in *both* v1 and
v2 against the record the row itself cites. Two reason texts (N20, N21) carry false "sole blob" sweeps. The
batch also consumes most of the frozen `withdrawn<=8` budget (arithmetic below).

## Evidence

Revisions: base `85b61a151923986e7e6b48f7084b9122561b5f3d`, list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`,
C1 landing `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93`, lane tip `4e56c48b8fc828f9aba2746e324dc46aa538bdbf`.
Append-only holds at both (`rev.startswith(base)` true; tail 43 lines). Scratch:
`/fast/scratch/hyaku/souji-r32/AuditC1N20N26/` (clone `git clone --no-local`, `origin` removed, detached).

Required counter run (v2, pasted verbatim):

```
$ python3 -B census/round-32/c1-counter-v2.py --root <lane> \
    --rev 9e8982b7a6ac57dffa415f9db43cf7cd6e829c93 --base 85b61a151923986e7e6b48f7084b9122561b5f3d \
    --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only N20,N21,N22,N23,N24,N25,N26 \
    --scratch /fast/scratch/hyaku/souji-r32/AuditC1N20N26/cnt
ITEM	N20	SCORECARD.md:313	literal=mismatches=10	binding=withdrawn	WITHDRAWN	the cell cites only the r29 fixture, which prints cases/pass and not this count, and names no record; the sole blob holding mismatches=10 is census/round-29/records/controls.tsv line 2, refused by A0(a) as uncited
ITEM	N21	SCORECARD.md:313	literal=mismatches=0	binding=withdrawn	WITHDRAWN	the cell cites only the r29 fixture, which prints cases/pass and not this count, and names no record; the sole blob holding the after value is census/round-29/records/final-tip-measure-2.txt line 4, refused by A0(a) as uncited
ITEM	N22	SCORECARD.md:314	literal=records=1381	binding=withdrawn	WITHDRAWN	the row names census/round-26/waves, a waves component that record paths forbid, and the blobs holding records=1381 are census/round-29/records/final-tip-measure.txt line 5 and amendments.txt line 35, neither cited on the row
ITEM	N23	SCORECARD.md:314	literal=failed=0	binding=withdrawn	WITHDRAWN	the only blobs holding failed=0 for this capture are census/round-29/records/final-tip-measure.txt and amendments.txt, neither cited on the row, and the cited fixture prints cases/pass only
ITEM	N24	SCORECARD.md:314	literal=uncovered=0	binding=withdrawn	WITHDRAWN	the only blobs holding uncovered=0 for this capture are census/round-29/records/final-tip-measure.txt and amendments.txt, neither cited on the row, and the cited fixture prints cases/pass only
ITEM	N25	SCORECARD.md:354	literal=k1=13	binding=withdrawn	WITHDRAWN	the cited blob census/round-30/records/c1-before.txt line 29 does hold k1=13, but no literal can contain the unit k1 and exactly one integer because the unit token itself carries the digit run 1
ITEM	N26	SCORECARD.md:354	literal=k1=0	binding=withdrawn	WITHDRAWN	the cited blob census/round-30/records/c1-after-a3.txt line 30 does hold k1=0, but no literal can contain the unit k1 with exactly one integer equal to 0 at all, since k1 carries digit run 1 and any glued form reads 10
SUMMARY items=7 bound_run=0 bound_record=0 bound_field=0 withdrawn=7 unbound=0 mismatches=0 partial=1 rev=9e8982b7a6ac57dffa415f9db43cf7cd6e829c93
rc=0
```

v1 (`census/round-32/c1-counter.py`, identical arguments) returns the same seven WITHDRAWN lines and
`SUMMARY items=7 bound_run=0 bound_record=0 bound_field=0 withdrawn=7 unbound=0 mismatches=0 partial=1`, rc=0.

No row in this batch is a `record:`, `field:` or `run:` binding (the seven are all `withdrawn:`), so there is
no bound record line / JSON field / argv to re-run. Instead I (a) opened the blob each reason names,
(b) ran an exhaustive admissible-record sweep over every blob the frozen `record` rules would allow, and
(c) ran the cited fixtures' stdout shape down from committed bytes.

**(a) Named blobs, opened at base (blob IDs identical base ↔ 9e8982b):**

| row | blob named by the reason | line | content / verdict |
|---|---|---|---|
| N20 | `census/round-29/records/controls.tsv` | 2 | base do-nothing control, `mismatches=10` present — the r29 C1 before-value |
| N21 | `census/round-29/records/final-tip-measure-2.txt` | 4 | after-value present |
| N22 | `census/round-29/records/final-tip-measure.txt` | 5 | `r26 records=1381 failed=0 uncovered=0 floor_violation=0` (also :12, :19) |
| N22 | `census/round-29/records/amendments.txt` | 35 | `records=1381 failed=0 uncovered=0` (also :32) |
| N23/N24 | same two blobs | — | the only lines pairing `failed=0` / `uncovered=0` with `records=1381` |
| N25 | `census/round-30/records/c1-before.txt` | 29 | `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10` |
| N26 | `census/round-30/records/c1-after-a3.txt` | 30 | `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10` |

So every integer in the batch is the cell's **own** measurement (same round, same instrument), never a
coincidental match; the barrier claimed is representability/citation, not truth.

**(b) Exhaustive admissible-record sweep** (`path_ok` + `cited` + digit-boundary + unit adjacency exactly as
`c1-counter-v2.py` implements them, over every blob in the items' rounds):

```
N20 rounds [29] cited-record-hits= []
N21 rounds [29] cited-record-hits= []
N22 rounds [26, 28, 29] cited-record-hits= []
N23 rounds [26, 28, 29] cited-record-hits= []
N24 rounds [26, 28, 29] cited-record-hits= []
```

**(c) Run-kind closure.** Line 313 cites only `tests/fixtures/r29-registry-agreement.py`; its base blob
writes stdout on exactly one line (`tests/fixtures/r29-registry-agreement.py:195`:
`print(f'cases={len(CASES)} pass={passed} control=`; the three other `print(` calls pass `file=sys.stderr`),
so no run argv can make `S` carry `mismatches=10|0`. Line 314 cites
`tests/fixtures/r28-wave-evidence-capture.sh`, whose last stdout line is
`printf 'cases=15 pass=%s control=TAMPER-REJECTED\n' "$pass"` (:537) and which prints no `records=`,
`failed=` or `uncovered=` token at all. The `.ufo/waves` and `waves`-component routes are refused by
`record_path_ok`; `census/round-26/waves` is a directory (`git cat-file -t` → tree).

**(d) Probe of the N25 hole** (clone at 9e8982b, row replaced by
`| N25 | SCORECARD.md:354 | k13 | record: census/round-30/records/c1-before.txt:29 | probe |`, committed as
`56d2b8c81c4f8cb7ff68cff1a87e9d51997a38c9`, run twice, identical):

```
ITEM	N25	SCORECARD.md:354	literal=k13	binding=record	MATCH	census/round-30/records/c1-before.txt:29
SUMMARY items=1 bound_run=0 bound_record=1 bound_field=0 withdrawn=0 unbound=0 mismatches=0 partial=1 rev=56d2b8c81c4f8cb7ff68cff1a87e9d51997a38c9
rc=0
```

Same result from `c1-counter.py` (v1) at the same probe rev.

**(e) Delivery ↔ landing identity.** The seven rows in
`.ufo/waves/round-32/w1/deliver-c1-bind-N20-N26.md` are byte-identical to the rows landed at 9e8982b
(7/7 verbatim, no integration drift).

**(f) Budget at tip** (`4e56c48`, SCORECARD unchanged since 9e8982b): tail kinds
`field=9 record=9 run=3 withdrawn=17`, unbound items `N28 N29 N30 N31 N33 N34`, no duplicate rows.

No tools installed (nothing needed); no pacman, no writes outside scratch/report.

## Findings

1. **N25 is a wrong-withdrawal (row at `SCORECARD.md:459` at 9e8982b).** The reason asserts "no literal can
   contain the unit k1 and exactly one integer". False: `k13` contains the unit `k1` and exactly one integer
   run (`13`), and the record cited on the base line — `census/round-30/records/c1-before.txt`, basename
   present on `SCORECARD.md:354` — holds it. Reproduced MATCH in v1 and v2 (evidence (d)). Impacted item:
   N25; impacted axis: calibration (C1).
2. **The literal rule is gameable by glue (contract hole, not a row defect per se).** "Literal holds exactly
   as many integers as the item; contains one of the item's units as a substring" plus "`record` line must
   have unit adjacent to integer" lets the *literal* misstate the bytes while the *line* passes. Every item
   whose unit ends in a digit (`k1`, `r26`, …) is affected.
3. **N20 and N21 reason texts carry false auxiliary sweeps** (`SCORECARD.md:454`, `:455` at 9e8982b). They
   claim the "sole blob" holding the value is the one they name. Counter-evidence, both in r29 records:
   `census/round-29/records/controls.tsv:6` — `SUMMARY k1=6 k2=4 mismatches=10 rev=18e881581ab3c322e59301629582921df9e33bcf`
   — and `census/round-29/records/amendments.txt:16` — ``Base do-nothing control with v2: `k1=6 k2=4 mismatches=10` (unchanged).``
   For N21: `census/round-29/records/final-tip-measure.txt:2` —
   `SUMMARY k1=0 k2=0 mismatches=0 rev=de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b` — and
   `census/round-29/records/controls-amended.tsv:2`. The operative claim (A0(a): uncited ⇒ inadmissible)
   still holds, so the verdicts stand; the provenance prose does not.
4. **N22–N24 qualifiers are load-bearing but sound.** `failed=0`/`uncovered=0` are common blob-wide (e.g.
   `controls.tsv:8-9`, `final-tip-measure-2.txt:5` carry `manifests=… failed=0`), yet only
   `final-tip-measure.txt` and `amendments.txt` pair them with `records=1381`, so "for this capture" is true.
   N22's line list is partial (`final-tip-measure.txt` also :12/:19; `amendments.txt` also :32) — imprecise,
   not false at blob granularity.
5. **Withdrawal budget is nearly saturated (N20–N26 contribution).** Unfixable-by-construction items in this
   batch: N20, N21, N22, N23, N24, N26 (verified above) — 6 of the 8 allowed; N25 becomes a 7th the moment
   the hole in Finding 2 is closed. N42 is forced too (`r26` carries the digit run 26, so no literal with
   exactly one integer `495` exists — the row's own reason states this). With `withdrawn=17` at tip, the
   frozen target leaves at most 1–2 other withdrawals and requires **all six** unbound items
   (`N28 N29 N30 N31 N33 N34`) to bind. [INFERENCE: this is arithmetic on verified counts, not a measured
   counter verdict.]
6. **`withdrawn:` rows have an unchecked literal and an unchecked reason.** The counter validates only the
   ≥8-word reason length; the literal and every factual claim inside the reason are never read. That is how
   Findings 1 and 3 survived a counter that reports `mismatches=0`. Not a proposal to change the frozen
   predicate — a reason the L1 must spot-check withdrawal prose by hand.

## Attack log

- **A1 — glued-literal bypass of the C1 record rule.** Reproduced state: commit
  `56d2b8c81c4f8cb7ff68cff1a87e9d51997a38c9` (clone of 9e8982b + N25 row rewritten as
  `k13`/`record: census/round-30/records/c1-before.txt:29`) yields `MATCH` in v1 and v2. Consequence: N25's
  landed withdrawal is not valid under the frozen definition ("no observable shows it"), and the same glue
  would let an item substitute a fabricated literal for a real measurement.
- **A2 — premature saturation of `withdrawn<=8`.** Counted at tip 4e56c48: 17 withdrawn, 6 unbound
  (command in Evidence (f)). Six forced withdrawals already come from this batch; the target therefore
  demands essentially every remaining withdrawal convert plus all six unbound bind. Any further
  structurally-unrepresentable item makes C1's frozen target unreachable.
- **A3 — false provenance in the unchecked reason column.** N20/N21 as in Finding 3. The counter cannot see
  it; the rows still read as evidence-backed refusals.

### Smallest safe correction

1. **Stricter-only amendment, `record` kind only (A(c)):** require every integer of a `record:` literal to
   sit adjacent to one of the item's units *inside the literal*, using the same regex A0(b) already applies
   to the record line (`unit`, ≤3 non-alphanumeric bytes, integer — or the reverse). Then `k13` is refused,
   N25's withdrawal becomes true, and no landed row regresses: all 9 landed `record:` rows pass the test
   (`N14 leaks=0`, `N27 items=41`, `N32 unbound=22`, `N35 cases=10`, `N36 pass=10`, `N37 cases=10`,
   `N39 fp=0`, `N40 real=2`, `N41 cne=0`), while scoping it to `record` leaves the `field` rows (all pass
   anyway) and the `run` literals `failed=0` (N12) and `base_discriminating=12` (N16) untouched — applying
   adjacency to `run` would regress those two. Cost: N25 stays withdrawn, so the forced-withdrawal count in
   this batch is 7, consuming the last budget slot (Finding 5) — the L1 must decide with that cost visible.
2. **Do not take the cheaper-looking alternative** of rebinding N25 as `k13`: the record prints `k1=13`, so
   the literal would be a fabricated token and the row would claim provenance the bytes do not support.
3. **Append-only text correction for N20/N21 reason columns** (the tail is editable; the base bytes are not):
   replace "the sole blob holding …" with the true sweep, e.g. "uncited blobs holding it: controls.tsv:2 and
   :6, amendments.txt:16 — A0(a) refuses all". Same for N21 naming `final-tip-measure.txt:2` and
   `controls-amended.tsv:2`. N22's line list should add `final-tip-measure.txt:12,:19`, `amendments.txt:32`.
4. N26, N22, N23, N24, N20, N21 need no row change: their withdrawals are true as stated (modulo item 3).

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/a2w1/SwarmCritic04.md` (this file)

Scratch `/fast/scratch/hyaku/souji-r32/AuditC1N20N26` removed after writing; the probe state is reproducible
from the exact row substitution recorded in Evidence (d).
