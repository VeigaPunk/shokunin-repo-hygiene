# CensusBoundary — C2 census protected boundary (round 14, w1)

Seat: `SoujiR14.CensusBoundary` (executor, axes calibration/operability).
Scope: `tools/souji-census.sh` and `tests/fixtures/r14-census-boundary.py` only.
No shared bookkeeping, no commits, no live census, no real credential path.

## Files and byte pins

| file | lines | sha256 |
|---|---:|---|
| `tools/souji-census.sh` | 1539 | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` |
| `tests/fixtures/r14-census-boundary.py` | 735 | `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2` |

Pins are from `sha256sum` after the final edit. Earlier intermediate pins
(`baf98373…`, `2cf44ee9…`, `ec79adbc…`, `034a518e…`, `a118225b…`,
`9a6ce8ef…`) are superseded by this final set. The fixture also pins the
known a31642d baseline bytes
`6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`
and prints `TOOL-KIND baseline-a31642d` when `--tool` matches it.

## Exercised evidence vs code inspection

Exercised (static only, no behaviour):

- `bash -n tools/souji-census.sh` → rc 0, `parse-ok`.
- `python3 -c 'compile(open("tests/fixtures/r14-census-boundary.py").read(), …, "exec")'` → `parse-ok`.
- Q4 markers on the fixture: `grep -c 'TMPDIR:-/tmp'` → 0; `grep -c '/var/tmp'` → 6.
- `sha256sum`, `wc -l` above.

Not exercised (parent/L1 gate owns these; lane rule): fixture cases,
baseline `--tool` red run, installed green run, `--selftest`, ShellCheck,
and any live fleet census. No result below is a measured run.

## Implemented behaviour (code inspection)

Ordering: `main` resolves `--root` then `--compare` through
`guard_path` before `command -v git/du`; `emit_census` re-guards the root
and `load_census` guards the compare file before `[ -f ]`, `stat`, or
`< file`. `resolve_guarded` is a component walker, not `readlink -m`:

1. refuses any input containing a `..` component as `ambiguous-path`;
2. folds one path component at a time, refusing as soon as a prefix equals
   or is inside a protected root;
3. reads each symlink one hop with `readlink`, folds the target, and refuses
   a target that reaches the store before stat/open below it;
4. applies the ancestor predicate only to the final input path, so an
   ordinary parent prefix (`/home/vgpnk`) is not refused while walking, but
   `--root $HOME` is;
5. fails closed (`unresolved-path`, `symlink-loop`, exit 2) instead of the
   old `canon_path` fail-open fallback;
6. performs a lexical lookahead of `candidate + remaining suffix` before
   any `lstat` of the input walk, so a path like `.omp` followed by `agent`
   is refused before the parent directory is even statted. Startup still
   stats each home and its `.omp` parent (not the agent store) to seed
   relocation roots;
7. never relies on bash `errexit` for a refusal: every `$(guard_*)`,
   `$(resolve_guarded*)`, `$(gitfile_admin*)`, and
   `$(worktree_extra_flags ...)` capture is written
   `... || exit 2`. The only deliberate non-fatal captures are the two
   seeded-root probes in `build_protected_roots` (`if can=$(...)` /
   `if omp=$(...)`), which skip an unresolvable canonical home root.

Protected set (per L1 decision, text-only first):

- `$HOME/.omp/agent` and the passwd-derived home's `.omp/agent`;
- `PI_CODING_AGENT_DIR` (absolute or home-relative) and
  `<home>/${PI_CONFIG_DIR:-.omp}/agent` as additive relocation roots;
- component pair `.omp/agent` (catches canonical paths behind a symlinked
  home after the lexical store names are seeded);
- operator surfaces: `census/operator-sweep-*`, `.ufo/state`,
  `.ufo/watchdog.log`.

No `readlink`/`stat` of the store is performed while constructing roots;
home canonicalisation happens only after the lexical/component store names
are seeded, inside a subshell that cannot abort the run.

Stable refusal: `souji-census: path-protected: <reason> (<label>: <path>)`
on stderr, exit 2, no census header/stdout. Refusal reasons in code:
`credential-store`, `operator-sweep`, `operator-runtime`,
`ambiguous-path`, `unresolved-path`, `symlink-loop`,
`git-alternates-unparsed`, `git-config-unparsed`,
`git-config-unsupported`, `git-metadata-hardlink`,
`git-metadata-nonregular`, `git-metadata-unavailable`,
`git-metadata-symlink`. Git aliases surface under the `credential-store`
reason with labels such as `git-metadata`, `gitdir`,
`git-common-dir`, `alternates`, `worktree`, `core-worktree`.

Traversal hardening:

- `list_repos` skips symlink children before following, guards child names
  before directory stat, and fills an array (rows are buffered; a failure
  never leaves a partial census).
- `census_one` resolves the repo, then `guard_git_surface` before
  `git rev-parse`/`worktree list`/`rev-list`/`status`.
- `.git` symlinks are not followed as rows; `.git` files are resolved one
  `gitdir:` line; `commondir`, `objects/info/alternates`, and worktree
  registrations (`worktrees/*/gitdir` plus the worktree `.git` pointer) are
  boundary-checked before git.
- Git metadata symlinks may not leave their own gitdir; fixed metadata
  (`config`, `HEAD`, `index`, `packed-refs`, `commondir`, `info/exclude`,
  `objects/info/alternates`) must be regular, single-link files.
- Local config is read with `git config --file … --no-includes`: refuses
  `include`/`includeIf`, `filter.*.clean|smudge|process`,
  `core.hooksPath`, `core.attributesFile`, `core.excludesFile`,
  `core.alternateRefsCommand`, `remote.*.promisor`,
  `extensions.partialClone`, `extensions.worktreeConfig`; validates
  `core.worktree` as a guarded path; rejects `~` indirection. This is an
  operability boundary, not full normal-config support. `core.fsmonitor` is
  overridden with `-c core.fsmonitor=false` on status; status also uses
  `--ignore-submodules=all`, `-c core.hooksPath=/dev/null`,
  `-c core.excludesFile=/dev/null` and `-c core.attributesFile=/dev/null`
  so default XDG ignore/attribute files cannot point into a store.
- Alternates are followed recursively to depth 5; a symlinked alternates
  file or a quoted line is refused as unparsed; worktree registrations are
  read from `worktrees/*/gitdir` and their admin `commondir` is guarded
  before `git worktree list`, not only inside a later swallowed capture.
- All inherited `GIT_*` variables are cleared; global/system config is
  `/dev/null`; optional locks are disabled.
- `scratch_bytes` tests `-L` before `-e`; `find -P` and `du -P` remain
  non-following; `newest_mtime` and `count_dirty` prune/exclude
  `census/operator-sweep-*`.

Honest limits written into the header: the mtime walk never opens contents,
but `git status` may read/hash tracked content; this is not a DLP classifier.

## Fixture cases (`tests/fixtures/r14-census-boundary.py`)

Synthetic `/var/tmp/r14-census-boundary.*`, synthetic HOME, real repo inside
the synthetic store, canary content, store root mode 000 (sessions also 000)
with the `HOME/.omp` parent left traversable (0755). No real `~/.omp` path is
constructed or read. The fixture refuses to run as root so mode 000 remains
meaningful. The alternates case writes the alternate chain and the ref file
directly (no `git update-ref` object validation), and points the second hop
at the store's `objects` directory, so setup never reads the 000 store.

| id | case | baseline (a31642d copy) | installed expectation |
|---|---|---|---|
| R14C2-01 | store root direct | rc 0 header only / store readdir access | rc 2, `path-protected`, empty stdout |
| R14C2-02 | store descendant (`sessions`, 000) | rc 0 header, openat EACCES below store | rc 2, no store syscall |
| R14C2-03 | ancestor `$HOME` | censuses `agent-alias` into store repo | rc 2, `path-protected` |
| R14C2-04 | root symlink + `alias/..` | follows alias into store (or dotdot root) | rc 2 both, no store syscall |
| R14C2-05 | `--compare` direct + alias + `/proc/self/fd` | store 000 blocks the read (EACCES) or a readable copy yields diff rc 3; no finding | rc 2 all three, empty stdout |
| R14C2-06 | `.git` gitfile / `.git` symlink / commondir | include-root runs git into store or exits 0 without refusal | rc 2 all three |
| R14C2-07 | safe normal repo | PASS (green control) | rc 0, clean row |
| R14C2-08 | `.scratch` symlink to store | PASS (green control; `-L` short-circuits) | rc 0, scratch_bytes 0 |
| R14C2-09 | poisoned `GIT_*` env + poisoned HOME | git gets store `GIT_COMMON_DIR`/worktree; spy env shows store | rc 0, clean row, no store path |
| R14C2-10 | linked-worktree admin commondir into store | include-root `git worktree list`/status reads store | rc 2, no git into store |
| R14C2-11 | two-hop alternates into store | does not refuse the alternates chain; store object read only via alternate | rc 2, empty stdout |
| R14C2-12 | fleet child symlink into store | follows child symlink, emits store access | rc 0, normal row, no access |

Access oracle: PATH spies for
`find/du/git/cat/head/tail/readlink/stat/realpath` log cwd, argv and
selected `GIT_*` values; `strace -f -y -e
trace=%file,getdents64,execve` is authoritative (positive control: a
mode-000 store read must show `EACCES`, else exit 2). The initial execve is
ignored because its argv is the user-supplied path; readlink is judged by
its path argument, not by the printed target, so an alias outside the store
whose target is the store is not treated as a read. Refusal checks use a
strict oracle: EACCES, a readlink whose path argument is the store or below
it, an open/getdents/exec naming
the store, or any stat naming the store (including the bare root). For
refusals, absolute path arguments of open/getdents lines are also resolved
with `realpath` after the run, so a symlinked fleet child that opens the
store is visible even when strace prints only the fleet path. Positive
checks use the lenient oracle that exempts a bare store-root stat, keeping
the legacy scratch-symlink control green where baseline `-e` stats the root.
Refusal cases require `contract:` rc 2, the stable finding, empty stdout,
and no canary, plus no `access:` line. Positive cases require a clean
7-column row and no `access:` line. Fixture cleanup is a `finally`
`shutil.rmtree` after restoring modes.

## Baseline discrimination (expected, not run here)

`git show a31642d:tools/souji-census.sh > /var/tmp/r14-census-baseline.sh`
then `--tool` that path must yield aggregate exit 1 with R14C2-01..06,
R14C2-09, R14C2-10, R14C2-11 and R14C2-12 FAIL for the listed reasons
(absence of rc 2/finding, or observed store access), and R14C2-07/08 PASS.
Installed must yield exit 0 with all twelve PASS. Red is asserted in two
parts: `access:` evidence (required on every baseline red case by the
fixture) and the guarded `contract:` exit/finding, so a marker-only
mismatch cannot pass. The fixture prints `TOOL-KIND baseline-a31642d` when
the supplied bytes match the pinned baseline digest.

## Reviewer deltas (static re-reviews, not run here)

- BoundaryReviewRoot/Compare/Git/Scratch: root/compare ordering, empty
  `--compare`, resolved-path reads, nlink refusal, row validation, stderr
  usage, temp cleanup, worktree guards, `.git`/commondir/alternates, and
  `GIT_*`/config scrubbing are reflected above.
- BoundaryReviewScratch F1 (tracked secret-shaped content may be hashed by
  `git status`) is **disclosed, not excluded**, per the L1 decision to
  avoid new general credential-class protection this round. No new
  `scratch-symlink` flag was added: a symlinked `.scratch` still reports 0
  bytes and keeps the legacy verdict interface; R14C2-08 therefore expects
  the legacy silence. Operator-sweep pruning is likewise invisible in
  `verdict_flags`.
- BoundaryReviewCompare residuals kept as legacy scope: named FIFO/`-`
  compare paths yield exit 2 "not found" without hanging; columns 6-7 are
  text; repeated `--root`/`--compare` are last-wins; `--selftest` still
  ignores `--compare`. None of these touch credential access.

## L1 final commands

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin
sha256sum tools/souji-census.sh tests/fixtures/r14-census-boundary.py
python3 -B tests/fixtures/r14-census-boundary.py
# expect SUMMARY total=12 failed=0, exit 0

git show a31642d:tools/souji-census.sh > /var/tmp/r14-census-baseline.sh
python3 -B tests/fixtures/r14-census-boundary.py --tool /var/tmp/r14-census-baseline.sh
# expect SUMMARY total=12 failed=10, exit 1; R14C2-07/08 PASS
rm -f /var/tmp/r14-census-baseline.sh

TMPDIR=/var/tmp bash tools/souji-census.sh --selftest
shellcheck -S warning tools/souji-census.sh
```

The fixture itself removes its `/var/tmp/r14-census-boundary.*` tree. No
live census is required for C2 and none was run. The embedded legacy
selftest still contains its dirty, repeated-census, `--compare` identical/
mutated/malformed, and linked-worktree controls; this fixture adds the
safe-normal/scratch/env positives. No universal "all existing behaviour is
preserved" claim is made: the exact newly refused local configs are
include/includeIf, filter.*.clean|smudge|process, core.hooksPath,
core.attributesFile, core.excludesFile, core.alternateRefsCommand,
remote.*.promisor, extensions.partialClone and extensions.worktreeConfig,
plus core.worktree paths that reach the store and symlinked/unparsed
alternates.

## Risks, residuals, nonclaims

- Boundary is name/root based (`~/.omp/agent` plus operator surfaces); it is
  not a general DLP classifier and does not protect every secret-shaped file
  class. Per L1, general credential-name expansion was not added this round.
- Hardlinked aliases are refused for `--compare` and fixed git metadata
  (`nlink > 1`), but hardlinked object files and arbitrary hardlinks into a
  store are not detectable without stat'ing the store. Stated as residual.
- Guard and later access are not atomic; a concurrent symlink/path swap is
  outside the proof.
- Unsupported local configs (LFS `filter.*`, includes, hooks path, alternate
  refs command, promisor/partial clone, worktreeConfig) refuse the whole
  census with exit 2. This is fail-closed operability debt, not normal-config
  support.
- `git status` may read/hash tracked content; the header discloses this.
  Submodule content is not inspected (`--ignore-submodules=all`).
- A relocated store is covered by resolving the `.omp` parent and adding
  `<resolved>/.omp/agent`; startup performs a stat/readlink of each home's
  `.omp` parent (not the agent store) to seed that root. A `~/.omp/agent`
  that is itself a symlink is left as a residual because resolving it would
  touch the store. A `PI_CODING_AGENT_DIR` pointing at `$HOME` deliberately
  over-refuses all HOME-internal roots (fail closed).
- Work-tree content symlinks (for example a tracked `.gitignore` symlink)
  are not boundary-guarded; git's own handling is relied on and is stated as
  an inference, not exercised. `guard_git_links` refuses an unreadable
  subdirectory inside a gitdir rather than failing open on `find` errors.
- Global/system git config is disabled; global excludes/identity no longer
  affect counts. `--root`/`--compare` containing `..` are refused (legacy
  relative-parent invocations no longer supported).
- `git worktree list` is still the discovery call; registrations are guarded
  first, but a race or a non-registration path is not proven.
- No tools were installed or upgraded. The only real `~/.omp/agent` read was
  the contract-permitted `RULES.md`; no store content, listing, hash, or
  query was performed. No operator sweep, live census, GUI, or live removal
  was accessed. S038 was not applicable (no vendor timeout docs opened for
  C2); S039 was not used (own-work evidence after L1 only).
