#!/usr/bin/env python3
"""r42-drift-conditions.py — condition-level behaviours of tools/souji-worktree-drift.py.

Every case builds its own scenario under --work, runs the tool as a subprocess and asserts what the
tool does: exit code, stdout/stderr tokens, or the bytes of the --json file it writes. No case reads
the tool's source, a label or a digest.

Cases (the condition each one pins):
  record-fifo-not-blocking      a FIFO record is refused (exit 2 RECORD-MALFORMED) instead of blocking the open
  row-sibling-prefix-outside    a row resolving to a sibling dir sharing the root's name prefix is outside
  gitdir-sibling-prefix-outside a gitdir in a sibling dir sharing the root's name prefix is outside
  timeout-one-accepted          --timeout 1 is a valid value
  timeout-zero-refused          --timeout 0 is a usage refusal
  timeout-default-allows-slow   without --timeout a git that needs a couple of seconds still answers
  list-timeout-reported         a git that blocks past --timeout is reported UNREACHABLE:list-timeout, not a crash
  list-rc-reported              a failing `worktree list` is reported UNREACHABLE:list-rc=
  root-required                 omitting --root is an argparse usage error (exit 2, "required")
  record-required               omitting --record is an argparse usage error (exit 2, "required")
  symlink-child-skipped         a symlinked child directory is not discovered as an unrecorded repository
  regs-two-digits               a two-digit regs count parses and drifts as record=10 live=1
  json-truncates-old-file       --json over a longer old file leaves exactly the new document
  record-invalid-utf8-replaced  an undecodable byte in a repository name becomes U+FFFD, not a backslash escape

CLI:
  python3 -B tests/fixtures/r42-drift-conditions.py --tool PATH --work DIR
Output: `case-<name>=PASS|FAIL` lines and `SUMMARY cases=<n> pass=<p> fail=<f>`.
Exit: 0 all cases pass, 1 any case fails, 2 usage or refused (root).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

BASE_ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C",
    "PYTHONIOENCODING": "utf-8",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}
ROW = b"REPO\tr\tregs=1\tprunable=0\n"


class Scene:
    def __init__(self, work, name):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="c-%s." % name, dir=work))
        self.root = self.tmp + "/root"
        self.out = self.tmp + "/o"
        os.makedirs(self.root)
        os.makedirs(self.out)
        self.env = dict(BASE_ENV)
        self.env["TMPDIR"] = self.tmp

    def git_init(self, path, bare=False):
        cmd = ["git", "init", "-q"] + (["--bare"] if bare else []) + [path]
        subprocess.run(cmd, env=self.env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def repo(self, name="r"):
        self.git_init(self.root + "/" + name)
        return self.root + "/" + name

    def write(self, path, data):
        with open(path, "wb") as handle:
            handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))
        return path

    def run(self, tool, args, timeout=60, env=None, cwd=None):
        try:
            return subprocess.run(["python3", "-B", tool] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=timeout, env=env or self.env, cwd=cwd or self.tmp, check=False)
        except subprocess.TimeoutExpired:
            return None

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def text(p, stream):
    return getattr(p, stream).decode("utf-8", "replace")


def refused(p, cls):
    return p is not None and p.returncode == 2 and ("REFUSAL %s:" % cls) in text(p, "stderr")


def case_record_fifo_not_blocking(tool, s):
    s.repo()
    os.mkfifo(s.out + "/fifo")
    p = s.run(tool, ["--root", s.root, "--record", s.out + "/fifo", "--skip-unrecorded"], timeout=15)
    return refused(p, "RECORD-MALFORMED")


def case_row_sibling_prefix_outside(tool, s):
    s.repo()
    os.makedirs(s.tmp + "/root2")
    rec = s.write(s.out + "/rec", "REPO\t../root2\tregs=1\tprunable=0\n")
    return refused(s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded"]), "RECORD-OUTSIDE-ROOT")


def case_gitdir_sibling_prefix_outside(tool, s):
    s.repo()
    os.makedirs(s.tmp + "/rootX")
    gd = s.tmp + "/rootX/gd"
    s.git_init(gd, bare=True)
    os.makedirs(s.root + "/s")
    s.write(s.root + "/s/.git", "gitdir: " + gd + "\n")
    rec = s.write(s.out + "/rec", "REPO\ts\tregs=1\tprunable=0\n")
    return refused(s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded"]), "RECORD-OUTSIDE-ROOT")


def case_timeout_one_accepted(tool, s):
    rec = s.write(s.out + "/rec", "REPO\ta\tregs=1\tprunable=0\n")
    s.repo()
    p = s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded", "--timeout", "1"])
    return p is not None and p.returncode == 1 and "DRIFT\tABSENT\ta" in text(p, "stdout")


def case_timeout_zero_refused(tool, s):
    rec = s.write(s.out + "/rec", ROW)
    s.repo()
    p = s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded", "--timeout", "0"])
    return refused(p, "USAGE")


def case_timeout_default_allows_slow(tool, s):
    s.repo()
    real = shutil.which("git", path=BASE_ENV["PATH"])
    if not real:
        return False
    shim = s.tmp + "/shim"
    os.makedirs(shim)
    s.write(shim + "/git", "#!%s\nimport os, sys, time\ntime.sleep(2.5)\nos.execv(%r, [%r] + sys.argv[1:])\n"
            % (sys.executable, real, real))
    os.chmod(shim + "/git", 0o755)
    env = dict(s.env)
    env["PATH"] = shim + os.pathsep + BASE_ENV["PATH"]
    rec = s.write(s.out + "/rec", ROW)
    p = s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded"], env=env, timeout=90)
    return p is not None and p.returncode == 0 and "DRIFT" not in text(p, "stdout")


def case_list_timeout_reported(tool, s):
    s.repo()
    t = s.repo("t")
    os.remove(t + "/.git/HEAD")
    os.mkfifo(t + "/.git/HEAD")
    rec = s.write(s.out + "/rec", ROW + b"REPO\tt\tregs=1\tprunable=0\n")
    p = s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded", "--timeout", "1"], timeout=60)
    return (p is not None and p.returncode == 1
            and "DRIFT\tUNREACHABLE\tt\tUNREACHABLE:list-timeout" in text(p, "stdout")
            and "Traceback" not in text(p, "stderr"))


def case_list_rc_reported(tool, s):
    s.repo()
    os.makedirs(s.root + "/u/.git")
    rec = s.write(s.out + "/rec", ROW + b"REPO\tu\tregs=1\tprunable=0\n")
    p = s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded"])
    return (p is not None and p.returncode == 1
            and "DRIFT\tUNREACHABLE\tu\tUNREACHABLE:list-rc=" in text(p, "stdout"))


def case_root_required(tool, s):
    rec = s.write(s.out + "/rec", ROW)
    s.repo()
    empty = s.tmp + "/emptycwd"
    os.makedirs(empty)
    p = s.run(tool, ["--record", rec, "--skip-unrecorded"], cwd=empty)
    err = text(p, "stderr") if p else ""
    return p is not None and p.returncode == 2 and "required" in err and "--root" in err


def case_record_required(tool, s):
    s.repo()
    p = s.run(tool, ["--root", s.root, "--skip-unrecorded"])
    err = text(p, "stderr") if p else ""
    return p is not None and p.returncode == 2 and "required" in err and "--record" in err


def case_symlink_child_skipped(tool, s):
    s.repo()
    u2 = s.repo("u2")
    os.symlink(u2, s.root + "/lnk")
    rec = s.write(s.out + "/rec", ROW)
    p = s.run(tool, ["--root", s.root, "--record", rec])
    out = text(p, "stdout") if p else ""
    return (p is not None and p.returncode == 1 and "DRIFT\tUNRECORDED\tu2" in out
            and "UNRECORDED\tlnk" not in out)


def case_regs_two_digits(tool, s):
    s.repo()
    rec = s.write(s.out + "/rec", "REPO\tr\tregs=10\tprunable=0\n")
    p = s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded"])
    return p is not None and p.returncode == 1 and "record=10 live=1" in text(p, "stdout")


def case_json_truncates_old_file(tool, s):
    s.repo()
    rec = s.write(s.out + "/rec", ROW)
    out = s.write(s.out + "/old.json", b"x" * 5000)
    p = s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded", "--json", out])
    if p is None or p.returncode != 0:
        return False
    with open(out, "rb") as handle:
        doc = json.loads(handle.read().decode("utf-8"))
    return isinstance(doc, dict) and "summary" in doc and doc.get("drift") == []


def case_record_invalid_utf8_replaced(tool, s):
    s.repo()
    rec = s.write(s.out + "/rec", b"REPO\tal\xffpha\tregs=1\tprunable=0\n")
    p = s.run(tool, ["--root", s.root, "--record", rec, "--skip-unrecorded"])
    if p is None or p.returncode != 1:
        return False
    out = p.stdout
    return b"ABSENT" in out and b"al\xef\xbf\xbdpha" in out and b"\\xff" not in out


CASES = [(n[len("case_"):].replace("_", "-"), f) for n, f in sorted(globals().items())
         if n.startswith("case_")]


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r42-drift-conditions: refusing to run as root\n")
        return 2
    os.makedirs(a.work, exist_ok=True)
    tool = os.path.abspath(a.tool)
    work = os.path.realpath(a.work)
    bad = 0
    for name, fn in CASES:
        s = None
        try:
            s = Scene(work, name)
            good = bool(fn(tool, s))
        except Exception as exc:  # noqa: BLE001 - a scenario that cannot be built is a failed case
            good = False
            sys.stdout.write("note-%s=%s: %s\n" % (name, type(exc).__name__, str(exc)[:120]))
        finally:
            if s is not None:
                s.cleanup()
        bad += not good
        sys.stdout.write("case-%s=%s\n" % (name, "PASS" if good else "FAIL"))
    sys.stdout.write("SUMMARY cases=%d pass=%d fail=%d\n" % (len(CASES), len(CASES) - bad, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
