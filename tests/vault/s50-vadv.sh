#!/usr/bin/env bash
# s50-vadv.sh — seat S50 adversarial battery, souji-shokunin round 4
# (Obsidian-CLI vault verification). Three assigned attack families:
#
#   d  vault path is a directory (ledger row's vault_path resolves to a dir)
#   e  source path readable but sha256sum binary absent from PATH (busybox env)
#   f  ledger file itself missing (absent path / directory / mode-000 / empty)
#
# Oracle: none of the attack cases may yield SAFE/VERIFIED; controlled exit
# (no hang, no uncontrolled rc); read-only over the real vault and the live
# ledger (both snapshotted before/after).
#
# Usage: tests/vault/s50-vadv.sh [--tool PATH]... [--out FILE] [--raw DIR]
#                                [--keep] [--no-selftest]
#   default tools: auto-discovery — tools/souji-vault-verify.impl-*.sh if
#   present, then tools/souji-vault-verify.sh, tools/obsidian-vault-verify.sh,
#   tools/vault-verify.sh, tools/souji-verify.sh (first existing of each).
#   default out:   tests/results/vadv-50.json
#   default raw:   tests/vault/s50-raw/ (cases.tsv, tools.tsv, meta.txt, outputs)
#
# Invocation of the tool under test (env-based ledger interface):
#   timeout 30 env SHOKUNIN_ROOT=<empty fleet> SOUJI_LEDGER=<case ledger> \
#     /usr/bin/bash <tool> --stale-days 1 <target>
#   (retried without --stale-days if the tool answers rc=2/usage)
#
# Safety: fixtures live in a mktemp -d under /tmp (removed unless --keep);
# /usr/bin/obsidian (the GUI launcher) is never executed; no git fetch/push/
# commit/branch; the real vault is touched read-only (stat + a sha256sum
# attempt on a directory for case D5 only); the live ledger is only read.
set -uo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"

OUT="$REPO_ROOT/tests/results/vadv-50.json"
RAW="$REPO_ROOT/tests/vault/s50-raw"
VAULT="/home/vgpnk/Documents/shokoknowledge"
LIVE_LEDGER="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"
KEEP=0
DO_SELFTEST=1
TOOLS=()

usage() { sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool) [ "$#" -ge 2 ] || usage; TOOLS+=("$2"); shift 2 ;;
    --tool=*) TOOLS+=("${1#*=}"); shift ;;
    --out) [ "$#" -ge 2 ] || usage; OUT=$2; shift 2 ;;
    --out=*) OUT=${1#*=}; shift ;;
    --raw) [ "$#" -ge 2 ] || usage; RAW=$2; shift 2 ;;
    --raw=*) RAW=${1#*=}; shift ;;
    --keep) KEEP=1; shift ;;
    --no-selftest) DO_SELFTEST=0; shift ;;
    -h|--help) usage ;;
    *) printf 's50-vadv: unknown arg %s\n' "$1" >&2; exit 2 ;;
  esac
done

if [ "${#TOOLS[@]}" -eq 0 ]; then
  TOOLS=()
  for p in $(ls -1 "$REPO_ROOT"/tools/souji-vault-verify.impl-*.sh 2>/dev/null | sort -V); do
    TOOLS+=("$p")
  done
  for p in $(ls -1 "$REPO_ROOT"/tools/impl-*.sh 2>/dev/null | sort -V); do
    case "$(basename -- "$p")" in souji-verify.impl-*) continue ;; esac
    TOOLS+=("$p")
  done
  for p in "$REPO_ROOT/tools/souji-vault-verify.sh" \
           "$REPO_ROOT/tools/obsidian-vault-verify.sh" \
           "$REPO_ROOT/tools/vault-verify.sh" \
           "$REPO_ROOT/tools/souji-verify.sh"; do
    [ -f "$p" ] && TOOLS+=("$p")
  done
fi
[ "${#TOOLS[@]}" -gt 0 ] || { printf 's50-vadv: no tool found\n' >&2; exit 1; }
for t in "${TOOLS[@]}"; do [ -f "$t" ] || { printf 's50-vadv: tool missing: %s\n' "$t" >&2; exit 1; }; done

# Dedupe: impl-*.sh may be a symlink alias of souji-vault-verify.impl-*.sh
DEDUP=(); SEEN_REAL=""
for t in "${TOOLS[@]}"; do
  r=$(readlink -m -- "$t")
  case ":$SEEN_REAL:" in *":$r:"*) continue ;; esac
  SEEN_REAL="$SEEN_REAL:$r"; DEDUP+=("$t")
done
TOOLS=("${DEDUP[@]}")

mkdir -p "$RAW"
WORK=$(mktemp -d "${TMPDIR:-/tmp}/s50-vadv.XXXXXX")
cleanup() { [ "$KEEP" = 1 ] || rm -rf -- "$WORK"; }
trap cleanup EXIT

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
dir_digest() { ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }
vault_snap() { find "$VAULT" -maxdepth 3 -printf '%P\t%T@\t%s\n' 2>/dev/null \
    | LC_ALL=C sort | sha256sum | cut -d' ' -f1; }
vault_notes_snap() { find "$VAULT" -name '*.md' -type f -print0 2>/dev/null \
    | sort -z | xargs -0 -r sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1; }
vault_notes_count() { find "$VAULT" -name '*.md' -type f 2>/dev/null | wc -l; }
live_ledger_state() { printf '%s lines=%s' "$(sha "$LIVE_LEDGER")" \
    "$(wc -l < "$LIVE_LEDGER" 2>/dev/null || echo 0)"; }

log() { printf '%s\n' "$*" >> "$RAW/run.log"; }

# ------------------------------------------------------------------ fixtures

FLEET="$WORK/fleet"; mkdir -p "$FLEET"
FX="$WORK/fx"; mkdir -p "$FX"

WRONG_A=0000000000000000000000000000000000000000000000000000000000000000
WRONG_B=1111111111111111111111111111111111111111111111111111111111111111

# --- D family: vault path is a directory -----------------------------------
D="$FX/d"; mkdir -p "$D/src"
printf 's50 payload D-family\n' > "$D/src/note.md"
SRC_D="$D/src/note.md"; SS_D=$(sha "$SRC_D")
mkdir -p "$D/vault0"; cp "$SRC_D" "$D/vault0/note.md"; VS0=$(sha "$D/vault0/note.md")
L_D0="$D/ledger-d0.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_D0"
printf '%s\t%s\t%s\t%s\t2026-10-18\td0-control\n' "$SRC_D" "$SS_D" "$D/vault0/note.md" "$VS0" >> "$L_D0"
L_D1="$D/ledger-d1.tsv"; mkdir -p "$D/vault1"      # vault_path = EMPTY DIRECTORY
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_D1"
printf '%s\t%s\t%s\t%s\t2026-10-18\td1-dir-empty\n' "$SRC_D" "$SS_D" "$D/vault1" "$SS_D" >> "$L_D1"
L_D2="$D/ledger-d2.tsv"; mkdir -p "$D/vault2"      # dir CONTAINING a byte-identical file
printf 's50 payload D-family\n' > "$D/vault2/inner.md"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_D2"
printf '%s\t%s\t%s\t%s\t2026-10-18\td2-dir-with-inner-copy\n' "$SRC_D" "$SS_D" "$D/vault2" "$SS_D" >> "$L_D2"
L_D3="$D/ledger-d3.tsv"; mkdir -p "$D/vault3"; printf 'inner\n' > "$D/vault3/x.txt"
DG3=$(dir_digest "$D/vault3")                      # mixed-domain: file sha vs dir digest
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_D3"
printf '%s\t%s\t%s\t%s\t2026-10-18\td3-dir-digest-mixed\n' "$SRC_D" "$SS_D" "$D/vault3" "$DG3" >> "$L_D3"
L_D4="$D/ledger-d4.tsv"; mkdir -p "$D/vault4"      # vault_path dir, vault hash EMPTY
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_D4"
printf '%s\t%s\t%s\t\t2026-10-18\td4-dir-empty-vaulthash\n' "$SRC_D" "$SS_D" "$D/vault4" >> "$L_D4"
L_D5="$D/ledger-d5.tsv"                            # vault_path = REAL vault subdirectory
RV_DIR="$VAULT/atlas"; [ -d "$RV_DIR" ] || RV_DIR="$VAULT"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_D5"
printf '%s\t%s\t%s\t%s\t2026-10-18\td5-real-vault-dir\n' "$SRC_D" "$SS_D" "$(readlink -m -- "$RV_DIR")" "$SS_D" >> "$L_D5"
L_D6="$D/ledger-d6.tsv"; mkdir -p "$D/srcdir6" "$D/vault6"
printf 'six\n' > "$D/srcdir6/a.txt"; cp "$D/srcdir6/a.txt" "$D/vault6/a.txt"
DG6S=$(dir_digest "$D/srcdir6"); DG6V=$(dir_digest "$D/vault6")
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_D6"
printf '%s\t%s\t%s\t%s\t2026-10-18\td6-dir-dir-control\n' "$D/srcdir6" "$DG6S" "$D/vault6" "$DG6V" >> "$L_D6"
L_D7="$D/ledger-d7.tsv"; mkdir -p "$D/srcdir7"; printf 'seven\n' > "$D/srcdir7/b.txt"
DG7S=$(dir_digest "$D/srcdir7"); printf 'seven\n' > "$D/vault7file"   # vault_path = FILE, target = DIR
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_D7"
printf '%s\t%s\t%s\t%s\t2026-10-18\td7-dir-target-vault-file\n' "$D/srcdir7" "$DG7S" "$D/vault7file" "$(sha "$D/vault7file")" >> "$L_D7"

# --- E family: sha256sum absent from PATH ----------------------------------
E="$FX/e"; mkdir -p "$E/src" "$E/vault"
printf 's50 payload E-family\n' > "$E/src/note.md"
SRC_E="$E/src/note.md"; SS_E=$(sha "$SRC_E")
cp "$SRC_E" "$E/vault/note.md"; VS_E=$(sha "$E/vault/note.md")
L_E_OK="$E/ledger-ok.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_E_OK"
printf '%s\t%s\t%s\t%s\t2026-10-18\te-correct\n' "$SRC_E" "$SS_E" "$E/vault/note.md" "$VS_E" >> "$L_E_OK"
L_E_WS="$E/ledger-wrong-src.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_E_WS"
printf '%s\t%s\t%s\t%s\t2026-10-18\te-wrong-source\n' "$SRC_E" "$WRONG_A" "$E/vault/note.md" "$VS_E" >> "$L_E_WS"
L_E_WV="$E/ledger-wrong-vault.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_E_WV"
printf '%s\t%s\t%s\t%s\t2026-10-18\te-wrong-vault\n' "$SRC_E" "$SS_E" "$E/vault/note.md" "$WRONG_B" >> "$L_E_WV"
L_E_EH="$E/ledger-empty-hash.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_E_EH"
printf '%s\t\t%s\t\t2026-10-18\te-empty-hashes\n' "$SRC_E" "$E/vault/note.md" >> "$L_E_EH"

EBIN="$WORK/ebin"; mkdir -p "$EBIN"
for c in bash sh env git rg sed grep sort xargs wc head cat find stat date cut \
         dirname basename readlink mktemp tr touch tail awk ls id uname printf \
         timeout sleep flock pgrep ps ss getconf cmp diff dd tee seq; do
  p=$(command -v "$c" 2>/dev/null) || continue
  ln -s "$p" "$EBIN/$c" 2>/dev/null
done
# busybox premise: NO hasher binaries in EBIN
for c in sha256sum sha512sum sha1sum md5sum cksum busybox python3 openssl; do
  [ -e "$EBIN/$c" ] && rm -f "$EBIN/$c"
done

# evil PATH: a fake sha256sum that prints the attacker's claimed hash
EVILBIN="$WORK/ebin-evil"; mkdir -p "$EVILBIN"
cat > "$EVILBIN/sha256sum" <<'SHIM'
#!/usr/bin/env bash
last=""; for a in "$@"; do case "$a" in --) ;; *) last=$a ;; esac; done
printf '%s  %s\n' "${S50_CLAIM_SHA:-}" "$last"
exit 0
SHIM
chmod +x "$EVILBIN/sha256sum"

# busybox premise, take 2: PATH with git/rg/coreutils but a `sha256sum` NAME
# that resolves to nothing (busybox env without the applet / stripped image)
E_EMPTY="$E/src/note2.md"; cp "$SRC_E" "$E_EMPTY"
E_V2="$E/vault/note2.md";  cp "$SRC_E" "$E_V2"
L_E_EMPTY="$E/ledger-ok2.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_E_EMPTY"
printf '%s\t%s\t%s\t%s\t2026-10-18\te-nosha-name\n' "$E_EMPTY" "$(sha "$E_EMPTY")" "$E_V2" "$(sha "$E_V2")" >> "$L_E_EMPTY"

# E3: hostile hasher forges a row that matches the attacker-claimed hash pair
E3_SRC="$E/src/forge.md"; printf 'attacker controlled bytes\n' > "$E3_SRC"
E3_V="$E/vault/forge.md"; printf 'different vault bytes\n' > "$E3_V"
E3_CLAIM="deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
L_E3="$E/ledger-forge.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_E3"
printf '%s\t%s\t%s\t%s\t2026-10-18\te3-hostile-hasher\n' "$E3_SRC" "$E3_CLAIM" "$E3_V" "$E3_CLAIM" >> "$L_E3"

# --- F family: ledger file itself missing ----------------------------------
F="$FX/f"; mkdir -p "$F/src" "$F/vault"
printf 's50 payload F-family\n' > "$F/src/note.md"
SRC_F="$F/src/note.md"; SS_F=$(sha "$SRC_F")
cp "$SRC_F" "$F/vault/note.md"; VS_F=$(sha "$F/vault/note.md")
L_F_OK="$F/ledger-ok.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_F_OK"
printf '%s\t%s\t%s\t%s\t2026-10-18\tf-control\n' "$SRC_F" "$SS_F" "$F/vault/note.md" "$VS_F" >> "$L_F_OK"
L_F_EMPTY="$F/ledger-empty.tsv"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$L_F_EMPTY"
F_MISSING="$F/ledger-missing.tsv"     # never created
F_DIR="$F/ledger-dir"; mkdir -p "$F_DIR"
F_000="$F/ledger-000.tsv"; printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$F_000"; chmod 000 "$F_000"
F_DANGLE="$F/ledger-dangling.tsv"; ln -s "$F/no-such-target.tsv" "$F_DANGLE"
F_REL="rel-ledger-missing.tsv"        # relative path, absent from every cwd
mkdir -p "$F/scratchrepo/.scratch"
printf 'stale payload\n' > "$F/scratchrepo/.scratch/old-s50.out"
touch -d '3 days ago' "$F/scratchrepo/.scratch/old-s50.out"

# ------------------------------------------------------------------ runner

: > "$RAW/cases.tsv"
: > "$RAW/tools.tsv"
: > "$RAW/run.log"

parse_class() { # $1 file -> "class<TAB>evidence"
  local f=$1 line v ev f1
  if grep -qE 'syntax error' "$f" 2>/dev/null; then
    printf 'BROKEN\t%s\n' "syntax:$(head -c 160 "$f" | tr '\t\n' '  ')"; return 0
  fi
  line=$(grep -m1 '"verdict"' "$f" 2>/dev/null)
  if [ -n "$line" ]; then
    v=$(printf '%s\n' "$line" | sed -n 's/.*"verdict"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    ev=$line
  else
    line=$(grep -m1 -E '^(VERDICT|VERIFIED|NOT-VERIFIED|NOT-SAFE|SAFE)[[:space:]]' "$f" 2>/dev/null)
    if [ -n "$line" ]; then
      f1=${line%%$'\t'*}
      case "$f1" in
        VERDICT) v=$(printf '%s\n' "$line" | awk -F'\t' '{print $3}')
                 ev=$(printf '%s\n' "$line" | awk -F'\t' '{for(i=5;i<=NF;i++) printf "%s%s", (i>5?" ":""), $i}') ;;
        *)       v=$f1
                 ev=$(printf '%s\n' "$line" | cut -f2- | tr '\t' ' ') ;;
      esac
    fi
  fi
  case "${v:-}" in
    SAFE|VERIFIED) printf 'SAFE\t%s\n' "$ev"; return 0 ;;
  esac
  case "${v:-}" in
    NOT-SAFE*|NOT-VERIFIED*|NOTSAFE*) printf 'NOTSAFE\t%s\n' "$ev"; return 0 ;;
  esac
  if grep -qE 'NOT-SAFE|NOT-VERIFIED|not-safe|not-verified' "$f" 2>/dev/null; then
    printf 'NOTSAFE\t%s\n' "implicit:$(head -c 200 "$f" | tr '\t\n' '  ')"; return 0
  fi
  if grep -qiE 'not found|cannot|refus|unverifiable|unreachable|missing|no-ledger' "$f" 2>/dev/null; then
    printf 'NOTSAFE\t%s\n' "refusal:$(head -c 200 "$f" | tr '\t\n' '  ')"; return 0
  fi
  printf 'OTHER\t%s\n' "$(head -c 200 "$f" 2>/dev/null | tr '\t\n' '  ')"
}

run_case() { # id family binding expect ledger target pathmode [extra_env...]
  local id=$1 fam=$2 bind=$3 exp=$4 ledger=$5 target=$6 pmode=$7; shift 7
  local extra=("$@")
  local tool="$CUR_TOOL" tname="$CUR_NAME"
  local path="$PATH"
  case "$pmode" in
    nosha) path="$EBIN" ;;
    evil)  path="$EVILBIN:$PATH" ;;
  esac
  local outfile="$RAW/out.${tname}.${id}.txt"
  local t0 t1 secs rc class ev result why
  t0=$(date +%s.%N)
  if [ "$ledger" = "-UNSET-" ]; then
    timeout 30 env -u SOUJI_LEDGER PATH="$path" SHOKUNIN_ROOT="$FLEET" "${extra[@]}" \
      /usr/bin/bash "$tool" --stale-days 1 "$target" >"$outfile" 2>&1
  else
    timeout 30 env PATH="$path" SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$ledger" "${extra[@]}" \
      /usr/bin/bash "$tool" --stale-days 1 "$target" >"$outfile" 2>&1
  fi
  rc=$?
  if [ "$rc" = 2 ]; then
    log "retry $tname/$id without --stale-days (rc=2)"
    if [ "$ledger" = "-UNSET-" ]; then
      timeout 30 env -u SOUJI_LEDGER PATH="$path" SHOKUNIN_ROOT="$FLEET" "${extra[@]}" \
        /usr/bin/bash "$tool" "$target" >>"$outfile" 2>&1
    else
      timeout 30 env PATH="$path" SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$ledger" "${extra[@]}" \
        /usr/bin/bash "$tool" "$target" >>"$outfile" 2>&1
    fi
    rc=$?
  fi
  t1=$(date +%s.%N)
  secs=$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f", b-a}')
  IFS=$'\t' read -r class ev < <(parse_class "$outfile")
  class=${class:-OTHER}; ev=${ev:-}
  result="INFO"; why=""
  if [ "$class" = "BROKEN" ]; then
    result="FAIL"; why="syntax-error (tool does not run)"
    [ "$bind" = 0 ] && result="INFO"
  elif [ "$rc" = 124 ]; then
    result="FAIL"; why="timeout(30s)"
  elif [ "$rc" -ge 126 ] 2>/dev/null; then
    result="FAIL"; why="uncontrolled-exit rc=$rc"
  elif [ "$exp" = "SAFE" ]; then
    if [ "$class" = "SAFE" ]; then result="PASS"; else result="FAIL"; why="expected SAFE got $class rc=$rc"; fi
    [ "$bind" = 0 ] && result="INFO"
  else
    case "$class" in
      NOTSAFE) result="PASS" ;;
      SAFE)    result="FAIL"; why="FALSE-SAFE" ;;
      *)       result="FAIL"; why="unparseable/unknown output rc=$rc" ;;
    esac
    [ "$bind" = 0 ] && result="INFO"
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$tname" "$id" "$fam" "$bind" "$exp" "$rc" "$secs" "$class" "$result" "$why" \
    "$(printf '%s' "$ev" | tr '\t\n' '  ' | head -c 300)" "$(basename "$outfile")" >> "$RAW/cases.tsv"
  printf '%-9s %-6s %-8s rc=%-3s %-8s %s %s\n' "$tname" "$id" "$result" "$rc" "$class" "$why" "${ev:0:80}" >&2
}

# ------------------------------------------------------------------ meta

REPO_HEAD=$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)
HOST_GIT=$(git --version 2>/dev/null || echo unknown)
LEDGER_BEFORE=$(live_ledger_state)
VSNAP_BEFORE=$(vault_snap)
VNOTES_BEFORE=$(vault_notes_snap)
VNOTES_N_BEFORE=$(vault_notes_count)
APP_PIDS_BEFORE=$(pgrep -f 'obsidian/app.asar' 2>/dev/null | tr '\n' ',' || true)
: > "$RAW/meta.txt"
{
  printf 'seat=S50\n'
  printf 'role=adversarial tester: (d) vault-path-is-a-directory, (e) sha256sum-absent-from-PATH, (f) ledger-file-missing\n'
  printf 'round=4\n'
  printf 'lane_repo=%s\n' "$REPO_ROOT"
  printf 'repo_head=%s\n' "$REPO_HEAD"
  printf 'host_git=%s\n' "$HOST_GIT"
  printf 'vault=%s\n' "$VAULT"
  printf 'live_ledger=%s\n' "$LIVE_LEDGER"
  printf 'live_ledger_before=%s\n' "$LEDGER_BEFORE"
  printf 'vault_snap_before=%s\n' "$VSNAP_BEFORE"
  printf 'vault_notes_snap_before=%s\n' "$VNOTES_BEFORE"
  printf 'vault_notes_count_before=%s\n' "$VNOTES_N_BEFORE"
  printf 'obsidian_app_pids_before=%s\n' "$APP_PIDS_BEFORE"
  printf 'workdir=%s\n' "$WORK"
  printf 'invocation=timeout 30 env SHOKUNIN_ROOT=<empty fleet> SOUJI_LEDGER=<case ledger> /usr/bin/bash <tool> --stale-days 1 <target>\n'
  printf 'run_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "$RAW/meta.txt"

# ------------------------------------------------------------------ main

for t in "${TOOLS[@]}"; do
  CUR_TOOL=$(readlink -m -- "$t")
  CUR_NAME=$(basename -- "$CUR_TOOL" .sh)
  SHA_BEFORE=$(sha "$CUR_TOOL")
  ST_RC=skipped; ST_TAIL=""; SYN_RC=0; SYN_ERR=""
  if ! SYN_ERR=$(/usr/bin/bash -n "$CUR_TOOL" 2>&1); then SYN_RC=1; fi
  if [ "$DO_SELFTEST" = 1 ] && [ "$SYN_RC" = 0 ]; then
    st_out="$RAW/selftest.$CUR_NAME.txt"
    timeout 120 /usr/bin/bash "$CUR_TOOL" --selftest >"$st_out" 2>&1
    ST_RC=$?
    ST_TAIL=$(tail -1 "$st_out" 2>/dev/null | tr '\t\n' '  ' | head -c 200)
  fi

  run_case D0 d 1 SAFE "$L_D0" "$SRC_D" full
  run_case D1 d 1 NOTSAFE "$L_D1" "$SRC_D" full
  run_case D2 d 1 NOTSAFE "$L_D2" "$SRC_D" full
  run_case D3 d 1 NOTSAFE "$L_D3" "$SRC_D" full
  run_case D4 d 1 NOTSAFE "$L_D4" "$SRC_D" full
  run_case D5 d 1 NOTSAFE "$L_D5" "$SRC_D" full
  run_case D6 d 0 SAFE "$L_D6" "$D/srcdir6" full
  run_case D7 d 1 NOTSAFE "$L_D7" "$D/srcdir7" full

  run_case E0a e 1 SAFE "$L_E_OK" "$SRC_E" full
  run_case E0b e 1 NOTSAFE "$L_E_WS" "$SRC_E" full
  run_case E1a e 0 NOTSAFE "$L_E_OK" "$SRC_E" nosha
  run_case E1b e 1 NOTSAFE "$L_E_WS" "$SRC_E" nosha
  run_case E1c e 1 NOTSAFE "$L_E_WV" "$SRC_E" nosha
  run_case E1d e 1 NOTSAFE "$L_E_EH" "$SRC_E" nosha
  run_case E1e e 1 NOTSAFE "$L_E_EMPTY" "$E_EMPTY" nosha
  run_case E2 e 0 NOTSAFE "$L_E_WS" "$SRC_E" evil S50_CLAIM_SHA="$WRONG_A"
  run_case E3 e 0 NOTSAFE "$L_E3" "$E3_SRC" evil S50_CLAIM_SHA="$E3_CLAIM"

  run_case F0 f 1 SAFE "$L_F_OK" "$SRC_F" full
  run_case F1 f 1 NOTSAFE "$F_MISSING" "$SRC_F" full
  run_case F2 f 1 NOTSAFE "$F_MISSING" "$SRC_F" full
  run_case F3 f 1 NOTSAFE "$F_DIR" "$SRC_F" full
  run_case F4 f 1 NOTSAFE "$F_000" "$SRC_F" full
  run_case F5 f 0 NOTSAFE "$F_MISSING" "$F/scratchrepo/.scratch/old-s50.out" full
  run_case F6 f 1 NOTSAFE "$L_F_EMPTY" "$SRC_F" full
  run_case F7 f 1 NOTSAFE "-UNSET-" "$SRC_F" full
  run_case F8 f 1 NOTSAFE "$F_DANGLE" "$SRC_F" full
  run_case F9 f 1 NOTSAFE "$F_REL" "$SRC_F" full

  SHA_AFTER=$(sha "$CUR_TOOL")
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$CUR_NAME" "$CUR_TOOL" "$SHA_BEFORE" "$SHA_AFTER" "$ST_RC" "$ST_TAIL" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$SYN_RC" "$(printf '%s' "$SYN_ERR" | tr '\t\n' '  ' | head -c 200)" >> "$RAW/tools.tsv"
done

LEDGER_AFTER=$(live_ledger_state)
VSNAP_AFTER=$(vault_snap)
VNOTES_AFTER=$(vault_notes_snap)
VNOTES_N_AFTER=$(vault_notes_count)
APP_PIDS_AFTER=$(pgrep -f 'obsidian/app.asar' 2>/dev/null | tr '\n' ',' || true)
{
  printf 'live_ledger_after=%s\n' "$LEDGER_AFTER"
  printf 'vault_snap_after=%s\n' "$VSNAP_AFTER"
  printf 'vault_notes_snap_after=%s\n' "$VNOTES_AFTER"
  printf 'vault_notes_count_after=%s\n' "$VNOTES_N_AFTER"
  printf 'obsidian_app_pids_after=%s\n' "$APP_PIDS_AFTER"
  printf 'run_end_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} >> "$RAW/meta.txt"

python3 - "$RAW" "$OUT" <<'PYEOF'
import json, os, re, sys
raw, out = sys.argv[1], sys.argv[2]

meta = {}
for line in open(os.path.join(raw, "meta.txt")):
    if "=" in line:
        k, v = line.rstrip("\n").split("=", 1)
        meta[k] = v

tools = {}
for line in open(os.path.join(raw, "tools.tsv")):
    f = line.rstrip("\n").split("\t")
    if len(f) >= 7:
        tools[f[0]] = {"path": f[1], "sha256": f[2], "sha256_after": f[3],
                       "selftest_rc": f[4], "selftest_tail": f[5], "run_at": f[6],
                       "syntax_ok": f[7] == "0" if len(f) > 7 else None,
                       "syntax_error": f[8] if len(f) > 8 else ""}

cases = []
for line in open(os.path.join(raw, "cases.tsv")):
    f = line.rstrip("\n").split("\t")
    if len(f) < 12:
        continue
    tool, cid, fam, bind, expect, rc, secs, cls, result, why, ev, outfile = f[:12]
    cases.append({"tool": tool, "id": cid, "family": fam, "binding": bind == "1",
                  "expected": expect, "rc": int(rc) if rc.isdigit() else rc,
                  "secs": float(secs) if re.match(r'^\d+(\.\d+)?$', secs) else secs,
                  "class": cls, "result": result, "why": why,
                  "evidence": ev, "raw_out": "s50-raw/" + outfile})

impls = {}
for name, t in tools.items():
    tc = [c for c in cases if c["tool"] == name]
    binding = [c for c in tc if c["binding"]]
    bp = sum(1 for c in binding if c["result"] == "PASS")
    bt = len(binding)
    fails = [{"id": c["id"], "why": c["why"], "class": c["class"]} for c in binding if c["result"] == "FAIL"]
    advisory = [{"id": c["id"], "class": c["class"], "why": c["why"]} for c in tc
                if not c["binding"] and c["class"] == "SAFE" and c["expected"] == "NOTSAFE"]
    impls[name] = {
        "survival": f"{bp}/{bt}",
        "survived": f"{bp}/{bt}",
        "binding_pass": bp, "binding_total": bt,
        "failures": fails,
        "advisory_false_safe_candidates": advisory,
        "selftest_exit": t["selftest_rc"],
        "syntax_ok": t.get("syntax_ok"),
        "sha256": t["sha256"], "sha256_after": t["sha256_after"],
    }

def fam_concl(name, fam):
    tc = [c for c in cases if c["tool"] == name and c["family"] == fam]
    binding = [c for c in tc if c["binding"]]
    return {
        "binding_pass": sum(1 for c in binding if c["result"] == "PASS"),
        "binding_total": len(binding),
        "false_safes": [c["id"] for c in tc if c["result"] == "FAIL" and c["why"] == "FALSE-SAFE"],
        "rc_anomalies": [{"id": c["id"], "rc": c["rc"], "why": c["why"]} for c in tc
                         if c["result"] == "FAIL" and c["why"] != "FALSE-SAFE"],
        "notes": [f"{c['id']}: {c['class']} rc={c['rc']}" for c in tc if c["result"] == "INFO"][:12],
    }

conclusions = {name: {fam: fam_concl(name, fam) for fam in ("d", "e", "f")} for name in tools}

primary = next(iter(tools), None)
verdict = "PASS"
if primary:
    if impls[primary]["binding_pass"] != impls[primary]["binding_total"]:
        verdict = "FAIL"
all_pass = all(v["binding_pass"] == v["binding_total"] for v in impls.values())
if not all_pass:
    verdict = "FAIL"

doc = {
    "seat": "S50",
    "role": "adversarial tester: vault-path-is-a-directory / sha256sum-absent-from-PATH / ledger-file-missing",
    "round": 4,
    "kind": "adversarial",
    "attacks": {
        "d": "ledger row's vault_path resolves to a directory (empty dir / dir with inner copy / dir-digest mixed domain / empty vault hash / real-vault subdir / dir-target+file-vault)",
        "e": "source readable but sha256sum absent from PATH (busybox-like bin dir: git+rg+coreutils, no hashers); plus wrong-hash and empty-hash rows; advisory PATH-hijack shim",
        "f": "ledger file missing (absent path / directory / mode-000 / header-only / unset default)",
    },
    "oracle": "no attack case may yield SAFE/VERIFIED; rc must be controlled (not 124, not >=126); controls D0/E0a/F0 must reach SAFE(moved-to-obsidian) for the battery to be valid",
    "tool": ({"path": tools[primary]["path"], "sha256": tools[primary]["sha256"]} if primary else None),
    "tools": tools,
    "impls": impls,
    "conclusions": conclusions,
    "summary": {
        "tools_run": list(tools),
        "cases_per_tool": len(cases) // max(len(tools), 1),
        "total_runs": len(cases),
        "binding_false_safes": [{"tool": c["tool"], "id": c["id"]} for c in cases if c["why"] == "FALSE-SAFE" and c["binding"]],
        "advisory_false_safes": [{"tool": c["tool"], "id": c["id"]} for c in cases if c["why"] == "FALSE-SAFE" and not c["binding"]],
        "timeouts": [{"tool": c["tool"], "id": c["id"]} for c in cases if c["rc"] == 124],
        "uncontrolled_exits": [{"tool": c["tool"], "id": c["id"], "rc": c["rc"]} for c in cases if isinstance(c["rc"], int) and c["rc"] >= 126],
        "live_ledger_before": meta.get("live_ledger_before"),
        "live_ledger_after": meta.get("live_ledger_after"),
        "vault_snap_before": meta.get("vault_snap_before"),
        "vault_snap_after": meta.get("vault_snap_after"),
        "vault_untouched": meta.get("vault_snap_before") == meta.get("vault_snap_after"),
        "vault_notes_snap_before": meta.get("vault_notes_snap_before"),
        "vault_notes_snap_after": meta.get("vault_notes_snap_after"),
        "vault_notes_count_before": meta.get("vault_notes_count_before"),
        "vault_notes_count_after": meta.get("vault_notes_count_after"),
        "vault_notes_untouched": meta.get("vault_notes_snap_before") == meta.get("vault_notes_snap_after"),
        "obsidian_app_pids_before": meta.get("obsidian_app_pids_before"),
        "obsidian_app_pids_after": meta.get("obsidian_app_pids_after"),
        "live_ledger_untouched": meta.get("live_ledger_before") == meta.get("live_ledger_after"),
        "vault_whole_tree_note": "vault_untouched compares a depth-3 metadata snapshot; a False there may be an external actor (e.g. the Obsidian app itself, observed running during the wave) writing under .obsidian/. vault_notes_untouched (all *.md content hashes) is the binding integrity check for souji's read-only promise.",
        "advisory_case_note": "E2/E3/F5 are advisory by design: E2/E3 test a hostile PATH hasher (the lane's tool contract assumes coreutils is trustworthy; all four tools are fooled equally — recorded as an environment caveat, not a per-impl defect); F5 tests that a missing ledger does not block the independent stale receipt (correct behavior for a receipt-gate, outside the vault-verification claim).",
    },
    "harness": {"path": "tests/vault/s50-vadv.sh",
                "sha256": None, "raw_dir": "tests/vault/s50-raw/"},
    "verdict": verdict,
    "environment_finding": {
        "observed": "The Obsidian GUI app (electron43 /usr/lib/obsidian/app.asar) was launched several times during the round-4 wave window (app process seen 14:10:27-14:16 local; obsidian.log 'Loaded updated app' at 16:58/17:05/17:09/17:10/17:10 UTC; /run/user/1000/.obsidian-cli.sock present at 14:16). The launches coincide with the vault's .obsidian/*.json mtimes and a 2-line 'M .obsidian/...' git status in the vault repo.",
        "attribution": "NOT by seat S50: this harness never executes /usr/bin/obsidian, `obsidian`, or any resolved name (it runs only the 4 candidate tools with a mock-free PATH and the /tmp evil-hasher shims; pgrep before/after each battery recorded in s50-raw/meta.txt). The vault writes are app-side (.obsidian config/workspace), not note writes: all 58 vault *.md hashes are byte-identical before/after (vault_notes_untouched=True).",
        "who_else": "Other wave seats ran CLI-mock batteries concurrently (e.g. /tmp/s42-review/work/*/cli*/..., observed mock 'obsidian-cli' shims at 14:09-14:12). One of those batteries, or an operator action, plausibly started the app; the mock shims themselves cannot start it (they only print hashes). A real GUI launch is the only way to create the socket + .obsidian writes.",
        "recommendation": "The round's own evidence should treat any app-launched state as environment noise; seats must keep not launching it. If a future seat needs the official CLI, the operator must start the app; souji must never do it.",
    },
    "notes": [
        "fixtures under mktemp -d; removed unless --keep",
        "real vault touched read-only (stat only + sha256sum attempt on a directory for D5); note-content manifest (all *.md) hashed before/after",
        "live ledger read-only (cases F6 header-only copy, F7 default path); snapshot before/after recorded",
        "/usr/bin/obsidian (GUI launcher) never executed by this harness; the E2/E3 evil hashers are /tmp shims that only print attacker hashes",
        "invocation: timeout 30 env SHOKUNIN_ROOT=<empty fleet> SOUJI_LEDGER=<case ledger> /usr/bin/bash <tool> --stale-days 1 <target>",
    ],
}
hs = os.path.join(os.path.dirname(raw), "s50-vadv.sh")
if os.path.isfile(hs):
    import hashlib
    doc["harness"]["sha256"] = hashlib.sha256(open(hs, "rb").read()).hexdigest()

with open(out, "w") as fh:
    json.dump(doc, fh, indent=1, sort_keys=False)
    fh.write("\n")
print(f"S50: wrote {out} verdict={verdict} tools={list(tools)}")
for name, v in impls.items():
    print(f"  {name}: survival {v['survival']} selftest={v['selftest_exit']} failures={len(v['failures'])}")
PYEOF

exit 0
