# ScoutWorktreeDoc — round 24 wave 1

Seat: L1Souji24.ScoutWorktreeDoc (scout, read-only). Lane rev read: f9db2181647d91470a724a12d626bd6106805076.
Access date for all web sources: 2026-10-25 (fetched 09:19:55 UTC per the HTTP `date` header).

## Status

STATUS: PASS. Every requested quote was located on the live page and in the installed git 2.56.0 man page. All quotes are 25 words or fewer and contain no pipe characters. A scratch probe confirms the empty `refs` directory these quotes explain. The docs do not explain why an *empty* `refs/` is created eagerly. That remains an open gap; see Finding 6.

## Evidence

| item | value |
|---|---|
| live git-worktree | https://git-scm.com/docs/git-worktree. Banner: `git-worktree last updated in 2.56.0`. Version list shows `2.56.0 2026-09-28`. HTTP 200, `last-modified: Fri, 23 Oct 2026 13:46:13 GMT`. HTML sha256 fa25690b04900cfc1f1b52bb6b23a85d63f8b763477cca71e655434adbfc63d2 |
| live gitrepository-layout | https://git-scm.com/docs/gitrepository-layout. Banner: `gitrepository-layout last updated in 2.49.0`. HTML sha256 ad7b52fb48738c259c8c9097edafc4ef2cf01248beedf1755c83b99a5fe3c64c |
| installed man | `/usr/share/man/man1/git-worktree.1.gz` (`pacman -Qo`: `owned by git 2.56.0-1`), footer `Git 2.56.0 2026-09-27`, sha256(zcat) 2330c8c8…32408. `/usr/share/man/man5/gitrepository-layout.5.gz`, footer `Git 2.56.0 2026-09-27`, sha256(zcat) 2cc8adf8…6fa |
| `git --version` | `git version 2.56.0` |
| quote check | `python3 -B` normalized whitespace and joined man-page hyphenation (`‐` + newline), then tested each quote for substring membership. Result: 13/13 quotes found in both the web text and the man text. Max quote length 19 words. None of the 13 quotes contains a pipe character. |
| probe (scratch `/var/tmp/souji-r24-ScoutWorktreeDoc/probe`, `GIT_CONFIG_GLOBAL=/dev/null`) | `git init` + empty commit + `git worktree add ../l`. `find .git/worktrees/l` lists `commondir gitdir HEAD index logs/HEAD ORIG_HEAD refs`, and `refs` is empty. `rev-parse --git-path refs/bisect/x` returns `…/m/.git/worktrees/l/refs/bisect/x`. `--git-path refs/heads/main` returns `…/m/.git/refs/heads/main`. `count-objects -v` in the linked worktree prints `warning: garbage found: …/m/.git/worktrees/l/refs` and `garbage: 1`. `--show-ref-format` returns `files`. |

## Findings

1. **git-worktree § REFS (live 2.56.0; man identical).** Pseudo-refs are per-worktree, and three `refs/` namespaces are carved out as per-worktree:
   - "In general, all pseudo refs are per-worktree and all refs starting with refs/ are shared." (§ REFS, para 2)
   - "There are exceptions, however: refs inside refs/bisect, refs/worktree and refs/rewritten are not shared." (§ REFS, para 2)

2. **git-worktree § REFS: where those per-worktree refs live on disk.** They live inside the linked worktree's private dir under `$GIT_COMMON_DIR/worktrees/<id>/refs/…`:
   - "worktrees/foo/HEAD or worktrees/bar/refs/bisect/bad are the same as $GIT_COMMON_DIR/worktrees/foo/HEAD and $GIT_COMMON_DIR/worktrees/bar/refs/bisect/bad." (§ REFS, para 4; in the man text this wraps as `work‐ trees/bar`, a hyphenation artifact only)
   - "To access refs, it’s best not to look inside $GIT_DIR directly." (§ REFS, last para)

3. **git-worktree § DETAILS: the private dir is the linked worktree's `$GIT_DIR`.** Only the three exception namespaces resolve against it:
   - "Each linked worktree has a private sub-directory in the repository’s $GIT_DIR/worktrees directory." (§ DETAILS, para 1)
   - "Within a linked worktree, $GIT_DIR is set to point to this private directory (e.g. /path/main/.git/worktrees/test-next in the example)" (§ DETAILS, para 2)
   - "since refs are shared across all worktrees, except refs/bisect, refs/worktree and refs/rewritten." (§ DETAILS, para 3, `--git-path` example)

4. **gitrepository-layout § `refs` (live "last updated in 2.49.0"; man 2.56.0 identical).** This is the layout-level statement of the same rule:
   - "This directory is ignored (except refs/bisect, refs/rewritten and refs/worktree) if $GIT_COMMON_DIR is set and "$GIT_COMMON_DIR/refs" will be used instead."
   - § `common`: "most of files in $GIT_DIR are per-worktree with a few known exceptions."

5. **gitrepository-layout § `worktrees` and `worktrees/<id>`.** The page lists exactly three per-id files: `gitdir`, `locked` and `config.worktree`. The man page lists the same three.
   - § `worktrees`: "Contains administrative data for linked working trees. Each subdirectory contains the working tree-related part of a linked working tree."
   - § `worktrees/<id>/gitdir`: "A text file containing the absolute path back to the .git file that points to here."
   - § `worktrees/<id>/locked`: "If this file exists, the linked working tree may be on a portable device and not available."
   - § `worktrees/<id>/config.worktree`: "Working directory specific configuration file."
   - The page does **not** list `worktrees/<id>/refs`, `HEAD`, `index`, `commondir`, `logs/HEAD` or `ORIG_HEAD`, although the probe shows all of them on disk.

6. **Why the private gitdir carries `refs`.** This conclusion combines the docs with the probe. Because of Findings 3 and 4, a linked worktree's `$GIT_DIR` is `<common>/worktrees/<id>`, and `refs/bisect`, `refs/worktree` and `refs/rewritten` resolve to `$GIT_DIR/refs/…` rather than to `$GIT_COMMON_DIR/refs`. The probe's `--git-path refs/bisect/x` confirms this mapping. So `worktrees/<id>/refs` is the documented home of per-worktree refs, not debris.
   - Gap: neither page says that `worktree add` creates `refs/` eagerly and leaves it empty. [INFERENCE] The eager creation comes from the files-backend initialization of the per-worktree ref store. This was not traced in source; it would need `builtin/worktree.c` and `refs/files-backend.c` at v2.56.0.
   - The `garbage: 1` and `warning: garbage found: …/worktrees/<id>/refs` output from `count-objects -v` in a linked worktree is therefore a false positive against documented layout. This is consistent with the preregistration's design probe and with case 4 `linked`.

7. **Version skew.** git-worktree's live page and installed man page are both 2.56.0 and match on every quoted sentence. The web version list dates 2.56.0 as 2026-09-28; the man footer says 2026-09-27, a one-day difference with no textual effect. gitrepository-layout's live banner says it was last changed in 2.49.0, and the installed 2.56.0 man page matches it on every quoted sentence, so it is unchanged since 2.49.0.

## Remaining unknowns

- Not traced: the source location that creates the empty `worktrees/<id>/refs` directory (Finding 6). Grep-only, no LSP. Not attempted, because it is out of this item's doc scope.
- Reftable-format repositories were not probed. The `refs` layout under `worktrees/<id>` may differ there (`--show-ref-format` was `files`).

Tools installed: none. Scratch `/var/tmp/souji-r24-ScoutWorktreeDoc/` removed before finishing.
