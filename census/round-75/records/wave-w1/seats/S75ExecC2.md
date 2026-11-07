# S75ExecC2 — C2 falsification (r75), seat of SoujiR75 wave

Verdict items:
- Pristine r75 selftest: REPRODUCED — `SELFTEST cases=64 pass=64 fail=0 EXIT=0`; both r75 checks ok (`witness run (r75)` unwitnessed=[], `witness (r75)` base_unwitnessed=1/new_unwitnessed=1).
- X09: REPRODUCED — fail=1 (`witness (r75)` new_unwitnessed=0) EXIT=1, matches records/c2-after-X09-selftest.txt.
- P1 (X15 then M17): REPRODUCED — fail=1 (`witness run (r75)` unwitnessed=[AS2,FC2,FM2]) EXIT=1, matches records/c2-after-P1-selftest.txt. X15 alone SURVIVED (fail=0) as prereg states (not a target).
- M08/M14/M15/M17: REPRODUCED — fail=1/1/2/2, matching records/c2-after-*.txt and M17 fail=2 (both witness-run detectors kill it).
- Tally: `c2-kill-counter.py` over my receipts → `SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS EXIT=0`, identical to records/c2-after.txt. Do-nothing r74 control confirmed: killed=4, X09/P1 SURVIVED, EXIT=1.
- Diff r74→r75 c1-counter.py: only docstring + two selftest blocks changed (3 hunks); no evaluate()/verdict change. Verified by `diff -u` (37 lines).

Attack results (my edits via apply-edit.py, single-occurrence asserts passed):
- Y1 (n_pre unscoped, n_post scoped): KILLED — same `witness (r75)` fail as X09 (new_unwitnessed=0).
- Y2 (n_post unscoped, n_pre scoped): KILLED — same fail, same counts.
- Y3 (`row_scope(CASE_SPECS["FC2"],...)` cross-row): CRASH — `KeyError: 'FC2'` in stub two-row sub-run (CASE_SPECS filtered to 2 rows); no SELFTEST line, rc=1 via traceback. Detector does not kill it; it crashes. Not a coverage gap in r78 sense, but the X09-style scoping fault, when built cross-row, is not caught by a clean FAIL.
- Y3b (`CASE_SPECS["FM1"]` cross-row): CRASH — `KeyError: 'FM1'` likewise.
- Y3c (new slot scoped to empty set): KILLED — fail=2 (witness-run both checks).
- Y3d (new slot scoped to counter.py only): KILLED — fail=2 (FM1/FM2 notes rows unwitnessed).
- Y4 (`n_wit` post-only): SURVIVED — fail=0. In the witness-run fixture the forgery persists post-run, so post-only still witnesses. This is the mirror of M17 (pre-only); the r75 second detector only covers pre-only, not post-only. Symmetric fault uncovered. [MEDIUM]
- Y5 (row_fate witness=b_wit): SURVIVED — fail=0. In the fixture b_wit≡n_wit (both true), so swapping the recorded witness is invisible to every selftest check incl. the r75 second detector. Second detector reads row_fate, but row_fate can be trivially aliased to the base witness with no check noticing. [MEDIUM]

Commands run (from lane root):
- `python3 -B census/round-73/apply-edit.py --set census/round-75/c2-mutants.json --id X09|X15 --src census/round-75/c1-counter.py --out $S/mut/<id>.py` (+ r74 set for M08/M14/M15/M17, + X15→M17 chain for P1; + attack sets Y1–Y5/Y3c–Y3d)
- `python3 -B <counter> --selftest --root . --matrix census/round-73/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --work $S/work-<id>` for pristine, X09, X15, P1, M08, M14, M15, M17, Y1, Y2, Y4, Y5, Y3c, Y3d ($S=/fast/scratch/hyaku/souji-r75/S75ExecC2)
- `python3 -B census/round-75/c2-kill-counter.py --pristine $S/receipts/pristine.stdout --mutant X09=... --mutant P1=... --mutant M08=... --mutant M14=... --mutant M15=... --mutant M17=...`

Observed deciding lines:
- `SELFTEST cases=64 pass=64 fail=0` (pristine), `SELFTEST cases=64 pass=63 fail=1` (X09, P1), `SELFTEST cases=64 pass=62 fail=2` (M15, M17)
- `SUMMARY mutants=6 killed=6 survived=0 unread=0 pristine=PASS`

Files written: this report only (under .ufo/waves/round-75/w1/S75ExecC2.md); scratch under /fast/scratch/hyaku/souji-r75/S75ExecC2/ (mutants, receipts, work dirs; cleaned work-* dirs, mutants/receipts retained in scratch then dir removed per discipline).

Findings: [MEDIUM] Y4 — post-only new-slot witness survives; r75 second detector covers pre-only (M17) only. [MEDIUM] Y5 — row_fate witness aliased to base witness survives; second detector blind to it. [LOW] Cross-row row_scope faults (Y3/Y3b) crash rather than FAIL, so the X09 detector's kill signal is a traceback, not a clean FAIL. No mismatch vs frozen records anywhere.
