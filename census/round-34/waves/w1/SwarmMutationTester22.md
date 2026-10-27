## Status
STATUS: PARTIAL — pristine base control executed; eight mutants and their dedicated cheat controls remain untested.

## Evidence
- Command: `flock /fast/scratch/hyaku/souji-r34/MutateC1Counter/run.lock python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-34/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 9c76c7222a8abff027af42e37f0d160d52526bba --list-rev 2b0171e2071fdc9c16a69bed12b0d040e574d8c8 --scratch /fast/scratch/hyaku/souji-r34/MutateC1Counter/base`
- Output: exit 1; `SUMMARY items=60 agree=35 mismatches=25 restated=0 rev=9c76c7222a8abff027af42e37f0d160d52526bba`.
- `/proc/loadavg` beside run: `19.60 10.52 5.39 17/6584 982162`.
- Counter freeze revision: `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`.

## Findings
1. The pristine base reading has 25 mismatches, meeting the frozen do-nothing expectation. Source: `census/round-34/preregistration.txt`, C1 “Do-nothing control”; quote: “prints mismatches>0 (committed pre-data in census/round-34/records/controls.txt)”.
2. Mutant-specific falsifiers are unexecuted; no killed/survived verdict is asserted. The delivery table records this explicitly.

## Attack log
Not applicable; no attack was executed.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-c1-mutants.txt`
