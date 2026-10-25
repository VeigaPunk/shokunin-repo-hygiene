#!/usr/bin/env bash
# impl-43 — round-6 fleet census (seat S43, implementor).
#
# Round claims this script serves (dry-run only; the parent installs):
#   C1 calibration — reconcile SKILL.md / spec / installed tools; drift count.
#   O1 operability — repeatable fleet census (receipt taxonomy, no removal).
#   K1 coverage    — classify kotodama-shokunin/.scratch fully, read-only.
#
# CLI
#   tools/impl-43.sh [--selftest] [--json] [--stale-days N]
#                    [--out-dir DIR] [--root PATH]
#                    [--census] [--reconcile] [--kotodama]
#                    [--header-bytes N]
#
# Default (no mode flag) runs reconcile + census + kotodama and writes three
# files under --out-dir (default: a mktemp dir under /tmp, never the lane
# tree, never the live ledger):
#   reconcile.tsv   doc-claim vs installed-tool behavior
#   census.tsv      one row per fleet hygiene surface
#   kotodama.tsv    one class-aggregate row + a handoff note on stderr/stdout
#
# Output contract (stdout, one line per artifact or class):
#   CENSUS<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-reason<TAB>evidence
#   DRIFT<TAB>claim-id<TAB>AGREE|DRIFT<TAB>doc<TAB>installed
#   CLASS<TAB>class<TAB>count<TAB>bytes<TAB>note
#   HANDOFF<TAB>kotodama.scratch<TAB>NOT-SAFE<TAB>live-unpushed<TAB>...
#
# Exit: 0 evaluated clean (drift may be >0; drift is a finding, not a crash);
#       1 selftest failure; 2 usage. No other codes.
#
# Read-only rails
#   * No git fetch/push/commit/branch/checkout/reset/rebase/prune/rm.
#   * No read of secret-shaped paths (basename *.env / .env / .env.* / .envrc /
#     *credential* / *secret* / id_* / *.pem, case-insensitive). Those rows are
#     classified secrets-refusal from the name alone.
#   * Kotodama content probe is `head -c N` (default 200) on non-secret,
#     non-binary regular files only, and only to label the class — never to
#     dump a body into the census.
#   * Never touches corpus/knowledge/obsidian-ledger.tsv, .ufo/state,
#     .ufo/watchdog.log, or ~/.config. Writes only under /tmp (or an explicit
#     --out-dir the caller already owns).
#   * When uncertain, the verdict is NOT-SAFE.
#
# Repeatability: same tree + same --stale-days => same TSV rows. Timestamps
# appear only in the HANDOFF evidence field as observed counts, not as row
# keys. du/find order is sorted before emit.
set -uo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
export LC_ALL=C

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
LANE_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
FLEET_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$LANE_ROOT")}"
FLEET_ROOT="$(readlink -m -- "$FLEET_ROOT" 2>/dev/null || printf '%s' "$FLEET_ROOT")"

VERIFY="${SOUJI_VERIFY:-$LANE_ROOT/tools/souji-verify.sh}"
VAULT_VERIFY="${SOUJI_VAULT_VERIFY:-$LANE_ROOT/tools/souji-vault-verify.sh}"
SPEC="$LANE_ROOT/tools/souji-verify.spec.md"
SKILL="$LANE_ROOT/SKILL.md"

STALE_DAYS=1
JSON=0
SELFTEST=0
DO_CENSUS=0
DO_RECON=0
DO_KOTO=0
HEADER_BYTES=200
OUT_DIR=""
ROOT_OVERRIDE=""

usage() {
  sed -n '2,42p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "${1:-2}"
}
usage_err() { printf 'impl-43: %s\n' "$1" >&2; usage 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --stale-days)
      [ $# -ge 2 ] || usage_err "--stale-days needs N"
      STALE_DAYS="$2"; shift 2 ;;
    --out-dir)
      [ $# -ge 2 ] || usage_err "--out-dir needs DIR"
      OUT_DIR="$2"; shift 2 ;;
    --root)
      [ $# -ge 2 ] || usage_err "--root needs PATH"
      ROOT_OVERRIDE="$2"; shift 2 ;;
    --census) DO_CENSUS=1; shift ;;
    --reconcile) DO_RECON=1; shift ;;
    --kotodama) DO_KOTO=1; shift ;;
    --header-bytes)
      [ $# -ge 2 ] || usage_err "--header-bytes needs N"
      HEADER_BYTES="$2"; shift 2 ;;
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
  usage_err "--header-bytes refuses >200 (seat contract: head -c 200 max)"
fi

if [ "$DO_CENSUS" = 0 ] && [ "$DO_RECON" = 0 ] && [ "$DO_KOTO" = 0 ]; then
  DO_CENSUS=1; DO_RECON=1; DO_KOTO=1
fi

if [ -n "$ROOT_OVERRIDE" ]; then
  FLEET_ROOT="$(readlink -m -- "$ROOT_OVERRIDE" 2>/dev/null || printf '%s' "$ROOT_OVERRIDE")"
fi

TMP_OWNED=0
if [ -z "$OUT_DIR" ]; then
  OUT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/impl-43.XXXXXX")"
  TMP_OWNED=1
fi
case "$OUT_DIR" in
  /tmp/*|/var/tmp/*) : ;;
  *)
    # Caller-supplied dir is allowed only if it already exists and is not a
    # protected surface. Never create lane-tree output ourselves.
    [ -d "$OUT_DIR" ] || usage_err "--out-dir must already exist when not under /tmp"
    case "$OUT_DIR" in
      */.ufo/state|*/.ufo/state/*|*/.ufo/watchdog.log|*/obsidian-ledger.tsv) usage_err "refusing protected out-dir" ;;
    esac
    ;;
esac
mkdir -p -- "$OUT_DIR" || usage_err "cannot use out-dir $OUT_DIR"

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

emit() { # kind + fields, tab-separated; also mirrored to the mode TSV
  if [ "$JSON" = 1 ]; then
    local kind=$1; shift
    printf '{"kind":"%s"' "$(json_escape "$kind")"
    local i=0 f
    for f in "$@"; do
      i=$((i+1))
      printf ',"f%d":"%s"' "$i" "$(json_escape "$f")"
    done
    printf '}\n'
  else
    local first=1 f
    for f in "$@"; do
      if [ "$first" = 1 ]; then printf '%s' "$f"; first=0
      else printf '\t%s' "$f"
      fi
    done
    printf '\n'
  fi
}

# True when any path component is secret-shaped. Name only — never opens.
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

# Default-branch ref. Remote-tracking only. Local heads never establish pushed.
resolve_default_ref() {
  local repo=$1 b refs n
  b=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)
  if [ -n "$b" ] && git -C "$repo" show-ref --verify --quiet "refs/remotes/origin/$b" 2>/dev/null; then
    printf 'refs/remotes/origin/%s\n' "$b"
    return 0
  fi
  refs=$(git -C "$repo" for-each-ref --format='%(refname)' 'refs/remotes/origin' 2>/dev/null | grep -v '^refs/remotes/origin/HEAD$' || true)
  n=$(printf '%s\n' "$refs" | grep -c . || true)
  if [ "$n" = 1 ]; then
    printf '%s\n' "$refs"
    return 0
  fi
  return 1
}

# ---------------------------------------------------------------- reconcile --
# Each row is a doc claim the installed tools contradict, or an AGREE control.
# Counting is exact: DRIFT rows / total claims. Uncertain claims are DRIFT
# with installed=to-verify rather than a guessed AGREE.

recon_file="$OUT_DIR/reconcile.tsv"

recon_row() { # id, status, doc, installed
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" >> "$recon_file"
  emit DRIFT "$1" "$2" "$3" "$4"
}

run_reconcile() {
  : > "$recon_file"
  local skill_line spec_line
  # C1.1 SKILL.md pushed receipt requires `git fetch` and hard-codes origin/main.
  # Installed souji-verify.sh: no fetch; resolve origin/HEAD; local master is
  # never a pushed receipt (r5 amendment, spec lines 36-40).
  skill_line=$(grep -n -F 'origin/main' "$SKILL" 2>/dev/null | head -1 || true)
  if grep -q -F 'git fetch' "$SKILL" 2>/dev/null \
     && printf '%s\n' "$skill_line" | grep -q 'origin/main'; then
    recon_row "C1.pushed-receipt" "DRIFT" \
      "SKILL.md: git fetch && merge-base origin/main (${skill_line%%:*})" \
      "souji-verify.sh: no fetch; refs/remotes/origin/HEAD or single origin/* ; local heads never pushed"
  else
    recon_row "C1.pushed-receipt" "AGREE" \
      "SKILL.md pushed receipt matches installed resolver" \
      "souji-verify.sh resolve_default_ref"
  fi

  # C1.2 spec r5 amendment vs SKILL.md stale patterns (*.tmp / out/ / reports).
  if grep -q -F '*.tmp' "$SKILL" && ! grep -q -F '*.tmp' "$SPEC"; then
    recon_row "C1.stale-patterns" "DRIFT" \
      "SKILL.md stale set adds *.tmp, out/, reports/round-*/**-draft.* beyond the spec's four families" \
      "souji-verify.sh scratch_type: .scratch/ | *.out | *.log | *-draft.* | checkpoint json/png | launch-*.json"
  else
    recon_row "C1.stale-patterns" "AGREE" "SKILL.md stale set ⊆ spec" "souji-verify.sh scratch_type"
  fi

  # C1.3 SKILL.md stale command uses bare `rg -l <basename>` with no census exclusion.
  if grep -q -F 'rg -l <basename>' "$SKILL" \
     && grep -q -F 'souji-shokunin/census/**' "$SPEC"; then
    recon_row "C1.stale-sweep-exclusions" "DRIFT" \
      "SKILL.md: rg -l <basename> <repo> with no census/tests/quarantine exclusion (D3)" \
      "spec + souji-verify.sh count_live_refs excludes census/** tests/** .ufo-quarantine/**"
  else
    recon_row "C1.stale-sweep-exclusions" "AGREE" "SKILL.md sweep exclusions match spec D3" "count_live_refs"
  fi

  # C1.4 known-surfaces counts in SKILL.md are mint-time, not current.
  # Measured here, not asserted from memory.
  local lore_n gd2d_n
  lore_n=$(git -C "$FLEET_ROOT/lore-shokunin" worktree list 2>/dev/null | wc -l | tr -d ' ')
  gd2d_n=$(git -C "$FLEET_ROOT/game-dev-2d-shokunin" worktree list 2>/dev/null | wc -l | tr -d ' ')
  if grep -q -F '19 prunable worktrees' "$SKILL" && [ "${lore_n:-0}" != 20 ]; then
    recon_row "C1.known-surfaces-worktrees" "DRIFT" \
      "SKILL.md Known surfaces: lore 19 prunable, gd2d 5 prunable (mint figures)" \
      "measured worktree-list lines: lore=${lore_n:-missing} gd2d=${gd2d_n:-missing} (includes main)"
  else
    recon_row "C1.known-surfaces-worktrees" "to-verify" \
      "SKILL.md worktree figures not re-derived as a contradiction" \
      "lore_lines=${lore_n:-missing} gd2d_lines=${gd2d_n:-missing}"
  fi

  # C1.5 kotodama size: SKILL.md says 553M; live du is the census's job.
  if grep -q -F '553M' "$SKILL"; then
    recon_row "C1.kotodama-size-doc" "DRIFT" \
      "SKILL.md Known surfaces: kotodama .scratch 553M (mint figure, 2026-10-18 11:45)" \
      "live size is measured by --kotodama (LOG already corrected 553M→1.9G; do not trust the skill figure)"
  fi

  # C1.6 spec allows bash+coreutils+git+rg; installed verify uses grep/find/xargs
  # (r5 seat-51 finding). Confirm by a name scan, not by executing them.
  if grep -q -E '(^|[^a-z])grep([^a-z]|$)' "$VERIFY" && grep -q -F 'bash + coreutils + git + rg only' "$SPEC"; then
    recon_row "C1.tool-allowlist" "DRIFT" \
      "spec: bash + coreutils + git + rg only" \
      "souji-verify.sh source contains grep/find/xargs (r5 seat-51 E5; behavior still the installed contract)"
  else
    recon_row "C1.tool-allowlist" "AGREE" "spec allowlist matches verify source scan" "souji-verify.sh"
  fi

  # C1.7 hidden-file stale sweep (r5 seat-51 HIGH). Documented as open drift
  # until a parent fix lands. Detection: count_live_refs does not pass --hidden.
  if grep -q -F 'rg -l --no-ignore' "$VERIFY" && ! grep -q -F -- '--hidden' "$VERIFY"; then
    recon_row "C1.hidden-ref-sweep" "DRIFT" \
      "spec D3 sweep must see live references; rg default skips hidden files" \
      "souji-verify.sh count_live_refs has no --hidden (r5 false-SAFE class, open)"
  else
    recon_row "C1.hidden-ref-sweep" "AGREE" "verify sweep passes --hidden" "count_live_refs"
  fi

  local total drift
  total=$(grep -c . "$recon_file" || true)
  drift=$(grep -c $'^[^[:space:]]\+\tDRIFT\t' "$recon_file" || true)
  emit SUMMARY "reconcile" "claims=$total" "drift=$drift" "file=$recon_file"
}

# ----------------------------------------------------------------- census ----

census_file="$OUT_DIR/census.tsv"

census_row() { # path, verdict, receipt, evidence
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" >> "$census_file"
  emit CENSUS "$1" "$2" "$3" "$4"
}

# Repo-root row. Mirrors souji-verify evaluate_repo_root without calling it
# (a 21-lane sweep must not depend on the tool's ledger walk). NOT-SAFE unless
# unpushed=0 and dirty=0, and even then receipt=none: a clean pushed repo is
# not a removal candidate.
census_repo() {
  local repo=$1 name unpushed dirty branch
  name=$(basename -- "$repo")
  if [ ! -e "$repo/.git" ]; then
    census_row "$repo" "NOT-SAFE" "unreachable" "no-.git"
    return 0
  fi
  unpushed=$(git -C "$repo" log --branches --not --remotes --oneline 2>/dev/null | wc -l | tr -d ' ' || true)
  dirty=$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ' || true)
  if branch=$(resolve_default_ref "$repo"); then
    :
  else
    branch="pushed-unverifiable"
  fi
  if [ "${unpushed:-0}" -gt 0 ]; then
    census_row "$repo" "NOT-SAFE" "unpushed" "unpushed=${unpushed} dirty=${dirty:-0} default=$branch"
  elif [ "${dirty:-0}" -gt 0 ]; then
    census_row "$repo" "NOT-SAFE" "dirty" "unpushed=0 dirty=${dirty} default=$branch"
  else
    census_row "$repo" "NOT-SAFE" "none" "unpushed=0 dirty=0 default=$branch repo-root-not-a-removal-target"
  fi
}

# Worktree registrations other than the main worktree.
census_worktrees() {
  local repo=$1 line path head branch="" kind=""
  [ -e "$repo/.git" ] || return 0
  path=""; head=""; branch=""
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      'worktree '*)
        if [ -n "$path" ] && [ "$path" != "$repo" ]; then
          census_one_worktree "$repo" "$path" "$head" "$branch"
        fi
        path=${line#worktree }; head=""; branch="" ;;
      'HEAD '*) head=${line#HEAD } ;;
      'branch '*) branch=${line#branch } ;;
      'detached'*) branch="" ;;
    esac
  done < <(git -C "$repo" worktree list --porcelain 2>/dev/null || true)
  if [ -n "$path" ] && [ "$path" != "$repo" ]; then
    census_one_worktree "$repo" "$path" "$head" "$branch"
  fi
}

census_one_worktree() {
  local repo=$1 path=$2 head=$3 branch=$4 unique="" unpushed=0 rc=0
  if [ -n "$branch" ] && [ "$branch" != "(detached)" ]; then
    if ! git -C "$repo" show-ref --verify --quiet "$branch" 2>/dev/null; then
      census_row "$path" "NOT-SAFE" "none" "owner=$(basename -- "$repo") branch-ref-missing branch=$branch"
      return 0
    fi
    unpushed=$(git -C "$repo" rev-list --count "$branch" --not --remotes 2>/dev/null)
    rc=$?
    if [ "$rc" -ne 0 ] || [ -z "$unpushed" ]; then
      census_row "$path" "NOT-SAFE" "none" "owner=$(basename -- "$repo") unpushed-count-failed branch=$branch"
      return 0
    fi
    if [ "$unpushed" -gt 0 ]; then
      census_row "$path" "NOT-SAFE" "unpushed-branch" "owner=$(basename -- "$repo") branch=$branch unpushed=$unpushed dir=$([ -d "$path" ] && echo present || echo absent)"
      return 0
    fi
  fi
  if [ -n "$head" ]; then
    unique=$(git -C "$repo" rev-list --count "$head" --not --all 2>/dev/null)
    rc=$?
    if [ "$rc" -ne 0 ] || [ -z "$unique" ]; then
      census_row "$path" "NOT-SAFE" "none" "owner=$(basename -- "$repo") unique-count-failed head=${head:0:12}"
      return 0
    fi
  else
    unique="unknown"
  fi
  if [ ! -d "$path" ] && [ "$unique" = 0 ] && [ "$unpushed" = 0 ]; then
    census_row "$path" "SAFE" "metadata-prune" "owner=$(basename -- "$repo") dir=absent unique=0 head=${head:0:12}"
    return 0
  fi
  if [ -d "$path" ]; then
    local dirty
    dirty=$(git -C "$path" status --porcelain 2>/dev/null | wc -l | tr -d ' ' || true)
    if [ "${dirty:-0}" -gt 0 ]; then
      census_row "$path" "NOT-SAFE" "dirty" "owner=$(basename -- "$repo") dirty=$dirty"
      return 0
    fi
  fi
  census_row "$path" "NOT-SAFE" "none" "owner=$(basename -- "$repo") dir=$([ -d "$path" ] && echo present || echo absent) unique=${unique:-?} unpushed=${unpushed:-0}"
}

# Known mint-demand files at the fleet root. Existence + introducing-commit
# ancestry only. Missing files are NOT-SAFE(unreachable), never SAFE.
census_root_demand() {
  local rel path repo intro ref
  repo="$FLEET_ROOT"
  [ -e "$repo/.git" ] || return 0
  # Conf snapshot is the named stale-snapshot candidate. Classify by cmp
  # against live shokunin.conf; do not call it a duplicate.
  local snap="$repo/shokunin.conf.full-roster-20261015"
  local live="$repo/shokunin.conf"
  if [ -f "$snap" ] && [ -f "$live" ]; then
    if cmp -s -- "$snap" "$live"; then
      census_row "$snap" "NOT-SAFE" "none" "cmp=IDENTICAL-to-live-conf (unexpected; mint measured DIFFER)"
    else
      local sb lb
      sb=$(wc -c < "$snap" | tr -d ' ')
      lb=$(wc -c < "$live" | tr -d ' ')
      census_row "$snap" "NOT-SAFE" "stale-snapshot-not-receipt" "cmp=DIFFER snap_bytes=$sb live_bytes=$lb; stale receipt not granted (unique edits to-verify; no removal)"
    fi
  elif [ -e "$snap" ]; then
    census_row "$snap" "NOT-SAFE" "unreachable" "live conf missing; snapshot not classified"
  fi
}

run_census() {
  : > "$census_file"
  local d
  if [ -e "$FLEET_ROOT/.git" ]; then
    census_repo "$FLEET_ROOT"
    census_worktrees "$FLEET_ROOT"
    census_root_demand
  else
    census_row "$FLEET_ROOT" "NOT-SAFE" "unreachable" "fleet root has no .git"
  fi
  local -a lanes=()
  local lane
  shopt -s nullglob
  for lane in "$FLEET_ROOT"/*-shokunin; do
    [ -d "$lane" ] || continue
    lanes+=("$lane")
  done
  shopt -u nullglob
  # stable order
  if [ "${#lanes[@]}" -gt 0 ]; then
    local sorted
    sorted=$(printf '%s\n' "${lanes[@]}" | LC_ALL=C sort)
    while IFS= read -r d; do
      [ -n "$d" ] || continue
      census_repo "$d"
      census_worktrees "$d"
    done <<< "$sorted"
  fi
  local rows safe
  rows=$(grep -c . "$census_file" || true)
  safe=$(awk -F'\t' '$2=="SAFE"{c++} END{print c+0}' "$census_file")
  emit SUMMARY "census" "rows=$rows" "safe=$safe" "file=$census_file"
}

# ---------------------------------------------------------------- kotodama ---

koto_file="$OUT_DIR/kotodama.tsv"
koto_note="$OUT_DIR/kotodama-handoff.md"

# One-process classifier. Metadata (lstat, extension, name) plus at most
# HEADER_BYTES of each non-secret regular file — the same bound as
# `head -c 200`, not a per-file process (a 500k-file tree does not finish
# that way). Secret-shaped names are never opened. Symlinks are not followed.
run_kotodama() {
  local scratch="$FLEET_ROOT/kotodama-shokunin/.scratch"
  local repo="$FLEET_ROOT/kotodama-shokunin"
  if [ ! -d "$scratch" ]; then
    emit HANDOFF "kotodama.scratch" "NOT-SAFE" "unreachable" "dir missing"
    printf 'class\tcount\tbytes\tnote\nunreachable\t0\t0\tmissing\n' > "$koto_file"
    return 0
  fi
  local unpushed dirty
  unpushed=$(git -C "$repo" log --branches --not --remotes --oneline 2>/dev/null | wc -l | tr -d ' ' || true)
  dirty=$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ' || true)

  local files_tsv="$OUT_DIR/kotodama-files.tsv"
  local top_tsv="$OUT_DIR/kotodama-top.tsv"
  local sum_tsv="$OUT_DIR/kotodama-summary.tsv"
  local py_rc=0
  python3 - "$scratch" "$HEADER_BYTES" "$koto_file" "$files_tsv" "$top_tsv" "$sum_tsv" <<'PY'
import os, sys
scratch, header_n, class_path, files_path, top_path, sum_path = sys.argv[1:7]
header_n = int(header_n)
if header_n < 0 or header_n > 200:
    sys.stderr.write("impl-43: header bound violated\n")
    sys.exit(2)
BINARY_EXT = {
    "pdf","jpg","jpeg","png","gif","webp","gz","zip","pack","idx","rev",
    "bin","pyc","torrent","woff","woff2","mp3","mp4","wav","ogg",
}
TEXT_EXT = {
    "md": "markdown-or-yaml", "markdown": "markdown-or-yaml",
    "json": "json-text", "yml": "markdown-or-yaml", "yaml": "markdown-or-yaml",
    "py": "script", "sh": "script",
    "txt": "text-log", "out": "text-log", "log": "text-log", "err": "text-log",
    "stdout": "text-log", "stderr": "text-log", "sample": "text-log",
    "expected": "text-log", "tsv": "text-log",
    "html": "markup", "xml": "markup",
}
def is_secret(path):
    for comp in path.split("/"):
        if not comp:
            continue
        lc = comp.lower()
        if lc.endswith(".env") or lc == ".env" or lc.startswith(".env.") or lc == ".envrc":
            return True
        if "credential" in lc or "secret" in lc or lc.startswith("id_") or lc.endswith(".pem"):
            return True
    return False
def ext_of(name):
    if "." not in name:
        return ""
    return name.rsplit(".", 1)[-1].lower()
def mostly_text(data):
    if not data:
        return False
    bad = 0
    for b in data:
        if b in (9, 10, 13) or 32 <= b < 127:
            continue
        bad += 1
    return bad * 5 < len(data)
def classify(path, size, ext):
    if is_secret(path):
        return "secrets-refusal", "refused"
    if ext in BINARY_EXT:
        return "binary-media", "skipped-binary-ext"
    if size == 0:
        return "empty", "empty"
    if header_n == 0:
        return TEXT_EXT.get(ext, "unclassified"), "no-header"
    try:
        with open(path, "rb") as fh:
            data = fh.read(header_n)
    except OSError:
        return "unreadable", "unreadable"
    if len(data) > header_n:
        return "unclassified", "over-read"
    if b"\0" in data:
        return "binary-nul", "header"
    if data.startswith(b"#!"):
        return "script", "header"
    if data.startswith(b"---") or data.startswith(b"# "):
        return "markdown-or-yaml", "header"
    if data.startswith(b"{") or data.startswith(b"["):
        return "json-text", "header"
    if data.startswith(b"PACK"):
        return "git-pack", "header"
    if ext in TEXT_EXT:
        return TEXT_EXT[ext], "header"
    if mostly_text(data):
        return "text-or-unknown", "header"
    return "unclassified", "header"
counts = {}
bytes_by = {}
tops = {}
files = dirs = links = other = secrets = 0
rows = []
stack = [scratch]
while stack:
    current = stack.pop()
    try:
        entries = list(os.scandir(current))
    except OSError:
        other += 1
        continue
    for ent in entries:
        try:
            is_link = ent.is_symlink()
            if is_link:
                st = ent.stat(follow_symlinks=False)
                size = st.st_size
                cls, probe = "symlink", "skipped-symlink"
                links += 1
            elif ent.is_dir(follow_symlinks=False):
                dirs += 1
                stack.append(ent.path)
                rel = os.path.relpath(ent.path, scratch)
                top = rel.split(os.sep, 1)[0]
                slot = tops.setdefault(top, [0, 0, 0])
                slot[2] += 1
                continue
            elif ent.is_file(follow_symlinks=False):
                st = ent.stat(follow_symlinks=False)
                size = st.st_size
                cls, probe = classify(ent.path, size, ext_of(ent.name))
                files += 1
                if cls == "secrets-refusal":
                    secrets += 1
            else:
                other += 1
                cls, probe, size = "other", "other", 0
        except OSError:
            other += 1
            cls, probe, size = "unreadable", "unreadable", 0
        counts[cls] = counts.get(cls, 0) + 1
        bytes_by[cls] = bytes_by.get(cls, 0) + size
        rel = os.path.relpath(ent.path, scratch)
        top = rel.split(os.sep, 1)[0]
        slot = tops.setdefault(top, [0, 0, 0])
        slot[0] += 1
        slot[1] += size
        safe_path = ent.path.replace("\t", " ").replace("\n", " ").replace("\r", " ")
        rows.append((safe_path, cls, size, probe))
rows.sort(key=lambda r: r[0])
with open(files_path, "w", encoding="utf-8") as fh:
    fh.write("path\tclass\tbytes\tprobe\n")
    for path, cls, size, probe in rows:
        fh.write(f"{path}\t{cls}\t{size}\t{probe}\n")
with open(class_path, "w", encoding="utf-8") as fh:
    fh.write("class\tcount\tbytes\tnote\n")
    for cls in sorted(counts):
        fh.write(f"{cls}\t{counts[cls]}\t{bytes_by[cls]}\tmetadata+read<={header_n}; body not retained\n")
with open(top_path, "w", encoding="utf-8") as fh:
    fh.write("top\tentries\tbytes\tdirs\n")
    for name in sorted(tops):
        ent_n, byt, dirc = tops[name]
        safe = name.replace("\t", " ").replace("\n", " ")
        fh.write(f"{safe}\t{ent_n}\t{byt}\t{dirc}\n")
with open(sum_path, "w", encoding="utf-8") as fh:
    fh.write("files\tdirs\tlinks\tother\tbytes\tsecrets\tclasses\ttops\n")
    total_bytes = sum(bytes_by.values())
    fh.write(f"{files}\t{dirs}\t{links}\t{other}\t{total_bytes}\t{secrets}\t{len(counts)}\t{len(tops)}\n")
PY
  py_rc=$?
  if [ "$py_rc" -ne 0 ] || [ ! -s "$sum_tsv" ]; then
    emit HANDOFF "kotodama.scratch" "NOT-SAFE" "classifier-failed" "python_rc=$py_rc"
    return 0
  fi
  local files dirs links other bytes_total secret_n classes top_n
  IFS=$'\t' read -r _h < "$sum_tsv"
  IFS=$'\t' read -r files dirs links other bytes_total secret_n classes top_n < <(tail -n 1 "$sum_tsv")
  local line cls cnt byt
  while IFS=$'\t' read -r cls cnt byt _note; do
    [ "$cls" = "class" ] && continue
    [ -n "$cls" ] || continue
    emit CLASS "$cls" "$cnt" "$byt" "header<=${HEADER_BYTES}"
  done < "$koto_file"
  local du_h
  du_h=$(du -sh -- "$scratch" 2>/dev/null | awk '{print $1}')

  local verdict="NOT-SAFE" receipt="live-unpushed"
  if [ "${unpushed:-0}" = 0 ] && [ "${dirty:-0}" = 0 ]; then
    # Still NOT-SAFE: scratch beside a clean tree is not a stale receipt
    # until a reference sweep the parent runs says refs=0. This seat does
    # not grant SAFE(stale) on a 500k-file tree.
    verdict="NOT-SAFE"; receipt="none"
  elif [ "${unpushed:-0}" = 0 ]; then
    receipt="dirty"
  fi

  cat > "$koto_note" <<EOF
# kotodama .scratch handoff (impl-43, read-only)

verdict: ${verdict}
receipt: ${receipt}
owning repo unpushed commits (git log --branches --not --remotes --oneline | wc -l): ${unpushed}
owning repo dirty paths (git status --porcelain | wc -l): ${dirty}
du -sh: ${du_h}
top-level entries: ${top_n}
files: ${files}
dirs: ${dirs}
symlinks: ${links}
other: ${other}
apparent bytes summed from stat (files+links+other, not dirs): ${bytes_total}
secret-shaped paths refused unread: ${secret_n}
header probe: python read(${HEADER_BYTES}) on non-secret regular files (same bound as head -c ${HEADER_BYTES}); known binary extensions skipped unread; NUL => binary-nul; body never retained
classification table: ${koto_file}
per-file index: ${files_tsv}
top-level rollup: ${top_tsv}

largest top-level buckets by bytes:
$(tail -n +2 "$top_tsv" | sort -t$'\t' -k3,3nr | head -8)

Removal: NOT authorized. A false SAFE on this tree is the lane's worst failure.
The mint figure 553M and the SKILL.md known-surface line are historical; this
note is the measurement.
EOF

  emit HANDOFF "kotodama.scratch" "$verdict" "$receipt" \
    "unpushed=${unpushed} dirty=${dirty} du=${du_h} files=${files} dirs=${dirs} links=${links} secrets-refused=${secret_n} classes=${classes} note=$koto_note"
}

# ---------------------------------------------------------------- selftest ---

run_selftest() {
  local st tmp fleet pass=0 fail=0
  st=$(mktemp -d "${TMPDIR:-/tmp}/impl-43-selftest.XXXXXX")
  fleet="$st/fleet"
  export GIT_AUTHOR_NAME=impl-43 GIT_AUTHOR_EMAIL=impl-43@shokunin.local
  export GIT_COMMITTER_NAME=impl-43 GIT_COMMITTER_EMAIL=impl-43@shokunin.local
  mkdir -p "$fleet/alpha-shokunin/.scratch" "$fleet/kotodama-shokunin/.scratch/bucket" \
           "$fleet/lore-shokunin"
  # tiny git repos so census_repo does not blow up
  git init -q --initial-branch=master "$fleet/alpha-shokunin"
  git -C "$fleet/alpha-shokunin" symbolic-ref HEAD refs/heads/master
  printf 'a\n' > "$fleet/alpha-shokunin/a.txt"
  git -C "$fleet/alpha-shokunin" add -A >/dev/null
  local tr sha
  tr=$(git -C "$fleet/alpha-shokunin" write-tree)
  sha=$(printf 'c1\n' | git -C "$fleet/alpha-shokunin" commit-tree "$tr")
  git -C "$fleet/alpha-shokunin" update-ref refs/heads/master "$sha"
  # no remote-tracking ref => census must say pushed-unverifiable, NOT-SAFE
  printf 'old scratch\n' > "$fleet/alpha-shokunin/.scratch/old.out"
  # secret-shaped name inside kotodama scratch — must not be opened
  printf 'SHOULD-NOT-APPEAR-IN-OUTPUT\n' > "$fleet/kotodama-shokunin/.scratch/bucket/app.env"
  printf '# title\nhello\n' > "$fleet/kotodama-shokunin/.scratch/bucket/note.md"
  printf '{"k":1}\n' > "$fleet/kotodama-shokunin/.scratch/bucket/row.json"
  # binary NUL
  printf 'abc\0def' > "$fleet/kotodama-shokunin/.scratch/bucket/blob.dat"
  ln -s note.md "$fleet/kotodama-shokunin/.scratch/bucket/alias.md"
  git init -q --initial-branch=master "$fleet/kotodama-shokunin"
  git -C "$fleet/kotodama-shokunin" symbolic-ref HEAD refs/heads/master
  printf 'k\n' > "$fleet/kotodama-shokunin/keep.txt"
  # never git-add the secret-shaped fixture; add would read it
  git -C "$fleet/kotodama-shokunin" add -- keep.txt >/dev/null
  tr=$(git -C "$fleet/kotodama-shokunin" write-tree)
  sha=$(printf 'k1\n' | git -C "$fleet/kotodama-shokunin" commit-tree "$tr")
  git -C "$fleet/kotodama-shokunin" update-ref refs/heads/master "$sha"
  # unpushed: no origin ref at all, so --branches --not --remotes counts local commits
  git init -q --initial-branch=master "$fleet"
  git -C "$fleet" symbolic-ref HEAD refs/heads/master

  local out rc
  set +e
  out=$(SHOKUNIN_ROOT="$fleet" "$SELF" --root "$fleet" --out-dir "$st/out" --header-bytes 200 2>"$st/err")
  rc=$?
  set -e
  if [ "$rc" != 0 ]; then
    printf 'FAIL selftest exit=%s\n' "$rc" >&2
    printf '%s\n' "$out" >&2
    rm -rf -- "$st"
    return 1
  fi
  # secret body must not leak
  if printf '%s\n' "$out" | grep -q 'SHOULD-NOT-APPEAR-IN-OUTPUT'; then
    printf 'FAIL secret body leaked\n' >&2
    rm -rf -- "$st"
    return 1
  fi
  if ! grep -q $'secrets-refusal' "$st/out/kotodama.tsv"; then
    printf 'FAIL secrets-refusal class missing\n' >&2
    cat "$st/out/kotodama.tsv" >&2
    rm -rf -- "$st"
    return 1
  fi
  if grep -R -F -- 'SHOULD-NOT-APPEAR-IN-OUTPUT' "$st/out" >/dev/null 2>&1; then
    printf 'FAIL secret body leaked into out-dir\n' >&2
    rm -rf -- "$st"
    return 1
  fi
  if ! grep -q $'json-text' "$st/out/kotodama-files.tsv"; then
    printf 'FAIL json-text row missing\n' >&2
    rm -rf -- "$st"
    return 1
  fi
  if ! grep -q $'binary-nul' "$st/out/kotodama-files.tsv"; then
    printf 'FAIL binary-nul row missing\n' >&2
    rm -rf -- "$st"
    return 1
  fi
  if ! grep -q $'refused' "$st/out/kotodama-files.tsv"; then
    printf 'FAIL secret probe was not refused\n' >&2
    rm -rf -- "$st"
    return 1
  fi
  if ! grep -q $'HANDOFF\tkotodama.scratch\tNOT-SAFE' <<< "$out"; then
    printf 'FAIL handoff not NOT-SAFE\n' >&2
    rm -rf -- "$st"
    return 1
  fi
  if ! grep -q $'DRIFT\t' <<< "$out"; then
    # reconcile against the real SKILL.md (script dir), so drift rows exist
    # even when --root is a fixture. If the live skill was fixed, AGREE is ok
    # only when reconcile.tsv has rows.
    if [ ! -s "$st/out/reconcile.tsv" ]; then
      printf 'FAIL empty reconcile\n' >&2
      rm -rf -- "$st"
      return 1
    fi
  fi
  if ! grep -q $'CENSUS\t' <<< "$out"; then
    printf 'FAIL no census rows\n' >&2
    rm -rf -- "$st"
    return 1
  fi
  # repeatability: second run, same rows ignoring nothing (TSV is the contract)
  SHOKUNIN_ROOT="$fleet" "$SELF" --root "$fleet" --out-dir "$st/out2" --header-bytes 200 >/dev/null
  if ! cmp -s "$st/out/census.tsv" "$st/out2/census.tsv"; then
    printf 'FAIL census not repeatable\n' >&2
    diff -u "$st/out/census.tsv" "$st/out2/census.tsv" >&2 || true
    rm -rf -- "$st"
    return 1
  fi
  if ! cmp -s "$st/out/kotodama.tsv" "$st/out2/kotodama.tsv"; then
    printf 'FAIL kotodama classes not repeatable\n' >&2
    rm -rf -- "$st"
    return 1
  fi
  # header bound
  set +e
  "$SELF" --header-bytes 201 --out-dir "$st/out3" >/dev/null 2>"$st/err2"
  rc=$?
  set -e
  if [ "$rc" != 2 ]; then
    printf 'FAIL header-bytes 201 should exit 2, got %s\n' "$rc" >&2
    rm -rf -- "$st"
    return 1
  fi
  printf 'PASS impl-43 selftest\n'
  printf 'OUT %s\n' "$st/out"
  # keep the fixture out dir only on failure; success removes it
  rm -rf -- "$st"
  return 0
}

# ------------------------------------------------------------------- main ----

if [ "$SELFTEST" = 1 ]; then
  run_selftest
  exit $?
fi

printf 'impl-43 out-dir=%s root=%s\n' "$OUT_DIR" "$FLEET_ROOT" >&2

if [ "$DO_RECON" = 1 ]; then
  run_reconcile
fi
if [ "$DO_CENSUS" = 1 ]; then
  run_census
fi
if [ "$DO_KOTO" = 1 ]; then
  run_kotodama
fi

if [ "$TMP_OWNED" = 1 ]; then
  printf 'impl-43 wrote %s (remove when consumed)\n' "$OUT_DIR" >&2
fi
exit 0
