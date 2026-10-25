#!/usr/bin/env bash
# souji-quarantine — fail-closed quarantine ticket runner (round 8, seat S03).
#
# Implements the 5-step flow pre-staged in census/round-7/quarantine-plan.json
# (execution_plan_template): gate recheck -> stage -> hold -> second check ->
# operator-gated retire. Authorization rule is verbatim round-7:
#   gate1  git -C <repo> log --branches --not --remotes --oneline -- <path>
#          must print NOTHING (no local-only commit touches the path).
#   gate2  git -C <repo> status --porcelain=v1 --untracked-files=all -- <path>
#          must print NOTHING (untracked counts as dirty; ignored files do
#          not appear without --ignored, so ignored-clean is the only
#          untracked shape that can pass — durability caveat r7: an unpushed
#          .gitignore edit makes ignore-status non-durable).
#   gate3  BOTH receipt engines agree: tools/souji-verify.sh --json -> SAFE
#          AND tools/souji-vault-verify.sh --json -> SAFE with the SAME
#          receipt class, equal to --expect-receipt when given.
# AUTHORIZED requires all three; anything else is NOT-AUTHORIZED (fail-closed).
#
# CLI
#   tools/souji-quarantine.impl-03.sh --check [--json] [--expect-receipt CLASS] <path>...
#   tools/souji-quarantine.impl-03.sh --plan <path>          # runbook, no mutation
#   tools/souji-quarantine.impl-03.sh --stage [--dry-run] <path>
#   tools/souji-quarantine.impl-03.sh --verify-staged <original-path>
#   tools/souji-quarantine.impl-03.sh --retire --operator-signoff ID <staged-path>
#   tools/souji-quarantine.impl-03.sh --selftest
#
# Modes --check/--plan/--verify-staged are strictly READ-ONLY.
# Modes --stage/--retire MUTATE, but only inside the sandbox: the canonical
# target must lie under $SOUJI_Q_SANDBOX. In production that variable is left
# unset and every mutation request is REFUSED before any filesystem effect —
# the live fleet is never touchable through this tool. The selftest is the
# only component that sets it, to its own `mktemp -d` root.
#
# Staging layout: <repo>/.ufo-quarantine/<YYYY-MM-DD>/<rel with / -> __>
# plus a sidecar record <dest>.souji-qrecord.json (original path, receipt at
# stage time, sha256 manifest digest) that --verify-staged and --retire
# re-verify; a digest mismatch or a still-present original holds the ticket.
# --retire additionally requires an explicit --operator-signoff string
# (AGENTS.md: hold period + second receipt check + operator sign-off) and
# removes ONLY the staged copy and its record.
#
# Pitfall carried from r6 (recorded in LOG.md): bare `git log --not
# --remotes` silently returns NOTHING on git 2.55 when refs/remotes is
# empty. gate1 therefore always uses the explicit `--branches --not
# --remotes` form; the selftest proves the explicit form still fails closed
# in a zero-remote repo where the bare form returns empty.
#
# Safety rails
#   * Secret-shaped path components (*.env, .env.*, .envrc, *credential*,
#     *secret*, id_*, *.pem) are refused before anything is read.
#   * No git fetch/push/commit/branch/checkout/reset/rebase/mv/rm is ever
#     executed; the only index-free mutation is plain mv/rm under the sandbox.
#   * Fixtures live under `mktemp -d` only; .ufo/state, .ufo/watchdog.log and
#     ~/.config are never touched; the lane repo is never mutated.
#   * Exit codes: check/verify-staged/plan always 0 (verdict is data, not an
#     error); stage/retire 0 = performed, 1 = REFUSED, 2 = usage error;
#     selftest 0 = all green, 1 = any failure.
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
TOOL_A="$REPO_ROOT/tools/souji-verify.sh"
TOOL_B="$REPO_ROOT/tools/souji-vault-verify.sh"

MODE=""                 # check | plan | stage | verify-staged | retire
JSON=0
DRY_RUN=0
EXPECT_RECEIPT=""
SIGNOFF=""
TARGETS=()

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

usage() { # $1 = exit code
  sed -n '2,44p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "$1"
}

usage_err() { printf 'souji-quarantine: %s\n' "$1" >&2; usage 2; }

# True when any path component is secret-shaped (case-insensitive).
is_secret_shaped() {
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    lc=${comp,,}
    case "$lc" in
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem)
        set +f; return 0 ;;
    esac
  done
  set +f
  return 1
}

# Nearest enclosing git repo of a path.
find_repo_for() {
  local p=$1 d top
  if [ -d "$p" ]; then d=$p; else d=$(dirname -- "$p"); fi
  d=$(canon_path "$d")
  if top=$(git -C "$d" rev-parse --show-toplevel 2>/dev/null) && [ -n "$top" ]; then
    printf '%s\n' "$top"; return 0
  fi
  while :; do
    [ -e "$d/.git" ] && { printf '%s\n' "$d"; return 0; }
    [ "$d" = "/" ] && break
    d=$(dirname -- "$d")
  done
  return 1
}

file_sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

# Deterministic manifest digest of a file or directory (dirs: files only,
# any symlink fails closed with exit 2 — same rule as souji-verify r5 fix).
tree_digest() {
  local p=$1
  if [ -f "$p" ] && [ ! -L "$p" ]; then file_sha "$p"; return 0; fi
  if [ -d "$p" ]; then
    if ( cd "$p" && find . -path './.git' -prune -o -type l -print -quit 2>/dev/null | grep -q . ); then
      return 2
    fi
    ( cd "$p" && find . -path './.git' -prune -o -type f -print0 \
        | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 )
    return 0
  fi
  return 1
}

flat_rel() { # $1 rel path -> quarantine flat name
  local r=$1
  r=${r//\//__}
  printf '%s\n' "$r"
}

qdate() { date +%F; }

qpaths() { # $1 repo, $2 rel -> prints dest<TAB>record
  local d="$1/.ufo-quarantine/$(qdate)/$(flat_rel "$2")"
  printf '%s\t%s\n' "$d" "$d.souji-qrecord.json"
}

sandbox_allows() { # $1 canonical target -> 0 when mutation permitted
  local sb=${SOUJI_Q_SANDBOX:-}
  [ -n "$sb" ] || return 1
  sb=$(canon_path "$sb")
  case "$1" in
    "$sb"/*) return 0 ;;
    *) return 1 ;;
  esac
}

# Run one receipt engine with --json; prints "verdict receipt evidence".
run_receipt_tool() { # $1 tool path, $2 target
  local tool=$1 target=$2 out v r e
  out=$(bash "$tool" --json "$target" 2>/dev/null || true)
  v=$(printf '%s\n' "$out" | grep -o '"verdict":"[^"]*"' | head -1 | cut -d'"' -f4 || true)
  r=$(printf '%s\n' "$out" | grep -o '"receipt":"[^"]*"' | head -1 | cut -d'"' -f4 || true)
  e=$(printf '%s\n' "$out" | grep -o '"evidence":"[^"]*"' | head -1 | cut -d'"' -f4 || true)
  printf '%s\t%s\t%s\n' "${v:-unreadable}" "${r:-none}" "${e:-tool-unreadable}"
}

G1_LINES=0 G2_LINES=0
G1_STATE=pass G2_STATE=pass
RA_V=unreadable RA_R=none RA_E=tool-unreadable
RB_V=unreadable RB_R=none RB_E=tool-unreadable
G3_STATE=pass G3_REASON=""
VERDICT=NOT-AUTHORIZED
Q_RECEIPT=none
Q_EVIDENCE=""

emit_json() { # $1 raw path
  printf '{"path":"%s","verdict":"%s","receipt":"%s","gate1":"%s","gate1_lines":%s,"gate2":"%s","gate2_lines":%s,"gate3":"%s","receiptA":"%s","receiptB":"%s","evidence":"%s"}\n' \
    "$(json_escape "$1")" "$VERDICT" "$Q_RECEIPT" \
    "$G1_STATE" "$G1_LINES" "$G2_STATE" "$G2_LINES" \
    "$G3_STATE${G3_REASON:+:$G3_REASON}" \
    "$RA_V($RA_R)" "$RB_V($RB_R)" "$(json_escape "$Q_EVIDENCE")"
}

emit_text() { # $1 raw path
  printf 'QUARANTINE\t%s\t%s\t%s\tgate1=%s(%s)\tgate2=%s(%s)\tgate3=%s%s\tA=%s(%s)\tB=%s(%s)\n' \
    "$1" "$VERDICT" "$Q_RECEIPT" \
    "$G1_STATE" "$G1_LINES" "$G2_STATE" "$G2_LINES" \
    "$G3_STATE" "${G3_REASON:+:$G3_REASON}" \
    "$RA_V" "$RA_R" "$RB_V" "$RB_R"
  [ -z "$Q_EVIDENCE" ] || printf '  evidence: %s\n' "$Q_EVIDENCE"
}

# step_0_recheck — the round-7 authorization rule, verbatim.
check_path() { # $1 raw target
  local raw=$1 target repo rel
  G1_LINES=0 G2_LINES=0 G1_STATE=pass G2_STATE=pass
  G3_STATE=pass G3_REASON=""
  VERDICT=NOT-AUTHORIZED Q_RECEIPT=none Q_EVIDENCE=""
  RA_V=unreadable RA_R=none RA_E=tool-unreadable
  RB_V=unreadable RB_R=none RB_E=tool-unreadable

  target=$(canon_path "$raw")
  if is_secret_shaped "$target"; then
    Q_EVIDENCE="secrets-refusal: secret-shaped path component (refused before any read)"
    return 0
  fi
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    Q_EVIDENCE="unreachable: missing path"
    return 0
  fi
  repo=$(find_repo_for "$target") || { Q_EVIDENCE="unreachable: no enclosing git repo"; return 0; }
  case "$target" in "$repo"/*) rel=${target#"$repo"/} ;; *) rel=$target ;; esac
  case "$rel" in
    .ufo-quarantine/*) Q_EVIDENCE="refused: path already under .ufo-quarantine"; return 0 ;;
  esac

  # gate1: explicit --branches --not --remotes (bare --not --remotes is
  # silently empty on git 2.55 with zero remote-tracking refs — r6 pitfall).
  G1_LINES=$(git -C "$repo" log --branches --not --remotes --oneline -- "$rel" 2>/dev/null | wc -l || true)
  G1_LINES=${G1_LINES// /}
  [ "$G1_LINES" = 0 ] && G1_STATE=pass || G1_STATE=fail

  # gate2: porcelain incl. untracked; ignored files do not appear.
  G2_LINES=$(git -C "$repo" status --porcelain=v1 --untracked-files=all -- "$rel" 2>/dev/null | wc -l || true)
  G2_LINES=${G2_LINES// /}
  [ "$G2_LINES" = 0 ] && G2_STATE=pass || G2_STATE=fail

  # gate3: both engines, same receipt, equal to expectation.
  local a b
  a=$(run_receipt_tool "$TOOL_A" "$target"); IFS=$'\t' read -r RA_V RA_R RA_E <<< "$a"
  b=$(run_receipt_tool "$TOOL_B" "$target"); IFS=$'\t' read -r RB_V RB_R RB_E <<< "$b"
  if [ "$RA_V" != SAFE ] || [ "$RB_V" != SAFE ]; then
    G3_STATE=fail; G3_REASON="no-safe-receipt"
  elif [ "$RA_R" != "$RB_R" ]; then
    G3_STATE=fail; G3_REASON="tool-disagreement($RA_R vs $RB_R)"
  elif [ -n "$EXPECT_RECEIPT" ] && [ "$RA_R" != "$EXPECT_RECEIPT" ]; then
    G3_STATE=fail; G3_REASON="receipt-mismatch(ticket=$EXPECT_RECEIPT tree=$RA_R)"
  else
    Q_RECEIPT=$RA_R
  fi

  local -a fails=()
  [ "$G1_STATE" = pass ] || fails+=("gate1=unpushed-touching($G1_LINES)")
  [ "$G2_STATE" = pass ] || fails+=("gate2=dirty-touching($G2_LINES)")
  [ "$G3_STATE" = pass ] || fails+=("gate3=$G3_REASON")
  if [ "${#fails[@]}" -eq 0 ]; then
    VERDICT=AUTHORIZED
    Q_EVIDENCE="all gates pass; receipt=$Q_RECEIPT A[$RA_E] B[$RB_E]"
  else
    Q_EVIDENCE="$(printf '%s; ' "${fails[@]}")"
    Q_EVIDENCE=${Q_EVIDENCE%; }
    Q_EVIDENCE="$Q_EVIDENCE; A=$RA_V($RA_R)[$RA_E] B=$RB_V($RB_R)[$RB_E]"
  fi
  return 0
}

print_plan() { # $1 raw target — runbook with substituted paths, no mutation
  local raw=$1 target repo rel dest rec
  target=$(canon_path "$raw")
  repo=$(find_repo_for "$target" 2>/dev/null || true)
  if [ -z "$repo" ]; then
    printf 'PLAN\t%s\tUNREACHABLE no-enclosing-repo\n' "$raw"
    return 0
  fi
  case "$target" in "$repo"/*) rel=${target#"$repo"/} ;; *) rel=$target ;; esac
  IFS=$'\t' read -r dest rec <<< "$(qpaths "$repo" "$rel")"
  cat <<EOF
PLAN $rel (repo $repo)
  step_0_recheck : $SELF --check --expect-receipt <CLASS> $target
  step_1_stage   : $SELF --stage $target
                   (mv $target $dest; sandbox-only: SOUJI_Q_SANDBOX must cover the repo)
  step_2_hold    : hold window = current round; nothing commits, nothing deletes
  step_3_2ndchk  : $SELF --verify-staged $target
  step_4_retire  : $SELF --retire --operator-signoff <OPERATOR-ID> $dest
                   (rm of the staged copy + record ONLY, after operator sign-off)
  fail-closed    : any gate fail, tool disagreement, digest drift, present
                   original, or missing signoff => NOT-AUTHORIZED / REFUSED
EOF
}

# step_1_stage — sandbox-guarded plain mv + sidecar record.
stage_path() { # $1 raw target
  local raw=$1 target repo rel dest rec dg rc
  target=$(canon_path "$raw")
  if ! sandbox_allows "$target"; then
    printf 'REFUSED\toutside-sandbox\t%s\n' "$target" >&2
    printf 'souji-quarantine: mutation refused: SOUJI_Q_SANDBOX unset or does not cover %s\n' "$target" >&2
    return 1
  fi
  if is_secret_shaped "$target"; then
    printf 'REFUSED\tsecrets-refusal\t%s\n' "$target" >&2; return 1
  fi
  if [ -e "$target" ] && [ "$target" = "$(canon_path "$target")" ] \
     && case "$target" in *.souji-qrecord.json) true ;; *) false ;; esac; then
    printf 'REFUSED\trecord-path\t%s\n' "$target" >&2; return 1
  fi
  repo=$(find_repo_for "$target") || { printf 'REFUSED\tno-repo\t%s\n' "$target" >&2; return 1; }
  case "$target" in "$repo"/*) rel=${target#"$repo"/} ;; *) rel=$target ;; esac
  case "$rel" in .ufo-quarantine/*)
    printf 'REFUSED\talready-quarantined\t%s\n' "$target" >&2; return 1 ;;
  esac
  IFS=$'\t' read -r dest rec <<< "$(qpaths "$repo" "$rel")"
  if [ -e "$dest" ] || [ -e "$rec" ]; then
    printf 'REFUSED\tdest-exists\t%s\n' "$dest" >&2; return 1
  fi
  check_path "$target"
  if [ "$VERDICT" != AUTHORIZED ]; then
    printf 'REFUSED\tnot-authorized\t%s\t%s\n' "$target" "$Q_EVIDENCE" >&2
    return 1
  fi
  if [ "$DRY_RUN" = 1 ]; then
    printf 'DRY-RUN\tmv\t%s\t%s\n' "$target" "$dest"
    printf 'DRY-RUN\trecord\t%s\n' "$rec"
    return 0
  fi
  dg=$(tree_digest "$target") || { printf 'REFUSED\tdigest-failed\t%s\n' "$target" >&2; return 1; }
  mkdir -p -- "$(dirname -- "$dest")"
  mv -- "$target" "$dest"
  rc=$?
  if [ "$rc" -ne 0 ] || [ ! -e "$dest" ] || [ -e "$target" ]; then
    printf 'REFUSED\tmv-failed\t%s\n' "$target" >&2; return 1
  fi
  printf '{"original":"%s","staged":"%s","receipt":"%s","digest":"%s","staged_at":"%s"}\n' \
    "$(json_escape "$target")" "$(json_escape "$dest")" "$Q_RECEIPT" "$dg" \
    "$(date -Is)" > "$rec"
  printf 'STAGED\t%s\t%s\treceipt=%s\tdigest=%s\n' "$target" "$dest" "$Q_RECEIPT" "${dg:0:12}"
  return 0
}

# step_3 second check — original gone, staged copy intact, gates still clean.
verify_staged_path() { # $1 raw ORIGINAL path
  local raw=$1 target repo rel dest rec rdg now_dg
  target=$(canon_path "$raw")
  if is_secret_shaped "$target"; then
    printf 'HOLD\tsecrets-refusal\t%s\n' "$target"; return 0
  fi
  repo=$(find_repo_for "$target") || { printf 'HOLD\tno-repo\t%s\n' "$target"; return 0; }
  case "$target" in "$repo"/*) rel=${target#"$repo"/} ;; *) rel=$target ;; esac
  IFS=$'\t' read -r dest rec <<< "$(qpaths "$repo" "$rel")"
  if [ -e "$target" ] || [ -L "$target" ]; then
    printf 'HOLD\toriginal-present\t%s\n' "$target"
    printf '  staging did not take effect; nothing to second-check\n'
    return 0
  fi
  if [ ! -e "$dest" ] || [ ! -f "$rec" ]; then
    printf 'HOLD\tstaged-copy-or-record-missing\t%s\n' "$dest"
    return 0
  fi
  # gates must still be clean at the ORIGINAL path (tracked deletions show
  # up here as gate2 dirty — by design that holds the ticket).
  G1_LINES=$(git -C "$repo" log --branches --not --remotes --oneline -- "$rel" 2>/dev/null | wc -l || true)
  G1_LINES=${G1_LINES// /}
  G2_LINES=$(git -C "$repo" status --porcelain=v1 --untracked-files=all -- "$rel" 2>/dev/null | wc -l || true)
  G2_LINES=${G2_LINES// /}
  if [ "$G1_LINES" != 0 ] || [ "$G2_LINES" != 0 ]; then
    printf 'HOLD\tgates-dirty-after-stage\t%s\tgate1=%s gate2=%s\n' "$target" "$G1_LINES" "$G2_LINES"
    printf '  (tracked paths held by design: the mv leaves a deletion in the index-less worktree)\n'
    return 0
  fi
  rdg=$(printf '%s' "$(cat -- "$rec")" | grep -o '"digest":"[^"]*"' | cut -d'"' -f4 || true)
  now_dg=$(tree_digest "$dest") || now_dg=digest-failed
  if [ -z "$rdg" ] || [ "$now_dg" != "$rdg" ]; then
    printf 'HOLD\tdigest-mismatch\t%s\trecord=%s now=%s\n' "$dest" "${rdg:0:12}" "${now_dg:0:12}"
    return 0
  fi
  printf 'STAGED-VERIFIED\t%s\t%s\tdigest=%s\n' "$target" "$dest" "${now_dg:0:12}"
  printf '  eligible for step_4 retire with --operator-signoff\n'
  return 0
}

# step_4 retire — signoff + record + digest + sandbox, then rm staged ONLY.
retire_staged_path() { # $1 raw STAGED path
  local raw=$1 staged rec orig rdg now_dg
  staged=$(canon_path "$raw")
  if ! sandbox_allows "$staged"; then
    printf 'REFUSED\toutside-sandbox\t%s\n' "$staged" >&2
    printf 'souji-quarantine: retire refused: SOUJI_Q_SANDBOX unset or does not cover %s\n' "$staged" >&2
    return 1
  fi
  if [ -z "$SIGNOFF" ]; then
    printf 'REFUSED\tsignoff-required\t%s\n' "$staged" >&2
    return 1
  fi
  case "$staged" in
    *.souji-qrecord.json|*/.ufo-quarantine/*) : ;;
    *) printf 'REFUSED\tnot-quarantine-path\t%s\n' "$staged" >&2; return 1 ;;
  esac
  case "$staged" in *.souji-qrecord.json)
    printf 'REFUSED\trecord-path\t%s\n' "$staged" >&2; return 1 ;;
  esac
  rec="$staged.souji-qrecord.json"
  [ -f "$rec" ] || { printf 'REFUSED\trecord-missing\t%s\n' "$rec" >&2; return 1; }
  orig=$(printf '%s' "$(cat -- "$rec")" | grep -o '"original":"[^"]*"' | cut -d'"' -f4 || true)
  [ -n "$orig" ] || { printf 'REFUSED\trecord-unreadable\t%s\n' "$rec" >&2; return 1; }
  if [ -e "$orig" ] || [ -L "$orig" ]; then
    printf 'REFUSED\toriginal-reappeared\t%s\n' "$orig" >&2; return 1
  fi
  rdg=$(printf '%s' "$(cat -- "$rec")" | grep -o '"digest":"[^"]*"' | cut -d'"' -f4 || true)
  now_dg=$(tree_digest "$staged") || now_dg=digest-failed
  if [ -z "$rdg" ] || [ "$now_dg" != "$rdg" ]; then
    printf 'REFUSED\tdigest-mismatch\t%s\n' "$staged" >&2; return 1
  fi
  rm -rf -- "$staged" "$rec"
  printf 'RETIRED\t%s\toriginal=%s\tsignoff=%s\tdigest=%s\n' \
    "$staged" "$orig" "$SIGNOFF" "${now_dg:0:12}"
  return 0
}

# ---------------------------------------------------------------- selftest --

ST_TMP="" ST_FLEET="" ST_LEDGER="" ST_OTHER=""
ST_PASS=0 ST_FAIL=0
# NOTE: SOUJI_Q_SANDBOX is never defaulted here. Production runs leave it
# unset and every mutation is REFUSED; run_selftest sets it to its own
# mktemp root and nested invocations inherit it.

st_note() { printf '%s\n' "$*"; }
st_ok() { ST_PASS=$((ST_PASS+1)); st_note "PASS $*"; }
st_bad() { ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $*"; }

st_commit() { # $1 repo, $2 parent(sha|""), $3 msg -> sha (plumbing only)
  local repo=$1 parent=$2 msg=$3 tr sha
  git -C "$repo" add -A >/dev/null 2>&1
  tr=$(git -C "$repo" write-tree)
  if [ -n "$parent" ]; then
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr" -p "$parent")
  else
    sha=$(printf '%s\n' "$msg" | git -C "$repo" commit-tree "$tr")
  fi
  printf '%s' "$sha"
}

st_check_line() { # $1 id, $2 want-verdict, $3 want-gate3("" = any), $4 evidence-substr, $5 target, $6 expect-receipt("")
  local id=$1 wv=$2 wg3=$3 wsub=$4 target=$5 expect=$6 out verdict g3
  local -a args=(--check --json)
  [ -n "$expect" ] && args+=(--expect-receipt "$expect")
  set +e
  out=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
        "$SELF" "${args[@]}" "$target" 2>&1)
  set -e
  verdict=$(printf '%s\n' "$out" | grep -o '"verdict":"[^"]*"' | head -1 | cut -d'"' -f4 || true)
  g3=$(printf '%s\n' "$out" | grep -o '"gate3":"[^"]*"' | head -1 | cut -d'"' -f4 || true)
  if [ "$verdict" != "$wv" ]; then
    st_bad "$id: verdict=$verdict want=$wv out=$out"; return 0
  fi
  if [ -n "$wg3" ] && [ "${g3%%:*}" != "$wg3" ]; then
    st_bad "$id: gate3=$g3 want=$wg3"; return 0
  fi
  if [ -n "$wsub" ]; then
    case "$out" in
      *"$wsub"*) : ;;
      *) st_bad "$id: evidence lacks '$wsub': $out"; return 0 ;;
    esac
  fi
  st_ok "$id $verdict gate3=${g3:-any}"
}

st_refusal() { # $1 id, $2 want-exit, $3 must-still-exist path ("" = skip), rest = cmd
  local id=$1 want=$2 keep=$3; shift 3
  local status
  set +e
  "$@" >/dev/null 2>&1
  status=$?
  set -e
  if [ "$status" = "$want" ]; then st_ok "$id exit=$status"; else st_bad "$id exit=$status want=$want"; fi
  if [ -n "$keep" ]; then
    [ -e "$keep" ] && st_ok "$id target survived: $keep" || st_bad "$id target VANISHED: $keep"
  fi
}

st_build_fixtures() {
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-quarantine-selftest.XXXXXX")
  ST_FLEET="$ST_TMP/fleet"
  ST_LEDGER="$ST_TMP/ledger.tsv"
  ST_OTHER="$ST_TMP/other"          # deliberately NOT the sandbox
  mkdir -p "$ST_FLEET" "$ST_OTHER"
  : > "$ST_LEDGER"

  local R="$ST_FLEET/authz-repo-shokunin"
  git init -q --initial-branch=master "$R"
  mkdir -p "$R/.scratch"
  printf 'pushed payload\n' > "$R/pushed-file.txt"
  local c1; c1=$(st_commit "$R" "" "c1 adds pushed-file.txt")
  printf 'local payload\n' > "$R/local-only.txt"
  local c2; c2=$(st_commit "$R" "$c1" "c2 local-only adds local-only.txt")
  git -C "$R" update-ref refs/heads/master "$c2"
  git -C "$R" update-ref refs/remotes/origin/master "$c1"
  git -C "$R" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  printf '.scratch/\n' > "$R/.gitignore"
  local c3; c3=$(st_commit "$R" "$c2" "c3 local-only gitignore")
  git -C "$R" update-ref refs/heads/master "$c3"
  # stale-eligible scratch pair + a root-level UNTRACKED NON-ignored .out
  # (unq.out must sit outside the ignored .scratch/ dir to fail gate2)
  printf 'self mention old-q9.out\n'  > "$R/.scratch/old-q9.out"
  printf 'self mention old-q10.out\n' > "$R/.scratch/old-q10.out"
  printf 'self mention unq.out\n'     > "$R/unq.out"
  printf 'probe\n' > "$R/.scratch/probe-keep.txt"
  touch -d '3 days ago' "$R/.scratch/old-q9.out" "$R/.scratch/old-q10.out" "$R/unq.out"

  # zero-remote repo for the gate1 pitfall regression (r6)
  local RN="$ST_FLEET/noremo-shokunin"
  git init -q --initial-branch=master "$RN"
  printf 'tracked local-only\n' > "$RN/t.txt"
  local n1; n1=$(st_commit "$RN" "" "n1 adds t.txt (no remote ever)")
  git -C "$RN" update-ref refs/heads/master "$n1"
  return 0
}

run_selftest() {
  if [ "${SOUJI_Q_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'souji-quarantine: refusing nested --selftest\n' >&2
    exit 1
  fi
  # arm cleanup BEFORE fixture build: a quota/init failure mid-build must
  # not leak the partial mktemp root (qrun-03 incident)
  trap '[ -n "${ST_TMP:-}" ] && rm -rf -- "$ST_TMP"' EXIT
  st_build_fixtures
  local R="$ST_FLEET/authz-repo-shokunin"

  # --- step_0_recheck authorization matrix --------------------------------
  st_check_line Q1 AUTHORIZED pass "" "$R/pushed-file.txt" ""
  st_check_line Q1b AUTHORIZED pass "" "$R/pushed-file.txt" pushed
  st_check_line Q2 NOT-AUTHORIZED fail "gate1=unpushed-touching(1)" "$R/local-only.txt" ""
  st_check_line Q3 NOT-AUTHORIZED pass "gate2=dirty-touching(1)" "$R/unq.out" ""
  st_check_line Q3b AUTHORIZED pass "" "$R/.scratch/old-q9.out" ""
  st_check_line Q4 NOT-AUTHORIZED fail "gate1=unpushed-touching(1)" "$ST_FLEET/noremo-shokunin/t.txt" ""
  st_check_line Q5 NOT-AUTHORIZED fail "receipt-mismatch" "$R/.scratch/old-q9.out" pushed
  st_check_line Q6 NOT-AUTHORIZED pass "secrets-refusal" "$R/x.env" ""

  # r6 pitfall regression: bare --not --remotes is silently empty on a
  # zero-remote repo; the explicit gate1 form must NOT be.
  local bare expl
  bare=$(git -C "$ST_FLEET/noremo-shokunin" log --oneline --not --remotes -- t.txt 2>/dev/null | wc -l || true)
  expl=$(git -C "$ST_FLEET/noremo-shokunin" log --branches --not --remotes --oneline -- t.txt 2>/dev/null | wc -l || true)
  if [ "${bare// /}" = 0 ] && [ "${expl// /}" -ge 1 ]; then
    st_ok "Q7 gate1 explicit form fails closed where bare form is silently empty (bare=0 explicit>=1)"
  else
    st_bad "Q7 pitfall regression: bare=$bare explicit=$expl"
  fi

  # --- mutation refusals OUTSIDE the sandbox (live-fleet guard) -----------
  local NQ9="$R/.scratch/old-q9.out"
  st_refusal Q8 1 "$NQ9" env -u GIT_DIR -u SOUJI_Q_SANDBOX "$SELF" --stage "$NQ9"
  st_refusal Q9 1 "$NQ9" env -u GIT_DIR SOUJI_Q_SANDBOX="$ST_OTHER" "$SELF" --stage "$NQ9"
  st_refusal Q10 1 "" env -u GIT_DIR -u SOUJI_Q_SANDBOX "$SELF" --retire --operator-signoff x "$R/.ufo-quarantine/nowhere"

  # --- sandboxed end-to-end flow: stage -> hold -> 2nd check -> retire ----
  SOUJI_Q_SANDBOX="$ST_FLEET"
  export SOUJI_Q_SANDBOX
  local stage_out dest rec probe
  set +e
  stage_out=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
              "$SELF" --stage "$NQ9" 2>&1)
  set -e
  if printf '%s' "$stage_out" | grep -q '^STAGED' && [ ! -e "$NQ9" ]; then
    st_ok "Q11 staged + original gone"
  else
    st_bad "Q11 stage: $stage_out (original exists: $([ -e "$NQ9" ] && echo yes || echo no))"
  fi
  dest="$R/.ufo-quarantine/$(date +%F)/.scratch__old-q9.out"
  rec="$dest.souji-qrecord.json"
  probe="$R/.scratch/probe-keep.txt"
  if [ -f "$rec" ] && [ -e "$probe" ]; then
    st_ok "Q12 record written; unrelated neighbor untouched"
  else
    st_bad "Q12 rec=$([ -f "$rec" ] && echo ok || echo missing) probe=$([ -e "$probe" ] && echo ok || echo MISSING)"
  fi
  [ -f "$rec" ] || { st_note "ABORT: no record; cannot continue staged-path cases"; exit 1; }

  local vs
  vs=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
       "$SELF" --verify-staged "$NQ9" 2>&1)
  case "$vs" in STAGED-VERIFIED*) st_ok "Q13 second check verified" ;; *) st_bad "Q13: $vs" ;; esac

  st_refusal Q14 1 "$dest" env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
    "$SELF" --retire "$dest"

  # tamper case on the twin file, then retire the good one
  set +e
  env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
    "$SELF" --stage "$R/.scratch/old-q10.out" >/dev/null 2>&1
  set -e
  local dest2="$R/.ufo-quarantine/$(date +%F)/.scratch__old-q10.out"
  printf 'tampered\n' >> "$dest2"
  local vt
  vt=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
       "$SELF" --verify-staged "$R/.scratch/old-q10.out" 2>&1)
  case "$vt" in HOLD*digest-mismatch*) st_ok "Q15 tampered staged copy held" ;; *) st_bad "Q15: $vt" ;; esac

  local vstill
  vstill=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
           "$SELF" --verify-staged "$R/pushed-file.txt" 2>&1)
  case "$vstill" in HOLD*original-present*) st_ok "Q16 unstaged original held" ;; *) st_bad "Q16: $vstill" ;; esac

  set +e
  local retr
  retr=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
         "$SELF" --retire --operator-signoff "round8-S03-fixture-proof" "$dest" 2>&1)
  set -e
  if printf '%s' "$retr" | grep -q '^RETIRED' && [ ! -e "$dest" ] && [ ! -e "$rec" ] \
     && [ ! -e "$NQ9" ] && [ -e "$probe" ]; then
    st_ok "Q17 retired: staged copy + record removed; original stays absent; neighbor intact"
  else
    st_bad "Q17 retire: $retr"
  fi

  # dry-run must not move anything
  local dry
  set +e
  dry=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
        "$SELF" --stage --dry-run "$R/pushed-file.txt" 2>&1)
  set -e
  # pushed-file is AUTHORIZED (Q1) so dry-run prints commands but must not move
  if printf '%s' "$dry" | grep -q '^DRY-RUN' && [ -e "$R/pushed-file.txt" ]; then
    st_ok "Q18 dry-run prints mv without touching the tree"
  else
    st_bad "Q18 dry-run: $dry"
  fi

  # --- structural audits ---------------------------------------------------
  local n
  n=$(grep -nE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase|mv|rm)( |$)' "$SELF" | wc -l || true)
  [ "${n// /}" = 0 ] && st_ok "H1 no forbidden git subcommand" || st_bad "H1 $n forbidden git lines"
  n=$(grep -cE '^[^#]*\b(mv|rm) +--' "$SELF" || true)
  [ "${n// /}" -ge 1 ] && st_ok "H2 mutation lines present ($n) and sandbox-guarded at runtime (Q8/Q9/Q10/Q14)" \
                        || st_bad "H2 no guarded mutation lines found"
  case "$ST_FLEET" in
    "$ST_TMP"/*) st_ok "H5 fixtures under mktemp -d ($ST_TMP)" ;;
    *) st_bad "H5 fixtures not under mktemp" ;;
  esac
  local jout
  jout=$(env -u GIT_DIR SHOKUNIN_ROOT="$ST_FLEET" SOUJI_LEDGER="$ST_LEDGER" \
         "$SELF" --check --json "$R/pushed-file.txt" 2>&1)
  if printf '%s' "$jout" | grep -q '"verdict":"AUTHORIZED"' \
     && printf '%s' "$jout" | grep -q '"gate1":"pass"' \
     && printf '%s' "$jout" | grep -q '"gate3":"pass"'; then
    st_ok "H8 check --json shape"
  else
    st_bad "H8 json shape '$jout'"
  fi

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  [ "$ST_FAIL" -eq 0 ] || exit 1
  exit 0
}

# ------------------------------------------------------------------- main --

while [ "$#" -gt 0 ]; do
  case "$1" in
    --check) MODE=check; shift ;;
    --plan) MODE=plan; shift ;;
    --stage) MODE=stage; shift ;;
    --verify-staged) MODE=verify-staged; shift ;;
    --retire) MODE=retire; shift ;;
    --selftest) MODE=selftest; shift ;;
    --json) JSON=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --expect-receipt) [ "$#" -ge 2 ] || usage_err "--expect-receipt needs a value"; EXPECT_RECEIPT=$2; shift 2 ;;
    --expect-receipt=*) EXPECT_RECEIPT=${1#*=}; shift ;;
    --operator-signoff) [ "$#" -ge 2 ] || usage_err "--operator-signoff needs a value"; SIGNOFF=$2; shift 2 ;;
    --operator-signoff=*) SIGNOFF=${1#*=}; shift ;;
    -h|--help) usage 0 ;;
    --) shift; while [ "$#" -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -*) usage_err "unknown flag: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

case "$EXPECT_RECEIPT" in
  ''|pushed|moved-to-obsidian|stale|metadata-prune) : ;;
  *) usage_err "--expect-receipt must be pushed|moved-to-obsidian|stale|metadata-prune" ;;
esac

case "$MODE" in
  selftest) run_selftest ;;
  "") usage_err "no mode given (one of --check --plan --stage --verify-staged --retire --selftest)" ;;
esac

if [ "${#TARGETS[@]}" -eq 0 ]; then usage_err "no targets given"; fi
command -v git >/dev/null 2>&1 || { printf 'souji-quarantine: git not found\n' >&2; exit 2; }
command -v sha256sum >/dev/null 2>&1 || { printf 'souji-quarantine: sha256sum not found\n' >&2; exit 2; }
if [ ! -f "$TOOL_A" ] || [ ! -f "$TOOL_B" ]; then
  printf 'souji-quarantine: receipt engines missing (%s, %s)\n' "$TOOL_A" "$TOOL_B" >&2
  exit 2
fi

case "$MODE" in
  check)
    for t in "${TARGETS[@]}"; do
      check_path "$t"
      if [ "$JSON" = 1 ]; then emit_json "$t"; else emit_text "$t"; fi
    done
    exit 0 ;;
  plan)
    for t in "${TARGETS[@]}"; do print_plan "$t"; done
    exit 0 ;;
  stage)
    rc=0
    for t in "${TARGETS[@]}"; do stage_path "$t" || rc=1; done
    exit "$rc" ;;
  verify-staged)
    for t in "${TARGETS[@]}"; do verify_staged_path "$t"; done
    exit 0 ;;
  retire)
    rc=0
    for t in "${TARGETS[@]}"; do retire_staged_path "$t" || rc=1; done
    exit "$rc" ;;
esac
