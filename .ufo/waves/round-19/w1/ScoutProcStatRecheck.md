STATUS: DONE — S075 field 6 quote re-opened verbatim; field 22 starttime semantics confirmed; S075 needs a recheck note only, not supersession.

# Findings

- **Field 6:** The live page still contains the exact S075 quote, “The session ID of the process.” (6 words), under DESCRIPTION field (6), `session %d`. This matches the original S075 quotation in `corpus/lessons/round-18.md:60`.
- **Field 22:** `starttime %llu` is the time the process started after system boot. The page says it was expressed in jiffies before Linux 2.6 and, since Linux 2.6, in clock ticks divided by `sysconf(_SC_CLK_TCK)`. That supports the recorded start-time/units semantics; it does not make the page evidence for an atomic `/proc` snapshot.
- **Disposition:** S075 does **not** need supersession: the field 6 quote and field 22 meaning remain unchanged. The current S075 registry row already supersedes S068 (`corpus/SOURCES.md:95`), and the round-19 lesson records the 2026-10-21 recheck without changing S075’s status (`corpus/lessons/round-19.md:86-98`). A recheck note is sufficient. If a registry-visible, append-only recheck is desired, append this proposed row rather than editing S075; S088 is the latest inspected identifier (`corpus/SOURCES.md:105-108`):

```markdown
| S089 | proc_pid_stat(5) field 6/22 recheck — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | docs | A | field 6 session meaning; field 22 process start time and units | Linux man-pages 6.19 (2026-02-08), opened 2026-10-21; § DESCRIPTION, fields (6) `session %d` and (22) `starttime %llu`; COLOPHON release/date | Field 6: “The session ID of the process.” (6 words); field 22: starttime is measured from system boot and, since Linux 2.6, in clock ticks | mined | 2026-10-21 | on-release | corpus/lessons/round-19.md (S075 recheck) |
```

The anchor uses the page’s dated man-pages revision and named DESCRIPTION fields, not a mutable HTML line number. This is a proposal only; no source registry row was changed.

# Evidence

- **Direct page read, access date 2026-10-21:** https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html — § DESCRIPTION, field (6) `session %d`: “The session ID of the process.” (6 words). It appears verbatim.
- **Direct page read, access date 2026-10-21:** same URL — § DESCRIPTION, field (22) `starttime %llu`: “The time the process started after system boot.” (8 words); the following text says the value is expressed in clock ticks since Linux 2.6. The COLOPHON/footer identifies Linux man-pages 6.19, dated 2026-02-08, and the page says it was obtained from `man-pages-6.19.tar.gz` fetched 2026-09-09.
- Local registry and history checked: `corpus/SOURCES.md:19` gives the row schema; `corpus/SOURCES.md:95` is the current S075 row; `corpus/lessons/round-18.md:60` records its original field 6 quote; `corpus/lessons/round-19.md:86-98` records the current recheck and retained status.

# Commands run

- Opened the exact specified man7 URL with `read`; checked DESCRIPTION fields (6) and (22) and the COLOPHON/footer.
- Used local `grep` to locate S075/S088 and read only the relevant registry, lesson, and preregistration sections. The grep was file navigation, not evidence for the manual’s semantics.
- No shell commands were run.

# Contract compliance

- No subagents, installs, or additional network destinations. No files outside this scoped report were written. No signal, live census, or secret/environment read was performed.