#!/usr/bin/env bash
# souji-vault-verify.impl-24.sh — round-4 candidate (seat S24, independent).
#
# Ledger-backed `moved-to-obsidian` verification for souji-shokunin round 4
# (Obsidian-CLI vault verification). One bash tool; bash + coreutils + git +
# rg only. Read-only over every surface it inspects: the source copy, the
# ledger, and the vault side (the real vault /home/vgpnk/Documents/
# shokoknowledge is only ever read).
#
# Contract (as consumed by tests/vault/runner-*.sh):
#   tools/souji-vault-verify.impl-24.sh [--selftest] [--ledger PATH]
#        [--fallback] [--cli] [--json] [--vault ROOT] [--stale-days N] <target>...
#
# Output (default), two lines per target:
#   line 1 (r4 vocabulary):
#     VERIFIED(moved-to-obsidian)
#     NOT-VERIFIED(<reason>)
#   line 2 (r2 compatibility shape, field 2 = target path):
#     VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt-or-none<TAB>evidence
# --json prints one JSON object per target and nothing else.
#
# reasons (NOT-VERIFIED): source-absent, vault-absent, source-hash-mismatch,
#   vault-hash-mismatch, row-incomplete, self-receipt, no-ledger-row,
#   no-ledger, secrets-refusal, unreachable.
# Evidence keeps the r2 note spellings (obsidian=source-sha-mismatch,
# obsidian=vault-sha-mismatch, obsidian=vault-unreachable) so both fixture
# generations can match their declared tokens.
#
# Exit codes: 0 = evaluated (verdicts are not errors); 1 = selftest failure;
#             2 = usage. No other codes.
#
# The ledger is the receipt of record: a row must match source path AND
# source sha256 AND vault path AND vault sha256 (all four conjuncts, all
# non-empty), and the vault side is re-hashed live at verification time. A
# row missing any of the four conjuncts is NOT a receipt (row-incomplete).
# The official Obsidian CLI is NOT an entry point on this host (host probe
# 2026-10-18: no shim at ~/.local/bin/obsidian, no obsidian-cli binary
# beside the electron runtime, socket $XDG_RUNTIME_DIR/.obsidian-cli.sock
# absent, app not running), so the sha256sum fallback is the operational
# path. `--cli` asks for CLI-assisted verification: the tool probes the CLI
# entry point read-only, reports its state, and NEVER executes a resolved
# `obsidian` name (that is the GUI launcher on this host; starting the app
# is forbidden). A CLI that cannot be consulted degrades the note, never
# mints a VERIFIED.
#
# Safety rails:
#   * Never execute the desktop GUI launcher or any resolved `obsidian` name;
#     the launcher's absolute path is deliberately not named in this file.
#   * Secret-shaped path components (*.env, .env, .env.*, .envrc,
#     *credential*, *secret*, id_*, *.pem) are refused before any read:
#     NOT-VERIFIED(secrets-refusal).
#   * Never hash non-regular files (FIFO/socket/device): the vault side is
#     `stat`-checked first; non-regular -> NOT-VERIFIED(vault-absent).
#   * No git fetch/push/commit/branch/checkout/reset/rebase; no writes
#     outside `mktemp -d` scratch; .ufo/state, .ufo/watchdog.log and
#     ~/.config are never touched.
#
# Env overrides:
#   SOUJI_LEDGER   ledger path (default: <repo>/corpus/knowledge/obsidian-ledger.tsv)
#   SOUJI_CLI      explicit CLI entry point to probe with --cli (optional)
#   SOUJI_VAULT    default vault root hint (informational)
set -euo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true
export LC_ALL=C

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
LEDGER="${SOUJI_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}"
VAULT_ROOT="${SOUJI_VAULT:-/home/vgpnk/Documents/shokoknowledge}"
CLI_HINT="${SOUJI_CLI:-}"
STALE_DAYS=1

SELFTEST=0
JSON=0
WANT_CLI=0
FORCE_FALLBACK=0
TARGETS=()

usage() { # $1 = exit code
  sed -n '2,42p' "$SCRIPT_PATH" | sed 's/^# \{0,1\}//'
  exit "$1"
}
usage_err() { printf 'souji-vault-verify: %s\n' "$1" >&2; usage 2; }

json_escape() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

canon_path() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

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

file_sha() { # sha256 of a regular file only; fails on anything else
  local p=$1
  [ -f "$p" ] || return 1
  case "$(stat -c %F -- "$p" 2>/dev/null)" in
    "regular file"|"regular empty file") ;;
    *) return 1 ;;
  esac
  sha256sum -- "$p" 2>/dev/null | cut -d' ' -f1
}

dir_digest() { # deterministic manifest digest of a directory (ignores .git)
  local d=$1
  ( cd "$d" 2>/dev/null && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

# ---------------------------------------------------------------------------
# CLI entry-point probe (read-only; NEVER executes an `obsidian` name)
# ---------------------------------------------------------------------------
CLI_STATE="unavailable"
CLI_DETAIL=""

cli_probe() {
  local cand s
  if [ -n "$CLI_HINT" ]; then
    if [ -x "$CLI_HINT" ]; then
      case "$(basename -- "$CLI_HINT" 2>/dev/null || printf '%s' "$CLI_HINT")" in
        obsidian) CLI_STATE="gui-launcher-only"; CLI_DETAIL="hint=$CLI_HINT is the GUI launcher; not executed"; return 0 ;;
        *) CLI_STATE="present"; CLI_DETAIL="hint=$CLI_HINT"; return 0 ;;
      esac
    fi
    CLI_STATE="hint-missing"; CLI_DETAIL="hint=$CLI_HINT not executable"
    return 0
  fi
  local sock="${XDG_RUNTIME_DIR:-$HOME}/.obsidian-cli.sock"
  if [ -S "$sock" ]; then
    CLI_STATE="socket-live"; CLI_DETAIL="socket=$sock (app running; official CLI protocol reachable)"
    return 0
  fi
  for cand in "$HOME/.local/bin/obsidian" /usr/local/bin/obsidian; do
    if [ -e "$cand" ]; then
      s=$(basename -- "$(readlink -f -- "$cand" 2>/dev/null || printf '%s' "$cand")" 2>/dev/null || printf '%s' "$cand")
      case "$s" in
        obsidian-cli*) CLI_STATE="shim-present"; CLI_DETAIL="shim=$cand -> $s (not executed)"; return 0 ;;
        *) CLI_STATE="shim-ambiguous"; CLI_DETAIL="shim=$cand -> $s (not executed; may be the GUI launcher)"; return 0 ;;
      esac
    fi
  done
  for cand in /usr/lib/electron43/obsidian-cli /usr/lib/obsidian/obsidian-cli "$HOME/.local/bin/obsidian-cli"; do
    if [ -x "$cand" ]; then
      CLI_STATE="bundled-present"; CLI_DETAIL="binary=$cand (not executed)"
      return 0
    fi
  done
  CLI_STATE="unavailable"
  CLI_DETAIL="no shim (~/.local/bin/obsidian), no bundled obsidian-cli, socket ${XDG_RUNTIME_DIR:-$HOME}/.obsidian-cli.sock absent"
  return 0
}

# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------
LEDGER_ROWS=()
IDX_SP=0; IDX_SS=1; IDX_VP=2; IDX_VS=3

ledger_load() {
  local line first=1
  LEDGER_ROWS=()
  [ -f "$LEDGER" ] || return 1
  # The trailing CR of a CRLF row is deliberately NOT stripped: it rides on
  # the row's LAST field, exactly as the r2 tool's `read` sees it. On a
  # canonical 6-column row that field is `note` (harmless), but on a row
  # truncated after the hash columns the CR lands on vault_sha256 itself and
  # the digest comparison must fail (case-V6 T7 pins this boundary).
  while IFS= read -r line || [ -n "$line" ]; do
    if [ "$first" = 1 ]; then
      first=0
      case "$line" in source_path$'\t'*) continue ;; esac
    fi
    [ -n "$line" ] && LEDGER_ROWS+=("$line")
  done < "$LEDGER"
  return 0
}

# Column indexes from the header (extra interleaved columns must not break
# parsing); defaults follow the canonical order when the header is missing.
ledger_indexes() {
  local hdr col i=0
  IDX_SP=0; IDX_SS=1; IDX_VP=2; IDX_VS=3
  [ -f "$LEDGER" ] || return 0
  IFS= read -r hdr < "$LEDGER" || return 0
  hdr=${hdr%$'\r'}
  local IFS=$'\t'
  for col in $hdr; do
    case "$col" in
      source_path) IDX_SP=$i ;;
      source_sha256) IDX_SS=$i ;;
      vault_path) IDX_VP=$i ;;
      vault_sha256) IDX_VS=$i ;;
    esac
    i=$((i+1))
  done
  return 0
}

# ---------------------------------------------------------------------------
# Verdict emission
# ---------------------------------------------------------------------------
V_VERDICT=NOT-VERIFIED
V_REASON=none
V_EVIDENCE="no-receipt"

emit() { # $1 verdict-class, $2 reason, $3 evidence
  V_VERDICT=$1; V_REASON=$2; V_EVIDENCE=$3
}

print_line() { # $1 target
  local t=$1 te
  if [ "$JSON" = 1 ]; then
    printf '{"path":"%s","verdict":"%s","reason":"%s","receipt":"%s","evidence":"%s"}\n' \
      "$(json_escape "$t")" "$V_VERDICT" "$V_REASON" \
      "$([ "$V_VERDICT" = VERIFIED ] && printf moved-to-obsidian || printf none)" \
      "$(json_escape "$V_EVIDENCE")"
    return 0
  fi
  # One record per target: escape newline/tab/CR inside the path field so a
  # path containing them cannot split the record or shift later fields for
  # line-oriented TSV consumers (vadv-54 R1/R4).
  te=${t//\\/\\\\}
  te=${te//$'\t'/\\t}
  te=${te//$'\r'/\\r}
  te=${te//$'\n'/\\n}
  if [ "$V_VERDICT" = VERIFIED ]; then
    printf 'VERDICT\t%s\tSAFE\tmoved-to-obsidian\t%s\n' "$te" "$V_EVIDENCE"
    printf 'VERIFIED(moved-to-obsidian)\n'
  else
    printf 'VERDICT\t%s\tNOT-SAFE\tnone\t%s\n' "$te" "$V_EVIDENCE"
    printf 'NOT-VERIFIED(%s)\n' "$V_REASON"
  fi
}

# ---------------------------------------------------------------------------
# One target
# ---------------------------------------------------------------------------
verify_one() { # $1 target
  local target=$1 tcanon row sp ss vp vs
  local live_sha row_sha reason t_is_dir=0 cli_note=""
  local notes=()

  V_VERDICT=NOT-VERIFIED; V_REASON=none; V_EVIDENCE="no-receipt"

  if [ -z "$target" ]; then
    emit NOT-VERIFIED unreachable "empty target"
    return 0
  fi
  tcanon=$(canon_path "$target")

  if is_secret_shaped "$target"; then
    emit NOT-VERIFIED secrets-refusal "secret-shaped path refused basename=$(basename -- "$target")"
    return 0
  fi

  [ -d "$tcanon" ] && t_is_dir=1

  if [ "$WANT_CLI" = 1 ]; then
    cli_probe
    cli_note="cli=${CLI_STATE}"
  fi

  if ! ledger_load; then
    emit NOT-VERIFIED no-ledger "obsidian=no-ledger path=$LEDGER${cli_note:+ $cli_note}"
    return 0
  fi
  ledger_indexes

  if [ ${#LEDGER_ROWS[@]} -eq 0 ]; then
    emit NOT-VERIFIED no-ledger-row "obsidian=no-matching-ledger-row ledger=$LEDGER rows=0${cli_note:+ $cli_note}"
    return 0
  fi

  for row in "${LEDGER_ROWS[@]}"; do
    # Field-preserving split: bash `read -a` collapses runs of tabs, which
    # would silently shift a short row's fields left. Split manually so empty
    # fields stay empty (bash + coreutils only, no awk dependency).
    local _rest="$row" _field _f=()
    while :; do
      _field=${_rest%%$'\t'*}
      _f+=("$_field")
      [ "$_rest" = "$_field" ] && break
      _rest=${_rest#*$'\t'}
    done
    sp=${_f[$IDX_SP]:-}; ss=${_f[$IDX_SS]:-}; vp=${_f[$IDX_VP]:-}; vs=${_f[$IDX_VS]:-}
    # Only an absolute source_path can be a receipt: a relative row would be
    # resolved against the invocation cwd, making the verdict cwd-dependent
    # (vadv-52 J1-J5). Compare canonical forms, never raw strings.
    case "$sp" in
      /*) : ;;
      *) notes+=("obsidian=row-incomplete relative-source-path=$sp"); continue ;;
    esac
    [ "$(canon_path "$sp")" = "$tcanon" ] || continue

    # All four conjuncts must be present and non-empty; a row missing any of
    # them is not a receipt (never a silent SAFE from a short row).
    if [ -z "$ss" ] || [ -z "$vp" ] || [ -z "$vs" ]; then
      local _miss=""
      if [ -z "$ss" ]; then _miss="source_sha256"; fi
      if [ -z "$vp" ]; then _miss="${_miss:+$_miss,}vault_path"; fi
      if [ -z "$vs" ]; then _miss="${_miss:+$_miss,}vault_sha256"; fi
      notes+=("obsidian=row-incomplete missing=$_miss")
      continue
    fi

    if [ ! -e "$tcanon" ]; then
      notes+=("obsidian=source-absent source=$tcanon")
      emit NOT-VERIFIED source-absent "obsidian=source-absent row source=$tcanon vault=$vp"
      return 0
    fi

    if [ "$t_is_dir" = 1 ]; then
      live_sha=$(dir_digest "$tcanon") || live_sha=""
    else
      live_sha=$(file_sha "$tcanon" 2>/dev/null) || live_sha=""
    fi
    if [ -z "$live_sha" ]; then
      notes+=("obsidian=source-unreadable source=$tcanon")
      continue
    fi
    if [ "$live_sha" != "$ss" ]; then
      notes+=("obsidian=source-sha-mismatch live=${live_sha:0:12} row=${ss:0:12}")
      continue
    fi

    if [ "$(canon_path "$vp")" = "$tcanon" ]; then
      emit NOT-VERIFIED self-receipt "vault_path equals source path ($vp); not an independent copy"
      return 0
    fi

    if [ "$t_is_dir" = 1 ]; then
      # A vault copy nested INSIDE the directory being evaluated is not an
      # independent copy: removing the directory destroys its own receipt
      # (vadv-54 P6).
      local _vpc _tcc
      _vpc=$(canon_path "$vp"); _tcc=$tcanon
      case "$_vpc" in
        "$_tcc"/*) emit NOT-VERIFIED self-receipt "vault_path $vp is inside the source directory $tcanon; not an independent copy"; return 0 ;;
      esac
      if [ ! -d "$vp" ]; then
        notes+=("obsidian=vault-unreachable vault=$vp absent")
        emit NOT-VERIFIED vault-absent "obsidian=vault-unreachable source matches row; vault dir $vp absent"
        return 0
      fi
      row_sha=$(dir_digest "$vp") || row_sha=""
      if [ -z "$row_sha" ]; then
        emit NOT-VERIFIED vault-absent "obsidian=vault-unreachable vault=$vp unreadable"
        return 0
      fi
    else
      if [ ! -e "$vp" ]; then
        notes+=("obsidian=vault-unreachable vault=$vp absent")
        emit NOT-VERIFIED vault-absent "obsidian=vault-unreachable source matches row; vault=$vp absent"
        return 0
      fi
      case "$(stat -c %F -- "$vp" 2>/dev/null)" in
        "regular file"|"regular empty file") ;;
        *) emit NOT-VERIFIED vault-absent "obsidian=vault-unreachable vault=$vp not a regular file ($(stat -c %F -- "$vp" 2>/dev/null))"; return 0 ;;
      esac
      row_sha=$(file_sha "$vp" 2>/dev/null) || row_sha=""
      if [ -z "$row_sha" ]; then
        emit NOT-VERIFIED vault-absent "obsidian=vault-unreachable vault=$vp unreadable"
        return 0
      fi
    fi

    if [ "$row_sha" != "$vs" ]; then
      notes+=("obsidian=vault-sha-mismatch live=${row_sha:0:12} row=${vs:0:12}")
      continue
    fi

    emit VERIFIED none "ledger-row vault=$vp source-sha256=${ss:0:12} vault-sha256=${vs:0:12} verified=live${cli_note:+ $cli_note}"
    return 0
  done

  reason=no-ledger-row
  case "${notes[0]:-}" in
    *row-incomplete*) reason=row-incomplete ;;
    *source-sha-mismatch*) reason=source-hash-mismatch ;;
    *vault-sha-mismatch*) reason=vault-hash-mismatch ;;
    *vault-unreachable*) reason=vault-absent ;;
    *source-absent*) reason=source-absent ;;
    *source-unreadable*) reason=source-absent ;;
  esac
  emit NOT-VERIFIED "$reason" "${notes[*]:-}${cli_note:+ $cli_note}"
  return 0
}

# ---------------------------------------------------------------------------
# Selftest — isolated fixture world under mktemp -d
# ---------------------------------------------------------------------------
selftest() {
  local T rc=0 pass=0 fail=0
  T=$(mktemp -d "${TMPDIR:-/tmp}/souji-vault-s24.XXXXXX")
  trap 'rm -rf -- "${T:-}"' EXIT

  local FX="$T/fleet" VX="$T/vault"
  mkdir -p "$FX/corpus/knowledge" "$VX"
  local st_ledger="$FX/corpus/knowledge/obsidian-ledger.tsv"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$st_ledger"
  export SOUJI_LEDGER="$st_ledger"

  local old_ledger="$LEDGER"; LEDGER="$st_ledger"

  st() { # $1 id, $2 want-class, $3 want-reason-substr, $4 target
    local id=$1 wc=$2 wr=$3 tgt=$4
    verify_one "$tgt"
    local ok=1
    [ "$V_VERDICT" = "$wc" ] || ok=0
    if [ -n "$wr" ]; then
      case "$V_REASON$V_EVIDENCE" in *"$wr"*) : ;; *) ok=0 ;; esac
    fi
    if [ "$ok" = 1 ]; then pass=$((pass+1)); printf 'ST %s PASS %s(%s)\n' "$id" "$V_VERDICT" "$V_REASON"
    else fail=$((fail+1)); printf 'ST %s FAIL got=%s(%s) want=%s(%s) ev=%s\n' "$id" "$V_VERDICT" "$V_REASON" "$wc" "$wr" "$V_EVIDENCE"; fi
  }

  # S1 clean pair -> VERIFIED
  printf 'S24 selftest note alpha\n' > "$T/a.md"
  cp "$T/a.md" "$VX/a.md"; chmod 0444 "$VX/a.md"
  local sa; sa=$(sha256sum "$T/a.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 clean pair\n' "$T/a.md" "$sa" "$VX/a.md" "$sa" >> "$st_ledger"
  st S1 VERIFIED "" "$T/a.md"

  # S2 vault edited after row -> vault-hash-mismatch
  printf 'S24 beta\n' > "$T/b.md"; cp "$T/b.md" "$VX/b.md"
  local sb; sb=$(sha256sum "$T/b.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 stale vault\n' "$T/b.md" "$sb" "$VX/b.md" "$sb" >> "$st_ledger"
  printf 'edited-after-row\n' >> "$VX/b.md"
  st S2 NOT-VERIFIED vault-hash-mismatch "$T/b.md"

  # S3 source sha mismatch -> source-hash-mismatch
  printf 'S24 gamma\n' > "$T/c.md"; cp "$T/c.md" "$VX/c.md"
  local sc; sc=$(sha256sum "$T/c.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 bad source sha\n' "$T/c.md" "0000000000000000000000000000000000000000000000000000000000000000" "$VX/c.md" "$sc" >> "$st_ledger"
  st S3 NOT-VERIFIED source-hash-mismatch "$T/c.md"

  # S4 vault absent
  printf 'S24 delta\n' > "$T/d.md"
  local sd; sd=$(sha256sum "$T/d.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 vault absent\n' "$T/d.md" "$sd" "$VX/d.md" "$sd" >> "$st_ledger"
  st S4 NOT-VERIFIED vault-absent "$T/d.md"

  # S5 source absent
  local sd2; sd2=$(sha256sum "$T/d.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 source absent\n' "$T/e.md" "$sd2" "$VX/d.md" "$sd2" >> "$st_ledger"
  st S5 NOT-VERIFIED source-absent "$T/e.md"

  # S6 no ledger row
  printf 'S24 zeta\n' > "$T/f.md"
  st S6 NOT-VERIFIED no-ledger-row "$T/f.md"

  # S7 secrets refusal
  mkdir -p "$T/sec"; printf 'x\n' > "$T/sec/app.env"
  st S7 NOT-VERIFIED secrets-refusal "$T/sec/app.env"

  # S8 no ledger file at all
  LEDGER="$T/nonexistent-ledger.tsv"
  st S8 NOT-VERIFIED no-ledger "$T/a.md"
  LEDGER="$st_ledger"

  # S9 CRLF ledger row still matches (trailing CR trimmed)
  printf 'S24 eta\n' > "$T/g.md"; cp "$T/g.md" "$VX/g.md"
  local sg; sg=$(sha256sum "$T/g.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 crlf row\r\n' "$T/g.md" "$sg" "$VX/g.md" "$sg" >> "$st_ledger"
  st S9 VERIFIED "" "$T/g.md"

  # S10 FIFO vault side -> no hang, not VERIFIED
  printf 'S24 theta\n' > "$T/h.md"
  local sh; sh=$(sha256sum "$T/h.md" | cut -d' ' -f1)
  mkfifo "$VX/h.md" 2>/dev/null || true
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 fifo vault\n' "$T/h.md" "$sh" "$VX/h.md" "$sh" >> "$st_ledger"
  st S10 NOT-VERIFIED vault-absent "$T/h.md"
  rm -f "$VX/h.md"

  # S11 extra interleaved column (header-indexed parse)
  printf 'S24 iota\n' > "$T/i.md"; cp "$T/i.md" "$VX/i.md"
  local si; si=$(sha256sum "$T/i.md" | cut -d' ' -f1)
  local st2="$T/ledger-extra.tsv"
  printf 'source_path\tsource_sha256\textra\tvault_path\tvault_sha256\texported_at\tnote\n' > "$st2"
  printf '%s\t%s\tignored\t%s\t%s\t2026-10-18\tS24 extra col\n' "$T/i.md" "$si" "$VX/i.md" "$si" >> "$st2"
  LEDGER="$st2"
  st S11 VERIFIED "" "$T/i.md"
  LEDGER="$st_ledger"

  # S12 cli probe never executes a launcher; --cli degrades gracefully
  WANT_CLI=1
  CLI_HINT=""
  cli_probe
  local ok=1
  case "$CLI_STATE" in
    unavailable|socket-live|shim-present|bundled-present|shim-ambiguous|gui-launcher-only|hint-missing) : ;;
    *) ok=0 ;;
  esac
  if [ "$ok" = 1 ]; then pass=$((pass+1)); printf 'ST S12 PASS cli_probe=%s\n' "$CLI_STATE"
  else fail=$((fail+1)); printf 'ST S12 FAIL cli_probe=%s\n' "$CLI_STATE"; fi
  st S13 VERIFIED "" "$T/a.md"
  WANT_CLI=0

  # S14 row without trailing newline still parses
  printf 'S24 kappa\n' > "$T/j.md"; cp "$T/j.md" "$VX/j.md"
  local sj; sj=$(sha256sum "$T/j.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 no final newline' "$T/j.md" "$sj" "$VX/j.md" "$sj" >> "$st_ledger"
  st S14 VERIFIED "" "$T/j.md"
  printf '\n' >> "$st_ledger"

  # S15 short row (vault_sha256 missing) is not a receipt -> row-incomplete
  printf 'S24 lambda\n' > "$T/k.md"; cp "$T/k.md" "$VX/k.md"
  local sk; sk=$(sha256sum "$T/k.md" | cut -d' ' -f1)
  local st3="$T/ledger-short.tsv"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$st3"
  printf '%s\t%s\t%s\t\t2026-10-18\tS24 short row\n' "$T/k.md" "$sk" "$VX/k.md" >> "$st3"
  LEDGER="$st3"
  st S15 NOT-VERIFIED row-incomplete "$T/k.md"
  LEDGER="$st_ledger"

  # S16 directory digest pair -> VERIFIED
  mkdir -p "$T/dsrc" "$T/dvlt"
  printf 'one\n' > "$T/dsrc/one.txt"; cp "$T/dsrc/one.txt" "$T/dvlt/one.txt"
  local dd; dd=$(dir_digest "$T/dsrc")
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 dir pair\n' "$T/dsrc" "$dd" "$T/dvlt" "$dd" >> "$st_ledger"
  st S16 VERIFIED "" "$T/dsrc"

  # S17 self-receipt (vault_path == source_path) is not an independent copy
  printf 'S24 mu\n' > "$T/m.md"
  local sm; sm=$(sha256sum "$T/m.md" | cut -d' ' -f1)
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 self receipt\n' "$T/m.md" "$sm" "$T/m.md" "$sm" >> "$st_ledger"
  st S17 NOT-VERIFIED self-receipt "$T/m.md"

  # S18 dual output shape: line 1 = r2 VERDICT row (so line-1-only parsers
  # like case-V6/selftest.sh class_of work), line 2 = r4 vocabulary token.
  verify_one "$T/a.md"
  local l1 l2 l3
  l1=$(print_line "$T/a.md" | sed -n 1p)
  l2=$(print_line "$T/a.md" | sed -n 2p)
  l3=$(printf '%s' "$l1" | awk -F'\t' '{print $1"|"$3"|"$4}')
  if [ "$l2" = "VERIFIED(moved-to-obsidian)" ] && [ "$l3" = "VERDICT|SAFE|moved-to-obsidian" ]; then
    pass=$((pass+1)); printf 'ST S18 PASS r2-line-first %s\n' "$l3"
  else
    fail=$((fail+1)); printf 'ST S18 FAIL l2=%s l3=%s\n' "$l2" "$l3"
  fi

  # S19 true 6-column CRLF row (CR rides on the note column) -> VERIFIED
  printf 'S24 nu\n' > "$T/n.md"; cp "$T/n.md" "$VX/n.md"
  local sn; sn=$(sha256sum "$T/n.md" | cut -d' ' -f1)
  local st4="$T/ledger-trunc-crlf.tsv"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\r\n' > "$st4"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tS24 crlf six col\r\n' "$T/n.md" "$sn" "$VX/n.md" "$sn" >> "$st4"
  LEDGER="$st4"
  st S19 VERIFIED "" "$T/n.md"
  local st5="$T/ledger-trunc-crlf-short.tsv"
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\r\n' > "$st5"
  printf '%s\t%s\t%s\t%s\r\n' "$T/n.md" "$sn" "$VX/n.md" "$sn" >> "$st5"
  LEDGER="$st5"
  st S20 NOT-VERIFIED vault-hash-mismatch "$T/n.md"
  LEDGER="$st_ledger"

  LEDGER="$old_ledger"
  unset SOUJI_LEDGER 2>/dev/null || true

  printf 'selftest: %d checks, %d failed\n' "$((pass+fail))" "$fail"
  [ "$fail" -eq 0 ] || rc=1
  return "$rc"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --cli) WANT_CLI=1; shift ;;
    --fallback) FORCE_FALLBACK=1; shift ;;
    --ledger) [ $# -ge 2 ] || usage_err "--ledger requires a path"; LEDGER=$2; shift 2 ;;
    --vault) [ $# -ge 2 ] || usage_err "--vault requires a path"; VAULT_ROOT=$2; shift 2 ;;
    --stale-days) [ $# -ge 2 ] || usage_err "--stale-days requires N"; STALE_DAYS=$2; shift 2 ;;
    -h|--help) usage 0 ;;
    --) shift; break ;;
    -*) usage_err "unknown option: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done
while [ $# -gt 0 ]; do TARGETS+=("$1"); shift; done

[ "$FORCE_FALLBACK" = 1 ] && WANT_CLI=0

if [ "$SELFTEST" = 1 ]; then
  selftest
  exit $?
fi

[ ${#TARGETS[@]} -gt 0 ] || usage_err "no target given"

if [ "$WANT_CLI" = 1 ]; then
  cli_probe
  printf '# cli-state=%s %s\n' "$CLI_STATE" "$CLI_DETAIL" >&2
fi

rc=0
for t in "${TARGETS[@]}"; do
  verify_one "$t"
  print_line "$t"
done
exit "$rc"
