#!/usr/bin/env bash
# souji-census.impl-46 — repeatable read-only fleet census (round 6, seat S46).
#
# Contract (O1): for every repo directory in a root (default $SHOKUNIN_ROOT),
# emit one TSV row:
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#
# Counting commands (hand-check these; the -c/--no-optional-locks wrappers do
# not change the counts — they only refuse index writes and auto-gc):
#   worktrees:     git -C <repo> worktree list | wc -l
#   unpushed:      git -C <repo> log --branches --not --remotes --oneline | wc -l
#   dirty:         git -C <repo> status --porcelain | wc -l
#   scratch_bytes: du -sb <repo>/.scratch   (0 if absent; a symlink is NOT
#                  followed — du -sb reports the link's own size)
#   mtime_iso:     newest regular file under <repo>, fractional second
#                  truncated, formatted with `date -d @EPOCH --iso-8601=seconds`.
#                  Excluded from the walk (not opened, not stated as the max):
#                  .git, .ufo/state, .ufo/watchdog.log, and secret-shaped
#                  names (*.env, *credential*, *secret*, id_*, *.pem, .envrc).
#
# verdict_flags (fixed order, comma-separated, no spaces):
#   clean            unpushed=0 and dirty=0 and the repo has a HEAD commit
#   unpushed         unpushed>0
#   dirty            dirty>0
#   scratch          scratch_bytes>0
#   scratch-symlink  .scratch is a symlink (not followed)
#   multi-worktree   worktrees>1
#   no-remote        no refs/remotes/* (unpushed then counts every local commit)
#   unborn           no HEAD commit yet
#   git-error        a required git command failed; numeric fields may be "-"
#   measure-error    du or the mtime walk failed
#   secrets-refusal  a path component is secret-shaped; nothing inside was read
# `clean` is a git-tree observation, not a removal receipt.
#
# Discovery: the root itself if it contains .git, plus immediate child
# directories (not symlinks) that contain .git. Worktrees are counted on the
# owning repo; they are not separate rows unless they are themselves depth-1
# children of the root. Depth is 1 so a lane's nested checkouts are not
# double-counted.
#
# --compare PREV.tsv
#   Diff the live census against a previous TSV. Header-driven: only columns
#   present in BOTH files are compared (repo, worktrees, unpushed, dirty,
#   scratch_bytes, mtime_iso, verdict_flags). A basename match is used when
#   the basename is unique on both sides (absolute vs short name).
#   Drift is a finding, not an error: exit stays 0.
#   A TSV with no overlapping metric columns (round-1 artifact census is this
#   shape) prints COMPARE_SCHEMA incompatible and exits 0 — it is not a crash.
#   Secret-shaped compare paths are refused unread (exit 2).
#
# --selftest
#   Build a fixture fleet under mktemp (probes TMPDIR, /var/tmp, /tmp, ~/tmp;
#   /tmp on this host can be over quota) and assert the counts. Never scans
#   the live fleet. Exit 0 on pass, 1 on failure.
#
# Exit codes: 0 evaluated (including compare drift and an incompatible
# schema); 1 selftest failure or git missing; 2 usage / missing input.
# No other codes. No network. No git fetch/push/commit/branch/checkout/reset/
# rebase/prune. No writes outside the selftest mktemp dir. No reads of
# secret-shaped files (metadata census only — file contents are never opened).
set -uo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE GIT_PREFIX 2>/dev/null || true
export GIT_OPTIONAL_LOCKS=0
export LC_ALL=C

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
DEFAULT_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"

HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'
METRICS=(worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)

SELFTEST=0
ROOT=""
ROOT_SET=0
COMPARE=""
POSITIONAL=()

usage() {
  sed -n '2,48p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

die_usage() { printf 'souji-census.impl-46: %s\n' "$1" >&2; usage 2; }

is_secret_shaped() {
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    [ -n "$comp" ] || continue
    lc=${comp,,}
    case "$lc" in
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem) set +f; return 0 ;;
    esac
  done
  set +f
  return 1
}

canon() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

git_ro() { # git_ro <repo> <git-args...>
  git -C "$1" \
    --no-optional-locks \
    -c safe.directory='*' \
    -c color.ui=never \
    -c maintenance.auto=false \
    -c core.fsmonitor= \
    "${@:2}"
}

git_count() { # git_count <repo> <git-args...>  -> integer on stdout
  local n
  if ! n=$(git_ro "$1" "${@:2}" | wc -l); then
    return 1
  fi
  n=${n//[[:space:]]/}
  [ -n "$n" ] || n=0
  printf '%s' "$n"
}

scratch_measure() { # scratch_measure <repo> ; prints bytes, sets SCRATCH_LINK
  SCRATCH_LINK=0
  local s="$1/.scratch"
  if [ ! -e "$s" ] && [ ! -L "$s" ]; then
    printf '0'
    return 0
  fi
  if [ -L "$s" ]; then
    SCRATCH_LINK=1
  fi
  if is_secret_shaped "$s"; then
    return 3
  fi
  local line
  if ! line=$(du -sb -- "$s" 2>/dev/null); then
    return 1
  fi
  printf '%s' "${line%%[[:space:]]*}"
}

newest_epoch() { # newest_epoch <repo> ; integer epoch or empty
  # Metadata only (find -printf). Does not open file contents.
  # Prunes .git, off-limits driver files, and secret-shaped names so a
  # credential file can never become the reported mtime and is never opened.
  find -P "$1" \
    \( -name .git \
       -o -path '*/.ufo/state' \
       -o -path '*/.ufo/watchdog.log' \
       -o -name '.env' \
       -o -name '.envrc' \
       -o -name '*.env' \
       -o -name '.env.*' \
       -o -iname '*credential*' \
       -o -iname '*secret*' \
       -o -iname 'id_*' \
       -o -iname '*.pem' \
    \) -prune \
    -o -type f -printf '%T@\n' 2>/dev/null \
    | awk 'BEGIN{m=-1} {v=$1+0; if (v>m) m=v} END{if (m>=0) printf "%d", m}'
}

epoch_iso() {
  [ -n "$1" ] || return 1
  date -d "@$1" --iso-8601=seconds 2>/dev/null
}

join_flags() { # join_flags <name> <name> ...
  local out="" f
  for f in "$@"; do
    [ -n "$f" ] || continue
    if [ -z "$out" ]; then out=$f; else out="$out,$f"; fi
  done
  printf '%s' "$out"
}

measure_repo() { # prints one TSV data line (no header)
  local repo=$1
  if is_secret_shaped "$repo"; then
    printf '%s\t-\t-\t-\t-\t-\tsecrets-refusal\n' "$repo"
    return 0
  fi
  local worktrees="" unpushed="" dirty="" scratch="" mtime="" git_error=0 measure_error=0 unborn=0 no_remote=0
  SCRATCH_LINK=0
  if ! worktrees=$(git_count "$repo" worktree list); then
    worktrees='-'
    git_error=1
  fi
  if ! git_ro "$repo" rev-parse --verify --quiet HEAD >/dev/null 2>&1; then
    unborn=1
    unpushed=0
  elif ! unpushed=$(git_count "$repo" log --branches --not --remotes --oneline); then
    unpushed='-'
    git_error=1
  fi
  if ! dirty=$(git_count "$repo" status --porcelain); then
    dirty='-'
    git_error=1
  fi
  local nrem
  if nrem=$(git_count "$repo" for-each-ref --format=x refs/remotes); then
    if [ "$nrem" = 0 ]; then
      no_remote=1
    fi
  else
    git_error=1
  fi
  local sb_rc=0
  # scratch_measure runs in a subshell below; detect the symlink here so the
  # flag is not lost. du -sb does not follow the link (size stays the link's).
  if [ -L "$repo/.scratch" ]; then
    SCRATCH_LINK=1
  fi
  scratch=$(scratch_measure "$repo") || sb_rc=$?
  if [ "$sb_rc" -eq 3 ]; then
    printf '%s\t-\t-\t-\t-\t-\tsecrets-refusal\n' "$repo"
    return 0
  elif [ "$sb_rc" -ne 0 ]; then
    scratch='-'
    measure_error=1
  fi
  local epoch=""
  epoch=$(newest_epoch "$repo" || true)
  if [ -z "$epoch" ]; then
    # An empty tree is not an error. A find failure that produced nothing
    # looks the same; leave mtime empty rather than invent a timestamp.
    mtime=""
  elif ! mtime=$(epoch_iso "$epoch"); then
    mtime='-'
    measure_error=1
  fi
  local -a flagset=()
  if [ "$git_error" -eq 0 ] && [ "$unborn" -eq 0 ] \
     && [ "$unpushed" = 0 ] && [ "$dirty" = 0 ]; then
    flagset+=(clean)
  fi
  [ "$unpushed" != 0 ] && [ "$unpushed" != '-' ] && flagset+=(unpushed)
  [ "$dirty" != 0 ] && [ "$dirty" != '-' ] && flagset+=(dirty)
  if [[ "$scratch" =~ ^[0-9]+$ ]] && [ "$scratch" -gt 0 ]; then
    flagset+=(scratch)
  fi
  [ "$SCRATCH_LINK" -eq 1 ] && flagset+=(scratch-symlink)
  if [[ "$worktrees" =~ ^[0-9]+$ ]] && [ "$worktrees" -gt 1 ]; then
    flagset+=(multi-worktree)
  fi
  [ "$no_remote" -eq 1 ] && flagset+=(no-remote)
  [ "$unborn" -eq 1 ] && flagset+=(unborn)
  [ "$git_error" -eq 1 ] && flagset+=(git-error)
  [ "$measure_error" -eq 1 ] && flagset+=(measure-error)
  local flags
  flags=$(join_flags "${flagset[@]}")
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$repo" "$worktrees" "$unpushed" "$dirty" "$scratch" "$mtime" "$flags"
}

discover_repos() { # discover_repos <root> ; one absolute path per line, sorted
  local root=$1 d base
  if [ -e "$root/.git" ] || [ -L "$root/.git" ]; then
    printf '%s\n' "$root"
  fi
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    base=${d##*/}
    [ "$base" = .git ] && continue
    # -type d already skipped symlinks; re-check so a racing replacement
    # cannot pull the walk outside the root.
    [ -d "$d" ] && [ ! -L "$d" ] || continue
    [ -e "$d/.git" ] || [ -L "$d/.git" ] || continue
    printf '%s\n' "$d"
  done < <(find -P "$root" -mindepth 1 -maxdepth 1 -type d -printf '%p\n' 2>/dev/null | LC_ALL=C sort)
}

census_body() { # census_body <root> ; data lines only
  local repo
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    measure_repo "$repo"
  done < <(discover_repos "$1")
}

emit_census() { # emit_census <root>
  printf '%s\n' "$HEADER"
  census_body "$1"
}

# ---------------------------------------------------------------- compare

split_fields() { # split_fields <delim-tab|space> <line>  -> NUL-separated? use global FIELDS
  FIELDS=()
  local delim=$1 line=$2
  if [ "$delim" = tab ]; then
    local IFS=$'\t'
    read -r -a FIELDS <<< "$line"
  else
    # shellcheck disable=SC2206
    FIELDS=($line)
  fi
}

detect_delim() {
  case "$1" in
    *$'\t'*) printf 'tab' ;;
    *) printf 'space' ;;
  esac
}

is_int() { [[ "$1" =~ ^-?[0-9]+$ ]]; }

run_compare() { # run_compare <root> <prev-tsv>
  local root=$1 prev=$2
  if [ ! -f "$prev" ]; then
    printf 'souji-census.impl-46: compare file not found: %s\n' "$prev" >&2
    return 2
  fi
  if is_secret_shaped "$prev"; then
    printf 'souji-census.impl-46: refusing secret-shaped compare path\n' >&2
    return 2
  fi
  # GNU grep treats a NUL pattern as empty and matches every file. Compare
  # the file to itself with NULs stripped instead.
  if ! cmp -s "$prev" <(tr -d '\0' < "$prev"); then
    printf 'souji-census.impl-46: compare file is not text\n' >&2
    return 2
  fi

  local delim="" header="" line n=0
  local -a hfields=()
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line#$'\xef\xbb\xbf'}
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    case "$line" in
      \#*) continue ;;
    esac
    header=$line
    delim=$(detect_delim "$header")
    split_fields "$delim" "$header"
    hfields=("${FIELDS[@]}")
    break
  done < "$prev"
  if [ -z "$header" ]; then
    printf 'COMPARE_SCHEMA\tincompatible\treason=empty-file\theader=\n'
    printf 'COMPARE_SUMMARY\tadded=0\tremoved=0\tchanged=0\tunchanged=0\tschema=incompatible\n'
    return 0
  fi

  declare -A HIDX=()
  local i name
  for i in "${!hfields[@]}"; do
    name=${hfields[$i]}
    [ -n "$name" ] || continue
    HIDX["$name"]=$i
  done

  local -a compared=()
  if [ -n "${HIDX[repo]+x}" ]; then
    local m
    for m in "${METRICS[@]}"; do
      [ -n "${HIDX[$m]+x}" ] && compared+=("$m")
    done
  fi
  if [ "${#compared[@]}" -eq 0 ]; then
    local shown=""
    shown=$(printf '%s,' "${hfields[@]}" | head -c 180)
    shown=${shown%,}
    printf 'COMPARE_SCHEMA\tincompatible\treason=no-overlapping-metric-columns\theader=%s\n' "$shown"
    printf 'COMPARE_SUMMARY\tadded=0\tremoved=0\tchanged=0\tunchanged=0\tschema=incompatible\tcompared=\n'
    return 0
  fi

  declare -A PREV_LINE=()
  declare -A PREV_BASE_N=()
  declare -A PREV_BASE_KEY=()
  local repo_i=${HIDX[repo]}
  local dup=0
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    case "$line" in
      \#*) continue ;;
    esac
    n=$((n+1))
    [ "$n" -eq 1 ] && continue
    split_fields "$delim" "$line"
    local key="${FIELDS[$repo_i]:-}"
    [ -n "$key" ] || continue
    if [ -n "${PREV_LINE[$key]+x}" ]; then
      dup=$((dup+1))
    fi
    PREV_LINE["$key"]=$line
    local b=${key##*/}
    PREV_BASE_N["$b"]=$(( ${PREV_BASE_N[$b]:-0} + 1 ))
    PREV_BASE_KEY["$b"]=$key
  done < "$prev"

  local current
  current=$(emit_census "$root") || return 1

  declare -A CUR_LINE=()
  declare -A CUR_BASE_N=()
  declare -A CUR_BASE_KEY=()
  local first=1
  while IFS= read -r line || [ -n "$line" ]; do
    [ -n "$line" ] || continue
    if [ "$first" -eq 1 ]; then
      first=0
      continue
    fi
    local crepo=${line%%$'\t'*}
    CUR_LINE["$crepo"]=$line
    local cb=${crepo##*/}
    CUR_BASE_N["$cb"]=$(( ${CUR_BASE_N[$cb]:-0} + 1 ))
    CUR_BASE_KEY["$cb"]=$crepo
  done <<< "$current"

  # Map each current repo to a previous key (exact, else unique basename).
  declare -A MATCHED_PREV=()
  declare -A USED_PREV=()
  local crepo
  for crepo in "${!CUR_LINE[@]}"; do
    if [ -n "${PREV_LINE[$crepo]+x}" ]; then
      MATCHED_PREV["$crepo"]=$crepo
      USED_PREV["$crepo"]=1
      continue
    fi
    local cb=${crepo##*/}
    if [ "${CUR_BASE_N[$cb]:-0}" -eq 1 ] && [ "${PREV_BASE_N[$cb]:-0}" -eq 1 ]; then
      local pk=${PREV_BASE_KEY[$cb]}
      # Do not basename-match a previous key that already exact-matched.
      if [ -z "${USED_PREV[$pk]+x}" ] && [ -z "${CUR_LINE[$pk]+x}" ]; then
        MATCHED_PREV["$crepo"]=$pk
        USED_PREV["$pk"]=1
      fi
    fi
  done

  local added=0 removed=0 changed=0 unchanged=0
  local -a out_lines=()
  local cur_keys
  cur_keys=$(printf '%s\n' "${!CUR_LINE[@]}" | LC_ALL=C sort)
  local cr
  while IFS= read -r cr; do
    [ -n "$cr" ] || continue
    if [ -z "${MATCHED_PREV[$cr]+x}" ]; then
      added=$((added+1))
      out_lines+=("$(printf 'COMPARE\tadded\t%s\t*\t-\t-\tadded' "$cr")")
      continue
    fi
    local pk=${MATCHED_PREV[$cr]}
    local pline=${PREV_LINE[$pk]}
    local cline=${CUR_LINE[$cr]}
    split_fields tab "$cline"
    local -a cfields=("${FIELDS[@]}")
    split_fields "$delim" "$pline"
    local -a pfields=("${FIELDS[@]}")
    local row_changed=0
    local m mi pi pv cv delta
    for m in "${compared[@]}"; do
      mi=${HIDX[$m]}
      # current census is always our header order
      case "$m" in
        worktrees) ci=1 ;;
        unpushed) ci=2 ;;
        dirty) ci=3 ;;
        scratch_bytes) ci=4 ;;
        mtime_iso) ci=5 ;;
        verdict_flags) ci=6 ;;
        *) ci=-1 ;;
      esac
      pv=${pfields[$mi]:-}
      cv=${cfields[$ci]:-}
      if [ "$pv" = "$cv" ]; then
        continue
      fi
      row_changed=1
      if is_int "$pv" && is_int "$cv"; then
        delta=$((cv - pv))
      else
        delta=na
      fi
      out_lines+=("$(printf 'COMPARE\tchanged\t%s\t%s\t%s\t%s\t%s' "$cr" "$m" "$pv" "$cv" "$delta")")
    done
    if [ "$row_changed" -eq 1 ]; then
      changed=$((changed+1))
    else
      unchanged=$((unchanged+1))
    fi
  done <<< "$cur_keys"

  local pk
  local prev_keys
  prev_keys=$(printf '%s\n' "${!PREV_LINE[@]}" | LC_ALL=C sort)
  while IFS= read -r pk; do
    [ -n "$pk" ] || continue
    [ -n "${USED_PREV[$pk]+x}" ] && continue
    removed=$((removed+1))
    out_lines+=("$(printf 'COMPARE\tremoved\t%s\t*\t-\t-\tremoved' "$pk")")
  done <<< "$prev_keys"

  local ol
  if [ "${#out_lines[@]}" -gt 0 ]; then
    printf '%s\n' "${out_lines[@]}" | LC_ALL=C sort
  fi
  local cmp_list
  cmp_list=$(join_flags "${compared[@]}")
  printf 'COMPARE_SUMMARY\tadded=%s\tremoved=%s\tchanged=%s\tunchanged=%s\tschema=souji-census-v1\tcompared=%s\tduplicate_prev=%s\n' \
    "$added" "$removed" "$changed" "$unchanged" "$cmp_list" "$dup"
  return 0
}

# ---------------------------------------------------------------- selftest

pick_workdir() {
  local -a cands=()
  local c t
  [ -n "${SOUJI_TMPDIR:-}" ] && cands+=("${SOUJI_TMPDIR}")
  [ -n "${TMPDIR:-}" ] && cands+=("${TMPDIR}")
  cands+=(/var/tmp /tmp "${HOME:-}/tmp")
  for c in "${cands[@]}"; do
    [ -n "$c" ] && [ -d "$c" ] && [ -w "$c" ] || continue
    # Never build fixtures inside the fleet or the lane repo.
    case "$(canon "$c")" in
      "$(canon "$DEFAULT_ROOT")"|"$(canon "$DEFAULT_ROOT")"/*) continue ;;
      "$(canon "$REPO_ROOT")"|"$(canon "$REPO_ROOT")"/*) continue ;;
    esac
    t=$(mktemp -d "$c/souji-census-selftest.XXXXXX" 2>/dev/null) || continue
    if git init -q -b main --template= "$t/probe" >/dev/null 2>&1; then
      rm -rf -- "$t/probe"
      printf '%s' "$t"
      return 0
    fi
    rm -rf -- "$t"
  done
  return 1
}

fixture_commit() { # fixture_commit <repo> <parent-sha-or-empty> ; prints sha
  local repo=$1 parent=$2 tree sha
  git -C "$repo" add -A -- >/dev/null
  tree=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(git -C "$repo" commit-tree "$tree" -p "$parent" -m fixture)
  else
    sha=$(git -C "$repo" commit-tree "$tree" -m fixture)
  fi
  git -C "$repo" update-ref refs/heads/main "$sha"
  printf '%s' "$sha"
}

fixture_publish() { # point origin/main at current HEAD
  local repo=$1 sha
  sha=$(git -C "$repo" rev-parse HEAD)
  git -C "$repo" update-ref refs/remotes/origin/main "$sha"
}

WORKDIR=""
cleanup_census_tmp() {
  local d="${WORKDIR-}"
  [ -n "$d" ] || return 0
  [ "${SOUJI_CENSUS_KEEP:-}" = 1 ] && return 0
  case "$d" in
    /tmp/souji-census-selftest.*|/var/tmp/souji-census-selftest.*|"${HOME:-}/tmp/souji-census-selftest."*|${SOUJI_TMPDIR:-/nonexistent}/souji-census-selftest.*)
      rm -rf -- "$d"
      WORKDIR=""
      ;;
  esac
  return 0
}

selftest() {
  WORKDIR=""
  trap cleanup_census_tmp EXIT

  if ! WORKDIR=$(pick_workdir); then
    printf 'SELFTEST pass=0 fail=1\n'
    printf 'FAIL no writable temp for fixtures\n' >&2
    return 1
  fi

  export GIT_AUTHOR_NAME=souji GIT_AUTHOR_EMAIL=souji@shokunin.local
  export GIT_COMMITTER_NAME=souji GIT_COMMITTER_EMAIL=souji@shokunin.local

  local pass=0 fail=0
  assert_eq() {
    local name=$1 exp=$2 got=$3
    if [ "$exp" = "$got" ]; then
      pass=$((pass+1))
    else
      fail=$((fail+1))
      printf 'FAIL %s\n  expected: [%s]\n  got:      [%s]\n' "$name" "$exp" "$got" >&2
    fi
  }
  assert_has() {
    local name=$1 needle=$2 hay=$3
    case "$hay" in
      *"$needle"*) pass=$((pass+1)) ;;
      *) fail=$((fail+1)); printf 'FAIL %s missing [%s]\n' "$name" "$needle" >&2 ;;
    esac
  }
  assert_lacks() {
    local name=$1 needle=$2 hay=$3
    case "$hay" in
      *"$needle"*) fail=$((fail+1)); printf 'FAIL %s unexpectedly contains [%s]\n' "$name" "$needle" >&2 ;;
      *) pass=$((pass+1)) ;;
    esac
  }

  local fleet="$WORKDIR/fleet"
  mkdir -p "$fleet"
  # Root repo, published, clean.
  git init -q -b main --template= "$fleet"
  printf 'root\n' > "$fleet/README"
  local rsha
  rsha=$(fixture_commit "$fleet" "")
  fixture_publish "$fleet"

  local clean="$fleet/clean-lane"
  git init -q -b main --template= "$clean"
  printf 'seed\n' > "$clean/seed.txt"
  printf 'marker\n' > "$clean/marker.txt"
  mkdir -p "$clean/.ufo"
  printf 'log\n' > "$clean/.ufo/watchdog.log"
  printf 'SECRET-SENTINEL-do-not-emit\n' > "$clean/app.env"
  # Stamp mtimes before the commit so status stays clean (content matches
  # the index) while the walk still has to ignore .git, watchdog, and .env.
  touch -d '2024-06-01 12:34:56' "$clean/seed.txt"
  touch -d '2024-07-02 01:02:03' "$clean/marker.txt"
  touch -d '2099-01-01 00:00:00' "$clean/.ufo/watchdog.log"
  touch -d '2030-01-01 00:00:00' "$clean/app.env"
  fixture_commit "$clean" "" >/dev/null
  fixture_publish "$clean"
  touch -d '2099-01-01 00:00:00' "$clean/.git/config"

  local dirty="$fleet/dirty-lane"
  git init -q -b main --template= "$dirty"
  printf 'base\n' > "$dirty/tracked.txt"
  fixture_commit "$dirty" "" >/dev/null
  fixture_publish "$dirty"
  printf 'changed\n' > "$dirty/tracked.txt"
  printf 'new\n' > "$dirty/extra.txt"

  local unpushed="$fleet/unpushed-lane"
  git init -q -b main --template= "$unpushed"
  printf 'one\n' > "$unpushed/f.txt"
  local usha
  usha=$(fixture_commit "$unpushed" "")
  fixture_publish "$unpushed"
  printf 'two\n' > "$unpushed/f.txt"
  fixture_commit "$unpushed" "$usha" >/dev/null

  local scratch="$fleet/scratch-lane"
  git init -q -b main --template= "$scratch"
  printf 's\n' > "$scratch/f.txt"
  printf '.scratch\n' > "$scratch/.gitignore"
  fixture_commit "$scratch" "" >/dev/null
  fixture_publish "$scratch"
  mkdir -p "$scratch/.scratch"
  printf 'abcd' > "$scratch/.scratch/blob"

  local wt="$fleet/wt-lane"
  git init -q -b main --template= "$wt"
  printf 'w\n' > "$wt/f.txt"
  fixture_commit "$wt" "" >/dev/null
  fixture_publish "$wt"
  git -C "$wt" worktree add --detach "$WORKDIR/outside-wt" HEAD >/dev/null

  local noremote="$fleet/noremote-lane"
  git init -q -b main --template= "$noremote"
  printf 'n\n' > "$noremote/f.txt"
  fixture_commit "$noremote" "" >/dev/null

  local slink="$fleet/slink-lane"
  git init -q -b main --template= "$slink"
  printf 'l\n' > "$slink/f.txt"
  printf '.scratch\nrealscratch\n' > "$slink/.gitignore"
  fixture_commit "$slink" "" >/dev/null
  fixture_publish "$slink"
  mkdir -p "$slink/realscratch"
  dd if=/dev/zero of="$slink/realscratch/big" bs=1024 count=8 status=none
  ln -s realscratch "$slink/.scratch"

  local unborn="$fleet/unborn-lane"
  git init -q -b main --template= "$unborn"

  mkdir -p "$fleet/not-a-repo"
  printf 'note\n' > "$fleet/README-extra"
  ln -s /var/tmp "$fleet/escape-link"

  mkdir -p "$fleet/id_rsa/.git"
  printf 'SECRET-SENTINEL-do-not-emit\n' > "$fleet/id_rsa/payload"

  local space="$fleet/space lane"
  git init -q -b main --template= "$space"
  printf 'sp\n' > "$space/f.txt"
  fixture_commit "$space" "" >/dev/null
  fixture_publish "$space"

  # Static ban scan: plumbing `commit-tree` must not match `git commit`.
  local banned
  banned=$(grep -nE 'git[[:space:]]+(fetch|push|commit|branch|checkout|reset|rebase|prune|clean)([[:space:]]|$)' "$SELF" || true)
  assert_eq "no banned git subcommand" "" "$banned"
  local prune_hit
  prune_hit=$(grep -nE 'git[[:space:]]+worktree[[:space:]]+prune' "$SELF" || true)
  assert_eq "no worktree prune" "" "$prune_hit"

  local out rc
  set +e
  out=$(bash "$SELF" --root "$fleet" 2>"$WORKDIR/err")
  rc=$?
  set -e
  assert_eq "census exit" "0" "$rc"
  assert_lacks "no secret content" "SECRET-SENTINEL-do-not-emit" "$out"
  assert_lacks "selftest does not scan live fleet" "/home/vgpnk/Projects/shokunin/kotodama-shokunin" "$out"
  assert_lacks "symlink child excluded" "escape-link" "$out"
  assert_lacks "non-repo excluded" "not-a-repo" "$out"

  local header
  header=$(printf '%s\n' "$out" | head -1)
  assert_eq "header" "$HEADER" "$header"

  field_of() { # field_of <repo-basename-or-path> <column-name>
    local key=$1 col=$2
    printf '%s\n' "$out" | awk -F '\t' -v key="$key" -v col="$col" '
      NR==1 { for (i=1;i<=NF;i++) if ($i==col) c=i; next }
      $1==key || $1 ~ ("/" key "$") { print $c; found=1; exit }
      END { if (!found) print "" }
    '
  }
  row_count() { printf '%s\n' "$out" | awk 'END{print NR-1}'; }

  # root + 9 child repos (clean, dirty, unpushed, scratch, wt, noremote,
  # slink, unborn, space) + secret id_rsa. not-a-repo and escape-link omitted.
  assert_eq "row count" "11" "$(row_count)"

  local fleet_c
  fleet_c=$(canon "$fleet")
  assert_eq "clean worktrees" "1" "$(field_of "$fleet_c/clean-lane" worktrees)"
  assert_eq "clean unpushed" "0" "$(field_of "$fleet_c/clean-lane" unpushed)"
  assert_eq "clean dirty" "0" "$(field_of "$fleet_c/clean-lane" dirty)"
  assert_eq "clean scratch" "0" "$(field_of "$fleet_c/clean-lane" scratch_bytes)"
  assert_eq "clean flags" "clean" "$(field_of "$fleet_c/clean-lane" verdict_flags)"
  local expect_iso
  expect_iso=$(date -d '2024-07-02 01:02:03' --iso-8601=seconds)
  assert_eq "clean mtime ignores .git and watchdog and uses marker not secret" \
    "$expect_iso" "$(field_of "$fleet_c/clean-lane" mtime_iso)"

  assert_eq "dirty count" "2" "$(field_of "$fleet_c/dirty-lane" dirty)"
  assert_eq "dirty flags" "dirty" "$(field_of "$fleet_c/dirty-lane" verdict_flags)"
  assert_eq "dirty unpushed" "0" "$(field_of "$fleet_c/dirty-lane" unpushed)"

  assert_eq "unpushed count" "1" "$(field_of "$fleet_c/unpushed-lane" unpushed)"
  assert_eq "unpushed dirty" "0" "$(field_of "$fleet_c/unpushed-lane" dirty)"
  assert_eq "unpushed flags" "unpushed" "$(field_of "$fleet_c/unpushed-lane" verdict_flags)"

  local du_scratch
  du_scratch=$(du -sb -- "$scratch/.scratch" | awk '{print $1}')
  assert_eq "scratch bytes match du -sb" "$du_scratch" "$(field_of "$fleet_c/scratch-lane" scratch_bytes)"
  assert_eq "scratch flags" "clean,scratch" "$(field_of "$fleet_c/scratch-lane" verdict_flags)"

  assert_eq "worktree count" "2" "$(field_of "$fleet_c/wt-lane" worktrees)"
  assert_eq "worktree flags" "clean,multi-worktree" "$(field_of "$fleet_c/wt-lane" verdict_flags)"

  assert_eq "noremote unpushed" "1" "$(field_of "$fleet_c/noremote-lane" unpushed)"
  assert_eq "noremote flags" "unpushed,no-remote" "$(field_of "$fleet_c/noremote-lane" verdict_flags)"

  local link_bytes target_bytes
  link_bytes=$(du -sb -- "$slink/.scratch" | awk '{print $1}')
  target_bytes=$(du -sb -- "$slink/realscratch" | awk '{print $1}')
  assert_eq "symlink scratch not followed" "$link_bytes" "$(field_of "$fleet_c/slink-lane" scratch_bytes)"
  # The target is kilobytes; the link itself is a handful of bytes.
  if [ "$link_bytes" -lt "$target_bytes" ] && [ "$link_bytes" -lt 100 ]; then
    pass=$((pass+1))
  else
    fail=$((fail+1))
    printf 'FAIL symlink scratch size not link-sized link=%s target=%s\n' "$link_bytes" "$target_bytes" >&2
  fi
  assert_eq "symlink scratch flags" "clean,scratch,scratch-symlink" \
    "$(field_of "$fleet_c/slink-lane" verdict_flags)"

  assert_eq "unborn worktrees" "1" "$(field_of "$fleet_c/unborn-lane" worktrees)"
  assert_eq "unborn unpushed" "0" "$(field_of "$fleet_c/unborn-lane" unpushed)"
  assert_eq "unborn flags" "no-remote,unborn" "$(field_of "$fleet_c/unborn-lane" verdict_flags)"

  assert_eq "secret flags" "secrets-refusal" "$(field_of "$fleet_c/id_rsa" verdict_flags)"
  assert_eq "secret metrics withheld" "-" "$(field_of "$fleet_c/id_rsa" worktrees)"

  assert_eq "space-name flags" "clean" "$(field_of "$fleet_c/space lane" verdict_flags)"

  # Hand-check alignment: independent raw commands, not the tool's functions.
  local raw_wt raw_un raw_di
  raw_wt=$(git -C "$dirty" worktree list | wc -l)
  raw_wt=${raw_wt//[[:space:]]/}
  raw_un=$(git -C "$unpushed" log --branches --not --remotes --oneline | wc -l)
  raw_un=${raw_un//[[:space:]]/}
  raw_di=$(git -C "$dirty" status --porcelain | wc -l)
  raw_di=${raw_di//[[:space:]]/}
  assert_eq "raw worktree agrees" "$raw_wt" "$(field_of "$fleet_c/dirty-lane" worktrees)"
  assert_eq "raw unpushed agrees" "$raw_un" "$(field_of "$fleet_c/unpushed-lane" unpushed)"
  assert_eq "raw dirty agrees" "$raw_di" "$(field_of "$fleet_c/dirty-lane" dirty)"

  # Repeatability.
  local out2
  out2=$(bash "$SELF" --root "$fleet")
  if [ "$out" = "$out2" ]; then
    pass=$((pass+1))
  else
    fail=$((fail+1))
    printf 'FAIL repeat run differed\n' >&2
  fi

  # Positional root matches --root.
  local out3
  out3=$(bash "$SELF" "$fleet")
  assert_eq "positional root" "$out" "$out3"

  # Single repo root: one row.
  local one
  one=$(bash "$SELF" --root "$clean")
  assert_eq "single-repo rows" "1" "$(printf '%s\n' "$one" | awk 'END{print NR-1}')"

  # Empty directory: header only, exit 0.
  mkdir -p "$WORKDIR/empty"
  set +e
  local empty_out
  empty_out=$(bash "$SELF" --root "$WORKDIR/empty" 2>"$WORKDIR/empty.err")
  rc=$?
  set -e
  assert_eq "empty root exit" "0" "$rc"
  assert_eq "empty root rows" "1" "$(printf '%s\n' "$empty_out" | wc -l | tr -d ' ')"

  # Read-only: git metadata mtimes must not move.
  local before after
  before=$(find -P "$fleet" -path '*/.git/*' -printf '%p %T@\n' | LC_ALL=C sort)
  bash "$SELF" --root "$fleet" >/dev/null
  after=$(find -P "$fleet" -path '*/.git/*' -printf '%p %T@\n' | LC_ALL=C sort)
  assert_eq "no index writes" "$before" "$after"

  # --compare against a saved census: identical → changed=0.
  printf '%s\n' "$out" > "$WORKDIR/prev.tsv"
  set +e
  local cmp
  cmp=$(bash "$SELF" --root "$fleet" --compare "$WORKDIR/prev.tsv" 2>"$WORKDIR/cmp.err")
  rc=$?
  set -e
  assert_eq "compare identical exit" "0" "$rc"
  assert_has "compare identical summary" $'COMPARE_SUMMARY\tadded=0\tremoved=0\tchanged=0\tunchanged=11\t' "$cmp"

  # Drift on dirty count.
  awk -F '\t' 'BEGIN{OFS="\t"} NR==1{print; next} $1 ~ /dirty-lane$/ {$4=9} {print}' \
    "$WORKDIR/prev.tsv" > "$WORKDIR/drift.tsv"
  set +e
  cmp=$(bash "$SELF" --root "$fleet" --compare "$WORKDIR/drift.tsv" 2>"$WORKDIR/drift.err")
  rc=$?
  set -e
  assert_eq "compare drift exit" "0" "$rc"
  assert_has "compare drift field" $'\tdirty\t9\t2\t-7' "$cmp"
  assert_has "compare drift summary" "changed=1" "$cmp"

  # Basename match (short names in the previous file).
  awk -F '\t' 'BEGIN{OFS="\t"} NR==1{print; next} {n=$1; sub(/.*\//,"",n); $1=n; print}' \
    "$WORKDIR/prev.tsv" > "$WORKDIR/short.tsv"
  set +e
  cmp=$(bash "$SELF" --root "$fleet" --compare "$WORKDIR/short.tsv" 2>"$WORKDIR/short.err")
  rc=$?
  set -e
  assert_eq "basename compare exit" "0" "$rc"
  assert_has "basename match unchanged" "unchanged=11" "$cmp"
  assert_lacks "basename match not added" $'COMPARE\tadded' "$cmp"

  # Partial columns: only dirty is comparable.
  printf 'repo\tdirty\n' > "$WORKDIR/partial.tsv"
  printf 'dirty-lane\t9\n' >> "$WORKDIR/partial.tsv"
  set +e
  cmp=$(bash "$SELF" --root "$fleet" --compare "$WORKDIR/partial.tsv" 2>"$WORKDIR/partial.err")
  rc=$?
  set -e
  assert_eq "partial compare exit" "0" "$rc"
  assert_has "partial compared list" "compared=dirty" "$cmp"
  assert_has "partial drift" $'\tdirty\t9\t2\t-7' "$cmp"

  # Round-1 shaped artifact census: incompatible, exit 0, no crash.
  printf 'seat\tpath\tsize_bytes\tmtime\treceipt\tverdict\n' > "$WORKDIR/r1.tsv"
  printf 'S01\t/tmp/x\t1\t2020-01-01T00:00:00-03:00\tpushed\tSAFE\n' >> "$WORKDIR/r1.tsv"
  set +e
  cmp=$(bash "$SELF" --root "$fleet" --compare "$WORKDIR/r1.tsv" 2>"$WORKDIR/r1.err")
  rc=$?
  set -e
  assert_eq "round-1 schema exit" "0" "$rc"
  assert_has "round-1 incompatible" "schema=incompatible" "$cmp"
  assert_has "round-1 reason" "no-overlapping-metric-columns" "$cmp"

  # BOM + CRLF still parses as our schema.
  printf '\xef\xbb\xbf%s\r\n' "$HEADER" > "$WORKDIR/bom.tsv"
  printf '%s\r\n' "$out" | tail -n +2 >> "$WORKDIR/bom.tsv"
  set +e
  cmp=$(bash "$SELF" --root "$fleet" --compare "$WORKDIR/bom.tsv" 2>"$WORKDIR/bom.err")
  rc=$?
  set -e
  assert_eq "bom compare exit" "0" "$rc"
  assert_has "bom/crlf unchanged" "unchanged=11" "$cmp"

  # Secret-shaped compare path is refused unread.
  printf 'SECRET-SENTINEL-do-not-emit\n' > "$WORKDIR/credentials.txt"
  set +e
  cmp=$(bash "$SELF" --root "$fleet" --compare "$WORKDIR/credentials.txt" 2>"$WORKDIR/sec.err")
  rc=$?
  set -e
  assert_eq "secret compare exit" "2" "$rc"
  assert_lacks "secret compare unread" "SECRET-SENTINEL-do-not-emit" "$cmp$(cat "$WORKDIR/sec.err")"

  # Usage errors.
  set +e
  bash "$SELF" --no-such-flag >/dev/null 2>&1
  rc=$?
  set -e
  assert_eq "unknown flag exit" "2" "$rc"
  set +e
  bash "$SELF" --root "$WORKDIR/does-not-exist" >/dev/null 2>&1
  rc=$?
  set -e
  assert_eq "missing root exit" "2" "$rc"
  set +e
  bash "$SELF" --compare "$WORKDIR/missing-prev.tsv" --root "$fleet" >/dev/null 2>&1
  rc=$?
  set -e
  assert_eq "missing compare exit" "2" "$rc"
  set +e
  bash "$SELF" --help >/dev/null 2>&1
  rc=$?
  set -e
  assert_eq "help exit" "0" "$rc"

  if [ "$fail" -eq 0 ]; then
    printf 'SELFTEST pass=%s fail=0\n' "$pass"
    return 0
  fi
  printf 'SELFTEST pass=%s fail=%s\n' "$pass" "$fail"
  printf 'workdir kept only if SOUJI_CENSUS_KEEP=1 (%s)\n' "$WORKDIR" >&2
  return 1
}

# ---------------------------------------------------------------- main

if ! command -v git >/dev/null 2>&1; then
  printf 'souji-census.impl-46: git not on PATH\n' >&2
  exit 1
fi
if ! command -v du >/dev/null 2>&1 || ! command -v find >/dev/null 2>&1; then
  printf 'souji-census.impl-46: coreutils find/du missing\n' >&2
  exit 1
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --root)
      [ $# -ge 2 ] || die_usage "--root needs a path"
      ROOT=$2; ROOT_SET=1; shift 2 ;;
    --root=*) ROOT=${1#--root=}; ROOT_SET=1; shift ;;
    --compare)
      [ $# -ge 2 ] || die_usage "--compare needs a file"
      COMPARE=$2; shift 2 ;;
    --compare=*) COMPARE=${1#--compare=}; shift ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) die_usage "unknown option: $1" ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done
while [ $# -gt 0 ]; do
  POSITIONAL+=("$1"); shift
done

if [ "$SELFTEST" -eq 1 ]; then
  selftest
  exit $?
fi

if [ "${#POSITIONAL[@]}" -gt 1 ]; then
  die_usage "at most one positional root"
fi
if [ "${#POSITIONAL[@]}" -eq 1 ]; then
  if [ "$ROOT_SET" -eq 1 ] && [ "$(canon "$POSITIONAL")" != "$(canon "$ROOT")" ]; then
    die_usage "positional root and --root disagree"
  fi
  ROOT=${POSITIONAL[0]}
  ROOT_SET=1
fi
if [ "$ROOT_SET" -eq 0 ]; then
  ROOT=$DEFAULT_ROOT
fi
ROOT=$(canon "$ROOT")
if [ ! -d "$ROOT" ]; then
  printf 'souji-census.impl-46: root is not a directory: %s\n' "$ROOT" >&2
  exit 2
fi
if is_secret_shaped "$ROOT"; then
  printf 'souji-census.impl-46: refusing secret-shaped root\n' >&2
  exit 2
fi

if [ -n "$COMPARE" ]; then
  run_compare "$ROOT" "$COMPARE"
  exit $?
fi

emit_census "$ROOT"
exit 0
