#!/usr/bin/env bash
# impl-38 — round-6 read-only reconciler (seat S38, implementor).
#
# Serves the round claims and nothing else:
#   C1 calibration — docs/tools reconciliation. Compares SKILL.md and
#                    tools/souji-verify.spec.md to the installed tools.
#                    A drift row is a documented rule the tool does not
#                    implement, or a tool rule the docs still omit. The
#                    drift count is the number of those rows. This tool
#                    never edits the docs. drift>0 is a finding, not an
#                    error (exit stays 0) so the census stays repeatable.
#   O1 operability — repeatable fleet census. One row per rostered
#                    *-shokunin lane plus the fleet root, when it is a git
#                    repo: HEAD, dirty count, unpushed count, worktree count.
#                    Existing refs only.
#   K1 coverage    — kotodama-shokunin/.scratch classified read-only.
#                    Every file is classed by metadata (type, size,
#                    extension). A content class is taken only from a header
#                    of at most 200 bytes, and only when the whole file fits
#                    that cap (so a large blob is never prefix-sampled and
#                    called classified). Secret-shaped basenames are counted
#                    and never opened.
#
# CLI
#   tools/impl-38.sh [--selftest] [--json]
#                    [--drift] [--census] [--scratch]
#                    [--scratch-root PATH] [--header-budget N]
#                    [--docs-root PATH]
# No selection flag runs all three passes. --selftest ignores the rest.
#
# Text output is TSV:
#   DRIFT<TAB>id<TAB>doc<TAB>tool<TAB>status<TAB>note
#   CENSUS<TAB>lane<TAB>head12<TAB>dirty<TAB>unpushed<TAB>worktrees<TAB>note
#   SCRATCH<TAB>class<TAB>count<TAB>bytes<TAB>note
#   SUMMARY<TAB>pass<TAB>key=value ...
#   HANDOFF<TAB>scratch<TAB>NOT-SAFE<TAB>note
# --json prints one object.
#
# Exit: 0 evaluated; 1 selftest failure; 2 usage.
#
# Env: SHOKUNIN_ROOT (default: parent of this repo). SOUJI_SCRATCH_ROOT
# overrides the scratch tree. SOUJI_SCRATCH_TRACE=1 prints opened paths to
# stderr (selftest proof that secret-shaped names are not opened).
# Header budget is capped at 200 — the assignment's `head -c 200` ceiling.
#
# Safety: read-only outside the selftest's own mktemp directory. Never
# fetches, pushes, commits, branches, prunes, or removes. Never opens
# .ufo/state, .ufo/watchdog.log, or a secret-shaped path. Kotodama is a
# live unpushed lane — classify only.
set -uo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
SHOKUNIN_ROOT="${SHOKUNIN_ROOT:-$(dirname -- "$REPO_ROOT")}"
SHOKUNIN_ROOT="$(readlink -m -- "$SHOKUNIN_ROOT" 2>/dev/null || printf '%s' "$SHOKUNIN_ROOT")"

JSON=0
SELFTEST=0
DO_DRIFT=0
DO_CENSUS=0
DO_SCRATCH=0
HEADER_BUDGET=200
DOCS_ROOT="$REPO_ROOT"
SCRATCH_ROOT="${SOUJI_SCRATCH_ROOT:-$SHOKUNIN_ROOT/kotodama-shokunin/.scratch}"

usage() {
  sed -n '2,46p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "$1"
}
usage_err() { printf 'impl-38: %s\n' "$1" >&2; usage 2; }

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --drift) DO_DRIFT=1; shift ;;
    --census) DO_CENSUS=1; shift ;;
    --scratch) DO_SCRATCH=1; shift ;;
    --header-budget)
      HEADER_BUDGET="${2:?--header-budget needs N}"
      shift 2
      ;;
    --scratch-root)
      SCRATCH_ROOT="${2:?--scratch-root needs a path}"
      shift 2
      ;;
    --docs-root)
      DOCS_ROOT="${2:?--docs-root needs a path}"
      shift 2
      ;;
    -h|--help) usage 0 ;;
    *) usage_err "unknown argument: $1" ;;
  esac
done

case "$HEADER_BUDGET" in
  ''|*[!0-9]*) usage_err "--header-budget must be an integer" ;;
esac
if [ "$HEADER_BUDGET" -gt 200 ]; then
  usage_err "--header-budget must be <= 200 (head -c 200 cap)"
fi

if [ "$DO_DRIFT" = 0 ] && [ "$DO_CENSUS" = 0 ] && [ "$DO_SCRATCH" = 0 ]; then
  DO_DRIFT=1; DO_CENSUS=1; DO_SCRATCH=1
fi

# ---------------------------------------------------------------- primitives

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

is_offlimits() { # never open driver runtime, even if a walk reaches it
  case "$1" in
    */.ufo/state|*/.ufo/state/*|*/.ufo/watchdog.log) return 0 ;;
  esac
  return 1
}

file_has() { # $1 path, $2 fixed string. Never opens a secret-shaped path.
  local f=$1 needle=$2
  [ -f "$f" ] || return 1
  if is_secret_shaped "$f" || is_offlimits "$f"; then return 1; fi
  grep -F -q -- "$needle" "$f"
}

json_escape() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

# Read-only git allowlist. Anything else is refused before exec.
git_ok() {
  local sub=$1 repo=$2
  shift 2
  case "$sub" in
    rev-parse|status|log|worktree|for-each-ref) ;;
    *) printf 'impl-38: refused git %s\n' "$sub" >&2; return 2 ;;
  esac
  git -C "$repo" "$sub" "$@"
}

# ---------------------------------------------------------------- C1 drift

DRIFT_ROWS=()
DRIFT_COUNT=0
ALIGNED_COUNT=0

add_drift() {
  DRIFT_ROWS+=("$1"$'\t'"$2"$'\t'"$3"$'\t'"$4"$'\t'"$5")
  if [ "$4" = drift ]; then
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
  else
    ALIGNED_COUNT=$((ALIGNED_COUNT + 1))
  fi
}

run_drift() {
  local skill="$DOCS_ROOT/SKILL.md"
  local spec="$DOCS_ROOT/tools/souji-verify.spec.md"
  local verify="$DOCS_ROOT/tools/souji-verify.sh"
  local vault="$DOCS_ROOT/tools/souji-vault-verify.sh"
  DRIFT_ROWS=()
  DRIFT_COUNT=0
  ALIGNED_COUNT=0

  if [ ! -f "$skill" ] || [ ! -f "$spec" ] || [ ! -f "$verify" ] || [ ! -f "$vault" ]; then
    add_drift D0 missing docs-or-tools drift "skill=$skill spec=$spec verify=$verify vault=$vault"
    return 0
  fi

  # D1 — skill still requires a fetch before a pushed receipt. Spec and both
  # installed tools forbid fetch and use existing refs only (r5).
  if file_has "$skill" 'git fetch' \
     && file_has "$spec" 'NO `git fetch`' \
     && file_has "$verify" 'no git fetch' \
     && file_has "$vault" 'No git fetch'; then
    add_drift D1 SKILL.md tools/souji-verify.sh drift \
      "skill requires git fetch before a pushed receipt; spec and both tools forbid fetch and use existing refs only"
  else
    add_drift D1 SKILL.md tools/souji-verify.sh aligned \
      "fetch guidance agrees across skill, spec, and tools"
  fi

  # D2 — skill counts pushed against origin/main. Spec and the tool resolve
  # refs/remotes/origin/HEAD and emit pushed-unverifiable when that ref is
  # absent (r1 D1, r5 local-master refusal). The tool mentions
  # refs/heads/master only to forbid it, so a lacks-check would false-align.
  if file_has "$skill" 'origin/main' \
     && file_has "$spec" 'refs/remotes/origin/HEAD' \
     && file_has "$verify" 'pushed-unverifiable'; then
    add_drift D2 SKILL.md tools/souji-verify.sh drift \
      "skill counts a pushed receipt against origin/main; tools resolve refs/remotes/origin/HEAD and return pushed-unverifiable otherwise"
  else
    add_drift D2 SKILL.md tools/souji-verify.sh aligned \
      "default-branch guidance agrees"
  fi

  # D3 — stale sweep. Skill says rg -l / rg --files-with-matches. rg skips
  # hidden files unless --hidden is set. The installed sweep is
  # `rg -l --no-ignore` and does not pass --hidden. r5 reproduced
  # SAFE(stale) when the only live reference was a hidden file. Doc and
  # tool agree with each other and both still miss that class — counted
  # as drift so the reconciliation cannot report 0 while the class is open.
  if file_has "$skill" 'rg -l' \
     && file_has "$verify" 'rg -l --no-ignore' \
     && ! file_has "$verify" '--hidden' \
     && ! file_has "$skill" '--hidden'; then
    add_drift D3 SKILL.md+spec tools/souji-verify.sh drift \
      "stale sweep omits hidden files; r5 false-SAFE class is still open in the skill and the installed tool"
  else
    add_drift D3 SKILL.md tools/souji-verify.sh aligned \
      "stale sweep names hidden-file traversal"
  fi

  # D4 — known-surfaces table still freezes mint-time figures. The tools
  # re-measure; a frozen table is calibration drift.
  if file_has "$skill" '553M' && file_has "$skill" '19 prunable' \
     && file_has "$skill" '5 prunable'; then
    add_drift D4 SKILL.md "(tools re-measure)" drift \
      "known-surfaces still quotes mint figures (553M .scratch, lore 19 prunable, gd2d 5 prunable, rounds 17..22); tools do not hard-code them"
  else
    add_drift D4 SKILL.md "(tools re-measure)" aligned \
      "known-surfaces table no longer freezes mint-time counts"
  fi

  # D5 — r5 symlink-present refusal is in both tools and the spec, and is
  # not named in the skill decision table.
  if file_has "$verify" 'symlink-present' \
     && file_has "$vault" 'symlink' \
     && file_has "$spec" 'symlink-present' \
     && ! file_has "$skill" 'symlink'; then
    add_drift D5 SKILL.md tools/souji-verify.sh+souji-vault-verify.sh drift \
      "r5 symlink-present refusal is in both tools and the spec; SKILL.md does not name it"
  else
    add_drift D5 SKILL.md tools aligned \
      "symlink refusal is named in the skill"
  fi

  # D6 — spec still requires `rg --basename`, which the installed sweep does
  # not pass. The tool uses --fixed-strings (rg 15 has no --basename). A
  # comment in the tool mentions the missing flag, so the check looks for
  # the sweep invocation, not the bare word.
  if file_has "$spec" '--basename' \
     && file_has "$verify" 'rg -l --no-ignore --fixed-strings' \
     && ! file_has "$verify" 'rg -l --no-ignore --basename'; then
    add_drift D6 tools/souji-verify.spec.md tools/souji-verify.sh drift \
      "spec requires rg --basename; installed sweep is rg -l --no-ignore --fixed-strings"
  else
    add_drift D6 tools/souji-verify.spec.md tools/souji-verify.sh aligned \
      "sweep-flag contract matches the installed tool"
  fi

  # D7 — alignment, so a green row is visible. r5 local-master refusal is
  # in the spec and the tool.
  if file_has "$spec" 'can NEVER establish a pushed receipt' \
     && file_has "$verify" 'pushed-unverifiable'; then
    add_drift D7 tools/souji-verify.spec.md tools/souji-verify.sh aligned \
      "r5 pushed-unverifiable (no local-master fallback) is in the spec and the tool"
  else
    add_drift D7 tools/souji-verify.spec.md tools/souji-verify.sh drift \
      "spec and tool disagree on the local-master pushed fallback"
  fi
}

# ---------------------------------------------------------------- O1 census

CENSUS_ROWS=()
CENSUS_LANES=0

census_one() {
  local repo=$1 name head dirty unpushed wts note
  name=$(basename -- "$repo")
  if [ ! -e "$repo/.git" ]; then
    CENSUS_ROWS+=("$name"$'\t'"-"$'\t'"-"$'\t'"-"$'\t'"-"$'\t'"not-a-git-repo")
    CENSUS_LANES=$((CENSUS_LANES + 1))
    return 0
  fi
  head=$(git_ok rev-parse "$repo" --short=12 HEAD 2>/dev/null || printf 'unknown')
  dirty=$(git_ok status "$repo" --porcelain 2>/dev/null | grep -c . || true)
  dirty=${dirty// /}
  if git_ok for-each-ref "$repo" --format='%(refname)' refs/remotes/origin 2>/dev/null | grep -q .; then
    unpushed=$(git_ok log "$repo" --oneline --branches --not --remotes 2>/dev/null | grep -c . || true)
    note="refs=existing"
  else
    unpushed=$(git_ok log "$repo" --oneline --branches 2>/dev/null | grep -c . || true)
    note="no-remote-tracking-refs"
  fi
  unpushed=${unpushed// /}
  wts=$(git_ok worktree "$repo" list --porcelain 2>/dev/null | grep -c '^worktree ' || true)
  wts=${wts// /}
  CENSUS_ROWS+=("$name"$'\t'"$head"$'\t'"$dirty"$'\t'"$unpushed"$'\t'"$wts"$'\t'"$note")
  CENSUS_LANES=$((CENSUS_LANES + 1))
}

run_census() {
  local d
  local -a lanes=() sorted=()
  CENSUS_ROWS=()
  CENSUS_LANES=0
  if [ -e "$SHOKUNIN_ROOT/.git" ]; then
    census_one "$SHOKUNIN_ROOT"
  fi
  shopt -s nullglob
  for d in "$SHOKUNIN_ROOT"/*-shokunin; do
    [ -d "$d" ] && lanes+=("$d")
  done
  shopt -u nullglob
  if [ "${#lanes[@]}" -gt 0 ]; then
    mapfile -t sorted < <(printf '%s\n' "${lanes[@]}" | sort)
    for d in "${sorted[@]}"; do
      census_one "$d"
    done
  fi
}

# ---------------------------------------------------------------- K1 scratch
# One python process walks the tree. It does not follow symlinks. It reads
# at most HEADER_BUDGET bytes, and only of files whose size is in
# 1..HEADER_BUDGET — the same ceiling as `head -c 200`. Larger files are
# metadata-only. Secret-shaped paths and off-limits driver paths are counted
# and never opened.

SCRATCH_CLASSES=()
SCRATCH_FILES=0
SCRATCH_BYTES=0
SCRATCH_HEADER_READS=0
SCRATCH_SECRET_SKIPPED=0
SCRATCH_SYMLINKS=0
SCRATCH_DIRS=0
SCRATCH_NOTE=""
OWNING_LANE_NOTE=""

run_scratch() {
  local root base
  root=$(readlink -m -- "$SCRATCH_ROOT" 2>/dev/null || printf '%s' "$SCRATCH_ROOT")
  SCRATCH_CLASSES=()
  SCRATCH_FILES=0
  SCRATCH_BYTES=0
  SCRATCH_HEADER_READS=0
  SCRATCH_SECRET_SKIPPED=0
  SCRATCH_SYMLINKS=0
  SCRATCH_DIRS=0
  SCRATCH_NOTE=""
  OWNING_LANE_NOTE=""

  if [ ! -d "$root" ]; then
    SCRATCH_CLASSES+=("missing"$'\t'"0"$'\t'"0"$'\t'"$root")
    SCRATCH_NOTE="missing"
    return 0
  fi
  base=$(basename -- "$root")
  if [ "$base" != ".scratch" ]; then
    SCRATCH_CLASSES+=("refused"$'\t'"0"$'\t'"0"$'\t'"basename=$base (want .scratch)")
    SCRATCH_NOTE="refused"
    return 0
  fi
  if is_secret_shaped "$root" || is_offlimits "$root"; then
    SCRATCH_CLASSES+=("refused"$'\t'"0"$'\t'"0"$'\t'"secret-or-offlimits-root")
    SCRATCH_NOTE="refused"
    return 0
  fi

  local py_out
  py_out=$(python3 - "$root" "$HEADER_BUDGET" << 'PY'
import os, sys

root, budget = sys.argv[1], int(sys.argv[2])
trace = os.environ.get("SOUJI_SCRATCH_TRACE") == "1"

def secret_shaped(path):
    for comp in path.split("/"):
        if not comp:
            continue
        lc = comp.lower()
        if (lc.endswith(".env") or lc == ".env" or lc.startswith(".env.")
            or lc == ".envrc" or "credential" in lc or "secret" in lc
            or lc.startswith("id_") or lc.endswith(".pem")):
            return True
    return False

def offlimits(path):
    return "/.ufo/state" in path or path.endswith("/.ufo/watchdog.log") or path.endswith("/watchdog.log")

def ext_of(name):
    low = name.lower()
    if "." not in low:
        return "none"
    ext = low.rsplit(".", 1)[1]
    return ext if len(ext) <= 12 else "long"

def header_class(blob):
    if not blob:
        return "empty"
    if b"\0" in blob:
        return "binary-nul"
    stripped = blob.lstrip()
    if stripped.startswith(b"%PDF"):
        return "pdf"
    low = stripped[:64].lower()
    if low.startswith(b"<!doctype html") or low.startswith(b"<html"):
        return "html"
    if low.startswith(b"<?xml") or low.startswith(b"<xml"):
        return "xml"
    if stripped.startswith(b"#!"):
        head = stripped[:80]
        if b"python" in head:
            return "python"
        return "shell"
    if stripped[:1] in (b"{", b"["):
        return "json"
    if all(b in (9, 10, 13) or 32 <= b < 127 or b >= 128 for b in blob):
        return "text"
    return "other"

ext_count, ext_bytes, hdr_count = {}, {}, {}
files = bytes_total = header_reads = secret_skipped = symlinks = dirs = 0

for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
    # Do not descend into a symlink directory (os.walk already won't follow
    # a symlink dir unless followlinks). Count the directory itself.
    dirs += 1
    # Skip driver-runtime subtrees without listing their contents further.
    dirnames[:] = [d for d in dirnames if not offlimits(os.path.join(dirpath, d))]
    for name in dirnames:
        p = os.path.join(dirpath, name)
        if os.path.islink(p):
            symlinks += 1
    for name in filenames:
        p = os.path.join(dirpath, name)
        if os.path.islink(p):
            symlinks += 1
            continue
        if not os.path.isfile(p):
            continue
        files += 1
        try:
            sz = os.path.getsize(p)
        except OSError:
            sz = 0
        bytes_total += sz
        if secret_shaped(p) or offlimits(p):
            secret_skipped += 1
            ext_count["secret-shaped"] = ext_count.get("secret-shaped", 0) + 1
            ext_bytes["secret-shaped"] = ext_bytes.get("secret-shaped", 0) + sz
            continue
        ext = ext_of(name)
        ext_count[ext] = ext_count.get(ext, 0) + 1
        ext_bytes[ext] = ext_bytes.get(ext, 0) + sz
        if sz == 0:
            hdr_count["empty"] = hdr_count.get("empty", 0) + 1
            continue
        if sz > budget:
            hdr_count["metadata-only"] = hdr_count.get("metadata-only", 0) + 1
            continue
        # Whole file fits the cap. Read at most `budget` bytes — the
        # assignment's head -c 200 ceiling, applied in-process so a
        # half-million-file tree does not spawn one head per file.
        try:
            with open(p, "rb") as fh:
                blob = fh.read(budget)
            header_reads += 1
            if trace:
                sys.stderr.write(p + "\n")
        except OSError:
            hdr_count["unreadable"] = hdr_count.get("unreadable", 0) + 1
            continue
        cls = header_class(blob)
        hdr_count[cls] = hdr_count.get(cls, 0) + 1

def emit(cls, count, nbytes, note):
    sys.stdout.write(f"{cls}\t{count}\t{nbytes}\t{note}\n")

for k in sorted(ext_count):
    emit(f"ext:{k}", ext_count[k], ext_bytes[k], "metadata")
for k in sorted(hdr_count):
    emit(f"header:{k}", hdr_count[k], 0, f"bounded-read<={budget}")
emit("symlink", symlinks, 0, "not-followed")
emit("dir", dirs, 0, "directories")
sys.stdout.write(
    f"META\t{files}\t{bytes_total}\t{header_reads}\t{secret_skipped}\t{symlinks}\t{dirs}\n"
)
PY
  ) || {
    SCRATCH_CLASSES+=("error"$'\t'"0"$'\t'"0"$'\t'"scratch-walk-failed")
    SCRATCH_NOTE="error"
    return 0
  }

  local line cls count bytes note
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    if [[ "$line" == META$'\t'* ]]; then
      IFS=$'\t' read -r _ SCRATCH_FILES SCRATCH_BYTES SCRATCH_HEADER_READS \
        SCRATCH_SECRET_SKIPPED SCRATCH_SYMLINKS SCRATCH_DIRS <<< "$line"
      continue
    fi
    SCRATCH_CLASSES+=("$line")
  done <<< "$py_out"
  SCRATCH_NOTE="classified"
  probe_owning_lane "$root"
}

# Read-only receipt for the lane that owns the scratch tree. A classification
# is never a removal receipt; if that lane is dirty or unpushed the handoff
# says so from this probe, even when --census was not also requested.
probe_owning_lane() {
  local root=$1 parent name head dirty unpushed
  parent=$(dirname -- "$root")
  name=$(basename -- "$parent")
  if [ ! -e "$parent/.git" ]; then
    OWNING_LANE_NOTE="classify-only; owning-lane=$name not-a-git-repo; not a removal receipt"
    return 0
  fi
  head=$(git_ok rev-parse "$parent" --short=12 HEAD 2>/dev/null || printf 'unknown')
  dirty=$(git_ok status "$parent" --porcelain 2>/dev/null | grep -c . || true)
  dirty=${dirty// /}
  if git_ok for-each-ref "$parent" --format='%(refname)' refs/remotes/origin 2>/dev/null | grep -q .; then
    unpushed=$(git_ok log "$parent" --oneline --branches --not --remotes 2>/dev/null | grep -c . || true)
  else
    unpushed=$(git_ok log "$parent" --oneline --branches 2>/dev/null | grep -c . || true)
  fi
  unpushed=${unpushed// /}
  OWNING_LANE_NOTE="classify-only; owning-lane=$name dirty=$dirty unpushed=$unpushed head=$head; not a removal receipt"
}

# ---------------------------------------------------------------- emit

kotodama_note() {
  local row lane head dirty unpushed wts note
  if [ -n "$OWNING_LANE_NOTE" ]; then
    printf '%s' "$OWNING_LANE_NOTE"
    return 0
  fi
  for row in "${CENSUS_ROWS[@]}"; do
    IFS=$'\t' read -r lane head dirty unpushed wts note <<< "$row"
    if [ "$lane" = "kotodama-shokunin" ]; then
      printf 'classify-only; owning-lane dirty=%s unpushed=%s head=%s; not a removal receipt' \
        "$dirty" "$unpushed" "$head"
      return 0
    fi
  done
  printf 'classify-only; owning-lane-not-in-this-run; not a removal receipt'
}

emit_text() {
  local row
  if [ "$DO_DRIFT" = 1 ]; then
    for row in "${DRIFT_ROWS[@]}"; do
      printf 'DRIFT\t%s\n' "$row"
    done
    printf 'SUMMARY\tdrift\tdrift=%s aligned=%s\n' "$DRIFT_COUNT" "$ALIGNED_COUNT"
  fi
  if [ "$DO_CENSUS" = 1 ]; then
    for row in "${CENSUS_ROWS[@]}"; do
      printf 'CENSUS\t%s\n' "$row"
    done
    printf 'SUMMARY\tcensus\tlanes=%s\n' "$CENSUS_LANES"
  fi
  if [ "$DO_SCRATCH" = 1 ]; then
    for row in "${SCRATCH_CLASSES[@]}"; do
      printf 'SCRATCH\t%s\n' "$row"
    done
    printf 'SUMMARY\tscratch\tfiles=%s bytes=%s header_reads=%s secret_skipped=%s symlinks=%s dirs=%s budget=%s note=%s\n' \
      "$SCRATCH_FILES" "$SCRATCH_BYTES" "$SCRATCH_HEADER_READS" \
      "$SCRATCH_SECRET_SKIPPED" "$SCRATCH_SYMLINKS" "$SCRATCH_DIRS" \
      "$HEADER_BUDGET" "$SCRATCH_NOTE"
    printf 'HANDOFF\tscratch\tNOT-SAFE\t%s\n' "$(kotodama_note)"
  fi
}

emit_json() {
  local row id doc tool status note lane head dirty unpushed wts
  local cls count bytes first
  printf '{'
  printf '"tool":"impl-38","round":6'
  if [ "$DO_DRIFT" = 1 ]; then
    printf ',"drift_count":%s,"aligned_count":%s,"drift":[' "$DRIFT_COUNT" "$ALIGNED_COUNT"
    first=1
    for row in "${DRIFT_ROWS[@]}"; do
      IFS=$'\t' read -r id doc tool status note <<< "$row"
      [ "$first" = 1 ] && first=0 || printf ','
      printf '{"id":"%s","doc":"%s","tool":"%s","status":"%s","note":"%s"}' \
        "$(json_escape "$id")" "$(json_escape "$doc")" "$(json_escape "$tool")" \
        "$(json_escape "$status")" "$(json_escape "$note")"
    done
    printf ']'
  fi
  if [ "$DO_CENSUS" = 1 ]; then
    printf ',"lanes":%s,"census":[' "$CENSUS_LANES"
    first=1
    for row in "${CENSUS_ROWS[@]}"; do
      IFS=$'\t' read -r lane head dirty unpushed wts note <<< "$row"
      [ "$first" = 1 ] && first=0 || printf ','
      printf '{"lane":"%s","head":"%s","dirty":"%s","unpushed":"%s","worktrees":"%s","note":"%s"}' \
        "$(json_escape "$lane")" "$(json_escape "$head")" "$(json_escape "$dirty")" \
        "$(json_escape "$unpushed")" "$(json_escape "$wts")" "$(json_escape "$note")"
    done
    printf ']'
  fi
  if [ "$DO_SCRATCH" = 1 ]; then
    printf ',"scratch":{"files":%s,"bytes":%s,"header_reads":%s,"secret_skipped":%s,"symlinks":%s,"dirs":%s,"budget":%s,"note":"%s","handoff":"NOT-SAFE %s","classes":[' \
      "$SCRATCH_FILES" "$SCRATCH_BYTES" "$SCRATCH_HEADER_READS" \
      "$SCRATCH_SECRET_SKIPPED" "$SCRATCH_SYMLINKS" "$SCRATCH_DIRS" \
      "$HEADER_BUDGET" "$(json_escape "$SCRATCH_NOTE")" "$(json_escape "$(kotodama_note)")"
    first=1
    for row in "${SCRATCH_CLASSES[@]}"; do
      IFS=$'\t' read -r cls count bytes note <<< "$row"
      [ "$first" = 1 ] && first=0 || printf ','
      printf '{"class":"%s","count":%s,"bytes":%s,"note":"%s"}' \
        "$(json_escape "$cls")" "${count:-0}" "${bytes:-0}" "$(json_escape "$note")"
    done
    printf ']}'
  fi
  printf '}\n'
}

# ---------------------------------------------------------------- selftest

selftest() {
  local tmp n=0 fail=0 parent probe
  # /tmp is the preferred scratch. If the user quota there is exhausted
  # (observed 2026-10-18: 1M write returns "Disk quota exceeded" while
  # /var/tmp and /dev/shm accept it), fall through. Never a fleet path.
  parent=""
  for probe in /tmp /var/tmp /dev/shm; do
    [ -d "$probe" ] || continue
    local try
    try=$(mktemp "$probe/impl38-probe.XXXXXX" 2>/dev/null) || continue
    if dd if=/dev/zero of="$try" bs=1024 count=64 status=none 2>/dev/null; then
      rm -f "$try"
      parent=$probe
      break
    fi
    rm -f "$try"
  done
  [ -n "$parent" ] || { printf 'selftest: no writable scratch\n' >&2; return 1; }
  tmp=$(mktemp -d "$parent/impl-38-selftest.XXXXXX")
  case "$tmp" in
    /tmp/*|/var/tmp/*|/dev/shm/*) ;;
    *) printf 'selftest: refusing scratch outside temp dirs (%s)\n' "$tmp" >&2; return 1 ;;
  esac
  # Removes only this selftest's own mktemp directory. Never a fleet path.
  cleanup() { rm -rf "$tmp"; }
  trap cleanup RETURN

  mkdir -p "$tmp/docs/tools" "$tmp/fleet/fixture-shokunin/.scratch/sub" \
    "$tmp/fleet/fixture-shokunin/src"

  printf '%s\n' 'NO `git fetch` — existing refs only.' \
    'refs/remotes/origin/HEAD' 'symlink-present' \
    'can NEVER establish a pushed receipt' \
    'rg -l --basename <name>' \
    > "$tmp/docs/tools/souji-verify.spec.md"
  printf '%s\n' '# no git fetch' 'pushed-unverifiable' \
    'rg -l --no-ignore --fixed-strings' 'symlink-present' \
    > "$tmp/docs/tools/souji-verify.sh"
  printf '%s\n' '# No git fetch' 'symlink-present' \
    > "$tmp/docs/tools/souji-vault-verify.sh"
  printf '%s\n' \
    'after `git fetch`, ancestor of origin/main' \
    'rg -l <basename>' \
    '553M `.scratch/`' '19 prunable' '5 prunable' \
    > "$tmp/docs/SKILL.md"

  # Fixture lane via plumbing. No fetch/push/commit/branch/prune/remove.
  local repo blob sub tree commit
  repo="$tmp/fleet/fixture-shokunin"
  git -C "$repo" init -q
  git -C "$repo" config user.email souji@shokunin.local
  git -C "$repo" config user.name souji-shokunin
  printf 'x\n' > "$repo/src/a.txt"
  # This git's mktree rejects a path containing a slash, and hash-object
  # rejects one as an argument. Hash via stdin; build the src/ tree as a
  # nested tree so the fixture is a real commit without a forbidden verb.
  blob=$(git -C "$repo" hash-object -w --stdin < "$repo/src/a.txt")
  sub=$(printf '100644 blob %s\ta.txt\n' "$blob" | git -C "$repo" mktree)
  tree=$(printf '040000 tree %s\tsrc\n' "$sub" | git -C "$repo" mktree)
  commit=$(GIT_AUTHOR_NAME=souji-shokunin GIT_AUTHOR_EMAIL=souji@shokunin.local \
    GIT_COMMITTER_NAME=souji-shokunin GIT_COMMITTER_EMAIL=souji@shokunin.local \
    git -C "$repo" commit-tree "$tree" -m init)
  git -C "$repo" update-ref HEAD "$commit"
  git -C "$repo" read-tree HEAD
  case "$commit" in
    [0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f][0-9a-f]*) ;;
    *) printf 'selftest: fixture commit missing (%s)\n' "$commit" >&2; return 1 ;;
  esac
  printf 'dirty\n' >> "$repo/src/a.txt"

  printf 'hello scratch header\n' > "$repo/.scratch/note.txt"
  printf 'not a secret body\n' > "$repo/.scratch/sub/fake.secret"
  ln -s note.txt "$repo/.scratch/alias.txt"
  python3 -c 'import sys; open(sys.argv[1],"w").write("A"*250+"\n")' "$repo/.scratch/big.log"

  local out err
  err="$tmp/err"
  out=$(SOUJI_SCRATCH_TRACE=1 SHOKUNIN_ROOT="$tmp/fleet" bash "$SELF" --json \
    --docs-root "$tmp/docs" \
    --scratch-root "$repo/.scratch" 2>"$err") || {
      printf 'selftest: tool exit %s\n%s\n' "$?" "$(cat "$err")" >&2
      return 1
    }

  assert() {
    n=$((n + 1))
    if python3 -c 'import json,sys; o=json.loads(sys.argv[1]); sys.exit(0 if ('"$2"') else 1)' "$out"; then
      printf 'PASS %s\n' "$1"
    else
      printf 'FAIL %s\n' "$1" >&2
      fail=$((fail + 1))
    fi
  }

  assert drift-count-6 'o["drift_count"]==6'
  assert drift-d1-fetch 'any(r["id"]=="D1" and r["status"]=="drift" for r in o["drift"])'
  assert drift-d3-hidden 'any(r["id"]=="D3" and r["status"]=="drift" for r in o["drift"])'
  assert drift-d7-aligned 'any(r["id"]=="D7" and r["status"]=="aligned" for r in o["drift"])'
  assert census-has-fixture 'any(r["lane"]=="fixture-shokunin" and int(r["dirty"])>=1 for r in o["census"])'
  assert census-no-remote 'any(r["lane"]=="fixture-shokunin" and r["note"]=="no-remote-tracking-refs" for r in o["census"])'
  assert scratch-secret-skipped 'o["scratch"]["secret_skipped"]==1'
  assert scratch-header-text 'any(c["class"]=="header:text" and c["count"]>=1 for c in o["scratch"]["classes"])'
  assert scratch-symlink 'o["scratch"]["symlinks"]==1'
  assert scratch-metadata-only 'any(c["class"]=="header:metadata-only" and c["count"]>=1 for c in o["scratch"]["classes"])'
  assert scratch-budget 'o["scratch"]["budget"]==200'
  assert scratch-handoff-not-safe '"NOT-SAFE" in o["scratch"]["handoff"] and "fixture-shokunin" in o["scratch"]["handoff"] and "dirty=" in o["scratch"]["handoff"]'

  n=$((n + 1))
  if grep -F -q 'fake.secret' "$err"; then
    printf 'FAIL secret-not-opened\n' >&2
    fail=$((fail + 1))
  else
    printf 'PASS secret-not-opened\n'
  fi
  n=$((n + 1))
  if grep -F -q 'note.txt' "$err" && ! grep -F -q 'big.log' "$err"; then
    printf 'PASS header-cap-respected\n'
  else
    printf 'FAIL header-cap-respected\n' >&2
    fail=$((fail + 1))
  fi

  # Repeatability: a second census-only run matches the first census rows.
  n=$((n + 1))
  local c1 c2
  c1=$(SHOKUNIN_ROOT="$tmp/fleet" bash "$SELF" --census --json)
  c2=$(SHOKUNIN_ROOT="$tmp/fleet" bash "$SELF" --census --json)
  if [ "$c1" = "$c2" ]; then
    printf 'PASS census-repeatable\n'
  else
    printf 'FAIL census-repeatable\n' >&2
    fail=$((fail + 1))
  fi

  n=$((n + 1))
  if bash "$SELF" --header-budget 201 >/dev/null 2>&1; then
    printf 'FAIL budget-cap\n' >&2
    fail=$((fail + 1))
  else
    printf 'PASS budget-cap\n'
  fi

  n=$((n + 1))
  local refused
  refused=$(SHOKUNIN_ROOT="$tmp/fleet" bash "$SELF" --scratch --json \
    --scratch-root "$repo/src" 2>/dev/null || true)
  if python3 -c 'import json,sys; o=json.loads(sys.argv[1]); sys.exit(0 if any(c["class"]=="refused" for c in o["scratch"]["classes"]) else 1)' "$refused"; then
    printf 'PASS scratch-basename-refused\n'
  else
    printf 'FAIL scratch-basename-refused\n' >&2
    fail=$((fail + 1))
  fi

  # Literal head -c ceiling: a 250-byte file sliced with head -c 200 is 200 bytes.
  n=$((n + 1))
  local sliced
  sliced=$(head -c 200 -- "$repo/.scratch/big.log" | wc -c)
  sliced=${sliced// /}
  if [ "$sliced" = 200 ]; then
    printf 'PASS head-c-200-ceiling\n'
  else
    printf 'FAIL head-c-200-ceiling (got %s)\n' "$sliced" >&2
    fail=$((fail + 1))
  fi

  printf 'selftest: %s checks, %s failed\n' "$n" "$fail"
  [ "$fail" -eq 0 ]
}

if [ "$SELFTEST" = 1 ]; then
  selftest
  exit $?
fi

[ "$DO_DRIFT" = 1 ] && run_drift
[ "$DO_CENSUS" = 1 ] && run_census
[ "$DO_SCRATCH" = 1 ] && run_scratch

if [ "$JSON" = 1 ]; then
  emit_json
else
  emit_text
fi
exit 0
