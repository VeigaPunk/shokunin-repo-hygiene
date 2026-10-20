STATUS: DONE — paste-ready round-17 `## Gate` SOURCES draft for S051–S063 delivered below; all 13 quotes independently re-verified verbatim against the live sources on 2026-10-20 (no unconfirmed marks needed); registry-changes old→new sentence drafted; six falsify findings for L1 (id collisions, a duplicate-URL row to drop, landing-order preconditions).

# ConnLessonGateSection — round-17 lesson `## Gate`, SOURCES section (W2 FALSIFY)

Seat: SoujiR17-3.ConnLessonGateSection-2. Leaf; no subagents. Read-only wave: no lane tool run, no `jj`, no git write, no `/var/tmp` scratch (all web fetches in-memory), no tool installs. Only this report written.

## 0. Method and evidence base

- Format source: `corpus/lessons/round-16.md:24-35` at ddb7347 (heading `:24`, source lines `:26-33`, registry-changes paragraph `:35`). Working tree identical to ddb7347 for `corpus/SOURCES.md` and `corpus/lessons/round-16.md` (`git diff --stat ddb7347 --` on both: empty).
- Registry state at ddb7347: `corpus/SOURCES.md:9` (round-16 provenance note), rows end at S050 (`:63` S049, `:64` S050). S051–S063 are absent today; `corpus/lessons/round-17.md` does not exist (`ls` → exit 2).
- Quote sources: all 13 w1 reports `.ufo/waves/round-17/w1/Src{JjGitCompat,JjWorkingCopy,JjConfigSnapshot,JjKeepRefs,JjBookmarks,JjNestedRepo,GitShowUntracked,GitWorktreeConfig,GitRepoLayoutAttrs,GitRevAll,PyLstrip,Fifo7,GitGcReachability}.md`, each opened by exact name.
- My verification (the falsify pass): one kernel cell fetched all 17 URLs (13 quote pages + open(2) + gitrepository-layout + jj versions.json) with urllib, stripped tags (two normalizations: tags→`` and tags→space), unescaped entities, collapsed whitespace, and substring-tested each seat's exact quote; a second cell diagnosed the four initial misses (all artifacts of my `tag→space` insertion before adjacent punctuation, e.g. `refs/</code>,` → `refs/ ,`; all four match under flat normalization). Version stamps re-read from the same fetches. Exact probe outputs are in §3.

**Verbatim status: 13/13 CONFIRMED.** No quote below carries an unconfirmed mark. All matched today, 2026-10-20, same day as the seats' access date. Caveat stated once: my check tests the markup-stripped page text (the `[1]` link brackets, backticks and `*emphasis*` in the drafted lines are the pages' own inline markup as recorded by the seats; stripping them is what makes the flat text match).

## 1. Draft — paste-ready section (report only; L1 integrates)

```markdown
### Sources opened this round (URL · access 2026-10-20 · located quote ≤25 words)

- **S051** https://docs.jj-vcs.dev/latest/git-compatibility/ (docs.jj-vcs.dev `latest` = v0.46.0 per versions.json; page serves no last-updated line; canonical of the github.io URL, which 301s; SrcJjGitCompat): "jj commands will usually put the Git repo in a "detached HEAD" state, since in jj there is not concept of a "currently tracked branch"."
- **S052** https://docs.jj-vcs.dev/latest/working-copy/ (no version or last-updated line served; docs/working-copy.md at main a497458, 2026-09-17; SrcJjWorkingCopy): "Most `jj` commands you run will commit the working-copy changes if they have changed."
- **S053** https://docs.jj-vcs.dev/latest/config/ (`latest` = v0.46.0 per versions.json; no last-updated line served; SrcJjConfigSnapshot): "All new files in the working copy that don't match the ignore patterns are tracked by default."
- **S054** https://docs.jj-vcs.dev/latest/technical/architecture/ (`latest` = v0.46.0; § GitBackend; companion quote on the S051 page § Format mapping details: "Commits created by `jj` have a ref starting with `refs/jj/` to prevent GC."; SrcJjKeepRefs): "the `GitBackend` stores a ref for each commit in the operation log in the `refs/jj/keep/` namespace"
- **S055** https://docs.jj-vcs.dev/latest/bookmarks/ (`latest` = v0.46.0; page text identical to /v0.46.0/bookmarks/; SrcJjBookmarks): "if you create a `bar` branch in the backing Git repo, then a subsequent `jj git import` will create a `bar` bookmark"
- **S056** https://github.com/jj-vcs/jj/blob/v0.46.0/CHANGELOG.md (§ [0.36.0] - 2025-12-03 › Breaking changes, lines 1438-1439 at tag v0.46.0; implementation `RESERVED_DIR_NAMES` lib/src/local_working_copy.rs:822, :1745-1756; SrcJjNestedRepo): "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored. Note that Git submodules are unaffected by this."
- **S057** https://git-scm.com/docs/git-config ("last updated in 2.56.0"; § status.showUntrackedFiles; companion: git-status 2.53.0 default sentence; SrcGitShowUntracked): "This variable can be overridden with the -u|--untracked-files option of git-status[1] and git-commit[1]."
- **S058** https://git-scm.com/docs/git-worktree ("last updated in 2.56.0", "2.55.0 no changes"; § DETAILS; git-config pinned /docs/git-config/2.55.0 § status.showUntrackedFiles; SrcGitWorktreeConfig): "When extensions.worktreeConfig is enabled, the config file .git/worktrees/<id>/config.worktree is read after .git/config is."
- **S059** https://git-scm.com/docs/gitattributes ("last updated in 2.56.0"; § DESCRIPTION, gitattributes.adoc:69-71 at tag v2.56.0; gitrepository-layout "last updated in 2.49.0", "2.49.1 → 2.56.0 no changes", § info/attributes; SrcGitRepoLayoutAttrs): "When deciding what attributes are assigned to a path, Git consults `$GIT_DIR/info/attributes` file (which has the highest precedence)"
- **S060** https://git-scm.com/docs/git-rev-list ("last updated in 2.56.0"; § OPTIONS › Commit Limiting › --all; installed git 2.56.0-1 roff verbatim; SrcGitRevAll): "Pretend as if all the refs in refs/, along with HEAD, are listed on the command line as <commit>."
- **S061** https://docs.python.org/3/builtins/stdtypes.html#str.lstrip (Python 3.15.0 docs, footer "Last updated on Oct 20, 2026"; /3/library/stdtypes.html 301s to /3/builtins/; str.removeprefix on the same page; SrcPyLstrip): "The *chars* argument is not a prefix; rather, all combinations of its values are stripped:"
- **S062** https://man7.org/linux/man-pages/man7/fifo.7.html (Linux man-pages 6.19, 2026-02-08; § DESCRIPTION; open(2) § O_NONBLOCK same revision; SrcFifo7): "Normally, opening the FIFO blocks until the other end is opened also."
- **S063** https://git-scm.com/docs/git-gc ("last updated in 2.52.0", "2.53.0 → 2.56.0 no changes"; § NOTES first paragraph — the same sentence continues "and anything else in the refs/* namespace"; installed git-gc(1) 2.56.0-1 roff 412 verbatim; SrcGitGcReachability): "it will keep not only objects referenced by your current set of branches and tags, but also objects referenced by the index, remote-tracking branches, reflogs"

Registry changes (old → new): S051–S063 absent (registry ended at S050, `corpus/SOURCES.md:64` at ddb7347) → opened 2026-10-20, recheck on-release; S056, S057, S058, S059, S061, S062 absent → mined, used-by this lesson; S051, S054, S055, S063 absent → mined, used-by `corpus/knowledge/jj-colocation-receipts.md`; S060 absent → mined, used-by `corpus/knowledge/jj-colocation-receipts.md` or this lesson (seat allows either); S052 (jj working-copy) and S053 (jj config snapshot) absent → queued, used-by `—`, flip queued → mined when the knowledge entry cites them. Every mined row above keeps its seat's landing condition: if its used-by path does not exist at paste time, land it `queued`/`—` and log the flip old→new in this Gate. No existing row's status, recheck, teaches or used-by cell changes: S044 stays rejected for its own scope and its r16 "open, r17" `status.showUntrackedFiles` note is answered by S057/S058 here without a cell edit (not a supersede); S057/S058 share git-config's URL with S042 and S059 shares gitattributes' URL with S045 under new scopes, so the census prints the standing W04 duplicate-url warnings with exit 0 (S035/S036/S038/S049 precedent). Requires a "Round-17 provenance" header paragraph in `corpus/SOURCES.md` on the round-16 pattern (`corpus/SOURCES.md:9`).
```

Line-level format notes: numbering is the context's planned S051–S063 assignment (S051 git-compatibility, S052 working-copy, S053 config snapshot, S054 refs/jj/keep, S055 bookmarks, S056 nested .git/.jj, S057 showUntrackedFiles, S058 config.worktree/includes, S059 info/attributes, S060 rev-list --all, S061 lstrip/removeprefix, S062 fifo/open, S063 git-gc reachability). Word counts, all ≤25: 25, 14, 17, 16, 22, 21, 13, 13, 18, 19, 15, 12, 25.

## 2. Per-quote verification record (my fetch, 2026-10-20)

| id | seat quote check | my result | stamp I observed on the page |
|---|---|---|---|
| S051 | SrcJjGitCompat "present verbatim: True" | VERBATIM (as-quoted, flat) | `latest` = v0.46.0 (versions.json); no last-updated line |
| S052 | SrcJjWorkingCopy "in normalized text: True" (pinned md a497458) | VERBATIM (as-quoted) | no version/last-updated line |
| S053 | SrcJjConfigSnapshot `grep -c -F` → 1 | VERBATIM (as-quoted) | `latest` = v0.46.0 |
| S054 | SrcJjKeepRefs Q2/Q3 line-anchored at tag v0.46.0 | VERBATIM (as-quoted; Q1 on git-compatibility also) | `latest` = v0.46.0 |
| S055 | SrcJjBookmarks "latest==v046 text: True", all quotes FOUND | VERBATIM (as-quoted) | `latest` = v0.46.0 |
| S056 | SrcJjNestedRepo grep at tag v0.46.0 lines 1438-1439 | VERBATIM (as-quoted, raw md) | tag v0.46.0 (2026-10-07) |
| S057 | SrcGitShowUntracked roff 11936-11939 + web | VERBATIM (as-quoted incl. `[1]` brackets) | "git-config last updated in 2.56.0" |
| S058 | SrcGitWorktreeConfig Q1 § DETAILS :595 | VERBATIM (as-quoted) | "git-worktree last updated in 2.56.0" |
| S059 | SrcGitRepoLayoutAttrs adoc:69-71 at v2.56.0 | VERBATIM (as-quoted); gitrepository-layout corroboration VERBATIM | "gitattributes last updated in 2.56.0"; "gitrepository-layout last updated in 2.49.0" |
| S060 | SrcGitRevAll page + installed roff byte-identical | VERBATIM (as-quoted) | "git-rev-list last updated in 2.56.0" |
| S061 | SrcPyLstrip in served page | VERBATIM (as-quoted) | "Last updated on Oct 20, 2026"; "Python 3.15.0 documentation" |
| S062 | SrcFifo7 roff 22-34 wrapped-line match | VERBATIM (as-quoted); open(2) O_NONBLOCK sentence VERBATIM | "Linux man-pages 6.19" |
| S063 | SrcGitGcReachability A web+man True; D web True | VERBATIM (A as-quoted; D as-quoted) | "git-gc last updated in 2.52.0" |

## 3. Exact commands run (with outputs)

1. `read corpus/lessons/round-16.md:raw:24-35` → heading `:24`, eight `- **S0NN** URL (provenance): "quote"` lines, `Registry changes (old → new): …` at `:35`.
2. `read` of all 13 `w1/Src*.md` by exact name (quotes, drafted rows, landing conditions as cited above).
3. `read corpus/SOURCES.md` → registry ends S050; header `:9` round-16 provenance; S042/S044/S045 cells as described.
4. Kernel cell 1 — urllib GET + tag-strip + substring test of 17 quotes/pages. Result line: `S051 VERBATIM words=25 … S054q1 VERBATIM words=13 … S052 VERBATIM words=14 … S053 VERBATIM words=17 … S054 VERBATIM words=16 … S055 VERBATIM words=22 … S056 VERBATIM words=21 … S057 NOT-FOUND … S058 NOT-FOUND … S059 VERBATIM words=18 … S059b VERBATIM words=13 … S060 NOT-FOUND … S061 VERBATIM words=15 … S062 VERBATIM words=12 … S062b NOT-FOUND … S063 VERBATIM words=25 … S063d VERBATIM words=7`; stamps: git-config 2.56.0, git-worktree 2.56.0, gitattributes 2.56.0, gitrepository-layout 2.49.0, git-rev-list 2.56.0, git-gc 2.52.0, Python "Last updated on Oct 20, 2026" + "Built-in Types — Python 3.15.0 documentation", man-pages 6.19, jj versions.json latest v0.46.0.
5. Kernel cell 2 — diagnosis: all four misses match under flat normalization; snoops show the served sentences verbatim, e.g. git-worktree "…config.worktree is read after .git/config is." and rev-list "--all Pretend as if all the refs in refs/, along with HEAD, are listed on the command line as <commit>."
6. `git show ddb7347:corpus/SOURCES.md | grep -n -E 'Round-16 provenance|^\| S0(49|50) '` → `:9`, `:63`, `:64`; `git show ddb7347:corpus/lessons/round-16.md | grep -n …` → `:24`, `:26`, `:35`; `git diff --stat ddb7347 -- corpus/SOURCES.md corpus/lessons/round-16.md` → empty; `ls corpus/lessons/round-17.md` → exit 2 (absent).

## 4. Findings (falsify) for L1

1. **S051 id collision — six seats each drafted "S051".** SrcJjGitCompat, SrcJjWorkingCopy (§4), SrcJjBookmarks, SrcJjKeepRefs, SrcGitWorktreeConfig, SrcGitRevAll and SrcGitGcReachability each state "next unused id is S051" for their own row. Pasting any report verbatim duplicates the id. The context numbering resolves it (S051=git-compatibility … S063=git-gc); renumber on paste — seats state no other cell depends on the number.
2. **Drop SrcJjWorkingCopy's optional §4b row.** It drafts a second, `queued` row for the git-compatibility URL, which is S051. Its own instruction says drop it if a sibling drafted the page — SrcJjGitCompat did. Nothing else in w1 duplicates a planned id's URL except the declared overlaps already carried in the registry sentence (S042/S057/S058 git-config, S045/S059 gitattributes).
3. **Word-count nits (compliance unaffected).** SrcFifo7 labels its primary quote 11 words; it is 12. S063's quote A is 25 words exactly (cap). S059's secondary gitrepository-layout sentence is 13 words as I struck it (seat counted its longer `info/attributes` —prefixed form, 15).
4. **S062 scope fence.** fifo(7)/open(2) ground only the blocking-open hazard for a FIFO and `O_NONBLOCK`; the *hardlinked* half of D2 has no support on these pages (SrcFifo7's own finding; a hardlinked regular file is `S_ISREG` and needs a separate `st_nlink > 1` branch). The Gate line must not be cited for the hardlink refusal.
5. **S063 quote fence.** Quote A is the survival leg; the decisive `refs/*` clause is the same sentence's continuation (recorded after the quote in the line). The seat's quote B (`--prune` default) is man-verbatim only — the web render inserts a space ("gc.pruneExpire ).") — so B stays out of the Gate line. git-gc(1) names neither HEAD nor `refs/jj` (0 occurrences each); C3(a)'s "never HEAD" is consistent with, not sourced from, this page.
6. **Landing order gate.** `corpus/lessons/round-17.md` is absent and `corpus/knowledge/jj-colocation-receipts.md` is an uncommitted draft that does not yet cite S051/S063 (SrcGitGcReachability `grep 'S051'` → no citation). Any mined row pasted before its used-by path exists trips the frozen census `missing:` check — hence the `queued`-fallback clause written into the registry sentence. S052/S053 have no planned citing file at all; they stay `queued` unless the knowledge entry grows their citations.

## 5. Verdict

holds — the draft is complete for S051–S063, every quote verbatim-confirmed by an independent same-day fetch, the registry sentence covers every status/used-by transition with no change to any existing row. Smallest fix for L1: paste §1, renumber per the context (finding 1), drop the §4b duplicate row (finding 2), and honor the queued-fallback/landing-order clause (finding 6).
