#!/usr/bin/env bash
# souji-verify.sh independent test runner — seat S23 (souji-shokunin round 2).
#
# Subject: tools/souji-verify.sh (spec: tools/souji-verify.spec.md).
# Phases:
#   static   - syntax + safety-rail source audit of the subject (read-only)
#   selftest - the subject's own --selftest (exit code, cwd-independence)
#   fixture  - independently built mktemp fixtures: spec cases F1-F10 + E1/E2
#   cli      - CLI contract: usage=exit 2, evaluation=exit 0, --json, multi-target
#   live     - read-only fleet gates: kotodama unpushed/dirty, fleet root,
#              lore/gd2d worktree registrations, live pushed files, secrets-shaped
#
# Read-only over every real surface. All git mutations are confined to mktemp
# dirs; no network (fixture remotes are local paths). Writes only
# tests/results/runner-23.json. Exit 0 all pass, 1 any failure or blocked.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FLEET_ROOT="$(cd "$REPO_ROOT/.." && pwd)"
TOOL="$REPO_ROOT/tools/souji-verify.sh"
RESULTS_DIR="$REPO_ROOT/tests/results"
RESULTS_JSON="$RESULTS_DIR/runner-23.json"
MARKER='SOUJI-RUNNER-23-DO-NOT-READ-MARKER'

while [ $# -gt 0 ]; do
  case "$1" in
    --tool) TOOL="$2"; shift 2 ;;
    --out) RESULTS_JSON="$2"; shift 2 ;;
    -h|--help) echo "usage: tests/runner-23.sh [--tool PATH] [--out JSON]" >&2; exit 2 ;;
    *) echo "usage: tests/runner-23.sh [--tool PATH] [--out JSON]" >&2; exit 2 ;;
  esac
done
RESULTS_DIR="$(dirname "$RESULTS_JSON")"
TOOL_REL="${TOOL#"$REPO_ROOT"/}"

STARTED_AT="$(date -u +%FT%TZ)"
SECONDS=0
TMP="$(mktemp -d "${TMPDIR:-/tmp}/souji-runner-23.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# Hermetic git for every mutation and every fixture-side invocation.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME="souji-runner-23" GIT_AUTHOR_EMAIL="runner-23@shokunin.local"
export GIT_COMMITTER_NAME="souji-runner-23" GIT_COMMITTER_EMAIL="runner-23@shokunin.local"
export GIT_AUTHOR_DATE="2026-10-01T00:00:00+00:00" GIT_COMMITTER_DATE="2026-10-01T00:00:00+00:00"

mkdir -p "$RESULTS_DIR"
CASES_TSV="$TMP/cases.tsv"
: > "$CASES_TSV"
OUT="$TMP/out"
ERR="$TMP/err"
PHASE="preflight"

san() { printf '%s' "${1:-}" | tr '\t\n' '  ' | cut -c1-600; }
hide_tmp() { printf '%s' "${1//$TMP/\$TMP}"; }

add_case() { # name phase spec cmd rc expected actual result note
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san "$1")" "$(san "$2")" "$(san "$3")" "$(san "$4")" "$(san "$5")" \
    "$(san "$6")" "$(san "$7")" "$(san "$8")" "$(san "$9")" >> "$CASES_TSV"
}

TOOL_RC=0
TOOL_CMD=""
LAST_LINE=""
LAST_F3="?"
LAST_F4="?"
LAST_F5=""
TAG_SEEN=no

run_tool() { # run_tool <timeout_s> [args...]
  local t="$1"; shift
  TOOL_RC=0
  TOOL_CMD="$(hide_tmp "bash $TOOL_REL $*")"
  ( cd "$REPO_ROOT" && timeout -k 5 "$t" bash "$TOOL" "$@" >"$OUT" 2>"$ERR" ) || TOOL_RC=$?
}

run_tool_in() { # run_tool_in <cwd> <timeout_s> [args...]
  local d="$1" t="$2"; shift 2
  TOOL_RC=0
  TOOL_CMD="$(hide_tmp "(cd $d) bash $TOOL_REL $*")"
  ( cd "$d" && timeout -k 5 "$t" bash "$TOOL" "$@" >"$OUT" 2>"$ERR" ) || TOOL_RC=$?
}

run_tool_root() { # run_tool_root <SHOKUNIN_ROOT> <timeout_s> [args...]
  local root="$1" t="$2"; shift 2
  TOOL_RC=0
  TOOL_CMD="$(hide_tmp "SHOKUNIN_ROOT=$root bash $TOOL_REL $*")"
  ( cd "$REPO_ROOT" && SHOKUNIN_ROOT="$root" timeout -k 5 "$t" bash "$TOOL" "$@" >"$OUT" 2>"$ERR" ) || TOOL_RC=$?
}

parse_out() {
  local f="$1"
  TAG_SEEN=no
  LAST_LINE="$(grep -a $'^VERDICT\t' "$f" | tail -n 1 || true)"
  if [ -n "$LAST_LINE" ]; then TAG_SEEN=yes; else
    LAST_LINE="$(grep -av '^[[:space:]]*$' "$f" | tail -n 1 || true)"
  fi
  LAST_F3="?"; LAST_F4="?"; LAST_F5=""
  if [ -n "$LAST_LINE" ]; then
    IFS=$'\t' read -r _f1 _f2 LAST_F3 LAST_F4 LAST_F5 <<< "$LAST_LINE" || true
  fi
}

marker_leak() { # prints MARKER-LEAK if the fixture marker text appears in out/err
  if grep -aqF "$MARKER" "$OUT" "$ERR" 2>/dev/null; then echo "MARKER-LEAK"; else echo "no-leak"; fi
}

refs_diag() { # refs_diag <repo> <literal-name> -> "plain=N excluded=M"
  local repo="$1" name="$2" plain excl
  plain="$( { rg -l --no-ignore -F "$name" "$repo" 2>/dev/null || true; } | wc -l | tr -d ' ')"
  excl="$( { rg -l --no-ignore -F "$name" "$repo" -g '!.git' -g '!souji-shokunin/census/**' -g '!**/.ufo-quarantine/**' 2>/dev/null || true; } | wc -l | tr -d ' ')"
  printf 'plain=%s d3excluded=%s' "$plain" "$excl"
}

judge() { # judge <name> <spec> <exp_rc> <exp_verdict> <receipt_ere> <note> [evidence_ere]
  local c="$1" s="$2" erc="$3" ev="$4" er="$5" n="$6" ee="${7:-}"
  local av="${LAST_F3:-?}" ar="${LAST_F4:-?}"
  local res=fail
  if [ "$TOOL_RC" = "$erc" ] && [ "$av" = "$ev" ] && [[ "$ar" =~ ^($er)$ ]] \
     && { [ -z "$ee" ] || [[ "$LAST_F5" =~ $ee ]]; }; then res=pass; fi
  add_case "$c" "$PHASE" "$s" "$TOOL_CMD" "$TOOL_RC" \
    "rc=$erc verdict=$ev receipt~($er)" \
    "rc=$TOOL_RC verdict=$av receipt=$ar" "$res" "$n | evidence: ${LAST_F5:0:200}"
}

judge_rc() { # judge_rc <name> <spec> <exp_rc> <note>
  local c="$1" s="$2" erc="$3" n="$4"
  local res=fail
  if [ "$TOOL_RC" = "$erc" ]; then res=pass; fi
  add_case "$c" "$PHASE" "$s" "$TOOL_CMD" "$TOOL_RC" "rc=$erc" "rc=$TOOL_RC" "$res" \
    "$n | out: $(head -c 160 "$OUT" 2>/dev/null) | err: $(head -c 160 "$ERR" 2>/dev/null)"
}

rec_case() { # rec_case <name> <spec> <note>
  add_case "$1" "$PHASE" "$2" "$TOOL_CMD" "$TOOL_RC" "record-only" \
    "rc=$TOOL_RC verdict=${LAST_F3:-?} receipt=${LAST_F4:-?}" record "$3"
}

fail_early() { # fail_early <note>  — write blocked JSON, exit 1
  FINISHED_AT="$(date -u +%FT%TZ)"
  STATUS=blocked-tool-absent
  write_json "$1"
  echo "runner-23: BLOCKED — $1" >&2
  exit 1
}

write_json() {
  : > "$TMP/notes.txt"
  printf '%s\n' "$@" > "$TMP/notes.txt"
  CASES_TSV="$CASES_TSV" RESULTS_JSON="$RESULTS_JSON" TMP="$TMP" \
  SEAT=S23 STATUS="${STATUS:-unknown}" STARTED_AT="$STARTED_AT" FINISHED_AT="${FINISHED_AT:-$(date -u +%FT%TZ)}" \
  DURATION_S="$SECONDS" REPO_ROOT="$REPO_ROOT" FLEET_ROOT="$FLEET_ROOT" \
  TOOL_PATH="$TOOL" TOOL_REL="$TOOL_REL" TOOL_PRESENT="${TOOL_PRESENT:-0}" \
  TOOL_SHA_BEFORE="${TOOL_SHA_BEFORE:-}" TOOL_SHA_AFTER="${TOOL_SHA_AFTER:-}" TOOL_BYTES="${TOOL_BYTES:-}" \
  HARNESS_SHA="${HARNESS_SHA:-}" SAFETY_JSON="${SAFETY_JSON:-{\}}" NOTES_FILE="$TMP/notes.txt" \
  python3 - <<'PY'
import csv, json, os

cases = []
with open(os.environ["CASES_TSV"], newline="") as f:
    for row in csv.reader(f, delimiter="\t"):
        if len(row) < 9:
            continue
        cases.append({
            "case": row[0], "phase": row[1], "spec": row[2], "cmd": row[3],
            "exit": row[4], "expected": row[5], "actual": row[6],
            "result": row[7], "note": row[8],
        })

passed = sum(1 for c in cases if c["result"] == "pass")
failed = sum(1 for c in cases if c["result"] == "fail")
recorded = sum(1 for c in cases if c["result"] == "record")

notes = []
try:
    with open(os.environ["NOTES_FILE"]) as f:
        notes = [l.rstrip("\n") for l in f if l.strip()]
except OSError:
    pass

tool = {
    "path": os.environ["TOOL_REL"],
    "abs_path": os.environ["TOOL_PATH"],
    "present": os.environ["TOOL_PRESENT"] == "1",
    "sha256_before": os.environ["TOOL_SHA_BEFORE"],
    "sha256_after": os.environ["TOOL_SHA_AFTER"],
    "bytes": os.environ["TOOL_BYTES"],
    "stable_during_run": os.environ["TOOL_SHA_BEFORE"] == os.environ["TOOL_SHA_AFTER"],
}

try:
    safety = json.loads(os.environ["SAFETY_JSON"])
except ValueError:
    safety = {}

doc = {
    "seat": os.environ["SEAT"],
    "runner": "tests/runner-23.sh",
    "kind": "test-runner",
    "round": 2,
    "date": "2026-10-18",
    "status": os.environ["STATUS"],
    "started_at": os.environ["STARTED_AT"],
    "finished_at": os.environ["FINISHED_AT"],
    "duration_s": int(os.environ["DURATION_S"]),
    "repo_root": os.environ["REPO_ROOT"],
    "fleet_root": os.environ["FLEET_ROOT"],
    "harness_sha256": os.environ["HARNESS_SHA"],
    "tool": tool,
    "summary": {
        "cases_total": len(cases), "passed": passed, "failed": failed, "recorded": recorded,
    },
    "failures": [{"case": c["case"], "expected": c["expected"], "actual": c["actual"], "note": c["note"]}
                 for c in cases if c["result"] == "fail"],
    "safety_observations": safety,
    "notes": notes,
    "cases": cases,
}

with open(os.environ["RESULTS_JSON"], "w") as f:
    json.dump(doc, f, indent=2)
    f.write("\n")

print(f"runner-23 status={doc['status']} cases={len(cases)} pass={passed} fail={failed} record={recorded}")
PY
}

# ---------------------------------------------------------------- preflight
if [ ! -f "$TOOL" ]; then
  HARNESS_SHA="$(sha256sum "$0" | cut -d' ' -f1)"
  fail_early "subject missing: $TOOL (harness is ready to re-run when it lands)"
fi

HARNESS_SHA="$(sha256sum "$0" | cut -d' ' -f1)"
TOOL_PRESENT=1
TOOL_SHA_BEFORE="$(sha256sum "$TOOL" | cut -d' ' -f1)"
TOOL_BYTES="$(stat -c %s "$TOOL")"

# ------------------------------------------------------------------ static
PHASE=static
SRC_RC=0
bash -n "$TOOL" || SRC_RC=$?
add_case "S-syntax" "$PHASE" "spec: one bash tool" "bash -n $TOOL_REL" "$SRC_RC" "rc=0" "rc=$SRC_RC" \
  "$([ "$SRC_RC" = 0 ] && echo pass || echo fail)" "bash syntax check"

SHEBANG="$(head -n 1 "$TOOL")"
if [[ "$SHEBANG" == *bash* ]]; then
  add_case "S-shebang" "$PHASE" "spec: bash tool" "head -n1 $TOOL_REL" 0 "bash shebang" "$SHEBANG" pass ""
else
  add_case "S-shebang" "$PHASE" "spec: bash tool" "head -n1 $TOOL_REL" 0 "bash shebang" "$SHEBANG" fail "shebang is not bash"
fi

S_STRICT="$(grep -c 'set -euo pipefail' "$TOOL" || true)"
add_case "S-strict-mode" "$PHASE" "spec: shell discipline" "grep -c 'set -euo pipefail' $TOOL_REL" 0 ">=1" "$S_STRICT" \
  "$([ "${S_STRICT:-0}" -ge 1 ] && echo pass || echo fail)" "set -euo pipefail present"

for v in fetch push commit checkout reset rebase branch; do
  n="$(grep -cE "(^|[^-[:alnum:]_])git([[:space:]]+-[^[:space:]]+)*[[:space:]]+$v([[:space:]]|$)" "$TOOL" || true)"
  add_case "S-verb-$v" "$PHASE" "spec rail: never run git $v on live surfaces" "grep -cE 'git ... $v' $TOOL_REL" 0 \
    "count recorded" "count=$n" record \
    "informational: verb occurrences in subject source (selftest fixtures legitimately commit/push inside mktemp)"
done
IPN="$(grep -c 'symbolic-ref' "$TOOL" || true)"
add_case "S-D1-symbolic-ref" "$PHASE" "spec D1: default branch resolution" "grep -c symbolic-ref $TOOL_REL" 0 ">=1" "count=$IPN" \
  "$([ "${IPN:-0}" -ge 1 ] && echo pass || echo fail)" "origin/HEAD resolution present"
CEN="$(grep -c 'census' "$TOOL" || true)"
add_case "S-D3-census-exclude" "$PHASE" "spec D3: sweep excludes census dirs" "grep -c census $TOOL_REL" 0 ">=1" "count=$CEN" \
  "$([ "${CEN:-0}" -ge 1 ] && echo pass || echo fail)" "census exclusion present in source"

# ------------------------------------------------------------------ selftest
PHASE=selftest
run_tool 600 --selftest
judge_rc "ST1-exit0" "spec: --selftest exit 0 on all pass" 0 "subject --selftest (cwd=repo)"
run_tool_in "$TMP" 600 --selftest
judge_rc "ST2-cwd-independent" "spec: --selftest isolated under mktemp" 0 "subject --selftest (cwd=foreign tmp dir)"

# ------------------------------------------------------------------ fixtures
PHASE=fixture
FX="$TMP/fx"
mkdir -p "$FX"

# A: clone with origin/HEAD -> F1, F2, F7, F8, F10, C5
git init -q --bare -b master "$FX/origin.git"
git clone -q "$FX/origin.git" "$FX/work"
printf 'baseline\n' > "$FX/work/baseline.txt"
git -C "$FX/work" add baseline.txt
git -C "$FX/work" commit -q -m "add baseline"
git -C "$FX/work" push -q -u origin master
printf 'local only\n' > "$FX/work/local-only.txt"
git -C "$FX/work" add local-only.txt
git -C "$FX/work" commit -q -m "local only"
mkdir -p "$FX/work/.scratch" "$FX/work/souji-shokunin/census/round-1"
printf 'aged\n' > "$FX/work/.scratch/aged10.log"
printf 'polluted\n' > "$FX/work/.scratch/f8-polluted.log"
printf 'ref: f8-polluted.log\n' > "$FX/work/souji-shokunin/census/round-1/fixture-notes.json"
printf 'fresh\n' > "$FX/work/.scratch/fresh.log"
touch -d '10 days ago' "$FX/work/.scratch/aged10.log" "$FX/work/.scratch/f8-polluted.log"
printf '%s\n' "$MARKER" > "$FX/work/test.env"
printf '%s\n' "$MARKER" > "$FX/work/fixture-credential-note.txt"
printf '%s\n' "$MARKER" > "$FX/work/fixture-secret-note.txt"
printf '%s\n' "$MARKER" > "$FX/work/fixture-key.pem"

# B: repo-root unpushed=1 dirty=1 -> F3
git init -q --bare -b main "$FX/origin3.git"
git init -q -b main "$FX/work3"
git -C "$FX/work3" remote add origin "$FX/origin3.git"
printf 'a\n' > "$FX/work3/a.txt"
git -C "$FX/work3" add a.txt
git -C "$FX/work3" commit -q -m base
git -C "$FX/work3" push -q -u origin main
printf 'change\n' >> "$FX/work3/a.txt"
printf 'b\n' > "$FX/work3/b.txt"
git -C "$FX/work3" add b.txt
git -C "$FX/work3" commit -q -m unpushed

# C: clean fully pushed repo-root -> E1
git init -q --bare -b main "$FX/origin4.git"
git clone -q "$FX/origin4.git" "$FX/work4"
printf 'x\n' > "$FX/work4/x.txt"
git -C "$FX/work4" add x.txt
git -C "$FX/work4" commit -q -m x
git -C "$FX/work4" push -q -u origin main

# D: worktree registrations -> F4 (detached absent unique=0), F5 (branch absent 1 unpushed)
FXR="$FX/fxroot"
mkdir -p "$FXR"
git init -q -b main "$FXR/fx-shokunin"
printf 'x\n' > "$FXR/fx-shokunin/base.txt"
git -C "$FXR/fx-shokunin" add base.txt
git -C "$FXR/fx-shokunin" commit -q -m base
git -C "$FXR/fx-shokunin" worktree add -q --detach "$FXR/wt-f4" HEAD
rm -rf "$FXR/wt-f4"
git -C "$FXR/fx-shokunin" worktree add -q -b wt-f5 "$FXR/wt-f5" HEAD
printf 'extra\n' > "$FXR/wt-f5/extra.txt"
git -C "$FXR/wt-f5" add extra.txt
git -C "$FXR/wt-f5" commit -q -m extra
rm -rf "$FXR/wt-f5"

# E: pushed-unverifiable (E2) and single-origin-ref fallback (F9)
git init -q --bare -b main "$FX/origin9.git"
git init -q -b main "$FX/work9"
git -C "$FX/work9" remote add origin "$FX/origin9.git"
printf 'm\n' > "$FX/work9/main.txt"
git -C "$FX/work9" add main.txt
git -C "$FX/work9" commit -q -m main
git -C "$FX/work9" push -q -u origin main
git -C "$FX/work9" push -q origin main:dev
git clone -q "$FX/origin9.git" "$FX/work9b"
git -C "$FX/work9b" update-ref -d refs/remotes/origin/dev
git -C "$FX/work9b" remote set-head origin -d

# --- fixture cases -----------------------------------------------------------
run_tool 180 "$FX/work/baseline.txt"; parse_out "$OUT"
judge F1 "fixture case F1 (pushed file, ancestor of origin/HEAD)" 0 SAFE 'pushed' "origin/HEAD clone"

run_tool 180 "$FX/work/local-only.txt"; parse_out "$OUT"
judge F2 "fixture case F2 (introducing commit local-only)" 0 NOT-SAFE 'pushed-unverifiable|none' "unpushed commit not an ancestor"

run_tool 180 "$FX/work3"; parse_out "$OUT"
judge F3 "fixture case F3 (repo-root unpushed+dirty, kotodama-shaped)" 0 NOT-SAFE '.*' \
  "own oracle: unpushed=1 dirty=1" 'unpushed=1.*dirty=1'

run_tool 180 "$FX/work4"; parse_out "$OUT"
judge E1 "extra E1 (repo-root clean+pushed: still NOT-SAFE, counts 0/0)" 0 NOT-SAFE '.*' \
  "no obsidian receipt for repo-root" 'unpushed=0.*dirty=0'

run_tool_root "$FXR" 180 "$FXR/wt-f4"; parse_out "$OUT"
judge F4 "fixture case F4 (worktree detached, dir absent, unique=0)" 0 SAFE 'metadata-prune' \
  "owner=fx-shokunin SHOKUNIN_ROOT=<mktemp>"

run_tool_root "$FXR" 180 "$FXR/wt-f5"; parse_out "$OUT"
judge F5 "fixture case F5 (worktree named branch, 1 unpushed commit)" 0 NOT-SAFE 'unpushed-branch' \
  "owner=fx-shokunin branch wt-f5 unpushed=1, dir absent"

run_tool 180 "$FX/work/.scratch/aged10.log"; parse_out "$OUT"
judge F7 "fixture case F7 (scratch, no refs, mtime 10d)" 0 SAFE 'stale' \
  "refs on fixture repo: $(refs_diag "$FX/work" aged10.log)"

run_tool 180 "$FX/work/.scratch/f8-polluted.log"; parse_out "$OUT"
judge F8 "fixture case F8 (D3: basename planted in census-like dir)" 0 SAFE 'stale' \
  "planted ref in souji-shokunin/census/round-1; sweep diag: $(refs_diag "$FX/work" f8-polluted.log)"

run_tool 180 "$FX/work9b/main.txt"; parse_out "$OUT"
judge F9 "fixture case F9 (D1: origin/HEAD deleted, single origin ref)" 0 SAFE 'pushed' \
  "origin refs: main only, no origin/HEAD"

run_tool 180 "$FX/work9/main.txt"; parse_out "$OUT"
judge E2 "extra E2 (D1 terminal: 2 origin refs, no HEAD, no local master)" 0 NOT-SAFE 'pushed-unverifiable' \
  "origin refs main+dev, local branch main"

for f in test.env fixture-credential-note.txt fixture-secret-note.txt fixture-key.pem; do
  run_tool 180 "$FX/work/$f"; parse_out "$OUT"
  ML="$(marker_leak)"
  judge "F10:$f" "fixture case F10 (secrets-shaped target)" 0 NOT-SAFE 'secrets-refusal' \
    "marker check: $ML"
done

# ------------------------------------------------------------------ cli
PHASE=cli
run_tool 60
judge_rc "C1-usage-noargs" "spec: usage -> exit 2" 2 "no args"

run_tool 60 --bogus-flag
judge_rc "C1b-usage-badflag" "spec: usage -> exit 2" 2 "unknown flag"

run_tool 60 --stale-days abc "$FX/work/baseline.txt"
judge_rc "C2-usage-badN" "spec: usage -> exit 2" 2 "--stale-days with non-numeric N"

run_tool 60 "$TMP/does-not-exist-23"
parse_out "$OUT"
judge C3 "spec rail: missing target" 0 NOT-SAFE 'unreachable' "exit stays 0"

run_tool 180 --json "$FX/work/baseline.txt"
JOK=fail
if python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$OUT" 2>/dev/null; then JOK=pass; fi
add_case "C4-json" "$PHASE" "spec: --json output" "$TOOL_CMD" "$TOOL_RC" "rc=0 + parseable JSON" \
  "rc=$TOOL_RC json=$JOK" "$JOK" "json.load on stdout"

run_tool 180 "$FX/work/baseline.txt" "$FX/work/local-only.txt"
NLINES="$(grep -ac $'^VERDICT\t' "$OUT" || true)"
NLINES="${NLINES:-0}"
JB=fail
if [ "$TOOL_RC" = 0 ] && [ "$NLINES" = 2 ]; then JB=pass; fi
add_case "C6-multi-target" "$PHASE" "spec: one line per target" "$TOOL_CMD" "$TOOL_RC" "rc=0 + 2 VERDICT lines" \
  "rc=$TOOL_RC lines=$NLINES" "$JB" "two targets in one invocation"

run_tool 180 "$FX/work/baseline.txt"
parse_out "$OUT"
add_case "C7-format" "$PHASE" "spec: VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence" "$TOOL_CMD" "$TOOL_RC" \
  "literal VERDICT tag + tab fields" "tag=$TAG_SEEN fields=5" record "first line: $(head -n 1 "$OUT" | cut -c1-220)"

run_tool 180 --stale-days 30 "$FX/work/.scratch/aged10.log"; parse_out "$OUT"
judge C5b "spec: --stale-days threshold (10d old, N=30)" 0 NOT-SAFE 'none' "10 days old is not older than 30 days"

run_tool 180 "$FX/work/.scratch/fresh.log"; parse_out "$OUT"
judge C5c "spec: default threshold (fresh scratch, N=1)" 0 NOT-SAFE 'none' "fresh file is not older than 1 day"

# ------------------------------------------------------------------ live
PHASE=live
KOT="$FLEET_ROOT/kotodama-shokunin"
LORE="$FLEET_ROOT/lore-shokunin"
GD2D="$FLEET_ROOT/game-dev-2d-shokunin"

snap() { # snap <repo> -> head|porcelain_count|origin_refs_count
  local r="$1" h s o
  h="$(git -C "$r" rev-parse HEAD 2>/dev/null || echo none)"
  s="$(git -C "$r" status --porcelain 2>/dev/null | wc -l)"
  o="$(git -C "$r" for-each-ref refs/remotes/origin/ 2>/dev/null | wc -l)"
  printf '%s|%s|%s' "$h" "$s" "$o"
}
SNAP_KOT_BEFORE="$(snap "$KOT")"; SNAP_LORE_BEFORE="$(snap "$LORE")"
SNAP_GD2D_BEFORE="$(snap "$GD2D")"; SNAP_FLEET_BEFORE="$(snap "$FLEET_ROOT")"

ku="$(git -C "$KOT" log --oneline --branches --not --remotes 2>/dev/null | wc -l)"
kd="$(git -C "$KOT" status --porcelain 2>/dev/null | wc -l)"
run_tool 240 "$KOT"; parse_out "$OUT"
judge L1 "r2 gate: kotodama unpushed+dirty -> NOT-SAFE" 0 NOT-SAFE '.*' \
  "own counts unpushed=$ku dirty=$kd" 'unpushed=[0-9]+.*dirty=[0-9]+'

fu="$(git -C "$FLEET_ROOT" log --oneline --branches --not --remotes 2>/dev/null | wc -l)"
fd="$(git -C "$FLEET_ROOT" status --porcelain 2>/dev/null | wc -l)"
run_tool 240 "$FLEET_ROOT"; parse_out "$OUT"
judge L2 "live: fleet root repo-root -> NOT-SAFE with counts" 0 NOT-SAFE '.*' \
  "own counts unpushed=$fu dirty=$fd" 'unpushed=[0-9]+.*dirty=[0-9]+'

worktree_sweep() { # worktree_sweep <owner> <label>
  local owner="$1" label="$2" p h b d pr present unp uniq dirty expv expr
  while IFS=$'\t' read -r p h b d pr; do
    if [ -z "$p" ]; then continue; fi
    if [ "$p" = "$owner" ]; then continue; fi   # main worktree = the repo itself (kind 1)
    present=0
    if [ -e "$p" ]; then present=1; fi
    unp=0
    if [ -n "$b" ]; then unp="$( { git -C "$owner" log --oneline "$b" --not --remotes 2>/dev/null || true; } | wc -l)"; fi
    uniq="$( { git -C "$owner" log --oneline "$h" --not --all 2>/dev/null || true; } | wc -l)"
    dirty=0
    if [ "$present" = 1 ]; then dirty="$( { git -C "$p" status --porcelain 2>/dev/null || true; } | wc -l)"; fi
    expv=""; expr=""
    if [ -n "$b" ] && [ "$unp" -gt 0 ]; then expv=NOT-SAFE; expr=unpushed-branch
    elif [ "$present" = 0 ] && [ "$uniq" = 0 ]; then expv=SAFE; expr=metadata-prune
    elif [ "$present" = 1 ] && [ "$dirty" -gt 0 ]; then expv=NOT-SAFE; expr=dirty
    fi
    run_tool 180 "$p"; parse_out "$OUT"
    if [ -n "$expv" ]; then
      judge "WT:$label:${p##*/}" "spec kind2 worktree registration" 0 "$expv" "$expr" \
        "owner=${owner##*/} present=$present unp=$unp uniq=$uniq dirty=$dirty"
    else
      rec_case "WT:$label:${p##*/}" "spec kind2 (no bullet applies at oracle time)" \
        "owner=${owner##*/} present=$present unp=$unp uniq=$uniq dirty=$dirty"
    fi
  done < <(git -C "$owner" worktree list --porcelain | awk -F' ' '
      /^worktree /{p=substr($0,10)}
      /^HEAD /{h=$2}
      /^branch /{b=$2}
      /^detached/{d=1}
      /^prunable/{pr=1}
      /^$/{print p"\t"h"\t"b"\t"d"\t"pr; p="";h="";b="";d=0;pr=0}
      END{if(p!="")print p"\t"h"\t"b"\t"d"\t"pr}')
}

worktree_sweep "$LORE" lore
worktree_sweep "$GD2D" gd2d

# SHOKUNIN_ROOT explicitly set to the fleet root: same oracle, 2 spot checks
WT_SPOT_LORE="$(git -C "$LORE" worktree list --porcelain | awk '/^worktree /{n++; p=substr($0,10)} n==2{print p; exit}')"
WT_SPOT_GD2D="$(git -C "$GD2D" worktree list --porcelain | awk '/^worktree /{n++; p=substr($0,10)} n==2{print p; exit}')"
for pair in "$LORE|$WT_SPOT_LORE|lore" "$GD2D|$WT_SPOT_GD2D|gd2d"; do
  IFS='|' read -r owner wt label <<< "$pair"
  if [ -z "$wt" ]; then continue; fi
  wr_expect=SAFE; wr_receipt='metadata-prune'
  wr_b="$(git -C "$owner" worktree list --porcelain | awk -v t="$wt" '$0=="worktree "t{f=1} f&&/^branch /{print $2; exit}')"
  if [ -n "$wr_b" ]; then
    wr_u="$( { git -C "$owner" log --oneline "$wr_b" --not --remotes 2>/dev/null || true; } | wc -l)"
    if [ "$wr_u" -gt 0 ]; then wr_expect=NOT-SAFE; wr_receipt='unpushed-branch'; fi
  fi
  run_tool_root "$FLEET_ROOT" 180 "$wt"; parse_out "$OUT"
  judge "WT-ENV:$label:${wt##*/}" "spec: owner scan honors SHOKUNIN_ROOT" 0 "$wr_expect" "$wr_receipt" \
    "explicit SHOKUNIN_ROOT=<fleet root>"
done

# live pushed files (oracle-computed per D1 chain)
pushed_oracle() { # pushed_oracle <repo> <rel> -> SAFE:pushed | NOT-SAFE | pushed-unverifiable
  local r="$1" rel="$2" br intro
  br="$(git -C "$r" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' || true)"
  if [ -z "$br" ]; then
    local refs
    refs="$(git -C "$r" for-each-ref --format='%(refname)' refs/remotes/origin/ 2>/dev/null | grep -v '/HEAD$' || true)"
    if [ "$(printf '%s' "$refs" | grep -c . || true)" = 1 ]; then br="${refs##*/}"
    elif git -C "$r" show-ref --verify --quiet refs/heads/master; then br=master
    else echo "pushed-unverifiable"; return; fi
  fi
  intro="$(git -C "$r" log --diff-filter=A --format=%H -1 -- "$rel" 2>/dev/null || true)"
  if [ -n "$intro" ] && git -C "$r" merge-base --is-ancestor "$intro" "refs/remotes/origin/$br" 2>/dev/null; then
    echo "SAFE:pushed"; return
  fi
  if [ -n "$intro" ] && git -C "$r" merge-base --is-ancestor "$intro" "refs/heads/$br" 2>/dev/null; then
    echo "SAFE:pushed"; return
  fi
  echo "NOT-SAFE"
}

oracle_case() { # oracle_case <hard|soft> <name> <spec> <abs-file> <rel>
  local mode="$1" name="$2" spec="$3" abs="$4" rel="$5" repo exp
  repo="$(git -C "$(dirname "$abs")" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -z "$repo" ]; then rec_case "$name" "$spec" "no enclosing repo found by oracle"; return; fi
  exp="$(pushed_oracle "$repo" "$rel")"
  run_tool 180 "$abs"; parse_out "$OUT"
  case "$mode:$exp" in
    hard:SAFE:pushed) judge "$name" "$spec" 0 SAFE 'pushed' "oracle(owner=${repo##*/}) resolved $exp for $rel" ;;
    hard:pushed-unverifiable) judge "$name" "$spec" 0 NOT-SAFE 'pushed-unverifiable' "oracle(owner=${repo##*/}) resolved $exp for $rel" ;;
    *) rec_case "$name" "$spec" "oracle(owner=${repo##*/}) says $exp for $rel (soft: refusal reasons may legitimately differ)" ;;
  esac
}

oracle_case hard L4a "live: lore file, intro commit ancestor of origin/main" "$LORE/PROVINCE.md" "PROVINCE.md"
oracle_case soft L4b "live: souji file, D1 third fallback (local master exists)" "$REPO_ROOT/PROVINCE.md" "PROVINCE.md"
oracle_case hard L4c "live: fleet file, origin/HEAD=origin/master" "$FLEET_ROOT/templates/round-prompt.md" "templates/round-prompt.md"

# live secrets-shaped target (names only; content never read by this runner)
SEC_TARGET="$(ls -d "$FLEET_ROOT"/*/.env 2>/dev/null | head -n 1 || true)"
if [ -n "$SEC_TARGET" ]; then
  run_tool 120 "$SEC_TARGET"; parse_out "$OUT"
  judge "L5-secrets-live" "spec rail: secrets-shaped target" 0 NOT-SAFE 'secrets-refusal' \
    "target=${SEC_TARGET#$FLEET_ROOT/} (runner never read it)"
else
  add_case "L5-secrets-live" "$PHASE" "spec rail: secrets-shaped target" "ls -d <fleet>/*/.env" 0 \
    "NOT-SAFE/secrets-refusal" "no live *.env target found" record "skipped: none found at fleet depth 1"
fi

# ------------------------------------------------------------------ safety
SNAP_KOT_AFTER="$(snap "$KOT")"; SNAP_LORE_AFTER="$(snap "$LORE")"
SNAP_GD2D_AFTER="$(snap "$GD2D")"; SNAP_FLEET_AFTER="$(snap "$FLEET_ROOT")"
SAFETY_JSON="$(python3 - "$SNAP_KOT_BEFORE" "$SNAP_KOT_AFTER" "$SNAP_LORE_BEFORE" "$SNAP_LORE_AFTER" \
  "$SNAP_GD2D_BEFORE" "$SNAP_GD2D_AFTER" "$SNAP_FLEET_BEFORE" "$SNAP_FLEET_AFTER" <<'PY'
import json, sys
kot_b, kot_a, lore_b, lore_a, gd_b, gd_a, fl_b, fl_a = sys.argv[1:9]
def d(b, a):
    return {"before": b, "after": a, "changed": b != a}
print(json.dumps({
    "live_repo_snapshots": {
        "kotodama-shokunin": d(kot_b, kot_a),
        "lore-shokunin": d(lore_b, lore_a),
        "game-dev-2d-shokunin": d(gd_b, gd_a),
        "fleet-root": d(fl_b, fl_a),
    },
    "live_drift_note": "a 'changed' entry can be the owning lane's own in-flight work, not this runner; the runner never mutates real repos",
    "fixture_state": "all fixture git repositories were created under mktemp -d and removed on exit",
    "network": "none (fixture remotes are local paths)",
    "git_env": "GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null for this runner and its tool invocations",
}, indent=2))
PY
)"

# ------------------------------------------------------------------ emit
FINISHED_AT="$(date -u +%FT%TZ)"
FAILED="$(awk -F'\t' '$8=="fail"' "$CASES_TSV" | wc -l)"
TOTAL="$(wc -l < "$CASES_TSV" | tr -d ' ')"
if [ "$FAILED" -gt 0 ]; then STATUS=fail; else STATUS=pass; fi
TOOL_SHA_AFTER="$(sha256sum "$TOOL" 2>/dev/null | cut -d' ' -f1 || true)"
if [ "$TOOL_SHA_AFTER" != "$TOOL_SHA_BEFORE" ]; then
  write_json "tool changed on disk during the run (sha before != after); results are mixed-revision — re-run after integration"
else
  write_json "tool sha stable across the run"
fi
echo "runner-23: $STATUS ($TOTAL cases, $FAILED fail) -> $RESULTS_JSON"
if [ "$FAILED" -gt 0 ]; then
  awk -F'\t' '$8=="fail"{printf "  FAIL %s: expected %s | actual %s\n", $1, $6, $7}' "$CASES_TSV" | head -n 20 || true
fi
[ "$FAILED" -eq 0 ] || exit 1
