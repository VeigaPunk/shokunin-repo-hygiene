# SwarmExecutor02 — C1 bindings for N06–N11 (souji r32, wave 1)

## Status

STATUS: PASS — all six assigned items accept under both C1 counters (v1 and v2/A0): five `field:` MATCH, one `withdrawn` with the two alternative bindings measured and rejected; item-level result `unbound=0 mismatches=0 withdrawn=1`.

## Evidence

Revisions: base `85b61a151923986e7e6b48f7084b9122561b5f3d`, item list `3ec84fc81b3243429c834a051880b0bcde06291c`, controls+A0 `7a6667cd27652baf8d704b5cdb8e3200bd6e27a1`, proof commit in my scratch clone `043b0b4090e0b7aef6d5c37644f5ba07681bbb18`.

1. Production trail. `git -C <lane> log -S'oracle2372' --format='%H %ad %s' -- SCORECARD.md` → `4eb2fda51c9917abd734c7e411f98cbb59c5c0fe 2026-10-21 round-21: complete claims, independent oracle and scoped falsification evidence`. That commit's SCORECARD hunk wrote line 159 (`… oracle2372 keys over192 files, tp3/fp0/fn0; all401 old tuples identical; \`census/round-21/oracle-acceptance.json\``) and added the cited JSON, its text twin and `census/round-21/count-read-root.py`.
2. Record self-description: `census/round-21/oracle-acceptance.txt:1` is the producing command (`count-read-root.py --tool …/tools/souji-seat-audit.py --transcripts …/final …/recovery …/recovery-final --oracle …/read-root-oracle.tsv --json …/oracle-acceptance.json`), `:15` is `exit=0`.
3. Byte checks at base: `git grep -F '"labelled": 2372'` and `'"files": 192'` hit `census/round-21/oracle-acceptance.json`; `git grep -F "oracle2372 keys over192 files, tp3/fp0/fn0; all401 old tuples identical"` hits `SCORECARD.md`.
4. Blob stability: `git -C <lane> diff --stat 85b61a1… HEAD -- SCORECARD.md census/round-21/oracle-acceptance.json` → empty, so `field:` paths are the same blob at base and REV-as-tip.
5. Counter, v1 (`--root <scratch clone> --rev 043b0b4… --base 85b61a1… --list-rev 3ec84fc… --only N06,N07,N08,N09,N10,N11 --scratch …/cnt-v1`), exit 0:

```
ITEM	N06	SCORECARD.md:159	literal=oracle2372 keys	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.labelled=2372
ITEM	N07	SCORECARD.md:159	literal=files 192	binding=field	MATCH	census/round-21/oracle-acceptance.json files=192
ITEM	N08	SCORECARD.md:159	literal=tp 3	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.tp=3
ITEM	N09	SCORECARD.md:159	literal=fp 0	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.fp=0
ITEM	N10	SCORECARD.md:159	literal=fn 0	binding=field	MATCH	census/round-21/oracle-acceptance.json oracle.fn=0
ITEM	N11	SCORECARD.md:159	literal=401 tuples	binding=withdrawn	WITHDRAWN	No observable in the cited census/round-21/oracle-acceptance.json holds 401 as a JSON integer; …
SUMMARY items=6 bound_run=0 bound_record=0 bound_field=5 withdrawn=1 unbound=0 mismatches=0 partial=1 rev=043b0b4090e0b7aef6d5c37644f5ba07681bbb18
```

6. Same command with `census/round-32/c1-counter-v2.py` (A0) → identical six ITEM lines and the identical `SUMMARY … unbound=0 mismatches=0`, exit 0. `partial=1` is the counter's own `--only` marker.

## Findings

1. **N06–N10 bind to the cell's own cited JSON.** `census/round-21/oracle-acceptance.json` (unchanged base→tip) holds `oracle.labelled=2372`, `files=192`, `oracle.tp=3`, `oracle.fp=0`, `oracle.fn=0`; `census/round-21/count-read-root.py` computes `files` as the scanned transcript count, `oracle.labelled` as the oracle key count, and tp/fp/fn from `selected & expected`. Each integer sits in the same round-21 record the cell quotes, so the binding is the row's evidence and not a digit coincidence.
2. **N11 is not expressible as evidence.** The cell's `401` is `len(prior_verdicts)` — the counter tool prints it via `print('PRIOR-VERDICTS\tcount=%d\tsha256=%s' % (len(preserved), record['prior_verdicts_sha256']))` (`census/round-21/count-read-root.py`). The text record that prints `count=401` is `census/round-21/oracle-acceptance.txt:5`, but A0(a) requires the record basename on the base line and line 159 names only the `.json`. Measured alternatives: `record: census/round-21/oracle-acceptance.txt:5` → `BAD-ROW(A0a-not-cited)` (scratch rev `b405a8fff5da527a9a756fb9549607238167b0e5`, exit 1); `field: … prior_verdicts=401` → `BAD-ROW(field-shape)` (scratch rev `684f96f3bf1c3c6d16d11eb89b8908aef44f596b`, exit 1; `prior_verdicts` is a list and the unit clause has no `all`/`tuples`). Sweep: `git cat-file blob 85b61a1…:census/round-21/oracle-acceptance.json | grep -n '\b401\b'` → no match; the only `401` byte run lies inside `prior_verdicts_sha256`. The integer is correct; only its observability fails, so `withdrawn` is honest and spends 1 of the 8. A0(a)'s basename-only test is the specific cost: it cannot see a text sibling of a cited JSON, and no stricter-only amendment could repair that.
3. **Key reservations for the L1.** `(census/round-21/oracle-acceptance.json, oracle.labelled | files | oracle.tp | oracle.fp | oracle.fn)` are consumed by N06–N10; any second item on the same `(path,key)` would make both `BAD-ROW(shared-occurrence)`. Line 159 is the only base SCORECARD line citing that basename (`grep -n 'oracle-acceptance'` → `159:` alone), so no other item can use the record.
4. **No `run:` binding was available for this cell**: over all 234 blobs under `tools/` and `tests/fixtures/` at base, none has a basename stem occurring on line 159, and neither `run:` nor `record:` may cite a script under `census/`.
5. **Tooling**: nothing installed or upgraded this seat (no channel used); all work ran with `python3 -B` and git plumbing from the lane and a `--no-local` scratch clone.

## Attack log

Not an attack seat. No attack filed: the counter is not gameable in the direction I touched — A0 is stricter than the evidence surface needs for `N11`, and tightening it further cannot help. Reported as finding 2 instead.

## Deliveries

- `.ufo/waves/round-32/w1/deliver-c1-bind-N06-N11.md` — the exact append block (heading, header, six rows), the v1 and v2 acceptance output, the measured rejection of both N11 alternatives, key reservations and limits.
