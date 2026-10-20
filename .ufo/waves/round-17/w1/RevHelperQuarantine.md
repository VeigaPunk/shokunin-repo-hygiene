STATUS: DONE — file-target quarantine commits land through `jj-lane.sh` v2 and are index-independent; a quarantined tracked **directory** is silently dropped by the helper ("nothing to commit", exit 0), and any commit of the move before stage 4 poisons the second check.

# RevHelperQuarantine — `souji-quarantine.sh` × `scripts/hyaku/jj-lane.sh` v2 (round 17, wave 1)

Seat: leaf reviewer. No delegation, no commits, no `jj` invocation of any kind, no git write
in the lane or any fleet repo. Static reading only, per lane bounds.

Reviewed bytes (pinned):
- `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh` sha256 `df4075112c36bae8…b06b168c4`;
  `git -C <lane> diff --stat 5fa6017 -- tools/souji-quarantine.sh` → **empty** (byte-identical to the
  round-16 base; the C3 ref-list edits are landing elsewhere, the :518/:566 region is untouched).
- `/home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh` sha256 `3369dc27b4909a9d…b9024e421`;
  `git -C <fleet> status --porcelain -- scripts/hyaku/jj-lane.sh` → **empty** (committed v2).

Installations: none (nothing needed; no pacman/uv/npx transaction attempted).

## 0. Axes and what moved them

| axis | question this seat answers | direction |
|---|---|---|
| C1 operability | does the sanctioned commit path actually record what the tool did? | decides it |
| C2 calibration | is "the helper lands deletions/renames" true for every target class the tool accepts? | corrects a claim |
| C3 coverage | is the jj recipe in C3(d) executable end-to-end, in the right order? | decides the ordering rule |

## 1. Direct answers

### Q1 — naming both `<rel>` and `<qpath>` (target still staged, i.e. between stage 2 and stage 5)

**Yes: one commit contains the deletion and the addition, and it is pushed.** Mechanics, all
verified by reading:

1. `qpath` exists on disk → `elif [ -e "$q" ] || [ -L "$q" ]` (`jj-lane.sh:537-539`): `req+=`, `files+=`,
   `fs_files+=("root-file:…")`.
2. `rel` is gone from disk but present in `refs/heads/$branch` → `elif git cat-file -e
   "refs/heads/$branch:$q"` (`:543-546`): `req+=`, `fs_req+=("root-file:…")` — the v2 deletion branch
   that closes audit F1.
3. `jj file track --include-ignored -- "${fs_files[@]}"` (`:560`) records `qpath` in `@`
   (`snapshot.auto-track="none()"`, so track is mandatory — `:29`, `:68`).
4. `jj diff --summary -- "${fs_req[@]}"` (`:570`) sees `D rel` + `A qpath` (or `R`/`C`; the sweep
   parser handles `R` and `C`, `:632-648`).
5. `jj commit -m "$msg" -- "${fs_req[@]}"` (`:604`); sweep guards pass (`D rel`: `rel` absent →
   `:649-653` does not fire; both paths ∈ `req` → `path_ok` `:620-627`).
6. `jj bookmark set` (`:658-659`) then `do_push … || exit 3` (`:669`) — **the commit is published to
   `origin`**. That is the decisive fact for this flow: a mid-hold commit does not merely record the
   staging path locally, it pushes it, and the quoted `landed <hash>` contains the quarantined bytes
   at `.ufo-quarantine/<date>/<rel>`.

### Q2 — stage-5 `git rm --cached` ran first (qpath unstaged); is `qpath` still committed?

Two states must be separated, because the tool's own ordering makes only one of them reachable.

**(a) `qpath` still exists on disk** (only its git index entry was dropped — reachable only by hand or
by re-ordering, since the tool removes the file first): **yes, still committed.** jj never reads the
git index as content — `JjDocGitIndex.md:173-174` (E4: "jj reads the working tree, never the index"),
`:186-187` (E25: with `snapshot.auto-track="none()"` a git-staged new file jj does not track is
dropped to `??` by the next transaction), `:196-198` (docs: "Jujutsu will ignore Git's staging area").
`jj file track --include-ignored` (`:560`) is what admits it; the helper's own selftest case `m`
(`jj-lane-selftest.sh:291-307`) asserts the content survives a snapshot+commit that destroys the
staged entry. The index operation is irrelevant to the helper in both directions.

**(b) the real post-stage-5 state** (`souji-quarantine.sh:559` `rm -rf -- "$qpath"` runs *before*
`:566`): `qpath` is absent, so the helper takes `:547-548` — `warn: skipping missing path <qpath>` —
and `qpath` is **not** committed. That is correct: nothing remains to commit for it. If only `rel`
is named, `req` holds `rel` and the commit is exactly `D rel`.

So: stage-5's `git rm --cached` neither helps nor hurts a jj commit. It is a git-index cleanup for
plain repos, and its file-target behaviour is sound (see F4 for the directory exception).

### Q3 — does naming both paths "land the rename"?

For a **file** target, yes: the selftest cases `z23-deletion-lands` and `z24-rename-lands`
(`jj-lane-selftest.sh:658-673`) exercise exactly the post-stage-5 (`git rm`, file absent) and
both-paths-present shapes, and `z7` (`:417-427`) locks the phantom-deletion refusal.
For a **directory** target it does not — F1.

## 2. Findings

### F1 — CRITICAL: helper v2 silently drops a deleted tracked *directory*

`jj-lane.sh:543-546` writes `fs_req+=("root-file:\"<path>\"")` for **every** path that is missing on
disk but present in the branch tip. `root-file:` is an exact-file pattern; the subtree pattern is
`root:` (`jj-lane.sh:536` uses it for existing directories). jj v0.45 filesets:
`root-file:"path"` = "Matches workspace-relative file (or exact) path", `root:"path"` = "Matches
workspace-relative path prefix (file or files under directory recursively.)"
(<https://docs.jj-vcs.dev/v0.45.0/filesets/>).

The `elif` gate *does* admit a deleted directory — verified read-only in the lane:
`git -C <lane> cat-file -t master:tools` → `tree`; `git cat-file -e master:tools` → rc 0
(`cat-file -t master:tools/souji-verify.sh` → `blob`, i.e. the file branch is distinguished).

Consequence, exactly on the quarantine path:
- `souji-quarantine.sh:462-471` classifies a tracked directory (`isdir=1`, `git_tracked` true) and
  `:518` stages it with `git mv dir <qpath>`; stage 5 deletes the staged copy.
- Operator commits through the helper naming `dir` (or `dir` plus other paths): `root-file:"dir"`
  matches no diff entry → `diffout` empty → `jj-lane.sh:570-577` prints `nothing to commit`,
  **exit 0**. If other paths are named, the commit lands (and is pushed) *without* the directory
  deletion, and the cited `landed <hash>` does not contain it.
- No warning is emitted: `:551` passes because `req` is non-empty.

This is the same silent-false-success class as audit F1 (`JjAuditSouji.md:55-86`), relocated from the
"path not in argument list" shape to the "path is a tree" shape; the helper's claim that a named
deleted path is included is therefore partial. Nothing in `jj-lane-selftest.sh` covers it (z23/z24 are
files; no directory-deletion case).

Smallest fix (helper, 3 lines, no behaviour change for files):
```sh
elif [ "$(git cat-file -t "refs/heads/$branch:$q" 2>/dev/null)" = tree ]; then
  req+=("$q"); fs_req+=("root:\"$(fileset_escape "$q")\"")
elif git cat-file -e "refs/heads/$branch:$q" 2>/dev/null; then
  req+=("$q"); fs_req+=("root-file:\"$(fileset_escape "$q")\"")
```
plus a `z` case: create `d/`, commit+push, `rm -rf d`, `commit -- d`, require `landed` and
`! git -C <remote> cat-file -e <branch>:d`.

### F2 — HIGH: any commit of the move before stage 4 makes the second check fail (the documented order is self-defeating)

`second_check` for `CLASS=pushed` (`souji-quarantine.sh:1237-1253`):
- `:1240-1244` re-resolves `origin/<default>:$REL` and requires the *same object* as stage 1
  (`S18_PUSH_OBJECT`, set at `:1151-1157`). A pushed deletion makes `rev-parse "$ref:$REL"` fail →
  `default-snapshot=FAIL`.
- `:1251` `git log --format=%H HEAD --branches --not --remotes -- "$REL"` → `head-history=FAIL` for
  **any** unpushed commit touching `REL` reachable from HEAD or any branch — which is precisely a
  local quarantine-move commit (`D rel` + `A qpath`). The helper always ends in `do_push`
  (`jj-lane.sh:669`), so either branch of this check fails: pushed → `default-snapshot`; push failed
  (exit 3) → `head-history`.

Result: `SC_PASS=0` → `ABORTED` (`:548-556`), the staged copy stays in `.ufo-quarantine`, and the
tool cannot re-target it (targets under `.ufo-quarantine` are refused, `:435-439`) — the operator has to
remove the residue by hand. `SKILL.md:58` ("quarantine is a normal commit in the owning repo") read as
"commit at move time", plus `:61` hold, plus `:62` second check, therefore cannot pass for the
`pushed` class. In a jj lane it is worse: `HEAD` is detached at `@-` (`JjDocHeadAttachment.md:13-26`),
so *any* interleaved jj transaction/commit touching `REL` counts as unpushed history.

Smallest fix (docs + ordering, no tool change): the move is never committed. Order is
move → hold → second check → delete → **then** commit the deletion (`D rel` only). One sentence in
SKILL step 3 and the checklist replaces "quarantine is a normal commit": "the quarantine staging copy
is never committed; only the post-deletion `D <rel>` is, after the tool reports `RESULT DELETED`."

### F3 — HIGH: `.ufo-quarantine/**` is not a protected namespace in the helper

`jj-lane.sh:532-534` blocks `.ufo`, `.ufo/state`, `.ufo/state/*`, `.ufo/watchdog.log` only; the case
patterns are exact, so `.ufo-quarantine/<date>/<rel>` passes every guard. Combined with Q1 and `:669`,
a commit issued during the hold publishes the artifact's bytes to `origin` at a path the tool intends
to delete minutes later; the bytes stay in history after the deletion commit. Naming the quarantine
*directory* is worse than naming one `qpath`: it takes the `-d` branch (`:535-536`, `root:` = recursive)
and `jj file track -- "${fs_dirs[@]}"` (`:562-565`) tracks the whole subtree, so every target staged
that day is committed and pushed in one commit. This directly
contradicts the tool's contract that nothing leaves the repo and that the staging copy is temporary
(`souji-quarantine.sh:99-105`), and it is the one path the tool creates that the helper does not know.

Smallest fix: add `.ufo-quarantine|.ufo-quarantine/*` to the refusal case at `:532-534` and to the
header bullet at `:28`, so a mid-hold commit fails loudly instead of publishing.

### F4 — MEDIUM: stage-5 index cleanup is missing `-r`, so every tracked-**directory** quarantine leaves the staging subtree in the index

`souji-quarantine.sh:566` runs `git rm --cached --quiet -- "$qpath"` for a directory pathspec without
`-r`. git v2.47.0 `builtin/rm.c` (`cmd_rm`): after collecting matching index entries it dies with
`not removing '%s' recursively without -r` when `!recursive && seen[i] == MATCHED_RECURSIVELY`; the
paths of a directory pathspec match recursively. So for `isdir=1` targets the cleanup **always** fails
and emits `QSTAGE stage5-index … index-cleanup-skipped` (`:567`), leaving the index holding the whole
quarantine subtree (`git status` would show `AD .ufo-quarantine/<date>/<dir>/…`). File targets are
sound despite the `rm -rf` ordering: `check_local_mod` skips an entry whose `lstat` reports a missing
file (`/* It already vanished from the working tree */ continue`), so the removal proceeds.

Exposure: plain-git repos only (jj resets the index on its next transaction, `JjDocGitIndex.md:176-190`).
In a plain repo the tool's stated post-state — "the net index shows the original as staged-deleted"
(`:69-71`) — is false, and a bare `git commit` (no `-a`, no pathspec) would commit the quarantined
bytes under `.ufo-quarantine/`. The dry-run advertises the same failing command at `:502`.

Smallest fix: `git rm --cached -r --quiet -- "$qpath"` (and the same at `:502`); a tracked directory
whose entries vanished is then removed exactly like the file case.

### F5 — MEDIUM: the selftest cannot see F4 and never exercises a directory target

`P1` asserts only `printf '%s' "$porc" | grep -qF 'keep/pushed.txt'` (`:1515-1517`) — the original
path appearing anywhere in porcelain. It never asserts that the `qpath` entry is gone from the index,
and every `st_flow` target is a file or a missing registration (`:1442-1552`: `keep/*`, `.scratch/*`,
`notes.txt`, `wt-inside`). So `index-cleanup-skipped` is produced by the fixture suite without any
assertion, and a directory target — the class with two distinct defects (F1, F4) — is untested.

Smallest fix: after P1 assert `! git -C "$R" ls-files --error-unmatch -- "$R/.ufo-quarantine/…"` and
`! printf '%s' "$porc" | grep -q 'ufo-quarantine'`; add a tracked-directory P-case (git mv dir, hold 0,
delete) asserting the same two facts.

### F6 — LOW: two header claims are false under colocation

`souji-quarantine.sh:43-44` "Tracked files: `git mv` (index records the rename …)" and `:69-71`
"the net index shows the original as staged-deleted". In a jj-colocated repo the index is reset to the
parent tree of `@` by any transaction and staged entries are discarded (`JjDocGitIndex.md:180-187`,
`:190-193`), so "index records the rename" is not durable state; and for directory targets the second
claim is false in plain git too (F4). Fix: qualify both sentences with "(plain git; a jj transaction
resets the index)" and "file targets".

### F7 — LOW: helper diagnostics conflate a typo with a quarantined path, and a lost branch is fail-open

`:548` prints the same `warn: skipping missing path` for a typo, a path deleted by quarantine, and a
path the branch tip never had. Also `tip` is read after the loop (`:553`), so with only missing paths
and a missing `refs/heads/$branch`, `:551`'s `req` check can pass and `:553-554` exits 1 — but a
*typo-only* request silently reaches `nothing to commit (no such paths)`, exit 0. Fix: read `tip`
before the loop; make `:548` say "not on disk and not in refs/heads/<branch>: no change recorded".

## 3. What the operator needs to be told (C3(d) wording)

1. **Order is fixed:** run the tool to `RESULT DELETED` (exit 0) *first*; commit the deletion *after*.
   A commit of the move before stage 4 aborts the run and strands the residue (F2).
2. **Name `<rel>`, not `<qpath>`.** After a successful run `qpath` is gone, so naming it produces
   `warn: skipping missing path` and commits nothing for it; the deletion is recorded by naming the
   original path (`jj-lane.sh:543-546`). Never name the staging path while it exists: that publishes
   the artifact (Q1, F3).
3. **Never stage for jj.** `git add`/`git rm` state does not survive the next jj transaction
   (`JjDocGitIndex.md:186-187`, selftest case `m`); the helper tracks named files itself.
4. **Directories are currently unsafe:** a quarantined tracked directory cannot be committed by the
   helper (F1). Until the `root:`/`root-file:` fix lands, treat `nothing to commit` after a directory
   quarantine as a failure and verify with `git -C <lane> cat-file -e <branch>:<dir>` (expect rc ≠ 0).
5. **Do not run any mutating jj command during the 450 s hold.** `HEAD` is `@-` and the second check is
   HEAD/`refs/heads`-based (`souji-quarantine.sh:1237-1253`); a stray commit or bookmark move flips it
   to ABORTED.
6. **In a plain-git repo, never run a bare `git commit` after a directory quarantine** until F4 is
   fixed: the index still holds the staged subtree.

## 4. Residual risk (disclosed, not defects)

- **C3(b) keep refs make post-commit re-verification refuse.** Once the `--glob=refs/jj/keep/*` heads
  land in the unpushed-touching queries (`souji-quarantine.sh:299/:931/:1251`), jj's keep refs retain
  the pre-commit working-copy commits that touched `rel`; a re-run of the receipt on the same path in a
  jj lane can then read as "unpushed commit touching the path" and go NOT-SAFE. Conservative and
  disclosed in the claim; the operator should expect it after any helper commit in that lane.
- **Stage-4 prong1 for the stale class is index-sensitive.** `git status --porcelain
  --untracked-files=all` on `qpath` (`:919`) changes from `A` to `??` if a jj transaction runs during
  the hold; the receipt is path-local, so the verdict should not change, but this is inference, not
  observed.
- **`git mv` under a stale/odd index** fails closed (`STAGE2-FAILED` with the original reported,
  `:511-527`); no cross-tool data loss.

## 5. Verification actually performed

| command | output |
|---|---|
| `sha256sum tools/souji-quarantine.sh scripts/hyaku/jj-lane.sh` | `df407511…b06b168c4` / `3369dc27…b9024e421` |
| `git -C <lane> diff --stat 5fa6017 -- tools/souji-quarantine.sh` | empty (region unchanged since base) |
| `git -C <fleet> status --porcelain -- scripts/hyaku/jj-lane.sh` | empty |
| `git -C <lane> cat-file -t master:tools` / `-e` / `-t master:tools/souji-verify.sh` | `tree` / rc 0 / `blob` |
| `man git-rm` | "When --cached is given, the staged content has to match either the tip of the branch or the file on disk" |
| `strings $(command -v git)` | `the following file has staged content different from both the` / `the following file has local modifications:` |
| git v2.47.0 `builtin/rm.c` (read) | vanished-file early `continue` in `check_local_mod`; `not removing '%s' recursively without -r` in `cmd_rm` |
| jj v0.45.0 filesets doc (read) | `root-file:"path"` = file/exact; `root:"path"` = prefix recursive |

Not run (lane bounds): either tool, the helper selftest, any jj subcommand, any git write. The
selftest cases z23/z24/z7/m are cited as **code**, not as observed output. F1/F4 falsify with the
two fixtures named above; F2 falsifies by committing the move in a scratch clone before stage 4 and
observing `head-history=FAIL`.

## 6. Verdicts

| question | verdict |
|---|---|
| both paths named, target staged → one commit with `D rel` + `A qpath` | **holds** (file targets; `:537-546,:560,:570,:604`) |
| stage-5 `git rm --cached` before the helper prevents `qpath` from being committed | **fails** — jj commits from the worktree; it is committed whenever it exists (Q2a) |
| same, after the tool's actual stage 5 (file already `rm -rf`'d) | **holds** — dropped with a warning, deletion committed (Q2b) |
| helper v2 lands a deleted *file* and refuses phantom deletions | **holds** (z23/z24/z7, F1 residual closed for files) |
| helper v2 lands a deleted tracked *directory* | **fails silently** (F1) |
| committing the quarantine move at SKILL step 3 can still pass the second check | **fails** (F2) |
| `.ufo-quarantine/**` cannot enter a helper commit | **fails** (F3) |
| stage-5 index cleanup is complete for every tracked target | **fails for directories**, holds for files (F4) |

Smallest integrated fix set: helper `root:`-for-tree (`:543`) + `.ufo-quarantine` refusal (`:532`) +
doc order "commit only after DELETED, name only `<rel>`" + `-r` at `:566/:502` + the two fixture
assertions. None of these changes plain-repo read behaviour or the byte-identical plain path C3(b)
requires.
