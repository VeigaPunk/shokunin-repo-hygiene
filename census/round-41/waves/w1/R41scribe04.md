# R41scribe04 — S258 registry row draft (round 41, wave 1, role scribe)

Date: 2026-10-28. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. No commit, push, or mutating git/jj command was run. Scratch dir /fast/scratch/hyaku/souji-r41/R41scribe04 was removed after the receipts below were copied here.

## Deliverable

- Draft row + Gate: `.ufo/waves/round-41/w1/R41scribe04/S258-row.md`
- Upstream receipts (byte copies, hash-checked): `.ufo/waves/round-41/w1/R41scribe04/receipts/` (`SHA256SUMS`)

## Fetched sources (git tag v2.56.0 and v2.55.0)

Fetch command (all four succeeded, curl exit 0):

```
curl -fsSL --max-time 60 -o worktree.c https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c
curl -fsSL --max-time 60 -o worktree-v2.55.0.c https://raw.githubusercontent.com/git/git/v2.55.0/builtin/worktree.c
curl -fsSL --max-time 60 -o lib-worktree-v2.56.0.c https://raw.githubusercontent.com/git/git/v2.56.0/worktree.c
curl -fsSL --max-time 60 -o lib-worktree-v2.55.0.c https://raw.githubusercontent.com/git/git/v2.55.0/worktree.c
```

`sha256sum` output (after `wc -l`: 1541, 1493, 1139, and the v2.55.0 library file):

```
af2bd523c1e89e33d5e370941321fa3c3567c50cf44104e2b502f009e298babc  builtin-worktree.v2.56.0.c   (1541 lines)
2c8e8a8ee6a6ee346e226116fb5cc08cb76785dcb1ced76a824ba2a1d46ce884  builtin-worktree.v2.55.0.c   (1493 lines)
da5c259a2c78724ac776ad4c21a493f24008ac24d3023f33d30034269b353ff2  worktree.v2.56.0.c           (1139 lines)
65caa125b7f5d96a9b9ee38bddc4f7522f6b262cb5db451ae1dd422193eef64c  worktree.v2.55.0.c
```

`sha256sum -c receipts/SHA256SUMS`: all four `OK`.

## Gate quote

- Line 255 of builtin/worktree.c at v2.56.0: `prune missing working trees older than <time>` (inside `N_("...")`, the `prune --expire` help string).
- Command: `grep -n -F 'prune missing working trees older than <time>' worktree.c` → `255: N_("prune missing working trees older than <time>")),`; `grep -c -F` → `1`.
- Access date 2026-10-28; URL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/worktree.c.

## Anchor (tag v2.56.0), verified by `sed -n` on the fetched files

- builtin/worktree.c: `prune_worktrees()` :212-246; `should_prune_worktree(the_repository, d->d_name, &reason, &path, expire)` at :229; `prune()` option `--expire` :254-255; `expire = TIME_MAX` :259; `prune_worktrees();` :264.
- worktree.c (library): `worktree_prune_reason` :329-345; `should_prune_worktree` signature :937; `strbuf_addf(&file, "%s/locked", ...)` :966, `if (file_exists(file.buf)) {` :967, `goto done;` :968; `if (stat(file.buf, &st) || st.st_mtime <= expire) {` :1016, `strbuf_addstr(reason, _("gitdir file points to non-existent location"));` :1017.

## Finding: the prunable decision is not in builtin/worktree.c

The spec asked for an anchor on "the function that decides a registration is prunable". In builtin/worktree.c that decision is only delegated: `prune_worktrees()` calls `should_prune_worktree()` (:229), and the list path calls `worktree_prune_reason()` (:1036, :1078). The decision bodies (locked-file skip, gitdir-target test, index-mtime expiry) are in the library worktree.c. The row therefore lists both files in its source cell, cites the library lines from the fetched library file, and names the builtin lines as the caller. The Gate quote is from builtin/worktree.c only. Library line claims were checked by `sed -n` and `grep -n` on the fetched library file, but they have no Gate quote of their own.

## What v2.56.0 adds or re-pins versus S009 (v2.55.0)

- `diff -u builtin-worktree.v2.55.0.c builtin-worktree.v2.56.0.c` restricted to prune/expire/lock/should_prune hunks: one change, the call at :229 now passes `the_repository` (v2.55.0 :229 had no repo argument). Line 229 and the `expire = TIME_MAX` line (259) did not move.
- Library `should_prune_worktree`: v2.55.0 signature `(const char *id, ...)` at :929; v2.56.0 `(struct repository *repo, const char *id, ...)` at :937. A diff of the function bodies (v2.55.0 :929-1024 vs v2.56.0 :937-1032) shows only the repo parameter threading and the rename `repo` → `repo_path`; locked check, gitdir test, and index-mtime expiry are unchanged in content.
- Pins S009 cites at v2.55.0 (`worktree.c:954-956`, `:1001-1008`) match the v2.55.0 library file (locked check at :954-956; expiry test at :1004-1005 inside the :1001-1008 block). At v2.56.0 they are at :966-968 and :1016-1017, each +12 lines.

## Commands run and observed output (abridged, exact text kept where quoted)

- `grep -n -E 'prune|expire|lock|prunable|should_prune|is_worktree_locked' worktree.c` (fetched builtin file): hits at :171-264 (prune code), :1025-1082 (list porcelain/human prunable), :1138 (`add 'prunable' annotation to missing worktrees older than <time>`).
- `grep -n -E 'should_prune_worktree|worktree_prune_reason|worktree_lock_reason' worktree.c` → only :229 (should_prune_worktree), :329, :1025, :1036, :1072, :1078, :1203, :1239, :1339, :1451 — no should_prune definition in builtin.
- `grep -n -E 'should_prune_worktree|worktree_prune_reason|worktree_lock_reason' lib-worktree-v2.56.0.c` → :305 worktree_lock_reason, :329 worktree_prune_reason, :339 call, :937 definition.
- `grep -n -E '"%s/locked"|expire|TIME_MAX|prune_reason' lib-worktree-v2.56.0.c` → :966 (locked path), :1016 (`st_mtime <= expire`).
- `grep -n -E '"%s/locked"|st_mtime <= expire|^int should_prune_worktree|gitdir file points to non-existent' lib-worktree-v2.55.0.c` → :929, :954, :1004, :1005.
- `grep -n -E 'should_prune_worktree\(|expire = TIME_MAX|prune_worktrees\(\);' worktree-v2.55.0.c worktree.c` → v2.55.0 :229 without repo, :259, :264; v2.56.0 :229 with `the_repository`, :259, :264.
- `grep -n -F "add 'prunable' annotation" worktree.c` → :1138 (one match).
- Row check (python, 11 cells, `|` split): `cells: 11 ids: S258 status: mined tier: A`, run after the final edit.

## Row and Gate (summary)

- id S258; source `git/git source at tag v2.56.0: builtin/worktree.c, worktree.c — https://github.com/git/git/blob/v2.56.0/builtin/worktree.c`; kind code; tier A; scope excludes S001/S009 (trigger), S232 (list label), S003 (lock semantics); status mined; opened 2026-10-28; recheck on-release; used-by corpus/lessons/round-41.md (that lesson file does not exist yet; the L1 creates it).
- Corpus-contract notes checked against `/home/vgpnk/Projects/shokunin/CORPUS.md` § SOURCES.md: 11 columns; no `|` in cells; `S` + next unused id (S257 is the last row in corpus/SOURCES.md; S258 unused); not a correction, so no `supersedes` opener is required (rule 2).

## Path notes

- CORPUS.md is not under the lane; it is at /home/vgpnk/Projects/shokunin/CORPUS.md. The section was read there.
- Rows S009 and S232 were read in full from /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md at lines 38 and 185.

## Verdict

PASS for the drafted row and the upstream bytes: the v2.56.0 file was fetched, its sha256 recorded, the quote located once at line 255, and the anchors checked against the fetched bytes. Caveat: the spec's named gate function is in the library worktree.c (see Finding). Nothing was installed; the tools used were curl, sha256sum, grep, sed, diff, and python3 (preinstalled).
