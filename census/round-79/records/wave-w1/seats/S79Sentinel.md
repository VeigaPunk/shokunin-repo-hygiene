# S79Sentinel — W1 gate safety review (r79). Verdict: the signal rule reproduces; 2 new MEDIUM defects in the
# new scratch-dir path, 3 LOW limits; the s3/s4 and launch-mode instrument defects are confirmed.

MEASURED (S=/fast/scratch/hyaku/souji-r79/S79Sentinel; gate blob ae5022c5… = W1 = R2, writer 70bbf1c2…; `git diff c8c3fbc feebf2b -- tools/` empty, both 984f9e71…)
- `python3 -B census/round-79/c1-signal-counter.py --gate-dir $S/gw1 --work $S/c1-w1-fg` -> `SUMMARY rows=11 mismatches=0 errors=0 orphans=0`, EXIT=0 (s4 rc=130).
- same at base 5f5cb865… -> `SUMMARY rows=11 mismatches=10 errors=0 orphans=10`, EXIT=1.
- same at W1 launched with `&` from a non-interactive shell -> `SUMMARY rows=11 mismatches=1 errors=0 orphans=1`, `s4 … exited=n survivors=3 tmpleft=2`: the A receipt's 10->1 is the counter's own launch mode, not the gate.

1. Private dir (W1:61, cleanup 45/60, file reuse 66-67/79)
- Removed on normal, signal and usage exits: `receipt-tmpdir.txt` in-lane tmpleft=0, usage tmpleft=[], signal arms tmpleft=0. `set -u` abort runs the EXIT trap (`bash -c 'set -u; trap "echo CLEANUP-RAN" EXIT; echo $nope'` -> CLEANUP-RAN, rc=127); no reachable unbound-var abort in the gate. SIGKILL leaves the 0700 dir with `o` and a live child group (tmpleft=1) — untrappable; the counter reaps it.
- MEDIUM M1 symlink race: `o` is re-opened by path per call (66-67, 79). With TMPDIR a 0777 non-sticky dir, a writer on the parent renames the 0700 dir and plants `<name>/o -> victim`; the next write truncates the victim and the gate exits 0 (`ARM race … victim_changed=True`, victim_now=[]). Reads are redirectable too (forged `local_tip`). Default /tmp (sticky) not exploitable. Fix: open `o` once with O_NOFOLLOW|O_CREAT|O_EXCL and reuse the fd.
- MEDIUM M2 TMPDIR inside the judged tree: the gate's own dir is untracked -> `check-clean=FAIL`, `detail-clean: ?? tmp/souji-gate.mFqgACRi/o` (fails closed, but the verdict depends on caller env; also echoes its own scratch path). Relative TMPDIR -> `gate: mktemp failed` exit 2 (LOW); empty TMPDIR -> /tmp, fine.

2. Group kill (W1:49-50)
- Real `timeout` setpgid holds (shim log `pgid=<timeout pid> != pid`); term/int/hup -> rc=143/130/129, `check-signal=FAIL`, class, survivors=0, tmpleft=0.
- LOW L1: before setpgid the group kill is ESRCH and the pid fallback kills only the direct child. With a `timeout` wrapper on PATH the wrapper's child survives: `ARM early … survivors=1 … cmd='sleep 30' pgrp=<gate's group>` (receipt-signal.txt). Real coreutils closes the window before any grandchild exists.
- LOW L2: stale `gate_child` between `wait` (70) and `gate_child=` (71) — a signal there kills a reaped pid; a pid reused as a group leader would die. Two-instruction window, not deterministically reproducible.
- `kill $gate_tick`: no ticker in W1 (`grep -c gate_tick` = 0). R1 4a9bbb30 did `kill -KILL "$gate_tick"` after `wait -n` could reap it (R1:86) — reverted, not a W1 defect.

3. Async inheritance (W1:66-67)
- Children inherit SIGINT/SIGQUIT ignored (`int=trap -- '' SIGINT quit=trap -- '' SIGQUIT term=`); TERM default, so `timeout -k 5` and the gate's KILL still work; stdin restored `<&0`. No check result changes; the gate's own INT trap depends on the gate not starting with INT ignored (I2).
- LOW L3: a child that escapes the group (`setsid`) survives the signal path (`ARM escape survivors=1`), and on a no-signal timeout expiry coreutils kills only the direct child (`timeout -k 5 1 bash -c 'sleep 600 & wait'` -> rc=124, `sleep 600` alive). Group-scoped guarantee, stated-limit class.

4. D30: only new lines are `check-signal=FAIL` (stdout) and `detail-signal: RECEIPT-GATE-SIGNALED: SIG%s received; the running child group was killed` (stderr) — no path, no child output. PASS (M2's echo is the pre-existing detail-clean line).

5. r78 FIFO routes at W1: 3/3 refused, no block — `ROUTE fifo-git-config rc=1 ms=7`, `fifo-git-head rc=1 ms=8`, `fifo-include-path rc=1 ms=9`, each `check-gitsource=FAIL`, leftover=0.

INSTRUMENT (confirmed)
- MEDIUM I1: s3/s4 never reach ls-remote — their `gate.out` has no `check-gitsource=PASS`; the shim matches the row dir name in `--file <rowdir>/clone/.git/config`, so they hang at s1's check-0 config-read point (7 distinct hang points over 10 signal rows); the ls-remote/upload-pack path is untested.
- MEDIUM I2: the counter's verdict depends on its own launch mode (foreground 11/11 vs `&` 10->1 above); the frozen invocation does not say foreground, so the A receipt's s4 failure is this artefact.

Files written: /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-79/w1/S79Sentinel/{setup.sh, fifo-routes.sh, signal-probe.py, tmpdir-probe.py, receipt-fifo.txt, receipt-signal.txt, receipt-tmpdir.txt, receipt-c1-w1-fg.txt, receipt-c1-base-fg.txt, receipt-c1-w1-bg.txt}. No host changes, no sudo, no installs. Scratch removed; no leftover process.
