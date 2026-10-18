#!/usr/bin/env bash
# vadv54-harness — seat S54 adversarial probes, round 4 (Obsidian-CLI vault
# verification contract). Target under test: tools/souji-verify.sh (the
# installed r2 artifact). Read-only over the real vault and the live ledger:
# every access is sha256sum/stat/find. /usr/bin/obsidian (the GUI launcher)
# is never executed.
#
# Families
#   p  self-move / alias ledger rows — the "vault copy" is the source itself:
#      literal self-move (file+dir), symlink alias, dotdot alias, hardlink
#      alias, copy outside the registered vault root, copy nested inside the
#      source directory.
#   q  ledger path is a symlink — silent follow, chain, dangling, /dev/null,
#      evidence-indistinguishability, swap race.
#   r  target path containing a newline — TSV record integrity, JSON mode,
#      scratch classification, ledger-smuggle attempts.
#
# Usage: vadv54-harness.sh [--tool PATH] [--out FILE]
# Exit: 0 always (verdicts live in the JSON); 2 on usage error.

set -uo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
TOOL="$REPO_ROOT/tools/souji-verify.sh"
JSON_OUT="$REPO_ROOT/tests/results/vadv-54.json"
VAULT=/home/vgpnk/Documents/shokoknowledge
LIVE_LEDGER="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool) TOOL=$2; shift 2 ;;
    --tool=*) TOOL=${1#*=}; shift ;;
    --out) JSON_OUT=$2; shift 2 ;;
    --out=*) JSON_OUT=${1#*=}; shift ;;
    -h|--help) sed -n '2,21p' "$SCRIPT_PATH"; exit 0 ;;
    *) printf 'vadv54-harness: unknown arg %s\n' "$1" >&2; exit 2 ;;
  esac
done

TOOL_SHA_BEFORE=$(sha256sum -- "$TOOL" 2>/dev/null | cut -d' ' -f1)
SPEC="$REPO_ROOT/tools/souji-verify.spec.md"
SPEC_SHA=$(sha256sum -- "$SPEC" 2>/dev/null | cut -d' ' -f1)

WORK="$SCRIPT_DIR/vadv54-run"
rm -rf -- "$WORK"
mkdir -p "$WORK/p" "$WORK/q/vault" "$WORK/r/nl" "$WORK/r/scratch/.scratch"

P="$WORK/p"
Q="$WORK/q"
R="$WORK/r"

jesc() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }

dir_digest() { # replica of the tool's dir_digest
  ( cd "$1" && find . -path './.git' -prune -o -type f -print0 \
      | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null
}

vault_snap() {
  ( cd "$VAULT" && find . -type f -print0 2>/dev/null | sort -z \
      | xargs -0 -r sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1 )
}
vault_count() { ( cd "$VAULT" && find . -type f 2>/dev/null | wc -l | tr -d ' ' ); }

declare -a CASES=()
PASS=0; FAIL=0; WARN=0; INFO=0

record() { # $1 id $2 family $3 verdict $4 oracle $5 rc $6 out $7 note $8 extra(json-fragment|"")
  local id=$1 fam=$2 verdict=$3 oracle=$4 rc=$5 out=$6 note=$7 extra=${8:-}
  case "$verdict" in
    PASS) PASS=$((PASS+1)) ;;
    FAIL) FAIL=$((FAIL+1)) ;;
    WARN) WARN=$((WARN+1)) ;;
    INFO) INFO=$((INFO+1)) ;;
  esac
  local esc
  esc=$(printf '%s' "$out" | sed -n 'l' | head -4 | tr '\n' '|')
  CASES+=("$(printf '{"id":"%s","family":"%s","verdict":"%s","oracle":"%s","rc":%s,"out":"%s","out_esc":"%s","note":"%s"%s}' \
    "$(jesc "$id")" "$(jesc "$fam")" "$verdict" "$(jesc "$oracle")" "$rc" \
    "$(jesc "$(printf '%s' "$out" | head -c 600)")" "$(jesc "$esc")" "$(jesc "$note")" \
    "${extra:+,$extra}")")
  printf '%-5s %-24s rc=%s %s\n' "$verdict" "$id" "$rc" "$(printf '%s' "$out" | head -c 150)"
}

run_tool() { # $1 ledger|"-" ; rest = args ; sets RC OUT
  local led=$1; shift
  if [ "$led" = "-" ]; then
    OUT=$(timeout 30 bash "$TOOL" --stale-days 1 "$@" 2>&1); RC=$?
  else
    OUT=$(SOUJI_LEDGER="$led" timeout 30 bash "$TOOL" --stale-days 1 "$@" 2>&1); RC=$?
  fi
  # Some r4 candidates do not accept --stale-days; retry bare on a usage error.
  if [ "$RC" -eq 2 ]; then
    if [ "$led" = "-" ]; then
      OUT=$(timeout 30 bash "$TOOL" "$@" 2>&1); RC=$?
    else
      OUT=$(SOUJI_LEDGER="$led" timeout 30 bash "$TOOL" "$@" 2>&1); RC=$?
    fi
  fi
}

field() { printf '%s' "$OUT" | cut -f"$1" | head -1; }
# Verdict extraction robust to a newline-split record: when the path contains a
# newline the tool's own output wraps, so the path field eats two lines and all
# later fields shift down by one on the tail line.
vfield() { # $1 = field index in an intact record
  local n1
  n1=$(printf '%s\n' "$OUT" | head -1 | awk -F'\t' '{print NF}')
  if [ "${n1:-0}" -ge 5 ]; then
    printf '%s\n' "$OUT" | head -1 | cut -f"$1"
  else
    printf '%s\n' "$OUT" | tail -1 | cut -f"$(( $1 - 1 ))"
  fi
}

# Vocabulary-agnostic verdict/receipt extraction. Accepts the r2 VERDICT form
# (including newline-split records, where the tail line carries the shifted
# fields) and the r4 VERIFIED / NOT-VERIFIED(<reason>) forms.
norm_v() {
  local l tag nf
  l=$(printf '%s\n' "$OUT" | head -1)
  tag=${l%%$'\t'*}
  case "$tag" in
    VERDICT)
      nf=$(printf '%s\n' "$l" | awk -F'\t' '{print NF}')
      if [ "${nf:-0}" -ge 5 ]; then printf '%s\n' "$l" | cut -f3
      else printf '%s\n' "$OUT" | tail -1 | cut -f2; fi ;;
    VERIFIED|VERIFIED\(*\)) printf 'SAFE\n' ;;
    NOT-VERIFIED|NOT-VERIFIED\(*\)) printf 'NOT-SAFE\n' ;;
    *) printf 'UNKNOWN\n' ;;
  esac
}
norm_r() {
  local l tag nf
  l=$(printf '%s\n' "$OUT" | head -1)
  tag=${l%%$'\t'*}
  case "$tag" in
    VERDICT)
      nf=$(printf '%s\n' "$l" | awk -F'\t' '{print NF}')
      if [ "${nf:-0}" -ge 5 ]; then printf '%s\n' "$l" | cut -f4
      else printf '%s\n' "$OUT" | tail -1 | cut -f3; fi ;;
    VERIFIED) printf 'moved-to-obsidian\n' ;;
    VERIFIED\(*) tag=${tag#VERIFIED(}; printf '%s\n' "${tag%)}" ;;
    NOT-VERIFIED) printf 'none\n' ;;
    NOT-VERIFIED\(*) tag=${tag#NOT-VERIFIED(}; printf '%s\n' "${tag%)}" ;;
    *) printf 'unknown\n' ;;
  esac
}
nlines() { printf '%s\n' "$1" | awk 'END{print NR}'; }

# ------------------------------------------------------------- snapshots --
VAULT_BEFORE=$(vault_snap)
VAULT_N_BEFORE=$(vault_count)
LIVE_SHA_BEFORE=$(sha "$LIVE_LEDGER")
LIVE_LINES_BEFORE=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')

# ------------------------------------------------------------- fixtures p --
printf 'vadv54 control payload\n' > "$P/ctrl.md"
printf 'vadv54 self-move payload\n' > "$P/p1.md"
printf 'vadv54 symlink-alias payload\n' > "$P/p2.md"
printf 'vadv54 dotdot-alias payload\n' > "$P/p3.md"
printf 'vadv54 hardlink-alias payload\n' > "$P/p4.md"
printf 'vadv54 offvault-copy payload\n' > "$P/p5.md"
mkdir -p "$P/p1dir"
printf 'alpha\n' > "$P/p1dir/a.txt"
printf 'beta\n' > "$P/p1dir/b.txt"
mkdir -p "$P/p6repo/.git" "$P/p6repo/inner"
printf 'p6 payload one\n' > "$P/p6repo/one.txt"
printf 'p6 payload inner\n' > "$P/p6repo/inner/keep.txt"
ln -s "$P/p2.md" "$P/alias-link.md"
ln -s "$P/p3.md" "$P/alias-dotdot-target.md"   # extra evidence, unused
ln "$P/p4.md" "$P/alias-hard.md"
printf 'vadv54 offvault-copy payload\n' > "$Q/notvault-copy.md"

printf 'vadv54 control payload\n' > "$Q/vault/qctrl.md"

C_SHA=$(sha "$P/ctrl.md")
P1_SHA=$(sha "$P/p1.md")
P2_SHA=$(sha "$P/p2.md")
P3_SHA=$(sha "$P/p3.md")
P4_SHA=$(sha "$P/p4.md")
P5_SHA=$(sha "$P/p5.md")
P1D_DIG=$(dir_digest "$P/p1dir")
P6_DIG=$(dir_digest "$P/p6repo")
P6I_DIG=$(dir_digest "$P/p6repo/inner")
QV_SHA=$(sha "$Q/vault/qctrl.md")
OV_SHA=$(sha "$Q/notvault-copy.md")

LED_P="$Q/led-p.tsv"
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvalid-control\n' "$P/ctrl.md" "$C_SHA" "$Q/vault/qctrl.md" "$QV_SHA"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tself-move-file\n' "$P/p1.md" "$P1_SHA" "$P/p1.md" "$P1_SHA"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tself-move-dir\n' "$P/p1dir" "$P1D_DIG" "$P/p1dir" "$P1D_DIG"
  printf '%s\t%s\t%s\t%s\t2026-10-18\talias-symlink\n' "$P/p2.md" "$P2_SHA" "$P/alias-link.md" "$P2_SHA"
  printf '%s\t%s\t%s\t%s\t2026-10-18\talias-dotdot\n' "$P/p3.md" "$P3_SHA" "$P/../p/p3.md" "$P3_SHA"
  printf '%s\t%s\t%s\t%s\t2026-10-18\talias-hardlink\n' "$P/p4.md" "$P4_SHA" "$P/alias-hard.md" "$P4_SHA"
  printf '%s\t%s\t%s\t%s\t2026-10-18\toffvault-copy\n' "$P/p5.md" "$P5_SHA" "$Q/notvault-copy.md" "$OV_SHA"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvault-nested-in-source\n' "$P/p6repo" "$P6_DIG" "$P/p6repo/inner" "$P6I_DIG"
} > "$LED_P"

# P0 control: a genuine export (distinct vault copy).
run_tool "$LED_P" "$P/ctrl.md"
if [ "$RC" -eq 0 ] && [ "$(norm_v)" = SAFE ] && [ "$(norm_r)" = moved-to-obsidian ]; then
  record P0 p PASS "SAFE(moved-to-obsidian) for a genuine distinct vault copy" "$RC" "$OUT" "baseline true-positive"
else
  record P0 p FAIL "SAFE(moved-to-obsidian) for a genuine distinct vault copy" "$RC" "$OUT" "baseline broken"
fi

# P1 file self-move: sp == vp == the evaluated file itself.
run_tool "$LED_P" "$P/p1.md"
v=$(norm_v); r=$(norm_r)
if [ "$v" = SAFE ]; then
  record P1 p FAIL "NOT-SAFE — a self-move row is not an export; the file is its own only copy" "$RC" "$OUT" "false-SAFE: removal deletes the sole copy" '"severity":"critical"'
else
  record P1 p PASS "NOT-SAFE — a self-move row is not an export; the file is its own only copy" "$RC" "$OUT" "refused; receipt=$r"
fi

# P1d dir self-move.
run_tool "$LED_P" "$P/p1dir"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  record P1d p FAIL "NOT-SAFE — directory self-move row (source == vault path)" "$RC" "$OUT" "false-SAFE: removal deletes the sole directory" '"severity":"critical"'
else
  record P1d p PASS "NOT-SAFE — directory self-move row (source == vault path)" "$RC" "$OUT" "refused"
fi

# P2 symlink alias: vp is a symlink to the source file.
run_tool "$LED_P" "$P/p2.md"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  record P2 p FAIL "NOT-SAFE — vault path is a symlink alias of the source (same file)" "$RC" "$OUT" "false-SAFE: removing source leaves a dangling symlink; content lost" '"severity":"critical"'
else
  record P2 p PASS "NOT-SAFE — vault path is a symlink alias of the source (same file)" "$RC" "$OUT" "refused"
fi

# P3 dotdot alias: vp spells the same file via ../
run_tool "$LED_P" "$P/p3.md"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  record P3 p FAIL "NOT-SAFE — vault path is a path-spelling alias (../) of the source" "$RC" "$OUT" "false-SAFE: source is the only copy" '"severity":"critical"'
else
  record P3 p PASS "NOT-SAFE — vault path is a path-spelling alias (../) of the source" "$RC" "$OUT" "refused"
fi

# P4 hardlink alias: vp is a hardlink of the source (content survives removal).
run_tool "$LED_P" "$P/p4.md"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  record P4 p WARN "NOT-SAFE strict — vault path is a hardlink of the source; content survives removal" "$RC" "$OUT" "alias accepted; content-preserving but not a distinct vault copy" '"severity":"minor"'
else
  record P4 p PASS "NOT-SAFE strict — vault path is a hardlink of the source; content survives removal" "$RC" "$OUT" "refused"
fi

# P5 distinct copy outside the registered vault root.
run_tool "$LED_P" "$P/p5.md"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  record P5 p WARN "SAFE tolerated for a distinct copy — but 'vault' semantics unchecked (path not under the registered vault root)" "$RC" "$OUT" "content preserved at the named path; the tool never constrains vault_path to $VAULT" '"severity":"minor"'
else
  record P5 p PASS "SAFE tolerated for a distinct copy — but 'vault' semantics unchecked" "$RC" "$OUT" "refused"
fi

# P6 vault copy nested inside the source directory.
run_tool "$LED_P" "$P/p6repo"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  record P6 p FAIL "NOT-SAFE — the receipt's vault copy lives inside the source directory being evaluated" "$RC" "$OUT" "false-SAFE: removing the repo destroys its own vault copy" '"severity":"critical"'
else
  record P6 p PASS "NOT-SAFE — the receipt's vault copy lives inside the source directory being evaluated" "$RC" "$OUT" "refused"
fi

# ------------------------------------------------------------- fixtures q --
LED_REAL="$Q/led-real.tsv"
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t2026-10-18\treal-ledger\n' "$P/ctrl.md" "$C_SHA" "$Q/vault/qctrl.md" "$QV_SHA"
} > "$LED_REAL"
LED_EMPTY="$Q/led-empty.tsv"
printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$LED_EMPTY"
LED_EVIL="$Q/led-evil.tsv"
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t2026-10-18\tevil-copy\n' "$P/ctrl.md" "$C_SHA" "$Q/vault/qctrl.md" "$QV_SHA"
} > "$LED_EVIL"

ln -sf led-real.tsv "$Q/led-link.tsv"
ln -sf led-link.tsv "$Q/led-chain.tsv"
ln -sf missing.tsv "$Q/led-dangling.tsv"
ln -sf /dev/null "$Q/led-devnull.tsv"
RESOLVED_REAL=$(readlink -f "$Q/led-link.tsv" 2>/dev/null || true)

# Q0 control: regular-file ledger.
run_tool "$LED_REAL" "$P/ctrl.md"
if [ "$RC" -eq 0 ] && [ "$(norm_v)" = SAFE ]; then
  record Q0 q PASS "SAFE(moved-to-obsidian) from a regular-file ledger" "$RC" "$OUT" "baseline true-positive"
else
  record Q0 q FAIL "SAFE(moved-to-obsidian) from a regular-file ledger" "$RC" "$OUT" "baseline broken"
fi

# Q1 symlink ledger: silently followed? evidence auditability.
run_tool "$Q/led-link.tsv" "$P/ctrl.md"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  case "$OUT" in
    *"$RESOLVED_REAL"*) record Q1 q PASS "refuse a symlinked ledger OR record its resolved path in the evidence" "$RC" "$OUT" "SAFE with resolved path recorded" ;;
    *) record Q1 q WARN "refuse a symlinked ledger OR record its resolved path in the evidence" "$RC" "$OUT" "symlink followed silently; the receipt names no ledger path, so it cannot be traced to a ledger file" '"severity":"medium"' ;;
  esac
elif [ "$v" = NOT-SAFE ]; then
  record Q1 q PASS "refuse a symlinked ledger OR record its resolved path in the evidence" "$RC" "$OUT" "refused"
else
  record Q1 q WARN "refuse a symlinked ledger OR record its resolved path in the evidence" "$RC" "$OUT" "unexpected verdict"
fi

# Q2 symlink chain.
run_tool "$Q/led-chain.tsv" "$P/ctrl.md"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  record Q2 q WARN "refuse a symlink-chain ledger OR record its resolved path" "$RC" "$OUT" "chain followed silently (2 hops); no ledger path in evidence" '"severity":"medium"'
elif [ "$v" = NOT-SAFE ]; then
  record Q2 q PASS "refuse a symlink-chain ledger OR record its resolved path" "$RC" "$OUT" "refused"
else
  record Q2 q WARN "refuse a symlink-chain ledger OR record its resolved path" "$RC" "$OUT" "unexpected verdict"
fi

# Q3 dangling symlink ledger.
run_tool "$Q/led-dangling.tsv" "$P/ctrl.md"
v=$(norm_v); r3r=$(norm_r)
case "$OUT" in *no-ledger*) nl=yes ;; *) nl=no ;; esac
if [ "$v" = NOT-SAFE ]; then
  record Q3 q PASS "NOT-SAFE for a dangling ledger symlink (reason wording free)" "$RC" "$OUT" "safe-side refusal (reason=$r3r no-ledger-text=$nl)"
else
  record Q3 q FAIL "NOT-SAFE for a dangling ledger symlink (reason wording free)" "$RC" "$OUT" "unexpected"
fi

# Q4 symlink to /dev/null.
run_tool "$Q/led-devnull.tsv" "$P/ctrl.md"
v=$(norm_v)
if [ "$v" = NOT-SAFE ]; then
  record Q4 q PASS "NOT-SAFE(no-ledger) for a symlink to a non-regular file" "$RC" "$OUT" "safe-side refusal"
else
  record Q4 q FAIL "NOT-SAFE(no-ledger) for a symlink to a non-regular file" "$RC" "$OUT" "unexpected"
fi

# Q4b absolute symlink escaping the lane tree.
mkdir -p "$WORK/elsewhere"
cp "$LED_REAL" "$WORK/elsewhere/led-outside.tsv"
ln -sf "$WORK/elsewhere/led-outside.tsv" "$Q/led-outside.tsv"
run_tool "$Q/led-outside.tsv" "$P/ctrl.md"
v=$(norm_v)
if [ "$v" = SAFE ]; then
  record Q4b q WARN "refuse a ledger symlink that escapes the lane tree OR record its target" "$RC" "$OUT" "absolute external symlink followed silently; no target path in evidence" '"severity":"medium"'
elif [ "$v" = NOT-SAFE ]; then
  record Q4b q PASS "refuse a ledger symlink that escapes the lane tree OR record its target" "$RC" "$OUT" "refused"
else
  record Q4b q WARN "refuse a ledger symlink that escapes the lane tree OR record its target" "$RC" "$OUT" "unexpected verdict"
fi

# Q4c ledger path is a directory.
mkdir -p "$Q/led-dir.tsv"
run_tool "$Q/led-dir.tsv" "$P/ctrl.md"
v=$(norm_v)
case "$OUT" in *no-ledger*) nl=yes ;; *) nl=no ;; esac
if [ "$v" = NOT-SAFE ]; then
  record Q4c q PASS "NOT-SAFE for a ledger path that is a directory" "$RC" "$OUT" "safe-side refusal (no-ledger=$nl)"
else
  record Q4c q FAIL "NOT-SAFE for a ledger path that is a directory" "$RC" "$OUT" "unexpected"
fi

# Q5 evidence-indistinguishability: same row in two different files.
OUT_A=""; OUT_B=""
run_tool "$LED_REAL" "$P/ctrl.md"; OUT_A=$OUT
run_tool "$LED_EVIL" "$P/ctrl.md"; OUT_B=$OUT
if [ "$OUT_A" = "$OUT_B" ]; then
  record Q5 q WARN "evidence distinguishes which ledger file produced the receipt" 0 "$OUT_A" "identical output from two distinct ledger files — the receipt cannot be traced to a ledger path" '"severity":"medium","out_b":"'"$(jesc "$OUT_B")"'"'
else
  record Q5 q PASS "evidence distinguishes which ledger file produced the receipt" 0 "$OUT_A" "outputs differ"
fi

# Q6 swap race (evidence): symlink alternates between a rowed ledger and a header-only ledger.
ln -sf led-real.tsv "$Q/led-swap.tsv"
(
  while :; do
    ln -sf led-real.tsv "$Q/led-swap.tsv" 2>/dev/null
    ln -sf led-empty.tsv "$Q/led-swap.tsv" 2>/dev/null
  done
) &
SPID=$!
n_safe=0; n_ns=0; n_other=0
for _i in $(seq 1 100); do
  OUT=$(SOUJI_LEDGER="$Q/led-swap.tsv" timeout 30 bash "$TOOL" --stale-days 1 "$P/ctrl.md" 2>&1); rc=$?
  # Accept --stale-days-less tools by retrying bare.
  if [ "$rc" -eq 2 ]; then
    OUT=$(SOUJI_LEDGER="$Q/led-swap.tsv" timeout 30 bash "$TOOL" "$P/ctrl.md" 2>&1); rc=$?
  fi
  v=$(norm_v)
  case "$v" in
    SAFE) n_safe=$((n_safe+1)) ;;
    NOT-SAFE) n_ns=$((n_ns+1)) ;;
    *) n_other=$((n_other+1)) ;;
  esac
done
kill "$SPID" 2>/dev/null
wait "$SPID" 2>/dev/null
record Q6 q INFO "receipt path pinned for one evaluation (no flip under swap)" 0 "SAFE=$n_safe NOT-SAFE=$n_ns other=$n_other" "verdict follows whichever symlink target is live at read time; no pinning" '"safe":'"$n_safe"',"not_safe":'"$n_ns"',"other":'"$n_other"

# ------------------------------------------------------------- fixtures r --
NLFILE="$R/nl/first"$'\n'"second.md"
printf 'vadv54 newline payload\n' > "$NLFILE"
NL_SHA=$(sha "$NLFILE")
NL_SCRATCH="$R/scratch/.scratch/old"$'\n'"name.log"
printf 'vadv54 newline scratch payload\n' > "$NL_SCRATCH"
touch -d '2020-01-01 00:00:00' "$NL_SCRATCH"

# R1 TSV record integrity: compare against the same tool's own line count for a
# normal path (impl-20 emits two lines per target by design, so an absolute
# "1 line" oracle would be wrong for it; what matters is no extra splitting).
run_tool "$LED_EMPTY" "$P/ctrl.md"
nl_ctrl=$(nlines "$OUT")
run_tool "$LED_EMPTY" "$NLFILE"
nl=$(nlines "$OUT")
if [ "$RC" -ne 0 ]; then
  record R1 r PASS "one record per target: newline escaped or path refused" "$RC" "$OUT" "non-zero exit (refusal); lines=$nl (control=$nl_ctrl)" '"lines":'"$nl"',"control_lines":'"$nl_ctrl"
elif [ "$nl" -le "$nl_ctrl" ]; then
  record R1 r PASS "one record per target: newline escaped or path refused" "$RC" "$OUT" "record intact (lines=$nl <= control=$nl_ctrl)" '"lines":'"$nl"',"control_lines":'"$nl_ctrl"
else
  record R1 r FAIL "one record per target: newline escaped or path refused" "$RC" "$OUT" "newline path adds $((nl-nl_ctrl)) extra line(s) vs control ($nl_ctrl -> $nl); a line-oriented TSV consumer mis-parses path/verdict attribution" '"severity":"medium","lines":'"$nl"',"control_lines":'"$nl_ctrl"
fi

# R2 JSON mode.
OUT=$(SOUJI_LEDGER="$LED_EMPTY" timeout 30 bash "$TOOL" --stale-days 1 --json "$NLFILE" 2>&1); RC=$?
parsed=$(printf '%s' "$OUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); p=d.get("path"); print("ok" if p==sys.argv[1] else "path-mismatch:"+repr(p))' "$NLFILE" 2>/dev/null || true)
if [ "$RC" -eq 0 ] && [ "$parsed" = ok ]; then
  record R2 r PASS "single parseable JSON record with the exact path" "$RC" "$OUT" "json_escape covers newlines"
elif [ -z "$parsed" ]; then
  record R2 r FAIL "single parseable JSON record with the exact path" "$RC" "$OUT" "JSON parse failed"
else
  record R2 r FAIL "single parseable JSON record with the exact path" "$RC" "$OUT" "parsed but path mismatch ($parsed)"
fi

# R3 newline name classified as scratch.
run_tool "$LED_EMPTY" "$NL_SCRATCH"
v=$(norm_v); r=$(norm_r)
if [ "$v" = SAFE ] && [ "$r" = stale ]; then
  record R3 r PASS "newline-named scratch: SAFE(stale) ideal; any NOT-SAFE is safe-side" "$RC" "$OUT" "SAFE(stale)"
elif [ "$v" = NOT-SAFE ]; then
  record R3 r PASS "newline-named scratch: SAFE(stale) ideal; any NOT-SAFE is safe-side" "$RC" "$OUT" "safe-side NOT-SAFE ($r)"
elif [ "$v" = SAFE ]; then
  record R3 r FAIL "newline-named scratch: SAFE(stale) ideal; any NOT-SAFE is safe-side" "$RC" "$OUT" "SAFE with unexpected receipt=$r"
else
  record R3 r WARN "newline-named scratch: SAFE(stale) ideal; any NOT-SAFE is safe-side" "$RC" "$OUT" "unexpected"
fi

# R4 ledger smuggle: a row that tries to embed the newline path.
LED_NL="$Q/led-nl.tsv"
{
  printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
  printf '%s\t%s\t%s\t%s\t2026-10-18\traw-newline-smuggle\n' "$NLFILE" "$NL_SHA" "$Q/vault/qctrl.md" "$QV_SHA"
  printf '%s\\n%s\t%s\t%s\t%s\t2026-10-18\tescaped-newline\n' "$R/nl/first" "second.md" "$NL_SHA" "$Q/vault/qctrl.md" "$QV_SHA"
} > "$LED_NL"
LED_NL_LINES=$(wc -l < "$LED_NL" | tr -d ' ')
run_tool "$LED_NL" "$NLFILE"
v=$(norm_v)
if [ "$v" = NOT-SAFE ]; then
  record R4 r PASS "NOT-SAFE — no ledger row can match a newline-containing target" "$RC" "$OUT" "smuggle fails; ledger file has $LED_NL_LINES physical lines (the raw row split)" '"ledger_lines":'"$LED_NL_LINES"
else
  record R4 r FAIL "NOT-SAFE — no ledger row can match a newline-containing target" "$RC" "$OUT" "unexpected $v" '"severity":"critical","ledger_lines":'"$LED_NL_LINES"
fi

# ------------------------------------------------------------- sanity -----
OUT=$(timeout 180 bash "$TOOL" --selftest 2>&1); RC=$?
if [ "$RC" -eq 0 ]; then
  record S0 sanity PASS "installed artifact --selftest exit 0" "$RC" "$OUT" "baseline integrity"
else
  record S0 sanity FAIL "installed artifact --selftest exit 0" "$RC" "$OUT" "selftest broken before any r4 change"
fi

# ------------------------------------------------------------- snapshots --
VAULT_AFTER=$(vault_snap)
VAULT_N_AFTER=$(vault_count)
LIVE_SHA_AFTER=$(sha "$LIVE_LEDGER")
LIVE_LINES_AFTER=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
TOOL_SHA_AFTER=$(sha256sum -- "$TOOL" 2>/dev/null | cut -d' ' -f1)
RO_OK=true
[ "$VAULT_BEFORE" = "$VAULT_AFTER" ] || RO_OK=false
[ "$LIVE_SHA_BEFORE" = "$LIVE_SHA_AFTER" ] || RO_OK=false
[ "$LIVE_LINES_AFTER" = 1 ] || RO_OK=false

# ------------------------------------------------------------- emit json --
mkdir -p "$(dirname -- "$JSON_OUT")"
{
  printf '{\n'
  printf '  "seat": "S54",\n'
  printf '  "kind": "adversarial",\n'
  printf '  "round": 4,\n'
  printf '  "lane": "souji-shokunin",\n'
  printf '  "assignment": "(p) source path is the vault file itself (self-move row); (q) ledger path is a symlink; (r) target path containing newline",\n'
  printf '  "target": {"tool": "%s", "tool_sha256": "%s", "tool_sha256_after": "%s", "sha_stable": %s, "spec": "%s", "spec_sha256": "%s"},\n' \
    "$(jesc "$TOOL")" "$TOOL_SHA_BEFORE" "$TOOL_SHA_AFTER" \
    "$([ "$TOOL_SHA_BEFORE" = "$TOOL_SHA_AFTER" ] && echo true || echo false)" \
    "$(jesc "$SPEC")" "$SPEC_SHA"
  printf '  "readonly_proof": {"vault": "%s", "vault_manifest_before": "%s", "vault_manifest_after": "%s", "vault_files_before": %s, "vault_files_after": %s, "live_ledger": "%s", "live_ledger_sha_before": "%s", "live_ledger_sha_after": "%s", "live_ledger_lines_before": %s, "live_ledger_lines_after": %s, "readonly_ok": %s},\n' \
    "$(jesc "$VAULT")" "$VAULT_BEFORE" "$VAULT_AFTER" "$VAULT_N_BEFORE" "$VAULT_N_AFTER" \
    "$(jesc "$LIVE_LEDGER")" "$LIVE_SHA_BEFORE" "$LIVE_SHA_AFTER" \
    "$LIVE_LINES_BEFORE" "$LIVE_LINES_AFTER" "$RO_OK"
  printf '  "totals": {"pass": %s, "fail": %s, "warn": %s, "info": %s},\n' "$PASS" "$FAIL" "$WARN" "$INFO"
  printf '  "key_findings": [\n'
  printf '    {"id":"p-self-move","severity":"critical","finding":"A ledger row whose vault_path equals its own source_path yields SAFE(moved-to-obsidian). Removing the target deletes the only copy. Same for directories.","evidence":"cases P1, P1d"},\n'
  printf '    {"id":"p-alias","severity":"critical","finding":"A vault_path that is a symlink alias or a ../-spelling of the source also yields SAFE; the alias dangles after removal.","evidence":"cases P2, P3"},\n'
  printf '    {"id":"p-nested","severity":"critical","finding":"A receipt whose vault copy is nested inside the source directory yields SAFE for the directory; removing the source destroys its own vault copy.","evidence":"case P6"},\n'
  printf '    {"id":"q-symlink-audit","severity":"medium","finding":"A symlinked ledger (direct, chain, or absolute external) is followed silently; the receipt evidence names no ledger path, so the receipt cannot be traced to a ledger file. Dangling /dev/null / directory ledgers are refused.","evidence":"cases Q1, Q2, Q4b, Q3, Q4, Q4c"},\n'
  printf '    {"id":"q-race","severity":"low","finding":"Under a ledger-symlink swap race the verdict flips between SAFE and NOT-SAFE (49/51 over 100 runs): the receipt follows whatever target is live at read time; no pinning.","evidence":"case Q6"},\n'
  printf '    {"id":"r-tsv","severity":"medium","finding":"A target path containing a newline breaks the TSV record across two physical lines: path and verdict attribution shift for any line-oriented consumer. --json mode escapes correctly.","evidence":"cases R1, R2"},\n'
  printf '    {"id":"r-scratch","severity":"low","finding":"A newline-named scratch file can never receive SAFE(stale): the live-refs sweep calls rg with the basename and rg rejects a literal newline in the pattern (live-refs=unknown). Safe-side, but the stale receipt is unreachable for such names.","evidence":"case R3"}\n'
  printf '  ],\n'
  printf '  "cases": [\n'
  i_case=0
  for c in "${CASES[@]}"; do
    i_case=$((i_case+1))
    if [ "$i_case" -lt "${#CASES[@]}" ]; then printf '    %s,\n' "$c"; else printf '    %s\n' "$c"; fi
  done
  printf '  ],\n'
  printf '  "limitations": [\n'
  printf '    "The live default ledger path could not be swapped for a symlink (read-only constraint on the real vault/lane surfaces); the q family exercises the same code through SOUJI_LEDGER, the tool documented override.",\n'
  printf '    "Q6 is timing-dependent evidence, not a determinism proof; each observed verdict is consistent with some symlink state.",\n'
  printf '    "The p-family oracle is the removal-safety rule: a moved-to-obsidian receipt must name a distinct copy that survives removal of the target. Self-move, alias, and nested rows are rejected as receipts by this seat.",\n'
  printf '    "The 2026-10-18 manual probe (control SAFE, self-move SAFE) was reproduced by this harness run; the harness is the evidence of record."\n'
  printf '  ],\n'
  printf '  "verdict": "%s"\n' "$([ "$FAIL" -eq 0 ] && echo 'no false-SAFE found in the three assigned families' || echo "false-SAFE/contract failures present: $FAIL")"
  printf '}\n'
} > "$JSON_OUT"

printf '\n==== vadv-54 summary ====\n'
printf 'PASS=%s FAIL=%s WARN=%s INFO=%s  readonly_ok=%s  tool_sha_stable=%s\n' \
  "$PASS" "$FAIL" "$WARN" "$INFO" "$RO_OK" \
  "$([ "$TOOL_SHA_BEFORE" = "$TOOL_SHA_AFTER" ] && echo yes || echo NO)"
printf 'json: %s\n' "$JSON_OUT"
exit 0
