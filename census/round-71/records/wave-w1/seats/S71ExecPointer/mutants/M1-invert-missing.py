#!/usr/bin/env python3
"""souji-pointer-check.py — do the repo-relative paths a lesson or prereg cites exist at a revision?

Round 70 (lesson fix for r69 routed D1 and M14: cited evidence under the gitignored .ufo/waves/ tree
and prereg pointers to files that never existed). Reads each FILE from the revision (not the
worktree), extracts every token that starts with census/, corpus/, tests/, .ufo/ or tools/souji-
(bare tools/<x> tokens are fixture-internal paths in this lane's prose and are not checked) and
checks `git cat-file -e <rev>:<path>` (files and directories both count). Tokens starting with
probe/, probes/, records/, controls/ or battery/ are resolved against census/round-N/ when the file
is census/round-N/... or corpus/lessons/round-N[-*].md, and are counted as skipped elsewhere.
Tokens holding a placeholder (`<`, `*`, `{`, `$`, `…`, `round-N`) are skipped. A token immediately
followed by `(dead` (after an optional closing backtick) is a DECLARED-dead mention: it counts as
dead_declared when the path is absent and as MISSTATED-DEAD (a missing finding) when it exists.
  SUMMARY files=<n> checked=<n> missing=<n> skipped=<n> dead_declared=<n>
  EXIT=0 iff missing=0; 1 iff missing>0; 2 = could not evaluate

Code spans are NOT excluded by the token grammar: a backticked path is counted like any other
token (the grammar excludes only tokens preceded by [A-Za-z0-9_./-] and truncates the token at
whitespace, backtick, quotes, brackets, `|`, `,`, `;`). --selftest freezes that behaviour.

Read-only over the checked repo; stdlib only. --selftest writes only under --work (a throwaway git
fixture, removed after the run except with --keep).

Usage: python3 -B tools/souji-pointer-check.py --root LANE --rev FULL40 FILE [FILE...]
       python3 -B tools/souji-pointer-check.py --selftest --work DIR [--keep]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOKEN = re.compile(r"(?<![A-Za-z0-9_./-])((?:census|corpus|tests|\.ufo)/[^\s`'\"()\[\]|,;]+"
                   r"|tools/souji-[^\s`'\"()\[\]|,;]+"
                   r"|(?:probe|probes|records|controls|battery)/[^\s`'\"()\[\]|,;]+)")
LOCAL_PREFIXES = ("probe/", "probes/", "records/", "controls/", "battery/")
ROUND_OF = re.compile(r"^(?:census/round-([0-9]+)/|corpus/lessons/round-([0-9]+)(?:-[^/]*)?\.md$)")
PLACEHOLDER = ("<", "*", "{", "$", "…", "round-N")
DEAD_MARK = re.compile(r"^`?\s*\(dead\b")

GIT_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, env=GIT_ENV)


def check(root, rev, files, out=sys.stdout, err=sys.stderr):
    if not re.fullmatch(r"[0-9a-f]{40}", rev):
        print("POINTER-CHECK-FATAL: --rev must be full 40-hex", file=err)
        print("EXIT=2", file=out)
        return 2
    checked = missing = skipped = dead_declared = 0
    for rel in files:
        r = git(root, "show", f"{rev}:{rel}")
        if r.returncode != 0:
            print(f"POINTER-CHECK-FATAL: {rel} not readable at {rev}", file=err)
            print("EXIT=2", file=out)
            return 2
        seen = set()
        for lineno, line in enumerate(r.stdout.decode("utf-8", "replace").splitlines(), 1):
            for m in TOKEN.finditer(line):
                path = re.sub(r":[0-9][0-9,\-]*$", "", m.group(1).rstrip(".:/")).rstrip("/")
                if path.startswith(LOCAL_PREFIXES):
                    rm = ROUND_OF.match(rel)
                    if not rm:
                        skipped += 1
                        continue
                    path = f"census/round-{rm.group(1) or rm.group(2)}/{path}"
                if any(p in path for p in PLACEHOLDER):
                    skipped += 1
                    continue
                if (path, lineno) in seen:
                    continue
                seen.add((path, lineno))
                checked += 1
                exists = git(root, "cat-file", "-e", f"{rev}:{path}").returncode == 0
                if DEAD_MARK.match(line[m.end():]):
                    if exists:
                        missing += 1
                        print(f"MISSTATED-DEAD {rel}:{lineno} {path}")
                    else:
                        dead_declared += 1
                elif exists:
                    missing += 1
                    print(f"MISSING {rel}:{lineno} {path}")
    print(f"SUMMARY files={len(files)} checked={checked} missing={missing} skipped={skipped} "
          f"dead_declared={dead_declared}")
    rc = 0 if missing == 0 else 1
    print(f"EXIT={rc}")
    return rc


def _git_fixture(root, *args):
    r = subprocess.run(["git", "-C", root, *args], capture_output=True, env=GIT_ENV)
    if r.returncode != 0:
        raise RuntimeError(f"fixture git {' '.join(args)} failed: "
                           f"{r.stderr.decode('utf-8', 'replace').strip()}")
    return r


def _make_repo(work):
    """Throwaway fixture repo under *work*, per the round-71 fixture-repo rule."""
    d = tempfile.mkdtemp(prefix="ptr-fixture-", dir=work)
    if not d or not os.path.isdir(d):
        raise RuntimeError(f"fixture dir not created under {work!r}")
    _git_fixture(d, "init", "-q")
    top = _git_fixture(d, "rev-parse", "--show-toplevel").stdout.decode().strip()
    if os.path.realpath(top) != os.path.realpath(d):
        raise RuntimeError(f"fixture toplevel {top!r} != {d!r}")
    for rel, text in FIXTURE_FILES.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    _git_fixture(d, "add", "-A")
    _git_fixture(d, "-c", "user.name=pointer-selftest",
                 "-c", "user.email=pointer-selftest@example.invalid",
                 "commit", "-q", "-m", "pointer-check selftest fixture")
    rev = _git_fixture(d, "rev-parse", "HEAD").stdout.decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}", rev):
        raise RuntimeError(f"fixture HEAD not 40-hex: {rev!r}")
    return d, rev


FIXTURE_FILES = {
    # ref: existing path; missingpath: absent path; ref2: second existing path in a code span.
    "corpus/lessons/round-99.md": (
        "Mixed fixture: `census/round-99/records/existing.txt`,\n"
        "`census/round-99/records/missing.txt`, and `corpus/knowledge/in-span.md`.\n"
    ),
    "corpus/lessons/round-98.md": (
        "Clean fixture: `census/round-99/records/existing.txt` and\n"
        "`corpus/knowledge/in-span.md` only.\n"
    ),
    "census/round-99/records/existing.txt": "existing\n",
    "corpus/knowledge/in-span.md": "# in span\n",
}

MIXED = "corpus/lessons/round-99.md"
CLEAN = "corpus/lessons/round-98.md"


def run_selftest(work, keep=False):
    if not os.path.isdir(work):
        print(f"POINTER-CHECK-FATAL: --work must be an existing directory: {work}",
              file=sys.stderr)
        print("SELFTEST cases=0 pass=0 fail=1")
        return 1
    try:
        repo, rev = _make_repo(work)
    except Exception as exc:  # noqa: BLE001 - selftest must report, not traceback
        print(f"SELFTEST fixture FATAL: {exc}", file=sys.stderr)
        print("SELFTEST cases=0 pass=0 fail=1")
        return 1

    def run(args):
        return subprocess.run([sys.executable, "-B", os.path.realpath(__file__), *args],
                              capture_output=True, cwd=work)

    def summary(proc):
        out = proc.stdout.decode("utf-8", "replace")
        line = next((ln for ln in out.splitlines() if ln.startswith("SUMMARY ")), "")
        ex = next((ln for ln in out.splitlines() if ln.startswith("EXIT=")), "")
        return out, line, ex

    cases = passed = failed = 0

    def case(name, ok, detail=""):
        nonlocal cases, passed, failed
        cases += 1
        if ok:
            passed += 1
            print(f"CASE {name} PASS")
        else:
            failed += 1
            print(f"CASE {name} FAIL {detail}".rstrip())

    # Case 1: one existing + one missing + a code-span path; missing=1, EXIT=1, rc=1.
    p = run(["--root", repo, "--rev", rev, MIXED])
    out, summ, ex = summary(p)
    want = "files=1 checked=3 missing=1 skipped=0 dead_declared=0"
    case("missing_path_detected",
         p.returncode == 1 and ex == "EXIT=1" and want in summ
         and any(ln.startswith("MISSING ") and ln.endswith(
             "census/round-99/records/missing.txt") for ln in out.splitlines()),
         f"rc={p.returncode} {ex} [{summ}]")

    # Case 2: the token grammar does not exclude code spans; both backticked paths are checked
    # (3 checked above, not 2). This freezes current behaviour, it does not change it.
    case("code_span_counted", "checked=3" in summ,
         f"expected checked=3 (backticks are ordinary delimiters), got [{summ}]")

    # Case 3: existing-only file -> missing=0, EXIT=0, rc=0.
    p = run(["--root", repo, "--rev", rev, CLEAN])
    out, summ, ex = summary(p)
    want = "files=1 checked=2 missing=0 skipped=0 dead_declared=0"
    case("clean_file_exit0", p.returncode == 0 and ex == "EXIT=0" and want in summ,
         f"rc={p.returncode} {ex} [{summ}]")

    # Case 4: a non-40-hex --rev is refused with EXIT=2/rc=2 and no SUMMARY.
    p = run(["--root", repo, "--rev", "abc123", CLEAN])
    out, summ, ex = summary(p)
    case("bad_rev_exit2", p.returncode == 2 and ex == "EXIT=2" and not summ,
         f"rc={p.returncode} {ex} [{summ}]")

    if not keep:
        shutil.rmtree(repo, ignore_errors=True)
    print(f"SELFTEST cases={cases} pass={passed} fail={failed}")
    return 0 if failed == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(prog="souji-pointer-check.py")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--work")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--root")
    ap.add_argument("--rev")
    ap.add_argument("files", nargs="*")
    ns = ap.parse_args(argv)
    if ns.selftest:
        if not ns.work:
            ap.error("--selftest requires --work DIR")
        return run_selftest(ns.work, keep=ns.keep)
    if not ns.root or ns.rev is None or not ns.files:
        ap.error("--root, --rev and at least one FILE are required (or use --selftest)")
    return check(ns.root, ns.rev, ns.files)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
