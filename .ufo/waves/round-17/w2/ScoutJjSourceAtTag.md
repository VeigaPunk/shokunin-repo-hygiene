STATUS: DONE — jj v0.45.1 source at the exact tag commit that the host binary reports confirms: keep refs `refs/jj/keep/<hex>` are created for commits jj writes/imports, only `jj util gc` removes them (non-head + ref older than the 2-week `keep_newer`, loose refs only), default expiry 2 weeks; lane carries 17 live loose keep refs.

# Scope
Source item: `lib/src/git_backend.rs` and `cli/src/commands/util/gc.rs` at tag `v0.45.1`. No lane code was judged here; C3 bearings are advisory.

# Provenance (observed)
- `~/.local/bin/jj --version` → `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`
- `git ls-remote https://github.com/jj-vcs/jj 'refs/tags/v0.45.1*'` →
  `7c41cdeb16b6b321c64e789a966b6adf723816a5	refs/tags/v0.45.1`
  Tag commit == host commit (full 40-hex match). The raw files below are therefore the host's own code, not a nearby release.
- Fetched to `/var/tmp/souji-r17-ScoutJjSourceAtTag/`:
  `95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69  git_backend.rs` (2610 lines)
  `9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b  gc.rs` (67 lines)
- No tools installed; no pacman use.

# 1. Keep refs are created for commits jj creates (observed)

Verbatim quotes (line numbers are the tagged files):

| Where | Quote |
|---|---|
| `git_backend.rs:99` | `/// Ref namespace used only for preventing GC.` |
| `git_backend.rs:100` | `const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";` |
| `git_backend.rs:868-869` | ``Returns `RefEdit` that will create a ref in `refs/jj/keep` if not exist.`` / ``Used for preventing GC of commits we create.`` |
| `git_backend.rs:871` | `let name = format!("{NO_GC_REF_NAMESPACE}{id}");` |
| `git_backend.rs:1463-1466` | `Everything up to this point had no permanent effect on the repo except` / `GC-able objects` then `.edit_reference(to_no_gc_ref_update(&id))` |
| `git_backend.rs:493-498` | `Create no-gc ref even if known to the extras table. Concurrent GC` / `process might have deleted the no-gc ref.` |

Two creation sites, exactly matching the doc comment:
- `write_commit`: every commit jj writes gets `refs/jj/keep/<commit-id>` before the extra-metadata table is saved (`git_backend.rs:1463-1474`). This is precisely D4's "commits we create".
- `import_head_commits`: every imported git head gets one too, unconditionally — even if extras already know it, because a concurrent GC may have deleted it (`git_backend.rs:481-498`).
- Creation edit is idempotent: `PreviousValue::ExistingMustMatch(new)` (`git_backend.rs:873`), reflog message `used by jj` (`:877`).
- These refs are invisible to jj's own ref model: `diff_refs_to_import` scans only `local_branches()`, `remote_branches()`, `tags()` (`lib/src/git.rs:939-966`), i.e. `refs/heads/*`, `refs/remotes/*`, `refs/tags/*`. `refs/jj/keep` is never imported as a bookmark or head.

# 2. What removes them (observed)

| Where | Quote |
|---|---|
| `git_backend.rs:900-901` | ``Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other`` / `unreachable and non-head refs.` |
| `git_backend.rs:924-927` | `let name_good = ... == id.hex();` / `if new_heads.contains(&id) && name_good {` … keep |
| `git_backend.rs:929-932` | `Check timestamp of loose ref, but this is still racy on re-import` / `because:` / `- existing packed ref won't be demoted to loose ref` / `- existing loose ref won't be touched` |
| `git_backend.rs:938-945` | `let loose_ref_path = ...` / `if mtime > keep_newer {` / `not deleting new` |
| `git_backend.rs:947-948` | `Also deletes no-gc ref of random name created by old jj.` |
| `git_backend.rs:959-965` | `no_gc_refs_to_delete.into_iter().map(to_ref_deletion),` … one batch `edit_references` |
| `git_backend.rs:1558-1564` | `fn gc(&self, index: &dyn Index, keep_newer: SystemTime)` … `new_heads = index.all_heads_for_gc()` … `recreate_no_gc_refs(&git_repo, new_heads, keep_newer)?;` |
| `lib/src/default_index/composite.rs:636-638` | `fn all_heads_for_gc(...)` → `Ok(Box::new(self.commits().all_heads()))` |
| `lib/src/default_index/composite.rs:403-415` | `all_heads_pos` marks every parent; `filter(move |&pos| !not_head.get(pos))` — graph heads only |

Deletion edit is `Change::Delete { expected, log: LogRefLog::AndReference }` (`git_backend.rs:888-897`).

So the removal predicate is: **delete unless (commit ∈ index graph heads) OR (loose ref file mtime > keep_newer)**; a packed keep ref has no loose file, so it gets no mtime grace (`:931`). This is executed only from `GitBackend::gc`, and `gc` is reached only through `jj util gc` (`cli/.../util/gc.rs:62-65` calls `repo.op_store().gc(...)` and `repo.store().gc(...)`). In the inspected files there is no other call site: `run_git_gc(` appears once (`:1575`) and `fn gc(` once (`:1558`). No automatic/periodic GC path exists in these sources.

After the ref batch, `gc` runs `git gc` (`:1575-1580`), and then notes `Since "git gc" will move loose refs into packed refs, in-memory packed-refs cache should be invalidated without relying on mtime.` (`:1581-1583`). That packing is exactly what destroys the mtime grace described at `:929-932`.

# 3. Default expiry (observed)

| Where | Quote |
|---|---|
| `gc.rs:34-35` | `By default, only obsolete objects and operations older than 2 weeks are` / `pruned.` |
| `gc.rs:54-58` | `None => SystemTime::now() - Duration::from_secs(14 * 86400),` / `Some("now") => SystemTime::now() - Duration::ZERO,` / `_ => Err(... "--expire only accepts 'now'")` |
| `gc.rs:28-29` | `To garbage-collect old operations and the commits/objects referenced by` / `them, run `jj op abandon ..<some old operation>` before `jj util gc`.` |
| `git_backend.rs:976-977` | `.arg("gc")` / `.arg(format!("--prune=@{} +0000", keep_newer.as_secs()))` |

`keep_newer` is one single value threaded into all three sinks (op store, commit store/refs, `git gc --prune`), so "2 weeks" applies to operations, keep refs, extras, and loose-object pruning alike. `--expire=now` sets it to `now`, which both deletes every non-head keep ref (no ref can have mtime > now) and passes `--prune=@now`. Local `man git-gc`: `Prune loose objects older than date (default is 2 weeks ago, overridable by the config variable gc.pruneExpire)` — jj overrides that default explicitly with `--prune=@<epoch> +0000`.

# 4. Live corroboration (observed, read-only)
Lane `/home/vgpnk/Projects/shokunin/souji-shokunin` (gitdir `.git`, `refs/heads/master` = `d7e648d5a1931e6dbacfd5be0587547afee15de3`):
- `git -C … for-each-ref refs/jj` → 17 refs, all `refs/jj/keep/<hex>` with matching object ids; 17 loose files under `.git/refs/jj/keep/`, 0 entries in `packed-refs`.
- All 17 objects resolve (`git cat-file -e`: 17/17 present).
- `5fa6017ddcae9f6bd4412df44765f6360cb16294` (round base) is an ancestor of head → an interior commit, yet it holds a keep ref (mtime `2026-10-20 12:42:34 -0300`). So keep refs also cover commits that are not graph heads; those are exactly the ones retained only by the 2-week mtime grace. `ddb7347…` (round-17 landing) likewise holds one, mtime `2026-10-20 14:22:08`.
- Fleet root `/home/vgpnk/Projects/shokunin` has 0 `refs/jj` refs (plain git).

# 5. Bearing on C3 (advisory)
- (a') `for-each-ref --exclude='refs/jj/'` for live roots is **consistent** with jj's own model: refs/jj/* is deliberately not a branch namespace and is never imported (`git.rs:939-966`). **Holds.**
- (b') the `jj_keep_novel` rationale **holds** at source level: a commit held only by `refs/jj/keep` is a real object kept alive by a real git ref, so deletion at the target path is observable and must be checked by content, not by live-ref visibility. Caveat: this holding state is *not durable* — the ref is deleted at the first `jj util gc` after the commit stops being an index graph head, and after one gc the refs are packed so the mtime grace no longer applies; only then does `--prune` reach the objects (and `--expire=now` reaches immediately). C3 text that implies keep refs persist indefinitely should be tightened.
- "Dead shadowed sites untouched", repo-root unpushed count unchanged: no bearing in these sources either way.

# 6. Unresolved / inference
- [INFERENCE] Whether gix actually writes a reflog for `refs/jj/keep` deletion (`LogRefLog::AndReference` is requested at `:893`). If it does, git's default `gc.reflogExpireUnreachable` (30 days, per local `man git-gc`) could keep pruned objects alive past jj's 2-week date. Not executed, not verified.
- [INFERENCE] `all_heads()` covers every commit in the index (including retained hidden commits); the source shows graph-head computation, not view filtering, so a retained-but-hidden head keeps its ref.
- Not executed (no ALLOWED-EXEC for it): any `jj util gc`, `git gc`, or gc fixture. All claims above are static source + read-only observation.

# 7. Smallest fix
None for the three asked facts. For C3 wording: replace "held only by refs/jj/keep … persists" with the exact predicate — *deleted by `jj util gc` when the commit is not an index graph head and the loose ref's mtime is older than `keep_newer` (2 weeks); packed refs get no grace* — citing `git_backend.rs:900-968`, `:1558-1564`, `gc.rs:54-58`.

# Commands actually run (outputs summarized above)
- `~/.local/bin/jj --version`
- `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs` (+ `cli/.../util/gc.rs`, `lib/src/git.rs`, `lib/src/default_index/{mod,composite,readonly,mutable}.rs`)
- `git ls-remote https://github.com/jj-vcs/jj 'refs/tags/v0.45.1*'`
- `grep -n 'NO_GC_REF_NAMESPACE\|refs/jj/keep\|recreate_no_gc_refs\|run_git_gc\|fn gc(' git_backend.rs`
- `sed -n` over `:92-105,448-500,860-975,970-1045,1455-1475,1556-1600` and `gc.rs` (cat -n)
- `git -C … for-each-ref refs/jj`, `for-each-ref refs/heads`, `cat-file -e` ×17, `merge-base --is-ancestor`, `stat`, `ls .git/refs/jj/keep`, `grep -c refs/jj/keep .git/packed-refs`
- `man git-gc | col -b | grep -n -i 'prune\|reflog'` (local git 2.53 man page)
- `sha256sum git_backend.rs gc.rs`
