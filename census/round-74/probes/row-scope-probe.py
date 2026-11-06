#!/usr/bin/env python3
"""souji r74 pre-freeze feasibility probe (QUALITY Q70) for the C2 row-specific witness.

Imports a counter file (pristine or with one frozen edit applied) and, for each named row, rebuilds the
row's BASE-slot fixture with the counter's own builders, reads the counter's own tree_divergence before
the slot, runs the slot exactly as evaluate() does (same root/instrument/env/cwd rules) and reads it
again after. Prints every (path, kind) divergence at both points, then whether any divergence touches
the row's FORGED path set given on the command line (--forged ROW=path[,path]).

  ROW <id> verdict=<accept|refuse|error> pre=[...] post=[...] tree_witness=<yes|no> forged_paths=[...] row_witness=<yes|no>

Usage: row-scope-probe.py --counter <c1-counter.py> --slot <writer.py> --work <scratch> --rows FWw,FC1
         --forged FWw=tools/counter.py --forged FC1=tools/counter.py"""
import argparse
import importlib.util
import os
import shutil
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--slot", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--forged", action="append", default=[])
    ns = ap.parse_args()
    spec = importlib.util.spec_from_file_location("c1counter", os.path.abspath(ns.counter))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    forged = {}
    for f in ns.forged:
        row, _, paths = f.partition("=")
        forged[row] = paths.split(",")
    work = os.path.abspath(ns.work)
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    slot = os.path.abspath(ns.slot)
    try:
        for letter in ns.rows.split(","):
            s = m.CASE_SPECS[letter]
            repo, rev = m.build_case(work, letter, "base", s)
            rootsub = s.get("rootsub")
            root = os.path.join(repo, rootsub) if rootsub else repo
            instrument = "instr.sh" if rootsub else "tools/instr.sh"
            cwd = (os.path.dirname(repo) if s.get("cwd_parent")
                   else os.path.join(repo, ".git") if s.get("cwd_gitdir") else None)
            if s.get("cwd_parent"):
                instrument = "instr.sh"
            out = os.path.join(work, letter, "base", "out", "receipt.txt")
            pre = m.tree_divergence(repo, rev)
            rc, _, se = m.run_slot(slot, repo, rev, out, bool(s.get("allow_dirty")), m.wrapped_argv(s, repo),
                                   root=root, instrument=instrument, env_extra=m.case_env(s, repo), cwd=cwd)
            post = m.tree_divergence(repo, rev)
            v = m.judge(rc, out)
            fp = forged.get(letter, [])
            row_wit = any(p in fp for p, _ in pre + post)
            print(f"ROW {letter} verdict={v} pre={pre} post={post} tree_witness={'yes' if (pre or post) else 'no'} "
                  f"forged_paths={fp} row_witness={'yes' if row_wit else 'no'}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("EXIT=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
