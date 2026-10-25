#!/usr/bin/env bash
# souji-census.impl-44 — repeatable read-only fleet census (round 6, seat S44).
#
# Contract (S33, independent implementation): for every main git repo in a
# root (the root itself when it is one, plus each immediate child whose .git
# is a real directory), emit one TSV row:
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#
# Linked worktrees (.git is a file) are not separate rows. They are counted
# on the owning repo via `git worktree list`.
#
# Column commands (hand-check these; do not substitute):
#   worktrees      git -C <repo> worktree list | wc -l
#                  (main worktree included)
#   unpushed       git -C <repo> rev-list --count --branches --not --remotes
#                  (no remote-tracking refs → this count, plus flag no-remote;
#                  pushedness is unverifiable, matching souji-verify)
#   dirty          git -C <repo> status --porcelain | wc -l
#   scratch_bytes  du -sb <repo>/.scratch | cut -f1 ; 0 if .scratch is absent
#   mtime_iso      newest regular file outside .git, .ufo/state, and
#                  .ufo/watchdog.log, integer seconds, formatted with
#                  date -d @<epoch> --iso-8601=seconds
#                  lstat only — file contents are never opened. The max is
#                  tracked in-process (no sort spill), so a full /tmp does
#                  not fail the row.
#
# verdict_flags (fixed order, comma-joined):
#   clean | not-safe
#   unpushed            unpushed > 0
#   dirty               dirty > 0
#   extra-worktrees     worktrees > 1
#   scratch             scratch dir present and du -sb > 0
#   scratch-empty       scratch dir present and du -sb == 0
#   scratch-absent      no .scratch
#   scratch-symlink     .scratch is a symlink (not followed)
#   no-remote           zero refs/remotes/*
#   probe-error         a count command failed; failed numeric fields are -1
# clean requires unpushed=0, dirty=0, a remote-tracking ref, and no probe-error.
# clean is a git-hygiene observation, not a removal receipt.
#
# CLI
#   tools/souji-census.impl-44.sh [--selftest] [--json] [--root DIR]
#       [--compare PREV.tsv] [--out FILE] [--include-root] [ROOT]
#   tools/impl-44.sh is the same program.
#
# --compare PREV.tsv
#   Re-census --root and diff PREV. Same 7 columns required (any order, extra
#   columns ignored). A per-artifact table such as census/round-1/census.tsv
#   is schema-incomparable: reported, not crashed.
#   DIFF lines:  DIFF  repo  field  before  after
#   Summary:     COMPARE  summary  hygiene_changed=N  added=N  removed=N
#                unchanged=N  mtime_only=N  incomparable=0|1
#   mtime_iso is reported and does not by itself count as a hygiene change.
#   Exit 0 when hygiene matches, schema is incomparable, or only mtimes moved.
#   Exit 3 when a hygiene field changed or a repo was added or removed.
#
# Exit codes
#   0  census evaluated, or compare with no hygiene delta / incomparable schema
#   1  selftest failure
#   2  usage
#   3  compare hygiene delta
#   A probe-error flag is a row result, not a tool failure.
#
# Safety
#   Read-only over every inspected surface. GIT_OPTIONAL_LOCKS=0 so status
#   does not refresh the index. No git fetch/push/commit/branch/prune/remove,
#   no checkout/reset/rebase. Never reads secret-shaped paths, never opens
#   the live obsidian ledger, .ufo/state, .ufo/watchdog.log, or ~/.config.
#   Writes only under mktemp (--selftest) or an explicit --out the caller
#   named (those off-limits paths are refused).
#
# Env: SHOKUNIN_ROOT (default root: parent of this repo).
set -uo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
export GIT_OPTIONAL_LOCKS=0
export GIT_TERMINAL_PROMPT=0
export GIT_PAGER=cat

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'
ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
COMPARE=""
JSON=0
SELFTEST=0
OUT_FILE=""
FIELDS=()

usage_text() {
  cat <<'EOF'
souji-census.impl-44 — read-only fleet census

  tools/souji-census.impl-44.sh [--selftest] [--json] [--root DIR]
      [--compare PREV.tsv] [--out FILE] [--include-root] [ROOT]

TSV columns:
  repo worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags

Exit: 0 evaluated / compare-clean / schema-incomparable;
      1 selftest failure; 2 usage; 3 compare hygiene delta.
EOF
}

usage() { usage_text; exit 0; }
usage_err() { printf 'souji-census: %s\n' "$1" >&2; usage_text >&2; exit 2; }

is_secret_shaped() {
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    lc=${comp,,}
    case "$lc" in
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem)
        set +f
        return 0
        ;;
    esac
  done
  set +f
  return 1
}

is_off_limits() {
  case "$1" in
    *obsidian-ledger.tsv|*/.ufo/state|*/.ufo/state/*|*/.ufo/watchdog.log)
      return 0
      ;;
  esac
  return 1
}

canon() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

is_main_repo() {
  [ -d "$1/.git" ] && [ ! -L "$1/.git" ]
}

split_tabs() {
  local s=$1
  FIELDS=()
  while true; do
    FIELDS+=("${s%%$'\t'*}")
    [ "$s" = "${s#*$'\t'}" ] && break
    s=${s#*$'\t'}
  done
}

join_flags() {
  local IFS=','
  printf '%s' "$*"
}

# Integer-second newest mtime. In-process max: no sort(1) temp file.
newest_epoch() {
  local repo=$1 ts sec max=""
  while IFS= read -r ts; do
    sec=${ts%%.*}
    case "$sec" in
      ''|*[!0-9]*) continue ;;
    esac
    if [ -z "$max" ] || [ "$sec" -gt "$max" ]; then
      max=$sec
    fi
  done < <(find "$repo" \
    -path "$repo/.git" -prune -o \
    -path "$repo/.ufo/state" -prune -o \
    -path "$repo/.ufo/watchdog.log" -prune -o \
    -type f -printf '%T@\n' 2>/dev/null)
  printf '%s' "$max"
}

# measure_repo <abs-repo> — one TSV row on stdout
measure_repo() {
  local repo=$1
  local wt=-1 unp=-1 dirty=-1 scratch=0 mtime='-' probe=0 no_remote=0
  local scratch_state=absent out rc newest epoch flags=() gitdir="" own=0

  # Refuse a parent walk-up. An empty or invalid .git makes `git -C` discover
  # the enclosing repo and report that repo's clean counts — a false clean.
  gitdir=$(git -C "$repo" rev-parse --absolute-git-dir 2>/dev/null) || gitdir=""
  if [ -n "$gitdir" ] && [ "$(canon "$gitdir")" = "$(canon "$repo/.git")" ]; then
    own=1
  else
    probe=1
  fi

  if [ "$own" -eq 1 ]; then
  out=$(git -C "$repo" worktree list 2>/dev/null) && rc=0 || rc=$?
  if [ "$rc" -eq 0 ]; then
    if [ -n "$out" ]; then
      wt=$(printf '%s\n' "$out" | wc -l)
      wt=${wt// /}
    else
      wt=0
    fi
  else
    probe=1
  fi

  out=$(git -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null) && rc=0 || rc=$?
  if [ "$rc" -eq 0 ] && [[ "$out" =~ ^[0-9]+$ ]]; then
    unp=$out
  else
    probe=1
  fi

  out=$(git -C "$repo" status --porcelain 2>/dev/null) && rc=0 || rc=$?
  if [ "$rc" -eq 0 ]; then
    if [ -n "$out" ]; then
      dirty=$(printf '%s\n' "$out" | wc -l)
      dirty=${dirty// /}
    else
      dirty=0
    fi
  else
    probe=1
  fi

  out=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null) && rc=0 || rc=$?
  if [ "$rc" -eq 0 ]; then
    if [ -z "$out" ]; then
      no_remote=1
    fi
  else
    probe=1
    no_remote=1
  fi
  fi

  if [ -L "$repo/.scratch" ]; then
    scratch=-1
    scratch_state=symlink
    probe=1
  elif [ -d "$repo/.scratch" ]; then
    out=$(du -sb -- "$repo/.scratch" 2>/dev/null) && rc=0 || rc=$?
    if [ "$rc" -eq 0 ]; then
      scratch=${out%%$'\t'*}
      scratch=${scratch%% *}
      if [[ "$scratch" =~ ^[0-9]+$ ]] && [ "$scratch" -gt 0 ]; then
        scratch_state=present
      elif [[ "$scratch" =~ ^[0-9]+$ ]]; then
        scratch_state=empty
      else
        scratch=-1
        scratch_state=bad
        probe=1
      fi
    else
      scratch=-1
      scratch_state=bad
      probe=1
    fi
  elif [ -e "$repo/.scratch" ]; then
    scratch=-1
    scratch_state=bad
    probe=1
  fi

  epoch=$(newest_epoch "$repo")
  if [ -n "$epoch" ]; then
    mtime=$(date -d "@$epoch" --iso-8601=seconds 2>/dev/null || printf '%s' '-')
  fi

  if [ "$probe" -eq 1 ] || [ "$unp" -gt 0 ] || [ "$dirty" -gt 0 ] || [ "$no_remote" -eq 1 ]; then
    flags+=(not-safe)
  else
    flags+=(clean)
  fi
  if [ "$unp" -gt 0 ]; then flags+=(unpushed); fi
  if [ "$dirty" -gt 0 ]; then flags+=(dirty); fi
  if [ "$wt" -gt 1 ]; then flags+=(extra-worktrees); fi
  case "$scratch_state" in
    present) flags+=(scratch) ;;
    empty) flags+=(scratch-empty) ;;
    absent) flags+=(scratch-absent) ;;
    symlink) flags+=(scratch-symlink) ;;
  esac
  if [ "$no_remote" -eq 1 ]; then flags+=(no-remote); fi
  if [ "$probe" -eq 1 ]; then flags+=(probe-error); fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$repo" "$wt" "$unp" "$dirty" "$scratch" "$mtime" "$(join_flags "${flags[@]}")"
}

discover_repos() {
  local root=$1 child ng=0
  local -a found=()
  declare -A seen=()
  shopt -q nullglob && ng=1
  shopt -s nullglob
  if is_main_repo "$root"; then
    found+=("$(canon "$root")")
  fi
  for child in "$root"/*; do
    [ -d "$child" ] || continue
    [ -L "$child" ] && continue
    is_main_repo "$child" || continue
    found+=("$(canon "$child")")
  done
  [ "$ng" = 1 ] || shopt -u nullglob
  local p
  REPOS=()
  for p in "${found[@]}"; do
    [ -n "${seen[$p]+x}" ] && continue
    seen[$p]=1
    REPOS+=("$p")
  done
  if [ "${#REPOS[@]}" -gt 1 ]; then
    local sorted
    sorted=$(printf '%s\n' "${REPOS[@]}" | LC_ALL=C sort)
    REPOS=()
    while IFS= read -r p; do
      [ -n "$p" ] || continue
      REPOS+=("$p")
    done <<<"$sorted"
  fi
}

emit_census() {
  local p line body=$HEADER
  discover_repos "$ROOT"
  for p in "${REPOS[@]}"; do
    line=$(measure_repo "$p")
    body+=$'\n'"$line"
  done
  if [ "$JSON" = 1 ]; then
    local first=1 repo wt unp dirty scratch mtime flags
    printf '['
    while IFS= read -r line; do
      [ "$line" = "$HEADER" ] && continue
      [ -n "$line" ] || continue
      split_tabs "$line"
      repo=${FIELDS[0]:-}
      wt=${FIELDS[1]:-}
      unp=${FIELDS[2]:-}
      dirty=${FIELDS[3]:-}
      scratch=${FIELDS[4]:-}
      mtime=${FIELDS[5]:-}
      flags=${FIELDS[6]:-}
      if [ "$first" = 1 ]; then first=0; else printf ','; fi
      printf '{"repo":"%s","worktrees":%s,"unpushed":%s,"dirty":%s,"scratch_bytes":%s,"mtime_iso":"%s","verdict_flags":"%s"}' \
        "$(json_escape "$repo")" "$wt" "$unp" "$dirty" "$scratch" \
        "$(json_escape "$mtime")" "$(json_escape "$flags")"
    done <<<"$body"
    printf ']\n'
  else
    printf '%s\n' "$body"
  fi
}

col_index() {
  local want=$1 i=0 f
  for f in "${HDR_FIELDS[@]}"; do
    if [ "$f" = "$want" ]; then
      printf '%s' "$i"
      return 0
    fi
    i=$((i + 1))
  done
  return 1
}

norm_key() {
  local p=$1
  p=${p%$'\r'}
  if [ -d "$p" ] || [ -e "$p" ]; then
    canon "$p"
    return 0
  fi
  if [ -n "$ROOT" ] && [ -d "$ROOT/$p" ]; then
    canon "$ROOT/$p"
    return 0
  fi
  printf '%s' "$p"
}

run_compare() {
  local prev=$1 line n=0 missing="" f
  local -a need=(repo worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)
  declare -A BASE_LINE=() CUR_LINE=()
  declare -A BASE_BASE=() CUR_BASE=() BASE_BASE_N=() CUR_BASE_N=()
  declare -A MATCHED_BASE=()

  if [ ! -f "$prev" ]; then
    usage_err "compare baseline not a file: $prev"
  fi
  if is_secret_shaped "$prev" || is_off_limits "$prev"; then
    usage_err "refusing to read off-limits or secret-shaped baseline"
  fi

  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    case "$line" in
      \#*) continue ;;
    esac
    n=$((n + 1))
    if [ "$n" -eq 1 ]; then
      split_tabs "$line"
      HDR_FIELDS=("${FIELDS[@]}")
      continue
    fi
    split_tabs "$line"
    local key
    key=$(norm_key "${FIELDS[0]:-}")
    BASE_LINE[$key]=$line
  done <"$prev"

  for f in "${need[@]}"; do
    if ! col_index "$f" >/dev/null; then
      missing+="${missing:+,}$f"
    fi
  done
  if [ -n "$missing" ] || [ "$n" -eq 0 ]; then
    [ -n "$missing" ] || missing="header"
    printf 'COMPARE\tschema\tincomparable\tmissing=%s\n' "$missing"
    printf 'COMPARE\tsummary\thygiene_changed=0\tadded=0\tremoved=0\tunchanged=0\tmtime_only=0\tincomparable=1\n'
    return 0
  fi

  local i_repo i_wt i_unp i_dirty i_scratch i_mtime i_flags
  i_repo=$(col_index repo)
  i_wt=$(col_index worktrees)
  i_unp=$(col_index unpushed)
  i_dirty=$(col_index dirty)
  i_scratch=$(col_index scratch_bytes)
  i_mtime=$(col_index mtime_iso)
  i_flags=$(col_index verdict_flags)

  # Re-key baseline rows by the repo column even if it was not field 0.
  declare -A REKEY=()
  local k
  for k in "${!BASE_LINE[@]}"; do
    split_tabs "${BASE_LINE[$k]}"
    local rk bn
    rk=$(norm_key "${FIELDS[$i_repo]:-}")
    REKEY[$rk]=${BASE_LINE[$k]}
    bn=${rk##*/}
    BASE_BASE_N[$bn]=$((${BASE_BASE_N[$bn]:-0} + 1))
    BASE_BASE[$bn]=$rk
  done
  BASE_LINE=()
  for k in "${!REKEY[@]}"; do
    BASE_LINE[$k]=${REKEY[$k]}
  done

  discover_repos "$ROOT"
  local p
  for p in "${REPOS[@]}"; do
    line=$(measure_repo "$p")
    CUR_LINE[$p]=$line
    bn=${p##*/}
    CUR_BASE_N[$bn]=$((${CUR_BASE_N[$bn]:-0} + 1))
    CUR_BASE[$bn]=$p
  done

  local hygiene_changed=0 added=0 removed=0 unchanged=0 mtime_only=0
  local before after cur_key bkey field

  resolve_base() {
    local cur=$1 bn=${1##*/}
    if [ -n "${BASE_LINE[$cur]+x}" ]; then
      printf '%s' "$cur"
      return 0
    fi
    if [ "${CUR_BASE_N[$bn]:-0}" = 1 ] && [ "${BASE_BASE_N[$bn]:-0}" = 1 ]; then
      printf '%s' "${BASE_BASE[$bn]}"
      return 0
    fi
    return 1
  }

  for cur_key in "${!CUR_LINE[@]}"; do
    if ! bkey=$(resolve_base "$cur_key"); then
      printf 'DIFF\t%s\trepo\tABSENT\tPRESENT\n' "$cur_key"
      added=$((added + 1))
      continue
    fi
    MATCHED_BASE[$bkey]=1
    split_tabs "${CUR_LINE[$cur_key]}"
    local c_wt=${FIELDS[1]} c_unp=${FIELDS[2]} c_dirty=${FIELDS[3]}
    local c_scratch=${FIELDS[4]} c_mtime=${FIELDS[5]} c_flags=${FIELDS[6]}
    split_tabs "${BASE_LINE[$bkey]}"
    local b_wt=${FIELDS[$i_wt]:-} b_unp=${FIELDS[$i_unp]:-} b_dirty=${FIELDS[$i_dirty]:-}
    local b_scratch=${FIELDS[$i_scratch]:-} b_mtime=${FIELDS[$i_mtime]:-} b_flags=${FIELDS[$i_flags]:-}
    local hdelta=0 mdelta=0
    field_diff() {
      local name=$1 o=$2 n=$3
      if [ "$o" != "$n" ]; then
        printf 'DIFF\t%s\t%s\t%s\t%s\n' "$cur_key" "$name" "$o" "$n"
        return 1
      fi
      return 0
    }
    field_diff worktrees "$b_wt" "$c_wt" || hdelta=1
    field_diff unpushed "$b_unp" "$c_unp" || hdelta=1
    field_diff dirty "$b_dirty" "$c_dirty" || hdelta=1
    field_diff scratch_bytes "$b_scratch" "$c_scratch" || hdelta=1
    field_diff verdict_flags "$b_flags" "$c_flags" || hdelta=1
    field_diff mtime_iso "$b_mtime" "$c_mtime" || mdelta=1
    if [ "$hdelta" -eq 1 ]; then
      hygiene_changed=$((hygiene_changed + 1))
    elif [ "$mdelta" -eq 1 ]; then
      mtime_only=$((mtime_only + 1))
    else
      unchanged=$((unchanged + 1))
    fi
  done

  for bkey in "${!BASE_LINE[@]}"; do
    [ -n "${MATCHED_BASE[$bkey]+x}" ] && continue
    printf 'DIFF\t%s\trepo\tPRESENT\tABSENT\n' "$bkey"
    removed=$((removed + 1))
  done

  printf 'COMPARE\tsummary\thygiene_changed=%s\tadded=%s\tremoved=%s\tunchanged=%s\tmtime_only=%s\tincomparable=0\n' \
    "$hygiene_changed" "$added" "$removed" "$unchanged" "$mtime_only"
  if [ $((hygiene_changed + added + removed)) -gt 0 ]; then
    return 3
  fi
  return 0
}

write_out() {
  local payload=$1
  if [ -z "$OUT_FILE" ]; then
    printf '%s' "$payload"
    return 0
  fi
  if is_secret_shaped "$OUT_FILE" || is_off_limits "$OUT_FILE"; then
    usage_err "refusing off-limits or secret-shaped --out"
  fi
  printf '%s' "$payload" >"$OUT_FILE"
  printf '%s' "$payload"
}

# ------------------------------------------------------------------- selftest

ST_PASS=0
ST_FAIL=0
st_note() { printf '%s\n' "$*"; }

st_ok() { ST_PASS=$((ST_PASS + 1)); st_note "PASS $1"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $1"; }

row_of() {
  local file=$1 repo=$2
  awk -F '\t' -v r="$repo" 'NR>1 && $1==r {print; exit}' "$file"
}

run_selftest() {
  if [ "${SOUJI_CENSUS_SELFTEST:-0}" = 1 ]; then
    printf 'souji-census: refusing nested --selftest\n' >&2
    exit 1
  fi
  export SOUJI_CENSUS_SELFTEST=1
  local W
  W=$(mktemp -d "${TMPDIR:-/tmp}/souji-census-s44.XXXXXX") || {
    printf 'souji-census: mktemp failed\n' >&2
    exit 1
  }
  trap 'rm -rf -- "$W"' EXIT

  export GIT_AUTHOR_NAME=s44 GIT_AUTHOR_EMAIL=s44@shokunin.local
  export GIT_COMMITTER_NAME=s44 GIT_COMMITTER_EMAIL=s44@shokunin.local

  local fix="$W/fleet" alpha="$W/fleet/alpha-shokunin" beta="$W/fleet/beta-shokunin"
  local gamma="$W/fleet/gamma-shokunin" wt="$W/fleet/gamma-wt"
  local broken="$W/fleet/broken-shokunin" plain="$W/fleet/not-a-repo"
  mkdir -p "$fix" "$plain" "$broken/.git"

  git -C "$fix" init -q
  git -C "$fix" symbolic-ref HEAD refs/heads/master
  printf '*\n!.gitignore\n!README\n' >"$fix/.gitignore"
  printf 'fleet\n' >"$fix/README"
  git -C "$fix" add -- .gitignore README
  local tree commit
  tree=$(git -C "$fix" write-tree)
  commit=$(git -C "$fix" commit-tree "$tree" -m init)
  git -C "$fix" update-ref refs/heads/master "$commit"
  git -C "$fix" update-ref refs/remotes/origin/master "$commit"
  git -C "$fix" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

  mkdir -p "$alpha" "$beta" "$gamma"
  for repo in "$alpha" "$beta" "$gamma"; do
    git -C "$repo" init -q
    git -C "$repo" symbolic-ref HEAD refs/heads/master
    printf 'file\n' >"$repo/f.txt"
  done
  touch -d '2020-01-02 03:04:05 +0000' "$alpha/f.txt"
  git -C "$alpha" add -- f.txt
  tree=$(git -C "$alpha" write-tree)
  commit=$(git -C "$alpha" commit-tree "$tree" -m init)
  git -C "$alpha" update-ref refs/heads/master "$commit"
  git -C "$alpha" update-ref refs/remotes/origin/master "$commit"
  git -C "$alpha" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

  git -C "$beta" add -- f.txt
  tree=$(git -C "$beta" write-tree)
  commit=$(git -C "$beta" commit-tree "$tree" -m init)
  git -C "$beta" update-ref refs/heads/master "$commit"
  git -C "$beta" update-ref refs/remotes/origin/master "$commit"
  printf 'changed\n' >"$beta/f.txt"
  git -C "$beta" add -- f.txt
  tree=$(git -C "$beta" write-tree)
  local commit2
  commit2=$(git -C "$beta" commit-tree "$tree" -p "$commit" -m two)
  git -C "$beta" update-ref refs/heads/master "$commit2"
  printf 'dirty\n' >"$beta/dirty.txt"
  mkdir -p "$beta/.scratch"
  printf 'note\n' >"$beta/.scratch/note.txt"
  printf 'SECRET-MARKER-S44\n' >"$beta/.scratch/app.env"

  git -C "$gamma" add -- f.txt
  tree=$(git -C "$gamma" write-tree)
  commit=$(git -C "$gamma" commit-tree "$tree" -m init)
  git -C "$gamma" update-ref refs/heads/master "$commit"
  git -C "$gamma" -c advice.detachedHead=false worktree add --detach "$wt" HEAD >/dev/null 2>&1

  local out rc
  out=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fix" 2>"$W/err")
  rc=$?
  printf '%s\n' "$out" >"$W/census.tsv"
  if [ "$rc" -eq 0 ]; then st_ok "T00 census exit 0"; else st_bad "T00 census exit $rc"; fi

  local nlines
  nlines=$(wc -l <"$W/census.tsv")
  nlines=${nlines// /}
  if [ "$nlines" -eq 6 ]; then st_ok "T01 row count 5+header"; else st_bad "T01 lines=$nlines want 6"; fi

  local hdr
  hdr=$(head -1 "$W/census.tsv")
  if [ "$hdr" = "$HEADER" ]; then st_ok "T02 header"; else st_bad "T02 header '$hdr'"; fi

  if ! grep -F "$plain" "$W/census.tsv" >/dev/null; then st_ok "T03 plain dir excluded"; else st_bad "T03 plain dir included"; fi
  if ! grep -F "$wt" "$W/census.tsv" >/dev/null; then st_ok "T04 linked worktree excluded"; else st_bad "T04 linked worktree included"; fi
  if [ -f "$wt/.git" ]; then st_ok "T05 gamma-wt is a gitfile"; else st_bad "T05 gamma-wt .git is not a file"; fi

  local arow
  arow=$(row_of "$W/census.tsv" "$alpha")
  split_tabs "$arow"
  if [ "${FIELDS[1]}" = 1 ] && [ "${FIELDS[2]}" = 0 ] && [ "${FIELDS[3]}" = 0 ] && [ "${FIELDS[4]}" = 0 ]; then
    st_ok "T06 alpha counts 1/0/0/0"
  else
    st_bad "T06 alpha row '$arow'"
  fi
  case "${FIELDS[6]}" in
    clean,scratch-absent) st_ok "T07 alpha flags" ;;
    *) st_bad "T07 alpha flags '${FIELDS[6]}'" ;;
  esac
  local epoch expect_m ts sec
  epoch=""
  while IFS= read -r ts; do
    sec=${ts%%.*}
    case "$sec" in ''|*[!0-9]*) continue ;; esac
    if [ -z "$epoch" ] || [ "$sec" -gt "$epoch" ]; then epoch=$sec; fi
  done < <(find "$alpha" \
    -path "$alpha/.git" -prune -o \
    -path "$alpha/.ufo/state" -prune -o \
    -path "$alpha/.ufo/watchdog.log" -prune -o \
    -type f -printf '%T@\n')
  expect_m=$(date -d "@$epoch" --iso-8601=seconds)
  if [ "${FIELDS[5]}" = "$expect_m" ]; then st_ok "T08 alpha mtime"; else st_bad "T08 mtime '${FIELDS[5]}' want '$expect_m'"; fi

  local brow hand_unp hand_dirty hand_scratch
  brow=$(row_of "$W/census.tsv" "$beta")
  split_tabs "$brow"
  hand_unp=$(git -C "$beta" rev-list --count --branches --not --remotes)
  hand_dirty=$(git -C "$beta" status --porcelain | wc -l)
  hand_dirty=${hand_dirty// /}
  hand_scratch=$(du -sb -- "$beta/.scratch" | cut -f1)
  if [ "${FIELDS[2]}" = "$hand_unp" ] && [ "${FIELDS[3]}" = "$hand_dirty" ] && [ "${FIELDS[4]}" = "$hand_scratch" ]; then
    st_ok "T09 beta matches hand commands ($hand_unp/$hand_dirty/$hand_scratch)"
  else
    st_bad "T09 beta row '$brow' hand $hand_unp/$hand_dirty/$hand_scratch"
  fi
  case "${FIELDS[6]}" in
    *not-safe*unpushed*dirty*scratch*) st_ok "T10 beta flags" ;;
    *) st_bad "T10 beta flags '${FIELDS[6]}'" ;;
  esac
  if [ "$hand_unp" -ge 1 ] && [ "$hand_scratch" -gt 0 ]; then st_ok "T11 beta unpushed and scratch >0"; else st_bad "T11 beta magnitudes"; fi

  local grow hand_wt
  grow=$(row_of "$W/census.tsv" "$gamma")
  split_tabs "$grow"
  hand_wt=$(git -C "$gamma" worktree list | wc -l)
  hand_wt=${hand_wt// /}
  hand_unp=$(git -C "$gamma" rev-list --count --branches --not --remotes)
  if [ "${FIELDS[1]}" = "$hand_wt" ] && [ "$hand_wt" = 2 ] && [ "${FIELDS[2]}" = "$hand_unp" ]; then
    st_ok "T12 gamma worktrees=2 unpushed=$hand_unp"
  else
    st_bad "T12 gamma row '$grow' hand wt=$hand_wt unp=$hand_unp"
  fi
  case "${FIELDS[6]}" in
    *no-remote*) st_ok "T13 gamma no-remote" ;;
    *) st_bad "T13 gamma flags '${FIELDS[6]}'" ;;
  esac

  local xrow
  xrow=$(row_of "$W/census.tsv" "$broken")
  split_tabs "$xrow"
  case "${FIELDS[6]}" in
    *probe-error*) st_ok "T14 broken repo probe-error" ;;
    *) st_bad "T14 broken flags '${FIELDS[6]}' row '$xrow'" ;;
  esac
  if [ "${FIELDS[1]}" = -1 ]; then st_ok "T15 broken worktrees -1"; else st_bad "T15 broken wt '${FIELDS[1]}'"; fi

  out=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fix" 2>/dev/null)
  if [ "$out" = "$(cat "$W/census.tsv")" ]; then st_ok "T16 repeat byte-identical"; else st_bad "T16 repeat differed"; fi

  local crc cout
  cout=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fix" --compare "$W/census.tsv" 2>/dev/null)
  crc=$?
  if [ "$crc" -eq 0 ] && printf '%s\n' "$cout" | grep -F 'hygiene_changed=0' >/dev/null && printf '%s\n' "$cout" | grep -F 'added=0' >/dev/null; then
    st_ok "T17 compare identical exit 0"
  else
    st_bad "T17 compare identical exit=$crc out=$cout"
  fi

  cp "$W/census.tsv" "$W/tamper.tsv"
  # Drop gamma, bump alpha unpushed, add a phantom repo.
  awk -F '\t' -v a="$alpha" 'BEGIN{OFS="\t"} NR==1{print; next} $1==a {$3=7; print; next} $1 ~ /gamma-shokunin$/ {next} {print} END{print "/tmp/souji-s44-phantom\t1\t0\t0\t0\t-\tclean,scratch-absent"}' \
    "$W/census.tsv" >"$W/tamper.tsv"
  cout=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fix" --compare "$W/tamper.tsv" 2>/dev/null)
  crc=$?
  if [ "$crc" -eq 3 ] \
    && printf '%s\n' "$cout" | grep -F $'DIFF\t'"$alpha"$'\tunpushed\t7\t0' >/dev/null \
    && printf '%s\n' "$cout" | grep -F $'DIFF\t'"$gamma"$'\trepo\tABSENT\tPRESENT' >/dev/null \
    && printf '%s\n' "$cout" | grep -F $'DIFF\t/tmp/souji-s44-phantom\trepo\tPRESENT\tABSENT' >/dev/null; then
    st_ok "T18 compare delta exit 3"
  else
    st_bad "T18 compare delta exit=$crc out=$cout"
  fi

  printf 'seat\tpath\tsize_bytes\nS01\t/tmp/x\t1\n' >"$W/round1.tsv"
  cout=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fix" --compare "$W/round1.tsv" 2>/dev/null)
  crc=$?
  if [ "$crc" -eq 0 ] && printf '%s\n' "$cout" | grep -F $'COMPARE\tschema\tincomparable' >/dev/null; then
    st_ok "T19 round-1 schema incomparable exit 0"
  else
    st_bad "T19 incomparable exit=$crc out=$cout"
  fi

  # Basename-only baseline key still matches a unique repo.
  printf '%s\n' "$HEADER" >"$W/baseonly.tsv"
  printf 'alpha-shokunin\t1\t0\t0\t0\t%s\tclean,scratch-absent\n' "$expect_m" >>"$W/baseonly.tsv"
  cout=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fix" --compare "$W/baseonly.tsv" 2>/dev/null)
  crc=$?
  if [ "$crc" -eq 3 ] && printf '%s\n' "$cout" | grep -F $'DIFF\t'"$alpha"$'\tunpushed' >/dev/null; then
    st_bad "T20 basename match falsely diffed unpushed: $cout"
  elif printf '%s\n' "$cout" | grep -F $'DIFF\t'"$alpha"$'\trepo\tABSENT\tPRESENT' >/dev/null; then
    st_bad "T20 basename key not matched"
  else
    st_ok "T20 basename key matched (exit=$crc)"
  fi

  SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$W/no-such-root" >/dev/null 2>&1
  rc=$?
  if [ "$rc" -eq 2 ]; then st_ok "T21 missing root exit 2"; else st_bad "T21 exit=$rc"; fi
  SOUJI_CENSUS_SELFTEST=1 "$SELF" --bogus >/dev/null 2>&1
  rc=$?
  if [ "$rc" -eq 2 ]; then st_ok "T22 unknown flag exit 2"; else st_bad "T22 exit=$rc"; fi

  if ! grep -F 'SECRET-MARKER-S44' "$W/census.tsv" >/dev/null; then
    st_ok "T23 secret content not emitted"
  else
    st_bad "T23 secret content leaked"
  fi

  local nh
  nh=$(grep -nE '^[^#]*git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(fetch|push|commit|branch|prune|remove)([[:space:]]|$)' "$SELF" | wc -l || true)
  nh=${nh// /}
  if [ "${nh:-1}" = 0 ]; then st_ok "T24 no forbidden git subcommand"; else st_bad "T24 forbidden git hits=$nh"; fi

  out=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --json --root "$fix" 2>/dev/null)
  case "$out" in
    *'"repo":"'"$alpha"'"'*'"worktrees":1'*'"verdict_flags":"clean,scratch-absent"'*)
      st_ok "T25 json shape" ;;
    *) st_bad "T25 json '$out'" ;;
  esac

  out=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --include-root --root "$fix" 2>/dev/null)
  if [ "$out" = "$(cat "$W/census.tsv")" ]; then st_ok "T26 --include-root is the default"; else st_bad "T26 include-root differed"; fi

  SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fix" --out "$W/out.tsv" >/dev/null
  if cmp -s "$W/out.tsv" "$W/census.tsv"; then st_ok "T27 --out matches stdout"; else st_bad "T27 --out mismatch"; fi

  mkdir -p "$W/empty"
  out=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$W/empty" 2>/dev/null)
  if [ "$out" = "$HEADER" ]; then st_ok "T28 empty root header only"; else st_bad "T28 '$out'"; fi

  SOUJI_CENSUS_SELFTEST=1 "$SELF" --help >/dev/null 2>&1
  rc=$?
  if [ "$rc" -eq 0 ]; then st_ok "T29 help exit 0"; else st_bad "T29 help exit=$rc"; fi

  # Positional root matches --root.
  out=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" "$fix" 2>/dev/null)
  if [ "$out" = "$(cat "$W/census.tsv")" ]; then st_ok "T30 positional root"; else st_bad "T30 positional differed"; fi

  case "$W" in
    "${TMPDIR:-/tmp}"/*) st_ok "T31 fixtures under mktemp" ;;
    *) st_bad "T31 fixtures not under mktemp ($W)" ;;
  esac

  mkdir -p "$alpha/.ufo/state"
  printf 'state\n' >"$alpha/.ufo/state/live"
  printf 'watch\n' >"$alpha/.ufo/watchdog.log"
  touch -d '2099-01-01 00:00:00 +0000' "$alpha/.ufo/state/live" "$alpha/.ufo/watchdog.log"
  out=$(SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fix" 2>/dev/null)
  arow=$(printf '%s\n' "$out" | awk -F '\t' -v r="$alpha" 'NR>1 && $1==r {print; exit}')
  split_tabs "$arow"
  if [ "${FIELDS[5]}" = "$expect_m" ]; then
    st_ok "T32 off-limits paths excluded from mtime"
  else
    st_bad "T32 mtime picked an off-limits file '${FIELDS[5]}' want '$expect_m'"
  fi

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# ---------------------------------------------------------------------- main

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --include-root) shift ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a value"
      ROOT=$2
      shift 2
      ;;
    --root=*) ROOT=${1#*=}; shift ;;
    --compare)
      [ "$#" -ge 2 ] || usage_err "--compare needs a value"
      COMPARE=$2
      shift 2
      ;;
    --compare=*) COMPARE=${1#*=}; shift ;;
    --out)
      [ "$#" -ge 2 ] || usage_err "--out needs a value"
      OUT_FILE=$2
      shift 2
      ;;
    --out=*) OUT_FILE=${1#*=}; shift ;;
    -h|--help) usage ;;
    --) shift; break ;;
    -*) usage_err "unknown flag: $1" ;;
    *)
      if [ -n "${POSITIONAL_ROOT:-}" ]; then
        usage_err "unexpected argument: $1"
      fi
      POSITIONAL_ROOT=$1
      shift
      ;;
  esac
done
if [ -n "${POSITIONAL_ROOT:-}" ]; then
  if [ "$ROOT" != "${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}" ] && [ "$POSITIONAL_ROOT" != "$ROOT" ]; then
    usage_err "both --root and a positional root were given"
  fi
  ROOT=$POSITIONAL_ROOT
fi

if [ "$SELFTEST" = 1 ]; then
  run_selftest
fi

if [ "$JSON" = 1 ] && [ -n "$COMPARE" ]; then
  usage_err "--json and --compare are mutually exclusive"
fi

if [ ! -d "$ROOT" ]; then
  usage_err "root is not a directory: $ROOT"
fi
ROOT=$(canon "$ROOT")

if [ -n "$COMPARE" ]; then
  payload=$(run_compare "$COMPARE")
  crc=$?
  write_out "$payload"$'\n'
  exit "$crc"
fi

payload=$(emit_census)
# emit_census already ends with newline via printf '%s\n'
write_out "$payload"$'\n'
exit 0
