import os, subprocess, sys, time
LANE="/home/vgpnk/Projects/shokunin/souji-shokunin"
SNAP=("/tmp","/var/tmp","/dev/shm")
def snap():
    out={}
    for r in SNAP:
        try:
            for n in os.listdir(r):
                p=os.path.join(r,n)
                try: out[p]=os.stat(p).st_mtime
                except OSError: pass
        except OSError: pass
    return out
def audit(label, cmd, cwd=LANE, env=None):
    e=dict(os.environ); e.update(env or {})
    b=snap(); t0=time.time()
    p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=e, timeout=900)
    a=snap()
    new=sorted(set(a)-set(b)); changed=sorted(k for k in set(a)&set(b) if a[k]!=b[k])
    print(f"[{label}] rc={p.returncode} new_tmp_entries={new} modified_tmp_entries={changed}")
    for k in new+changed:
        try:
            for dp,_d,fs in os.walk(k):
                for f in fs:
                    fp=os.path.join(dp,f)
                    if os.stat(fp).st_mtime>=t0-10: print("    NEW/CHANGED FILE:",fp)
        except OSError: pass
    return p
tmpd="/fast/scratch/hyaku/souji-r95/R95Sentinel/tmpdir"; os.makedirs(tmpd,exist_ok=True)
# C2 arms counter with a private TMPDIR
w="/fast/scratch/hyaku/souji-r95/R95Sentinel/e21arms"; subprocess.run(["rm","-rf",w]); os.makedirs(w)
audit("C2-arms", ["python3","-B","census/round-95/c2-setup-arms.py","--probe","census/round-95/c2-forgery-probe.py",
  "--fixture-pass","tests/fixtures/r93-k4-flagfail.py","--fixture-fail","tests/fixtures/r92-k4-flagfail.py",
  "--tool","tools/souji-record-agreement.py","--before","census/round-92/controls/c2-before-tool.py","--work",w],
  env={"TMPDIR":tmpd})
print("   S13 /tmp path present after the run:", [n for n in os.listdir("/tmp") if n.startswith("souji-r95-arm-S13")])
