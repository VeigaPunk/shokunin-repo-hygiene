#!/usr/bin/env python3
"""r38-drift-write-envelope.py — the drift tool's output envelope, end to end.

r37 named three limits this fixture freezes as cases and scores against the r37
blob (`--base-tool`):

  - `--record X --json X` overwrote the record when the record lay outside
    `--root` (the tool exited 0 and replaced its input with JSON);
  - a `--json` FIFO blocked the run forever (a blocking O_WRONLY open);
  - the module docstring's exit-2 enumeration named only
    RECORD-MISSING / RECORD-MALFORMED / RECORD-EMPTY / usage while the code
    returns 2 for four more classes.

Cases (each builds its own synthetic fleet under `--work`):
  fifo-json-refused        `--json` naming a FIFO is refused, rc 2, within the bound
  fifo-json-with-reader    the same with a reader attached (the open succeeds, the
                           fstat refuses) — still no hang
  record-alias-refused     `--json` naming the record is refused; record bytes intact
  record-hardlink-refused  `--json` naming a hardlink of the record is refused;
                           record bytes intact
  docstring-enum           every refusal class the code can raise appears in the
                           module docstring (static)
  json-written-regular     a regular `--json` outside every measured tree is written
  json-inside-tree         a `--json` inside `--root` is refused (regression)
  json-hardlinked          an existing multi-link `--json` is refused (regression)
  json-symlink-resolved    a `--json` leaf symlink is written at its resolved path
  json-directory           a `--json` naming a directory is refused
  record-outside-root      a record row escaping `--root` is refused (regression)
  summary-still-exact      the plain run still prints its SUMMARY line

CLI:
  python3 -B tests/fixtures/r38-drift-write-envelope.py [--tool PATH]
      [--base-tool PATH] [--work DIR]

`--base-tool` scores the same cases against another tool blob and prints the
`base_fail=` arm; the base tool is expected to fail at least the three cases the
round repairs.

Exit: 0 every case passed, 1 otherwise, 2 usage.
"""
import argparse
import ast
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tokenize

ENV = {
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
    "LC_ALL": "C",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}
BOUND = 15


def sh(cmd):
    return subprocess.run(cmd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def make_repo(path):
    os.makedirs(path)
    sh(["git", "init", "-q", "-b", "main", path])
    write(os.path.join(path, "file.txt"), "base\n")
    sh(["git", "-C", path, "add", "file.txt"])
    sh(["git", "-C", path, "commit", "-qm", "base"])
    return path


def fleet(scratch, name):
    root = os.path.join(scratch, name)
    os.makedirs(root)
    path = os.path.join(root, "fleet")
    make_repo(os.path.join(path, "alpha"))
    record = os.path.join(root, "record.tsv")
    write(record, "REPO\talpha\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
    return root, path, record


def invoke(tool, path, rec, extra):
    start = time.time()
    try:
        proc = subprocess.run(
            ["python3", "-B", tool, "--root", path, "--record", rec, "--timeout", "30"] + extra,
            env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, timeout=BOUND,
        )
        return proc.returncode, proc.stdout + proc.stderr, time.time() - start, False
    except subprocess.TimeoutExpired:
        return None, "", time.time() - start, True


def has_token(text, token):
    """Whole-token containment: `JSON-HARDLINKED-LEGACY` is not `JSON-HARDLINKED`."""
    start = 0
    while True:
        idx = text.find(token, start)
        if idx < 0:
            return False
        before = text[idx - 1] if idx > 0 else " "
        after = text[idx + len(token)] if idx + len(token) < len(text) else " "
        if not before.isalnum() and after not in "-_" and not after.isalnum():
            return True
        start = idx + 1


def check(name, ok, detail, results):
    results.append((name, bool(ok), detail))


def run_cases(tool, work):
    scratch = tempfile.mkdtemp(prefix="souji-r38-envelope.", dir=work)
    results = []
    try:
        # fifo-json-refused
        root, path, rec = fleet(scratch, "fifo")
        fifo = os.path.join(root, "out.fifo")
        os.mkfifo(fifo)
        before = open(rec, encoding="utf-8").read()
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", fifo])
        check("fifo-json-refused", (not hung) and rc == 2 and "JSON-NOT-REGULAR" in out
              and open(rec, encoding="utf-8").read() == before,
              "rc=%r hung=%s elapsed=%.1fs out=%r" % (rc, hung, elapsed, out.splitlines()[:2]), results)

        # fifo-json-with-reader: the open can succeed here, so the fstat must refuse
        root, path, rec = fleet(scratch, "fifo-reader")
        fifo = os.path.join(root, "out2.fifo")
        os.mkfifo(fifo)
        reader = subprocess.Popen(["cat", fifo], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", fifo])
        finally:
            reader.kill()
            reader.wait()
        check("fifo-json-with-reader", (not hung) and rc == 2 and "JSON-NOT-REGULAR" in out,
              "rc=%r hung=%s elapsed=%.1fs out=%r" % (rc, hung, elapsed, out.splitlines()[:2]), results)

        # record-alias-refused
        root, path, rec = fleet(scratch, "alias")
        before = open(rec, encoding="utf-8").read()
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", rec])
        check("record-alias-refused", (not hung) and rc == 2 and "JSON-IS-RECORD" in out
              and open(rec, encoding="utf-8").read() == before,
              "rc=%r out=%r record_intact=%s" % (rc, out.splitlines()[:2],
                                                open(rec, encoding="utf-8").read() == before), results)

        # record-hardlink-refused
        root, path, rec = fleet(scratch, "alias-link")
        link = os.path.join(root, "record.link.tsv")
        os.link(rec, link)
        before = open(rec, encoding="utf-8").read()
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", link])
        check("record-hardlink-refused", (not hung) and rc == 2 and "JSON-IS-RECORD" in out
              and open(rec, encoding="utf-8").read() == before,
              "rc=%r out=%r record_intact=%s" % (rc, out.splitlines()[:2],
                                                open(rec, encoding="utf-8").read() == before), results)

        # docstring-enum (static; r38 A1 after wave-1 seat W1RevDocstring). The first draft
        # read source.split('"""')[1] and matched substrings, so it false-rejected a raise
        # form inside a comment (a1), accepted a triple-quoted module constant as the
        # docstring (b1), accepted a doc-only phantom token (d), accepted a class name
        # degraded to a prefix (d2), and missed the tool's other exit-2 idiom
        # `REFUSAL <TOKEN>:` on stderr (c2). The case now reads the real module docstring
        # through ast, strips comments before collecting code tokens, collects both
        # refusal idioms, and matches whole tokens.
        source = open(tool, encoding="utf-8").read()
        doc = ""
        doc_raw = ""
        try:
            doc_raw = ast.get_docstring(ast.parse(source), clean=False) or ""
            doc = doc_raw
        except SyntaxError:
            doc = ""
        try:
            # untokenize keeps the original adjacency, so `Refusal(` stays glued to its
            # literal; a plain join would break the `raise Refusal("TOKEN:` pattern.
            code_text = tokenize.untokenize(
                [tok for tok in tokenize.generate_tokens(io.StringIO(source).readline)
                 if tok.type != tokenize.COMMENT])
        except (tokenize.TokenError, ValueError):
            code_text = "\n".join(line.split("#", 1)[0] for line in source.splitlines())
        # the docstring is itself a STRING token in code_text: remove it, or a doc-only
        # phantom class would "exist" in code by being quoted in the documentation.
        if doc_raw:
            code_text = code_text.replace(doc_raw, "", 1)
        tokens = sorted(set(re.findall(r'raise Refusal\("([A-Z0-9-]+):', code_text))
                        | set(re.findall(r'REFUSAL ([A-Z0-9-]+):', code_text)))
        missing = [t for t in tokens if not has_token(doc, t)]
        phantom = sorted(t for t in re.findall(r'\b((?:JSON|RECORD)-[A-Z0-9-]+|USAGE)\b', doc)
                         if not has_token(code_text, t))
        check("docstring-enum", not missing and not phantom,
              "missing=%r phantom=%r tokens=%r" % (missing, phantom, tokens), results)

        # json-written-regular
        root, path, rec = fleet(scratch, "regular")
        target = os.path.join(scratch, "regular-out.json")
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        parsed = None
        if os.path.isfile(target):
            try:
                parsed = json.load(open(target, encoding="utf-8"))
            except ValueError:
                parsed = None
        check("json-written-regular", (not hung) and rc == 0 and parsed is not None
              and parsed["summary"]["record_repos"] == 1,
              "rc=%r parsed=%r" % (rc, bool(parsed)), results)

        # json-inside-tree
        root, path, rec = fleet(scratch, "inside")
        target = os.path.join(path, "alpha", "out.json")
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        check("json-inside-tree", (not hung) and rc == 2 and "JSON-INSIDE-MEASURED-TREE" in out,
              "rc=%r out=%r" % (rc, out.splitlines()[:2]), results)

        # json-hardlinked
        root, path, rec = fleet(scratch, "hardlink")
        victim = os.path.join(scratch, "hardlink-victim")
        write(victim, "x\n")
        link = os.path.join(scratch, "hardlink-out")
        os.link(victim, link)
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", link])
        check("json-hardlinked", (not hung) and rc == 2 and "JSON-HARDLINKED" in out,
              "rc=%r out=%r" % (rc, out.splitlines()[:2]), results)

        # json-symlink-resolved: the documented contract is "written on the resolved
        # path", so a leaf symlink is followed by realpath and the JSON lands at the
        # resolved target -- the case asserts that contract, not a refusal.
        root, path, rec = fleet(scratch, "symlink")
        target = os.path.join(scratch, "symlink-out")
        resolved = os.path.join(scratch, "symlink-target.json")
        os.symlink(resolved, target)
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        check("json-symlink-resolved", (not hung) and rc == 0 and os.path.isfile(resolved)
              and not os.path.islink(resolved),
              "rc=%r resolved_written=%s" % (rc, os.path.isfile(resolved)), results)

        # json-directory
        root, path, rec = fleet(scratch, "directory")
        target = os.path.join(scratch, "a-directory")
        os.makedirs(target)
        rc, out, elapsed, hung = invoke(tool, path, rec, ["--json", target])
        check("json-directory", (not hung) and rc == 2 and "JSON-NOT-REGULAR" in out,
              "rc=%r out=%r" % (rc, out.splitlines()[:2]), results)

        # record-outside-root
        root, path, rec = fleet(scratch, "outside")
        write(rec, "REPO\t../escaped\tregs=1\tprunable=0\nTOTAL\trepos=1\tregs=1\tprunable=0\n")
        rc, out, elapsed, hung = invoke(tool, path, rec, [])
        check("record-outside-root", (not hung) and rc == 2 and "RECORD-OUTSIDE-ROOT" in out,
              "rc=%r out=%r" % (rc, out.splitlines()[:2]), results)

        # summary-still-exact
        root, path, rec = fleet(scratch, "summary")
        rc, out, elapsed, hung = invoke(tool, path, rec, [])
        summary = [l for l in out.splitlines() if l.startswith("SUMMARY")]
        check("summary-still-exact", (not hung) and rc == 0 and summary
              and "record_repos=1" in summary[0] and "live_repos=1" in summary[0],
              "rc=%r summary=%r" % (rc, summary[:1]), results)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return results


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--tool")
    ap.add_argument("--base-tool")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tool = args.tool or os.path.join(lane_root, "tools", "souji-worktree-drift.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    results = run_cases(tool, work)
    for name, ok, detail in results:
        print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " " + detail))
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    line = "SUMMARY cases=%d pass=%d fail=%d" % (len(results), passed, failed)
    if args.base_tool:
        base = run_cases(args.base_tool, work)
        base_fail = sum(1 for _, ok, _ in base if not ok)
        for name, ok, detail in base:
            if not ok:
                print("base-%s=FAIL%s" % (name, " " + detail))
        # r38 A3 (wave-1 seat W1CritC2): base_fail alone does not say whether the base failed
        # behaviourally or only on a class name. These three cases are behavioural by
        # construction (a hang, a destroyed input, a missing documentation token); the other
        # base failures at ca4369a are class-name differences on behaviour the base already had.
        behavioural = {"fifo-json-refused", "record-alias-refused", "docstring-enum"}
        b_fail = sorted(name for name, ok, _ in base if not ok and name in behavioural)
        print("BASE-BEHAVIORAL failed=%d cases=%s" % (len(b_fail), ",".join(b_fail)))
        line += " base_cases=%d base_fail=%d behavioral_fail=%d" % (len(base), base_fail, len(b_fail))
    print(line)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
