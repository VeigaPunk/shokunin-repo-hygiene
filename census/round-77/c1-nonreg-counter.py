#!/usr/bin/env python3
"""souji r77 C1 counter: the pre-report gate's `check-clean` verdict AND refusal class against a frozen
expectation per route, over 16 r77 routes (9 non-regular sources, 3 one-path forgeries, 4 positive controls) defined here.

Claim surface: tools/souji-pre-report-gate.sh check 4 (clean). git opens every exclude source with a plain
blocking open(2) and checks the file type only afterwards (S321 git dir.c add_patterns at v2.56.0; S064
attr.c for attributes; S062 fifo(7): opening a FIFO blocks until the other end opens). A FIFO named as a
per-directory .gitignore/.gitattributes, as $GIT_DIR/info/exclude or info/attributes, or as
core.excludesFile/core.attributesFile therefore blocks the gate forever (S76Sentinel MEDIUM-2). The rows
also carry one-path forgeries (r76 lesson M2: S76MutGate M09, a gate refusing only above one undeclared
path, passes every frozen r76 row) and positive controls, so a gate that refuses everything is not a gain.

Each route builds a fresh bare-origin + clone fixture under --work (census/round-74 evade-probe build(),
imported byte-bound), applies one mutation, and runs `bash <gate-dir>/souji-pre-report-gate.sh` in its OWN
session with a ROW_TIMEOUT-second bound; on expiry the whole process group is killed (SIGKILL) and the row
reads clean=HANG (a plain subprocess timeout would wait forever on the grandchild git holding the pipes).

A row matches iff clean == expected verdict AND, for a FAIL row with a class, the class token appears in
the gate's `detail-clean:` line. Output: one `ROW <id> expect=<E>/<class> clean=<C> class=<seen> rc=<n>
secs=<t> match=<yes|no>` line per route, then `SUMMARY rows=<N> mismatches=<M> errors=<E> hangs=<H>`;
exit 0 iff M == 0 and E == 0, 1 otherwise, 2 on usage.
"""
import argparse
import hashlib
import importlib.util
import os
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "..", "round-74", "records", "wave-repair", "probes", "evade-probe.py")
ROW_TIMEOUT = 30
NONREG = "RECEIPT-NONREGULAR-SOURCE"
LOCAL = "RECEIPT-UNTRACKED-LOCAL-EXCLUDE"
UNDECL = "RECEIPT-UNTRACKED-UNDECLARED-IGNORE"
PINNED = "pinned git status"  # the writer's own pinned status lists the hidden path first (base behaviour)


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = _load(PROBE, "souji_r74_evade_probe")


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def _fifo(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.lexists(path):
        os.unlink(path)
    os.mkfifo(path)


# ---------------------------------------------------------------- non-regular exclude/attribute sources
def r_n1(c, w):
    """FIFO .gitignore inside a new untracked directory."""
    _fifo(os.path.join(c, "nd", ".gitignore"))
    _write(os.path.join(c, "nd", "x.txt"), b"untracked\n")


def r_n2(c, w):
    """FIFO .gitignore inside the tracked directory sub/."""
    _fifo(os.path.join(c, "sub", ".gitignore"))


def r_n3(c, w):
    """$GIT_DIR/info/exclude replaced by a FIFO."""
    _fifo(os.path.join(c, ".git", "info", "exclude"))


def r_n4(c, w):
    """repository-local core.excludesFile names a FIFO outside the work tree."""
    xf = os.path.join(w, "xf")
    _fifo(xf)
    P.git(c, "config", "core.excludesFile", xf)


def r_n5(c, w):
    """FIFO .gitattributes inside the tracked directory sub/."""
    _fifo(os.path.join(c, "sub", ".gitattributes"))


def r_n6(c, w):
    """$GIT_DIR/info/attributes is a FIFO."""
    _fifo(os.path.join(c, ".git", "info", "attributes"))


def r_n7(c, w):
    """repository-local core.attributesFile names a FIFO outside the work tree."""
    af = os.path.join(w, "af")
    _fifo(af)
    P.git(c, "config", "core.attributesFile", af)


def r_n8(c, w):
    """FIFO .gitignore inside a directory a tracked rule ignores (ruled FAIL: the gate fails closed and
    does not model whether git descends)."""
    _fifo(os.path.join(c, "cache", ".gitignore"))


def r_n10(c, w):
    """$GIT_DIR/info/exclude is a symlink to a FIFO outside the work tree."""
    tgt = os.path.join(w, "xf-target")
    _fifo(tgt)
    ex = os.path.join(c, ".git", "info", "exclude")
    if os.path.lexists(ex):
        os.unlink(ex)
    os.symlink(tgt, ex)


# ---------------------------------------------------------------- one-path forgeries (kill M09)
def r_o1(c, w):
    """$GIT_DIR/info/exclude hides exactly one new untracked file."""
    with open(os.path.join(c, ".git", "info", "exclude"), "a", encoding="utf-8") as f:
        f.write("/one.txt\n")
    _write(os.path.join(c, "one.txt"), b"hidden payload\n")


def r_o2(c, w):
    """an untracked .gitignore that ignores only itself (one undeclared path)."""
    _write(os.path.join(c, "pl", ".gitignore"), b"/.gitignore\n")


def r_o3(c, w):
    """a regular repository-local core.excludesFile hides exactly one new untracked file."""
    xf = os.path.join(w, "xf-regular")
    _write(xf, b"/one.txt\n")
    P.git(c, "config", "core.excludesFile", xf)
    _write(os.path.join(c, "one.txt"), b"hidden payload\n")


# ---------------------------------------------------------------- positive controls
def r_p1(c, w):
    """honest: nothing changed after the push."""


def r_p2(c, w):
    """honest: a regular core.excludesFile whose one pattern matches nothing present."""
    xf = os.path.join(w, "xf-nomatch")
    _write(xf, b"/never-present.bin\n")
    P.git(c, "config", "core.excludesFile", xf)


def r_p3(c, w):
    """honest: a FIFO that is not an exclude/attribute source, under a directory a tracked rule ignores."""
    _fifo(os.path.join(c, "cache", "pipe"))


def r_p4(c, w):
    """honest: a regular untracked self-ignoring .gitignore under a tracked rule naming its directory."""
    _write(os.path.join(c, "toolcache", ".gitignore"), b"*\n")
    _write(os.path.join(c, "toolcache", "state.bin"), b"cache\n")


ROUTES = [
    # id, mutate, tracked .gitignore bytes, expected verdict, expected class
    ("n1-fifo-gitignore-newdir", r_n1, None, "FAIL", NONREG),
    ("n2-fifo-gitignore-tracked-dir", r_n2, None, "FAIL", NONREG),
    ("n3-fifo-info-exclude", r_n3, None, "FAIL", NONREG),
    ("n4-fifo-excludesfile", r_n4, None, "FAIL", NONREG),
    ("n5-fifo-gitattributes", r_n5, None, "FAIL", NONREG),
    ("n6-fifo-info-attributes", r_n6, None, "FAIL", NONREG),
    ("n7-fifo-attributesfile", r_n7, None, "FAIL", NONREG),
    ("n8-fifo-gitignore-declared-dir", r_n8, b"cache/\n", "FAIL", NONREG),
    ("n10-symlink-info-exclude-to-fifo", r_n10, None, "FAIL", NONREG),
    ("o1-one-path-info-exclude", r_o1, None, "FAIL", LOCAL),
    ("o2-one-path-selfignore", r_o2, None, "FAIL", UNDECL),
    ("o3-one-path-excludesfile", r_o3, None, "FAIL", PINNED),
    ("p1-honest", r_p1, None, "PASS", "-"),
    ("p2-regular-excludesfile-nomatch", r_p2, None, "PASS", "-"),
    ("p3-fifo-not-a-source-declared-dir", r_p3, b"cache/\n", "PASS", "-"),
    ("p4-regular-selfignore-declared-dir", r_p4, b"toolcache/\n", "PASS", "-"),
]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_gate(gate, clone, report, prereg):
    env = P.env_clean()
    t0 = time.monotonic()
    p = subprocess.Popen(["bash", gate, "--lane", clone, "--branch", "master", "--report", report,
                          "--prereg", prereg], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, env=env, start_new_session=True)
    try:
        out, err = p.communicate(timeout=ROW_TIMEOUT)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
        return None, "HANG", "", time.monotonic() - t0
    text = out.decode("utf-8", "replace") + err.decode("utf-8", "replace")
    clean = next((l.split("=", 1)[1] for l in text.splitlines() if l.startswith("check-clean=")), "-")
    detail = " | ".join(l for l in text.splitlines() if l.startswith("detail-clean"))
    return p.returncode, clean, detail, time.monotonic() - t0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-dir", required=True,
                    help="directory holding souji-pre-report-gate.sh and souji-receipt-write.py")
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
    want = {r[0]: (r[3], r[4]) for r in ROUTES}
    if len(rows) != len(want) or {r[0]: (r[1], r[2]) for r in rows} != want:
        print("C1-COUNTER-FATAL: c1-population.tsv and the ROUTES table disagree", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("C1-COUNTER-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"C1-COUNTER-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    print(f"# gate path={gate} sha256={sha(gate)}")
    print(f"# writer path={writer} sha256={sha(writer)}")
    print(f"# population path={pop} sha256={sha(pop)}")
    print(f"# probe path={os.path.normpath(PROBE)} sha256={sha(PROBE)}")
    print(f"# counter sha256={sha(os.path.abspath(__file__))} row_timeout={ROW_TIMEOUT}s")
    mism = errs = hangs = 0
    for rid, mut, gi, ev, ecls in ROUTES:
        rowdir = os.path.join(work, rid)
        try:
            clone, report, prereg = P.build(rowdir, gitignore=gi)
            mut(clone, rowdir)
        except (P.FixtureError, OSError, subprocess.SubprocessError) as exc:
            errs += 1
            print(f"ROW {rid} expect={ev}/{ecls} clean=- class=- rc=- secs=- match=error "
                  f"detail={type(exc).__name__}: {str(exc)[:200]}")
            continue
        rc, clean, detail, secs = run_gate(gate, clone, report, prereg)
        hangs += clean == "HANG"
        seen = next((k for k in (NONREG, LOCAL, UNDECL, PINNED) if k in detail), "-").replace(" ", "-")
        ok = clean == ev and (ecls == "-" or ecls in detail)
        mism += 0 if ok else 1
        print(f"ROW {rid} expect={ev}/{ecls} clean={clean} class={seen} rc={rc} secs={secs:.1f} "
              f"match={'yes' if ok else 'no'}")
        if not ok:
            print(f"#  {rid} {detail[:300]}")
    print(f"SUMMARY rows={len(ROUTES)} mismatches={mism} errors={errs} hangs={hangs}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
