#!/usr/bin/env python3
"""DETERMINISTIC in-run filter route: the clean driver deletes its own attribute while `git status`
is running. post_st still says clean; the writer's post-run check-attr then sees nothing."""
import os, shutil, subprocess, sys, tempfile

S = "/fast/scratch/hyaku/souji-r71/S71Sentinel"
WRITER = os.path.join(S, "cand-writer.py")
GENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
GENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
            GIT_AUTHOR_DATE="2026-11-06T12:00:00Z", GIT_COMMITTER_DATE="2026-11-06T12:00:00Z")

def g(d, *a, inp=None):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, input=inp, env=GENV)

def mk(name):
    d = tempfile.mkdtemp(prefix=name + ".", dir=S)
    assert d and os.path.isdir(d), d
    g(d, "init", "-q")
    assert os.path.realpath(g(d, "rev-parse", "--show-toplevel").stdout.decode().strip()) == os.path.realpath(d)
    g(d, "config", "user.name", "probe"); g(d, "config", "user.email", "probe@invalid")
    os.makedirs(os.path.join(d, "tools"), exist_ok=True)
    open(os.path.join(d, "tools", "counter.py"), "wb").write(b"counter v1\n")
    open(os.path.join(d, "tools", "instr.sh"), "wb").write(b"#!/bin/sh\necho ok\n")
    os.chmod(os.path.join(d, "tools", "instr.sh"), 0o755)
    g(d, "add", "-A"); g(d, "commit", "-qm", "seed")
    return d

def status(d):
    r = g(d, "-c", "status.showUntrackedFiles=all", "status", "--porcelain")
    return r.stdout.decode().replace("\n", " ").strip() or "(clean)"

def run_writer(d, cmd):
    rev = g(d, "rev-parse", "HEAD").stdout.decode().strip()
    outdir = tempfile.mkdtemp(prefix="out.", dir=S)
    out = os.path.join(outdir, "r.txt")
    p = subprocess.run([sys.executable, "-B", WRITER, "--root", d, "--rev", rev, "--instrument",
                        "tools/instr.sh", "--out", out, "--allow-outside", "--", *cmd],
                       capture_output=True, text=True, env=GENV, timeout=300)
    body = open(out, "rb").read() if os.path.exists(out) else b""
    shutil.rmtree(outdir, ignore_errors=True)
    return p.returncode, bool(body), (p.stderr.strip().splitlines() or [""])[-1][:200], body

d = mk("toctou")
attr = os.path.join(d, ".git", "info", "attributes")
os.makedirs(os.path.dirname(attr), exist_ok=True)
# the clean driver: map v2 -> v1 for the hash, then delete the attribute file it was selected by
filt = os.path.join(S, "selfunlink-filter.py")
open(filt, "w").write(
    "import os,sys\n"
    "data=sys.stdin.buffer.read()\n"
    "sys.stdout.buffer.write(data.replace(b'counter v2',b'counter v1'))\n"
    "sys.stdout.buffer.flush()\n"
    f"try: os.unlink({attr!r})\n"
    "except OSError: pass\n")
g(d, "config", "filter.t.clean", f"{sys.executable} {filt}")

code = ("import os\n"
        f"open({attr!r},'w').write('tools/counter.py filter=t\\n')\n"
        f"open({os.path.join(d,'tools','counter.py')!r},'wb').write(b'counter v2\\n')\n")
rc, written, err, body = run_writer(d, (sys.executable, "-c", code))
print(f"T1 self-unlinking clean filter: writer rc={rc} receipt={'WRITTEN' if written else 'none'}")
print(f"   refusal={err!r}")
print(f"   receipt EXIT line={[l for l in body.decode(errors='replace').splitlines() if l.startswith('EXIT=')]}")
print(f"   attr exists after run={os.path.exists(attr)}")
print(f"   FINAL git status={status(d)!r}   (worktree vs index)")
print(f"   file bytes={open(os.path.join(d,'tools','counter.py'),'rb').read()!r} head blob="
      f"{g(d,'cat-file','blob','HEAD:tools/counter.py').stdout!r}")
