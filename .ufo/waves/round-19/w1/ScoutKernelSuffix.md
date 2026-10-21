STATUS: DONE — man7 explicitly documents the ` (deleted)` suffix for `exe`, not `cwd` or `fd`; the committed fixture supplies cwd/fd observations.

# Findings

- The three requested man7 DESCRIPTION sections are not equivalent: `proc_pid_exe(5)` explicitly states the suffix behavior for an unlinked executable pathname. Strongest sentence (19 words): “If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname.” [man7 proc_pid_exe(5), DESCRIPTION](https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html#DESCRIPTION), accessed 2026-10-21.
- `proc_pid_cwd(5)` describes the cwd symlink and `proc_pid_fd(5)` describes fd symlinks, but their inspected DESCRIPTION sections do not document the ` (deleted)` suffix. This is silence in those pages, not evidence that the kernel never emits it.
- The committed fixture carries the cwd/fd observations. `tests/fixtures/r18-proc-census.sh` P1 checks a removed cwd link ends in ` (deleted)` (lines 374–387), and P9 removes the stdout target, checks the fd link suffix, then expects a deleted-fd row (lines 173–188, 624–633). P12/P13 are the discriminating negative controls: a *live* cwd/fd target whose literal name ends in ` (deleted)` is inode-matched and omitted (lines 412–431, 657–680). Thus raw suffix text alone is not treated as proof of deletion.

# Evidence

- `https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html#DESCRIPTION` — cwd is described as a symlink to current working directory; no deleted-suffix rule in the inspected page. Accessed 2026-10-21.
- `https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html#DESCRIPTION` — fd symlinks and their contents are described; no deleted-suffix rule in the inspected page. Accessed 2026-10-21.
- `https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html#DESCRIPTION` — quoted sentence above explicitly documents the suffix for an unlinked pathname. Accessed 2026-10-21.
- The fixture is tracked at base `3ab2c81` as blob `2d7c5bed4df3dc3aaaae201a27b78ecc4dcabbbe`; the read-only comparison reported no worktree diff for that path. Line references above identify the case setup and assertions.

# Commands run

- `git ls-tree 3ab2c81 tests/fixtures/r18-proc-census.sh && git diff --quiet 3ab2c81 -- tests/fixtures/r18-proc-census.sh` — confirmed the fixture is in the base tree and unchanged in the worktree.
- Opened all three requested man7 pages and searched/read the cited fixture sections. No fixture, build, or selftest was executed.

# Contract compliance

- Wrote only this scoped report; no tools were installed or updated.
- No LSP device was exposed in the available tool routes, so no LSP query was possible. Fixture conclusions above are grounded in the opened setup and assertion code, not grep output alone.
- No scratch files were created.
