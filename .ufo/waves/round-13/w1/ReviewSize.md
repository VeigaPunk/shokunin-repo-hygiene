# ReviewSize — C3 empirical write-safety claim design (souji r13 w1)

Seat: `SoujiR13.ReviewSize` (reviewer, leaf). Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Date: 2026-10-20.
Scope: design review only. No fixture was built or run, no `git repo structure` was executed, no live repo was written, no commits. Certification stays OFF. No non-author status is claimed.
Tool installs/updates: none. Present and used read-only: git 2.55.0-1, strace 7.0-1, shellcheck 0.11.0-158, coreutils 9.11-2, findutils 4.11.0-1 (`pacman -Q`).

## Verdict

The C3 flip recorded in the round-12 Gate (`corpus/lessons/round-12.md:133`: "a /var/tmp fixture diffing `find .git -newer` around a `GIT_OPTIONAL_LOCKS=0 git repo structure` run") is **not sufficient** to admit a write-safety claim. Its detector cannot see several write classes, it has no positive control, and it passes silently on three shapes (symlinked `.git`, bare repo, failed command). Below: the defects, the case matrix, the checks L1 should run, and the one bounded claim the design can support.

## Facts observed (read-only)

- F1 command surface. `git repo structure` default format is the table; the man page says the table "may change and is not intended for machine parsing" and the whole command is "THIS COMMAND IS EXPERIMENTAL. THE BEHAVIOR MAY CHANGE." (installed `git-repo(1)` 2.55.0, `structure [--format=(table|lines|nul) | -z]`). Matches `corpus/SOURCES.md:13` (S005, status `queued`).
- F2 command body, source at tag v2.55.0 (`https://raw.githubusercontent.com/git/git/v2.55.0/builtin/repo.c`, sha256 `706e4ebbc03c4b1701c1375c8108f033acaf6d448f6571bf0c5ea04615b86d02`, fetched to a mktemp file and deleted):
  - `:877` `cmd_repo_structure`; `:884` `format = FORMAT_TABLE`;
  - `:904` `repo_init_revisions(repo, &revs, prefix)`;
  - `:744` `refs_for_each_ref(...)` (read); `:872` `walk_objects_by_path(...)` (read);
  - `:907` `show_progress = isatty(2)` (progress depends on stderr being a tty);
  - `:918` `=`/newline output; `:921` NUL output.
  - The command body contains no index, lock, or file-write call. [INFERENCE] the command is write-free; helper internals (refs backend, path walk, odb) were not read, so this is a hypothesis for the fixture to test, not a fact.
- F3 S006 (`GIT_OPTIONAL_LOCKS`) is `queued` (`corpus/SOURCES.md:14`) and was not opened in this review. The round-12 quote in `corpus/lessons/round-12.md` (S006 row) is the only grounding on file.
- F4 linked-worktree metadata. Installed `gitrepository-layout(5)` (2.55.0, roff lines 380–393): "`worktrees/<id>/gitdir` … The mtime of this file should be updated every time the linked repository is accessed." This means a *read* can legitimately touch a file under `.git`. A manifest case for linked worktrees must expect this and report it, not hide it. S033 (`corpus/SOURCES.md:41`) also records that the layout page omits `worktrees/<id>/index`, which `worktree.c:1001-1008` uses for aging (`corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:13`).
- F5 existing fixture isolation, `tests/fixtures/r12-maintenance-guard.sh`:
  - `:74-78` sets `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`, `HOME=$WORK/home`, and unsets only `GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE`.
  - NOT cleared: `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`, `GIT_TEMPLATE_DIR`, `GIT_CEILING_DIRECTORIES`, `GIT_NAMESPACE`, `GIT_OPTIONAL_LOCKS`, `XDG_CONFIG_HOME`. An inherited `GIT_CONFIG_PARAMETERS` (set by a parent `git -c …`) or `GIT_ALTERNATE_OBJECT_DIRECTORIES` would reach the fixture. `env -i` with an allowlist closes this.
  - `:118-119` setup `add`/`commit` run without `maintenance.auto=false`. `:145` `touch -d '4 months ago'` rewrites mtime backwards — direct evidence that an mtime-based diff is forgeable by the harness itself.
  - `:155` default-config commit; `:170-176` polls up to 30 s for a detached maintenance child to prune. Detached writes can land after a "before" snapshot (see D7).
- F6 the round-12 reviewer's scratch run found `.git` unchanged (`corpus/lessons/round-12.md:150`). One observation, one shape, one unreported command line. Corroboration only; not a method.
- F7 host: `/var/tmp` device 31, `/home` device 57 (`stat -c %d`). `/proc/sys/kernel/yama/ptrace_scope` = 1 (strace on own child is allowed). Mount options for `/var/tmp` were not probed (`findmnt` printed nothing), so atime behavior is unknown.

## Defects in the current design

- D1 `find -newer` is the wrong detector.
  - It reports only files newer than one reference, so ctime-only changes and mtime set back (the r12 fixture does exactly this at `:145`) are invisible.
  - It cannot see a lock created and deleted inside the window (`index.lock`, `*.lock`), so transient writes pass.
  - It needs directories listed to see entry creation/removal.
  - Replace with a full manifest (D12) plus syscall tracing (D8).
- D2 symlinked `.git` → false PASS. `find .git` without `-H`/`-L` (`find -P` is the default) lists only the link itself. Before and after are identical, so the verdict is PASS whatever git does. Resolve the roots first: `git -C "$repo" rev-parse --absolute-git-dir` and `--git-common-dir`, then `realpath`, then `find -P` on the real directory.
- D3 bare repo → false PASS. A bare repo has no `.git` child; the git dir *is* the repo root. `find "$repo/.git"` fails, and if the failure is suppressed (`2>/dev/null`, `|| true`) both manifests are empty. Use the resolved git dir and assert it is non-empty and equal to the repo root.
- D4 linked worktree → incomplete coverage. `$WT/.git` is a file (`gitdir: …`). Shared objects, refs and config live in `$COMMON`, and per-worktree admin in `$COMMON/worktrees/<id>/`. The manifest needs three roots: the worktree's `.git` file, `GIT_DIR` (`worktrees/<id>`), and `GIT_COMMON_DIR`. F4 predicts a `gitdir` mtime touch; record it as an observed change.
- D5 command failure → false PASS. If `git repo structure` exits non-zero (unknown subcommand on an older git, bad option, not a repo) and writes nothing, manifests match. Require: exit 0, non-empty output, and the observed key-name set (pinned on 2.55.0 by L1 from the final run). Do not parse the table (F1). Capture with `--format=nul` (or `-z`) and check keys by name.
- D6 no positive control → no detector sensitivity. A "no change" result means nothing until the same harness demonstrably detects a change. Positive control (predicted, unobserved [INFERENCE from S006 text and the layout of `git status`]): in a second copy of the fixture, `touch base.txt` then `git status` with optional locks ON rewrites `.git/index`; with `GIT_OPTIONAL_LOCKS=0` it does not. The harness must report the first as a change and the second as none. If the control fails to detect, the whole fixture is FAIL, not PASS.
- D7 setup confound and background children. Setup commits without `-c maintenance.auto=false` can spawn `git maintenance run --auto` (default autoDetach, `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:10`). Its writes can land after "before". Fix: setup uses `-c maintenance.auto=false -c gc.auto=0 -c maintenance.autoDetach=false`; before each snapshot, scan `/proc/[0-9]*/cwd` and `/proc/[0-9]*/fd/*` for anything under `$WORK`; if any process remains after a bounded wait, the case is could-not-evaluate (exit 2), not PASS.
- D8 transient writes need syscall evidence. Snapshots cannot see a file created and removed inside the run. `strace -f` is installed. Trace: `openat,openat2` (filter for `O_WRONLY|O_RDWR|O_CREAT|O_TRUNC|O_APPEND`), `rename,renameat,renameat2,unlink,unlinkat,rmdir,mkdir,mkdirat,link,linkat,symlink,symlinkat,truncate,utimensat,chmod,fchmodat,execve`. Any hit under a resolved git root, or any `execve` beyond the harness's own `env` and `git`, fails the case. Trace log lives under `$WORK/trace/`, outside every manifest root.
- D9 atime is a read, not a write. Do not put `%A@` in the failure criteria; state the exclusion in the claim. Record it as informational only. Mount options unprobed (F7).
- D10 environment isolation (see F5). Required: `env -i` allowlist (`PATH=/usr/bin:/bin`, `LC_ALL=C`, `HOME=$WORK/home`, `XDG_CONFIG_HOME=$WORK/home/.config`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`, `GIT_CEILING_DIRECTORIES=/var/tmp`), stdin from `/dev/null`, stderr to a file (so `isatty(2)` is false, `repo.c:907`). Set `GIT_OPTIONAL_LOCKS` explicitly per arm, never inherited. Run from the repo root (no `prefix`).
- D11 format and version stability. Output is not needed for the write claim itself, only for "the command ran and did its job". EXPERIMENTAL + "behavior may change" means the claim is bound to git 2.55.0 and must be re-run on any upgrade (Q1). Never parse the table.
- D12 manifest definition gaps. Needs: NUL-delimited records, `LC_ALL=C sort -z`, per entry `%y %m %s %T@ %C@ %i %n %l %p`, sha256 of regular files, the full path set (so creations and deletions both show), and roots as in D2–D4. Also include the worktree top level with `.git` pruned, as a "nothing outside `.git` changed" check (cheap, and it is the only outside-`.git` surface this command could touch).

## Case matrix (one fixture, one mktemp root, four subtrees)

| case | shape | roots in manifest | trap | status in claim |
|---|---|---|---|---|
| A normal | `init` repo, 2 commits, loose objects | `$GIT_DIR` | none beyond D5/D7 | in |
| B linked worktree | `worktree add --detach` off A | worktree `.git` file; `$COMMON/worktrees/<id>`; `$COMMON` | `gitdir` mtime may move (F4); `index` in admin dir (S033) | in; report any `gitdir` change explicitly, do not average it away |
| C bare | `init --bare` with the same two commits pushed in | the bare dir itself | D3: no `.git` child | in |
| D `.git` symlink | non-bare repo whose `.git` is a symlink to a dir elsewhere under `$WORK` | `realpath` target | D2: `find` sees only the link | in, only if built; otherwise drop the symlink wording |
| E alternates | `objects/info/alternates` | would need the target | reads another repo's objects, outside the manifest | out; assert absent (`test ! -e`) and fail closed if present |
| F reftable / sha256 | `--ref-format`/`--object-format` | — | different code paths and layouts | out; state it |
| G packed, large | `git gc` in setup | `$GIT_DIR` | pack files and `path_walk` differ from loose | optional; if out, state it |

## Proposed checks for L1 (not run here)

Authoring is L1's; the seat did not build or run. The design below is what the final fixture should do.

1. Harness skeleton (illustrative, not committed):
   ```bash
   WORK="$(mktemp -d /var/tmp/souji-r13-structure.XXXXXX)" || exit 2
   trap 'rc=$?; rm -rf "${WORK:?}"; exit "$rc"' EXIT
   envi=(env -i PATH=/usr/bin:/bin LC_ALL=C HOME="$WORK/home" XDG_CONFIG_HOME="$WORK/home/.config" \
     GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 GIT_CEILING_DIRECTORIES=/var/tmp)
   manifest() { # manifest <real-root>: NUL records, then content hashes
     find -P "$1" -printf '%y %m %s %T@ %C@ %i %n %l %p\0' | LC_ALL=C sort -z
     find -P "$1" -type f -print0 | LC_ALL=C sort -z | xargs -0 -r sha256sum
   }
   # trace: strace -f -o "$WORK/trace/strace.log" -e trace=openat,openat2,rename,renameat,renameat2,unlink,unlinkat,rmdir,mkdir,mkdirat,link,linkat,symlink,symlinkat,truncate,utimensat,chmod,fchmodat,execve -- "${envi[@]}" git -C "$repo" repo structure --format=nul </dev/null >"$WORK/out.bin" 2>"$WORK/err.txt"
   ```
2. Per case, roots from `git -C "$repo" rev-parse --absolute-git-dir --git-common-dir`, each through `realpath`; assert non-empty and that the bare case's root equals the repo dir.
3. Verdict per case: PASS only if (a) structure exit 0 and key names match the pinned 2.55.0 set, (b) quiescence scan clean before and after, (c) `cmp` of before/after manifests equal (with the `gitdir` exception in case B reported, not silently accepted), (d) zero write-mode open, rename/unlink/link, mkdir, utime/chmod, or extra `execve` in the trace under resolved roots, (e) positive control for the same harness reported as a change. Any setup error → exit 2 (could-not-evaluate), never PASS.
4. Q4: `grep -c 'TMPDIR:-/tmp' <fixture>` → 0; `grep -c '/var/tmp' <fixture>` ≥ 1; trap removes `$WORK`.
5. Q9: `shellcheck -S warning <fixture>; echo $?` → 0.
6. Selftest: `bash <fixture> --selftest` must print `selftest=PASS ids=<n>/<n>` and exit 0 with the pinned id list.
7. Post-run host check: `git -C /home/vgpnk/Projects/shokunin status --short` shows no new entries from this run; `git -C /home/vgpnk/Projects/shokunin worktree list` unchanged; `ls -d /var/tmp/souji-r13-structure.* 2>/dev/null` empty.
8. Q1: record `git --version` and host version in the knowledge entry, and re-run on any git upgrade.

## Admissible claim (bounded)

Admissible if and only if the checks above pass on the host:

> On git 2.55.0 (host Linux x86_64; code read at tag v2.55.0), inside one mktemp fixture under `/var/tmp` with an `env -i` allowlist and the harness shown to detect a `git status` index refresh, `git repo structure --format=nul` exited 0 with its pinned key set and changed no file under the resolved git dir / common dir of a normal repo, a linked worktree, a bare repo and (if built) a symlinked `.git`, by path set, type, mode, size, mtime, ctime, inode, link count, symlink target and content hash, with no write-mode open, rename, unlink, link, mkdir, utime/chmod or extra exec observed by `strace -f`. Where a linked worktree's `worktrees/<id>/gitdir` mtime moved, that single metadata touch is reported as the exception.

Not claimed: any other git version (EXPERIMENTAL); reftable or sha256 object formats; alternates; shallow or partial clones; large or packed repositories unless case G is run; concurrent writers; atime; the working tree; the table output; any universal "git repo structure is safe"; and any F2 admission, which also needs S005 and S006 opened with grounding quotes first (both `queued`).

## Limitations and residual risk

- Nothing was executed. Every "will" above is a prediction, marked [INFERENCE] where it rests on source reading or documentation.
- Source reading covered `builtin/repo.c` lines 744–921 at v2.55.0 only. Helper internals (ref backend, `path_walk`, odb reads, reftable) were not read.
- The positive control (D6) and the `gitdir` mtime behaviour (F4) are unobserved.
- strace may miss writes from a process that escapes tracing; the quiescence scan (D7) is the backstop, not a proof.
- Mount options for `/var/tmp` (atime) were not probed.
- One fixture, one git version, one host: the claim is an existence result for that fixture, not a property of git.

## Judged-on summary

- Calibration: the current flip overstates what a `-newer` diff can show; the admissible claim above is scoped to what the checks can actually detect.
- Operability: the harness skeleton, verdict rules, exit codes and post-run checks are written so L1 can build and run them without re-deriving the design.
- Coverage: four shapes in scope, one (symlinked `.git`) conditional on being built, four explicitly out (alternates, reftable/sha256, packed/large unless G, concurrent writers).
