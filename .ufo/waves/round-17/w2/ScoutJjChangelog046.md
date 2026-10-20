STATUS: DONE — 35 entries in CHANGELOG 0.36.0→0.46.0 touch the five axes; `refs/jj/keep` and `snapshot.auto-track` have **zero** changelog entries in range, and the keep-ref source is unchanged at v0.46.0, so the knowledge entry's 0.45.1 grounding HOLDS for those; HEAD is PARTIAL (per-worktree HEAD + colocated child workspaces are new) and one entry quote is mis-scoped.

# Scope and method

- Entry under test: `corpus/knowledge/jj-colocation-receipts.md` (uncommitted draft, not in ddb7347). Line refs `entry:N` are that file.
- Changelog under test: `CHANGELOG.md` at tag `v0.46.0` (`7d382314f9420b4b8d932245b49c99492c812b9f`), fetched raw, 5807 lines, sha256 `54ee00e57a9bdf652204f0f31458a62af0b39e42f3dbd54f8d547cb212719caf`. Read the whole 0.36.0–0.46.0 span (lines 21–1585), then term-scanned every line of it.
- Every `L<n>` below is `CHANGELOG.md@v0.46.0` unless another file is named. The `Unreleased` section (L9–20) is outside the asked range and is reported separately in §6.
- Source checks at both tags: `lib/src/git_backend.rs`, `cli/src/commands/util/gc.rs` (v0.45.1 and v0.46.0), plus `core/src/backend.rs`, `lib/src/store.rs` at v0.46.0.
- Docs checks: `https://docs.jj-vcs.dev/latest/{git-compatibility,config,technical/concurrency,bookmarks,working-copy}/`, fetched 2026-10-20.
- No `jj` command was run (not in ALLOWED-EXEC). No tools installed or upgraded.

# 1. Direct answer

**Is the entry's 0.45.1 grounding stable on 0.46.0?** For the two sharpest claims — `refs/jj/keep/*` semantics (§3, §4, §10 of the entry) and `snapshot.auto-track` (§6) — **yes, stable**, on three independent checks:

1. `grep -n 'refs/jj' CHANGELOG.md@v0.46.0` → **no matches** (0 occurrences in the entire file, not just the range). `grep -n 'snapshot.auto-track'` → exactly one occurrence, L3482, inside **0.22.0** (the option's introduction). No changelog entry 0.36.0→0.46.0 announces a change to either.
2. Source at v0.46.0 is the same algorithm: `lib/src/git_backend.rs@v0.46.0:100` `const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";`; creation at `:867-895`; `recreate_no_gc_refs` at `:899-968`; gc calls it at `:1566-1572`. `diff -u` of the file v0.45.1→v0.46.0 is 23 hunks, all gix-API/error-type churn; the **only** hunk inside the keep-ref region is the error wrapping at old `:918` (`.map_err(|err| BackendError::Other(err.into()))`), and the **only** hunk at `gc` is visibility/doc:
   ```diff
   -    fn gc(&self, index: &dyn Index, keep_newer: SystemTime) -> BackendResult<()> {
   +    pub fn gc(&self, index: &dyn Index, keep_newer: SystemTime) -> BackendResult<()> {
   ```
   `cli/src/commands/util/gc.rs@v0.46.0:65-68` still invokes it (`git_backend.gc(repo.index(), keep_newer)?`). Structural shift worth knowing: `Backend::gc` no longer exists in the moved `core/src/backend.rs`, and `lib/src/store.rs` no longer has a `gc` wrapper — the git backend's inherent `gc` is now the only path. Behaviour for a receipt's git store is identical.
3. Docs at `latest` still carry the entry's sentence verbatim: "Commits created by jj have a ref starting with refs/jj/ to prevent GC." (`grep -c 'refs/jj/'` on the page = 1).

So no counterexample exists for the keep-ref or auto-track claims in the changelog record. The rest of this report lists every in-range hit and the three places where the entry's *framing* needs tightening.

# 2. Every in-range entry that touches an axis

Axes: **A** `refs/jj/keep` · **B** git HEAD/detached · **C** git index in colocated repos · **D** nested `.git`/`.jj` · **E** `snapshot.auto-track`.

| # | Ver | Line | Ax | Quote (≤25 words) | Bearing |
|---|---|---|---|---|---|
| 1 | 0.46.0 | L25-27 | B | "Jujutsu can now colocate workspaces besides the default one by creating Git worktrees." (15) | Child workspaces get their own Git worktree → own HEAD. Entry §2/§9 assume one HEAD. |
| 2 | 0.46.0 | L31-33 | B | "The minimum supported `git` command version is now 2.42.0, up from 2.41.0." (12) | Host git 2.56.0, no exposure; receipts shelling to older git would be. |
| 3 | 0.46.0 | L57-61 | B | "`jj workspace forget` removes the corresponding Git worktree when one exists." (11) | Lifecycle of jj-created Git worktrees; `git worktree list` consumers see them. |
| 4 | 0.46.0 | L63-67 | B | "`jj git colocation status`/`enable`/`disable` now work on child workspaces." (9) | Colocation is now toggleable per child workspace, not just the root. |
| 5 | 0.46.0 | L69-70 | E* | "The working-copy state is snapshotted into a commit before removal." (10) | `jj workspace remove` now snapshots; adjacent to auto-track, not the config. |
| 6 | 0.46.0 | L144-147 | E* | "`.gitignore` files are now respected even if they aren't materialized in the working copy because they are excluded by the sparse patterns." (21) | Changes which files can become tracked; moot under `auto-track="none()"`. |
| 7 | 0.46.0 | L149-153 | D*/E* | "In-tree ignore files (`.gitignore`) are no longer read through symlinks, matching `git` behavior." (13) | `$GIT_DIR/info/exclude` unaffected; no bearing on nested `.git`. |
| 8 | 0.45.0 | L221-222 | B | "`jj git import` in non-colocated repositories no longer imports commits from a detached Git HEAD branch." (16) | Non-colocated only; the entry governs colocated. No conflict. |
| 9 | 0.45.0 | L239-242 | B | "Git HEAD state is now tracked per worktree internally." (9) · "This prepares colocated repositories for support of multiple Git worktrees" (11) | HEAD is no longer repo-global. Entry §2/§9 do not say this. |
| 10 | 0.45.0 | L264-265 | E* | "A side of a conflict … no longer loses that byte when … snapshotted from the working copy." (16) | Snapshot fidelity only. |
| 11 | 0.45.0 | L267-269 | B | "In colocated workspaces, `jj workspace update-stale` now correctly resets the Git HEAD to the parent of the fresh working-copy commit." (22) | Confirms HEAD rewriting on stale-update; receipts must not cache HEAD across jj calls (entry §9 already says this). |
| 12 | 0.45.0 | L280-283 | C | "In colocated repos, an external `git add` after a `jj` command no longer produces a tree with duplicate entries" (20) · "`jj` was leaving a stale cache-tree behind in `.git/index`." (10) | jj writes `.git/index`; entry §5's "index is not a signal" is reinforced. |
| 13 | 0.44.0 | L418-420 | C | "Git temporary files are now cleaned up more reliably in the presence of signals (e.g. `Ctrl-C`)." (17) | Index-lock recovery; no semantic change. |
| 14 | 0.44.0 | L420 | C | "This should reduce the rate of \"Could not acquire lock for index file\" errors." (14) | Same. |
| 15 | 0.44.0 | L423 | B | "Fixed Git HEAD mismatch after the working copy became immutable." (11) | HEAD repair; no claim in the entry is contradicted. |
| 16 | 0.44.0 | L426-428 | E | "`jj` now creates a new working-copy revision as soon as the one of the current workspace becomes immutable, as well as during snapshotting." (23) | Snapshot creates WC revisions; auto-track rule unaffected. |
| 17 | 0.44.0 | L430-432 | E | "Snapshotting no longer fails if the working copy contains a path whose name isn't valid UTF-8." (18) | Snapshot robustness only. |
| 18 | 0.44.0 | L451-452 | B/C | "`jj git import` and `export` in colocated workspaces are now disabled by default." (14) | The *commands* are disabled; automatic import/export still runs (docs quote in entry §1 holds). |
| 19 | 0.43.0 | L505-506 | B | "The deprecated `git_head()` and `git_refs()` functions have been removed from revsets and templates." (15) | Revset/template access to git HEAD is gone; helper uses neither. |
| 20 | 0.43.0 | L508-509 | B | "Git-like symbols (e.g. `refs/heads/main`) are no longer resolved to revisions." (11) | jj cannot resolve git ref names; receipts use git for refs (entry §3 rule), consistent. |
| 21 | 0.43.0 | L549-553 | D | "This identity check is used when writing the working copy to detect aliases of the reserved `.git` and `.jj` directories." (22) | jj actively guards `.git`/`.jj` aliasing; supports entry §7. |
| 22 | 0.43.0 | L556-558 | E | "`jj` now creates a new working-copy revision during snapshotting if the working copy was immutable." (16) | Snapshot timing only. |
| 23 | 0.41.0 | L691-694 | E* | "The new global flag `--no-integrate-operation` will let you run a command without impacting the repo state or the working copy" (23) | A jj call can be made snapshot-free; adjacent to the entry's rule 1. |
| 24 | 0.41.0 | L753-754 | E | "Improved performance for snapshotting, visibly improving `jj status` speed for large repositories." (12) | Performance only. |
| 25 | 0.39.0 | L919-920 | E | "`jj debug snapshot` is deprecated in favor of `jj util snapshot`." (10) | Command name. |
| 26 | 0.39.0 | L964-967 | C | "Changed Git representation of conflicted commits to include files from the first side of the conflict." (16) | Colocated checkout representation; index/working-copy display only. |
| 27 | 0.39.0 | L973-975 | E | "Added new `jj util snapshot` command to manually or programmatically trigger a snapshot." (13) | Command name. |
| 28 | 0.39.0 | L978-979 | E | "Changed background snapshotting to suppress stdout and stderr to avoid long hangs." (12) | Observability only. |
| 29 | 0.39.0 | L1009-1010 | B | "`jj` now safely detaches the `HEAD` of alternate Git worktrees if their checked-out branch is moved or deleted during Git export." (24) | jj actively manages HEAD of *other* worktrees; multi-worktree model predates 0.46. |
| 30 | 0.38.0 | L1057-1060 | E* | "Per-repo and per-workspace config is now stored outside the repo, for security reasons." (14) · "`.jj/repo/config.toml` and `.jj/workspace-config.toml` should no longer be used." (10) | The `auto-track` setting moved out of `.jj/`; `jj config --repo` is the supported accessor. |
| 31 | 0.38.0 | L1132-1134 | B | "`jj git init --colocate` now refuses to run inside a Git worktree, providing a helpful error message with alternatives." (19) | Guard rail; no bearing on receipts. |
| 32 | 0.37.0 | L1267-1270 | B | "`git_head()` should point to the `first_parent(@)` revision in colocated repositories." (12) | Documents which commit git HEAD means; entry §2's `@-` inference aligns. |
| 33 | 0.37.0 | L1298-1299 | A* | "`jj util gc` now prunes unreachable files in `.jj/repo/store/extra` to save disk space." (15) | GC touches jj store, not keep refs; no removal-path change. |
| 34 | 0.37.0 | L1350-1352 | D | "Fixed checkout of symlinks pointing to themselves or `.git`/`.jj` on Unix." (12) | jj checks out such symlinks; nested-dir handling adjacent. |
| 35 | 0.36.0 | L1399-1403 | B* | "Fixed race condition that could cause divergent operations when running concurrent `jj` commands in colocated repositories." (16) | Local colocated concurrency declared safe — see F1. |
| 36 | 0.36.0 | L1439-1441 | D | "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored." (13) · "Git submodules are unaffected" (4) | The policy behind the entry's observed phantom deletions; unchanged through 0.46. |

`*` = adjacent, not the exact named subject (e.g. `auto-track-bookmarks` vs `snapshot.auto-track`; jj's own index vs `.git/index`; GC of the jj store vs keep refs; local concurrency vs cross-machine sync).

Counts: **A direct 0** (+1 adjacent) · **B 12** · **C 4** (+1 adjacent) · **D 3** (+1 adjacent) · **E direct 0** (+10 adjacent).

# 3. Axis verdicts against the entry

## A. `refs/jj/keep/*` — HOLDS
- Changelog: zero mentions in the whole file. The only GC-related in-range item is 0.37.0 L1298 (prunes `.jj/repo/store/extra`), which does not touch keep refs.
- Source: identical algorithm at v0.46.0; the const, the two creation sites, the `new_heads`/mtime predicate, and the batched deletion survive verbatim apart from error-type plumbing. `jj util gc` still calls it.
- Docs: sentence unchanged.
- Consequence for the entry: §3's "keep refs are not a durable root" and §4's unpushed blind spot remain valid; the proposed `--glob=refs/jj/keep/*` rule (entry rule 5) is neither helped nor hurt by 0.46.0.

## B. git HEAD / detached — PARTIAL
- Every docs assertion the entry quotes is still present at `latest`: "detached HEAD state", "no concept of an active/current/checked-out bookmark", "will usually put the Git repo in a detached HEAD state".
- But HEAD's *scope* changed under the quote: 0.45.0 L239-242 made HEAD per-worktree, and 0.46.0 L25-27/L57-61/L63-67 made additional colocated workspaces (each with a Git worktree and its own HEAD) a supported, user-creatable state. The entry §2 and §9 speak of "the Git repo in a detached HEAD state" and "pin an explicit commit"; both stay true for the workspace you are in, but the entry never says HEAD is per-worktree, nor that a colocated repo can now contain jj-created Git worktrees visible to `git worktree list`.
- This is a coverage gap, not a false statement. It matters to the receipt lane: any check that enumerates worktree registrations (`git worktree list --porcelain`, `rev-list` over refs) can now see worktrees jj created, and `git rev-parse HEAD` must be taken inside the receiving worktree.

## C. Git index in colocated repos — HOLDS
- No 0.46.0 entry mentions `.git/index`; the 0.46 "index" hit (`at_operation() … operation's index`, L139-142) is jj's revset/operation index, not the git index. 0.39's "legacy index files written by jj < 0.33" (L907) is also jj's own index.
- The last index-semantics change is 0.45.0 L280-283 (stale cache-tree), already in force at 0.45.1 and unchanged on 0.46.0. Docs still say "The staging area will be ignored."
- Entry §5 remains correct and is arguably strengthened: jj writes `.git/index`, so it is neither read-only nor authoritative.

## D. Nested `.git`/`.jj` — HOLDS (with a source improvement)
- 0.36.0 L1439-1441 is the operative policy: any directory containing `.jj` or `.git` is ignored, submodules excepted. No later in-range entry relaxes or changes it (the 0.37/0.43 items are symlink/identity hardening; 0.46 L149-153 is `.gitignore` only).
- The entry §7 says the docs pages "do not describe a nested `.git` directory". That is accurate for the docs pages read, but the CHANGELOG does describe the policy, so S056 should cite `CHANGELOG.md@v0.46.0:1439-1441` instead of leaning on the submodule analogue at entry:58. The observed phantom deletions are the consequence of "ignored", and remain expected on 0.46.0.

## E. `snapshot.auto-track` — HOLDS
- The only occurrence in the whole changelog is its 0.22.0 introduction (L3482). Nothing in 0.36.0→0.46.0 changes the option, its default, or `none()` semantics.
- Docs config page still states: "All new files in the working copy that don't match the ignore patterns are tracked by default", and "If you set `snapshot.auto-track` to a non-default value, untracked files can be tracked with `jj file track`." Working-copy page still says "added files are implicitly tracked by default."
- The 0.46 `.gitignore` fixes (L144-147, L149-153) change which files *would* be tracked under `all()`, but under `none()` they are irrelevant. The entry's rule 1 is unaffected.
- One 0.38.0 consequence to keep in mind (not a defect): repo config now lives outside `.jj/`, so a receipt that greps `.jj/repo/config.toml` for `auto-track` sees nothing. The lane helper is safe: it uses `jj config set/list --repo` (`scripts/hyaku/jj-lane.sh:426`, `:519-521`), which is version-agnostic.

# 4. Secondary findings (beyond the asked list)

**F1 — FAILS (precision), the one real counterexample found.** `entry:15` labels the bullet "Colocated concurrency is untested" and quotes the technical/concurrency sentence. In the served page that sentence sits inside the section **"Syncing with rsync, NFS, Dropbox, etc"**, and its referent "such use" is *updating copies of the clone on different machines and letting rsync/Dropbox/NFS merge them*; the following sentence is "concurrent modification of a repository from different computers might conceivably lose some bookmark pointers." It is not a statement about local concurrent `jj` commands. 0.36.0 L1399-1403 states the opposite for that case: after #6830 it "is now safe to continuously run e.g. `jj log` … while you're running other commands in another terminal." Smallest fix: relabel the bullet "cross-machine sync (rsync/NFS/Dropbox) of a colocated repo is not thoroughly tested", or drop it and cite the 0.36.0 fix; keep the per-workspace caveat only for the sync scenario. (For the next hop: `Unreleased` L88-90 adds a narrower colocated race, concurrent `jj git fetch` + `jj` importing partially fetched refs, #7349 — not in 0.46.0.)

**F2 — retention is sourceable; entry:98 says it is not.** The Limits sentence claims the docs do not state how long `refs/jj/keep/*` lives. The code does define it: refs for commits not in `index.all_heads_for_gc()` are deleted unless the loose ref's mtime is newer than `keep_newer`; `jj util gc` defaults `keep_newer = now − 14 days`, `--expire now` disables the grace; packed refs get no grace (comment at `git_backend.rs@v0.46.0:928-934`), and the same gc then packs loose refs (`:1589-1590`). Cite `lib/src/git_backend.rs@v0.46.0:899-968,1566-1588` + `cli/src/commands/util/gc.rs@v0.46.0:54-68` and replace the `[INFERENCE]` retention sentence with the predicate. This also gives C3's `jj_keep_novel` a precise durability bound.

**F3 — HEAD gap (see B).** Smallest fix: add one sentence to §2 — "HEAD is per-worktree since 0.45.0; from 0.46.0 a colocated child workspace has its own Git worktree and HEAD, so resolve HEAD only inside the worktree being gated" — and one line in §9 that `git worktree list` may now contain jj-created worktrees.

**F4 — S056 wording.** Cite `CHANGELOG.md@v0.46.0:1439-1441` for the nested `.git`/`.jj` policy; retain the docs-silence statement only for the *behaviour* (phantom deletions), not the policy.

**F5 — verified non-issue.** 0.38.0 moved repo/workspace config out of the repo (L1057-1060), but the lane helper reads it via `jj config list --repo`, so its `auto-track` guard does not break on 0.46.0. No fix.

**F6 — citation path stability for S054.** `lib/src/git_backend.rs` still exists at v0.46.0 and still holds the keep-ref code, so the entry's planned `@v0.45.1` citation remains meaningful; but the `Backend` trait moved to the new `jj-core` crate (`core/src/backend.rs@v0.46.0`; `lib/src/backend.rs`/`lib/src/store.rs` no longer contain it) and `GitBackend::gc` became inherent `pub`. Any citation of "`store().gc()`" is stale on 0.46.0; cite `cli/src/commands/util/gc.rs:65-68` → `lib/src/git_backend.rs:1566`.

# 5. Not hits (coverage proof; near-misses deliberately excluded)

- `at_operation() … commits missing from the current operation's index` (0.46.0 L139-142) — jj operation/revset index.
- `Dropped support for legacy index files written by jj < 0.33` (0.39.0 L907) — jj's own index.
- `remotes.<name>.auto-track-bookmarks` / `auto-track-created-bookmarks` (0.37.0 L1237, 0.38.0 L1108, 0.36.0 L1454/L1506) — bookmark tracking, not `snapshot.auto-track`.
- 0.46.0 L129-132 (Windows `colocation enable/disable` with pack files) — OS-specific colocation conversion, no HEAD/index semantics.
- 0.46.0 L95-97 (`jj run` sparse patterns), L155-156 (workspace template labels) — workspace metadata only.
- 0.44.0 L435-436 (`config` in a copied repo with an empty repo-level config dir) — config loading, not auto-track semantics.
- 0.44.0 L326-329 (`jj git fetch` fetches tags like bookmarks; fetched tags are tracked by local tags) — changes which `refs/tags/*` a colocated repo exports, but tags remain git refs, so the entry §3 durable-roots list is unaffected. It is not a keep-ref change.
- 0.39.0 L1005-1007 (Windows file locks) — lock implementation.
- 0.42.0 — no hits in any of the five axes (read in full).
- 0.40.0 — no hits (read in full).

# 6. Unreleased (outside 0.36.0–0.46.0; matters on the next hop)

- L21-22 (breaking): "In non-colocated workspaces, `jj git fetch` no longer updates remote-tracking Git refs." Non-colocated only; no bearing on the entry.
- L88-90 (fixed): "Fix a race condition in colocated workspaces where concurrent `jj git fetch` and `jj` commands could import partially fetched refs, causing divergence. #7349". A narrower, still-live colocated race than 0.36.0's #6830; if the entry keeps any concurrency caveat, this is the accurate one today. Not present in 0.46.0.

# 7. Verdict summary

| Axis | 0.45.1 → 0.46.0 | Changelog hits (direct) | Smallest fix |
|---|---|---|---|
| `refs/jj/keep` | **holds** | 0 | none |
| HEAD / detached | **partial** | 12 | add per-worktree HEAD + `--colocate` worktrees to §2/§9 (F3) |
| git index (colocated) | **holds** | 4 | none |
| nested `.git`/`.jj` | **holds** | 3 | cite 0.36.0 L1439 in S056 (F4) |
| `snapshot.auto-track` | **holds** | 0 | none |

Overall: the entry's 0.45.1 grounding is **stable on 0.46.0** for the receipt-critical keep-ref and auto-track claims; it is **incomplete**, not wrong, on HEAD scope. One quoted caveat is mis-scoped (F1) and one "undocumented" claim is now sourceable (F2).

# 8. Commands actually run (outputs as observed)

1. `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/main/CHANGELOG.md -o jjch.md` → 5876 lines (main has extra Unreleased text).
2. `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/CHANGELOG.md -o jj46.md` → 5807 lines; sha256 `54ee00e5…719caf`.
3. `git ls-remote https://github.com/jj-vcs/jj 'refs/tags/v0.46.0*' 'refs/tags/v0.45.1*'` → `7d382314f9420b4b8d932245b49c99492c812b9f refs/tags/v0.46.0`, `7c41cdeb16b6b321c64e789a966b6adf723816a5 refs/tags/v0.45.1`.
4. `grep -n '^## \[' jj46.md` → 0.46.0 at L21, 0.45.1 L192, 0.45.0 L207, 0.44.0 L317, 0.43.0 L494, 0.42.0 L598, 0.41.0 L684, 0.40.0 L806, 0.39.0 L893, 0.38.0 L1053, 0.37.0 L1218, 0.36.0 L1389, 0.35.0 L1586.
5. `grep -n 'refs/jj' jj46.md` → no output; `grep -n 'refs/jj' jj46.md | wc -l` → `0`.
6. `grep -n 'snapshot.auto-track' jj46.md` → `3482` only (0.22.0 New features).
7. `grep -n 'auto-track' jj46.md` → bookmark-only hits at 1108, 1237, 1454, 1458, 1466, 1471, 1506, 3482.
8. `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs` / `.../v0.46.0/lib/src/git_backend.rs` → 2610 / 2619 lines; sha256 of the v0.46.0 copy `8767abb9…921f58`; `diff -u | grep '^@@'` → 23 hunks; the keep region differs only at old `:918` (error wrapping) and the gc hunk is doc + `fn`→`pub fn`.
9. `curl -fsSL .../v0.45.1/cli/src/commands/util/gc.rs` and `.../v0.46.0/...` → v0.46.0 L65-68 calls `git_backend.gc(repo.index(), keep_newer)?`; `--expire` default is `now − 14*86400` in both.
10. `curl -fsSL https://api.github.com/repos/jj-vcs/jj/contents/core/src?ref=v0.46.0` → `backend.rs` present, no `gc`; `lib/src/store.rs@v0.46.0` has no `fn gc`; `lib/src/backend.rs` and `lib/src/store/mod.rs` are 404 at v0.46.0.
11. `curl -fsSL https://docs.jj-vcs.dev/latest/git-compatibility/` → `grep -c 'refs/jj/'` = 1; text "Commits created by jj have a ref starting with refs/jj/ to prevent GC"; "Detached HEAD: Yes"; "The staging area will be ignored"; "Commits created by jj…"; "It should be safe to run `git gc` … but it's not tested"; "There's no garbage collection and repacking of Jujutsu's own data structures yet"; ".gitattributes: No"; "Hooks: No".
12. `curl -fsSL https://docs.jj-vcs.dev/latest/config/` → "All new files … are tracked by default"; "If you set `snapshot.auto-track` to a non-default value…"; "When creating a Git-backed Jujutsu repository, they use \"colocated\" mode by default"; `git.colocate` boolean.
13. `curl -fsSL https://docs.jj-vcs.dev/latest/technical/concurrency/` → the "not currently thoroughly tested" sentence is inside the section "Syncing with rsync, NFS, Dropbox, etc"; preceding sentence: "possible to update copies of the clone on different machines and then let rsync (or Dropbox, or NFS, etc.) merge them."
14. `curl -fsSL https://docs.jj-vcs.dev/latest/bookmarks/` → "There is currently no concept of an active/current/checked-out bookmark."; "When a commit has been abandoned, all associated bookmarks will be deleted."
15. `curl -fsSL https://docs.jj-vcs.dev/latest/working-copy/` → "added files are implicitly tracked by default."
16. `grep -n 'auto-track\|repo/config.toml\|workspace-config\|config edit --repo' scripts/hyaku/jj-lane.sh` → no direct `.jj/repo/config.toml` path; uses `config set --repo` (L426) and `config list --repo` (L519-521).

# 9. Unresolved / inference

- [INFERENCE] `docs.jj-vcs.dev/latest` is the "latest released version" (index page) and the latest release is 0.46.0 (2026-10-07); the pages carry no version stamp. The git-compatibility page does not mention `jj workspace add --colocate`, so docs content lags the 0.46.0 changelog for that feature. Docs-only grounding therefore cannot establish 0.46 stability; changelog + source were required.
- [INFERENCE] `jj util gc` at v0.46.0 calls `get_git_backend(repo.store())`; I did not execute it. The keep-ref recreation is static-read, not observed on 0.46.0.
- No behavioural recheck of the entry's F2/F3 sandbox sequences was run (no ALLOWED-EXEC; the contract forbids jj).
- Tooling: no installs or upgrades; scratch files live in `/var/tmp` only.
