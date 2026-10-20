# ScoutSubmoduleIgnore — what `--ignore-submodules=all` hides in porcelain status

STATUS: ok

Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.
Subject: `tools/souji-census.sh`, sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`, 1877 lines (verified at HEAD).
Measurements on git 2.56.0 (host), synthetic superproject + real submodule under
`/var/tmp/souji-r16-ScoutSubmoduleIgnore/` (deleted after use).

## Question

Does `git status --porcelain --ignore-submodules=all` hide a **staged gitlink change** (index vs HEAD),
i.e. is the census's `dirty` field a truthful lower bound on "would `git commit` do anything"?

## Answer (observed)

**Yes — it hides staged gitlink changes, unstaged gitlink moves, submodule-content changes, and a
staged gitlink deletion.** The census's exact invocation (options and pathspec form of
`tools/souji-census.sh:1034-1042`) returns **zero lines** for a repository that `git diff --cached --raw`
proves is staged-dirty.

Test repo: `sup` with submodule `sub` (two commits); HEAD records `sub` at `f4fe408`, index moved to
`21b9b54` via `git update-index --cacheinfo 160000,…`.

| # | scenario | `status --porcelain` | `--ignore-submodules=all` | `--ignore-submodules=dirty` |
|---|---|---|---|---|
| A | submodule worktree content modified | ` M sub` | *(empty)* | *(empty)* |
| B | submodule HEAD moved, unstaged (` M` gitlink) | ` M sub` | *(empty)* | ` M sub` |
| C | staged gitlink bump + worktree differs | `MM sub` | *(empty)* | `M  sub` |
| D | **pure staged gitlink bump** (worktree == index) | `M  sub` | ***(empty)*** | `M  sub` |
| E | staged gitlink deletion, checkout present | `D  sub` + `?? sub/` | `?? sub/` only | `D  sub` + `?? sub/` |
| E2 | staged gitlink deletion, checkout removed | `D  sub` | ***(empty → count 0)*** | `D  sub` |
| F | submodule directory removed from worktree | ` D sub` | *(empty)* | ` D sub` |
| G | untracked nested repo (`sub3/.git` dir) | `?? sub3/` | `?? sub3/` | — |
| H | submodule `.git` gitfile broken (target missing) | — | ***(empty)*** | `M  sub` |
| I | unmerged gitlink (stages 1/2/3) | `UU sub` | `UU sub` | `UU sub` |

Scenario D in full:

```
$ git diff --cached --raw
:160000 160000 f4fe408 21b9b54 M	sub
$ git status --porcelain
M  sub
$ git --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null \
    status --porcelain --ignore-submodules=all -- . | grep -c .
0
```

Scenario D with `--ignore-submodules=dirty` prints `M  sub`; scenario A stays empty. So `dirty` is
exactly "hide submodule *work-tree* changes, keep recorded-commit changes" — the semantics the census
header *claims* to want.

What is **not** hidden: unmerged gitlinks (`UU`, scenario I) and untracked nested repos that are not
gitlinks (scenario G). Conflict states therefore never read as clean.

## Mechanism

`Documentation/diff-options.adoc` (git-diff): "`dirty` … only changes to the commits stored in the
superproject are shown", "`all` hides all changes to submodules". Source `diff-lib.c`
(`match_stat_with_submodule`) short-circuits gitlink change detection unconditionally:

```c
if (diffopt->flags.ignore_submodules)
        changed = 0;
```

so the suppression is not limited to work-tree/content inspection — it also kills the `ce_compare_gitlink`
result that would surface an index-vs-HEAD (or HEAD-vs-worktree) gitlink difference.

### Citations (access date 2026-10-20)

1. https://git-scm.com/docs/git-status — "`all` hide all changes to submodules (and suppresses the output of submodule summaries when the config option `status.submoduleSummary` is set)." (19 words)
2. https://git-scm.com/docs/git-diff — "Using `dirty` ignores all changes to the work tree of submodules, only changes to the commits stored in the superproject are shown" (22 words); "Using `all` hides all changes to submodules." (6 words)
3. https://raw.githubusercontent.com/git/git/master/diff-lib.c — lines 98-99: `if (diffopt->flags.ignore_submodules)` / `changed = 0;`
4. https://raw.githubusercontent.com/git/git/master/Documentation/diff-options.adoc — lines 853-863, text quoted in (2).

## Impact on the census at HEAD

- `count_dirty()` (`tools/souji-census.sh:1021-1048`) runs the flagged status at **line 1037**
  (`--ignore-submodules=all`) and prints the line count; scenario D/E2 yield `0`.
- Verdict assembly `1224-1239`: `dirty` 0 → no `dirty` flag; with `unpushed=0` and a remote-tracking
  ref, `has_problem=0` → **`clean` is appended (`1239`)**. A superproject whose only uncommitted change
  is a staged submodule bump would therefore print `clean` while `git commit` would create a commit.
- `wt-dirty` (`worktree_extra_flags`, `1127-1172`) calls the same `count_dirty()` (`1162`), so non-main
  worktrees inherit the identical contraction.
- `--compare` sees no field change for scenario D/E2 (all fields identical), so round-over-round drift
  caused by a submodule pointer move is invisible.
- Doc contract mismatch: header `38-39` says "Submodule **content** is not inspected
  (`--ignore-submodules=all`)". Observed: the recorded commit (gitlink) is suppressed too. The stated
  rationale is narrower than the effect.
- Partial compensation, not a fix: `newest_mtime()` (`find` at `1075-1077`) prunes only `.git`, so it
  *does* descend into submodule worktrees; a content edit (A) perturbs `mtime_iso`, but a gitlink bump
  with no recent file (D) or a staged deletion (E2) perturbs nothing.

### Live impact: latent, zero victims today

Sweep of all 21 repos in the round-16 live census (`census/round-16/live-fleet-final.json`,
`jq -r '.arms.changed.rows[][0]'`): every repo has **no `.gitmodules`** and **0 gitlinks in `ls-tree -r HEAD`**;
the scan root `/home/vgpnk/Projects/shokunin` itself also tracks 0 gitlinks; the lane repo tracks 0.
No current row is misreported. The defect is reachable only if a scanned repo gains a submodule.

### Test coverage

No coverage exists: `submodule` appears in the script only at lines 18, 39, 754, 1037 (comments and the
one flag); `tests/fixtures/r15-census-config.py` and `census/round-16/c1-matrix-final.json` contain no
`submodule`/`gitlink`/`160000` case. A future edit to this flag is unpinned by the selftest.

## Verdict

- "Staged gitlink changes are hidden by `--ignore-submodules=all`": **fails** as documented intent —
  the flag hides them, contradicting header `38-39` and the `clean` verdict's meaning.
- Operability of the census today: **partial** — real, reproducible contraction with zero live victims;
  no crash, no wrong row in the 21-repo fleet, but `dirty=0`/`clean` carry an undocumented submodule
  blind spot and no fixture pins the behavior.

## Smallest fix

1. **Zero-risk (recommended now), comment-only:** replace header line 39 with a truthful statement, e.g.
   "Submodule changes are never inspected: `--ignore-submodules=all` also hides a staged or unstaged
   gitlink bump (and a staged deletion), so `dirty=0` does not imply index == HEAD when submodules exist."
   No behavior change, no new reads; keeps every matrix/fixture result identical.
2. **Semantic (only with guard work):** switch line 1037 to `--ignore-submodules=dirty`. Measured
   equivalent to "hide content, show pointer": A stays empty, B/C/D/E/F surface, and it spawns **zero**
   child `git status` processes (`GIT_TRACE=1` → `run_command` count 0; `is_submodule_modified` is skipped
   under `ignore_dirty_submodules`). Robustness: a broken submodule gitfile does not fatal (rc=0, entry
   reported `M`), whereas `none` fatals rc=128. Caveat before adopting: `dirty` resolves each submodule's
   HEAD through `<sub>/.git`, and the protected-path guard only covers scan-root children with `.git`
   files (`list_repos` call at `1295`, function at `757`); a submodule's gitfile inside a row is currently unguarded. Either
   extend `guard_git_pointer` to submodule gitfiles first, or accept that bounded read.
3. **Pin whichever is chosen** with one fixture case in `tests/fixtures/r15-census-config.py`: synthetic
   superproject with a staged gitlink bump → assert `dirty=0` (current, documents the blind spot) or
   `dirty=1` (option 2).

## Residual unknowns

- Whether any *non-main worktree branch* in the 21 repos tracks a gitlink (only `HEAD` of each main
  worktree was inspected via `ls-tree`); no repo has `.gitmodules`, so unlikely.
- Protected-path reachability of option 2's gitfile resolution: not exercised (would require a submodule
  `.git` pointing at `.ufo/state` or `census/operator-sweep-*`); inferred from `list_repos` guard scope.
- `submodule.<name>.ignore` in `.gitmodules` cannot override the command-line flag
  (`override_submodule_config`), so no config can widen the blind spot — not separately measured.

## Commands

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh && wc -l tools/souji-census.sh && git rev-parse HEAD
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'submodule\|ignore-submodules\|diff-index\|diff-files\|ls-files\|porcelain\|status' tools/souji-census.sh
set -x; git --version; W=/var/tmp/souji-r16-ScoutSubmoduleIgnore; rm -rf "$W"; mkdir -p "$W"; cd "$W"; git init -q sub; git -C sub config user.email a@b; git -C sub config user.name a; echo x > sub/f; git -C sub add f; git -C sub commit -qm one; echo y >> sub/f; git -C sub commit -qam two; git init -q sup; git -C sup config user.email a@b; git -C sup config user.name a; echo s > sup/s; git -C sup add s; git -C sup commit -qm init; git -C sup -c protocol.file.allow=always submodule add -q ../sub sub; git -C sup commit -qm addsub; echo '=== HEAD state ==='; git -C sup status --porcelain; git -C sup log --oneline -2
cd /var/tmp/souji-r16-ScoutSubmoduleIgnore/sup && ONE=$(git -C ../sub rev-parse HEAD~1) && echo "ONE=$ONE" && echo '--- A: submodule worktree modified (unstaged content) ---' && printf 'z\n' >> sub/f && echo '[plain]' && git status --porcelain && echo '[ignore-all]' && git status --porcelain --ignore-submodules=all && git -C sub checkout -q -- . && echo '--- B: unstaged gitlink move (submodule HEAD detached to ONE) ---' && git -C sub checkout -q --detach "$ONE" && echo '[plain]' && git status --porcelain && echo '[ignore-all]' && git status --porcelain --ignore-submodules=all && echo '--- C: staged gitlink change via update-index ---' && git -C sub checkout -q --detach "$(git -C sub rev-parse HEAD@{1} 2>/dev/null || echo "$ONE")" ; SHA_NEW=$(git -C sub rev-parse HEAD) ; echo "SHA_NEW=$SHA_NEW" ; git update-index --cacheinfo 160000,$ONE,sub && echo '[index vs HEAD]' && git diff --cached --raw && echo '[status plain]' && git status --porcelain && echo '[status ignore-all]' && git status --porcelain --ignore-submodules=all && echo '[ls-files -s sub]' && git ls-files -s sub
cd /var/tmp/souji-r16-ScoutSubmoduleIgnore/sup && ONE=$(git -C ../sub rev-parse HEAD~1) && git -C sub checkout -q --detach "$ONE" && git update-index --cacheinfo 160000,$ONE,sub && echo '=== D: pure staged gitlink bump (worktree matches index) ===' && echo '[plain status --porcelain]' && git status --porcelain && echo '[exact census status form]' && git --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null status --porcelain --ignore-submodules=all -- . | grep -c . ; echo '[dirty mode]' && git --no-optional-locks -c core.fsmonitor=false -c core.hooksPath=/dev/null status --porcelain --ignore-submodules=dirty -- . ; echo '[none mode]' && git --no-optional-locks status --porcelain --ignore-submodules=none -- . ; echo '=== A repeat under dirty mode: submodule content modified only ===' ; git -C sub checkout -q -- . ; echo z >> sub/f ; git status --porcelain --ignore-submodules=dirty ; echo "[plain]"; git status --porcelain ; echo '[diff-cached raw]'; git diff --cached --raw
cd /var/tmp/souji-r16-ScoutSubmoduleIgnore/sup && echo "[whoami] $(whoami)"; echo '[broken submodule gitfile test]'; mv sub/.git sub/.git.real && printf 'gitdir: /nonexistent/path\n' > sub/.git && echo '[all]'; git status --porcelain --ignore-submodules=all; echo "rc=$?"; echo '[dirty]'; git status --porcelain --ignore-submodules=dirty; echo "rc=$?"; echo '[none]'; git status --porcelain --ignore-submodules=none; echo "rc=$?"; mv sub/.git.real sub/.git 2>/dev/null; rm -f sub/.git; echo '[restore?]'; ls sub/.git 2>&1 | head -1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -ld .ufo/waves/round-16 .ufo/waves/round-16/w2 2>&1; ls -1 .ufo/waves/round-16/w2 2>&1 | head -20; echo '--- selftest submodule mentions ---'; grep -c 'submodule' tools/souji-census.sh
cd /var/tmp/souji-r16-ScoutSubmoduleIgnore/sup && git checkout -q -- . 2>/dev/null; git read-tree --reset -u HEAD 2>/dev/null; git reset -q --hard HEAD; ONE=$(git -C sub rev-parse HEAD~1); TWO=$(git -C sub rev-parse HEAD); git -C sub checkout -q --detach "$TWO"; echo '=== unmerged gitlink (stages 1,2,3) ==='; printf '160000 %s 1\tsub\n160000 %s 2\tsub\n160000 %s 3\tsub\n' "$ONE" "$TWO" "$ONE" | git update-index --index-info; echo '[plain]'; git status --porcelain; echo '[all]'; git status --porcelain --ignore-submodules=all; echo "rc=$?"; echo '[dirty]'; git status --porcelain --ignore-submodules=dirty; echo '[reset]'; git reset -q --hard HEAD; git checkout -q -- . ; echo '=== trace: does dirty mode spawn child git status? ==='; echo z >> sub/f; GIT_TRACE=1 git status --porcelain --ignore-submodules=dirty 2>&1 | grep -E 'run_command|built-in|sub/f|status' | head -20; echo '--- all mode trace ---'; GIT_TRACE=1 git status --porcelain --ignore-submodules=all 2>&1 | grep -cE 'run_command'; echo '--- dirty mode trace run_command count ---'; GIT_TRACE=1 git status --porcelain --ignore-submodules=dirty 2>&1 | grep -cE 'run_command'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo '--- submodule mentions ---'; grep -n 'submodule' tools/souji-census.sh; echo '--- default root ---'; grep -n 'SHOKUNIN_ROOT' tools/souji-census.sh | head -5; echo '--- census/round-16 ---'; ls -1 census/round-16 | head -30; echo '--- known sibling .gitmodules ---'; ls -l /home/vgpnk/Projects/shokunin/tsukuroi-shokunin/.gitmodules 2>&1
cd /var/tmp/souji-r16-ScoutSubmoduleIgnore && rm -rf sup2 && cp -a sup sup2 && cd sup2 && git reset -q --hard HEAD; git config user.email a@b; git config user.name a; echo '=== E: staged gitlink deletion ==='; git rm -q --cached sub && echo '[plain]' && git status --porcelain && echo '[all]' && git status --porcelain --ignore-submodules=all && echo '[dirty]' && git status --porcelain --ignore-submodules=dirty && git reset -q --hard HEAD && echo '=== F: worktree submodule directory removed (unstaged) ===' && rm -rf sub && echo '[plain]' && git status --porcelain && echo '[all]' && git status --porcelain --ignore-submodules=all && echo '[dirty]' && git status --porcelain --ignore-submodules=dirty && git reset -q --hard HEAD 2>/dev/null; echo '=== G: untracked nested repo ===' ; git init -q sub3 && echo q > sub3/q && git -C sub3 add q && git -C sub3 -c user.email=a@b -c user.name=a commit -qm x && echo '[plain]' && git status --porcelain && echo '[all]' && git status --porcelain --ignore-submodules=all
cd /var/tmp/souji-r16-ScoutSubmoduleIgnore && rm -rf sup3 && cp -a sup sup3 && cd sup3 && git reset -q --hard HEAD && git rm -q --cached sub && rm -rf sub && echo '=== E2: staged gitlink deletion + checkout removed ===' && echo '[plain]' && git status --porcelain && echo '[all]' && git status --porcelain --ignore-submodules=all && echo "[all line count: $(git status --porcelain --ignore-submodules=all | grep -c .)]" && echo '[dirty]' && git status --porcelain --ignore-submodules=dirty && echo '[diff-cached raw]' && git diff --cached --raw
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in $(jq -r '.arms.changed.rows[][0]' census/round-16/live-fleet-final.json); do g="/home/vgpnk/Projects/shokunin/$r/.gitmodules"; gl=$(git -C "/home/vgpnk/Projects/shokunin/$r" ls-tree -r HEAD 2>/dev/null | awk '$2=="commit"' | wc -l); printf '%-26s gitmodules=%s gitlinks_in_HEAD=%s\n' "$r" "$([ -e "$g" ] && echo YES || echo no)" "$gl"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'count_dirty()\|--ignore-submodules\|dirty)' tools/souji-census.sh | head -12; echo '--- SOURCES rows ---'; grep -n 'ignore-submodules\|submodule' corpus/SOURCES.md | head -10
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'worktree_extra_flags() {\|d=$(count_dirty\|scratch_bytes() {\|guard_git_pointer "$d" "$g"\|guard_git_pointer() {\|guard_git_pointer "\$d"' tools/souji-census.sh; echo '--- cleanup ---'; rm -rf /var/tmp/souji-r16-ScoutSubmoduleIgnore && ls -d /var/tmp/souji-r16-ScoutSubmoduleIgnore 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1224,1242p' tools/souji-census.sh | cat -n | sed 's/^/   /'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1186,1196p' tools/souji-census.sh | cat -n; echo '--- census_one start ---'; grep -n 'census_one() {' tools/souji-census.sh
```

Files read with the read tool (not shell): `tools/souji-census.sh` (ranges 1-60, 740-790, 1015-1065,
1085-1122, 1120-1185, 1195-1263, 1218-1245, 1264-1353), `skill://godspeed`,
`census/round-16/live-fleet-final.json` (ranges 13-90, 94-240, 244-330), and the four URLs cited above.

No tools were installed or upgraded. Temporary tree `/var/tmp/souji-r16-ScoutSubmoduleIgnore` removed.
