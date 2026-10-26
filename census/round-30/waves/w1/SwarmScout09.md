# SwarmScout09 — jj v0.45.1 gc path vs jj-colocation-receipts.md

## Status

STATUS: PASS — the full gc call chain (CLI, op store, backend, index) was read at tag v0.45.1 and every asked question is answered with line numbers and quotes. Nothing was executed against jj; behaviour claims below are source-reading only, and the few inferences are labelled `[INFERENCE]`.

## Evidence

Sources downloaded on 2026-10-26 with `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/<path>` into scratch, then read with line numbers (awk NR). Lane revision read for the corpus lines: working tree of /home/vgpnk/Projects/shokunin/souji-shokunin (read-only, `jj-colocation-receipts.md` as opened this run).

| file at v0.45.1 | lines | sha256 |
|---|---|---|
| lib/src/git_backend.rs | 2610 | 95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69 |
| cli/src/commands/util/gc.rs | 67 | 9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b |

Also opened (same tag): lib/src/index.rs, lib/src/default_index/composite.rs, lib/src/default_index/store.rs, lib/src/operation.rs, lib/src/view.rs, lib/src/op_store.rs, lib/src/simple_op_store.rs, lib/src/backend.rs, lib/src/store.rs, cli/src/commands/operation/abandon.rs, lib/Cargo.toml.

Tooling installed: none.

Call chain (all line numbers at v0.45.1):
`jj util gc` (`cli/src/commands/util/gc.rs:43-66`) -> `repo.op_store().gc(...)` (`:62-64`) then `repo.store().gc(repo.index(), keep_newer)` (`:65`) -> `Store::gc` (`lib/src/store.rs:255-257`) -> `GitBackend::gc` (`git_backend.rs:1558-1583`) -> `recreate_no_gc_refs` (`:902-968`), extra-metadata store gc (`:1571-1573`), `run_git_gc` (`:970-989`).

## Findings

1. **What `keep_newer` is.** A `SystemTime` made in the CLI, never a ref or commit property.
   - `gc.rs:55`: `None => SystemTime::now() - Duration::from_secs(14 * 86400),`
   - `gc.rs:56`: `Some("now") => SystemTime::now() - Duration::ZERO,`
   - `gc.rs:57`: `_ => return Err(user_error("--expire only accepts 'now'")),` — so the only flag value is `now`; there is no other expiry.
   - `gc.rs:49-53`: refuses on a non-head operation ("Cannot garbage collect from a non-head operation").
2. **What `keep_newer` is compared to (keep refs).** The filesystem mtime of the loose ref file under the git dir.
   - `git_backend.rs:938`: `let loose_ref_path = git_repo.path().join(git_ref.name.to_path());`
   - `git_backend.rs:940-941`: `let mtime = metadata.modified().expect("unsupported platform?");` then `if mtime > keep_newer {` — the ref is kept (`:942-944`, "not deleting new").
   - It is not the commit's author/committer time and not the git reflog.
3. **Which keep refs are recreated.** Every id in `new_heads` gets `to_no_gc_ref_update` in the same transaction as the deletions.
   - `git_backend.rs:959-962`: `no_gc_refs_to_delete.into_iter().map(to_ref_deletion),` chained with `new_heads.iter().map(to_no_gc_ref_update),`
   - `:963-965`: one `git_repo.edit_references(ref_edits)` call for both, so a missing or wrongly named head ref is recreated. The root commit is filtered out first (`:1563`: `.filter(|id| *id != self.root_commit_id)`).
   - Doc comment `:900-901`: "Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other unreachable and non-head refs."
4. **Which keep refs are deleted.** Any `refs/jj/keep/*` ref that is NOT (a head with the correct name) AND NOT (loose file newer than `keep_newer`).
   - Keep test: `git_backend.rs:924-928`: `let name_good = git_ref.name.as_bstr()[NO_GC_REF_NAMESPACE.len()..] == id.hex();` and `if new_heads.contains(&id) && name_good {` then `continue`.
   - Everything else falls to `:949`: `no_gc_refs_to_delete.push(git_ref);`. The comment at `:947` says "Also deletes no-gc ref of random name created by old jj."
   - **A ref with no loose file is deleted regardless of age.** The mtime test is `if let Ok(metadata) = loose_ref_path.metadata() {` (`:939`). When the stat fails (a packed ref has no loose file) the block is skipped and the ref is pushed for deletion at `:949`. `git gc` packs refs afterwards (`:1581-1583`, comment: "Since "git gc" will move loose refs into packed refs"). So after one gc a non-head keep ref that exists only in `packed-refs` is deleted at the next gc even if the commit is newer than the threshold. The source comment names this race: `:929-932`: "Check timestamp of loose ref, but this is still racy on re-import because: - existing packed ref won't be demoted to loose ref". [INFERENCE for the "next gc" timing: the control flow is read, not run.]
   - `--expire now`: `keep_newer` = now, so `mtime > keep_newer` is false for every existing loose file; every non-head keep ref is deleted regardless of age.
   - Deletion uses `RefLog::AndReference` (`:893`), so the ref's reflog goes with it.
5. **What "head" means (the key point).** Not the visible heads. `all_heads_for_gc` returns the heads among ALL indexed commits, and the index covers every commit referenced by any operation in the history.
   - `lib/src/index.rs:141-145`: "Heads among all indexed commits at the associated operation. Suppose the index contains all the historical heads and their ancestors reachable from the associated operation, this function returns the heads that should be preserved on garbage collection."
   - `lib/src/default_index/composite.rs:636-638`: `all_heads_for_gc` returns `self.commits().all_heads()`; `:403-415` define it as every indexed commit that is not a parent of another indexed commit.
   - `lib/src/default_index/store.rs:267-277` builds the index from `op.all_referenced_commit_ids()` and `op.view().await?.all_referenced_commit_ids()` of each operation, including predecessors (`lib/src/operation.rs:141-146`: "The predecessor commit ids are also included, which ensures that the old commits to be returned by ... are still reachable.").
   - `lib/src/view.rs:589-591`: "This can include hidden commits referenced by remote bookmarks, previous positions of conflicted bookmarks, etc."
   - Consequence: a hidden commit whose operation is still in the op log is an index head (or an ancestor of one) and keeps its keep ref. `jj util gc` only prunes after `jj op abandon` makes the commit unreachable from the op history, as the CLI doc says (`gc.rs:28-29`: "run `jj op abandon ..<some old operation>` before `jj util gc`"; `abandon.rs:40-43`: "Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history"). This turns corpus §3 line 31's `[INFERENCE]` into a sourced mechanism. That index shrinks correctly after an abandon is NOT read from source here (`store.rs:241-262` reuses a parent op's index only when `op_links_dir.join(op.id().hex()).is_file()`); `[INFERENCE]` that `op abandon` rewrites op ids so the rebuilt index drops abandoned commits. This is C3's measurement target, not settled by reading.
6. **Can a keep ref for a commit still reachable from a visible head be removed?** The ref can be; the commit's protection cannot be lost through this path in the same gc.
   - A visible head X is in `view.head_ids`, so it is in the index (`view.rs:604-612` lists `head_ids` first). X is either an index head (then kept, `:925-927`, and recreated, `:961`) or a strict ancestor of an index head Y (e.g. a hidden child still in the op log). In the second case X's own keep ref is not in `new_heads`, so it is deleted unless its loose file is newer than `keep_newer` (`:949`); X stays reachable through Y's keep ref, which is recreated in the same `edit_references` batch (`:959-965`) before `git gc` runs (`:1575`).
   - So: "removed ref, retained commit" is possible; "commit lost while a visible head needs it" is not, as far as the code shows. The same gc keeps parent-linked ancestors because git reachability follows commit parents. [INFERENCE: parent edges are git parents for all commits in the index; shallow roots and conflict-tree commits (doc comment at `:1588`, `.jjconflict-*` subtrees) were not traced.]
   - Concurrency guard: `lib/src/backend.rs:877-881`: "objects created after `keep_newer` will be preserved. This mitigates a risk of deleting new commits created concurrently by another process." Two other writers also recreate: `git_backend.rs:493-494` "Create no-gc ref even if known to the extras table. Concurrent GC process might have deleted the no-gc ref." (import path, `:497`) and `:1463-1467` (write_commit).
7. **What is passed to git, and how.** jj shells out; it does not use git2 or gix for the gc itself, and it does not call `git prune`.
   - `git_backend.rs:974`: `let mut git = Command::new(program);`
   - `:975-977`: `git.arg("--git-dir=.") // turn off discovery`, `.arg("gc")`, `.arg(format!("--prune=@{} +0000", keep_newer.as_secs()));`
   - `:980`: `git.current_dir(git_dir);` and `:983`: `let status = git.status().map_err(GitGcError::GcCommand)?;` (stdout/stderr inherited; `:981` TODO "pass output to UI layer"). Non-zero exit becomes `GitGcError::GcCommandErrorStatus` (`:985-987`).
   - `program` is `self.git_executable` (`:1576`), set from `git_settings.executable_path` (`:223`), and `git_dir` is `self.git_repo_path()` = `self.base_repo.path()` (`:415-417`, `:1577`). The same `keep_newer` that gated the keep refs becomes the prune date, so the two clocks are one value.
   - Ref edits and the extras table use gix (`use gix::...` at `:41-46`, `edit_references` at `:497, 964`). `grep -n git2 git_backend.rs` finds one hit, `:1715` `temp_dir.path().join("git2")`, a test directory name; `lib/Cargo.toml` has only `gix` dependency lines (`:38-39`) and no `git2` line in the grep of that file.
   - Other stores: `op_store().gc` removes operation and view files whose mtime is not newer than `keep_newer` (`lib/src/simple_op_store.rs:286-298`: `if mtime > keep_newer {` keep else `fs::remove_file`), and `extra_metadata_store.gc(&table, keep_newer)` at `git_backend.rs:1571-1573`. The git gc is the last step; ref deletion precedes it.

## What the corpus entry already says (jj-colocation-receipts.md)

Quoted from the file as opened this run (line numbers are file lines):
- `:30` (§3): "Keep refs for current heads are kept. Other keep refs are deleted when their loose-ref file is older than the threshold." and cites `git_backend.rs:1558-1564`, `:902-953`, `:928-937`, `gc.rs:55`.
- `:31` (§3): `[INFERENCE]` "a commit hidden by a rewrite keeps its keep ref until its operation is abandoned, `jj util gc` runs, and the ref is older than the threshold."
- `:84` (§10): "There's no garbage collection and repacking of Jujutsu's own data structures yet" (S051 docs).
- `:86` (§10): "jj's `util gc` runs `git gc --prune=@<keep_newer>` (`lib/src/git_backend.rs@v0.45.1:977`), so the two prune clocks are linked".
- `:108` (Limits): "**Keep-ref lifetime.** The docs read do not state it. The timing in §3 is an inference from source and from observed keep-ref counts."
- `:122` (Limits, ungoverned residue): "`util gc` pruning of hidden keep-held commits (Limits, first bullet)."
- `:137` (S054): cited line list `:100, 497, 868-870, 902-953, 928-937, 977, 1466, 1558-1564` and `gc.rs:55, 65`.

## ALREADY HELD versus NEW ground

Already held (confirmed correct against the source read): namespace `refs/jj/keep/` at `:100`; `to_no_gc_ref_update` at `:868-870`, called at `:497` and `:1466`; gc entry `:1558-1564` calling `recreate_no_gc_refs` with `all_heads_for_gc()`; 14-day default at `gc.rs:55`; `git gc --prune=@<keep_newer>` at `:977` and the shared clock; `op abandon` precondition from the CLI doc; the "still racy" comment (corpus cites `:928-937`, the comment is `:929-937`, one line off); the `[INFERENCE]` that hidden commits keep their ref until op abandon plus gc plus age.

NEW ground (not in the entry; each with its source line):
- N1. `--expire` accepts only `now`, and `now` makes `keep_newer` the present instant: every non-head keep ref is deleted regardless of age (`gc.rs:54-58`, `git_backend.rs:941`). The entry never mentions `--expire`.
- N2. The `keep_newer` comparison target is the loose ref FILE mtime (`git_backend.rs:938-941`), not a commit date. The entry says "loose-ref file is older" but never says what happens without a loose file.
- N3. A non-head keep ref with no loose file (packed) is deleted with no age test (`:939` `if let Ok(metadata)` falls through to `:949`). The entry's "deleted when their loose-ref file is older than the threshold" is incomplete for packed refs, which `git gc` creates (`:1581-1583`). This is a refinement of line 30, not a contradiction.
- N4. The definition of "head": heads among all indexed commits from the operation history, including predecessors, not the visible heads (`index.rs:141-145`, `composite.rs:398-415, 636-638`, `default_index/store.rs:267-277`, `operation.rs:141-146`, `view.rs:589-595`). This turns the §3 `[INFERENCE]` mechanism into a sourced one; the timing end-to-end stays `[INFERENCE]` until measured.
- N5. Recreate and delete happen in ONE `edit_references` batch (`:959-965`); head refs with a missing or wrong-name entry are recreated; wrong-name refs are deleted (`:924, 947`); reflogs are deleted with the ref (`:893`). The entry cites `:902-953`, which stops before the actual edit at `:958-965`.
- N6. A visible head's own keep ref can be deleted while the commit stays protected through a descendant index head's ref; a commit needed by a visible head is not left unprotected by the same gc (ref batch before `git gc`, `:959-965` before `:1575`).
- N7. Process facts: jj shells out with `Command::new(program)`, `--git-dir=.` plus `gc` plus `--prune=@<secs> +0000`, cwd = git dir, output inherited (`:974-983`); gix (not git2, not `git prune`) does the ref edits; `program` comes from git settings `executable_path` (`:223, 1576`). The entry says "runs `git gc --prune=@<keep_newer>`" but not the argv, the shell-out, or that git2 is absent.
- N8. The same `keep_newer` also gates op-store files (`simple_op_store.rs:286-298`) and the extras table (`git_backend.rs:1571-1573`); the gc refuses to run from a non-head operation (`gc.rs:49-53`).

## Unresolved (for the C3 measurement, not settled here)

- U1. `[INFERENCE]` that after `jj op abandon` the rebuilt index excludes the abandoned commits so that the next `jj util gc --expire now` deletes their keep refs. Measure: scratch jj 0.45.1 repo; count `refs/jj/keep/*` before and after `op abandon` plus `util gc --expire now`, and with default expiry.
- U2. Whether a packed keep ref (after one `git gc`) is deleted at the next default-expiry gc while the commit is newer than 14 days (N3). Measure with `git pack-refs --all` in the fixture, then `jj util gc` without `--expire`.
- U3. Which git dir `base_repo.path()` resolves to in a colocated repo (`:415-417`; `canonicalize_git_repo_path` near `:285-300` was not traced).
- U4. git-gc docs for the prune/unpack-unreachable semantics were not opened in this seat; corpus S063 already carries them.

## Deliveries

None beyond this report. Scratch `/fast/scratch/hyaku/souji-r30/SwarmScout09/` held only downloaded source copies; removed before finishing (see the final check below).
