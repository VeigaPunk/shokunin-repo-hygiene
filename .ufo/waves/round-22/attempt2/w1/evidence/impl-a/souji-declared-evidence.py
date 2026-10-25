#!/usr/bin/env python3
"""souji-declared-evidence.py — declared-evidence calibration audit (souji r22 attempt 2, C1).

Candidate implementation A.  Frozen contract: .ufo/waves/round-22/attempt2/
preregistration.txt, claim C1.  Reads a self-assessment file at a committed
revision and re-derives its machine-checkable assertions from the same
revision's bytes:

  class A — a backticked repo-relative path ending .py/.sh/.json/.tsv/.md/.txt,
            optionally suffixed :<line>, optionally a glob (*), must be present
            among the tracked files at --rev (globs must match >= 1 tracked file).
  class B — a bare hex token of length 7..40 in a cell that also names a
            revision context (commit/rev/revision/measured/at, or a
            census/round-<N>/ path) must satisfy `git cat-file -e <tok>^{commit}`.
  class C — a 64-hex token in a cell carrying exactly one backticked path must
            equal sha256 of that path's bytes at --rev.

Counts line (one line, exact):
  assertions=<N> resolved=<R> skipped=<S> mismatches=<M>
Exit 0 iff M == 0, 1 otherwise, 2 on an unusable invocation.

Read-only.  The audit path only runs `git cat-file`, `git ls-tree` and
`git show` plus hashlib.sha256; nothing under --root is written.  Scratch, when
--selftest is given, is a single mktemp directory under /var/tmp (never /tmp)
that the process removes itself in a finally block.  --selftest is also the
only place that runs repo-building git verbs (init/add/commit), and only inside
that disposable directory, never against --root.
"""
import argparse
import fnmatch
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

CLASS_EXTS = ("py", "sh", "json", "tsv", "md", "txt")
EXT_RE = "(?:" + "|".join(CLASS_EXTS) + ")"
PATH_RE = re.compile(r"[A-Za-z0-9_.][A-Za-z0-9_./-]*\.%s" % EXT_RE)
GLOB_RE = re.compile(r"[A-Za-z0-9_.*][A-Za-z0-9_./*-]*\.%s" % EXT_RE)
LINE_SUFFIX_RE = re.compile(r":(\d+)$")
HEX_TOKEN_RE = re.compile(r"[0-9a-f]{7,40}|[0-9a-f]{64}")
HEX_ANY_RE = re.compile(r"[0-9a-f]{7,}")
HEX_RUN_RE = re.compile(r"[0-9a-f]+")
SPAN_RE = re.compile(r"`([^`\n]+)`")
CONTEXT_RE = re.compile(r"\b(?:commit|commits|rev|revision|revisions|measured|at)\b", re.I)
CENSUS_ROUND_RE = re.compile(r"census/round-\d+/")
# A hex run touching one of these is embedded in an identifier or a path.
IDENT_CHARS = set("abcdefghijklmnopqrstuvwxyz"
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                  "0123456789_.-")

SKIP_REASONS = {
    "span-empty": "empty backticked span",
    "span-command-or-prose": "span is a command or prose phrase, not a bare path",
    "span-absolute-or-home": "absolute or home-relative path; class A requires repo-relative",
    "span-composite": "composite or annotated span outside frozen class A",
    "span-glob-not-clean": "glob span is not a clean repo-relative path",
    "span-not-path-or-hex": "span is not a path with a class extension, a glob, or a hex token",
    "hex-run-embedded": "hex-shaped run embedded in an identifier or path (not bare)",
    "hex-run-length": "hex run length is neither 7..40 (class B) nor 64 (class C)",
    "hex64-without-single-path": "64-hex token with %d backticked path(s) in the same cell "
                                 "(class C requires exactly 1)",
    "hex-no-revision-context": "bare hex token with no revision context in the same cell",
}


class Repo:
    """Read-only view of a git repository: cat-file, ls-tree, show only."""

    def __init__(self, root):
        self.root = os.path.abspath(root)
        self._revs = {}
        self._trees = {}
        self._tree_sets = {}
        self._blobs = {}

    def _git(self, *args):
        cmd = ["git", "--no-optional-locks", "-c", "maintenance.auto=false",
               "-C", self.root] + list(args)
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return res.returncode, res.stdout

    def rev_ok(self, tok):
        if tok not in self._revs:
            rc, _ = self._git("cat-file", "-e", tok + "^{commit}")
            self._revs[tok] = rc == 0
        return self._revs[tok]

    def tracked(self, rev):
        if rev not in self._trees:
            rc, out = self._git("ls-tree", "-r", "--name-only", rev)
            self._trees[rev] = ([ln for ln in out.decode("utf-8", "replace").splitlines() if ln]
                                if rc == 0 else [])
        return self._trees[rev]

    def tracked_set(self, rev):
        if rev not in self._tree_sets:
            self._tree_sets[rev] = frozenset(self.tracked(rev))
        return self._tree_sets[rev]

    def blob(self, rev, path):
        key = (rev, path)
        if key not in self._blobs:
            rc, out = self._git("show", "%s:%s" % (rev, path))
            self._blobs[key] = out if rc == 0 else None
        return self._blobs[key]

    def read_declaration(self, rev, relfile):
        data = self.blob(rev, relfile)
        return None if data is None else data.decode("utf-8", "replace")


def repo_relative(core):
    if not core or core.startswith(("/", "~")):
        return False
    return all(part not in ("", ".", "..") for part in core.split("/"))


def classify_span(raw):
    """Classify one backticked span as an assertion or an excluded token."""
    s = raw.strip()
    if not s:
        return {"kind": "skip", "token": raw, "reason": "span-empty"}
    core = s
    line_no = None
    m = LINE_SUFFIX_RE.search(s)
    if m:
        cand = s[:m.start()]
        if PATH_RE.fullmatch(cand) or GLOB_RE.fullmatch(cand):
            core = cand
            line_no = int(m.group(1))
    if "*" in core:
        if GLOB_RE.fullmatch(core) and repo_relative(core):
            return {"kind": "A", "token": s, "glob": core, "line": line_no}
        return {"kind": "skip", "token": s, "reason": "span-glob-not-clean"}
    if PATH_RE.fullmatch(core) and repo_relative(core):
        return {"kind": "A", "token": s, "path": core, "line": line_no}
    if HEX_ANY_RE.fullmatch(s):
        return {"kind": "hex", "token": s}
    if any(ch.isspace() for ch in s):
        return {"kind": "skip", "token": s, "reason": "span-command-or-prose"}
    if s.startswith(("/", "~")):
        return {"kind": "skip", "token": s, "reason": "span-absolute-or-home"}
    if ":" in s:
        return {"kind": "skip", "token": s, "reason": "span-composite"}
    return {"kind": "skip", "token": s, "reason": "span-not-path-or-hex"}


def cells_of(line):
    """Split a line into cells, keeping a backticked span atomic.

    A table row is a line whose first non-space character is `|`; each cell is
    the range between two pipe delimiters.  Every other line is one context
    unit, so prose evidence is enumerated instead of being silently invisible.
    A span may itself contain `|` (markdown escapes it as \\|), so pipe splitting
    never happens inside backticks.  Returns a list of cells, each a list of
    (kind, start, end) pieces where kind is "text" or "span".
    """
    row = line.lstrip().startswith("|")
    cells = [[]]
    i = 0
    while i < len(line):
        if line[i] == "`":
            j = line.find("`", i + 1)
            if j < 0:
                cells[-1].append(("text", i, len(line)))
                break
            cells[-1].append(("span", i + 1, j))
            i = j + 1
            continue
        if line[i] == "|" and row:
            cells.append([])
            i += 1
            continue
        j = i
        while j < len(line) and line[j] != "`" and not (row and line[j] == "|"):
            j += 1
        cells[-1].append(("text", i, j))
        i = j
    return cells


def scan(text):
    """Return (assertions, skipped) in document order."""
    assertions, skipped = [], []
    for lineno, line in enumerate(text.splitlines(), 1):
        for pieces in cells_of(line):
            spans = [classify_span(line[s:e]) for kind, s, e in pieces if kind == "span"]
            cell = "".join(line[s:e] if kind == "text" else line[s - 1:e + 1]
                           for kind, s, e in pieces)
            path_spans = [sp for sp in spans if sp["kind"] == "A" and "path" in sp]
            for sp in spans:
                if sp["kind"] == "A":
                    assertions.append({"line": lineno, "token": sp["token"], "cls": "A",
                                       "rev": None, "path": sp.get("path"),
                                       "glob": sp.get("glob"), "suffix": sp.get("line")})
                elif sp["kind"] == "hex":
                    pass  # decided by the run scan, so it is counted exactly once
                else:
                    skipped.append({"line": lineno, "token": sp["token"], "cls": "-",
                                    "reason": sp["reason"]})
            ctx = bool(CONTEXT_RE.search(cell) or CENSUS_ROUND_RE.search(cell))
            for m in HEX_RUN_RE.finditer(cell):
                tok = m.group(0)
                if len(tok) < 7:
                    continue
                left = cell[m.start() - 1] if m.start() else ""
                right = cell[m.end()] if m.end() < len(cell) else ""
                if (left and left in IDENT_CHARS) or (right and right in IDENT_CHARS):
                    skipped.append({"line": lineno, "token": tok, "cls": "-",
                                    "reason": "hex-run-embedded"})
                    continue
                if len(tok) == 64:
                    if len(path_spans) == 1:
                        assertions.append({"line": lineno, "token": tok, "cls": "C",
                                           "rev": None, "path": path_spans[0]["path"],
                                           "glob": None, "suffix": None})
                    else:
                        skipped.append({"line": lineno, "token": tok, "cls": "-",
                                        "reason": "hex64-without-single-path",
                                        "arg": len(path_spans)})
                elif 7 <= len(tok) <= 40:
                    if ctx:
                        assertions.append({"line": lineno, "token": tok, "cls": "B",
                                           "rev": None, "path": None, "glob": None,
                                           "suffix": None})
                    else:
                        skipped.append({"line": lineno, "token": tok, "cls": "-",
                                        "reason": "hex-no-revision-context"})
                else:
                    skipped.append({"line": lineno, "token": tok, "cls": "-",
                                    "reason": "hex-run-length"})
    return assertions, skipped


def evaluate(repo, rev, a):
    if a["cls"] == "A":
        if a["glob"] is not None:
            hits = [p for p in repo.tracked(rev) if fnmatch.fnmatchcase(p, a["glob"])]
            if hits:
                return "resolved", "glob matches %d tracked file(s) at %s" % (len(hits), rev)
            return "mismatch", "glob matches no tracked file at %s" % rev
        if a["path"] in repo.tracked_set(rev):
            return "resolved", "present at %s" % rev
        return "mismatch", "path absent at %s" % rev
    if a["cls"] == "B":
        if repo.rev_ok(a["token"]):
            return "resolved", "resolves as a commit"
        return "mismatch", "does not resolve with cat-file -e <tok>^{commit}"
    if a["cls"] == "C":
        data = repo.blob(rev, a["path"])
        if data is None:
            return "mismatch", "digest target `%s` absent at %s" % (a["path"], rev)
        got = hashlib.sha256(data).hexdigest()
        if got == a["token"]:
            return "resolved", "sha256 matches `%s` at %s" % (a["path"], rev)
        return "mismatch", "sha256 of `%s` at %s is %s" % (a["path"], rev, got)
    return "skipped", "unknown class"


def run(root, decl_file, rev, fmt, out=sys.stdout):
    repo = Repo(root)
    relfile = decl_file[2:] if decl_file.startswith("./") else decl_file
    if os.path.isabs(relfile):
        sys.stderr.write("error: --file must be repo-relative, not absolute: %s\n" % decl_file)
        return 2
    if not repo.rev_ok(rev):
        sys.stderr.write("error: revision does not resolve as a commit: %s\n" % rev)
        return 2
    text = repo.read_declaration(rev, relfile)
    if text is None:
        sys.stderr.write("error: declaration file not present at %s: %s\n" % (rev, relfile))
        return 2
    assertions, skipped = scan(text)
    resolved = mismatches = 0
    rows = []
    for a in assertions:
        verdict, detail = evaluate(repo, rev, a)
        if verdict == "resolved":
            resolved += 1
        else:
            mismatches += 1
        rows.append((a["line"], a["token"], a["cls"], verdict, detail))
    for s in skipped:
        reason = s["reason"]
        if s.get("arg") is not None:
            detail = reason % s["arg"]
        else:
            detail = SKIP_REASONS.get(reason, reason)
        rows.append((s["line"], s["token"], s["cls"], "skipped", detail))
    if fmt == "tsv":
        out.write("#line\ttoken\tclass\tverdict\tdetail\n")
        for row in rows:
            out.write("%d\t%s\t%s\t%s\t%s\n" % row)
    out.write("assertions=%d resolved=%d skipped=%d mismatches=%d\n"
              % (len(assertions), resolved, len(skipped), mismatches))
    return 0 if mismatches == 0 else 1


# ---------------------------------------------------------------------------
# selftest — the five frozen fixtures plus the always-zero control
# ---------------------------------------------------------------------------

def _wait_git(repo, env, *args):
    cmd = ["git", "-C", repo, "-c", "maintenance.auto=false",
           "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false"] + list(args)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if res.returncode != 0:
        raise RuntimeError("fixture git %s failed: %s"
                           % (" ".join(args), res.stderr.decode("utf-8", "replace")))
    return res.stdout.decode("utf-8", "replace").strip()


def _fixture_repo(base):
    repo = os.path.join(base, "repo")
    os.makedirs(os.path.join(repo, "tools"))
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "souji", "GIT_AUTHOR_EMAIL": "souji@example.invalid",
        "GIT_COMMITTER_NAME": "souji", "GIT_COMMITTER_EMAIL": "souji@example.invalid",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0", "HOME": base,
    })
    _wait_git(repo, env, "init", "-q", "-b", "main")
    with open(os.path.join(repo, "tools", "present.sh"), "w", encoding="utf-8") as fh:
        fh.write("#!/bin/sh\nexit 0\n")
    with open(os.path.join(repo, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("fixture repository\n")
    with open(os.path.join(repo, "revonly.md"), "w", encoding="utf-8") as fh:
        fh.write("| artifact | note |\n|---|---|\n| `later.md` | checked at the earlier revision |\n")
    _wait_git(repo, env, "add", "-A")
    _wait_git(repo, env, "commit", "-q", "-m", "one")
    early = _wait_git(repo, env, "rev-parse", "HEAD")
    with open(os.path.join(repo, "later.md"), "w", encoding="utf-8") as fh:
        fh.write("later\n")
    _wait_git(repo, env, "add", "-A")
    _wait_git(repo, env, "commit", "-q", "-m", "two")
    mid = _wait_git(repo, env, "rev-parse", "HEAD")
    return repo, early, mid, env


def _fixture_counts(repo, decl, rev):
    import io
    buf = io.StringIO()
    rc = run(repo, decl, rev, "counts", buf)
    text = buf.getvalue().strip()
    line = text.splitlines()[-1] if text else "no counts line (exit %d)" % rc
    fields = {}
    for kv in line.split():
        if "=" in kv:
            key, val = kv.split("=", 1)
            fields[key] = val
    try:
        mism = int(fields.get("mismatches", "-1"))
    except ValueError:
        mism = -1
    return rc, line, mism


def selftest(out=sys.stdout):
    base = tempfile.mkdtemp(prefix="souji-declared-evidence-", dir="/var/tmp")
    checks = []
    try:
        repo, early, mid, env = _fixture_repo(base)
        with open(os.path.join(repo, "tools", "present.sh"), "rb") as fh:
            good_sha = hashlib.sha256(fh.read()).hexdigest()

        def put(name, body):
            path = os.path.join(repo, name)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(body)
            return name

        # The declaration files are committed in a third commit and name the
        # second commit (mid), which resolves and holds every class-A target.
        put("good.md", "| artifact | note |\n|---|---|\n"
            "| `tools/present.sh` | measured commit %s |\n"
            "| sha256 `%s` on `tools/present.sh` | measured commit %s |\n"
            % (mid[:7], good_sha, mid[:7]))
        put("absent.md", "| artifact | note |\n|---|---|\n"
            "| `tools/absent.sh` | measured commit %s |\n" % mid[:7])
        put("dangling.md", "| artifact | note |\n|---|---|\n"
            "| `tools/present.sh` | measured commit %s |\n"
            % ("deadbeef" * 5))
        put("digest.md", "| artifact | note |\n|---|---|\n"
            "| sha256 `%s` on `tools/present.sh` | measured commit %s |\n"
            % ("0" * 64, mid[:7]))
        _wait_git(repo, env, "add", "-A")
        _wait_git(repo, env, "commit", "-q", "-m", "fixtures")
        late = _wait_git(repo, env, "rev-parse", "HEAD")

        rc, line, mism = _fixture_counts(repo, "good.md", late)
        checks.append(("1 all-good declaration -> 0 mismatches",
                       rc == 0 and mism == 0, line))
        rc, line, mism = _fixture_counts(repo, "absent.md", late)
        checks.append(("2 nonexistent path -> >=1", rc == 1 and mism >= 1, line))
        rc, line, mism = _fixture_counts(repo, "dangling.md", late)
        checks.append(("3 dangling revision -> >=1", rc == 1 and mism >= 1, line))
        rc, line, mism = _fixture_counts(repo, "digest.md", late)
        checks.append(("4 wrong digest -> >=1", rc == 1 and mism >= 1, line))
        rc, line, mism = _fixture_counts(repo, "revonly.md", early)
        checks.append(("5 path present only at a different revision -> >=1",
                       rc == 1 and mism >= 1, line))

        # The cheapest do-nothing control prints all zeros without reading a
        # byte; it cannot satisfy the >=1 mismatch that fixtures 2..5 require,
        # so the same fixture set rejects it.
        control_rejections = 0
        for decl, rev in (("absent.md", late), ("dangling.md", late),
                          ("digest.md", late), ("revonly.md", early)):
            _rc, _line, required = _fixture_counts(repo, decl, rev)
            if required >= 1:
                control_rejections += 1
        rejected = control_rejections == 4
        checks.append(("control always-zero -> FALSE-GREEN-REJECTED", rejected,
                       "FALSE-GREEN-REJECTED" if rejected
                       else "control would pass %d fixture(s)" % (4 - control_rejections)))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    ok = sum(1 for _n, good, _d in checks if good)
    for name, good, detail in checks:
        out.write("%s %s [%s]\n" % ("PASS" if good else "FAIL", name, detail))
    out.write("selftest=%d/%d\n" % (ok, len(checks)))
    if any(n.startswith("control") and g for n, g, _d in checks):
        out.write("control=FALSE-GREEN-REJECTED\n")
    return 0 if ok == len(checks) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="declared-evidence calibration audit (souji round 22, claim C1)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--file")
    ap.add_argument("--rev")
    ap.add_argument("--format", choices=("counts", "tsv"), default="counts")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.file or not args.rev:
        ap.error("--file and --rev are required unless --selftest is given")
    return run(args.root, args.file, args.rev, args.format)


if __name__ == "__main__":
    sys.exit(main())
