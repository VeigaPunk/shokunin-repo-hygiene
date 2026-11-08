#!/usr/bin/env python3
"""S87ExecC1 by-hand driver: drives the filed counter (and single-edit mutants of it) on the harness's OWN fixture
clone, one forged row at a time, without the harness's pass/fail scaffold. Only build_fixture and the POPS table are
imported from census/round-87/c1-false-row-harness.py, so the cells below are the counter's own FORGE/ITEM output.

  matrix  --rows TQ1,NE1          one cell per (row, counter variant) for the named rows
  scan    --population FILE --mutant ID   every row of that population against one counter variant

Every cell prints `CELL row=<id> variant=<v> expect=<got>/<rc> forge=<expect-cell> got=<S> rc=<n> match=<yes|no>`
plus the counter's own ITEM line for the driven item (so `why` is the counter's, not this script's).

stdlib only; writes only under --work (empty or absent, never /tmp).
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
HARNESS = os.path.join(LANE, "census/round-87/c1-false-row-harness.py")
COUNTER = os.path.join(LANE, "census/round-87/c1-pointer-counter.py")
MUTANTS = os.path.join(LANE, "census/round-87/c1-mutants.json")


def load_harness():
    spec = importlib.util.spec_from_file_location("c1hrn", HARNESS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows_of(path):
    with open(path, encoding="utf-8") as f:
        return [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]


def variants(mutant_ids):
    """[(label, counter_path, workdir_or_None)]; None means 'write this mutant under --work'."""
    out = [("pristine", COUNTER, None)]
    src = open(COUNTER, encoding="utf-8").read()
    mem = {m["id"]: m for m in json.load(open(MUTANTS, encoding="utf-8"))["members"]}
    for mid in mutant_ids:
        if mid not in mem:
            raise SystemExit(f"unknown mutant {mid!r}; have {sorted(mem)}")
        m = mem[mid]
        n = src.count(m["old"])
        if n != 1:
            raise SystemExit(f"edit {mid} occurs {n} times, need exactly 1")
        out.append((mid, None, src.replace(m["old"], m["new"])))
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("matrix", "scan"))
    ap.add_argument("--work", required=True)
    ap.add_argument("--fixture", default=None, help="reuse an existing fixture dir (matrix only)")
    ap.add_argument("--rows", default="TQ1,NE1")
    ap.add_argument("--population", default=os.path.join(LANE, "census/round-87/c1-false-rows.tsv"))
    ap.add_argument("--mutant", default="m16-nf6b-punct")
    ap.add_argument("--mutants", default=None, help="comma list; default: all ten")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        raise SystemExit("--work under /tmp is refused")
    os.makedirs(work, exist_ok=True)

    hrn = load_harness()
    print(f"# driver=byhand-matrix.py harness={HARNESS} sha256={hashlib.sha256(open(HARNESS,'rb').read()).hexdigest()}")
    print(f"# counter={COUNTER} sha256={hashlib.sha256(open(COUNTER,'rb').read()).hexdigest()}")
    print(f"# mutants={MUTANTS} sha256={hashlib.sha256(open(MUTANTS,'rb').read()).hexdigest()}")

    if ns.fixture:
        fx = os.path.abspath(ns.fixture)
        revs = json.load(open(os.path.join(fx, "..", "revs.json")))
    else:
        fx, revs = hrn.build_fixture(LANE, work)
        with open(os.path.join(work, "revs.json"), "w") as f:
            json.dump(revs, f)
        print("# fixture " + " ".join(f"{k}={v}" for k, v in revs.items()))
    print(f"# fixture toplevel={hrn.git(fx, 'rev-parse', '--show-toplevel')}")

    if ns.mode == "matrix":
        want = [x for x in ns.rows.split(",") if x]
        pop = rows_of(ns.population)
        by = {r[0]: r for r in pop}
        sel = [by[x] for x in want]
        mids = [x for x in (ns.mutants.split(",") if ns.mutants else
                            [m["id"] for m in json.load(open(MUTANTS, encoding="utf-8"))["members"]]) if x]
        vs = variants(mids)
    else:
        mid = ns.mutant
        vs = variants([] if mid == "pristine" else [mid])
        sel = rows_of(ns.population)

    paths = {}
    for label, cpath, newtext in vs:
        if newtext is not None:
            cpath = os.path.join(work, "mut", label + ".py")
            os.makedirs(os.path.dirname(cpath), exist_ok=True)
            with open(cpath, "w", encoding="utf-8") as f:
                f.write(newtext)
        paths[label] = cpath

    cells = []
    for label, _, _ in vs:
        counter = paths[label]
        for r in sel:
            rid, where, rlabel, popl, item, cls, target, exp_got, exp_rc, _src = r
            root, rev = (LANE, hrn.BASE) if where == "lane" else (fx, revs[rlabel])
            pfile, lfile = hrn.POPS[popl]
            forge = os.path.join(work, f"forge-{label}-{rid}.tsv")
            cell = "ERROR" if exp_got == "ERROR" else ("MISMATCH" if exp_rc != "-" else "REFUSED")
            with open(forge, "w", encoding="utf-8") as f:
                f.write(f"{rid}\t{item}\t{cls}\t{target}\t{cell}\n")
            p = subprocess.run([sys.executable, "-B", counter, "--root", root, "--rev", rev,
                                "--fleet-root", FLEET, "--population", os.path.join(LANE, pfile),
                                "--ledger", os.path.join(LANE, lfile), "--forge", forge],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=LANE)
            out = p.stdout.decode("utf-8", "replace")
            m = re.search(rf"^FORGE {re.escape(rid)} item={re.escape(item)} .*?got=(\S+)", out, re.M)
            it = re.search(rf"^ITEM {re.escape(item)} .*$", out, re.M)
            got = m.group(1) if m else "-"
            ok = bool(m) and got == exp_got and (exp_rc == "-" or p.returncode == int(exp_rc))
            line = (f"CELL row={rid} variant={label} expect={exp_got}/{exp_rc} forge={cell} got={got} rc={p.returncode} "
                    f"match={'yes' if ok else 'no'} | {(it.group(0) if it else 'no ITEM line')}"
                    + (f" | stderr={p.stderr.decode()[:160]!r}" if not m else ""))
            print(line)
            cells.append((rid, label, ok))
    print(f"# cells={len(cells)} mismatch={sum(1 for c in cells if not c[2])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
