#!/usr/bin/env bash
# tests/vault/vadv-49/run-vadv-49.sh — seat S49 adversarial battery, souji round 4.
#
# Attacks (assigned): (a) ledger row whose source_path is a symlink to the
# vault file; (b) uppercase hex sha256 in the ledger; (c) ledger TSV with a
# comment line starting '#'.
# Targets: the best impls by runner consensus (tests/results/vrun-*.json);
# default top 2 are primary, all discovered impls are also measured (cheap).
# Falls back to the installed tools/souji-verify.sh baseline when no r4 impl
# exists (flagged in the output).
#
# usage: run-vadv-49.sh [--impl PATH]... [--top N] [--wait SECS] [--grace SECS]
#                       [--out PATH]
# exit: 0 battery complete; 1 nothing runnable; 2 usage
set -uo pipefail
export LC_ALL=C
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LANE_ROOT="$(cd -- "$HERE/../../.." && pwd)"
RESULTS_DIR="$LANE_ROOT/tests/results"
OUT_JSON="$RESULTS_DIR/vadv-49.json"
FIX="$HERE/fixture"
REAL_VAULT="/home/vgpnk/Documents/shokoknowledge"
LIVE_LEDGER="$LANE_ROOT/corpus/knowledge/obsidian-ledger.tsv"
TOP=2; WAIT=1200; GRACE=300
IMPLS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --impl) IMPLS+=("$2"); shift 2 ;;
    --top) TOP=$2; shift 2 ;;
    --wait) WAIT=$2; shift 2 ;;
    --grace) GRACE=$2; shift 2 ;;
    --out) OUT_JSON=$2; shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) printf 'usage: %s [--impl PATH]... [--top N] [--wait SECS] [--grace SECS] [--out PATH]\n' "$0" >&2; exit 2 ;;
  esac
done

# ---- safety: PATH shims so no impl can spawn the Obsidian app -------------
SHIM="$HERE/shims"; mkdir -p "$SHIM"
for b in obsidian electron43; do
  cat > "$SHIM/$b" <<'EOF'
#!/bin/sh
printf 'vadv-49 shim: refusing to exec %s (Obsidian app-spawn guard)\n' "$0" >&2
exit 127
EOF
  chmod +x "$SHIM/$b"
done
PATH="$SHIM:$PATH"; export PATH

log() { printf '%s\n' "$*" >&2; }
impl_glob() { local p; for p in "$LANE_ROOT"/tools/souji-vault-verify.impl-*.sh; do [ -e "$p" ] && printf '%s\n' "$p"; done | sort -V; }
manifest() { find "$1" \( -type f -o -type l \) -printf '%y %p %s %T@ %l\n' 2>/dev/null | sort | sha256sum | cut -d' ' -f1; }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/vadv49.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# ---- phase 1: wait for impls ----------------------------------------------
FALLBACK=0
d1=$(( $(date +%s) + WAIT ))
while :; do
  [ "${#IMPLS[@]}" -gt 0 ] && break
  [ "$(impl_glob | wc -l)" -ge 1 ] && break
  [ "$(date +%s)" -ge "$d1" ] && break
  sleep 15
done
if [ "${#IMPLS[@]}" -eq 0 ]; then
  while IFS= read -r p; do [ -n "$p" ] && IMPLS+=("$p"); done < <(impl_glob)
fi
if [ "${#IMPLS[@]}" -eq 0 ]; then
  log "S49: no r4 impls after wait; falling back to installed tools/souji-verify.sh baseline"
  IMPLS=("$LANE_ROOT/tools/souji-verify.sh")
  FALLBACK=1
fi

# ---- phase 2: grace wait for runner consensus -----------------------------
consensus_count() { ls "$RESULTS_DIR"/vrun-*.json 2>/dev/null | wc -l; }
if [ "$(consensus_count)" -eq 0 ]; then
  d2=$(( $(date +%s) + GRACE ))
  while [ "$(date +%s)" -lt "$d2" ]; do
    [ "$(consensus_count)" -ge 1 ] && break
    sleep 15
  done
fi

python3 - "$RESULTS_DIR" > "$TMP/consensus.json" <<'PYEOF'
import glob, json, os, sys
res_dir = sys.argv[1]
agg = {}
def merge(impl, ok, case, fname):
    impl = os.path.basename(str(impl))
    if impl.endswith('.sh'): impl = impl[:-3]
    if not impl.startswith('souji-vault-verify'): return
    e = agg.setdefault(impl, {'pass': 0, 'total': 0, 'selftest': None, 'files': []})
    if fname not in e['files']: e['files'].append(fname)
    if case == '--selftest':
        if ok: e['selftest'] = True
    else:
        e['total'] += 1
        e['pass'] += 1 if ok else 0
def walk(x, fname):
    if isinstance(x, dict):
        # shape 1: flat rows {impl, case, pass}
        if 'impl' in x and ('pass' in x or 'ok' in x):
            ok = x.get('pass', x.get('ok'))
            if isinstance(ok, str): ok = ok.strip().lower() == 'true'
            merge(x['impl'], bool(ok), str(x.get('case', '')), fname)
        # shape 2: {impls: {name: {pass, fail, rate, cases:[...]}}}
        for k, v in x.items():
            if k == 'impls' and isinstance(v, dict):
                for name, e in v.items():
                    if isinstance(e, dict) and 'pass' in e:
                        g = agg.setdefault(os.path.basename(str(name)),
                                           {'pass': 0, 'total': 0, 'selftest': None, 'files': []})
                        if fname not in g['files']: g['files'].append(fname)
                        p = int(e.get('pass', 0)); t = p + int(e.get('fail', 0))
                        g['pass'] += p; g['total'] += t
                        if '--selftest' in (e.get('cases') or []): g['selftest'] = True
            else:
                walk(v, fname)
    elif isinstance(x, list):
        for v in x: walk(v, fname)
files = sorted(glob.glob(os.path.join(res_dir, 'vrun-*.json')))
for f in files:
    try: doc = json.load(open(f))
    except Exception: continue
    walk(doc, os.path.basename(f))
def key(it):
    n, e = it
    st = 1 if e['selftest'] else 0
    ratio = (e['pass'] / e['total']) if e['total'] else 0.0
    return (-st, -ratio, -e['pass'], n)
ranked = [{'impl': n, **e} for n, e in sorted(agg.items(), key=key)]
print(json.dumps({'files': files, 'ranking': ranked}))
PYEOF

cat > "$TMP/topnames.py" <<'PYEOF'
import json, sys
top = int(sys.argv[1])
d = json.load(open(sys.argv[2]))
for e in d.get('ranking', [])[:top]:
    print(e['impl'])
PYEOF
mapfile -t TOPNAMES < <(python3 "$TMP/topnames.py" "$TOP" "$TMP/consensus.json")
SELECTED=()
if [ "${#TOPNAMES[@]}" -gt 0 ]; then
  for n in "${TOPNAMES[@]}"; do
    [ -f "$LANE_ROOT/tools/$n.sh" ] && SELECTED+=("$LANE_ROOT/tools/$n.sh")
  done
fi
if [ "${#SELECTED[@]}" -eq 0 ]; then
  SELECTED=("${IMPLS[@]}")
  [ "$FALLBACK" -eq 0 ] && log "S49: no consensus ranking; measuring all ${#IMPLS[@]} impls"
fi
# also measure any impl not selected (cheap completeness)
for p in "${IMPLS[@]}"; do
  found=0
  for s in "${SELECTED[@]}"; do [ "$s" = "$p" ] && found=1; done
  [ "$found" -eq 0 ] && SELECTED+=("$p")
done

# ---- fixtures + snapshots --------------------------------------------------
bash "$HERE/make-fixtures.sh" --out "$FIX" >/dev/null
LIVE_LEDGER_SHA_BEFORE=$(sha256sum -- "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || printf 'absent')
VAULT_MAN_BEFORE=$(manifest "$REAL_VAULT")
VAULT_COUNT_BEFORE=$(find "$REAL_VAULT" -type f 2>/dev/null | wc -l)
FIX_MAN_BEFORE=$(manifest "$FIX")
LEDGERS_SHA_BEFORE=$(sha256sum "$HERE"/ledger-*.tsv | sha256sum | cut -d' ' -f1)

# ---- case table ------------------------------------------------------------
# oracle: expected verdict. "ANY" = not binding (either verdict tolerated),
# used where the spec is genuinely silent; binding cases drive survived.
cat > "$TMP/cases.tsv" <<EOF
control	control	$HERE/ledger-control.tsv	$FIX/control/source/alpha.txt	VERIFIED
A1	a-symlink-source	$HERE/ledger-a1.tsv	$FIX/a1/source/link.txt	NOT-VERIFIED
A2	a-symlink-source	$HERE/ledger-a2.tsv	$FIX/a2/source/link.txt	ANY
A3	a-symlink-source	$HERE/ledger-a3.tsv	$FIX/a1/source/link.txt	NOT-VERIFIED
A4	a-symlink-source	$HERE/ledger-a4.tsv	$FIX/a4/source/alpha.txt	NOT-VERIFIED
A5	a-symlink-source	$HERE/ledger-a5.tsv	$FIX/a5/source/self.txt	NOT-VERIFIED
A6	a-symlink-source	$HERE/ledger-a3.tsv	$FIX/a1/vault/alpha.txt	NOT-VERIFIED
B1	b-uppercase-sha	$HERE/ledger-b1.tsv	$FIX/b/source/alpha.txt	ANY
B2	b-uppercase-sha	$HERE/ledger-b2.tsv	$FIX/b/source/alpha.txt	NOT-VERIFIED
B3	b-uppercase-sha	$HERE/ledger-b3.tsv	$FIX/b/source/alpha.txt	ANY
B4	b-uppercase-sha	$HERE/ledger-b4.tsv	$FIX/b/source/alpha.txt	NOT-VERIFIED
C1	c-comment-line	$HERE/ledger-c1.tsv	$FIX/c/source/alpha.txt	VERIFIED
C2	c-comment-line	$HERE/ledger-c2.tsv	$FIX/c/source/alpha.txt	NOT-VERIFIED
C3	c-comment-line	$HERE/ledger-c3.tsv	$FIX/c/source/alpha.txt	VERIFIED
C4	c-comment-line	$HERE/ledger-c4.tsv	$FIX/c/source/alpha.txt	VERIFIED
C5	c-comment-line	$HERE/ledger-c5.tsv	$FIX/c/source/#weird.txt	VERIFIED
EOF

# ---- run battery -----------------------------------------------------------
: > "$TMP/results.tsv"; : > "$TMP/selftests.tsv"
for impl in "${SELECTED[@]}"; do
  name="$(basename "$impl")"; name="${name%.sh}"
  # wait for a mid-write impl to settle
  for _ in 1 2 3; do
    age=$(( $(date +%s) - $(stat -c %Y "$impl" 2>/dev/null || echo 0) ))
    [ "$age" -ge 45 ] && break
    sleep 15
  done
  sha=$(sha256sum -- "$impl" | cut -d' ' -f1)
  st_raw=$(timeout 300 env SOUJI_LEDGER="$HERE/ledger-control.tsv" bash "$impl" --selftest 2>&1); st_rc=$?
  printf '%s\t%s\t%s\n' "$name" "$st_rc" "$(printf '%s' "$st_raw" | tail -c 220 | tr '\n\t' '  ')" >> "$TMP/selftests.tsv"
  while IFS=$'\t' read -r cid attack ledger target oracle; do
    [ -n "$cid" ] || continue
    raw=$(timeout 60 env SOUJI_LEDGER="$ledger" bash "$impl" --ledger "$ledger" --fallback "$target" 2>&1); rc=$?
    if [ "$rc" -eq 2 ]; then raw=$(timeout 60 env SOUJI_LEDGER="$ledger" bash "$impl" --ledger "$ledger" "$target" 2>&1); rc=$?; fi
    if [ "$rc" -eq 2 ]; then raw=$(timeout 60 env SOUJI_LEDGER="$ledger" bash "$impl" "$target" 2>&1); rc=$?; fi
    verdict=$(printf '%s\n' "$raw" | grep -aoE '^(VERIFIED|NOT-VERIFIED)' | head -1)
    if [ -z "$verdict" ]; then
      vline=$(printf '%s\n' "$raw" | grep -aE '^VERDICT' | head -1)
      case "$vline" in *$'\tSAFE\t'*) verdict=VERIFIED ;; *$'\tNOT-SAFE\t'*) verdict=NOT-VERIFIED ;; esac
    fi
    if [ -z "$verdict" ] && [ "$rc" -ne 0 ]; then
      raw=$(timeout 60 env SOUJI_LEDGER="$ledger" bash "$impl" "$target" 2>&1); rc=$?
      verdict=$(printf '%s\n' "$raw" | grep -aoE '^(VERIFIED|NOT-VERIFIED)' | head -1)
    fi
    [ -z "$verdict" ] && verdict=NO-VERDICT
    snippet=$(printf '%s' "$raw" | head -c 220 | tr '\n\t' '  ')
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$impl" "$name" "$sha" "$cid" "$attack" "$ledger" "$target" "$oracle" "$rc" "$verdict" "$snippet" >> "$TMP/results.tsv"
  done < "$TMP/cases.tsv"
done

# ---- post snapshots --------------------------------------------------------
LIVE_LEDGER_SHA_AFTER=$(sha256sum -- "$LIVE_LEDGER" 2>/dev/null | cut -d' ' -f1 || printf 'absent')
VAULT_MAN_AFTER=$(manifest "$REAL_VAULT")
VAULT_COUNT_AFTER=$(find "$REAL_VAULT" -type f 2>/dev/null | wc -l)
FIX_MAN_AFTER=$(manifest "$FIX")
LEDGERS_SHA_AFTER=$(sha256sum "$HERE"/ledger-*.tsv | sha256sum | cut -d' ' -f1)

# ---- final JSON ------------------------------------------------------------
python3 - "$TMP" "$OUT_JSON" "$HERE" "$FIX" "$LANE_ROOT" "$FALLBACK" \
  "$LIVE_LEDGER_SHA_BEFORE" "$LIVE_LEDGER_SHA_AFTER" \
  "$VAULT_MAN_BEFORE" "$VAULT_MAN_AFTER" "$VAULT_COUNT_BEFORE" "$VAULT_COUNT_AFTER" \
  "$FIX_MAN_BEFORE" "$FIX_MAN_AFTER" "$LEDGERS_SHA_BEFORE" "$LEDGERS_SHA_AFTER" \
  "${TOPNAMES[@]+"${TOPNAMES[@]}"}" <<'PYEOF'
import json, os, sys, datetime
tmp, out_json, here, fix, lane_root, fallback = sys.argv[1:7]
(ll_b, ll_a, vm_b, vm_a, vc_b, vc_a, fm_b, fm_a, lg_b, lg_a) = sys.argv[7:17]
topnames = sys.argv[17:]

def rows(path, min_cols):
    out = []
    if not os.path.isfile(path): return out
    for line in open(path, encoding='utf-8', errors='replace'):
        p = line.rstrip('\n').split('\t')
        if len(p) >= min_cols: out.append(p)
    return out

results = rows(os.path.join(tmp, 'results.tsv'), 11)
selftests = {}
for p in rows(os.path.join(tmp, 'selftests.tsv'), 3):
    selftests[p[0]] = {'rc': p[1], 'tail': p[2]}
consensus = json.load(open(os.path.join(tmp, 'consensus.json')))

ORACLE = {'control': 'VERIFIED', 'A1': 'NOT-VERIFIED', 'A2': 'ANY',
          'A3': 'NOT-VERIFIED', 'A4': 'NOT-VERIFIED', 'A5': 'NOT-VERIFIED',
          'A6': 'NOT-VERIFIED',
          'B1': 'ANY', 'B2': 'NOT-VERIFIED', 'B3': 'ANY', 'B4': 'NOT-VERIFIED',
          'C1': 'VERIFIED', 'C2': 'NOT-VERIFIED', 'C3': 'VERIFIED',
          'C4': 'VERIFIED', 'C5': 'VERIFIED'}
CASE_ATTACK = {'control': 'control', 'A1': 'a-symlink-source', 'A2': 'a-symlink-source',
               'A3': 'a-symlink-source', 'A4': 'a-symlink-source', 'A5': 'a-symlink-source',
               'A6': 'a-symlink-source',
               'B1': 'b-uppercase-sha', 'B2': 'b-uppercase-sha', 'B3': 'b-uppercase-sha',
               'B4': 'b-uppercase-sha', 'C1': 'c-comment-line', 'C2': 'c-comment-line',
               'C3': 'c-comment-line', 'C4': 'c-comment-line', 'C5': 'c-comment-line'}

impls = {}
order = []
for p in results:
    impl_path, name, sha, cid, attack, ledger, target, oracle, rc, verdict, snip = p
    if name not in impls:
        impls[name] = {'impl': impl_path, 'sha256': sha, 'cases': []}
        order.append(name)
    impls[name]['cases'].append({'case': cid, 'attack': attack, 'ledger': ledger,
                                 'target': target, 'oracle': oracle, 'rc': int(rc),
                                 'observed': verdict, 'match': (oracle == 'ANY' or verdict == oracle),
                                 'command': 'env SOUJI_LEDGER=%s bash %s --ledger %s --fallback %s' % (ledger, impl_path, ledger, target),
                                 'snippet': snip})

out_impls = []
for name in order:
    e = impls[name]
    st = selftests.get(name, {})
    cases = e['cases']
    control_ok = any(c['case'] == 'control' and c['observed'] == 'VERIFIED' for c in cases)
    attacks = []
    for atk in ('a-symlink-source', 'b-uppercase-sha', 'c-comment-line'):
        acases = [c for c in cases if c['attack'] == atk]
        binding = [c for c in acases if c['oracle'] != 'ANY']
        survived = bool(binding) and all(c['match'] for c in binding) and control_ok
        attacks.append({'attack': atk, 'survived': survived,
                        'binding_cases': [{'case': c['case'], 'oracle': c['oracle'],
                                           'observed': c['observed'], 'match': c['match']} for c in acases]})
    out_impls.append({'impl': e['impl'], 'name': name, 'sha256': e['sha256'],
                      'selftest_rc': st.get('rc'), 'selftest_tail': st.get('tail', ''),
                      'control_ok': control_ok, 'attacks': attacks,
                      'survived_all': all(a['survived'] for a in attacks),
                      'cases': cases})

rows_flat = []
for e in out_impls:
    for a in e['attacks']:
        rows_flat.append({'impl': e['name'], 'attack': a['attack'], 'survived': a['survived'],
                          'control_ok': e['control_ok'], 'selftest_rc': e['selftest_rc']})

safety = {
    'live_ledger_path': os.path.join(lane_root, 'corpus/knowledge/obsidian-ledger.tsv'),
    'live_ledger_sha256_before': ll_b, 'live_ledger_sha256_after': ll_a,
    'live_ledger_unchanged': ll_b == ll_a,
    'real_vault_path': '/home/vgpnk/Documents/shokoknowledge',
    'real_vault_manifest_before': vm_b, 'real_vault_manifest_after': vm_a,
    'real_vault_untouched': vm_b == vm_a and vc_b == vc_a,
    'real_vault_file_count_before': vc_b, 'real_vault_file_count_after': vc_a,
    'fixture_root': fix,
    'fixture_manifest_before': fm_b, 'fixture_manifest_after': fm_a,
    'fixture_untouched': fm_b == fm_a,
    'test_ledgers_sha256_before': lg_b, 'test_ledgers_sha256_after': lg_a,
    'test_ledgers_unchanged': lg_b == lg_a,
    'obsidian_shim': 'PATH shim refuses obsidian/electron43 execution (app-spawn guard)',
    'real_vault_manifest_method': 'find -type f -o -type l -printf, sorted, sha256',
}

doc = {
    'seat': 'S49', 'role': 'adversarial tester: symlink source / uppercase sha / comment line',
    'round': 4, 'lane_repo': lane_root,
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'assigned_attacks': ['a-symlink-source', 'b-uppercase-sha', 'c-comment-line'],
    'fixture_contract': {
        'builder': os.path.join(here, 'make-fixtures.sh'),
        'harness': os.path.join(here, 'run-vadv-49.sh'),
        'ledgers': sorted(f for f in os.listdir(here) if f.startswith('ledger-') and f.endswith('.tsv')),
        'invocation': 'env SOUJI_LEDGER=<ledger> bash <impl> --ledger <ledger> --fallback <target>',
        'oracle_rule': 'binding case passes iff observed == oracle; survived per attack iff control VERIFIED and all binding cases pass',
    },
    'consensus': {'vrun_files': consensus.get('files', []), 'ranking': consensus.get('ranking', []),
                  'top_by_consensus': topnames, 'fallback_to_installed_baseline': fallback == '1'},
    'safety': safety,
    'rows': rows_flat,
    'impls': out_impls,
}
with open(out_json, 'w') as f:
    json.dump(doc, f, indent=1)
print(json.dumps({'out': out_json, 'impls': len(out_impls),
                  'survived_all': {e['name']: e['survived_all'] for e in out_impls}}, indent=1))
PYEOF
