# R41w2scout02 — S009 recheck recon: git `worktree.c` v2.55.0 → v2.56.0

Seat: R41w2scout02 (scout, wave 2, falsify). Report-only; no candidate landed. Lane tip at fetch time: `1d41c13574db80fdd9a4bde490b712da7ce2a85f`. Date: 2026-10-28.

## Question
S009 (corpus/SOURCES.md:38) pins `worktree.c:954-956` (lock test) and `:1001-1008` (expiry test) at git tag v2.55.0, recheck pending. Did those cited lines move or change in v2.56.0?

## Commands run (all in /fast/scratch/hyaku/souji-r41/R41w2scout02/, deleted after receipts copied)

```
mkdir -p /fast/scratch/hyaku/souji-r41/R41w2scout02
curl -fsSL -o worktree-v2.55.0.c https://raw.githubusercontent.com/git/git/v2.55.0/worktree.c
curl -fsSL -o worktree-v2.56.0.c https://raw.githubusercontent.com/git/git/v2.56.0/worktree.c
sha256sum worktree-v2.55.0.c worktree-v2.56.0.c
wc -l worktree-v2.55.0.c worktree-v2.56.0.c
diff -u worktree-v2.55.0.c worktree-v2.56.0.c > worktree.diff; echo "diff exit: $?"; wc -l worktree.diff
```

Observed output:
```
65caa125b7f5d96a9b9ee38bddc4f7522f6b262cb5db451ae1dd422193eef64c  worktree-v2.55.0.c
da5c259a2c78724ac776ad4c21a493f24008ac24d3023f33d30034269b353ff2  worktree-v2.56.0.c
 1125 worktree-v2.55.0.c
 1139 worktree-v2.56.0.c
diff exit: 1   (1 = differences found)
557 worktree.diff
```

Line pins below come from `grep -n` / ranged reads of the two fetched files (raw content, not semantic tooling).

## Findings

**1. Both cited regions MOVED +12 lines; statement text is logically unchanged.**

| S009 citation (v2.55.0) | v2.56.0 location | Content |
|---|---|---|
| `worktree.c:954-956` (lock test) | **worktree.c:966-968** | `strbuf_addf(&file, "%s/locked", repo_path.buf);` / `if (file_exists(file.buf)) {` / `goto done;` — a `locked` file still short-circuits pruning. |
| `worktree.c:1001-1008` (expiry test) | **worktree.c:1013-1020** | `if (!file_exists(dotgit.buf)) {` … `if (stat(file.buf, &st) \|\| st.st_mtime <= expire) {` … — dangling gitdir still prunable only when the per-worktree index is missing or `mtime <= expire`. |

Only in-region textual change: local strbuf renamed `repo` → `repo_path` (e.g. `repo.buf` → `repo_path.buf`); no logic token differs. Verbatim quote, v2.56.0 line 1016 (12 words): `if (stat(file.buf, &st) || st.st_mtime <= expire) {`. Companion quote, v2.56.0 line 1017: `strbuf_addstr(reason, _("gitdir file points to non-existent location"));` (8 words).

**2. The enclosing function's signature DID change (API-level drift).**

- v2.55.0:929: `int should_prune_worktree(const char *id, struct strbuf *reason, char **wtpath, timestamp_t expire)` (4 params; body used implicit `the_repository`).
- v2.56.0:937-941: `int should_prune_worktree(struct repository *repo, const char *id, struct strbuf *reason, char **wtpath, timestamp_t expire)` (5 params; `the_repository` uses replaced by the new `repo` parameter).
- In-file caller updated: v2.55.0:337 `should_prune_worktree(wt->id, …)` → v2.56.0:339 `should_prune_worktree(wt->repo, wt->id, &reason, &path, expire)`.
- Same conversion hits `move_config_setting` (v2.56.0:1031-1032 adds `struct repository *repo`) and other `repo_common_path*(the_repository, …)` call sites across the file (e.g. v2.55.0:417 → v2.56.0:419 now `repo_common_path_replace(wt->repo, …)`).

**3. Diff shape.** 40 hunks, file 1125 → 1139 lines; the +12 offset at the lock test accumulates from earlier hunks (header −1, `get_worktrees`/worktree-struct region +2, plus small shifts) and +4 from the 1-line → 5-line signature. Hunks touching the cited function: `@@ -926,12 +934,16 @@`, `@@ -941,17 +953,17 @@`, `@@ -995,12 +1007,12 @@`, `@@ -1012,17 +1024,18 @@`. Full diff receipt: `worktree-v2.55.0-to-v2.56.0.diff` (seat dir, 557 lines); hashes: `sha256.txt` (seat dir).

## Cross-reference
Landed S258 (registry row, corpus/SOURCES.md:212) re-pins only the builtin half (`builtin/worktree.c` v2.56.0) and explicitly defers the library half: "the library's eligibility test `should_prune_worktree()` lives in worktree.c and is not read here". This recon supplies exactly that library half at v2.56.0: same two tests, new line numbers, changed signature.

## Verdict
The lock/expiry eligibility logic S009 cites is **semantically unchanged** between v2.55.0 and v2.56.0, but the **line citations are stale at v2.56.0** (`:954-956` → `:966-968`; `:1001-1008` → `:1013-1020`) and the function **signature changed** (explicit `struct repository *repo`). A v2.56.0 re-pin of S009's library half is warranted if the L1 opens a row; nothing in this diff falsifies the r41 C1–C3/r1 claims. [INFERENCE on consequence only; all line/hash facts above observed.]
