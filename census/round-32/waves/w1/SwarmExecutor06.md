# SwarmExecutor06 — r32 w1, C1 bindings N35-N43 + L29

## Status

STATUS: PASS — the ten assigned items of `census/round-32/c1-items.tsv` carry one appended binding row each; under
the frozen v1 counter and under v2 (amendment A0) all ten read MATCH or WITHDRAWN:
`SUMMARY items=10 bound_run=0 bound_record=6 bound_field=1 withdrawn=3 unbound=0 mismatches=0`, exit 0, two v2 runs
byte-identical and v1 output identical to v2. Three items are withdrawn (N38, N42, N43) because no A0-admissible
observable exists for them; each carries its reproduced alternative. Frozen target `unbound=0 mismatches=0
withdrawn<=8` holds for this slice; 3 of the round's 8 withdrawal budget used.

No C1 row reads a file that an r32 seat may edit: the first cut used `run:` rows for N35/N36/N37 and was revised
after a critic note, because the counter writes only the *script* blob into the REV clone, so the fixture's
`--tool tools/souji-landing-gate.py` argument is REV bytes owned by C2.

## Evidence

Base rev `85b61a151923986e7e6b48f7084b9122561b5f3d`, prereg/list rev
`3ec84fc81b3243429c834a051880b0bcde06291c`. Python 3.14.8, git 2.56.0. Scratch clone
`/fast/scratch/hyaku/souji-r32/C1BindF/r.73SAs3/c` (origin removed; `rev-parse --show-toplevel` printed it), row
commit `fb969674de644bb63de126ad43da57252afd24cb`.

```
$ python3 -B census/round-32/c1-counter-v2.py --root <scratch> --rev fb969674... --base 85b61a15... \
    --list-rev 3ec84fc8... --only N35,N36,N37,N38,N39,N40,N41,N42,N43,L29 --scratch .../cnt
ITEM	N35	SCORECARD.md:423	literal=cases=10	binding=record	MATCH	census/round-31/records/c2-after-v1.txt:22
ITEM	N36	SCORECARD.md:423	literal=pass=10	binding=record	MATCH	census/round-31/records/c2-after-v2.txt:22
ITEM	N37	SCORECARD.md:423	literal=cases=10	binding=record	MATCH	census/round-31/records/c2-after-v3.txt:22
ITEM	N38	SCORECARD.md:423	literal=pass=3	binding=withdrawn	WITHDRAWN	...
ITEM	N39	SCORECARD.md:423	literal=fp=0	binding=record	MATCH	census/round-31/records/c2-after-v1.txt:28
ITEM	N40	SCORECARD.md:423	literal=real=2	binding=record	MATCH	census/round-31/records/c2-after-v2.txt:29
ITEM	N41	SCORECARD.md:423	literal=cne=0	binding=record	MATCH	census/round-31/records/c2-after-v3.txt:30
ITEM	N42	SCORECARD.md:423	literal=495	binding=withdrawn	WITHDRAWN	...
ITEM	N43	SCORECARD.md:424	literal=17 RESULT	binding=withdrawn	WITHDRAWN	...
ITEM	L29	SCORECARD.md:170	literal=18/18 remote-source-after.json	binding=field	MATCH	census/round-21/remote-source-after.json expected_command_count=18 matched_command_count=18
SUMMARY items=10 bound_run=0 bound_record=6 bound_field=1 withdrawn=3 unbound=0 mismatches=0 partial=1 rev=fb969674...
EXIT=0
```

The v1 counter (`census/round-32/c1-counter.py`, same arguments) prints byte-identical output (`diff` clean), so the
rows are not v2-specific. Two v2 runs are byte-identical as well.

Diagnostic commits in the same scratch clone (evidence for the withdrawals, never delivered):
`a835df43ce82f70072bb8363b61a4b598a210d0d` (N38/N43 bound to the red-before transcript / the D1 amendment) prints
`MATCH` under v1 and `BAD-ROW(A0a-not-cited)` under v2; `690ba4fa51e3979b64ad58889705cfdce498a311` (N42 bound with
literal `r26=495` against `c2-after-v3.txt:60`) prints `BAD-ROW(literal)` under v1 and v2.

## Findings

1. **N42 is unsatisfiable by construction (counter defect).** Item unit is `r26`; the literal rule needs a literal
   with exactly as many integers as the item (one) *and* containing that unit, but any literal containing `r26`
   yields two digit runs (`r26=495` → `['26','495']`). Reproduced under both counters:
   `ITEM N42 ... literal=r26=495 binding=record BAD-ROW(literal)`. No `record`, `field` or `run` shape escapes it;
   the only writable row is `withdrawn`. Location: `census/round-32/c1-items.tsv` row N42; rule in
   `census/round-32/c1-counter-v2.py` docstring ("the literal holds exactly as many integers as the item").
2. **N38's base-gate arm has no citable observable.** The cell (`SCORECARD.md:423`) points the base-tool reading at
   the `REDARM` line of `census/round-31/records/c2-after-v1.txt`, which carries per-case verdicts
   (`base_cases=[('G1','FAIL'),…]`), not the integer 3. The transcript that prints it,
   `census/round-31/records/c2-fixture-red-before.txt:30`, is not a token on line 423, so A0(a) rejects the record
   (`BAD-ROW(A0a-not-cited)`, commit a835df43). The `run:` route is closed too: the fixture prints `pass=3` only
   against the r31 base gate, whose committed copy is `census/round-30/waves/w1/deliver-souji-landing-gate.py`
   (sha256 `ba37e6bf…cd9056` = the fixture's REDARM key), and that arm exits 1 while `run` requires exit 0.
3. **A0(b) cannot read `results=17` for unit `result`.** The r31 C3 counter's own measure line,
   `census/round-31/records/c3-after-c3-counter-v3.txt:9` (`L8 PASS run_record=present results=17`), has the plural
   `s` between unit and `=`, so adjacency fails; the only line that satisfies adjacency,
   `census/round-31/records/amendments.txt:53` (`4 of 17 RESULT lines`), is not cited on base line 424 (A0(a)).
   N43 is therefore withdrawn; a `run:` of `tests/fixtures/r31-jj-object-clock.sh` prints RESULT lines only, none
   of which carries 17.
4. **`run:` rows are not REV-stable, so none were kept (critic A2, adopted).** `c1-counter-v2.py`'s `run()` writes
   only the base blob of the *script* into the REV clone (`with open(os.path.join(clone, sp), "wb")`), so the
   fixture's `--tool tools/souji-landing-gate.py` argument resolves to REV bytes — a path C2 owns (T02/T29/T30).
   A REV-side tool change flips those rows to `RUN-MISMATCH` (critic reproduction at scratch rev
   `ec3f2f2d2699`). N35/N36/N37 are now `record:` rows on unchanged r31 blobs
   (`census/round-31/records/c2-after-v1.txt:22`, `-v2.txt:22`, `-v3.txt:22`), which the counter pins by OID.
5. **Provenance of the two cells.** Both `SCORECARD.md:423` and `:424` were written by
   `f950267893340096964ae8ceb7116f6789d7c87b` (r31 close); `:170` was opened in r21
   (`f7431d775ab8326bd3e82b1d1785866fb0064544`) and its record `census/round-21/remote-source-after.json` added in
   `4eb2fda51c9917abd734c7e411f98cbb59c5c0fe`. `SCORECARD.md` is byte-identical between base and lane tip
   `7a6667cd`, so the append block lands unchanged.

## Attack log

Counter defect, reproduced (not a cheat — it blocks a bind, it does not let one through):

- **State:** scratch commit `690ba4fa51e3979b64ad58889705cfdce498a311` — one row
  `| N42 | SCORECARD.md:423 | r26=495 | record: census/round-31/records/c2-after-v3.txt:60 | … |`, with
  `census/round-31/records/c2-after-v3.txt:60` = `SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok …`.
- **Result:** v1 and v2 both print `ITEM N42 … binding=record BAD-ROW(literal)`, exit 1. The integer is correct and
  the record line states it verbatim; only the digit-bearing unit token defeats the literal rule. Fix (a later
  round, stricter-only rules forbid it now): count integers in the literal after removing the unit substring, or
  compare digit runs as a multiset against the item's integers.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-c1-bind-N35-N43-L29.md` — exact row block to append, provenance table, cited
  record lines, acceptance output (v2 twice, v1 identical), withdrawal evidence, integration note.
- `.ufo/waves/round-32/w1/SwarmExecutor06.md` — this report.

Hard bound: no file outside `souji-shokunin/.ufo/waves/round-32/w1/` was written; no `git add/commit/push/stash/
checkout/reset` and no `jj` in the lane; the only commits made were inside the scratch clone, which was removed
after the delivery was copied. No tooling was installed or upgraded. Scratch
`/fast/scratch/hyaku/souji-r32/C1BindF` deleted.
