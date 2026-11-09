# R99ExecC2 — C2 counter build (R99C2)

## Files changed
- `census/round-99/c2-setup-arms.py` (copy of `census/round-98/c2-setup-arms.py`, sha256 `03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57`):
  - In `_reap_owned`: deleted the branch `elif _is_descendant(pid, os.getpid()): pass` (r98 subreaper branch (c)). A pid is now owned iff it equals the spawn pid (starttime verified) or `_is_descendant(pid, spawn_pid)` is true. `grep` confirms no remaining `getpid`-based ownership: the only `_is_descendant` calls are against `spawn_pid`/`spawn[0]` (lines 187, 374).
  - Survivors count updated to the same spawn-chain rule (counts spawn pid or ppid-chain descendant of spawn pid only).
  - For the T1 escapee, spawn-chain only is used — no invented rule. See Finding F1.
- `census/round-99/c2-decoy-test.py` (byte-identical copy of `census/round-98/c2-decoy-test.py`, sha256 `9d06e806daf15b34c1c2b4e546cd9262e45e1d7c6921fd029ae2ef7b461b79cc`; `diff` clean).
- No census/round-98 file edited. No commit/push/git mutation.

## Commands, exit codes, observed lines

### r99 counter + decoy test (spared expected)
```
python3 -B census/round-99/c2-decoy-test.py --counter census/round-99/c2-setup-arms.py --probe census/round-98/c2-forgery-probe.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work /fast/scratch/hyaku/souji-r99/R99ExecC2/decoy --arm-timeout 200 --plant-delay 2
exit=0 (EXIT=0)
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=20
DECOY-PLANTED n=86 dead=0 alive=86 counter_exit=0 token=/fast/scratch/hyaku/souji-r99/R99ExecC2/decoy/arms/fixture-pipe-holder.py
DECOY-SUMMARY verdict=spared
```
Full per-arm output: `counter-r99.out`. All 20 arms conform.

### r97 counter + same decoy test (killed expected)
```
python3 -B census/round-99/c2-decoy-test.py --counter census/round-97/c2-setup-arms.py --probe census/round-98/c2-forgery-probe.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work /fast/scratch/hyaku/souji-r99/R99ExecC2/decoy97 --arm-timeout 200 --plant-delay 2
exit=1 (EXIT=1)
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=20
DECOY-PLANTED n=85 dead=60 alive=25 counter_exit=0 token=/fast/scratch/hyaku/souji-r99/R99ExecC2/decoy97/arms/fixture-pipe-holder.py
DECOY-SUMMARY verdict=killed
```
Full per-arm output: `counter-r97.out`. 60 of 85 planted foreign decoys were killed; 25 planted after the r97 T1 snapshot survived (expected — confirms the test is not over-killing by construction).

## Findings

### F1 (open limit, with evidence) — T1 escapee not reachable from spawn pid after parent exits
- Reproducer/output: `counter-r99.out` shows `--survivors 0 planted-killed 0--` (T1.out) and `ARM T1 … survivors=0`. The count is 0 **vacuously**, not by kill: `planted-killed 0`. Cross-check after the run: process `3624139` (the T1 escapee, `/fast/scratch/hyaku/souji-r99/R99ExecC2/decoy/arms/fixture-pipe-holder.py --tool … --before … --work …/T1/positive`) was still alive with stat `3624139 (python3) S 1525 3624139 3624139 …` — ppid `1525`, sid `3624139` (own setsid session, S368). Its ppid chain does not reach the recorded spawn pid, so under the spawn-chain-only rule it is NOT killed, exactly as the seat spec states. This is the reported open limit — no rule was invented. The lender (L1) must decide whether `survivors=0` bound to conform is misleading when the escapee is unreachable; the decoy leg (spared, 86/86) is the binding check that this reap does not over-kill.

### F2 — no over-kill, no under-kill on foreign decoys
- r99: 86 planted, 0 dead → `spared`, exit 0. r97: 85 planted, 60 dead → `killed`, exit 1. The argv-only mutant is still killed; the spawn-chain counter spares every foreign own-uid carrier.

## Risks / blockers
- Collateral leftovers: sibling seats' decoys and the T1 escapee were noted in `ps` output during the run; only my own planted decoys were killed by the decoy test itself. My scratch dir is deleted before yield; the T1 escapee (3624139) is not reaped by the counter by rule and was left as evidence for F1 — killing it from this seat would be out of contract.
- No sysctl mutation, no tool installs. `python3 -B` used; host python3 version not recorded (no install needed).
- The `decoy/` workdir under my scratch contains per-arm outputs used as evidence; copies saved under `.ufo/waves/round-99/w1/R99ExecC2/`.

Report: .ufo/waves/round-99/w1/R99ExecC2.md
