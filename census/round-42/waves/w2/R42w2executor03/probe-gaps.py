#!/usr/bin/env python3
"""Targeted probe of the docstring gaps: POPULATION-EMPTY threshold, CONTROL-NOT-RED reading, post-freeze control edit.
  python3 -B probe-gaps.py TOOL SCRATCH"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOL, SCR = sys.argv[1], sys.argv[2]
ENV = {"PATH": os.environ["PATH"], "TMPDIR": SCR, "HOME": SCR, "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "fx", "GIT_AUTHOR_EMAIL": "fx@example.invalid",
       "GIT_COMMITTER_NAME": "fx", "GIT_COMMITTER_EMAIL": "fx@example.invalid"}


def git(d, *a):
    return subprocess.run(["git", "-C", d] + list(a), env=ENV, check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True).stdout.strip()


def run(pop="h\nr\n", ctl="EXIT=1\n", post_ctl=None):
    D = tempfile.mkdtemp(prefix="pg-", dir=SCR)
    try:
        git(D, "init", "-q", "-b", "main")
        assert os.path.realpath(git(D, "rev-parse", "--show-toplevel")) == os.path.realpath(D)
        open(os.path.join(D, "README.md"), "w").write("r\n")
        git(D, "add", "-A")
        git(D, "commit", "-q", "-m", "base")
        base = git(D, "rev-parse", "HEAD")
        os.makedirs(os.path.join(D, "census"))
        open(os.path.join(D, "census/c.py"), "w").write("c\n")
        open(os.path.join(D, "census/p.tsv"), "wb").write(pop.encode())
        open(os.path.join(D, "census/k.txt"), "wb").write(ctl.encode())
        open(os.path.join(D, "census/pre.txt"), "w").write(
            "Round: 7\n## C1\nBase: %s\nCounter: census/c.py sha256=%s\nPopulation: census/p.tsv sha256=%s\n"
            "Control: census/k.txt\nTarget: t\nKill: k\n"
            % (base, hashlib.sha256(b"c\n").hexdigest(), hashlib.sha256(pop.encode()).hexdigest()))
        git(D, "add", "-A")
        git(D, "commit", "-q", "-m", "freeze")
        if post_ctl is not None:
            open(os.path.join(D, "census/k.txt"), "wb").write(post_ctl.encode())
            git(D, "add", "-A")
            git(D, "commit", "-q", "-m", "post")
        tip = git(D, "rev-parse", "HEAD")
        p = subprocess.run(["python3", "-B", TOOL, "--root", D, "--prereg", "census/pre.txt", "--rev", tip],
                           env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        fl = [re.sub(r"[0-9a-f]{40,64}", "<hex>", x)[8:90] for x in p.stdout.splitlines() if x.startswith("FINDING")]
        return "exit=%d %s" % (p.returncode, fl or "(clean)")
    finally:
        shutil.rmtree(D, ignore_errors=True)


print("== population variants (control red, counter ok)")
for label, pop in [("zero bytes", ""), ("only newline", "\n"), ("header only", "h\n"), ("header + blank lines", "h\n\n \n"),
                   ("header + 1 row", "h\n1\n"), ("header + blank + 1 row", "h\n\n1\n"), ("1 row CRLF + header", "h\r\n1\r\n"),
                   ("no trailing newline 2 rows", "h\n1")]:
    print("%-28s %s" % (label, run(pop=pop)))
print("== control variants (population ok)")
for label, ctl in [("EXIT=1", "EXIT=1\n"), ("EXIT=1 no newline", "EXIT=1"), ("EXIT=1 + blank lines", "EXIT=1\n\n\n"),
                   ("EXIT=0", "EXIT=0\n"), ("no EXIT line", "SUMMARY x\n"), ("EXIT=1 then prose", "EXIT=1\nnote\n"),
                   ("EXIT=0 then EXIT=1", "EXIT=0\nEXIT=1\n"), ("EXIT=1 then EXIT=0", "EXIT=1\nEXIT=0\n"),
                   ("EXIT=1 CRLF", "x\r\nEXIT=1\r\n"), ("EXIT=01", "EXIT=01\n"), ("EXIT=-1", "EXIT=-1\n"),
                   ("leading space ' EXIT=1'", " EXIT=1\n"), ("EXIT=1 trailing space", "EXIT=1 \n"), ("exit=1 lowercase", "exit=1\n"),
                   ("empty file", "")]:
    print("%-28s %s" % (label, run(ctl=ctl)))
print("== control edited AFTER freeze (frozen rule: Control must not change)")
for label, post in [("red -> green", "EXIT=0\n"), ("red -> different red", "x\nEXIT=2\n")]:
    print("%-28s %s" % (label, run(post_ctl=post)))
