#!/usr/bin/env python3
"""r71 post-wave probe (L1): which size-preserving, mtime-restored edits does `git status` see under the
writer's stat pins? Usage: stat-granularity-probe.py <scratch-dir>. Writes only under the scratch dir."""
import os
import subprocess
import sys
import time

S = os.path.abspath(sys.argv[1])
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
PINS = ["-c", "core.checkStat=default", "-c", "core.trustctime=true"]


def g(d, *a):
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=ENV)


def repo(name, cfg):
    d = os.path.join(S, name)
    assert d and not os.path.exists(d), d
    os.makedirs(d)
    g(d, "init", "-q")
    assert os.path.realpath(g(d, "rev-parse", "--show-toplevel").stdout.strip()) == os.path.realpath(d)
    with open(os.path.join(d, "t.txt"), "wb") as f:
        f.write(b"clean\n")
    g(d, "add", "t.txt")
    g(d, "-c", "user.name=probe", "-c", "user.email=probe@invalid", "commit", "-qm", "seed")
    for k, v in cfg:
        g(d, "config", k, v)
    return d


def run(name, cfg, mode):
    d = repo(name, cfg)
    p = os.path.join(d, "t.txt")
    past = time.time_ns() - 60 * 10**9
    time.sleep(1.02 - (time.time() % 1.0))
    os.utime(p, ns=(past, past))
    g(d, "update-index", "--really-refresh")
    if mode == "same-second-inplace":
        time.sleep(0.05)
        open(p, "wb").write(b"dirty\n")
        os.utime(p, ns=(past, past))
    elif mode == "same-second-replace":
        time.sleep(0.05)
        open(p + ".new", "wb").write(b"dirty\n")
        os.utime(p + ".new", ns=(past, past))
        os.replace(p + ".new", p)
    elif mode == "later-second-inplace":
        time.sleep(1.02 - (time.time() % 1.0))
        open(p, "wb").write(b"dirty\n")
        os.utime(p, ns=(past, past))
    plain = g(d, "status", "--porcelain").stdout.strip() or "(clean)"
    pinned = g(d, *PINS, "status", "--porcelain").stdout.strip() or "(clean)"
    print(f"{name}: config={cfg or 'none'} edit={mode} status={plain!r} status_with_writer_pins={pinned!r}")


print(f"# {g(S, 'version').stdout.strip()}; writer pins: {' '.join(PINS)}")
for cfg in ([], [("core.checkStat", "minimal")], [("core.trustctime", "false")]):
    tag = "default" if not cfg else f"{cfg[0][0]}={cfg[0][1]}"
    for mode in ("same-second-inplace", "same-second-replace", "later-second-inplace"):
        run(f"{tag}-{mode}", cfg, mode)
