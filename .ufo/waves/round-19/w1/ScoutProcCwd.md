STATUS: DONE — the man7 page's cwd-link statement and its documentary limits are located; it does not specify deleted/unlinked rendering.

# Findings

- `proc_pid_cwd(5)` DESCRIPTION identifies `/proc/pid/cwd` as a symbolic link to the process's current working directory. The same section says reading or dereferencing the link is governed by a `PTRACE_MODE_READ_FSCREDS` check.
- The page does **not** say how an unlinked/deleted cwd is rendered: it contains no claim that ` (deleted)` is appended. It does not compare cwd with `/proc/pid/exe` or say that the exe suffix rule applies to cwd. It also says nothing about inode identity or using inode comparison to disambiguate a literal live path ending in ` (deleted)`.
- Existing `S076` in `corpus/SOURCES.md:96` scopes its suffix statement to `exe` and calls cwd/fd application separately measured. The knowledge entry likewise labels inode comparison as a fixture rule, not a cwd-page statement (`corpus/knowledge/process-residue-observations.md:26-31,60-63`).
- **Proposed SOURCES row for C3:** this source is already registered as S082 (`corpus/SOURCES.md:102`), so retain S082 rather than add a duplicate ID. Suggested precise row wording:

  `| S082 | proc_pid_cwd(5) — https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html | docs | A | what /proc/pid/cwd links to and its access rule; not deleted/unlinked rendering, cwd-vs-exe suffix scope, or inode identity | Linux man-pages 6.19 (2026-02-08), opened 2026-10-21; § DESCRIPTION (#DESCRIPTION) | “This is a symbolic link to the current working directory of the process.” The page says nothing about the literal \` (deleted)\` suffix or an inode-identity test. | mined | 2026-10-21 | on-release | corpus/knowledge/process-residue-observations.md |`

# Evidence

- Public source opened at https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html, accessed 2026-10-21. Located quote, § DESCRIPTION (`#DESCRIPTION`): “This is a symbolic link to the current working directory of the process.” (11 words.) This is the page's cwd-link definition; there is no deleted/unlinked-representation quote to extract from this page.
- Read the rendered page and its raw HTML. The raw page's DESCRIPTION, NAME, SEE ALSO, and COLOPHON sections contain no deleted-suffix or inode-identity statement. The page contains no `exe` mention and makes no cwd-versus-exe comparison.
- Lane evidence: `corpus/SOURCES.md:96` (S076 scope), `corpus/SOURCES.md:102` (existing S082), and `corpus/knowledge/process-residue-observations.md:15-17,26-31,60-63`.

# Commands run

- No shell commands executed and no tools installed. Opened the exact requested public URL with `read` in rendered and raw modes; used local `grep` to locate the SOURCES schema and local `read` for the cited lane sections and round-19 preregistration.

# Contract compliance

- Wrote only this scoped report. No source, corpus, tool, test, census, or other lane file was edited. No network URL other than the exact requested man7 page was opened. No subagents or processes were spawned or signalled; no verification was run.