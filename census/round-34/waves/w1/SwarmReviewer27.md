## Status
STATUS: PARTIAL — C1 three-clause behavioral junk control passed; C2 fixture timed out after 900s, so its five-leg rejection is not verified.

## Evidence
- `flock /fast/scratch/hyaku/souji-r34/ReviewJunkFixtures/fixture.lock python3 -B .../r34-c1-junk.py --counter .../c1-counter.py --scratch .../c1` → `cases=3 pass=3 control=STUB-REJECTED`, exit 0. Per-case E18 MISMATCH details identify last-digit-line, RESULTS>=1, and own-file argv clauses. Lane tip observed `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; list rev `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`.
- `flock ... python3 -B .../r34-sandbox-junk.py --counter .../c2-counter.py --scratch .../c2` → uncaught `subprocess.TimeoutExpired` at fixture line 117; inner counter exceeded 900 seconds, exit 1. No case receipt. Post-run load `39.80 38.53 30.17 23/7767 2824911`.
- Historical cause evidence: `census/round-34/records/controls.txt:5` records E18 cause `728b2ce71acbe574ae3036b456724d0a3d6f8f08`, parent `ids=5/5` and cause `ids=7/7`. Observed C1 emitter MISMATCH confirms probe reached intended statement check. The C2 timeout is also recorded at `controls.txt:11`.

## Findings
1. C2 junk fixture completion remains unverified: inner full counter hit timeout and the fixture has no timeout handler/structured failure receipt (`tests/fixtures/r34-sandbox-junk.py:117-120`).
2. C2 fixture's fail criterion is permissive: it checks only that each named ID appears among failure rows and rc is nonzero (`tests/fixtures/r34-sandbox-junk.py:121-127`); unrelated failure causes can satisfy this without demonstrating work-witness rejection.
3. Both fixtures assume `master` identifies intended lane tip and derive lane root from the supplied counter path (`r34-c1-junk.py:71-82`; `r34-sandbox-junk.py:61-68`). They do not pin/validate the passed counter bytes. These are attack assumptions, not reproduced bypasses.
4. C1 is non-vacuous for this run: emitter uses historical E18 item/cause (`r34-c1-junk.py:32-40`); counter validates value drift at `c1-counter.py:284-291`; observed MISMATCH was specifically `statement is not the run's last digit-bearing line`.

## Attack log
No weakened-counter bypass was reproduced. C1 control passed all three frozen forged constructs. C2 attack inconclusive due timeout; do not infer any of its five stubs were rejected.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-junk-fixture-review.txt`
