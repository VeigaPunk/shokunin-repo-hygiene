## Status
STATUS: PASS — the frozen 12-case C3 fixture is delivered at `.ufo/waves/round-26/w1/r26-axis-check.py`; it reports `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, exit 0, against both a scratch reference tool and the current `tools/souji-axis-check.py`, and rejects the always-green target arm (9/11 case failures).

## Evidence

Frozen contract read first (bytes verified, not inferred):
- `git show 89e0fceeefcf28db313c94120be6d25e03c60094:.ufo/waves/round-26/preregistration.txt | sha256sum` → `cbfa4c5486118c243fca936d30f23a18c858eca305db84fc3aa4334b3c7d5832`; the working file has the same sha256, so the C3 case set I implemented is the frozen one. Amendments 1 and 2 read (K4 grounded 7→9 literal correction; C1 protected regions are byte spans).
- Case-1 provenance, `git show 6e4737eab43d8fde1b85eb9f57023d29046705b4:.ufo/waves/round-25/preregistration.txt` line 59: “C2 — operability (8). Size-census refusal surfaces covered by the frozen fixture.” (11 words, no `|`). Reconstructed into the fixture as a synthetic prereg (`axis: operability`, `surface-class: fixture-expansion`, enumerate present) paired with an axes table calibration 7 / operability 8 / coverage 8.
- Revisions: lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`; `git rev-parse HEAD` was `4453128` at first read and `0833de9591a7db81cdfa4efda2cdad2e75606f58` at the final run (sibling seats landed during the wave; no git/jj mutation was issued by this seat).

Delivered file: `.ufo/waves/round-26/w1/r26-axis-check.py`, sha256 `220eed2e15f3154d8a6909cac57f325862d0d472a4e3bab6d88ce48776e1d88d`. CLI `--tool PATH`; one `CASE <n> <name> PASS|FAIL <detail>` line per case; last line `cases=12 pass=<P> control=FALSE-GREEN-REJECTED|FALSE-GREEN-ACCEPTED`; exit 0 iff P=12 and the first spelling. Each case owns `<base>/run-<pid>/case-NN/{prereg.txt}`; the run directory is removed in a `finally` block and the shared base is only `rmdir`-ed when empty.

Arm A — scratch reference tool `/var/tmp/souji-r26-ExecAxisFixture/ref/souji-axis-check.py` (frozen-R1..R4 implementation):
```
CASE 1 r25-c2-replica-fixture-expansion-on-operability PASS rc=1 claims=1 flags=2 rules=R2,R3
CASE 2 wellformed-3claim PASS rc=0 claims=3 flags=0 rules=-
CASE 3 r1-axis-not-owned PASS rc=1 claims=2 flags=1 rules=R1
CASE 4 r2-fixture-expansion-on-operability PASS rc=1 claims=2 flags=1 rules=R2
CASE 5 r2-bookkeeping-file-on-coverage PASS rc=1 claims=2 flags=1 rules=R2
CASE 6 r2-instrument-acquisition-on-calibration PASS rc=1 claims=2 flags=1 rules=R2
CASE 7 r3-no-claim-on-lowest-axis PASS rc=1 claims=2 flags=1 rules=R3
CASE 8 r4-universal-clause-without-enumerate PASS rc=1 claims=1 flags=1 rules=R4
CASE 9 r4-universal-clause-with-enumerate PASS rc=0 claims=1 flags=0 rules=-
CASE 10 wellformed-surface-class-and-enumerate PASS rc=0 claims=1 flags=0 rules=-
CASE 11 malformed-missing-axis-line PASS rc=2 claims=- flags=- rules=-
CASE 12 control-always-green-stub PASS stub_passed=2/11 discriminator=PASS control=FALSE-GREEN-REJECTED
cases=12 pass=12 control=FALSE-GREEN-REJECTED
EXIT=0
```

Arm B — lane tool `tools/souji-axis-check.py` (sha256 `14bc9632e88ef58f18108011f6645bd970cd825d0ffc1664369dc60b0d579332`): all twelve `CASE ... PASS`, identical per-case `rc/claims/flags/rules` to Arm A, `EXIT=0`.

Arm C — always-green target (`claims=1 flags=0`, exit 0): cases 1,2,3,4,5,6,7,8,11 FAIL (missing flags/claims/rc), cases 9 and 10 legitimately pass (their expectation is “clean”), `stub_passed=2/11 discriminator=PASS`, `cases=12 pass=3 control=FALSE-GREEN-REJECTED`, `EXIT=1` — the target cannot pass the suite; the control spelling and the overall exit are separate signals.

Arm D — sibling candidate `.ufo/waves/round-26/w1/souji-axis-check.py` (sha256 `0805afff649a2f893542bd7f8e2e676408bb934a7cf3255d13b46d921c3d121b` at run time): `cases=12 pass=6 control=FALSE-GREEN-REJECTED`, `EXIT=1`; failing cases 3, 6, 7, 8, 9, 10 (see finding 4).

Scratch/cleanup: after all runs the base held only `ref/`; `find /var/tmp/souji-r26-ExecAxisFixture -maxdepth 1` printed no `run-*` directory. No `__pycache__` was created in the lane (`python3 -B` for every lane and scratch invocation).

## Findings

1. Fixture content (`.ufo/waves/round-26/w1/r26-axis-check.py`): the twelve frozen cases with the exact expectations — 1 r25-C2 replica → exit 1 + R2; 2 three well-formed claims → 0 flags, `claims=3`; 3 `axis: quality` + a calibration claim → exactly {R1}; 4 fixture-expansion on operability (plus a clean calibration claim) → exactly {R2}; 5 bookkeeping-file on coverage → exactly {R2}; 6 instrument-acquisition on calibration → exactly {R2}; 7 operability+coverage only → exactly {R3}; 8 universal clause without `enumerate:` → exactly {R4}; 9 same clause with `enumerate:` → 0 flags; 10 neutral `measurement` claim with surface-class+enumerate → 0 flags; 11 claim without `axis:` → exit 2, no `FLAG` line; 12 stub control arm. Flagged cases assert the exact rule set (so an extra R3/R4 finding is a failure, not a pass), clean cases assert `flags=0`, exit 0 and no `FLAG` lines.
2. Case 1 discriminator is real: the always-green stub prints `flags=0` on the replica, so case 1 fails for it (`discriminator=PASS` in the Arm C/A detail). This is the pre-registered kill-rule shape “stub/base arm prints flags=0 on the r25-C2 replica”.
3. Self-exercise found one fixture defect before delivery: `FLAG_RE` lacked `re.M`, so a run emitting two `FLAG` lines was scored as one (first Arm A run: `CASE 1 ... FAIL ... counts line flags=2 but 1 FLAG line(s)`). Fixed to `re.compile(r"^FLAG\s+(\S+)\s+(R\d+)\b", re.M)`; the runs above are post-fix. Recorded because it shows the suite executes rather than passing vacuously.
4. Two untracked tool candidates exist and they disagree: `tools/souji-axis-check.py` passes 12/12; `.ufo/waves/round-26/w1/souji-axis-check.py` passes 6/12. Single root cause at `w1/souji-axis-check.py:142` — `if retired or "retired" in line.lower(): continue` drops any SCORECARD line whose text contains the substring `retired`, so the synthetic calibration axes row (observation cell “synthetic row: lowest non-retired axis”) is discarded; `scores` collapses to `{operability: 8, coverage: 8}`, R3 then misfires on cases 3, 6, 8, 9, 10 and never fires on case 7. A tool that qualifies axes rows by the `## Retired` section is unaffected. The L1 must fix that line (or ship the `tools/` candidate) and re-run K2 on the exact bytes it lands — the fixture is the oracle, and no case will be re-worded after data.
5. `.ufo/waves/round-26/w1/r26-axis-check.py` is the delivery; `tests/fixtures/r26-axis-check.py` already exists untracked (sha256 `2ffc18289fc82b9075ad3580cb9bec6a80384061c7d294b5aa17dbf9ca93c8da`, 11 cases, no r25-C2 replica, no case-12 control contract). It does not implement the frozen set; the L1's copy of the delivered file must overwrite it.
6. No fixture case reads the lane `preregistration.txt` or `SCORECARD.md`: every input is a synthetic file inside the scratch world (Arm B used the lane tool binary, never lane data), so the K1 self-hosting run remains the L1's to perform.
7. Bounds held: writes limited to the report directory and `/var/tmp/souji-r26-ExecAxisFixture/` (removed); no `git add/commit/stash/checkout/reset`, no `jj` mutation, no `rm`/`mv` outside my own scratch, no signals, no `agent://all`; nothing under `/home/vgpnk/Projects/shokuknow` touched. No tool installed or upgraded (nothing was needed); toolchain: system `python3`, `git` 2.56.0.

## Attack log

Not an attack item. One disclosed design choice, so the L1 can adjudicate it before scoring: the synthetic axes table's observation cell contains the lane's own phrase “lowest non-retired axis”, which exposes tools that skip axes rows by substring instead of by the `## Retired` section (finding 4). The case set, predicates and targets are exactly the frozen C3 set; no relaxation is proposed.
