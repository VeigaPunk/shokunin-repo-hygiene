import importlib.util, subprocess, os, sys, tempfile, shutil, concurrent.futures
L = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "b7408095543579ac71b33ecf7b80b0cb8ef45036"
S = "/fast/scratch/hyaku/souji-r42/R42critic06/exp"
spec = importlib.util.spec_from_file_location("c3", L + "/census/round-42/c3-counter.py")
c3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c3)
src = subprocess.run(["git", "-C", L, "show", REV + ":tools/souji-worktree-drift.py"], capture_output=True).stdout.decode()
wd = tempfile.mkdtemp(prefix="pvm.", dir=S)
try:
    fx = {}
    for p in c3.PRIOR:
        b = subprocess.run(["git", "-C", L, "show", REV + ":" + p], capture_output=True).stdout
        f = os.path.join(wd, "fx-" + os.path.basename(p)); open(f, "wb").write(b); fx[p] = f
    muts = {}
    for mid, _d, old, new in c3.MUTANTS + c3.EQUIV:
        assert src.count(old) == 1, mid
        m = os.path.join(wd, "mut-%s.py" % mid); open(m, "w").write(src.replace(old, new)); muts[mid] = m
    def run(p, mid):
        work = tempfile.mkdtemp(prefix="w-", dir=wd)
        e = c3.env(S); e["TMPDIR"] = work
        try:
            pr = subprocess.run(["python3", "-B", fx[p], "--tool", muts[mid], "--work", work], capture_output=True,
                                text=True, timeout=120, env=e)
            m = c3.SUMMARY_RE.findall(pr.stdout)
            crash = "Traceback (most recent call last)" in pr.stderr
            cls = "KILL" if (m and pr.returncode == 1 and int(m[-1][2]) > 0 and not crash) else "NOT-KILL"
            return "%-4s %-34s rc=%-7s summary=%-12s crash=%-5s %s" % (mid, os.path.basename(p), pr.returncode,
                   ("%s/%s/%s" % m[-1]) if m else "none", crash, cls)
        except subprocess.TimeoutExpired:
            return "%-4s %-34s rc=TIMEOUT summary=none crash=True NOT-KILL(timeout)" % (mid, os.path.basename(p))
        finally:
            shutil.rmtree(work, ignore_errors=True)
    jobs = [(p, mid) for mid in muts for p in c3.PRIOR]
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        out = list(ex.map(lambda a: run(*a), jobs))
    for line in out:
        if "NOT-KILL" not in line or "crash=True" in line or "TIMEOUT" in line or "none" in line:
            print(line)
    print("TOTAL_RUNS=%d" % len(out))
    print("NOT_KILL_CLEAN=%d" % sum(1 for l in out if "NOT-KILL" in l and "crash=False" in l and "none" not in l))
    print("NOT_KILL_CRASH_OR_TIMEOUT_OR_NOSUMMARY=%d" % sum(1 for l in out if "NOT-KILL" in l and ("crash=True" in l or "none" in l)))
    print("KILLS=%d" % sum(1 for l in out if l.endswith("KILL")))
finally:
    shutil.rmtree(wd, ignore_errors=True)
