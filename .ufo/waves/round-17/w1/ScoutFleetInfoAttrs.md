STATUS: DONE — D2 live exposure is nil: 0 of 22 fleet gitdirs and 0 of 4 linked-worktree admin gitdirs have `$GIT_DIR/info/attributes`; every guarded metadata path in the fleet is a regular file with `nlink=1`, so the planned degrade-to-error-row path would fire for zero live repositories (fixtures only).

# ScoutFleetInfoAttrs — D2 live exposure sweep (`$GIT_DIR/info/attributes`)

Round 17 / WAVE 1 / lane souji-shokunin, base `5fa6017ddcae9f6bd4412df44765f6360cb16294`.
Measured census snapshot: `tools/souji-census.sh` sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (matches the ticket's `64a60fd0…`), working-tree diff vs HEAD for that file: empty (`git diff --stat` rc=0, no output — read before sibling executors touched it; line numbers below are that snapshot).

## Question

Read-only, stat-only: for the fleet root `/home/vgpnk/Projects/shokunin` and every `/home/vgpnk/Projects/shokunin/*-shokunin`, plus every linked-worktree gitdir and its common dir, does `<gitdir>/info/attributes` exist, and if so what is its type and link count? How many live repositories would C1 D2 (hardlinked or non-regular `$GIT_DIR/info/attributes` → per-repo `error` row, exit 0) actually degrade? No file contents were opened except the two named config-dump/ancillary reads; `info/attributes` itself was never opened (stat only).

## What the change would touch (code as measured)

- `guard_git_files` at `tools/souji-census.sh:519-535`; rel list at `:521` already contains `info/attributes` alongside `config HEAD index packed-refs commondir info/exclude objects/info/alternates`.
- Today both hazards are whole-run refusals: `nlink -gt 1` → `protected_fail "git-metadata-hardlink"` (`:526-530`), non-regular → `protected_fail "git-metadata-nonregular"` (`:531-533`), and `protected_fail` is `exit 2` (`:200-207`).
- Called with `|| exit 2` for the repo gitdir and the common dir, and for each worktree admin gitdir: `:790` (admin), `:831`, `:849`, `:873`, `:891`.
- D2 is **not implemented** at this snapshot: `grep -n 'git-metadata-unsupported' tools/souji-census.sh` returns nothing (only `git-metadata-hardlink` :529 and `git-metadata-nonregular` :532 exist). So "would be degraded" is prospective; the measurement below bounds how much live behavior can change.
- Repo reach: `list_repos` (`:1257-1305`) considers only the root (if `INCLUDE_ROOT=1`, default 0 at `:176`, flag at `:1842`) and its **immediate** children that carry `.git` — no recursive discovery. A fleet-root census therefore covers exactly the 22 repos measured here; a lane-root census with `--include-root` covers exactly one (the lane).

## Result — 22 fleet repositories: no `info/attributes` anywhere

All 22 `.git` are real directories (no gitfile redirection): `git -C <repo> rev-parse --absolute-git-dir` returned `<repo>/.git` for each; `git -C <repo> rev-parse --git-path info/attributes` returned `.git/info/attributes` for the three probed (root, game-dev-2d, kotodama). `commondir` absent in every main gitdir (`cat <repo>/.git/commondir` ENOENT), i.e. no repo is itself a linked worktree.

For every row: `stat -c '%F %h %s' <repo>/.git/info/attributes` → `No such file or directory` (ENOENT); `test -L` false (no dangling symlink masquerading as absent); `ls -la <repo>/.git/info` shows only `exclude` (regular, 240 or 277 B) plus `refs` where present. Nothing named `attributes`.

| repo | `.git` kind | `info/` entries | `info/attributes` | guard-list anomalies |
|---|---|---|---|---|
| shokunin (fleet root) | dir | exclude, refs | **absent** | none |
| audio-shokunin | dir | exclude, refs | **absent** | none |
| chousa-shokunin | dir | exclude, refs | **absent** | none |
| game-dev-2d-shokunin | dir | exclude, refs | **absent** | none (+3 worktree admins, below) |
| game-dev-3d-shokunin | dir | exclude, refs | **absent** | none |
| kagi-shokunin | dir | exclude | **absent** | none |
| kaidoku-shokunin | dir | exclude, refs | **absent** | none |
| kake-shokunin | dir | exclude | **absent** | none |
| kama-shokunin | dir | exclude, refs | **absent** | none |
| kasegi-shokunin | dir | exclude | **absent** | none |
| kengaku-shokunin | dir | exclude | **absent** | none |
| kotoba-shokunin | dir | exclude, refs | **absent** | none |
| kotodama-shokunin | dir | exclude, refs | **absent** | none (+1 worktree admin) |
| kumitate-shokunin | dir | exclude, refs | **absent** | none |
| lore-shokunin | dir | exclude, refs | **absent** | none |
| mado-shokunin | dir | exclude, refs | **absent** | none |
| mori-shokunin | dir | exclude, refs | **absent** | none |
| revenger-shokunin | dir | exclude, refs | **absent** | none |
| souji-shokunin | dir | exclude, refs | **absent** | none |
| tabi-shokunin | dir | exclude, refs | **absent** | none |
| tameshi-shokunin | dir | exclude, refs | **absent** | none |
| tsukuroi-shokunin | dir | exclude | **absent** | none |

`info/refs` in 17 repos is an ordinary update-server-info artifact; it is not in the guard rel list and is irrelevant to D2.

### The whole guard list is clean, not just `info/attributes`

For all 22 gitdirs, for every rel in `config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates`:
`[ -L ]` never true, `[ -f ]` → `stat -L -c %h` always `1`, no `-e`-true non-directory non-regular entry, `commondir` absent. Output of the sweep was the single word `DONE` (no `SYMLINK`, `HARDLINK`, `NONREG` lines). So no live repo is refused today by `guard_git_files`, and D2's reclassification cannot change any live row — not only for `info/attributes` but for the sibling entries too.

## Result — linked worktrees: 4 admin gitdirs, all clean; every working directory is gone

`git -C <repo> worktree list --porcelain` reports exactly four non-main registrations:

| admin gitdir | registered worktree path | path on disk | state | `commondir` | per-worktree `info/attributes` |
|---|---|---|---|---|---|
| game-dev-2d-shokunin/.git/worktrees/game-dev-2d-shokunin-wt-r100 | /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r100 | **ABSENT** | locked (`souji r5` pin) | `../..` | **absent** (ENOENT, not a symlink) |
| game-dev-2d-shokunin/.git/worktrees/game-dev-2d-shokunin-wt-r98 | …-wt-r98 | **ABSENT** | locked (same pin) | `../..` | **absent** |
| game-dev-2d-shokunin/.git/worktrees/game-dev-2d-shokunin-wt-r99 | …-wt-r99 | **ABSENT** | locked (same pin) | `../..` | **absent** |
| kotodama-shokunin/.git/worktrees/ca02-wt-r34 | kotodama-shokunin/.scratch/ca02-wt-r34 | **ABSENT** | prunable ("gitdir file points to non-existent location") | `../..` | **absent** |

Common dirs resolve to the main `.git` of each repo (both already measured absent), so both paths a linked worktree could carry an attributes file on are empty. Note git's own resolution for a live linked worktree (`rev-parse --git-path info/attributes` in that worktree) could not be exercised because all four worktree directories are missing; it does not change the result since both candidate gitdirs are absent.

## Fixture path named in C3(e) — observed state

`tests/vault/vadv54-run/p/p6repo/.git` does **not exist right now**: `stat` → ENOENT, `ls -la` of `p6repo` shows only `inner/` and `one.txt`, and `git ls-files -s` shows the two tracked files (`inner/keep.txt`, `one.txt`). The `p6repo` directory mtime is `Oct 20 13:33` (today, during this wave), so this is very likely concurrent fixture state owned by another seat/test rather than a contradiction of the ticket. Even if the empty `.git` stub is recreated, it is an empty directory with no `info/` child — it can contribute no `info/attributes`, so it cannot add D2 exposure. Flagged only so nobody treats my p6repo stat as evidence about C3(e).

## Auxiliary breadth check (outside the assigned set)

One non-recursive level over `/home/vgpnk/Projects/*/` (15 repos with `.git`, all main gitdirs, no worktree walk): `audio-shokunin-publish, burnerchrome, gkeep, godspeed-core, kimi-code, kimi-shokunin, myskills, omarchy-usage-tray, ompskills, prymeagnt, prymeagnt-archive, shokunin, the-kimiraikkoner, ufo-fsd-alpha, xsnapshot` — `info/attributes` **absent** in all 15. (Also: no `/etc/gitconfig`, no `~/.gitconfig`; `~/.config/git/config` carries no `status.showUntrackedFiles`, `core.attributesFile`, or `extensions.worktreeConfig` key — dumps filtered to those keys only. `core.attributesFile` is a separate attribute source the D2 guard does not stat; no live repo sets it, so nothing is missed in practice today.)

## Findings

F1 (observed, high confidence). **No `$GIT_DIR/info/attributes` exists in any live gitdir of the fleet**: 22 main gitdirs + 4 worktree admin gitdirs, all ENOENT, none a symlink. Expected count of repos degraded by C1 D2 on this host = **0** (0 of 22 repos; 0 of 26 reachable gitdirs; the denominator is the exact set a fleet-root census reaches, per `list_repos`).

F2 (observed, high confidence). All eight guarded metadata paths in all 22 gitdirs are regular, `nlink=1`, non-symlink. Therefore no live repository trips today's hard refusals (`git-metadata-hardlink` :529, `git-metadata-nonregular` :532) and D2's reclassification is invisible on live state. A fleet census at this base and after a correct D2 patch must produce identical bytes for these 22 repos on this axis.

F3 (observed, high confidence). D2 is unimplemented at the measured snapshot: the string `git-metadata-unsupported` does not exist and `info/attributes` sits in the hard-fail rel list. The ticket's "would be degraded" is therefore hypothetical for live state; only the r17 hygiene fixture can exercise it. A fixture that merely reuses an existing lane gitdir would pass vacuously — the fixture **must create** the hardlink (`ln`, `nlink=2`) and the non-regular (`mkfifo` or symlink-to-device) shapes in its own throwaway `/var/tmp` repos, exactly as the D1 sibling found for `status.showUntrackedFiles`.

F4 (observed, medium confidence on tie-break, high on counts). The four linked-worktree registrations are stale: three locked (souji r5 pins) and one prunable, with **all four working directories absent**. Their per-worktree and common `info/attributes` are both absent. Practical consequence: no linked worktree can currently hold an attributes file, and a census row for them is impossible while the paths are gone.

F5 (observed, high confidence — nuance for the D2 predicate). Today's non-regular test is `[ -f ]` then `[ -e ] && [ ! -d ]`; a symlink to a regular file is followed (`-f` true, target `nlink` checked) and a dangling symlink is silently ignored. If D2's "non-regular" means lstat-based (symlink itself), the class widens; measured live exposure is still 0 because `test -L` is false for every candidate path. Worth pinning in the fixture: symlink-to-regular, dangling symlink, FIFO, hardlink.

F6 (observed, low relevance). `info/` in these repos holds only `exclude` (all 22) and `refs` (17); no other file can be mistaken for attributes. `core.attributesFile` is set in no local config, so no alternate attributes file exists fleet-wide.

## Verdict

**Holds — exposure nil.** D2 is the right control (a hardlinked or FIFO `$GIT_DIR/info/attributes` would otherwise be read by git inside an audited repository, or hang on the FIFO), but it has **zero live subjects** on this host: 0/22 fleet repos, 0/4 worktree admin gitdirs, 0/15 non-fleet Projects repos. The plain-repo byte-identical requirement in C1 is guaranteed here for the trivial reason that the guard already sees no file at that path.

## Smallest implication for the r17 harness (advisory, not a code fix)

The hygiene fixture must self-generate every D2 shape inside `/var/tmp` throwaway repos: (a) `info/attributes` hardlinked (`ln` → `nlink=2`) → error row, exit 0, stderr `git-metadata-unsupported … <path>`, neighbours' rows unchanged; (b) `info/attributes` a FIFO (and a symlink case per F5) → same; (c) a control repo where `config` (or `index`) is hardlinked must still produce whole-run exit 2, proving the degradation is scoped to `info/attributes` only; (d) absence must stay silent. Assert on the exact `error` row text and on the absence of any git invocation that opens the file (the fixture can make the file unreadable/FIFO so a stray read would hang or fail the arm).

## Residual unknowns / limits

- No live repo was exercised through the census: running `tools/souji-census.sh` against real directories is forbidden, and D2 does not exist in the measured bytes. All statements are stat-level state, not run output.
- Nested repositories below `tests/` are not reachable by `list_repos` (one level only, F-reach above) and were not recursively enumerated (probe bound); the only ticket-named fixture repo was checked and its `.git` is currently absent. If a future census is pointed **at** a fixture directory as its root, that root repo's own `info/attributes` is the only new subject — none of the currently existing ones has one.
- Whether the r17 `run-matrix.py --changed WORKTREE` invocation passes `--include-root` could not be confirmed: `census/round-17/run-matrix.py` does not exist yet (`MISSING`). Without the flag, a lane-root worktree census yields **no rows at all** (`list_repos` skips dot-dirs and non-repos); with it, exactly the lane repo, whose `info/attributes` is absent.
- `info/attributes` contents were never read (stat only); no credential or secret file was opened. Only `.git/config` key-filtered dumps and three global config key filters were read.

## Tooling

None installed or upgraded. No pacman/uv/npm/cargo transaction; no network write; no `jj`; no git write in any repo.
