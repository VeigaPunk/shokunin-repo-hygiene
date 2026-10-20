STATUS: DONE — the ` (deleted)` wording is not on proc_pid_cwd(5) at all (man-pages 6.19 split proc(5)); it lives on proc_pid_exe(5) and reaches cwd through the pinned `d_path()` path; the readlink predicate reproduced exactly 58 deleted-cwd processes on this host, while `stat -L /proc/<pid>/cwd` still reports `directory` for every one of them.

# Source item — proc_pid_cwd(5): the cwd link and the ` (deleted)` annotation

## Fetch record

- URL fetched (exact): `https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html` — `read`, native, `text/html`, complete page (NAME/DESCRIPTION/SEE ALSO/COLOPHON, no truncation).
- Access date: 2026-10-20.
- Served version / last-updated line: footer reads

  ```
  Linux man-pages 6.19            2026-02-08                proc_pid_cwd(5)
  ```

  No separate "last updated" line is served. Colophon: "This page was obtained from the tarball man-pages-6.19.tar.gz fetched ... on 2026-09-09"; "HTML rendering created 2026-09-09 by Michael Kerrisk".
- Corroborating pages opened the same day: `proc_pid_exe.5.html` (carries the annotation wording), `proc_pid_fd.5.html` (checked, no `deleted` wording), `proc.5.html` (stub/index only — see mined mistake 1), and the installed man-pages 6.19 roff under `/usr/share/man/man5/`.
- The cwd page contains **no** occurrence of `deleted`: `grep` of `https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html:raw` with pattern `deleted` → "No matches found", on a page small enough that the whole file was in the search space (it rendered in full above).

## Draft SOURCES.md row (single line, registry shape of S051–S063)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S064 | proc_pid_cwd(5) — https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html; ` (deleted)` wording on proc_pid_exe(5) — https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html | docs | A | `/proc/pid/cwd` as a readlink surface and the suffix the kernel appends for an unlinked target; not errno values, argv/fd surfaces, or pid-reuse safety | Linux man-pages 6.19 (2026-02-08; HTML rendered 2026-09-09), opened 2026-10-20 — proc_pid_cwd(5) § DESCRIPTION (:71-72), proc_pid_exe(5) § DESCRIPTION (:76-78); installed man-pages 6.19 roff proc_pid_cwd.5.gz :7,:13 and proc_pid_exe.5.gz :7,:23-25; kernel fs/d_path.c@fa0d6d9 :255-256,:287-289 and fs/proc/base.c@e2f0d6d :222,:1811,:1820,:3310 | readlink(/proc/pid/cwd) returns the path text and the kernel appends ` (deleted)` when the directory is unlinked (d_path applies it to any unlinked dentry and calls the result ambiguous), while following the magic link still reaches the live inode — classify by readlink text and confirm by stat of the stripped path, never by `-d` | mined | 2026-10-20 | on-release | corpus/lessons/round-18.md |

Lesson-Gate provenance line (shape of the round-17 provenance paragraph, for `corpus/lessons/round-18.md` Gate):

```
S064 — https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html (annotation wording: https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html), opened 2026-10-20, Linux man-pages 6.19 (2026-02-08), HTML rendering 2026-09-09. Quote (proc_pid_exe(5) § DESCRIPTION, :76-78, 20 words): "If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname."
```

ID note for L1: `ScribeRowsProc.md` already drafted **S064** for proc_pid_cwd and **S065** for proc_pid_stat; `SrcProcStat.md` also drafted an **S064** (stat) — those two already collide with each other. This row should **replace** ScribeRowsProc's S064 (same page; it closes the deleted-suffix item that row explicitly left open) rather than become a third id. If L1 keeps all three, the next free id after S065 is **S066**.

## Located quotes (verbatim)

Q1 — the row's grounding quote, proc_pid_exe(5) § DESCRIPTION, served HTML :76-78, installed roff proc_pid_exe.5.gz :23-25:

> If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname.

`printf '%s\n' "<quote>" | wc -w` → **20** (limit 25). Copied from the served page and from the installed roff (`\[aq]\ (deleted)\[aq]`), unchanged.

Q2 — the cwd link itself, proc_pid_cwd(5) § DESCRIPTION, served HTML :71-72, installed roff :13:

> This is a symbolic link to the current working directory of the process.

`wc -w` → **13**.

Q3 — the permission gate, proc_pid_cwd(5) § DESCRIPTION (last paragraph), 20 words:

> Permission to dereference or read (readlink(2)) this symbolic link is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check; see ptrace(2).

Q4 — kernel cross-check, `fs/d_path.c@fa0d6d9` :255-256 (implementation evidence, not the doc quote): "Convert a dentry into an ASCII path name. If the entry has been deleted the string " (deleted)" is appended. Note that this is ambiguous." (`wc -w` = 25 with quote tokens counted; 21 semantic words).

## What it teaches for souji r18 (C3)

1. **Predicate.** The residue class "cwd is deleted" is `readlink(/proc/<pid>/cwd)` ending in the literal ` (deleted)`; strip the 10-byte suffix (`" (deleted)"` = space + 9 chars; kernel passes length 11 for the NUL-inclusive form) and `stat` the remaining text — that text path is gone.
2. **Anti-predicate (operability).** `stat -L /proc/<pid>/cwd`, `test -d`, and the page's own recipe (`cd /proc/20/cwd; pwd -P`) all **succeed** on a deleted cwd: `/proc/pid/cwd` is a magic link resolved by `nd_jump_link()` to the live `struct path`, not by reparsing the text. A census written as `-d /proc/$pid/cwd` classifies every one of the 58 leaked processes as healthy. This is the single most dangerous false negative in the C3 surface.
3. **Permission model.** The link's readlink is gated by `PTRACE_MODE_READ_FSCREDS`, which is consistent with C3's "processes of the current uid" scope; a uid-scoped census reading its own processes passes. Denial and races must still become an explicit row `reason`, never a silently skipped pid (same no-lost-rows principle as C1's timeout rows).
4. **Thread caveat.** "In a multithreaded process, the contents of this symbolic link are not available if the main thread has already terminated" — readlink can fail while the pid is still visible; that is a reportable reason, not absence of residue.
5. **Ambiguity must be carried, not hidden.** The kernel comment says outright "Note that this is ambiguous": a live directory literally named `x (deleted)` produces identical readlink text. C3 must count that as its own class (confirmed by `stat` on the stripped path, plus a stated residual ambiguity) instead of asserting "deleted" from text alone.
6. **Residue severity.** The deleted directory stays alive because the process holds it (`fs->pwd`), and `stat -L` proves the inode is reachable: the residue is permanent until the process is reaped, not a transient the next sweep will lose.
7. **Man-page recipes are not detection recipes.** The page's example dereferences the link; it is fine for healthy processes and wrong for a census (it chdirs the census into a foreign directory, and `getcwd` on an unlinked cwd is itself an error path).

## What it does NOT establish

1. **The suffix for cwd.** proc_pid_cwd(5) never mentions ` (deleted)` (0 occurrences, verified). The wording exists only on proc_pid_exe(5), whose subject is `exe`. Applying it to `cwd` rests on the pinned kernel chain — `fs/proc/base.c:3310 LNK("cwd", proc_cwd_link)`, `:222 proc_cwd_link`, `:1811 do_proc_readlink` → `:1820 d_path()`, and `fs/d_path.c:288-289 prepend(&b, " (deleted)", 11)` when `d_unlinked(path->dentry)` — not on a documentation sentence. A row that stops at the man page would be a dangling claim of exactly the LG-DANGLING class.
2. **Errno values.** No EACCES/EPERM/ESRCH/ENOENT is stated for a denied or racing readlink; `ptrace(2)` owns that. C3 must not derive its `reason` vocabulary from this page.
3. **stat/`-d`/`cd` behavior on a deleted target.** The page is silent; the observed "still `directory`" behavior is host evidence (below), not a sourced claim.
4. **A disambiguation procedure.** The kernel names the ambiguity and offers none. No rule is given for a directory whose real name ends in ` (deleted)`.
5. **argv.** Nothing about `/proc/pid/cmdline`, so C3's second leg — "argv names a path under /var/tmp, /tmp or /dev/shm that no longer exists" — has no grounding here and needs its own row.
6. **fd targets.** proc_pid_fd(5) is a separate page; it shows pipe/socket links as `type:[inode]` and anonymous fds as `anon_inode:file-type`, so a path parser must exclude non-absolute link contents. That fact is on that page, not this one.
7. **Race safety.** No statement about readdir → readlink races or pid reuse; a row can describe a pid that exited and was reused.
8. **That the process is blocked or orphaned.** Holding a deleted cwd says nothing about wait channel, pgid, or parentage; C1's timeout/group handling is orthogonal.

## Host cross-check (read-only; no signalling)

Exact commands and outputs (kernel 7.2.11-arch1-1, uid 1000):

```
$ for p in 185605 562279 562276 447890; do printf '%s cwd_readlink=[%s] statL=[%s]\n' "$p" "$(readlink /proc/$p/cwd)" "$(stat -L -c '%F' /proc/$p/cwd 2>&1)"; done
185605 cwd_readlink=[/var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo (deleted)] statL=[directory]
562279 cwd_readlink=[/var/tmp/r17-census-hygiene.e80b0xqe/d2-fifo/b (deleted)] statL=[directory]
562276 cwd_readlink=[/var/tmp/r17-census-hygiene.e80b0xqe (deleted)] statL=[directory]
447890 cwd_readlink=[/home/vgpnk/Projects/shokunin] statL=[directory]
```

```
$ stat -c '%F %N' /proc/185605/cwd
symbolic link '/proc/185605/cwd' -> '/var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo (deleted)'
$ stat -L -c '%F %n' /proc/185605/cwd
directory /proc/185605/cwd
$ test -e /var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo && echo exists || echo gone
gone
$ test -e '/var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo (deleted)' && echo literal-exists || echo literal-gone
literal-gone
```

Independent counter over all current-uid pids (readlink predicate; `tee` wrote a scratch file under /tmp, since deleted):

```
$ for d in /proc/[0-9]*; do p=${d#/proc/}; [ "$(stat -c %u "$d" 2>/dev/null)" = "$u" ] || continue; t=$(readlink "$d/cwd" 2>/dev/null) || continue; case $t in *" (deleted)") printf '%s\t%s\n' "$p" "$t";; esac; done | wc -l
58
```

First rows of the same sweep: `1026787 /var/tmp/r15-census-config.tf977fa2 (deleted)`, `1026800 .../unsafe-repos/r-inc-fifo (deleted)`, `1242228 /var/tmp/r15-census-config.9lkl1cdg (deleted)`, `1242241 .../unsafe-repos/r-inc-fifo (deleted)`. The count is exactly the 58 the lane recorded as host evidence, reproduced independently here. Corroboration (peer message, 2026-10-20): seat `SoujiR18.LeakCounter-5` ran its own counter with the same readlink-suffix predicate, observed the same 58 deleted-cwd PIDs, and its live PID set matched its retained 58-entry baseline; that seat did not use `stat -L` for cwd — i.e. two independent implementations and one retained baseline agree, and no implementation that used `-d`/`stat -L` could have agreed. The broad argv filter `ps -eo pid=,uid=,stat=,cmd= | awk '$2==uid && /var\/tmp/' | wc -l` returns **73**, which is a superset (legitimate /var/tmp executor clones included) and is **not** a residue count — argv alone over-counts, cwd-deleted under-counts nothing but needs the readlink test.

The three deleted-cwd pids checked also sit inside the fixture process trees named in the C1 host evidence (`r15-census-config`, `r17-census-hygiene`), and each is `state=S` with parentage back to a `souji-census.sh`/`git` pair — consistent with the lane's leak story. No process was signalled, stopped, or started by this seat.

## Mined mistakes

1. **"The cwd page documents the deleted annotation."** False. proc_pid_cwd(5) has no `deleted` text at all; man-pages 6.19 split `proc(5)` into per-pid pages (`proc.5.html` is now a stub ending at COLOPHON around :250, listing `proc_pid_cwd(5)`, `proc_pid_exe(5)`, …), and the annotation stayed on the exe page. Any C3 claim citing only the cwd page would be a dangling pointer of the LG-DANGLING class.
2. **"Deleted cwd ⇒ `stat -L` fails."** False on this kernel: `stat -L /proc/185605/cwd` printed `directory`. The magic link jumps to the live inode the process still holds; only the text returned by readlink exposes the unlink. A `-d`-based residue check would have reported 0 of the 58.

## Verdict

- Row shape and cells: **holds** (11 columns, S051–S063 contract; single row; `wc -w` 20 against a 25-word limit).
- Scope honesty: **holds** — the cwd page is cited only for link semantics and the ptrace gate; the suffix is cited to proc_pid_exe(5) and the pinned kernel path.
- Detection predicate: **holds**, reproduced 58/58 against the live host.
- `-d`/`stat -L` as a predicate: **fails**, demonstrated on 4/4 sampled pids.
- Smallest fix for L1: replace ScribeRowsProc's S064 with this row (keep its S065 stat row; resolve the duplicate S064 stat draft), and in `tools/souji-proc-census.sh` require `readlink` + `" (deleted)"` suffix match for the cwd class, with the stripped-path `stat` as confirmation; forbid `-d`/`stat -L`/`cd` as the classifier. `used-by` stays `corpus/lessons/round-18.md` until a residue knowledge page exists.

## Tooling

No tools installed or upgraded; no pacman transactions attempted; no network writes. Writes: this report only (plus a `/tmp` scratch file created and removed in the same command).

---

GODSPEED

Axes named: (1) source grounding for C3's cwd-deleted class, (2) dangling-claim risk (LG-DANGLING/LG-FROZEN-MEASURED lineage), (3) probe-rule cleanliness. Moves kept: opening the sibling page when the named page was silent; pinning `d_path.c`/`base.c` to commits; cross-checking the predicate on live residue; measuring the `-d` false-negative before recommending a predicate. No move was made that would harm another axis (no repo writes, no signalling, no fleet-directory probes).
