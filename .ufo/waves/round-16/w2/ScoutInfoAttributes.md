# ScoutInfoAttributes — `$GIT_DIR/info/attributes` precedence and status/check-attr reads

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` @ `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`
- Tool under test: `tools/souji-census.sh`, sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`
- Host git: 2.56.0; all source citations are tag `v2.56.0`
- Recon only; no execution of the census. All URLs accessed **2026-10-20**.

STATUS: ok

## Verdicts

| Claim | Verdict |
|---|---|
| `$GIT_DIR/info/attributes` has the highest attribute precedence | **holds** |
| `core.attributesFile` does not replace/suppress it | **holds** |
| `git check-attr` reads it | **holds** |
| `git status` reads it | **holds, conditional** — only when status reads a worktree blob through conversion (index-refresh content compare or diff/rename content read), not on every invocation |
| `tools/souji-census.sh` is safe against a filter bound only via `info/attributes` | **holds by code reading**, **partial on exercised evidence** — no fixture/selftest creates `info/attributes`, so the round-16 "any attributes source" claim is not asserted for the one source `-c core.attributesFile` cannot neutralize |

Overall: no safety hole found in the census; evidence coverage is partial (details below).

## Observed facts (docs)

1. Highest precedence. `gitattributes(5)`: "Git consults `$GIT_DIR/info/attributes` file (which has the highest precedence), `.gitattributes` file in the same directory as the path" — https://git-scm.com/docs/gitattributes (accessed 2026-10-20). Order: info/attributes > deeper `.gitattributes` > shallower > global/system.
2. Additive, not replaceable. `core.attributesFile` doc: "in addition to `.gitattributes` (per-directory) and `.git/info/attributes`" — https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/core.adoc:505-510 (accessed 2026-10-20); rendered at https://git-scm.com/docs/git-config. Setting `core.attributesFile=/dev/null` therefore does **not** remove the info frame.
3. Symlinks are followed for `info/attributes` (unlike in-tree `.gitattributes`): test "symlinks respected in info/attributes" at https://raw.githubusercontent.com/git/git/v2.56.0/t/t0003-attributes.sh:520-524 (accessed 2026-10-20); bare-repo test at :473-487. The census refuses git-metadata symlinks that resolve outside the gitdir, so it is stricter than git here (pre-existing r14 guard, `tools/souji-census.sh:86`, `guard_git_links` at :500-517) — an over-refusal, not a hole.

## Observed facts (implementation, v2.56.0)

All source URLs below accessed 2026-10-20.

1. `INFOATTRIBUTES_FILE` is `"info/attributes"` — https://raw.githubusercontent.com/git/git/v2.56.0/environment.h:27-28.
2. The info frame is read unconditionally when a repository is present and pushed **last** (top of stack = highest precedence): `if (startup_info->have_repository) e = read_attr_from_file(git_path_info_attributes(), flags);` — https://raw.githubusercontent.com/git/git/v2.56.0/attr.c:940-947, re-pushed at :1037-1040. The file's own comment says: "Finally, at the very top of the stack we always keep the contents of $GIT_DIR/info/attributes" — attr.c:958-971. `git_path_info_attributes` is `GIT_PATH_FUNC(..., INFOATTRIBUTES_FILE)` at :896; `GIT_PATH_FUNC` expands to `repo_git_path` (https://raw.githubusercontent.com/git/git/v2.56.0/path.h:299-306, accessed 2026-10-20), and `path.c:98-102` marks `info` as common-dir (linked worktrees read the common dir's file; census guards `commondir` at `tools/souji-census.sh:847-857`).
3. `git check-attr` uses the same stack: `git_check_attr(the_repository->index, full_path, check);` — https://raw.githubusercontent.com/git/git/v2.56.0/builtin/check-attr.c:64-76; `git_check_attr` → `collect_some_attrs` → `prepare_attr_stack` at attr.c:1325-1332. No `--cached`/`--source` in the census call, so it is the default (worktree, index fallback) direction, same as status.
4. `git status` opens it on the content path: `cmd_status` calls `refresh_index(the_repository->index, REFRESH_QUIET|REFRESH_UNMERGED|progress_flag, &s.pathspec, NULL, NULL);` — https://raw.githubusercontent.com/git/git/v2.56.0/builtin/commit.c:1630-1632. Refresh content-compares entries whose size is unchanged/unknown: `ce_compare_data` → `index_fd(istate, &oid, fd, st, OBJ_BLOB, ce->name, 0)` (read-cache.c:231-244, :489-492) → `would_convert_to_git[_filter_fd]` (object-file.c:942-961) → `convert_attrs` → `git_check_attr(istate, path, check);` (convert.c:1321-1334). Diff/rename content reads use `would_convert_to_git`/`convert_to_git` too (diff.c:4409, :4539-4567).
   - Boundary: a **size-changing** edit sets `DATA_CHANGED` and `ie_modified` returns at read-cache.c:474-487 **without** reading content; a same-size edit (or unknown `sd_size`) reaches the content compare. So status does not open `info/attributes` on every run — only when it must hash a worktree blob.
5. `attr.tree` (repo config) changes only the in-tree `.gitattributes` source, not the info frame: https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/attr.adoc:1-6; attr.c:1201-1242. Both `check-attr` and status consume the same `default_attr_source()` (attr.c:1330), so the census's guard stays aligned with status under `attr.tree` as well.

## Relation to `tools/souji-census.sh` at HEAD

- `guard_git_files` lists `info/attributes` among fixed metadata and refuses non-regular/hardlinked targets (`tools/souji-census.sh:519-535`); `guard_git_links` refuses symlinks escaping the gitdir (:500-517). Both run for the main gitdir, the resolved commondir, and linked-worktree admin dirs (:831-891, :790) before any measurement.
- `status_info_file` (:942-978) models only the `core.attributesFile`/XDG frame; `count_dirty` passes `-c core.attributesFile="$at"` to status (:1037) and `guard_bound_filters` passes the same to `ls-files`/`check-attr` (:1002-1008). That override removes the global frame but **cannot** remove the info frame (fact 2 above). The census does not try to neutralize it; it catches filter bindings through `check-attr`, which reads it (fact 3).
- `guard_bound_filters` (:983-1018) builds the driver-name set from `git config --get-regexp '^filter\..*\.(clean|smudge|process)$'` (:985-993) and skips status (`unverifiable`, stderr `status-skipped`) when `check-attr` reports a bound name (:1014-1017, :1021-1035). A driver bound only via `info/attributes` is therefore detected, and if no driver command is configured the binding is inert (git has nothing to execute). The guard's `check-attr` and status share the same attribute stack and the same `GIT_DIR` discovery (`git -C "$wt"`), so the sources agree; the only residual is the documented non-atomic guard/access window.
- Conclusion: the census's handling is faithful for `info/attributes`; no counterexample found in the code path.

## Gap and smallest fix (partial evidence)

- Coverage hole: `grep -n 'info/attributes'` finds only `tools/souji-census.sh:521`; the r16 fixture `tests/fixtures/r15-census-config.py` contains no `info/attributes` case. Its bound-filter evidence uses worktree `.gitattributes` only (:525, :537), and its `core.attributesFile` cases are `/dev/null` (:580), a safe `-text` file (:584), and a store-reaching path (:522). Fixture header claims the general rule "a filter bound by a reachable attributes file refuses" (:64-65), but the highest-precedence, non-overridable source is the one not exercised. Case 14 (fixture `case_14`, :1288-1301) asserts the sentinel only for the `.gitattributes` repos.
- Smallest fix: add one unsafe repo next to `r-filter-clean` (fixture :522-534):
  `r-filter-info`: tracked `f.bin`, commit; write `.git/info/attributes` = `*.bin filter=i`; config `[filter "i"] clean = <sentinel>`; modify `f.bin` with a **same-length** edit (e.g. `bin\n` → `bxn\n`); expect `status-unverifiable` and no sentinel, and add it to `case_14`'s `single_positive` list and sentinel assertions. Optionally add a census selftest arm that binds a configured driver through `$GIT_DIR/info/attributes`.
- Adjacent inference (affects the same evidence): the existing positive controls edit with **different lengths** (`bin\n`→`bin changed\n`, `d\n`→`d changed\n`). By read-cache.c:474-487 that returns at the `DATA_CHANGED` branch without content read, and rename detection does not queue a modified (two-sided) file; with the fixture's config (no `diff.breakRewrites`), those modifications likely never exercise a clean driver even without the guard — the sentinel assertion is weaker than its comment claims (`tests/fixtures/r15-census-config.py:528-531`). [INFERENCE, high confidence from source; not executed]. Same-length edits fix both cases.
- Also worth one sentence at `tools/souji-census.sh:935-941`: "`core.attributesFile`/XDG is only the global frame; `$GIT_DIR/info/attributes` is always consulted (highest precedence) and is covered by `check-attr` and `guard_git_files`." Current wording ("Effective excludes/attributes file for status") invites reading it as the only attributes source.

## Unresolved

- Status's attribute reads are lazy; no run was allowed, so the exact set of paths status hashes (same-size vs size-changed vs rename candidates) is inferred from source, not observed.
- Linked-worktree `info/attributes` lives in the common dir; the census guards commondir, but no worktree scenario was executed.

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git --version && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n -i -E 'attribute|GIT_DIR|GIT_WORK_TREE|GIT_CONFIG|check-attr|core\.attributesFile|info/attr' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n 'info/attributes\|guard_git_files\|core.attributesFile\|attributesFile' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | grep -n 'info_attributes\|ATTR_OVERRIDE\|prepare_attr_stack\|read_attr_from_file'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | awk 'NR>=886 && NR<=948 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/path.c | grep -n 'common_list\|INFOATTRIBUTES\|info/attributes'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/check-attr.c | grep -n 'git_check_attr\|check_attr\|typename\|attr_check'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/convert.c | grep -n 'git_check_attr\|convert_to_git\|filter'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/t/t0003-attributes.sh | grep -n 'info/attributes\|highest\|precedence'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | grep -n 'refresh_index\|git_check_attr\|convert_to_git'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | grep -n 'ce_compare_data\|convert_to_git\|would_convert' | head -20
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/path.c | awk 'NR>=90 && NR<=130 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | awk 'NR>=840 && NR<=890 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/core.adoc | grep -n -A12 '^core\.attributesFile'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/t/t0003-attributes.sh | awk 'NR>=225 && NR<=260 || NR>=465 && NR<=530 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/attr.adoc | grep -n -B2 -A12 'attr\.tree'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | grep -n 'attr\.tree\|attrtree\|attr_tree\|git_attr_tree\|source' | head -40
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | awk 'NR>=225 && NR<=300 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/object-file.c | grep -n 'index_blob\|get_stream_filter\|convert_to_git\|index_fd' | head -30
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/convert.c | awk 'NR>=1310 && NR<=1345 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | awk 'NR>=2780 && NR<=2800 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/object-file.c | awk 'NR>=936 && NR<=1006 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/commit.c | grep -n 'refresh_index\|wt_status_collect'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | grep -n 'attributesfile\|attributes_file\|read_attr_config'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitattributes.adoc | grep -n -B3 -A8 'highest'
grep -rn 'info/attributes\|attributesFile\|check-attr\|core.attributes' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/diff-lib.c | grep -n 'ce_modified\|ce_compare\|match_stat' | head -20
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/commit.c | awk 'NR>=1615 && NR<=1665 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | awk 'NR>=948 && NR<=1005 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | grep -n -A25 '^int ie_modified'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | grep -n -B2 -A6 'DATA_CHANGED' | head -60
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | grep -n 'ie_modified('
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/convert.c | awk 'NR>=1355 && NR<=1400 {printf "%d:%s\n", NR, $0}'
grep -n 'info/attributes\|"info"\|attributes' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
grep -n 'filter\|check-attr\|attributes' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh | awk -F: '$1>1150 {print}'
grep -n 'filter\|status-unverifiable\|status-skipped\|info/attributes' /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py
grep -rn 'attributes_file' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh || true; curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/repo-settings.c | grep -n 'attributes'
grep -n 'info/attributes' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
for f in attr.c attr.h git-compat-util.h cache.h repository.h environment.h path.h; do printf '%s: ' "$f"; curl -fsSL "https://raw.githubusercontent.com/git/git/v2.56.0/$f" | grep -n 'INFOATTRIBUTES_FILE\|GITATTRIBUTES_FILE' || true; done
grep -n 'status-unverifiable\|status-skipped\|filter' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py | awk -F: '$1>640 && $1<760 {print}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/check-attr.c | awk 'NR>=55 && NR<=110 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | grep -n -B4 -A12 '^void git_check_attr'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/path.c | grep -n -B3 -A8 'is_common' | awk 'NR<=60'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c | awk 'NR>=470 && NR<=520 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/diff.c | grep -n 'would_convert_to_git\|convert_to_git\|index_fd\|index_path\|hash_filespec'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/diffcore-rename.c | grep -n -A20 '^static int hash_filespec'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/wt-status.c | grep -n 'detect_rename\|status.renames\|renames'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/commit.c | grep -n 'status.renames\|detect_rename'
grep -n 'git-metadata symlink\|git-metadata symlink must\|any git-metadata symlink\|git-metadata-symlink' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n '^guard_git_links\|^guard_git_files\|^guard_bound_filters\|^status_info_file\|^count_dirty\|^guard_git_surface\|^guard_config_path' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n 'def case_14' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/path.h | grep -n -A8 'GIT_PATH_FUNC'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/builtin/check-attr.c | awk 'NR>=110 && NR<=205 {printf "%d:%s\n", NR, $0}'
curl -fsSL https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | grep -n 'git_attr_direction\|direction =\|set_direction'
grep -n '^scratch_bytes' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh && awk 'NR>=536 && NR<=542 || NR>=978 && NR<=984 || NR>=1016 && NR<=1022 {printf "%d:%s\n", NR, $0}' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ScoutInfoAttributes.md && grep -n '^# ScoutInfoAttributes\|^## ' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ScoutInfoAttributes.md
```
