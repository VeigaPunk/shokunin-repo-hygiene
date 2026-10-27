## Status
STATUS: PARTIAL — reproduced one C1 survivor (wildcard exit); the other listed probes were not executed.

## Evidence
- Command: `flock /fast/scratch/hyaku/souji-r34/AttackC1Counter/score.lock python3 -B /fast/scratch/hyaku/souji-r34/AttackC1Counter/c/census/round-34/c1-counter.py --root /fast/scratch/hyaku/souji-r34/AttackC1Counter/c --rev 58166e2ef1f0a88441f02cad5f875c9b962ffd04 --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/AttackC1Counter/run1 --only E18`
- Load sample: `29.36 15.59 7.61 26/7679 1622431`.
- Output: `ITEM E18 AGREE restated rc=0 expect_exit=* statement is the run's last digit-bearing line last=selftest=PASS ids=7/7 load=29.36`; summary `items=1 agree=1 mismatches=0 restated=1`.
- Revision: attack commit `58166e2ef1f0a88441f02cad5f875c9b962ffd04`, parent is frozen list-rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`.
- Counter evidence opened this run, `census/round-34/c1-counter.py`, lines 211-213: “if not re.fullmatch(r"-?\\d+|\\*", rexit):” and later “exit_ok = exit_ == "*" or rc == int(exit_)”. This confirms `*` is accepted without matching the observed exit. The reproduced E18 run happened to return rc=0; the forged row does not bind that value.

## Findings
1. **Wildcard exit is a false authority / survivor.** In `census/round-34/c1-counter.py` (`judge`, restatement exit validation and measured `exit_ok`), `*` passes regardless of rc. I appended an E18 row with valid executed value-drift cause `728b2ce71acbe574ae3036b456724d0a3d6f8f08`, statement `selftest=PASS ids=7/7`, and exit `*`; the exact output above is AGREE. This weakens calibration evidence because the restated record does not assert the command's actual exit. **Impacted axis:** calibration. **Smallest safe correction:** reject wildcard restatement exits or require a concrete exit equal to the measured rc; keep all frozen item predicates and target unchanged.
2. **Unexecuted probe cautions [INFERENCE].** Source inspection shows corrected-argv validation tests `os.path.basename(f) in argv` (counter `judge`) rather than whether argv invokes that file; likely wrapper/comment/echo spellings can pass that gate, but cause eligibility and end-to-end acceptance were not tested. `lines = out.splitlines() + err.splitlines()` makes stderr digit lines take precedence over stdout for the last-digit selection; whether a relevant frozen item has such output was not tested. `collapse()` is applied to both statement and observed last line, so whitespace variants appear intentionally equivalent. Duplicate rows are explicitly rejected. A `####` heading turns section parsing off, so subsequent rows would be ignored rather than treated as restatements. Timeout, merge-cause, RESULTS re-add/add-by-measured-rev edge cases, and progress-line wildcard were not executed; no outcome is claimed for them.

Source quote: `census/round-34/c1-counter.py`, `judge` measured-exit logic, opened this run: “exit_ok = exit_ == "*" or rc == int(exit_)”.

## Attack log
1. Wildcard exit, E18: scratch commit `58166e2ef1f0a88441f02cad5f875c9b962ffd04`; counter command and ITEM line in `deliver-c1-attacks.txt`; **AGREE, SURVIVOR**.
2. Wrapper/basename-only argv; stderr last-line; whitespace collapse; merge cause; parent timeout; duplicate rows; nested `####`; RESULTS file added by measured commit; progress-line with wildcard exit: **not run**.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-c1-attacks.txt`
- `.ufo/waves/round-34/w1/SwarmCritic18.md`
