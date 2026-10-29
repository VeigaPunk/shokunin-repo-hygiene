#!/usr/bin/env python3
"""Held-out differential check for the r42 C2 grammar (R42critic02 attack harness).

The fixtures below are NOT in census/round-42/c2-cases.tsv or c2-counter.py CASES. Every expectation was
written from the c2-counter.py docstring grammar before any candidate was run; none was copied from a tool's
output. Each fixture is a synthetic git repository built under --scratch (a directory named ho-<case>).

  python3 -B heldout-check.py --scratch DIR TOOL [TOOL...]

Prints `HELDOUT <tool> <case>=PASS|FAIL [detail]` and `HELDOUT-SUMMARY <tool> pass=<p> fail=<f> n=<n>`.
Removes only the scratch directories it created.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

COUNTER = "# counter\nprint('counter')\n"
POPULATION = "id\tname\n1\talpha\n2\tbeta\n"
CONTROL = "SUMMARY items=2 corrected=0\nEXIT=1\n"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
           "GIT_AUTHOR_NAME": "heldout", "GIT_AUTHOR_EMAIL": "heldout@example.invalid",
           "GIT_COMMITTER_NAME": "heldout", "GIT_COMMITTER_EMAIL": "heldout@example.invalid"}
FINDING = re.compile(r"^FINDING (\S+) (\S+)", re.M)

# name, fixture spec, expected exit code, expected sorted (claim, class) multiset, why (docstring clause)
FIXTURES = (
    ("H1-dispatch-jsonl-before", {"before": [".ufo/waves/round-42/w1/Seat01-dispatch.jsonl"]}, 1,
     [("C0", "DISPATCH-BEFORE-FREEZE")], "basename contains -dispatch, any depth"),
    ("H2-dispatch-deep-ready", {"before": [".ufo/waves/round-42/w1/deep/x.ready"]}, 1,
     [("C0", "DISPATCH-BEFORE-FREEZE")], "basename contains .ready at any depth"),
    ("H3-dispatch-spec-bak", {"before": [".ufo/waves/round-42/w1-spec.json.bak"]}, 0, [],
     "-spec.json.bak neither ends -spec.json nor contains -dispatch/.ready"),
    ("H4-dispatch-other-round", {"before": [".ufo/waves/round-41/w1-dispatch.json"]}, 0, [],
     "only .ufo/waves/round-<N>/ of the Round line is scanned"),
    ("H5-dup-kill-triple", {"extra": ["Kill: any uncorrected", "Kill: any uncorrected"]}, 1,
     [("C1", "KEY-DUPLICATE")], "one finding per duplicated key, not per extra line"),
    ("H6-dup-two-keys", {"extra": ["Kill: x", "Target: y"]}, 1,
     [("C1", "KEY-DUPLICATE"), ("C1", "KEY-DUPLICATE")], "one finding per duplicated key (two keys, two findings)"),
    ("H7-heading-hash3", {"tail": "### C2 - sub\n"}, 0, [],
     "a line starting ### is excluded from HEADING-MALFORMED and opens no claim"),
    ("H8-heading-C-no-digit", {"tail": "## C - sub\n"}, 0, [],
     "HEADING-MALFORMED needs a digit after C; the line opens no claim"),
    ("H9-heading-glued-no-digit", {"tail": "##C\n"}, 0, [],
     "##C with no digit does not match the malformed pattern"),
    ("H10-counter-symlink-dangling", {"counter_symlink": "missing-target"}, 1,
     [("C1", "COUNTER-SYMLINK")], "a symlink at freeze gives COUNTER-SYMLINK alone, even when the target is absent"),
    ("H11-clean-trailing-spaces", {"trailing": True}, 0, [],
     "KEYLINE strips trailing spaces; a clean claim stays clean"),
)


def sha(text):
    return hashlib.new("sha256", text.encode("utf-8")).hexdigest()


def build(scratch, name, spec):
    d = os.path.join(scratch, "ho-" + name)
    os.makedirs(d)
    env = dict(GIT_ENV, PATH=os.environ.get("PATH", "/usr/bin:/bin"))

    def git(*args):
        p = subprocess.run(["git", "-C", d] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=env, check=False)
        if p.returncode != 0:
            raise RuntimeError("git %s: %s" % (args[0], p.stderr.decode("utf-8", "replace")))
        return p.stdout.decode("utf-8", "replace").strip()

    def write(rel, text):
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def commit(msg):
        git("add", "-A")
        git("commit", "-q", "-m", msg)
        return git("rev-parse", "HEAD")

    git("init", "-q", "-b", "main")
    write("README", "base\n")
    base = commit("base")
    if spec.get("before"):
        for rel in spec["before"]:
            write(rel, "x\n")
        commit("early wave files")
    fields = ["Base: %s" % base,
              "Counter: census/c1.py sha256=%s" % sha(COUNTER),
              "Population: census/pop.tsv sha256=%s" % sha(POPULATION),
              "Control: census/control.txt",
              "Target: items=2 corrected=2" + ("   " if spec.get("trailing") else ""),
              "Kill: any uncorrected"]
    lines = ["# prereg", "Round: 42", "", "## C1 - claim 1"] + fields + list(spec.get("extra", [])) + [""]
    write("prereg.txt", "\n".join(lines) + "\n" + spec.get("tail", ""))
    if spec.get("counter_symlink"):
        os.makedirs(os.path.join(d, "census"), exist_ok=True)
        os.symlink(spec["counter_symlink"], os.path.join(d, "census/c1.py"))
    else:
        write("census/c1.py", COUNTER)
    write("census/pop.tsv", POPULATION)
    write("census/control.txt", CONTROL)
    commit("freeze")
    return d, git("rev-parse", "HEAD")


def run_case(tool, scratch, name, spec, want_rc, want):
    d, tip = build(scratch, name, spec)
    p = subprocess.run(["python3", "-B", tool, "--root", d, "--prereg", "prereg.txt", "--rev", tip],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
                       env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "TMPDIR": scratch}, timeout=300)
    got = sorted(FINDING.findall(p.stdout))
    crash = "Traceback (most recent call last)" in p.stderr
    ok = p.returncode == want_rc and got == sorted(want) and not crash
    return ok, "rc=%d want=%d got=%r want=%r crash=%s" % (p.returncode, want_rc, got, sorted(want), crash)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("tools", nargs="+")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.scratch):
        sys.stderr.write("--scratch is not a directory\n")
        return 2
    root = tempfile.mkdtemp(prefix="heldout.", dir=args.scratch)
    try:
        for tool in args.tools:
            passed = 0
            for name, spec, rc, want, _why in FIXTURES:
                ok, detail = run_case(tool, root, name, spec, rc, want)
                passed += 1 if ok else 0
                print("HELDOUT %s %s=%s%s" % (os.path.basename(tool), name, "PASS" if ok else "FAIL",
                                              "" if ok else " " + detail))
                shutil.rmtree(os.path.join(root, "ho-" + name), ignore_errors=True)
            print("HELDOUT-SUMMARY %s pass=%d fail=%d n=%d" % (os.path.basename(tool), passed,
                                                              len(FIXTURES) - passed, len(FIXTURES)))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
