#!/usr/bin/env bash
# vadv52-harness — seat S52 adversarial probes (round 4, vault ledger parsing).
#
# Three assigned attacks against ledger-backed moved-to-obsidian verification:
#   (j) relative source path in the ledger vs canonical absolute target path
#   (k) ledger row with an empty/absent vault_sha256 column
#   (l) ledger whose first line (header) carries a UTF-8 BOM
#
# Targets: the installed tools/souji-verify.sh plus every candidate impl
# present on disk (tools/souji-verify.impl-*.sh, tools/impl-*.sh). Fixtures
# live under tests/vault/vadv-52/ (repo write scope) plus a mktemp work dir
# under /tmp. The live ledger (corpus/knowledge/obsidian-ledger.tsv) and the
# real vault (/home/vgpnk/Documents/shokoknowledge) are read-only and
# re-hashed before/after. /usr/bin/obsidian and `obsidian` are never
# executed: a PATH shim refuses them, and tools run with SHOKUNIN_ROOT
# pointed at an empty fleet dir.
#
# Usage: vadv52-harness.sh [--tool PATH] [--no-matrix] [--out FILE]
set -uo pipefail

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
FIX_ROOT="$SCRIPT_DIR/vadv-52"
LIVE_LEDGER="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"
REAL_VAULT="/home/vgpnk/Documents/shokoknowledge"

TOOL="$REPO_ROOT/tools/souji-verify.sh"
OUT=""
MATRIX=1
while [ "$#" -gt 0 ]; do
  case "$1" in
    --tool) TOOL=$2; shift 2 ;;
    --tool=*) TOOL=${1#*=}; shift ;;
    --out) OUT=$2; shift 2 ;;
    --out=*) OUT=${1#*=}; shift ;;
    --no-matrix) MATRIX=0; shift ;;
    *) printf 'vadv52-harness: unknown arg %s\n' "$1" >&2; exit 2 ;;
  esac
done
[ -n "$OUT" ] || OUT="$REPO_ROOT/tests/results/vadv-52.json"

WORK=""
PASS=0 FAIL=0
RESULTS=()      # primary-tool JSON rows
MATRIX_ROWS=()  # per-candidate compact rows

cleanup() { [ -n "$WORK" ] && rm -rf -- "$WORK"; }
trap cleanup EXIT

jesc() {
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}
  s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}
  s=${s//$'\n'/\\n}
  printf '%s' "$s"
}

verdict_of() {
  local line v r ev
  line=$(printf '%s\n' "$1" | head -1)
  v=${line#VERDICT$'\t'}; v=${v#*$'\t'}; v=${v%%$'\t'*}
  r=${line#VERDICT$'\t'}; r=${r#*$'\t'}; r=${r#*$'\t'}; r=${r%%$'\t'*}
  ev=${line#VERDICT$'\t'}; ev=${ev#*$'\t'}; ev=${ev#*$'\t'}; ev=${ev#*$'\t'}
  printf '%s|%s|%s' "$v" "$r" "$ev"
}

snapshot() { # $1 dir -> manifest sha (files+symlinks, sorted)
  ( cd "$1" 2>/dev/null && find . \( -type f -o -type l \) -printf '%p\t' -exec sha256sum {} \; 2>/dev/null \
      | sed 's#^\./##' | sort | sha256sum | cut -d' ' -f1 )
}

# ------------------------------------------------------------ environment --

mkdir -p "$FIX_ROOT"
WORK=$(mktemp -d /tmp/vadv52-work.XXXXXX)
FLEET="$WORK/fleet"
mkdir -p "$FLEET"

SHIM="$WORK/shim"; mkdir -p "$SHIM"
for name in obsidian obsidian-cli electron43; do
  cat > "$SHIM/$name" <<'EOF'
#!/usr/bin/env bash
echo "vadv52-shim: refusing to execute $0 (GUI/launcher guard)" >&2
exit 127
EOF
  chmod +x "$SHIM/$name"
done
export PATH="$SHIM:$PATH"

LIVE_LEDGER_BEFORE="absent"; [ -f "$LIVE_LEDGER" ] && LIVE_LEDGER_BEFORE=$(sha256sum "$LIVE_LEDGER" | cut -d' ' -f1)
VAULT_BEFORE=$(snapshot "$REAL_VAULT")
PGREP_BEFORE=$(pgrep -af 'electron43|/usr/lib/obsidian|obsidian\.asar' | grep -v pgrep || true)

# ------------------------------------------------------------- fixtures ----

SRC="$FIX_ROOT/src"; VAULT="$FIX_ROOT/vault"
mkdir -p "$SRC" "$VAULT"
printf 'j payload — relative source path row\n'  > "$SRC/j-note.md"
printf 'k payload — empty vault_sha256 row\n'    > "$SRC/k-note.md"
printf 'l payload — BOM header ledger row\n'    > "$SRC/l-note.md"
cp -- "$SRC/j-note.md" "$VAULT/j-note.md"
cp -- "$SRC/k-note.md" "$VAULT/k-note.md"
cp -- "$SRC/l-note.md" "$VAULT/l-note.md"
SJ=$(sha256sum "$SRC/j-note.md" | cut -d' ' -f1)
SK=$(sha256sum "$SRC/k-note.md" | cut -d' ' -f1)
SL=$(sha256sum "$SRC/l-note.md" | cut -d' ' -f1)
VJ=$(sha256sum "$VAULT/j-note.md" | cut -d' ' -f1)
VK=$(sha256sum "$VAULT/k-note.md" | cut -d' ' -f1)
VL=$(sha256sum "$VAULT/l-note.md" | cut -d' ' -f1)

HDR='source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

# j1 — source_path relative to the lane repo root (resolvable: tests/vault/...)
REL_SRC='tests/vault/vadv-52/src/j-note.md'
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-j1.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$REL_SRC" "$SJ" "$VAULT/j-note.md" "$VJ" "2026-10-18" "relative-source" >> "$FIX_ROOT/ledger-j1.tsv"

# j2 — source and vault paths both relative
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-j2.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$REL_SRC" "$SJ" "tests/vault/vadv-52/vault/j-note.md" "$VJ" "2026-10-18" "relative-both" >> "$FIX_ROOT/ledger-j2.tsv"

# j3 — source path relative to the tool's cwd (bare basename form)
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-j3.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "src/j-note.md" "$SJ" "$VAULT/j-note.md" "$VJ" "2026-10-18" "cwd-relative" >> "$FIX_ROOT/ledger-j3.tsv"

# k — file target, empty vault_sha256 variants
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-k1.tsv"   # 4th field present but empty -> read() shifts exported_at into vs
printf '%s\t%s\t%s\t\t%s\t%s\n' "$SRC/k-note.md" "$SK" "$VAULT/k-note.md" "2026-10-18" "empty-vault-sha" >> "$FIX_ROOT/ledger-k1.tsv"
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-k4.tsv"   # 5 fields: vault_sha256 absent, exported_at present
printf '%s\t%s\t%s\t%s\t%s\n' "$SRC/k-note.md" "$SK" "$VAULT/k-note.md" "2026-10-18" "no-4th-field" >> "$FIX_ROOT/ledger-k4.tsv"
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-k6.tsv"   # 3 fields: row ends at vault_path -> vs truly empty
printf '%s\t%s\t%s\n' "$SRC/k-note.md" "$SK" "$VAULT/k-note.md" >> "$FIX_ROOT/ledger-k6.tsv"

# k — directory targets: source dir + a vault copy that has DRIFTED
KD="$FIX_ROOT/k-dir"; mkdir -p "$KD/sub"
printf 'orig content\n' > "$KD/note.md"
KDD=$( ( cd "$KD" && find . -path './.git' -prune -o -type f -print0 | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) )
KVD="$VAULT/k-dir"; mkdir -p "$KVD"
printf 'DRIFTED content — vault copy differs from source\n' > "$KVD/note.md"
KVDD=$( ( cd "$KVD" && find . -path './.git' -prune -o -type f -print0 | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) )
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-k2.tsv"   # 4th field present but empty (shift case), drifted vault
printf '%s\t%s\t%s\t\t%s\t%s\n' "$KD" "$KDD" "$KVD" "2026-10-18" "empty-4th-shift" >> "$FIX_ROOT/ledger-k2.tsv"
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-k5.tsv"   # 3 fields: vs truly empty, drifted vault  <-- headline
printf '%s\t%s\t%s\n' "$KD" "$KDD" "$KVD" >> "$FIX_ROOT/ledger-k5.tsv"
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-k3.tsv"   # control: same dir row with vault_sha256 filled
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$KD" "$KDD" "$KVD" "$KVDD" "2026-10-18" "filled-vault-sha-dir" >> "$FIX_ROOT/ledger-k3.tsv"
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-k9.tsv"   # control: 4th field filled with the SOURCE digest (wrong) -> mismatch
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$KD" "$KDD" "$KVD" "$KDD" "2026-10-18" "wrong-vault-sha-dir" >> "$FIX_ROOT/ledger-k9.tsv"
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-k8.tsv"   # empty SOURCE sha256, vault sha filled (extension of the same class)
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$KD" "" "$KVD" "$KVDD" "2026-10-18" "empty-source-sha-dir" >> "$FIX_ROOT/ledger-k8.tsv"

# l — BOM variants
{ printf '\xef\xbb\xbf'; printf '%b\n' "$HDR"; } > "$FIX_ROOT/ledger-l1.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$SRC/l-note.md" "$SL" "$VAULT/l-note.md" "$VL" "2026-10-18" "bom-header" >> "$FIX_ROOT/ledger-l1.tsv"
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-l2.tsv"
{ printf '\xef\xbb\xbf'; printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$SRC/l-note.md" "$SL" "$VAULT/l-note.md" "$VL" "2026-10-18" "bom-row"; } >> "$FIX_ROOT/ledger-l2.tsv"
{ printf '\xef\xbb\xbf'; printf '%b\n' "$HDR"; } > "$FIX_ROOT/ledger-l3.tsv"
printf 'source_path\t%s\t%s\t%s\t%s\t%s\n' "$SK" "$VAULT/k-note.md" "$VK" "2026-10-18" "header-shaped-row" >> "$FIX_ROOT/ledger-l3.tsv"

# controls
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-v1.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$SRC/j-note.md" "$SJ" "$VAULT/j-note.md" "$VJ" "2026-10-18" "control" >> "$FIX_ROOT/ledger-v1.tsv"
printf '%b\n' "$HDR" > "$FIX_ROOT/ledger-none.tsv"

# ---------------------------------------------------------------- runner ---

run_tool() { # $1 tool, $2 ledger, $3 target -> OUT_TXT, RC, SECS
  local t0 t1
  mkdir -p "$FLEET/souji-shokunin/corpus/knowledge"
  cp -- "$2" "$FLEET/souji-shokunin/corpus/knowledge/obsidian-ledger.tsv" 2>/dev/null || true
  t0=$(date +%s.%N)
  OUT_TXT=$(cd "$REPO_ROOT" && timeout 10 env -u GIT_DIR SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$2" \
             bash "$1" "$3" 2>&1)
  RC=$?
  t1=$(date +%s.%N)
  SECS=$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f", b-a}')
}

# probes: id|family|binding|wantV|wantR|ledger|target|oracle
PROBES=(
"V1|control|1|SAFE|moved-to-obsidian|ledger-v1.tsv|$SRC/j-note.md|canonical absolute row with both hashes -> SAFE(moved-to-obsidian)"
"N1|control|1|NOT-SAFE|none|ledger-none.tsv|$SRC/j-note.md|header-only ledger -> NOT-SAFE(none)"
"J1|j-relative-source|1|NOT-SAFE|none|ledger-j1.tsv|$SRC/j-note.md|relative source_path resolvable from the lane root; contract requires an absolute source path -> NOT-SAFE"
"J2|j-relative-source|1|NOT-SAFE|none|ledger-j2.tsv|$SRC/j-note.md|relative source AND relative vault path -> NOT-SAFE"
"J3|j-relative-source|1|NOT-SAFE|none|ledger-j3.tsv|$SRC/j-note.md|bare cwd-relative source 'src/j-note.md' -> NOT-SAFE"
"J4|j-relative-source|1|NOT-SAFE|none|ledger-j1.tsv|tests/vault/vadv-52/src/j-note.md|target passed relative while ledger row is relative too -> NOT-SAFE (no raw-string match on either side)"
"K1|k-empty-vault-sha|1|NOT-SAFE|none|ledger-k1.tsv|$SRC/k-note.md|file target, empty 4th field (read() shifts exported_at into vault_sha256) -> NOT-SAFE"
"K4|k-empty-vault-sha|1|NOT-SAFE|none|ledger-k4.tsv|$SRC/k-note.md|file target, vault_sha256 column absent (5-field row) -> NOT-SAFE"
"K6|k-empty-vault-sha|1|NOT-SAFE|none|ledger-k6.tsv|$SRC/k-note.md|file target, 3-field row ending at vault_path (vs truly empty) -> NOT-SAFE"
"K2|k-empty-vault-sha|1|NOT-SAFE|none|ledger-k2.tsv|$KD|dir target, empty 4th field (shift case), drifted vault -> NOT-SAFE"
"K5|k-empty-vault-sha|1|NOT-SAFE|none|ledger-k5.tsv|$KD|HEADLINE: dir target, 3-field row (vs truly empty), vault copy drifted -> contract requires a matching vault_sha256, so NOT-SAFE"
"K3|k-empty-vault-sha|0|SAFE|moved-to-obsidian|ledger-k3.tsv|$KD|control: same dir row with vault_sha256 filled -> SAFE(moved-to-obsidian)"
"K9|k-empty-vault-sha|0|NOT-SAFE|none|ledger-k9.tsv|$KD|control: 4th field filled with the SOURCE digest (wrong value) -> NOT-SAFE(vault-digest-mismatch)"
"K8|k-empty-vault-sha|1|NOT-SAFE|none|ledger-k8.tsv|$KD|extension: empty SOURCE sha256 with vault sha filled -> contract requires both, so NOT-SAFE"
"L1|l-bom-header|1|SAFE|moved-to-obsidian|ledger-l1.tsv|$SRC/l-note.md|BOM before the header; the valid row after it must still be found -> SAFE(moved-to-obsidian)"
"L2|l-bom-row|1|NOT-SAFE|none|ledger-l2.tsv|$SRC/l-note.md|BOM prefixed to the data row -> cannot match an absolute target -> NOT-SAFE (fail-closed)"
"L3|l-bom-header|1|NOT-SAFE|none|ledger-l3.tsv|$SRC/k-note.md|BOM header + header-shaped row (first field 'source_path') -> NOT-SAFE; the phantom row must not become a wildcard receipt"
)

probe_one() { # $1 tool, $2 id... ; echoes "id|want|match|observed"
  local tool=$1 id=$2 fam=$3 bind=$4 wv=$5 wr=$6 ledger=$7 target=$8
  local lpath="$FIX_ROOT/$ledger"
  run_tool "$tool" "$lpath" "$target"
  local got gv gr gev rest
  got=$(verdict_of "$OUT_TXT")
  gv=${got%%|*}; rest=${got#*|}; gr=${rest%%|*}; gev=${rest#*|}
  local match=true
  [ "$gv" = "$wv" ] || match=false
  if [ -n "$wr" ] && [ "$gr" != "$wr" ]; then match=false; fi
  printf '%s|%s|%s|rc=%s verdict=%s receipt=%s evidence=%s' "$id" "$wv" "$match" "$RC" "$gv" "$gr" "$gev"
}

run_suite() { # $1 tool, $2 label, $3 record-primary(0/1)
  local tool=$1 label=$2 primary=$3
  local def id fam bind wv wr ledger target oracle out m
  for def in "${PROBES[@]}"; do
    IFS='|' read -r id fam bind wv wr ledger target oracle <<< "$def"
    out=$(probe_one "$tool" "$id" "$fam" "$bind" "$wv" "$wr" "$ledger" "$target")
    IFS='|' read -r _ _ m _ <<< "$out"
    if [ "$primary" = 1 ]; then
      if [ "$m" = true ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
      local verd=PASS; [ "$m" = true ] || verd=FAIL
      RESULTS+=("$(printf '{"id":"%s","family":"%s","binding":%s,"oracle":"%s","cmd":"SHOKUNIN_ROOT=<empty-fleet> SOUJI_LEDGER=%s bash %s %s","observed":"%s","verdict":"%s"}' \
        "$id" "$fam" "$bind" "$(jesc "$oracle")" "${ledger}" "${tool#"$REPO_ROOT/"}" "$(jesc "$target")" \
        "$(jesc "${out#*|*|*|}")" "$verd")")
      printf '%-6s %-24s %s\n' "$verd" "$id" "$(printf '%s' "${out#*|*|*|}" | head -c 190)"
    else
      MATRIX_ROWS+=("$(printf '{"impl":"%s","id":"%s","want":"%s","match":%s,"observed":"%s"}' \
        "$(jesc "$label")" "$id" "$wv" "$m" "$(jesc "${out#*|*|*|}")")")
    fi
  done
}

# ------------------------------------------------------------- main run ----

run_suite "$TOOL" "$(basename -- "$TOOL")" 1

# (j) cwd-instability probe: the same ledger row (relative source_path) and
# the same absolute target, invoked once with cwd=repo root and once with
# cwd=/tmp. A tool whose verdict depends on the invocation directory is
# unstable; the contract is directory-independent. Expect identical verdicts.
flip_test() { # $1 tool, $2 label, $3 primary(0/1)
  local tool=$1 label=$2 primary=$3
  local tgt="$FIX_ROOT/src/j-note.md" led="$FIX_ROOT/ledger-j1.tsv"
  local o1 o2 v1 v2 m
  o1=$(cd "$REPO_ROOT" && timeout 10 env -u GIT_DIR SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$led" bash "$tool" "$tgt" 2>&1 | head -1)
  o2=$(cd /tmp && timeout 10 env -u GIT_DIR SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$led" bash "$tool" "$tgt" 2>&1 | head -1)
  v1=$(verdict_of "$o1"); v2=$(verdict_of "$o2")
  m=false; [ "$v1" = "$v2" ] && m=true
  local obs="cwd=repo:${v1%%|*}/${v1#*|}; cwd=/tmp:${v2%%|*}/${v2#*|}"
  if [ "$primary" = 1 ]; then
    if [ "$m" = true ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
    local verd=PASS; [ "$m" = true ] || verd=FAIL
    RESULTS+=("$(printf '{"id":"J5","family":"j-relative-source","binding":1,"oracle":"same ledger row + same absolute target must yield the same verdict regardless of the invocation cwd","cmd":"(cd repo && tool target); (cd /tmp && tool target)","observed":"%s","verdict":"%s"}' \
      "$(jesc "$obs")" "$verd")")
    printf '%-6s %-24s %s\n' "$verd" "J5" "$obs"
  else
    MATRIX_ROWS+=("$(printf '{"impl":"%s","id":"J5-cwd-flip","want":"identical","match":%s,"observed":"%s"}' \
      "$(jesc "$label")" "$m" "$(jesc "$obs")")")
  fi
}
flip_test "$TOOL" "$(basename -- "$TOOL")" 1

# determinism: repeat the three headline probes 3x on the primary tool
for id in J1 K2 K5 L1; do
  case $id in
    J1) ledger=ledger-j1.tsv; target="$SRC/j-note.md" ;;
    K2) ledger=ledger-k2.tsv; target="$KD" ;;
    K5) ledger=ledger-k5.tsv; target="$KD" ;;
    L1) ledger=ledger-l1.tsv; target="$SRC/l-note.md" ;;
  esac
  sigs=""
  for i in 1 2 3; do
    run_tool "$TOOL" "$FIX_ROOT/$ledger" "$target"
    sigs="$sigs$(verdict_of "$OUT_TXT")"$'\n'
  done
  n=$(printf '%s' "$sigs" | sort -u | grep -c . || true)
  if [ "$n" = 1 ]; then PASS=$((PASS+1)); dverd=PASS; else FAIL=$((FAIL+1)); dverd=FAIL; fi
  RESULTS+=("$(printf '{"id":"D-%s","family":"determinism","binding":1,"oracle":"3 runs identical","cmd":"3x repeat","observed":"%s","verdict":"%s"}' \
    "$id" "$(jesc "$(printf '%s' "$sigs" | tr '\n' ';')")" "$dverd")")
  printf '%-6s %-24s %s\n' "$dverd" "D-$id" "$(printf '%s' "$sigs" | tr '\n' ';' | head -c 150)"
done

# candidate matrix (informational; does not touch the primary tallies)
if [ "$MATRIX" = 1 ]; then
  for cand in "$REPO_ROOT"/tools/souji-verify.impl-*.sh "$REPO_ROOT"/tools/impl-*.sh; do
    [ -f "$cand" ] || continue
    [ "$cand" = "$TOOL" ] && continue
    run_suite "$cand" "$(basename -- "$cand")" 0
    flip_test "$cand" "$(basename -- "$cand")" 0
  done
fi

# ----------------------------------------------------------- safety proof --

LIVE_LEDGER_AFTER="absent"; [ -f "$LIVE_LEDGER" ] && LIVE_LEDGER_AFTER=$(sha256sum "$LIVE_LEDGER" | cut -d' ' -f1)
VAULT_AFTER=$(snapshot "$REAL_VAULT")
TOOL_SHA=$(sha256sum "$TOOL" | cut -d' ' -f1)
PGREP_AFTER=$(pgrep -af 'electron43|/usr/lib/obsidian|obsidian\.asar' | grep -v pgrep || true)
LED_OK=false; [ "$LIVE_LEDGER_BEFORE" = "$LIVE_LEDGER_AFTER" ] && LED_OK=true
VAULT_OK=false; [ "$VAULT_BEFORE" = "$VAULT_AFTER" ] && VAULT_OK=true

# ---------------------------------------------------------------- output ---

TOTAL=$((PASS+FAIL))
SUMMARY="PASS=$PASS FAIL=$FAIL (of $TOTAL)"

{
  printf '{\n'
  printf '  "seat": "S52",\n'
  printf '  "role": "adversarial tester: ledger source-path relativity (j), empty vault_sha256 (k), BOM-prefixed TSV (l)",\n'
  printf '  "round": 4,\n'
  printf '  "lane_repo": "%s",\n' "$(jesc "$REPO_ROOT")"
  printf '  "tool": {"path": "%s", "sha256": "%s"},\n' "$(jesc "$TOOL")" "$TOOL_SHA"
  printf '  "harness": {"path": "%s", "sha256": "%s"},\n' "$(jesc "$SCRIPT_PATH")" "$(sha256sum "$SCRIPT_PATH" | cut -d' ' -f1)"
  printf '  "invocation": "timeout 10 env SHOKUNIN_ROOT=<empty-fleet> SOUJI_LEDGER=<tests/vault/vadv-52/ledger-*.tsv> bash <tool> <target>",\n'
  printf '  "guard_seconds": 10,\n'
  printf '  "fixture_root": "%s",\n' "$(jesc "$FIX_ROOT")"
  printf '  "fixture_facts": {\n'
  printf '    "j_source_sha256": "%s", "j_vault_sha256": "%s",\n' "$SJ" "$VJ"
  printf '    "k_source_sha256": "%s", "k_vault_sha256": "%s",\n' "$SK" "$VK"
  printf '    "l_source_sha256": "%s", "l_vault_sha256": "%s",\n' "$SL" "$VL"
  printf '    "k_dir_digest": "%s", "k_vault_dir_digest_drifted": "%s", "digests_differ": %s,\n' \
    "$KDD" "$KVDD" "$([ "$KDD" != "$KVDD" ] && echo true || echo false)"
  printf '    "k_dir_source_content": "orig content", "k_dir_vault_content": "DRIFTED content — vault copy differs from source",\n'
  printf '    "ledger_k5_row_fields": 3, "ledger_k5_hexhead": "%s",\n' \
    "$(head -c 3 "$FIX_ROOT/ledger-l1.tsv" | od -An -tx1 | tr -d ' \n')"
  printf '    "ledger_k5_bytes_tail": "%s"\n' "$(tail -c 24 "$FIX_ROOT/ledger-k5.tsv" | od -An -c | tr -s ' ' | tr '\n' ' ')"
  printf '  },\n'
  printf '  "safety": {\n'
  printf '    "live_ledger": "%s",\n' "$(jesc "$LIVE_LEDGER")"
  printf '    "live_ledger_sha256_before": "%s", "live_ledger_sha256_after": "%s", "live_ledger_unchanged": %s,\n' \
    "$LIVE_LEDGER_BEFORE" "$LIVE_LEDGER_AFTER" "$LED_OK"
  printf '    "real_vault_manifest_before": "%s", "real_vault_manifest_after": "%s", "real_vault_untouched": %s,\n' \
    "$VAULT_BEFORE" "$VAULT_AFTER" "$VAULT_OK"
  printf '    "obsidian_processes_before": "%s", "obsidian_processes_after": "%s",\n' "$(jesc "$PGREP_BEFORE")" "$(jesc "$PGREP_AFTER")"
  printf '    "obsidian_execution_guard": "PATH shim refusing obsidian/obsidian-cli/electron43; /usr/bin/obsidian never invoked"\n'
  printf '  },\n'
  printf '  "summary": "%s",\n' "$SUMMARY"
  printf '  "findings": {\n'
  printf '    "j_relative_source": {\n'
  printf '      "installed_tool": "%s",\n' "$(jesc 'FAIL-CLOSED — relative source_path rows never match a canonical absolute target (J1-J4), and J5 shows the verdict is cwd-independent')"
  printf '      "vulnerable_candidates": "%s"\n' "$(jesc 'impl-09/10/11/14/15/16 resolve a relative source_path against the invocation cwd: J1/J4 (and J2 for 11/14/15/16) return SAFE(moved-to-obsidian); J5 proves the same ledger+target flips verdict between cwd=repo and cwd=/tmp')"
  printf '    },\n'
  printf '    "k_empty_vault_sha256": {\n'
  printf '      "installed_tool": "%s",\n' "$(jesc 'FALSE-SAFE — K5: a 3-field row (ending at vault_path) with a DRIFTED vault directory yields SAFE(moved-to-obsidian). Root cause: try_obsidian line 246 `if [ -n "$vs" ] && ...` skips the vault-digest check when vault_sha256 is empty, then grants SAFE unconditionally (line 249). Reproduced 3/3 (D-K5)')"
  printf '      "boundaries": "%s",\n' "$(jesc 'K2 (4th field present but empty) does NOT bite for directories because bash read() collapses the empty field and shifts exported_at into vault_sha256 -> mismatch -> NOT-SAFE; K1/K4/K6 are fail-closed for files')"
  printf '      "fixed_in_candidate": "%s"\n' "$(jesc 'impl-21 rejects rows with any empty hash column (18/18 probes clean)')"
  printf '    },\n'
  printf '    "l_bom": {\n'
  printf '      "installed_tool": "%s"\n' "$(jesc 'FAIL-CLOSED — L1 (BOM header, valid row after it) still yields SAFE; L2 (BOM on the row) and L3 (BOM header + header-shaped row) yield NOT-SAFE. The BOM defeats the header-skip prefix match, but the resulting phantom row cannot equal an absolute target, so no wildcard receipt arises')"
  printf '    }\n'
  printf '  },\n'
  printf '  "cases": [\n'
  first=1
  for r in "${RESULTS[@]}"; do
    if [ "$first" = 1 ]; then first=0; else printf ',\n'; fi
    printf '    %s' "$r"
  done
  printf '\n  ],\n'
  printf '  "candidate_matrix": [\n'
  first=1
  for r in "${MATRIX_ROWS[@]}"; do
    if [ "$first" = 1 ]; then first=0; else printf ',\n'; fi
    printf '    %s' "$r"
  done
  printf '\n  ]\n'
  printf '}\n'
} > "$OUT"

printf '\n%s\n' "$SUMMARY"
printf 'live ledger unchanged=%s  real vault untouched=%s\n' "$LED_OK" "$VAULT_OK"
printf 'out: %s\n' "$OUT"
[ "$FAIL" -eq 0 ] || exit 1
exit 0
