STATUS: DONE — `refs/jj/keep/*` are jj's anti-GC refs for commits reachable only from the operation log; only the manual `jj util gc` re-derives and deletes them (default grace 2 weeks). The assigned git-compatibility page states the purpose but does **not** name the `keep` namespace, hidden/abandoned retention or removal; those parts are `not stated` there and are grounded below on the same docs set plus tagged source.

# SrcJjKeepRefs — `refs/jj/keep/*`: why written, what they hold, what removes them

Scope: one question, source-opening for `corpus/SOURCES.md`. Read only `CORPUS.md` § `SOURCES.md — where a shokunin learns` and `corpus/SOURCES.md` (header + registry shape). No lane file other than the report target was written.

## 1. Answer

**Observed (documents):**

- *Why:* jj writes a Git ref for commits that are reachable from the operation log but from no Git ref, so that Git's GC cannot delete jj's history. Two pages say this:
  - `docs/git-compatibility.md` § Format mapping details: "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC."
  - `docs/technical/architecture.md` § GitBackend: "To prevent GC from deleting commits that are still reachable from the operation log, the `GitBackend` stores a ref for each commit in the operation log in the `refs/jj/keep/` namespace."
- *Whether they hold hidden/abandoned commits:* yes, while the operation log still references them. The index that drives the refs is built from every operation's referenced commit ids **including predecessor commit ids** ("which ensures that the old commits to be returned by `predecessors_for_commit()` are still reachable", `lib/src/operation.rs:141-154` @v0.46.0). Rewritten versions (hidden) and abandoned commits are exactly the commits that are not on a branch/tag/remote, so they are kept only by this mechanism until operation history drops them. The CLI reference makes the discard step explicit: "Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history" (§ `jj operation abandon`).
- *What removes them:* **`jj util gc` — and only that command.** At v0.46.0 it re-derives the set of heads to preserve (`index.all_heads_for_gc()`), rewrites `refs/jj/keep/<commit-id>` for them, deletes the refs for commits outside that set once the loose ref file is older than the threshold, then runs `git gc --prune=@<threshold>` (`lib/src/git_backend.rs:899-901`, `:1566-1588`). The only call site is the CLI command (`cli/src/commands/util/gc.rs:62-68`); no automatic GC path exists. Default threshold is `now - 14 days`; `--expire=now` removes the grace (`gc.rs:54-58`; CLI reference § `jj util gc`, option `--expire`: "By default, only obsolete objects and operations older than 2 weeks are pruned."). The documented sequence is `jj op abandon ..<some old operation>` first, then `jj util gc` (§ `jj util gc` and § `jj operation abandon`).
- *CHANGELOG corroboration:* `§ 0.14.0 - 2024-02-07 › New features`: "New `jj op abandon` command is added to clean up the operation history. Git refs and commit objects can be further compacted by `jj util gc`." The "Git refs" that jj itself owns are the `refs/jj/keep/` refs (the CHANGELOG never spells the namespace: `grep -c 'refs/jj' CHANGELOG.md` = 0). Prior history: `§ 0.6.0 - 2022-12-05 › Fixed bugs`: "Git's GC could remove commits that were referenced from jj in some cases. We are now better at adding Git refs to prevent that." (§ issue #815) — this is the defect class the namespace exists for.

**Inference / precision notes (not page-stated):**

- `git gc` alone cannot remove these refs: refs are GC roots and `git gc` does not delete refs. The jj page only says "It should be safe to run `git gc` in the Git repo". `[INFERENCE — general git semantics, git-gc(1) not opened this round]`
- Refs are written per *head among indexed commits*, not one per operation-log commit: the architecture page's "a ref for each commit in the operation log" overstates the count. Hidden predecessors that are ancestors of a kept head have no ref of their own but are still reachable *through* that head's ref, so `git log --glob=refs/jj/keep/* -- <path>` sees them by traversal. This keeps C3(b)'s `--glob=refs/jj/keep/*` roots sound, and it means a `for-each-ref refs/jj/keep/*` count is a lower bound, not the number of held commits.
- These refs can appear without any explicit commit action: `import_head_commits()` creates a keep ref on every Git-ref import as a race guard ("Create no-gc ref even if known to the extras table. Concurrent GC process might have deleted the no-gc ref.", `lib/src/git_backend.rs:477-500` @v0.46.0). A receipt scan may therefore encounter `refs/jj/keep/*` in any jj-touched repo.

**Remaining gap:** the exact moment a keep ref for a *specific* hidden commit disappears after its operation is GC'd (op-store retention vs. the pre-built index segment) is not stated by any opened page and was not determined from the code here.

## 2. Quotes — verbatim, anchored, word-counted

| # | Verbatim quote | Words | Location / anchor |
|---|---|---|---|
| Q1 (assigned page) | "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC." | 13 | Git compatibility, § Format mapping details, `#format-mapping-details`; served page 2026-10-20 = v0.46.0; `docs/git-compatibility.md:260` @ tag v0.46.0 |
| Q2 (purpose, exact namespace) | "To prevent GC from deleting commits that are still reachable from the operation log" | 14 | technical/architecture, § GitBackend, `#gitbackend`; `docs/technical/architecture.md:78-79` @ tag v0.46.0 |
| Q3 (holders + namespace) | "the `GitBackend` stores a ref for each commit in the operation log in the `refs/jj/keep/` namespace" | 16 | same page, `docs/technical/architecture.md:79-80` @ tag v0.46.0 |
| Q4 (removal, CHANGELOG) | "Git refs and commit objects can be further compacted by `jj util gc`." | 13 | CHANGELOG, § 0.14.0 - 2024-02-07 › New features; `CHANGELOG.md:4493-4494` (main @ 7dd5f92) |
| Q5 (grace) | "By default, only obsolete objects and operations older than 2 weeks are pruned." | 13 | CLI reference, § `jj util gc`, `#jj-util-gc`, option `--expire`; same site |
| Q6 (hidden/predecessor discard) | "Previous versions of a change (or predecessors) are also discarded if they become unreachable from the operation history." | 18 | CLI reference, § `jj operation abandon`, `#jj-operation-abandon` |
| Q7 (mechanics) | "Recreates `refs/jj/keep` refs for the `new_heads`, and removes the other unreachable and non-head refs." | 14 | `lib/src/git_backend.rs:899-900` @ tag v0.46.0 (doc comment of `recreate_no_gc_refs`) |

**`not stated` on the assigned git-compatibility page:** the literal `keep` namespace (Q1 says only `refs/jj/`), whether the refs hold hidden/abandoned commits, and what deletes them. Its only `jj util gc` sentence is about import speed: "This can be mitigated by occasionally running `jj util gc` to speed up the import (that command includes packing the Git refs)." (§ Colocated Jujutsu/Git workspaces) — that is ref packing, not ref deletion, and must not be quoted as a removal statement.

## 3. Access record (2026-10-20)

- Assigned URL `https://jj-vcs.github.io/jj/latest/git-compatibility/` → `HTTP/2 301`, `location: http://docs.jj-vcs.dev/latest/git-compatibility/`; served title "Git compatibility - Jujutsu docs".
- **No "last updated" line is served** by the page (mkdocs-material without a revision-date plugin; `grep -i 'last updated\|last-updated\|git-revision'` on the HTML: 0 hits). Version is resolved by the site, not the page: `https://docs.jj-vcs.dev/versions.json` lists `{"version": "v0.46.0", "title": "v0.46.0", "aliases": ["latest"]}`; GitHub's latest release is `v0.46.0`, published `2026-10-07T21:28:17Z`. The served page's Format mapping details paragraph matches `docs/git-compatibility.md` at tag `v0.46.0` word-for-word (line 260).
- CHANGELOG `https://github.com/jj-vcs/jj/blob/main/CHANGELOG.md` opened 2026-10-20: file begins `## [Unreleased]`; newest released section `## [0.46.0] - 2026-10-07`; no page-level "last updated" (GitHub shows history, not a date). Latest commit touching the file on `main`: `7dd5f92dde1c2a83366237180319520722ccee54` (committer `2026-10-20T07:48:26Z`, author `2026-10-14T13:44:25Z`).

## 4. Mechanical trace @ tag v0.46.0 (source tarball of the tag)

- `const NO_GC_REF_NAMESPACE: &str = "refs/jj/keep/";` — `lib/src/git_backend.rs:100`
- `to_no_gc_ref_update`: "Returns `RefEdit` that will create a ref in `refs/jj/keep` if not exist. Used for preventing GC of commits we create." Ref name is `format!("{NO_GC_REF_NAMESPACE}{id}")` — `git_backend.rs:867-871`
- `recreate_no_gc_refs`: deletes refs not in `new_heads` or whose name ≠ hex id, unless the loose ref mtime > `keep_newer`; also "deletes no-gc ref of random name created by old jj" — `git_backend.rs:899-973`
- `GitBackend::gc(index, keep_newer)`: `new_heads = index.all_heads_for_gc()` (root commit filtered), then `recreate_no_gc_refs`, extras gc, `git gc --prune=@<keep_newer>` — `git_backend.rs:1560-1590`, `:971-990`
- `Index::all_heads_for_gc`: "Heads among all indexed commits at the associated operation … returns the heads that should be preserved on garbage collection." — `lib/src/index.rs:141-148`
- Index construction from historical heads: `op.all_referenced_commit_ids()` + `op.view().all_referenced_commit_ids()` — `lib/src/default_index/store.rs:268-296`; predecessor ids included — `lib/src/operation.rs:141-154`
- CLI: threshold `14 * 86400`, `--expire` accepts only `now`, refuses off-head operation, then `op_store.gc` + `git_backend.gc(repo.index(), keep_newer)` — `cli/src/commands/util/gc.rs:26-29, :47-68`
- Call sites of `GitBackend::gc`: only `cli/src/commands/util/gc.rs:67` (grep over `cli/` + `lib/`, tests excluded). No auto-GC.
- Bug class the namespace exists for: CHANGELOG § 0.6.0 `Git's GC could remove commits that were referenced from jj in some cases` (issue #815); `jj util gc` introduced § 0.12.0 (`There is a new jj util gc command for cleaning up the repository storage`); expanded to op/view/Git objects § 0.14.0; `--expire=now` passthrough § 0.31.0; extras pruning § 0.37.0.

## 5. Drafted SOURCES row (registry column order; L1 numbers it — next unused is S051)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S0?? | Jujutsu docs, Git compatibility and technical architecture — https://docs.jj-vcs.dev/latest/git-compatibility/ | docs | A | purpose, holders and removal of `refs/jj/keep/` on jj v0.46.0; not git's own ref or GC semantics | § Format mapping details (#format-mapping-details), docs/git-compatibility.md:260 at tag v0.46.0; § GitBackend (#gitbackend), docs/technical/architecture.md:78-80 at tag v0.46.0; § jj util gc (#jj-util-gc) and § jj operation abandon (#jj-operation-abandon), same site served 2026-10-20 (latest = v0.46.0); § 0.14.0 New features, CHANGELOG.md:4493-4494 at main 7dd5f92; lib/src/git_backend.rs:100, :899-901, :1566-1574 and lib/src/index.rs:141-148 at tag v0.46.0 | jj refs every operation-log-reachable commit head under `refs/jj/keep/<commit-id>` so Git cannot collect hidden or abandoned history; only the manual `jj util gc` re-derives those refs and deletes the rest, by default after two weeks | mined | 2026-10-20 | on-release | corpus/knowledge/jj-colocation-receipts.md |

Row notes for L1:

- **Status dependency.** `mined` is correct only once C3(c) lands `corpus/knowledge/jj-colocation-receipts.md`; the frozen census prints `missing:` for a `mined` row whose `used-by` path does not exist. If the row lands before the entry, write `queued` with `used-by` `—` and flip `queued → mined` in the round lesson (append-only rule allows this).
- **Split option.** If a single-page row is preferred, this becomes three rows: (a) git-compatibility § Format mapping details (Q1 only; evidence that the `refs/jj/` namespace exists to prevent GC); (b) technical/architecture § GitBackend (Q2/Q3; the operation-log holder and exact `keep/` namespace); (c) cli-reference § jj util gc + CHANGELOG § 0.14.0 (Q4/Q5; removal and 2-week default). The single row above was drafted because the registry already accepts multi-file rows for one project (S009 spans four files).
- **Scope discipline.** Tier A covers only the purpose/namespace/lifetime claim. The page's GC bullet also contains a stale clause (see § 6); it is outside the row's scope and must not be cited.

## 6. Contradictions

**Against C3's claim text: none.** No opened page contradicts C3(a) (never root receipts at `refs/jj/*`), C3(b) (`refs/jj/keep/*` roots for touching checks), or C3(d)/(e). Q1–Q3 support (a) and (b); "Jujutsu will import and export from and to the Git repo on every `jj` command automatically" and "`jj` commands will usually put the Git repo in a 'detached HEAD' state" support (d)'s recipes. The page never mentions `refs/stash`, `HEAD`, `--not --all`, phantom deletions, or `@{u}`, so it cannot contradict those clauses.

**Two page statements do contradict the current docs set / each other** (flagging for C3's premise, not as C3 refutations):

1. *Worktrees.* Git compatibility § Supported features: "git-worktree: No. However, there's native support for multiple working copies backed by a single repo." (15 words) — contradicted by the CHANGELOG's 0.46.0 release highlight (the same version the page serves): "Jujutsu can now colocate workspaces besides the default one by creating Git worktrees." (13 words). Relevance: C3 governs jj-colocated repos; under 0.46.0 a colocated non-default workspace is a Git worktree, so `$GIT_DIR` may be a `.git` *file* plus `commondir` — which the census guard already lists, but the page cannot be cited as evidence that worktrees are absent. Smallest fix: cite the 0.46.0 CHANGELOG row for worktree colocation; treat the page's `git-worktree: No` as stale. (Upstream doc fix, not a lane edit.)
2. *GC of jj's own data.* Same page, Garbage collection bullet: "There's no garbage collection and repacking of Jujutsu's own data structures yet, however." (13 words) — contradicted by CLI reference § `jj util gc` ("Run backend-dependent garbage collection.") and CHANGELOG § 0.14.0: "`jj util gc` now removes unreachable operation, view, and Git objects." (11 words). Relevance: a reader trusting the page would treat keep refs as permanent; C3(a) is conservative either way (NOT-SAFE), but the census/verify rationale must not claim permanence. Smallest fix: in the knowledge entry, state removal as Q4+Q5, never as "never collected".

**Documented coverage gap relevant to C3(a):** Git compatibility § Branches is literally "TODO: Describe how branches are mapped". The receipt-root policy assumes jj bookmarks export to `refs/heads`; the assigned page does not state that mapping, so the `refs/heads` half of C3(a) needs a different source (bookmarks doc) — not this row.

**Doc-vs-code imprecision (not a contradiction of C3):** architecture says "a ref for each commit in the operation log"; the implementation makes refs for `all_heads_for_gc()` only. Ancestors remain protected transitively. Consequence: `for-each-ref refs/jj/keep/*` is a lower bound on held commits; `git log --glob=refs/jj/keep/*` is the complete view because it walks ancestors.

## 7. Verdict and smallest fix

- **Verdict: holds** for the premise of C3(a)/(b): `refs/jj/keep/*` are jj-owned, non-branch, non-remote refs that pin commits which otherwise have no durable Git root; they are written automatically on import/creation and removed only by a manual `jj util gc` (2-week default grace, `--expire=now` overrides). **Partial** only on the citation: the assigned page alone answers "why" (Q1) and not "what they hold" or "what removes them" — those require Q2–Q7.
- **Smallest fix:** in `corpus/knowledge/jj-colocation-receipts.md`, cite Q2/Q3 (architecture § GitBackend) for the holder semantics and Q4/Q5 (CHANGELOG § 0.14.0 + CLI reference § `jj util gc`) for removal; do not cite the page's "no garbage collection … yet" clause, and do not describe keep refs as permanent. If a single sentence is needed for the tools' rationale: keep refs exist precisely so Git GC cannot drop operation-log-only commits, so a commit visible only through `refs/jj/keep/*` is held by jj, not by any durable root — never `SAFE(metadata-prune)`.

## 8. Commands run (read-only; scratch under `/var/tmp/souji-r17-SrcJjKeepRefs/`, deleted after)

Web fetches (2026-10-20):

- `read https://jj-vcs.github.io/jj/latest/git-compatibility/` → canonical `https://docs.jj-vcs.dev/latest/git-compatibility/`; full page text captured.
- `curl -fsSI https://jj-vcs.github.io/jj/latest/git-compatibility/` → `HTTP/2 301`; `location: http://docs.jj-vcs.dev/latest/git-compatibility/`.
- `curl -fsSL https://docs.jj-vcs.dev/versions.json` → `"version": "v0.46.0"`, `"aliases": ["latest"]` (first two entries: `prerelease`, `v0.46.0`).
- `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/main/CHANGELOG.md` → 5876 lines; `grep -n '^## \['` → `9:## [Unreleased]`, `90:## [0.46.0] - 2026-10-07`, `261:## [0.45.1]`, …; `grep -c 'refs/jj'` → 0.
- `curl -fsSL https://api.github.com/repos/jj-vcs/jj/releases/latest` → `"tag_name": "v0.46.0"`, `"published_at": "2026-10-07T21:28:17Z"`.
- `curl -fsSL 'https://api.github.com/repos/jj-vcs/jj/commits?path=CHANGELOG.md&sha=main&per_page=1'` → `7dd5f92dde1c2a83366237180319520722ccee54`; commit dates `2026-10-14T13:44:25Z` (author) / `2026-10-20T07:48:26Z` (committer); the commit touches `CHANGELOG.md` (4 path hits).
- `curl -fsSL https://raw.githubusercontent.com/jj-vcs/jj/v0.46.0/docs/git-compatibility.md` → `260:Commits created by \`jj\` have a ref starting with \`refs/jj/\` to prevent GC.`
- `curl -fsSL https://docs.jj-vcs.dev/latest/technical/architecture/` → HTML line 2381: `<p>To prevent GC from deleting commits that are still reachable from the operation`; line 2383: `the <code>refs/jj/keep/</code> namespace.</p>`; section id `gitbackend`.
- `curl -fsSL https://docs.jj-vcs.dev/latest/cli-reference/` → `<h2 id="jj-util-gc">` with "Run backend-dependent garbage collection." and the 2-week `--expire` text; `<h2 id="jj-operation-abandon">` with the predecessor sentence.
- `curl -fsSL https://codeload.github.com/jj-vcs/jj/tar.gz/refs/tags/v0.46.0` + `tar xzf` (scratch only) → source greps as in § 4; `grep -rn '\.gc(' cli lib | grep -v test` → `cli/src/commands/util/gc.rs:63`, `:67`, `lib/src/git_backend.rs:1580` (extras table only) — no automatic Git GC.
- `grep -rn 'refs/jj/keep' jj-0.46.0 --include='*.rs' --include='*.md'` → `docs/technical/architecture.md:80`, `web/docs/src/content/docs/technical/architecture.md:82`, `lib/src/git_backend.rs:100, :867, :899, :1840, :2406, :2412, :2419, :2457`, `lib/tests/test_git_backend.rs:69`.

Files read in the lane (only these): `/home/vgpnk/Projects/shokunin/CORPUS.md` § SOURCES contract; `corpus/SOURCES.md` header + registry rows; the report target directory listing. No lane tool was run.

Tool installation: none (no pacman, no `uv`, no new binaries). Scratch directory `/var/tmp/souji-r17-SrcJjKeepRefs/` was removed after this report was written.

## 9. Remaining unknowns

- Exact retention timing of a specific keep ref after the referencing operation is GC'd (op-store prune vs. the already-built index segment) — not stated by docs; not traced to a definitive answer here.
- Whether `jj util gc`'s `git gc --prune=@<time>` can still drop an object that a *concurrent* writer created after the ref snapshot — the source comment claims `keep_newer` mitigates it; not tested (running jj is forbidden for seats).
- jj bookmark → `refs/heads` export mapping (needed for the `refs/heads` half of C3(a)) is a TODO on the assigned page; a bookmarks source must cover it.
