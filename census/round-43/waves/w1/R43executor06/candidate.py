#!/usr/bin/env python3
"""Behavioral survivor battery for souji-worktree-drift.py."""
import argparse
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def run(tool, work, scene, args, timeout=25, cwd=None):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work}
    env.update(GIT_ENV)
    return subprocess.run([sys.executable, "-B", tool] + args, cwd=cwd or scene,
                          env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=timeout, check=False)


def init_repo(path, work):
    os.makedirs(path, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work}
    env.update(GIT_ENV)
    p = subprocess.run(["git", "-C", path, "init", "-q"], env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError("git init failed: " + p.stderr.decode("utf-8", "replace"))


def record(path, rows, total=True):
    body = ["REPO\t%s\tregs=%d\tprunable=%d" % row for row in rows]
    if total:
        body.append("TOTAL\trepos=%d\tregs=%d\tprunable=%d" %
                    (len(rows), sum(r[1] for r in rows), sum(r[2] for r in rows)))
    pathlib.Path(path).write_text("\n".join(body) + "\n", encoding="utf-8")


def case(name, base, work, tool):
    scene = tempfile.mkdtemp(prefix="scene-", dir=work)
    try:
        root = os.path.join(scene, "root")
        os.mkdir(root)
        rec = os.path.join(scene, "record.tsv")
        def invoke(extra=(), timeout=25, cwd=None):
            return run(tool, work, scene, ["--root", root, "--record", rec] + list(extra), timeout, cwd)
        def expect(p, rc=None, out=(), err=(), absent_out=(), no_trace=False):
            stdout, stderr = p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")
            return ((rc is None or p.returncode == rc) and all(x in stdout for x in out)
                    and all(x in stderr for x in err) and all(x not in stdout for x in absent_out)
                    and (not no_trace or "Traceback" not in stderr))
        if name == "big-record-fully-parsed":
            rows=[]
            for i in range(3000):
                n="repo-%04d" % i; init_repo(os.path.join(root,n), work); rows.append((n,1,0))
            record(rec, rows)
            p=invoke(timeout=50)
            return expect(p, 0) and len(pathlib.Path(rec).read_bytes()) > 65536
        if name == "total-trailing-junk-refused":
            record(rec, [("absent",1,0)])
            with open(rec,"a") as f: f.write("TOTAL\trepos=1\tregs=1\tprunable=0JUNK\n")
            return expect(invoke(), 2, err=("RECORD-MALFORMED",))
        if name == "repo-name-with-space":
            name="repo with space"; init_repo(os.path.join(root,name),work); record(rec,[(name,1,0)])
            p=invoke(); return expect(p, 1, out=("UNREACHABLE",)) or expect(p,0)
        if name == "empty-regs-refused":
            pathlib.Path(rec).write_text("REPO\tx\tregs=\tprunable=0\n")
            return expect(invoke(),2,err=("RECORD-MALFORMED",))
        if name == "total-prunable-below-rows-refused":
            record(rec,[("x",1,1)])
            with open(rec,"a") as f: f.write("TOTAL\trepos=1\tregs=1\tprunable=0\n")
            return expect(invoke(),2,err=("RECORD-MALFORMED",))
        if name == "root-named-not-a-repo":
            root=os.path.join(scene,"namedrepo"); os.mkdir(root); rec=os.path.join(scene,"r.tsv")
            record(rec,[("namedrepo",1,0)])
            return expect(run(tool,work,scene,["--root",root,"--record",rec]),1,out=("ABSENT",))
        if name == "unreadable-root-listed-absent":
            init_repo(os.path.join(root,"missing"),work); record(rec,[("missing",1,0)])
            os.chmod(root,0)
            try:
                p=invoke(); return expect(p,1,out=("ABSENT",),no_trace=True)
            finally: os.chmod(root,0o755)
        if name == "symlinked-root-measured":
            actual=os.path.join(scene,"actual"); os.mkdir(actual); init_repo(os.path.join(actual,"r"),work)
            os.rmdir(root); os.symlink(actual,root); record(rec,[("r",1,0)])
            return expect(invoke(),0)
        if name == "relative-root-basename":
            os.rename(root,os.path.join(scene,"namedrepo")); root=os.path.join(scene,"namedrepo")
            init_repo(root,work); record(rec,[("namedrepo",1,0)])
            return expect(run(tool,work,scene,["--root",".","--record",rec],cwd=root),0)
        if name == "gitdir-probe-honors-timeout":
            repo=os.path.join(root,"slow"); os.mkdir(repo); gitdir=os.path.join(repo,".git"); os.mkdir(gitdir)
            os.mkfifo(os.path.join(gitdir,"HEAD")); record(rec,[("slow",1,0)])
            start=time.monotonic(); p=invoke(("--timeout","1"),timeout=12)
            return time.monotonic()-start < 12 and expect(p,1,out=("UNREACHABLE",),no_trace=True)
        if name == "regs-rise-reported":
            repo=os.path.join(root,"r"); init_repo(repo,work)
            env={"PATH":os.environ.get("PATH","/usr/bin:/bin"),"TMPDIR":work}; env.update(GIT_ENV)
            subprocess.run(["git","-C",repo,"-c","user.name=Fixture","-c","user.email=fixture@example.invalid","commit","--allow-empty","-m","base"],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            for i in range(2):
                subprocess.run(["git","-C",repo,"worktree","add","--detach",os.path.join(scene,"wt%d"%i)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            record(rec,[("r",1,0)])
            return expect(invoke(),1,out=("REGS-CHANGED",))
        if name == "prunable-fall-reported":
            init_repo(os.path.join(root,"r"),work); record(rec,[("r",1,1)])
            return expect(invoke(),1,out=("PRUNABLE-CHANGED",))
        if name == "json-sibling-prefix-written":
            init_repo(os.path.join(root,"r"),work); record(rec,[("r",1,0)])
            sibling=root+"X"; os.mkdir(sibling); target=os.path.join(sibling,"out.json")
            p=invoke(("--json",target)); return expect(p,0) and os.path.isfile(target)
        if name == "json-created-mode":
            init_repo(os.path.join(root,"r"),work); record(rec,[("r",1,0)])
            target=os.path.join(scene,"out.json"); old=os.umask(0o022)
            try: p=invoke(("--json",target))
            finally: os.umask(old)
            return expect(p,0) and stat.S_IMODE(os.stat(target).st_mode)==0o644
        if name == "json-empty-string-ignored":
            record(rec,[("absent",1,0)])
            return expect(invoke(("--json","")),1,out=("ABSENT",))
        if name == "timeout-float-refused":
            return expect(invoke(("--timeout","1.5")),2,err=("usage:",))
        if name == "json-symlink-leaf-refused":
            init_repo(os.path.join(root,"r"),work); record(rec,[("r",1,0)])
            real=os.path.join(scene,"real.json"); pathlib.Path(real).write_text("keep")
            link=os.path.join(scene,"link.json"); os.symlink(real,link)
            return expect(invoke(("--json",link)),2,err=("REFUSAL JSON-TARGET-SYMLINK:",)) and pathlib.Path(real).read_text()=="keep"
        raise ValueError(name)
    finally:
        shutil.rmtree(scene,ignore_errors=True)


def main(argv):
    ap=argparse.ArgumentParser(); ap.add_argument("--tool",required=True); ap.add_argument("--work",required=True)
    ns=ap.parse_args(argv); os.makedirs(ns.work,exist_ok=True); os.umask(0o022)
    cases=["big-record-fully-parsed","total-trailing-junk-refused","repo-name-with-space","empty-regs-refused",
    "total-prunable-below-rows-refused","root-named-not-a-repo","unreadable-root-listed-absent","symlinked-root-measured",
    "relative-root-basename","gitdir-probe-honors-timeout","regs-rise-reported","prunable-fall-reported",
    "json-sibling-prefix-written","json-created-mode","json-empty-string-ignored","timeout-float-refused","json-symlink-leaf-refused"]
    passed=0
    for name in cases:
        try: ok=case(name,os.path.abspath(ns.work),os.path.abspath(ns.work),os.path.abspath(ns.tool))
        except Exception: ok=False
        print("case-%s=%s"%(name,"PASS" if ok else "FAIL")); passed+=int(ok)
    failed=len(cases)-passed; print("SUMMARY cases=%d pass=%d fail=%d"%(len(cases),passed,failed))
    return 0 if failed==0 else 1

if __name__=="__main__": sys.exit(main(sys.argv[1:]))
