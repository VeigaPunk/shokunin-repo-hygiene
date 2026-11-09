# MutC1WideRule — wide-rule (r97 argv-only) mutant probe report

Seat: MutC1WideRule (mutation-tester) — souji round 100, wave 1.
Mission: take the r100 C1 T1 ownership test (`census/round-100/c2-setup-arms.py`,
already written by ExecC1SessionApplier) and restore the r97 argv-only branch as
the **m_wide** mutant — *any own-uid token-carrying pid is killed, no session
test* — then run the decoy detector and record whether the frozen predicate
punishes the too-wide rule (Q175) and what the mutant does to the escapee leg.

## Mutant (m_wide)

Base: scratch copy of `census/round-100/c2-setup-arms.py` at
`census/round-100/c2-setup-arms.py` sha256
`f71b2155cb9f68cd75d5f56c9a50a0b941f4ed7b26aece7489486e8bed777abe`
(captured after ExecC1SessionApplier landed; it is no longer the r99 copy,
`03e8a99e…`: the r100 file now defines `_proc_sid` (field 6), the spawn tuple is
`(pid, starttime, sid)` at line 349, and `_reap_owned` enforces session
ownership — root cause of the cross-talk in run-pristine below).

Mutant file: `.ufo/waves/round-100/w1/MutC1WideRule/m_wide.py`
(diff: `.ufo/waves/round-100/w1/MutC1WideRule/m_wide.diff`), sha256
`eb3aeff10675b6c989bdb3e45eef7f3cc11f0b56037bd2085f138c03f82a9c90`.
Smallest behavior-bearing change, in `_reap_owned` only:

1. spawn branch → `pass` (r97 argv-only; no `pid == spawn_pid` +
   starttime test, no field-6 session test).
2. no-spawn compat branch `continue` → `pass` (any own-uid token-carrying
   pid authorized, the r97 behavior).

`/proc` selection (byte-exact token on argv, own-uid scan) is unchanged; the
mutant is a pure ownership-widening. No lane file, sibling file, or git/jj
state was touched. Lane files were read only.

## Detector runs (commands, exit codes, observed lines)

All runs use the frozen r100 detector
`census/round-100/c2-decoy-test.py`, the r98 forgery probe
`census/round-98/c2-forgery-probe.py`, tool
`tools/souji-record-agreement.py`, before
`census/round-92/controls/c2-before-tool.py`, `--arm-timeout 200
--plant-delay 2`. Scratch under `/fast/scratch/hyaku/souji-r100/MutC1WideRule/`
(deleted before yield; evidence copied under this wave dir).

### Wide mutant + decoy detector (the load-bearing run)

```
python3 census/round-100/c2-decoy-test.py \
  --counter /fast/scratch/hyaku/souji-r100/MutC1WideRule/m_wide.py \
  --probe census/round-98/c2-forgery-probe.py \
  --tool tools/souji-record-agreement.py \
  --before census/round-92/controls/c2-before-tool.py \
  --work /fast/scratch/hyaku/souji-r100/MutC1WideRule/run-wide
```

Exit code **1** (verdict=killed). Observed (saved: `counter-wide.out`):

```
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=20
DECOY-PLANTED n=83 dead=82 alive=1 counter_exit=0 token=/fast/scratch/hyaku/souji-r100/MutC1WideRule/run-wide/arms/fixture-pipe-holder.py
DECOY-SUMMARY verdict=killed
```

Expected: `verdict=killed` — the decoys were killed. **Match.**

Note the counter's own T1 arm reports `survivors=0` under the mutant
(it reaps the escapee trivially — see escapee leg below), and the counter
exited 0 with conform=20, so the run was a clean arms pass, not a crash.

### Pristine r100 counter + decoy detector (baseline, solo re-run)

(First attempt `run-pristine` ran concurrently with the wide-mutant run;
m_wide scans *all* own-uid token carriers, so it killed the pristine run's
decoys: `verdict=killed`, counter_exit=1, T1 `line=no conform=no`. That run is
**contaminated and inconclusive** — its output is not reproduced as evidence
of pristine behavior; it is preserved only in scratch, not in this wave dir.
A mutant-positive through a shared /proc scan is a cross-talk artifact, not a
false credit against the predicate. The solo re-run below is the baseline.)

```
python3 census/round-100/c2-decoy-test.py \
  --counter census/round-100/c2-setup-arms.py \
  ... --work /fast/scratch/hyaku/souji-r100/MutC1WideRule/run-pristine2
```

Exit code **0** (verdict=spared). Observed (saved: `counter-pristine.out`):

```
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=20
DECOY-PLANTED n=83 dead=0 alive=83 counter_exit=0 token=/fast/scratch/hyaku/souji-r100/MutC1WideRule/run-pristine2/arms/fixture-pipe-holder.py
DECOY-SUMMARY verdict=spared
```

Expected (frozen C1 predicate): `verdict=spared` — every foreign decoy
survived. **Match.** Baseline passes, verdict meaningful.

### m_wide + T1 escapee leg (ESCAPEE-ALIVE)

Solo run of `m_wide.py` directly:

```
python3 m_wide.py --probe census/round-98/c2-forgery-probe.py \
  --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py \
  --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py \
  --work /fast/scratch/hyaku/souji-r100/MutC1WideRule/esc-m-wide/arms
… then count live /proc carriers of the run's token …
```

Exit code **0**. Observed:

```
ARMS-SUMMARY arms=20 conform=20
ESCAPEE-ALIVE token=/fast/scratch/hyaku/souji-r100/MutC1WideRule/esc-m-wide/arms/fixture-pipe-holder.py alive=0
```

(T1.out `--survivors 0 planted-killed 1--`.) Expected: `alive=0` trivially.
**Match.** The wide mutant reaps the T1 escapee, exactly as predicted — which
is why the decoy leg is load-bearing: alive=0 alone cannot distinguish the
session-owned predicate from an argv-only kill.

### Pristine r100 escapee leg (context run)

Same solo run with the pristine counter (`esc-wide-work`):

```
ARMS-SUMMARY arms=20 conform=20
ESCAPEE-ALIVE token=/fast/scratch/hyaku/souji-r100/MutC1WideRule/esc-wide-work/arms/fixture-pipe-holder.py alive=1
```

(T1.out `--survivors 0 planted-killed 0--`.) One live carrier remained
(pid 3407560, ppid 1525, killed by this seat after capture; a re-sweep showed
`alive=0` after the kill). Expected frozen target: `alive=0` with decoy
`spared`. The escapee leg **did not meet the frozen target in this run** —
notably `--survivors 0 planted-killed 0`: the counter's own ownership
accounting counted zero survivors but signalled nothing, while an external
scan still found the token carrier live. This is a finding against the
pristine predicate/run, reported with reproducer above, not a finding about
m_wide. Possible causes ([INFERENCE], needs the L1/predicate owner):
(a) a race — the escapee is counted/survivor-scanned after it exits, or
reaped by a parallel run's wider scan (this run overlapped in time with the
pristine2 decoy run, whose counter does not reap foreign decoys); (b) the
planted escapee's session id differs from the recorded spawn sid (setsid
child of the fixture, ppid chain broken, subreaper reparenting) and its
starttime predates the spawn record, failing branch (b); (c) a run-specific
flake. The decoy leg (spared, 83/83) and the wide-mutant verdicts are
unaffected.

## Verdicts

| Run | Detector | Observed | Expected | Verdict |
|---|---|---|---|---|
| m_wide + decoy | DECOY-SUMMARY | `verdict=killed` (dead=82, counter_exit=0) | `killed` (decoy killed) | **mutant killed** |
| pristine r100 + decoy (solo) | DECOY-SUMMARY | `verdict=spared` (dead=0, n=83) | `spared` | baseline holds |
| pristine r100 + decoy (concurrent) | DECOY-SUMMARY | `verdict=killed` (cross-talk) | — | **inconclusive, contaminated** |
| m_wide + escapee | ESCAPEE-ALIVE | `alive=0` | `alive=0` (trivial) | mutant passes escapee leg trivially |
| pristine r100 + escapee | ESCAPEE-ALIVE | `alive=1` | `alive=0` | **frozen target missed in this run** |

**Overall probe verdict: mutant killed.** The frozen predicate (session
ownership, field-6 sid + spawn-pid/starttime) punishes the too-wide rule —
m_wide kills the foreign decoys (82/83) and is caught by the decoy detector
with exit 1. The escapee leg alone is non-discriminating (m_wide trivially
`alive=0`), confirming the decoy leg is load-bearing. The pristine predicate
itself passed the decoy leg cleanly (spared 83/83) but missed the escapee
alive=0 target in one run — flagged as a finding for the L1, not resolved
here (seat scope: mutation probe only).

## Restoration / cleanup evidence

- No lane, sibling, or git/jj state mutated. Only writes: this wave dir
  (`MutC1WideRule.md`, `MutC1WideRule/` + evidence) and the seat scratch
  root `/fast/scratch/hyaku/souji-r100/MutC1WideRule/`.
- Scratch tree deleted before yield (`rm -rf /fast/scratch/hyaku/souji-r100/MutC1WideRule`).
- All planted processes killed: decoy-test leftovers 3347878
  (`run-pristine2` token) and 3407560 (`esc-wide-work` token) SIGKILLed by
  the seat; final sweeps of all four run tokens (run-wide, run-pristine,
  run-pristine2, esc-wide-work) and the esc-m-wide token all show `alive=0`.
  `m_wide.py` itself wrote no other writes.
