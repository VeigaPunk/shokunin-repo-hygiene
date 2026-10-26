# SwarmExecutor04 (C1BindD) — C1 bindings for items N20-N26

## Status
STATUS: PARTIAL — all seven items are honestly bound as WITHDRAWN and the frozen target arithmetic holds for them
(`unbound=0 mismatches=0 withdrawn=7`, identical under v1 and v2, deterministic, rc=0), but no MATCH binding exists:
five cells name no record that holds their integer (A0(a) refuses the only blobs that do) and two carry a
digit-bearing unit word (`k1`) that makes any honest literal inadmissible. This consumes 7 of the round's 8
withdrawals, leaving 1 for the other 37 items.

## Evidence

Base `85b61a151923986e7e6b48f7084b9122561b5f3d`; list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`; scratch proof
revision `e181dc6fc3d2b820df1429328d6cc67400466978`; probe revisions `26f35510251f95d3ec3f0ea5f1963ecc5382ac27`
(record kind) and `c027c07f4d37e601feed0c570e23519022d6712f` (run kind, glued literal). Lane tip untouched at
`7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`.

Acceptance (run twice, byte-identical; v1 with the same arguments gives the same seven verdicts):

```
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-32/c1-counter-v2.py \
  --root /fast/scratch/hyaku/souji-r32/C1BindD/c --rev e181dc6fc3d2b820df1429328d6cc67400466978 \
  --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
  --only N20,N21,N22,N23,N24,N25,N26 --scratch /fast/scratch/hyaku/souji-r32/C1BindD/cnt
```

```
ITEM	N20	SCORECARD.md:313	literal=mismatches=10	binding=withdrawn	WITHDRAWN	<reason: delivery, row N20>
ITEM	N21	SCORECARD.md:313	literal=mismatches=0	binding=withdrawn	WITHDRAWN	<reason: delivery, row N21>
ITEM	N22	SCORECARD.md:314	literal=records=1381	binding=withdrawn	WITHDRAWN	<reason: delivery, row N22>
ITEM	N23	SCORECARD.md:314	literal=failed=0	binding=withdrawn	WITHDRAWN	<reason: delivery, row N23>
ITEM	N24	SCORECARD.md:314	literal=uncovered=0	binding=withdrawn	WITHDRAWN	<reason: delivery, row N24>
ITEM	N25	SCORECARD.md:354	literal=k1=13	binding=withdrawn	WITHDRAWN	<reason: delivery, row N25>
ITEM	N26	SCORECARD.md:354	literal=k1=0	binding=withdrawn	WITHDRAWN	<reason: delivery, row N26>
SUMMARY items=7 bound_run=0 bound_record=0 bound_field=0 withdrawn=7 unbound=0 mismatches=0 partial=1 rev=e181dc6fc3d2b820df1429328d6cc67400466978
rc=0
```

Refusals reproduced with the records that actually hold the integers (probe `26f3551…`):

```
ITEM	N20	record	census/round-29/records/controls.tsv:2	BAD-ROW(A0a-not-cited)
ITEM	N21	record	census/round-29/records/final-tip-measure-2.txt:4	BAD-ROW(A0a-not-cited)
ITEM	N22	record	census/round-29/records/final-tip-measure.txt:5	BAD-ROW(A0a-not-cited)
ITEM	N23	record	census/round-29/records/final-tip-measure.txt:12	BAD-ROW(A0a-not-cited)
ITEM	N24	record	census/round-29/records/final-tip-measure.txt:19	BAD-ROW(A0a-not-cited)
ITEM	N25	record	census/round-30/records/c1-before.txt:29	BAD-ROW(literal)
ITEM	N26	record	census/round-30/records/c1-after-a3.txt:30	BAD-ROW(literal)
SUMMARY items=7 bound_run=0 bound_record=0 bound_field=0 withdrawn=0 unbound=0 mismatches=7 partial=1 rev=26f35510251f95d3ec3f0ea5f1963ecc5382ac27
```

Run-kind refusal and the glued-literal hole (probe `c027c07…`):

```
ITEM	N22	...	binding=run	RUN-MISMATCH	bash tests/fixtures/r28-wave-evidence-capture.sh rc=0 observed=cases=15 pass=15 control=TAMPER-REJECTED
ITEM	N23	...	binding=run	RUN-MISMATCH	<s same run>
ITEM	N24	...	binding=run	RUN-MISMATCH	<s same run>
ITEM	N25	literal=k13	binding=record	MATCH	census/round-30/records/c1-before.txt:29
ITEM	N26	literal=k10	binding=record	BAD-ROW(record-shape)	census/round-30/records/c1-after-a3.txt:30
SUMMARY items=5 bound_run=0 bound_record=1 bound_field=0 withdrawn=0 unbound=0 mismatches=4 partial=1 rev=c027c07f4d37e601feed0c570e23519022d6712f
```

Base-line bytes read for the three rows (no pipe characters inside these quotes):
- `SCORECARD.md:313` (base): "its fixture rejects the always-zero emitter"
- `SCORECARD.md:314` (base): "GNU-escaped records for odd names"
- `SCORECARD.md:354` (base): "records/c1-before.txt` (`k1=13`) -> `census/round-30/records/c1-after-a3.txt` (`k1=0`)"
  Both record basenames are on the row, which is why N25/N26 pass A0(a) and fail only on the literal rule.

## Findings

1. **A0(a) leaves the r29 rows un-bindable.** Location `SCORECARD.md:313`, `SCORECARD.md:314`. Line 313 names only
   `tests/fixtures/r29-registry-agreement.py` (base blob line 195 prints `cases=… pass=… control=…` only); line 314
   names `census/round-26/waves`, whose `waves` component `record_path_ok` forbids
   (`census/round-32/c1-counter-v2.py:143-149`). The only blobs holding the integers are
   `census/round-29/records/controls.tsv:2`, `final-tip-measure-2.txt:4`, `final-tip-measure.txt:5/12/19` and
   `census/round-29/records/amendments.txt:16,35`; none of their basenames occurs on either line, so `cited()`
   (`c1-counter-v2.py:152-158`) refuses them: reproduced `BAD-ROW(A0a-not-cited)` five times.
2. **The literal rule makes every digit-bearing unit word inadmissible.** `ints()` (`c1-counter-v2.py:123`) splits
   `k1=13` into `["1","13"]`, so `len(ints(lit)) != len(iints)` (`:297-298`) refuses the row's own literal; for the
   integer `0` no literal containing the unit `k1` can carry exactly one digit run equal to 0 at all (`k10` reads 10,
   reproduced `BAD-ROW(record-shape)`). N25/N26 are therefore un-bindable by any kind, though the cited blobs do hold
   `k1=13` (`census/round-30/records/c1-before.txt:29`) and `k1=0` (`c1-after-a3.txt:30`).
2b. **No stated integer is wrong.** All seven re-derive from committed bytes: `controls.tsv:2` `k1=6 k2=4 mismatches=10`;
   `final-tip-measure-2.txt:4` `k1=0 k2=0 mismatches=0`; `final-tip-measure.txt:5` `records=1381 failed=0 uncovered=0`;
   `c1-before.txt:29` `k1=13`; `c1-after-a3.txt:30` `k1=0`. The defect is the missing pointer and the literal rule, not
   the counts.
3. **The `run` escape hatch is closed for these cells.** The r28 fixture's last digit-bearing line is
   `cases=15 pass=15 control=TAMPER-REJECTED` (observed, rc=0), so no `records=`/`failed=`/`uncovered=` literal can
   match; the r29 fixture's only stdout summary line is `cases=20 pass=20 control=…` (base blob line 195).
4. **The five withdrawals are the r31 defect-2 pattern recurring at one more pair of rows.** Corroboration, read this
   run: `census/round-31/waves/w2/SwarmScout08.md:35` says "L313/L314 name no record for `mismatches=10 -> 0` and
   `records=1381`" — the cells' integers were never pointed at by the cell.
5. **Budget.** `withdrawn<=8` over 44 items: this seat uses 7. The other 37 items (seats C1BindA/B/C/E/F + L29) must
   yield at most 1 more withdrawal, or the frozen C1 target cannot hold.

## Attack log

- **A1 — A0(a) vs uncited rows (reproduced).** State: probe `26f3551…`, rows shown in Evidence. Five items whose
  integers are observable in committed census records cannot be bound because the r29 capability cells name no record;
  `unbound=0 mismatches=0` is reachable for them only by spending 5 withdrawals. Reproduce with the counter command
  above at that revision.
- **A2 — literal rule is both over- and under-strict (reproduced).** State: probe `c027c07…`. `k1=13` (the row's own
  literal) → `BAD-ROW(literal)`, while the fabricated glued form `k13` → `MATCH` on
  `census/round-30/records/c1-before.txt:29`; the counter accepts a literal that does not occur in the record line and
  refuses the one that does. For `k1=0` no literal passes at all. Not delivered: `k13` would be a gamed binding.
- **A3 — withdrawal budget pressure (arithmetic, not run).** Location `census/round-32/c1-counter.py:62`
  (`WITHDRAW_MAX = 8`). One seat's seven items consume seven of eight; a stricter-only amendment cannot relax the
  literal or citation rules, so either the remaining seats stay at ≤1 withdrawal or the target is lost.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-c1-bind-N20-N26.md` — the exact append block (heading, header, seven rows) plus the
  full counter and probe outputs.
- `.ufo/waves/round-32/w1/SwarmExecutor04.md` — this report.

Lane mutation: none (no add/commit/push/stash/checkout/reset, no jj). Scratch `/fast/scratch/hyaku/souji-r32/C1BindD`
removed after the two files were written; every clone and fixture repo lived under it, and the r28 fixture was run with
`SOUJI_R29_C2FIXTURE_BASE` pointed inside it. No tool installs, no network, no credentials.
