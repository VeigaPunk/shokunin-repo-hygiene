STATUS: DONE — C1-D2 falsified statically at 5fa6017: three defects (symlink→FIFO reachability, five-call-site completeness, soft-return ordering), all fixable inside the declared scope; no census run.

# RevD2Static — pre-implementation falsification of C1-D2 (`info/attributes` per-repo degrade)

- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
- Base: `5fa6017ddcae9f6bd4412df44765f6360cb16294`. All line citations below are `git show 5fa6017:tools/souji-census.sh` bytes, sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (1877 lines).
- Method: static source review only; no census execution (no ALLOWED-EXEC on this seat), no `/var/tmp` scratch. Git behaviour is grounded in git v2.51.0 source and `gitattributes(5)`; host git is `2.56.0`.
- Concurrent note: the executor `CensusD1D2` was editing the worktree copy while this seat ran (worktree sha256 moved `5db74bb…` → `3efa919…`; `git diff --stat` +29…+40 lines in `tools/souji-census.sh`; `guard_git_files` and all five call sites were still 5fa6017 bytes at the last observation). This report judges the *committed* base, as instructed; the in-flight helper is not reviewed as a final patch.

Verdict: **fails as specified**, for three concrete reasons (F1–F3). The claim is implementable and testable without widening scope once those are fixed; F4–F6 are constraints the implementation and the fixture must carry, F7–F8 are disclosures.

---

## 1. Every path by which `info/attributes` can be *opened* before `guard_git_files` runs

**Result: none open its contents. The file is only stat'ed/lstat'ed, and one symlink shape is refused earlier by a different whole-run policy.**

Ordered inventory for one scan (all at 5fa6017):

| # | operation | site | opens `info/attributes`? |
|---|---|---|---|
| 1 | `guard_path`/`guard_target`/`resolve_guarded` (root, repo, gitdir, commondir, worktree targets) — walk with `[ -L ]`, `readlink`, `[ -e/-d ]` | `resolve_guarded` :381-455, `guard_path` :457-461, `guard_target` :466-470 | **no** — lstat/readlink only; refuses `\n\t\r` inputs |
| 2 | `guard_git_links`: `find -P "$dir" -type d ! -readable` and `find -P "$dir" -type l` | :500-514 | **no** — `stat`/`access`/`lstat`; a FIFO is stat'ed but never opened; a symlink is `readlink`ed |
| 3 | `guard_git_files`: `[ -f ]`, `[ -e ]`, `[ ! -d ]`, `stat -L -c %h` | :519-535 | **no** — `test`/`stat` only (non-blocking on FIFOs) |
| 4 | `guard_git_config`/`guard_wt_config` → `scan_config_file` → `git config --file … --list`, `tr '\0' < cfg`, `cmp` | `guard_config_file_kind` :587-599, `scan_config_file` :608-692, `guard_wt_config` :696-711, `guard_git_config` :715-733 | **no** — explicit `--file` config parsing; no attribute lookup anywhere in git's config code |
| 5 | `guard_worktree_registrations`: reads `worktrees/*/gitdir` and `*/commondir` via `IFS= read … <` | :766-812 | **no** — different files, each gated by `[ -f ]` first (:775, :787, :798) |
| 6 | `guard_alternates_file`: reads `objects/info/alternates` | :472-494 | **no** — different file, gated by `[ -f ]` |
| 7 | `gitfile_admin`: reads the `.git` pointer file | :738-752 | **no** |
| 8 | `newest_mtime`: `find . … -name .git -prune` | :1068-1123 | **no** — `.git` is pruned by name; contents never opened; `-type f` excludes FIFOs |
| 9 | `scratch_bytes`: `du -sb -P .scratch` | :1049-1062 | **no** |
| 10 | `list_repos` discovery: `[ -L ]`, `[ -d ]`, `protected_reason_input`, `guard_git_pointer`, `guard_git_surface` | :1257-1302 | **no** — no measurement git call at discovery; only the guard's own `git config --file` |
| 11 | `census_one`: `guard_git_surface` is the **first** call; every measurement git call follows it | :1176-1207 | **no** — on soft the function returns at :1177-1182 before `rev-parse` (:1194), `worktree list` (:917, :1166), `for-each-ref`/`rev-list` (:923-931), `config` (:944, :986), `ls-files|check-attr` (:1002-1008), `status` (:1035-1040) |

The **first** open of the file in a successful run is `git status` (:1035-1040) or, when `filter.*.clean|smudge|process` keys exist, `git check-attr` inside `guard_bound_filters` (:1002-1008). Both are after the guard. Note that the status call's `-c core.attributesFile="$at"` does **not** neutralize this file: git always pushes the `info` frame with highest precedence (`attr.c` `bootstrap_attr_stack` → `read_attr_from_file(git_path_info_attributes(), …)`; `static GIT_PATH_FUNC(git_path_info_attributes, INFOATTRIBUTES_FILE)`; `INFOATTRIBUTES_FILE "info/attributes"` in `environment.h:27`).

### The symlink override (the important pre-guard exception)

`guard_git_links` runs **before** `guard_git_files` at four of the five sites (:830/831, :848/849, :872/873, :890/891) and exits 2 on any symlink whose resolved target is not under the same gitdir (`:510-513`, `protected_fail "git-metadata-symlink"`). Therefore:

- `$dir/info/attributes` → FIFO **inside** `$dir`: link guard passes (`"$dir"/*`), file guard sees `-f` false / `-e` true / not dir → `git-metadata-nonregular`. **D2 is reachable here.**
- `$dir/info/attributes` → FIFO (or any file) **outside** `$dir`: link guard exits 2 *before* D2 can run. **D2 is unreachable for this shape** — this is F1.
- `$dir/info/attributes` → credential store / operator surface: `guard_target`'s `resolve_guarded` calls `protected_fail` during the walk (`protected_reason_inside` checks at :401-427), so exit 2. Protected refusals stay whole-run.
- A hardlinked *regular* file (nlink > 1) has no symlink, so no override; D2 is reachable.

At the fifth site (:790) the order is files-then-links (:790 files, :791 links), but the outcome converges only if the soft is `|| soft=1` and execution continues into :791; an early `return 1` there would silently convert an out-of-gitdir symlink from whole-run refusal to a degrade (see F3).

---

## 2. Every path *after* a per-repo degrade where a git call might still read the file

**Result: none for the degraded row, provided the soft is carried as `soft=1` — not as an early return — and every one of the five call sites participates.**

- `census_one` prints the `error` row and returns at :1177-1182. No git call in the row's measurement block runs.
- Calls that still run *inside the same `guard_git_surface`* after a soft: `guard_git_config` (:832/:850/:874/:892, `git config --file`), `guard_wt_config` (:851/:893, `git config --file`), `guard_worktree_registrations` (:855/:897 → `git config --file` per admin at :792). None of them reach git's attr code; they cannot open `info/attributes`.
- `guard_alternates` (:854/:896) reads `objects/info/alternates` — a different file, and its own nlink/nonregular check is `guard_git_files`' last entry (:521, after `info/attributes`) — see F3.
- `list_repos`' guard pass (:1266, :1269, :1299) also runs before any row is printed; its soft is discarded by `|| true` and re-derived by `census_one`'s guard (which resets `CFG_SOFT_REASON` at :823). No measurement git call exists at discovery.
- `worktree_extra_flags`' `git -C "$repo" worktree list --porcelain` (:1166) starts before the per-worktree guards, but it reads registration metadata only; `builtin/worktree.c` (v2.51.0) calls no attr API. `count_dirty "$cpath"` (:1162) is skipped when `guard_git_surface "$cpath"` soft-returns (:1156-1161). [INFERENCE for the source-negative on `worktree list`; the three ref/object commands at :917/:923-931 and `rev-parse` at :1194 are likewise not attr consumers.]
- `--compare`/`load_census` open a TSV, not a gitdir.

Residual after-degrade reads that are **not** eliminations:

1. **Divergent commondir (crafted):** a registered worktree of repo A whose `worktrees/<id>/commondir` points at repo B's gitdir. A's guard checks A and only *resolves* the child's commondir (:793-805, `guard_target git-common-dir "$c"`, no file guard); A's row is legitimately measured (A's own status, :1205). The child guard (:1156) then sees B's bad file and skips `count_dirty` → `wt-dirty`. That is honest and conservative, but it is **not** an `error` row for A, and the diagnostic belongs to B, which may not even be a row in this run. The claim's "per-repository error row" must not be read as "the scanned row becomes error" in this shape.
2. **TOCTOU:** the guard and git's later open are not atomic — already disclosed in the header (:126-128).
3. **`error` rows are placeholders, not measurements:** numeric fields print `0` (:1180). Consumers that ignore `verdict_flags` (e.g., `--compare`, see F8) can read a placeholder as data. `error`/`has_problem` (:1236) is the only honest marker.

---

## 3. Linked worktree whose common dir's `info/attributes` is bad: same row or several?

Git reads **one** file for the whole repository: `$GIT_COMMON_DIR/info/attributes`. Evidence:

- `path.c` `common_list[]` at v2.51.0: `{ 0, 1, 1, "info" }` — `is_common = 1` (only `info/sparse-checkout` is per-worktree). `adjust_git_path` replaces the gitdir prefix with `repo->commondir` whenever `different_commondir` (path.c:395-411).
- `attr.c`: `static GIT_PATH_FUNC(git_path_info_attributes, INFOATTRIBUTES_FILE)` → `repo_git_path(the_repository, "info/attributes")`; `bootstrap_attr_stack` pushes it unconditionally when a repository exists.
- `gitattributes(5)`: "Git consults `$GIT_DIR/info/attributes` file (which has the highest precedence)".

Consequences for a linked worktree whose **common** `info/attributes` is the bad file:

- The **admin** dir's own `info/attributes` (`…/.git/worktrees/<id>/info/attributes`) is **never** read by git. Only the common one matters.
- Row model at 5fa6017: linked worktrees are not rows — header :19-21, and `list_repos` skips a child whose `.git` is a file (`guard_git_pointer` + `continue`, :1294-1296). So a run rooted at the fleet contains **one** row (the owner/main repo). The bad common file is that row's own `$GIT_DIR/info/attributes` when the main worktree is the row (:831 guards `$dir`, which for a main worktree *is* the common dir), so one row, one degrade.
- `--include-root` on the **linked worktree path** makes it its own row (:1261-1267, `-f "$g"` branch); its guard reaches the same common file through the commondir branch (:876-891). So the *same physical file* yields an `error` row for every run whose row owns a worktree reading that common dir: one row per run, never two rows for the same row identity. Two different runs (rooted at the main worktree and at the linked worktree) each yield their own error row; the census holds no cross-run state.
- The independent detections are equivalent because each row's guard visits both `$GIT_DIR` and the resolved `$GIT_COMMON_DIR`; no cross-row cache is needed, and `CFG_SOFT_REASON` is reset per `guard_git_surface` (:823) — the metadata channel must be reset alongside it (F4).

**What the degrade must cover**, stated minimally:

1. `$GIT_COMMON_DIR/info/attributes` for every row whose own git calls can open it: the main-worktree row (:831) and any gitfile row (:891). `--include-root` rows therefore need :891, not just :831/:849.
2. Per-worktree status skip: `guard_git_surface "$cpath"` (:1156) must soft on the common file so `count_dirty "$cpath"` (:1162) never runs; the row then carries `wt-dirty`, which is conservative.
3. The admin-dir sighting (:790) is inert for git. A uniform degrade (error row) is safe but over-broad; treating it as a whole-run refusal is also defensible. Pick one, pin it in the fixture, and disclose it. Do **not** try to relax `guard_git_links` to reach out-of-gitdir symlinks (F1).
4. Nothing else: other entries (:521) and every `protected_fail` reach keep exit 2.

---

## 4. Findings

### F1 — HIGH (claim/test mismatch): a symlink→FIFO outside the gitdir cannot degrade; it exits 2 in `guard_git_links`

`guard_git_files` is reached only after `guard_git_links` at :830/848/872/890. `guard_git_links` refuses any symlink resolving outside `$dir` (:508-514, reason `git-metadata-symlink`). So the declared "non-regular (… a symlink resolving to one)" is implementable **only when the FIFO target resolves inside the same gitdir**. The fixture brief says "symlink info/attributes → FIFO → same"; if it creates the FIFO next to the repo (outside `.git`), the *correct* implementation exits 2 and the fixture reds the changed arm for the wrong reason.

Smallest fix: keep the guard policy; scope the claim and fixture to an in-gitdir target (e.g. `<repo>/.git/info/attrs.fifo`), and add a paired case asserting an out-of-gitdir symlink (regular or FIFO) still gives `path-protected: git-metadata-symlink`, exit 2, whole run. Do not special-case `info/attributes` in `guard_git_links` — that would relax a r14 namespace invariant for one file.

### F2 — HIGH (completeness): all five call sites must change, not the three in r16's S5

5fa6017 call sites: `:790` (registered worktree admin), `:831` (repo `.git`), `:849` (commondir of a `.git`-dir repo), `:873` (gitfile admin), `:891` (gitfile commondir). The patch idea in `.ufo/waves/round-16/w2/RevCensusScanFinal.md` S5 lists only `831/849/873` and proposes softening **every** entry — both halves are wrong for C1-D2: leaving `:790`/`:891` as `|| exit 2` still aborts the whole fleet for a registered-worktree admin or for an `--include-root` linked-worktree row, and softening every entry would break "every other entry keeps whole-run exit 2". The executor prompt ("Read the closure's D2 note and the patch idea … (S5) first") can therefore import the wrong scope.

Smallest fix: apply the classification in `guard_git_files` (entry == `info/attributes`) and convert all five sites to the same `soft` accumulation; leave the other eight entries on `protected_fail`.

### F3 — HIGH (ordering): the soft must not return early, and the site must not skip the remaining guards

`objects/info/alternates` is the **last** entry (:521) and follows `info/attributes`. A naive `cfg_soft …; return 1` inside the loop loses a later whole-run refusal: a hardlinked/non-regular `objects/info/alternates` would be scanned as absent when `info/attributes` was seen first. The same failure exists at the call-site level if a site does `guard_git_files "$dir" || return 1` instead of `|| soft=1`: the later `guard_alternates` (:854/:896) and `guard_worktree_registrations` (:855/:897) — and at `:790`, `guard_git_links "$admin"` (:791) — must still run so protected reaches and other-entry refusals still exit 2.

Smallest fix: scan the whole nine-entry list, record the metadata reason/path, and `return 1` only after the loop; at every call site use `|| soft=1` (never an early return).

### F4 — MEDIUM (diagnostics and state): reuse of `CFG_SOFT_REASON` mislabels the row, and the reason leaks across repos

The two soft printers hardcode the config class (:1157-1159, :1177-1181) and read `CFG_SOFT_REASON`, which `cfg_soft` sets first-wins (:579-584). If the metadata reason reuses that channel, stderr reads `config-unsupported: git-metadata-hardlink` — not the declared `git-metadata-unsupported <reason> <path>`. If a separate `META_SOFT_*` is added but never reset, the first degraded repo's reason/path is printed for the next repo (and a config-only soft in a later repo prints the earlier metadata finding). `list_repos`' extra guard pass per repo makes the "report once" requirement easy to get wrong.

Smallest fix: carry reason **and** path in a metadata channel reset at `guard_git_surface` entry next to :823; route both printers through one helper that prefers the metadata reason and prints exactly `souji-census: git-metadata-unsupported <reason> <path>` (the claim's literal shape, no parentheses; sanitized; resolve_guarded already rejects tab/newline targets), keeping `config-unsupported: <reason> (<label>)` for config softs; print only from `census_one`/`worktree_extra_flags`, never inside the guard, so the discovery pass cannot double-print. Pin the exact string with the fixture seat before both land.

### F5 — MEDIUM (semantics to pin): common-vs-admin, and the divergent-commondir row outcome

Ground truth: the read file is `$GIT_COMMON_DIR/info/attributes` (section 3). An admin-dir `info/attributes` is inert, yet the census checks it at `:790` and would degrade the owner row for a file git never opens. Likewise the crafted divergent-commondir shape leaves the scanned row measured and only sets `wt-dirty` (section 2.1). Both are acceptable conservative outcomes, but they are **not** "the repository errors".

Smallest fix: state explicitly in the header and in the claim's wording that (a) the soft applies to the common dir a row's worktrees read, (b) an inert admin-dir sighting may degrade conservatively, (c) the divergent-commondir child skip is `wt-dirty`, not `error`. The fixture must pin whichever admin-dir policy is chosen.

### F6 — MEDIUM (test validity): the FIFO hang probe is vacuous without a stat-dirty tracked file, and `timeout` alone leaks the blocked `git`

`git status` hashes a worktree file only when the index stat does not match: `ce_modified_check_fs` → `ce_compare_data` (read-cache.c:230-241, 285-291) → `index_fd` (object-file.c:1246/1149) → `convert_to_git` (convert.c:1429) → `convert_attrs` → `git_check_attr` (convert.c:1332) → attr bootstrap opens `info/attributes` with plain `open(O_RDONLY)` (attr.c `read_attr_from_file`), which blocks on a writer-less FIFO. A repo whose tracked files are stat-clean may never consult attributes, so pre-harm/cc21683 could finish without hanging and the "finishes within timeout" assertion would pass on the *unguarded* arms — non-discriminating evidence for "no git call read it".

Also, the census runs status inside `$( … )` (:1035); killing only the shell on timeout leaves the substituted subshell and its blocked `git` orphaned in `open()`. Repeated across arms, that leaks blocked processes and can make later arms fail on resource pressure.

Smallest fix for the fixture: make the D2 repos' tracked file modified (append a byte after the commit) so the open is forced; run every census invocation with a process-group kill (`subprocess.run(..., start_new_session=True)` + `os.killpg` after a short timeout, or `setsid`/`timeout -k` with group signalling) and record timeout explicitly in the CASE detail. Stronger, if the r15 fixture's `probe_strace` is reusable: trace the changed arm with `strace -f -e trace=openat` and assert that **no** `openat` of the attributes path appears, while the same trace on pre-harm/cc21683 shows it — this is the direct proof of "no git call read it" and does not depend on the hang. Verified history: pre-harm `a31642d` has no `guard_git_files` at all, and r14-harm `cc21683`'s `guard_git_files` (`git show cc21683:…:475`) does not list `info/attributes`; r16 `5fa6017` exits 2 at `:519-535`. The four arms therefore discriminate as timeout-or-normal-row (a31642d/cc21683), exit 2 (5fa6017), exit 0 + `error` row + stderr (changed).

### F7 — LOW (unspecified shapes): stat failure and a directory at `info/attributes`

`stat -L %h` failure is `git-metadata-unavailable` (:525-527); C1-D2 names only hardlink and non-regular, so this reason stays exit 2 unless deliberately included. A **directory** at `info/attributes` is exempt (`[ ! -d ]`, :533) and is inert for the read path: git's `open()` fails `EISDIR`, `read_attr_from_file` warns and continues; a directory cannot block or alias. Recommendation: degrade `info/attributes` for all three reasons (the row never reads it, so an `unavailable` stat is not a reason to lose the fleet), keep directories exempt, and state both. If `unavailable` stays exit 2, state that too; do not leave it implicit.

### F8 — LOW (documentation and an unclaimed amplification)

- Header :83-88 still says the git-metadata guards "still refuse the whole run", and :97-108 documents `config-unsupported` as the only per-repo soft class. Both contradict the new behavior; the executor brief already requires a Round-17 paragraph, but it must also correct these two blocks (a stale contract is an operability defect in a tool whose header is its spec).
- `--compare` computes numeric deltas against `error`-row placeholders (:1465 in 5fa6017; S6 in the r16 review). D2 increases the number of `error` rows, so this pre-existing dishonesty becomes more reachable. Not part of C1-D2; record as residual so L1 does not count it as a regression.

---

## 5. Fixture acceptance matrix the counting command needs (beyond the current brief)

All cases run under the fixture's isolated HOME/XDG/GIT_CONFIG and a process-group timeout; "changed" = the C1 arm.

| id | shape | changed expectation | discriminator vs old arms |
|---|---|---|---|
| D2-01 | fleet a/b/c; b regular hardlinked (`nlink=2`) `info/attributes` | exit 0; b row `…\t0\t0\t0\t0\t\terror`; one stderr `git-metadata-unsupported … git-metadata-hardlink <b/.git/info/attributes>`; a,c rows byte-identical to a no-b run | a31642d/cc21683: normal b row; 5fa6017: exit 2 |
| D2-02 | b FIFO, **tracked file modified after commit**, no writer | exit 0 within timeout; b error; a,c unchanged | a31642d/cc21683: timeout (or normal row if the open is not forced — hence the modified file); 5fa6017: exit 2 |
| D2-03 | b symlink → FIFO **inside** b/.git/info | same as D2-02 | same |
| D2-04 | b symlink → FIFO/regular **outside** the gitdir | exit 2, `path-protected: git-metadata-symlink`, no rows | pins F1 (all arms likely exit 2 except a31642d, which has no guard — record its actual shape) |
| D2-05 | b hardlinked `config` (control) | exit 2 whole run, no rows | pins "other entries keep refusing" |
| D2-06 | b regular `info/attributes` | normal rows, exit 0 | plain control |
| D2-07 | W with linked worktree L; bad `W/.git/info/attributes` (common), FIFO; run `--root W` | exit 0 within timeout; W error; no L row | proves no status of W/L ran |
| D2-08 | same repo, `--root L --include-root` | exit 0; L row error | pins `:891` (F2) |
| D2-09 | bad `W/.git/worktrees/L/info/attributes` (admin) | pin policy: error row (uniform) or exit 2 | pins the inert-admin decision (F5) |
| D2-10 | b info/attributes hardlinked **and** `objects/info/alternates` hardlinked | exit 2 whole run | proves the scan completes after the metadata soft (F3) |

The hardlink case (D2-01) proves row shape; the FIFO cases (D2-02/03/07) are the only ones that observe "no git call opened it". Test-design pitfalls: do not hardlink `info/attributes` to `info/exclude` (the exclude entry is checked first at `:521` and would keep the whole-run exit 2, reding the changed arm), and do not let a second link sit at another guarded name (`config`, `HEAD`, `index`, `packed-refs`, `commondir`, `objects/info/alternates`). `--compare` over a run with an error row (F8) is optional and must not be an acceptance criterion.

---

## 6. Commands run (all read-only)

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin
git rev-parse HEAD
# 5fa6017ddcae9f6bd4412df44765f6360cb16294
git show 5fa6017:tools/souji-census.sh | sha256sum
# 64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c
sha256sum tools/souji-census.sh; git status --porcelain; git diff --stat
# worktree moved under this seat (executor concurrent): 5db74bb…, then 3efa919…; only helper lines added
#   M tools/souji-census.sh (+40 then +29), plus other seats' files; no edit by this seat
git --version
# git version 2.56.0
git show 5fa6017:tools/souji-census.sh | grep -nE 'guard_git_files|guard_git_links|guard_git_surface|CFG_SOFT_REASON|config-unsupported|rev-parse|worktree list|status --porcelain|check-attr|INCLUDE_ROOT'
# anchors: 519 (fn), 521 (list), 790/831/849/873/891 (call sites), 823 (reset),
#          1037 (status), 1008 (check-attr), 1177-1181 (error row), 1261-1267 (include-root), 1294-1296 (child skip)
git show 5fa6017:tools/souji-census.sh | sed -n '818,905p' | nl -ba -v818
git show 5fa6017:tools/souji-census.sh | sed -n '1118,1215p' | nl -ba -v1118
for r in a31642d cc21683 5fa6017; do git show $r:tools/souji-census.sh | grep -n 'info/attributes\|guard_git_files'; done
# a31642d: none; cc21683: guard_git_files at 475 but no info/attributes; 5fa6017: :521
```

Git source consulted (v2.51.0, tag `v2.51.0`):
- `path.c` — `common_list[]` `{0,1,1,"info"}`, `adjust_git_path`/`update_common_dir` (gitdir→commondir replacement), `repo_git_pathv`.
- `environment.h:27` — `#define INFOATTRIBUTES_FILE "info/attributes"`.
- `attr.c` — `GIT_PATH_FUNC(git_path_info_attributes, INFOATTRIBUTES_FILE)`; `bootstrap_attr_stack` pushes it; `read_attr_from_file` uses `open(path, O_RDONLY)` (no `O_NONBLOCK`), so a writer-less FIFO blocks.
- `Documentation/gitattributes.adoc` — `$GIT_DIR/info/attributes` has the highest precedence.
- `convert.c:1322-1332, 1429-1439` — `convert_to_git` → `convert_attrs` → `git_check_attr`.
- `read-cache.c:230-241, 285-291` — stat-dirty file → `ce_compare_data` → `index_fd`; stat-clean files short-circuit.
- `object-file.c:1149, 1246-1262` — `index_fd` → `convert_to_git` for blobs with a path.
- `builtin/worktree.c` — no attr API call [INFERENCE: source-negative for `git worktree list`].

Tool installs/updates by this seat: none.

---

## 7. Verdict

- **C1-D2 does not hold as written.** F1 (symlink→FIFO outside the gitdir is preempted by `guard_git_links`, exit 2), F2 (r16's S5 leaves `:790`/`:891` aborting the fleet and softens the wrong entries), F3 (early soft return loses the later `objects/info/alternates` refusal and can skip `guard_git_links` at `:790`).
- **The core claim holds statically:** no census code path opens `info/attributes` before `guard_git_files`; a soft carried as `soft=1` in `census_one`/`worktree_extra_flags` suppresses every git call that can open it; `git` reads exactly one such file per repository, the **common** dir's, and both row shapes that read it (main `.git`, gitfile commondir) already have a guard site.
- **Smallest fix set:** classify by entry inside `guard_git_files` (scan all nine, defer the soft return); convert all five call sites to `|| soft=1`; carry reason+path in a channel reset per `guard_git_surface` and print once with the `git-metadata-unsupported` class; scope the symlink case to in-gitdir targets and add the out-of-gitdir refusal control; update header :83-88/:97-108.

Residual risk / verification gaps: static only; no census, fixture, or matrix run (no ALLOWED-EXEC). Git semantics were read from v2.51.0 source while the host runs 2.56.0; the `info`-is-common resolution and the blocking `open()` are stable across that range but not re-verified against 2.56.0 bytes. The `worktree list` non-consumer claim is a source-negative inference. The worktree copy was being edited concurrently; if the landed patch differs from 5fa6017 beyond the helper block, F1–F5 must be re-checked against it. The no-harm trade to disclose: a hardlink alias of a store file at `info/attributes` is no longer a whole-run refusal (it degrades to `error`, and is never read); a symlink that reaches the store still exits 2 through `guard_target`.
