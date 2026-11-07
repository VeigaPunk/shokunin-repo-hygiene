# Round 80 — the pointer counter refuses the r79 wave's false ledger rows (C1 calibration), the quarantine tool answers a caller's signal (C2 operability)

Attempt 1 (`SoujiR80`). Lane base `f80f9368a8a20679438b1dffd72d0faab0ccf194` (r79 closed `rejected-honest-stop`,
spot-check committed). Frozen claims, counters and predicates are in `census/round-80/preregistration.txt` and are not
restated here.

## Inherited

The r79 spot-check routed seven defects (`corpus/lessons/round-79-verifier-spotcheck.md` section 5) and the r79 lesson
four routes (`## Routed to round 80`):

- defect 1 (receipts record their launch disposition; the counter resets inherited dispositions) → instrument part
  taken: `census/round-80/rec.sh` writes a column-0 `launch=` line (SigIgn, SigBlk, pgid, sid, stdin tty) on every
  receipt, and the new C2 counter prints a `# launch` line and resets INT/QUIT/TERM/HUP in every tool child. The r79
  gate counter itself is not re-run (defect 2).
- defect 2 (re-measure the r79 gate C1 under a fresh successor counter before any operability score or capability
  row) → not taken this round; the r79 "signal-safe gate children" capability row stays closure-gated and unearned.
- defect 3 (state launch conditions in the prereg Stated limits) → C2 Stated limits name the inherited-INT condition.
- defect 4 (diagnose before repairing) → no repair commit this round without a probe; the one pre-freeze rule change
  (C1 NF10 draft) was driven by the regression conjunct that refused it (`records/prefreeze-feasibility.txt`).
- defect 5 (seats write only under their seat directory) → wave context forbids lane paths by name.
- defect 6 (C2 survivors NF6b, NF8, NF10, DM01/DM07/DM11) → C1 of this round; NF6a and NF9 carried as stated limits.
- defect 7 (check-4 300 s backstop row; r76 K03/K04; status-trusting lane tools) → carried; route (c)'s
  `tools/souji-quarantine.sh` is taken as C2, `tools/souji-vault-verify.sh` carried.

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=f80f9368… ahead=0 tracked=0 untracked=0`; the
watchdog log has no `lane-dead-no-report souji round=80`). No `considerthese/` directory exists in this lane; no
shokuknow theme taken (Assimilation: none).

## Measured

Staged commits in the order the preregistration binds: P `515d57c8c559d64d0c071cc25b07df0b815bd77a` (counters,
populations, control variants and every control receipt, rec.sh, S327/S328 captures and rows, census-before,
pre-freeze feasibility); F `aaad410f4de2c1b0e98f1a7f305736dfcee5c5ab` (preregistration; freeze-check `--substance
--chronology` `SUMMARY claims=2 findings=0`, `census/round-80/records/freeze-check-at-F.txt`); W1
`bd263c3f7d376e617c2fde5b99793622b0908b53` (C1 counter); W2 `836dac3e336863c57d9d7125837ed22b22d8d044` (C2 tool);
A `a4aa888037922b7b5ccfac7150f156f92af5916e` (after-arms, regressions, diagnosis receipts).

- C1 (frozen harness `census/round-80/c1-false-row-harness.py`, 18 rows): K-a r79 counter mismatches=3 accepted=3
  (NF6b, NF8, NF10; `controls/c1-K-a-r79-counter.txt`) → `records/c1-after.txt` mismatches=0 accepted=0 EXIT=0. K-b
  refuse-all 18/18 on the harness but 3/22 on the r78 regression (`controls/c1-K-b-refuse-all-regress-r78.txt`);
  ablations without-regular NF8, without-capture-root NF10, without-whole NF6b, 1 accepted each. Regressions at W1:
  r78 22/22 + 12/12, r77 35/35 + 7/7, r79 harness 9/9 (`records/c1-regress-*.txt`).
- C2 (frozen counter `census/round-80/c2-signal-counter.py`, 15 rows): K-a base tool mismatches=12 orphans=12, p1-p3
  match (`controls/c2-K-a-do-nothing.txt`); K-b trap-only 12/12, K-c no-session-kill 12/12 → `records/c2-after.txt`
  mismatches=0 errors=0 orphans=0 EXIT=0 (every signal row exits within the 5 s settle with 128 + n: 0.8-3.9 s, the slowest rows ran while the C1 after-arms ran beside the counter). The receipt was launched
  with `&` from a subshell (`launch=` line: SigIgn 0x1000004 = SIGQUIT and SIGXFSZ ignored, SigBlk 0x2 = SIGINT
  blocked); every signal row's `ign=` at delivery is `0000000000000004` (SIGQUIT only, which bash ignores itself),
  so the INT rows measured a trappable INT whatever the launch. Regressions at W2: r13 5/5
  (`records/c2-regress-r13.txt`), r17 total=35 failed=0 skipped=2 (`records/c2-regress-r17.txt`), selftest 108 checks
  0 failed on the committed file (`records/c2-regress-selftest-committed-mode.txt`; see M1 for the first, red run on a
  mode-0644 copy, `records/c2-regress-selftest.txt` 81/51), domain trial v3 identical=yes with 3 RESULT lines per arm
  (`records/c2-domain-trial.txt`; see M2 for v1/v2).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | measurement environment: the C2 selftest conjunct was replayed on a `git show` copy outside the lane (mode 0644); 51 of 81 checks failed for the base tool and the candidate alike — the first A receipt of that conjunct is red for a reason that is not the candidate. The L1 first named the mode as the cause; S80CriticDiscern F3 and S80ExecC2 measured it: chmod 0755 still fails 47 (mode = 4 checks); the rest is layout — the engine and `souji-round9-selftest.sh` are tool-dir siblings, and the tool derives its fleet root from its own location. The diagnosis receipt also binds the lane file's digest while its command ran the base copy (rec.sh binds lane paths only) | `census/round-80/records/c2-regress-selftest.txt` (81/51, candidate copy); `census/round-80/records/diagnosis/selftest-base-mode0644-copy.txt` (81/51, BASE copy); `census/round-80/records/c2-regress-selftest-committed-mode.txt` (108/0, the committed 100755 file) | none: pre-freeze feasibility (Q70) ran the C2 counter only, not the regression conjuncts (`records/prefreeze-feasibility.txt` lists no selftest run) | QUALITY Q145 (replay the committed object in its installed layout — mode, sibling tools, derived roots; feasibility runs every conjunct before F; a receipt binds the bytes it executed). The diagnosis receipt is the failing case: the same command on the base copy fails identically (S80ExecC2 reproduced it from the true base blob e2f2d083), so the defect is the copy; the rule fails whenever a lossy copy is replayed |
| M2 | vacuous equivalence: domain trial v1 compared two empty outputs (both copies, outside the lane, looked for `<copy>/../tools/souji-verify.sh` and exited 1) and printed identical=yes; v2 ran the arms from different locations, and only the lane-located arm printed the live-fleet GUARD note (the tool derives roots from its own path) | `census/round-80/records/diagnosis/c2-domain-trial-v1-vacuous.txt`, `c2-domain-trial-v2-location.txt`; probes `census/round-80/probes/domain-trial-v1-vacuous.sh`, `-v2-location.sh` | none (the r79 domain trial checked check lines, not an expected verdict count) | v3 (`census/round-80/probes/domain-trial.sh`) installs both arms in the same layout, pins the engine and ledger, and requires one RESULT line per target in both arms; shown able to fail: two empty arms now print identical=no, EXIT=1 (`census/round-80/records/diagnosis/domain-trial-v3-refuses-empty.txt`); QUALITY Q145 |
| M3 | rule over-fit caught before freeze: the first NF10 draft ("the target keeps the token's whole path below round-<N>") refused the legitimate captures r78 L15 and r77 P31, which flatten the wave subdirectory | `census/round-80/records/prefreeze-feasibility.txt` | the regression conjunct (r78 22/22, r77 35/35) in pre-freeze feasibility — it worked | replaced by the capture-root rule before P; recorded so the closure can see the rule was shaped by the regression, not by the target rows |

## Gate

- **S327 admit (A, mined)** — git-ls-tree(1) as installed: `/usr/share/man/man1/git-ls-tree.1.gz` owned by git
  2.56.0-1 (`pacman -Qo`), sha256 `c0e10ef543481ac2569e665eca314067c394b10d4965f78e96e85ce79a1a7e86`, opened
  2026-11-07 by the L1 (capture `census/round-80/srcs/git-ls-tree.1.gz-2.56.0`). Decompressed lines 252-255 (one
  sentence across roff lines), FIELD NAMES objecttype: "The type of the object (commit, blob or tree)" (9 words;
  S80CriticDiscern F7 corrected the span from "252"; the row keeps its P text and this Gate carries the span); line 204, the default format
  "%(objectmode) %(objecttype) %(objectname)%x09%(path)". Grounds the sourced claim C1 (range members must be blobs of
  a regular-file mode).
- **S328 admit (A, mined)** — setsid(1) as installed: `/usr/share/man/man1/setsid.1.gz` owned by util-linux 2.42.4-1,
  sha256 `614ae07f37d95c2e250b32c812835dba09e91144f9cbf520efa586cac7385243`, opened 2026-11-07 by the L1 (capture
  `census/round-80/srcs/setsid.1.gz-util-linux-2.42.4`). Decompressed line 37: "The command calls fork(2) if already a
  process group leader. Otherwise, it executes a program in the current process." (19 words; the first draft
  quoted the fork sentence without the "Otherwise" clause that carries "execs in place" — S80CriticDiscern F2,
  S80Scribe MEDIUM-1 — corrected here and in the knowledge entry; the registry row keeps its P text, append-only). Grounds C2's front/worker split (the
  worker is an asynchronous job, not a group leader, so setsid execs in place and `$!` is the session id). Cited by
  `corpus/knowledge/gate-signal-handling.md`.
- **Rejected (L1): draft S329, proc_pid_stat(5) as installed** (man-pages 6.19-1, sha256 `d2b5d09d…b002b51`, opened
  2026-11-07, lines 107-108 "(6) session %d / The session ID of the process.") — a within-scope duplicate of S068
  (the same page and field, web copy opened 2026-10-20, scope "field order and units of pgrp, session and
  starttime"); withdrawn before commit and S068 cited instead (CORPUS.md rule 2). Flip: none needed. S80ScoutSources
  HIGH-1: S068 is superseded by S075 (same page and field), and citing S068 from the knowledge entry, whose path is
  not in S068's used-by, turned the lane's registry gate red (`tools/souji-registry-agreement.py` K1); the entry and
  the tool now cite S075.
- **Row cells touched old→new (CORPUS.md rule 2: status/recheck/used-by only):** S075 used-by `corpus/lessons/round-18.md,
  corpus/knowledge/process-residue-observations.md` → `…, corpus/knowledge/gate-signal-handling.md`; S294 used-by
  `corpus/lessons/round-63.md` → `corpus/lessons/round-63.md, corpus/lessons/round-80.md` (S294, git-fast-import(1)
  mode list 100644/100755/120000/160000/040000, re-read from its row this round, is what grounds the C1 counter's
  100644/100755 whitelist — S327's page names no mode constants, S80ScoutSources MEDIUM-1; the frozen counter's
  docstring cites S327 only, a qualification). The S327/S328 anchor cells were edited in place after P during
  integration (S80ScoutSources LOW-2) and are restored to their P bytes; the corrections live in this Gate.
- No other row's status, recheck or used-by cell changed. Within-scope duplicate check before append: S071
  (git-cat-file -e, existence of rev:path) and S078 (git-ls-tree -r/-z enumeration as the gate uses it) are other
  scopes of the same command family than S327 (object type and mode of an entry); `git show master:corpus/SOURCES.md
  | grep -F setsid` hits only S067/S074 prose, no setsid(1) row.
- Census: before `census/round-80/records/census-before.txt` (souji ok, EXIT=0, 87 W04 lines).

## Wave

One v1 wave `w1`, 12 seats (connector 1, scout 1, executor 3, mutation-tester 2, reviewer 1, critic 2, sentinel 1,
scribe 1; attack seats reviewer + critics + mutation-testers = 5 of 12, 42 %), validated under
`scripts/hyaku/ufo-wave-policy.json` (band 8-16, spawn 12) and dispatched through the inline handoff
(`w1.ready.dispatched` 04:39:56). Seat files are mirrored under `census/round-80/records/wave-w1/`.

| seat | verdict | disposition |
|---|---|---|
| S80Connector | C1/C2 SEPARABLE; MEDIUM `tools/souji-vault-verify.sh:213` foreground `$(timeout …)` orphans the CLI group on TERM/HUP; LOW `tools/souji-census.sh` group kill misses timeout's groups; 15 sibling rows exposed | routed r81 (lane tools); sibling rows documented only |
| S80ScoutSources | S327/S328 sha256 MATCH, quotes verbatim, setsid.c fork condition confirmed; HIGH-1 the knowledge entry cited S068 (superseded by S075, entry not in its used-by): registry K1 7 → 8 at the tip; MEDIUM-1 S327 names no mode constants (S294 does); MEDIUM-2 a comm holding `) ` mis-parses; MEDIUM-3 a comm holding a newline escapes the scan; LOW-2 row cells edited in place | HIGH-1 fixed (S075 cited, used-by extended, K1 back to the base count — report); MEDIUM-1 recorded with S294; MEDIUM-2 REFUTED by the L1 (a process named `a) b.sh` parses to its true sid: the strip runs to the LAST `) `, which is the comm's end); MEDIUM-3 confirmed and repaired at R3 (probe D3 fails at R2); LOW-2 cells restored |
| S80ExecC1 | C1 HOLDS: every receipt reproduces byte-for-byte, fixtures deterministic, no r77/r78 ITEM verdict moves under the r80 counter; LOW `rev=` lines of the A receipts name the lane tip at run time (W2), not W1; LOW the population adds a `rev` column to the r79 rows | LOW-1 recorded (counter bytes bound by sha256 lines); LOW-2 accepted: "unchanged" in the prereg means row content, the file is not byte-identical |
| S80ExecC2 | C2 HOLDS (foreground and `&` launch: the counter itself started with SIGINT ignored and every row still matched — the per-child reset works); selftest mechanism confirmed and refined (0644 51, 0755 47, layout); MEDIUM the diagnosis receipt binds the wrong bytes; v3 trial not vacuous on real bytes | M1 rewritten with the measured cause; binding defect disclosed (rec.sh binds lane paths only) |
| S80ExecEvade | frozen target HOLDS; timing probes (between targets, double signals, a 48-rep early burst) 0 orphans; double-fork and setpgid descendants ARE killed (session); F1 MEDIUM a signal after the worker finished printed a false SIGNAL and exit 143; F2 MEDIUM `SOUJI_Q_SESSION=<own sid>` / `SOUJI_Q_WORKER=1` under a session leader skip the front; F3 LOW stage-2 signal leaves the source moved with no RESULT; F4 LOW front mktemp failure exits 2 (base 1) | F1 repaired at R (signals ignored after `wait`); F2 repaired at R (worker needs its front as parent; nested branch needs the session leader to run this file; probe arm spoof-session); F4 repaired at R2 (probe arm tmpdir-missing); F3 recorded as a limit |
| S80MutTool | 12 mutants, 9 killed; M01 (no SIGSTOP) and M02 (single pass) equivalent under any static row; M09 (handler `rm -rf`) redundant with the EXIT trap | qualification: the STOP pass and repeat passes are unmeasured; M09 left (harmless redundancy) |
| S80MutCounter | every C1 number reproduces, but the frozen rows kill 3 of 9 rule mutants (the 100755/120000 mode arm is unseen: no symlink member row); MEDIUM a byte-equal decoy under `census/round-32/decoy/` is ACCEPTED (NF12); LOW a path in `( … )` is accepted (NF14); NF11b/NF11c/NF13/NF15b/NF16 refused | qualification on C1; NF12 is inside the prereg's "census/round-<N>" wording but was unmeasured: routed r81 with NF14 and the six new detector rows |
| S80Reviewer | C1 and C2 predicates HONOURED as frozen; the A-arm re-measurements are the frozen predicate, not a changed rule; MEDIUM env spoof (as S80ExecEvade F2); LOW job-control fork path; LOW a signal between `&` and `$!`; LOW `_regular` passes a pathspec; LOW the NF10 residual | MEDIUM and the fork path repaired (R); the `&`→`$!` window recorded as a limit; pathspec LOW routed r81 |
| S80CriticClaims | C1 QUALIFIED (regression fit, the census carve-out needed by 14 real rows, decoy residual LOW); C2 QUALIFIED: MEDIUM harm — under job control the front exits 0 with no work (pty `bash -m`), base runs; strictest reading of the selftest conjunct is red (frozen command on a copy), most lenient green | the harm is real at W2 and was repaired after the wave (R, probe failing-before at W2); both readings are reported to the closure |
| S80Sentinel | P1-P6 PASS (pty ^C, byte-identical no-signal output, 0700 private dir holds ERRTMP and selftest fixtures, no tty dependence, no new path echo); F1 MEDIUM silent false success under SHELLOPTS=monitor; F2 MEDIUM SIGKILL to the front leaves the worker session; F3 MEDIUM a worker killed without the trap leaks its children; F4 MEDIUM env fail-open; F5 LOW stale sid | F1/F4 repaired at R, F3 at R2 (probe arm worker-killed), F5 closed by ignoring signals after `wait`; F2 recorded as a limit (untrappable; base equally leaves its children) |
| S80Scribe | three drafts; MEDIUM-1 S328 quote truncated; MEDIUM-2 "until none is left" overstated; MEDIUM-3 exec-in-place precondition unstated; LOW-4 "INT was held" inferred | all four applied to the knowledge entry (and the row/lesson quote); Q144/Q145 and the capability row were already integrated from the L1's own text |
| S80CriticDiscern | sources agree 3/3 (S329 withdrawal agreed); F1 HIGH job-control launch; F2 S328 quote; F3 M1 cause misstated (4 checks are mode) and the receipt binds the wrong bytes; F4 v3 passes an all-blocked pair; F5-F7 LOW | F1 repaired (R); F2, F3, F5, F7 applied; F4 recorded as a qualification of the trial guard and routed; F6 (M3's refusing draft not archived) accepted as a gap |

## Repairs after the wave (not the claim's measurement)

C2's claim is judged at A on the W2 bytes. The wave found a harm at W2 outside the frozen rows (M4); the tool was
repaired after the wave, each repair behind a probe that fails on the earlier bytes:

- D `37ab234e` probe `census/round-80/probes/front-launch-modes.py` (SHELLOPTS=monitor q4 and p1 through the frozen
  counter's own run_row; a spoofed `SOUJI_Q_SESSION`): 3/3 arms fail at W2 (`records/repair/front-launch-modes-at-W2.txt`).
- R `8ba93218` (tool): `set +m` before the launch; the worker requires sid==pid and parent==front; the nested branch
  requires the session leader's argv to name the tool; signals after `wait` are ignored; kill-pass exhaustion is
  reported. At R: probe 3/3, frozen counter 15/15 (also with SHELLOPTS=monitor), r13 5/5, selftest 108/0, r17 35/0,
  trial identical (`records/repair/*-at-R.txt`).
- D2 `330197b9` probe `census/round-80/probes/front-worker-death.py` (worker SIGKILLed mid-digest; TMPDIR missing):
  2/2 arms fail at R (`records/repair/front-worker-death-at-R.txt`).
- R2 `97289f81` (tool): sweep the worker session when the worker died by a signal; front mktemp failure exits 1 like
  the base. At R2: both probes pass, frozen counter 15/15 (also with SHELLOPTS=monitor), r13 5/5, selftest 108/0, r17
  35/0, trial identical (`records/repair2/`).

- D3 `f6fcddb5` probe `census/round-80/probes/front-comm-newline.py` (a newline-named grandchild at the file digest):
  fails at R2 (`records/repair2/front-comm-newline-at-R2.txt`, survivors=1). Its first version marked at fork time and
  passed by a race (`records/diagnosis/front-comm-newline-racy-v1-at-R2.txt`, probe `-racy-v1.py`), M8.
- R3 `4a499e9a` (tool): q_proc_sid reads the whole stat file; S075 cited. At R3: all three probes pass, frozen counter
  15/15 (also with SHELLOPTS=monitor), r13 5/5, selftest 108/0, r17 35/0, trial identical (`records/repair3/`).

## Mistakes (wave)

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M4 | an unmeasured precondition in the candidate: the front assumed setsid execs in place (S328's own "Otherwise" clause) and nothing checked it; with job control on, the tool exited 0 with no verdict — a harm against the base, which ran correctly | `census/round-80/records/repair/front-launch-modes-at-W2.txt` (3/3 arms fail on W2), S80CriticDiscern F1, S80CriticClaims item 10, S80Sentinel F1 | the wave (three non-author seats); no frozen row varies the launch | R `8ba93218`: `set +m`, worker refuses unless sid==pid and parent==front; the probe fails on W2 and passes at R/R2 (`records/repair/front-launch-modes-at-R.txt`, `records/repair2/front-launch-modes-at-R2.txt`); the frozen C2 counter run with SHELLOPTS=monitor is 15/15 at R2 (`records/repair2/c2-monitor-at-R2.txt`) |
| M5 | a quote cut before the clause that carries the claim (S328 without "Otherwise, it executes a program in the current process.") | S80CriticDiscern F2, S80Scribe MEDIUM-1 | the wave | row, lesson and knowledge carry the 19-word quote with the clause |
| M6 | a citation of a superseded row that the lane's own registry gate refuses: the knowledge entry cited S068, which S075 supersedes and whose used-by does not list the entry (`souji-registry-agreement.py` K1 7 → 8) | S80ScoutSources HIGH-1 (reproducer at `79fcc73d`) | the registry gate exists (`tools/souji-registry-agreement.py`) but the L1 did not run it before landing I | cite S075 and extend its used-by; the gate is run at the tip before the report (see the report's Sources section); it fails on the I bytes, so the check can fail |
| M7 | in-place edits of landed registry anchor cells (S327 span, S328 quote) | S80ScoutSources LOW-2; CORPUS.md rule 2 | none (the census does not diff anchor cells against the landing commit) | cells restored to their P bytes; corrections recorded in the Gate |
| M8 | a probe that passed by a race: the newline-comm probe marked at fork time, so TERM could land while the child was still a bash fork named `sha256sum`, and the arm passed at R2 | `census/round-80/records/diagnosis/front-comm-newline-racy-v1-at-R2.txt` (ok=y at R2) vs `records/repair2/front-comm-newline-at-R2.txt` (ok=n, survivors=1, 3 of 3 manual repeats) | the L1's own instrumented re-run (a debug wrapper slowed the arm and the survivor appeared) | v2 marks only after the child's comm is the newline name; a failing-before probe is run at least three times before it is trusted as failing (same rule as r79 M4) |

## Routed to round 81

- (a) C1 counter rows the wave built: NF12 (a byte-equal decoy under `census/round-<N>/` other than the capture
  subtree is accepted — bind the capture root to its capture subtrees and re-derive the 14 real MOVED rows), NF14
  (a path inside `( … )`), and detector rows for the mode arm (NF11b symlink, NF11c gitlink), the before-check
  (NF13/NF13b), the punctuation allowance (NF15b) and `fleet:` symlinks (NF16) (S80MutCounter); `_regular` passing a
  pathspec (S80Reviewer LOW).
- (b) C2 rows the frozen population lacks: a launch-mode row (SHELLOPTS=monitor), a worker-killed row, the git-blob
  digest call site (`tools/souji-quarantine.sh` intro-blob digest, reachable in dry-run), a fork-tail row for the
  STOP/repeat passes (S80MutTool M01/M02; likely equivalent), and the v3 trial's expected-verdict vector
  (S80CriticDiscern F4).
- (c) `tools/souji-vault-verify.sh:213` and `tools/souji-census.sh` group kill (S80Connector); the stage-2 signal
  state (S80ExecEvade F3); SIGKILL to the front (S80Sentinel F2).
- (d) carried: the r79 gate re-measurement (r79 defect 2), the check-4 300 s backstop row, r76 K03/K04, the
  status-trusting lane tools.

