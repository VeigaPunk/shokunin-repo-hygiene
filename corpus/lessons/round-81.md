# Round 81 — the pointer counter binds census captures to wave subtrees (C1 calibration), the vault tool stops its CLI on a caller's signal (C2 operability)

Attempt 1 (`SoujiR81`). Lane base `b15279bbc3f11ec10fc375a05a08b19cac460d0c` (r80 closed `admitted`, spot-check
committed). Frozen claims, counters and predicates are in `census/round-81/preregistration.txt` and are not
restated here.

## Inherited

The r80 spot-check routed seven defects (`corpus/lessons/round-80-verifier-spotcheck.md` section 5) and the r80
lesson four routes (`## Routed to round 81` (a)-(d)):

- defect 1 (freeze the post-wave quarantine rows and re-measure the R3 front under a fresh freeze with a wave
  attack) → taken as verification V1, not a claim (the R3 bytes already pass their probes, so a claim would pass
  with no work, §9): the frozen r80 counter, its SHELLOPTS=monitor run and the three r80 repair probes are named in
  the preregistration with their expected verdicts before the wave, re-run by the L1 at this base
  (`census/round-81/records/v1-quarantine/`), and attacked by wave seats on the base bytes.
- defect 2 (a receipt binds the bytes it executed, and their mode) → `census/round-81/rec.sh` accepts absolute
  BIND paths and writes `mode=` on every bind line; every scratch-copy receipt of this round binds the copy it ran.
- defect 3 (label registry receipts with the measured revision) → this round's registry receipts are named by the
  revision they measure (`registry-agreement-base.txt` measures the base, the command's `--rev`); the `rev=` line
  stays the recording lane tip by rec.sh design and is not the measured revision.
- defect 4 (registry-agreement red at base and tip, k1=7 k2=1) → base re-measured
  (`census/round-81/records/registry-agreement-base.txt`: `k1=7 k2=1`, EXIT=1); disposition in `## Registry
  agreement` below.
- defect 5 (census receipts bind rec.sh, not the census script) → `census-before.txt` binds
  `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (sha256 `3fb72615…4e30`, mode 755).
- defect 6 (C1 qualifications: NF12/NF14, mode-arm detectors, the counter docstring citing S294) → NF12 is C1 of
  this round; NF14 is a stated limit (reason in the preregistration); the r81 counter docstring names S294 as the
  ground of the mode whitelist; the mode-arm detector rows (NF11b/NF11c) are carried.
- defect 7 (S328 `teaches` names S068, superseded by S075) → recorded here, append-only: S328's `teaches` cell
  should read S075 for field 6; the row is not edited (CORPUS.md rule 2).
- route (c) `tools/souji-vault-verify.sh:213` (S80Connector MEDIUM) → C2 of this round. `tools/souji-census.sh`
  group kill, the stage-2 signal state (S80ExecEvade F3) and SIGKILL to the quarantine front are carried.
- route (d) carried: the r79 gate re-measurement, the check-4 300 s backstop row, r76 K03/K04, the status-trusting
  lane tools.

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=b15279bb… ahead=0 tracked=0
untracked=0`; the watchdog log has no `lane-dead-no-report souji round=81`). No `considerthese/` directory exists
in this lane; no shokuknow theme taken (Assimilation: none).

## Gate

- **S329 admit (A, mined)** — GNU Bash 5.3 Reference Manual, node 3.2.4 Lists of Commands, as installed:
  `/usr/share/info/bash.info.gz` owned by bash 5.3.20-1, sha256
  `cde1a3366897684b0a86fe553687e31d070b7839b19ca98186ffc6e0e105588f` (equal to the r79 capture
  `census/round-79/srcs/bash.info.gz-5.3`), opened 2026-11-07 by the L1; node excerpt
  `census/round-81/srcs/bash.info-5.3-Lists.txt` (decompressed lines 738-770). Decompressed lines 758-760: "the
  standard input for asynchronous commands, in the absence of any explicit redirections, is redirected from
  ‘/dev/null’" (19 words). Grounds the sourced claim C2: the vault tool's CLI call becomes an asynchronous job, so
  it carries an explicit `<&0`; the K-c control without it turns the stdin-reading CLI's answer into `cli=empty`
  (`census/round-81/controls/c2-K-c-no-stdin.txt`, p3).
- Within-scope duplicate check before append: S325 (node 3.7.6 Signals) teaches which signals an asynchronous
  command ignores and the `wait` interrupt, not its stdin; `grep -n 'Lists' corpus/SOURCES.md` finds no row on the
  Lists node. The id S329 was a withdrawn r80 draft that never entered the registry.
