#!/usr/bin/env bash
# runner-31.sh — independent test runner for tools/souji-verify.sh (SEAT S31, round 2)
#
# Independent by construction: this runner builds its OWN fixtures under
# `mktemp -d /tmp/...` from the binding spec (tools/souji-verify.spec.md,
# cases F1..F10) and never consumes tests/fixtures/** owned by other seats.
# It is read-only over the live tree: every git write happens inside $WORK.
#
# usage: tests/runner-31.sh [--tool PATH] [--results PATH] [--wait SECONDS] [--keep]
#   --tool      tool under test          (default <lane>/tools/souji-verify.sh)
#   --results   JSON report path         (default <lane>/tests/results/runner-31.json)
#   --wait      seconds to wait for the tool to appear before running (default 0)
#   --keep      keep the mktemp fixture dir (default: removed)
# exit: 0 all checks pass | 1 any check failed/blocked-interface | 2 usage | 3 tool missing
#
# expectation DSL for assert_target: "<VERDICT>:<ok-reasons>[:<forbidden>]"
#   VERDICT     SAFE | NOT-SAFE | ANY
#   ok-reasons  '|'-separated receipt/reason tokens (at least one must appear)
#   forbidden   '|'-separated tokens that must NOT appear
set -euo pipefail
export LC_ALL=C

SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$SELF_DIR/.." && pwd)
TOOL="$ROOT/tools/souji-verify.sh"
RESULTS="$ROOT/tests/results/runner-31.json"
WAIT=0
KEEP=0
LIVE=0
TOOL_TIMEOUT=120

die_usage() { printf 'runner-31.sh: %s\n' "$1" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --tool)    [ $# -ge 2 ] || die_usage "--tool needs a value"; TOOL=$2; shift 2;;
    --results) [ $# -ge 2 ] || die_usage "--results needs a value"; RESULTS=$2; shift 2;;
    --wait)    [ $# -ge 2 ] || die_usage "--wait needs a value"; WAIT=$2; shift 2;;
    --live)    LIVE=1; shift;;
    --keep)    KEEP=1; shift;;
    -h|--help) sed -n '2,22p' "$0"; exit 0;;
    *) die_usage "unknown argument: $1";;
  esac
done

WORK=$(mktemp -d /tmp/souji31-runner.XXXXXX)
case "$WORK" in /tmp/souji31-runner.*) : ;; *) echo "refusing: WORK=$WORK" >&2; exit 9;; esac
BK="$WORK/.runner"; mkdir -p "$BK"
cleanup() { chmod -R u+rwX "$WORK" 2>/dev/null || true; [ "$KEEP" = 1 ] || rm -rf "$WORK"; }
trap cleanup EXIT

# ---------------------------------------------------------------- git hygiene
# fixture commits use a fixed identity/date set; nothing here ever runs
# fetch/push/branch/checkout/reset/rebase, and every git write is inside $WORK.
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_TERMINAL_PROMPT=0
export GIT_AUTHOR_NAME=souji-fixture GIT_AUTHOR_EMAIL=fixture@souji.local
export GIT_COMMITTER_NAME=souji-fixture GIT_COMMITTER_EMAIL=fixture@souji.local
FAKE_DATE_1=2026-10-14T00:00:00+00:00
FAKE_DATE_2=2026-10-14T00:01:00+00:00
FAKE_DATE_3=2026-10-14T00:02:00+00:00
STALE_STAMP=202610150000          # 3 days before the round date; > default 1 day

commit_at() { GIT_AUTHOR_DATE="$2" GIT_COMMITTER_DATE="$2" git -C "$1" commit -q -m "$3"; }
# stage a "remote" without any network verb: bare clone + hand-set tracking ref
wire_origin() { # repo [publish-tip]
  local repo=$1 tip=${2:-$(git -C "$1" rev-parse HEAD)}
  git clone -q --bare "$repo" "$repo.origin.git"
  git -C "$repo" remote add origin "$repo.origin.git"
  git -C "$repo" update-ref refs/remotes/origin/master "$tip"
  git -C "$repo" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
}

RTSV="$BK/results.tsv"; : > "$RTSV"
san_field() { local s=${1:-}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; printf '%s' "$s"; }
record() { # id case status expected observed exit detail
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san_field "$1")" "$(san_field "$2")" "$(san_field "$3")" "$(san_field "$4")" \
    "$(san_field "$5")" "$(san_field "${6:-}")" "$(san_field "${7:-}")" >> "$RTSV"
}
note() { record "$1" "$2" info "$3" "" "" "${4:-}"; }

# ------------------------------------------------------------- tool discovery
if [ "$WAIT" -gt 0 ]; then
  deadline=$(( SECONDS + WAIT ))
  while [ ! -f "$TOOL" ] && [ "$SECONDS" -lt "$deadline" ]; do sleep 5; done
fi
TOOL_EXISTS=false; TOOL_SHA=""; TOOL_SYNTAX="missing"; ENV_VARS=""
if [ -f "$TOOL" ]; then
  TOOL_EXISTS=true
  TOOL_SHA=$(sha256sum "$TOOL" | cut -d' ' -f1)
  if bash -n "$TOOL" 2>"$BK/syntax.err"; then TOOL_SYNTAX=ok
  else TOOL_SYNTAX=$(head -c 300 "$BK/syntax.err"); fi
  ENV_VARS=$(rg -o --no-filename '\$\{?[A-Z][A-Z0-9_]{2,}\}?' "$TOOL" 2>/dev/null \
             | tr -d '${}' | sort -u | tr '\n' ' ' || true)
fi
SPEC="$ROOT/tools/souji-verify.spec.md"
SPEC_SHA=$([ -f "$SPEC" ] && sha256sum "$SPEC" | cut -d' ' -f1 || echo missing)

# -------------------------------------------------------------------- fixtures
FIXROOT="$WORK/fleet"                      # mimics $SHOKUNIN_ROOT
mkdir -p "$FIXROOT/souji-shokunin/corpus/knowledge" "$FIXROOT/corpus/knowledge"

# --- F1: file whose introducing commit is a strict ancestor of origin/master
F1="$WORK/f1-pushed"; git init -q -b master "$F1"
printf 'F1 payload: pushed ancestor of origin/master\n' > "$F1/pushed-keep.txt"
git -C "$F1" add pushed-keep.txt; commit_at "$F1" "$FAKE_DATE_1" f1-c1
printf 'second pushed commit\n' > "$F1/pushed-other.txt"
git -C "$F1" add pushed-other.txt; commit_at "$F1" "$FAKE_DATE_2" f1-c2
wire_origin "$F1"

# --- F2: file introduced by a local-only commit
F2R="$WORK/f2-local"; git init -q -b master "$F2R"
printf 'base\n' > "$F2R/base.txt"; git -C "$F2R" add base.txt; commit_at "$F2R" "$FAKE_DATE_1" f2-c1
wire_origin "$F2R"
printf 'F2 payload: introducing commit never published\n' > "$F2R/local-only.txt"
git -C "$F2R" add local-only.txt; commit_at "$F2R" "$FAKE_DATE_3" f2-c2-local

# --- F3: kotodama-shaped repo root: unpushed commits + dirty tree
F3R="$WORK/f3-kotodama-shaped"; git init -q -b master "$F3R"
printf 'base\n' > "$F3R/base.txt"; git -C "$F3R" add base.txt; commit_at "$F3R" "$FAKE_DATE_1" f3-c1
wire_origin "$F3R"
printf 'unpushed one\n' > "$F3R/u1.txt"; git -C "$F3R" add u1.txt; commit_at "$F3R" "$FAKE_DATE_2" f3-c2
printf 'unpushed two\n' > "$F3R/u2.txt"; git -C "$F3R" add u2.txt; commit_at "$F3R" "$FAKE_DATE_3" f3-c3
printf 'dirty tracked edit\n' >> "$F3R/base.txt"
printf 'dirty untracked\n' > "$F3R/untracked.tmp"

# --- F4/F5: worktree registrations in an owner repo discoverable via SHOKUNIN_ROOT
WTOWNER="$FIXROOT/fixture-shokunin"; git init -q -b master "$WTOWNER"
printf 'owner note\n' > "$WTOWNER/owner-note.txt"
git -C "$WTOWNER" add owner-note.txt; commit_at "$WTOWNER" "$FAKE_DATE_1" wt-owner-c1
WT_C1=$(git -C "$WTOWNER" rev-parse HEAD)
printf 'owner note two\n' > "$WTOWNER/owner-note2.txt"
git -C "$WTOWNER" add owner-note2.txt; commit_at "$WTOWNER" "$FAKE_DATE_2" wt-owner-c2
wire_origin "$WTOWNER"
# F5: real worktree, named branch, exactly one unpushed commit, clean dir
F5DIR="$WORK/wt-r99-f5"
git -C "$WTOWNER" worktree add -q -b wt-r99 "$F5DIR" master
printf 'f5 payload\n' > "$F5DIR/f5.txt"; git -C "$F5DIR" add f5.txt
commit_at "$F5DIR" "$FAKE_DATE_3" f5-unpushed
# F4: prunable registration whose directory is gone. Built LAST because
# `git worktree add` can prune stale registrations while it runs; the shape is
# the real one (add a detached worktree, then delete its directory).
F4DIR="$WORK/wt-absent-f4"
git -C "$WTOWNER" worktree add -q --detach "$F4DIR" "$WT_C1"
rm -rf "$F4DIR"

# --- F6: obsidian-ledger match (source + vault sha256 on both sides)
F6SRC_DIR="$FIXROOT/kept-artifacts"; mkdir -p "$F6SRC_DIR"
F6SRC="$F6SRC_DIR/kept-artifact.md"
printf 'F6 payload: preserved artifact recorded in the obsidian ledger\n' > "$F6SRC"
F6VAULT_DIR="$FIXROOT/vault"; mkdir -p "$F6VAULT_DIR"
F6VAULT="$F6VAULT_DIR/kept-artifact.md"
cp "$F6SRC" "$F6VAULT"
F6_SHA=$(sha256sum "$F6SRC" | cut -d' ' -f1)
F6_VAULT_SHA=$(sha256sum "$F6VAULT" | cut -d' ' -f1)
# F6b: ledger row whose vault copy is edited afterwards (hash re-check must fail)
F6BSRC="$F6SRC_DIR/stale-ledger-row.md"
printf 'F6b payload: ledger row exists but the vault copy no longer matches\n' > "$F6BSRC"
F6BVAULT="$F6VAULT_DIR/stale-ledger-row.md"
cp "$F6BSRC" "$F6BVAULT"
F6B_SHA=$(sha256sum "$F6BSRC" | cut -d' ' -f1)
F6B_VAULT_SHA_AT_ROW=$(sha256sum "$F6BVAULT" | cut -d' ' -f1)
LEDGER_PRIMARY="$FIXROOT/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv"
LEDGER_ALT="$FIXROOT/corpus/knowledge/obsidian-ledger.tsv"
for L in "$LEDGER_PRIMARY" "$LEDGER_ALT"; do
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18\trunner-31 F6 fixture (absolute keying)\n' \
      "$F6SRC" "$F6_SHA" "$F6VAULT" "$F6_VAULT_SHA"
    printf '%s\t%s\t%s\t%s\t2026-10-18\trunner-31 F6 fixture (root-relative keying)\n' \
      "kept-artifacts/kept-artifact.md" "$F6_SHA" "$F6VAULT" "$F6_VAULT_SHA"
    printf '%s\t%s\t%s\t%s\t2026-10-18\trunner-31 F6b fixture (vault file edited after the row)\n' \
      "$F6BSRC" "$F6B_SHA" "$F6BVAULT" "$F6B_VAULT_SHA_AT_ROW"
  } > "$L"
done
# F6b: the vault copy changed after the ledger row was written -> no receipt
printf 'edited inside the vault after the row was recorded\n' >> "$F6BVAULT"

# --- F7/F8: scratch artifacts, zero live references, old mtime
F7R="$WORK/f7-scratch"; git init -q -b master "$F7R"
printf 'base\n' > "$F7R/base.txt"; git -C "$F7R" add base.txt; commit_at "$F7R" "$FAKE_DATE_1" f7-c1
wire_origin "$F7R"
mkdir -p "$F7R/.scratch"
F7T="$F7R/.scratch/deadfile-f7.out"
printf 'F7 payload: unreferenced scratch\n' > "$F7T"; touch -t "$STALE_STAMP" "$F7T"
# F8: basename mentioned only in census fragments (D3); also fleet-root-shaped copy
F8T="$F7R/.scratch/census-mention-f8.out"
printf 'F8 payload: mentioned only by census fragments\n' > "$F8T"; touch -t "$STALE_STAMP" "$F8T"
mkdir -p "$F7R/souji-shokunin/census/round-9" "$F7R/souji-shokunin/tests" "$F7R/.ufo-quarantine/2026-10-15"
printf '{"note":"census-mention-f8.out appeared in round-9 fragments"}\n' \
  > "$F7R/souji-shokunin/census/round-9/fragment.json"
mkdir -p "$FIXROOT/souji-shokunin/census/round-9"
printf '{"note":"census-mention-f8.out appeared in round-9 fragments"}\n' \
  > "$FIXROOT/souji-shokunin/census/round-9/fragment.json"
# F8b: mention inside the lane-shaped tests/ dir
F8BT="$F7R/.scratch/tests-mention-f8b.out"
printf 'F8b payload: mentioned only by lane tests/\n' > "$F8BT"; touch -t "$STALE_STAMP" "$F8BT"
printf '{"note":"tests-mention-f8b.out appears in runner expectations"}\n' \
  > "$F7R/souji-shokunin/tests/expected.json"
# F8c: mention inside a .ufo-quarantine dir
F8CT="$F7R/.scratch/quarantine-mention-f8c.out"
printf 'F8c payload: mentioned only by quarantine notes\n' > "$F8CT"; touch -t "$STALE_STAMP" "$F8CT"
printf 'quarantine-mention-f8c.out staged here\n' > "$F7R/.ufo-quarantine/2026-10-15/note.md"
# F7b: scratch-shaped and old, but genuinely referenced -> stale must NOT fire
F7BT="$F7R/.scratch/live-referenced-f7b.out"
printf 'F7b payload: this one is still referenced\n' > "$F7BT"; touch -t "$STALE_STAMP" "$F7BT"
printf 'Live notes: live-referenced-f7b.out is still used by the pipeline.\n' > "$F7R/notes-live.md"
# F7c: scratch-shaped, unreferenced, but fresh -> stale must NOT fire
F7CT="$F7R/.scratch/fresh-f7c.out"
printf 'F7c payload: unreferenced but written today\n' > "$F7CT"

# --- F9: default-branch resolution fallbacks (D1)
F9="$WORK/f9-single-origin"; git init -q -b master "$F9"
printf 'F9 payload\n' > "$F9/pushed-keep-9.txt"
git -C "$F9" add pushed-keep-9.txt; commit_at "$F9" "$FAKE_DATE_1" f9-c1
printf 'F9 second\n' > "$F9/other9.txt"
git -C "$F9" add other9.txt; commit_at "$F9" "$FAKE_DATE_2" f9-c2
git clone -q --bare "$F9" "$F9.origin.git"
git -C "$F9" remote add origin "$F9.origin.git"
git -C "$F9" update-ref refs/remotes/origin/master "$(git -C "$F9" rev-parse HEAD)"
# origin/HEAD deliberately never set: exactly one refs/remotes/origin/* ref
F9B="$WORK/f9b-master-only"; git init -q -b master "$F9B"
printf 'F9b payload\n' > "$F9B/pushed-keep-9b.txt"
git -C "$F9B" add pushed-keep-9b.txt; commit_at "$F9B" "$FAKE_DATE_1" f9b-c1
printf 'F9b second\n' > "$F9B/other9b.txt"
git -C "$F9B" add other9b.txt; commit_at "$F9B" "$FAKE_DATE_2" f9b-c2
# no origin refs at all, local master exists -> 'master' fallback
F9C="$WORK/f9c-no-default"; git init -q -b trunk "$F9C"
printf 'F9c payload\n' > "$F9C/no-default.txt"
git -C "$F9C" add no-default.txt; commit_at "$F9C" "$FAKE_DATE_1" f9c-c1

# --- F10: secret-shaped basenames (app.env is mode 000: refusal must not read)
F10="$WORK/f10-secrets"; mkdir -p "$F10"
printf 'CANARY=souji31-env-canary-9d4c1a\n' > "$F10/app.env"
printf 'SOUJI31-PEM-CANARY-7b2e80\n' > "$F10/creds.pem"
printf 'F10 control payload: ordinary file, ordinary receipt chain\n' > "$F10/notes.txt"
chmod 600 "$F10/creds.pem"; chmod 000 "$F10/app.env"

# ------------------------------------------------------- read-only fingerprint
fingerprint() {
  local out=$1
  {
    for d in "$F1" "$F2R" "$F3R" "$WTOWNER" "$F7R" "$F9" "$F9B" "$F9C"; do
      printf '## repo %s\n' "${d//$WORK/<work>}"
      printf 'refs: %s\n' "$(git -C "$d" for-each-ref --format='%(refname)=%(objectname)' | sort | tr '\n' ' ')"
      printf 'status: %s\n' "$(git -C "$d" status --porcelain | sort | tr '\n' ' ')"
      printf 'worktrees: %s\n' "$(git -C "$d" worktree list --porcelain | sort | tr '\n' ' ')"
      printf 'commits: %s\n' "$(git -C "$d" log --all --format=%H | sort | tr '\n' ' ')"
    done
    printf '## files\n'
    find "$WORK" \( -name .git -o -name .runner \) -prune -o -type f -print 2>/dev/null | sort | while read -r f; do
      if [ -r "$f" ] && [ -s "$f" ]; then printf '%s %s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "${f//$WORK/<work>}"
      else printf 'unreadable-or-empty %s\n' "${f//$WORK/<work>}"; fi
    done
  } > "$out" 2>/dev/null || true
}

# ---------------------------------------------------------------- CLI battery
OUT_TEXT=""; OUT_ERR=""; OUT_CODE=0
RUN_ENV=(SHOKUNIN_ROOT="$FIXROOT" SOUJI_LEDGER="$LEDGER_PRIMARY"
         SOUJI_LEDGER_PATH="$LEDGER_PRIMARY" SOUJI_ROOT="$FIXROOT")
run_tool() {
  local rc=0
  OUT_TEXT=$(env "${RUN_ENV[@]}" timeout "$TOOL_TIMEOUT" bash "$TOOL" "$@" 2>"$BK/stderr") || rc=$?
  OUT_CODE=$rc
  OUT_ERR=$(cat "$BK/stderr" 2>/dev/null || true)
  { printf '### args:'; printf ' [%s]' "$@"; printf '\n--stdout--\n%s\n--stderr--\n%s\n--rc=%s\n' \
      "$OUT_TEXT" "$OUT_ERR" "$rc"; } >> "$BK/tool-output.all"
}
line_of() { printf '%s\n' "$OUT_TEXT" | awk -F'\t' -v t="$1" 'NF>=3 && $2==t {print; f=1} END{if(!f) exit 1}'; }
verdict_of() { printf '%s' "$1" | awk -F'\t' '{v=$3; gsub(/[()[:space:]]/,"",v); print toupper(v)}'; }
reason_of() { printf '%s' "$1" | awk -F'\t' '{r=$4; gsub(/[()]/,"",r); print tolower(r)}'; }
joined_of() { printf '%s' "$1" | awk -F'\t' '{s=$3; for(i=4;i<=NF;i++) s=s" "$i; print tolower(s)}'; }
has_tok() { printf '%s' "$1" | grep -Eq "(^|[^[:alnum:]_-])$2([^[:alnum:]_-]|\$)"; }

assert_target() { # id case target "<VERDICT>:<ok-reasons>[:<forbidden>]"
  local id=$1 case=$2 tgt=$3 exp=$4
  local want=${exp%%:*}; rest=${exp#*:}; ok=${rest%%:*}; forb=""
  case "$rest" in *:*) forb=${rest#*:};; esac
  local line
  if ! line=$(line_of "$tgt"); then
    record "$id" "$case" fail "line for '$tgt' -> $exp" "no line with field2=='$tgt' (exit $OUT_CODE)" "$OUT_CODE" "$OUT_ERR"
    return 0
  fi
  local v r j vraw; vraw=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
  v=$(verdict_of "$line"); r=$(reason_of "$line"); j=$(joined_of "$line")
  case "$v" in
    SAFE|NOT-SAFE) : ;;
    *) if printf '%s' "$j" | grep -q 'not-safe'; then v=NOT-SAFE; else v=SAFE; fi
       j="$j [verdict-field='$vraw' not clean]" ;;
  esac
  local vok=false tok=false fok=true t okhit=""
  [ "$want" = ANY ] && vok=true
  [ "$v" = "$want" ] && vok=true
  if [ "$ok" = "*" ]; then
    tok=true; okhit='*'
  else
    IFS='|' read -r -a toks <<< "$ok"
    for t in "${toks[@]}"; do
      if has_tok "$r" "$t" || has_tok "$j" "$t"; then tok=true; okhit=$t; fi
    done
  fi
  if [ -n "$forb" ]; then
    IFS='|' read -r -a ftoks <<< "$forb"
    for t in "${ftoks[@]}"; do has_tok "$r" "$t" && fok=false; done
  fi
  local status=pass detail="reason='$r' matched='$okhit'"
  [ "$vok" = true ] || { status=fail; detail="$detail verdict_mismatch"; }
  [ "$tok" = true ] || { status=fail; detail="$detail reason_token_missing"; }
  [ "$fok" = true ] || { status=fail; detail="$detail forbidden_token_present"; }
  record "$id" "$case" "$status" "$exp" "exit=$OUT_CODE line=$line" "$OUT_CODE" "$detail"
}

assert_evidence() { # id case target regex
  local id=$1 case=$2 tgt=$3 re=$4 line
  if ! line=$(line_of "$tgt"); then
    record "$id" "$case" fail "evidence ~/$re/" "no line for '$tgt'" "$OUT_CODE" "$OUT_ERR"; return 0
  fi
  local ev; ev=$(printf '%s' "$line" | awk -F'\t' '{print $5"\t"$4}')
  if printf '%s' "$ev" | grep -Eq "$re"; then
    record "$id" "$case" pass "evidence ~/$re/" "line=$line" "$OUT_CODE" ""
  else
    record "$id" "$case" fail "evidence ~/$re/" "line=$line" "$OUT_CODE" "evidence field lacks $re"
  fi
}

assert_exit() { # id case expected_code detail
  if [ "$3" = "$OUT_CODE" ]; then record "$1" "$2" pass "exit=$3" "exit=$OUT_CODE" "$OUT_CODE" "${4:-}"
  else record "$1" "$2" fail "exit=$3" "exit=$OUT_CODE" "$OUT_CODE" "${4:-}"; fi
}

fingerprint "$BK/fp.before"

if [ "$TOOL_EXISTS" != true ]; then
  note "tool.present" "P0" "tool absent: $TOOL"
  note "tool.interface" "P0" "env overrides seen: none (tool absent)"
else
  note "tool.present" "P0" "sha256=$TOOL_SHA syntax=$TOOL_SYNTAX"
  note "tool.interface" "P0" "all-caps env vars referenced in source: ${ENV_VARS:-none}"
fi

if [ "$TOOL_EXISTS" = true ]; then
  # --- P1: the tool's own selftest
  TOOL_TIMEOUT=300 run_tool --selftest
  assert_exit "selftest.exit" "P1" 0 "$(printf '%s' "$OUT_ERR" | tail -c 200)"
  note "selftest.output-tail" "P1" "$(printf '%s\n%s' "$OUT_TEXT" "$OUT_ERR" | tail -3 | tr '\n' ' ' | cut -c1-300)"
  TOOL_TIMEOUT=120

  # --- F1 file introduced pre-tip, pushed
  run_tool "$F1/pushed-keep.txt"
  assert_target "F1.pushed" "F1" "$F1/pushed-keep.txt" "SAFE:pushed"

  # --- F2 introducing commit local-only
  run_tool "$F2R/local-only.txt"
  assert_target "F2.local-only" "F2" "$F2R/local-only.txt" "NOT-SAFE:none|pushed-unverifiable"

  # --- F3 kotodama-shaped repo root
  run_tool "$F3R"
  assert_target "F3.repo-root" "F3" "$F3R" "NOT-SAFE:unpushed|dirty|none"
  assert_evidence "F3.evidence-counts" "F3" "$F3R" 'unpushed=[0-9]+ dirty=[0-9]+'

  # --- F3b clean, fully pushed repo root: still no receipt (never remove a live repo)
  run_tool "$F1"
  assert_target "F3b.clean-repo-root" "F3" "$F1" "NOT-SAFE:*"
  assert_evidence "F3b.clean-counts" "F3" "$F1" 'unpushed=0 dirty=0'

  # --- F4 metadata-only registration, absent dir, unique=0
  run_tool "$F4DIR"
  assert_target "F4.metadata-prune" "F4" "$F4DIR" "SAFE:metadata-prune"

  # --- F5 named-branch worktree with one unpushed commit
  run_tool "$F5DIR"
  assert_target "F5.unpushed-branch" "F5" "$F5DIR" "NOT-SAFE:unpushed-branch"

  # --- F6 ledger match; F6b ledger row whose vault copy changed
  run_tool "$F6SRC"
  assert_target "F6.moved-to-obsidian" "F6" "$F6SRC" "SAFE:moved-to-obsidian"
  run_tool "$F6BSRC"
  assert_target "F6b.vault-hash-mismatch" "F6" "$F6BSRC" "NOT-SAFE:*"

  # --- F7 stale scratch; F7b referenced; F7c fresh
  run_tool "$F7T"
  assert_target "F7.stale" "F7" "$F7T" "SAFE:stale"
  run_tool "$F7BT" "$F7CT"
  assert_target "F7b.live-referenced" "F7" "$F7BT" "NOT-SAFE:*:stale"
  assert_target "F7c.fresh-mtime" "F7" "$F7CT" "NOT-SAFE:*:stale"

  # --- F8/F8b/F8c exclusion regressions (D3)
  run_tool "$F8T" "$F8BT" "$F8CT"
  assert_target "F8.census-mention" "F8" "$F8T" "SAFE:stale"
  assert_target "F8b.tests-mention" "F8" "$F8BT" "SAFE:stale"
  assert_target "F8c.quarantine-mention" "F8" "$F8CT" "SAFE:stale"

  # --- F9 default-branch resolution fallbacks (D1)
  run_tool "$F9/pushed-keep-9.txt"
  assert_target "F9.single-origin-ref" "F9" "$F9/pushed-keep-9.txt" "SAFE:pushed"
  run_tool "$F9B/pushed-keep-9b.txt"
  assert_target "F9b.master-fallback" "F9" "$F9B/pushed-keep-9b.txt" "SAFE:pushed"
  run_tool "$F9C/no-default.txt"
  assert_target "F9c.no-default-branch" "F9" "$F9C/no-default.txt" "NOT-SAFE:pushed-unverifiable|none"

  # --- F10 secrets refusal (app.env mode 000: refusal must not need a read)
  run_tool "$F10/app.env" "$F10/creds.pem" "$F10/notes.txt"
  assert_target "F10.env" "F10" "$F10/app.env" "NOT-SAFE:secrets-refusal"
  assert_target "F10.pem" "F10" "$F10/creds.pem" "NOT-SAFE:secrets-refusal"
  assert_target "F10.control" "F10" "$F10/notes.txt" "ANY:none|pushed|pushed-unverifiable:secrets-refusal"

  # --- flag semantics, unreachable targets, usage, --json, batch determinism
  run_tool --stale-days 30 "$F7T"
  assert_target "flag.stale-days-30" "F7" "$F7T" "NOT-SAFE:none"
  run_tool --stale-days 0 "$F7T"
  assert_target "flag.stale-days-0" "F7" "$F7T" "SAFE:stale"
  run_tool "$WORK/does-not-exist-31"
  assert_exit "unreachable.exit" "X1" 0
  assert_target "unreachable.missing-path" "X1" "$WORK/does-not-exist-31" "NOT-SAFE:unreachable"
  run_tool ""
  assert_target "unreachable.empty-arg" "X1" "" "NOT-SAFE:unreachable"
  run_tool --definitely-not-a-flag
  assert_exit "usage.unknown-flag" "X2" 2 "$(printf '%s' "$OUT_ERR" | head -c 200)"
  run_tool --json "$F1/pushed-keep.txt"
  assert_exit "json.exit" "X3" 0
  if printf '%s' "$OUT_TEXT" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
    note "json.parses" "X3" "output parses as JSON"
  else
    note "json.parses" "X3" "output is not JSON: $(printf '%s' "$OUT_TEXT" | head -c 160 | tr '\n' ' ')"
  fi
  run_tool "$F1/pushed-keep.txt" "$F3R" "$F7T"
  BATCH_1="$OUT_TEXT"
  assert_target "batch.f1" "X4" "$F1/pushed-keep.txt" "SAFE:pushed"
  assert_target "batch.f3" "X4" "$F3R" "NOT-SAFE:unpushed|dirty|none"
  assert_target "batch.f7" "X4" "$F7T" "SAFE:stale"
  run_tool "$F1/pushed-keep.txt" "$F3R" "$F7T"
  if [ "$BATCH_1" = "$OUT_TEXT" ]; then record "determinism.rerun" "X4" pass "identical output on rerun" "identical" "$OUT_CODE" ""
  else record "determinism.rerun" "X4" fail "identical output on rerun" "differs" "$OUT_CODE" ""; fi
else
  for c in selftest.exit F1.pushed F2.local-only F3.repo-root F3.evidence-counts F3b.clean-repo-root \
           F3b.clean-counts F4.metadata-prune F5.unpushed-branch F6.moved-to-obsidian \
           F6b.vault-hash-mismatch F7.stale F7b.live-referenced F7c.fresh-mtime F8.census-mention \
           F8b.tests-mention F8c.quarantine-mention F9.single-origin-ref F9b.master-fallback \
           F9c.no-default-branch F10.env F10.pem F10.control flag.stale-days-30 flag.stale-days-0 \
           unreachable.exit unreachable.missing-path unreachable.empty-arg usage.unknown-flag json.exit \
           batch.f1 batch.f3 batch.f7 determinism.rerun; do
    record "$c" "P0" skip "tool missing" "not run" "" "tools/souji-verify.sh absent"
  done
fi

# --------------------------------------------------------- post-run invariants
fingerprint "$BK/fp.after"
RO_IDENTICAL=true
cmp -s "$BK/fp.before" "$BK/fp.after" || RO_IDENTICAL=false
if [ "$TOOL_EXISTS" != true ]; then
  record "readonly.fixtures-unchanged" "P2" skip "fixture tree identical before vs after" "not run" ""
elif [ "$RO_IDENTICAL" = true ]; then
  record "readonly.fixtures-unchanged" "P2" pass "fixture tree identical before vs after" "identical" ""
else
  record "readonly.fixtures-unchanged" "P2" fail "fixture tree identical before vs after" "changed" "" "tool wrote into a fixture it only inspects"
fi

CANARY_LEAK=false
if [ -f "$BK/tool-output.all" ]; then
  grep -qF 'souji31-env-canary-9d4c1a' "$BK/tool-output.all" && CANARY_LEAK=true
  grep -qF 'SOUJI31-PEM-CANARY-7b2e80' "$BK/tool-output.all" && CANARY_LEAK=true
fi
if [ "$TOOL_EXISTS" != true ]; then
  record "secrets.no-content-leak" "F10" skip "secret content never in tool output" "not run" ""
elif [ "$CANARY_LEAK" = true ]; then
  record "secrets.no-content-leak" "F10" fail "secret content never in tool output" "canary found" "" "tool printed secret-file content"
else
  record "secrets.no-content-leak" "F10" pass "secret content never in tool output" "no canary" ""
fi

# A fixture failing only because the tool exposes no override hook is a wiring
# gap, not a wrong verdict - classify it separately from a genuine failure.
if [ "$TOOL_EXISTS" = true ]; then
  class_interface_gap() { # check-id source-pattern hook-pattern
    local id=$1 pattern=$2 hook=$3
    awk -F'\t' -v id="$id" '$1==id && $3=="fail"{f=1} END{exit !f}' "$RTSV" || return 0
    if grep -q "$pattern" "$TOOL" && ! grep -q "$hook" "$TOOL"; then
      awk -F'\t' -v id="$id" -v hook="$hook" 'BEGIN{OFS="\t"}
        $1==id && $3=="fail" {$3="blocked-interface"; $7=$7" (tool source lacks a " hook " override hook)"}
        {print}' "$RTSV" > "$RTSV.tmp" && mv "$RTSV.tmp" "$RTSV"
    fi
  }
  class_interface_gap F4.metadata-prune 'worktree' 'SHOKUNIN_ROOT'
  class_interface_gap F5.unpushed-branch 'worktree' 'SHOKUNIN_ROOT'
  class_interface_gap F6.moved-to-obsidian 'obsidian-ledger' 'LEDGER'
fi

# --------------------------------------------------------------- JSON assembly
mkdir -p "$(dirname "$RESULTS")"
python3 - "$RTSV" "$RESULTS" "$WORK" "$TOOL" "$TOOL_SHA" "$TOOL_SYNTAX" "$SPEC_SHA" \
        "$RO_IDENTICAL" "$CANARY_LEAK" "$ENV_VARS" "$LEDGER_PRIMARY" "$LEDGER_ALT" "$FIXROOT" <<'PY'
import json, sys, collections, datetime, os
(tsv, out_path, work, tool, tool_sha, tool_syntax, spec_sha,
 ro_identical, canary_leak, env_vars, ledger_primary, ledger_alt, fixroot) = sys.argv[1:14]

def san(s):
    return (s or "").replace(work, "<work>")

checks = []
for raw in open(tsv):
    if not raw.strip():
        continue
    f = (raw.rstrip("\n").split("\t") + [""] * 7)[:7]
    checks.append({
        "id": san(f[0]), "case": san(f[1]), "status": f[2],
        "expected": san(f[3]), "observed": san(f[4]),
        "exit_code": int(f[5]) if f[5].strip().lstrip("-").isdigit() else None,
        "detail": san(f[6]),
    })

counts = collections.Counter(c["status"] for c in checks)
fails = [c["id"] for c in checks if c["status"] == "fail"]
blocked = [c["id"] for c in checks if c["status"] == "blocked-interface"]
skipped = [c["id"] for c in checks if c["status"] == "skip"]
measured = [c for c in checks if c["status"] not in ("info", "skip")]

if not measured:
    status, exit_code = "blocked", 3
elif fails or blocked:
    status, exit_code = "fail", 1
else:
    status, exit_code = "pass", 0

fixture_inventory = []
fdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(tool))), "tests", "fixtures")
if os.path.isdir(fdir):
    fixture_inventory = sorted(os.listdir(fdir))

report = {
    "runner": "S31",
    "lane": "souji-shokunin",
    "round": 2,
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "generator": "tests/runner-31.sh",
    "status": status,
    "exit_code": exit_code,
    "counts": {"total": len(checks), "pass": counts["pass"], "fail": counts["fail"],
               "blocked-interface": counts["blocked-interface"], "skip": counts["skip"],
               "info": counts["info"]},
    "failed_checks": fails,
    "blocked_interface_checks": blocked,
    "skipped_checks": skipped,
    "tool": {"path": "tools/souji-verify.sh", "exists": os.path.isfile(tool),
             "sha256": tool_sha or None, "bash_syntax": tool_syntax},
    "spec": {"path": "tools/souji-verify.spec.md", "sha256": spec_sha},
    "method": {
        "independence": "own fixtures built from the spec under mktemp -d; tests/fixtures/** of other seats not consumed",
        "fixture_root": "mktemp -d /tmp/souji31-runner.XXXXXX (ephemeral, cleaned up)",
        "shokunin_root_override": fixroot.replace(work, "<work>"),
        "ledger_locations_provisioned": [ledger_primary.replace(work, "<work>"),
                                        ledger_alt.replace(work, "<work>")],
        "env_overrides_declared_in_tool_source": env_vars.split() if env_vars.strip() else [],
        "env_passed_to_every_invocation": ["SHOKUNIN_ROOT", "SOUJI_LEDGER", "SOUJI_LEDGER_PATH", "SOUJI_ROOT"],
        "git_writes": "confined to the mktemp fixture dir; no fetch/push/branch/checkout/reset/rebase anywhere",
        "path_placeholders": "<work> = the ephemeral mktemp fixture root",
    },
    "readonly_fingerprint": {
        "identical": ro_identical == "true",
        "components": "per-fixture-repo refs+status+worktree-list+commit-list, plus sha256 of every fixture file",
    },
    "canary_leak": {"leaked": canary_leak == "true",
                    "canaries": ["souji31-env-canary-9d4c1a", "SOUJI31-PEM-CANARY-7b2e80"],
                    "scope": "tool stdout+stderr across every invocation"},
    "fixture_inventory_tests_fixtures_dir": fixture_inventory,
    "checks": checks,
}
with open(out_path, "w") as fh:
    json.dump(report, fh, indent=2, sort_keys=False)
    fh.write("\n")
print("runner-31: status=%s exit=%d pass=%d fail=%d blocked-interface=%d skip=%d info=%d"
      % (status, exit_code, counts["pass"], counts["fail"], counts["blocked-interface"],
         counts["skip"], counts["info"]))
if fails:
    print("failed: " + ", ".join(fails))
if blocked:
    print("blocked-interface: " + ", ".join(blocked))
PY

exit "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["exit_code"])' "$RESULTS")"
