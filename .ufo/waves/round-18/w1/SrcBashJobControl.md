STATUS: DONE — S064 draft row (Bash 5.3 job control) located, quoted verbatim, and grounded to the C1 mechanism; live gnu.org unreachable, Wayback captures opened 2026-10-20.

# SrcBashJobControl — frontier source item (r18 W1)

Seat: `SoujiR18.SrcBashJobControl-5`. Scope: one SOURCES row for "with job control each pipeline/background job runs in its own process group, and what `set -m` enables". Judged axis: operability. No code edits, no lane writes beyond this report.

## 1. Source fetched (exact URLs, access date, served version line)

Live pages were attempted first; both timed out (same failure S043 recorded for this exact host/day):

```
$ curl -sS --max-time 40 -o jc.html -w 'jc:%{http_code} %{size_download}\n' \
    https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html
curl: (28) Connection timed out after 40000 milliseconds
jc:000 0
$ curl -sS --max-time 40 -o set.html -w 'set:%{http_code} %{size_download}\n' \
    https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
curl: (28) Connection timed out after 40001 milliseconds
set:000 0
```

Opened through Wayback instead, access date **2026-10-20** (UTC), capture reads 200:

| role | URL fetched (effective) | capture | sha256 of archived bytes |
|---|---|---|---|
| Job Control Basics | `https://web.archive.org/web/20260803220758/https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html` | 20260803220758 | `fd1d6c6b842713e99d40c1a79138bf706887b931331bea5e0e6166f545504cb7` |
| The Set Builtin | `https://web.archive.org/web/20260930073822/https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html` | 20260930073822 | `39fb870335963552325a4fabb22d00ab68cd48738d76d18690db17646379991b` |

```
$ curl -sSL --max-time 60 -o Job-Control-Basics.wayback.html -w "$n: %{http_code} %{size_download} %{url_effective}\n" \
    https://web.archive.org/web/2026/https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html
Job-Control-Basics: 200 21032 https://web.archive.org/web/20260803220758/https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html
$ ... The-Set-Builtin.html
The-Set-Builtin: 200 19732 https://web.archive.org/web/20260930073822/https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
```

Version/last-updated line served by **both** captures (GNU's HTML head comment, not a visible footer):

> This is Edition 5.3, last updated 18 May 2025, of The GNU Bash Reference Manual, for Bash, Version 5.3.

Confirmed by `tr '\n' ' ' < <file> | grep -o 'This is Edition 5.3, …'` → one hit per file. This is the same Set Builtin capture id S043 used (`20260930073822`), so S064 is consistent with the round-16/17 provenance trail. Host bash is `GNU bash, version 5.3.20(1)-release` (Edition 5.3 series).

## 2. Verbatim quotes (located, ≤25 words, `wc -w` exact)

HTML line wraps were normalized to single spaces; no other change. All six verified present in the archived bytes.

| # | page · section | verbatim quote | words | what it pins |
|---|---|---|---|---|
| Q1 | Set Builtin § 4.3.1, `-m` | "Job control is enabled (see Job Control). All processes run in a separate process group." | **15** | the only sentence stating that monitor mode creates a process group |
| Q2 | Job Control Basics § 7.1 | "The shell associates a job with each pipeline." | **8** | job ≡ pipeline, so Q1's group is a pipeline's group |
| Q3 | Job Control Basics § 7.1 | "All of the processes in a single pipeline are members of the same job." | **14** | every element of the pipeline shares that job/group |
| Q4 | Set Builtin § 4.3.1, `-m` | "When a background job completes, the shell prints a line containing its exit status." | **14** | a completion notice is a `-m` side effect |
| Q5 | Job Control Basics § 7.1 | "Background processes are those whose process group ID differs from the controlling terminal’s; such processes are immune to keyboard-generated signals." | **20** | monitor-mode children do **not** get terminal Ctrl-C |
| Q6 | Job Control Basics § 7.1 (async-job printout) | "the process ID of the last process in the pipeline associated with this job is 25647" | **16** | `$!` is the last pipeline element, not the group leader |

Q5 carries the typographic apostrophe `’` in "terminal’s" exactly as served. Q6 is a lower-case mid-sentence fragment by design (it is the clause that defines `$!`); L1 may prefer Q2+Q1 for the row quote.

## 3. Draft SOURCES.md row — S064

Append after S063 in `corpus/SOURCES.md`. Id is the next free one (`grep -c '^| S0'` = 63; no `S064`); L1 may renumber. Contract cells match S051–S063: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.

| S064 | GNU Bash 5.3 manual, Job Control Basics and The Set Builtin `-m` — https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html; https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html | docs | A | what `set -m` enables and how Bash binds jobs, pipelines and process groups; not signal delivery, not descendants that call setsid, not notice behavior without a tty | live pages unreachable 2026-10-20 (curl exit 28, 40 s each); Wayback captures 20260803220758 (Job Control Basics § 7.1) and 20260930073822 (Set Builtin § 4.3.1 `-m`), both serving "This is Edition 5.3, last updated 18 May 2025"; installed bash(1) 5.3.20 roff 11462 repeats the group sentence and 11456-11461 gives the interactive default; opened by SoujiR18.SrcBashJobControl | `set -m` enables job control — "Job control is enabled (see Job Control). All processes run in a separate process group." (15 words) — so one pipeline, one Bash job, is signalable as a group | mined | 2026-10-20 | on-release | corpus/lessons/round-18.md |

Landing notes for L1:
- **Provenance header**: add a "Round-18 provenance" sentence in the `corpus/SOURCES.md` header naming S064+, its access record (this report), and any sibling rows, matching the round-13/14/16/17 paragraphs.
- **E11 ordering**: `scripts/sources-census.sh` E11 errors when a `mined` row's `used-by` path is missing on disk (`sources-census.sh:566-567`, `if [ ! -e "$dir/$path" ]`). `corpus/lessons/round-18.md` must exist (or `used-by` must point at the knowledge entry that consumes S064) before the validator runs; do not land the row alone if a validate step precedes the lesson.
- The `teaches` cell carries the quote because this round's ticket requires the verbatim quote in the row; if the contract prefers paraphrase, the quote already lives in the Gate section below and the cell can drop to: "`set -m` gives each pipeline (a job) a separate process group, so one `census_one` fork is signalable as a unit".

## 4. What it teaches for souji r18 (C1 operability)

Current state at `b576341` (read-only `git show`, line-stable):

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b576341:tools/souji-census.sh \
  | grep -n '^emit_census()\|census_one "\$repo"\|^census_one()\|set -m'
1261:census_one() { # $1 repo-dir
1394:emit_census() {
1403:    if row=$(census_one "$repo"); then
```

`emit_census` calls `census_one` **synchronously in the census shell's own process group** via command substitution; there is no `set -m` anywhere in the file at `b576341`. `guard_git_files` (`tools/souji-census.sh:546-585`) only `stat`s the metadata before git runs, so the L1 repro (regular file swapped for a FIFO on the shim's `status` call) reaches git's own `open(2)` and blocks; S062 owns the blocking-open fact, this row owns the process-group fact.

Load-bearing consequences for the fix contract:

1. **SOURCED (Q1, Q2, Q3 + bash(1) roff 11456-11461).** In a non-interactive shell job control is off (`"This option is on by default for interactive shells on systems that support it"`), so today the child shares the census shell's pgid. `set -m` must be enabled around the fork for "its own process group" to exist at all; without it a `kill -- -PGID` has no child group to hit.
2. **SOURCED (Q1).** With `-m` on, the async job is placed in a separate process group; SIGTERM-then-SIGKILL can therefore be sent to the group id, not to a pid. (Delivery semantics are kill(2), not this source — see §5.)
3. **SOURCED (Q6, Q2, Q3).** Do not assume `$!` is the group id when the job is a pipeline: JCB defines `$!` as "the process ID of the last process in the pipeline", while bash(1) `jobs -p` is documented as "List only the process ID of the job's process group leader" (roff 10674-10675). If `census_one` is backgrounded as **one** command (`( census_one … ) &` or a single `bash … &`), the leader is that process; if it is ever backgrounded as a pipeline, the watchdog must take the pgid from `jobs -p` rather than `$!`. [INFERENCE] that bash sets pgid = leader pid for a simple async job; Q1 states only that a separate group exists.
4. **SOURCED (Q5) — the leak the naive fix creates.** Under monitor mode the job's pgid differs from the terminal's and such processes "are immune to keyboard-generated signals". Ctrl-C/SIGINT on a running census will no longer reach the in-flight repo job; unless `emit_census` traps INT/TERM/EXIT and group-kills the current child, the L1 hang is traded for a leaked blocked process on operator interrupt — against C1's "no lane fixture leaves a blocked process behind". **Smallest fix**: `trap 'kill -TERM -- -"$pgid" 2>/dev/null; kill -KILL -- -"$pgid" 2>/dev/null' INT TERM EXIT` scoped to the live child, plus the contract's watchdog for the ordinary timeout.
5. **SOURCED (Q4) — stderr shape.** Under `-m` "When a background job completes, the shell prints a line containing its exit status." The contract's stderr surface is only `souji-census: repo-timeout <N>s <repo>`, so a completion notice would be extra bytes. The source does not say which descriptor carries it or whether a headless non-interactive script emits it (§5). **Smallest hedge**: give each job its own stderr (the private temp file, or `2>&1` into it) so the parent's stderr is written only by the watchdog, and let the fixture assert stderr byte-exactly.
6. **Scope the mode change**: `set -m` before the fork, `set +m` immediately after reaping, so no other command runs under changed signal/terminal semantics; the watchdog process must hold none of the caller's stdout/stderr descriptors (contract text) — the source is silent on fd inheritance, so that part stays a design assertion, not a sourced one.

## 5. What it does NOT establish (row scope boundary)

- It does not state that a **process group can be signalled**: that is kill(2)/kill(1); bash's own `kill` builtin entry (bash(1) roff 10709ff) documents signal names and defaults, not negative-pid group targets.
- It does not say a blocked `open(2)` is interruptible, or that SIGKILL works on a D-state task: S062 owns the FIFO block, kill(2) owns delivery.
- It does not say a descendant cannot leave the group (`setsid`/`setpgid`), nor that re-parenting preserves group membership.
- It does not say the completion line appears in a **non-interactive, no-tty** script, nor on which descriptor; bash(1)'s `-m` entry states it unconditionally, but this must be measured (see §7).
- It does not state the timeout value, the SIGTERM→SIGKILL interval, the TSV row shape, or the exit-code split (2 for protected refusal, 1 otherwise) — all contract/implementation decisions.
- It does not establish that `$!` equals the group id for a pipeline (Q6 says it is the last element), nor that `jobs -p` output is stable under `set -m` plus command substitution.
- Manual-vs-man-page divergence, worth citing carefully: the Edition 5.3 Set Builtin page's `-m` entry does **not** carry the "on by default for interactive shells" clause that installed bash(1) 5.3.20 roff 11456-11461 carries. Cite the man page for the default, the manual for the group statement; do not present them as one text.

## 6. Mined mistake

The belief mined out: *"a backgrounded `census_one` already runs in its own process group, so a timeout watchdog can just `kill -- -$!`."* At `b576341` no `set -m` exists (grep output above is empty for it), so the child is in the census shell's group; and Q6 shows `$!` is the last pipeline element, not the leader. A watchdog built on that belief would either signal a pid with no group (ESRCH, child keeps blocking) or, if the negative id resolves to the census shell's own group, signal the census — and its caller's group — instead. The documented design is `set -m` around the fork, a single-command async job (or `jobs -p` for the leader), and an explicit group kill that also runs from the INT/TERM/EXIT trap (Q5).

## 7. Commands run (exact, with outputs)

All read-only; no lane writes except this report; no processes started beyond the fetches and no signals sent.

```
$ bash --version | head -1
GNU bash, version 5.3.20(1)-release (x86_64-pc-linux-gnu)

$ zgrep -n "All processes run in a separate process group" /usr/share/man/man1/bash.1.gz
11462:All processes run in a separate process group.

$ zcat /usr/share/man/man1/bash.1.gz | grep -n "process group" | head
6056:same process group as the terminal, and ...
6179:each process has a process group ID, and ...
6185:Processes that have the same process group ID are said to be part of
6186:the same process group.
6196:processes are those whose process group ID differs from the
10675:List only the process ID of the job's process group leader.
10703:with the corresponding process group ID, and executes
11462:All processes run in a separate process group.

$ zcat /usr/share/man/man1/bash.1.gz | sed -n '11455,11466p'   # -m entry, roff
Monitor mode.
Job control is enabled.
This option is on by default for interactive shells on systems
that support it (see JOB CONTROL ...).
All processes run in a separate process group.
When a background job completes, the shell prints a line
containing its exit status.

$ head -1 <(python3 -c '...strip tags...')      # extracted text, Job Control Basics
Job Control Basics (Bash Reference Manual)
$ grep -n -i "process group\|job control is enabled" Job-Control-Basics.txt The-Set-Builtin.txt
Job-Control-Basics.txt:41:each process has a process group ID, and
Job-Control-Basics.txt:46:Processes that have the same process group ID are said to be part of
Job-Control-Basics.txt:47:the same process group.
Job-Control-Basics.txt:49:process group ID is equal to the current terminal process group
The-Set-Builtin.txt:73:Job control is enabled (see Job Control).
The-Set-Builtin.txt:74:All processes run in a separate process group.

$ wc -w  (each quote on its own line)
15   Job control is enabled (see Job Control). All processes run in a separate process group.
8    The shell associates a job with each pipeline.
14   All of the processes in a single pipeline are members of the same job.
14   When a background job completes, the shell prints a line containing its exit status.
20   Background processes are those whose process group ID differs from the controlling terminal’s; such processes are immune to keyboard-generated signals.
16   the process ID of the last process in the pipeline associated with this job is 25647

$ sha256sum Job-Control-Basics.wayback.html The-Set-Builtin.wayback.html
fd1d6c6b842713e99d40c1a79138bf706887b931331bea5e0e6166f545504cb7  Job-Control-Basics.wayback.html
39fb870335963552325a4fabb22d00ab68cd48738d76d18690db17646379991b  The-Set-Builtin.wayback.html

$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b576341:tools/souji-census.sh \
  | grep -n '^emit_census()\|census_one "\$repo"\|^census_one()\|set -m'
1261:census_one() { # $1 repo-dir
1394:emit_census() {
1403:    if row=$(census_one "$repo"); then
```

(`set -m` has **zero** matches in `tools/souji-census.sh` at `b576341`, and none in the working-tree copy either.)

## 8. Verdict

**Holds** for the assigned source item: both pages are located at a named edition (5.3, 18 May 2025), the mechanism sentence Q1 is verbatim and 15 words, the pipeline↔job↔process-group chain is fully quoted (Q1–Q3), and the row matches the 11-column registry contract. Confidence: **high** for quotes/edition/capture identity; **medium** for consequences 3–5 (documented mechanism plus one unmeasured behavior — completion-notice emission in a headless non-interactive script). The row is a mechanism source, not proof that the census watchdog works; the fixture must still show 0 blocked processes.

## 9. Remaining unknowns

- Whether bash 5.3.20 emits the `-m` completion line on stderr in a non-interactive, no-tty script. I did **not** execute arbitrary bash under the probe rule, so this is unmeasured; the executor's fixture should assert stderr exactly (contract line only), which settles it.
- Whether the census runner's bash is 5.3.x everywhere (host is 5.3.20; the lane's evidence is this host).
- Final row id (S064) and `used-by` target depend on L1's landing order and on the round-18 lesson file existing before `sources-census.sh validate` (E11).
- Whether another wave-1 seat also claims S064 (frontier allows S064+; renumber at landing if so).

## 10. Tooling

No installs or upgrades were needed or performed (pacman is paused host-wide anyway). Temporary fetch workspace `/var/tmp/souji-r18-SrcBashJobControl/` was removed after this report was written; the archived bytes are public and both sha256 sums plus capture ids are recorded above for re-fetch.
