#!/usr/bin/env bash
# souji-vault-verify.impl-23.sh — round-4 vault verification (SEAT S23).
#
# Question: does the ledger's `moved-to-obsidian` receipt hold? For each
# target the tool re-derives BOTH sides of every matching ledger row:
# source path + source sha256, vault path + vault sha256. A row receipts
# only when all four conjuncts hold at evaluation time and the vault copy
# is a distinct, surviving copy (not the source itself, not a path alias,
# not nested inside the source directory).
#
# CLI
#   tools/souji-vault-verify.impl-23.sh [--selftest] [--json] [--cli]
#       [--fallback] [--stale-days N] [--ledger FILE] <path>...
#
# Output (default) — two lines per target:
#   VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence
#   VERIFIED(moved-to-obsidian) | NOT-VERIFIED(reason)
# The first line is the r2-addressable record (field 3 = class, field 4 =
# receipt, field 5 = evidence); the second is the r4 single-token verdict
# with the fixture reason vocabulary (vault-hash-mismatch, source-hash,
# vault-absent, source-absent, moved-to-obsidian, ...).
#
# CLI integration status: the official Obsidian CLI is a socket client of a
# running app; on this host the shim is unregistered and no socket exists
# (evidence: .ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md and
# census/round-4/seat-05.json). This tool therefore NEVER executes any
# external CLI binary: `--cli` is accepted, the cli state is reported on
# stderr, and verification always runs through read-only sha256sum under
# the vault path (the fallback the evidence bank anticipated). A lying,
# hanging, or absent CLI can never turn into a false SAFE because the CLI
# is never consulted for the verdict.
#
# Safety rails
#   * Read-only everywhere: sha256sum/stat/readlink only; nothing is
#     written outside `mktemp -d` (selftest) — the real vault and the live
#     ledger are never written.
#   * Never executes `obsidian` or any desktop-app launcher; no git verbs.
#   * Secret-shaped path components (*.env/.env/.env.*/.envrc/
#     *credential*/*secret*/id_*/*.pem) are refused before any read.
#   * FIFOs/devices/sockets are never hashed (no hang); only regular
#     files and directories are digest sources.
#   * Newlines/tabs/CRs in paths are escaped in TSV fields so one record
#     stays on one physical line; --json emits one parseable object per
#     target with the exact path.
#
# Exit codes: 0 evaluated (NOT-SAFE is a verdict, not an error);
#             1 selftest failure; 2 usage.
set -uo pipefail
export LC_ALL=C

unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE 2>/dev/null || true

SELF="${BASH_SOURCE[0]}"
SELF_DIR="$(cd -- "$(dirname -- "$SELF")" && pwd -P)"
SELF="$(cd -- "$SELF_DIR" && pwd -P)/$(basename -- "$SELF")"
REPO_ROOT="$(cd -- "$SELF_DIR/.." && pwd -P)"
DEFAULT_LEDGER="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"

SELFTEST=0
JSON=0
CLI_REQUESTED=0
LEDGER_ARG=""
STALE_DAYS=1
TARGETS=()

usage() { # $1 = exit code
  printf 'usage: %s [--selftest] [--json] [--cli] [--fallback] [--stale-days N] [--ledger FILE] <path>...\n' \
    "$(basename -- "$SELF")" >&2
  exit "$1"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --selftest) SELFTEST=1; shift ;;
    --json) JSON=1; shift ;;
    --cli) CLI_REQUESTED=1; shift ;;
    --fallback|--auto) shift ;;          # fallback is the only mode; flags kept for the contract
    --stale-days) [ "$#" -ge 2 ] && shift 2 || shift ;;
    --ledger) [ "$#" -ge 2 ] && { LEDGER_ARG="$2"; shift 2; } || shift ;;
    --) shift; while [ "$#" -gt 0 ]; do TARGETS+=("$1"); shift; done ;;
    -h|--help) usage 0 ;;
    -*) usage 2 ;;
    *) TARGETS+=("$1"); shift ;;
  esac
done

if [ "$SELFTEST" = 1 ]; then
  :
elif [ "${#TARGETS[@]}" -eq 0 ]; then
  usage 2
fi

if [ "$CLI_REQUESTED" = 1 ]; then
  printf 'cli=unavailable(degraded: sha256sum fallback; official CLI shim unregistered on this host)\n' >&2
fi

# ---------------------------------------------------------------- helpers --

json_escape() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

# Escape a value for a TAB-separated field: one record = one physical line.
tsv_field() {
  local s=$1
  s=${s//$'\t'/\\t}
  s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

canon() { readlink -m -- "$1" 2>/dev/null || printf '%s' "$1"; }

file_sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

dir_digest() { # deterministic manifest digest; .git pruned (matches r2)
  ( cd "$1" 2>/dev/null && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
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

# Ledger resolution: --ledger flag > SOUJI_LEDGER env > repo default.
resolve_ledger() {
  if [ -n "$LEDGER_ARG" ]; then printf '%s' "$LEDGER_ARG"
  elif [ -n "${SOUJI_LEDGER:-}" ]; then printf '%s' "$SOUJI_LEDGER"
  else printf '%s' "$DEFAULT_LEDGER"
  fi
}

R_CLASS=NOT-SAFE R_RECEIPT=none R_REASON=none R_EVIDENCE=no-receipt

emit_result() { # $1 = raw target path
  local raw=$1 tfield efield
  tfield="$(tsv_field "$raw")"
  efield="$(tsv_field "$R_EVIDENCE")"
  if [ "$JSON" = 1 ]; then
    if [ "$R_CLASS" = SAFE ]; then
      printf '{"path":"%s","verdict":"SAFE","verified":"VERIFIED(moved-to-obsidian)","receipt":"%s","reason":"%s","evidence":"%s"}\n' \
        "$(json_escape "$raw")" "$R_RECEIPT" "$R_RECEIPT" "$(json_escape "$R_EVIDENCE")"
    else
      printf '{"path":"%s","verdict":"NOT-SAFE","verified":"NOT-VERIFIED(%s)","receipt":"none","reason":"%s","evidence":"%s"}\n' \
        "$(json_escape "$raw")" "$R_REASON" "$R_REASON" "$(json_escape "$R_EVIDENCE")"
    fi
    return 0
  fi
  printf 'VERDICT\t%s\t%s\t%s\t%s\n' "$tfield" "$R_CLASS" "$R_RECEIPT" "$efield"
  # Line 2: the r4 single-token verdict. The evidence tail keeps the
  # fixture `contains` tokens (mismatch/absent/…) resolvable on this line
  # too, while the parenthesized token stays exact (source-hash, …).
  if [ "$R_CLASS" = SAFE ]; then
    printf 'VERIFIED(moved-to-obsidian)\t%s\n' "$efield"
  else
    printf 'NOT-VERIFIED(%s)\t%s\n' "$R_REASON" "$efield"
  fi
}

# Split one ledger line into its exact fields (empty fields preserved).
# Echoes NUL-separated fields; callers use mapfile -d ''.
split_ledger_line() {
  printf '%s' "$1" | awk -F'\t' '{ for (i = 1; i <= NF; i++) printf "%s%c", $i, 0 }'
}

# -------------------------------------------------------------- evaluate ---
# Evaluates one target. Sets R_CLASS/R_RECEIPT/R_REASON/R_EVIDENCE.

eval_target() {
  local raw=$1 target
  R_CLASS=NOT-SAFE; R_RECEIPT=none; R_REASON=none; R_EVIDENCE=no-receipt
  target="$(canon "$raw")"

  if is_secret_shaped "$raw"; then
    R_RECEIPT=secrets-refusal
    R_REASON=secrets-refusal
    R_EVIDENCE="obsidian=secrets-refusal secret-shaped path component"
    return 0
  fi

  local ledger ledger_resolved
  ledger="$(resolve_ledger)"
  ledger_resolved="$(readlink -f -- "$ledger" 2>/dev/null || printf '%s' "$ledger")"

  if [ -z "$ledger" ] || [ ! -f "$ledger" ] || [ ! -r "$ledger" ]; then
    R_REASON=no-ledger
    R_EVIDENCE="obsidian=no-ledger ledger=$ledger_resolved"
    return 0
  fi

  local line sp ss vp vs first_reason="" first_evidence="" saw_row=0
  local csp cvp ssh vsh
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in source_path$'\t'*) continue ;; esac
    [ -n "$line" ] || continue
    local -a F=()
    mapfile -d '' -t F < <(split_ledger_line "$line")
    sp="${F[0]:-}"; ss="${F[1]:-}"; vp="${F[2]:-}"; vs="${F[3]:-}"
    [ -n "$sp" ] || continue
    # Path match: literal, or canonical form (dotdot / symlink spelling).
    # A row still matches when the target is absent (V5 source-absent) —
    # canonicalization of a missing path is pure string work.
    if [ "$sp" = "$raw" ] || [ "$sp" = "$target" ]; then
      :
    else
      csp="$(canon "$sp")"
      [ "$csp" = "$target" ] || continue
    fi
    saw_row=1

    if [ -z "$ss" ] || [ -z "$vs" ]; then
      [ -n "$first_reason" ] || { first_reason=row-incomplete; first_evidence="obsidian=row-incomplete source=$sp"; }
      continue
    fi

    csp="$(canon "$sp")"; cvp="$(canon "$vp")"

    # Receipt-safety family: the vault copy must be a distinct, surviving copy.
    if [ "$csp" = "$cvp" ]; then
      [ -n "$first_reason" ] || { first_reason=self-move; first_evidence="obsidian=self-move source=$sp vault=$vp"; }
      continue
    fi
    if [ -d "$csp" ] && [ "$cvp" != "$csp" ] && [ "${cvp#"$csp"/}" != "$cvp" ]; then
      [ -n "$first_reason" ] || { first_reason=nested-copy; first_evidence="obsidian=nested-copy source=$sp vault=$vp"; }
      continue
    fi
    if [ -e "$csp" ] && [ -e "$cvp" ] && [ "$csp" -ef "$cvp" ]; then
      [ -n "$first_reason" ] || { first_reason=self-move; first_evidence="obsidian=self-move(alias) source=$sp vault=$vp"; }
      continue
    fi

    # Source side. A row matches even when the source path is absent; the
    # verdict then names the missing side (V5: NOT-VERIFIED(source-absent)).
    if [ ! -e "$sp" ] && [ ! -L "$sp" ]; then
      [ -n "$first_reason" ] || { first_reason=source-absent; first_evidence="obsidian=source-absent source-unreachable source=$sp"; }
      continue
    fi
    if [ -f "$sp" ]; then
      ssh="$(file_sha "$sp")"
    elif [ -d "$sp" ]; then
      ssh="$(dir_digest "$sp")"
    else
      [ -n "$first_reason" ] || { first_reason=source-unreachable; first_evidence="obsidian=source-unreachable source=$sp"; }
      continue
    fi
    if [ "$ssh" != "$ss" ]; then
      [ -n "$first_reason" ] || { first_reason=source-hash; first_evidence="obsidian=source-sha-mismatch source-hash live=$ssh row=$ss source=$sp"; }
      continue
    fi

    # Vault side.
    if [ ! -e "$vp" ] && [ ! -L "$vp" ]; then
      [ -n "$first_reason" ] || { first_reason=vault-absent; first_evidence="obsidian=vault-absent vault-unreachable vault=$vp"; }
      continue
    fi
    if [ -f "$vp" ]; then
      vsh="$(file_sha "$vp")"
    elif [ -d "$vp" ]; then
      vsh="$(dir_digest "$vp")"
    else
      [ -n "$first_reason" ] || { first_reason=vault-unreachable; first_evidence="obsidian=vault-unreachable vault=$vp"; }
      continue
    fi
    if [ "$vsh" != "$vs" ]; then
      [ -n "$first_reason" ] || { first_reason=vault-hash-mismatch; first_evidence="obsidian=vault-sha-mismatch vault-hash-mismatch live=$vsh row=$vs vault=$vp"; }
      continue
    fi

    # All four conjuncts hold and the copy is distinct: the receipt stands.
    R_CLASS=SAFE; R_RECEIPT=moved-to-obsidian; R_REASON=moved-to-obsidian
    R_EVIDENCE="ledger-row ledger=$ledger_resolved vault=$vp source-sha256=${ss:0:12} vault-sha256=${vs:0:12}"
    return 0
  done < "$ledger"

  if [ "$saw_row" = 1 ]; then
    R_REASON="$first_reason"; R_EVIDENCE="$first_evidence"
  elif [ ! -e "$target" ] && [ ! -L "$target" ]; then
    # r2 convention: a missing target's receipt field names the condition
    # (vrun-33 C3 asserts ^unreachable$ in field 4).
    R_RECEIPT=unreachable
    R_REASON=unreachable
    R_EVIDENCE="obsidian=unreachable missing path target=$target"
  else
    R_REASON=no-row
    R_EVIDENCE="obsidian=no-matching-ledger-row ledger=$ledger_resolved"
  fi
  return 0
}

# --------------------------------------------------------------- selftest --

st_pass=0 st_fail=0

st_note() { printf '%s\n' "$*"; }

st_case() { # id want-class want-token target
  local id=$1 wc=$2 wt=$3 tgt=$4 out rc
  out="$(bash "$SELF" --ledger "$ST_LEDGER" "$tgt" 2>&1)"; rc=$?
  local l1 l2 vc l2t
  l1="$(printf '%s\n' "$out" | grep -E '^VERDICT' | head -1)"
  l2="$(printf '%s\n' "$out" | grep -E '^(VERIFIED|NOT-VERIFIED)' | head -1)"
  vc="$(printf '%s' "$l1" | awk -F'\t' '{print $3}')"
  l2t="${l2%%$'\t'*}"
  if [ "$rc" -ne 0 ]; then
    st_fail=$((st_fail+1)); st_note "FAIL $id: exit=$rc out=$(printf '%s' "$out" | head -c 200)"; return 0
  fi
  if [ "$vc" != "$wc" ] || [ "$l2t" != "$wt" ]; then
    st_fail=$((st_fail+1)); st_note "FAIL $id: got '$vc'/'$l2t' want '$wc'/'$wt'"
    return 0
  fi
  st_pass=$((st_pass+1)); st_note "PASS $id $wc $l2t"
}

st_rc() { # id want-exit -- args...
  local id=$1 want=$2; shift 2
  local rc=0
  bash "$SELF" "$@" >/dev/null 2>&1 || rc=$?
  if [ "$rc" = "$want" ]; then st_pass=$((st_pass+1)); st_note "PASS $id exit=$rc"
  else st_fail=$((st_fail+1)); st_note "FAIL $id exit=$rc want=$want"; fi
}

st_selftest() {
  local tmp
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/souji-vault-s23.XXXXXX")"
  ST_LEDGER="$tmp/ledger.tsv"
  local src="$tmp/src" vault="$tmp/vault"
  mkdir -p "$src" "$vault" "$tmp/dirsrc" "$tmp/dirvault" "$tmp/dirsrc/inner"

  printf 'note-a payload\n' > "$src/a.md";   cp "$src/a.md" "$vault/a.md"
  printf 'note-b payload\n' > "$src/b.md";   cp "$src/b.md" "$vault/b.md"
  printf 'note-c payload\n' > "$src/c.md";   cp "$src/c.md" "$vault/c.md"
  printf 'note-d payload\n' > "$src/d.md"
  printf 'note-e payload\n' > "$vault/e.md"
  printf 'note-f payload\n' > "$src/f.md";   cp "$src/f.md" "$vault/f.md"
  printf 'note-g payload\n' > "$src/g.md";   cp "$src/g.md" "$vault/g.md"
  printf 'note-h payload\n' > "$src/h.md";   cp "$src/h.md" "$vault/h.md"
  : > "$src/empty.md";                       cp "$src/empty.md" "$vault/empty.md"
  printf 'one\n' > "$tmp/dirsrc/one.txt";    printf 'two\n' > "$tmp/dirsrc/two.txt"
  cp -r "$tmp/dirsrc/." "$tmp/dirvault/"
  mkdir -p "$tmp/nested-src/inner";          printf 'alpha\n' > "$tmp/nested-src/a.txt"
  printf 'crlf payload\n' > "$src/crlf.md";  cp "$src/crlf.md" "$vault/crlf.md"
  ln -s "$src/g.md" "$vault/g-link.md"
  mkfifo "$vault/fifo.md" 2>/dev/null || true

  local sha_a sha_b sha_c sha_d sha_e sha_g sha_h sha_empty dig digv dig_n sha_crlf
  sha_a=$(file_sha "$src/a.md"); sha_b=$(file_sha "$src/b.md")
  sha_c=$(file_sha "$src/c.md"); sha_d=$(file_sha "$src/d.md")
  sha_e=$(file_sha "$vault/e.md"); sha_g=$(file_sha "$src/g.md")
  sha_h=$(file_sha "$src/h.md"); sha_empty=$(file_sha "$src/empty.md")
  dig=$(dir_digest "$tmp/dirsrc"); digv=$(dir_digest "$tmp/dirvault")
  dig_n=$(dir_digest "$tmp/nested-src")
  sha_crlf=$(file_sha "$src/crlf.md")

  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18\tmatch\n' "$src/a.md" "$sha_a" "$vault/a.md" "$sha_a"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tvault-edit\n' "$src/b.md" "$sha_b" "$vault/b.md" "$sha_b"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tsource-edit\n' "$src/c.md" "$sha_c" "$vault/c.md" "$sha_c"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tvault-absent\n' "$src/d.md" "$sha_d" "$vault/missing.md" "$sha_d"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tsource-absent\n' "$src/missing.md" "$sha_e" "$vault/e.md" "$sha_e"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tself-move\n' "$src/f.md" "$(file_sha "$src/f.md")" "$src/f.md" "$(file_sha "$src/f.md")"
    printf '%s\t%s\t%s\t%s\t2026-10-18\talias\n' "$src/g.md" "$sha_g" "$vault/g-link.md" "$sha_g"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tnested\n' "$tmp/nested-src" "$dig_n" "$tmp/nested-src/inner" "$dig_n"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tempty-file\n' "$src/empty.md" "$sha_empty" "$vault/empty.md" "$sha_empty"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tdir-pair\n' "$tmp/dirsrc" "$dig" "$tmp/dirvault" "$digv"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tfifo\n' "$src/h.md" "$sha_h" "$vault/fifo.md" "$sha_h"
    printf '%s\t%s\t%s\t%s\t2026-10-18\tcrlf-row\r\n' "$src/crlf.md" "$sha_crlf" "$vault/crlf.md" "$sha_crlf"
  } > "$ST_LEDGER"
  printf 'EDIT AFTER ROW\n' >> "$vault/b.md"
  printf 'EDIT AFTER ROW\n' >> "$src/c.md"

  st_case S1 SAFE 'VERIFIED(moved-to-obsidian)' "$src/a.md"
  st_case S2 NOT-SAFE 'NOT-VERIFIED(vault-hash-mismatch)' "$src/b.md"
  st_case S3 NOT-SAFE 'NOT-VERIFIED(source-hash)' "$src/c.md"
  st_case S4 NOT-SAFE 'NOT-VERIFIED(vault-absent)' "$src/d.md"
  st_case S5 NOT-SAFE 'NOT-VERIFIED(source-absent)' "$src/missing.md"
  st_case S6 NOT-SAFE 'NOT-VERIFIED(self-move)' "$src/f.md"
  st_case S7 NOT-SAFE 'NOT-VERIFIED(self-move)' "$src/g.md"
  st_case S8 NOT-SAFE 'NOT-VERIFIED(nested-copy)' "$tmp/nested-src"
  st_case S9 SAFE 'VERIFIED(moved-to-obsidian)' "$src/empty.md"
  st_case S10 SAFE 'VERIFIED(moved-to-obsidian)' "$tmp/dirsrc"
  st_case S11 NOT-SAFE 'NOT-VERIFIED(vault-unreachable)' "$src/h.md"
  st_case S12 SAFE 'VERIFIED(moved-to-obsidian)' "$src/crlf.md"
  st_case S13 NOT-SAFE 'NOT-VERIFIED(self-move)' "$vault/g-link.md"

  # header-only ledger -> no row
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$tmp/empty.tsv"
  local out13
  out13="$(bash "$SELF" --ledger "$tmp/empty.tsv" "$src/a.md" 2>&1)"
  if printf '%s' "$out13" | grep -q '^NOT-VERIFIED(no-row)'; then
    st_pass=$((st_pass+1)); st_note "PASS S14 no-row"
  else
    st_fail=$((st_fail+1)); st_note "FAIL S14 no-row: $(printf '%s' "$out13" | head -1)"
  fi

  # missing ledger -> no-ledger
  local out15
  out15="$(bash "$SELF" --ledger "$tmp/nope.tsv" "$src/a.md" 2>&1)"
  if printf '%s' "$out15" | grep -q 'no-ledger'; then
    st_pass=$((st_pass+1)); st_note "PASS S15 no-ledger"
  else
    st_fail=$((st_fail+1)); st_note "FAIL S15 no-ledger"
  fi

  # secrets refusal
  local out16
  printf 'x\n' > "$tmp/creds.pem"
  out16="$(bash "$SELF" --ledger "$ST_LEDGER" "$tmp/creds.pem" 2>&1)"
  if printf '%s' "$out16" | grep -q '^NOT-VERIFIED(secrets-refusal)'; then
    st_pass=$((st_pass+1)); st_note "PASS S16 secrets-refusal"
  else
    st_fail=$((st_fail+1)); st_note "FAIL S16 secrets-refusal"
  fi

  # missing target -> unreachable
  st_case S17 NOT-SAFE 'NOT-VERIFIED(unreachable)' "$tmp/does-not-exist.md"

  # batch: 2 targets -> 4 lines, both targets addressed
  local bout blines
  bout="$(bash "$SELF" --ledger "$ST_LEDGER" "$src/a.md" "$src/b.md" 2>&1)"
  blines=$(printf '%s\n' "$bout" | grep -c . || true)
  if [ "$blines" = 4 ] && printf '%s' "$bout" | grep -q '^VERIFIED(moved-to-obsidian)' \
     && printf '%s' "$bout" | grep -q '^NOT-VERIFIED(vault-hash-mismatch)'; then
    st_pass=$((st_pass+1)); st_note "PASS S18 batch lines=4"
  else
    st_fail=$((st_fail+1)); st_note "FAIL S18 batch lines=$blines"
  fi

  # json mode: one parseable object with the exact path
  local jout
  jout="$(bash "$SELF" --ledger "$ST_LEDGER" --json "$src/a.md" 2>&1)"
  if printf '%s' "$jout" | grep -q "\"path\":\"$src/a.md\"" && printf '%s' "$jout" | grep -q '"verdict":"SAFE"'; then
    st_pass=$((st_pass+1)); st_note "PASS S19 json"
  else
    st_fail=$((st_fail+1)); st_note "FAIL S19 json: $(printf '%s' "$jout" | head -c 160)"
  fi

  # determinism
  local d1 d2
  d1="$(bash "$SELF" --ledger "$ST_LEDGER" "$src/a.md" 2>&1)"
  d2="$(bash "$SELF" --ledger "$ST_LEDGER" "$src/a.md" 2>&1)"
  if [ "$d1" = "$d2" ]; then st_pass=$((st_pass+1)); st_note "PASS S20 determinism"
  else st_fail=$((st_fail+1)); st_note "FAIL S20 determinism"; fi

  # newline path: one physical record per target line
  local nlfile nout nl_ctl ctlout
  nlfile="$tmp/nl"$'\n'"name.md"
  printf 'x\n' > "$nlfile"
  nout="$(bash "$SELF" --ledger "$tmp/empty.tsv" "$nlfile" 2>&1)"
  ctlout="$(bash "$SELF" --ledger "$tmp/empty.tsv" "$src/a.md" 2>&1)"
  if [ "$(printf '%s\n' "$nout" | grep -c .)" = "$(printf '%s\n' "$ctlout" | grep -c .)" ]; then
    st_pass=$((st_pass+1)); st_note "PASS S21 newline-record"
  else
    st_fail=$((st_fail+1)); st_note "FAIL S21 newline-record"
  fi

  # cli flag: accepted, rc 0, cli state named
  local cout crc=0
  cout="$(bash "$SELF" --cli --ledger "$ST_LEDGER" "$src/a.md" 2>&1)" || crc=$?
  if [ "$crc" = 0 ] && printf '%s' "$cout" | grep -qi 'cli'; then
    st_pass=$((st_pass+1)); st_note "PASS S22 cli-degrade"
  else
    st_fail=$((st_fail+1)); st_note "FAIL S22 cli-degrade rc=$crc"
  fi

  # fallback + stale-days accepted
  st_rc S23 0 --fallback --stale-days 1 --ledger "$ST_LEDGER" "$src/a.md"
  st_rc S24 2
  st_rc S25 2 --bogus-flag-xyz

  rm -rf -- "$tmp"
  printf '%s\n' "selftest: pass=$st_pass fail=$st_fail"
  [ "$st_fail" -eq 0 ]
}

if [ "$SELFTEST" = 1 ]; then
  st_selftest
  exit $?
fi

for t in "${TARGETS[@]}"; do
  eval_target "$t"
  emit_result "$t"
done
exit 0
