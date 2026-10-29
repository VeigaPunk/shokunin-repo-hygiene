#!/usr/bin/env python3
"""Final probes: prereg symlink, ssh remote exec, selftest write scope, oversize/NUL inputs."""
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import driver as D  # reuses mkrepo/git/write/commit/manifest/run_tool

L = D.log


def prereg_symlink():
    L("\n=== N1: committed prereg that is a SYMLINK (git stores the link text) ===")
    d = D.mkrepo("n1_presym")
    D.write(d, "real.txt", "Round: 7\n## C1\nBase: x\n")
    os.symlink("real.txt", os.path.join(d, "pre.txt"))
    D.commit(d, "sym")
    rev = D.git(d, "rev-parse", "HEAD")
    link_text = D.git(d, "cat-file", "-p", "HEAD:pre.txt")
    L("  blob at HEAD:pre.txt (what the tool reads): %r" % link_text)
    rc, out, err, dt = D.run_tool(d, "pre.txt", rev, timeout=30)
    L("  tool rc=%s out=%s err=%s" % (rc, out.strip().replace("\n", " | ")[:160], err.strip()[:120]))
    L("  checkout readers follow the link to real.txt; the tool does not check PREREG symlink-ness")


def ssh_exec():
    L("\n=== I2: partial clone, remote.origin.url=ssh://..., core.sshCommand -> repo program ===")
    src = D.mkrepo("i2_src")
    D.write(src, "pre.txt", "Round: 7\n## C1\n")
    D.commit(src, "base")
    D.git(src, "config", "uploadpack.allowFilter", "true")
    dest = os.path.join(D.ATK, "i2_partial")
    shutil.rmtree(dest, ignore_errors=True)
    p = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout",
                        "file://" + src, dest], env=D.GITENV, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    if p.returncode != 0:
        L("  clone failed: %s" % p.stderr.decode()[:160])
        return
    marker = os.path.join(D.ATK, "I2_MARKER.txt")
    if os.path.exists(marker):
        os.unlink(marker)
    D.write(D.ATK, "i2_ssh.sh", "#!/bin/sh\necho \"EXEC sshCommand $*\" >> %s\nexit 1\n" % marker)
    os.chmod(os.path.join(D.ATK, "i2_ssh.sh"), 0o755)
    D.git(dest, "config", "core.sshCommand", os.path.join(D.ATK, "i2_ssh.sh"))
    D.git(dest, "config", "remote.origin.url", "ssh://attacker.invalid/x")
    D.git(dest, "config", "extensions.partialClone", "origin")
    rev = D.git(dest, "rev-parse", "HEAD")
    rc, out, err, dt = D.run_tool(dest, "pre.txt", rev, timeout=60)
    L("  tool rc=%s time=%ss out=%s" % (rc, dt, (out.splitlines() or [""])[-1][:60]))
    L("  sshCommand program executed: %s" % os.path.exists(marker))
    if os.path.exists(marker):
        L("  marker: %s" % open(marker).read().strip().replace("\n", " | "))


def selftest_scope():
    L("\n=== H4: --selftest write scope: HOME, cwd, TMPDIR and /tmp before/after ===")
    base = os.path.join(D.ATK, "h4")
    shutil.rmtree(base, ignore_errors=True)
    home, cwd, tmpd = (os.path.join(base, x) for x in ("home", "cwd", "tmp"))
    for x in (home, cwd, tmpd):
        os.makedirs(x)
    tmp_before = set(os.listdir("/tmp"))
    env = dict(os.environ)
    env["HOME"] = home
    env["TMPDIR"] = tmpd
    before = {"home": D.manifest(home), "cwd": D.manifest(cwd), "tmp": D.manifest(tmpd)}
    p = subprocess.run([sys.executable, "-B", D.TOOL, "--selftest"], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env, cwd=cwd, timeout=300)
    L("  rc=%s stdout=%s" % (p.returncode, p.stdout.decode().strip()))
    for k, dpath in (("home", home), ("cwd", cwd), ("tmp", tmpd)):
        ch = D.diff_manifest(before[k], D.manifest(dpath))
        L("  %s changes: %s" % (k, ch or "NONE"))
    new_tmp = set(os.listdir("/tmp")) - tmp_before
    L("  new entries in /tmp: %s" % (sorted(new_tmp) or "NONE"))


def oversize_and_nul():
    L("\n=== K1: oversize path value and NUL byte in a Counter value ===")
    d = D.mkrepo("k1")
    D.write(d, "census/c1.py", "counter\n")
    D.commit(d, "base")
    rev = D.git(d, "rev-parse", "HEAD")
    big = "a" * 70000
    D.write(d, "big.txt", "Round: 7\n## C1\nBase: %s\nCounter: %s sha256=%s\nPopulation: census/c1.py sha256=%s\nControl: census/c1.py\nTarget: t\nKill: k\n" % (rev, big, "0" * 64, "0" * 64))
    D.commit(d, "big")
    r2 = D.git(d, "rev-parse", "HEAD")
    rc, out, err, dt = D.run_tool(d, "big.txt", r2, timeout=30)
    L("  70KB counter path: rc=%s err=%s out=%s" % (rc, err.strip()[-120:], out.strip().replace("\n", " | ")[:120]))
    raw = b"Round: 7\n## C1\nBase: " + rev.encode() + b"\nCounter: census/c1.py\x00 sha256=" + b"0" * 64 + b"\nPopulation: census/c1.py sha256=" + b"0" * 64 + b"\nControl: census/c1.py\nTarget: t\nKill: k\n"
    with open(os.path.join(d, "nul.txt"), "wb") as fh:
        fh.write(raw)
    D.commit(d, "nul")
    r3 = D.git(d, "rev-parse", "HEAD")
    rc, out, err, dt = D.run_tool(d, "nul.txt", r3, timeout=30)
    L("  NUL in Counter value: rc=%s crash=%s out=%s" % (rc, "Traceback" in err, out.strip().replace("\n", " | ")[:140]))


def clock_lane():
    L("\n=== K2: real-lane wall time for one run (read-only) ===")
    lane = "/home/vgpnk/Projects/shokunin/souji-shokunin"
    t = time.time()
    rc, out, err, dt = D.run_tool(lane, "census/round-42/preregistration.txt",
                                  "3105a63b23481fccf7df58e74d14a6681e0ea0c8", timeout=120)
    L("  rc=%s wall=%.2fs out=%s" % (rc, time.time() - t, out.strip().replace("\n", " | ")))


if __name__ == "__main__":
    os.makedirs(D.ATK, exist_ok=True)
    for fn in (prereg_symlink, ssh_exec, selftest_scope, oversize_and_nul, clock_lane):
        fn()
