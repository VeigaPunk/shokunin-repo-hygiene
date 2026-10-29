#!/usr/bin/env python3
"""r42 C3: condition-level behaviours of souji-worktree-drift.py, each observed through a subprocess run.

Protocol: `python3 -B r42-drift-conditions.py --tool PATH --work DIR` prints `case-<name>=PASS|FAIL` per case and
`SUMMARY cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0, exit 1 otherwise. Every case builds its own scenario
under --work and judges only exit codes, stdout/stderr tokens and the bytes of the --json file the tool writes.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROW = "REPO\tr\tregs=1\tprunable=0\n"


class Ctx:
    def __init__(self, tool, work):
        self.tool = tool
        self.work = work
        self.env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work,
                    "LC_ALL": "C.UTF-8", "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1", "HOME": work,
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}

    def git_init(self, path, bare=False):
        cmd = [b"git", b"init", b"-q"] + ([b"--bare"] if bare else []) + [os.fsencode(path)]
        subprocess.run(cmd, env=self.env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=60)

    def tool_run(self, args, cwd, timeout=25):
        t0 = time.monotonic()
        try:
            p = subprocess.run(["python3", "-B", self.tool] + args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, timeout=timeout, env=self.env, cwd=cwd)
        except subprocess.TimeoutExpired:
            return None, time.monotonic() - t0
        return p, time.monotonic() - t0


def put(path, data):
    with open(path, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def scenario(ctx, tag):
    """Fresh W with root R (one real repository r: regs=1 prunable=0), record dir O and an empty cwd C."""
    w = os.path.realpath(tempfile.mkdtemp(prefix=tag + "-", dir=ctx.work))
    r, o, c = w + "/root", w + "/o", w + "/cwd"
    for d in (r, o, c):
        os.makedirs(d)
    ctx.git_init(r + "/r")
    return w, r, o, c


def txt(b):
    return b.decode("utf-8", "replace")


def refused(p, cls):
    if p is None:
        return False, "timeout"
    ok = p.returncode == 2 and ("REFUSAL %s:" % cls) in txt(p.stderr)
    return ok, "rc=%d" % p.returncode


def base_args(r, rec):
    return ["--root", r, "--record", rec, "--skip-unrecorded"]


def valid_clean_json(path):
    try:
        with open(path, "rb") as f:
            d = json.loads(f.read().decode("utf-8"))
        return isinstance(d, dict) and "summary" in d and d.get("drift") == []
    except Exception:  # noqa: BLE001 - any parse failure is a failed observation
        return False


def c_fifo_record(ctx):
    w, r, o, c = scenario(ctx, "fifo")
    os.mkfifo(o + "/rfifo")
    p, _ = ctx.tool_run(base_args(r, o + "/rfifo"), c, timeout=20)
    return refused(p, "RECORD-MALFORMED")


def c_outside_prefix_sibling(ctx):
    w, r, o, c = scenario(ctx, "pfx")
    rec = put(o + "/rec", "REPO\t../root2\tregs=1\tprunable=0\n")
    p, _ = ctx.tool_run(base_args(r, rec), c)
    return refused(p, "RECORD-OUTSIDE-ROOT")


def c_gitdir_prefix_sibling(ctx):
    w, r, o, c = scenario(ctx, "gdp")
    os.makedirs(w + "/rootX")
    ctx.git_init(w + "/rootX/gd2", bare=True)
    os.makedirs(r + "/s")
    put(r + "/s/.git", "gitdir: " + w + "/rootX/gd2\n")
    rec = put(o + "/rec", "REPO\ts\tregs=1\tprunable=0\n")
    p, _ = ctx.tool_run(base_args(r, rec), c)
    return refused(p, "RECORD-OUTSIDE-ROOT")


def c_timeout_one_accepted(ctx):
    w, r, o, c = scenario(ctx, "t1")
    rec = put(o + "/rec", "REPO\ta\tregs=1\tprunable=0\n")
    p, _ = ctx.tool_run(base_args(r, rec) + ["--timeout", "1"], c)
    good = p is not None and p.returncode == 1 and "DRIFT\tABSENT\ta" in txt(p.stdout)
    return good, "rc=%s" % (p.returncode if p else "timeout")


def fifo_head_repo(ctx, r, name):
    ctx.git_init(r + "/" + name)
    os.remove(r + "/%s/.git/HEAD" % name)
    os.mkfifo(r + "/%s/.git/HEAD" % name)


def c_default_timeout_waits(ctx):
    w, r, o, c = scenario(ctx, "dto")
    fifo_head_repo(ctx, r, "t")
    rec = put(o + "/rec", "REPO\tt\tregs=1\tprunable=0\n")
    p, dt = ctx.tool_run(base_args(r, rec), c, timeout=100)
    good = (p is not None and p.returncode == 1 and "UNREACHABLE:list-timeout" in txt(p.stdout)
            and dt >= 12.0)
    return good, "rc=%s elapsed=%.1f" % (p.returncode if p else "timeout", dt)


def c_list_timeout_reported(ctx):
    w, r, o, c = scenario(ctx, "lto")
    fifo_head_repo(ctx, r, "t")
    rec = put(o + "/rec", "REPO\tt\tregs=1\tprunable=0\n")
    p, _ = ctx.tool_run(base_args(r, rec) + ["--timeout", "1"], c, timeout=60)
    good = (p is not None and p.returncode == 1
            and "DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout" in txt(p.stdout)
            and "Traceback" not in txt(p.stderr))
    return good, "rc=%s" % (p.returncode if p else "timeout")


def c_list_rc_reported(ctx):
    w, r, o, c = scenario(ctx, "lrc")
    os.makedirs(r + "/u/.git")
    rec = put(o + "/rec", "REPO\tu\tregs=1\tprunable=0\n")
    p, _ = ctx.tool_run(base_args(r, rec), c)
    good = p is not None and p.returncode == 1 and "DRIFT\tUNREACHABLE\tu\tUNREACHABLE:list-rc=" in txt(p.stdout)
    return good, "rc=%s" % (p.returncode if p else "timeout")


def c_root_required(ctx):
    w, r, o, c = scenario(ctx, "rreq")
    rec = put(o + "/rec", ROW)
    p, _ = ctx.tool_run(["--record", rec, "--skip-unrecorded"], c)
    good = p is not None and p.returncode == 2 and re.search(r"are required: .*--root", txt(p.stderr)) is not None
    return good, "rc=%s" % (p.returncode if p else "timeout")


def c_record_required(ctx):
    w, r, o, c = scenario(ctx, "qreq")
    p, _ = ctx.tool_run(["--root", r, "--skip-unrecorded"], c)
    good = p is not None and p.returncode == 2 and re.search(r"are required: .*--record", txt(p.stderr)) is not None
    return good, "rc=%s" % (p.returncode if p else "timeout")


def c_symlink_child_skipped(ctx):
    w, r, o, c = scenario(ctx, "sym")
    ctx.git_init(r + "/u2")
    os.symlink(r + "/u2", r + "/symchild")
    rec = put(o + "/rec", ROW)
    p, _ = ctx.tool_run(["--root", r, "--record", rec], c)
    out = txt(p.stdout) if p else ""
    good = p is not None and p.returncode == 1 and "DRIFT\tUNRECORDED\tu2" in out and "symchild" not in out
    return good, "rc=%s" % (p.returncode if p else "timeout")


def c_regs_two_digits(ctx):
    w, r, o, c = scenario(ctx, "regs")
    rec = put(o + "/rec", "REPO\tr\tregs=10\tprunable=0\n")
    p, _ = ctx.tool_run(base_args(r, rec), c)
    good = p is not None and p.returncode == 1 and "record=10 live=1" in txt(p.stdout)
    return good, "rc=%s" % (p.returncode if p else "timeout")


def c_json_truncates_old_tail(ctx):
    w, r, o, c = scenario(ctx, "jtr")
    rec = put(o + "/rec", ROW)
    out = put(o + "/big.json", "x" * 5000)
    p, _ = ctx.tool_run(base_args(r, rec) + ["--json", out], c)
    good = p is not None and p.returncode == 0 and valid_clean_json(out)
    return good, "rc=%s" % (p.returncode if p else "timeout")


def c_record_bad_byte_replaced(ctx):
    w, r, o, c = scenario(ctx, "d4")
    name = b"bad\xef\xbf\xbdname"  # the replacement character as a real directory name
    ctx.git_init(os.fsencode(r) + b"/" + name)
    rec = put(o + "/rec", b"REPO\tr\tregs=1\tprunable=0\nREPO\tbad\xffname\tregs=1\tprunable=0\n")
    p, _ = ctx.tool_run(base_args(r, rec), c)
    good = p is not None and p.returncode == 0 and b"ABSENT" not in p.stdout and b"\\x" not in p.stdout
    return good, "rc=%s stdout=%r" % (p.returncode if p else "timeout", (p.stdout[:160] if p else b""))


def c_clean_run_exit_zero(ctx):
    w, r, o, c = scenario(ctx, "pos")
    rec = put(o + "/rec", ROW)
    out = o + "/pos.json"
    p, _ = ctx.tool_run(base_args(r, rec) + ["--json", out], c)
    good = p is not None and p.returncode == 0 and valid_clean_json(out)
    return good, "rc=%s" % (p.returncode if p else "timeout")


def c_drift_exit_one(ctx):
    w, r, o, c = scenario(ctx, "drf")
    rec = put(o + "/rec", "REPO\tr\tregs=2\tprunable=0\n")
    p, _ = ctx.tool_run(base_args(r, rec), c)
    good = p is not None and p.returncode == 1 and "DRIFT\tREGS-CHANGED\tr" in txt(p.stdout)
    return good, "rc=%s" % (p.returncode if p else "timeout")


CASES = [
    ("fifo-record-not-blocking", c_fifo_record),
    ("record-row-prefix-sibling-outside", c_outside_prefix_sibling),
    ("gitdir-prefix-sibling-outside", c_gitdir_prefix_sibling),
    ("timeout-one-accepted", c_timeout_one_accepted),
    ("default-timeout-waits", c_default_timeout_waits),
    ("list-timeout-reported", c_list_timeout_reported),
    ("list-returncode-reported", c_list_rc_reported),
    ("root-required", c_root_required),
    ("record-required", c_record_required),
    ("symlink-child-skipped", c_symlink_child_skipped),
    ("regs-two-digits", c_regs_two_digits),
    ("json-truncates-old-tail", c_json_truncates_old_tail),
    ("record-bad-byte-replaced", c_record_bad_byte_replaced),
    ("clean-run-exit-zero", c_clean_run_exit_zero),
    ("drift-exit-one", c_drift_exit_one),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    if os.geteuid() == 0:
        sys.stderr.write("r42-drift-conditions: refusing to run as root\n")
        return 2
    os.makedirs(a.work, exist_ok=True)
    work = os.path.realpath(tempfile.mkdtemp(prefix="r42dc-", dir=a.work))
    ctx = Ctx(os.path.abspath(a.tool), work)
    bad = 0
    try:
        for name, fn in CASES:
            try:
                good, detail = fn(ctx)
            except Exception as exc:  # noqa: BLE001 - a scenario failure is a failed case, never a traceback
                good, detail = False, "error %s" % type(exc).__name__
            bad += not good
            print("case-%s=%s %s" % (name, "PASS" if good else "FAIL", detail))
            sys.stdout.flush()
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(CASES), len(CASES) - bad, bad))
    return 1 if bad else 0


sys.exit(main())
