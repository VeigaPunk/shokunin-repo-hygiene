STATUS: DONE — one draft SOURCES row for kill(2) at Linux man-pages 6.19, with a verbatim 21-word located quote, grounded on both the fetched page and the host-installed page at the same revision; provisional id S066 because S064 and S065 are already multiply claimed by sibling wave-1 drafts.

# SrcKill2 — round 18, wave 1 (frontier source for C1: group kill)

Question assigned: open the kill(2) man page, extract that a negative `pid` signals every
process in process group `-pid`, and return one draft SOURCES row plus what it teaches and
what it does not establish. Not landed: this seat writes no registry row (leaf seat);
L1 integrates.

## Access record

- URL fetched: https://man7.org/linux/man-pages/man2/kill.2.html
- Fetched: 2026-10-20T19:56Z, `read` tool with `:raw` (text/html, complete page).
- Served identity: `<title>kill(2) - Linux manual page</title>`; headline
  `kill(2)  System Calls Manual  kill(2)`; no separate "last updated" line.
- Version/date line served (footer): `Linux man-pages 6.19            2026-06-05                        kill(2)`
- Colophon served: "This page was obtained from the tarball man-pages-6.19.tar.gz …
  on 2026-09-09"; "HTML rendering created 2026-09-09".
- Host re-check (same revision): `pacman -Q man-pages` → `man-pages 6.19-1`;
  `/usr/share/man/man2/kill.2.gz` `.TH kill 2 2026-06-05 "Linux man-pages 6.19"`;
  sha256 `908338fcf6a2404d4c37bad36f2e5d63f158b5ebd393fcdf0e5d8e76ee626f5a`;
  man 2.13.1. The installed roff carries the same sentences (line numbers below), so the
  row does not depend on man7.org continuing to serve 6.19 — but the row names that
  revision, because man7.org serves a rolling `latest`.

## Located quote (primary, verbatim)

Anchor: § DESCRIPTION, `pid` less than −1 paragraph. Web HTML and installed roff
`:64-72` (`If` / `.I pid` / `is less than \-1,` / … / `.IR \-pid .`) agree word for word.

> If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid.

Word count, exactly (emphasis markup removed, as in S061/S062):

```
$ printf '%s\n' 'If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid.' | wc -w
21
```

Second located quote (§ RETURN VALUE, roff `:96-99`), used below for the reap hazard:

> If signals were sent to a process group, success means that at least one signal was delivered.

```
$ printf '%s\n' 'If signals were sent to a process group, success means that at least one signal was delivered.' | wc -w
17
```

## What it teaches for souji r18 (C1)

1. The watchdog's kill step is exactly `kill(-pgid, SIGTERM)` then `kill(-pgid, SIGKILL)`:
   the negative-`pid` form is the documented address for the whole group, so the fix does
   not need to walk the process tree. This is the mechanism the C1 fix contract names.
2. `pid` 0 is the *caller's own* group (same §, roff `:44-50`: "If pid equals 0, then sig is
   sent to every process in the process group of the calling process."). Consequences: the
   watchdog must never pass `0`, and a watchdog forked *inside* the target group is itself
   signalled by the first `kill -TERM -$pgid`. kill(2) grounds the addressing; that the
   default action of SIGTERM terminates the watchdog is signal(7), not this page
   ([INFERENCE] on the design consequence: the contract text does not say where the
   watchdog sits, only that it must not outlive its repo).
3. rc 0 is not proof of reap. "success means that at least one signal was delivered" — a
   group of three where one member is signalled returns success. A watchdog that treats
   the first kill's status as "repo done" can return while git still holds the private
   temp file / stderr pipe. The page also documents the probe that settles it: `sig` 0
   sends nothing but still performs existence checks, "this can be used to check for the
   existence of a process ID or process group ID that the caller is permitted to signal"
   (§ DESCRIPTION, roff `:74-81`).
4. ESRCH is the idempotent branch, not an error: `ESRCH` — "The target process or process
   group does not exist" (roff `:112-113`). A repo that exited between arming and firing
   yields ESRCH, which the watchdog must read as "already gone".
5. EPERM is *not* "gone": it means "does not have permission to send the signal to any of
   the target processes" (roff `:115-119`), i.e. the group exists. A `sig` 0 probe must
   treat rc 0 as exists, EPERM as exists-but-forbidden, and only ESRCH as empty.
6. § BUGS (`:168-180`) records the historical partial case: `kill()` returned EPERM when
   the caller lacked permission for *some* members while the signal "was still delivered
   to all of the processes for which the caller had permission". rc −1 must never be read
   as "nothing was signalled".
7. Permission model (`:83-92`): `CAP_KILL` in the target's user namespace, or sender real
   or effective uid equal to target real or saved set-uid. In the lane the watchdog and
   git share uid, so the group kill is permitted; a group containing a differently-owned
   child would be only partially signalled.

## What it does NOT establish

- **Group membership.** A process that calls `setsid()`/`setpgid()` leaves the group and
  `kill(-pgid)` misses it. This page never says a process *is* in the group, only that the
  signal goes to the group. That bash `set -m` puts the forked job in its own process group
  is bash(1) § JOB CONTROL (`/usr/share/man/man1/bash.1.gz` has 16 lines matching
  "process group"), not kill(2). Unopened lead below.
- **Delivery under blocked or ignored signals.** SIGTERM can be blocked or caught;
  kill(2) performs no delivery guarantee. That is signal(7)/signal(2).
- **Uninterruptible sleep.** Whether SIGKILL terminates a task in D state is not stated
  here; signal(7) documents the deferral. The r15/r17 leaks were FIFO `open(2)` waiters
  (interruptible, S), so this does not block the fix, but the row must not be cited as
  "SIGKILL always kills".
- **SIGKILL's own semantics.** Uncatchable/uncatchable, default action: signal(7). kill(2)
  only says the signal is sent.
- **Reaping / zombies.** A killed child remains a zombie until `wait(2)`; kill(2)'s ESRCH
  note even warns an existing process may be a zombie. The C1 evidence must therefore be
  "0 processes blocked in the fixture dir" from `ps`/`/proc`, not "kill returned 0".
- **Numeric-pgid reuse.** A pgid can be recycled once the leader dies; kill(2) does not
  discuss it, and its § SEE ALSO (`:181-184`) offers `pidfd_send_signal(2)` as the
  race-free alternative. The 600 s default bound widens that window. This row must not be
  read as making a bare-numeric group kill race-free; the contract does not require pidfd,
  but the gap is real.
- **Shell builtin parsing.** That `kill -TERM -$pgid` or `kill -- -$pgid` in bash reaches
  `kill(-pgid, sig)` is kill(1)/bash(1); the syscall page says nothing about argument
  parsing. The census watchdog is bash, so whichever form the executor uses needs the
  builtin's own evidence (or an executed fixture arm).
- **C1's row and stderr shapes** (`<repo>\t0\t0\t0\t0\t\terror`,
  `souji-census: repo-timeout <N>s <repo>`) are souji's contract, not sourced here.
- **That the timed-out repo's git children share the group** — that is the `set -m` fork
  and the git-shim fixture's evidence, not this page.

## Draft SOURCES row (paste-ready; provisional id)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S066 | kill(2) — https://man7.org/linux/man-pages/man2/kill.2.html | docs | A | negative-pid delivery to the process group whose ID is -pid, the sig 0 existence probe, group-success return and ESRCH; not set -m group creation, blocked or ignored signals, uninterruptible sleep, reaping, or numeric-pgid reuse | served as Linux man-pages 6.19, page dated 2026-06-05, HTML rendered 2026-09-09 from man-pages-6.19.tar.gz, opened 2026-10-20; § DESCRIPTION pid less than -1 and sig 0; § RETURN VALUE; § ERRORS ESRCH and EPERM; § BUGS; host man-pages 6.19-1 `.TH kill 2 2026-06-05` roff :64-72, :74-81, :96-99, :112-119, :168-180 | kill(-pgid, sig) signals every process in the process group whose ID is pgid; sig 0 sends nothing but still checks that the group exists; group success means at least one delivery and ESRCH means no such group | mined | 2026-10-20 | on-release | — |

Validator-conformance of the row as written (parser in `scripts/sources-census.sh`):
11 columns → NF=13 (E01 ok); kind `docs` (E05 ok); tier `A` (E06 ok); status `mined`
(E07 ok); opened 2026-10-20 is not in the future (E08 ok); `on-release` is a symbolic
cadence (E09 ok); docs at tier A with kind != community (E10 ok); no other row cites this
URL, so neither E04 nor W04 applies.

`used-by` is `—` on purpose: E11 fails when the path does not exist, and
`corpus/lessons/round-18.md` does not exist yet; W03 is only a warning. When the r18
lesson lands, set `used-by` to `corpus/lessons/round-18.md` (the r17 pattern for
S057–S062), then re-run `sources-census.sh validate`.

## Gate bullet (round-17 lesson format)

- **S066** https://man7.org/linux/man-pages/man2/kill.2.html (Linux man-pages 6.19, 2026-06-05; § DESCRIPTION; § RETURN VALUE; installed man-pages 6.19-1 roff :64-72 same wording; SrcKill2): "If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid."

## Candidate mined mistake (one; L1 decides admission)

**Candidate:** "reading the group kill's exit status as proof the census repo is done."
Grounding: § RETURN VALUE says group success means *at least one* signal delivered; §
BUGS shows rc −1 can coexist with actual delivery. A watchdog built on the obvious
`kill -TERM -$pgid || log` pattern therefore reports `error` and moves on while git
processes still hold the private temp file — the exact residue class r15/r17 left behind.
Fix that the same page grounds: after SIGTERM, probe `kill(-pgid, 0)`; only ESRCH means
empty; EPERM means "exists but not ours"; after the 2 s SIGKILL, re-probe. Label: candidate
from a source, not a claim that a landed souji revision did it.

## Id collision (must be resolved by L1 before pasting)

Sibling wave-1 drafts already use S064 and S065, several for different sources:

| id claimed | drafting file | source in that draft |
|---|---|---|
| S064 | `ScribeRowsPy.md` | Python subprocess docs |
| S064 | `SrcProcStat.md` | proc_pid_stat(5) |
| S064 | `ScribeRowsProc.md` | proc(5) /proc/pid/cwd |
| S064 | `SrcFifoOpenNonblock.md` | open(2) |
| S064 | `ScribeRowsGit.md` | git/git attr.c at v2.56.0 |
| S065 | `ScribeRowsProc.md` | proc(5) /proc/pid/stat |
| S065 | `ScribeRowsGit.md` | git-cat-file(1) |

`grep -ohE 'S0[6-9][0-9]' .ufo/waves/round-18/w1/*.md | sort -u` → `S062 S063 S064 S065`
only; S066 is the first unclaimed id, hence the provisional id above. If L1 renumbers,
this row's id is the only cell that changes; its Gate bullet, anchor and quote do not
depend on the number. Do not paste two rows with the same id — the validator reports E03.

## Commands run (all read-only; no lane file edited)

```
read https://man7.org/linux/man-pages/man2/kill.2.html (raw)      -> complete page, footer "Linux man-pages 6.19  2026-06-05"
printf … | wc -w                                                 -> 21  (primary quote)
printf … | wc -w                                                 -> 17  (RETURN VALUE quote)
printf … | wc -w                                                 -> 19  (pid 0 sentence, not used as a quote)
pacman -Q man-pages                                              -> man-pages 6.19-1
ls -l /usr/share/man/man2/kill.2.gz                              -> -rw-r--r-- 1976 Aug 27 11:12
zcat …/kill.2.gz | grep -n 'less than -1\|at least one signal'   -> 71:the process group whose ID is / 99:success means that at least one signal was delivered.
zcat …/kill.2.gz | nl -ba | sed -n '60,74p;94,100p;168,181p'     -> roff :64-72, :96-99, :168-180 as cited
zcat …/kill.2.gz | grep -n 'equals 0\|CAP_KILL\|pidfd'           -> 45:equals 0, / 85:CAP_KILL / 183:pidfd_send_signal(2)
sha256sum …/kill.2.gz                                            -> 908338fcf6a2404d4c37bad36f2e5d63f158b5ebd393fcdf0e5d8e76ee626f5a
grep -n 'kill\|pgid\|set -m\|timeout' tools/souji-census.sh      -> no kill/pgid/set -m usage at b576341 (only mktemp at :1510, :1613)
sed -n '1394,1416p' tools/souji-census.sh                        -> emit_census runs `census_one "$repo"` inline, no bound
bash: grep of corpus/SOURCES.md                                  -> 63 registry rows, no kill(2)/killpg row, S064+ absent
```

## Verdict and smallest fix

**Verdict: holds.** The claimed fact — a negative `pid` signals every process in process
group `-pid` — is stated verbatim by man-pages 6.19 on the web page and in the installed
page at the same `.TH` revision, with the 21-word quote inside the 25-word cap; the
operational corollaries (pid 0 = caller's group, `sig` 0 probe, group success = partial,
ESRCH = empty) are all in the same page, and the gaps are named above rather than papered
over.

**Smallest fix:** paste the S066 row into `## Registry` after S063 with a unique id
(L1 renumbers S064/S065 across the sibling drafts first), add the Gate bullet, and set
`used-by` to `corpus/lessons/round-18.md` only after that file exists. Then
`sources-census.sh validate` should show the row clean (W03 until used-by is set).

## Leads (unopened, for the next frontier step)

- bash(1) § JOB CONTROL / `set -m` — grounds that the forked census job gets its own
  process group, the missing premise for `kill(-pgid)` from the parent watchdog.
- signal(7) — blocked/ignored SIGTERM, default dispositions, uninterruptible sleep,
  SIGKILL semantics.
- wait(2) — zombie/reap, for the "0 blocked processes" counting statement.
- pidfd_send_signal(2) — race-free group targeting against pgid reuse (kill(2) SEE ALSO).
- kill(1) — shell/builtin negative-PID argument parsing (`kill -- -PGID`), if the
  executor's watchdog uses the builtin rather than a direct syscall.

## Tool installs / updates

None. All checks were reads, `pacman -Q` (query, not a transaction), `zcat`, `grep`,
`sha256sum`, `wc`, and one `sed` line-range read.
