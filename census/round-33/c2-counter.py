#!/usr/bin/env python3
"""r33 C2 operability counter (frozen at the r33 preregistration): the r32-closure-routed scratch-discipline repairs,
measured by executing the tools (legs O1-O5) with no-harm guards (G1-G6).

Legs: `census/round-33/c2-legs.tsv`, read at --list-rev (never at --rev); kinds (sandbox, sandbox-nt, slash, guard)
and PASS rules in that file's header; sandbox-nt runs are not strace-wrapped.
Every run happens in a private clone (`git clone --no-local --no-checkout`, origin removed) checked out detached at
the run's revision and `git clean -fdx`-ed before each run, cwd = the clone root, environment = the caller's plus
TMPDIR=<fresh scratch dir> and GIT_CONFIG_NOSYSTEM=1, the process tree traced by `strace -f` for file-creating
syscalls (mkdir, mkdirat, creat, open/openat/openat2 with O_CREAT, result >= 0). Sandboxed runs use
`bwrap --dev-bind / / --ro-bind <empty> /tmp --ro-bind <empty> /var/tmp --ro-bind <empty> /dev/shm`.
S = last digit-bearing line of normalized stdout (stderr when stdout has none): scratch paths and /tmp, /var/tmp,
/fast/scratch paths -> <TMP>, 12+ hex -> <HEX>, `N.Ns` -> <DUR>, whitespace collapsed.
Output: one LEG line per leg, then
    SUMMARY legs=<n> pass=<p> fail=<f> harm=<h> rev=<REV>
where pass/fail count the O legs and harm counts FAILed G guards.
Frozen target (preregistration): `legs=11 pass=5 fail=0 harm=0` at the C2 landing commit and at the tip.
Exit 0 iff fail=0 and harm=0; 1 otherwise; 2 could-not-evaluate. Read-only on --root.
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
TRACE = "mkdir,mkdirat,creat,open,openat,openat2"
LEGS_PATH = "census/round-33/c2-legs.tsv"


def cne(msg):
    print(f"COULD-NOT-EVALUATE {msg}")
    sys.exit(2)


def git(root, *a, check=True):
    p = subprocess.run(["git", "-C", root, "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", *a],
                       capture_output=True)
    if check and p.returncode:
        cne("git " + " ".join(a) + ": " + p.stderr.decode("utf-8", "replace").strip())
    return p


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "cat-file", "blob", f"{rev}:{path}"], capture_output=True)
    return None if p.returncode else p.stdout.decode("utf-8", "replace")


def normalize(text, work):
    text = text.replace(work, "<TMP>")
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
    ap.add_argument("--list-rev", required=True, help="preregistration commit holding census/round-33/c2-legs.tsv")
    ap.add_argument("--scratch", required=True)
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
    tsv = blob(root, a.list_rev, LEGS_PATH)
    if tsv is None:
        cne(f"{LEGS_PATH} absent at --list-rev")
    legs = []
    for ln in tsv.splitlines():
        if not ln.strip() or ln.startswith("#") or ln.startswith("id\t"):
            continue
        f = ln.split("\t")
        if len(f) != 3 or f[1] not in ("sandbox", "sandbox-nt", "slash", "guard"):
            cne(f"malformed leg line: {ln!r}")
        legs.append((f[0], f[1], f[2]))
    only = set(x for x in a.only.split(",") if x)
    if only - {x[0] for x in legs}:
        cne("unknown --only ids")
    os.makedirs(scratch, exist_ok=True)
    work = tempfile.mkdtemp(prefix="c2.", dir=scratch)
    empty = os.path.join(work, "empty")
    os.makedirs(empty)
    os.chmod(empty, 0o555)
    passed = failed = harm = 0
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

        def run(tag, argv_t, sandbox=False, slash=False, trace=True):
            c, rev = clones[tag]
            git(c, "checkout", "-qf", "--detach", rev)
            git(c, "clean", "-fdxq")
            argv = shlex.split(argv_t.replace("{REV}", rev))
            tmp = tempfile.mkdtemp(prefix="t.", dir=work)
            log = os.path.join(work, "strace." + os.path.basename(tmp))
            env = dict(os.environ, TMPDIR=tmp + ("/" if slash else ""), GIT_CONFIG_NOSYSTEM="1")
            for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
                env.pop(k, None)
            cmd = ["strace", "-f", "-qq", "-o", log, "-e", "trace=" + TRACE, *argv] if trace else list(argv)
            if sandbox:
                cmd = ["bwrap", "--dev-bind", "/", "/", "--ro-bind", empty, "/tmp", "--ro-bind", empty, "/var/tmp",
                       "--ro-bind", empty, "/dev/shm", "--chdir", c, *cmd]
            try:
                q = subprocess.run(cmd, cwd=c, env=env, capture_output=True, timeout=a.timeout)
                rc, out, err = q.returncode, q.stdout.decode("utf-8", "replace"), q.stderr.decode("utf-8", "replace")
            except subprocess.TimeoutExpired as e:
                rc, out, err = 124, (e.stdout or b"").decode("utf-8", "replace"), (e.stderr or b"").decode("utf-8", "replace")
            w = creations(log)
            subprocess.run(["chmod", "-R", "u+w", tmp], capture_output=True)
            shutil.rmtree(tmp, ignore_errors=True)
            if os.path.exists(log):
                os.unlink(log)
            s = summary_line(normalize(out, work))
            if s == "NONE":
                s = summary_line(normalize(err, work))
            return rc, s, w

        for lid, kind, argv in legs:
            if only and lid not in only:
                continue
            rc0, s0, w0 = run("base", argv, trace=kind != "sandbox-nt")
            if kind == "sandbox-nt":
                rc1, s1, w1 = run("rev", argv, sandbox=True, trace=False)
                ok = rc1 == rc0 and s1 == s0 and s0 != "NONE"
                detail = f"base=rc{rc0}:{s0}\tsbox=rc{rc1}:{s1}"
            elif kind == "sandbox":
                rc1, s1, w1 = run("rev", argv, sandbox=True)
                ok = rc1 == rc0 and s1 == s0 and s0 != "NONE" and w1 * 2 >= w0
                detail = f"base=rc{rc0}:W{w0}:{s0}\tsbox=rc{rc1}:W{w1}:{s1}"
            elif kind == "slash":
                rc1, s1, w1 = run("rev", argv)
                rc2, s2, w2 = run("rev", argv, slash=True)
                ok = rc1 == rc0 and s1 == s0 and rc2 == rc1 and s2 == s1 and s0 != "NONE"
                detail = f"base=rc{rc0}:{s0}\trev=rc{rc1}:{s1}\trev-slash=rc{rc2}:{s2}"
            else:
                rc1, s1, w1 = run("rev", argv)
                ok = rc1 == rc0 and s1 == s0 and s0 != "NONE"
                detail = f"base=rc{rc0}:{s0}\trev=rc{rc1}:{s1}"
            if kind == "guard":
                harm += not ok
            else:
                passed += ok
                failed += not ok
            print(f"LEG\t{lid}\t{kind}\t{'PASS' if ok else 'FAIL'}\t{detail}", flush=True)
    finally:
        subprocess.run(["chmod", "-R", "u+w", work], capture_output=True)
        shutil.rmtree(work, ignore_errors=True)
    n = len(only) if only else len(legs)
    partial = " partial=1" if only else ""
    print(f"SUMMARY legs={n} pass={passed} fail={failed} harm={harm}{partial} rev={a.rev}")
    return 0 if failed == 0 and harm == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
