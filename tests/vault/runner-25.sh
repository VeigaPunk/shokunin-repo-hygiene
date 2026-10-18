#!/usr/bin/env bash
# tests/vault/runner-25.sh — S25 runner, souji-shokunin round 4 (Obsidian-CLI
# vault verification).
#
# Seat contract (S25): for each candidate tools/souji-vault-verify.impl-*.sh
# (17..24; bare tools/impl-1[7-9].sh and tools/impl-2[0-4].sh are accepted
# too — one seat shipped under that name), run --selftest (record exit) and
# run the tool against every tests/vault/case-V* fixture with its ledger
# file; compare got vs expected.json. Writes tests/results/vrun-25.json as
# [{impl, case, pass, got, want}] (S57 aggregator schema; a leading meta row
# with impl "-" carries counts/invariants and is skipped by the aggregator).
#
# Fixture interfaces (measured 2026-10-18, heterogeneous by design):
#   builders V1/V2/V3/V4/V5/V8: make-fixture.sh --out DIR --ledger FILE --quiet
#   builder  V6:                build.sh [dest]  (positional; writes
#                               ledger-*.tsv + expected.json into dest)
#   expected.json shapes: probes[] (V6), targets[] of dicts (V1), targets[]
#   of strings + expect[] (V2..V5, V8); accept.exact/contains and scoped
#   must_not_be honored.
#
# Judge rule (documented for the final judge): verdict class must match
# (SAFE/NOT-SAFE map to VERIFIED/NOT-VERIFIED); when the fixture names a
# reason, the got line must carry that reason either literally or as the
# same token set with hash≡sha equivalence (the fixtures' own accept notes
# bless "reason names the side" forms); accept.contains tokens must appear
# on the got line; scoped must_not_be entries veto. Selftest rows pass iff
# exit 0.
#
# Independence / safety: fixtures are built under /tmp only; the live ledger
# corpus/knowledge/obsidian-ledger.tsv and the real vault
# /home/vgpnk/Documents/shokoknowledge are only read (sha256 manifest
# before/after). /usr/bin/obsidian is never executed; the matrix runs tools
# with --fallback so no CLI path is requested. No git mutation verbs.
#
# usage: runner-25.sh [--wait SECS] [--settle SECS] [--out PATH]
#                     [--impls GLOB] [--tool PATH] [--no-r2-fallback] [--keep]
# exit: 0 matrix complete | 1 nothing to run | 2 usage
set -uo pipefail
export LC_ALL=C

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$REPO_ROOT/tests/results/vrun-25.json"
WAIT=360
SETTLE=60
KEEP=0
IMPL_GLOB=""
TOOL_OVERRIDE=""
R2_FALLBACK=1

while [ $# -gt 0 ]; do
  case "$1" in
    --wait) WAIT="${2:-0}"; shift ;;
    --settle) SETTLE="${2:-0}"; shift ;;
    --out) OUT="${2:?--out needs a path}"; shift ;;
    --impls) IMPL_GLOB="${2:?--impls needs a glob}"; shift ;;
    --tool) TOOL_OVERRIDE="${2:?--tool needs a path}"; shift ;;
    --no-r2-fallback) R2_FALLBACK=0 ;;
    --keep) KEEP=1 ;;
    -h|--help) sed -n '2,38p' "$0"; exit 0 ;;
    *) echo "usage: $0 [--wait SECS] [--settle SECS] [--out PATH] [--impls GLOB] [--tool PATH] [--no-r2-fallback] [--keep]" >&2; exit 2 ;;
  esac
  shift
done

TMP="$(mktemp -d "${TMPDIR:-/tmp}/souji25-vault.XXXXXX")"
case "$TMP" in /tmp/*) : ;; *) echo "refusing: TMP=$TMP" >&2; exit 9 ;; esac
cleanup() {
  rc=$?
  if [ "$KEEP" = 1 ]; then printf 'kept scratch: %s\n' "$TMP" >&2
  else rm -rf "$TMP"; fi
  exit $rc
}
trap cleanup EXIT
log() { printf '%s\n' "$*" >&2; }

LIVE_LEDGER="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"
REAL_VAULT=/home/vgpnk/Documents/shokoknowledge
US=$'\x1f'

impl_paths() {
  local p rp seen=""
  if [ -n "$TOOL_OVERRIDE" ]; then
    [ -f "$TOOL_OVERRIDE" ] && printf '%s\n' "$TOOL_OVERRIDE"
    return
  fi
  if [ -n "$IMPL_GLOB" ]; then
    for p in "$REPO_ROOT"/tools/$IMPL_GLOB; do
      [ -f "$p" ] && printf '%s\n' "$p"
    done
    return
  fi
  for p in "$REPO_ROOT"/tools/souji-vault-verify.impl-*.sh \
           "$REPO_ROOT"/tools/impl-1[7-9].sh "$REPO_ROOT"/tools/impl-2[0-4].sh; do
    [ -f "$p" ] || continue
    rp=$(readlink -f -- "$p")
    case " $seen " in *" $rp "*) continue ;; esac
    seen="$seen $rp"
    printf '%s\n' "$p"
  done
}

vault_fp() {
  find "$REAL_VAULT" -type f \
    -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 2>/dev/null \
  | sort -z | xargs -0 -r sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1
}

# ---- wait for impls + late writers ----------------------------------------
impl_set_fp() {
  local p h
  for p in $(impl_paths); do
    h=$(sha256sum -- "$p" 2>/dev/null | cut -d' ' -f1)
    printf '%s %s\n' "$p" "$h"
  done
}

if [ -z "$TOOL_OVERRIDE" ]; then
  deadline=$(( $(date +%s) + WAIT ))
  while :; do
    n=$(impl_paths | wc -l)
    [ "$n" -ge 8 ] && break
    [ "$(date +%s)" -ge "$deadline" ] && break
    sleep 10
  done
  n=$(impl_paths | wc -l)
  if [ "$n" -lt 8 ] && [ "$SETTLE" -gt 0 ] && [ "$n" -gt 0 ]; then
    last=$n; stable=0
    while [ "$stable" -lt "$SETTLE" ]; do
      sleep 10
      cur=$(impl_paths | wc -l)
      if [ "$cur" = "$last" ]; then stable=$((stable+10)); else stable=0; last=$cur; fi
    done
  fi
  # sha-stability gate: late seats keep rewriting impls mid-run (observed
  # 14:36-14:37). Hold until the full path+sha set is unchanged for SETTLE s,
  # capped at 2 extra minutes, so the matrix snapshots one settled byte set.
  if [ "$SETTLE" -gt 0 ] && [ "$n" -gt 0 ]; then
    last_fp="$(impl_set_fp)"; stable=0; cap=$(( $(date +%s) + 120 ))
    while [ "$stable" -lt "$SETTLE" ] && [ "$(date +%s)" -lt "$cap" ]; do
      sleep 10
      cur_fp="$(impl_set_fp)"
      if [ "$cur_fp" = "$last_fp" ]; then stable=$((stable+10)); else stable=0; last_fp="$cur_fp"; fi
    done
    log "S25 runner: sha-stability gate released (stable=${stable}s)"
  fi
fi

n_impl=$(impl_paths | wc -l)
log "S25 runner: impls=$n_impl"
if [ "$n_impl" -eq 0 ]; then
  if [ "$R2_FALLBACK" = 1 ] && [ -f "$REPO_ROOT/tools/souji-verify.sh" ] && [ -z "$TOOL_OVERRIDE" ]; then
    log "S25 runner: no r4 impls found — falling back to tools/souji-verify.sh (r2 reference)"
    TOOL_OVERRIDE="$REPO_ROOT/tools/souji-verify.sh"
  else
    log "S25 runner: nothing to run"
    printf '[]\n' > "$OUT"
    exit 1
  fi
fi

# ---- impl snapshots --------------------------------------------------------
: > "$TMP/impls.tsv"
impl_paths > "$TMP/impls.txt"
while IFS= read -r impl; do
  [ -n "$impl" ] || continue
  iname="$(basename "$impl")"; iname="${iname%.sh}"
  isha=$(sha256sum -- "$impl" 2>/dev/null | cut -d' ' -f1)
  if bash -n "$impl" 2>/dev/null; then syn=ok; else syn=SYNTAX-ERROR; fi
  printf '%s\t%s\t%s\n' "$iname" "$isha" "$syn" >> "$TMP/impls.tsv"
  log "  impl $iname sha=${isha:0:12} syntax=$syn"
done < "$TMP/impls.txt"

# ---- live-surface fingerprints (read-only, before) -------------------------
LIVE_SHA_BEFORE=$(sha256sum "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || echo missing)
LIVE_LINES_BEFORE=$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ' || echo 0)
VAULT_FP_BEFORE=$(vault_fp)
GUI_BEFORE=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); GUI_BEFORE=${GUI_BEFORE:-0}

# ---- 1. build fixtures + extract (case, ledger, target, want, reason, ...) --
python3 - "$REPO_ROOT" "$TMP" <<'PYEOF'
import json, os, re, subprocess, sys, glob

repo, tmp = sys.argv[1], sys.argv[2]
vault_dir = os.path.join(repo, "tests", "vault")
US = "\x1f"
rows = open(os.path.join(tmp, "cases.tsv"), "w")
notes = open(os.path.join(tmp, "prep-notes.txt"), "w")

def log(m): print(m, file=notes)

def map_vocab(v):
    if not isinstance(v, str): return v
    u = v.strip().upper()
    if u == "SAFE": return "VERIFIED"
    if u in ("NOT-SAFE", "NOT_SAFE"): return "NOT-VERIFIED"
    return u

def parse_reason(verdict_str, reason):
    if reason: return reason
    if isinstance(verdict_str, str):
        m = re.match(r"^\s*(?:NOT-)?(?:VERIFIED|SAFE)\s*\(([^)]*)\)", verdict_str)
        if m: return m.group(1).strip()
    return None

def case_num(p):
    m = re.search(r"case-V(\d+)", p)
    return int(m.group(1)) if m else 99

for case_dir in sorted(glob.glob(os.path.join(vault_dir, "case-V*")), key=case_num):
    if not os.path.isdir(case_dir): continue
    case = os.path.basename(case_dir)
    cid = case.replace("case-", "")
    exp_src = os.path.join(case_dir, "expected.json")
    tpl_src = os.path.join(case_dir, "expected.template.json")
    if not os.path.isfile(exp_src) and not os.path.isfile(tpl_src):
        log(f"{case}: no expected.json — skipped"); continue
    maker = None
    for cand in ("make-fixture.sh", "build.sh", "make.sh"):
        p = os.path.join(case_dir, cand)
        if os.path.isfile(p): maker = p; break
    root = None
    ledger_arg = os.path.join(tmp, "ledgers", case + ".tsv")
    os.makedirs(os.path.dirname(ledger_arg), exist_ok=True)
    out_dir = os.path.join(tmp, "roots", case)
    if maker:
        base = os.path.basename(maker)
        if base == "make-fixture.sh":
            forms = [["--out", out_dir, "--ledger", ledger_arg, "--quiet"],
                     ["--out", out_dir, "--ledger", ledger_arg],
                     ["--out", out_dir], []]
        else:
            forms = [[out_dir], ["--out", out_dir], []]
        r = None
        for args in forms:
            try:
                r = subprocess.run(["bash", maker] + args, cwd=case_dir,
                                   capture_output=True, text=True, timeout=300)
            except Exception as e:
                log(f"{case}: builder error {e}"); r = None; break
            if r.returncode == 2 and args:
                continue
            break
        if r is not None:
            log(f"{case}: builder rc={r.returncode} args={' '.join(args)}")
            m = re.search(r"^FIXTURE_ROOT=(\S+)", r.stdout, re.M)
            if m: root = m.group(1)
            if not root:
                m = re.search(r"^FIXTURE_READY\s+\S+\s+(.+?)\s*$", r.stdout, re.M)
                if m:
                    cand = m.group(1)
                    root = cand if os.path.isdir(cand) else None
            if not root and os.path.isdir(out_dir) and os.listdir(out_dir):
                root = out_dir
            if not root and base != "make-fixture.sh":
                root = case_dir
            if r.returncode not in (0, 2):
                log(f"{case}: builder stderr tail: {r.stderr.strip()[-300:]}")
    exp_path = None
    if root and os.path.isfile(os.path.join(root, "expected.json")):
        exp_path = os.path.join(root, "expected.json")
    elif os.path.isfile(exp_src): exp_path = exp_src
    elif os.path.isfile(tpl_src): exp_path = tpl_src
    try:
        raw = open(exp_path).read()
        if root: raw = raw.replace("@FIXTURE_ROOT@", root)
        doc = json.loads(raw)
    except Exception as e:
        log(f"{case}: expected unparsable ({exp_path}): {e}"); continue

    ledger = None
    if os.path.isfile(ledger_arg): ledger = ledger_arg
    if not ledger and root:
        c = os.path.join(root, "ledger.tsv")
        if os.path.isfile(c): ledger = c
    if not ledger:
        c = doc.get("ledger_path") or doc.get("ledger")
        if isinstance(c, str) and c:
            c = c.replace("@FIXTURE_ROOT@", root or case_dir)
            if not os.path.isabs(c): c = os.path.join(root or case_dir, c)
            if os.path.isfile(c): ledger = c
    if not ledger:
        c = os.path.join(case_dir, "ledger.tsv")
        if os.path.isfile(c): ledger = c

    def emit(cid2, ledger, target, want, reason, exact, contains, mnb):
        t = str(target).replace("@FIXTURE_ROOT@", root or case_dir)
        if not os.path.isabs(t): t = os.path.join(root or case_dir, t)
        fields = [cid2, ledger or "-", t, str(want or ""), str(reason or ""),
                  json.dumps(exact or []), json.dumps(contains or []), json.dumps(mnb or [])]
        print(US.join(fields), file=rows)

    probes = doc.get("probes")
    if isinstance(probes, list) and probes:
        for pr in probes:
            if not isinstance(pr, dict): continue
            pid = pr.get("id") or cid
            pled = pr.get("ledger")
            if pled:
                pl = str(pled)
                if not os.path.isabs(pl): pl = os.path.join(root or case_dir, pl)
            else:
                pl = ledger
            contains = []
            if pr.get("evidence_substr"): contains.append(pr["evidence_substr"])
            if isinstance(pr.get("contains"), list): contains.extend(pr["contains"])
            emit(pid, pl, pr.get("target"), map_vocab(pr.get("verdict")),
                 pr.get("reason"), [], contains, [])
        continue

    targets = doc.get("targets") or []
    expect = doc.get("expect")
    if isinstance(expect, dict): expect = [expect]
    if not isinstance(expect, list): expect = []
    exp_by_path = {e.get("path"): e for e in expect if isinstance(e, dict) and e.get("path")}
    acc = doc.get("accept") if isinstance(doc.get("accept"), dict) else {}
    mnb_all = doc.get("must_not_be") or []
    applies = doc.get("must_not_be_applies_to") or ""
    m = re.search(r"([A-Za-z0-9._-]+\.[A-Za-z0-9]+)", applies)
    mfn = m.group(1) if m else None
    pairs = []
    pt = doc.get("primary_target")
    if isinstance(pt, str) and pt:
        pt = pt.replace("@FIXTURE_ROOT@", root or case_dir)
    else:
        pt = None
    for i, t in enumerate(targets):
        if isinstance(t, dict):
            e = dict(t.get("expected") or {})
            if not e and expect:
                e = expect[0] if len(expect) == 1 else (exp_by_path.get(t.get("path"), {}) or {})
            pairs.append((t.get("path"), e, t.get("accept"), t.get("ledger")))
        else:
            e = exp_by_path.get(t)
            if e is None and len(expect) == len(targets) and i < len(expect) and isinstance(expect[i], dict):
                e = expect[i]
            if e is None and len(expect) == 1 and isinstance(expect[0], dict):
                e = expect[0]
            pairs.append((t, e or {}, None, None))
    if not pairs:
        log(f"{case}: no targets parsed (keys={list(doc)[:14]}) — skipped"); continue
    for t, e, tacc, tled in pairs:
        if not t:
            log(f"{case}: target missing a path — skipped"); continue
        led = ledger
        if tled:
            cand = str(tled).replace("@FIXTURE_ROOT@", root or case_dir)
            if not os.path.isabs(cand): cand = os.path.join(root or case_dir, cand)
            if os.path.isfile(cand): led = cand
        want = e.get("verdict") or e.get("expect") or e.get("expected")
        if isinstance(want, dict): want = want.get("verdict")
        want = map_vocab(want)
        reason = parse_reason(e.get("verdict_string") or e.get("verdict"), e.get("reason"))
        tstr = str(t).replace("@FIXTURE_ROOT@", root or case_dir)
        if not os.path.isabs(tstr): tstr = os.path.join(root or case_dir, tstr)
        if isinstance(tacc, dict):
            a = tacc
        elif isinstance(e.get("accept"), dict):
            a = e["accept"]
        elif pt and tstr != pt:
            a = {}
        elif (not pt) and mfn and os.path.basename(tstr) != mfn:
            a = {}
        else:
            a = acc
        exact = a.get("exact") or []
        contains = a.get("contains") or []
        base = os.path.basename(str(t))
        if mfn:
            mnb = mnb_all if base == mfn else []
        else:
            mnb = mnb_all if map_vocab(want) == "NOT-VERIFIED" else []
        emit(cid, led, t, want, reason, exact, contains, mnb)

rows.close(); notes.close()
PYEOF

cat "$TMP/prep-notes.txt" >&2 2>/dev/null || true
n_rows=$(awk 'NF{n++} END{print n+0}' "$TMP/cases.tsv" 2>/dev/null); n_rows=${n_rows:-0}
log "S25 runner: prepared $n_rows fixture target rows"
if [ "$n_rows" -eq 0 ]; then
  printf '[]\n' > "$OUT"
  exit 1
fi

# ---- 2. run matrix ----------------------------------------------------------
: > "$TMP/results.tsv"
: > "$TMP/transcript.txt"
while IFS= read -r impl; do
  [ -n "$impl" ] || continue
  iname="$(basename "$impl")"; iname="${iname%.sh}"
  st_out="$(cd "$REPO_ROOT" && timeout 300 bash "$impl" --selftest 2>&1)"; st_rc=$?
  printf '%s\t%s\t%s\t%s\n' "$iname" "--selftest" "exit=$st_rc $(printf '%s' "$st_out" | tail -1 | tr '\t\n' '  ' | cut -c1-200)" "exit=0" >> "$TMP/results.tsv"
  printf 'SELFTEST %s rc=%s :: %s\n' "$iname" "$st_rc" \
    "$(printf '%s' "$st_out" | tail -2 | tr '\n\t' '  ' | cut -c1-300)" >> "$TMP/transcript.txt"

  while IFS="$US" read -r f_case f_ledger f_target f_want f_reason f_exact f_contains f_mnb; do
    [ -n "$f_case" ] || continue
    got_out=""; RC=1; line=""
    for mode in fallback plain bare; do
      case "$mode" in
        fallback) got_out="$(cd "$REPO_ROOT" && timeout 60 env SOUJI_LEDGER="$f_ledger" bash "$impl" --ledger "$f_ledger" --fallback "$f_target" 2>&1)"; RC=$? ;;
        plain)    got_out="$(cd "$REPO_ROOT" && timeout 60 env SOUJI_LEDGER="$f_ledger" bash "$impl" --ledger "$f_ledger" "$f_target" 2>&1)"; RC=$? ;;
        bare)     got_out="$(cd "$REPO_ROOT" && timeout 60 env SOUJI_LEDGER="$f_ledger" bash "$impl" "$f_target" 2>&1)"; RC=$? ;;
      esac
      lines="$(printf '%s\n' "$got_out" \
        | grep -aE '^(VERDICT|VERIFIED|NOT-VERIFIED|NOT-SAFE|SAFE)' \
        | grep -av '<TAB>')"
      line="$(printf '%s\n' "$lines" | grep -av '^VERDICT' | head -1)"
      [ -n "$line" ] || line="$(printf '%s\n' "$lines" | head -1)"
      [ -n "$line" ] && [ "$RC" -ne 2 ] && break
    done
    got_line="$(printf '%s' "$line" | sed 's/\x1b\[[0-9;]*m//g' | tr '\t\n' '  ' | cut -c1-400)"
    if [ -z "$got_line" ]; then
      got_line="rc=$RC out=$(printf '%s' "$got_out" | head -c 220 | tr '\t\n' '  ')"
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$iname" "$f_case" "$f_target" "$got_line" "rc=$RC" >> "$TMP/results.tsv"
    printf 'CASE %s %s target=%s want=%s(%s) got=%s\n' "$iname" "$f_case" "$f_target" "$f_want" "$f_reason" "$got_line" >> "$TMP/transcript.txt"
  done < "$TMP/cases.tsv"
done < "$TMP/impls.txt"

# ---- live-surface fingerprints (after) --------------------------------------
LIVE_SHA_AFTER=$(sha256sum "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || echo missing)
LIVE_LINES_AFTER=$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ' || echo 0)
VAULT_FP_AFTER=$(vault_fp)
GUI_AFTER=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); GUI_AFTER=${GUI_AFTER:-0}

# ---- 3. judge + emit JSON ----------------------------------------------------
python3 - "$TMP/results.tsv" "$TMP/cases.tsv" "$OUT" "$TMP/impls.tsv" \
         "$LIVE_SHA_BEFORE" "$LIVE_SHA_AFTER" "$LIVE_LINES_BEFORE" "$LIVE_LINES_AFTER" \
         "$VAULT_FP_BEFORE" "$VAULT_FP_AFTER" "$GUI_BEFORE" "$GUI_AFTER" "$TMP/transcript.txt" <<'PYEOF'
import json, re, sys

res_path, cases_path, out_path, impls_path = sys.argv[1:5]
live_b, live_a, lines_b, lines_a, vfp_b, vfp_a, gui_b, gui_a = sys.argv[5:13]
transcript_path = sys.argv[13]
US = "\x1f"

def strip_ansi(s): return re.sub(r"\x1b\[[0-9;]*m", "", s or "")
def norm(s): return re.sub(r"[_ ]", "-", strip_ansi(s or "").strip().lower())
def toks(s):
    n = norm(s).replace("sha", "hash")
    return [p for p in re.split(r"[^a-z0-9]+", n) if p]
def vclass(s):
    s = strip_ansi(s or "")
    if "NOT-VERIFIED" in s or "NOT_VERIFIED" in s: return "NOT-VERIFIED"
    if re.search(r"\bVERIFIED\b", s): return "VERIFIED"
    if "NOT-SAFE" in s or "NOT_SAFE" in s: return "NOT-VERIFIED"
    if re.search(r"\bSAFE\b", s): return "VERIFIED"
    return None
def got_reason(line):
    line = strip_ansi(line or "")
    m = re.match(r"^\s*(?:NOT-VERIFIED|VERIFIED|NOT-SAFE|SAFE)\s*\(([^)]*)\)", line)
    if m: return m.group(1).strip()
    m = re.search(r"reason=(\S+)", line)
    if m: return m.group(1).strip()
    parts = line.split()
    if len(parts) >= 4 and parts[0].upper() == "VERDICT":
        return parts[3].strip()
    return ""
def contains_all(wants, gline):
    g = set(toks(gline))
    for w in wants:
        if not w: continue
        if str(w).upper() in ("VERIFIED", "NOT-VERIFIED", "NOT_VERIFIED", "SAFE", "NOT-SAFE"): continue
        if not set(toks(w)).issubset(g): return False
    return True

cases = {}
with open(cases_path) as f:
    for raw in f:
        p = raw.rstrip("\n").split(US)
        if len(p) < 8: continue
        cases[(p[0], p[2])] = {"ledger": p[1], "want": p[3], "reason": p[4],
                               "exact": json.loads(p[5]), "contains": json.loads(p[6]),
                               "mnb": json.loads(p[7])}

impl_meta = {}
with open(impls_path) as f:
    for raw in f:
        p = raw.rstrip("\n").split("\t")
        if len(p) >= 3: impl_meta[p[0]] = {"sha256": p[1], "syntax": p[2]}

rows = []
counts = {"pass": 0, "fail": 0}
per_impl = {}
CLASS_TOKENS = ("VERIFIED", "NOT-VERIFIED", "NOT_VERIFIED", "SAFE", "NOT-SAFE")

def case_lookup(cid, target):
    c = cases.get((cid, target))
    if c is not None: return c
    for (cid2, t2), v in cases.items():
        if cid2 == cid: return v
    return None

for raw in open(res_path):
    p = raw.rstrip("\n").split("\t")
    if len(p) < 4: continue
    impl = p[0]
    if p[1] == "--selftest":
        got_line, want = p[2], p[3]
        ok = got_line.startswith("exit=0")
        rows.append({"impl": impl, "case": "--selftest", "pass": bool(ok),
                     "got": got_line, "want": want})
        per_impl.setdefault(impl, [0, 0])
        per_impl[impl][1] += 1
        per_impl[impl][0] += 1 if ok else 0
        counts["pass" if ok else "fail"] += 1
        continue
    if len(p) < 5:
        rows.append({"impl": impl, "case": p[1], "pass": False,
                     "got": p[2], "want": "malformed-row"})
        per_impl.setdefault(impl, [0, 0]); per_impl[impl][1] += 1
        counts["fail"] += 1
        continue
    case, target, got_line, rc = p[1], p[2], p[3], p[4]
    c = case_lookup(case, target)
    if c is None:
        rows.append({"impl": impl, "case": case, "pass": False,
                     "got": got_line, "want": "unknown-case"})
        per_impl.setdefault(impl, [0, 0]); per_impl[impl][1] += 1
        counts["fail"] += 1
        continue
    gcls = vclass(got_line)
    greason = got_reason(got_line)
    gstr = f"{gcls}({greason})" if gcls and greason else (gcls or got_line)
    wcls = c["want"]; reason = c["reason"]; exact = c["exact"]
    contains = c["contains"]; mnb = c["mnb"]
    if re.match(r"^rc=", got_line or ""):
        p_ok = False
        rows.append({"impl": impl, "case": case, "pass": False,
                     "got": got_line, "want": (wcls if not reason else f"{wcls}({reason})")})
        per_impl.setdefault(impl, [0, 0]); per_impl[impl][1] += 1
        counts["fail"] += 1
        continue
    bad = False
    for tok in mnb:
        t = str(tok).strip()
        if not t: continue
        if t in ("VERIFIED", "SAFE"):
            if gcls == "VERIFIED": bad = True
        elif t in ("NOT-VERIFIED", "NOT-VERIFIED(none)"):
            if gcls == "NOT-VERIFIED" and "none" in t and "none" in greason: bad = True
        elif "(" in t:
            if norm(gstr) == norm(t): bad = True
        else:
            if t in got_line and ("NOT-" + t) not in got_line: bad = True
    if bad or gcls is None:
        p_ok = False
    else:
        cls_ok = (gcls == wcls)
        reason_ok = (not reason) or wcls == "VERIFIED" \
            or norm(reason) in norm(got_line) \
            or set(toks(reason)).issubset(set(toks(got_line)))
        contains_ok = contains_all(contains, got_line)
        if exact:
            exact_ok = norm(gstr) in [norm(e) for e in exact]
            if not exact_ok:
                toks2 = [x for x in contains if str(x).upper() not in CLASS_TOKENS]
                exact_ok = cls_ok and all(
                    norm(x) in norm(got_line) or set(toks(x)).issubset(set(toks(got_line)))
                    for x in toks2)
        else:
            exact_ok = True
        p_ok = cls_ok and reason_ok and contains_ok and exact_ok
    want_disp = wcls if not reason else f"{wcls}({reason})"
    rows.append({"impl": impl, "case": case, "pass": bool(p_ok),
                 "got": got_line, "want": want_disp})
    per_impl.setdefault(impl, [0, 0])
    per_impl[impl][1] += 1
    per_impl[impl][0] += 1 if p_ok else 0
    counts["pass" if p_ok else "fail"] += 1

live_ok = (live_b == live_a) and (lines_b == lines_a)
vault_ok = (vfp_b == vfp_a)
gui_ok = (gui_b == gui_a)
sha_map = ", ".join(f"{k}={v['sha256'][:12]}" for k, v in sorted(impl_meta.items()))
meta_got = (f"impls={len(impl_meta)} rows={counts['pass'] + counts['fail']} "
            f"pass={counts['pass']} fail={counts['fail']} "
            f"live_ledger_unchanged={str(live_ok).lower()} header_only={lines_a == '1'} "
            f"vault_manifest_unchanged={str(vault_ok).lower()} gui_count={gui_a} "
            f"impl_shas={sha_map}")
meta_want = ("runner=tests/vault/runner-25.sh judge=class+reason-token(hash=sha)+"
             "accept.contains+scoped-must_not_be; selftest pass iff exit=0")
meta = {"impl": "-", "case": "--meta", "pass": None, "got": meta_got, "want": meta_want}
doc = [meta] + rows
tmp_out = out_path + ".tmp"
with open(tmp_out, "w") as f:
    json.dump(doc, f, indent=1)
    f.write("\n")
import os
os.replace(tmp_out, out_path)

print(json.dumps({"rows": len(rows), "counts": counts,
                  "per_impl": {k: f"{v[0]}/{v[1]}" for k, v in sorted(per_impl.items())},
                  "live_ledger_unchanged": live_ok, "vault_unchanged": vault_ok,
                  "gui_before_after": [gui_b, gui_a]}))
PYEOF

log "S25 runner: wrote $OUT"
