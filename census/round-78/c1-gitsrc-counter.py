#!/usr/bin/env python3
"""souji r78 C1 counter: the pre-report gate's exit code AND refusal class against a frozen expectation per
route, over the r78 routes defined here (11 non-regular git configuration/ref sources read before check 4,
1 blocking remote, 5 positive controls).

Claim surface: tools/souji-pre-report-gate.sh checks 1-3 (tip, report, shonen) and the git calls check 4 makes
before its r77 source pre-check. Every git command first discovers the repository: it reads $GIT_DIR/HEAD,
$GIT_DIR/commondir (S324 git setup.c get_common_dir_noenv: file_exists() then strbuf_read_file(), a blocking
open), and the config files with every include.path / includeIf.*.path they name (S323 git config.adoc
"Includes": "The contents of the included file are inserted immediately"). A FIFO at any of those paths
blocks the gate's FIRST git call (check 1, `rev-parse`) forever, before the r77 pre-check of check 4 can run
(r77 lesson Wave: S77ExecEvade, S77Sentinel MEDIUM-2). `ls-remote origin` additionally runs upload-pack in
the remote repository, whose own config the gate cannot pre-check: it must be time-bounded.

Each route builds a fresh bare-origin + clone fixture under --work (census/round-74 evade-probe build(),
imported byte-bound), applies one mutation, and runs `bash <gate-dir>/souji-pre-report-gate.sh` in its OWN
session with a ROW_TIMEOUT-second bound; on expiry the whole process group is killed (SIGKILL) and the row
reads verdict=HANG. Some routes add HOME / XDG_CONFIG_HOME to the gate's environment (the gate inherits
both from its caller and git reads $HOME/.gitconfig and $XDG_CONFIG_HOME/git/config).

A row matches iff verdict == expected verdict (PASS: exit 0 and no `check-*=FAIL` line; FAIL: exit 1 and at
least one `check-*=FAIL` line) AND, for a FAIL row, the expected class token appears in the gate's output.
Output: one `ROW <id> expect=<E>/<class> verdict=<V> class=<seen> rc=<n> secs=<t> match=<yes|no>` line per
route, then `SUMMARY rows=<N> mismatches=<M> errors=<E> hangs=<H>`; exit 0 iff M == 0 and E == 0, 1
otherwise, 2 on usage.
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
ROW_TIMEOUT = 75
GITSRC = "RECEIPT-NONREGULAR-GITSOURCE"
GITTIME = "RECEIPT-GIT-TIMEOUT"
CLASSES = (GITSRC, GITTIME, "RECEIPT-NONREGULAR-SOURCE")


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


def _cfg(c, *args):
    P.git(c, "config", *args)


# ---------------------------------------------------------------- non-regular sources read at discovery
def r_g1(c, w):
    """$GIT_DIR/config is a FIFO."""
    _fifo(os.path.join(c, ".git", "config"))


def r_g2(c, w):
    """$GIT_DIR/HEAD is a FIFO."""
    _fifo(os.path.join(c, ".git", "HEAD"))


def r_g3(c, w):
    """refs packed, $GIT_DIR/packed-refs replaced by a FIFO."""
    P.git(c, "pack-refs", "--all", "--prune")
    _fifo(os.path.join(c, ".git", "packed-refs"))


def r_g4(c, w):
    """$GIT_DIR/commondir is a FIFO."""
    _fifo(os.path.join(c, ".git", "commondir"))


def r_g5(c, w):
    """repository config include.path names a FIFO outside the work tree (absolute)."""
    f = os.path.join(w, "inc-fifo")
    _fifo(f)
    _cfg(c, "include.path", f)


def r_g6(c, w):
    """repository config includeIf.gitdir:<clone>/.path names a FIFO (condition true)."""
    f = os.path.join(w, "incif-fifo")
    _fifo(f)
    _cfg(c, "includeIf.gitdir:" + os.path.realpath(c) + "/.path", f)


def r_g7(c, w):
    """include.path names a regular file whose own include.path (relative) names a FIFO."""
    mid = os.path.join(w, "inc", "mid.cfg")
    _write(mid, b"[include]\n\tpath = deep-fifo\n")
    _fifo(os.path.join(w, "inc", "deep-fifo"))
    _cfg(c, "include.path", mid)


def r_g8(c, w):
    """extensions.worktreeConfig enabled; $GIT_DIR/config.worktree is a FIFO."""
    _cfg(c, "core.repositoryformatversion", "1")
    _cfg(c, "extensions.worktreeConfig", "true")
    _fifo(os.path.join(c, ".git", "config.worktree"))


def r_g9(c, w):
    """the caller's HOME holds a FIFO .gitconfig."""
    _fifo(os.path.join(w, "home", ".gitconfig"))


def r_g10(c, w):
    """the caller's XDG_CONFIG_HOME holds a FIFO git/config."""
    _fifo(os.path.join(w, "xdg", "git", "config"))


def r_g11(c, w):
    """$GIT_DIR/config is a symlink to a FIFO outside the work tree."""
    src = os.path.join(c, ".git", "config")
    keep = os.path.join(w, "config-copy")
    with open(src, "rb") as f:
        data = f.read()
    _write(keep, data)
    tgt = os.path.join(w, "config-fifo")
    _fifo(tgt)
    os.unlink(src)
    os.symlink(tgt, src)


# ---------------------------------------------------------------- a remote that blocks (time bound)
def r_t1(c, w):
    """the origin repository's own config is a FIFO (ls-remote runs upload-pack there)."""
    _fifo(os.path.join(w, "origin.git", "config"))


# ---------------------------------------------------------------- positive controls
def r_q1(c, w):
    """honest: nothing changed after the push."""


def r_q2(c, w):
    """honest: include.path names a regular file."""
    f = os.path.join(w, "inc-regular.cfg")
    _write(f, b"[user]\n\tname = include-check\n")
    _cfg(c, "include.path", f)


def r_q3(c, w):
    """honest: include.path names a missing file (git skips it)."""
    _cfg(c, "include.path", os.path.join(w, "never-there.cfg"))


def r_q4(c, w):
    """honest: a FIFO under $GIT_DIR that git never reads at discovery (hooks/pipe)."""
    _fifo(os.path.join(c, ".git", "hooks", "pipe"))


def r_q5(c, w):
    """honest: the caller's HOME holds a regular .gitconfig and XDG_CONFIG_HOME a regular git/config."""
    _write(os.path.join(w, "home", ".gitconfig"), b"[user]\n\tname = home-check\n")
    _write(os.path.join(w, "xdg", "git", "config"), b"[user]\n\temail = xdg@check\n")


HOMEENV = "home"
XDGENV = "xdg"
ROUTES = [
    # id, mutate, extra env keys, expected verdict, expected class
    ("g1-fifo-config", r_g1, (), "FAIL", GITSRC),
    ("g2-fifo-head", r_g2, (), "FAIL", GITSRC),
    ("g3-fifo-packed-refs", r_g3, (), "FAIL", GITSRC),
    ("g4-fifo-commondir", r_g4, (), "FAIL", GITSRC),
    ("g5-fifo-include-path", r_g5, (), "FAIL", GITSRC),
    ("g6-fifo-includeif-gitdir", r_g6, (), "FAIL", GITSRC),
    ("g7-fifo-nested-relative-include", r_g7, (), "FAIL", GITSRC),
    ("g8-fifo-config-worktree", r_g8, (), "FAIL", GITSRC),
    ("g9-fifo-home-gitconfig", r_g9, (HOMEENV,), "FAIL", GITSRC),
    ("g10-fifo-xdg-git-config", r_g10, (XDGENV,), "FAIL", GITSRC),
    ("g11-symlink-config-to-fifo", r_g11, (), "FAIL", GITSRC),
    ("t1-origin-fifo-config", r_t1, (), "FAIL", GITTIME),
    ("q1-honest", r_q1, (), "PASS", "-"),
    ("q2-regular-include", r_q2, (), "PASS", "-"),
    ("q3-missing-include", r_q3, (), "PASS", "-"),
    ("q4-fifo-hooks-not-a-source", r_q4, (), "PASS", "-"),
    ("q5-regular-home-xdg", r_q5, (HOMEENV, XDGENV), "PASS", "-"),
]


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_gate(gate, clone, report, prereg, extra):
    env = P.env_clean(extra)
    t0 = time.monotonic()
    p = subprocess.Popen(["bash", gate, "--lane", clone, "--branch", "master", "--report", report,
                          "--prereg", prereg], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL, env=env, start_new_session=True, cwd=os.path.dirname(clone))
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
    fails = [l for l in text.splitlines() if l.startswith("check-") and l.endswith("=FAIL")]
    if p.returncode == 0 and not fails:
        verdict = "PASS"
    elif p.returncode == 1 and fails:
        verdict = "FAIL"
    else:
        verdict = "ODD"
    return p.returncode, verdict, text, time.monotonic() - t0


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
    for rid, mut, envkeys, ev, ecls in ROUTES:
        rowdir = os.path.join(work, rid)
        extra = {}
        if HOMEENV in envkeys:
            extra["HOME"] = os.path.join(rowdir, "home")
        if XDGENV in envkeys:
            extra["XDG_CONFIG_HOME"] = os.path.join(rowdir, "xdg")
        try:
            clone, report, prereg = P.build(rowdir)
            for d in extra.values():
                os.makedirs(d, exist_ok=True)
            mut(clone, rowdir)
        except (P.FixtureError, OSError, subprocess.SubprocessError) as exc:
            errs += 1
            print(f"ROW {rid} expect={ev}/{ecls} verdict=- class=- rc=- secs=- match=error "
                  f"detail={type(exc).__name__}: {str(exc)[:200]}")
            continue
        rc, verdict, text, secs = run_gate(gate, clone, report, prereg, extra)
        hangs += verdict == "HANG"
        seen = next((k for k in CLASSES if k in text), "-")
        ok = verdict == ev and (ecls == "-" or ecls in text)
        mism += 0 if ok else 1
        print(f"ROW {rid} expect={ev}/{ecls} verdict={verdict} class={seen} rc={rc} secs={secs:.1f} "
              f"match={'yes' if ok else 'no'}")
        if not ok:
            brief = " | ".join(l for l in text.splitlines() if l.startswith(("check-", "detail-")))
            print(f"#  {rid} {brief[:300]}")
    print(f"SUMMARY rows={len(ROUTES)} mismatches={mism} errors={errs} hangs={hangs}")
    return 0 if mism == 0 and errs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
