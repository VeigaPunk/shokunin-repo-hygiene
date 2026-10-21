STATUS: DONE — proc_pid_fd(5) documents fd entries and symlink targets; it is silent on unlinked-target suffixes.

# Findings
- The `DESCRIPTION` says `/proc/pid/fd/` contains one entry per open file, named by file descriptor and symbolically linked to the actual file. This is the directory-entry behavior covered by the located quote below.
- The page also describes special symlink contents for pipes/sockets (`type:[inode]`) and inode-less descriptors (`anon_inode:file-type`); for the latter, it says the file-type is surrounded by square brackets in many, but not all, cases, with `anon_inode:[eventpoll]` as an example. This is target-content formatting, not a general pathname-suffix rule.
- The page does not discuss unlinked/deleted targets and documents no suffix behavior for them. In particular, it provides no basis here for asserting a ` (deleted)` suffix.
- Remaining unknown: behavior for unlinked targets is not established by this page; a suffix rule would require evidence from another source.

# Evidence
- Source: [proc_pid_fd(5), DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html#DESCRIPTION), accessed 2026-10-21. Quote (25 words): “one entry for each file which the process has open, named by its file descriptor, and which is a symbolic link to the actual file.”
- The same `DESCRIPTION` contains the `type:[inode]` and `anon_inode:file-type` formats and the bracket qualification cited above; a full-page read found no discussion of unlinked/deleted targets.

# Commands run
- Read `skill://godspeed` and `.ufo/waves/round-19/preregistration.txt` for the assignment context.
- Opened only the named public documentation URL with `read`; used `glob` to check the assigned report destination before writing it. No shell commands, tests, or installations.

# Contract compliance
- Wrote only `.ufo/waves/round-19/w1/ScoutProcFd.md`; no patch/artifact was requested. No lane source files were changed.
- No subagents, git/jj commands or mutations, process signaling, secret reads, or scratch files. No tool was installed or updated.
