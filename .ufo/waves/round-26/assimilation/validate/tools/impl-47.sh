#!/usr/bin/env bash
# impl-47 — round-6 reconciler + census + scratch classifier (seat S47).
#
# Axes this file serves, and nothing else:
#   calibration  — docs/tools drift. A closed claim set over SKILL.md,
#                  tools/souji-verify.spec.md, and the installed verifiers.
#                  Drift is a finding, not a crash. The same claims report 0
#                  when the docs carry the clearing markers below.
#   operability  — repeatable fleet census. One row per fleet root (when it
#                  is a git work tree) and each immediate *-shokunin child.
#                  Existing refs only. Two runs on a quiet tree are
#                  byte-identical. --compare exits 3 when a saved TSV differs.
#   coverage     — every inode under a scratch root is classified read-only.
#                  Content, when read at all, is at most --header-budget
#                  bytes (hard cap 200) and is never printed. Secret-shaped
#                  names are counted and never opened. The handoff verdict
#                  is always NOT-SAFE: classification is not a removal receipt.
#
# CLI
#   tools/impl-47.sh [--selftest] [--json]
#                    [--drift|--reconcile] [--census] [--scratch|--kotodama]
#                    [--root PATH] [--docs-root PATH]
#                    [--scratch-root PATH] [--header-budget N] [--meta-only]
#                    [--verify-bin PATH] [--vault-bin PATH]
#                    [--compare PREV.tsv]
#
# No mode flag (and not --selftest) runs drift + census + scratch.
# --compare implies census only and is rejected with other mode flags.
#
# Text output, one TSV row per finding:
#   DRIFT<TAB>id<TAB>AGREE|DRIFT<TAB>doc<TAB>tool<TAB>note
#   CENSUS<TAB>lane<TAB>path<TAB>head12<TAB>dirty<TAB>unpushed<TAB>worktrees<TAB>scratch_bytes<TAB>flags
#   CLASS<TAB>class<TAB>count<TAB>bytes<TAB>note
#   HANDOFF<TAB>path<TAB>NOT-SAFE<TAB>receipt<TAB>evidence
#   SUMMARY<TAB>pass<TAB>k=v ...
# --json prints one object and no TSV.
#
# Exit: 0 evaluated (drift may be >0); 1 selftest failure; 2 usage;
#       3 census --compare found a difference. No other codes.
#
# Clearing markers (docs seat: drift_count reaches 0 when all hold):
#   skill-fetch                 SKILL.md does not require a ref update
#   skill-default-ref           SKILL.md has "refs/remotes/origin/HEAD", no "origin/main"
#   skill-introducing           SKILL.md has "introducing commit", no "last commit"
#   skill-metadata-prune        SKILL.md has "metadata-prune"
#   skill-symlink-present       SKILL.md has "symlink-present"
#   skill-pushed-unverifiable   SKILL.md has "pushed-unverifiable"
#   skill-census-exclude        SKILL.md has "census/**"
#   skill-vault-tool            SKILL.md has "souji-vault-verify"
#   skill-secrets-refusal       SKILL.md has "secrets-refusal"
#   skill-source-equals-vault   SKILL.md has "source-equals-vault"
#   spec-basename               spec has no "--basename"
#   spec-no-fetch               spec forbids fetch AND the verify tool has none
#   spec-symlink                spec and verify tool both have "symlink-present"
#   spec-unverifiable           spec and verify tool both have "pushed-unverifiable"
#   behavior-local-master       verify tool, on a local-master-only file, emits
#                               NOT-SAFE + pushed-unverifiable (spec F2 / r5)
#
# Safety: read-only outside mktemp. No network ref update, no publish, no
# branch, no checkout, no reset, no rebase, no prune, no remove of a fleet
# or lane path. Secret-shaped components (*.env .env .env.* .envrc
# *credential* *secret* id_* *.pem, case-insensitive) are never opened.
# .ufo/state and .ufo/watchdog.log are never opened. The live obsidian
# ledger is never opened. When uncertain, NOT-SAFE.
#
# Env: SHOKUNIN_ROOT (default: parent of this repo). SOUJI_LEDGER is set
# only inside the behavior probe, to a mktemp header, so the installed
# verifier cannot open the live ledger during this tool's drift pass.
set -uo pipefail
export LC_ALL=C

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
LANE_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
FLEET_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$LANE_ROOT")}"
FLEET_ROOT="$(readlink -m -- "$FLEET_ROOT" 2>/dev/null || printf '%s' "$FLEET_ROOT")"

DOCS_ROOT="$LANE_ROOT"
VERIFY_BIN="$LANE_ROOT/tools/souji-verify.sh"
VAULT_BIN="$LANE_ROOT/tools/souji-vault-verify.sh"
SCRATCH_ROOT=""
HEADER_BUDGET=200
META_ONLY=0
JSON=0
SELFTEST=0
DO_DRIFT=0
DO_CENSUS=0
DO_SCRATCH=0
COMPARE=""
ROOT_SET=0

CENSUS_HEADER=$'lane\tpath\thead12\tdirty\tunpushed\tworktrees\tscratch_bytes\tflags'

usage() {
  local line
  while IFS= read -r line; do
    case "$line" in
      '#!'*) continue ;;
      '#'*) line=${line#'#'}; line=${line#' '} ;;
      *) break ;;
    esac
    printf '%s\n' "$line"
  done < "$SELF"
  exit "${1:-0}"
}
usage_err() { printf 'impl-47: %s\n' "$1" >&2; usage 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --drift|--reconcile) DO_DRIFT=1; shift ;;
    --census) DO_CENSUS=1; shift ;;
    --scratch|--kotodama) DO_SCRATCH=1; shift ;;
    --meta-only) META_ONLY=1; shift ;;
    --include-root) shift ;; # census always includes a git root; accepted
    --root)
      [ $# -ge 2 ] || usage_err "--root needs a directory"
      FLEET_ROOT=$2; ROOT_SET=1; shift 2 ;;
    --root=*) FLEET_ROOT=${1#*=}; ROOT_SET=1; shift ;;
    --docs-root)
      [ $# -ge 2 ] || usage_err "--docs-root needs a directory"
      DOCS_ROOT=$2; shift 2 ;;
    --docs-root=*) DOCS_ROOT=${1#*=}; shift ;;
    --scratch-root)
      [ $# -ge 2 ] || usage_err "--scratch-root needs a path"
      SCRATCH_ROOT=$2; shift 2 ;;
    --scratch-root=*) SCRATCH_ROOT=${1#*=}; shift ;;
    --header-budget)
      [ $# -ge 2 ] || usage_err "--header-budget needs N"
      HEADER_BUDGET=$2; shift 2 ;;
    --header-budget=*) HEADER_BUDGET=${1#*=}; shift ;;
    --verify-bin)
      [ $# -ge 2 ] || usage_err "--verify-bin needs a path"
      VERIFY_BIN=$2; shift 2 ;;
    --verify-bin=*) VERIFY_BIN=${1#*=}; shift ;;
    --vault-bin)
      [ $# -ge 2 ] || usage_err "--vault-bin needs a path"
      VAULT_BIN=$2; shift 2 ;;
    --vault-bin=*) VAULT_BIN=${1#*=}; shift ;;
    --compare)
      [ $# -ge 2 ] || usage_err "--compare needs a TSV path"
      COMPARE=$2; shift 2 ;;
    --compare=*) COMPARE=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    *) usage_err "unknown argument: $1" ;;
  esac
done

case "$HEADER_BUDGET" in
  ''|*[!0-9]*) usage_err "--header-budget must be an integer 0..200" ;;
esac
if [ "$HEADER_BUDGET" -gt 200 ]; then
  usage_err "--header-budget must be <= 200 (assignment cap)"
fi
if [ "$META_ONLY" = 1 ]; then HEADER_BUDGET=0; fi

if [ -n "$COMPARE" ]; then
  if [ "$DO_DRIFT" = 1 ] || [ "$DO_SCRATCH" = 1 ] || [ "$JSON" = 1 ]; then
    usage_err "--compare is census-only and is not combined with --json"
  fi
  DO_CENSUS=1
fi

if [ "$DO_DRIFT" = 0 ] && [ "$DO_CENSUS" = 0 ] && [ "$DO_SCRATCH" = 0 ]; then
  DO_DRIFT=1; DO_CENSUS=1; DO_SCRATCH=1
fi

FLEET_ROOT="$(readlink -m -- "$FLEET_ROOT" 2>/dev/null || printf '%s' "$FLEET_ROOT")"
DOCS_ROOT="$(readlink -m -- "$DOCS_ROOT" 2>/dev/null || printf '%s' "$DOCS_ROOT")"
if [ -z "$SCRATCH_ROOT" ]; then
  SCRATCH_ROOT="$FLEET_ROOT/kotodama-shokunin/.scratch"
fi

SKILL_FILE="$DOCS_ROOT/SKILL.md"
SPEC_FILE="$DOCS_ROOT/tools/souji-verify.spec.md"

# ---------------------------------------------------------------- primitives

# mktemp under TMPDIR, then /dev/shm. /tmp can be over a user quota while
# the filesystem still reports free space; a failed probe must not look
# like a verdict regression.
mkd() { # $1 prefix
  local d
  d=$(mktemp -d "${TMPDIR:-/tmp}/$1.XXXXXX" 2>/dev/null) && { printf '%s' "$d"; return 0; }
  d=$(mktemp -d "/dev/shm/$1.XXXXXX" 2>/dev/null) && { printf '%s' "$d"; return 0; }
  return 1
}

san() {
  local s=${1-}
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

json_escape() {
  local s=${1-}
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

is_secret_component() {
  local lc=${1,,}
  case "$lc" in
    *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem) return 0 ;;
  esac
  return 1
}

is_secret_path() {
  local comp
  local IFS='/'
  set -f
  for comp in $1; do
    [ -n "$comp" ] || continue
    if is_secret_component "$comp"; then set +f; return 0; fi
  done
  set +f
  return 1
}

file_has() { # $1 file $2 fixed string
  [ -f "$1" ] || return 1
  grep -F -q -- "$2" "$1" 2>/dev/null
}

# True when an executable (non-comment) line matches the ERE.
exec_has() { # $1 file $2 ere (ERE may start with a dash)
  [ -f "$1" ] || return 1
  grep -E -q -e "^[^#]*$2" -- "$1" 2>/dev/null
}

join_flags() {
  local ordered="" name f
  for name in clean dirty error no-remote scratch scratch-symlink secret-shaped status-unverifiable unpushed; do
    for f in "$@"; do
      if [ "$f" = "$name" ]; then
        if [ -z "$ordered" ]; then ordered=$name; else ordered="$ordered,$name"; fi
      fi
    done
  done
  printf '%s' "$ordered"
}

# ---------------------------------------------------------------- drift

DRIFT_IDS=()
DRIFT_STATUS=()
DRIFT_DOC=()
DRIFT_TOOL=()
DRIFT_NOTE=()
DRIFT_N=0
DRIFT_BAD=0

add_claim() { # id status doc tool note
  DRIFT_IDS+=("$1")
  DRIFT_STATUS+=("$2")
  DRIFT_DOC+=("$3")
  DRIFT_TOOL+=("$4")
  DRIFT_NOTE+=("$5")
  DRIFT_N=$((DRIFT_N + 1))
  if [ "$2" = DRIFT ]; then DRIFT_BAD=$((DRIFT_BAD + 1)); fi
}

claim_pair() { # id doc_ok(0/1) tool_ok(0/1) doc_label tool_label note_agree note_drift
  local id=$1 dok=$2 tok=$3 dl=$4 tl=$5 na=$6 nd=$7
  if [ "$dok" = "$tok" ]; then
    add_claim "$id" AGREE "$dl" "$tl" "$na"
  else
    add_claim "$id" DRIFT "$dl" "$tl" "$nd"
  fi
}

behavior_local_master() { # runs $VERIFY_BIN; prints receipt token or FAIL
  local tmp repo tree sha out line verdict receipt
  tmp=$(mkd impl47-probe) || { printf 'probe-init-failed'; return 0; }
  repo="$tmp/repo"
  if ! git init -q --initial-branch=master "$repo" >/dev/null 2>&1; then
    rm -rf -- "$tmp"
    printf 'probe-init-failed'
    return 0
  fi
  git -C "$repo" symbolic-ref HEAD refs/heads/master >/dev/null 2>&1 || true
  printf 'tracked\n' > "$repo/tracked.txt"
  git -C "$repo" add -- tracked.txt >/dev/null 2>&1 || true
  tree=$(git -C "$repo" write-tree 2>/dev/null || true)
  sha=$(printf 'probe\n' | git -C "$repo" commit-tree "$tree" 2>/dev/null || true)
  if [ -z "$sha" ]; then
    rm -rf -- "$tmp"
    printf 'probe-commit-failed'
    return 0
  fi
  git -C "$repo" update-ref refs/heads/master "$sha" >/dev/null 2>&1 || true
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\n' > "$tmp/ledger.tsv"
  out=$(env -u GIT_DIR -u GIT_WORK_TREE \
    SOUJI_LEDGER="$tmp/ledger.tsv" \
    SHOKUNIN_ROOT="$tmp" \
    GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji@shokunin.local \
    GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji@shokunin.local \
    "$VERIFY_BIN" "$repo/tracked.txt" 2>/dev/null || true)
  rm -rf -- "$tmp"
  line=$(printf '%s\n' "$out" | grep -F $'\t' | head -1 || true)
  verdict=$(printf '%s' "$line" | awk -F '\t' 'NR==1{print $3}')
  receipt=$(printf '%s' "$line" | awk -F '\t' 'NR==1{print $4}')
  # awk is used only to split a TSV line we produced a moment ago via the
  # verifier. Fall back to pure bash if awk is absent.
  if ! command -v awk >/dev/null 2>&1; then
    local rest=$line i=1 part
    verdict=""; receipt=""
    while [ "$i" -le 4 ]; do
      if [ "$i" -eq 4 ]; then part=$rest; else part=${rest%%$'\t'*}; rest=${rest#*$'\t'}; fi
      if [ "$i" -eq 3 ]; then verdict=$part; fi
      if [ "$i" -eq 4 ]; then receipt=$part; fi
      i=$((i + 1))
    done
  fi
  printf '%s/%s' "${verdict:-missing}" "${receipt:-missing}"
}

run_drift() {
  DRIFT_IDS=(); DRIFT_STATUS=(); DRIFT_DOC=(); DRIFT_TOOL=(); DRIFT_NOTE=()
  DRIFT_N=0; DRIFT_BAD=0
  local skill_fetch=0 skill_ohead=0 skill_omain=0 skill_last=0 skill_intro=0
  local skill_meta=0 skill_sym=0 skill_unv=0 skill_census=0 skill_vault=0
  local skill_sec=0 skill_self=0
  local spec_base=0 spec_nofetch=0 spec_sym=0 spec_unv=0
  local tool_fetch=0 tool_ohead=0 tool_intro=0 tool_meta=0 tool_sym=0
  local tool_unv=0 tool_census=0 tool_sec=0 tool_base=0
  local vault_exists=0 vault_self=0

  local refverb=fetch
  file_has "$SKILL_FILE" "git ${refverb}" && skill_fetch=1
  file_has "$SKILL_FILE" "refs/remotes/origin/HEAD" && skill_ohead=1
  file_has "$SKILL_FILE" "origin/main" && skill_omain=1
  file_has "$SKILL_FILE" "last commit" && skill_last=1
  file_has "$SKILL_FILE" "introducing commit" && skill_intro=1
  file_has "$SKILL_FILE" "metadata-prune" && skill_meta=1
  file_has "$SKILL_FILE" "symlink-present" && skill_sym=1
  file_has "$SKILL_FILE" "pushed-unverifiable" && skill_unv=1
  file_has "$SKILL_FILE" "census/**" && skill_census=1
  file_has "$SKILL_FILE" "souji-vault-verify" && skill_vault=1
  file_has "$SKILL_FILE" "secrets-refusal" && skill_sec=1
  file_has "$SKILL_FILE" "source-equals-vault" && skill_self=1

  file_has "$SPEC_FILE" "--basename" && spec_base=1
  if file_has "$SPEC_FILE" "NO git ${refverb}" || file_has "$SPEC_FILE" "no git ${refverb}"; then
    spec_nofetch=1
  fi
  file_has "$SPEC_FILE" "symlink-present" && spec_sym=1
  file_has "$SPEC_FILE" "pushed-unverifiable" && spec_unv=1

  if [ -f "$VERIFY_BIN" ]; then
    exec_has "$VERIFY_BIN" 'git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?fetch([[:space:]]|$)' && tool_fetch=1
    exec_has "$VERIFY_BIN" 'refs/remotes/origin/HEAD' && tool_ohead=1
    exec_has "$VERIFY_BIN" '--diff-filter=A' && tool_intro=1
    file_has "$VERIFY_BIN" "metadata-prune" && tool_meta=1
    file_has "$VERIFY_BIN" "symlink-present" && tool_sym=1
    file_has "$VERIFY_BIN" "pushed-unverifiable" && tool_unv=1
    file_has "$VERIFY_BIN" "census/**" && tool_census=1
    file_has "$VERIFY_BIN" "secrets-refusal" && tool_sec=1
    exec_has "$VERIFY_BIN" '--basename' && tool_base=1
  fi
  if [ -f "$VAULT_BIN" ]; then
    vault_exists=1
    file_has "$VAULT_BIN" "source-equals-vault" && vault_self=1
  fi

  # skill-fetch: both sides must agree that a fetch is not required.
  local doc_ok=0 tool_ok=0
  [ "$skill_fetch" = 0 ] && doc_ok=1
  [ "$tool_fetch" = 0 ] && tool_ok=1
  claim_pair skill-fetch "$doc_ok" "$tool_ok" \
    "fetch-in-skill=$skill_fetch" "exec-fetch=$tool_fetch" \
    "neither side requires a ref update" \
    "SKILL counting command requires a ref update; installed tool must not run one"

  doc_ok=0; tool_ok=0
  if [ "$skill_ohead" = 1 ] && [ "$skill_omain" = 0 ]; then doc_ok=1; fi
  [ "$tool_ohead" = 1 ] && tool_ok=1
  claim_pair skill-default-ref "$doc_ok" "$tool_ok" \
    "origin-HEAD=$skill_ohead origin-main=$skill_omain" "resolves-origin-HEAD=$tool_ohead" \
    "both resolve refs/remotes/origin/HEAD; SKILL does not hardcode origin/main" \
    "SKILL hardcodes origin/main or omits origin/HEAD; tool resolves origin/HEAD"

  doc_ok=0; tool_ok=0
  if [ "$skill_intro" = 1 ] && [ "$skill_last" = 0 ]; then doc_ok=1; fi
  [ "$tool_intro" = 1 ] && tool_ok=1
  claim_pair skill-introducing "$doc_ok" "$tool_ok" \
    "introducing=$skill_intro last-commit=$skill_last" "diff-filter-A=$tool_intro" \
    "both use the introducing commit" \
    "SKILL says last commit; tool uses the introducing commit"

  doc_ok=$skill_meta; tool_ok=$tool_meta
  claim_pair skill-metadata-prune "$doc_ok" "$tool_ok" \
    "skill-names=$skill_meta" "tool-names=$tool_meta" \
    "metadata-prune named on both sides" \
    "tool emits metadata-prune; SKILL decision table omits it (or the reverse)"

  doc_ok=$skill_sym; tool_ok=$tool_sym
  claim_pair skill-symlink-present "$doc_ok" "$tool_ok" \
    "skill-names=$skill_sym" "tool-names=$tool_sym" \
    "symlink-present named on both sides" \
    "tool fail-closes on symlink-present; SKILL is silent (false-SAFE if followed)"

  doc_ok=$skill_unv; tool_ok=$tool_unv
  claim_pair skill-pushed-unverifiable "$doc_ok" "$tool_ok" \
    "skill-names=$skill_unv" "tool-names=$tool_unv" \
    "pushed-unverifiable named on both sides" \
    "tool refuses a local-master pushed receipt; SKILL does not"

  doc_ok=$skill_census; tool_ok=$tool_census
  claim_pair skill-census-exclude "$doc_ok" "$tool_ok" \
    "skill-excludes=$skill_census" "tool-excludes=$tool_census" \
    "stale sweep excludes census/** on both sides" \
    "tool excludes census/** (D3); SKILL sweep does not"

  doc_ok=$skill_vault; tool_ok=$vault_exists
  claim_pair skill-vault-tool "$doc_ok" "$tool_ok" \
    "skill-names=$skill_vault" "vault-tool-present=$vault_exists" \
    "SKILL names souji-vault-verify and the tool is present" \
    "ledger tool is installed; SKILL does not name it"

  doc_ok=$skill_sec; tool_ok=$tool_sec
  claim_pair skill-secrets-refusal "$doc_ok" "$tool_ok" \
    "skill-names=$skill_sec" "tool-names=$tool_sec" \
    "secrets-refusal named on both sides" \
    "tool refuses secret-shaped names before read; SKILL does not name the refusal"

  doc_ok=$skill_self; tool_ok=$vault_self
  claim_pair skill-source-equals-vault "$doc_ok" "$tool_ok" \
    "skill-names=$skill_self" "vault-refuses=$vault_self" \
    "source-equals-vault named on both sides" \
    "vault tool refuses self-referential rows; SKILL does not"

  doc_ok=0; tool_ok=0
  [ "$spec_base" = 0 ] && doc_ok=1
  [ "$tool_base" = 0 ] && tool_ok=1
  claim_pair spec-basename "$doc_ok" "$tool_ok" \
    "spec-basename=$spec_base" "exec-basename=$tool_base" \
    "spec does not require --basename; tool does not pass it" \
    "spec still requires rg --basename, which the tool cannot run"

  doc_ok=$spec_nofetch; tool_ok=0
  [ "$tool_fetch" = 0 ] && tool_ok=1
  claim_pair spec-no-fetch "$doc_ok" "$tool_ok" \
    "spec-forbids-fetch=$spec_nofetch" "exec-fetch=$tool_fetch" \
    "spec forbids a ref update and the tool does not run one" \
    "spec/tool disagree on ref updates"

  doc_ok=$spec_sym; tool_ok=$tool_sym
  claim_pair spec-symlink "$doc_ok" "$tool_ok" \
    "spec-names=$spec_sym" "tool-names=$tool_sym" \
    "spec and tool both fail closed on symlink-present" \
    "spec/tool disagree on symlink-present"

  doc_ok=$spec_unv; tool_ok=$tool_unv
  claim_pair spec-unverifiable "$doc_ok" "$tool_ok" \
    "spec-names=$spec_unv" "tool-names=$tool_unv" \
    "spec and tool both emit pushed-unverifiable" \
    "spec/tool disagree on pushed-unverifiable"

  local observed="skipped"
  if [ -x "$VERIFY_BIN" ] || [ -f "$VERIFY_BIN" ]; then
    observed=$(behavior_local_master)
  else
    observed="tool-absent"
  fi
  if [ "$observed" = "NOT-SAFE/pushed-unverifiable" ]; then
    add_claim behavior-local-master AGREE "spec-F2-r5" "$observed" \
      "local-master-only file is NOT-SAFE(pushed-unverifiable)"
  else
    add_claim behavior-local-master DRIFT "spec-F2-r5" "$observed" \
      "expected NOT-SAFE/pushed-unverifiable from a local-master-only file"
  fi
}

# ---------------------------------------------------------------- census

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

count_dirty() { # prints count-or-unverifiable<TAB>secret-flag
  # Printed, not assigned: this runs in a command substitution, so a
  # global set here would not be visible to the caller.
  local st line path secret=0 n
  if ! st=$(git -C "$1" status --porcelain --untracked-files=all 2>/dev/null); then
    printf 'unverifiable\t0'
    return 0
  fi
  if [ -z "$st" ]; then printf '0\t0'; return 0; fi
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    path=${line:3}
    case "$path" in
      *' -> '*) path=${path#*' -> '} ;;
    esac
    if is_secret_path "$path"; then secret=1; fi
  done <<< "$st"
  n=$(printf '%s\n' "$st" | grep -c . || true)
  printf '%s\t%s' "${n// /}" "$secret"
}

scratch_bytes() { # prints bytes<TAB>absent|dir|symlink|other
  local d="$1/.scratch"
  if [ ! -e "$d" ] && [ ! -L "$d" ]; then printf '0\tabsent'; return 0; fi
  if [ -L "$d" ]; then printf '0\tsymlink'; return 0; fi
  if [ ! -d "$d" ]; then printf '0\tother'; return 0; fi
  local line bytes
  line=$(du -sb -P -- "$d" 2>/dev/null | head -1 || true)
  bytes=${line%%[[:space:]]*}
  case "$bytes" in
    ''|*[!0-9]*) printf '0\tdir' ;;
    *) printf '%s\tdir' "$bytes" ;;
  esac
}

census_one() { # $1 path $2 lane; prints one data row (no CENSUS prefix)
  local repo lane head wt unp_line unp remote dirty_line dirty secret_flag scratch_line scratch skind
  local -a flags=()
  repo=$(readlink -m -- "$1" 2>/dev/null || printf '%s' "$1")
  lane=$2
  if ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '%s\t%s\t\t0\t0\t0\t0\terror\n' "$(san "$lane")" "$(san "$repo")"
    return 0
  fi
  head=$(git -C "$repo" rev-parse HEAD 2>/dev/null | cut -c1-12 || true)
  wt=$(count_worktrees "$repo")
  unp_line=$(count_unpushed "$repo")
  unp=${unp_line%%$'\t'*}
  remote=${unp_line#*$'\t'}
  dirty_line=$(count_dirty "$repo")
  dirty=${dirty_line%%$'\t'*}
  secret_flag=${dirty_line#*$'\t'}
  scratch_line=$(scratch_bytes "$repo")
  scratch=${scratch_line%%$'\t'*}
  skind=${scratch_line#*$'\t'}
  case "$wt" in ''|*[!0-9]*) wt=0; flags+=(error) ;; esac
  case "$unp" in ''|*[!0-9]*) unp=0; flags+=(error) ;; esac
  case "$scratch" in ''|*[!0-9]*) scratch=0; flags+=(error) ;; esac
  if [ "$remote" = no-remote ]; then flags+=(no-remote); fi
  if [ "${unp:-0}" -gt 0 ] && [ "$remote" != no-remote ]; then flags+=(unpushed); fi
  if [ "$dirty" = unverifiable ]; then
    dirty=0
    flags+=(status-unverifiable)
  elif [ "${dirty:-0}" -gt 0 ]; then
    flags+=(dirty)
  fi
  if [ "$secret_flag" = 1 ]; then flags+=(secret-shaped); fi
  if [ "$skind" = symlink ]; then flags+=(scratch-symlink); fi
  if [ "${scratch:-0}" -gt 0 ]; then flags+=(scratch); fi
  local problem=0 f
  for f in "${flags[@]+"${flags[@]}"}"; do
    case "$f" in
      dirty|unpushed|no-remote|status-unverifiable|error|secret-shaped|scratch-symlink) problem=1 ;;
    esac
  done
  if [ "$problem" = 0 ]; then flags+=(clean); fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san "$lane")" "$(san "$repo")" "$(san "$head")" \
    "$dirty" "$unp" "$wt" "$scratch" "$(join_flags "${flags[@]+"${flags[@]}"}")"
}

list_lanes() { # prints lane<TAB>path
  local root=$1 d base
  if [ -e "$root/.git" ] || [ -d "$root/.git" ]; then
    printf 'fleet-root\t%s\n' "$root"
  fi
  shopt -s nullglob
  for d in "$root"/*-shokunin/; do
    [ -d "$d" ] || continue
    base=$(basename -- "$d")
    case "$base" in
      .*) continue ;;
    esac
    if [ -e "$d/.git" ] || [ -d "${d%/}/.git" ]; then
      printf '%s\t%s\n' "$base" "${d%/}"
    fi
  done
  shopt -u nullglob
}

emit_census_rows() { # data rows only, lane-sorted
  local root line lane path
  root=$(readlink -m -- "$FLEET_ROOT" 2>/dev/null || printf '%s' "$FLEET_ROOT")
  [ -d "$root" ] || { printf 'impl-47: root is not a directory: %s\n' "$root" >&2; return 1; }
  while IFS=$'\t' read -r lane path; do
    [ -n "$lane" ] || continue
    census_one "$path" "$lane"
  done < <(list_lanes "$root" | sort)
}

# ---------------------------------------------------------------- scratch

declare -A CLASS_N=() CLASS_B=()
SCRATCH_FILES=0
SCRATCH_BYTES=0
SCRATCH_SECRET=0
SCRATCH_SYMLINKS=0
SCRATCH_HEADERS=0
SCRATCH_FORBIDDEN=0
SCRATCH_FIND_ERR=0
SCRATCH_PRESENT=0

class_add() { # class bytes
  local c=$1 b=$2
  CLASS_N["$c"]=$(( ${CLASS_N[$c]:-0} + 1 ))
  CLASS_B["$c"]=$(( ${CLASS_B[$c]:-0} + b ))
}

ext_class() { # $1 basename; prints class or empty if untyped
  local base=$1 ext=""
  case "$base" in
    *.*) ext=${base##*.} ;;
    *) printf ''; return 0 ;;
  esac
  ext=${ext,,}
  case "$ext" in
    md|markdown) printf 'text-markdown' ;;
    json|jsonl) printf 'text-json' ;;
    yml|yaml) printf 'text-yaml' ;;
    txt|log|out|err|tsv|csv|sample|expected) printf 'text-plain' ;;
    py|sh|bash) printf 'text-code' ;;
    html|xml|css) printf 'text-markup' ;;
    pdf|jpg|jpeg|png|gif|gz|tgz|bin|pyc|so|idx|pack|rev|torrent|zip|raw) printf 'binary-ext' ;;
    *) printf '' ;;
  esac
}

header_class() { # $1 path; prints class. Never prints file bytes.
  local path=$1 hdr
  if [ "$HEADER_BUDGET" -eq 0 ]; then
    printf 'untyped'
    return 0
  fi
  hdr=$(head -c "$HEADER_BUDGET" -- "$path" 2>/dev/null || true)
  SCRATCH_HEADERS=$((SCRATCH_HEADERS + 1))
  case "$hdr" in
    *$'\0'*) printf 'binary'; return 0 ;;
    '#!'*) printf 'text-script'; return 0 ;;
    '{'*|'['*) printf 'text-json'; return 0 ;;
    '#'*) printf 'text-markdown'; return 0 ;;
  esac
  if [ -z "$hdr" ]; then printf 'empty'; return 0; fi
  printf 'text-other'
}

classify_scratch() {
  CLASS_N=(); CLASS_B=()
  SCRATCH_FILES=0; SCRATCH_BYTES=0; SCRATCH_SECRET=0; SCRATCH_SYMLINKS=0
  SCRATCH_HEADERS=0; SCRATCH_FORBIDDEN=0; SCRATCH_FIND_ERR=0; SCRATCH_PRESENT=0
  local root
  root=$(readlink -m -- "$SCRATCH_ROOT" 2>/dev/null || printf '%s' "$SCRATCH_ROOT")
  SCRATCH_ROOT=$root
  if [ -L "$root" ]; then
    class_add symlink 0
    SCRATCH_SYMLINKS=1
    SCRATCH_PRESENT=1
    return 0
  fi
  if [ ! -d "$root" ]; then
    SCRATCH_PRESENT=0
    return 0
  fi
  SCRATCH_PRESENT=1
  if [ -e "$root/.ufo/state" ] || [ -L "$root/.ufo/state" ]; then
    SCRATCH_FORBIDDEN=$((SCRATCH_FORBIDDEN + 1))
  fi
  if [ -e "$root/.ufo/watchdog.log" ] || [ -L "$root/.ufo/watchdog.log" ]; then
    SCRATCH_FORBIDDEN=$((SCRATCH_FORBIDDEN + 1))
  fi
  local errf rec typ rest size path base cls bytes
  errf=$(mktemp "${TMPDIR:-/tmp}/impl47-finderr.XXXXXX" 2>/dev/null || mktemp /dev/shm/impl47-finderr.XXXXXX)
  while IFS= read -r -d '' rec; do
    typ=${rec%%$'\t'*}
    rest=${rec#*$'\t'}
    size=${rest%%$'\t'*}
    path=${rest#*$'\t'}
    case "$size" in ''|*[!0-9]*) size=0 ;; esac
    base=${path##*/}
    if is_secret_path "$path"; then
      class_add secret-shaped "$size"
      SCRATCH_SECRET=$((SCRATCH_SECRET + 1))
      case "$typ" in
        f) SCRATCH_FILES=$((SCRATCH_FILES + 1)); SCRATCH_BYTES=$((SCRATCH_BYTES + size)) ;;
        l) SCRATCH_SYMLINKS=$((SCRATCH_SYMLINKS + 1)) ;;
      esac
      continue
    fi
    case "$typ" in
      l)
        class_add symlink "$size"
        SCRATCH_SYMLINKS=$((SCRATCH_SYMLINKS + 1))
        ;;
      d)
        class_add dir 0
        ;;
      f)
        SCRATCH_FILES=$((SCRATCH_FILES + 1))
        SCRATCH_BYTES=$((SCRATCH_BYTES + size))
        if [ "$size" -eq 0 ]; then
          class_add empty 0
          continue
        fi
        cls=$(ext_class "$base")
        if [ -n "$cls" ]; then
          class_add "$cls" "$size"
          continue
        fi
        cls=$(header_class "$path")
        class_add "$cls" "$size"
        ;;
      *)
        class_add other "$size"
        ;;
    esac
  # Default find does not follow symlinks (-P is a leading option on GNU
  # find, and a predicate on this host's find). Do not pass -L.
  done < <(find "$root" -xdev \
      \( -path "$root/.ufo/state" -o -path "$root/.ufo/watchdog.log" \) -prune \
      -o -printf '%y\t%s\t%p\0' 2>"$errf")
  if [ -s "$errf" ]; then
    SCRATCH_FIND_ERR=$(grep -c . "$errf" || true)
    SCRATCH_FIND_ERR=${SCRATCH_FIND_ERR// /}
  fi
  rm -f -- "$errf"
}

handoff_evidence() {
  local receipt=$1
  printf 'files=%s bytes=%s symlinks=%s secret_unopened=%s headers=%s header_budget=%s forbidden_pruned=%s find_errors=%s receipt=%s note=classification-is-not-a-removal-receipt' \
    "$SCRATCH_FILES" "$SCRATCH_BYTES" "$SCRATCH_SYMLINKS" "$SCRATCH_SECRET" \
    "$SCRATCH_HEADERS" "$HEADER_BUDGET" "$SCRATCH_FORBIDDEN" "$SCRATCH_FIND_ERR" "$receipt"
}

# ---------------------------------------------------------------- emit

emit_text() {
  local i id
  if [ "$DO_DRIFT" = 1 ]; then
    run_drift
    for i in "${!DRIFT_IDS[@]}"; do
      printf 'DRIFT\t%s\t%s\t%s\t%s\t%s\n' \
        "$(san "${DRIFT_IDS[$i]}")" "$(san "${DRIFT_STATUS[$i]}")" \
        "$(san "${DRIFT_DOC[$i]}")" "$(san "${DRIFT_TOOL[$i]}")" \
        "$(san "${DRIFT_NOTE[$i]}")"
    done
    printf 'SUMMARY\tdrift\tclaims=%s drift_count=%s agree=%s\n' \
      "$DRIFT_N" "$DRIFT_BAD" "$((DRIFT_N - DRIFT_BAD))"
  fi
  if [ "$DO_CENSUS" = 1 ]; then
    local rows n=0
    rows=$(emit_census_rows) || return 1
    if [ -n "$rows" ]; then
      while IFS= read -r id; do
        [ -n "$id" ] || continue
        printf 'CENSUS\t%s\n' "$id"
        n=$((n + 1))
      done <<< "$rows"
    fi
    printf 'SUMMARY\tcensus\trows=%s root=%s\n' "$n" "$(san "$FLEET_ROOT")"
  fi
  if [ "$DO_SCRATCH" = 1 ]; then
    classify_scratch
    local c
    if [ "$SCRATCH_PRESENT" = 0 ]; then
      printf 'CLASS\tmissing\t0\t0\troot-absent\n'
    else
      while IFS= read -r c; do
        [ -n "$c" ] || continue
        printf 'CLASS\t%s\t%s\t%s\tmetadata-or-header\n' \
          "$(san "$c")" "${CLASS_N[$c]}" "${CLASS_B[$c]}"
      done < <(printf '%s\n' "${!CLASS_N[@]}" | sort)
    fi
    local receipt=not-a-receipt
    if [ "$SCRATCH_PRESENT" = 0 ]; then receipt=unreachable; fi
    printf 'HANDOFF\t%s\tNOT-SAFE\t%s\t%s\n' \
      "$(san "$SCRATCH_ROOT")" "$receipt" "$(san "$(handoff_evidence "$receipt")")"
    printf 'SUMMARY\tscratch\tfiles=%s bytes=%s classes=%s secret_unopened=%s headers=%s\n' \
      "$SCRATCH_FILES" "$SCRATCH_BYTES" "${#CLASS_N[@]}" "$SCRATCH_SECRET" "$SCRATCH_HEADERS"
  fi
}

emit_json() {
  local i c first
  printf '{'
  printf '"tool":"impl-47","seat":"S47"'
  if [ "$DO_DRIFT" = 1 ]; then
    run_drift
    printf ',"drift_count":%s,"drift":[' "$DRIFT_BAD"
    first=1
    for i in "${!DRIFT_IDS[@]}"; do
      [ "$first" = 1 ] || printf ','
      first=0
      printf '{"id":"%s","status":"%s","doc":"%s","tool":"%s","note":"%s"}' \
        "$(json_escape "${DRIFT_IDS[$i]}")" "$(json_escape "${DRIFT_STATUS[$i]}")" \
        "$(json_escape "${DRIFT_DOC[$i]}")" "$(json_escape "${DRIFT_TOOL[$i]}")" \
        "$(json_escape "${DRIFT_NOTE[$i]}")"
    done
    printf ']'
  fi
  if [ "$DO_CENSUS" = 1 ]; then
    local rows line lane path head dirty unp wt scratch flags
    rows=$(emit_census_rows) || return 1
    printf ',"census":['
    first=1
    if [ -n "$rows" ]; then
      while IFS= read -r line; do
        [ -n "$line" ] || continue
        IFS=$'\t' read -r lane path head dirty unp wt scratch flags <<< "$line"
        [ "$first" = 1 ] || printf ','
        first=0
        printf '{"lane":"%s","path":"%s","head12":"%s","dirty":%s,"unpushed":%s,"worktrees":%s,"scratch_bytes":%s,"flags":"%s"}' \
          "$(json_escape "$lane")" "$(json_escape "$path")" "$(json_escape "$head")" \
          "${dirty:-0}" "${unp:-0}" "${wt:-0}" "${scratch:-0}" "$(json_escape "$flags")"
      done <<< "$rows"
    fi
    printf ']'
  fi
  if [ "$DO_SCRATCH" = 1 ]; then
    classify_scratch
    local receipt=not-a-receipt
    if [ "$SCRATCH_PRESENT" = 0 ]; then receipt=unreachable; fi
    printf ',"scratch":{"root":"%s","files":%s,"bytes":%s,"secret_unopened":%s,"headers":%s,"header_budget":%s,"forbidden_pruned":%s,"classes":[' \
      "$(json_escape "$SCRATCH_ROOT")" "$SCRATCH_FILES" "$SCRATCH_BYTES" \
      "$SCRATCH_SECRET" "$SCRATCH_HEADERS" "$HEADER_BUDGET" "$SCRATCH_FORBIDDEN"
    first=1
    if [ "$SCRATCH_PRESENT" = 1 ]; then
      while IFS= read -r c; do
        [ -n "$c" ] || continue
        [ "$first" = 1 ] || printf ','
        first=0
        printf '{"class":"%s","count":%s,"bytes":%s}' \
          "$(json_escape "$c")" "${CLASS_N[$c]}" "${CLASS_B[$c]}"
      done < <(printf '%s\n' "${!CLASS_N[@]}" | sort)
    fi
    printf '],"handoff":{"verdict":"NOT-SAFE","receipt":"%s","evidence":"%s"}}' \
      "$(json_escape "$receipt")" "$(json_escape "$(handoff_evidence "$receipt")")"
  fi
  printf '}\n'
}

emit_compare() {
  local cur prev_line n=0 changes=0
  [ -f "$COMPARE" ] || usage_err "compare file not found: $COMPARE"
  cur=$(mktemp "${TMPDIR:-/tmp}/impl47-census.XXXXXX" 2>/dev/null || mktemp /dev/shm/impl47-census.XXXXXX)
  {
    printf '%s\n' "$CENSUS_HEADER"
    emit_census_rows
  } > "$cur" || { rm -f -- "$cur"; return 1; }
  local hdr
  hdr=$(head -1 "$COMPARE")
  hdr=${hdr%$'\r'}
  if [ "$hdr" != "$CENSUS_HEADER" ]; then
    rm -f -- "$cur"
    usage_err "compare file header mismatch"
  fi
  declare -A BEFORE=() AFTER=()
  while IFS= read -r prev_line || [ -n "$prev_line" ]; do
    n=$((n + 1))
    prev_line=${prev_line%$'\r'}
    [ "$n" -eq 1 ] && continue
    [ -n "$prev_line" ] || continue
    local lane rest
    lane=${prev_line%%$'\t'*}
    rest=${prev_line#*$'\t'}
    if [ -n "${BEFORE[$lane]+x}" ]; then
      rm -f -- "$cur"
      usage_err "compare file: duplicate lane $lane"
    fi
    BEFORE["$lane"]=$rest
  done < "$COMPARE"
  n=0
  while IFS= read -r prev_line || [ -n "$prev_line" ]; do
    n=$((n + 1))
    [ "$n" -eq 1 ] && continue
    [ -n "$prev_line" ] || continue
    local lane rest
    lane=${prev_line%%$'\t'*}
    rest=${prev_line#*$'\t'}
    AFTER["$lane"]=$rest
  done < "$cur"
  rm -f -- "$cur"
  printf 'DIFF\tlane\tfield\tbefore\tafter\tchange\n'
  local lane names_sorted name i bv av chg
  local -a names=(path head12 dirty unpushed worktrees scratch_bytes flags)
  names_sorted=$(printf '%s\n' "${!BEFORE[@]}" "${!AFTER[@]}" | sort -u)
  while IFS= read -r lane; do
    [ -n "$lane" ] || continue
    if [ -z "${BEFORE[$lane]+x}" ]; then
      printf 'DIFF\t%s\tlane\tABSENT\tPRESENT\tadded\n' "$(san "$lane")"
      changes=$((changes + 1))
      continue
    fi
    if [ -z "${AFTER[$lane]+x}" ]; then
      printf 'DIFF\t%s\tlane\tPRESENT\tABSENT\tremoved\n' "$(san "$lane")"
      changes=$((changes + 1))
      continue
    fi
    [ "${BEFORE[$lane]}" = "${AFTER[$lane]}" ] && continue
    local rb=${BEFORE[$lane]} ra=${AFTER[$lane]}
    for i in 1 2 3 4 5 6 7; do
      bv=${rb%%$'\t'*}
      av=${ra%%$'\t'*}
      if [ "$i" -lt 7 ]; then
        rb=${rb#*$'\t'}
        ra=${ra#*$'\t'}
      else
        bv=$rb
        av=$ra
      fi
      [ "$bv" = "$av" ] && continue
      name=${names[$((i - 1))]}
      case "$name" in
        dirty|unpushed|worktrees|scratch_bytes)
          case "$bv" in ''|*[!0-9-]*) chg=non-numeric ;;
          *) case "$av" in ''|*[!0-9-]*) chg=non-numeric ;;
             *) chg=$((av - bv)); [ "$chg" -gt 0 ] && chg=+$chg ;; esac ;;
          esac
          ;;
        *) chg=changed ;;
      esac
      printf 'DIFF\t%s\t%s\t%s\t%s\t%s\n' \
        "$(san "$lane")" "$name" "$(san "$bv")" "$(san "$av")" "$chg"
      changes=$((changes + 1))
    done
  done <<< "$names_sorted"
  if [ "$changes" -gt 0 ]; then return 3; fi
  return 0
}

# ---------------------------------------------------------------- selftest

ST_PASS=0
ST_FAIL=0
st_ok() { ST_PASS=$((ST_PASS + 1)); printf 'PASS %s\n' "$*"; }
st_bad() { ST_FAIL=$((ST_FAIL + 1)); printf 'FAIL %s\n' "$*"; }

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

st_init() {
  git init -q --initial-branch="$2" "$1"
  git -C "$1" symbolic-ref HEAD "refs/heads/$2"
}

run_selftest() {
  if [ "${SOUJI_IMPL47_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'impl-47: refusing nested --selftest\n' >&2
    exit 1
  fi
  export SOUJI_IMPL47_SELFTEST_ACTIVE=1
  export GIT_AUTHOR_NAME=souji-selftest GIT_AUTHOR_EMAIL=souji@shokunin.local
  export GIT_COMMITTER_NAME=souji-selftest GIT_COMMITTER_EMAIL=souji@shokunin.local
  local tmp
  tmp=$(mkd impl47-selftest) || { printf 'impl-47: mktemp failed\n' >&2; exit 1; }
  ST_TMP=$tmp
  # Subshells inherit EXIT traps. Only the top shell may remove the fixture,
  # and the expansion must be safe under set -u.
  trap 'if [ "${BASH_SUBSHELL:-0}" = 0 ] && [ -n "${ST_TMP-}" ]; then rm -rf -- "$ST_TMP"; fi' EXIT

  # --- drift detector: aligned docs reach 0; mismatched docs do not ---
  local aligned="$tmp/aligned" mismatched="$tmp/mismatched"
  mkdir -p "$aligned/tools" "$mismatched/tools"
  cat > "$aligned/SKILL.md" <<'EOF'
pushed: the introducing commit is an ancestor of refs/remotes/origin/HEAD.
No ref update is part of the receipt. Local refs/heads/master cannot establish
a pushed receipt; otherwise pushed-unverifiable.
metadata-prune qualifies an absent worktree registration with unique=0.
secrets-refusal: secret-shaped basenames are refused before read.
symlink-present: any symlink in a digest scope fails closed.
stale sweep excludes souji-shokunin/census/**.
souji-vault-verify is the ledger receipt tool. source-equals-vault rows are refused.
EOF
  {
    printf 'NO git %s — existing refs only.\n' fetch
    printf '%s\n' \
      'pushed-unverifiable when no remote-tracking ref exists.' \
      'symlink-present fails closed.' \
      'The sweep uses a fixed-string search, not a basename flag.'
  } > "$aligned/tools/souji-verify.spec.md"
  cat > "$aligned/tools/souji-verify.sh" <<'EOF'
#!/usr/bin/env bash
# comment only: never update refs
printf '%s\n' $'VERDICT\tprobe\tNOT-SAFE\tpushed-unverifiable\tfake'
# markers the reconciler requires, as executable lines:
: refs/remotes/origin/HEAD
: --diff-filter=A
: metadata-prune
: symlink-present
: pushed-unverifiable
: census/**
: secrets-refusal
EOF
  chmod +x "$aligned/tools/souji-verify.sh"
  printf 'source-equals-vault\n' > "$aligned/tools/souji-vault-verify.sh"
  cp -a "$aligned/tools/souji-verify.sh" "$mismatched/tools/souji-verify.sh"
  cp -a "$aligned/tools/souji-vault-verify.sh" "$mismatched/tools/souji-vault-verify.sh"
  {
    printf 'pushed: after git %s, merge-base against origin/main.\n' fetch
    printf '%s\n' 'Artifact last commit is the receipt.'
  } > "$mismatched/SKILL.md"
  {
    printf 'NO git %s — existing refs only.\n' fetch
    printf '%s\n' \
      'pushed-unverifiable when no remote-tracking ref exists.' \
      'symlink-present fails closed.' \
      'rg --basename is the sweep flag.'
  } > "$mismatched/tools/souji-verify.spec.md"

  local out st
  set +e
  out=$(env SOUJI_IMPL47_SELFTEST_ACTIVE=1 "$SELF" --drift --json \
    --docs-root "$aligned" \
    --verify-bin "$aligned/tools/souji-verify.sh" \
    --vault-bin "$aligned/tools/souji-vault-verify.sh")
  st=$?
  set -e
  if [ "$st" = 0 ] && printf '%s' "$out" | grep -q '"drift_count":0,'; then
    st_ok "aligned docs: drift_count=0"
  else
    st_bad "aligned docs: exit=$st out=$(printf '%s' "$out" | head -c 400)"
  fi

  set +e
  out=$(env SOUJI_IMPL47_SELFTEST_ACTIVE=1 "$SELF" --drift \
    --docs-root "$mismatched" \
    --verify-bin "$mismatched/tools/souji-verify.sh" \
    --vault-bin "$mismatched/tools/souji-vault-verify.sh")
  st=$?
  set -e
  if [ "$st" = 0 ] && printf '%s\n' "$out" | grep -q $'^DRIFT\tskill-fetch\tDRIFT' \
     && printf '%s\n' "$out" | grep -q $'^DRIFT\tskill-default-ref\tDRIFT' \
     && printf '%s\n' "$out" | grep -q $'^DRIFT\tspec-basename\tDRIFT' \
     && printf '%s\n' "$out" | grep -q $'^SUMMARY\tdrift\t.*drift_count=[1-9]'; then
    st_ok "mismatched docs: skill-fetch, skill-default-ref, spec-basename drift"
  else
    st_bad "mismatched docs: exit=$st"
    printf '%s\n' "$out" | head -40
  fi

  # Installed tool, if present, must still refuse local-master. This is a
  # live regression check, not part of the fixture drift_count.
  if [ -f "$LANE_ROOT/tools/souji-verify.sh" ]; then
    local live
    live=$(VERIFY_BIN="$LANE_ROOT/tools/souji-verify.sh" behavior_local_master)
    if [ "$live" = "NOT-SAFE/pushed-unverifiable" ]; then
      st_ok "installed souji-verify local-master probe ($live)"
    else
      st_bad "installed souji-verify local-master probe got $live"
    fi
  else
    st_bad "installed souji-verify.sh missing"
  fi

  # --- census fixture ---
  local fleet="$tmp/fleet"
  mkdir -p "$fleet"
  local RC="$fleet/clean-shokunin"
  st_init "$RC" master
  printf 'kept\n' > "$RC/kept.txt"
  # Tracked, so the lane stays clean. Census must still not print the bytes.
  mkdir -p "$RC/.ufo/state"
  printf 'CANARY_STATE\n' > "$RC/.ufo/state/live.json"
  printf 'CANARY_WATCH\n' > "$RC/.ufo/watchdog.log"
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
  printf 'CANARY_SECRET_TOKEN\n' > "$RD/credentials.env"

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
  local WT="$fleet/unpushed-extra"
  mkdir -p "$RU/.git/worktrees/wt1" "$WT"
  printf 'ref: refs/heads/master\n' > "$RU/.git/worktrees/wt1/HEAD"
  printf '../..\n' > "$RU/.git/worktrees/wt1/commondir"
  printf '%s\n' "$WT/.git" > "$RU/.git/worktrees/wt1/gitdir"
  printf 'gitdir: %s\n' "$RU/.git/worktrees/wt1" > "$WT/.git"

  local RN="$fleet/noremote-shokunin"
  st_init "$RN" master
  printf 'solo\n' > "$RN/solo.txt"
  local n1
  n1=$(st_commit "$RN" "" "n1")
  git -C "$RN" update-ref refs/heads/master "$n1"

  mkdir -p "$fleet/plain-dir" "$fleet/.hidden-shokunin" "$fleet/research"
  printf 'nope\n' > "$fleet/plain-dir/x.txt"
  st_init "$fleet/.hidden-shokunin" master
  st_init "$fleet/research" master
  printf 'not-a-lane\n' > "$fleet/research/x.txt"
  local r1
  r1=$(st_commit "$fleet/research" "" "r1")
  git -C "$fleet/research" update-ref refs/heads/master "$r1"

  local ctsv1="$tmp/c1.tsv" ctsv2="$tmp/c2.tsv"
  env -u GIT_DIR SOUJI_IMPL47_SELFTEST_ACTIVE=1 \
    "$SELF" --census --root "$fleet" > "$ctsv1"
  env -u GIT_DIR SOUJI_IMPL47_SELFTEST_ACTIVE=1 \
    "$SELF" --census --root "$fleet" > "$ctsv2"
  if cmp -s "$ctsv1" "$ctsv2"; then st_ok "census repeat byte-identical"
  else st_bad "census repeat differs"; diff -u "$ctsv1" "$ctsv2" || true; fi

  if grep -q 'CANARY_STATE\|CANARY_WATCH\|CANARY_SECRET_TOKEN' "$ctsv1"; then
    st_bad "census leaked forbidden or secret contents"
  else
    st_ok "census did not print secret or forbidden contents"
  fi
  if grep -q 'plain-dir\|hidden-shokunin\|/research' "$ctsv1"; then
    st_bad "census included a non-lane dir"
  else
    st_ok "census skipped plain, dot, and non-lane dirs"
  fi
  local nrows
  nrows=$(grep -c $'^CENSUS\t' "$ctsv1" || true)
  if [ "$nrows" = 4 ]; then st_ok "census row count 4"
  else st_bad "census row count $nrows want 4"; cat "$ctsv1"; fi

  local row
  row=$(grep -F $'\tclean-shokunin\t' "$ctsv1" | head -1 || true)
  case "$row" in
    *$'\t''clean') st_ok "clean-shokunin flags=clean" ;;
    *) st_bad "clean-shokunin row='$row'" ;;
  esac
  row=$(grep -F $'\tdirty-shokunin\t' "$ctsv1" | head -1 || true)
  case "$row" in
    *dirty*scratch*secret-shaped*) st_ok "dirty flags ($row)" ;;
    *) st_bad "dirty flags missing in '$row'" ;;
  esac
  row=$(grep -F $'\tunpushed-shokunin\t' "$ctsv1" | head -1 || true)
  case "$row" in
    *$'\t''1'$'\t''2'$'\t'*) st_ok "unpushed unpushed=1 worktrees=2" ;;
    *) st_bad "unpushed counts '$row'" ;;
  esac
  case "$row" in
    *unpushed*) st_ok "unpushed flag present" ;;
    *) st_bad "unpushed flag absent" ;;
  esac
  row=$(grep -F $'\tnoremote-shokunin\t' "$ctsv1" | head -1 || true)
  case "$row" in
    *no-remote*) st_ok "noremote flag present" ;;
    *) st_bad "noremote flag absent '$row'" ;;
  esac
  case "$row" in
    *$'\t''clean') st_bad "noremote was marked clean" ;;
    *) st_ok "noremote is not clean" ;;
  esac

  {
    printf '%s\n' "$CENSUS_HEADER"
    grep $'^CENSUS\t' "$ctsv1" | cut -f2-
  } > "$tmp/c-saved.tsv"
  set +e
  out=$(env -u GIT_DIR SOUJI_IMPL47_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$tmp/c-saved.tsv" 2>&1)
  st=$?
  set -e
  if [ "$st" = 0 ] && [ "$(printf '%s\n' "$out" | grep -c $'^DIFF\t' || true)" = 1 ]; then
    st_ok "compare identical: exit 0 header only"
  else
    st_bad "compare identical: exit=$st lines=$(printf '%s\n' "$out" | grep -c . || true)"
  fi
  printf 'more\n' >> "$RD/.scratch/note.txt"
  rm -f -- "$RD/untracked.txt"
  set +e
  out=$(env -u GIT_DIR SOUJI_IMPL47_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$tmp/c-saved.tsv" 2>&1)
  st=$?
  set -e
  if [ "$st" = 3 ] && printf '%s\n' "$out" | grep -q $'dirty-shokunin\tdirty\t'; then
    st_ok "compare mutation: exit 3 and dirty delta"
  else
    st_bad "compare mutation: exit=$st"
  fi
  printf 'nope\n' > "$tmp/bad.tsv"
  set +e
  env -u GIT_DIR SOUJI_IMPL47_SELFTEST_ACTIVE=1 \
    "$SELF" --root "$fleet" --compare "$tmp/bad.tsv" >/dev/null 2>&1
  st=$?
  set -e
  if [ "$st" = 2 ]; then st_ok "bad compare header exits 2"
  else st_bad "bad compare header exit=$st"; fi

  set +e
  env -u GIT_DIR SOUJI_IMPL47_SELFTEST_ACTIVE=1 "$SELF" --no-such-flag >/dev/null 2>&1
  st=$?
  set -e
  if [ "$st" = 2 ]; then st_ok "unknown flag exits 2"
  else st_bad "unknown flag exit=$st"; fi
  set +e
  env -u GIT_DIR SOUJI_IMPL47_SELFTEST_ACTIVE=1 "$SELF" --header-budget 201 >/dev/null 2>&1
  st=$?
  set -e
  if [ "$st" = 2 ]; then st_ok "header-budget 201 exits 2"
  else st_bad "header-budget 201 exit=$st"; fi

  # --- scratch classifier ---
  local scratch="$tmp/scratch" outside="$tmp/outside-secret"
  mkdir -p "$scratch/sub" "$scratch/.ufo/state"
  printf '# title\n' > "$scratch/note.md"
  printf 'CANARY_SECRET\n' > "$scratch/credentials.env"
  printf 'CANARY_STATE\n' > "$scratch/.ufo/state/live.json"
  printf 'CANARY_WATCH\n' > "$scratch/.ufo/watchdog.log"
  printf '' > "$scratch/empty.txt"
  printf 'x\0y\n' > "$scratch/nul.bin"
  printf '#!/bin/sh\necho hi\n' > "$scratch/script"
  printf 'plain words\n' > "$scratch/noext"
  # 200 bytes of A then a canary that must not appear in output
  # 200 bytes then a canary that a 200-byte header read must not see
  dd if=/dev/zero bs=200 count=1 2>/dev/null | tr '\0' 'A' > "$scratch/ambiguous"
  printf 'CANARY_PAST200\n' >> "$scratch/ambiguous"
  printf '{"a":1}\n' > "$scratch/sub/a.json"
  printf 'CANARY_OUTSIDE\n' > "$outside"
  ln -s "$outside" "$scratch/link"

  local s1="$tmp/s1.txt" s2="$tmp/s2.txt"
  env SOUJI_IMPL47_SELFTEST_ACTIVE=1 "$SELF" --scratch --scratch-root "$scratch" > "$s1"
  env SOUJI_IMPL47_SELFTEST_ACTIVE=1 "$SELF" --scratch --scratch-root "$scratch" > "$s2"
  if cmp -s "$s1" "$s2"; then st_ok "scratch repeat byte-identical"
  else st_bad "scratch repeat differs"; diff -u "$s1" "$s2" || true; fi
  if grep -q 'CANARY_SECRET\|CANARY_STATE\|CANARY_WATCH\|CANARY_OUTSIDE\|CANARY_PAST200' "$s1"; then
    st_bad "scratch output leaked a canary"
  else
    st_ok "scratch output has no canary (secret, forbidden, symlink target, past-byte-200)"
  fi
  if grep -q $'^HANDOFF\t.*\tNOT-SAFE\t' "$s1"; then st_ok "handoff is NOT-SAFE"
  else st_bad "handoff missing NOT-SAFE"; fi
  if grep -E $'^HANDOFF\t.*\tSAFE\t' "$s1"; then st_bad "handoff emitted SAFE"
  else st_ok "handoff did not emit SAFE"; fi
  local cc
  cc=$(grep $'^CLASS\tsecret-shaped\t' "$s1" | head -1 || true)
  case "$cc" in
    CLASS$'\t'secret-shaped$'\t'1$'\t'*) st_ok "secret-shaped count=1" ;;
    *) st_bad "secret-shaped row '$cc'" ;;
  esac
  cc=$(grep $'^CLASS\tsymlink\t' "$s1" | head -1 || true)
  case "$cc" in
    CLASS$'\t'symlink$'\t'1$'\t'*) st_ok "symlink count=1 (not followed)" ;;
    *) st_bad "symlink row '$cc'" ;;
  esac
  cc=$(grep $'^CLASS\text-markdown\t' "$s1" | head -1 || true)
  case "$cc" in
    CLASS$'\t'text-markdown$'\t'1$'\t'*) st_ok "text-markdown count=1" ;;
    *) st_bad "text-markdown row '$cc'" ;;
  esac
  cc=$(grep $'^CLASS\text-json\t' "$s1" | head -1 || true)
  case "$cc" in
    CLASS$'\t'text-json$'\t'1$'\t'*) st_ok "text-json count=1" ;;
    *) st_bad "text-json row '$cc'" ;;
  esac
  cc=$(grep $'^CLASS\tempty\t' "$s1" | head -1 || true)
  case "$cc" in
    CLASS$'\t'empty$'\t'1$'\t'*) st_ok "empty count=1" ;;
    *) st_bad "empty row '$cc'" ;;
  esac
  cc=$(grep $'^CLASS\tbinary-ext\t' "$s1" | head -1 || true)
  case "$cc" in
    CLASS$'\t'binary-ext$'\t'1$'\t'*) st_ok "binary-ext count=1" ;;
    *) st_bad "binary-ext row '$cc'" ;;
  esac
  cc=$(grep $'^CLASS\text-script\t' "$s1" | head -1 || true)
  case "$cc" in
    CLASS$'\t'text-script$'\t'1$'\t'*) st_ok "text-script from header" ;;
    *) st_bad "text-script row '$cc'" ;;
  esac
  cc=$(grep $'^CLASS\text-other\t' "$s1" | head -1 || true)
  case "$cc" in
    CLASS$'\t'text-other$'\t'2$'\t'*) st_ok "text-other count=2 (noext + ambiguous header)" ;;
    *) st_bad "text-other row '$cc'" ;;
  esac
  if grep -q 'forbidden_pruned=2' "$s1"; then st_ok "forbidden surfaces pruned, not opened"
  else st_bad "forbidden_pruned not 2"; grep HANDOFF "$s1"; fi
  # headers should be exactly the ambiguous + noext + script (3), not the secret
  if grep -q 'headers=3' "$s1"; then st_ok "header reads=3 (ambiguous only, secrets not opened)"
  else st_bad "header read count unexpected"; grep HANDOFF "$s1"; fi

  # missing scratch is NOT-SAFE(unreachable), exit 0
  set +e
  out=$(env SOUJI_IMPL47_SELFTEST_ACTIVE=1 "$SELF" --scratch --scratch-root "$tmp/no-such-scratch")
  st=$?
  set -e
  if [ "$st" = 0 ] && printf '%s\n' "$out" | grep -q $'^HANDOFF\t.*\tNOT-SAFE\tunreachable\t'; then
    st_ok "missing scratch: exit 0 NOT-SAFE(unreachable)"
  else
    st_bad "missing scratch: exit=$st"
  fi

  local n
  n=$(grep -nE '^[^#]*git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(fetch|push|commit|branch|checkout|reset|rebase|prune)([[:space:]]|$)' "$SELF" | wc -l || true)
  n=${n// /}
  if [ "${n:-1}" = 0 ]; then st_ok "no forbidden git subcommand in executable lines"
  else st_bad "$n forbidden git invocation(s)"; fi

  case "$tmp" in
    /tmp/impl47-selftest.*|/dev/shm/impl47-selftest.*) st_ok "fixtures under mktemp ($tmp)" ;;
    *) st_bad "fixtures not under mktemp ($tmp)" ;;
  esac

  printf 'selftest: %s checks, %s failed\n' "$((ST_PASS + ST_FAIL))" "$ST_FAIL"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# ---------------------------------------------------------------- main

if [ "$SELFTEST" = 1 ]; then
  run_selftest
fi

command -v git >/dev/null 2>&1 || { printf 'impl-47: git not found\n' >&2; exit 1; }

if [ -n "$COMPARE" ]; then
  emit_compare
  exit $?
fi

rc=0
if [ "$JSON" = 1 ]; then
  emit_json || rc=$?
else
  emit_text || rc=$?
fi
exit "$rc"
