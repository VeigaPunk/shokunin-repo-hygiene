# C1 capability-cell bindings — items L01-L07 (round 31, wave 1)

Seat: SwarmExecutor01. Claim C1 (calibration), axis calibration 7.
Base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`, prereg list-rev `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`,
enumeration `census/round-31/c1-cells.tsv`, counter `tools/souji-capability-cells.py` (frozen).
Lane tip at measurement `1b811368461785040e955f41f9c97e62f61fd67c`; `git diff --stat 9f17a1e 1b81136 -- SCORECARD.md`
is empty, so SCORECARD.md is bit-identical to base at the tip. Run bindings were executed by the counter in its
private `--no-local` clone at my scratch commit `b19a3510d22041e0d65ca0d3d9679c13f6aa25a4` (lane tip tree plus the
appended rows below; no other file differs).

## Rows to append (verbatim, after the base SCORECARD bytes)

```
### Round 31 capability-cell supersessions

| item | base line | literal | binding | reason |
|---|---|---|---|---|
| L01 | SCORECARD.md:152 | 6/6 | run: bash tests/fixtures/r12-maintenance-guard.sh --selftest | Written at d7266c5 together with `tests/results/r12-maintenance-guard.txt`, whose selftest run records `selftest=PASS ids=6/6`, and the same command re-run at the revision still prints ids=6/6. |
| L02 | SCORECARD.md:153 | 36/36 | run: python3 tools/souji-cert-evidence.py --selftest | Written at 23014d4 with the `evidence-selftest` entry of `census/round-13/verification.json`, and the same command re-run at the revision still prints 36/36 passed. |
| L03 | SCORECARD.md:153 | 5/5 | record: census/round-13/verification.json | Written at 23014d4, whose `evidence-external-fixture` entry runs `tests/fixtures/r13-cert-evidence.py` and records the stdout line `fixture: 5/5 checks passed` that the cell's "external fixture 5/5" restates. |
| L04 | SCORECARD.md:154 | total=5 failed=0 | run: bash tests/fixtures/r13-quarantine-bounds.sh | Written at 23014d4 citing the `quarantine-bounds` entry of `census/round-13/verification.json`, and the same command re-run at the revision prints `SUMMARY total=5 failed=0`, the fixture's own notation for the cell's 5/5. |
| L05 | SCORECARD.md:155 | ids=7/7 | run: bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh | Written at 23014d4 citing the `structure-selftest` entry of `census/round-13/verification.json` as ids=5/5, and the same command re-run at the revision prints ids=7/7, the grown count restated in the fixture's notation. |
| L06 | SCORECARD.md:158 | pass=65 fail=0 | run: python3 tools/souji-landing-gate.py --selftest | Written at 163158a as 18/18; the only committed round-16 mentions of that count are under census/round-16/transcripts/, which the record rule excludes, so the re-run at the revision that prints `SELFTEST pass=65 fail=0` is the row observable. |
| L07 | SCORECARD.md:158 | total=15 failed=0 | run: python3 tests/fixtures/r16-landing-gate.py | Written at 163158a as 15/15; the count appears in no committed census/round-16 record outside transcripts/, and the same command re-run at the revision prints `SUMMARY total=15 failed=0`, the fixture's own notation for the unchanged 15/15. |
```

## Provenance: how each base literal was produced

`git blame 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc -L152,158 -- SCORECARD.md` gives the writing commit per line:
152 `d7266c5` (r12), 153-155 `23014d4` (r13), 158 `163158a` (r16). `git log -S` on each cell phrase names the same
commits.

| item | base line | base literal | writing commit | record the writing round committed and the cell cites | re-run at measured rev |
|---|---|---|---|---|---|
| L01 | 152 | 6/6 | d7266c5 | `tests/results/r12-maintenance-guard.txt` (blob `03c3d11` at d7266c5 and at base) holds `selftest=PASS ids=6/6` | rc=0, `selftest=PASS ids=6/6` (unchanged) |
| L02 | 153 | 36/36 | 23014d4 | `census/round-13/verification.json` entry `evidence-selftest` records the 36/36 selftest summary | rc=0, `selftest: 36/36 passed` (unchanged) |
| L03 | 153 | 5/5 | 23014d4 | `census/round-13/verification.json:57` entry `evidence-external-fixture`: its command is `python3 tests/fixtures/r13-cert-evidence.py` and its stdout ends `fixture: 5/5 checks passed` | record binding; blob `879d96b` identical at base and at measured rev |
| L04 | 154 | 5/5 | 23014d4 | same record, entry `quarantine-bounds`, stdout ends `SUMMARY total=5 failed=0 hung=0` | rc=0, `SUMMARY total=5 failed=0 hung=0` (restated) |
| L05 | 155 | 5/5 | 23014d4 | same record, entry `structure-selftest`, stdout ends `selftest=PASS ids=5/5` | rc=0, `selftest=PASS ids=7/7` (grew from 5/5) |
| L06 | 158 | 18/18 | 163158a | no non-transcript record under `census/round-16/` carries 18/18 (sweep below); the cell points at the Gate replays in `corpus/lessons/round-16.md` | rc=0, `SELFTEST pass=65 fail=0` (grew from 18/18) |
| L07 | 158 | 15/15 | 163158a | same sweep: no non-transcript `census/round-16/` record carries 15/15 | rc=0, `SUMMARY total=15 failed=0` (restated, count unchanged) |

Why the r13 record IS the evidence (not a grep hit): it was committed by the same writing commit `23014d4` that
wrote cells 153-155, it holds the argv actually run for each fixture and the stdout of that run, and it is the path
the cells themselves cite. Record entries at base: `evidence-selftest` (line 17), `evidence-external-fixture`
(line 49), `structure-selftest` (line 63), `quarantine-bounds` (line 97).

Round-16 negative sweep for L06/L07:

```
$ git grep -l -E '(^|[^0-9])(18/18|15/15)([^0-9]|$)' 9f17a1e -- census/round-16/ | grep -v '/transcripts/'
(no output; rc=1)
```

## L03 has no run binding: negative probe

A `run:` row for L03 would have to re-run the script whose output is 5/5, `tests/fixtures/r13-cert-evidence.py`.
Its stem is absent from the base cell, so the frozen counter refuses that forced row:

```
$ git show 9f17a1e:SCORECARD.md | sed -n '153p' | grep -c 'r13-cert-evidence'
0
$ python3 -B tools/souji-capability-cells.py --root <scratch c1x> --rev 9a51467f65e996223f1cbeb73dca894d6da60942 \
    --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --only L03
ITEM	L03	SCORECARD.md:153	literal=5/5	superseded	binding=run	BAD-ROW(run-shape)	python3 tests/fixtures/r13-cert-evidence.py
SUMMARY items=1 bound_run=0 bound_record=0 unbound=0 mismatches=1 partial=1 rev=9a51467f65e996223f1cbeb73dca894d6da60942
```

The script whose stem IS on the cell, `tools/souji-cert-evidence.py`, prints 36/36 for its selftest (L02) and no
5/5. So the record binding is the only honest one for L03, not a preference.

## Acceptance in a scratch clone

```
$ D=/fast/scratch/hyaku/souji-r31/C1BindA/c1
$ git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin "$D"; git -C "$D" remote remove origin
$ git -C "$D" rev-parse --show-toplevel
/fast/scratch/hyaku/souji-r31/C1BindA/c1
$ (append the row block above to SCORECARD.md; git -C "$D" add SCORECARD.md; git -C "$D" commit)
$ git -C "$D" rev-parse HEAD
b19a3510d22041e0d65ca0d3d9679c13f6aa25a4
```

Run 1 and run 2 are byte-identical (`diff` empty), both exit 0:

```
$ python3 -B tools/souji-capability-cells.py --root /fast/scratch/hyaku/souji-r31/C1BindA/c1 \
    --rev b19a3510d22041e0d65ca0d3d9679c13f6aa25a4 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc \
    --list-rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --only L01,L02,L03,L04,L05,L06,L07 \
    --scratch /fast/scratch/hyaku/souji-r31/C1BindA/cnt
ITEM	L01	SCORECARD.md:152	literal=6/6	superseded	binding=run	MATCH	bash tests/fixtures/r12-maintenance-guard.sh --selftest rc=0 observed=selftest=PASS ids=6/6
ITEM	L02	SCORECARD.md:153	literal=36/36	superseded	binding=run	MATCH	python3 tools/souji-cert-evidence.py --selftest rc=0 observed=selftest: 36/36 passed
ITEM	L03	SCORECARD.md:153	literal=5/5	superseded	binding=record	MATCH	census/round-13/verification.json
ITEM	L04	SCORECARD.md:154	literal=total=5 failed=0	superseded	binding=run	MATCH	bash tests/fixtures/r13-quarantine-bounds.sh rc=0 observed=SUMMARY total=5 failed=0 hung=0
ITEM	L05	SCORECARD.md:155	literal=ids=7/7	superseded	binding=run	MATCH	bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh rc=0 observed=selftest=PASS ids=7/7
ITEM	L06	SCORECARD.md:158	literal=pass=65 fail=0	superseded	binding=run	MATCH	python3 tools/souji-landing-gate.py --selftest rc=0 observed=SELFTEST pass=65 fail=0
ITEM	L07	SCORECARD.md:158	literal=total=15 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r16-landing-gate.py rc=0 observed=SUMMARY total=15 failed=0
SUMMARY items=7 bound_run=6 bound_record=1 unbound=0 mismatches=0 partial=1 rev=b19a3510d22041e0d65ca0d3d9679c13f6aa25a4
```

Second invocation, same argv, same rev:

```
ITEM	L01	SCORECARD.md:152	literal=6/6	superseded	binding=run	MATCH	bash tests/fixtures/r12-maintenance-guard.sh --selftest rc=0 observed=selftest=PASS ids=6/6
ITEM	L02	SCORECARD.md:153	literal=36/36	superseded	binding=run	MATCH	python3 tools/souji-cert-evidence.py --selftest rc=0 observed=selftest: 36/36 passed
ITEM	L03	SCORECARD.md:153	literal=5/5	superseded	binding=record	MATCH	census/round-13/verification.json
ITEM	L04	SCORECARD.md:154	literal=total=5 failed=0	superseded	binding=run	MATCH	bash tests/fixtures/r13-quarantine-bounds.sh rc=0 observed=SUMMARY total=5 failed=0 hung=0
ITEM	L05	SCORECARD.md:155	literal=ids=7/7	superseded	binding=run	MATCH	bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh rc=0 observed=selftest=PASS ids=7/7
ITEM	L06	SCORECARD.md:158	literal=pass=65 fail=0	superseded	binding=run	MATCH	python3 tools/souji-landing-gate.py --selftest rc=0 observed=SELFTEST pass=65 fail=0
ITEM	L07	SCORECARD.md:158	literal=total=15 failed=0	superseded	binding=run	MATCH	python3 tests/fixtures/r16-landing-gate.py rc=0 observed=SUMMARY total=15 failed=0
SUMMARY items=7 bound_run=6 bound_record=1 unbound=0 mismatches=0 partial=1 rev=b19a3510d22041e0d65ca0d3d9679c13f6aa25a4
```

## Effect on the full 41-item enumeration and isolation

Full counter, same rev, no `--only`:

```
SUMMARY items=41 bound_run=11 bound_record=1 unbound=21 mismatches=29 rev=b19a3510d22041e0d65ca0d3d9679c13f6aa25a4
```

Base full run at lane tip `1b811368461785040e955f41f9c97e62f61fd67c` (no rows) reproduces the frozen control
exactly: `SUMMARY items=41 bound_run=7 bound_record=0 unbound=22 mismatches=34`. Delta over my rows: +4 run
(L04-L07), +1 record (L03), unbound 22->21, mismatches 34->29 (=5 closed). The other 34 ITEM lines (L08-L41) are
byte-identical between the two full runs (`diff` empty, 34 lines each), so these rows touch nothing outside L01-L07.
Expected remaining after integration: 29 mismatches across L08-L29 (+ L28/L29 record rows still to come from other
seats).

## Risks for the L1

1. L06/L07 restate counts printed by `tools/souji-landing-gate.py --selftest` and `tests/fixtures/r16-landing-gate.py`.
   They stay MATCH only while C2's REGRESS leg keeps both commands' (rc, last line) byte-equal, as the
   preregistration requires; a C2 change that grows the selftest count invalidates both rows and needs a restated
   literal at the landing commit.
2. The counter keys supersession rows by item id and the LAST row in the appended tail wins (`sup[id] = ...`). If
   any other seat appends a row for L01-L07, that later row decides.
3. L04/L05 restate the cell literal (`total=5 failed=0`, `ids=7/7`); the claim's per-revision obligation must be
   re-run at the C1 landing commit and at the final tip, not only here.
4. No tool installs, no upgrades, no pacman transaction. Scratch removed after this delivery was copied.
