#!/usr/bin/env python3
"""r41 C3 reviewer draft: class-asserting probes for the 19 refusal sites of tools/souji-worktree-drift.py.

Protocol (census/round-41/c3-counter.py): python3 -B <this> --tool PATH --work DIR
Each probe builds a hermetic fixture under DIR, runs the tool, and PASSes only when the
tool exits 2 and its stderr names the probe's expected refusal class at the start of the
line. A probe never trusts the exit code alone.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

PROBES = []


def probe(pid):
    def deco(fn):
        PROBES.append((pid, fn))
        return fn
    return deco


def run_tool(tool, args):
    proc = subprocess.run(
        [sys.executable, "-B", tool] + args,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=120,
    )
    return proc.returncode, proc.stdout, proc.stderr


def expect_refusal(tool, args, klass):
    rc, _out, err = run_tool(tool, args)
    first = err.strip().splitlines()[0] if err.strip() else ""
    ok = rc == 2 and first.startswith("REFUSAL %s:" % klass)
    return ok, "rc=%d want=%s stderr=%s" % (rc, klass, first[:160])


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


GOOD_ROW = "REPO\tgood\tregs=1\tprunable=0\n"


def new_root(base):
    root = os.path.join(base, "root")
    os.mkdir(root)
    return root


@probe("P01")
def p01(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "absent.tsv")
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MALFORMED")


@probe("P02a")
def p02a(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "locked.tsv")
    write(rec, GOOD_ROW)
    os.chmod(rec, 0)
    try:
        return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MISSING")
    finally:
        os.chmod(rec, 0o644)


@probe("P02b")
def p02b(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "loop.tsv")
    os.symlink("loop.tsv", rec)
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MISSING")


@probe("P03")
def p03(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "dir.tsv")
    os.mkdir(rec)
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MALFORMED")


@probe("P04")
def p04(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "dup.tsv")
    write(rec, GOOD_ROW + GOOD_ROW)
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MALFORMED")


@probe("P05")
def p05(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "schema.tsv")
    write(rec, GOOD_ROW + "not a census row\n")
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MALFORMED")


@probe("P06")
def p06(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "empty.tsv")
    write(rec, "# only a comment\n\n")
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-EMPTY")


@probe("P07")
def p07(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "total-repos.tsv")
    write(rec, GOOD_ROW + "TOTAL\trepos=2\tregs=1\tprunable=0\n")
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MALFORMED")


@probe("P08")
def p08(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "total-regs.tsv")
    write(rec, GOOD_ROW + "TOTAL\trepos=1\tregs=2\tprunable=0\n")
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MALFORMED")


@probe("P09")
def p09(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "total-prunable.tsv")
    write(rec, GOOD_ROW + "TOTAL\trepos=1\tregs=1\tprunable=1\n")
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-MALFORMED")


@probe("P10a")
def p10a(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "ghost.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    fifo = os.path.join(base, "out.fifo")
    os.mkfifo(fifo)
    return expect_refusal(tool, ["--root", root, "--record", rec, "--json", fifo], "JSON-NOT-REGULAR")


@probe("P10b")
def p10b(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "ghost.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    jdir = os.path.join(base, "jdir")
    os.mkdir(jdir)
    return expect_refusal(tool, ["--root", root, "--record", rec, "--json", jdir], "JSON-NOT-REGULAR")


@probe("P11")
def p11(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "ghost.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    return expect_refusal(tool, ["--root", root, "--record", rec, "--json", "/dev/null"], "JSON-NOT-REGULAR")


@probe("P12")
def p12(tool, base):
    rec = os.path.join(base, "ghost.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    notdir = os.path.join(base, "plain-file")
    write(notdir, "x\n")
    return expect_refusal(tool, ["--root", notdir, "--record", rec], "USAGE")


@probe("P13")
def p13(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "escape.tsv")
    write(rec, "REPO\t../sibling\tregs=0\tprunable=0\n")
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-OUTSIDE-ROOT")


@probe("P14")
def p14(tool, base):
    root = new_root(base)
    gd = os.path.join(base, "outside-gd")
    os.mkdir(gd)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": base, "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    init = subprocess.run(["git", "-C", gd, "init", "-q"], env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=False)
    if init.returncode != 0:
        return False, "git init failed rc=%d" % init.returncode
    linked = os.path.join(root, "linked")
    os.mkdir(linked)
    write(os.path.join(linked, ".git"), "gitdir: %s\n" % os.path.join(gd, ".git"))
    rec = os.path.join(base, "linked.tsv")
    write(rec, "REPO\tlinked\tregs=1\tprunable=0\n")
    return expect_refusal(tool, ["--root", root, "--record", rec], "RECORD-OUTSIDE-ROOT")


@probe("P15")
def p15(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "self.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    return expect_refusal(tool, ["--root", root, "--record", rec, "--json", rec], "JSON-IS-RECORD")


@probe("P16")
def p16(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "ghost.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    inside = os.path.join(root, "out.json")
    return expect_refusal(tool, ["--root", root, "--record", rec, "--json", inside], "JSON-INSIDE-MEASURED-TREE")


@probe("P17")
def p17(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "ghost.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    outside = os.path.join(base, "outside")
    os.mkdir(outside)
    target = os.path.join(outside, "a.json")
    write(target, "{}\n")
    os.link(target, os.path.join(outside, "b.json"))
    return expect_refusal(tool, ["--root", root, "--record", rec, "--json", target], "JSON-HARDLINKED")


@probe("P18")
def p18(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "ghost.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    locked = os.path.join(base, "locked-dir")
    os.mkdir(locked)
    os.chmod(locked, 0o555)
    try:
        return expect_refusal(tool, ["--root", root, "--record", rec, "--json", os.path.join(locked, "out.json")],
                              "JSON-UNWRITABLE")
    finally:
        os.chmod(locked, 0o755)


@probe("P19")
def p19(tool, base):
    root = new_root(base)
    rec = os.path.join(base, "ghost.tsv")
    write(rec, "REPO\tghost\tregs=0\tprunable=0\n")
    return expect_refusal(tool, ["--root", root, "--record", rec, "--timeout", "0"], "USAGE")


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args(argv)
    tool = os.path.abspath(args.tool)
    work = os.path.abspath(args.work)
    os.makedirs(work, exist_ok=True)
    passed = failed = 0
    for pid, fn in PROBES:
        base = tempfile.mkdtemp(prefix="probe-%s." % pid, dir=work)
        try:
            ok, detail = fn(tool, base)
        except Exception as exc:  # a probe that cannot run is a failure, never a pass
            ok, detail = False, "exception %s" % exc
        finally:
            for dirpath, dirnames, _files in os.walk(base):
                for name in dirnames:
                    os.chmod(os.path.join(dirpath, name), 0o755)
            shutil.rmtree(base, ignore_errors=True)
        detail = " ".join(str(detail).split())
        print("probe-%s=%s %s" % (pid, "PASS" if ok else "FAIL", detail))
        if ok:
            passed += 1
        else:
            failed += 1
    print("SUMMARY probes=%d pass=%d fail=%d" % (len(PROBES), passed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
