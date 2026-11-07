#!/usr/bin/env python3
"""S80MutTool probe for M09: is the handler's `rm -rf -- "$q_front_tmp"` redundant because the EXIT trap
removes the same private dir?  Same row shape as the frozen counter (file-digest hang point, TERM), but the
private TMPDIR is listed while the tool is blocked and again after it exits."""
import importlib.util
import os
import signal
import subprocess
import sys
import time

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
spec = importlib.util.spec_from_file_location(
    "c2c", os.path.join(LANE, "census", "round-80", "c2-signal-counter.py"))
c2c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c2c)


def probe(tool, label, work):
    rowdir = os.path.join(work, "row-" + label)
    os.makedirs(rowdir)
    fleet, repo, ledger, target = c2c.build(rowdir, "file")
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    nonce = "m09" + label
    mark = os.path.join(rowdir, "hang.mark")
    shimdir = os.path.join(rowdir, "shim")
    stubs = c2c.make_shims(shimdir)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_"))}
    env.update({"PATH": shimdir + os.pathsep + os.environ["PATH"], "TMPDIR": tmpdir, "LC_ALL": "C",
                "SOUJI_R80_NONCE": nonce, "SOUJI_R80_MARK": mark, "SOUJI_R80_TARGET": target,
                "SOUJI_VERIFY_BIN": stubs["hang"], "SOUJI_Q_SHOKUNIN_ROOT": fleet, "SOUJI_Q_LEDGER": ledger,
                "SOUJI_R80_POINT": "file-digest", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    outp = os.path.join(rowdir, "tool.out")
    with open(outp, "wb") as fo:
        p = subprocess.Popen(["bash", tool, "--dry-run", repo, target], stdout=fo, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, env=env, start_new_session=True, cwd=rowdir,
                             preexec_fn=c2c._preexec)
    t0 = time.monotonic()
    while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < 60:
        time.sleep(0.05)
    if not os.path.exists(mark):
        print(f"M09PROBE {label} ERROR no mark")
        c2c.reap(nonce)
        return
    during = sorted(os.listdir(tmpdir))
    os.kill(p.pid, signal.SIGTERM)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass
    time.sleep(0.2)
    after = sorted(os.listdir(tmpdir))
    out = open(outp, encoding="utf-8", errors="replace").read()
    print(f"M09PROBE {label} during={during} after={after} rc={p.returncode} "
          f"signal_line={'y' if 'SIGNAL\tSIGTERM\tRECEIPT-QUARANTINE-SIGNALED' in out.splitlines() else 'n'}")
    c2c.reap(nonce)
    if p.poll() is None:
        p.kill()
    p.wait()


def main():
    work = os.path.abspath(sys.argv[1])
    os.makedirs(work, exist_ok=True)
    S = "/fast/scratch/hyaku/souji-r80/S80MutTool"
    for label, tool in (("pristine", os.path.join(S, "base", "souji-quarantine.sh")),
                        ("M09", os.path.join(S, "mut", "M09-no-rmrf-in-handler", "souji-quarantine.sh"))):
        probe(tool, label, work)
    return 0


if __name__ == "__main__":
    sys.exit(main())
