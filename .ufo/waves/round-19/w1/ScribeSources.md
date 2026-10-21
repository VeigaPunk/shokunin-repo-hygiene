STATUS: DONE — drafted and verified SOURCES rows for the four proc pages opened this round (S082 cwd, S083 fd, S084 wchan, S085 status) plus the recheck rows S075/S076; all four quotes re-fetched and matched byte-for-byte, three teaches cells carry non-documented policy and are corrected in the draft, and three lesson word counts are wrong. SOURCES.md was not modified.

# Findings

1. **The four rows already exist in the lane worktree.** `corpus/SOURCES.md:102-105` holds S082–S085 in the 11-column contract-v1 shape. The draft below reproduces them with the verified quote and a corrected `teaches` cell where the integrated text states lane policy as if it were documentation. No new id is needed; the contract shape has no quote column, so the quotes live in the round-19 Gate (`corpus/lessons/round-19.md:74-85`).
2. **Quotes verified verbatim.** All four quotes in the round-19 Gate appear exactly in the live man7 pages (Linux man-pages 6.19, footer date 2026-02-08), opened 2026-10-21. No quote is paraphrased.
3. **Three word counts in the Gate are wrong.** The quotes are correct; the stated counts are not. The Gate says S082 = 15 words (actual 13), S083 = 17 (actual 13), S085 = 23 (actual 18). S084 (15) and the S075/S076 quotes (6 and 20) are counted correctly. All remain under the 25-word limit. Correct these in the lesson, not in SOURCES.md.
4. **Three `teaches` cells overreach the page.** The page-only claims are in the drafted cells below.
   - S083: "so a vanished top-level directory can only be judged for path-shaped targets" is lane inference, not page text. Removed.
   - S084: "it is context for a residue row, never proof of what the process is blocked on" is lane policy. Removed; the page supports meaning and the ptrace gate only.
   - S085: "which the census prints as context and never as a liveness proof" is lane policy. Removed; the page supports the restatement and the State values.
5. **No page documents the `(deleted)` suffix for cwd or fd.** A case-insensitive grep for `deleted` over the cwd, fd, wchan and status pages returns zero matches. Only proc_pid_exe(5) carries it (S076). The S082 and knowledge-entry statements that the cwd/fd suffix is fixture-carried are confirmed.
6. **Recheck rows S075 and S076 match the live pages.** Both were re-fetched this round. Neither needs a new registry row: the page text is unchanged in substance, and the registry has no re-open date cell (the re-open is recorded in the Gate, as the lesson says). If L1 wants a registry-visible recheck, that is a supersession decision, not a fix.
7. **S079–S081 (git docs opened by L1 this round) are outside this item's named scope.** I did not re-open them; the contract restricts network use to the URLs the item names. Their rows are integrated at `corpus/SOURCES.md:99-101` and are unverified by this seat.

# Draft rows (contract-v1 columns; integrated text unless marked CHANGED)

Columns: id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S082 | proc_pid_cwd(5) — https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html | docs | A | what /proc/pid/cwd is and its access rule; no deleted-suffix statement | Linux man-pages 6.19 (2026-02-08), page dated 2026-02-08, opened 2026-10-21; § DESCRIPTION | cwd is a symbolic link to the process's current working directory, and readlink is governed by a ptrace access-mode PTRACE_MODE_READ_FSCREDS check; the page says nothing about a ` (deleted)` suffix, so the cwd suffix rule is fixture-carried, not documented here | mined | 2026-10-21 | on-release | corpus/knowledge/process-residue-observations.md |
| S083 | proc_pid_fd(5) — https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html | docs | A | fd directory entries and non-path link contents | Linux man-pages 6.19 (2026-02-08), opened 2026-10-21; § DESCRIPTION | CHANGED teaches: the fd directory has one entry per open file, each a symlink to the actual file; pipe and socket entries read `type:[inode]` rather than a pathname | mined | 2026-10-21 | on-release | corpus/knowledge/process-residue-observations.md |
| S084 | proc_pid_wchan(5) — https://man7.org/linux/man-pages/man5/proc_pid_wchan.5.html | docs | A | wchan meaning and its access rule | Linux man-pages 6.19 (2026-02-08), opened 2026-10-21; § DESCRIPTION | CHANGED teaches: wchan is the symbolic name of the kernel location where the process sleeps; access is ptrace-gated (PTRACE_MODE_READ_FSCREDS) | mined | 2026-10-21 | on-release | corpus/knowledge/process-residue-observations.md |
| S085 | proc_pid_status(5) — https://man7.org/linux/man-pages/man5/proc_pid_status.5.html | docs | A | human-parseable restatement of stat/statm fields | Linux man-pages 6.19 (2026-02-08), opened 2026-10-21; § DESCRIPTION (State field) | CHANGED teaches: status restates much of stat and statm in a parseable form; State is one of R (running), S (sleeping), D (disk sleep), T (stopped), t (tracing stop), Z (zombie) or X (dead) | mined | 2026-10-21 | on-release | corpus/knowledge/process-residue-observations.md |

Note on the S082 and S085 anchors: the integrated cells say `Linux man-pages 6.19 (2026-02-08)` and `opened 2026-10-21`. Those match the fetched footers. The S083 and S084 anchors are the same form.

The S082 row is unchanged from `corpus/SOURCES.md:102` (verified; no change needed). The S083, S084 and S085 rows differ from `corpus/SOURCES.md:103-105` only in the `teaches` cell marked CHANGED.

# Quote companion (for the round-19 Gate; ≤25 words each, located)

| id | quote (verbatim) | words (counted) | Gate states | location (rendered text dump, my extraction; see Evidence) |
|---|---|---|---|---|
| S082 | "This is a symbolic link to the current working directory of the process." | 13 | 15 — CORRECT | proc_pid_cwd.5 § DESCRIPTION, dump lines 73-74 |
| S083 | "a subdirectory containing one entry for each file which the process has open" | 13 | 17 — CORRECT | proc_pid_fd.5 § DESCRIPTION, dump lines 73-74 |
| S084 | "The symbolic name corresponding to the location in the kernel where the process is sleeping." | 15 | 15 | proc_pid_wchan.5 § DESCRIPTION, dump lines 73-74 |
| S085 | "Provides much of the information in /proc/pid/stat and /proc/pid/statm in a format that's easier for humans to parse." | 18 | 23 — CORRECT | proc_pid_status.5 § DESCRIPTION, dump lines 73-74 |
| S075 (recheck) | "The session ID of the process." | 6 | 6 | proc_pid_stat.5 field (6) session, dump line 52 |
| S076 (recheck) | "If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname." | 20 | 20 | proc_pid_exe.5 § DESCRIPTION, dump lines 78-80 |

Supporting, non-quote anchors (same dumps): S082 access sentence ("Permission to dereference or read (readlink(2)) this symbolic link is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check"), dump lines 84-85. S083 pipe/socket sentence ("For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode."), dump lines 79-80, and `type:[inode]` example, line 84. S084 access sentence, dump line 77. S085 State list ("One of "R (running)", "S (sleeping)", "D (disk sleep)", "T (stopped)", "t (tracing stop)", "Z (zombie)", or "X (dead)"."), status dump lines 144-146, under § DESCRIPTION (DESCRIPTION header line 71; next section SEE ALSO line 322). S075 starttime sentence ("Since Linux 2.6, the value is expressed in clock ticks"), stat dump lines 232-234.

# Evidence

Fetched 2026-10-21 with `curl -sS -L` from the exact man7 URLs named in S082–S085 and the recheck rows S075/S076 (HTTP 200 each). Plain-text dumps were made by stripping tags in scratch; line numbers refer to those dumps, not to the HTML. SHA-256 (full, from `sha256sum`; scratch removed after hashing):

- proc_pid_cwd.html c5ec2b4283537f52fd9132e290d8911dc35b891582434f0de54a70488d147f3f; proc_pid_cwd.txt 8a3e70d6ea059b1ae03f868558210466ea8e8589376363d8391eabff149e2c75
- proc_pid_fd.html 3a50ddef6f2f3a4f1139dcef3299a5eadf8fc96514df9fcb329a3bffd47ff27e; proc_pid_fd.txt b3b00b699d8f4faa07b23314dedfdb3676ac6ec7e477d347e72ec31d6fbba8e6
- proc_pid_wchan.html 6c117695e23f6cf8fb0fd38625ac7c157aa7e9692a7d5dd1670e4ba1efdb5400; proc_pid_wchan.txt ecb787a3cbeaa51f28c18e93f85584454b6a983f555dbb773c2f0c8377b219f4
- proc_pid_status.html 1596cd2751b15f9332136b60b28ba8d5c39ebc45e9d75ca8bd1d4d702f7eee43; proc_pid_status.txt 67d3110291d3064e9070d862d1556770f83d1628049958053d285b856b311835
- proc_pid_stat.html 0f04d78946538fd84db1536845abeb236da51a04844989f34ea7ee7cb0b6700f; proc_pid_stat.txt 77075e7c99db630a7f5a8d216fd907024eaeadb5bf6972a202e2f0cf7d34fa73
- proc_pid_exe.html 8c9bf02f95a93763ca8bc46a2e165c1c0e173658124e97d4e3d407d0a0b5afdc; proc_pid_exe.txt e09ea5dd6e68c5ccdf8f54312829ecbfb413ed64357c951ae333bea51f2f1b8f

Pages checked, with footer `Linux man-pages 6.19  2026-02-08` on each: proc_pid_cwd(5), proc_pid_fd(5), proc_pid_wchan(5), proc_pid_status(5), proc_pid_stat(5), proc_pid_exe(5).

Negative check: the case-insensitive grep for `deleted` over the four new pages returned no lines.

Access date for each quote: 2026-10-21.

Tier A: the man7 man-pages are the same tier-A class as S068–S069 and S075–S078 (SOURCES.md rows), which the registry already admits under the same contract.

# Commands run

- `curl -sS -m 60 -L -o <page>.html -w ... https://man7.org/linux/man-pages/man5/<page>.5.html` for proc_pid_cwd, proc_pid_fd, proc_pid_wchan, proc_pid_status, proc_pid_stat, proc_pid_exe — all HTTP 200.
- `sed` tag stripping to `<page>.txt`; `sha256sum *.html *.txt`.
- `grep -n` for quote and section anchors, and `grep -i deleted` negative check.
- `wc -w` on each quote.
- Read-only: `git status --short` and `git log --oneline -3` in the lane (no mutation).
- Read: `corpus/SOURCES.md` (registry and footer), `corpus/lessons/round-19.md` (Gate), `corpus/knowledge/process-residue-observations.md`, `.ufo/waves/round-19/preregistration.txt`, `skill://godspeed`, `~/.omp/agent/RULES.md`.
- Scratch under `/var/tmp/souji-r19-ScribeSources/` removed after hashing.

Tool installs or updates: none. (curl was already present; no pacman transaction.)

# Contract compliance

- Leaf seat: no subagent spawned; no `ask`; no message to agent://all.
- Writes: this report only. `corpus/SOURCES.md` was not modified; no tools/, tests/, census/, corpus/, SCORECARD.md, LOG.md, PROVINCE.md, SKILL.md, corpus/README.md, fleet repo, sibling lane, .ufo/state/, watchdog, MANIFEST.json, scripts/, templates/, or census/operator-sweep-20261019/ touched.
- No git or jj mutation. No jj-lane.sh.
- No signal sent; no /proc/*/environ read; no secret read.
- Network: only the man7 URLs for the four named proc pages and the two recheck rows (S075/S076); no other URL opened. S079–S081 not re-opened (out of the item's named URLs).
- No live census; no fleet-reading fixture run.
- Quotes ≤25 words, each with URL, access date 2026-10-21 and a located anchor.
- Items not executed: none within this item's named scope.
- Outstanding for L1: correct the three Gate word counts (S082 15→13, S083 17→13, S085 23→18) in `corpus/lessons/round-19.md`; apply the three `teaches` corrections (S083, S084, S085) to `corpus/SOURCES.md:103-105` if you adopt the draft; re-verify S079–S081 in a separate seat if you want them grounded by a second reading.
