# C1 bindings N12–N19 (round 32, wave 1) — delivery

Eight rows for `census/round-32/c1-items.tsv` items N12–N19. Accepted at scratch rev
`5c14cad06f52beb2ce898a9e5b5dae28fd08c650` (lane base `85b61a151923986e7e6b48f7084b9122561b5f3d`,
list-rev `3ec84fc81b3243429c834a051880b0bcde06291c`) by **both** counters with rc=0:
`SUMMARY items=8 bound_run=3 bound_record=1 bound_field=0 withdrawn=4 unbound=0 mismatches=0`.

## Insert — append verbatim to SCORECARD.md

```markdown

### Round 32 capability-count bindings

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| N12 | SCORECARD.md:161 | failed=0 | run: bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools | Line 161 quotes that exact command; re-run now its SUMMARY prints failed=0, the 13 being the same SUMMARY's failed count with the 5fa6017 tool dir, so the count is restated. |
| N13 | SCORECARD.md:165 | 19 leaks | withdrawn: the only cited occurrence base_leaks=19 sits on reason-after.txt line 29, which N14 already binds, and the counter forbids a shared occurrence |
| N14 | SCORECARD.md:165 | leaks=0 | record: census/round-21/reason-after.txt:29 | reason-after.txt is the record line 165 cites, and its SUMMARY reports the repaired count leaks=0 beside base_leaks=19, the 19 to 0 the cell states. |
| N15 | SCORECARD.md:168 | 18 step | withdrawn: the 18 steps live in census/round-21/step-inventory.json, whose basename line 168 never cites, and no line-named script prints them |
| N16 | SCORECARD.md:168 | base_discriminating=12 | run: python3 -B tests/fixtures/r19-seat-audit-shapes.py | Line 168's r19-seat-audit-shapes17/0 (base12) is this fixture's own SUMMARY, and re-running it now prints base_discriminating=12. |
| N17 | SCORECARD.md:168 | 11 base | withdrawn: the 11 needs the pre-r20 auditor passed as --base-tool, no committed copy of it exists, and line 168 cites no round-20 record |
| N18 | SCORECARD.md:175 | 2 base | withdrawn: census/round-24/records/c2-control-base.tsv line 11 holds mismatches=2 but never the word base, so the A0(b) adjacency the unit demands cannot hold |
| N19 | SCORECARD.md:175 | mismatches=0 | run: python3 -B tools/souji-coverage-agreement.py --root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c | Line 175's c2-after.tsv (0) is this tool's counts line at that rev, and re-running that same argv now prints mismatches=0. |
```

## Acceptance — counter output at the scratch rev

`python3 -B census/round-32/c1-counter-v2.py --root <scratch clone> --rev 5c14cad06f52beb2ce898a9e5b5dae28fd08c650 --base 85b61a151923986e7e6b48f7084b9122561b5f3d --list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --only N12,N13,N14,N15,N16,N17,N18,N19 --scratch <scratch>/cnt`

```
ITEM	N12	SCORECARD.md:161	literal=failed=0	binding=run	MATCH	bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools rc=0 observed=SUMMARY total=35 failed=0 skipped=2
ITEM	N13	SCORECARD.md:165	literal=19 leaks	binding=withdrawn	WITHDRAWN	the only cited occurrence base_leaks=19 sits on reason-after.txt line 29, which N14 already binds, and the counter forbids a shared occurrence
ITEM	N14	SCORECARD.md:165	literal=leaks=0	binding=record	MATCH	census/round-21/reason-after.txt:29
ITEM	N15	SCORECARD.md:168	literal=18 step	binding=withdrawn	WITHDRAWN	the 18 steps live in census/round-21/step-inventory.json, whose basename line 168 never cites, and no line-named script prints them
ITEM	N16	SCORECARD.md:168	literal=base_discriminating=12	binding=run	MATCH	python3 -B tests/fixtures/r19-seat-audit-shapes.py rc=0 observed=SUMMARY total=17 failed=0 base_discriminating=12
ITEM	N17	SCORECARD.md:168	literal=11 base	binding=withdrawn	WITHDRAWN	the 11 needs the pre-r20 auditor passed as --base-tool, no committed copy of it exists, and line 168 cites no round-20 record
ITEM	N18	SCORECARD.md:175	literal=2 base	binding=withdrawn	WITHDRAWN	census/round-24/records/c2-control-base.tsv line 11 holds mismatches=2 but never the word base, so the A0(b) adjacency the unit demands cannot hold
ITEM	N19	SCORECARD.md:175	literal=mismatches=0	binding=run	MATCH	python3 -B tools/souji-coverage-agreement.py --root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c rc=0 observed=grounded=6 mapped=6 dangling=0 mismatches=0
SUMMARY items=8 bound_run=3 bound_record=1 bound_field=0 withdrawn=4 unbound=0 mismatches=0 partial=1 rev=5c14cad06f52beb2ce898a9e5b5dae28fd08c650
EXIT=0
```

`census/round-32/c1-counter.py` (v1) with the same arguments prints the same eight ITEM lines and
`SUMMARY items=8 bound_run=3 bound_record=1 bound_field=0 withdrawn=4 unbound=0 mismatches=0`,
EXIT=0. The same eight rows were run twice under v2 (rev `34655dcb27b45a26aaaf30058b2499ea820f0d13`
and the rev above) with identical verdicts.

## Why each line is the row's evidence

| item | integer the cell states | how that integer was produced |
|---|---|---|
| N12 | `(5fa6017 tools: 13 fail)` — SCORECARD.md:161 | `census/round-17/jj-receipts-base5fa6017.txt:51` reads `SUMMARY	total=33	failed=13	skipped=2`, the fixture run against the 5fa6017 tool dir. That line is refused by A0(b) (`failed=13` puts two alphanumerics between `fail` and `13`), so the binding is the cell's own quoted command re-run; it now prints `failed=0` and the count is restated (v1 docstring allows a restated run count). |
| N13 | `leaks19→0` — SCORECARD.md:165 | `census/round-21/reason-after.txt:29` reads `SUMMARY	total=27	pass=27	fail=0	leaks=0	base_leaks=19	max_reason_bytes=160`: the 19 is `base_leaks`, the 0 is `leaks`. Both integers sit on that one line, and the counter binds one occurrence to one item, so N13 is withdrawn and N14 takes it (`leaks=0`, the after count of the file the cell cites). Swapping the pair is equivalent for the counter; binding both is `BAD-ROW(shared-occurrence)` for both (reproduced). |
| N14 | `leaks19→0` — SCORECARD.md:165 | same line 29; `leaks=0` is the file's own after measurement. |
| N15 | `18-step receipts` — SCORECARD.md:168 | `census/round-21/step-inventory.json` holds exactly 18 steps (`len(d["steps"])==18`) but line 168 names no path, so it is refused by A0(a); no script named on the line prints a step count. Withdrawn. |
| N16 | `(base12)` — SCORECARD.md:168 | `python3 -B tests/fixtures/r19-seat-audit-shapes.py` ends `SUMMARY	total=17	failed=0	base_discriminating=12`; the cell's `r19-seat-audit-shapes17/0 (base12)` is that SUMMARY. The run literal is the same token, unchanged. |
| N17 | `(base11)` — SCORECARD.md:168 | `census/round-21/r20-closure-excerpt.json:40` says `r20-audit-contract 78/78/0 base_discriminating=11`, but line 168 names no path (A0a) and the token `base_discriminating=11` is refused by A0(b) anyway. No committed copy of the pre-r20 auditor exists, so the run cannot pass `--base-tool`. Withdrawn. |
| N18 | `(2 at base)` — SCORECARD.md:175 | `census/round-24/records/c2-control-base.tsv:11` reads `grounded=4 mapped=2 dangling=0 mismatches=2`; the file contains the word `base` zero times, so A0(b) adjacency for the unit `base` cannot hold. Withdrawn. |
| N19 | `c2-after.tsv` (0) — SCORECARD.md:175 | `c2-after.tsv:5` records the argv `--root . --rev 778747eb671f8e85ef5387bc3d7023337b30467c` and `:9` the counts `grounded=6 mapped=6 dangling=0 mismatches=0`; the unitless item cannot use `record:`, so the binding re-runs that exact argv and reads `mismatches=0`. |

## Residual risk for integration

N12's and N16's runs execute the **base** fixture blob but read files at REV: N12 reads
`tools/souji-verify.sh` (a C2 item, T15), N16 reads `tools/souji-seat-audit.py` (C2 item, T10). C2 must
leave their behaviour identical; re-run the C1 counter at the integrated tip to confirm both stay
`MATCH`.
