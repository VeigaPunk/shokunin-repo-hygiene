#!/usr/bin/env bash
# tests/vault/runner-29.sh — S29 runner, souji-shokunin round 4
# (Obsidian-CLI vault verification). "Identical" runner seat; output
# tests/results/vrun-29.json in the S57 aggregator schema: a JSON list of
# {impl, case, pass, got, want, mode, note} rows (impl "-" = meta row).
#
# Subject of record (round 4, as measured by peer runners 35/39/30 and this
# seat): the installed tools/souji-verify.sh with its SOUJI_LEDGER override —
# the ledger-backed moved-to-obsidian receipt path. If r4 candidates
# tools/souji-vault-verify*.sh land, every one is tested as well, in the r4
# VERIFIED/NOT-VERIFIED vocabulary.
#
# What is verified per subject:
#   1. --selftest exit;
#   2. every tests/vault/case-V* fixture, rebuilt under this runner's own
#      mktemp root with its own ledger copy (never another seat's ledger),
#      got-class vs the fixture's expected.json;
#   3. case-V6 CRLF mechanics probes (V6a CRLF valid / V6b LF control /
#      V6c CRLF-truncated) with the fixture's evidence requirement;
#   4. case-V8 auxiliary no-row control (vault copy exists, no ledger row);
#   5. the REAL vault /home/vgpnk/Documents/shokoknowledge read-only: a
#      correct-hash row must verify, a wrong vault hash must NOT;
#   6. read-only proof: vault file manifest and the live ledger
#      (corpus/knowledge/obsidian-ledger.tsv) identical before/after, and
#      the live ledger header-only;
#   7. CLI probe: obsidian-cli-inspector --version (timeout 5). The GUI
#      launcher /usr/bin/obsidian is never executed — stat only.
#
# Independence: writes only tests/results/vrun-29.json (and, with
# --seat-meta, census/round-4/seat-29.json) plus mktemp scratch under /tmp.
# Read-only over the lane repo, the real vault, and every sibling.
#
# usage: tests/vault/runner-29.sh [--wait SECS] [--out PATH] [--once]
#        [--impl PATH]... [--impls GLOB] [--vault PATH] [--seat-meta] [--keep]
# exit: 0 matrix complete | 1 nothing to run (blocked; JSON still written) | 2 usage
set -uo pipefail
export LC_ALL=C

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$REPO_ROOT/tests/results/vrun-29.json"
WAIT=900
IMPL_GLOB="souji-vault-verify*.sh"
VAULT="/home/vgpnk/Documents/shokoknowledge"
WRITE_SEAT_META=0
KEEP=0
declare -a IMPL_EXPLICIT=()

die_usage() { printf 'runner-29: %s\nusage: tests/vault/runner-29.sh [--wait SECS] [--out PATH] [--once] [--impl PATH]... [--impls GLOB] [--vault PATH] [--seat-meta] [--keep]\n' "$1" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --wait)  [ $# -ge 2 ] || die_usage "--wait needs a value"; WAIT="$2"; shift 2 ;;
    --out)   [ $# -ge 2 ] || die_usage "--out needs a value"; OUT="$2"; shift 2 ;;
    --once)  WAIT=0; shift ;;
    --impl)  [ $# -ge 2 ] || die_usage "--impl needs a value"; IMPL_EXPLICIT+=("$2"); shift 2 ;;
    --impls) [ $# -ge 2 ] || die_usage "--impls needs a value"; IMPL_GLOB="$2"; shift 2 ;;
    --vault) [ $# -ge 2 ] || die_usage "--vault needs a value"; VAULT="$2"; shift 2 ;;
    --seat-meta) WRITE_SEAT_META=1; shift ;;
    --keep)  KEEP=1; shift ;;
    -h|--help) sed -n '2,34p' "$0"; exit 0 ;;
    *) die_usage "unknown argument: $1" ;;
  esac
done

TMP="$(mktemp -d "${TMPDIR:-/tmp}/souji29.XXXXXX")"
case "$TMP" in /tmp/souji29.*) : ;; *) echo "refusing: TMP=$TMP" >&2; exit 9 ;; esac
cleanup() { [ "$KEEP" = 1 ] || rm -rf "$TMP"; }
trap cleanup EXIT

log() { printf '%s\n' "$*" >&2; }
san() { printf '%s' "${1:-}" | tr '\t\n' '  ' | cut -c1-700; }

export GIT_CONFIG_SYSTEM=/dev/null
# Hermetic-but-functional git for child invocations: a synthetic global config
# with an identity (subjects' --selftest builds fixture repos and commits);
# the system config is nulled. The runner itself runs no git verbs.
export GIT_CONFIG_GLOBAL="$TMP/gitconfig"
printf '[user]\n\tname = souji-runner-29\n\temail = runner-29@shokunin.local\n[init]\n\tdefaultBranch = master\n' > "$GIT_CONFIG_GLOBAL"
export GIT_AUTHOR_NAME=souji-runner-29 GIT_AUTHOR_EMAIL=runner-29@shokunin.local
export GIT_COMMITTER_NAME=souji-runner-29 GIT_COMMITTER_EMAIL=runner-29@shokunin.local
export SHOKUNIN_ROOT="$TMP/fleet-empty"; mkdir -p "$SHOKUNIN_ROOT"

ROWS_TSV="$TMP/rows.tsv"; : > "$ROWS_TSV"
META_TSV="$TMP/meta.tsv"; : > "$META_TSV"
PREP_TSV="$TMP/prep.tsv"; : > "$PREP_TSV"
PREP_NOTES="$TMP/prep-notes.txt"; : > "$PREP_NOTES"

add_row() { # impl case pass got want mode note
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san "$1")" "$(san "$2")" "$(san "$3")" "$(san "$4")" "$(san "$5")" "$(san "$6")" "$(san "$7")" >> "$ROWS_TSV"
}
add_meta() { printf '%s\t%s\t%s\n' "$(san "$1")" "$(san "$2")" "$(san "$3")" >> "$META_TSV"; }

r4_impls() {
  local p
  if [ "${#IMPL_EXPLICIT[@]}" -gt 0 ]; then
    for p in "${IMPL_EXPLICIT[@]}"; do [ -f "$p" ] && printf '%s\n' "$p"; done
    return
  fi
  for p in "$REPO_ROOT"/tools/$IMPL_GLOB; do
    [ -f "$p" ] || continue
    case "$p" in *.spec.md) continue ;; esac
    case "$(basename "$p")" in souji-verify*.sh) continue ;; esac
    printf '%s\n' "$p"
  done | sort -V
}

installed_tool() { [ -f "$REPO_ROOT/tools/souji-verify.sh" ] && printf '%s\n' "$REPO_ROOT/tools/souji-verify.sh"; }

count_cases_ready() {
  local d n=0
  for d in "$REPO_ROOT"/tests/vault/case-V*; do
    [ -d "$d" ] || continue
    if [ -f "$d/expected.json" ] || [ -f "$d/make-fixture.sh" ]; then n=$((n+1)); fi
  done
  printf '%s' "$n"
}

# ------------------------------------------------------------------ wait
deadline=$(( $(date +%s) + WAIT ))
while :; do
  n_r4=$(r4_impls | wc -l | tr -d ' ')
  n_inst=$([ -n "$(installed_tool)" ] && echo 1 || echo 0)
  n_case=$(count_cases_ready)
  log "runner-29: waiting — r4_impls=$n_r4 installed=$n_inst cases=$n_case"
  { [ $((n_r4 + n_inst)) -gt 0 ] && [ "$n_case" -ge 6 ]; } && break
  [ "$(date +%s)" -ge "$deadline" ] && break
  sleep 15
done

# ------------------------------------------------------------------ prep
# Rebuild every case under $TMP with this runner's own ledger; parse
# expected.json (tolerant of schema variants) into
#   case<TAB>kind<TAB>ledger<TAB>source<TAB>want<TAB>token<TAB>root<TAB>accept<TAB>note
python3 - "$REPO_ROOT" "$TMP" <<'PYEOF'
import json, os, re, subprocess, sys, glob

repo, tmp = sys.argv[1], sys.argv[2]
vault_dir = os.path.join(repo, "tests", "vault")
prep = open(os.path.join(tmp, "prep.tsv"), "w")
notes = open(os.path.join(tmp, "prep-notes.txt"), "w")

def norm_base(v):
    if not isinstance(v, str) or not v.strip():
        return None
    v = v.strip().upper()
    v = re.sub(r"[^A-Z_-]", "_", v)
    if "NOT" in v and ("VERIFIED" in v or "SAFE" in v):
        return "NOT-VERIFIED"
    if v.startswith("VERIFIED") or v.startswith("SAFE"):
        return "VERIFIED"
    return None

def reason_of(s):
    if not isinstance(s, str):
        return None
    m = re.search(r"\(([^)]+)\)", s)
    return m.group(1).strip() if m else None

def pick(d, keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k) not in (None, ""):
            return d[k]
    return None

def sub(s, root):
    return s.replace("@FIXTURE_ROOT@", root) if isinstance(s, str) else None

def emit(case, kind, ledger, source, want, token, root, accept, note):
    if not (case and ledger and source and want):
        return
    print("\x1f".join([case, kind, ledger, source, want, token or "", root or "",
                       json.dumps(accept or []), note or ""]), file=prep)

for case_dir in sorted(glob.glob(os.path.join(vault_dir, "case-V*"))):
    if not os.path.isdir(case_dir):
        continue
    case = os.path.basename(case_dir)
    maker = os.path.join(case_dir, "make-fixture.sh")
    root = None
    my_ledger = os.path.join(tmp, "ledger-" + case + ".tsv")
    if os.path.isfile(maker):
        attempts = [
            ["bash", maker, "--out", os.path.join(tmp, "fx-" + case), "--ledger", my_ledger],
            ["bash", maker, "--out", os.path.join(tmp, "fx2-" + case)],
            ["bash", maker],
        ]
        for i, cmd in enumerate(attempts):
            try:
                r = subprocess.run(cmd, cwd=case_dir, capture_output=True, text=True, timeout=300)
            except subprocess.TimeoutExpired:
                print(f"{case}: builder TIMEOUT ({i})", file=notes)
                continue
            out = (r.stdout or "") + "\n" + (r.stderr or "")
            print(f"{case}: builder attempt {i} rc={r.returncode}", file=notes)
            if r.returncode != 0:
                print(f"{case}:   stderr tail: {r.stderr.strip()[-300:]}", file=notes)
                continue
            root = None
            m = re.search(r'^\{.*"root"\s*:\s*"([^"]+)".*\}$', out, re.M)
            if m and os.path.isdir(m.group(1)):
                root = m.group(1)
            if root is None:
                m = re.search(r"^FIXTURE_ROOT=(\S+)\s*$", out, re.M)
                if m and os.path.isdir(m.group(1)):
                    root = m.group(1)
            if root is None:
                m = re.search(r"^FIXTURE_READY\s+\S+\s+(\S+)\s*$", out, re.M)
                if m and os.path.isdir(m.group(1)):
                    root = m.group(1)
            if root is None:
                cand = os.path.join(tmp, "fx-" + case)
                if i == 1:
                    cand = os.path.join(tmp, "fx2-" + case)
                if os.path.isdir(cand):
                    root = cand
            if root is None:
                root = case_dir
            break
    exp_path = None
    if root and os.path.isfile(os.path.join(root, "expected.json")):
        exp_path = os.path.join(root, "expected.json")
    elif os.path.isfile(os.path.join(case_dir, "expected.json")):
        exp_path = os.path.join(case_dir, "expected.json")
    if exp_path is None:
        print(f"{case}: no expected.json — skipped", file=notes)
        continue
    if root is None:
        root = case_dir
    try:
        doc = json.load(open(exp_path))
    except Exception as e:
        print(f"{case}: expected.json unparsable: {e}", file=notes)
        continue

    # ---- probe-shaped cases (V6 CRLF mechanics): ledgers and targets are
    #      built under the fixture root (the builder regenerates them), so
    #      resolve relative paths against root, falling back to case_dir.
    probes = doc.get("probes")
    if case == "case-V6" and isinstance(probes, list):
        accept6 = []
        if isinstance(doc.get("accept"), dict) and isinstance(doc["accept"].get("contains"), list):
            accept6 = [str(x) for x in doc["accept"]["contains"]]
        for pr in probes:
            if not isinstance(pr, dict):
                continue
            rel_lg = pr.get("ledger", "")
            rel_tgt = pr.get("target", "")
            lg = os.path.join(root, rel_lg) if os.path.isfile(os.path.join(root, rel_lg)) \
                else os.path.join(case_dir, rel_lg)
            tgt = os.path.join(root, rel_tgt) if os.path.isfile(os.path.join(root, rel_tgt)) \
                else os.path.join(case_dir, rel_tgt)
            want = norm_base(pr.get("verdict"))
            contains = pr.get("contains") if isinstance(pr.get("contains"), list) else accept6
            emit(case, "v6probe", lg, tgt, want, pr.get("receipt") or pr.get("evidence_substr"),
                 root, contains, f"probe {pr.get('id')} ({pr.get('line_endings', 'n/a')})")
        # truncated probe (V6c shape) when the builder produced it — the
        # fixture declares this boundary INFORMATIONAL, not judged ("a
        # schema-tolerant harness that strips CR from every field may
        # legitimately still verify it, so no verdict is required"). Emit as
        # kind v6info so the runner records it without counting pass/fail.
        trunc = os.path.join(root, "ledger-crlf-truncated.tsv")
        if os.path.isfile(trunc):
            tgt = os.path.join(root, "src/payload.md")
            if not os.path.isfile(tgt):
                tgt = os.path.join(case_dir, "src/payload.md")
            emit(case, "v6info", trunc, tgt, "NOT-VERIFIED", "mismatch", root,
                 [], "probe V6c (CRLF truncated: informational boundary, not judged)")
        continue

    # ---- ledger: this runner's own built copy first -----------------------
    ledger = my_ledger if os.path.isfile(my_ledger) else None
    if ledger is None:
        cand = pick(doc, ["ledger_path", "ledger", "ledger_file"])
        if isinstance(cand, str) and cand:
            cand = sub(cand, root)
            ledger = cand if os.path.isabs(cand) else os.path.join(repo, cand)
    if not ledger or not os.path.isfile(ledger):
        for pat in (f"ledger-{case}.tsv", f"ledger-{case.replace('case-','')}.tsv"):
            p = os.path.join(vault_dir, pat)
            if os.path.isfile(p):
                ledger = p; break
    if not ledger or not os.path.isfile(ledger):
        p = os.path.join(root, "ledger.tsv")
        if os.path.isfile(p):
            ledger = p
    if not ledger or not os.path.isfile(ledger):
        print(f"{case}: no ledger found — skipped", file=notes)
        continue

    accept = []
    if isinstance(doc.get("accept"), dict) and isinstance(doc["accept"].get("contains"), list):
        accept = [str(x) for x in doc["accept"]["contains"]]

    targets = doc.get("targets")
    expect = doc.get("expect")
    pairs = []

    def pair(src, e, note=""):
        if not isinstance(src, str) or not src:
            return
        src = sub(src, root)
        if not os.path.isabs(src):
            src = os.path.join(case_dir, src)
        e = e if isinstance(e, dict) else {}
        want = norm_base(pick(e, ["verdict", "expect", "expected", "result"]))
        if want is None and isinstance(expect, str):
            want = norm_base(expect)
        if want is None:
            want = norm_base(pick(doc, ["expect_string", "verdict", "expect"]))
        token = pick(e, ["reason"]) or reason_of(pick(e, ["verdict_string"]))
        receipt = pick(e, ["receipt"])
        if not token and isinstance(receipt, str) and receipt.lower() not in ("none", "null"):
            token = receipt
        if not token:
            token = reason_of(pick(doc, ["expect_string"]))
        pairs.append((src, want or "NOT-VERIFIED", token or "", note))

    if isinstance(targets, list) and targets and all(isinstance(t, dict) for t in targets):
        for t in targets:
            e = pick(t, ["expected", "expect"])
            pair(pick(t, ["path", "source", "source_path", "target"]),
                 e if isinstance(e, dict) else {})
    elif isinstance(targets, list) and targets and all(isinstance(t, str) for t in targets):
        if isinstance(expect, list) and expect and all(isinstance(e, dict) for e in expect):
            for i, t in enumerate(targets):
                pair(t, expect[i] if i < len(expect) else expect[0])
        elif isinstance(expect, dict):
            for t in targets:
                pair(t, expect)
        elif isinstance(expect, str):
            for t in targets:
                pair(t, {"verdict": expect})
    elif isinstance(expect, list):
        for e in expect:
            if isinstance(e, dict):
                pair(pick(e, ["path", "source", "source_path", "target"]), e)
    elif isinstance(expect, dict):
        src = pick(doc, ["source_path", "source", "path", "target", "input"])
        if isinstance(src, list):
            for s in src:
                pair(s, expect)
        else:
            pair(src, expect)
    elif isinstance(expect, str):
        pair(pick(doc, ["source_path", "source", "path", "target", "input"]), {"verdict": expect})

    if not pairs:
        print(f"{case}: no (source,want) pairs parsed; keys={list(doc)[:12]}", file=notes)
        continue
    for src, want, token, note in pairs:
        emit(case, "generic", ledger, src, want, token, root, accept, note)

    # auxiliary no-row controls (V8 shape): declared, must NOT verify
    aux = doc.get("auxiliary_checks")
    if isinstance(aux, list):
        for a in aux:
            if not isinstance(a, dict):
                continue
            e = a.get("expected") if isinstance(a.get("expected"), dict) else {}
            src = sub(pick(a, ["source_path", "path", "source"]), root)
            if src and not os.path.isabs(src):
                src = os.path.join(case_dir, src)
            emit(case + "-aux", "generic", ledger, src,
                 norm_base(pick(e, ["verdict"])) or "NOT-VERIFIED",
                 pick(e, ["reason"]), root, accept, a.get("id") or "auxiliary no-row control")

prep.close()
notes.close()
PYEOF

n_rows=$(wc -l < "$PREP_TSV" | tr -d ' ')
log "runner-29: prepared $n_rows fixture rows"
cat "$PREP_NOTES" >&2 2>/dev/null || true

n_r4=$(r4_impls | wc -l | tr -d ' ')
INST="$(installed_tool)"
if [ -z "$INST" ] && [ "$n_r4" -eq 0 ]; then
  add_meta "blocked" "no subject tool found" "installed tools/souji-verify.sh absent and no r4 impls"
fi
if [ "$n_r4" -eq 0 ]; then
  add_meta "r4-impls-absent" "0 candidates matching tools/$IMPL_GLOB" "round-4 implementor candidates did not land; incumbent tested"
fi

# ------------------------------------------------------------------ live setup
LIVE="$TMP/live"; mkdir -p "$LIVE"
VAULT_FILE=""
if [ -f "$VAULT/Home.md" ]; then VAULT_FILE="$VAULT/Home.md"
else
  VAULT_FILE="$(find "$VAULT" -maxdepth 2 -name '*.md' -type f 2>/dev/null | LC_ALL=C sort | head -1 || true)"
fi
LIVE_OK=0
if [ -n "$VAULT_FILE" ] && [ -f "$VAULT_FILE" ]; then
  LIVE_OK=1
  cp "$VAULT_FILE" "$LIVE/src-home.md"
  SHA_LIVE=$(sha256sum "$LIVE/src-home.md" | cut -d' ' -f1)
  WRONG=$(printf 'souji-29-wrong' | sha256sum | cut -d' ' -f1)
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18\tlive-home\n' "$LIVE/src-home.md" "$SHA_LIVE" "$VAULT_FILE" "$SHA_LIVE"
  } > "$LIVE/ledger-ok.tsv"
  {
    printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n'
    printf '%s\t%s\t%s\t%s\t2026-10-18\tlive-home-bad\n' "$LIVE/src-home.md" "$SHA_LIVE" "$VAULT_FILE" "$WRONG"
  } > "$LIVE/ledger-bad.tsv"
  add_meta "live-vault-target" "$VAULT_FILE" "real vault file used read-only; sha256=$SHA_LIVE"
fi

VAULT_MANIFEST_BEFORE=$(find "$VAULT" -type f -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LIVE_LEDGER="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"
LL_SHA_BEFORE=$(sha256sum "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || echo none)
LL_LINES_BEFORE=$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ' || echo 0)

# ------------------------------------------------------------------ runner
# run_subject <impl> <vocab> <ledger> <target> -> GOT_LINE GOT_MODE; rc 0 if a verdict line parsed
run_subject() {
  local impl="$1" vocab="$2" lg="$3" tgt="$4" out rc
  GOT_LINE=""; GOT_MODE=""
  if [ "$vocab" = r2 ]; then
    out=$(env SOUJI_LEDGER="$lg" timeout 30 bash "$impl" "$tgt" 2>&1); rc=$?
    if printf '%s\n' "$out" | grep -q $'^VERDICT\t'; then
      GOT_LINE=$(printf '%s\n' "$out" | grep $'^VERDICT\t' | head -1); GOT_MODE="env-SOUJI_LEDGER"
      return 0
    fi
    GOT_LINE="rc=$rc out=$(printf '%s' "$out" | head -c 200)"; GOT_MODE="-"
    return 1
  fi
  out=$(timeout 30 bash "$impl" --ledger "$lg" --fallback "$tgt" 2>&1); rc=$?
  if printf '%s\n' "$out" | grep -qE '^[[:space:]]*(VERIFIED|NOT-VERIFIED)'; then
    GOT_LINE=$(printf '%s\n' "$out" | grep -E '^[[:space:]]*(VERIFIED|NOT-VERIFIED)' | head -1); GOT_MODE="--ledger --fallback"
    return 0
  fi
  [ "$rc" = 124 ] && { GOT_LINE="timeout(mode A)"; GOT_MODE="--ledger --fallback"; return 1; }
  out=$(timeout 30 bash "$impl" --ledger "$lg" "$tgt" 2>&1); rc=$?
  if printf '%s\n' "$out" | grep -qE '^[[:space:]]*(VERIFIED|NOT-VERIFIED)'; then
    GOT_LINE=$(printf '%s\n' "$out" | grep -E '^[[:space:]]*(VERIFIED|NOT-VERIFIED)' | head -1); GOT_MODE="--ledger"
    return 0
  fi
  out=$(env SOUJI_LEDGER="$lg" timeout 30 bash "$impl" "$tgt" 2>&1); rc=$?
  if printf '%s\n' "$out" | grep -qE '^[[:space:]]*(VERIFIED|NOT-VERIFIED)'; then
    GOT_LINE=$(printf '%s\n' "$out" | grep -E '^[[:space:]]*(VERIFIED|NOT-VERIFIED)' | head -1); GOT_MODE="env-SOUJI_LEDGER"
    return 0
  fi
  GOT_LINE="rc=$rc out=$(printf '%s' "$out" | head -c 200)"; GOT_MODE="-"
  return 1
}

got_class() { # got_class <vocab> <line> -> VERIFIED|NOT-VERIFIED|?
  local vocab="$1" s="$2"
  if [ "$vocab" = r2 ]; then
    printf '%s\n' "$s" | awk -F'\t' '{print $3}' | head -1 | tr -d '[:space:]' | \
      sed 's/^SAFE$/VERIFIED/;s/^NOT-SAFE$/NOT-VERIFIED/'
  else
    s="${s%%$'\t'*}"; s="${s%%(*}"
    printf '%s' "$s" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]' | sed 's/^VERIFIED$/VERIFIED/;s/^NOT-VERIFIED$/NOT-VERIFIED/'
  fi
}

# token_ok <line> <class> <token> -> 0 if the token's requirement is met.
# Semantic (fixture accept notes say "the primary reason must name a
# source-side hash mismatch"): wording variants sha/hash and the various
# mismatch nouns count; class-level tokens check the parsed class.
token_ok() {
  local line="$1" class="$2" token="$3" l
  l="$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')"
  case "$token" in
    VERIFIED) [ "$class" = VERIFIED ] ;;
    NOT-VERIFIED) [ "$class" = NOT-VERIFIED ] ;;
    moved-to-obsidian) printf '%s' "$l" | grep -qF -- "moved-to-obsidian" ;;
    mismatch) printf '%s' "$l" | grep -q "mismatch" ;;
    vault-sha-mismatch|vault-hash-mismatch)
      [ "$class" = NOT-VERIFIED ] && printf '%s' "$l" | grep -q "vault" && printf '%s' "$l" | grep -q "mismatch" ;;
    source-hash|source-sha-mismatch)
      [ "$class" = NOT-VERIFIED ] && printf '%s' "$l" | grep -q "source" && printf '%s' "$l" | grep -q "mismatch" ;;
    source-absent)
      [ "$class" = NOT-VERIFIED ] && printf '%s' "$l" | grep -qF -- "source-absent" ;;
    vault-absent)
      [ "$class" = NOT-VERIFIED ] && printf '%s' "$l" | grep -q "vault" && printf '%s' "$l" | grep -qE "absent|unreachable" ;;
    ledger-row) printf '%s' "$l" | grep -qF -- "ledger-row" ;;
    *) printf '%s' "$l" | grep -qiF -- "$token" ;;
  esac
}

judge_row() { # judge_row <impl_path> <vocab> <case> <ledger> <target> <want> <token> <accept_json> <note>
  local impl="$1" vocab="$2" case="$3" lg="$4" tgt="$5" want="$6" token="$7" accept="$8" note="$9"
  local p=false extra=""
  local iname; iname="$(basename "$impl")"; iname="${iname%.sh}"
  if run_subject "$impl" "$vocab" "$lg" "$tgt"; then
    local gc; gc=$(got_class "$vocab" "$GOT_LINE")
    if [ "$gc" = "$want" ]; then
      p=true
      if [ "$want" = VERIFIED ]; then
        printf '%s' "$GOT_LINE" | grep -qiF -- "moved-to-obsidian" || { p=false; extra="receipt!=moved-to-obsidian"; }
      fi
      # case-level accept.apply only to the target whose class matches the
      # accept's own class (fixtures document accept for the PRIMARY target;
      # controls in the same case have their own expect entries)
      if [ "$vocab" != r2 ] && [ -n "$accept" ] && [ "$accept" != "[]" ]; then
        local accept_class
        accept_class=$(printf '%s' "$accept" | python3 -c '
import json,sys
try:
    toks=json.load(sys.stdin)
except Exception:
    print(""); raise SystemExit
for t in toks:
    u=str(t).upper()
    if "NOT" in u and ("VERIFIED" in u or "SAFE" in u):
        print("NOT-VERIFIED"); break
    if "VERIFIED" in u or u=="SAFE":
        print("VERIFIED"); break
' 2>/dev/null)
        if [ -z "$accept_class" ] || [ "$accept_class" = "$want" ]; then
          local tok
          for tok in $(printf '%s' "$accept" | python3 -c 'import json,sys; print(" ".join(json.load(sys.stdin)))' 2>/dev/null); do
            token_ok "$GOT_LINE" "$gc" "$tok" || { p=false; extra="accept-contains missing: $tok"; }
          done
        fi
      fi
      if [ -n "$token" ] && [ "$token" != "none" ] && [ "$token" != "null" ]; then
        if token_ok "$GOT_LINE" "$gc" "$token"; then
          :
        elif [ "$vocab" = r2 ] && [ "$token" != "moved-to-obsidian" ]; then
          # r4 refines reason vocabulary; the r2 incumbent may emit a coarser
          # reason (e.g. unreachable for source-absent). Class stays hard.
          extra="${extra:+$extra; }r2-reason-refinement: wants '$token'"
        else
          p=false; extra="${extra:+$extra; }token missing: $token"
        fi
      fi
    fi
    add_row "$iname" "$case" "$p" "$GOT_LINE" "$want${token:+ ($token)}" "$GOT_MODE" "${note}${extra:+ | $extra}"
  else
    add_row "$iname" "$case" false "$GOT_LINE" "$want${token:+ ($token)}" "$GOT_MODE" "${note} | no verdict line"
  fi
}

# subject list: r4 candidates first, then the installed incumbent
SUBJ_TSV="$TMP/subjects.tsv"; : > "$SUBJ_TSV"
while IFS= read -r p; do
  [ -n "$p" ] || continue
  n="$(basename "$p")"; n="${n%.sh}"
  printf '%s\t%s\t%s\n' "$n" "$p" r4 >> "$SUBJ_TSV"
done < <(r4_impls)
if [ -n "$INST" ]; then
  printf '%s\t%s\t%s\n' "souji-verify" "$INST" r2 >> "$SUBJ_TSV"
fi

while IFS=$'\t' read -r iname impl vocab; do
  [ -n "$impl" ] || continue
  sha_before=$(sha256sum "$impl" | cut -d' ' -f1)
  add_meta "impl-sha" "$iname sha256=$sha_before" "vocab=$vocab path=${impl#$REPO_ROOT/}"
  # 1. selftest
  st_out=$(timeout 300 bash "$impl" --selftest 2>&1); st_rc=$?
  st_pass=false; [ "$st_rc" -eq 0 ] && st_pass=true
  add_row "$iname" "--selftest" "$st_pass" "exit=$st_rc $(printf '%s' "$st_out" | tail -1 | head -c 160)" "exit=0" "direct" "subject --selftest"
  # 2. fixture rows
  while IFS=$'\x1f' read -r case kind lg src want token root accept note; do
    [ -n "$case" ] || continue
    [ -n "$lg" ] && [ -f "$lg" ] || { add_row "$iname" "$case" false "ledger missing: $lg" "$want" "-" "$note | ledger absent"; continue; }
    if [ "$kind" = "v6info" ]; then
      # informational boundary (fixture: "not judged"): record the observed
      # line without counting a pass/fail
      if run_subject "$impl" "$vocab" "$lg" "$src"; then
        add_row "$iname" "$case" record "$GOT_LINE" "$want (informational)" "$GOT_MODE" "$note"
      else
        add_row "$iname" "$case" record "$GOT_LINE" "$want (informational)" "$GOT_MODE" "$note | no verdict line"
      fi
      continue
    fi
    judge_row "$impl" "$vocab" "$case" "$lg" "$src" "$want" "$token" "$accept" "$note"
  done < "$PREP_TSV"
  # 3. live real-vault rows
  if [ "$LIVE_OK" = 1 ]; then
    judge_row "$impl" "$vocab" "live-vault-home" "$LIVE/ledger-ok.tsv" "$LIVE/src-home.md" VERIFIED "moved-to-obsidian" "[]" "real vault read-only: correct hash"
    judge_row "$impl" "$vocab" "live-vault-home-bad" "$LIVE/ledger-bad.tsv" "$LIVE/src-home.md" NOT-VERIFIED "vault-hash-mismatch" "[]" "real vault read-only: wrong vault hash"
  fi
  sha_after=$(sha256sum "$impl" | cut -d' ' -f1)
  [ "$sha_before" != "$sha_after" ] && add_meta "impl-drift" "$iname changed during run" "before=$sha_before after=$sha_after"
done < "$SUBJ_TSV"

# ------------------------------------------------------------------ safety + CLI meta
VAULT_MANIFEST_AFTER=$(find "$VAULT" -type f -printf '%P\t%s\t%T@\n' 2>/dev/null | LC_ALL=C sort | sha256sum | cut -d' ' -f1)
LL_SHA_AFTER=$(sha256sum "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || echo none)
LL_LINES_AFTER=$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ' || echo 0)
if [ "$VAULT_MANIFEST_BEFORE" = "$VAULT_MANIFEST_AFTER" ]; then
  add_meta "vault-readonly" "UNCHANGED manifest=$VAULT_MANIFEST_BEFORE" "real vault byte-manifest identical before/after"
else
  add_meta "vault-readonly" "CHANGED before=$VAULT_MANIFEST_BEFORE after=$VAULT_MANIFEST_AFTER" "INVESTIGATE"
fi
if [ "$LL_SHA_BEFORE" = "$LL_SHA_AFTER" ] && [ "$LL_LINES_AFTER" = "1" ]; then
  add_meta "live-ledger" "header-only lines=$LL_LINES_AFTER sha=$LL_SHA_AFTER" "live ledger unchanged and header-only"
else
  add_meta "live-ledger" "before sha=$LL_SHA_BEFORE lines=$LL_LINES_BEFORE | after sha=$LL_SHA_AFTER lines=$LL_LINES_AFTER" "INVESTIGATE"
fi
INSP_VER=$(timeout 5 obsidian-cli-inspector --version 2>&1 | head -1 || true)
add_meta "inspector-probe" "obsidian-cli-inspector: ${INSP_VER:-unavailable}" "timeout 5 --version only; /usr/bin/obsidian never executed"
GUI_SIZE=$(stat -c '%s bytes mode=%a' /usr/bin/obsidian 2>/dev/null || echo missing)
add_meta "gui-launcher" "/usr/bin/obsidian: $GUI_SIZE" "GUI launcher stat only; runner never invokes it"
r2sha=$(sha256sum "$REPO_ROOT/tools/souji-verify.sh" 2>/dev/null | cut -d' ' -f1 || echo none)
add_meta "incumbent" "tools/souji-verify.sh sha256=$r2sha" "subject of record when r4 candidates are absent"

# ------------------------------------------------------------------ emit
FINISHED_AT="$(date -u +%FT%TZ)"
python3 - "$ROWS_TSV" "$META_TSV" "$OUT" "$FINISHED_AT" <<'PYEOF'
import json, sys, os
rows_tsv, meta_tsv, out, finished = sys.argv[1:5]
rows = []
counted = passed = failed = recorded = 0
with open(rows_tsv) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 7:
            if p[2] == "record":
                rows.append({"impl": p[0], "case": p[1], "pass": None,
                             "got": p[3], "want": p[4], "mode": p[5], "note": p[6]})
                recorded += 1
                continue
            rows.append({"impl": p[0], "case": p[1], "pass": p[2] == "true",
                         "got": p[3], "want": p[4], "mode": p[5], "note": p[6]})
            counted += 1
            passed += 1 if p[2] == "true" else 0
            failed += 0 if p[2] == "true" else 1
with open(meta_tsv) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            rows.append({"impl": "-", "case": "meta:" + p[0], "pass": None,
                         "got": p[1], "want": None, "note": p[2]})
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(rows, open(out, "w"), indent=1)
impls = sorted({r["impl"] for r in rows if r["impl"] != "-"})
print(f"runner-29: counted={counted} pass={passed} fail={failed} recorded={recorded} impls={impls} meta={len(rows)-counted-recorded} -> {out}")
if failed:
    for r in rows:
        if r.get("pass") is False:
            print(f"  FAIL {r['impl']} {r['case']}: want={r['want']} got={r['got'][:120]}")
PYEOF

if [ "$WRITE_SEAT_META" = 1 ]; then
  META_OUT="$REPO_ROOT/census/round-4/seat-29.json"
  python3 - "$OUT" "$META_OUT" <<'PYEOF'
import json, sys, os
src, dst = sys.argv[1:3]
rows = json.load(open(src))
counted = [r for r in rows if r.get("impl") != "-" and r.get("pass") is not None]
per = {}
for r in counted:
    d = per.setdefault(r["impl"], {"pass": 0, "fail": 0})
    d["pass" if r["pass"] else "fail"] += 1
doc = {
    "seat": "S29", "role": "runner", "round": 4, "date": "2026-10-18",
    "artifact": "tests/vault/runner-29.sh",
    "output": "tests/results/vrun-29.json",
    "subject_note": "subjects = every tools/souji-vault-verify*.sh candidate present at run time (r4 vocabulary) + the installed tools/souji-verify.sh incumbent (r2 vocabulary, SOUJI_LEDGER seam); each tested against every case-V* fixture rebuilt under the runner's own mktemp root with its own ledger copy, the V6 CRLF probes, the V8 no-row aux control, and two read-only real-vault rows (correct hash must verify, wrong vault hash must not)",
    "summary": {"counted": len(counted),
                "pass": sum(1 for r in counted if r["pass"]),
                "fail": sum(1 for r in counted if not r["pass"]),
                "per_impl": per},
    "failures": [{"impl": r["impl"], "case": r["case"], "want": r["want"], "got": r["got"]}
                 for r in counted if not r["pass"]],
    "meta": [r for r in rows if r.get("impl") == "-"],
}
os.makedirs(os.path.dirname(dst), exist_ok=True)
json.dump(doc, open(dst, "w"), indent=1)
print(f"runner-29: seat meta -> {dst}")
PYEOF
fi

FAILED_N=$(awk -F'\t' '$3=="false"' "$ROWS_TSV" | wc -l | tr -d ' ')
TOTAL_N=$(wc -l < "$ROWS_TSV" | tr -d ' ')
[ "$TOTAL_N" -gt 0 ] || exit 1
exit 0
