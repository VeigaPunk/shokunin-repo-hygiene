STATUS: DONE — one draft SOURCES row (provisional S066, id collision noted) with a 9-word located quote from os.killpg plus a six-sentence extraction of run()/communicate()/start_new_session() semantics; C1's group-kill API is grounded, descendant containment is not.

# SrcPySubprocess — round 18, wave 1 (C1 source item, operability)

Axes named: calibration (quote cap, served version, locate-before-paraphrase), operability (C1 fixture/watchdog API grounding), coverage (one new registry row, non-overlapping with the sibling S064). No repo or clone writes; this report only.

## 1. Access record (exact URLs, access date, served version/last-updated line)

| URL fetched | served as | version / last-updated line served | access |
|---|---|---|---|
| https://docs.python.org/3/library/subprocess.html | `subprocess — Subprocess management — Python 3.15.0 documentation` (canonical `meta-og:url` is the same URL) | footer: `Last updated on Oct 20, 2026 (19:47 UTC).` | 2026-10-20 |
| https://docs.python.org/3/library/os.html | `os — Miscellaneous operating system interfaces — Python 3.15.0 documentation` | footer: `Last updated on Oct 20, 2026 (19:47 UTC).` | 2026-10-20 |
| https://docs.python.org/3.14/library/subprocess.html | Python 3.14 documentation (no `<title>` line captured; page body) | footer: `Last updated on Oct 20, 2026 (19:51 UTC).` | 2026-10-20 |
| https://docs.python.org/3.14/library/os.html | Python 3.14 documentation | footer: `Last updated on Oct 20, 2026 (19:51 UTC).` | 2026-10-20 |

Host interpreter: `python3 --version` → `Python 3.14.8`. The `/3/` pages serve 3.15.0; every line number below is therefore from `/3.14/`, the version the host interpreter implements. The `/3/` rendering was read directly and carries the same wording for the run, communicate, kill, start_new_session and killpg sentences; its line numbers differ (e.g. communicate's "not killed" sentence sits at `/3/` :741-743 vs `/3.14/` :726-728), so this report does not cite `/3/` line numbers.

Correction for L1: the sibling `ScribeRowsPy.md` records "no last-updated line in the served text" for `/3/library/subprocess.html`. That is not what the page served on 2026-10-20: the footer line `Last updated on Oct 20, 2026 (19:47 UTC).` is present. Its quote text is unaffected; the access-record cell is the part to correct.

## 2. Extraction — what each call does on expiry, and what start_new_session / killpg do

Convention: quotes are verbatim from the served pages with markup removed (the pages carry `*timeout*`, `sig`, `` `setsid()` `` emphasis); words are counted with `wc -w` on the de-marked string, not by eye. Locations are `/3.14/` ranges.

| # | fact | verbatim quote | words | location | ≤25 for a row quote |
|---|---|---|---|---|---|
| 1 | `run(timeout=)` on expiry kills the child and waits | `If the timeout expires, the child process will be killed and waited for.` | 13 | subprocess § subprocess.run timeout paragraph :69-70 | yes |
| 2 | `run(timeout=)` raises only after the child terminated | `The TimeoutExpired exception will be re-raised after the child process has terminated.` | 12 | :70-71 | yes |
| 3 | process creation is not interruptible, so the deadline is soft at the start | `The initial process creation itself cannot be interrupted on many platform APIs so you are not guaranteed to see a timeout exception until at least after however long process creation takes.` | 31 | :71-74 | no — over cap, extraction only |
| 4 | `communicate()` reads until pipe EOF | `Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.` | 17 | § Popen.communicate :708-709 | yes |
| 5 | `communicate(timeout=)` raises `TimeoutExpired` | `If the process does not terminate after timeout seconds, a TimeoutExpired exception will be raised.` | 15 | :721-722 | yes |
| 6 | `communicate(timeout=)` does NOT kill the child | full sentence `The child process is not killed if the timeout expires, so in order to cleanup properly a well-behaved application should kill the child process and finish communication:` | 27 | :726-728 | no — over cap; fragment `The child process is not killed if the timeout expires` is 10 words and is not a complete sentence (do not land it as a whole-sentence quotation) |
| 7 | after a timeout, do not `wait()` | `After a call to communicate() raises TimeoutExpired, do not call wait().` | 11 | :739-740 | yes |
| 8 | `wait()` with pipes can deadlock | Note under `Popen.wait`: `This will deadlock when using stdout=PIPE or stderr=PIPE and the child process generates enough output to a pipe such that it blocks waiting for the OS pipe buffer to accept more data.` | 32 | § Popen.wait, `Note` marker :692 | no — over cap, extraction only |
| 9 | `start_new_session=True` calls `setsid()` in the child before exec, POSIX only | `If start_new_session is true the setsid() system call will be made in the child process prior to the execution of the subprocess.` | 22 | § Popen Constructor :507-508; `Availability: POSIX` :510; `Changed in version 3.2: start_new_session was added.` :512 | yes |
| 10 | `process_group=N` calls `setpgid(0, N)` in the child instead, POSIX only | `If process_group is a non-negative integer, the setpgid(0, value) system call will be made in the child process prior to the execution of the subprocess.` | 25 (exactly at cap) | :514-516 | yes, but the page does not define what `value` 0 means |
| 11 | `kill()` is SIGKILL, addressed to the child | `Kills the child. On POSIX OSs the function sends SIGKILL to the child.` | 13 | § Popen.kill :768 | yes |
| 12 | `killpg` signals a process group | `Send the signal sig to the process group pgid.` | 9 | os § os.killpg :4204 (definition :4202); `Availability: Unix, not WASI, not iOS.` :4208 | yes |
| 13 | the same page does not define `setsid()` semantics | `Call the system call setsid(). See the Unix manual for the semantics.` | 12 | os § os.setsid :637-639 | yes (negative anchor) |

What this means in one sentence per call, as the page states it:
- `run(timeout=)` — the timeout is passed to `communicate()`; on expiry "the child process will be killed and waited for", and `TimeoutExpired` is re-raised after termination (#1, #2); the deadline cannot interrupt process creation (#3). The page's `kill()` method is SIGKILL addressed "to the child" (#11); nothing on the page extends "killed" to the child's own children.
- `communicate(timeout=)` — raises `TimeoutExpired` and, in so many words, does NOT kill the child (#5, #6); the page's own repair recipe is `proc.kill()` followed by a second `communicate()`, and it says not to call `wait()` after the exception (#7). It also reads stdout and stderr "until end-of-file is reached" (#4) — an EOF on the pipe, not the child's exit, is what completes the read.
- `start_new_session=True` — `setsid()` in the child before exec, POSIX (#9). `process_group=N` — `setpgid(0, N)` in the child, POSIX (#10).
- `os.killpg(pgid, sig)` — "Send the signal sig to the process group pgid", Unix only (#12).

## 3. Draft SOURCES row (header shown for reference; only the S066 line is new)

Id note: at the time of writing, the w1 reports already claim `S064` twice (`ScribeRowsPy.md` for this same subprocess page; `ScribeRowsProc.md` for proc_pid_cwd) and `S065` once (`ScribeRowsProc.md`); `S066` is unclaimed in all five w1 reports (`grep -ho 'S0[6-9][0-9]' …` → only S062/S063/S064/S065). This row is therefore **provisional S066**; L1 sequences the final ids. It is deliberately *not* a duplicate of ScribeRowsPy's S064: that row's quote is `start_new_session` and its scope excludes group-kill semantics; this row's quote is `os.killpg` and its scope excludes `setsid` semantics. Two rows on one URL with different scopes is the established pattern (S036/S049 on git(1); S045/S059 on gitattributes(5); S042/S057 on git-config(1)). If L1 prefers one merged subprocess row, the merge quote should be #1 (`run` timeout, 13 words) and both scope exclusions must be kept; I do not recommend merging, because it would detach the `killpg` quote from the row that teaches group signalling.

```
| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S066 | Python os.killpg documentation, with the subprocess timeout anchors as companion — https://docs.python.org/3/library/os.html#os.killpg, https://docs.python.org/3/library/subprocess.html | docs | A | process-group signal delivery and the child-scoped wording of subprocess timeout kills; not setsid or process-group-leadership semantics (S064), not descendant survival, not signal delivery to a task blocked in open(2) | Python 3.14.0 documentation served at /3.14/ on 2026-10-20, footer "Last updated on Oct 20, 2026 (19:51 UTC)", host python3 3.14.8; /3/ serves 3.15.0 (footer 19:47 UTC) with the same wording; os.html § os.killpg :4202-4208; subprocess.html § subprocess.run timeout paragraph :69-74, § Popen.communicate :708-709 and :721-722, § Popen.kill :768; § os.setsid :637-639 as the negative anchor | killpg sends sig to a whole process group, Unix only; run(timeout=) kills and waits for "the child" and kill() is SIGKILL "to the child", neither sentence reaching the child's group; communicate() reads both streams until end-of-file is reached; after TimeoutExpired the page says do not call wait() | mined | 2026-10-20 | on-release | — |
```

Row quote, verbatim, with count: `Send the signal sig to the process group pgid.` — **9 words** (`printf … | wc -w` → 9). Located at os § os.killpg, `/3.14/library/os.html:4204`, same sentence served at `/3/library/os.html` (read on 2026-10-20); the quote is one complete sentence and needs no ellipsis. `used-by` is left `—` because `corpus/lessons/round-18.md` does not exist yet (`ls` → No such file); L1 adds it when the lesson lands.

## 4. What it teaches for souji r18 (C1 wording that is now citable)

1. **The fixture protocol is composed of two documented primitives.** `start_new_session=True` (#9) plus `os.killpg(child.pid, SIGKILL)` (#12): the pages document each call, not this combination, so the C1 sentence "every census subprocess runs with `start_new_session=True` and on timeout `os.killpg(..., SIGKILL)`" may cite this row for the API meaning of both calls but not for the claim that the named group contains the blocked process (gap 2 below).
2. **`run(timeout=)` is not a containment primitive.** Its documented effect is "the child process will be killed" (#1, #11). The page never extends that to a group or to descendants. C1 must not cite `run(timeout=)` as the reason a red arm leaves nothing behind; the fixture's own `killpg` is the reason, and the "0 blocked processes" acceptance must remain a measured count.
3. **`communicate(timeout=)` is worse than `run(timeout=)` for cleanup.** It documents that the child is *not* killed (#6). A fixture (or a helper) that catches `TimeoutExpired` and returns has signalled nothing at all; the page's own recipe is an explicit `kill()` (#6) and then a second `communicate()` rather than `wait()` (#7).
4. **The pipe clause in the C1 contract has a documented mechanism.** `communicate()` completes on pipe EOF, not on child exit (#4). A process that still holds the write end keeps the read from returning **[INFERENCE — the page states the EOF completion condition, not this consequence]**; that is the source-level reason a supervisor must not inherit or hand on the caller's stdout/stderr, and why the C1 wording "holds no stdout/stderr pipe of the caller" is the right constraint rather than a stylistic one. The converse use: redirect the child's output to a private temp file (as the C1 contract already specifies) instead of `PIPE`, which also sidesteps the `wait()`-with-PIPE deadlock note (#8).
5. **Deadline honesty.** The deadline cannot interrupt process creation (#3), so a watchdog's "after the bound" is measured from after the fork returns, not from the caller's request **[INFERENCE — the page guarantees only that the exception arrives after process creation takes its time]**. This matters for the `--repo-timeout`/`SOUJI_CENSUS_REPO_TIMEOUT` bound wording and for the 2 s SIGTERM→SIGKILL escalation: the bound bounds the child's run, not the parent's start.
6. **Calibration for C2.** The load-bearing sentences are short and scope-limited ("the child", "until end-of-file", "a process group"); the row's `teaches` cell therefore states them as written and carries the exclusions in `scope`. No paraphrase gains a reach the sentences do not have.

## 5. What it does NOT establish (unresolved gaps, for the r18 lesson and for later rows)

1. **Descendant survival.** Neither page says what happens to the killed child's own children. That `run(timeout=)`'s SIGKILL leaves a grandchild running (the FIFO-blocked `git` class) is **[INFERENCE]** from SIGKILL being addressed "to the child" plus the OS process model; it is not a documented claim. Do not write it into a lesson as source-backed.
2. **`setsid()` ⇒ process-group leader.** `os.setsid()` on the same page is a one-liner that defers to the Unix manual (#13). Nothing on these pages says the child's pgid equals its pid, so `os.killpg(child.pid, …)` is **not grounded by this row**. A `setsid(2)`/POSIX row is required before C1 claims that the group named by `child.pid` is the child's group. (S062 covers blocking FIFO open only.)
3. **`process_group=0`.** The page documents that `setpgid(0, value)` is called (#10) but not what `value` 0 means; do not state "pgid = child pid" from this source. If the fixture wants the bash `set -m` shape (a new group, no new session), this is the parameter — but its semantics need `setpgid(2)`.
4. **Signals versus a blocked `open(2)`.** Nothing here says SIGKILL (or SIGTERM) terminates a task blocked opening a FIFO; `fifo(7)` (S062) says the open blocks and does not say a signal ends it. "killpg unblocks the FIFO-blocked git" is unproven by S062 + S066 and needs fixture measurement or a `signal(7)`/`open(2)` row. This is the sharpest remaining gap for C1's acceptance.
5. **Grace-period sufficiency.** Nothing here supports the 2 s SIGTERM→SIGKILL interval, signal-handler behaviour, or that a group dies as a unit; those are policy, to be measured.
6. **bash job control.** Nothing here grounds `set -m`, job-control process groups, or bash's own signalling; the C1 bash watchdog (`emit_census`) needs bash(1) evidence, not this row.
7. **Reaping and pgid reuse.** No statement about zombies, `waitpid`, or the race in signalling a pgid after the child exits; the contract's "watchdog never outlives its repo" is not derivable here.
8. **Host applicability of the Python side.** `subprocess`/`os.killpg` availability is asserted for the documented platforms (#9 POSIX, #12 Unix-not-WASI-not-iOS) and the host is Python 3.14.8 on Linux; the pages do not assert this host's kernel behaviour, only the API.

## 6. Mined mistake (one, per the frontier step)

**"A timeout at the Python layer means the subtree is dead."** The pages explicitly contradict the two readings behind it: `communicate(timeout=)` "is not killed" (#6), and `run(timeout=)`'s kill is `SIGKILL` "to the child" (#1, #11) — neither sentence reaches the group the child created. A supervisor that treats `TimeoutExpired` as cleanup therefore leaves exactly the residue class the lane is closing (a process blocked in a path that no longer exists). Attribution note: I did **not** open the r15 `r-inc-fifo`/r17 `d2-fifo` fixture scripts (doing so would need a recursive search over `tests/`, which the probe rule forbids), so "the fixtures used `run`/`communicate`" is **not verified**; the mistake is mined from the documentation's wording, and the fixture attribution is left open.

## 7. Commands run (exact) and outputs

- `read https://docs.python.org/3/library/subprocess.html` (whole-page fetch, lines 1-300, :301-700, :700-820, :1430-1460) — served 3.15.0; captured run()/communicate()/kill()/start_new_session() text and the footer `Last updated on Oct 20, 2026 (19:47 UTC).`
- `read https://docs.python.org/3/library/os.html` (:1-60, :4560-4615, :5670-5700) — served 3.15.0; captured `os.kill(pid, sig)`, `os.killpg(pgid, sig)` "Send the signal *sig* to the process group *pgid*." and `Availability: Unix, not WASI, not iOS.`; footer `Last updated on Oct 20, 2026 (19:47 UTC).`
- `grep 'killpg|kill process group' https://docs.python.org/3/library/os.html` → match at line 4600-4606.
- `grep 'start_new_session is true|setsid\(\)|killed and waited for' https://docs.python.org/3.14/library/subprocess.html` → :69-70 run sentence, :71-72 creation sentence, :507-508 start_new_session, :466 `process_group` cross-reference.
- `grep 'sends SIGKILL to the|Interact with process|until end-of-file is reached|do not call' …/3.14/…/subprocess.html` → :708-709, :768.
- `grep 'does not terminate after|after a call to|After a call to' …/3.14/…/subprocess.html` → :689 wait, :721 communicate, :739-740 do-not-wait.
- `grep 'Added in version 3\.2: .start_new_session|Changed in version 3\.3: .timeout. was added' …/3.14/…/subprocess.html` → matched only the second alternative (`Changed in version 3.3: *timeout* was added.` at :704, :747); the first alternative did not match because the page wording is `Changed in version 3.2: *start_new_session* was added.`, found at :512 by the `start_new_session` sweep.
- `grep 'os\.setsid|Call the system call setsid' …/3.14/…/os.html` → :637-639.
- `grep 'Send the signal sig to the process group pgid|os.killpg' https://docs.python.org/3.14/library/os.html` → :4202-4208.
- `read …/3.14/…/subprocess.html:66-80` and `:686-700` → paragraph spans quoted above (run :69-74; wait `Note` at :692).
- `read …/3.14/…/subprocess.html:1435-1465` and `…/3.14/…/os.html:5280-5294` → footer `Last updated on Oct 20, 2026 (19:51 UTC).`
- `python3 --version` → `Python 3.14.8`.
- `printf '%s\n' '<quote>' | wc -w` for each extraction row. First run (start_new_session, run sentence, full communicate sentence, killpg) → `22`, `13`, `27`, `9`. Second run (communicate EOF, communicate raise, TimeoutExpired re-raised, do-not-wait, kill, process_group, os.setsid, run creation sentence) → `17`, `15`, `12`, `11`, `13`, `25`, `12`, `31`. Third run (wait deadlock sentence, #8) → `32`.
- `grep 'Added in version 3\.2: .start_new_session|Changed in version 3\.3: .timeout. was added' …/3.14/…/subprocess.html` → matched only the second alternative (`Changed in version 3.3: *timeout* was added.` at :704, :747); the first alternative did not match because the page wording is `Changed in version 3.2: *start_new_session* was added.`, found at :512 by the `start_new_session` sweep.
- `grep -ho 'S0[6-9][0-9]' ScribeRowsGit.md ScribeRowsPy.md ScribeRowsProc.md ScribeLessonDraft.md ScribeProvinceProc.md | sort | uniq -c` in `.ufo/waves/round-18/w1/` → `2 S062`, `4 S063`, `23 S064`, `19 S065`.
- `ls corpus/lessons/round-18.md` → No such file or directory.
- No `git`, no `jj`, no lane/fleet writes; no tool installs or updates.

Caveat on line numbers: the numbers cited are the ones `grep` reported for the `/3.14/` URLs and are reproducible with the same patterns. `/3/` line numbers are not cited because the two renderings differ (the `/3/` page is longer before the communicate section).

## 8. Verdict and smallest fix

- **Extraction: holds.** All four behaviours asked for are located verbatim, word-counted, and scoped: `run(timeout=)` kills and waits for the child (#1, #2), `communicate(timeout=)` raises without killing (#5, #6), `start_new_session=True` calls `setsid()` POSIX-only (#9), `os.killpg` signals a process group Unix-only (#12); the pipe/EOF and do-not-`wait()` clauses are also located (#4, #7, #8).
- **Row: holds as a complement, not as a duplicate.** The quote is 9 words and verified on both served versions; id must be sequenced by L1 (S064 double-claimed, S065 claimed, S066 free at scan time).
- **C1's "0 blocked processes" claim: fails if rested on this source alone.** The source grounds the API, not that a group kill reaches the FIFO-blocked `git`, and not that the blocked `open(2)` is interruptible (gaps 1, 2, 4). Smallest fix: land a `setsid(2)` row (group-leadership is the missing link between `child.pid` and `pgid`) and keep the residue claim tied to a measured fixture arm; the lesson must say "signals the group it created" and cite the measurement, not the doc, for the count.
- **Smallest fix for L1 on this file:** paste the S066 body line after S065 (renumber if the S064 collision resolves against it), add `corpus/lessons/round-18.md` to `used-by` when the lesson lands, and correct `ScribeRowsPy.md`'s access record to record the served footer `Last updated on Oct 20, 2026 (19:47 UTC)`.
