#!/usr/bin/env bash
# runner-30-r4.sh — SEAT S30 supplementary runner: round-4 candidate matrix.
#
# The "identical" runner (runner-30.sh -> vrun-30.json) verified the installed
# r2 tool (tools/souji-verify.sh) against the vault/ledger contract. This
# harness runs the same ground-truth matrix against the round-4 CANDIDATES
# (tools/*vault*.sh, tools/impl-*.sh) with contract normalization:
#   VERIFIED == SAFE ; NOT-VERIFIED(*) == NOT-SAFE ; VERDICT<tab>...<tab>SAFE == SAFE.
# It also exercises the --cli path with a mock `obsidian-cli` (honest /
# lying / hanging) and a launcher-shaped-CLI refusal probe. The GUI launcher
# /usr/bin/obsidian is NEVER executed or named as a runnable target; a mock
# whose content mentions the app bundle is used and it only ever writes a
# marker file if some tool actually executes it.
#
# Read-only over the real vault; all fixtures under /tmp; writes only
# tests/results/vrun-30-r4.json + tests/vault/s30-r4-raw/**.
#
# usage: tests/vault/runner-30-r4.sh [--keep]
# exit: 0 always (results are data); the JSON carries per-candidate status.
set -uo pipefail
export LC_ALL=C

SELF_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$SELF_DIR/../.." && pwd)
VAULT=/home/vgpnk/Documents/shokoknowledge
OUT="$ROOT/tests/results/vrun-30-r4.json"
RAW="$ROOT/tests/vault/s30-r4-raw"
KEEP=0
[ "${1:-}" = "--keep" ] && KEEP=1
mkdir -p "$RAW"

W=$(mktemp -d /tmp/souji30r4.XXXXXX)
cleanup() { [ "$KEEP" = 1 ] || rm -rf "$W"; }
trap cleanup EXIT
mkdir -p "$W/src" "$W/vault" "$W/mockbin"

say() { printf '%s\n' "$*"; }

# ---------------------------------------------------------------- fixtures
printf 'r4c payload kept\n'  > "$W/src/kept.md"
cp "$W/src/kept.md" "$W/vault/kept.md"
printf 'r4c payload stale\n' > "$W/src/stale.md"
cp "$W/src/stale.md" "$W/vault/stale.md"
printf 'r4c payload mis\n'   > "$W/src/mis.md"
cp "$W/src/mis.md" "$W/vault/mis.md"
printf 'r4c payload abs\n'   > "$W/src/abs.md"
printf 'r4c payload nonl\n'  > "$W/src/nonl.md"
printf 'r4c payload crlf\n'  > "$W/src/crlf.md"
cp "$W/src/crlf.md" "$W/vault/crlf.md"

SHA_KEPT=$(sha256sum "$W/src/kept.md" | cut -d' ' -f1)
SHA_STALE=$(sha256sum "$W/src/stale.md" | cut -d' ' -f1)
SHA_STALE_VAULT_ROW=$(sha256sum "$W/vault/stale.md" | cut -d' ' -f1)
SHA_MIS=$(sha256sum "$W/src/mis.md" | cut -d' ' -f1)
SHA_MIS_WRONG=1111111111111111111111111111111111111111111111111111111111111111
SHA_ABS=$(sha256sum "$W/src/abs.md" | cut -d' ' -f1)
SHA_NONL=$(sha256sum "$W/src/nonl.md" | cut -d' ' -f1)
SHA_CRLF=$(sha256sum "$W/src/crlf.md" | cut -d' ' -f1)

HDR='source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'

LEDGER="$W/ledger.tsv"
{
  printf "$HDR\n"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tkept\n'   "$W/src/kept.md"  "$SHA_KEPT"  "$W/vault/kept.md"  "$SHA_KEPT"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tstale\n'  "$W/src/stale.md" "$SHA_STALE" "$W/vault/stale.md" "$SHA_STALE_VAULT_ROW"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tmis\n'    "$W/src/mis.md"   "$SHA_MIS_WRONG" "$W/vault/mis.md" "$SHA_MIS"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tabs\n'    "$W/src/abs.md"   "$SHA_ABS"   "$W/vault/abs.md"   "$SHA_ABS"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tcrlf\r\n' "$W/src/crlf.md"  "$SHA_CRLF"  "$W/vault/crlf.md"  "$SHA_CRLF"
} > "$LEDGER"
printf 'EDIT AFTER ROW\n' >> "$W/vault/stale.md"

# nonl: valid single row, NO trailing newline (conservative NOT-SAFE acceptable)
LEDGER_NONL="$W/ledger-nonl.tsv"
{
  printf "$HDR\n"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tunterminated' "$W/src/nonl.md" "$SHA_NONL" "$W/src/nonl.md" "$SHA_NONL"
} > "$LEDGER_NONL"

# real-vault rows: source is a COPY of the real vault file (so the source
# hash equals the vault hash), vault side read-only
SHA_HOME=""
[ -r "$VAULT/Home.md" ] && SHA_HOME=$(sha256sum "$VAULT/Home.md" | cut -d' ' -f1)
LEDGER_REAL="$W/ledger-real.tsv"
LEDGER_REAL_BAD="$W/ledger-real-bad.tsv"
if [ -n "$SHA_HOME" ]; then
  cp "$VAULT/Home.md" "$W/src/real.md"
  cp "$VAULT/Home.md" "$W/src/real2.md"
  {
    printf "$HDR\n"
    printf '%s\t%s\t%s\t%s\t2026-10-18\treal-match\n' "$W/src/real.md" "$SHA_HOME" "$VAULT/Home.md" "$SHA_HOME"
  } > "$LEDGER_REAL"
  # separate ledger: ONE row, vault hash deliberately wrong (isolated case)
  {
    printf "$HDR\n"
    printf '%s\t%s\t%s\t%s\t2026-10-18\treal-mismatch\n' "$W/src/real2.md" "$SHA_HOME" "$VAULT/Home.md" "$SHA_MIS_WRONG"
  } > "$LEDGER_REAL_BAD"
fi

# ------------------------------------------------------------- mock CLI
# Honest mock named `obsidian-cli` (the asar-declared CLI binary name; a mock
# named `obsidian` would be — correctly — refused by several tools as the
# GUI launcher name). It never launches anything; it logs and prints a claim.
cat > "$W/mockbin/obsidian-cli" <<'EOF'
#!/usr/bin/env bash
MOCK_LOG=${MOCK_LOG:-/tmp/s30-mock.log}
{ flock 9; printf '%s\t%s\n' "${MOCK_MODE:-honest}" "$*" >>"$MOCK_LOG"; } 9>>"$MOCK_LOG" 2>/dev/null || true
mode=${MOCK_MODE:-honest}
case "$mode" in
  hang) sleep 600; exit 0 ;;
  error) printf 'mock: cli error\n' >&2; exit 3 ;;
  garbage) printf 'not-a-hash\n'; exit 0 ;;
  empty) exit 0 ;;
esac
f=""
for a in "$@"; do [ -f "$a" ] && f=$a; done
if [ "$mode" = lying ]; then h=${MOCK_LIE_HASH:-0000000000000000000000000000000000000000000000000000000000000000}
elif [ -n "$f" ]; then h=$(sha256sum -- "$f" 2>/dev/null | cut -d' ' -f1)
else h=""; fi
printf '{"path":"%s","sha256":"%s"}\n' "$f" "$h"
printf 'sha256 %s %s\n' "$f" "$h"
EOF
chmod +x "$W/mockbin/obsidian-cli"
# Launcher-shaped mock: textually references the electron app bundle (with
# the exact signature impl-21's content guard looks for) so a tool's
# launcher-refusal (unread) logic can trigger. If a tool EXECUTES it, it
# writes a marker (and still launches nothing).
cat > "$W/mockbin/obsidian-gui-shape" <<EOF
#!/usr/bin/env bash
# shaped like /usr/bin/obsidian: references the electron app bundle
OBSIDIAN_USER_FLAGS_FILE="\${XDG_CONFIG_HOME:-\$HOME/.config}/obsidian/user-flags.conf"
touch "$W/gui-shape-executed.marker"
exec electron43 /usr/lib/obsidian/app.asar "\$@"
EOF
chmod +x "$W/mockbin/obsidian-gui-shape"

# --------------------------------------------------- vault read-only guard
vault_fp() {
  { find "$VAULT" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 \
      | sort -z | xargs -0 -r sha256sum 2>/dev/null; } > "$1" 2>/dev/null || true
  printf 'files=%s manifest_sha=%s\n' "$(grep -c . "$1" 2>/dev/null || true)" \
    "$(sha256sum "$1" 2>/dev/null | cut -d' ' -f1)"
}
FP_BEFORE=$(vault_fp "$W/fp.before")
LIVE_LEDGER="$ROOT/corpus/knowledge/obsidian-ledger.tsv"
LL_BEFORE=$(sha256sum "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1)
GUI_BEFORE=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); GUI_BEFORE=${GUI_BEFORE:-0}

RTSV="$W/results.tsv"; : > "$RTSV"
san() { local s=${1:-}; s=${s//$'\t'/\\t}; s=${s//$'\n'/\\n}; printf '%s' "$s"; }
record() { printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(san "$1")" "$(san "$2")" "$(san "$3")" "$(san "$4")" "$(san "$5")" "$(san "${6:-}")" "$(san "${7:-}")" >> "$RTSV"; }

# normalize any of the observed contracts to SAFE / NOT-SAFE / OTHER
norm() { # $1 raw output line
  local l=$1 f3
  case "$l" in
    VERDICT$'\t'*)
      f3=$(printf '%s' "$l" | cut -f3)
      case "$f3" in
        SAFE) printf 'SAFE' ;;
        NOT-SAFE) printf 'NOT-SAFE' ;;
        *) printf 'OTHER' ;;
      esac
      return ;;
  esac
  case "$l" in
    VERIFIED|VERIFIED$'\t'*|VERIFIED\(*) printf 'SAFE' ;;
    NOT-VERIFIED|NOT-VERIFIED$'\t'*|NOT-VERIFIED\(*) printf 'NOT-SAFE' ;;
    SAFE|SAFE$'\t'*) printf 'SAFE' ;;
    NOT-SAFE|NOT-SAFE$'\t'*) printf 'NOT-SAFE' ;;
    *) printf 'OTHER' ;;
  esac
}
line1() { printf '%s\n' "$1" | grep -Ev '^#|^souji-verify: cli=|^cli:' | grep -E '^(VERDICT|VERIFIED|NOT-VERIFIED|SAFE|NOT-SAFE)' | sed -n '1p'; }
mocklines() { [ -f "$1" ] && grep -c . "$1" 2>/dev/null || printf '0'; }

CANDIDATES=()
add_cand() { [ -f "$1" ] && CANDIDATES+=("$1"); }
for f in "$ROOT"/tools/*vault*.sh "$ROOT"/tools/impl-*.sh; do
  case "$f" in *"$ROOT"/tools/impl-21.sh) continue ;; esac   # handled via /tmp copy (exec-bit)
  add_cand "$f"
done
if [ -f "$ROOT/tools/impl-21.sh" ]; then
  cp "$ROOT/tools/impl-21.sh" "$W/impl-21.sh"; chmod +x "$W/impl-21.sh"; CANDIDATES+=("$W/impl-21.sh")
fi
CANDIDATES+=("$ROOT/tools/souji-verify.sh")

# tools.tsv for the report
TOOLS_TSV="$W/tools.tsv"; : > "$TOOLS_TSV"
for t in "${CANDIDATES[@]}"; do
  printf '%s\t%s\t%s\n' "$(basename "$t")" "$(sha256sum "$t" | cut -d' ' -f1)" \
    "$(bash -n "$t" 2>/dev/null && echo ok || echo syntax-error)" >> "$TOOLS_TSV"
done

say "candidates:"; printf '  %s\n' "${CANDIDATES[@]}"

run_case() { # tool id name ledger target want [extra flags...]
  local tool=$1 id=$2 name=$3 led=$4 tgt=$5 want=$6; shift 6
  local out rc=0
  out=$(env SOUJI_LEDGER="$led" SHOKUNIN_ROOT="$W" timeout 30 bash "$tool" "$@" "$tgt" 2>&1) || rc=$?
  local l; l=$(line1 "$out")
  local v; v=$(norm "$l")
  local res=FAIL
  case "$want" in
    ANY) { [ "$v" = SAFE ] || [ "$v" = NOT-SAFE ]; } && [ "$rc" != 124 ] && res=PASS ;;
    *)   [ "$v" = "$want" ] && [ "$rc" != 124 ] && res=PASS ;;
  esac
  record "$(basename "$tool")" "$id" "$name" "$res" "want=$want got=$v rc=$rc" "$l" "flags:${*:-none}"
  printf '%-34s %-6s %-4s %-8s %s\n' "$(basename "$tool")" "$id" "$res" "$v" "$name"
  printf '### %s %s (want=%s got=%s rc=%s)\n%s\n' "$id" "$name" "$want" "$v" "$rc" "$out" >> "$RAW/$(basename "$tool").out"
}

for tool in "${CANDIDATES[@]}"; do
  tn=$(basename "$tool")
  : > "$RAW/$tn.out"
  say ""
  say "== $tn (sha256 $(sha256sum "$tool" | cut -d' ' -f1 | cut -c1-16)) =="

  st_rc=0; st_out=$(timeout 200 bash "$tool" --selftest 2>&1) || st_rc=$?
  record "$tn" "ST" "selftest" "$([ "$st_rc" = 0 ] && echo PASS || echo FAIL)" "rc=$st_rc" "$(printf '%s' "$st_out" | tail -2 | tr '\n' ' ')" ""
  printf '%-34s %-6s %-4s %s\n' "$tn" "ST" "$([ "$st_rc" = 0 ] && echo PASS || echo FAIL)" "selftest rc=$st_rc"
  printf '### selftest rc=%s\n%s\n' "$st_rc" "$(printf '%s' "$st_out" | tail -6)" >> "$RAW/$tn.out"

  run_case "$tool" M1 "ledger match"               "$LEDGER" "$W/src/kept.md"  SAFE
  run_case "$tool" M2 "vault edited after row"     "$LEDGER" "$W/src/stale.md" NOT-SAFE
  run_case "$tool" M3 "source sha mismatch"        "$LEDGER" "$W/src/mis.md"   NOT-SAFE
  run_case "$tool" M4 "vault absent"               "$LEDGER" "$W/src/abs.md"   NOT-SAFE
  run_case "$tool" M5 "no ledger row"              "$LEDGER" "$W/src/nonl.md"  NOT-SAFE
  run_case "$tool" M6 "no ledger file"             "$W/none.tsv" "$W/src/kept.md" NOT-SAFE
  run_case "$tool" M7 "crlf row matches"           "$LEDGER" "$W/src/crlf.md"  SAFE
  run_case "$tool" M8 "nonl row (either direction ok)" "$LEDGER_NONL" "$W/src/nonl.md" ANY
  if [ -n "$SHA_HOME" ]; then
    run_case "$tool" M9  "real vault match"        "$LEDGER_REAL" "$W/src/real.md" SAFE
    run_case "$tool" M10 "real vault mismatch"     "$LEDGER_REAL_BAD" "$W/src/real2.md" NOT-SAFE
  fi
  rc2=0; timeout 15 bash "$tool" --bogus-flag x >/dev/null 2>&1 || rc2=$?
  record "$tn" "M11" "unknown flag exit 2" "$([ "$rc2" = 2 ] && echo PASS || echo FAIL)" "rc=$rc2" "" ""
  printf '%-34s %-6s %-4s %s\n' "$tn" "M11" "$([ "$rc2" = 2 ] && echo PASS || echo FAIL)" "unknown flag rc=$rc2"

  # CLI path only for tools that declare --cli; others recorded as skip.
  if grep -q -- '--cli' "$tool"; then
    for mode in honest lying hang; do
      mlog="$W/mock.$mode.$tn.log"; : > "$mlog"
      mrc=0
      mout=$(env PATH="$W/mockbin:$PATH" MOCK_LOG="$mlog" MOCK_MODE="$mode" \
             SOUJI_CLI="$W/mockbin/obsidian-cli" SOUJI_CLI_TIMEOUT=3 \
             SOUJI_LEDGER="$LEDGER" timeout 25 bash "$tool" --cli "$W/src/kept.md" 2>&1) || mrc=$?
      mv=$(norm "$(line1 "$mout")")
      case "$mode" in
        honest) want=SAFE ;;      # local receipt holds; CLI may only add a note
        lying)  want=ANY ;;       # disagreement recorded OR conservative degrade
        hang)   want=ANY ;;       # CLI bounded by timeout; must not hang (rc!=124)
      esac
      res=FAIL
      case "$want" in
        ANY) { [ "$mv" = SAFE ] || [ "$mv" = NOT-SAFE ]; } && [ "$mrc" != 124 ] && res=PASS ;;
        *)   [ "$mv" = "$want" ] && [ "$mrc" != 124 ] && res=PASS ;;
      esac
      record "$tn" "CLI-$mode" "mock cli $mode (bounded)" "$res" \
        "want=$want got=$mv rc=$mrc mock_calls=$(mocklines "$mlog")" "$(line1 "$mout")" ""
      printf '%-34s %-9s %-4s %-8s %s\n' "$tn" "CLI-$mode" "$res" "$mv" "rc=$mrc calls=$(mocklines "$mlog")"
      printf '### CLI-%s (want=%s got=%s rc=%s calls=%s)\n%s\n' "$mode" "$want" "$mv" "$mrc" "$(mocklines "$mlog")" "$mout" >> "$RAW/$tn.out"
    done
    # launcher-shaped hint: the tool must not execute it (marker stays absent)
    rm -f "$W/gui-shape-executed.marker"
    gui_rc=0
    gui_out=$(env PATH="$W/mockbin:$PATH" SOUJI_CLI="$W/mockbin/obsidian-gui-shape" \
              SOUJI_LEDGER="$LEDGER" timeout 20 bash "$tool" --cli "$W/src/kept.md" 2>&1) || gui_rc=$?
    gui_now=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); gui_now=${gui_now:-0}
    gv=$(norm "$(line1 "$gui_out")")
    if [ -e "$W/gui-shape-executed.marker" ]; then
      gres=FAIL; gdet="launcher-shaped CLI was EXECUTED (marker present)"
    elif [ "$gui_now" != "$GUI_BEFORE" ]; then
      gres=FAIL; gdet="app process delta $GUI_BEFORE->$gui_now"
    elif [ "$gv" = OTHER ]; then
      gres=FAIL; gdet="verdict OTHER"
    else
      gres=PASS; gdet="not executed; verdict=$gv"
    fi
    record "$tn" "GUI" "launcher-shaped SOUJI_CLI refused/not-executed" "$gres" \
      "verdict=$gv rc=$gui_rc $gdet" "$(line1 "$gui_out")" ""
    printf '%-34s %-9s %-4s %-8s %s\n' "$tn" "GUI" "$gres" "$gv" "$gdet"
    printf '### GUI (rc=%s %s)\n%s\n' "$gui_rc" "$gdet" "$gui_out" >> "$RAW/$tn.out"
  else
    for id in CLI-honest CLI-lying CLI-hang GUI; do
      record "$tn" "$id" "no --cli contract" "skip" "tool declares no --cli" "" ""
    done
  fi
done

# ------------------------------------------------------------- post checks
FP_AFTER=$(vault_fp "$W/fp.after")
LL_AFTER=$(sha256sum "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1)
GUI_AFTER=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); GUI_AFTER=${GUI_AFTER:-0}
VAULT_OK=false; [ "$FP_BEFORE" = "$FP_AFTER" ] && VAULT_OK=true
LEDGER_OK=false; [ "$LL_BEFORE" = "$LL_AFTER" ] && LEDGER_OK=true
GUI_OK=false; [ "$GUI_BEFORE" = "$GUI_AFTER" ] && GUI_OK=true
record "guard" "G1" "real vault untouched" "$([ "$VAULT_OK" = true ] && echo PASS || echo FAIL)" "$FP_BEFORE -> $FP_AFTER" "" ""
record "guard" "G2" "live ledger untouched" "$([ "$LEDGER_OK" = true ] && echo PASS || echo FAIL)" "$LL_BEFORE -> $LL_AFTER" "" ""
record "guard" "G3" "no GUI process spawned" "$([ "$GUI_OK" = true ] && echo PASS || echo FAIL)" "$GUI_BEFORE -> $GUI_AFTER" "" ""

# ------------------------------------------------------------- report
python3 - "$RTSV" "$OUT" "$RAW" "$W" "$FP_BEFORE" "$FP_AFTER" "$LL_BEFORE" "$LL_AFTER" \
        "$GUI_BEFORE" "$GUI_AFTER" "$TOOLS_TSV" <<'PY'
import json, sys, datetime, os, glob

(tsv, out, raw, work, fp_b, fp_a, ll_b, ll_a, gui_b, gui_a, tools_tsv) = sys.argv[1:12]

tool_hashes = {}
for line in open(tools_tsv):
    f = line.rstrip("\n").split("\t")
    if len(f) >= 3:
        tool_hashes[f[0]] = {"sha256": f[1], "bash_syntax": f[2]}

rows = []
for line in open(tsv):
    if not line.strip():
        continue
    f = (line.rstrip("\n").split("\t") + [""] * 7)[:7]
    rows.append({"tool": f[0], "id": f[1], "name": f[2], "status": f[3],
                 "observed": f[4].replace(work, "<work>"),
                 "line": f[5].replace(work, "<work>"),
                 "detail": f[6].replace(work, "<work>")})

by_tool = {}
for r in rows:
    by_tool.setdefault(r["tool"], []).append(r)
summary = {}
for t, rs in by_tool.items():
    measured = [r for r in rs if r["status"] in ("PASS", "FAIL")]
    fails = [r["id"] for r in measured if r["status"] == "FAIL"]
    summary[t] = {"pass": sum(1 for r in measured if r["status"] == "PASS"),
                  "fail": len(fails), "failed_ids": fails}

doc = {
 "seat": "S30", "role": "vault-runner (supplementary)", "round": 4,
 "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
 "purpose": "round-4 candidate matrix: same ground-truth vault/ledger cases against every candidate tool, contract-normalized",
 "normalization": {"SAFE": ["VERIFIED", "VERIFIED(*)", "VERDICT<tab>..<tab>SAFE", "SAFE"],
                   "NOT-SAFE": ["NOT-VERIFIED(*)", "VERDICT<tab>..<tab>NOT-SAFE", "NOT-SAFE"],
                   "OTHER": "anything else"},
 "tool_hashes": tool_hashes,
 "guards": {"vault_fingerprint_before": fp_b, "vault_fingerprint_after": fp_a,
            "vault_unchanged": fp_b == fp_a,
            "live_ledger_before": ll_b, "live_ledger_after": ll_a,
            "live_ledger_unchanged": ll_b == ll_a,
            "gui_procs_before": int(gui_b or 0), "gui_procs_after": int(gui_a or 0),
            "no_gui_spawn": gui_b == gui_a},
 "summary": summary,
 "checks": rows,
 "raw_outputs": sorted(os.path.basename(p) for p in glob.glob(os.path.join(raw, "*.out"))),
}
with open(out, "w") as fh:
    json.dump(doc, fh, indent=2); fh.write("\n")
print("wrote", out)
PY

say ""
say "== summary =="
python3 - "$OUT" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
for t, s in d["summary"].items():
    tag = ("FAILED: " + ",".join(s["failed_ids"])) if s["failed_ids"] else ""
    print("%-34s pass=%-3d fail=%-3d %s" % (t, s["pass"], s["fail"], tag))
print("guards: vault_unchanged=%s live_ledger_unchanged=%s no_gui_spawn=%s" % (
    d["guards"]["vault_unchanged"], d["guards"]["live_ledger_unchanged"], d["guards"]["no_gui_spawn"]))
PY
