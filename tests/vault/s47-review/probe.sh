#!/usr/bin/env bash
# S47 reviewer — independent probe battery for round-4 vault-verify impls.
# Usage: probe.sh <impl-path> <world-dir> <outdir>
# Emits <outdir>/probes.tsv (id, expect, observed-class, verdict-field,
# receipt, pass, exit, evidence) and raw logs. Read-only over the real vault
# and the live ledger; the sandbox PATH never resolves the real obsidian.
set -uo pipefail
IMPL="${1:?impl}"; W="${2:?world}"; OUT="${3:?outdir}"
mkdir -p "$OUT"
IMPL=$(readlink -f "$IMPL"); W=$(readlink -f "$W")
LD="$W/ledgers"; SRC="$W/src"; VLT="$W/vault"
REPO=/home/vgpnk/Projects/shokunin/souji-shokunin
LIVE_LEDGER=$REPO/corpus/knowledge/obsidian-ledger.tsv
REALVAULT=/home/vgpnk/Documents/shokoknowledge
TSV="$OUT/probes.tsv"
printf 'id\texpect\tobserved\tverdict\treceipt\tpass\texit\tevidence\n' > "$TSV"

# ---- sandbox: poison obsidian, isolate HOME/TMPDIR -------------------------
SB="$OUT/sandbox"; mkdir -p "$SB/bin" "$SB/home" "$SB/tmp"
POISON="$SB/obsidian-poison.log"; : > "$POISON"
cat > "$SB/bin/obsidian" <<'EOF'
#!/usr/bin/env bash
echo "INVOKED $*" >> "$POISON_LOG_S47"
exit 99
EOF
chmod +x "$SB/bin/obsidian"
cat > "$SB/bin/obsidian-cli-inspector" <<'EOF'
#!/usr/bin/env bash
echo "INVOKED $*" >> "$POISON_LOG_S47"
exit 98
EOF
chmod +x "$SB/bin/obsidian-cli-inspector"
export POISON_LOG_S47="$POISON"
export PATH="$SB/bin:/usr/bin:/bin"
export HOME="$SB/home"
export TMPDIR="$SB/tmp"

# ---- discovery -------------------------------------------------------------
HELP="$OUT/help.txt"
timeout 30 bash "$IMPL" --help > "$HELP" 2>&1; HELP_RC=$?
LEDGER_FLAG=$(grep -oE '\-\-[a-z-]*ledger[a-z-]*' "$HELP" | head -1)
VAULT_FLAG=$(grep -oE '\-\-[a-z-]*vault[a-z-]*' "$HELP" | head -1)
[ -n "$VAULT_FLAG" ] || VAULT_FLAG=$(grep -oE '\-\-vault-dir' "$HELP" | head -1)
printf 'help_rc=%s ledger_flag=%s vault_flag=%s\n' "$HELP_RC" "${LEDGER_FLAG:-}" "${VAULT_FLAG:-}" >> "$OUT/meta.txt"
IMPL_SHA=$(sha256sum "$IMPL" | cut -d' ' -f1); IMPL_MODE=$(stat -c %a "$IMPL")

# ---- run helper ------------------------------------------------------------
# run_impl <ledger> <vault> <target> [extra args...]
# primary form: plain positional target (r4 mode-A contract, runner-39 shape);
# fallback: `--` separator (r2 tool shape) when the primary yields nothing.
run_impl() {
  local lg=$1 vt=$2 tgt=$3; shift 3
  local args=()
  [ -n "$LEDGER_FLAG" ] && args+=("$LEDGER_FLAG" "$lg")
  [ -n "$VAULT_FLAG" ] && [ -n "$vt" ] && args+=("$VAULT_FLAG" "$vt")
  local out rc
  out=$(env SOUJI_LEDGER="$lg" SOUJI_VAULT="${vt:-}" OBSIDIAN_LEDGER="$lg" \
      OBSIDIAN_VAULT="${vt:-}" SOUJI_VAULT_PATH="${vt:-}" VAULT_PATH="${vt:-}" \
      timeout 30 bash "$IMPL" "${args[@]}" "$@" "$tgt" 2>&1); rc=$?
  if [ -z "$out" ] || [ $rc -eq 2 ]; then
    out=$(env SOUJI_LEDGER="$lg" SOUJI_VAULT="${vt:-}" OBSIDIAN_LEDGER="$lg" \
        OBSIDIAN_VAULT="${vt:-}" SOUJI_VAULT_PATH="${vt:-}" VAULT_PATH="${vt:-}" \
        timeout 30 bash "$IMPL" "${args[@]}" "$@" -- "$tgt" 2>&1); rc=$?
  fi
  printf '%s' "$out"
  return $rc
}

# classify output — scan lines for the first carrying a verdict token so
# stderr noise (e.g. sha256sum EACCES) ahead of the verdict line is skipped
classify() { # stdin -> class|verdict|receipt|evidence
  local line v r ev fld cls i n
  line=""
  while IFS= read -r l; do
    case "$l" in
      *VERIFIED*|*SAFE*) line="$l"; break;;
    esac
    [ -z "$line" ] && [ -n "$l" ] && line="$l"
  done <<<"$1"
  if [ -z "$line" ]; then printf 'NONE|||\n'; return; fi
  v=""; r=""; ev=""
  n=$(printf '%s' "$line" | awk -F'\t' '{print NF}')
  for i in $(seq 1 "$n"); do
    fld=$(printf '%s' "$line" | awk -F'\t' -v k="$i" '{print $k}')
    case "$fld" in
      VERIFIED|SAFE|NOT-VERIFIED|NOT_VERIFIED|NOT-SAFE|NOTSAFE|NOT-VERIFIED\(*|NOT_VERIFIED\(*|NOT-SAFE\(*)
        [ -z "$v" ] && v="$fld";;
      VERIFIED\(*|SAFE\(*|NOT-VERIFIED\(*|NOT-SAFE\(*)
        [ -z "$v" ] && v="$fld";;
    esac
  done
  [ -z "$v" ] && v=$(printf '%s' "$line" | awk '{print $1}')
  # normalize composite tokens: VERIFIED(receipt) -> VERIFIED ; keep reason inside
  local base_v="$v"
  case "$base_v" in
    VERIFIED\(*|SAFE\(*) base_v="${base_v%%(*}";;
  esac
  case "$base_v" in
    VERIFIED|SAFE) cls=V;;
    NOT-VERIFIED*|NOT_VERIFIED*|NOT-SAFE*|NOTSAFE*) cls=N;;
    *) cls=X;;
  esac
  r=$(printf '%s' "$line" | awk -F'\t' '{for(i=1;i<=NF;i++) if($i ~ /moved-to-obsidian|none|secrets-refusal|unreachable|metadata-prune|pushed|absent|sha-mismatch|no-ledger|no-matching/) {print $i; exit}}')
  ev=$(printf '%s' "$line" | awk -F'\t' '{print $NF}')
  printf '%s|%s|%s|%s\n' "$cls" "$v" "$r" "$ev"
}

probe() { # probe <id> <expect> <ledger> <target> [note]
  local id=$1 exp=$2 lg=$3 tgt=$4 note=${5:-}
  local out rc
  out=$(run_impl "$lg" "$VLT" "$tgt"); rc=$?
  local cls v r ev; IFS='|' read -r cls v r ev <<<"$(classify "$out")"
  local pass=0
  case "$exp" in
    V) [ "$cls" = V ] && pass=1;;
    N) [ "$cls" = N ] && pass=1;;
    R) [ "$cls" = N ] && pass=1;;
    I) pass=1;;
  esac
  # secrets canary must never appear
  if [ "$exp" = R ]; then
    case "$out" in *SECRET_CANARY_S47*) pass=0; ev="$ev;CANARY-ECHOED";; esac
  fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$id" "$exp" "$cls" "$v" "$r" "$pass" "$rc" "${ev:0:180}" >> "$TSV"
  { printf '### %s expect=%s rc=%s\n%s\n' "$id" "$exp" "$rc" "$out"; } >> "$OUT/raw.log"
}

# ---- vault + live-ledger fingerprints (rails) ------------------------------
vault_fp() {
  { find "$REALVAULT" -type f -not -path '*/.git/*' -print0 | sort -z \
      | xargs -0 -r sha256sum 2>/dev/null; } | sha256sum | cut -d' ' -f1
}

# real-vault probe fixtures must exist BEFORE the world fingerprint
RV="$W/realledger"; mkdir -p "$RV"
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
mkled() { # mkled <file> <rows...>
  local f=$1; shift
  { printf '%s\n' "$HDR"; local r; for r in "$@"; do printf '%b\n' "$r"; done; } > "$f"
}
SHA_HOME=$(sha256sum "$REALVAULT/Home.md" 2>/dev/null | cut -d' ' -f1)
SP_HOME="$SRC/real-home.md"; cp "$REALVAULT/Home.md" "$SP_HOME" 2>/dev/null
mkled "$RV/RV1.tsv" "$SP_HOME\t$SHA_HOME\t$REALVAULT/Home.md\t$SHA_HOME\t2026-10-18\treal-match"
mkled "$RV/RV2.tsv" "$SP_HOME\t$SHA_HOME\t$REALVAULT/Home.md\t0000000000000000000000000000000000000000000000000000000000000000\t2026-10-18\treal-wrong-hash"

V_BEFORE=$(vault_fp)
LL_BEFORE=$(sha256sum "$LIVE_LEDGER" | cut -d' ' -f1)
W_BEFORE=$(find "$W" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1)

# ---- probes ----------------------------------------------------------------
probe L1  V "$LD/L1.tsv"  "$SRC/matched.md"      "matched row"
probe L2  N "$LD/L2.tsv"  "$SRC/vaulttamper.md"  "vault tampered"
probe L3  N "$LD/L3.tsv"  "$SRC/sourcetamper.md" "source tampered"
probe L4  N "$LD/L4.tsv"  "$SRC/absentvault.md"  "vault absent"
probe L5  N "$LD/L5.tsv"  "$SRC/absentsource.md" "source absent"
probe L6  N "$LD/L6.tsv"  "$SRC/matched.md"      "header-only ledger"
probe L7  N "$LD/L7.tsv"  "$SRC/matched.md"      "wrong vault hash col"
probe L8  N "$LD/L8.tsv"  "$SRC/matched.md"      "both hash cols empty"
probe L8b N "$LD/L8b.tsv" "$SRC/matched.md"      "vault hash col empty"
probe L8c N "$LD/L8c.tsv" "$SRC/matched.md"      "source hash col empty"
probe L9  N "$LD/L9.tsv"  "$SRC/subtle.md"       "one-byte change (newline)"
probe L10 V "$LD/L10.tsv" "$SRC/crlfpair.md"     "crlf pair matched"
probe L12 N "$LD/L12.tsv" "$SRC/matched.md"      "malformed 3-col row"
probe L13 N "$LD/L13.tsv" "$SRC/traversal.md"    "traversal vault path"
probe L14 R "$LD/L14.tsv" "$SRC/canary.env"      "secret-shaped refusal"
probe L15 N "$LD/L15.tsv" "$SRC/matched.md"      "vault path is a dir"
probe L17 I "$LD/L17.tsv" "$SRC/samepath.md"     "source==vault path"
probe L18 V "$LD/L18.tsv" "$SRC/future.md"       "future mtime"
probe L19 V "$LD/L19.tsv" "$SRC/emptypair.md"    "empty pair, empty digest"
probe L20 N "$LD/L20.tsv" "$SRC/mode000.md"      "mode 000 vault file"
probe L21 I "$LD/L21.tsv" "$SRC/matched.md"      "vault symlink to real file"
probe L22 N "$LD/L22.tsv" "$SRC/matched.md"      "symlink loop (no hang)"
probe L23 N "$LD/L23.tsv" "$SRC/matched.md"      "fifo vault (no hang)"
probe L24 I "$LD/L24.tsv" "$SRC/matched.md"      "dup rows good-then-bad"
probe L25 I "$LD/L25.tsv" "$SRC/matched.md"      "dup rows bad-then-good"
probe L26 I "$LD/L26.tsv" "$SRC/crlfpair.md"     "crlf ledger file"
probe L27 N "$LD/L27-missing.tsv" "$SRC/matched.md" "ledger file missing"
probe L29 V "$LD/L29.tsv" "$SRC/meeting notes 2026-10.md" "space-bearing names"
probe L30 N "$LD/L30.tsv" "$SRC/crlfpair.md"     "crlf-truncated row"
probe L31 V "$LD/L31.tsv" "$SRC/matched.md"      "5-col row (exported_at absent)"
probe L32 I "$LD/L32.tsv" "$SRC/dirpair"         "dir pair, dir digests"
probe L33 V "$LD/L33.tsv" "$SRC/matched.md"      "no trailing newline"

# ---- real-vault probes (read-only): Home.md known content ---------------
RV="$W/realledger"; mkdir -p "$RV"
HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
mkled() { # mkled <file> <rows...>
  local f=$1; shift
  { printf '%s\n' "$HDR"; local r; for r in "$@"; do printf '%b\n' "$r"; done; } > "$f"
}
SHA_HOME=$(sha256sum "$REALVAULT/Home.md" 2>/dev/null | cut -d' ' -f1)
SP_HOME="$SRC/real-home.md"; cp "$REALVAULT/Home.md" "$SP_HOME" 2>/dev/null
mkled "$RV/RV1.tsv" "$SP_HOME\t$SHA_HOME\t$REALVAULT/Home.md\t$SHA_HOME\t2026-10-18\treal-match"
mkled "$RV/RV2.tsv" "$SP_HOME\t$SHA_HOME\t$REALVAULT/Home.md\t0000000000000000000000000000000000000000000000000000000000000000\t2026-10-18\treal-wrong-hash"
probe RV1 V "$RV/RV1.tsv" "$SP_HOME" "REAL vault Home.md match (read-only)"
probe RV2 N "$RV/RV2.tsv" "$SP_HOME" "REAL vault wrong hash control"
probe RV3 I "$LD/L6.tsv"  "$REALVAULT/Home.md" "REAL vault target, header-only ledger"

# L28: no SOUJI_LEDGER override -> must default to the live ledger and must
# not modify it (checked against LL_BEFORE/LL_AFTER below)
OUT28=$(env -u SOUJI_LEDGER -u OBSIDIAN_LEDGER timeout 30 bash "$IMPL" "$SRC/matched.md" 2>&1); RC28=$?
IFS='|' read -r cls28 v28 r28 ev28 <<<"$(classify "$OUT28")"
P28=0; [ "$cls28" = N ] && P28=1
printf 'L28\tN\t%s\t%s\t%s\t%s\t%s\tdefault-ledger (%s)\n' "$cls28" "$v28" "$r28" "$P28" "$RC28" "${ev28:0:120}" >> "$TSV"

# R5: strace write audit — no writes outside /tmp sandbox and the lane must not
# be written (ledger, repo) during a full evaluation run
TRACE="$OUT/strace.log"
strace -f -e trace=openat,open,unlink,unlinkat,rename,renameat -o "$TRACE" \
  env SOUJI_LEDGER="$LD/L1.tsv" timeout 30 bash "$IMPL" -- "$SRC/matched.md" >/dev/null 2>&1
R5_BAD=$(grep -E 'O_WRONLY|O_RDWR|O_CREAT|unlink|rename' "$TRACE" 2>/dev/null \
  | grep -vE '/tmp/|/dev/null|/dev/tty|/dev/pts|ENOENT' \
  | grep -vE '"/proc/|"/sys/' | grep -c . || true)
R5=0; [ "${R5_BAD:-0}" = 0 ] && R5=1
printf 'R5\trails\t%s\twrite-audit-outside-tmp\t\t%s\t0\tbad_write_lines=%s\n' rails "$R5" "$R5_BAD" >> "$TSV"
grep -E 'O_WRONLY|O_RDWR|O_CREAT|unlink|rename' "$TRACE" 2>/dev/null | head -20 >> "$OUT/raw.log"

# ---- rails checks ----------------------------------------------------------
vault_fp2=$(vault_fp)
LL_AFTER=$(sha256sum "$LIVE_LEDGER" | cut -d' ' -f1)
W_AFTER=$(find "$W" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1)
POISON_LINES=$(wc -l < "$POISON")
R1=0; [ "$V_BEFORE" = "$vault_fp2" ] && R1=1
R2=0; [ "$LL_BEFORE" = "$LL_AFTER" ] && R2=1
R3=0; [ "$POISON_LINES" = 0 ] && R3=1
R4=0; [ "$W_BEFORE" = "$W_AFTER" ] && R4=1
printf 'R1\trails\t%s\tvault-unchanged\t\t%s\t0\t%s->%s\n' rails "$R1" "$V_BEFORE" "$vault_fp2" >> "$TSV"
printf 'R2\trails\t%s\tlive-ledger-unchanged\t\t%s\t0\t%s\n' rails "$R2" "$LL_BEFORE" >> "$TSV"
printf 'R3\trails\t%s\tno-gui-spawn\t\t%s\t0\tpoison_lines=%s\n' rails "$R3" "$POISON_LINES" >> "$TSV"
printf 'R4\trails\t%s\tworld-unchanged\t\t%s\t0\t%s\n' rails "$R4" "$W_BEFORE" >> "$TSV"

# selftest
ST_OUT=$(timeout 300 bash "$IMPL" --selftest 2>&1); ST_RC=$?
printf '### selftest rc=%s\n%s\n' "$ST_RC" "$ST_OUT" >> "$OUT/raw.log"
printf 'ST\tselftest\t%s\tselftest\t\t%s\t%s\t%s\n' \
  "$([ "$ST_RC" = 0 ] && echo PASS || echo FAIL)" \
  "$([ "$ST_RC" = 0 ] && echo 1 || echo 0)" "$ST_RC" "$(printf '%s' "$ST_OUT" | tail -1 | cut -c1-160)" >> "$TSV"

# summary
awk -F'\t' 'NR>1 && $2!="selftest"{t++; if($6==1)p++} END{printf "PROBES %d/%d\n", p+0, t+0}' "$TSV" >> "$OUT/meta.txt"
printf 'impl=%s sha=%s mode=%s\n' "$IMPL" "$IMPL_SHA" "$IMPL_MODE" >> "$OUT/meta.txt"
echo "battery done: $TSV"
