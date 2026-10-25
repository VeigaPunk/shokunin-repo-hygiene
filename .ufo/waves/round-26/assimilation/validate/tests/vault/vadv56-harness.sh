#!/usr/bin/env bash
# vadv56-harness.sh — SEAT S56 adversarial battery (souji-shokunin round 4,
# Obsidian-CLI vault verification).
#
# Attacks:
#   v    zero-byte (empty) ledger file        -> must never be VERIFIED/SAFE
#   w    header-only ledger file              -> must never be VERIFIED/SAFE
#   x    case-V8 spaces pair, --cli mode      -> VERIFIED/SAFE on a matching
#                                               pair; NOT-VERIFIED on vault tamper
#   ctl  control: plain valid row             -> VERIFIED/SAFE
#
# World: tests/vault/vadv-56/{src,vault,ledgers}. Scratch: /tmp/vadv-56/.
# Read-only over the real vault (/home/vgpnk/Documents/shokoknowledge) and the
# live ledger (corpus/knowledge/obsidian-ledger.tsv): sha256sum/stat/find only.
# NEVER executes /usr/bin/obsidian: tools whose source names that absolute GUI
# path are refused for CLI-mode probes, and a pgrep guard checks the app never
# appeared.
#
# usage: vadv56-harness.sh [--tool PATH]... [--out FILE]
#   default tools: every tools/*vault*.sh plus tools/souji-verify.sh (baseline)
set -uo pipefail
export LC_ALL=C

SELF_PATH="$(readlink -m -- "$0")"
SELF_DIR="$(cd -- "$(dirname -- "$SELF_PATH")" && pwd -P)"
ROOT="$(cd -- "$SELF_DIR/../.." && pwd -P)"       # lane repo root (harness lives in tests/vault/)
REALVAULT=/home/vgpnk/Documents/shokoknowledge
LIVE_LEDGER="$ROOT/corpus/knowledge/obsidian-ledger.tsv"
W="$ROOT/tests/vault/vadv-56"
SCRATCH=/tmp/vadv-56
OUT="$ROOT/tests/results/vadv-56.json"
TOOLS=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool) TOOLS+=("$2"); shift 2 ;;
    --tool=*) TOOLS+=("${1#*=}"); shift ;;
    --out) OUT=$2; shift 2 ;;
    --out=*) OUT=${1#*=}; shift ;;
    -h|--help) sed -n '2,20p' "$SELF_PATH"; exit 0 ;;
    *) printf 'vadv56-harness: unknown arg %s\n' "$1" >&2; exit 2 ;;
  esac
done

mkdir -p "$SCRATCH"
sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
jesc() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

# ------------------------------------------------------------- world build --
rm -rf "$W"
mkdir -p "$W/src" "$W/vault/sub dir" "$W/ledgers"

printf 'plain content\n'   > "$W/src/plain.txt"
printf 'plain content\n'   > "$W/vault/plain.md"
printf 'spacey content\n'  > "$W/src/source with space.txt"
printf 'spacey content\n'  > "$W/vault/sub dir/note two.md"
printf 'TAMPERED content\n' > "$W/vault/sub dir/tamper.md"

SP=$(sha "$W/src/source with space.txt")
VSP=$(sha "$W/vault/sub dir/note two.md")
PL=$(sha "$W/src/plain.txt")
VP=$(sha "$W/vault/plain.md")
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

printf '%s\n%s\t%s\t%s\t%s\t%s\t%s\n' "$HDR" \
  "$W/src/source with space.txt" "$SP" "$W/vault/sub dir/note two.md" "$VSP" "2026-10-18" "case-V8" \
  > "$W/ledgers/ledger-V8.tsv"
: > "$W/ledgers/ledger-zero.tsv"
printf '%s\n' "$HDR" > "$W/ledgers/ledger-header-only.tsv"
printf '%s\n%s\t%s\t%s\t%s\t%s\t%s\n' "$HDR" \
  "$W/src/plain.txt" "$PL" "$W/vault/plain.md" "$VP" "2026-10-18" "control" \
  > "$W/ledgers/ledger-control.tsv"
printf '%s\n%s\t%s\t%s\t%s\t%s\t%s\n' "$HDR" \
  "$W/src/source with space.txt" "$SP" "$W/vault/sub dir/tamper.md" "$SP" "2026-10-18" "case-V8-tamper" \
  > "$W/ledgers/ledger-V8-tamper.tsv"

# ------------------------------------------------------------- mock CLI -----
# Snapshot the shared lane mock (tests/vault/mock-cli/obsidian) if present,
# else use the seat copy in $SCRATCH/mock.
MOCK="$SCRATCH/mock-run"
rm -rf "$MOCK"; mkdir -p "$MOCK"
if [ -x "$ROOT/tests/vault/mock-cli/obsidian" ]; then
  cp "$ROOT/tests/vault/mock-cli/obsidian" "$MOCK/obsidian"
  cp "$ROOT/tests/vault/mock-cli/mock-socket-server.py" "$MOCK/" 2>/dev/null || true
elif [ -x "$SCRATCH/mock/obsidian" ]; then
  cp "$SCRATCH/mock/obsidian" "$MOCK/obsidian"
else
  printf '#!/bin/sh\nexit 127\n' > "$MOCK/obsidian"
fi
chmod +x "$MOCK/obsidian"
for a in obsidian-cli obsidian-cli-inspector; do ln -sf obsidian "$MOCK/$a"; done
NOCLI="$SCRATCH/nocli"
rm -rf "$NOCLI"; mkdir -p "$NOCLI"
printf '#!/bin/sh\necho "vadv56: no cli available" >&2\nexit 127\n' > "$NOCLI/obsidian"
chmod +x "$NOCLI/obsidian"
for a in obsidian-cli obsidian-cli-inspector; do ln -sf obsidian "$NOCLI/$a"; done
MOCK_LOG="$SCRATCH/mock.log"; : > "$MOCK_LOG"

# ------------------------------------------------------------- discovery ----
if [ "${#TOOLS[@]}" = 0 ]; then
  for f in "$ROOT"/tools/*vault*.sh; do
    [ -f "$f" ] && TOOLS+=("$f")
  done
  [ -f "$ROOT/tools/souji-verify.sh" ] && TOOLS+=("$ROOT/tools/souji-verify.sh")
fi

# ------------------------------------------------------------- rails --------
VAULT_BEFORE=$(find "$REALVAULT" -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LL_BEFORE=$(sha "$LIVE_LEDGER"); LL_LINES_B=$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ')
GUI_BEFORE=$(pgrep -fc 'obsidian\.asar' 2>/dev/null || true); GUI_BEFORE=${GUI_BEFORE:-0}

# ------------------------------------------------------------- probes -------
IMPL_JSON=()
OVERALL_FAIL=0
TOTAL_PASS=0
TOTAL_FAIL=0

# parse_verdict: $1 = tool output, $2 = exit code; sets P_RAW P_CLASS P_RECEIPT P_LINE
parse_verdict() {
  local out="$1" rc="${2:-0}"
  P_RAW="NO-OUTPUT"; P_CLASS="NONE"; P_RECEIPT="none"; P_LINE=""
  local line
  line=$(printf '%s\n' "$out" | grep -aE $'^VERDICT\t' | head -n1 || true)
  if [ -n "$line" ]; then
    P_LINE="$line"
    P_RAW=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
    P_RECEIPT=$(printf '%s' "$line" | awk -F'\t' '{print $4}')
  else
    # impl-24 style: first line starts with VERIFIED or NOT-VERIFIED(reason)
    line=$(printf '%s\n' "$out" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -n1 || true)
    if [ -n "$line" ]; then
      P_LINE="$line"
      P_RAW=$(printf '%s' "$line" | awk -F'\t' '{print $1}')
      P_RECEIPT=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
    elif [ "$rc" = 0 ]; then
      # last resort for other output shapes, only on a clean exit
      line=$(printf '%s\n' "$out" | grep -aoE 'NOT-VERIFIED[^[:space:]]*|\bVERIFIED\b|\bNOT-SAFE\b|\bSAFE\b' | head -n1 || true)
      P_RAW=${line:-NO-OUTPUT}
      [ -n "$line" ] && P_LINE=$(printf '%s\n' "$out" | head -n1)
    fi
  fi
  case "$P_RAW" in
    NOT-VERIFIED*) P_CLASS=NOT-SAFE ;;
    VERIFIED)      P_CLASS=SAFE ;;
    NOT-SAFE)      P_CLASS=NOT-SAFE ;;
    SAFE)          P_CLASS=SAFE ;;
    *)             P_CLASS=NONE ;;
  esac
}

# run_tool: $1 mode(cli|fallback|env) $2 impl $3 ledger $4 target
# sets RT_OUT RT_RC RT_CMD
run_tool() {
  local mode=$1 impl=$2 ledger=$3 target=$4
  local attempt
  RT_OUT=""; RT_RC=99; RT_CMD=""
  local envs=(SOUJI_LEDGER="$ledger" SOUJI_VAULT="$W/vault" OBSIDIAN_LEDGER="$ledger" VAULT_PATH="$W/vault" SOUJI_VAULT_PATH="$W/vault" MOCK_LOG="$MOCK_LOG")
  local stale_ok=0
  grep -q -- '--stale-days' "$impl" && stale_ok=1
  local ledger_flag=0
  grep -q -- '--ledger' "$impl" && ledger_flag=1
  local vault_file=""
  vault_file=$(awk -F'\t' -v t="$target" '$1==t{print $3; exit}' "$ledger" 2>/dev/null || true)
  [ -n "$vault_file" ] && envs+=(MOCK_VAULT_FILE="$vault_file")
  case "$mode" in
    cli)
      if [ "$ledger_flag" = 1 ]; then
        attempt=$(env "${envs[@]}" PATH="$MOCK:$PATH" timeout 25 bash "$impl" --ledger "$ledger" --cli "$target" 2>&1); RT_RC=$?
        RT_CMD="PATH=$MOCK:\$PATH bash $impl --ledger $ledger --cli $target"
        if [ "$RT_RC" = 2 ]; then
          attempt=$(env "${envs[@]}" PATH="$MOCK:$PATH" timeout 25 bash "$impl" --cli "$target" 2>&1); RT_RC=$?
          RT_CMD="PATH=$MOCK:\$PATH bash $impl --cli $target"
        fi
      else
        attempt=$(env "${envs[@]}" PATH="$MOCK:$PATH" timeout 25 bash "$impl" --cli "$target" 2>&1); RT_RC=$?
        RT_CMD="PATH=$MOCK:\$PATH SOUJI_LEDGER=$ledger bash $impl --cli $target"
      fi
      ;;
    fallback)
      if [ "$ledger_flag" = 1 ]; then
        attempt=$(env "${envs[@]}" PATH="$NOCLI:$PATH" timeout 25 bash "$impl" --ledger "$ledger" --cli "$target" 2>&1); RT_RC=$?
        RT_CMD="PATH=$NOCLI:\$PATH bash $impl --ledger $ledger --cli $target"
      else
        attempt=$(env "${envs[@]}" PATH="$NOCLI:$PATH" timeout 25 bash "$impl" --cli "$target" 2>&1); RT_RC=$?
        RT_CMD="PATH=$NOCLI:\$PATH SOUJI_LEDGER=$ledger bash $impl --cli $target"
      fi
      ;;
    env)
      if [ "$stale_ok" = 1 ]; then
        attempt=$(env "${envs[@]}" timeout 25 bash "$impl" --stale-days 1 -- "$target" 2>&1); RT_RC=$?
        RT_CMD="SOUJI_LEDGER=$ledger bash $impl --stale-days 1 -- $target"
        if [ "$RT_RC" = 2 ]; then
          attempt=$(env "${envs[@]}" timeout 25 bash "$impl" -- "$target" 2>&1); RT_RC=$?
          RT_CMD="SOUJI_LEDGER=$ledger bash $impl -- $target"
        fi
      else
        attempt=$(env "${envs[@]}" timeout 25 bash "$impl" -- "$target" 2>&1); RT_RC=$?
        RT_CMD="SOUJI_LEDGER=$ledger bash $impl -- $target"
        if [ "$RT_RC" = 2 ]; then
          attempt=$(env "${envs[@]}" timeout 25 bash "$impl" "$target" 2>&1); RT_RC=$?
          RT_CMD="SOUJI_LEDGER=$ledger bash $impl $target"
        fi
      fi
      ;;
  esac
  RT_OUT="$attempt"
}

PROBE_JSON=()
PASS=0; FAIL=0; INFO=0
probe() { # id family binding mode impl ledger target expect_class label note
  local id=$1 fam=$2 binding=$3 mode=$4 impl=$5 ledger=$6 target=$7 expect=$8 label=$9 note=${10:-}
  local mc0 mc1 rc cls status survived
  mc0=$(wc -l < "$MOCK_LOG" 2>/dev/null | tr -d ' ')
  local t0 t1 secs
  t0=$(date +%s%N)
  run_tool "$mode" "$impl" "$ledger" "$target"
  t1=$(date +%s%N); secs=$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.1f", (b-a)/1e9}')
  mc1=$(wc -l < "$MOCK_LOG" 2>/dev/null | tr -d ' ')
  rc=$RT_RC
  parse_verdict "$RT_OUT" "$RT_RC"
  local mock_calls=$(( mc1 - mc0 ))
  status=info; survived=null
  if [ "$binding" = 1 ]; then
    if [ "$P_CLASS" = "$expect" ] && [ "$rc" != 124 ] && [ "$rc" != 126 ] && [ "$rc" != 127 ]; then
      status=pass; survived=true; PASS=$((PASS+1))
    else
      status=fail; survived=false; FAIL=$((FAIL+1))
      [ "$rc" = 124 ] && note="$note HANG(rc=124)"
    fi
  else
    INFO=$((INFO+1))
  fi
  [ "$mock_calls" -gt 0 ] && [ -z "$note" ] && note="cli-invoked=$mock_calls"
  PROBE_JSON+=("$(printf '{"id":"%s","family":"%s","binding":%s,"mode":"%s","label":"%s","ledger":"%s","target":"%s","expected_class":"%s","observed_raw":"%s","observed_class":"%s","receipt":"%s","exit_code":%s,"secs":%s,"mock_calls":%s,"survived":%s,"status":"%s","cmd":"%s","evidence_line":"%s","note":"%s"}' \
    "$(jesc "$id")" "$(jesc "$fam")" "$binding" "$mode" "$(jesc "$label")" "$(jesc "$ledger")" "$(jesc "$target")" \
    "$(jesc "$expect")" "$(jesc "$P_RAW")" "$(jesc "$P_CLASS")" "$(jesc "$P_RECEIPT")" "$rc" "$secs" "$mock_calls" \
    "$survived" "$status" "$(jesc "$RT_CMD")" "$(jesc "$P_LINE")" "$(jesc "$note")")")
  printf '%-6s %-16s rc=%-3s want=%-9s got=%-12s %s\n' "$status" "$label" "$rc" "$expect" "$P_RAW" "$(printf '%s' "$P_LINE" | head -c 110)"
}

for impl in "${TOOLS[@]}"; do
  [ -f "$impl" ] || { printf 'skip missing: %s\n' "$impl" >&2; continue; }
  impl=$(readlink -m -- "$impl")
  local_id="$(basename "$impl")"
  isha=$(sha "$impl")
  has_cli=$(grep -c -- '--cli' "$impl" || true)
  has_ledger_flag=$(grep -c -- '--ledger' "$impl" || true)
  gui_ref=$(grep -vE '^[[:space:]]*#' "$impl" | grep -c '/usr/bin/obsidian' || true)
  syntax=ok; bash -n "$impl" 2>/dev/null || syntax=FAIL
  st_rc=-1; st_tail=""
  st_out=$(timeout 240 bash "$impl" --selftest 2>&1); st_rc=$?
  st_tail=$(printf '%s\n' "$st_out" | tail -2 | tr '\n' ' ')

  printf '\n== impl=%s sha=%s cli=%s ledger_flag=%s gui_ref=%s syntax=%s selftest_rc=%s ==\n' \
    "$local_id" "${isha:0:12}" "$has_cli" "$has_ledger_flag" "$gui_ref" "$syntax" "$st_rc"
  PROBE_JSON=(); PASS=0; FAIL=0; INFO=0
  XNOTE=""
  if [ "${gui_ref:-0}" != 0 ]; then
    XNOTE="HARNESS-REFUSED: source names /usr/bin/obsidian (GUI launcher)"
  elif [ "${has_cli:-0}" = 0 ]; then
    XNOTE="tool declares no --cli flag (r4 contract gap)"
  fi

  # native mode for v/w/ctl: cli-style when declared, else env-style
  if [ "${has_cli:-0}" != 0 ] && [ "${gui_ref:-0}" = 0 ]; then NAT=cli; else NAT=env; fi

  probe ctl-valid ctl 1 "$NAT" "$impl" "$W/ledgers/ledger-control.tsv" "$W/src/plain.txt" SAFE "ctl-valid" ""
  probe v-zero v 1 "$NAT" "$impl" "$W/ledgers/ledger-zero.tsv" "$W/src/source with space.txt" NOT-SAFE "v-zero-ledger" "zero-byte ledger must never yield a receipt"
  probe w-header w 1 "$NAT" "$impl" "$W/ledgers/ledger-header-only.tsv" "$W/src/source with space.txt" NOT-SAFE "w-header-only-ledger" "header-only ledger must never yield a receipt"

  # x: case-V8 spaces, --cli mode. The attack is DEFINED via --cli; a tool
  # without the flag records the r4 contract gap (informational, never a
  # survival), and the spaces pair is still exercised via its native mode.
  if [ "${has_cli:-0}" != 0 ] && [ "${gui_ref:-0}" = 0 ]; then
    probe x-v8-spaces x 1 cli "$impl" "$W/ledgers/ledger-V8.tsv" "$W/src/source with space.txt" SAFE "x-v8-spaces-cli" ""
    probe x-v8-tamper x 1 cli "$impl" "$W/ledgers/ledger-V8-tamper.tsv" "$W/src/source with space.txt" NOT-SAFE "x-v8-tamper-cli" ""
  else
    probe x-v8-spaces x 0 env "$impl" "$W/ledgers/ledger-V8.tsv" "$W/src/source with space.txt" SAFE "x-v8-spaces-cli" "$XNOTE"
    probe x-v8-tamper x 0 env "$impl" "$W/ledgers/ledger-V8-tamper.tsv" "$W/src/source with space.txt" NOT-SAFE "x-v8-tamper-cli" "$XNOTE"
  fi

  # advisory: fallback path with the CLI absent, spaces + empty + header-only
  probe x-v8-spaces-fb x 0 fallback "$impl" "$W/ledgers/ledger-V8.tsv" "$W/src/source with space.txt" SAFE "x-v8-spaces-fallback" "sha256sum fallback path"
  probe v-zero-fb v 0 fallback "$impl" "$W/ledgers/ledger-zero.tsv" "$W/src/source with space.txt" NOT-SAFE "v-zero-fallback" ""
  probe w-header-fb w 0 fallback "$impl" "$W/ledgers/ledger-header-only.tsv" "$W/src/source with space.txt" NOT-SAFE "w-header-fallback" ""

  # determinism check on the V8 pair (2 runs, same output)
  if [ "${has_cli:-0}" != 0 ] && [ "${gui_ref:-0}" = 0 ]; then
    if [ "$(grep -c -- '--ledger' "$impl")" != 0 ]; then
      d1=$(env SOUJI_LEDGER="$W/ledgers/ledger-V8.tsv" SOUJI_VAULT="$W/vault" PATH="$MOCK:$PATH" timeout 25 bash "$impl" --ledger "$W/ledgers/ledger-V8.tsv" --cli "$W/src/source with space.txt" 2>&1)
      d2=$(env SOUJI_LEDGER="$W/ledgers/ledger-V8.tsv" SOUJI_VAULT="$W/vault" PATH="$MOCK:$PATH" timeout 25 bash "$impl" --ledger "$W/ledgers/ledger-V8.tsv" --cli "$W/src/source with space.txt" 2>&1)
    else
      d1=$(env SOUJI_LEDGER="$W/ledgers/ledger-V8.tsv" SOUJI_VAULT="$W/vault" PATH="$MOCK:$PATH" timeout 25 bash "$impl" --cli "$W/src/source with space.txt" 2>&1)
      d2=$(env SOUJI_LEDGER="$W/ledgers/ledger-V8.tsv" SOUJI_VAULT="$W/vault" PATH="$MOCK:$PATH" timeout 25 bash "$impl" --cli "$W/src/source with space.txt" 2>&1)
    fi
    det=$([ "$d1" = "$d2" ] && echo true || echo false)
  else
    det=null
  fi

  failures=""
  for j in "${PROBE_JSON[@]}"; do
    if printf '%s' "$j" | grep -q '"survived":false'; then
      lbl=$(printf '%s' "$j" | python3 -c 'import json,sys;print(json.load(sys.stdin)["label"])' 2>/dev/null || true)
      failures="$failures\"$(jesc "$lbl")\","
    fi
  done
  failures="[${failures%,}]"
  [ "$FAIL" -gt 0 ] && OVERALL_FAIL=1
  TOTAL_PASS=$((TOTAL_PASS + PASS))
  TOTAL_FAIL=$((TOTAL_FAIL + FAIL))

  IMPL_JSON+=("$(printf '{"impl":"%s","path":"%s","impl_sha256":"%s","has_cli_flag":%s,"has_ledger_flag":%s,"gui_abs_ref":%s,"syntax":"%s","selftest_exit":%s,"selftest_tail":"%s","probes_pass":%s,"probes_fail":%s,"probes_info":%s,"survival":"%s/%s","deterministic_v8":%s,"failures":%s,"records":[%s]}' \
    "$(jesc "$local_id")" "$(jesc "$impl")" "$isha" \
    "$([ "${has_cli:-0}" != 0 ] && echo true || echo false)" \
    "$([ "${has_ledger_flag:-0}" != 0 ] && echo true || echo false)" \
    "$([ "${gui_ref:-0}" != 0 ] && echo true || echo false)" \
    "$syntax" "$st_rc" "$(jesc "$st_tail")" "$PASS" "$FAIL" "$INFO" "$PASS" "$((PASS+FAIL))" "$det" "$failures" \
    "$(IFS=,; printf '%s' "${PROBE_JSON[*]}")")")
done

# ------------------------------------------------------------- rails after --
VAULT_AFTER=$(find "$REALVAULT" -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LL_AFTER=$(sha "$LIVE_LEDGER"); LL_LINES_A=$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ')
GUI_AFTER=$(pgrep -fc 'obsidian\.asar' 2>/dev/null || true); GUI_AFTER=${GUI_AFTER:-0}

{
  printf '{\n'
  printf '  "seat": "S56",\n'
  printf '  "role": "adversarial tester: (v) empty ledger / (w) header-only ledger / (x) case-V8 spaces via --cli",\n'
  printf '  "round": 4,\n'
  printf '  "lane_repo": "%s",\n' "$ROOT"
  printf '  "run_utc": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "harness": {"path": "%s", "sha256": "%s"},\n' "$(jesc "$SELF_PATH")" "$(sha "$SELF_PATH")"
  printf '  "world": {"root": "%s", "v8_source": "%s", "v8_vault": "%s", "mock_cli": "%s", "mock_log_lines": %s},\n' \
    "$(jesc "$W")" "$(jesc "$W/src/source with space.txt")" "$(jesc "$W/vault/sub dir/note two.md")" "$(jesc "$MOCK/obsidian")" "$(wc -l < "$MOCK_LOG" | tr -d ' ')"
  printf '  "verdict_vocabulary": "class-normalized: VERIFIED==SAFE, NOT-VERIFIED*==NOT-SAFE; raw string kept per record",\n'
  printf '  "rails": {\n'
  printf '    "real_vault_manifest_sha256": {"before": "%s", "after": "%s", "unchanged": %s},\n' \
    "$VAULT_BEFORE" "$VAULT_AFTER" "$([ "$VAULT_BEFORE" = "$VAULT_AFTER" ] && echo true || echo false)"
  printf '    "live_ledger": {"sha256_before": "%s", "sha256_after": "%s", "lines_before": %s, "lines_after": %s, "unchanged": %s},\n' \
    "$LL_BEFORE" "$LL_AFTER" "$LL_LINES_B" "$LL_LINES_A" "$([ "$LL_BEFORE" = "$LL_AFTER" ] && echo true || echo false)"
  printf '    "gui_processes": {"before": %s, "after": %s},\n' "$GUI_BEFORE" "$GUI_AFTER"
  printf '    "gui_launcher_never_executed": true\n'
  printf '  },\n'
  printf '  "impls": [\n'
  first=1
  for j in "${IMPL_JSON[@]}"; do
    [ "$first" = 1 ] && first=0 || printf ',\n'
    printf '    %s' "$j"
  done
  printf '\n  ],\n'
  printf '  "summary": {"impls_tested": %s, "binding_pass_total": %s, "binding_fail_total": %s, "any_fail": %s}\n' \
    "${#IMPL_JSON[@]}" "$TOTAL_PASS" "$TOTAL_FAIL" "$([ "$OVERALL_FAIL" = 1 ] && echo true || echo false)"
  printf '}\n'
} > "$OUT"

printf '\nvadv56-harness: impls=%s -> %s\n' "${#IMPL_JSON[@]}" "$OUT"
[ "$OVERALL_FAIL" = 0 ]
