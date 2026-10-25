#!/usr/bin/env bash
# tests/vault/runner-27.sh — SEAT S27 runner, souji-shokunin round 4
# (Obsidian-CLI vault verification). Produces tests/results/vrun-27.json.
#
# Independent by construction (r2 house pattern: twin runners share only the
# fixture contract, never code or fixture state):
#   * every fixture is (re)built by ITS OWN builder into a fresh mktemp dir
#     with a per-run ledger path under /tmp -- no other seat's ledger or
#     fixture root is consumed;
#   * own expected.json parser (tolerant of the declared schema variants) and
#     own judging code;
#   * own invariants: live ledger stays header-only, real vault manifest
#     unchanged, no Obsidian GUI process spawned, tool bytes stable.
#
# Matrix: for each candidate tools/souji-vault-verify.impl-*.sh
#   --selftest exit 0;
#   every tests/vault/case-V*/ target judged VERIFIED / NOT-VERIFIED against
#   expected.json, with a header-only-ledger negative (same target must NOT
#   verify without its row) and a determinism rerun;
# output rows {impl, case, pass, got, want, rc, cmd, detail} + invariants.
#
# Safety: /usr/bin/obsidian (GUI launcher) is NEVER executed; the real vault
# (/home/vgpnk/Documents/shokoknowledge) is only read (sha256sum/stat/find);
# the live ledger corpus/knowledge/obsidian-ledger.tsv is never written.
#
# usage: runner-27.sh [--wait SECS] [--out PATH] [--impls-dir DIR]
#                     [--cases-dir DIR] [--timeout SECS] [--keep]
#   --wait S      wait up to S seconds for impls+fixtures (default 0)
#   --out PATH    JSON output (default <lane>/tests/results/vrun-27.json)
#   --impls-dir   dir holding souji-vault-verify.impl-*.sh (default <lane>/tools)
#   --cases-dir   dir holding case-V*/ fixtures (default <lane>/tests/vault)
#   --keep        keep the mktemp scratch dir (prints path)
# exit: 0 matrix completed; 1 blocked (no impls/fixtures after wait); 2 usage
set -uo pipefail
export LC_ALL=C

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LANE="$(cd -- "$HERE/../.." && pwd)"
SEAT="S27"
ROUND=4
OUT="$LANE/tests/results/vrun-27.json"
IMPLS_DIR="$LANE/tools"
CASES_DIR="$LANE/tests/vault"
WAIT=0
KEEP=0
TOOL_TIMEOUT=60
SELFTEST_TIMEOUT=300
VAULT="/home/vgpnk/Documents/shokoknowledge"
LIVE_LEDGER="$LANE/corpus/knowledge/obsidian-ledger.tsv"

usage() { sed -n '2,30p' "$0" >&2; exit 2; }
while [ $# -gt 0 ]; do
  case "$1" in
    --wait)      [ $# -ge 2 ] || usage; WAIT="$2"; shift 2 ;;
    --out)       [ $# -ge 2 ] || usage; OUT="$2"; shift 2 ;;
    --impls-dir) [ $# -ge 2 ] || usage; IMPLS_DIR="$2"; shift 2 ;;
    --cases-dir) [ $# -ge 2 ] || usage; CASES_DIR="$2"; shift 2 ;;
    --timeout)   [ $# -ge 2 ] || usage; TOOL_TIMEOUT="$2"; shift 2 ;;
    --keep)      KEEP=1; shift ;;
    -h|--help)   usage ;;
    *) printf 'runner-27.sh: unknown argument: %s\n' "$1" >&2; usage ;;
  esac
done

# absolutize user dirs before any cd/relative use
IMPLS_DIR="$(cd -- "$IMPLS_DIR" 2>/dev/null && pwd -P || printf '%s' "$IMPLS_DIR")"
CASES_DIR="$(cd -- "$CASES_DIR" 2>/dev/null && pwd -P || printf '%s' "$CASES_DIR")"
OUT="$(cd -- "$(dirname -- "$OUT")" 2>/dev/null && pwd -P || printf '%s' "$(dirname -- "$OUT")")/$(basename -- "$OUT")"

W="$(mktemp -d "${TMPDIR:-/tmp}/souji27v.XXXXXX")"
case "$W" in /tmp/souji27v.*) : ;; *) printf 'refusing: W=%s\n' "$W" >&2; exit 9 ;; esac
cleanup() { [ "$KEEP" = 1 ] && { printf 'kept: %s\n' "$W" >&2; return; }; rm -rf "$W"; }
trap cleanup EXIT

ROWS="$W/rows.tsv"; : > "$ROWS"
META="$W/meta.tsv"; : > "$META"

log() { printf '%s\n' "$*" >&2; }
sha() { sha256sum -- "$1" 2>/dev/null | awk '{print $1}'; }
san() { printf '%s' "${1:-}" | tr '\t\n' '  ' | cut -c1-500; }

meta_kv() { printf '%s\t%s\n' "$1" "$(san "$2")" >> "$META"; }

# row <impl> <case> <pass(1|0|null)> <got> <want> <rc> <cmd> <detail>
row() {
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(san "$1")" "$(san "$2")" "$3" "$(san "$4")" "$(san "$5")" "$(san "$6")" "$(san "$7")" "$(san "$8")" >> "$ROWS"
}

# ---------------------------------------------------------------- invariants
vault_fp() { # $1 out-file -> prints "files=N manifest=<sha>"
  {
    [ -d "$VAULT" ] || { printf 'VAULT-ABSENT\n'; return 0; }
    find "$VAULT" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 2>/dev/null \
      | sort -z | xargs -0 -r sha256sum 2>/dev/null
  } > "$1" 2>/dev/null
  printf 'files=%s manifest=%s' \
    "$(grep -c . "$1" 2>/dev/null || true)" "$(sha "$1")"
}
LL_SHA_BEFORE="$([ -f "$LIVE_LEDGER" ] && sha "$LIVE_LEDGER" || echo missing)"
LL_LINES_BEFORE="$([ -f "$LIVE_LEDGER" ] && wc -l < "$LIVE_LEDGER" || echo missing)"
VAULT_FP_BEFORE="$(vault_fp "$W/vault-fp.before")"
GUI_BEFORE="$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true)"; GUI_BEFORE="${GUI_BEFORE:-0}"

# GUI-launcher tripwire: a shim named `obsidian` first on PATH records any
# attempt to execute the launcher (executing it would spawn the desktop app;
# another seat's adversarial harness cycles the real app, so a bare process
# count is not trustworthy — this counts OUR OWN attempts).
mkdir -p "$W/tripwire"
cat > "$W/tripwire/obsidian" <<'TRIP'
#!/usr/bin/env bash
printf 'TRIPPED pid=%s args=%s\n' "$$" "$*" >> "${S27_TRIP_LOG:-/tmp/s27-trip.log}"
exit 127
TRIP
chmod +x "$W/tripwire/obsidian"
export S27_TRIP_LOG="$W/tripwire.log"
: > "$S27_TRIP_LOG"

# ------------------------------------------------------------------ wait loop
impl_paths() {
  local p
  for p in "$IMPLS_DIR"/souji-vault-verify.impl-*.sh; do [ -f "$p" ] && printf '%s\n' "$p"; done
  [ -f "$IMPLS_DIR/souji-vault-verify.sh" ] && printf '%s\n' "$IMPLS_DIR/souji-vault-verify.sh"
}
case_dirs() {
  local d
  for d in "$CASES_DIR"/case-V*; do
    [ -d "$d" ] && [ -f "$d/expected.json" ] && printf '%s\n' "$d"
  done | sort -V
}
deadline=$(( $(date +%s) + WAIT ))
while :; do
  n_impl=$(impl_paths | wc -l); n_case=$(case_dirs | wc -l)
  [ "$n_impl" -gt 0 ] && [ "$n_case" -gt 0 ] && break
  [ "$(date +%s)" -ge "$deadline" ] && break
  sleep 10
done
N_IMPL=$(impl_paths | wc -l); N_CASE=$(case_dirs | wc -l)
log "runner-27: impls=$N_IMPL fixtures=$N_CASE (impls-dir=$IMPLS_DIR cases-dir=$CASES_DIR)"

meta_kv seat "$SEAT"; meta_kv round "$ROUND"
meta_kv runner_sha256 "$(sha "$0")"
meta_kv generated_at_utc "$(date -u +%FT%TZ)"
meta_kv impls_dir "$IMPLS_DIR"; meta_kv cases_dir "$CASES_DIR"
meta_kv n_impls "$N_IMPL"; meta_kv n_fixtures "$N_CASE"
meta_kv wait_s "$WAIT"
meta_kv live_ledger_sha_before "$LL_SHA_BEFORE"
meta_kv live_ledger_lines_before "$LL_LINES_BEFORE"
meta_kv vault_fingerprint_before "$VAULT_FP_BEFORE"
meta_kv gui_procs_before "$GUI_BEFORE"
meta_kv lane_head "$(git -C "$LANE" rev-parse --short HEAD 2>/dev/null || echo unknown)"

if [ "$N_IMPL" -eq 0 ] || [ "$N_CASE" -eq 0 ]; then
  row "-" "matrix" "null" "impls=$N_IMPL fixtures=$N_CASE" ">=1 impl, >=1 fixture" "" \
    "runner-27.sh --wait $WAIT" "blocked: candidate impls or fixtures absent"
fi

# ------------------------------------------------------ fixture preparation
# python: run each builder into $W/<case> with a per-run ledger, parse
# expected.json, emit cases.tsv: case, root, ledger, target, want, note
python3 - "$CASES_DIR" "$W" <<'PYEOF'
import json, os, re, subprocess, sys

cases_dir, work = sys.argv[1], sys.argv[2]
rows = open(os.path.join(work, "cases.tsv"), "w")
notes = open(os.path.join(work, "prep-notes.txt"), "w")

def norm_class(v):
    if not isinstance(v, str):
        return None
    t = re.sub(r"[^A-Za-z-]", "", v.strip().upper().replace("_", "-"))
    if "NOT-VERIFIED" in t or t == "NOTVERIFIED" or t.startswith("NOT-SAFE"):
        return "NOT-VERIFIED"
    if "VERIFIED" in t or t.startswith("SAFE"):
        return "VERIFIED"
    return None

def resolve(p, root):
    if not isinstance(p, str) or not p:
        return None
    p = p.replace("@FIXTURE_ROOT@", root)
    if not os.path.isabs(p):
        p = os.path.join(root, p)
    return os.path.normpath(p)

def walk_expect(doc, root):
    """Return list of dicts {path,want,receipt,ledger,reason,entry} from declared shapes."""
    out = []
    targets = doc.get("targets")

    # shape A: targets[] dicts carrying their own expected
    if isinstance(targets, list):
        for t in targets:
            if not isinstance(t, dict):
                continue
            p = t.get("path") or t.get("target") or t.get("source_path")
            e = t.get("expected") or t.get("expect") or {}
            if isinstance(e, str):
                e = {"verdict": e}
            if not isinstance(e, dict):
                e = {}
            w = norm_class(e.get("verdict") or t.get("verdict") or doc.get("verdict"))
            if p and w:
                ent = dict(e)
                ent.setdefault("path", p)
                out.append({"path": resolve(p, root), "want": w, "receipt": e.get("receipt"),
                            "ledger": t.get("ledger"), "reason": e.get("reason"), "entry": ent})
    if out:
        return out

    # shape B: targets[] strings + expect[] dicts, paired by order
    exp = doc.get("expect")
    if isinstance(exp, dict):
        exp = [exp]
    if isinstance(targets, list) and isinstance(exp, list):
        for i, e in enumerate(exp):
            if not isinstance(e, dict):
                continue
            p = e.get("path") or e.get("target")
            if not p and i < len(targets):
                t = targets[i]
                p = t if isinstance(t, str) else (t.get("path") if isinstance(t, dict) else None)
            w = norm_class(e.get("verdict") or e.get("expect") or doc.get("verdict"))
            if p and w:
                out.append({"path": resolve(p, root), "want": w, "receipt": e.get("receipt"),
                            "ledger": e.get("ledger"), "reason": e.get("reason"), "entry": e})
    if out:
        return out

    # shape C: probes[] (r2-style fixture: target + verdict + per-probe ledger)
    probes = doc.get("probes")
    if isinstance(probes, list):
        for pr in probes:
            if not isinstance(pr, dict):
                continue
            p = pr.get("target") or pr.get("path")
            w = norm_class(pr.get("verdict") or pr.get("expect"))
            if p and w:
                out.append({"path": resolve(p, root), "want": w, "receipt": pr.get("receipt"),
                            "ledger": pr.get("ledger"), "reason": pr.get("reason"), "entry": pr})
    if out:
        return out

    # shape D: single top-level pair
    p = doc.get("source_path") or doc.get("target") or doc.get("path")
    w = norm_class(doc.get("verdict") or doc.get("expected"))
    if p and w:
        out.append({"path": resolve(p, root), "want": w, "receipt": doc.get("receipt"),
                    "ledger": None, "reason": doc.get("reason"), "entry": doc})
    return out

def try_build(cd, root, ledger):
    """Run the case builder; return built root or None."""
    maker = os.path.join(cd, "make-fixture.sh")
    if os.path.isfile(maker):
        variants = (["--out", root, "--ledger", ledger, "--quiet"],
                    ["--out", root, "--ledger", ledger],
                    ["--out", root, "--quiet"],
                    ["--out", root])
        for argv in variants:
            try:
                r = subprocess.run(["bash", maker] + argv, cwd=cd, capture_output=True,
                                   text=True, timeout=300)
            except subprocess.TimeoutExpired:
                print("%s: builder timeout %s" % (os.path.basename(cd), argv), file=notes)
                continue
            m = re.search(r"FIXTURE_READY\s+\S+\s+(\S+)", r.stdout)
            got = m.group(1) if m else root
            if r.returncode == 0:
                return got
            tail = (r.stderr or r.stdout or "").strip().splitlines()
            print("%s: builder rc=%s %s | %s" % (os.path.basename(cd), r.returncode, argv,
                  tail[-1][:160] if tail else ""), file=notes)
    b = os.path.join(cd, "build.sh")
    if os.path.isfile(b):
        try:
            r = subprocess.run(["bash", b, root], cwd=cd, capture_output=True,
                               text=True, timeout=300)
        except subprocess.TimeoutExpired:
            print("%s: build.sh timeout" % os.path.basename(cd), file=notes)
            return None
        if r.returncode == 0:
            return root
        print("%s: build.sh rc=%s" % (os.path.basename(cd), r.returncode), file=notes)
    return None

for name in sorted(os.listdir(cases_dir)):
    cd = os.path.join(cases_dir, name)
    if not name.startswith("case-V") or not os.path.isdir(cd):
        continue
    case = name
    root = os.path.join(work, case)
    ledger = os.path.join(work, "ledger-%s.tsv" % case)
    built = try_build(cd, root, ledger)
    if not built:
        print("%s: no builder succeeded (skipped)" % case, file=notes)
        continue

    # expected.json: prefer the substituted copy the builder wrote into its root
    doc_path = None
    for cand in (os.path.join(built, "expected.json"), os.path.join(cd, "expected.json")):
        if os.path.isfile(cand):
            doc_path = cand
            break
    if not doc_path:
        print("%s: no expected.json (skipped)" % case, file=notes)
        continue
    try:
        doc = json.load(open(doc_path))
    except Exception as e:
        print("%s: expected.json unparsable: %s" % (case, e), file=notes)
        continue

    # ledger discovery: per-run ledger, then builder root, then declared path
    led = ledger if os.path.isfile(ledger) else None
    if not led:
        for cand in (os.path.join(built, "ledger.tsv"),
                     os.path.join(built, "ledger-%s.tsv" % case),
                     os.path.join(cases_dir, "ledger-%s.tsv" % case)):
            if os.path.isfile(cand):
                led = cand
                break
    if not led:
        cand = doc.get("ledger_path") or doc.get("ledger")
        if isinstance(cand, str) and cand:
            cand = resolve(cand, built)
            if cand and os.path.isfile(cand):
                led = cand
    if not led:
        print("%s: no ledger found; rows use header-only negative only" % case, file=notes)

    pairs = walk_expect(doc, built)
    if not pairs:
        print("%s: no target/verdict pairs parsed" % case, file=notes)
        continue
    # Judging data per row, US-separated (bash `read` collapses empty fields on
    # whitespace IFS; 0x1f is non-whitespace, so empty columns survive):
    # case US root US ledger US target US want US receipt US exp_path US reason
    #   US accept_exact(JSON) US accept_contains(JSON) US reason_aliases(JSON)
    #   US must_not_be(JSON)
    top_acc = doc.get("accept") if isinstance(doc.get("accept"), dict) else {}
    top_mnb = doc.get("must_not_be") if isinstance(doc.get("must_not_be"), list) else []
    for ent in pairs:
        p = ent["path"]
        want = ent["want"]
        rowled = led or "-"
        lhint = ent.get("ledger")
        if isinstance(lhint, str) and lhint:
            cand = resolve(lhint, built)
            if cand and os.path.isfile(cand):
                rowled = cand
            else:
                cand2 = os.path.join(cd, lhint)
                if os.path.isfile(cand2):
                    rowled = cand2
        # reason contract: a declared distinct reason (or the fixture's own
        # aliases) must appear in the output — fixture failure mode "class
        # collapse" (e.g. NOT-VERIFIED(none) for a source-hash mismatch).
        e = ent.get("entry") if isinstance(ent.get("entry"), dict) else {}
        rtext = ent.get("reason") if isinstance(ent.get("reason"), str) and ent.get("reason") else ""
        if not rtext:
            vs = str(e.get("verdict_string") or "")
            m2 = re.match(r"^(?:NOT-VERIFIED|VERIFIED)\((.+)\)$", vs)
            if m2 and m2.group(1) not in ("none",):
                rtext = m2.group(1)
        e_acc = e.get("accept") if isinstance(e.get("accept"), dict) else {}
        exact = e_acc.get("exact") or top_acc.get("exact") or []
        contains = e_acc.get("contains") or top_acc.get("contains") or e.get("contains") or []
        aliases = e.get("reason_aliases_accepted") or e_acc.get("reason_aliases_accepted") \
            or top_acc.get("reason_aliases_accepted") or []
        mnb = e.get("must_not_be") or top_mnb or []
        # The fixtures' must_not_be lists are scoped to the negative targets
        # (V2 declares must_not_be_applies_to=the primary target). Applying a
        # bare "VERIFIED"/"SAFE" veto to the VERIFIED control would veto the
        # fixture's own correct answer, so the list is skipped on VERIFIED
        # targets and only its composite (reason-bearing) entries are kept
        # everywhere.
        if want == "VERIFIED":
            mnb = [m for m in mnb if isinstance(m, str) and "(" in m]
        print("\x1f".join([
            case, built, rowled, p, want, ent.get("receipt") or "", doc_path, rtext,
            json.dumps(exact), json.dumps(contains), json.dumps(aliases), json.dumps(mnb),
        ]), file=rows)
rows.close(); notes.close()
PYEOF
cat "$W/prep-notes.txt" >&2 2>/dev/null || true

PREP_ROWS=$(grep -c . "$W/cases.tsv" 2>/dev/null || true); PREP_ROWS="${PREP_ROWS:-0}"
log "runner-27: prepared $PREP_ROWS fixture target rows"
meta_kv prepared_rows "$PREP_ROWS"

# ------------------------------------------------------------- run one tool
LAST_OUT=""; LAST_RC=0; STRICT_CLASS=""; SEM_CLASS=""

parses_verdict() {
  printf '%s\n' "$1" | grep -qaE '^(VERIFIED|NOT-VERIFIED)' && return 0
  printf '%s\n' "$1" | grep -qa '^VERDICT	' && return 0
  return 1
}

run_tool() { # <impl> <ledger> <target> [--fallback]
  local impl="$1" led="$2" tgt="$3" flag="${4:-}"
  local rc=0 out=""
  local trippath="$W/tripwire:$PATH"
  # attempt 1: declared r4 CLI (--ledger + optional --fallback)
  if [ -n "$flag" ]; then
    out=$(env PATH="$trippath" SOUJI_LEDGER="$led" timeout "$TOOL_TIMEOUT" bash "$impl" --ledger "$led" "$flag" "$tgt" 2>&1) || rc=$?
  else
    out=$(env PATH="$trippath" SOUJI_LEDGER="$led" timeout "$TOOL_TIMEOUT" bash "$impl" --ledger "$led" "$tgt" 2>&1) || rc=$?
  fi
  # attempt 2: no --fallback
  if [ "$rc" = 2 ] || ! parses_verdict "$out"; then
    local rc2=0 out2=""
    out2=$(env PATH="$trippath" SOUJI_LEDGER="$led" timeout "$TOOL_TIMEOUT" bash "$impl" --ledger "$led" "$tgt" 2>&1) || rc2=$?
    if [ "$rc2" != 2 ] && parses_verdict "$out2"; then rc=$rc2; out="$out2"; fi
  fi
  # attempt 3: env seam only
  if [ "$rc" = 2 ] || ! parses_verdict "$out"; then
    local rc3=0 out3=""
    out3=$(env PATH="$trippath" SOUJI_LEDGER="$led" timeout "$TOOL_TIMEOUT" bash "$impl" "$tgt" 2>&1) || rc3=$?
    if [ "$rc3" != 2 ] && parses_verdict "$out3"; then rc=$rc3; out="$out3"; fi
  fi
  LAST_OUT="$out"; LAST_RC="$rc"
  extract_verdict "$LAST_OUT"
}

extract_verdict() {
  local out="$1" line
  STRICT_CLASS=""; SEM_CLASS=""
  line=$(printf '%s\n' "$out" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -1)
  if [ -n "$line" ]; then
    STRICT_CLASS=$(printf '%s' "$line" | grep -aoE '^(VERIFIED|NOT-VERIFIED)')
    SEM_CLASS="$STRICT_CLASS"
    return
  fi
  line=$(printf '%s\n' "$out" | grep -a '^VERDICT	' | head -1)
  if [ -n "$line" ]; then
    local v; v=$(printf '%s' "$line" | awk -F'\t' '{print $3}')
    case "$v" in
      SAFE) SEM_CLASS="VERIFIED" ;;
      NOT-SAFE) SEM_CLASS="NOT-VERIFIED" ;;
      *) SEM_CLASS="$v" ;;
    esac
  fi
}

# --------------------------------------------------------------- matrix run
if [ "$N_IMPL" -gt 0 ] && [ "$PREP_ROWS" -gt 0 ]; then
  while IFS= read -r impl; do
    [ -n "$impl" ] || continue
    iname="$(basename "$impl")"; iname="${iname%.sh}"
    isha_before="$(sha "$impl")"
    meta_kv "impl_sha256.$iname" "$isha_before"

    # selftest
    st_rc=0
    st_out=$(timeout "$SELFTEST_TIMEOUT" bash "$impl" --selftest 2>&1) || st_rc=$?
    row "$iname" "--selftest" "$([ "$st_rc" = 0 ] && echo 1 || echo 0)" \
      "exit=$st_rc" "exit=0" "$st_rc" "bash $iname --selftest" \
      "$(printf '%s' "$st_out" | tail -2 | tr '\n' ' ')"

    while IFS=$'\x1f' read -r case root ledger target want receipt exp_path reason a_exact a_contains a_aliases a_mnb; do
      [ -n "$case" ] || continue
      run_tool "$impl" "$ledger" "$target" "--fallback"
      got_class="$STRICT_CLASS"
      sem_class="$SEM_CLASS"
      got_line="$(printf '%s\n' "$LAST_OUT" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -1)"
      [ -n "$got_line" ] || got_line="$(printf '%s\n' "$LAST_OUT" | grep -a '^VERDICT	' | head -1)"
      [ -n "$got_line" ] || got_line="rc=$LAST_RC out=$(printf '%s' "$LAST_OUT" | head -c 200 | tr '\n' ' ')"
      pass=0
      [ "$got_class" = "$want" ] && pass=1
      sem_ok=0
      [ "$sem_class" = "$want" ] && sem_ok=1
      detail=""
      # Vocabulary: the r4 fixtures pin the VERIFIED/NOT-VERIFIED contract for
      # every candidate (only the exact r2 tool sha is exempted by the fixture
      # selftests); r2-vocabulary output (SAFE/NOT-SAFE) does not pass, and
      # the semantic class is recorded in detail for the judges.
      # reason contract: a declared distinct reason (or a fixture-declared
      # alias, or the documented spelling family <side>-(hash|sha|sha256|
      # digest)-mismatch) must appear in the output — "class collapse" is a
      # named fixture failure mode (e.g. NOT-VERIFIED(none) for source-hash).
      if [ "$pass" = 1 ] && [ -n "$reason" ]; then
        r_ok=0
        printf '%s\n' "$got_line" | grep -qaF -- "$reason" && r_ok=1
        if [ "$r_ok" = 0 ] && [ -n "$a_aliases" ] && [ "$a_aliases" != "[]" ]; then
          for alias in $(printf '%s' "$a_aliases" | python3 -c 'import json,sys; print("\n".join(json.load(sys.stdin)))' 2>/dev/null); do
            printf '%s\n' "$got_line" | grep -qaF -- "$alias" && { r_ok=1; break; }
          done
        fi
        # documented family convention (V2 accept.note): any spelling of
        # <side> + (hash|sha|sha256|digest) + mismatch satisfies the case
        if [ "$r_ok" = 0 ]; then
          mfam="$(printf '%s' "$reason" | sed -nE 's/^(.*)-(hash|sha|sha256|digest)-mismatch$/\1/p')"
          if [ -n "$mfam" ]; then
            for alt in "$mfam-hash-mismatch" "$mfam-sha-mismatch" "$mfam-sha256-mismatch" "$mfam-digest-mismatch"; do
              printf '%s\n' "$got_line" | grep -qaF -- "$alt" && { r_ok=1; break; }
            done
          fi
        fi
        [ "$r_ok" = 1 ] || { pass=0; detail="reason '$reason' (or alias) absent from output; "; }
      fi
      # must_not_be: bare class tokens (VERIFIED/SAFE/NOT-VERIFIED/NOT-SAFE)
      # are class-equality vetoes — substring matching would veto the correct
      # NOT-VERIFIED(...) answer (V3's must_not_be_note documents this);
      # composite tokens are substring vetoes.
      if [ "$pass" = 1 ] && [ -n "$a_mnb" ] && [ "$a_mnb" != "[]" ]; then
        for bad in $(printf '%s' "$a_mnb" | python3 -c 'import json,sys; print("\n".join(json.load(sys.stdin)))' 2>/dev/null); do
          case "$bad" in
            VERIFIED|SAFE|NOT-VERIFIED|NOT-SAFE)
              if [ "$got_class" = "$bad" ] || [ "$sem_class" = "$bad" ]; then
                pass=0; detail="vetoed class '$bad'; "; break
              fi ;;
            *)
              if printf '%s\n' "$got_line" | grep -qaF -- "$bad"; then
                pass=0; detail="vetoed substring '$bad' present; "; break
              fi ;;
          esac
        done
      fi
      [ "$pass" = 1 ] || detail="${detail}strict-vocab=${got_class:-none} semantic=${sem_class:-none} want=$want"
      if [ "$pass" = 1 ] && [ "$sem_ok" = 1 ] && [ "$got_class" != "$want" ]; then
        detail="${detail}r2-vocabulary output (semantic match)"
      fi
      row "$iname" "$case" "$pass" "$got_line" "$want" "$LAST_RC" \
        "bash $iname --ledger <ledger> --fallback $target" "$detail"

      # header-only-ledger negative: same target, empty ledger -> must not verify
      if [ "$want" = "VERIFIED" ]; then
        printf 'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n' > "$W/empty-ledger.tsv"
        run_tool "$impl" "$W/empty-ledger.tsv" "$target"
        neg_class="$STRICT_CLASS"
        [ -z "$neg_class" ] && neg_class="$SEM_CLASS"
        neg=0; [ "$neg_class" = "NOT-VERIFIED" ] && neg=1
        row "$iname" "$case.ledger-negative" "$neg" \
          "rc=$LAST_RC ${neg_class:-none}" "NOT-VERIFIED" "$LAST_RC" \
          "bash $iname --ledger <empty> --fallback $target" \
          "$([ "$neg" = 1 ] && echo ok || echo 'verified without a ledger row')"
      fi
    done < "$W/cases.tsv"

    # determinism on the first prepared row
    if [ "$PREP_ROWS" -gt 0 ]; then
      IFS=$'\x1f' read -r dcase droot dled dtgt dwant _drest < "$W/cases.tsv"
      run_tool "$impl" "$dled" "$dtgt" "--fallback"; d1="$LAST_OUT"
      run_tool "$impl" "$dled" "$dtgt" "--fallback"; d2="$LAST_OUT"
      row "$iname" "$dcase.determinism" "$([ "$d1" = "$d2" ] && echo 1 || echo 0)" \
        "run1==run2:$([ "$d1" = "$d2" ] && echo yes || echo no)" "identical output" "" \
        "bash $iname ... $dtgt (x2)" "$(printf '%s' "$d1" | head -1)"
    fi

    isha_after="$(sha "$impl")"
    row "$iname" "--tool-bytes-stable" "$([ "$isha_before" = "$isha_after" ] && echo 1 || echo 0)" \
      "$isha_after" "$isha_before" "" "sha256sum $impl" ""
  done < <(impl_paths)
fi

# ------------------------------------------------------------- invariants
LL_SHA_AFTER="$([ -f "$LIVE_LEDGER" ] && sha "$LIVE_LEDGER" || echo missing)"
LL_LINES_AFTER="$([ -f "$LIVE_LEDGER" ] && wc -l < "$LIVE_LEDGER" || echo missing)"
LL_HDR_OK=0
if [ "$LL_LINES_BEFORE" = 1 ] && [ "$LL_LINES_AFTER" = 1 ] && [ "$LL_SHA_BEFORE" = "$LL_SHA_AFTER" ] \
   && head -1 "$LIVE_LEDGER" 2>/dev/null | grep -q '^source_path'; then LL_HDR_OK=1; fi
row "-" "invariant.live-ledger-header-only" "$LL_HDR_OK" \
  "lines=$LL_LINES_AFTER sha=${LL_SHA_AFTER:0:12}" "lines=1 unchanged" "" \
  "sha256sum $LIVE_LEDGER" "before lines=$LL_LINES_BEFORE sha=${LL_SHA_BEFORE:0:12}"

VAULT_FP_AFTER="$(vault_fp "$W/vault-fp.after")"
row "-" "invariant.vault-unchanged" "$([ "$VAULT_FP_BEFORE" = "$VAULT_FP_AFTER" ] && echo 1 || echo 0)" \
  "$VAULT_FP_AFTER" "$VAULT_FP_BEFORE" "" \
  "find $VAULT -type f | sort | xargs sha256sum | sha256sum" \
  "$([ "$VAULT_FP_BEFORE" = "$VAULT_FP_AFTER" ] && echo ok || echo 'external writer or runner wrote to the vault')"

GUI_AFTER="$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true)"; GUI_AFTER="${GUI_AFTER:-0}"
TRIP_COUNT=$(grep -c . "$S27_TRIP_LOG" 2>/dev/null || true); TRIP_COUNT="${TRIP_COUNT:-0}"
# primary invariant: our own executions never reached an `obsidian` launcher
# (tripwire counts only attempts made through this runner's PATH). The raw
# process-count delta is recorded as an observation: a sibling seat's
# adversarial harness may cycle the real app concurrently.
row "-" "invariant.no-gui-spawn" "$([ "$TRIP_COUNT" = 0 ] && echo 1 || echo 0)" \
  "tripwire_attempts=$TRIP_COUNT gui_before=$GUI_BEFORE gui_after=$GUI_AFTER" \
  "tripwire_attempts=0" "" "PATH shim 'obsidian' + pgrep -fc /usr/lib/obsidian/app.asar" \
  "$( [ "$GUI_BEFORE" != "$GUI_AFTER" ] && echo 'note: GUI process count changed concurrently (external activity; tripwire clean)'; )"
meta_kv gui_tripwire_attempts "$TRIP_COUNT"
meta_kv gui_tripwire_log "$(head -3 "$S27_TRIP_LOG" 2>/dev/null | tr '\n' ';')"

# ------------------------------------------------------------------- emit
meta_kv live_ledger_sha_after "$LL_SHA_AFTER"
meta_kv vault_fingerprint_after "$VAULT_FP_AFTER"
meta_kv gui_procs_after "$GUI_AFTER"
mkdir -p "$(dirname "$OUT")"

python3 - "$ROWS" "$META" "$OUT" "$W" <<'PYEOF'
import json, sys, os, collections

rows_path, meta_path, out_path, work = sys.argv[1:5]

meta = {}
for line in open(meta_path):
    line = line.rstrip("\n")
    if "\t" in line:
        k, v = line.split("\t", 1)
        meta[k] = v

rows = []
for raw in open(rows_path):
    if not raw.strip():
        continue
    f = (raw.rstrip("\n").split("\t") + [""] * 8)[:8]
    p = f[2]
    rows.append({
        "impl": f[0], "case": f[1],
        "pass": None if p == "null" else (p == "1"),
        "got": f[3], "want": f[4], "rc": f[5], "cmd": f[6], "detail": f[7],
    })

impls = collections.OrderedDict()
for r in rows:
    if r["impl"] in ("-", ""):
        continue
    d = impls.setdefault(r["impl"], {"pass": 0, "fail": 0, "null": 0, "cases": []})
    if r["pass"] is True:
        d["pass"] += 1
    elif r["pass"] is False:
        d["fail"] += 1
    else:
        d["null"] += 1
    d["cases"].append(r["case"])
for name, d in impls.items():
    d["total"] = d["pass"] + d["fail"]
    d["rate"] = (d["pass"] / d["total"]) if d["total"] else None
    d["sha256"] = meta.get("impl_sha256.%s" % name)

invariants = {r["case"]: r["pass"] for r in rows if r["impl"] == "-"}
n_pass = sum(1 for r in rows if r["pass"] is True)
n_fail = sum(1 for r in rows if r["pass"] is False)
n_null = sum(1 for r in rows if r["pass"] is None)
if not impls:
    status = "blocked"
elif n_fail:
    status = "fail"
else:
    status = "pass"

doc = {
    "seat": meta.get("seat", "S27"),
    "role": "vault-runner",
    "round": int(meta.get("round", "4")),
    "runner": "tests/vault/runner-27.sh",
    "runner_sha256": meta.get("runner_sha256"),
    "generated_at_utc": meta.get("generated_at_utc"),
    "status": status,
    "lane_head": meta.get("lane_head"),
    "tool_selection": {
        "impls_dir": meta.get("impls_dir"),
        "cases_dir": meta.get("cases_dir"),
        "pattern": "souji-vault-verify.impl-*.sh (+ canonical souji-vault-verify.sh)",
        "n_impls": int(meta.get("n_impls", "0")),
        "n_fixtures": int(meta.get("n_fixtures", "0")),
        "prepared_rows": int(meta.get("prepared_rows", "0")),
    },
    "method": {
        "independence": "each fixture rebuilt by its own make-fixture.sh into a fresh mktemp root with a per-run --ledger under /tmp; own expected.json parser and judging; no peer ledger consumed",
        "invocations": "env SOUJI_LEDGER=<ledger> bash <impl> --ledger <ledger> --fallback <target>; on rc=2 retried without --fallback; on rc=2 retried with the env seam only",
        "vocabulary": "pass requires the r4 VERIFIED/NOT-VERIFIED vocabulary; SAFE/NOT-SAFE output is recorded as semantic class but fails strict judging",
        "vault_access": "read-only (sha256sum/stat/find); /usr/bin/obsidian never executed",
    },
    "counts": {"rows": len(rows), "pass": n_pass, "fail": n_fail, "null": n_null},
    "impls": impls,
    "invariants": invariants,
    "rows": rows,
}
with open(out_path, "w") as fh:
    json.dump(doc, fh, indent=1)
    fh.write("\n")
print("runner-27: status=%s impls=%d rows=%d pass=%d fail=%d null=%d -> %s"
      % (status, len(impls), len(rows), n_pass, n_fail, n_null, out_path))
for name, d in impls.items():
    print("  %-34s %s/%s" % (name, d["pass"], d["total"]))
PYEOF

if [ "$N_IMPL" -eq 0 ] || [ "$N_CASE" -eq 0 ]; then exit 1; fi
exit 0
