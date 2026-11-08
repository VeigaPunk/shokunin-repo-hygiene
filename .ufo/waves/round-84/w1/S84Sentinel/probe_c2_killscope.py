#!/usr/bin/env python3
"""S84Sentinel C2 kill-scope ground truth: strace the tool's abort path and report EVERY pid it signals.

This is the direct answer to "can the C2 repair be made to signal a process it should not?":
  * strace -f -e trace=kill on the tool, so every kill(2) the tool issues is recorded with its target pid;
  * the fixture records the CLI's own pid, so the descendant set is known exactly;
  * a canary process (owned here, NOT a descendant) logs every signal it receives.

A signal delivered to a pid outside the CLI's descendant set is a CRITICAL by the r84 kill rule.

Usage: probe_c2_killscope.py --tool <tool.sh> --work <empty dir> [--case nlcomm|plain|setsid2]
"""
import argparse
import hashlib
import os
import re
import shutil
import signal
import subprocess
import sys
import time

SETTLE = 5.0

STUBS = {
    # a CLI whose own /proc/<pid>/stat comm holds a NEWLINE and ')'
    "nlcomm": r'''#!/usr/bin/env python3
import ctypes, os, signal, sys, time
libc = ctypes.CDLL("libc.so.6", use_errno=True)
libc.prctl(15, b"a\nb)c", 0, 0, 0)
def term(*a):
    with open(os.environ["S84_MARK"], "a") as f:
        f.write("got-signal\n")
    os._exit(0)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s ppid=%s pgid=%s sid=%s\n" % (os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0)))
while True:
    time.sleep(0.2)
''',
    # an ordinary CLI that ignores nothing and dies on TERM
    "plain": r'''#!/usr/bin/env python3
import os, signal, sys, time
def term(*a):
    with open(os.environ["S84_MARK"], "a") as f:
        f.write("got-signal\n")
    os._exit(0)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s ppid=%s pgid=%s sid=%s\n" % (os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0)))
while True:
    time.sleep(0.2)
''',
    # a CLI with a child that setsids 0.35 s later (after the first map pass)
    "setsid2": r'''#!/usr/bin/env python3
import os, signal, sys, time
pid = os.fork()
if pid == 0:
    time.sleep(0.35)
    os.setsid()
    while True:
        time.sleep(0.3)
def term(*a):
    os._exit(0)
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    signal.signal(s, term)
with open(os.environ["S84_MARK"], "w") as f:
    f.write("ready pid=%s ppid=%s pgid=%s sid=%s\n" % (os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0)))
while True:
    time.sleep(0.2)
''',
}

CANARY = r'''#!/usr/bin/env python3
import os, signal, sys, time
log = os.environ["S84_CANARY_LOG"]
def note(s):
    with open(log, "a") as f:
        f.write(s + "\n")
for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT, signal.SIGSTOP):
    try:
        signal.signal(s, lambda n, f: note("sig%d" % n))
    except (OSError, ValueError):
        pass
note("start")
open(os.environ["S84_CANARY_READY"], "w").write("ready\n")
while True:
    time.sleep(0.1)
'''


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def build(d):
    src, vault, fleet, tmp = (os.path.join(d, x) for x in ("src", "vault", "fleet", "tmp"))
    for x in (src, vault, fleet, tmp):
        os.makedirs(x)
    s, v = os.path.join(src, "a-src.md"), os.path.join(vault, "a-vlt.md")
    for p in (s, v):
        with open(p, "w", encoding="utf-8") as f:
            f.write("r84 sentinel killscope payload\n")
    h = sha(s)
    led = os.path.join(d, "ledger.tsv")
    with open(led, "w", encoding="utf-8") as f:
        f.write("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n")
        f.write(f"{s}\t{h}\t{v}\t{h}\t2026-11-07\tr84-sentinel\n")
    return s, led, tmp


def descendants(root):
    """The pid set the tool's descendant walk could see: root plus every pid whose /proc ppid chain reaches root."""
    kids = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            with open(f"/proc/{d}/stat", "rb") as f:
                data = f.read()
        except OSError:
            continue
        try:
            rest = data.rsplit(b")", 1)[1].split()
            ppid = int(rest[1])
        except (IndexError, ValueError):
            continue
        kids.setdefault(ppid, []).append(int(d))
    out, stack = {int(root)}, [int(root)]
    while stack:
        cur = stack.pop()
        for k in kids.get(cur, []):
            if k not in out:
                out.add(k)
                stack.append(k)
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--case", default="nlcomm", choices=sorted(STUBS))
    ns = ap.parse_args(argv)
    tool = os.path.abspath(ns.tool)
    work = os.path.abspath(ns.work)
    if not os.path.isfile(tool):
        print("PROBE-FATAL: no tool", file=sys.stderr)
        return 2
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("PROBE-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    d = os.path.join(work, ns.case)
    src, led, tmp = build(d)
    mark = os.path.join(d, "cli.mark")
    canary_log = os.path.join(d, "canary.log")
    canary_ready = os.path.join(d, "canary.ready")
    stub = os.path.join(d, "cli-stub")
    with open(stub, "w", encoding="utf-8") as f:
        f.write(STUBS[ns.case])
    os.chmod(stub, 0o755)
    cpath = os.path.join(d, "canary")
    with open(cpath, "w", encoding="utf-8") as f:
        f.write(CANARY)
    os.chmod(cpath, 0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SOUJI_", "S84_"))}
    env.update({"LC_ALL": "C", "S84_MARK": mark, "TMPDIR": tmp, "SOUJI_LEDGER": led,
                "SOUJI_CLI_BIN": stub, "SOUJI_CLI_TIMEOUT": "300", "SHOKUNIN_ROOT": os.path.join(d, "fleet"),
                "S84_CANARY_LOG": canary_log, "S84_CANARY_READY": canary_ready,
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    canary = subprocess.Popen([cpath], env=env)
    t0 = time.monotonic()
    while not os.path.exists(canary_ready) and time.monotonic() - t0 < 10:
        time.sleep(0.05)
    trace = os.path.join(d, "strace.log")
    with open(os.path.join(d, "tool.out"), "wb") as fo, open(os.path.join(d, "tool.err"), "wb") as fe, \
            open(os.devnull, "rb") as fi:
        p = subprocess.Popen(["strace", "-f", "-qq", "-e", "trace=kill", "-o", trace,
                               "bash", tool, src], stdout=fo, stderr=fe, stdin=fi, env=env,
                              start_new_session=True, cwd=d)
        while not os.path.exists(mark) and p.poll() is None and time.monotonic() - t0 < 30:
            time.sleep(0.05)
        time.sleep(0.4)
        cli_pid = None
        if os.path.exists(mark):
            m = re.search(r"pid=(\d+)", open(mark, encoding="utf-8", errors="replace").read())
            if m:
                cli_pid = int(m.group(1))
        desc = descendants(cli_pid) if cli_pid else set()
        # p is the strace process; the tool runs as ITS bash child. Signal the tool, not strace.
        tool_pid = None
        for d in os.listdir("/proc"):
            if not d.isdigit():
                continue
            try:
                with open(f"/proc/{d}/stat", "rb") as f:
                    data = f.read()
                rest = data.rsplit(b")", 1)[1].split()
                if int(rest[1]) == p.pid and b"bash" in data.split(b")")[0]:
                    tool_pid = int(d)
                    break
            except (OSError, IndexError, ValueError):
                continue
        if tool_pid:
            os.kill(tool_pid, signal.SIGTERM)
        try:
            p.wait(timeout=SETTLE)
        except subprocess.TimeoutExpired:
            pass
        if p.poll() is None:
            p.kill()
            p.wait()
    time.sleep(0.3)
    try:
        os.kill(canary.pid, signal.SIGKILL)
    except OSError:
        pass
    canary.wait()
    hits = []
    if os.path.exists(canary_log):
        hits = [l.strip() for l in open(canary_log, encoding="utf-8", errors="replace") if l.strip() != "start"]
    print(f"# tool sha256={sha(tool)} case={ns.case} cli_pid={cli_pid} canary_pid={canary.pid} tool_pid={tool_pid}")
    print(f"# descendant set at signal time: {sorted(desc)}")
    sigs = []
    if os.path.exists(trace):
        for line in open(trace, encoding="utf-8", errors="replace"):
            m = re.search(r"kill\((?:-?\d+|NULL), (\w+)\)", line)
            if not m:
                continue
            sig = m.group(1)
            tg = re.search(r"kill\((-?\d+),", line)
            sigs.append((int(tg.group(1)) if tg else None, sig, line.strip()))
    outside = []
    for pid, sig, line in sigs:
        if pid is None:
            continue
        if pid in desc or pid == p.pid:
            continue
        if pid == canary.pid:
            outside.append(("CANARY", pid, sig, line))
            continue
        if pid > 0:
            outside.append(("FOREIGN", pid, sig, line))
    print(f"# kill() calls observed by strace: {len(sigs)}")
    for pid, sig, line in sigs[:40]:
        tag = "descendant" if pid in desc else ("root" if pid == p.pid else "OUTSIDE")
        print(f"  KILL target={pid} sig={sig} class={tag}  {line[:150]}")
    print(f"# signals to a pid OUTSIDE the descendant set: {len(outside)}")
    for kind, pid, sig, line in outside:
        print(f"  OUTSIDE {kind} pid={pid} sig={sig} {line[:150]}")
    print(f"# canary signals received: {hits}")
    print(f"SUMMARY case={ns.case} kills={len(sigs)} outside={len(outside)} canary_hits={len(hits)}")
    return 0 if not outside and not hits else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
