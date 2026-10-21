STATUS: DONE — `proc_pid_status(5)` defines State/Name (and Pid/PPid/Uid), but most census output is sourced or derived elsewhere.

# Findings

- **Located quote (12 words):** “Name Command run by this process. State Current state of the process.” Source: [proc_pid_status(5)](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html#DESCRIPTION), `DESCRIPTION` → “The fields are as follows” → `Name`, `State`; accessed 2026-10-21.
- **Direct column-semantic coverage:** `state` is documented by the `State` definition and its listed values. `ppid` corresponds to the documented `PPid` (“PID of parent process”). `pid` has a qualified correspondence to the documented `Pid` field (“Thread ID”): this census prints the numeric `/proc/<pid>` directory name, and this page does not document that enumeration rule. The census reads its emitted `state` and `ppid` from `/proc/<pid>/stat`, not from `/proc/<pid>/status` (`tools/souji-proc-census.sh:110-132,314-330,375-377`). Thus the page supports meanings, not this census’s acquisition or snapshot behavior.
- **Name is not a census column.** The page documents status `Name` (including truncation at `TASK_COMM_LEN`); the census’s `cmd` instead joins NUL-separated `/proc/<pid>/cmdline` arguments, then redacts and truncates them (`tools/souji-proc-census.sh:230-256,364-377`). Do not cite the page’s `Name` field as documentation for the `cmd` column.
- **Documented but not emitted:** `Uid` is defined on this page and is read from `status` to apply the own-UID filter; no UID column is printed (`tools/souji-proc-census.sh:147-157,333-334`).
- **Not documented by this page; code/measurement governs:** `pgid`, `sid`, and `starttime` are parsed from `stat`; `age_s` is calculated from `/proc/uptime`, `starttime`, and `CLK_TCK`; `wchan` is read from `/proc/<pid>/wchan`; `reason` is the census classifier based on cwd, argv, and fd path checks (`tools/souji-proc-census.sh:110-132,258-285,335-363`). The `boot_id` comment is read from `/proc/sys/kernel/random/boot_id` (`:286-292`), not from `status`. In particular, the page does not establish the cwd/fd ` (deleted)` behavior or the census’s residue classification; these are implementation/observed-interface claims, not facts supplied by this page.
- **Confidence: high** on the page/code distinction; this is a source review, not a new census execution or live-process observation.

# Evidence

- Public source: [https://man7.org/linux/man-pages/man5/proc_pid_status.5.html#DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html#DESCRIPTION), accessed 2026-10-21. Anchor `DESCRIPTION`, field definitions `Name`, `State`, `Pid`, `PPid`, `Uid`.
- Current worktree implementation read: `tools/souji-proc-census.sh:5-13` (schema), `:110-132` (stat parse), `:147-157` (status Uid), `:230-256` (cmdline), `:258-285` (fd and uptime), `:286-292` (boot ID), `:314-377` (age, reason, wchan, output). This is the integrated worktree source, not the base revision.
- The routed tool inventory exposed no LSP device (`xd://lsp` returned “No such tool”); grep was used only to locate source sections, followed by targeted reads. Source claims above are based on those reads, not grep as semantic proof.

# Commands run

No shell commands or fixtures were run. Used targeted source searches/reads, opened only the assigned public URL, and read the round-19 preregistration.

# Contract compliance

Wrote only this assigned report. No tools were installed; no pacman transaction, process signal, live census, git/jj mutation, scratch directory, or additional network access was used.