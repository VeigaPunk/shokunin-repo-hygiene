#!/usr/bin/env python3
"""Supplementary probe: show a surviving C1 mutant is behaviourally distinct.

Rebuilds a matrix case repo from the frozen case files, rewrites the Control
receipt with one edit, then runs the pristine and the mutant --substance arm on
the SAME rebuilt repo and prints both verdicts and FINDING lines.

A survivor is confirmed as a missing fixture assertion when pristine refuses
(exit 1, the expected class) and the mutant accepts (exit 0).

usage: probe_c1.py --build-matrix P --case-dir DIR --pristine P --mutant P
                    --edit {instrument-name,command-missing} --outdir DIR
"""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys


def load(path):
    spec = importlib.util.spec_from_file_location("bm", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def edit_ctl(path, kind):
    with open(path, "rb") as f:
        text = f.read().decode("utf-8")
    if kind == "instrument-name":
        assert text.count("instrument=counter.py") == 1, "anchor"
        text = text.replace("instrument=counter.py", "instrument=other-tool.py")
    elif kind == "command-missing":
        lines = [l for l in text.splitlines() if not l.startswith("command=")]
        assert len(lines) != len(text.splitlines()), "anchor"
        text = "\n".join(lines) + "\n"
    else:
        raise SystemExit("unknown edit %r" % kind)
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))


def run(tool, repo, rev, outdir, tag):
    argv = [sys.executable, "-B", tool, "--root", repo, "--prereg", "pre.txt",
            "--rev", rev, "--substance"]
    p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode() + p.stderr.decode()
    with open(os.path.join(outdir, tag + ".txt"), "w", encoding="utf-8") as f:
        f.write("ARGV %s\n%sEXIT=%d\n" % (json.dumps(argv), out, p.returncode))
    return p.returncode, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-matrix", required=True)
    ap.add_argument("--case-dir", required=True)
    ap.add_argument("--pristine", required=True)
    ap.add_argument("--mutant", required=True)
    ap.add_argument("--edit", required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    bm = load(a.build_matrix)
    case = os.path.join(a.outdir, "case")
    if os.path.isdir(case):
        shutil.rmtree(case)
    shutil.copytree(a.case_dir, case)
    edit_ctl(os.path.join(case, "ctl.txt"), a.edit)
    repo = os.path.join(a.outdir, "repo")
    if os.path.isdir(repo):
        shutil.rmtree(repo)
    _anc, freeze = bm.rebuild_case("honest-1", repo, case)
    prc, pout = run(a.pristine, repo, freeze, a.outdir, "pristine")
    mrc, mout = run(a.mutant, repo, freeze, a.outdir, "mutant")
    cls = [l.split()[2] for l in pout.splitlines() if l.startswith("FINDING ")]
    print("edit=%s pristine_exit=%d findings=%s mutant_exit=%d"
          % (a.edit, prc, ",".join(cls) or "-", mrc))
    print("MISSING-ASSERTION-CONFIRMED" if (prc == 1 and mrc == 0) else "NO-DIVERGENCE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
