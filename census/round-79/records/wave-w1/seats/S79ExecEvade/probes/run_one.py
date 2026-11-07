#!/usr/bin/env python3
"""S79ExecEvade probe runner: launch a gate revision on a scratch fixture,
deliver timed signals to the gate pid ONLY, verify claim invariants.
Usage: run_one.py CASE SPEC GATE SHIMDIR FIXTURE
Knobs (env): SHIM_PRE_SLEEP SHIM_AWK_SLEEP SHIM_REALPATH_SLEEP SHIM_ESCAPE
             SHIM_PAYLOAD SHIM_LOG R79_TMPDIR(DEFAULT|UNSET|path) R79_HOME(DEFAULT|UNSET|path)
             R79_ULIMIT(nproc)
Prints one JSON line with: exit, exit_ms, check_signal_lines, receipt, checks,
survivors, leftover_tmp.
"""
import glob, json, os, signal, subprocess, sys, time


def pre():
    for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, signal.SIG_DFL)
    os.setsid()


def scan(mark, exclude):
    found = []
    pat = ("SHIM_MARK=" + mark).encode()
    for d in glob.glob("/proc/[0-9]*"):
        try:
            pid = int(d.rsplit("/", 1)[1])
            if pid in exclude:
                continue
            if pat not in open(d + "/environ", "rb").read():
                continue
            cmd = open(d + "/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace").strip()
            found.append([pid, cmd])
        except OSError:
            continue
    return found


def main():
    case, spec, gate, shimdir, fx = sys.argv[1:6]
    case = os.path.abspath(case)
    os.makedirs(case, exist_ok=True)
    res = {"case": os.path.basename(case), "gate": os.path.basename(gate)}
    env = dict(os.environ)
    env["SHIM_MARK"] = case
    tmpdir = env.pop("R79_TMPDIR", "DEFAULT")
    home = env.pop("R79_HOME", "DEFAULT")
    ulim = env.pop("R79_ULIMIT", "")
    if tmpdir == "UNSET":
        env.pop("TMPDIR", None); tdir = "/tmp"
    elif tmpdir == "DEFAULT":
        tdir = env.get("TMPDIR", "/tmp")
    else:
        env["TMPDIR"] = tmpdir; tdir = tmpdir
    if home == "UNSET":
        env.pop("HOME", None)
    elif home != "DEFAULT":
        env["HOME"] = home
    if shimdir != "-":
        env["PATH"] = shimdir + ":" + env["PATH"]
    sigs = []
    for part in filter(None, spec.split(",")):
        s, t = part.split("@")
        sigs.append((getattr(signal, "SIG" + s), float(t)))
    pre_existing = set(glob.glob(tdir + "/souji-gate.*"))
    cmd = ["bash", "-c", ("ulimit -u %s 2>/dev/null; " % ulim if ulim else "") + 'exec bash "$@"', "--",
           gate, "--lane", fx + "/repo", "--branch", "master",
           "--report", fx + "/report.md", "--prereg", fx + "/prereg.txt"]
    t0 = time.time()
    with open(case + "/gate.out", "wb") as fo, open(case + "/gate.err", "wb") as fe:
        p = subprocess.Popen(cmd, env=env, stdin=subprocess.DEVNULL, stdout=fo, stderr=fe,
                             preexec_fn=pre, cwd=case)
        first = None
        for s, t in sigs:
            d = t0 + t - time.time()
            if d > 0:
                time.sleep(d)
            if first is None:
                first = time.time()
            try:
                os.kill(p.pid, s)
            except ProcessLookupError:
                pass
        deadline = (first + 6.5) if first else (t0 + 300.0)
        while time.time() < deadline and p.poll() is None:
            time.sleep(0.002)
        res["exit_ms"] = round((time.time() - t0) * 1000)
        if p.poll() is None:
            res["exit"] = "NO-EXIT-BY-DEADLINE"
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            p.wait()
        else:
            res["exit"] = p.returncode
    time.sleep(0.3)
    res["survivors"] = scan(case, {p.pid, os.getpid()})
    for pid, _c in res["survivors"]:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    res["leftover_tmp"] = [d for d in glob.glob(tdir + "/souji-gate.*") if d not in pre_existing]
    for d in res["leftover_tmp"]:
        try:
            os.rmdir(d)
        except OSError:
            pass
    out = open(case + "/gate.out", errors="replace").read()
    err = open(case + "/gate.err", errors="replace").read()
    res["check_signal_lines"] = out.count("check-signal=FAIL")
    res["receipt"] = "RECEIPT-GATE-SIGNALED" in err
    res["checks"] = [l for l in out.splitlines() if l.startswith("check-")]
    print(json.dumps(res))


main()
