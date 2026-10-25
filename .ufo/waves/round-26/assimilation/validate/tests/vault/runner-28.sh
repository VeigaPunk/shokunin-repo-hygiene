#!/usr/bin/env bash
# tests/vault/runner-28.sh — S28 runner, souji round 4 (Obsidian-CLI vault
# verification). Seat contract: for each impl tools/souji-vault-verify.impl-*.sh
# (17..24): run --selftest (record exit) and run against every
# tests/vault/case-V* fixture with its ledger file; compare got vs
# expected.json. Emits tests/results/vrun-28.json as [{impl, case, pass, got,
# want}].
#
# Fixture interfaces (measured, heterogeneous by design):
#   builder  V1/V8:  make-fixture.sh --out DIR --ledger FILE --quiet
#                    stdout has FIXTURE_ROOT=<root> (V1) / FIXTURE_READY (V8)
#   builder  V2/V4/V5: make-fixture.sh --out DIR --ledger FILE --quiet
#                    stdout has FIXTURE_READY <case> <root>; writes
#                    <root>/expected.json (substituted) + <root>/ledger.tsv
#   builder  V6:     build.sh already ran in-tree; probes[] drive r2-style
#                    SAFE/NOT-SAFE vocabulary (mapped to VERIFIED/NOT-VERIFIED)
#   expected.json shapes: dict-targets (V1), list-targets+list-expect
#                    (V2/V4/V5/V8), probes (V6). accept.exact/contains and
#                    must_not_be honored with scoping.
#
# Tool output contract (from the dispatch + S27 reference impl):
#   VERIFIED\t<target>\treceipt=... / NOT-VERIFIED\t<target>\treason=...
#
# Independence: builders run into /tmp only; nothing under the lane or the
# real vault is written. Read-only over everything else.
#
# usage: runner-28.sh [--wait SECS] [--out PATH] [--keep]
# exit: 0 matrix complete; 1 nothing to run; 2 usage
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$REPO_ROOT/tests/results/vrun-28.json"
WAIT=0
KEEP=0
TMP="$(mktemp -d "${TMPDIR:-/tmp}/souji28.XXXXXX")"
trap '[ "$KEEP" = 1 ] && echo "kept: $TMP" >&2 || rm -rf "$TMP"' EXIT
SEP=$'\x1f'

while [ $# -gt 0 ]; do
  case "$1" in
    --wait) WAIT="$2"; shift ;;
    --out) OUT="$2"; shift ;;
    --keep) KEEP=1 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "usage: $0 [--wait SECS] [--out PATH] [--keep]" >&2; exit 2 ;;
  esac
  shift
done

log() { printf '%s\n' "$*" >&2; }

impl_paths() {
  local p
  for p in "$REPO_ROOT"/tools/souji-vault-verify.impl-*.sh; do
    [ -e "$p" ] || continue
    printf '%s\n' "$p"
  done | sort -V
}

# --- wait for impls ---------------------------------------------------------
deadline=$(( $(date +%s) + WAIT ))
while :; do
  n=$(impl_paths | wc -l)
  [ "$n" -ge 8 ] && break
  [ "$(date +%s)" -ge "$deadline" ] && break
  sleep 10
done
# settle: 90s of count-stability so late impls are included
if [ "$(impl_paths | wc -l)" -lt 8 ]; then
  last=$(impl_paths | wc -l); stable=0
  while [ "$stable" -lt 9 ] && [ "$(impl_paths | wc -l)" -lt 8 ]; do
    sleep 10
    cur=$(impl_paths | wc -l)
    if [ "$cur" = "$last" ]; then stable=$((stable+1)); else stable=0; last=$cur; fi
  done
fi
n_impl=$(impl_paths | wc -l)
log "S28 runner: impls=$n_impl"
if [ "$n_impl" -eq 0 ]; then
  log "S28 runner: no impls to run"
  printf '[]\n' > "$OUT"
  exit 1
fi

# --- 1. build fixtures + extract (case, root, ledger, target, want, rules) --
python3 - "$REPO_ROOT" "$TMP" <<'PYEOF'
import json, os, re, subprocess, sys, glob

repo, tmp = sys.argv[1], sys.argv[2]
vault = os.path.join(repo, "tests", "vault")
rows = open(os.path.join(tmp, "cases.tsv"), "w")
notes = open(os.path.join(tmp, "prep-notes.txt"), "w")
US = "\x1f"

def log(m): print(m, file=notes)

def case_key(p):
    m = re.search(r"case-V(\d+)", p)
    return int(m.group(1)) if m else 99

def map_vocab(v):
    if not isinstance(v, str): return v
    v = v.strip().upper()
    if v == "SAFE": return "VERIFIED"
    if v in ("NOT-SAFE", "NOT_SAFE"): return "NOT-VERIFIED"
    return v

for case_dir in sorted(glob.glob(os.path.join(vault, "case-V*")), key=case_key):
    if not os.path.isdir(case_dir): continue
    case = os.path.basename(case_dir)
    maker = os.path.join(case_dir, "make-fixture.sh")
    exp_src = os.path.join(case_dir, "expected.json")
    root = None
    builder_out = ""
    mled = os.path.join(tmp, "ledgers", case + ".tsv")
    if os.path.isfile(maker):
        mroot = os.path.join(tmp, "roots", case)
        os.makedirs(os.path.dirname(mled), exist_ok=True)
        try:
            r = subprocess.run(["bash", maker, "--out", mroot, "--ledger", mled, "--quiet"],
                               cwd=case_dir, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            log(f"{case}: builder TIMEOUT"); r = None
        if r is not None and r.returncode == 2:
            # builder without --ledger support
            try:
                r = subprocess.run(["bash", maker, "--out", mroot, "--quiet"],
                                   cwd=case_dir, capture_output=True, text=True, timeout=300)
            except subprocess.TimeoutExpired:
                log(f"{case}: builder TIMEOUT"); r = None
        if r is not None and r.returncode == 2:
            try:
                r = subprocess.run(["bash", maker, "--quiet"],
                                   cwd=case_dir, capture_output=True, text=True, timeout=300)
            except subprocess.TimeoutExpired:
                log(f"{case}: builder TIMEOUT"); r = None
        if r is not None:
            builder_out = r.stdout or ""
            m = re.search(r"^FIXTURE_ROOT=(\S+)", builder_out, re.M)
            if m: root = m.group(1)
            if not root:
                m = re.search(r"^FIXTURE_READY\s+\S+\s+(\S+)", builder_out, re.M)
                if m:
                    cand = m.group(1)
                    root = cand if os.path.isdir(cand) else None
            if not root and os.path.isdir(mroot) and os.listdir(mroot):
                root = mroot
            log(f"{case}: builder rc={r.returncode} root={root}")
            if r.returncode not in (0, 2):
                log(f"{case}: builder stderr tail: {r.stderr.strip()[-300:]}")

    exp_path = None
    if root and os.path.isfile(os.path.join(root, "expected.json")):
        exp_path = os.path.join(root, "expected.json")
    elif os.path.isfile(exp_src):
        exp_path = exp_src
    if not exp_path:
        log(f"{case}: no expected.json (root={root}) — skipped")
        continue
    try:
        doc = json.load(open(exp_path))
    except Exception as e:
        log(f"{case}: expected.json unparsable ({exp_path}): {e} — skipped")
        continue

    ledger_default = None
    if root:
        cand = os.path.join(root, "ledger.tsv")
        if os.path.isfile(cand): ledger_default = cand
    if not ledger_default and os.path.isfile(mled):
        ledger_default = mled
    if not ledger_default:
        cand = doc.get("ledger") or doc.get("ledger_path")
        if isinstance(cand, str) and cand:
            cand = cand.replace("@FIXTURE_ROOT@", root or case_dir)
            if not os.path.isabs(cand): cand = os.path.join(root or case_dir, cand)
            if os.path.isfile(cand): ledger_default = cand
    if not ledger_default:
        m = re.search(r"^LEDGER_FILE=(\S+)", builder_out, re.M)
        if m and os.path.isfile(m.group(1)): ledger_default = m.group(1)
    if not ledger_default:
        m = re.search(r"^LEDGER=(\S+)", builder_out, re.M)
        if m and os.path.isfile(m.group(1)): ledger_default = m.group(1)

    must_nb = doc.get("must_not_be") or []
    applies = doc.get("must_not_be_applies_to") or ""
    mfn = re.search(r"([A-Za-z0-9._-]+\.(?:md|txt|payload))", applies)
    mfn = mfn.group(1) if mfn else None

    def veto_for(target_path):
        # No applies_to => the list applies to every target of the case
        # (V3's must_not_be_note states exactly this); otherwise only to the
        # named primary target (V2/V7 style).
        if mfn is None:
            return must_nb
        return must_nb if os.path.basename(target_path) == mfn else []

    def emit(case_id, ledger, target, want, reason, acc, is_primary=True, contains=None, veto_scope=None):
        t = str(target).replace("@FIXTURE_ROOT@", root or case_dir)
        if not os.path.isabs(t):
            t = os.path.join(root or case_dir, t)
        # case-level accept/must_not_be bind to the primary target only
        use_acc = acc if is_primary else {}
        if contains and not use_acc.get("contains"):
            use_acc = dict(use_acc, contains=contains)
        scoped = veto_scope if veto_scope is not None else (must_nb if is_primary else [])
        fields = [case_id, root or "", ledger or "-", t, str(want or ""),
                  str(reason or ""),
                  json.dumps(use_acc.get("exact")) if use_acc.get("exact") else "",
                  json.dumps(use_acc.get("contains")) if use_acc.get("contains") else "",
                  json.dumps(scoped)]
        print(US.join(fields), file=rows)

    # Shape C: probes (V6) — ledger/target resolve against ROOT first
    if isinstance(doc.get("probes"), list):
        for pr in doc["probes"]:
            if not isinstance(pr, dict): continue
            pid = pr.get("id") or case
            pled = pr.get("ledger")
            ledger = None
            if pled:
                if os.path.isabs(pled):
                    ledger = pled
                else:
                    for base in (root, case_dir):
                        if base and os.path.isfile(os.path.join(base, pled)):
                            ledger = os.path.join(base, pled); break
                    if not ledger:
                        ledger = os.path.join(case_dir, pled)
            ptg = pr.get("target")
            if ptg and not os.path.isabs(ptg) and root:
                ptg = os.path.join(root, ptg)
            pr_acc = pr.get("accept") if isinstance(pr.get("accept"), dict) else {}
            acc_use = pr_acc or ({"exact": [map_vocab(pr.get("verdict"))]} if pr.get("verdict") else {})
            emit(case + "-" + str(pid), ledger, ptg,
                 map_vocab(pr.get("verdict")), pr.get("reason"), acc_use,
                 is_primary=True, contains=pr.get("contains"))
        continue

    # Shape A/B: targets list (str or dict) + expect (dict or list)
    targets = doc.get("targets") or []
    expect = doc.get("expect")
    if isinstance(expect, dict): expect = [expect]
    if not isinstance(expect, list): expect = []
    exp_by_path = {e.get("path"): e for e in expect if isinstance(e, dict) and e.get("path")}
    acc = doc.get("accept") if isinstance(doc.get("accept"), dict) else {}
    primary = doc.get("primary_target")
    if not primary and mfn:
        for t in targets:
            tp = t.get("path") if isinstance(t, dict) else t
            if tp and os.path.basename(str(tp)) == mfn:
                primary = tp; break
    if not primary:
        primary = targets[0].get("path") if targets and isinstance(targets[0], dict) else (targets[0] if targets else None)
    pairs = []
    for i, t in enumerate(targets):
        if isinstance(t, dict):
            e = t.get("expected") if isinstance(t.get("expected"), dict) else {}
            if not e and expect:
                e = expect[0] if len(expect) == 1 else (exp_by_path.get(t.get("path"), {}) if exp_by_path else {})
            pairs.append((t.get("path"), e))
        else:
            e = exp_by_path.get(t)
            if e is None and len(expect) == len(targets) and i < len(expect) and isinstance(expect[i], dict):
                e = expect[i]
            if e is None and len(expect) == 1 and isinstance(expect[0], dict):
                e = expect[0]
            pairs.append((t, e or {}))
    if not pairs:
        log(f"{case}: no targets parsed (keys={list(doc)[:14]}) — skipped")
        continue
    for t, e in pairs:
        if not t:
            log(f"{case}: target missing a path — skipped"); continue
        want = e.get("verdict") or e.get("expect") or e.get("expected")
        if isinstance(want, dict): want = want.get("verdict")
        want = map_vocab(want)
        is_primary = bool(primary) and (str(t) == str(primary))
        # per-target accept overrides the case-level accept block (V3 style);
        # the veto list keeps its own scoping from veto_for().
        e_acc = e.get("accept") if isinstance(e.get("accept"), dict) else {}
        if not e_acc and e.get("contains"):
            e_acc = {"contains": e.get("contains")}
        if e_acc:
            emit(case, ledger_default, t, want, e.get("reason"), e_acc,
                 is_primary=True, veto_scope=veto_for(str(t)))
        else:
            emit(case, ledger_default, t, want, e.get("reason"), acc,
                 is_primary=is_primary, veto_scope=veto_for(str(t)))

rows.close(); notes.close()
PYEOF

cat "$TMP/prep-notes.txt" >&2 2>/dev/null || true
n_rows=$(wc -l < "$TMP/cases.tsv")
log "S28 runner: prepared $n_rows fixture target rows"

# --- 2. execute matrix ------------------------------------------------------
: > "$TMP/results.tsv"
impl_paths > "$TMP/impls.txt"
: > "$TMP/transcript.txt"
: > "$TMP/impl-shas.txt"
while IFS= read -r impl; do
  [ -n "$impl" ] || continue
  printf '%s\t%s\n' "$(basename "$impl")" "$(sha256sum "$impl" | cut -d' ' -f1)" >> "$TMP/impl-shas.txt"
done < "$TMP/impls.txt"

while IFS= read -r impl; do
  [ -n "$impl" ] || continue
  iname="$(basename "$impl")"; iname="${iname%.sh}"
  st_out="$(cd "$REPO_ROOT" && timeout 300 bash "$impl" --selftest 2>&1)"; st_rc=$?
  printf '%s\t%s\t%s\t%s\t%s\n' "$iname" "--selftest" \
    "$([ "$st_rc" -eq 0 ] && echo true || echo false)" "exit=$st_rc" "exit=0" >> "$TMP/results.tsv"
  printf '%s' "$st_out" > "$TMP/st-${iname}.log"
  printf 'SELFTEST %s rc=%s :: %s\n' "$iname" "$st_rc" \
    "$(printf '%s' "$st_out" | tail -2 | tr '\n\t' '  ')" >> "$TMP/transcript.txt"

  while IFS= read -r line; do
    [ -n "$line" ] || continue
    f_case=$(printf '%s' "$line" | cut -d"$SEP" -f1)
    f_root=$(printf '%s' "$line" | cut -d"$SEP" -f2)
    f_ledger=$(printf '%s' "$line" | cut -d"$SEP" -f3)
    f_target=$(printf '%s' "$line" | cut -d"$SEP" -f4)
    f_want=$(printf '%s' "$line" | cut -d"$SEP" -f5)
    f_reason=$(printf '%s' "$line" | cut -d"$SEP" -f6)
    f_exact=$(printf '%s' "$line" | cut -d"$SEP" -f7)
    f_contains=$(printf '%s' "$line" | cut -d"$SEP" -f8)
    f_mnb=$(printf '%s' "$line" | cut -d"$SEP" -f9)

    got_line=""; RC=1; OUT_TXT=""
    # argv shapes vary across impls: try explicit flags first, then env-only.
    for mode in fallback auto; do
      for shape in flags envonly plain; do
        case "$shape" in
          flags) OUT_TXT="$(cd "$REPO_ROOT" && timeout 60 env SOUJI_LEDGER="$f_ledger" \
                   bash "$impl" --ledger "$f_ledger" --"$mode" "$f_target" 2>&1)"; RC=$? ;;
          envonly) OUT_TXT="$(cd "$REPO_ROOT" && timeout 60 env SOUJI_LEDGER="$f_ledger" \
                   bash "$impl" --"$mode" "$f_target" 2>&1)"; RC=$? ;;
          plain) OUT_TXT="$(cd "$REPO_ROOT" && timeout 60 env SOUJI_LEDGER="$f_ledger" \
                   bash "$impl" "$f_target" 2>&1)"; RC=$? ;;
        esac
        if printf '%s' "$OUT_TXT" | grep -qaE 'unknown flag|unrecognized|usage:'; then
          continue
        fi
        break
      done
      # r4 vocabulary first line: VERIFIED(...) / NOT-VERIFIED(...)
      got_line="$(printf '%s\n' "$OUT_TXT" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -1)"
      # r2-form fallback: VERDICT<TAB>path<TAB>SAFE|NOT-SAFE<TAB>receipt<TAB>evidence
      if [ -z "$got_line" ]; then
        got_line="$(printf '%s\n' "$OUT_TXT" | grep -aE '^VERDICT' | head -1 | awk -F'\t' '{
          cls = ($3 == "SAFE") ? "VERIFIED" : "NOT-VERIFIED";
          r = $4; if (r == "") r = $5;
          if (r != "" && r != "none") printf "%s(%s)", cls, r; else printf "%s", cls
        }')"
      fi
      [ -n "$got_line" ] && break
    done
    if [ -z "$got_line" ]; then
      got_line="rc=$RC out=$(printf '%s' "$OUT_TXT" | head -c 220 | tr '\t\n' '  ')"
    fi
    got_line="$(printf '%s' "$got_line" | tr '\t\n' '  ' | cut -c1-300)"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$iname" "$f_case" "$got_line" \
      "$f_want" "$f_reason" "$f_exact" "$f_contains" "$f_mnb" >> "$TMP/results.tsv"
    printf 'CASE %s %s target=%s want=%s(%s) got=%s\n' "$iname" "$f_case" "$f_target" "$f_want" "$f_reason" "$got_line" >> "$TMP/transcript.txt"
  done < "$TMP/cases.tsv"
done < "$TMP/impls.txt"

# --- 3. judge + emit JSON ---------------------------------------------------
python3 - "$TMP/results.tsv" "$OUT" "$TMP/impls.txt" "$TMP/prep-notes.txt" "$TMP/impl-shas.txt" <<'PYEOF'
import json, sys, os, re

res_path, out_path, impls_path, notes_path, impls_sha_path = sys.argv[1:6]

def vclass(s):
    s = s or ""
    if "NOT-VERIFIED" in s or "NOT_VERIFIED" in s: return "NOT-VERIFIED"
    if re.search(r"\bNOT-SAFE\b", s) or "NOT_SAFE" in s: return "NOT-SAFE"
    if re.search(r"\bVERIFIED\b", s): return "VERIFIED"
    if re.search(r"\bSAFE\b", s): return "SAFE"
    return None

def norm(s):
    return re.sub(r"[_ ]", "-", (s or "").strip().lower())

def got_parts(line):
    line = (line or "").strip()
    cls = vclass(line)
    if not cls: return None, None
    # parenthesized reason may be a prefix: "NOT-VERIFIED(reason)\tpath\t..."
    m = re.match(r"^(NOT-VERIFIED|VERIFIED|NOT-SAFE|SAFE)\s*\(([^)]*)\)", line)
    if m: return m.group(1), m.group(2).strip()
    m = re.search(r"reason=(\S+)", line)
    if m: return cls, m.group(1)
    parts = line.split()
    if len(parts) >= 2 and "/" not in parts[1] and "=" not in parts[1]:
        return cls, parts[1]
    return cls, ""

rows = []
with open(res_path) as f:
    for raw in f:
        p = raw.rstrip("\n").split("\t")
        if len(p) < 5: continue
        impl, case = p[0], p[1]
        if case == "--selftest":
            rows.append({"impl": impl, "case": case, "pass": p[3] == p[4],
                         "got": p[3], "want": p[4]})
            continue
        got_line, want, reason = p[2], p[3], p[4]
        exact = json.loads(p[5]) if len(p) > 5 and p[5] else []
        contains = json.loads(p[6]) if len(p) > 6 and p[6] else []
        mnb = json.loads(p[7]) if len(p) > 7 and p[7] else []
        gcls, greason = got_parts(got_line)
        wcls = vclass(want)
        canon = {"SAFE": "VERIFIED", "NOT-SAFE": "NOT-VERIFIED"}
        gcanon = canon.get(gcls, gcls)
        gstr = f"{gcls}({greason})" if gcls and greason else (gcls or got_line)

        p_pass = None
        if gcls is None:
            p_pass = False
        else:
            # must_not_be (scoped already by the prep stage).
            # Bare class tokens veto by RAW class equality (so "VERIFIED" does
            # not veto the correct answer "NOT-VERIFIED(...)", and "SAFE" does
            # veto a SAFE answer); parenthesized tokens by exact normalized
            # string; other bare words by whole-reason equality.
            bad = False
            for tok in mnb:
                if not tok: continue
                t = tok.strip()
                if t in ("VERIFIED", "SAFE", "NOT-VERIFIED", "NOT-SAFE"):
                    if gcls == t: bad = True
                elif "(" in t:
                    if norm(gstr) == norm(t): bad = True
                else:
                    if norm(greason) == norm(t): bad = True
            if bad:
                p_pass = False
            else:
                reason_ok = (not reason) or (norm(reason) in norm(got_line))
                toks = [c for c in contains
                        if c and c.upper() not in ("VERIFIED", "NOT-VERIFIED", "NOT_VERIFIED", "SAFE", "NOT-SAFE")]
                contains_ok = all(norm(c) in norm(got_line) for c in toks)
                if exact:
                    # a bare-class exact entry ("VERIFIED") matches any reason;
                    # a parenthesized entry matches the exact verdict string.
                    ex_ok = False
                    for e in exact:
                        ne = norm(e)
                        if ne in ("verified", "safe"):
                            if gcanon == "VERIFIED": ex_ok = True
                        elif ne in ("not-verified", "not-safe"):
                            if gcanon == "NOT-VERIFIED": ex_ok = True
                        elif ne == norm(gstr):
                            ex_ok = True
                    p_pass = ex_ok and contains_ok
                elif contains:
                    p_pass = (gcanon == wcls) and contains_ok
                else:
                    p_pass = (gcanon == wcls) and reason_ok
        want_disp = want if not reason else f"{want}({reason})"
        rows.append({"impl": impl, "case": case, "pass": bool(p_pass),
                     "got": got_line, "want": want_disp})

try:
    notes = open(notes_path).read().strip().splitlines()
except Exception:
    notes = []
try:
    shas = dict(l.rstrip("\n").split("\t") for l in open(impls_sha_path) if "\t" in l)
except Exception:
    shas = {}
meta = {"impl": "-", "case": "--meta", "pass": None,
        "got": f"runner=tests/vault/runner-28.sh cases={len({r['case'] for r in rows if r['case'] != '--selftest'})}",
        "want": f"fixtures: {'; '.join(notes[-14:])[:900]}",
        "impl_sha256": shas}
json.dump([meta] + rows, open(out_path, "w"), indent=1)
per = {}
for r in rows:
    per.setdefault(r["impl"], [0, 0])
    per[r["impl"]][1] += 1
    per[r["impl"]][0] += 1 if r["pass"] else 0
print(json.dumps({"rows": len(rows), "impls": len(per),
                  "per_impl": {k: f"{v[0]}/{v[1]}" for k, v in sorted(per.items())}}))
PYEOF

log "S28 runner: wrote $OUT"
