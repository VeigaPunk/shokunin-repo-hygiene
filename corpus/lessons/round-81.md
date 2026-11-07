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

## Wave

One v1 wave `w1`, 13 seats (connector 1, scout 1, executor 4, mutation-tester 2, reviewer 1, critic 2, sentinel 1,
scribe 1; attack seats reviewer + critics + mutation-testers = 5 of 13, 38 %), validated under
`scripts/hyaku/ufo-wave-policy.json` (band 8-16, `ufo-swarm-wave-dispatch-v1`, spawn 13) and dispatched through the
inline handoff (`w1.ready.dispatched` 06:29:32; queued ~8 min for fleet slots). WAVE-DONE received; 13 of 13 reports
written, 0 dead seats. Seat files are under `.ufo/waves/round-81/w1/` (committed as wave evidence).

| seat | verdict | disposition |
|---|---|---|
| S81Connector | C1/C2 SEPARABLE; MEDIUM `tests/fixtures/r17-jj-receipts.sh` 240 s `$(timeout …)` runners orphan on signal; LOW the W2 mktemp-failure foreground fallback; `souji-verify.sh`/`souji-census.sh` hold no `$(timeout)` (the r80 hypothesis falsified); 15 sibling rows | fallback is a stated limit; r17 runner routed r82; sibling rows documented only |
| S81ScoutSources | S329 HOLDS (byte-equal excerpt, host behaviour matches), admit; S326 forwards TERM to child and group; F1 MEDIUM: a background timeout inherits SIGINT ignored and installs no INT handler — group-INT leaves timeout and the CLI alive; the C2 INT rows pass because the tool's trap turns INT into a group TERM; F2 quote count 17 not 19; F3 anchor drops the job-control precondition (the scope cell states it); S294 grounds the mode whitelist | F1 recorded in Q147 and the knowledge entry's mechanism; F2 corrected in the Gate (I2); F3 accepted (scope cell carries it) |
| S81ExecC1 | C1 reproduced in full; fixture revs identical across runs; no r77/r78 ITEM moves r80 → r81; 14/14 real MOVED rows pass `_capture_ok` | none needed |
| S81ExecC2 | C2 reproduces (fg, `&`); controls, selftest, r17, domain trial reproduce; an extra real-bytes trial reaching cli_claim is byte-identical over 5 CLI states; HIGH: under `SHELLOPTS=monitor` v7/v8 leave 1 survivor (the stub's job-controlled grandchild) | same finding as the L1's M4 (found independently); disclosed, not repaired; routed r82 (kill by descendant tree, frozen before timeout's group can be left) |
| S81ExecEvade | no claim violation: early signal, double signals, signal during the 2 s poll, TERM-ignoring CLI (KILL at 2.7 s), --json, two targets, 8 MB output, TMPDIR odd names — all inside the contract; CLI setsid = stated limit; found the vault-path write (already repaired at R); at R: frozen counter 12/0/0 and its probes green; LOW windows before the traps arm and after `wait` (nothing left running) | R confirmed by a non-author seat; windows recorded |
| S81ExecV1 | V1 HOLDS 4 of 5 replays; MEDIUM: one monitor replay of the frozen r80 counter failed once (q4 not exited at the 5 s settle, 1 survivor), the rerun was green — a tail event (1 in 7 observed); LOW pty wrapper SIGKILLs the front (stated SIGKILL limit, TMPDIR litter); LOW nohup/HUP ignored on entry; the r80 front beats the pre-r80 tool under every varied shape | V1's monitor expectation is not stable: recorded as a V1 finding, routed r82 (settle tail of the session sweep under job control) |
| S81MutTool | W2: 11 mutants, 7 killed; M02 pid-only kill equivalent (S326); M03 (no KILL fallback) and M05 (traps not reset after the call) survive — not equivalent, rows missing (`v9-term-ignoring-cli`, `p5-late-term` proposed, M03 reproduced); M09 equivalent; at R: cli_tmp_ok mutants N2/N4 killed by probe D, N1 (inside-vault subdir) and N3 (hint loop) survive — two arms proposed, both pass on R | missing rows routed r82; the closure sees that the KILL fallback and the trap reset are unmeasured branches (M3) |
| S81MutCounter | C1 holds; mutants M1/M3/M4/M5 killed, M2 killed only by regressions, M6a/M6b equivalent, M7 (census-token guard) and M8 (`records/wave-` → `records/`) survive; MEDIUM: a decoy in the token's OWN round tree (`.ufo/waves/round-32/decoy/…`, NF-F/NF-G/PF-4) is accepted — the r81 rule never runs there; LOW: the prereg's stated-limit example `waves/x/a2w1/…` is REFUSED (the rule is stronger than the limit says), its true instance is a partial-suffix decoy (PF-1) | the own-tree decoy class and M8's missing killer row routed r82; the stated-limit wording error recorded here (prereg not edited) |
| S81Reviewer | C1 and C2 HONOURED as frozen; no frozen file changes after F; every receipt digest matches; trailing-newline semantics unchanged; LOW stale `$!` fallback in the trap; LOW foreground fallback unrowed; LOW the stated limit names only INT as untrappable-on-entry (TERM/HUP too) | stale `$!` routed r82 (needs a deterministic probe); others recorded |
| S81CriticClaims | C1 HOLDS, QUALIFIED (the suffix binding's only pressure is NF12c, a decoy the L1 built; NF12c/NF12d falseness is stipulated); C2 HOLDS for the default launch, QUALIFIED on launch mode; no harm; no-signal stdout byte-identical incl. mktemp-failure and closed stdin; LOW SKILL "removed on every exit" overstated | qualifications carried to the report; SKILL wording corrected |
| S81Sentinel | P on file mode, kill target, `<&0`, safety rails; LOW-1 the private file lands under a vault path when TMPDIR is inside the vault (rail "Nothing is ever written under a vault path" broken at W2); LOW-2 other terminating signals leak the file; LOW-3 reopen-by-name (no cross-user impact); LOW-4 stale `$!` | LOW-1 repaired at R behind probe D (3/3 fail at W2, 3/3 pass at R); LOW-2..4 routed r82 |
| S81CriticDiscern | sources agree (S329 admit, not a dup of S325); defects 1, 2, 4, 7 discharged, 3/5/6 partly; F1 cited receipts not yet committed (committed at I2 `c25f000f`); F2 `_regular`/intro-blob/fork-tail had no disposition; F3-F6 LOW | F1 closed by I2; F2 carried lines added; F3/F4/F5/F6 applied in the Gate and limits |
| S81Scribe | drafts; Q147 lacked cwd and overstated rowed properties; Q146 "per allowed shape" unmet (no built wave/ row); knowledge section over 25 lines | Q146/Q147 rewritten; section length kept (it carries the M4 limit) |

## Repairs after the wave (not the claim's measurement)

C2's claim is judged at A on the W2 bytes. The wave and the L1 found one harm at W2 outside the frozen rows:

- D `398e568c` probe `census/round-81/probes/tmpdir-in-vault.py` (TMPDIR equal to, inside or an ancestor of the vault
  directory, with and without the `SOUJI_VAULT` hint; a sibling TMPDIR as positive control): 3 of 4 arms fail at W2
  in 3 of 3 runs (`records/repair/tmpdir-in-vault-at-W2-run{1,2,3}.txt`; the CLI saw `souji-vault-cli.XXXXXX` under
  the vault), 4/4 pass at base (`tmpdir-in-vault-at-base.txt`). A harm against the base: the tool's own rail.
- R `ef76a14f` (tool blob `89a2ed8c…`): `cli_tmp_ok` — when TMPDIR and the row's vault directory or the hint are not
  disjoint, the CLI call runs in the foreground as at base. At R: probe D 4/4 in 3 of 3 runs, frozen C2 counter
  12/0/0, selftest 57/0 on the committed file, r17 37/0/0, domain trial identical 3/3 (`records/repair/*-at-R*`).
  Non-author: S81ExecEvade re-ran the frozen counter and its probes at R (12/0/0); S81MutTool's mutants N2/N4 die on
  probe D, N1/N3 survive (two arms missing, routed). Cost: in the refused configuration a signal during the call
  leaves the CLI group as at base (S81ExecEvade: 3 survivors).

## Routed to round 82

- (a) C2 rows the frozen population lacks: a launch-mode row (`SHELLOPTS=monitor`; M4, S81ExecC2 HIGH) with a kill
  by descendant tree taken before the CLI can leave timeout's group; `v9-term-ignoring-cli` (KILL fallback, M03) and
  `p5-late-term` (trap reset, M05); probe D's two missing arms (inside-vault subdir, hint root); the stale `$!`
  fallback; other terminating signals leaking the private file; the windows before the traps arm.
- (b) C1: a decoy in the token's own round tree (NF-F/NF-G/PF-4, S81MutCounter MEDIUM), a killer row for M8
  (`census/round-<N>/records/<non-wave>/`), the partial-suffix instance of the stated limit (PF-1).
- (c) V1: the r80 front's monitor-mode settle tail (S81ExecV1 MEDIUM, 1 in 7); `tests/fixtures/r17-jj-receipts.sh`
  240 s runners (S81Connector).
- (d) carried: the `_regular` pathspec, the quarantine intro-blob digest row, the fork-tail row, the r79 gate
  re-measurement, the check-4 300 s backstop row, r76 K03/K04, the status-trusting lane tools.
