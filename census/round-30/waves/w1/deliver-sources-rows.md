# R30 C3 source rows — draft registry rows for `jj-keep-ref-expiry`

Seat `SwarmScribe13` (scribe), wave 1, item: SOURCES rows for C3. Lane
`/home/vgpnk/Projects/shokunin/souji-shokunin`, base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`.
Contract read first: `census/round-30/records/preregistration.txt`. No lane byte was written by
this seat; this file is the only delivery.

Two new rows (S220, S221). Two of the four requested slots are already held by existing rows and
must not be duplicated: slot 2 resolves to **S054**, slot 4 to **S063** (see "Slots not created").
Slot order kept: slot 1 = S220, slot 2 = none (S054), slot 3 = S221, slot 4 = none (S063).

## New registry rows — insert exactly these two lines after `corpus/SOURCES.md:164` (`| S219 | … |`), before `## Paths`

Insert the two data lines only — no header and no separator row (the registry table already has
both, and a second `| id | source |` line would parse as a row with id `id`). Cells follow the
existing column order: id, source, kind, tier, scope, anchor, teaches, status, opened, recheck, used-by.

| S220 | jj CLI reference at tag v0.45.1 — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap (served as https://docs.jj-vcs.dev/v0.45.1/cli-reference/) | docs | A | the documented contract of `jj util gc` and `jj op abandon` at v0.45.1: the default expire window, the only accepted `--expire` value, and what abandoning an operation does to its ancestors; not the keep-ref code path (S054) and not later releases | cli/tests/cli-reference@.md.snap at tag v0.45.1 (7c41cdeb), 4038 lines: :2411-2421 § `jj operation abandon`, :3789-3803 § `jj util gc`; served page /v0.45.1/ carries no 0.46-only subcommand (no `jj file delete`, no `jj util diff`); opened 2026-10-26 | `jj util gc` prunes only obsolete objects and operations older than 2 weeks by default and its `--expire` option accepts only "now"; `jj op abandon` discards the named operation with all its ancestors and reparents the descendants | mined | 2026-10-26 | on-release | corpus/knowledge/jj-keep-ref-expiry.md |
| S221 | jj docs/operation-log.md at tag v0.45.1 — https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/operation-log.md | docs | A | what the operation log stores at v0.45.1: each operation object carries a view of bookmark, tag and Git ref positions, the head set and each workspace's working-copy commit; not `jj op abandon` (the word does not occur in the file; S220 holds it) and not GC thresholds | docs/operation-log.md at tag v0.45.1, 65 lines: :5-12 § Introduction, :47-56 § Loading an old version of the repo; `grep -c abandon` = 0; opened 2026-10-26 | each operation object carries a view recording where every bookmark, tag and Git ref pointed at the end of that operation, plus the set of heads and the working-copy commit of each workspace | mined | 2026-10-26 | on-release | corpus/knowledge/jj-keep-ref-expiry.md |

Both rows split to 13 fields on the pipe; no cell contains a pipe. Kind `docs`, tier A (jj's own
docs at the tag), status `mined`, opened 2026-10-26, recheck `on-release`.

## Grounding quotes (opened 2026-10-26, ≤25 words, no pipe)

Byte identity: each file was fetched independently from `raw.githubusercontent.com` at the tag and
its sha256 equals the staged snapshot in `.ufo/waves/round-30/w1/sources/SHA256SUMS`
(`sha256sum -c` → 5 × OK); those snapshots are what the L1 commits as `census/round-30/sources/`.

### S220 — `cli/tests/cli-reference@.md.snap`, jj v0.45.1 (7c41cdeb), 154561 B / 4038 lines

| line | verbatim quote | words |
|---|---|---|
| 2415 | It will abandon the specified operation and all its ancestors. | 10 |
| 3801 | By default, only obsolete objects and operations older than 2 weeks are pruned. | 13 |
| 3803 | Only the string "now" can be passed to this parameter. | 10 |

Version check on the served page (the citation a human follows): `https://docs.jj-vcs.dev/v0.45.1/cli-reference/`
was fetched and compared with `/latest/`; the 0.46-only headings `jj file delete`, `jj file edit`,
`jj util diff`, `jj workspace remove` occur only on `/latest/`, and the `jj util gc` section text is
identical to the tag snapshot lines 3789-3803. So the versioned page is v0.45.1, not a redirect to latest.

### S221 — `docs/operation-log.md`, jj v0.45.1, 3334 B / 65 lines

| location | verbatim quote | words |
|---|---|---|
| :8-9 (line break after `and`) | The view contains information about where each bookmark, tag, and / Git ref (in Git-backed repos) pointed | 16 |

Negative claim in the scope cell carries its sweep: `grep -c abandon docs/operation-log.md` → `0`
(also confirmed by the C3 snapshot seat, `deliver-c3-anchor-lines.md` § 4). The file's only
discard verbs are `jj undo`, `jj op revert` and `jj op restore` (:15-18), so `jj op abandon` prose
is cited to S220, not here.

## Slots not created — existing rows the entry should cite instead

### Slot 2, `jj lib/src/git_backend.rs` at v0.45.1 (gc and keep refs) → **S054** (no new row)

`corpus/SOURCES.md:75` already holds this exact file at this exact tag with this exact subject:
source `jj source at tag v0.45.1 — https://github.com/jj-vcs/jj/blob/v0.45.1/lib/src/git_backend.rs`,
scope "creation and removal of `refs/jj/keep/*` in jj 0.45.1 (tag commit 7c41cdeb = host binary)",
anchor `:900-953 recreate_no_gc_refs, :1558-1564 gc` (with `cli/src/commands/util/gc.rs:34-35, :54-58`),
teaches "only `jj util gc` removes non-head keep refs older than its threshold (default 2 weeks)".
A second row on the same file would be duplicate evidence under a second convention, so none is drafted.

used-by change implied (append only):
`corpus/knowledge/jj-colocation-receipts.md` → `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-keep-ref-expiry.md`

Optional anchor enrichment for S054, if the entry cites the git-gc call line: the current anchor
list stops at `:1558-1564 gc`; the `--prune` argument itself is `:975-977`
(`.arg(format!("--prune=@{} +0000", keep_newer.as_secs()));` at :975, `run_git_gc(` call at 1575-1578).
Verified in the staged `sources/git_backend.rs`. This is an anchor addition, not a re-grounding; L1 decides.

### Slot 4, git `Documentation/git-gc.adoc` at v2.56.0 (`--prune`) → **S063** (no new row)

The lane already holds git-gc: `grep -n 'git-gc' corpus/SOURCES.md` → S002 (`git-gc(1)` grace
periods, `:23`), S030 (rejected, `:51`), S063 (reachability, `:84`). S063's scope is "which refs
keep objects alive during gc; not jj's own gc", and the lane already attributes the .adoc bytes to
it: `corpus/knowledge/jj-colocation-receipts.md:86` cites `git-gc.adoc@v2.56.0:18, 81-83` under
S063. Re-opened at the tag this run: `:18` "performance), removing unreachable objects which may
have been"; `:82` "Prune loose objects older than date (default is 2 weeks ago," (:83 continues
"overridable by the config variable `gc.pruneExpire`)."). A new row would restate S063 under a
second URL for the same predicate.

used-by change implied (append only):
`corpus/knowledge/jj-colocation-receipts.md` → `corpus/knowledge/jj-colocation-receipts.md, corpus/knowledge/jj-keep-ref-expiry.md`

Note: S002 (`:23`) is the row for git's own grace periods if the entry states git's two-week
`--prune` default as a git fact; co-citing it would imply the same used-by append on S002
(old `corpus/knowledge/git-grace-periods-and-expire-to.md` → old value plus
`, corpus/knowledge/jj-keep-ref-expiry.md`). S063 alone is sufficient for the consequence the entry needs.

## Validation

Tree: scratch mirror `/fast/scratch/hyaku/souji-r30/SwarmScribe13/val/` — `tools/` symlinked to the
lane, `corpus/*` symlinked per entry, `corpus/knowledge/*` symlinked per file, `corpus/SOURCES.md` a
real copy of the lane registry with S220/S221 spliced after S219.

Command and exit:

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file /fast/scratch/hyaku/souji-r30/SwarmScribe13/val/corpus/SOURCES.md --today 2026-10-26
EXIT=0
```

Output (complete; 36 W04 are pre-existing registry warnings, none from S220/S221):

```
file	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
file	W04	S036 duplicate url git-scm.com/docs/git across scopes
file	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S049 duplicate url git-scm.com/docs/git across scopes
file	W04	S057 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S058 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S059 duplicate url git-scm.com/docs/gitattributes across scopes
file	W04	S063 duplicate url git-scm.com/docs/git-gc across scopes
file	W04	S065 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
file	W04	S072 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
file	W04	S073 duplicate url man7.org/linux/man-pages/man2/kill.2.html across scopes
file	W04	S075 duplicate url man7.org/linux/man-pages/man5/proc_pid_stat.5.html across scopes
file	W04	S076 duplicate url man7.org/linux/man-pages/man5/proc_pid_exe.5.html across scopes
file	W04	S077 duplicate url man7.org/linux/man-pages/man2/open.2.html across scopes
file	W04	S086 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S087 duplicate url man7.org/linux/man-pages/man5/proc_pid_wchan.5.html across scopes
file	W04	S088 duplicate url man7.org/linux/man-pages/man5/proc_pid_status.5.html across scopes
file	W04	S089 duplicate url git-scm.com/docs/git across scopes
file	W04	S090 duplicate url git-scm.com/docs/git-filter-branch across scopes
file	W04	S091 duplicate url git-scm.com/docs/git-rev-parse across scopes
file	W04	S092 duplicate url git-scm.com/docs/git-for-each-ref across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-diff across scopes
file	W04	S094 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S095 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S096 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S097 duplicate url git-scm.com/docs/git-filter-branch across scopes
file	W04	S098 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S099 duplicate url git-scm.com/docs/git-rev-parse across scopes
file	W04	S106 duplicate url docs.python.org/3/library/json.html across scopes
file	W04	S108 duplicate url docs.python.org/3/builtins/exceptions.html across scopes
file	W04	S123 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S124 duplicate url git-scm.com/docs/gitrepository-layout across scopes
file	W04	S125 duplicate url git-scm.com/docs/git across scopes
file	W04	S126 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes
file	W04	S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes
file	ok	/fast/scratch/hyaku/souji-r30/SwarmScribe13/val/corpus/SOURCES.md
```

E11 depends on a target outside this item: `corpus/knowledge/jj-keep-ref-expiry.md` does not exist
yet (it is the C3 entry this wave produces). The run above therefore used a scratch-only placeholder
file at that path, disclosed here. The same tree without the placeholder:

```
EXIT=1
file	E11	S220 missing used-by corpus/knowledge/jj-keep-ref-expiry.md
file	E11	S221 missing used-by corpus/knowledge/jj-keep-ref-expiry.md
```

(identical to the exit-0 output otherwise: same 36 W04, plus those two lines, minus the `ok` line).
**The L1 must re-run the same command against the committed registry after the C3 entry lands; E11
must be 0 there without any placeholder.**

## For the L1

1. Insert the two rows after `corpus/SOURCES.md:164`.
2. Apply the two used-by appends (S054, S063), and optionally the S054 anchor addition (:975-977).
3. Re-run the validate command above against the committed registry once
   `corpus/knowledge/jj-keep-ref-expiry.md` exists.
4. `corpus/README.md:46` still says "remaining: keep-ref expiry unmeasured"; flipping that line is a
   C3/L1 act, not a rows act — noted, not done.
