#!/usr/bin/env bash
# souji-vault-verify — ledger-backed moved-to-obsidian verification with a
# read-only vault check (round 4, seat S18 / impl-18).
#
# A row in the Obsidian ledger is the receipt of record: it qualifies only
# when the source side AND the vault side both re-hash to the row's recorded
# sha256, byte-exact. The Obsidian CLI, when a shim literally named
# `obsidian-cli` is resolvable (or SOUJI_CLI_BIN / SOUJI_CLI is given), is
# *advisory* confirmation only — always bounded by `timeout`, consulted only
# when a ledger row is about to be confirmed, and never able to produce a
# VERIFIED verdict by itself. A CLI that lies, hangs, errors or is absent
# cannot flip the result; a vault file that changes while the CLI probes is
# re-hashed before the verdict stands. The desktop-app launcher name is never
# resolved or executed — only `obsidian-cli` from PATH.
#
# CLI
#   tools/souji-vault-verify.impl-18.sh [--selftest] [--json] [--vault PATH]
#        [--ledger PATH] [--stale-days N] [--fallback|--auto|--cli] [--] <path>...
#
# Output (default), two lines per target:
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence   (r2 form)
#   VERIFIED(receipt) | NOT-VERIFIED(reason)                      (r4 vocabulary)
# --json prints one JSON object per target and nothing else.
#
# Reasons (NOT-VERIFIED): source-absent, source-hash-mismatch, vault-absent,
# vault-hash-mismatch, source-equals-vault, row-incomplete, no-ledger,
# no-ledger-row, secrets-refusal, unreachable, none.
# Receipts (VERIFIED): moved-to-obsidian.
#
# Exit codes: 0 evaluated (NOT-SAFE is not an error), 1 selftest failure,
# 2 usage.
#
# Safety rails
#   * The vault is opened read-only: sha256sum/stat/readlink/find only.
#     Nothing is ever written under a vault path; the live ledger is never
#     written; the only writes anywhere are inside a `mktemp -d` selftest
#     scratch tree.
#   * Secret-shaped path components (*.env, .envrc, *credential*, *secret*,
#     id_*, *.pem) are refused before anything is read.
#   * No git fetch/push/commit/branch/checkout/reset/rebase is ever run;
#     .ufo/state, .ufo/watchdog.log and ~/.config are never touched.
#   * Path fields in TSV output escape tabs/newlines so one target always
#     produces exactly one record; --json escapes properly.
#
# Env overrides: SOUJI_LEDGER, SOUJI_VAULT (hint), SOUJI_CLI_BIN, SOUJI_CLI,
# SOUJI_CLI_TIMEOUT (default 6), SOUJI_SELFTEST_ACTIVE (recursion guard).
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
export LC_ALL=C

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

LEDGER="${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}"
VAULT_HINT="${SOUJI_VAULT:-}"
JSON=0
SELFTEST=0
CLI_MODE=auto              # auto | cli | fallback
STALE_DAYS=1
CLI_TIMEOUT="${SOUJI_CLI_TIMEOUT:-6}"
TARGETS=()

R_CLASS=NOT-SAFE
R_REASON=none
R_EVIDENCE="no-receipt"
R_RECEIPT=none
CLI_STATE=""
VR_CLI=""
VR_NOTE=""
VR_REASON=""
VR_EVIDENCE=""

usage() {
  cat <<'EOF'
souji-vault-verify — ledger-backed moved-to-obsidian verification (read-only vault check)

usage: souji-vault-verify.impl-18.sh [--selftest] [--json] [--vault PATH]
       [--ledger PATH] [--stale-days N] [--fallback|--auto|--cli] [--] <path>...

A ledger row qualifies only when the source side AND the vault side both
re-hash to the row's recorded sha256 (byte-exact). The Obsidian CLI, when a
shim named obsidian-cli is resolvable, is advisory confirmation only (bounded
by timeout) and can never produce VERIFIED alone. The vault is opened
read-only; nothing is ever written under a vault path.
EOF
  exit "${1:-0}"
}
usage_err() { printf 'souji-vault-verify: %s\n' "$1" >&2; usage 2; }

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

file_sha() {
  [ -f "$1" ] || return 1
  sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1
}

dir_digest() {
  [ -d "$1" ] || return 1
  ( cd "$1" 2>/dev/null && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

digest_for() { # $1 path (regular file or directory)
  if [ -d "$1" ]; then dir_digest "$1"; elif [ -f "$1" ]; then file_sha "$1"; else return 1; fi
}

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

san() { # single TSV/JSON-safe evidence token: no tabs, no newlines
  local s=${1:-}
  s=${s//$'\t'/ }
  s=${s//$'\n'/ }
  s=${s//$'\r'/ }
  printf '%s' "$s"
}

san_tsv() { # path field: escape control separators, keep one physical line
  local s=${1:-}
  s=${s//$'\t'/\\t}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  printf '%s' "$s"
}

jesc() {
  local s=${1:-}
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

# ---------------------------------------------------------------- CLI shim --
cli_resolve() {
  local cand
  if [ -n "${SOUJI_CLI_BIN:-}" ] && [ -x "${SOUJI_CLI_BIN}" ]; then
    printf '%s' "$SOUJI_CLI_BIN"; return 0
  fi
  if [ -n "${SOUJI_CLI:-}" ] && [ -x "${SOUJI_CLI}" ]; then
    printf '%s' "$SOUJI_CLI"; return 0
  fi
  cand=$(command -v obsidian-cli 2>/dev/null || true)
  case "$cand" in
    /*) if [ -x "$cand" ]; then printf '%s' "$cand"; return 0; fi ;;
  esac
  return 1
}

cli_label() {
  if cli_resolve >/dev/null 2>&1; then printf 'available'; else printf 'unavailable'; fi
}

CLI_CLAIM=""
CLI_STATE=""
cli_probe() { # $1 vault path; sets CLI_STATE and CLI_CLAIM
  local bin out rc
  CLI_CLAIM=""
  if [ "$CLI_MODE" = fallback ]; then CLI_STATE="skipped(fallback)"; return 0; fi
  if ! bin=$(cli_resolve); then CLI_STATE="unavailable"; return 0; fi
  set +e
  out=$(timeout "$CLI_TIMEOUT" "$bin" sha256 "$1" 2>/dev/null)
  rc=$?
  set -e
  case "$rc" in
    0)
      if [ -z "$out" ]; then
        CLI_STATE="empty"
      else
        CLI_CLAIM=$(printf '%s\n' "$out" | grep -oE '[0-9a-f]{64}' | head -n1 || true)
        if [ -n "$CLI_CLAIM" ]; then CLI_STATE="claimed"; else CLI_STATE="unparsed"; fi
      fi ;;
    124) CLI_STATE="timeout" ;;
    *)   CLI_STATE="error($rc)" ;;
  esac
  return 0
}

cli_executed() {
  case "$CLI_STATE" in
    claimed|timeout|empty|unparsed|error*) return 0 ;;
  esac
  return 1
}

# ------------------------------------------------------------- row verify --
# Verifies one ledger row against the current filesystem. Sets VR_REASON /
# VR_EVIDENCE / VR_CLI / VR_NOTE; returns 0 only when the row fully verifies.
row_verify() { # $1 target-canon $2 rsp $3 rss $4 rvp $5 rvs $6 nfields $7 rest
  local t=$1 rsp=$2 rss=$3 rvp=$4 rvs=$5 nf=$6 rest=$7
  local sp_c vp_c sp_real vp_real ssha vsha vsha2 claim rnote
  VR_REASON=""; VR_EVIDENCE=""; VR_CLI=""; VR_NOTE=""

  if [ "$nf" -lt 4 ]; then
    VR_REASON=row-incomplete
    VR_EVIDENCE="row-incomplete columns=$nf"
    return 1
  fi
  if is_secret_shaped "$rsp" || is_secret_shaped "$rvp"; then
    VR_REASON=secrets-refusal
    VR_EVIDENCE="row path secret-shaped refused"
    return 1
  fi

  # A row that points the artifact at itself is not an export: the file
  # would be its own only copy. Catch spelling, symlink and hardlink aliases
  # too, and refuse a vault copy nested inside the source directory (removing
  # the source would destroy the very copy the receipt cites).
  sp_c=$(canon_path "$rsp"); vp_c=$(canon_path "$rvp")
  sp_real=$(readlink -f -- "$rsp" 2>/dev/null || true)
  vp_real=$(readlink -f -- "$rvp" 2>/dev/null || true)
  if { [ -n "$sp_real" ] && [ "$sp_real" = "$vp_real" ]; } || [ "$sp_c" = "$vp_c" ]; then
    VR_REASON=source-equals-vault
    VR_EVIDENCE="source-equals-vault: the row points the artifact at itself vault=$rvp"
    return 1
  fi
  if [ -e "$rsp" ] && [ -e "$rvp" ]; then
    local si vi
    si=$(stat -c '%d:%i' -- "$rsp" 2>/dev/null || true)
    vi=$(stat -c '%d:%i' -- "$rvp" 2>/dev/null || true)
    if [ -n "$si" ] && [ "$si" = "$vi" ]; then
      VR_REASON=source-equals-vault
      VR_EVIDENCE="source-equals-vault: vault path is a hardlink of the source vault=$rvp"
      return 1
    fi
  fi
  case "$vp_c" in
    "$sp_c"/*)
      VR_REASON=vault-nested-in-source
      VR_EVIDENCE="vault-nested-in-source: vault copy lives inside the source path being evaluated vault=$rvp"
      return 1 ;;
  esac
  # SOUJI_VAULT is a hint by default (callers pass it even when rows point at
  # fixture vaults elsewhere). Only SOUJI_VAULT_STRICT=1 turns it into a
  # constraint on where a qualifying vault copy may live.
  if [ "${SOUJI_VAULT_STRICT:-0}" = 1 ] && [ -n "$VAULT_HINT" ]; then
    local vr_root
    vr_root=$(canon_path "$VAULT_HINT")
    case "$vp_c" in
      "$vr_root"|"$vr_root"/*) : ;;
      *)
        VR_REASON=vault-outside-root
        VR_EVIDENCE="vault-outside-root: vault=$rvp not under vault root $vr_root"
        return 1 ;;
    esac
  fi

  # Source side
  if [ ! -e "$rsp" ] && [ ! -L "$rsp" ]; then
    VR_REASON=source-absent
    VR_EVIDENCE="source-absent source=$rsp vault=$rvp"
    return 1
  fi
  if [ ! -f "$rsp" ] && [ ! -d "$rsp" ]; then
    VR_REASON=source-absent
    VR_EVIDENCE="source-absent source=$rsp not a regular file"
    return 1
  fi
  ssha=$(digest_for "$rsp" 2>/dev/null || true)
  if [ -z "$ssha" ]; then
    VR_REASON=source-absent
    VR_EVIDENCE="source-absent source=$rsp unreadable"
    return 1
  fi
  if [ "$ssha" != "$rss" ]; then
    VR_REASON=source-hash-mismatch
    VR_EVIDENCE="obsidian=source-sha-mismatch source-hash-mismatch live=${ssha:0:12} row=${rss:0:12} source=$rsp"
    return 1
  fi

  # Vault side (read-only)
  if [ ! -e "$rvp" ] && [ ! -L "$rvp" ]; then
    VR_REASON=vault-absent
    VR_EVIDENCE="obsidian=vault-unreachable vault-absent vault=$rvp"
    return 1
  fi
  if [ ! -f "$rvp" ] && [ ! -d "$rvp" ]; then
    VR_REASON=vault-absent
    VR_EVIDENCE="obsidian=vault-unreachable vault-absent vault=$rvp not a regular file"
    return 1
  fi
  vsha=$(digest_for "$rvp" 2>/dev/null || true)
  if [ -z "$vsha" ]; then
    VR_REASON=vault-absent
    VR_EVIDENCE="obsidian=vault-unreachable vault-absent vault=$rvp unreadable"
    return 1
  fi
  if [ "$vsha" != "$rvs" ]; then
    VR_REASON=vault-hash-mismatch
    VR_EVIDENCE="obsidian=vault-sha-mismatch vault-hash-mismatch live=${vsha:0:12} row=${rvs:0:12} vault=$rvp"
    return 1
  fi

  # Advisory CLI confirmation, bounded. It never decides the verdict; when it
  # ran, the vault side is re-hashed afterwards so a file that changed during
  # the probe cannot ride an earlier match to VERIFIED.
  if [ "$CLI_MODE" != fallback ]; then
    cli_probe "$rvp"
    case "$CLI_STATE" in
      claimed)
        if [ "$CLI_CLAIM" = "$vsha" ]; then
          VR_CLI=" cli=agree"
        else
          VR_CLI=" cli=disagreement(claimed=${CLI_CLAIM:0:12})"
        fi ;;
      *) VR_CLI=" cli=$CLI_STATE" ;;
    esac
    if cli_executed; then
      vsha2=$(digest_for "$rvp" 2>/dev/null || true)
      if [ "$vsha2" != "$rvs" ]; then
        VR_REASON=vault-hash-mismatch
        VR_EVIDENCE="obsidian=vault-sha-mismatch vault-hash-mismatch vault-changed-during-cli-probe vault=$rvp"
        return 1
      fi
    fi
  fi

  rnote=$(printf '%s' "$rest" | cut -f2)
  if [ -n "$rnote" ]; then VR_NOTE=" note=$(san "$rnote")"; fi
  return 0
}

# ---------------------------------------------------------- target verify --
evaluate_target() { # $1 raw target
  local target=$1 tcanon line first=1 nfields=0 rows=0 got_fail=0
  local fr_reason="" fr_ev="" rsp rss rvp rvs rest
  R_CLASS=NOT-SAFE; R_REASON=none; R_EVIDENCE="no-receipt"; R_RECEIPT=none
  CLI_STATE=""

  if [ -z "$target" ]; then
    R_REASON=unreachable; R_EVIDENCE="empty target"
    return 0
  fi
  if is_secret_shaped "$target"; then
    R_REASON=secrets-refusal
    R_EVIDENCE="secret-shaped path refused basename=$(basename -- "$target")"
    return 0
  fi
  tcanon=$(canon_path "$target")

  if [ ! -f "$LEDGER" ] || [ ! -r "$LEDGER" ]; then
    R_REASON=no-ledger
    R_EVIDENCE="obsidian=no-ledger path=$LEDGER"
    if [ "$CLI_MODE" = cli ]; then R_EVIDENCE="$R_EVIDENCE cli=$(cli_label)"; fi
    return 0
  fi
  # A receipt must trace to a concrete ledger file. A symlinked ledger can be
  # re-pointed mid-run (swap races) and a chain or escaping link hides which
  # file actually produced the row, so refuse rather than follow.
  if [ -L "$LEDGER" ]; then
    R_REASON=ledger-symlink
    R_EVIDENCE="obsidian=ledger-symlink refused path=$LEDGER resolves=$(readlink -f -- "$LEDGER" 2>/dev/null || true)"
    return 0
  fi

  while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    [ -n "$line" ] || continue
    case "$line" in \#*) continue ;; esac
    if [ "$first" = 1 ]; then
      first=0
      case "$line" in source_path$'\t'*) continue ;; esac
    fi
    rows=$((rows+1))
    nfields=$(( $(printf '%s' "$line" | tr -cd '\t' | wc -c) + 1 ))
    IFS=$'\t' read -r rsp rss rvp rvs rest <<< "$line"
    [ "$rsp" = "$tcanon" ] || continue
    if row_verify "$tcanon" "$rsp" "$rss" "$rvp" "$rvs" "$nfields" "$rest"; then
      R_CLASS=SAFE; R_REASON=moved-to-obsidian; R_RECEIPT=moved-to-obsidian
      R_EVIDENCE="ledger-row ledger=$(canon_path "$LEDGER") vault=$rvp source-sha256=${rss:0:12} vault-sha256=${rvs:0:12}${VR_CLI}${VR_NOTE}"
      return 0
    fi
    if [ "$got_fail" = 0 ]; then
      got_fail=1; fr_reason=$VR_REASON; fr_ev=$VR_EVIDENCE
    fi
  done < "$LEDGER"

  if [ "$got_fail" = 1 ]; then
    R_REASON=$fr_reason; R_EVIDENCE=$fr_ev
    if [ "$CLI_MODE" = cli ]; then R_EVIDENCE="$R_EVIDENCE cli=$(cli_label)"; fi
    return 0
  fi
  if [ ! -e "$tcanon" ] && [ ! -L "$tcanon" ]; then
    R_REASON=unreachable; R_EVIDENCE="missing path"
  else
    R_REASON=no-ledger-row
    R_EVIDENCE="obsidian=no-matching-ledger-row ledger=$LEDGER rows=$rows"
  fi
  if [ "$CLI_MODE" = cli ]; then R_EVIDENCE="$R_EVIDENCE cli=$(cli_label)"; fi
  return 0
}

emit_target() { # $1 path as given
  local token receipt
  if [ "$R_CLASS" = SAFE ]; then
    token="VERIFIED($R_RECEIPT)"; receipt=$R_RECEIPT
  else
    token="NOT-VERIFIED($R_REASON)"; receipt=none
  fi
  if [ "$JSON" = 1 ]; then
    printf '{"path":"%s","verdict":"%s","verified":"%s","receipt":"%s","reason":"%s","evidence":"%s"}\n' \
      "$(jesc "$1")" "$R_CLASS" "$(jesc "$token")" "$(jesc "$receipt")" \
      "$(jesc "$R_REASON")" "$(jesc "$R_EVIDENCE")"
  else
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' \
      "$(san_tsv "$1")" "$R_CLASS" "$(san_tsv "$receipt")" "$(san_tsv "$R_EVIDENCE")"
    printf '%s\n' "$token"
  fi
}

# --------------------------------------------------------------- selftest --
ST_TMP=""
ST_N=0
ST_FAIL=0

vrun() { # ENV=V ... -- args...
  local -a envs=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  if [ "$#" -gt 0 ]; then shift; fi
  env SOUJI_SELFTEST_ACTIVE=1 "${envs[@]}" timeout 30 bash "$SELF" "$@"
}

st_case() { # $1 id, $2 want token, $3 evidence regex (may be ""), rest = cmd
  local id=$1 want=$2 evre=$3; shift 3
  local out line rc
  set +e
  out=$("$@" 2>/dev/null); rc=$?
  set -e
  ST_N=$((ST_N+1))
  line=$(printf '%s\n' "$out" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -n1 || true)
  if [ "$line" = "$want" ] && { [ -z "$evre" ] || printf '%s\n' "$out" | grep -aqE "$evre"; }; then
    printf 'PASS %s %s\n' "$id" "$line"
  else
    ST_FAIL=$((ST_FAIL+1))
    printf 'FAIL %s want=%s got=%s\n' "$id" "$want" "${line:-<no-line> rc=$rc}"
  fi
}

st_line_count() { # $1 id, $2 want-lines, rest = cmd
  local id=$1 want=$2; shift 2
  local out n
  set +e; out=$("$@" 2>/dev/null); set -e
  ST_N=$((ST_N+1))
  n=$(printf '%s\n' "$out" | wc -l)
  if [ "$n" = "$want" ]; then printf 'PASS %s lines=%s\n' "$id" "$n"
  else ST_FAIL=$((ST_FAIL+1)); printf 'FAIL %s want-lines=%s got=%s\n' "$id" "$want" "$n"; fi
}

run_selftest() {
  ST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/souji-vault-selftest.XXXXXX")
  trap 'rm -rf -- "$ST_TMP"' EXIT
  local W="$ST_TMP/world"
  mkdir -p "$W/vault/sub dir" "$W/src/dir-case" "$W/vault/dir-case" "$W/ledgers"

  printf 'alpha content\n'            > "$W/vault/note.md"
  printf 'tampered content\n'         > "$W/vault/tampered.md"
  printf 'spacey content\n'           > "$W/vault/sub dir/note two.md"
  printf 'alpha content\n'            > "$W/src/source-a.txt"
  printf 'different source\n'         > "$W/src/source-b.txt"
  printf 'spacey content\n'           > "$W/src/source with space.txt"
  printf 'SECRET=canary-18\n'         > "$W/src/dummy.env"
  printf 'one\n'                      > "$W/src/dir-case/one.txt"
  cp "$W/src/dir-case/one.txt" "$W/vault/dir-case/one.txt"
  ln -sf "$W/src/source-a.txt" "$W/src/alias-link.md"
  mkfifo "$W/vault/fifo.md" 2>/dev/null || true

  local sa sb sp vsp vtamp dd dvd upper
  sa=$(file_sha "$W/src/source-a.txt")
  sb=$(file_sha "$W/src/source-b.txt")
  sp=$(file_sha "$W/src/source with space.txt")
  vsp=$(file_sha "$W/vault/sub dir/note two.md")
  vtamp=$(file_sha "$W/vault/tampered.md")
  dd=$(dir_digest "$W/src/dir-case")
  dvd=$(dir_digest "$W/vault/dir-case")
  upper=$(printf '%s' "$sa" | tr 'a-f' 'A-F')

  local HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
  row() { printf '%s\t%s\t%s\t%s\t2026-10-18\t%s\n' "$1" "$2" "$3" "$4" "$5"; }
  mkled() { local f=$1; shift; { printf '%s\n' "$HDR"; local r; for r in "$@"; do printf '%s\n' "$r"; done; } > "$f"; }

  local L1="$W/ledgers/L1.tsv"   L2="$W/ledgers/L2.tsv"   L3="$W/ledgers/L3.tsv"
  local L4="$W/ledgers/L4.tsv"   L5="$W/ledgers/L5.tsv"   L6="$W/ledgers/L6.tsv"
  local L7="$W/ledgers/L7.tsv"   L8="$W/ledgers/L8.tsv"   L9="$W/ledgers/L9.tsv"
  local L10="$W/ledgers/L10.tsv" L11="$W/ledgers/L11.tsv" L12="$W/ledgers/L12.tsv"
  local L13="$W/ledgers/L13.tsv" L14="$W/ledgers/L14.tsv" L15="$W/ledgers/L15.tsv"
  local L16="$W/ledgers/L16.tsv" L25="$W/ledgers/L25.tsv" L23="$W/ledgers/L23.tsv"

  mkled "$L1"  "$(row "$W/src/source-a.txt" "$sa" "$W/vault/note.md" "$sa" "case-match")"
  mkled "$L2"  "$(row "$W/src/source-a.txt" "$sa" "$W/vault/tampered.md" "$sa" "case-vault-tamper")"
  mkled "$L3"  "$(row "$W/src/source-a.txt" "$sb" "$W/vault/note.md" "$sa" "case-source-tamper")"
  mkled "$L4"  "$(row "$W/src/source-a.txt" "$sa" "$W/vault/absent.md" "$sa" "case-vault-absent")"
  mkled "$L5"  "$(row "$W/src/gone.txt" "$sb" "$W/vault/note.md" "$sa" "case-source-absent")"
  { printf '%s\r\n' "$HDR"; row "$W/src/source-a.txt" "$sa" "$W/vault/note.md" "$sa" "case-crlf" | sed 's/$/\r/'; } > "$L6"
  printf '%s\n%s\t%s\t%s\t%s\t2026-10-18\t%s\textra1\t\n' "$HDR" \
    "$W/src/source-a.txt" "$sa" "$W/vault/note.md" "$sa" "case-extra-cols" > "$L7"
  mkled "$L8"  "$(row "$W/src/source-a.txt" "$sa" "$W/vault/note.md" "$sa" "dup-match")" \
               "$(row "$W/src/source-a.txt" "$sb" "$W/vault/tampered.md" "$vtamp" "dup-mismatch")"
  { printf '%s\n' "$HDR"; printf '# a comment row\n'; row "$W/src/source-a.txt" "$sa" "$W/vault/note.md" "$sa" "case-comment"; } > "$L9"
  mkled "$L10" "$(row "$W/src/source-a.txt" "$upper" "$W/vault/note.md" "$sa" "case-upper")"
  mkled "$L11" "$(row "$W/src/dummy.env" "$(file_sha "$W/src/dummy.env")" "$W/vault/note.md" "$sa" "case-secret")"
  mkled "$L12" "$(row "$W/src/source-a.txt" "$sa" "$W/src/source-a.txt" "$sa" "case-self-move")"
  mkled "$L13" "$(row "$W/src/source-a.txt" "$sa" "$W/src/alias-link.md" "$sa" "case-symlink-alias")"
  mkled "$L14" "$(row "$W/src/source-a.txt" "$sa" "$W/vault/fifo.md" "$sa" "case-fifo")"
  mkled "$L15" "$(row "$W/src/source with space.txt" "$sp" "$W/vault/sub dir/note two.md" "$vsp" "case-spaces")"
  printf '%s\n' "$HDR" > "$L16"
  mkled "$L25" "$(row "$W/src/dir-case" "$dd" "$W/vault/dir-case" "$dvd" "case-dir")"
  printf 'alpha content\n' > "$W/vault/mutate-target.md"
  mkled "$L23" "$(row "$W/src/source-a.txt" "$sa" "$W/vault/mutate-target.md" "$sa" "case-mutate")"

  local MOCK="$ST_TMP/mock-cli"
  cat > "$MOCK" <<'EOS'
#!/usr/bin/env bash
mode=${MOCK18_MODE:-honest}
f=${MOCK18_FILE:-}
h=$(sha256sum -- "$f" 2>/dev/null | cut -d' ' -f1)
case "$mode" in
  honest) printf '{"ok":true,"sha256":"%s"}\n' "$h" ;;
  liar)   printf '{"ok":true,"sha256":"%s"}\n' "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" ;;
  hang)   sleep 60 ;;
  mutate) printf '{"ok":true,"sha256":"%s"}\n' "$h"; printf 'MUTATED' >> "$f" ;;
  *)      printf '{"ok":true,"sha256":"%s"}\n' "$h" ;;
esac
EOS
  chmod +x "$MOCK"

  local T1="$W/src/source-a.txt"

  printf '== souji-vault-verify impl-18 selftest ==\n'
  st_case V1  "VERIFIED(moved-to-obsidian)"      'ledger-row ledger=' \
    vrun SOUJI_LEDGER="$L1" -- --fallback -- "$T1"
  st_case V2  "NOT-VERIFIED(vault-hash-mismatch)" 'vault-sha-mismatch' \
    vrun SOUJI_LEDGER="$L2" -- --fallback -- "$T1"
  st_case V3  "NOT-VERIFIED(source-hash-mismatch)" 'source-sha-mismatch' \
    vrun SOUJI_LEDGER="$L3" -- --fallback -- "$T1"
  st_case V4  "NOT-VERIFIED(vault-absent)"       'vault-unreachable' \
    vrun SOUJI_LEDGER="$L4" -- --fallback -- "$T1"
  st_case V5  "NOT-VERIFIED(source-absent)"      'source-absent' \
    vrun SOUJI_LEDGER="$L5" -- --fallback -- "$W/src/gone.txt"
  st_case V6  "VERIFIED(moved-to-obsidian)"      '' \
    vrun SOUJI_LEDGER="$L6" -- --fallback -- "$T1"
  st_case V7  "VERIFIED(moved-to-obsidian)"      'note=case-extra-cols' \
    vrun SOUJI_LEDGER="$L7" -- --fallback -- "$T1"
  st_case V8  "VERIFIED(moved-to-obsidian)"      '' \
    vrun SOUJI_LEDGER="$L8" -- --fallback -- "$T1"
  st_case V9  "VERIFIED(moved-to-obsidian)"      '' \
    vrun SOUJI_LEDGER="$L9" -- --fallback -- "$T1"
  st_case V10 "NOT-VERIFIED(source-hash-mismatch)" '' \
    vrun SOUJI_LEDGER="$L10" -- --fallback -- "$T1"
  st_case V11 "NOT-VERIFIED(secrets-refusal)"    '' \
    vrun SOUJI_LEDGER="$L11" -- --fallback -- "$W/src/dummy.env"
  st_case V12 "NOT-VERIFIED(source-equals-vault)" '' \
    vrun SOUJI_LEDGER="$L12" -- --fallback -- "$T1"
  st_case V13 "NOT-VERIFIED(source-equals-vault)" '' \
    vrun SOUJI_LEDGER="$L13" -- --fallback -- "$T1"
  st_case V14 "NOT-VERIFIED(vault-absent)"       '' \
    vrun SOUJI_LEDGER="$L14" -- --fallback -- "$T1"
  st_case V15 "VERIFIED(moved-to-obsidian)"      '' \
    vrun SOUJI_LEDGER="$L15" -- --fallback -- "$W/src/source with space.txt"
  st_case V16 "NOT-VERIFIED(no-ledger-row)"      '' \
    vrun SOUJI_LEDGER="$L1" -- --fallback -- "$W/src/source-b.txt"
  st_case V17 "NOT-VERIFIED(no-ledger-row)"      '' \
    vrun SOUJI_LEDGER="$L16" -- --fallback -- "$T1"
  st_case V18 "NOT-VERIFIED(no-ledger)"          '' \
    vrun SOUJI_LEDGER="$W/ledgers/absent.tsv" -- --fallback -- "$T1"
  st_case V19 "NOT-VERIFIED(unreachable)"        '' \
    vrun SOUJI_LEDGER="$L1" -- --fallback -- ""
  st_case V20 "VERIFIED(moved-to-obsidian)"      'cli=agree' \
    vrun SOUJI_LEDGER="$L1" SOUJI_CLI_BIN="$MOCK" MOCK18_MODE=honest MOCK18_FILE="$W/vault/note.md" -- --cli -- "$T1"
  st_case V21 "VERIFIED(moved-to-obsidian)"      'cli=disagreement' \
    vrun SOUJI_LEDGER="$L1" SOUJI_CLI_BIN="$MOCK" MOCK18_MODE=liar MOCK18_FILE="$W/vault/note.md" -- --cli -- "$T1"
  st_case V22 "VERIFIED(moved-to-obsidian)"      'cli=timeout' \
    vrun SOUJI_LEDGER="$L1" SOUJI_CLI_BIN="$MOCK" MOCK18_MODE=hang SOUJI_CLI_TIMEOUT=2 -- --cli -- "$T1"
  st_case V23 "NOT-VERIFIED(vault-hash-mismatch)" 'vault-changed-during-cli-probe' \
    vrun SOUJI_LEDGER="$L23" SOUJI_CLI_BIN="$MOCK" MOCK18_MODE=mutate MOCK18_FILE="$W/vault/mutate-target.md" -- --cli -- "$T1"
  st_case V25 "VERIFIED(moved-to-obsidian)"      '' \
    vrun SOUJI_LEDGER="$L25" -- --fallback -- "$W/src/dir-case"
  st_case V26 "NOT-VERIFIED(no-ledger-row)"      'cli=unavailable' \
    vrun SOUJI_LEDGER="$L16" -- --cli -- "$T1"

  # V30: hardlink alias (source and vault share the inode)
  ln "$W/src/source-a.txt" "$W/src/alias-hard.md" 2>/dev/null || cp "$W/src/source-a.txt" "$W/src/alias-hard.md"
  local L30="$W/ledgers/L30.tsv"
  mkled "$L30" "$(row "$W/src/source-a.txt" "$sa" "$W/src/alias-hard.md" "$sa" "case-hardlink")"
  if [ "$(stat -c '%d:%i' "$W/src/source-a.txt")" = "$(stat -c '%d:%i' "$W/src/alias-hard.md")" ]; then
    st_case V30 "NOT-VERIFIED(source-equals-vault)" '' \
      vrun SOUJI_LEDGER="$L30" -- --fallback -- "$T1"
  else
    ST_N=$((ST_N+1)); printf 'PASS V30 hardlink-unsupported-on-fs (skipped)\n'
  fi

  # V31: vault copy nested inside the source directory being evaluated
  mkdir -p "$W/src/repo/inner"
  printf 'nested payload\n' > "$W/src/repo/inner/copy.md"
  local nd ndi L31="$W/ledgers/L31.tsv"
  nd=$(dir_digest "$W/src/repo"); ndi=$(dir_digest "$W/src/repo/inner")
  mkled "$L31" "$(row "$W/src/repo" "$nd" "$W/src/repo/inner" "$ndi" "case-nested")"
  st_case V31 "NOT-VERIFIED(vault-nested-in-source)" '' \
    vrun SOUJI_LEDGER="$L31" -- --fallback -- "$W/src/repo"

  # V32: strict vault-root constraint (SOUJI_VAULT + SOUJI_VAULT_STRICT=1)
  st_case V32 "NOT-VERIFIED(vault-outside-root)" '' \
    vrun SOUJI_LEDGER="$L1" SOUJI_VAULT="$W/other-vault" SOUJI_VAULT_STRICT=1 -- --fallback -- "$T1"

  # V33: receipt evidence names the ledger file it came from
  st_case V33 "VERIFIED(moved-to-obsidian)"      "ledger=$L1" \
    vrun SOUJI_LEDGER="$L1" -- --fallback -- "$T1"

  # V34: a symlinked ledger is refused (receipts must trace to a real file)
  ln -sf "$L1" "$W/ledgers/L34-link.tsv"
  st_case V34 "NOT-VERIFIED(ledger-symlink)" '' \
    vrun SOUJI_LEDGER="$W/ledgers/L34-link.tsv" -- --fallback -- "$T1"

  # V24: --json is one parseable JSON object carrying the exact path
  ST_N=$((ST_N+1))
  local jout
  jout=$(env SOUJI_SELFTEST_ACTIVE=1 SOUJI_LEDGER="$L1" timeout 30 bash "$SELF" --json --fallback -- "$T1" 2>/dev/null || true)
  if printf '%s' "$jout" | grep -q '^{.*}$' && printf '%s' "$jout" | grep -qF "\"path\":\"$T1\""; then
    printf 'PASS V24 json-shape\n'
  else
    ST_FAIL=$((ST_FAIL+1)); printf 'FAIL V24 json-shape got=%s\n' "$(printf '%s' "$jout" | head -c 160)"
  fi

  # V27: determinism
  local o1 o2
  o1=$(env SOUJI_SELFTEST_ACTIVE=1 SOUJI_LEDGER="$L1" timeout 30 bash "$SELF" --fallback -- "$T1" 2>/dev/null || true)
  o2=$(env SOUJI_SELFTEST_ACTIVE=1 SOUJI_LEDGER="$L1" timeout 30 bash "$SELF" --fallback -- "$T1" 2>/dev/null || true)
  ST_N=$((ST_N+1))
  if [ "$o1" = "$o2" ]; then printf 'PASS V27 determinism\n'
  else ST_FAIL=$((ST_FAIL+1)); printf 'FAIL V27 determinism\n'; fi

  # V28: a newline-bearing path stays one record (escaped, not split)
  local nlf="$W/src/first
second.md"
  printf 'x\n' > "$nlf"
  st_line_count V28 2 \
    vrun SOUJI_LEDGER="$L1" -- --fallback -- "$nlf"

  # V29: bounded CLI wall time (hang mode must return well before the outer bound)
  ST_N=$((ST_N+1))
  local t0 t1
  t0=$(date +%s)
  env SOUJI_SELFTEST_ACTIVE=1 SOUJI_LEDGER="$L1" SOUJI_CLI_BIN="$MOCK" MOCK18_MODE=hang \
    SOUJI_CLI_TIMEOUT=2 timeout 30 bash "$SELF" --cli -- "$T1" >/dev/null 2>&1 || true
  t1=$(date +%s)
  if [ $((t1 - t0)) -lt 20 ]; then printf 'PASS V29 cli-hang-bounded %ss\n' "$((t1 - t0))"
  else ST_FAIL=$((ST_FAIL+1)); printf 'FAIL V29 cli-hang-bounded %ss\n' "$((t1 - t0))"; fi

  printf 'selftest: %s checks, %s failed\n' "$ST_N" "$ST_FAIL"
  [ "$ST_FAIL" -eq 0 ] || return 1
  return 0
}

# -------------------------------------------------------------------- main --
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --ledger) [ $# -ge 2 ] || usage_err "--ledger needs a value"; LEDGER=$2; shift 2 ;;
    --ledger=*) LEDGER=${1#*=}; shift ;;
    --vault) [ $# -ge 2 ] || usage_err "--vault needs a value"; VAULT_HINT=$2; shift 2 ;;
    --vault=*) VAULT_HINT=${1#*=}; shift ;;
    --stale-days) [ $# -ge 2 ] || usage_err "--stale-days needs a value"; STALE_DAYS=$2; shift 2 ;;
    --stale-days=*) STALE_DAYS=${1#*=}; shift ;;
    --fallback) CLI_MODE=fallback; shift ;;
    --auto) CLI_MODE=auto; shift ;;
    --cli) CLI_MODE=cli; shift ;;
    -h|--help) usage 0 ;;
    --) shift; while [ $# -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    --*) usage_err "unknown flag: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

if [ "$SELFTEST" = 1 ]; then
  if [ "${SOUJI_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'souji-vault-verify: refusing nested --selftest\n' >&2
    exit 1
  fi
  run_selftest
  exit $?
fi

if [ "${#TARGETS[@]}" -eq 0 ]; then
  usage_err "no target given"
fi

for t in "${TARGETS[@]}"; do
  evaluate_target "$t"
  emit_target "$t"
done
exit 0
