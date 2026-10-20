STATUS: DONE — drafted SOURCES rows S064 (proc_pid_cwd) and S065 (proc_pid_stat) for C3 with located ≤25-word quotes; no repo writes beyond this report.

# ScribeRowsProc — C3 frontier rows (draft, for L1 integration)

Scope: draft only. Not appended to `corpus/SOURCES.md`; L1 owns registry admission and the round-18 gate record in `corpus/lessons/round-18.md`.

## Accessed

| item | value |
|---|---|
| URL 1 | https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html |
| URL 2 | https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html |
| access date | 2026-10-20 (opened by ScribeRowsProc seat) |
| version stamp served | "Linux man-pages 6.19 2026-02-08"; page COLOPHON says tarball man-pages-6.19 fetched 2026-09-09 |
| tool used | `read` (web reader, rendered text) |

## Draft rows (registry shape of S051–S063)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S064 | proc(5) /proc/pid/cwd — https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html | docs | A | the cwd link and its read-permission gate; not what the kernel prints for a removed directory | Linux man-pages 6.19 (2026-02-08), opened 2026-10-20; § DESCRIPTION /proc/pid/cwd | /proc/pid/cwd is a symlink to the process's current working directory; reading or dereferencing it is governed by a PTRACE_MODE_READ_FSCREDS check, so an unreadable cwd is a denied read and not a missing process; the page does not describe a deleted directory or any suffix shown for one | queued | 2026-10-20 | on-release | — |
| S065 | proc(5) /proc/pid/stat — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | docs | A | per-field meaning of state, ppid, pgrp, starttime, comm and wchan, and the [PT] access rule; not any path, cwd or argv content | Linux man-pages 6.19 (2026-02-08), opened 2026-10-20; § DESCRIPTION /proc/pid/stat fields (3) state, (4) ppid, (5) pgrp, (2) comm, (22) starttime, (35) wchan; kernel source fs/proc/array.c as named by the page | queued | 2026-10-20 | on-release | — |

Teaches for S065 in full: state D is uninterruptible disk sleep; starttime is in clock ticks after boot, so age needs sysconf(_SC_CLK_TCK) and the boot time; fields marked [PT] read as 0 when the ptrace check denies access; comm is silently truncated at 16 characters; wchan is a kernel address whose symbol is read from /proc/pid/wchan.

## Located quotes (verbatim from the rendered page; ≤25 words each)

Q-S064-1 (DESCRIPTION, /proc/pid/cwd), 13 words:
> "This is a symbolic link to the current working directory of the process."

Q-S064-2 (DESCRIPTION, /proc/pid/cwd), 18 words — the limit:
> "Permission to dereference or read (readlink(2)) this symbolic link is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check"

Q-S065-1 (DESCRIPTION, field (3) state, D entry), 5 words:
> "Waiting in uninterruptible disk sleep"

Q-S065-2 (DESCRIPTION intro, [PT] rule), 13 words:
> "If the check denies access, then the field value is displayed as 0."

Q-S065-3 (field (22) starttime), 13 words:
> "Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK))."

Q-S065-4 (field (2) comm), 14 words — the truncation limit:
> "Strings longer than TASK_COMM_LEN (16) characters (including the terminating null byte) are silently truncated."

Q-S065-5 (field (35) wchan, 1st sentence), 14 words:
> "It is the address of a location in the kernel where the process is sleeping."

Quote check: each string above was copied from the rendered text returned by `read` on 2026-10-20 and word-counted by hand. Rendered-text whitespace was joined to single spaces; no words changed.

## What the rows do NOT ground (for C3 gate and lesson wording)

- "(deleted)" suffix on a removed cwd: not in S064's page. Any lane claim that a deleted cwd reads back with a suffix needs a fixture observation, not S064.
- Process age: S065 grounds the unit (clock ticks) and the sysconf divisor only. The boot-time base (`btime` in /proc/stat) is in proc(5), not opened here; a new row is needed before the census states an absolute start time.
- argv content: neither page describes /proc/pid/cmdline; the redaction and path-match in `souji-proc-census.sh` need a separate row (proc(5) cmdline section) if it is cited.
- The pages say the fields are "defined in" fs/proc/array.c but do not pin a kernel version for each field; the stat row is tied to the man-pages 6.19 revision only.

## Counting record

- Identified 2 documents (the two named man pages), screened 2, included 2 new rows (S064, S065), excluded 0.
- Stop: the cwd permission gate, the state/ppid/pgrp/starttime/comm/wchan field meanings and the [PT] rule are located; the deleted-cwd display, boot-time base and argv are not in these pages and are routed as open.

## Commands and tools

- `read` of corpus/SOURCES.md (rows S001–S065 registry shape; no writes).
- `read` of https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html.
- `read` of https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html (lines 1–300 of 373; fields 1–44 read, quotes above all located in that span).
- Tools installed or updated: none.
- Writes: this file only.

## Verdict

- S064 row shape and quote: holds (quote located on the served page; limit stated).
- S065 row shape and five quotes: holds (located on the served page; the field (44) region and beyond were not needed).
- "(deleted)" and boot-time base: fails as grounded by these rows; routed as open for fixture or a further row.

## Smallest fix for L1

Append S064 and S065 to the registry after S063 and cite this file as the Gate record in corpus/lessons/round-18.md; add a fixture-observed row (or fixture-only evidence) for the deleted-cwd readlink text before any C3 claim uses it.
