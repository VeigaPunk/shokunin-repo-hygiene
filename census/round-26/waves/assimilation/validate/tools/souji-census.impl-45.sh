#!/usr/bin/env bash
# souji-census.impl-45.sh — repeatable fleet census (round 6, seat S45).
#
# Independent implementation of the S33 contract. Runners glob
# tools/souji-census.impl-*.sh (33..48); this file is that name for seat 45.
#
# CLI
#   tools/souji-census.impl-45.sh [--selftest] [--compare PREV.tsv] [--root DIR] [ROOT]
#
# Default root: $SHOKUNIN_ROOT if set, otherwise the parent of this repo
# (the fleet root). --selftest is exclusive. --compare reads a previous
# census-v1 TSV and prints a diff instead of the census.
#
# Census (stdout, census-v1 TSV, one row per repo, LC_ALL=C sorted by path):
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#
# What a repo is
#   The root itself, if it is a git worktree toplevel, plus each immediate
#   child directory that is a git worktree toplevel (.git file or directory,
#   git rev-parse --show-toplevel equal to that directory). Not recursive.
#   Symlink children are not followed. Bare repos are omitted. A child whose
#   basename is secret-shaped is skipped before any git command runs inside it.
#
# Hand-check commands (run from nowhere special; paths are absolute):
#   worktrees   git -C REPO --no-optional-locks worktree list --porcelain | grep -c '^worktree '
#               Includes the main worktree. Equals `git worktree list | wc -l`
#               for ordinary paths.
#   unpushed    git -C REPO --no-optional-locks rev-list --count --branches --not --remotes
#               Commits reachable from any local branch and not from any
#               remote-tracking ref. No HEAD commit -> 0 (flag no-commits).
#               Equals `git log --branches --not --remotes --oneline | wc -l`.
#               This is NOT `status -sb` ahead-count: side branches count.
#   dirty       git -C REPO --no-optional-locks status --porcelain --untracked-files=all
#               then drop lines whose path is .ufo/state, under .ufo/state/,
#               or .ufo/watchdog.log (at any depth). Those paths are off-limits
#               and are not opened. Secret-shaped untracked paths are counted
#               (status does not read content) and never opened.
#               Uses the invoking git excludes (repo .gitignore, info/exclude,
#               core.excludesFile). A hand check must use the same environment.
#   scratch     absent -> 0. Symlink -> stat -c %s of the link, not followed
#               (flag scratch-symlink). Otherwise `du -sb -- REPO/.scratch | cut -f1`
#               (apparent bytes, not allocated blocks).
#   mtime_iso   newest regular file (-type f, no -L) under the worktree,
#               excluding .git, nested git repos, .ufo/state, .ufo/watchdog.log,
#               and secret-shaped names. Convert the find %T@ epoch with
#               `date -d @EPOCH --iso-8601=seconds`. No eligible file -> `-`.
#               Nested repos are separate rows; their files are not this row's.
#
# verdict_flags, comma-separated, fixed order, or the single token ok:
#   worktrees-failed, unpushed-failed, status-failed, scratch-unreadable,
#   no-commits, detached, no-remote, unpushed, dirty, extra-worktrees,
#   scratch, scratch-symlink
#   ok means worktrees=1, unpushed=0, dirty=0, scratch_bytes=0, HEAD is a
#   commit on a branch, and at least one remote-tracking branch ref exists
#   (refs/remotes/*/HEAD alone does not count).
#   -1 in a numeric field means that count failed; the matching *-failed flag
#   is set. A per-repo failure still emits a row and does not abort the scan.
#
# --compare PREV.tsv
#   Header must be exactly the census-v1 header. Diff columns are every field
#   except repo. Stdout:
#     status  repo  field  baseline  current
#     changed|unchanged|added|removed|incomparable  ...
#     summary  compared=N  unchanged=N  changed=N  added=N  removed=N  incomparable=0|1
#   Exit 0 when the file was read (deltas are not a failure). Exit 2 when
#   PREV is missing, unreadable, or a restricted path (live obsidian ledger,
#   .ufo/state, .ufo/watchdog.log, secret-shaped component) — those are not opened.
#   A non-census-v1 header (including census/round-1/census.tsv) is
#   incomparable, exit 0, and the file is not interpreted as counts.
#
# Exit codes: 0 census or compare completed, or selftest passed; 1 selftest
# failure or unexpected evaluation error; 2 usage. No other codes.
#
# Safety
#   Read-only over every inspected surface. git is only ever invoked as
#   `git --no-optional-locks` plus read subcommands (rev-parse, worktree list,
#   rev-list, status, for-each-ref, symbolic-ref, update-ref/commit-tree/
#   write-tree/add/init/worktree add only inside --selftest fixtures under
#   mktemp). Never fetch/push/commit/branch/prune/checkout/reset/rebase,
#   never rm, never delete. Never reads secret-shaped file content. Never
#   opens .ufo/state, .ufo/watchdog.log, or the obsidian ledger. Does not
#   follow .scratch symlinks. --selftest writes only under mktemp -d and
#   leaves that directory in place.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE GIT_PREFIX 2>/dev/null || true
export GIT_OPTIONAL_LOCKS=0
export GIT_TERMINAL_PROMPT=0
export GIT_PAGER=cat
export LC_ALL=C

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'
COMPARE_HEADER=$'status\trepo\tfield\tbaseline\tcurrent'
TOOL=souji-census.impl-45

usage() {
  sed -n '2,62p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

usage_err() {
  printf '%s: %s\n' "$TOOL" "$1" >&2
  exit 2
}

git_ro() {
  git --no-optional-locks "$@"
}

is_secret_component() {
  local lc=${1,,}
  case "$lc" in
    *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem) return 0 ;;
  esac
  return 1
}

refuse_path() {
  local p=$1 c comp
  [ -n "$p" ] || return 0
  c=$(readlink -m -- "$p" 2>/dev/null || printf '%s' "$p")
  case "$c" in
    */.ufo/state|*/.ufo/state/*|*/.ufo/watchdog.log) return 0 ;;
  esac
  case "$(basename -- "$c")" in
    obsidian-ledger.tsv) return 0 ;;
  esac
  local IFS=/
  set -f
  for comp in $c; do
    if is_secret_component "$comp"; then
      set +f
      return 0
    fi
  done
  set +f
  return 1
}

is_repo_toplevel() {
  local d=$1 top canon
  [ -d "$d" ] || return 1
  [ -e "$d/.git" ] || [ -L "$d/.git" ] || return 1
  canon=$(readlink -f -- "$d" 2>/dev/null) || return 1
  top=$(git_ro -C "$d" rev-parse --show-toplevel 2>/dev/null) || return 1
  [ "$top" = "$canon" ]
}

discover_repos() {
  local root=$1 path base canon
  if is_repo_toplevel "$root"; then
    printf '%s\n' "$(readlink -f -- "$root")"
  fi
  while IFS= read -r path; do
    [ -n "$path" ] || continue
    base=$(basename -- "$path")
    [ "$base" = ".git" ] && continue
    if is_secret_component "$base"; then
      continue
    fi
    if is_repo_toplevel "$path"; then
      canon=$(readlink -f -- "$path")
      printf '%s\n' "$canon"
    fi
  done < <(find -P "$root" -mindepth 1 -maxdepth 1 -type d -printf '%p\n' 2>/dev/null || true)
}

count_worktrees() {
  local repo=$1 out n
  if ! out=$(git_ro -C "$repo" worktree list --porcelain 2>/dev/null); then
    printf -- '-1\n'
    return 1
  fi
  n=$(printf '%s\n' "$out" | grep -c '^worktree ' || true)
  printf '%s\n' "$n"
}

count_unpushed() {
  local repo=$1 n
  if ! git_ro -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
    printf '0\n'
    return 2
  fi
  if ! n=$(git_ro -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null); then
    printf -- '-1\n'
    return 1
  fi
  case "$n" in
    ''|*[!0-9]*) printf -- '-1\n'; return 1 ;;
  esac
  printf '%s\n' "$n"
}

status_path_offlimits() {
  local path=$1
  case "$path" in
    .ufo/state|.ufo/state/*|*/.ufo/state|*/.ufo/state/*|.ufo/watchdog.log|*/.ufo/watchdog.log)
      return 0 ;;
  esac
  return 1
}

count_dirty() {
  local repo=$1 line path n=0 failed=0
  while IFS= read -r line; do
    if [ "$line" = $'\037' ]; then
      failed=1
      break
    fi
    [ -n "$line" ] || continue
    path=${line:3}
    case "$path" in
      *' -> '*) path=${path##*' -> '} ;;
    esac
    if [[ "$path" == \"*\" ]]; then
      path=${path:1:${#path}-2}
    fi
    if status_path_offlimits "$path"; then
      continue
    fi
    n=$((n + 1))
  done < <(git_ro -C "$repo" status --porcelain --untracked-files=all 2>/dev/null || printf '\037\n')
  if [ "$failed" = 1 ]; then
    printf -- '-1\n'
    return 1
  fi
  printf '%s\n' "$n"
}

scratch_of() {
  local p=$1 n
  if [ ! -e "$p" ] && [ ! -L "$p" ]; then
    printf '0\n'
    return 0
  fi
  if [ -L "$p" ]; then
    if ! n=$(stat -c '%s' -- "$p" 2>/dev/null); then
      printf -- '-1\n'
      return 1
    fi
    printf '%s\n' "$n"
    return 3
  fi
  if ! n=$(du -sb -- "$p" 2>/dev/null | cut -f1); then
    printf -- '-1\n'
    return 1
  fi
  case "$n" in
    ''|*[!0-9]*) printf -- '-1\n'; return 1 ;;
  esac
  printf '%s\n' "$n"
}

newest_epoch() {
  local repo=$1 nested name epoch
  local -a extra=()
  extra+=(-o -path './.souji-census-impl-45-no-such-path')
  while IFS= read -r nested; do
    [ -n "$nested" ] || continue
    name=${nested#./}
    extra+=(-o -path "./$name" -o -path "./$name/*")
  done < <(find -P "$repo" -mindepth 1 -maxdepth 1 -type d ! -name '.git' -exec test -e '{}/.git' \; -printf '%P\n' 2>/dev/null || true)
  epoch=$(
    cd -- "$repo" && find -P . \
      \( -name '.git' \
         -o -path './.ufo/state' -o -path './.ufo/state/*' \
         -o -path '*/.ufo/state' -o -path '*/.ufo/state/*' \
         -o -path './.ufo/watchdog.log' -o -path '*/.ufo/watchdog.log' \
         -o -iname '*.env' -o -iname '.env' -o -iname '.env.*' -o -iname '.envrc' \
         -o -iname '*credential*' -o -iname '*secret*' -o -iname 'id_*' -o -iname '*.pem' \
         "${extra[@]}" \
      \) -prune -o -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1 || true
  )
  printf '%s\n' "$epoch"
}

epoch_to_iso() {
  local ts=$1 iso
  [ -n "$ts" ] || { printf '%s\n' '-'; return 0; }
  if ! iso=$(date -d "@$ts" --iso-8601=seconds 2>/dev/null); then
    printf '%s\n' '-'
    return 0
  fi
  printf '%s\n' "$iso"
}

has_remote_branch() {
  local repo=$1 ref
  while IFS= read -r ref; do
    [ -n "$ref" ] || continue
    case "$ref" in
      refs/remotes/*/HEAD) continue ;;
    esac
    return 0
  done < <(git_ro -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null || true)
  return 1
}

is_detached() {
  local repo=$1
  if git_ro -C "$repo" symbolic-ref -q HEAD >/dev/null 2>&1; then
    return 1
  fi
  if git_ro -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

build_flags() {
  local wt=$1 un=$2 dirty=$3 scratch=$4 no_commits=$5 detached=$6 no_remote=$7 symlink=$8
  local -a f=()
  [ "$wt" = -1 ] && f+=(worktrees-failed)
  [ "$un" = -1 ] && f+=(unpushed-failed)
  [ "$dirty" = -1 ] && f+=(status-failed)
  [ "$scratch" = -1 ] && f+=(scratch-unreadable)
  [ "$no_commits" = 1 ] && f+=(no-commits)
  [ "$detached" = 1 ] && f+=(detached)
  [ "$no_remote" = 1 ] && f+=(no-remote)
  if [ "$un" != -1 ] && [ "$un" -gt 0 ] 2>/dev/null; then f+=(unpushed); fi
  if [ "$dirty" != -1 ] && [ "$dirty" -gt 0 ] 2>/dev/null; then f+=(dirty); fi
  if [ "$wt" != -1 ] && [ "$wt" -gt 1 ] 2>/dev/null; then f+=(extra-worktrees); fi
  if [ "$scratch" != -1 ] && [ "$scratch" -gt 0 ] 2>/dev/null; then f+=(scratch); fi
  [ "$symlink" = 1 ] && f+=(scratch-symlink)
  if [ ${#f[@]} -eq 0 ]; then
    printf 'ok'
  else
    local IFS=,
    printf '%s' "${f[*]}"
  fi
}

census_one() {
  local repo=$1
  local wt un dirty scratch mt epoch
  local no_commits=0 detached=0 no_remote=0 symlink=0
  local wrc urc drc src
  case "$repo" in
    *$'\t'*|*$'\n'*)
      printf '%s: skip path with tab or newline\n' "$TOOL" >&2
      return 0
      ;;
  esac
  if wt=$(count_worktrees "$repo"); then wrc=0; else wrc=$?; fi
  if un=$(count_unpushed "$repo"); then urc=0; else urc=$?; fi
  if [ "$urc" = 2 ]; then no_commits=1; fi
  if dirty=$(count_dirty "$repo"); then drc=0; else drc=$?; fi
  if scratch=$(scratch_of "$repo/.scratch"); then src=0; else src=$?; fi
  if [ "$src" = 3 ]; then symlink=1; fi
  if is_detached "$repo"; then detached=1; fi
  if ! has_remote_branch "$repo"; then no_remote=1; fi
  epoch=$(newest_epoch "$repo")
  mt=$(epoch_to_iso "$epoch")
  local flags
  flags=$(build_flags "$wt" "$un" "$dirty" "$scratch" "$no_commits" "$detached" "$no_remote" "$symlink")
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$repo" "$wt" "$un" "$dirty" "$scratch" "$mt" "$flags"
}

census_root() {
  local root=$1 repo
  local -a lines=()
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    lines+=("$(census_one "$repo")")
  done < <(discover_repos "$root" | LC_ALL=C sort -u)
  if [ ${#lines[@]} -eq 0 ]; then
    return 0
  fi
  printf '%s\n' "${lines[@]}" | LC_ALL=C sort -t $'\t' -k1,1
}

compare_incomparable() {
  local reason=$1
  printf '%s: compare file is not a census-v1 TSV (%s)\n' "$TOOL" "$reason" >&2
  printf '%s\n' "$COMPARE_HEADER"
  printf 'incomparable\t-\tschema\t%s\tcensus-v1\n' "$reason"
  printf 'summary\tcompared=0\tunchanged=0\tchanged=0\tadded=0\tremoved=0\tincomparable=1\n'
}

compare_against() {
  local prev=$1 current=$2
  local line n=0 header repo wt un dirty scratch mt flags
  local -a clines=()
  declare -A SEEN=()
  declare -A BWT=() BUN=() BDIRTY=() BSCR=() BMT=() BFLAGS=()

  if [ ! -f "$prev" ] || [ -L "$prev" ]; then
    usage_err "compare file is missing or not a regular file"
  fi
  if refuse_path "$prev"; then
    usage_err "refusing to read restricted compare path"
  fi

  header=$(head -n 1 -- "$prev" || true)
  if [ -z "$header" ]; then
    compare_incomparable empty
    return 0
  fi
  if [ "$header" != "$HEADER" ]; then
    compare_incomparable header-mismatch
    return 0
  fi

  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    [ "$n" = 1 ] && continue
    [ -n "$line" ] || continue
    IFS=$'\t' read -r repo wt un dirty scratch mt flags <<< "$line"
    if [ -z "$repo" ] || [ -z "${flags+x}" ] || [ -z "$wt" ] || [ -z "$un" ] || [ -z "$dirty" ] || [ -z "$scratch" ] || [ -z "$mt" ] || [ -z "$flags" ]; then
      compare_incomparable bad-row
      return 0
    fi
    # 7 fields: exactly 6 tabs.
    local tabs=${line//[!$'\t']/}
    if [ "${#tabs}" -ne 6 ]; then
      compare_incomparable bad-row
      return 0
    fi
    if [ -n "${BWT[$repo]+x}" ]; then
      compare_incomparable duplicate-repo
      return 0
    fi
    BWT["$repo"]=$wt
    BUN["$repo"]=$un
    BDIRTY["$repo"]=$dirty
    BSCR["$repo"]=$scratch
    BMT["$repo"]=$mt
    BFLAGS["$repo"]=$flags
  done < "$prev"

  local changed=0 unchanged=0 added=0 removed=0
  local -a out=()
  while IFS= read -r line || [ -n "$line" ]; do
    [ -n "$line" ] || continue
    IFS=$'\t' read -r repo wt un dirty scratch mt flags <<< "$line"
    SEEN["$repo"]=1
    if [ -z "${BWT[$repo]+x}" ]; then
      added=$((added + 1))
      out+=("added"$'\t'"$repo"$'\t'"*"$'\t'"-"$'\t'"present")
      continue
    fi
    local diffed=0 field old new
    local -a fields=(worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)
    local -a cur=("$wt" "$un" "$dirty" "$scratch" "$mt" "$flags")
    local -a olds=("${BWT[$repo]}" "${BUN[$repo]}" "${BDIRTY[$repo]}" "${BSCR[$repo]}" "${BMT[$repo]}" "${BFLAGS[$repo]}")
    local i
    for i in 0 1 2 3 4 5; do
      if [ "${cur[$i]}" != "${olds[$i]}" ]; then
        diffed=1
        out+=("changed"$'\t'"$repo"$'\t'"${fields[$i]}"$'\t'"${olds[$i]}"$'\t'"${cur[$i]}")
      fi
    done
    if [ "$diffed" = 1 ]; then
      changed=$((changed + 1))
    else
      unchanged=$((unchanged + 1))
      out+=("unchanged"$'\t'"$repo"$'\t'"*"$'\t'"-"$'\t'"-")
    fi
  done <<< "$current"

  local brepo
  for brepo in "${!BWT[@]}"; do
    if [ -z "${SEEN[$brepo]+x}" ]; then
      removed=$((removed + 1))
      out+=("removed"$'\t'"$brepo"$'\t'"*"$'\t'"present"$'\t'"-")
    fi
  done

  local compared=$((unchanged + changed + added + removed))
  printf '%s\n' "$COMPARE_HEADER"
  if [ ${#out[@]} -gt 0 ]; then
    printf '%s\n' "${out[@]}" | LC_ALL=C sort -t $'\t' -k2,2 -k3,3
  fi
  printf 'summary\tcompared=%s\tunchanged=%s\tchanged=%s\tadded=%s\tremoved=%s\tincomparable=0\n' \
    "$compared" "$unchanged" "$changed" "$added" "$removed"
}

emit_census() {
  local root=$1 rows
  rows=$(census_root "$root")
  printf '%s\n' "$HEADER"
  if [ -n "$rows" ]; then
    printf '%s\n' "$rows"
  fi
}

selftest() {
  local tmp="" root win iso base probe
  local passes=0
  local -a bases=()
  [ -n "${TMPDIR:-}" ] && bases+=("$TMPDIR")
  bases+=(/var/tmp /tmp)
  for base in "${bases[@]}"; do
    [ -d "$base" ] && [ -w "$base" ] || continue
    probe=$(mktemp -d "$base/souji-census-45.XXXXXX" 2>/dev/null) || continue
    if git --no-optional-locks init -q "$probe/probe" 2>/dev/null; then
      tmp=$probe
      break
    fi
  done
  [ -n "$tmp" ] || { printf 'selftest FAIL no writable temp for fixtures\n' >&2; exit 1; }
  root="$tmp/fleet"
  win=1736942400
  mkdir -p "$root"
  iso=$(date -d "@$win" --iso-8601=seconds)

  fail() { printf 'selftest FAIL %s\n' "$*" >&2; printf 'selftest_tmp=%s\n' "$tmp" >&2; exit 1; }
  eq() { [ "$1" = "$2" ] || fail "$3: got [$1] want [$2]"; passes=$((passes + 1)); }
  absent() { if grep -F -q -e "$2" -- "$1"; then fail "marker present: $2"; fi; passes=$((passes + 1)); }

  fixture_commit() {
    local repo=$1 msg=$2 when=$3 tree parent commit
    tree=$(git --no-optional-locks -C "$repo" write-tree)
    if git --no-optional-locks -C "$repo" rev-parse --verify refs/heads/main >/dev/null 2>&1; then
      parent=$(git --no-optional-locks -C "$repo" rev-parse refs/heads/main)
      commit=$(GIT_AUTHOR_NAME=souji GIT_AUTHOR_EMAIL=souji@shokunin.local GIT_AUTHOR_DATE="$when" \
               GIT_COMMITTER_NAME=souji GIT_COMMITTER_EMAIL=souji@shokunin.local GIT_COMMITTER_DATE="$when" \
               git --no-optional-locks -C "$repo" commit-tree "$tree" -p "$parent" -m "$msg")
    else
      commit=$(GIT_AUTHOR_NAME=souji GIT_AUTHOR_EMAIL=souji@shokunin.local GIT_AUTHOR_DATE="$when" \
               GIT_COMMITTER_NAME=souji GIT_COMMITTER_EMAIL=souji@shokunin.local GIT_COMMITTER_DATE="$when" \
               git --no-optional-locks -C "$repo" commit-tree "$tree" -m "$msg")
    fi
    git --no-optional-locks -C "$repo" update-ref refs/heads/main "$commit"
    git --no-optional-locks -C "$repo" symbolic-ref HEAD refs/heads/main
  }
  pin_remote() {
    local repo=$1 sha
    sha=$(git --no-optional-locks -C "$repo" rev-parse refs/heads/main)
    git --no-optional-locks -C "$repo" update-ref refs/remotes/origin/main "$sha"
  }

  # clean: pushed, one worktree, off-limits untracked files must not count or win mtime.
  git --no-optional-locks init -q "$root/clean"
  printf 'README-CONTENT-45\n' > "$root/clean/README"
  git --no-optional-locks -C "$root/clean" add -- README
  fixture_commit "$root/clean" base '2026-01-01T00:00:00-03:00'
  pin_remote "$root/clean"
  mkdir -p "$root/clean/.ufo/state"
  printf 'state\n' > "$root/clean/.ufo/state/x"
  printf 'watch\n' > "$root/clean/.ufo/watchdog.log"
  touch -d "@$((win + 9000))" "$root/clean/.ufo/state/x" "$root/clean/.ufo/watchdog.log"
  touch -d "@$win" "$root/clean/README"

  # dirty: 1 unpushed, modified + untracked, scratch, extra detached worktree, secret decoys.
  git --no-optional-locks init -q "$root/dirty"
  printf 'base\n' > "$root/dirty/README"
  git --no-optional-locks -C "$root/dirty" add -- README
  fixture_commit "$root/dirty" base '2026-01-01T00:00:00-03:00'
  pin_remote "$root/dirty"
  printf 'base\nmore\n' > "$root/dirty/README"
  git --no-optional-locks -C "$root/dirty" add -- README
  fixture_commit "$root/dirty" second '2026-01-02T00:00:00-03:00'
  printf 'base\nmore\ndirty\n' > "$root/dirty/README"
  printf 'extra\n' > "$root/dirty/extra.txt"
  mkdir -p "$root/dirty/.scratch" "$root/dirty/.ufo/state" "$root/dirty/subdir/credentials"
  printf 'abcd' > "$root/dirty/.scratch/a.txt"
  printf 'SECRET-MARKER-45\n' > "$root/dirty/id_rsa"
  printf 'ENV-MARKER-45\n' > "$root/dirty/.env.local"
  printf 'cred\n' > "$root/dirty/subdir/credentials/note.txt"
  printf 'state\n' > "$root/dirty/.ufo/state/x"
  printf 'watch\n' > "$root/dirty/.ufo/watchdog.log"
  touch -d "@$((win - 100))" "$root/dirty/extra.txt" "$root/dirty/.scratch/a.txt"
  touch -d "@$((win + 9000))" \
    "$root/dirty/id_rsa" "$root/dirty/.env.local" \
    "$root/dirty/.ufo/state/x" "$root/dirty/.ufo/watchdog.log" \
    "$root/dirty/subdir/credentials/note.txt"
  touch -d "@$win" "$root/dirty/README"
  git --no-optional-locks -C "$root/dirty" worktree add --detach "$tmp/wt-dirty" HEAD >/dev/null 2>&1

  # fresh: no commit, no remote.
  git --no-optional-locks init -q "$root/fresh"

  # local-only: one commit, no remote-tracking branch.
  git --no-optional-locks init -q "$root/localonly"
  printf 'local\n' > "$root/localonly/README"
  git --no-optional-locks -C "$root/localonly" add -- README
  fixture_commit "$root/localonly" local '2026-01-01T00:00:00-03:00'
  touch -d "@$win" "$root/localonly/README"

  # scratch symlink must not be followed and its target content must not appear.
  git --no-optional-locks init -q "$root/linkscratch"
  printf 'link\n' > "$root/linkscratch/README"
  git --no-optional-locks -C "$root/linkscratch" add -- README
  fixture_commit "$root/linkscratch" link '2026-01-01T00:00:00-03:00'
  pin_remote "$root/linkscratch"
  printf 'TARGETDATA\n' > "$tmp/target-file"
  ln -s "$tmp/target-file" "$root/linkscratch/.scratch"
  touch -d "@$win" "$root/linkscratch/README"

  # not a repo, bare repo, secret-named repo, symlink child: all omitted.
  mkdir -p "$root/notes"
  printf 'note\n' > "$root/notes/n.txt"
  git --no-optional-locks init --bare -q "$root/bare.git"
  git --no-optional-locks init -q "$root/id_skip"
  printf 'SHOULD-NOT-APPEAR\n' > "$root/id_skip/marker.txt"
  ln -s clean "$root/clean-link"

  local idx_before cfg_before
  idx_before=$(sha256sum "$root/dirty/.git/index" "$root/clean/.git/index")
  cfg_before=$(sha256sum "$root/dirty/.git/config" "$root/clean/.git/config")

  "$SELF" --root "$root" > "$tmp/out.tsv"
  eq "$(head -n 1 "$tmp/out.tsv")" "$HEADER" header

  local repos want
  repos=$(tail -n +2 "$tmp/out.tsv" | cut -f1)
  want=$(printf '%s\n' "$root/clean" "$root/dirty" "$root/fresh" "$root/linkscratch" "$root/localonly" | LC_ALL=C sort)
  eq "$repos" "$want" repo-set
  absent "$tmp/out.tsv" "$root/notes"
  absent "$tmp/out.tsv" "$root/bare.git"
  absent "$tmp/out.tsv" "$root/id_skip"
  absent "$tmp/out.tsv" "$root/clean-link"
  absent "$tmp/out.tsv" "$tmp/wt-dirty"
  absent "$tmp/out.tsv" 'SECRET-MARKER-45'
  absent "$tmp/out.tsv" 'ENV-MARKER-45'
  absent "$tmp/out.tsv" 'SHOULD-NOT-APPEAR'
  absent "$tmp/out.tsv" 'TARGETDATA'
  absent "$tmp/out.tsv" 'README-CONTENT-45'

  row_of() { awk -F '\t' -v r="$1" '$1==r {print; exit}' "$tmp/out.tsv"; }
  local row
  row=$(row_of "$root/clean")
  eq "$row" "$root/clean"$'\t'"1"$'\t'"0"$'\t'"0"$'\t'"0"$'\t'"$iso"$'\t'"ok" clean-row
  # raw status sees the off-limits files; the row above proves they were dropped.
  git --no-optional-locks -C "$root/clean" status --porcelain --untracked-files=all > "$tmp/clean-status.txt"
  grep -F -q '.ufo/watchdog.log' "$tmp/clean-status.txt" || fail 'clean fixture did not surface watchdog.log'
  passes=$((passes + 1))
  grep -F -q '.ufo/state' "$tmp/clean-status.txt" || fail 'clean fixture did not surface .ufo/state'
  passes=$((passes + 1))

  local scratch_want link_want
  scratch_want=$(du -sb -- "$root/dirty/.scratch" | cut -f1)
  row=$(row_of "$root/dirty")
  eq "$row" "$root/dirty"$'\t'"2"$'\t'"1"$'\t'"6"$'\t'"$scratch_want"$'\t'"$iso"$'\t'"unpushed,dirty,extra-worktrees,scratch" dirty-row
  [ "$scratch_want" -ge 4 ] || fail "scratch bytes below payload: $scratch_want"
  passes=$((passes + 1))

  row=$(row_of "$root/fresh")
  eq "$row" "$root/fresh"$'\t'"1"$'\t'"0"$'\t'"0"$'\t'"0"$'\t'"-"$'\t'"no-commits,no-remote" fresh-row

  row=$(row_of "$root/localonly")
  eq "$row" "$root/localonly"$'\t'"1"$'\t'"1"$'\t'"0"$'\t'"0"$'\t'"$iso"$'\t'"no-remote,unpushed" local-row

  link_want=$(stat -c '%s' -- "$root/linkscratch/.scratch")
  row=$(row_of "$root/linkscratch")
  eq "$row" "$root/linkscratch"$'\t'"1"$'\t'"0"$'\t'"1"$'\t'"$link_want"$'\t'"$iso"$'\t'"dirty,scratch,scratch-symlink" link-row
  [ "$link_want" != 11 ] || fail 'symlink size collided with target payload length'
  passes=$((passes + 1))

  # independent hand-check commands, not the script's functions.
  local hw hu hd
  hw=$(git --no-optional-locks -C "$root/dirty" worktree list --porcelain | grep -c '^worktree ' || true)
  hu=$(git --no-optional-locks -C "$root/dirty" rev-list --count --branches --not --remotes)
  hd=$(git --no-optional-locks -C "$root/dirty" status --porcelain --untracked-files=all | awk '
    {
      p=substr($0,4)
      sub(/.* -> /,"",p)
      if (p ~ /^\.ufo\/state(\/|$)/ || p ~ /\/\.ufo\/state(\/|$)/) next
      if (p ~ /^\.ufo\/watchdog\.log$/ || p ~ /\/\.ufo\/watchdog\.log$/) next
      c++
    }
    END {print c+0}')
  eq "$hw" 2 hand-worktrees
  eq "$hu" 1 hand-unpushed
  eq "$hd" 6 hand-dirty

  eq "$(sha256sum "$root/dirty/.git/index" "$root/clean/.git/index")" "$idx_before" index-unchanged
  eq "$(sha256sum "$root/dirty/.git/config" "$root/clean/.git/config")" "$cfg_before" config-unchanged
  [ ! -e "$root/dirty/.git/index.lock" ] || fail 'index.lock appeared'
  passes=$((passes + 1))
  [ ! -e "$root/fresh/.git/index" ] || fail 'fresh census created an index'
  passes=$((passes + 1))

  SHOKUNIN_ROOT="$root" "$SELF" > "$tmp/default.tsv"
  eq "$(cat "$tmp/default.tsv")" "$(cat "$tmp/out.tsv")" default-root-env

  "$SELF" --root "$root" > "$tmp/out2.tsv"
  eq "$(cat "$tmp/out2.tsv")" "$(cat "$tmp/out.tsv")" idempotent

  # compare: tweak unpushed only, plus one removed repo.
  awk -F '\t' -v OFS='\t' -v d="$root/dirty" '
    NR==1 {print; next}
    $1==d {$3=0}
    {print}
    END {print "/tmp/souji-census-impl-45-gone\t1\t0\t0\t0\t-\tok"}
  ' "$tmp/out.tsv" > "$tmp/base.tsv"
  "$SELF" --root "$root" --compare "$tmp/base.tsv" > "$tmp/cmp.tsv"
  eq "$(head -n 1 "$tmp/cmp.tsv")" "$COMPARE_HEADER" compare-header
  grep -F -q "changed"$'\t'"$root/dirty"$'\t'"unpushed"$'\t'"0"$'\t'"1" "$tmp/cmp.tsv" || fail 'missing unpushed delta'
  passes=$((passes + 1))
  grep -F -q "unchanged"$'\t'"$root/clean"$'\t' "$tmp/cmp.tsv" || fail 'clean not unchanged'
  passes=$((passes + 1))
  grep -F -q $'removed\t/tmp/souji-census-impl-45-gone\t' "$tmp/cmp.tsv" || fail 'missing removed'
  passes=$((passes + 1))
  eq "$(tail -n 1 "$tmp/cmp.tsv")" "summary"$'\t'"compared=6"$'\t'"unchanged=4"$'\t'"changed=1"$'\t'"added=0"$'\t'"removed=1"$'\t'"incomparable=0" compare-summary

  printf 'seat\tpath\n' > "$tmp/round1.tsv"
  "$SELF" --root "$root" --compare "$tmp/round1.tsv" > "$tmp/inc.tsv"
  eq "$(sed -n '2p' "$tmp/inc.tsv")" $'incomparable\t-\tschema\theader-mismatch\tcensus-v1' incomparable
  eq "$(tail -n 1 "$tmp/inc.tsv")" "summary"$'\t'"compared=0"$'\t'"unchanged=0"$'\t'"changed=0"$'\t'"added=0"$'\t'"removed=0"$'\t'"incomparable=1" incomparable-summary

  : > "$tmp/empty.tsv"
  "$SELF" --root "$root" --compare "$tmp/empty.tsv" > "$tmp/empty-cmp.tsv"
  grep -F -q $'incomparable\t-\tschema\tempty\t' "$tmp/empty-cmp.tsv" || fail 'empty compare not incomparable'
  passes=$((passes + 1))

  printf 'PEM-MARKER\n' > "$tmp/secret-compare.pem"
  set +e
  "$SELF" --root "$root" --compare "$tmp/secret-compare.pem" > "$tmp/pem.out" 2> "$tmp/pem.err"
  local pem_rc=$?
  set -e
  eq "$pem_rc" 2 pem-refuse
  absent "$tmp/pem.out" 'PEM-MARKER'
  absent "$tmp/pem.err" 'PEM-MARKER'

  printf 'ledger\n' > "$tmp/obsidian-ledger.tsv"
  set +e
  "$SELF" --root "$root" --compare "$tmp/obsidian-ledger.tsv" > "$tmp/led.out" 2> "$tmp/led.err"
  local led_rc=$?
  set -e
  eq "$led_rc" 2 ledger-refuse
  absent "$tmp/led.out" 'ledger'

  mkdir -p "$tmp/.ufo/state"
  printf 'x\n' > "$tmp/.ufo/state/c.tsv"
  set +e
  "$SELF" --root "$root" --compare "$tmp/.ufo/state/c.tsv" > "$tmp/ufo.out" 2> "$tmp/ufo.err"
  local ufo_rc=$?
  set -e
  eq "$ufo_rc" 2 ufo-refuse

  set +e
  "$SELF" --root "$tmp/no-such-root" > "$tmp/miss.out" 2> "$tmp/miss.err"
  local miss_rc=$?
  "$SELF" --selftest --root "$root" > "$tmp/mix.out" 2> "$tmp/mix.err"
  local mix_rc=$?
  "$SELF" --compare > "$tmp/noc.out" 2> "$tmp/noc.err"
  local noc_rc=$?
  set -e
  eq "$miss_rc" 2 missing-root
  eq "$mix_rc" 2 selftest-exclusive
  eq "$noc_rc" 2 compare-needs-file

  # static safety: no forbidden porcelain, no rm, in the executable body.
  if grep -v -E '^[[:space:]]*#' "$SELF" | grep -E 'git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(fetch|push|commit|branch|prune|checkout|reset|rebase|clean)([[:space:]]|$)'; then
    fail 'forbidden git subcommand in body'
  fi
  passes=$((passes + 1))
  if grep -v -E '^[[:space:]]*#' "$SELF" | grep -E '(^|[[:space:]])rm[[:space:]]'; then
    fail 'rm in body'
  fi
  passes=$((passes + 1))

  bash -n "$SELF" || fail 'bash -n'
  passes=$((passes + 1))

  printf 'selftest ok cases=%s\n' "$passes"
}

ROOT=""
ROOT_SET=0
COMPARE=""
DO_SELFTEST=0

set_root() {
  if [ "$ROOT_SET" = 1 ]; then
    usage_err "multiple roots"
  fi
  ROOT=$1
  ROOT_SET=1
}

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) DO_SELFTEST=1; shift ;;
    --help|-h) usage 0 ;;
    --compare)
      [ $# -ge 2 ] || usage_err "--compare needs a file"
      COMPARE=$2
      shift 2
      ;;
    --root)
      [ $# -ge 2 ] || usage_err "--root needs a directory"
      set_root "$2"
      shift 2
      ;;
    --) shift; break ;;
    -*) usage_err "unknown option: $1" ;;
    *) set_root "$1"; shift ;;
  esac
done
while [ $# -gt 0 ]; do
  set_root "$1"
  shift
done

if [ "$DO_SELFTEST" = 1 ]; then
  if [ "$ROOT_SET" = 1 ] || [ -n "$COMPARE" ]; then
    usage_err "--selftest does not take a root or --compare"
  fi
  selftest
  exit 0
fi

if [ "$ROOT_SET" = 0 ]; then
  if [ -n "${SHOKUNIN_ROOT:-}" ]; then
    ROOT=$SHOKUNIN_ROOT
  else
    ROOT=$(dirname -- "$REPO_ROOT")
  fi
fi

if refuse_path "$ROOT"; then
  usage_err "refusing restricted root"
fi
if [ ! -d "$ROOT" ]; then
  usage_err "root is not a directory: $ROOT"
fi
ROOT=$(readlink -f -- "$ROOT")

if [ -n "$COMPARE" ]; then
  rows=$(census_root "$ROOT")
  compare_against "$COMPARE" "$rows"
else
  emit_census "$ROOT"
fi
