# SwarmExecutor04 — C1 bindings L21-L29 (souji r31 w1)

## Status

STATUS: PARTIAL — 8 of 9 assigned items (L21-L28) are honestly bound and read MATCH twice at the proof revision; L29 has no honest binding under the frozen C1 record rule (its named record states the count as scalar fields, never as a two-integer literal), so `unbound=1` remains and I did not force a row.

## Evidence

Lane tip used for the base state: `1b811368461785040e955f41f9c97e62f61fd67c` (branch `master`; `git diff --stat 9f17a1e..1b81136 -- SCORECARD.md` is empty, so the append-only base bytes hold). Lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; enumeration `--list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`. Scratch clone `/fast/scratch/hyaku/souji-r31/C1BindD/cf` (origin removed, toplevel verified), block committed as `4b8010d1850cac1c0ca5490739672edb5996ff41` (13 insertions, SCORECARD.md only).

Red before (lane repo, no supersession rows), `python3 -B tools/souji-capability-cells.py … --only L21,…,L29`:

```
ITEM	L21	SCORECARD.md:166	literal=4/0	base-cell	binding=run	RUN-MISMATCH	… observed=SUMMARY total=4 failed=0 base_discriminating=2
ITEM	L24	SCORECARD.md:168	literal=118/0	base-cell	binding=-	UNBOUND
ITEM	L27	SCORECARD.md:170	literal=3/3	base-cell	binding=-	UNBOUND
SUMMARY items=9 bound_run=0 bound_record=0 unbound=6 mismatches=9 partial=1 rev=1b811368461785040e955f41f9c97e62f61fd67c
rc=1
```

After appending the eight rows in the scratch clone (identical output on two runs, `--scratch …/cnt1` and `…/cnt2`):

```
ITEM	L21	SCORECARD.md:166	literal=total=4 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r19-carry-wrap.py rc=0 observed=SUMMARY total=4 failed=0 base_discriminating=2
ITEM	L22	SCORECARD.md:167	literal=total=11 failed=0	superseded	binding=run	MATCH	python3 tools/souji-rev-pin.py --selftest rc=0 observed=SUMMARY total=11 failed=0
ITEM	L23	SCORECARD.md:167	literal=total=13 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r19-rev-pin.py rc=0 observed=SUMMARY total=13 failed=0 base_discriminating=6
ITEM	L24	SCORECARD.md:168	literal=118/0	superseded	binding=record	MATCH	census/round-21/r20-closure-excerpt.json
ITEM	L25	SCORECARD.md:168	literal=total=17 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r19-seat-audit-shapes.py rc=0 observed=SUMMARY total=17 failed=0 base_discriminating=12
ITEM	L26	SCORECARD.md:168	literal=78/0	superseded	binding=record	MATCH	census/round-21/r20-closure-excerpt.json
ITEM	L27	SCORECARD.md:170	literal=scenarios=3\treplayed=3	superseded	binding=record	MATCH	census/round-21/final-code-verification.json
ITEM	L28	SCORECARD.md:170	literal=matched=18/18	superseded	binding=record	MATCH	census/round-21/final-code-verification.json
ITEM	L29	SCORECARD.md:170	literal=18/18	base-cell	binding=-	UNBOUND
SUMMARY items=9 bound_run=4 bound_record=4 unbound=1 mismatches=1 partial=1 rev=4b8010d1850cac1c0ca5490739672edb5996ff41
rc=1
```

Record blobs unchanged base to proof rev (the counter's own identity check passed for every record row): `census/round-21/r20-closure-excerpt.json` `5cd2243dd0f30854752f2a4608ca146866ccfb95`; `census/round-21/final-code-verification.json` `6483d98f7ea9bd7ddd1997648f64a143c1c56901`; `census/round-21/remote-source-after.json` `f4123cf12614e43bc26e500a75befbcfadbe3bac`.

No tooling was installed or upgraded in this seat (existing `git`, `python3`, and the lane's committed scripts only). Fixture scripts create and remove their own `/var/tmp` synthetic worlds (their documented behaviour); all seat-owned clones, blocks and receipts lived under `/fast/scratch/hyaku/souji-r31/C1BindD/` with `TMPDIR` set there, and the directory is removed before hand-off.

## Findings

1. **L21, L22, L23, L25 slash literals are not printed by the commands the cells name; the counts are.** SCORECARD.md:166 (`4/0`) and :167 (`11/0`, `13/0`) were added by `1db7108d`; :168 (`17/0`) by `4eb2fda5`. The named fixtures/helper print `SUMMARY total=4 failed=0 base_discriminating=2`, `SUMMARY total=11 failed=0`, `SUMMARY total=13 failed=0 base_discriminating=6`, and `SUMMARY total=17 failed=0 base_discriminating=12`. Red-before shows `RUN-MISMATCH` for the first three precisely because the cells keep the slash form. Bound as `run:` rows with the emitted SUMMARY notation; counts equal the cell integers exactly (no growth, no shrink).

2. **L24 (118/0) cannot take a run binding even though the auditor still prints it.** SCORECARD.md:168 names `auditor selftest118/0`; `python3 tools/souji-seat-audit.py --selftest` prints `SELFTEST pass=118 fail=0` today, but the tool's stem `souji-seat-audit` does not occur on the base line, so a superseding run row is `BAD-ROW(run-shape)`. Bound to `census/round-21/r20-closure-excerpt.json`, whose r20 closure recheck (the record the row's own r21 commit cites) states `auditor selftest 118/0`.

3. **L26 (78/0) is reachable only with an uncommitted baseline auditor.** SCORECARD.md:168 states `r20-audit-contract78/0 (base11)`. The bare fixture prints `SUMMARY total=66 pass=66 fail=0 base_discriminating=0`; supplying `--base-tool` with the auditor extracted from `12516f7d` (sha256 `62522acc…`, matching the closure receipt) prints `SUMMARY total=78 pass=78 fail=0 base_discriminating=11`. No baseline auditor blob is committed in the lane, so no committed argv can reproduce 78; bound to `census/round-21/r20-closure-excerpt.json`, which states `r20 oracle 78/0, 11 base-discriminating`.

4. **L27/L28: the cell's named JSON carries the counts only as fields, so the observable is the same run's retained stdout.** SCORECARD.md:170 (rewritten by `4eb2fda5`) cites `census/round-21/accepted-matrix.json`, which states `"scenarios": 3`, `"replayed": 3` and `matched_command_count: 18` per scenario but contains neither `3/3` nor `18/18`. The accepted-matrix run's stdout is retained in `census/round-21/final-code-verification.json` (`matrix.argv` rev `195715439a08…`, work `/var/tmp/souji-r21-matrix-1957`, the same run `accepted-matrix.json` serializes): `SCENARIO S1 exit=0 matched=18/18 src_sample_unchanged=yes` … `MATRIX scenarios=3 replayed=3 summaries_equal=True`. Bound both as `record:` rows there, with L27's literal in the JSON-escaped form (`scenarios=3\treplayed=3`, two bytes backslash and `t`).

5. **L29 has no honest binding: the cell names a record that never states `18/18`.** SCORECARD.md:170 states `remote-source-after.json18/18`. `census/round-21/remote-source-after.json` records that result as `"expected_command_count": 18`, `"matched_command_count": 18`, `"observed_command_count": 18`, `"all_matched": true` — scalar fields, no two-integer literal. Exhaustive line-by-line sweep of every file under `census/round-20/` and `census/round-21/` for substrings whose only integer tokens are exactly two `18`s returns six records carrying `18/18` (`census/round-20/recovery-status-catalog.json`, `census/round-21/r20-closure-excerpt.json`, `replay-integrated.txt`, `replay-final.txt`, `final-verification.json`, `final-code-verification.json` — all matrix or r20/r19 acceptance receipts) plus hex/path fragments (`18-clone-executor`, `18/missing.json`). None states the remote-ref-only source as `18/18`, and no `tools/` or `tests/fixtures/` stem occurs anywhere on line 170, so no run row exists either. The honest conclusion is that this cell literal is not backed by the bytes of the record it cites; reaching `unbound=0` here requires an L1 decision, not a binding.

6. **Integration hazard for the L1's append.** The L27 literal must survive as a literal backslash plus `t`; expanding it to a TAB silently turns the row into `RECORD-MISMATCH` (the JSON blob has no tab there). The post-append check is `sed -n '/^### Round 31 capability-cell supersessions$/,$p' SCORECARD.md | cat -A | grep '^| L27'`.

## Attack log

**A1 — C1's `record:` predicate is satisfiable for L29 by an unrelated block of the chosen blob (gameable in the one place the honest binding fails).** Reproduced in scratch clone `/fast/scratch/hyaku/souji-r31/C1BindD/cnt-trap` (base `1b81136`, origin removed):

```
# L29 bound to a blob that contains its own 18/18 in the matrix block
ITEM	L29	SCORECARD.md:170	literal=18/18	superseded	binding=record	MATCH	census/round-21/final-code-verification.json
SUMMARY items=1 bound_run=0 bound_record=1 unbound=0 mismatches=0 partial=1 rev=682ab74d03ac12153495dcd1add95351bf550ba6
rc=0

# L29 bound to the record the cell actually names
ITEM	L29	SCORECARD.md:170	literal=18/18	superseded	binding=record	RECORD-MISMATCH	census/round-21/remote-source-after.json
SUMMARY items=1 bound_run=0 bound_record=0 unbound=0 mismatches=1 partial=1 rev=7d20a3143beb85f0e7787a847dbdde9921bb1d2c
rc=1
```

The predicate only asks whether the literal occurs at digit boundaries anywhere in the blob, so a seat can reach `unbound=0 mismatches=0` for L29 by pointing at an `18/18` that belongs to the accepted matrix. That is the binding the preregistration forbids ("never bind to a file merely because grep found the digits"), and I did not write it. The refusal in the second control is byte absence and not shape: the counter's unchanged-blob check runs first, so `RECORD-MISMATCH` also proves `remote-source-after.json` is identical at base and rev. No amendment is proposed here (any amendment is stricter-only and the L1's to log).

## Deliveries

- `.ufo/waves/round-31/w1/deliver-c1-bind-L21-L29.md` — append block (sha256 `085c07c92a5d34494d55de7e89c95bf8c5dd3f314ebcd46950a1cbcd2469df2e`), per-item evidence, red-before and two-run proof receipts, L29 reproduced state and controls.
- `.ufo/waves/round-31/w1/SwarmExecutor04.md` — this report.
