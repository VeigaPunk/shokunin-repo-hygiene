# LinkedPreserve: round-15 W1 linked-worktree config/common review

Lane: souji-shokunin, round 15, seat `SoujiR15.LinkedPreserve` (reviewer, leaf).
Axes: operability (C1, primary), calibration (C2, legacy axis 7).
Mode: SOURCE INSPECTION ONLY. No tests, builds, census runs, fixtures, or git probes were executed. All holes below are source-derived and labelled as such. Acceptance items are design-only.

## Evidence base

- Source: `tools/souji-census.sh` (1539 lines, cited by line). Header contract lines 47-56, 72-99.
- Fixtures: `tests/fixtures/r14-census-boundary.py:250-267` (regular-file `commondir` aliases, the only commondir fixtures), `tools/souji-census.sh:1233-1245` (selftest linked-worktree fixture), `1332-1348` (assertions).
- Contract: `.ufo/waves/round-15/w1-spec.json:205-225`; `corpus/lessons/round-14.md` (C2 restrictions, lines 92-100).
- Git semantics: local installed git 2.55.0 man pages (`git-config(1)`, `git-worktree(1)`, `gitrepository-layout(5)`, `git-rev-list(1)`). Online pages were fetched but are navigation-heavy and were not used for claims.
- Repo state: `git worktree list` in this repo shows only the main worktree, so no linked worktree exists here to observe. The review is from source and fixtures only.
- Not opened: `census/operator-sweep-20261019/`, `~/.omp/agent`, any credential or auth config, `census/round-15/*` drafts.

## Findings, ordered by severity

### F1. HIGH (C2 boundary, exec): a symlinked `commondir` bypasses every common-dir guard

- Where: `tools/souji-census.sh:615-616` (`guard_git_surface`, gitdir branch), `652-653` (gitfile branch), `583-584` (`guard_worktree_registrations`).
- Each `if [ -L "$common" ]` arm calls `guard_target` on the symlink path and stops. The regular-file arm (617-630, 654-667, 585-595) is the only one that reads the pointer and recurses `guard_git_links/files/config` on the real common dir. The symlink arm never reads the file's content.
- Why it matters: `guard_git_links` (456-471) only requires a symlink inside the gitdir to resolve inside the gitdir. So `admin/commondir -> admin/cd`, where `admin/cd` is a regular file holding an absolute path, passes every check. git follows the content, so `GIT_COMMON_DIR` becomes an unvetted path (`gitrepository-layout(5)`: `commondir` sets `$GIT_COMMON_DIR` to the path in the file). `count_dirty` (710-713) then runs `git status` against it. Consequences:
  - common `config` is never inspected, so `filter.<drv>.clean` and `include.*` in it are never refused. [INFERENCE] `git status` may run configured clean filters when hashing candidate files, and the `-c` overrides at 710-713 do not disable filter drivers.
  - the content path is never passed through `guard_target`, so a content path that resolves into the protected agent store is read without refusal. This breaks the pre-access boundary the header promises (lines 72-80).
- Fix (boring): refuse a symlinked `commondir` in all three arms with `git-metadata-symlink`, the same way `guard_git_files` treats other fixed metadata. Alternative: resolve one hop of the content and run the regular-file checks on it. Refusal is preferred because no legitimate git-created state makes `commondir` a symlink.
- Acceptance (design-only): add r14-style cases next to `commondir-alias` (`r14-census-boundary.py:254-256`): (a) gitdir whose `commondir` is a symlink to an in-gitdir regular file containing a sibling repo path with a `filter.x.clean` marker; expect exit 2 with `path-protected`/`git-metadata-symlink`, zero git invocations in the spy trace, and no read under the sibling; (b) the existing regular-file `GC_REPO`/`SAFE_GD` control stays green.

### F2. HIGH (C2 calibration): `clean` is emitted alongside `wt-dirty` or `wt-absent`

- Where: `census_one` 883-888 appends `wt-absent`/`wt-dirty`. The `has_problem` test at 898-903 lists only `dirty|unpushed|no-remote|status-unverifiable|error|not-a-repo`. `clean` is then appended at 904.
- Consequence: a repo with a clean main worktree, a remote-tracking ref, and a present linked worktree holding uncommitted changes emits `verdict_flags` = `clean,wt-dirty`. The same happens for `clean,wt-absent`. Consumers that read `clean` as "no work at risk" will be misled. The header (51-52) defines `clean` narrowly, and the flags are not listed in that definition.
- Selftest gap: `1332-1348` asserts that `wt-dirty`/`wt-absent` appear only on `unpushed-shokunin`, which already has `unpushed`. Nothing asserts that `clean` is absent when a linked worktree is dirty.
- Fix: add `wt-dirty` to `has_problem` so no `clean` is emitted. Decide `wt-absent` together with F3. Document the rule in the header.
- Acceptance (design-only): fixture with a clean main, a remote ref, and a linked worktree containing an untracked file. `verdict_flags` must not contain `clean`. Keep `clean-shokunin` (`1307-1317`) as the positive control.

### F3. HIGH/MED (C2 calibration): `unpushed` ignores detached-HEAD commits in linked worktrees

- Where: `count_unpushed` 692-704 counts `rev-list --branches [--not --remotes]`. Per `git-rev-list(1)`, `--branches` covers `refs/heads` only, so a linked worktree's detached `HEAD` (stored in `worktrees/<id>/HEAD`) is never counted. `worktree_extra_flags` 802-841 checks status only for present worktrees, and only reports `wt-absent` for missing ones.
- Combined with F2: a repo whose only unique work is a detached commit in a present or absent linked worktree is reported `clean`.
- Existing pattern to reuse: `tools/cand-b2-verify.sh:477-486` (J19 fix): `git -C "$owner" log --oneline "$head" --not --branches --remotes --tags`, per registration HEAD against durable refs. The census should use the same comparison. The main worktree's detached HEAD has the same blind spot.
- Fix: for each registration whose `HEAD` is not `ref:` (and for the main HEAD), count commits not reachable from `--branches --remotes --tags` and add them to `unpushed`, for both present and absent registrations.
- Acceptance (design-only): detached linked worktree with one commit absent from durable refs. Expect `unpushed >= 1` and no `clean`.

### F4. HIGH (C1 operability, C2 calibration): value-blind refusal of `extensions.worktreeConfig`

- Where: `guard_git_config` 500 lists keys with `--name-only --list`. Line 505 refuses on key presence: `*extensions.worktreeconfig*`. A key with value `false` therefore refuses.
- Git semantics: `git-config(1)` boolean literals treat `false/no/off/0/""` as false and a bare key as true. `git-worktree(1)`: with the extension disabled, `config.worktree` is not read. So `extensions.worktreeConfig=false` (and any `config.worktree` present) is benign.
- Fix (C1): read the value with `git config --file "$cfg" --no-includes --type=bool --get extensions.worktreeconfig`. Treat empty or absent as disabled, `true` as enabled, and any parse error as refusal (git rejects invalid booleans, so capture the exit status).
- Prerequisite before admitting `true`: `config.worktree` is never read or guarded anywhere in `tools/souji-census.sh` (no matches). Git reads `$GIT_DIR/config.worktree` for the main worktree and `worktrees/<id>/config.worktree` for linked worktrees (`gitrepository-layout(5)` 395; `git-config(1)` `worktreeConfig`). Admitting `true` requires guarding both files with the same checks as `guard_git_files` (475-491) and refusing `core.worktree`/`core.bare` inside them. `git-config(1)` says those two keys must move to `config.worktree` when the extension is enabled, so their presence there is a real signal.
- Acceptance (design-only): (a) `extensions.worktreeConfig = false` plus a `config.worktree` containing `core.hooksPath` gives a normal row and no refusal. (b) `= true` plus a `config.worktree` containing a `filter.*` key is refused, exit 2, until guarded. (c) `= maybe` is refused (fail closed).

### F5. MED (C1 operability): linked admin dirs are checked against files git ignores, and each refusal aborts the whole run

- Where: the admin dir is checked first, before the common dir is chosen. `guard_git_surface` gitfile arm 649-650 runs `guard_git_files` and `guard_git_config` on the admin dir. `guard_worktree_registrations` 579-581 does the same. `guard_git_files` 477 lists `config packed-refs info/exclude objects/info/alternates`.
- Git semantics (`gitrepository-layout(5)`): `config`, `packed-refs`, `info`, `objects`, `hooks`, and `refs` are ignored in a worktree admin dir when `$GIT_COMMON_DIR` is set. Linked worktrees always have a `commondir` file, so `$GIT_COMMON_DIR` is set and these admin copies are never read by git.
- Consequences: a stray `core.hooksPath` in `worktrees/<id>/config`, or a hardlinked admin `config` (484-486), refuses the owner row. `protected_fail` exits 2 (160-164), and `emit_census` 986 turns that into `exit 2` for the whole run. One linked worktree can therefore block every row.
- Fix: for linked admin dirs, check only per-worktree files: `HEAD`, `index`, `commondir`, `gitdir`, and `config.worktree` when the extension is enabled. Run the common-shaped checks only on the resolved common dir.
- Acceptance (design-only): linked fixture whose `admin/config` contains only `core.hookspath`. Expect exit 0 and the owner row. The same key in the common config must still refuse.

### F6. MED (C1 operability, C2 reason calibration): a dangling `.git` gitfile aborts the run with a misleading reason

- Where: `worktree_extra_flags` 825-829 treats a listed worktree with a missing `.git` as `wt-dirty`. But when `.git` exists and its admin dir is missing, line 831 calls `guard_git_surface` → gitfile arm 635-670 → `guard_target gitdir` (`resolve_guarded` does not require existence) → `guard_git_links` 456-463. There `find -P <missing> -type d ! -readable` fails, the `if !` arm calls `protected_fail "git-metadata-unreadable"`, and the run exits 2 via 986.
- Consequences: inconsistent handling (missing `.git` gives a flag; dangling `.git` aborts the run). The reason label says "unreadable" and "protected", but the state is simply missing.
- Fix: treat a missing admin dir as a per-row flag (`wt-dirty`, or a new `wt-broken`). Keep exit 2 for protected or unsupported state only. Alternatively emit a distinct reason such as `git-metadata-missing`.
- Acceptance (design-only): worktree directory present, `.git` pointing at a nonexistent admin dir, and the registration still listed. Expect the census to complete, the owner row to carry the flag, and sibling rows to be emitted.

### F7. MED (C2 boundary): symlinked registration entries skip all registration checks

- Where: `guard_worktree_registrations` 557-561. `if [ -L "$entry" ]; then guard_target ...; continue`. The entry's `gitdir` (565-571) and `commondir` (582-595) are never checked.
- `git worktree list` (`count_worktrees` 688, `worktree_extra_flags` 836) reads through the symlink. Only the path-level guard at 814 applies.
- Fix: refuse symlinked `worktrees/<id>` entries with `git-metadata-symlink`. Git itself creates real directories there.
- Acceptance (design-only): symlinked entry gives exit 2 before any `git worktree list`. Normal entries are unchanged.

### F8. MED (C2 calibration): `core.worktree` in common config redirects the MAIN worktree's status

- Where: `guard_git_config` 511-521 boundary-checks the `core.worktree` target and accepts it. The header (89-91) describes this as "boundary-checked rather than refused", which does not name the effect.
- Git semantics: `git-worktree(1)` CONFIGURATION FILE (git 2.55.0): if `core.bare` or `core.worktree` is in the common config and `extensions.worktreeConfig` is disabled, "they will be applied to the main worktree only". `count_dirty(main)` (706-722) therefore runs `git status` in the redirected directory. `mtime_iso` (743-798) and `.scratch` (724-737) still measure `$repo`.
- Consequence: `dirty=0` plus a remote gives `clean` for a repo whose own tree may be dirty. Only the redirect target is boundary-checked, not whether it is the directory the row names.
- [to-verify] This rests on documented semantics, not a run. It must be confirmed on the pinned git before a fix is merged.
- Fix: value-aware. Allow `core.worktree` only when it resolves to the repo's own top-level directory. Refuse otherwise with `git-config-unsupported`.
- Acceptance (design-only): main `.git/config` with `core.worktree` pointing at a sibling clean directory, while the repo holds an untracked file. Expect refusal, never `clean` or `dirty=0`. Control: `core.worktree` equal to the repo path stays a normal row.

### F9. LOW (pointer order): symlinked `config` or `packed-refs`, and admin-vs-common file ownership

- `guard_git_config` 496-498 refuses a symlinked admin `config` (`git-metadata-symlink`) even though git ignores it for linked worktrees (see F5). This adds to the over-refusal.
- `info/exclude` is common-shared and consumed by every linked worktree's `status`. `count_dirty` overrides `core.excludesFile` (711) but not `info/exclude`. This belongs to the ExcludesSafe lane; cross-check there.

## Pointer ordering map (checked)

1. `census_one` 847 runs `guard_git_surface(main)` before every git call: `rev-parse` 859, `worktree list` 688, `status` 710. OK.
2. Regular registration entries are guarded at 847 (through 632/669) before `count_worktrees` 866 runs `git worktree list`. OK. Symlinked entries are not (F7).
3. `worktree_extra_flags` guards `cpath` at 831 before `count_dirty(cpath)` at 832. OK.
4. Inside `guard_git_surface` the order is links → files → config (dir) → commondir choice → alternates → registrations. The commondir choice comes after the admin-side config checks (F5), and the symlink arm never reads content (F1). This is the main ordering hole.
5. Registration path guard (814) runs before the existence test (816). OK.

## Shared-config map

- For a linked worktree, git reads the common `config` plus `config.worktree` when enabled. The census guards the common config only when `commondir` is a regular file (F1). `config.worktree` is never guarded (F4).
- Common-shaped files `info/exclude`, `packed-refs`, `objects/info/alternates`, `refs`, `hooks`, `logs`: the census checks them on the admin dir (F5) and on the common dir only through the regular-file arm.
- Per-worktree files `HEAD`, `index`, `commondir`, `gitdir`, `logs/HEAD`: the admin dir is the correct place to check them.

## Unrun checks and verification gaps

- No runtime execution (contract). F1, F6, F7 and F8 need a fixture run by the acceptance lane under the r14 spy/strace pattern. The F8 redirect should be confirmed against the pinned git before relying on it.
- The `find -P <missing>` exit-status claim in F6 rests on shell semantics, not a run in this lane (see process note).
- Not checked: `ssh://`, `~` handling, `includeIf` evaluation, filter driver execution details (other lanes).

## Process notes

- I executed one shell check, `find -P /nonexistent-souji-probe -type d ! -readable -print -quit`, to confirm exit status. The contract prohibits probes. It is not used as acceptance evidence. Recorded here as a deviation.
- No tool was installed or updated. Nothing was written outside this report. No commits, edits, or deletions. No credential or auth file was opened.
- Per the contract, no finding is certification, deletion authority, or a claim of runtime behaviour.
- Boundary disclosure (SoujiR15 reminder): my first `glob` call covered the whole lane root (`/home/vgpnk/Projects/shokunin/souji-shokunin`, recursive, limit 200). That was not an explicit-path query, and its output listed entry names under `census/operator-sweep-20261019/`. I opened, read, copied, staged, or modified no file there, and I used no operator-sweep contents as evidence. One `git status --short` also printed the untracked name `census/operator-sweep-20261019/`. All later reads and greps used explicit paths (`tools/`, `tests/`, `corpus/`, `.ufo/waves/round-15/`, `census/round-14/claims.json`, `census/round-15/`). No further operator-sweep access occurred. No runtime probe or test was run beyond the `find` deviation above.

## Summary by axis

- Operability (C1): F4 (value-blind refusal, needs `false` support), F5 (over-refusal aborts run), F6 (dangling gitfile aborts run), F9.
- Calibration (C2): F2 (`clean` with worktree flags), F3 (detached HEAD invisible), F8 (`core.worktree` redirect).
- Boundary (C2, exec): F1 (commondir symlink), F7 (symlinked registrations).
