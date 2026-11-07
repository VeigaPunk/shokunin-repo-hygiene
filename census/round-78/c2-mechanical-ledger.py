#!/usr/bin/env python3
"""souji r78 C2 control K-b: a mechanical ledger generator (S77CriticClaims "thin": a short generator reached
35/35 on the r77 population). It writes a ledger for a population from existence tests alone, adds no byte to
the lane and verifies nothing itself: FLEET when a `.ufo/` token exists under the fleet root and no bytes were
frozen; LOCAL-POLICY under a policy-local prefix with frozen bytes; MOVED to the first path at --rev with the
token's last component, the token's round and the frozen digest; TOKEN to every path at --rev that starts with the
stripped token; QUARANTINED to the first lane-disk path under .ufo/quarantine/<seg>/ ending in the token's
directory; ABSENT otherwise. Its score under census/round-78/c2-pointer-counter.py is the ceiling a ledger reaches
with no capture. Usage: c2-mechanical-ledger.py --root LANE --rev REV --fleet-root FLEET --population TSV --out TSV
"""
import argparse
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("c2r78", os.path.join(HERE, "c2-pointer-counter.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def main(argv):
    ap = argparse.ArgumentParser()
    for a in ("--root", "--rev", "--fleet-root", "--population", "--out"):
        ap.add_argument(a, required=True)
    ns = ap.parse_args(argv)
    root, fleet = os.path.abspath(ns.root), os.path.abspath(ns.fleet_root)
    paths = C.git(root, "ls-tree", "-r", "-t", "--name-only", ns.rev).stdout.decode().split("\n")
    with open(ns.population, encoding="utf-8") as f:
        pop = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    out = ["# mechanical ledger (control K-b): existence tests only, no capture"]
    for iid, _file, _line, token, frozen in pop:
        frozen = None if frozen == "-" else frozen
        base = os.path.basename(token.rstrip("/"))
        kr = C.ROUND.search(token)
        cls, tgt = "ABSENT", "-"
        if frozen is None and token.startswith(".ufo/") and os.path.lexists(os.path.join(fleet, token)):
            cls = "FLEET"
        elif frozen is not None and token.startswith(C.POLICY_LOCAL):
            cls = "LOCAL-POLICY"
        elif frozen is not None:
            for p in paths:
                tr = C.ROUND.search(p)
                if (os.path.basename(p) == base and (not kr or (tr and tr.group(1) == kr.group(1)))
                        and C.rev_digest(root, ns.rev, p) == frozen):
                    cls, tgt = "MOVED", p
                    break
        elif token[-1] in ">\\-" or ".." in base:
            stem = token.rstrip(">\\")
            hits = [p for p in paths if p.startswith(stem)]
            if hits:
                cls, tgt = "TOKEN", ";".join(hits)
        else:
            qroot = os.path.join(root, ".ufo", "quarantine")
            if os.path.isdir(qroot):
                for seg in sorted(os.listdir(qroot)):
                    d = os.path.join(qroot, seg, os.path.dirname(token))
                    if os.path.isdir(d) and os.listdir(d):
                        cls = "QUARANTINED"
                        tgt = os.path.relpath(os.path.join(d, sorted(os.listdir(d))[0]), root)
                        break
        out.append(f"{iid}\t{cls}\t{tgt}\tmechanical")
    with open(ns.out, "w", encoding="utf-8") as o:
        o.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
