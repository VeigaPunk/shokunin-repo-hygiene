#!/usr/bin/env bash
# tests/vault/judge-60-vault.sh — round-4 SEAT S60 "final judge": independent
# battery for the Obsidian-CLI vault-verification candidates
# (tools/souji-vault-verify.impl-*.sh and installed-name variants).
#
# Usage: judge-60-vault.sh [--wait SECS] [--out PATH] [--impls GLOB] [--only PATH]
#   --wait  wait for candidates to land (>=4 impls, count stable) before running
#   --out   JSON report (default <lane>/tests/results/vfinal-60.json)
#   --impls extra glob for candidates (default: the standard set)
#   --only  run a single candidate (path or basename)
# Exit: 0 battery ran; 1 no candidate found; 2 usage.
#
# Independence: builds its own fixture world under mktemp -d (single-row
# ledgers everywhere, so every verdict is attributable) and additionally
# drives the round's own tests/vault/case-V* builders as contract fixtures.
# Expected verdicts come from the ledger + filesystem, never from a candidate.
#
# Safety: read-only over the real vault (/home/vgpnk/Documents/shokoknowledge)
# and over the live ledger (corpus/knowledge/obsidian-ledger.tsv, which must
# stay header-only); the GUI launcher is never executed (exe-link rail only);
# candidate runs are bounded by `timeout`; writes stay inside the mktemp
# world, /tmp scratch, and the --out path.
#
# Internal plumbing note: all TSVs written here use "-" placeholders for
# empty fields because `IFS=$'\t' read` collapses empty fields.
set -uo pipefail
export LC_ALL=C

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
LANE="$REPO_ROOT"
OUT="$REPO_ROOT/tests/results/vfinal-60.json"
WAIT=0
EXTRA_GLOB=""
ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --wait) WAIT="${2:-0}"; shift 2 ;;
    --out) OUT="${2:?}"; shift 2 ;;
    --impls) EXTRA_GLOB="${2:?}"; shift 2 ;;
    --only) ONLY="${2:?}"; shift 2 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) echo "judge-60-vault: unknown arg $1" >&2; exit 2 ;;
  esac
done

REALVAULT="${SOUJI_REAL_VAULT:-/home/vgpnk/Documents/shokoknowledge}"
LIVE_LEDGER="$LANE/corpus/knowledge/obsidian-ledger.tsv"
W="$(mktemp -d /tmp/judge60-vault.XXXXXX)"
case "$W" in /tmp/judge60-vault.*) : ;; *) echo "refusing W=$W" >&2; exit 9 ;; esac
mkdir -p "$W/out" "$W/world" "$W/tmp"
KEEP="${J60_KEEP:-0}"
cleanup() { [ "$KEEP" = 1 ] || rm -rf -- "$W"; }
trap cleanup EXIT

log() { printf '%s\n' "$*" >&2; }
san() { printf '%s' "$1" | tr '\n' ' ' | tr -d '\t'; }
pl() { [ -n "${1:-}" ] && san "$1" || printf -- '-'; }

cand_globs() {
  printf '%s\n' \
    "$LANE"/tools/souji-vault-verify.impl-*.sh \
    "$LANE"/tools/souji-vault-verify.sh \
    "$LANE"/tools/obsidian-vault-verify*.sh \
    "$LANE"/tools/vault-verify*.sh \
    "$LANE"/tools/impl-2*.sh
  [ -n "$EXTRA_GLOB" ] && printf '%s\n' "$EXTRA_GLOB"
}
cand_paths() {
  local p
  for p in $(cand_globs); do
    [ -f "$p" ] || continue
    p="$(readlink -m -- "$p")"
    case "$p" in "$LANE"/tools/*) : ;; *) continue ;; esac
    printf '%s\n' "$p"
  done | sort -u
}

# ---------------------------------------------------------------- wait for impls
if [ "$WAIT" -gt 0 ] && [ -z "$ONLY" ]; then
  deadline=$(( $(date +%s) + WAIT ))
  last=-1; stable=0
  while :; do
    n=$(cand_paths | wc -l)
    if [ "$n" -ge 4 ]; then
      if [ "$n" = "$last" ]; then stable=$((stable+1)); else stable=0; last=$n; fi
      [ "$stable" -ge 3 ] && break
    else
      stable=0; last=$n
    fi
    [ "$(date +%s)" -ge "$deadline" ] && break
    sleep 10
  done
  log "judge-60: candidate count after wait: $(cand_paths | wc -l)"
fi

if [ -n "$ONLY" ]; then
  if [ -f "$ONLY" ]; then CANDS="$(readlink -m -- "$ONLY")"
  else CANDS="$(cand_paths | grep -E "/${ONLY}(\.sh)?$" | head -1)"; fi
else
  CANDS="$(cand_paths)"
fi
[ -n "$CANDS" ] || { echo "judge-60-vault: no candidates found" >&2; exit 1; }

# ------------------------------------------------------------- rails: before
UFO_STATE="$LANE/../.ufo/state"
WATCHDOG="$LANE/../.ufo/watchdog.log"
gui_count() {
  local p c e n=0
  for p in /proc/[0-9]*; do
    [ -r "$p/cmdline" ] || continue
    c=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null) || continue
    case "$c" in *obsidian*) ;; *) continue ;; esac
    case "$c" in *judge-60*|*pgrep*|*grep*) continue ;; esac
    e=$(readlink "$p/exe" 2>/dev/null) || continue
    case "$e" in *electron*|*obsidian*) n=$((n+1)) ;; esac
  done
  printf '%s' "$n"
}
GUI_BEFORE="$(gui_count)"; GUI_BEFORE=${GUI_BEFORE:-0}
LIVE_SHA_B="$(sha256sum "$LIVE_LEDGER" 2>/dev/null | awk '{print $1}')"
LIVE_LN_B="$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ')"
(cd "$REALVAULT" && find . -type f -not -path './.git/*' -print0 2>/dev/null | sort -z | xargs -0 -r sha256sum 2>/dev/null | sha256sum) > "$W/vault.before" 2>/dev/null
VFILE_B="$(find "$REALVAULT" -type f 2>/dev/null | wc -l | tr -d ' ')"
HEAD_B="$(git -C "$LANE" rev-parse HEAD 2>/dev/null || echo '')"
UFO_B=""
[ -d "$UFO_STATE" ] && UFO_B="$(find "$UFO_STATE" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1)"
WD_B="$(stat -c '%Y:%s' "$WATCHDOG" 2>/dev/null || echo absent)"

# ------------------------------------------------------------ fixture world
s()   { sha256sum -- "$1" 2>/dev/null | awk '{print $1}'; }
row() { printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "${5:-2026-10-18}" "${6:-}"; }
dir_digest() { ( cd "$1" && find . -type f -print0 | sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1 ) 2>/dev/null; }

build_world() {
  local w="$W/world"
  mkdir -p "$w/src/notes" "$w/src/dir-case" "$w/vault/atlas" "$w/vault/dir-case" "$w/ledgers"
  local HDR=$'source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote'
  local led="$w/ledgers"

  printf '# Note ok\n\nbody ok\n'        > "$w/src/notes/ok.md"
  printf '# Note vtamper\n\nbody v\n'    > "$w/src/notes/vtamper.md"
  printf '# Note stamper\n\nbody s\n'    > "$w/src/notes/stamper.md"
  printf '# Note vmiss\n\nbody m\n'      > "$w/src/notes/vmiss.md"
  printf '# Note spaces\n\nbody sp\n'    > "$w/src/notes/spaces.md"
  printf ''                              > "$w/src/notes/empty.md"
  printf 'PEM-ish placeholder\n'         > "$w/src/notes/creds.pem"
  printf '# Note dup\n\nbody d\n'        > "$w/src/notes/dup.md"
  printf '# Note second\n\nbody 2\n'     > "$w/src/notes/second.md"
  printf '# Note traversal\n\nbody t\n'  > "$w/src/notes/traversal.md"
  printf '# Note symlink\n\nbody sl\n'   > "$w/src/notes/symlink.md"
  printf '# Note dangling\n\nbody dl\n'  > "$w/src/notes/dangling.md"
  printf '# Note fifo\n\nbody f\n'       > "$w/src/notes/fifo.md"
  printf '# Note selfmove\n\nbody sm\n'  > "$w/src/notes/selfmove.md"
  printf '# Note alias\n\nbody al\n'     > "$w/src/notes/alias.md"
  printf '# Note symalias\n\nbody sa\n'  > "$w/src/notes/symalias.md"
  printf 'one\n'                         > "$w/src/dir-case/one.txt"
  printf 'two\n'                         > "$w/src/dir-case/two.txt"

  cp "$w/src/notes/ok.md"      "$w/vault/atlas/ok.md"
  cp "$w/src/notes/vtamper.md" "$w/vault/atlas/vtamper.md"
  cp "$w/src/notes/spaces.md"  "$w/vault/atlas/space name.md"
  cp "$w/src/notes/empty.md"   "$w/vault/atlas/empty.md"
  cp "$w/src/notes/dup.md"     "$w/vault/atlas/dup.md"
  cp "$w/src/notes/second.md"  "$w/vault/atlas/second.md"
  cp "$w/src/notes/symlink.md" "$w/vault/atlas/symlink-target.md"
  ln -s "$w/src/notes/symalias.md" "$w/vault/atlas/symalias.md"
  cp "$w/src/dir-case/one.txt" "$w/vault/dir-case/one.txt"
  cp "$w/src/dir-case/two.txt" "$w/vault/dir-case/two.txt"
  mkfifo "$w/vault/atlas/fifo.md" 2>/dev/null || true
  ln -s "$w/vault/atlas/symlink-target.md" "$w/vault/atlas/symlink.md"
  ln -s "$w/does-not-exist" "$w/vault/atlas/dangling.md"

  local OK_S=$(s "$w/src/notes/ok.md")        OK_V=$(s "$w/vault/atlas/ok.md")
  local VT_EXPORT=$(printf '# Note vtamper\n\nbody v\n' | sha256sum | cut -d' ' -f1)
  local ST_S=$(s "$w/src/notes/stamper.md")
  local VM_S=$(s "$w/src/notes/vmiss.md")
  local SP_S=$(s "$w/src/notes/spaces.md")    SP_V=$(s "$w/vault/atlas/space name.md")
  local EM_S=$(s "$w/src/notes/empty.md")     EM_V=$(s "$w/vault/atlas/empty.md")
  local DP_S=$(s "$w/src/notes/dup.md")       DP_V=$(s "$w/vault/atlas/dup.md")
  local SC_S=$(s "$w/src/notes/second.md")    SC_V=$(s "$w/vault/atlas/second.md")
  local SL_S=$(s "$w/src/notes/symlink.md")   SL_V=$(s "$w/vault/atlas/symlink-target.md")
  local DL_S=$(s "$w/src/notes/dangling.md")
  local FI_S=$(s "$w/src/notes/fifo.md")
  local TR_S=$(s "$w/src/notes/traversal.md")
  local DC_S=$(dir_digest "$w/src/dir-case")  DC_V=$(dir_digest "$w/vault/dir-case")
  local WRONG=1111111111111111111111111111111111111111111111111111111111111111

  { printf '%s\n' "$HDR"; row "$w/src/notes/ok.md" "$OK_S" "$w/vault/atlas/ok.md" "$OK_V" "" b1-match; } > "$led/B1.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/vtamper.md" "$VT_EXPORT" "$w/vault/atlas/vtamper.md" "$VT_EXPORT" "" b2-vtamper; } > "$led/B2.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/stamper.md" "$ST_S" "$w/vault/atlas/second.md" "$SC_V" "" b3-stamper; } > "$led/B3.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/vmiss.md" "$VM_S" "$w/vault/atlas/vmiss.md" "$VM_S" "" b4-vmiss; } > "$led/B4.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/ok.md" "" "$w/vault/atlas/ok.md" "$OK_V" "" b5-src-empty; } > "$led/B5.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/ok.md" "$OK_S" "$w/vault/atlas/ok.md" "" "" b6-vault-empty; } > "$led/B6.tsv"
  printf '%s\n' "$HDR" > "$led/B7.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/ok.md" "$OK_S" "$w/vault/atlas/ok.md" "$OK_V" "" b8; } > "$led/B8.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/creds.pem" "$(s "$w/src/notes/creds.pem")" "$w/vault/atlas/ok.md" "$OK_V" "" b9-secret; } > "$led/B9.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/fifo.md" "$FI_S" "$w/vault/atlas/fifo.md" "$FI_S" "" b10-fifo; } > "$led/B10.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/dangling.md" "$DL_S" "$w/vault/atlas/dangling.md" "$DL_S" "" b11-dangling; } > "$led/B11.tsv"
  { printf '%s\n' "$HDR"; printf '%s\t%s\t%s\t%s\t%s\t%s' "$w/src/notes/ok.md" "$OK_S" "$w/vault/atlas/ok.md" "$OK_V" "2026-10-18" b12-noeol; } > "$led/B12.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/empty.md" "$EM_S" "$w/vault/atlas/empty.md" "$EM_V" "" b13-empty; } > "$led/B13.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/dir-case" "$DC_S" "$w/vault/dir-case" "$DC_V" "" b14-dir; } > "$led/B14.tsv"
  # empty hash columns on a DIRECTORY row: must not verify (impl-21's selftest
  # false-SAFE class; the IFS-collapsed row reads vault_path=exported_at).
  { printf '%s\n' "$HDR"; row "$w/src/dir-case" "" "$w/vault/dir-case" "" "" b25-dir-empty-hash; } > "$led/B25.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/spaces.md" "$SP_S" "$w/vault/atlas/space name.md" "$SP_V" "" b15-spaces; } > "$led/B15.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/dup.md" "$DP_S" "$w/vault/atlas/dup.md" "$DP_V" "" dup-first
    row "$w/src/notes/dup.md" "$WRONG" "$w/vault/atlas/dup.md" "$WRONG" "" dup-second; } > "$led/B18.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/second.md" "$WRONG" "$w/vault/atlas/second.md" "$SC_V" "" bad-first
    row "$w/src/notes/second.md" "$SC_S" "$w/vault/atlas/second.md" "$SC_V" "" good-second; } > "$led/B19.tsv"
  local ETC_SHA=$(sha256sum /etc/hostname 2>/dev/null | awk '{print $1}')
  { printf '%s\n' "$HDR"; row "$w/src/notes/traversal.md" "$TR_S" "$w/../../../etc/hostname" "$ETC_SHA" "" traversal; } > "$led/B20.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/symlink.md" "$SL_S" "$w/vault/atlas/symlink.md" "$SL_V" "" b21-symlink; } > "$led/B21.tsv"
  # self-reference family (round-4 adversarial discriminator, S54 P1/P2/P3):
  # a "receipt" whose vault path is the source itself (spelled identically,
  # via a symlink, or via a ../ alias) is not an export and must not verify.
  local SM_S=$(s "$w/src/notes/selfmove.md")
  local AL_S=$(s "$w/src/notes/alias.md")
  local SA_S=$(s "$w/src/notes/symalias.md")
  { printf '%s\n' "$HDR"; row "$w/src/notes/selfmove.md" "$SM_S" "$w/src/notes/selfmove.md" "$SM_S" "" self-move; } > "$led/B22.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/alias.md" "$AL_S" "$w/src/../src/notes/alias.md" "$AL_S" "" path-alias; } > "$led/B23.tsv"
  { printf '%s\n' "$HDR"; row "$w/src/notes/symalias.md" "$SA_S" "$w/vault/atlas/symalias.md" "$SA_S" "" symlink-alias; } > "$led/B24.tsv"

  printf 'DIFFERENT\n' >> "$w/vault/atlas/vtamper.md"
  printf '# Note stamper MUTATED\n' > "$w/src/notes/stamper.md"

  local RH="Home.md"
  [ -f "$REALVAULT/Home.md" ] || RH="$(cd "$REALVAULT" && find . -type f -name '*.md' 2>/dev/null | head -1 | sed 's#^\./##')"
  if [ -n "$RH" ] && [ -f "$REALVAULT/$RH" ]; then
    cp "$REALVAULT/$RH" "$w/src/notes/real-home.md"
    local RH_SHA=$(s "$REALVAULT/$RH")  RH_COPY_SHA=$(s "$w/src/notes/real-home.md")
    { printf '%s\n' "$HDR"; row "$w/src/notes/real-home.md" "$RH_COPY_SHA" "$REALVAULT/$RH" "$RH_SHA" "" b16-real; } > "$led/B16.tsv"
    { printf '%s\n' "$HDR"; row "$w/src/notes/real-home.md" "$RH_COPY_SHA" "$REALVAULT/$RH" "$WRONG" "" b17-real-wrong; } > "$led/B17.tsv"
  else
    printf '%s\n' "$HDR" > "$led/B16.tsv"; printf '%s\n' "$HDR" > "$led/B17.tsv"
  fi
}
build_world
log "judge-60: world built at $W/world"

# ---------------------------------------------------- contract fixture cases
: > "$W/cases.tsv"
: > "$W/prep-notes.txt"
emit_case() { # id kind hard ledger target wcls wreason contains ev_contains note
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(pl "$1")" "$(pl "$2")" "$(pl "$3")" "$(pl "$4")" "$(pl "$5")" "$(pl "$6")" \
    "$(pl "${7:-}")" "$(pl "${8:-}")" "$(pl "${9:-}")" "$(pl "${10:-}")" >> "$W/cases.tsv"
}

python3 - "$LANE" "$W" <<'PYEOF'
import json, os, re, subprocess, sys, glob
lane, W = sys.argv[1], sys.argv[2]
vault = os.path.join(lane, "tests", "vault")
out = open(os.path.join(W, "cases.tsv"), "a")
notes = open(os.path.join(W, "prep-notes.txt"), "a")

def pl(x):
    s = str(x).replace("\t", " ").replace("\n", " ").strip() if x is not None else ""
    return s if s else "-"

def emit(cid, kind, hard, ledger, target, wcls, reason, contains, ev, note):
    out.write("\t".join([pl(cid), pl(kind), pl(hard), pl(ledger), pl(target), pl(wcls),
                         pl(reason), pl(contains), pl(ev), pl(note)]) + "\n")

def map_class(v):
    v = (v or "").strip().upper()
    if v in ("VERIFIED", "SAFE"): return "VERIFIED"
    if v.startswith("NOT"): return "NOT-VERIFIED"
    return v

def vnum(p):
    m = re.search(r"case-V(\d+)", p)
    return (int(m.group(1)) if m else 99, p)

for case_dir in sorted(glob.glob(os.path.join(vault, "case-V*")), key=vnum):
    case = os.path.basename(case_dir)
    maker = os.path.join(case_dir, "make-fixture.sh")
    exp_src = os.path.join(case_dir, "expected.json")
    root = None
    if os.path.isfile(maker):
        r = subprocess.run(["bash", maker, "--quiet"], cwd=case_dir, capture_output=True, text=True, timeout=300)
        if r.returncode == 2:
            r = subprocess.run(["bash", maker], cwd=case_dir, capture_output=True, text=True, timeout=300)
        m = re.search(r"FIXTURE_READY\s+\S+\s+(\S+)", r.stdout or "")
        root = m.group(1) if m else None
        if r.returncode != 0 or not root:
            notes.write(f"{case}: builder rc={r.returncode} root={root} stderr={(r.stderr or '').strip()[-200:]}\n")
            root = None
    exp_path = os.path.join(root, "expected.json") if root else None
    if not exp_path or not os.path.isfile(exp_path):
        exp_path = exp_src
    if not os.path.isfile(exp_path):
        notes.write(f"{case}: no expected.json — skipped\n"); continue
    try:
        doc = json.load(open(exp_path))
    except Exception as e:
        notes.write(f"{case}: expected.json unparsable: {e}\n"); continue
    base = root or case_dir

    ledger = os.path.join(root, "ledger.tsv") if root else None
    if not ledger or not os.path.isfile(ledger):
        cand = doc.get("ledger") or doc.get("ledger_path") or ""
        cand = str(cand).replace("@FIXTURE_ROOT@", base)
        if cand and not os.path.isabs(cand): cand = os.path.join(base, cand)
        ledger = cand if os.path.isfile(cand) else None

    if isinstance(doc.get("probes"), list):
        for pr in doc["probes"]:
            pid = str(pr.get("id") or case)
            pled = pr.get("ledger")
            plath = os.path.join(base, pled) if pled and not os.path.isabs(pled) else pled
            tgt = str(pr.get("target") or "")
            t = tgt.replace("@FIXTURE_ROOT@", base)
            if not os.path.isabs(t): t = os.path.join(base, t)
            exp = pr.get("expect") if isinstance(pr.get("expect"), dict) else {}
            want = exp.get("verdict") or pr.get("verdict") or ""
            emit(pid, "fixture", "1", plath, t, map_class(want), exp.get("reason"),
                 None, exp.get("evidence_substr") or pr.get("evidence_substr"), case)
        continue

    targets = doc.get("targets") or []
    expect = doc.get("expect")
    if isinstance(expect, dict): expect = [expect]
    if not isinstance(expect, list): expect = []
    exp_by_path = {e.get("path"): e for e in expect if isinstance(e, dict) and e.get("path")}
    pairs = []
    for i, t in enumerate(targets):
        if isinstance(t, dict):
            p = t.get("path")
            e = t.get("expected") if isinstance(t.get("expected"), dict) else {}
            if not e:
                e = exp_by_path.get(p) or (expect[i] if i < len(expect) and isinstance(expect[i], dict) else {}) or (expect[0] if len(expect) == 1 else {})
        else:
            p = t
            e = exp_by_path.get(p) or (expect[i] if i < len(expect) and isinstance(expect[i], dict) else {}) or (expect[0] if len(expect) == 1 else {})
        if p: pairs.append((str(p), e or {}))
    if not pairs:
        pairs = [(e.get("path"), e) for e in expect if isinstance(e, dict) and e.get("path")]
    primary_cls = None
    if isinstance(doc.get("accept"), dict):
        st = doc["accept"].get("structured")
        if isinstance(st, dict):
            primary_cls = map_class(st.get("verdict"))
    for p, e in pairs:
        t = p.replace("@FIXTURE_ROOT@", base)
        if not os.path.isabs(t): t = os.path.join(base, t)
        want = e.get("verdict") or e.get("expected") or ""
        if isinstance(want, dict): want = want.get("verdict")
        wcls = map_class(want)
        cont = None
        if primary_cls and wcls == primary_cls:
            toks = []
            if isinstance(doc.get("accept"), dict) and isinstance(doc["accept"].get("contains"), list):
                toks = [str(x) for x in doc["accept"]["contains"]]
            toks = [x for x in toks if x.upper() not in ("VERIFIED", "NOT-VERIFIED", "SAFE", "NOT-SAFE")]
            cont = ",".join(toks) if toks else None
        emit(case, "fixture", "1", ledger, t, wcls, e.get("reason"),
             cont, None, (e.get("why") or "")[:90])
out.close(); notes.close()
PYEOF

# --- world cases (single-row ledgers; reasons are this battery's own words) --
W2="$W/world"
emit_case B1  world 1 "$W2/ledgers/B1.tsv"  "$W2/src/notes/ok.md"        VERIFIED     ""                "" "" "clean match control"
emit_case B2  world 1 "$W2/ledgers/B2.tsv"  "$W2/src/notes/vtamper.md"   NOT-VERIFIED "vault-mismatch"   "" "" "vault edited after row, same byte count"
emit_case B3  world 1 "$W2/ledgers/B3.tsv"  "$W2/src/notes/stamper.md"   NOT-VERIFIED "source-mismatch"  "" "" "source edited after row"
emit_case B4  world 1 "$W2/ledgers/B4.tsv"  "$W2/src/notes/vmiss.md"     NOT-VERIFIED "vault-absent"     "" "" "vault path absent, parent present"
emit_case B5  world 1 "$W2/ledgers/B5.tsv"  "$W2/src/notes/ok.md"        NOT-VERIFIED ""                "" "" "source hash column empty"
emit_case B6  world 1 "$W2/ledgers/B6.tsv"  "$W2/src/notes/ok.md"        NOT-VERIFIED ""                "" "" "vault hash column empty"
emit_case B7  world 1 "$W2/ledgers/B7.tsv"  "$W2/src/notes/ok.md"        NOT-VERIFIED ""                "" "" "header-only ledger"
emit_case B8  world 1 "$W2/ledgers/B8.tsv"  "$W2/src/notes/nope.md"      NOT-VERIFIED ""                "" "" "missing target"
emit_case B9  world 1 "$W2/ledgers/B9.tsv"  "$W2/src/notes/creds.pem"    NOT-VERIFIED "secrets-refusal"  "" "" "secret-shaped target"
emit_case B10 world 1 "$W2/ledgers/B10.tsv" "$W2/src/notes/fifo.md"      NOT-VERIFIED ""                "" "" "FIFO vault path (bounded, no hang)"
emit_case B11 world 1 "$W2/ledgers/B11.tsv" "$W2/src/notes/dangling.md"  NOT-VERIFIED ""                "" "" "dangling symlink vault path"
emit_case B12 world 0 "$W2/ledgers/B12.tsv" "$W2/src/notes/ok.md"        VERIFIED     ""                "" "" "valid final row, no trailing newline (advisory)"
emit_case B13 world 1 "$W2/ledgers/B13.tsv" "$W2/src/notes/empty.md"     VERIFIED     ""                "" "" "empty file, empty digest"
emit_case B14 world 0 "$W2/ledgers/B14.tsv" "$W2/src/dir-case"           VERIFIED     ""                "" "" "directory pair with manifest digests (advisory)"
emit_case B15 world 1 "$W2/ledgers/B15.tsv" "$W2/src/notes/spaces.md"    VERIFIED     ""                "" "" "spaces in names"
emit_case B16 world 1 "$W2/ledgers/B16.tsv" "$W2/src/notes/real-home.md" VERIFIED     ""                "" "" "real vault file match (read-only)"
emit_case B17 world 1 "$W2/ledgers/B17.tsv" "$W2/src/notes/real-home.md" NOT-VERIFIED "vault-mismatch"   "" "" "real vault, wrong ledger hash"
emit_case B18 world 1 "$W2/ledgers/B18.tsv" "$W2/src/notes/dup.md"       VERIFIED     ""                "" "" "duplicate rows, first fully matching"
emit_case B19 world 1 "$W2/ledgers/B19.tsv" "$W2/src/notes/second.md"    VERIFIED     ""                "" "" "row1 mismatching, row2 fully matching"
emit_case B20 world 0 "$W2/ledgers/B20.tsv" "$W2/src/notes/traversal.md" NOT-VERIFIED ""                "" "" "vault path traversal (advisory)"
emit_case B21 world 0 "$W2/ledgers/B21.tsv" "$W2/src/notes/symlink.md"   VERIFIED     ""                "" "" "vault symlink to real file (advisory)"
emit_case B22 world 1 "$W2/ledgers/B22.tsv" "$W2/src/notes/selfmove.md"  NOT-VERIFIED ""                "" "" "self-move row: vault path is the source itself"
emit_case B23 world 1 "$W2/ledgers/B23.tsv" "$W2/src/notes/alias.md"     NOT-VERIFIED ""                "" "" "path-alias row: vault path is a ../ spelling of the source"
emit_case B24 world 1 "$W2/ledgers/B24.tsv" "$W2/src/notes/symalias.md"  NOT-VERIFIED ""                "" "" "symlink-alias row: vault path is a symlink to the source"
emit_case B25 world 1 "$W2/ledgers/B25.tsv" "$W2/src/dir-case"           NOT-VERIFIED ""                "" "" "directory row with both hash columns empty (no receipt)"

log "judge-60: $(wc -l < "$W/cases.tsv") cases staged"

# ---------------------------------------------------------------- run helper
run_cand() { # $1 impl $2 ledger $3 target $4 outfile
  local impl="$1" ledger="$2" target="$3" ofile="$4"
  local envs=(env -u GIT_DIR SOUJI_LEDGER="$ledger" SOUJI_VAULT="$REALVAULT" \
    SHOKUNIN_ROOT="$W/world" TMPDIR="$W/tmp" LC_ALL=C TERM=dumb)
  local rc=1 txt="" i
  for i in 1 2 3; do
    case "$i" in
      1) txt="$("${envs[@]}" timeout -k 5 20 bash "$impl" --ledger "$ledger" --fallback "$target" 2>&1)"; rc=$? ;;
      2) txt="$("${envs[@]}" timeout -k 5 20 bash "$impl" --ledger "$ledger" "$target" 2>&1)"; rc=$? ;;
      3) txt="$("${envs[@]}" timeout -k 5 20 bash "$impl" "$target" 2>&1)"; rc=$? ;;
    esac
    printf '%s\n' "$txt" > "$ofile"
    [ "$rc" -eq 124 ] && break
    if printf '%s' "$txt" | grep -aqF -- "$target" && printf '%s' "$txt" | grep -aqE 'VERIFIED|NOT-SAFE|SAFE'; then
      [ "$rc" -ne 2 ] && break
    fi
  done
  printf 'rc=%s\n' "$rc" > "$ofile.rc"
  return 0
}

# ------------------------------------------------------------------ main loop
SUMMARY_TSV="$W/summary.tsv"
: > "$SUMMARY_TSV"
: > "$W/impls.tsv"

for impl in $CANDS; do
  iname="$(basename "$impl" .sh)"
  odir="$W/out/$iname"; mkdir -p "$odir"
  isha="$(sha256sum "$impl" | awk '{print $1}')"
  ibytes="$(stat -c %s "$impl")"
  log "== candidate $iname sha=${isha:0:12} bytes=$ibytes"

  st_out="$(env -u GIT_DIR -u SOUJI_SELFTEST_ACTIVE TMPDIR="$W/tmp" LC_ALL=C TERM=dumb \
    timeout -k 5 300 bash "$impl" --selftest 2>&1)"
  st_rc=$?
  printf '%s\n' "$st_out" > "$odir/selftest.log"
  printf '%s\tselftest\tSELFTEST\t%s\t%s\n' "$(pl "$iname")" "exit=$st_rc" "$([ "$st_rc" -eq 0 ] && echo true || echo false)" >> "$SUMMARY_TSV"

  txt="$(env -u GIT_DIR TMPDIR="$W/tmp" LC_ALL=C TERM=dumb timeout -k 5 20 bash "$impl" 2>&1)"; rc=$?
  printf '%s\tnoargs\tCLI\t%s\t%s\n' "$(pl "$iname")" "exit=$rc" "$([ "$rc" -eq 2 ] && echo true || echo false)" >> "$SUMMARY_TSV"
  txt="$(env -u GIT_DIR TMPDIR="$W/tmp" LC_ALL=C TERM=dumb timeout -k 5 20 bash "$impl" --bogus-flag-xyz 2>&1)"; rc=$?
  printf '%s\tunknownflag\tCLI\t%s\t%s\n' "$(pl "$iname")" "exit=$rc" "$([ "$rc" -eq 2 ] && echo true || echo false)" >> "$SUMMARY_TSV"

  hits="$(grep -vE '^[[:space:]]*#' "$impl" | grep -nE '(^|[^[:alnum:]_])git[[:space:]]+(-C[[:space:]]+[^[:space:]]+[[:space:]]+)?(fetch|push|reset|rebase|pull)([^[:alnum:]_-]|$)' || true)"
  nhits=$(printf '%s' "$hits" | grep -c . || true)
  printf '%s\tgitwrite\tRAIL\t%s\t%s\n' "$(pl "$iname")" "hits=$nhits" "$([ -z "$hits" ] && echo true || echo false)" >> "$SUMMARY_TSV"
  guiname="$(grep -vE '^[[:space:]]*#' "$impl" | grep -c 'usr/bin/obsidian' || true)"
  printf '%s\tguiname\tRAIL\t%s\tinfo\n' "$(pl "$iname")" "occurrences=$guiname" >> "$SUMMARY_TSV"

  n=0
  while IFS=$'\t' read -r cid kind hard ledger target wcls wreason contains evcontains note; do
    [ -n "$cid" ] || continue
    n=$((n+1))
    [ "$ledger" = "-" ] && ledger="$W/nonexistent-ledger.tsv"
    ofile="$odir/$(printf '%03d' "$n")-$cid.out"
    run_cand "$impl" "$ledger" "$target" "$ofile"
    rc=$(sed -n 's/^rc=//p' "$ofile.rc" 2>/dev/null)
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$(pl "$iname")" "$(pl "$cid")" "$(pl "$kind")" "$(pl "$hard")" "$(pl "$ledger")" \
      "$(pl "$target")" "$(pl "$wcls")" "$(pl "$wreason")" "$(pl "$contains")" \
      "$(pl "$evcontains")" "rc=$rc" "$(pl "$ofile")" "$(pl "$note")" >> "$SUMMARY_TSV"
  done < "$W/cases.tsv"

  isha_after="$(sha256sum "$impl" | awk '{print $1}')"
  printf '%s\tshastable\tRAIL\t%s\t%s\n' "$(pl "$iname")" "before=${isha:0:12} after=${isha_after:0:12}" "$([ "$isha" = "$isha_after" ] && echo true || echo false)" >> "$SUMMARY_TSV"
  printf '%s\t%s\t%s\n' "$(pl "$iname")" "$(pl "$impl")" "$(pl "$isha")" >> "$W/impls.tsv"
done

# -------------------------------------------------------------- rails: after
GUI_AFTER="$(gui_count)"; GUI_AFTER=${GUI_AFTER:-0}
LIVE_SHA_A="$(sha256sum "$LIVE_LEDGER" 2>/dev/null | awk '{print $1}')"
LIVE_LN_A="$(wc -l < "$LIVE_LEDGER" 2>/dev/null | tr -d ' ')"
(cd "$REALVAULT" && find . -type f -not -path './.git/*' -print0 2>/dev/null | sort -z | xargs -0 -r sha256sum 2>/dev/null | sha256sum) > "$W/vault.after" 2>/dev/null
VFILE_A="$(find "$REALVAULT" -type f 2>/dev/null | wc -l | tr -d ' ')"
HEAD_A="$(git -C "$LANE" rev-parse HEAD 2>/dev/null || echo '')"
DIRTY_A="$(git -C "$LANE" status --porcelain 2>/dev/null | grep -v '^??' | wc -l | tr -d ' ')"
UFO_A=""
[ -d "$UFO_STATE" ] && UFO_A="$(find "$UFO_STATE" -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1)"
WD_A="$(stat -c '%Y:%s' "$WATCHDOG" 2>/dev/null || echo absent)"

VAULT_OK=0; cmp -s "$W/vault.before" "$W/vault.after" && VAULT_OK=1
LEDGER_OK=0; { [ "$LIVE_SHA_B" = "$LIVE_SHA_A" ] && [ "$LIVE_LN_A" = "1" ]; } && LEDGER_OK=1
GUI_OK=0; [ "$GUI_BEFORE" = "$GUI_AFTER" ] && GUI_OK=1
HEAD_OK=0; [ "$HEAD_B" = "$HEAD_A" ] && HEAD_OK=1
WD_OK=0; [ "$WD_B" = "$WD_A" ] && WD_OK=1
UFO_OK=0; [ "$UFO_B" = "$UFO_A" ] && UFO_OK=1

cat > "$W/rails.txt" <<EOF
gui_ok=$GUI_OK gui_before=$GUI_BEFORE gui_after=$GUI_AFTER
vault_ok=$VAULT_OK files_before=$VFILE_B files_after=$VFILE_A
ledger_ok=$LEDGER_OK lines_after=$LIVE_LN_A sha_before=${LIVE_SHA_B:0:16} sha_after=${LIVE_SHA_A:0:16}
head_ok=$HEAD_OK tracked_dirty_after=$DIRTY_A
watchdog_ok=$WD_OK ufo_state_ok=$UFO_OK
EOF
cat "$W/rails.txt" >&2

# ------------------------------------------------------------- score + emit
J60_W="$W" J60_OUT="$OUT" J60_LANE="$LANE" python3 - <<'PYEOF'
import json, os, re, datetime

W = os.environ['J60_W']; OUT = os.environ['J60_OUT']; LANE = os.environ['J60_LANE']
DASH = "-"

def unpl(x):
    return "" if x == DASH else x

def norm_class(tok):
    tok = (tok or "").strip().upper()
    if tok in ("VERIFIED", "SAFE"): return "VERIFIED"
    if tok.startswith("NOT-VERIFIED") or tok.startswith("NOT_VERIFIED"): return "NOT-VERIFIED"
    if tok in ("NOT-SAFE", "NOT_SAFE"): return "NOT-VERIFIED"
    if tok.startswith("VERIFIED"): return "VERIFIED"
    if tok.startswith("NOT"): return "NOT-VERIFIED"
    return None

def parse_out(text, target):
    """Return (class, reason, receipt, line) for the target.

    Some tools (impl-24) print the r4 reason line WITHOUT the path
    (``NOT-VERIFIED(source-absent)``) and the path-bearing r2 line
    separately. We therefore (a) prefer a path-bearing line when present,
    and (b) fall back to a path-less r4 line when no path-bearing line
    carries a verdict.
    """
    bare = None  # (cls, reason, line) from a path-less r4 line
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line: continue
        if line.startswith("{"):
            try: d = json.loads(line)
            except Exception: d = None
            if isinstance(d, dict) and d.get("path") is not None:
                p = str(d.get("path"))
                if p != target and not p.endswith(target): continue
                return (norm_class(str(d.get("verdict", ""))),
                        str(d.get("reason") or d.get("receipt") or ""),
                        str(d.get("receipt") or ""), line)
        fields = line.split("\t")
        pi = None
        for idx, f in enumerate(fields[:4]):
            if f == target or f.endswith(target): pi = idx; break
        f0 = fields[0].strip()
        m0 = re.match(r"^(NOT-VERIFIED|NOT_VERIFIED|VERIFIED)\s*\((.*)\)\s*$", f0)
        if pi is None:
            if m0 and bare is None and len(fields) == 1:
                bare = (norm_class(m0.group(1)), m0.group(2).strip(), line)
            continue
        m = re.match(r"^(NOT-VERIFIED|NOT_VERIFIED|VERIFIED)\s*\((.*)\)\s*$", f0)
        if m:
            return (norm_class(m.group(1)), m.group(2).strip(), "", line)
        if f0 == "VERDICT" and len(fields) >= 4:
            # merge a path-less r4 reason line seen earlier in the stream
            if bare and norm_class(fields[2]) == bare[0]:
                return (bare[0], bare[1], fields[3], line + " || " + bare[2])
            return (norm_class(fields[2]), fields[3] if fields[3] != "none" else "", fields[3], line)
        if f0 in ("VERIFIED", "SAFE"):
            rec = fields[2] if len(fields) > 2 else ""
            return ("VERIFIED", rec, rec, line)
        if f0 in ("NOT-VERIFIED", "NOT-SAFE", "NOT_SAFE"):
            return ("NOT-VERIFIED", fields[2] if len(fields) > 2 else "", "", line)
    if bare:
        return (bare[0], bare[1], "", bare[2])
    for raw in (text or "").splitlines():
        if target in raw and re.search(r"VERIFIED|NOT-SAFE|SAFE", raw):
            m = re.search(r"(NOT-VERIFIED|NOT-SAFE|VERIFIED|SAFE)", raw)
            if m: return (norm_class(m.group(1)), raw, "", raw.strip())
    return (None, None, None, None)

def reason_blob(reason, line, target):
    blob = (reason or "") + " " + (line or "")
    return blob.replace(target, " ")

def contains_ok(contains, reason, line, target):
    if not contains: return True, ""
    blob = (reason_blob(reason, line, target)).lower()
    alias_used = []
    for tok in contains.split(","):
        tok = tok.strip().lower()
        if not tok: continue
        if tok in ("verified", "not-verified", "safe", "not-safe"): continue
        if tok in blob: continue
        # same-family alias acceptance (recorded, not silent)
        if family_token_ok(tok, blob):
            alias_used.append(tok)
            continue
        return False, ""
    return True, (",".join(alias_used) if alias_used else "")

def family_token_ok(tok, blob):
    """Accept a contract token via its failure-family aliases (e.g.
    vault-absent ~ vault-unreachable ~ vault-missing)."""
    side = "source" if "source" in tok else ("vault" if "vault" in tok else None)
    absent = any(t in tok for t in ("absent", "missing", "unreachable", "not-found", "no-such"))
    mismatch = any(t in tok for t in ("mismatch", "hash", "digest", "drift", "differ"))
    fam_absent = any(t in blob for t in ("absent", "missing", "unreachable", "not-found", "notfound", "no-such"))
    fam_mismatch = any(t in blob for t in ("mismatch", "differ", "drift", "changed", "hash", "digest"))
    if side and side not in blob:
        if not (side == "source" and absent and "unreachable" in blob):
            return False
    if absent and not fam_absent: return False
    if mismatch and not fam_mismatch: return False
    if not absent and not mismatch:
        return tok in blob
    return True

def family_reason_ok(want, reason, line, target):
    if not want: return True
    low = reason_blob(reason, line, target).lower()
    wr = want.lower()
    if "secret" in wr or "credential" in wr:
        return ("secret" in low) or ("credential" in low)
    side = "source" if "source" in wr else ("vault" if "vault" in wr else None)
    absent = any(t in wr for t in ("absent", "missing", "unreachable", "not-found", "no-such"))
    mismatch = any(t in wr for t in ("mismatch", "hash", "digest", "drift", "differ", "changed"))
    ok = True
    if side:
        # side token may appear as the family word or in a row/path token kept in evidence
        ok = ok and (side in low or (side == "source" and "src" in low) or (side == "vault" and "vp" in low))
    if absent:
        ok = ok and any(t in low for t in ("absent", "missing", "unreachable", "not-found", "notfound", "no-such", "no_row", "no-row"))
    if mismatch:
        ok = ok and any(t in low for t in ("mismatch", "differ", "drift", "changed", "hash", "digest"))
    if not side and not absent and not mismatch:
        return wr in low
    return ok

summary = {}
order = []
with open(os.path.join(W, "summary.tsv")) as fh:
    for ln in fh:
        p = ln.rstrip("\n").split("\t")
        if len(p) < 5: continue
        summary.setdefault(unpl(p[0]), []).append(p)
        if unpl(p[0]) not in order: order.append(unpl(p[0]))

impls = {}
with open(os.path.join(W, "impls.tsv")) as fh:
    for ln in fh:
        p = ln.rstrip("\n").split("\t")
        if len(p) == 3: impls[p[0]] = {"path": p[1], "sha256": p[2]}

n_cases = 0
with open(os.path.join(W, "cases.tsv")) as fh:
    n_cases = sum(1 for ln in fh if ln.strip())

per_impl = {}
for iname in order:
    rows = summary[iname]
    results = []
    hard_pass = hard_fail = info = 0
    for p in rows:
        kind = p[2]
        if kind == "SELFTEST":
            ok = p[4] == "true"
            results.append({"id": "selftest", "kind": "selftest", "expected": "exit=0",
                            "actual": p[3], "result": "pass" if ok else "fail", "detail": ""})
            hard_pass += 1 if ok else 0; hard_fail += 0 if ok else 1
            continue
        if kind == "CLI":
            ok = p[4] == "true"
            results.append({"id": p[1], "kind": "cli", "expected": "exit=2",
                            "actual": p[3], "result": "pass" if ok else "fail", "detail": ""})
            hard_pass += 1 if ok else 0; hard_fail += 0 if ok else 1
            continue
        if kind == "RAIL":
            if p[1] in ("gitwrite", "shastable"):
                ok = p[4] == "true"
                results.append({"id": p[1], "kind": "rail",
                                "expected": "clean" if p[1] == "gitwrite" else "stable sha",
                                "actual": p[3], "result": "pass" if ok else "fail", "detail": ""})
                hard_pass += 1 if ok else 0; hard_fail += 0 if ok else 1
            else:
                results.append({"id": p[1], "kind": "rail", "expected": "info",
                                "actual": p[3], "result": "info", "detail": ""})
                info += 1
            continue
        if len(p) < 13: continue
        _, cid, kind, hard, ledger, target, wcls, wreason, contains, evc, rc, ofile, note = p[:13]
        ledger, target, wcls = unpl(ledger), unpl(target), unpl(wcls)
        wreason, contains, evc, rc, ofile = unpl(wreason), unpl(contains), unpl(evc), unpl(rc), unpl(ofile)
        text = ""
        try: text = open(ofile).read()
        except Exception: pass
        cls, reason, receipt, line = parse_out(text, target)
        ok = (cls == wcls)
        detail = ""
        if ok and contains:
            ok, alias = contains_ok(contains, reason, line, target)
            if not ok: detail = f"contains {contains!r} absent"
            elif alias: detail = f"alias-accepted for {alias}"
        elif ok and wreason:
            ok = family_reason_ok(wreason, reason, line, target)
            if not ok: detail = f"reason {reason!r} !~ {wreason!r}"
        if ok and evc and evc not in text:
            ok = False; detail = f"evidence {evc!r} absent"
        if "rc=124" in rc or "rc=137" in rc:
            ok = False; detail = "hang (rc=%s)" % rc
        is_hard = (hard == "1")
        result = "pass" if ok else ("fail" if is_hard else "info")
        if not ok and not detail:
            detail = "no verdict line naming the target" if cls is None else f"class {cls} != {wcls}"
        actual = f"{rc}; line={(line or 'NONE')[:170]}"
        results.append({"id": cid, "kind": kind, "expected": f"{wcls}({wreason or contains or 'any'})",
                        "actual": actual, "result": result, "detail": detail})
        if result == "fail": hard_fail += 1
        elif result == "pass": hard_pass += 1
        else: info += 1
    per_impl[iname] = {
        "path": impls.get(iname, {}).get("path", ""),
        "sha256": impls.get(iname, {}).get("sha256", ""),
        "selftest_exit": next((p[3].split("=")[-1] for p in rows if p[2] == "SELFTEST"), ""),
        "hard_pass": hard_pass, "hard_fail": hard_fail, "info": info,
        "cases": results,
    }

ranking = sorted(per_impl.keys(), key=lambda i: (per_impl[i]["hard_fail"], -per_impl[i]["hard_pass"], i))
winner = ranking[0] if ranking and per_impl[ranking[0]]["hard_fail"] == 0 else None

toks = {}
for ln in open(os.path.join(W, "rails.txt")):
    for t in ln.split():
        if "=" in t:
            k, _, v = t.partition("="); toks[k] = v

doc = {
    "seat": "S60",
    "role": "final judge — independent vault-verification battery (round 4)",
    "round": 4,
    "task": "Obsidian-CLI vault verification",
    "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "harness": {"path": "tests/vault/judge-60-vault.sh",
                "sha256": os.popen("sha256sum %s/tests/vault/judge-60-vault.sh 2>/dev/null" % LANE).read().split()[0:1]},
    "lane_repo": LANE,
    "fixture_universe": W,
    "case_count": n_cases,
    "candidates": per_impl,
    "ranking": ranking,
    "winner": winner,
    "rails": {
        "gui_spawned": "no" if toks.get("gui_ok") == "1" else "YES",
        "real_vault_unchanged": toks.get("vault_ok") == "1",
        "real_vault_files_before": toks.get("files_before", ""),
        "real_vault_files_after": toks.get("files_after", ""),
        "live_ledger_header_only": toks.get("ledger_ok") == "1",
        "live_ledger_lines_after": toks.get("lines_after", ""),
        "lane_head_stable": toks.get("head_ok") == "1",
        "lane_tracked_dirty_after": toks.get("tracked_dirty_after", ""),
        "watchdog_untouched": toks.get("watchdog_ok") == "1",
        "ufo_state_untouched": toks.get("ufo_state_ok") == "1",
    },
    "notes": [
        "Expected verdicts are computed by this battery from the ledger+filesystem; tests/vault/case-V* builders supply the round's contract fixtures (B-cases are this battery's own single-row-ledger world).",
        "Verdict extraction accepts r4 vocabulary (VERIFIED / NOT-VERIFIED(reason)) and r2 form (VERDICT\\tpath\\tSAFE...); fixture cases match their accept.contains tokens, world cases use a reason-family rule (side + absent/mismatch).",
        "Advisory cases (B12 no-trailing-newline, B14 dir digest, B20 traversal, B21 symlink) never hard-fail a candidate.",
        "A hang (rc=124/137) on any case is a hard failure of that case.",
    ],
}
doc["harness"]["sha256"] = doc["harness"]["sha256"][0] if doc["harness"]["sha256"] else ""
doc["verdict"] = "PASS" if winner else "NO-CLEAN-CANDIDATE"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as fh:
    json.dump(doc, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

print(f"judge-60: wrote {OUT} (cases={n_cases})")
for i in ranking:
    d = per_impl[i]
    print(f"  {i}: hard_pass={d['hard_pass']} hard_fail={d['hard_fail']} info={d['info']} selftest={d['selftest_exit']}")
print(f"  winner={winner} verdict={doc['verdict']}")
PYEOF
exit 0
