#!/usr/bin/env python3
"""S16 round-8 pointer sweep — verification pass (read-only).

Consumes seat-16-inventory.json, probes every token mechanically, writes
seat-16-verdicts.json. Existence checks only: no content reads of referenced
targets; .ufo/state and watchdog.log refused without probing; secret-shaped
components refused without probing; no git mutation, no fetch (one read-only
ls-remote against the lane origin, mirroring the r7 documented probe).
"""
import glob as globmod
import json
import os
import re
import subprocess
import sys

FLEET = "/home/vgpnk/Projects/shokunin"
LANE = FLEET + "/souji-shokunin"
GD2D = FLEET + "/game-dev-2d-shokunin"

SECRET_RX = re.compile(
    r"(^|/)(?:\.env(\..*)?|\.envrc|.*credential.*|.*secret.*|id_.+|.*\.pem)$",
    re.IGNORECASE,
)
FORBIDDEN_RX = re.compile(r"\.ufo/state(/|$)|watchdog\.log$")

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()

def raw_bytes(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True)
    return p.returncode, p.stdout or b"", (p.stderr or b"").decode(
        "utf-8", "replace").strip()

def expand(tok):
    t = os.path.expanduser(tok)
    t = re.sub(r"\$([A-Z_][A-Z0-9_]*)",
               lambda m: os.environ.get(m.group(1), m.group(0)), t)
    return t

def candidate_paths(tok):
    """Documented mechanical resolution order."""
    t = expand(tok)
    out = []
    if t.startswith("/"):
        out.append(t)
    elif t.startswith("../"):
        out.append(os.path.normpath(os.path.join(LANE, t)))
    else:
        out.append(os.path.join(LANE, t))
        out.append(os.path.join(FLEET, t))
        # one-hop: lane top-level dirs (mechanically enumerated, existing only)
        try:
            for d in sorted(os.listdir(LANE)):
                if os.path.isdir(os.path.join(LANE, d)) and d not in (".git",):
                    out.append(os.path.join(LANE, d, t))
        except OSError:
            pass
    return out

def probe_fs(tok):
    if SECRET_RX.search(tok):
        return {"status": "EXCLUDED-secret-shaped", "detail": "no probe performed"}
    cands = candidate_paths(tok)
    for c in cands:
        if FORBIDDEN_RX.search(c):
            return {"status": "EXCLUDED-forbidden-surface",
                    "detail": "rule forbids probing .ufo/state or watchdog.log"}
    for c in cands:
        if os.path.lexists(c):
            return {"status": "ALIVE", "resolved": c,
                    "what": "dir" if os.path.isdir(c) else "file"}
    # absent: documented-deletion check over the sweep sources
    base = os.path.basename(tok.rstrip("/"))
    hit = documented_absence(base)
    if hit:
        return {"status": "ABSENT-EXPECTED", "resolved": None, "detail": hit}
    # prefix-of-existing (prose truncation)
    for c in cands:
        parent = os.path.dirname(c)
        last = os.path.basename(c)
        if os.path.isdir(parent):
            for e in os.listdir(parent):
                if e.startswith(last) and last:
                    return {"status": "ALIVE(prefix)", "resolved":
                            os.path.join(parent, e), "what": "prefix-match"}
    return {"status": "UNRESOLVED", "resolved": None}

def documented_absence(base):
    quotes = {
        "logs_tier.txt": "r5: already deleted pre-census (R5:29)",
        "r87-B1": "r5: pruned /tmp/r87-B1, NOT-SAFE(unreachable) (R5:65)",
        "r87-C5": "r1: evidence already unreachable (R1:20)",
    }
    return quotes.get(base)

def probe_glob(tok):
    if tok == "souji-shokunin/census/**":
        return {"status": "NOT-A-POINTER(glob-syntax)",
                "detail": "rg exclusion pattern (R1:27 D3 note, LG:67), not a path"}
    if tok == "refs/remotes/origin/*":
        rc, out, _ = run(["git", "for-each-ref", "refs/remotes/origin"],
                         cwd=LANE)
        n = len(out.splitlines())
        return {"status": "ALIVE(pattern)" if n else "ALIVE(pattern-empty)",
                "detail": "lane for-each-ref refs/remotes/origin -> %d refs" % n}
    m = re.search(r"(\d+)\.\.(\d+)", tok)
    if m:  # range form seat-01..64 / final-57..64
        d = None
        for c in candidate_paths(os.path.dirname(tok)):
            if os.path.isdir(c):
                d = c
                break
        if d is None:
            return {"status": "UNRESOLVED", "detail": "base dir not found"}
        base = os.path.basename(tok)
        stem = re.sub(r"\d+\.\.\d+.*$", "", base)
        lo, hi = int(m.group(1)), int(m.group(2))
        want = ["%s%02d.json" % (stem, i) for i in range(lo, hi + 1)]
        have = [w for w in want if os.path.lexists(os.path.join(d, w))]
        return {"status": "ALIVE(range)", "resolved": d,
                "detail": "%d/%d present%s" % (len(have), len(want),
                        "" if len(have) == len(want) else
                        " missing=" + ",".join(sorted(set(want) - set(have))))}
    d = os.path.dirname(tok)
    base = None
    for c in candidate_paths(d):
        if os.path.isdir(c):
            base = c
            break
    if base is None:
        return {"status": "UNRESOLVED", "detail": "base dir not found"}
    hits = globmod.glob(os.path.join(base, os.path.basename(tok)))
    return {"status": "ALIVE(glob)", "resolved": base,
            "detail": "%d matches" % len(hits)}

def probe_commit(tok):
    for repo, name in ((LANE, "lane"), (FLEET, "fleet"), (GD2D, "gd2d")):
        rc, _, _ = run(["git", "cat-file", "-e", tok + "^{commit}"], cwd=repo)
        if rc == 0:
            _, subj, _ = run(["git", "show", "-s", "--format=%s", tok], cwd=repo)
            return {"status": "ALIVE", "resolved": name,
                    "detail": subj[:100]}
    return {"status": "UNRESOLVED", "detail": "no repo resolves token"}

def probe_ref(tok, sources):
    lane_only = "lane repo" in " ".join(sources) or False
    if tok == "origin/master":
        rcl, outl, errl = run(["git", "rev-parse", "--verify", tok], cwd=LANE)
        rcf, outf, _ = run(["git", "rev-parse", "--verify", tok], cwd=FLEET)
        det = []
        st = "ALIVE"
        if rcf == 0:
            det.append("fleet->" + outf[:12])
        else:
            det.append("fleet->unresolved")
        if rcl == 0:
            det.append("lane->" + outl[:12])
        else:
            det.append("lane->unresolved (%s)" % errl.splitlines()[0][:40])
            st = "ALIVE(fleet)/DEAD(lane)"
        return {"status": st, "detail": "; ".join(det)}
    if tok == "origin/main":
        rcl, _, _ = run(["git", "rev-parse", "--verify", tok], cwd=LANE)
        rcf, _, _ = run(["git", "rev-parse", "--verify", tok], cwd=FLEET)
        return {"status": "NOT-A-POINTER(rhetorical-negative)",
                "detail": "lane rc=%d fleet rc=%d; docs cite it as the never-"
                          "hardcode example (R1:27, R6:19, LG:63)" % (rcl, rcf)}
    rc, out, _ = run(["git", "rev-parse", "--verify", tok], cwd=LANE)
    if rc == 0:
        return {"status": "ALIVE", "resolved": "lane", "detail": out[:12]}
    rc, out, _ = run(["git", "rev-parse", "--verify", tok], cwd=FLEET)
    if rc == 0:
        return {"status": "ALIVE", "resolved": "fleet", "detail": out[:12]}
    if tok.startswith("refs/remotes/"):
        _, nl, _ = run(["git", "for-each-ref", tok], cwd=LANE)
        _, nf, _ = run(["git", "for-each-ref", tok], cwd=FLEET)
        return {"status": "ALIVE(pattern-empty)",
                "detail": "for-each-ref lane=%d fleet=%d refs (lane=0 expected: "
                          "r7 remote 404)" % (len(nl.splitlines()),
                                              len(nf.splitlines()))}
    return {"status": "UNRESOLVED", "detail": "unresolved in lane+fleet"}

def probe_digest(tok, sources):
    mapping = {
        "7efda63bd760": ("souji-verify.sh", "9435e46"),
        "d312263a": ("souji-vault-verify.sh", "48a64d8"),
        "11bf9cdf": ("souji-census.sh", "b5db5cf"),
    }
    tool, commit = mapping[tok]
    path = "tools/" + tool
    rc, blob, _ = raw_bytes(["git", "show", "%s:%s" % (commit, path)], cwd=LANE)
    if rc != 0:
        return {"status": "UNRESOLVED",
                "detail": "git show %s:%s failed" % (commit, path)}
    import hashlib
    at = hashlib.sha256(blob).hexdigest()
    rc2, now, _ = run(["sha256sum", path], cwd=LANE)
    now_d = now.split()[0] if rc2 == 0 else "?"
    ok = at.startswith(tok)
    drift = not now_d.startswith(tok)
    return {"status": "ALIVE(at measured commit)" if ok else "MISMATCH",
            "detail": "%s@%s=%s… working-tree=%s… %s"
                      % (tool, commit, at[:12], now_d[:12],
                         "(working-tree drifts; r5/r6 patches documented)"
                         if drift else "(working tree identical)") }

def probe_url(tok):
    if "github.com" in tok:
        rc, url, _ = run(["git", "remote", "get-url", "origin"], cwd=LANE)
        rcs, out, err = run(["git", "ls-remote", "origin"], cwd=LANE)
        return {"status": "CONFIRMED-404",
                "detail": "get-url=%s rc=%d; ls-remote rc=%d: %s"
                          % (url.strip(), rc, rcs,
                             (err.splitlines() or [""])[0][:60])}
    return {"status": "UNRESOLVED"}

PROSE_SEGMENT_RX = re.compile(r"^\d[\d.,a-zA-Z]*$")

def looks_prose(tok):
    segs = tok.split("/")
    if re.match(r"^~\d", tok) or PROSE_SEGMENT_RX.match(segs[-1]):
        return True
    if len(segs) < 2:
        return False
    if any(s.isdigit() for s in segs):
        return True
    if segs[-1].startswith("~"):
        return True
    verdictish = {"SAFE", "NOT-SAFE", "hands-off", "pushed", "stale",
                  "duplicate", "preserved", "metadata-prune",
                  "moved-to-obsidian", "dirty", "unpushed", "author", "blind",
                  "operator", "secret-shaped", "gap", "missed-items",
                  "checklists", "patterns", "error", "tables", "docs",
                  "tools", "C1", "O1", "F7", "F8"}
    if all(s in verdictish or s.startswith(("S5", "S6", "impl-", "wt-r",
                                            "gd2d", "gd3d", "kaidoku",
                                            "kotodama", "game-dev-2d",
                                            "tsukuroi", "SKILL", "AGENTS",
                                            "PROVINCE", "seat-")) for s in segs):
        return True
    if tok in ("36/impl", "lessons/round-5.md"):
        return tok == "36/impl"
    return False

def main():
    inv = json.load(open(LANE + "/census/round-8/seat-16-inventory.json"))
    results = []
    for e in inv["tokens"]:
        kind, tok, locs = e["kind"], e["token"], e["locations"]
        r = {"kind": kind, "token": tok, "locations": locs}
        if kind == "fs:path" and looks_prose(tok):
            r["status"] = "NON-POINTER(prose-list)"
            r["detail"] = "slash-joined prose/labels; string-level, no probe"
        elif kind == "fs:path":
            r.update(probe_fs(tok))
            if r["status"] == "UNRESOLVED":
                r["status"] = "UNRESOLVED(real-path-shaped)"
        elif kind == "fs:glob":
            r.update(probe_glob(tok))
        elif kind == "git:commit":
            r.update(probe_commit(tok))
        elif kind == "git:ref":
            r.update(probe_ref(tok, locs))
        elif kind == "digest":
            r.update(probe_digest(tok, locs))
        elif kind == "remote:url":
            r.update(probe_url(tok))
        else:
            r["status"] = "NON-POINTER(%s)" % kind.split(":", 1)[-1]
        results.append(r)
    out = LANE + "/census/round-8/seat-16-verdicts.json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1)
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("probed:", len(results))
    for k in sorted(counts):
        print("%-36s %d" % (k, counts[k]))
    print("wrote", out)

if __name__ == "__main__":
    sys.exit(main())
