#!/usr/bin/env bash
# tests/vault/runner-26.sh — S26 runner, souji round 4 (Obsidian-CLI vault
# verification). Seat contract: for each candidate tools/souji-vault-verify*.sh
# (or --impls filter), run --selftest (record exit) and run every
# tests/vault/case-V* fixture target with its ledger; compare got vs the
# fixture's expected.json. Emits tests/results/vrun-26.json as
# [{impl, case, pass, got, want}] (S57 aggregator schema).
#
# Independence: builds each case with its own make-fixture.sh under /tmp,
# never writes tests/vault/ledger-*.tsv (all ledgers go to the scratch dir),
# mutates nothing outside /tmp. Read-only over the lane, the live ledger and
# the real vault. Never executes /usr/bin/obsidian (GUI launcher): only
# stat/pgrep.
#
# usage: runner-26.sh [--wait SECS] [--out PATH] [--impls "PATTERN"] [--keep]
# exit: 0 matrix complete | 1 nothing to run after wait | 2 usage
set -uo pipefail
export LC_ALL=C

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$REPO_ROOT/tests/results/vrun-26.json"
WAIT=0
IMPL_GLOB="souji-vault-verify*.sh"
KEEP=0

while [ $# -gt 0 ]; do
  case "$1" in
    --wait) WAIT="${2:-0}"; shift ;;
    --out) OUT="${2:?}"; shift ;;
    --impls) IMPL_GLOB="${2:?}"; shift ;;
    --keep) KEEP=1 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "usage: $0 [--wait SECS] [--out PATH] [--impls GLOB] [--keep]" >&2; exit 2 ;;
  esac
  shift
done

TMP="$(mktemp -d /tmp/souji26-vault.XXXXXX)"
case "$TMP" in /tmp/souji26-vault.*) : ;; *) echo "refusing: TMP=$TMP" >&2; exit 9 ;; esac
cleanup() { [ "$KEEP" = 1 ] || rm -rf "$TMP"; }
trap cleanup EXIT
log() { printf '%s\n' "$*" >&2; }

impl_paths() {
  local pat p
  for pat in $IMPL_GLOB; do
    for p in "$REPO_ROOT"/tools/$pat; do
      [ -f "$p" ] && readlink -f -- "$p"
    done
  done | sort -u
}
case_dirs() {
  local d
  for d in "$REPO_ROOT"/tests/vault/case-V*; do
    [ -d "$d" ] && [ -f "$d/expected.json" ] && printf '%s\n' "$d"
  done | sort -V
}

# ---- wait for impls + cases -------------------------------------------------
deadline=$(( $(date +%s) + WAIT ))
while :; do
  n_impl=$(impl_paths | wc -l)
  n_case=$(case_dirs | wc -l)
  [ "$n_impl" -gt 0 ] && [ "$n_case" -gt 0 ] && break
  now=$(date +%s)
  [ "$now" -ge "$deadline" ] && break
  sleep 10
done
n_impl=$(impl_paths | wc -l)
n_case=$(case_dirs | wc -l)
log "S26 runner: impls=$n_impl cases-with-expected=$n_case"
if [ "$n_impl" -eq 0 ] || [ "$n_case" -eq 0 ]; then
  log "S26 runner: nothing to run (impls=$n_impl cases=$n_case)"
  printf '[]\n' > "$OUT"
  exit 1
fi

# ---- build each case into the scratch dir ----------------------------------
# rows.tsv: case<TAB>ledger<TAB>target<TAB>want_class<TAB>want_string<TAB>accept_contains<TAB>must_not_be
python3 - "$REPO_ROOT" "$TMP" <<'PYEOF'
import json, os, re, subprocess, sys

repo, tmp = sys.argv[1], sys.argv[2]
vault_dir = os.path.join(repo, "tests", "vault")
rows = open(os.path.join(tmp, "cases.tsv"), "w")
notes = open(os.path.join(tmp, "prep-notes.txt"), "w")

def norm_class(v):
    if not isinstance(v, str):
        return None
    u = v.strip().upper()
    u = u.replace("NOT-VERIFIED", "NOT_VERIFIED").replace("NOT VERIFIED", "NOT_VERIFIED")
    if "NOT_VERIFIED" in u or "NOT-SAFE" in u.replace("_", "-"):
        return "NOT-VERIFIED"
    if u.startswith("NOT-SAFE") or u.startswith("NOT_SAFE"):
        return "NOT-VERIFIED"
    if re.search(r"\bVERIFIED\b", u) or re.search(r"\bSAFE\b", u):
        return "VERIFIED"
    return None

for case_dir in sorted(os.listdir(vault_dir)):
    if not case_dir.startswith("case-V"):
        continue
    cd = os.path.join(vault_dir, case_dir)
    if not os.path.isdir(cd):
        continue
    exp_src = os.path.join(cd, "expected.json")
    if not os.path.isfile(exp_src):
        continue
    case = case_dir[len("case-"):] if case_dir.startswith("case-") else case_dir
    maker = None
    for cand_name in ("make-fixture.sh", "build.sh", "make.sh"):
        cand = os.path.join(cd, cand_name)
        if os.path.isfile(cand):
            maker = cand
            break
    root = None
    out_dir = os.path.join(tmp, case_dir)
    ledger = os.path.join(tmp, case + "-ledger.tsv")
    if maker:
        r = None
        base = os.path.basename(maker)
        if base == "make-fixture.sh":
            forms = [["--out", out_dir, "--ledger", ledger, "--quiet"],
                     ["--out", out_dir, "--ledger", ledger],
                     ["--quiet"], []]
        else:
            # build.sh-style builders take a positional dest dir
            forms = [[out_dir], ["--out", out_dir], []]
        for args in forms:
            try:
                r = subprocess.run(["bash", maker] + args, cwd=cd, capture_output=True, text=True, timeout=300)
            except Exception as e:
                notes.write(f"{case}: builder error {e}\n"); r = None; break
            if r.returncode == 2 and args:
                continue
            break
        if r is not None:
            notes.write(f"{case}: builder rc={r.returncode} args={' '.join(args)}\n")
            m = re.search(r"FIXTURE_READY\s+\S+\s+(\S+)", r.stdout)
            if m:
                root = m.group(1)
            else:
                for key in ("FIXTURE_ROOT", "ROOT"):
                    m = re.search(rf"^{key}=(\S+)\s*$", r.stdout, re.M)
                    if m:
                        root = m.group(1); break
            if not root:
                if os.path.isdir(out_dir) and os.listdir(out_dir):
                    root = out_dir
                elif os.path.isdir(os.path.join(cd, "src")) or os.path.isdir(os.path.join(cd, "vault")):
                    root = cd
            if r.returncode != 0:
                notes.write(f"{case}: builder stderr tail: {r.stderr.strip()[-300:]}\n")
    exp_path = os.path.join(root, "expected.json") if root else None
    if not exp_path or not os.path.isfile(exp_path):
        for cand in (os.path.join(cd, "expected.json"), os.path.join(cd, "expected.template.json"),
                     os.path.join(root, "expected.template.json") if root else ""):
            if cand and os.path.isfile(cand):
                exp_path = cand
                break
    try:
        with open(exp_path) as fh:
            raw_doc = fh.read()
        if "@FIXTURE_ROOT@" in raw_doc and root:
            raw_doc = raw_doc.replace("@FIXTURE_ROOT@", root)
        doc = json.loads(raw_doc)
    except Exception as e:
        notes.write(f"{case}: expected.json unparsable ({exp_path}): {e}\n"); continue

    # ledger discovery: builder --ledger arg > <ROOT>/ledger.tsv > doc ledger_path
    lg = ledger if os.path.isfile(ledger) else None
    if not lg and root:
        for cand in (os.path.join(root, "ledger.tsv"),):
            if os.path.isfile(cand):
                lg = cand
    if not lg:
        cand = doc.get("ledger_path") or doc.get("ledger")
        if isinstance(cand, str) and cand:
            cand = cand.replace("@FIXTURE_ROOT@", root or cd)
            if not os.path.isabs(cand):
                cand = os.path.join(root or cd, cand)
            if os.path.isfile(cand):
                lg = cand
    # ledger may live in the case dir too
    if not lg:
        for cand in (os.path.join(cd, "ledger.tsv"),):
            if os.path.isfile(cand):
                lg = cand

    # probes[] schema (case-V6): probes carry their own ledger/target/verdict
    probes = doc.get("probes")
    if isinstance(probes, list) and probes:
        for pr in probes:
            if not isinstance(pr, dict):
                continue
            t = pr.get("target")
            if not t:
                continue
            if not os.path.isabs(str(t)):
                t = os.path.join(root or cd, str(t))
            plg = pr.get("ledger")
            if plg:
                plg = str(plg).replace("@FIXTURE_ROOT@", root or cd)
                if not os.path.isabs(plg):
                    plg = os.path.join(root or cd, plg)
            want = pr.get("verdict")
            reason = pr.get("reason")
            want_s = str(want) if want is not None else ""
            if reason and "(" not in want_s:
                want_s = f"{want_s}({reason})"
            contains = pr.get("contains") or []
            ev = pr.get("evidence_substr")
            if ev:
                contains = list(contains) + [ev]
            print("\t".join([case + "-" + str(pr.get("id", "")), plg or lg or "-", str(t), want_s,
                             json.dumps(contains), "[]"]), file=rows)
        continue

    targets = doc.get("targets") or []
    expect = doc.get("expect")
    if isinstance(expect, dict):
        expect = [expect]
    if not isinstance(expect, list):
        expect = []
    exp_by_path = {e.get("path"): e for e in expect if isinstance(e, dict) and e.get("path")}
    pairs = []
    for t in targets:
        if isinstance(t, dict):
            tpath = t.get("path")
            e = dict(t.get("expected") or {})
            for k in ("verdict", "reason", "must_not_be"):
                if k in t and k not in e:
                    e[k] = t[k]
            if not e and exp_by_path.get(tpath):
                e = exp_by_path[tpath]
            pairs.append((tpath, e))
        else:
            e = exp_by_path.get(t) or (expect[targets.index(t)] if len(expect) == len(targets) else {})
            pairs.append((t, e))
    if not pairs:
        want = doc.get("verdict") or doc.get("expect_string") or doc.get("expected")
        src = doc.get("source_path") or doc.get("target")
        if src and want:
            pairs = [(src, {"path": src, "verdict": want})]
    if not pairs:
        notes.write(f"{case}: no targets parsed (keys={list(doc)[:14]})\n"); continue

    acc = doc.get("accept") if isinstance(doc.get("accept"), dict) else {}
    primary = str(doc.get("primary_target") or "").replace("@FIXTURE_ROOT@", root or cd)
    for t, e in pairs:
        t = str(t).replace("@FIXTURE_ROOT@", root or cd)
        want = e.get("verdict") or e.get("expect") or e.get("expected")
        if isinstance(want, dict):
            want = want.get("verdict")
        reason = e.get("reason")
        want_s = str(want) if want is not None else ""
        if reason and "(" not in want_s:
            want_s = f"{want_s}({reason})"
        contains = e.get("contains") or []
        if not contains:
            # doc-level accept.contains binds to the primary target (or the
            # only target); other rows keep only their own constraints
            if (primary and t == primary) or len(pairs) == 1:
                contains = acc.get("contains") or []
        must_not = e.get("must_not_be") or doc.get("must_not_be") or []
        print("\t".join([case, lg or "-", t, want_s,
                         json.dumps(contains), json.dumps(must_not)]), file=rows)
notes.write(f"prepared\n")
rows.close(); notes.close()
PYEOF
cat "$TMP/prep-notes.txt" >&2 2>/dev/null || true
n_rows=$(grep -c . "$TMP/cases.tsv" || true)
log "S26 runner: prepared $n_rows target rows"
if [ "$n_rows" -eq 0 ]; then
  printf '[]\n' > "$OUT"; exit 1
fi

# ---- live-surface fingerprints (read-only proof) ---------------------------
LIVE_LEDGER="$REPO_ROOT/corpus/knowledge/obsidian-ledger.tsv"
LIVE_SHA_BEFORE=$(sha256sum "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || echo missing)
REAL_VAULT=/home/vgpnk/Documents/shokoknowledge
VAULT_FP_BEFORE=$(find "$REAL_VAULT" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 2>/dev/null | sort -z | xargs -0 -r sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1)
GUI_BEFORE=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); GUI_BEFORE=${GUI_BEFORE:-0}

# ---- run matrix ------------------------------------------------------------
: > "$TMP/results.tsv"
impl_paths > "$TMP/impls.txt"
while IFS= read -r impl; do
  [ -n "$impl" ] || continue
  iname="$(basename "$impl")"; iname="${iname%.sh}"
  isha=$(sha256sum "$impl" | cut -d' ' -f1)
  st_out=$(timeout 300 bash "$impl" --selftest 2>&1); st_rc=$?
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$iname" "--selftest" \
    "exit=$st_rc" "exit=0" "[]" "[]" "-" >> "$TMP/results.tsv"
  printf '%s' "$st_out" > "$TMP/st-${iname}.log"
  printf '%s\t%s\n' "$iname" "$isha" >> "$TMP/implshas.tsv"

  while IFS=$'\t' read -r case ledger target want contains mustnot; do
    [ -n "$case" ] || continue
    got_out=""; got_rc=1
    got_out=$(timeout 60 env SOUJI_LEDGER="$ledger" bash "$impl" --ledger "$ledger" --fallback "$target" 2>&1); got_rc=$?
    if [ "$got_rc" -eq 2 ]; then
      got_out=$(timeout 60 env SOUJI_LEDGER="$ledger" bash "$impl" --ledger "$ledger" "$target" 2>&1); got_rc=$?
    fi
    if [ "$got_rc" -eq 2 ]; then
      got_out=$(timeout 60 env SOUJI_LEDGER="$ledger" bash "$impl" "$target" 2>&1); got_rc=$?
    fi
    got_line=$(printf '%s\n' "$got_out" | grep -aE '^(VERIFIED|NOT-VERIFIED)' | head -1)
    [ -z "$got_line" ] && got_line=$(printf '%s\n' "$got_out" | grep -aE '^(VERDICT|SAFE|NOT-SAFE)' | head -1)
    [ -z "$got_line" ] && got_line="rc=$got_rc out=$(printf '%s' "$got_out" | head -c 200 | tr '\t\n' '  ')"
    got_enc=${got_line//$'\t'/\\t}
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$iname" "$case" "$got_enc" "$want" "$contains" "$mustnot" "$ledger" >> "$TMP/results.tsv"
  done < "$TMP/cases.tsv"
done < "$TMP/impls.txt"

# ---- live-surface check (after) --------------------------------------------
LIVE_SHA_AFTER=$(sha256sum "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || echo missing)
VAULT_FP_AFTER=$(find "$REAL_VAULT" -type f -not -path '*/.git/*' -not -path '*/.obsidian/*' -print0 2>/dev/null | sort -z | xargs -0 -r sha256sum 2>/dev/null | sha256sum | cut -d' ' -f1)
GUI_AFTER=$(pgrep -fc '/usr/lib/obsidian/app\.asar' 2>/dev/null || true); GUI_AFTER=${GUI_AFTER:-0}

# ---- judge + emit JSON ------------------------------------------------------
python3 - "$TMP/results.tsv" "$OUT" "$TMP/cases.tsv" "$LIVE_SHA_BEFORE" "$LIVE_SHA_AFTER" "$VAULT_FP_BEFORE" "$VAULT_FP_AFTER" "$GUI_BEFORE" "$GUI_AFTER" "$TMP/implshas.tsv" "$REPO_ROOT" <<'PYEOF'
import json, re, sys

res_path, out_path, cases_path = sys.argv[1:4]
live_b, live_a, vfp_b, vfp_a, gui_b, gui_a = sys.argv[4:10]
shas_path, repo = sys.argv[10:12]

def vclass(s):
    s = s or ""
    # r2 tool format: VERDICT<TAB>path<TAB>CLASS<TAB>receipt<TAB>evidence
    parts = s.split("\t")
    if parts and parts[0].strip() == "VERDICT" and len(parts) >= 3:
        s = parts[2]
    if "NOT-VERIFIED" in s or "NOT_VERIFIED" in s or re.search(r"\bNOT-SAFE\b", s):
        return "NOT-VERIFIED"
    if re.search(r"\bVERIFIED\b", s) or re.search(r"\bSAFE\b", s):
        return "VERIFIED"
    return None

def norm(s):
    s = (s or "").strip()
    parts = s.split("\t")
    if parts and parts[0].strip() == "VERDICT" and len(parts) >= 4:
        # keep path + class + receipt for readability: CLASS(receipt)
        cls, receipt = parts[2].strip(), parts[3].strip()
        return f"{cls}({receipt})" if receipt and receipt != "none" else cls
    m = re.match(r"^(NOT-VERIFIED|VERIFIED|NOT-SAFE|SAFE)\s*\((.*)\)\s*$", s)
    if m:
        return f"{m.group(1)}({m.group(2).strip()})"
    return s

REASON_ALT = r'(?:hash|sha256|sha|digest)'

def token_pattern(tok):
    """Reason tokens tolerate hash/sha/digest spellings: source-hash matches
    source-sha-mismatch, vault-hash-mismatch matches vault-sha-mismatch."""
    parts = tok.split('-')
    pat = []
    for p in parts:
        if p.lower() in ('hash', 'sha', 'sha256', 'digest'):
            pat.append(REASON_ALT)
        else:
            pat.append(re.escape(p))
    return '-'.join(pat)

def contains_hit(token, got_line, got_cls):
    tok = token.strip()
    if not tok:
        return True
    tu = tok.upper()
    if tu in ('SAFE', 'VERIFIED'):
        return got_cls == 'VERIFIED'
    if tu in ('NOT-SAFE', 'NOT-VERIFIED', 'NOT_SAFE', 'NOT_VERIFIED'):
        return got_cls == 'NOT-VERIFIED'
    return re.search(token_pattern(tok), got_line) is not None

def mustnot_hit(token, got_line, got_cls):
    tok = token.strip()
    if not tok:
        return False
    tu = tok.upper()
    first = got_line.split('\t')[0].strip()
    if tu in ('SAFE', 'VERIFIED'):
        return got_cls == 'VERIFIED'
    if tu.startswith('NOT-SAFE') or tu.startswith('NOT_SAFE'):
        # vocabulary ban: the r2 class token itself must not be emitted
        return first.upper() == 'NOT-SAFE'
    if tu.startswith('NOT-VERIFIED') or tu.startswith('NOT_VERIFIED'):
        if got_cls != 'NOT-VERIFIED':
            return False
        m = re.match(r'^NOT[-_]VERIFIED\s*\((.*)\)\s*$', first, re.I)
        if not m:
            return False
        reason_tok = tok[tok.find('(') + 1:tok.rfind(')')] if '(' in tok else ''
        if not reason_tok:
            return True
        return re.search(token_pattern(reason_tok), m.group(1)) is not None
    return re.search(re.escape(tok), got_line) is not None

want_meta = {}
with open(cases_path) as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 6:
            want_meta[p[0]] = {"want": p[3], "contains": p[4], "mustnot": p[5]}

shas = {}
for line in open(shas_path):
    p = line.rstrip("\n").split("\t")
    if len(p) == 2:
        shas[p[0]] = p[1]

rows = []
with open(res_path) as f:
    for raw in f:
        p = raw.rstrip("\n").split("\t")
        if len(p) < 5:
            continue
        impl, case, got_line, want, contains = p[:5]
        got_line = got_line.replace("\\t", "\t")
        mustnot = p[5] if len(p) > 5 else "[]"
        want_s = want.strip()
        want_cls = vclass(want_s) or want_s
        got_cls = vclass(got_line)
        # strict r4 vocabulary: a pass requires the literal VERIFIED /
        # NOT-VERIFIED token in the tool's own output (SAFE/NOT-SAFE is the
        # r2 baseline vocabulary and is recorded but never counted as pass)
        first_tok = got_line.split('\t')[0].strip().split('(')[0].strip().upper().replace('_', '-')
        r4_vocab = first_tok in ('VERIFIED', 'NOT-VERIFIED')
        pass_ = False
        detail = ""
        if case == "--selftest":
            pass_ = (got_line == "exit=0")
        elif not r4_vocab:
            detail = f"r2 vocabulary ({first_tok or 'no verdict'}) != r4 VERIFIED/NOT-VERIFIED"
        else:
            if got_cls is None:
                detail = "unparsable verdict"
            elif got_cls != want_cls:
                detail = f"class {got_cls} != {want_cls}"
            else:
                ok = True
                # doc-level must_not_be describes the NOT-VERIFIED expectation;
                # a case may carry a positive control target inside it (V2's
                # matched-notes), which must not be judged by that list
                mn = json.loads(mustnot or "[]")
                if want_cls != "NOT-VERIFIED":
                    mn = []
                try:
                    for c in json.loads(contains or "[]"):
                        if c and not contains_hit(c, got_line, got_cls):
                            ok = False; detail = f"missing contains {c!r}"
                    for m in mn:
                        if m and mustnot_hit(m, got_line, got_cls):
                            ok = False; detail = f"must_not_be hit {m!r}"
                except Exception:
                    pass
                pass_ = ok
        rows.append({"impl": impl, "impl_sha256": shas.get(impl, ""), "case": case,
                     "pass": pass_, "got": norm(got_line), "want": want_s,
                     "vocab": "r4" if r4_vocab else "r2", "detail": detail})

summary = {}
for r in rows:
    if r["case"] == "--selftest":
        continue
    s = summary.setdefault(r["impl"], {"pass": 0, "fail": 0})
    s["pass" if r["pass"] else "fail"] += 1
report = {
    "seat": "S26",
    "round": 4,
    "role": "runner",
    "kind": "vault-verify-matrix",
    "generated_at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
    "schema_note": "rows: [{impl, case, pass, got, want}] + --selftest rows; S57 aggregator compatible",
    "rows": rows,
    "summary": summary,
    "live_ledger": {"sha_before": live_b, "sha_after": live_a, "unchanged": live_b == live_a},
    "real_vault": {"fingerprint_before": vfp_b, "fingerprint_after": vfp_a, "unchanged": vfp_b == vfp_a},
    "gui_processes": {"before": gui_b, "after": gui_a, "unchanged": gui_b == gui_a,
                      "note": "/usr/bin/obsidian (GUI launcher) never executed; pgrep count only"},
    "impl_shas": shas,
}
json.dump(report, open(out_path, "w"), indent=1)
print(json.dumps({"out": out_path, "rows": len(rows), "summary": summary}))
PYEOF
rc=$?
log "S26 runner: wrote $OUT (rc=$rc)"
exit $rc
