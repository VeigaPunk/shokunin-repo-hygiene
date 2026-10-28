#!/usr/bin/env python3
"""r41-refusal-sites.py — r41 C3 refusal-site battery for tools/souji-worktree-drift.py.

Protocol:
  python3 -B r41-refusal-sites.py --tool PATH --work DIR
  stdout: one `probe-<ID>=PASS|FAIL [detail]` line per probe id, then
          `SUMMARY probes=<n> pass=<p> fail=<f>`; exit 0 iff fail=0, else 1.
  exit 2: could not run (uid 0, bad arguments).

Each probe builds its own trigger under --work, runs the tool and asserts BOTH exit code 2 AND
a stderr line starting with the exact token `REFUSAL <CLASS>:` for the class its site raises.
One probe reaches one site only (S01..S19, frozen in census/round-41/c3-sites.tsv). Stdlib
only, no network, no writes outside --work. The EACCES probes (P02a, P18) need a non-root uid.
"""
import argparse
import os
import shutil
import stat
import subprocess
import sys

REC_OK = "REPO\ta\tregs=1\tprunable=0\n"
PROBES = []


def probe(pid):
    def deco(fn):
        PROBES.append((pid, fn))
        return fn
    return deco


class Ctx:
    def __init__(self, tool, work, pid):
        self.tool = tool
        self.base = os.path.join(work, "r41-" + pid)
        self.root = os.path.join(self.base, "root")
        self.outside = os.path.join(self.base, "outside")
        for d in (self.root, self.outside):
            os.makedirs(d)

    def record(self, text, name="record.tsv"):
        path = os.path.join(self.outside, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def run(self, *extra, root=None, record=None):
        cmd = [sys.executable, "-B", self.tool, "--root", root or self.root,
               "--record", record if record is not None else self.record(REC_OK)] + list(extra)
        env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": self.base}
        proc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, env=env, timeout=120, check=False)
        return proc.returncode, proc.stderr


def expect(result, cls):
    """None on success, else a failure detail: exit 2 and a `REFUSAL <cls>:` stderr line."""
    rc, err = result
    token = "REFUSAL %s:" % cls
    if rc != 2:
        return "rc=%d want 2 stderr=%r" % (rc, err[:120])
    if not any(line.startswith(token) for line in err.splitlines()):
        return "no %r in stderr=%r" % (token, err[:120])
    return None


@probe("P01")
def probe_p01(c):
    """S01 RECORD-MALFORMED: --record names a path that does not exist (ENOENT)."""
    return expect(c.run(record=os.path.join(c.outside, "absent.tsv")), "RECORD-MALFORMED")


@probe("P02a")
def probe_p02a(c):
    """S02 RECORD-MISSING: record exists, chmod 000 (EACCES, unprivileged uid)."""
    path = c.record(REC_OK)
    os.chmod(path, 0)
    try:
        return expect(c.run(record=path), "RECORD-MISSING")
    finally:
        os.chmod(path, 0o644)


@probe("P02b")
def probe_p02b(c):
    """S02 RECORD-MISSING: --record is a symlink loop (ELOOP)."""
    a = os.path.join(c.outside, "loop-a")
    b = os.path.join(c.outside, "loop-b")
    os.symlink(b, a)
    os.symlink(a, b)
    return expect(c.run(record=a), "RECORD-MISSING")


@probe("P03")
def probe_p03(c):
    """S03 RECORD-MALFORMED: --record is a directory (opens, fstat not regular)."""
    d = os.path.join(c.outside, "record-dir")
    os.mkdir(d)
    return expect(c.run(record=d), "RECORD-MALFORMED")


@probe("P04")
def probe_p04(c):
    """S04 RECORD-MALFORMED: two REPO rows with the same name."""
    rec = c.record(REC_OK + REC_OK)
    return expect(c.run(record=rec), "RECORD-MALFORMED")


@probe("P05")
def probe_p05(c):
    """S05 RECORD-MALFORMED: a non-comment line matching neither REPO nor TOTAL schema."""
    rec = c.record(REC_OK + "this line is not in the census schema\n")
    return expect(c.run(record=rec), "RECORD-MALFORMED")


@probe("P06")
def probe_p06(c):
    """S06 RECORD-EMPTY: only comment and blank lines, no REPO rows."""
    rec = c.record("# comment only\n\n   \n# another\n")
    return expect(c.run(record=rec), "RECORD-EMPTY")


@probe("P07")
def probe_p07(c):
    """S07 RECORD-MALFORMED: TOTAL repos= disagrees with the REPO row count."""
    rec = c.record(REC_OK + "TOTAL\trepos=2\tregs=1\tprunable=0\n")
    return expect(c.run(record=rec), "RECORD-MALFORMED")


@probe("P08")
def probe_p08(c):
    """S08 RECORD-MALFORMED: TOTAL regs= disagrees with the REPO regs sum (repos agrees)."""
    rec = c.record(REC_OK + "TOTAL\trepos=1\tregs=5\tprunable=0\n")
    return expect(c.run(record=rec), "RECORD-MALFORMED")


@probe("P09")
def probe_p09(c):
    """S09 RECORD-MALFORMED: TOTAL prunable= disagrees with the REPO prunable sum (repos, regs agree)."""
    rec = c.record(REC_OK + "TOTAL\trepos=1\tregs=1\tprunable=5\n")
    return expect(c.run(record=rec), "RECORD-MALFORMED")


@probe("P10a")
def probe_p10a(c):
    """S10 JSON-NOT-REGULAR: --json is a FIFO with no reader (ENXIO), outside root and measured repos."""
    fifo = os.path.join(c.outside, "out.fifo")
    os.mkfifo(fifo)
    return expect(c.run("--json", fifo), "JSON-NOT-REGULAR")


@probe("P10b")
def probe_p10b(c):
    """S10 JSON-NOT-REGULAR: --json is a directory (EISDIR), outside root and measured repos."""
    d = os.path.join(c.outside, "out-dir")
    os.mkdir(d)
    return expect(c.run("--json", d), "JSON-NOT-REGULAR")


@probe("P11")
def probe_p11(c):
    """S11 JSON-NOT-REGULAR: --json is /dev/null (opens, fstat is a character device)."""
    if not stat.S_ISCHR(os.stat(os.devnull).st_mode):
        return "%s is not a character device" % os.devnull
    return expect(c.run("--json", os.devnull), "JSON-NOT-REGULAR")


@probe("P12")
def probe_p12(c):
    """S12 USAGE: --root names a path that is not a directory."""
    f = os.path.join(c.outside, "not-a-dir")
    with open(f, "w", encoding="utf-8") as handle:
        handle.write("x\n")
    return expect(c.run(root=f), "USAGE")


@probe("P13")
def probe_p13(c):
    """S13 RECORD-OUTSIDE-ROOT: a REPO row named `../sibling` resolving outside --root."""
    rec = c.record("REPO\t../sibling\tregs=1\tprunable=0\n")
    return expect(c.run(record=rec), "RECORD-OUTSIDE-ROOT")


@probe("P14")
def probe_p14(c):
    """S14 RECORD-OUTSIDE-ROOT: a REPO row whose .git file points to a gitdir outside --root."""
    gitdir = os.path.join(c.outside, "ext.git")
    for sub in ("objects", "refs"):
        os.makedirs(os.path.join(gitdir, sub))
    with open(os.path.join(gitdir, "HEAD"), "w", encoding="utf-8") as handle:
        handle.write("ref: refs/heads/main\n")
    repo = os.path.join(c.root, "a")
    os.mkdir(repo)
    with open(os.path.join(repo, ".git"), "w", encoding="utf-8") as handle:
        handle.write("gitdir: %s\n" % gitdir)
    return expect(c.run(), "RECORD-OUTSIDE-ROOT")


@probe("P15")
def probe_p15(c):
    """S15 JSON-IS-RECORD: --json is the --record path (record outside root)."""
    rec = c.record(REC_OK)
    return expect(c.run("--json", rec, record=rec), "JSON-IS-RECORD")


@probe("P16")
def probe_p16(c):
    """S16 JSON-INSIDE-MEASURED-TREE: --json lies under the measured root."""
    return expect(c.run("--json", os.path.join(c.root, "out.json")), "JSON-INSIDE-MEASURED-TREE")


@probe("P17")
def probe_p17(c):
    """S17 JSON-HARDLINKED: --json is an outside regular file with two links."""
    target = os.path.join(c.outside, "out.json")
    with open(target, "w", encoding="utf-8") as handle:
        handle.write("{}\n")
    os.link(target, os.path.join(c.outside, "out-alias.json"))
    return expect(c.run("--json", target), "JSON-HARDLINKED")


@probe("P18")
def probe_p18(c):
    """S18 JSON-UNWRITABLE: --json in an unwritable directory (EACCES, unprivileged uid)."""
    d = os.path.join(c.outside, "ro")
    os.mkdir(d)
    os.chmod(d, 0o555)
    try:
        return expect(c.run("--json", os.path.join(d, "out.json")), "JSON-UNWRITABLE")
    finally:
        os.chmod(d, 0o755)


@probe("P19")
def probe_p19(c):
    """S19 USAGE: --timeout 0."""
    return expect(c.run("--timeout", "0"), "USAGE")


def rmtree(path):
    def fix(func, p, _exc):
        try:
            os.chmod(os.path.dirname(p), 0o755)
            os.chmod(p, 0o755)
        except OSError:
            pass
        func(p)
    if os.path.lexists(path):
        shutil.rmtree(path, onerror=fix)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r41-refusal-sites: refusing to run as uid 0 (P02a and P18 need an unprivileged uid)\n")
        return 2
    tool = os.path.abspath(args.tool)
    work = os.path.abspath(args.work)
    if not os.path.isfile(tool) or not os.path.isdir(work):
        sys.stderr.write("r41-refusal-sites: --tool must be a file and --work a directory\n")
        return 2
    passed = failed = 0
    for pid, fn in PROBES:
        ctx_base = os.path.join(work, "r41-" + pid)
        rmtree(ctx_base)
        try:
            detail = fn(Ctx(tool, work, pid))
        except Exception as exc:  # a probe that cannot build or run its trigger is a FAIL
            detail = "probe error %s: %s" % (type(exc).__name__, exc)
        finally:
            rmtree(ctx_base)
        if detail is None:
            passed += 1
            print("probe-%s=PASS" % pid)
        else:
            failed += 1
            print("probe-%s=FAIL %s" % (pid, " ".join(str(detail).split())))
    print("SUMMARY probes=%d pass=%d fail=%d" % (passed + failed, passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
