STATUS: DONE — static hostile-content review of `info/attributes` shapes against census 5fa6017 and the C1-D2 design. Four D2 design hazards, one adjacent unguarded hang class, and 18 fixture shapes with expected results per arm.

Seat: SoujiR17-3.SentinelFifoHostile (sentinel, leaf). Axis judged: operability. Each target must yield a row or a deliberate refusal. The census must never hang, never lose neighbour rows, and never report a measurement it did not take.
Method: static only. This item had no `ALLOWED-EXEC`, so the census was not run (not even a copy) and nothing was created under `/var/tmp`. Line numbers come from `git show 5fa6017:tools/souji-census.sh` (sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`, the r16 census bytes). At review time `git diff 5fa6017 -- tools/souji-census.sh` was empty, so no D2 patch existed in the worktree yet. I reviewed the D2 *design* (the claim text plus the r16 S5 patch in `.ufo/waves/round-16/w2/RevCensusScanFinal.md:138-155`), not an implementation.
Git behaviour claims come from git `master` source read over the web (attr.c, path.c, commit.c, worktree.c), not from the host's installed version. Treat the cited functions as current-master facts. Anything marked [INFERENCE] was not read in source this session.

## Axes

- A1 **no hang / no unbounded read.** No census process (bash or git) may `open()` a hostile `info/attributes`.
- A2 **blast radius.** A non-protected defect costs one row; it must not cost the whole run.
- A3 **refusal preservation.** Every protected-namespace refusal, and every other `guard_git_files` entry, keeps whole-run exit 2.
- A4 **honest rows and diagnostics.** An `error` row is a placeholder, never a measurement. Each affected repo gets exactly one diagnostic.

## Source facts that decide the shapes

- **git opens info/attributes with a blocking open.** `attr.c` `read_attr_from_file`: `fd = open(path, O_RDONLY)` (no `O_NONBLOCK`; `open_nofollow` is used only for in-tree `.gitattributes`). Then `fstat`; the file is skipped only if `st.st_size >= ATTR_MAX_FILE_SIZE`; then `while (strbuf_getline(&buf, fp) != EOF)`. The over-long-line check (`ATTR_MAX_LINE_LENGTH`) runs on the line *after* it has been read.
  - FIFO with no writer: `open` blocks forever, so git hangs.
  - `/dev/zero`: `st_size` is 0, so it passes the size cap, and `strbuf_getline` accumulates NUL bytes with no newline forever. Memory grows without bound.
  - Directory: `open(O_RDONLY)` succeeds, and the first `read` fails with `EISDIR`, which ends as EOF/an empty frame. No hang.
  - Socket: `open` fails (ENXIO), which warns and treats the file as absent. No hang.
- **Which info/attributes git reads.** `bootstrap_attr_stack` reads `git_path_info_attributes()` (`INFOATTRIBUTES_FILE`) when `startup_info->have_repository`. In `path.c` `common_list`, `info` is `{0,1,1,"info"}` (a common dir); only `info/sparse-checkout` is per-worktree. So git reads **`$GIT_COMMON_DIR/info/attributes`**. A linked admin's own `worktrees/<id>/info/attributes` is never read by git.
- **When git triggers the read.** git consults attributes only when it does an attribute lookup. One example is `status` refresh content-checking a stat-dirty or racily-clean tracked file through `convert_to_git` [INFERENCE: call chain from memory, not re-read]. A fixture without a provoker can therefore let a guardless arm pass vacuously (see "Harness requirements").
- **census 5fa6017 ordering in `guard_git_surface`.**
  - Main `.git` directory: `guard_git_links` (:830), then `guard_git_files` (:831), then config. The commondir target gets the same treatment at :848/:849.
  - `.git` file: :872/:873, and for its common dir :890/:891.
  - Linked admin, inside `guard_worktree_registrations`: the order is reversed, `guard_git_files "$admin"` (:790) then `guard_git_links "$admin"` (:791).
- **`guard_git_files` :519-535.**
  - The list is `config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates` (:521). info/attributes is checked before alternates.
  - Regular files get an nlink check through `stat -L` (:524-530).
  - A path that exists and is neither a regular file nor a directory gets `protected_fail git-metadata-nonregular` (:531-532). A directory is allowed silently.
  - These are `stat`/`test` calls only, so the guard itself never opens the file.
- **`guard_git_links` :500-516.** Every symlink under the gitdir (`find -P -type l`) is resolved with `guard_target`, which uses `resolve_guarded` with no existence requirement and loop detection after more than 40 hops. The link must land inside the gitdir; otherwise it fails with `git-metadata-symlink`, exit 2.
- **`guard_alternates_file` :482.** `[ -f "$alt" ] || return 0`. A FIFO `objects/info/alternates` passes this check. Only `guard_git_files` catches it.
- **Arms.**
  - a31642d has no git-metadata guard at all.
  - cc21683 has `guard_git_links` (:470) and `guard_git_files` without `info/attributes` (:477). That arm's status passes `-c core.attributesFile=/dev/null`, which replaces only the *global* file, not `info/attributes`.
  - At 5fa6017, `info/attributes` is present (:521). It entered at b410186 (per the r16 closure).

## Required behaviour per shape (contract for D2)

"Degrade" means:
- exit 0;
- that repo's row is `0 0 0 0 <empty> error`;
- exactly one stderr line `souji-census: git-metadata-unsupported <reason> <path>`, with reason `git-metadata-nonregular` or `git-metadata-hardlink`;
- no `git -C <repo>` call for that repo, and no `open`/`openat` of the attributes path or its target by any process;
- neighbour rows are byte-identical to a run without the hostile repo.

"Refuse" means: exit 2, `path-protected: <reason>`, no census stdout (rows are buffered and the header is printed after them, :1315-1329, header at :1326).

| # | shape (at `$GIT_COMMON_DIR/info/attributes` unless stated) | 5fa6017 today | D2 MUST | MUST NEVER |
|---|---|---|---|---|
| H1 | FIFO | refuse `git-metadata-nonregular` (:532) | degrade | open (it blocks forever); run any git in the repo |
| H2 | symlink → FIFO inside the gitdir | links pass (target inside); files: `-f` false, `-e` true → refuse :532 | degrade | follow by open; stat is fine (stat on a FIFO does not block) |
| H3 | symlink → FIFO outside the gitdir | refuse `git-metadata-symlink` (:830 before :831) | refuse (namespace class, unchanged) | degrade; open |
| H4 | symlink → `/dev/zero` | refuse `git-metadata-symlink` (escapes the gitdir) | refuse (unchanged) | open: git would read NULs into memory without bound |
| H5 | symlink → `/dev/null` (plausible "disable" idiom) | refuse `git-metadata-symlink` | refuse (unchanged; disclose as a hostile/benign-repo whole-run lever, F6) | open |
| H6 | hardlink to a regular file outside the repo (canary content) | refuse `git-metadata-hardlink` (:529) | degrade | read the content (it must never appear on stdout/stderr); name the other link (unknowable anyway) |
| H7 | hardlink between two names inside the same gitdir | refuse :529 | degrade (indistinguishable from H6) | read |
| H8 | directory | normal row (`-d` allowed) | **decision needed** (F4): either a normal row, pinned, with the claim worded "FIFO/socket/device", or degrade it | hang (it cannot hang: EISDIR) |
| H9 | dangling symlink inside the gitdir (`-> ../nope`) | normal row (`-e` false, skipped) | normal row (git gets ENOENT and treats it as absent) | degrade; refuse |
| H10 | dangling symlink escaping the gitdir | refuse `git-metadata-symlink` | refuse (unchanged) | |
| H11 | self-loop symlink (`attributes -> attributes`) | refuse `symlink-loop` (resolve_guarded at more than 40 hops) | refuse (unchanged; label says `path-protected`, which is misleading, F6) | |
| H12 | unix socket | refuse :532 | degrade | |
| H13 | FIFO in a linked admin `M/.git/worktrees/w/info/attributes` (inert to git) | refuse via :790 | degrade the M row (conservative), or skip the check for admins. Pick one and pin it (F2) | exit 2 |
| H14 | M `.git/commondir` → hostile C; FIFO in `C/info/attributes` | refuse via :849 | degrade the M row; the diagnostic names `C/info/attributes` | run git in M (git would read C's attributes) |
| H15 | linked worktree W of M (W outside the fleet); `W/.git` → admin A; `A/commondir` → C; FIFO in `C/info/attributes` | refuse via :891 inside `worktree_extra_flags` → `guard_git_surface(W)` | M measured normally plus `wt-dirty`; no status in W; one diagnostic naming C | refuse; measure W |
| H16 | fleet child that is itself a linked worktree (`.git` file) whose admin/common holds a FIFO | not a row; only `guard_git_pointer` runs (:1294-1296) | unchanged: not a row, exit 0, no diagnostic | stat/open the FIFO; run git |

## Findings

### F1 — major (D2 design hazard, A3): a soft early `return` in `guard_git_files` masks the alternates refusal

- **Evidence.** :521 lists `info/attributes` before `objects/info/alternates`. The r16 S5 patch (`RevCensusScanFinal.md:144,148`) is `cfg_soft …; return 1` *inside* the loop. `guard_alternates_file:482` returns 0 for a non-regular alternates file, so `guard_git_files` is the only guard that sees a FIFO alternates.
- **Exploit path.** A repo with FIFO `info/attributes` and FIFO `objects/info/alternates` returns soft on the first entry. The alternates check never runs, so the repo becomes an `error` row with exit 0. That violates the claim that every other `guard_git_files` entry keeps exit 2. The same masking applies if any soft entry ever precedes `config`/`HEAD`.
- **Impact.** A silent downgrade of a whole-run refusal to a per-repo row. No hang follows in the changed arm, because no git runs in the degraded repo, but the refusal contract is broken and the matrix would not notice unless a combo case exists (S-C1 below).
- **Smallest fix.** Inside the loop, for `rel = info/attributes` only, set `META_SOFT_REASON`/`META_SOFT_PATH` (first wins) and `continue`. Keep `protected_fail` for every other entry. Return 1 after the loop if a soft reason was set. Change the call sites from `|| exit 2` to `|| soft=1` only after confirming that `protected_fail` still `exit 2`s inside the function, which it does (`protected_fail` :200-208).

### F2 — major (A2/A3): the linked-admin site :790 and the reversed order at :790/:791

- **Evidence.** :790 `guard_git_files "$admin" || exit 2` runs before :791 `guard_git_links "$admin"`. The claim lists :790 among the sites to soften.
- **Hazard 1 (under-softening).** If :790 is left as `|| exit 2` while `guard_git_files` returns 1 for attributes, H13 still kills the whole run.
- **Hazard 2 (over-softening).** If :790 becomes `|| soft=1` and someone also reorders or short-circuits, an admin with `info/attributes -> /dev/zero` (escaping) passes :790 softly. It must still hit :791 and refuse. Today it refuses at :790 as non-regular. After D2 it must refuse at :791 as a symlink.
- **Semantics.** git never reads an admin's `info/attributes` (path.c `common_list` makes `info` common), so degrading M for H13 is a conservative over-approximation. It loses M's measurement over an inert file. That is acceptable, but disclose it, or skip `info/attributes` (and `info/exclude`, likewise common) for admin dirs.
- **Smallest fix.** :790 → `|| soft=1`, keep :791 unconditional, and add S-H13 plus S-C4 (admin escaping symlink → exit 2).

### F3 — minor (A4): duplicated or masked diagnostics

- **Evidence.** `guard_git_surface` runs for the same repo in `list_repos` (:1266/:1269/:1299, result discarded with `|| true`), again in `census_one` (:1177), and for linked worktrees in `worktree_extra_flags` (:1156). `CFG_SOFT_REASON` is first-wins (:579-583) and is printed as `config-unsupported: <reason>` (:1178, :1157).
- **Impact.**
  - If the new `git-metadata-unsupported` line is printed at detection inside `guard_git_files`, each affected repo gets it twice (list pass plus row pass), or more with worktrees.
  - If it is routed through `CFG_SOFT_REASON`, the stderr format is wrong. A repo that also has a soft config reason earlier in the walk prints only the config reason, so the claim's diagnostic never appears.
- **Smallest fix.** Keep separate `META_SOFT_REASON`/`META_SOFT_PATH` variables, reset in `guard_git_surface`. Print `souji-census: git-metadata-unsupported <reason> <sanitize_field path>` once, in `census_one`'s and `worktree_extra_flags`' soft branches, in addition to any `config-unsupported` line. Oracle: exactly one such line per affected repo (S-M1).

### F4 — minor (claim wording vs behaviour, A4): directory, dangling and socket semantics

- **Gap.** The claim says "non-regular … degrades", but :531 exempts directories. git handles a directory benignly (EISDIR → empty frame; source above), so a normal row is truthful.
- **Smallest fix.** Either pin H8 = normal row and word the claim "FIFO, socket or device (a directory is read by git as empty)", or drop the `-d` exemption for `info/attributes` only and pin H8 = degrade. Do not leave it unpinned.
- **Related pins.** H9 (dangling inside the gitdir) must stay a normal row, since git gets ENOENT and treats the file as absent. H12 (socket) can degrade, because git only gets ENXIO, but disclose that as conservative.

### F5 — major, adjacent (outside the D2 claim; route it, do not widen this round): unguarded blocking-open surfaces still hang the census

There is no timeout anywhere in the census. An attacker-controlled fleet repo can hang the whole run through files `guard_git_files` does not cover.

- **`worktrees/<id>/gitdir` as a FIFO.** `guard_worktree_registrations:775` does `[ -f "$reg" ] || continue`, so the FIFO is skipped silently. `count_worktrees:917` then runs `git worktree list`, which calls `get_linked_worktree`, which calls `strbuf_read_file(worktrees/<id>/gitdir)` (worktree.c, read this session) and blocks in `open` [INFERENCE: `strbuf_read_file` uses a plain `open(O_RDONLY)`]. `worktrees/<id>/HEAD` (`add_head_info`) and `locked` are the same class [INFERENCE].
- **`info/grafts` and `shallow` as FIFOs.** commit.c `read_graft_file` does `fopen_or_warn(graft_file, "r")`, called from `prepare_commit_graft`, which also calls `is_repository_shallow` and is reached via `lookup_commit_graft` (read this session). `count_unpushed:921-931` (`rev-list --count`) parses commits, so it blocks [INFERENCE on the rev-list → parse_commit_buffer → lookup_commit_graft path]. Neither name is in :521.
- **Loose refs as FIFOs** (`refs/heads/x`, read by `for-each-ref`/`rev-list --branches`) [INFERENCE: the files backend opens loose refs].
- **Smallest fix (next round).**
  - Add `info/grafts shallow` to the soft or refuse list.
  - In `guard_worktree_registrations`, treat an existing non-regular `gitdir`/`HEAD`/`locked` as degrade (the current `continue` lets git open it).
  - Optionally refuse non-regular, non-directory, non-symlink entries anywhere under `refs/` using `find -P "$dir/refs" ! -type f ! -type d ! -type l -print -quit` (stat-only).
  - A `timeout -k` wrapper on git calls would be the general backstop. That is a design choice for the lane, not D2.
- Disclose in the r17 report that D2 removes one hang trigger class, not all of them.

### F6 — info (A2 disclosure): one escaping symlink in any `.git` aborts the whole fleet run

H3, H4, H5, H10 and H11 all refuse through `guard_git_links`/`resolve_guarded` before `guard_git_files` runs. This is the r14 namespace policy, which the claim keeps. For H4 the refusal is load-bearing: it is what keeps `/dev/zero` from being read.

The cost: a hostile or merely odd repo (`info/attributes -> /dev/null`) denies the census for every repo. The `symlink-loop` refusal is labelled `path-protected` although nothing protected is involved. Disclose under L0; no change this round.

### F7 — residual (A1): TOCTOU

The guard does `stat`/`test`; git's `open` comes later. A repo owner who swaps a regular `info/attributes` (or a dangling H9 target) for a FIFO between the two hangs the census. The census header already discloses "guard and later access are not one atomic operation". D2 cannot close this without a timeout or `O_NONBLOCK`-style probing. Disclose; do not claim "never hangs".

## Fixture test shapes (for `tests/fixtures/r17-census-hygiene.py`)

Each shape is one repo under its own `--root` (using `--include-root` style, like `r15-census-config.py` `soft_repo`/`unsafe_repo` at :1041-1086), unless marked "mixed".

Common setup (provoker): `init_repo`, commit `kept.txt`, set `refs/remotes/origin/master` to the tip (so the row is CLEAN when unharmed), then `os.utime(kept.txt, (t+7, t+7))` with identical content. The stat-dirty, content-same tracked file makes status content-check it, which runs the attribute bootstrap and opens `info/attributes` on guardless arms [INFERENCE: refresh → `convert_to_git` chain]. Without the provoker, a31642d/cc21683 may pass vacuously.

Expected results per arm: pre-harm a31642d / r14 cc21683 / r16 5fa6017 / changed. "hang" means the per-run timeout fired (expected rc 124 in the runner's convention).

| id | setup | a31642d | cc21683 | 5fa6017 | changed |
|---|---|---|---|---|---|
| S-CTL | regular `info/attributes` containing `*.txt text` + provoker | CLEAN | CLEAN | CLEAN | CLEAN. **Vacuity check:** the strace shows git `openat` of `.git/info/attributes` (proves the provoker works) |
| S-H1 | `os.mkfifo(.git/info/attributes)` | hang | hang | exit 2 nonregular | degrade `git-metadata-nonregular` |
| S-H2 | `mkfifo .git/fifo-in`; `symlink("../fifo-in", .git/info/attributes)` | hang | hang (links pass; :477 lacks attributes) | exit 2 | degrade nonregular; diagnostic path = `.git/info/attributes` |
| S-H3 | `mkfifo $SCRATCH/outside.fifo`; symlink to it | hang | exit 2 git-metadata-symlink | exit 2 symlink | exit 2 symlink |
| S-H4 | symlink → `/dev/zero` | **unsafe: run only under `prlimit --as=1G`**, expect git killed or ENOMEM → `status-unverifiable` or a timeout; otherwise mark not-run | exit 2 symlink | exit 2 symlink | exit 2 symlink |
| S-H5 | symlink → `/dev/null` | CLEAN | exit 2 symlink | exit 2 symlink | exit 2 symlink (pinned residual F6) |
| S-H6 | `$SCRATCH/canary.attr` = `* filter=x\nCANARY-r17-attr\n`; `os.link(canary, .git/info/attributes)` | CLEAN (reads it) | CLEAN (reads it) | exit 2 hardlink | degrade `git-metadata-hardlink`; `CANARY-r17-attr` absent from stdout/stderr; no `openat` of either name |
| S-H7 | regular `.git/info/attributes` plus `os.link` to `.git/info/attributes.bak` | CLEAN | CLEAN | exit 2 hardlink | degrade hardlink |
| S-H8 | `mkdir .git/info/attributes` | CLEAN | CLEAN | CLEAN | per the F4 decision (CLEAN or degrade); pin one |
| S-H9 | `symlink("../nope", .git/info/attributes)` | CLEAN | CLEAN | CLEAN | CLEAN (must not degrade) |
| S-H10 | `symlink("/nonexistent/x", .git/info/attributes)` | CLEAN | exit 2 symlink | exit 2 symlink | exit 2 symlink |
| S-H11 | `symlink("attributes", .git/info/attributes)` | CLEAN | exit 2 symlink-loop | exit 2 symlink-loop | exit 2 symlink-loop |
| S-H12 | AF_UNIX socket bound at `.git/info/attributes` (bind, then close; the inode persists) | CLEAN | CLEAN | exit 2 nonregular | degrade nonregular |
| S-H13 | M with a registered linked worktree (selftest :1573-1582 pattern); `mkfifo M/.git/worktrees/wt1/info/attributes` | CLEAN, no hang (git never reads it) | CLEAN | exit 2 (:790) | per the F2 decision: M `error` + one diagnostic naming the admin path, or M normal; pin one |
| S-H14 | N = init outside the fleet; `M/.git/commondir` = abs `N/.git`; `mkfifo N/.git/info/attributes` | hang | hang | exit 2 (:849) | degrade M; diagnostic path = `N/.git/info/attributes` |
| S-H15 | M with linked worktree W outside the fleet; `W/.git` → admin A; `A/commondir` → `N/.git`; FIFO in `N/.git/info/attributes`; provoker in W | hang (W status) | hang [INFERENCE] | exit 2 (:891) | M row measured, flags include `wt-dirty`; no `git -C W status` in the spy log; one diagnostic naming N |
| S-H16 | fleet child L with `.git` file → `N/.git/worktrees/l`; FIFO in N's attributes | no row, exit 0 | no row | no row | no row, no diagnostic, no `stat` of the FIFO in strace |
| S-MIX | mixed fleet: `a-benign`, `m-fifo` (S-H1), `z-benign` | hang | hang | exit 2, zero rows | exit 0; a/z CLEAN and byte-equal to a fleet without m; m `error` |
| S-M1 | S-MIX diagnostics | — | — | — | exactly one `git-metadata-unsupported` line in stderr (F3) |
| S-C1 | S-H1 + `mkfifo .git/objects/info/alternates` | hang | exit 2 | exit 2 | **exit 2** (F1 falsifier) |
| S-C2 | S-H1 + hardlinked `.git/config` | hang | exit 2 | exit 2 | exit 2 |
| S-C3 | S-H1 + `[include] path = <synthetic AGENT>/secret.gitconfig` | hang | exit 2 | exit 2 | exit 2 `include-protected`, no store access |
| S-C4 | S-H13 admin plus `worktrees/wt1/info/attributes -> /dev/zero` (escaping) | CLEAN | exit 2 | exit 2 | exit 2 `git-metadata-symlink` (F2 falsifier) |
| S-C5 | S-H1 + soft config (`include.path = ~nobody/x`) | hang | exit 2 | exit 2 | degrade; stderr has **both** `config-unsupported` and `git-metadata-unsupported` (F3 masking falsifier) |

### Oracles

- **Degrade.** rc 0. Row exactly `0 0 0 0 '' error`. The diagnostic must match the format that finally lands. Claim text: `^souji-census: git-metadata-unsupported <reason> <path>$`. CensusD1D2 reports implementing `souji-census: git-metadata-unsupported: <reason> (<path>)`, so align the claim and the code before pinning. Reason ∈ {nonregular, hardlink}; path ends `/info/attributes`. No `path-protected`.
- **No open.** Using strace `-e trace=%file`, no `open`/`openat` names the resolved attributes path, its symlink target, or the hardlink partner. `stat`/`newfstatat`/`statx` are allowed.
- **No git.** The spy log has no `git -C <degraded repo>` execve. `git config --file <cfg>` from `scan_config_file` is allowed.
- **Timing.** Wall time under 30 s.
- **Refuse.** rc 2, stdout empty, stderr `path-protected: <reason>`.

### Harness requirements (operability of the fixture itself)

1. Run the tool with `start_new_session=True` and a per-case timeout (30 s). On timeout:
   - `os.killpg(proc.pid, SIGKILL)`. Killing only the strace child leaves a git process blocked in `open` (tracees detach and continue).
   - Then unblock every fixture FIFO: `fd = os.open(p, os.O_WRONLY | os.O_NONBLOCK)` (ENXIO when no reader is left, which is fine), then `os.close(fd)`.
   - The r15 runner's `subprocess.run(..., timeout=90)` (`r15-census-config.py:781-793`) does neither.
2. Never run S-H4 on a31642d without an address-space cap (`prlimit --as` or `resource.setrlimit` in `preexec_fn`). git there would read `/dev/zero` into memory without bound.
3. Use the provoker, and the S-CTL vacuity assertion on every arm. Otherwise the "hang" expectations for a31642d/cc21683 can silently become CLEAN, and the matrix loses falsifying power.
4. Build fixtures only under the runner's `/var/tmp` scratch; HOME and AGENT are synthetic, as in r15.

## Commands run (exact) and outputs

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 5fa6017:tools/souji-census.sh`: 1878 lines (read; cited above).
- `cd …/souji-shokunin && git diff --stat 5fa6017 -- tools/souji-census.sh; git ls-tree --name-only 5fa6017 tests/fixtures/; git diff 5fa6017 -- tools/souji-census.sh`: the diffs were empty. The fixture list includes `r14-census-boundary.py` and `r15-census-config.py`; there is no r17 fixture yet.
- `for r in a31642d cc21683 5fa6017; do git show $r:tools/souji-census.sh | grep -n -E 'for rel in|info/attributes|attributesFile=|git-metadata-nonregular|find -P "\$dir" -type l'; done`:
  - a31642d: no match.
  - cc21683: `470 find … -type l`, `477 for rel in config HEAD index packed-refs commondir info/exclude objects/info/alternates`, `488 git-metadata-nonregular`, `712 -c core.attributesFile=/dev/null status`.
  - 5fa6017: `514`, `521 … info/exclude info/attributes objects/info/alternates`, `532`, `1002`, `1007`, `1037`.
- `git log --oneline -3 -- tools/souji-census.sh`: `0a70bef`, `cbf688a`, `b410186`.
- `git show 5fa6017:tools/souji-census.sh | grep -n -E '^guard_git_files|^count_worktrees|^emit_census|^census_one|guard_git_files "\$admin"'`: 519, 790, 915, 1174, 1308, 1876.
- `… | sha256sum`: `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`.
- `git ls-tree --name-only 5fa6017 .ufo/waves/round-16/w1/ .ufo/waves/round-16/w2/ | grep -i census`: located `w2/RevCensusScanFinal.md`.
- Reads of exact named files:
  - `corpus/lessons/round-16-verifier-spotcheck.md` (D2 at :135);
  - `.ufo/waves/round-16/w2/RevCensusScanFinal.md` (:132-157);
  - `tests/fixtures/r15-census-config.py` (:757-808 run_tool, :1054-1076 soft oracle; plus a grep of its def/case structure).
- Web source reads (git `master`, raw.githubusercontent.com): `attr.c` (read_attr_from_file :699-735, bootstrap :925-955), `path.c` (common_list), `commit.c` (read_graft_file :293-305, prepare_commit_graft :322-335), `worktree.c` (get_linked_worktree, get_worktrees_internal).
- One `curl -fsS …/path.c | grep …` via bash: exit 1, no output. It was replaced by the read tool.
- Peer notes sent: to `SoujiR17-3.CensusD1D2` (F1–F4 summary) and `SoujiR17-3.MatrixR17` (unsafe arms, killpg/unblock, prlimit, provoker).

## Coordination outcome (peer messages, after the report was drafted)

`SoujiR17-3.CensusD1D2` acknowledged F1–F4 as adopted in its landing edit:
- the soft flag is recorded and the loop finishes, so alternates still refuses;
- :790 → `|| soft=1`, and :791 still runs;
- `META_SOFT_*` is printed once, by `census_one`/`worktree_extra_flags`;
- a directory stays allowed, and degrade is scoped to FIFO/socket/device/hardlink/symlink-to-nonregular.

I have not verified any of this; there was no diff at review time.

### F8 — major (raised in reply, A3)

The executor also said it skips the git-config enumeration for a degraded gitdir. That would drop the protected-include refusal: S-C3 becomes exit 0 instead of exit 2. It would also contradict the header's "a soft finding never stops the scan". The skip is not needed: `scan_config_file` runs `git config --file <cfg> --no-includes --list -z` (:618, :621), which reads only that file and never `info/attributes`.

- **Fix.** Keep `guard_git_config`, commondir, `guard_alternates` and `guard_worktree_registrations` running after a soft attributes finding. Skip only the measurement git calls in `census_one`, which already return early (:1177-1181).
- **Falsifier.** S-C3. The objection was sent to CensusD1D2. The diagnostic-format mismatch (`: <reason> (<path>)` vs the claim's `<reason> <path>`) was flagged in the same message.

## Verdict

- **5fa6017 is hang-safe for H1–H12 in the main gitdir and the commondir (it refuses, and never opens), but at the wrong blast radius.** For FIFO, socket and hardlink shapes the whole run exits 2 (A2 fails, which is the routed D2). The two shapes it accepts, directory and in-gitdir dangling symlink, are benign per git source.
- **The D2 design holds if** (a) the soft path does not return early (F1), (b) :790 is softened while :791 still runs (F2), (c) the diagnostic has its own channel and is printed once (F3), and (d) the directory decision is pinned (F4).
- **The census still has unguarded blocking-open triggers** (F5: `worktrees/<id>/gitdir`, `info/grafts`, `shallow`, loose refs) plus TOCTOU (F7). "Never hangs on a hostile repo" therefore must not be claimed this round.

Tool installs/updates: none.
