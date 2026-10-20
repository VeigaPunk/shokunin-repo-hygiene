#!/usr/bin/env bash
# souji-census — repeatable read-only fleet census (round 6, seat S33).
# Round-14 C2 adds a pre-access protected-path boundary. Round-16 C1 makes
# the repository-config guard value/effect-aware (repairs r14's value-blind
# whole-run refusals of benign configuration).
#
# One bash tool; bash + coreutils + git only. Never fetches, never writes
# outside /var/tmp temporary output. The mtime walk never opens file
# contents, but `git status` may read or hash tracked content (this is not a
# data-loss-prevention classifier), and .ufo/state or .ufo/watchdog.log are
# never traversed by the mtime walk.
#
# CLI
#   tools/souji-census.sh [--root DIR] [--compare PREV.tsv]
#                         [--include-root] [--selftest]
#
# Default scan: every immediate child of $SHOKUNIN_ROOT (or --root) whose
# .git is a directory (a main repo, not a linked work tree or submodule
# gitfile). Linked work trees are counted on their owner via `worktree list`,
# not emitted as their own row. --include-root also emits a row for the root
# itself when it is a main repo.
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
#                   only (default untracked mode: a wholly untracked directory
#                   is one line, matching souji-verify). Other work trees are
#                   not added into this number; see wt-dirty. Submodule
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
#   Builds a fixture fleet under /var/tmp, runs the census twice (byte-
#   identical), mutates one fixture, checks --compare and the protected
#   boundary. Removes the fixture tree on exit. Exit 0 on pass, 1 on fail.
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
#   Global/system git config and every inherited GIT_* variable are
#   cleared. Startup resolves each home's .omp parent (not the agent store)
#   to seed a relocated-store root; this is a stat/readlink of the store
#   parent, never store content. Residual: hardlinked aliases are refused
#   for --compare (nlink > 1) and fixed git metadata, but hardlinked object
#   files and arbitrary hardlinks into a store are not detectable without
#   stat'ing the store; the guard and the later access are not one atomic
#   operation.
#
# Exit codes
#   0 census emitted (rows may carry `error`/status-unverifiable for
#     degraded repositories) / header-only diff; 1 selftest or setup failure;
#   2 usage, malformed baseline, or protected-path refusal; 3 compare drift.
#
# Env
#   SHOKUNIN_ROOT   default root when --root is omitted
#                   (default: parent of this repo)
set -euo pipefail

# Imported BASH_FUNC_* definitions could shadow the externally-resolved
# commands this tool relies on. Remove functions for those names.
unset -f git find du stat awk grep sort head cut date readlink 2>/dev/null || true

# Clear every inherited GIT_* variable. GIT_DIR/GIT_COMMON_DIR/
# GIT_OBJECT_DIRECTORY/GIT_ALTERNATE_OBJECT_DIRECTORIES and GIT_CONFIG_*
# can redirect reads or command execution into a credential store. Global
# and system config are disabled; repository-local config inside a guarded
# repo is still inspected and, if unsupported, refused.
while IFS= read -r _souji_gitvar; do unset "$_souji_gitvar"; done < <(compgen -v GIT_ || true)
unset _souji_gitvar
export GIT_OPTIONAL_LOCKS=0
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0
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
ROOT_RAW_IS_SYMLINK=0
CENSUS_TMP=""

usage() {
  awk 'NR > 1 { if ($0 !~ /^#/) exit; sub(/^# ?/, ""); print }' "$SELF"
  exit "${1:-0}"
}

usage_err() { printf 'souji-census: %s\n' "$1" >&2; usage 2 >&2; }

cleanup_census_tmp() {
  if [ -n "${CENSUS_TMP:-}" ]; then
    rm -f -- "$CENSUS_TMP"
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
guard_git_files() { # $1 resolved gitdir
  local dir=$1 rel path nlink
  for rel in config HEAD index packed-refs commondir info/exclude info/attributes objects/info/alternates; do
    path="$dir/$rel"
    if [ -f "$path" ]; then
      nlink=$(stat -L -c %h -- "$path" 2>/dev/null || true)
      case "$nlink" in
        ''|*[!0-9]*) protected_fail "git-metadata-unavailable" "$dir" "$path" ;;
      esac
      if [ "$nlink" -gt 1 ]; then
        protected_fail "git-metadata-hardlink" "$dir" "$path"
      fi
    elif [ -e "$path" ] && [ ! -d "$path" ]; then
      protected_fail "git-metadata-nonregular" "$dir" "$path"
    fi
  done
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
  for entry in "$dir"/worktrees/*; do
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
            guard_git_files "$admin" || exit 2
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
# cannot be evaluated; every remaining guard still runs first, so a later
# protected reach still refuses the whole run.
guard_git_surface() { # $1 repo dir
  local repo=$1 g="$1/.git" target common dir first soft=0
  CFG_SOFT_REASON=""
  if [ -L "$g" ]; then
    guard_target git-metadata "$g" >/dev/null
    return 0
  fi
  if [ -d "$g" ]; then
    dir=$(guard_target gitdir "$g") || exit 2
    guard_git_links "$dir" || exit 2
    guard_git_files "$dir" || exit 2
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
        guard_git_files "$dir" || exit 2
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
    guard_git_files "$dir" || exit 2
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
        guard_git_files "$dir" || exit 2
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
  # Pathspec-exclude the off-limits driver surfaces so status does not walk
  # them. A wholly untracked directory elsewhere still collapses to one line.
  if ! st=$(git -C "$1" --no-optional-locks -c core.fsmonitor=false \
      -c core.hooksPath=/dev/null -c core.excludesFile="$ex" \
      -c core.attributesFile="$at" status --porcelain --ignore-submodules=all -- . \
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
      printf 'souji-census: config-unsupported: %s (%s)\n' \
        "${CFG_SOFT_REASON:-git-config-unsupported}" "$(sanitize_field "$cpath")" >&2
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
    printf 'souji-census: config-unsupported: %s (%s)\n' \
      "${CFG_SOFT_REASON:-git-config-unsupported}" "$(sanitize_field "$repo")" >&2
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
  local d g base reason
  REPOS=()
  if [ "$INCLUDE_ROOT" = 1 ] && [ "$ROOT_RAW_IS_SYMLINK" = 0 ] && [ -d "$root" ]; then
    g="$root/.git"
    if [ -L "$g" ]; then
      guard_target git-metadata "$g" >/dev/null
    elif [ -f "$g" ]; then
      guard_git_surface "$root" || true
      REPOS+=("$root")
    elif [ -d "$g" ]; then
      guard_git_surface "$root" || true
      REPOS+=("$root")
    fi
  fi
  shopt -s nullglob
  for d in "$root"/*; do
    base=${d##*/}
    # skip dot-dirs (operator config, .ufo, .scratch) and unrepresentable names
    case "$base" in
      .*) continue ;;
    esac
    case "$base" in
      *$'\n'*|*$'\t'*|*$'\r'*) continue ;;
    esac
    if reason=$(protected_reason_input "$d"); then
      protected_fail "$reason" candidate "$d"
    fi
    # A symlink child is never a repo root and is never followed.
    if [ -L "$d" ]; then continue; fi
    [ -d "$d" ] || continue
    g="$d/.git"
    if [ -L "$g" ]; then
      guard_target git-metadata "$g" >/dev/null
      continue
    fi
    if [ -f "$g" ]; then
      guard_git_pointer "$d" "$g"
      continue
    fi
    if [ -d "$g" ]; then
      guard_git_surface "$d" || true
      REPOS+=("$d")
    fi
  done
  shopt -u nullglob
  if [ "${#REPOS[@]}" -eq 0 ]; then return 0; fi
  mapfile -t REPOS < <(printf '%s\n' "${REPOS[@]}" | LC_ALL=C sort)
}

emit_census() {
  local root repo row rc
  root=$(guard_path root "$ROOT") || exit 2
  [ -d "$root" ] || { printf 'souji-census: root is not a directory: %s\n' "$root" >&2; exit 1; }
  ROOT_RAW_IS_SYMLINK=0
  if [ -L "$ROOT" ]; then ROOT_RAW_IS_SYMLINK=1; fi
  list_repos "$root"
  local -a rows=()
  for repo in "${REPOS[@]+"${REPOS[@]}"}"; do
    if row=$(census_one "$repo"); then
      rows+=("$row")
    else
      rc=$?
      if [ "$rc" = 2 ]; then exit 2; fi
      printf 'souji-census: census failed for %s (rc=%s)\n' "$repo" "$rc" >&2
      exit 1
    fi
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
  CENSUS_TMP=$(mktemp /var/tmp/souji-census-now.XXXXXX)
  trap cleanup_census_tmp EXIT
  emit_census > "$CENSUS_TMP"
  load_census "$CENSUS_TMP" after
  rm -f -- "$CENSUS_TMP"
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

if [ "$COMPARE_SET" = 1 ]; then
  emit_compare
  exit $?
fi

emit_census
exit 0
