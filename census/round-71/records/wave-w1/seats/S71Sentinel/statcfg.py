#!/usr/bin/env python3
"""E1-E4: can repository-local status config hide a same-size edit whose mtime is restored?"""
import os, subprocess, sys, tempfile, time

S = "/fast/scratch/hyaku/souji-r71/S71Sentinel"
GENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
GENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_DATE="2026-11-06T12:00:00Z", GIT_COMMITTER_DATE="2026-11-06T12:00:00Z")

def g(d, *a, env=None):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, env=env or GENV)

def mk(name):
    d = tempfile.mkdtemp(prefix=name + ".", dir=S)
    assert d and os.path.isdir(d), d
    g(d, "init", "-q")
    top = g(d, "rev-parse", "--show-toplevel").stdout.decode().strip()
    assert os.path.realpath(top) == os.path.realpath(d), (top, d)
    g(d, "config", "user.name", "probe"); g(d, "config", "user.email", "probe@invalid")
    os.makedirs(os.path.join(d, "tools"), exist_ok=True)
    open(os.path.join(d, "tools", "counter.py"), "wb").write(b"counter v1\n")
    open(os.path.join(d, "tools", "instr.sh"), "wb").write(b"#!/bin/sh\necho ok\n")
    os.chmod(os.path.join(d, "tools", "instr.sh"), 0o755)
    g(d, "add", "-A"); g(d, "commit", "-qm", "seed")
    time.sleep(1.2)                      # leave the racy window behind
    g(d, "status", "--porcelain")        # refresh the stat cache (optional locks on)
    return d

def wstatus(d):
    env = dict(GENV); env["GIT_OPTIONAL_LOCKS"] = "0"
    r = subprocess.run(["git", "-C", d, "-c", "core.fsmonitor=false", "-c", "core.excludesFile=/dev/null",
                        "-c", "core.fileMode=true", "-c", "status.showUntrackedFiles=all",
                        "status", "--porcelain"], capture_output=True, env=env)
    return r.stdout.decode().replace("\n", " ").strip() or "(clean)"

def forge_restore_mtime(d, rel="tools/counter.py"):
    p = os.path.join(d, rel)
    st = os.stat(p)
    open(p, "wb").write(b"counter v2\n")
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
    return os.stat(p).st_mtime_ns == st.st_mtime_ns

def case(label, cfgs, rel="tools/counter.py"):
    d = mk(label)
    for k, v in cfgs:
        r = g(d, "config", k, v)
        assert r.returncode == 0, (k, v, r.stderr)
    same = forge_restore_mtime(d, rel)
    print(f"{label:34s} mtime_restored={same} status={wstatus(d)!r}")
    return d

case("E1 checkStat=minimal", [("core.checkStat", "minimal")])
case("E2 trustctime=false", [("core.trustctime", "false")])
case("E3 ignoreStat=true", [("core.ignoreStat", "true")])
case("E0 control (no config)", [])
case("E1b checkStat=minimal+trustctime", [("core.checkStat", "minimal"), ("core.trustctime", "false")])

# E4: untrackedCache hides a file created in-run with the directory mtime restored
d = mk("e4")
g(d, "config", "core.untrackedCache", "true")
sub = os.path.join(d, "sub"); os.makedirs(sub)
open(os.path.join(sub, "keep.txt"), "w").write("k\n")
g(d, "status", "--porcelain")  # populate the untracked cache
before = os.stat(sub)
open(os.path.join(sub, "hidden.txt"), "w").write("hidden\n")
os.utime(sub, ns=(before.st_atime_ns, before.st_mtime_ns))
print(f"{'E4 untrackedCache':34s} status={wstatus(d)!r} dir_mtime_restored=True")
# control: same without restoring the directory mtime
d2 = mk("e4b"); g(d2, "config", "core.untrackedCache", "true")
sub2 = os.path.join(d2, "sub"); os.makedirs(sub2)
open(os.path.join(sub2, "keep.txt"), "w").write("k\n")
g(d2, "status", "--porcelain")
open(os.path.join(sub2, "hidden.txt"), "w").write("hidden\n")
print(f"{'E4b untrackedCache no-restore':34s} status={wstatus(d2)!r}")
