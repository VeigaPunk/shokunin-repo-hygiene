#!/usr/bin/env bash
# souji-verify.impl-10.sh — round-2 seat S10 implementation of tools/souji-verify.sh
# Binding spec: tools/souji-verify.spec.md. Read-only over every surface inspected.
#
# Implementation notes (decisions, all on the safe side):
# - The spec's reference sweep names `--basename`; rg 15.2.0 rejects that flag
#   (unrecognized). The D3 pollution is content-borne (census JSON records
#   basenames in its body), so the sweep is the spec command minus that flag:
#   a content search for the basename with the spec's exclusion globs.
# - Secret-shaped paths are never opened (hard rail). The sweep therefore also
#   excludes them, and `.ufo/**` is excluded because the rails say those paths
#   are never touched. Any target that is secret-shaped short-circuits to
#   NOT-SAFE(secrets-refusal) before any stat/hash/read.
# - Only read-only git verbs are used (rev-parse, symbolic-ref, for-each-ref,
#   show-ref, log, merge-base, status, worktree list, cat-file). GIT_OPTIONAL_LOCKS=0
#   is exported so nothing refreshes an index, takes a lock, or writes a ref.

set -euo pipefail

export GIT_OPTIONAL_LOCKS=0
export GIT_TERMINAL_PROMPT=0
export LC_ALL=C

PROG=souji-verify
SELF_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
SELF="$SELF_DIR/$(basename -- "${BASH_SOURCE[0]}")"
REPO_ROOT=$(cd -- "$SELF_DIR/.." && pwd)
SHOKUNIN_ROOT=${SHOKUNIN_ROOT:-$(cd -- "$REPO_ROOT/.." && pwd)}

STALE_DAYS=1
JSON=0
SELFTEST=0
ERRORS=0
declare -A WT_CACHE=()

usage() {
  cat <<'USAGE'
usage: souji-verify.sh [--selftest] [--stale-days N] [--json] <path>...

  --selftest      build an isolated fixture fleet under mktemp -d, run the
                  spec's fixture cases F1-F10, exit 0 on all pass / 1 on any fail
  --stale-days N  mtime threshold in days for the `stale` receipt (default 1)
  --json          emit one JSON object per target instead of TSV lines

output (TSV): VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>evidence
exit codes: 0 evaluated clean; 1 selftest failure or evaluation error; 2 usage
USAGE
}

usage_err() { printf '%s: %s\n' "$PROG" "$1" >&2; usage >&2; exit 2; }

# ---------------------------------------------------------------- primitives

norm() { realpath -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

nl_count() {
  local out="$1"
  if [ -z "$out" ]; then printf '0'; else printf '%s\n' "$out" | wc -l | tr -d '[:space:]'; fi
}

git_out() { local repo="$1"; shift; git -C "$repo" "$@" 2>/dev/null || true; }
git_count() { local out; out=$(git_out "$@"); nl_count "$out"; }

fsan() {
  local s="$1"
  s=${s//$'\t'/ }; s=${s//$'\n'/ }; s=${s//$'\r'/ }
  printf '%s' "$s"
}

jesc() {
  local s="$1"
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; s=${s//$'\r'/\\r}
  printf '%s' "$s"
}

is_secret_path() {
  local p="$1" comp lc oldifs="$IFS"
  IFS='/'
  for comp in $p; do
    IFS="$oldifs"
    if [ -n "$comp" ]; then
      lc=$(printf '%s' "$comp" | tr '[:upper:]' '[:lower:]')
      case "$lc" in
        *.env|*.env.*|.env*|*credential*|*secret*|id_*|*.pem) IFS="$oldifs"; return 0 ;;
      esac
    fi
    IFS='/'
  done
  IFS="$oldifs"
  return 1
}

find_owner_repo() {
  local d="$1" p
  [ -d "$d" ] || d=$(dirname -- "$d")
  while :; do
    if [ -e "$d/.git" ]; then printf '%s' "$d"; return 0; fi
    [ "$d" = "/" ] && return 1
    p=$(dirname -- "$d")
    [ "$p" = "$d" ] && return 1
    d="$p"
  done
}

# $1 = path of a `.git` file -> "owner<TAB>id" when it is a worktree gitfile
parse_gitfile() {
  local line owner id
  line=$(head -n 1 -- "$1" 2>/dev/null || true)
  case "$line" in
    'gitdir: '*) line=${line#gitdir: } ;;
    *) return 1 ;;
  esac
  case "$line" in
    */.git/worktrees/*)
      owner=${line%/.git/worktrees/*}
      id=${line#"$owner"/.git/worktrees/}
      if [ -n "$owner" ] && [ -n "$id" ]; then printf '%s\t%s' "$owner" "$id"; return 0; fi
      ;;
  esac
  return 1
}

ledger_path() {
  local c
  if [ -n "${SOUJI_LEDGER:-}" ] && [ -f "$SOUJI_LEDGER" ]; then printf '%s' "$SOUJI_LEDGER"; return 0; fi
  for c in "$SHOKUNIN_ROOT/corpus/knowledge/obsidian-ledger.tsv" \
           "$SHOKUNIN_ROOT/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv" \
           "$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"; do
    [ -f "$c" ] && { printf '%s' "$c"; return 0; }
  done
  return 1
}

resolve_default_ref() {
  local repo="$1" b refs r only="" cnt=0 c
  b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  if [ -n "$b" ]; then
    b=${b#origin/}
  else
    refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin/ 2>/dev/null || true)
    while IFS= read -r r; do
      [ -n "$r" ] || continue
      case "$r" in */HEAD) continue ;; esac
      cnt=$((cnt + 1)); only="$r"
    done <<< "$refs"
    if [ "$cnt" = "1" ]; then
      b=${only#refs/remotes/origin/}
    elif git -C "$repo" show-ref --verify --quiet refs/heads/master; then
      b=master
    else
      return 1
    fi
  fi
  for c in "refs/remotes/origin/$b" "origin/$b" "refs/heads/$b" "$b"; do
    if git -C "$repo" rev-parse --verify --quiet "$c^{commit}" >/dev/null 2>&1; then
      printf '%s' "$c"; return 0
    fi
  done
  return 1
}

# --------------------------------------------------- worktree registration map

# wt_scan_repo <repo> <wanted-path> ; sets WT_FOUND/WT_HEAD/WT_BRANCH/WT_PRUNE
wt_scan_repo() {
  local repo="$1" want="$2" text line
  WT_FOUND=0; WT_HEAD=""; WT_BRANCH=""; WT_PRUNE=""
  if [ -n "${WT_CACHE["$repo"]+set}" ]; then
    text=${WT_CACHE["$repo"]}
  else
    text=$(git_out "$repo" worktree list --porcelain)
    WT_CACHE["$repo"]="$text"
  fi
  [ -n "$text" ] || return 0
  local main="" path="" head="" branch="" prun=""
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      'worktree '*) path=${line#worktree }; head=""; branch=""; prun="" ;;
      'HEAD '*) head=${line#HEAD } ;;
      'branch '*) branch=${line#branch } ;;
      'detached'*) branch="" ;;
      'prunable'*) prun=${line#prunable } ;;
      '')
        if [ -n "$path" ]; then
          [ -z "$main" ] && main="$path"
          if [ "$path" = "$want" ] && [ "$path" != "$main" ]; then
            WT_FOUND=1; WT_HEAD="$head"; WT_BRANCH="$branch"; WT_PRUNE="$prun"; return 0
          fi
          path=""
        fi
        ;;
    esac
  done <<< "$text"
  if [ -n "$path" ] && [ "$path" != "$main" ] && [ "$path" = "$want" ]; then
    WT_FOUND=1; WT_HEAD="$head"; WT_BRANCH="$branch"; WT_PRUNE="$prun"
  fi
}

_wt_add() {
  local r="$1" x
  for x in "${WT_CANDS[@]:-}"; do [ -n "$x" ] && [ "$x" = "$r" ] && return 0; done
  [ -e "$r/.git" ] && WT_CANDS+=("$r")
  return 0
}

# wt_candidates <abs> ; sets WT_CANDS
wt_candidates() {
  local abs="$1" d parent
  WT_CANDS=()
  _wt_add "$SHOKUNIN_ROOT"
  for d in "$SHOKUNIN_ROOT"/*-shokunin; do [ -d "$d" ] && _wt_add "$d"; done
  parent=$(dirname -- "$abs")
  _wt_add "$parent"
  for d in "$parent"/*-shokunin; do [ -d "$d" ] && _wt_add "$d"; done
  return 0
}

# wt_find_owner <abs> ; sets WT_OWNER (and WT_* from the matching block)
wt_find_owner() {
  local r
  WT_OWNER=""
  wt_candidates "$1"
  for r in "${WT_CANDS[@]:-}"; do
    [ -n "$r" ] || continue
    wt_scan_repo "$r" "$1"
    if [ "$WT_FOUND" = 1 ]; then WT_OWNER="$r"; return 0; fi
  done
  return 1
}

wt_admin_head() { # <owner> <admin-id> -> sets WT_HEAD/WT_BRANCH
  local owner="$1" id="$2" hf line
  WT_HEAD=""; WT_BRANCH=""
  hf="$owner/.git/worktrees/$id/HEAD"
  [ -f "$hf" ] || return 0
  line=$(head -n 1 -- "$hf" 2>/dev/null || true)
  case "$line" in
    'ref: '*)
      WT_BRANCH=${line#ref: }
      WT_HEAD=$(git -C "$owner" rev-parse --verify --quiet "${WT_BRANCH}^{commit}" 2>/dev/null || true) ;;
    *) WT_HEAD="$line" ;;
  esac
}

# --------------------------------------------------------------- ledger lookup

# ledger_match <abs> file|dir ; on match prints "vault=<path> sha=<sha12>"
ledger_match() {
  local abs="$1" kind="$2" ledger sp ssha vp vsha rest
  local -a forms=()
  ledger=$(ledger_path) || return 1
  forms+=("$abs")
  case "$abs" in "$SHOKUNIN_ROOT"/*) forms+=("${abs#"$SHOKUNIN_ROOT"/}") ;; esac
  case "$abs" in "$REPO_ROOT"/*) forms+=("${abs#"$REPO_ROOT"/}") ;; esac
  if [ -n "${EV_OWNER_REPO:-}" ]; then
    case "$abs" in "$EV_OWNER_REPO"/*) forms+=("${abs#"$EV_OWNER_REPO"/}") ;; esac
  fi
  while IFS=$'\t' read -r sp ssha vp vsha rest; do
    [ -n "${sp:-}" ] || continue
    [ "$sp" = "source_path" ] && continue
    case "$sp" in '#'*) continue ;; esac
    [ -n "${vp:-}" ] || continue
    local f hit=0
    for f in "${forms[@]}"; do [ "$sp" = "$f" ] && { hit=1; break; }; done
    [ "$hit" = 1 ] || continue
    case "$kind" in
      file)
        local actual
        actual=$(sha256sum -- "$abs" 2>/dev/null | cut -d' ' -f1 || true)
        [ -n "$actual" ] && [ "${ssha:-}" = "$actual" ] || continue
        ;;
      dir)
        case "${ssha:-}" in -|dir|directory) : ;; *) continue ;; esac
        ;;
    esac
    local vabs="" cand
    case "$vp" in
      /*) [ -e "$vp" ] && vabs="$vp" ;;
      *)
        for cand in "$SHOKUNIN_ROOT/$vp" "$(dirname -- "$ledger")/$vp"; do
          [ -e "$cand" ] && { vabs="$cand"; break; }
        done
        ;;
    esac
    [ -n "$vabs" ] || continue
    is_secret_path "$vabs" && continue
    if [ -f "$vabs" ]; then
      local vsha_actual
      vsha_actual=$(sha256sum -- "$vabs" 2>/dev/null | cut -d' ' -f1 || true)
      [ -n "$vsha_actual" ] && [ "$vsha_actual" = "${vsha:-}" ] || continue
    elif [ -d "$vabs" ]; then
      :
    else
      continue
    fi
    printf 'vault=%s sha=%s' "$vabs" "$(printf '%s' "${ssha:-}" | cut -c1-12)"
    return 0
  done < "$ledger"
  return 1
}

# ------------------------------------------------------ scratch / staleness

scratch_desc() { # <abs> -> description or empty
  local abs="$1" name base=""
  name=$(basename -- "$abs")
  case "$name" in
    *.tmp|*.out|*.log) base=ext ;;
    *checkpoint*.json|*checkpoint*.png) base=checkpoint ;;
    *-draft.*) base=draft ;;
  esac
  case "$abs" in
    */.scratch|*/.scratch/*)
      if [ -n "$base" ]; then printf 'dotted-scratch/%s' "$base"; else printf 'dotted-scratch'; fi
      return 0 ;;
  esac
  if [ -d "$abs" ] && [ "$name" = "out" ]; then printf 'out-dir'; return 0; fi
  [ -n "$base" ] && printf '%s' "$base"
  return 0
}

age_days() { # <abs> -> integer days since mtime, or empty when unknown
  local m now
  m=$(stat -c %Y -- "$1" 2>/dev/null || true)
  [ -n "$m" ] || { printf ''; return 0; }
  now=$(date +%s)
  printf '%s' $(((now - m) / 86400))
}

ref_count() { # <abs> <basename> -> number of files mentioning the basename
  local abs="$1" name="$2" root="" out rc=0
  case "$abs" in "$SHOKUNIN_ROOT"/*) root="$SHOKUNIN_ROOT" ;; esac
  if [ -z "$root" ] && [ -n "${EV_OWNER_REPO:-}" ]; then root="$EV_OWNER_REPO"; fi
  if [ -z "$root" ]; then root=$(dirname -- "$abs"); fi
  # ripgrep anchors -g globs to the current working directory, so run the
  # sweep with cwd = search root; unreadable/absent roots count as referenced.
  if [ ! -d "$root" ] || [ ! -r "$root" ] || [ ! -x "$root" ]; then printf '1'; return 0; fi
  out=$( cd -- "$root" 2>/dev/null && rg -l --no-ignore \
        -g '!.git' \
        -g '!souji-shokunin/census/**' \
        -g '!souji-shokunin/tests/**' \
        -g '!**/.ufo-quarantine/**' \
        -g '!.ufo/**' \
        -g '!*.env' -g '!*.env.*' -g '!.env*' \
        -g '!*credential*' -g '!*secret*' -g '!id_*' -g '!*.pem' \
        -- "$name" . 2>/dev/null ) || rc=$?
  if [ "$rc" -gt 1 ]; then printf '1'; return 0; fi
  nl_count "$out"
}

# ------------------------------------------------------------------ evaluator
# evaluate() sets: EV_RAW EV_ABS EV_KIND EV_VERDICT EV_REASON EV_EVIDENCE

evaluate() {
  local raw="$1"
  EV_RAW="$raw"; EV_ABS=""; EV_KIND="artifact"; EV_OWNER_REPO=""
  EV_VERDICT="NOT-SAFE"; EV_REASON="none"; EV_EVIDENCE=""

  if [ -z "$raw" ]; then
    EV_REASON="unreachable"; EV_EVIDENCE="empty-target"
    return 0
  fi
  local abs
  abs=$(norm "$raw")
  EV_ABS="$abs"

  if is_secret_path "$raw" || is_secret_path "$abs"; then
    EV_KIND="secrets"; EV_REASON="secrets-refusal"
    EV_EVIDENCE="path=secret-shaped never-read"
    return 0
  fi

  local exists=0 isdir=0
  [ -e "$abs" ] && exists=1
  [ -d "$abs" ] && isdir=1
  local gitfile=0 gitdir_entry=0
  [ -f "$abs/.git" ] && gitfile=1
  [ -d "$abs/.git" ] && gitdir_entry=1

  if [ "$gitfile" = 1 ]; then
    EV_KIND="worktree"
    eval_worktree "$abs"
    return 0
  fi
  if [ "$gitdir_entry" = 1 ]; then
    EV_KIND="repo-root"
    eval_repo_root "$abs"
    return 0
  fi
  if [ "$exists" = 0 ] || [ "$isdir" = 1 ]; then
    if wt_find_owner "$abs"; then
      EV_KIND="worktree"
      eval_worktree_verdict "$abs" "$WT_OWNER" 1
      return 0
    fi
    if [ "$exists" = 0 ]; then
      EV_REASON="unreachable"; EV_EVIDENCE="path=absent no-worktree-registration"
      return 0
    fi
  fi
  EV_KIND="artifact"
  eval_artifact "$abs"
}

eval_repo_root() {
  local abs="$1" unpushed dirty m
  EV_OWNER_REPO="$abs"
  if m=$(ledger_match "$abs" dir); then
    EV_VERDICT="SAFE"; EV_REASON="moved-to-obsidian"; EV_EVIDENCE="$m"
    return 0
  fi
  unpushed=$(git_count "$abs" log --oneline --branches --not --remotes)
  dirty=$(git_count "$abs" status --porcelain)
  EV_EVIDENCE="unpushed=$unpushed dirty=$dirty"
  if [ "$unpushed" != "0" ] || [ "$dirty" != "0" ]; then
    EV_REASON="unpushed/dirty"
  else
    EV_REASON="none"
  fi
}

eval_worktree() { # present directory carrying a `.git` file
  local abs="$1" owner id parsed r
  if parsed=$(parse_gitfile "$abs/.git"); then
    owner=${parsed%%$'\t'*}
    id=${parsed#*$'\t'}
    wt_candidates "$abs"
    for r in "${WT_CANDS[@]:-}"; do
      [ -n "$r" ] || continue
      wt_scan_repo "$r" "$abs"
      if [ "$WT_FOUND" = 1 ]; then eval_worktree_verdict "$abs" "$r" 1; return 0; fi
    done
    wt_scan_repo "$owner" "$abs"
    if [ "$WT_FOUND" = 1 ]; then eval_worktree_verdict "$abs" "$owner" 1; return 0; fi
    wt_admin_head "$owner" "$id"
    eval_worktree_verdict "$abs" "$owner" 0
    return 0
  fi
  if wt_find_owner "$abs"; then
    eval_worktree_verdict "$abs" "$WT_OWNER" 1
  else
    eval_worktree_verdict "$abs" "" 0
  fi
}

# eval_worktree_verdict <abs> <owner> <registered:1|0>
eval_worktree_verdict() {
  local abs="$1" owner="$2" registered="$3"
  local present=0 dirty=0 unique="" unpushed="" brshort="" head_ok=0
  [ -d "$abs" ] && present=1
  if [ "$present" = 1 ]; then dirty=$(git_count "$abs" status --porcelain); fi
  if [ -n "$owner" ] && [ -n "${WT_HEAD:-}" ] \
     && [ "$WT_HEAD" != "0000000000000000000000000000000000000000" ] \
     && git -C "$owner" cat-file -e "$WT_HEAD^{commit}" >/dev/null 2>&1; then
    head_ok=1
    unique=$(git_count "$owner" log --oneline "$WT_HEAD" --not --all)
  fi
  if [ -n "${WT_BRANCH:-}" ]; then
    brshort=${WT_BRANCH#refs/heads/}
    unpushed=$(git_count "$owner" log --oneline "$WT_BRANCH" --not --remotes)
  fi

  if [ "$registered" = 0 ] || [ -z "$owner" ]; then
    EV_REASON="worktree-unregistered"
    EV_EVIDENCE="dir=$([ "$present" = 1 ] && printf present || printf absent) gitfile-owner-unverified"
    return 0
  fi
  if [ "$present" = 1 ] && [ "$dirty" != "0" ]; then
    EV_REASON="dirty"; EV_EVIDENCE="dirty=$dirty dir=present owner=$owner"; return 0
  fi
  if [ -n "$brshort" ] && [ -n "$unpushed" ] && [ "$unpushed" != "0" ]; then
    EV_REASON="unpushed-branch"
    EV_EVIDENCE="branch=$brshort unpushed=$unpushed unique=${unique:-?}"; return 0
  fi
  if [ "$present" = 0 ]; then
    if [ "$head_ok" = 1 ] && [ "$unique" = "0" ]; then
      EV_VERDICT="SAFE"; EV_REASON="metadata-prune"
      EV_EVIDENCE="dir=absent unique=0 branch=${brshort:-detached} owner=$owner"
      return 0
    fi
    if [ "$head_ok" = 1 ]; then
      EV_REASON="unique-commits"; EV_EVIDENCE="dir=absent unique=$unique owner=$owner"; return 0
    fi
    EV_REASON="head-unknown"; EV_EVIDENCE="dir=absent head-unresolvable owner=$owner"; return 0
  fi
  if [ "$head_ok" = 1 ] && [ "$unique" != "0" ]; then
    EV_REASON="unique-commits"; EV_EVIDENCE="dir=present unique=$unique owner=$owner"; return 0
  fi
  EV_REASON="worktree-present"
  EV_EVIDENCE="dir=present dirty=$dirty unique=${unique:-?} owner=$owner"
}

eval_artifact() {
  local abs="$1" name owner="" pushed_reason="none" sha rel default_ref
  name=$(basename -- "$abs")
  if owner=$(find_owner_repo "$abs"); then :; else owner=""; fi
  EV_OWNER_REPO="$owner"

  if [ -n "$owner" ]; then
    rel=${abs#"$owner"/}
    sha=$(git_out "$owner" log --diff-filter=A --format=%H -1 -- "$rel")
    sha=$(printf '%s\n' "$sha" | head -n 1)
    if [ -n "$sha" ]; then
      if default_ref=$(resolve_default_ref "$owner"); then
        if git -C "$owner" merge-base --is-ancestor "$sha" "$default_ref" 2>/dev/null; then
          local dirty
          dirty=$(git_count "$owner" status --porcelain -- "$rel")
          EV_VERDICT="SAFE"; EV_REASON="pushed"
          EV_EVIDENCE="commit=${sha:0:12} ref=$default_ref dirty=$dirty"
          return 0
        fi
        pushed_reason="pushed-unverifiable"
      else
        pushed_reason="pushed-unverifiable"
      fi
    else
      pushed_reason="none"
    fi
  fi

  local kind="file"
  [ -d "$abs" ] && kind="dir"
  local m
  if m=$(ledger_match "$abs" "$kind"); then
    EV_VERDICT="SAFE"; EV_REASON="moved-to-obsidian"; EV_EVIDENCE="$m"
    return 0
  fi

  local desc refs age
  desc=$(scratch_desc "$abs")
  if [ -n "$desc" ]; then
    refs=$(ref_count "$abs" "$name")
    age=$(age_days "$abs")
    if [ "$refs" = "0" ] && [ -n "$age" ] && [ "$age" -gt "$STALE_DAYS" ]; then
      EV_VERDICT="SAFE"; EV_REASON="stale"
      EV_EVIDENCE="scratch=$desc refs=0 mtime_age_days=$age"
      return 0
    fi
    EV_EVIDENCE="scratch=$desc refs=$refs mtime_age_days=${age:-?} owner=${owner:-none}"
  else
    EV_EVIDENCE="scratch=no owner=${owner:-none} introducing=${sha:+${sha:0:12}}"
    [ -n "$sha" ] || EV_EVIDENCE="scratch=no owner=${owner:-none} introducing=none"
  fi
  EV_VERDICT="NOT-SAFE"; EV_REASON="$pushed_reason"
}

# ------------------------------------------------------------------ selftest

ST_PASS=0
ST_FAIL=0
ST_FIXTURE=""
ST_TMPDIR=""

st_ok()  { ST_PASS=$((ST_PASS + 1)); printf 'PASS %s\n' "$1"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); printf 'FAIL %s :: %s\n' "$1" "$2"; }

# st_check <case> <target> <expected-verdict> <expected-receipt-or-reason> [evidence-substring]
st_check() {
  local case_id="$1" target="$2" want_v="$3" want_r="$4" want_ev="${5:-}"
  local out rc=0 line v r ev
  out=$(SHOKUNIN_ROOT="$ST_FIXTURE" PATH="$ST_FIXTURE/bin:$PATH" \
        bash "$SELF" --stale-days 1 -- "$target" 2>&1) || rc=$?
  if [ "$rc" != "0" ]; then
    st_bad "$case_id" "exit=$rc output=$(printf '%s' "$out" | head -n 2 | tr '\n' '|')"
    return 0
  fi
  line=$(printf '%s\n' "$out" | head -n 1)
  v=$(printf '%s' "$line" | cut -f3)
  r=$(printf '%s' "$line" | cut -f4)
  ev=$(printf '%s' "$line" | cut -f5)
  if [ "${v:-}" != "$want_v" ] || [ "${r:-}" != "$want_r" ]; then
    st_bad "$case_id" "want $want_v($want_r) got ${v:-?}(${r:-?})"
    return 0
  fi
  if [ -n "$want_ev" ]; then
    case "$ev" in
      *"$want_ev"*) : ;;
      *) st_bad "$case_id" "evidence '$ev' lacks '$want_ev'"; return 0 ;;
    esac
  fi
  st_ok "$case_id"
}

st_repo() { # <dir>
  mkdir -p "$1"
  git -C "$1" init -q -b master
  git -C "$1" config user.email souji-selftest@local
  git -C "$1" config user.name souji-selftest
  git -C "$1" config commit.gpgsign false
}

st_commit() { # <repo> <msg> -> new commit sha on master (plumbing only)
  local repo="$1" msg="$2" tree parent sha
  git -C "$repo" add -A
  tree=$(git -C "$repo" write-tree)
  parent=$(git -C "$repo" rev-parse --verify --quiet HEAD || true)
  if [ -n "$parent" ]; then
    sha=$(git -C "$repo" commit-tree "$tree" -p "$parent" -m "$msg")
  else
    sha=$(git -C "$repo" commit-tree "$tree" -m "$msg")
  fi
  git -C "$repo" update-ref refs/heads/master "$sha"
  printf '%s' "$sha"
}

st_admin() { # <owner> <admin-id> <worktree-path> <HEAD: sha | 'ref: refs/heads/x'>
  local a="$1/.git/worktrees/$2"
  mkdir -p "$a"
  printf '%s/.git\n' "$3" > "$a/gitdir"
  printf '../..\n' > "$a/commondir"
  printf '%s\n' "$4" > "$a/HEAD"
}

st_origin() { git -C "$1" update-ref "refs/remotes/origin/$2" "$3"; }

run_selftest() {
  local F
  ST_TMPDIR=$(mktemp -d "${TMPDIR:-/tmp}/souji-verify.XXXXXX")
  F="$ST_TMPDIR"
  ST_FIXTURE="$ST_TMPDIR"
  # EXIT traps are inherited by $(...) subshells; only the main shell may clean up.
  trap 'if [ "$BASHPID" = "$$" ]; then rm -rf "$ST_TMPDIR"; fi' EXIT INT TERM

  mkdir -p "$F/bin" "$F/corpus/knowledge" "$F/vault"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' \
    > "$F/corpus/knowledge/obsidian-ledger.tsv"

  # path shim: the tool must never invoke a state-mutating git verb
  {
    printf '#!/usr/bin/env bash\n'
    printf 'LOG=%q\n' "$F/forbidden.log"
    printf 'REAL_GIT=%q\n' "$REAL_GIT"
    cat <<'SHIM'
sub=${1:-}
[ "$sub" = "-C" ] && sub=${3:-}
case "$sub" in
  fetch|push|commit|branch|checkout|reset|rebase)
    printf 'FORBIDDEN git %s\n' "$sub" >> "$LOG"
    exit 99 ;;
esac
exec "$REAL_GIT" "$@"
SHIM
  } > "$F/bin/git"
  chmod +x "$F/bin/git"
  : > "$F/forbidden.log"

  # ---- F1 / F10 repo: pushed file, origin/HEAD symref
  local R1="$F/f1-shokunin" c1 c2
  st_repo "$R1"
  mkdir -p "$R1/data" "$R1/config"
  printf 'one\n' > "$R1/data/kept.txt"
  c1=$(st_commit "$R1" "c1 base")
  printf 'payload\n' > "$R1/data/pushed.txt"
  c2=$(st_commit "$R1" "c2 adds pushed.txt")
  st_origin "$R1" master "$c2"
  git -C "$R1" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  printf 'KEY=value\n' > "$R1/config/settings.env"

  # ---- F2 repo: file whose introducing commit is local-only
  local R2="$F/f2-shokunin" d1
  st_repo "$R2"
  printf 'base\n' > "$R2/base.txt"
  d1=$(st_commit "$R2" "d1 base")
  st_origin "$R2" master "$d1"
  printf 'local only\n' > "$R2/local-only.txt"
  st_commit "$R2" "d2 adds local-only.txt" >/dev/null

  # ---- F3 repo: unpushed commits + dirty tree (kotodama-shaped)
  local R3="$F/f3-shokunin" e1
  st_repo "$R3"
  printf 'v1\n' > "$R3/tracked.txt"
  e1=$(st_commit "$R3" "e1 base")
  st_origin "$R3" master "$e1"
  printf 'v2\n' > "$R3/tracked.txt"
  st_commit "$R3" "e2 unpushed work" >/dev/null
  printf 'v2-dirty\n' > "$R3/tracked.txt"

  # ---- F9 repo: no origin/HEAD, exactly one origin branch ref (trunk)
  local R9="$F/f9-shokunin" g1
  st_repo "$R9"
  mkdir -p "$R9/data"
  printf 'single origin ref\n' > "$R9/data/single.txt"
  g1=$(st_commit "$R9" "g1 base")
  st_origin "$R9" trunk "$g1"

  # ---- F4/F4b/F5/F5b: worktree registrations
  local RW="$F/f45-shokunin" w1 tree_w orphan branch_commit
  st_repo "$RW"
  printf 'w\n' > "$RW/w.txt"
  w1=$(st_commit "$RW" "w1 base")
  st_origin "$RW" master "$w1"
  tree_w=$(git -C "$RW" rev-parse 'HEAD^{tree}')
  orphan=$(git -C "$RW" commit-tree "$tree_w" -m "commit on no ref")      # F4b
  branch_commit=$(git -C "$RW" commit-tree "$tree_w" -m "branch-only commit")
  git -C "$RW" update-ref refs/heads/wt-branch "$branch_commit"           # F5
  st_admin "$RW" wt-absent-det "$F/wt-absent-det" "$w1"
  st_admin "$RW" wt-orphan "$F/wt-orphan" "$orphan"
  st_admin "$RW" wt-branch "$F/wt-absent-branch" "ref: refs/heads/wt-branch"
  local WTP="$F/wt-present"
  mkdir -p "$WTP"
  printf 'gitdir: %s/.git/worktrees/wt-present\n' "$RW" > "$WTP/.git"
  st_admin "$RW" wt-present "$WTP" "ref: refs/heads/master"
  git -C "$WTP" read-tree HEAD
  git -C "$WTP" checkout-index -af -q --prefix="$WTP/"
  printf 'dirty\n' >> "$WTP/w.txt"                                        # F5b

  # ---- F6/F6b: ledger-matched file, and a row whose source sha does not match
  local R6="$F/f6-shokunin" s1 v1 s2 v2
  st_repo "$R6"
  mkdir -p "$R6/data"
  printf 'preserved payload\n' > "$R6/data/preserved.txt"
  cp "$R6/data/preserved.txt" "$F/vault/preserved.txt"
  printf 'not the same\n' > "$R6/data/preserved-2.txt"
  cp "$R6/data/preserved-2.txt" "$F/vault/preserved-2.txt"
  s1=$(sha256sum "$R6/data/preserved.txt" | cut -d' ' -f1)
  v1=$(sha256sum "$F/vault/preserved.txt" | cut -d' ' -f1)
  s2=$(sha256sum "$R6/data/preserved-2.txt" | cut -d' ' -f1)
  v2=$(sha256sum "$F/vault/preserved-2.txt" | cut -d' ' -f1)
  printf 'f6-shokunin/data/preserved.txt\t%s\tvault/preserved.txt\t%s\t2026-10-18\tselftest\n' \
    "$s1" "$v1" >> "$F/corpus/knowledge/obsidian-ledger.tsv"
  printf 'f6-shokunin/data/preserved-2.txt\t%s\tvault/preserved-2.txt\t%s\t2026-10-18\tselftest-bad-source-sha\n' \
    "${s2%?}x" "$v2" >> "$F/corpus/knowledge/obsidian-ledger.tsv"

  # ---- F7/F7b/F8: scratch files in a souji-shaped repo
  local RS="$F/souji-shokunin" old
  st_repo "$RS"
  mkdir -p "$RS/.scratch" "$RS/census" "$RS/tests" "$RS/.ufo-quarantine/old"
  printf 'hello world\n' > "$RS/.scratch/scratch-1.out"
  printf 'hello world\n' > "$RS/.scratch/scratch-2.out"
  printf 'fresh\n' > "$RS/.scratch/scratch-3.out"
  printf '{"rows":[{"path":"/x/.scratch/scratch-2.out"}]}\n' > "$RS/census/seat-01.json"
  printf 'notes mentioning scratch-2.out here\n' > "$RS/tests/fixture.txt"
  printf 'quarantine note scratch-2.out\n' > "$RS/.ufo-quarantine/old/note.txt"
  old=$(( $(date +%s) - 10 * 86400 ))
  touch -d "@$old" "$RS/.scratch/scratch-1.out" "$RS/.scratch/scratch-2.out"

  # ---- spec fixture cases -------------------------------------------------
  st_check F1   "$R1/data/pushed.txt"          SAFE     pushed            "commit="
  st_check F1b  "$R1/data/pushed.txt"          SAFE     pushed            "ref=refs/remotes/origin/master"
  st_check F1c  "$R1/data/kept.txt"            SAFE     pushed
  st_check F2   "$R2/local-only.txt"           NOT-SAFE pushed-unverifiable
  st_check F3   "$R3"                          NOT-SAFE "unpushed/dirty"  "unpushed=1 dirty=1"
  st_check F4   "$F/wt-absent-det"             SAFE     metadata-prune    "dir=absent unique=0"
  st_check F5   "$F/wt-absent-branch"          NOT-SAFE unpushed-branch   "unpushed=1"
  st_check F6   "$R6/data/preserved.txt"       SAFE     moved-to-obsidian
  st_check F7   "$RS/.scratch/scratch-1.out"   SAFE     stale             "scratch=dotted-scratch/ext refs=0"
  st_check F8   "$RS/.scratch/scratch-2.out"   SAFE     stale             "refs=0"
  st_check F9   "$R9/data/single.txt"          SAFE     pushed            "ref=refs/remotes/origin/trunk"
  st_check F10  "$R1/config/settings.env"      NOT-SAFE secrets-refusal
  # ---- extra cases (round-1 error patterns and edge shapes) ---------------
  st_check F4b  "$F/wt-orphan"                 NOT-SAFE unique-commits    "unique=1"
  st_check F5b  "$F/wt-present"                NOT-SAFE dirty             "dirty=1"
  st_check F6b  "$R6/data/preserved-2.txt"     NOT-SAFE none
  st_check F7b  "$RS/.scratch/scratch-3.out"   NOT-SAFE none              "refs=0"
  st_check F10b "$R1/config/absent.env"        NOT-SAFE secrets-refusal
  st_check FB1  ""                             NOT-SAFE unreachable
  st_check FB2  "$F/does-not-exist-xyz"        NOT-SAFE unreachable
  st_check FB3  "$F/corpus"                    NOT-SAFE none
  st_check FB4  "$R1"                          NOT-SAFE none              "unpushed=0 dirty=0"

  if [ -s "$F/forbidden.log" ]; then
    st_bad RAIL "forbidden git verbs attempted: $(tr '\n' ',' < "$F/forbidden.log")"
  else
    st_ok RAIL
  fi

  rm -rf "$ST_TMPDIR"
  printf 'selftest: %d passed, %d failed\n' "$ST_PASS" "$ST_FAIL"
  [ "$ST_FAIL" = "0" ]
}

# ---------------------------------------------------------------------- main

REAL_GIT=$(command -v git || true)
for dep in git rg sha256sum; do
  command -v "$dep" >/dev/null 2>&1 || { printf '%s: missing dependency: %s\n' "$PROG" "$dep" >&2; exit 1; }
done

TARGETS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1 ;;
    --json) JSON=1 ;;
    --stale-days)
      shift; [ $# -gt 0 ] || usage_err "--stale-days needs a value"
      case "$1" in ''|*[!0-9]*) usage_err "--stale-days wants a whole number of days" ;; esac
      STALE_DAYS="$1" ;;
    --stale-days=*)
      STALE_DAYS="${1#--stale-days=}"
      case "$STALE_DAYS" in ''|*[!0-9]*) usage_err "--stale-days wants a whole number of days" ;; esac ;;
    -h|--help) usage; exit 0 ;;
    --) shift; while [ $# -gt 0 ]; do TARGETS+=("$1"); shift; done; break ;;
    -*) usage_err "unknown option: $1" ;;
    *) TARGETS+=("$1") ;;
  esac
  shift
done

if [ "$SELFTEST" = 1 ]; then
  if run_selftest; then exit 0; else exit 1; fi
fi

if [ "${#TARGETS[@]}" = 0 ]; then
  usage_err "no targets given"
fi

first=1
if [ "$JSON" = 1 ]; then printf '['; fi
for t in "${TARGETS[@]}"; do
  evaluate "$t"
  if [ "$JSON" = 1 ]; then
    [ "$first" = 1 ] || printf ','
    first=0
    printf '\n  {"path":"%s","verdict":"%s","receipt_or_reason":"%s","evidence":"%s","kind":"%s"}' \
      "$(jesc "$EV_RAW")" "$EV_VERDICT" "$(jesc "$EV_REASON")" "$(jesc "$(fsan "$EV_EVIDENCE")")" "$EV_KIND"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' \
      "$(fsan "$EV_RAW")" "$EV_VERDICT" "$(fsan "$EV_REASON")" "$(fsan "$EV_EVIDENCE")"
  fi
done
if [ "$JSON" = 1 ]; then
  if [ "$first" = 1 ]; then printf ']\n'; else printf '\n]\n'; fi
fi

if [ "$ERRORS" != "0" ]; then exit 1; fi
exit 0
