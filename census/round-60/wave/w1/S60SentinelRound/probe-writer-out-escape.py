#!/usr/bin/env python3
"""probe-writer-out-escape.py - where can the C2 writer's --out point?

The writer computes `out = os.path.abspath(ns.out)`, refuses only when OUT already exists
(os.path.lexists) or its parent is not a directory, and never confines OUT to the lane, to a
caller scratch root, or away from credential-shaped paths. The r23/r24 predecessor
tools/souji-receipt-run.py refuses OUT under /tmp, OUT outside the caller scratch root, and OUT
inside --root; this candidate refuses none of the three.

  O1  OUT = a credential-shaped path under a fake HOME (".ssh/authorized_keys") is written.
  O2  OUT inside --root (a repo write) is written.
  O3  OUT whose parent is a symlink to a directory outside --root is written through the link.
  O4  OUT in a non-writable directory: refusal or uncaught traceback? (Q107: no traceback)
  O5  --selftest --report PATH truncates an existing caller file (no refusal, unlike --out).
  O6  OUT = /dev/full or an existing special file: lexists refuses (control).

Usage: probe-writer-out-escape.py --work DIR --tool PATH
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _h  # noqa: E402


def fresh(work, tag):
    repo = _h.make_repo(os.path.join(work, tag))
    _h.write(repo, "instrument.sh", "#!/bin/sh\necho i\n")
    _h.write(repo, "tracked.txt", "clean\n")
    return repo, _h.commit(repo, "seed")


def run_writer(tool, root, rev, out, extra=(), cwd=None, env=None):
    argv = [sys.executable, "-B", tool, "--root", root, "--rev", rev,
            "--instrument", "instrument.sh", "--out", out] + list(extra) + ["--", "/bin/echo", "ok"]
    return _h.run(argv, cwd=cwd, env=env)


def main():
    work = _h.scratch_root(sys.argv)
    tool = os.path.abspath(_h.opt(sys.argv, "--tool"))
    p = _h.Probe("writer-out-escape")
    if not (tool and os.path.isfile(tool)):
        p.check("O0 tool-present", False, "absent: %r" % tool)
        return p.finish()
    p.check("O0 tool-present", True, tool)

    # ---- O1: credential-shaped path under a fake HOME --------------------------------------
    repo, rev = fresh(work, "o1")
    home = os.path.join(work, "o1-home")
    os.makedirs(os.path.join(home, ".ssh"), exist_ok=True)
    out = os.path.join(home, ".ssh", "authorized_keys")
    rc, so, se = run_writer(tool, repo, rev, out, env={"HOME": home})
    wrote = os.path.exists(out)
    p.check("O1 writes credential-shaped path", rc == 0 and wrote,
            "rc=%d path=%s bytes=%s" % (rc, out, os.path.getsize(out) if wrote else "absent"))

    # ---- O2: OUT inside --root --------------------------------------------------------------
    repo2, rev2 = fresh(work, "o2")
    out2 = os.path.join(repo2, "census", "round-60", "records", "receipt.txt")
    os.makedirs(os.path.dirname(out2), exist_ok=True)
    rc, so, se = run_writer(tool, repo2, rev2, out2)
    wrote2 = os.path.exists(out2)
    dirty = _h.out(_h.git(repo2, "status", "--porcelain"))
    p.check("O2 writes inside --root", rc == 0 and wrote2,
            "rc=%d wrote=%s root now dirty=%r" % (rc, wrote2, dirty))

    # ---- O3: symlinked parent directory ----------------------------------------------------
    repo3, rev3 = fresh(work, "o3")
    outside = os.path.join(work, "o3-outside")
    os.makedirs(outside, exist_ok=True)
    link = os.path.join(work, "o3-link")
    if os.path.lexists(link):
        os.unlink(link)
    os.symlink(outside, link)
    out3 = os.path.join(link, "receipt.txt")
    rc, so, se = run_writer(tool, repo3, rev3, out3)
    landed = os.path.exists(os.path.join(outside, "receipt.txt"))
    p.check("O3 follows symlinked parent", rc == 0 and landed,
            "rc=%d real target=%s landed=%s" % (rc, os.path.realpath(out3), landed))

    # ---- O4: non-writable OUT directory ----------------------------------------------------
    repo4, rev4 = fresh(work, "o4")
    rodir = os.path.join(work, "o4-ro")
    os.makedirs(rodir, exist_ok=True)
    os.chmod(rodir, 0o555)
    out4 = os.path.join(rodir, "receipt.txt")
    try:
        rc, so, se = run_writer(tool, repo4, rev4, out4)
        traceback = "Traceback (most recent call last)" in se
        p.check("O4 read-only dir: refusal not traceback",
                rc == 2 and not traceback,
                "rc=%d traceback=%s stderr_tail=%r" % (rc, traceback, se.strip().splitlines()[-1][:110]
                                                       if se.strip() else ""))
    finally:
        os.chmod(rodir, 0o755)

    # ---- O5: --selftest --report truncates a caller file ----------------------------------
    victim = os.path.join(work, "o5-victim.txt")
    with open(victim, "wb") as fh:
        fh.write(b"CALLER-BYTES-DO-NOT-TRUNCATE\n")
    workdir = os.path.join(work, "o5-selftest-work")
    os.makedirs(workdir, exist_ok=True)
    rc, so, se = _h.run([sys.executable, "-B", tool, "--selftest", "--work", workdir,
                         "--report", victim], timeout=300)
    after = open(victim, "rb").read()
    p.check("O5 --report overwrites caller file",
            after != b"CALLER-BYTES-DO-NOT-TRUNCATE\n",
            "rc=%d victim now %d bytes, starts %r" % (rc, len(after), after[:40]))

    # ---- O6: control - existing special file is refused ----------------------------------
    repo6, rev6 = fresh(work, "o6")
    rc, so, se = run_writer(tool, repo6, rev6, "/dev/full")
    p.check("O6 control: existing special file refused", rc == 2,
            "rc=%d err=%r" % (rc, se.strip()[:110]))
    return p.finish()


if __name__ == "__main__":
    sys.exit(main())
