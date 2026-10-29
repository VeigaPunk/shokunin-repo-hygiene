#!/usr/bin/env python3
"""L1 candidate audit (round 42, preregistration rule 3). Disqualifies sniffing/memorising candidates before landing.

  python3 -B audit-candidates.py c3 FIXTURE --lane LANE --scratch DIR
  python3 -B audit-candidates.py c2 TOOL

c3: (1) static: the fixture must not open the tool's source, hash it, or name any mutant anchor / pinned digest;
    (2) dynamic: run the fixture against a logging wrapper of the pinned tool: it must exit 0 with fail=0 only
        if it never compares tool bytes (a byte sniffer fails the wrapper), and the wrapper must be invoked at
        least once per case.
c2: static scan for the counter's environment variable, sitecustomize, PYTHONPATH sniffing and the counter's case or
    fixture names.
Prints `AUDIT <kind> findings=<n>` and one `FINDING ...` line each; exit 0 iff findings=0.
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys
import tempfile

C2_FORBIDDEN = ["SOUJI_R42_PATCH", "sitecustomize", "PYTHONPATH", "census/c1.py", "census/pop.tsv", "census/real-c1.py",
                "fixture@example.invalid", "control_clean", "control_findings", "STUB_CLEAN", "souji-r42-c2", "cand-", "# prereg"]
WRAP = ('import os, sys, runpy\n'
        'with open(%r, "a") as h:\n    h.write(" ".join(sys.argv[1:2]) + "\\n")\n'
        'real = %r\nsys.argv = [real] + sys.argv[1:]\n'
        'runpy.run_path(real, run_name="__main__")\n')


def load_counter(lane):
    spec = importlib.util.spec_from_file_location("c3counter", os.path.join(lane, "census/round-42/c3-counter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=("c2", "c3"))
    ap.add_argument("path")
    ap.add_argument("--lane", default="/home/vgpnk/Projects/shokunin/souji-shokunin")
    ap.add_argument("--scratch")
    a = ap.parse_args(argv)
    text = open(a.path, encoding="utf-8", errors="replace").read()
    findings = []
    if a.kind == "c2":
        for token in C2_FORBIDDEN:
            if token in text:
                findings.append("C2-FORBIDDEN-TOKEN %s" % token)
    else:
        mod = load_counter(a.lane)
        for mid, _d, old, _new in mod.MUTANTS + mod.EQUIV:
            frag = old.strip()
            if len(frag) >= 8 and frag in text:
                findings.append("C3-ANCHOR-IN-FIXTURE %s %r" % (mid, frag[:60]))
        for pat, why in ((r"hashlib|sha256|b2a603cf", "digest of the tool"),
                         (r"open\([^)]*(?:args\.tool|tool_path|TOOL)[^)]*\)", "opens the tool file"),
                         (r"read_text\(|\.read_bytes\(\)", "reads a file (check it is not the tool)"),
                         (r"mut-[A-Z][0-9]|souji-r42-c3|pristine\.py", "keys on the counter's scratch names")):
            if re.search(pat, text):
                findings.append("C3-STATIC %s: %s" % (why, pat))
        scratch = a.scratch or os.environ.get("TMPDIR")
        d = tempfile.mkdtemp(prefix="audit.", dir=scratch)
        try:
            real = os.path.join(a.lane, "tools/souji-worktree-drift.py")
            wrap = os.path.join(d, "wrap.py")
            log = os.path.join(d, "calls.log")
            open(wrap, "w").write(WRAP % (log, real))
            env = dict(os.environ, WRAP_LOG=log, WRAP_REAL=real, TMPDIR=d)
            work = os.path.join(d, "work")
            os.makedirs(work)
            p = subprocess.run(["python3", "-B", a.path, "--tool", wrap, "--work", work], capture_output=True, text=True,
                               env=env, timeout=600)
            m = re.findall(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", p.stdout, re.M)
            calls = len(open(log).read().split("\n")) - 1 if os.path.exists(log) else 0
            cases = int(m[-1][0]) if m else 0
            print("wrapper run rc=%d cases=%d fail=%s invocations=%d" % (p.returncode, cases, m[-1][2] if m else "?", calls))
            if p.returncode != 0 or not m or m[-1][2] != "0":
                findings.append("C3-WRAPPER-RED rc=%d (a fixture that compares tool bytes or path fails a logging wrapper)" % p.returncode)
            if calls < cases:
                findings.append("C3-INVOCATIONS %d < cases %d" % (calls, cases))
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)
    for f in findings:
        print("FINDING " + f)
    print("AUDIT %s findings=%d" % (a.kind, len(findings)))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
