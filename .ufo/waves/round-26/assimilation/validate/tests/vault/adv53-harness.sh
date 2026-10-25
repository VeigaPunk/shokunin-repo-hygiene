#!/usr/bin/env bash
# adv53-harness — seat S53 adversarial probes for the round-4 Obsidian-CLI
# verification contract. Three families:
#
#   m  --cli forced while the CLI contract is FALLBACK-ONLY: the tool must
#      degrade or error cleanly, never hang and never silently ignore the flag.
#   n  huge file (100MB sparse): hash correctness, no size/mtime shortcut.
#   o  vault file modified between the CLI read and the fallback read: the
#      tool must surface cli-disagreement (or re-verify), never a silent SAFE.
#
# Usage: adv53-harness.sh [--tool PATH] [--out FILE] [--only m|n|o]
#
# Safety: fixtures live in a mktemp -d under /tmp; the real vault
# (/home/vgpnk/Documents/shokoknowledge) is never touched; /usr/bin/obsidian
# (the GUI launcher) is never executed — the mock CLI is prepended to PATH
# and a static pre-check refuses to run if the tool under test names the
# absolute GUI path.
set -uo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
MOCK_DIR="$SCRIPT_DIR/mock-cli"
DEFAULT_TOOL="$REPO_ROOT/tools/souji-verify.sh"

TOOL="$DEFAULT_TOOL"
OUT=""
ONLY=""
CLI_TIMEOUT=12
HUGE_MB=100

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool) TOOL=$2; shift 2 ;;
    --tool=*) TOOL=${1#*=}; shift ;;
    --out) OUT=$2; shift 2 ;;
    --out=*) OUT=${1#*=}; shift ;;
    --only) ONLY=$2; shift 2 ;;
    --only=*) ONLY=${1#*=}; shift ;;
    -h|--help) sed -n '2,15p' "$SCRIPT_PATH"; exit 0 ;;
    *) printf 'adv53-harness: unknown arg %s\n' "$1" >&2; exit 2 ;;
  esac
done
[ -n "$OUT" ] || OUT="$REPO_ROOT/tests/results/vadv-53.json"

WORK=""
PASS=0 FAIL=0 NA=0
RESULTS=()

cleanup() { [ -n "$WORK" ] && rm -rf -- "$WORK"; }
trap cleanup EXIT

jesc() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

# H1 self-audit — a backtick inside a double-quoted string is command
# substitution. In a harness whose whole purpose is to prove that a bare
# `obsidian` is never executed, that mistake executes the desktop-app launcher.
# Refuse to run if any such string is found in this file.
self_audit_backticks() {
  local hits bt
  bt=$(printf '\140')
  # A backtick inside a double-quoted string is command substitution. Comments
  # are exempt. The scan is written in awk so the scanner cannot match itself.
  hits=$(awk -v bt="$bt" '
    /^[[:space:]]*#/ { next }
    {
      n = split($0, p, "\"")
      for (i = 2; i <= n; i += 2) {
        if (index(p[i], bt) > 0) { print NR ": " $0; next }
      }
    }
  ' "$SCRIPT_PATH" 2>/dev/null || true)
  if [ -n "$hits" ]; then
    printf 'adv53-harness: REFUSING TO RUN — backtick inside a double-quoted string\n' >&2
    printf '%s\n' "$hits" >&2
    printf 'adv53-harness: that is command substitution and can launch the real app.\n' >&2
    exit 3
  fi
}
self_audit_backticks

record() { # $1 id, $2 family, $3 binding(0/1), $4 oracle, $5 rc, $6 secs, $7 out, $8 verdict
  local id=$1 fam=$2 bind=$3 oracle=$4 rc=$5 secs=$6 out=$7 verdict=$8
  if [ "$verdict" = PASS ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
  RESULTS+=("$(printf '{"id":"%s","family":"%s","binding":%s,"oracle":"%s","rc":%s,"secs":%s,"verdict":"%s","out":"%s"}' \
    "$(jesc "$id")" "$(jesc "$fam")" "$bind" "$(jesc "$oracle")" "$rc" "$secs" "$verdict" "$(jesc "$out")")")
  printf '%-6s %-6s %s\n' "$verdict" "$id" "$(printf '%s' "$out" | head -c 150)"
}

record_na() { # $1 id, $2 family, $3 reason — a probe that cannot be exercised
  local id=$1 fam=$2 reason=$3
  NA=$((NA+1))
  RESULTS+=("$(printf '{"id":"%s","family":"%s","binding":true,"verdict":"N/A","reason":"%s"}' \
    "$(jesc "$id")" "$(jesc "$fam")" "$(jesc "$reason")")")
  printf '%-6s %-6s %s\n' "N/A" "$id" "$reason"
}

note() { # $1 id, $2 text, optional extra JSON fragment $3
  RESULTS+=("$(printf '{"id":"%s","note":"%s"%s}' "$(jesc "$1")" "$(jesc "$2")" "${3:+,$3}")")
}

# --------------------------------------------------------------- fixtures --

snapshot() { # $1 dir -> "path<TAB>mtime<TAB>sha" lines (read-only proof)
  ( cd "$1" && find . -type f -not -path './.git/*' -printf '%p\t%T@\t' -exec sha256sum {} \; 2>/dev/null \
      | sed 's#^\./##' | sort )
}

mk_repo() { # $1 dir -> sha
  local d=$1 tr sha
  mkdir -p "$d/keep"
  git init -q --initial-branch=master "$d" >/dev/null 2>&1
  printf 'anchor\n' > "$d/keep/anchor.txt"
  git -C "$d" add -A >/dev/null 2>&1
  tr=$(git -C "$d" write-tree)
  sha=$(printf 'anchor\n' | git -C "$d" commit-tree "$tr")
  git -C "$d" update-ref refs/heads/master "$sha"
  git -C "$d" update-ref refs/remote/origin/master "$sha" 2>/dev/null || true
  git -C "$d" update-ref refs/remotes/origin/master "$sha"
  git -C "$d" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/master
  git -C "$d" symbolic-ref HEAD refs/heads/master
  printf '%s' "$sha"
}

sparse_file() { # $1 path, $2 logical bytes, $3 fill-char (default NUL => truly sparse)
  local p=$1 n=$2 c=${3:-}
  truncate -s "$n" -- "$p"
  if [ -n "$c" ]; then
    head -c "$n" < /dev/zero | tr '\0' "$c" > "$p"
  fi
}

# ------------------------------------------------------------- run helper --

LAST_RC=0 LAST_OUT="" LAST_STDOUT="" LAST_ERR="" LAST_SECS=0 GUI_SEEN=0

# Only real verdict records count. Usage/help text that merely mentions the
# words SAFE / NOT-SAFE must never be read as a verdict. Both the r2
# VERDICT<TAB>... form and the r4 VERIFIED/NOT-VERIFIED vocabulary are parsed.
verdict_of() { # $1 = 1 verdict | 2 receipt ; prints one value per verdict record
  local idx=$1 line rest
  while IFS= read -r line; do
    case "$line" in
      VERDICT$'\t'*)
        rest=${line#VERDICT$'\t'}      # path
        rest=${rest#*$'\t'}            # verdict
        if [ "$idx" = 1 ]; then printf '%s\n' "${rest%%$'\t'*}"
        else
          rest=${rest#*$'\t'}          # receipt
          printf '%s\n' "${rest%%$'\t'*}"
        fi
        ;;
      VERIFIED$'\t'*)
        if [ "$idx" = 1 ]; then
          printf 'SAFE\n'
        else
          rest=${line#VERIFIED$'\t'}; rest=${rest#*$'\t'}
          printf '%s\n' "${rest%%$'\t'*}"
        fi
        ;;
      'NOT-VERIFIED('*)
        if [ "$idx" = 1 ]; then printf 'NOT-SAFE\n'; else printf 'none\n'; fi
        ;;
      \{*'"verdict":"'*)
        if [ "$idx" = 1 ]; then
          case "$line" in *'"verdict":"NOT-SAFE"'*) printf 'NOT-SAFE\n' ;; *'"verdict":"SAFE"'*) printf 'SAFE\n' ;; esac
        else
          case "$line" in *'"receipt":"'*) rest=${line#*'"receipt":"'}; printf '%s\n' "${rest%%\"*}" ;; esac
        fi
        ;;
    esac
    # Never let the last test inside a branch become the loop's exit status:
    # with `set -o pipefail` that would fail the caller's pipeline even when
    # grep found a match.
    :
  done <<<"$LAST_STDOUT"
  return 0
}

saw_verdict() { verdict_of 1 | grep -qx -- "$1"; }
saw_receipt() { verdict_of 2 | grep -qx -- "$1"; }

run_tool() { # $1 cli_timeout, $2 path-prefix, rest = env assignments then -- then args
  local to=$1 prefix=$2; shift 2
  local envs=() args=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  [ "$#" -gt 0 ] && shift
  args=("$@")
  local t0 t1
  t0=$(date +%s.%N)
  # GUARD_DIR is always prepended (except when the caller deliberately passes a
  # single-directory PATH): it shadows any name that could reach the real
  # desktop-app launcher, turning an accidental exec into a recorded hazard
  # instead of a launched application.
  local path_val="$prefix:$GUARD_DIR:$PATH"
  env "${envs[@]}" PATH="$path_val" timeout "$to" bash "$TOOL" "${args[@]}" >"$WORK/.stdout" 2>"$WORK/.stderr"
  LAST_RC=$?
  t1=$(date +%s.%N)
  LAST_STDOUT=$(cat "$WORK/.stdout" 2>/dev/null)
  LAST_ERR=$(cat "$WORK/.stderr" 2>/dev/null)
  LAST_OUT=$(printf '%s\n%s' "$LAST_STDOUT" "$LAST_ERR")
  LAST_SECS=$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f", b-a}')
  # Passive observation only: never signal another process. A running Obsidian
  # belongs to the operator; killing it would be destructive.
  if pgrep -f 'obsidian\.asar' >/dev/null 2>&1; then
    GUI_SEEN=1
  fi
}

mock_calls() { # $1 log -> invocation count (awk, so pipefail cannot double-print)
  awk 'END{printf "%d", NR+0}' "$1" 2>/dev/null || printf '0'
}

# run_best — exercise whichever verification mode the tool actually implements.
# Today the installed tool has no --cli at all: forcing it yields rc=2 and no
# verdict, so the real (fallback) contract can only be tested without the flag.
# When a future candidate does implement --cli, this uses it and the mock CLI
# becomes live. CLI_MODE records which branch ran, so the report never confuses
# "safe because it degraded" with "safe because the capability is absent".
CLI_MODE=""
run_best() { # $1 timeout, $2 path-prefix, rest = env assignments then -- then args
  local to=$1 prefix=$2; shift 2
  local envs=() args=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  [ "$#" -gt 0 ] && shift
  args=("$@")
  if [ "${TOOL_HAS_CLI:-0}" != 0 ]; then
    run_tool "$to" "$prefix" "${envs[@]}" -- --cli "${args[@]}"
    CLI_MODE="cli"
    return 0
  fi
  # Probe once whether this tool accepts --cli despite the static scan.
  run_tool "$to" "$prefix" "${envs[@]}" -- --cli "${args[@]}"
  if [ "$LAST_RC" != 2 ]; then
    CLI_MODE="cli"
    return 0
  fi
  run_tool "$to" "$prefix" "${envs[@]}" -- "${args[@]}"
  CLI_MODE="fallback"
  return 0
}

# ------------------------------------------------------------ case runner --

# case_m: --cli forced while the CLI contract is fallback-only.
case_m() {
  local d="$WORK/m"
  mkdir -p "$d"
  local target="$d/m-target.txt"
  printf 'm payload\n' > "$target"
  local emptybin="$d/emptybin"; mkdir -p "$emptybin"
  local log="$d/mock.log"; : > "$log"

  # M1 — bare `--cli`, no cli binary on PATH at all.
  run_tool "$CLI_TIMEOUT" "$emptybin" -- --cli "$target"
  local v=PASS why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="HANG (25s bound) with no cli present"
  elif [ "$LAST_RC" -ge 126 ]; then v=FAIL; why="crash rc=$LAST_RC"
  elif [ "${TOOL_HAS_CLI:-0}" = 0 ]; then
    # Fallback-only tool: clean answers are usage-error (rc=2) or an explicit
    # unsupported/degrade notice. rc=0 with no mention = silent ignore.
    if [ "$LAST_RC" = 0 ] && ! grep -qiE 'cli|degrad|fallback|unavailable|unsupported' <<<"$LAST_OUT"; then
      v=FAIL; why="silent-ignore: rc=0, no cli mention anywhere"
    fi
  else
    if [ "$LAST_RC" = 0 ] && ! grep -qiE 'cli' <<<"$LAST_OUT"; then
      v=FAIL; why="rc=0 but the output never names the cli state"
    fi
  fi
  record M1 m 1 "never rc=124; either rc=2 usage-error or an explicit degrade naming cli" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note M1.note "$why"

  # M2 — `--cli --json` (flag + output-format combination).
  run_tool "$CLI_TIMEOUT" "$emptybin" -- --cli --json "$target"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang"
  elif [ "${TOOL_HAS_CLI:-0}" = 0 ]; then
    [ "$LAST_RC" = 2 ] || { v=FAIL; why="unknown flag should exit 2, got rc=$LAST_RC"; }
  else
    [ "$LAST_RC" = 0 ] || { v=FAIL; why="declared --cli should be accepted, got rc=$LAST_RC"; }
  fi
  record M2 m 1 "no-cli tool: rc=2; cli-capable tool: rc=0" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note M2.note "$why"

  # M3 — a CLI that hangs: the tool must bound the call itself.
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=hang MOCK_LOG="$log" -- --cli "$target"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="tool inherited the hang (no internal bound)"; fi
  record M3 m 1 "tool returns before the harness bound; never inherits a hanging cli" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note M3.note "$why"

  # M4 — CLI exits 3.
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=error MOCK_LOG="$log" -- --cli "$target"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang"
  elif saw_verdict SAFE; then v=FAIL; why="SAFE although the cli errored"; fi
  record M4 m 1 "cli rc=3 => degrade/error; never a SAFE verdict" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note M4.note "$why"

  # M5 — unparseable CLI output.
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=garbage MOCK_LOG="$log" -- --cli "$target"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang"
  elif saw_verdict SAFE; then v=FAIL; why="SAFE on unparseable cli output"; fi
  record M5 m 1 "unparseable cli output => degrade; never a SAFE verdict" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note M5.note "$why"

  # M6 — empty CLI output (rc=0, nothing printed): the classic trap.
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=empty MOCK_LOG="$log" -- --cli "$target"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang"
  elif saw_verdict SAFE; then v=FAIL; why="FALSE-SAFE: empty cli output treated as agreement"; fi
  record M6 m 0 "empty cli output => degrade; never a SAFE verdict" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note M6.note "$why"

  # M7 — honest CLI but no ledger row: the CLI alone must never be a receipt.
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=ok MOCK_LOG="$log" \
    SOUJI_LEDGER="$d/nonexistent-ledger.tsv" SHOKUNIN_ROOT="$d" -- --cli "$target"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang"
  elif saw_verdict SAFE; then v=FAIL; why="SAFE with no ledger row (cli treated as the receipt)"; fi
  record M7 m 1 "cli ok + no ledger row => NOT-SAFE; the ledger stays the receipt of record" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note M7.note "$why"

  # M8 — GUI-LAUNCH HAZARD. On this host the name "obsidian" resolves to the
  # desktop-app launcher; a --cli path that execs the resolved name would
  # start the GUI. The mock records any execution in a sentinel file.
  # NOTE: no backticks anywhere in quoted strings in this file — backticks are
  # command substitution and would execute the very command we are probing for.
  local sentinel="$d/gui.sentinel"; : > "$sentinel"
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=gui MOCK_GUI_SENTINEL="$sentinel" \
    MOCK_LOG="$log" SOUJI_LEDGER="$d/nonexistent-ledger.tsv" SHOKUNIN_ROOT="$d" -- --cli "$target"
  local launched=0
  [ -s "$sentinel" ] && launched=1
  v=PASS; why=""
  if [ "$launched" = 1 ]; then
    v=FAIL; why="HAZARD: --cli executed the obsidian name, which is the GUI launcher on this host"
  elif [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang"
  fi
  record M8 m 1 "never execute a bare obsidian name (it launches the desktop app here)" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  note M8.sentinel "gui-launch sentinel state" \
    "\"launched\":$([ "$launched" = 1 ] && printf true || printf false),\"sentinel_bytes\":$(stat -c %s "$sentinel" 2>/dev/null || printf 0)"
  [ -n "$why" ] && note M8.note "$why"

  # M9 — socket transport, degraded server side (the real CLI's own channel).
  local sd="$d/sock"; mkdir -p "$sd"
  for mode in noreply garbage close eof; do
    rm -f "$sd/.obsidian-cli.sock" "$sd/.obsidian-cli.sock.ready"
    MOCK_SOCK_DIR="$sd" MOCK_MODE="$mode" MOCK_VAULT_FILE="$target" \
      MOCK_LOG="$d/sock-$mode.log" python3 "$MOCK_DIR/mock-socket-server.py" &
    local spid=$!
    for _ in $(seq 1 40); do [ -e "$sd/.obsidian-cli.sock.ready" ] && break; sleep 0.1; done
    local ready=0; [ -e "$sd/.obsidian-cli.sock.ready" ] && ready=1
    if [ "$ready" = 0 ]; then
      note M9.pre "$mode: mock socket server never became ready; probe skipped"
      kill "$spid" 2>/dev/null; wait "$spid" 2>/dev/null
      continue
    fi
    run_tool "$CLI_TIMEOUT" "$MOCK_DIR" XDG_RUNTIME_DIR="$sd" MOCK_MODE="$mode" \
      MOCK_SOCK_DIR="$sd" SOUJI_LEDGER="$d/nonexistent-ledger.tsv" SHOKUNIN_ROOT="$d" \
      -- --cli "$target"
    kill "$spid" 2>/dev/null; wait "$spid" 2>/dev/null
    v=PASS; why=""
    if [ "$LAST_RC" = 124 ]; then v=FAIL; why="HANG on a $mode socket (no own bound)"
    elif [ "$LAST_RC" != 0 ] && [ "$LAST_RC" != 2 ]; then
      v=FAIL; why="abnormal exit rc=$LAST_RC on a $mode socket (crash, not a clean degrade)"
    elif [ -z "$LAST_STDOUT" ]; then
      v=FAIL; why="no output at all on a $mode socket — a verdict is required"
    elif saw_verdict SAFE; then v=FAIL; why="SAFE from a $mode socket (no usable answer)"; fi
    record "M9.$mode" m 1 "socket $mode => degrade within the bound; never SAFE" \
      "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
    [ -n "$why" ] && note "M9.$mode.note" "$why"
  done

  # M10 — was the CLI ever actually invoked? Decisive evidence for the --cli claim.
  local calls; calls=$(mock_calls "$log")
  note M.arglog "mock cli invocations during the whole m family" \
    "\"mock_invocations\":${calls// /},\"tool_has_cli_flag\":$([ "${TOOL_HAS_CLI:-0}" != 0 ] && printf true || printf false),\"log\":\"$(jesc "$log")\""
}

# case_n: 100MB sparse hash correctness.
case_n() {
  local d="$WORK/n"; mkdir -p "$d"
  local repo="$d/repo-shokunin" vault="$d/vault"
  mk_repo "$repo" >/dev/null
  mkdir -p "$vault" "$repo/notes"
  local bytes=$(( HUGE_MB * 1024 * 1024 ))
  local hdr='source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

  # N1 — identical 100MB sparse content on both sides -> SAFE(moved-to-obsidian).
  local src="$repo/notes/huge-a.bin" vcopy="$vault/huge-a.bin"
  sparse_file "$src" "$bytes"
  sparse_file "$vcopy" "$bytes"
  local s_sha v_sha
  s_sha=$(sha256sum -- "$src" | cut -d' ' -f1)
  v_sha=$(sha256sum -- "$vcopy" | cut -d' ' -f1)
  [ "$s_sha" = "$v_sha" ] || note N.oracle "constructed equal 100MB pair hashed unequal" '"verdict":"FIXTURE-BROKEN"'
  local ledger="$d/ledger.tsv"
  printf "$hdr\n" > "$ledger"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-huge\n' "$src" "$s_sha" "$vcopy" "$v_sha" >> "$ledger"
  local snap_before snap_after
  snap_before=$(snapshot "$d")
  run_best 180 /usr/bin SOUJI_LEDGER="$ledger" SHOKUNIN_ROOT="$d" -- "$src"
  local v=PASS why=""
  saw_verdict SAFE || { v=FAIL; why="not SAFE on a matching 100MB sparse pair"; }
  saw_receipt moved-to-obsidian || { v=FAIL; why="receipt is not moved-to-obsidian"; }
  [ "$LAST_RC" = 124 ] && { v=FAIL; why="timeout on the 100MB target"; }
  snap_after=$(snapshot "$d")
  [ "$snap_before" = "$snap_after" ] || { v=FAIL; why="the tool mutated the fixture (read-only violated)"; }
  record N1 n 1 "SAFE(moved-to-obsidian) on 100MB sparse; fixture untouched; within 180s" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note N1.note "$why" "\"oracle_src_sha\":\"$s_sha\",\"oracle_vault_sha\":\"$v_sha\""
  note N1.sizes "100MB sparse fixture geometry" \
    "\"logical_bytes\":$bytes,\"src_apparent\":$(du -B1 --apparent-size "$src" | cut -f1),\"src_disk\":$(du -B1 "$src" | cut -f1),\"vault_disk\":$(du -B1 "$vcopy" | cut -f1)"

  # N2 — identical size, identical mtime, one byte differs at 50MB -> NOT-SAFE.
  #      Defeats every size-, mtime- and inode-based shortcut.
  local src2="$repo/notes/huge-b.bin" v2="$vault/huge-b.bin"
  sparse_file "$src2" "$bytes"
  cp --sparse=always -- "$src2" "$v2" 2>/dev/null || cp -- "$src2" "$v2"
  printf 'X' | dd of="$v2" bs=1 seek=$(( 50 * 1024 * 1024 )) conv=notrunc status=none
  local ts='2026-01-01 00:00:00'
  touch -d "$ts" -- "$src2" "$v2"
  local src2_sha; src2_sha=$(sha256sum -- "$src2" | cut -d' ' -f1)
  local v2_sha; v2_sha=$(sha256sum -- "$v2" | cut -d' ' -f1)
  [ "$src2_sha" != "$v2_sha" ] || note N2.oracle "constructed byte-differing pair hashed equal" '"verdict":"FIXTURE-BROKEN"'
  local ledger2="$d/ledger2.tsv"
  printf "$hdr\n" > "$ledger2"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-huge-byte-diff\n' "$src2" "$src2_sha" "$v2" "$src2_sha" >> "$ledger2"
  run_best 180 /usr/bin SOUJI_LEDGER="$ledger2" SHOKUNIN_ROOT="$d" -- "$src2"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="timeout"
  elif saw_verdict SAFE; then v=FAIL; why="FALSE-SAFE: same size+mtime, vault content differs at 50MB"; fi
  record N2 n 1 "NOT-SAFE when the vault byte differs at 50MB though size and mtime match" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note N2.note "$why" "\"src_sha\":\"$src2_sha\",\"vault_sha\":\"$v2_sha\",\"same_size\":true,\"same_mtime\":true"

  # N3 — vault copy one byte short.
  local src3="$repo/notes/huge-c.bin" v3="$vault/huge-c.bin"
  sparse_file "$src3" "$bytes"
  sparse_file "$v3" $(( bytes - 1 ))
  local ledger3="$d/ledger3.tsv"
  printf "$hdr\n" > "$ledger3"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-huge-short\n' "$src3" \
    "$(sha256sum -- "$src3" | cut -d' ' -f1)" "$v3" "$(sha256sum -- "$src3" | cut -d' ' -f1)" >> "$ledger3"
  run_best 180 /usr/bin SOUJI_LEDGER="$ledger3" SHOKUNIN_ROOT="$d" -- "$src3"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="timeout"
  elif saw_verdict SAFE; then v=FAIL; why="FALSE-SAFE on a truncated vault copy"; fi
  record N3 n 0 "NOT-SAFE when the vault copy is one byte short" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  [ -n "$why" ] && note N3.note "$why"

  # N4 — the independent sha256sum oracle itself.
  v=PASS
  { [ "$s_sha" = "$v_sha" ] && [ "$src2_sha" != "$v2_sha" ]; } || v=FAIL
  record N4 n 1 "sha256sum oracle: N1 pair equal, N2 pair differs" \
    0 "0.00" "oracle cross-check" "$v"
}

# case_o: vault file modified between the CLI read and the fallback read.
case_o() {
  local d="$WORK/o"; mkdir -p "$d"
  local repo="$d/repo-shokunin" vault="$d/vault"
  mk_repo "$repo" >/dev/null
  mkdir -p "$vault" "$repo/notes"
  local hdr='source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

  # O1 — the CLI reads the honest hash, then the vault file changes underneath
  #      (mutation happens inside the mock, i.e. between the CLI read and any
  #      fallback read the tool performs afterwards).
  local src="$repo/notes/racy.txt" vf="$vault/racy.txt"
  printf 'racy original payload\n' > "$src"
  cp -- "$src" "$vf"
  local s_sha v_sha
  s_sha=$(sha256sum -- "$src" | cut -d' ' -f1)
  v_sha=$(sha256sum -- "$vf" | cut -d' ' -f1)
  local ledger="$d/ledger.tsv"
  printf "$hdr\n" > "$ledger"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-racy\n' "$src" "$s_sha" "$vf" "$v_sha" >> "$ledger"
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=mutate MOCK_VAULT_FILE="$vf" \
    MOCK_LOG="$d/mock-o1.log" SOUJI_LEDGER="$ledger" SHOKUNIN_ROOT="$d" -- --cli "$src"
  local final_sha; final_sha=$(sha256sum -- "$vf" | cut -d' ' -f1)
  local v=PASS why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang on the racy vault"
  elif [ "$LAST_RC" != 0 ] && [ "$LAST_RC" != 2 ]; then
    v=FAIL; why="abnormal exit rc=$LAST_RC on the racy vault (crash, no verdict produced)"
  elif [ -z "$LAST_STDOUT" ]; then
    v=FAIL; why="no verdict emitted on the racy vault"
  elif saw_verdict SAFE; then
    if [ "$final_sha" = "$v_sha" ]; then why="SAFE and the final content still matches the ledger"
    else v=FAIL; why="FALSE-SAFE: vault changed mid-read (ledger $v_sha -> actual $final_sha) and the tool still said SAFE"; fi
  fi
  record O1 o 1 "after a mid-read change the tool must not report SAFE unless final content matches" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  note O1.state "race state after the run" \
    "\"ledger_vault_sha\":\"$v_sha\",\"final_vault_sha\":\"$final_sha\",\"mutated\":$([ "$v_sha" = "$final_sha" ] && printf false || printf true),\"mock_invocations\":$(mock_calls "$d/mock-o1.log")"
  [ -n "$why" ] && note O1.note "$why"

  # O2 — the CLI lies: it asserts the ledger hash while the file does not have it.
  local src2="$repo/notes/liar.txt" vf2="$vault/liar.txt"
  printf 'liar source payload\n' > "$src2"
  printf 'DIFFERENT vault payload\n' > "$vf2"
  local s2 claim
  s2=$(sha256sum -- "$src2" | cut -d' ' -f1)
  claim=$(sha256sum -- "$src2" | cut -d' ' -f1)   # ledger+cli both claim the source hash
  local ledger2="$d/ledger2.tsv"
  printf "$hdr\n" > "$ledger2"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-liar\n' "$src2" "$s2" "$vf2" "$claim" >> "$ledger2"
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=stale MOCK_CLAIM_HASH="$claim" MOCK_VAULT_FILE="$vf2" \
    MOCK_LOG="$d/mock-o2.log" SOUJI_LEDGER="$ledger2" SHOKUNIN_ROOT="$d" -- --cli "$src2"
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang"
  elif [ "$LAST_RC" != 0 ] && [ "$LAST_RC" != 2 ]; then
    v=FAIL; why="abnormal exit rc=$LAST_RC when the cli lied (crash, no verdict produced)"
  elif [ -z "$LAST_STDOUT" ]; then
    v=FAIL; why="no verdict emitted when the cli lied"
  elif saw_verdict SAFE; then
    v=FAIL; why="FALSE-SAFE: trusted the cli claim over the actual file (no cli-disagreement)"
  fi
  record O2 o 1 "lying cli + non-matching file => NOT-SAFE (cli-disagreement or hash mismatch)" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  note O2.state "lying-cli state" \
    "\"claimed_sha\":\"$claim\",\"actual_vault_sha\":\"$(sha256sum -- "$vf2" | cut -d' ' -f1)\",\"mock_invocations\":$(mock_calls "$d/mock-o2.log")"
  [ -n "$why" ] && note O2.note "$why"

  # O3 — control: honest CLI, matching pair, ledger row present -> SAFE.
  #      Binding only when the tool actually implements a CLI path; otherwise
  #      it cannot be exercised and is reported N/A rather than failed.
  local src3="$repo/notes/honest.txt" vf3="$vault/honest.txt"
  printf 'honest payload\n' > "$src3"
  cp -- "$src3" "$vf3"
  local ledger3="$d/ledger3.tsv"
  printf "$hdr\n" > "$ledger3"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-control\n' "$src3" \
    "$(sha256sum -- "$src3" | cut -d' ' -f1)" "$vf3" "$(sha256sum -- "$vf3" | cut -d' ' -f1)" >> "$ledger3"
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=ok MOCK_VAULT_FILE="$vf3" MOCK_LOG="$d/mock-o3.log" \
    SOUJI_LEDGER="$ledger3" SHOKUNIN_ROOT="$d" -- --cli "$src3"
  local cli3_rc=$LAST_RC
  if [ "$cli3_rc" = 2 ]; then
    record_na O3 o "tool rejects --cli (rc=2): no CLI path exists to control-test"
  else
    v=PASS; why=""
    saw_receipt moved-to-obsidian || { v=FAIL; why="control did not reach SAFE(moved-to-obsidian)"; }
    record O3 o 0 "control: honest cli + matching pair + ledger row => SAFE(moved-to-obsidian)" \
      "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
    [ -n "$why" ] && note O3.note "$why"
  fi

  # O5 — rename-swap TOCTOU: the vault path is atomically replaced by a
  #      same-size, same-mtime file between the CLI read and any later read.
  #      Only a content hash taken after the swap can catch this.
  local src5="$repo/notes/swap.txt" vf5="$vault/swap.txt"
  printf 'swap original payload 0123456789\n' > "$src5"
  cp -- "$src5" "$vf5"
  local s5 v5
  s5=$(sha256sum -- "$src5" | cut -d' ' -f1)
  v5=$(sha256sum -- "$vf5" | cut -d' ' -f1)
  local ledger5="$d/ledger5.tsv"
  printf "$hdr\n" > "$ledger5"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-swap\n' "$src5" "$s5" "$vf5" "$v5" >> "$ledger5"
  local swap_bytes; swap_bytes=$(stat -c %s -- "$vf5")
  run_tool "$CLI_TIMEOUT" "$MOCK_DIR" MOCK_MODE=swap MOCK_VAULT_FILE="$vf5" \
    MOCK_MUTATE_BYTES="$swap_bytes" MOCK_MUTATE_CHAR='Z' MOCK_LOG="$d/mock-o5.log" \
    SOUJI_LEDGER="$ledger5" SHOKUNIN_ROOT="$d" -- --cli "$src5"
  local final5; final5=$(sha256sum -- "$vf5" | cut -d' ' -f1)
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang on the rename swap"
  elif [ "$LAST_RC" != 0 ] && [ "$LAST_RC" != 2 ]; then
    v=FAIL; why="abnormal exit rc=$LAST_RC on the rename swap (crash, no verdict produced)"
  elif [ -z "$LAST_STDOUT" ]; then
    v=FAIL; why="no verdict emitted on the rename swap"
  elif saw_verdict SAFE; then
    if [ "$final5" = "$v5" ]; then why="SAFE and the vault content still matches the ledger"
    else v=FAIL; why="FALSE-SAFE: vault was atomically replaced (same size/mtime) and the tool still said SAFE"; fi
  fi
  record O5 o 1 "rename-swap mid-read => no SAFE unless final content matches the ledger" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  note O5.state "rename-swap state" \
    "\"ledger_vault_sha\":\"$v5\",\"final_vault_sha\":\"$final5\",\"same_size\":true,\"swapped\":$([ "$v5" = "$final5" ] && printf false || printf true)"
  [ -n "$why" ] && note O5.note "$why"

  # O4 — the fallback contract itself: no cli binary anywhere on PATH, a
  #      matching ledger pair, and the tool must still reach
  #      SAFE(moved-to-obsidian) via sha256sum alone. This is the path the
  #      host actually depends on (the official CLI is non-functional here).
  local src4="$repo/notes/fallback.txt" vf4="$vault/fallback.txt"
  printf 'fallback payload\n' > "$src4"
  cp -- "$src4" "$vf4"
  local ledger4="$d/ledger4.tsv"
  printf "$hdr\n" > "$ledger4"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-fallback\n' "$src4" \
    "$(sha256sum -- "$src4" | cut -d' ' -f1)" "$vf4" "$(sha256sum -- "$vf4" | cut -d' ' -f1)" >> "$ledger4"
  local emptybin="$d/emptybin"; mkdir -p "$emptybin"
  run_best "$CLI_TIMEOUT" "$emptybin" SOUJI_LEDGER="$ledger4" SHOKUNIN_ROOT="$d" -- "$src4"
  v=PASS; why=""
  saw_receipt moved-to-obsidian || { v=FAIL; why="fallback path did not resolve the ledger receipt"; }
  record O4 o 1 "no cli present + matching ledger pair => SAFE via the sha256sum fallback" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  note O4.mode "mode used for the fallback control" "\"cli_mode\":\"$CLI_MODE\""
  [ -n "$why" ] && note O4.note "$why"

  # O6 — real race on the fallback path: a background mutator flips the vault
  #      file repeatedly while the tool hashes it. There is no CLI to blame
  #      here, so this is the TOCTOU the tool actually owns. Oracle: if the
  #      tool reports SAFE, a re-hash taken immediately afterwards must still
  #      match the ledger; otherwise it approved a file that no longer exists
  #      in that state.
  local src6="$repo/notes/race-fallback.txt" vf6="$vault/race-fallback.txt"
  printf 'race fallback original\n' > "$src6"
  cp -- "$src6" "$vf6"
  local v6; v6=$(sha256sum -- "$vf6" | cut -d' ' -f1)
  local ledger6="$d/ledger6.tsv"
  printf "$hdr\n" > "$ledger6"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tadv53-fallback-race\n' "$src6" \
    "$(sha256sum -- "$src6" | cut -d' ' -f1)" "$vf6" "$v6" >> "$ledger6"
  local mut_bytes; mut_bytes=$(stat -c %s -- "$vf6")
  (
    end=$(( $(date +%s) + 6 ))
    while [ "$(date +%s)" -lt "$end" ]; do
      printf '%s' "$(head -c "$mut_bytes" /dev/zero | tr '\0' 'R')" > "$vf6.tmp"
      mv -f -- "$vf6.tmp" "$vf6"
      printf '%s' "$(head -c "$mut_bytes" /dev/zero | tr '\0' 'S')" > "$vf6.tmp"
      mv -f -- "$vf6.tmp" "$vf6"
    done
    printf '%s' "$(head -c "$mut_bytes" /dev/zero | tr '\0' 'X')" > "$vf6"
  ) &
  local mpid=$!
  run_best "$CLI_TIMEOUT" "$emptybin" SOUJI_LEDGER="$ledger6" SHOKUNIN_ROOT="$d" -- "$src6"
  kill "$mpid" 2>/dev/null; wait "$mpid" 2>/dev/null
  local final6; final6=$(sha256sum -- "$vf6" | cut -d' ' -f1)
  v=PASS; why=""
  if [ "$LAST_RC" = 124 ]; then v=FAIL; why="hang under a concurrent writer"
  elif saw_verdict SAFE; then
    if [ "$final6" = "$v6" ]; then why="SAFE and the final content still matches the ledger"
    else v=FAIL; why="FALSE-SAFE: SAFE while the vault file was being rewritten (ledger $v6 -> actual $final6)"; fi
  fi
  record O6 o 1 "concurrent writer on the fallback path => no SAFE unless final content matches" \
    "$LAST_RC" "$LAST_SECS" "$LAST_OUT" "$v"
  note O6.state "fallback race state" \
    "\"ledger_vault_sha\":\"$v6\",\"final_vault_sha\":\"$final6\",\"changed\":$([ "$v6" = "$final6" ] && printf false || printf true),\"cli_mode\":\"$CLI_MODE\""
  [ -n "$why" ] && note O6.note "$why"
}

# ------------------------------------------------------------------- main --

[ -x "$MOCK_DIR/obsidian" ] || chmod +x "$MOCK_DIR/obsidian" 2>/dev/null || true
for alias in obsidian-cli obsidian-cli-inspector; do
  [ -e "$MOCK_DIR/$alias" ] || ln -s obsidian "$MOCK_DIR/$alias" 2>/dev/null || true
done

TOOL=$(readlink -m -- "$TOOL")
if [ ! -f "$TOOL" ]; then
  printf 'adv53-harness: tool not found: %s\n' "$TOOL" >&2
  exit 1
fi
TOOL_SHA=$(sha256sum -- "$TOOL" | cut -d' ' -f1)
TOOL_HAS_CLI=$(grep -c -- '--cli' "$TOOL" || true)
TOOL_CLI_MENTIONS=$(grep -ci 'cli' "$TOOL" || true)
TOOL_BOUNDED=$(grep -cE '^[^#]*timeout ' "$TOOL" || true)
# A tool that *mentions* /usr/bin/obsidian is not a hazard — mentioning it in a
# comment that forbids it is exactly the safe behaviour. Only an *executable*
# reference (a line that is not a comment and invokes the launcher) is.
GUI_ABS_REF=$(grep -n '/usr/bin/obsidian' "$TOOL" 2>/dev/null | grep -vE '^[0-9]+:[[:space:]]*#' | grep -cE '(^|[^[:alnum:]_/.-])(exec|eval|bash|sh|source|\.)[[:space:]].*/usr/bin/obsidian|^\s*/usr/bin/obsidian' || true)
GUI_ABS_REF=${GUI_ABS_REF// /}

WORK=$(mktemp -d "${TMPDIR:-/tmp}/adv53.XXXXXX")
mkdir -p "$WORK"

# GUARD_DIR — the last line of defence. Prepend a directory holding a stub for
# every name that could reach the real desktop-app launcher, so that even a bug
# in the harness (e.g. an unintended command substitution) records a hazard
# instead of launching the operator's app.
GUARD_DIR="$WORK/guard"; mkdir -p "$GUARD_DIR"
cat > "$GUARD_DIR/obsidian" <<'GUARD'
#!/usr/bin/env bash
printf 'guard: refused to execute the real obsidian launcher: %s\n' "$*" >&2
printf '%s\n' "$*" >>"${GUARD_SENTINEL:-/dev/null}"
exit 127
GUARD
chmod +x "$GUARD_DIR/obsidian"
for n in obsidian-cli electron43 electron; do
  ln -sf obsidian "$GUARD_DIR/$n" 2>/dev/null || true
done
GUARD_SENTINEL="$WORK/guard-hits.log"; : > "$GUARD_SENTINEL"; export GUARD_SENTINEL
guard_hits() { awk 'END{printf "%d", NR+0}' "$GUARD_SENTINEL" 2>/dev/null || printf '0'; }

HAZARD=""
if [ "${GUI_ABS_REF:-0}" != 0 ]; then
  HAZARD="tool contains an executable reference to /usr/bin/obsidian (GUI launcher) — cli cases not executed"
fi

case "$ONLY" in
  ""|m) if [ -z "$HAZARD" ]; then case_m; else note M.all "$HAZARD" '"verdict":"HARNESS-REFUSED"'; fi ;;
esac
case "$ONLY" in
  ""|n) case_n ;;
esac
case "$ONLY" in
  ""|o) if [ -z "$HAZARD" ]; then case_o; else note O.all "$HAZARD" '"verdict":"HARNESS-REFUSED"'; fi ;;
esac

[ "$GUI_SEEN" = 1 ] && note HAZARD.gui "an obsidian.asar process appeared during probes and was killed"

{
  printf '{\n'
  printf '  "seat": "S53",\n'
  printf '  "role": "adversarial tester: obsidian --cli contract, huge-file hash, racy vault",\n'
  printf '  "round": 4,\n'
  printf '  "run_utc": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "tool": {"path": "%s", "sha256": "%s", "has_cli_flag": %s, "cli_mentions": %s, "bounded": %s, "gui_exec_refs": %s},\n' \
    "$(jesc "$TOOL")" "$TOOL_SHA" \
    "$([ "${TOOL_HAS_CLI:-0}" != 0 ] && printf true || printf false)" "${TOOL_CLI_MENTIONS// /}" \
    "$([ "${TOOL_BOUNDED:-0}" != 0 ] && printf true || printf false)" "${GUI_ABS_REF:-0}"
  printf '  "harness": {"path": "%s", "sha256": "%s", "cli_timeout_s": %s, "huge_mb": %s, "guard_dir": "%s", "guard_hits": %s},\n' \
    "$(jesc "$SCRIPT_PATH")" "$(sha256sum -- "$SCRIPT_PATH" | cut -d' ' -f1)" "$CLI_TIMEOUT" "$HUGE_MB" \
    "$(jesc "$GUARD_DIR")" "$(guard_hits)"
  printf '  "counts": {"pass": %s, "fail": %s, "na": %s},\n' "$PASS" "$FAIL" "$NA"
  printf '  "cases": [\n'
  local_first=1
  for r in "${RESULTS[@]}"; do
    if [ "$local_first" = 1 ]; then local_first=0; else printf ',\n'; fi
    printf '    %s' "$r"
  done
  printf '\n  ]\n}\n'
} > "$OUT"

printf '\nadv53-harness: tool=%s pass=%s fail=%s -> %s\n' "$TOOL" "$PASS" "$FAIL" "$OUT"
[ "$FAIL" = 0 ]
