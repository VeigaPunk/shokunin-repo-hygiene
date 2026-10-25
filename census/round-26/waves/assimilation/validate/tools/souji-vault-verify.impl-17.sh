#!/usr/bin/env bash
# souji-vault-verify (impl-17) — ledger-backed moved-to-obsidian verification
# with read-only vault confirmation. souji-shokunin round 4, seat S17.
#
# The ledger (corpus/knowledge/obsidian-ledger.tsv; columns source_path,
# source_sha256, vault_path, vault_sha256, exported_at, note) is the receipt
# of record. A row verifies only when BOTH sides re-hash to the recorded
# values: the source path and the vault path (files via sha256sum, read-only;
# directories via a sorted sha256 manifest digest). The official Obsidian CLI
# is advisory at most — never the receipt — and this tool NEVER executes the
# GUI launcher binary (which would start the desktop app on this host) nor
# any entry whose basename is `obsidian`.
#
# CLI
#   tools/souji-vault-verify.impl-17.sh [--ledger PATH] [--vault PATH]
#        [--cli|--fallback|--auto] [--json] [--stale-days N] [--selftest]
#        [--] <source-path>...
#
# Output, two lines per target (default mode):
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt|none<TAB>evidence   (r2 form)
#   VERIFIED(<receipt>) | NOT-VERIFIED(<reason>)                       (r4 form)
# --json prints one JSON object per target and nothing else.
#
# Modes:
#   --auto (default): read census/round-4/cli-contract.json. If the contract
#     verdict is CLI-USABLE the CLI entry point is probed; the CLI hash and
#     the sha256sum fallback hash must agree, else NOT-VERIFIED
#     (cli-disagreement). Otherwise the sha256sum fallback alone decides.
#   --fallback: never probe the CLI (evidence cli=off).
#   --cli: force a probe. SOUJI_CLI_BIN wins over the contract entry point.
#     An unusable CLI (absent/timeout/error/empty/garbage) degrades to the
#     sha256sum fallback with cli=<state> in the evidence — never silently
#     ignored, never a verdict of its own.
#
# Reasons (NOT-VERIFIED): source-absent, source-hash, vault-absent,
# vault-hash-mismatch, none, no-ledger, source-equals-vault, secrets-refusal,
# unreachable, row-incomplete, cli-disagreement.
#
# Exit codes: 0 = every target evaluated (VERIFIED or NOT-VERIFIED);
#             1 = internal error; 2 = usage. No other codes.
#
# Safety rails
#   * Read-only: the vault and the ledger are only ever read (sha256sum/stat/
#     find/readlink). Nothing is written outside /tmp scratch.
#   * The GUI launcher path and the bare `obsidian` name are NEVER executed;
#     no PATH lookup of a bare `obsidian` name happens at all.
#   * Secret-shaped basenames (*.env, .env.*, .envrc, *credential*, *secret*,
#     id_*, *.pem) are refused before anything is read.
#   * No git commands; no network.
#
# Env overrides: SOUJI_LEDGER, SOUJI_CLI_BIN, SOUJI_CLI_TIMEOUT,
# SOUJI_CONTRACT, SOUJI_VAULT (advisory), SOUJI_SELFTEST_ACTIVE.
set -euo pipefail
export LC_ALL=C

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

LEDGER="${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}"
VAULT_HINT="${SOUJI_VAULT:-}"
CONTRACT="${SOUJI_CONTRACT:-$REPO_ROOT/census/round-4/cli-contract.json}"
CLI_TIMEOUT="${SOUJI_CLI_TIMEOUT:-6}"
MODE=auto
JSON=0
SELFTEST=0
STALE_DAYS=1
TARGETS=()

CLI_ENTRY=""
CLI_STATE=""

R_CLASS=NOT-VERIFIED
R_REASON=none
R_RECEIPT=none
R_EVIDENCE="no-evaluation"

usage() {
  printf 'usage: %s [--ledger PATH] [--vault PATH] [--cli|--fallback|--auto]\n' \
    "$(basename -- "$SELF")"
  printf '       [--json] [--stale-days N] [--selftest] [--] <source-path>...\n'
}

# ---------------------------------------------------------------- helpers --

san() { # escape tabs/newlines/CRs so one record stays one line
  local s=${1:-}
  s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; s=${s//$'\r'/}
  printf '%s' "$s"
}

jesc() {
  local s=${1:-} out='' i c
  for ((i = 0; i < ${#s}; i++)); do
    c=${s:i:1}
    case "$c" in
      '"') out+='\"' ;;
      '\') out+='\\' ;;
      $'\n') out+='\n' ;;
      $'\r') out+='\r' ;;
      $'\t') out+='\t' ;;
      *) out+=$c ;;
    esac
  done
  printf '%s' "$out"
}

canon() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }
short() { printf '%s' "${1:0:12}"; }

file_sha() {
  sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1 || true
}

dir_digest() { # sorted sha256 manifest digest, identical to the r2 recipe
  ( cd -- "$1" 2>/dev/null && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum 2>/dev/null \
      | sha256sum | cut -d' ' -f1 ) 2>/dev/null || true
}

hash_for() { # path isdir
  if [ "$2" = 1 ]; then dir_digest "$1"; else file_sha "$1"; fi
}

secret_shape() {
  local b
  b=$(basename -- "${1:-}" 2>/dev/null || true)
  case "$b" in
    *.env | .env.* | .envrc | *.envrc | *credential* | *secret* | id_* | *.pem) return 0 ;;
  esac
  return 1
}

# --------------------------------------------------------- CLI contract ----

contract_state() { # prints "<usable|not-usable><TAB><value>"
  if [ ! -f "$CONTRACT" ]; then printf 'not-usable\tmissing'; return 0; fi
  if ! command -v python3 >/dev/null 2>&1; then
    printf 'not-usable\tno-python3'; return 0
  fi
  python3 - "$CONTRACT" <<'PY' 2>/dev/null || printf 'not-usable\tunreadable'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("not-usable\tunreadable")
    raise SystemExit
v = str(d.get("verdict") or "")
e = d.get("entry_point")
if "CLI-USABLE" in v.upper() and isinstance(e, str) and e:
    print("usable\t" + e)
else:
    print("not-usable\t" + (v or "unknown"))
PY
}

init_cli() {
  CLI_ENTRY=""
  CLI_STATE=""
  if [ "$MODE" = fallback ]; then CLI_STATE=off; return 0; fi
  local e=""
  if [ "$MODE" = cli ] && [ -n "${SOUJI_CLI_BIN:-}" ] \
     && [ -f "${SOUJI_CLI_BIN}" ] && [ -x "${SOUJI_CLI_BIN}" ]; then
    e=$SOUJI_CLI_BIN
  fi
  if [ -z "$e" ]; then
    local line cst cval
    line=$(contract_state)
    cst=${line%%$'\t'*}
    cval=${line#*$'\t'}
    if [ "$cst" = usable ]; then
      e=$cval
    elif [ "$MODE" = auto ]; then
      CLI_STATE=fallback-only
    else
      CLI_STATE=unavailable
    fi
  fi
  if [ -n "$e" ]; then
    # Refuse the GUI launcher: its basename is the bare app name. The
    # app-bundle directory prefix is refused as well.
    case "$(basename -- "$e")" in obsidian) e=""; CLI_STATE=hazard-refused ;; esac
    case "$e" in /usr/lib/obsidian/*) e=""; CLI_STATE=hazard-refused ;; esac
    if [ -n "$e" ] && { [ ! -x "$e" ] || [ ! -f "$e" ]; }; then
      e=""; CLI_STATE=unavailable
    fi
  fi
  CLI_ENTRY=$e
  [ -n "$CLI_STATE" ] || CLI_STATE=unknown
  return 0
}

cli_probe_hash() { # vault-path -> "<state><TAB><hash-or-empty>"
  local vp=$1 out rc=0
  out=$(timeout "$CLI_TIMEOUT" "$CLI_ENTRY" hash "$vp" 2>/dev/null) || rc=$?
  if [ "$rc" = 124 ] || [ "$rc" = 137 ]; then printf 'timeout\t'; return 0; fi
  if [ "$rc" != 0 ]; then printf 'error\t'; return 0; fi
  if [ -z "$out" ]; then printf 'empty\t'; return 0; fi
  local h
  h=$(printf '%s\n' "$out" | grep -oE '[0-9a-fA-F]{64}' | head -1 | tr 'A-F' 'a-f' || true)
  if [ -n "$h" ]; then printf 'ok\t%s' "$h"; else printf 'garbage\t'; fi
  return 0
}

# ---------------------------------------------------------------- verify ---

eval_row() { # target canon sp ss vp vs note ledger_used mode_tag
  local target=$1 ct=$2 sp=$3 ss=$4 vp=$5 vs=$6 note=$7 lused=$8 mtag=$9
  R_CLASS=NOT-VERIFIED
  R_RECEIPT=none
  local vpc
  vpc=$(canon "$vp")
  if [ "$vpc" = "$ct" ]; then
    R_REASON=source-equals-vault
    R_EVIDENCE="source-equals-vault vault=$(san "$vp") ledger=$(san "$lused") $mtag"
    return 0
  fi
  if secret_shape "$vp"; then
    R_REASON=secrets-refusal
    R_EVIDENCE="secret-shaped vault=$(san "$vp") ledger=$(san "$lused") $mtag"
    return 0
  fi
  if [ -z "${ss:-}" ] || [ -z "${vs:-}" ]; then
    R_REASON=row-incomplete
    R_EVIDENCE="row-incomplete ledger=$(san "$lused") $mtag"
    return 0
  fi
  if [ ! -e "$target" ]; then
    R_REASON=source-absent
    R_EVIDENCE="source-unreachable source-absent source=$(san "$target") ledger=$(san "$lused") $mtag"
    return 0
  fi
  local isdir=0
  [ -d "$target" ] && isdir=1
  local act_s
  act_s=$(hash_for "$target" "$isdir")
  if [ -z "$act_s" ]; then
    R_REASON=source-absent
    R_EVIDENCE="source-unreadable source-absent source=$(san "$target") ledger=$(san "$lused") $mtag"
    return 0
  fi
  if [ "$act_s" != "$ss" ]; then
    R_REASON=source-hash
    R_EVIDENCE="source-sha-mismatch source-hash-mismatch ledger-sha=$(short "$ss") actual-sha=$(short "$act_s") ledger=$(san "$lused") $mtag"
    return 0
  fi
  if [ ! -e "$vp" ]; then
    R_REASON=vault-absent
    R_EVIDENCE="vault-unreachable vault-absent vault=$(san "$vp") ledger=$(san "$lused") $mtag"
    return 0
  fi
  local vdir=0
  [ -d "$vp" ] && vdir=1
  if [ "$vdir" != "$isdir" ]; then
    R_REASON=vault-absent
    R_EVIDENCE="vault-unreachable vault-kind-mismatch vault-absent vault=$(san "$vp") ledger=$(san "$lused") $mtag"
    return 0
  fi
  if [ "$isdir" = 0 ]; then
    local rt rv
    rt=$(readlink -f -- "$target" 2>/dev/null || true)
    rv=$(readlink -f -- "$vp" 2>/dev/null || true)
    if [ -n "$rt" ] && [ "$rt" = "$rv" ]; then
      R_REASON=source-equals-vault
      R_EVIDENCE="source-equals-vault symlink-alias vault=$(san "$vp") ledger=$(san "$lused") $mtag"
      return 0
    fi
    local it iv
    it=$(stat -c '%d:%i' -- "$target" 2>/dev/null || true)
    iv=$(stat -c '%d:%i' -- "$vp" 2>/dev/null || true)
    if [ -n "$it" ] && [ "$it" = "$iv" ]; then
      R_REASON=source-equals-vault
      R_EVIDENCE="source-equals-vault hardlink-alias vault=$(san "$vp") ledger=$(san "$lused") $mtag"
      return 0
    fi
  else
    case "$vpc" in
      "$ct"/*)
        R_REASON=source-equals-vault
        R_EVIDENCE="source-equals-vault vault-nested-in-source vault=$(san "$vp") ledger=$(san "$lused") $mtag"
        return 0
        ;;
    esac
  fi
  local act_v
  act_v=$(hash_for "$vp" "$vdir")
  if [ -z "$act_v" ]; then
    R_REASON=vault-absent
    R_EVIDENCE="vault-unreadable vault-absent vault=$(san "$vp") ledger=$(san "$lused") $mtag"
    return 0
  fi
  if [ "$isdir" = 0 ] && [ -n "$CLI_ENTRY" ]; then
    local st cst ch
    st=$(cli_probe_hash "$vp")
    cst=${st%%$'\t'*}
    ch=${st#*$'\t'}
    case "$cst" in
      ok)
        if [ -n "$ch" ] && [ "$ch" != "$act_v" ]; then
          R_REASON=cli-disagreement
          R_EVIDENCE="cli-disagreement cli-sha=$(short "$ch") fallback-sha=$(short "$act_v") vault=$(san "$vp") ledger=$(san "$lused") mode=$MODE cli=disagreement"
          return 0
        fi
        mtag="mode=$MODE cli=ok"
        ;;
      timeout) mtag="mode=$MODE cli=timeout" ;;
      error) mtag="mode=$MODE cli=error" ;;
      empty) mtag="mode=$MODE cli=empty" ;;
      garbage) mtag="mode=$MODE cli=garbage" ;;
      *) mtag="mode=$MODE cli=unavailable" ;;
    esac
  fi
  if [ "$act_v" != "$vs" ]; then
    R_REASON=vault-hash-mismatch
    R_EVIDENCE="vault-sha-mismatch vault-hash-mismatch vault=$(san "$vp") ledger-sha=$(short "$vs") actual-sha=$(short "$act_v") ledger=$(san "$lused") $mtag"
    return 0
  fi
  note=${note%$'\r'}
  if [ "$isdir" = 1 ]; then
    R_EVIDENCE="ledger-row vault=$(san "$vp") source-digest=$(short "$act_s") vault-digest=$(short "$act_v") note=$(san "$note") ledger=$(san "$lused") $mtag"
  else
    R_EVIDENCE="ledger-row vault=$(san "$vp") source-sha256=$(short "$act_s") note=$(san "$note") ledger=$(san "$lused") $mtag"
  fi
  R_CLASS=VERIFIED
  R_RECEIPT=moved-to-obsidian
  R_REASON=moved-to-obsidian
  return 0
}

verify_target() {
  local target=$1
  R_CLASS=NOT-VERIFIED
  R_REASON=none
  R_RECEIPT=none
  R_EVIDENCE=""
  local mtag="mode=$MODE cli=${CLI_STATE:-unknown}"
  if [ -z "$target" ]; then
    R_REASON=unreachable
    R_EVIDENCE="empty-target $mtag"
    return 0
  fi
  if secret_shape "$target"; then
    R_REASON=secrets-refusal
    R_EVIDENCE="secret-shaped source=$(san "$target") $mtag"
    return 0
  fi
  if [ ! -f "$LEDGER" ]; then
    R_REASON=no-ledger
    R_EVIDENCE="no-ledger ledger=$(san "$LEDGER") $mtag"
    return 0
  fi
  local lused
  lused=$(readlink -f -- "$LEDGER" 2>/dev/null || printf '%s' "$LEDGER")
  local ct
  ct=$(canon "$target")
  local found=0 first_reason="" first_ev=""
  local row sp ss vp vs ea note extra
  while IFS= read -r row || [ -n "$row" ]; do
    [ -n "$row" ] || continue
    case "$row" in source_path$'\t'*) continue ;; esac
    IFS=$'\t' read -r sp ss vp vs ea note extra <<<"$row"
    [ -n "${sp:-}" ] || continue
    [ "$(canon "$sp")" = "$ct" ] || continue
    found=1
    eval_row "$target" "$ct" "$sp" "$ss" "$vp" "$vs" "${note:-}" "$lused" "$mtag"
    if [ "$R_CLASS" = VERIFIED ]; then return 0; fi
    if [ -z "$first_reason" ]; then
      first_reason=$R_REASON
      first_ev=$R_EVIDENCE
    fi
  done <"$LEDGER"
  if [ "$found" = 0 ]; then
    R_REASON=none
    R_EVIDENCE="no-matching-ledger-row ledger=$(san "$lused") $mtag"
  else
    R_REASON=$first_reason
    R_EVIDENCE=$first_ev
  fi
  return 0
}

emit_record() {
  local t=$1 sp
  sp=$(san "$t")
  if [ "$JSON" = 1 ]; then
    printf '{"path":"%s","verdict":"%s","reason":"%s","receipt":"%s","evidence":"%s"}\n' \
      "$(jesc "$t")" "$R_CLASS" "$(jesc "$R_REASON")" "$(jesc "$R_RECEIPT")" \
      "$(jesc "$R_EVIDENCE")"
    return 0
  fi
  if [ "$R_CLASS" = VERIFIED ]; then
    printf 'VERDICT\t%s\tSAFE\t%s\t%s\n' "$sp" "$R_RECEIPT" "$(san "$R_EVIDENCE")"
    printf 'VERIFIED(%s)\n' "$R_RECEIPT"
  else
    # r2-parity evidence token: consumers (runner-37 et al.) grep for
    # `obsidian=<ground-of-refusal>` on the negative path.
    printf 'VERDICT\t%s\tNOT-SAFE\tnone\tobsidian=%s %s\n' \
      "$sp" "$R_REASON" "$(san "$R_EVIDENCE")"
    printf 'NOT-VERIFIED(%s)\n' "$R_REASON"
  fi
  return 0
}

# --------------------------------------------------------------- selftest --

ST_TMP=""
ST_CHECKS=0
ST_FAILS=0
ST_NOTES=0

st_cleanup() {
  if [ -n "${ST_TMP:-}" ]; then rm -rf -- "$ST_TMP"; fi
  return 0
}

st_note() {
  ST_NOTES=$((ST_NOTES + 1))
  printf '  note: %s\n' "$*"
}

st_case() { # id want-r4 ev-substr ; then [env assignments] -- args...
  local id=$1 want=$2 ev=$3
  shift 3
  local -a envs=() args=()
  while [ $# -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  [ $# -gt 0 ] && shift
  args=("$@")
  local o rc=0
  o=$(env "${envs[@]}" SOUJI_SELFTEST_ACTIVE=1 timeout 60 bash "$SELF" "${args[@]}" 2>&1) || rc=$?
  ST_CHECKS=$((ST_CHECKS + 1))
  local got ok=1 why=""
  got=$(printf '%s\n' "$o" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -1 || true)
  [ "$got" = "$want" ] || { ok=0; why="verdict '$got' != '$want'"; }
  if [ "$ok" = 1 ] && [ -n "$ev" ] && ! printf '%s' "$o" | grep -qF -- "$ev"; then
    ok=0; why="evidence '$ev' missing"
  fi
  if [ "$rc" -ne 0 ]; then ok=0; why="${why:+$why; }rc=$rc"; fi
  if [ "$ok" = 1 ]; then
    printf 'PASS %s: %s\n' "$id" "$got"
  else
    ST_FAILS=$((ST_FAILS + 1))
    printf 'FAIL %s: %s\n' "$id" "$why"
    printf '%s\n' "$o" | sed 's/^/    | /'
  fi
  return 0
}

st_live_phase() {
  local case_dir builder out led exp rc got o rcx
  local cid lgr tgt wcls wrsn gcls grsn ok
  local -a lrows=()
  mkdir -p -- "$ST_TMP/live"
  for case_dir in "$REPO_ROOT"/tests/vault/case-V*; do
    [ -d "$case_dir" ] || continue
    builder=""
    for cand in make-fixture.sh build.sh; do
      [ -f "$case_dir/$cand" ] && { builder="$case_dir/$cand"; break; }
    done
    if [ -z "$builder" ]; then
      st_note "live $(basename -- "$case_dir"): no builder — skipped"
      continue
    fi
    out="$ST_TMP/live/$(basename -- "$case_dir")"
    led="$ST_TMP/live/$(basename -- "$case_dir")-ledger.tsv"
    rc=0
    timeout 120 bash "$builder" --out "$out" --ledger "$led" --quiet \
      >"$ST_TMP/live/$(basename -- "$case_dir").builder.out" 2>&1 || rc=$?
    if [ "$rc" -ne 0 ]; then
      st_note "live $(basename -- "$case_dir"): builder rc=$rc — skipped"
      continue
    fi
    exp="$out/expected.json"
    [ -f "$exp" ] || exp="$case_dir/expected.json"
    if [ ! -f "$exp" ]; then
      st_note "live $(basename -- "$case_dir"): no expected.json — skipped"
      continue
    fi
    : >"$ST_TMP/live/$(basename -- "$case_dir").rows.tsv"
    if ! python3 - "$exp" "$out" >"$ST_TMP/live/$(basename -- "$case_dir").rows.tsv" 2>"$ST_TMP/live/$(basename -- "$case_dir").rows.err" <<'PY'
import json, os, re, sys

exp, out = sys.argv[1], sys.argv[2]

def sub(s):
    return str(s).replace("@FIXTURE_ROOT@", out)

try:
    doc = json.load(open(exp))
except Exception as e:
    print("PARSE-ERROR", e, file=sys.stderr)
    raise SystemExit(1)

def norm_reason(v, rs):
    if not isinstance(v, str):
        return str(v or ""), str(rs or "")
    u = v.strip().upper().replace("NOT_VERIFIED", "NOT-VERIFIED").replace("NOT VERIFIED", "NOT-VERIFIED")
    if u.startswith("NOT-VERIFIED") or u.startswith("NOT-SAFE"):
        cls = "NOT-VERIFIED"
    elif u.startswith("VERIFIED") or u.startswith("SAFE"):
        cls = "VERIFIED"
    else:
        cls = u
    reason = str(rs or "")
    if not reason:
        m = re.search(r"\((.*)\)\s*$", v)
        if m:
            reason = m.group(1).strip()
    return cls, reason

rows = []
probes = doc.get("probes")
if isinstance(probes, list) and probes:
    for pr in probes:
        if not isinstance(pr, dict):
            continue
        t = pr.get("target")
        if not t:
            continue
        t = sub(t)
        if not os.path.isabs(t):
            t = os.path.join(out, t)
        lg = pr.get("ledger")
        if lg:
            lg = sub(lg)
            if not os.path.isabs(lg):
                lg = os.path.join(out, lg)
        cls, rsn = norm_reason(pr.get("verdict"), pr.get("reason"))
        rows.append((str(pr.get("id") or "probe"), lg or "-", t, cls, rsn))
else:
    targets = doc.get("targets") or []
    expect = doc.get("expect")
    if isinstance(expect, dict):
        expect = [expect]
    if not isinstance(expect, list):
        expect = []
    bypath = {}
    for e in expect:
        if isinstance(e, dict) and e.get("path"):
            bypath[sub(e["path"])] = e
    prim = doc.get("primary_target")
    if isinstance(prim, str):
        prim = sub(prim)
    pairs = []
    for t in targets:
        if isinstance(t, dict):
            tp = t.get("path")
            e = t.get("expected") if isinstance(t.get("expected"), dict) else {}
        else:
            tp, e = t, {}
        if not tp:
            continue
        tp = sub(tp)
        if not os.path.isabs(tp):
            tp = os.path.join(out, tp)
        if not e:
            e = bypath.get(tp) or {}
        if not e and len(expect) == 1:
            e = expect[0]
        pairs.append((tp, e))
    if not pairs and prim:
        e = bypath.get(prim) or (expect[0] if len(expect) == 1 else {})
        pairs = [(prim, e)]
    if prim:
        pairs.sort(key=lambda p: 0 if p[0] == prim else 1)
    for tp, e in pairs:
        wv = e.get("verdict") if isinstance(e, dict) else None
        wr = e.get("reason") if isinstance(e, dict) else None
        if wv is None and isinstance(e, dict) and isinstance(e.get("verdict_string"), str):
            wv = e["verdict_string"]
        cls, rsn = norm_reason(wv, wr)
        rows.append((os.path.basename(tp) or "target", "-", tp, cls, rsn))

if not rows:
    print("NO-ROWS", file=sys.stderr)
    raise SystemExit(1)
for r in rows:
    print("\t".join(r))
PY
    then
      st_note "live $(basename -- "$case_dir"): expected.json not parsed — skipped"
      continue
    fi
    while IFS=$'\t' read -r cid lgr tgt wcls wrsn; do
      [ -n "$cid" ] || continue
      [ "$lgr" = "-" ] && lgr="$led"
      rcx=0
      o=$(env SOUJI_SELFTEST_ACTIVE=1 timeout 60 bash "$SELF" \
        --ledger "$lgr" --fallback "$tgt" 2>&1) || rcx=$?
      got=$(printf '%s\n' "$o" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -1 || true)
      gcls=${got%%(*}
      grsn=""
      case "$got" in
        *"("*")"*) grsn=${got#*\(}; grsn=${grsn%\)} ;;
      esac
      ok=1
      if [ "$rcx" -ne 0 ] || [ -z "$got" ]; then ok=0; fi
      if [ "$ok" = 1 ] && [ "$gcls" != "$wcls" ]; then ok=0; fi
      if [ "$ok" = 1 ] && [ "$wcls" = NOT-VERIFIED ] && [ -n "$wrsn" ]; then
        local an_w an_g
        an_w=$(printf '%s' "$wrsn" | tr 'A-Z' 'a-z')
        an_w=${an_w//_/-}; an_w=${an_w//sha256/hash}; an_w=${an_w//sha/hash}; an_w=${an_w//digest/hash}
        an_g=$(printf '%s' "$grsn" | tr 'A-Z' 'a-z')
        an_g=${an_g//_/-}; an_g=${an_g//sha256/hash}; an_g=${an_g//sha/hash}; an_g=${an_g//digest/hash}
        case "$an_g" in
          *"$an_w"*) : ;;
          *)
            case "$an_w" in
              *"$an_g"*) : ;;
              *) ok=0 ;;
            esac
            ;;
        esac
      fi
      ST_CHECKS=$((ST_CHECKS + 1))
      if [ "$ok" = 1 ]; then
        printf 'PASS live %s/%s: %s\n' "$(basename -- "$case_dir")" "$cid" "$got"
      else
        ST_FAILS=$((ST_FAILS + 1))
        printf 'FAIL live %s/%s: got='%s' want=%s(%s) rc=%s\n' \
          "$(basename -- "$case_dir")" "$cid" "$got" "$wcls" "$wrsn" "$rcx"
      fi
    done <"$ST_TMP/live/$(basename -- "$case_dir").rows.tsv"
  done
  return 0
}

run_selftest() {
  if [ "${SOUJI_SELFTEST_ACTIVE:-}" = 1 ]; then
    printf 'souji-vault-verify: refusing nested --selftest\n' >&2
    return 1
  fi
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-vault-verify-selftest.XXXXXX")
  trap st_cleanup EXIT
  local st=$ST_TMP
  mkdir -p -- "$st/src" "$st/vault"

  local live_ledger_before live_ledger_after
  local LIVE_LEDGER_PATH="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"
  live_ledger_before=$(sha256sum -- "$LIVE_LEDGER_PATH" 2>/dev/null | cut -d' ' -f1 || true)
  local live_lines_before
  live_lines_before=$(wc -l <"$LIVE_LEDGER_PATH" 2>/dev/null || printf '0')

  # ---- fixtures: V1..V8 (mirror of tests/vault/ case semantics) + extras --
  local p1 p2 p3 p4 p5 p6 p6c p7 p8 p9 p13 p14 p14link
  p1=$st/src/v1.md
  printf 'V1 payload: clean pair\n' >"$p1"
  cp -- "$p1" "$st/vault/v1.md"
  p2=$st/src/v2.md
  printf 'V2 payload: vault edited after the row\n' >"$p2"
  cp -- "$p2" "$st/vault/v2.md"
  p3=$st/src/v3.md
  printf 'V3 payload: source edited after the row\n' >"$p3"
  cp -- "$p3" "$st/vault/v3.md"
  p4=$st/src/v4.md
  printf 'V4 payload: vault side never created\n' >"$p4"
  p5=$st/vault/v5.md
  printf 'V5 payload: source side never created\n' >"$p5"
  p6=$st/src/v6.md
  printf 'V6 payload: crlf ledger row\n' >"$p6"
  cp -- "$p6" "$st/vault/v6.md"
  p6c=$st/src/v6c.md
  printf 'V6c payload: crlf truncated row\n' >"$p6c"
  cp -- "$p6c" "$st/vault/v6c.md"
  p7=$st/src/v7.md
  printf 'V7 payload: extra columns ignored\n' >"$p7"
  cp -- "$p7" "$st/vault/v7.md"
  p8="$st/src/meeting notes 2026-10.md"
  printf 'V8 payload: space-bearing names\n' >"$p8"
  cp -- "$p8" "$st/vault/Meeting Notes 2026-10.md"
  p9=$st/src/v9.md
  printf 'V9 payload: no ledger row\n' >"$p9"
  p13=$st/src/v13.md
  printf 'V13 payload: self-move row\n' >"$p13"
  p14=$st/src/v14.md
  printf 'V14 payload: symlink alias row\n' >"$p14"
  p14link=$st/alias-link.md
  ln -s -- "$p14" "$p14link"
  printf 'not-a-secret fixture\n' >"$st/src/x.env"

  local v2_sha v3_sha
  v2_sha=$(file_sha "$p2")
  v3_sha=$(file_sha "$p3")

  # V2: row records the export-time bytes; the vault copy is edited after.
  printf 'EDIT AFTER ROW\n' >>"$st/vault/v2.md"
  # V3: row records the export-time bytes; the source is edited after.
  printf 'EDIT AFTER ROW\n' >>"$p3"

  local LED="$st/ledger.tsv"
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV1 clean pair\n' \
      "$p1" "$(file_sha "$p1")" "$st/vault/v1.md" "$(file_sha "$p1")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV2 vault edited\n' \
      "$p2" "$v2_sha" "$st/vault/v2.md" "$v2_sha"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV3 source edited\n' \
      "$p3" "$v3_sha" "$st/vault/v3.md" "$v3_sha"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV4 vault absent\n' \
      "$p4" "$(file_sha "$p4")" "$st/vault/v4-missing.md" "$(file_sha "$p4")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV5 source absent\n' \
      "$st/src/v5-missing.md" "$(file_sha "$p5")" "$p5" "$(file_sha "$p5")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV6 crlf row\r\n' \
      "$p6" "$(file_sha "$p6")" "$st/vault/v6.md" "$(file_sha "$p6")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV7 note text\textra-col\n' \
      "$p7" "$(file_sha "$p7")" "$st/vault/v7.md" "$(file_sha "$p7")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV8 spaces\n' \
      "$p8" "$(file_sha "$p8")" "$st/vault/Meeting Notes 2026-10.md" "$(file_sha "$p8")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV13 self-move\n' \
      "$p13" "$(file_sha "$p13")" "$p13" "$(file_sha "$p13")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tV14 symlink alias\n' \
      "$p14" "$(file_sha "$p14")" "$p14link" "$(file_sha "$p14")"
  } >"$LED"

  local LED6C="$st/ledger-6c.tsv"
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\r\n'
    printf '%s\t%s\t%s\t%s\r\n' \
      "$p6c" "$(file_sha "$p6c")" "$st/vault/v6c.md" "$(file_sha "$p6c")"
  } >"$LED6C"

  local LED0="$st/ledger-empty.tsv"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' >"$LED0"

  local MOCK="$st/mock-cli"
  cat >"$MOCK" <<'EOS'
#!/usr/bin/env bash
set -u
case "${MOCK_MODE:-ok}" in
  ok) h=$(sha256sum -- "${2:-/dev/null}" 2>/dev/null | cut -d' ' -f1); printf '{"ok":true,"sha256":"%s"}\n' "$h" ;;
  lie) printf '{"ok":true,"sha256":"%064d"}\n' 0 ;;
  hang) sleep 60 ;;
  err) printf 'mock: cli error\n' >&2; exit 3 ;;
  garbage) printf 'not-a-hash\n' ;;
  empty) exit 0 ;;
esac
EOS
  chmod +x -- "$MOCK"

  printf 'selftest fixtures under %s\n' "$st"

  # ---- V1..V8 + extras ---------------------------------------------------
  st_case "V1 clean pair" "VERIFIED(moved-to-obsidian)" "note=V1 clean pair" \
    -- --ledger "$LED" --fallback "$p1"
  st_case "V2 vault edited" "NOT-VERIFIED(vault-hash-mismatch)" "vault-sha-mismatch" \
    -- --ledger "$LED" --fallback "$p2"
  st_case "V3 source edited" "NOT-VERIFIED(source-hash)" "source-sha-mismatch" \
    -- --ledger "$LED" --fallback "$p3"
  st_case "V4 vault absent" "NOT-VERIFIED(vault-absent)" "vault-unreachable" \
    -- --ledger "$LED" --fallback "$p4"
  st_case "V5 source absent" "NOT-VERIFIED(source-absent)" "source-absent" \
    -- --ledger "$LED" --fallback "$st/src/v5-missing.md"
  st_case "V6 crlf valid row" "VERIFIED(moved-to-obsidian)" "ledger-row" \
    -- --ledger "$LED" --fallback "$p6"
  st_case "V6c crlf truncated row" "NOT-VERIFIED(vault-hash-mismatch)" "vault-sha-mismatch" \
    -- --ledger "$LED6C" --fallback "$p6c"
  st_case "V7 extra columns" "VERIFIED(moved-to-obsidian)" "V7 note text" \
    -- --ledger "$LED" --fallback "$p7"
  st_case "V8 space-bearing names" "VERIFIED(moved-to-obsidian)" "note=V8 spaces" \
    -- --ledger "$LED" --fallback "$p8"
  st_case "V9 no matching row" "NOT-VERIFIED(none)" "no-matching-ledger-row" \
    -- --ledger "$LED" --fallback "$p9"
  st_case "V10 header-only ledger" "NOT-VERIFIED(none)" "no-matching-ledger-row" \
    -- --ledger "$LED0" --fallback "$p1"
  st_case "V11 missing ledger" "NOT-VERIFIED(no-ledger)" "no-ledger" \
    -- --ledger "$st/does-not-exist.tsv" --fallback "$p1"
  st_case "V12 secrets refusal" "NOT-VERIFIED(secrets-refusal)" "secret-shaped" \
    -- --ledger "$LED" --fallback "$st/src/x.env"
  st_case "V13 self-move row" "NOT-VERIFIED(source-equals-vault)" "source-equals-vault" \
    -- --ledger "$LED" --fallback "$p13"
  st_case "V14 symlink alias row" "NOT-VERIFIED(source-equals-vault)" "source-equals-vault" \
    -- --ledger "$LED" --fallback "$p14"
  st_case "V15 fallback mode" "VERIFIED(moved-to-obsidian)" "cli=off" \
    -- --ledger "$LED" --fallback "$p1"
  st_case "V16 auto mode fallback-only contract" "VERIFIED(moved-to-obsidian)" "cli=fallback-only" \
    -- --ledger "$LED" --auto "$p1"
  st_case "V17 cli mode, honest mock" "VERIFIED(moved-to-obsidian)" "cli=ok" \
    SOUJI_CLI_BIN="$MOCK" MOCK_MODE=ok -- --ledger "$LED" --cli "$p1"
  st_case "V18 cli mode, lying mock" "NOT-VERIFIED(cli-disagreement)" "cli-disagreement" \
    SOUJI_CLI_BIN="$MOCK" MOCK_MODE=lie -- --ledger "$LED" --cli "$p1"
  st_case "V19 cli mode, hanging mock bounded" "VERIFIED(moved-to-obsidian)" "cli=timeout" \
    SOUJI_CLI_BIN="$MOCK" MOCK_MODE=hang SOUJI_CLI_TIMEOUT=2 -- --ledger "$LED" --cli "$p1"
  st_case "V20 cli mode, no entry point" "VERIFIED(moved-to-obsidian)" "cli=unavailable" \
    -- --ledger "$LED" --cli "$p1"
  st_case "V21 empty target" "NOT-VERIFIED(unreachable)" "empty-target" \
    -- --ledger "$LED" --fallback ""

  # V22 batch: one record pair per target.
  local bout brc=0
  bout=$(env SOUJI_SELFTEST_ACTIVE=1 timeout 60 bash "$SELF" \
    --ledger "$LED" --fallback "$p1" "$p2" "$p4" 2>&1) || brc=$?
  ST_CHECKS=$((ST_CHECKS + 1))
  local nrec nverdict
  nrec=$(printf '%s\n' "$bout" | grep -ac '^VERDICT' || true)
  nverdict=$(printf '%s\n' "$bout" | grep -ac '^NOT-VERIFIED(vault-' || true)
  if [ "$brc" = 0 ] && [ "$nrec" = 3 ] && [ "$nverdict" = 2 ]; then
    printf 'PASS V22 batch: 3 records, 2 vault-side negatives\n'
  else
    ST_FAILS=$((ST_FAILS + 1))
    printf 'FAIL V22 batch: rc=%s records=%s vault-negatives=%s\n' "$brc" "$nrec" "$nverdict"
  fi

  # V23 json parses with the exact path.
  ST_CHECKS=$((ST_CHECKS + 1))
  if env SOUJI_SELFTEST_ACTIVE=1 timeout 60 bash "$SELF" --json \
      --ledger "$LED" --fallback "$p1" 2>/dev/null \
      | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("path") and d.get("verdict")=="VERIFIED" and d.get("receipt")=="moved-to-obsidian" else 1)' \
      2>/dev/null; then
    printf 'PASS V23 json record\n'
  else
    ST_FAILS=$((ST_FAILS + 1))
    printf 'FAIL V23 json record\n'
  fi

  # V24 live surfaces untouched (header-only ledger, unchanged sha).
  ST_CHECKS=$((ST_CHECKS + 1))
  live_ledger_after=$(sha256sum -- "$LIVE_LEDGER_PATH" 2>/dev/null | cut -d' ' -f1 || true)
  if [ "$live_lines_before" = 1 ] && [ "$live_ledger_before" = "$live_ledger_after" ]; then
    printf 'PASS V24 live ledger untouched (header-only, sha unchanged)\n'
  else
    ST_FAILS=$((ST_FAILS + 1))
    printf 'FAIL V24 live ledger: lines_before=%s sha_before=%s sha_after=%s\n' \
      "$live_lines_before" "$(short "$live_ledger_before")" "$(short "$live_ledger_after")"
  fi

  # ---- live phase: run the tests/vault/ case-V* fixtures ----------------
  st_live_phase

  printf 'selftest: %s checks, %s failed, %s note(s)\n' \
    "$ST_CHECKS" "$ST_FAILS" "$ST_NOTES"
  [ "$ST_FAILS" -eq 0 ]
}

# ------------------------------------------------------------------- main --

while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --quiet) shift ;;
    --ledger)
      [ $# -ge 2 ] || { usage >&2; exit 2; }
      LEDGER=$2; shift 2 ;;
    --ledger=*) LEDGER=${1#*=}; shift ;;
    --vault)
      [ $# -ge 2 ] || { usage >&2; exit 2; }
      VAULT_HINT=$2; shift 2 ;;
    --vault=*) VAULT_HINT=${1#*=}; shift ;;
    --cli) MODE=cli; shift ;;
    --fallback) MODE=fallback; shift ;;
    --auto) MODE=auto; shift ;;
    --stale-days)
      [ $# -ge 2 ] || { usage >&2; exit 2; }
      STALE_DAYS=$2; shift 2 ;;
    --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
    -h | --help) usage; exit 0 ;;
    --)
      shift
      while [ $# -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -*)
      printf 'souji-vault-verify: unknown flag: %s\n' "$1" >&2
      usage >&2
      exit 2 ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done
case "$STALE_DAYS" in '' | *[!0-9]*) usage >&2; exit 2 ;; esac
case "$CLI_TIMEOUT" in '' | *[!0-9]*) CLI_TIMEOUT=6 ;; esac

if [ "$SELFTEST" = 1 ]; then
  run_selftest || exit 1
  exit 0
fi

if [ "${#TARGETS[@]}" -eq 0 ]; then
  usage >&2
  exit 2
fi

init_cli
for t in "${TARGETS[@]}"; do
  verify_target "$t"
  emit_record "$t"
done
exit 0
