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
  ground of the mode whitelist; the r80 wave's detector rows NF11b/NF11c (mode arm), NF13/NF13b (before-check),
  NF15b (punctuation) and NF16 (`fleet:` symlinks) are carried, not rows — the r80 counter already refuses each
  (`census/round-80/records/wave-w1/seats/S80MutCounter.md` lines 21-30, all REFUSED); their value is mutant
  coverage, which this round does not claim.
- defect 7 (S328 `teaches` names S068, superseded by S075) → recorded here, append-only: S328's `teaches` cell
  should read S075 for field 6; the row is not edited (CORPUS.md rule 2).
- route (c) `tools/souji-vault-verify.sh:213` (S80Connector MEDIUM) → C2 of this round. `tools/souji-census.sh`
  group kill, the stage-2 signal state (S80ExecEvade F3) and SIGKILL to the quarantine front are carried.
- route (d) carried: the r79 gate re-measurement, the check-4 300 s backstop row, r76 K03/K04, the status-trusting
  lane tools.
- carried with no work this round (S81CriticDiscern F2: the r81 planned line and route (a)/(b) named them): the
  `_regular` pathspec of the pointer counter (S80Reviewer LOW; `_regular` is byte-identical r80 → r81, no row
  holds a member name with pathspec magic); the quarantine intro-blob digest call site as a C2 row; the fork-tail
  row for the quarantine STOP/repeat passes (S80MutTool M01/M02).

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
  ‘/dev/null’" (17 words, `wc -w` on the joined quote; the first Gate draft said 19, S81CriticDiscern F3). Grounds the sourced claim C2: the vault tool's CLI call becomes an asynchronous job, so
  it carries an explicit `<&0`; the K-c control without it turns the stdin-reading CLI's answer into `cli=empty`
  (`census/round-81/controls/c2-K-c-no-stdin.txt`, p3).
- Within-scope duplicate check before append: S325 (node 3.7.6 Signals) teaches which signals an asynchronous
  command ignores and the `wait` interrupt, not its stdin; `grep -n 'Lists' corpus/SOURCES.md` finds no row on the
  Lists node. The id S329 was a withdrawn r80 draft that never entered the registry; `corpus/lessons/round-80.md`
  line 80 still names that draft (proc_pid_stat(5)) as "S329", so a `grep S329` meets two sources — the registry
  row (bash Lists) is the only S329 that exists (S81CriticDiscern F6; precedent: r15 draft S047).
- Pre-freeze drafts vs committed candidates (S81CriticDiscern F4): the C1 draft measured in
  `census/round-81/records/prefreeze/c1-*.txt` (sha256 `ec2578a2…`) is the committed counter minus its docstring
  lines 13-15 (the S294 citation note; `sed '13,15d' census/round-81/c1-pointer-counter.py` reproduces it); the
  C2 draft (`ba61e912…`) is byte-equal to the committed W2 tool.
- **Row cells touched old→new (CORPUS.md rule 2: used-by only; each citing entry re-read this round and its
  citation matches the row's scope):** S062 used-by `corpus/lessons/round-17.md` → `+ corpus/knowledge/git-discovery-sources.md`
  (line 34 cites S062 for the blocking FIFO open); S110 `corpus/knowledge/quarantine-staging-no-copy-r23.md` →
  `+ corpus/knowledge/quarantine-restore-path-reoccupied.md` (source line 2, rename(2) NOREPLACE); S251
  `corpus/knowledge/git-strict-descendant-relation-r40.md` → `+ corpus/knowledge/control-chronology-binding.md,
  corpus/knowledge/freeze-record-substance-binding.md` (both cite `--is-ancestor`); S298
  `…caller-env-routes-receipt-writer.md, …common-dir-route-receipt-writer.md` → `+
  corpus/knowledge/replace-ref-receipt-writer.md` (source line 3, git(1) ENVIRONMENT); S321
  `corpus/knowledge/filter-filemode-witness.md` → `+ corpus/knowledge/git-discovery-sources.md` (line 35, add_patterns()
  open). No status or recheck cell changed.

## Measured

Staged commits in the order the preregistration binds: P `804f132ef717d96157c107e219a254286644b706`, F
`0b1aeaf1c1bb11605bb9e139116323f5680b1a1c` (freeze-check `--substance --chronology` `SUMMARY claims=2
findings=0`, `census/round-81/records/freeze-check-at-F.txt`), W1 `308bc77bddc725aa8f302e4f62746bde3f843f56` (C1
counter), W2 `7076ed2d12faf82e9c762f49d627b84ae549fbd1` (C2 tool), A `cb14eae71c02d51d2e071628ac4c882f01daf844`.

- C1 (frozen harness `census/round-81/c1-false-row-harness.py`, 25 rows): K-a r80 counter mismatches=3 accepted=3
  (NF12, NF12c, NF12d) → `records/c1-after.txt` mismatches=0 accepted=0 refused_true=0 EXIT=0. K-b refuse-all
  refused_true=3 (TF1-TF3), K-c without the suffix binding accepted=1 (NF12c). Regressions at W1: r78 22/22 +
  12/12, r77 35/35 + 7/7, r79 harness 9/9, r80 harness 18/18.
- C2 (frozen counter `census/round-81/c2-vault-signal-counter.py`, 12 rows): K-a base mismatches=8 orphans=8 (v1-v8;
  p1-p4 match) → `records/c2-after.txt` mismatches=0 errors=0 orphans=0 EXIT=0; K-b trap-only 8/8; K-c without `<&0`
  1 (p3 `cli=empty`). Regressions at W2: selftest on the committed lane file 57 checks 0 failed
  (`records/c2-regress-selftest.txt`), r17 total=37 failed=0 skipped=0 (`records/c2-regress-r17.txt`), domain trial
  identical, 3/3 verdicts (`records/c2-domain-trial.txt`; the probe refuses an empty pair,
  `records/diagnosis-domain-trial-refuses-empty.txt`, EXIT=1).
- V1 at base (`records/v1-quarantine/`): frozen r80 counter 15/15, 15/15 under SHELLOPTS=monitor; front-launch-modes
  3/3, front-worker-death 2/2, front-comm-newline 1/1 pass.

## Registry agreement

`tools/souji-registry-agreement.py` (frozen r29 instrument, `--list-rev b8cb4b31`): base `k1=7 k2=1`
(`census/round-81/records/registry-agreement-base.txt`) → at I `f6f699de` `k1=1 k2=1`
(`records/registry-agreement-at-f6f699de.txt`, named by the measured revision). The five used-by repairs above
close six K1 findings. The two left are recorded accepted-red, with reasons: K1 `cited-no-row S146` — the token
sits in the provenance prose of `corpus/knowledge/origin-record-format-gvfs-r40.md` line 1 ("staged id S146",
the shokuknow package id the entry was re-pointed FROM), not a citation; the frozen instrument reads every S### on
a `source:` line and cannot tell them apart; rewriting the entry to hide the token would game the instrument.
K2 `rewrote-not-appended SCORECARD.md` — SCORECARD was rewritten in place after the r29 list revision (history;
not repairable without rewriting history). Flip: a successor instrument that parses citations by `S### —` lead
position, or an operator ruling on K2.

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | registry row format: the first S329 draft's scope cell held a literal double pipe (the list operators), so the row parsed as 13 fields | pre-commit `scripts/sources-census.sh validate` printed `souji E01 S329 fields=13` (scratch run before P; the committed row is the fixed one) | the census E01 check — it fired | scope cell rewritten without pipes before P; the census is run before every registry commit (it failed here, so it can fail) |
| M2 | instrument parse defect: the first C2 counter read the `cli=` state from the `VERIFIED(...)` line, but the tool prints it in the `VERDICT` record's evidence; all four no-signal rows were red on the base tool | reconstructed after freeze as a diagnosis copy `census/round-81/probes/c2-counter-m2-first-parse.py` (the frozen counter with the first parse restored): `census/round-81/records/diagnosis-m2-first-parse-at-base.txt` p1-p4 `state=- match=no`, `mismatches=12`, EXIT=1 | the positive rows run against the base tool before freeze (a positive control that fails on the do-nothing tool is an instrument defect, Q70) — it fired | parse the single `VERDICT` record's evidence field; p1-p4 match at base in `controls/c2-K-a-do-nothing.txt` |
| M3 | untested branch shipped with the claim: the trap's group kill and its KILL fallback have no row that needs them — a pid-only draft scores 12/0 because timeout forwards the signal to its group (S326) | `census/round-81/records/prefreeze/c2-pid-only-kill-draft.txt` | none before freeze (Q70 measures the target, not each branch's necessity) | disclosed in the preregistration Stated limits and the knowledge entry; routed to the wave's mutation seat and r82 (a TERM-ignoring CLI row, a signal before timeout's handlers) |
| M4 | a launch mode the frozen rows never vary, found by the L1 after A (r80 M4's class again): with `SHELLOPTS=monitor` exported by the caller, the tool's environment carries job control into the CLI, whose own `sleep 600 &` then runs in a process group of its own, outside timeout's group; the W2 trap's group kill misses it | `census/round-81/records/launch/c2-at-W2-monitor.txt` (v7, v8 `survivors=1`, `mismatches=2 orphans=2`, EXIT=1); the same counter launched with `&` is 12/0 (`c2-at-W2-bg.txt`); the base under the same launch leaves 3-5 survivors on those rows and 8 orphan rows in all (`launch/c2-K-a-base-monitor.txt`), so this is a residual limit, not a harm against the base | the r80 lesson's M4 rule ("vary the launch") was applied to the counter's own launch in the r80 instrument, not written into this round's frozen rows; it is the prereg's stated limit "a CLI descendant that leaves timeout's group itself", reached through an inherited SHELLOPTS | not repaired inside the claim (the frozen rows and predicate are unchanged); routed to r82: a launch-mode row (SHELLOPTS=monitor, `bash -m`) for the vault tool, and a kill by membership that a job-controlled CLI cannot leave (the r80 session front, or the nonce-free equivalent: the CLI's session) |
