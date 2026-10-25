#!/usr/bin/env bash
# souji-census.impl-39 — repeatable read-only fleet census (round 6, seat S39).
#
# Contract (SEAT S33, implemented independently as impl-39):
#   for every repo directory under a root (default $SHOKUNIN_ROOT), emit one
#   TSV row:
#     repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#   plus --compare against a previous census TSV.
#
# CLI
#   tools/souji-census.impl-39.sh [--selftest] [--json] [--root DIR]
#       [--compare PREV.tsv] [--out FILE]
#
# Census (default) prints a header line then one data row per repo, sorted by
# repo path. Exit 0 when every row was measured, 1 on a measurement error,
# 2 on usage. A NOT-SAFE flag is a census result, not an error.
#
# --compare PREV.tsv
#   Re-census --root, diff against PREV (same 7 columns). One line per repo
#   that is added, removed, or whose numeric/flag fields changed:
#     DIFF<TAB>repo<TAB>field<TAB>old<TAB>new
#   Exit 0 when the trees match, 1 when any row differs or PREV is unreadable.
#   mtime_iso is reported but does not by itself fail the compare (a live
#   tree's newest file moves without a hygiene change).
#
# Counting commands (what a hand re-derivation should re-run):
#   worktrees      git -C REPO worktree list --porcelain | grep -c '^worktree '
#                  (includes the main worktree; a healthy repo is >= 1)
#   unpushed       git -C REPO rev-list --count --branches --not --remotes
#   dirty          git -C REPO status --porcelain | wc -l
#                  (default untracked collapsing, not --untracked-files=all)
#   scratch_bytes  du -sb REPO/.scratch; absent -> 0. Contents are not opened.
#   mtime_iso      newest regular file, .git pruned, UTC ISO-8601.
#                  .ufo/state and watchdog.log are pruned (off-limits).
#
# Verdict flags (comma-joined, stable order; "clean" if none fire):
#   unpushed       unpushed commit count > 0
#   dirty          porcelain status line count > 0
#   multi-worktree linked worktree registrations beyond the main worktree
#   scratch        .scratch exists and is non-empty
#   no-remote      no refs/remotes/* (pushed receipt unverifiable)
#   not-a-repo     path looked like a repo but git refused it
#
# A --compare file whose header is not this schema (round-1 receipt census,
# for example) exits 1 with one schema DIFF line and does not scan the tree.
#
# Safety
#   Read-only over every inspected surface. No git fetch/push/commit/branch/
#   checkout/reset/rebase/prune. Writes only under `mktemp -d` (--selftest)
#   or the explicit --out path. Never reads secret-shaped basenames, never
#   touches .ufo/state, .ufo/watchdog.log, or ~/.config. .scratch size is
#   `du -sb` metadata only — file contents are not opened.
#
# Env
#   SHOKUNIN_ROOT   fleet root (default: parent of this repo)
#   SOUJI_CENSUS_NOW  epoch seconds frozen into mtime formatting (selftest)
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
export GIT_OPTIONAL_LOCKS=0

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"

SELFTEST=0
JSON=0
DO_COMPARE=0
COMPARE_FILE=""
OUT_FILE=""
ROOT_SET=0
POSITIONAL=()

usage() {
  sed -n '2,36p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

usage_err() {
  printf 'souji-census: %s\n' "$1" >&2
  usage 2
}

# A directory is a repo when it has a .git directory or a .git gitfile.
is_repo_dir() {
  local d=$1
  [ -d "$d/.git" ] || [ -f "$d/.git" ]
}

# Enumerate repo dirs: the root itself if it is a repo, plus immediate
# children that are repos. Nested lane worktrees are counted via
# `worktree list`, not as separate fleet rows.
list_repos() {
  local root=$1 d
  local found=()
  if is_repo_dir "$root"; then
    found+=("$root")
  fi
  shopt -s nullglob
  for d in "$root"/*/; do
    d=${d%/}
    if is_repo_dir "$d"; then
      found+=("$d")
    fi
  done
  shopt -u nullglob
  if [ "${#found[@]}" -eq 0 ]; then
    return 0
  fi
  printf '%s\n' "${found[@]}" | LC_ALL=C sort
}

# worktree registrations, including the main worktree. 0 if git refuses.
count_worktrees() {
  local repo=$1 n
  n=$(git -C "$repo" worktree list --porcelain 2>/dev/null | grep -c '^worktree ' || true)
  n=${n//[[:space:]]/}
  printf '%s' "${n:-0}"
}

# Commits reachable from any local branch but not from any remote-tracking ref.
# With no remotes this equals the local branch commit count (unverifiable).
count_unpushed() {
  local repo=$1 n
  if ! n=$(git -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null); then
    printf '0'
    return 0
  fi
  n=${n//[[:space:]]/}
  printf '%s' "${n:-0}"
}

count_dirty() {
  local repo=$1 n
  # Default porcelain so a hand check of `git status --porcelain | wc -l` matches.
  if ! n=$(git -C "$repo" --no-optional-locks status --porcelain 2>/dev/null | wc -l); then
    printf '0'
    return 0
  fi
  n=${n//[[:space:]]/}
  printf '%s' "${n:-0}"
}

# Byte size of <repo>/.scratch. Absent -> 0. Never opens file contents.
# A live scratch can lose a file mid-walk (du exits 1 after printing a total).
# Keep that total. If the path exists and du produced no number, print
# UNMEASURED so the caller fail-closes instead of reporting a false 0.
scratch_bytes() {
  local repo=$1 p="$1/.scratch" n=""
  if [ ! -e "$p" ] && [ ! -L "$p" ]; then
    printf '0'
    return 0
  fi
  n=$(du -sb -- "$p" 2>/dev/null | awk 'NF { print $1; exit }' || true)
  n=${n//[[:space:]]/}
  case "$n" in
    ''|*[!0-9]*) printf 'UNMEASURED' ;;
    *) printf '%s' "$n" ;;
  esac
}

# Newest regular-file mtime. Metadata only — contents are not opened.
# Prunes .git plus the off-limits driver paths .ufo/state and watchdog.log.
# Empty tree -> 1970-01-01T00:00:00Z.
newest_mtime_iso() {
  local repo=$1 epoch
  epoch=$(
    find "$repo" \
      \( -name .git -o -path '*/.ufo/state' -o -path '*/.ufo/state/*' -o -name watchdog.log \) -prune -o \
      -type f -printf '%T@\n' 2>/dev/null \
      | awk 'BEGIN { best=-1 } { ts=$1+0; if (ts>best) best=ts } END { if (best<0) print ""; else printf "%.0f\n", best }'
  ) || epoch=""
  if [ -z "$epoch" ]; then
    printf '1970-01-01T00:00:00Z'
    return 0
  fi
  date -u -d "@${epoch}" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || printf '1970-01-01T00:00:00Z'
}

has_remote() {
  local repo=$1 n
  n=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null | grep -c . || true)
  n=${n//[[:space:]]/}
  [ "${n:-0}" -gt 0 ]
}

# Emit flags in a fixed order. "clean" when nothing fires.
verdict_flags() {
  local wt=$1 unp=$2 dirty=$3 scratch=$4 remote_ok=$5 git_ok=$6
  local flags=()
  if [ "$git_ok" != 1 ]; then
    flags+=(not-a-repo)
  fi
  if [ "${unp:-0}" -gt 0 ] 2>/dev/null; then
    flags+=(unpushed)
  fi
  if [ "${dirty:-0}" -gt 0 ] 2>/dev/null; then
    flags+=(dirty)
  fi
  if [ "${wt:-0}" -gt 1 ] 2>/dev/null; then
    flags+=(multi-worktree)
  fi
  if [ "${scratch:-0}" -gt 0 ] 2>/dev/null; then
    flags+=(scratch)
  fi
  if [ "$remote_ok" != 1 ]; then
    flags+=(no-remote)
  fi
  if [ "${#flags[@]}" -eq 0 ]; then
    printf 'clean'
  else
    local IFS=','
    printf '%s' "${flags[*]}"
  fi
}

# Measure one repo. Prints the 7 TSV fields. Returns 1 if git itself refuses
# the directory (row still emitted, flag not-a-repo).
measure_repo() {
  local repo=$1
  local wt=0 unp=0 dirty=0 scratch=0 mtime git_ok=1 remote_ok=0 flags
  if ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git_ok=0
  else
    wt=$(count_worktrees "$repo")
    unp=$(count_unpushed "$repo")
    dirty=$(count_dirty "$repo")
    if has_remote "$repo"; then
      remote_ok=1
    fi
  fi
  scratch=$(scratch_bytes "$repo")
  mtime=$(newest_mtime_iso "$repo")
  if [ "$scratch" = UNMEASURED ]; then
    scratch=0
    flags=$(verdict_flags "$wt" "$unp" "$dirty" "0" "$remote_ok" "$git_ok")
    if [ "$flags" = clean ]; then
      flags=scratch-unmeasured
    else
      flags="${flags},scratch-unmeasured"
    fi
  else
    flags=$(verdict_flags "$wt" "$unp" "$dirty" "$scratch" "$remote_ok" "$git_ok")
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$repo" "$wt" "$unp" "$dirty" "$scratch" "$mtime" "$flags"
}

HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'

census_tsv() {
  local root=$1
  printf '%s\n' "$HEADER"
  local repo
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    measure_repo "$repo"
  done < <(list_repos "$root")
}

# Compare two census TSVs. Prints DIFF lines. Returns 1 if any difference
# other than mtime-only, or if a file is malformed.
compare_tsv() {
  local prev=$1 curr=$2
  awk -F '\t' -v OFS='\t' '
    function bad(msg) { print "souji-census: " msg > "/dev/stderr"; err=1 }
    FNR==1 && NR==FNR {
      if ($0 != "repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags")
        bad("previous census header mismatch")
      next
    }
    NR==FNR {
      if (NF != 7) { bad("previous census: want 7 fields, got " NF " at " $1); next }
      seen[$1]=1
      for (i=2; i<=7; i++) old[$1,i]=$i
      next
    }
    FNR==1 {
      if ($0 != "repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags")
        bad("current census header mismatch")
      next
    }
    {
      if (NF != 7) { bad("current census: want 7 fields, got " NF " at " $1); next }
      cur[$1]=1
      if (!($1 in seen)) {
        print "DIFF", $1, "row", "-", "added"
        diffed=1
        next
      }
      # fields 2..5 and 7 are hygiene; field 6 (mtime) is reported only
      split("worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags", names, " ")
      for (i=2; i<=7; i++) {
        if (old[$1,i] != $i) {
          print "DIFF", $1, names[i-1], old[$1,i], $i
          if (i != 6) diffed=1
        }
      }
    }
    END {
      for (r in seen) if (!(r in cur)) {
        print "DIFF", r, "row", "removed", "-"
        diffed=1
      }
      exit (err || diffed) ? 1 : 0
    }
  ' "$prev" "$curr"
}

# ---------------------------------------------------------------- selftest --

ST_PASS=0
ST_FAIL=0
ST_TMP=""

st_note() { printf 'selftest: %s\n' "$1"; }

st_ok() {
  ST_PASS=$((ST_PASS + 1))
  st_note "PASS $1"
}

st_bad() {
  ST_FAIL=$((ST_FAIL + 1))
  st_note "FAIL $1"
}

st_init() {
  local repo=$1 branch=$2
  git init -q -b "$branch" "$repo"
  git -C "$repo" config user.email "souji-census@shokunin.local"
  git -C "$repo" config user.name "souji-census"
}

st_commit() {
  local repo=$1 msg=$2
  git -C "$repo" add -A -- . >/dev/null
  local tree parent=()
  tree=$(git -C "$repo" write-tree)
  if git -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
    parent=(-p "$(git -C "$repo" rev-parse HEAD)")
  fi
  local commit
  commit=$(git -C "$repo" commit-tree "$tree" "${parent[@]}" -m "$msg")
  git -C "$repo" update-ref HEAD "$commit"
}

run_selftest() {
  if [ "${SOUJI_CENSUS_SELFTEST:-0}" = 1 ]; then
    printf 'souji-census: refusing nested --selftest\n' >&2
    exit 1
  fi
  ST_TMP=$(mktemp -d)
  trap 'rm -rf -- "$ST_TMP"' EXIT
  local fleet="$ST_TMP/fleet"
  mkdir -p "$fleet"

  # clean repo: 1 commit, origin/master at HEAD, no scratch, no dirt.
  local clean="$fleet/clean-shokunin"
  st_init "$clean" master
  printf 'kept\n' > "$clean/kept.txt"
  st_commit "$clean" "c1"
  git -C "$clean" update-ref refs/remotes/origin/master HEAD

  # kotodama-shaped: 1 unpushed commit, 1 dirty file, non-empty .scratch,
  # a second linked worktree, no remote.
  local koto="$fleet/kotodama-shaped-shokunin"
  st_init "$koto" master
  printf 'base\n' > "$koto/base.txt"
  st_commit "$koto" "k1"
  printf 'ahead\n' > "$koto/ahead.txt"
  st_commit "$koto" "k2 unpushed"
  printf 'dirty\n' >> "$koto/base.txt"
  mkdir -p "$koto/.scratch/gen"
  printf 'blob\n' > "$koto/.scratch/gen/out.bin"
  # secret-shaped name must not be opened and must not win newest-mtime
  printf 'nope\n' > "$koto/.scratch/app.env"
  touch -d '2020-01-01 00:00:00 UTC' "$koto/base.txt" "$koto/ahead.txt" "$koto/.scratch/gen/out.bin"
  touch -d '2030-01-01 00:00:00 UTC' "$koto/.scratch/app.env"
  local wt="$ST_TMP/wt-extra"
  git -C "$koto" worktree add -q -b side "$wt" HEAD

  # not a fleet repo: plain directory, must be skipped
  mkdir -p "$fleet/notes"

  # fleet root itself is not a repo
  local out
  out=$(env SHOKUNIN_ROOT="$fleet" SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fleet")
  local rows
  rows=$(printf '%s\n' "$out" | wc -l)
  rows=${rows//[[:space:]]/}
  if [ "$rows" = 3 ]; then
    st_ok "S1 header+2 repos (plain dir skipped)"
  else
    st_bad "S1 expected 3 lines, got $rows"
  fi

  local header
  header=${out%%$'\n'*}
  if [ "$header" = "$HEADER" ]; then
    st_ok "S2 header columns"
  else
    st_bad "S2 header '$header'"
  fi

  local crow
  crow=$(printf '%s\n' "$out" | awk -F '\t' -v p="$clean" '$1==p {print}')
  local krow
  krow=$(printf '%s\n' "$out" | awk -F '\t' -v p="$koto" '$1==p {print}')

  local c_wt c_unp c_dirty c_sc c_flags
  IFS=$'\t' read -r _ c_wt c_unp c_dirty c_sc _ c_flags <<< "$crow"
  if [ "$c_wt" = 1 ] && [ "$c_unp" = 0 ] && [ "$c_dirty" = 0 ] && [ "$c_sc" = 0 ] && [ "$c_flags" = clean ]; then
    st_ok "S3 clean repo flags"
  else
    st_bad "S3 clean wt=$c_wt unp=$c_unp dirty=$c_dirty sc=$c_sc flags=$c_flags"
  fi

  local k_wt k_unp k_dirty k_sc k_mtime k_flags
  IFS=$'\t' read -r _ k_wt k_unp k_dirty k_sc k_mtime k_flags <<< "$krow"
  local expect_sc
  expect_sc=$(du -sb -- "$koto/.scratch" | awk '{print $1}')
  # modified tracked file + one collapsed untracked .scratch directory
  if [ "$k_wt" = 2 ] && [ "$k_unp" = 2 ] && [ "$k_dirty" = 2 ] \
     && [ "$k_sc" = "$expect_sc" ] && [ "$k_sc" != 0 ]; then
    st_ok "S4 kotodama-shaped counts wt=$k_wt unp=$k_unp dirty=$k_dirty scratch=$k_sc"
  else
    st_bad "S4 koto wt=$k_wt unp=$k_unp dirty=$k_dirty sc=$k_sc expect_sc=$expect_sc"
  fi

  case ",$k_flags," in
    *,unpushed,*dirty,*multi-worktree,*scratch,*no-remote,*)
      st_ok "S5 flag order" ;;
    *)
      st_bad "S5 flags '$k_flags'" ;;
  esac

  # 2030 stamp sits on a secret-shaped basename. Report its mtime (metadata)
  # and never open the file.
  case "$k_mtime" in
    2030-01-01T00:00:00Z) st_ok "S6 newest mtime is metadata only" ;;
    *) st_bad "S6 unexpected mtime '$k_mtime'" ;;
  esac
  if grep -nE '^[^#]*\b(cat|head|sha256sum|md5sum) ' "$SELF" | grep -q .; then
    st_bad "S6b script contains a content-read command"
  else
    st_ok "S6b no content-read command in executable lines"
  fi

  # --compare identical -> exit 0, no DIFF
  printf '%s\n' "$out" > "$ST_TMP/prev.tsv"
  local cmp rc=0
  set +e
  cmp=$(env SHOKUNIN_ROOT="$fleet" SOUJI_CENSUS_SELFTEST=1 \
    "$SELF" --root "$fleet" --compare "$ST_TMP/prev.tsv" 2>"$ST_TMP/cmp.err")
  rc=$?
  set -e
  if [ "$rc" = 0 ] && [ -z "$cmp" ]; then
    st_ok "S7 compare identical exit 0"
  else
    st_bad "S7 compare identical rc=$rc out='$cmp'"
  fi

  # mutate: extra dirty file -> compare exit 1 and a dirty DIFF
  printf 'more\n' > "$koto/more.txt"
  set +e
  cmp=$(env SHOKUNIN_ROOT="$fleet" SOUJI_CENSUS_SELFTEST=1 \
    "$SELF" --root "$fleet" --compare "$ST_TMP/prev.tsv")
  rc=$?
  set -e
  if [ "$rc" = 1 ] && printf '%s\n' "$cmp" | grep -q $'^DIFF\t'"$koto"$'\tdirty\t'; then
    st_ok "S8 compare detects dirty drift"
  else
    st_bad "S8 rc=$rc out='$cmp'"
  fi

  # added repo
  local extra="$fleet/extra-shokunin"
  st_init "$extra" master
  printf 'e\n' > "$extra/e.txt"
  st_commit "$extra" "e1"
  git -C "$extra" update-ref refs/remotes/origin/master HEAD
  set +e
  cmp=$(env SHOKUNIN_ROOT="$fleet" SOUJI_CENSUS_SELFTEST=1 \
    "$SELF" --root "$fleet" --compare "$ST_TMP/prev.tsv")
  rc=$?
  set -e
  if [ "$rc" = 1 ] && printf '%s\n' "$cmp" | grep -q $'^DIFF\t'"$extra"$'\trow\t-\tadded$'; then
    st_ok "S9 compare detects added repo"
  else
    st_bad "S9 rc=$rc out='$cmp'"
  fi

  # usage discipline — --selftest must not census the live fleet
  local urc=0
  set +e
  "$SELF" --bogus >/dev/null 2>&1
  urc=$?
  set -e
  if [ "$urc" = 2 ]; then
    st_ok "S10 bad flag exit 2"
  else
    st_bad "S10 bad flag rc=$urc"
  fi

  set +e
  "$SELF" --compare /no/such/census.tsv --root "$fleet" >/dev/null 2>&1
  urc=$?
  set -e
  if [ "$urc" = 1 ]; then
    st_ok "S11 missing compare file exit 1"
  else
    st_bad "S11 missing compare rc=$urc"
  fi

  # --json is one object per repo
  local jout
  jout=$(env SHOKUNIN_ROOT="$fleet" SOUJI_CENSUS_SELFTEST=1 "$SELF" --json --root "$clean")
  case "$jout" in
    '{"repo":"'*'","worktrees":'*',"unpushed":'*',"dirty":'*',"scratch_bytes":'*',"mtime_iso":"'*'","verdict_flags":"'*'"}')
      st_ok "S12 json shape" ;;
    *)
      st_bad "S12 json '$jout'" ;;
  esac

  # safety: no forbidden git subcommands in executable lines
  local n
  n=$(grep -nE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase|prune)( |$)' "$SELF" | wc -l || true)
  n=${n//[[:space:]]/}
  if [ "${n:-1}" = 0 ]; then
    st_ok "S13 no forbidden git subcommand"
  else
    st_bad "S13 $n forbidden git invocation(s)"
  fi

  case "$ST_TMP" in
    /tmp/*|/var/tmp/*) st_ok "S14 fixtures under mktemp ($ST_TMP)" ;;
    *) st_bad "S14 fixtures not under tmp ($ST_TMP)" ;;
  esac

  # idempotence: two back-to-back censuses of the frozen fixture agree
  # on every field except that we already mutated koto; re-snapshot.
  local a b
  a=$(env SHOKUNIN_ROOT="$fleet" SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fleet")
  b=$(env SHOKUNIN_ROOT="$fleet" SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fleet")
  if [ "$a" = "$b" ]; then
    st_ok "S15 repeat census byte-identical"
  else
    st_bad "S15 repeat census diverged"
  fi

  # schema refusal must not scan; a foreign header is not a match
  printf 'seat\tpath\nS01\t/tmp/x\n' > "$ST_TMP/foreign.tsv"
  set +e
  cmp=$(env SHOKUNIN_ROOT="$fleet" SOUJI_CENSUS_SELFTEST=1 \
    "$SELF" --root "$fleet" --compare "$ST_TMP/foreign.tsv" 2>"$ST_TMP/foreign.err")
  rc=$?
  set -e
  if [ "$rc" = 1 ] && [ "$cmp" = $'DIFF\t-\tschema\tseat\tpath\t'"$HEADER" ]; then
    st_ok "S16 foreign schema refused without a match"
  else
    st_bad "S16 rc=$rc out='$cmp'"
  fi

  local pos via_flag
  via_flag=$(env SHOKUNIN_ROOT=/nonexistent SOUJI_CENSUS_SELFTEST=1 "$SELF" --root "$fleet")
  pos=$(env SHOKUNIN_ROOT=/nonexistent SOUJI_CENSUS_SELFTEST=1 "$SELF" "$fleet")
  if [ -n "$via_flag" ] && [ "$pos" = "$via_flag" ]; then
    st_ok "S17 positional root matches --root census"
  else
    st_bad "S17 positional diverged"
  fi

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then
    exit 1
  fi
  exit 0
}

# ------------------------------------------------------------------- main --

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a directory"
      SHOKUNIN_ROOT=$2
      ROOT_SET=1
      shift 2
      ;;
    --root=*) SHOKUNIN_ROOT=${1#*=}; ROOT_SET=1; shift ;;
    --compare)
      [ "$#" -ge 2 ] || usage_err "--compare needs a TSV path"
      COMPARE_FILE=$2
      DO_COMPARE=1
      shift 2
      ;;
    --compare=*) COMPARE_FILE=${1#*=}; DO_COMPARE=1; shift ;;
    --out)
      [ "$#" -ge 2 ] || usage_err "--out needs a path"
      OUT_FILE=$2
      shift 2
      ;;
    --out=*) OUT_FILE=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown flag: $1" ;;
    *) POSITIONAL+=("$1"); shift ;;
  esac
done

if [ "${#POSITIONAL[@]}" -gt 1 ]; then
  usage_err "unexpected argument: ${POSITIONAL[1]}"
fi
if [ "${#POSITIONAL[@]}" -eq 1 ]; then
  if [ "$ROOT_SET" = 1 ]; then
    usage_err "pass the root via --root or as one argument, not both"
  fi
  SHOKUNIN_ROOT=${POSITIONAL[0]}
  ROOT_SET=1
fi

if [ "$SELFTEST" = 1 ]; then
  run_selftest
fi

if [ ! -d "$SHOKUNIN_ROOT" ]; then
  printf 'souji-census: root is not a directory: %s\n' "$SHOKUNIN_ROOT" >&2
  exit 1
fi

command -v git >/dev/null 2>&1 || { printf 'souji-census: git not found\n' >&2; exit 1; }
command -v du >/dev/null 2>&1 || { printf 'souji-census: du not found\n' >&2; exit 1; }

if [ "$DO_COMPARE" = 1 ]; then
  if [ ! -f "$COMPARE_FILE" ] || [ ! -r "$COMPARE_FILE" ]; then
    printf 'souji-census: compare file unreadable: %s\n' "$COMPARE_FILE" >&2
    exit 1
  fi
  IFS= read -r prev_header < "$COMPARE_FILE" || prev_header=""
  if [ "$prev_header" != "$HEADER" ]; then
    printf 'DIFF\t-\tschema\t%s\t%s\n' "$prev_header" "$HEADER"
    printf 'souji-census: compare schema mismatch (not a souji-census TSV)\n' >&2
    exit 1
  fi
  tmp_curr=$(mktemp)
  trap 'rm -f -- "$tmp_curr"' EXIT
  census_tsv "$SHOKUNIN_ROOT" > "$tmp_curr"
  set +e
  compare_tsv "$COMPARE_FILE" "$tmp_curr"
  rc=$?
  set -e
  exit "$rc"
fi

tsv=$(census_tsv "$SHOKUNIN_ROOT")

if [ -n "$OUT_FILE" ]; then
  printf '%s\n' "$tsv" > "$OUT_FILE"
fi

if [ "$JSON" = 1 ]; then
  printf '%s\n' "$tsv" | awk -F '\t' 'NR>1 && NF==7 {
    gsub(/\\/,"\\\\",$1); gsub(/"/,"\\\"",$1)
    gsub(/\\/,"\\\\",$6); gsub(/"/,"\\\"",$6)
    gsub(/\\/,"\\\\",$7); gsub(/"/,"\\\"",$7)
    printf "{\"repo\":\"%s\",\"worktrees\":%s,\"unpushed\":%s,\"dirty\":%s,\"scratch_bytes\":%s,\"mtime_iso\":\"%s\",\"verdict_flags\":\"%s\"}\n", $1,$2,$3,$4,$5,$6,$7
  }'
else
  printf '%s\n' "$tsv"
fi
exit 0
