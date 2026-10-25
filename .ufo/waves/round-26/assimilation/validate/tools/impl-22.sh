#!/usr/bin/env bash
# impl-22 — round-4 Obsidian vault verification (seat S22, implementor, independent).
#
# Capability claim (round 4): ledger-backed `moved-to-obsidian` verification
# against corpus/knowledge/obsidian-ledger.tsv, with the official Obsidian CLI
# as an OPTIONAL advisory confirmer. The receipt of record is always the
# locally recomputed content-hash pair (source file/dir digest + vault
# file/dir digest) compared to the ledger row — a CLI claim alone is never a
# receipt, and a CLI disagreement never overrides the local hashes.
#
# Output (per target, two lines; --json prints one JSON object per target):
#   VERIFIED<TAB>moved-to-obsidian            (on a verified receipt)
#   NOT-VERIFIED(<reason>)                    (otherwise; bare token line)
#   VERDICT<TAB><path><TAB>SAFE|NOT-SAFE<TAB><receipt><TAB><evidence>
# The r4 token line comes first so greppers that take the first verdict-looking
# line read the r4 vocabulary; the r2-layout VERDICT line carries the path in
# field 2 for the awk-based parsers.
# exit codes: 0 evaluated clean; 1 selftest failure; 2 usage. No other codes.
#
# Env overrides
#   SOUJI_LEDGER / OBSIDIAN_LEDGER   ledger path
#   SOUJI_VAULT / SOUJI_VAULT_PATH / VAULT_PATH   vault root for RELATIVE rows
#   SOUJI_CLI        explicit CLI binary (skips discovery)
#   SOUJI_CLI_TIMEOUT seconds bound for one CLI call (default 10)
#   SHOKUNIN_ROOT    accepted for compatibility (unused: no worktree logic)
#
# CLI contract (--cli, opt-in)
#   Discovery: $SOUJI_CLI, else `obsidian-cli` on PATH, else
#   ~/.local/bin/obsidian-cli, else ~/.local/bin/obsidian (the shim the app
#   registers). A bare `obsidian` resolved from PATH is NEVER executed: on
#   this host that name is the desktop-app launcher. Any candidate whose first
#   bytes reference the Electron app bundle / launcher flags file is refused
#   unread. The call is bounded by `timeout`; the CLI is consulted only when a
#   ledger row already matches, and the whole probe is re-run AFTER the call,
#   so a mutation or rename race under the CLI read can never yield a stale
#   SAFE.
#
# Safety rails
#   * Secret-shaped path components are refused before anything is read.
#   * Read-only: sha256sum/stat/readlink/find on vault paths; no writes
#     outside `mktemp -d` fixture dirs (selftest only); no git subcommand is
#     ever issued; no network.
set -uo pipefail

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
SELF="$SCRIPT_DIR/$(basename -- "$SCRIPT_PATH")"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
LEDGER="${SOUJI_LEDGER:-${OBSIDIAN_LEDGER:-$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv}}"
VAULT_ROOT="${SOUJI_VAULT:-${SOUJI_VAULT_PATH:-${VAULT_PATH:-/home/vgpnk/Documents/shokoknowledge}}}"
CLI_TIMEOUT="${SOUJI_CLI_TIMEOUT:-10}"

JSON=0
SELFTEST=0
CLI_MODE=0
TARGETS=()
CLI_BIN=""
CLI_NOTE=""

usage() { # $1 = exit code
  sed -n '2,40p' "$SELF" | sed 's/^# \{0,1\}//'
  exit "$1"
}
usage_err() { printf 'impl-22: %s\n' "$1" >&2; usage 2; }

# ---------------------------------------------------------------- primitives

canon() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

is_secret_shaped() { # $1 = path; matches per component, case-insensitive
  local comp lc
  local IFS='/'
  set -f
  for comp in $1; do
    lc=${comp,,}
    case "$lc" in
      *.env|.env|.env.*|.envrc|*credential*|*secret*|id_*|*.pem) set +f; return 0 ;;
    esac
  done
  set +f
  return 1
}

file_sha() { [ -f "$1" ] || return 1; sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

dir_digest() { # deterministic manifest digest of a directory (ignores .git)
  local d=$1
  [ -d "$d" ] || return 1
  ( cd "$d" 2>/dev/null && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

is_regular() { [ -f "$1" ] && [ ! -p "$1" ]; }

sha12() { printf '%s' "${1:0:12}"; }

json_escape() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

# ------------------------------------------------------------- ledger probe
# ledger_probe <abs-target> <texists 0/1>
# stdout: <status><TAB><vault-path><TAB><detail>
# statuses: match | source-absent | vault-absent | vault-sha-mismatch |
#           source-sha-mismatch | none
ledger_probe() {
  local target=$1 texists=$2
  local row n=0 sp ss vp vs vfull
  local best_status=none best_vp="" best_detail="no-matching-ledger-row" rows=0
  if [ ! -f "$LEDGER" ]; then
    printf 'none\t\tno-ledger-file\n'; return 0
  fi
  if is_secret_shaped "$LEDGER"; then
    printf 'none\t\tledger-secret-shaped\n'; return 0
  fi
  while IFS= read -r row || [ -n "$row" ]; do
    row=${row%$'\r'}
    n=$((n+1))
    if [ "$n" -eq 1 ]; then
      case "$row" in source_path$'\t'*) continue ;; esac
    fi
    [ -n "$row" ] || continue
    rows=$((rows+1))
    sp=$(printf '%s' "$row" | awk -F'\t' '{print $1}')
    ss=$(printf '%s' "$row" | awk -F'\t' '{print $2}')
    vp=$(printf '%s' "$row" | awk -F'\t' '{print $3}')
    vs=$(printf '%s' "$row" | awk -F'\t' '{print $4}')
    [ -n "$sp" ] || continue
    if [ "$sp" != "$target" ]; then
      if [ -e "$sp" ] && [ "$(canon "$sp")" = "$target" ]; then :; else continue; fi
    fi
    case "$vp" in
      /*) vfull=$vp ;;
      '') vfull="" ;;
      *) vfull="$VAULT_ROOT/$vp" ;;
    esac
    best_vp=$vfull
    if [ "$texists" -eq 0 ]; then
      best_status=source-absent
      best_detail="ledger_row=$n source-absent"
      continue
    fi
    if [ -z "$ss" ]; then
      best_status=none
      best_detail="ledger_row=$n source-hash-empty"
      continue
    fi
    local sactual="" vactual=""
    if [ -d "$target" ]; then sactual=$(dir_digest "$target") || sactual=""
    else sactual=$(file_sha "$target") || sactual=""
    fi
    if [ -z "$sactual" ]; then
      best_status=source-absent
      best_detail="ledger_row=$n source-unreadable"
      continue
    fi
    if [ "$sactual" != "$ss" ]; then
      best_status=source-sha-mismatch
      best_detail="ledger_row=$n source expected=$(sha12 "$ss") actual=$(sha12 "$sactual")"
      continue
    fi
    if [ -z "$vp" ] || [ -z "$vs" ]; then
      best_status=none
      best_detail="ledger_row=$n vault-path-or-hash-empty"
      continue
    fi
    if is_secret_shaped "$vfull"; then
      best_status=none
      best_detail="ledger_row=$n vault-secret-shaped"
      continue
    fi
    # self-export guard (judge B22-B24): a vault path that resolves to the
    # source itself (identical spelling, ../ alias, or symlink to the source)
    # is not an export and must never verify.
    if [ "$(canon "$vfull")" = "$target" ]; then
      best_status=self-export
      best_detail="ledger_row=$n vault-path-is-source vault=$vfull"
      continue
    fi
    if [ -d "$target" ]; then
      if ! [ -d "$vfull" ]; then
        best_status=vault-absent
        best_detail="ledger_row=$n vault-unreachable vault=$vfull"
        continue
      fi
      vactual=$(dir_digest "$vfull") || vactual=""
      if [ -z "$vactual" ]; then
        best_status=vault-absent
        best_detail="ledger_row=$n vault-unreadable vault=$vfull"
        continue
      fi
      if [ "$vactual" != "$vs" ]; then
        best_status=vault-sha-mismatch
        best_detail="ledger_row=$n vault expected=$(sha12 "$vs") actual=$(sha12 "$vactual")"
        continue
      fi
      printf 'match\t%s\tledger_row=%s dir-digest source=%s vault=%s\n' \
        "$vfull" "$n" "$(sha12 "$ss")" "$(sha12 "$vactual")"
      return 0
    fi
    if ! is_regular "$vfull"; then
      best_status=vault-absent
      best_detail="ledger_row=$n vault-unreachable vault=$vfull"
      continue
    fi
    vactual=$(file_sha "$vfull") || vactual=""
    if [ -z "$vactual" ]; then
      best_status=vault-absent
      best_detail="ledger_row=$n vault-unreadable vault=$vfull"
      continue
    fi
    if [ "$vactual" != "$vs" ]; then
      best_status=vault-sha-mismatch
      best_detail="ledger_row=$n vault expected=$(sha12 "$vs") actual=$(sha12 "$vactual")"
      continue
    fi
    printf 'match\t%s\tledger_row=%s source=%s vault=%s\n' \
      "$vfull" "$n" "$(sha12 "$ss")" "$(sha12 "$vactual")"
    return 0
  done < "$LEDGER"
  printf '%s\t%s\t%s rows=%s\n' "$best_status" "$best_vp" "$best_detail" "$rows"
  return 0
}

# ------------------------------------------------------------------- CLI path

cli_guard() { # refuse launcher-shaped candidates without executing them
  local c=$1 head
  head=$(head -c 2048 -- "$c" 2>/dev/null || true)
  case "$head" in
    *app.asar*|*electron43*|*user-flags*) return 1 ;;
  esac
  return 0
}

cli_discover() {
  local cand
  CLI_BIN=""
  if [ -n "${SOUJI_CLI:-}" ]; then
    cand=$SOUJI_CLI
    if [ -f "$cand" ] && [ -x "$cand" ]; then
      if cli_guard "$cand"; then
        CLI_BIN=$cand; CLI_NOTE="cli=available"
        return 0
      fi
      CLI_NOTE="cli=refused-launcher-shape"
      return 1
    fi
    CLI_NOTE="cli=explicit-missing"
    return 1
  fi
  if command -v obsidian-cli >/dev/null 2>&1; then
    cand=$(command -v obsidian-cli)
    if cli_guard "$cand"; then
      CLI_BIN=$cand; CLI_NOTE="cli=available"
      return 0
    fi
    CLI_NOTE="cli=refused-launcher-shape"
    return 1
  fi
  for cand in "$HOME/.local/bin/obsidian-cli" "$HOME/.local/bin/obsidian"; do
    if [ -f "$cand" ] && [ -x "$cand" ]; then
      if cli_guard "$cand"; then
        CLI_BIN=$cand; CLI_NOTE="cli=available"
        return 0
      fi
      CLI_NOTE="cli=refused-launcher-shape"
      return 1
    fi
  done
  CLI_NOTE="cli=unavailable"
  return 1
}

cli_hash() { # $1 = vault file; prints a 64-hex claim or ""
  local f=$1 out
  [ -n "$CLI_BIN" ] || return 1
  out=$(timeout "$CLI_TIMEOUT" "$CLI_BIN" file --json -- "$f" 2>/dev/null) || true
  if [ -z "$out" ]; then
    out=$(timeout "$CLI_TIMEOUT" "$CLI_BIN" -- "$f" 2>/dev/null) || true
  fi
  printf '%s\n' "$out" | grep -aoE '[0-9a-f]{64}' | head -1
}

cli_verify() { # $1 = vault file, $2 = expected ledger hash; sets CLI_NOTE
  [ "$CLI_MODE" = 1 ] || return 0
  [ -n "$CLI_BIN" ] || return 0
  local claim post
  claim=$(cli_hash "$1" || true)
  post=$(file_sha "$1" || true)
  if [ -z "$claim" ]; then
    CLI_NOTE="cli=unparsed"
  elif [ "$claim" = "$2" ] && [ "$post" = "$2" ]; then
    CLI_NOTE="cli=agree"
  elif [ "$claim" != "$post" ]; then
    CLI_NOTE="cli=disagreement claim=$(sha12 "$claim") post=$(sha12 "$post")"
  else
    CLI_NOTE="cli=agree"
  fi
  return 0
}

# ------------------------------------------------------------------- verdict

emit() { # $1 path-as-given, $2 r2 verdict, $3 receipt, $4 evidence, $5 r4 token line
  if [ "$JSON" = 1 ]; then
    printf '{"path":"%s","verdict":"%s","receipt":"%s","evidence":"%s"}\n' \
      "$(json_escape "$1")" "$2" "$3" "$(json_escape "$4")"
  else
    printf '%s\n' "$5"
    printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4"
  fi
}

cli_suffix() { # appended to every evidence line when --cli was requested
  [ "$CLI_MODE" = 1 ] || return 0
  printf ' %s' "$CLI_NOTE"
}

emit_nv() { # $1 raw, $2 receipt, $3 evidence-base, $4 r4 token
  emit "$1" NOT-SAFE "$2" "$3$(cli_suffix)" "$4"
}

evaluate() { # $1 = target as given
  local raw=$1 target probe status vp detail
  if [ -z "$raw" ]; then
    emit_nv "" unreachable "target-unreachable empty-arg" "NOT-VERIFIED(unreachable)"
    return 0
  fi
  target=$(canon "$raw")
  if is_secret_shaped "$raw"; then
    emit_nv "$raw" none "secrets-refusal basename=${raw##*/}" "NOT-VERIFIED(secrets-refusal)"
    return 0
  fi
  local texists=0 dangling=0
  if [ -e "$target" ]; then texists=1
  elif [ -L "$target" ]; then dangling=1
  fi
  probe=$(ledger_probe "$target" "$texists")
  status=${probe%%$'\t'*}
  detail=${probe##*$'\t'}
  vp=$(printf '%s' "$probe" | cut -f2)
  case "$status" in
    match)
      if [ "$CLI_MODE" = 1 ]; then
        if [ -f "$target" ] && is_regular "$vp"; then
          local want_vs
          want_vs=$(file_sha "$vp" || true)
          cli_verify "$vp" "$want_vs"
          # re-run the whole probe after the CLI read: a mutation/rename under
          # the CLI read can never yield a stale SAFE
          probe=$(ledger_probe "$target" "$texists")
          status=${probe%%$'\t'*}
          detail=${probe##*$'\t'}
          vp=$(printf '%s' "$probe" | cut -f2)
          if [ "$status" != match ]; then
            case "$status" in
              vault-sha-mismatch)
                emit_nv "$raw" none "obsidian=vault-sha-mismatch vault=$vp race=changed-under-cli $detail" "NOT-VERIFIED(vault-hash-mismatch)" ;;
              vault-absent)
                emit_nv "$raw" none "obsidian=vault-unreachable vault-absent vault=$vp race=changed-under-cli $detail" "NOT-VERIFIED(vault-absent)" ;;
              *)
                emit_nv "$raw" none "obsidian=no-matching-ledger-row race=changed-under-cli $detail" "NOT-VERIFIED(none)" ;;
            esac
            return 0
          fi
        else
          CLI_NOTE="cli=skipped-dir-or-fifo"
        fi
      fi
      emit "$raw" SAFE moved-to-obsidian "obsidian=ledger-match vault=$vp $detail$(cli_suffix)" $'VERIFIED\tmoved-to-obsidian'
      ;;
    vault-absent)
      emit_nv "$raw" none \
        "obsidian=vault-unreachable vault-absent vault=$vp $detail" "NOT-VERIFIED(vault-absent)"
      ;;
    vault-sha-mismatch)
      emit_nv "$raw" none \
        "obsidian=vault-sha-mismatch vault=$vp $detail" "NOT-VERIFIED(vault-hash-mismatch)"
      ;;
    source-sha-mismatch)
      emit_nv "$raw" none \
        "obsidian=source-sha-mismatch source=$target $detail" "NOT-VERIFIED(source-hash-mismatch)"
      ;;
    source-absent)
      emit_nv "$raw" none \
        "obsidian=source-absent source-unreachable source=$target $detail" "NOT-VERIFIED(source-absent)"
      ;;
    self-export)
      emit_nv "$raw" none \
        "obsidian=self-export vault-path-is-source source=$target $detail" "NOT-VERIFIED(self-export)"
      ;;
    none)
      if [ "$texists" -eq 0 ] && [ "$dangling" -eq 0 ]; then
        emit_nv "$raw" unreachable "target-unreachable path=$target $detail" "NOT-VERIFIED(unreachable)"
      else
        emit_nv "$raw" none "obsidian=no-matching-ledger-row ledger=$LEDGER $detail" "NOT-VERIFIED(none)"
      fi
      ;;
    *)
      emit_nv "$raw" none "obsidian=unexpected-probe-status status=$status" "NOT-VERIFIED(none)"
      ;;
  esac
  return 0
}

# ----------------------------------------------------------------- selftest

ST_PASS=0 ST_FAIL=0
st_note() { printf '%s\n' "$*"; }

st_check() { # $1 id, $2 out, $3 want-class, $4 want-evidence-substr, $5 want-token
  local id=$1 out=$2 wv=$3 wsub=$4 wtok=$5
  local line v e tok
  line=$(printf '%s\n' "$out" | awk -F'\t' '$1=="VERDICT"{print; exit}')
  tok=$(printf '%s\n' "$out" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -1)
  if [ -z "$line" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: no VERDICT line out=$out"; return 0
  fi
  v=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
  e=$(printf '%s' "$line" | awk -F'\t' '{print $5}')
  if [ "$v" != "$wv" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: verdict=$v want=$wv line=$line"; return 0
  fi
  if [ -n "$wsub" ]; then
    case "$e" in *"$wsub"*) : ;; *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: evidence '$e' lacks '$wsub'"; return 0 ;; esac
  fi
  if [ -n "$wtok" ] && [ "$tok" != "$wtok" ]; then
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id: token='$tok' want='$wtok'"; return 0
  fi
  ST_PASS=$((ST_PASS+1)); st_note "PASS $id $v ($tok)"
}

st_case() { # $1 id, $2 want-class, $3 want-substr, $4 want-token, rest = args
  local id=$1 wv=$2 wsub=$3 wtok=$4; shift 4
  local out
  out=$(SOUJI_SELFTEST_ACTIVE=1 "$SELF" "$@" 2>&1)
  st_check "$id" "$out" "$wv" "$wsub" "$wtok"
}

st_case_cli() { # $1 id, $2 cli path, $3 want-class, $4 want-substr, $5 want-token, rest = args
  local id=$1 clipath=$2 wv=$3 wsub=$4 wtok=$5; shift 5
  local out
  out=$(SOUJI_SELFTEST_ACTIVE=1 SOUJI_CLI="$clipath" SOUJI_CLI_TIMEOUT=2 "$SELF" "$@" 2>&1)
  st_check "$id" "$out" "$wv" "$wsub" "$wtok"
}

st_status() { # $1 id, $2 want-exit, rest args
  local id=$1 want=$2; shift 2
  local status
  SOUJI_SELFTEST_ACTIVE=1 "$SELF" "$@" >/dev/null 2>&1
  status=$?
  if [ "$status" = "$want" ]; then ST_PASS=$((ST_PASS+1)); st_note "PASS $id exit=$status"
  else ST_FAIL=$((ST_FAIL+1)); st_note "FAIL $id exit=$status want=$want"; fi
}

run_selftest() {
  if [ "${SOUJI_SELFTEST_ACTIVE:-0}" = 1 ]; then
    printf 'impl-22: refusing nested --selftest\n' >&2
    exit 1
  fi
  local W
  W=$(mktemp -d "${TMPDIR:-/tmp}/impl22-selftest.XXXXXX") || { printf 'impl-22: mktemp failed\n' >&2; exit 1; }
  trap 'rm -rf -- "$W"' EXIT
  local SRC="$W/src" VLT="$W/vault" LED="$W/ledgers" BIN="$W/bin"
  mkdir -p "$SRC" "$VLT" "$LED" "$BIN"

  printf '# ok\n\nbody\n' > "$SRC/ok.md"; cp "$SRC/ok.md" "$VLT/ok.md"
  printf '# vtamper\n\nbody v\n' > "$SRC/vtamper.md"; cp "$SRC/vtamper.md" "$VLT/vtamper.md"
  printf '# stamper\n\nbody s\n' > "$SRC/stamper.md"; cp "$SRC/stamper.md" "$VLT/stamper.md"
  printf '# vmiss\n\nbody m\n' > "$SRC/vmiss.md"
  printf '# gone\n\nbody g\n' > "$SRC/gone.md"
  cp "$SRC/gone.md" "$VLT/gone.md"
  printf '' > "$SRC/empty.md"; cp "$SRC/empty.md" "$VLT/empty.md"
  printf 'PEM-ish\n' > "$SRC/creds.pem"
  mkdir -p "$SRC/dirA" "$VLT/dirA"
  printf 'one\n' > "$SRC/dirA/one.txt"; printf 'one\n' > "$VLT/dirA/one.txt"
  printf '# crlf\n\nbody c\n' > "$SRC/crlf.md"; cp "$SRC/crlf.md" "$VLT/crlf.md"
  printf '# nonl\n\nbody n\n' > "$SRC/nonl.md"; cp "$SRC/nonl.md" "$VLT/nonl.md"
  printf '# sym\n\nbody sl\n' > "$SRC/sym.md"; cp "$SRC/sym.md" "$VLT/sym-target.md"
  ln -s "$VLT/sym-target.md" "$VLT/sym.md"
  printf '# selfmove\n\nbody sm\n' > "$SRC/selfmove.md"
  printf '# alias\n\nbody al\n' > "$SRC/alias.md"
  printf '# symalias\n\nbody sa\n' > "$SRC/symalias.md"
  ln -s "$SRC/symalias.md" "$VLT/symalias.md"
  mkfifo "$VLT/fifo.md" 2>/dev/null || true

  local OK_S VT_S ST_S VM_S GO_S EM_S CR_S NL_S SY_S DA_S DA_V WRONG
  OK_S=$(file_sha "$SRC/ok.md"); VT_S=$(file_sha "$SRC/vtamper.md"); ST_S=$(file_sha "$SRC/stamper.md")
  VM_S=$(file_sha "$SRC/vmiss.md"); GO_S=$(file_sha "$SRC/gone.md"); EM_S=$(file_sha "$SRC/empty.md")
  CR_S=$(file_sha "$SRC/crlf.md"); NL_S=$(file_sha "$SRC/nonl.md"); SY_S=$(file_sha "$SRC/sym.md")
  DA_S=$(dir_digest "$SRC/dirA"); DA_V=$(dir_digest "$VLT/dirA")
  WRONG=1111111111111111111111111111111111111111111111111111111111111111

  local HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
  printf '%s\n' "$HDR" > "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tmatch\n'   "$SRC/ok.md" "$OK_S" "$VLT/ok.md" "$OK_S" >> "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvtamper\n' "$SRC/vtamper.md" "$VT_S" "$VLT/vtamper.md" "$VT_S" >> "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tstamper\n' "$SRC/stamper.md" "$WRONG" "$VLT/stamper.md" "$(file_sha "$VLT/stamper.md")" >> "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvmiss\n'   "$SRC/vmiss.md" "$VM_S" "$VLT/vmiss.md" "$VM_S" >> "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tgone\n'    "$SRC/gone.md" "$GO_S" "$VLT/gone.md" "$GO_S" >> "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tempty\n'   "$SRC/empty.md" "$EM_S" "$VLT/empty.md" "$EM_S" >> "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tdirA\n'    "$SRC/dirA" "$DA_S" "$VLT/dirA" "$DA_V" >> "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tcrlf\r\n'  "$SRC/crlf.md" "$CR_S" "$VLT/crlf.md" "$CR_S" >> "$LED/main.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tsym\n'     "$SRC/sym.md" "$SY_S" "$VLT/sym.md" "$SY_S" >> "$LED/main.tsv"
  printf 'EDIT\n' >> "$VLT/vtamper.md"
  rm -f -- "$SRC/gone.md"

  printf '%s\n' "$HDR" > "$LED/nonl.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tunterminated' "$SRC/nonl.md" "$NL_S" "$VLT/nonl.md" "$NL_S" >> "$LED/nonl.tsv"

  printf '%s\n' "$HDR" > "$LED/emptyhash.tsv"
  printf '%s\t\t%s\t%s\t2026-10-18\tvault-empty\n' "$SRC/ok.md" "$VLT/ok.md" "$OK_S" >> "$LED/emptyhash.tsv"

  printf '%s\n' "$HDR" > "$LED/headeronly.tsv"
  : > "$LED/zero.tsv"

  printf '%s\r\n' "$HDR" > "$LED/crlf.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tcrlf-row\r\n' "$SRC/ok.md" "$OK_S" "$VLT/ok.md" "$OK_S" >> "$LED/crlf.tsv"

  printf '%s\n' "$HDR" > "$LED/fifo.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tfifo\n' "$SRC/ok.md" "$OK_S" "$VLT/fifo.md" "$OK_S" >> "$LED/fifo.tsv"

  printf '%s\n' "$HDR" > "$LED/dirbad.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tdir-wrong\n' "$SRC/dirA" "$DA_S" "$VLT/dirA" "$WRONG" >> "$LED/dirbad.tsv"

  local SM_S AL_S SA_S
  SM_S=$(file_sha "$SRC/selfmove.md"); AL_S=$(file_sha "$SRC/alias.md"); SA_S=$(file_sha "$SRC/symalias.md")
  printf '%s\n' "$HDR" > "$LED/selfmove.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tself-move\n' "$SRC/selfmove.md" "$SM_S" "$SRC/selfmove.md" "$SM_S" >> "$LED/selfmove.tsv"
  printf '%s\n' "$HDR" > "$LED/alias.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tpath-alias\n' "$SRC/alias.md" "$AL_S" "$SRC/../src/alias.md" "$AL_S" >> "$LED/alias.tsv"
  printf '%s\n' "$HDR" > "$LED/symalias.tsv"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tsymlink-alias\n' "$SRC/symalias.md" "$SA_S" "$VLT/symalias.md" "$SA_S" >> "$LED/symalias.tsv"

  printf '#!/usr/bin/env bash\nsleep 30\n' > "$BIN/obsidian-cli-hang"; chmod +x "$BIN/obsidian-cli-hang"
  cat > "$BIN/mock-honest" <<'MOCK'
#!/usr/bin/env bash
f=""; for a in "$@"; do [ -f "$a" ] && f=$a; done
h=$(sha256sum -- "$f" 2>/dev/null | cut -d' ' -f1)
printf '{"path":"%s","sha256":"%s"}\n' "$f" "$h"
MOCK
  cat > "$BIN/mock-lying" <<'MOCK'
#!/usr/bin/env bash
f=""; for a in "$@"; do [ -f "$a" ] && f=$a; done
printf '{"path":"%s","sha256":"%s"}\n' "$f" "0000000000000000000000000000000000000000000000000000000000000000"
MOCK
  cat > "$BIN/mock-gui-shape" <<MOCK
#!/usr/bin/env bash
printf 'launched\n' >> "$W/gui-marker"
exec electron43 /usr/lib/obsidian/app.asar "\$@"
MOCK
  chmod +x "$BIN/mock-honest" "$BIN/mock-lying" "$BIN/mock-gui-shape"

  st_case T01 SAFE "vault=" $'VERIFIED\tmoved-to-obsidian' --ledger "$LED/main.tsv" "$SRC/ok.md"
  st_case T02 NOT-SAFE "vault-sha-mismatch" "NOT-VERIFIED(vault-hash-mismatch)" --ledger "$LED/main.tsv" "$SRC/vtamper.md"
  st_case T03 NOT-SAFE "source-sha-mismatch" "NOT-VERIFIED(source-hash-mismatch)" --ledger "$LED/main.tsv" "$SRC/stamper.md"
  st_case T04 NOT-SAFE "vault-unreachable" "NOT-VERIFIED(vault-absent)" --ledger "$LED/main.tsv" "$SRC/vmiss.md"
  st_case T05 NOT-SAFE "source-absent" "NOT-VERIFIED(source-absent)" --ledger "$LED/main.tsv" "$SRC/gone.md"
  st_case T06 NOT-SAFE "no-matching-ledger-row" "NOT-VERIFIED(none)" --ledger "$LED/headeronly.tsv" "$SRC/ok.md"
  st_case T07 NOT-SAFE "no-matching-ledger-row" "NOT-VERIFIED(none)" --ledger "$LED/zero.tsv" "$SRC/ok.md"
  st_case T08 SAFE "vault=" $'VERIFIED\tmoved-to-obsidian' --ledger "$LED/crlf.tsv" "$SRC/ok.md"
  st_case T09 SAFE "vault=" $'VERIFIED\tmoved-to-obsidian' --ledger "$LED/nonl.tsv" "$SRC/nonl.md"
  st_case T10 NOT-SAFE "source-hash-empty" "NOT-VERIFIED(none)" --ledger "$LED/emptyhash.tsv" "$SRC/ok.md"
  st_case T11 SAFE "vault=" $'VERIFIED\tmoved-to-obsidian' --ledger "$LED/main.tsv" "$SRC/empty.md"
  st_case T12 SAFE "vault=" $'VERIFIED\tmoved-to-obsidian' --ledger "$LED/main.tsv" "$SRC/dirA"
  st_case T13 NOT-SAFE "vault-sha-mismatch" "NOT-VERIFIED(vault-hash-mismatch)" --ledger "$LED/dirbad.tsv" "$SRC/dirA"
  st_case T14 SAFE "vault=" $'VERIFIED\tmoved-to-obsidian' --ledger "$LED/main.tsv" "$SRC/sym.md"
  st_case T15 NOT-SAFE "secrets-refusal" "NOT-VERIFIED(secrets-refusal)" --ledger "$LED/main.tsv" "$SRC/creds.pem"
  st_case T16 NOT-SAFE "vault-unreachable" "NOT-VERIFIED(vault-absent)" --ledger "$LED/fifo.tsv" "$SRC/ok.md"
  st_case T17 NOT-SAFE "cli=" "NOT-VERIFIED(none)" --cli --ledger "$LED/headeronly.tsv" "$SRC/ok.md"
  st_case_cli T18 "$BIN/mock-honest" SAFE "cli=agree" $'VERIFIED\tmoved-to-obsidian' --cli --ledger "$LED/main.tsv" "$SRC/ok.md"
  st_case_cli T19 "$BIN/mock-lying" SAFE "cli=disagreement" $'VERIFIED\tmoved-to-obsidian' --cli --ledger "$LED/main.tsv" "$SRC/ok.md"
  st_case_cli T20 "$BIN/obsidian-cli-hang" SAFE "cli=unparsed" $'VERIFIED\tmoved-to-obsidian' --cli --ledger "$LED/main.tsv" "$SRC/ok.md"
  st_case T21 NOT-SAFE "self-export" "NOT-VERIFIED(self-export)" --ledger "$LED/selfmove.tsv" "$SRC/selfmove.md"
  st_case T24 NOT-SAFE "self-export" "NOT-VERIFIED(self-export)" --ledger "$LED/alias.tsv" "$SRC/alias.md"
  st_case T25 NOT-SAFE "self-export" "NOT-VERIFIED(self-export)" --ledger "$LED/symalias.tsv" "$SRC/symalias.md"
  st_status T22 2
  st_status T23 2 --bogus-flag "$SRC/ok.md"

  # H2: GUI-shaped SOUJI_CLI is refused without being executed
  local marker="$W/gui-marker"; : > "$marker"
  SOUJI_SELFTEST_ACTIVE=1 SOUJI_CLI="$BIN/mock-gui-shape" "$SELF" --cli --ledger "$LED/main.tsv" "$SRC/ok.md" >/dev/null 2>&1
  if [ ! -s "$marker" ]; then
    ST_PASS=$((ST_PASS+1)); st_note "PASS H2 launcher-shaped CLI not executed"
  else
    ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H2 launcher-shaped CLI executed"
  fi

  # H3: JSON shape
  local jout
  jout=$(SOUJI_SELFTEST_ACTIVE=1 "$SELF" --json --ledger "$LED/main.tsv" "$SRC/ok.md" 2>&1)
  case "$jout" in
    '{"path":"'*'"verdict":"SAFE","receipt":"moved-to-obsidian","evidence":"'*'"}')
      ST_PASS=$((ST_PASS+1)); st_note "PASS H3 json shape" ;;
    *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H3 json shape '$jout'" ;;
  esac

  # H1: no forbidden git subcommand in executable lines
  local nh
  nh=$(grep -nE '^[^#]*git +(-C +[^ ]+ +)?(fetch|push|commit|branch|checkout|reset|rebase)( |$)' "$SELF" | wc -l || true)
  nh=${nh// /}
  if [ "${nh:-1}" = 0 ]; then ST_PASS=$((ST_PASS+1)); st_note "PASS H1 no forbidden git subcommand"
  else ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H1 $nh forbidden git invocation(s)"; fi

  # H4: fixtures isolated under mktemp
  case "$W" in "${TMPDIR:-/tmp}"/*) ST_PASS=$((ST_PASS+1)); st_note "PASS H4 fixtures under mktemp ($W)" ;;
    *) ST_FAIL=$((ST_FAIL+1)); st_note "FAIL H4 fixtures not under mktemp ($W)" ;; esac

  st_note "selftest: $((ST_PASS + ST_FAIL)) checks, $ST_FAIL failed"
  if [ "$ST_FAIL" -gt 0 ]; then exit 1; fi
  exit 0
}

# ------------------------------------------------------------------- main

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --cli) CLI_MODE=1; shift ;;
    --fallback|--auto) shift ;;
    --ledger) [ "$#" -ge 2 ] || usage_err "--ledger needs a value"; LEDGER=$2; shift 2 ;;
    --ledger=*) LEDGER=${1#*=}; shift ;;
    --vault) [ "$#" -ge 2 ] || usage_err "--vault needs a value"; VAULT_ROOT=$2; shift 2 ;;
    --vault=*) VAULT_ROOT=${1#*=}; shift ;;
    --stale-days) [ "$#" -ge 2 ] || usage_err "--stale-days needs a value"; shift 2 ;;
    --stale-days=*) shift ;;
    -h|--help) usage 0 ;;
    --) shift; while [ "$#" -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -*) usage_err "unknown flag: $1" ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

if [ "$SELFTEST" = 1 ]; then run_selftest; fi

if [ "${#TARGETS[@]}" -eq 0 ]; then
  usage_err "no targets"
fi

if [ "$CLI_MODE" = 1 ]; then
  cli_discover || true
fi

for t in "${TARGETS[@]}"; do
  evaluate "$t"
done
exit 0
