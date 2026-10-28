#!/usr/bin/env python3
"""tests/fixtures/r41-refusal-sites.py — r41 C3: one class-asserting probe per refusal site.

Protocol (census/round-41/c3-counter.py):
  python3 -B r41-refusal-sites.py --tool PATH --work DIR
  stdout: one `probe-<ID>=PASS|FAIL [detail]` line per probe id, then
          `SUMMARY probes=<n> pass=<p> fail=<f>`; exit 0 iff fail=0, else 1.
  Exit 2 (message on stderr, no probe lines) when the uid is 0 or the arguments are unusable:
  the EACCES probes (P02a, P18) change class under a privileged runner and are never skipped.

Every probe builds its own trigger in a private directory under --work, runs the tool with an
explicit timeout, and asserts BOTH exit code 2 AND the exact stderr token `REFUSAL <CLASS>:` for
the class its site raises, plus a detail substring that separates same-class sites (S01/S03 and
S12/S19 share a class and a message family). A probe reaches one site only. A timeout, a spawn
failure or any unexpected exception is a FAIL line carrying the probe id, never a traceback.
Stdlib only; no network; writes only under --work (the private directory is removed on exit).
"""
import argparse
import os
import shutil
import stat
import subprocess
import sys
import tempfile

RUN_TIMEOUT = 30   # seconds for one tool run (the tool's own --timeout is 5)
GIT_TIMEOUT = 30   # seconds for one fixture-side git init
TOOL_TIMEOUT = "5"
NULL = os.devnull


class Probe(Exception):
    """A probe assertion failed; the message is the one-line detail."""


def child_env(work):
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "LC_ALL": "C",
        "TMPDIR": work,
        "HOME": work,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": NULL,
        "GIT_CONFIG_SYSTEM": NULL,
        "GIT_TERMINAL_PROMPT": "0",
    }


class Ctx:
    def __init__(self, tool, base):
        self.tool = tool
        self.base = base
        self.env = child_env(base)

    def mkdir(self, *parts):
        path = os.path.join(*parts)
        os.makedirs(path, exist_ok=True)
        return path

    def write(self, path, text):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def git_init(self, path, *flags):
        os.makedirs(path, exist_ok=True)
        try:
            proc = subprocess.run(["git", "-C", path, "init", "-q"] + list(flags),
                                  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=self.env, timeout=GIT_TIMEOUT,
                                  check=False)
        except subprocess.TimeoutExpired:
            raise Probe("fixture git init timed out after %ds" % GIT_TIMEOUT)
        if proc.returncode != 0:
            raise Probe("fixture git init failed rc=%d" % proc.returncode)

    def run_tool(self, args):
        cmd = [sys.executable, "-B", self.tool] + list(args)
        try:
            proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=self.env, timeout=RUN_TIMEOUT,
                                  check=False)
        except subprocess.TimeoutExpired:
            raise Probe("tool timed out after %ds" % RUN_TIMEOUT)
        return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")

    def expect(self, args, cls, detail):
        """Run the tool; require exit 2, stderr token 'REFUSAL <cls>:' and the detail substring."""
        rc, _out, err = self.run_tool(args)
        token = "REFUSAL %s:" % cls
        if rc != 2:
            raise Probe("exit %d, want 2 (stderr=%r)" % (rc, err[:160]))
        if token not in err:
            raise Probe("stderr lacks %r (stderr=%r)" % (token, err[:160]))
        if detail not in err:
            raise Probe("stderr lacks detail %r (stderr=%r)" % (detail, err[:160]))
        return err


def tool_args(root, record, *extra):
    return ["--root", root, "--record", record, "--timeout", TOOL_TIMEOUT] + list(extra)


def record_case(ctx, pid, body, cls, detail, record_is=None):
    """Parse-stage case: an empty root and a record built from `body`."""
    d = ctx.mkdir(ctx.base, pid)
    root = ctx.mkdir(d, "root")
    record = record_is or ctx.write(os.path.join(d, "record.tsv"), body)
    ctx.expect(tool_args(root, record), cls, detail)


ROW_A = "REPO\ta\tregs=1\tprunable=0\n"


def p01(ctx):
    d = ctx.mkdir(ctx.base, "P01")
    root = ctx.mkdir(d, "root")
    record = os.path.join(d, "no-such-record.tsv")
    if os.path.lexists(record):
        raise Probe("trigger not built: record exists")
    ctx.expect(tool_args(root, record), "RECORD-MALFORMED", "is not a regular file")


def p02a(ctx):
    d = ctx.mkdir(ctx.base, "P02a")
    root = ctx.mkdir(d, "root")
    record = ctx.write(os.path.join(d, "record.tsv"), ROW_A)
    os.chmod(record, 0)
    try:
        if os.access(record, os.R_OK):
            raise Probe("trigger not built: chmod 000 record is still readable")
        ctx.expect(tool_args(root, record), "RECORD-MISSING", "Errno 13")
    finally:
        os.chmod(record, 0o600)


def p02b(ctx):
    d = ctx.mkdir(ctx.base, "P02b")
    root = ctx.mkdir(d, "root")
    a = os.path.join(d, "loop-a")
    b = os.path.join(d, "loop-b")
    os.symlink(b, a)
    os.symlink(a, b)
    ctx.expect(tool_args(root, a), "RECORD-MISSING", "Errno 40")


def p03(ctx):
    d = ctx.mkdir(ctx.base, "P03")
    root = ctx.mkdir(d, "root")
    record = ctx.mkdir(d, "record-is-a-directory")
    ctx.expect(tool_args(root, record), "RECORD-MALFORMED", "is not a regular file")


def p04(ctx):
    record_case(ctx, "P04", ROW_A + ROW_A, "RECORD-MALFORMED", "duplicates a")


def p05(ctx):
    record_case(ctx, "P05", ROW_A + "this line is not a census row\n", "RECORD-MALFORMED",
                "does not match the census schema")


def p06(ctx):
    record_case(ctx, "P06", "# only a comment\n\n   \n# another\n", "RECORD-EMPTY", "no REPO rows")


def p07(ctx):
    record_case(ctx, "P07", ROW_A + "TOTAL\trepos=2\tregs=1\tprunable=0\n", "RECORD-MALFORMED",
                "TOTAL repos=2 but 1 REPO rows")


def p08(ctx):
    record_case(ctx, "P08", ROW_A + "TOTAL\trepos=1\tregs=2\tprunable=0\n", "RECORD-MALFORMED",
                "TOTAL regs=2 but REPO rows sum to 1")


def p09(ctx):
    record_case(ctx, "P09", ROW_A + "TOTAL\trepos=1\tregs=1\tprunable=1\n", "RECORD-MALFORMED",
                "TOTAL prunable=1 but REPO rows sum to 0")


def json_case(ctx, pid, json_path_of, cls, detail, build=None):
    """Write-stage case: a recorded-but-absent row (no git), --skip-unrecorded, --json outside root."""
    d = ctx.mkdir(ctx.base, pid)
    root = ctx.mkdir(d, "root")
    outside = ctx.mkdir(d, "outside")
    record = ctx.write(os.path.join(d, "record.tsv"), ROW_A)
    target = json_path_of(d, root, outside)
    if build is not None:
        build(d, root, outside, target)
    return ctx.expect(tool_args(root, record, "--skip-unrecorded", "--json", target), cls, detail), d, target


def p10a(ctx):
    def build(d, root, outside, target):
        os.mkfifo(target)           # never opened by the fixture: no reader, no writer
        if not stat.S_ISFIFO(os.lstat(target).st_mode):
            raise Probe("trigger not built: not a FIFO")
    json_case(ctx, "P10a", lambda d, r, o: os.path.join(o, "fifo.json"), "JSON-NOT-REGULAR",
              "is not a regular file", build)


def p10b(ctx):
    def build(d, root, outside, target):
        os.mkdir(target)
    json_case(ctx, "P10b", lambda d, r, o: os.path.join(o, "dir.json"), "JSON-NOT-REGULAR",
              "is not a regular file", build)


def p11(ctx):
    if not stat.S_ISCHR(os.stat(NULL).st_mode):
        raise Probe("trigger not built: %s is not a character device" % NULL)
    json_case(ctx, "P11", lambda d, r, o: NULL, "JSON-NOT-REGULAR", "is not a regular file")


def p12(ctx):
    d = ctx.mkdir(ctx.base, "P12")
    not_a_dir = ctx.write(os.path.join(d, "root-is-a-file"), "x\n")
    record = ctx.write(os.path.join(d, "record.tsv"), ROW_A)
    ctx.expect(tool_args(not_a_dir, record), "USAGE", "is not a directory")


def p13(ctx):
    d = ctx.mkdir(ctx.base, "P13")
    root = ctx.mkdir(d, "root")
    ctx.mkdir(d, "sibling")
    record = ctx.write(os.path.join(d, "record.tsv"), "REPO\t../sibling\tregs=1\tprunable=0\n")
    ctx.expect(tool_args(root, record, "--skip-unrecorded"), "RECORD-OUTSIDE-ROOT", "../sibling resolves outside")


def p14(ctx):
    d = ctx.mkdir(ctx.base, "P14")
    root = ctx.mkdir(d, "root")
    outside_git = os.path.join(d, "outside-gitdir")
    ctx.git_init(outside_git, "--bare")
    repo = ctx.mkdir(root, "repo")
    ctx.write(os.path.join(repo, ".git"), "gitdir: %s\n" % os.path.realpath(outside_git))
    record = ctx.write(os.path.join(d, "record.tsv"), "REPO\trepo\tregs=1\tprunable=0\n")
    ctx.expect(tool_args(root, record, "--skip-unrecorded"), "RECORD-OUTSIDE-ROOT", "gitdir resolves outside")


def p15(ctx):
    d = ctx.mkdir(ctx.base, "P15")
    root = ctx.mkdir(d, "root")
    record = ctx.write(os.path.join(d, "record.tsv"), ROW_A)
    before = open(record, encoding="utf-8").read()
    ctx.expect(tool_args(root, record, "--skip-unrecorded", "--json", record), "JSON-IS-RECORD",
               "is the record file")
    if open(record, encoding="utf-8").read() != before:
        raise Probe("record bytes changed")


def p16(ctx):
    d = ctx.mkdir(ctx.base, "P16")
    root = ctx.mkdir(d, "root")
    repo = os.path.join(root, "repo")
    ctx.git_init(repo)
    record = ctx.write(os.path.join(d, "record.tsv"), "REPO\trepo\tregs=1\tprunable=0\n")
    target = os.path.join(repo, "out.json")
    ctx.expect(tool_args(root, record, "--skip-unrecorded", "--json", target),
               "JSON-INSIDE-MEASURED-TREE", "is under")
    if os.path.lexists(target):
        raise Probe("--json file was created inside the measured repository")


def p17(ctx):
    def build(d, root, outside, target):
        ctx.write(target, "KEEP\n")
        os.link(target, os.path.join(outside, "alias.json"))
        if os.stat(target).st_nlink != 2:
            raise Probe("trigger not built: nlink != 2")
    err, d, target = json_case(ctx, "P17", lambda d, r, o: os.path.join(o, "linked.json"),
                               "JSON-HARDLINKED", "has 2 links", build)
    if open(target, encoding="utf-8").read() != "KEEP\n":
        raise Probe("hardlinked inode was modified")


def p18(ctx):
    holder = {}

    def build(d, root, outside, target):
        locked = os.path.dirname(target)
        os.mkdir(locked)
        os.chmod(locked, 0o555)
        holder["dir"] = locked
        if os.access(locked, os.W_OK):
            raise Probe("trigger not built: 0555 directory is writable")
    try:
        json_case(ctx, "P18", lambda d, r, o: os.path.join(o, "locked", "out.json"),
                  "JSON-UNWRITABLE", "Errno 13", build)
    finally:
        if "dir" in holder:
            os.chmod(holder["dir"], 0o755)


def p19(ctx):
    d = ctx.mkdir(ctx.base, "P19")
    root = ctx.mkdir(d, "root")
    record = ctx.write(os.path.join(d, "record.tsv"), ROW_A)
    ctx.expect(["--root", root, "--record", record, "--timeout", "0"], "USAGE", "--timeout must be >= 1")


PROBES = [
    ("P01", p01), ("P02a", p02a), ("P02b", p02b), ("P03", p03), ("P04", p04), ("P05", p05),
    ("P06", p06), ("P07", p07), ("P08", p08), ("P09", p09), ("P10a", p10a), ("P10b", p10b),
    ("P11", p11), ("P12", p12), ("P13", p13), ("P14", p14), ("P15", p15), ("P16", p16),
    ("P17", p17), ("P18", p18), ("P19", p19),
]


def rmtree_force(path):
    def fix(func, p, _exc):
        try:
            os.chmod(os.path.dirname(p), 0o755)
            os.chmod(p, 0o755)
            func(p)
        except OSError:
            pass
    shutil.rmtree(path, onerror=fix)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r41-refusal-sites: refusing to run as uid 0: the EACCES probes (P02a, P18) "
                         "need an unprivileged uid\n")
        return 2
    tool = os.path.abspath(args.tool)
    if not os.path.isfile(tool):
        sys.stderr.write("r41-refusal-sites: --tool %s is not a file\n" % tool)
        return 2
    os.makedirs(args.work, exist_ok=True)
    base = tempfile.mkdtemp(prefix="r41-refusal-", dir=os.path.abspath(args.work))
    ctx = Ctx(tool, base)
    passed = failed = 0
    try:
        for pid, fn in PROBES:
            try:
                fn(ctx)
                verdict, detail = "PASS", ""
            except Probe as exc:
                verdict, detail = "FAIL", str(exc)
            except Exception as exc:  # a probe must report, never traceback
                verdict, detail = "FAIL", "%s: %s" % (type(exc).__name__, exc)
            if verdict == "PASS":
                passed += 1
            else:
                failed += 1
            print(("probe-%s=%s %s" % (pid, verdict, " ".join(detail.split()))).rstrip(), flush=True)
        print("SUMMARY probes=%d pass=%d fail=%d" % (passed + failed, passed, failed), flush=True)
    finally:
        rmtree_force(base)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
