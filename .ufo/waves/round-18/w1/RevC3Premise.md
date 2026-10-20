STATUS: DONE — C3 premise HOLDS: all 58 blocked processes are orphaned r15/r16/r17 fixture residue, not live work; two evidence-quality findings for L1 (artifact col4 mislabel; live reap-seat overlap).

Seat: SoujiR18.RevC3Premise-5 · 2026-10-20 · lane base b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 (b576341)
Axes (godspeed): coverage (judged — every family × every premise element checked), calibration/evidence-precision (col4 defect found), speed (4–3–3 parallel batches, no serialization).
Tooling directive: no tools installed or upgraded; read-only ps//proc, stat, git log only. No processes signalled; no census script executed; no pacman.

# Method

All checks read-only. Artifact: census/round-18/leaked-procs-before-1631.txt = 58 data rows, NO header (first row is pid 185592). Columns: pid, ppid, pgid, col4(see F1), lstart(5 fields), command.

Commands run (abbreviated outputs; full outputs in transcript):
1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --format='%h %ci %s' -n 40` — r15 land b410186 06:28; r16 wave cbf688a 11:13, 0a70bef 11:40, land 163158a 12:03; r16-repin/preservation window 13:41–15:57 (d7e648d 14:24, 4f48343 15:57); r17 land 2cfc6c0 16:12; r18 base b576341 16:24:03.
2. `ps -eo pid,ppid,pgid,sid,lstart,stat,wchan:32,args` (3 scans: ~16:53, ~16:58, ~17:01) — all 58 listed pids present in every scan; identical wchan/args across scans (no progress).
3. Per-pid `readlink /proc/<pid>/cwd`, `cat /proc/<pid>/wchan`, field 3 of `/proc/<pid>/stat`, fields 5/6 (pgrp/sess) of `/proc/<pid>/stat` — all 58: state S; cwd `… (deleted)`; wchan per role (below).
4. `for d in <24 scratch roots + 44 harness dirs>; do [ -e $d ] && echo EXISTS || echo GONE; done` — 24/24 scratch roots GONE; 42/44 harness dirs GONE.
5. `awk … /proc/1497/{stat,cmdline}` — comm=(systemd), cmdline=`/usr/lib/systemd/systemd --user`, ppid=1.
6. Session-leader liveness, both column systems: file col4 values (7631, 7265, 4991, 10140, 10139, 10080, 10078, 10055, 1648, 9793, 9630, 19517, 19106, 18930, 17659, 17517, 17494, 20144, 17317, 17212, 16771, 16613, 16430, 8165, 15972) all dead; kernel sess values (184726, 288604, 362699, 558610, 558608, 598023, 638541, 811234, 917803, 1024798, 1240270, 1537128, 2473532, 2568042, 2626165, 2638126, 2763057, 2794427, 2983111, 3049307, 3137586, 3250850, 3845852, 4034097) all 24 dead.
7. Fresh-run scan `ps -eo pid,lstart,args | awk '/souji-census|souji-r1[0-9]|r15-census-config|r17-census-hygiene|r-inc-fifo|d2-fifo/'` — beyond the blocked 58: a 16:56:34–16:58:01 batch (python3/strace/bash/git, short-lived, gone by next scan) and at 17:00:50 `python3 /var/tmp/souji-r18-FixtureReapR14/lane/tests/fixtures/r14-census-boundary.py` + `strace -f … -- bash /var/tmp/souji-r18-FixtureReapR14/census-r14-harm.sh --root /var/tmp/r14-census-boundary.khlcz99i/commondir-alias --include-root` — r18 reap seats on FRESH mktemp roots.
8. `stat` the two surviving harness dirs' scripts — regular files (`/var/tmp/souji-r16/preharm.sh`, `/var/tmp/souji-r16-PreservationRepin/preharm/tools/souji-census.sh`).
9. col4 probe: `ps -o lstart` + `/proc/1910/stat` field 22 — pid 1910 = `/opt/1Password/1password --type=zygote`, started 09:57:13 (1685 ticks after btime 1792501016), i.e. hours BEFORE the 15:57:36 fixture whose col4 is 1910 → col4 is not a recycled spawner pid either.

# Family verdicts (58/58 = ORPHANED FIXTURE RESIDUE, not live work)

Family A — `souji-census.sh --root /var/tmp/r15-census-config.<rand>/unsafe-repos/r-inc-fifo` (44 procs: 22 bash + 22 `git rev-parse --is-inside-work-tree`), 22 runs:
- A1 r16-matrix.{p74cclr3,jku4qe9z,sc9ho6nz,hy6ocfc4,9az4qh_i,9zgl_8hd,6m58cnsu,v6lm0rcz} — 8 runs, 16 procs, starts 11:04:09–12:03:14. VERDICT: orphaned residue.
- A2 r16-repin.{z0t4kl7c,v12xk2yg,t4vqobh_,sf2f30d9,qucgbnxl,scjidogf,_i36vtux} — 7 runs, 14 procs, starts 13:41:51–14:22:15 and 15:57:36. VERDICT: orphaned residue.
- A3 r16-PreservationRepin (1 dir, 2 runs: 2572254, 2800031) — 4 procs, 11:37:29 / 11:42:34. VERDICT: orphaned residue.
- A4 souji-r16/preharm.sh (1 run: 2650283) — 2 procs, 10:53:42. VERDICT: orphaned residue.
- A5 r17-matrix.{qmxy_npd,pmzb8vuw,8cxpl2lv,ccednztz} — 4 runs, 8 procs, starts 14:13:21–16:01:58. VERDICT: orphaned residue.

Family B — r17 hygiene fixtures on `r17-census-hygiene.<rand>/{d2-fifo,d2-symlink-fifo}/b` (`git status --porcelain`), 14 procs, 4 runs:
- B1 souji-r17-FixtureR17Census/a31642d.sh × e80b0xqe (d2-fifo 562276-79; d2-symlink-fifo 596478-80) — 6 procs, 13:40:26 / 13:41:26. VERDICT: orphaned residue.
- B2 souji-r17-FixtureR17Census/cc21683.sh × lwka_g_w (d2-fifo 574643-574989; d2-symlink-fifo 597162-597359) — 8 procs, 13:40:27 / 13:41:27. VERDICT: orphaned residue.

Premise elements, per family:
- Scratch dir gone: YES, 24/24 roots GONE (`r15-census-config.*` ×22, `r17-census-hygiene.*` ×2); every one of the 58 processes reports cwd `… (deleted)` via readlink — including the 4 procs whose harness dirs happen to survive (their cwds are the deleted data roots). A deleted cwd cannot be re-crossed; the run cannot complete. NOT live work.
- Parent: census bash ppid=1497 = `systemd --user` (orphan reaper) for all 22+4 top bashes; git children parented by their own census bash (alive but itself orphaned, wchan do_wait). Kernel session leader dead for all 24 distinct sessions. NOT collected by any live fixture parent.
- Start time vs lane fixture runs: all 58 starts 10:53:42–16:01:58, inside r15→r17 activity windows (A1/A3/A4 bracket the r16 wave-1 commits cbf688a 11:13 / 0a70bef 11:40 / land 163158a 12:03; B1/B2 and A2 bracket r17 wave work d7e648d 14:22 / 4f48343 15:57; A5 brackets r17 wave-2). Zero starts after the r17 landing (16:12:16) or the r18 base (16:24:03). Youngest was ≥55 min blocked at first scan (16:53), oldest ~6 h. The census contract at b576341 bounds each repo at seconds (`timeout 15` outer per C1) — nothing legitimately lives this long. NOT live work.
- wchan: every git = `wait_for_partner` (blocked in fifo open(2), fs/fifo.c waiting for the opposite end — the FIFO-swapped `.git/info/attributes` red arm); every census bash = `do_wait`; wrapper bashes (562276, 574643, 596478, 597162, 574984, 597357) = `anon_pipe_read`. Command lines match exactly the two known recipes (A: `r-inc-fifo` + `rev-parse`; B: `d2-fifo`/`d2-symlink-fifo` + `status --porcelain`). Consistent with pipe/fifo-open hang. [INFERENCE on the exact open(2) target: wchan + cmdline consistent; `/proc/<pid>/fd` and `syscall` not read per probe rule.]
- No live run uses those prefixes now: no process exists under the blocked mktemp suffixes (suffixes unique per run; blocked roots deleted). Live r18 reap seats DO re-run the same RECIPES right now on fresh roots (`/var/tmp/r14-census-boundary.khlcz99i`, 16:56–17:00 batches) — different scratch, short-lived, strace-wrapped; none is a continuation of the 58. Premise holds with the F2 nuance below.

Falsification attempts that failed: (1) live-work hypothesis — rejected on age (55 min–6 h vs second-scale bounds), deleted cwd, dead session leaders; (2) non-fifo hang — rejected on `wait_for_partner` wchan matching the fifo red-arm recipes exactly; (3) hidden live collector — rejected: ppid is systemd --user, all session leaders dead; (4) pending fifo writer — none exists: the fifo's directory is deleted and no live run reuses those suffixes; the git processes have not advanced one step across 3 scans 8 min apart.

# Findings

- F1 (calibration, medium) — census/round-18/leaked-procs-before-1631.txt column 4 is NOT the kernel session id, though position (pid,ppid,pgid,?) invites reading it as `sid`. Kernel `/proc/<pid>/stat` fields 5/6 disagree for every family (e.g. 185605: file col4 7631 vs kernel pgrp 184733 / sess 184726; 562276: 10140 vs 558610/558610; 4037294: 1910 vs 4034162/4034097). The pid-reuse explanation also fails: col4=1910 rows started 15:57:36, but pid 1910 has been 1Password's zygote since 09:57:13. col4 is per-run/per-job consistent but unidentifiable. Additionally the file has no header, and treating its first data row as a header silently drops pid 185592 (my first reconciliation loop did exactly that: 57/58). Smallest fix: regenerate via `ps -eo pid,ppid,pgid,sid,lstart,args` cross-checked against `/proc/<pid>/stat` fields 5–6 for 2–3 sampled pids, and write a header row. C2's LG-DANGLING-PTR discipline should extend to generated evidence: a leak census whose columns don't match the kernel is exactly the "evidence that does not exist" class round 18 is gating on.
- F2 (coverage, low, affects C3 counting) — the fixture recipe families are LIVE again at 16:56–17:01 via r18 reap seats (FixtureReapR14-5 confirmed at 17:00:50; two sibling strace batches 16:56–16:58) on fresh mktemp roots. C3's "orphans detected by the census vs an independent counter" must match on exact scratch root (mktemp suffix) or pid, and use point-in-time snapshots, never family prefixes like `r15-census-config.*` or `souji-r1*` — otherwise live red-arms count as residue and inflate/deflate the delta.
- F3 (housekeeping, low) — two orphan-owning harness dirs still exist: /var/tmp/souji-r16 and /var/tmp/souji-r16-PreservationRepin (42 sibling dirs were cleaned). Not required for the verdict; normal residue-cleanup surface for C3's first real run.

# Residual risk / verification gaps

- Exact open(2) target (`.git/info/attributes` vs another attributes path) not proven — /proc fd/syscall reads are outside the probe rule; wchan+cmdline make it near-certain but it stays [INFERENCE].
- col4's generator semantics remain unexplained after three hypotheses (sid, recycled spawner pid, per-job bookkeeping) — flagged, not root-caused; fix is regeneration, not forensic closure.
- The 58 are still blocked as of 17:01; I did not and may not signal them. Whoever integrates C1's process-group watchdog gets the cleanup for free on the next red-arm reap.

Verdict: premise holds, 58/58, both families. No finding invalidates C3's "process residue becomes a governed surface" framing; F1/F2 are precision fixes to its evidence and counting.
