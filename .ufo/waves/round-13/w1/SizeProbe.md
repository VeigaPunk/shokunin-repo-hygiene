# SizeProbe — r13 w1: F2 structure probe and write-safety fixture

Seat: `SoujiR13.SizeProbe` (executor, leaf). Axes: calibration, operability,
coverage. Certification remains OFF; this is in-wave authored evidence, not an
independent non-author verification, and no commit was made.

**Status: authored only — neither tool was executed by this seat.** Expected
metric values and the detector deltas below are design targets derived from
the installed command and git v2.55.0 source, not observed output. Values that
I did observe are marked *fact*; everything derived without execution is
marked *inference*.

## Write set

| path | state |
|---|---|
| `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh` | new, executable |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-repo-structure.sh` | new, executable |
| `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-13/w1/SizeProbe.md` | this report |

No other file was written; `census/operator-sweep-20261019/`, the fleet repo,
sibling repos, shared bookkeeping and the concurrently authored
`corpus/knowledge/git-repo-structure-readonly.md` were not touched. *Fact*:
`git -C ... status --porcelain` shows these two files as `??`; the lane
baseline at start was `31984f4` with `.ufo/` and the operator sweep untracked.

## Observed evidence (facts)

| source | exact observation |
|---|---|
| `git --version` | `git version 2.55.0` |
| `git-repo.1.gz` roff line 10 | `.TH "GIT-REPO" "1" "2026-06-29" "Git 2.55.0" "Git Manual"` |
| `git-repo.1.gz` roff line 44 | `THIS COMMAND IS EXPERIMENTAL\&. THE BEHAVIOR MAY CHANGE\&.` |
| `git-repo.1.gz` roff line 166 | `This format may change and is not intended for machine parsing\&.` (the `table` default) |
| `git.1.gz` roff lines 2195–2200 | `GIT_OPTIONAL_LOCKS`: "If this Boolean environment variable is set to false, Git will complete any requested operation without performing any optional sub-operations that require taking a lock. For example, this will prevent git status from refreshing the index as a side effect." |
| `git.1.gz` roff line 2122 | `GIT_NO_LAZY_FETCH`: "tells Git not to lazily fetch missing objects from the promisor remote on demand" |
| upstream git v2.55.0 `builtin/repo.c` | `structure_keyvalue_print` at :633–685 is the `lines`/`nul` path (:918); keys at :636 (`references.branches.count`), :645 (`objects.commits.count`), :656/:658 (tree/blob inflated size), :667 (blob disk size), :672–683 (`max_size` + `_oid`, `max_parents`, `max_entries`); the walk is seeded with `add_pending_oid` per reference at :722; structure command at :877–925 |
| upstream git v2.55.0 `setup.c` | `handle_extension_v0` accepts `extensions.partialclone` even in v0-format repositories (:623–631) |
| `corpus/lessons/round-12.md:133` | F2 rejected/deferred; flip required "a /var/tmp fixture diffing `find .git -newer` around a `GIT_OPTIONAL_LOCKS=0 git repo structure` run" |
| `PROVINCE.md` F2 row (current worktree) | "bounded structure probe and isolated write-safety fixture acquired r13; whole-workspace size attribution and unreachable-object census remain frontier" |

Source file line numbers above are from `https://raw.githubusercontent.com/git/git/v2.55.0/...`
read this session; the installed manual is `/usr/share/man/man1/git-repo.1.gz`
and `git.1.gz`.

## Ground truth relayed by L1 from AttackCoverage (not re-run here)

- A `partialClone` `tree:0` repository lazily fetched three times and grew
  `.git` from 28 to 40 files with incomplete statistics, even with optional
  locks off and `maintenance.auto=false`.
- `git repo structure` can exit 0 while skipping missing objects; exit 0 is
  not a completeness proof.
- The structure walk is seeded from references; detached-HEAD tips outside
  the ref namespace are not counted. Linked worktrees share the common object
  store.

The tools below encode those as refusals/scoping, not as a claim that
`GIT_OPTIONAL_LOCKS=0` alone is write-safe.

## Probe behavior — `tools/souji-repo-structure.sh`

- CLI: `--repo PATH` (work-tree root or subdirectory; bare resolution is
  incidental and not covered by the fixture), `--help`; no other modes.
- Every git call is `git -c maintenance.auto=false -c
  maintenance.autoDetach=false -C PATH ...`; environment is
  `LC_ALL=C GIT_OPTIONAL_LOCKS=0 GIT_NO_LAZY_FETCH=1
  GIT_TERMINAL_PROMPT=0`, with `GIT_DIR/GIT_WORK_TREE/GIT_COMMON_DIR/
  GIT_INDEX_FILE/GIT_OBJECT_DIRECTORY/GIT_ALTERNATE_OBJECT_DIRECTORIES`
  unset. No fetch, no maintenance, no index operation, no `cd`.
- Refusal before the walk (exit 2): repo-local `extensions.partialClone`
  present, or any effective `remote.*.promisor=true` (normalized with
  `git config --type=bool --get-regexp`). Errors:
  `probe.error=partial-clone-unsupported` /
  `probe.error=promisor-remote-unsupported`.
- Capability detection: `git -C PATH repo structure -h` text (LC_ALL=C) must
  name `repo structure` and `lines`; otherwise exit 3
  (`probe.status=unsupported`). The volatile `table` format is never parsed
  and there is no fallback. *Inference*: parse-options prints the usage line
  for `-h` and exits nonzero; only the text is used.
- Capture: one `mktemp -d /var/tmp/souji-repo-structure.XXXXXX`, removed by an
  EXIT trap. `git repo structure --format=lines` stdout/stderr go to files
  there; numeric stdout is emitted only if rc=0 AND stderr is empty AND
  `objects.commits.count=` is present. Nonzero, any stderr, or unexpected
  output exits 4 with `probe.status=could-not-evaluate` and
  `probe.error=structure-failed|structure-stderr|unexpected-structure-output`;
  up to 20 captured stderr lines are echoed as `probe.stderr=` diagnostics and
  no numeric line reaches stdout. This follows the relayed false-success
  ground truth.
- Output (LC_ALL=C, `key=value`): `probe.tool`, `probe.status=ok`,
  `probe.git_version`, `probe.command` (exact structure argv, repo path
  `%q`-quoted), optional `probe.repo_root`, `probe.git_dir`,
  `probe.git_common_dir`, `probe.bare`, `probe.scope=refs-rooted-reachable`,
  `probe.git_optional_locks=0`, `probe.maintenance_auto=false`,
  `probe.format=lines`, then the command's 28 keys verbatim. `probe.*` cannot
  collide with `references.*`/`objects.*`.
- Exit map: 0 ok; 2 usage/git missing/unusable repo/refused promisor-partial;
  3 no `repo structure --format=lines`; 4 could-not-evaluate (config
  unreadable, structure nonzero/stderr, no known metric).

## Fixture behavior — `tests/fixtures/r13-repo-structure.sh`

- CLI: `--selftest [--probe PATH]`. `--probe` is optional: without it the
  fixture exercises the raw installed baseline command (the r12 deferred
  capability) and pins **4** ids (`selftest=PASS ids=4/4`); with `--probe` it
  runs the candidate tool (`[P|bash P] --repo <repo>`) and pins **5** ids
  (`ids=5/5`). The fixture does not embed or copy the probe implementation.
- Isolation (Q4): hard-coded `mktemp -d
  /var/tmp/souji-r13-repo-structure.XXXXXX`; no `${TMPDIR:-/tmp}` literal;
  trap `rm -rf`; `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`,
  `HOME` under `WORK`; inherited `GIT_*` unset; no network.
- Measured invocation is wrapped in `env -i` with an explicit allowlist:
  `PATH`, `HOME`, `LC_ALL=C`, `GIT_OPTIONAL_LOCKS=0`,
  `GIT_NO_LAZY_FETCH=1`, `GIT_TERMINAL_PROMPT=0`, `GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1`, bounded by `timeout 120`. Every setup call
  (init/add/commit/rev-parse) uses `-c maintenance.auto=false
  -c maintenance.autoDetach=false`.
- Manifest (lines 205–219): `*.content` is sorted `sha256sum` of every regular
  file under the resolved absolute git dir (path set + bytes); `*.meta` is
  sorted `%y %m %s %T@ %p %l` for every path (type, mode, size, mtime,
  symlink target; directories included). atime and ctime are never recorded.
- Positive detector control (lines 322–359, before the measured run): append
  to `.git/description` → content and meta must both differ; restore with
  `cp -p` → both must equal the baseline; `touch -d 2001-02-03T04:05:06` →
  content must be equal while meta differs; restore → equal again. A detector
  that misses any delta fails the write-free verdict.
- Cases: `SOUJI-R13-STRUCT-manifest-control`, `-write-free` (rc=0, empty
  stderr, before/after content+meta equal, non-vacuous markers
  index/HEAD/config/refs/heads/master/logs/HEAD, control passed),
  `-object-metrics` (exact refs/object counts, `blobs.inflated_size` = known
  file bytes, `max_size_oid` = HEAD/root tree/blob, `max_parents=0`,
  `max_entries=1`, `blobs.disk_size>0`, zero tag oid; in probe mode also
  `probe.status=ok`, `probe.scope=refs-rooted-reachable`, version equality,
  guard fields, format and command), `-bogus-repo` (plain dir and missing
  path reject nonzero, rc=2 in probe mode, no structure key, unchanged dir),
  and probe-only `-promisor-refusal` (config-marked promisor repo and
  config-marked `extensions.partialClone` repo exit 2 with matching
  `probe.error`, emit no structure key, manifests unchanged; remote URL is
  `example.invalid` and is never contacted). Any measured stderr fails both
  the write-free and metrics verdicts.

## Proposed exact checks for L1 (I did not run any of these)

```bash
shellcheck -S warning \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh \
  /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-repo-structure.sh

# baseline capability + metrics (4 ids)
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-repo-structure.sh --selftest

# lane probe end to end (5 ids, adds promisor/partial refusal)
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r13-repo-structure.sh \
  --selftest --probe /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh

# direct probe on a throwaway repo; expect rc 0, probe.status=ok,
# probe.scope=refs-rooted-reachable, references.branches.count=1
d=$(mktemp -d /var/tmp/souji-r13-manual.XXXXXX)
git -C "$d" init -q -b master
printf 'probe manual check\n' >"$d/f.txt"
git -C "$d" -c user.name=check -c user.email=check@example.invalid \
  -c maintenance.auto=false add -- f.txt
git -C "$d" -c user.name=check -c user.email=check@example.invalid \
  -c maintenance.auto=false commit -qm check
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh --repo "$d"
# expect exit 2:
bash /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-repo-structure.sh \
  --repo /var/tmp/souji-r13-absent
rm -rf "$d"
```

Expected: baseline final line `selftest=PASS ids=4/4`; probe final line
`selftest=PASS ids=5/5`; direct probe rc 0 with 28 structure keys where
`references.branches.count=1`, `objects.commits.count=1`,
`objects.trees.count=1`, `objects.blobs.count=1`, `objects.tags.count=0`,
`objects.blobs.inflated_size=19` (content `probe manual check\n`); invalid
repo rc 2 with `probe.error=repo-missing`. These expected counts are
*inference* from `builtin/repo.c`; the fixture's first run establishes the
observed baseline.

## Risks, limits and residual checks

1. **Unobserved expectations.** I did not execute either artifact. If any
   assertion in the fixture is wrong on the installed git, the verdict is
   FAIL, not a silent pass; re-baselining must amend the header/expected
   values with the observed run, never weaken the checks.
2. **Experimental format.** The 28-key `lines` schema and the all-zero tag oid
   are pinned to git 2.55.0 behavior. A future git change intentionally fails
   the fixture; the probe never falls back to the table and fails closed on
   unknown output shape.
3. **Write-safety bound.** One fresh SHA-1, loose-object, single-commit,
   normal repository; no packs, remotes, tags, linked worktrees, bare repos,
   alternates, submodules, concurrent writers, ownership/xattr/ACL changes.
   Transient writes that restore their own effect are not excluded; atime and
   ctime are excluded. The claim is "no persistent delta in the compared
   path/content/stat fields for this run", not universal absence of writes.
4. **Promisor refusal is config-marker based.** It refuses repo-local
   `extensions.partialClone` and effective `remote.*.promisor=true`, but the
   fixture does not construct a real promisor object store or contact a
   remote (deliberately no network). A repo with a promisor remote declared
   through a mechanism outside these config keys is not refused; residual
   risk reported, not claimed closed.
5. **Capability check is inferred.** `-h` text matching is a fail-closed
   heuristic; an exotic git build with different help text exits 3
   (could-not-evaluate) rather than mis-parsing output.
6. **Recheck pairing.** The concurrently authored knowledge entry currently
   records `recheck: bash tests/fixtures/r13-repo-structure.sh --selftest`,
   which exercises the raw baseline capability, not the probe's refusal/stderr
   logic. To cover the entry's probe claims, L1 should also run the
   `--probe` invocation above (or have that entry's owner pair it). I did not
   edit the entry.
7. **No deletion authority.** Reachable-object and disk-size metrics are not
   filesystem space recoverable and are not a receipt; the probe and fixture
   authorize no removal, gc/repack/prune, or history rewrite.
8. **Q8 scope.** Q8 (per-target staging/digest bounds) applies to
   `tools/souji-quarantine.sh`, not this probe; the fixture's only bound is
   `timeout 120` around the measured command.

No blockers. Installation/upgrade: none performed.
