#!/usr/bin/env python3
"""souji-declared-evidence.py — declared-evidence calibration audit (round 22, C1).

Reads a self-assessment file (default SCORECARD.md) at a committed revision and
re-derives its machine-checkable assertions from the same revision:

  class A — a backticked repo-relative path (optional :<line>, optional '*'
            glob) must exist in the tree at --rev, or at the revision named in
            the same span as '<rev>:<path>'.
  class B — a bare 7..40-char hex token in a cell that names a revision context
            (commit/commits/rev/revision/measured/at, or a census/round-<N>/
            path) must resolve with `git cat-file -e <tok>^{commit}`.
  class C — a 64-char hex digest in the same cell as exactly one backticked
            path must equal sha256 of that path's bytes at --rev.

Counts line: assertions=<N> resolved=<R> skipped=<S> mismatches=<M>
Exit 0 iff M == 0.  Read-only: git plumbing only, scratch under /var/tmp.

Frozen contract: .ufo/waves/round-22/attempt2/preregistration.txt (C1).
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile

EXT = r"(?:py|sh|json|tsv|md|txt)"
PATH_RE = re.compile(r"^[A-Za-z0-9_.][A-Za-z0-9_./-]*\.%s$" % EXT)
GLOB_RE = re.compile(r"^[A-Za-z0-9_.*][A-Za-z0-9_./*-]*\.%s$" % EXT)
REV_AT_PATH_RE = re.compile(r"^([0-9a-f]{7,40}):(\S+)$")
HEX_B_RE = re.compile(r"(?<![A-Za-z0-9_.-])([0-9a-f]{7,40})(?![A-Za-z0-9_.-])")
HEX64_RE = re.compile(r"(?<![A-Za-z0-9_.-])([0-9a-f]{64})(?![A-Za-z0-9_.-])")
SPAN_RE = re.compile(r"`([^`]+)`")
LINE_SUFFIX_RE = re.compile(r":(\d+)$")
REV_WORDS = re.compile(r"\b(commit|commits|rev|revision|revisions|measured|at)\b", re.I)
CENSUS_ROUND_RE = re.compile(r"census/round-\d+/")


class Repo:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        top = self.git("rev-parse", "--show-toplevel")
        if not top or os.path.realpath(top.decode().strip()) != os.path.realpath(self.root):
            raise SystemExit("not the root of a git repository: %s" % root)
        self._tree_cache: dict[str, list[str]] = {}

    def git(self, *args: str):
        res = subprocess.run(
            ["git", "-C", self.root, "-c", "maintenance.auto=false"] + list(args),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        return res.stdout if res.returncode == 0 else None

    def rev_ok(self, rev: str) -> bool:
        return self.git("cat-file", "-e", rev + "^{commit}") is not None

    def tracked(self, rev: str) -> list[str]:
        if rev not in self._tree_cache:
            out = self.git("ls-tree", "-r", "--name-only", rev) or b""
            self._tree_cache[rev] = [ln for ln in out.decode("utf-8", "replace").splitlines() if ln]
        return self._tree_cache[rev]

    def blob(self, rev: str, path: str):
        return self.git("show", "%s:%s" % (rev, path))

    def read_declaration(self, rev: str, relfile: str) -> str:
        """From the revision when tracked there, else from the filesystem."""
        if relfile in self.tracked(rev):
            data = self.blob(rev, relfile)
            if data is not None:
                return data.decode("utf-8", "replace")
        path = relfile if os.path.isabs(relfile) else os.path.join(self.root, relfile)
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()

    def path_present(self, rev: str, path: str) -> bool:
        if path in self.tracked(rev):
            return True
        return self.blob(rev, path) is not None


def cells_of(line: str) -> list[str]:
    """Table cells when the line is a table row, else the whole line."""
    return line.split("|") if line.count("|") >= 2 else [line]


def classify(repo: Repo, rev: str, decl_file: str):
    text = repo.read_declaration(rev, decl_file)
    assertions: list[dict] = []
    skipped = 0

    for lineno, line in enumerate(text.splitlines(), 1):
        spans = [m.group(1) for m in SPAN_RE.finditer(line)]
        for span in spans:
            raw = span.strip()
            rev_path = REV_AT_PATH_RE.match(raw)
            if rev_path and (PATH_RE.match(rev_path.group(2)) or GLOB_RE.match(rev_path.group(2))):
                assertions.append(dict(line=lineno, token=raw, cls="A",
                                        rev=rev_path.group(1), path=rev_path.group(2)))
                continue
            token = LINE_SUFFIX_RE.sub("", raw)
            if "*" in token and GLOB_RE.match(token):
                assertions.append(dict(line=lineno, token=raw, cls="A", rev=rev, glob=token))
                continue
            if PATH_RE.match(token):
                assertions.append(dict(line=lineno, token=raw, cls="A", rev=rev, path=token))
                continue
            if re.fullmatch(r"[0-9a-f]{7,40}", raw) or re.fullmatch(r"[0-9a-f]{64}", raw):
                continue  # hex span: class B/C candidate, decided by the cell pass
            skipped += 1

        seen_hex: set[str] = set()
        for cell in cells_of(line):
            digests = set(HEX64_RE.findall(cell))
            if digests:
                path_spans = [LINE_SUFFIX_RE.sub("", s.strip()) for s in SPAN_RE.findall(cell)]
                path_spans = [p for p in path_spans if PATH_RE.match(p)]
                if len(path_spans) == 1:
                    for d in sorted(digests):
                        assertions.append(dict(line=lineno, token=d, cls="C", rev=rev, path=path_spans[0]))
                        seen_hex.add(d)
                else:
                    skipped += len(digests)
                    seen_hex |= digests
            ctx = bool(REV_WORDS.search(cell) or CENSUS_ROUND_RE.search(cell))
            for h in sorted(set(HEX_B_RE.findall(cell)) - seen_hex):
                if len(h) == 64:
                    skipped += 1
                    continue
                if not ctx:
                    skipped += 1
                    continue
                assertions.append(dict(line=lineno, token=h, cls="B", rev=rev))
                seen_hex.add(h)
    return assertions, skipped


def evaluate(repo: Repo, a: dict):
    cls = a["cls"]
    if cls == "A":
        if not repo.rev_ok(a["rev"]):
            return "mismatch:rev-unresolved", "named revision %s does not resolve" % a["rev"]
        if "glob" in a:
            hits = [f for f in repo.tracked(a["rev"]) if fnmatch.fnmatch(f, a["glob"])]
            return ("resolved", "%d match(es) at %s" % (len(hits), a["rev"])) if hits \
                else ("mismatch:path-absent", "glob matches nothing at %s" % a["rev"])
        if repo.path_present(a["rev"], a["path"]):
            return "resolved", "present at %s" % a["rev"]
        return "mismatch:path-absent", "not in tree at %s" % a["rev"]
    if cls == "B":
        if repo.rev_ok(a["token"]):
            return "resolved", "commit/object resolves"
        return "mismatch:rev-unresolved", "not a commit or object in this repository"
    if cls == "C":
        data = repo.blob(a["rev"], a["path"])
        if data is None:
            return "mismatch:path-absent", "digest target absent at %s" % a["rev"]
        got = hashlib.sha256(data).hexdigest()
        return ("resolved", "sha256 matches") if got == a["token"] else ("mismatch:digest", "sha256 is %s" % got)
    return "skipped:unknown-class", cls


def run(root_path: str, decl_file: str, rev: str, fmt: str, out=sys.stdout) -> int:
    repo = Repo(root_path)
    if not repo.rev_ok(rev):
        raise SystemExit("revision does not resolve: %s" % rev)
    assertions, skipped = classify(repo, rev, decl_file)
    resolved = mism = 0
    for a in assertions:
        observed, detail = evaluate(repo, a)
        if observed == "resolved":
            resolved += 1
        elif observed.startswith("mismatch"):
            mism += 1
        else:
            skipped += 1
        if fmt == "tsv":
            out.write("%d\t%s\t%s\t%s\t%s\n" % (a["line"], a["token"], a["cls"], observed, detail))
    out.write("assertions=%d resolved=%d skipped=%d mismatches=%d\n" % (len(assertions), resolved, skipped, mism))
    return 0 if mism == 0 else 1


# --------------------------------------------------------------------------
# selftest: the five frozen fixtures + the always-zero control, which must fail
# --------------------------------------------------------------------------

GOOD_DECL = "| cell | note |\n|---|---|\n| `tools/present.sh` | measured commit %s |\n"
ABSENT_DECL = "| cell | note |\n|---|---|\n| `tools/absent.sh` | measured commit %s |\n"
DANGLING_DECL = "| cell | note |\n|---|---|\n| `tools/present.sh` | measured commit deadbeefdeadbeefdeadbeefdeadbeefdeadbeef |\n"
REVONLY_DECL = "| cell | note |\n|---|---|\n| `later.md` | measured commit %s |\n"


def _fixture_repo(base: str):
    repo = os.path.join(base, "repo")
    os.makedirs(repo)
    env = dict(os.environ, GIT_AUTHOR_NAME="souji", GIT_AUTHOR_EMAIL="souji@shokunin.local",
               GIT_COMMITTER_NAME="souji", GIT_COMMITTER_EMAIL="souji@shokunin.local")

    def sh(*cmd):
        res = subprocess.run(cmd, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if res.returncode != 0:
            raise RuntimeError("%s: %s" % (" ".join(cmd), res.stderr.decode()))
        return res.stdout.decode()

    sh("git", "init", "-q", "-b", "main")
    os.makedirs(os.path.join(repo, "tools"))
    with open(os.path.join(repo, "tools", "present.sh"), "w") as fh:
        fh.write("#!/bin/sh\nexit 0\n")
    with open(os.path.join(repo, "README.md"), "w") as fh:
        fh.write("fixture\n")
    sh("git", "add", "README.md", "tools/present.sh")
    sh("git", "commit", "-q", "-m", "one")
    early = sh("git", "rev-parse", "HEAD").strip()
    with open(os.path.join(repo, "later.md"), "w") as fh:
        fh.write("later\n")
    sh("git", "add", "later.md")
    sh("git", "commit", "-q", "-m", "two")
    late = sh("git", "rev-parse", "HEAD").strip()
    return repo, early, late


def _write(path: str, text: str) -> str:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def _counts(decl: str, repo: str, rev: str) -> tuple[int, str]:
    buf = io.StringIO()
    rc = run(repo, decl, rev, "counts", buf)
    return rc, buf.getvalue().strip().splitlines()[-1]


def selftest(out=sys.stdout) -> int:
    checks: list[tuple[str, bool, str]] = []
    base = tempfile.mkdtemp(prefix="souji-declared-evidence-", dir="/var/tmp")
    try:
        repo, early, late = _fixture_repo(base)
        good_sha = hashlib.sha256(open(os.path.join(repo, "tools", "present.sh"), "rb").read()).hexdigest()
        fixtures = {
            "all-good": _write(os.path.join(base, "good.md"), GOOD_DECL % late[:7]),
            "absent-path": _write(os.path.join(base, "absent.md"), ABSENT_DECL % late[:7]),
            "dangling-rev": _write(os.path.join(base, "dangling.md"), DANGLING_DECL),
            "wrong-digest": _write(os.path.join(base, "digest.md"),
                                   "| c | note |\n|---|---|\n| sha256 `%s` on `tools/present.sh` | measured commit %s |\n"
                                   % ("0" * 64, late[:7])),
            "rev-only-path": _write(os.path.join(base, "revonly.md"), REVONLY_DECL % early[:7]),
        }
        rc, line = _counts(fixtures["all-good"], repo, late)
        checks.append(("fixture1 all-good -> 0", rc == 0 and line.endswith("mismatches=0"), line))
        rc, line = _counts(fixtures["absent-path"], repo, late)
        checks.append(("fixture2 absent path -> mismatch", rc == 1 and "mismatches=1" in line, line))
        rc, line = _counts(fixtures["dangling-rev"], repo, late)
        checks.append(("fixture3 dangling rev -> mismatch", rc == 1 and "mismatches=1" in line, line))
        rc, line = _counts(fixtures["wrong-digest"], repo, late)
        checks.append(("fixture4 wrong digest -> mismatch", rc == 1 and "mismatches=1" in line, line))
        rc, line = _counts(fixtures["rev-only-path"], repo, early)
        checks.append(("fixture5 path only at other rev -> mismatch", rc == 1 and "mismatches=1" in line, line))
        # digest of present.sh really equals its sha256 (positive control for class C)
        rc, line = _counts(_write(os.path.join(base, "digest-good.md"),
                                  "| c | note |\n|---|---|\n| sha256 `%s` on `tools/present.sh` | measured commit %s |\n"
                                  % (good_sha, late[:7])), repo, late)
        checks.append(("fixture6 correct digest -> resolved", rc == 0 and line.endswith("mismatches=0"), line))
        # the cheapest do-nothing control: claims zeros, reads no byte
        control = _write(os.path.join(base, "always-zero.py"),
                         "print('assertions=0 resolved=0 skipped=0 mismatches=0')\n")
        control_green = True
        for key in ("absent-path", "dangling-rev", "wrong-digest", "rev-only-path"):
            res = subprocess.run([sys.executable, control], stdout=subprocess.PIPE)
            tail = res.stdout.decode().strip()
            m = re.search(r"mismatches=(\d+)$", tail)
            control_green = control_green and bool(m) and int(m.group(1)) >= 1
        checks.append(("control always-zero -> FALSE-GREEN-REJECTED", not control_green,
                       "FALSE-GREEN-REJECTED" if not control_green else "control met the fixtures"))
        # skipped accounting stays visible
        rc, line = _counts(_write(os.path.join(base, "skipped.md"),
                                  "| c | note |\n|---|---|\n| `git status --short` | run at release |\n"), repo, late)
        checks.append(("fixture7 command span -> skipped, not asserted", "assertions=0" in line and "skipped=" in line
                       and "skipped=0 " not in line, line))
    finally:
        subprocess.run(["rm", "-rf", base], check=False)
    ok = sum(1 for _, good, _ in checks if good)
    for name, good, detail in checks:
        out.write("%s %s [%s]\n" % ("PASS" if good else "FAIL", name, detail))
    out.write("selftest=%d/%d\n" % (ok, len(checks)))
    return 0 if ok == len(checks) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="declared-evidence calibration audit (souji round 22 C1)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--file", default="SCORECARD.md")
    ap.add_argument("--rev")
    ap.add_argument("--format", choices=["counts", "tsv"], default="counts")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.rev:
        ap.error("--rev is required unless --selftest")
    return run(args.root, args.file, args.rev, args.format)


if __name__ == "__main__":
    sys.exit(main())
