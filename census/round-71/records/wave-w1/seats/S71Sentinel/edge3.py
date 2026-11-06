#!/usr/bin/env python3
"""Debug: process-filter protocol, text/eol and working-tree-encoding fixtures built correctly."""
import os, subprocess, sys, tempfile

S = "/fast/scratch/hyaku/souji-r71/S71Sentinel"
PF = os.path.join(S, "procfilter.py")
GENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
GENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_DATE="2026-11-06T12:00:00Z", GIT_COMMITTER_DATE="2026-11-06T12:00:00Z")

def run(argv, cwd, inp=None, env=None):
    return subprocess.run(argv, cwd=cwd, capture_output=True, input=inp, env=env or GENV)

def g(d, *a, inp=None):
    return run(["git", *a], d, inp)

def mk(name, files, attrs=None, cfg=()):
    d = tempfile.mkdtemp(prefix=name + ".", dir=S)
    assert d and os.path.isdir(d), d
    g(d, "init", "-q")
    assert os.path.realpath(g(d, "rev-parse", "--show-toplevel").stdout.decode().strip()) == os.path.realpath(d)
    g(d, "config", "user.name", "probe"); g(d, "config", "user.email", "probe@invalid")
    for k, v in cfg:
        g(d, "config", k, v)
    if attrs:
        os.makedirs(os.path.join(d, ".git", "info"), exist_ok=True)
        open(os.path.join(d, ".git", "info", "attributes"), "w").write(attrs)
    for rel, body in files.items():
        os.makedirs(os.path.dirname(os.path.join(d, rel)) or d, exist_ok=True)
        open(os.path.join(d, rel), "wb").write(body)
    open(os.path.join(d, "tools", "instr.sh"), "wb").write(b"#!/bin/sh\necho ok\n")
    os.chmod(os.path.join(d, "tools", "instr.sh"), 0o755)
    g(d, "add", "-A"); g(d, "commit", "-qm", "seed")
    return d

def st(d):
    r = g(d, "-c", "status.showUntrackedFiles=all", "status", "--porcelain")
    return (r.stdout.decode().replace("\n", " ").strip() or "(clean)") + \
           (f" rc={r.returncode} ERR:{r.stderr.decode()[:120]!r}" if r.returncode or r.stderr else "")

print("D2 text+eol: attribute BEFORE commit; committed LF blob, worktree variants")
d = mk("d2", {"tools/counter.py": b"aaaaaaaa\n"}, attrs="tools/counter.py text\n",
       cfg=[("core.autocrlf", "false")])
print("   blob:", g(d, "cat-file", "blob", "HEAD:tools/counter.py").stdout)
print("   status LH:", st(d))
open(os.path.join(d, "tools", "counter.py"), "wb").write(b"aaaaaaaa\r\n")
print("   status CRLF:", st(d))
d = mk("d2b", {"tools/counter.py": b"aaaaaaaa\r\n"}, attrs="tools/counter.py text\n",
       cfg=[("core.autocrlf", "true")])
print("   d2b blob:", g(d, "cat-file", "blob", "HEAD:tools/counter.py").stdout)
print("   d2b status:", st(d))
open(os.path.join(d, "tools", "counter.py"), "wb").write(b"bbbbbbb\r\n")
print("   d2b forged 8B CRLF:", st(d))
open(os.path.join(d, "tools", "counter.py"), "wb").write(b"bbbbbbbb\n")
print("   d2b forged 8B+LF :", st(d))

print("D3 working-tree-encoding=UTF-16, attribute BEFORE commit")
text = "counter v1\n"
d = mk("d3", {"tools/counter.py": b"\xff\xfe" + text.encode("utf-16-le")},
       attrs="tools/counter.py working-tree-encoding=UTF-16\n")
print("   blob (want UTF-8):", g(d, "cat-file", "blob", "HEAD:tools/counter.py").stdout)
print("   status LE:", st(d))
open(os.path.join(d, "tools", "counter.py"), "wb").write(b"\xfe\xff" + text.encode("utf-16-be"))
print("   status BE (same text, same size):", st(d))
open(os.path.join(d, "tools", "counter.py"), "wb").write(b"\xff\xfe" + "counter v2\n".encode("utf-16-le"))
print("   status other text:", st(d))

print("D4 untrackedCache: new file inside a cached tracked dir, dir mtime restored")
d = mk("d4", {"tools/counter.py": b"counter v1\n", "sub/keep.txt": b"k\n"},
       cfg=[("core.untrackedCache", "true")])
g(d, "status", "--porcelain")
sub = os.path.join(d, "sub"); before = os.stat(sub)
open(os.path.join(sub, "hidden.txt"), "w").write("hidden\n")
os.utime(sub, ns=(before.st_atime_ns, before.st_mtime_ns))
print("   restored dir mtime:", st(d))
d = mk("d4b", {"tools/counter.py": b"counter v1\n", "sub/keep.txt": b"k\n"},
       cfg=[("core.untrackedCache", "true")])
g(d, "status", "--porcelain")
open(os.path.join(d, "sub", "hidden.txt"), "w").write("hidden\n")
print("   no restore        :", st(d))
