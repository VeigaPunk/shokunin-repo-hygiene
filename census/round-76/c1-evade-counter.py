#!/usr/bin/env python3
"""souji r76 C1 counter: the pre-report gate's `check-clean` verdict against a frozen expected verdict per
route, over the r75 population (25 routes, imported byte-bound from census/round-75/c1-evade-counter.py)
plus five r76 ignore-source routes defined here.

r76 ruling (the claim): an untracked path may be hidden only by a pattern whose source is a TRACKED
per-directory .gitignore (git-check-ignore(1) -v names each pattern's source file, S320). The r75 stated
limit f7-selfignore-dir (an untracked directory whose own untracked .gitignore ignores itself) is
therefore relabelled FAIL; the same shape under a committed rule naming the directory (the lane's .jj/
and .ruff_cache/ case) stays PASS.

Each route builds a fresh bare-origin + clone fixture under --work (census/round-74 evade-probe build()),
applies one mutation, runs `bash <gate-dir>/souji-pre-report-gate.sh` (the writer must sit beside it) and
reads `check-clean=`.

Output: one `ROW <id> expect=<E> clean=<C> rc=<n> match=<yes|no>` line per route, then
`SUMMARY rows=<N> mismatches=<M> errors=<E>`; exit 0 iff M == 0 and E == 0, 1 otherwise, 2 on usage.
"""
import argparse
import hashlib
import importlib.util
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
R75 = os.path.join(HERE, "..", "round-75", "c1-evade-counter.py")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


C75 = _load(R75, "souji_r75_c1_evade_counter")
P = C75.P
_write = C75._write


# ---------------------------------------------------------------- r76 ignore-source routes
def r_f9_selfignore_nested(c, w):
    """forgery: a new nested directory whose own untracked .gitignore (`*`) hides itself and a payload."""
    _write(os.path.join(c, "deep", "er", "cache", ".gitignore"), b"*\n")
    _write(os.path.join(c, "deep", "er", "cache", "payload.txt"), b"hidden payload\n")
    return {}


def r_f10_selfignore_named(c, w):
    """forgery: an untracked .gitignore naming itself and one payload by anchored path (no wildcard)."""
    _write(os.path.join(c, "pl", ".gitignore"), b"/.gitignore\n/payload.txt\n")
    _write(os.path.join(c, "pl", "payload.txt"), b"hidden payload\n")
    return {}


def r_f14_selfignore_in_tracked_dir(c, w):
    """forgery: an untracked self-ignoring .gitignore inside a tracked directory (sub/) hides a new file."""
    _write(os.path.join(c, "sub", ".gitignore"), b"/.gitignore\n/new.txt\n")
    _write(os.path.join(c, "sub", "new.txt"), b"hidden payload\n")
    return {}


def r_f11_committed_dir_rule(c, w):
    """honest: the .jj/ shape under declared policy -- a committed root rule `toolcache/` covers a tool
    directory that also carries its own untracked self-ignoring .gitignore."""
    _write(os.path.join(c, "toolcache", ".gitignore"), b"*\n")
    _write(os.path.join(c, "toolcache", "state.bin"), b"cache\n")
    return {}


def r_f12_committed_nested_gitignore(c, w):
    """honest: a committed sub/.gitignore rule (*.log) covers a new build log in sub/."""
    _write(os.path.join(c, "sub", "build.log"), b"log\n")
    return {}


R76_ROUTES = [
    ("f9-selfignore-nested", r_f9_selfignore_nested, None, None, None, ["deep/er/cache/payload.txt"]),
    ("f10-selfignore-named", r_f10_selfignore_named, None, None, None, ["pl/payload.txt"]),
    ("f14-selfignore-in-tracked-dir", r_f14_selfignore_in_tracked_dir, None, None, None, ["sub/new.txt"]),
    ("f11-committed-dir-rule", r_f11_committed_dir_rule, None, None, b"toolcache/\n", ["toolcache/state.bin"]),
    ("f12-committed-nested-gitignore", r_f12_committed_nested_gitignore, {"sub/.gitignore": b"*.log\n"},
     None, None, ["sub/build.log"]),
]

EXPECT = dict(C75.EXPECT)
# r76 ruling: relabelled from the r75 stated limit (PASS) -- the hiding rule's source is an untracked file.
EXPECT["f7-selfignore-dir"] = "FAIL"
EXPECT.update({
    "f9-selfignore-nested": "FAIL",
    "f10-selfignore-named": "FAIL",
    "f14-selfignore-in-tracked-dir": "FAIL",
    "f11-committed-dir-rule": "PASS",
    "f12-committed-nested-gitignore": "PASS",
})


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-dir", required=True, help="directory holding souji-pre-report-gate.sh and souji-receipt-write.py")
    ap.add_argument("--work", required=True, help="empty scratch directory (never under /tmp)")
    ns = ap.parse_args(argv)
    gate_dir = os.path.abspath(ns.gate_dir)
    gate = os.path.join(gate_dir, "souji-pre-report-gate.sh")
    writer = os.path.join(gate_dir, "souji-receipt-write.py")
    work = os.path.abspath(ns.work)
    if not (os.path.isfile(gate) and os.path.isfile(writer)):
        print(f"C1-COUNTER-FATAL: gate dir incomplete: {gate_dir}", file=sys.stderr)
        return 2
    pop = os.path.join(HERE, "c1-population.tsv")
    with open(pop, encoding="utf-8") as f:
        rows = [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]
    if dict((r[0], r[1]) for r in rows) != EXPECT or len(rows) != len(EXPECT):
        print("C1-COUNTER-FATAL: c1-population.tsv and the EXPECT table disagree", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C1-COUNTER-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C1-COUNTER-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    routes = list(P.ROUTES) + list(C75.R75_ROUTES) + R76_ROUTES
    ids = [r[0] for r in routes]
    if sorted(ids) != sorted(EXPECT) or len(set(ids)) != len(ids):
        print("C1-COUNTER-FATAL: route set and EXPECT table disagree", file=sys.stderr)
        return 2
    print(f"# gate path={gate} sha256={sha(gate)}")
    print(f"# writer path={writer} sha256={sha(writer)}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# r75 counter path={os.path.normpath(R75)} sha256={sha(R75)}")
    print(f"# counter sha256={sha(os.path.abspath(__file__))}")
    mism = errs = 0
    for rid, mut, seed, attrs, gi, paths in routes:
        o = P.run_route(gate, work, rid, mut, seed, attrs, gi, paths)
        clean = o.get("clean", "-")
        if o.get("error") or clean not in ("PASS", "FAIL"):
            errs += 1
            print(f"ROW {rid} expect={EXPECT[rid]} clean={clean} rc={o.get('rc')} match=error "
                  f"detail={o.get('error') or o.get('detail', '')[:200]}")
            continue
        ok = clean == EXPECT[rid]
        mism += 0 if ok else 1
        print(f"ROW {rid} expect={EXPECT[rid]} clean={clean} rc={o.get('rc')} match={'yes' if ok else 'no'}")
        if not ok:
            print(f"#  {rid} {o.get('detail', '')[:300]}")
    print(f"SUMMARY rows={len(routes)} mismatches={mism} errors={errs}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
