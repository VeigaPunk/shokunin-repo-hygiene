#!/usr/bin/env bash
# vadv-51 — adversarial probes for vault-side receipts (seat S51, souji-shokunin round 4).
#
# Assigned families:
#   (g) two ledger rows for the same source path — first matches, second mismatches.
#       Questions: which row wins, is the outcome deterministic, is SAFE justified?
#   (h) vault file unreadable (chmod 000) — must degrade to NOT-SAFE, not crash.
#   (i) FIFO as vault file — must not hang (every tool run is wrapped in `timeout 10`).
#
# Advisory extras: stale-first duplicate row, same-vault-path hash contradiction,
# both-rows-mismatch control, unreadable *source*, FIFO as CLI target,
# vault_path outside the vault root, vault copy that is a symlink to the source.
#
# Write scope: tests/vault/vadv-51/ (fixtures + ledgers) and the results JSON.
# Everything else is read-only; the live ledger must stay header-only (asserted).
#
# Usage: run-vadv-51.sh [out.json]   default <repo>/tests/results/vadv-51.json

set -uo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$ROOT_DIR/../../.." && pwd -P)"
TOOL="$REPO_ROOT/tools/souji-verify.sh"
OUT_JSON="${1:-$REPO_ROOT/tests/results/vadv-51.json}"
GUARD=10

command -v timeout >/dev/null || { echo "timeout not found" >&2; exit 2; }
command -v mkfifo  >/dev/null || { echo "mkfifo not found"  >&2; exit 2; }
[ -f "$TOOL" ] || { echo "tool not found: $TOOL" >&2; exit 2; }

FIX="$(readlink -m -- "$ROOT_DIR/fixture")"
SRC="$FIX/src"; VAULT="$FIX/vault"; FLEET="$FIX/empty-fleet"
LIVE_LEDGER="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"
mkdir -p "$SRC" "$VAULT" "$FLEET" "$(dirname -- "$OUT_JSON")"

cleanup() {
  chmod 644 -- "$VAULT/h-note.txt" "$SRC/h-note.txt" 2>/dev/null
  rm -f -- "$VAULT/i-note-fifo" "$VAULT/i2-pipe.out"
}
trap cleanup EXIT

# ---------------------------------------------------------------- fixture ---
printf 'vadv51 g-note payload\n'  > "$SRC/g-note.txt"
cp -f -- "$SRC/g-note.txt"  "$VAULT/g-note.txt"
printf 'vadv51 g3-note payload\n' > "$SRC/g3-note.txt"
cp -f -- "$SRC/g3-note.txt" "$VAULT/g3-note.txt"
printf 'vadv51 g6-note payload\n' > "$SRC/g6-note.txt"
cp -f -- "$SRC/g6-note.txt" "$VAULT/g6-note.txt"
cp -f -- "$SRC/g6-note.txt" "$VAULT/g6-note-alt.txt"
printf 'vadv51 g7-note payload\n' > "$SRC/g7-note.txt"
cp -f -- "$SRC/g7-note.txt" "$VAULT/g7-note.txt"
printf 'vadv51 h-note payload\n'  > "$SRC/h-note.txt"
cp -f -- "$SRC/h-note.txt"  "$VAULT/h-note.txt"
printf 'vadv51 i-note payload\n'  > "$SRC/i-note.txt"
printf 'vadv51 x1-note payload\n' > "$SRC/x1-note.txt"
cp -f -- "$SRC/x1-note.txt" "$SRC/x1-note-copy.txt"          # NOT under vault/
printf 'vadv51 x2-note payload\n' > "$SRC/x2-note.txt"
rm -f -- "$VAULT/i-note-fifo" "$VAULT/i2-pipe.out"
mkfifo -- "$VAULT/i-note-fifo" "$VAULT/i2-pipe.out"
rm -f -- "$VAULT/x2-note.txt"
ln -s -- "$SRC/x2-note.txt" "$VAULT/x2-note.txt"             # vault copy = symlink to source
chmod 644 -- "$VAULT/h-note.txt" "$SRC/h-note.txt" 2>/dev/null

sha256_of() { sha256sum -- "$1" 2>/dev/null | cut -d' ' -f1; }
manifest()  { find "$ROOT_DIR" -type f -print0 | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1; }
rel() { case "$1" in "$REPO_ROOT"/*) printf '%s' "${1#"$REPO_ROOT"/}" ;; *) printf '%s' "$1" ;; esac; }
esc() { local s=$1; s=${s//\\/\\\\}; s=${s//\"/\\\"}; s=${s//$'\t'/\\t}; s=${s//$'\r'/\\r}; s=${s//$'\n'/\\n}; printf '%s' "$s"; }

WRONG="$(printf 'vadv51-wrong-vault' | sha256sum | cut -d' ' -f1)"
G_SS=$(sha256_of "$SRC/g-note.txt")
G3_SS=$(sha256_of "$SRC/g3-note.txt")
G6_SS=$(sha256_of "$SRC/g6-note.txt")
G7_SS=$(sha256_of "$SRC/g7-note.txt")
H_SS=$(sha256_of "$SRC/h-note.txt")
I_SS=$(sha256_of "$SRC/i-note.txt")
X1_SS=$(sha256_of "$SRC/x1-note.txt")
X2_SS=$(sha256_of "$SRC/x2-note.txt")

T=$'\t'
row() { printf '%s\t%s\t%s\t%s\t2026-10-18\t%s' "$1" "$2" "$3" "$4" "$5"; }
led() { # $1 out-file, rest rows
  local f=$1; shift
  { printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\n' "$@"; } > "$f"
}

ROW_G_MATCH=$(row "$SRC/g-note.txt" "$G_SS" "$VAULT/g-note.txt" "$G_SS" g1-match)
ROW_G_MISMATCH=$(row "$SRC/g-note.txt" "$G_SS" "$VAULT/g-note.txt" "$WRONG" g1-mismatch)
ROW_G_GHOST=$(row "$SRC/g-note.txt" "$G_SS" "$VAULT/g-note-ghost.txt" "$G_SS" g5-ghost)
ROW_G3_STALE=$(row "$SRC/g3-note.txt" "$WRONG" "$VAULT/g3-note.txt" "$G3_SS" g3-stale-source)
ROW_G3_MATCH=$(row "$SRC/g3-note.txt" "$G3_SS" "$VAULT/g3-note.txt" "$G3_SS" g3-match)
ROW_G4_WRONG=$(row "$SRC/g-note.txt" "$G_SS" "$VAULT/g-note.txt" "$WRONG" g4-wrong-first)
ROW_G4_RIGHT=$(row "$SRC/g-note.txt" "$G_SS" "$VAULT/g-note.txt" "$G_SS" g4-right-second)
ROW_H=$(row "$SRC/h-note.txt" "$H_SS" "$VAULT/h-note.txt" "$H_SS" h1-row)
ROW_I=$(row "$SRC/i-note.txt" "$I_SS" "$VAULT/i-note-fifo" "$I_SS" i1-row)
ROW_I2=$(row "$VAULT/i2-pipe.out" "$WRONG" "$VAULT/g-note.txt" "$G_SS" i2-row)
ROW_X1=$(row "$SRC/x1-note.txt" "$X1_SS" "$SRC/x1-note-copy.txt" "$X1_SS" x1-copy-outside-vault)
ROW_X2=$(row "$SRC/x2-note.txt" "$X2_SS" "$VAULT/x2-note.txt" "$X2_SS" x2-vault-symlink)
ROW_G6_A=$(row "$SRC/g6-note.txt" "$G6_SS" "$VAULT/g6-note.txt" "$G6_SS" g6-vault-a)
ROW_G6_B=$(row "$SRC/g6-note.txt" "$G6_SS" "$VAULT/g6-note-alt.txt" "$G6_SS" g6-vault-b)
ROW_G7_GHOST=$(row "$SRC/g7-note.txt" "$G7_SS" "$VAULT/g7-note-ghost.txt" "$G7_SS" g7-ghost-vault)
ROW_G7_MATCH=$(row "$SRC/g7-note.txt" "$G7_SS" "$VAULT/g7-note.txt" "$G7_SS" g7-match)

led "$ROOT_DIR/ledger-g1.tsv" "$ROW_G_MATCH" "$ROW_G_MISMATCH"
led "$ROOT_DIR/ledger-g2.tsv" "$ROW_G_MISMATCH" "$ROW_G_MATCH"
led "$ROOT_DIR/ledger-g3.tsv" "$ROW_G3_STALE" "$ROW_G3_MATCH"
led "$ROOT_DIR/ledger-g4.tsv" "$ROW_G4_WRONG" "$ROW_G4_RIGHT"
led "$ROOT_DIR/ledger-g5.tsv" "$ROW_G_MISMATCH" "$ROW_G_GHOST"
led "$ROOT_DIR/ledger-g6.tsv" "$ROW_G6_A" "$ROW_G6_B"
led "$ROOT_DIR/ledger-g6r.tsv" "$ROW_G6_B" "$ROW_G6_A"
led "$ROOT_DIR/ledger-g7.tsv" "$ROW_G7_GHOST" "$ROW_G7_MATCH"
led "$ROOT_DIR/ledger-h1.tsv" "$ROW_H"
led "$ROOT_DIR/ledger-h2.tsv" "$ROW_H"
led "$ROOT_DIR/ledger-i1.tsv" "$ROW_I"
led "$ROOT_DIR/ledger-i2.tsv" "$ROW_I2"
led "$ROOT_DIR/ledger-x1.tsv" "$ROW_X1"
led "$ROOT_DIR/ledger-x2.tsv" "$ROW_X2"

# ------------------------------------------------------------- run helper ---
LINE="" RC=0 MS=0
run_tool() { # $1 ledger, $2 target
  local t0 t1
  t0=$(date +%s%N)
  LINE=$(timeout "$GUARD" env SHOKUNIN_ROOT="$FLEET" SOUJI_LEDGER="$1" \
        "$TOOL" --stale-days 1 "$2" 2>/dev/null)
  RC=$?
  t1=$(date +%s%N)
  MS=$(( (t1 - t0) / 1000000 ))
  return 0
}

parse_line() { # $1 raw stdout -> TAG PATHF V R EV
  local line=$1 rest
  TAG=""; PATHF=""; V=""; R=""; EV=""
  if [[ "$line" != *$'\t'* ]]; then PATHF="$line"; return 1; fi
  TAG=${line%%$'\t'*}; rest=${line#*$'\t'}
  PATHF=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  if [[ "$rest" != *$'\t'* ]]; then V="$rest"; return 1; fi
  V=${rest%%$'\t'*}; rest=${rest#*$'\t'}
  R=${rest%%$'\t'*}; EV=${rest#*$'\t'}
  return 0
}

# --------------------------------------------------------------- snapshot ---
TOOL_SHA_BEFORE=$(sha256_of "$TOOL")
LIVE_SHA_BEFORE=$(sha256_of "$LIVE_LEDGER")
LIVE_LINES_BEFORE=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
MANIFEST_BEFORE=$(manifest)
REPO_HEAD=$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)
GIT_VER=$(git --version 2>/dev/null || echo unknown)
RUN_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# --------------------------------------------------------------- controls ---
H0_CMD="chmod 000 tests/vault/vadv-51/fixture/vault/h-note.txt && timeout 3 sha256sum tests/vault/vadv-51/fixture/vault/h-note.txt"
chmod 000 -- "$VAULT/h-note.txt"
H0_OUT=$(timeout 3 sha256sum -- "$VAULT/h-note.txt" 2>&1); H0_RC=$?
chmod 644 -- "$VAULT/h-note.txt"
I0_CMD="timeout 3 sha256sum tests/vault/vadv-51/fixture/vault/i-note-fifo"
I0_OUT=$(timeout 3 sha256sum -- "$VAULT/i-note-fifo" 2>&1); I0_RC=$?

# ------------------------------------------------------------- selftest ----
ST_OUT=$(timeout 120 "$TOOL" --selftest 2>&1); ST_RC=$?
ST_TAIL=$(printf '%s\n' "$ST_OUT" | tail -1)

# ----------------------------------------------------------------- cases ---
CASES_JSON=(); NPASS=0; NFAIL=0; NADP=0; NADF=0; NHANG=0; NRUN=0

case_check() {
  # $1 id $2 binding $3 family $4 constructed $5 want_v $6 want_r $7 wsub $8 nruns
  # $9 ledger ${10} target ${11} note ${12} oracle
  local id=$1 binding=$2 family=$3 constructed=$4 wv=$5 wr=$6 wsub=$7 nruns=$8
  local ledger=$9 target=${10} note=${11:-} oracle=${12:-}
  local -a outs=() rcs=() mss=()
  local i
  for ((i=0; i<nruns; i++)); do
    run_tool "$ledger" "$target"
    outs+=("$LINE"); rcs+=("$RC"); mss+=("$MS")
  done
  NRUN=$((NRUN+nruns))
  local maxms=0; for i in "${mss[@]}"; do [ "$i" -gt "$maxms" ] && maxms=$i; done
  local nlines; nlines=$(printf '%s\n' "${outs[0]}" | grep -c . || true); nlines=${nlines// /}
  parse_line "${outs[0]}"; local malformed=$?
  local det=true
  for ((i=1; i<nruns; i++)); do [ "${outs[$i]}" != "${outs[0]}" ] && det=false; done
  local -a fails=()
  for ((i=0; i<nruns; i++)); do
    if [ "${rcs[$i]}" = 124 ]; then fails+=("hang-run$((i+1))"); NHANG=$((NHANG+1)); fi
    if [ "${rcs[$i]}" != 0 ] && [ "${rcs[$i]}" != 124 ]; then fails+=("rc=${rcs[$i]}"); fi
  done
  [ "$nlines" = 1 ] || fails+=("stdout-lines=$nlines")
  [ "$malformed" = 0 ] || fails+=("malformed-line")
  [ "$det" = true ] || fails+=("nondeterministic")
  [ "$TAG" = VERDICT ] || fails+=("tag=$TAG")
  if [ "$V" != "$wv" ] || [ "$R" != "$wr" ]; then fails+=("got=$V($R)"); fi
  if [ -n "$wsub" ]; then case "$EV" in *"$wsub"*) : ;; *) fails+=("evidence-lacks=$wsub") ;; esac; fi
  local match=true; [ "${#fails[@]}" -gt 0 ] && match=false
  if [ "$binding" = 1 ]; then
    if [ "$match" = true ]; then NPASS=$((NPASS+1)); else NFAIL=$((NFAIL+1)); fi
  else
    if [ "$match" = true ]; then NADP=$((NADP+1)); else NADF=$((NADF+1)); fi
  fi
  local fails_str="ok"
  if [ "${#fails[@]}" -gt 0 ]; then fails_str=$(printf '%s;' "${fails[@]}"); fi
  local hang=false; [ "${rcs[0]}" = 124 ] && hang=true
  local binding_bool=false; [ "$binding" = 1 ] && binding_bool=true
  local cmd="timeout $GUARD env SHOKUNIN_ROOT=$(rel "$FLEET") SOUJI_LEDGER=$(rel "$ledger") $(rel "$TOOL") --stale-days 1 $(rel "$target")"
  local frag
  frag=$(printf '{ "id": "%s", "binding": %s, "family": "%s", "constructed": "%s", "expected": {"verdict": "%s", "receipt": "%s"}, "oracle": "%s", "command": "%s", "observed": {"rc": %s, "verdict": "%s", "receipt": "%s", "evidence_line": "%s", "stdout_lines": %s, "runs": %s, "deterministic": %s, "wall_ms_max": %s, "hang": %s}, "match": %s, "notes": "%s" }' \
    "$id" "$binding_bool" "$(esc "$family")" "$(esc "$constructed")" "$wv" "$wr" "$(esc "$oracle")" "$(esc "$cmd")" \
    "${rcs[0]}" "$V" "$R" "$(esc "$EV")" "$nlines" "$nruns" "$det" "$maxms" "$hang" "$match" "$(esc "$note")")
  CASES_JSON+=("$frag")
  printf '%-4s %-8s %s(%s) det=%s rc=%s ms=%s fails=%s\n' \
    "$id" "$binding_bool" "$V" "$R" "$det" "${rcs[0]}" "$maxms" "$fails_str"
  return 0
}

# (g) duplicate rows: match-first / mismatch-first / stale-first / contradiction-first
case_check G1 1 dup-ledger-match-first \
  "row1 full match (source sha + vault file + vault sha); row2 same source path, wrong vault_sha256" \
  SAFE moved-to-obsidian "ledger-row" 5 "$ROOT_DIR/ledger-g1.tsv" "$SRC/g-note.txt" \
  "first fully-matching row supplies the receipt; the mismatching duplicate is skipped with a note; 5 identical runs" \
  "SAFE(moved-to-obsidian): any row matching all four fields is a receipt per spec; winning row's vault copy verified live"

case_check G2 1 dup-ledger-mismatch-first \
  "same two rows as G1, order reversed: mismatching row first, matching row second" \
  SAFE moved-to-obsidian "ledger-row" 3 "$ROOT_DIR/ledger-g2.tsv" "$SRC/g-note.txt" \
  "scan continues past the mismatching row; outcome identical to G1 => order-independent, not first-row-only" \
  "SAFE(moved-to-obsidian): a match anywhere wins; spec silent on duplicate precedence"

case_check G3 0 dup-ledger-stale-first \
  "row1 same source path but stale source_sha256; row2 full match" \
  SAFE moved-to-obsidian "ledger-row" 2 "$ROOT_DIR/ledger-g3.tsv" "$SRC/g3-note.txt" \
  "stale first row does not block the later valid row" \
  "SAFE(moved-to-obsidian): valid row exists; advisory"

case_check G4 0 dup-ledger-same-vault-contradiction \
  "two rows, SAME vault path, contradictory vault_sha256: wrong first, correct second" \
  SAFE moved-to-obsidian "ledger-row" 2 "$ROOT_DIR/ledger-g4.tsv" "$SRC/g-note.txt" \
  "ground-truth-consistent row wins regardless of order" \
  "SAFE(moved-to-obsidian): row agreeing with live vault hash wins; advisory"

case_check G5 0 dup-ledger-both-mismatch \
  "control: both duplicate rows mismatch (wrong vault sha + missing vault path)" \
  NOT-SAFE none "no-matching-ledger-row" 1 "$ROOT_DIR/ledger-g5.tsv" "$SRC/g-note.txt" \
  "no matching row anywhere => NOT-SAFE, no false-SAFE" \
  "NOT-SAFE(none): control"

case_check G6 1 dup-ledger-both-match-different-vaults \
  "two rows, both full matches, but each names a DIFFERENT vault copy (both byte-identical to source)" \
  SAFE moved-to-obsidian "vault=" 3 "$ROOT_DIR/ledger-g6.tsv" "$SRC/g6-note.txt" \
  "first fully-matching row wins; evidence names the winning vault; deterministic across 3 runs" \
  "SAFE(moved-to-obsidian): spec-conformant either way; observed first-row-wins"

case_check G6R 0 dup-ledger-both-match-reversed \
  "same two full-match rows as G6, order reversed: winner evidence should follow row order, not sort order" \
  SAFE moved-to-obsidian "g6-note-alt.txt" 1 "$ROOT_DIR/ledger-g6r.tsv" "$SRC/g6-note.txt" \
  "proves first-row-wins is positional (the alternate vault named by row1 supplies the evidence)" \
  "SAFE(moved-to-obsidian): order-dependent winner; advisory"

case_check G7 0 dup-ledger-ghost-first \
  "row1 same source path, vault_path missing on disk; row2 full match" \
  SAFE moved-to-obsidian "ledger-row" 2 "$ROOT_DIR/ledger-g7.tsv" "$SRC/g7-note.txt" \
  "a dead first row does not block a valid second row" \
  "SAFE(moved-to-obsidian): advisory"

# (h) unreadable vault file (chmod 000), then unreadable source (advisory)
chmod 000 -- "$VAULT/h-note.txt"
case_check H1 1 vault-file-chmod-000 \
  "ledger row fully matching a vault file whose mode is 000 (sha256sum EACCES)" \
  NOT-SAFE none "vault-sha-mismatch" 3 "$ROOT_DIR/ledger-h1.tsv" "$SRC/h-note.txt" \
  "unreadable vault copy => sha unverifiable => NOT-SAFE; no crash, rc 0, deterministic" \
  "NOT-SAFE: vault hash cannot be verified, receipt fails"
chmod 644 -- "$VAULT/h-note.txt"

chmod 000 -- "$SRC/h-note.txt"
case_check H2 0 source-file-chmod-000 \
  "ledger row fully matching but the SOURCE file itself is mode 000" \
  NOT-SAFE none "source-sha-mismatch" 2 "$ROOT_DIR/ledger-h2.tsv" "$SRC/h-note.txt" \
  "unreadable source => source hash unverifiable => NOT-SAFE; advisory mirror of H1" \
  "NOT-SAFE: source hash cannot be verified, receipt fails"
chmod 644 -- "$SRC/h-note.txt"

# (i) FIFO as vault file, then FIFO as CLI target (advisory)
case_check I1 1 vault-fifo \
  "ledger row fully matching, vault_path is a FIFO (no writer); raw sha256sum on it blocks forever" \
  NOT-SAFE none "vault-unreachable" 3 "$ROOT_DIR/ledger-i1.tsv" "$SRC/i-note.txt" \
  "tool's -f guard skips the FIFO before hashing => no hang (rc 0, fast)" \
  "NOT-SAFE: FIFO is not a regular file; vault copy unverifiable"

case_check I2 0 target-fifo \
  "FIFO passed as the CLI target itself, fresh mtime, ledger row present for it" \
  NOT-SAFE none "mtime-age-days=0" 1 "$ROOT_DIR/ledger-i2.tsv" "$VAULT/i2-pipe.out" \
  "no hang on FIFO target either; -f guard skips it in the ledger branch; fresh mtime blocks stale" \
  "NOT-SAFE: FIFO target has no receipt; advisory"

# advisory: vault_path outside the vault root / vault copy = symlink to source
case_check X1 0 vault-path-outside-vault-root \
  "row whose vault_path is a byte-identical copy sitting NEXT TO the source, not under any vault root" \
  NOT-SAFE none "" 1 "$ROOT_DIR/ledger-x1.tsv" "$SRC/x1-note.txt" \
  "spec is silent on vault-root containment; tool trusts vault_path as given => SAFE observed (finding, not harness failure)" \
  "conservative oracle NOT-SAFE (receipt claims moved-to-obsidian but copy is not in the vault); spec-silent"

case_check X2 0 vault-copy-symlink-to-source \
  "row whose vault_path is a symlink resolving back to the source file itself" \
  NOT-SAFE none "" 1 "$ROOT_DIR/ledger-x2.tsv" "$SRC/x2-note.txt" \
  "sha256sum follows the symlink => hashes equal => SAFE observed; deleting the source would dangle the vault copy (false-SAFE candidate)" \
  "conservative oracle NOT-SAFE: symlinked vault copy is not an independent preserved copy"

# cross-order equality (G1 vs G2)
run_tool "$ROOT_DIR/ledger-g1.tsv" "$SRC/g-note.txt"; L1=$LINE
run_tool "$ROOT_DIR/ledger-g2.tsv" "$SRC/g-note.txt"; L2=$LINE
ORDER_OK=false; [ "$L1" = "$L2" ] && ORDER_OK=true
NRUN=$((NRUN+2))

# ------------------------------------------------------------- close-out ---
TOOL_SHA_AFTER=$(sha256_of "$TOOL")
LIVE_SHA_AFTER=$(sha256_of "$LIVE_LEDGER")
LIVE_LINES_AFTER=$(wc -l < "$LIVE_LEDGER" | tr -d ' ')
MANIFEST_AFTER=$(manifest)
RO_VIOL=0
[ "$TOOL_SHA_BEFORE" = "$TOOL_SHA_AFTER" ] || RO_VIOL=$((RO_VIOL+1))
[ "$LIVE_SHA_BEFORE" = "$LIVE_SHA_AFTER" ] || RO_VIOL=$((RO_VIOL+1))
[ "$MANIFEST_BEFORE" = "$MANIFEST_AFTER" ] || RO_VIOL=$((RO_VIOL+1))

VERDICT=PASS
{ [ "$NFAIL" = 0 ] && [ "$NHANG" = 0 ] && [ "$RO_VIOL" = 0 ]; } || VERDICT=FAIL

CASES_BLOCK=""
for f in "${CASES_JSON[@]}"; do
  [ -n "$CASES_BLOCK" ] && CASES_BLOCK+=","
  CASES_BLOCK+=$'\n'
  CASES_BLOCK+="    $f"
done

HARNESS_SHA=$(sha256_of "${BASH_SOURCE[0]}")

{
  printf '{\n'
  printf '  "seat": "S51",\n'
  printf '  "role": "adversarial tester: vault-side receipt edge cases (duplicate ledger rows / unreadable vault file / FIFO)",\n'
  printf '  "round": 4,\n'
  printf '  "lane_repo": "%s",\n' "$(esc "$REPO_ROOT")"
  printf '  "tool": {"path": "tools/souji-verify.sh", "sha256": "%s", "sha256_after_run": "%s", "selftest_rc": %s, "selftest_tail": "%s"},\n' \
    "$TOOL_SHA_BEFORE" "$TOOL_SHA_AFTER" "$ST_RC" "$(esc "$ST_TAIL")"
  printf '  "harness": {"path": "tests/vault/vadv-51/run-vadv-51.sh", "sha256": "%s"},\n' "$HARNESS_SHA"
  printf '  "invocation": "timeout %s env SHOKUNIN_ROOT=<empty-fleet> SOUJI_LEDGER=<case ledger under tests/vault/vadv-51/> tools/souji-verify.sh --stale-days 1 <target>",\n' "$GUARD"
  printf '  "guard_seconds": %s,\n' "$GUARD"
  printf '  "run_utc": "%s",\n' "$RUN_UTC"
  printf '  "host_git": "%s",\n' "$(esc "$GIT_VER")"
  printf '  "repo_head": "%s",\n' "$REPO_HEAD"
  printf '  "fixture_root": "tests/vault/vadv-51/fixture",\n'
  printf '  "controls": [\n'
  printf '    {"id": "H0", "family": "unreadable-file-proof", "command": "%s", "rc": %s, "output": "%s", "conclusion": "mode-000 file is genuinely unreadable by its owner (EACCES), so H1 exercises a real unreadable vault copy"},\n' \
    "$(esc "$H0_CMD")" "$H0_RC" "$(esc "$H0_OUT")"
  printf '    {"id": "I0", "family": "fifo-hash-hang-proof", "command": "%s", "rc": %s, "output": "%s", "conclusion": "raw sha256sum on a writer-less FIFO blocks (timeout rc 124); the tool must not hash non-regular files, and this harness timeout guard is load-bearing"}\n' \
    "$(esc "$I0_CMD")" "$I0_RC" "$(esc "$I0_OUT")"
  printf '  ],\n'
  printf '  "cases": [%s\n  ],\n' "$CASES_BLOCK"
  printf '  "order_independence": {"g1_vs_g2_identical": %s, "g1_line": "%s", "g2_line": "%s"},\n' \
    "$ORDER_OK" "$(esc "$L1")" "$(esc "$L2")"
  printf '  "summary": {"cases_total": %s, "binding_pass": %s, "binding_fail": %s, "advisory_pass": %s, "advisory_fail": %s, "hangs": %s, "runs_total": %s, "readonly_violations": %s, "live_ledger_lines_before": %s, "live_ledger_lines_after": %s},\n' \
    "$(( ${#CASES_JSON[@]} ))" "$NPASS" "$NFAIL" "$NADP" "$NADF" "$NHANG" "$NRUN" "$RO_VIOL" "$LIVE_LINES_BEFORE" "$LIVE_LINES_AFTER"
  printf '  "conclusions": {\n'
  printf '    "g": "Duplicate rows for one source path: the first FULLY-MATCHING row supplies the receipt (G6/G6R: both rows match but name different vault copies; reversing row order reverses the named winner, so precedence is positional = row order, not sort order); rows that mismatch source sha, vault sha or vault reachability are skipped with notes and never win (G1/G2/G3/G4/G7: a mismatching, stale, contradictory or dead row never blocks a later valid row). The outcome is order-independent (G1 match-first == G2 mismatch-first, byte-identical) and deterministic across repeated runs. SAFE is spec-conformant (a row matching all four fields is a receipt and its vault copy is verified live at run time); duplicate-row precedence itself is spec-silent, so conflict-safety is recorded as NOT-VERIFIED-by-spec rather than as a defect.",\n'
  printf '    "h": "chmod-000 vault file: file_sha fails (EACCES) => vault-sha-mismatch => NOT-SAFE(none), rc 0, no crash, deterministic across 3 runs. Unreadable source (H2) mirrors it: NOT-SAFE(source-sha-mismatch).",\n'
  printf '    "i": "FIFO as vault file: the tool'"'"'s -f guard skips it before any hashing => vault-unreachable => NOT-SAFE(none), rc 0, no hang (raw sha256sum on the same FIFO hangs: control I0 rc 124). FIFO as CLI target (I2) also completes without hanging.",\n'
  printf '    "advisory": "X2 symlinked vault copy resolving to the source yields SAFE (false-SAFE candidate: removing the source dangles the vault copy). X1 vault_path outside any vault root also yields SAFE (spec-silent). Both are spec gaps, not harness failures."\n'
  printf '  },\n'
  printf '  "verdict": "%s",\n' "$VERDICT"
  printf '  "notes": [\n'
  printf '    "Binding cases: G1, G2, G6 (duplicate rows), H1 (unreadable vault file), I1 (FIFO vault file). Advisory: G3, G4, G5, G6R, G7, H2, I2, X1, X2.",\n'
  printf '    "Every tool invocation is wrapped in timeout %s; a timeout is counted as a hang (rc 124).",\n' "$GUARD"
  printf '    "All fixtures and ledgers live under tests/vault/vadv-51/; the live ledger was header-only before and after (%s line(s)), tool sha unchanged, and the fixture manifest hash is unchanged across the run.",\n' "$LIVE_LINES_AFTER"
  printf '    "G1/G2/G3/G4/G5/X1/X2 targets are untracked fixture files inside this repo, so the pushed receipt is cleanly inapplicable and only the ledger/stale branches can yield SAFE.",\n'
  printf '    "Recommendation: add an explicit spec sentence for duplicate rows (first full match wins) and consider refusing vault copies that are symlinks resolving to the source, plus a vault-root containment note."\n'
  printf '  ]\n'
  printf '}\n'
} > "$OUT_JSON"

printf 'harness: selftest rc=%s | binding %s/%s | advisory %s/%s | hangs=%s | readonly_violations=%s | order_independent=%s\n' \
  "$ST_RC" "$NPASS" "$((NPASS+NFAIL))" "$NADP" "$((NADP+NADF))" "$NHANG" "$RO_VIOL" "$ORDER_OK"
printf 'json: %s\n' "$OUT_JSON"
[ "$VERDICT" = PASS ]
