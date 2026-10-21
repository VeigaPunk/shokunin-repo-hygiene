STATUS: DONE — documented the proc-census state/wchan observations, permission caveat, and evidentiary limits.

# Findings

- The census header places `state` and `wchan` in separate TSV columns. It reads `state` from field 0 of `/proc/<pid>/stat`; it reads `/proc/<pid>/wchan`, substitutes `-` when that read leaves an empty value, sanitizes it, and emits both values in the row. [Source: `tools/souji-proc-census.sh:5-6,13,128,359-363,375-377`]
- The manual describes wchan as a symbolic kernel location where a process is sleeping. Access is governed by `PTRACE_MODE_READ_FSCREDS`, so the field is permission-sensitive. In this census, `-` is only the empty-read fallback; it does not establish whether access was denied or the value was otherwise unavailable/empty. [Source: `tools/souji-proc-census.sh:359-363`; manual quote below]
- `wchan` cannot prove why the process reached that kernel location, that it is deadlocked or permanently stuck, how long it has waited, or whether it will wake. Nor is the output pair an atomic snapshot: the census reads wchan at line 360 and subsequently rereads `stat` at lines 373-377 before emitting the final state.
- This is observational evidence only; it does not grant or imply authority to reap a process, consistent with the preregistered C3 boundary (`.ufo/waves/round-19/preregistration.txt:51-54`).

# Evidence

- Manual, `DESCRIPTION` anchor: “location in the kernel where the process is sleeping; … Permission to access this file is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check.” (23 words) https://man7.org/linux/man-pages/man5/proc_pid_wchan.5.html#DESCRIPTION — accessed 2026-10-21.
- Source mapping: `tools/souji-proc-census.sh:5-6,13,128-132,359-363,370-377`.
- Limits above are bounded to the documented value and the census read/order behavior; this does not claim a cause for any particular process.

# Commands run

- Searched `tools/souji-proc-census.sh` for `wchan|state` to locate relevant source sections, then read the header, state parse, and census output sections.
- Read `.ufo/waves/round-19/preregistration.txt` and opened the specified man7 URL.
- No census or other executable check was run; no tool was installed.

# Contract compliance

- Wrote only this scoped report; no source, corpus, tests, or lane integration files were changed.
- No LSP device/server was exposed in the available seat tooling, so semantic definition/reference queries were unavailable. The source statements above are direct source-text observations, not claims based on grep semantics.
- No subagents, git/jj mutations, process signals, or restricted census commands were used.
