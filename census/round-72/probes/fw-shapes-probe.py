#!/usr/bin/env python3
"""souji r72 pre-freeze feasibility probe (QUALITY Q70) for the five C2 filter-witness shapes.

Builds each shape in a fresh fixture repo (tracked tools/counter.py = b"counter v1\\n") and runs one
writer over it; prints one line per (shape, writer): rc, verdict (accept = receipt written, refuse =
rc 2 and no receipt) and the first refusal token. Shapes:
  FWr  info/attributes filter=t, clean driver `sed s/v2/v1/`, pre-run same-size forged bytes; the
       wrapped command restores the committed bytes and unsets the driver (pre-run witness only).
  FWi  honest tree; the wrapped command forges same-size bytes AND creates the attribute and the
       driver (post-run witness only).
  FWp  info/attributes filter=p, `filter.p.process` long-running driver (pkt-line v2, clean maps
       v2 -> v1), pre-run forged bytes (process-driver lookup).
  FWw  committed EMPTY .gitattributes; the worktree copy assigns itself filter=e (`cat >/dev/null`,
       cleans back to empty) and tools/counter.py filter=t; pre-run forged bytes (worktree-only
       attribute source: the index copy carries no filter).
  FWs  info/attributes filter=set with a driver literally named `set`; pre-run forged bytes.
Usage: python3 -B fw-shapes-probe.py --work DIR WRITER.py [WRITER.py ...]
Stdlib only; writes only under --work (must exist; never inside the lane)."""
import argparse, os, shutil, subprocess, sys

SEED = {"tools/instr.sh": b"#!/bin/sh\necho instrument-ok\n", "tools/counter.py": b"counter v1\n",
        "tools/notes.txt": b"notes v1\n", "README.md": b"readme v1\n"}
FORGED = b"counter v2\n"
CLEAN = "sed s/v2/v1/"
PROC_FILTER = r'''import sys
i, o = sys.stdin.buffer, sys.stdout.buffer
def rd():
    h = i.read(4)
    if not h:
        sys.exit(0)
    n = int(h, 16)
    return None if n == 0 else i.read(n - 4)
def wr(b):
    o.write(b"%04x" % (len(b) + 4) + b)
def fl():
    o.write(b"0000"); o.flush()
def lst():
    out = []
    while True:
        p = rd()
        if p is None:
            return out
        out.append(p)
lst(); wr(b"git-filter-server\n"); wr(b"version=2\n"); fl()
lst(); wr(b"capability=clean\n"); fl()
while True:
    hdr = lst()
    data = b"".join(lst())
    cmd = [h for h in hdr if h.startswith(b"command=")]
    if cmd and cmd[0] == b"command=clean\n":
        data = data.replace(b"v2", b"v1")
    wr(b"status=success\n"); fl()
    if data:
        wr(data)
    fl(); fl()
'''
RESTORE_UNSET = ("import subprocess, sys\n"
                 "open(sys.argv[1], 'wb').write(sys.argv[2].encode('latin-1'))\n"
                 "subprocess.run(['git', '-C', sys.argv[3], 'config', '--unset', 'filter.t.clean'], check=True)\n")
CREATE_FORGE = ("import os, subprocess, sys\n"
                "repo = sys.argv[1]\n"
                "open(os.path.join(repo, 'tools', 'counter.py'), 'wb').write(sys.argv[2].encode('latin-1'))\n"
                "os.makedirs(os.path.join(repo, '.git', 'info'), exist_ok=True)\n"
                "open(os.path.join(repo, '.git', 'info', 'attributes'), 'wb').write(b'tools/counter.py filter=t\\n')\n"
                "subprocess.run(['git', '-C', repo, 'config', 'filter.t.clean', sys.argv[3]], check=True)\n")


def env():
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in ("HOME", "XDG_CONFIG_HOME")}
    e.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
              "GIT_AUTHOR_DATE": "2026-11-06T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-06T12:00:00Z"})
    return e


def g(repo, *a):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, env=env())
    if r.returncode != 0:
        raise SystemExit(f"git {a} failed: {r.stderr.decode()}")
    return r.stdout.decode().strip()


def build(case_dir, shape):
    shutil.rmtree(case_dir, ignore_errors=True)
    repo = os.path.join(case_dir, "repo")
    os.makedirs(os.path.join(repo, "tools"))
    g(repo, "init", "-q")
    assert os.path.realpath(g(repo, "rev-parse", "--show-toplevel")) == os.path.realpath(repo)
    g(repo, "config", "user.name", "probe"); g(repo, "config", "user.email", "probe@invalid")
    for rel, data in SEED.items():
        open(os.path.join(repo, rel), "wb").write(data)
    os.chmod(os.path.join(repo, "tools/instr.sh"), 0o755)
    if shape == "FWw":
        open(os.path.join(repo, ".gitattributes"), "wb").write(b"")
    g(repo, "add", "-A"); g(repo, "commit", "-q", "-m", "seed")
    rev = g(repo, "rev-parse", "HEAD")
    info = os.path.join(repo, ".git", "info"); os.makedirs(info, exist_ok=True)
    argv = ["/bin/echo", "hi"]
    if shape == "FWr":
        open(os.path.join(info, "attributes"), "wb").write(b"tools/counter.py filter=t\n")
        g(repo, "config", "filter.t.clean", CLEAN)
        open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
        argv = [sys.executable, "-c", RESTORE_UNSET, os.path.join(repo, "tools/counter.py"),
                SEED["tools/counter.py"].decode("latin-1"), repo]
    elif shape == "FWi":
        argv = [sys.executable, "-c", CREATE_FORGE, repo, FORGED.decode("latin-1"), CLEAN]
    elif shape == "FWp":
        pf = os.path.join(case_dir, "proc-filter.py")
        open(pf, "w").write(PROC_FILTER)
        open(os.path.join(info, "attributes"), "wb").write(b"tools/counter.py filter=p\n")
        g(repo, "config", "filter.p.process", f"{sys.executable} -B {pf}")
        open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    elif shape == "FWw":
        open(os.path.join(repo, ".gitattributes"), "wb").write(
            b".gitattributes filter=e\ntools/counter.py filter=t\n")
        g(repo, "config", "filter.e.clean", "cat >/dev/null")
        g(repo, "config", "filter.t.clean", CLEAN)
        open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    elif shape == "FWs":
        open(os.path.join(info, "attributes"), "wb").write(b"tools/counter.py filter=set\n")
        g(repo, "config", "filter.set.clean", CLEAN)
        open(os.path.join(repo, "tools/counter.py"), "wb").write(FORGED)
    st = subprocess.run(["git", "-C", repo, "status", "--porcelain"], capture_output=True, env=env())
    return repo, rev, argv, st.stdout.decode().replace("\n", "|")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("writers", nargs="+")
    ns = ap.parse_args()
    work = os.path.realpath(ns.work)
    assert os.path.isdir(work) and not work.startswith(("/tmp/", "/var/tmp/"))
    for shape in ("FWr", "FWi", "FWp", "FWw", "FWs"):
        for w in ns.writers:
            cd = os.path.join(work, shape, os.path.basename(w))
            repo, rev, argv, prestatus = build(cd, shape)
            out = os.path.join(cd, "out", "receipt.txt"); os.makedirs(os.path.dirname(out))
            e = {k: v for k, v in env().items() if not k.startswith("GIT_AUTHOR") and not k.startswith("GIT_COMMITTER")}
            p = subprocess.run([sys.executable, "-B", os.path.abspath(w), "--root", repo, "--rev", rev,
                                "--instrument", "tools/instr.sh", "--out", out, "--allow-outside", "--", *argv],
                               cwd=repo, capture_output=True, env=e, timeout=180)
            v = ("accept" if p.returncode == 0 and os.path.isfile(out) else
                 "refuse" if p.returncode == 2 and not os.path.lexists(out) else "error")
            tok = p.stderr.decode("utf-8", "replace").strip().split("\n")[-1][:110]
            print(f"PROBE shape={shape} writer={os.path.basename(w)} pre_status={prestatus or '<clean>'} "
                  f"rc={p.returncode} verdict={v} stderr={tok or '-'}")


if __name__ == "__main__":
    main()
