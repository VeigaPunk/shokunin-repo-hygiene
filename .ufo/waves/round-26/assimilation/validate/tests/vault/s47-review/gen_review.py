#!/usr/bin/env python3
"""S47 review generator — round 4 (Obsidian-CLI vault verification).

Reads /tmp/s47/review/out-<tag>/{probes.tsv,meta.txt,help.txt} produced by
probe.sh and emits a vreview-47-shaped JSON for the S57 aggregator:
  {"seat":"S47","role":"reviewer","round":4,"spec":...,"method":{...},
   "impls":{name:{sha256,shipped_mode,scores,total,max_total,fatal_defects,
                  detail,probes,selectable,notes}}}
Dimension mapping (10 points each):
  D1-ledger      L1 L10 L24 L25 L26 L19 L18 (positive/parse semantics)
  D2-integrity   L2 L3 L4 L5 L7 L8 L8b L8c L9 L20 RV2 (must not verify)
  D3-negative    L6 L12 L13 L15 L17 L21 L22 L23 L27 L28 RV3 (edges/negatives)
  live-vault     RV1 RV2 RV3 (real vault read-only correctness)
  rails          R1 R2 R3 R4 R5 L14 (safety: vault/live-ledger/poison/world/
                 strace/secrets) — any failure = fatal
  selftest       ST (exit 0)
"""
import json, os, sys, hashlib, datetime

def sha256f(p):
    try:
        h = hashlib.sha256()
        with open(p, 'rb') as f:
            for b in iter(lambda: f.read(1 << 20), b''):
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None

DIMS = {
    "D1-ledger":    ["L1", "L10", "L24", "L25", "L26", "L19", "L18", "L29", "L31", "L33"],
    "D2-integrity": ["L2", "L3", "L4", "L5", "L7", "L8", "L8b", "L8c", "L9", "L20", "L30", "RV2"],
    "D3-negative":  ["L6", "L12", "L13", "L15", "L17", "L21", "L22", "L23", "L27", "L28"],
    "live-vault":   ["RV1", "RV2"],
    "rails":        ["R1", "R2", "R3", "R4", "R5", "L14"],
    "selftest":     ["ST"],
}
FATAL = {"R1", "R2", "R3", "R4", "R5", "L14"}

def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else None
    if tag:
        dirs = [f"/tmp/s47/review/out-{tag}"]
        names = [tag]
    else:
        import glob
        dirs = sorted(glob.glob("/tmp/s47/review/out-impl-*"))
        names = [os.path.basename(d).replace("out-", "") for d in dirs]
    out_impls = {}
    for d, name in zip(dirs, names):
        tsv = os.path.join(d, "probes.tsv")
        if not os.path.exists(tsv):
            continue
        rows = {}
        with open(tsv) as f:
            hdr = f.readline()
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 8:
                    continue
                pid, exp, cls, verdict, receipt, passv, rc, ev = parts[:8]
                rows[pid] = {
                    "expect": exp, "observed_class": cls, "verdict": verdict,
                    "receipt": receipt, "pass": passv == "1",
                    "exit": rc, "evidence": ev,
                }
        meta = {}
        mp = os.path.join(d, "meta.txt")
        if os.path.exists(mp):
            for line in open(mp):
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    meta[k] = v
                    if k == "impl":
                        import re as _re
                        m = _re.search(r"sha=([0-9a-f]+)\s+mode=(\S+)", v)
                        if m:
                            meta["sha"], meta["mode"] = m.group(1), m.group(2)
                elif line.startswith("PROBES"):
                    meta["summary"] = line
        scores, detail, failed = {}, {}, []
        for dim, ids in DIMS.items():
            got = [i for i in ids if i in rows]
            npass = sum(1 for i in got if rows[i]["pass"])
            scores[dim] = round(10.0 * npass / len(got), 2) if got else 0.0
            detail[dim] = {
                "pass": npass, "of": len(got),
                "failed": [i for i in got if not rows[i]["pass"]],
                "missing": [i for i in ids if i not in rows],
            }
            failed.extend(i for i in got if not rows[i]["pass"])
        total = round(sum(scores.values()), 2)
        fatals = sorted(set(f for f in failed if f in FATAL))
        out_impls[name] = {
            "sha256": meta.get("sha"),
            "shipped_mode": meta.get("mode"),
            "scores": scores,
            "total": total,
            "max_total": 10 * len(DIMS),
            "fatal_defects": fatals,
            "detail": detail,
            "probes": rows,
            "selectable": not fatals,
            "notes": meta.get("summary", ""),
        }
    doc = {
        "seat": "S47",
        "role": "reviewer",
        "round": 4,
        "spec": "tests/vault (case-V* expected.json) + tools/souji-verify.spec.md; "
                "ledger-backed moved-to-obsidian vault verification (read-only vault)",
        "method": {
            "fixture": "/tmp/s47/review/world — independent world: 30 single-row "
                       "ledger probes (tamper/absent/empty-hash/subtle/CRLF/dup/"
                       "traversal/FIFO/symlink-loop/mode-000/secrets) + real-vault rows",
            "rails": "vault sha256 manifest before/after, live ledger digest, "
                     "poisoned PATH obsidian shim, world manifest, strace write audit",
            "vocabulary": "VERIFIED/NOT-VERIFIED and SAFE/NOT-SAFE both accepted; "
                          "verdict token scanned across tab fields",
            "dims": {k: v for k, v in DIMS.items()},
        },
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "impls": out_impls,
    }
    outpath = sys.argv[2] if len(sys.argv) > 2 else "/tmp/s47/review/vreview-47.json"
    with open(outpath, "w") as f:
        json.dump(doc, f, indent=1)
    for name, e in out_impls.items():
        print(name, "total", e["total"], "fatal", e["fatal_defects"],
              "selectable", e["selectable"])
    print("wrote", outpath)

if __name__ == "__main__":
    main()
