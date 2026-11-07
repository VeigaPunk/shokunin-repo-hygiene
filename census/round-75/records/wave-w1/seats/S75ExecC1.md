# S75ExecC1 — C1 reproduction (round 75)

Verdicts vs frozen preregistration (preregistration.txt:7-30):
1. W gate (1ad737b) mismatches=0 EXIT=0: REPRODUCED. ROW lines identical to records/c1-after.txt (diff of ^ROW|^SUMMARY empty); SUMMARY rows=25 mismatches=0 errors=0, EXIT=0.
2. Lane-base gate (52d3f07) mismatches=2 EXIT=1: REPRODUCED. ROW lines identical to controls/c1-K-a-do-nothing.txt; SUMMARY rows=25 mismatches=2 errors=0, EXIT=1 (f-info-exclude, f5-info-exclude-dir mismatched).
3. K-b blanket (controls/c1-K-b-blanket-ignored.txt replayed via controls/variants/gate-K-b-blanket-ignored.sh): REPRODUCED. ROW lines identical; SUMMARY rows=25 mismatches=3 errors=0, EXIT=1 (f2, f6, f7 mismatch).
4. Fail-closed (W gate, no writer): FAIL-CLOSED. Counter prints `C1-COUNTER-FATAL: gate dir incomplete: .../FW`, EXIT=2, no ROW lines — expected-PASS rows do not read PASS.
5. Domain trial: MISMATCH vs prereg claim (which pins check-clean=PASS only at clean lane): observed check-clean=FAIL, RC=1, wall ~0.46-0.48s. Cause: tracked modifications `M corpus/SOURCES.md`, `M corpus/knowledge/filter-filemode-witness.md` (detail-clean) and check-shonen=FAIL (found 0 headings vs 1; prereg file used as --report has no SHONEN heading). No RECEIPT-UNTRACKED-LOCAL-EXCLUDE line fired. Ignored-untracked count identical: 25993 paths under both `--exclude-standard` and `--exclude-per-directory=.gitignore`; sample ignored: `.jj/.gitignore` (the f7 self-ignore shape, hence accepted).

Commands run (cwd=lane root):
- `python3 -B census/round-75/c1-evade-counter.py --gate-dir <dir> --work <scratch>` with dirs built via `git show <rev>:tools/...` (W/Ka) and variant copy (Kb) or W-copy alone (FW).
- Domain: `bash tools/souji-pre-report-gate.sh --lane <lane> --branch master --report <prereg> --prereg <prereg>`.

Findings: none HIGH/MEDIUM/LOW against the counter numbers. Note: parallel invocations from one cwd raced (first 3-run fork failed with wrong cwd /home/vgpnk/Projects/shokunin/census/...); re-ran from lane root — all four arms then clean. [INFERENCE] Domain-trial mismatch is environmental (dirty lane, wrong report file for shonen check), not a counter falsification.

Files written: only this report `.ufo/waves/round-75/w1/S75ExecC1.md`.
