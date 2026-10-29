#!/usr/bin/env python3
"""r42 C3: condition-level behaviour cases for souji-worktree-drift.py.

Each case builds its own scenario under --work, runs the tool as a subprocess and asserts only what
the tool does (exit code, stdout/stderr tokens, the --json file). The case name states the behaviour
it pins. Output: case-<name>=PASS|FAIL lines and `SUMMARY cases=<n> pass=<p> fail=<f>`.
"""
import argparse
import json
import os
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
                    "LC_ALL": "C", "HOME": work, "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                    "GIT_TERMINAL_PROMPT": "0"}

    def scene(self, name):
        """Fresh scenario: <w>/root holds one real repository r (regs=1 prunable=0); <w>/o is for records."""
        w = os.path.join(self.work, name)
        root, out = w + "/root", w + "/o"
        os.makedirs(root)
        os.makedirs(out)
        self.init(root + "/r")
        return w, root, out

    def init(self, path, bare=False):
        cmd = ["git", "init", "-q"] + (["--bare"] if bare else []) + [path]
        subprocess.run(cmd, env=self.env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=60)

    def tool_run(self, args, timeout=60, cwd=None):
        """Run the tool; return (CompletedProcess with bytes output, elapsed seconds) or (None, elapsed) on timeout."""
        t0 = time.monotonic()
        try:
            p = subprocess.run(["python3", "-B", self.tool] + args, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=self.env, timeout=timeout, cwd=cwd or self.work)
        except subprocess.TimeoutExpired:
            return None, time.monotonic() - t0
        return p, time.monotonic() - t0


def put(path, data):
    with open(path, "wb") as handle:
        handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


def refused(p, cls):
    return p is not None and p.returncode == 2 and ("REFUSAL %s:" % cls) in p.stderr.decode("utf-8", "replace")


def drift_line(p, text):
    return p is not None and p.returncode == 1 and text in p.stdout.decode("utf-8", "replace")


def case_fifo_record_is_refused_not_blocked(c):
    w, root, out = c.scene("fifo-record")
    os.mkfifo(out + "/rfifo")
    p, _ = c.tool_run(["--root", root, "--record", out + "/rfifo", "--skip-unrecorded"], timeout=25)
    return refused(p, "RECORD-MALFORMED")


def case_root_sibling_prefix_is_outside(c):
    w, root, out = c.scene("root-sibling")
    rec = put(out + "/rec", "REPO\t../root2\tregs=1\tprunable=0\n")
    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])
    return refused(p, "RECORD-OUTSIDE-ROOT")


def case_gitdir_sibling_prefix_is_outside(c):
    w, root, out = c.scene("gitdir-sibling")
    os.makedirs(w + "/rootX")
    c.init(w + "/rootX/gd2", bare=True)
    os.makedirs(root + "/s")
    put(root + "/s/.git", "gitdir: " + w + "/rootX/gd2\n")
    rec = put(out + "/rec", "REPO\ts\tregs=1\tprunable=0\n")
    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])
    return refused(p, "RECORD-OUTSIDE-ROOT")


def case_timeout_of_one_is_accepted(c):
    w, root, out = c.scene("timeout-one")
    rec = put(out + "/rec", "REPO\ta\tregs=1\tprunable=0\n")
    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"])
    return drift_line(p, "DRIFT\tABSENT\ta")


def blocked_head_scene(c, name):
    """A repository whose HEAD is a FIFO: git blocks reading it until the tool's timeout fires."""
    w, root, out = c.scene(name)
    c.init(root + "/t")
    os.remove(root + "/t/.git/HEAD")
    os.mkfifo(root + "/t/.git/HEAD")
    rec = put(out + "/rec", "REPO\tt\tregs=1\tprunable=0\n")
    return root, rec


def case_default_timeout_outlasts_a_blocked_git(c):
    root, rec = blocked_head_scene(c, "default-timeout")
    p, elapsed = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"], timeout=100)
    # the default allowance is far above 5 s; a 1 s default would answer in about 1 s
    return drift_line(p, "DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout") and elapsed >= 5.0


def case_list_timeout_is_reported_unreachable(c):
    root, rec = blocked_head_scene(c, "list-timeout")
    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--timeout", "1"], timeout=60)
    return drift_line(p, "DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout")


def case_list_nonzero_rc_is_reported_unreachable(c):
    w, root, out = c.scene("list-rc")
    os.makedirs(root + "/u/.git")
    rec = put(out + "/rec", "REPO\tu\tregs=1\tprunable=0\n")
    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])
    return drift_line(p, "DRIFT\tUNREACHABLE\tu\tUNREACHABLE:list-rc=")


def case_root_option_is_required(c):
    w, root, out = c.scene("root-required")
    rec = put(out + "/rec", ROW)
    p, _ = c.tool_run(["--record", rec], cwd=out)
    return p is not None and p.returncode == 2 and "required" in p.stderr.decode("utf-8", "replace")


def case_record_option_is_required(c):
    w, root, out = c.scene("record-required")
    p, _ = c.tool_run(["--root", root])
    return p is not None and p.returncode == 2 and "required" in p.stderr.decode("utf-8", "replace")


def case_symlinked_child_is_not_discovered(c):
    w, root, out = c.scene("symlink-child")
    c.init(root + "/u2")
    os.symlink(root + "/u2", root + "/lnk")
    rec = put(out + "/rec", ROW)
    p, _ = c.tool_run(["--root", root, "--record", rec])
    text = p.stdout.decode("utf-8", "replace") if p is not None else ""
    return drift_line(p, "DRIFT\tUNRECORDED\tu2") and "UNRECORDED\tlnk" not in text


def case_two_digit_regs_are_read_whole(c):
    w, root, out = c.scene("two-digit-regs")
    rec = put(out + "/rec", "REPO\tr\tregs=10\tprunable=0\n")
    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded"])
    return drift_line(p, "record=10 live=1")


def case_longer_old_json_is_truncated_on_write(c):
    w, root, out = c.scene("json-truncate")
    rec = put(out + "/rec", ROW)
    target = put(out + "/old.json", "x" * 5000)
    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--json", target])
    if p is None or p.returncode != 0:
        return False
    try:
        with open(target, "rb") as handle:
            data = json.loads(handle.read().decode("utf-8"))
    except (OSError, ValueError):
        return False
    return data.get("drift") == [] and "summary" in data


def case_invalid_utf8_in_record_becomes_replacement_char(c):
    w, root, out = c.scene("invalid-utf8")
    rec = put(out + "/rec", b"REPO\ta\xffb\tregs=1\tprunable=0\n")
    js = out + "/o.json"
    p, _ = c.tool_run(["--root", root, "--record", rec, "--skip-unrecorded", "--json", js])
    if p is None or p.returncode != 1:
        return False
    if b"DRIFT\tABSENT\ta\xef\xbf\xbdb\t" not in p.stdout or b"\\xff" in p.stdout:
        return False
    try:
        with open(js, "rb") as handle:
            data = json.loads(handle.read().decode("utf-8"))
    except (OSError, ValueError):
        return False
    return [row.get("repo") for row in data.get("drift", [])] == ["a\ufffdb"]


CASES = [(name[5:].replace("_", "-"), fn) for name, fn in sorted(globals().items())
         if name.startswith("case_") and callable(fn)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    if os.geteuid() == 0:
        sys.stderr.write("r42-drift-conditions: refusing to run as root\n")
        return 2
    work = os.path.realpath(tempfile.mkdtemp(prefix="r42dc.", dir=a.work))
    ctx = Ctx(os.path.realpath(a.tool), work)
    bad = 0
    try:
        for name, fn in CASES:
            try:
                good = bool(fn(ctx))
            except Exception as exc:  # noqa: BLE001 - a scenario error is a failed case, never a traceback
                good = False
                sys.stderr.write("case-%s: %s: %s\n" % (name, type(exc).__name__, exc))
            bad += not good
            print("case-%s=%s" % (name, "PASS" if good else "FAIL"), flush=True)
        print("SUMMARY cases=%d pass=%d fail=%d" % (len(CASES), len(CASES) - bad, bad))
        return 1 if bad else 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


sys.exit(main())
