#!/usr/bin/env bash
# tests/runner-27.sh — independent test runner for tools/souji-verify.sh
# Seat S27, round 2. Twin seat S17 owns tests/results/runner-17.json; this
# runner is written from tools/souji-verify.spec.md only and shares nothing
# with it (own fixtures, own expectations, own output file).
#
# Independence: it does NOT rely on the tool's own --selftest for fixture
# construction. Every fixture below is built here, under mktemp -d, with git
# plumbing only (init / hash-object / update-index / write-tree / commit-tree
# / update-ref / symbolic-ref) — no fetch, push, commit, branch, checkout,
# reset or rebase is ever run, in any repo, live or fixture.
#
# usage: tests/runner-27.sh [--fixtures-only] [--tool PATH] [--out PATH] [--keep]
#   --fixtures-only  build fixtures, run fixture-validity self-checks only
#                    (no tool invocation, nothing written into the repo)
#   --tool PATH      candidate tool (default <repo>/tools/souji-verify.sh)
#   --out PATH       JSON result (default <repo>/tests/results/runner-27.json)
#   --keep           keep the mktemp dir and print its path
# exit: 0 all strict cases pass; 1 strict failure(s) or tool missing
set -euo pipefail

SEAT="S27"
ROLE="test-runner"
ROUND="2"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
TOOL="$REPO_ROOT/tools/souji-verify.sh"
OUT="$REPO_ROOT/tests/results/runner-27.json"
OUT_SET=0
FIXTURES_ONLY=0
KEEP=0
TOOL_TIMEOUT=240

while [ $# -gt 0 ]; do
  case "$1" in
    --fixtures-only) FIXTURES_ONLY=1 ;;
    --tool) TOOL="$2"; shift ;;
    --out) OUT="$2"; OUT_SET=1; shift ;;
    --keep) KEEP=1 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "usage: $0 [--fixtures-only] [--tool PATH] [--out PATH] [--keep]" >&2; exit 2 ;;
  esac
  shift
done

T="$(mktemp -d "${TMPDIR:-/tmp}/souji27.XXXXXX")"
if [ "$FIXTURES_ONLY" = 1 ] && [ "$OUT_SET" = 0 ]; then
  OUT="$T/runner-27.fixtures-only.json"
fi
cleanup() {
  if [ "$KEEP" = 1 ]; then echo "kept: $T" >&2; else rm -rf "$T"; fi
}
trap cleanup EXIT

RES="$T/cases.tsv"
: > "$RES"
ERRF="$T/stderr.txt"
META="$T/meta.tsv"
: > "$META"
EXECUTED_RCS="$T/rcs.txt"
: > "$EXECUTED_RCS"

log() { printf '%s\n' "$*" >&2; }

san() { printf '%s' "$1" | tr '\t\n' '  ' | cut -c1-600; }

record() { # id strict spec argv expected actual status evidence
  # status: "1" pass, "0" fail, "skip" not executed
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san "$1")" "$(san "$2")" "$(san "$3")" "$(san "$4")" \
    "$(san "$5")" "$(san "$6")" "$(san "$7")" "$(san "$8")" >> "$RES"
}

meta() { printf '%s\t%s\n' "$1" "$(san "$2")" >> "$META"; }

STRICT_FAILS=0
TOTAL=0
PASSED=0
SKIPPED=0

# ---------------------------------------------------------------- git helpers
export GIT_AUTHOR_NAME="souji runner" GIT_AUTHOR_EMAIL="souji@shokunin.local"
export GIT_COMMITTER_NAME="souji runner" GIT_COMMITTER_EMAIL="souji@shokunin.local"
export GIT_AUTHOR_DATE="2020-01-01T00:00:00+0000" GIT_COMMITTER_DATE="2020-01-01T00:00:00+0000"
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0

ginit() { git init -q -b "${2:-master}" "$1"; }

# commit_file <repo> <relpath> <content> <msg> [<parent>] -> prints commit sha
commit_file() {
  local repo="$1" rel="$2" content="$3" msg="$4" parent="${5:-}" blob tree commit
  blob="$(printf '%s' "$content" | git -C "$repo" hash-object -w --stdin)"
  git -C "$repo" update-index --add --cacheinfo "100644,$blob,$rel"
  tree="$(git -C "$repo" write-tree)"
  if [ -n "$parent" ]; then
    commit="$(git -C "$repo" commit-tree "$tree" -p "$parent" -m "$msg")"
  else
    commit="$(git -C "$repo" commit-tree "$tree" -m "$msg")"
  fi
  printf '%s\n' "$commit"
}

# materialize <repo> <relpath> <content> — write the worktree file so that
# index == HEAD == worktree (clean status) for committed content.
materialize() {
  local repo="$1" rel="$2" content="$3"
  mkdir -p "$(dirname "$repo/$rel")"
  printf '%s' "$content" > "$repo/$rel"
}

# mkreg <owner-repo> <reg-id> <wtpath> <head-value> <detached|ref>
# Hand-written worktree admin dir (what `git worktree add` writes):
#   .git/worktrees/<id>/{HEAD,gitdir,commondir}
mkreg() {
  local repo="$1" id="$2" wtpath="$3" headval="$4" mode="$5" adm
  adm="$repo/.git/worktrees/$id"
  mkdir -p "$adm"
  if [ "$mode" = ref ]; then
    printf 'ref: %s\n' "$headval" > "$adm/HEAD"
  else
    printf '%s\n' "$headval" > "$adm/HEAD"
  fi
  printf '%s\n' "$wtpath/.git" > "$adm/gitdir"
  printf '../..\n' > "$adm/commondir"
}

# ----------------------------------------------------------- fixture building
FIXROOT="$T/root"                       # stands in for $SHOKUNIN_ROOT
mkdir -p "$FIXROOT" "$T/vault"

# --- F1/kind-3 pushed file: push-shokunin
PUSH="$FIXROOT/push-shokunin"
ginit "$PUSH"
C1="$(commit_file "$PUSH" sub/a.txt 'alpha
' c1)"
materialize "$PUSH" sub/a.txt 'alpha
'
C2="$(commit_file "$PUSH" sub/b.txt 'beta
' c2 "$C1")"
materialize "$PUSH" sub/b.txt 'beta
'
git -C "$PUSH" update-ref refs/heads/master "$C2"
git -C "$PUSH" update-ref refs/remotes/origin/master "$C2"
git -C "$PUSH" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

# --- F2: local-only commit beside a pushed sibling
LOCAL="$FIXROOT/localonly-shokunin"
ginit "$LOCAL"
L1="$(commit_file "$LOCAL" kept.txt 'kept
' l1)"
materialize "$LOCAL" kept.txt 'kept
'
L2="$(commit_file "$LOCAL" local-only.txt 'local work
' l2 "$L1")"
materialize "$LOCAL" local-only.txt 'local work
'
git -C "$LOCAL" update-ref refs/heads/master "$L2"
git -C "$LOCAL" update-ref refs/remotes/origin/master "$L1"
git -C "$LOCAL" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master

# --- F3 kotodama-shaped repo-root: 1 unpushed commit + dirty tree
DIRTY="$FIXROOT/dirty-shokunin"
ginit "$DIRTY"
D1="$(commit_file "$DIRTY" tracked.txt 'v1
' d1)"
materialize "$DIRTY" tracked.txt 'v1
'
D2="$(commit_file "$DIRTY" extra.txt 'extra
' d2 "$D1")"
materialize "$DIRTY" extra.txt 'extra
'
git -C "$DIRTY" update-ref refs/heads/master "$D2"
git -C "$DIRTY" update-ref refs/remotes/origin/master "$D1"
git -C "$DIRTY" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
printf 'v2\n' > "$DIRTY/tracked.txt"          # modified (tracked)
printf 'scratch\n' > "$DIRTY/untracked.tmp"   # untracked

# --- F4/F5 worktree registrations, owner = owner-shokunin (scanned as *-shokunin)
OWNER="$FIXROOT/owner-shokunin"
ginit "$OWNER"
O1="$(commit_file "$OWNER" base.txt 'base
' o1)"
materialize "$OWNER" base.txt 'base
'
git -C "$OWNER" update-ref refs/heads/master "$O1"
git -C "$OWNER" update-ref refs/remotes/origin/master "$O1"
git -C "$OWNER" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
O_ALPHA="$(commit_file "$OWNER" alpha-only.txt 'alpha
' o-alpha "$O1")"
git -C "$OWNER" update-ref refs/heads/wt-alpha "$O_ALPHA"
materialize "$OWNER" alpha-only.txt 'alpha
' 2>/dev/null || true
WT_PRUNE="$FIXROOT/absent-wt-prune"
WT_BRANCH="$FIXROOT/absent-wt-branch"
WT_PRESENT="$FIXROOT/present-wt"
mkreg "$OWNER" absent-wt-prune "$WT_PRUNE" "$O1" detached
mkreg "$OWNER" absent-wt-branch "$WT_BRANCH" "refs/heads/wt-alpha" ref
mkreg "$OWNER" present-wt "$WT_PRESENT" "$O1" detached
mkdir -p "$WT_PRESENT"
printf 'gitdir: %s\n' "$OWNER/.git/worktrees/present-wt" > "$WT_PRESENT/.git"

# --- F7/F8 stale scratch files (outside any repo, plain tree)
# Names carry a per-run token so that no file outside the fixture (including
# this runner's own source, or a previous run's JSON in the lane repo) can be
# the "live reference" that keeps the stale receipt from firing — that would
# make the case self-polluting, the very D3 defect the tool must avoid.
STALE_DIR="$FIXROOT/stale-shokunin/out"
mkdir -p "$STALE_DIR"
RID="$(basename "$T" | tr -cd 'A-Za-z0-9')"
STALE7="$STALE_DIR/s27-$RID-stale7.out"
STALE8="$STALE_DIR/s27-$RID-stale8.out"
printf 'old scratch\n' > "$STALE7"
printf 'old scratch\n' > "$STALE8"
touch -d '2020-01-01T00:00:00Z' "$STALE7" "$STALE8"
FRESH="$STALE_DIR/s27-$RID-fresh.out"
printf 'fresh scratch\n' > "$FRESH"

# --- F8 polluter: census-like dir that names the stale basename (D3)
mkdir -p "$FIXROOT/souji-shokunin/census/round-2"
printf '{"ref":"%s"}\n' "$(basename "$STALE8")" > "$FIXROOT/souji-shokunin/census/round-2/seat-decoy.json"

# --- F9 single origin ref, no origin/HEAD, no local master
SINGLE="$FIXROOT/single-ref-shokunin"
ginit "$SINGLE" main
S1="$(commit_file "$SINGLE" pushed.txt 'pushed
' s1)"
materialize "$SINGLE" pushed.txt 'pushed
'
git -C "$SINGLE" update-ref refs/heads/main "$S1"
git -C "$SINGLE" update-ref refs/remotes/origin/trunk "$S1"

# --- F10 secrets refusal (files must exist; canary must never surface)
SECRET_DIR="$FIXROOT/secrets-shokunin"
mkdir -p "$SECRET_DIR"
CANARY="SOUJI27CANARY"
printf 'API_KEY=%s\n' "$CANARY" > "$SECRET_DIR/config.env"
printf '{"tok":"%s"}\n' "$CANARY" > "$SECRET_DIR/mycredential.json"
printf '%s\n' "$CANARY" > "$SECRET_DIR/id_rsa"
printf '%s\n' "$CANARY" > "$SECRET_DIR/cert.pem"

# --- F6 ledger match: source + vault copy, ledger row in both plausible spots.
# Three self-consistent rows cover the path conventions a ledger reader may
# use: absolute/absolute, root-relative/absolute, root-relative/root-relative.
VAULTED="$FIXROOT/vaulted.txt"
VAULT_COPY="$T/vault/vaulted.md"
printf 'preserved content\n' > "$VAULTED"
printf 'preserved content\n' > "$VAULT_COPY"
V_SRC_SHA="$(sha256sum "$VAULTED" | awk '{print $1}')"
V_DST_SHA="$(sha256sum "$VAULT_COPY" | awk '{print $1}')"
mkdir -p "$FIXROOT/corpus/knowledge" "$FIXROOT/souji-shokunin/corpus/knowledge"
LEDGER_ROW="$(printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n%s\t%s\t%s\t%s\t2020-01-01\tS27 fixture abs\nvaulted.txt\t%s\t%s\t%s\t2020-01-01\tS27 fixture src-rel\nvaulted.txt\t%s\t../vault/vaulted.md\t%s\t2020-01-01\tS27 fixture both-rel\n' \
  "$VAULTED" "$V_SRC_SHA" "$VAULT_COPY" "$V_DST_SHA" \
  "$V_SRC_SHA" "$VAULT_COPY" "$V_DST_SHA" \
  "$V_SRC_SHA" "$V_DST_SHA")"
printf '%s' "$LEDGER_ROW" > "$FIXROOT/corpus/knowledge/obsidian-ledger.tsv"
printf '%s' "$LEDGER_ROW" > "$FIXROOT/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv"

# --------------------------------------------------------- fixture self-checks
fv() { # id description expected_pass (run check via $CHECK_FN)
  local id="$1" desc="$2" ok="$3" ev="$4"
  local strict=1
  if [ "$ok" = "1" ]; then
    TOTAL=$((TOTAL+1)); PASSED=$((PASSED+1))
  else
    TOTAL=$((TOTAL+1)); STRICT_FAILS=$((STRICT_FAILS+1))
  fi
  record "$id" "$strict" "fixture validity (S27 self-check)" "read-only git check" "fixture in expected state" "$( [ "$ok" = 1 ] && echo ok || echo broken )" "$ok" "$ev"
}

FV1_OK=1
git -C "$PUSH" merge-base --is-ancestor "$C1" refs/remotes/origin/master || FV1_OK=0
[ -z "$(git -C "$PUSH" status --porcelain)" ] || FV1_OK=0
fv FV1 "push-shokunin: c1 ancestor of origin/master, clean tree" "$FV1_OK" \
  "intro=$(git -C "$PUSH" log --diff-filter=A --format=%H -1 -- sub/a.txt)"

UNP_LOCAL="$(git -C "$LOCAL" log --oneline master --not --remotes | wc -l)"
FV2_OK=1; [ "$UNP_LOCAL" = 1 ] || FV2_OK=0
fv FV2 "localonly-shokunin: exactly 1 unpushed commit on master" "$FV2_OK" "unpushed=$UNP_LOCAL"

UNP_DIRTY="$(git -C "$DIRTY" log --oneline master --not --remotes | wc -l)"
STATUS_DIRTY="$(git -C "$DIRTY" status --porcelain | wc -l)"
FV3_OK=1; [ "$UNP_DIRTY" = 1 ] && [ "$STATUS_DIRTY" -ge 2 ] || FV3_OK=0
fv FV3 "dirty-shokunin: 1 unpushed commit + dirty tree" "$FV3_OK" "unpushed=$UNP_DIRTY dirty=$STATUS_DIRTY"

WT_LIST="$(git -C "$OWNER" worktree list --porcelain)"
FV4_OK=1
printf '%s' "$WT_LIST" | grep -q "worktree $WT_PRUNE" || FV4_OK=0
printf '%s' "$WT_LIST" | grep -q 'prunable' || FV4_OK=0
UNIQ_O1="$(git -C "$OWNER" log --oneline "$O1" --not --all | wc -l)"
[ "$UNIQ_O1" = 0 ] || FV4_OK=0
fv FV4 "owner-shokunin: prune registration visible, dir absent, unique=0" "$FV4_OK" \
  "unique=$UNIQ_O1 reg=$(printf '%s' "$WT_LIST" | grep -c 'worktree ' )"

UNP_ALPHA="$(git -C "$OWNER" log --oneline wt-alpha --not --remotes | wc -l)"
FV5_OK=1; [ "$UNP_ALPHA" = 1 ] || FV5_OK=0
fv FV5 "owner-shokunin: named branch wt-alpha holds 1 unpushed commit" "$FV5_OK" "unpushed=$UNP_ALPHA"

FV6_OK=1
[ "$V_SRC_SHA" = "$(sha256sum "$VAULTED" | awk '{print $1}')" ] || FV6_OK=0
[ "$V_DST_SHA" = "$(sha256sum "$VAULT_COPY" | awk '{print $1}')" ] || FV6_OK=0
grep -q "$VAULTED" "$FIXROOT/corpus/knowledge/obsidian-ledger.tsv" || FV6_OK=0
fv FV6 "ledger fixture: row hashes match both sides" "$FV6_OK" "src=$V_SRC_SHA dst=$V_DST_SHA"

FV7_OK=1
[ "$(find "$STALE7" -mtime +1 | wc -l)" = 1 ] || FV7_OK=0
fv FV7 "stale fixture: mtime older than 1 day" "$FV7_OK" "mtime=$(date -r "$STALE7" +%F)"

FV9_OK=1
[ "$(git -C "$SINGLE" for-each-ref refs/remotes/ | wc -l)" = 1 ] || FV9_OK=0
[ -z "$(git -C "$SINGLE" symbolic-ref -q refs/remotes/origin/HEAD || true)" ] || FV9_OK=0
[ -z "$(git -C "$SINGLE" for-each-ref refs/heads/master | wc -l | grep -v '^0$' || true)" ] || FV9_OK=0
fv FV9 "single-ref fixture: exactly 1 origin ref, no origin/HEAD, no local master" "$FV9_OK" \
  "refs=$(git -C "$SINGLE" for-each-ref --format='%(refname)' refs/remotes/ | tr '\n' ' ')"

FV10_OK=1
for f in config.env mycredential.json id_rsa cert.pem; do [ -f "$SECRET_DIR/$f" ] || FV10_OK=0; done
fv FV10 "secrets fixture: all four secret-shaped files exist" "$FV10_OK" "dir=$SECRET_DIR"

# ------------------------------------------------------------- tool invocation
TOOL_PRESENT=0
TOOL_SHA="absent"
if [ -f "$TOOL" ]; then
  TOOL_PRESENT=1
  TOOL_SHA="$(sha256sum "$TOOL" | awk '{print $1}')"
fi

OUT_TXT=""
ERR_TXT=""
RC=0
EXTRA_ENV=()
ARGV=()

run_tool() {
  : > "$ERRF"
  set +e
  OUT_TXT="$(timeout "$TOOL_TIMEOUT" env "${EXTRA_ENV[@]}" bash "$TOOL" "${ARGV[@]}" 2>"$ERRF")"
  RC=$?
  set -e
  ERR_TXT="$(cat "$ERRF")"
  printf '%s\n' "$RC" >> "$EXECUTED_RCS"
}

verdict_line() { # <path> -> VERDICT line for that exact path
  printf '%s\n' "$OUT_TXT" | awk -F'\t' -v p="$1" '$1=="VERDICT" && $2==p {print; exit}'
}
fld() { printf '%s' "$1" | awk -F'\t' -v n="$2" '{print $n}'; }

emit_case() { # id strict spec argv expected actual pass evidence
  local id="$1" strict="$2" pass="$3"
  TOTAL=$((TOTAL+1))
  if [ "$pass" = 1 ]; then PASSED=$((PASSED+1)); else
    if [ "$strict" = 1 ]; then STRICT_FAILS=$((STRICT_FAILS+1)); fi
  fi
  record "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8"
}

skip_case() { # id strict spec reason
  SKIPPED=$((SKIPPED+1))
  record "$1" "$2" "$3" "(skipped)" "unspecified" "not run: $4" "skip" "$4"
}

# ------------------------------------------------------------- A: static audit
if [ "$FIXTURES_ONLY" = 0 ] && [ "$TOOL_PRESENT" = 1 ]; then

  # A1 syntax
  if bash -n "$TOOL" 2>"$T/a1.err"; then A1=1; else A1=0; fi
  emit_case A1 1 "spec: one bash tool" "bash -n $TOOL" "syntax ok" "$([ "$A1" = 1 ] && echo ok || echo syntax-error)" "$A1" "$(cat "$T/a1.err")"

  # A2 no prohibited git subcommands anywhere in the source (comments excluded:
  # a line whose text before the first `git` token contains `#` is not executed)
  A2RAW="$(grep -nE 'git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+(fetch|push|commit|branch|checkout|reset|rebase)([^[:alnum:]_-]|$)' "$TOOL" || true)"
  A2HITS="$(printf '%s\n' "$A2RAW" | while IFS= read -r l; do
    [ -n "$l" ] || continue
    body="${l#*:}"
    pre="${body%%git*}"
    case "$pre" in *'#'*) continue ;; esac
    printf '%s\n' "$l"
  done)"
  A2NOTREE="$(grep -nE 'commit-tree' "$TOOL" || true)"
  if [ -z "$A2HITS" ]; then A2=1; else A2=0; fi
  emit_case A2 1 "safety rails: never run git fetch/push/commit/branch/checkout/reset/rebase" "grep prohibited subcommands in $TOOL" "0 hits" "$(printf '%s' "$A2HITS" | wc -l) hit(s)" "$A2" "${A2HITS:-clean}${A2NOTREE:+ | plumbing commit-tree used: $(printf '%s' "$A2NOTREE" | wc -l)}"

  # A3 set -euo pipefail
  if grep -q 'set -euo pipefail' "$TOOL"; then A3=1; else A3=0; fi
  emit_case A3 1 "universal rule: set -euo pipefail" "grep 'set -euo pipefail'" "present" "$([ "$A3" = 1 ] && echo present || echo missing)" "$A3" ""

  # A4 operator-config surfaces untouched. Three kinds of mention are not writes:
  # comment-only lines; rg exclusion guards (`-g '!<path>'`); and case-filter
  # guards (`... | .ufo/state/*) continue ;;`). Only the remainder is a hit.
  A4RAW="$(grep -nE '\.ufo/state|watchdog\.log|/\.config/|~/\.config' "$TOOL" || true)"
  A4HITS="$(printf '%s\n' "$A4RAW" | while IFS= read -r l; do
    [ -n "$l" ] || continue
    body="${l#*:}"
    case "${body%%#*}" in "$body") ;; *) continue ;; esac
    case "$body" in *"-g "*) continue ;; esac
    case "$body" in *"continue ;;"*) continue ;; esac
    printf '%s\n' "$l"
  done)"
  A4GUARDS=$(( $(printf '%s\n' "$A4RAW" | grep -c . || true) - $(printf '%s\n' "$A4HITS" | grep -c . || true) ))
  if [ -z "$A4HITS" ]; then A4=1; else A4=0; fi
  emit_case A4 1 "safety rails: never touch .ufo/state, .ufo/watchdog.log, ~/.config" "grep forbidden path refs (comments, rg -g '!' guards and case filters excluded)" "0 remaining hits" "$(printf '%s' "$A4HITS" | grep -c . || true) hit(s)" "$A4" "hits=${A4HITS:-none} | guards_or_comments=$A4GUARDS"

  # A5 exec bit + shebang (advisory: bash pre-invocation is used regardless)
  A5=0; [ -x "$TOOL" ] && head -1 "$TOOL" | grep -q '^#!' && A5=1
  emit_case A5 0 "CLI contract nicety: executable + shebang" "test -x; head -1" "executable with shebang" "$([ "$A5" = 1 ] && echo yes || echo no)" "$A5" "mode=$(stat -c %A "$TOOL")"

  # ------------------------------------------------- C: behavioral fixtures
  ROOT_ENV_SUPPORT=0
  grep -q 'SHOKUNIN_ROOT' "$TOOL" && ROOT_ENV_SUPPORT=1
  LEDGER_ENV=""
  if grep -q 'SOUJI_LEDGER' "$TOOL"; then
    LEDGER_ENV="SOUJI_LEDGER=$FIXROOT/corpus/knowledge/obsidian-ledger.tsv"
  fi

  # C1: pushed file -> SAFE(pushed)
  EXTRA_ENV=("SHOKUNIN_ROOT=$FIXROOT"); ARGV=("$PUSH/sub/a.txt"); run_tool
  L="$(verdict_line "$PUSH/sub/a.txt")"
  C1OK=1
  [ "$RC" = 0 ] || C1OK=0
  [ "$(fld "$L" 3)" = "SAFE" ] || C1OK=0
  [ "$(fld "$L" 4)" = "pushed" ] || C1OK=0
  emit_case C1 1 "F1: introducing commit ancestor of default ref -> SAFE(pushed)" \
    "souji-verify.sh $PUSH/sub/a.txt" "SAFE<TAB>pushed" "rc=$RC ${L:-<no line>}" "$C1OK" "$L rc=$RC"

  # C1b: line format of that same run
  C1B=1
  [ -n "$L" ] || C1B=0
  [ "$(printf '%s\n' "$OUT_TXT" | grep -c $'^VERDICT\t')" = "$(printf '%s\n' "$OUT_TXT" | grep -cv '^$')" ] || C1B=0
  [ -z "$(printf '%s\n' "$OUT_TXT" | awk -F'\t' 'NF!=5 {print; exit}')" ] || C1B=0
  [ -z "$(printf '%s\n' "$OUT_TXT" | awk -F'\t' '$3!="SAFE" && $3!="NOT-SAFE" {print; exit}')" ] || C1B=0
  emit_case C1b 1 "CLI: VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence, one line per target" \
    "(format check on C1 output)" "all lines 5 fields, col1 VERDICT" "$(printf '%s' "$OUT_TXT" | head -3 | tr '\n' ';')" "$C1B" "$OUT_TXT"

  # C2a/C2b: local-only file NOT-SAFE, pushed sibling SAFE (same repo)
  ARGV=("$LOCAL/local-only.txt" "$LOCAL/kept.txt"); run_tool
  LA="$(verdict_line "$LOCAL/local-only.txt")"
  LB="$(verdict_line "$LOCAL/kept.txt")"
  C2A=1
  [ "$RC" = 0 ] || C2A=0
  [ "$(fld "$LA" 3)" = "NOT-SAFE" ] || C2A=0
  case "$(fld "$LA" 4)" in pushed-unverifiable|none) ;; *) C2A=0 ;; esac
  emit_case C2a 1 "F2: introducing commit local-only -> NOT-SAFE(pushed-unverifiable|none)" \
    "souji-verify.sh $LOCAL/local-only.txt" "NOT-SAFE<TAB>pushed-unverifiable|none" "${LA:-<no line>}" "$C2A" "$LA rc=$RC"
  C2B=1
  [ "$(fld "$LB" 3)" = "SAFE" ] && [ "$(fld "$LB" 4)" = "pushed" ] || C2B=0
  emit_case C2b 1 "paired control: pushed sibling in same repo -> SAFE(pushed)" \
    "souji-verify.sh $LOCAL/kept.txt" "SAFE<TAB>pushed" "${LB:-<no line>}" "$C2B" "$LB rc=$RC"

  # C3: repo-root kotodama-shaped -> NOT-SAFE with unpushed/dirty counts
  ARGV=("$DIRTY"); run_tool
  LD="$(verdict_line "$DIRTY")"
  RD="$(fld "$LD" 5)"
  C3OK=1
  [ "$RC" = 0 ] || C3OK=0
  [ "$(fld "$LD" 3)" = "NOT-SAFE" ] || C3OK=0
  printf '%s' "$RD" | grep -qE 'unpushed=[1-9]' || C3OK=0
  printf '%s' "$RD" | grep -qE 'dirty=[1-9]' || C3OK=0
  emit_case C3 1 "kind repo-root (kotodama-shaped): unpushed+dirty -> NOT-SAFE, evidence field carries unpushed=N dirty=M" \
    "souji-verify.sh $DIRTY" "NOT-SAFE with evidence unpushed>=1 dirty>=1" "${LD:-<no line>}" "$C3OK" "$LD rc=$RC"

  # C3b: repo-root clean+pushed -> still NOT-SAFE with unpushed=0 dirty=0
  ARGV=("$PUSH"); run_tool
  LP="$(verdict_line "$PUSH")"
  RP="$(fld "$LP" 5)"
  C3B=1
  [ "$(fld "$LP" 3)" = "NOT-SAFE" ] || C3B=0
  printf '%s' "$RP" | grep -qE 'unpushed=0' || C3B=0
  printf '%s' "$RP" | grep -qE 'dirty=0' || C3B=0
  emit_case C3b 1 "kind repo-root: SAFE only via moved-to-obsidian; clean+pushed root -> NOT-SAFE, evidence unpushed=0 dirty=0" \
    "souji-verify.sh $PUSH" "NOT-SAFE with evidence unpushed=0 dirty=0" "${LP:-<no line>}" "$C3B" "$LP rc=$RC"

  # C4: worktree registration, dir absent, unique=0 -> SAFE(metadata-prune)
  WT_STRICT="$ROOT_ENV_SUPPORT"
  ARGV=("$WT_PRUNE"); run_tool
  L4="$(verdict_line "$WT_PRUNE")"
  C4=1
  [ "$RC" = 0 ] || C4=0
  [ "$(fld "$L4" 3)" = "SAFE" ] || C4=0
  [ "$(fld "$L4" 4)" = "metadata-prune" ] || C4=0
  emit_case C4 "$WT_STRICT" "F4: worktree registration, dir absent, unique commits=0 -> SAFE(metadata-prune)" \
    "souji-verify.sh $WT_PRUNE (SHOKUNIN_ROOT=$FIXROOT)" "SAFE<TAB>metadata-prune" "${L4:-<no line>}" "$C4" "$L4 rc=$RC root_env=$ROOT_ENV_SUPPORT"

  # C5: named branch, 1 unpushed -> NOT-SAFE(unpushed-branch)
  ARGV=("$WT_BRANCH"); run_tool
  L5="$(verdict_line "$WT_BRANCH")"
  C5=1
  [ "$RC" = 0 ] || C5=0
  [ "$(fld "$L5" 3)" = "NOT-SAFE" ] || C5=0
  [ "$(fld "$L5" 4)" = "unpushed-branch" ] || C5=0
  emit_case C5 "$WT_STRICT" "F5: worktree named branch, 1 unpushed commit -> NOT-SAFE(unpushed-branch)" \
    "souji-verify.sh $WT_BRANCH (SHOKUNIN_ROOT=$FIXROOT)" "NOT-SAFE<TAB>unpushed-branch" "${L5:-<no line>}" "$C5" "$L5 rc=$RC"

  # C5b (advisory): dir present -> NOT-SAFE(dirty) [dirty by construction: index absent]
  ARGV=("$WT_PRESENT"); run_tool
  L5B="$(verdict_line "$WT_PRESENT")"
  C5B=1
  [ "$(fld "$L5B" 3)" = "NOT-SAFE" ] || C5B=0
  emit_case C5b 0 "kind worktree: dir present -> NOT-SAFE (advisory; registration lacks index so 'dirty' is synthetic)" \
    "souji-verify.sh $WT_PRESENT" "NOT-SAFE" "${L5B:-<no line>}" "$C5B" "$L5B rc=$RC"

  # C6: ledger match -> SAFE(moved-to-obsidian) [strict only if an override knob exists]
  if [ -n "$LEDGER_ENV" ]; then
    EXTRA_ENV=("SHOKUNIN_ROOT=$FIXROOT" "$LEDGER_ENV"); ARGV=("$VAULTED"); run_tool
    C6S=1
  else
    EXTRA_ENV=("SHOKUNIN_ROOT=$FIXROOT"); ARGV=("$VAULTED"); run_tool
    C6S=0
  fi
  L6="$(verdict_line "$VAULTED")"
  C6=1
  [ "$RC" = 0 ] || C6=0
  [ "$(fld "$L6" 3)" = "SAFE" ] || C6=0
  [ "$(fld "$L6" 4)" = "moved-to-obsidian" ] || C6=0
  emit_case C6 "$C6S" "F6: ledger row + matching sha256 both sides -> SAFE(moved-to-obsidian)" \
    "souji-verify.sh $VAULTED ${LEDGER_ENV:-<no ledger override found>}" "SAFE<TAB>moved-to-obsidian" "${L6:-<no line>}" "$C6" "$L6 rc=$RC ledger_override=${LEDGER_ENV:-none}"

  # C7: stale scratch, old mtime, no refs -> SAFE(stale)
  EXTRA_ENV=("SHOKUNIN_ROOT=$FIXROOT"); ARGV=("$STALE7"); run_tool
  L7="$(verdict_line "$STALE7")"
  C7=1
  [ "$RC" = 0 ] || C7=0
  [ "$(fld "$L7" 3)" = "SAFE" ] || C7=0
  [ "$(fld "$L7" 4)" = "stale" ] || C7=0
  emit_case C7 1 "F7: scratch type + zero live refs + old mtime -> SAFE(stale)" \
    "souji-verify.sh $STALE7" "SAFE<TAB>stale" "${L7:-<no line>}" "$C7" "$L7 rc=$RC"

  # C8: same, but a census-like dir names the basename -> still SAFE(stale) (D3)
  ARGV=("$STALE8"); run_tool
  L8="$(verdict_line "$STALE8")"
  C8=1
  [ "$RC" = 0 ] || C8=0
  [ "$(fld "$L8" 3)" = "SAFE" ] || C8=0
  [ "$(fld "$L8" 4)" = "stale" ] || C8=0
  emit_case C8 1 "F8/D3: reference sweep must exclude souji-shokunin/census/** -> still SAFE(stale)" \
    "souji-verify.sh $STALE8 (decoy names its basename)" "SAFE<TAB>stale" "${L8:-<no line>}" "$C8" "$L8 rc=$RC"

  # C9: D1 fallback — no origin/HEAD, single origin ref
  ARGV=("$SINGLE/pushed.txt"); run_tool
  L9="$(verdict_line "$SINGLE/pushed.txt")"
  C9=1
  [ "$RC" = 0 ] || C9=0
  [ "$(fld "$L9" 3)" = "SAFE" ] || C9=0
  [ "$(fld "$L9" 4)" = "pushed" ] || C9=0
  emit_case C9 1 "F9/D1: origin/HEAD missing, single origin ref -> resolved, SAFE(pushed)" \
    "souji-verify.sh $SINGLE/pushed.txt" "SAFE<TAB>pushed" "${L9:-<no line>}" "$C9" "$L9 rc=$RC"

  # C10: secrets refusal + canary must not surface
  ARGV=("$SECRET_DIR/config.env"); run_tool
  L10="$(verdict_line "$SECRET_DIR/config.env")"
  C10=1
  [ "$RC" = 0 ] || C10=0
  [ "$(fld "$L10" 3)" = "NOT-SAFE" ] || C10=0
  [ "$(fld "$L10" 4)" = "secrets-refusal" ] || C10=0
  printf '%s' "$OUT_TXT$ERR_TXT" | grep -q "$CANARY" && C10=0
  emit_case C10 1 "F10: *.env -> NOT-SAFE(secrets-refusal), content never read/echoed" \
    "souji-verify.sh $SECRET_DIR/config.env" "NOT-SAFE<TAB>secrets-refusal, canary absent" "${L10:-<no line>}" "$C10" "$L10 rc=$RC canary_absent=$(printf '%s' "$OUT_TXT$ERR_TXT" | grep -q "$CANARY" && echo no || echo yes)"

  # C10b: other secret shapes in one run
  ARGV=("$SECRET_DIR/mycredential.json" "$SECRET_DIR/id_rsa" "$SECRET_DIR/cert.pem"); run_tool
  C10B=1
  [ "$RC" = 0 ] || C10B=0
  for p in mycredential.json id_rsa cert.pem; do
    l="$(verdict_line "$SECRET_DIR/$p")"
    [ "$(fld "$l" 3)" = "NOT-SAFE" ] && [ "$(fld "$l" 4)" = "secrets-refusal" ] || C10B=0
  done
  printf '%s' "$OUT_TXT$ERR_TXT" | grep -q "$CANARY" && C10B=0
  emit_case C10b 1 "F10: *credential*, id_*, *.pem -> NOT-SAFE(secrets-refusal)" \
    "souji-verify.sh $SECRET_DIR/{mycredential.json,id_rsa,cert.pem}" "3x NOT-SAFE<TAB>secrets-refusal" "$(printf '%s' "$OUT_TXT" | tr '\n' ';')" "$C10B" "$OUT_TXT rc=$RC"

  # C11: missing target -> NOT-SAFE(unreachable), exit stays 0
  MISSING="$FIXROOT/does-not-exist-s27"
  ARGV=("$MISSING"); run_tool
  L11="$(verdict_line "$MISSING")"
  C11=1
  [ "$RC" = 0 ] || C11=0
  [ "$(fld "$L11" 3)" = "NOT-SAFE" ] || C11=0
  [ "$(fld "$L11" 4)" = "unreachable" ] || C11=0
  emit_case C11 1 "rails: empty/missing target -> NOT-SAFE(unreachable), exit 0" \
    "souji-verify.sh $MISSING" "NOT-SAFE<TAB>unreachable rc=0" "${L11:-<no line>}" "$C11" "$L11 rc=$RC"

  # C12: determinism — identical bytes across two runs of the same batch
  ARGV=("$DIRTY" "$PUSH/sub/a.txt" "$STALE7"); run_tool; FIRST="$OUT_TXT"; FIRST_RC=$RC
  ARGV=("$DIRTY" "$PUSH/sub/a.txt" "$STALE7"); run_tool; SECOND="$OUT_TXT"; SECOND_RC=$RC
  C12=1
  [ "$FIRST" = "$SECOND" ] && [ "$FIRST_RC" = "$SECOND_RC" ] || C12=0
  emit_case C12 1 "determinism: repeated identical invocation -> identical stdout+rc" \
    "souji-verify.sh $DIRTY $PUSH/sub/a.txt $STALE7 (x2)" "identical output" "rc=$FIRST_RC/$SECOND_RC bytes=$(printf '%s' "$FIRST" | wc -c)/$(printf '%s' "$SECOND" | wc -c)" "$C12" "$( [ "$FIRST" = "$SECOND" ] && echo identical || echo DIFFER )"

  # C13: --selftest exit 0, twice; live tree untouched
  # (digest the tested tool file itself: concurrent seats may add files under
  # tools/, which is not a violation by the tool under test)
  TOOLS_DIGEST_BEFORE="$(sha256sum "$TOOL" | awk '{print $1}')"
  LS_BEFORE="$(ls -A "$REPO_ROOT/tools" | sort | tr '\n' ' ')"
  TOP_BEFORE="$(ls -A "$REPO_ROOT" | sort | tr '\n' ' ')"
  STATUS_BEFORE="$(git -C "$REPO_ROOT" status --porcelain | sort)"
  EXTRA_ENV=(); ARGV=(--selftest); run_tool; S1_RC=$RC; S1_ERR="$ERR_TXT"
  ARGV=(--selftest); run_tool; S2_RC=$RC
  C13=1
  [ "$S1_RC" = 0 ] && [ "$S2_RC" = 0 ] || C13=0
  TOOLS_DIGEST_AFTER="$(sha256sum "$TOOL" | awk '{print $1}')"
  LS_AFTER="$(ls -A "$REPO_ROOT/tools" | sort | tr '\n' ' ')"
  TOP_AFTER="$(ls -A "$REPO_ROOT" | sort | tr '\n' ' ')"
  STATUS_AFTER="$(git -C "$REPO_ROOT" status --porcelain | sort)"
  [ "$TOOLS_DIGEST_BEFORE" = "$TOOLS_DIGEST_AFTER" ] || C13=0
  emit_case C13 1 "CLI: --selftest exit 0 (F1-F10 covered by the tool), twice, live tree untouched" \
    "souji-verify.sh --selftest (x2)" "rc=0/rc=0, tool sha256 unchanged" "rc=$S1_RC/$S2_RC tool_sha=$([ "$TOOLS_DIGEST_BEFORE" = "$TOOLS_DIGEST_AFTER" ] && echo unchanged || echo CHANGED)" "$C13" "${S1_ERR:-} tools_dir=$([ "$LS_BEFORE" = "$LS_AFTER" ] && echo stable || echo CHANGED) top=$([ "$TOP_BEFORE" = "$TOP_AFTER" ] && echo stable || echo CHANGED)"

  # C14: --json parses
  ARGV=(--json "$PUSH/sub/a.txt"); run_tool
  C14=1
  [ "$RC" = 0 ] || C14=0
  if ! printf '%s' "$OUT_TXT" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>"$T/c14.err"; then C14=0; fi
  printf '%s' "$OUT_TXT" | grep -q "$PUSH/sub/a.txt" || C14=0
  emit_case C14 1 "CLI: --json emits parseable JSON naming the target" \
    "souji-verify.sh --json $PUSH/sub/a.txt" "valid JSON, path present" "$(printf '%s' "$OUT_TXT" | head -c 200)" "$C14" "$(cat "$T/c14.err") rc=$RC"

  # C15: stale threshold direction
  ARGV=(--stale-days 100 "$STALE7"); run_tool
  L15A="$(verdict_line "$STALE7")"
  C15A=1
  [ "$(fld "$L15A" 3)" = "SAFE" ] && [ "$(fld "$L15A" 4)" = "stale" ] || C15A=0
  emit_case C15a 1 "--stale-days 100 on 2020 file -> SAFE(stale)" "--stale-days 100 $STALE7" "SAFE<TAB>stale" "${L15A:-<no line>}" "$C15A" "$L15A"
  ARGV=(--stale-days 3650 "$STALE7"); run_tool
  L15B="$(verdict_line "$STALE7")"
  C15B=1
  [ "$(fld "$L15B" 3)" = "NOT-SAFE" ] || C15B=0
  emit_case C15b 1 "--stale-days 3650 on 2020 file -> NOT-SAFE (threshold honored)" "--stale-days 3650 $STALE7" "NOT-SAFE" "${L15B:-<no line>}" "$C15B" "$L15B"
  ARGV=("$FRESH"); run_tool
  L15C="$(verdict_line "$FRESH")"
  C15C=1
  [ "$(fld "$L15C" 3)" = "NOT-SAFE" ] || C15C=0
  emit_case C15c 1 "fresh scratch file under default --stale-days 1 -> NOT-SAFE" "souji-verify.sh $FRESH" "NOT-SAFE" "${L15C:-<no line>}" "$C15C" "$L15C"

  # C16: no-argument invocation -> usage, exit 2 (spec: exit 2 = usage)
  EXTRA_ENV=(); ARGV=(); run_tool
  C16=1
  [ "$RC" = 2 ] || C16=0
  emit_case C16 1 "CLI: exit codes only 0/1/2; no args = usage -> 2" "souji-verify.sh" "rc=2" "rc=$RC out=$(printf '%s' "$OUT_TXT" | head -c 120)" "$C16" "$OUT_TXT$ERR_TXT"

  # C16b (advisory): empty-string target -> NOT-SAFE(unreachable), exit 0
  ARGV=(""); run_tool
  C16B=1
  [ "$RC" = 0 ] || C16B=0
  emit_case C16b 0 "rails: empty-string target -> NOT-SAFE(unreachable), exit 0 (advisory reading)" \
    "souji-verify.sh ''" "rc=0" "rc=$RC out=$(printf '%s' "$OUT_TXT" | head -c 120)" "$C16B" "$OUT_TXT$ERR_TXT"

  # C17: rc contract across all executed invocations
  BAD_RCS="$(sort -u "$EXECUTED_RCS" | grep -vE '^(0|1|2)$' || true)"
  C17=1
  [ -z "$BAD_RCS" ] || C17=0
  emit_case C17 1 "CLI: no exit code outside {0,1,2}" "collect every invocation rc" "subset of 0/1/2" "rcs=$(sort -u "$EXECUTED_RCS" | tr '\n' ' ')" "$C17" "${BAD_RCS:-clean}"

else
  for st in A1 A2 A3 A4 A5 C1 C1b C2a C2b C3 C3b C4 C5 C5b C6 C7 C8 C9 C10 C10b C11 C12 C13 C14 C15a C15b C15c C16 C16b C17; do
    skip_case "$st" 1 "tool cases" "tools/souji-verify.sh absent (or --fixtures-only)"
  done
fi

# ------------------------------------------------------------------- JSON emit
meta seat "$SEAT"
meta role "$ROLE"
meta round "$ROUND"
meta tool_path "$TOOL"
meta tool_present "$TOOL_PRESENT"
meta tool_sha256 "$TOOL_SHA"
meta lane_repo_head "$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
meta generated_at "$(date -u +%FT%TZ)"
meta rg_version "$(rg --version 2>/dev/null | head -1)"
meta fixtures_only "$FIXTURES_ONLY"
meta rg_basename_supported "$(rg -l --no-ignore --basename probe /tmp 2>/dev/null >/dev/null && echo yes || echo no)"
meta strict_failures "$STRICT_FAILS"
meta totals "$TOTAL"
meta passed "$PASSED"
meta skipped "$SKIPPED"

if [ "$FIXTURES_ONLY" = 0 ]; then
  mkdir -p "$(dirname "$OUT")"
fi

python3 - "$RES" "$META" "$OUT" <<'PY'
import json, os, sys
cases_path, meta_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
meta = {}
for line in open(meta_path):
    line = line.rstrip("\n")
    if "\t" in line:
        k, v = line.split("\t", 1)
        meta[k] = v
cases = []
for line in open(cases_path):
    line = line.rstrip("\n")
    if not line:
        continue
    f = line.split("\t")
    while len(f) < 8:
        f.append("")
    cases.append({
        "id": f[0], "strict": f[1] == "1", "spec": f[2], "argv": f[3],
        "expected": f[4], "actual": f[5], "pass": f[6] == "1",
        "skipped": f[6] == "skip", "evidence": f[7],
    })
cases.sort(key=lambda c: c["id"])
strict_fail = [c["id"] for c in cases if c["strict"] and not c["pass"] and not c["skipped"]]
if meta.get("fixtures_only") == "1":
    verdict = "FIXTURES-ONLY"
elif meta.get("tool_present") != "1":
    verdict = "BLOCKED"
elif strict_fail:
    verdict = "FAIL"
elif cases and all(c["pass"] for c in cases):
    verdict = "PASS"
else:
    verdict = "PASS-ADVISORY-FAILS" if cases else "FAIL"
doc = {
    "seat": meta.get("seat"), "role": meta.get("role"), "round": meta.get("round"),
    "tool": {
        "path": os.path.relpath(meta.get("tool_path", ""), os.path.dirname(os.path.dirname(os.path.dirname(out_path)))) if out_path else meta.get("tool_path"),
        "present": meta.get("tool_present") == "1",
        "sha256": meta.get("tool_sha256"),
    },
    "lane_repo_head": meta.get("lane_repo_head"),
    "generated_at": meta.get("generated_at"),
    "verdict": verdict,
    "totals": {
        "cases": len(cases),
        "passed": sum(1 for c in cases if c["pass"]),
        "failed": sum(1 for c in cases if not c["pass"] and not c["skipped"]),
        "strict_failures": len(strict_fail),
        "skipped": sum(1 for c in cases if c["skipped"]),
    },
    "strict_failures": strict_fail,
    "environment": {
        "rg_version": meta.get("rg_version"),
        "rg_basename_supported": meta.get("rg_basename_supported") == "yes",
        "note": "spec's D3 sweep command uses rg --basename, which this host's rg rejects (rc=2); F8 here asserts the behaviour (census-like dir must not poison the stale receipt), not the literal command.",
    },
    "cases": cases,
}
with open(out_path, "w") as fh:
    json.dump(doc, fh, indent=2, sort_keys=False)
    fh.write("\n")
print(f"runner-27: verdict={verdict} cases={len(cases)} strict_failures={len(strict_fail)} -> {out_path}")
for cid in strict_fail:
    print(f"  strict fail: {cid}")
PY

[ "$STRICT_FAILS" = 0 ] || exit 1
[ "$FIXTURES_ONLY" = 1 ] || [ "$TOOL_PRESENT" = 1 ] || exit 1
exit 0
