#!/usr/bin/env python3
"""R41w2mutationtester04 helper: for each mutant that survives r39/r40/r41, build a small scratch fleet that
exercises the mutated line and compare the pristine tool's output with the mutant's output. A difference
means the mutant is observable (a coverage gap), not an equivalent mutant. Read-only on the lane; every
fleet lives under SCR. Mutant files come from mutate-r1.py's scratch (SCR/mut). Git calls use the real git.
CLI: python3 -B probe-survivors.py [--scratch DIR]
"""
import argparse
import os
import shutil
import stat
import subprocess
import sys

SCR_DEFAULT = "/fast/scratch/hyaku/souji-r41/R41w2mutationtester04"
REAL_GIT = shutil.which("git")
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
           "GIT_AUTHOR_NAME": "probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
           "GIT_COMMITTER_NAME": "probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid"}
ROWS = "REPO\talpha\tregs=1\tprunable=0\n"


def g(args, cwd=None):
    subprocess.run([REAL_GIT] + args, cwd=cwd, env=dict(GIT_ENV, PATH=os.environ["PATH"]),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def mkrepo(path):
    os.makedirs(path)
    g(["init", "-q", "-b", "main", path])
    with open(os.path.join(path, "file.txt"), "w", encoding="utf-8") as handle:
        handle.write("base\n")
    g(["-C", path, "add", "file.txt"])
    g(["-C", path, "commit", "-qm", "base"])


def shim(dirpath, needle, message):
    os.makedirs(dirpath, exist_ok=True)
    path = os.path.join(dirpath, "git")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write('#!/bin/sh\ncase "$*" in *"%s"*) echo "%s" >&2; exit 1;; esac\nexec %s "$@"\n'
                     % (needle, message, REAL_GIT))
    os.chmod(path, 0o755)
    return dirpath


def tool_run(tool, root, record, extra=(), path_prefix=None, work=None):
    env = dict(GIT_ENV)
    env["PATH"] = (path_prefix + ":" if path_prefix else "") + os.environ["PATH"]
    env["TMPDIR"] = work
    proc = subprocess.run(["python3", "-B", tool, "--root", root, "--record", record, "--timeout", "30"]
                          + list(extra), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, check=False)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def write_record(path, body):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(body)
    return path


def broken_gitfile(root, name):
    """A work tree whose .git file points at a gitdir that does not exist (git calls fail)."""
    d = os.path.join(root, name)
    os.makedirs(d)
    with open(os.path.join(d, ".git"), "w", encoding="utf-8") as handle:
        handle.write("gitdir: /nonexistent/%s/.git\n" % name)


def base_fleet(scr, tag):
    d = os.path.join(scr, "probe", tag)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "work"))
    root = os.path.join(d, "root")
    os.makedirs(root)
    mkrepo(os.path.join(root, "alpha"))
    return d, root


def probes(scr):
    """(mutant id, description, builder(scr) -> (root, record, extra, path_prefix)) ."""
    def x01(scr):
        d, root = base_fleet(scr, "X01")
        ext = os.path.join(d, "ext-repo")
        mkrepo(ext)
        os.symlink(ext, os.path.join(root, "ext"))
        return root, write_record(os.path.join(d, "rec.tsv"), ROWS + "TOTAL\trepos=1\tregs=1\tprunable=0\n"), (), None

    def x02(scr):
        d, root = base_fleet(scr, "X02")
        broken_gitfile(root, "wt")
        return root, write_record(os.path.join(d, "rec.tsv"), ROWS + "TOTAL\trepos=1\tregs=1\tprunable=0\n"), (), None

    def x03(scr):
        d, root = base_fleet(scr, "X03")
        broken_gitfile(root, "wt")
        body = "REPO\twt\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n"
        return root, write_record(os.path.join(d, "rec.tsv"), body), (), None

    def x04(scr):
        d, root = base_fleet(scr, "X04")
        return root, write_record(os.path.join(d, "rec.tsv"), ROWS + "TOTAL\trepos=1\tregs=1\tprunable=0\n"), (), None

    def x08(scr):
        d, root = base_fleet(scr, "X08")
        body = "REPO\talpha\tregs=5\tprunable=0\nTOTAL\trepos=1\tregs=5\tprunable=0\n"
        return root, write_record(os.path.join(d, "rec.tsv"), body), (), None

    def x09(scr):
        d, root = base_fleet(scr, "X09")
        body = "REPO\talpha\tregs=1\tprunable=1\nTOTAL\trepos=1\tregs=1\tprunable=1\n"
        return root, write_record(os.path.join(d, "rec.tsv"), body), (), None

    def x10(scr):
        d, root = base_fleet(scr, "X10")
        g(["-C", os.path.join(root, "alpha"), "worktree", "add", "-q", "-b", "side", os.path.join(d, "side-wt")])
        return root, write_record(os.path.join(d, "rec.tsv"), ROWS + "TOTAL\trepos=1\tregs=1\tprunable=0\n"), (), None

    def x11(scr):
        d, root = base_fleet(scr, "X11")
        pre = shim(os.path.join(d, "shim-list"), "worktree list", "fatal: shim list failure")
        return root, write_record(os.path.join(d, "rec.tsv"), ROWS + "TOTAL\trepos=1\tregs=1\tprunable=0\n"), (), pre

    def x12(scr):
        d, root = base_fleet(scr, "X12")
        pre = shim(os.path.join(d, "shim-prune"), "worktree prune", "fatal: shim prune failure")
        return root, write_record(os.path.join(d, "rec.tsv"), ROWS + "TOTAL\trepos=1\tregs=1\tprunable=0\n"), (), pre

    def x13(scr):
        d, root = base_fleet(scr, "X13")
        body = ("REPO\talpha\tregs=2\tprunable=0\nREPO\tzeta\tregs=1\tprunable=0\n"
                "TOTAL\trepos=2\tregs=3\tprunable=0\n")
        return root, write_record(os.path.join(d, "rec.tsv"), body), (), None

    def x14(scr):
        d, root = base_fleet(scr, "X14")
        body = ROWS + ROWS + "TOTAL\trepos=2\tregs=2\tprunable=0\n"
        return root, write_record(os.path.join(d, "rec.tsv"), body), (), None

    def x18(scr):
        d, root = base_fleet(scr, "X18")
        broken_gitfile(root, "wt")
        body = "REPO\twt\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n"
        return root, write_record(os.path.join(d, "rec.tsv"), body), (), None

    def x19(scr):
        d, root = base_fleet(scr, "X19")
        return root, write_record(os.path.join(d, "rec.tsv"), ROWS + "TOTAL\trepos=1\tregs=1\tprunable=0\n"), (), None

    def x21(scr):
        d, root = base_fleet(scr, "X21")
        wt = os.path.join(d, "gone-wt")
        g(["-C", os.path.join(root, "alpha"), "worktree", "add", "-q", "-b", "gone", wt])
        shutil.rmtree(wt)
        body = "REPO\talpha\tregs=2\tprunable=1\nTOTAL\trepos=1\tregs=2\tprunable=1\n"
        return root, write_record(os.path.join(d, "rec.tsv"), body), (), None

    def x22(scr):
        d, root = base_fleet(scr, "X22")
        outside = os.path.join(d, "outside", "alpha2")
        mkrepo(outside)
        esc = os.path.join(root, "esc")
        os.makedirs(esc)
        with open(os.path.join(esc, ".git"), "w", encoding="utf-8") as handle:
            handle.write("gitdir: %s/.git\n" % outside)
        body = "REPO\tesc\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n"
        return root, write_record(os.path.join(d, "rec.tsv"), body), (), None

    def x24(scr):
        d = os.path.join(scr, "probe", "X24")
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(os.path.join(d, "work"))
        root = os.path.join(d, "rootrepo")
        mkrepo(root)
        mkrepo(os.path.join(root, "alpha"))
        mkrepo(os.path.join(root, "beta"))
        return root, write_record(os.path.join(d, "rec.tsv"), ROWS + "TOTAL\trepos=1\tregs=1\tprunable=0\n"), (), None

    return [
        ("X01", "symlinked child to a repo outside root", x01, ()),
        ("X02", "unrecorded child with a broken .git file (discovery)", x02, ()),
        ("X03", "recorded name whose direct dir has a .git file", x03, ()),
        ("X04", "control: recorded direct repo", x04, ()),
        ("X08", "live_regs accumulation (SUMMARY live_regs)", x08, ()),
        ("X09", "PRUNABLE-CHANGED (record prunable=1, live 0)", x09, ()),
        ("X10", "REGS-CHANGED with live > record (live 2, record 1)", x10, ()),
        ("X11", "worktree list failure (shim fails 'worktree list')", x11, ()),
        ("X12", "worktree prune failure (shim fails 'worktree prune')", x12, ()),
        ("X13", "drift row order (ABSENT zeta vs REGS-CHANGED alpha)", x13, ()),
        ("X14", "duplicate REPO name", x14, ()),
        ("X18", "SUMMARY drift_rows with one UNREACHABLE row", x18, ()),
        ("X19", "SUMMARY record_regs", x19, ()),
        ("X21", "SUMMARY live_prunable (one prunable worktree)", x21, ()),
        ("X22", "gitdir resolving outside root", x22, ()),
        ("X24", "root inserted at end of discovery (expected equivalent)", x24, ()),
    ]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", default=SCR_DEFAULT)
    args = ap.parse_args(argv)
    scr = os.path.abspath(args.scratch)
    pristine = os.path.join(scr, "mut", "pristine.py")
    print("%-4s %-58s %-12s %s" % ("id", "probe", "distinguished", "pristine_rc/mutant_rc"))
    for mid, desc, build, _ in probes(scr):
        if mid == "X04":
            mutant = os.path.join(scr, "mut", "X04.py")
        else:
            mutant = os.path.join(scr, "mut", mid + ".py")
        root, record, extra, prefix = build(scr)
        work = os.path.join(os.path.dirname(record), "work")
        rc_p, out_p = tool_run(pristine, root, record, extra, prefix, work)
        rc_m, out_m = tool_run(mutant, root, record, extra, prefix, work)
        differ = (rc_p, out_p) != (rc_m, out_m)
        print("%-4s %-58s %-12s rc %d/%d" % (mid, desc[:58], "yes" if differ else "no", rc_p, rc_m))
        print("     pristine: " + out_p.replace("\n", " | ")[:300])
        print("     mutant  : " + out_m.replace("\n", " | ")[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
