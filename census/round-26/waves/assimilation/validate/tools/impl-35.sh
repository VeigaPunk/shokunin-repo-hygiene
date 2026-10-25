#!/usr/bin/env bash
# impl-35 — round-6 implementor (seat S35).
#
# Axes this file serves:
#   calibration  --drift   docs vs installed tools; exit 3 while drift_count>0
#   operability  (default) repeatable read-only fleet census + --compare
#   coverage     --classify  full scratch inventory, metadata + <=200 byte headers
#
# Read-only over every surface it inspects. Never fetches, never writes
# outside a --selftest mktemp, never reads secret-shaped file contents,
# never follows a symlink root, never opens .ufo/state or .ufo/watchdog.log.
#
# Reconciled contract (docs must move to the tools; do not widen SAFE to
# match stale SKILL.md text — a false SAFE is this lane's worst failure):
#   pushed: no fetch; origin/HEAD or the single origin/* ref; local heads
#           never establish pushed; no remote-tracking ref → unverifiable
#   metadata-prune: worktree dir absent AND unique commits = 0
#   stale: tool scratch_type only (.scratch, *.out, *.log, *-draft.*,
#          checkpoint json/png, launch-*.json) and --stale-days (default 1)
#   rg --basename does not exist; the sweep is fixed-string basename
#   hardcoded scratch sizes and prunable-worktree counts in SKILL.md are
#   measurements, not a contract — remeasure, do not trust 553M / 19 / 5
#
# CLI
#   tools/impl-35.sh [--root DIR] [--include-root] [--compare PREV.tsv]
#   tools/impl-35.sh --drift [--skill FILE] [--tools DIR] [--scratch DIR] [--root DIR]
#   tools/impl-35.sh --classify DIR
#   tools/impl-35.sh --selftest
#
# Census TSV (header + one row per git work tree, paths sorted):
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
# Flags (stable order): clean, dirty, unpushed, no-remote, scratch,
#   scratch-symlink, secret-shaped, status-unverifiable, not-a-repo, error.
# "clean" is withheld when any hygiene signal is present, including
# scratch_bytes>0, a symlinked .scratch (not followed), secret-shaped
# names, or no remote-tracking ref. no-remote replaces a false unpushed
# proof: the unpushed column still counts local commits.
#
# --compare PREV.tsv
#   Diff TSV: repo  field  before  after  change
#   Exit 0 if header-only, 3 if any field differs, 2 if PREV is malformed.
#
# --drift
#   TSV: status  id  disposition  claim  observed
#   status is DRIFT or ALIGNED. Exit 0 if drift_count=0, else 3.
#   A hardcoded size is DRIFT when live du -sb differs by more than 5%
#   from both 1000^2 and 1024^2 interpretations.
#
# --classify DIR
#   Summary TSV. Every file is in exactly one partition:
#     secret-shaped (unread) | forbidden-skipped (unread) | unreadable | classified
#   Classified files are cross-tabulated by extension and by magic of at
#   most 200 bytes. Symlinks are counted and not followed. A missing path
#   or a symlink root is NOT-SAFE and exits 1 — it must not look like an
#   empty successful classification. Exit 0 only when accounted=yes.
#
# Exit codes: 0 evaluated clean; 1 selftest/evaluation failure; 2 usage;
#   3 compare differs or drift_count>0. No other codes.
#
# Env: SHOKUNIN_ROOT  default census root (parent of this repo).
# Git config is neutralized (GIT_CONFIG_GLOBAL=/dev/null) so the census
# does not depend on operator aliases or insteadOf rules.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_SYSTEM=/dev/null
export LC_ALL=C

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'
DIFF_HEADER=$'repo\tfield\tbefore\tafter\tchange'
DRIFT_HEADER=$'status\tid\tdisposition\tclaim\tobserved'

ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
COMPARE=""
INCLUDE_ROOT=0
SELFTEST=0
MODE=census
SKILL_FILE=""
TOOLS_DIR=""
SCRATCH_DIR=""
CLASSIFY_DIR=""
CLEAN_TMP=""

usage() {
  sed -n '2,58p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}
usage_err() {
  [ -n "$CLEAN_TMP" ] && rm -f -- "$CLEAN_TMP"
  printf 'impl-35: %s\n' "$1" >&2
  usage 2
}

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

is_secret_component() {
  local lc=${1,,}
  case "$lc" in
    *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem) return 0 ;;
  esac
  return 1
}

is_secret_relpath() {
  local comp
  local IFS='/'
  set -f
  for comp in $1; do
    if is_secret_component "$comp"; then set +f; return 0; fi
  done
  set +f
  return 1
}

is_forbidden_relpath() {
  case "$1" in
    .ufo/state|.ufo/state/*|.ufo/watchdog.log) return 0 ;;
  esac
  return 1
}

sanitize_field() {
  local s=$1
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

count_worktrees() {
  local n
  n=$(git -C "$1" worktree list 2>/dev/null | grep -c . || true)
  printf '%s' "${n// /}"
}

count_unpushed() { # prints count<TAB>no-remote|has-remote
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

count_dirty() {
  local st
  if ! st=$(git -C "$1" status --porcelain --untracked-files=all 2>/dev/null); then
    printf 'unverifiable'
    return 0
  fi
  if [ -z "$st" ]; then printf '0'; return 0; fi
  printf '%s' "$(printf '%s\n' "$st" | grep -c . || true)"
}

scratch_bytes() { # $1 repo; prints bytes<TAB>ok|absent|symlink|error
  local d="$1/.scratch"
  if [ ! -e "$d" ] && [ ! -L "$d" ]; then printf '0\tabsent'; return 0; fi
  if [ -L "$d" ]; then printf '0\tsymlink'; return 0; fi
  if [ ! -d "$d" ]; then printf '0\terror'; return 0; fi
  local line bytes
  line=$(du -sb -P -- "$d" 2>/dev/null | head -1 || true)
  bytes=${line%%[[:space:]]*}
  case "$bytes" in
    ''|*[!0-9]*) printf '0\terror' ;;
    *) printf '%s\tok' "$bytes" ;;
  esac
}

newest_mtime() { # prints iso<TAB>secret-shaped|ok
  local repo=$1
  local newest=0 saw_secret=0 rec epoch_raw epoch rel iso
  while IFS= read -r -d '' rec; do
    epoch_raw=${rec%%$'\t'*}
    rel=${rec#*$'\t'}
    [ -n "$rel" ] || continue
    if is_forbidden_relpath "$rel"; then continue; fi
    if is_secret_relpath "$rel"; then saw_secret=1; continue; fi
    epoch=${epoch_raw%%.*}
    case "$epoch" in
      ''|*[!0-9]*) continue ;;
    esac
    if [ "$epoch" -gt "$newest" ]; then newest=$epoch; fi
  done < <(cd -- "$repo" && find . \
      \( -name .git -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \) -prune \
      -o -type f -printf '%T@\t%P\0' 2>/dev/null || true)
  if [ "$newest" -eq 0 ]; then
    iso=""
  else
    iso=$(date -d "@$newest" --iso-8601=seconds 2>/dev/null || true)
  fi
  if [ "$saw_secret" = 1 ]; then
    printf '%s\tsecret-shaped' "$iso"
  else
    printf '%s\tok' "$iso"
  fi
}

census_one() {
  local repo
  repo=$(canon_path "$1")
  if [ ! -e "$repo/.git" ]; then
    printf '%s\t0\t0\t0\t0\t\tnot-a-repo\n' "$(sanitize_field "$repo")"
    return 0
  fi
  if ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '%s\t0\t0\t0\t0\t\terror\n' "$(sanitize_field "$repo")"
    return 0
  fi

  local wt unp_line unp remote_flag dirty scratch_line scratch scratch_kind
  local mt_line iso secret_flag
  wt=$(count_worktrees "$repo")
  unp_line=$(count_unpushed "$repo")
  unp=${unp_line%%$'\t'*}
  remote_flag=${unp_line#*$'\t'}
  dirty=$(count_dirty "$repo")
  scratch_line=$(scratch_bytes "$repo")
  scratch=${scratch_line%%$'\t'*}
  scratch_kind=${scratch_line#*$'\t'}
  mt_line=$(newest_mtime "$repo")
  iso=${mt_line%%$'\t'*}
  secret_flag=${mt_line#*$'\t'}

  local flagset=" "
  add_flag() {
    case "$flagset" in
      *" $1 "*) ;;
      *) flagset+="$1 " ;;
    esac
  }

  case "$wt" in ''|*[!0-9]*) wt=0; add_flag error ;; esac
  case "$unp" in ''|*[!0-9]*) unp=0; add_flag error ;; esac
  case "$scratch" in ''|*[!0-9]*) scratch=0; add_flag error ;; esac

  if [ "$remote_flag" = no-remote ]; then add_flag no-remote; fi
  if [ "${unp:-0}" -gt 0 ] && [ "$remote_flag" != no-remote ]; then
    add_flag unpushed
  fi
  if [ "$dirty" = unverifiable ]; then
    dirty=0
    add_flag status-unverifiable
  elif [ "${dirty:-0}" -gt 0 ]; then
    add_flag dirty
  fi
  if [ "$scratch_kind" = symlink ]; then add_flag scratch-symlink; fi
  if [ "$scratch_kind" = error ]; then add_flag error; fi
  if [ "${scratch:-0}" -gt 0 ]; then add_flag scratch; fi
  if [ "$secret_flag" = secret-shaped ]; then add_flag secret-shaped; fi

  local has_problem=0 name
  for name in dirty unpushed no-remote scratch scratch-symlink secret-shaped status-unverifiable not-a-repo error; do
    case "$flagset" in
      *" $name "*) has_problem=1 ;;
    esac
  done
  if [ "$has_problem" = 0 ]; then add_flag clean; fi

  local ordered="" 
  for name in clean dirty unpushed no-remote scratch scratch-symlink secret-shaped status-unverifiable not-a-repo error; do
    case "$flagset" in
      *" $name "*)
        if [ -z "$ordered" ]; then ordered=$name; else ordered="$ordered,$name"; fi
        ;;
    esac
  done

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(sanitize_field "$repo")" "$wt" "$unp" "$dirty" "$scratch" \
    "$(sanitize_field "$iso")" "$(sanitize_field "$ordered")"
}

list_repos() {
  local root=$1 d base
  local -a found=()
  if [ "$INCLUDE_ROOT" = 1 ] && [ -d "$root" ] && [ -e "$root/.git" ]; then
    found+=("$root")
  fi
  shopt -s nullglob
  for d in "$root"/*/; do
    [ -d "$d" ] || continue
    base=$(basename -- "$d")
    case "$base" in
      .*) continue ;;
    esac
    if [ -e "${d%/}/.git" ]; then
      found+=("${d%/}")
    fi
  done
  shopt -u nullglob
  if [ "${#found[@]}" -eq 0 ]; then return 0; fi
  local p
  for p in "${found[@]}"; do printf '%s\n' "$p"; done | sort
}

emit_census() {
  local root
  root=$(canon_path "$ROOT")
  [ -d "$root" ] || { printf 'impl-35: root is not a directory: %s\n' "$root" >&2; exit 1; }
  printf '%s\n' "$HEADER"
  local repo
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    census_one "$repo"
  done < <(list_repos "$root")
}

load_census() { # $1 file, $2 nameref
  local file=$1
  local -n _map=$2
  [ -f "$file" ] || usage_err "compare file not found: $file"
  local line n=0 repo rest
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    if [ "$n" = 1 ]; then
      [ "$line" = "$HEADER" ] || usage_err "compare file header mismatch (want 7 census columns)"
      continue
    fi
    repo=${line%%$'\t'*}
    rest=${line#*$'\t'}
    [ -n "$repo" ] || usage_err "compare file: empty repo on line $n"
    if [ -n "${_map[$repo]+x}" ]; then
      usage_err "compare file: duplicate repo $repo"
    fi
    _map["$repo"]=$rest
  done < "$file"
}

field_at() {
  local rest=$1 idx=$2 i=1 part
  while [ "$i" -le 6 ]; do
    if [ "$i" -eq 6 ]; then part=$rest; else part=${rest%%$'\t'*}; rest=${rest#*$'\t'}; fi
    if [ "$i" -eq "$idx" ]; then printf '%s' "$part"; return 0; fi
    i=$((i + 1))
  done
}

numeric_change() {
  local b=$1 a=$2
  case "$b" in ''|*[!0-9-]*) printf 'non-numeric'; return 0 ;; esac
  case "$a" in ''|*[!0-9-]*) printf 'non-numeric'; return 0 ;; esac
  local d=$((a - b))
  if [ "$d" -gt 0 ]; then printf '+%s' "$d"
  elif [ "$d" -lt 0 ]; then printf '%s' "$d"
  else printf '0'; fi
}

emit_compare() {
  local -A before=() after=()
  load_census "$COMPARE" before
  local tmp
  tmp=$(mktemp "${TMPDIR:-/tmp}/impl-35-census.XXXXXX")
  CLEAN_TMP=$tmp
  emit_census > "$tmp"
  load_census "$tmp" after
  rm -f -- "$tmp"
  CLEAN_TMP=""

  printf '%s\n' "$DIFF_HEADER"
  local changes=0 repo rest_b rest_a
  local -a repos=()
  for repo in "${!before[@]}"; do repos+=("$repo"); done
  for repo in "${!after[@]}"; do
    if [ -z "${before[$repo]+x}" ]; then repos+=("$repo"); fi
  done
  local sorted name i before_v after_v chg
  local -a names=(worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)
  sorted=$(printf '%s\n' "${repos[@]}" | sort -u)
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

# --- drift -------------------------------------------------------------------

drift_row() { # status id disposition claim observed
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$(sanitize_field "$4")" "$(sanitize_field "$5")"
  if [ "$1" = DRIFT ]; then DRIFT_N=$((DRIFT_N + 1)); else DRIFT_ALIGNED=$((DRIFT_ALIGNED + 1)); fi
}

file_has() { # $1 file $2 fixed string (case-sensitive)
  [ -f "$1" ] || return 1
  grep -F -q -- "$2" "$1"
}

tools_have_ci() { # $1 fixed string, case-insensitive, any tool file
  local f
  for f in "$TOOLS_DIR/souji-verify.sh" "$TOOLS_DIR/souji-vault-verify.sh"; do
    [ -f "$f" ] || continue
    if grep -F -i -q -- "$1" "$f"; then return 0; fi
  done
  return 1
}

run_drift() {
  local skill=${SKILL_FILE:-$REPO_ROOT/SKILL.md}
  local tools=${TOOLS_DIR:-$SCRIPT_DIR}
  TOOLS_DIR=$tools
  [ -f "$skill" ] || usage_err "skill file not found: $skill"
  [ -d "$tools" ] || usage_err "tools dir not found: $tools"
  DRIFT_N=0
  DRIFT_ALIGNED=0
  printf '%s\n' "$DRIFT_HEADER"

  local fetch_seq='git ''fetch'
  local skill_fetch=0 tool_forbids=0
  if grep -F -q -- "$fetch_seq" "$skill"; then skill_fetch=1; fi
  if tools_have_ci "no git fetch"; then tool_forbids=1; fi
  if [ "$skill_fetch" = 1 ] && [ "$tool_forbids" = 1 ]; then
    drift_row DRIFT SKILL-FETCH doc-behind-tool \
      "skill receipt command contains fetch; tools forbid fetch" \
      "skill_fetch=1 tool_forbids_fetch=1"
  elif [ "$skill_fetch" = 1 ] && [ "$tool_forbids" = 0 ]; then
    drift_row DRIFT SKILL-FETCH tool-missing-prohibition \
      "skill contains fetch and tools do not forbid it" \
      "skill_fetch=1 tool_forbids_fetch=0"
  else
    drift_row ALIGNED SKILL-FETCH reconciled \
      "skill does not require fetch" \
      "skill_fetch=$skill_fetch tool_forbids_fetch=$tool_forbids"
  fi

  local skill_mp=0 tool_mp=0
  if grep -F -q -- 'metadata-prune' "$skill"; then skill_mp=1; fi
  if tools_have_ci 'metadata-prune'; then tool_mp=1; fi
  if [ "$tool_mp" = 1 ] && [ "$skill_mp" = 0 ]; then
    drift_row DRIFT SKILL-METADATA-PRUNE doc-behind-tool \
      "tools emit metadata-prune; skill receipt table omits it" \
      "skill=0 tools=1"
  else
    drift_row ALIGNED SKILL-METADATA-PRUNE reconciled \
      "metadata-prune presence matches" \
      "skill=$skill_mp tools=$tool_mp"
  fi

  local skill_tmp=0 tool_tmp=0
  if grep -F -q -- '*.tmp' "$skill"; then skill_tmp=1; fi
  if tools_have_ci '*.tmp'; then tool_tmp=1; fi
  if [ "$skill_tmp" = 1 ] && [ "$tool_tmp" = 0 ]; then
    drift_row DRIFT SKILL-STALE-TMP doc-ahead-of-tool \
      "skill lists *.tmp as scratch; tools do not; do not widen SAFE" \
      "skill_tmp=1 tool_tmp=0"
  else
    drift_row ALIGNED SKILL-STALE-TMP reconciled \
      "stale *.tmp token agreement" \
      "skill_tmp=$skill_tmp tool_tmp=$tool_tmp"
  fi

  local skill_clock=0 tool_clock=0
  if grep -F -q -- 'last admitted round' "$skill"; then skill_clock=1; fi
  if tools_have_ci 'stale-days'; then tool_clock=1; fi
  if [ "$skill_clock" = 1 ] && [ "$tool_clock" = 1 ]; then
    drift_row DRIFT SKILL-STALE-CLOCK doc-ahead-of-tool \
      "skill ages stale by last admitted round; tools use --stale-days" \
      "skill_round_clock=1 tool_stale_days=1"
  else
    drift_row ALIGNED SKILL-STALE-CLOCK reconciled \
      "stale clock tokens do not disagree" \
      "skill_round_clock=$skill_clock tool_stale_days=$tool_clock"
  fi

  local skill_main=0 tool_head=0
  if grep -F -q -- 'origin/main' "$skill"; then skill_main=1; fi
  if tools_have_ci 'origin/HEAD'; then tool_head=1; fi
  if [ "$skill_main" = 1 ] && [ "$tool_head" = 1 ]; then
    drift_row DRIFT SKILL-ORIGIN-MAIN doc-behind-tool \
      "skill hardcodes origin/main; tools resolve origin/HEAD" \
      "skill_origin_main=1 tool_origin_HEAD=1"
  else
    drift_row ALIGNED SKILL-ORIGIN-MAIN reconciled \
      "default-branch token agreement" \
      "skill_origin_main=$skill_main tool_origin_HEAD=$tool_head"
  fi

  local spec="$TOOLS_DIR/souji-verify.spec.md"
  local basename_hit=0
  if grep -F -q -- '--basename' "$skill"; then basename_hit=1; fi
  if [ -f "$spec" ] && grep -F -q -- '--basename' "$spec"; then basename_hit=1; fi
  if [ "$basename_hit" = 1 ]; then
    local rg_err rg_st
    set +e
    rg_err=$(rg --basename </dev/null 2>&1)
    rg_st=$?
    set -e
    if [ "$rg_st" != 0 ]; then
      drift_row DRIFT SPEC-BASENAME doc-behind-tool \
        "docs cite rg --basename; installed rg rejects that flag" \
        "rg_exit=$rg_st ${rg_err%%$'\n'*}"
    else
      drift_row ALIGNED SPEC-BASENAME reconciled \
        "docs cite --basename and rg accepts it" \
        "rg_exit=0"
    fi
  else
    drift_row ALIGNED SPEC-BASENAME reconciled \
      "docs do not cite rg --basename" \
      "basename_flag=absent"
  fi

  local size_claim=""
  size_claim=$(grep -o -E '[0-9]+M `\.scratch/`' "$skill" | head -1 || true)
  if [ -z "$size_claim" ]; then
    size_claim=$(grep -o -E '[0-9]+M \.scratch/' "$skill" | head -1 || true)
  fi
  if [ -n "$size_claim" ]; then
    local claimed_m scratch live
    claimed_m=${size_claim%%M*}
    scratch=${SCRATCH_DIR:-$ROOT/kotodama-shokunin/.scratch}
    if [ ! -d "$scratch" ] || [ -L "$scratch" ]; then
      drift_row DRIFT SKILL-SCRATCH-SIZE doc-stale-measurement \
        "skill hardcodes ${claimed_m}M .scratch; live path unavailable" \
        "claimed_m=$claimed_m path=$(sanitize_field "$scratch") state=absent-or-symlink"
    else
      live=$(du -sb -P -- "$scratch" 2>/dev/null | awk '{print $1; exit}')
      case "$live" in
        ''|*[!0-9]*)
          drift_row DRIFT SKILL-SCRATCH-SIZE doc-stale-measurement \
            "skill hardcodes ${claimed_m}M .scratch; du failed" \
            "claimed_m=$claimed_m du=failed"
          ;;
        *)
          local si=$((claimed_m * 1000 * 1000)) iec=$((claimed_m * 1024 * 1024))
          local ok=0
          # within 5% of either interpretation
          local dsi diec
          dsi=$((live > si ? live - si : si - live))
          diec=$((live > iec ? live - iec : iec - live))
          if [ $((dsi * 20)) -le "$si" ] || [ $((diec * 20)) -le "$iec" ]; then ok=1; fi
          if [ "$ok" = 1 ]; then
            drift_row ALIGNED SKILL-SCRATCH-SIZE reconciled \
              "hardcoded scratch size within 5% of live du -sb" \
              "claimed_m=$claimed_m live_bytes=$live"
          else
            drift_row DRIFT SKILL-SCRATCH-SIZE doc-stale-measurement \
              "skill hardcodes ${claimed_m}M .scratch; live du -sb disagrees by >5%" \
              "claimed_m=$claimed_m si=$si iec=$iec live_bytes=$live path=$(sanitize_field "$scratch")"
          fi
          ;;
      esac
    fi
  else
    drift_row ALIGNED SKILL-SCRATCH-SIZE reconciled \
      "skill does not hardcode a scratch mebibyte/megabyte size" \
      "hardcoded_size=absent"
  fi

  local wt_lines wt_n=0
  wt_lines=$(grep -E '^[-*][[:space:]]*[^:]+:[[:space:]]*[0-9]+[[:space:]]+prunable worktrees' "$skill" || true)
  if [ -z "$wt_lines" ]; then
    drift_row ALIGNED SKILL-WORKTREES reconciled \
      "skill does not hardcode a prunable-worktree count" \
      "hardcoded_counts=absent"
  else
    local line name claimed repo prunable total
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      wt_n=$((wt_n + 1))
      name=$(printf '%s\n' "$line" | sed -E 's/^[-*][[:space:]]*([^:]+):.*/\1/')
      claimed=$(printf '%s\n' "$line" | sed -E 's/.*:[[:space:]]*([0-9]+)[[:space:]]+prunable worktrees.*/\1/')
      repo="$ROOT/$name"
      if [ ! -e "$repo/.git" ]; then
        drift_row DRIFT "SKILL-WT-$name" doc-stale-measurement \
          "skill claims $claimed prunable worktrees" \
          "repo=absent claimed=$claimed"
        continue
      fi
      prunable=$(git -C "$repo" worktree list 2>/dev/null | grep -c 'prunable' || true)
      total=$(git -C "$repo" worktree list 2>/dev/null | grep -c . || true)
      prunable=${prunable// /}
      total=${total// /}
      if [ "$prunable" = "$claimed" ]; then
        drift_row ALIGNED "SKILL-WT-$name" reconciled \
          "prunable count matches live git worktree list" \
          "claimed=$claimed prunable=$prunable worktree_lines=$total"
      else
        drift_row DRIFT "SKILL-WT-$name" doc-stale-measurement \
          "skill claims $claimed prunable; live git worktree list disagrees" \
          "claimed=$claimed prunable=$prunable worktree_lines=$total"
      fi
    done <<< "$wt_lines"
  fi

  printf 'SUMMARY\tdrift_count\t%s\taligned\t%s\n' "$DRIFT_N" "$DRIFT_ALIGNED"
  if [ "$DRIFT_N" -gt 0 ]; then return 3; fi
  return 0
}

# --- classify ----------------------------------------------------------------

run_classify() {
  local target=$1
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    printf 'NOT-SAFE\tunreachable\t%s\n' "$(sanitize_field "$target")"
    return 1
  fi
  if [ -L "$target" ]; then
    printf 'NOT-SAFE\tsymlink-root\t%s\n' "$(sanitize_field "$target")"
    return 1
  fi
  if [ ! -d "$target" ]; then
    printf 'NOT-SAFE\tnot-a-directory\t%s\n' "$(sanitize_field "$target")"
    return 1
  fi
  python3 - "$target" <<'PY'
import os, sys
from collections import Counter

root = os.path.abspath(sys.argv[1])
MAX = 200

def secret_component(name: str) -> bool:
    lc = name.lower()
    if lc == ".env" or lc == ".envrc" or lc.startswith(".env.") or lc.endswith(".env"):
        return True
    if "credential" in lc or "secret" in lc:
        return True
    if lc.startswith("id_") or lc.endswith(".pem"):
        return True
    return False

def secret_rel(rel: str) -> bool:
    return any(secret_component(p) for p in rel.split("/") if p)

def forbidden_rel(rel: str) -> bool:
    return rel == ".ufo/state" or rel.startswith(".ufo/state/") or rel == ".ufo/watchdog.log"

def magic_of(buf: bytes) -> str:
    if not buf:
        return "empty"
    if buf.startswith(b"%PDF"):
        return "pdf"
    if buf.startswith(b"\x89PNG"):
        return "png"
    if buf.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if buf.startswith(b"GIF8"):
        return "gif"
    if buf.startswith(b"PK\x03\x04") or buf.startswith(b"PK\x05\x06"):
        return "zip"
    if buf.startswith(b"\x1f\x8b"):
        return "gzip"
    if buf.startswith(b"PACK"):
        return "git-pack"
    if buf.startswith(b"\x7fELF"):
        return "elf"
    if buf.startswith(b"#!"):
        return "shebang"
    if b"\x00" in buf[:80]:
        return "binary"
    stripped = buf.lstrip()
    if stripped.startswith(b"{") or stripped.startswith(b"["):
        return "json-text"
    if stripped.startswith(b"---") or stripped.startswith(b"%YAML"):
        return "yaml-text"
    if stripped.startswith(b"#"):
        return "hash-text"
    return "text"

def ext_of(name: str) -> str:
    lc = name.lower()
    dot = lc.rfind(".")
    if dot <= 0:
        return "(none)"
    return lc[dot:]

ext_n, ext_b = Counter(), Counter()
mag_n, mag_b = Counter(), Counter()
top_n, top_b, top_sec = Counter(), Counter(), Counter()
secret_names = Counter()

entries = dirs = files = symlinks = other = vanished = stat_errors = 0
secret_files = secret_bytes = secret_bytes_read = 0
forbidden_files = unreadable = classified = 0
file_bytes = 0
max_read = 0
header_reads = 0
seen_ino = set()
unique_bytes = 0

def top_key(rel: str) -> str:
    if "/" not in rel:
        return "(root)"
    return rel.split("/", 1)[0]

stack = [root]
while stack:
    d = stack.pop()
    try:
        it = os.scandir(d)
    except OSError:
        stat_errors += 1
        continue
    with it:
        batch = list(it)
    for e in batch:
        entries += 1
        name = e.name
        rel = os.path.relpath(e.path, root)
        try:
            is_link = e.is_symlink()
        except OSError:
            vanished += 1
            continue
        if is_link:
            symlinks += 1
            top_n[top_key(rel)] += 0  # keep key only if we later add files
            continue
        try:
            is_dir = e.is_dir(follow_symlinks=False)
        except OSError:
            vanished += 1
            continue
        if is_dir:
            dirs += 1
            stack.append(e.path)
            continue
        try:
            is_file = e.is_file(follow_symlinks=False)
        except OSError:
            vanished += 1
            continue
        if not is_file:
            other += 1
            continue
        files += 1
        tk = top_key(rel)
        if forbidden_rel(rel):
            forbidden_files += 1
            top_n[tk] += 1
            continue
        if secret_rel(rel):
            secret_files += 1
            secret_names[name] += 1
            top_sec[tk] += 1
            top_n[tk] += 1
            try:
                st = e.stat(follow_symlinks=False)
                secret_bytes += st.st_size
                top_b[tk] += st.st_size
                file_bytes += st.st_size
            except OSError:
                stat_errors += 1
            continue
        try:
            st = e.stat(follow_symlinks=False)
        except OSError:
            unreadable += 1
            vanished += 1
            top_n[tk] += 1
            continue
        size = st.st_size
        file_bytes += size
        top_b[tk] += size
        top_n[tk] += 1
        ino = (st.st_dev, st.st_ino)
        if ino not in seen_ino:
            seen_ino.add(ino)
            unique_bytes += size
        ext = ext_of(name)
        buf = b""
        try:
            with open(e.path, "rb") as fh:
                buf = fh.read(MAX)
            nread = len(buf)
            if nread > MAX:
                print("impl-35: read exceeded 200 bytes", file=sys.stderr)
                sys.exit(1)
            if nread > max_read:
                max_read = nread
            header_reads += 1
        except OSError:
            unreadable += 1
            continue
        classified += 1
        mag = magic_of(buf)
        ext_n[ext] += 1
        ext_b[ext] += size
        mag_n[mag] += 1
        mag_b[mag] += size

accounted_files = secret_files + forbidden_files + unreadable + classified
# unreadable files that vanished before stat were also added to vanished;
# they are in `files` only when is_file succeeded. Rebuild the equation
# from the counters that increment `files`.
# files increments, then exactly one of: forbidden, secret, unreadable
# (stat fail), unreadable (open fail), classified.
# open-fail increments unreadable and does not increment classified.
# stat-fail increments unreadable and vanished.
ok = accounted_files == files

def emit(line: str) -> None:
    sys.stdout.buffer.write(line.encode("utf-8", "backslashreplace") + b"\n")

emit("IMPL35\tclassify\t1")
emit(f"root\t{root}")
emit(f"entries\t{entries}")
emit(f"dirs\t{dirs}")
emit(f"files\t{files}")
emit(f"symlinks\t{symlinks}")
emit(f"other\t{other}")
emit(f"vanished\t{vanished}")
emit(f"stat_errors\t{stat_errors}")
emit(f"secret_shaped_files\t{secret_files}")
emit(f"secret_shaped_bytes\t{secret_bytes}")
emit(f"secret_bytes_read\t{secret_bytes_read}")
emit(f"forbidden_skipped_files\t{forbidden_files}")
emit(f"unreadable_files\t{unreadable}")
emit(f"classified_files\t{classified}")
emit(f"file_bytes_sum\t{file_bytes}")
emit(f"unique_file_inodes\t{len(seen_ino)}")
emit(f"unique_file_bytes\t{unique_bytes}")
emit(f"max_bytes_read_per_file\t{max_read}")
emit(f"header_reads\t{header_reads}")
emit(f"accounted_files\t{accounted_files}")
emit("accounted\t" + ("yes" if ok else "no"))
for name, k in sorted(secret_names.items()):
    emit(f"SECRET_NAME\t{name}\t{k}")
for ext in sorted(ext_n):
    emit(f"CLASS\text\t{ext}\t{ext_n[ext]}\t{ext_b[ext]}")
for mag in sorted(mag_n):
    emit(f"CLASS\tmagic\t{mag}\t{mag_n[mag]}\t{mag_b[mag]}")
for key in sorted(set(list(top_n) + list(top_b) + list(top_sec))):
    emit(f"TOP\t{key}\t{top_n[key]}\t{top_b[key]}\t{top_sec[key]}")
sys.exit(0 if ok else 1)
PY
}

# --- selftest ----------------------------------------------------------------

ST_PASS=0
ST_FAIL=0
ST_TMP=""
st_note() { printf '%s\n' "$*"; }
st_ok() { ST_PASS=$((ST_PASS + 1)); st_note "PASS $*"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $*"; }

st_commit() {
  local repo=$1 parent=$2 msg=$3 tr sha
  git -C "$repo" add -A >/dev/null
  tr=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr")
  fi
  printf '%s' "$sha"
}

st_init() {
  git init -q --initial-branch="$2" "$1"
  git -C "$1" symbolic-ref HEAD "refs/heads/$2"
}

st_row_field() {
  local tsv=$1 base=$2 col=$3 line i=1 rest part
  line=$(grep -F "/$base"$'\t' "$tsv" | head -1 || true)
  [ -n "$line" ] || { printf ''; return 0; }
  rest=$line
  while [ "$i" -le 7 ]; do
    if [ "$i" -eq 7 ]; then part=$rest; else part=${rest%%$'\t'*}; rest=${rest#*$'\t'}; fi
    if [ "$i" -eq "$col" ]; then printf '%s' "$part"; return 0; fi
    i=$((i + 1))
  done
}

run_selftest() {
  if [ "${SOUJI_IMPL35_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'impl-35: refusing nested --selftest\n' >&2
    exit 1
  fi
  export GIT_AUTHOR_NAME=souji-selftest
  export GIT_AUTHOR_EMAIL=souji@shokunin.local
  export GIT_COMMITTER_NAME=souji-selftest
  export GIT_COMMITTER_EMAIL=souji@shokunin.local
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/impl-35-selftest.XXXXXX")
  trap 'rm -rf -- "$ST_TMP"' EXIT
  local fleet="$ST_TMP/fleet"
  mkdir -p "$fleet"

  local RC="$fleet/clean-shokunin"
  st_init "$RC" master
  printf '%s\n' '.ufo/' > "$RC/.gitignore"
  printf 'kept\n' > "$RC/kept.txt"
  local c1
  c1=$(st_commit "$RC" "" "c1 kept")
  git -C "$RC" update-ref refs/heads/master "$c1"
  git -C "$RC" update-ref refs/remotes/origin/master "$c1"
  git -C "$RC" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  mkdir -p "$RC/.ufo/state"
  printf 'watchdog-secret\n' > "$RC/.ufo/watchdog.log"
  printf 'state-secret\n' > "$RC/.ufo/state/live.json"

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
  printf 'SUPER-SECRET-TOKEN-do-not-print\n' > "$RD/.scratch/credentials.env"

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
  local WT="$fleet/unpushed-shokunin-wt"
  mkdir -p "$RU/.git/worktrees/wt1"
  printf 'ref: refs/heads/master\n' > "$RU/.git/worktrees/wt1/HEAD"
  printf '../..\n' > "$RU/.git/worktrees/wt1/commondir"
  printf '%s\n' "$WT/.git" > "$RU/.git/worktrees/wt1/gitdir"
  mkdir -p "$WT"
  printf 'gitdir: %s\n' "$RU/.git/worktrees/wt1" > "$WT/.git"
  printf 'wt\n' > "$WT/from-wt.txt"

  local RN="$fleet/noremote-shokunin"
  st_init "$RN" master
  printf 'solo\n' > "$RN/solo.txt"
  local n1
  n1=$(st_commit "$RN" "" "n1")
  git -C "$RN" update-ref refs/heads/master "$n1"

  mkdir -p "$fleet/plain-dir"
  printf 'nope\n' > "$fleet/plain-dir/x.txt"
  mkdir -p "$fleet/.hidden-shokunin"
  st_init "$fleet/.hidden-shokunin" master

  # symlinked .scratch must not be followed and must not count as clean
  local RS="$fleet/symlink-scratch-shokunin"
  st_init "$RS" master
  printf 's\n' > "$RS/s.txt"
  local s1
  s1=$(st_commit "$RS" "" "s1")
  git -C "$RS" update-ref refs/heads/master "$s1"
  git -C "$RS" update-ref refs/remotes/origin/master "$s1"
  mkdir -p "$ST_TMP/hidden-scratch"
  printf 'SYMLINK-SCRATCH-TOKEN-do-not-print\n' > "$ST_TMP/hidden-scratch/payload.txt"
  ln -s "$ST_TMP/hidden-scratch" "$RS/.scratch"

  local out1="$ST_TMP/c1.tsv" out2="$ST_TMP/c2.tsv"
  env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" > "$out1"
  env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" > "$out2"
  if cmp -s "$out1" "$out2"; then st_ok "census repeat byte-identical"
  else st_bad "census repeat differs"; diff -u "$out1" "$out2" || true; fi

  local hdr
  hdr=$(head -1 "$out1")
  if [ "$hdr" = "$HEADER" ]; then st_ok "census header"
  else st_bad "census header '$hdr'"; fi

  local data_rows
  data_rows=$(( $(grep -c $'\t' "$out1" || true) - 1 ))
  # clean dirty noremote unpushed unpushed-wt symlink-scratch = 6
  if [ "$data_rows" = 6 ]; then st_ok "row count 6"
  else st_bad "row count $data_rows want 6"; cat "$out1"; fi
  if grep -q 'plain-dir' "$out1"; then st_bad "plain-dir included"; else st_ok "plain-dir skipped"; fi
  if grep -q 'hidden-shokunin' "$out1"; then st_bad "dot-dir included"; else st_ok "dot-dir skipped"; fi

  local v
  v=$(st_row_field "$out1" clean-shokunin 7)
  case "$v" in
    clean) st_ok "clean verdict ($v)" ;;
    *) st_bad "clean verdict '$v'"; grep clean-shokunin "$out1" || true ;;
  esac
  v=$(st_row_field "$out1" clean-shokunin 3)
  if [ "$v" = 0 ]; then st_ok "clean unpushed=0"; else st_bad "clean unpushed=$v"; fi
  v=$(st_row_field "$out1" clean-shokunin 4)
  if [ "$v" = 0 ]; then st_ok "clean dirty=0"; else st_bad "clean dirty=$v"; fi

  v=$(st_row_field "$out1" dirty-shokunin 4)
  if [ "$v" = 3 ]; then st_ok "dirty count=3"; else st_bad "dirty count=$v want 3"; fi
  v=$(st_row_field "$out1" dirty-shokunin 5)
  if [ "${v:-0}" -gt 0 ]; then st_ok "dirty scratch_bytes=$v"; else st_bad "dirty scratch_bytes=$v"; fi
  v=$(st_row_field "$out1" dirty-shokunin 7)
  case "$v" in
    *dirty*scratch*secret-shaped*) st_ok "dirty flags ($v)" ;;
    *) st_bad "dirty flags '$v'" ;;
  esac
  case "$v" in
    clean*) st_bad "dirty repo marked clean"; ;;
    *) st_ok "dirty repo not marked clean" ;;
  esac

  v=$(st_row_field "$out1" unpushed-shokunin 3)
  if [ "$v" = 1 ]; then st_ok "unpushed count=1"; else st_bad "unpushed count=$v"; fi
  v=$(st_row_field "$out1" unpushed-shokunin 2)
  if [ "$v" = 2 ]; then st_ok "unpushed worktrees=2"; else st_bad "unpushed worktrees=$v"; fi

  v=$(st_row_field "$out1" noremote-shokunin 7)
  case "$v" in
    *no-remote*) st_ok "noremote flag ($v)" ;;
    *) st_bad "noremote flags '$v'" ;;
  esac
  case "$v" in
    clean*) st_bad "noremote marked clean" ;;
    *) st_ok "noremote not clean" ;;
  esac

  v=$(st_row_field "$out1" symlink-scratch-shokunin 7)
  case "$v" in
    *scratch-symlink*) st_ok "scratch-symlink flagged ($v)" ;;
    *) st_bad "scratch-symlink flags '$v'" ;;
  esac
  v=$(st_row_field "$out1" symlink-scratch-shokunin 5)
  if [ "$v" = 0 ]; then st_ok "symlink scratch_bytes=0 (not followed)"
  else st_bad "symlink scratch_bytes=$v (followed?)"; fi
  case "$(st_row_field "$out1" symlink-scratch-shokunin 7)" in
    clean*) st_bad "symlink scratch marked clean" ;;
    *) st_ok "symlink scratch not clean" ;;
  esac

  if grep -q 'SUPER-SECRET-TOKEN' "$out1"; then st_bad "secret contents leaked"
  else st_ok "secret contents absent"; fi
  if grep -q 'SYMLINK-SCRATCH-TOKEN' "$out1"; then st_bad "symlink target contents leaked"
  else st_ok "symlink target contents absent"; fi
  if grep -q 'watchdog-secret' "$out1" || grep -q 'state-secret' "$out1"; then
    st_bad "forbidden surface contents leaked"
  else st_ok "forbidden surface contents absent"; fi

  v=$(st_row_field "$out1" clean-shokunin 6)
  case "$v" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T*) st_ok "mtime_iso shape" ;;
    *) st_bad "mtime_iso '$v'" ;;
  esac

  local cmp_out cmp_st
  set +e
  cmp_out=$(env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$out1" 2>&1)
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 0 ] && [ "$cmp_out" = "$DIFF_HEADER" ]; then
    st_ok "compare identical exit 0"
  else
    st_bad "compare identical exit=$cmp_st"
  fi

  printf 'more\n' >> "$RD/.scratch/note.txt"
  rm -f -- "$RD/untracked.txt"
  local cmp2
  set +e
  cmp2=$(env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$out1" 2>&1)
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 3 ]; then st_ok "compare mutation exit 3"
  else st_bad "compare mutation exit=$cmp_st"; fi
  case "$cmp2" in
    *dirty-shokunin*$'\t'"scratch_bytes"$'\t'*) st_ok "compare reports scratch_bytes" ;;
    *) st_bad "compare missing scratch_bytes" ;;
  esac
  case "$cmp2" in
    *dirty-shokunin*$'\t'"dirty"$'\t'*) st_ok "compare reports dirty" ;;
    *) st_bad "compare missing dirty" ;;
  esac

  printf 'nope\n' > "$ST_TMP/bad.tsv"
  set +e
  env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$ST_TMP/bad.tsv" >/dev/null 2>&1
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 2 ]; then st_ok "bad compare header exits 2"
  else st_bad "bad compare header exit=$cmp_st"; fi

  set +e
  env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 "$SELF" --nope >/dev/null 2>&1
  cmp_st=$?
  set -e
  if [ "$cmp_st" = 2 ]; then st_ok "unknown flag exits 2"
  else st_bad "unknown flag exit=$cmp_st"; fi

  local n
  n=$(grep -nE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase|prune)( |$)' "$SELF" | wc -l || true)
  n=${n// /}
  if [ "${n:-1}" = 0 ]; then st_ok "no forbidden git subcommand"
  else st_bad "$n forbidden git invocation(s)"; grep -nE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase|prune)( |$)' "$SELF" || true; fi

  case "$fleet" in
    "$ST_TMP"/*) st_ok "fixtures under mktemp" ;;
    *) st_bad "fixtures not under mktemp" ;;
  esac

  # drift fixtures
  local TGOOD="$ST_TMP/tools-good" TBAD="$ST_TMP/tools-bad"
  mkdir -p "$TGOOD" "$TBAD"
  printf '%s\n' '# no git fetch' 'metadata-prune' 'origin/HEAD' '--stale-days 1' \
    > "$TGOOD/souji-verify.sh"
  printf '%s\n' '# aligned spec, no flag' > "$TGOOD/souji-verify.spec.md"
  cp "$TGOOD/souji-verify.sh" "$TBAD/souji-verify.sh"
  printf '%s\n' 'rg -l --no-ignore --basename <name>' > "$TBAD/souji-verify.spec.md"
  local SGOOD="$ST_TMP/skill-good.md" SBAD="$ST_TMP/skill-bad.md"
  cat > "$SGOOD" <<'EOF'
| pushed | existing remote-tracking refs only | merge-base origin/HEAD |
| metadata-prune | dir absent, unique commits 0 | git worktree list |
| stale | .scratch, *.out, *.log; age is --stale-days | --stale-days 1 |
EOF
  # Build the drifted skill without a contiguous fetch command in this source.
  local fetch_seq='git ''fetch'
  {
    printf '| pushed | after %s | %s -q && git merge-base --is-ancestor <commit> origin/main |\n' \
      "$fetch_seq" "$fetch_seq"
    printf '%s\n' '| stale | .scratch/, *.tmp, out/ | last admitted round |'
    printf '%s\n' '- demo-shokunin: 9 prunable worktrees (`git worktree list`).'
    printf '%s\n' 'kotodama 553M `.scratch/`'
  } > "$SBAD"
  st_init "$fleet/demo-shokunin" master
  printf 'd\n' > "$fleet/demo-shokunin/d.txt"
  local demo
  demo=$(st_commit "$fleet/demo-shokunin" "" "demo")
  git -C "$fleet/demo-shokunin" update-ref refs/heads/master "$demo"

  mkdir -p "$ST_TMP/scratch-live"
  printf 'x\n' > "$ST_TMP/scratch-live/a.txt"

  local dout dst
  set +e
  dout=$(env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --drift --skill "$SGOOD" --tools "$TGOOD" --root "$fleet" 2>&1)
  dst=$?
  set -e
  if [ "$dst" = 0 ] && printf '%s\n' "$dout" | grep -q $'SUMMARY\tdrift_count\t0\t'; then
    st_ok "aligned drift exit 0"
  else
    st_bad "aligned drift exit=$dst"
    printf '%s\n' "$dout" | head -20
  fi

  set +e
  dout=$(env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --drift --skill "$SBAD" --tools "$TBAD" --root "$fleet" \
    --scratch "$ST_TMP/scratch-live" 2>&1)
  dst=$?
  set -e
  if [ "$dst" = 3 ]; then st_ok "drift fixture exit 3"
  else st_bad "drift fixture exit=$dst"; fi
  local id
  for id in SKILL-FETCH SKILL-METADATA-PRUNE SKILL-STALE-TMP SKILL-STALE-CLOCK SKILL-ORIGIN-MAIN SPEC-BASENAME SKILL-SCRATCH-SIZE SKILL-WT-demo-shokunin; do
    if printf '%s\n' "$dout" | grep -q "^DRIFT	$id	"; then st_ok "drift id $id"
    else st_bad "missing drift id $id"; fi
  done

  # classify fixture
  local CD="$ST_TMP/class"
  mkdir -p "$CD/sub" "$CD/.ufo/state"
  printf 'hello\n' > "$CD/hello.txt"
  : > "$CD/empty.dat"
  {
    printf '%%PDF-1.4\n'
    # pad past 200 bytes then a tail that must not appear
    python3 - <<'PY'
import sys
sys.stdout.buffer.write(b"x" * 180)
sys.stdout.buffer.write(b"PDF-TAIL-LEAK-MUST-NOT-APPEAR")
PY
  } > "$CD/doc.pdf"
  python3 - <<PY
open("$CD/big.bin","wb").write(b"A"*200 + b"BIN-TAIL-LEAK-MUST-NOT-APPEAR")
PY
  printf '%s\n' '{"ok":true}' > "$CD/sub/data.json"
  printf '#!/bin/sh\necho hi\n' > "$CD/run.sh"
  printf 'LEAKED-SECRET-TOKEN\n' > "$CD/outside-secret.txt"
  ln -s "$CD/outside-secret.txt" "$CD/alias-secret"
  printf 'STATE-LEAK\n' > "$CD/.ufo/state/live.json"
  printf 'WATCH-LEAK\n' > "$CD/.ufo/watchdog.log"
  printf '# title\n' > "$CD/note.md"

  local c1out="$ST_TMP/class1.tsv" c2out="$ST_TMP/class2.tsv" cst
  set +e
  env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 "$SELF" --classify "$CD" > "$c1out"
  cst=$?
  env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 "$SELF" --classify "$CD" > "$c2out"
  set -e
  if [ "$cst" = 0 ]; then st_ok "classify exit 0"
  else st_bad "classify exit=$cst"; cat "$c1out"; fi
  if cmp -s "$c1out" "$c2out"; then st_ok "classify repeat byte-identical"
  else st_bad "classify repeat differs"; diff -u "$c1out" "$c2out" || true; fi
  if grep -q $'^accounted\tyes$' "$c1out"; then st_ok "classify accounted"
  else st_bad "classify not accounted"; fi
  if grep -q 'LEAKED-SECRET-TOKEN\|PDF-TAIL-LEAK\|BIN-TAIL-LEAK\|STATE-LEAK\|WATCH-LEAK' "$c1out"; then
    st_bad "classify leaked file body"
  else st_ok "classify body absent"; fi
  local mx
  mx=$(awk -F'\t' '$1=="max_bytes_read_per_file"{print $2}' "$c1out")
  if [ "$mx" = 200 ]; then st_ok "max header read 200"
  else st_bad "max header read '$mx'"; fi
  if grep -q $'^CLASS\tmagic\tpdf\t' "$c1out"; then st_ok "pdf magic class"
  else st_bad "pdf magic missing"; fi
  if grep -q $'^CLASS\tmagic\tjson-text\t' "$c1out"; then st_ok "json magic class"
  else st_bad "json magic missing"; fi
  local sec sym
  sec=$(awk -F'\t' '$1=="secret_shaped_files"{print $2}' "$c1out")
  sym=$(awk -F'\t' '$1=="symlinks"{print $2}' "$c1out")
  if [ "$sec" = 1 ]; then st_ok "secret-shaped counted unread"; else st_bad "secret count=$sec"; fi
  if [ "$sym" = 1 ]; then st_ok "symlink counted not followed"; else st_bad "symlink count=$sym"; fi
  local forb
  forb=$(awk -F'\t' '$1=="forbidden_skipped_files"{print $2}' "$c1out")
  if [ "$forb" = 2 ]; then st_ok "forbidden surfaces skipped"; else st_bad "forbidden count=$forb"; fi
  local sread
  sread=$(awk -F'\t' '$1=="secret_bytes_read"{print $2}' "$c1out")
  if [ "$sread" = 0 ]; then st_ok "secret_bytes_read=0"; else st_bad "secret_bytes_read=$sread"; fi

  set +e
  dout=$(env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --classify "$ST_TMP/no-such-dir" 2>&1)
  cst=$?
  set -e
  if [ "$cst" = 1 ] && printf '%s\n' "$dout" | grep -q $'^NOT-SAFE\tunreachable\t'; then
    st_ok "missing classify root is unreachable exit 1"
  else
    st_bad "missing classify exit=$cst out=$(printf '%s' "$dout" | head -1)"
  fi
  if printf '%s\n' "$dout" | grep -q $'^accounted\tyes$'; then
    st_bad "missing root looked accounted"
  else st_ok "missing root not accounted"; fi

  ln -s "$CD" "$ST_TMP/class-link"
  set +e
  dout=$(env -u GIT_DIR SOUJI_IMPL35_SELFTEST_ACTIVE=1 \
    "$SELF" --classify "$ST_TMP/class-link" 2>&1)
  cst=$?
  set -e
  if [ "$cst" = 1 ] && printf '%s\n' "$dout" | grep -q $'^NOT-SAFE\tsymlink-root\t'; then
    st_ok "symlink root refused"
  else st_bad "symlink root exit=$cst"; fi
  if printf '%s\n' "$dout" | grep -q 'LEAKED-SECRET-TOKEN'; then
    st_bad "symlink root leaked target"
  else st_ok "symlink root did not read target"; fi

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# --- main --------------------------------------------------------------------

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; MODE=selftest; shift ;;
    --drift) MODE=drift; shift ;;
    --classify)
      [ "$#" -ge 2 ] || usage_err "--classify needs a directory"
      CLASSIFY_DIR=$2; MODE=classify; shift 2 ;;
    --classify=*) CLASSIFY_DIR=${1#*=}; MODE=classify; shift ;;
    --include-root) INCLUDE_ROOT=1; shift ;;
    --root)
      [ "$#" -ge 2 ] || usage_err "--root needs a directory"
      ROOT=$2; shift 2 ;;
    --root=*) ROOT=${1#*=}; shift ;;
    --compare)
      [ "$#" -ge 2 ] || usage_err "--compare needs a TSV path"
      COMPARE=$2; shift 2 ;;
    --compare=*) COMPARE=${1#*=}; shift ;;
    --skill)
      [ "$#" -ge 2 ] || usage_err "--skill needs a file"
      SKILL_FILE=$2; shift 2 ;;
    --skill=*) SKILL_FILE=${1#*=}; shift ;;
    --tools)
      [ "$#" -ge 2 ] || usage_err "--tools needs a directory"
      TOOLS_DIR=$2; shift 2 ;;
    --tools=*) TOOLS_DIR=${1#*=}; shift ;;
    --scratch)
      [ "$#" -ge 2 ] || usage_err "--scratch needs a directory"
      SCRATCH_DIR=$2; shift 2 ;;
    --scratch=*) SCRATCH_DIR=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown flag: $1" ;;
    *) usage_err "unexpected argument: $1" ;;
  esac
done

if [ "$SELFTEST" = 1 ]; then run_selftest; fi
case "$MODE" in
  drift) run_drift; exit $? ;;
  classify) run_classify "$CLASSIFY_DIR"; exit $? ;;
  census)
    if [ -n "$COMPARE" ]; then emit_compare; exit $?; fi
    emit_census
    exit 0
    ;;
  *) usage_err "unknown mode" ;;
esac
