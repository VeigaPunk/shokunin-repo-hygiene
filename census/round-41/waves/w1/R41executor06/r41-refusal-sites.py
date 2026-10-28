#!/usr/bin/env python3
"""tests/fixtures/r41-refusal-sites.py -- r41 C3: one class-asserting probe per refusal site.

Reaches every one of the 19 refusal sites of tools/souji-worktree-drift.py (21 probe ids, P01..P19;
P02 and P10 have two probes each). Every probe builds its own trigger under --work, runs the tool in a
whitelisted environment, and asserts BOTH exit code 2 AND that stderr carries exactly one
`REFUSAL <CLASS>:` line whose class token is the one its site raises. One probe reaches one site only.

  python3 -B tests/fixtures/r41-refusal-sites.py --tool PATH --work DIR
  stdout: probe-<ID>=PASS|FAIL [detail] per probe, then SUMMARY probes=<n> pass=<p> fail=<f>
  exit:   0 iff fail=0; 1 otherwise; 2 when it cannot run (uid 0: the EACCES probes P02a/P18 would
          change class under a privileged runner, so the fixture refuses instead of skipping).

Hermetic: stdlib only, no network, every child gets a whitelisted environment (no inherited GIT_*
variable; config discovery neutralised), everything is created under --work and removed in a finally.
"""
import argparse
import os
import shutil
import stat
import subprocess
import sys
import tempfile

PROBE_TIMEOUT = 60


def child_env(work):
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": work,
        "TMPDIR": work,
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


class Ctx:
    def __init__(self, tool, work):
        self.tool = tool
        self.work = work
        self.env = child_env(work)

    def sub(self, pid):
        """Fresh per-probe directory with an empty fleet root and an out/ dir outside it."""
        base = os.path.join(self.work, pid)
        os.makedirs(os.path.join(base, "root"))
        os.makedirs(os.path.join(base, "out"))
        return base

    def tool_run(self, argv):
        return subprocess.run([sys.executable, "-B", self.tool] + argv, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, env=self.env,
                              cwd=self.work, timeout=PROBE_TIMEOUT, check=False)

    def git(self, argv):
        return subprocess.run(["git"] + argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              stdin=subprocess.DEVNULL, env=self.env, cwd=self.work,
                              timeout=PROBE_TIMEOUT, check=True)


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def row(name, regs=1, prunable=0):
    return "REPO\t%s\tregs=%d\tprunable=%d\n" % (name, regs, prunable)


def total(repos, regs, prunable):
    return "TOTAL\trepos=%d\tregs=%d\tprunable=%d\n" % (repos, regs, prunable)


def expect(ctx, argv, cls):
    """Run the tool; PASS only when rc==2 and stderr has exactly one REFUSAL line carrying <cls>."""
    proc = ctx.tool_run(argv)
    err = proc.stderr.decode("utf-8", "replace")
    lines = [ln for ln in err.splitlines() if ln.startswith("REFUSAL ")]
    token = "REFUSAL %s:" % cls
    if proc.returncode != 2:
        return False, "rc=%d want 2; stderr=%r" % (proc.returncode, err[:160])
    if len(lines) != 1 or token not in lines[0]:
        return False, "want %s got %r" % (token, err[:160])
    return True, ""


def rec_args(base, record, *extra):
    return ["--root", os.path.join(base, "root"), "--record", record] + list(extra)


def ok_record(base, text=None):
    path = os.path.join(base, "record.tsv")
    write(path, text if text is not None else row("alpha") + total(1, 1, 0))
    return path


# ---- probes: each returns (ok, detail) -------------------------------------------------------

def p01(c):  # S01 RECORD-MALFORMED: --record path does not exist (ENOENT)
    b = c.sub("P01")
    return expect(c, rec_args(b, os.path.join(b, "absent.tsv")), "RECORD-MALFORMED")


def p02a(c):  # S02 RECORD-MISSING: chmod 000 file (EACCES)
    b = c.sub("P02a")
    rec = ok_record(b)
    os.chmod(rec, 0)
    return expect(c, rec_args(b, rec), "RECORD-MISSING")


def p02b(c):  # S02 RECORD-MISSING: symlink loop (ELOOP)
    b = c.sub("P02b")
    a, z = os.path.join(b, "loop-a"), os.path.join(b, "loop-b")
    os.symlink(z, a)
    os.symlink(a, z)
    return expect(c, rec_args(b, a), "RECORD-MISSING")


def p03(c):  # S03 RECORD-MALFORMED: record is a directory (opens, fstat not regular)
    b = c.sub("P03")
    d = os.path.join(b, "record-dir")
    os.makedirs(d)
    return expect(c, rec_args(b, d), "RECORD-MALFORMED")


def p04(c):  # S04 RECORD-MALFORMED: duplicate REPO name
    b = c.sub("P04")
    return expect(c, rec_args(b, ok_record(b, row("alpha") + row("alpha"))), "RECORD-MALFORMED")


def p05(c):  # S05 RECORD-MALFORMED: line matching neither schema
    b = c.sub("P05")
    return expect(c, rec_args(b, ok_record(b, row("alpha") + "this is not a census row\n")),
                  "RECORD-MALFORMED")


def p06(c):  # S06 RECORD-EMPTY: only comments and blanks
    b = c.sub("P06")
    return expect(c, rec_args(b, ok_record(b, "# comment only\n\n   \n# another\n")), "RECORD-EMPTY")


def p07(c):  # S07 RECORD-MALFORMED: TOTAL repos disagrees (regs and prunable agree)
    b = c.sub("P07")
    return expect(c, rec_args(b, ok_record(b, row("alpha", 3, 1) + total(2, 3, 1))), "RECORD-MALFORMED")


def p08(c):  # S08 RECORD-MALFORMED: TOTAL regs disagrees (repos and prunable agree)
    b = c.sub("P08")
    return expect(c, rec_args(b, ok_record(b, row("alpha", 3, 1) + total(1, 4, 1))), "RECORD-MALFORMED")


def p09(c):  # S09 RECORD-MALFORMED: TOTAL prunable disagrees (repos and regs agree)
    b = c.sub("P09")
    return expect(c, rec_args(b, ok_record(b, row("alpha", 3, 1) + total(1, 3, 2))), "RECORD-MALFORMED")


def p10a(c):  # S10 JSON-NOT-REGULAR: --json is a FIFO with no reader (ENXIO)
    b = c.sub("P10a")
    fifo = os.path.join(b, "out", "fifo")
    os.mkfifo(fifo)
    return expect(c, rec_args(b, ok_record(b), "--json", fifo), "JSON-NOT-REGULAR")


def p10b(c):  # S10 JSON-NOT-REGULAR: --json is a directory (EISDIR)
    b = c.sub("P10b")
    d = os.path.join(b, "out", "dir")
    os.makedirs(d)
    return expect(c, rec_args(b, ok_record(b), "--json", d), "JSON-NOT-REGULAR")


def p11(c):  # S11 JSON-NOT-REGULAR: --json is /dev/null (opens; fstat says character device)
    b = c.sub("P11")
    if not stat.S_ISCHR(os.stat(os.devnull).st_mode):
        return False, "%s is not a character device here" % os.devnull
    return expect(c, rec_args(b, ok_record(b), "--json", os.devnull), "JSON-NOT-REGULAR")


def p12(c):  # S12 USAGE: --root is not a directory
    b = c.sub("P12")
    not_dir = os.path.join(b, "out", "plain-file")
    write(not_dir, "x\n")
    return expect(c, ["--root", not_dir, "--record", ok_record(b)], "USAGE")


def p13(c):  # S13 RECORD-OUTSIDE-ROOT: row name ../sibling
    b = c.sub("P13")
    return expect(c, rec_args(b, ok_record(b, row("../sibling") + total(1, 1, 0))), "RECORD-OUTSIDE-ROOT")


def p14(c):  # S14 RECORD-OUTSIDE-ROOT: in-root .git file pointing at a gitdir outside --root
    b = c.sub("P14")
    outside = os.path.join(b, "out", "elsewhere")
    os.makedirs(outside)
    c.git(["init", "-q", outside])
    repo = os.path.join(b, "root", "alpha")
    os.makedirs(repo)
    write(os.path.join(repo, ".git"), "gitdir: %s\n" % os.path.join(outside, ".git"))
    return expect(c, rec_args(b, ok_record(b)), "RECORD-OUTSIDE-ROOT")


def p15(c):  # S15 JSON-IS-RECORD: --json is the --record path
    b = c.sub("P15")
    rec = ok_record(b)
    return expect(c, rec_args(b, rec, "--json", rec), "JSON-IS-RECORD")


def p16(c):  # S16 JSON-INSIDE-MEASURED-TREE: --json under a measured repository
    b = c.sub("P16")
    repo = os.path.join(b, "root", "alpha")
    os.makedirs(repo)
    c.git(["init", "-q", repo])
    target = os.path.join(repo, "report.json")
    return expect(c, rec_args(b, ok_record(b), "--json", target), "JSON-INSIDE-MEASURED-TREE")


def p17(c):  # S17 JSON-HARDLINKED: --json is an outside file with two links
    b = c.sub("P17")
    first = os.path.join(b, "out", "one.json")
    write(first, "{}\n")
    os.link(first, os.path.join(b, "out", "two.json"))
    if os.stat(first).st_nlink != 2:
        return False, "fixture could not create a two-link file"
    return expect(c, rec_args(b, ok_record(b), "--json", first), "JSON-HARDLINKED")


def p18(c):  # S18 JSON-UNWRITABLE: --json in an unwritable directory (EACCES)
    b = c.sub("P18")
    ro = os.path.join(b, "out", "ro")
    os.makedirs(ro)
    os.chmod(ro, 0o555)
    return expect(c, rec_args(b, ok_record(b), "--json", os.path.join(ro, "report.json")), "JSON-UNWRITABLE")


def p19(c):  # S19 USAGE: --timeout 0
    b = c.sub("P19")
    return expect(c, rec_args(b, ok_record(b), "--timeout", "0"), "USAGE")


PROBES = [
    ("P01", p01), ("P02a", p02a), ("P02b", p02b), ("P03", p03), ("P04", p04), ("P05", p05),
    ("P06", p06), ("P07", p07), ("P08", p08), ("P09", p09), ("P10a", p10a), ("P10b", p10b),
    ("P11", p11), ("P12", p12), ("P13", p13), ("P14", p14), ("P15", p15), ("P16", p16),
    ("P17", p17), ("P18", p18), ("P19", p19),
]


def rmtree_force(path):
    """Remove a tree that may hold chmod-000 / read-only entries made by the probes."""
    for dirpath, dirnames, filenames in os.walk(path):
        for name in dirnames + filenames:
            full = os.path.join(dirpath, name)
            try:
                if not os.path.islink(full):
                    os.chmod(full, 0o700)
            except OSError:
                pass
        try:
            os.chmod(dirpath, 0o700)
        except OSError:
            pass
    shutil.rmtree(path, ignore_errors=True)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    if os.geteuid() == 0:
        sys.stderr.write("r41-refusal-sites: refusing to run as uid 0 (P02a and P18 are EACCES probes; "
                         "root bypasses permission checks, so they would not reach their sites)\n")
        return 2
    tool = os.path.abspath(args.tool)
    if not os.path.isfile(tool):
        sys.stderr.write("r41-refusal-sites: --tool %s is not a file\n" % tool)
        return 2
    os.makedirs(args.work, exist_ok=True)
    work = tempfile.mkdtemp(prefix="r41-refusal.", dir=os.path.abspath(args.work))
    passed = failed = 0
    try:
        ctx = Ctx(tool, work)
        for pid, fn in PROBES:
            try:
                ok, detail = fn(ctx)
            except Exception as exc:  # a probe that cannot build or run its trigger is a FAIL
                ok, detail = False, "%s: %s" % (type(exc).__name__, exc)
            if ok:
                passed += 1
                print("probe-%s=PASS" % pid)
            else:
                failed += 1
                print("probe-%s=FAIL %s" % (pid, " ".join(str(detail).split())))
        print("SUMMARY probes=%d pass=%d fail=%d" % (passed + failed, passed, failed))
        sys.stdout.flush()
    finally:
        rmtree_force(work)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
