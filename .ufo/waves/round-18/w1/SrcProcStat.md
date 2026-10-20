STATUS: DONE — proc_pid_stat(5) (man-pages 6.19, 2026-02-08) grounds starttime as clock ticks since boot and pgrp/session as fields 5/6; host tick rate 100 and the index mapping were verified live; the boot-epoch (btime) leg and the comm-parse rule are outside this source.

# Source item — proc_pid_stat(5)

## Fetch record

- URL fetched (exact): `https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html`
  (`read` method native, Content-Type `text/html`, 373 HTML-rendered man lines).
- Access date: 2026-10-20.
- Served version / last-updated line: footer reads

  ```
  Linux man-pages 6.19            2026-02-08               proc_pid_stat(5)
  ```

  Colophon: "This page was obtained from the tarball man-pages-6.19.tar.gz fetched ... on 2026-09-09"; "HTML rendering created 2026-09-09 by Michael Kerrisk". No separate "last updated" line is served.
- Host cross-check: `pacman -Q man-pages` → `man-pages 6.19-1`; installed roff `.TH proc_pid_stat 5 2026-02-08 "Linux man-pages 6.19"` at `/usr/share/man/man5/proc_pid_stat.5.gz:7`; anchors `:104` `(5) pgrp`, `:107` `(6) session`, `:227` `(22) starttime` — same revision as the web page, so the row can cite both.

## Verbatim quote (located, ≤25 words)

Location: § DESCRIPTION, field `(22) starttime` (two contiguous sentences, only line-wrapped in the HTML):

> Before Linux 2.6, this value was expressed in jiffies. Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK)).

`printf '%s' "<quote>" | wc -w` → **22**. Not paraphrased; punctuation and wrapping exactly as served.

Supporting fields, also verbatim (short, so quoted separately rather than folded into the 22-word quote):

- `(5) pgrp %d` — "The process group ID of the process." (`wc -w` = 7)
- `(6) session %d` — "The session ID of the process." (`wc -w` = 6)

## Extracted contract

Field numbering is 1-based from `pid`, per "The fields, in order, with their proper scanf(3) format specifiers, are listed below." Because field 2 `comm` sits inside parentheses, the reliable parse is: drop everything through the **last** `)`; the remaining tokens start at field 3, so overall field *N* = token *N−2*.

| `stat` field | name | census column |
|---|---|---|
| 1 | pid | `pid` |
| 2 | comm | — (parenthesised; unstable width) |
| 3 | state | `state` |
| 4 | ppid | `ppid` |
| 5 | pgrp | `pgid` |
| 6 | session | `sid` |
| 7 | tty_nr | — |
| … | … | — |
| 22 | starttime | `age_s` input |

`starttime` is **clock ticks since boot** (jiffies before Linux 2.6), so:

```
age_s = (uptime_seconds * CLK_TCK - starttime) / CLK_TCK      # equivalent: now_epoch - (btime + starttime/CLK_TCK)
```

`CLK_TCK` is the runtime value of `sysconf(_SC_CLK_TCK)`; on this host `getconf CLK_TCK` → `100`.

`[PT]` note: the page marks (26)–(30), (35) `wchan`, and (45)–(52) with `[PT]` ("If the check denies access, then the field value is displayed as 0"). `pgrp` (5), `session` (6) and `starttime` (22) carry **no** `[PT]` mark, so the census needs no ptrace access for the three fields it takes from this source.

## What it teaches for souji r18

1. C3's `tools/souji-proc-census.sh` must read `pgid` from field 5 and `sid` from field 6; they are different namespaces, and a residue row cannot substitute one for the other.
2. Age must be computed from field 22 divided by the tick rate — never treated as seconds. A 100-tick value read as seconds understates a 25 000 s-old orphan by ~250×, which would silently pass any `--min-age` filter.
3. The parse must key on the last `)`; a whitespace split is wrong because **`comm` can contain spaces on this host**. Observed live: `/proc/409/stat` begins `409 (UVM global queue) S 2 0 0 0 …`.
4. `pgid`/`sid` may legitimately be `0`. Observed live: pid 409 is a kernel thread with `pgrp 0 session 0` (`ps -o pid,ppid,pgid,sid` agrees). A fixture or census that treats 0 as "missing" would misclassify.
5. The three fields are readable without ptrace access (no `[PT]` mark), so the census can stay unprivileged and still populate `pgid`, `sid`, `age_s`.

## What it does NOT establish

- **The boot epoch.** The page says `starttime` is relative to "system boot" but never defines that instant and does not mention `/proc/stat`'s `btime` or `/proc/uptime`. The census age formula therefore has one leg outside this source. Host observation (separate file, not this page): `/proc/stat` `btime 1792501016`, and `now−btime = 25113` vs `uptime = 25112.70`, i.e. `btime` is the boot epoch. [Observed, not sourced by S064.]
- **The tick rate value.** No numeric HZ is stated; the page defers to `sysconf(_SC_CLK_TCK)`. Host 100 is an observation (`getconf CLK_TCK`), not a claim of this page.
- **The `comm` parse hazard.** The page says only "The filename of the executable, in parentheses." It does not state that `comm` may contain spaces or parentheses; the last-`)` rule is grounded by live observation, not by this text.
- **The `comm` truncation bound.** The page states "Strings longer than TASK_COMM_LEN (16) characters (including the terminating null byte) are silently truncated", yet host pid 410 serves a 26-character comm (`UVM deferred release queue`; `/proc/410/comm` identical). The 16-character bound is therefore not a host guarantee and must not be relied on.
- **Read atomicity / non-blocking / ESRCH.** The page says nothing about a `/proc/<pid>/stat` read racing with process exit or ever blocking. C1/C3 fixture safety must not cite this source for "a `/proc` read cannot hang".
- **Cross-kernel or cross-OS field stability.** Linux-only page; "since Linux X.Y" annotations mark additions, not a stability promise; no BSD/macOS `stat` layout is covered.
- **That a process is orphaned, leaked or safe to kill.** The fields are descriptive; nothing here supports a kill decision (C3 stays list-only).

## Empirical verification (commands and output, verbatim)

Field mapping and tick units, against `ps` at the same instant:

```
$ pid=$$; line=$(</proc/$pid/stat); rest=${line##*) }; set -- $rest; \
  printf 'pid=%s state=%s ppid=%s pgrp=%s session=%s num_threads=%s starttime=%s\n' \
    "$pid" "${1}" "${2}" "${3}" "${4}" "${18}" "${20}"
pid=3092 state=R ppid=2765 pgrp=3092 session=2765 num_threads=178 starttime=3467
$ read -r u _ </proc/uptime; ui=${u%.*}; echo "uptime_int_s=$ui hz_assumed=100 computed_age_s=$(( (ui*100 - ${20}) / 100 ))"
uptime_int_s=25078 hz_assumed=100 computed_age_s=25043
$ ps -o pid=,ppid=,pgid=,sid=,etimes= -p $pid
3092 2765 3092 2765 25044
$ getconf CLK_TCK
100
```

→ pgrp/session/uptime-derived age match `ps` (1 s from the truncated fractional uptime). `pgrp` (3092) ≠ `session` (2765), which is the distinction the two columns exist for.

Kernel-thread zero values and the `comm`-space parse hazard:

```
$ head -c 90 /proc/409/stat; echo
409 (UVM global queue) S 2 0 0 0 -1 2129984 0 0 0 0 0 0 0 0 20 0 1 0 417 0 0 1844674407370
$ line=$(</proc/$p/stat); rest=${line##*) }; set -- $rest; \
  printf 'state=%s ppid=%s pgrp=%s session=%s starttime=%s\n' "${1}" "${2}" "${3}" "${4}" "${20}"
state=S ppid=2 pgrp=0 session=0 starttime=417
$ ps -o pid=,ppid=,pgid=,sid=,etimes=,comm= -p 409
409 2 0 0 25094 UVM global queue
```

Boot-epoch reconciliation (btime is a separate document, recorded because the age formula consumes it):

```
$ read -r up ui2 _ </proc/uptime; ui=${up%.*}; bt=$(grep -m1 '^btime ' /proc/stat | cut -d' ' -f2); \
  echo "uptime=$up btime=$bt now=$(date +%s) now_minus_btime=$(( $(date +%s) - bt ))"
uptime=25112.70 btime=1792501016 now=1792526129 now_minus_btime=25113
$ ... starttime=417 age_s=$(( (ui*100 - 417) / 100 )) ps_etimes=$(ps -o etimes= -p 409 | tr -d ' ')
pid409 starttime=417 age_s=25107 ps_etimes=25108
```

Quote accounting: `wc -w` = 22 (limit 25). Installed-page anchors: `:104`, `:107`, `:227`; `.TH ... 2026-02-08 "Linux man-pages 6.19"`.

## Draft SOURCES.md row (next free id after S063)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S064 | proc_pid_stat(5) — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | docs | A | `/proc/pid/stat` field order and the `starttime`/`pgrp`/`session` fields on Linux; not the boot epoch (`btime`), the runtime tick rate, the `comm` parse rule, or read atomicity | Linux man-pages 6.19 (2026-02-08), served 2026-10-20 (HTML rendering 2026-09-09); § DESCRIPTION fields (5) pgrp, (6) session, (22) starttime; host man-pages 6.19-1 /usr/share/man/man5/proc_pid_stat.5.gz roff :104, :107, :227 | `starttime` counts clock ticks since boot (jiffies before 2.6), so age_s = (uptime_ticks − starttime)/sysconf(_SC_CLK_TCK); pgrp is field 5 and session field 6 and the two are distinct; the ordered list follows a parenthesised `comm`, so fields are counted from the last `)` | mined | 2026-10-20 | on-release | corpus/lessons/round-18.md |

Lesson-Gate provenance line (shape per the S051–S063 provenance paragraph; goes to `corpus/lessons/round-18.md` Gate when L1 integrates):

```
S064 — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html, opened 2026-10-20, Linux man-pages 6.19 (2026-02-08), HTML rendering 2026-09-09. Quote (§ DESCRIPTION, (22) starttime, 22 words): "Before Linux 2.6, this value was expressed in jiffies. Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK))."
```

`used-by` is proposed as `corpus/lessons/round-18.md` because C3 is new this round and no knowledge page cites it yet; L1 should repoint it if the residue knowledge page lands.

## Verdict

**Holds** for the scoped claim: field 5 = `pgrp`, field 6 = `session`, field 22 = `starttime` in clock ticks since boot, verified live (age 25043 vs `ps` 25044; 25107 vs 25108) with `CLK_TCK` = 100. The row must not be used for `btime`, HZ, the last-`)` parse rule, `comm` width, or `/proc` read safety — all are outside the page; the `comm`-space and zero-`pgid` facts are host observations and need their own line if cited.

**Smallest fix at integration** (C3 consumer, not this report's file): compute `age_s` as `(uptime_ticks − starttime)/$(getconf CLK_TCK)` or `now − btime − starttime/CLK_TCK`, parse `/proc/<pid>/stat` from the last `)`, keep `0` as a valid `pgid`/`sid`, and cite S064 only for units and indices. If the age leg must be fully sourced, a wave-2 row for `/proc/stat` `btime` (proc(5) or proc_pid_stat does not document it) is the missing prerequisite; none of the above changes the C3 surface contract (header `pid\tppid\tpgid\tsid\tage_s\tstate\twchan\treason\tcmd`, never signals).

No tools installed or upgraded; no pacman transactions attempted; no files written outside this report.
