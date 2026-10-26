# SwarmExecutor07 — C1 re-measure from committed bytes (r32 a2w1)

## Status
STATUS: PASS — both frozen C1 counters re-run from committed bytes at the C1 landing commit and at the lane tip; the L1's reading `unbound=6 withdrawn=17` is CONFIRMED (mismatches=6, all of them UNBOUND); the append-only prefix holds byte-exactly and each enumerated id has at most one row. Claim C1 is MISSED at both required revisions. One reproduced ATTACK on the counter's `run` branch is logged below.

## Evidence

Revisions. Lane tip at measurement time = `4e56c48b8fc828f9aba2746e324dc46aa538bdbf` (orchestrator salvage of attempt-1 records; `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse master`); C1 landing = `9e8982b7a6ac57dffa415f9db43cf7cd6e829c93`; base = `85b61a151923986e7e6b48f7084b9122561b5f3d`; list-rev = `3ec84fc81b3243429c834a051880b0bcde06291c`. Instrument identity is unchanged between landing and tip: `census/round-32/c1-counter.py` = `a96ea45a07ac10ef0914df2b74b8d30179cd668b`, `census/round-32/c1-counter-v2.py` = `6621291de0a100bf61d4f32050960aec4f678420`, `census/round-32/c1-items.tsv` = `bb93acf4f30b06218bc375ce0cc2c6f4a0504d72` (same oids at 9e8982b and 4e56c48).

Four runs (TMPDIR + `--scratch` under `/fast/scratch/hyaku/souji-r32/RemeasureC1/`):

```
python3 -B census/round-32/c1-counter.py    --root <lane> --rev 9e8982b… --base 85b61a1… --list-rev 3ec84fc…   # v1 @ landing
python3 -B census/round-32/c1-counter-v2.py --root <lane> --rev 9e8982b… --base 85b61a1… --list-rev 3ec84fc…   # v2 @ landing
python3 -B census/round-32/c1-counter.py    --root <lane> --rev 4e56c48… --base 85b61a1… --list-rev 3ec84fc…   # v1 @ tip
python3 -B census/round-32/c1-counter-v2.py --root <lane> --rev 4e56c48… --base 85b61a1… --list-rev 3ec84fc…   # v2 @ tip
```

SUMMARY, all four runs identical except `rev=`:

```
SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6 rev=9e8982b7a6ac57dffa415f9db43cf7cd6e829c93   EXIT=1
SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6 rev=9e8982b7a6ac57dffa415f9db43cf7cd6e829c93   EXIT=1   (v2)
SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6 rev=4e56c48b8fc828f9aba2746e324dc46aa538bdbf   EXIT=1
SUMMARY items=44 bound_run=3 bound_record=9 bound_field=9 withdrawn=17 unbound=6 mismatches=6 rev=4e56c48b8fc828f9aba2746e324dc46aa538bdbf   EXIT=1   (v2)
```

`mismatches=6` equals `unbound=6`, so no row failed on shape or on its observable: every one of the 38 appended rows is a MATCH or a well-formed WITHDRAWN under v1 AND v2.

Every non-MATCH ITEM line (v1 @ tip; byte-identical set under v2 and at landing):

```
ITEM	N02	SCORECARD.md:151	literal=33 rows	binding=withdrawn	WITHDRAWN	no cited record holds the baseline 33 rows because verification.json prints the ending census rows 37
ITEM	N03	SCORECARD.md:151	literal=16 mined	binding=withdrawn	WITHDRAWN	no cited record holds 16 mined since verification.json prints the ending census mined 20
ITEM	N11	SCORECARD.md:159	literal=401 tuples	binding=withdrawn	WITHDRAWN	No observable in the cited census/round-21/oracle-acceptance.json holds 401 as a JSON integer; the 401 old tuples survive only as the length of the prior_verdicts list plus a sha256 digest, while the text record that prints count=401 is oracle-acceptance.txt, a basename the base line does not cite.
ITEM	N13	SCORECARD.md:165	literal=19 leaks	binding=withdrawn	WITHDRAWN	the only cited occurrence base_leaks=19 sits on reason-after.txt line 29, which N14 already binds, and the counter forbids a shared occurrence
ITEM	N15	SCORECARD.md:168	literal=18 step	binding=withdrawn	WITHDRAWN	the 18 steps live in census/round-21/step-inventory.json, whose basename line 168 never cites, and no line-named script prints them
ITEM	N17	SCORECARD.md:168	literal=11 base	binding=withdrawn	WITHDRAWN	the 11 needs the pre-r20 auditor passed as --base-tool, no committed copy of it exists, and line 168 cites no round-20 record
ITEM	N18	SCORECARD.md:175	literal=2 base	binding=withdrawn	WITHDRAWN	census/round-24/records/c2-control-base.tsv line 11 holds mismatches=2 but never the word base, so the A0(b) adjacency the unit demands cannot hold
ITEM	N20	SCORECARD.md:313	literal=mismatches=10	binding=withdrawn	WITHDRAWN	the cell cites only the r29 fixture, which prints cases/pass and not this count, and names no record; the sole blob holding mismatches=10 is census/round-29/records/controls.tsv line 2, refused by A0(a) as uncited
ITEM	N21	SCORECARD.md:313	literal=mismatches=0	binding=withdrawn	WITHDRAWN	the cell cites only the r29 fixture, which prints cases/pass and not this count, and names no record; the sole blob holding the after value is census/round-29/records/final-tip-measure-2.txt line 4, refused by A0(a) as uncited
ITEM	N22	SCORECARD.md:314	literal=records=1381	binding=withdrawn	WITHDRAWN	the row names census/round-26/waves, a waves component that record paths forbid, and the blobs holding records=1381 are census/round-29/records/final-tip-measure.txt line 5 and amendments.txt line 35, neither cited on the row
ITEM	N23	SCORECARD.md:314	literal=failed=0	binding=withdrawn	WITHDRAWN	the only blobs holding failed=0 for this capture are census/round-29/records/final-tip-measure.txt and amendments.txt, neither cited on the row, and the cited fixture prints cases/pass only
ITEM	N24	SCORECARD.md:314	literal=uncovered=0	binding=withdrawn	WITHDRAWN	the only blobs holding uncovered=0 for this capture are census/round-29/records/final-tip-measure.txt and amendments.txt, neither cited on the row, and the cited fixture prints cases/pass only
ITEM	N25	SCORECARD.md:354	literal=k1=13	binding=withdrawn	WITHDRAWN	the cited blob census/round-30/records/c1-before.txt line 29 does hold k1=13, but no literal can contain the unit k1 and exactly one integer because the unit token itself carries the digit run 1
ITEM	N26	SCORECARD.md:354	literal=k1=0	binding=withdrawn	WITHDRAWN	the cited blob census/round-30/records/c1-after-a3.txt line 30 does hold k1=0, but no literal can contain the unit k1 with exactly one integer equal to 0 at all, since k1 carries digit run 1 and any glued form reads 10
ITEM	N28	SCORECARD.md:422	literal=20	binding=-	UNBOUND	
ITEM	N29	SCORECARD.md:422	literal=20	binding=-	UNBOUND	
ITEM	N30	SCORECARD.md:422	literal=1	binding=-	UNBOUND	
ITEM	N31	SCORECARD.md:422	literal=1	binding=-	UNBOUND	
ITEM	N33	SCORECARD.md:422	literal=34	binding=-	UNBOUND	
ITEM	N34	SCORECARD.md:422	literal=41	binding=-	UNBOUND	
ITEM	N38	SCORECARD.md:423	literal=pass=3	binding=withdrawn	WITHDRAWN	the base-gate arm's 3 is recorded only in census/round-31/records/c2-fixture-red-before.txt, which this base line does not cite, and that arm exits 1
ITEM	N42	SCORECARD.md:423	literal=495	binding=withdrawn	WITHDRAWN	the item's only unit r26 contains a digit, so any literal naming that unit holds two digit runs and the frozen literal rule rejects it, leaving no representable observable
ITEM	N43	SCORECARD.md:424	literal=17 RESULT	binding=withdrawn	WITHDRAWN	the 17 is a count of RESULT lines and no cited round-31 record puts 17 adjacent to a result word, so no A0-admissible observable shows it
```

Append-only prefix (byte compare, not line compare):

```
git cat-file blob 85b61a1…:SCORECARD.md > sc-base.md      # 81245 bytes
git cat-file blob 9e8982b…:SCORECARD.md > sc-landing.md   # 91433 bytes
git cat-file blob 4e56c48…:SCORECARD.md > sc-tip.md       # 91433 bytes
cmp -n 81245 sc-base.md sc-landing.md  -> no output (identical)
cmp -n 81245 sc-base.md sc-tip.md      -> no output (identical)
cmp sc-landing.md sc-tip.md            -> no output (landing and tip SCORECARD.md are byte-identical)
```

Rows per id in the appended tail (`tail -n +<base_lines+1>` of the tip blob): 38 rows, 38 distinct ids, `uniq -d` empty. Present set vs `c1-items.tsv` ids at 3ec84fc — missing exactly `N28 N29 N30 N31 N33 N34`, extras none.

## Findings

1. **The L1's reading is confirmed and the claim is MISSED at both required revisions.** `unbound=6 mismatches=6 withdrawn=17` at landing `9e8982b` and at tip `4e56c48`, under v1 and v2 alike. Preregistration target is `unbound=0 mismatches=0 withdrawn<=8`; all three conditions fail. Kill rule ("any of the three off target at the C1 landing commit or at the tip") triggers. Location: `census/round-32/records/preregistration.txt` (C1 paragraph, target + kill rule); counter exit codes 1 in all four runs above.
2. **`withdrawn=17 > 8` fails independently of the six unbound items**, so converting N28–N31/N33/N34 to matches could not have met the target. At least three withdrawals are forced by the frozen literal rule itself, because the unit token carries a digit run and a literal must hold exactly one integer (`k1` for N25/N26 — `census/round-30/records/c1-before.txt:29`, `c1-after-a3.txt:30`; `r26` for N42 — `SCORECARD.md:423`). Floor on honest withdrawals is therefore ≥3 of a cap of 8.
3. **The six unbound items have a structural floor of six, not a seat-effort shortfall.** All eight items on `SCORECARD.md:422` (N27–N34) derive their integers from two r31 SUMMARY lines only: `census/round-31/records/c1-after-a4.txt:43` (`items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1`) and `census/round-31/records/c1-before.txt:43` (`items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34`) — `grep -nE 'bound_run|unbound|mismatches'` over both blobs returns only line 43. The counter allows one item per `(path, line)` (`BAD-ROW(shared-occurrence)`), so at most 2 of the 8 are bindable by `record:`; the other path cited on line 422, `census/round-31/c1-cells.tsv`, contains none of the units `items|bound_run|bound_record|unbound|mismatches` (grep, 48 lines) and no line 422 `field:` target is a `.json`. Observed 6 unbound = the floor. Location: counter docstring "No two items may bind the same (path, line) record occurrence"; `SCORECARD.md:422`.
4. **The only `run:` script cited on line 422 exits 1 at REV, so `run:` is closed honestly.** `tools/souji-capability-cells.py` (blob `8c1453c33dbd3251d86600abb9f3ff6f948fc968`, identical at base and REV) run from the base blob in a clone at tip prints `SUMMARY items=41 bound_run=20 bound_record=20 unbound=1 mismatches=1 rev=24f343c8…` with exit 1 (it returns 1 whenever `mismatches>0`); the counter requires exit 0 for MATCH.
5. **Amendment A0 was not consulted as data and changes nothing here.** v2 and v1 produce the same 44 verdicts at both revisions, i.e. no landed row violates A0(a) citation or A0(b) adjacency — the shortfall is entirely unbound + withdrawals. Location: `census/round-32/records/amendments.txt:3-11`.
6. **Not re-derived (out of this item's remit):** whether each of the other 14 withdrawal reasons is genuinely unavailable was not re-probed; `ExecC1Measure` owns the row-by-row quote audit.

## Attack log

ATTACK A-1 (C1 counter, `run` branch — reachability of the target without observing the cell): the `run` literal rule only requires the literal to carry the item's *number of* integers plus one of its unit words; it explicitly permits "a corrected count" and never requires the literal's integer to equal the item's. A cited script with a partial-run switch therefore binds every item on a base line regardless of the cell's numbers. Reproduced state, all inside `/fast/scratch/hyaku/souji-r32/RemeasureC1/attack/` (scratch clone of the lane at tip, origin removed, probe commit `08e705703b123afffa4b004a5b4f923aebf21ee7` appending six rows to `SCORECARD.md`):

```
| N28 | SCORECARD.md:422 | bound_run=1   | run: python3 -B tools/souji-capability-cells.py … --only L01 --scratch <scratch> | PROBE only |
| N29 | SCORECARD.md:422 | bound_record=0| run: …same… | PROBE only |
| N30 | SCORECARD.md:422 | unbound=0     | run: …same… | PROBE only |
| N31 | SCORECARD.md:422 | mismatches=0  | run: …same… | PROBE only |
| N33 | SCORECARD.md:422 | mismatches=0  | run: …same… | PROBE only |
| N34 | SCORECARD.md:422 | items=1       | run: …same… | PROBE only |
```

```
python3 -B census/round-32/c1-counter.py --root <probe clone> --rev 08e7057… --base 85b61a1… --list-rev 3ec84fc… --only N28,N29,N30,N31,N33,N34
-> six lines "binding=run  MATCH  … rc=0 observed=SUMMARY items=1 bound_run=1 bound_record=0 unbound=0 mismatches=0 partial=1 rev=<HEX>"
SUMMARY items=6 bound_run=6 bound_record=0 bound_field=0 withdrawn=0 unbound=0 mismatches=0 partial=1 rev=08e705703b123afffa4b004a5b4f923aebf21ee7   EXIT=0
```

The probe binds nothing to anything: `items=1 … partial=1` is the r31 tool auditing one item (`--only L01`), not the cell's `items=41 bound_run=20 unbound=1`. Consequences: (a) Finding 3 holds for *honest* binding only — the `unbound=0` target is reachable, but only by restating a single-item partial run as the cell's count; (b) the same switch makes any future `run` cell bindable by an arbitrary audit subset, so `run:` rows are not ground truth on their own; (c) a stricter-only successor instrument would require the run's summary not to carry `partial=1` and would require the literal integer to equal the item's integer. No amendment is proposed here: amendments are the L1's and must be stricter-only.

## Deliveries
- `.ufo/waves/round-32/a2w1/SwarmExecutor07.md` (this report).

No lane file was written, no git/jj mutation in the lane, no build/test run. Scratch `/fast/scratch/hyaku/souji-r32/RemeasureC1` (four counter runs, the capability-cells probes `probe/`, and the attack clone `attack/`) was created for this item and removed on exit.
