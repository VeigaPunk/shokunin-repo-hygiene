#!/usr/bin/env python3
"""r42-drift-conditions.py — condition-level behaviours of tools/souji-worktree-drift.py.

The r41 battery asserts one refusal class per site. This fixture observes the CONDITIONS behind the
classes through exit codes, stdout/stderr tokens and the --json file, never through the tool's bytes:

  record is a FIFO         a record named by a FIFO with no writer is refused, never waited on
  prefix-sibling rows      a record row / a gitdir that resolves to a sibling directory whose name
                           merely starts with the root's name is OUTSIDE the root
  --timeout                1 is a valid value; the default lets a slow git finish; a hung git is
                           reported as UNREACHABLE:list-timeout; a failing worktree list is
                           reported as UNREACHABLE:list-rc=
  --root / --record        both are required arguments
  discovery                a symlinked child directory is not an unrecorded work tree
  record rows              regs holds more than one digit
  --json                   a longer pre-existing file is truncated, not overwritten in place
  invalid UTF-8            an undecodable byte in a repository name becomes U+FFFD, so it names the
                           directory spelled with U+FFFD

Every case builds its own scenario under --work and runs `python3 -B <tool>` as a subprocess. Cases
run concurrently. No case asserts a wall clock: the slow-git case lets git block for a fixed delay
that is 8x shorter than the default timeout and 2.5x longer than a mutated default of one second.

CLI:
  python3 -B r42-drift-conditions.py --tool PATH --work DIR
Output: case-<name>=PASS|FAIL per case, then `SUMMARY cases=<n> pass=<p> fail=<f>`.
Exit: 0 iff fail=0, 1 on any failure, 2 usage / refused to run as root.
"""
import argparse
import concurrent.futures
import errno
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C.UTF-8",
    "PYTHONUTF8": "1",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_TERMINAL_PROMPT": "0",
}
ROW = "REPO\tr\tregs=1\tprunable=0\n"
SLOW_GIT_DELAY = 2.5


class Fail(Exception):
    pass


def need(cond, why):
    if not cond:
        raise Fail(why)


def git_init(path):
    os.makedirs(path, exist_ok=True)
    subprocess.run(["git", "init", "-q", path], env=ENV, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=True)


def put(path, data):
    with open(path, "wb") as handle:
        handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    return path


class Scenario:
    """W/<case>/root (the --root, holds repository r), W/<case>/o (records and outputs)."""

    def __init__(self, work, name, tool):
        self.dir = os.path.join(work, name)
        self.root = os.path.join(self.dir, "root")
        self.out = os.path.join(self.dir, "o")
        self.tool = tool
        os.makedirs(self.root)
        os.makedirs(self.out)
        git_init(os.path.join(self.root, "r"))

    def record(self, text, name="rec"):
        return put(os.path.join(self.out, name), text)

    def run(self, args, timeout=60, env=None):
        """Return (rc, stdout, stderr); a timeout yields rc=None."""
        try:
            p = subprocess.run(["python3", "-B", self.tool] + args, cwd=self.dir,
                               env=dict(env or ENV, TMPDIR=self.dir), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            return None, "", ""
        return (p.returncode, p.stdout.decode("utf-8", "replace"),
                p.stderr.decode("utf-8", "replace"))

    def drift(self, record, extra=(), **kw):
        return self.run(["--root", self.root, "--record", record, "--skip-unrecorded"] + list(extra),
                        **kw)


def case_baseline(sc):
    rc, out, err = sc.drift(sc.record(ROW))
    need(rc == 0 and "UNREACHABLE" not in out and "DRIFT" not in out, "clean run rc=%r" % (rc,))


def case_record_fifo_not_waited_on(sc):
    fifo = os.path.join(sc.out, "fifo")
    os.mkfifo(fifo)
    rc, out, err = sc.drift(fifo, timeout=10)
    need(rc is not None, "tool blocked opening a record FIFO")
    need(rc == 2 and "RECORD-MALFORMED" in err, "rc=%r err=%r" % (rc, err[-120:]))


def case_row_prefix_sibling_outside_root(sc):
    rc, out, err = sc.drift(sc.record("REPO\t../root2\tregs=1\tprunable=0\n"))
    need(rc == 2 and "RECORD-OUTSIDE-ROOT" in err, "rc=%r err=%r" % (rc, err[-120:]))


def case_gitdir_prefix_sibling_outside_root(sc):
    gd = os.path.join(sc.dir, "rootX", "gd")
    os.makedirs(gd)
    subprocess.run(["git", "init", "-q", "--bare", gd], env=ENV, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=True)
    os.makedirs(os.path.join(sc.root, "s"))
    put(os.path.join(sc.root, "s", ".git"), "gitdir: " + gd + "\n")
    rc, out, err = sc.drift(sc.record("REPO\ts\tregs=1\tprunable=0\n"))
    need(rc == 2 and "RECORD-OUTSIDE-ROOT" in err, "rc=%r err=%r" % (rc, err[-120:]))


def case_timeout_one_is_valid(sc):
    rc, out, err = sc.drift(sc.record("REPO\ta\tregs=1\tprunable=0\n"), ["--timeout", "1"])
    need(rc == 1 and "ABSENT" in out and "REFUSAL" not in err, "rc=%r err=%r" % (rc, err[-120:]))


def hang_head(sc):
    """Replace repository t's HEAD with a FIFO: every git call opening it blocks."""
    git_init(os.path.join(sc.root, "t"))
    head = os.path.join(sc.root, "t", ".git", "HEAD")
    os.remove(head)
    os.mkfifo(head)
    return head


def case_hung_git_reported_as_list_timeout(sc):
    hang_head(sc)
    rc, out, err = sc.drift(sc.record("REPO\tt\tregs=1\tprunable=0\n"), ["--timeout", "1"])
    need(rc == 1 and "UNREACHABLE:list-timeout" in out, "rc=%r out=%r err=%r" % (
        rc, out[-120:], err[-120:]))


def case_default_timeout_lets_slow_git_finish(sc):
    head = hang_head(sc)
    stop = threading.Event()

    def serve():
        first = True
        while not stop.is_set():
            try:
                fd = os.open(head, os.O_WRONLY | os.O_NONBLOCK)
            except OSError as exc:
                if exc.errno != errno.ENXIO:
                    return
                time.sleep(0.02)
                continue
            try:
                os.set_blocking(fd, True)
                if first:
                    first = False
                    time.sleep(SLOW_GIT_DELAY)
                os.write(fd, b"ref: refs/heads/main\n")
            except OSError:
                pass
            finally:
                os.close(fd)

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    try:
        rc, out, err = sc.drift(sc.record("REPO\tt\tregs=1\tprunable=0\n"))
    finally:
        stop.set()
        thread.join(10)
    need(rc == 0 and "UNREACHABLE" not in out and "DRIFT" not in out,
         "rc=%r out=%r err=%r" % (rc, out[-160:], err[-120:]))


def case_failing_worktree_list_reported_as_list_rc(sc):
    os.makedirs(os.path.join(sc.root, "u", ".git"))
    rc, out, err = sc.drift(sc.record("REPO\tu\tregs=1\tprunable=0\n"))
    need(rc == 1 and "UNREACHABLE:list-rc=" in out, "rc=%r out=%r err=%r" % (rc, out[-160:], err[-120:]))


def case_root_is_required(sc):
    rc, out, err = sc.run(["--record", sc.record(ROW)])
    need(rc == 2 and "required" in err and "--root" in err, "rc=%r err=%r" % (rc, err[-160:]))


def case_record_is_required(sc):
    rc, out, err = sc.run(["--root", sc.root])
    need(rc == 2 and "required" in err and "--record" in err, "rc=%r err=%r" % (rc, err[-160:]))


def case_symlinked_child_is_not_discovered(sc):
    git_init(os.path.join(sc.root, "other"))
    os.symlink(os.path.join(sc.root, "other"), os.path.join(sc.root, "lnk"))
    rc, out, err = sc.run(["--root", sc.root, "--record", sc.record(ROW)])
    need(rc == 1 and "UNRECORDED" in out and "other" in out, "rc=%r out=%r" % (rc, out[-160:]))
    need("lnk" not in out, "symlinked child reported: %r" % out[-160:])


def case_regs_holds_two_digits(sc):
    rc, out, err = sc.drift(sc.record("REPO\tr\tregs=10\tprunable=0\n"))
    need(rc == 1 and "record=10" in out and "REFUSAL" not in err, "rc=%r out=%r err=%r" % (
        rc, out[-160:], err[-120:]))


def case_json_overwrite_truncates(sc):
    target = put(os.path.join(sc.out, "out.json"), "x" * 20000)
    rc, out, err = sc.drift(sc.record(ROW), ["--json", target])
    need(rc == 0, "rc=%r err=%r" % (rc, err[-120:]))
    with open(target, "rb") as handle:
        data = handle.read()
    try:
        doc = json.loads(data.decode("utf-8"))
    except ValueError as exc:
        raise Fail("json file is not one JSON document: %s" % exc)
    need(isinstance(doc, dict) and len(data) < 20000, "json file kept old bytes (%d)" % len(data))


def case_invalid_utf8_name_becomes_replacement_char(sc):
    # U+FFFD spelled as raw bytes: the directory name the `replace` handler produces.
    git_init(os.path.join(os.fsencode(sc.root), b"al\xef\xbf\xbdpha"))
    rc, out, err = sc.drift(put(os.path.join(sc.out, "rec"), b"REPO\tal\xffpha\tregs=1\tprunable=0\n"))
    need(rc == 0 and "ABSENT" not in out and "DRIFT" not in out,
         "rc=%r out=%r err=%r" % (rc, out[-160:], err[-120:]))


CASES = [
    ("baseline-clean-run", case_baseline),
    ("record-fifo-not-waited-on", case_record_fifo_not_waited_on),
    ("row-prefix-sibling-outside-root", case_row_prefix_sibling_outside_root),
    ("gitdir-prefix-sibling-outside-root", case_gitdir_prefix_sibling_outside_root),
    ("timeout-one-is-valid", case_timeout_one_is_valid),
    ("hung-git-reported-as-list-timeout", case_hung_git_reported_as_list_timeout),
    ("default-timeout-lets-slow-git-finish", case_default_timeout_lets_slow_git_finish),
    ("failing-worktree-list-reported-as-list-rc", case_failing_worktree_list_reported_as_list_rc),
    ("root-is-required", case_root_is_required),
    ("record-is-required", case_record_is_required),
    ("symlinked-child-is-not-discovered", case_symlinked_child_is_not_discovered),
    ("regs-holds-two-digits", case_regs_holds_two_digits),
    ("json-overwrite-truncates", case_json_overwrite_truncates),
    ("invalid-utf8-name-becomes-replacement-char", case_invalid_utf8_name_becomes_replacement_char),
]


def run_case(work, tool, name, fn):
    try:
        fn(Scenario(work, name, tool))
        return name, True, ""
    except Fail as exc:
        return name, False, str(exc)
    except Exception as exc:  # noqa: BLE001 - any harness error is a failed case, never a traceback
        return name, False, "%s: %s" % (type(exc).__name__, exc)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r42-drift-conditions: refusing to run as root\n")
        return 2
    tool = os.path.abspath(args.tool)
    if not os.path.isfile(tool) or not os.path.isdir(args.work):
        sys.stderr.write("usage: --tool must name a file and --work an existing directory\n")
        return 2
    work = os.path.realpath(tempfile.mkdtemp(prefix="r42-drift-", dir=args.work))
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(CASES)) as pool:
            futures = [pool.submit(run_case, work, tool, n, f) for n, f in CASES]
            results = [f.result() for f in futures]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    failed = sum(1 for _, ok, _ in results if not ok)
    print("SUMMARY cases=%d pass=%d fail=%d" % (len(results), len(results) - failed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
