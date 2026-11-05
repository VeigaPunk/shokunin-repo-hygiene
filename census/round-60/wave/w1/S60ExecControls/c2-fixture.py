#!/usr/bin/env python3
"""C2 fixture, minimal equivalent (souji round 60 pre-freeze controls, seat S60ExecControls).

The wave's fixture seat (S60ExecRecorderFix) had delivered nothing into
.ufo/waves/round-60/w1/ at control time, so this fixture rebuilds the frozen
8-case design from the wave spec and scores any receipt writer:

  python3 -B c2-fixture.py --tool PATH --work DIR

--tool is the writer under test, e.g. the base recorder
census/round-57/record-receipt.sh (shell ABI: `record-receipt.sh LANE REV
INSTR OUT -- cmd...`) or a python writer with the S60ExecRecorder ABI
(`--root LANE --rev REV --instrument PATH --out FILE [--max-bytes N] -- cmd...`).
Python-only flags (--max-bytes) are passed verbatim before `--` in the shell
ABI too; the base recorder then treats them as part of the wrapped command and
fails that case deterministically.

Cases (fresh output subdir each; re-runnable):
  1 clean-write        5 bound
  2 overwrite          6 rev-short
  3 atomic-in-flight   7 instrument-absent
  4 kill-residue       8 dirty-tree

Prints `CASE <n> <name> pass|fail` per case, then
`SUMMARY cases=8 pass=<p> fail=<f> control=ALWAYS-WRITE-REJECTED|ACCEPTED,ALWAYS-REFUSE-REJECTED|ACCEPTED`.
Exit 0 iff pass=8 and both stub controls are rejected (always-write must fail
cases 2/4/5/6/7/8; always-refuse must fail case 1); 1 otherwise.

The fixture repo is a synthetic lane built under --work/lane (git init,
toplevel asserted equal before the first commit, throwaway identity scoped by
environment and used only there).
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
from fnmatch import fnmatch

FULL40 = re.compile(r"^[0-9a-f]{40}$")
FAST_CMD = ["sh", "-c", "echo ok"]
SLOW_CMD = ["sh", "-c", "sleep 1; echo done"]
BIG_CMD = ["sh", "-c", "head -c 2097152 /dev/zero | tr '\\0' x"]
SENTINEL = b"SENTINEL-r60-c2-control\n"
INSTRUMENT = "tools/instr.py"
INSTRUMENT_BYTES = "print('instr-v60')\n"
DIRT = "dirt.txt"

STUB_ALWAYS_WRITE = '''#!/usr/bin/env python3
"""stub control: always writes a receipt-shaped OUT and exits 0."""
import sys

args = sys.argv[1:]
out = None
for i, a in enumerate(args):
    if a == "--out" and i + 1 < len(args):
        out = args[i + 1]
if out is None and len(args) >= 4:
    out = args[3]
if out:
    with open(out, "w") as fh:
        fh.write("instrument=stub\\ninstrument_sha256=%s\\nrev=stub\\ncommand=stub\\nEXIT=0\\n"
                 % ("0" * 64))
sys.exit(0)
'''

STUB_ALWAYS_REFUSE = '''#!/usr/bin/env python3
"""stub control: always refuses with exit 2 and writes nothing."""
import sys
print("FINDING S0 STUB-ALWAYS-REFUSE refuses every case")
sys.exit(2)
'''


def git_env():
    return {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
            "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_AUTHOR_NAME": "r60-controls", "GIT_AUTHOR_EMAIL": "r60-controls@fixture.invalid",
            "GIT_COMMITTER_NAME": "r60-controls", "GIT_COMMITTER_EMAIL": "r60-controls@fixture.invalid"}


def git(repo, *args):
    p = subprocess.run(["git", "-C", repo] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=git_env())
    if p.returncode != 0:
        raise RuntimeError("git -C %s %s -> %d: %s" % (repo, " ".join(args), p.returncode,
                                                       p.stderr.decode("utf-8", "replace").strip()))
    return p.stdout.decode("utf-8", "replace").strip()


def last_line(path):
    with open(path, "rb") as fh:
        data = fh.read()
    lines = data.decode("utf-8", "replace").splitlines()
    return lines[-1] if lines else ""


class Fixture:
    def __init__(self, tool, work):
        self.tool = os.path.abspath(tool)
        self.work = os.path.abspath(work)
        self.lane = os.path.join(self.work, "lane")
        self.py = sys.executable or "python3"
        shutil.rmtree(self.lane, ignore_errors=True)
        os.makedirs(os.path.join(self.lane, "tools"))
        subprocess.run(["git", "-C", self.lane, "init", "-q"], check=True, env=git_env(),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        top = subprocess.run(["git", "-C", self.lane, "rev-parse", "--show-toplevel"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=git_env())
        top_out = top.stdout.decode("utf-8", "replace").strip()
        if top.returncode != 0 or os.path.realpath(top_out) != os.path.realpath(self.lane):
            raise RuntimeError("fixture rule violated: toplevel %r != %s" % (top_out, self.lane))
        with open(os.path.join(self.lane, INSTRUMENT), "w") as fh:
            fh.write(INSTRUMENT_BYTES)
        with open(os.path.join(self.lane, "a.txt"), "w") as fh:
            fh.write("a\n")
        git(self.lane, "add", "-A")
        git(self.lane, "commit", "-q", "-m", "r60 c2 fixture lane")
        self.rev = git(self.lane, "rev-parse", "HEAD")
        if not FULL40.match(self.rev):
            raise RuntimeError("fixture lane HEAD is not full 40-hex: %r" % self.rev)
        # raw bytes: the expected digest must be over the exact blob, never a
        # decoded/stripped round-trip (the recorder hashes `git show` bytes)
        p = subprocess.run(["git", "-C", self.lane, "cat-file", "blob",
                            "%s:%s" % (self.rev, INSTRUMENT)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=git_env(), check=True)
        self.sha_instr = hashlib.sha256(p.stdout).hexdigest()
        self.case_no = 0

    def argv(self, out, cmd, rev=None, instr=None, extra=None, tool=None):
        tool = self.tool if tool is None else os.path.abspath(tool)
        rev = self.rev if rev is None else rev
        instr = INSTRUMENT if instr is None else instr
        if tool.endswith(".sh"):
            return ["bash", tool, self.lane, rev, instr, out] + list(extra or []) + ["--"] + list(cmd)
        return [self.py, "-B", tool, "--root", self.lane, "--rev", rev,
                "--instrument", instr, "--out", out] + list(extra or []) + ["--"] + list(cmd)

    def fresh_dir(self, name):
        self.case_no += 1
        d = os.path.join(self.work, "case-%d-%s" % (self.case_no, name))
        os.makedirs(d)
        return d

    def tmp_siblings(self, out):
        parent = os.path.dirname(os.path.abspath(out))
        if not os.path.isdir(parent):
            return []
        return sorted(b for b in os.listdir(parent)
                      if fnmatch(b, "*.tmp*") or fnmatch(b, "*.partial*"))

    def run(self, argv, timeout=60):
        try:
            p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=timeout)
        except subprocess.TimeoutExpired:
            return 124, ["TIMEOUT"]
        return p.returncode, p.stdout.decode("utf-8", "replace").splitlines()

    def spawn(self, argv):
        return subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)


def case_clean(fx, tool=None):
    d = fx.fresh_dir("clean")
    out = os.path.join(d, "out.txt")
    rc, _lines = fx.run(fx.argv(out, FAST_CMD, tool=tool))
    problems = []
    if rc != 0:
        problems.append("tool exit %d != 0" % rc)
    if not os.path.isfile(out):
        problems.append("OUT absent")
    else:
        body = open(out, encoding="utf-8", errors="replace").read().splitlines()
        want = {"instrument=" + INSTRUMENT, "instrument_sha256=" + fx.sha_instr, "rev=" + fx.rev}
        missing = want - set(body)
        if missing:
            problems.append("missing lines: %s" % sorted(missing))
        if not any(l.startswith("command=") and len(l) > len("command=") for l in body):
            problems.append("no command= line")
        if not body or body[-1] != "EXIT=0":
            problems.append("last line %r != EXIT=0" % (body[-1] if body else ""))
    sibs = fx.tmp_siblings(out)
    if sibs:
        problems.append("temp siblings: %s" % sibs)
    return problems


def case_overwrite(fx, tool=None):
    d = fx.fresh_dir("overwrite")
    out = os.path.join(d, "out.txt")
    with open(out, "wb") as fh:
        fh.write(SENTINEL)
    rc, _lines = fx.run(fx.argv(out, FAST_CMD, tool=tool))
    problems = []
    if rc != 2:
        problems.append("tool exit %d != 2" % rc)
    with open(out, "rb") as fh:
        if fh.read() != SENTINEL:
            problems.append("OUT bytes changed")
    sibs = fx.tmp_siblings(out)
    if sibs:
        problems.append("temp siblings: %s" % sibs)
    return problems


def case_inflight(fx, tool=None):
    d = fx.fresh_dir("atomic-in-flight")
    out = os.path.join(d, "out.txt")
    p = fx.spawn(fx.argv(out, SLOW_CMD, tool=tool))
    time.sleep(0.3)
    absent = not os.path.exists(out)
    try:
        p.wait(timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
        return ["tool did not exit within 30s"]
    problems = []
    if not absent:
        problems.append("OUT existed at ~0.3s (mid-flight)")
    if not os.path.isfile(out):
        problems.append("OUT absent after completion")
    elif last_line(out) != "EXIT=0":
        problems.append("last line %r != EXIT=0" % last_line(out))
    return problems


def case_kill(fx, tool=None):
    d = fx.fresh_dir("kill-residue")
    out = os.path.join(d, "out.txt")
    p = fx.spawn(fx.argv(out, SLOW_CMD, tool=tool))
    time.sleep(0.4)
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        p.wait(timeout=30)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
    problems = []
    if os.path.exists(out):
        problems.append("OUT present after SIGKILL")
    sibs = fx.tmp_siblings(out)
    if sibs:
        problems.append("residue siblings: %s" % sibs)
    return problems


def case_bound(fx, tool=None):
    d = fx.fresh_dir("bound")
    out = os.path.join(d, "out.txt")
    rc, _lines = fx.run(fx.argv(out, BIG_CMD, extra=["--max-bytes", "65536"], tool=tool))
    problems = []
    if rc != 2:
        problems.append("tool exit %d != 2" % rc)
    if os.path.exists(out):
        problems.append("OUT present")
    sibs = fx.tmp_siblings(out)
    if sibs:
        problems.append("temp siblings: %s" % sibs)
    return problems


def case_rev_short(fx, tool=None):
    d = fx.fresh_dir("rev-short")
    out = os.path.join(d, "out.txt")
    rc, _lines = fx.run(fx.argv(out, FAST_CMD, rev=fx.rev[:12], tool=tool))
    problems = []
    if rc != 2:
        problems.append("tool exit %d != 2" % rc)
    if os.path.exists(out):
        problems.append("OUT present")
    sibs = fx.tmp_siblings(out)
    if sibs:
        problems.append("temp siblings: %s" % sibs)
    return problems


def case_instr_absent(fx, tool=None):
    d = fx.fresh_dir("instrument-absent")
    out = os.path.join(d, "out.txt")
    rc, _lines = fx.run(fx.argv(out, FAST_CMD, instr="tools/absent.py", tool=tool))
    problems = []
    if rc != 2:
        problems.append("tool exit %d != 2" % rc)
    if os.path.exists(out):
        problems.append("OUT present")
    sibs = fx.tmp_siblings(out)
    if sibs:
        problems.append("temp siblings: %s" % sibs)
    return problems


def case_dirty(fx, tool=None):
    d = fx.fresh_dir("dirty-tree")
    out = os.path.join(d, "out.txt")
    dirt = os.path.join(fx.lane, DIRT)
    problems = []
    try:
        with open(dirt, "w") as fh:
            fh.write("untracked\n")
        rc, _lines = fx.run(fx.argv(out, FAST_CMD, tool=tool))
        if rc != 2:
            problems.append("tool exit %d != 2" % rc)
        if os.path.exists(out):
            problems.append("OUT present")
        sibs = fx.tmp_siblings(out)
        if sibs:
            problems.append("temp siblings: %s" % sibs)
    finally:
        if os.path.exists(dirt):
            os.remove(dirt)
    return problems


CASES = [
    (1, "clean", case_clean),
    (2, "overwrite", case_overwrite),
    (3, "atomic-in-flight", case_inflight),
    (4, "kill-residue", case_kill),
    (5, "bound", case_bound),
    (6, "rev-short", case_rev_short),
    (7, "instrument-absent", case_instr_absent),
    (8, "dirty-tree", case_dirty),
]
ALWAYS_WRITE_MUST_FAIL = (2, 4, 5, 6, 7, 8)


def stub_control(fx, work):
    sw = os.path.join(work, "stub-always-write.py")
    sr = os.path.join(work, "stub-always-refuse.py")
    with open(sw, "w", encoding="utf-8") as fh:
        fh.write(STUB_ALWAYS_WRITE)
    with open(sr, "w", encoding="utf-8") as fh:
        fh.write(STUB_ALWAYS_REFUSE)
    aw_failed = []
    for n, _name, fn in CASES:
        if n in ALWAYS_WRITE_MUST_FAIL:
            if fn(fx, tool=sw):
                aw_failed.append(n)
    ar_failed = [1] if case_clean(fx, tool=sr) else []
    aw_rej = sorted(aw_failed) == sorted(ALWAYS_WRITE_MUST_FAIL)
    ar_rej = bool(ar_failed)
    return aw_rej, len(aw_failed), ar_rej, len(ar_failed)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Round-60 C2 receipt-writer fixture (minimal equivalent).")
    ap.add_argument("--tool", required=True, help="receipt writer under test")
    ap.add_argument("--work", required=True, help="scratch dir for the fixture lane and case dirs")
    args = ap.parse_args(argv)
    if not os.path.isfile(args.tool):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --tool %s is missing\n" % args.tool)
        return 2
    try:
        os.makedirs(args.work, exist_ok=True)
        fx = Fixture(args.tool, args.work)
    except Exception as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: fixture build failed: %s: %s\n"
                         % (type(exc).__name__, exc))
        return 2
    print("# c2-fixture minimal equivalent (souji round 60 pre-freeze control, seat S60ExecControls)")
    print("TOOL %s" % fx.tool)
    print("LANE-FIXTURE %s rev=%s instrument=%s instrument_sha256=%s"
          % (fx.lane, fx.rev, INSTRUMENT, fx.sha_instr))
    passed = 0
    for n, name, fn in CASES:
        problems = fn(fx)
        ok = not problems
        passed += 1 if ok else 0
        print("CASE %d %s %s" % (n, name, "pass" if ok else "fail"))
        for pr in problems:
            print("  reason: %s" % pr)
    aw_rej, aw_failed, ar_rej, ar_failed = stub_control(fx, args.work)
    print("STUB always-write cases=%d failed=%d %s"
          % (len(ALWAYS_WRITE_MUST_FAIL), aw_failed, "REJECTED" if aw_rej else "ACCEPTED"))
    print("STUB always-refuse cases=1 failed=%d %s"
          % (ar_failed, "REJECTED" if ar_rej else "ACCEPTED"))
    print("SUMMARY cases=8 pass=%d fail=%d control=ALWAYS-WRITE-%s,ALWAYS-REFUSE-%s"
          % (passed, 8 - passed, "REJECTED" if aw_rej else "ACCEPTED",
             "REJECTED" if ar_rej else "ACCEPTED"))
    return 0 if (passed == 8 and aw_rej and ar_rej) else 1


if __name__ == "__main__":
    sys.exit(main())
