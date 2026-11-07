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
| M1 | measurement environment: the C2 selftest conjunct was replayed on a `git show` copy (mode 0644); the selftest runs `"$SELF"` directly, so 51 of 81 checks failed with rc 126 for the base tool and the candidate alike — the first A receipt of that conjunct is red for a reason that is not the candidate | `census/round-80/records/c2-regress-selftest.txt` (81/51, candidate copy); `census/round-80/records/diagnosis/selftest-base-mode0644-copy.txt` (81/51, BASE copy); `census/round-80/records/c2-regress-selftest-committed-mode.txt` (108/0, the committed 100755 file) | none: pre-freeze feasibility (Q70) ran the C2 counter only, not the regression conjuncts (`records/prefreeze-feasibility.txt` lists no selftest run) | QUALITY Q145 (replay the committed object, mode included; feasibility runs every conjunct before F). The diagnosis receipt is the failing case: the same command on the base copy fails, so the defect is the copy, and the rule fails whenever a mode-dropping copy is replayed |
| M2 | vacuous equivalence: domain trial v1 compared two empty outputs (both copies, outside the lane, looked for `<copy>/../tools/souji-verify.sh` and exited 1) and printed identical=yes; v2 ran the arms from different locations, and only the lane-located arm printed the live-fleet GUARD note (the tool derives roots from its own path) | `census/round-80/records/diagnosis/c2-domain-trial-v1-vacuous.txt`, `c2-domain-trial-v2-location.txt`; probes `census/round-80/probes/domain-trial-v1-vacuous.sh`, `-v2-location.sh` | none (the r79 domain trial checked check lines, not an expected verdict count) | v3 (`census/round-80/probes/domain-trial.sh`) installs both arms in the same layout, pins the engine and ledger, and requires one RESULT line per target in both arms; shown able to fail: two empty arms now print identical=no, EXIT=1 (`census/round-80/records/diagnosis/domain-trial-v3-refuses-empty.txt`); QUALITY Q145 |
| M3 | rule over-fit caught before freeze: the first NF10 draft ("the target keeps the token's whole path below round-<N>") refused the legitimate captures r78 L15 and r77 P31, which flatten the wave subdirectory | `census/round-80/records/prefreeze-feasibility.txt` | the regression conjunct (r78 22/22, r77 35/35) in pre-freeze feasibility — it worked | replaced by the capture-root rule before P; recorded so the closure can see the rule was shaped by the regression, not by the target rows |

## Gate

- **S327 admit (A, mined)** — git-ls-tree(1) as installed: `/usr/share/man/man1/git-ls-tree.1.gz` owned by git
  2.56.0-1 (`pacman -Qo`), sha256 `c0e10ef543481ac2569e665eca314067c394b10d4965f78e96e85ce79a1a7e86`, opened
  2026-11-07 by the L1 (capture `census/round-80/srcs/git-ls-tree.1.gz-2.56.0`). Decompressed line 252, FIELD NAMES
  objecttype: "The type of the object (commit, blob or tree)" (9 words); line 204, the default format
  "%(objectmode) %(objecttype) %(objectname)%x09%(path)". Grounds the sourced claim C1 (range members must be blobs of
  a regular-file mode).
- **S328 admit (A, mined)** — setsid(1) as installed: `/usr/share/man/man1/setsid.1.gz` owned by util-linux 2.42.4-1,
  sha256 `614ae07f37d95c2e250b32c812835dba09e91144f9cbf520efa586cac7385243`, opened 2026-11-07 by the L1 (capture
  `census/round-80/srcs/setsid.1.gz-util-linux-2.42.4`). Decompressed line 37: "setsid runs a program in a new session.
  The command calls fork(2) if already a process group leader." (18 words). Grounds C2's front/worker split (the
  worker is an asynchronous job, not a group leader, so setsid execs in place and `$!` is the session id). Cited by
  `corpus/knowledge/gate-signal-handling.md`.
- **Rejected (L1): draft S329, proc_pid_stat(5) as installed** (man-pages 6.19-1, sha256 `d2b5d09d…b002b51`, opened
  2026-11-07, lines 107-108 "(6) session %d / The session ID of the process.") — a within-scope duplicate of S068
  (the same page and field, web copy opened 2026-10-20, scope "field order and units of pgrp, session and
  starttime"); withdrawn before commit and S068 cited instead (CORPUS.md rule 2). Flip: none needed; S068 covers it.
- No other row's status, recheck or used-by cell changed. Within-scope duplicate check before append: S071
  (git-cat-file -e, existence of rev:path) and S078 (git-ls-tree -r/-z enumeration as the gate uses it) are other
  scopes of the same command family than S327 (object type and mode of an entry); `git show master:corpus/SOURCES.md
  | grep -F setsid` hits only S067/S074 prose, no setsid(1) row.
- Census: before `census/round-80/records/census-before.txt` (souji ok, EXIT=0, 87 W04 lines).
