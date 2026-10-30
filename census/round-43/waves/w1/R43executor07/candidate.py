#!/usr/bin/env python3
"""r43 drift survivor behavioral checks. Each case runs the pinned tool in an isolated scene."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROW = "REPO\tr\tregs=1\tprunable=0\n"

class Context:
    def __init__(self, tool, work):
        self.tool, self.work = tool, work
        self.env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work,
                    "LC_ALL": "C", "HOME": work, "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                    "GIT_TERMINAL_PROMPT": "0"}
    def scene(self, name):
        base = os.path.join(self.work, name)
        root, out = os.path.join(base, "root"), os.path.join(base, "out")
        os.makedirs(root); os.makedirs(out)
        self.init(os.path.join(root, "r"))
        return base, root, out
    def init(self, path, bare=False):
        subprocess.run(["git", "init", "-q"] + (["--bare"] if bare else []) + [path],
                       env=self.env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    def run(self, args, timeout=60, cwd=None):
        try:
            return subprocess.run([sys.executable, "-B", self.tool] + args, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=self.env, timeout=timeout, cwd=cwd or self.work)
        except subprocess.TimeoutExpired:
            return None

def put(path, data):
    with open(path, "wb") as f: f.write(data if isinstance(data, bytes) else data.encode())
    return path

def drift(p, token):
    return p is not None and p.returncode == 1 and token in p.stdout.decode("utf-8", "replace")
def refuse(p, token):
    return p is not None and p.returncode == 2 and ("REFUSAL " + token + ":") in p.stderr.decode("utf-8", "replace")

def case_fifo_record_is_refused_not_blocked(c):
    _, root, out = c.scene("fifo-record"); os.mkfifo(out + "/record")
    return refuse(c.run(["--root", root, "--record", out + "/record", "--skip-unrecorded"], 25), "RECORD-MALFORMED")
def case_root_sibling_prefix_is_outside(c):
    _, root, out = c.scene("root-sibling"); rec = put(out+"/rec", "REPO\t../root2\tregs=1\tprunable=0\n")
    return refuse(c.run(["--root",root,"--record",rec,"--skip-unrecorded"]),"RECORD-OUTSIDE-ROOT")
def case_gitdir_sibling_prefix_is_outside(c):
    w, root, out = c.scene("gitdir-sibling"); os.makedirs(w+"/rootX"); c.init(w+"/rootX/gd2",True)
    os.makedirs(root+"/s"); put(root+"/s/.git", "gitdir: "+w+"/rootX/gd2\n")
    rec=put(out+"/rec","REPO\ts\tregs=1\tprunable=0\n")
    return refuse(c.run(["--root",root,"--record",rec,"--skip-unrecorded"]),"RECORD-OUTSIDE-ROOT")
def case_timeout_of_one_is_accepted(c):
    _,root,out=c.scene("timeout-one"); rec=put(out+"/rec","REPO\ta\tregs=1\tprunable=0\n")
    return drift(c.run(["--root",root,"--record",rec,"--skip-unrecorded","--timeout","1"]),"DRIFT\tABSENT\ta")
def blocked(c,name):
    _,root,out=c.scene(name); c.init(root+"/t"); os.remove(root+"/t/.git/HEAD"); os.mkfifo(root+"/t/.git/HEAD")
    return root,put(out+"/rec","REPO\tt\tregs=1\tprunable=0\n")
def case_default_timeout_outlasts_a_blocked_git(c):
    root,rec=blocked(c,"default-timeout"); t=time.monotonic()
    p=c.run(["--root",root,"--record",rec,"--skip-unrecorded"],100)
    return drift(p,"DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout") and time.monotonic()-t>=5
def case_list_timeout_is_reported_unreachable(c):
    root,rec=blocked(c,"list-timeout")
    return drift(c.run(["--root",root,"--record",rec,"--skip-unrecorded","--timeout","1"],60),"DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout")
def case_list_nonzero_rc_is_reported_unreachable(c):
    _,root,out=c.scene("list-rc"); os.makedirs(root+"/u/.git"); rec=put(out+"/rec","REPO\tu\tregs=1\tprunable=0\n")
    return drift(c.run(["--root",root,"--record",rec,"--skip-unrecorded"]),"DRIFT\tUNREACHABLE\tu\tUNREACHABLE:list-rc=")
def case_root_option_is_required(c):
    _,_,out=c.scene("root-required"); rec=put(out+"/rec",ROW); p=c.run(["--record",rec],cwd=out)
    return p is not None and p.returncode==2 and b"required" in p.stderr
def case_record_option_is_required(c):
    _,root,_=c.scene("record-required"); p=c.run(["--root",root])
    return p is not None and p.returncode==2 and b"required" in p.stderr
def case_symlinked_child_is_not_discovered(c):
    _,root,out=c.scene("symlink-child"); c.init(root+"/u2"); os.symlink(root+"/u2",root+"/lnk"); rec=put(out+"/rec",ROW)
    p=c.run(["--root",root,"--record",rec]); text=p.stdout.decode("utf-8","replace") if p else ""
    return drift(p,"DRIFT\tUNRECORDED\tu2") and "UNRECORDED\tlnk" not in text
def case_two_digit_regs_are_read_whole(c):
    _,root,out=c.scene("two-digit-regs"); rec=put(out+"/rec","REPO\tr\tregs=10\tprunable=0\n")
    return drift(c.run(["--root",root,"--record",rec,"--skip-unrecorded"]),"record=10 live=1")
def case_longer_old_json_is_truncated_on_write(c):
    _,root,out=c.scene("json-truncate"); rec=put(out+"/rec",ROW); target=put(out+"/old.json",b"x"*5000)
    p=c.run(["--root",root,"--record",rec,"--skip-unrecorded","--json",target])
    if p is None or p.returncode: return False
    try:
        with open(target,encoding="utf-8") as f: data=json.load(f)
    except (OSError,ValueError): return False
    return data.get("drift")==[] and "summary" in data
def case_invalid_utf8_in_record_becomes_replacement_char(c):
    _,root,out=c.scene("invalid-utf8"); rec=put(out+"/rec",b"REPO\ta\xffb\tregs=1\tprunable=0\n"); target=out+"/o.json"
    p=c.run(["--root",root,"--record",rec,"--skip-unrecorded","--json",target])
    if p is None or p.returncode!=1 or b"DRIFT\tABSENT\ta\xef\xbf\xbdb\t" not in p.stdout: return False
    try:
        with open(target,encoding="utf-8") as f: data=json.load(f)
    except (OSError,ValueError): return False
    return [r.get("repo") for r in data.get("drift",[])]==["a\ufffdb"]
def case_json_symlink_leaf(c):
    _,root,out=c.scene("json-symlink-leaf"); rec=put(out+"/rec",ROW); victim=put(out+"/victim",b"untouched")
    target=out+"/report.json"; os.symlink(victim,target)
    p=c.run(["--root",root,"--record",rec,"--skip-unrecorded","--json",target])
    return refuse(p,"JSON-TARGET-SYMLINK") and open(victim,"rb").read()==b"untouched" and os.path.islink(target)

CASES=[(name[5:].replace("_","-"),fn) for name,fn in sorted(globals().items()) if name.startswith("case_") and callable(fn)]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--tool",required=True); ap.add_argument("--work",required=True); a=ap.parse_args()
    if os.geteuid()==0: sys.stderr.write("r43-drift-survivors: refusing to run as root\n"); return 2
    work=os.path.realpath(tempfile.mkdtemp(prefix="r43ds.",dir=a.work)); c=Context(os.path.realpath(a.tool),work); bad=0
    try:
        for name,fn in CASES:
            try: ok=bool(fn(c))
            except Exception as exc: ok=False; sys.stderr.write("case-%s: %s: %s\n"%(name,type(exc).__name__,exc))
            bad+=not ok; print("case-%s=%s"%(name,"PASS" if ok else "FAIL"),flush=True)
        print("SUMMARY cases=%d pass=%d fail=%d"%(len(CASES),len(CASES)-bad,bad)); return 1 if bad else 0
    finally: shutil.rmtree(work,ignore_errors=True)
sys.exit(main())
