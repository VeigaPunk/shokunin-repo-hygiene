#!/usr/bin/env bash
# r13-repo-structure.sh — F2 size-census write-safety fixture (round 13).
#
# STATUS: authored, NOT EXECUTED by this seat (round contract: seats author
# runnable artifacts; the integrator runs them). Expected values below are the
# design target grounded in the installed command and git v2.55.0 source, not
# an observed PASS.
#
# CLAIM UNDER TEST (bounded): in one isolated normal (non-bare, non-linked)
# /var/tmp repository, ONE invocation of `git repo structure --format=lines`
# (or of the lane probe that runs it) produces exit 0 with EMPTY stderr plus
# the structure metrics, and leaves NO PERSISTENT delta in the compared .git
# path set, file bytes, types, modes, sizes or mtimes. Transient writes that
# restore their own effect are not excluded; atime and ctime are excluded by
# design. This authorizes no deletion.
#
# GROUND TRUTH reported by AttackCoverage this wave (not re-run here):
# `git repo structure` can exit 0 while skipping missing objects, and its
# walk is seeded from references, not detached-HEAD tips; on a partialClone
# tree:0 repo it lazily fetched three times and grew .git 28 -> 40 files with
# incomplete stats. The fixture therefore treats nonzero exit OR any stderr
# as could-not-evaluate, and the probe refuses promisor/partial-clone config
# before the walk. Metrics are refs-rooted reachable only; they are not a
# completeness proof.
#
# METHOD
#   1. git init (--object-format=sha1), commit one known file.
#   2. Capture HEAD/tree/blob oids and `git --version`.
#   3. Manifest A: every path under the resolved absolute git dir, as
#        - content: sorted sha256 of every regular file (names + bytes), and
#        - meta:    sorted type/mode/size/mtime/path[/link-target] for every
#                   path, directories and symlinks included.
#      atime is never recorded.
#   4. POSITIVE DETECTOR CONTROL (runs before the measured probe):
#        a. append a byte to .git/description -> content AND meta must differ;
#           restore with `cp -p` from a saved copy -> both must equal A.
#        b. `touch -d` that file -> content must equal A but meta must differ;
#           restore -> both must equal A.
#      A detector that cannot see these deltas makes the write-free verdict
#      FAIL. ctime changes from the control are expected and not compared.
#   5. Manifest BEFORE, run structure ONCE under an `env -i` allowlist,
#      manifest AFTER -> compare.
#   6. Parse the structure output and assert the real metrics of the commit.
#   7. Rejected-repository control: a plain non-repo directory and a missing
#      path must both exit nonzero (exit 2 in --probe mode), emit no structure
#      key on stdout, and leave the plain directory unchanged.
#
# BASELINE vs --probe
#   no --probe : runs the raw baseline command
#                `git -c maintenance.auto=false -c maintenance.autoDetach=false
#                 -C <repo> repo structure --format=lines`
#                i.e. exercises the installed capability that r12 deferred.
#   --probe P  : runs `[P|bash P] --repo <repo>`; the fixture never copies,
#                embeds or re-implements the probe, it only parses output.
#
# ENVIRONMENT (measured run, and every git call in this fixture)
#   Measured invocation is wrapped in `env -i` with an explicit allowlist:
#   PATH, HOME (under WORK), LC_ALL=C, GIT_OPTIONAL_LOCKS=0,
#   GIT_NO_LAZY_FETCH=1, GIT_TERMINAL_PROMPT=0, GIT_CONFIG_GLOBAL=/dev/null,
#   GIT_CONFIG_NOSYSTEM=1. Inherited GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE/
#   GIT_OBJECT_DIRECTORY/alternates therefore cannot leak in. Every setup git
#   call (init/add/commit/rev-parse) uses -c maintenance.auto=false and
#   -c maintenance.autoDetach=false; no fetch, no maintenance.
#
# GATE INTERFACE (PROTOCOL Gate standard)
#   0 = pass: every pinned case id emitted, every verdict PASS
#   1 = fail: a verdict FAIL or id-set mismatch
#   2 = could-not-evaluate: git/timeout missing, mktemp failure, or an
#       unguarded setup command failed (ERR trap)
#   final line: `selftest=PASS ids=4/4` (baseline mode) or
#   `selftest=PASS ids=5/5` (--probe mode), or
#   `selftest=FAIL ids=<got>/<want> missing=[...] extra=[...] failed_verdicts=<n>`
#   The promisor-refusal case exists only in --probe mode: baseline mode has
#   no refusal logic and must never run the raw command against a promisor
#   repository (that is the hazard under test).
#
# CASES (pinned ids)
#   SOUJI-R13-STRUCT-manifest-control detector sees content, stat and
#                                    mtime-only deltas; restores are observed
#   SOUJI-R13-STRUCT-write-free      rc=0, stderr empty, before/after
#                                    manifests equal, manifest non-vacuous
#                                    (index/HEAD/config/refs/heads/master/
#                                    logs/HEAD present), detector control
#                                    passed
#   SOUJI-R13-STRUCT-object-metrics  clean evaluation and, on stdout:
#                                    references.branches.count=1,
#                                    objects.{commits,trees,blobs}.count=1,
#                                    tags=0, blobs.inflated_size=<file bytes>,
#                                    max_size oids == HEAD/tree/blob,
#                                    commits.max_parents=0, trees.max_entries=1,
#                                    blobs.disk_size>0, tags.max_size_oid
#                                    all-zero (SHA-1); in --probe mode also
#                                    probe.status=ok,
#                                    probe.scope=refs-rooted-reachable,
#                                    probe.git_version==`git --version`,
#                                    probe.git_optional_locks=0,
#                                    probe.maintenance_auto=false,
#                                    probe.format=lines,
#                                    command contains
#                                    `repo structure --format=lines`
#   SOUJI-R13-STRUCT-bogus-repo      plain directory and missing path rejected
#   SOUJI-R13-STRUCT-promisor-refusal (--probe only) config-marked promisor and
#                                    partialClone repos exit 2 with the matching
#                                    probe.error, emit no structure key, and
#                                    are unchanged; no network is contacted
#
# HERMETIC: hard-coded mktemp -d /var/tmp/souji-r13-repo-structure.XXXXXX
# (TMPDIR ignored; no tmpfs fallback), trap cleanup, no network, no
# live repository touched. The measured command is bounded by `timeout 120`.
#
# LIMITS: one fresh SHA-1, loose-object, single-commit, normal repository. The
# fixture does not exercise packs, tags, remotes, linked worktrees, bare
# repos, alternates, real promisor fetches, submodules or concurrent writers,
# and makes no claim about them; the promisor/partial case only proves that
# marked configuration is refused before the walk. The result is an observed
# no-persistent-delta for this run and host, not universal write-safety.
set -euo pipefail
shopt -s inherit_errexit

usage() { printf 'usage: %s --selftest [--probe PATH]\n' "$0" >&2; exit 2; }
die2() { printf 'id=SOUJI-R13-STRUCT-SETUP error=%s\n' "$*" >&2; exit 2; }

selftest=0
PROBE=""
PROBE_SET=0
while (($#)); do
  case "$1" in
    --selftest)
      selftest=1
      shift
      ;;
    --probe)
      (($# >= 2)) || usage
      PROBE=$2
      PROBE_SET=1
      shift 2
      ;;
    --probe=*)
      PROBE=${1#*=}
      PROBE_SET=1
      shift
      ;;
    *)
      usage
      ;;
  esac
done
((selftest)) || usage
if ((PROBE_SET)); then
  [[ -n $PROBE ]] || die2 "empty --probe"
  [[ -f $PROBE ]] || die2 "probe not found: $PROBE"
fi

command -v git >/dev/null 2>&1 || die2 "git not found"
command -v timeout >/dev/null 2>&1 || die2 "timeout not found"

GIT_VERSION="$(git --version)"

WORK="$(mktemp -d /var/tmp/souji-r13-repo-structure.XXXXXX)" ||
  die2 "mktemp failed under /var/tmp"
rc=0
trap 'rc=$?; rm -rf "${WORK:?}"; exit "$rc"' EXIT
trap 'rc=$?; printf "id=SOUJI-R13-STRUCT-SETUP error=unexpected-failure rc=%s\n" "$rc" >&2; exit 2' ERR

export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0
export GIT_OPTIONAL_LOCKS=0
export GIT_NO_LAZY_FETCH=1
export LC_ALL=C
export HOME="$WORK/home"
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE \
  GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
mkdir -p "$HOME"

GIT_GUARDS=(
  git
  -c user.name=r13-structure
  -c user.email=structure@example.invalid
  -c init.defaultBranch=master
  -c commit.gpgsign=false
  -c maintenance.auto=false
  -c maintenance.autoDetach=false
)
g() { # g <repo> <git args...>
  local repo=$1
  shift
  "${GIT_GUARDS[@]}" -C "$repo" "$@"
}

# Allowlist for the measured invocation: no inherited Git_* can leak in.
ENV_ALLOW=(
  env -i
  "PATH=$PATH"
  "HOME=$HOME"
  "LC_ALL=C"
  "GIT_OPTIONAL_LOCKS=0"
  "GIT_NO_LAZY_FETCH=1"
  "GIT_TERMINAL_PROMPT=0"
  "GIT_CONFIG_GLOBAL=/dev/null"
  "GIT_CONFIG_NOSYSTEM=1"
)

# ---------------------------------------------------------------- manifests
manifest_all() { # manifest_all <dir> <tag>; writes <tag>.content and <tag>.meta
  local dir=$1 tag=$2
  : >"$tag.content"
  find "$dir" -type f -print0 |
    LC_ALL=C sort -z |
    xargs -0 -r sha256sum -- >>"$tag.content"
  find "$dir" -printf '%y\t%m\t%s\t%T@\t%p\t%l\n' |
    LC_ALL=C sort >"$tag.meta"
}

count_lines() { # count_lines <file>
  local n=0 line
  while IFS= read -r line; do n=$((n + 1)); done <"$1"
  printf '%s\n' "$n"
}

# ---------------------------------------------------------------- structure
run_structure() { # run_structure <repo> <out> <err>; echoes rc
  local repo=$1 out=$2 err=$3 rc=0
  if [[ -n $PROBE ]]; then
    local -a cmd=()
    if [[ -x $PROBE ]]; then cmd=("$PROBE"); else cmd=(bash "$PROBE"); fi
    if "${ENV_ALLOW[@]}" timeout 120 "${cmd[@]}" --repo "$repo" >"$out" 2>"$err"; then
      rc=0
    else
      rc=$?
    fi
  else
    if "${ENV_ALLOW[@]}" timeout 120 git \
      -c maintenance.auto=false -c maintenance.autoDetach=false \
      -C "$repo" repo structure --format=lines >"$out" 2>"$err"; then
      rc=0
    else
      rc=$?
    fi
  fi
  printf '%s\n' "$rc"
}

declare -A M=()
parse_metrics() { # parse_metrics <file>; fills M
  local line key value
  M=()
  while IFS= read -r line; do
    case "$line" in
      *=*)
        key=${line%%=*}
        value=${line#*=}
        M["$key"]=$value
        ;;
      *) : ;;
    esac
  done <"$1"
}

CHECKS=0
FAILS=()
check_eq() { # check_eq <key> <expected>
  local key=$1 expected=$2 actual
  actual=${M[$key]-}
  CHECKS=$((CHECKS + 1))
  if [[ $actual == "$expected" ]]; then return 0; fi
  FAILS+=("$key=$actual want=$expected")
}
check_nonempty() { # check_nonempty <key>
  local key=$1
  CHECKS=$((CHECKS + 1))
  if [[ -n ${M[$key]-} ]]; then return 0; fi
  FAILS+=("$key=empty")
}
check_contains() { # check_contains <key> <literal>
  local key=$1 needle=$2 actual
  actual=${M[$key]-}
  CHECKS=$((CHECKS + 1))
  if [[ $actual == *"$needle"* ]]; then return 0; fi
  FAILS+=("$key lacks '$needle'")
}

# ---------------------------------------------------------------- fixture repo
REPO="$WORK/repo"
mkdir "$REPO"
g "$REPO" init -q --object-format=sha1 .
CONTENT='r13 repo structure payload'
printf '%s\n' "$CONTENT" >"$REPO/payload.txt"
EXPECTED_BLOB_BYTES=$((${#CONTENT} + 1))
g "$REPO" add -- payload.txt
g "$REPO" commit -qm 'r13 fixture commit'
HEAD_OID="$(g "$REPO" rev-parse HEAD)"
TREE_OID="$(g "$REPO" rev-parse 'HEAD^{tree}')"
BLOB_OID="$(g "$REPO" rev-parse 'HEAD:payload.txt')"
ZERO40="$(printf '%040d' 0)"

GITDIR_ABS="$(g "$REPO" rev-parse --path-format=absolute --absolute-git-dir)"
case "$GITDIR_ABS" in
  /?*) : ;;
  *) die2 "git dir not absolute: $GITDIR_ABS" ;;
esac

EMITTED_IDS=()
FAILED=0
emit() { # emit <id> <case> <fields...>
  local id=$1 case_name=$2
  shift 2
  EMITTED_IDS+=("$id")
  printf 'id=%s case=%s %s\n' "$id" "$case_name" "$*"
}

printf 'git_version=%s\n' "$GIT_VERSION"
if ((PROBE_SET)); then
  printf 'probe_mode=tool:%s\n' "$PROBE"
else
  printf 'probe_mode=baseline\n'
fi
printf 'fixture_repo=%s\n' "$REPO"
printf 'fixture_git_dir=%q\n' "$GITDIR_ABS"

# ---------------------------------------------------------------- control
MAN_A="$WORK/man-a"
manifest_all "$GITDIR_ABS" "$MAN_A"

CONTROL=()
cp -p "$GITDIR_ABS/description" "$WORK/description.orig" ||
  die2 "control backup failed"

printf 'r13-detector-control\n' >>"$GITDIR_ABS/description"
manifest_all "$GITDIR_ABS" "$WORK/man-ctrl-content"
if cmp -s "$WORK/man-ctrl-content.content" "$MAN_A.content"; then
  CONTROL+=("content-delta-not-detected")
fi
if cmp -s "$WORK/man-ctrl-content.meta" "$MAN_A.meta"; then
  CONTROL+=("stat-delta-not-detected")
fi
cp -p "$WORK/description.orig" "$GITDIR_ABS/description"
manifest_all "$GITDIR_ABS" "$WORK/man-ctrl-restore"
if ! cmp -s "$WORK/man-ctrl-restore.content" "$MAN_A.content" ||
  ! cmp -s "$WORK/man-ctrl-restore.meta" "$MAN_A.meta"; then
  CONTROL+=("content-restore-not-observed")
fi

touch -d '2001-02-03 04:05:06' "$GITDIR_ABS/description"
manifest_all "$GITDIR_ABS" "$WORK/man-ctrl-mtime"
if ! cmp -s "$WORK/man-ctrl-mtime.content" "$MAN_A.content"; then
  CONTROL+=("metadata-control-changed-content")
fi
if cmp -s "$WORK/man-ctrl-mtime.meta" "$MAN_A.meta"; then
  CONTROL+=("mtime-delta-not-detected")
fi
cp -p "$WORK/description.orig" "$GITDIR_ABS/description"
manifest_all "$GITDIR_ABS" "$WORK/man-ctrl-final"
if ! cmp -s "$WORK/man-ctrl-final.content" "$MAN_A.content" ||
  ! cmp -s "$WORK/man-ctrl-final.meta" "$MAN_A.meta"; then
  CONTROL+=("metadata-restore-not-observed")
fi

CTRL_OK=1
if ((${#CONTROL[@]} != 0)); then
  CTRL_OK=0
  FAILED=1
fi
control_detail=""
for reason in "${CONTROL[@]}"; do
  control_detail+="${control_detail:+;} $reason"
done
if ((CTRL_OK)); then
  emit SOUJI-R13-STRUCT-manifest-control manifest-control \
    "content_delta=seen stat_delta=seen mtime_delta=seen restore=equal verdict=PASS"
else
  emit SOUJI-R13-STRUCT-manifest-control manifest-control \
    "verdict=FAIL detail=$control_detail"
fi

# ---------------------------------------------------------------- measured run
MAN_BEFORE="$WORK/man-before"
MAN_AFTER="$WORK/man-after"
OUT="$WORK/structure.out"
ERR="$WORK/structure.err"

manifest_all "$GITDIR_ABS" "$MAN_BEFORE"
STRUCT_RC="$(run_structure "$REPO" "$OUT" "$ERR")"
manifest_all "$GITDIR_ABS" "$MAN_AFTER"

WF_REASONS=()
if ((STRUCT_RC != 0)); then
  WF_REASONS+=("rc=$STRUCT_RC")
fi
if [[ -s $ERR ]]; then
  WF_REASONS+=("stderr-nonempty")
fi
if ! cmp -s "$MAN_BEFORE.content" "$MAN_AFTER.content" ||
  ! cmp -s "$MAN_BEFORE.meta" "$MAN_AFTER.meta"; then
  WF_REASONS+=("manifest-delta")
fi
MAN_FILES="$(count_lines "$MAN_AFTER.meta")"
if ((MAN_FILES < 10)); then
  WF_REASONS+=("manifest_entries=$MAN_FILES")
fi
for marker in \
  "$GITDIR_ABS/index" \
  "$GITDIR_ABS/HEAD" \
  "$GITDIR_ABS/config" \
  "$GITDIR_ABS/refs/heads/master" \
  "$GITDIR_ABS/logs/HEAD"; do
  if ! grep -Fq -- "$marker" "$MAN_AFTER.content"; then
    WF_REASONS+=("missing=$marker")
  fi
done
if ((CTRL_OK == 0)); then
  WF_REASONS+=("manifest-control-failed")
fi

wf_detail=""
for reason in "${WF_REASONS[@]}"; do
  wf_detail+="${wf_detail:+;} $reason"
done
if ((${#WF_REASONS[@]} == 0)); then
  emit SOUJI-R13-STRUCT-write-free write-free \
    "rc=$STRUCT_RC manifest_entries=$MAN_FILES verdict=PASS"
else
  FAILED=1
  emit SOUJI-R13-STRUCT-write-free write-free \
    "rc=$STRUCT_RC manifest_entries=$MAN_FILES verdict=FAIL detail=$wf_detail"
fi

# ---------------------------------------------------------------- metrics
parse_metrics "$OUT"
CHECKS=0
FAILS=()
if ((STRUCT_RC != 0)) || [[ -s $ERR ]]; then
  CHECKS=1
  FAILS+=("not-clean rc=$STRUCT_RC stderr_lines=$(count_lines "$ERR")")
else
  check_eq references.branches.count 1
  check_eq references.tags.count 0
  check_eq references.remotes.count 0
  check_eq references.others.count 0
  check_eq objects.commits.count 1
  check_eq objects.trees.count 1
  check_eq objects.blobs.count 1
  check_eq objects.tags.count 0
  check_eq objects.blobs.inflated_size "$EXPECTED_BLOB_BYTES"
  check_eq objects.commits.max_size_oid "$HEAD_OID"
  check_eq objects.commits.max_parents 0
  check_eq objects.commits.max_parents_oid "$HEAD_OID"
  check_eq objects.trees.max_size_oid "$TREE_OID"
  check_eq objects.trees.max_entries 1
  check_eq objects.trees.max_entries_oid "$TREE_OID"
  check_eq objects.blobs.max_size_oid "$BLOB_OID"
  check_eq objects.tags.max_size_oid "$ZERO40"

  CHECKS=$((CHECKS + 1))
  blob_disk=${M[objects.blobs.disk_size]-}
  if [[ $blob_disk =~ ^[0-9]+$ ]] && ((10#$blob_disk > 0)); then
    :
  else
    FAILS+=("objects.blobs.disk_size=$blob_disk want>0")
  fi

  if ((PROBE_SET)); then
    check_eq probe.status ok
    check_eq probe.scope refs-rooted-reachable
    check_eq probe.git_version "$GIT_VERSION"
    check_eq probe.git_optional_locks 0
    check_eq probe.maintenance_auto false
    check_eq probe.format lines
    check_eq probe.bare false
    check_nonempty probe.git_dir
    check_nonempty probe.git_common_dir
    check_nonempty probe.repo_root
    check_contains probe.command 'repo structure --format=lines'
  fi
fi

metrics_detail=""
for reason in "${FAILS[@]}"; do
  metrics_detail+="${metrics_detail:+;} $reason"
done
if ((${#FAILS[@]} == 0 && CHECKS > 0)); then
  emit SOUJI-R13-STRUCT-object-metrics object-metrics \
    "checks=$CHECKS verdict=PASS"
else
  FAILED=1
  emit SOUJI-R13-STRUCT-object-metrics object-metrics \
    "checks=$CHECKS verdict=FAIL detail=$metrics_detail"
fi

# ---------------------------------------------------------------- bogus repo
BOGUS="$WORK/not-a-repo"
mkdir "$BOGUS"
printf 'not a repository\n' >"$BOGUS/plain.txt"
manifest_all "$BOGUS" "$WORK/bogus-before"
BOGUS_RC="$(run_structure "$BOGUS" "$WORK/bogus.out" "$WORK/bogus.err")"
MISSING_RC="$(run_structure "$WORK/absent" "$WORK/absent.out" "$WORK/absent.err")"
manifest_all "$BOGUS" "$WORK/bogus-after"

BOGUS_REASONS=()
if ((BOGUS_RC == 0)); then
  BOGUS_REASONS+=("plain-dir-accepted")
fi
if ((MISSING_RC == 0)); then
  BOGUS_REASONS+=("missing-path-accepted")
fi
if ((PROBE_SET)); then
  if ((BOGUS_RC != 2)); then
    BOGUS_REASONS+=("plain-dir-rc=$BOGUS_RC want=2")
  fi
  if ((MISSING_RC != 2)); then
    BOGUS_REASONS+=("missing-path-rc=$MISSING_RC want=2")
  fi
fi
if [[ -s "$WORK/bogus.err" ]]; then
  :
else
  BOGUS_REASONS+=("plain-dir-stderr-empty")
fi
if grep -q '^references\.branches\.count=' "$WORK/bogus.out"; then
  BOGUS_REASONS+=("plain-dir-emitted-structure")
fi
if ! cmp -s "$WORK/bogus-before.content" "$WORK/bogus-after.content" ||
  ! cmp -s "$WORK/bogus-before.meta" "$WORK/bogus-after.meta"; then
  BOGUS_REASONS+=("plain-dir-mutated")
fi
if ((PROBE_SET)) && ! grep -q 'probe\.error=' "$WORK/bogus.err"; then
  BOGUS_REASONS+=("plain-dir-no-probe-error")
fi

bogus_detail=""
for reason in "${BOGUS_REASONS[@]}"; do
  bogus_detail+="${bogus_detail:+;} $reason"
done
if ((${#BOGUS_REASONS[@]} == 0)); then
  emit SOUJI-R13-STRUCT-bogus-repo bogus-repo \
    "plain_dir_rc=$BOGUS_RC missing_rc=$MISSING_RC verdict=PASS"
else
  FAILED=1
  emit SOUJI-R13-STRUCT-bogus-repo bogus-repo \
    "plain_dir_rc=$BOGUS_RC missing_rc=$MISSING_RC verdict=FAIL detail=$bogus_detail"
fi

# ---------------------------------------------------- promisor/partial refusal
# Probe-only: baseline mode has no refusal logic, and running the raw command
# against a promisor repository is the hazard this case exists to prevent.
# No network: the remote URL is example.invalid and the probe must refuse from
# configuration before any structure/object walk.
if ((PROBE_SET)); then
  PR="$WORK/promisor-repo"
  PART="$WORK/partial-repo"
  for refusal_repo in "$PR" "$PART"; do
    mkdir "$refusal_repo"
    g "$refusal_repo" init -q --object-format=sha1 .
    printf 'refusal fixture payload\n' >"$refusal_repo/payload.txt"
    g "$refusal_repo" add -- payload.txt
    g "$refusal_repo" commit -qm 'r13 refusal fixture'
    g "$refusal_repo" config remote.origin.url \
      'https://example.invalid/r13-refusal.git'
    g "$refusal_repo" config remote.origin.promisor true
  done
  # extensions.partialclone is honoured in v0-format repositories for
  # historical compatibility (setup.c handle_extension_v0); no format bump is
  # needed for the config marker.
  g "$PART" config extensions.partialClone origin

  PR_GITDIR="$(g "$PR" rev-parse --path-format=absolute --absolute-git-dir)"
  PART_GITDIR="$(g "$PART" rev-parse --path-format=absolute --absolute-git-dir)"
  manifest_all "$PR_GITDIR" "$WORK/promisor-before"
  manifest_all "$PART_GITDIR" "$WORK/partial-before"

  PROM_RC="$(run_structure "$PR" "$WORK/prom.out" "$WORK/prom.err")"
  PART_RC="$(run_structure "$PART" "$WORK/partial.out" "$WORK/partial.err")"

  manifest_all "$PR_GITDIR" "$WORK/promisor-after"
  manifest_all "$PART_GITDIR" "$WORK/partial-after"

  REFUSAL=()
  if ((PROM_RC != 2)); then
    REFUSAL+=("promisor-rc=$PROM_RC want=2")
  fi
  if ! grep -q 'probe\.error=promisor-remote-unsupported' "$WORK/prom.err"; then
    REFUSAL+=("promisor-marker-missing")
  fi
  if ((PART_RC != 2)); then
    REFUSAL+=("partial-rc=$PART_RC want=2")
  fi
  if ! grep -q 'probe\.error=partial-clone-unsupported' "$WORK/partial.err"; then
    REFUSAL+=("partial-marker-missing")
  fi
  if grep -q '^references\.branches\.count=' \
    "$WORK/prom.out" "$WORK/partial.out"; then
    REFUSAL+=("refusal-emitted-structure")
  fi
  if ! cmp -s "$WORK/promisor-before.content" "$WORK/promisor-after.content" ||
    ! cmp -s "$WORK/promisor-before.meta" "$WORK/promisor-after.meta"; then
    REFUSAL+=("promisor-repo-mutated")
  fi
  if ! cmp -s "$WORK/partial-before.content" "$WORK/partial-after.content" ||
    ! cmp -s "$WORK/partial-before.meta" "$WORK/partial-after.meta"; then
    REFUSAL+=("partial-repo-mutated")
  fi

  refusal_detail=""
  for reason in "${REFUSAL[@]}"; do
    refusal_detail+="${refusal_detail:+;} $reason"
  done
  if ((${#REFUSAL[@]} == 0)); then
    emit SOUJI-R13-STRUCT-promisor-refusal promisor-refusal \
      "promisor_rc=$PROM_RC partial_rc=$PART_RC verdict=PASS"
  else
    FAILED=1
    emit SOUJI-R13-STRUCT-promisor-refusal promisor-refusal \
      "promisor_rc=$PROM_RC partial_rc=$PART_RC verdict=FAIL detail=$refusal_detail"
  fi
fi

# ---------------------------------------------------------------- selftest ids
SELFTEST_EXPECTED_IDS=(
  SOUJI-R13-STRUCT-manifest-control
  SOUJI-R13-STRUCT-write-free
  SOUJI-R13-STRUCT-object-metrics
  SOUJI-R13-STRUCT-bogus-repo
)
if ((PROBE_SET)); then
  SELFTEST_EXPECTED_IDS+=(SOUJI-R13-STRUCT-promisor-refusal)
fi

missing=()
extra=()
for id in "${SELFTEST_EXPECTED_IDS[@]}"; do
  found=0
  for probe in "${EMITTED_IDS[@]}"; do
    if [[ $probe == "$id" ]]; then
      found=1
      break
    fi
  done
  ((found)) || missing+=("$id")
done
for id in "${EMITTED_IDS[@]}"; do
  found=0
  for probe in "${SELFTEST_EXPECTED_IDS[@]}"; do
    if [[ $probe == "$id" ]]; then
      found=1
      break
    fi
  done
  ((found)) || extra+=("$id")
done

want_n=${#SELFTEST_EXPECTED_IDS[@]}
got_n=${#EMITTED_IDS[@]}
if ((${#missing[@]} == 0 && ${#extra[@]} == 0 && got_n == want_n && FAILED == 0)); then
  printf 'selftest=PASS ids=%s/%s\n' "$want_n" "$want_n"
  exit 0
fi
printf 'selftest=FAIL ids=%s/%s missing=[%s] extra=[%s] failed_verdicts=%s\n' \
  "$got_n" "$want_n" "${missing[*]-}" "${extra[*]-}" "$FAILED"
exit 1
