# SwarmScout13 — scout: jj 0.45.1 reflogs, `jj util gc`, and what keeps an abandoned commit's object alive

## Status

STATUS: PASS — all four questions answered from tag-v0.45.1 source bytes opened this run, with line numbers and quotes. The object-removal side was also measured with real jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5 and git 2.56.0 in scratch. One link is an inference and is labelled `[INFERENCE]`: the predecessor path that keeps the old working-copy commit alive in the gc-preceding arm.

## Evidence

Sources fetched live this run (raw.githubusercontent.com, tag v0.45.1 for jj and v2.56.0 for git); sha256 of the bytes opened:

- jj `lib/src/git.rs` c9e734e65f9cad8968a9124c47b9615550c548831dd11b93d215413a388119eb
- jj `lib/src/git_backend.rs` 95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69 (`cmp` identical to `census/round-30/sources/git_backend.rs`)
- jj `cli/src/commands/util/gc.rs` 9c4d6a3704abb6f3afbb63cfd44153437b83d7e68d0f2426f84f8cdbbb0b4b9b
- jj `lib/src/operation.rs` ac5e677d3101ea8647177f89de5beeaf1ed4e9243d04acfb6ba2a17c6da1de85
- jj `lib/src/index.rs` 0b9cdec80f7a86fd9a841c754e728f354dbb27220e21f204cc9067d9f15601fe
- jj `lib/src/default_index/store.rs` 8d3bd76a72dd83d8609da20e5ad65192f94e2c2bfe6e747128201d35fbb9de09
- jj `lib/src/default_index/composite.rs` 665b449028a887a96f8cf4135fd1631dc448a1f3c247580a7b550ca7bbda3afe
- git `builtin/gc.c` 17a03f6f413a82f9a532596b0b3bf5c43119c1d9e8209149dff8d5f69e41e21d
- git `Documentation/git-reflog.adoc` 59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54
- git `Documentation/git-gc.adoc` e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c (equals the r30 capture hash)

Measurement: `jj --version` = `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`; `git --version` = `git version 2.56.0`. Every fixture repo was made with `jj git init --colocate <scratch dir>`; `git -C <dir> rev-parse --show-toplevel` printed the scratch dir before the first commit; jj ran only with `-R <scratch repo>`; user identity passed as `--config user.name/user.email` flags. Scripts: `/fast/scratch/hyaku/souji-r31/SwarmScout13/tmp/{run.sh,arm.sh,arm2.sh}` (removed at the end; the step tables below are copied from their output). Colocated repos have `core.logallrefupdates=true`. Steps print `keep_refs` = count of `refs/jj/keep/*`, `keep_names_B` = count of those refs naming the abandoned commit B, `B_in_HEAD_reflog` = count of HEAD reflog entries naming B, `B_object` = `git cat-file -e B`.

## Findings

### Q1 — Does jj write git reflog entries when it moves HEAD or refs in a colocated repo, and with what message?

1. **HEAD: yes, message `export from jj`.** `update_git_head` edits `HEAD` with a log message (lib/src/git.rs:1782-1817); quote at :1808: `message: "export from jj".into(),`. It is called from the export path when a HEAD-pointed bookmark moves (git.rs:1382) and from `reset_head` (git.rs:1879). Measured: after `jj commit` twice, `git reflog show HEAD` held 2 entries, both `export from jj`; after `jj abandon @-` it held 3, all `export from jj`; the logs tree was only `logs/HEAD`.
2. **Exported bookmarks: yes, same message in the source; the tag reflog is absent in the measurement.** `create_git_ref` and `move_git_ref` (used for bookmarks and tags) call `git_repo.reference(..., "export from jj")` (git.rs:1705, :1737, :1759); quote at :1705: `git_repo.reference(git_ref_name.as_str(), new_oid, constraint, "export from jj")`. Measured: bookmark `bm` created then moved gave `logs/refs/heads/bm` with two `export from jj` entries; the file was gone after `jj bookmark delete bm` (deletes use `RefLog::AndReference`, git.rs:1687 and :3503). `refs/tags/t1` (created by `jj tag set`) produced no `logs/refs/tags/*` file — the logs tree was `logs/HEAD` and `logs/refs/heads/bm` only.
3. **Keep refs: a log message is requested, no reflog file results.** `to_no_gc_ref_update` carries `message: "used by jj".into(),` (lib/src/git_backend.rs:877, function :868-886); `to_ref_deletion` uses `RefLog::AndReference` (:893). Measured: with 7-9 keep refs present, the logs tree held no `logs/refs/jj/` path (run.sh printed `logs/HEAD` only after two commits). So `refs/jj/keep/*` has no reflog in a default colocated repo. [INFERENCE] why: gix writes a reflog only for HEAD and refs/heads, refs/remotes, refs/notes under `logallrefupdates=true`; the source requests a message but sets no `force_create_reflog` (git.rs:2249 shows the only explicit `force_create_reflog: false`). The absence is measured, the gix rule is not opened.
4. **Other writers.** `add_ref` (git.rs:2240-2258) and `remove_ref` (git.rs:2260-2271) serve remote rename with message `renamed remote <old> to <new>` (git.rs:2631-2634); pushed remote-tag ref updates use `LogChange::default()` (git.rs:3497, empty message). Import (`import_refs`, `import_head`) only reads git refs; the HEAD import doc says `Imports HEAD from the underlying Git repo.` (git.rs:1167) and no `edit_references` call sits in the import path (the only call sites are git.rs:1817, :2542, :2669 and git_backend.rs:497, :964).

### Q2 — Does `jj util gc` expire git reflogs or pass any reflog option to git? Which git command does it run to prune?

5. **No reflog option, no reflog expiry by jj.** `cmd_util_gc` computes `keep_newer` (`None` -> now minus 14 days, `Some("now")` -> now, anything else rejected; gc.rs:54-58), then runs `repo.op_store().gc(...)` (gc.rs:62-64) and `repo.store().gc(repo.index(), keep_newer)` (gc.rs:65). The backend `gc` (git_backend.rs:1558-1580) calls `recreate_no_gc_refs` (:1564, function :902-968) and `run_git_gc` (:1575). Nothing in those functions touches `logs/`.
6. **The exact git command.** `run_git_gc` (git_backend.rs:970-989) builds `<git.executable-path> --git-dir=. gc --prune=@<keep_newer unix seconds> +0000`, run with cwd = the git dir (:974-980). Quotes: `git.arg("--git-dir=.") // turn off discovery` (:975) and `.arg(format!("--prune=@{} +0000", keep_newer.as_secs()));` (:977). The program is the `git.executable-path` setting (git.rs:113, backend field git_backend.rs:195). No other argument: no `--aggressive`, no `--cruft`, no reflog flag. Seconds are truncated (`.as_secs()`), so the prune instant has 1 s granularity. A non-zero exit becomes `GitGcError::GcCommandErrorStatus` (:985-987).
7. **Git itself expires reflogs inside that gc.** git 2.56.0 `builtin/gc.c` runs `git reflog expire --all` as a foreground task (gc.c:329-336, :540); quote at :334: `strvec_pushl(&cmd.args, "reflog", "expire", "--all", NULL);`. It is skipped only when both `gc.reflogexpire` and `gc.reflogexpireunreachable` are `never` (gc.c:166-168). Thresholds come from config, defaults 90 days and 30 days: git-reflog.adoc:113-115 `configuration setting `gc.reflogExpire`, which in turn defaults to 90 days` and :122-124 `setting `gc.reflogExpireUnreachable`, which in turn defaults to 30 days`. So `jj util gc --expire=now` does not shorten reflog life; the prune date it passes (`--prune=@now`) is separate from the reflog clocks.
8. **Measured.** A HEAD reflog entry naming B survived two `jj util gc --expire=now` runs unchanged (HEAD reflog list identical before and after in run.sh). With `gc.reflogExpire=now` and `gc.reflogExpireUnreachable=now` set in the repo config, one `jj util gc --expire=now` emptied the HEAD reflog (arm Z below).

### Q3 — What else keeps an abandoned commit's object alive besides `refs/jj/keep/*`, branches/tags and reflogs?

9. **Descendant or predecessor-referenced heads, through the op store and index (indirect, via keep refs).** The op store is not a git root: git sees only refs. But jj's index feeds the keep-ref set. The index heads are `Heads among all indexed commits at the associated operation.` (lib/src/index.rs:141) and `all_heads_for_gc` returns `self.commits().all_heads()` (default_index/composite.rs:636-637). The index is built from `op.all_referenced_commit_ids()` plus each view's referenced commits (default_index/store.rs:267-276), and that operation method documents: `The predecessor commit ids are also included,` / `which ensures that the old commits to be returned by` `predecessors_for_commit()` `are still reachable.` (lib/src/operation.rs:141-148). So a hidden predecessor commit whose operation was not abandoned stays an index head, gets a keep ref (git_backend.rs:1560-1564), and its parent B stays reachable in git.
   Measured (arm X, `jj abandon @-` then `jj op abandon '..@-'` then `jj util gc --expire=now`): `keep_refs` fell 8 -> 2 but 2 remained, one naming a commit whose git parent is B (read with `git log --all`), so B stayed present while `keep_names_B=0`. Arm V (`jj abandon @-`, `jj new`, `jj op abandon '..@-'`, `jj util gc --expire=now`): `keep_refs` 9 -> 1, none naming B or a child of B. [INFERENCE] the surviving child ref in arm X is held by the head operation's own predecessor record (operation.rs:141-154); the measured part is the 2-versus-1 difference.
10. **Keep refs are also (re)created on import**, not only on write: `import_head_commits` does `edit_references(head_ids...to_no_gc_ref_update)` (git_backend.rs:485-498; comment at :493-494 `Create no-gc ref even if known to the extras table`).
11. **Git index and other worktrees' HEADs.** git-gc NOTES say gc keeps `objects referenced by the index, remote-tracking branches, reflogs` (git-gc.adoc:143-145). The git index holds trees and blobs, not commits; jj resets it from the working-copy parent on `reset_head` (git.rs:1839-1881). [INFERENCE] it cannot keep a commit object alive; not measured. The export loop also visits linked worktrees' HEADs (git.rs:1396-1400), so a worktree HEAD and its reflog are roots too (not measured).
12. **`refs/jj/root`** is only the placeholder for an unborn HEAD (git.rs:96, :1791-1803); it names no commit.

### Measured object lifetime (fixture: commits A, B, B abandoned; scratch repos, jj 0.45.1, git 2.56.0)

Arm N — `jj abandon @-`, `jj new`, `jj op abandon '..@-'`, `jj util gc --expire=now`, then `git gc --prune=now`:
- after `jj util gc`: `keep_names_B=0` `B_in_HEAD_reflog=1` `B_object=yes`; after `git gc --prune=now`: `B_in_HEAD_reflog=1` `B_object=yes`.

Arm R — same, then `git reflog expire --expire=now --all`, then `git gc --prune=now`:
- after reflog expire: `B_in_HEAD_reflog=0` `B_object=yes`; after `git gc --prune=now`: `B_object=no`.

Arm R2 — same, then `git reflog expire --expire=now --all`, then `jj util gc --expire=now` only:
- `B_object=no` after that one jj command (jj's own `git gc --prune=@now` removed the unreachable object).

Arm Z — same, with `gc.reflogExpire=now` and `gc.reflogExpireUnreachable=now` set in the repo config, then `jj util gc --expire=now` only:
- before: `B_in_HEAD_reflog=1` `B_object=yes`; after: `B_in_HEAD_reflog=0` `B_object=no`.

Arm X (no `jj new` before the op abandon) — a second keep ref names a child of B, so `B_object=yes` after every step, including `git reflog expire --expire=now --all` plus `git gc --prune=now` (matches the r30 wave-2 correction).

### Q4 — Compare with `corpus/knowledge/jj-keep-ref-expiry.md` (opened this run; sections up to `## Round 30 wave-2 corrections`): what is NEW ground?

Already held there (not new): keep-ref removal by `recreate_no_gc_refs`, the loose-ref mtime gate and packed-ref fall-through (git_backend.rs:929-946), `--expire` accepting only `now`, `--prune=@<keep_newer>` at :977, `git gc` alone not removing a keep-ref commit, and the wave-2 correction that a surviving descendant keep ref plus the reflog arm left B present (without the reflog source lines, the message, or an arm that removed B).

NEW ground, in order of value:
- **N1 — Object removal measured, with the full condition set.** B's object disappears only when (a) no keep ref names B or any descendant/predecessor-held child, (b) no reflog entry names B, and (c) a git prune runs at or after the object's mtime. Arms R, R2 and Z show `B_object=no`; the held entry says `Object removal is not measured` and every record step shows `object_present=yes`.
- **N2 — Reflog presence and message, by ref class.** HEAD and exported bookmarks get `export from jj` entries (git.rs:1808, :1705, :1737, :1759); keep refs request `used by jj` (git_backend.rs:877) but no reflog file appears; tags get none; deleting a bookmark removes its reflog file. The held entry names reflogs only in a correction, with no source line or message.
- **N3 — `jj util gc` never touches reflogs; git's own gc does, on git's clock.** `git reflog expire --all` runs inside gc (gc.c:334, :540) with 90 d / 30 d defaults (git-reflog.adoc:113-124); jj passes only `--git-dir=.`, `gc`, `--prune=@<secs> +0000` (git_backend.rs:975-977). So reflog life is a separate clock from jj's `--expire`, measured by the HEAD reflog surviving two `jj util gc --expire=now` runs and by arm Z.
- **N4 — The index/op-history mechanism behind "a descendant's keep ref".** The held correction states the descendant observation; the cause path is `Operation::all_referenced_commit_ids` including predecessors (operation.rs:141-154) feeding the index (default_index/store.rs:267-276) whose heads become keep refs (composite.rs:636-637, git_backend.rs:1560-1564). Arm X versus arm V (`jj new` before `jj op abandon`) shows the practical fix to reach B; the link inside arm X is `[INFERENCE]`.
- **N5 — Exact git invocation incl. executable path and 1 s truncation** (git_backend.rs:970-989, git.rs:113). The held entry cites only line 977.
- **N6 — Keep refs are also created on import** (git_backend.rs:485-498), and the export loop touches other worktrees' HEADs (git.rs:1396-1400).
- **Open (not settled here):** whether git's cruft-pack handling changes object mtime semantics for packed unreachable objects (gc.c has `.cruft_packs = 1` default at :138; not read in depth); whether a git index entry can keep a tree that holds nothing commit-shaped (irrelevant to commits); behaviour on a later jj release.

Candidate registry rows opened this run that are absent from the corpus (C3 sourcing; S054 already says "also cli/src/commands/util/gc.rs, lib/src/git.rs" but no held entry snapshots them): `lib/src/git.rs`, `lib/src/operation.rs`, `lib/src/index.rs`, `lib/src/default_index/store.rs`, `cli/src/commands/util/gc.rs` (jj v0.45.1), git `builtin/gc.c` at v2.56.0 (S009 holds v2.55.0), git `Documentation/git-reflog.adoc` at v2.56.0 (no row matched `git-reflog` in `corpus/SOURCES.md`; sweep: `grep -n -i "git-reflog" corpus/SOURCES.md` returned nothing). S002 (git-gc(1)) already carries `gc.reflogExpire`.

## Deliveries

None (report only). Scratch `/fast/scratch/hyaku/souji-r31/SwarmScout13/` removed after this report was written; no writes outside it and this report. Tools installed or updated: none.
