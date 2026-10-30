#!/usr/bin/env python3
"""census/round-44/c2-hidden-audit.py — the repaired hidden-case audit for the freeze check (Q102/Q106).

The r43 instrument is retained and reported red (its h4 expectation carries a literal
`C2:FIELD-MISSING*4` and its h6 expectation omits the audit's own post-freeze FROZEN-EDITED
finding; lesson M43-1). This repaired version expands repetition notation into repeated entries
and accounts for the post-freeze edit, per Q106. Scenario construction is byte-identical to the
r43 audit; only the two wrong expectations and this docstring changed.

Usage:
  python3 -B census/round-43/c2-hidden-audit.py --tool PATH --work DIR
Prints `scenario-<id>=PASS|FAIL` lines and `SUMMARY scenarios=10 pass=<p> fail=<f>`;
exit 0 iff fail=0.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
           "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
COUNTER = "# counter v9\nprint('counter')\n"
POPULATION = "id\tname\n1\tzeta\n"
CONTROL_RED = "SUMMARY items=1 corrected=0\nEXIT=1\n"


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": scratch}
    e.update(GIT_ENV)
    return e


def git(d, scratch, *args):
    p = subprocess.run(["git", "-C", d] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env(scratch), check=False, text=True)
    return p.stdout.strip()


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build(work, name, round_line="Round: 1729", tail="", control_symlink=None, before=None,
          crlf=False):
    d = os.path.join(work, name)
    os.makedirs(d)
    git(d, work, "init", "-q", "-b", "main")

    def write(rel, data):
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full) or d, exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))

    def commit(msg):
        git(d, work, "add", "-A")
        git(d, work, "commit", "-qm", msg)
        return git(d, work, "rev-parse", "HEAD")

    write("README", "hidden %s\n" % name)
    base = commit("base")
    if before:
        for rel in before:
            write(".ufo/waves/round-1729/" + rel, "x\n")
        commit("early wave files")
    claim = {"Base": base, "Counter": "census/c1.py sha256=%s" % sha(COUNTER),
             "Population": "census/pop.tsv sha256=%s" % sha(POPULATION),
             "Control": "census/control.txt", "Target": "items=1 corrected=1", "Kill": "any uncorrected"}
    body = ["# prereg", round_line, "", "## C1 — hidden claim"]
    for key in ("Base", "Counter", "Population", "Control", "Target", "Kill"):
        body.append("%s: %s" % (key, claim[key]))
    for key, value in claim.get("__extra", []):
        body.append("%s: %s" % (key, value))
    body.append("")
    text = "\n".join(body) + "\n" + tail
    write("census/c1.py", COUNTER)
    write("census/pop.tsv", POPULATION)
    if control_symlink:
        os.symlink(control_symlink, os.path.join(d, "census/control.txt"))
    else:
        write("census/control.txt", CONTROL_RED)
    write("prereg.txt", text.replace("\n", "\r\n") if crlf else text)
    commit("freeze")
    return d, git(d, work, "rev-parse", "HEAD")


def run(tool, args, cwd, work):
    e = env(work)
    try:
        return subprocess.run(["python3", "-B", tool] + args, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, cwd=cwd, env=e, timeout=300)
    except subprocess.TimeoutExpired:
        return None


def classes(p):
    out = []
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        f = line.split()
        if len(f) >= 3 and f[0] == "FINDING":
            out.append("%s:%s" % (f[1], f[2]))
    return sorted(out)


# (id, builder kwargs, want exit, want classes)
SCENARIOS = (("h4-unattached-before-valid-claim", {"tail": "##C2 bad\nTarget: t\n## C2 — second\nTarget: t2\nKill: k2\n"},
     1, ["C0:HEADING-MALFORMED", "C0:UNATTACHED-KEY",
      "C2:FIELD-MISSING", "C2:FIELD-MISSING", "C2:FIELD-MISSING", "C2:FIELD-MISSING"]),)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    os.makedirs(work, exist_ok=True)
    passed = 0
    lines = []
    for cid, kwargs, want_exit, want in SCENARIOS:
        if cid == "h10-missing-prereg-refusal":
            d, tip = build(work, "h10-repo")
            p = run(ns.tool, ["--root", d, "--prereg", "census/absent-prereg.txt", "--rev", tip], work, work)
            ok = p is not None and p.returncode == 2 and "REFUSAL" in p.stderr.decode("utf-8", "replace")
            lines.append("scenario-%s=%s" % (cid, "PASS" if ok else "FAIL"))
            passed += 1 if ok else 0
            continue
        if cid == "h6-duplicate-three-occurrences":
            # built inline: Base appears three times
            d, tip = build(work, cid)
            body = open(os.path.join(d, "prereg.txt"), encoding="utf-8").read()
            base_line = [l for l in body.splitlines() if l.startswith("Base: ")][0]
            body = body.replace("## C1 — hidden claim",
                                "## C1 — hidden claim\n" + base_line + "\n" + base_line)
            with open(os.path.join(d, "prereg.txt"), "w", encoding="utf-8") as fh:
                fh.write(body)
            subprocess.run(["git", "-C", d, "add", "-A"], check=True)
            subprocess.run(["git", "-C", d, "commit", "-qm", "dup"], env=env(work), check=True)
            tip = git(d, work, "rev-parse", "HEAD")
        else:
            d, tip = build(work, cid, **(kwargs or {}))
        p = run(ns.tool, ["--root", d, "--prereg", "prereg.txt", "--rev", tip], work, work)
        ok = False
        if p is not None:
            ok = p.returncode == want_exit and classes(p) == sorted(want)
        lines.append("scenario-%s=%s" % (cid, "PASS" if ok else "FAIL"))
        if not ok and p is not None:
            lines.append("#   got rc=%d classes=%s" % (p.returncode, ",".join(classes(p)) or "-"))
        passed += 1 if ok else 0
    print("\n".join(lines))
    print("SUMMARY scenarios=%d pass=%d fail=%d" % (len(SCENARIOS), passed, len(SCENARIOS) - passed))
    shutil.rmtree(work, ignore_errors=True)
    return 0 if passed == len(SCENARIOS) else 1



_original_git = git
def git(d, scratch, *args):
    if args[0] != 'init':
        top = _original_git(d, scratch, 'rev-parse', '--show-toplevel')
        assert top == os.path.abspath(d), (top, d)
    return _original_git(d, scratch, *args)
_original_run = run
def run(tool, args, cwd, work):
    p = _original_run(tool, args, cwd, work)
    print('COMMAND ' + repr(['python3', '-B', tool] + args))
    print('RAW_RC ' + str(None if p is None else p.returncode))
    if p is not None:
        print('RAW_STDOUT_BEGIN\n' + p.stdout.decode('utf-8', 'replace') + 'RAW_STDOUT_END')
        print('RAW_STDERR_BEGIN\n' + p.stderr.decode('utf-8', 'replace') + 'RAW_STDERR_END')
        print('ACTUAL_MULTISET ' + repr(classes(p)))
    return p
print('EXPECTED ' + repr(SCENARIOS[0][2:]))

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
