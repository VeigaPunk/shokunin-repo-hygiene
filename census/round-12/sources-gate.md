# r12 SOURCES gate — per-row grounding

Author: W2RoundSouji-8.R12SourcesExec2. Date: 2026-10-19. Contract rule 1 requires, for every new row in `corpus/SOURCES.md`, the URL, the access date, and a quote of 25 words or fewer with its location that grounds `teaches`. Each entry below also says whether the W1 ART dossier claim (`kaika-w1/souji-art.md` §3–§4) agrees or differs.

How the quotes were taken:
- **Man pages** are quoted from the roff source of the installed page, with roff escapes rendered: `\-` becomes `-` and `\&` is dropped. Line numbers are roff source lines. Each copy was checked with `zcat /usr/share/man/<sect>/<page>.gz | cmp -`.
- **HTML pages** are quoted from tag-stripped text.

Scratch downloads are in `/var/tmp/souji-r12-MvtJYK/`. Reused sibling copies are listed in `corpus/SOURCES.md` § Search log, each with its byte comparison.

Host versions: `pacman -Q` reports git 2.55.0-1, git-filter-repo 2.47.0-3, findutils 4.11.0-1, coreutils 9.11-2 and shellcheck 0.11.0-158.

## S001 — git-maintenance(1)
- URL: https://git-scm.com/docs/git-maintenance (live page fetched; it reports 2.56.0). Row anchor: installed 2.55.0 page. Accessed 2026-10-19.
- Quote, § CONFIGURATION › maintenance.strategy › geometric (roff :591 and the following entry): "The strategy expires data in the reflog and removes worktrees that cannot be located anymore." … "This is the default strategy for manual maintenance."
- ART: agrees.

## S002 — git-gc(1)
- URL: https://git-scm.com/docs/git-gc. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § OPTIONS --prune (roff :113): "--prune=now prunes loose objects regardless of their age and increases the risk of corruption if another process is writing to the repository concurrently"
- ART: agrees. `gc.worktreePruneExpire` is at roff :333-340 ("calls git worktree prune --expire 3.months.ago"). The reflog defaults (90 and 30 days) are at :346 and :352; the rerere defaults (60 and 15 days) at :399 and :407.

## S003 — git-worktree(1)
- URL: https://git-scm.com/docs/git-worktree. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § COMMANDS lock (roff :167): "lock it to prevent its administrative files from being pruned automatically. This also prevents it from being moved or deleted."
- ART: agrees. The `-z` porcelain text is at roff :596 ("If -z is given then the lines are terminated with NUL rather than a newline").

## S004 — git-repack(1)
- URL: https://git-scm.com/docs/git-repack. Accessed 2026-10-19. Sources: the installed 2.55.0 page, and `Documentation/git-repack.adoc` at tag v2.56.0, byte-identical to master on that date.
- Quote, § OPTIONS --expire-to (installed, roff :132): "This option is useful for keeping a copy of any pruned objects in a separate directory as a backup."
- ART: agrees.
- `--drop-filtered` exists only at v2.56.0 (adoc :186-220): "refuses to drop any blob that the current index references". It is absent from the host's 2.55.0.

## S005 — git-repo(1)
- URL: https://git-scm.com/docs/git-repo. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § COMMANDS structure --format table (roff :166): "This format may change and is not intended for machine parsing."
- ART: agrees. Roff :44 reads "THIS COMMAND IS EXPERIMENTAL". The report bullets (refs, reachable counts, inflated size, disk size, largest objects) are listed after roff :103.

## S006 — git(1)
- URL: https://git-scm.com/docs/git. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § ENVIRONMENT GIT_OPTIONAL_LOCKS (roff :2195-2200): "this will prevent git status from refreshing the index as a side effect"
- ART: agrees.

## S007 — git-clean(1)
- URL: https://git-scm.com/docs/git-clean. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § DESCRIPTION (roff :57): "Git will refuse to modify untracked nested git repositories (directories with a .git subdirectory) unless a second -f is given."
- ART: agrees.

## S008 — git-last-modified(1)
- URL: https://git-scm.com/docs/git-last-modified. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § DESCRIPTION (roff :41): "Shows which commit last modified each of the relevant files and subdirectories."
- ART: agrees on content. The ART note "(2.52+)" was not re-verified this session, so it is omitted from the row.

## S009 — git/git source at v2.55.0
- URL: https://github.com/git/git/blob/v2.55.0/builtin/gc.c (tag v2.55.0 = 5ce91c0). Accessed 2026-10-19.
- Byte check: the local `gc.c`, `worktree.c`, `run-command.c` and `commit.c` copies each pass `cmp` against `raw.githubusercontent.com/git/git/v2.55.0/<path>`.
- Quote, builtin/gc.c:1974-1975: "strategy = geometric_strategy; type = MAINTENANCE_TYPE_MANUAL;"
- Quote, worktree.c:1004: "if (stat(file.buf, &st) || st.st_mtime <= expire) {"
- ART: differs in wording only, per the reviewer preflight. The geometric table entries for worktree-prune and reflog-expire are `MAINTENANCE_TYPE_SCHEDULED | MAINTENANCE_TYPE_MANUAL` with WEEKLY schedule (gc.c:1912-1919). `--auto` runs as type MANUAL and selects them (gc.c:1975, :1989). The task is at gc.c:379-389 (ART says 379-388) and the condition at :391-427 (ART says 391-420). Conclusion unchanged.
- Other call sites:
  - `builtin/commit.c:1965` holds `run_auto_maintenance`.
  - am.c, fetch.c, merge.c and rebase.c at v2.55.0 each hold one call (`grep -c run_auto_maintenance` → 1 each).

## S010 — Git release notes
- URL: https://github.com/git/git/tree/master/Documentation/RelNotes. Accessed 2026-10-19.
- Revisions:
  - 2.50.0–2.54.0: byte-identical to master.
  - 2.55.0: matches tag v2.55.0.
  - 2.56.0: matches tag v2.56.0.
- Quote, 2.54.0.adoc:58: " * "git maintenance" starts using the "geometric" strategy by default."
- ART: agrees. ART status was `watch`; the contract has no such value, so it became `queued`, and the row is now `mined` per the K1 plan.

## S011 — Git BreakingChanges
- URL: https://git-scm.com/docs/BreakingChanges. The adoc was fetched at master c514088. Accessed 2026-10-19.
- Quote, § Git 3.0 › Changes (BreakingChanges.adoc:219-220): "The default value of `safe.bareRepository` will change from `all` to `explicit`."
- ART: agrees. ART `watch` became `queued`.

## S012 — git-filter-repo(1)
- URL: https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt (main d7b75ac). Accessed 2026-10-19.
- Quote, :418: "Every time filter-repo is run, files are created in the `.git/filter-repo/` directory."
- ART: agrees. Line :97 reads "Will not modify your repo." Lines :582-584 read "It is a really bad idea to get in the habit of always specifying `--force`".

## S013 — git-sizer README
- URL: https://github.com/github/git-sizer (README at master 56a6df5). Accessed 2026-10-19.
- Quote, README.md:176: "If you'd like the output in machine-readable format, including exact numbers, use the `--json` option."
- Release date: the v1.5.0 release page shows `datetime="2021-11-16T16:14:39Z"`.
- ART: agrees. ART `watch` became `queued`.

## S014 — GitLab blog, What's new in Git 2.53.0
- URL: https://about.gitlab.com/blog/whats-new-in-git-2-53-0/ ("Published on: February 2, 2026", Justin Tobler). Accessed 2026-10-19.
- Quote: "The intent of this command was to collect information about the repository and eventually become a native replacement for tools such as git-sizer(1)"
- ART: agrees. The source is community, so it stays tier B.

## S015 — GitHub Docs, Removing sensitive data
- URL: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository. Accessed 2026-10-19.
- Quote, § About removing sensitive data from a repository: "as a first step you need to revoke and/or rotate that secret."
- ART: agrees. ART `watch` became `queued`.

## S016 — rmlint(1)
- URL: https://github.com/sahib/rmlint/blob/master/docs/rmlint.1.rst (master 3a44e63; the local copy passes `cmp`). Accessed 2026-10-19.
- Quote, rmlint.1.rst:28: "``rmlint`` itself WILL NOT DELETE ANY FILES."
- ART: agrees.

## S017 — rmlint docs, Cautions
- URL: https://rmlint.readthedocs.io/en/latest/cautions.html (page says rmlint 2.11.0). Accessed 2026-10-19.
- Quote, § Consider safe removal options: "Rather than deleting duplicates, consider moving them to a holding area or trash folder."
- ART: differs on tier only, A → B. This is the rmlint project describing failure modes of other tools (fdupes demo under Symlinks). That makes it a strong secondary with reproducible detail, not a primary for those tools. Content agrees.

## S018 — jdupes README
- URL: https://codeberg.org/jbruchon/jdupes (README at master d198306; the local copy passes `cmp`).
- Release: the Codeberg API reports v1.31.2 published 2026-09-02T15:16:04+02:00. Accessed 2026-10-19.
- Quote, README.md:249-250: "The `-t`/`--no-change-check` option disables file change checks during/after scanning. This opens a security vulnerability that is called a TOCTTOU"
- ART: agrees.

## S019 — fdupes(1)
- URL: https://github.com/adrianlopezroche/fdupes/blob/master/fdupes.1 (byte-identical at tag v2.4.0, released 2025-03-30, and master a7c1da4). Accessed 2026-10-19.
- Quote, fdupes.1:131-132 and § CAVEATS :175-176: "Log file deletion choices to LOGFILE." … "a user could accidentally preserve a symlink while deleting the file it points to."
- ART: agrees.

## S020 — fclones README
- URL: https://github.com/pkolaczk/fclones/blob/main/fclones/README.md (main a74f90d; the local copy passes `cmp`). Accessed 2026-10-19.
- Quote, README.md:22: "There is also a `--dry-run` option that can tell you exactly what changes on the file system would be made."
- ART: agrees.

## S021 — fclones src/dedupe.rs
- URL: https://github.com/pkolaczk/fclones/blob/main/fclones/src/dedupe.rs. Tag v0.35.0 and main are byte-identical. Accessed 2026-10-19.
- Quote, dedupe.rs:844-845: "We need to skip the whole group, because we don't know if these files are really different. if let Some(max_timestamp) = config.modified_before {"
- ART: differs. ART says "aborts a group if any file changed after the report". The code does two things:
  - Non-regular files (:814-824) and length-changed files (:826-841) are skipped one at a time.
  - The whole group aborts only when `config.modified_before` is set (:843-847).

## S022 — FreeDesktop.org Trash Specification
- URL: https://specifications.freedesktop.org/trash/latest/ ("Publication Date: 2014-01-02, Version: 1.0"). Accessed 2026-10-19.
- Quote, § 5 and § 6: "The implementation also MUST check that this directory is not a symbolic link." … "MUST create the corresponding file in $trash/info first."
- ART: agrees. § 6 also says "opening with O_EXCL" and "each subsequent trashing must not overwrite a previous copy".

## S023 — trash-cli README
- URL: https://github.com/andreafrancia/trash-cli (README.rst at master bfb1595; release 0.26.9.29 shows `datetime="2026-09-29T20:32:57Z"`). Accessed 2026-10-19.
- Quote, README.rst:122-125: "Can I alias `rm` to `trash-put`? … You can but you shouldn't."
- ART: agrees.

## S024 — GNU coreutils, rm invocation
- URL: https://www.gnu.org/software/coreutils/manual/html_node/rm-invocation.html (page title "GNU Coreutils 9.12"; host 9.11). Accessed 2026-10-19.
- Quote, § 11.5 --preserve-root: "When ‘all’ is specified, reject any command line argument that is not on the same file system as its parent."
- ART: agrees. The host's `/usr/bin/rm --help` lists `--one-file-system` and `--preserve-root[=all]`.

## S025 — GNU coreutils, mv invocation
- URL: https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html (GNU Coreutils 9.12). Accessed 2026-10-19.
- Quote, § 11.4: "mv falls back on copying as if by cp -a, then (assuming the copy succeeded) it removes the original."
- ART: agrees.

## S026 — find(1)
- Source: installed `man find`, /usr/share/man/man1/find.1.gz, owned by findutils 4.11.0-1. Accessed 2026-10-19.
- Quote, § ACTIONS -delete (roff :1270-1277): "As in turn -depth makes -prune ineffective, the -delete action cannot usefully be combined with -prune."
- ART: agrees.

## S027 — ShellCheck wiki SC2115
- URL: https://github.com/koalaman/shellcheck/wiki/SC2115 (wiki HEAD d9486e5). Accessed 2026-10-19.
- Quote, SC2115.md § Rationale (link markup removed): "If `STEAMROOT` is empty, this will end up deleting everything in the system's root directory."
- ART: agrees. Local run on shellcheck 0.11.0:
  - Input: `printf '#!/bin/bash\nrm -rf "$X/"*\n'` piped to `shellcheck`.
  - With `-S error`: rc=0, no output.
  - At default severity: rc=1, with "SC2115 (warning)".

## S028 — GitLab postmortem of January 31
- URL: https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/ ("Published on: February 10, 2017"). Accessed 2026-10-19.
- Quote: "Unfortunately this process was executed on the primary instead." … "When we went to look for the pg_dump backups we found out they were not there."
- ART: agrees. The page also says "around 300 GB of data had already been removed".

## S029 — Google SRE book ch. 26
- URL: https://sre.google/sre-book/data-integrity/. Accessed 2026-10-19.
- Quote, § First Layer: Soft Deletion: "Common choices of soft deletion delays are 15, 30, 45, or 60 days."
- ART: differs. ART says "lazy deletion behind it". The text reads "The first layer is soft deletion (or "lazy deletion" in the case of developer API offerings)", which makes lazy deletion another name for soft deletion, not a later layer. The second layer is backups.

## S030 — OneNine (rejected)
- URL: https://onenine.com/how-to-reduce-git-repository-size-safely/. Accessed 2026-10-19.
- Quote: "running git gc --aggressive --prune=now on a monthly basis helps keep your repository in check"
- ART: agrees. The page also offers "git filter-branch – Built into Git – Well-documented Suitable for simpler tasks". It contradicts:
  - S002 roff :113 (`--prune=now` corruption risk);
  - S002 :153 ("probably not worth it" for `--aggressive` without benchmarks);
  - S032.

## S031 — r12 maintenance guard fixture (own-work)
- Path: `tests/fixtures/r12-maintenance-guard.sh`. Result: `tests/results/r12-maintenance-guard.txt`, generated 2026-10-19T21:53:39Z on git 2.55.0. Opened 2026-10-19.
- Quote, result :11 and :13: "case=plain-commit-sync before=2 after=1 expect=1 verdict=PASS" … "case=auto-off before=2 after=2 expect=2 verdict=PASS"
- ART: this confirms C1's falsifying fixture. It also settles what ART §4 C1 left as [INFERENCE] about the detached HEAD. Result :36-40 shows the commit with no ref and no reflog entry, listed by fsck as unreachable. It is still present after `gc --prune=2.weeks.ago` and absent after `--prune=now`.

## S032 — git-filter-branch(1) (rejected)
- URL: https://git-scm.com/docs/git-filter-branch. Accessed 2026-10-19 (installed 2.55.0, `cmp` match).
- Quote, § WARNING (roff :46): "git filter-branch has a plethora of pitfalls that can produce non-obvious manglings of the intended history rewrite … its use is not recommended."
- ART: agrees with ART §6 item 1, which was not a §3 row there and is new here. PROVINCE.md § Refuses: "Git history rewrite in any repo … — operator-owned".

## S033 — gitrepository-layout(5)
- URL: https://git-scm.com/docs/gitrepository-layout. Accessed 2026-10-19 (installed 2.55.0, `cmp` match).
- Quote, § worktrees/<id>/locked (roff :387-392): "The presence of this file prevents worktrees/<id> from being pruned either automatically or manually by git worktree prune."
- ART: agrees with the ART lead. New in this round: the page has no `worktrees/<id>/index` entry; the 3 per-id entries are gitdir, locked and config.worktree. Yet `worktree.c:1001-1008`@v2.55.0 ages registrations by that file.

## Omitted
None. All 30 ART rows were opened this session.
