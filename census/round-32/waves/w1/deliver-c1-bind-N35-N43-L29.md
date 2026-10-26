# Deliver — r32 C1 bindings N35-N43 and L29 (seat SwarmExecutor06)

Frozen contract: `census/round-32/records/preregistration.txt` (3ec84fc81b3243429c834a051880b0bcde06291c),
lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`. Environment: Python 3.14.8, git 2.56.0.

Revision note: the first cut bound N35/N36/N37 with `run:` rows. Critic A2
(`.ufo/waves/round-32/w1/SwarmCritic37.md`) is right that the counter writes only the *script* blob into the REV
clone, so those rows read `tools/souji-landing-gate.py` at REV — a path C2 owns (T02/T29/T30) — and a REV tool
edit flips them to `RUN-MISMATCH`. All three are now `record:` rows on unchanged r31 blobs, so nothing in this
delivery depends on REV tool bytes: `bound_run=0 bound_record=6 bound_field=1 withdrawn=3`.

## Rows to append (exact bytes, after the --base bytes of SCORECARD.md)

```
### Round 32 capability-count bindings

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| N35 | SCORECARD.md:423 | cases=10 | record: census/round-31/records/c2-after-v1.txt:22 | Line 22 is the r31 C2 counter's FIXTURE leg recording the cell's own fixture run, whose cases=10 the cell states. |
| N36 | SCORECARD.md:423 | pass=10 | record: census/round-31/records/c2-after-v2.txt:22 | The v2 run's FIXTURE line records the same fixture output, including pass=10. |
| N37 | SCORECARD.md:423 | cases=10 | record: census/round-31/records/c2-after-v3.txt:22 | The case total is arm-independent and the v3 FIXTURE line records cases=10 for that same fixture. |
| N38 | SCORECARD.md:423 | pass=3 | withdrawn: the base-gate arm's 3 is recorded only in census/round-31/records/c2-fixture-red-before.txt, which this base line does not cite, and that arm exits 1 | No A0-admissible observable shows this base-arm reading. |
| N39 | SCORECARD.md:423 | fp=0 | record: census/round-31/records/c2-after-v1.txt:28 | Line 28 is the r31 C2 counter's landing SUMMARY, whose fp=0 is the false-positive count this cell states. |
| N40 | SCORECARD.md:423 | real=2 | record: census/round-31/records/c2-after-v2.txt:29 | The v2 run's landing SUMMARY line records the same measurement with the SHIFT leg added, including real=2. |
| N41 | SCORECARD.md:423 | cne=0 | record: census/round-31/records/c2-after-v3.txt:30 | The v3 run's first landing SUMMARY line records cne=0 for that same measurement. |
| N42 | SCORECARD.md:423 | 495 | withdrawn: the item's only unit r26 contains a digit, so any literal naming that unit holds two digit runs and the frozen literal rule rejects it, leaving no representable observable | The counter cannot express this item's literal for any binding kind. |
| N43 | SCORECARD.md:424 | 17 RESULT | withdrawn: the 17 is a count of RESULT lines and no cited round-31 record puts 17 adjacent to a result word, so no A0-admissible observable shows it | The record measures this count, but the frozen adjacency rule cannot read it. |
| L29 | SCORECARD.md:170 | 18/18 remote-source-after.json | field: census/round-21/remote-source-after.json expected_command_count=18 matched_command_count=18 | The record's own two command counters are 18 and 18, exactly the 18/18 this cell states. |
```

Rows are mutually distinct: six `record` rows name six different `(path, line)` pairs (v1:22 / v2:22 / v3:22,
v1:28, v2:29, v3:30), the single `field` row names two keys of one unchanged JSON blob, and there is no `run:` row,
so no binding reads a file that any r32 seat may edit.

## Provenance (how each integer was produced)

| item | base line | integer | writing commit of the row | evidence read |
|---|---|---|---|---|
| N35, N36 | SCORECARD.md:423 | cases=10, pass=10 | f950267893340096964ae8ceb7116f6789d7c87b (r31) | cell names `tests/fixtures/r31-landing-gate-precision.py`; the r31 C2 counter's FIXTURE leg records its output |
| N37, N38 | SCORECARD.md:423 | cases=10, pass=3 | f950267893340096964ae8ceb7116f6789d7c87b (r31) | cell's base-tool arm; transcript `census/round-31/records/c2-fixture-red-before.txt:30` |
| N39-N42 | SCORECARD.md:423 | fp=0, real=2, cne=0, r26=495 | f950267893340096964ae8ceb7116f6789d7c87b (r31) | `census/round-31/records/c2-after-v1.txt:28`, `-v2.txt:29`, `-v3.txt:30`, `-v3.txt:60` |
| N43 | SCORECARD.md:424 | 17 | f950267893340096964ae8ceb7116f6789d7c87b (r31) | `census/round-31/records/jj-object-clock-run.txt` (17 RESULT lines) and `c3-after-c3-counter-v3.txt:9` |
| L29 | SCORECARD.md:170 | 18, 18 | row opened r21 (f7431d775ab8326bd3e82b1d1785866fb0064544); record added 4eb2fda51c9917abd734c7e411f98cbb59c5c0fe | `census/round-21/remote-source-after.json` `expected_command_count=18`, `matched_command_count=18` |

The cited record lines, read at base:

```
census/round-31/records/c2-after-v1.txt:22  FIXTURE rc=0 line='cases=10 pass=10 control=FALSE-GREEN-REJECTED' g1_g10_pass=True ok
census/round-31/records/c2-after-v2.txt:22  FIXTURE rc=0 line='cases=10 pass=10 control=FALSE-GREEN-REJECTED' g1_g10_pass=True ok
census/round-31/records/c2-after-v3.txt:22  FIXTURE rc=0 line='cases=10 pass=10 control=FALSE-GREEN-REJECTED' g1_g10_pass=True ok
census/round-31/records/c2-after-v1.txt:28  SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same rev=8024b540…
census/round-31/records/c2-after-v2.txt:29  SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok rev=8024b540…
census/round-31/records/c2-after-v3.txt:30  SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok rev=8024b540…
```

Blob identity checked read-only: `census/round-31/records/c2-fixture-red-before.txt` = d123b9ba at base and at
HEAD; `census/round-21/remote-source-after.json` = f4123cf1 at base and at HEAD. The six cited `record` blobs and
the L29 JSON were re-verified base-unchanged by the counter's own `record-not-unchanged-base-blob` leg, which
stayed silent for all seven rows. `SCORECARD.md` is byte-identical between base `85b61a15` and the current lane tip
`7a6667cd`, so the block appends cleanly.

## Acceptance (scratch clone, origin removed, own commit)

Scratch: `/fast/scratch/hyaku/souji-r32/C1BindF/` (`r.73SAs3/c`, `git rev-parse --show-toplevel` printed it;
scratch identity; commit `fb969674de644bb63de126ad43da57252afd24cb` = base bytes + the block above). Two v2 runs
byte-identical:

```
$ python3 -B census/round-32/c1-counter-v2.py --root <scratch>/r.73SAs3/c --rev fb969674de644bb63de126ad43da57252afd24cb \
    --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c \
    --only N35,N36,N37,N38,N39,N40,N41,N42,N43,L29 --scratch .../cnt
ITEM	N35	SCORECARD.md:423	literal=cases=10	binding=record	MATCH	census/round-31/records/c2-after-v1.txt:22
ITEM	N36	SCORECARD.md:423	literal=pass=10	binding=record	MATCH	census/round-31/records/c2-after-v2.txt:22
ITEM	N37	SCORECARD.md:423	literal=cases=10	binding=record	MATCH	census/round-31/records/c2-after-v3.txt:22
ITEM	N38	SCORECARD.md:423	literal=pass=3	binding=withdrawn	WITHDRAWN	the base-gate arm's 3 is recorded only in census/round-31/records/c2-fixture-red-before.txt, which this base line does not cite, and that arm exits 1
ITEM	N39	SCORECARD.md:423	literal=fp=0	binding=record	MATCH	census/round-31/records/c2-after-v1.txt:28
ITEM	N40	SCORECARD.md:423	literal=real=2	binding=record	MATCH	census/round-31/records/c2-after-v2.txt:29
ITEM	N41	SCORECARD.md:423	literal=cne=0	binding=record	MATCH	census/round-31/records/c2-after-v3.txt:30
ITEM	N42	SCORECARD.md:423	literal=495	binding=withdrawn	WITHDRAWN	the item's only unit r26 contains a digit, so any literal naming that unit holds two digit runs and the frozen literal rule rejects it, leaving no representable observable
ITEM	N43	SCORECARD.md:424	literal=17 RESULT	binding=withdrawn	WITHDRAWN	the 17 is a count of RESULT lines and no cited round-31 record puts 17 adjacent to a result word, so no A0-admissible observable shows it
ITEM	L29	SCORECARD.md:170	literal=18/18 remote-source-after.json	binding=field	MATCH	census/round-21/remote-source-after.json expected_command_count=18 matched_command_count=18
SUMMARY items=10 bound_run=0 bound_record=6 bound_field=1 withdrawn=3 unbound=0 mismatches=0 partial=1 rev=fb969674de644bb63de126ad43da57252afd24cb
EXIT=0
```

Same rows under the frozen v1 counter (`census/round-32/c1-counter.py`, same arguments): identical verdicts, same
`SUMMARY`, EXIT=0.

## The three withdrawals (each with its reproduced alternative)

1. **N38 `pass=3`** — the cell's base-gate arm. Rejected alternative:
   `record: census/round-31/records/c2-fixture-red-before.txt:30`, whose line 30 is
   `    cases=10 pass=3 control=FALSE-GREEN-REJECTED`. Diagnostic commit `a835df43ce82f70072bb8363b61a4b598a210d0d`:
   v1 prints `MATCH`, v2 prints `BAD-ROW(A0a-not-cited)` (`c2-fixture-red-before.txt` is not a token on base line
   423; the cell points at the `REDARM` line of `c2-after-v1.txt`, which lists per-case verdicts and carries no 3).
   A `run:` binding cannot reach it either: the fixture prints `pass=3` only against the r31 base gate
   (`9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`), whose committed copy is
   `census/round-30/waves/w1/deliver-souji-landing-gate.py` (sha256 `ba37e6bf…cd9056`), and that arm exits 1, so
   `MATCH iff exit 0` fails. Restating `pass=10` was refused: r31's restatement allowance covers a count that grew,
   not the other arm of the same fixture.
2. **N42 `495`** — item unit is `r26`, which itself contains a digit run. Any literal that satisfies `has_unit`
   (`r26` a substring) yields two or more integers, while the item has one; `r26495` satisfies the count but not
   the multiset. Reproduced on both counters with literal `r26=495` against
   `census/round-31/records/c2-after-v3.txt:60` (commit `690ba4fa51e3979b64ad58889705cfdce498a311`):
   `BAD-ROW(literal)` under v1 and v2 alike. Counter defect, not a seat preference; see the report's attack log.
3. **N43 `17`** — a count of `RESULT` lines. The measure exists in
   `census/round-31/records/c3-after-c3-counter-v3.txt:9` (`L8 PASS run_record=present results=17`) and in
   `census/round-31/records/amendments.txt:53` (`4 of 17 RESULT lines`), but the first fails A0(b) (the unit
   `result` is followed by `s` before `=17`) and the second fails A0(a) (`amendments.txt` is not cited on line 424).
   Reproduced at commit a835df43: v1 `MATCH`, v2 `BAD-ROW(A0a-not-cited)`. A `run:` of
   `tests/fixtures/r31-jj-object-clock.sh` prints RESULT lines only, none carrying 17.

Withdrawn total for this seat: 3 of the round's budget of 8 (preregistration target `withdrawn<=8`).

## Integration note for the L1

Append the row block verbatim after the current tip's SCORECARD.md bytes (append-only: the counter requires
`SCORECARD.md@REV` to start with the `--base` bytes). The `SCORECARD.md:<line>` cells are fixed at the frozen base
numbering (423, 424, 170) and must not be renumbered. No other file changes for C1, and no C1 row reads a r32-edited
file.
