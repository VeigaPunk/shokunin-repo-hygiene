#!/usr/bin/env python3
"""Round-71 writer security probes: run the CANDIDATE writer against each attribute/config route."""
import os, shutil, subprocess, sys, tempfile, time

S = "/fast/scratch/hyaku/souji-r71/S71Sentinel"
WRITER = os.path.join(S, "cand-writer.py")
GENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
GENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_DATE="2026-11-06T12:00:00Z", GIT_COMMITTER_DATE="2026-11-06T12:00:00Z")

def g(d, *a, inp=None, env=None):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, input=inp, env=env or GENV)

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
    return d

def attrtree(d, body):
    """Unreferenced commit whose tree has a root .gitattributes with `body`."""
    blob = g(d, "hash-object", "-w", "--stdin", inp=body.encode()).stdout.decode().strip()
    tree = g(d, "mktree", inp=("100644 blob %s\t.gitattributes\n" % blob).encode()).stdout.decode().strip()
    c = g(d, "commit-tree", "-m", "attrs", tree).stdout.decode().strip()
    assert len(c) == 40, (tree, c)
    return c

def run_writer(d, cmd=("/bin/echo", "hi"), extra_cfg=()):
    rev = g(d, "rev-parse", "HEAD").stdout.decode().strip()
    outdir = tempfile.mkdtemp(prefix="out.", dir=S)
    out = os.path.join(outdir, "r.txt")
    argv = [sys.executable, "-B", WRITER, "--root", d, "--rev", rev, "--instrument", "tools/instr.sh",
            "--out", out, "--allow-outside", "--", *cmd]
    p = subprocess.run(argv, capture_output=True, text=True, env=GENV, timeout=300)
    rc, written = p.returncode, os.path.exists(out)
    shutil.rmtree(outdir, ignore_errors=True)
    return rc, written, (p.stderr.strip().splitlines() or [""])[-1][:170]

def py(code):
    return (sys.executable, "-c", code)

def forge(d, rel="tools/counter.py", body=b"counter v2\n", restore_mtime=False):
    p = os.path.join(d, rel)
    st = os.stat(p)
    open(p, "wb").write(body)
    if restore_mtime:
        os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))

def report(label, d, **kw):
    rc, written, err = run_writer(d, **kw)
    print(f"{label:44s} writer rc={rc} receipt={'WRITTEN' if written else 'none'} err={err!r}")

print("### W-series: candidate writer (a1db6c85) routes")

# W1: repo-local core.checkStat=minimal, PRE-RUN same-size forged + mtime restored
d = mk("w1"); g(d, "config", "core.checkStat", "minimal")
time.sleep(1.2); g(d, "status", "--porcelain")
forge(d, restore_mtime=True)
report("W1 checkStat=minimal pre-run forge", d)

# W2: same, IN-RUN forge by the wrapped command
d = mk("w2"); g(d, "config", "core.checkStat", "minimal")
time.sleep(1.2); g(d, "status", "--porcelain")
report("W2 checkStat=minimal in-run forge", d,
       cmd=py("import os;p='tools/counter.py';s=os.stat(p);open(p,'wb').write(b'counter v2\\n');"
              "os.utime(p,ns=(s.st_atime_ns,s.st_mtime_ns))"))

# W3: core.trustctime=false, pre-run
d = mk("w3"); g(d, "config", "core.trustctime", "false")
time.sleep(1.2); g(d, "status", "--porcelain")
forge(d, restore_mtime=True)
report("W3 trustctime=false pre-run forge", d)

# W4 control: no config
d = mk("w4"); forge(d, restore_mtime=True)
report("W4 control pre-run forge (no config)", d)

# W5: attr.tree naming a commit with filter=t + configured clean driver
d = mk("w5"); g(d, "config", "filter.t.clean", "sed s/v2/v1/")
g(d, "config", "attr.tree", attrtree(d, "tools/counter.py filter=t\n"))
forge(d)
report("W5 attr.tree filter + driver", d)

# W6: repo-local core.attributesFile with filter=t + driver
d = mk("w6"); g(d, "config", "filter.t.clean", "sed s/v2/v1/")
p = os.path.join(S, "w6-attrs-" + os.path.basename(d))
open(p, "w").write("tools/counter.py filter=t\n")
g(d, "config", "core.attributesFile", p)
forge(d)
report("W6 core.attributesFile filter + driver", d)

# W7: driver name with uppercase and a dot
for name, cfg in (("T", "filter.T.clean"), ("a.b", "filter.a.b.clean")):
    d = mk("w7" + name.replace(".", "_"))
    os.makedirs(os.path.join(d, ".git", "info"), exist_ok=True)
    open(os.path.join(d, ".git", "info", "attributes"), "w").write(f"tools/counter.py filter={name}\n")
    g(d, "config", cfg, "sed s/v2/v1/")
    forge(d)
    report(f"W7 driver name {name!r}", d)

# W8: in-run add driver + attribute + edit (expect post-run catch)
d = mk("w8")
code = ("import os,subprocess\n"
        "subprocess.run(['git','-C','.','config','filter.t.clean','sed s/v2/v1/'])\n"
        "os.makedirs('.git/info',exist_ok=True)\n"
        "open('.git/info/attributes','w').write('tools/counter.py filter=t\\n')\n"
        "open('tools/counter.py','wb').write(b'counter v2\\n')\n")
report("W8 in-run driver+attr+edit", d, cmd=py(code))

# W9: in-run add driver + attribute only (no edit)
d = mk("w9")
code = ("import os,subprocess\n"
        "subprocess.run(['git','-C','.','config','filter.t.clean','cat'])\n"
        "os.makedirs('.git/info',exist_ok=True)\n"
        "open('.git/info/attributes','w').write('tools/counter.py filter=t\\n')\n")
report("W9 in-run driver+attr, no edit", d, cmd=py(code))
