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
