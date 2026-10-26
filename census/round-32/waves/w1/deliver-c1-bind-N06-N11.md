# C1 bindings — items N06–N11 (seat SwarmExecutor02, souji r32 wave 1)

Revisions: lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`; preregistration (item list) `3ec84fc81b3243429c834a051880b0bcde06291c`; controls + amendment A0 `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`. Item source: `census/round-32/c1-items.tsv` rows N06–N11, all six on base `SCORECARD.md:159` (seat transcript audit).

## How the integers were produced

`git -C <lane> log -S'oracle2372' -- SCORECARD.md` names `4eb2fda51c9917abd734c7e411f98cbb59c5c0fe` (2026-10-21, "round-21: complete claims, independent oracle and scoped falsification evidence") as the commit that wrote line 159. Its diff rewrote the row to `r21 literal32/32 (base18/32), renderer4/4; oracle2372 keys over192 files, tp3/fp0/fn0; all401 old tuples identical; \`census/round-21/oracle-acceptance.json\``, and the same commit added `census/round-21/oracle-acceptance.json`, `census/round-21/oracle-acceptance.txt`, `census/round-21/read-root-oracle.tsv` and `census/round-21/count-read-root.py`.

The record states its own command on `census/round-21/oracle-acceptance.txt:1` (`python3 -B …/count-read-root.py --tool …/tools/souji-seat-audit.py --transcripts …/round-20/transcripts/final --transcripts …/recovery --transcripts …/recovery-final --oracle …/read-root-oracle.tsv --json …/oracle-acceptance.json`) and closes with `exit=0` on line 15. `census/round-21/count-read-root.py` builds that JSON: `files` counts the transcript `.txt` files scanned, `oracle.labelled` is the oracle key count, `tp`/`fp`/`fn` come from `selected & expected` set comparison, and it prints `print('PRIOR-VERDICTS\tcount=%d\tsha256=%s' % (len(preserved), record['prior_verdicts_sha256']))` — i.e. the cell's `401` is `len(prior_verdicts)`.

Base `SCORECARD.md:159` carries the verbatim sequence `oracle2372 keys over192 files, tp3/fp0/fn0; all401 old tuples identical` (verified with `git grep -F` at the base). The cited JSON at the base holds `"labelled": 2372`, `"files": 192`, and `oracle.tp=3`, `oracle.fp=0`, `oracle.fn=0`. `git diff --stat 85b61a1… HEAD` over `SCORECARD.md` and `census/round-21/oracle-acceptance.json` is empty, so both blobs are unchanged from base to the current tip (requirement for `field:`/`record:` paths).

Five items are therefore bound as `field:` on the cell's own cited evidence pointer; the sixth (401) has no expressible observable (see below).

## Rows (append verbatim, with the heading and header, after the base SCORECARD bytes)

```
### Round 32 capability-count bindings

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| N06 | SCORECARD.md:159 | oracle2372 keys | field: census/round-21/oracle-acceptance.json oracle.labelled=2372 | The r21 commit 4eb2fda wrote both this cell and census/round-21/oracle-acceptance.json from one count-read-root.py run, and oracle.labelled is the 2372 independently labelled read-call keys the cell quotes. |
| N07 | SCORECARD.md:159 | files 192 | field: census/round-21/oracle-acceptance.json files=192 | The same r21 JSON top-level files counter is the 192 corpus files the cell quotes over, from the same count-read-root.py measurement. |
| N08 | SCORECARD.md:159 | tp 3 | field: census/round-21/oracle-acceptance.json oracle.tp=3 | The cell's tp3 is the oracle true-positive count recorded in the same r21 JSON (oracle.tp=3) for the same 2372-key measurement. |
| N09 | SCORECARD.md:159 | fp 0 | field: census/round-21/oracle-acceptance.json oracle.fp=0 | The cell's fp0 is the oracle false-positive count recorded in the same r21 JSON (oracle.fp=0), a measured zero rather than an unmeasured absence. |
| N10 | SCORECARD.md:159 | fn 0 | field: census/round-21/oracle-acceptance.json oracle.fn=0 | The cell's fn0 is the oracle false-negative count recorded in the same r21 JSON (oracle.fn=0), same run and key set. |
| N11 | SCORECARD.md:159 | 401 tuples | withdrawn: No observable in the cited census/round-21/oracle-acceptance.json holds 401 as a JSON integer; the 401 old tuples survive only as the length of the prior_verdicts list plus a sha256 digest, while the text record that prints count=401 is oracle-acceptance.txt, a basename the base line does not cite. |
```

## Acceptance (measured, scratch clone with `origin` removed)

Private clone `/fast/scratch/hyaku/souji-r32/C1BindB/c` of the lane at `7a6667c…`, identity set with `git -C <scratch> config`, one commit `043b0b4090e0b7aef6d5c37644f5ba07681bbb18` appending only the block above.

`python3 -B census/round-32/c1-counter.py --root /fast/scratch/hyaku/souji-r32/C1BindB/c --rev 043b0b4090e0b7aef6d5c37644f5ba07681bbb18 --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only N06,N07,N08,N09,N10,N11 --scratch /fast/scratch/hyaku/souji-r32/C1BindB/cnt-v1`:

```
ITEM	N06	SCORECARD.md:159	literal=oracle2372 keys	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.labelled=2372
ITEM	N07	SCORECARD.md:159	literal=files 192	binding=field	MATCH	census/round-21/oracle-acceptance.json files=192
ITEM	N08	SCORECARD.md:159	literal=tp 3	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.tp=3
ITEM	N09	SCORECARD.md:159	literal=fp 0	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.fp=0
ITEM	N10	SCORECARD.md:159	literal=fn 0	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.fn=0
ITEM	N11	SCORECARD.md:159	literal=401 tuples	binding=withdrawn	WITHDRAWN	No observable in the cited census/round-21/oracle-acceptance.json holds 401 as a JSON integer; the 401 old tuples survive only as the length of the prior_verdicts list plus a sha256 digest, while the text record that prints count=401 is oracle-acceptance.txt, a basename the base line does not cite.
SUMMARY items=6 bound_run=0 bound_record=0 bound_field=5 withdrawn=1 unbound=0 mismatches=0 partial=1 rev=043b0b4090e0b7aef6d5c37644f5ba07681bbb18
```

exit 0. Same command with `census/round-32/c1-counter-v2.py` (amendment A0) and `--scratch …/cnt` prints the identical six ITEM lines and:

```
SUMMARY items=6 bound_run=0 bound_record=0 bound_field=5 withdrawn=1 unbound=0 mismatches=0 partial=1 rev=043b0b4090e0b7aef6d5c37644f5ba07681bbb18
```

exit 0. `partial=1` is the counter's own marker for `--only`.

## N11 withdrawal: the rejected alternatives, measured

Two candidates were built and run against the v2 counter in a separate scratch clone (`/fast/scratch/hyaku/souji-r32/C1BindB/alt`, base checked out, `origin` removed):

1. `record: census/round-21/oracle-acceptance.txt:5` (`PRIOR-VERDICTS count=401 sha256=…`) → `BAD-ROW(A0a-not-cited)`, `mismatches=1`, exit 1 at scratch rev `b405a8fff5da527a9a756fb9549607238167b0e5`. A0(a) requires the record basename to occur on the base line, and line 159 names only `oracle-acceptance.json`.
2. `field: census/round-21/oracle-acceptance.json prior_verdicts=401` → `BAD-ROW(field-shape)`, `mismatches=1`, exit 1 at scratch rev `684f96f3bf1c3c6d16d11eb89b8908aef44f596b` — the unit clause has no `all`/`tuples` in the basename or key, and `prior_verdicts` is a 401-element list, not a JSON integer.
3. Sweep for a digit-bounded `401` in the cited blob: `git cat-file blob 85b61a1…:census/round-21/oracle-acceptance.json` piped to `grep -n '\b401\b'` → no output (exit 1); the single `401` byte run in the file is interior to `prior_verdicts_sha256`. Scalar keys are `calls`, `classes.*`, `files`, `oracle.{extra,fn,fp,labelled,missing,tp}`, `read_root`; none holds 401.

The cell's `401` is not wrong (the list length really is 401); it is simply not observable as an integer in the cited evidence under the frozen rules, so `withdrawn` is the honest binding. It spends 1 of the round's 8.

## Key reservations for the L1

- `(census/round-21/oracle-acceptance.json, oracle.labelled)`, `(…, files)`, `(…, oracle.tp)`, `(…, oracle.fp)`, `(…, oracle.fn)` are consumed by N06–N10. A second item binding the same (path, key) turns both into `BAD-ROW(shared-occurrence)`.
- Base line 159 is the only SCORECARD line citing that basename (`grep -n 'oracle-acceptance'` over the base SCORECARD prints 159 alone), so no item other than N06–N11 can use this record at all.

## Limits

The five field bindings re-derive integers from committed bytes; they do not re-run `count-read-root.py`. A `run:` binding was unavailable: no `tools/` or `tests/fixtures/` basename stem occurs on line 159 (checked over all 234 such blobs at base), and `record:`/`run:` cannot cite a script under `census/`.
