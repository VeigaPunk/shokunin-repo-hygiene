#!/usr/bin/env bash
# souji-census — repeatable read-only fleet census (round 6, seat S33).
# Round-14 C2 adds a pre-access protected-path boundary. Round-16 C1 makes
# the repository-config guard value/effect-aware (repairs r14's value-blind
# whole-run refusals of benign configuration). Round-17 C1 pins
# --untracked-files=normal on the dirty count and degrades a hardlinked or
# non-regular info/attributes to a per-repo error row.
#
# One bash tool; Bash, coreutils, git, util-linux `setsid`, Python 3 (--selftest),
# and Linux /proc. Never fetches; writes only temporary census output under /var/tmp.
# The mtime walk never opens file contents, but `git status` may read or hash
# tracked content (this is not a data-loss-prevention classifier), and
# .ufo/state or .ufo/watchdog.log are never traversed by the mtime walk.
#
# CLI
#   tools/souji-census.sh [--root DIR] [--compare PREV.tsv]
#                         [--repo-timeout N] [--include-root] [--selftest]
#
# Default scan: every immediate child of $SHOKUNIN_ROOT (or --root) whose
# .git is a directory (a main repo, not a linked work tree or submodule
# gitfile). Linked work trees are counted on their owner via `worktree list`,
# not emitted as their own row. --include-root also emits a row for the root
# itself when it is a main repo.

#   Immediate child basenames containing TAB, LF or CR are skipped with
#   stderr `souji-census: skipped-ambiguous-name <sanitized-path>`.
#
# Census TSV (header + one row per repo, LC_ALL=C path sort):
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#
#   repo            absolute canonical path
#   worktrees       `git worktree list` line count (main work tree included)
#   unpushed        commits on any local branch not reachable from any
#                   remote-tracking ref (`git rev-list --count --branches
#                   --not --remotes`). If the repo has zero refs/remotes/*,
#                   the count is every local commit and verdict_flags includes
#                   no-remote (pushedness unverifiable — same rule as
#                   souji-verify). The number is still reported, and unpushed
#                   is also set when that count is > 0.
#   dirty           `git status --porcelain` line count on the main work tree
#                   only (explicit --untracked-files=normal: a wholly
#                   untracked directory is one line, matching souji-verify).
#                   Other work trees are not added into this number; see
#                   wt-dirty. Submodule
#                   content is not inspected (--ignore-submodules=all).
#   scratch_bytes   apparent byte size of <repo>/.scratch (`du -sb -P`; 0 if
#                   absent or a symlink). Does not follow symlinks.
#   mtime_iso       newest regular-file mtime under the main work tree,
#                   ISO-8601 with numeric offset, second resolution. .git,
#                   .ufo/state, and .ufo/watchdog.log are pruned and never
#                   stat'd. census/operator-sweep-* is pruned the same way.
#                   Secret-shaped names are flagged and excluded from
#                   the max by this walk. The walk never opens contents;
#                   `git status` still may read/hash tracked files.
#   verdict_flags   comma-joined, stable order, subset of:
#                     clean | dirty | unpushed | no-remote | scratch |
#                     secret-shaped | wt-absent | wt-dirty |
#                     status-unverifiable | not-a-repo | error
#                   "clean" only when unpushed=0, dirty=0, and a remote
#                     tracking ref exists. no-remote replaces a false "clean".
#                   wt-absent: a non-main worktree registration whose directory
#                     is missing (metadata only; not a separate row).
#                   wt-dirty: a non-main worktree directory is present and its
#                     own `git status --porcelain` is non-empty.

# --repo-timeout N
#   Maximum integer seconds per repository (1..86400; default 600).
#   Overrides SOUJI_CENSUS_REPO_TIMEOUT; invalid values exit 2.
#
# --compare PREV.tsv
#   Reads a previous census (header required, same columns). Emits a diff
#   TSV on stdout:
#     repo  field  before  after  change
#   One row per changed numeric/text field, plus rows for added/removed
#   repos (field=repo, before/after = ABSENT or PRESENT). Exit 0 when the
#   diff is header-only; exit 3 when any row differs. Census rows are not
#   mixed into the diff.
#
# --selftest
#   Builds fixture fleets under /var/tmp, runs the census twice (byte-
#   identical), mutates one fixture, checks --compare, protected refusals,
#   and per-repository watchdog behavior. Removes fixtures on exit. Exit 0
#   on pass, 1 on fail.
#
# Protected boundary (round 14, C2)
#   --root and --compare are resolved one component at a time before any
#   git, find, du or file read. A path that reaches, equals, or is an
#   ancestor of ~/.omp/agent (HOME union the passwd home, plus
#   PI_CODING_AGENT_DIR and <home>/${PI_CONFIG_DIR:-.omp}/agent), or that
#   contains a census/operator-sweep-* or .ufo/state|.ufo/watchdog.log
#   component, is refused with the stable finding `path-protected` on
#   stderr and exit 2. An input containing a `..` component is refused as
#   ambiguous: a lexical parent and a symlink-resolved parent can differ.
#   Symlink repo roots and child symlinks are skipped; a .git symlink is
#   not followed as a row; gitfile gitdir targets, commondir and
#   objects/info/alternates are boundary-checked before git runs, and any
#   git-metadata symlink must resolve inside its own gitdir (these r14
#   git-metadata guards are unchanged by round 16 and still refuse the
#   whole run). Repository config is scanned per key and value (round 16),
#   recursively through include.path/includeIf.*.path targets (every
#   target is guarded whatever its condition; relative targets resolve
#   against the including file's spelled directory) and through
#   config.worktree when the common config's extensions.worktreeConfig is
#   true. Config outcomes: Refused (exit 2, whole run, `path-protected`): a
#   config-named path (include target, core.excludesFile,
#   core.attributesFile, core.worktree) overlapping a protected root; a soft
#   finding never stops the scan, so a later protected reach still refuses.
#   Round-17: dirty counts pass an explicit --untracked-files=normal, so a
#   repo-local, included or config.worktree `status.showUntrackedFiles=no|
#   all` cannot change the dirty/clean measure or the directory collapse.
#   Round-17: a hardlinked or non-regular (FIFO/socket/device, or a
#   symlink inside the gitdir resolving to one; a looping or out-of-gitdir
#   symlink keeps the whole-run symlink refusal) $GIT_DIR/info/attributes
#   — in the repo
#   gitdir, a common dir, or a linked-worktree admin dir — joins the
#   degraded set below instead of refusing the fleet: stderr `souji-census:
#   git-metadata-unsupported <reason> <path>` for that repository only
#   (exit 0; no git call that could read that file runs in it). A
#   directory info/attributes stays accepted (git opens it, gets EISDIR,
#   and treats it as empty); a dangling symlink is treated as absent; an
#   admin-dir copy degrades the owner although git reads only the common
#   info/ (fail-safe over-refusal). Empty files are regular. Every
#   other guarded metadata entry —
#   config, HEAD, index, packed-refs, commondir, info/exclude,
#   objects/info/alternates — keeps its exit-2 whole-run refusal even when
#   info/attributes of the same gitdir is already soft.
#   Degraded to one `error` row for that repository only (exit 0; no git
#   command runs in it; stderr `souji-census: config-unsupported: <reason>
#   (<repo>)`; its numeric fields are placeholders, not measurements): a
#   `~user` or `%(prefix)` path; an unresolvable or ambiguous config path;
#   an include cycle or depth over 10; a non-regular or hardlinked include
#   target or config.worktree; NUL bytes or unparsable config; an invalid
#   extensions.worktreeConfig boolean. Status skipped for that repository
#   only (status-unverifiable, dirty unknown): a
#   filter.<name>.clean|smudge|process driver that an attributes source
#   binds to a tracked path (stderr `status-skipped`; the driver never
#   runs, and the attribute lookup fails closed), or an effective
#   excludes/attributes value that cannot be modelled or is non-regular.
#   Accepted: any core.hooksPath/core.fsmonitor value (every census git
#   call carries core.fsmonitor=false and core.hooksPath=/dev/null via
#   GIT_CONFIG_COUNT; status also passes them with -c), boundary-clean
#   excludes/attributes files (honored on status, as before round 14; a
#   set-but-empty value disables the file; when unset the XDG default is
#   honored if present and boundary-clean), any remote.*.promisor or
#   extensions.partialClone value (GIT_NO_LAZY_FETCH=1 on every call, git
#   >= 2.45; an invalid promisor boolean fails git's own status, giving
#   status-unverifiable as before round 14), any core.alternateRefsCommand
#   (consumed only by receive-pack ref advertisement, fetch negotiation and
#   `rev-list --alternate-refs`, none of which the census runs), unbound
#   filter drivers, missing include targets. A refused path that is itself
#   inside a protected root is printed as `<protected>`.
#   Global/system git config and every inherited GIT_* variable are cleared;
#   GIT_ATTR_NOSYSTEM=1 disables the system attributes file. Startup resolves
#   each home's .omp parent (not the agent store) for relocated-store safety.
#   This is a stat/readlink of the store parent, never store content. Residual:
#   hardlinked aliases are refused for --compare (nlink > 1) and fixed git
#   metadata, but hardlinked object files and arbitrary hardlinks into a store
#   are not detectable without stat'ing the store; the guard and access are
#   not one atomic operation.
#   Candidate metadata guards and census runs each use a private process group.
#   If one exceeds the bound, its group receives TERM, then KILL two seconds
#   later; a timed-out repository gets the row
#   `<repo>\t0\t0\t0\t0\t\terror` and stderr
#   `souji-census: repo-timeout <N>s <repo>`. Other repositories continue.
#   After KILL, reaping is bounded to three seconds; a survivor is reported
#   as `souji-census: repo-timeout-unreaped <repo>`.

#   Parent HUP/TERM cleanup stops the active worker and watchdog before
#   deleting temporary state. A parent SIGKILL cannot trap; the detached
#   watchdog remains armed to reap the worker and then remove its temp tree.
#
# Exit codes
#   0 census emitted (rows may carry `error`/status-unverifiable for
#     degraded or timed-out repositories) / header-only diff; 1 selftest or
#     setup/census failure; 2 usage, malformed baseline, protected-path
#     refusal; 3 compare drift.
#
# Env
#   SHOKUNIN_ROOT                 default root when --root is omitted
#                                 (default: parent of this repo)
#   SOUJI_CENSUS_REPO_TIMEOUT     integer seconds per repository, 1..86400
#                                 (default: 600)
set -euo pipefail

# Imported BASH_FUNC_* definitions could shadow the externally-resolved
# commands this tool relies on. Remove functions for those names.
unset -f bash cat git kill find du stat awk grep sort head cut date readlink sleep mktemp setsid mkdir rm cmp tr python3 2>/dev/null || true

# Clear every inherited GIT_* variable. GIT_DIR/GIT_COMMON_DIR/
# GIT_OBJECT_DIRECTORY/GIT_ALTERNATE_OBJECT_DIRECTORIES and GIT_CONFIG_*
# can redirect reads or command execution into a credential store. Global
# and system config are disabled; repository-local config inside a guarded
# repo is still inspected and, if unsupported, refused.
while IFS= read -r _souji_gitvar; do unset "$_souji_gitvar"; done < <(compgen -v GIT_ || true)
unset _souji_gitvar
export GIT_OPTIONAL_LOCKS=0
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 GIT_ATTR_NOSYSTEM=1
# Round 16: no census git call may lazily fetch a missing object
# (GIT_NO_LAZY_FETCH, git >= 2.45), so remote.*.promisor and
# extensions.partialClone markers stay inert. Every census git call (not
# only status) also runs with the fsmonitor hook and the hooks directory
# neutralized: index readers such as ls-files would otherwise run a
# repository's core.fsmonitor command.
export GIT_NO_LAZY_FETCH=1
export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=core.fsmonitor GIT_CONFIG_VALUE_0=false
export GIT_CONFIG_KEY_1=core.hooksPath GIT_CONFIG_VALUE_1=/dev/null

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'
DIFF_HEADER=$'repo\tfield\tbefore\tafter\tchange'

ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
COMPARE=""
COMPARE_SET=0
INCLUDE_ROOT=0
SELFTEST=0
REPOS=()
GUARD_CANDIDATES=()
GUARD_KINDS=()
ROOT_RAW_IS_SYMLINK=0
CENSUS_TMP=""
REPO_TIMEOUT="${SOUJI_CENSUS_REPO_TIMEOUT-600}"
REPO_TIMED_OUT=0
REPO_UNREAPED=0
PROC_STATE=""
CURRENT_WORKER_PGID=""
CURRENT_WATCHDOG_PID=""
CURRENT_REPO=""

usage() {
  awk 'NR > 1 { if ($0 !~ /^#/) exit; sub(/^# ?/, ""); print }' "$SELF"
  exit "${1:-0}"
}

usage_err() { printf 'souji-census: %s\n' "$1" >&2; usage 2 >&2; }

stop_active_census() {
  local worker=${CURRENT_WORKER_PGID:-} watchdog=${CURRENT_WATCHDOG_PID:-}
  local ticks=0 dead=0
  if [ -n "$worker" ]; then
    kill -TERM -- "-$worker" 2>/dev/null || true
    sleep 0.1
    kill -KILL -- "-$worker" 2>/dev/null || true
  fi
  if [ -n "$watchdog" ]; then
    kill -KILL -- "-$watchdog" 2>/dev/null || true
    wait "$watchdog" 2>/dev/null || true
  fi
  if [ -n "$worker" ]; then
    while [ "$ticks" -lt 30 ]; do
      if proc_state "$worker"; then
        case "$PROC_STATE" in
          Z|X)
            wait "$worker" 2>/dev/null || true
            dead=1
            break
            ;;
        esac
      else
        wait "$worker" 2>/dev/null || true
        dead=1
        break
      fi
      sleep 0.1
      ticks=$((ticks + 1))
    done
    if [ "$dead" = 0 ]; then
      printf 'souji-census: repo-timeout-unreaped %s\n' \
        "$(sanitize_field "${CURRENT_REPO:-}")" >&2
    fi
  fi
  CURRENT_WORKER_PGID=""
  CURRENT_WATCHDOG_PID=""
  CURRENT_REPO=""
}

cleanup_census_tmp() {
  stop_active_census
  if [ -n "${CENSUS_TMP:-}" ]; then
    rm -rf -- "$CENSUS_TMP"
  fi
}

handle_census_signal() {
  local signal=$1 status=128
  case "$signal" in HUP) status=129 ;; INT) status=130 ;; TERM) status=143 ;; esac
  trap - HUP INT TERM
  stop_active_census
  if [ -n "${CENSUS_TMP:-}" ]; then
    rm -rf -- "$CENSUS_TMP"
    CENSUS_TMP=""
  fi
  kill -s "$signal" "$BASHPID" 2>/dev/null || exit "$status"
  exit "$status"
}

trap 'handle_census_signal HUP' HUP
trap 'handle_census_signal INT' INT
trap 'handle_census_signal TERM' TERM

prepare_census_tmp() {
  if [ -z "${CENSUS_TMP:-}" ]; then
    CENSUS_TMP=$(mktemp -d /var/tmp/souji-census-now.XXXXXX)
    trap cleanup_census_tmp EXIT
  fi
}

validate_repo_timeout() {
  case "$REPO_TIMEOUT" in
    ''|*[!0-9]*) usage_err "invalid repo timeout (expected integer 1..86400)" ;;
  esac
  while [ "${#REPO_TIMEOUT}" -gt 1 ] && [ "${REPO_TIMEOUT:0:1}" = 0 ]; do
    REPO_TIMEOUT=${REPO_TIMEOUT:1}
  done
  if [ "${#REPO_TIMEOUT}" -gt 5 ]; then
    usage_err "invalid repo timeout (expected integer 1..86400)"
  fi
  if [ "$REPO_TIMEOUT" -lt 1 ] || [ "$REPO_TIMEOUT" -gt 86400 ]; then
    usage_err "invalid repo timeout (expected integer 1..86400)"
  fi
}

# --- protected-path boundary (round 14, C2) --------------------------------

PROTECTED_FINDING='path-protected'
PROTECTED_HOME_ROOTS=()

protected_fail() { # $1 reason, $2 label, $3 path
  local shown=$3
  if [ -n "$shown" ] && protected_reason_inside "$shown" >/dev/null 2>&1; then
    shown='<protected>'
  fi
  printf 'souji-census: %s: %s (%s: %s)\n' \
    "$PROTECTED_FINDING" "$1" "$2" "$shown" >&2
  exit 2
}

# Textual absolute normalization: no filesystem access. Callers that accept
# user input still refuse a `..` component (see resolve_guarded) because a
# lexical parent and a link-resolved parent can differ.
lexical_abs() {
  local p=${1:-} out="" part
  local -a parts=()
  case "$p" in
    /*) ;;
    *) p="$PWD/$p" ;;
  esac
  local IFS=/
  read -r -a parts <<< "$p"
  for part in "${parts[@]}"; do
    case "$part" in
      ''|.) continue ;;
      ..) if [ -n "$out" ]; then out=${out%/*}; fi ;;
      *) out="$out/$part" ;;
    esac
  done
  if [ -z "$out" ]; then printf '/'; else printf '%s' "$out"; fi
}

path_under() { # $1 path, $2 prefix; both normalized absolute
  [ "$2" = / ] && return 0
  [ "$1" = "$2" ] && return 0
  case "$1" in "$2"/*) return 0 ;; esac
  return 1
}

path_overlaps() { # equality, descendant, or ancestor
  path_under "$1" "$2" || path_under "$2" "$1"
}

passwd_home() {
  local uid home
  uid=$(id -u 2>/dev/null) || return 0
  command -v getent >/dev/null 2>&1 || return 0
  home=$(getent passwd "$uid" 2>/dev/null | awk -F: 'NR == 1 { print $6 }')
  if [ -n "$home" ]; then printf '%s\n' "$home"; fi
  return 0
}

# Protected roots: the agent credential store under HOME and under the
# passwd-derived home (a poisoned HOME may only add roots), plus explicit
# agent-store relocation variables. Roots are text-only: no readlink/stat is
# performed before the actual store name is guarded. The .omp/agent
# component pair covers canonical paths reached through a symlinked home.
build_protected_roots() {
  local home lex can pi omp
  local -a homes=()
  if [ -n "${HOME:-}" ]; then homes+=("$HOME"); fi
  home=$(passwd_home)
  if [ -n "$home" ]; then homes+=("$home"); fi
  for home in "${homes[@]+"${homes[@]}"}"; do
    lex=$(lexical_abs "$home")
    PROTECTED_HOME_ROOTS+=("$lex/.omp/agent")
    pi=${PI_CONFIG_DIR:-}
    if [ -n "$pi" ]; then
      case "$pi" in
        /*) PROTECTED_HOME_ROOTS+=("$pi/agent") ;;
        *) PROTECTED_HOME_ROOTS+=("$lex/$pi/agent") ;;
      esac
    fi
  done
  pi=${PI_CODING_AGENT_DIR:-}
  if [ -n "$pi" ]; then
    case "$pi" in
      /*) PROTECTED_HOME_ROOTS+=("$(lexical_abs "$pi")") ;;
      *) for home in "${homes[@]+"${homes[@]}"}"; do
           PROTECTED_HOME_ROOTS+=("$(lexical_abs "$home/$pi")")
         done ;;
    esac
  fi
  # With the actual store names seeded, resolve each home only if its
  # lexical form does not itself reach the store. The walker refuses before
  # any readlink below the store; failures simply skip the canonical root.
  for home in "${homes[@]+"${homes[@]}"}"; do
    lex=$(lexical_abs "$home")
    if protected_component_reason "$lex" >/dev/null; then continue; fi
    if can=$(resolve_guarded "$home" 0 0 2>/dev/null); then
      if [ -n "$can" ] && [ "$can" != "$lex" ]; then
        PROTECTED_HOME_ROOTS+=("$can/.omp/agent")
        pi=${PI_CONFIG_DIR:-}
        if [ -n "$pi" ]; then
          case "$pi" in
            /*) ;;
            *) PROTECTED_HOME_ROOTS+=("$can/$pi/agent") ;;
          esac
        fi
      fi
    fi
    # A relocated ~/.omp (a symlink to another directory) needs its agent
    # child protected too. Resolve only the parent; a symlinked
    # ~/.omp/agent itself is left as a documented residual.
    if omp=$(resolve_guarded "$lex/.omp" 0 0 2>/dev/null); then
      if [ -n "$omp" ]; then
        case "$omp" in
          */agent) PROTECTED_HOME_ROOTS+=("$omp") ;;
          *) PROTECTED_HOME_ROOTS+=("$omp/agent") ;;
        esac
      fi
    fi
  done
  return 0
}

# Operator surfaces and the agent store, matched by path component. The
# boundary is a refusal list, not a general secret-class classifier.
protected_component_reason() { # $1 normalized absolute path
  local path=$1 rest c lc nxt
  local -a comps=()
  local i
  rest=${path#/}
  local IFS=/
  read -r -a comps <<< "$rest"
  for ((i = 0; i < ${#comps[@]}; i++)); do
    c=${comps[i]}
    lc=${c,,}
    nxt=${comps[i + 1]:-}
    nxt=${nxt,,}
    if [ "$lc" = .omp ] && [ "$nxt" = agent ]; then
      printf 'credential-store'; return 0
    fi
    if [ "$lc" = census ] && [[ $nxt == operator-sweep-* ]]; then
      printf 'operator-sweep'; return 0
    fi
    if [ "$lc" = .ufo ] && { [ "$nxt" = state ] || [ "$nxt" = watchdog.log ]; }; then
      printf 'operator-runtime'; return 0
    fi
  done
  return 1
}

# Component pairs plus roots that equal or contain the path. Used while
# walking a path, where intermediate prefixes are naturally ancestors of a
# protected root and must not be refused.
protected_reason_inside() { # $1 normalized absolute path
  local path=$1 reason root
  path=$(lexical_abs "$path")
  if reason=$(protected_component_reason "$path"); then
    printf '%s' "$reason"; return 0
  fi
  for root in "${PROTECTED_HOME_ROOTS[@]+"${PROTECTED_HOME_ROOTS[@]}"}"; do
    [ -n "$root" ] || continue
    if path_under "$path" "$root"; then
      printf 'credential-store'; return 0
    fi
  done
  return 1
}

# Final input predicate: equality, descendant, or ancestor (including /).
protected_reason_input() { # $1 normalized absolute path
  local path=$1 reason root
  path=$(lexical_abs "$path")
  if reason=$(protected_component_reason "$path"); then
    printf '%s' "$reason"; return 0
  fi
  for root in "${PROTECTED_HOME_ROOTS[@]+"${PROTECTED_HOME_ROOTS[@]}"}"; do
    [ -n "$root" ] || continue
    if path_overlaps "$path" "$root"; then
      printf 'credential-store'; return 0
    fi
  done
  return 1
}

# Resolve one input path component by component. Each symlink is read one
# hop and folded back into the walk, so a link whose target reaches the
# store is refused before any stat/open below the store. readlink -m is not
# used here: it would resolve suffixes inside a protected tree.
resolve_guarded() { # $1 raw, $2 allow-dotdot(0|1), $3 final-input-check(0|1)
  local raw=$1 allow=${2:-0} final=${3:-1}
  local lex rest comp candidate target reason hops=0 acc=""
  case "$raw" in
    *$'\n'*|*$'\t'*|*$'\r'*) protected_fail "ambiguous-path" input "$raw" ;;
  esac
  if [ "$allow" != 1 ]; then
    case "/$raw/" in
      *"/../"*) protected_fail "ambiguous-path" input "$raw" ;;
    esac
    lex=$(lexical_abs "$raw")
  else
    case "$raw" in
      /*) lex=$raw ;;
      *) lex="$PWD/$raw" ;;
    esac
  fi
  case "$lex" in
    *$'\n'*|*$'\t'*|*$'\r'*) protected_fail "ambiguous-path" input "$raw" ;;
  esac
  # Ancestors (and direct/descendant inputs) are refused before the first
  # stat or symlink hop. The final predicate below still re-checks the
  # resolved result for alias-shaped inputs.
  if [ "$final" = 1 ]; then
    if reason=$(protected_reason_input "$lex"); then
      protected_fail "$reason" input "$lex"
    fi
  fi
  rest=${lex#/}
  while [ -n "$rest" ]; do
    comp=${rest%%/*}
    if [ "$comp" = "$rest" ]; then rest=""; else rest=${rest#*/}; fi
    [ -n "$comp" ] || continue
    case "$comp" in
      .) continue ;;
      ..)
        if [ -z "$acc" ] || [ "$acc" = / ]; then acc=""; else acc=${acc%/*}; fi
        if reason=$(protected_reason_inside "${acc:-/}"); then
          protected_fail "$reason" path "${acc:-/}"
        fi
        continue ;;
    esac
    candidate="$acc/$comp"
    if reason=$(protected_reason_inside "$candidate"); then
      protected_fail "$reason" path "$candidate"
    fi
    # Refuse before lstat when the remaining lexical suffix already reaches
    # a protected root (for example .omp before agent, or a custom root).
    if reason=$(protected_reason_inside "$(lexical_abs "$candidate${rest:+/$rest}")"); then
      protected_fail "$reason" path "$(lexical_abs "$candidate${rest:+/$rest}")"
    fi
    if [ -L "$candidate" ]; then
      target=$(readlink -- "$candidate" 2>/dev/null) || target=""
      if [ -z "$target" ]; then
        protected_fail "unresolved-path" path "$candidate"
      fi
      case "$target" in
        *$'\n'*|*$'\t'*|*$'\r'*)
          protected_fail "ambiguous-path" path "$candidate" ;;
        /*) acc="" ;;
        *) ;;
      esac
      hops=$((hops + 1))
      if [ "$hops" -gt 40 ]; then
        protected_fail "symlink-loop" path "$raw"
      fi
      rest="$target${rest:+/$rest}"
      continue
    fi
    acc="$candidate"
  done
  if [ "$final" = 1 ]; then
    if reason=$(protected_reason_input "${acc:-/}"); then
      protected_fail "$reason" path "${acc:-/}"
    fi
  fi
  printf '%s' "${acc:-/}"
}

guard_path() { # $1 label, $2 raw path; prints the resolved path
  local resolved
  resolved=$(resolve_guarded "$2" 0 1) || exit 2
  printf '%s' "$resolved"
}

# Internal git targets (gitfile, commondir, alternates, worktree paths) may
# legitimately contain `..`; resolve them physically, still refusing a
# protected prefix.
guard_target() { # $1 label, $2 raw path; prints the resolved path
  local resolved
  resolved=$(resolve_guarded "$2" 1 1) || exit 2
  printf '%s' "$resolved"
}

guard_alternates_file() { # $1 objects dir, $2 depth
  local objdir=$1 depth=${2:-0} alt line target resolved
  if [ "$depth" -gt 5 ]; then
    protected_fail "git-alternates-depth" "$objdir" "$objdir"
  fi
  alt="$objdir/info/alternates"
  if [ -L "$alt" ]; then
    guard_target alternates "$alt" >/dev/null
    protected_fail "git-alternates-unparsed" "$objdir" "$alt"
  fi
  [ -f "$alt" ] || return 0
  while IFS= read -r line || [ -n "$line" ]; do
    [ -n "$line" ] || continue
    case "$line" in
      \#*) continue ;;
      \"*) protected_fail "git-alternates-unparsed" "$objdir" "$alt" ;;
      /*) target=$line ;;
      *) target="$objdir/$line" ;;
    esac
    resolved=$(guard_target alternates "$target") || exit 2
    guard_alternates_file "$resolved" $((depth + 1))
  done < "$alt"
}

guard_alternates() { # $1 resolved gitdir
  guard_alternates_file "$1/objects" 0
}

guard_git_links() { # $1 resolved gitdir; symlinks may not leave the gitdir
  local dir=$1 link resolved bad
  if ! bad=$(find -P "$dir" -type d ! -readable -print -quit 2>/dev/null); then
    protected_fail "git-metadata-unreadable" "$dir" "$dir"
  fi
  if [ -n "$bad" ]; then
    protected_fail "git-metadata-unreadable" "$dir" "$bad"
  fi
  while IFS= read -r -d '' link; do
    resolved=$(guard_target git-metadata "$link") || exit 2
    case "$resolved" in
      "$dir"/*) ;;
      *) protected_fail "git-metadata-symlink" "$dir" "$link" ;;
    esac
  done < <(find -P "$dir" -type l -print0 2>/dev/null || true)
}

# Fixed git metadata that git reads directly must be regular or a directory;
# a FIFO/device/socket is refused rather than opened or waited on.
# info/attributes is the sole exception (round 17, D2): a hardlink or a
# non-regular (FIFO/socket/device, or a symlink resolving to one) degrades
# that repository to an `error` row instead of aborting the fleet. The
# finding is recorded and the loop still finishes, so a hardlinked or
# non-regular alternates after it keeps its exit-2 refusal.
guard_git_files() { # $1 resolved gitdir
  local dir=$1 rel path kind nlink soft=0
  for rel in config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates; do
    path="$dir/$rel"
    # One lstat-resolved type probe before anything could open the path: a
    # FIFO or device is classified here, never touched by open(2). A failed
    # stat means absent (or a dangling symlink, which git also skips).
    # LC_ALL=C: %F is gettext-translated; GNU prints "regular empty file" for
    # a zero-length file, which is still a regular file (r17 wave-2 F1/F2).
    if ! kind=$(LC_ALL=C stat -L -c '%F %h' -- "$path" 2>/dev/null); then continue; fi
    nlink=${kind##* }
    kind=${kind% *}
    case "$kind" in
      directory) continue ;;
      'regular file'|'regular empty file')
        case "$nlink" in
          ''|*[!0-9]*) protected_fail "git-metadata-unavailable" "$dir" "$path" ;;
        esac
        if [ "$nlink" -gt 1 ]; then
          if [ "$rel" = "info/attributes" ]; then
            meta_soft "git-metadata-hardlink" "$path"
            soft=1
            continue
          fi
          protected_fail "git-metadata-hardlink" "$dir" "$path"
        fi
        ;;
      *)
        if [ "$rel" = "info/attributes" ]; then
          meta_soft "git-metadata-nonregular" "$path"
          soft=1
          continue
        fi
        protected_fail "git-metadata-nonregular" "$dir" "$path"
        ;;
    esac
  done
  [ "$soft" = 0 ] || return 1
  return 0
}

# A config-named path is checked lexically, then walked one component at a
# time. A protected reach is reported against the naming config file with
# the given reason (exit 2), so a protected target name is never echoed. A
# path that cannot be resolved but reaches nothing protected (ambiguous
# characters, dangling or looping symlink) returns 3: the caller degrades.
guard_config_path() { # $1 reason, $2 gitdir, $3 cfg, $4 absolute raw path
  local reason=$1 dir=$2 cfg=$3 raw=$4 out
  case "$raw" in
    *$'\n'*|*$'\t'*|*$'\r'*) return 3 ;;
  esac
  if protected_reason_input "$(lexical_abs "$raw")" >/dev/null; then
    protected_fail "$reason" "$dir" "$cfg"
  fi
  if out=$(resolve_guarded "$raw" 1 1 2>&1); then
    printf '%s' "$out"
    return 0
  fi
  case "$out" in
    *"$PROTECTED_FINDING: credential-store "*|*"$PROTECTED_FINDING: operator-sweep "*|*"$PROTECTED_FINDING: operator-runtime "*)
      protected_fail "$reason" "$dir" "$cfg" ;;
  esac
  return 3
}

# Expand a git pathname value: `~/` via HOME, relative to $2. `~user` and
# `%(prefix)` forms are not modelled: rc 1 (caller degrades). Callers strip
# `:(optional)` themselves where git honors it (pathname keys, not
# include.path).
expand_config_path() { # $1 value, $2 base dir; prints path, rc 1 unsupported
  local v=$1 base=$2
  case "$v" in
    \~/*) [ -n "${HOME:-}" ] || return 1; v="$HOME/${v:2}" ;;
    \~*|%\(*) return 1 ;;
    /*) ;;
    *) v="$base/$v" ;;
  esac
  printf '%s' "$v"
}

# Config that cannot be evaluated but reaches no protected path is not a
# whole-run refusal (round 16): the repository is skipped (no git command
# runs in it) and emitted as an `error` row, so unaffected rows survive.
# CFG_SOFT_REASON keeps the first reason; guard_git_surface resets it.
CFG_SOFT_REASON=""
cfg_soft() { # $1 reason; always returns 1
  [ -n "$CFG_SOFT_REASON" ] || CFG_SOFT_REASON=$1
  return 1
}

# Guarded-gitmetadata soft finding (round 17, D2): a hardlinked or
# non-regular $GIT_DIR/info/attributes cannot be opened by git safely (a
# FIFO would block status forever; a hardlink can alias into a store), so
# its repository degrades to an `error` row instead of aborting the run.
# META_SOFT_* keep the first finding; the finding is stored, not printed,
# so a repeated guard pass (list_repos, then census_one) reports once and
# a first-wins config reason cannot mask it. The scan itself continues —
# no git call that could read that file runs afterwards, so protected
# reaches elsewhere in the repo still refuse the whole run.
META_SOFT_REASON=""
META_SOFT_PATH=""
meta_soft() { # $1 reason, $2 path; always returns 1
  if [ -z "$META_SOFT_REASON" ]; then
    META_SOFT_REASON=$1
    META_SOFT_PATH=$2
  fi
  return 1
}
emit_soft_diag() { # $1 repo label; prints every stored soft finding (stderr)
  if [ -n "$META_SOFT_REASON" ]; then
    printf 'souji-census: git-metadata-unsupported %s %s\n' \
      "$META_SOFT_REASON" "$(sanitize_field "$META_SOFT_PATH")" >&2
  fi
  if [ -n "${CFG_SOFT_REASON:-}" ] || [ -z "$META_SOFT_REASON" ]; then
    printf 'souji-census: config-unsupported: %s (%s)\n' \
      "${CFG_SOFT_REASON:-git-config-unsupported}" \
      "$(sanitize_field "$1")" >&2
  fi
}

# Regular, single-link config file, else a soft refusal (never opened).
guard_config_file_kind() { # $1 resolved file
  local nlink
  if [ ! -f "$1" ]; then cfg_soft "git-include-nonregular"; return 1; fi
  nlink=$(stat -L -c %h -- "$1" 2>/dev/null || true)
  case "$nlink" in
    ''|*[!0-9]*) cfg_soft "git-config-unparsed"; return 1 ;;
  esac
  if [ "$nlink" -gt 1 ]; then cfg_soft "git-include-hardlink"; return 1; fi
  return 0
}

CFG_STACK=()
CFG_WT_ENABLED=0

# Scan one config file key by key (round 16). Includes are followed in
# place, so last-wins settings track git's own reading order. Returns 1
# (soft, CFG_SOFT_REASON set) when the file cannot be evaluated; exits 2
# when a config-named path reaches a protected root. A soft finding does not
# stop the scan, so a later protected reach still refuses the whole run.
# Relative include paths resolve against the directory of the path git
# opened (the spelled name, $4), not its symlink-resolved location.
scan_config_file() { # $1 gitdir, $2 resolved cfg, $3 depth, $4 spelled cfg path
  local dir=$1 cfg=$2 depth=$3 spelled=${4:-$2} rec key val bare sec var rest sub tgt raw s soft=0 rc
  local -a recs=()
  if [ "$depth" -gt 10 ]; then cfg_soft "git-include-depth"; return 1; fi
  for s in "${CFG_STACK[@]+"${CFG_STACK[@]}"}"; do
    if [ "$s" = "$cfg" ]; then cfg_soft "git-include-cycle"; return 1; fi
  done
  if ! tr -d '\000' < "$cfg" | cmp -s -- - "$cfg"; then
    cfg_soft "git-config-unparsed"; return 1
  fi
  if ! git config --file "$cfg" --no-includes --list -z >/dev/null 2>&1; then
    cfg_soft "git-config-unparsed"; return 1
  fi
  mapfile -d '' -t recs < <(git config --file "$cfg" --no-includes --list -z 2>/dev/null)
  CFG_STACK+=("$cfg")
  for rec in "${recs[@]+"${recs[@]}"}"; do
    if [[ $rec == *$'\n'* ]]; then
      key=${rec%%$'\n'*}; val=${rec#*$'\n'}; bare=0
    else
      key=$rec; val=""; bare=1
    fi
    sec=${key%%.*}; sec=${sec,,}
    var=${key##*.}; var=${var,,}
    rest=${key#*.}
    if [ "$rest" = "${key##*.}" ]; then sub=""; else sub=${rest%.*}; fi
    case "$sec:$var" in
      include:path|includeif:path)
        # include.path has no subsection; includeIf.<cond>.path has one.
        if [ "$sec" = include ] && [ -n "$sub" ]; then continue; fi
        if [ "$sec" = includeif ] && [ -z "$sub" ]; then continue; fi
        # A bare or empty path makes git itself fail; nothing is opened.
        if [ "$bare" = 1 ] || [ -z "$val" ]; then continue; fi
        if ! raw=$(expand_config_path "$val" "${spelled%/*}"); then
          cfg_soft "git-config-unsupported"; soft=1; continue
        fi
        tgt=$(guard_config_path include-protected "$dir" "$cfg" "$raw") || {
          rc=$?; [ "$rc" = 3 ] || exit 2
          cfg_soft "git-include-unresolved"; soft=1; continue; }
        if [ ! -e "$tgt" ]; then continue; fi
        if ! guard_config_file_kind "$tgt"; then soft=1; continue; fi
        scan_config_file "$dir" "$tgt" $((depth + 1)) "$raw" || soft=1
        ;;
      core:excludesfile|core:attributesfile)
        if [ "$bare" = 1 ] || [ -z "$val" ]; then continue; fi
        if ! tgt=$(expand_config_path "${val#:(optional)}" "${dir%/*}"); then
          cfg_soft "git-config-unsupported"; soft=1; continue
        fi
        guard_config_path git-config-unsupported "$dir" "$cfg" "$tgt" >/dev/null || {
          cfg_soft "git-config-unresolved"; soft=1; continue; }
        ;;
      core:worktree)
        if [ "$bare" = 1 ] || [ -z "$val" ]; then continue; fi
        if ! tgt=$(expand_config_path "${val#:(optional)}" "$dir"); then
          cfg_soft "git-config-unsupported"; soft=1; continue
        fi
        guard_config_path core-worktree-protected "$dir" "$cfg" "$tgt" >/dev/null || {
          cfg_soft "git-config-unresolved"; soft=1; continue; }
        ;;
      extensions:worktreeconfig)
        # git reads repository extensions from $GIT_DIR/config itself, not
        # from its includes (round 16).
        [ "$depth" = 0 ] || continue
        if [ "$bare" = 1 ]; then CFG_WT_ENABLED=1; continue; fi
        if ! s=$(git config --file "$cfg" --no-includes --type=bool --get-all "$key" 2>/dev/null); then
          cfg_soft "git-config-unparsed"; soft=1; continue
        fi
        s=${s##*$'\n'}
        if [ "$s" = true ]; then CFG_WT_ENABLED=1; else CFG_WT_ENABLED=0; fi
        ;;
      # Inert for the census, any value: core.hooksPath (status writes no
      # index, and carries -c core.hooksPath=/dev/null) and core.fsmonitor
      # (status carries -c core.fsmonitor=false, which alone disables the
      # fsmonitor hook); core.alternateRefsCommand, consumed only by
      # receive-pack ref advertisement, fetch negotiation and
      # `rev-list --alternate-refs` (no census command is one of these);
      # remote.*.promisor, remote.*.partialCloneFilter and
      # extensions.partialClone: GIT_NO_LAZY_FETCH=1 (git >= 2.45) stops
      # on-demand promisor fetches; filter drivers are checked for an
      # attributes binding before status.
    esac
  done
  unset 'CFG_STACK[${#CFG_STACK[@]}-1]'
  [ "$soft" = 0 ] || return 1
  return 0
}

# config.worktree is read by git only while extensions.worktreeConfig is
# true; it is never opened otherwise.
guard_wt_config() { # $1 resolved gitdir (main or linked admin)
  local dir=$1 wtc="$1/config.worktree"
  [ "$CFG_WT_ENABLED" = 1 ] || return 0
  if [ -L "$wtc" ]; then
    protected_fail "git-metadata-symlink" "$dir" "$wtc"
  fi
  [ -e "$wtc" ] || return 0
  local inherited=$CFG_WT_ENABLED
  guard_config_file_kind "$wtc" || return 1
  CFG_STACK=()
  # git takes extensions.worktreeConfig from the common config only; a value
  # inside config.worktree must not change which files are scanned.
  scan_config_file "$dir" "$wtc" 0 || { CFG_WT_ENABLED=$inherited; return 1; }
  CFG_WT_ENABLED=$inherited
  return 0
}

# Returns 1 (soft) when the repository's config cannot be evaluated; exits 2
# on a protected reach.
guard_git_config() { # $1 resolved gitdir, $2 optional inherited worktreeConfig (0|1)
  local dir=$1 cfg
  cfg="$dir/config"
  if [ -L "$cfg" ]; then
    protected_fail "git-metadata-symlink" "$dir" "$cfg"
  fi
  if [ -n "${2:-}" ]; then CFG_WT_ENABLED=$2; else CFG_WT_ENABLED=0; fi
  local soft=0
  if [ -f "$cfg" ]; then
    CFG_STACK=()
    scan_config_file "$dir" "$cfg" 0 || soft=1
  fi
  # A linked admin's own config is never git's extension source: keep the
  # inherited common-config value.
  if [ -n "${2:-}" ]; then CFG_WT_ENABLED=$2; fi
  guard_wt_config "$dir" || soft=1
  [ "$soft" = 0 ] || return 1
  return 0
}

# Resolve one `gitdir:` pointer to its admin directory. Prints nothing when
# the file is not a pointer. Relative targets are relative to the owning
# worktree directory.
gitfile_admin() { # $1 .git file, $2 owner dir
  local file=$1 base=$2 line target
  IFS= read -r line < "$file" || return 0
  case "$line" in
    gitdir:*) target=${line#gitdir:} ;;
    *) return 0 ;;
  esac
  target=${target#"${target%%[![:space:]]*}"}
  [ -n "$target" ] || return 0
  case "$target" in
    /*) ;;
    *) target="$base/$target" ;;
  esac
  guard_target gitdir "$target" || exit 2
}

# A .git file is a linked worktree/submodule pointer, not a row. Only its
# target is checked; the child's config is not consulted because no git
# command is run on it.
guard_git_pointer() { # $1 repo dir, $2 .git file
  local admin
  admin=$(gitfile_admin "$2" "$1") || exit 2
  [ -n "$admin" ] || return 0
}

# Registered worktree paths are guarded from the admin gitdir files before
# `git worktree list` runs, so that command cannot stat a protected path
# first. Relative registration paths are resolved against the admin dir.
guard_worktree_registrations() { # $1 resolved gitdir; rc 1 soft (all entries still guarded)
  local dir=$1 entry reg target wt admin common c soft=0
  # Dot-named admin dirs are registrations too (git lists them; r17 wave-2 F4).
  for entry in "$dir"/worktrees/* "$dir"/worktrees/.[!.]* "$dir"/worktrees/..?*; do
    if [ -L "$entry" ]; then
      guard_target worktree "$entry" >/dev/null
      continue
    fi
    [ -d "$entry" ] || continue
    reg="$entry/gitdir"
    [ -f "$reg" ] || continue
    IFS= read -r target < "$reg" || target=""
    [ -n "$target" ] || continue
    case "$target" in
      /*) ;;
      *) target="$dir/$target" ;;
    esac
    guard_target worktree "$target" >/dev/null
    case "$target" in
      */.git)
        wt=${target%/.git}
        guard_target worktree "$wt" >/dev/null
        if [ -f "$target" ]; then
          admin=$(gitfile_admin "$target" "$wt") || exit 2
          if [ -n "$admin" ]; then
            guard_git_files "$admin" || soft=1
            guard_git_links "$admin" || exit 2
            guard_git_config "$admin" "$CFG_WT_ENABLED" || soft=1
            common="$admin/commondir"
            if [ -L "$common" ]; then
              # Read a symlinked commondir through its guarded target, as git does.
              common=$(guard_target git-common-dir "$common") || exit 2
            fi
            if [ -f "$common" ]; then
              IFS= read -r c < "$common" || c=""
              c=${c#"${c%%[![:space:]]*}"}
              if [ -n "$c" ]; then
                case "$c" in
                  /*) ;;
                  *) c="$admin/$c" ;;
                esac
                guard_target git-common-dir "$c" >/dev/null
              fi
            fi
          fi
        fi
        ;;
    esac
  done
  [ "$soft" = 0 ] || return 1
  return 0
}

# Exits 2 on a protected git surface. Returns 1 (soft) when some config
# or metadata cannot be evaluated; every remaining guard still runs
# first, so a later protected reach still refuses the whole run.
guard_git_surface() { # $1 repo dir
  local repo=$1 g="$1/.git" target common dir first soft=0
  CFG_SOFT_REASON=""
  META_SOFT_REASON=""
  META_SOFT_PATH=""
  if [ -L "$g" ]; then
    guard_target git-metadata "$g" >/dev/null
    return 0
  fi
  if [ -d "$g" ]; then
    dir=$(guard_target gitdir "$g") || exit 2
    guard_git_links "$dir" || exit 2
    guard_git_files "$dir" || soft=1
    guard_git_config "$dir" || soft=1
    first=$dir
    common="$dir/commondir"
    if [ -L "$common" ]; then
      # Read a symlinked commondir through its guarded target, as git does.
      common=$(guard_target git-common-dir "$common") || exit 2
    fi
    if [ -f "$common" ]; then
      IFS= read -r target < "$common" || target=""
      target=${target#"${target%%[![:space:]]*}"}
      if [ -n "$target" ]; then
        case "$target" in
          /*) ;;
          *) target="$dir/$target" ;;
        esac
        dir=$(guard_target git-common-dir "$target") || exit 2
        guard_git_links "$dir" || exit 2
        guard_git_files "$dir" || soft=1
        guard_git_config "$dir" || soft=1
        guard_wt_config "$first" || soft=1
      fi
    fi
    guard_alternates "$dir" || exit 2
    guard_worktree_registrations "$dir" || soft=1
    [ "$soft" = 0 ] || return 1
    return 0
  fi
  if [ -f "$g" ]; then
    IFS= read -r target < "$g" || target=""
    case "$target" in
      gitdir:*) target=${target#gitdir:} ;;
      *) return 0 ;;
    esac
    target=${target#"${target%%[![:space:]]*}"}
    [ -n "$target" ] || protected_fail "unresolved-path" "$repo" "$g"
    case "$target" in
      /*) ;;
      *) target="$repo/$target" ;;
    esac
    dir=$(guard_target gitdir "$target") || exit 2
    guard_git_links "$dir" || exit 2
    guard_git_files "$dir" || soft=1
    guard_git_config "$dir" || soft=1
    first=$dir
    common="$dir/commondir"
    if [ -L "$common" ]; then
      # Read a symlinked commondir through its guarded target, as git does.
      common=$(guard_target git-common-dir "$common") || exit 2
    fi
    if [ -f "$common" ]; then
      IFS= read -r target < "$common" || target=""
      target=${target#"${target%%[![:space:]]*}"}
      if [ -n "$target" ]; then
        case "$target" in
          /*) ;;
          *) target="$dir/$target" ;;
        esac
        dir=$(guard_target git-common-dir "$target") || exit 2
        guard_git_links "$dir" || exit 2
        guard_git_files "$dir" || soft=1
        guard_git_config "$dir" || soft=1
        guard_wt_config "$first" || soft=1
      fi
    fi
    guard_alternates "$dir" || exit 2
    guard_worktree_registrations "$dir" || soft=1
  fi
  [ "$soft" = 0 ] || return 1
  return 0
}

build_protected_roots

sanitize_field() {
  local s=$1
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

# --- measurements (read-only) ----------------------------------------------

count_worktrees() { # $1 repo
  local n
  n=$(git -C "$1" worktree list 2>/dev/null | grep -c . || true)
  printf '%s' "${n// /}"
}

count_unpushed() { # $1 repo; prints "count<TAB>no-remote|has-remote"
  local repo=$1 nremotes n
  nremotes=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null \
    | grep -c . || true)
  nremotes=${nremotes// /}
  if [ "${nremotes:-0}" = 0 ]; then
    n=$(git -C "$repo" rev-list --count --branches 2>/dev/null || printf '0')
    printf '%s\tno-remote' "${n// /}"
    return 0
  fi
  n=$(git -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null || printf '0')
  printf '%s\thas-remote' "${n// /}"
}

# Effective excludes/attributes file for status (round 16): the guarded
# value git would use, else the XDG default when present and
# boundary-clean, else /dev/null. Rows before round 14 honored these files;
# round 14 forced /dev/null and so changed dirty counts. A set-but-empty
# value disables the file (git falls back to XDG only when unset); an
# `:(optional)` value whose target is missing counts as unset. rc 3: the
# value cannot be modelled (`~user`, `%(prefix)`); exit 2: protected reach.
status_info_file() { # $1 worktree, $2 key, $3 XDG leaf (ignore|attributes)
  local wt=$1 key=$2 leaf=$3 val tgt base rc=0
  val=$(git -C "$wt" config --get "$key" 2>/dev/null) || rc=$?
  if [ "$rc" = 0 ] && [ -z "$val" ]; then printf '/dev/null'; return 0; fi
  if [ "$rc" = 0 ]; then
    tgt=$(expand_config_path "${val#:(optional)}" "$wt") || return 3
    tgt=$(guard_config_path git-config-unsupported "$wt" "$key" "$tgt") || {
      rc=$?; [ "$rc" = 3 ] && return 3; exit 2; }
    case "$val" in
      ':(optional)'*) [ -e "$tgt" ] || rc=1 ;;
    esac
    # A non-regular target (FIFO, device) could block status: degrade.
    # /dev/null is git's own documented "no file" value and stays honored.
    if [ "$rc" = 0 ] && [ "$tgt" != /dev/null ] && [ -e "$tgt" ] && [ ! -f "$tgt" ]; then
      return 3
    fi
    if [ "$rc" = 0 ]; then printf '%s' "$tgt"; return 0; fi
  fi
  base=${XDG_CONFIG_HOME:-}
  if [ -z "$base" ]; then
    if [ -z "${HOME:-}" ]; then printf '/dev/null'; return 0; fi
    base="$HOME/.config"
  fi
  tgt="$base/git/$leaf"
  case "$tgt" in
    /*) ;;
    *) printf '/dev/null'; return 0 ;;
  esac
  if protected_reason_input "$(lexical_abs "$tgt")" >/dev/null; then
    printf '/dev/null'; return 0
  fi
  if tgt=$(resolve_guarded "$tgt" 1 1 2>/dev/null) && [ -f "$tgt" ]; then
    printf '%s' "$tgt"
  else
    printf '/dev/null'
  fi
}

# A filter driver command that an attributes source binds to a tracked path
# could run during status: refuse (round 16). Unbound drivers are inert.
# Neither ls-files nor check-attr runs a driver.
guard_bound_filters() { # $1 worktree, $2 effective attributes file; rc 1 bound or unknown
  local wt=$1 attrs=$2 rec name i pid
  local -a drivers=() recs=()
  mapfile -d '' -t recs < <(git -C "$wt" config -z --get-regexp \
    '^filter\..*\.(clean|smudge|process)$' 2>/dev/null || true)
  for rec in "${recs[@]+"${recs[@]}"}"; do
    # An explicitly empty value (`key\n`) defines no command; a value that
    # merely ends in a newline still does.
    case "$rec" in *$'\n'*) [ -n "${rec#*$'\n'}" ] || continue ;; esac
    name=${rec%%$'\n'*}
    name=${name#*.}
    name=${name%.*}
    drivers+=("$name")
  done
  [ "${#drivers[@]}" -gt 0 ] || return 0
  recs=()
  # Fail closed: if the attribute lookup itself fails, treat as bound.
  # Same pathspec exclusions as status, so check-attr never reads an
  # attributes file inside an operator-owned surface.
  mapfile -d '' -t recs < <(set -o pipefail; git -C "$wt" -c core.attributesFile="$attrs" \
      ls-files -z --cached -- . ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' \
      ':(exclude,glob)census/operator-sweep-*' \
      ':(exclude,glob)census/operator-sweep-*/**' \
      ':(exclude,glob)**/census/operator-sweep-*' 2>/dev/null \
    | git -C "$wt" -c core.attributesFile="$attrs" \
      check-attr -z --stdin filter 2>/dev/null)
  pid=$!
  wait "$pid" || return 1
  if [ $(( ${#recs[@]} % 3 )) != 0 ]; then return 1; fi
  for ((i = 2; i < ${#recs[@]}; i += 3)); do
    for name in "${drivers[@]}"; do
      if [ "${recs[i]}" = "$name" ]; then return 1; fi
    done
  done
  return 0
}

# Prints "count", or "unverifiable" when status cannot run safely or fails.
count_dirty() { # $1 repo; exit 2 on a protected reach
  local st ex at rc
  ex=$(status_info_file "$1" core.excludesFile ignore) || {
    rc=$?; [ "$rc" = 3 ] || exit 2; printf 'unverifiable'; return 0; }
  at=$(status_info_file "$1" core.attributesFile attributes) || {
    rc=$?; [ "$rc" = 3 ] || exit 2; printf 'unverifiable'; return 0; }
  if ! guard_bound_filters "$1" "$at"; then
    printf 'souji-census: status-skipped: filter-driver-bound (%s)\n' \
      "$(sanitize_field "$1")" >&2
    printf 'unverifiable'
    return 0
  fi
  # Explicit untracked mode (round 17, D1): a repo-local, included or
  # config.worktree `status.showUntrackedFiles=no|all` must not falsify the
  # count — the flag overrides every config scope and keeps the one-line
  # collapse of a wholly untracked directory.
  # Pathspec-exclude the off-limits driver surfaces so status does not walk
  # them.
  if ! st=$(git -C "$1" --no-optional-locks -c core.fsmonitor=false \
      -c core.hooksPath=/dev/null -c core.excludesFile="$ex" \
      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all \
      --untracked-files=normal -- . \
      ':(exclude).ufo/state' ':(exclude).ufo/watchdog.log' \
      ':(exclude,glob)census/operator-sweep-*' \
      ':(exclude,glob)census/operator-sweep-*/**' \
      ':(exclude,glob)**/census/operator-sweep-*' 2>/dev/null); then
    printf 'unverifiable'
    return 0
  fi
  if [ -z "$st" ]; then printf '0'; return 0; fi
  printf '%s' "$(printf '%s\n' "$st" | grep -c . || true)"
}

scratch_bytes() { # $1 repo
  local d="$1/.scratch"
  if [ -L "$d" ]; then printf '0'; return 0; fi
  if [ ! -e "$d" ]; then printf '0'; return 0; fi
  if [ ! -d "$d" ]; then printf '0'; return 0; fi
  # du -sb sums apparent size; -P does not follow symlinks inside .scratch.
  local line bytes
  line=$(du -sb -P -- "$d" 2>/dev/null | head -1 || true)
  bytes=${line%%[[:space:]]*}
  case "$bytes" in
    ''|*[!0-9]*) printf '0' ;;
    *) printf '%s' "$bytes" ;;
  esac
}

# Newest regular file under the work tree. One find|awk pass (no per-file
# stat spawn — kotodama .scratch is hundreds of thousands of files). Prints:
#   iso<TAB>secret-shaped|ok     or empty iso when no eligible file.
# File contents are never opened. .git, .ufo/state, .ufo/watchdog.log pruned.
newest_mtime() {
  local repo=$1 raw epoch secret iso
  # pipefail is off only for this pipeline: a permission error in find must
  # not abort the census. awk still emits a row.
  set +e
  set +o pipefail
  raw=$(cd -- "$repo" && find -P . \
      \( -name .git -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \
         -o -path './census/operator-sweep-*' \
         -o -path '*/census/operator-sweep-*' \) -prune \
      -o -type f -printf '%T@ %P\0' 2>/dev/null \
      | awk '
        BEGIN { RS="\0"; max=0; sec=0 }
        function secret_comp(c,    lc) {
          lc = tolower(c)
          if (lc == ".envrc") return 1
          if (lc ~ /\.env$/) return 1
          if (lc ~ /^\.env\./) return 1
          if (lc ~ /credential/ || lc ~ /secret/) return 1
          if (lc ~ /^id_/ || lc ~ /\.pem$/) return 1
          return 0
        }
        function secret_path(p,    n, i, a) {
          n = split(p, a, "/")
          for (i = 1; i <= n; i++) if (secret_comp(a[i])) return 1
          return 0
        }
        {
          if ($0 == "") next
          ep = $0; sub(/ .*/, "", ep)
          p = $0; sub(/^[^ ]+ /, "", p)
          if (p == "") next
          if (secret_path(p)) { sec = 1; next }
          if (ep+0 > max) max = ep+0
        }
        END { printf "%d\t%s\n", int(max), (sec ? "secret-shaped" : "ok") }
      ')
  set -o pipefail
  set -e
  epoch=${raw%%$'\t'*}
  secret=${raw#*$'\t'}
  secret=${secret%%$'\n'*}
  case "$epoch" in
    ''|*[!0-9]*) epoch=0; secret=${secret:-ok} ;;
  esac
  if [ "$epoch" = 0 ]; then
    iso=""
  else
    iso=$(date -d "@$epoch" --iso-8601=seconds 2>/dev/null || true)
  fi
  if [ "$secret" = secret-shaped ]; then
    printf '%s\tsecret-shaped' "$iso"
  else
    printf '%s\tok' "$iso"
  fi
}

# Non-main worktree side flags. Prints zero or more of: wt-absent wt-dirty
# separated by spaces. Does not status a missing directory.
worktree_extra_flags() {
  local repo=$1 line path crepo cpath saw_absent=0 saw_dirty=0 d
  crepo=$repo
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      'worktree '*) path=${line#worktree } ;;
      *) continue ;;
    esac
    [ -n "$path" ] || continue
    case "$path" in
      *$'\n'*|*$'\t'*|*$'\r'*) protected_fail "ambiguous-path" "$repo" "$path" ;;
    esac
    cpath=$(guard_target worktree "$path") || exit 2
    [ "$cpath" = "$crepo" ] && continue
    if [ ! -e "$cpath" ]; then
      saw_absent=1
      continue
    fi
    if [ -L "$cpath/.git" ]; then
      guard_target git-metadata "$cpath/.git" >/dev/null
      saw_dirty=1
      continue
    fi
    if [ ! -e "$cpath/.git" ]; then
      # Never let git discover an ancestor repository from a broken
      # worktree registration.
      saw_dirty=1
      continue
    fi
    if ! guard_git_surface "$cpath"; then
      emit_soft_diag "$cpath"
      saw_dirty=1
      continue
    fi
    d=$(count_dirty "$cpath") || exit 2
    if [ "$d" = unverifiable ] || [ "${d:-0}" -gt 0 ]; then
      saw_dirty=1
    fi
  done < <(git -C "$repo" worktree list --porcelain 2>/dev/null || true)
  local out=""
  [ "$saw_absent" = 1 ] && out="wt-absent"
  [ "$saw_dirty" = 1 ] && out="${out:+$out }wt-dirty"
  printf '%s' "$out"
}

# Emit one TSV row (no newline issues; fields already sanitized).
census_one() { # $1 repo-dir
  local repo
  repo=$(guard_path repo "$1") || exit 2
  if ! guard_git_surface "$repo"; then
    emit_soft_diag "$repo"
    printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"
    return 0
  fi
  if [ -L "$repo/.git" ]; then
    printf '%s\t0\t0\t0\t0\t\tnot-a-repo\n' "$(sanitize_field "$repo")"
    return 0
  fi
  if [ ! -e "$repo/.git" ] && [ ! -d "$repo/.git" ]; then
    # Linked work trees have a .git file; bare dirs are not repos.
    if [ ! -e "$repo/.git" ]; then
      printf '%s\t0\t0\t0\t0\t\tnot-a-repo\n' "$(sanitize_field "$repo")"
      return 0
    fi
  fi
  if ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"
    return 0
  fi

  local wt unp_line unp remote_flag dirty scratch mt_line iso secret_flag wt_extra
  local -a flags=()
  wt=$(count_worktrees "$repo")
  unp_line=$(count_unpushed "$repo")
  unp=${unp_line%%$'\t'*}
  remote_flag=${unp_line#*$'\t'}
  dirty=$(count_dirty "$repo") || exit 2
  scratch=$(scratch_bytes "$repo")
  wt_extra=$(worktree_extra_flags "$repo") || exit 2
  mt_line=$(newest_mtime "$repo")
  iso=${mt_line%%$'\t'*}
  secret_flag=${mt_line#*$'\t'}

  case "$wt" in ''|*[!0-9]*) wt=0; flags+=(error) ;; esac
  case "$unp" in ''|*[!0-9]*) unp=0; flags+=(error) ;; esac
  case "$scratch" in ''|*[!0-9]*) scratch=0; flags+=(error) ;; esac

  if [ "$remote_flag" = no-remote ]; then flags+=(no-remote); fi
  if [ "${unp:-0}" -gt 0 ]; then flags+=(unpushed); fi
  case "$wt_extra" in
    *wt-absent*) flags+=(wt-absent) ;;
  esac
  case "$wt_extra" in
    *wt-dirty*) flags+=(wt-dirty) ;;
  esac
  if [ "$dirty" = unverifiable ]; then
    dirty=0
    flags+=(status-unverifiable)
  elif [ "${dirty:-0}" -gt 0 ]; then
    flags+=(dirty)
  fi
  if [ "${scratch:-0}" -gt 0 ]; then flags+=(scratch); fi
  if [ "$secret_flag" = secret-shaped ]; then flags+=(secret-shaped); fi

  local has_problem=0 f
  for f in "${flags[@]+"${flags[@]}"}"; do
    case "$f" in
      dirty|unpushed|no-remote|status-unverifiable|error|not-a-repo) has_problem=1 ;;
    esac
  done
  if [ "$has_problem" = 0 ]; then flags+=(clean); fi

  # Stable flag order.
  local ordered=""
  local name
  for name in clean dirty unpushed no-remote scratch secret-shaped wt-absent wt-dirty status-unverifiable not-a-repo error; do
    for f in "${flags[@]+"${flags[@]}"}"; do
      if [ "$f" = "$name" ]; then
        if [ -z "$ordered" ]; then ordered=$name; else ordered="$ordered,$name"; fi
      fi
    done
  done

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(sanitize_field "$repo")" "$wt" "$unp" "$dirty" "$scratch" \
    "$(sanitize_field "$iso")" "$(sanitize_field "$ordered")"
}

list_repos() { # $1 resolved root; fills REPOS, basename-sorted
  local root=$1
  local d g base last
  REPOS=()
  GUARD_CANDIDATES=()
  GUARD_KINDS=()
  if [ "$INCLUDE_ROOT" = 1 ] && [ "$ROOT_RAW_IS_SYMLINK" = 0 ] && [ -d "$root" ]; then
    g="$root/.git"
    if [ -L "$g" ]; then
      GUARD_CANDIDATES+=("$root")
      GUARD_KINDS+=(symlink)
    elif [ -f "$g" ]; then
      GUARD_CANDIDATES+=("$root")
      GUARD_KINDS+=(repo)
      REPOS+=("$root")
    elif [ -d "$g" ]; then
      GUARD_CANDIDATES+=("$root")
      GUARD_KINDS+=(repo)
      REPOS+=("$root")
    fi
  fi
  shopt -s nullglob
  for d in "$root"/*; do
    base=${d##*/}
    case "$base" in
      .*) continue ;;
    esac
    case "$base" in
      *$'\n'*|*$'\t'*|*$'\r'*)
        printf 'souji-census: skipped-ambiguous-name %s\n' \
          "$(sanitize_field "$d")" >&2
        continue ;;
    esac
    GUARD_CANDIDATES+=("$d")
    GUARD_KINDS+=(path)
    if [ -L "$d" ] || [ ! -d "$d" ]; then continue; fi
    g="$d/.git"
    last=$((${#GUARD_KINDS[@]} - 1))
    if [ -L "$g" ]; then
      GUARD_KINDS[last]=symlink
      continue
    fi
    if [ -f "$g" ]; then
      GUARD_KINDS[last]=gitfile
      continue
    fi
    if [ -d "$g" ]; then
      GUARD_KINDS[last]=repo
      REPOS+=("$d")
    fi
  done
  shopt -u nullglob
  if [ "${#REPOS[@]}" -gt 0 ]; then
    mapfile -t REPOS < <(printf '%s\n' "${REPOS[@]}" | LC_ALL=C sort)
  fi
}

guard_repo_candidate() { # $1 candidate path, $2 parent-classified kind
  local repo=$1 kind=$2 rc reason
  if reason=$(protected_reason_input "$repo"); then
    protected_fail "$reason" candidate "$repo"
  fi
  case "$kind" in
    repo)
      if guard_git_surface "$repo"; then return 0; else rc=$?; fi
      [ "$rc" = 1 ] && return 0
      return "$rc"
      ;;
    gitfile) guard_git_pointer "$repo" "$repo/.git" ;;
    symlink) guard_target git-metadata "$repo/.git" >/dev/null ;;
    path) return 0 ;;
    *) return 1 ;;
  esac
}


proc_state() { # $1 PID; sets PROC_STATE, returning 1 when absent
  local stat_line
  PROC_STATE=""
  if IFS= read -r stat_line 2>/dev/null < "/proc/$1/stat"; then
    stat_line=${stat_line##*) }
    PROC_STATE=${stat_line%% *}
    return 0
  fi
  return 1
}

run_repo_with_watchdog() { # repo, stdout file, stderr file, command and arguments
  local repo=$1 row_file=$2 stderr_file=$3 worker watchdog rc state_path parent_pid
  local dead=0 waited=0 ticks=0 timeout_ticks=0 elapsed_ticks=0 poll_count=0
  shift 3
  if ! state_path=$(mktemp -d "$CENSUS_TMP/watchdog.XXXXXX"); then return 1; fi
  REPO_TIMED_OUT=0
  REPO_UNREAPED=0
  CURRENT_REPO=$repo
  set -m
  "$@" > "$row_file" 2> "$stderr_file" &
  worker=$! CURRENT_WORKER_PGID=$!
  set +m
  parent_pid=$BASHPID
  setsid bash -c '
    pgid=$1
    limit=$2
    state_path=$3
    parent_pid=$4
    tmpdir=$5
    elapsed=0
    while [ "$elapsed" -lt "$limit" ]; do
      kill -0 -- "-$pgid" 2>/dev/null || exit 0
      sleep 1
      elapsed=$((elapsed + 1))
    done
    kill -0 -- "-$pgid" 2>/dev/null || exit 0
    : > "$state_path/timed_out" 2>/dev/null || true
    kill -TERM -- "-$pgid" 2>/dev/null || true
    sleep 2
    kill -KILL -- "-$pgid" 2>/dev/null || true
    : > "$state_path/killed" 2>/dev/null || true
    parent_state=""
    if IFS= read -r parent_stat 2>/dev/null < "/proc/$parent_pid/stat"; then
      parent_stat=${parent_stat##*) }
      parent_state=${parent_stat%% *}
    fi
    case "$parent_state" in
      ""|Z|X) rm -rf -- "$tmpdir" ;;
    esac
  ' souji-census-watchdog "$worker" "$REPO_TIMEOUT" "$state_path" \
    "$parent_pid" "$CENSUS_TMP" >/dev/null 2>&1 &
  watchdog=$! CURRENT_WATCHDOG_PID=$!

  while [ "$dead" = 0 ]; do
    if proc_state "$worker"; then
      case "$PROC_STATE" in Z|X) dead=1 ;; esac
    else
      dead=1
    fi
    elapsed_ticks=$((elapsed_ticks + 1))
    if [ -f "$state_path/timed_out" ]; then
      REPO_TIMED_OUT=1
      if [ -f "$state_path/killed" ]; then
        ticks=$((ticks + 1))
        if [ "$ticks" -ge 30 ]; then REPO_UNREAPED=1; break; fi
      else
        timeout_ticks=$((timeout_ticks + 1))
        if [ "$timeout_ticks" -ge 50 ]; then REPO_UNREAPED=1; break; fi
      fi
    elif [ "$elapsed_ticks" -ge $((REPO_TIMEOUT * 10 + 50)) ]; then
      REPO_UNREAPED=1
      break
    fi
    if [ "$dead" = 0 ] && [ "$REPO_UNREAPED" = 0 ]; then
      poll_count=$((poll_count + 1))
      if [ "$poll_count" -le 20 ]; then sleep 0.01; else sleep 0.1; fi
    fi
  done
  if [ "$dead" = 1 ]; then
    if wait "$worker"; then rc=0; else rc=$?; fi
    waited=1
    CURRENT_WORKER_PGID=""
  else
    rc=124
  fi

  if [ "$REPO_TIMED_OUT" = 0 ]; then
    if [ "$REPO_UNREAPED" = 1 ]; then
      kill -TERM -- "-$worker" 2>/dev/null || true
      sleep 0.1
      kill -KILL -- "-$worker" 2>/dev/null || true
      ticks=0
      while [ "$dead" = 0 ] && [ "$ticks" -lt 30 ]; do
        if proc_state "$worker"; then
          case "$PROC_STATE" in Z|X) dead=1 ;; esac
        else
          dead=1
        fi
        [ "$dead" = 1 ] || sleep 0.1
        ticks=$((ticks + 1))
      done
      if [ "$dead" = 1 ] && [ "$waited" = 0 ]; then
        if wait "$worker"; then rc=0; else rc=$?; fi
        waited=1
        CURRENT_WORKER_PGID=""
      fi
    fi
    kill -KILL -- "-$watchdog" 2>/dev/null || true
    wait "$watchdog" 2>/dev/null || true
    CURRENT_WATCHDOG_PID=""
    cat -- "$stderr_file" >&2
    if [ "$REPO_UNREAPED" = 1 ]; then
      printf 'souji-census: repo-timeout-unreaped %s\n' \
        "$(sanitize_field "$repo")" >&2
    fi
    rm -rf -- "$state_path"
    CURRENT_REPO=""
    if [ "$REPO_UNREAPED" = 1 ] && [ "$rc" != 2 ]; then return 1; fi
    return "$rc"
  fi

  ticks=0
  while [ ! -f "$state_path/killed" ] && [ "$ticks" -lt 30 ]; do
    sleep 0.1
    ticks=$((ticks + 1))
  done
  if [ ! -f "$state_path/killed" ]; then
    kill -KILL -- "-$worker" 2>/dev/null || true
    REPO_UNREAPED=1
  fi
  if [ "$dead" = 0 ] && [ "$REPO_UNREAPED" = 0 ]; then
    ticks=0
    while [ "$ticks" -lt 30 ]; do
      if proc_state "$worker"; then
        case "$PROC_STATE" in Z|X) dead=1; break ;; esac
      else
        dead=1
        break
      fi
      sleep 0.1
      ticks=$((ticks + 1))
    done
    if [ "$dead" = 1 ]; then
      if wait "$worker"; then rc=0; else rc=$?; fi
      waited=1
      CURRENT_WORKER_PGID=""
    else
      REPO_UNREAPED=1
    fi
  fi
  if [ "$dead" = 1 ] && [ "$REPO_UNREAPED" = 0 ]; then
    ticks=0
    while kill -0 -- "-$worker" 2>/dev/null && [ "$ticks" -lt 30 ]; do
      sleep 0.1
      ticks=$((ticks + 1))
    done
    if kill -0 -- "-$worker" 2>/dev/null; then REPO_UNREAPED=1; fi
  fi
  wait "$watchdog" 2>/dev/null || true
  CURRENT_WATCHDOG_PID=""
  cat -- "$stderr_file" >&2
  if [ "$REPO_UNREAPED" = 1 ]; then
    printf 'souji-census: repo-timeout-unreaped %s\n' \
      "$(sanitize_field "$repo")" >&2
  fi
  rm -rf -- "$state_path"
  CURRENT_REPO=""
  if [ "$rc" = 2 ]; then
    REPO_TIMED_OUT=0
    return 2
  fi
  return 124
}

emit_census() {
  local root repo row rc row_file stderr_file kind i
  local -A preflight_timeout=()
  root=$(guard_path root "$ROOT") || exit 2
  [ -d "$root" ] || { printf 'souji-census: root is not a directory: %s\n' "$root" >&2; exit 1; }
  ROOT_RAW_IS_SYMLINK=0
  if [ -L "$ROOT" ]; then ROOT_RAW_IS_SYMLINK=1; fi
  list_repos "$root"
  prepare_census_tmp

  # Guard all candidate surfaces before any census Git commands run. Parent
  # discovery classifies metadata only; guarded content reads happen below.
  for ((i = 0; i < ${#GUARD_CANDIDATES[@]}; i++)); do
    repo=${GUARD_CANDIDATES[i]}
    kind=${GUARD_KINDS[i]}
    row_file=$(mktemp "$CENSUS_TMP/guard.XXXXXX")
    stderr_file=$(mktemp "$CENSUS_TMP/stderr.XXXXXX")
    if run_repo_with_watchdog "$repo" "$row_file" "$stderr_file" \
      guard_repo_candidate "$repo" "$kind"; then
      :
    else
      rc=$?
      rm -f -- "$row_file" "$stderr_file"
      if [ "$rc" = 2 ]; then exit 2; fi
      if [ "$REPO_TIMED_OUT" = 1 ]; then
        printf 'souji-census: repo-timeout %ss %s\n' \
          "$REPO_TIMEOUT" "$(sanitize_field "$repo")" >&2
        if [ "$kind" = repo ] || [ "$kind" = gitfile ]; then
          preflight_timeout["$repo"]=1
          if [ "$kind" = gitfile ]; then REPOS+=("$repo"); fi
        fi
      else
        printf 'souji-census: census failed for %s (rc=%s)\n' "$repo" "$rc" >&2
        exit 1
      fi
      continue
    fi
    rm -f -- "$row_file" "$stderr_file"
  done
  if [ "${#REPOS[@]}" -gt 0 ]; then
    mapfile -t REPOS < <(printf '%s\n' "${REPOS[@]}" | LC_ALL=C sort -u)
  fi

  local -a rows=()
  for repo in "${REPOS[@]+"${REPOS[@]}"}"; do
    if [ "${preflight_timeout[$repo]+x}" = x ]; then
      row="$(sanitize_field "$repo")"$'\t0\t0\t0\t0\t\terror'
      rows+=("$row")
      continue
    fi
    row_file=$(mktemp "$CENSUS_TMP/repo.XXXXXX")
    stderr_file=$(mktemp "$CENSUS_TMP/stderr.XXXXXX")
    if run_repo_with_watchdog "$repo" "$row_file" "$stderr_file" census_one "$repo"; then
      row=$(<"$row_file")
      rows+=("$row")
    else
      rc=$?
      rm -f -- "$row_file" "$stderr_file"
      if [ "$rc" = 2 ]; then exit 2; fi
      if [ "$REPO_TIMED_OUT" = 1 ]; then
        printf 'souji-census: repo-timeout %ss %s\n' \
          "$REPO_TIMEOUT" "$(sanitize_field "$repo")" >&2
        row="$(sanitize_field "$repo")"$'\t0\t0\t0\t0\t\terror'
        rows+=("$row")
      else
        printf 'souji-census: census failed for %s (rc=%s)\n' "$repo" "$rc" >&2
        exit 1
      fi
      continue
    fi
    rm -f -- "$row_file" "$stderr_file"
  done
  printf '%s\n' "$HEADER"
  for row in "${rows[@]+"${rows[@]}"}"; do
    printf '%s\n' "$row"
  done
}

# --- compare ---------------------------------------------------------------

# Load a census TSV into parallel arrays keyed by repo. Caller supplies the
# namerefs. The header must be the FIRST line of the file and match exactly:
# an empty, blank-led or malformed baseline is a hard error (exit 2) — a
# corrupt previous census must never look like "no diff". Blank lines AFTER
# the header are skipped.
load_census() { # $1 file, $2 assoc-nameref of "repo -> rest-of-row"
  local file=$1
  local -n _map=$2
  file=$(guard_path compare "$file") || exit 2
  case "$file" in
    /proc/*|/dev/fd/*|/dev/stdin|/dev/stdout|/dev/stderr)
      protected_fail "special-path" compare "$file" ;;
  esac
  [ -f "$file" ] || usage_err "compare file not found: $file"
  [ -r "$file" ] || usage_err "compare file unreadable: $file"
  local nlink
  nlink=$(stat -c %h -- "$file" 2>/dev/null || true)
  case "$nlink" in
    ''|*[!0-9]*) usage_err "compare file metadata unavailable: $file" ;;
  esac
  if [ "$nlink" -gt 1 ]; then
    printf 'souji-census: %s: hardlinked-compare (%s)\n' \
      "$PROTECTED_FINDING" "$file" >&2
    exit 2
  fi
  local line n=0 repo rest saw_header=0 stripped tabs i v
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    line=${line%$'\r'}
    if [ "$saw_header" = 0 ]; then
      if [ "$line" != "$HEADER" ]; then
        usage_err "compare file header mismatch (want 7 census columns)"
      fi
      saw_header=1
      continue
    fi
    [ -n "$line" ] || continue
    stripped=${line//$'\t'/}
    tabs=$(( ${#line} - ${#stripped} ))
    if [ "$tabs" -ne 6 ]; then
      usage_err "compare file: line $n has $((tabs + 1)) columns (want 7)"
    fi
    repo=${line%%$'\t'*}
    rest=${line#*$'\t'}
    [ -n "$repo" ] || usage_err "compare file: empty repo on line $n"
    for i in 1 2 3 4; do
      v=$(field_at "$rest" "$i")
      case "$v" in
        ''|*[!0-9]*) usage_err "compare file: column $((i + 1)) is not numeric on line $n" ;;
      esac
    done
    if [ -n "${_map[$repo]+x}" ]; then
      usage_err "compare file: duplicate repo $repo"
    fi
    _map["$repo"]=$rest
  done < "$file"
  [ "$saw_header" = 1 ] || usage_err "compare file header mismatch (want 7 census columns)"
}

field_at() { # $1 rest-of-row (6 fields), $2 1-based index among those 6
  local rest=$1 idx=$2 i=1 part
  while [ "$i" -le 6 ]; do
    if [ "$i" -eq 6 ]; then
      part=$rest
    else
      part=${rest%%$'\t'*}
      rest=${rest#*$'\t'}
    fi
    if [ "$i" -eq "$idx" ]; then printf '%s' "$part"; return 0; fi
    i=$((i + 1))
  done
}

numeric_change() { # $1 before $2 after -> +N / -N / 0
  local b=$1 a=$2
  case "$b" in ''|*[!0-9-]*) printf 'non-numeric'; return 0 ;; esac
  case "$a" in ''|*[!0-9-]*) printf 'non-numeric'; return 0 ;; esac
  local d=$((a - b))
  if [ "$d" -gt 0 ]; then printf '+%s' "$d"
  elif [ "$d" -lt 0 ]; then printf '%s' "$d"
  else printf '0'
  fi
}

emit_compare() { # census of $ROOT vs $COMPARE; writes diff TSV; exit 3 if any change
  local -A before=() after=()
  local root
  root=$(guard_path root "$ROOT") || exit 2
  [ -d "$root" ] || { printf 'souji-census: root is not a directory: %s\n' "$root" >&2; exit 1; }
  load_census "$COMPARE" before
  CENSUS_TMP=$(mktemp -d /var/tmp/souji-census-now.XXXXXX)
  trap cleanup_census_tmp EXIT
  emit_census > "$CENSUS_TMP/now.tsv"
  load_census "$CENSUS_TMP/now.tsv" after
  cleanup_census_tmp
  CENSUS_TMP=""
  trap - EXIT

  printf '%s\n' "$DIFF_HEADER"
  local changes=0 repo rest_b rest_a
  local -a repos=()
  for repo in "${!before[@]}"; do repos+=("$repo"); done
  for repo in "${!after[@]}"; do
    if [ -z "${before[$repo]+x}" ]; then repos+=("$repo"); fi
  done
  local sorted
  sorted=$(printf '%s\n' "${repos[@]}" | LC_ALL=C sort -u)

  local name i before_v after_v chg
  local -a names=(worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    if [ -z "${before[$repo]+x}" ]; then
      printf '%s\trepo\tABSENT\tPRESENT\tadded\n' "$(sanitize_field "$repo")"
      changes=$((changes + 1))
      continue
    fi
    if [ -z "${after[$repo]+x}" ]; then
      printf '%s\trepo\tPRESENT\tABSENT\tremoved\n' "$(sanitize_field "$repo")"
      changes=$((changes + 1))
      continue
    fi
    rest_b=${before[$repo]}
    rest_a=${after[$repo]}
    [ "$rest_b" = "$rest_a" ] && continue
    for i in 1 2 3 4 5 6; do
      before_v=$(field_at "$rest_b" "$i")
      after_v=$(field_at "$rest_a" "$i")
      [ "$before_v" = "$after_v" ] && continue
      name=${names[$((i - 1))]}
      case "$name" in
        worktrees|unpushed|dirty|scratch_bytes) chg=$(numeric_change "$before_v" "$after_v") ;;
        *) chg=changed ;;
      esac
      printf '%s\t%s\t%s\t%s\t%s\n' \
        "$(sanitize_field "$repo")" "$name" \
        "$(sanitize_field "$before_v")" "$(sanitize_field "$after_v")" "$chg"
      changes=$((changes + 1))
    done
  done <<< "$sorted"

  if [ "$changes" -gt 0 ]; then return 3; fi
  return 0
}

# --- selftest --------------------------------------------------------------

ST_PASS=0
ST_FAIL=0
ST_TMP=""

st_note() { printf '%s\n' "$*"; }

st_ok() { ST_PASS=$((ST_PASS + 1)); st_note "PASS $*"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $*"; }

st_commit() { # $1 repo, $2 parent-or-empty, $3 msg -> sha
  local repo=$1 parent=$2 msg=$3 tr sha
  git -C "$repo" add -A >/dev/null
  tr=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -c user.name=souji-census \
      -c user.email=souji@example.invalid -C "$repo" commit-tree "$tr" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -c user.name=souji-census \
      -c user.email=souji@example.invalid -C "$repo" commit-tree "$tr")
  fi
  printf '%s' "$sha"
}

st_init() { # $1 path $2 branch
  git init -q --initial-branch="$2" "$1"
  git -C "$1" symbolic-ref HEAD "refs/heads/$2"
}

st_row_field() { # $1 tsv $2 repo-basename $3 1-based column (1=repo)
  local tsv=$1 base=$2 col=$3 line
  line=$(grep -F "/$base"$'\t' "$tsv" | head -1 || true)
  # also match a repo whose path ends with /base exactly (grep above does)
  [ -n "$line" ] || { printf ''; return 0; }
  local i=1 rest=$line part
  while [ "$i" -le 7 ]; do
    if [ "$i" -eq 7 ]; then part=$rest; else part=${rest%%$'\t'*}; rest=${rest#*$'\t'}; fi
    if [ "$i" -eq "$col" ]; then printf '%s' "$part"; return 0; fi
    i=$((i + 1))
  done
}

st_proc_pgid() { # $1 PID; prints its observed process-group id
  local stat_line stat_tail pgid
  IFS= read -r stat_line 2>/dev/null < "/proc/$1/stat" || return 1
  stat_tail=${stat_line##*) }
  read -r _ _ pgid _ <<< "$stat_tail"
  printf '%s' "$pgid"
}


st_worker_tmpdir() { # worker PGID -> CENSUS_TMP via its private stdout file
  local path
  path=$(readlink -- "/proc/$1/fd/1" 2>/dev/null) || return 1
  case "$path" in
    /var/tmp/souji-census-now.*/*) printf '%s' "${path%/*}" ;;
    *) return 1 ;;
  esac
}

st_pid_gone() { # $1 PID, $2 tenths-of-a-second bound
  local pid=$1 limit=$2 tick
  for ((tick = 0; tick < limit; tick++)); do
    [ ! -e "/proc/$pid" ] && return 0
    sleep 0.1
  done
  [ ! -e "/proc/$pid" ]
}

run_selftest() {
  if [ "${SOUJI_CENSUS_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'souji-census: refusing nested --selftest\n' >&2
    exit 1
  fi
  ST_TMP=$(mktemp -d /var/tmp/souji-census-selftest.XXXXXX)
  trap 'rm -rf -- "$ST_TMP"' EXIT
  # Round 16: the census honors the XDG excludes/attributes default; pin it
  # to an absent scratch path so host files cannot change selftest rows.
  export XDG_CONFIG_HOME="$ST_TMP/no-xdg-config"
  REPO_TIMEOUT=600
  export SOUJI_CENSUS_REPO_TIMEOUT="$REPO_TIMEOUT"
  local fleet="$ST_TMP/fleet"
  mkdir -p "$fleet"

  # clean-shokunin: 1 commit, origin/master at that tip, empty tree otherwise
  local RC="$fleet/clean-shokunin"
  st_init "$RC" master
  printf 'kept\n' > "$RC/kept.txt"
  local c1
  c1=$(st_commit "$RC" "" "c1 kept")
  git -C "$RC" update-ref refs/heads/master "$c1"
  git -C "$RC" update-ref refs/remotes/origin/master "$c1"
  git -C "$RC" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

  # dirty-shokunin: pushed tip + untracked file + a .scratch payload
  local RD="$fleet/dirty-shokunin"
  st_init "$RD" master
  printf 'base\n' > "$RD/base.txt"
  local d1
  d1=$(st_commit "$RD" "" "d1 base")
  git -C "$RD" update-ref refs/heads/master "$d1"
  git -C "$RD" update-ref refs/remotes/origin/master "$d1"
  printf 'dirt\n' > "$RD/untracked.txt"
  mkdir -p "$RD/.scratch"
  printf 'scratch-payload\n' > "$RD/.scratch/note.txt"
  # secret-shaped name: must be flagged and never opened
  printf 'SUPER-SECRET-TOKEN-do-not-print\n' > "$RD/.scratch/credentials.env"

  # unpushed-shokunin: origin tip at u1, local master at u2 (1 unpushed)
  local RU="$fleet/unpushed-shokunin"
  st_init "$RU" master
  printf 'u1\n' > "$RU/a.txt"
  local u1
  u1=$(st_commit "$RU" "" "u1")
  git -C "$RU" update-ref refs/remotes/origin/master "$u1"
  printf 'u2\n' > "$RU/b.txt"
  local u2
  u2=$(st_commit "$RU" "$u1" "u2 local only")
  git -C "$RU" update-ref refs/heads/master "$u2"

  # linked worktree (present, dirty) + one absent registration.
  # worktrees must be 3. Neither is its own census row.
  local WT="$fleet/unpushed-shokunin-wt"
  mkdir -p "$RU/.git/worktrees/wt1" "$RU/.git/worktrees/wt-absent"
  printf 'ref: refs/heads/master\n' > "$RU/.git/worktrees/wt1/HEAD"
  printf '../..\n' > "$RU/.git/worktrees/wt1/commondir"
  printf '%s\n' "$WT/.git" > "$RU/.git/worktrees/wt1/gitdir"
  mkdir -p "$WT"
  printf 'gitdir: %s\n' "$RU/.git/worktrees/wt1" > "$WT/.git"
  printf 'wt\n' > "$WT/from-wt.txt"
  printf '%s\n' "$u2" > "$RU/.git/worktrees/wt-absent/HEAD"
  printf '../..\n' > "$RU/.git/worktrees/wt-absent/commondir"
  printf '%s\n' "$ST_TMP/missing-wt/.git" > "$RU/.git/worktrees/wt-absent/gitdir"

  # noremote-shokunin: local commit, no refs/remotes
  local RN="$fleet/noremote-shokunin"
  st_init "$RN" master
  printf 'solo\n' > "$RN/solo.txt"
  local n1
  n1=$(st_commit "$RN" "" "n1")
  git -C "$RN" update-ref refs/heads/master "$n1"

  # not a repo: must be skipped (no .git)
  mkdir -p "$fleet/plain-dir"
  printf 'nope\n' > "$fleet/plain-dir/x.txt"

  # dot-dir with a .git must be skipped (operator/config shaped)
  mkdir -p "$fleet/.hidden-shokunin"
  st_init "$fleet/.hidden-shokunin" master

  # forbidden-surface sentinels, committed so they do not inflate dirty.
  # Touched into the future below: newest-file must still ignore them.
  mkdir -p "$RC/.ufo/state"
  printf 'watchdog-secret\n' > "$RC/.ufo/watchdog.log"
  printf 'state-secret\n' > "$RC/.ufo/state/live.json"
  local c2
  c2=$(st_commit "$RC" "$c1" "c2 sentinels")
  git -C "$RC" update-ref refs/heads/master "$c2"
  git -C "$RC" update-ref refs/remotes/origin/master "$c2"
  touch -d 'tomorrow' "$RC/.ufo/watchdog.log" "$RC/.ufo/state/live.json"

  local out1="$ST_TMP/c1.tsv" out2="$ST_TMP/c2.tsv"
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" > "$out1"
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" > "$out2"

  if cmp -s "$out1" "$out2"; then
    st_ok "repeat: two runs byte-identical"
  else
    st_bad "repeat: runs differ"; diff -u "$out1" "$out2" || true
  fi

  local hdr
  hdr=$(head -1 "$out1")
  if [ "$hdr" = "$HEADER" ]; then st_ok "header matches contract"
  else st_bad "header '$hdr'"; fi

  local nrows
  nrows=$(grep -c $'\t' "$out1" || true)
  # header + 4 main repos. plain-dir, dot-dir, and the linked work tree
  # (.git file) are not rows.
  local data_rows
  data_rows=$((nrows - 1))
  if [ "$data_rows" = 4 ]; then st_ok "row count 4 (main repos only)"
  else st_bad "row count $data_rows want 4"; cat "$out1"; fi

  if grep -q 'plain-dir' "$out1"; then st_bad "plain-dir was included"; else st_ok "plain-dir skipped"; fi
  if grep -q 'hidden-shokunin' "$out1"; then st_bad "dot-dir was included"; else st_ok "dot-dir skipped"; fi
  if grep -q 'unpushed-shokunin-wt' "$out1"; then st_bad "linked worktree emitted as its own row"
  else st_ok "linked worktree not a separate row"; fi

  local v kept_iso
  kept_iso=$(date -d "@$(stat -c %Y -- "$RC/kept.txt")" --iso-8601=seconds)
  v=$(st_row_field "$out1" clean-shokunin 7)
  case "$v" in
    clean) st_ok "clean-shokunin verdict=clean ($v)" ;;
    *) st_bad "clean-shokunin verdict='$v' want clean" ;;
  esac
  v=$(st_row_field "$out1" clean-shokunin 2)
  if [ "$v" = 1 ]; then st_ok "clean worktrees=1"; else st_bad "clean worktrees=$v"; fi
  v=$(st_row_field "$out1" clean-shokunin 3)
  if [ "$v" = 0 ]; then st_ok "clean unpushed=0"; else st_bad "clean unpushed=$v"; fi
  v=$(st_row_field "$out1" clean-shokunin 4)
  if [ "$v" = 0 ]; then st_ok "clean dirty=0"; else st_bad "clean dirty=$v"; fi

  # default porcelain collapses untracked .scratch/ to one line, plus untracked.txt
  v=$(st_row_field "$out1" dirty-shokunin 4)
  if [ "$v" = 2 ]; then st_ok "dirty count=2 (untracked file + collapsed .scratch/)"
  else st_bad "dirty count=$v want 2"; fi
  v=$(st_row_field "$out1" dirty-shokunin 5)
  if [ "${v:-0}" -gt 0 ]; then st_ok "dirty scratch_bytes=$v (>0)"
  else st_bad "dirty scratch_bytes=$v"; fi
  v=$(st_row_field "$out1" dirty-shokunin 7)
  case "$v" in
    *dirty*scratch*secret-shaped*) st_ok "dirty flags include dirty,scratch,secret-shaped ($v)" ;;
    *) st_bad "dirty flags='$v'" ;;
  esac

  v=$(st_row_field "$out1" unpushed-shokunin 3)
  if [ "$v" = 1 ]; then st_ok "unpushed count=1"; else st_bad "unpushed count=$v want 1"; fi
  v=$(st_row_field "$out1" unpushed-shokunin 2)
  if [ "$v" = 3 ]; then st_ok "unpushed worktrees=3"; else st_bad "unpushed worktrees=$v want 3"; fi
  v=$(st_row_field "$out1" unpushed-shokunin 7)
  case "$v" in
    *unpushed*) st_ok "unpushed flag present ($v)" ;;
    *) st_bad "unpushed flags='$v'" ;;
  esac
  case "$v" in
    *wt-dirty*) st_ok "wt-dirty flag present ($v)" ;;
    *) st_bad "wt-dirty missing from '$v'" ;;
  esac
  case "$v" in
    *wt-absent*) st_ok "wt-absent flag present ($v)" ;;
    *) st_bad "wt-absent missing from '$v'" ;;
  esac

  v=$(st_row_field "$out1" noremote-shokunin 7)
  case "$v" in
    *no-remote*) st_ok "noremote flag present ($v)" ;;
    *) st_bad "noremote flags='$v'" ;;
  esac
  v=$(st_row_field "$out1" noremote-shokunin 3)
  if [ "${v:-0}" -ge 1 ]; then st_ok "noremote unpushed=$v (>=1, unverifiable but counted)"
  else st_bad "noremote unpushed=$v"; fi

  # secret contents must not appear anywhere in the census output
  if grep -q 'SUPER-SECRET-TOKEN' "$out1"; then
    st_bad "secret file contents leaked into census"
  else
    st_ok "secret file contents absent from census"
  fi
  if grep -q 'watchdog-secret' "$out1" || grep -q 'state-secret' "$out1"; then
    st_bad "forbidden surface contents leaked"
  else
    st_ok "forbidden surface contents absent"
  fi

  # mtime_iso is ISO-8601 with offset
  v=$(st_row_field "$out1" clean-shokunin 6)
  case "$v" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T*) st_ok "mtime_iso shape ($v)" ;;
    *) st_bad "mtime_iso shape '$v'" ;;
  esac
  if [ "$v" = "$kept_iso" ]; then
    st_ok "mtime ignores future .ufo/state and .ufo/watchdog.log"
  else
    st_bad "mtime '$v' want kept.txt '$kept_iso' (forbidden surfaces leaked into mtime)"
  fi

  # compare against itself: header only, exit 0
  local cmp_out cmp_st
  set +e
  cmp_out=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$out1" 2>&1)
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 0 ] && [ "$cmp_out" = "$DIFF_HEADER" ]; then
    st_ok "compare identical: exit 0, header only"
  else
    st_bad "compare identical: exit=$cmp_st out=$(printf '%s' "$cmp_out" | head -5)"
  fi

  # blank lines AFTER a valid header are skipped, not an error: a real
  # prior census with trailing blank lines must still compare clean.
  # (Placed before the mutation block: out1 is still the identical baseline.)
  cat "$out1" > "$ST_TMP/blank-after-header.tsv"
  printf '\n\n' >> "$ST_TMP/blank-after-header.tsv"
  set +e
  cmp_out=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$ST_TMP/blank-after-header.tsv" 2>&1)
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 0 ] && [ "$cmp_out" = "$DIFF_HEADER" ]; then
    st_ok "blank-after-header compares clean (exit 0, header only)"
  else
    st_bad "blank-after-header: exit=$cmp_st out=$(printf '%s' "$cmp_out" | head -5)"
  fi

  # mutate scratch size and dirty set, compare must report both
  printf 'more-scratch\n' >> "$RD/.scratch/note.txt"
  rm -f -- "$RD/untracked.txt"
  local cmp2 cmp2_st
  set +e
  cmp2=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$out1" 2>&1)
  cmp2_st=$?
  set -e
  if [ "$cmp2_st" = 3 ]; then st_ok "compare mutation: exit 3"
  else st_bad "compare mutation: exit=$cmp2_st"; fi
  case "$cmp2" in
    *dirty-shokunin*$'\t'"scratch_bytes"$'\t'*) st_ok "compare reports scratch_bytes" ;;
    *) st_bad "compare missing scratch_bytes row" ;;
  esac
  case "$cmp2" in
    *dirty-shokunin*$'\t'"dirty"$'\t'*) st_ok "compare reports dirty delta" ;;
    *) st_bad "compare missing dirty row" ;;
  esac

  # malformed baselines must exit 2, never look like an empty diff
  printf 'nope\n' > "$ST_TMP/bad.tsv"
  : > "$ST_TMP/empty.tsv"
  printf '\n' > "$ST_TMP/blank-lead.tsv"
  printf '\n%s\n' "$HEADER" > "$ST_TMP/blank-before-header.tsv"
  for f in bad empty blank-lead blank-before-header; do
    set +e
    env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
      "$SELF" --root "$fleet" --compare "$ST_TMP/$f.tsv" >/dev/null 2>&1
    cmp_st=$?
    set -e
    if [ "$cmp_st" = 2 ]; then st_ok "$f compare baseline exits 2"
    else st_bad "$f compare baseline exit=$cmp_st want 2"; fi
  done
  # unknown flag exits 2
  set +e
  env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 "$SELF" --nope >/dev/null 2>&1
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 2 ]; then st_ok "unknown flag exits 2"
  else st_bad "unknown flag exit=$cmp_st want 2"; fi

  # protected boundary: synthetic HOME, never the real store.
  mkdir -p "$ST_TMP/home/.omp/agent"
  printf 'boundary-canary\n' > "$ST_TMP/home/.omp/agent/config.yml"
  ln -s "$ST_TMP/home/.omp/agent/config.yml" "$ST_TMP/protected-compare.tsv"
  local prot_rc prot_err
  set +e
  prot_err=$(env -u GIT_DIR HOME="$ST_TMP/home" TMPDIR=/var/tmp \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$ST_TMP/home/.omp/agent" 2>&1 >/dev/null)
  prot_rc=$?
  set -e
  if [ "$prot_rc" = 2 ] && printf '%s' "$prot_err" | grep -q 'path-protected'; then
    st_ok "protected root refused before access (exit 2, path-protected)"
  else
    st_bad "protected root: rc=$prot_rc err=$(printf '%s' "$prot_err" | head -1)"
  fi
  set +e
  prot_err=$(env -u GIT_DIR HOME="$ST_TMP/home" TMPDIR=/var/tmp \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$ST_TMP/protected-compare.tsv" 2>&1 >/dev/null)
  prot_rc=$?
  set -e
  if [ "$prot_rc" = 2 ] && printf '%s' "$prot_err" | grep -q 'path-protected'; then
    st_ok "protected compare alias refused (exit 2, path-protected)"
  else
    st_bad "protected compare: rc=$prot_rc err=$(printf '%s' "$prot_err" | head -1)"
  fi

  # Round-17 D1/D2 hygiene fleet: repo-local status.showUntrackedFiles=no
  # must not falsify dirty; a hardlinked and a FIFO info/attributes each
  # degrade their own repo to an `error` row (exit 0, one stderr finding)
  # while a neighbour repo still measures and a hardlinked config still
  # refuses the whole run.
  local fleet2="$ST_TMP/fleet-hygiene"
  mkdir -p "$fleet2"
  local RU2="$fleet2/untrackedcfg-shokunin"
  st_init "$RU2" master
  printf 'base\n' > "$RU2/base.txt"
  local u2
  u2=$(st_commit "$RU2" "" "u2 base")
  git -C "$RU2" update-ref refs/heads/master "$u2"
  git -C "$RU2" update-ref refs/remotes/origin/master "$u2"
  printf 'dirt\n' > "$RU2/untracked.txt"
  mkdir -p "$RU2/newdir"
  printf 'a\n' > "$RU2/newdir/a.txt"
  printf 'b\n' > "$RU2/newdir/b.txt"
  printf '[status]\n\tshowUntrackedFiles = no\n' >> "$RU2/.git/config"

  local RA="$fleet2/attrslink-shokunin"
  st_init "$RA" master
  printf 'base\n' > "$RA/base.txt"
  local a1
  a1=$(st_commit "$RA" "" "a1 base")
  git -C "$RA" update-ref refs/heads/master "$a1"
  git -C "$RA" update-ref refs/remotes/origin/master "$a1"
  printf '*.bin filter=x\n' > "$RA/.git/info/attrs-source"
  ln "$RA/.git/info/attrs-source" "$RA/.git/info/attributes"

  local RF="$fleet2/attrsfifo-shokunin"
  st_init "$RF" master
  printf 'base\n' > "$RF/base.txt"
  local f1
  f1=$(st_commit "$RF" "" "f1 base")
  git -C "$RF" update-ref refs/heads/master "$f1"
  git -C "$RF" update-ref refs/remotes/origin/master "$f1"
  mkfifo "$RF/.git/info/attributes"

  local RB="$fleet2/benign-shokunin"
  st_init "$RB" master
  printf 'base\n' > "$RB/base.txt"
  local b1
  b1=$(st_commit "$RB" "" "b1 base")
  git -C "$RB" update-ref refs/heads/master "$b1"
  git -C "$RB" update-ref refs/remotes/origin/master "$b1"

  local out_h err_h rc_h nhyg
  set +e
  err_h=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet2" 2>&1 >"$ST_TMP/hygiene.tsv")
  rc_h=$?
  set -e
  out_h="$ST_TMP/hygiene.tsv"

  if [ "$rc_h" = 0 ]; then st_ok "hygiene fleet: exit 0 (per-repo degrade)"
  else st_bad "hygiene fleet: exit=$rc_h want 0"; fi

  v=$(st_row_field "$out_h" untrackedcfg-shokunin 4)
  # untracked.txt (1) + collapsed newdir/ (1) = 2 despite config "no"
  if [ "$v" = 2 ]; then st_ok "showUntrackedFiles=no: dirty=2 (no false clean)"
  else st_bad "showUntrackedFiles=no: dirty=$v want 2"; fi
  v=$(st_row_field "$out_h" untrackedcfg-shokunin 7)
  case "$v" in
    *dirty*) st_ok "showUntrackedFiles=no: dirty flag present ($v)" ;;
    *) st_bad "showUntrackedFiles=no: flags='$v'" ;;
  esac

  v=$(st_row_field "$out_h" attrslink-shokunin 7)
  if [ "$v" = "error" ]; then st_ok "hardlinked info/attributes: error row"
  else st_bad "hardlinked info/attributes: flags='$v' want error"; fi
  v=$(st_row_field "$out_h" attrslink-shokunin 4)
  if [ "$v" = 0 ]; then st_ok "hardlinked info/attributes: dirty placeholder 0"
  else st_bad "hardlinked info/attributes: dirty=$v want 0"; fi
  case "$err_h" in
    *"git-metadata-unsupported git-metadata-hardlink "*/info/attributes*)
      st_ok "hardlinked info/attributes: stderr finding + path" ;;
    *) st_bad "hardlinked info/attributes: err=$(printf '%s' "$err_h" | head -2)" ;;
  esac
  nhyg=$(printf '%s\n' "$err_h" | grep -c 'git-metadata-unsupported' || true)
  if [ "${nhyg:-0}" = 2 ]; then st_ok "git-metadata-unsupported printed once per repo (2)"
  else st_bad "git-metadata-unsupported lines=$nhyg want 2"; fi

  v=$(st_row_field "$out_h" attrsfifo-shokunin 7)
  if [ "$v" = "error" ]; then st_ok "FIFO info/attributes: error row (no hang)"
  else st_bad "FIFO info/attributes: flags='$v' want error"; fi
  case "$err_h" in
    *"git-metadata-unsupported git-metadata-nonregular "*/info/attributes*)
      st_ok "FIFO info/attributes: stderr finding + path" ;;
    *) st_bad "FIFO info/attributes: err=$(printf '%s' "$err_h" | head -2)" ;;
  esac

  v=$(st_row_field "$out_h" benign-shokunin 7)
  if [ "$v" = "clean" ]; then st_ok "hygiene neighbour unaffected (clean)"
  else st_bad "hygiene neighbour: flags='$v' want clean"; fi

  # control: a hardlinked config in the same fleet keeps exit 2
  ln "$RB/.git/config" "$RB/.git/config-hardlink" 2>/dev/null || true
  set +e
  err_h=$(env -u GIT_DIR SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet2" 2>&1 >/dev/null)
  rc_h=$?
  set -e
  rm -f -- "$RB/.git/config-hardlink"
  if [ "$rc_h" = 2 ] && printf '%s' "$err_h" | grep -q 'path-protected: git-metadata-hardlink'; then
    st_ok "hardlinked config still refuses whole run (exit 2)"
  else st_bad "hardlinked config: rc=$rc_h err=$(printf '%s' "$err_h" | head -1)"; fi

  # Round-18 C1: replace a regular info/attributes after census guards have
  # passed, then hang Git's status open; bounded work must preserve neighbours.
  local real_git shim_dir fleet_timeout RT NA NB timeout_sha out_t err_t repo
  local timeout_rc timeout_start timeout_end timeout_ms fifo_rc blocked_git_pid attempt
  real_git=$(command -v git)
  shim_dir="$ST_TMP/watchdog-shim"
  mkdir -p "$shim_dir"
  cat > "$shim_dir/git" <<'SHIM'
#!/usr/bin/env bash
real_git=${SOUJI_CENSUS_REAL_GIT:?}
if [ -n "${SOUJI_CENSUS_GIT_ATTR_LOG:-}" ]; then
  printf '%s\n' "${GIT_ATTR_NOSYSTEM-unset}" >> "$SOUJI_CENSUS_GIT_ATTR_LOG"
fi
case "${SOUJI_CENSUS_GIT_MODE:-}" in
  fifo)
    if [ "${1:-}" = -C ] &&
      [ "${2:-}" = "${SOUJI_CENSUS_STALL_REPO:-}" ]; then
      repo=$2
      shift 2
      is_status=0
      for arg in "$@"; do
        if [ "$arg" = status ]; then is_status=1; fi
      done
      if [ "$is_status" = 1 ]; then
        rm -f -- "$repo/.git/info/attributes"
        mkfifo -- "$repo/.git/info/attributes"
        printf '%s\n' "$$" > "$SOUJI_CENSUS_STALL_PID_FILE"
        touch -- "$repo/watched.txt"
      fi
      exec "$real_git" -C "$repo" "$@"
    fi
    ;;
  slow)
    if [ "${1:-}" = -C ] &&
      [ "${2:-}" = "${SOUJI_CENSUS_SLOW_REPO:-}" ]; then
      printf 'call\n' >> "$SOUJI_CENSUS_GIT_CALLS"
      sleep 2
    fi
    ;;
  killworker)
    if [ "${1:-}" = -C ] &&
      [ "${2:-}" = "${SOUJI_CENSUS_KILL_REPO:-}" ] &&
      [ "${3:-}" = rev-parse ]; then
      if IFS= read -r stat_line 2>/dev/null < "/proc/$$/stat"; then
        stat_line=${stat_line##*) }
        read -r _state _parent pgid _rest <<< "$stat_line"
        printf '%s\n' "$$" > "$SOUJI_CENSUS_KILL_PID_FILE"
        kill -KILL -- "-$pgid" 2>/dev/null || true
      fi
    fi
    ;;
  protected)
    if [ "${1:-}" = -C ] &&
      [ "${2:-}" = "${SOUJI_CENSUS_PROTECTED_REPO:-}" ] &&
      [ "${3:-}" = config ] && [ "${4:-}" = --get ] &&
      [ "${5:-}" = core.excludesFile ] &&
      [ ! -e "$SOUJI_CENSUS_PROTECTED_MARKER" ]; then
      printf '[core]\n\texcludesFile = %s\n' \
        "$SOUJI_CENSUS_PROTECTED_FILE" >> "$2/.git/config"
      : > "$SOUJI_CENSUS_PROTECTED_MARKER"
    fi
    ;;
esac
exec "$real_git" "$@"
SHIM
  chmod +x "$shim_dir/git"

  fleet_timeout="$ST_TMP/fleet-timeout"
  mkdir -p "$fleet_timeout"
  RT="$fleet_timeout/blocked-shokunin"
  st_init "$RT" master
  printf 'tracked\n' > "$RT/watched.txt"
  timeout_sha=$(st_commit "$RT" "" "timeout target")
  git -C "$RT" update-ref refs/heads/master "$timeout_sha"
  git -C "$RT" update-ref refs/remotes/origin/master "$timeout_sha"
  : > "$RT/.git/info/attributes"
  NA="$fleet_timeout/neighbour-a"
  NB="$fleet_timeout/neighbour-b"
  for repo in "$NA" "$NB"; do
    st_init "$repo" master
    printf 'neighbour\n' > "$repo/tracked.txt"
    local neighbour_sha
    neighbour_sha=$(st_commit "$repo" "" "neighbour")
    git -C "$repo" update-ref refs/heads/master "$neighbour_sha"
    git -C "$repo" update-ref refs/remotes/origin/master "$neighbour_sha"
  done

  out_t="$ST_TMP/watchdog-timeout.tsv"
  err_t="$ST_TMP/watchdog-timeout.err"
  timeout_start=$(date +%s%N)
  if env -u GIT_DIR PATH="$shim_dir:$PATH" \
    SOUJI_CENSUS_REAL_GIT="$real_git" \
    SOUJI_CENSUS_GIT_MODE=fifo \
    SOUJI_CENSUS_STALL_REPO="$RT" SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    SOUJI_CENSUS_STALL_PID_FILE="$ST_TMP/stalled-git.pid" \
    "$SELF" --root "$fleet_timeout" --repo-timeout 1 >"$out_t" 2>"$err_t"; then
    timeout_rc=0
  else
    timeout_rc=$?
  fi
  timeout_end=$(date +%s%N)
  timeout_ms=$(((timeout_end - timeout_start) / 1000000))
  if [ "$timeout_rc" = 0 ]; then st_ok "watchdog FIFO race exits 0"
  else st_bad "watchdog FIFO race exit=$timeout_rc want 0"; fi
  if grep -Fqx -- "$RT"$'\t0\t0\t0\t0\t\terror' "$out_t"; then
    st_ok "watchdog timeout emits the exact error placeholder row"
  else
    st_bad "watchdog timeout row missing or malformed"
  fi
  if grep -Fqx -- "souji-census: repo-timeout 1s $RT" "$err_t"; then
    st_ok "watchdog timeout diagnostic exact"
  else
    st_bad "watchdog timeout diagnostic missing"
  fi
  for base in neighbour-a neighbour-b; do
    local neighbour_worktrees neighbour_dirty neighbour_flags
    neighbour_worktrees=$(st_row_field "$out_t" "$base" 2)
    neighbour_dirty=$(st_row_field "$out_t" "$base" 4)
    neighbour_flags=$(st_row_field "$out_t" "$base" 7)
    if [ "$neighbour_worktrees" = 1 ] &&
      [ "$neighbour_dirty" = 0 ] && [ "$neighbour_flags" = clean ]; then
      st_ok "watchdog neighbour $base measured normally"
    else
      st_bad "watchdog neighbour $base fields=$neighbour_worktrees/$neighbour_dirty/$neighbour_flags"
    fi
  done
  if [ "$timeout_ms" -lt 6000 ]; then
    st_ok "watchdog wall time ${timeout_ms}ms (< 6000ms bound+5)"
  else
    st_bad "watchdog wall time ${timeout_ms}ms (want < 6000ms)"
  fi
  if grep -qi 'job control' "$err_t"; then
    st_bad "watchdog emitted job-control warning"
  else
    st_ok "watchdog stderr has no job-control warning"
  fi
  if python3 -c 'import errno, os, sys
try:
    fd = os.open(sys.argv[1], os.O_WRONLY | os.O_NONBLOCK)
except OSError as error:
    sys.exit(0 if error.errno == errno.ENXIO else 1)
os.close(fd)
sys.exit(2)' "$RT/.git/info/attributes"; then
    st_ok "timed-out FIFO has no reader (nonblocking open returns ENXIO)"
  else
    fifo_rc=$?
    st_bad "timed-out FIFO nonblocking open did not return ENXIO (rc=$fifo_rc)"
  fi
  if [ -r "$ST_TMP/stalled-git.pid" ]; then
    blocked_git_pid=$(<"$ST_TMP/stalled-git.pid")
  else
    blocked_git_pid=""
  fi
  if [ -n "$blocked_git_pid" ]; then
    for ((attempt = 0; attempt < 20; attempt++)); do
      [ ! -e "/proc/$blocked_git_pid" ] && break
      sleep 0.1
    done
  fi
  if [ -n "$blocked_git_pid" ] && [ ! -e "/proc/$blocked_git_pid" ]; then
    st_ok "timed-out Git process is gone"
  else
    st_bad "timed-out Git process remains (pid=$blocked_git_pid)"
  fi
  # A two-second-per-Git-call shim must complete normally under a 30s bound.
  local fleet_slow RS slow_sha slow_rc slow_start slow_end slow_ms slow_calls attr_logged attr_bad
  fleet_slow="$ST_TMP/fleet-slow"
  RS="$fleet_slow/slow-shokunin"
  mkdir -p "$fleet_slow"
  st_init "$RS" master
  printf 'slow\n' > "$RS/tracked.txt"
  slow_sha=$(st_commit "$RS" "" "slow path")
  git -C "$RS" update-ref refs/heads/master "$slow_sha"
  git -C "$RS" update-ref refs/remotes/origin/master "$slow_sha"
  : > "$ST_TMP/slow-git-calls"
  : > "$ST_TMP/git-attr-nosystem.log"
  slow_start=$(date +%s%N)
  if env -u GIT_DIR PATH="$shim_dir:$PATH" \
    SOUJI_CENSUS_REAL_GIT="$real_git" \
    SOUJI_CENSUS_GIT_MODE=slow \
    SOUJI_CENSUS_SLOW_REPO="$RS" \
    SOUJI_CENSUS_GIT_CALLS="$ST_TMP/slow-git-calls" \
    SOUJI_CENSUS_GIT_ATTR_LOG="$ST_TMP/git-attr-nosystem.log" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet_slow" --repo-timeout 30 \
    >"$ST_TMP/slow.tsv" 2>"$ST_TMP/slow.err"; then
    slow_rc=0
  else
    slow_rc=$?
  fi
  slow_end=$(date +%s%N)
  slow_ms=$(((slow_end - slow_start) / 1000000))
  slow_calls=$(grep -c '^call$' "$ST_TMP/slow-git-calls" || true)
  slow_calls=${slow_calls:-0}
  v=$(st_row_field "$ST_TMP/slow.tsv" slow-shokunin 7)
  if [ "$slow_rc" = 0 ] && [ "$v" = clean ] &&
    [ "$slow_calls" -ge 2 ] && [ "$slow_ms" -ge 4000 ]; then
    st_ok "two-second Git calls measured normally (${slow_calls} calls, ${slow_ms}ms)"
  else
    st_bad "slow-Git test rc=$slow_rc flags=$v calls=$slow_calls wall=${slow_ms}ms"
  fi
  if ! grep -q 'repo-timeout' "$ST_TMP/slow.err"; then
    st_ok "slow-Git census did not time out"
  else
    st_bad "slow-Git census timed out unexpectedly"
  fi
  attr_logged=$(grep -c '^1$' "$ST_TMP/git-attr-nosystem.log" || true)
  attr_bad=$(grep -vc '^1$' "$ST_TMP/git-attr-nosystem.log" || true)
  if [ "${attr_logged:-0}" -gt 0 ] && [ "${attr_bad:-0}" = 0 ]; then
    st_ok "GIT_ATTR_NOSYSTEM=1 reaches every shimmed Git call"
  else
    st_bad "GIT_ATTR_NOSYSTEM calls=${attr_logged:-0}, unexpected=${attr_bad:-0}"
  fi
  # A worker group killed outside its watchdog must not be mislabelled timeout.
  local killworker_rc killworker_pid
  if env -u GIT_DIR PATH="$shim_dir:$PATH" \
    SOUJI_CENSUS_REAL_GIT="$real_git" \
    SOUJI_CENSUS_GIT_MODE=killworker SOUJI_CENSUS_KILL_REPO="$RS" \
    SOUJI_CENSUS_KILL_PID_FILE="$ST_TMP/killed-worker.pid" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet_slow" --repo-timeout 30 \
    >"$ST_TMP/killed-worker.tsv" 2>"$ST_TMP/killed-worker.err"; then
    killworker_rc=0
  else
    killworker_rc=$?
  fi
  if [ -r "$ST_TMP/killed-worker.pid" ]; then
    killworker_pid=$(<"$ST_TMP/killed-worker.pid")
  else
    killworker_pid=""
  fi
  if [ -n "$killworker_pid" ]; then
    for ((attempt = 0; attempt < 20; attempt++)); do
      [ ! -e "/proc/$killworker_pid" ] && break
      sleep 0.1
    done
  fi
  if [ "$killworker_rc" = 1 ] && [ ! -s "$ST_TMP/killed-worker.tsv" ] &&
    grep -q "census failed for $RS (rc=137)" "$ST_TMP/killed-worker.err" &&
    ! grep -q 'repo-timeout' "$ST_TMP/killed-worker.err" &&
    [ -n "$killworker_pid" ] && [ ! -e "/proc/$killworker_pid" ]; then
    st_ok "unmarked worker SIGKILL remains census failure, not timeout"
  else
    st_bad "unmarked worker kill rc=$killworker_rc stderr=$(cat "$ST_TMP/killed-worker.err")"
  fi

  # A protected reach discovered within census_one still fails the full run.
  local protected_fleet PR protected_sha protected_marker protected_rc
  protected_fleet="$ST_TMP/fleet-worker-protected"
  PR="$protected_fleet/protected-shokunin"
  protected_marker="$ST_TMP/protected-config-mutation"
  mkdir -p "$protected_fleet"
  st_init "$PR" master
  printf 'protected\n' > "$PR/tracked.txt"
  protected_sha=$(st_commit "$PR" "" "protected path")
  git -C "$PR" update-ref refs/heads/master "$protected_sha"
  git -C "$PR" update-ref refs/remotes/origin/master "$protected_sha"
  if env -u GIT_DIR HOME="$ST_TMP/home" PATH="$shim_dir:$PATH" \
    SOUJI_CENSUS_REAL_GIT="$real_git" \
    SOUJI_CENSUS_GIT_MODE=protected \
    SOUJI_CENSUS_PROTECTED_REPO="$PR" \
    SOUJI_CENSUS_PROTECTED_FILE="$ST_TMP/home/.omp/agent/protected-excludes" \
    SOUJI_CENSUS_PROTECTED_MARKER="$protected_marker" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$protected_fleet" --repo-timeout 5 \
    >"$ST_TMP/protected-worker.tsv" 2>"$ST_TMP/protected-worker.err"; then
    protected_rc=0
  else
    protected_rc=$?
  fi
  if [ "$protected_rc" = 2 ] &&
    grep -q 'path-protected' "$ST_TMP/protected-worker.err" &&
    ! grep -q 'repo-timeout' "$ST_TMP/protected-worker.err" &&
    [ ! -s "$ST_TMP/protected-worker.tsv" ]; then
    st_ok "census_one protected refusal remains exit 2"
  else
    st_bad "protected worker refusal rc=$protected_rc stderr=$(cat "$ST_TMP/protected-worker.err")"
  fi
  local invalid_cli_rc invalid_env_rc
  if "$SELF" --root "$fleet_timeout" --repo-timeout 0 \
    >/dev/null 2>"$ST_TMP/invalid-timeout.err"; then
    invalid_cli_rc=0
  else
    invalid_cli_rc=$?
  fi
  if env SOUJI_CENSUS_REPO_TIMEOUT=86401 "$SELF" --root "$fleet_timeout" \
    >/dev/null 2>"$ST_TMP/invalid-env-timeout.err"; then
    invalid_env_rc=0
  else
    invalid_env_rc=$?
  fi
  if [ "$invalid_cli_rc" = 2 ] && [ "$invalid_env_rc" = 2 ]; then
    st_ok "invalid CLI and environment timeouts exit 2"
  else
    st_bad "invalid timeout exits: CLI=$invalid_cli_rc env=$invalid_env_rc"
  fi
  local odd_fleet odd_tab odd_lf odd_cr odd_path odd_rc odd_rows odd_ok
  local raw_prefix raw_root raw_root_rc raw_compare raw_compare_rc
  local -a odd_repos=()
  odd_fleet="$ST_TMP/fleet-odd-names"
  odd_tab="$odd_fleet/odd"$'\t'"tab"
  odd_lf="$odd_fleet/odd"$'\n'"line"
  odd_cr="$odd_fleet/odd"$'\r'"cr"
  mkdir -p "$odd_fleet"
  for odd_path in "$odd_tab" "$odd_lf" "$odd_cr"; do
    st_init "$odd_path" master
    odd_repos+=("$odd_path")
  done
  if "$SELF" --root "$odd_fleet" >"$ST_TMP/odd-names.tsv" 2>"$ST_TMP/odd-names.err"; then
    odd_rc=0
  else
    odd_rc=$?
  fi
  odd_ok=1
  for odd_path in "${odd_repos[@]}"; do
    v=$(sanitize_field "$odd_path")
    if ! grep -Fqx -- "souji-census: skipped-ambiguous-name $v" "$ST_TMP/odd-names.err"; then
      odd_ok=0
    fi
  done
  odd_rows=$(grep -c $'\t' "$ST_TMP/odd-names.tsv" || true)
  if [ "$odd_rc" = 0 ] && [ "$odd_ok" = 1 ] && [ "$odd_rows" = 1 ]; then
    st_ok "TAB/LF/CR repo basenames are skipped with sanitized diagnostics"
  else
    st_bad "odd-name census rc=$odd_rc diagnostic-check=$odd_ok TSV-lines=$odd_rows"
  fi

  local raw_root_out="$ST_TMP/raw-root.tsv" raw_root_err="$ST_TMP/raw-root.err"
  local raw_compare_out="$ST_TMP/raw-compare.tsv" raw_compare_err="$ST_TMP/raw-compare.err"
  raw_prefix="$ST_TMP/raw-root-prefix"
  mkdir -p "$raw_prefix"
  raw_root="$raw_prefix"$'\n'"suffix"
  if "$SELF" --root "$raw_root" >"$raw_root_out" 2>"$raw_root_err"; then
    raw_root_rc=0
  else
    raw_root_rc=$?
  fi
  printf '%s\n' "$HEADER" > "$ST_TMP/raw-baseline.tsv"
  raw_compare="$ST_TMP/raw-baseline.tsv"$'\n'"suffix"
  if "$SELF" --root "$fleet_slow" --compare "$raw_compare" \
    >"$raw_compare_out" 2>"$raw_compare_err"; then
    raw_compare_rc=0
  else
    raw_compare_rc=$?
  fi
  if [ "$raw_root_rc" = 2 ] && [ "$raw_compare_rc" = 2 ] &&
    grep -q 'ambiguous-path' "$raw_root_err" &&

    grep -q 'ambiguous-path' "$raw_compare_err" &&
    [ ! -s "$raw_root_out" ] && [ ! -s "$raw_compare_out" ]; then
    st_ok "raw LF --root/--compare inputs are rejected before lexical_abs"
  else
    st_bad "raw LF path refusal exits: root=$raw_root_rc compare=$raw_compare_rc"
  fi


  # Python's Popen restores default signal dispositions and makes the census
  # child a fresh session, matching an external supervisor.
  local signal_launcher
  signal_launcher="$ST_TMP/launch-census.py"
  cat > "$signal_launcher" <<'LAUNCH_CENSUS'
#!/usr/bin/env python3
import os
import subprocess
import sys
import time

tool, root, timeout, stdout_path, stderr_path, git_pid_path, census_pid_path, watchdog_pid_path, rc_path = sys.argv[1:]

def save(path, value):
    with open(path, "w", encoding="ascii") as stream:
        stream.write(f"{value}\n")

with open(stdout_path, "wb") as stdout, open(stderr_path, "wb") as stderr:
    child = subprocess.Popen(
        ["bash", tool, "--root", root, "--repo-timeout", timeout],
        stdout=stdout, stderr=stderr, start_new_session=True,
    )
    save(census_pid_path, child.pid)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline and child.poll() is None:
        try:
            with open(git_pid_path, encoding="ascii") as stream:
                git_pid = int(stream.read().strip())
            with open(f"/proc/{git_pid}/stat", encoding="ascii") as stream:
                stat = stream.read()
            worker_pgid = stat.rsplit(")", 1)[1].split()[2]
            with open(f"/proc/{child.pid}/task/{child.pid}/children") as stream:
                children = stream.read().split()
        except (OSError, ValueError, IndexError):
            time.sleep(0.02)
            continue
        for candidate in children:
            try:
                with open(f"/proc/{candidate}/cmdline", "rb") as stream:
                    args = stream.read().split(b"\0")
            except OSError:
                continue
            if any(
                arg == b"souji-census-watchdog"
                and index + 1 < len(args)
                and args[index + 1].decode("ascii", "ignore") == worker_pgid
                for index, arg in enumerate(args)
            ):
                save(watchdog_pid_path, candidate)
                break
        if os.path.exists(watchdog_pid_path):
            break
        time.sleep(0.02)
    result = child.wait()
save(rc_path, result)
LAUNCH_CENSUS
  chmod 700 "$signal_launcher"

  local term_git_pidfile term_census_pidfile term_watchdog_pidfile
  local term_rcfile term_launcher_pid term_census_pid term_git_pid
  local term_worker_pgid term_watchdog_pid term_tmp_dir term_rc term_launcher_rc
  local term_ticks kill_git_pidfile kill_census_pidfile kill_watchdog_pidfile
  local kill_rcfile kill_launcher_pid kill_census_pid kill_git_pid
  local kill_worker_pgid kill_watchdog_pid kill_tmp_dir kill_rc kill_launcher_rc
  local kill_ticks
  interrupt_fleet="$ST_TMP/fleet-interruption"
  RI="$interrupt_fleet/interrupt-shokunin"
  mkdir -p "$interrupt_fleet"
  st_init "$RI" master
  printf 'interrupt\n' > "$RI/tracked.txt"
  interrupt_sha=$(st_commit "$RI" "" "interrupt target")
  git -C "$RI" update-ref refs/heads/master "$interrupt_sha"
  git -C "$RI" update-ref refs/remotes/origin/master "$interrupt_sha"
  : > "$RI/.git/info/attributes"

  # TERM to the census PID must clean the worker, watchdog and its private tmp.
  term_git_pidfile="$ST_TMP/term-git.pid"
  term_census_pidfile="$ST_TMP/term-census.pid"
  term_watchdog_pidfile="$ST_TMP/term-watchdog.pid"
  term_rcfile="$ST_TMP/term-parent.rc"
  env -u GIT_DIR PATH="$shim_dir:$PATH" \
    SOUJI_CENSUS_REAL_GIT="$real_git" \
    SOUJI_CENSUS_GIT_MODE=fifo SOUJI_CENSUS_STALL_REPO="$RI" \
    SOUJI_CENSUS_STALL_PID_FILE="$term_git_pidfile" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    python3 "$signal_launcher" "$SELF" "$interrupt_fleet" 30 \
    "$ST_TMP/term-parent.tsv" "$ST_TMP/term-parent.err" \
    "$term_git_pidfile" "$term_census_pidfile" "$term_watchdog_pidfile" \
    "$term_rcfile" >/dev/null 2>&1 &
  term_launcher_pid=$!
  term_ticks=0
  while { [ ! -s "$term_census_pidfile" ] || [ ! -s "$term_git_pidfile" ] ||
    [ ! -s "$term_watchdog_pidfile" ]; } && [ "$term_ticks" -lt 60 ]; do
    sleep 0.1
    term_ticks=$((term_ticks + 1))
  done
  if [ -r "$term_census_pidfile" ]; then term_census_pid=$(<"$term_census_pidfile"); else term_census_pid=""; fi
  if [ -r "$term_git_pidfile" ]; then term_git_pid=$(<"$term_git_pidfile"); else term_git_pid=""; fi
  if [ -r "$term_watchdog_pidfile" ]; then term_watchdog_pid=$(<"$term_watchdog_pidfile"); else term_watchdog_pid=""; fi
  if [ -n "$term_git_pid" ]; then
    term_worker_pgid=$(st_proc_pgid "$term_git_pid" || true)
    term_tmp_dir=$(st_worker_tmpdir "$term_worker_pgid" || true)
  else
    term_worker_pgid=""
    term_tmp_dir=""
  fi
  if [ -n "$term_census_pid" ]; then
    kill -TERM "$term_census_pid" 2>/dev/null || true
  fi
  if wait "$term_launcher_pid"; then term_launcher_rc=0; else term_launcher_rc=$?; fi
  if [ -r "$term_rcfile" ]; then term_rc=$(<"$term_rcfile"); else term_rc=-1; fi
  for ((term_ticks = 0; term_ticks < 40; term_ticks++)); do
    if [ -n "$term_git_pid" ] && [ ! -e "/proc/$term_git_pid" ] &&
      [ -n "$term_watchdog_pid" ] && [ ! -e "/proc/$term_watchdog_pid" ] &&
      [ -n "$term_tmp_dir" ] && [ ! -e "$term_tmp_dir" ]; then
      break
    fi
    sleep 0.1
  done
  if [ "$term_rc" = -15 ] && [ "$term_launcher_rc" = 0 ] &&
    [ -n "$term_git_pid" ] && [ ! -e "/proc/$term_git_pid" ] &&
    [ -n "$term_watchdog_pid" ] && [ ! -e "/proc/$term_watchdog_pid" ] &&
    [ -n "$term_tmp_dir" ] && [ ! -e "$term_tmp_dir" ] &&
    [ ! -s "$ST_TMP/term-parent.tsv" ]; then
    st_ok "parent SIGTERM stops worker and timer before temp cleanup"
  else
    st_bad "parent SIGTERM cleanup rc=$term_rc launcher=$term_launcher_rc census=$term_census_pid git=$term_git_pid watchdog=$term_watchdog_pid tmp=$term_tmp_dir"
  fi
  if [ -n "$term_worker_pgid" ] && kill -0 -- "-$term_worker_pgid" 2>/dev/null; then
    kill -KILL -- "-$term_worker_pgid" 2>/dev/null || true
  fi
  if [ -n "$term_watchdog_pid" ] && [ -e "/proc/$term_watchdog_pid" ]; then
    kill -KILL -- "-$term_watchdog_pid" 2>/dev/null || true
  fi
  if [ -n "$term_census_pid" ] && [ -e "/proc/$term_census_pid" ]; then
    kill -KILL "$term_census_pid" 2>/dev/null || true
  fi
  if [ -e "/proc/$term_launcher_pid" ]; then kill -KILL "$term_launcher_pid" 2>/dev/null || true; fi
  case "$term_tmp_dir" in /var/tmp/souji-census-now.*) rm -rf -- "$term_tmp_dir" ;; esac

  # SIGKILL cannot run a trap; the detached timer must still reap the group.
  rm -f -- "$RI/.git/info/attributes" "$ST_TMP/kill-git.pid"
  : > "$RI/.git/info/attributes"
  kill_git_pidfile="$ST_TMP/kill-git.pid"
  kill_census_pidfile="$ST_TMP/kill-census.pid"
  kill_watchdog_pidfile="$ST_TMP/kill-watchdog.pid"
  kill_rcfile="$ST_TMP/kill-parent.rc"
  env -u GIT_DIR PATH="$shim_dir:$PATH" \
    SOUJI_CENSUS_REAL_GIT="$real_git" \
    SOUJI_CENSUS_GIT_MODE=fifo SOUJI_CENSUS_STALL_REPO="$RI" \
    SOUJI_CENSUS_STALL_PID_FILE="$kill_git_pidfile" \
    SOUJI_CENSUS_SELFTEST_ACTIVE=1 \
    python3 "$signal_launcher" "$SELF" "$interrupt_fleet" 2 \
    "$ST_TMP/kill-parent.tsv" "$ST_TMP/kill-parent.err" \
    "$kill_git_pidfile" "$kill_census_pidfile" "$kill_watchdog_pidfile" \
    "$kill_rcfile" >/dev/null 2>&1 &
  kill_launcher_pid=$!
  kill_ticks=0
  while { [ ! -s "$kill_census_pidfile" ] || [ ! -s "$kill_git_pidfile" ] ||
    [ ! -s "$kill_watchdog_pidfile" ]; } && [ "$kill_ticks" -lt 60 ]; do
    sleep 0.1
    kill_ticks=$((kill_ticks + 1))
  done
  if [ -r "$kill_census_pidfile" ]; then kill_census_pid=$(<"$kill_census_pidfile"); else kill_census_pid=""; fi
  if [ -r "$kill_git_pidfile" ]; then kill_git_pid=$(<"$kill_git_pidfile"); else kill_git_pid=""; fi
  if [ -r "$kill_watchdog_pidfile" ]; then kill_watchdog_pid=$(<"$kill_watchdog_pidfile"); else kill_watchdog_pid=""; fi
  if [ -n "$kill_git_pid" ]; then
    kill_worker_pgid=$(st_proc_pgid "$kill_git_pid" || true)
    kill_tmp_dir=$(st_worker_tmpdir "$kill_worker_pgid" || true)
  else
    kill_worker_pgid=""
    kill_tmp_dir=""
  fi
  if [ -n "$kill_census_pid" ]; then kill -KILL "$kill_census_pid" 2>/dev/null || true; fi
  if wait "$kill_launcher_pid"; then kill_launcher_rc=0; else kill_launcher_rc=$?; fi
  if [ -r "$kill_rcfile" ]; then kill_rc=$(<"$kill_rcfile"); else kill_rc=-1; fi
  for ((kill_ticks = 0; kill_ticks < 100; kill_ticks++)); do
    if [ -n "$kill_git_pid" ] && [ ! -e "/proc/$kill_git_pid" ] &&
      [ -n "$kill_watchdog_pid" ] && [ ! -e "/proc/$kill_watchdog_pid" ] &&
      [ -n "$kill_tmp_dir" ] && [ ! -e "$kill_tmp_dir" ]; then
      break
    fi
    sleep 0.1
  done
  if [ "$kill_rc" = -9 ] && [ "$kill_launcher_rc" = 0 ] &&
    [ -n "$kill_git_pid" ] && [ ! -e "/proc/$kill_git_pid" ] &&
    [ -n "$kill_watchdog_pid" ] && [ ! -e "/proc/$kill_watchdog_pid" ] &&
    [ -n "$kill_tmp_dir" ] && [ ! -e "$kill_tmp_dir" ]; then
    st_ok "parent SIGKILL leaves timer to reap worker and temp state"
  else
    st_bad "parent SIGKILL cleanup rc=$kill_rc launcher=$kill_launcher_rc census=$kill_census_pid git=$kill_git_pid watchdog=$kill_watchdog_pid tmp=$kill_tmp_dir"
  fi
  if [ -n "$kill_worker_pgid" ] && kill -0 -- "-$kill_worker_pgid" 2>/dev/null; then
    kill -KILL -- "-$kill_worker_pgid" 2>/dev/null || true
  fi
  if [ -n "$kill_watchdog_pid" ] && [ -e "/proc/$kill_watchdog_pid" ]; then
    kill -KILL -- "-$kill_watchdog_pid" 2>/dev/null || true
  fi
  if [ -n "$kill_census_pid" ] && [ -e "/proc/$kill_census_pid" ]; then
    kill -KILL "$kill_census_pid" 2>/dev/null || true
  fi
  if [ -e "/proc/$kill_launcher_pid" ]; then kill -KILL "$kill_launcher_pid" 2>/dev/null || true; fi
  case "$kill_tmp_dir" in /var/tmp/souji-census-now.*) rm -rf -- "$kill_tmp_dir" ;; esac


  # An inherited SIG_IGN TERM must not hold a normally-cancelled timer open.
  local ignored_rc ignored_start ignored_end ignored_ms ignored_flags
  ignored_start=$(date +%s%N)
  if bash -c 'trap "" TERM; exec "$1" --root "$2" --repo-timeout 30' \
    souji-census-selftest "$SELF" "$fleet_slow" \
    >"$ST_TMP/ignored-term.tsv" 2>"$ST_TMP/ignored-term.err"; then
    ignored_rc=0
  else
    ignored_rc=$?
  fi
  ignored_end=$(date +%s%N)
  ignored_ms=$(((ignored_end - ignored_start) / 1000000))
  ignored_flags=$(st_row_field "$ST_TMP/ignored-term.tsv" slow-shokunin 7)
  if [ "$ignored_rc" = 0 ] && [ "$ignored_flags" = clean ] &&
    [ "$ignored_ms" -lt 1500 ] && ! grep -q 'repo-timeout' "$ST_TMP/ignored-term.err"; then
    st_ok "SIGTERM-ignored caller cancels watchdogs (${ignored_ms}ms)"
  else
    st_bad "SIGTERM-ignored run rc=$ignored_rc flags=$ignored_flags wall=${ignored_ms}ms"
  fi

  # source audit: no forbidden git porcelain in non-comment lines
  local n
  n=$(grep -cE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase|prune)( |$)|^[^#]*--alternate-refs' "$SELF" || true)
  n=${n// /}
  if [ "${n:-1}" = 0 ]; then st_ok "no forbidden git subcommand"
  else st_bad "$n forbidden git invocation(s)"; fi

  case "$fleet" in
    "$ST_TMP"/*) st_ok "fixtures under mktemp ($ST_TMP)" ;;
    *) st_bad "fixtures not under mktemp" ;;
  esac

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# --- main ------------------------------------------------------------------

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --repo-timeout)
      [ "$#" -ge 2 ] || usage_err "--repo-timeout needs an integer"
      REPO_TIMEOUT=$2; shift 2 ;;
    --repo-timeout=*) REPO_TIMEOUT=${1#*=}; shift ;;
    --include-root) INCLUDE_ROOT=1; shift ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a directory"
      ROOT=$2; shift 2 ;;
    --root=*) ROOT=${1#*=}; shift ;;
    --compare)
      [ "$#" -ge 2 ] || usage_err "--compare needs a TSV path"
      COMPARE=$2; COMPARE_SET=1; shift 2 ;;
    --compare=*) COMPARE=${1#*=}; COMPARE_SET=1; shift ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown flag: $1" ;;
    *) usage_err "unexpected argument: $1 (repos come from --root)" ;;
  esac
done
validate_repo_timeout

if [ "$SELFTEST" = 1 ]; then run_selftest; fi

[ -n "$ROOT" ] || usage_err "--root needs a directory"
if [ "$COMPARE_SET" = 1 ] && [ -z "$COMPARE" ]; then
  usage_err "--compare needs a TSV path"
fi
# Boundary refusal precedes command lookup and every git/find/du/read path.
guard_path root "$ROOT" >/dev/null
if [ "$COMPARE_SET" = 1 ]; then guard_path compare "$COMPARE" >/dev/null; fi

command -v git >/dev/null 2>&1 || { printf 'souji-census: git not found\n' >&2; exit 1; }
command -v du >/dev/null 2>&1 || { printf 'souji-census: du not found\n' >&2; exit 1; }
command -v setsid >/dev/null 2>&1 || { printf 'souji-census: setsid not found\n' >&2; exit 1; }

if [ "$COMPARE_SET" = 1 ]; then
  emit_compare
  exit $?
fi

emit_census
exit 0
