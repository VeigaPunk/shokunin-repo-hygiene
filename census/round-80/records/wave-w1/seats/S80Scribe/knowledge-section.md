## A session front for tools that use `$(...)` everywhere (r80, souji-quarantine.sh)

- The r79 pattern (each child an async job the shell `wait`s on) fits a gate with 12 flat call sites
  (`tools/souji-pre-report-gate.sh`, 388 lines). `tools/souji-quarantine.sh` is 1935 lines at base with 242 `$(`
  outside comments; its four bounded children (120/120/60/300 s) sit in functions themselves called in `$(...)`
  (`content_digest` -> `dir_digest`, line 891), so each depth's stdout/rc plumbing would change, and a trap in the
  outer shell still waits for the innermost substitution (S325). At base TERM/HUP killed the shell, timeout's group
  survived, and INT had not exited at 5 s (`census/round-80/controls/c2-K-a-do-nothing.txt`: 12/12 orphaned).
- r80 splits the tool: the front starts the worker (the same file) as `SOUJI_Q_WORKER=1 TMPDIR=<private mktemp dir>
  setsid "$BASH" "$SELF" "$@" <&0 &` and only `wait`s. A `&` job of a non-interactive shell is not a process-group
  leader, so setsid execs in place: "setsid runs a program in a new session. The command calls fork(2) if already a
  process group leader. Otherwise, it executes a program in the current process." (S328, line 37). `$!` is then the
  session id; descendants that do not call setsid stay in it (S326 changes the group, not the session).
- On TERM/INT/HUP the front's trap fires at once (it is in `wait`, S325): SIGSTOP then SIGKILL every process whose
  `/proc/<pid>/stat` field 6 equals the worker pid (S068; after the last `) `, builtins only, no fork), at most 8
  passes, remove the private TMPDIR, print `SIGNAL<TAB>SIG<name><TAB>RECEIPT-QUARANTINE-SIGNALED`, exit 128+n.
- Measured (`census/round-80/records/c2-after.txt`): 15 rows, 0 mismatches, 0 orphans, worst 3.9 s; trap-only and
  worker-pid-only controls stay at 12 orphan rows each (`controls/c2-K-b-trap-only.txt`,
  `c2-K-c-no-session-kill.txt`); p1-p3 keep their verdicts, no SIGNAL line.
- Limits: SIGKILL to the front; a descendant that calls setsid itself or double-forks; a SIGINT the caller ignored on
  entry (S325); stage-2 mv and stages 4-5 (same mechanism, no row). The SIGNAL line prints even if the 8 passes ended
  with survivors (`q_kill_session` returns 0 after the loop), so the census, not the line, is the evidence; and the
  front never checks `$!` is a session leader — under job control (`bash -m`) the `&` job IS a group leader, setsid
  forks, `wait` returns at once, the EXIT trap deletes the TMPDIR, and the tool exits 0 with no verdict (probe: rc=0
  in 140 ms, 0 lines, worker dead on a missing `mktemp` dir).
