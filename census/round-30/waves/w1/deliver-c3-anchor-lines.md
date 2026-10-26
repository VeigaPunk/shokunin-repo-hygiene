# R30 C3 — pinned source snapshots and anchor lines

Seat: `SwarmExecutor07` (item `C3Snapshots`). Wave: `souji-r30-w1`. Lane base
`9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; no lane bytes were touched by this seat.

Snapshot directory (staged for the L1 to commit as `census/round-30/sources/`):
`.ufo/waves/round-30/w1/sources/` — five files, digests in `sources/SHA256SUMS`,
per-fetch provenance in `deliver-fetch-receipts.tsv` (`snapshot` column = final committed path).
Anchor lines below were emitted by script from those exact bytes; nothing was retyped.

## Tag pins

```
jj-vcs/jj  v0.45.1  lightweight tag -> 7c41cdeb16b6b321c64e789a966b6adf723816a5
git/git    v2.56.0  tag object 2478544319491bbd2a42cc57a83e3d2f4730a280
                    -> commit a018953688f1b10bddf91bff8747068f5f4746a4
```
Commands: `git ls-remote https://github.com/jj-vcs/jj 'refs/tags/v0.45.1*'` and
`git ls-remote https://github.com/git/git 'refs/tags/v2.56.0*'`.

All four named URLs answered `200`; no substitution was needed for items 1, 2 and 4.
`cli-reference@.md.snap` is the committed, generated CLI reference at the tag; the docs
page `docs/cli-reference.md` includes it (line 16, `include-markdown
"../cli/tests/cli-reference@.md.snap"`), so the `jj op abandon` prose lives in the
snapshot, not in hand-written docs.

### Item (3) selection record

`docs/operation-log.md` was fetched at the named URL (`200`, 3334 B, 65 lines) and
**does not document `jj op abandon`**: `grep -c abandon sources/operation-log.md` -> `0`.
Recursive sweep at the tag (`grep -rn "op abandon" <tag>/docs/`, 53 `*.md` files) has
exactly one hit, `docs/working-copy.md:114`, and it is incidental ("the operation has
then been lost"). Chosen at-tag documentation for `jj op abandon` therefore: the CLI
reference snapshot (item 1), anchored below; `docs/cli-reference.md` is pinned as the
include mapping that makes that snapshot the docs page.

## 1. `sources/cli-reference@.md.snap` — jj CLI reference, v0.45.1 (154561 B, 4038 lines)

Requested anchors: `jj util gc` and its `--expire` text; `jj op abandon`. The command
surface is documented as `jj operation abandon` / `jj util gc`; the prose uses the
documented alias `jj op`.

```
2411: ## `jj operation abandon`
2412: 
2413: Abandon operation history
2414: 
2415: To discard old operation history, use `jj op abandon ..<operation ID>`. It will abandon the specified operation and all its ancestors. The descendants will be reparented onto the root operation.
2416: 
2417: To discard recent operations, use `jj op restore <operation ID>` followed by `jj op abandon <operation ID>..@-`.
2418: 
2419: Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history. The abandoned operations, commits, and other unreachable objects can later be garbage collected by using `jj util gc` command.
2420: 
2421: **Usage:** `jj operation abandon <OPERATION>`
3789: ## `jj util gc`
3790: 
3791: Run backend-dependent garbage collection.
3792: 
3793: To garbage-collect old operations and the commits/objects referenced by them, run `jj op abandon ..<some old operation>` before `jj util gc`.
3794: 
3795: **Usage:** `jj util gc [OPTIONS]`
3796: 
3797: ###### **Options:**
3798: 
3799: * `--expire <EXPIRE>` — Time threshold
3800: 
3801:    By default, only obsolete objects and operations older than 2 weeks are pruned.
3802: 
3803:    Only the string "now" can be passed to this parameter. Support for arbitrary absolute and relative timestamps will come in a subsequent release.
```
## 2. `sources/git_backend.rs` — jj 0.45.1 `lib/src/git_backend.rs` (102068 B, 2610 lines)

Requested anchors: keep-ref namespace constant, the `gc` function, the code deciding
which keep refs survive (`recreate_no_gc_refs` — still present under that name at this
tag), and the `--prune` argument passed to git. Line 100 is the namespace constant
(comment on 99); 902 the survivor/deletion function; 925 and 941 the two keep
conditions; 948-949 the deletion queue; 964 the ref transaction; 970/977 the git-gc
wrapper and its `--prune` argument; 1558 the backend `gc` entry point, 1564/1575 the
calls it makes.

```
99: /// Ref namespace used only for preventing GC.
100: const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";
868: /// Returns `RefEdit` that will create a ref in `refs/jj/keep` if not exist.
869: /// Used for preventing GC of commits we create.
870: fn to_no_gc_ref_update(id: &CommitId) -> gix::refs::transaction::RefEdit {
900: /// Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other
901: /// unreachable and non-head refs.
902: fn recreate_no_gc_refs(
925:         if new_heads.contains(&id) && name_good {
929:         // Check timestamp of loose ref, but this is still racy on re-import
930:         // because:
931:         // - existing packed ref won't be demoted to loose ref
932:         // - existing loose ref won't be touched
941:             if mtime > keep_newer {
942:                 tracing::trace!(?git_ref, "not deleting new");
943:                 no_gc_refs_to_keep_count += 1;
944:                 continue;
945:             }
946:         }
947:         // Also deletes no-gc ref of random name created by old jj.
948:         tracing::trace!(?git_ref, ?name_good, "will delete");
949:         no_gc_refs_to_delete.push(git_ref);
960:         no_gc_refs_to_delete.into_iter().map(to_ref_deletion),
961:         new_heads.iter().map(to_no_gc_ref_update),
962:     );
963:     git_repo
964:         .edit_references(ref_edits)
970: fn run_git_gc(program: &OsStr, git_dir: &Path, keep_newer: SystemTime) -> Result<(), GitGcError> {
975:     git.arg("--git-dir=.") // turn off discovery
976:         .arg("gc")
977:         .arg(format!("--prune=@{} +0000", keep_newer.as_secs()));
1558:     fn gc(&self, index: &dyn Index, keep_newer: SystemTime) -> BackendResult<()> {
1559:         let git_repo = self.lock_git_repo();
1560:         let new_heads = index
1561:             .all_heads_for_gc()
1562:             .map_err(|err| BackendError::Other(err.into()))?
1563:             .filter(|id| *id != self.root_commit_id);
1564:         recreate_no_gc_refs(&git_repo, new_heads, keep_newer)?;
1565: 
1566:         // No locking is needed since we aren't going to add new "commits".
1572:             .gc(&table, keep_newer)
1573:             .map_err(|err| BackendError::Other(err.into()))?;
1574: 
1575:         run_git_gc(
1576:             self.git_executable.as_ref(),
1577:             self.git_repo_path(),
1578:             keep_newer,
```

Other `refs/jj/keep/` sites in the same file (not anchors, for completeness): lines 1831,
2397, 2403, 2410, 2448.

## 3. `sources/git-gc.adoc` — git v2.56.0 `Documentation/git-gc.adoc` (6744 B, 187 lines)

Requested anchor: the `--prune` default. Definition at 81; default at 82-83 (2 weeks,
overridable by `gc.pruneExpire`); "on by default" wraps 86-87; 160-161 states why a
newer-than-`--prune` object survives.

```
81: --prune=<date>::
82: 	Prune loose objects older than date (default is 2 weeks ago,
83: 	overridable by the config variable `gc.pruneExpire`).
84: 	--prune=now prunes loose objects regardless of their age and
85: 	increases the risk of corruption if another process is writing to
86: 	the repository concurrently; see "NOTES" below. --prune is on by
87: 	default.
88: 
89: --no-prune::
90: 	Do not prune any loose objects.
160: . Any object with modification time newer than the `--prune` date is kept,
161:   along with everything reachable from it.
```

## 4. `sources/operation-log.md` — jj 0.45.1 `docs/operation-log.md` (3334 B, 65 lines)

Pinned as the item (3) URL. Anchor for `jj op abandon`: **none exists**. The file's
only operation-discarding text names `jj undo`, `jj op revert` and `jj op restore`
(lines 15-18); `abandon` occurs zero times.

```
15: The operation log allows you to undo operations one-by-one (`jj undo`) or even
16: revert a specific one which isn't the most recent operation (`jj op revert`). It
17: also lets you restore the entire repo to the way it looked at an earlier point
18: (`jj op restore`).
```

## 5. `sources/cli-reference.md` — include mapping, supplementary (674 B, 20 lines)

Anchor: line 16 includes the snapshot that carries the `jj op abandon` prose.

```
15: {%
16:   include-markdown "../cli/tests/cli-reference@.md.snap"
17:   rewrite-relative-urls=false
```

## Byte-identity cross-checks (snapshot vs tag archives)

The same blobs were extracted from `https://codeload.github.com/jj-vcs/jj/tar.gz/refs/tags/v0.45.1`
and `https://codeload.github.com/git/git/tar.gz/refs/tags/v2.56.0` and compared with `cmp`:

```
CLI-REF-SNAP-IDENTICAL   cli/tests/cli-reference@.md.snap
GIT_BACKEND-IDENTICAL    lib/src/git_backend.rs
OPLOG-IDENTICAL          docs/operation-log.md
CLIREF-DOC-IDENTICAL     docs/cli-reference.md
GIT-GC-ADOC-IDENTICAL    Documentation/git-gc.adoc
```

`sha256sum -c SHA256SUMS` run with cwd `sources/` -> 5 x `OK`.

Response pins observed at fetch time (headers, `curl -sI`): ETag
`"cc365f3b2604d4cd6b9b58aff90d78bb0b22b046f576da050d03f3f402a49749"` (snapshot),
`"fdcb93c5067a65d3c6a5d90b769c995707eee58709564b23a009c641882cb670"` (git_backend.rs),
`"72eb8c0d5277694c11f3cb99a52d1d6187d5d3434ad2ae7d435d8ea44ab65a47"` (operation-log.md),
`"18446faf97bb5113b32d210eda6a2c87484f9abee887b28bfd5fe969a6d64e55"` (git-gc.adoc),
`"65a45ce0391c28b287fdd52b6acfb9dcafceabd36b9360dcdfc9cab902d15d4d"` (cli-reference.md).

## Local corroboration (this seat's scratch run, `git 2.56.0`)

The `--prune` argument shape at `git_backend.rs:977` matters: git takes the raw date and
timezone in a **single** argv element. Passed as two words it is a usage error:

```
$ git --git-dir=. gc --prune=@1792903642 +0000
usage: git gc [<options>]
rc=129
$ git --git-dir=. gc "--prune=@1792903646 +0000"
rc=0
```

The date is honoured as the loose-object cutoff: an unreferenced loose blob present
before (`cat-file -e` rc 0) is gone after `gc --prune=@<now+3600> +0000` (rc 1). Scratch
fixture under `/fast/scratch/hyaku/souji-r30/C3Snapshots/`, deleted at seat close; no
lane repo touched. The C3 measured run itself is a different seat's artifact
(`census/round-30/records/jj-keep-expiry-run.txt`).

## Appendix — tag-archive cross-reference (not in the pinned set)

`cli/src/commands/util/gc.rs` at v0.45.1 maps the flag to the source's time cut-off
(tag-archive bytes, not copied into the snapshot set):

```
54:     let keep_newer = match args.expire.as_deref() {
55:         None => SystemTime::now() - Duration::from_secs(14 * 86400),
56:         Some("now") => SystemTime::now() - Duration::ZERO,
65:     repo.store().gc(repo.index(), keep_newer)?;
```

Location: `jj-vcs/jj@7c41cdeb16b6b321c64e789a966b6adf723816a5:cli/src/commands/util/gc.rs`
(tarball URL above; scratch copy deleted, so this is a cross-reference only).
