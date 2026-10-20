STATUS: DONE — opened git v2.56.0 `attr.c`/`attr.h`/`wrapper.c`; the FIFO block is a plain blocking `open(2)` with no `S_ISREG`/`O_NONBLOCK` fence and the only fstat check is a post-open size cap; draft SOURCES row S064 supplied with a 13-word verbatim quote.

# SrcGitAttrC — how git opens `$GIT_DIR/info/attributes` and `.gitattributes` (source item, r18 W1)

## Source opened

- Exact URL fetched: `https://github.com/git/git/blob/v2.56.0/attr.c` — served as `https://raw.githubusercontent.com/git/git/v2.56.0/attr.c` (reader method `github-raw`, plain text, 1373 lines).
- Access date: 2026-10-20.
- Version line: none is served in the raw text (plain source, no last-updated header). Version is pinned by the URL tag and by `git ls-remote`: `refs/tags/v2.56.0` = `2478544319491bbd2a42cc57a83e3d2f4730a280`, peeled commit `a018953688f1b10bddf91bff8747068f5f4746a4`. Host `git --version` = `git version 2.56.0`, so the tag matches the installed release.
- Companion files opened at the same tag: `attr.h` (`ATTR_MAX_FILE_SIZE`), `wrapper.c` (`open_nofollow`).

## Located verbatim quote (attr.c, tag v2.56.0, lines 702-705, `read_attr_from_file`)

Tab-indented exactly as served:

```
	if (flags & READ_ATTR_NOFOLLOW)
		fd = open_nofollow(path, O_RDONLY);
	else
		fd = open(path, O_RDONLY);
```

`wc -w` on this block: **13**.

## Draft SOURCES row (S064; last committed id is S063, S064 is free)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S064 | git source at tag v2.56.0: attr.c, attr.h, wrapper.c — https://github.com/git/git/blob/v2.56.0/attr.c | code | A | how git opens `$GIT_DIR/info/attributes` and worktree `.gitattributes`; not which commands consult attributes, not a runtime bound, not other versions or platforms | tag v2.56.0 (annotated 2478544, commit a018953): attr.c:693 `read_attr_from_file`, :702-705 blocking open choice, :712-720 `fstat` after open then size-only cap, :937 root `.gitattributes` with `READ_ATTR_NOFOLLOW`, :1028 per-directory `.gitattributes` same, :942 info frame with flags lacking NOFOLLOW; attr.h:120 `ATTR_MAX_FILE_SIZE (100 * 1024 * 1024)`; wrapper.c:828-861 `open_nofollow` = `open` plus `O_NOFOLLOW`, with lstat fallback | `$GIT_DIR/info/attributes` is opened by a plain blocking `open(path, O_RDONLY)` (info frame passes flags without `READ_ATTR_NOFOLLOW`), `.gitattributes` by `open_nofollow` which adds only `O_NOFOLLOW`; neither passes `O_NONBLOCK`, the `fstat` runs after the open and checks only the 100 MiB size cap, and attr.c contains no `S_ISREG`/`S_ISFIFO` fence, so a FIFO at either path blocks inside git's own open and a stat taken before the open cannot be atomic with it | mined | 2026-10-20 | on-release | corpus/lessons/round-18.md |

## What it teaches for souji r18 (C1)

1. `$GIT_DIR/info/attributes` — `bootstrap_attr_stack` calls `read_attr_from_file(git_path_info_attributes(), flags)` at attr.c:942 with `flags = READ_ATTR_MACRO_OK` (attr.c:915) and no `READ_ATTR_NOFOLLOW`, so `read_attr_from_file` reaches attr.c:705 `fd = open(path, O_RDONLY);`. No `O_NONBLOCK` anywhere (grep counts below). On a writer-less FIFO this open blocks until a writer appears — the exact r17 `d2-fifo` block.
2. `.gitattributes` — root and per-directory lookups pass `READ_ATTR_NOFOLLOW` (attr.c:937, :1028), which selects `open_nofollow(path, O_RDONLY)` (attr.c:703). `open_nofollow` is `open(path, flags | O_NOFOLLOW)` (wrapper.c:831); `O_NOFOLLOW` only refuses a final-component symlink (the `#else` path only lstat-rejects `S_ISLNK`, wrapper.c:851-861). It does **not** make a FIFO non-blocking, so a FIFO `.gitattributes` blocks identically; only a symlink is refused.
3. No type fence inside git: `fstat(fd, &st)` is at attr.c:712, i.e. **after** the potentially blocking open, and its only consequence is `if (st.st_size >= ATTR_MAX_FILE_SIZE)` (attr.c:717, cap = 100 MiB at attr.h:120). `grep -c` over attr.c at the tag: `S_ISREG` 0, `S_ISFIFO` 0, `O_NONBLOCK` 0; wrapper.c `O_NONBLOCK` 0.
4. Direction does not gate the info frame: `bootstrap_attr_stack` reads it unconditionally when `startup_info->have_repository` (attr.c:940-943), regardless of `direction` (attr.c:680, zero-initialized = `GIT_ATTR_CHECKIN` per attr.h:223-227). So any command that builds the attribute stack opens `info/attributes`; the worktree `.gitattributes` open, by contrast, is conditional on the direction/tree branch in `read_attr` (attr.c:841-862).
5. Consequence for C1: `guard_git_files` (tools/souji-census.sh:546-585) is a stat probe taken **before** git runs; the r17 shim swaps the regular file for a FIFO on the later `status` call. Nothing in git's open path can be made atomic with that probe — [INFERENCE] the race cannot be closed by adding another pre-open stat on the census side. The only closure is bounding the subprocess: `emit_census` currently runs `row=$(census_one "$repo")` in the foreground (tools/souji-census.sh:1403-1405), so one blocked `open(2)` stops every later repo. The declared fix (per-repo process group + temp-file stdout + SIGTERM then SIGKILL, error row, continue, exit 0) is the right shape and needs no further file guard.

## What it does NOT establish

- It does **not** show that a given git command (e.g. `status`) performs an attribute lookup. The open exists only when a command builds the attribute stack; for `status` the block is an observation (tests/fixtures/r17-census-hygiene.py:749-758 "a census that opens it blocks (writer-less FIFO open)"), not a code-path trace of wt-status/diff.
- It does **not** establish that `O_NOFOLLOW` prevents the block; it refuses symlinks only, and a FIFO still blocks (contra any reading of the flag name as a type gate).
- It does **not** establish cross-version or cross-platform behavior. Only tag v2.56.0 (host matches) was read; the `#else` `open_nofollow` (wrapper.c:851-861) is lstat-then-open and is itself racy.
- It does **not** establish any git-side timeout or recovery; nothing in attr.c bounds a stuck open, so a hang is unbounded from git's side.
- It does **not** establish that the 100 MiB cap protects the census: the cap is applied after the open and is a size check, not a type check; [INFERENCE] a FIFO's `st_size` is 0, so it would pass the cap if a writer ever unblocked the open.
- It does **not** establish that `guard_git_files` is incorrect; the guard's soft `git-metadata-nonregular` degrade (tools/souji-census.sh:568-575) is correct for a file present at probe time and simply cannot see a later swap.

## Verdict

**Holds** for C1's mechanism: the block is a blocking `open(O_RDONLY)` on a FIFO in git's own code, with no `S_ISREG`/`O_NONBLOCK`/early-fstat fence, for both `$GIT_DIR/info/attributes` (plain open) and worktree `.gitattributes` (`O_NOFOLLOW` open). The source supports "git cannot be relied on to bound itself"; it does not itself prove the reproduction, which the r17 fixture and L1's b576341 run establish.

Smallest fix (advisory, L1 integrates): implement the already-declared bound in `emit_census` (tools/souji-census.sh:1394-1416) — `set -m` only around the `census_one` fork, stdout to a private temp file, watchdog SIGTERM to the process group at the bound and SIGKILL 2 s later, timed-out repo becomes the `error` row plus `souji-census: repo-timeout <N>s <repo>` on stderr, other repos still measured, exit 0; `census_one` rc 2 still aborts the run with 2. Do not add a second stat guard: the source shows the race is in the open, not in the file type.

## Exact commands run and outputs

1. `read https://github.com/git/git/blob/v2.56.0/attr.c` → served `https://raw.githubusercontent.com/git/git/v2.56.0/attr.c`, `Content-Type: text/plain`, 1373 lines.
2. `git ls-remote --tags https://github.com/git/git refs/tags/v2.56.0` → `2478544319491bbd2a42cc57a83e3d2f4730a280 refs/tags/v2.56.0`; `refs/tags/v2.56.0^{}` → `a018953688f1b10bddf91bff8747068f5f4746a4`. `git --version` → `git version 2.56.0`.
3. `curl -fsS https://raw.githubusercontent.com/git/git/v2.56.0/attr.c | sed -n '693,720p'` → verbatim block above plus `if (fstat(fd, &st)) {` at 712 and `if (st.st_size >= ATTR_MAX_FILE_SIZE) {` at 717.
4. `sed -n '936,943p'` → `e = read_attr(istate, tree_oid, GITATTRIBUTES_FILE, flags | READ_ATTR_NOFOLLOW);` (937), `e = read_attr_from_file(git_path_info_attributes(), flags);` (942).
5. `grep -n "next = read_attr(istate"` → `1028: next = read_attr(istate, tree_oid, pathbuf.buf, READ_ATTR_NOFOLLOW);`.
6. `grep -n "ATTR_MAX_FILE_SIZE"` in attr.h → `120:#define ATTR_MAX_FILE_SIZE (100 * 1024 * 1024)`.
7. Counts: `S_ISREG attr.c: 0`, `O_NONBLOCK attr.c: 0`, `S_ISFIFO attr.c: 0`, `O_NONBLOCK wrapper.c: 0`.
8. `grep -n -A14 "^int open_nofollow" wrapper.c` → function at 828, `open(path, flags | O_NOFOLLOW)` at 831, lstat `#else` fallback 851-861.
9. Quote word count: `printf <block> | wc -w` → `13`.
10. Local reads: `corpus/SOURCES.md:1-43,44-113` (header + S051-S063 column contract; `grep -n "S064\|S063"` shows S063 last, S064 absent); `tools/souji-census.sh:540-600` (guard) and `:1387-1425` (`emit_census` loop); `tests/fixtures/r17-census-hygiene.py:590-599,749-758` (`d2-fifo`).

## Probe-rule record

No delegation. No `jj`. No git write (only `git ls-remote` read and `git --version`). No souji tool executed, no process signalled, no network write; all fetches were GETs of named source URLs. Only exact named files were read; no recursive search over the lane, fleet root, or a directory tree. Tool installs/updates: none.

## Remaining unknowns

- The precise caller chain by which `git status` consults attributes on this host was not traced in source; the r17 fixture's observed block is the ground truth for the command.
- Whether `status` ever supplies a non-NULL `tree_oid` at v2.56.0 (which would route root `.gitattributes` through the tree/blob reader) is not established; the info frame is unconditional either way.
- Behavior at tags other than v2.56.0 and on platforms without `O_NOFOLLOW` is unexamined.
