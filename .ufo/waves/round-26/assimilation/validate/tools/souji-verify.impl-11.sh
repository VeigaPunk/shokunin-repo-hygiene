#!/usr/bin/env bash
# tools/souji-verify.sh — receipt-gated verifier for artifact removal.
#
# Binding spec: tools/souji-verify.spec.md (round 2). Fixes round-1 defects
# D1 (default-branch resolution), D2 (artifact-kind branches), D3 (reference
# check glob exclusions).
#
# Output, one line per target:
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>decisive-evidence
#
# Read-only over every surface it inspects. Never runs git fetch/push/commit/
# branch/checkout/reset/rebase; never writes outside a mktemp dir created by
# --selftest; never touches .ufo/state, .ufo/watchdog.log or ~/.config.
#
# Environment overrides (used by --selftest so it stays off the live tree):
#   SHOKUNIN_ROOT   fleet root scanned for worktree owners (default: lane/..)
#   SOUJI_LEDGER    obsidian ledger (default: corpus/knowledge/obsidian-ledger.tsv)
#
# Two documented substitutions, because the environment cannot run the spec
# text verbatim:
#   * rg 15.2 has no --basename flag (rc=2 "unrecognized flag"). The D3
#     reference check therefore runs
#       rg -l --no-ignore --fixed-strings -- <name> . -g '!.git' \
#          -g '!souji-shokunin/census/**' -g '!souji-shokunin/tests/**' \
#          -g '!**/.ufo-quarantine/**'
#     with the repo root as cwd: the `-g` exclusions only anchor on relative
#     paths (verified: with an absolute root the census hit leaks through).
#     Hits under census/tests/.ufo-quarantine are then dropped again in a
#     defensive post-filter.
#   * a directory has no single file sha256, so a ledger row for a directory
#     records dir_digest() below: sha256 over the path-sorted `sha256sum`
#     listing of every regular file under it (.git pruned).

set -euo pipefail
LC_ALL=C
export LC_ALL

SELF=${BASH_SOURCE[0]}
SCRIPT_DIR=$(cd -- "$(dirname -- "$SELF")" >/dev/null 2>&1 && pwd -P)
LANE_DIR=$(cd -- "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd -P)
SHOKUNIN_ROOT=${SHOKUNIN_ROOT:-$(cd -- "$LANE_DIR/.." >/dev/null 2>&1 && pwd -P)}
LEDGER=${SOUJI_LEDGER:-$LANE_DIR/corpus/knowledge/obsidian-ledger.tsv}

STALE_DAYS=1
JSON=0
SELFTEST=0
ERRORS=0
FT=""                 # fixture tmpdir, set by --selftest
CANDIDATES=()         # worktree-owner candidates

usage() {
  printf 'usage: %s [--selftest] [--stale-days N] [--json] <path>...\n' "${0##*/}"
}

usage_error() {
  printf '%s: %s\n' "${0##*/}" "$1" >&2
  usage >&2
  exit 2
}

# ---------------------------------------------------------------- utilities

note() { printf '%s\n' "$*" >&2; }

norm_path() {
  local p=${1-} out
  if [ -z "$p" ]; then return 0; fi
  if out=$(realpath -m -- "$p" 2>/dev/null); then
    printf '%s' "$out"
  else
    case $p in
      /*) printf '%s' "$p" ;;
      *)  printf '%s/%s' "${PWD:-.}" "$p" ;;
    esac
  fi
  return 0
}

count_lines() {   # count stdout lines of a command that is allowed to fail
  local n
  n=$({ "$@" 2>/dev/null || true; } | wc -l)
  printf '%s' "${n//[[:space:]]/}"
}

json_escape() {
  local s=${1-}
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  printf '"%s"' "$s"
}

is_secret_basename() {   # secret rails are case-insensitive (fail closed)
  local b
  b=$(printf '%s' "${1-}" | tr '[:upper:]' '[:lower:]')
  case $b in
    *.env|*credential*|*secret*|id_*|*.pem) return 0 ;;
  esac
  return 1
}

is_forbidden_scope() {   # operator state / config is never an artifact target
  local p=${1-}
  case $p in
    */.ufo/state|*/.ufo/state/*|*/.ufo/watchdog.log|*/.ufo/watchdog.log/*) return 0 ;;
  esac
  if [ -n "${HOME:-}" ]; then
    case $p in
      "$HOME"/.config|"$HOME"/.config/*) return 0 ;;
    esac
  fi
  return 1
}

is_scratch_type() {
  local abs=${1-} bn
  case $abs in
    */.scratch/*) return 0 ;;
  esac
  bn=$(basename -- "$abs" | tr '[:upper:]' '[:lower:]')
  case $bn in
    *.out|*.log|*-draft.*|*checkpoint*.json|*checkpoint*.png) return 0 ;;
  esac
  return 1
}

sha256_file() {
  local h
  h=$(sha256sum -- "${1-}" 2>/dev/null | awk '{print $1}') || return 1
  [ -n "$h" ] || return 1
  printf '%s' "$h"
}

dir_digest() {   # see header: sha256 over path-sorted `sha256sum` of files
  local d=${1-}
  { ( cd -- "$d" 2>/dev/null &&
      find . -path ./.git -prune -o -type f -print0 2>/dev/null \
        | LC_ALL=C sort -z \
        | xargs -0 -r sha256sum 2>/dev/null
    ) || true
  } | sha256sum | awk '{print $1}'
}

target_digest() {   # sha256 of a file, or dir_digest of a directory
  local t=${1-}
  if [ -L "$t" ]; then return 1; fi
  if [ -f "$t" ]; then sha256_file "$t" || return 1; return 0; fi
  if [ -d "$t" ]; then dir_digest "$t"; return 0; fi
  return 1
}

build_candidates() {
  local d
  CANDIDATES=()
  if [ -d "$SHOKUNIN_ROOT" ]; then CANDIDATES+=("$SHOKUNIN_ROOT"); fi
  for d in "$SHOKUNIN_ROOT"/*-shokunin; do
    [ -d "$d" ] && CANDIDATES+=("$d")
  done
  return 0
}

# ------------------------------------------------------- git/ledger receipts

default_ref() {   # D1: origin/HEAD -> single origin branch -> local master
  local repo=${1-} sym ref r
  local -a orefs=()
  sym=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  if [ -n "$sym" ]; then
    ref="refs/remotes/$sym"
    if git -C "$repo" rev-parse --verify --quiet "$ref" >/dev/null 2>&1; then
      printf '%s' "$ref"; return 0
    fi
  fi
  while IFS= read -r r; do
    [ -n "$r" ] && orefs+=("$r")
  done < <(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin/ 2>/dev/null \
             | grep -v 'refs/remotes/origin/HEAD$' || true)
  if [ "${#orefs[@]}" -eq 1 ]; then
    printf '%s' "${orefs[0]}"; return 0
  fi
  if git -C "$repo" rev-parse --verify --quiet refs/heads/master >/dev/null 2>&1; then
    printf 'refs/heads/master'; return 0
  fi
  return 1
}

ledger_match() {   # prints "ledger_row=N src_sha256=.. vault_sha256=.." on hit
  local target=${1-} want ln=0 spath ssha vpath vsha rest want_sha i vactual
  local -a cand_ln=() cand_sha=() cand_vpath=() cand_vsha=()
  [ -f "$LEDGER" ] && [ -r "$LEDGER" ] || return 1
  want=$(norm_path "$target")
  # pass 1 — cheap: collect rows recorded for this exact source path only.
  # Nothing is hashed unless a row already names this path.
  while IFS=$'\t' read -r spath ssha vpath vsha rest || [ -n "${spath:-}" ]; do
    ln=$((ln + 1))
    case $spath in ''|'#'*|source_path) continue ;; esac
    [ -n "$ssha" ] && [ -n "$vpath" ] && [ -n "$vsha" ] || continue
    [ "$(norm_path "$spath")" = "$want" ] || continue
    cand_ln+=("$ln"); cand_sha+=("$ssha")
    cand_vpath+=("$vpath"); cand_vsha+=("$vsha")
  done < "$LEDGER"
  [ "${#cand_ln[@]}" -gt 0 ] || return 1
  # pass 2 — expensive: both sides must hash to the recorded values
  want_sha=$(target_digest "$target") || return 1
  [ -n "$want_sha" ] || return 1
  for i in "${!cand_ln[@]}"; do
    [ "${cand_sha[$i]}" = "$want_sha" ] || continue
    [ -e "${cand_vpath[$i]}" ] || continue
    vactual=$(target_digest "${cand_vpath[$i]}") || continue
    [ "$vactual" = "${cand_vsha[$i]}" ] || continue
    printf 'ledger_row=%s src_sha256=%s vault_sha256=%s' \
      "${cand_ln[$i]}" "${cand_sha[$i]:0:12}" "${vactual:0:12}"
    return 0
  done
  return 1
}

find_worktree() {   # prints "owner<TAB>head<TAB>branch" for an exact match
  local want=${1-} cand out line p head branch hit
  for cand in ${CANDIDATES[@]+"${CANDIDATES[@]}"}; do
    out=$(git -C "$cand" worktree list --porcelain 2>/dev/null) || continue
    [ -n "$out" ] || continue
    p=""; head=""; branch=""; hit=0
    while IFS= read -r line; do
      case $line in
        'worktree '*)
          p=${line#worktree }
          head=""; branch=""
          if [ "$(norm_path "$p")" = "$want" ]; then hit=1; else hit=0; fi
          ;;
        'HEAD '*)   [ "$hit" -eq 1 ] && head=${line#HEAD } ;;
        'branch '*) [ "$hit" -eq 1 ] && branch=${line#branch } ;;
        'detached') [ "$hit" -eq 1 ] && branch='(detached)' ;;
        '')         if [ "$hit" -eq 1 ]; then
                      printf '%s\t%s\t%s' "$cand" "$head" "$branch"; return 0
                    fi
                    hit=0 ;;
      esac
    done <<< "$out"
    if [ "$hit" -eq 1 ]; then
      printf '%s\t%s\t%s' "$cand" "$head" "$branch"; return 0
    fi
  done
  return 1
}

refs_count() {   # D3: live references to basename; "ERR" if the search failed
  local name=${1-} root=${2-} raw rc n
  set +e
  raw=$( cd -- "$root" 2>/dev/null && \
         rg -l --no-ignore --fixed-strings \
            -g '!.git' \
            -g '!souji-shokunin/census/**' \
            -g '!souji-shokunin/tests/**' \
            -g '!**/.ufo-quarantine/**' \
            -- "$name" . 2>/dev/null )
  rc=$?
  set -e
  case $rc in
    0|1) ;;
    *) printf 'ERR'; return 0 ;;
  esac
  n=$(printf '%s\n' "$raw" \
        | grep -v -E '(^|/)\.git/|(^|/)souji-shokunin/census/|(^|/)souji-shokunin/tests/|(^|/)\.ufo-quarantine/' \
        | grep -c . || true)
  printf '%s' "${n//[[:space:]]/}"
}

# ------------------------------------------------------------- verification

verify_repo_root() {
  local path=${1-} unpushed dirty lm
  unpushed=$(count_lines git -C "$path" log --oneline HEAD --not --remotes)
  dirty=$(count_lines git -C "$path" status --porcelain)
  if lm=$(ledger_match "$path"); then
    printf 'SAFE\tmoved-to-obsidian\t%s\trepo-root\n' "$lm"
    return 0
  fi
  if [ "$unpushed" -gt 0 ]; then
    printf 'NOT-SAFE\tunpushed\tunpushed=%s dirty=%s\trepo-root\n' "$unpushed" "$dirty"
  elif [ "$dirty" -gt 0 ]; then
    printf 'NOT-SAFE\tdirty\tunpushed=%s dirty=%s\trepo-root\n' "$unpushed" "$dirty"
  else
    printf 'NOT-SAFE\tnone\tunpushed=%s dirty=%s\trepo-root\n' "$unpushed" "$dirty"
  fi
  return 0
}

verify_worktree() {
  local path=${1-} reg=${2-} owner head branch present=0 dirty=0 unique unpushed
  IFS=$'\t' read -r owner head branch <<< "$reg"
  [ -e "$path" ] && present=1
  if [ -n "$head" ] && git -C "$owner" rev-parse --verify --quiet "$head" >/dev/null 2>&1; then
    unique=$(count_lines git -C "$owner" log --oneline "$head" --not --all)
  else
    unique=$(count_lines git -C "$owner" log --oneline HEAD --not --all)
  fi
  if [ "$present" -eq 1 ]; then
    dirty=$(count_lines git -C "$path" status --porcelain)
  fi
  if [ "$present" -eq 0 ] && [ "$unique" -eq 0 ]; then
    printf 'SAFE\tmetadata-prune\towner=%s dir=absent unique=0\tworktree\n' "$owner"
    return 0
  fi
  if [ -n "$branch" ] && [ "$branch" != '(detached)' ]; then
    unpushed=$(count_lines git -C "$owner" log --oneline "$branch" --not --remotes)
    if [ "$unpushed" -gt 0 ]; then
      printf 'NOT-SAFE\tunpushed-branch\towner=%s branch=%s unpushed=%s dir=%s\tworktree\n' \
        "$owner" "$branch" "$unpushed" "$([ "$present" -eq 1 ] && echo present || echo absent)"
      return 0
    fi
  fi
  if [ "$present" -eq 1 ] && [ "$dirty" -gt 0 ]; then
    printf 'NOT-SAFE\tdirty\towner=%s branch=%s dirty=%s dir=present\tworktree\n' \
      "$owner" "${branch:-none}" "$dirty"
    return 0
  fi
  if [ "$present" -eq 0 ] && [ "$unique" -gt 0 ]; then
    printf 'NOT-SAFE\tunpushed-head\towner=%s branch=%s unique=%s dir=absent\tworktree\n' \
      "$owner" "${branch:-none}" "$unique"
    return 0
  fi
  printf 'NOT-SAFE\tnone\towner=%s branch=%s unique=%s dirty=%s dir=%s\tworktree\n' \
    "$owner" "${branch:-none}" "$unique" "$dirty" \
    "$([ "$present" -eq 1 ] && echo present || echo absent)"
  return 0
}

verify_artifact() {
  local target=${1-} abs base_dir repo="" ic bref lm
  local scratch=0 refs="" age_days="" mtime now
  abs=$(norm_path "$target")
  if [ -d "$target" ]; then base_dir=$target; else base_dir=$(dirname -- "$target"); fi
  repo=$(git -C "$base_dir" rev-parse --show-toplevel 2>/dev/null || true)

  # receipt 1 — pushed: the introducing commit is on the default branch ref
  if [ -n "$repo" ]; then
    ic=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$abs" 2>/dev/null || true)
    if [ -n "$ic" ]; then
      bref=$(default_ref "$repo" 2>/dev/null || true)
      if [ -z "$bref" ]; then
        printf 'NOT-SAFE\tpushed-unverifiable\tcommit=%s repo=%s\tartifact\n' "${ic:0:10}" "$repo"
        return 0
      fi
      if git -C "$repo" merge-base --is-ancestor "$ic" "$bref" 2>/dev/null; then
        printf 'SAFE\tpushed\tcommit=%s ref=%s\tartifact\n' "${ic:0:10}" "$bref"
        return 0
      fi
    fi
  fi

  # receipt 2 — moved-to-obsidian: ledger row, source and vault sha256 agree
  if lm=$(ledger_match "$target"); then
    printf 'SAFE\tmoved-to-obsidian\t%s\tartifact\n' "$lm"
    return 0
  fi

  # receipt 3 — stale: scratch type, zero live refs, older than --stale-days
  if is_scratch_type "$abs"; then
    scratch=1
    now=$(date +%s)
    mtime=$(stat -c %Y -- "$abs" 2>/dev/null || true)
    if [ -n "$mtime" ]; then
      age_days=$(( (now - mtime) / 86400 ))
    else
      age_days="unknown"
    fi
    if [ -n "$repo" ]; then
      refs=$(refs_count "$(basename -- "$abs")" "$repo")
    else
      refs=$(refs_count "$(basename -- "$abs")" "$base_dir")
    fi
    if [ "$refs" = "0" ] && [ -n "$mtime" ] && \
       [ "$(( now - mtime ))" -gt "$(( STALE_DAYS * 86400 ))" ]; then
      printf 'SAFE\tstale\trefs=0 age_days=%s stale_days=%s\tartifact\n' \
        "$age_days" "$STALE_DAYS"
      return 0
    fi
  fi

  # receipt 4 — none
  local why=""
  if [ -z "$repo" ]; then
    why="no-repo"
  elif [ -z "$ic" ]; then
    why="untracked"
  else
    why="introducer=${ic:0:10} not-on-default-ref"
  fi
  if [ "$scratch" -eq 1 ]; then
    why="$why scratch refs=$refs age_days=$age_days"
    if [ "$refs" = "ERR" ]; then
      printf 'NOT-SAFE\tnone\t%s\tartifact-error\n' "$why"
      return 0
    fi
  fi
  printf 'NOT-SAFE\tnone\t%s\tartifact\n' "$why"
  return 0
}

evaluate() {   # prints "verdict<TAB>receipt<TAB>evidence<TAB>kind"
  local target=${1-} npath reg
  if [ -z "$target" ]; then
    printf 'NOT-SAFE\tunreachable\tempty-target\tartifact\n'
    return 0
  fi
  npath=$(norm_path "$target")
  if is_secret_basename "$(basename -- "$target")"; then
    printf 'NOT-SAFE\tsecrets-refusal\tbasename-matches-secret-glob\tartifact\n'
    return 0
  fi
  if is_forbidden_scope "$npath"; then
    printf 'NOT-SAFE\tscope-refusal\tufo-state-or-operator-config\tartifact\n'
    return 0
  fi
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    if reg=$(find_worktree "$npath"); then
      verify_worktree "$target" "$reg"
    else
      printf 'NOT-SAFE\tunreachable\tpath-absent\tartifact\n'
    fi
    return 0
  fi
  if [ -d "$target" ] && [ -d "$target/.git" ]; then
    verify_repo_root "$target"
    return 0
  fi
  # a worktree registration can only name a directory; skip the owner scan for
  # plain files (the scan costs one `git worktree list` per fleet repo)
  if { [ -d "$target" ] || [ -L "$target" ]; } && reg=$(find_worktree "$npath"); then
    verify_worktree "$target" "$reg"
    return 0
  fi
  verify_artifact "$target"
  return 0
}

# ----------------------------------------------------------------- selftest

case_run() {   # NAME EXPECTED_VERDICT EXPECTED_RECEIPT(alternation) PATH [EVIDENCE_SUBSTR]
  local name=$1 want_v=$2 want_r=$3 path=$4 want_e=${5-}
  local line rc f3 f4 f5 nf alt found=0 ok=1
  set +e
  line=$(bash "$SELF" --stale-days "$STALE_DAYS" -- "$path" 2>"$FT/case.err")
  rc=$?
  set -e
  nf=$(printf '%s' "$line" | awk -F'\t' '{print NF}')
  f3=$(printf '%s' "$line" | cut -f3)
  f4=$(printf '%s' "$line" | cut -f4)
  f5=$(printf '%s' "$line" | cut -f5)
  [ "$rc" -eq 0 ] || ok=0
  [ "$nf" = 5 ] || ok=0
  [ "$f3" = "$want_v" ] || ok=0
  local IFS='|'
  for alt in $want_r; do [ "$f4" = "$alt" ] && found=1; done
  unset IFS
  [ "$found" -eq 1 ] || ok=0
  if [ -n "$want_e" ]; then
    case $f5 in *"$want_e"*) ;; *) ok=0 ;; esac
  fi
  if [ "$ok" -eq 1 ]; then
    printf 'selftest %-7s pass  rc=%s %s/%s  %s\n' "$name" "$rc" "$f3" "$f4" "$f5"
    SELFTEST_PASS=$((SELFTEST_PASS + 1))
  else
    printf 'selftest %-7s FAIL  want %s/%s%s  got rc=%s %s/%s  %s\n' \
      "$name" "$want_v" "$want_r" "${want_e:+ (evidence ~ $want_e)}" \
      "$rc" "$f3" "$f4" "$f5"
    printf '        raw: %s\n' "$line"
    [ -s "$FT/case.err" ] && sed 's/^/        err: /' "$FT/case.err"
    SELFTEST_FAIL=$((SELFTEST_FAIL + 1))
  fi
  return 0
}

run_selftest() {
  local origin own koto dead feat vsh ssh nrefs
  local -a gt=(git -c user.name=souji-fixture -c user.email=fixture@shokunin.local)

  SELFTEST_PASS=0
  SELFTEST_FAIL=0
  FT=$(mktemp -d)
  trap 'rm -rf -- "$FT"' EXIT
  mkdir -p "$FT"
  export SHOKUNIN_ROOT="$FT"
  export SOUJI_LEDGER="$FT/obsidian-ledger.tsv"
  export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1
  build_candidates

  origin="$FT/origin.git"
  own="$FT/fixture-shokunin"
  "${gt[@]}" init -q --bare --initial-branch=main "$origin"
  "${gt[@]}" clone -q "$origin" "$own" 2>/dev/null
  "${gt[@]}" -C "$own" config user.name souji-fixture
  "${gt[@]}" -C "$own" config user.email fixture@shokunin.local

  # F1 — tracked file, introducing commit pushed to the default branch
  mkdir -p "$own/tracked"
  printf 'kept content\n' > "$own/tracked/keep.md"
  "${gt[@]}" -C "$own" add tracked/keep.md
  "${gt[@]}" -C "$own" commit -qm "F1 tracked file"
  "${gt[@]}" -C "$own" push -q origin main
  "${gt[@]}" -C "$own" remote set-head origin main >/dev/null

  # F2 — introducing commit local-only
  printf 'local only\n' > "$own/local-only.md"
  "${gt[@]}" -C "$own" add local-only.md
  "${gt[@]}" -C "$own" commit -qm "F2 local only"

  # F3 — kotodama-shaped: pushed base, one unpushed commit, one dirty path
  koto="$FT/kotodama-shaped-shokunin"
  "${gt[@]}" init -q --bare --initial-branch=main "$FT/origin3.git"
  "${gt[@]}" init -q --initial-branch=main "$koto"
  "${gt[@]}" -C "$koto" config user.name souji-fixture
  "${gt[@]}" -C "$koto" config user.email fixture@shokunin.local
  printf 'base\n' > "$koto/base.md"
  "${gt[@]}" -C "$koto" add base.md
  "${gt[@]}" -C "$koto" commit -qm base
  "${gt[@]}" -C "$koto" remote add origin "$FT/origin3.git"
  "${gt[@]}" -C "$koto" push -q -u origin main
  printf 'unpushed\n' > "$koto/unpushed.md"
  "${gt[@]}" -C "$koto" add unpushed.md
  "${gt[@]}" -C "$koto" commit -qm "unpushed commit"
  printf 'scratch\n' > "$koto/dirty.tmp"

  # F4 / F5 — worktree registrations owned by the fixture repo
  dead="$FT/wt-dead"
  feat="$FT/wt-feature"
  "${gt[@]}" -C "$own" worktree add -q -b dead-branch "$dead" origin/main
  "${gt[@]}" -C "$own" worktree add -q -b feature-x "$feat" origin/main
  printf 'feature body\n' > "$feat/f.md"
  "${gt[@]}" -C "$feat" add f.md
  "${gt[@]}" -C "$feat" commit -qm "feature work"
  rm -rf -- "$dead"

  # F6 — ledger-matched file (source + vault sha256 agree)
  mkdir -p "$own/moved" "$FT/vault"
  printf 'archived body\n' > "$own/moved/thing.md"
  printf 'archived body\n' > "$FT/vault/thing.md"
  ssh=$(sha256sum -- "$own/moved/thing.md" | awk '{print $1}')
  vsh=$(sha256sum -- "$FT/vault/thing.md" | awk '{print $1}')
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$own/moved/thing.md" "$ssh" \
      "$FT/vault/thing.md" "$vsh" 2026-10-18 fixture-file
  } > "$SOUJI_LEDGER"

  # F6b (extension) — ledger-matched repo-root directory
  local arepo="$FT/archived-repo" avault="$FT/vault-archived"
  "${gt[@]}" init -q --initial-branch=main "$arepo"
  "${gt[@]}" -C "$arepo" config user.name souji-fixture
  "${gt[@]}" -C "$arepo" config user.email fixture@shokunin.local
  printf 'archived repo body\n' > "$arepo/body.md"
  "${gt[@]}" -C "$arepo" add body.md
  "${gt[@]}" -C "$arepo" commit -qm "archived repo"
  mkdir -p "$avault"
  cp -a "$arepo/." "$avault/"
  local adig vdig empty_sha
  adig=$(dir_digest "$arepo"); vdig=$(dir_digest "$avault")
  empty_sha=$(printf '' | sha256sum | awk '{print $1}')
  if [ "$adig" = "$empty_sha" ]; then
    printf 'selftest F6b     FAIL  fixture: dir_digest returned the empty-input hash\n'
    SELFTEST_FAIL=$((SELFTEST_FAIL + 1))
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$arepo" "$adig" \
    "$avault" "$vdig" 2026-10-18 fixture-dir >> "$SOUJI_LEDGER"

  # F6c (extension) — ledger row with a wrong source sha must NOT be a receipt
  local brepo="$FT/archived-repo-bad" bvault="$FT/vault-archived-bad"
  "${gt[@]}" init -q --initial-branch=main "$brepo"
  "${gt[@]}" -C "$brepo" config user.name souji-fixture
  "${gt[@]}" -C "$brepo" config user.email fixture@shokunin.local
  printf 'not really archived\n' > "$brepo/body.md"
  "${gt[@]}" -C "$brepo" add body.md
  "${gt[@]}" -C "$brepo" commit -qm "archived repo bad"
  mkdir -p "$bvault"
  cp -a "$brepo/." "$bvault/"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$brepo" \
    "0000000000000000000000000000000000000000000000000000000000000000" \
    "$bvault" "$(dir_digest "$bvault")" 2026-10-18 fixture-dir-bad >> "$SOUJI_LEDGER"

  # F7 / F8 — scratch files, no live references, mtime older than --stale-days
  mkdir -p "$own/.scratch" "$own/souji-shokunin/census"
  printf 'junk data one\n' > "$own/.scratch/junk-1.out"
  printf 'junk data two\n' > "$own/.scratch/junk-2.log"
  printf 'historical mention of junk-2.log lives here\n' > "$own/souji-shokunin/census/mentions.md"
  touch -d '4 days ago' "$own/.scratch/junk-1.out" "$own/.scratch/junk-2.log"

  # F10 — secret-shaped path
  mkdir -p "$own/config"
  printf 'TOKEN=not-a-real-secret\n' > "$own/config/app.env"

  case_run F1 SAFE  pushed                  "$own/tracked/keep.md"
  case_run F2 NOT-SAFE 'pushed-unverifiable|none' "$own/local-only.md"
  case_run F3 NOT-SAFE 'unpushed|dirty|none' "$koto" 'unpushed=1 dirty=1'
  case_run F4 SAFE  metadata-prune          "$dead"
  case_run F5 NOT-SAFE unpushed-branch      "$feat" 'unpushed=1'
  case_run F6 SAFE  moved-to-obsidian       "$own/moved/thing.md" 'ledger_row=2'
  case_run F6b SAFE moved-to-obsidian       "$arepo" 'ledger_row=3'
  case_run F6c NOT-SAFE 'unpushed|dirty|none' "$brepo" 'unpushed=1'
  case_run F7 SAFE  stale                   "$own/.scratch/junk-1.out" 'refs=0'
  case_run F8 SAFE  stale                   "$own/.scratch/junk-2.log" 'refs=0'
  # F9 — drop the origin/HEAD symref (--no-deref: never touch origin/main),
  # leaving exactly one refs/remotes/origin/* branch ref for D1's fallback.
  "${gt[@]}" -C "$own" update-ref --no-deref -d refs/remotes/origin/HEAD
  nrefs=$(git -C "$own" for-each-ref --format='%(refname)' refs/remotes/origin/ | grep -vc 'HEAD$' || true)
  if [ "$nrefs" = 1 ]; then
    case_run F9 SAFE pushed "$own/tracked/keep.md"
  else
    printf 'selftest F9      FAIL  fixture precondition: %s origin refs, want 1\n' "$nrefs"
    SELFTEST_FAIL=$((SELFTEST_FAIL + 1))
  fi
  case_run F10 NOT-SAFE secrets-refusal     "$own/config/app.env"

  # extension: usage errors exit 2, empty target stays exit 0
  local rc
  set +e
  bash "$SELF" >/dev/null 2>&1; rc=$?
  set -e
  if [ "$rc" -eq 2 ]; then
    printf 'selftest F-usage pass  rc=2 no-args\n'; SELFTEST_PASS=$((SELFTEST_PASS + 1))
  else
    printf 'selftest F-usage FAIL  want rc=2 got rc=%s\n' "$rc"; SELFTEST_FAIL=$((SELFTEST_FAIL + 1))
  fi
  set +e
  local eline
  eline=$(bash "$SELF" -- "" 2>/dev/null); rc=$?
  set -e
  if [ "$rc" -eq 0 ] && [ "$(printf '%s' "$eline" | cut -f4)" = unreachable ]; then
    printf 'selftest F-empty pass  rc=0 NOT-SAFE/unreachable\n'; SELFTEST_PASS=$((SELFTEST_PASS + 1))
  else
    printf 'selftest F-empty FAIL  want rc=0 NOT-SAFE/unreachable got rc=%s %s\n' "$rc" "$eline"
    SELFTEST_FAIL=$((SELFTEST_FAIL + 1))
  fi

  printf 'selftest summary: %s pass, %s fail\n' "$SELFTEST_PASS" "$SELFTEST_FAIL"
  [ "$SELFTEST_FAIL" -eq 0 ] || return 1
  return 0
}

# --------------------------------------------------------------------- main

targets=()
while [ $# -gt 0 ]; do
  case $1 in
    --selftest)   SELFTEST=1; shift ;;
    --json)       JSON=1; shift ;;
    --stale-days) [ $# -ge 2 ] || usage_error "--stale-days needs a value"; STALE_DAYS=$2; shift 2 ;;
    --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
    -h|--help)    usage; exit 0 ;;
    --)           shift; while [ $# -gt 0 ]; do targets+=("$1"); shift; done ;;
    -*)           usage_error "unknown option: $1" ;;
    *)            targets+=("$1"); shift ;;
  esac
done
case $STALE_DAYS in
  ''|*[!0-9]*) usage_error "--stale-days must be a non-negative integer" ;;
esac

if [ "$SELFTEST" -eq 1 ]; then
  [ "${#targets[@]}" -eq 0 ] || usage_error "--selftest takes no targets"
  set +e
  run_selftest
  rc=$?
  set -e
  exit "$rc"
fi

[ "${#targets[@]}" -gt 0 ] || usage_error "no targets given"

build_candidates

for t in "${targets[@]}"; do
  out=$(evaluate "$t" || printf 'ERROR\tevaluation-failed\tsubshell\tartifact-error\n')
  v=""; r=""; e=""; k=""
  IFS=$'\t' read -r v r e k <<< "$out"
  if [ "$v" = ERROR ]; then
    ERRORS=1
    v=NOT-SAFE; r=${r:-evaluation-error}; e=${e:-subshell-failed}
  fi
  case $k in *-error) ERRORS=1 ;; esac
  if [ "$JSON" -eq 1 ]; then
    printf '{"path":%s,"verdict":%s,"receipt":%s,"evidence":%s,"kind":%s}\n' \
      "$(json_escape "$t")" "$(json_escape "$v")" "$(json_escape "$r")" \
      "$(json_escape "$e")" "$(json_escape "$k")"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$t" "$v" "$r" "$e"
  fi
done

[ "$ERRORS" -eq 0 ] || exit 1
exit 0
