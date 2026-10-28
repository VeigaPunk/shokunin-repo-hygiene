#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one runnable command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40

Reads the preregistration blob PATH at --rev through git (never the work tree), parses its
`## C<digits>` claim blocks and reports grammar and freeze findings:

  stdout  `FINDING <claim> <CLASS> <detail>` per finding (sorted), then `SUMMARY claims=<n> findings=<m>`
  exit    0 no findings; 1 findings; 2 could-not-evaluate (stderr `REFUSAL COULD-NOT-EVALUATE: ...`)

Classes: NO-CLAIMS FIELD-MISSING FIELD-EMPTY BASE-UNRESOLVED BASE-NOT-ANCESTOR COUNTER-MISSING
COUNTER-DIGEST POPULATION-MISSING POPULATION-DIGEST POPULATION-EMPTY CONTROL-MISSING CONTROL-NOT-RED
FROZEN-EDITED DISPATCH-BEFORE-FREEZE.  A prereg-wide finding carries the claim label C0.

FREEZE-REV = the oldest commit reachable from --rev whose own diff adds PATH (merges are not diffed,
renames are not followed: a rename-in is an add of the new path). Every frozen path is read at
FREEZE-REV and again at --rev. Read-only: git is run with optional locks off, replace refs ignored,
config isolated; nothing is written into --root. Python stdlib only.
"""
import argparse
import fnmatch
import hashlib
import os
import posixpath
import re
import subprocess
import sys

REV = re.compile(r"^[0-9a-f]{40}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
CLAIM = re.compile(r"^## C(\d+)")
KEY = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")
ROUND = re.compile(r"^Round:[ \t]*(\d+)[ \t]*$")
EXIT_LINE = re.compile(r"^EXIT=([+-]?\d+)$")
FILE_DIGEST = re.compile(r"^(\S+)[ \t]+sha256=(\S*)$")
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")
TIMEOUT = 300


class CouldNotEvaluate(Exception):
    pass


class Repo:
    def __init__(self, root):
        self.root = root
        self.env = {
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0",
            "GIT_NO_REPLACE_OBJECTS": "1", "GIT_PAGER": "cat",
        }

    def run(self, *args, stdin=None):
        try:
            p = subprocess.run(["git", "-C", self.root] + list(args), input=stdin,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env,
                               check=False, timeout=TIMEOUT)
        except (OSError, subprocess.SubprocessError) as exc:
            raise CouldNotEvaluate("git could not run: %s" % exc)
        return p.returncode, p.stdout

    def commit_exists(self, rev):
        rc, _ = self.run("cat-file", "-e", rev + "^{commit}")
        return rc == 0

    def blob(self, rev, path):
        """Bytes of the blob at rev:path, or None when no blob exists there."""
        path = clean_path(path)
        if path is None:
            return None
        rc, out = self.run("cat-file", "blob", "%s:%s" % (rev, path))
        return out if rc == 0 else None

    def is_ancestor(self, a, b):
        """True when a is an ancestor of b or equal to it."""
        rc, _ = self.run("merge-base", "--is-ancestor", a, b)
        if rc == 0:
            return True
        if rc == 1:
            return False
        raise CouldNotEvaluate("merge-base --is-ancestor %s %s failed (rc=%d)" % (a[:12], b[:12], rc))

    def adds(self, rev, pathspec, names=False):
        """Commits reachable from rev whose own diff adds a path under pathspec: {commit: [names]}."""
        rc, out = self.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--no-merges",
                           "--format=%x01%H", "--name-only", "-z", rev, "--", ":(literal)" + pathspec)
        if rc != 0:
            raise CouldNotEvaluate("git log failed over %s (rc=%d)" % (pathspec, rc))
        found = {}
        cur = None
        for tok in out.split(b"\0"):
            tok = tok.lstrip(b"\n")
            if tok.startswith(b"\x01"):
                cur = tok[1:].decode("ascii", "replace")
                found.setdefault(cur, [])
            elif tok and cur is not None:
                found[cur].append(tok.decode("utf-8", "replace"))
        return found

    def committer_time(self, commit):
        rc, out = self.run("show", "-s", "--format=%ct", commit)
        try:
            return int(out.strip()) if rc == 0 else 0
        except ValueError:
            return 0


def clean_path(path):
    if not path or "\0" in path or "\n" in path or path.startswith("/"):
        return None
    norm = posixpath.normpath(path)
    if norm in (".", "..") or norm.startswith("../"):
        return None
    return norm


def freeze_rev(repo, rev, path):
    """Oldest commit reachable from rev that adds path."""
    clean = clean_path(path)
    if clean is None:
        raise CouldNotEvaluate("PATH %r is not a repository-relative path" % path)
    cands = [c for c, _names in repo.adds(rev, clean).items()]
    if not cands:
        raise CouldNotEvaluate("no commit reachable from %s adds %s" % (rev[:12], path))
    if len(cands) > 1:
        # keep the minimal candidates (none has another candidate as an ancestor), then the earliest
        minimal = [c for c in cands
                   if not any(o != c and repo.is_ancestor(o, c) for o in cands)]
        cands = minimal or cands
        cands.sort(key=lambda c: (repo.committer_time(c), c))
    return cands[0]


def parse(text):
    """-> (round number or None, [(label, {key: value})])"""
    round_no = None
    claims = []
    cur = None
    for line in text.split("\n"):
        line = line.rstrip("\r")
        m = CLAIM.match(line)
        if m:
            cur = ("C" + m.group(1), {})
            claims.append(cur)
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur is None:
            if round_no is None:
                r = ROUND.match(line)
                if r:
                    round_no = r.group(1)
            continue
        k = KEY.match(line)
        if k and k.group(1) not in cur[1]:
            cur[1][k.group(1)] = k.group(2)
    return round_no, claims


def digest_spec(value):
    m = FILE_DIGEST.match(value)
    if m:
        return m.group(1), m.group(2)
    parts = value.split()
    return (parts[0] if parts else ""), ""


def check_claim(repo, label, fields, freeze, rev, out):
    def add(cls, detail):
        out.append((label, cls, detail))

    for key in KEYS:
        if key not in fields:
            add("FIELD-MISSING", key)
    for key in ("Target", "Kill"):
        if key in fields and not fields[key].strip():
            add("FIELD-EMPTY", key)

    if "Base" in fields:
        base = fields["Base"]
        if not REV.match(base) or not repo.commit_exists(base):
            add("BASE-UNRESOLVED", base or "(blank)")
        elif base == freeze or not repo.is_ancestor(base, freeze):
            add("BASE-NOT-ANCESTOR", "%s freeze=%s" % (base[:12], freeze[:12]))

    for key, miss, dig in (("Counter", "COUNTER-MISSING", "COUNTER-DIGEST"),
                           ("Population", "POPULATION-MISSING", "POPULATION-DIGEST")):
        if key not in fields:
            continue
        path, want = digest_spec(fields[key])
        data = repo.blob(freeze, path)
        if data is None:
            add(miss, path or "(blank)")
            continue
        have = hashlib.sha256(data).hexdigest()
        if not SHA.match(want) or have != want:
            add(dig, "%s stated=%s actual=%s" % (path, want or "(none)", have))
        if key == "Population":
            lines = [x for x in data.decode("utf-8", "replace").splitlines() if x.strip()]
            if len(lines) < 2:
                add("POPULATION-EMPTY", "%s has %d non-blank line(s)" % (path, len(lines)))
        now = repo.blob(rev, path)
        if now != data:
            add("FROZEN-EDITED", "%s differs at %s from freeze %s" % (path, rev[:12], freeze[:12]))

    if "Control" in fields:
        path = fields["Control"].strip()
        data = repo.blob(freeze, path.split()[0]) if path else None
        if data is None:
            add("CONTROL-MISSING", path or "(blank)")
        else:
            nonblank = [x.strip() for x in data.decode("utf-8", "replace").splitlines() if x.strip()]
            m = EXIT_LINE.match(nonblank[-1]) if nonblank else None
            if not m or int(m.group(1)) == 0:
                add("CONTROL-NOT-RED", "%s last line %r" % (path, nonblank[-1] if nonblank else ""))


def dispatch_findings(repo, round_no, freeze, out):
    tree = ".ufo/waves/round-%s/" % round_no
    for commit, names in repo.adds(freeze, tree).items():
        for name in names:
            base = posixpath.basename(name)
            if not (fnmatch.fnmatchcase(base, "*-dispatch.json") or fnmatch.fnmatchcase(base, "*.ready")):
                continue
            if repo.is_ancestor(commit, freeze):
                out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s added by %s" % (name, commit[:12])))


def evaluate(root, prereg, rev):
    if not REV.match(rev):
        raise CouldNotEvaluate("--rev must be a full40 lowercase hex commit id")
    if not os.path.isdir(root):
        raise CouldNotEvaluate("--root %s is not a directory" % root)
    repo = Repo(root)
    rc, _ = repo.run("rev-parse", "--git-dir")
    if rc != 0:
        raise CouldNotEvaluate("--root %s is not a git repository" % root)
    if not repo.commit_exists(rev):
        raise CouldNotEvaluate("--rev %s does not resolve to a commit" % rev)
    blob = repo.blob(rev, prereg)
    if blob is None:
        raise CouldNotEvaluate("%s is absent at %s" % (prereg, rev))
    round_no, claims = parse(blob.decode("utf-8", "replace"))
    findings = []
    if not claims:
        findings.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    freeze = freeze_rev(repo, rev, prereg)
    for label, fields in claims:
        check_claim(repo, label, fields, freeze, rev, findings)
    if round_no is not None:
        dispatch_findings(repo, round_no, freeze, findings)
    return len(claims), sorted(findings)


def main(argv):
    ap = argparse.ArgumentParser(description="souji freeze checklist over a preregistration at a revision")
    ap.add_argument("--root", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--rev", required=True)
    args = ap.parse_args(argv)
    try:
        n, findings = evaluate(args.root, args.prereg, args.rev)
    except CouldNotEvaluate as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2
    except Exception as exc:  # never a traceback: an unforeseen failure is a could-not-evaluate
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: unexpected %s: %s\n" % (type(exc).__name__, exc))
        return 2
    for label, cls, detail in findings:
        print("FINDING %s %s %s" % (label, cls, detail))
    print("SUMMARY claims=%d findings=%d" % (n, len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
