#!/usr/bin/env python3
# R41critic04 attack candidate, trick D (exit-code-only decoy). It RUNS the tool on a refusal trigger
# for each probe id but judges only that the exit code is nonzero; it never reads stderr or the class
# label. The pinned tool refuses with exit 2. Expected by the counter's design: a mutated label leaves
# the exit code unchanged, so every site survives.
import argparse
import os
import shutil
import subprocess
import sys

GOOD = "REPO\tfoo\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n"


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def run(tool, root, record, extra=()):
    args = ["python3", "-B", tool, "--root", root, "--record", record] + list(extra)
    try:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              timeout=60, check=False)
    except subprocess.TimeoutExpired:
        return None
    return proc.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    args = ap.parse_args()
    work = os.path.join(args.work, "decoy")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    tool = os.path.abspath(args.tool)
    root = os.path.join(work, "root")
    os.makedirs(os.path.join(root, "foo"))
    os.makedirs(os.path.join(work, "sibling"))
    gitrow = os.path.join(root, "gitrow")
    os.makedirs(gitrow)
    write(os.path.join(gitrow, ".git"), "gitdir: /elsewhere/outside\n")
    notdir = write(os.path.join(work, "notadir"), "x\n")
    good = write(os.path.join(work, "good.tsv"), GOOD)
    locked = write(os.path.join(work, "locked.tsv"), GOOD)
    os.chmod(locked, 0)
    loop = os.path.join(work, "loop.tsv")
    os.symlink(loop, loop)
    dirrec = os.path.join(work, "dir.d")
    os.makedirs(dirrec)
    fifo = os.path.join(work, "out.fifo")
    os.mkfifo(fifo)
    outdir = os.path.join(work, "outdir")
    os.makedirs(outdir)
    outside = write(os.path.join(work, "linked.json"), "{}\n")
    os.link(outside, os.path.join(work, "linked2.json"))
    ro = os.path.join(work, "ro")
    os.makedirs(ro)
    os.chmod(ro, 0o500)

    cases = {
        "P01": (root, os.path.join(work, "nonexistent.tsv"), ()),
        "P02a": (root, locked, ()),
        "P02b": (root, loop, ()),
        "P03": (root, dirrec, ()),
        "P04": (root, write(os.path.join(work, "dup.tsv"),
                            "REPO\tfoo\tregs=1\tprunable=0\nREPO\tfoo\tregs=1\tprunable=0\n"), ()),
        "P05": (root, write(os.path.join(work, "bad.tsv"), "garbage line\n"), ()),
        "P06": (root, write(os.path.join(work, "empty.tsv"), "# only a comment\n"), ()),
        "P07": (root, write(os.path.join(work, "t7.tsv"),
                            "REPO\tfoo\tregs=1\tprunable=0\nTOTAL\trepos=2\tregs=1\tprunable=0\n"), ()),
        "P08": (root, write(os.path.join(work, "t8.tsv"),
                            "REPO\tfoo\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=9\tprunable=0\n"), ()),
        "P09": (root, write(os.path.join(work, "t9.tsv"),
                            "REPO\tfoo\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=9\n"), ()),
        "P10a": (root, good, ("--json", fifo)),
        "P10b": (root, good, ("--json", outdir)),
        "P11": (root, good, ("--json", "/dev/null")),
        "P12": (notdir, good, ()),
        "P13": (root, write(os.path.join(work, "rel.tsv"),
                            "REPO\t../sibling\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n"), ()),
        "P14": (root, write(os.path.join(work, "gitrow.tsv"),
                            "REPO\tgitrow\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n"), ()),
        "P15": (root, good, ("--json", good)),
        "P16": (root, good, ("--json", os.path.join(root, "foo", "out.json"))),
        "P17": (root, good, ("--json", outside)),
        "P18": (root, good, ("--json", os.path.join(ro, "out.json"))),
        "P19": (root, good, ("--timeout", "0")),
    }
    results = {}
    for pid in sorted(cases):
        root_, record, extra = cases[pid]
        results[pid] = run(tool, root_, record, extra)

    failing = 0
    for pid in sorted(results):
        ok = results[pid] not in (0, None)
        failing += 0 if ok else 1
        print("probe-%s=%s rc=%s" % (pid, "PASS" if ok else "FAIL", results[pid]))
    print("SUMMARY probes=%d pass=%d fail=%d" % (len(results), len(results) - failing, failing))
    os.chmod(ro, 0o700)
    os.chmod(locked, 0o600)
    shutil.rmtree(work, ignore_errors=True)
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
