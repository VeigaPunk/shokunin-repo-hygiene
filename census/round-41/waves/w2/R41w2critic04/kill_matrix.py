import json, os, random, shutil, signal, stat, subprocess, sys, time

S = "/fast/scratch/hyaku/souji-r41/R41w2critic04"
FIX = S + "/fixture.py"
TOOL = S + "/tool.py"
SHIM = S + "/slow_tool.py"
BASE_ENV = {"PATH": os.environ["PATH"]}

with open(SHIM, "w") as f:
    f.write(
        "import os, sys, time\n"
        "time.sleep(float(os.environ.get('SHIM_SLEEP', '1.0')))\n"
        "os.execv(sys.executable, [sys.executable, '-B', %r] + sys.argv[1:])\n" % TOOL
    )


def modes(work):
    out = []
    for root, dirs, files in os.walk(work):
        for n in dirs + files:
            p = os.path.join(root, n)
            st = os.lstat(p)
            out.append("%s %s" % (oct(stat.S_IMODE(st.st_mode)), os.path.relpath(p, work)))
    return sorted(out)


def session_members(sid):
    out = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        try:
            with open("/proc/%s/stat" % name) as f:
                fields = f.read().rsplit(")", 1)[1].split()
            # fields[0]=state, fields[3]=session id
            if int(fields[3]) == sid and fields[0] != "Z":
                out.append(int(name))
        except (OSError, IndexError, ValueError):
            pass
    return out


def trial(sig, delay, sleep_s, tag):
    work = S + "/K-%s-%s-%s" % (tag, str(delay).replace(".", "p"), random.randrange(10 ** 6))
    os.makedirs(work)
    env = dict(BASE_ENV, SHIM_SLEEP=str(sleep_s))
    p = subprocess.Popen(
        ["python3", "-B", FIX, "--tool", SHIM, "--work", work],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        env=env, start_new_session=True,
    )
    time.sleep(delay)
    completed = p.poll() is not None
    if not completed:
        os.killpg(p.pid, sig)
    o, e = p.communicate(timeout=120)
    time.sleep(0.3)
    orphans = session_members(p.pid)
    if orphans:  # only our own session; clean up what we spawned
        for pid in orphans:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    left = modes(work) if os.path.exists(work) else ["<work gone>"]
    leftover_count = len(left)
    rm = subprocess.run(["rm", "-rf", work], capture_output=True, text=True)
    rm_ok = rm.returncode == 0 and not os.path.exists(work)
    py_rm = "n/a"
    if os.path.exists(work):
        try:
            shutil.rmtree(work)
            py_rm = "shutil ok"
        except Exception as ex:
            py_rm = "shutil fail: %r" % ex
    return dict(sig=signal.Signals(sig).name, delay=delay, completed_before_kill=completed,
                rc=p.returncode, leftover_count=leftover_count, leftover=left[:12],
                orphans_killed=orphans, rm_rf_ok=rm_ok, rm_rf_err=rm.stderr[-160:],
                py_rmtree_after_rm=py_rm, stderr_tail=e[-160:])


if __name__ == "__main__":
    res = []
    plan = [(signal.SIGKILL, d) for d in (0.3, 1.5, 4.5, 9.5)]
    plan += [(signal.SIGTERM, d) for d in (0.3, 1.5, 4.5, 9.5)]
    plan += [(signal.SIGINT, d) for d in (0.3, 1.5, 4.5, 9.5)]
    for sig, d in plan:
        res.append(trial(sig, d, 0.5, signal.Signals(sig).name))
    for _ in range(12):
        res.append(trial(signal.SIGKILL, round(random.uniform(0.0, 1.2), 2), 0.0, "RND"))
    with open(S + "/logs/kill-matrix.json", "w") as f:
        json.dump(res, f, indent=1)
    for r in res:
        print(json.dumps({k: r[k] for k in ("sig", "delay", "completed_before_kill", "rc",
                                            "leftover_count", "orphans_killed", "rm_rf_ok",
                                            "py_rmtree_after_rm")}))
    sample = [r for r in res if r["sig"] == "SIGKILL" and r["delay"] == 1.5][0]
    print("SAMPLE SIGKILL@1.5:", json.dumps(sample["leftover"]))
    sample = [r for r in res if r["sig"] == "SIGTERM" and r["delay"] == 1.5][0]
    print("SAMPLE SIGTERM@1.5:", json.dumps(sample["leftover"]))
    sample = [r for r in res if r["sig"] == "SIGINT" and r["delay"] == 1.5][0]
    print("SAMPLE SIGINT@1.5:", json.dumps(sample["leftover"]))
