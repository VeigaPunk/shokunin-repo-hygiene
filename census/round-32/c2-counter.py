#!/usr/bin/env python3
"""r32 C2 operability counter (frozen at the r32 preregistration): lane tools and fixtures run under the
operator's scratch discipline (prompt section 7 item 4: a committed counter, probe or gate that writes under
/tmp or /var/tmp regardless of TMPDIR is a routed defect).

Enumerated set: `census/round-32/c2-items.tsv`, read at --list-rev (never at REV): id, argv (shlex, run from
the clone root), files (the committed files whose scratch root the item exercises). Rule for the set in that
file's header.

Per item, two runs, each in its own private `git clone --no-local` (origin removed), each with TMPDIR a
fresh directory under --scratch and the process tree traced by `strace -f`:
  BASE  the clone checked out at --base, run as is.
  SBOX  the clone checked out at REV, run inside `bwrap --dev-bind / / --ro-bind <empty> /tmp
        --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm` (strace runs inside the sandbox), so any
        attempt to create a path under /tmp, /var/tmp or /dev/shm fails.
S = last digit-bearing line of normalized stdout (stderr when stdout has none; scratch and tmp paths ->
<TMP>, 12+ hex -> <HEX>, `N.Ns` -> <DUR>, whitespace collapsed). W = number of successful file-creating
syscalls in the trace (mkdir, mkdirat, creat, and open/openat/openat2 carrying O_CREAT, result >= 0).
An item PASSES iff
  (a) SBOX exits with BASE's exit code and prints BASE's S, BASE's S is not NONE, and
  (b) SBOX's W is at least half of BASE's W (a tool that stops doing its work to dodge the sandbox fails).
Output: one ITEM line per item, then
    SUMMARY items=<n> pass=<p> fail=<f> rev=<REV>
Frozen target (preregistration): `fail=0` over the enumerated set at the C2 landing commit and at the tip.
Exit 0 iff fail=0; 1 otherwise; 2 could-not-evaluate. Read-only on --root.
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

FULL = re.compile(r"[0-9a-f]{40}")
GITC = ["-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null"]
TRACE = "mkdir,mkdirat,creat,open,openat,openat2"


def cne(msg):
    print(f"COULD-NOT-EVALUATE {msg}")
    sys.exit(2)


def git(root, *a, check=True):
    p = subprocess.run(["git", "-C", root, *GITC, *a], capture_output=True)
    if check and p.returncode:
        cne("git " + " ".join(a) + ": " + p.stderr.decode("utf-8", "replace").strip())
    return p


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return None if p.returncode else p.stdout.decode("utf-8", "replace")


def normalize(text, scratch):
    text = text.replace(scratch, "<TMP>")
    text = re.sub(r"(?:/var)?/tmp/[^\s'\"`:,)]+", "<TMP>", text)
    text = re.sub(r"/fast/scratch/[^\s'\"`:,)]+", "<TMP>", text)
    text = re.sub(r"\b[0-9a-f]{12,}\b", "<HEX>", text)
    text = re.sub(r"\b\d+\.\d+s\b", "<DUR>", text)
    return text


def summary_line(text):
    for line in reversed(text.splitlines()):
        s = " ".join(line.split())
        if s and re.search(r"\d", s):
            return s
    return "NONE"


def creations(log):
    n = 0
    try:
        fh = open(log, errors="replace")
    except OSError:
        return 0
    with fh:
        for line in fh:
            m = re.search(r"\b(mkdir|mkdirat|creat|open|openat|openat2)\((.*)\)\s+=\s+(-?\d+)", line)
            if not m or int(m.group(3)) < 0:
                continue
            if m.group(1) in ("mkdir", "mkdirat", "creat") or "O_CREAT" in m.group(2):
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser(prog="c2-counter.py")
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--list-rev", required=True, help="preregistration commit holding census/round-32/c2-items.tsv")
    ap.add_argument("--scratch", default=os.environ.get("HYAKU_SCRATCH", "/fast/scratch/hyaku") + "/souji-r32/c2-counter")
    ap.add_argument("--timeout", type=int, default=1200)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    for name in ("rev", "base", "list_rev"):
        if not FULL.fullmatch(getattr(a, name)):
            cne(f"--{name.replace('_', '-')} must be a full 40-hex revision")
        git(a.root, "cat-file", "-e", getattr(a, name) + "^{commit}")
    for tool in ("bwrap", "strace"):
        if shutil.which(tool) is None:
            cne(f"{tool} not on PATH")
    root = os.path.abspath(a.root)
    scratch = os.path.abspath(a.scratch)
    for bad in ("/tmp", "/var/tmp", "/dev/shm"):
        if scratch == bad or scratch.startswith(bad + "/"):
            cne("--scratch must not be under /tmp, /var/tmp or /dev/shm")
    tsv = blob(root, a.list_rev, "census/round-32/c2-items.tsv")
    if tsv is None:
        cne("census/round-32/c2-items.tsv absent at --list-rev")
    items = []
    for ln in tsv.splitlines():
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        f = ln.split("\t")
        if len(f) != 3:
            cne(f"malformed c2-items line: {ln!r}")
        items.append((f[0], shlex.split(f[1])))
    only = set(x for x in a.only.split(",") if x)
    os.makedirs(scratch, exist_ok=True)
    work = tempfile.mkdtemp(prefix="c2.", dir=scratch)
    empty = os.path.join(work, "empty")
    os.makedirs(empty)
    os.chmod(empty, 0o555)
    passed = failed = 0
    try:
        clones = {}
        for tag, rev in (("base", a.base), ("rev", a.rev)):
            c = os.path.join(work, tag)
            p = subprocess.run(["git", "clone", "-q", "--no-local", "--no-checkout", root, c], capture_output=True)
            if p.returncode:
                cne("clone failed: " + p.stderr.decode("utf-8", "replace").strip())
            git(c, "remote", "remove", "origin")
            if git(c, "rev-parse", "--show-toplevel").stdout.decode().strip() != c:
                cne("clone toplevel mismatch")
            clones[tag] = (c, rev)

        def run(tag, argv, sandbox):
            c, rev = clones[tag]
            git(c, "checkout", "-qf", "--detach", rev)
            git(c, "clean", "-fdxq")
            tmp = tempfile.mkdtemp(prefix="t.", dir=work)
            log = tempfile.mktemp(prefix="strace.", dir=work)
            env = dict(os.environ, TMPDIR=tmp, GIT_CONFIG_NOSYSTEM="1")
            env.pop("GIT_DIR", None)
            env.pop("GIT_WORK_TREE", None)
            cmd = ["strace", "-f", "-qq", "-o", log, "-e", "trace=" + TRACE, *argv]
            if sandbox:
                cmd = ["bwrap", "--dev-bind", "/", "/", "--ro-bind", empty, "/tmp", "--ro-bind", empty, "/var/tmp",
                       "--ro-bind", empty, "/dev/shm", "--chdir", c, *cmd]
            try:
                q = subprocess.run(cmd, cwd=c, env=env, capture_output=True, timeout=a.timeout)
                rc, out, err = q.returncode, q.stdout.decode("utf-8", "replace"), q.stderr.decode("utf-8", "replace")
            except subprocess.TimeoutExpired as e:
                rc, out, err = 124, (e.stdout or b"").decode("utf-8", "replace"), (e.stderr or b"").decode("utf-8", "replace")
            w = creations(log)
            for x in (tmp, log):
                shutil.rmtree(x, ignore_errors=True) if os.path.isdir(x) else (os.path.exists(x) and os.unlink(x))
            s = summary_line(normalize(out, work))
            if s == "NONE":
                s = summary_line(normalize(err, work))
            return rc, s, w

        for iid, argv in items:
            if only and iid not in only:
                continue
            rc0, s0, w0 = run("base", argv, False)
            rc1, s1, w1 = run("rev", argv, True)
            ok_a = rc1 == rc0 and s1 == s0 and s0 != "NONE"
            ok_b = w1 * 2 >= w0
            ok = ok_a and ok_b
            passed += ok
            failed += not ok
            print(f"ITEM\t{iid}\t{'PASS' if ok else 'FAIL'}\tbase=rc{rc0}:W{w0}:{s0}\tsbox=rc{rc1}:W{w1}:{s1}"
                  f"\t{'' if ok_a else 'regress '}{'' if ok_b else 'work-dropped'}")
    finally:
        subprocess.run(["chmod", "-R", "u+w", work], capture_output=True)
        shutil.rmtree(work, ignore_errors=True)
    n = len(items) if not only else len(only)
    partial = " partial=1" if only else ""
    print(f"SUMMARY items={n} pass={passed} fail={failed}{partial} rev={a.rev}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
