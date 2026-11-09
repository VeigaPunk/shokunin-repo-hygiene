# R99ExecC2b — C2 cross-arm probe (operability, S075/S368)

## Seat axes

1. **Discrimination**: the probe must give `spared` under the r99 counter and `killed` under the r98
   counter (branch (c)) — any verdict that does not flip is vacuous.
2. **Carrier fidelity**: the carrier must be a counter-descendant (ppid chain reaches the counter) and
   must carry the T1 reap token byte-exactly, while not being a member of the T1 arm's spawn chain.
3. **Timing-insensitivity**: carriers are planted continuously during the run (post-snapshot for any
   argv-snapshot reap), so the verdict cannot be an artifact of plant timing.

## Deliverable

`census/round-99/c2-cross-arm-probe.py` (sha256
`22eda14170decb34549e6e1a7787ea72f283a1771398ae1a187b9b3f3e7cb154`). Mechanism, adapted from
R98Sentinel `reproducers/cross_arm_probe.py` (R98Sentinel FINDING 4): the probe writes an
"other arm" fixture and points the counter's `--fixture-pass` and `--fixture-fail` at it. Every arm
running that fixture forks a carrier (setsid sleeper, pipes detached to `/dev/null`, argv carries the
counter's T1 reap token `<counter --work>/fixture-pipe-holder.py` byte-exactly) and records the carrier
pid at `<arm --work>/<label>/carrier.pid`. The fixture prints the tool_pass SUMMARY and exits, so the
carrier orphans and reparents to the counter itself (the counter sets `PR_SET_CHILD_SUBREAPER`): a
descendant of the counter, not of the T1 arm's recorded spawn pid. The probe polls each recorded pid
after the counter exits. Exit 0 = spared, 1 = killed, 2 = inconclusive.

## Commands (all run from scratch `/fast/scratch/hyaku/souji-r99/R99ExecC2b/`, deleted after)

Common args: `--probe census/round-98/c2-forgery-probe.py --tool tools/souji-record-agreement.py
--before census/round-92/controls/c2-before-tool.py --arm-timeout 60`

| # | command | exit | observed summary |
|---|---------|------|------------------|
| 1 | `python3 -B census/round-99/c2-cross-arm-probe.py --counter census/round-99/c2-setup-arms.py --work $S/r99 --label r99` | **0** | `CROSS-ARM-PLANTED n=30 dead=0 alive=30 counter_exit=1` / `CROSS-ARM-SUMMARY verdict=spared` |
| 2 | `python3 -B census/round-99/c2-cross-arm-probe.py --counter census/round-98/c2-setup-arms.py --work $S/r98 --label r98` (do-nothing control) | **1** | `CROSS-ARM-PLANTED n=30 dead=30 alive=0 counter_exit=1` / `T1-REAP survivors 0 planted-killed 32` / `CROSS-ARM-SUMMARY verdict=killed` |
| 3 | `python3 -B census/round-99/c2-decoy-test.py --counter census/round-99/c2-setup-arms.py --work $S/decoy99 --plant-delay 1` | **0** | `DECOY-PLANTED n=107 dead=0 alive=107` / `DECOY-SUMMARY verdict=spared` |
| 4 | `python3 -B census/round-98/c2-decoy-test.py --counter census/round-98/c2-setup-arms.py --work $S/decoy98 --plant-delay 1` (r98 baseline) | **0** | `DECOY-PLANTED n=106 dead=0 alive=106` / `DECOY-SUMMARY verdict=spared` |
| 5 | `python3 -B census/round-98/c2-decoy-test.py --counter census/round-98/c2-cm8-mutant.py --work $S/cm8 --plant-delay 1` (CM8 argv-only mutant) | **1** | `DECOY-PLANTED n=106 dead=105 alive=1` / `DECOY-SUMMARY verdict=killed` |

## Findings

- **F1 (discrimination holds).** The probe gives opposite verdicts on the two counters: 30/30 carriers
  survive the r99 counter (spawn pid + ppid chain only, branch (c) removed), 30/30 are killed by the
  r98 counter (branch (c): `elif _is_descendant(pid, os.getpid())`). Reproducer:
  `census/round-99/c2-cross-arm-probe.py` (commands 1–2 above).
- **F2 (decoy predicate still discriminates).** The r99 counter spares 107/107 foreign decoys; the r98
  CM8 argv-only mutant kills 105/106 (1 sleeper raced past the reap — same class as the r98 record's
  `24 of 33`; the predicate needs ≥1 dead to fail, so the mutant is still killed). Commands 3 and 5.
- **F3 (carriers genuinely counter-owned).** In the r99 run every carrier's argv carried the token
  (`argv_token=yes`), and the r98 run's `planted-killed 32` plus 30/30 dead confirms the carriers were
  counter-descendants for the r98 reap to reach. Carrier ppids read `1525` at verdict time in run 1
  (post-counter-exit reparent to init) — expected, not a fidelity gap: the r98 leg proves ownership.
- **F4 (smoke detail, not a defect).** Every counter run reported `ARM T1 exit=hung` because the other-arm
  fixture makes P1/P2/S1 exit 1 (no `FORGERY-SUMMARY` line — the fixture prints a bare SUMMARY, so the
  verdict arms fail their line check). Conform stays 15/20 on probe runs regardless of counter; the
  probe's verdict does not depend on it. The T1 arm also hangs with the *unmodified* counters in this
  configuration (arm-timeout 60 vs the pipe-holder escapee); `T1-REAP survivors 0` is still printed
  because the timeout killpg path runs before the reap block. This seat's claim does not ride on T1's
  internals.
- **F5 (r98 baseline unchanged).** The r98 counter spares the foreign decoy (106/106, command 4),
  matching the lane's round-98 record. No regression from r99 work on the r98 instruments (read-only).

## Risks / notes for the L1

- The probe plants 30 carriers per run (one per forgery/label run of each arm); all are SIGKILLed by the
  probe after the verdict. One leftover sleeper from a manual debug run (pid 534801) was killed at
  cleanup; `ps` count of `time.sleep(3600)` processes is 0.
- Scratch `/fast/scratch/hyaku/souji-r99/R99ExecC2b/` deleted before yielding (verified absent).
- No tools installed or upgraded; no host sysctls touched.
- The probe file is untracked in git (`?? census/round-99/c2-cross-arm-probe.py`); committing is the
  L1's call.
