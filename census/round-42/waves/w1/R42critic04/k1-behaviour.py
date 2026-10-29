#!/usr/bin/env python3
"""R42critic04 candidate K1: behaviour-only condition fixture for tools/souji-worktree-drift.py.

Each case builds a fixture under --work, runs the tool as a child process (python3 -B TOOL ...) and
asserts on the exit code, the refusal class on stderr, the DRIFT rows on stdout, or the --json file.
No byte of the tool is read, and no case key depends on the tool's path or name.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

REAL_GIT = shutil.which("git") or "/usr/bin/git"
TOOL = None
WORK = None
RESULTS = []


def case(name, ok):
    RESULTS.append(bool(ok))
    print("case-%s=%s" % (name, "PASS" if ok else "FAIL"))


def write(path, data):
    with open(path, "wb") as handle:
        handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))


def new_base():
    return os.path.realpath(tempfile.mkdtemp(prefix="c.", dir=WORK))


def git_init(path):
    os.makedirs(path, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": os.devnull}
    subprocess.run([REAL_GIT, "init", "-q", path], env=env, check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def fake_git(base, delay):
    """A git stand-in that sleeps before exec-ing the real git, so a short --timeout is exceeded."""
    bindir = os.path.join(base, "bin")
    os.makedirs(bindir)
    path = os.path.join(bindir, "git")
    write(path, "#!%s\nimport os, sys, time\ntime.sleep(%d)\nos.execv(%r, [%r] + sys.argv[1:])\n"
          % (sys.executable, delay, REAL_GIT, REAL_GIT))
    os.chmod(path, 0o755)
    return bindir


def tool(args, cwd, timeout=60, bindir=None):
    path = os.environ.get("PATH", "/usr/bin:/bin")
    env = {"PATH": (bindir + os.pathsep + path) if bindir else path, "TMPDIR": WORK, "LC_ALL": "C"}
    try:
        proc = subprocess.run([sys.executable, "-B", TOOL] + args, cwd=cwd, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return None, "", "TIMEOUT"
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")


def record(base, data, name="rec.tsv"):
    path = os.path.join(base, name)
    write(path, data)
    return path


def fleet_with(base, *repos):
    fleet = os.path.join(base, "fleet")
    os.makedirs(fleet)
    for name in repos:
        git_init(os.path.join(fleet, name))
    return fleet


def c_B1():
    base = new_base()
    fleet = fleet_with(base)
    fifo = os.path.join(base, "rec.fifo")
    os.mkfifo(fifo)
    rc, _out, err = tool(["--root", fleet, "--record", fifo], base, timeout=15)
    case("B1", rc == 2 and "RECORD-MALFORMED" in err)


def c_E2():
    base = new_base()
    fleet = fleet_with(base)
    os.makedirs(os.path.join(base, "fleet-x"))
    rec = record(base, b"REPO\t../fleet-x\tregs=1\tprunable=0\n")
    rc, _out, err = tool(["--root", fleet, "--record", rec], base)
    case("E2", rc == 2 and "RECORD-OUTSIDE-ROOT" in err)


def c_E4():
    base = new_base()
    fleet = fleet_with(base)
    gitdir_repo = os.path.join(base, "fleet-gd", "r1")
    git_init(gitdir_repo)
    os.makedirs(os.path.join(fleet, "r1"))
    write(os.path.join(fleet, "r1", ".git"), "gitdir: %s\n" % os.path.join(gitdir_repo, ".git"))
    rec = record(base, b"REPO\tr1\tregs=1\tprunable=0\n")
    rc, _out, err = tool(["--root", fleet, "--record", rec], base)
    case("E4", rc == 2 and "RECORD-OUTSIDE-ROOT" in err)


def c_G2():
    base = new_base()
    fleet = fleet_with(base, "a")
    rec = record(base, b"REPO\ta\tregs=1\tprunable=0\n")
    rc, _out, err = tool(["--root", fleet, "--record", rec, "--timeout", "1"], base)
    case("G2", rc == 0 and "REFUSAL" not in err)


def c_G3():
    base = new_base()
    fleet = fleet_with(base, "a")
    rec = record(base, b"REPO\ta\tregs=1\tprunable=0\n")
    bindir = fake_git(base, 2)
    rc, out, _err = tool(["--root", fleet, "--record", rec], base, timeout=120, bindir=bindir)
    case("G3", rc == 0 and "UNREACHABLE" not in out)


def c_G4():
    base = new_base()
    fleet = fleet_with(base, "a")
    rec = record(base, b"REPO\ta\tregs=1\tprunable=0\n")
    bindir = fake_git(base, 2)
    rc, out, _err = tool(["--root", fleet, "--record", rec, "--timeout", "1"], base, timeout=120, bindir=bindir)
    case("G4", rc == 1 and "DRIFT\tUNREACHABLE\ta\tUNREACHABLE:list-timeout" in out)


def c_G5():
    base = new_base()
    fleet = fleet_with(base)
    bad = os.path.join(fleet, "r2")
    os.makedirs(bad)
    write(os.path.join(bad, ".git"), "gitdir: /nonexistent-r42-critic04\n")
    rec = record(base, b"REPO\tr2\tregs=1\tprunable=0\n")
    rc, out, _err = tool(["--root", fleet, "--record", rec], base)
    case("G5", rc == 1 and "DRIFT\tUNREACHABLE\tr2\tUNREACHABLE:list-rc=128" in out)


def c_H1():
    base = new_base()
    fleet = fleet_with(base, "a")
    rec = record(base, b"REPO\ta\tregs=1\tprunable=0\n")
    rc, _out, err = tool(["--record", rec], base)
    case("H1", rc == 2 and "required" in err and "--root" in err)


def c_H2():
    base = new_base()
    fleet = fleet_with(base, "a")
    rc, _out, err = tool(["--root", fleet], base)
    case("H2", rc == 2 and "required" in err and "--record" in err)


def c_I1():
    base = new_base()
    fleet = fleet_with(base, "real")
    ext = os.path.join(base, "outside", "ext")
    git_init(ext)
    os.symlink(ext, os.path.join(fleet, "alias"))
    rec = record(base, b"REPO\treal\tregs=1\tprunable=0\n")
    rc, out, _err = tool(["--root", fleet, "--record", rec], base)
    case("I1", rc == 0 and "UNRECORDED" not in out)


def c_J9():
    base = new_base()
    fleet = fleet_with(base, "big")
    rec = record(base, b"REPO\tbig\tregs=10\tprunable=0\n")
    rc, out, _err = tool(["--root", fleet, "--record", rec], base)
    case("J9", rc == 1 and "DRIFT\tREGS-CHANGED\tbig\trecord=10 live=1" in out)


def c_M1():
    base = new_base()
    fleet = fleet_with(base, "a")
    rec = record(base, b"REPO\ta\tregs=1\tprunable=0\n")
    target = os.path.join(base, "out.json")
    write(target, b'{"pad": "' + b"x" * 4000 + b'"}\n')
    rc, _out, _err = tool(["--root", fleet, "--record", rec, "--json", target], base)
    ok = False
    try:
        with open(target, encoding="utf-8") as handle:
            data = json.load(handle)
        ok = rc == 0 and data["summary"]["record_repos"] == 1
    except (OSError, ValueError, KeyError):
        ok = False
    case("M1", ok)


def c_D4():
    base = new_base()
    fleet = fleet_with(base, "a")
    rec = record(base, b"REPO\tna\xffme\tregs=1\tprunable=0\nREPO\ta\tregs=1\tprunable=0\n")
    target = os.path.join(base, "out.json")
    rc, _out, _err = tool(["--root", fleet, "--record", rec, "--json", target], base)
    ok = False
    try:
        with open(target, encoding="utf-8") as handle:
            data = json.load(handle)
        ok = rc == 1 and "na\ufffdme" in [d["repo"] for d in data["drift"]]
    except (OSError, ValueError, KeyError):
        ok = False
    case("D4", ok)


CASES = (c_B1, c_E2, c_E4, c_G2, c_G3, c_G4, c_G5, c_H1, c_H2, c_I1, c_J9, c_M1, c_D4)


def main(argv):
    global TOOL, WORK
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    TOOL = os.path.realpath(args.tool)
    WORK = os.path.realpath(args.work)
    for fn in CASES:
        try:
            fn()
        except Exception as exc:  # a broken setup is a failed case, never a traceback
            case(fn.__name__[2:] + "-SETUP", False)
            print("setup-error %s: %s" % (fn.__name__, type(exc).__name__))
    failed = RESULTS.count(False)
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(RESULTS), len(RESULTS) - failed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
