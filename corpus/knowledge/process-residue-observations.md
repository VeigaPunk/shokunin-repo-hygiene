source: S082, S083, S084, S085 (opened 2026-10-21); S075, S076 (rechecked 2026-10-21); own-work `tools/souji-proc-census.sh`
verified-at: base 3ab2c81479f5004c8bc91946eea482caec45408f; man-pages 6.19 (2026-02-08); host Linux 7.2.11-arch1-1
recheck: `bash tools/souji-proc-census.sh --selftest` and `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh` (fixture P1–P19, scratch only under /var/tmp)

# Process residue as an observed, list-only surface (F5)

A process can outlive the file it references. Souji lists that residue for
its own uid; it does not reap it, and a listed row is a nomination, never a
removal receipt. This entry is the knowledge bar for that surface: what the
kernel interface actually documents, what souji measured, and where the
claim stops.

## What the kernel documents

- `/proc/pid/cwd` is a symlink to the process's current working directory
  (S082). Reading or dereferencing it requires a ptrace access-mode
  `PTRACE_MODE_READ_FSCREDS` check.
- `/proc/pid/fd/` has one entry per open file, each a symlink to the actual
  file; entries for pipes and sockets carry `type:[inode]` instead of a
  pathname (S083). The same ptrace permission rule applies.
- `/proc/pid/wchan` is "the symbolic name corresponding to the location in
  the kernel where the process is sleeping" (S084), also permission-checked.
- `/proc/pid/status` restates much of `stat`/`statm` in a human-parseable
  form (S085); `State` is one of `R`, `S`, `D`, `T`, `t`, `Z`, `X`.

**The docs do not document the `(deleted)` suffix for `cwd` or `fd`.** Only
`proc_pid_exe(5)` says the string is appended to an unlinked pathname
(S076), and that sentence describes `exe`. Treating cwd/fd suffix text as a
documented fact would be the r18 R18-M7 overreach class. The cwd/fd suffix
is an observed kernel behaviour carried by the committed fixture cases, not
by a quote.

## What souji lists

`bash tools/souji-proc-census.sh [--prefix DIR]... [--min-age S]` emits one
row per own-uid process whose:

- `cwd` link ends in ` (deleted)` (any location), or
- `argv` names a scratch path whose top-level directory is gone, or
- an `fd` link names such a path.

Columns: `pid, ppid, pgid, sid, age_s, starttime, state, wchan, reason,
cmd`. Precedence is cwd > argv > fd, so one process yields one row.
`--prefix` limits argv/fd evidence only, never cwd.

Identity binder: `(pid, starttime, boot_id)`. `starttime` is proc stat field
22 (S075); `boot_id` heads every table so a snapshot cannot be compared
across a reboot. A pid alone is never identity.

Safety rules (the whole point of the surface):

1. **No signal in census mode.** The tool never signals; selftest signals
   only workers it spawned after checking their session. A no-signal claim
   is verified by tracing signal syscalls (fixture P7), not by liveness.
2. **No `environ`.** The tool reads `stat`, `status`, `cmdline`, `cwd`, `fd`
   and `wchan` only. `environ` would leak secret material and is outside the
   surface.
3. **Redaction.** Secret-shaped argv (headers, AWS keys, Slack tokens) is
   redacted before printing; argv is truncated.
4. **Literal names are not residue.** A live cwd/fd whose literal path ends
   in ` (deleted)` is classified by comparing the inode of the held link
   with the named target (S076 semantics applied to cwd/fd as a fixture
   rule); the raw suffix alone is not proof (S076; QUALITY Q33).

## Documented failure case

At r18 the census and an independently written counter disagreed stably on
one pid (1659) because the counter excluded every ancestor of its own
process chain; launched from a GUI, that hid the compositor's deleted shm
fd. The counter was narrowed to exclude only its own pid, and two later
two-window snapshots agreed 66 = 66 with identical pid sets. The failed
observation is retained in `census/round-18/proc-agreement-final.json`; the
repaired pair is `census/round-18/proc-agreement-counterfix.json`. Two
implementations agreeing is still not proof of a shared-bug's absence; it is
a dated observation.

## Limits

- **No reap authority.** Reaping a listed process requires operator
  approval, fresh `(pid, starttime, boot_id)` verification at act time, and a
  LOG record. Souji's fixtures signal only their own spawned workers.
- **Own uid only.** Other uids and host-wide liveness are mori's ground;
  resource findings route there. This entry does not absorb that scope.
- **No atomic snapshot.** `/proc` is read incrementally; a process may exit
  or change state between rows. Counts are observations, not a census of the
  machine.
- **Not a filesystem proof.** The list says a link names a missing path; it
  does not prove the file's bytes are unrecoverable or that any artifact is
  safe to delete.
- **Unmeasured: PID-namespace differences.** The tool reads the namespace
  it is in; nested-pid columns (`NSpid`) are not used.
