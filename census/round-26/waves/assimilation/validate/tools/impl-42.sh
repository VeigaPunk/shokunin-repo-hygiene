#!/usr/bin/env bash
# impl-42 — round-6 fleet census (seat S42, implementor, independent).
#
# Serves the round claims without removing anything:
#   C1 calibration — docs vs installed tools, drift counted, never guessed AGREE.
#   O1 operability — repeatable dry-run fleet census (receipt taxonomy).
#   K1 coverage    — kotodama .scratch classified read-only (metadata + <=200 byte
#                    headers) plus a handoff note. Removal stays NOT-SAFE.
#
# CLI
#   tools/impl-42.sh [--selftest] [--json]
#                    [--census] [--reconcile] [--kotodama]
#                    [--root PATH] [--lane PATH]
#                    [--out-dir DIR] [--header-bytes N] [--stale-days N]
#
# No mode flag runs all three. Stdout is tagged TSV:
#   DRIFT<TAB>id<TAB>AGREE|DRIFT|to-verify<TAB>doc<TAB>installed
#   CENSUS<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence
#   CLASS<TAB>class<TAB>count<TAB>bytes<TAB>note
#   HANDOFF<TAB>kotodama.scratch<TAB>NOT-SAFE<TAB>receipt<TAB>evidence
#   SUMMARY<TAB>mode<TAB>k=v...
# Copies land under --out-dir (default: mktemp under /tmp). Never the lane tree.
#
# Exit: 0 evaluated (drift>0 is a finding, not a failure); 1 selftest or
# evaluation error; 2 usage. No other codes.
#
# Rails: no git fetch/push/commit/branch/checkout/reset/rebase/prune; no read of
# secret-shaped names; header probe is read(N) with N<=200; GIT_OPTIONAL_LOCKS=0
# so status cannot refresh the index; .ufo/state, .ufo/watchdog.log, the live
# ledger, and ~/.config are never opened. Uncertain => NOT-SAFE.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
export LC_ALL=C
export GIT_OPTIONAL_LOCKS=0

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
LANE_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
FLEET_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$LANE_ROOT")}"
FLEET_ROOT="$(readlink -m -- "$FLEET_ROOT" 2>/dev/null || printf '%s' "$FLEET_ROOT")"

LANE_OVERRIDE=""
ROOT_OVERRIDE=""
OUT_DIR=""
HEADER_BYTES=200
STALE_DAYS=1
JSON=0
SELFTEST=0
DO_CENSUS=0
DO_RECON=0
DO_KOTO=0

usage() {
  sed -n '2,32p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-2}"
}
usage_err() { printf 'impl-42: %s\n' "$1" >&2; usage 2; }

san() {
  local s=${1:-}
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

emit() {
  if [ "$JSON" = 1 ]; then
    local kind=$1
    shift
    printf '{"kind":"%s"' "$(json_escape "$kind")"
    local i=0 f
    for f in "$@"; do
      i=$((i + 1))
      printf ',"f%d":"%s"' "$i" "$(json_escape "$f")"
    done
    printf '}\n'
  else
    local first=1 f
    for f in "$@"; do
      if [ "$first" = 1 ]; then printf '%s' "$f"; first=0
      else printf '\t%s' "$f"; fi
    done
    printf '\n'
  fi
}

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

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --census) DO_CENSUS=1; shift ;;
    --reconcile) DO_RECON=1; shift ;;
    --kotodama) DO_KOTO=1; shift ;;
    --stale-days)
      [ $# -ge 2 ] || usage_err "--stale-days needs N"
      STALE_DAYS=$2; shift 2 ;;
    --header-bytes)
      [ $# -ge 2 ] || usage_err "--header-bytes needs N"
      HEADER_BYTES=$2; shift 2 ;;
    --root)
      [ $# -ge 2 ] || usage_err "--root needs PATH"
      ROOT_OVERRIDE=$2; shift 2 ;;
    --lane)
      [ $# -ge 2 ] || usage_err "--lane needs PATH"
      LANE_OVERRIDE=$2; shift 2 ;;
    --out-dir)
      [ $# -ge 2 ] || usage_err "--out-dir needs DIR"
      OUT_DIR=$2; shift 2 ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown flag: $1" ;;
    *) usage_err "unexpected argument: $1" ;;
  esac
done
[ $# -eq 0 ] || usage_err "unexpected argument: $1"

case "$STALE_DAYS" in
  ''|*[!0-9]*) usage_err "--stale-days must be a non-negative integer" ;;
esac
case "$HEADER_BYTES" in
  ''|*[!0-9]*) usage_err "--header-bytes must be an integer" ;;
esac
if [ "$HEADER_BYTES" -gt 200 ]; then
  usage_err "--header-bytes refuses >200 (contract: head -c 200 max)"
fi

if [ -n "$ROOT_OVERRIDE" ]; then
  FLEET_ROOT=$(canon "$ROOT_OVERRIDE")
fi
if [ -n "$LANE_OVERRIDE" ]; then
  LANE_ROOT=$(canon "$LANE_OVERRIDE")
fi

SKILL="$LANE_ROOT/SKILL.md"
SPEC="$LANE_ROOT/tools/souji-verify.spec.md"
VERIFY="$LANE_ROOT/tools/souji-verify.sh"
SCORECARD="$LANE_ROOT/SCORECARD.md"

# ------------------------------------------------------------------- reconcile --

ticks_of_line() { # $1 file, $2 awk pattern selecting one line
  local file=$1 pat=$2 line
  [ -f "$file" ] || return 0
  line=$(awk -v pat="$pat" 'index($0, pat) {print; exit}' "$file" 2>/dev/null || true)
  [ -n "$line" ] || return 0
  printf '%s\n' "$line" | grep -o '`[^`]*`' | tr -d '`' | LC_ALL=C sort -u
}

run_reconcile() { # writes $1 (tsv). prints drift count. emits DRIFT rows.
  local dest=$1
  : > "$dest"
  local -a rows=()
  recon() { # id status doc installed
    rows+=("$1"$'\t'"$2"$'\t'"$(san "$3")"$'\t'"$(san "$4")")
  }

  if [ ! -f "$SKILL" ]; then
    recon "C1.pushed-receipt" "DRIFT" "SKILL.md missing" "to-verify"
  elif grep -q -F 'git fetch' "$SKILL" && grep -q -F 'origin/main' "$SKILL"; then
    local spec_note="spec missing"
    if [ -f "$SPEC" ] && grep -q -F 'git fetch' "$SPEC"; then
      spec_note="spec forbids fetch; local refs/heads/master never establishes pushed"
    fi
    recon "C1.pushed-receipt" "DRIFT" \
      "SKILL.md pushed receipt uses git fetch and origin/main" \
      "installed souji-verify: no fetch; origin/HEAD or single origin/*; else pushed-unverifiable ($spec_note)"
  else
    recon "C1.pushed-receipt" "AGREE" \
      "SKILL.md does not hard-code git fetch + origin/main" \
      "souji-verify resolve_default_ref"
  fi

  local skill_ticks spec_ticks diff_note
  skill_ticks=$(ticks_of_line "$SKILL" 'known scratch type' | tr '\n' ' ' || true)
  spec_ticks=$(ticks_of_line "$SPEC" '`stale`:' | tr '\n' ' ' || true)
  if [ ! -f "$SKILL" ] || [ ! -f "$SPEC" ]; then
    recon "C1.stale-patterns" "to-verify" "skill or spec missing" "to-verify"
  elif [ "$(ticks_of_line "$SKILL" 'known scratch type')" = "$(ticks_of_line "$SPEC" '`stale`:' )" ] \
       && [ -n "${skill_ticks// /}" ]; then
    recon "C1.stale-patterns" "AGREE" "stale backtick tokens match" "spec stale family"
  else
    diff_note="skill=[${skill_ticks:-none}] spec=[${spec_ticks:-none}]"
    recon "C1.stale-patterns" "DRIFT" \
      "SKILL.md stale tokens differ from spec ($diff_note)" \
      "souji-verify scratch_type follows the spec families, not the skill list"
  fi

  if [ -f "$SKILL" ] && grep -q -F 'rg -l <basename>' "$SKILL" \
     && [ -f "$SPEC" ] && grep -q -F 'souji-shokunin/census/**' "$SPEC"; then
    recon "C1.stale-sweep-exclusions" "DRIFT" \
      "SKILL.md sweep is bare rg -l with no census/tests/quarantine exclusion" \
      "spec D3 excludes souji-shokunin/census/** tests/** .ufo-quarantine/**"
  elif [ -f "$SKILL" ] && [ -f "$SPEC" ]; then
    recon "C1.stale-sweep-exclusions" "AGREE" "sweep exclusion text does not contradict" "spec D3"
  else
    recon "C1.stale-sweep-exclusions" "to-verify" "skill or spec missing" "to-verify"
  fi

  if [ -f "$SKILL" ] && grep -q -F '19 prunable worktrees' "$SKILL"; then
    local lore_n="missing" gd2d_n="missing"
    if [ -d "$FLEET_ROOT/lore-shokunin/.git" ] || [ -e "$FLEET_ROOT/lore-shokunin/.git" ]; then
      lore_n=$(git -C "$FLEET_ROOT/lore-shokunin" worktree list 2>/dev/null | grep -c . || true)
    fi
    if [ -e "$FLEET_ROOT/game-dev-2d-shokunin/.git" ]; then
      gd2d_n=$(git -C "$FLEET_ROOT/game-dev-2d-shokunin" worktree list 2>/dev/null | grep -c . || true)
    fi
    if [ "$lore_n" = "missing" ]; then
      recon "C1.known-surfaces-worktrees" "to-verify" \
        "SKILL.md still says lore 19 prunable" "lore repo not in this root"
    elif [ "$lore_n" != "20" ]; then
      recon "C1.known-surfaces-worktrees" "DRIFT" \
        "SKILL.md Known surfaces: lore 19 prunable (implies 20 worktree-list lines)" \
        "git worktree list | wc -l: lore=$lore_n gd2d=$gd2d_n"
    else
      recon "C1.known-surfaces-worktrees" "AGREE" "lore worktree-list lines=20" "gd2d=$gd2d_n"
    fi
  else
    recon "C1.known-surfaces-worktrees" "AGREE" \
      "SKILL.md does not freeze the mint 19-prunable figure" "not asserted"
  fi

  if [ -f "$SKILL" ] && grep -q -F '553M' "$SKILL"; then
    local measured="not-measured"
    local scratch="$FLEET_ROOT/kotodama-shokunin/.scratch"
    if [ -d "$scratch" ] && [ ! -L "$scratch" ]; then
      measured=$(du -sb -P -- "$scratch" 2>/dev/null | awk '{print $1}' || true)
      measured=${measured:-du-failed}
    fi
    recon "C1.kotodama-size-doc" "DRIFT" \
      "SKILL.md Known surfaces still says 553M" \
      "du -sb kotodama .scratch = ${measured} (553*1024*1024=579862528; figure is historical)"
  else
    recon "C1.kotodama-size-doc" "AGREE" "SKILL.md does not claim 553M" "no stale size figure"
  fi

  if [ -f "$SPEC" ] && grep -q -F 'bash + coreutils + git + rg only' "$SPEC" \
     && [ -f "$VERIFY" ] && grep -q -E '(^|[^[:alnum:]_])grep([^[:alnum:]_]|$)' "$VERIFY"; then
    recon "C1.tool-allowlist" "DRIFT" \
      "spec: bash + coreutils + git + rg only" \
      "souji-verify.sh source contains grep (installed behavior is the contract)"
  elif [ -f "$SPEC" ] && [ -f "$VERIFY" ]; then
    recon "C1.tool-allowlist" "AGREE" "allowlist scan found no contradiction" "souji-verify.sh"
  else
    recon "C1.tool-allowlist" "to-verify" "spec or verify missing" "to-verify"
  fi

  if [ -f "$VERIFY" ] && grep -q -F 'rg -l' "$VERIFY" && ! grep -q -F -- '--hidden' "$VERIFY"; then
    recon "C1.hidden-ref-sweep" "DRIFT" \
      "a live-reference sweep that skips hidden files can false-SAFE a scratch cite" \
      "souji-verify.sh count_live_refs has rg -l and no --hidden"
  elif [ -f "$VERIFY" ]; then
    recon "C1.hidden-ref-sweep" "AGREE" "verify sweep passes --hidden or does not use rg -l" "count_live_refs"
  else
    recon "C1.hidden-ref-sweep" "to-verify" "verify missing" "to-verify"
  fi

  if [ -f "$SCORECARD" ]; then
    local flat cov_t cal_t op_t sat
    flat=$(tr '\n' ' ' < "$SCORECARD")
    cov_t=$(grep -E '^\| coverage \|' "$SCORECARD" | head -1 | awk -F'|' '{gsub(/ /,"",$3); print $3}')
    cal_t=$(grep -E '^\| calibration \|' "$SCORECARD" | head -1 | awk -F'|' '{gsub(/ /,"",$3); print $3}')
    op_t=$(grep -E '^\| operability \|' "$SCORECARD" | head -1 | awk -F'|' '{gsub(/ /,"",$3); print $3}')
    sat=$(printf '%s\n' "$flat" | grep -oE 'Coverage [0-9]+, operability [0-9]+, calibration [0-9]+' | head -1 || true)
    if [ -n "$sat" ] && [ -n "$cov_t" ] && [ -n "$cal_t" ] && [ -n "$op_t" ]; then
      local scov sop scal
      scov=$(printf '%s\n' "$sat" | sed -n 's/.*Coverage \([0-9][0-9]*\).*/\1/p')
      sop=$(printf '%s\n' "$sat" | sed -n 's/.*operability \([0-9][0-9]*\).*/\1/p')
      scal=$(printf '%s\n' "$sat" | sed -n 's/.*calibration \([0-9][0-9]*\).*/\1/p')
      if [ "$scov" = "$cov_t" ] && [ "$sop" = "$op_t" ] && [ "$scal" = "$cal_t" ]; then
        recon "C1.scorecard-saturation" "AGREE" "saturation numbers match the axis table" "SCORECARD.md"
      else
        recon "C1.scorecard-saturation" "DRIFT" \
          "saturation paragraph ($sat) disagrees with the axis table" \
          "table coverage=$cov_t calibration=$cal_t operability=$op_t"
      fi
    else
      recon "C1.scorecard-saturation" "to-verify" "scorecard present but table or saturation line unparsed" "to-verify"
    fi
  fi

  local drift=0 line id status
  for line in "${rows[@]}"; do
    printf '%s\n' "$line" >> "$dest"
    id=${line%%$'\t'*}
    status=${line#*$'\t'}; status=${status%%$'\t'*}
    local doc inst
    doc=${line#*$'\t'}; doc=${doc#*$'\t'}; doc=${doc%%$'\t'*}
    inst=${line##*$'\t'}
    emit DRIFT "$id" "$status" "$doc" "$inst"
    if [ "$status" = "DRIFT" ]; then drift=$((drift + 1)); fi
  done
  emit SUMMARY "reconcile" "claims=${#rows[@]}" "drift=$drift" "file=$dest"
  printf 'impl-42: reconcile drift=%s claims=%s\n' "$drift" "${#rows[@]}" >&2
}

# --------------------------------------------------------------------- census --

resolve_default_ref() {
  local repo=$1 b refs n
  b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)
  if [ -n "$b" ] && git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b" 2>/dev/null; then
    printf 'refs/remotes/origin/%s\n' "$b"
    return 0
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' refs/remotes/origin 2>/dev/null | grep -v '^refs/remotes/origin/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c . || true)
  if [ "$n" = 1 ]; then printf '%s\n' "$refs"; return 0; fi
  return 1
}

# Append one census record. $1 is the array name. Never SAFE for a repo root.
census_add() {
  local -n _dst=$1
  _dst+=("$2"$'\t'"$3"$'\t'"$4"$'\t'"$(san "$5")")
}

census_repo() {
  local _name=$1
  local repo=$2 unpushed dirty branch
  if [ ! -e "$repo/.git" ]; then
    census_add "$_name" "$repo" "NOT-SAFE" "unreachable" "no-.git"
    return 0
  fi
  unpushed=$(git -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null || printf 'unverifiable')
  dirty=$(git -C "$repo" status --porcelain --untracked-files=normal 2>/dev/null | grep -c . || true)
  if ! branch=$(resolve_default_ref "$repo"); then branch="pushed-unverifiable"; fi
  if [ "$unpushed" = "unverifiable" ]; then
    census_add "$_name" "$repo" "NOT-SAFE" "unpushed" "unpushed=unverifiable dirty=${dirty:-0} default=$branch"
  elif [ "${unpushed:-0}" -gt 0 ]; then
    census_add "$_name" "$repo" "NOT-SAFE" "unpushed" "unpushed=$unpushed dirty=${dirty:-0} default=$branch"
  elif [ "${dirty:-0}" -gt 0 ]; then
    census_add "$_name" "$repo" "NOT-SAFE" "dirty" "unpushed=0 dirty=$dirty default=$branch"
  else
    census_add "$_name" "$repo" "NOT-SAFE" "none" "unpushed=0 dirty=0 default=$branch repo-root-not-a-removal-target stale-days=$STALE_DAYS"
  fi
}

census_worktrees() {
  local _name=$1
  local repo=$2 line path="" head="" branch=""
  [ -e "$repo/.git" ] || return 0
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      'worktree '*)
        if [ -n "$path" ] && [ "$path" != "$repo" ]; then
          census_one_worktree "$_name" "$repo" "$path" "$head" "$branch"
        fi
        path=${line#worktree }; head=""; branch="" ;;
      'HEAD '*) head=${line#HEAD } ;;
      'branch '*) branch=${line#branch } ;;
      detached*) branch="" ;;
    esac
  done < <(git -C "$repo" worktree list --porcelain 2>/dev/null || true)
  if [ -n "$path" ] && [ "$path" != "$repo" ]; then
    census_one_worktree "$_name" "$repo" "$path" "$head" "$branch"
  fi
}

census_one_worktree() {
  local _name=$1
  local repo=$2 path=$3 head=$4 branch=$5 unique=0 unpushed=0 dir_state="absent"
  [ -d "$path" ] && dir_state="present"
  if [ -n "$branch" ]; then
    unpushed=$(git -C "$repo" rev-list --count "$branch" --not --remotes 2>/dev/null || printf 0)
    if [ "${unpushed:-0}" -gt 0 ]; then
      census_add "$_name" "$path" "NOT-SAFE" "unpushed-branch" \
        "owner=$(basename -- "$repo") branch=$branch unpushed=$unpushed dir=$dir_state"
      return 0
    fi
  fi
  if [ -n "$head" ]; then
    unique=$(git -C "$repo" rev-list --count "$head" --not --all 2>/dev/null || printf 0)
  fi
  if [ "$dir_state" = "absent" ] && [ "${unique:-0}" = 0 ] && [ "${unpushed:-0}" = 0 ]; then
    census_add "$_name" "$path" "SAFE" "metadata-prune" \
      "owner=$(basename -- "$repo") dir=absent unique=0 unpushed=0 head=${head:0:12}"
    return 0
  fi
  if [ "$dir_state" = "present" ]; then
    local dirty
    dirty=$(git -C "$path" status --porcelain --untracked-files=normal 2>/dev/null | grep -c . || true)
    if [ "${dirty:-0}" -gt 0 ]; then
      census_add "$_name" "$path" "NOT-SAFE" "dirty" "owner=$(basename -- "$repo") dirty=$dirty"
      return 0
    fi
  fi
  census_add "$_name" "$path" "NOT-SAFE" "none" \
    "owner=$(basename -- "$repo") dir=$dir_state unique=${unique:-?} unpushed=${unpushed:-0}"
}

census_snapshot() {
  local _name=$1
  local snap="$FLEET_ROOT/shokunin.conf.full-roster-20261015"
  local live="$FLEET_ROOT/shokunin.conf"
  if [ -f "$snap" ] && [ -f "$live" ]; then
    if cmp -s -- "$snap" "$live"; then
      census_add "$_name" "$snap" "NOT-SAFE" "none" "cmp=IDENTICAL (mint measured DIFFER; not a removal receipt)"
    else
      local sb lb
      sb=$(wc -c < "$snap" | tr -d ' ')
      lb=$(wc -c < "$live" | tr -d ' ')
      census_add "$_name" "$snap" "NOT-SAFE" "stale-snapshot-not-receipt" \
        "cmp=DIFFER snap_bytes=$sb live_bytes=$lb; unique edits to-verify; no removal"
    fi
  fi
}

run_census() { # $1 dest tsv
  local dest=$1
  local -a rows=()
  : > "$dest"
  if [ -e "$FLEET_ROOT/.git" ]; then
    census_repo rows "$FLEET_ROOT"
    census_worktrees rows "$FLEET_ROOT"
    census_snapshot rows
  else
    census_add rows "$FLEET_ROOT" "NOT-SAFE" "unreachable" "fleet root has no .git"
  fi
  local d
  local -a lanes=()
  shopt -s nullglob
  for d in "$FLEET_ROOT"/*/; do
    local base
    base=$(basename -- "$d")
    case "$base" in
      .*) continue ;;
    esac
    if [ -e "${d%/}/.git" ]; then lanes+=("${d%/}"); fi
  done
  shopt -u nullglob
  if [ "${#lanes[@]}" -gt 0 ]; then
    local sorted
    sorted=$(printf '%s\n' "${lanes[@]}" | LC_ALL=C sort)
    while IFS= read -r d; do
      [ -n "$d" ] || continue
      census_repo rows "$d"
      census_worktrees rows "$d"
    done <<< "$sorted"
  fi
  local line safe=0
  if [ "${#rows[@]}" -gt 0 ]; then
    printf '%s\n' "${rows[@]}" | LC_ALL=C sort > "$dest"
  fi
  while IFS= read -r line || [ -n "$line" ]; do
    [ -n "$line" ] || continue
    local path verdict receipt evidence
    path=${line%%$'\t'*}
    verdict=${line#*$'\t'}; verdict=${verdict%%$'\t'*}
    receipt=${line#*$'\t'}; receipt=${receipt#*$'\t'}; receipt=${receipt%%$'\t'*}
    evidence=${line##*$'\t'}
    emit CENSUS "$path" "$verdict" "$receipt" "$evidence"
    if [ "$verdict" = "SAFE" ]; then safe=$((safe + 1)); fi
  done < "$dest"
  emit SUMMARY "census" "rows=$(grep -c . "$dest" || true)" "safe=$safe" "file=$dest" "stale-days=$STALE_DAYS"
}

# ------------------------------------------------------------------- kotodama ---

classify_scratch() { # $1 scratch $2 dest-class-tsv $3 dest-meta. prints nothing but files.
  local scratch=$1 dest=$2 meta=$3
  python3 - "$scratch" "$HEADER_BYTES" "$dest" "$meta" << 'PY'
import os, sys, collections
scratch, nbytes, dest, meta = sys.argv[1:]
nbytes = int(nbytes)
if nbytes > 200:
    sys.stderr.write("header cap exceeded\n")
    sys.exit(2)

def secret_component(name: str) -> bool:
    lc = name.lower()
    if lc in {".env", ".envrc"} or lc.startswith(".env.") or lc.endswith(".env") or lc.endswith(".pem"):
        return True
    if "credential" in lc or "secret" in lc or lc.startswith("id_"):
        return True
    return False

def secret_path(path: str) -> bool:
    return any(secret_component(p) for p in path.split("/") if p)

def forbidden(rel: str) -> bool:
    parts = rel.split("/")
    for i, p in enumerate(parts):
        if p == ".ufo" and i + 1 < len(parts) and parts[i + 1] == "state":
            return True
        if p == ".ufo" and i + 1 < len(parts) and parts[i + 1] == "watchdog.log":
            return True
    return False

def header_class(path: str, size: int) -> str:
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    if size == 0:
        return "empty"
    try:
        with open(path, "rb") as fh:
            blob = fh.read(nbytes)
    except OSError:
        return "unreadable"
    if not blob:
        return "empty"
    if b"\x00" in blob:
        return "binary-nul"
    if blob.startswith(b"%PDF") or blob.startswith(b"\x89PNG") or blob.startswith(b"\xff\xd8\xff") or blob.startswith(b"GIF8"):
        return "binary-media"
    if blob.startswith(b"PACK"):
        return "git-pack"
    stripped = blob.lstrip()
    if stripped.startswith(b"#!"):
        return "script"
    if stripped[:1] in (b"{", b"["):
        return "json-text"
    if stripped.startswith(b"#") or stripped.startswith(b"---"):
        return "markdown-or-yaml"
    if ext in {"pdf", "jpg", "jpeg", "png", "gif", "webp", "gz", "zip", "pack", "idx", "pyc", "bin"}:
        return "binary-media"
    if ext in {"md", "yml", "yaml"}:
        return "markdown-or-yaml"
    if ext == "json":
        return "json-text"
    if ext in {"py", "sh"}:
        return "script"
    if ext in {"txt", "out", "log", "err", "tsv", "sample", "expected", "stdout", "stderr"}:
        return "text-log"
    if ext in {"html", "xml"}:
        return "markup"
    return "text-or-unknown"

counts = collections.Counter()
bytes_by = collections.Counter()
top_files = collections.Counter()
top_bytes = collections.Counter()
top_kind = {}
walked = classified = 0
secret_n = sym_n = dir_n = file_n = opened = forbidden_n = 0

def add(cls: str, size: int) -> None:
    global classified
    counts[cls] += 1
    bytes_by[cls] += size
    classified += 1

# root
walked += 1
add("directory", 0)

for dirpath, dirnames, filenames in os.walk(scratch, followlinks=False):
    # classify symlink directories without descending
    real_dirs = []
    for d in dirnames:
        p = os.path.join(dirpath, d)
        rel = os.path.relpath(p, scratch)
        walked += 1
        top = rel.split("/", 1)[0]
        if os.path.islink(p):
            sym_n += 1
            add("symlink", 0)
            top_kind.setdefault(top, "symlink")
            continue
        if secret_path(rel):
            secret_n += 1
            add("secrets-refusal", 0)
            real_dirs.append(d)
            continue
        if forbidden(rel):
            forbidden_n += 1
            add("forbidden-surface", 0)
            real_dirs.append(d)
            continue
        dir_n += 1
        add("directory", 0)
        real_dirs.append(d)
        top_kind.setdefault(top, "dir")
    dirnames[:] = real_dirs
    for fn in filenames:
        p = os.path.join(dirpath, fn)
        rel = os.path.relpath(p, scratch)
        walked += 1
        top = rel.split("/", 1)[0]
        if os.path.islink(p):
            sym_n += 1
            add("symlink", 0)
            continue
        if secret_path(rel):
            secret_n += 1
            add("secrets-refusal", 0)
            continue
        if forbidden(rel):
            forbidden_n += 1
            add("forbidden-surface", 0)
            continue
        try:
            size = os.lstat(p).st_size
        except OSError:
            add("unreadable", 0)
            continue
        file_n += 1
        opened += 1
        cls = header_class(p, size)
        add(cls, size)
        top_files[top] += 1
        top_bytes[top] += size
        top_kind.setdefault(top, "dir")

unclassified = walked - classified
with open(dest, "w", encoding="utf-8") as fh:
    for cls in sorted(counts):
        fh.write(f"{cls}\t{counts[cls]}\t{bytes_by[cls]}\tmetadata+header<={nbytes}; body not retained\n")
    for name in sorted(set(list(top_files) + list(top_kind))):
        fh.write(f"TOP\t{name}\t{top_kind.get(name, 'dir')}\t{top_bytes[name]}\t{top_files[name]}\n")
with open(meta, "w", encoding="utf-8") as fh:
    fh.write(f"walked\t{walked}\n")
    fh.write(f"classified\t{classified}\n")
    fh.write(f"unclassified\t{unclassified}\n")
    fh.write(f"files\t{file_n}\n")
    fh.write(f"dirs\t{dir_n}\n")
    fh.write(f"symlinks\t{sym_n}\n")
    fh.write(f"secret_unopened\t{secret_n}\n")
    fh.write(f"forbidden_unopened\t{forbidden_n}\n")
    fh.write(f"header_opens\t{opened}\n")
    fh.write(f"header_cap\t{nbytes}\n")
if unclassified != 0:
    sys.exit(1)
PY
}

run_kotodama() { # $1 class tsv, $2 meta, $3 handoff md
  local dest=$1 meta=$2 note=$3
  local repo="$FLEET_ROOT/kotodama-shokunin"
  local scratch="$repo/.scratch"
  if [ ! -d "$scratch" ] || [ -L "$scratch" ]; then
    emit HANDOFF "kotodama.scratch" "NOT-SAFE" "unreachable" "scratch missing or is a symlink"
    printf 'unreachable\t0\t0\tmissing\n' > "$dest"
    printf 'verdict: NOT-SAFE\nreceipt: unreachable\n' > "$note"
    return 0
  fi
  case "$scratch" in
    "$HOME/.config"|"$HOME/.config"/*|*/.ufo/state|*/.ufo/state/*) usage_err "refusing protected scratch path" ;;
  esac
  classify_scratch "$scratch" "$dest.raw" "$meta"
  local unpushed dirty du_b find_n
  unpushed=$(git -C "$repo" rev-list --count --branches --not --remotes 2>/dev/null || printf unverifiable)
  dirty=$(git -C "$repo" status --porcelain --untracked-files=normal 2>/dev/null | grep -c . || true)
  du_b=$(du -sb -P -- "$scratch" 2>/dev/null | awk '{print $1}' || true)
  find_n=$(find "$scratch" -print 2>/dev/null | grep -c . || true)
  local walked classified unclassified files dirs syms secrets forbidden opens
  walked=$(awk -F'\t' '$1=="walked"{print $2}' "$meta")
  classified=$(awk -F'\t' '$1=="classified"{print $2}' "$meta")
  unclassified=$(awk -F'\t' '$1=="unclassified"{print $2}' "$meta")
  files=$(awk -F'\t' '$1=="files"{print $2}' "$meta")
  dirs=$(awk -F'\t' '$1=="dirs"{print $2}' "$meta")
  syms=$(awk -F'\t' '$1=="symlinks"{print $2}' "$meta")
  secrets=$(awk -F'\t' '$1=="secret_unopened"{print $2}' "$meta")
  forbidden=$(awk -F'\t' '$1=="forbidden_unopened"{print $2}' "$meta")
  opens=$(awk -F'\t' '$1=="header_opens"{print $2}' "$meta")

  : > "$dest"
  while IFS= read -r line || [ -n "$line" ]; do
    [ -n "$line" ] || continue
    case "$line" in
      TOP$'\t'*)
        printf '%s\n' "$line" >> "$dest"
        ;;
      *)
        local cls count bytes note_f
        cls=${line%%$'\t'*}
        count=${line#*$'\t'}; count=${count%%$'\t'*}
        bytes=${line#*$'\t'}; bytes=${bytes#*$'\t'}; bytes=${bytes%%$'\t'*}
        note_f=${line##*$'\t'}
        printf '%s\t%s\t%s\t%s\n' "$cls" "$count" "$bytes" "$note_f" >> "$dest"
        emit CLASS "$cls" "$count" "$bytes" "$note_f"
        ;;
    esac
  done < "$dest.raw"

  local receipt="live-unpushed"
  if [ "$unpushed" = "unverifiable" ]; then
    receipt="unpushed"
  elif [ "${unpushed:-0}" = 0 ] && [ "${dirty:-0}" = 0 ]; then
    receipt="none"
  elif [ "${unpushed:-0}" = 0 ]; then
    receipt="dirty"
  fi
  local mismatch=0
  if [ "${find_n:-0}" != "${walked:-0}" ]; then mismatch=1; fi

  cat > "$note" <<EOF
# kotodama .scratch handoff (impl-42, read-only)

verdict: NOT-SAFE
receipt: ${receipt}
removal: NOT authorized. A false SAFE on this tree is the lane's worst failure.
owning repo: ${repo}
unpushed (git rev-list --count --branches --not --remotes): ${unpushed}
dirty porcelain lines (git status --porcelain, untracked dirs collapsed): ${dirty}
du -sb: ${du_b}
find inode count (includes scratch root): ${find_n}
walked: ${walked}
classified: ${classified}
unclassified: ${unclassified}
find_mismatch: ${mismatch}
files opened for header: ${opens}
header cap bytes: ${HEADER_BYTES}
dirs: ${dirs}
symlinks not followed: ${syms}
secret-shaped unopened: ${secrets}
forbidden-surface unopened: ${forbidden}
class table: ${dest}
snapshot: point-in-time. The owning lane is live; counts are not a removal receipt.
EOF

  emit HANDOFF "kotodama.scratch" "NOT-SAFE" "$receipt" \
    "unpushed=${unpushed} dirty=${dirty} du_sb=${du_b} walked=${walked} classified=${classified} unclassified=${unclassified} find=${find_n} mismatch=${mismatch} files=${files} dirs=${dirs} links=${syms} secrets_unopened=${secrets} header_opens=${opens} cap=${HEADER_BYTES} note=$note"
  emit SUMMARY "kotodama" "unclassified=$unclassified" "mismatch=$mismatch" "file=$dest" "note=$note"
  if [ "${unclassified:-1}" != 0 ]; then
    return 1
  fi
  return 0
}

# -------------------------------------------------------------------- selftest --

st_commit() { # $1 repo $2 parent-or-empty $3 msg -> sha on stdout
  local repo=$1 parent=$2 msg=$3 tr sha
  tr=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr")
  fi
  printf '%s' "$sha"
}

write_lane_docs() { # $1 dir $2 drifted|aligned
  local lane=$1 mode=$2
  mkdir -p "$lane/tools"
  if [ "$mode" = "drifted" ]; then
    cat > "$lane/SKILL.md" <<'EOF'
| `pushed` | after `git fetch`, merge-base against origin | `git fetch -q && git merge-base --is-ancestor <commit> origin/main && echo PUSHED` |
| `stale` | known scratch type (`.scratch/`, `*.tmp`, checkpoint blobs, `out/`, `reports/round-*/**-draft.*`), nothing references it (`rg -l <basename>` across the owning repo returns 0 live hits) | `rg -l <basename> <repo>` |
- kotodama-shokunin: 553M `.scratch/`
- lore-shokunin: 19 prunable worktrees (`git worktree list`).
EOF
    cat > "$lane/tools/souji-verify.spec.md" <<'EOF'
bash + coreutils + git + rg only
NO `git fetch` — existing refs only.
local refs such as `refs/heads/master` can NEVER establish a pushed receipt
- `stale`: scratch type (`.scratch/`, `*.out`, `*.log`, checkpoint json/png, `*-draft.*`) AND zero live references
`souji-shokunin/census/**`
EOF
    printf 'rg -l --fixed-strings\n' > "$lane/tools/souji-verify.sh"
    cat > "$lane/SCORECARD.md" <<'EOF'
| coverage | 8 | x |
| calibration | 7 | x |
| operability | 8 | x |
Saturation line: 8 per axis. Coverage 8, operability 7, calibration 6 — calibration flavor
EOF
  else
    cat > "$lane/SKILL.md" <<'EOF'
| `pushed` | ancestor of the resolved remote-tracking default ref; no fetch | `git merge-base --is-ancestor <commit> <origin-ref>` |
| `stale` | known scratch type (`.scratch/`, `*.out`, `*.log`, checkpoint json/png, `*-draft.*`) | excluded census sweep |
EOF
    cat > "$lane/tools/souji-verify.spec.md" <<'EOF'
coreutils + git
NO `git fetch` — existing refs only.
- `stale`: scratch type (`.scratch/`, `*.out`, `*.log`, checkpoint json/png, `*-draft.*`) AND zero live references
`souji-shokunin/census/**`
EOF
    printf 'rg -l --hidden --fixed-strings\n' > "$lane/tools/souji-verify.sh"
  fi
}

run_selftest() {
  local st fleet rc out
  st=$(mktemp -d "${TMPDIR:-/tmp}/impl-42-selftest.XXXXXX")
  cleanup_selftest() {
    case "$st" in
      /tmp/impl-42-selftest.*|/var/tmp/impl-42-selftest.*) rm -rf -- "$st" ;;
    esac
  }
  trap cleanup_selftest RETURN
  fleet="$st/fleet"
  mkdir -p "$fleet"

  # drifted docs live in a side lane so reconcile is asserted exactly
  write_lane_docs "$st/drifted-lane" drifted
  write_lane_docs "$st/aligned-lane" aligned

  # owner with two linked worktrees: one prunable (SAFE), one unpushed (NOT-SAFE)
  local own="$fleet/wt-owner-shokunin"
  git init -q --initial-branch=master "$own"
  git -C "$own" symbolic-ref HEAD refs/heads/master
  printf 'base\n' > "$own/base.txt"
  git -C "$own" add -A >/dev/null
  local c1
  c1=$(st_commit "$own" "" "c1")
  git -C "$own" update-ref refs/heads/master "$c1"
  git -C "$own" symbolic-ref HEAD refs/heads/master
  git -C "$own" update-ref refs/remotes/origin/master "$c1"
  git -C "$own" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$own" read-tree "$c1"
  git -C "$own" update-ref refs/heads/wt-done "$c1"
  local wt_safe="$fleet/wt-done-missing"
  git -C "$own" worktree add -q "$wt_safe" wt-done
  rm -rf -- "$wt_safe"
  local idx="$st/idx" blob
  GIT_INDEX_FILE="$idx" git -C "$own" read-tree "$c1"
  printf 'extra\n' > "$own/extra.txt"
  blob=$(git -C "$own" hash-object -w -- "$own/extra.txt")
  GIT_INDEX_FILE="$idx" git -C "$own" update-index --add --cacheinfo "100644,$blob,extra.txt"
  local tr c2
  tr=$(GIT_INDEX_FILE="$idx" git -C "$own" write-tree)
  c2=$(printf 'c2\n' | git -C "$own" commit-tree "$tr" -p "$c1")
  git -C "$own" update-ref refs/heads/wt-r98 "$c2"
  rm -f -- "$own/extra.txt"
  git -C "$own" read-tree "$c1"
  local wt_bad="$fleet/wt-r98-missing"
  git -C "$own" worktree add -q "$wt_bad" wt-r98
  rm -rf -- "$wt_bad"

  # kotodama-shaped scratch: secret name must not be opened, symlink not followed
  local koto="$fleet/kotodama-shokunin"
  mkdir -p "$koto/.scratch/bucket" "$koto/.scratch/.ufo/state"
  printf 'SHOULD-NOT-APPEAR-IN-OUTPUT\n' > "$koto/.scratch/bucket/app.env"
  chmod 000 "$koto/.scratch/bucket/app.env"
  printf 'CANARY-LINK-TARGET\n' > "$st/outside-target.txt"
  ln -s "$st/outside-target.txt" "$koto/.scratch/bucket/alias.md"
  printf '# title\nhello\n' > "$koto/.scratch/bucket/note.md"
  printf '{"k":1}\n' > "$koto/.scratch/bucket/row.json"
  printf 'abc\0def' > "$koto/.scratch/bucket/blob.bin"
  printf 'state-secret\n' > "$koto/.scratch/.ufo/state/live.json"
  git init -q --initial-branch=master "$koto"
  git -C "$koto" symbolic-ref HEAD refs/heads/master
  printf 'k\n' > "$koto/keep.txt"
  git -C "$koto" add keep.txt >/dev/null
  local k1
  k1=$(st_commit "$koto" "" "k1")
  git -C "$koto" update-ref refs/heads/master "$k1"
  git -C "$koto" symbolic-ref HEAD refs/heads/master
  git -C "$koto" read-tree "$k1"

  # fleet root repo so census_repo has a root row
  git init -q --initial-branch=master "$fleet"
  git -C "$fleet" symbolic-ref HEAD refs/heads/master
  printf 'root\n' > "$fleet/root.txt"
  git -C "$fleet" add root.txt >/dev/null
  local r1
  r1=$(st_commit "$fleet" "" "r1")
  git -C "$fleet" update-ref refs/heads/master "$r1"

  set +e
  out=$(SHOKUNIN_ROOT="$fleet" "$SELF" --root "$fleet" --lane "$st/drifted-lane" \
    --out-dir "$st/out" --header-bytes 200 2>"$st/err")
  rc=$?
  set -e
  if [ "$rc" != 0 ]; then
    printf 'FAIL drifted run exit=%s\n' "$rc" >&2
    printf '%s\n' "$out" >&2
    cat "$st/err" >&2 || true
    return 1
  fi
  if printf '%s\n' "$out" | grep -q 'SHOULD-NOT-APPEAR-IN-OUTPUT'; then
    printf 'FAIL secret body leaked\n' >&2
    return 1
  fi
  if printf '%s\n' "$out" | grep -q 'CANARY-LINK-TARGET'; then
    printf 'FAIL symlink target leaked\n' >&2
    return 1
  fi
  if printf '%s\n' "$out" | grep -q 'state-secret'; then
    printf 'FAIL forbidden surface leaked\n' >&2
    return 1
  fi
  if ! grep -q $'CLASS\tsecrets-refusal\t' <<< "$out"; then
    printf 'FAIL secrets-refusal missing\n' >&2
    return 1
  fi
  if ! grep -q $'HANDOFF\tkotodama.scratch\tNOT-SAFE' <<< "$out"; then
    printf 'FAIL handoff not NOT-SAFE\n' >&2
    return 1
  fi
  if ! grep -q $'DRIFT\tC1.pushed-receipt\tDRIFT\t' <<< "$out"; then
    printf 'FAIL pushed-receipt drift not detected\n' >&2
    return 1
  fi
  if ! grep -q $'DRIFT\tC1.scorecard-saturation\tDRIFT\t' <<< "$out"; then
    printf 'FAIL scorecard drift not detected\n' >&2
    return 1
  fi
  if ! grep -q $'CENSUS\t'"$wt_safe"$'\tSAFE\tmetadata-prune\t' <<< "$out"; then
    printf 'FAIL metadata-prune SAFE missing for %s\n' "$wt_safe" >&2
    printf '%s\n' "$out" | grep CENSUS >&2 || true
    return 1
  fi
  if ! grep -q $'CENSUS\t'"$wt_bad"$'\tNOT-SAFE\tunpushed-branch\t' <<< "$out"; then
    printf 'FAIL unpushed-branch NOT-SAFE missing\n' >&2
    return 1
  fi
  # repo roots must not be SAFE
  if awk -F'\t' '$1=="CENSUS" && $3=="SAFE" && $4!="metadata-prune" {found=1} END{exit !found}' <<< "$out"; then
    printf 'FAIL non-prune SAFE row\n' >&2
    return 1
  fi
  local unc
  unc=$(awk -F'\t' '$1=="unclassified"{print $2}' "$st/out/kotodama.meta" 2>/dev/null || echo missing)
  # meta path is beside the class file; run_kotodama writes the path we pass.
  # The driver below uses fixed names. Here the default run wrote them.
  if ! grep -q $'SUMMARY\tkotodama\tunclassified=0\t' <<< "$out"; then
    printf 'FAIL kotodama not fully classified\n' >&2
    printf '%s\n' "$out" | grep SUMMARY >&2 || true
    return 1
  fi

  # repeatability of the class table and census file
  SHOKUNIN_ROOT="$fleet" "$SELF" --root "$fleet" --lane "$st/drifted-lane" \
    --out-dir "$st/out2" --header-bytes 200 >/dev/null
  if ! cmp -s "$st/out/census.tsv" "$st/out2/census.tsv"; then
    printf 'FAIL census not repeatable\n' >&2
    diff -u "$st/out/census.tsv" "$st/out2/census.tsv" >&2 || true
    return 1
  fi
  if ! cmp -s "$st/out/kotodama.tsv" "$st/out2/kotodama.tsv"; then
    printf 'FAIL kotodama classes not repeatable\n' >&2
    diff -u "$st/out/kotodama.tsv" "$st/out2/kotodama.tsv" >&2 || true
    return 1
  fi

  # aligned lane: those doc claims agree (drift count from reconcile file)
  set +e
  out=$(SHOKUNIN_ROOT="$fleet" "$SELF" --reconcile --root "$fleet" --lane "$st/aligned-lane" \
    --out-dir "$st/aligned-out" 2>"$st/aligned.err")
  rc=$?
  set -e
  if [ "$rc" != 0 ]; then
    printf 'FAIL aligned reconcile exit=%s\n' "$rc" >&2
    return 1
  fi
  if grep -q $'DRIFT\tC1\.[^[:space:]]*\tDRIFT\t' <<< "$out"; then
    printf 'FAIL aligned lane still drifted\n' >&2
    printf '%s\n' "$out" >&2
    return 1
  fi
  if ! grep -q $'DRIFT\tC1.pushed-receipt\tAGREE\t' <<< "$out"; then
    printf 'FAIL aligned pushed-receipt not AGREE\n' >&2
    return 1
  fi

  set +e
  "$SELF" --header-bytes 201 --out-dir "$st/out3" >/dev/null 2>"$st/err2"
  rc=$?
  set -e
  if [ "$rc" != 2 ]; then
    printf 'FAIL header-bytes 201 exit=%s want 2\n' "$rc" >&2
    return 1
  fi

  # source audit: no forbidden git porcelain outside comments
  local n
  n=$(grep -nE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase|prune)( |$)' "$SELF" | wc -l || true)
  n=${n// /}
  if [ "${n:-1}" != 0 ]; then
    printf 'FAIL forbidden git invocations: %s\n' "$n" >&2
    return 1
  fi

  printf 'PASS impl-42 selftest\n'
  return 0
}

# ----------------------------------------------------------------------- main --

prepare_out() {
  OWNED=0
  if [ -z "$OUT_DIR" ]; then
    OUT_DIR=$(mktemp -d "${TMPDIR:-/tmp}/impl-42.XXXXXX")
    OWNED=1
  fi
  case "$OUT_DIR" in
    /tmp/*|/var/tmp/*) ;;
    *)
      [ -d "$OUT_DIR" ] || usage_err "--out-dir must already exist when not under /tmp"
      case "$OUT_DIR" in
        */.ufo/state|*/.ufo/state/*|*/.ufo/watchdog.log|*obsidian-ledger.tsv) usage_err "refusing protected out-dir" ;;
      esac
      ;;
  esac
  mkdir -p -- "$OUT_DIR"
}

if [ "$SELFTEST" = 1 ]; then
  run_selftest
  exit $?
fi

if [ "$DO_CENSUS" = 0 ] && [ "$DO_RECON" = 0 ] && [ "$DO_KOTO" = 0 ]; then
  DO_CENSUS=1
  DO_RECON=1
  DO_KOTO=1
fi

prepare_out
printf 'impl-42 out-dir=%s root=%s lane=%s\n' "$OUT_DIR" "$FLEET_ROOT" "$LANE_ROOT" >&2

rc=0
if [ "$DO_RECON" = 1 ]; then
  run_reconcile "$OUT_DIR/reconcile.tsv"
fi
if [ "$DO_CENSUS" = 1 ]; then
  run_census "$OUT_DIR/census.tsv"
fi
if [ "$DO_KOTO" = 1 ]; then
  if ! run_kotodama "$OUT_DIR/kotodama.tsv" "$OUT_DIR/kotodama.meta" "$OUT_DIR/kotodama-handoff.md"; then
    rc=1
  fi
fi
if [ "$OWNED" = 1 ]; then
  printf 'impl-42 wrote %s\n' "$OUT_DIR" >&2
fi
exit "$rc"
