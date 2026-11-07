#!/usr/bin/env python3
"""souji r78 C2 control harness: run the FROZEN r77 counter (census/round-77/c2-pointer-counter.py, unchanged)
once per forged row of census/round-78/c2-forge-r77.tsv. Each run uses the r77 shipped ledger with that one
item's row replaced by the forged row (written under --work), and reads the item's status from the r77
counter's ITEM line. Output: `FORGE <fid> item=<id> class=<C> expect=<E> got=<S> match=<yes|no>` per row and
`FORGE-SUMMARY forged=<N> matched=<K> accepted=<A>`; exit 0 iff every row matches, 1 otherwise, 2 on usage.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--fleet-root", required=True)
    ap.add_argument("--work", required=True, help="empty scratch directory (never under /tmp)")
    ap.add_argument("--counter", default=os.path.join(HERE, "..", "round-77", "c2-pointer-counter.py"))
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")) or (
            os.path.exists(work) and os.listdir(work)):
        print("FORGE-LEGACY-FATAL: --work must be an empty directory outside /tmp", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    ledger = os.path.join(HERE, "..", "round-77", "c2-pointer-ledger.tsv")
    forge = os.path.join(HERE, "c2-forge-r77.tsv")
    for label, p in (("counter", ns.counter), ("ledger", ledger), ("forge", forge)):
        with open(p, "rb") as f:
            print(f"# {label} path={os.path.normpath(p)} sha256={hashlib.sha256(f.read()).hexdigest()}")
    with open(ledger, encoding="utf-8") as f:
        base_lines = f.read().split("\n")
    forged = matched = accepted = 0
    with open(forge, encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    for fid, iid, cls, target, expect in rows:
        lines = [l for l in base_lines if not l.startswith(iid + "\t")]
        lines.insert(1, f"{iid}\t{cls}\t{target}\tforged {fid}")
        lp = os.path.join(work, f"ledger-{fid}.tsv")
        with open(lp, "w", encoding="utf-8") as o:
            o.write("\n".join(lines))
        p = subprocess.run([sys.executable, "-B", ns.counter, "--root", ns.root, "--rev", ns.rev,
                            "--fleet-root", ns.fleet_root, "--ledger", lp], stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True)
        m = re.search(r"^ITEM " + re.escape(iid) + r" \S+ status=(\S+)", p.stdout, re.M)
        got = m.group(1) if m else "NO-ITEM-LINE"
        forged += 1
        hit = got == expect
        matched += hit
        accepted += got not in ("REFUSED", "MISMATCH", "UNRESOLVED", "ERROR", "NO-ITEM-LINE")
        print(f"FORGE {fid} item={iid} class={cls} expect={expect} got={got} match={'yes' if hit else 'no'}")
    print(f"FORGE-SUMMARY forged={forged} matched={matched} accepted={accepted}")
    return 0 if forged and matched == forged else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
