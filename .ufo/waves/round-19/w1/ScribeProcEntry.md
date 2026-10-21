STATUS: DONE — proposal text for the C3 F5 knowledge entry drafted and checked against the base (3ab2c81) and worktree bytes; the entry already exists as integrated (commit 005f3d3, not at base), so the proposal is a revision of it, not a new file; 8 defects in the integrated bytes are listed, one of which (the `State` letter list attributed to S085) also sits in SOURCES.md, L1-owned.

# Findings

## Status of the target file
- `corpus/knowledge/process-residue-observations.md` is NOT absent: it is tracked in the lane (`git log` → `005f3d3 round-19: … F5 process-residue entry …`, blob `7e9242d8…`, worktree identical to HEAD). `git show 3ab2c81:corpus/knowledge/process-residue-observations.md` fails, so the entry is new in r19. This report therefore proposes replacement text for the integrated bytes; it does not create the file, and it does not edit it.
- Admission shape is mechanical (`census/round-13/count-claims.py:38`): the first three lines must start `source:`, `verified-at:`, `recheck:`, and the body must not contain `## Admission status — HELD`. The proposal keeps that shape.

## Defects in the integrated entry (`005f3d3` bytes), each checked against the bytes
1. **Source omits the committed fixture.** Line 1 cites S082–S085, S075/S076 and the tool, but not `tests/fixtures/r18-proc-census.sh`, which the item requires.
2. **verified-at omits git and tool identity.** Line 2 gives base, man-pages and kernel, but not the git version (2.56.0) and not that the tool and fixture bytes equal the base bytes. Tool sha256 `37c3316a…` matches base, the worktree and `4800fd7` (the r18 measurement commit); fixture sha256 `01995f8d…` matches base and the worktree.
3. **The `State` letter list is attributed to S085 and is wrong for that page.** Line 24 says `State` is one of `R, S, D, T, t, Z, X`, citing S085. `proc_pid_status(5)` (man-pages 6.19-1) gives only `State: S (sleeping)` as an example; it does not enumerate letters. The letter list is `proc_pid_stat(5)` field 3, and that page lists R, S, D, Z, T, t, W, X, x, K, W, P, I (I and P are kernel-version-scoped). The S085 teaches cell in `SOURCES.md` carries the same overstatement (L1-owned; see Routed).
4. **Redaction is overstated.** Line 59 "Secret-shaped argv (headers, AWS keys, Slack tokens) is redacted" implies a general guarantee. `tools/souji-proc-census.sh:192-228` redacts a fixed pattern list (`Authorization: Bearer`, `--token=`, `ghp_`, `sk-`, `password=`, `scheme://user:pass@`, `AKIA…`, `xox…`) and nothing else; `cmd` is cut to 160 bytes after redaction (`:227`).
5. **Scope of argv/fd is under-stated.** Lines 38–44 omit the default prefixes (`/var/tmp`, `/tmp`, `/dev/shm`; `:100-101`), that an argv candidate must be absolute or `--opt=/path` and must not exist (`:236-240`), and that fd links are read only for an absolute target whose top-level is gone (`:263-267`).
6. **Silent omission is not stated.** A process whose cwd `readlink` fails gets `cwd=''` (`:340`) and an unreadable fd link is skipped (`:263`); the row is dropped with no error. The entry says nothing about this, so "absent from the list" could be misread as "holds nothing".
7. **Identity-binder mechanics are thin.** Lines 46–48 name `(pid, starttime, boot_id)` but not where boot_id appears (the `# boot_id <id>` header comment, `:322`) or that starttime and uid are rechecked before a row is emitted (`:330`, `:371-374`), which is what stops a reused pid from mixing data into one row.
8. **Safety rule 1 wording is loose.** Line 53 says the selftest signals "workers it spawned after checking their session". The check (`:402-408`, `:416`) matches pid, parent, process group, session and starttime, and the only signal is `kill -KILL` in cleanup (`:417`).
9. **Failure case and recheck need precision.** Lines 67–75 say "two later two-window snapshots"; the record shows two pairs at `after_pairs [[66,66],[66,66]]` (`census/round-18/counter-exclusion-repair.json`, `proc-agreement-counterfix.json`). The failure is at `4800fd7` (not stated), the cause sentence should cite `census/round-18/leak-count.py:143-147` (whose comment says the ancestor exclusion "hid Hyprland's deleted shm fd when launched through the GUI"), and the recheck names no expected output and no `strace` dependency (fixture P7 needs it; `strace -- version 7.2` is installed).

## Verified facts the proposal relies on (no change needed)
- Local man pages 6.19-1 match the S082–S085 quotes: cwd "This is a symbolic link to the current working directory of the process." (`proc_pid_cwd.5.gz`, §DESCRIPTION, line 13); fd pipes/sockets "file type with the inode" and `type:[inode]` (`proc_pid_fd.5.gz`, lines 18–27); wchan "The symbolic name corresponding to the location in the kernel where the process is sleeping." (`proc_pid_wchan.5.gz`, lines 12–14); status "Provides much of the information in /proc/pid/stat …" (`proc_pid_status.5.gz`, line 13).
- No `deleted` string appears in `proc_pid_cwd`, `proc_pid_fd`, or `proc_pid_wchan`; only `proc_pid_exe.5.gz` (line 25) carries the `(deleted)` suffix. The entry's "the docs do not document the suffix for cwd or fd" is correct.
- Tool columns, precedence, `--prefix` scope, identity fields, no `environ` (grep: zero hits), and single kill site match the entry (`:35-44`, `:104-133`, `:339-357`).
- Failure record: `census/round-18/proc-agreement-final.json` has `stable_tool_missing_counter: [1659]`, `pass: false`, both pairs tool 66 / counter 65, `tool_only [1659]`. Pid 1659 is `Hyprland --watchdog-fd 4`, ppid 1654, reason `fd-path-gone:/dev/shm/e193e6b6-…`, starttime 1560 (every snapshot file). `counterfix` pairs: 66 = 66, `identical_pids True`.
- PROVINCE routing: `PROVINCE.md:73-78` keeps other uids and host-wide liveness with mori and says nominations, not receipts.

## Proposed replacement text (for `corpus/knowledge/process-residue-observations.md`)

```
source: S082 proc_pid_cwd(5), S083 proc_pid_fd(5), S084 proc_pid_wchan(5), S085 proc_pid_status(5) (opened 2026-10-21); S075 proc_pid_stat(5), S076 proc_pid_exe(5) (rechecked 2026-10-21); own work `tools/souji-proc-census.sh` and `tests/fixtures/r18-proc-census.sh`
verified-at: base 3ab2c81479f5004c8bc91946eea482caec45408f (tool sha256 37c3316a…, fixture sha256 01995f8d…; the tool bytes are identical at r18 measurement commit 4800fd7); man-pages 6.19-1 (`.TH` 2026-02-08); git 2.56.0; strace 7.2 (fixture P7); host Linux 7.2.11-arch1-1
recheck: `bash tools/souji-proc-census.sh --selftest && bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh` — run from the lane root; expect the selftest PASS line and fixture `SUMMARY total=19 failed=0`; needs strace; signals only its own spawned workers; scratch only under /var/tmp

# Process residue as an observed, list-only surface (F5)

A process can outlive the file it names. Souji lists that residue for its own
uid. It does not reap it: a listed row is a nomination, never a removal
receipt, and this entry grants no reap authority.

## What the kernel documents

- `/proc/pid/cwd` is a symbolic link to the process's current working directory
  (S082). Access is governed by a ptrace `PTRACE_MODE_READ_FSCREDS` check.
- `/proc/pid/fd/` has one entry per open file, each a symbolic link to the file
  (S083). Pipes and sockets read `type:[inode]` rather than a pathname.
- `/proc/pid/wchan` is the symbolic name of the kernel location where the
  process sleeps (S084). It is context for a row, never proof of what the
  process is blocked on.
- `/proc/pid/status` restates much of stat and statm in parseable form (S085).
  The census prints `State` as context. The letter set is documented in
  proc_pid_stat(5) field 3, not in S085; this entry claims no closed list.
- The `(deleted)` suffix is documented only for `exe` (S076). The cwd and fd
  pages say nothing about it. The cwd/fd rule below is carried by the committed
  fixture, not by a quote.

## What souji lists

`bash tools/souji-proc-census.sh [--prefix DIR]... [--min-age S]` prints one row
for each own-uid process (the `Uid:` field in `/proc/pid/status` equals the
caller's uid) that matches one of these reasons. Precedence is cwd > argv > fd,
so each process yields at most one row:

- `cwd-deleted`: the cwd link ends in ` (deleted)`, at any location, and the
  literal path is not a live file with the same inode as the held link.
- `argv-path-gone:<path>`: an absolute argv path, or the value of a
  `--opt=/path` argument, does not exist, and its top-level directory under a
  scratch prefix is gone. Default prefixes are `/var/tmp`, `/tmp`, `/dev/shm`;
  `--prefix` narrows only argv and fd evidence, never cwd.
- `fd-path-gone:<path>`: an fd link ends in ` (deleted)`, its target is an
  absolute path under a scratch prefix, and that top-level directory is gone.
  A live literal name is exempt, as for cwd.

Output starts with a `# boot_id <id>` comment line, then the ten-column TSV
header `pid ppid pgid sid age_s starttime state wchan reason cmd`. `cmd` is
redacted and then cut to 160 bytes.

Rows are absent, not reported as errors, when a /proc link cannot be read.
Absence is not proof that a process holds nothing.

## Identity binder

Identity is `(pid, starttime, boot_id)`. `starttime` is `/proc/pid/stat` field 22
in clock ticks (S075). `boot_id` is printed in the header comment, so a snapshot
is never compared across a reboot. The census rereads starttime and uid before
it emits a row, so no row mixes data from a reused pid. A pid alone is never
identity.

## Safety rules

1. **No signal in census mode.** The census issues no signal. `kill` appears
   only in selftest cleanup, which signals a recorded worker only when its pid,
   parent, process group, session and starttime still match. Signal-free
   operation is verified by tracing syscalls (fixture P7 uses strace), not by
   process liveness (QUALITY Q33).
2. **No `environ`.** The census reads `stat`, `status` (uid only), `cmdline`,
   `cwd`, `fd`, `wchan`, `/proc/uptime` and boot_id. It never opens `environ`.
3. **Redaction is pattern-bounded.** Secret-shaped argv (an `Authorization:
   Bearer` header, `--token=`, `ghp_`, `sk-`, `password=`, `user:pass@` URLs,
   AWS `AKIA` keys, Slack `xox` tokens) is replaced with `[REDACTED]`. A secret
   in any other shape is not redacted, and the census makes no broader claim.

## Literal names and inodes

A live cwd or fd whose literal path ends in ` (deleted)` is not residue when the
path exists and has the same inode as the proc link (fixture P12 for cwd, P13
for fd; the census uses an `-ef` comparison). The raw suffix alone is not proof.
This applies the S076 class to cwd and fd by fixture, not by documentation.

## Documented failure case: r18 pid 1659

At the r18 measurement commit 4800fd7, the census and a standalone counter
disagreed stably on one pid. `census/round-18/proc-agreement-final.json`
(`stable_tool_missing_counter: [1659]`, `pass: false`) records tool 66 rows
against counter 65 in both pairs, with 1659 tool-only. Pid 1659 is
`Hyprland --watchdog-fd 4` (ppid 1654) holding `fd-path-gone:/dev/shm/e193e6b6-…`.
The counter excluded every ancestor of its own chain; `census/round-18/leak-count.py:143-147`
says that exclusion "hid Hyprland's deleted shm fd when launched through the GUI".
The repair excludes only the counter's own pid (`census/round-18/counter-exclusion-repair.json`).
The repaired pairs in `census/round-18/proc-agreement-counterfix.json` agree
66 = 66 with identical pid sets. Two implementations agreeing is a dated
observation, not proof that a shared bug is absent.

## Limits

- **No reap authority.** A listed row is a nomination. Reaping needs operator
  approval, a fresh `(pid, starttime, boot_id)` check at act time, and a LOG
  record. The 58 fixture orphans remain unreaped; the operator ruling is open.
- **Own uid only.** Other uids and host-wide liveness belong to mori
  (`PROVINCE.md:73-78`).
- **Not atomic.** `/proc` is read in passes, and a process can change between
  them. The starttime recheck bounds pid reuse, not concurrency.
- **Unbounded stats.** Candidate paths are stat-ed with no timeout, so an
  unresponsive filesystem can block the census. This is not measured.
- **Silent omission.** An unreadable /proc link drops a row without an error.
- **Namespaces not measured.** `NSpid` is not read.
- **Shared-bug absence not proven.** The agreement above is one dated
  observation, not a proof.
```

## Routed (L1-owned, not edited here)
- `SOURCES.md` S085 teaches cell says "State is one of R, S, D, T, t, Z or X". That is not in `proc_pid_status(5)`. Either supersede S085 with a row citing `proc_pid_stat(5)` field 3 (a new source row, opened by a seat) or correct the teaches cell. The integrated entry should not be relied on for the letter set until that is decided.
- The S075 row cites fields 5, 6, 22 only; the State letters are field 3 and need their own row if the entry is to name them.

# Evidence

Quotes are short and located; all came from the local man-pages 6.19-1 copies at `/usr/share/man/man5/*.5.gz` (the same revision the S-rows cite). The live man7 URLs were not opened (not named in the item).
- `proc_pid_cwd.5.gz` line 13: "This is a symbolic link to the current working directory of the process." (13 words)
- `proc_pid_fd.5.gz` lines 13–15, 18–20: "a symbolic link to the actual file" / "the entries will be symbolic links whose content is the file type with the inode." (13 words)
- `proc_pid_status.5.gz` lines 13, 25: "Provides much of the information in … format that's easier for humans to parse." and the sole State example `State:  S (sleeping)`.
- `proc_pid_stat.5.gz` field 3 list: R Running; S Sleeping in an interruptible wait; D Waiting in uninterruptible disk sleep; Z Zombie; T Stopped (on a signal); t Tracing stop; W; X; x; K; W; P; I.
- Tool and fixture line references: `tools/souji-proc-census.sh` header `:13`, `:100-102`, `:168-186`, `:188-228`, `:230-257`, `:258-276`, `:286-292`, `:322`, `:330`, `:339-357`, `:359-364`, `:371-374`, `:402-417`; `tests/fixtures/r18-proc-census.sh:5-20` (P1–P19), `:752` (`SUMMARY total=19`).
- Failure: `census/round-18/proc-agreement-final.json`; `census/round-18/proc-agreement-counterfix.json` (`pairs`, `identical_pids`); `census/round-18/counter-exclusion-repair.json` (`cause`, `after_pairs`); `census/round-18/leak-count.py:143-147`; `census/round-18/proc-census-final-1.tsv` and `proc-census-live-1721.tsv` row for 1659.
- Admission: `census/round-13/count-claims.py:38`.
- Routing: `PROVINCE.md:73-78`.

# Commands run
All read-only; no census, fixture, or lane tool was executed.
- `git --version` → 2.56.0
- `git status --short`; `git log --oneline -3`; `git log --oneline -- corpus/knowledge/process-residue-observations.md`; `git hash-object corpus/knowledge/process-residue-observations.md` → `7e9242d8…`
- `git show 3ab2c81:tools/souji-proc-census.sh | sha256sum` → `37c3316a…`; `sha256sum tools/souji-proc-census.sh` → `37c3316a…`; `git show 4800fd7:tools/souji-proc-census.sh | sha256sum` → `37c3316a…`
- `git show 3ab2c81:tests/fixtures/r18-proc-census.sh | sha256sum` → `01995f8d…`; `sha256sum` of the worktree copy → `01995f8d…`
- `git log 3ab2c81..HEAD -- tools/souji-proc-census.sh tests/fixtures/r18-proc-census.sh` (empty); `git diff --stat 3ab2c81 -- …` (empty); `git merge-base --is-ancestor 4800fd7 3ab2c81` (ancestor)
- `git show 3ab2c81:corpus/knowledge/process-residue-observations.md` → absent
- `git ls-files corpus/knowledge`; `sha256sum corpus/knowledge/process-residue-observations.md` (read only)
- `pacman -Q man-pages` → `man-pages 6.19-1` (query only; no transaction)
- `zcat /usr/share/man/man5/proc_pid_*.5.gz` with `grep`/`sed` for quotes, `.TH` dates and state list
- `man -w -S 5 …` path lookups
- `strace -V` → `strace -- version 7.2` (version query only; strace was not run against any census)
- `grep`/`sed`/`cat -n` over the lane tool, fixture, census artifacts, corpus, SOURCES, PROVINCE, count-claims
- `python3` read-only JSON parse of `census/round-18/proc-agreement-final.json` and `proc-agreement-counterfix.json` (no writes)
- Network: none.

# Contract compliance
- Wrote only the report at `.ufo/waves/round-19/w1/ScribeProcEntry.md` (lane-relative, resolved under the lane root). Did not create `corpus/knowledge/process-residue-observations.md`, and did not edit any lane file, SOURCES, QUALITY, README, SKILL or PROVINCE.
- No git or jj mutation; read-only git only. `jj-lane.sh` not run.
- No process signalled; no `/proc/*/environ` read; no census, fixture, or lane tool executed.
- Tool installs: none. (`pacman -Q` is a query and is not a transaction.)
- Scratch: none created under /var/tmp or elsewhere, so no cleanup was needed.
- Leaf seat: no subagent dispatch, no `ask`, no agent messages sent.
- Quotes: all ≤25 words, from local man-pages 6.19-1, with located anchors; access date 2026-10-21.
- Checks for the main agent to run after integration: `ls corpus/knowledge/*.md` count and the `count-claims.py` admission count, and the recheck command in the proposal's header, run once after the entry is replaced (not run here).
