STATUS: DONE — two SOURCES rows drafted (S064 bash job model, S065 kill(2) group signalling) with located quotes; the live bash page timed out, so S064 is grounded on a Wayback capture.

# ScribeRowsJobs — round 18, wave 1 (C1 operability watchdog)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin (base b5763415cc67ecff1e8fe56c58c39a6fb106d7a3). Seat: SoujiR18.ScribeRowsJobs-5, leaf, no delegation, no commits, no jj, no git writes. This report is the only file written; `corpus/SOURCES.md` is NOT edited (L1 integrates the rows).

## Behavior

Two rows drafted for the C1 watchdog (`emit_census` process-group kill: SIGTERM to the group after the bound, SIGKILL 2 s later). Both are primary documentation, tier A, opened 2026-10-20, quotes verbatim and ≤25 words each. Rows use the S051–S063 shape (11 columns).

## Access record

| Document | Attempt | Result |
|---|---|---|
| https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html | `_read` ×2 (live) | Failed: "The operation timed out." (both attempts) |
| https://web.archive.org/web/20260803220758/https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html | `_read` | Fetched (Wayback capture 2026-08-03, "§ 7.1 Job Control Basics"); used for S064 quotes |
| https://man7.org/linux/man-pages/man2/kill.2.html | `_read` | Fetched natively; man-pages 6.19 (footer 2026-06-05; colophon fetched 2026-09-09) |
| https://web.archive.org/web/2026/https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html → capture 20260930073822 | `_read` | Fetched; `-m` text located (lead, see below) |
| /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md, corpus/lessons/round-17.md | `_read` | Read for row shape and Gate quote style |

Tools installed or updated: none.

## Drafted rows

Row shape: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`

```
| S064 | GNU Bash Reference Manual, 7.1 Job Control Basics — https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html | docs | A | bash job model: a pipeline is one job, and the processes of a job share a process group; not how a script enables job control | live page timed out 2026-10-20 (web fetch failed twice); Wayback capture 20260803220758 opened 2026-10-20; § 7.1 Job Control Basics; quotes "Processes that have the same process group ID are said to be part of the same process group." and "All of the processes in a single pipeline are members of the same job." | the census's per-repository pipeline forms one job whose members share one process group, so a group signal reaches each member; the page does not say how a non-interactive script turns job control on (set -m, documented in The Set Builtin, not this row) | queued | 2026-10-20 | on-release | —
| S065 | kill(2) — https://man7.org/linux/man-pages/man2/kill.2.html | docs | A | POSIX/Linux kill(2) signalling of a process group (negative pid), sig 0 existence probe, pid 0 and zombie semantics; not whether a group member can ignore the signal | Linux man-pages 6.19 (footer 2026-06-05), opened 2026-10-20; § DESCRIPTION (pid < -1; pid = 0; sig = 0), § ERRORS ESRCH, § NOTES; quotes "If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid." and "If sig is 0, then no signal is sent, but existence and permission checks are still performed;" | kill -TERM -- -PGID signals one whole group in one call; kill -0 tests existence without signalling; a zombie still counts as existing, so a probe alone cannot prove exit; limit: "If pid equals 0, then sig is sent to every process in the process group of the calling process." so an empty or unset PGID must never reach kill | queued | 2026-10-20 | on-release | — |
```

Quote verification (word counts, verbatim from the fetched text):

- S064 q1 "Processes that have the same process group ID are said to be part of the same process group." — 18 words. Source: Wayback capture 20260803220758, section 7.1.
- S064 q2 "All of the processes in a single pipeline are members of the same job." — 14 words. Same source.
- S065 q1 "If pid is less than -1, then sig is sent to every process in the process group whose ID is -pid." — 21 words. Source: kill(2) § DESCRIPTION.
- S065 q2 "If sig is 0, then no signal is sent, but existence and permission checks are still performed;" — 17 words. § DESCRIPTION.
- S065 q3 "Note that an existing process might be a zombie, a process that has terminated execution, but has not yet been wait(2)ed for." — 23 words. § ERRORS, ESRCH.
- S065 q4 "If pid equals 0, then sig is sent to every process in the process group of the calling process." — 19 words. § DESCRIPTION (limit).

## Leads (not drafted; L1 decides)

- **bash `set -m`** — The Set Builtin (Wayback 20260930073822, live page unreachable) reads: "Job control is enabled (see Job Control). All processes run in a separate process group." (9 words). This is the only located statement of the mechanism the watchdog's `set -m` depends on; S064 does not state it. Recommended as a third row S066 if L1 wants `set -m` cited, scope "set -m turns on job control; not the signal-delivery semantics".
- The live bash manual failed on two attempts; S064's `opened`/access record must say "Wayback capture", not "live page".

## Findings

1. Gap: the C1 claim "watchdog sends SIGTERM to the group" rests on S065 (negative pid) and on S064 (pipeline = one job = one group). The group creation step itself (`set -m`) is the lead above; without a row for it, the fix's `set -m` is ungrounded in SOURCES.
2. Limit to carry into the fix: `kill 0` and an empty PGID both address the caller's own group (S065 limit). A watchdog that computes PGID from `$!` or `ps` output must refuse empty or non-positive values before calling kill.
3. Limit on S064: job control is documented as an interactive-terminal feature; the non-interactive `set -m` behavior is not established by S064 and must be exercised by the C1 fixture, not inferred from the manual.
4. Not verified: any exercise of the watchdog, of `set -m`, or of killpg. These rows are documentation only; no runtime claim is made.

## Probes

- `_read` of the four URLs and the two local corpus files listed above. No shell commands run. No processes started or signalled. Nothing written outside this report.

## Verdict

- S064 holds for the two quoted statements; fails as a source for `set -m` (not stated there).
- S065 holds for all four quotes.
- Both rows: documentation-tier, scoped; no row changed. Re-open S064 on the live bash page when it responds (recheck on-release).

## Next (for L1 integration)

- Append S064 and S065 to `corpus/SOURCES.md` registry after S063; re-run `sources-census.sh validate` (the round-17 gate used that command).
- Decide S066 (`set -m`, Wayback capture 20260930073822) or record it as a lead.
- Round-18 Gate must list S064/S065 with access record and quotes; the round-18 lesson file does not yet exist.
