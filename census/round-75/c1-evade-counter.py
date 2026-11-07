#!/usr/bin/env python3
"""souji r75 C1 counter: the pre-report gate's `check-clean` verdict against a frozen expected verdict per
route (not against a bytes-only truth, which mislabels two r74 routes: S74 routed defect 2).

Population: the 20 r74 evasion routes (imported, byte-bound, from
census/round-74/records/wave-repair/probes/evade-probe.py) plus five r75 ignore-surface routes defined here.
Each route builds a fresh bare-origin + clone fixture under --work, applies one mutation, runs
`bash <gate-dir>/souji-pre-report-gate.sh` (the writer must sit beside it) and reads `check-clean=`.

Expected verdicts (frozen; the ruling for each relabelled r74 route is the line's comment):
  FAIL = the tree carries a lane change the gate must refuse; PASS = an honest tree the gate must accept.

Output: one `ROW <id> expect=<E> clean=<C> rc=<n> match=<yes|no>` line per route, then
`SUMMARY rows=<N> mismatches=<M> errors=<E>`; exit 0 iff M == 0 and E == 0, 1 otherwise, 2 on usage.
The gate and writer sha256 and the gate path are printed so the receipt binds what ran (S74MutGate F2/F3).
"""
import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "..", "round-74", "records", "wave-repair", "probes", "evade-probe.py")


def load_probe():
    spec = importlib.util.spec_from_file_location("souji_r74_evade_probe", PROBE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = load_probe()


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


# ---------------------------------------------------------------- r75 ignore-surface routes
def r_f3_repo_excludesfile(c, w):
    """repository-local core.excludesFile names a file that hides a new untracked file."""
    ex = os.path.join(w, "hide.txt")
    _write(ex, b"new.txt\n")
    P.git(c, "config", "core.excludesFile", ex)
    _write(os.path.join(c, "new.txt"), b"untracked\n")
    return {}


def r_f5_info_exclude_dir(c, w):
    """$GIT_DIR/info/exclude hides a whole new directory."""
    with open(os.path.join(c, ".git", "info", "exclude"), "a", encoding="utf-8") as f:
        f.write("newdir/\n")
    _write(os.path.join(c, "newdir", "x.txt"), b"untracked\n")
    return {}


def r_f6_committed_pyc(c, w):
    """honest: a committed .gitignore rule (*.pyc) covers a new build artifact."""
    _write(os.path.join(c, "sub", "mod.pyc"), b"\x00bytecode\n")
    return {}


def r_f7_selfignore_dir(c, w):
    """honest by mechanism: a tool directory that ignores itself (the .jj/.gitignore and
    .ruff_cache/.gitignore shape the lane itself carries). A stated limit: the same mechanism hides a
    forger's new directory; the gate cannot tell the two apart, so the honest label binds."""
    _write(os.path.join(c, "toolcache", ".gitignore"), b"*\n")
    _write(os.path.join(c, "toolcache", "state.bin"), b"cache\n")
    return {}


def r_f8_info_exclude_honest_empty(c, w):
    """honest: info/exclude carries a pattern that matches nothing in the tree."""
    with open(os.path.join(c, ".git", "info", "exclude"), "a", encoding="utf-8") as f:
        f.write("nothing-here.txt\n")
    return {}


R75_ROUTES = [
    ("f3-repo-excludesfile", r_f3_repo_excludesfile, None, None, None, ["new.txt"]),
    ("f5-info-exclude-dir", r_f5_info_exclude_dir, None, None, None, ["newdir/x.txt"]),
    ("f6-committed-pyc", r_f6_committed_pyc, None, None, b"*.pyc\n", ["sub/mod.pyc"]),
    ("f7-selfignore-dir", r_f7_selfignore_dir, None, None, None, ["toolcache/state.bin"]),
    ("f8-info-exclude-unmatched", r_f8_info_exclude_honest_empty, None, None, None, ["a.txt"]),
]

EXPECT = {
    "ctl-honest": "PASS",
    "ctl-gd1": "FAIL",
    "a-v4-forge": "FAIL",
    "b-split-forge": "FAIL",
    "b2-split-linked": "FAIL",
    # r74 probe label OVER-REFUSAL; ruling r75: an executable-bit change is a lane change git records
    # (the index mode is part of the tree), whatever core.fileMode the clone sets.
    "n-filemode-config": "FAIL",
    "c-assume-unchanged": "FAIL",
    "c2-skip-worktree": "FAIL",
    "d-fsmonitor-empty": "FAIL",
    "e-checkstat-minimal": "FAIL",
    # hidden only by $GIT_DIR/info/exclude (a local, unversioned rule; gitignore(5)).
    "f-info-exclude": "FAIL",
    # r74 probe label FORGERY; ruling r75: the hiding rule is a committed .gitignore line, the lane's
    # declared policy for untracked artifacts (same mechanism as the lane's own __pycache__/ rule).
    "f2-gitignore": "PASS",
    "g-fifo": "FAIL",
    "g2-symlink-dev-zero": "FAIL",
    "h-envconfig-filter": "FAIL",
    "h2-envconfig-filter-infoattrs": "FAIL",
    "h3-repo-filter": "FAIL",
    "i-ident": "FAIL",
    "k-gitlink-mode": "FAIL",
    "l-core-worktree": "FAIL",
    "f3-repo-excludesfile": "FAIL",
    "f5-info-exclude-dir": "FAIL",
    "f6-committed-pyc": "PASS",
    "f7-selfignore-dir": "PASS",
    "f8-info-exclude-unmatched": "PASS",
}


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
    routes = list(P.ROUTES) + R75_ROUTES
    ids = [r[0] for r in routes]
    if sorted(ids) != sorted(EXPECT) or len(set(ids)) != len(ids):
        print("C1-COUNTER-FATAL: route set and EXPECT table disagree", file=sys.stderr)
        return 2
    print(f"# gate path={gate} sha256={sha(gate)}")
    print(f"# writer path={writer} sha256={sha(writer)}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# probe path={os.path.normpath(PROBE)} sha256={sha(PROBE)}")
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
