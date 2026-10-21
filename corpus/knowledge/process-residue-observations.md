source: S082, S083, S084, S085; S075, S076; S100 (CWE-532), S101 (OWASP Logging); own-work `tools/souji-proc-census.sh`
verified-at: reason-only synthetic repair 4d5bf78432de7f4afe38e6bf195fd7843bdcb7e3 (r21); historical scanner base 3ab2c81479f5004c8bc91946eea482caec45408f; man-pages 6.19 (2026-02-08)
recheck: synthetic-only `bash tests/fixtures/r21-reason-canary.sh --tool tools/souji-proc-census.sh --base <6ff3413 tool file>`; historical live-proc fixtures require a separate authorized run and were NOT run in r21

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

## Correction (appended after wave 1b, 2026-10-21)

The "reads only" list above is incomplete: the census also reads `/proc/uptime` (for `age_s`),
the `boot_id` header, and lists `/proc` to enumerate pids. It still never reads `environ`. The
full read set is listed in `.ufo/waves/round-19/w1/ScribeProcSkillRow.md`; no tool behaviour
changed. Also, Q32's read list omits `status`, which the tool reads; Q33 supersedes the wording
but not that list.

## Round-20 precision correction (supersedes the broad read/enumeration wording above)

source: S082, S086, S087, S088; S075/S076 for field/suffix attribution; exact own-code and fixture bindings below.
verified-at: baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812`; read-only SHA-256 observation on2026-10-21, not a fresh process census.
recheck: `sha256sum tools/souji-proc-census.sh tests/fixtures/r18-proc-census.sh census/round-18/leak-count.py`; isolated behavior command remains the initial fixture command.

Use S086–S088 instead of the superseded S083–S085 teaches claims. Kernel-page facts and lane
policy remain separate: the pages describe links/sleep context/state formatting, not disappearance,
reaping, liveness or universal redaction guarantees. The implementation observed at this revision is:

| owned file | SHA-256 |
|---|---|
| `tools/souji-proc-census.sh` | `37c3316a1fd8cdda18cbefdc7692d3d3f388e5783e8fe19085f5d932a8ceba64` |
| `tests/fixtures/r18-proc-census.sh` | `01995f8d79f128b07dfab50ca317c13069adcd1ed933fd9325295610d56758be` |
| `census/round-18/leak-count.py` | `a26530199434ecddf4b36d2513730765bb0ae7487fa3c007f9c04d33244ebb3b` |

The read set includes the proc directory listing, uptime, boot_id, stat, status, cmdline, cwd,
fd directory/link names and wchan; no environ read is present in the bound implementation.
This is static code evidence plus the historical fixture, not a claim about an exercised live scan
this round. Enumeration is only eligible readable own-uid candidates; self/descendants can be
excluded, unreadable or racing data skipped. The broad “one row per own-uid process” wording above
does not promise exhaustive machine coverage.

Raw cmdline/argv is read **before** printing-time redaction. The tested fake header/AWS/Slack
shapes are not a universal private-value or output-redaction proof. `reason` has separate sanitation
from `cmd`; a credential-shaped argv-derived path escaping that separate field remains
**[INFERENCE]**, not an observed leak. No live private-value probe was performed or authorized.

Other uids are outside this tool's surface; this does not assign all other-uid residue to Mori.
Health/liveness/resource findings may route to Mori, host repair to Tsukuroi and credential concerns
to Kagi; contested scope stays operator-owned. F5 reap remains held at the specific
`souji | round-18` request. Listing/nomination never authorizes signal, quarantine or deletion;
the historical58-orphan figure is not a current count. See `corpus/lessons/round-20.md` and Q42.

### Round-20 exclusion precision (Q43)

The bounded parent-chain snapshot excludes the scanner and descendants that
`is_self_tree` recognizes (its ancestry walk is bounded to 512 hops); unreadable,
racing, UID-transition or identity-mismatch candidates are skipped. This is the
same eligibility boundary meant by the preceding correction's “can be excluded”,
not exhaustive descendant discovery. Evidence: the already-bound implementation
`tools/souji-proc-census.sh` `is_self_tree`, snapshot construction and final UID/
starttime rechecks; no new process census was run. This correction improves the
existing entry's precision; it creates no new knowledge path or coverage-map ground.

### Round-20 fd access source mapping (S095)

source: S095 — https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html,
Linux man-pages6.19 (2026-02-08), DESCRIPTION permission paragraph, reopened2026-10-21.
The fd-link permission sentence in the original kernel-facts list is supported
by this specific opened scope: reading or dereferencing those symlinks is
governed by PTRACE_MODE_READ_FSCREDS. S086 still teaches entries and link
contents; neither source grants Souji access to private values or signal authority.

### Final round-20 source and privacy correction

S096 supersedes S095's teaching: the fd access-mode fact comes from the page;
the prohibition on private-value probes and signalling is Souji policy, not
that page's teaching. The located permission quotation remains unchanged.

This explicitly supersedes Safety rules item 3 above and any unqualified
argv-redaction wording in Q32 or the r19 SKILL pattern: tested fake canaries
exercise **cmd**, not **reason**. The reason column contains argv/fd path
text with control-byte sanitation only. A credential-shaped path can remain
visible there; that is a real source-level privacy defect, not proof of a
secret-free read or fully redacted table. No private-value payload, live proc
scan or historical TSV was inspected to measure exposure this round.

The raw-read and reason-output risk is operator/Kagi-owned for exposure
assessment; a separate synthetic-only repair needs the recorded round20 L0
ruling. No scanner code or canary fixture is changed here. Observation and
nomination grant no reap, deletion, snapshot-purge or credential authority.

## Round-21 reason output repair — synthetic only

The r20 privacy finding is repaired in the current output path, not erased
from its historical record. CloseSouji20 routed a synthetic-only reason repair;
historical exposure remains unmeasured under operator/Kagi ownership. S100
warns against secrets in logs; S101 separately requires sensitive-data masking
and control-character sanitation. Neither source promises universal masking.

`cmd` and the path-bearing `reason` now use one ordered eight-pattern redactor.
Both replace control bytes and bound the whole field to 160 bytes. A selected
argv gone-path retains its originating argument's secret classification:
the value following `--token`, `--token=...`, `--password=...`, `password=...`
or an argument changed by an inherited secret pattern yields
`argv-path-gone:[REDACTED]`. Thus extracting the path does not erase the token
marker. An ordinary short path remains byte-exact; fd path text goes through
the same patterns and whole-field bound.

Proc-free replay:

```sh
# Fabricated nonexistent path only; this mode opens no /proc files.
printf 'worker\0--token=/var/tmp/souji-r21-example-nonexistent/file\0' |
  bash tools/souji-proc-census.sh --reason-only argv --prefix /var/tmp
# argv-path-gone:[REDACTED]
```

`--reason-only argv` reads NUL-separated synthetic cmdline bytes and uses the
same stream parser and formatter as the census. `--reason-only fd` reads one
synthetic target (one trailing newline removed). Exit 0 prints one reason;
exit 3 prints nothing when no gone path qualifies. The branch exits before
process enumeration, boot-id or uptime reads.

Evidence: `census/round-21/reason-oracle-before.txt` versus `reason-after.txt`:
the same27-case oracle goes6/27→27/27, fabricated leaks19→0, maximum
reason454→160 bytes. Base function bodies are extracted exactly; only their
input path points to a generated cmdline file, never /proc. The two
arbitrary-input output sinks are now covered,1/2→2/2; wchan and the kernel
identity/state fields are not asserted to be universal redaction surfaces.
Eight inherited cmd-pattern probes are byte-identical (`cmd-compatibility.json`).

This does not establish secret-free reads, historical live exposure, encoded
or unknown secret detection, or a complete scanner recheck. Raw argv/fd paths
still enter memory. The r18 live-proc selftest and fixture were not run.
No change to own-uid/racing/recognized-descendant boundaries, certification
OFF, K5 HELD, or inherited reap/NAMESPACE holds.
