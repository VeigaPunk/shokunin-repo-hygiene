STATUS: DONE — `pidfd_send_signal(2)` adds distinct, limited identity-context ground; it does not prove the no-signal claim.

# Findings

- I opened `pidfd_send_signal(2)` as the additional candidate. Its PID-file-descriptor note documents the PID-reuse hazard and a stable process-reference alternative. This adds distinct context for why a PID alone is insufficient; it is not a duplicate of S075 or the `kill(2)` rows S066/S073. It does **not** establish that Souji uses pidfds or independently validate its `(pid, starttime, boot_id)` binder (`corpus/knowledge/process-residue-observations.md:46-48`).
- The other opened candidate, `proc_pid_stat(5)` field 22, duplicates existing S075: that row already covers field 22's starttime tick units and use for PID-identity revalidation (`corpus/SOURCES.md:95`).
- `pidfd_send_signal(2)` describes sending a signal, not the absence of signal calls. The entry's no-signal claim remains supported by the stated signal-syscall trace fixture P7, not by this source (`corpus/knowledge/process-residue-observations.md:52-54`).

# Evidence

- `pidfd_send_signal(2)`, https://man7.org/linux/man-pages/man2/pidfd_send_signal.2.html, opened 2026-10-21; Linux man-pages 6.19 (2026-02-08), `NOTES` → `PID file descriptors`: “may accidentally send a signal to the wrong process if the originally intended target process has terminated and its PID has been recycled” (23 words).
- Existing source rows distinguish the relevant coverage: S075 is `proc_pid_stat(5)` field attribution (`corpus/SOURCES.md:95`); S066/S073 are `kill(2)` group-addressing and delivery semantics (`corpus/SOURCES.md:86,93`).

# Commands run

- Searched `corpus/` for S079–S085 and process-residue references, then for existing `kill(2)`, pidfd, and signal rows.
- Read the process-residue identity/safety sections and the cited source-ledger rows; opened the public `pidfd_send_signal(2)` and `proc_pid_stat(5)` man pages. No executable command or test was run.
- Checked for `lsp`; `xd://lsp` is not mounted in this environment. No code-semantic claim depends on grep output.

# Contract compliance

- Wrote only this scoped report. No repository source, tests, corpus, or ledger files were changed.
- Network access was limited to the two named public man7 candidate pages. No tool was installed; no tests or live census were run.
