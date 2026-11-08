S84ExecEvade — C2 evasion probes against the r84 freeze candidate

VERDICT: FAIL as delivered (sha256 a810acaf...) — the freeze it adds is dead code, so the frozen population scores
22 rows / 5 mismatches / 5 orphans, EXIT 1, and three of those five rows are a regression against the r83 control.
Root cause is one status guard on `read -d ''` (proven below). With that guard fixed and nothing else changed, the
same population scores 22/0/0/0 twice and all ten of my adversarial cells go clean; the one shape that still leaves
a process behind is a CLI that daemonizes and exits before any signal, which no population row covers.

## Bytes under test
- SEAT CANDIDATE (S84ExecC2/souji-vault-verify.sh) sha256 72a405f2c634712fb0211afb79f0462bf052b0b7c5fb8b663988017d2f1a8a18
  — byte-identical to tools/souji-vault-verify.sh (r83) and to census/round-84/controls/c2-K-a-r83-tool.sh.
  `diff` against the lane tool is EMPTY: the C2 seat's own directory carried the r83 bytes at probe time.
- ACTUAL FREEZE CANDIDATE (RefC2/souji-vault-verify.sh) sha256 a810acaf438cd6deee83a98f0db5b9697a5b5029f3126c207929c391f1130b25
  — the only bytes in the wave with the r84 repair (r83 cli_kill_tree replaced by a STOP-first two-pass walk + KILL
  sweep). All scores below are on THESE bytes, copied to my scratch as cand.sh.

## Frozen-population score (frozen command, unmodified counter)
python3 -B census/round-84/c2-late-fork-counter.py --tool <cand.sh> --work <empty dir outside /tmp>
  -> SUMMARY rows=22 mismatches=5 errors=0 orphans=5 ; exit 1
  RED rows: m1-monitor-term-fork (survivors=1), m2-monitor-hup-fork (survivors=1),
            d24-monitor-group (survivors=24), l1-late-setsid-pid (survivors=1), l2-late-setsid-group (survivors=1)
  GREEN: v1..v10, p1..p4, d12 x2, d24-term-pid.
Target is 22/0/0/0 EXIT 0 with l1/l2 survivors=0. Observed EXIT 1, and the two rows the round was built for still
show one survivor each. The claim as worded is false on these bytes.

## Mechanism (why the freeze does not bind) — PROVEN, not inferred
The r84 repair's freeze loop is DEAD CODE. Both signal loops in cli_kill_tree use

    { IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null || continue      (lines 271 and 288)

`read -d ''` reads to a NUL delimiter that /proc/<pid>/stat never contains, so it consumes the whole file and
returns **1 at EOF** while the variable is correctly filled. Measured on this host:

    $ bash -c '{ IFS= read -r -d "" v < /proc/self/stat; } 2>/dev/null; echo rc=$? len=${#v}'
    rc=1 len=326
    $ bash -c '{ read -r v < /proc/self/stat; } 2>/dev/null; echo rc=$? len=${#v}'
    rc=0 len=324

So `|| continue` fires for EVERY descendant, in both the STOP pass and the KILL sweep. Instrumented copy of the
candidate (scratch, dbg() appends to a log) on a 24-child monitor row:

    pass=1 root=2924946 mapn=5264 kids_root=[ 2924955]
    pass=2 root=2924946 mapn=5255 kids_root=[ 2924955]
    (zero STOP lines, zero KILL lines)

The map finds the tree (root -> timeout -> CLI) but nothing is ever stopped or killed; the rows that pass do so only
on the group TERM/KILL that follows. This is exactly why the monitor-launched children survive: under
`SHELLOPTS=monitor` each `sleep 600 &` is its own process group, so the group kill cannot reach it, and the tree
kill that was meant to reach it never ran. Three of the five red rows (m1, m2, d24-monitor-group) are a REGRESSION
against the r83 control, whose tree walk does execute: r83 uses `read -r now` (line read, rc 0 on success), so its
`|| continue` is correct. The repair changed the read to `-d ''` for the D5 newline-in-comm fix and kept the status
guard, which silently disabled the whole freeze.

Re-scored the r83 control myself for the comparison:
  census/round-84/controls/c2-K-a-r83-tool.sh (72a405f2...) -> SUMMARY rows=22 mismatches=2 errors=0 orphans=2,
  red only l1-late-setsid-pid and l2-late-setsid-group, d24-monitor-group survivors=0.
So a810acaf scores WORSE than the control it replaces (5 red vs 2 red).

### Repair (advisory) — measured
Two-site edit, nothing else: at lines 271 and 288 replace

    { IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null || continue
with
    { IFS= read -r -d '' now < "/proc/$k/stat"; } 2>/dev/null; [ -n "$now" ] || continue

Scored copy: cand_fix.sh (exact unified diff in this seat dir as fix.patch). Measured:
  frozen population run 1 -> SUMMARY rows=22 mismatches=0 errors=0 orphans=0
  frozen population run 2 -> SUMMARY rows=22 mismatches=0 errors=0 orphans=0 (independent empty --work dir)
  l1/l2 both `survivors=0 tmpleft=0 secs=0.4-0.7 match=yes`, d24-monitor-group survivors=0
  my adversarial cells on the repaired copy: latefork pid/group 0/0, monfork pid/group 0/0, deepmon 24-child
  pid/group 0/0, a2sig pid/group 0/0 — 10 of 10 cells clean, where the unfixed candidate left 1/1/1/1/24/24/2/2/0.
So the delivered candidate's only defect is that status guard; with it removed the sentence holds on the frozen
population and on every one of my shapes except (b) below.

Correction to my own record: an earlier intermediate run of mine reported 1-2 survivors for the "repaired" copy. That
was a driver defect — the driver copy used for those runs (`probe2.py`) hardcodes cand.sh and ignores PROBE_TOOL, so
it re-measured the UNFIXED candidate. The numbers above are from drivers that print the resolved tool path.

Residual, NOT fixed by the repair and NOT covered by any population row:
  shape (b) — a CLI that double-forks a daemon and exits during the walk — still leaves 1 nonce-carrying `sleep 600`
  (ppid reparented, state S), with the tool exiting rc=0 and NO `souji-vault-verify: SIGTERM` line on both
  deliveries, before and after the repair. Cause: the tool's `wait "$CLI_PID"` returns as soon as the CLI exits, so
  the signal path never runs at all; the daemon is already out of the tree. This is a claim-scope gap (no row has a
  CLI that exits early while a descendant lives), not something cli_kill_tree can fix once it is never called: a
  counter row would need to signal the tool before the CLI's exit, or the claim must exclude the shape.

## Shape matrix — DELIVERED bytes (cand.sh = a810acaf), own stubs, own nonce, own fixtures, 5 s settle
(the post-repair cells for the same shapes are in the table at the end of this section)
Each cell: exit within settle? rc? SIG line? survivors (nonce-carrying pids)? private TMPDIR empty?
| shape | delivery/launch | exited | rc | SIG line | survivors | tmpleft |
|---|---|---|---|---|---|---|
| (a1) latefork: setsid child on FIRST signal | pid/default | y 2.75s | 143 | y | 1 | 0 |
| (a1) latefork | group/monitor | y 2.69s | 143 | y | 1 | 0 |
| (a2) new shape: setsid child on first AND second signal | pid/default | y 2.68s | 143 | y | 2 | 0 |
| (a2) same, group | group/monitor | y 2.68s | 143 | y | 2 | 0 |
| (b) double-fork daemon (setsid & exit) during the walk | pid/default | y 0.05s | 0 | n | 1 | 0 |
| (b) same | group/monitor | y 0.10s | 0 | n | 1 | 0 |
| (c) 24-child fan-out plus late setsid child | pid/default | y 2.68s | 143 | y | 2 | 0 |
| (c) same | group/monitor | y 2.69s | 143 | y | 26 | 0 |
| (d) comm with `)` and a newline (exec -a) | pid/default | y 0.77s | 143 | y | 0 | 0 |
| (d) comm with `)` and a space | group/monitor | y 0.77s | 143 | y | 0 | 0 |
| (e) child exits early (pid could be reused) | pid/default | y 0.77s | 143 | y | 0 | 0 |
| (f) CLI ignores TERM | pid/default | y 2.69s | 143 | y | 0 | 0 |
| (f) same | group/monitor | y 2.69s | 143 | y | 0 | 0 |
| (g) fast exit (no hang point) | pid/default | y 0.11s | 0 | n | 0 | 0 |

Two independent full runs of the matrix agree cell for cell; the run above is the second (matrix.txt, sha256
1d69d0fd0a392ec94339ab3859d310d4c507887556c655e5b840a4ad8a47244f). Shape (e) reuse detection: the early child exits
within 0.2 s of the fan-out; I did not race the host for pid reuse (pid_max 4194304 makes a same-pid reuse in a 3 s
window unobservable here), so (e) is reported as "no survivor, no false signal", not as a proof the starttime
re-check binds.

### Post-repair cells (cand_fix.sh = two-site read-status edit; drivers print the resolved path)
| shape | delivery/launch | exited | rc | SIG line | survivors | tmpleft |
|---|---|---|---|---|---|---|
| (a1) latefork | pid/default | y 0.62s | 143 | y | 0 | 0 |
| (a1) latefork | group/monitor | y 0.57s | 143 | y | 0 | 0 |
| (a2) fork on first and second signal | pid/default | y 0.77s | 143 | y | 0 | 0 |
| (a2) same | group/monitor | y 0.77s | 143 | y | 0 | 0 |
| (b) double-fork daemon + exit | pid/default | y 0.11s | 0 | n | 1 | 0 |
| (b) same | group/monitor | y 0.10s | 0 | n | 1 | 0 |
| (c) 24-child fan-out + late setsid | pid/default | y 0.72s | 143 | y | 0 | 0 |
| (c) same | group/monitor | y 0.72s | 143 | y | 0 | 0 |
| monfork (counter's `fork` stub shape) | pid/monitor | y 0.62s | 143 | y | 0 | 0 |
| monfork | group/monitor | y 0.62s | 143 | y | 0 | 0 |

## Findings (all "as delivered" = sha256 a810acaf unless marked)
F1 (HIGH, survivor; the claim's own rows): l1/l2 each leave one nonce-carrying `sleep 600` on the delivered bytes —
  the frozen population scores orphans=5 EXIT 1. Repaired copy: 0 survivors, twice.
F2 (HIGH, wrong verdict, SURVIVES THE REPAIR): shape (b) — a CLI that double-forks a daemon and exits during the walk
  — makes the tool exit rc=0 with NO `souji-vault-verify: SIGTERM` stderr line while one nonce-carrying daemon child
  survives (ppid reparented, state S), on both deliveries, before and after the read-status repair. The tool's `wait`
  returns on the CLI's exit, so no signal path runs. No population row has this shape.
F3 (MEDIUM, second-signal fork): shape (a2, setsid child on every signal) leaves 2/2 survivors on the delivered
  bytes; 0/0 on the repaired copy.
F4 (MEDIUM, fan-out plus late fork under monitor): shape (c) leaves 2 (default) / 26 (monitor) on the delivered
  bytes; deepmon 24-child monitor is 0/0 on the repaired copy. The 24 children alone are handled either way
  (d24-term-pid and d24-monitor-group are green on the r83 control).
F5 (clean, no change, either copy): comm containing `)` plus a newline or a space is handled (whole-stat read with the
  last-`)` strip holds); a TERM-ignoring CLI is handled; an early-exiting child is handled with no false signal; no
  signal reached any pid outside the CLI descendant set — an external canary `sleep 600` in its own session, started
  by my harness, was alive before and after a full latefork run and died only from my own SIGKILL; no private TMPDIR
  file was left behind on any well-formed row (tmpleft=0 everywhere).
F6 (note for the L1, not a tool defect): at probe time `.ufo/waves/round-84/w1/S84ExecC2/souji-vault-verify.sh` was
  sha256 72a405f2... — the r83 bytes, empty diff against the lane tool. The repaired bytes exist only in
  `RefC2/souji-vault-verify.sh` (a810acaf..., itself broken as shown). The L1 must not certify the seat's 72a405f2
  file; and must not certify a810acaf without the read-status fix.
F7 (retracted, recorded for honesty): a `sleep 600` with cwd my scratch and NO SOUJI_* env was alive at 03:27
  (pid 1444838) and I killed it. It is my own canary start, not a C2 stub leak: every stub the counter and my driver
  run inherits SOUJI_R81_NONCE, and the nonce reap killed every such survivor it reported. No C2 fixture process was
  left running at the end of my probe (scan of `sleep` cwds under my seat path: empty). The four `sleep 600` pids the
  matrix reports as survivors were all reaped by the driver's nonce sweep; survivors in the table are the count the
  tool left, not processes still running afterwards.

## What the L1 should do (as a finding, not an edit — lane is read-only to me)
1. Do not score `S84ExecC2/souji-vault-verify.sh` (72a405f2..., the r83 bytes) as the C2 candidate: it cannot pass.
2. Do not score `RefC2/souji-vault-verify.sh` (a810acaf...) either: 22 rows, 5 mismatches, 5 orphans, EXIT 1.
3. The two-site status fix in `fix.patch` takes the same bytes to 22/0/0/0 twice and cleans all ten of my cells.
   Apply it (or an equivalent that tests the variable instead of the read status) before re-scoring.
4. Shape (b) is still open and is a scope question for the claim wording, not a cli_kill_tree repair: a CLI that
   daemonizes and exits while its child lives leaves that child behind with rc=0 and no SIG line, because `wait`
   returns and the abort path never runs. Either add a row/counter rule that rejects a zero-exit-with-no-SIG row, or
   narrow the sentence to the shapes it covers.

## Reproduction (files in this seat dir)
- matrix.txt — the 14-cell deliverable-bytes matrix (sha256 1d69d0fd0a392ec94339ab3859d310d4c507887556c655e5b840a4ad8a47244f)
- probe.py — the driver that produced it (it resolves the tool to `<scratch>/cand.sh`; place the candidate there)
- probe_post.py — the post-repair driver (resolves to `<scratch>/cand_fix.sh`)
- fix.patch — the exact two-site edit (aa1181b22d7fc5bc62c12f68df46489233003f5f7d76c714221811f5de353d21)
Scratch `/fast/scratch/hyaku/souji-r84/S84ExecEvade/` removed after copying; no lane tracked file was written.
Commands:
  python3 -B census/round-84/c2-late-fork-counter.py --tool <cand.sh|cand_fix.sh> --work <empty dir outside /tmp>
  python3 -B <seat>/probe.py   |   python3 -B <seat>/probe_post.py
Stub bodies (verbatim, `#!/bin/bash` + the counter's r81_mark + body):
  latefork : flag=0; trap 'if [ "$flag" = 0 ]; then flag=1; setsid sleep 600 & fi' TERM INT HUP; r81_mark "$@"; while :; do :; done
  a2sig    : flag=0; trap on both branches forks `setsid sleep 600 &`; r81_mark "$@"; while :; do :; done
  bdaemon  : setsid sleep 600 &; exit 0            (mark written before)
  cfanout  : 24x `sleep 600 &`; trap 'setsid sleep 600 &' TERM INT HUP; mark after the fan-out; busy loop
  dparen   : r81_mark "$@"; exec -a "we)rd\nname" sleep 600
  ereuse   : sleep 0.2 &; r81_mark "$@"; exec sleep 600
  ftermign : trap "" TERM; r81_mark "$@"; exec sleep 600
  gfast    : r81_mark "$@"; exit 0

## Tooling
No installs, no upgrades, no pacman. Used system bash, python3, strace/setsid/timeout already present.
