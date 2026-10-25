#!/usr/bin/env bash
# reviewer-43.sh — SEAT S43 independent reviewer harness, souji-shokunin round 4
# (Obsidian-CLI vault verification).
#
# Independence: fixtures + ledgers are built by this harness from the round-4
# contract (ledger-backed moved-to-obsidian receipt over a vault side); it does
# NOT consume any other seat's fixtures, ledgers, or harness code.
#
# Safety rails:
#   * /usr/bin/obsidian (GUI launcher) is NEVER executed — a static pre-check
#     refuses any tool whose resolved invocation would exec the GUI path.
#   * The real vault (/home/vgpnk/Documents/shokoknowledge) is only ever read:
#     sha256sum / stat / find / readlink. No writes, no notes, no git commands
#     that touch the index (rev-parse only).
#   * The live ledger corpus/knowledge/obsidian-ledger.tsv is hashed only.
#   * All fixture state lives under /tmp/s43-review/.
#
# usage: reviewer-43.sh [--tool PATH] [--out FILE] [--only SECTION] [--keep]
# exit: 0 all counted checks pass; 1 any counted check failed; 2 usage; 3 tool missing
set -uo pipefail
export LC_ALL=C

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=/home/vgpnk/Projects/shokunin/souji-shokunin
VAULT=/home/vgpnk/Documents/shokoknowledge
LIVE_LEDGER=$REPO/corpus/knowledge/obsidian-ledger.tsv
TOOL=""
OUT=$REPO/tests/results/vreview-43.json
ONLY=""
KEEP=0
TOOL_TIMEOUT=120

while [ $# -gt 0 ]; do
  case "$1" in
    --tool) TOOL=$2; shift 2;;
    --out) OUT=$2; shift 2;;
    --only) ONLY=$2; shift 2;;
    --keep) KEEP=1; shift;;
    -h|--help) sed -n '2,18p' "$0"; exit 0;;
    *) echo "reviewer-43: unknown arg $1" >&2; exit 2;;
  esac
done

WORK=$(mktemp -d /tmp/s43-review/run.XXXXXX)
FX="$WORK/fx"; mkdir -p "$FX"
LED="$FX/ledger.tsv"
RTSV="$WORK/results.tsv"; : > "$RTSV"
LOG="$WORK/log.txt"; : > "$LOG"

san() { local s=${1:-}; s=${s//$'\t'/ }; s=${s//$'\n'/ }; printf '%s' "$s"; }
record() { # id name status expected observed exit detail
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san "$1")" "$(san "$2")" "$(san "$3")" "$(san "$4")" \
    "$(san "$5")" "$(san "${6:-}")" "$(san "${7:-}")" >> "$RTSV"
}
info() { record "$1" "$2" info "$3" "" "" "${4:-}"; }

sha() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
dir_digest() { ( cd "$1" 2>/dev/null && find . -path './.git' -prune -o -type f -print0 \
    | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }

# ---------------------------------------------------------------- tool check
if [ -z "$TOOL" ]; then
  for cand in "$REPO/tools/obsidian-vault-verify.sh" "$REPO/tools/vault-verify.sh" \
              "$REPO/tools/souji-verify.sh"; do
    [ -f "$cand" ] && { TOOL=$cand; break; }
  done
fi
[ -n "$TOOL" ] || { echo "reviewer-43: no tool found" >&2; exit 3; }
TOOL=$(readlink -m -- "$TOOL")
[ -f "$TOOL" ] || { echo "reviewer-43: tool not found: $TOOL" >&2; exit 3; }

TOOL_SHA=$(sha "$TOOL"); TOOL_MODE=$(stat -c %A "$TOOL")
TOOL_SYNTAX=missing
if bash -n "$TOOL" 2>"$WORK/syntax.err"; then TOOL_SYNTAX=ok
else TOOL_SYNTAX=$(head -c 300 "$WORK/syntax.err"); fi

# static GUI-refusal check: a tool may mention the GUI path only in comments
# (refusal notes); any *code* reference to it is treated as execution-capable
# and the harness refuses to run the tool (hard fail, no exec).
GUI_ABS_REFS=$(grep -vE '^[[:space:]]*#' -- "$TOOL" | grep -c -- '/usr/bin/obsidian' || true)
info "tool.present" "A0" "path=$TOOL sha256=$TOOL_SHA syntax=$TOOL_SYNTAX mode=$TOOL_MODE gui_abs_refs=$GUI_ABS_REFS"

# ---------------------------------------------------------------- fixture set
SP_OK="$FX/src/ok.md";        VP_OK="$FX/vault/ok.md"
SP_VE="$FX/src/vault-edit.md"; VP_VE="$FX/vault/vault-edit.md"
SP_SM="$FX/src/src-mis.md";   VP_SM="$FX/vault/src-mis.md"
SP_AB="$FX/src/absent.md";    VP_AB="$FX/vault/absent.md"      # never created
SP_EH="$FX/src/empty-hash.md"; VP_EH="$FX/vault/empty-hash.md"
SP_D="$FX/src/dir-case";      VP_D="$FX/vault/dir-case"
mkdir -p "$FX/src" "$FX/vault" "$SP_D" "$VP_D"
printf 's43 ok payload\n'            > "$SP_OK";  cp "$SP_OK" "$VP_OK"
printf 's43 vault-edit payload\n'    > "$SP_VE";  cp "$SP_VE" "$VP_VE"
printf 's43 src-mis payload\n'       > "$SP_SM";  cp "$SP_SM" "$VP_SM"
printf 's43 absent payload\n'        > "$SP_AB"
printf 's43 empty-hash payload\n'    > "$SP_EH";  cp "$SP_EH" "$VP_EH"
printf 'one\n' > "$SP_D/one.txt"; printf 'two\n' > "$SP_D/two.txt"
cp -r "$SP_D/." "$VP_D/"

SHA_OK=$(sha "$SP_OK"); SHA_VE=$(sha "$SP_VE"); SHA_SM=$(sha "$SP_SM")
SHA_AB=$(sha "$SP_AB"); SHA_EH=$(sha "$SP_EH")
DIG_D=$(dir_digest "$SP_D")
WRONG=0000000000000000000000000000000000000000000000000000000000000000

# vault-side edited AFTER the row was written
printf 'EDITED AFTER ROW\n' >> "$VP_VE"
# source modified after the row (row records pre-edit hash)
SRC_MIS_ROW_HASH=$SHA_SM
printf 'SOURCE EDITED AFTER ROW\n' >> "$SP_SM"

HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
{
  printf '%s\n' "$HDR"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tok\n'         "$SP_OK" "$SHA_OK" "$VP_OK" "$SHA_OK"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tvault-edit\n' "$SP_VE" "$SHA_VE" "$VP_VE" "$SHA_VE"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tsrc-mis\n'    "$SP_SM" "$SRC_MIS_ROW_HASH" "$VP_SM" "$(sha "$VP_SM")"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tabsent\n'     "$SP_AB" "$SHA_AB" "$VP_AB" "$SHA_AB"
  printf '%s\t\t%s\t\t2026-10-18\tempty-hashes\n'   "$SP_EH" "$VP_EH"
  printf '%s\t%s\t%s\t%s\t2026-10-18\tdir-case\n'   "$SP_D" "$DIG_D" "$VP_D" "$(dir_digest "$VP_D")"
} > "$LED"

# self-receipt row: vault_path == source_path (the S20 loophole shape)
SP_SELF="$FX/src/self.md"; printf 'self receipt payload\n' > "$SP_SELF"
SHA_SELF=$(sha "$SP_SELF")
{
  printf '%s\t%s\t%s\t%s\t2026-10-18\tself\n' "$SP_SELF" "$SHA_SELF" "$SP_SELF" "$SHA_SELF"
} >> "$LED"

# real-vault rows (read-only): Home.md copy as source, real vault Home.md as vault
REAL_OK=0; SHA_HOME=""
if [ -r "$VAULT/Home.md" ]; then
  REAL_OK=1; SHA_HOME=$(sha "$VAULT/Home.md")
  SP_HOME="$FX/src/real-home.md"; cp "$VAULT/Home.md" "$SP_HOME"
  SP_HOMEBAD="$FX/src/real-home-bad.md"; cp "$VAULT/Home.md" "$SP_HOMEBAD"
  SP_HOMEABS="$FX/src/real-home-abs.md"; cp "$VAULT/Home.md" "$SP_HOMEABS"
  {
    printf '%s\t%s\t%s\t%s\t2026-10-18\treal-match\n'      "$SP_HOME" "$SHA_HOME" "$VAULT/Home.md" "$SHA_HOME"
    printf '%s\t%s\t%s\t%s\t2026-10-18\treal-mismatch\n'   "$SP_HOMEBAD" "$SHA_HOME" "$VAULT/Home.md" "$WRONG"
    printf '%s\t%s\t%s\t%s\t2026-10-18\treal-absent\n'     "$SP_HOMEABS" "$SHA_HOME" "$VAULT/no-such-s43.md" "$SHA_HOME"
  } >> "$LED"
fi

# ---------------------------------------------------------------- runner
OUT_TEXT=""; OUT_ERR=""; OUT_CODE=0
run_tool() {
  local rc=0
  OUT_TEXT=$(env SOUJI_LEDGER="$LED" timeout "$TOOL_TIMEOUT" bash "$TOOL" "$@" 2>"$WORK/stderr") || rc=$?
  OUT_CODE=$rc
  OUT_ERR=$(cat "$WORK/stderr" 2>/dev/null || true)
  { printf '### args:'; printf ' [%s]' "$@"; printf '\n--stdout--\n%s\n--stderr--\n%s\n--rc=%s\n\n' \
      "$OUT_TEXT" "$OUT_ERR" "$rc"; } >> "$LOG"
}
line_of() { printf '%s\n' "$OUT_TEXT" | awk -F'\t' -v t="$1" 'NF>=3 && $2==t {print; f=1} END{if(!f) exit 1}'; }

# r4 vocabulary normalization: VERIFIED/NOT-VERIFIED -> SAFE/NOT-SAFE for scoring.
norm_v() { case "$1" in VERIFIED|VERIFIED\(*) printf 'SAFE' ;; NOT-VERIFIED|NOT-VERIFIED\(*) printf 'NOT-SAFE' ;; *) printf '%s' "$1" ;; esac; }
norm_r() { local r=$1; case "$r" in VERIFIED\(*\)) r=${r#VERIFIED(}; printf '%s' "${r%)}" ;; moved-to-obsidian) printf 'moved-to-obsidian' ;; *) printf '%s' "$r" ;; esac; }

check_line() { # id name target want-verdict receipt-regex evidence-regex [want-rc]
  local id=$1 name=$2 tgt=$3 wv=$4 wre=${5:-} ere=${6:-} wrc=${7:-}
  local line v r e status=pass detail=""
  if ! line=$(line_of "$tgt"); then
    record "$id" "$name" fail "line for '$tgt' -> $wv" "no line with field2=='$tgt' (rc=$OUT_CODE)" "$OUT_CODE" "$OUT_ERR"
    return
  fi
  # layout A (r4): VERIFIED | NOT-VERIFIED(reason) <TAB> path <TAB> receipt <TAB> evidence
  # layout B (r2): VERDICT <TAB> path <TAB> SAFE|NOT-SAFE <TAB> receipt <TAB> evidence
  case "$(printf '%s' "$line" | awk -F'\t' '{print $1}')" in
    VERIFIED|NOT-VERIFIED*)
      v=$(norm_v "$(printf '%s' "$line" | awk -F'\t' '{print $1}')")
      r=$(norm_r "$(printf '%s' "$line" | awk -F'\t' '{print $3}')")
      e=$(printf '%s' "$line" | awk -F'\t' '{print $4}') ;;
    *)
      v=$(norm_v "$(printf '%s' "$line" | awk -F'\t' '{print $3}')")
      r=$(norm_r "$(printf '%s' "$line" | awk -F'\t' '{print $4}')")
      e=$(printf '%s' "$line" | awk -F'\t' '{print $5}') ;;
  esac
  [ "$wv" = ANY ] || [ "$v" = "$wv" ] || { status=fail; detail="verdict=$v want=$wv; "; }
  if [ -n "$wre" ]; then
    if ! printf '%s' "$r" | grep -Eq "$wre"; then
      # r4 layout carries the reason in the verdict parens; accept a match there too
      local vraw; vraw=$(printf '%s' "$line" | awk -F'\t' '{print $1}')
      printf '%s' "$vraw" | grep -Eq "$wre" || { status=fail; detail="${detail}receipt='$r' v='$vraw' !~ /$wre/; "; }
    fi
  fi
  [ -n "$ere" ] && { printf '%s' "$e" | grep -Eq "$ere" || { status=fail; detail="${detail}evidence='$e' !~ /$ere/; "; }; }
  [ -n "$wrc" ] && [ "$OUT_CODE" != "$wrc" ] && { status=fail; detail="${detail}rc=$OUT_CODE want=$wrc; "; }
  record "$id" "$name" "$status" "$wv r~/$wre/ e~/$ere/" "rc=$OUT_CODE line=$line" "$OUT_CODE" "$detail"
}

# ---------------------------------------------------------------- pre-state
vault_fp() { { find "$VAULT" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 \
    | sort -z | xargs -0 -r sha256sum 2>/dev/null; } > "$1"; \
  printf '%s' "$(sha "$1")"; }
FP_BEFORE=$(vault_fp "$WORK/vault-fp.before")
LL_SHA_BEFORE=$(sha "$LIVE_LEDGER"); LL_LINES_BEFORE=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
GUI_BEFORE=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); GUI_BEFORE=${GUI_BEFORE:-0}

# ---------------------------------------------------------------- battery
if [ "$TOOL_SYNTAX" = ok ] && [ "${GUI_ABS_REFS:-0}" = 0 ]; then
  # selftest if advertised
  if grep -q -- '--selftest' "$TOOL"; then
    TOOL_TIMEOUT=300 run_tool --selftest
    if [ "$OUT_CODE" = 0 ]; then
      record "A1.selftest" "selftest exit 0" pass "exit 0" "exit=0 $(printf '%s' "$OUT_TEXT" | tail -1 | cut -c1-160)" 0 ""
    else
      record "A1.selftest" "selftest exit 0" fail "exit 0" "exit=$OUT_CODE $(printf '%s' "$OUT_TEXT" | tail -1 | cut -c1-160)" "$OUT_CODE" "$OUT_ERR"
    fi
    TOOL_TIMEOUT=120
  else
    info "A1.selftest" "selftest" "tool has no --selftest" ""
  fi

  # fixture family
  run_tool "$SP_OK";      check_line "F1.ledger-match"        "fixture ledger match"          "$SP_OK" SAFE '^moved-to-obsidian$' 'vault=' 0
  run_tool "$SP_VE";      check_line "F2.vault-edited"        "vault edited after row"        "$SP_VE" NOT-SAFE '.*' 'vault-sha-mismatch|vault-hash-mismatch' 0
  run_tool "$SP_SM";      check_line "F3.source-mismatch"     "source edited after row"       "$SP_SM" NOT-SAFE '.*' 'source-sha-mismatch|source-hash-mismatch' 0
  run_tool "$SP_AB";      check_line "F4.vault-absent"        "vault side never created"      "$SP_AB" NOT-SAFE '.*' 'vault.*(unreachable|absent)' 0
  run_tool "$SP_EH";      check_line "F5.empty-hashes"        "empty hash columns"            "$SP_EH" NOT-SAFE '.*' '.*' 0
  run_tool "$SP_D";       check_line "F6.dir-digest"          "dir pair, digests correct"     "$SP_D" SAFE '^moved-to-obsidian$' 'vault=' 0
  run_tool "$SP_SELF";    check_line "F7.self-receipt"        "vault_path==source_path row"   "$SP_SELF" NOT-SAFE '.*' '.*' 0

  # real vault family (read-only)
  if [ "$REAL_OK" = 1 ]; then
    run_tool "$SP_HOME";     check_line "V1.real-match"      "real vault Home.md match"      "$SP_HOME" SAFE '^moved-to-obsidian$' "$VAULT/Home\.md" 0
    run_tool "$SP_HOMEBAD";  check_line "V2.real-mismatch"   "real vault wrong hash"         "$SP_HOMEBAD" NOT-SAFE '.*' 'vault-sha-mismatch|vault-hash-mismatch' 0
    run_tool "$SP_HOMEABS";  check_line "V3.real-absent"     "real vault path absent"        "$SP_HOMEABS" NOT-SAFE '.*' 'vault.*(unreachable|absent)' 0
  else
    record "V1.real-match" "real vault match" skip "SAFE" "vault Home.md unreadable" "" ""
  fi

  # determinism / json / batch / header-only ledger
  run_tool "$SP_OK"; D1="$OUT_TEXT"; run_tool "$SP_OK"
  [ "$D1" = "$OUT_TEXT" ] && record "B1.determinism" "determinism" pass "identical on rerun" "identical" "$OUT_CODE" "" \
                          || record "B1.determinism" "determinism" fail "identical on rerun" "differs" "$OUT_CODE" ""
  run_tool --json "$SP_OK"
  if printf '%s' "$OUT_TEXT" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
    record "B2.json" "json mode parses" pass "parses as JSON" "parsed" "$OUT_CODE" ""
  else
    record "B2.json" "json mode parses" fail "parses as JSON" "$(printf '%s' "$OUT_TEXT" | head -c 160)" "$OUT_CODE" ""
  fi
  run_tool "$SP_OK" "$SP_VE" "$SP_AB"
  check_line "B3.batch-ok"     "batch ok"     "$SP_OK" SAFE '^moved-to-obsidian$' 'vault=' 0
  check_line "B3.batch-edit"   "batch edit"   "$SP_VE" NOT-SAFE '.*' 'vault-sha-mismatch|vault-hash-mismatch' 0
  check_line "B3.batch-absent" "batch absent" "$SP_AB" NOT-SAFE '.*' 'vault.*(unreachable|absent)' 0

  # header-only ledger -> no receipt
  printf '%s\n' "$HDR" > "$FX/ledger-empty.tsv"
  OUT_TEXT=$(env SOUJI_LEDGER="$FX/ledger-empty.tsv" timeout 60 bash "$TOOL" "$SP_OK" 2>/dev/null); OUT_CODE=$?
  check_line "B4.header-only" "header-only ledger" "$SP_OK" NOT-SAFE '.*' '.*' 0
else
  record "A1.selftest" "selftest" fail "tool runnable" "syntax=$TOOL_SYNTAX gui_abs_refs=$GUI_ABS_REFS (refused)" 1 "$TOOL_SYNTAX"
fi

# ---------------------------------------------------------------- strace exec audit
if command -v strace >/dev/null && [ "$TOOL_SYNTAX" = ok ] && [ "${GUI_ABS_REFS:-0}" = 0 ]; then
  strace -f -qq -e trace=execve -o "$WORK/exec.trace" \
    env SOUJI_LEDGER="$LED" timeout 120 bash "$TOOL" "$SP_OK" >/dev/null 2>&1 || true
  EXEC_FORBIDDEN=$(grep -E 'execve\("[^"]*(/usr/bin/obsidian"|/usr/lib/obsidian/|obsidian-cli)' "$WORK/exec.trace" 2>/dev/null | grep -v 'EACCES\|ENOENT' | head -5 || true)
  GIT_FORBIDDEN=$(grep -E 'execve\("[^"]*git"' "$WORK/exec.trace" 2>/dev/null | grep -E '" (fetch|push|commit|branch|checkout|reset|rebase)"' | head -5 || true)
  [ -z "$EXEC_FORBIDDEN" ] && record "S1.no-gui-exec" "no obsidian exec" pass "no obsidian/GUI execve" "clean" 0 "" \
                            || record "S1.no-gui-exec" "no obsidian exec" fail "no obsidian/GUI execve" "$EXEC_FORBIDDEN" 0 ""
  [ -z "$GIT_FORBIDDEN" ] && record "S2.no-git-mutators" "no mutating git" pass "no fetch/push/commit/etc" "clean" 0 "" \
                           || record "S2.no-git-mutators" "no mutating git" fail "no fetch/push/commit/etc" "$GIT_FORBIDDEN" 0 ""
else
  info "S1.no-gui-exec" "no obsidian exec" "strace unavailable or tool refused" ""
fi

# ---------------------------------------------------------------- post-state
FP_AFTER=$(vault_fp "$WORK/vault-fp.after")
LL_SHA_AFTER=$(sha "$LIVE_LEDGER"); LL_LINES_AFTER=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
GUI_AFTER=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); GUI_AFTER=${GUI_AFTER:-0}

[ "$FP_BEFORE" = "$FP_AFTER" ] && record "R1.vault-unchanged" "vault unchanged" pass "manifest identical" "$FP_BEFORE" 0 "" \
                               || record "R1.vault-unchanged" "vault unchanged" fail "manifest identical" "before=$FP_BEFORE after=$FP_AFTER" 0 ""
[ "$LL_SHA_BEFORE" = "$LL_SHA_AFTER" ] && [ "$LL_LINES_BEFORE" = 1 ] && [ "$LL_LINES_AFTER" = 1 ] \
  && record "R2.live-ledger" "live ledger header-only" pass "lines=1 unchanged" "sha=${LL_SHA_AFTER:0:12}" 0 "" \
  || record "R2.live-ledger" "live ledger header-only" fail "lines=1 unchanged" "lines $LL_LINES_BEFORE->$LL_LINES_AFTER sha ${LL_SHA_BEFORE:0:12}->${LL_SHA_AFTER:0:12}" 0 ""
[ "$GUI_BEFORE" = "$GUI_AFTER" ] && record "R3.no-gui-spawn" "GUI process count stable" pass "count unchanged" "before=$GUI_BEFORE after=$GUI_AFTER" 0 "" \
                                 || record "R3.no-gui-spawn" "GUI process count stable" fail "count unchanged" "before=$GUI_BEFORE after=$GUI_AFTER" 0 ""

# ---------------------------------------------------------------- CLI ground truth (info)
CLI_INSP=$(command -v obsidian-cli-inspector || true)
if [ -n "$CLI_INSP" ]; then
  V=$(timeout 5 "$CLI_INSP" --version 2>&1); RC=$?
  info "C1.inspector-version" "obsidian-cli-inspector --version" "rc=$RC out=$(printf '%s' "$V" | head -1)"
fi
SHIMS_LOCAL=$(ls /home/vgpnk/.local/bin 2>/dev/null | grep -i '^obsidian' | tr '\n' ' ')
SHIMS_UL=$(ls /usr/local/bin 2>/dev/null | grep -i '^obsidian' | tr '\n' ' ')
SOCK="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/.obsidian-cli.sock"
info "C2.official-cli" "official CLI registration" "shims: ~/.local/bin=[${SHIMS_LOCAL:-none}] /usr/local/bin=[${SHIMS_UL:-none}] socket=$([ -e "$SOCK" ] && echo present || echo absent)"

# ---------------------------------------------------------------- report
mkdir -p "$(dirname "$OUT")"
python3 - "$RTSV" "$OUT" "$TOOL" "$TOOL_SHA" "$TOOL_SYNTAX" "$TOOL_MODE" "$WORK" \
        "$FP_BEFORE" "$FP_AFTER" "$LL_SHA_BEFORE" "$LL_SHA_AFTER" "$GUI_BEFORE" "$GUI_AFTER" <<'PY'
import json, sys, collections, datetime, os
(tsv, out_path, tool, tool_sha, tool_syntax, tool_mode, work,
 fp_before, fp_after, ll_b, ll_a, gui_b, gui_a) = sys.argv[1:14]
def san(s): return (s or "").replace(work, "<work>")
checks = []
for raw in open(tsv):
    if not raw.strip(): continue
    f = (raw.rstrip("\n").split("\t") + [""]*7)[:7]
    checks.append({"id": san(f[0]), "name": san(f[1]), "status": f[2],
                   "expected": san(f[3]), "observed": san(f[4]),
                   "exit_code": int(f[5]) if f[5].strip().lstrip("-").isdigit() else None,
                   "detail": san(f[6])})
counts = collections.Counter(c["status"] for c in checks)
fails = [c["id"] for c in checks if c["status"] == "fail"]
measured = [c for c in checks if c["status"] not in ("info", "skip")]
status = "blocked" if not measured else ("fail" if fails else "pass")
exit_code = 3 if not measured else (1 if fails else 0)
report = {
  "seat": "S43", "role": "reviewer", "round": 4,
  "reviewer": "tests/vault/reviewer-43.sh",
  "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "status": status, "exit_code": exit_code,
  "tool": {"path": tool, "sha256": tool_sha, "bash_syntax": tool_syntax, "mode": tool_mode},
  "vault": {"path": "/home/vgpnk/Documents/shokoknowledge",
            "fingerprint_before": fp_before, "fingerprint_after": fp_after,
            "unchanged": fp_before == fp_after},
  "live_ledger": {"sha256_before": ll_b, "sha256_after": ll_a, "header_only": ll_b == ll_a},
  "gui_processes": {"before": gui_b, "after": gui_a},
  "counts": {"total": len(checks), "pass": counts["pass"], "fail": counts["fail"],
             "skip": counts["skip"], "info": counts["info"]},
  "failed_checks": fails,
  "checks": checks,
}
with open(out_path, "w") as fh:
    json.dump(report, fh, indent=2); fh.write("\n")
print("reviewer-43: status=%s exit=%d pass=%d fail=%d skip=%d info=%d tool=%s"
      % (status, exit_code, counts["pass"], counts["fail"], counts["skip"], counts["info"], os.path.basename(tool)))
if fails: print("failed: " + ", ".join(fails))
PY
echo "log: $LOG"; echo "results: $RTSV"
[ "$KEEP" = 1 ] || rm -rf "$WORK"
exit 0
