STATUS: DONE — all six assigned bash-5.3 semantics questions answered with exact outputs; the watchdog design is sound, and five non-obvious constraints were falsified/confirmed that the C1 patch must respect.

# ScoutSetM — bash 5.3 semantics for the C1 emit_census watchdog

Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin` at `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`.
Interpreter: `GNU bash, version 5.3.20(1)-release (x86_64-pc-linux-gnu)`.
Scope: the six ALLOWED-EXEC questions only. No lane file edited, no jj, no git write anywhere.
All work under `/var/tmp/souji-r18-ScoutSetM/`, every process started was reaped; the directory was
removed after this report was written (no probe artifacts remain).

Axes I optimised (godspeed): **operability** (does the documented design produce a bounded, residue-free
census), **falsification** (does the obvious-but-wrong variant fail visibly), **cost** (one extra probe per
suspicion, no scaffolding).

---

## P1 — `set -m; f & pid=$!; set +m`: is the job its own process group, and is it noisy?

```bash
# p1_pgid.sh   (run: bash p1_pgid.sh </dev/null)
sleep 5 & pid=$!                      # no set -m
ps -o pgid= -p $pid
set -m; sleep 5 & pid=$!; set +m      # set -m around the fork
ps -o pgid= -p $pid
```

Exact output:

```
== parent pgid: 399621 pid=399621
-- without set -m
child pid=399661 pgid=399621          <-- SAME group as the parent
-- with set -m (stderr captured separately)
child pid=399685 pgid=399685          <-- own group, pgid == pid
-- set -m emitted no warning above (stderr shows only if any)
-- nested: set -m inside function
in-fn pid=399707 pgid=399707          <-- works inside a function
-- set -m with job already running (bash warns about new process group pgid)
monitor mode on: on
monitor mode off: off
```

**Verdict: holds.** `set -m` / fork / `set +m` is the correct primitive: it gives the census child
`pgid == pid`, so `kill -TERM -- -$cpid` reaches exactly that repo's tree. Without it the child shares the
caller's group — the census's own group, which in a verifier run is the harness's group — so any group
signal would take out the caller. This is also visible in the host leak inventory: the leaked census bash
(`leaked-procs-before-1631.txt:1`, pid 185592, pgid 184733) and its blocked git (pid 185605) are both in a
*different, ancestor* pgid, proving the census was running with no job control of its own.

Three side-effects worth knowing, all measured:

* **No stderr noise.** No `cannot set terminal process group` / `no job control` line; `set -m` in a
  non-interactive, tty-less, pipe-stdout script is silent.
* **No job-completion noise on stdout.** `out=$( set -m; true & p=$!; set +m; wait $p; echo ROW-A )` →
  `captured=[ROW-A]` (no `[1]+ Done`).
* **The child's stdin becomes `/dev/null`.** `set -m; head -1 & …; wait` → `head rc=0` (read returned EOF).
  Harmless here — `census_one` reads no stdin — but it is a behaviour change from today's inherited stdin,
  and it is what prevents a background-group child from taking `SIGTTIN` on a terminal.

---

## P2 — does `kill -TERM -- -$pid` free a git blocked in `open(2)` on a FIFO?

Setup per case: `git init`, one commit, then `.git/info/attributes` replaced by a FIFO
(`os.mkfifo`). The census child is forked under `set -m`.

```bash
# the child, forked by the parent:
set -m; git -C "$d" status --porcelain & cpid=$!; set +m
# state of the blocked git:
#   /proc/<pid>/stat -> ('S', ppid, pgid)   /proc/<pid>/wchan -> wait_for_partner
kill -TERM -- -"$cpid"; rc=0; wait "$cpid" || rc=$?
```

Exact output (T9b / p2b, one run):

```
T9b: guard-visible type: regular file
T9b stdout:
CPGID=556974                    <-- git's own group == its pid
RC=143 SENT=yes
FIFO-STILL-THERE=yes
T9b elapsed=2.00s
T9b: procs referencing this base still alive: []
```

and the direct measurement of the child state (`p2_killpg_fifo.py`, `t2b_killpg_child.py`):

```
A: child 399833 state/ppid/pgrp=('S', '399827', '399833') wchan='wait_for_partner'
A: child after kill: 399833 ('S', '1497', '399833')      <-- when only the PARENT group was signalled
2b-3: git after TERM: ('DEAD', '-', '-')  wchan ?
2b-4: parent stdout: 'CPID=469386 CPGID=469386\nWAITRC=143\n' stderr: ''
2b-5: SIGKILL path stdout: 'KILL-WAITRC=137\n' parent rc: 0
2b-5 stderr: 'bash: line 6: 470469 Killed   git -C … status --porcelain > /dev/null 2>&1'
```

**Verdict: holds, and the failure mode is now proven at the exact frame that leaked.** Three distinct facts:

1. `SIGTERM` to the child's group kills a process blocked in `open(2)` on a FIFO (`wchan=wait_for_partner`)
   immediately, and the parent's `wait` returns **143**.
2. `SIGKILL` to the group returns **137** — and bash also prints a `… Killed <cmdline>` job notice on
   **stderr** when it reaps that job asynchronously. That notice is real output that will land in the
   census's stderr unless the reaping path is arranged so it does not (it did *not* appear in the
   end-to-end run below, where the parent `wait`s the killed child inside the same iteration).
3. **Killing the bash parent alone does not free the git child.** `os.kill(bash_pid, SIGTERM)` → bash dies
   (`rc=-15`), and the git child **survives, reparented to pid 1497, still `S` in `wait_for_partner`**
   (`B: git child 408052 after parent-only TERM: ('S', '1497', '408052')`). This is precisely the
   58-process residue class in `leaked-procs-before-1631.txt`. A pid-only fallback is not a fix.

**The group outlives its shell, which is what makes the fix work even in the worst ordering.** T7b — kill
*only* the subshell, with a real child (not the `( sleep N )` exec-optimised form):

```
T7b: shell 535827 ('S', '535826', '535827') | sleep child 535828 ('S', '535827', '535827')
bash: line 1: 535827 Killed   { sleep 300; :; }
T7b: after killing ONLY the shell -> sleep child: ('S', '1497', '535827')   <-- reparented, SAME pgid
T7b: after killpg( 535827 SIGTERM) -> child: ('DEAD', '-', '-')
```

So even if `census_one`'s subshell has already exited and only a blocked git survives, the pgid is
unchanged and `kill -- -$pgid` still reaches it. No `/proc` walk, no pid bookkeeping.

Beware this trap when reproducing: `( cmd )` where the subshell body is a **single** command is
exec-optimised by bash into the command itself (my first T7 attempt killed nothing because the "subshell"
*was* the `sleep`). Use `{ cmd; :; }` or two commands when you need a genuine fork.

---

## P3 — does a parent `EXIT` trap run in the background subshell?

```bash
trap 'echo PARENT-EXIT-TRAP >> $T/trace' EXIT
( echo sub A ) &            # inherits the definition
( trap 'echo SUB-B >> $T/trace' EXIT; … ) &   # own trap
( trap '…' EXIT; sleep 30 ) & kill -TERM $!   # own trap + signal
```

Exact output:

```
sub traps visible in subshell: trap -- 'echo "PARENT-EXIT-TRAP ran ($$)" >> … ' EXIT;trap -- '' SIGXFSZ;
wait rc after TERM: 143
-- trace file so far:
SUB-B-EXIT-TRAP ran
SUB-D-TRAP term
```

**Verdict: holds, in the safe direction.** The subshell *sees* the parent's trap definition (`trap -p`
prints it) but does **not execute** it on subshell exit; only a trap the subshell sets itself fires — on
normal exit (B) and on `SIGTERM` to the subshell (D). A parent `EXIT` trap does fire on normal exit, on
`exit 2` mid-loop, and on an external `SIGTERM` (`parent-script rc after TERM=143 ; trap log:
PARENT-TRAP-ON-EXIT`).

Confirmed against the exact shape the fix will use (T11 — parent owns `mktemp -d`, child is forked under
`set -m` three times, then `exit 2`):

```
T11: WORK=/var/tmp/souji-r18-ScoutSetM/t11-DMmV4x created
T11: i=1 rc=0 row=row-1 work_exists=yes entries=row seen
T11: i=2 rc=0 row=row-2 work_exists=yes entries=row seen
T11: i=3 rc=0 row=row-3 work_exists=yes entries=row seen
T11: now exit 2 mid-run; parent trap must remove WORK
PARENT-CLEANUP rm -rf /var/tmp/souji-r18-ScoutSetM/t11-DMmV4x
SCRIPT-EXIT=2
```

So **one shared `mktemp -d` per run plus a single `trap 'rm -rf -- "$W"' EXIT` is safe**: the forked
census child can never delete the parent's work dir, and the trap still cleans up on the `exit 2`
protected-refusal path.

---

## P4 — does `$( … )` finish while a watchdog is sleeping, and is the watchdog's `sleep` orphaned?

```bash
out=$( ( sleep 30; echo LATE ) >/dev/null 2>&1 & wpid=$!; echo "innerwpid=$wpid" )
kill $wpid
```

Exact output:

```
== 4a: $( … ) capture returns while a watchdog sleep is still alive
capture rc=0 out=[innerwpid=399673] elapsed_ms=1
watchdog pid=399673 alive=yes
its children:  399675 399673 399647 S sleep 30
-- kill $wpid only (not the group)
sleep child after kill wpid:  399675 1497 399647 S sleep 30     <-- ORPHANED, ppid 1497
== 4b: same but the watchdog is a subshell whose stdout is NOT redirected
capture-without-redirect rc=0 elapsed_ms=30005 out2=[innerwpid=401573
LATE]
== 4d: watchdog writes to the caller stdout => corrupts captured rows?
out3=[ROW1
WATCHDOG-NOISE]
```

**Verdict: holds only with `>/dev/null 2>&1`, and the failure without it is severe.**

* With the redirect: the capture returns in **1 ms**; the watchdog and its `sleep` child are still alive
  afterwards (which is the point — you then release them).
* **Without** the redirect the capture blocks for the watchdog's whole life — **30005 ms** — because the
  watchdog holds the inherited stdout pipe write end. At the exact fix shape (T8, `{ sleep 3; echo LATE; }
  &` inside the substitution): `elapsed_ms=3010 out=[ROW\nLATE]`. A single forgotten redirect converts the
  whole census into a 600 s-per-repo hang *and* injects `LATE` into a TSV row.
* `$( )` alone is **not** enough to protect the capture; the watchdog must not hold either caller stream.
  T10 confirms the good shape, with *both* streams captured (`2>&1`) and a 30 s watchdog live:
  `T10: both-stream capture elapsed_ms=1 out=[ROW-a …]`, `stray sleeps from this test: 0`.

Two further requirements fall out:

* **The watchdog needs its own process group too.** Without it, `kill $wpid` orphans its `sleep`
  (`4f: wpid=GONE sleep=469523 state=S ppid=1497`), and `kill -- -$wpid` would signal the census's own
  group. With `set -m` around the watchdog fork (`4e`): `wpid=469328 pgid=469328`, both shell and sleep
  share it, and one call clears them: `after killpg: wpid state=GONE | sleep state=GONE`; `wait` then
  returns `137` (`4i`), which must be `|| :`-guarded.
* **The watchdog's own `kill` needs `2>/dev/null`.** Signalling an already-empty group is an error:
  `pK: kill: (-487362) - No such process`, `second kill rc=1`.

---

## P5 — `set -e` interaction with `wait` returning nonzero

`souji-census.sh:161` is `set -euo pipefail`, so this one decides the patch's shape.

```
== 5a: set -e, wait on a TERM-killed child, bare `wait`
SCRIPT-EXIT=143              <-- script aborted; the next echo never ran
== 5b-2: set -e inside a subshell, bare `wait`
SCRIPT-EXIT=4                <-- subshell exited 4; UNREACHABLE never printed;
                                 and the OUTER script then died too (a plain ( ) is not a condition)
== 5b-1: `wait $pid || rc=$?` under set -e
captured rc=3 (expected 3)
== 5b-8: set -e + `wait` inside a || compound
reached rc=7 ; outer=0
== 5b-9: set -e + `if wait $p; then … else r=$?; fi`
else rc=7 ; reached2 ; outer2=0
== 5b-3/4: rc for a killed child
sigkill rc=137 (expect 137)
sigterm rc=143 (expect 143)
== 5b-5: double wait on the same pid
double-wait rc=0             <-- NOT 127; do not use a second wait as an error probe
== 5b-6/7: timeout(1) alternatives
timeout rc=124 (expect 124)
timeout -k rc=137 (expect 137 after 1s grace)
```

**Verdict: fails as written without the guard.** `wait` on a nonzero child aborts the whole script under
`set -e`, so every `wait` and every `kill` in the new code needs an explicit `|| rc=$?` / `|| :`.
`if wait …; then/else` also captures the status correctly. `timeout(1)` would work (`124`, and `137` with
`-k`), but it forks an extra process per repo and cannot put the child in its own group relative to the
caller — `set -m` remains the better primitive; `timeout` values are recorded only as the control.

---

## Contract-critical consequence: `137` is ambiguous; use a sentinel, not the rc

The contract says a **timed-out** repo becomes the `error` row and the run exits **0**, while **other
nonzero** still exits **1**. But a repo killed by something else (OOM killer, an admin) also yields 137 —
indistinguishable from the watchdog's SIGKILL escalation. T4 shows the discriminating design working:

```
=== T4: census_one SIGKILLed by something else (rc=137, NO sentinel)
rc=1 (contract: 'other nonzero still exit 1' => expect 1) stderr=[souji-census: census failed for … (rc=137)]
=== T5: census_one ignores SIGTERM -> escalation to SIGKILL at bound+2s
rc=0 elapsed_ms=3019 (expect ~3000) stderr=[souji-census: repo-timeout 1s …]
```

So the watchdog must **create a sentinel file before its first signal**, and the parent must attribute the
timeout by the sentinel, not by `143`/`137`. Evaluate `rc = 0` **first**, then the sentinel — that removes
the only false-timeout race (a repo that finishes exactly as the bound expires; its kill hits an empty
group and the sentinel would otherwise win).

---

## End-to-end miniature of the proposed `emit_census` (3 repos, repo2 FIFO-poisoned)

```bash
set -m; ( census_one "$repo" >"$W/row" 2>"$W/err" ) & cpid=$!
set +m
set -m; ( sleep "$BOUND"
          : >"$W/sent"
          kill -TERM -- -"$cpid" 2>/dev/null
          sleep 2
          kill -KILL -- -"$cpid" 2>/dev/null ) >/dev/null 2>&1 & wpid=$!
set +m
rc=0; wait "$cpid" 2>/dev/null || rc=$?
kill -KILL -- -"$wpid" 2>/dev/null || :; wait "$wpid" 2>/dev/null || :
```

Exact output (bound 2):

```
=== EXIT rc=0 elapsed_ms=2048 (expect 0, ~2000)
repo	worktrees	unpushed	dirty	scratch_bytes	mtime_iso	verdict_flags
/var/tmp/…/repo1	1	0	0	0	2026-10-20T00:00:00Z	clean
/var/tmp/…/repo2	0	0	0	0		error
/var/tmp/…/repo3	1	0	0	0	2026-10-20T00:00:00Z	clean
=== STDERR (cat -A)
souji-census: repo-timeout 2s /var/tmp/…/repo2$
=== LEFTOVER PROCESSES
(none)
```

Every clause of the contract in one run: **exit 0**, the healthy neighbours measured, the timed-out repo
as `<repo>\t0\t0\t0\t0\t\terror` (7 fields, empty `mtime_iso`), **exactly one** stderr line and no bash
`Killed` notice, **zero residue**, and the bound actually respected (2.0 s, not 600 s).

Remaining clauses, each measured:

| case | command | result |
|---|---|---|
| watchdog never outlives its repo | 2 repos, bound 600, both instant | `rc=0 elapsed_ms=20`, `stderr=[]`, `leftover sleeps: 0` |
| census_one exit 2 | `return 2` | `rc=2`, `stdout=[]`, refusal replayed on stderr |
| other nonzero | `return 9` | `rc=1`, `census failed for … (rc=9)` |
| TERM-ignoring repo | `trap '' TERM; while :; do sleep 1; done` | `rc=0 elapsed_ms=3019`, error row, one timeout line |
| no per-repo leak | 40 repos, one iteration each | `rc=0 rows=41 elapsed_ms=392 stderr_bytes=0`, `leftover sleeps: 0` |
| L1's exact TOCTOU | PATH `git` shim swaps `info/attributes` for a FIFO on the `status` call, after a guard saw `regular file` | `RC=143 SENT=yes`, 2.00 s, `procs … still alive: []` |

---

## What the patch must respect (source-anchored)

1. **Row shape.** Header is 7 columns — `repo worktrees unpushed dirty scratch_bytes mtime_iso
   verdict_flags` (`tools/souji-census.sh:192`). The existing degraded rows are
   `printf '%s\t0\t0\t0\t0\t\terror\n'` (`:1266`, `:1281`) — note the **double tab** (empty `mtime_iso`).
   The timeout row must be byte-identical in shape.
2. **`sanitize_field`.** `:988-994` replaces tab/LF/CR with a space, and every existing row passes the repo
   through it. `emit_census` receives repo paths from `list_repos`, and a directory name may legally
   contain a tab or newline, so the timeout row must also use `sanitize_field "$repo"` — it is the one new
   row-emission site and would otherwise be a TSV-injection hole.
3. **Replay the child's stderr on refusal.** `census_one`'s `guard_path repo "$1" || exit 2` (`:1262`) and
   `protected_fail`'s `exit 2` (`:223-229`) run inside the forked subshell. Once stderr is redirected to a
   private file, the parent must `cat "$err" >&2` on the `rc=2` **and** other-nonzero paths or the
   protected-refusal diagnostic (masked `<protected>` output included) is lost. On the timeout path do
   **not** replay it — the contract wants exactly the one `repo-timeout` line.
4. **One work dir, one trap.** `emit_census` (`:1394-1416`) has no `EXIT` trap today; the file's precedents
   are `trap cleanup_census_tmp EXIT` (`:1511`, `rm -f`) and `trap 'rm -rf -- "$ST_TMP"' EXIT` (`:1614`).
   Use a single `mktemp -d /var/tmp/souji-census-repo.XXXXXX` for the whole run with fixed `row`/`err`
   names and `rm -rf` in the trap: no per-repo allocation, and P3/T11 prove the child cannot remove it.
5. **Option parsing.** The `case` is at `:2035-2048`; `--repo-timeout` needs a `--repo-timeout N` and
   `--repo-timeout=N` arm plus documentation in the header comment block, because `usage()`
   (`:204-207`) *prints the file's own leading comment block* — an undocumented flag is invisible in
   `--help`. `usage_err` exits 2, matching the contract. Validation: `case "$v" in ''|*[!0-9]*) usage_err …`
   then `1..86400`; run the **same** validation on `SOUJI_CENSUS_REPO_TIMEOUT` so an invalid env value
   also exits 2 (flag > env > 600).
6. **Ordering after `wait`:** `rc=0` first, then sentinel, then `rc=2`, then other-nonzero.
7. **Guards under `set -e`:** `wait … || rc=$?`, `kill … || :` everywhere (P5). Bash low-byte statuses are
   `143 = 128+15`, `137 = 128+9`.

## Scoping fact — the bound covers every production git call

Every production git invocation is in `census_one` (`:1261`) or a helper reached only from it:
`:1000, :1006, :1010, :1014, :1027, :1069, :1085-1090, :1122, :1253, :1280`. `list_repos` (`:1343`)
runs **no** git. The only `rev-parse --is-inside-work-tree` site is `:1280`, inside `census_one` — which is
exactly the frame the host's leaked processes are blocked in
(`leaked-procs-before-1631.txt:2`: `git -C /var/tmp/r15-census-config…/r-inc-fifo rev-parse
--is-inside-work-tree`). A watchdog at the per-repo boundary therefore covers the whole hang surface; no
second bound is needed around `list_repos`. `list_repos`' own guards only `stat` and can only `exit 2`,
which is the designed refusal, not a hang.

## Residual risks (not exercised; stated as inference)

* **[INFERENCE]** `set -m` inside a script running on a real terminal leaves the child in a
  *background* group w.r.t. the tty. A child that *reads* the tty would take `SIGTTIN` and stop — but job
  control gives it `/dev/null` on stdin (P1, measured), and `census_one` reads no stdin, so this cannot
  bite. Output goes to a file, so `SIGTTOU` is not in play either.
* **[INFERENCE]** A `$( … )`-captured census whose own `EXIT` trap runs `rm -rf` is safe only because the
  trap is inherited-but-not-run by the child (P3, measured). Do not move the `rm -rf` into the child.
* Rows are still buffered and printed after the loop (`:1412-1415`); if the *census itself* is SIGKILLed
  the rows are lost. Out of contract (the contract only bounds one repo), noted only because it is the same
  "neighbours' rows lost" symptom through a different door.

No tools were installed or upgraded for this work (no pacman transaction was run; the host-wide pause was
respected).
