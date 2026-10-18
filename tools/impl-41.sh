#!/usr/bin/env bash
# impl-41 — round-6 census candidate (seat S41). Install name: tools/souji-census.sh.
#
# Three read-only jobs, one tool:
#   census     repeatable per-repo hygiene TSV (S33 column contract)
#   reconcile  SKILL.md + souji-verify.spec.md against the installed verifiers
#   classify   kotodama .scratch fully classed from metadata; headers <=200 bytes
#
# CLI
#   tools/impl-41.sh [--selftest] [--census] [--reconcile] [--classify]
#                    [--compare PREV.tsv] [--root DIR] [--classify-root DIR]
#                    [--json] [--help]
#
# No mode flag: census + reconcile + classify (handoff included).
# --census alone prints only the 7-column TSV (header + rows) so two idle
# runs are byte-comparable and --compare can read the file.
#
# Census columns
#   repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags
#   worktrees     `git worktree list` line count (main included)
#   unpushed      `git rev-list --count --branches --not --remotes`
#                 (local commit count + no-remote when refs/remotes is empty)
#   dirty         `git status --porcelain` line count
#   scratch_bytes `du -sb <repo>/.scratch` (0 if absent); does not follow links
#   mtime_iso     newest regular-file mtime, UTC, secret-shaped names skipped
#   verdict_flags comma-sorted subset of clean|dirty|unpushed|no-remote|
#                 scratch|secret-shaped|status-unverifiable|error
#                 clean only when unpushed=0, dirty=0, a remote-tracking ref
#                 exists, and no other flag fired
#
# --compare PREV.tsv
#   Re-census and emit DIFF rows for added/removed repos and for changes in
#   worktrees, unpushed, dirty, scratch_bytes, verdict_flags. mtime_iso
#   changes are INFO and do not fail the compare. Exit 0 match, 1 differ.
#
# Reconcile statuses: DRIFT, ALIGNED, ALIGNED-GAP. drift= count of DRIFT.
# ALIGNED-GAP is agreement on a known hole (hidden-ref sweep); it is not drift.
#
# Classify never follows symlinks, never opens secret-shaped paths, never
# opens .ufo/state or watchdog.log, never reads more than 200 bytes of a
# header, never writes the ledger. HANDOFF verdict is NOT-SAFE unless a
# receipt is actually proven — size is not a receipt.
#
# Exit: 0 evaluated / selftest pass; 1 selftest fail or measurement error;
# 2 usage. NOT-SAFE and DRIFT are results, not errors.
#
# Env: SHOKUNIN_ROOT, SOUJI_SKILL, SOUJI_SPEC, SOUJI_VERIFY, SOUJI_VAULT,
#      SOUJI_LIVE_LORE_WT, SOUJI_LIVE_GD2D_WT, SOUJI_LIVE_KOTO_BYTES.
# Dependencies: bash, coreutils, find, gawk, git. No network. No git
# fetch/push/commit/branch/checkout/reset/rebase/prune.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
export LC_ALL=C
export GIT_OPTIONAL_LOCKS=0

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"

CENSUS=0
RECONCILE=0
CLASSIFY=0
COMPARE=0
SELFTEST=0
JSON=0
COMPARE_FILE=""
CLASSIFY_ROOT=""
MODE_SET=0

HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'

usage() {
  local line
  while IFS= read -r line; do
    case "$line" in
      '#'*) line=${line#'#'}; line=${line#' '} ;;
      *) break ;;
    esac
    printf '%s\n' "$line"
  done < "$SELF"
  exit "${1:-0}"
}

usage_err() { printf 'impl-41: %s\n' "$1" >&2; usage 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; MODE_SET=1; shift ;;
    --census) CENSUS=1; MODE_SET=1; shift ;;
    --reconcile) RECONCILE=1; MODE_SET=1; shift ;;
    --classify) CLASSIFY=1; MODE_SET=1; shift ;;
    --compare)
      [ $# -ge 2 ] || usage_err '--compare needs a TSV path'
      COMPARE=1; MODE_SET=1; COMPARE_FILE=$2; shift 2 ;;
    --root)
      [ $# -ge 2 ] || usage_err '--root needs a directory'
      SHOKUNIN_ROOT=$2; shift 2 ;;
    --classify-root)
      [ $# -ge 2 ] || usage_err '--classify-root needs a directory'
      CLASSIFY_ROOT=$2; shift 2 ;;
    --json) JSON=1; shift ;;
    --help|-h) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown flag: $1" ;;
    *) usage_err "unexpected argument: $1" ;;
  esac
done
[ $# -eq 0 ] || usage_err "unexpected argument: $1"

if [ "$MODE_SET" = 0 ]; then
  CENSUS=1
  RECONCILE=1
  CLASSIFY=1
fi

# git_ro runs inspection commands only. Fixture setup in --selftest calls git
# directly inside its own mktemp and never goes through this function.
git_ro() {
  local sub repo
  if [ "${1:-}" = "-C" ]; then
    repo=${2:-}
    sub=${3:-}
    case "$sub" in
      fetch|push|commit|branch|checkout|reset|rebase|prune|clean|add|merge|switch|restore|rm|gc)
        printf 'impl-41: refused git %s\n' "$sub" >&2
        return 1
        ;;
      worktree)
        case "${4:-}" in
          list) ;;
          *) printf 'impl-41: refused git worktree %s\n' "${4:-}" >&2; return 1 ;;
        esac
        ;;
      status|rev-list|rev-parse|for-each-ref|worktree|log|show-ref|merge-base|diff)
        ;;
      *)
        printf 'impl-41: refused git %s\n' "$sub" >&2
        return 1
        ;;
    esac
    git "$@"
    return
  fi
  printf 'impl-41: refused git %s\n' "${1:-}" >&2
  return 1
}

is_secret_shaped() {
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    [ -n "$comp" ] || continue
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

is_repo_dir() {
  [ -d "$1/.git" ] || [ -f "$1/.git" ]
}

trim_ws() {
  local s=$1
  s=${s#"${s%%[![:space:]]*}"}
  s=${s%"${s##*[![:space:]]}"}
  printf '%s' "$s"
}

join_flags() {
  local f
  if [ $# -eq 0 ]; then
    printf 'clean'
    return
  fi
  printf '%s\n' "$@" | LC_ALL=C sort -u | paste -sd, -
}

list_repos() {
  local root=$1 d
  local -a kids=()
  shopt -s nullglob
  for d in "$root"/*/; do
    kids+=("${d%/}")
  done
  shopt -u nullglob
  [ "${#kids[@]}" -gt 0 ] || return 0
  printf '%s\n' "${kids[@]}" | LC_ALL=C sort | while IFS= read -r d; do
    if is_repo_dir "$d"; then
      printf '%s\n' "$d"
    fi
  done
}

# Prints "epoch\tsecretflag" (secretflag 1 if any secret-shaped regular file).
newest_mtime() {
  local repo=$1
  find "$repo" \
    \( -path "$repo/.git" -o -path "$repo/.git/*" \
       -o -path "$repo/.ufo/state" -o -path "$repo/.ufo/state/*" \
       -o -name 'watchdog.log' \) -prune \
    -o -type f -printf '%T@\t%P\n' 2>/dev/null \
    | awk '
      function secret(path,    n,i,parts,lc) {
        n = split(path, parts, "/")
        for (i = 1; i <= n; i++) {
          lc = tolower(parts[i])
          if (lc == "" ) continue
          if (lc == ".env" || lc == ".envrc") return 1
          if (lc ~ /\.env$/) return 1
          if (lc ~ /^\.env\./) return 1
          if (lc ~ /credential/ || lc ~ /secret/) return 1
          if (lc ~ /^id_/) return 1
          if (lc ~ /\.pem$/) return 1
        }
        return 0
      }
      secret($2) { sec = 1; next }
      $1+0 > best { best = $1+0 }
      END { printf "%.9f\t%d\n", best+0, sec+0 }
    '
}

epoch_iso() {
  local ep=$1
  if [ -z "$ep" ] || [ "$ep" = "0" ] || [ "$ep" = "0.000000000" ]; then
    printf '1970-01-01T00:00:00+00:00'
    return
  fi
  TZ=UTC date -d "@$ep" --iso-8601=seconds
}

census_one() {
  local repo=$1
  local wt=0 unpushed=0 dirty=0 scratch=0
  local wt_out st_out rem_out mt secret=0 epoch flags=()
  local nonempty=0

  if ! wt_out=$(git_ro -C "$repo" worktree list 2>/dev/null); then
    printf '%s\t0\t0\t0\t0\t1970-01-01T00:00:00+00:00\terror\n' "$repo"
    return 0
  fi
  if [ -n "$wt_out" ]; then
    wt=$(printf '%s\n' "$wt_out" | wc -l)
    wt=$(trim_ws "$wt")
  fi

  if rem_out=$(git_ro -C "$repo" for-each-ref --format='%(refname)' refs/remotes 2>/dev/null); then
    if [ -z "$rem_out" ]; then
      flags+=(no-remote)
      unpushed=$(git_ro -C "$repo" rev-list --count --branches 2>/dev/null || printf '0')
    else
      unpushed=$(git_ro -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null || printf '0')
    fi
  else
    flags+=(error)
    unpushed=0
  fi
  unpushed=$(trim_ws "$unpushed")

  if st_out=$(git_ro -C "$repo" status --porcelain 2>/dev/null); then
    if [ -n "$st_out" ]; then
      dirty=$(printf '%s\n' "$st_out" | wc -l)
      dirty=$(trim_ws "$dirty")
    fi
  else
    flags+=(status-unverifiable)
  fi

  if [ -d "$repo/.scratch" ] && [ ! -L "$repo/.scratch" ]; then
    scratch=$(du -sb -- "$repo/.scratch" 2>/dev/null | cut -f1 || printf '0')
    scratch=$(trim_ws "${scratch:-0}")
    if [ -n "$(find "$repo/.scratch" -mindepth 1 -print -quit 2>/dev/null)" ]; then
      nonempty=1
    fi
  fi

  mt=$(newest_mtime "$repo" || printf '0.000000000\t0')
  epoch=${mt%%$'\t'*}
  secret=${mt##*$'\t'}
  if [ "$secret" = 1 ]; then
    flags+=(secret-shaped)
  fi
  if [ "${unpushed:-0}" -gt 0 ] 2>/dev/null; then
    flags+=(unpushed)
  fi
  if [ "${dirty:-0}" -gt 0 ] 2>/dev/null; then
    flags+=(dirty)
  fi
  if [ "$nonempty" = 1 ]; then
    flags+=(scratch)
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$repo" "$wt" "${unpushed:-0}" "${dirty:-0}" "${scratch:-0}" \
    "$(epoch_iso "$epoch")" "$(join_flags "${flags[@]+"${flags[@]}"}")"
}

emit_census() {
  local root=$1 repo
  printf '%s\n' "$HEADER"
  while IFS= read -r repo; do
    [ -n "$repo" ] || continue
    census_one "$repo"
  done < <(list_repos "$root")
}

compare_census() {
  local root=$1 prev=$2
  local tmp now diff_n=0
  [ -f "$prev" ] || { printf 'impl-41: compare file missing: %s\n' "$prev" >&2; return 1; }
  tmp=$(mktemp)
  emit_census "$root" > "$tmp"
  awk -F'\t' -v oldf="$prev" -v newf="$tmp" '
    FNR==NR {
      if (FNR==1) next
      old[$1]=$0
      owt[$1]=$2; oun[$1]=$3; odi[$1]=$4; osc[$1]=$5; omt[$1]=$6; ofl[$1]=$7
      next
    }
    FNR==1 { next }
    {
      seen[$1]=1
      if (!($1 in old)) { printf "DIFF\t%s\trepo\tABSENT\tPRESENT\n", $1; d++; next }
      if (owt[$1]!=$2) printf "DIFF\t%s\tworktrees\t%s\t%s\n", $1, owt[$1], $2
      if (oun[$1]!=$3) printf "DIFF\t%s\tunpushed\t%s\t%s\n", $1, oun[$1], $3
      if (odi[$1]!=$4) printf "DIFF\t%s\tdirty\t%s\t%s\n", $1, odi[$1], $4
      if (osc[$1]!=$5) printf "DIFF\t%s\tscratch_bytes\t%s\t%s\n", $1, osc[$1], $5
      if (ofl[$1]!=$7) printf "DIFF\t%s\tverdict_flags\t%s\t%s\n", $1, ofl[$1], $7
      if (omt[$1]!=$6) printf "INFO\t%s\tmtime_iso\t%s\t%s\n", $1, omt[$1], $6
      if (owt[$1]!=$2 || oun[$1]!=$3 || odi[$1]!=$4 || osc[$1]!=$5 || ofl[$1]!=$7) d++
    }
    END {
      for (r in old) if (!(r in seen)) { printf "DIFF\t%s\trepo\tPRESENT\tABSENT\n", r; d++ }
      printf "COMPARE\tdiffs\t%d\n", d+0
      exit (d+0 > 0 ? 1 : 0)
    }
  ' "$prev" "$tmp"
  local rc=$?
  rm -f -- "$tmp"
  return "$rc"
}

# --- reconcile --------------------------------------------------------------

extract_fn() {
  local file=$1 name=$2 line in=0
  [ -f "$file" ] || return 0
  while IFS= read -r line; do
    if [ "$in" = 0 ]; then
      case "$line" in
        "$name()"*|"$name ()"*) in=1 ;;
      esac
      continue
    fi
    case "$line" in
      [a-zA-Z_]*"()"*) break ;;
    esac
    printf '%s\n' "$line"
  done < "$file"
}

noncomment_has() {
  local file=$1 word=$2 line
  [ -f "$file" ] || return 1
  while IFS= read -r line; do
    case "$line" in
      ''|[[:space:]]#*) continue ;;
    esac
    case "$line" in
      *"$word"*) return 0 ;;
    esac
  done < "$file"
  return 1
}

fn_has() {
  local file=$1 fn=$2 word=$3 body
  body=$(extract_fn "$file" "$fn")
  case "$body" in
    *"$word"*) return 0 ;;
  esac
  return 1
}

tool_executes_fetch() {
  local file=$1 line
  [ -f "$file" ] || return 1
  while IFS= read -r line; do
    case "$line" in
      ''|[[:space:]]#*) continue ;;
    esac
    case "$line" in
      *"git fetch"*|*"git_ro fetch"*) return 0 ;;
    esac
  done < "$file"
  return 1
}

normalize_doc_types() {
  local raw=$1
  raw=${raw//\`/}
  {
    case "$raw" in *'.scratch'*) printf 'scratch-dir\n' ;; esac
    case "$raw" in *'*.tmp'*) printf 'tmp\n' ;; esac
    case "$raw" in *'*.out'*) printf 'out\n' ;; esac
    case "$raw" in *'*.log'*) printf 'log\n' ;; esac
    case "$raw" in *'*-draft.'*) printf 'draft\n' ;; esac
    case "$raw" in *'out/'*) printf 'out-dir\n' ;; esac
    case "$raw" in *'reports/'*) printf 'reports-draft\n' ;; esac
    case "$raw" in *checkpoint*) printf 'checkpoint\n' ;; esac
  } | LC_ALL=C sort -u
}

normalize_tool_types() {
  local body=$1
  {
    case "$body" in *'.scratch'*) printf 'scratch-dir\n' ;; esac
    case "$body" in *'*.tmp'*) printf 'tmp\n' ;; esac
    case "$body" in *'*.out'*) printf 'out\n' ;; esac
    case "$body" in *'*.log'*) printf 'log\n' ;; esac
    case "$body" in *'*-draft.'*) printf 'draft\n' ;; esac
    case "$body" in *'checkpoint'*|*'launch-*.json'*) printf 'checkpoint\n' ;; esac
    case "$body" in *'"out"'*) printf 'out-dir\n' ;; esac
    case "$body" in *'reports/'*) printf 'reports-draft\n' ;; esac
  } | LC_ALL=C sort -u
}

size_to_bytes() {
  local tok=$1 n unit
  case "$tok" in
    bytes=*) tok=${tok#bytes=} ;;
    scratch_bytes=*) tok=${tok#scratch_bytes=} ;;
  esac
  case "$tok" in
    *B) n=${tok%B}; unit=B ;;
    *G) n=${tok%G}; unit=G ;;
    *M) n=${tok%M}; unit=M ;;
    *K) n=${tok%K}; unit=K ;;
    *) n=$tok; unit=B ;;
  esac
  case "$n" in
    ''|*[!0-9]*) printf '0'; return ;;
  esac
  case "$unit" in
    B) printf '%s' "$n" ;;
    K) printf '%s' $((n * 1024)) ;;
    M) printf '%s' $((n * 1024 * 1024)) ;;
    G) printf '%s' $((n * 1024 * 1024 * 1024)) ;;
  esac
}

row_matching() {
  local file=$1 needle=$2 line
  [ -f "$file" ] || return 0
  while IFS= read -r line; do
    case "$line" in
      *"$needle"*) printf '%s\n' "$line"; return 0 ;;
    esac
  done < "$file"
  return 0
}

first_int() {
  local s=$1 rest tok
  rest=${s#*:}
  rest=${rest#"${rest%%[![:space:]]*}"}
  for tok in $rest; do
    tok=${tok//[^0-9]/}
    if [ -n "$tok" ]; then
      printf '%s' "$tok"
      return
    fi
  done
  printf ''
}

size_token() {
  local s=$1 tok
  for tok in $s; do
    tok=${tok//\`/}
    tok=${tok%,}
    tok=${tok%.}
    case "$tok" in
      scratch_bytes=*|bytes=*|[0-9]*G|[0-9]*M|[0-9]*K|[0-9]*B) printf '%s' "$tok"; return ;;
    esac
  done
  printf ''
}

emit_rec() {
  printf 'RECONCILE\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4"
}

reconcile() {
  local skill=${SOUJI_SKILL:-$REPO_ROOT/SKILL.md}
  local spec=${SOUJI_SPEC:-$REPO_ROOT/tools/souji-verify.spec.md}
  local verify=${SOUJI_VERIFY:-$REPO_ROOT/tools/souji-verify.sh}
  local vault=${SOUJI_VAULT:-$REPO_ROOT/tools/souji-vault-verify.sh}
  local root=$SHOKUNIN_ROOT
  local pushed stale lore gd2d koto
  local doc_types tool_types missing extra body
  local drift=0 aligned=0 gaps=0
  local lore_live gd2d_live koto_live claimed unit_bytes
  local spec_line allow_hit="" f

  if [ ! -f "$skill" ]; then
    emit_rec skill-missing DRIFT doc-tool "missing $skill"
    printf 'RECONCILE-SUMMARY\tdrift\t1\taligned\t0\tgaps\t0\n'
    return 0
  fi

  pushed=$(row_matching "$skill" '| `pushed` |')
  [ -n "$pushed" ] || pushed=$(row_matching "$skill" '| pushed |')
  stale=$(row_matching "$skill" '| `stale` |')
  [ -n "$stale" ] || stale=$(row_matching "$skill" '| stale |')

  if [[ "$pushed" == *'git fetch'* ]]; then
    if tool_executes_fetch "$verify" || tool_executes_fetch "$vault"; then
      emit_rec pushed-fetch ALIGNED doc-tool 'doc requires fetch and a tool executes it'
      aligned=$((aligned + 1))
    else
      emit_rec pushed-fetch DRIFT doc-tool 'SKILL pushed row requires git fetch; installed tools forbid it and do not execute it'
      drift=$((drift + 1))
    fi
  else
    if tool_executes_fetch "$verify" || tool_executes_fetch "$vault"; then
      emit_rec pushed-fetch DRIFT doc-tool 'doc does not require fetch but a tool executes git fetch'
      drift=$((drift + 1))
    else
      emit_rec pushed-fetch ALIGNED doc-tool 'neither SKILL pushed row nor installed tools execute git fetch'
      aligned=$((aligned + 1))
    fi
  fi

  if [[ "$pushed" == *'origin/main'* ]]; then
    if fn_has "$verify" resolve_default_ref 'origin/main'; then
      emit_rec pushed-origin-main ALIGNED doc-tool 'doc and resolve_default_ref both hardcode origin/main'
      aligned=$((aligned + 1))
    else
      emit_rec pushed-origin-main DRIFT doc-tool 'SKILL counting command hardcodes origin/main; resolve_default_ref uses refs/remotes/origin/HEAD and refuses a local-master fallback'
      drift=$((drift + 1))
    fi
  else
    emit_rec pushed-origin-main ALIGNED doc-tool 'SKILL pushed row does not hardcode origin/main'
    aligned=$((aligned + 1))
  fi

  doc_types=$(normalize_doc_types "$stale")
  body=$(extract_fn "$verify" scratch_type)
  tool_types=$(normalize_tool_types "$body")
  missing=$(comm -23 <(printf '%s\n' "$doc_types") <(printf '%s\n' "$tool_types") | paste -sd, -)
  extra=$(comm -13 <(printf '%s\n' "$doc_types") <(printf '%s\n' "$tool_types") | paste -sd, -)
  if [ -z "$missing" ] && [ -z "$extra" ] && [ -n "$tool_types" ]; then
    emit_rec stale-types ALIGNED doc-tool "types=$(printf '%s' "$tool_types" | paste -sd, -)"
    aligned=$((aligned + 1))
  else
    emit_rec stale-types DRIFT doc-tool "doc-only=${missing:-none} tool-only=${extra:-none}"
    drift=$((drift + 1))
  fi

  if grep -q 'symlink-present' "$spec" "$verify" "$vault" 2>/dev/null; then
    :
  fi
  local tool_sym=0 doc_sym=0
  if [ -f "$spec" ] && [[ $(cat "$spec") == *'symlink-present'* ]]; then tool_sym=1; fi
  if [[ $(cat "$verify") == *'symlink-present'* ]]; then tool_sym=1; fi
  if [[ $(cat "$skill") == *'symlink'* ]]; then doc_sym=1; fi
  if [ "$tool_sym" = 1 ] && [ "$doc_sym" = 0 ]; then
    emit_rec symlink-doc DRIFT doc-tool 'tools/spec fail closed on symlink-present; SKILL.md never mentions symlink'
    drift=$((drift + 1))
  elif [ "$tool_sym" = 1 ] && [ "$doc_sym" = 1 ]; then
    emit_rec symlink-doc ALIGNED doc-tool 'SKILL mentions symlink and tools implement symlink-present'
    aligned=$((aligned + 1))
  else
    emit_rec symlink-doc ALIGNED doc-tool 'no symlink-present claim on the tool side'
    aligned=$((aligned + 1))
  fi

  local hidden_doc=0 hidden_tool=0
  if [[ "$stale" == *'--hidden'* ]] || [[ $(cat "$skill") == *'--hidden'* ]]; then hidden_doc=1; fi
  if fn_has "$verify" count_live_refs '--hidden'; then hidden_tool=1; fi
  if [ "$hidden_doc" = "$hidden_tool" ]; then
    emit_rec hidden-sweep ALIGNED-GAP doc-tool "doc_hidden=$hidden_doc tool_hidden=$hidden_tool (r5 false-SAFE class if both 0; not a docs/tools disagreement)"
    gaps=$((gaps + 1))
  else
    emit_rec hidden-sweep DRIFT doc-tool "doc_hidden=$hidden_doc tool_hidden=$hidden_tool"
    drift=$((drift + 1))
  fi

  spec_line=$(row_matching "$spec" 'bash + coreutils')
  if [[ "$spec_line" == *'only'* ]]; then
    allow_hit=""
    for f in "$verify" "$vault"; do
      [ -f "$f" ] || continue
      if noncomment_has "$f" 'grep '; then allow_hit+=" grep:${f##*/}"; fi
      if noncomment_has "$f" 'find '; then allow_hit+=" find:${f##*/}"; fi
      if noncomment_has "$f" 'xargs'; then allow_hit+=" xargs:${f##*/}"; fi
    done
    if [ -n "$allow_hit" ]; then
      emit_rec spec-allowlist DRIFT doc-tool "spec allowlist is bash+coreutils+git+rg; tools also use:${allow_hit}"
      drift=$((drift + 1))
    else
      emit_rec spec-allowlist ALIGNED doc-tool 'no grep/find/xargs on non-comment tool lines'
      aligned=$((aligned + 1))
    fi
  else
    emit_rec spec-allowlist ALIGNED doc-tool 'spec has no exclusive allowlist sentence'
    aligned=$((aligned + 1))
  fi

  if [ -f "$spec" ] && [[ $(cat "$spec") == *'--basename'* ]]; then
    if fn_has "$verify" count_live_refs '--basename'; then
      emit_rec spec-rg-basename ALIGNED doc-tool 'spec and tool both pass --basename'
      aligned=$((aligned + 1))
    else
      emit_rec spec-rg-basename DRIFT doc-tool 'spec names rg --basename (not a ripgrep flag); tool uses --fixed-strings'
      drift=$((drift + 1))
    fi
  fi

  if [ -n "${SOUJI_LIVE_LORE_WT:-}" ]; then
    lore_live=$SOUJI_LIVE_LORE_WT
  elif [ -d "$root/lore-shokunin" ]; then
    lore_live=$(git_ro -C "$root/lore-shokunin" worktree list 2>/dev/null | wc -l)
    lore_live=$(trim_ws "$lore_live")
  else
    lore_live=""
  fi
  if [ -n "${SOUJI_LIVE_GD2D_WT:-}" ]; then
    gd2d_live=$SOUJI_LIVE_GD2D_WT
  elif [ -d "$root/game-dev-2d-shokunin" ]; then
    gd2d_live=$(git_ro -C "$root/game-dev-2d-shokunin" worktree list 2>/dev/null | wc -l)
    gd2d_live=$(trim_ws "$gd2d_live")
  else
    gd2d_live=""
  fi
  if [ -n "${SOUJI_LIVE_KOTO_BYTES:-}" ]; then
    koto_live=$SOUJI_LIVE_KOTO_BYTES
  elif [ -d "$root/kotodama-shokunin/.scratch" ]; then
    koto_live=$(du -sb -- "$root/kotodama-shokunin/.scratch" | cut -f1)
    koto_live=$(trim_ws "$koto_live")
  else
    koto_live=""
  fi

  lore=$(row_matching "$skill" 'lore-shokunin:')
  if [ -n "$lore" ] && [ -n "$lore_live" ]; then
    claimed=$(first_int "$lore")
    if [[ "$lore" == *prunable* ]]; then
      claimed_cmp=$((lore_live - 1))
    else
      claimed_cmp=$lore_live
    fi
    if [ -n "$claimed" ] && [ "$claimed" = "$claimed_cmp" ]; then
      emit_rec surface-lore ALIGNED doc-live "doc=$claimed live_worktrees=$lore_live"
      aligned=$((aligned + 1))
    else
      emit_rec surface-lore DRIFT doc-live "doc_line claims $claimed; git worktree list lines=$lore_live"
      drift=$((drift + 1))
    fi
  elif [ -z "$lore" ]; then
    emit_rec surface-lore ALIGNED doc-live 'no numeric lore worktree claim'
    aligned=$((aligned + 1))
  fi

  gd2d=$(row_matching "$skill" 'game-dev-2d-shokunin:')
  if [ -n "$gd2d" ] && [ -n "$gd2d_live" ]; then
    claimed=$(first_int "$gd2d")
    if [[ "$gd2d" == *prunable* ]]; then
      claimed_cmp=$((gd2d_live - 1))
    else
      claimed_cmp=$gd2d_live
    fi
    if [ -n "$claimed" ] && [ "$claimed" = "$claimed_cmp" ]; then
      emit_rec surface-gd2d ALIGNED doc-live "doc=$claimed live_worktrees=$gd2d_live"
      aligned=$((aligned + 1))
    else
      emit_rec surface-gd2d DRIFT doc-live "doc_line claims $claimed; git worktree list lines=$gd2d_live"
      drift=$((drift + 1))
    fi
  elif [ -z "$gd2d" ]; then
    emit_rec surface-gd2d ALIGNED doc-live 'no numeric gd2d worktree claim'
    aligned=$((aligned + 1))
  fi

  koto=$(row_matching "$skill" 'kotodama-shokunin:')
  if [ -n "$koto" ] && [ -n "$koto_live" ]; then
    local stok
    stok=$(size_token "$koto")
    if [ -n "$stok" ]; then
      unit_bytes=$(size_to_bytes "$stok")
      if [ "$unit_bytes" = "$koto_live" ]; then
        emit_rec surface-kotodama ALIGNED doc-live "doc=$stok live_bytes=$koto_live"
        aligned=$((aligned + 1))
      else
        emit_rec surface-kotodama DRIFT doc-live "doc=$stok (${unit_bytes}B) live du -sb=$koto_live"
        drift=$((drift + 1))
      fi
    else
      emit_rec surface-kotodama ALIGNED doc-live 'kotodama line has no size token'
      aligned=$((aligned + 1))
    fi
  elif [ -z "$koto" ]; then
    emit_rec surface-kotodama ALIGNED doc-live 'no kotodama scratch size claim'
    aligned=$((aligned + 1))
  fi

  printf 'RECONCILE-SUMMARY\tdrift\t%s\taligned\t%s\tgaps\t%s\n' "$drift" "$aligned" "$gaps"
  RECONCILE_DRIFT=$drift
}

# --- classify ---------------------------------------------------------------

classify_header() {
  local f=$1 n=0 sig raw stripped class
  if is_secret_shaped "$f"; then
    printf 'secret-shaped\t0\n'
    return
  fi
  case "$f" in
    */.ufo/state|*/.ufo/state/*|*/watchdog.log)
      printf 'off-limits\t0\n'
      return
      ;;
  esac
  n=$(head -c 200 -- "$f" 2>/dev/null | wc -c | tr -d ' ')
  n=${n:-0}
  if [ "$n" -eq 0 ]; then
    printf 'empty\t0\n'
    return
  fi
  sig=$(head -c 8 -- "$f" 2>/dev/null | od -An -tx1 | tr -d ' \n')
  case "$sig" in
    25504446*) printf 'header-pdf\t%s\n' "$n"; return ;;
    89504e47*) printf 'header-png\t%s\n' "$n"; return ;;
    ffd8ff*) printf 'header-jpeg\t%s\n' "$n"; return ;;
    1f8b*) printf 'header-gzip\t%s\n' "$n"; return ;;
    504b0304*|504b0506*) printf 'header-zip\t%s\n' "$n"; return ;;
    7f454c46*) printf 'header-elf\t%s\n' "$n"; return ;;
  esac
  raw=$(head -c 200 -- "$f" 2>/dev/null | wc -c | tr -d ' ')
  stripped=$(head -c 200 -- "$f" 2>/dev/null | tr -d '\0' | wc -c | tr -d ' ')
  if [ "$raw" != "$stripped" ]; then
    class=header-binary
  else
    class=header-text
  fi
  printf '%s\t%s\n' "$class" "$n"
}

classify_tree() {
  local root=$1
  local tmp need class path bytes
  HEADER_MAX=0
  HEADER_SAMPLED=0
  if [ ! -d "$root" ]; then
    printf 'CLASS-PROOF\tentries\t0\tclassified\t0\tunclassified\t0\theader_cap\t200\theader_max_read\t0\theader_sampled\t0\n'
    printf 'HANDOFF\tpath\t%s\n' "$root"
    printf 'HANDOFF\tverdict\tNOT-SAFE\n'
    printf 'HANDOFF\treceipt\tunreachable\n'
    printf 'HANDOFF\taction\tdo-not-prune\n'
    return 0
  fi
  tmp=$(mktemp)
  find "$root" -mindepth 1 \
    \( -path "$root/.ufo/state" -o -path "$root/.ufo/state/*" -o -name 'watchdog.log' \) \
      -printf 'X\t%s\t%P\n' -prune \
    -o -printf '%y\t%s\t%P\n' 2>/dev/null \
    | awk -v out="$tmp" '
      function secret(path,    n,i,parts,lc) {
        n = split(path, parts, "/")
        for (i = 1; i <= n; i++) {
          lc = tolower(parts[i])
          if (lc == "") continue
          if (lc == ".env" || lc == ".envrc") return 1
          if (lc ~ /\.env$/) return 1
          if (lc ~ /^\.env\./) return 1
          if (lc ~ /credential/ || lc ~ /secret/) return 1
          if (lc ~ /^id_/) return 1
          if (lc ~ /\.pem$/) return 1
        }
        return 0
      }
      function extclass(name,    ext,i) {
        if (name ~ /^\.[^.]+$/) return "dotfile"
        i = match(name, /\.[^.]+$/)
        if (i == 0) return ""
        ext = tolower(substr(name, i+1))
        if (ext ~ /^(md|markdown)$/) return "text-md"
        if (ext ~ /^(json|jsonl)$/) return "text-json"
        if (ext ~ /^(yml|yaml)$/) return "text-yaml"
        if (ext == "txt") return "text-txt"
        if (ext == "py") return "text-py"
        if (ext ~ /^(sh|bash)$/) return "text-sh"
        if (ext ~ /^(html|htm)$/) return "text-html"
        if (ext == "xml") return "text-xml"
        if (ext ~ /^(log|err|stderr|stdout)$/) return "text-log"
        if (ext == "out") return "text-out"
        if (ext ~ /^(tsv|csv)$/) return "text-tsv"
        if (ext == "pdf") return "data-pdf"
        if (ext ~ /^(jpg|jpeg|png|gif|webp)$/) return "data-image"
        if (ext ~ /^(gz|tgz|zip)$/) return "data-archive"
        if (ext ~ /^(pyc|pyo|so|o)$/) return "data-bytecode"
        if (ext ~ /^(bin|raw)$/) return "data-bin"
        if (ext == "torrent") return "data-torrent"
        if (ext ~ /^(pack|idx|rev)$/) return "git-pack"
        if (ext ~ /^[a-z0-9_+-]+$/) return "ext-" ext
        return "ext-other"
      }
      function add(c, b) { count[c]++; bytes[c]+=b; classified++ }
      {
        entries++
        kind=$1; sz=$2+0; path=$3
        name=path; sub("^.*/","",name)
        if (kind == "X") { add("off-limits", sz); next }
        if (secret(path)) { add("secret-shaped", sz); next }
        if (kind == "l") { add("symlink", sz); next }
        if (kind == "d") { add("dir", sz); next }
        if (kind != "f") { add("non-regular", sz); next }
        if (path ~ /(^|\/)\.git(\/|$)/) { add("git-metadata", sz); next }
        c = extclass(name)
        if (c != "") { add(c, sz); next }
        if (sz == 0) { add("empty", 0); next }
        print path >> out
        need++
        pending[need]=path
        psz[need]=sz
      }
      END {
        for (c in count) printf "COUNT\t%s\t%d\t%d\n", c, count[c], bytes[c]
        printf "PROOF\t%d\t%d\t%d\n", entries+0, classified+0, need+0
      }
    '
  local proof entries classified need
  proof=$(awk -F'\t' '$1=="PROOF"{print $2" "$3" "$4}' "$tmp.wait" 2>/dev/null || true)
  # The awk above wrote COUNT/PROOF to stdout mixed with the pipe consumer.
  # Re-run is avoided: the pipe already printed COUNT/PROOF to our stdout if
  # we did not capture it. Capture properly instead.
  rm -f -- "$tmp"
  return 0
}

# classify_tree above is replaced by classify_tree_capture — the first
# definition is intentionally unused. The live function is below.
classify_tree() {
  local root=$1
  local raw counts needf
  local entries=0 pre=0 need=0
  HEADER_MAX=0
  HEADER_SAMPLED=0
  if [ ! -e "$root" ]; then
    printf 'CLASS-PROOF\tentries\t0\tclassified\t0\tunclassified\t0\theader_cap\t200\theader_max_read\t0\theader_sampled\t0\n'
    printf 'HANDOFF\tpath\t%s\n' "$root"
    printf 'HANDOFF\tverdict\tNOT-SAFE\n'
    printf 'HANDOFF\treceipt\tunreachable\n'
    printf 'HANDOFF\taction\tdo-not-prune\n'
    printf 'HANDOFF\tnote\tclassify root absent; nothing removed\n'
    return 0
  fi
  raw=$(mktemp)
  needf=$(mktemp)
  find "$root" -mindepth 1 \
    \( -path "$root/.ufo/state" -o -path "$root/.ufo/state/*" -o -name 'watchdog.log' \) \
      -printf 'X\t%s\t%P\n' -prune \
    -o -printf '%y\t%s\t%P\n' 2>/dev/null \
    | awk -v needf="$needf" '
      function secret(path,    n,i,parts,lc) {
        n = split(path, parts, "/")
        for (i = 1; i <= n; i++) {
          lc = tolower(parts[i])
          if (lc == "") continue
          if (lc == ".env" || lc == ".envrc") return 1
          if (lc ~ /\.env$/) return 1
          if (lc ~ /^\.env\./) return 1
          if (lc ~ /credential/ || lc ~ /secret/) return 1
          if (lc ~ /^id_/) return 1
          if (lc ~ /\.pem$/) return 1
        }
        return 0
      }
      function extclass(name,    ext,i) {
        if (name ~ /^\.[^.]+$/) return "dotfile"
        i = match(name, /\.[^.]+$/)
        if (i == 0) return ""
        ext = tolower(substr(name, i+1))
        if (ext ~ /^(md|markdown)$/) return "text-md"
        if (ext ~ /^(json|jsonl)$/) return "text-json"
        if (ext ~ /^(yml|yaml)$/) return "text-yaml"
        if (ext == "txt") return "text-txt"
        if (ext == "py") return "text-py"
        if (ext ~ /^(sh|bash)$/) return "text-sh"
        if (ext ~ /^(html|htm)$/) return "text-html"
        if (ext == "xml") return "text-xml"
        if (ext ~ /^(log|err|stderr|stdout)$/) return "text-log"
        if (ext == "out") return "text-out"
        if (ext ~ /^(tsv|csv)$/) return "text-tsv"
        if (ext == "pdf") return "data-pdf"
        if (ext ~ /^(jpg|jpeg|png|gif|webp)$/) return "data-image"
        if (ext ~ /^(gz|tgz|zip)$/) return "data-archive"
        if (ext ~ /^(pyc|pyo|so|o)$/) return "data-bytecode"
        if (ext ~ /^(bin|raw)$/) return "data-bin"
        if (ext == "torrent") return "data-torrent"
        if (ext ~ /^(pack|idx|rev)$/) return "git-pack"
        if (ext ~ /^[a-z0-9_+-]+$/) return "ext-" ext
        return "ext-other"
      }
      function add(c, b) { count[c]++; bytes[c]+=b; classified++ }
      {
        entries++
        kind=$1; sz=$2+0; path=$3
        name=path; sub("^.*/","",name)
        if (kind == "X") { add("off-limits", sz); next }
        if (secret(path)) { add("secret-shaped", sz); next }
        if (kind == "l") { add("symlink", sz); next }
        if (kind == "d") { add("dir", sz); next }
        if (kind != "f") { add("non-regular", sz); next }
        if (path ~ /(^|\/)\.git(\/|$)/) { add("git-metadata", sz); next }
        c = extclass(name)
        if (c != "") { add(c, sz); next }
        if (sz == 0) { add("empty", 0); next }
        printf "%s\t%d\n", path, sz >> needf
        need++
      }
      END {
        for (c in count) printf "COUNT\t%s\t%d\t%d\n", c, count[c], bytes[c]
        printf "PROOF\t%d\t%d\t%d\n", entries+0, classified+0, need+0
      }
    ' > "$raw"

  entries=$(awk -F'\t' '$1=="PROOF"{print $2}' "$raw")
  pre=$(awk -F'\t' '$1=="PROOF"{print $3}' "$raw")
  need=$(awk -F'\t' '$1=="PROOF"{print $4}' "$raw")
  entries=${entries:-0}
  pre=${pre:-0}
  need=${need:-0}

  if [ -s "$needf" ]; then
    while IFS=$'\t' read -r rel sz; do
      [ -n "$rel" ] || continue
      if is_secret_shaped "$rel"; then
        class=secret-shaped
      else
        local nbytes=0
        IFS=$'\t' read -r class nbytes < <(classify_header "$root/$rel")
        HEADER_SAMPLED=$((HEADER_SAMPLED + 1))
        if [ "${nbytes:-0}" -gt "${HEADER_MAX:-0}" ]; then HEADER_MAX=$nbytes; fi
      fi
      printf 'COUNT\t%s\t1\t%s\n' "$class" "${sz:-0}" >> "$raw"
    done < "$needf"
  fi

  awk -F'\t' '
    $1=="COUNT" { c[$2]+=$3; b[$2]+=$4; n+=$3 }
    END {
      for (k in c) printf "CLASS\t%s\t%d\t%d\n", k, c[k], b[k]
      printf "CLASS-SUM\t%d\n", n+0
    }
  ' "$raw" | LC_ALL=C sort

  local summed unclassified
  summed=$(awk -F'\t' '$1=="COUNT"{n+=$3} END{print n+0}' "$raw")
  unclassified=$((entries - summed))
  if [ "$unclassified" -lt 0 ]; then unclassified=0; fi
  printf 'CLASS-PROOF\tentries\t%s\tclassified\t%s\tunclassified\t%s\theader_cap\t200\theader_max_read\t%s\theader_sampled\t%s\n' \
    "$entries" "$summed" "$unclassified" "${HEADER_MAX:-0}" "${HEADER_SAMPLED:-0}"
  rm -f -- "$raw" "$needf"
  CLASS_ENTRIES=$entries
  CLASS_SUM=$summed
  CLASS_UNCLASS=$unclassified
}

emit_handoff() {
  local root=$1 scratch=$2
  local lane unpushed=0 dirty=0 bytes=0
  lane=$(basename -- "$(dirname -- "$scratch")")
  if [ -d "$root/$lane" ] && is_repo_dir "$root/$lane"; then
    unpushed=$(git_ro -C "$root/$lane" rev-list --count --branches --not --remotes 2>/dev/null || printf '0')
    unpushed=$(trim_ws "$unpushed")
    local st
    st=$(git_ro -C "$root/$lane" status --porcelain 2>/dev/null || true)
    if [ -n "$st" ]; then
      dirty=$(printf '%s\n' "$st" | wc -l)
      dirty=$(trim_ws "$dirty")
    fi
  fi
  if [ -d "$scratch" ]; then
    bytes=$(du -sb -- "$scratch" | cut -f1)
    bytes=$(trim_ws "$bytes")
  fi
  printf 'HANDOFF\tlane\t%s\n' "$lane"
  printf 'HANDOFF\tpath\t%s\n' "$scratch"
  printf 'HANDOFF\tverdict\tNOT-SAFE\n'
  printf 'HANDOFF\treceipt\tnone\n'
  printf 'HANDOFF\tunpushed\t%s\n' "${unpushed:-0}"
  printf 'HANDOFF\tdirty\t%s\n' "${dirty:-0}"
  printf 'HANDOFF\tscratch_bytes\t%s\n' "${bytes:-0}"
  printf 'HANDOFF\tunclassified\t%s\n' "${CLASS_UNCLASS:-0}"
  printf 'HANDOFF\theader_cap\t200\n'
  printf 'HANDOFF\theader_max_read\t%s\n' "${HEADER_MAX:-0}"
  printf 'HANDOFF\tsymlinks_followed\t0\n'
  printf 'HANDOFF\tsecret_bytes_read\t0\n'
  printf 'HANDOFF\tledger_touched\t0\n'
  printf 'HANDOFF\taction\tdo-not-prune\n'
  printf 'HANDOFF\tnote\tOwning lane measured unpushed=%s dirty=%s. Size is not a receipt. Symlinks were not followed. Secret-shaped names were not opened. .ufo/state and watchdog.log were not opened. No ledger write, quarantine, or removal was performed. Operator disposition only after lane work settles and a receipt exists.\n' \
    "${unpushed:-0}" "${dirty:-0}"
}

pin_files() {
  local f
  for f in \
    "${SOUJI_SKILL:-$REPO_ROOT/SKILL.md}" \
    "${SOUJI_SPEC:-$REPO_ROOT/tools/souji-verify.spec.md}" \
    "${SOUJI_VERIFY:-$REPO_ROOT/tools/souji-verify.sh}" \
    "${SOUJI_VAULT:-$REPO_ROOT/tools/souji-vault-verify.sh}"
  do
    if [ -f "$f" ]; then
      printf 'PIN\t%s\t%s\n' "$f" "$(sha256sum -- "$f" | cut -d' ' -f1)"
    else
      printf 'PIN\t%s\tMISSING\n' "$f"
    fi
  done
}

run_modes() {
  local root=$1
  local scratch=${CLASSIFY_ROOT:-$root/kotodama-shokunin/.scratch}
  local census_only=0
  if [ "$CENSUS" = 1 ] && [ "$RECONCILE" = 0 ] && [ "$CLASSIFY" = 0 ] && [ "$COMPARE" = 0 ]; then
    census_only=1
  fi
  if [ "$COMPARE" = 1 ]; then
    compare_census "$root" "$COMPARE_FILE"
    return
  fi
  if [ "$census_only" = 1 ]; then
    emit_census "$root"
    return
  fi
  if [ "$CENSUS" = 1 ]; then
    printf '## census\n'
    emit_census "$root"
  fi
  if [ "$RECONCILE" = 1 ]; then
    printf '## reconcile\n'
    pin_files
    reconcile
  fi
  if [ "$CLASSIFY" = 1 ]; then
    printf '## classify\n'
    classify_tree "$scratch"
    printf '## handoff\n'
    emit_handoff "$root" "$scratch"
  fi
  if [ "$JSON" = 1 ]; then
    printf 'SUMMARY-JSON\t{"drift":%s,"unclassified":%s,"header_max_read":%s}\n' \
      "${RECONCILE_DRIFT:-0}" "${CLASS_UNCLASS:-0}" "${HEADER_MAX:-0}"
  fi
}

# --- selftest ---------------------------------------------------------------

st_fail=0
st_note() { printf 'SELFTEST\tFAIL\t%s\n' "$1" >&2; st_fail=1; }
st_ok() { printf 'SELFTEST\tPASS\t%s\n' "$1"; }

selftest() {
  local tmp fleet alpha beta scratch
  tmp=$(mktemp -d /tmp/impl-41-selftest.XXXXXX)
  fleet=$tmp/fleet
  alpha=$fleet/alpha-shokunin
  beta=$fleet/beta-shokunin
  scratch=$fleet/kotodama-shokunin/.scratch
  mkdir -p "$alpha" "$beta/.ufo/state" "$beta/.scratch" "$beta/credentials" \
    "$scratch/sub" "$scratch/.ufo/state" "$scratch/verify/.git" "$fleet/kotodama-shokunin"

  git -C "$alpha" init -q -b master
  printf 'alpha\n' > "$alpha/keep.txt"
  git -C "$alpha" -c user.email=souji@shokunin.local -c user.name=souji add keep.txt
  git -C "$alpha" -c user.email=souji@shokunin.local -c user.name=souji commit -q -m init
  git -C "$alpha" update-ref refs/remotes/origin/master HEAD
  git -C "$alpha" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

  git -C "$beta" init -q -b master
  printf 'beta\n' > "$beta/keep.txt"
  git -C "$beta" -c user.email=souji@shokunin.local -c user.name=souji add keep.txt
  git -C "$beta" -c user.email=souji@shokunin.local -c user.name=souji commit -q -m init
  printf 'dirty\n' > "$beta/dirty.txt"
  mkdir -p "$beta/.scratch" "$beta/credentials"
  printf 'scratch\n' > "$beta/.scratch/note.out"
  printf 'SECRETTOKEN41\n' > "$beta/credentials/fake.env"
  printf 'STATETOKEN41\n' > "$beta/.ufo/state/live.json"
  printf 'WATCHTOKEN41\n' > "$beta/.ufo/watchdog.log"

  printf 'hello md\n' > "$scratch/note.md"
  : > "$scratch/empty.out"
  printf 'plain text header\n' > "$scratch/noext"
  dd if=/dev/zero bs=200 count=1 of="$scratch/blob" status=none
  printf 'PAST200MARKER' >> "$scratch/blob"
  printf 'TARGETTOKEN41\n' > "$tmp/outside-target"
  ln -s "$tmp/outside-target" "$scratch/link.md"
  printf 'SECRETTOKEN41\n' > "$scratch/outside-secret.txt"
  printf 'SECRETTOKEN41\n' > "$scratch/sub/fake.env"
  printf 'STATETOKEN41\n' > "$scratch/.ufo/state/x"
  printf 'WATCHTOKEN41\n' > "$scratch/.ufo/watchdog.log"
  mkdir -p "$scratch/verify/.git"
  printf 'gitmeta\n' > "$scratch/verify/.git/description"

  # refusal
  local refused=0
  if git_ro fetch >/dev/null 2>&1; then st_note 'git_ro fetch was not refused'; else refused=$((refused+1)); fi
  if git_ro -C "$alpha" push >/dev/null 2>&1; then st_note 'git_ro push was not refused'; else refused=$((refused+1)); fi
  if git_ro -C "$alpha" prune >/dev/null 2>&1; then st_note 'git_ro prune was not refused'; else refused=$((refused+1)); fi
  if git_ro -C "$alpha" worktree prune >/dev/null 2>&1; then st_note 'git_ro worktree prune was not refused'; else refused=$((refused+1)); fi
  [ "$refused" = 4 ] && st_ok 'git_ro refuses fetch/push/prune'

  local c1 c2
  c1=$tmp/c1.tsv
  c2=$tmp/c2.tsv
  SHOKUNIN_ROOT=$fleet emit_census "$fleet" > "$c1"
  SHOKUNIN_ROOT=$fleet emit_census "$fleet" > "$c2"
  if cmp -s "$c1" "$c2"; then st_ok 'census repeat byte-identical'; else st_note 'census repeat differed'; fi
  if [[ $(cat "$c1") == *SECRETTOKEN41* || $(cat "$c1") == *STATETOKEN41* || $(cat "$c1") == *WATCHTOKEN41* ]]; then
    st_note 'census leaked a planted token'
  else
    st_ok 'census output has no planted secret/state tokens'
  fi
  if [[ $(cat "$c1") == *secret-shaped* ]]; then st_ok 'census flags secret-shaped'; else st_note 'census missed secret-shaped'; fi
  local alpha_flags
  alpha_flags=$(awk -F'\t' -v p="$alpha" '$1==p{print $7}' "$c1")
  if [ "$alpha_flags" = "clean" ]; then st_ok 'clean pushed repo flags=clean'; else st_note "alpha flags=$alpha_flags"; fi
  local beta_flags
  beta_flags=$(awk -F'\t' -v p="$beta" '$1==p{print $7}' "$c1")
  case "$beta_flags" in
    *dirty*|*no-remote*|*scratch*|*secret-shaped*) st_ok "beta flags=$beta_flags" ;;
    *) st_note "beta flags incomplete: $beta_flags" ;;
  esac

  printf 'more\n' >> "$alpha/keep.txt"
  local cmp_out cmp_rc
  set +e
  cmp_out=$(SHOKUNIN_ROOT=$fleet compare_census "$fleet" "$c1" 2>&1)
  cmp_rc=$?
  set -e
  if [ "$cmp_rc" = 1 ] && [[ "$cmp_out" == *DIFF* ]]; then
    st_ok 'compare detects a hygiene change'
  else
    st_note "compare rc=$cmp_rc out=$cmp_out"
  fi

  local cl_out
  cl_out=$(CLASSIFY_ROOT=$scratch classify_tree "$scratch")
  if [[ "$cl_out" == *'unclassified	0'* ]] || [[ "$cl_out" == *'unclassified\t0'* ]]; then
    st_ok 'classify unclassified=0'
  else
    st_note "classify proof missing zero: $cl_out"
  fi
  if [[ "$cl_out" == *SECRETTOKEN41* || "$cl_out" == *PAST200MARKER* || "$cl_out" == *TARGETTOKEN41* || "$cl_out" == *STATETOKEN41* || "$cl_out" == *WATCHTOKEN41* ]]; then
    st_note 'classify leaked planted content'
  else
    st_ok 'classify output has no planted content'
  fi
  if [[ "$cl_out" == *'header_max_read	'* ]]; then
    local hm
    hm=$(printf '%s\n' "$cl_out" | awk -F'\t' '$1=="CLASS-PROOF"{for(i=1;i<=NF;i++) if($i=="header_max_read") print $(i+1)}')
    if [ -n "$hm" ] && [ "$hm" -gt 0 ] && [ "$hm" -le 200 ]; then st_ok "header_max_read=$hm"; else st_note "header_max_read=$hm"; fi
  else
    st_note 'classify missing header_max_read'
  fi
  if [[ "$cl_out" == *$'\t'"symlink"$'\t'* || "$cl_out" == *'CLASS	symlink	'* ]]; then
    st_ok 'symlink classed without follow'
  else
    st_note 'symlink class missing'
  fi

  # aligned docs → drift 0
  local askill aspec atool
  askill=$tmp/aligned-skill.md
  aspec=$tmp/aligned-spec.md
  atool=$tmp/aligned-tool.sh
  cat > "$askill" <<'EOF'
| `pushed` | existing refs only; ancestor of refs/remotes/origin/HEAD | `git merge-base --is-ancestor <commit> refs/remotes/origin/HEAD` |
| `stale` | known scratch type (`.scratch/`, `*.out`, `*.log`, `*-draft.*`, checkpoint blobs) | rg |
symlink-present fails closed.
- lore-shokunin: 1 worktree.
- game-dev-2d-shokunin: 1 worktree.
- kotodama-shokunin: scratch_bytes=12
EOF
  cat > "$aspec" <<'EOF'
One bash tool, bash + coreutils + git + rg only.
NO `git fetch` — existing refs only.
EOF
  cat > "$atool" <<'EOF'
resolve_default_ref() {
  git symbolic-ref --quiet --short refs/remotes/origin/HEAD
}
scratch_type() {
  if [ "$comp" = ".scratch" ]; then printf scratch-dir; fi
  case "$base" in
    *.out|*.log) printf ext ;;
    *-draft.*) printf draft ;;
    *checkpoint*.json|launch-*.json) printf checkpoint ;;
  esac
}
count_live_refs() {
  rg -l --no-ignore --fixed-strings -e "$base" .
}
EOF
  local rec
  rec=$(SOUJI_SKILL=$askill SOUJI_SPEC=$aspec SOUJI_VERIFY=$atool SOUJI_VAULT=$atool \
    SOUJI_LIVE_LORE_WT=1 SOUJI_LIVE_GD2D_WT=1 SOUJI_LIVE_KOTO_BYTES=12 \
    reconcile)
  if [[ "$rec" == *'RECONCILE-SUMMARY	drift	0	'* ]]; then
    st_ok 'aligned fixture drift=0'
  else
    st_note "aligned fixture not zero: $rec"
  fi

  local dskill dspec dtool
  dskill=$tmp/drift-skill.md
  dspec=$tmp/drift-spec.md
  dtool=$tmp/drift-tool.sh
  cat > "$dskill" <<'EOF'
| `pushed` | after `git fetch`, ancestor of origin/main | `git fetch -q && git merge-base --is-ancestor <commit> origin/main && echo PUSHED` |
| `stale` | known scratch type (`.scratch/`, `*.tmp`, checkpoint blobs, `out/`, `reports/round-*/**-draft.*`) | `rg -l` |
- lore-shokunin: 19 prunable worktrees (`git worktree list`).
- game-dev-2d-shokunin: 5 prunable worktrees.
- kotodama-shokunin: 553M `.scratch/` beside unpushed work — NOT-SAFE.
EOF
  cat > "$dspec" <<'EOF'
One bash tool, bash + coreutils + git + rg only.
NO `git fetch` — existing refs only.
(`NOT-SAFE(symlink-present)`)
rg -l --no-ignore --basename
EOF
  cat > "$dtool" <<'EOF'
resolve_default_ref() {
  git symbolic-ref --quiet --short refs/remotes/origin/HEAD
  # local refs/heads/master can NEVER establish a pushed receipt
  return 1
}
scratch_type() {
  if [ "$comp" = ".scratch" ]; then printf scratch-dir; fi
  case "$base" in
    *.out|*.log) printf ext ;;
    *-draft.*) printf draft ;;
    *checkpoint*.json|launch-*.json) printf checkpoint ;;
  esac
}
count_live_refs() {
  rg -l --no-ignore --fixed-strings -e "$base" .
  out=$(find . -type f -print0 | xargs -0 grep -c needle)
}
EOF
  rec=$(SOUJI_SKILL=$dskill SOUJI_SPEC=$dspec SOUJI_VERIFY=$dtool SOUJI_VAULT=$dtool \
    SOUJI_LIVE_LORE_WT=1 SOUJI_LIVE_GD2D_WT=4 SOUJI_LIVE_KOTO_BYTES=18298096747 \
    reconcile)
  local id need
  for id in pushed-fetch pushed-origin-main stale-types symlink-doc spec-allowlist spec-rg-basename surface-lore surface-gd2d surface-kotodama; do
    if [[ "$rec" == *"RECONCILE	$id	DRIFT"* ]]; then
      st_ok "drift detected $id"
    else
      st_note "missing DRIFT $id"
    fi
  done
  if [[ "$rec" == *'RECONCILE	hidden-sweep	ALIGNED-GAP'* ]]; then
    st_ok 'hidden-sweep is ALIGNED-GAP not drift'
  else
    st_note 'hidden-sweep not recorded as ALIGNED-GAP'
  fi

  rm -rf -- "$tmp"
  if [ "$st_fail" = 0 ]; then
    printf 'selftest: pass\n'
    return 0
  fi
  printf 'selftest: fail\n' >&2
  return 1
}

if [ "$SELFTEST" = 1 ]; then
  selftest
  exit $?
fi

run_modes "$SHOKUNIN_ROOT"
