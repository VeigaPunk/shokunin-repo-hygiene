#!/usr/bin/env bash
# souji-repo-structure — read-only F2 size-census probe (round 13).
#
# Purpose: run the installed `git repo structure --format=lines` against one
# repository and report the metrics together with the exact git version and
# argv. The read-only envelope the r13 F2 evidence depends on:
#   GIT_OPTIONAL_LOCKS=0          no optional locks / no index refresh (S036,
#                                 git(1) roff :2195-2200)
#   -c maintenance.auto=false     no auto-maintenance rides along (r12 M51)
#   -c maintenance.autoDetach=false
#   GIT_NO_LAZY_FETCH=1           no promisor fetch from object reads (git(1)
#                                 roff :2122)
#   GIT_TERMINAL_PROMPT=0         no credential prompt
#   git -c ... -C PATH ...        never `cd`; every call names the repo
# Promisor/partial-clone repositories are REFUSED before any structure walk
# (exit 2) when `extensions.partialClone` is set or any
# `remote.*.promisor=true` exists. Ground truth reported by AttackCoverage
# this wave (not re-run by this seat): on a partialClone tree:0 repository,
# `git repo structure` performed three lazy fetches and grew .git from 28 to
# 40 files with incomplete stats even with optional locks off and
# maintenance.auto=false. GIT_NO_LAZY_FETCH=1 alone would change that into
# an error/incomplete read, not a trustworthy census, so the probe fails
# closed instead of reporting numbers.
# This wrapper requests no fetch, maintenance or index operation; Git reads
# repository objects internally. It creates ONE mktemp directory under the
# caller's TMPDIR (falling back to /var/tmp)
# only to capture the command's stdout/stderr, removes it on exit, and emits
# numeric metrics only if the command exited 0 with EMPTY stderr. Ground truth
# reported by AttackCoverage this wave (not re-run by this seat): the command
# can exit 0 while skipping missing objects, so exit 0 is not a completeness
# proof. Metrics are therefore described as refs-rooted reachable only:
# `structure` seeds its walk from references (builtin/repo.c:722) in the
# common object store; an unreferenced detached HEAD is not counted, and a
# skipped object can be omitted silently. In a linked worktree the probe
# reports the resolved common dir; the object store is shared.
#
# Format: `git repo structure` is EXPERIMENTAL in installed git 2.55.0
# (git-repo(1), roff :44: "THIS COMMAND IS EXPERIMENTAL. THE BEHAVIOR MAY
# CHANGE."). Its default table "may change and is not intended for machine
# parsing" (roff :166), so this probe requires `--format=lines` and NEVER
# parses or falls back to the table. The lines key set is the installed
# command's contract (upstream git v2.55.0 builtin/repo.c:633-685; the format
# dispatch is :918).
#
# CLI
#   tools/souji-repo-structure.sh --repo PATH
#   tools/souji-repo-structure.sh --help
#
# PATH may be the work-tree root, any subdirectory of it, or a bare
# repository; discovery is `git -C PATH rev-parse`. The probe does not
# canonicalize PATH itself. Bare/subdirectory resolution is incidental; the
# committed fixture and its write-safety claim cover one normal work tree
# only.
#
# Output (stdout, LC_ALL=C, one key=value per line; metadata first):
#   probe.tool=souji-repo-structure
#   probe.status=ok
#   probe.git_version=<verbatim `git --version`>
#   probe.command=<exact git argv, path %q-quoted by this script>
#   probe.repo_root=<toplevel; omitted when there is none (bare repo)>
#   probe.git_dir=<absolute git dir, %q-quoted>
#   probe.git_common_dir=<absolute common dir, %q-quoted>
#   probe.bare=true|false
#   probe.scope=refs-rooted-reachable
#   probe.git_optional_locks=0
#   probe.maintenance_auto=false
#   probe.format=lines
#   <verbatim `git repo structure --format=lines` output: 28 keys>
# probe.* cannot collide with the command's references.*/objects.* keys.
#
# Exit codes
#   0  probe ran; stdout carries probe.status=ok and the structure lines
#   2  usage, git missing, PATH missing/not a directory, PATH is not a usable
#      repository (including a corrupt one rev-parse rejects), or the repo is
#      a promisor/partial clone (`extensions.partialClone` set or a
#      `remote.*.promisor=true`); such repos are refused before structure
#   3  installed git lacks `repo structure --format=lines`; the capability
#      check is `git -C PATH repo structure -h` (LC_ALL=C) whose text must
#      name both "repo structure" and "lines"
#   4  repository resolved, but config was unreadable, structure exited
#      nonzero, structure wrote to stderr, or the output lacked
#      `objects.commits.count=`; captured stderr is echoed as bounded
#      `probe.stderr=` diagnostics and no numeric metric reaches stdout
# Errors go to stderr as `probe.status=error|unsupported probe.error=...`.
#
# Read-only claim and its bound: this tool issues only the guarded read
# command above. That is not a proof for arbitrary environments: system/global
# config includes, alternates, promisor remotes, hooks of other commands,
# filesystem/mount behaviour, concurrent writers and future EXPERIMENTAL
# format changes are out of scope. The bounded, re-runnable evidence for this
# host is tests/fixtures/r13-repo-structure.sh: it diffs a full .git
# path/content/stat manifest (sha256, type, mode, size, mtime; no atime)
# around one run in one isolated normal repository rooted in the caller's
# TMPDIR, after first proving the manifest detects content and metadata deltas. The claim is "no
# persistent delta observed for this run", never universal write-safety. A
# size census authorizes no deletion (PROVINCE.md F2; QUALITY Q18).
set -euo pipefail
shopt -s inherit_errexit

usage_text() {
  cat <<'EOF'
usage: souji-repo-structure.sh --repo PATH
       souji-repo-structure.sh --help

Read-only probe of one git repository using the installed
`git repo structure --format=lines`. Prints probe.* metadata, then the
command's own key=value metrics. The volatile table format is never used.

Guards on every git call: GIT_OPTIONAL_LOCKS=0, GIT_NO_LAZY_FETCH=1,
GIT_TERMINAL_PROMPT=0, git -c maintenance.auto=false
-c maintenance.autoDetach=false -C PATH. No fetch, no maintenance, no index
refresh, no file writes. Promisor/partial-clone repositories are refused
(exit 2) before the structure walk.

Exit codes: 0 ok; 2 usage/git-missing/repo-unusable/promisor-or-partial;
3 installed git lacks `repo structure --format=lines`; 4 structure failed,
config unreadable, or no known metric emitted.
EOF
}
usage() { usage_text >&2; exit 2; }
help() { usage_text; exit 0; }
probe_error() { # <error> [detail]; stderr only
  printf 'probe.status=error probe.error=%s' "$1"
  if (($# > 1)); then printf ' %s' "$2"; fi
  printf '\n'
}

repo=""
while (($#)); do
  case "$1" in
    --repo)
      (($# >= 2)) || usage
      repo=$2
      shift 2
      ;;
    --repo=*)
      repo=${1#*=}
      shift
      ;;
    --help|-h)
      help
      ;;
    *)
      usage
      ;;
  esac
done
[[ -n $repo ]] || usage

export LC_ALL=C
export GIT_OPTIONAL_LOCKS=0
export GIT_NO_LAZY_FETCH=1
export GIT_TERMINAL_PROMPT=0
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE \
  GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES

command -v git >/dev/null 2>&1 || { probe_error git-missing >&2; exit 2; }

probe_tmp=""
cleanup_probe_tmp() {
  local rc=$?
  if [[ -n ${probe_tmp:-} && -d $probe_tmp ]]; then
    rm -rf -- "$probe_tmp"
  fi
  exit "$rc"
}
trap cleanup_probe_tmp EXIT

[[ -e $repo ]] || {
  probe_error repo-missing "path=$(printf %q "$repo")" >&2
  exit 2
}
[[ -d $repo ]] || {
  probe_error repo-not-directory "path=$(printf %q "$repo")" >&2
  exit 2
}

GIT=(git -c maintenance.auto=false -c maintenance.autoDetach=false)
git_version="$("${GIT[@]}" --version)"

git_dir=""
if ! git_dir="$("${GIT[@]}" -C "$repo" rev-parse --path-format=absolute --absolute-git-dir 2>/dev/null)"; then
  probe_error not-a-repo "path=$(printf %q "$repo")" >&2
  exit 2
fi
[[ -n $git_dir ]] || {
  probe_error not-a-repo "path=$(printf %q "$repo")" >&2
  exit 2
}

top=""
top="$("${GIT[@]}" -C "$repo" rev-parse --show-toplevel 2>/dev/null)" || top=""
common=""
common="$("${GIT[@]}" -C "$repo" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || common="$git_dir"
bare=""
bare="$("${GIT[@]}" -C "$repo" rev-parse --is-bare-repository 2>/dev/null)" || bare=false

# Promisor/partial-clone refusal: fail closed before the structure walk.
# A partialClone tree:0 repo was observed lazily fetching three times and
# growing .git 28 -> 40 files with incomplete stats; GIT_NO_LAZY_FETCH=1
# turns that into an error or an incomplete read, neither of which is a
# trustworthy census. Either marker rejects, regardless of value spelling.
partial_rc=0
"${GIT[@]}" -C "$repo" config --local --get extensions.partialClone >/dev/null 2>&1 ||
  partial_rc=$?
if ((partial_rc == 0)); then
  probe_error partial-clone-unsupported "detail=extensions.partialClone" >&2
  exit 2
fi
if ((partial_rc != 1)); then
  printf 'probe.status=could-not-evaluate probe.error=config-unreadable rc=%s key=extensions.partialClone\n' \
    "$partial_rc" >&2
  exit 4
fi

promisor_rc=0
promisor_lines="$("${GIT[@]}" -C "$repo" config --type=bool --get-regexp '^remote\..*\.promisor$' 2>/dev/null)" ||
  promisor_rc=$?
if ((promisor_rc == 0)); then
  while IFS= read -r line; do
    case "$line" in
      *" true")
        probe_error promisor-remote-unsupported "detail=${line%% *}" >&2
        exit 2
        ;;
      *) : ;;
    esac
  done <<<"$promisor_lines"
fi
if ((promisor_rc != 0 && promisor_rc != 1)); then
  printf 'probe.status=could-not-evaluate probe.error=config-unreadable rc=%s key=remote-promisor\n' \
    "$promisor_rc" >&2
  exit 4
fi

# Capability check: fail closed if the installed git has no structure
# subcommand or no lines format. -h exits nonzero by design; only its text is
# used, and LC_ALL=C keeps the usage text deterministic.
help_text=""
help_text="$("${GIT[@]}" -C "$repo" repo structure -h 2>&1)" || true
case "$help_text" in
  *"repo structure"*lines*) : ;;
  *)
    printf 'probe.status=unsupported probe.error=repo-structure-unsupported git_version=%q\n' \
      "$git_version" >&2
    exit 3
    ;;
esac

emit_stderr_file() { # <file>: bounded diagnostics, prefixed, stderr only
  local n=0 line
  while IFS= read -r line; do
    if ((n >= 20)); then
      printf 'probe.stderr_truncated=true\n' >&2
      break
    fi
    printf 'probe.stderr=%s\n' "$line" >&2
    n=$((n + 1))
  done <"$1"
}

# Numeric output is captured first and emitted only after a clean
# evaluation: exit 0 AND empty stderr AND a known metric key. Any stderr on
# exit 0 is treated as could-not-evaluate (the command can exit 0 while
# skipping unreadable/missing objects); no partial numbers reach stdout.
probe_tmp="$(mktemp -d "${TMPDIR:-/var/tmp}/souji-repo-structure.XXXXXX")" || {
  probe_error mktemp-failed >&2
  exit 2
}

structure_rc=0
if "${GIT[@]}" -C "$repo" repo structure --format=lines \
  >"$probe_tmp/structure.out" 2>"$probe_tmp/structure.err"; then
  structure_rc=0
else
  structure_rc=$?
fi
if ((structure_rc != 0)); then
  printf 'probe.status=could-not-evaluate probe.error=structure-failed rc=%s\n' \
    "$structure_rc" >&2
  if [[ -s $probe_tmp/structure.err ]]; then
    emit_stderr_file "$probe_tmp/structure.err"
  fi
  exit 4
fi
if [[ -s $probe_tmp/structure.err ]]; then
  printf 'probe.status=could-not-evaluate probe.error=structure-stderr\n' >&2
  emit_stderr_file "$probe_tmp/structure.err"
  exit 4
fi
if [[ ! -s $probe_tmp/structure.out ]] ||
  ! grep -q '^objects\.commits\.count=' "$probe_tmp/structure.out"; then
  printf 'probe.status=could-not-evaluate probe.error=unexpected-structure-output\n' >&2
  exit 4
fi

cmd_display="git -c maintenance.auto=false -c maintenance.autoDetach=false -C $(printf %q "$repo") repo structure --format=lines"

printf 'probe.tool=souji-repo-structure\n'
printf 'probe.status=ok\n'
printf 'probe.git_version=%s\n' "$git_version"
printf 'probe.command=%s\n' "$cmd_display"
if [[ -n $top ]]; then
  printf 'probe.repo_root=%q\n' "$top"
fi
printf 'probe.git_dir=%q\n' "$git_dir"
printf 'probe.git_common_dir=%q\n' "$common"
printf 'probe.bare=%s\n' "$bare"
printf 'probe.scope=refs-rooted-reachable\n'
printf 'probe.git_optional_locks=0\n'
printf 'probe.maintenance_auto=false\n'
printf 'probe.format=lines\n'
cat -- "$probe_tmp/structure.out"
