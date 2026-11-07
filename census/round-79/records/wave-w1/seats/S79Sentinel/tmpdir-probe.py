#!/usr/bin/env python3
"""S79Sentinel r79: the gate's private scratch dir (mktemp -d -t under the caller's TMPDIR).

Arms:
  in-lane   TMPDIR=<clone>/tmp: the gate's own scratch dir is inside the tree it judges
  empty     TMPDIR="": what mktemp -d -t does
  relative  TMPDIR=rel: where the dir lands (relative to the gate's cwd)
  race      TMPDIR is a 0777 non-sticky dir: another user with write on the parent renames the
            gate's 0700 dir away and plants <name>/o as a symlink to a victim file; the gate's next
            child-output write follows it
  usage     a usage error: is a scratch dir created before the argument check?
  sigkill   SIGKILL to the gate: the dir cannot be removed
"""
import importlib.util
import os
import secrets
import shutil
import signal
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/souji-r79/S79Sentinel"
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
PROBE = os.path.join(LANE, "census/round-74/records/wave-repair/probes/evade-probe.py")
GATE = os.path.join(S, "gw1", "souji-pre-report-gate.sh")
BASE = os.path.join(S, "tmp")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = load(PROBE, "evade_probe")


def fixture(name):
    rowdir = os.path.join(BASE, name)
    if os.path.isdir(rowdir):
        subprocess.run(["rm", "-rf", rowdir], check=False)
    os.makedirs(BASE, exist_ok=True)
    clone, report, prereg = P.build(rowdir)
    return rowdir, clone, report, prereg


def gate_env(tmpdir, extra=None):
    e = P.env_clean({"TMPDIR": tmpdir})
    if extra:
        e.update(extra)
    return e


def run(name, argv, env, cwd, timeout_s=60):
    outp = os.path.join(BASE, name + ".out")
    errp = os.path.join(BASE, name + ".err")
    t0 = time.monotonic()
    with open(outp, "wb") as fo, open(errp, "wb") as fe:
        p = subprocess.run(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, env=env,
                           cwd=cwd, timeout=timeout_s, start_new_session=True)
    return p.returncode, time.monotonic() - t0, outp, errp


def show(name, rc, secs, outp, errp, extra=""):
    out = open(outp, encoding="utf-8", errors="replace").read()
    err = open(errp, encoding="utf-8", errors="replace").read()
    lines = [l for l in (out + err).splitlines() if l.startswith(("check-", "detail-", "gate:"))]
    print(f"ARM {name} rc={rc} secs={secs:.1f} {extra}")
    for l in lines:
        print(f"    {l}")


def arm_in_lane():
    rowdir, clone, report, prereg = fixture("in-lane")
    tmpdir = os.path.join(clone, "tmp")
    os.makedirs(tmpdir)
    rc, secs, outp, errp = run("in-lane", ["bash", GATE, "--lane", clone, "--branch", "master",
                                           "--report", report, "--prereg", prereg],
                               gate_env(tmpdir), rowdir)
    left = os.listdir(tmpdir)
    show("in-lane", rc, secs, outp, errp, f"tmpleft={len(left)}")
    print(f"    NOTE scratch dir lived inside the judged tree: {left}")


def arm_empty():
    rowdir, clone, report, prereg = fixture("empty")
    rc, secs, outp, errp = run("empty", ["bash", GATE, "--lane", clone, "--branch", "master",
                                         "--report", report, "--prereg", prereg],
                               gate_env(""), rowdir)
    show("empty", rc, secs, outp, errp)


def arm_relative():
    rowdir, clone, report, prereg = fixture("relative")
    rel = os.path.join(rowdir, "rel")
    os.makedirs(rel)
    rc, secs, outp, errp = run("relative", ["bash", GATE, "--lane", clone, "--branch", "master",
                                            "--report", report, "--prereg", prereg],
                               gate_env("rel"), rel)
    show("relative", rc, secs, outp, errp, f"rel_left={os.listdir(rel)}")


def arm_usage():
    rowdir, clone, report, prereg = fixture("usage")
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    rc, secs, outp, errp = run("usage", ["bash", GATE, "--lane", clone, "--branch", "master"],
                               gate_env(tmpdir), rowdir)
    show("usage", rc, secs, outp, errp, f"tmpleft={os.listdir(tmpdir)}")


def arm_race():
    rowdir, clone, report, prereg = fixture("race")
    shared = os.path.join(rowdir, "shared")
    os.makedirs(shared)
    os.chmod(shared, 0o777)
    victim = os.path.join(rowdir, "victim.txt")
    with open(victim, "w", encoding="utf-8") as f:
        f.write("ORIGINAL-VICTIM-CONTENT\n")
    shimdir = os.path.join(rowdir, "shim")
    os.makedirs(shimdir)
    with open(os.path.join(shimdir, "git"), "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\ncase \" $* \" in *' config -z '*) sleep 2 ;; esac\n"
                "exec %s \"$@\"\n" % shutil.which("git"))
    os.chmod(os.path.join(shimdir, "git"), 0o755)
    env = gate_env(shared, {"PATH": shimdir + os.pathsep + os.environ["PATH"]})
    outp = os.path.join(BASE, "race.out")
    errp = os.path.join(BASE, "race.err")
    with open(outp, "wb") as fo, open(errp, "wb") as fe:
        p = subprocess.Popen(["bash", GATE, "--lane", clone, "--branch", "master",
                              "--report", report, "--prereg", prereg],
                             stdout=fo, stderr=fe, stdin=subprocess.DEVNULL, env=env,
                             cwd=rowdir, start_new_session=True)
    # the attacker: write on the parent is enough to rename our 0700 dir away
    stolen = None
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        names = [n for n in os.listdir(shared) if n.startswith("souji-gate.")]
        if names:
            name = names[0]
            os.rename(os.path.join(shared, name), os.path.join(shared, "held." + name))
            os.makedirs(os.path.join(shared, name))
            os.symlink(victim, os.path.join(shared, name, "o"))
            stolen = name
            break
        time.sleep(0.01)
    p.wait(timeout=60)
    after = open(victim, encoding="utf-8", errors="replace").read()
    out = open(outp, encoding="utf-8", errors="replace").read()
    err = open(errp, encoding="utf-8", errors="replace").read()
    print(f"ARM race rc={p.returncode} stolen={stolen!r} victim_changed={after != 'ORIGINAL-VICTIM-CONTENT\\n'}")
    print(f"    victim_now={after.splitlines()[:2]}")
    for l in (out + err).splitlines():
        if l.startswith(("check-", "detail-")):
            print(f"    {l}")


def arm_sigkill():
    rowdir, clone, report, prereg = fixture("sigkill")
    tmpdir = os.path.join(rowdir, "tmp")
    os.makedirs(tmpdir)
    shimdir = os.path.join(rowdir, "shim")
    os.makedirs(shimdir)
    with open(os.path.join(shimdir, "git"), "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\ncase \" $* \" in *' rev-parse --verify '*) exec sleep 600 ;; esac\n"
                "exec %s \"$@\"\n" % shutil.which("git"))
    os.chmod(os.path.join(shimdir, "git"), 0o755)
    env = gate_env(tmpdir, {"PATH": shimdir + os.pathsep + os.environ["PATH"]})
    p = subprocess.Popen(["bash", GATE, "--lane", clone, "--branch", "master",
                          "--report", report, "--prereg", prereg],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         stdin=subprocess.DEVNULL, env=env, cwd=rowdir, start_new_session=True)
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline and not [n for n in os.listdir(tmpdir)]:
        time.sleep(0.02)
    time.sleep(0.5)
    os.kill(p.pid, signal.SIGKILL)
    p.wait()
    left = os.listdir(tmpdir)
    print(f"ARM sigkill rc={p.returncode} tmpleft={len(left)} {left}")
    for n in left:
        d = os.path.join(tmpdir, n)
        if os.path.isdir(d):
            print(f"    left_dir={d} mode={oct(os.stat(d).st_mode & 0o777)} files={os.listdir(d)}")
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError:
        pass


if __name__ == "__main__":
    arm_in_lane()
    arm_empty()
    arm_relative()
    arm_usage()
    arm_race()
    arm_sigkill()
