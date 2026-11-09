# R99MutC2 — mutation test of the r99 C2 arms counter

Seat: R99MutC2 (mutation-tester). Target: `census/round-99/c2-setup-arms.py` `_reap_owned`, five one-edit mutants, each run against both committed predicates: `census/round-99/c2-decoy-test.py` and `census/round-99/c2-cross-arm-probe.py`.

Method: mutants were built as copies of "pristine" in scratch (`pristine.py`, sha256 `03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57`, byte-identical to the landed lane file — verified by sha256 before and after the runs; the lane files `c2-setup-arms.py` / `c2-decoy-test.py` / `c2-cross-arm-probe.py` were never edited). Each mutant file was compiled (`py_compile` OK) and its sha256 recorded. All counter runs for a given predicate shared identical arguments except `--counter` and `--work`:

```
python3 -B census/round-99/c2-decoy-test.py --counter <MUTANT> \
  --probe census/round-98/c2-forgery-probe.py \
  --tool tools/souji-record-agreement.py \
  --before census/round-92/controls/c2-before-tool.py \
  --work <scratch/s-<name>-decoy> --arm-timeout 200 --plant-delay 2
python3 -B census/round-99/c2-cross-arm-probe.py --counter <MUTANT> \
  --probe census/round-98/c2-forgery-probe.py \
  --tool tools/souji-record-agreement.py \
  --before census/round-92/controls/c2-before-tool.py \
  --work <scratch/s-<name>-cross> --arm-timeout 200 --label <name>
```

Full paths (seat scratch `/fast/scratch/hyaku/souji-r99/R99MutC2/`; mutant scripts and the twelve serial logs are copied into `.ufo/waves/round-99/w1/R99MutC2/`).

## Mutants (one edit each, in `_reap_owned` lines 182–194)

All five are small diffs against pristine's gate:

* **m_bb (restore branch (c))**: inserted `elif _is_descendant(pid, os.getpid()): pass` before the `else: continue` — i.e. the r98 subreaper-net branch restored. sha256 `82e2b385923a21b3c3434a94ef0111a3697f0084a9f6408971a68ab0f217eca4`.
* **m_noppid (drop the ppid walk)**: `elif _is_descendant(pid, spawn_pid):` → `elif False:` — ppid-chain descendants are never owned; only the recorded spawn pid (starttime-verified) can be killed. sha256 `5482e0ffb3a816f5821a9a7209aaa117fb175ddf0b2ec79b4a5f6c0bbd9ba1c1`.
* **m_argv (match argv only)**: replaced the whole ownership gate with unconditional `os.kill(pid, SIGKILL)` for every own-uid argv carrier of the token (the r97 rule); the original gate is preserved under `if False:` so the edit is one logical change. sha256 `230d8d234fd5c65806fdca52ed60e3a3edd176af50d10921026ec20719f78bb6`.
* **m_nosttime (drop the starttime check)**: `if st[1] != spawn_st: continue` → `pass` — the recorded pid is killed on pid equality alone, so a recycled pid would kill a stranger. sha256 `44efbc46d099da3ed63b893ccceef1347881499c869e014888bacefb4e7b8a91`.
* **m_spawnonly (kill the recorded pid without the descendant test)**: `elif _is_descendant(pid, spawn_pid):` → `elif False:` — same gate shape as m_noppid (recorded pid only); differs from m_noppid only in which branch label carries the removed predicate. sha256 `14b300cc420771d2da2939f4715af3ad2c0df1eb8c6156f2af63e2cdda3e0698`.

## Baseline (pristine r99 counter, serial)

* Decoy: exit 0; `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0`, `ARMS-SUMMARY arms=20 conform=20`, `DECOY-PLANTED n=83 dead=0 alive=83`, `DECOY-SUMMARY verdict=spared`.
* Cross-arm: exit 0; `ARMS-SUMMARY arms=20 conform=17` (3 non-T1 arms expectedly non-conforming under the other-arm fixture), `T1-REAP survivors 0 planted-killed 0`, `CROSS-ARM-PLANTED n=30 dead=0 alive=30`, `CROSS-ARM-SUMMARY verdict=spared` (carriers ppid=1525/ppid-chain already reaches systemd's 1, argv_token=yes — a counter-descendant outside the T1 spawn chain).

## Results — serial (the table used for the verdicts)

| Counter | Decoy exit / verdict (dead/n) | Cross-arm exit / verdict (dead/n) | Kills either predicate? |
| --- | --- | --- | --- |
| pristine (r99) | 0 / spared (0/83) | 0 / spared (0/30) | — (healthy baseline) |
| **m_bb — restore branch (c)** | **0 / spared (0/83)** | **1 / killed (30/30)** | **KILLED — by cross-arm only** |
| m_noppid — drop ppid walk | 0 / spared (0/83) | 0 / spared (0/30) | **SURVIVES both** |
| m_argv — argv only | 1 / killed (82/83) | 1 / killed (30/30) | KILLED — by both |
| m_nosttime — drop starttime check | 0 / spared (0/83) | 0 / spared (0/30) | **SURVIVES both (no probe exercises pid reuse)** |
| m_spawnonly — recorded pid only | 0 / spared (0/83) | 0 / spared (0/30) | **SURVIVES both** |

Observed summary lines per mutant (serial logs):

* m_bb decoy: `ARMS-SUMMARY arms=20 conform=20`, `DECOY-SUMMARY verdict=spared` (exit 0). Cross-arm: `T1-REAP survivors 0 planted-killed 32` (vs pristine `planted-killed 0`), `CROSS-ARM-PLANTED n=30 dead=30 alive=0`, `CROSS-ARM-SUMMARY verdict=killed` (exit 1).
* m_noppid decoy: spared (exit 0, 0/83). Cross-arm: `planted-killed 0`, spared (exit 0, 0/30).
* m_argv decoy: `DECOY-PLANTED n=83 dead=82 alive=1`, killed (exit 1). Cross-arm: `planted-killed 64`, killed (exit 1, 30/30).
* m_nosttime decoy: spared (exit 0, 0/83). Cross-arm: `planted-killed 0`, spared (exit 0, 0/30).
* m_spawnonly decoy: spared (exit 0, 0/83). Cross-arm: `planted-killed 0`, spared (exit 0, 0/30).

## Verdicts and interpretation

* **m_bb (restore branch (c)) — killed, and only by the cross-arm probe.** The decoy predicate correctly shows the foreign decoy spared (branch (c) cannot reach it: its ppid is the driver, never the counter). The cross-arm probe shows all 30 counter-descendant carriers killed, with `T1-REAP planted-killed 32` against pristine `0`. The cross-arm probe is therefore the sole detector for the exact r99 regression (branch (c) restoration). This is the requested explicit result.
* **m_argv — killed by both, as required** (C2 acceptance: "the r98 CM8 argv-only mutant is still killed by the decoy test").
* **m_noppid and m_spawnonly SURVIVE both predicates — and that is expected, not a missed kill.** Dropping the descendant leg makes the counter kill *less*, not more: the foreign decoy and the counter-descendant carrier are both spared (correctly so, from the predicates' point of view), and the T1 escapee is unreachable from the spawn pid after its parent exits (the open limit R99ExecC2 itself reports), so the predicates observe identical behaviour to pristine. Neither predicate asserts the escapee is actually reaped; the survivors byte is the onlyбеж byte that could expose under-killing, and it counts spawn-chain members only, which is empty in this configuration.
* **m_nosttime SURVIVES both — a coverage finding.** No predicate exercises pid reuse: no decoy or carrier ever occupies the recorded spawn pid after the spawn process dies, so the starttime check is never the binding constraint. A predicate that plants a carrier *on the recycled spawn pid* (same pid, different starttime) is needed to kill this mutant. Reported as a finding, not a defect in the counter.

## Harness / execution notes (honesty)

* The first cross-arm invocation used the probe revision then on disk and returned `inconclusive` (exit 2, `n=0`): the other-arm fixture inherited the pipes (verified with a standalone fixture test: `HUNG (carrier holds pipes)`). The probe predates this seat; ExecC2b later landed a revision that detaches stdio (`dup2` to `/dev/null` in the fork child) and walks `carrier.pid` at any depth. At `--arm-timeout 200` the revised probe is sound — pristine gives spared, 0/30, exit 0, confirmed serially.
* A concurrent batch (five decoys run in one shell loop) produced readings where m_bb and m_noppid appeared to kill foreign decoys (dead=26/61 and 30/61, conform=19, counter preserved at exit 1). Serial re-runs of exactly those two configurations give spared, 0/83, conform=20, exit 0. The concurrent readings were caused by five counter instances sharing the host (overlapping `/proc` argv scans across independently-scoped `--work` dirs), i.e. cross-run interference. **All verdicts above come from the serial runs; the concurrent m_bb/m_noppid numbers are superseded and are reported only so the L1 is not misled if it sees them.**
* One synthetic cross-arm run (my own plant-mechanism check, foreign carrier at ppid-chain already reaching systemd's 1) read `killed` while the concurrent decoy batch was executing; it is not part of the table and is not evidence about any mutant or the pristine counter.
* Restoration evidence: the lane files were never written by this seat — `c2-setup-arms.py` sha256 `03e8a99e…` (identical to the pristine copy taken before any run), `c2-decoy-test.py` `9d06e806…`, `c2-cross-arm-probe.py` `22eda141…` (the ExecC2b revision). No git/jj mutation was performed. No tools were installed or fetched. No subagents were dispatched.

## Which mutants pass both predicates

Three mutants survive both detectors: **m_noppid**, **m_nosttime**, **m_spawnonly**. Two are sub-approximation mutants (they kill less) and are observationally indistinguishable from pristine under the current predicates — see the interpretation. One (m_nosttime) is a genuine coverage hole: pid-reuse is not exercised by either predicate, and this seat names the needed additional probe.

Report: .ufo/waves/round-99/w1/R99MutC2.md
