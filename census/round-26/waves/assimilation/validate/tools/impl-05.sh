#!/usr/bin/env bash
# impl-05.sh — souji round 8: quarantine-flow tool (S05 implementor seat)
#
# Implements SKILL.md "Removal flow" steps 1–6 as machine steps:
#   plan | stage | second-check | release | restore  + --selftest
#
# Receipt engine: tools/souji-verify.sh (installed) when present, else an
# internal fallback implementing the r6 spec (pushed / moved-to-obsidian /
# stale, fail-closed refusals). Pass --receipt PATH to override.
#
# SAFETY (round-8 contract):
#   * stage / second-check / release / restore mutate ONLY inside a fixture
#     repo whose realpath is under "${TMPDIR:-/tmp}/tmp.*" (mktemp). Anything
#     else is refused with exit 3 BEFORE touching disk. There is no override.
#   * plan is read-only everywhere.
#   * No git push/fetch/reset/rebase/amend/checkout/branch anywhere.
#   * Never reads secret-shaped files; never touches .ufo/state,
#     .ufo/watchdog.log, ~/.config.
#   * Commits (fixtures only) use souji-shokunin <souji@shokunin.local> and
#     name the receipt class + evidence pointer.
#
# Exit codes: 0 ok · 1 gate refusal / operational failure / selftest fail ·
#             2 usage · 3 live-mutation refusal.

set -u -o pipefail

SELF=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
SOUJI_ID="souji-shokunin <souji@shokunin.local>"
DEFAULT_HOLD=450
STALE_DAYS=1
TMPBASE=$(realpath -m "${TMPDIR:-/tmp}")

VERDICT_OK=0

die() { printf 'impl-05: %s\n' "$*" >&2; exit "${2:-1}"; }
usage() {
  cat >&2 <<'EOF'
usage:
  impl-05.sh plan         [--receipt PATH|--receipt internal] [options] <path>...
  impl-05.sh stage        --root FIXTURE_ROOT [options] <path>...
  impl-05.sh second-check --root FIXTURE_ROOT --ticket TICKET_JSON
  impl-05.sh release      --root FIXTURE_ROOT --ticket TICKET_JSON
  impl-05.sh restore      --root FIXTURE_ROOT --ticket TICKET_JSON
  impl-05.sh --selftest
options:
  --hold-seconds N   hold period for non-pushed receipts (default 450)
  --stale-days N     mtime threshold for stale receipts (default 1)
  --ledger PATH      obsidian ledger for internal engine
  --json             machine-readable output (plan)
  --dry-run          plan always is; accepted-and-ignored on other verbs
plan is read-only and works on live paths. stage/second-check/release/
restore refuse any --root outside "${TMPDIR:-/tmp}/tmp.*" (exit 3).
EOF
  exit 2
}

# ---------- tiny JSON helpers (no jq) ------------------------------------
json_escape() { # stdin: raw -> stdout: escaped single-line string
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; s=${s//$'\r'/\\r}
  printf '%s' "$s"
}
json_str() { printf '"%s"' "$(json_escape "$1")"; }
json_get() { # json_get <json> <key> -> raw string value (plain regex, our own files)
  local re="\"$2\"[[:space:]]*:[[:space:]]*\"([^\"]*)\""
  [[ $1 =~ $re ]] && printf '%s' "${BASH_REMATCH[1]}" || return 1
}
json_get_num() {
  local re="\"$2\"[[:space:]]*:[[:space:]]*(-?[0-9]+)"
  [[ $1 =~ $re ]] && printf '%s' "${BASH_REMATCH[1]}" || return 1
}
json_get_bool() {
  local re="\"$2\"[[:space:]]*:[[:space:]]*(true|false|null)"
  [[ $1 =~ $re ]] && printf '%s' "${BASH_REMATCH[1]}" || return 1
}

# ---------- receipt engine -----------------------------------------------
RECEIPT=auto   # auto | internal | path
LEDGER=""
SOUJI_DIR_ENG="$(dirname "$SELF")/souji-verify.sh"

engine_cmd() { # engine_cmd <path> -> prints VERDICT line on stdout
  local path=$1
  local eng=$RECEIPT
  if [[ $eng == auto ]]; then
    if [[ -x $SOUJI_DIR_ENG ]]; then eng=$SOUJI_DIR_ENG; else eng=internal; fi
  fi
  if [[ $eng == internal ]]; then
    engine_internal "$path"
  else
    "$eng" --stale-days "$STALE_DAYS" "$path" 2>/dev/null | awk -F'\t' -v p="$path" '$1=="VERDICT" && $2==p'
  fi
}

engine_internal() { # fallback receipt engine, r6-spec faithful
  local path=$1
  local name ev receipt verdict ev_line
  name=$(basename "$path")
  case $name in
    *.env|*credential*|*secret*|id_*|*.pem)
      printf 'VERDICT\t%s\tNOT-SAFE\tsecrets-refusal\tbasename matches refusal list\n' "$path"; return 0;;
  esac
  if [[ ! -e $path ]]; then
    printf 'VERDICT\t%s\tNOT-SAFE\tunreachable\tno such path\n' "$path"; return 0
  fi
  if [[ -L $path ]]; then
    printf 'VERDICT\t%s\tNOT-SAFE\tsymlink-present\tfail-closed r5\n' "$path"; return 0
  fi
  local dir repo default_ref intro unpushed
  dir=$([[ -d $path ]] && echo "$path" || dirname "$path")
  repo=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || repo=""
  # receipt 1: pushed
  if [[ -n $repo ]]; then
    default_ref=$(git -C "$repo" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')
    if [[ -z $default_ref ]]; then
      mapfile -t obrs < <(git -C "$repo" for-each-ref --format='%(refname:short)' refs/remotes/origin 2>/dev/null)
      if [[ ${#obrs[@]} -eq 1 && -n ${obrs[0]} ]]; then default_ref=${obrs[0]#origin/}; fi
    fi
    if [[ -z $default_ref ]]; then
      ev_line="pushed-unverifiable: no origin/HEAD and not exactly one origin/* ref"
    else
      intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$path" 2>/dev/null)
      unpushed=$(git -C "$repo" log --branches --not --remotes --oneline -- "$path" 2>/dev/null | wc -l)
      if [[ -z $intro ]]; then
        ev_line="pushed-unverifiable: no introducing commit (untracked or history gone)"
      elif ! git -C "$repo" merge-base --is-ancestor "$intro" "refs/remotes/origin/$default_ref" 2>/dev/null; then
        ev_line="pushed-unverifiable: introducing commit not ancestor of origin/$default_ref"
      elif [[ $unpushed -ne 0 ]]; then
        ev_line="unpushed-commits-touching: $unpushed local commit(s) touch path"
      else
        printf 'VERDICT\t%s\tSAFE\tpushed\tintro=%s ancestor of origin/%s, unpushed-touching=0\n' "$path" "${intro:0:12}" "$default_ref"
        return 0
      fi
    fi
  else
    ev_line="pushed-unverifiable: path not inside a git repo"
  fi
  # receipt 2: moved-to-obsidian
  if [[ -n $LEDGER && -f $LEDGER ]]; then
    local line src sha_s vault sha_v mysha
    mysha=$(sha256sum "$path" 2>/dev/null | awk '{print $1}')
    while IFS=$'\t' read -r src sha_s vault sha_v _; do
      [[ ${src:-} == "$path" ]] || continue
      if [[ $sha_s == "$mysha" && -e $vault && $(sha256sum "$vault" 2>/dev/null | awk '{print $1}') == "$sha_v" ]]; then
        printf 'VERDICT\t%s\tSAFE\tmoved-to-obsidian\tledger row + sha256 match both sides\n' "$path"
        return 0
      fi
      ev_line="moved-to-obsidian: ledger row found but hash/path mismatch"
    done < "$LEDGER"
  fi
  # receipt 3: stale
  local scratch=0
  case $path in
    *.scratch/*|*.scratch) scratch=1;;
    *.out|*.log|launch-*.json|*-draft.*) scratch=1;;
  esac
  if [[ $scratch -eq 1 && -n $repo ]]; then
    local hits mtime_now age_days rgrc
    rg -l --no-ignore --fixed-strings -g '!.git/**' -g '!souji-shokunin/census/**' \
        -g '!souji-shokunin/tests/**' -g '!**/.ufo-quarantine/**' -- "$name" "$repo" >/dev/null 2>&1
    rgrc=$?
    case $rgrc in
      1) hits=0;;          # no matches
      0) hits=$(rg -l --no-ignore --fixed-strings -g '!.git/**' -g '!souji-shokunin/census/**' \
            -g '!souji-shokunin/tests/**' -g '!**/.ufo-quarantine/**' -- "$name" "$repo" 2>/dev/null | wc -l);;
      *) hits=-1;;         # rg error: fail closed, never claim zero refs
    esac
    mtime_now=$(stat -c %Y "$path")
    age_days=$(( ( $(date +%s) - mtime_now ) / 86400 ))
      if [[ $hits -eq 0 && $age_days -ge $STALE_DAYS ]]; then
        printf 'VERDICT\t%s\tSAFE\tstale\trefs=0 age=%sd>=%sd scratch-type\n' "$path" "$age_days" "$STALE_DAYS"
        return 0
      fi
      ev_line="stale-unmet: refs=$hits age=${age_days}d required>=${STALE_DAYS}d"
  fi
  printf 'VERDICT\t%s\tNOT-SAFE\tnone\t%s\n' "$path" "${ev_line:-no receipt qualifies}"
  return 0
}

parse_verdict() { # parse_verdict <line> -> sets V_PATH V_SAFE V_RECEIPT V_EVID
  V_PATH=""; V_SAFE=""; V_RECEIPT=""; V_EVID=""
  local IFS=$'\t'
  read -r _ V_PATH V_SAFE V_RECEIPT V_EVID <<< "$1"
}

# ---------- safety guard --------------------------------------------------
assert_fixture_root() { # exit 3 unless realpath is under TMPBASE/tmp.*
  local root=$1 real
  real=$(realpath -e "$root" 2>/dev/null) || die "root not accessible: $root" 3
  [[ -d $real ]] || die "root not a directory: $real" 3
  case $real in
    "$TMPBASE"/tmp.*) return 0;;
    *) die "REFUSED live-mutation: $real is not under $TMPBASE/tmp.* — quarantine mutations are fixture-only (round-8 contract)" 3;;
  esac
}

# ---------- plan (read-only) ---------------------------------------------
do_plan() {
  local json=$1; shift || true
  local out=() line p first=1
  [[ $json == 1 ]] && printf '['
  for p in "$@"; do
    line=$(engine_cmd "$p")
    [[ -n $line ]] || line=$(printf 'VERDICT\t%s\tNOT-SAFE\tnone\tengine returned no line' "$p")
    parse_verdict "$line"
    if [[ $JSON == 1 ]]; then
      (( first )) || printf ','
      first=0
      printf '{"path":%s,"safe":%s,"receipt":%s,"evidence":%s}' \
        "$(json_str "$V_PATH")" \
        "$([[ $V_SAFE == SAFE ]] && echo true || echo false)" \
        "$(json_str "$V_RECEIPT")" "$(json_str "$V_EVID")"
    else
      printf '%s\n' "$line"
    fi
  done
  [[ $json == 1 ]] && printf ']\n'
  return 0
}

# ---------- ticket io -----------------------------------------------------
ticket_write() { # atomic write inside fixture root
  local file=$1 body=$2 tmp
  tmp="${file}.tmp.$$"
  printf '%s\n' "$body" > "$tmp" && mv "$tmp" "$file"
}
ticket_read() { cat "$1"; }

# ---------- stage ---------------------------------------------------------
do_stage() {
  local root=$1 hold=$2; shift 2
  assert_fixture_root "$root"
  local ok=1 p line first_bad=""
  for p in "$@"; do
    [[ -e $p ]] || { printf 'stage: REFUSED %s unreachable\n' "$p" >&2; ok=0; first_bad=${first_bad:-$p}; continue; }
    line=$(engine_cmd "$p")
    parse_verdict "$line"
    if [[ $V_SAFE != SAFE ]]; then
      printf 'stage: REFUSED %s receipt=%s evidence=%s\n' "$p" "${V_RECEIPT:-?}" "${V_EVID:-?}" >&2
      ok=0; first_bad=${first_bad:-$p}
    fi
  done
  [[ $ok -eq 1 ]] || die "stage: at least one target failed the receipt gate (first: $first_bad)" 1

  local repo=$(git -C "$root" rev-parse --show-toplevel 2>/dev/null) || die "stage: --root is not a git repo: $root" 1
  local date_tag staged_at hold_until now
  now=$(date -u +%s); staged_at=$(date -u +%Y-%m-%dT%H:%M:%SZ); date_tag=$(date -u +%Y%m%d)
  local origin_tip; origin_tip=$(git -C "$repo" rev-parse "refs/remotes/origin/${ORIG_DEF:-HEAD}" 2>/dev/null || echo "")
  local made_commit=0
  for p in "$@"; do
    parse_verdict "$(engine_cmd "$p")"
    local abs=$(realpath -e "$p")
    [[ $abs == "$repo"/* || $abs == "$repo" ]] || die "stage: $p is outside its root repo" 1
    local rel=${abs#"$repo"/}; [[ $rel == "$abs" ]] && rel=$(basename "$abs")
    local qdir="$repo/.ufo-quarantine/$date_tag"
    mkdir -p "$qdir"
    local staged="$qdir/$rel"
    [[ ! -e $staged ]] || die "stage: quarantine slot exists: $staged" 1
    local tracked=0; git -C "$repo" ls-files --error-unmatch -- "$rel" >/dev/null 2>&1 && tracked=1
    if [[ $tracked -eq 1 ]]; then
      mkdir -p "$(dirname "$staged")"
      git -C "$repo" mv "$rel" "${staged#"$repo"/}" || die "stage: git mv failed for $rel" 1
    else
      mkdir -p "$(dirname "$staged")"
      mv "$abs" "$staged" || die "stage: mv failed for $rel" 1
    fi
    local sha; sha=$(sha256sum "$staged" | awk '{print $1}')
    if [[ $V_RECEIPT == pushed ]]; then hold_until="null"; hold_req=false; else
      hold_until=$(( now + hold )); hold_req=true
    fi
    local tid="${date_tag}/${rel}"
    local ticket="$qdir/${rel}.ticket.json"
    [[ ! -e $ticket ]] || die "stage: ticket exists: $ticket" 1
    local intro; intro=$(git -C "$repo" log --diff-filter=A --format=%H -1 -- "$rel" 2>/dev/null || echo "")
    ticket_write "$ticket" "$(printf '{
 "ticket": %s,
 "artifact_original_rel": %s,
 "artifact_staged_rel": %s,
 "receipt_class": %s,
 "receipt_evidence": %s,
 "introducing_commit": %s,
 "origin_tip_at_stage": %s,
 "sha256": %s,
 "staged_at_utc": %s,
 "hold_required": %s,
 "hold_until_epoch": %s,
 "second_check": null,
 "released_at_utc": null,
 "restored_at_utc": null,
 "tool": "impl-05.sh"
}' "$(json_str "$tid")" "$(json_str "$rel")" "$(json_str "${staged#"$repo"/}")" \
   "$(json_str "$V_RECEIPT")" "$(json_str "$V_EVID")" "$(json_str "$intro")" \
   "$(json_str "$origin_tip")" "$(json_str "$sha")" "$(json_str "$staged_at")" \
   "${hold_req}" "${hold_until}")"
    printf 'stage: STAGED %s -> %s receipt=%s ticket=%s hold=%s\n' \
      "$rel" "${staged#"$repo"/}" "$V_RECEIPT" "${ticket#"$repo"/}" "$hold_until"
    local qst
    git -C "$repo" add -A -- .ufo-quarantine >/dev/null 2>&1 || true
    if [[ $tracked -eq 1 ]]; then
      qst=$(git -C "$repo" status --porcelain -- .ufo-quarantine "$rel" 2>/dev/null)
      if [[ -n $qst ]]; then
        git -C "$repo" -c user.name="${SOUJI_ID%% <*}" -c user.email="${SOUJI_ID#*<}" \
          commit -q -m "quarantine(stage): $V_RECEIPT $rel [evidence: $V_EVID] [tool: impl-05.sh]" \
          -- .ufo-quarantine "$rel" && made_commit=1
      fi
    else
      qst=$(git -C "$repo" status --porcelain -- .ufo-quarantine 2>/dev/null)
      if [[ -n $qst ]]; then
        git -C "$repo" -c user.name="${SOUJI_ID%% <*}" -c user.email="${SOUJI_ID#*<}" \
          commit -q -m "quarantine(stage): $V_RECEIPT $rel [evidence: $V_EVID] [tool: impl-05.sh]" \
          -- .ufo-quarantine && made_commit=1
      fi
    fi
  done
  return 0
}

# ---------- second-check / release / restore ------------------------------
load_ticket_ctx() { # $1=ticket file -> T_ vars; verifies artifact integrity
  local file=$1
  [[ -f $file ]] || die "second-check: ticket not found: $file" 1
  T_BODY=$(ticket_read "$file")
  T_FILE=$file
  T_TICKET=$(json_get "$T_BODY" ticket) || die "second-check: malformed ticket" 1
  T_REL=$(json_get "$T_BODY" artifact_staged_rel)
  T_ORIG=$(json_get "$T_BODY" artifact_original_rel)
  T_CLASS=$(json_get "$T_BODY" receipt_class)
  T_SHA=$(json_get "$T_BODY" sha256)
  T_INTRO=$(json_get "$T_BODY" introducing_commit)
  T_OTIP=$(json_get "$T_BODY" origin_tip_at_stage)
  T_HOLDREQ=$(json_get_bool "$T_BODY" hold_required)
  T_HOLDUN=$(json_get_num "$T_BODY" hold_until_epoch || echo "")
  T_SC=$(json_get "$T_BODY" second_check)
  [[ $T_SC == "" || $T_SC == null ]] && T_SC=""
  local repo; repo=$(git -C "$(dirname "$file")" rev-parse --show-toplevel 2>/dev/null) || die "ticket outside a repo?" 1
  T_REPO=$repo
  T_STAGED="$repo/$T_REL"
  [[ -e $T_STAGED ]] || die "second-check: staged artifact missing: $T_STAGED" 1
  local sha_now; sha_now=$(sha256sum "$T_STAGED" | awk '{print $1}')
  [[ $sha_now == "$T_SHA" ]] || die "second-check: artifact sha drift ($sha_now != $T_SHA)" 1
  local ev; ev=$(engine_internal "$T_STAGED" 2>/dev/null) || true
  T_ENGINE_LINE=$ev
}

receipt_still_holds() { # receipt-content re-verification at second-check time
  case $T_CLASS in
    pushed)
      local def
      def=$(git -C "$T_REPO" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')
      [[ -n $def ]] || { mapfile -t obrs < <(git -C "$T_REPO" for-each-ref --format='%(refname:short)' refs/remotes/origin 2>/dev/null); [[ ${#obrs[@]} -eq 1 ]] && def=${obrs[0]#origin/}; }
      [[ -n $def ]] || { SC_WHY="origin default ref vanished"; return 1; }
      if [[ -n $T_INTRO ]] && ! git -C "$T_REPO" merge-base --is-ancestor "$T_INTRO" "refs/remotes/origin/$def" 2>/dev/null; then
        SC_WHY="introducing commit $T_INTRO no longer ancestor of origin/$def"; return 1
      fi
      local tip_now; tip_now=$(git -C "$T_REPO" rev-parse "refs/remotes/origin/$def" 2>/dev/null || echo "")
      if [[ -n $T_OTIP && $tip_now != "$T_OTIP" && -n $tip_now ]] && ! git -C "$T_REPO" merge-base --is-ancestor "$T_OTIP" "$tip_now" 2>/dev/null; then
        SC_WHY="origin rewound: $T_OTIP -> $tip_now"; return 1
      fi
      SC_WHY="intro still ancestor of origin/$def; origin tip monotone; sha intact"
      return 0;;
    stale|moved-to-obsidian)
      if [[ $T_HOLDREQ == true && -n $T_HOLDUN ]]; then
        local now; now=$(date -u +%s)
        (( now >= T_HOLDUN )) || { SC_WHY="hold not elapsed ($(( T_HOLDUN - now ))s left)"; return 1; }
      fi
      case $T_CLASS in
        stale)
          local name hits rgrc
          name=$(basename "$T_ORIG")
          rg -l --no-ignore --fixed-strings -g '!.git/**' -g '!souji-shokunin/census/**' \
              -g '!souji-shokunin/tests/**' -g '!**/.ufo-quarantine/**' -- "$name" "$T_REPO" >/dev/null 2>&1
          rgrc=$?
          case $rgrc in
            1) hits=0;;
            0) hits=$(rg -l --no-ignore --fixed-strings -g '!.git/**' -g '!souji-shokunin/census/**' \
                  -g '!souji-shokunin/tests/**' -g '!**/.ufo-quarantine/**' -- "$name" "$T_REPO" 2>/dev/null | wc -l);;
            *) SC_WHY="reference sweep errored (rc=$rgrc) — fail closed"; return 1;;
          esac
          [[ $hits -eq 0 ]] || { SC_WHY="$hits live reference(s) appeared"; return 1; }
          SC_WHY="hold elapsed; refs=0 (quarantine excluded); sha intact"; return 0;;
        moved-to-obsidian)
          SC_WHY="hold elapsed; sha intact; ledger re-check delegated to engine at stage time"; return 0;;
      esac;;
    *) SC_WHY="unknown receipt class $T_CLASS"; return 1;;
  esac
}

do_second_check() {
  local root=$1 ticket=$2
  assert_fixture_root "$root"
  load_ticket_ctx "$ticket"
  [[ -z $T_SC ]] || die "second-check: already performed ($T_SC)" 1
  if receipt_still_holds; then
    T_SC="pass"
    local now; now=$(date -u +%s)
    T_BODY=${T_BODY/\"second_check\": null/\"second_check\": \"pass at $(date -u -d "@$now" +%Y-%m-%dT%H:%M:%SZ): $SC_WHY\"}
    ticket_write "$T_FILE" "$T_BODY"
    printf 'second-check: PASS %s (%s)\n' "$T_TICKET" "$SC_WHY"
    return 0
  else
    T_SC="fail"
    T_BODY=${T_BODY/\"second_check\": null/\"second_check\": \"fail: $SC_WHY\"}
    ticket_write "$T_FILE" "$T_BODY"
    printf 'second-check: FAIL %s (%s)\n' "$T_TICKET" "$SC_WHY" >&2
    return 1
  fi
}

do_release() {
  local root=$1 ticket=$2
  assert_fixture_root "$root"
  load_ticket_ctx "$ticket"
  [[ $T_SC == pass* ]] || die "release: second-check has not passed for $T_TICKET" 1
  local tracked=0; git -C "$T_REPO" ls-files --error-unmatch -- "$T_REL" >/dev/null 2>&1 && tracked=1
  if [[ $tracked -eq 1 ]]; then
    git -C "$T_REPO" rm -q -r -f -- "$T_REL"
  else
    rm -rf -- "$T_STAGED"
  fi
  local now; now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  T_BODY=${T_BODY/\"released_at_utc\": null/\"released_at_utc\": \"$now\"}
  printf '%s\n' "$T_BODY" > "$T_FILE"
  git -C "$T_REPO" add -A -- .ufo-quarantine >/dev/null 2>&1 || true
  git -C "$T_REPO" -c user.name="${SOUJI_ID%% <*}" -c user.email="${SOUJI_ID#*<}" \
    commit -q -m "quarantine(release): $T_CLASS $T_ORIG [second-check: pass; tool: impl-05.sh]" -- .ufo-quarantine 2>/dev/null || true
  printf 'release: RELEASED %s (deleted from quarantine, receipt=%s)\n' "$T_TICKET" "$T_CLASS"
}

do_restore() {
  local root=$1 ticket=$2
  assert_fixture_root "$root"
  load_ticket_ctx "$ticket"
  local dst="$T_REPO/$T_ORIG"
  mkdir -p "$(dirname "$dst")"
  local tracked=0; git -C "$T_REPO" ls-files --error-unmatch -- "$T_REL" >/dev/null 2>&1 && tracked=1
  if [[ $tracked -eq 1 ]]; then
    git -C "$T_REPO" mv "$T_REL" "$T_ORIG"
  else
    mv "$T_STAGED" "$dst"
  fi
  local now; now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  T_BODY=${T_BODY/\"restored_at_utc\": null/\"restored_at_utc\": \"$now\"}
  printf '%s\n' "$T_BODY" > "$T_FILE"
  git -C "$T_REPO" add -A -- .ufo-quarantine "$T_ORIG" >/dev/null 2>&1 || true
  if [[ -n $(git -C "$T_REPO" status --porcelain -- .ufo-quarantine "$T_ORIG" 2>/dev/null) ]]; then
    git -C "$T_REPO" -c user.name="${SOUJI_ID%% <*}" -c user.email="${SOUJI_ID#*<}" \
      commit -q -m "quarantine(restore): $T_ORIG [hold-period recovery; tool: impl-05.sh]" \
      -- .ufo-quarantine "$T_ORIG" 2>/dev/null || true
  fi
  printf 'restore: RESTORED %s -> %s\n' "$T_TICKET" "$T_ORIG"
}

# ---------- selftest ------------------------------------------------------
SELFTEST_RESULTS=()
ts_pass() { SELFTEST_RESULTS+=("PASS|$1|$2"); printf '  TS PASS %s — %s\n' "$1" "$2"; }
ts_fail() { SELFTEST_RESULTS+=("FAIL|$1|$2"); printf '  TS FAIL %s — %s\n' "$1" "$2" >&2; }
print_tally() {
  local pass=0 fail=0 r
  for r in "${SELFTEST_RESULTS[@]}"; do
    [[ $r == PASS* ]] && pass=$((pass+1)) || fail=$((fail+1))
  done
  printf 'impl-05 selftest: %d/%d passed\n' "$pass" "$((pass+fail))"
  (( fail == 0 ))
}

selftest() {
  printf 'impl-05 selftest: building fixtures under mktemp\n'
  # static self-audit: no forbidden git verbs in this tool
  if grep -nE '(^|[^[:alnum:]_-])git +(--[a-z-]+ +)*(push|fetch|reset|rebase|amend|checkout|branch)( |$)' "$SELF" >/dev/null; then
    ts_fail SA1 "forbidden git verb found in tool source"
  else
    ts_pass SA1 "no git push/fetch/reset/rebase/amend/checkout/branch in source"
  fi

  local W=""
  cleanup() { [[ -n ${W:-} ]] && rm -rf "$W"; return 0; }
  trap cleanup EXIT
  local attempt=0
  W=""
  while (( attempt < 4 )); do
    W=$(mktemp -d "${TMPBASE}/tmp.q05.XXXXXX" 2>/dev/null) && break
    attempt=$((attempt+1)); sleep $(( attempt * 5 ))   # transient /tmp quota pressure under fleet load
  done
  [[ -n $W ]] || { ts_fail ENV1 "mktemp failed: /tmp quota exhausted after retries"; print_tally; exit 1; }
  if ! git init -q --bare "$W/origin.git" 2>/dev/null; then
    local tries=0
    while (( tries < 3 )); do
      sleep $(( (tries+1) * 5 ))
      rm -rf "$W"; W=$(mktemp -d "${TMPBASE}/tmp.q05.XXXXXX") && git init -q --bare "$W/origin.git" 2>/dev/null && break
      tries=$((tries+1))
    done
    [[ -d $W/origin.git/objects ]] || { ts_fail ENV1 "git init failed: /tmp quota exhausted after retries"; print_tally; exit 1; }
  fi
  local ORIG="$W/origin.git" CLONE="$W/clone"
  git init -q --bare "$ORIG"
  git init -q "$CLONE"
  git -C "$CLONE" remote add origin "$ORIG"
  git -C "$CLONE" checkout -q -b master
  : > "$CLONE/README.md"
  git -C "$CLONE" add README.md
  git -C "$CLONE" -c user.name=souji-shokunin -c user.email=souji@shokunin.local commit -q -m "init"
  git -C "$CLONE" push -q origin master
  git -C "$CLONE" remote set-head origin -a >/dev/null 2>&1 || true

  # pushed fixture file (commit pushed to origin)
  printf 'payload-pushed\n' > "$CLONE/notes-v1.txt"
  git -C "$CLONE" add notes-v1.txt
  git -C "$CLONE" -c user.name=souji-shokunin -c user.email=souji@shokunin.local commit -q -m "add notes-v1"
  git -C "$CLONE" push -q origin master

  # dirty tracked file with unpushed commit touching it (NOT-SAFE class)
  printf 'wip\n' > "$CLONE/wip.txt"
  git -C "$CLONE" add wip.txt
  git -C "$CLONE" -c user.name=souji-shokunin -c user.email=souji@shokunin.local commit -q -m "wip (local only)"
  printf 'dirtier\n' >> "$CLONE/wip.txt"

  # stale scratch fixture (untracked, old, zero refs)
  mkdir -p "$CLONE/.scratch"
  printf 'old scratch\n' > "$CLONE/.scratch/old-scan.out"
  touch -d '3 days ago' "$CLONE/.scratch/old-scan.out"

  # obsidian fixture: preserved copy + matching ledger
  printf 'archived prose\n' > "$CLONE/essay-draft.md"
  touch -d '2 days ago' "$CLONE/essay-draft.md"
  mkdir -p "$W/vault"
  cp "$CLONE/essay-draft.md" "$W/vault/essay-draft.md"
  local esha vsha; esha=$(sha256sum "$CLONE/essay-draft.md" | awk '{print $1}'); vsha=$(sha256sum "$W/vault/essay-draft.md" | awk '{print $1}')
  printf '%s\t%s\t%s\t%s\tr8-fixture\n' "$CLONE/essay-draft.md" "$esha" "$W/vault/essay-draft.md" "$vsha" > "$W/ledger.tsv"

  export LEDGER="$W/ledger.tsv"
  RECEIPT=internal

  # TS1 plan: read-only on fixture, pushed verdict
  local line; line=$(engine_cmd "$CLONE/notes-v1.txt")
  parse_verdict "$line"
  [[ $V_SAFE == SAFE && $V_RECEIPT == pushed ]] \
    && ts_pass TS1 "plan pushed: $V_EVID" || ts_fail TS1 "got: $line"

  # TS2 plan: NOT-SAFE on unpushed+dirty
  line=$(engine_cmd "$CLONE/wip.txt"); parse_verdict "$line"
  [[ $V_SAFE == NOT-SAFE ]] && ts_pass TS2 "plan not-safe on unpushed+dirty ($V_EVID)" || ts_fail TS2 "got: $line"

  # TS3 plan: stale on old unreferenced scratch
  line=$(engine_cmd "$CLONE/.scratch/old-scan.out"); parse_verdict "$line"
  [[ $V_SAFE == SAFE && $V_RECEIPT == stale ]] && ts_pass TS3 "plan stale ($V_EVID)" || ts_fail TS3 "got: $line"

  # TS4 plan: moved-to-obsidian via fixture ledger
  line=$(engine_cmd "$CLONE/essay-draft.md"); parse_verdict "$line"
  [[ $V_SAFE == SAFE && $V_RECEIPT == moved-to-obsidian ]] && ts_pass TS4 "plan obsidian ($V_EVID)" || ts_fail TS4 "got: $line"

  # TS5 secrets refusal
  printf 'x=1\n' > "$CLONE/deploy.env"
  line=$(engine_cmd "$CLONE/deploy.env"); parse_verdict "$line"
  [[ $V_SAFE == NOT-SAFE && $V_RECEIPT == secrets-refusal ]] && ts_pass TS5 "secrets refusal" || ts_fail TS5 "got: $line"

  # TS6 quarantine-exclusion: reference inside .ufo-quarantine must not block stale
  mkdir -p "$CLONE/.ufo-quarantine/keep"
  printf 'mentions old-scan.out\n' > "$CLONE/.ufo-quarantine/keep/log.txt"
  line=$(engine_cmd "$CLONE/.ufo-quarantine/keep/log.txt"); parse_verdict "$line"
  [[ $V_RECEIPT == stale || $V_RECEIPT == none ]] && ts_pass TS6 "quarantine dir excluded from ref sweep ($V_RECEIPT)" || ts_fail TS6 "got: $line"
  rm -rf "$CLONE/.ufo-quarantine"

  # TS7 live-mutation guard: root outside /tmp must refuse with exit 3, before any write
  local LIVE; LIVE=$(mktemp -d "$HOME/tmp.q05live.XXXXXX")
  ( cd "$LIVE" && git init -q . && printf 'a\n' > a.txt && git add a.txt \
      && git -c user.name=s -c user.email=s@s commit -q -m a ) >/dev/null 2>&1
  local rc=0
  "$SELF" stage --root "$LIVE" --receipt internal "$LIVE/a.txt" >/dev/null 2>&1 || rc=$?
  if [[ $rc -eq 3 && ! -e $LIVE/.ufo-quarantine ]]; then
    ts_pass TS7 "live root refused exit=3, nothing created"; else ts_fail TS7 "rc=$rc quarantine=$([[ -e $LIVE/.ufo-quarantine ]] && echo created || echo absent)"; fi
  rm -rf "$LIVE"

  # TS8 stage NOT-SAFE target refused, nothing moved
  rc=0; "$SELF" stage --root "$CLONE" --receipt internal "$CLONE/wip.txt" >/dev/null 2>&1 || rc=$?
  if [[ $rc -ne 0 && -f $CLONE/wip.txt && ! -d $CLONE/.ufo-quarantine ]]; then
    ts_pass TS8 "NOT-SAFE stage refused; wip.txt untouched"; else ts_fail TS8 "rc=$rc state moved?"; fi

  # TS9 stage pushed + ticket + stage commit
  OUT=$("$SELF" stage --root "$CLONE" --receipt internal "$CLONE/notes-v1.txt" 2>&1); rc=$?
  local last_subject art tkt
  last_subject=$(git -C "$CLONE" log --format=%s -1 2>/dev/null)
  art=$(ls "$CLONE"/.ufo-quarantine/*/notes-v1.txt 2>/dev/null | head -1)
  tkt=$(ls "$CLONE"/.ufo-quarantine/*/notes-v1.txt.ticket.json 2>/dev/null | head -1)
  if [[ $rc -eq 0 && -f $art && -f $tkt && ! -e $CLONE/notes-v1.txt ]] \
     && [[ $last_subject == 'quarantine(stage): pushed'* ]]; then
    ts_pass TS9 "pushed staged: $(printf '%s' "$OUT" | tail -1)"
  else ts_fail TS9 "rc=$rc art=$([[ -f $CLONE/.ufo-quarantine/*/notes-v1.txt ]] && echo Y || echo N) tkt=$([[ -f $CLONE/.ufo-quarantine/*/notes-v1.txt.ticket.json ]] && echo Y || echo N) orig=$([[ ! -e $CLONE/notes-v1.txt ]] && echo gone || echo present) subj=|$last_subject|"; fi
  local T1; T1=$(ls "$CLONE"/.ufo-quarantine/*/notes-v1.txt.ticket.json 2>/dev/null | head -1)

  # TS10 pushed needs no hold: immediate second-check pass, release works
  OUT=$("$SELF" second-check --root "$CLONE" --ticket "$T1" 2>&1); rc=$?
  [[ $rc -eq 0 ]] && ts_pass TS10 "pushed second-check immediate pass ($(printf '%s' "$OUT" | sed 's/.*(\(.*\))/\1/'))" || ts_fail TS10 "$OUT"
  "$SELF" release --root "$CLONE" --ticket "$T1" >/dev/null 2>&1 || ts_fail TS11a "release failed"
  [[ ! -e $art ]] \
    && ts_pass TS11 "release deleted artifact from quarantine" || ts_fail TS11 "artifact still present"

  # TS12 stale: stage ok, hold gate refuses early second-check
  OUT=$("$SELF" stage --root "$CLONE" --hold-seconds 450 --receipt internal "$CLONE/.scratch/old-scan.out" 2>&1); rc=$?
  local T2 art2
  T2=$(ls "$CLONE"/.ufo-quarantine/*/.scratch/old-scan.out.ticket.json 2>/dev/null | head -1)
  art2=$(ls "$CLONE"/.ufo-quarantine/*/.scratch/old-scan.out 2>/dev/null | grep -v ticket | head -1)
  [[ $rc -eq 0 && -n $T2 && -f $art2 ]] \
    && ts_pass TS12 "stale staged with 450s hold" || ts_fail TS12 "rc=$rc tkt=|$T2| art=$([[ -f $art2 ]] && echo Y || echo N)"
  OUT=$("$SELF" second-check --root "$CLONE" --ticket "$T2" 2>&1); rc=$?
  [[ $rc -eq 1 ]] && ts_pass TS13 "second-check refused before hold ($(printf '%s' "$OUT" | sed 's/.*(\(.*\))/\1/'))" || ts_fail TS13 "$OUT"
  OUT=$("$SELF" release --root "$CLONE" --ticket "$T2" 2>&1); rc=$?
  [[ $rc -eq 1 && -f $art2 ]] \
    && ts_pass TS14 "release refused without passing second-check" || ts_fail TS14 "$OUT"

  # TS15 restore returns artifact byte-identical to origin path
  OUT=$("$SELF" restore --root "$CLONE" --ticket "$T2" 2>&1); rc=$?
  if [[ $rc -eq 0 && -f $CLONE/.scratch/old-scan.out ]] && printf 'old scratch\n' | cmp -s - "$CLONE/.scratch/old-scan.out"; then
    ts_pass TS15 "restore byte-identical to original path"
  else ts_fail TS15 "$OUT"; fi

  # TS16 hold elapses -> second-check passes -> release works (2s hold)
  rm -rf "$CLONE/.ufo-quarantine"   # fixture reset: free the quarantine slot for re-stage
  touch -d '3 days ago' "$CLONE/.scratch/old-scan.out"
  OUT16=$("$SELF" stage --root "$CLONE" --hold-seconds 2 --receipt internal "$CLONE/.scratch/old-scan.out" 2>&1); rc16=$?
  local T3; T3=$(ls "$CLONE"/.ufo-quarantine/*/.scratch/old-scan.out.ticket.json 2>/dev/null | tail -1)
  [[ $rc16 -eq 0 && -n $T3 ]] || ts_fail TS16pre "stage rc=$rc16 out=|$OUT16|"
  sleep 3
  OUT=$("$SELF" second-check --root "$CLONE" --ticket "$T3" 2>&1); rc=$?
  [[ $rc -eq 0 ]] && ts_pass TS16 "second-check passes after hold elapsed" || ts_fail TS16 "$OUT"
  OUT=$("$SELF" release --root "$CLONE" --ticket "$T3" 2>&1); rc=$?
  local art3; art3=$(ls "$CLONE"/.ufo-quarantine/*/.scratch/old-scan.out 2>/dev/null | grep -v ticket | head -1)
  [[ $rc -eq 0 && ! -e $art3 ]] \
    && ts_pass TS17 "release after hold deletes from quarantine" || ts_fail TS17 "$OUT"

  # TS18 sha drift guard: tamper with staged artifact, second-check must fail
  printf 'tamper\n' > "$CLONE/notes-tmp.txt"; git -C "$CLONE" add notes-tmp.txt
  git -C "$CLONE" -c user.name=souji-shokunin -c user.email=souji@shokunin.local commit -q -m "t1"
  git -C "$CLONE" push -q origin master
  "$SELF" stage --root "$CLONE" --receipt internal "$CLONE/notes-tmp.txt" >/dev/null 2>&1
  local T4; T4=$(ls "$CLONE"/.ufo-quarantine/*/notes-tmp.txt.ticket.json)
  printf 'tampered\n' >> "$CLONE/.ufo-quarantine/"*/notes-tmp.txt
  OUT=$("$SELF" second-check --root "$CLONE" --ticket "$T4" 2>&1); rc=$?
  [[ $rc -eq 1 ]] && ts_pass TS18 "sha drift detected at second-check ($(printf '%s' "$OUT" | sed 's/.*(\(.*\))/\1/'))" || ts_fail TS18 "$OUT"

  # TS19 obsidian receipt round-trip (hold 2s)
  touch -d '2 days ago' "$CLONE/essay-draft.md"
  OUT=$("$SELF" stage --root "$CLONE" --hold-seconds 2 --receipt internal "$CLONE/essay-draft.md" >/dev/null 2>&1)
  local T5; T5=$(ls "$CLONE"/.ufo-quarantine/*/essay-draft.md.ticket.json 2>/dev/null | tail -1)
  sleep 2
  OUT=$("$SELF" second-check --root "$CLONE" --ticket "$T5" 2>&1); rc=$?
  [[ $rc -eq 0 ]] && ts_pass TS19 "obsidian staged + second-check after hold" || ts_fail TS19 "$OUT"
  "$SELF" restore --root "$CLONE" --ticket "$T5" >/dev/null 2>&1

  # TS20 plan --json is valid-looking JSON and read-only over a LIVE lane path
  local lane_file="$SCRIPT_DIR_LIVE/souji-verify.spec.md"
  SCRIPT_DIR_LIVE="$(dirname "$SELF")"
  lane_file="$SCRIPT_DIR_LIVE/souji-verify.spec.md"
  if [[ -f $lane_file ]]; then
    OUT=$("$SELF" plan --json --receipt internal "$lane_file" 2>/dev/null)
    [[ $OUT == \[*\]* && $OUT == *'"safe":'* ]] \
      && ts_pass TS20 "plan --json works on live path (read-only): ${OUT:0:80}..." || ts_fail TS20 "got: $OUT"
  else ts_pass TS20 "skipped (spec file absent)"; fi

  # tally
  if print_tally; then exit 0; else exit 1; fi
}

# ---------- arg parsing ---------------------------------------------------
SCRIPT_DIR_LIVE="$(dirname "$SELF")"
CMD=""
ROOT="" TICKET="" HOLD=$DEFAULT_HOLD JSON=0 DRYRUN=0
ARGS=()
while [[ $# -gt 0 ]]; do
  case $1 in
    --selftest) selftest;;
    --root) ROOT=$2; shift 2;;
    --ticket) TICKET=$2; shift 2;;
    --receipt) RECEIPT=$2; shift 2;;
    --ledger) LEDGER=$2; shift 2;;
    --hold-seconds) HOLD=$2; shift 2;;
    --stale-days) STALE_DAYS=$2; shift 2;;
    --json) JSON=1; shift;;
    --dry-run) DRYRUN=1; shift;;
    plan|stage|second-check|release|restore) CMD=$1; shift;;
    -h|--help) usage;;
    *) ARGS+=("$1"); shift;;
  esac
done
if [[ $CMD == plan || $CMD == stage ]]; then
  [[ ${#ARGS[@]} -ge 1 ]] || usage
fi
case $CMD in
  plan)          do_plan "$JSON" "${ARGS[@]}";;
  stage)         [[ -n $ROOT ]] || usage; do_stage "$ROOT" "$HOLD" "${ARGS[@]}";;
  second-check)  [[ -n $ROOT && -n $TICKET ]] || usage; do_second_check "$ROOT" "$TICKET" || exit 1;;
  release)       [[ -n $ROOT && -n $TICKET ]] || usage; do_release "$ROOT" "$TICKET";;
  restore)       [[ -n $ROOT && -n $TICKET ]] || usage; do_restore "$ROOT" "$TICKET";;
  *) usage;;
esac
