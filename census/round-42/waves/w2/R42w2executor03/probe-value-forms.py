#!/usr/bin/env python3
"""Targeted probe: what does the tool say for out-of-grammar Counter values when the counter exists at freeze?
  python3 -B probe-value-forms.py TOOL SCRATCH
One fixture repo per form (counter+population+control present at freeze, prereg otherwise valid)."""
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


CNT = "c\n"
H = hashlib.sha256(CNT.encode()).hexdigest()
def forms(P):
    return {
        "ok": "%s sha256=%s" % (P, H),
        "no-digest": P,
        "upper-hex": "%s sha256=%s" % (P, H.upper()),
        "63-hex": "%s sha256=%s" % (P, H[:63]),
        "trailing-word": "%s sha256=%s extra" % (P, H),
        "two-spaces-before-sha": "%s  sha256=%s" % (P, H),
        "tab-before-sha": "%s\tsha256=%s" % (P, H),
        "sha256-colon": "%s sha256:%s" % (P, H),
        "no-space-before-sha": "%ssha256=%s" % (P, H),
    }


out = []
CASES = [(P, name, val) for P in ("census/c.py", "census/c d.py") for name, val in forms(P).items()]
for P, name, val in CASES:
    D = tempfile.mkdtemp(prefix="vf-", dir=SCR)
    try:
        git(D, "init", "-q", "-b", "main")
        assert os.path.realpath(git(D, "rev-parse", "--show-toplevel")) == os.path.realpath(D)
        open(os.path.join(D, "README.md"), "w").write("r\n")
        git(D, "add", "-A")
        git(D, "commit", "-q", "-m", "base")
        base = git(D, "rev-parse", "HEAD")
        os.makedirs(os.path.join(D, "census"))
        open(os.path.join(D, P), "w").write(CNT)
        open(os.path.join(D, "census/p.tsv"), "w").write("h\nr\n")
        open(os.path.join(D, "census/k.txt"), "w").write("EXIT=1\n")
        ph = hashlib.sha256(b"h\nr\n").hexdigest()
        open(os.path.join(D, "census/pre.txt"), "w").write(
            "Round: 7\n## C1\nBase: %s\nCounter: %s\nPopulation: census/p.tsv sha256=%s\nControl: census/k.txt\n"
            "Target: t\nKill: k\n" % (base, val, ph))
        git(D, "add", "-A")
        git(D, "commit", "-q", "-m", "freeze")
        tip = git(D, "rev-parse", "HEAD")
        p = subprocess.run(["python3", "-B", TOOL, "--root", D, "--prereg", "census/pre.txt", "--rev", tip],
                           env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        fl = [re.sub(r"[0-9a-f]{40,64}", "<hex>", x)[:120] for x in p.stdout.splitlines() if x.startswith("FINDING")]
        out.append("%-14s %-24s exit=%d %s" % (P, name, p.returncode, fl or "(clean)"))
    finally:
        shutil.rmtree(D, ignore_errors=True)
print("\n".join(out))
