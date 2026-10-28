#!/usr/bin/env python3
"""tests/fixtures/r41-refusal-sites.py — r41 C3: class-asserting probe for every refusal site.

  python3 -B tests/fixtures/r41-refusal-sites.py --tool PATH --work DIR

One probe per frozen probe id (census/round-41/c3-sites.tsv). Each builds its own trigger under a
fresh directory inside --work, runs the tool, and passes only when the exit code is 2 AND stderr
carries the exact token `REFUSAL <CLASS>:` of the class its site raises. Prints
`probe-<ID>=PASS|FAIL`, then `SUMMARY probes=<n> pass=<p> fail=<f>`; exit 0 iff fail=0.
The EACCES probes (P02a, P18) need a non-root uid: as uid 0 the fixture exits 2.
Python standard library only; nothing is written outside --work.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_TERMINAL_PROMPT": "0",
}
ROW = "REPO\tr1\tregs=1\tprunable=0\n"


class Case:
    """Per-probe scratch: d/root (empty), d/rec.tsv (one valid row), d/out (outside-root dir)."""

    def __init__(self, base, pid):
        self.d = os.path.join(base, pid)
        self.root = os.path.join(self.d, "root")
        self.out = os.path.join(self.d, "out")
        self.rec = os.path.join(self.d, "rec.tsv")
        for p in (self.root, self.out):
            os.makedirs(p)
        self.write(self.rec, ROW)

    def write(self, path, text):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def git_init(self, path):
        os.makedirs(path, exist_ok=True)
        subprocess.run(["git", "-C", path, "init", "-q"], env=ENV, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run(self, tool, record=None, root=None, extra=()):
        cmd = ["python3", "-B", tool, "--root", root or self.root, "--record", record or self.rec] + list(extra)
        try:
            proc = subprocess.run(cmd, env=ENV, cwd=self.d, stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            return None, "timeout"
        return proc.returncode, proc.stderr


def rec_text(c, text):
    return c.write(c.rec, text)


def p01(c, tool):
    return c.run(tool, record=os.path.join(c.d, "no-such-record"))


def p02a(c, tool):
    os.chmod(c.rec, 0)
    return c.run(tool)


def p02b(c, tool):
    loop = os.path.join(c.d, "loop")
    os.symlink(loop, loop)
    return c.run(tool, record=loop)


def p03(c, tool):
    return c.run(tool, record=c.out)


def p04(c, tool):
    rec_text(c, ROW + ROW)
    return c.run(tool)


def p05(c, tool):
    rec_text(c, ROW + "garbage line\n")
    return c.run(tool)


def p06(c, tool):
    rec_text(c, "# comment only\n\n   \n# another\n")
    return c.run(tool)


def p07(c, tool):
    rec_text(c, ROW + "TOTAL\trepos=2\tregs=1\tprunable=0\n")
    return c.run(tool)


def p08(c, tool):
    rec_text(c, ROW + "TOTAL\trepos=1\tregs=5\tprunable=0\n")
    return c.run(tool)


def p09(c, tool):
    rec_text(c, ROW + "TOTAL\trepos=1\tregs=1\tprunable=3\n")
    return c.run(tool)


def p10a(c, tool):
    fifo = os.path.join(c.out, "fifo")
    os.mkfifo(fifo)
    return c.run(tool, extra=["--json", fifo])


def p10b(c, tool):
    return c.run(tool, extra=["--json", c.out])


def p11(c, tool):
    return c.run(tool, extra=["--json", os.devnull])


def p12(c, tool):
    return c.run(tool, root=c.write(os.path.join(c.d, "not-a-dir"), "x\n"))


def p13(c, tool):
    rec_text(c, "REPO\t../sibling\tregs=1\tprunable=0\n")
    return c.run(tool)


def p14(c, tool):
    outside = os.path.join(c.d, "elsewhere")
    c.git_init(outside)
    os.makedirs(os.path.join(c.root, "r1"))
    c.write(os.path.join(c.root, "r1", ".git"), "gitdir: %s\n" % os.path.join(outside, ".git"))
    return c.run(tool)


def p15(c, tool):
    return c.run(tool, extra=["--json", c.rec])


def p16(c, tool):
    c.git_init(os.path.join(c.root, "r1"))
    return c.run(tool, extra=["--json", os.path.join(c.root, "r1", "out.json")])


def p17(c, tool):
    first = c.write(os.path.join(c.out, "a.json"), "{}\n")
    os.link(first, os.path.join(c.out, "b.json"))
    return c.run(tool, extra=["--json", first])


def p18(c, tool):
    os.chmod(c.out, 0o555)
    return c.run(tool, extra=["--json", os.path.join(c.out, "out.json")])


def p19(c, tool):
    return c.run(tool, extra=["--timeout", "0"])


PROBES = [
    ("P01", "RECORD-MALFORMED", p01), ("P02a", "RECORD-MISSING", p02a), ("P02b", "RECORD-MISSING", p02b),
    ("P03", "RECORD-MALFORMED", p03), ("P04", "RECORD-MALFORMED", p04), ("P05", "RECORD-MALFORMED", p05),
    ("P06", "RECORD-EMPTY", p06), ("P07", "RECORD-MALFORMED", p07), ("P08", "RECORD-MALFORMED", p08),
    ("P09", "RECORD-MALFORMED", p09), ("P10a", "JSON-NOT-REGULAR", p10a), ("P10b", "JSON-NOT-REGULAR", p10b),
    ("P11", "JSON-NOT-REGULAR", p11), ("P12", "USAGE", p12), ("P13", "RECORD-OUTSIDE-ROOT", p13),
    ("P14", "RECORD-OUTSIDE-ROOT", p14), ("P15", "JSON-IS-RECORD", p15),
    ("P16", "JSON-INSIDE-MEASURED-TREE", p16), ("P17", "JSON-HARDLINKED", p17),
    ("P18", "JSON-UNWRITABLE", p18), ("P19", "USAGE", p19),
]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r41-refusal-sites: refusing to run as uid 0 (P02a and P18 need an unprivileged uid)\n")
        return 2
    tool = os.path.abspath(args.tool)
    os.makedirs(args.work, exist_ok=True)
    base = tempfile.mkdtemp(prefix="r41-refusal-", dir=os.path.abspath(args.work))
    passed = 0
    try:
        for pid, cls, fn in PROBES:
            try:
                rc, err = fn(Case(base, pid), tool)
                ok = rc == 2 and ("REFUSAL %s:" % cls) in err
                detail = "" if ok else " rc=%s want=REFUSAL %s: stderr=%r" % (rc, cls, err[:160])
            except Exception as exc:  # a probe that cannot build its trigger is a FAIL, never a skip
                ok, detail = False, " probe error %s: %s" % (type(exc).__name__, exc)
            passed += ok
            print("probe-%s=%s%s" % (pid, "PASS" if ok else "FAIL", detail))
    finally:
        for dirpath, dirnames, _files in os.walk(base):
            for name in dirnames:
                os.chmod(os.path.join(dirpath, name), 0o755)
        shutil.rmtree(base, ignore_errors=True)
    print("SUMMARY probes=%d pass=%d fail=%d" % (len(PROBES), passed, len(PROBES) - passed))
    return 0 if passed == len(PROBES) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
