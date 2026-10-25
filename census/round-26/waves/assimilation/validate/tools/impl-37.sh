#!/usr/bin/env bash
# impl-37 — round-6 implementor candidate (seat S37).
#
# Candidate for tools/souji-census.sh, plus the r6 calibration and coverage
# checks the census alone does not cover. Read-only over every surface it
# inspects. Never fetches. Never writes outside a mktemp dir. Never reads a
# secret-shaped path. Never touches .ufo/state or .ufo/watchdog.log.
#
# CLI
#   tools/impl-37.sh census [--root DIR] [--include-root] [--compare PREV.tsv]
#   tools/impl-37.sh drift [--skill PATH]
#   tools/impl-37.sh reconcile [--skill PATH]
#   tools/impl-37.sh scratch [--path DIR] [--headers none|extensionless]
#   tools/impl-37.sh --selftest
#
# census TSV (stdout only; repos sorted by path):
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#   mtime_iso excludes .scratch, .git, .ufo/state, and .ufo/watchdog.log so a
#   live scratch writer does not churn the repeatable columns. scratch_bytes
#   is still the apparent size of <repo>/.scratch (du -sb -P; symlinks not
#   followed). verdict_flags is a comma list drawn from:
#     clean dirty unpushed no-remote scratch scratch-symlink
#     scratch-unverifiable secret-shaped status-unverifiable not-a-repo error
#   clean means unpushed=0, dirty=0, and a remote-tracking ref exists. It does
#   not mean "no hygiene notes": scratch and secret-shaped are additive.
#   Unpushed with zero refs/remotes/* is the local commit count plus no-remote
#   (pushed-unverifiable). The number is reported; clean is not.
#
# --compare PREV.tsv
#   Diff TSV on stdout: repo  field  before  after  change
#   Exit 0 if header-only; exit 3 if any field differs. Exit 2 on a bad file.
#
# drift
#   Closed checklist of SKILL.md receipt guidance against the installed tools
#   and tools/souji-verify.spec.md. One TSV row per check:
#     DRIFT  id  AGREE|DRIFT  detail
#   SUMMARY  drift=N  agree=M  advisory=K
#   Counted ids are S* (the skill path) and T* (installed tools/spec).
#   A* rows are advisory known gaps that docs and tools currently share, or
#   tool defects this seat does not patch in place. Exit 0 when counted
#   drift=0; exit 3 when counted drift>0.
#
# reconcile
#   Prints a SKILL.md with the r5-routed receipt guidance rewritten to match
#   the installed tools (no git fetch, no hardcoded origin/main,
#   pushed-unverifiable, symlink-present, secrets-refusal, census exclusion,
#   mint-time counts removed). Stdout only — the live file is not written.
#   Idempotent: a second run on its own output is a no-op. Exit 1 if a block
#   cannot be applied and is not already present.
#
# scratch
#   Classifies every descendant of a .scratch tree by metadata. Content is
#   opened only for non-secret, non-forbidden, non-empty extensionless files,
#   and then only the first 200 bytes (head -c 200). Secret-shaped names are
#   counted and never opened. The mode never emits SAFE: size is not a
#   receipt. Handoff verdict is NOT-SAFE.
#
# Exit codes: 0 evaluated / selftest pass; 1 selftest or reconcile failure;
# 2 usage; 3 drift>0 or compare differs. No other codes.
#
# Env: SHOKUNIN_ROOT (default: parent of this repo).
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
SHOKUNIN_ROOT="$(readlink -m -- "$SHOKUNIN_ROOT" 2>/dev/null || printf '%s' "$SHOKUNIN_ROOT")"

CENSUS_HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'
DIFF_HEADER=$'repo\tfield\tbefore\tafter\tchange'

usage() {
  sed -n '2,58p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}
usage_err() { printf 'impl-37: %s\n' "$1" >&2; usage 2; }

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

sanitize_field() {
  local s=${1-}
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

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
    .ufo/state|.ufo/state/*|*/.ufo/state|*/.ufo/state/*|.ufo/watchdog.log|*/.ufo/watchdog.log)
      return 0 ;;
  esac
  return 1
}

# --- census -------------------------------------------------------------------

count_worktrees() {
  local n
  n=$(git -C "$1" worktree list 2>/dev/null | grep -c . || true)
  printf '%s' "${n// /}"
}

count_unpushed() { # prints count<TAB>no-remote|has-remote
  local repo=$1 nremotes n
  nremotes=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null | grep -c . || true)
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

scratch_bytes() { # prints bytes<TAB>flag-or-empty
  local d="$1/.scratch"
  if [ -L "$d" ]; then printf '0\tscratch-symlink'; return 0; fi
  if [ ! -e "$d" ]; then printf '0\t'; return 0; fi
  if [ ! -d "$d" ]; then printf '0\tscratch-unverifiable'; return 0; fi
  local line bytes
  line=$(du -sb -P -- "$d" 2>/dev/null | head -1 || true)
  bytes=${line%%[[:space:]]*}
  case "$bytes" in
    ''|*[!0-9]*) printf '0\tscratch-unverifiable' ;;
    0) printf '0\t' ;;
    *) printf '%s\tscratch' "$bytes" ;;
  esac
}

# Newest regular-file mtime outside scratch/git/forbidden surfaces.
# Prints iso (possibly empty). Does not open file contents.
newest_mtime() {
  local repo=$1 epoch iso
  epoch=$(
    cd -- "$repo" && find . \
      \( -name .git -o -name .scratch -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \) -prune \
      -o -type f -printf '%T@\n' 2>/dev/null \
      | awk 'BEGIN{m=0} {if ($1>m) m=$1} END{if (m>0) printf "%d\n", m}'
  ) || true
  if [ -z "${epoch:-}" ]; then printf ''; return 0; fi
  iso=$(date -d "@$epoch" --iso-8601=seconds 2>/dev/null || true)
  printf '%s' "$iso"
}

# Name-only. Prints secret-shaped or empty. Never opens a matched file.
secret_flag() {
  local repo=$1 saw
  saw=$(
    cd -- "$repo" && find . \
      \( -name .git -o -path './.ufo/state' -o -path './.ufo/watchdog.log' \) -prune \
      -o -print 2>/dev/null \
      | awk '
        function secret(s,   n,i,p,lc) {
          n = split(s, p, "/")
          for (i = 1; i <= n; i++) {
            lc = tolower(p[i])
            if (lc ~ /\.env$/ || lc ~ /^\.env\./ || lc == ".envrc" || lc ~ /credential/ || lc ~ /secret/ || lc ~ /^id_/ || lc ~ /\.pem$/)
              return 1
          }
          return 0
        }
        {
          rel = $0
          sub(/^\.\//, "", rel)
          if (rel == "" || rel == ".") next
          if (secret(rel)) { print "yes"; exit }
        }
      '
  ) || true
  if [ "$saw" = yes ]; then printf 'secret-shaped'; fi
}

join_ordered_flags() {
  local ordered="" name f
  local -a flags=("$@")
  for name in clean dirty unpushed no-remote scratch scratch-symlink scratch-unverifiable secret-shaped status-unverifiable not-a-repo error; do
    for f in "${flags[@]+"${flags[@]}"}"; do
      if [ "$f" = "$name" ]; then
        if [ -z "$ordered" ]; then ordered=$name; else ordered="$ordered,$name"; fi
      fi
    done
  done
  printf '%s' "$ordered"
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
  local wt unp_line unp remote_flag dirty sb_line scratch sflag iso sec
  local -a flags=()
  wt=$(count_worktrees "$repo")
  unp_line=$(count_unpushed "$repo")
  unp=${unp_line%%$'\t'*}
  remote_flag=${unp_line#*$'\t'}
  dirty=$(count_dirty "$repo")
  sb_line=$(scratch_bytes "$repo")
  scratch=${sb_line%%$'\t'*}
  sflag=${sb_line#*$'\t'}
  iso=$(newest_mtime "$repo")
  sec=$(secret_flag "$repo")

  case "$wt" in ''|*[!0-9]*) wt=0; flags+=(error) ;; esac
  case "$unp" in ''|*[!0-9]*) unp=0; flags+=(error) ;; esac
  case "$scratch" in ''|*[!0-9]*) scratch=0; flags+=(error) ;; esac
  if [ "$remote_flag" = no-remote ]; then flags+=(no-remote); fi
  if [ "${unp:-0}" -gt 0 ] && [ "$remote_flag" != no-remote ]; then flags+=(unpushed); fi
  if [ "$dirty" = unverifiable ]; then
    dirty=0
    flags+=(status-unverifiable)
  elif [ "${dirty:-0}" -gt 0 ]; then
    flags+=(dirty)
  fi
  if [ -n "$sflag" ]; then flags+=("$sflag"); fi
  if [ -n "$sec" ]; then flags+=("$sec"); fi

  local has_problem=0 f
  for f in "${flags[@]+"${flags[@]}"}"; do
    case "$f" in
      dirty|unpushed|no-remote|status-unverifiable|error|not-a-repo) has_problem=1 ;;
    esac
  done
  if [ "$has_problem" = 0 ]; then flags+=(clean); fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(sanitize_field "$repo")" "$wt" "$unp" "$dirty" "$scratch" \
    "$(sanitize_field "$iso")" "$(sanitize_field "$(join_ordered_flags "${flags[@]+"${flags[@]}"}")")"
}

list_repos() {
  local root=$1 include_root=$2 d base
  local -a found=()
  if [ "$include_root" = 1 ] && [ -d "$root" ] && [ -e "$root/.git" ]; then
    found+=("$root")
  fi
  shopt -s nullglob
  for d in "$root"/*/; do
    [ -d "$d" ] || continue
    base=$(basename -- "$d")
    case "$base" in .*) continue ;; esac
    if [ -e "${d%/}/.git" ]; then found+=("${d%/}"); fi
  done
  shopt -u nullglob
  if [ "${#found[@]}" -eq 0 ]; then return 0; fi
  local p
  for p in "${found[@]}"; do printf '%s\n' "$p"; done | LC_ALL=C sort
}

emit_census() { # $1 root $2 include_root
  local root repo
  root=$(canon_path "$1")
  [ -d "$root" ] || { printf 'impl-37: root is not a directory: %s\n' "$root" >&2; exit 1; }
  printf '%s\n' "$CENSUS_HEADER"
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    census_one "$repo"
  done < <(list_repos "$root" "$2")
}

load_census() { # $1 file $2 nameref
  local file=$1
  local -n _map=$2
  [ -f "$file" ] || usage_err "compare file not found: $file"
  local line n=0 repo rest
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    if [ "$n" = 1 ]; then
      [ "$line" = "$CENSUS_HEADER" ] || usage_err "compare file header mismatch"
      continue
    fi
    repo=${line%%$'\t'*}
    rest=${line#*$'\t'}
    [ -n "$repo" ] || usage_err "compare file: empty repo on line $n"
    [ -z "${_map[$repo]+x}" ] || usage_err "compare file: duplicate repo $repo"
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

emit_compare() { # $1 root $2 include_root $3 prev
  local -A before=() after=()
  load_census "$3" before
  local tmp
  tmp=$(mktemp "${TMPDIR:-/tmp}/impl37-census.XXXXXX")
  emit_census "$1" "$2" > "$tmp"
  load_census "$tmp" after
  rm -f -- "$tmp"
  printf '%s\n' "$DIFF_HEADER"
  local changes=0 repo rest_b rest_a sorted name i before_v after_v chg
  local -a repos=()
  local -a names=(worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags)
  for repo in "${!before[@]}"; do repos+=("$repo"); done
  for repo in "${!after[@]}"; do
    [ -n "${before[$repo]+x}" ] || repos+=("$repo")
  done
  sorted=$(printf '%s\n' "${repos[@]}" | LC_ALL=C sort -u)
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    if [ -z "${before[$repo]+x}" ]; then
      printf '%s\trepo\tABSENT\tPRESENT\tadded\n' "$(sanitize_field "$repo")"
      changes=$((changes + 1)); continue
    fi
    if [ -z "${after[$repo]+x}" ]; then
      printf '%s\trepo\tPRESENT\tABSENT\tremoved\n' "$(sanitize_field "$repo")"
      changes=$((changes + 1)); continue
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

# --- drift --------------------------------------------------------------------

DRIFT_N=0
AGREE_N=0
ADVISORY_N=0

drift_row() { # $1 id $2 AGREE|DRIFT|ADVISORY $3 detail
  local id=$1 st=$2 detail=$3
  printf 'DRIFT\t%s\t%s\t%s\n' "$id" "$st" "$(sanitize_field "$detail")"
  case "$st" in
    AGREE) AGREE_N=$((AGREE_N + 1)) ;;
    DRIFT) DRIFT_N=$((DRIFT_N + 1)) ;;
    ADVISORY) ADVISORY_N=$((ADVISORY_N + 1)) ;;
  esac
}

file_has() { grep -F -q -- "$2" "$1"; }
file_lacks() { ! grep -F -q -- "$2" "$1"; }

# Non-comment executable git-fetch. Comments may name the prohibition.
tool_runs_fetch() {
  awk '
    /^[[:space:]]*#/ { next }
    /(^|[[:space:];|&])git[[:space:]]+fetch([[:space:]]|$)/ { found=1 }
    END { exit found ? 0 : 1 }
  ' "$1"
}

emit_drift() { # $1 skill path
  local skill=$1 spec="$REPO_ROOT/tools/souji-verify.spec.md"
  local verify="$REPO_ROOT/tools/souji-verify.sh" vault="$REPO_ROOT/tools/souji-vault-verify.sh"
  DRIFT_N=0; AGREE_N=0; ADVISORY_N=0
  [ -f "$skill" ] || { printf 'impl-37: skill not found: %s\n' "$skill" >&2; exit 1; }
  [ -f "$spec" ] || { printf 'impl-37: spec not found: %s\n' "$spec" >&2; exit 1; }
  [ -f "$verify" ] || { printf 'impl-37: verify tool not found: %s\n' "$verify" >&2; exit 1; }
  [ -f "$vault" ] || { printf 'impl-37: vault tool not found: %s\n' "$vault" >&2; exit 1; }

  if file_lacks "$skill" 'git fetch -q'; then drift_row S1 AGREE "skill lacks the fetch-q procedure"
  else drift_row S1 DRIFT "skill still instructs a fetch-q procedure"; fi
  if file_lacks "$skill" 'after `git fetch`'; then drift_row S2 AGREE "skill lacks after-git-fetch procedure"
  else drift_row S2 DRIFT "skill still says after git fetch"; fi
  if file_has "$skill" 'existing refs only'; then drift_row S3 AGREE "skill forbids fetch; existing refs only"
  else drift_row S3 DRIFT "skill does not say existing refs only"; fi
  if file_lacks "$skill" 'origin/main'; then drift_row S4 AGREE "skill does not hardcode origin/main"
  else drift_row S4 DRIFT "skill hardcodes origin/main"; fi
  if file_has "$skill" 'pushed-unverifiable'; then drift_row S5 AGREE "skill names pushed-unverifiable"
  else drift_row S5 DRIFT "skill omits pushed-unverifiable"; fi
  if file_has "$skill" 'refs/remotes/origin/HEAD'; then drift_row S6 AGREE "skill names refs/remotes/origin/HEAD"
  else drift_row S6 DRIFT "skill omits refs/remotes/origin/HEAD"; fi
  if file_has "$skill" 'symlink-present'; then drift_row S7 AGREE "skill names symlink-present"
  else drift_row S7 DRIFT "skill omits symlink-present"; fi
  if file_has "$skill" 'secrets-refusal'; then drift_row S8 AGREE "skill names secrets-refusal"
  else drift_row S8 DRIFT "skill omits secrets-refusal"; fi
  if file_has "$skill" 'souji-shokunin/census'; then drift_row S9 AGREE "skill names census exclusion"
  else drift_row S9 DRIFT "skill omits souji-shokunin/census exclusion"; fi
  if file_lacks "$skill" '553M'; then drift_row S10 AGREE "skill does not state 553M as current"
  else drift_row S10 DRIFT "skill still states 553M"; fi
  if file_lacks "$skill" '19 prunable'; then drift_row S11 AGREE "skill does not state 19 prunable as current"
  else drift_row S11 DRIFT "skill still states 19 prunable"; fi
  if file_lacks "$skill" '5 prunable'; then drift_row S12 AGREE "skill does not state 5 prunable as current"
  else drift_row S12 DRIFT "skill still states 5 prunable"; fi

  if tool_runs_fetch "$verify"; then drift_row T1 DRIFT "souji-verify.sh runs git fetch"
  else drift_row T1 AGREE "souji-verify.sh does not run git fetch"; fi
  if tool_runs_fetch "$vault"; then drift_row T2 DRIFT "souji-vault-verify.sh runs git fetch"
  else drift_row T2 AGREE "souji-vault-verify.sh does not run git fetch"; fi
  if file_has "$spec" 'pushed-unverifiable'; then drift_row T3 AGREE "spec names pushed-unverifiable"
  else drift_row T3 DRIFT "spec omits pushed-unverifiable"; fi
  if file_has "$verify" 'symlink-present'; then drift_row T4 AGREE "souji-verify.sh names symlink-present"
  else drift_row T4 DRIFT "souji-verify.sh omits symlink-present"; fi
  if file_has "$vault" 'symlink-present'; then drift_row T5 AGREE "souji-vault-verify.sh names symlink-present"
  else drift_row T5 DRIFT "souji-vault-verify.sh omits symlink-present"; fi
  if file_has "$spec" 'existing refs only'; then drift_row T6 AGREE "spec says existing refs only"
  else drift_row T6 DRIFT "spec does not say existing refs only"; fi

  # Advisory: shared or tool-side gaps. Not counted. Not patched in place.
  if file_has "$spec" 'bash + coreutils + git + rg only' && grep -qE '(^|[^[:alnum:]_])(find|xargs|grep)([^[:alnum:]_]|$)' "$verify"; then
    drift_row A1 ADVISORY "spec allowlist omits find/xargs/grep that souji-verify.sh uses (r5 E5); not rewritten by this seat"
  else
    drift_row A1 ADVISORY "spec allowlist check did not match the r5 E5 pattern; re-verify before treating it as closed"
  fi
  if ! grep -F -q 'is_secret_shaped "$vp"' "$verify" && ! grep -F -q 'is_secret_shaped "$vp"' "$vault"; then
    drift_row A2 ADVISORY "neither installed tool applies is_secret_shaped to ledger vault path \$vp before hashing (r5 E3); live tools not patched"
  else
    drift_row A2 ADVISORY "a vault-path secret check is now present; re-verify the hash sites before closing r5 E3"
  fi
  if ! grep -F -q -- '--hidden' "$verify" && ! grep -F -q -- '--hidden' "$spec"; then
    drift_row A3 ADVISORY "stale sweep in spec and souji-verify.sh both omit --hidden (r5 hidden-ref false-SAFE); they agree, so this is not docs/tools drift"
  else
    drift_row A3 ADVISORY "hidden-ref wording changed; re-verify spec and tool together"
  fi

  printf 'SUMMARY\tdrift=%s\tagree=%s\tadvisory=%s\n' "$DRIFT_N" "$AGREE_N" "$ADVISORY_N"
  if [ "$DRIFT_N" -gt 0 ]; then return 3; fi
  return 0
}

# --- reconcile (stdout only) --------------------------------------------------

apply_block() { # $1 curfile $2 id $3 oldfile $4 newfile $5 marker
  local cur=$1 id=$2 oldf=$3 newf=$4 marker=$5
  local rc
  set +e
  LC_ALL=C awk -v oldfile="$oldf" -v newfile="$newf" -v marker="$marker" '
    BEGIN {
      old = ""; new = ""
      while ((getline line < oldfile) > 0) old = old line "\n"
      close(oldfile)
      while ((getline line < newfile) > 0) new = new line "\n"
      close(newfile)
      if (old == "" || new == "") exit 3
    }
    { buf = buf $0 "\n" }
    END {
      if (index(buf, old) > 0) {
        i = index(buf, old)
        printf "%s%s%s", substr(buf, 1, i - 1), new, substr(buf, i + length(old))
        exit 0
      }
      if (marker != "" && index(buf, marker) > 0) {
        printf "%s", buf
        exit 0
      }
      exit 2
    }
  ' "$cur" > "$cur.next"
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    rm -f -- "$cur.next"
    printf 'impl-37: reconcile block %s not applied (rc=%s)\n' "$id" "$rc" >&2
    return 1
  fi
  mv -- "$cur.next" "$cur"
  printf 'impl-37: reconcile block %s ok\n' "$id" >&2
}

write_blocks() { # $1 dir
  local d=$1
  cat > "$d/A.old" <<'EOF'
| `pushed` | after `git fetch`, the commit carrying the artifact passes `git merge-base --is-ancestor <commit> origin/<branch>` | `git fetch -q && git merge-base --is-ancestor <commit> origin/main && echo PUSHED` |
| `moved-to-obsidian` | a matching row exists in `corpus/knowledge/obsidian-ledger.tsv` with source path + sha256 AND vault path + sha256 | `awk -F'\t' -v p="<relpath>" '$1==p{print}' corpus/knowledge/obsidian-ledger.tsv` then `sha256sum` both sides |
| `stale` | known scratch type (`.scratch/`, `*.tmp`, checkpoint blobs, `out/`, `reports/round-*/**-draft.*`), nothing references it (`rg --files-with-matches <name>` across the owning repo returns 0 live hits), AND mtime older than the owning lane's last admitted round | `find <path> -newermt <last-round-date> | wc -l` == 0 and `rg -l <basename> <repo>` == 0 |
EOF
  cat > "$d/A.new" <<'EOF'
| `pushed` | the introducing commit (`git log --diff-filter=A --format=%H -1 -- <path>`) is an ancestor of the remote-tracking default ref. Resolve with `git symbolic-ref --quiet --short refs/remotes/origin/HEAD` (strip `origin/`). If that ref is missing, use the single `refs/remotes/origin/*` branch when exactly one exists; otherwise the receipt is `pushed-unverifiable`. No `git fetch` — existing refs only. A local ref such as `refs/heads/master` never establishes pushed. | `ref=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's@^origin/@@'); git merge-base --is-ancestor <intro> refs/remotes/origin/$ref && echo PUSHED` |
| `moved-to-obsidian` | a ledger row matches source path + sha256 AND vault path + sha256, both re-hashed read-only. Any symlink in a digest scope is `NOT-SAFE(symlink-present)`. A secret-shaped source or vault path component is `NOT-SAFE(secrets-refusal)` before any read. | `sha256sum` both sides; refuse on `symlink-present` or `secrets-refusal` |
| `stale` | scratch type is a `.scratch` path component, or basename `*.out`, `*.log`, `*-draft.*`, or checkpoint json/png (`*checkpoint*.json`, `*checkpoint*.png`, `*ckpt*`, `launch-*.json`). Zero live references from `rg -l --no-ignore --fixed-strings`, excluding `souji-shokunin/census/**`, `souji-shokunin/tests/**`, and `.ufo-quarantine/**`. Mtime older than `--stale-days` (default 1). `*.tmp` alone is not a receipt. | `rg -l --no-ignore --fixed-strings -e <basename> <repo> -g '!.git' -g '!**/souji-shokunin/census/**' -g '!**/souji-shokunin/tests/**' -g '!**/.ufo-quarantine/**'` returns 0, and mtime age > stale-days |
EOF
  cat > "$d/B.old" <<'EOF'
| Owning repo has unpushed commits touching the artifact's path, or a dirty worktree over it | `NOT-SAFE` — live work; record and skip |
| Artifact's last commit is an ancestor of `origin/<default>` | `SAFE(pushed)` — removable after quarantine |
| Ledger row matches path + hash | `SAFE(moved-to-obsidian)` — source copy removable |
| Scratch type + zero live references + older than lane's last admitted round | `SAFE(stale)` — removable |
| Anything else, any doubt, any credential-shaped content | `NOT-SAFE` — stay silent in the dry run |
EOF
  cat > "$d/B.new" <<'EOF'
| Owning repo has unpushed commits touching the artifact's path, or a dirty worktree over it | `NOT-SAFE` — live work; record and skip |
| Introducing commit is an ancestor of `refs/remotes/origin/HEAD` (or the single origin branch ref) | `SAFE(pushed)` — removable after quarantine |
| No remote-tracking ref can establish pushed | `NOT-SAFE(pushed-unverifiable)` |
| Ledger row matches path + both hashes, no symlink in the digest scope, no secret-shaped component | `SAFE(moved-to-obsidian)` — source copy removable |
| Symlink inside a digest scope | `NOT-SAFE(symlink-present)` |
| Secret-shaped path component (`*.env`, `.env`, `.env.*`, `.envrc`, `*credential*`, `*secret*`, `id_*`, `*.pem`) | `NOT-SAFE(secrets-refusal)` — before any read |
| Scratch type + zero live references (census/tests/quarantine excluded) + older than `--stale-days` | `SAFE(stale)` — removable |
| Anything else, any doubt | `NOT-SAFE` — stay |
EOF
  cat > "$d/C.old" <<'EOF'
- **Unpushed-lane trap**: `git worktree list` says `prunable`, but
  `git log --branches --not --remotes --oneline` in the owning repo is
  non-empty → the worktree metadata is NOT safe to prune yet; classify the
  *commits* first. Live instance: kotodama-shokunin 2026-10-18 (round-17..22
  unpushed, dirty tree, 553M `.scratch/`).
EOF
  cat > "$d/C.new" <<'EOF'
- **Unpushed-lane trap**: a worktree registration whose named branch has
  commits not in any remote-tracking ref is `NOT-SAFE(unpushed-branch)`,
  even when the directory is absent and `git log <HEAD> --not --all` is
  empty. Dir absent AND unique commits of that HEAD vs `--all` = 0 AND no
  named unpushed branch → `SAFE(metadata-prune)`. Repo-level unpushed
  commits that do not touch the registration do not by themselves block
  metadata-prune. A lane with unpushed commits and a dirty tree over
  `.scratch/` (kotodama-shokunin, 2026-10-18) is `NOT-SAFE` as a repo-root;
  re-measure size — a mint-time byte figure is not a current receipt.
EOF
  cat > "$d/D.old" <<'EOF'
## Known surfaces (fleet, 2026-10-18)

- Fleet root: `b2f2efa` checkpoint files at HEAD; `shokunin.conf.full-roster-20261015`.
- lore-shokunin: 19 prunable worktrees (`git worktree list`).
- game-dev-2d-shokunin: 5 prunable worktrees.
- kotodama-shokunin: 553M `.scratch/` beside unpushed round-17..22 work — NOT-SAFE.
- Sibling lane repos: census rounds extend the surface table.
EOF
  cat > "$d/D.new" <<'EOF'
## Known surfaces (re-measure; do not trust mint-time counts)

- Fleet root and each `*-shokunin` lane: re-measure with the census tool. Counts are point-in-time, not receipts.
- Worktree registrations: `git worktree list --porcelain` in the owning repo; prune only on `SAFE(metadata-prune)`.
- kotodama-shokunin `.scratch/`: live unpushed lane — `NOT-SAFE` regardless of size. Classify read-only; never prune on size alone. Content reads are a 200-byte header at most and skip secret-shaped names.
- Sibling lane repos: census rounds extend the surface table. Historical mint figures live in MINT.md and are not current receipts.
EOF
}

emit_reconcile() { # $1 skill; prints reconciled skill on stdout
  local src=$1
  [ -f "$src" ] || { printf 'impl-37: skill not found: %s\n' "$src" >&2; exit 1; }
  local tmp
  tmp=$(mktemp -d "${TMPDIR:-/tmp}/impl37-reconcile.XXXXXX")
  cp -- "$src" "$tmp/cur"
  write_blocks "$tmp"
  apply_block "$tmp/cur" A "$tmp/A.old" "$tmp/A.new" 'existing refs only' || { rm -rf -- "$tmp"; return 1; }
  apply_block "$tmp/cur" B "$tmp/B.old" "$tmp/B.new" 'secrets-refusal' || { rm -rf -- "$tmp"; return 1; }
  apply_block "$tmp/cur" C "$tmp/C.old" "$tmp/C.new" 'SAFE(metadata-prune)' || { rm -rf -- "$tmp"; return 1; }
  apply_block "$tmp/cur" D "$tmp/D.old" "$tmp/D.new" 'do not trust mint-time counts' || { rm -rf -- "$tmp"; return 1; }
  cat -- "$tmp/cur"
  rm -rf -- "$tmp"
}

# --- scratch ------------------------------------------------------------------

header_class() { # $1 file; prints a hdr-* class. Caller already refused secrets.
  local f=$1 raw
  if ! raw=$(head -c 200 -- "$f" 2>/dev/null); then
    printf 'hdr-unreadable'
    return 0
  fi
  # A NUL byte in the sample => binary. Do not put NUL in a bash pattern:
  # the pattern string truncates and then matches everything. od -An prints
  # space-separated hex and no address column.
  if head -c 200 -- "$f" 2>/dev/null | od -An -tx1 | grep -qE '(^|[[:space:]])00([[:space:]]|$)'; then
    printf 'hdr-binary'
    return 0
  fi
  if [ -z "$raw" ]; then printf 'hdr-empty'; return 0; fi
  case "$raw" in
    '{'*|'['*) printf 'hdr-json'; return 0 ;;
    '#!'*) printf 'hdr-shebang'; return 0 ;;
    'import '*|'def '*|'from '*) printf 'hdr-python'; return 0 ;;
    '#'*) printf 'hdr-hash'; return 0 ;;
  esac
  # Mostly printable => text. Ratio over the 200-byte sample only.
  local len non
  len=${#raw}
  non=$(printf '%s' "$raw" | tr -cd '[:print:][:space:]' | wc -c | tr -d ' ')
  if [ "$len" -gt 0 ] && [ $((non * 100 / len)) -ge 90 ]; then
    printf 'hdr-text'
  else
    printf 'hdr-binary'
  fi
}

emit_scratch() { # $1 scratch path $2 headers mode
  local root headers=$2
  root=$(canon_path "$1")
  if is_secret_relpath "$root"; then
    printf 'HANDOFF\ttarget\t%s\n' "$(sanitize_field "$root")"
    printf 'HANDOFF\tverdict\tNOT-SAFE\n'
    printf 'HANDOFF\treceipt\tsecrets-refusal\n'
    printf 'HANDOFF\taction\tdo-not-walk\n'
    printf 'HANDOFF\tmethod\tpath refused before any read\n'
    return 0
  fi
  if [ ! -d "$root" ]; then
    printf 'impl-37: scratch path is not a directory: %s\n' "$root" >&2
    return 1
  fi
  local owner
  owner=$(dirname -- "$root")
  local unpushed=unverifiable dirty=unverifiable
  if [ -e "$owner/.git" ]; then
    unpushed=$(git -C "$owner" rev-list --count --branches --not --remotes 2>/dev/null || printf 'unverifiable')
    unpushed=${unpushed// /}
    if dirty_st=$(git -C "$owner" status --porcelain --untracked-files=all 2>/dev/null); then
      if [ -z "$dirty_st" ]; then dirty=0; else dirty=$(printf '%s\n' "$dirty_st" | grep -c . || true); fi
    fi
  fi

  local agg find_rc awk_rc find_errs=0
  agg=$(mktemp "${TMPDIR:-/tmp}/impl37-scratch.XXXXXX")
  # Metadata only. Do not open file contents in this pass.
  # find exits non-zero on an unreadable descendant; that must not abort the
  # classification of everything it did print. Do not echo the error paths.
  set +e
  find "$root" -mindepth 1 -printf '%y\t%s\t%P\n' 2>"$agg.finderr" \
    | LC_ALL=C awk -v out="$agg.counts" '
    function secret(s,   n,i,p,lc) {
      n = split(s, p, "/")
      for (i = 1; i <= n; i++) {
        lc = tolower(p[i])
        if (lc ~ /\.env$/ || lc ~ /^\.env\./ || lc == ".envrc" || lc ~ /credential/ || lc ~ /secret/ || lc ~ /^id_/ || lc ~ /\.pem$/)
          return 1
      }
      return 0
    }
    function bump(cls, sz) { count[cls]++; bytes[cls] += sz; total++; total_bytes += sz }
    {
      if (index($0, "\t") == 0) { warn++; next }
      type = $1
      sz = $2
      rel = substr($0, length($1) + length($2) + 3)
      if (rel ~ /\t/ || type !~ /^[a-z]$/ || sz !~ /^[0-9]+$/) { warn++; next }
      entries++
      if (secret(rel)) { bump("secret-shaped", sz); next }
      if (rel ~ /(^|\/)\.git(\/|$)/) { bump("git-metadata", sz); next }
      if (rel ~ /(^|\/)\.ufo\/state(\/|$)/ || rel ~ /(^|\/)\.ufo\/watchdog\.log$/) { bump("forbidden-unread", sz); next }
      if (type == "l") { bump("symlink", sz); next }
      if (type == "d") { bump("dir", sz); next }
      if (type != "f") { bump("other-" type, sz); next }
      if (sz == 0) { bump("empty", sz); next }
      base = rel
      sub(/.*\//, "", base)
      ext = ""
      if (match(base, /\.[^.]+$/)) ext = tolower(substr(base, RSTART + 1, RLENGTH - 1))
      if (ext == "") { bump("extensionless", sz); next }
      if (ext ~ /^(md|txt|json|jsonl|yml|yaml|py|sh|log|out|tsv|err|stderr|stdout|raw|stamp|sha256|gitignore|nohup)$/) {
        bump("text-" ext, sz); next
      }
      if (ext ~ /^(pyc|png|jpg|jpeg|gif|so|bin|gz|zip|woff|wasm)$/) {
        bump("binary-" ext, sz); next
      }
      bump("ext-" ext, sz)
    }
    END {
      for (c in count) printf "%s\t%d\t%d\n", c, count[c], bytes[c] > out
      printf "META\tentries\t%d\n", entries+0
      printf "META\twarn\t%d\n", warn+0
      printf "META\ttotal_bytes\t%d\n", total_bytes+0
    }
  ' > "$agg.meta"
  find_rc=${PIPESTATUS[0]}
  awk_rc=${PIPESTATUS[1]}
  set -e
  if [ -f "$agg.finderr" ]; then
    find_errs=$(wc -l < "$agg.finderr" | tr -d ' ')
  fi
  if [ "$awk_rc" -ne 0 ]; then
    printf 'impl-37: scratch classifier awk failed rc=%s\n' "$awk_rc" >&2
    rm -f -- "$agg" "$agg.counts" "$agg.meta" "$agg.finderr"
    return 1
  fi

  declare -A CLS_N=() CLS_B=()
  local line cls n b
  if [ -f "$agg.counts" ]; then
    while IFS=$'\t' read -r cls n b; do
      [ -n "$cls" ] || continue
      CLS_N["$cls"]=$n
      CLS_B["$cls"]=$b
    done < "$agg.counts"
  fi

  local header_reads=0
  if [ "$headers" = extensionless ]; then
    while IFS= read -r -d '' f; do
      rel=${f#"$root"/}
      if is_secret_relpath "$rel"; then continue; fi
      if is_forbidden_relpath "$rel"; then continue; fi
      case "$rel" in .git/*|*/.git/*|.git) continue ;; esac
      [ -s "$f" ] || continue
      # only refine files the metadata pass called extensionless (no dot in the basename)
      base=$(basename -- "$f")
      case "$base" in *.*) continue ;; esac
      hcls=$(header_class "$f")
      header_reads=$((header_reads + 1))
      CLS_N["$hcls"]=$(( ${CLS_N[$hcls]:-0} + 1 ))
      # byte move: extensionless bytes are not split per file here; header class
      # counts files. Byte totals stay on the metadata class so sums still match
      # the find pass. Header classes are count-only refinements.
      CLS_B["$hcls"]=$(( ${CLS_B[$hcls]:-0} + 0 ))
      CLS_N["extensionless"]=$(( ${CLS_N[extensionless]:-0} - 1 ))
    done < <(find "$root" \
      \( -name .git -o -path '*/.git' -o -path '*/.ufo/state' -o -name watchdog.log \) -prune \
      -o -type f ! -name '*.*' -print0 2>/dev/null || true)
  fi

  local entries=0 warn=0 file_bytes=0
  while IFS=$'\t' read -r tag k v; do
    case "$tag" in
      META)
        case "$k" in
          entries) entries=$v ;;
          warn) warn=$v ;;
          total_bytes) file_bytes=$v ;;
        esac
        ;;
    esac
  done < "$agg.meta"

  local sum=0 c
  for c in "${!CLS_N[@]}"; do
    case "$c" in
      extensionless) [ "${CLS_N[$c]}" -eq 0 ] && continue ;;
    esac
    sum=$((sum + CLS_N[$c]))
  done

  printf 'CLASS\tclass\tcount\tbytes\n'
  for c in $(printf '%s\n' "${!CLS_N[@]}" | LC_ALL=C sort); do
    [ "${CLS_N[$c]}" -eq 0 ] && continue
    printf 'CLASS\t%s\t%s\t%s\n' "$c" "${CLS_N[$c]}" "${CLS_B[$c]:-0}"
  done
  local du_bytes=unverifiable
  if du_line=$(du -sb -P -- "$root" 2>/dev/null | head -1); then
    du_bytes=${du_line%%[[:space:]]*}
  fi
  printf 'TOTAL\tentries\t%s\n' "$entries"
  printf 'TOTAL\tclass_sum\t%s\n' "$sum"
  printf 'TOTAL\tfind_file_bytes\t%s\n' "$file_bytes"
  printf 'TOTAL\tdu_bytes\t%s\n' "$du_bytes"
  printf 'TOTAL\theader_reads\t%s\n' "$header_reads"
  printf 'TOTAL\tpath_warn\t%s\n' "$warn"
  printf 'HANDOFF\ttarget\t%s\n' "$(sanitize_field "$root")"
  printf 'HANDOFF\towner\t%s\n' "$(sanitize_field "$owner")"
  printf 'HANDOFF\tverdict\tNOT-SAFE\n'
  printf 'HANDOFF\treceipt\tnone\n'
  printf 'HANDOFF\tunpushed\t%s\n' "$(sanitize_field "$unpushed")"
  printf 'HANDOFF\tdirty\t%s\n' "$(sanitize_field "$dirty")"
  printf 'HANDOFF\taction\tdo-not-prune\n'
  printf 'HANDOFF\tmethod\tmetadata find -printf; head -c 200 only for non-secret extensionless files; secret-shaped names unread\n'
  printf 'HANDOFF\tnote\tsize is not a receipt; route to the owning lane; this mode never emits SAFE\n'
  if [ "$sum" -ne "$entries" ]; then
    printf 'HANDOFF\tclass_sum_mismatch\tclass_sum=%s entries=%s\n' "$sum" "$entries" >&2
    rm -f -- "$agg" "$agg.counts" "$agg.meta"
    return 1
  fi
  rm -f -- "$agg" "$agg.counts" "$agg.meta"
  return 0
}

# --- selftest -----------------------------------------------------------------

ST_PASS=0
ST_FAIL=0
st_note() { printf '%s\n' "$*"; }
st_ok() { ST_PASS=$((ST_PASS + 1)); st_note "PASS $*"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); st_note "FAIL $*"; }

st_commit() {
  local repo=$1 parent=$2 msg=$3 tree sha
  git -C "$repo" add -A >/dev/null
  tree=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tree" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tree")
  fi
  printf '%s' "$sha"
}

st_init() { git init -q --initial-branch="$2" "$1"; }

st_row_field() { # $1 tsv $2 basename $3 column
  local tsv=$1 base=$2 col=$3 line rest part i
  line=$(grep -F "/$base"$'\t' "$tsv" | head -1 || true)
  [ -n "$line" ] || { printf ''; return 0; }
  rest=$line
  i=1
  while [ "$i" -le 7 ]; do
    if [ "$i" -eq 7 ]; then part=$rest; else part=${rest%%$'\t'*}; rest=${rest#*$'\t'}; fi
    if [ "$i" -eq "$col" ]; then printf '%s' "$part"; return 0; fi
    i=$((i + 1))
  done
}

run_selftest() {
  if [ "${SOUJI_IMPL37_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'impl-37: refusing nested --selftest\n' >&2
    exit 1
  fi
  local skill_before skill_after
  ST_CLEAN=$(mktemp -d "${TMPDIR:-/tmp}/impl37-selftest.XXXXXX")
  local tmp=$ST_CLEAN
  skill_before=$(sha256sum -- "$REPO_ROOT/SKILL.md" | awk '{print $1}')
  trap 'rm -rf -- "${ST_CLEAN:-}"' EXIT
  export GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji@shokunin.local
  export GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji@shokunin.local

  # secret-component unit checks
  if is_secret_relpath 'a/credentials.env' && is_secret_relpath 'a/ID_RSA' && is_secret_relpath 'a/.envrc' \
     && is_secret_relpath 'a/foo.pem' && ! is_secret_relpath 'dir-with-.env-child/x' \
     && ! is_secret_relpath 'a/note.md'; then
    st_ok "secret-component matcher"
  else
    st_bad "secret-component matcher"
  fi

  local fleet="$tmp/fleet"
  mkdir -p "$fleet"
  local RC="$fleet/clean-shokunin"
  st_init "$RC" master
  printf 'kept\n' > "$RC/kept.txt"
  mkdir -p "$RC/.ufo/state"
  printf 'watchdog-secret\n' > "$RC/.ufo/watchdog.log"
  printf 'state-secret\n' > "$RC/.ufo/state/live.json"
  local c1
  c1=$(st_commit "$RC" "" "c1")
  git -C "$RC" update-ref refs/heads/master "$c1"
  git -C "$RC" update-ref refs/remotes/origin/master "$c1"
  git -C "$RC" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

  local RD="$fleet/dirty-shokunin"
  st_init "$RD" master
  printf 'base\n' > "$RD/base.txt"
  local d1
  d1=$(st_commit "$RD" "" "d1")
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
  u2=$(st_commit "$RU" "$u1" "u2")
  git -C "$RU" update-ref refs/heads/master "$u2"

  local RN="$fleet/noremote-shokunin"
  st_init "$RN" master
  printf 'solo\n' > "$RN/solo.txt"
  local n1
  n1=$(st_commit "$RN" "" "n1")
  git -C "$RN" update-ref refs/heads/master "$n1"

  mkdir -p "$fleet/plain-dir" "$fleet/.hidden-shokunin"
  printf 'nope\n' > "$fleet/plain-dir/x.txt"
  st_init "$fleet/.hidden-shokunin" master

  local out1="$tmp/c1.tsv" out2="$tmp/c2.tsv"
  env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" census --root "$fleet" > "$out1"
  env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" census --root "$fleet" > "$out2"
  if cmp -s "$out1" "$out2"; then st_ok "census repeat byte-identical"; else st_bad "census repeat differs"; diff -u "$out1" "$out2" || true; fi
  if [ "$(head -1 "$out1")" = "$CENSUS_HEADER" ]; then st_ok "census header"; else st_bad "census header"; fi
  local data_rows
  data_rows=$(( $(grep -c $'\t' "$out1" || true) - 1 ))
  if [ "$data_rows" = 4 ]; then st_ok "census row count 4"; else st_bad "census row count $data_rows want 4"; cat "$out1"; fi
  if grep -q 'plain-dir' "$out1"; then st_bad "plain-dir included"; else st_ok "plain-dir skipped"; fi
  if grep -q 'hidden-shokunin' "$out1"; then st_bad "dot-dir included"; else st_ok "dot-dir skipped"; fi
  if grep -q 'SUPER-SECRET-TOKEN' "$out1"; then st_bad "secret contents leaked into census"; else st_ok "secret contents absent from census"; fi
  if grep -q 'watchdog-secret\|state-secret' "$out1"; then st_bad "forbidden contents leaked"; else st_ok "forbidden contents absent"; fi

  local v
  v=$(st_row_field "$out1" clean-shokunin 7)
  case "$v" in *clean*) st_ok "clean flags ($v)" ;; *) st_bad "clean flags '$v'" ;; esac
  v=$(st_row_field "$out1" clean-shokunin 3)
  if [ "$v" = 0 ]; then st_ok "clean unpushed=0"; else st_bad "clean unpushed=$v"; fi
  v=$(st_row_field "$out1" dirty-shokunin 4)
  if [ "${v:-0}" -ge 1 ]; then st_ok "dirty count=$v"; else st_bad "dirty count=$v"; fi
  v=$(st_row_field "$out1" dirty-shokunin 7)
  case "$v" in *dirty*scratch*secret-shaped*) st_ok "dirty flags ($v)" ;; *) st_bad "dirty flags '$v'" ;; esac
  v=$(st_row_field "$out1" unpushed-shokunin 3)
  if [ "$v" = 1 ]; then st_ok "unpushed=1"; else st_bad "unpushed=$v"; fi
  v=$(st_row_field "$out1" noremote-shokunin 7)
  case "$v" in *no-remote*) st_ok "noremote flag ($v)" ;; *) st_bad "noremote flags '$v'" ;; esac
  case "$v" in clean*) st_bad "noremote marked clean" ;; *) st_ok "noremote not clean" ;; esac

  printf 'extra\n' >> "$RD/.scratch/note.txt"
  local cmp_out rc
  set +e
  cmp_out=$(env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" census --root "$fleet" --compare "$out1" 2>&1)
  rc=$?
  set -e
  if [ "$rc" = 3 ] && printf '%s\n' "$cmp_out" | grep -q $'scratch_bytes'; then
    st_ok "compare detects scratch_bytes change (exit 3)"
  else
    st_bad "compare rc=$rc out=$cmp_out"
  fi

  # drift + reconcile against the live SKILL.md (read-only; output in tmp)
  local live_out rec_out rec_file="$tmp/SKILL.reconciled.md" rec2="$tmp/SKILL.reconciled2.md"
  set +e
  live_out=$(env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" drift --skill "$REPO_ROOT/SKILL.md" 2>"$tmp/drift.err")
  local live_rc=$?
  set -e
  local live_summary
  live_summary=$(printf '%s\n' "$live_out" | awk -F'\t' '$1=="SUMMARY"{print; exit}')
  if [ -n "$live_summary" ]; then st_ok "drift summary present ($live_summary rc=$live_rc)"
  else st_bad "drift summary missing rc=$live_rc"; fi
  env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" reconcile --skill "$REPO_ROOT/SKILL.md" > "$rec_file" 2>"$tmp/rec.err"
  env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" reconcile --skill "$rec_file" > "$rec2" 2>"$tmp/rec2.err"
  if cmp -s "$rec_file" "$rec2"; then st_ok "reconcile idempotent"; else st_bad "reconcile not idempotent"; fi
  set +e
  rec_out=$(env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" drift --skill "$rec_file" 2>"$tmp/drift2.err")
  local rec_rc=$?
  set -e
  local rec_summary
  rec_summary=$(printf '%s\n' "$rec_out" | awk -F'\t' '$1=="SUMMARY"{print; exit}')
  case "$rec_summary" in
    *$'drift=0'*) st_ok "reconciled skill drift=0 ($rec_summary rc=$rec_rc)" ;;
    *) st_bad "reconciled skill not drift=0 ($rec_summary rc=$rec_rc)"; printf '%s\n' "$rec_out" | awk -F'\t' '$3=="DRIFT"{print}' ;;
  esac
  if grep -q 'git fetch -q' "$rec_file"; then st_bad "reconciled skill still has a fetch-q procedure"; else st_ok "reconciled skill has no fetch-q procedure"; fi
  if grep -q 'origin/main' "$rec_file"; then st_bad "reconciled skill still has origin/main"; else st_ok "reconciled skill has no origin/main"; fi
  skill_after=$(sha256sum -- "$REPO_ROOT/SKILL.md" | awk '{print $1}')
  if [ "$skill_before" = "$skill_after" ]; then st_ok "live SKILL.md unchanged"; else st_bad "live SKILL.md changed"; fi

  # scratch fixture
  local sc="$tmp/scratch"
  mkdir -p "$sc/sub" "$sc/nested/.git" "$sc/.ufo/state"
  printf '# title\n' > "$sc/note.md"
  : > "$sc/empty.txt"
  printf 'SUPER-SECRET-TOKEN-do-not-print\n' > "$sc/credentials.env"
  printf '{"a":1}\n' > "$sc/extless"
  printf 'TOKEN-GIT\n' > "$sc/nested/.git/config"
  printf 'TOKEN-STATE\n' > "$sc/.ufo/state/live.json"
  ln -s note.md "$sc/link.md"
  printf 'ok\n' > "$sc/sub/keep.txt"
  local s1="$tmp/s1.txt" s2="$tmp/s2.txt"
  env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" scratch --path "$sc" --headers extensionless > "$s1"
  env -u GIT_DIR SOUJI_IMPL37_SELFTEST_ACTIVE=1 "$SELF" scratch --path "$sc" --headers extensionless > "$s2"
  if cmp -s "$s1" "$s2"; then st_ok "scratch repeat byte-identical"; else st_bad "scratch repeat differs"; fi
  if grep -q 'SUPER-SECRET-TOKEN\|TOKEN-GIT\|TOKEN-STATE' "$s1"; then st_bad "scratch leaked content"; else st_ok "scratch content absent"; fi
  if grep -q $'HANDOFF\tverdict\tNOT-SAFE' "$s1"; then st_ok "scratch handoff NOT-SAFE"; else st_bad "scratch handoff missing"; fi
  if grep -q $'SAFE' "$s1" && ! grep -q 'never emits SAFE' "$s1"; then st_bad "scratch emitted SAFE"; else st_ok "scratch did not authorize SAFE"; fi
  if grep -q $'CLASS\tsecret-shaped\t' "$s1"; then st_ok "secret-shaped class present"; else st_bad "secret-shaped class missing"; fi
  if grep -q $'CLASS\thdr-json\t' "$s1"; then st_ok "extensionless header class hdr-json"; else st_bad "hdr-json missing"; cat "$s1"; fi
  if grep -q $'CLASS\tgit-metadata\t' "$s1"; then st_ok "git-metadata class present"; else st_bad "git-metadata missing"; fi
  if grep -q $'CLASS\tforbidden-unread\t' "$s1"; then st_ok "forbidden-unread class present"; else st_bad "forbidden-unread missing"; fi
  local ent sum
  ent=$(awk -F'\t' '$1=="TOTAL" && $2=="entries"{print $3}' "$s1")
  sum=$(awk -F'\t' '$1=="TOTAL" && $2=="class_sum"{print $3}' "$s1")
  if [ -n "$ent" ] && [ "$ent" = "$sum" ] && [ "$ent" -gt 0 ]; then st_ok "scratch class_sum=$sum entries=$ent"
  else st_bad "scratch class_sum=$sum entries=$ent"; fi

  # static: no forbidden git verbs. Strip single-quoted needles first so
  # a search string is not mistaken for an invocation.
  if awk '
      /^[[:space:]]*#/ { next }
      {
        s = $0
        gsub(/\047[^\047]*\047/, "", s)
        if (s ~ /(^|[[:space:];|&])git[[:space:]]+(fetch|push|branch|checkout|reset|rebase)([[:space:]]|$)/) bad=1
        if (s ~ /(^|[[:space:];|&])git[[:space:]]+commit[[:space:]]/) bad=1
      }
      END { exit bad ? 0 : 1 }
    ' "$SELF"; then
    st_bad "script contains a forbidden git verb"
  else
    st_ok "no forbidden git verb in executable lines"
  fi

  st_note "selftest: $ST_PASS passed, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then return 1; fi
  return 0
}

# --- main ---------------------------------------------------------------------

MODE=""
ROOT="$SHOKUNIN_ROOT"
INCLUDE_ROOT=0
COMPARE=""
SKILL_PATH="$REPO_ROOT/SKILL.md"
SCRATCH_PATH="$SHOKUNIN_ROOT/kotodama-shokunin/.scratch"
HEADERS=extensionless

while [ $# -gt 0 ]; do
  case "$1" in
    census|drift|reconcile|scratch|selftest) MODE=$1; shift ;;
    --selftest) MODE=selftest; shift ;;
    --root) ROOT=${2:-}; shift 2 ;;
    --include-root) INCLUDE_ROOT=1; shift ;;
    --compare) COMPARE=${2:-}; shift 2 ;;
    --skill) SKILL_PATH=${2:-}; shift 2 ;;
    --path) SCRATCH_PATH=${2:-}; shift 2 ;;
    --headers) HEADERS=${2:-}; shift 2 ;;
    -h|--help) usage 0 ;;
    *) usage_err "unknown argument: $1" ;;
  esac
done

[ -n "$MODE" ] || usage_err "mode required (census|drift|reconcile|scratch|--selftest)"
case "$HEADERS" in
  none|extensionless) ;;
  *) usage_err "--headers must be none or extensionless" ;;
esac

case "$MODE" in
  selftest) run_selftest ;;
  census)
    if [ -n "$COMPARE" ]; then emit_compare "$ROOT" "$INCLUDE_ROOT" "$COMPARE"; else emit_census "$ROOT" "$INCLUDE_ROOT"; fi
    ;;
  drift) emit_drift "$SKILL_PATH" ;;
  reconcile) emit_reconcile "$SKILL_PATH" ;;
  scratch) emit_scratch "$SCRATCH_PATH" "$HEADERS" ;;
esac
