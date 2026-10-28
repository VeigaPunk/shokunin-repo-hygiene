#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40

Reads the preregistration blob at --rev through git (never the work tree) and checks every
`## C<digits>` claim block against the freeze rules of addendum 9. Output on stdout:

  FINDING <claim> <CLASS> <detail>     one per finding, sorted
  SUMMARY claims=<n> findings=<m>

Exit 0 no findings, 1 findings, 2 could-not-evaluate (stderr `REFUSAL COULD-NOT-EVALUATE: ...`:
--rev is not a resolvable full40 commit, PATH has no blob at --rev, or git cannot be read).
Prereg-wide findings (NO-CLAIMS, DISPATCH-BEFORE-FREEZE) carry the claim label C0.

Grammar: a claim block starts at a column-0 `## C<digits>` line and runs to the next `## ` line.
Key lines are `Key: value` at column 0 (Base, Counter, Population, Control, Target, Kill; the first
occurrence in a block wins). Base is a full40 commit; Counter/Population are `<path> sha256=<64 hex>`;
Control is `<path>`; Target and Kill are non-empty text. FREEZE-REV is the oldest commit reachable from
--rev that adds PATH. Finding classes: NO-CLAIMS FIELD-MISSING FIELD-EMPTY BASE-UNRESOLVED
BASE-NOT-ANCESTOR COUNTER-MISSING COUNTER-DIGEST POPULATION-MISSING POPULATION-DIGEST POPULATION-EMPTY
CONTROL-MISSING CONTROL-NOT-RED FROZEN-EDITED DISPATCH-BEFORE-FREEZE.

Only git plumbing is run (cat-file, log, merge-base) with read-only arguments; content read from the
repository is parsed as data and never executed. Nothing is written into --root. Python stdlib only.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

FULL40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
CLAIM_HEAD = re.compile(r"^## C([0-9]+)(?![0-9])")
KEY_LINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):(.*)$")
EXIT_LINE = re.compile(r"^EXIT=(-?[0-9]+)$")
ROUND_LINE = re.compile(r"^Round:[ \t]*([0-9]+)[ \t]*$")
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")


class CouldNotEvaluate(Exception):
    pass


class Repo:
    def __init__(self, root):
        self.root = root
        self.env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
                    "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
                    "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1"}
        tmp = os.environ.get("TMPDIR")
        if tmp:
            self.env["TMPDIR"] = tmp

    def run(self, *args):
        try:
            return subprocess.run(["git", "--literal-pathspecs", "-C", self.root] + list(args),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env,
                                  check=False)
        except OSError as exc:
            raise CouldNotEvaluate("cannot run git: %s" % exc)

    def is_commit(self, rev):
        return (FULL40.match(rev or "") is not None
                and self.run("cat-file", "-e", rev + "^{commit}").returncode == 0)

    def blob(self, rev, path):
        """Bytes of path at rev, or None when there is no blob."""
        if not path or path.startswith(":") or "\n" in path:
            return None
        p = self.run("cat-file", "blob", "%s:%s" % (rev, path))
        return p.stdout if p.returncode == 0 else None

    def is_ancestor(self, anc, desc):
        return self.run("merge-base", "--is-ancestor", anc, desc).returncode == 0

    def log(self, *args):
        p = self.run("log", "--no-renames", "--topo-order", *args)
        if p.returncode != 0:
            raise CouldNotEvaluate("git log failed: %s" % p.stderr.decode("utf-8", "replace").strip()[:200])
        return p.stdout.decode("utf-8", "replace")


def text_lines(data):
    """Decode tolerantly and split on LF/CRLF; trailing whitespace of every line removed."""
    return [ln.rstrip() for ln in data.decode("utf-8", "replace").replace("\r\n", "\n").replace("\r", "\n").split("\n")]


def parse(lines):
    """-> (round_no or None, [(label, {key: value-or-None-if-absent})])."""
    round_no = None
    blocks = []
    cur = None
    for ln in lines:
        if ln.startswith("## "):
            m = CLAIM_HEAD.match(ln)
            cur = ("C" + m.group(1), {}) if m else None
            if cur:
                blocks.append(cur)
            continue
        if cur is None:
            m = ROUND_LINE.match(ln)
            if m and round_no is None:
                round_no = m.group(1)
            continue
        m = KEY_LINE.match(ln)
        if m and m.group(1) not in cur[1]:
            cur[1][m.group(1)] = m.group(2).strip()
    if round_no is None:  # a Round line after the first block still counts
        for ln in lines:
            m = ROUND_LINE.match(ln)
            if m:
                round_no = m.group(1)
                break
    return round_no, blocks


def clean(s):
    return " ".join(s.split())[:120]


def check_blob_field(repo, freeze, label, key, value, findings, digest, population):
    """Counter/Population: returns (path, blob-at-freeze or None) after emitting findings."""
    toks = value.split()
    path = toks[0] if toks else ""
    stated = None
    for t in toks[1:]:
        if t.startswith("sha256="):
            stated = t[len("sha256="):].lower()
    up = key.upper()
    data = repo.blob(freeze, path)
    if data is None:
        findings.append((label, up + "-MISSING", "%s has no blob at %s" % (clean(path), freeze[:12])))
        return path, None
    if stated is None or not SHA64.match(stated):
        findings.append((label, up + "-DIGEST", "%s: no valid sha256= in %r" % (clean(path), clean(value))))
    elif hashlib.sha256(data).hexdigest() != stated:
        findings.append((label, up + "-DIGEST", "%s: blob at %s hashes to %s, stated %s" % (
            clean(path), freeze[:12], hashlib.sha256(data).hexdigest()[:12], stated[:12])))
    if population and sum(1 for ln in text_lines(data) if ln.strip()) < 2:
        findings.append((label, "POPULATION-EMPTY", "%s has fewer than 2 non-blank lines" % clean(path)))
    return path, data


def evaluate(repo, prereg, rev):
    data = repo.blob(rev, prereg)
    if data is None:
        raise CouldNotEvaluate("%s has no blob at %s" % (prereg, rev))
    adds = repo.log("--diff-filter=A", "--reverse", "--format=%H", rev, "--", prereg).split()
    if not adds:
        raise CouldNotEvaluate("no commit reachable from %s adds %s" % (rev, prereg))
    freeze = adds[0]
    round_no, blocks = parse(text_lines(data))
    findings = []
    if not blocks:
        findings.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % clean(prereg)))
    for label, fields in blocks:
        for key in KEYS:
            if key not in fields:
                findings.append((label, "FIELD-MISSING", key))
            elif not fields[key]:
                findings.append((label, "FIELD-EMPTY", key))
        base = fields.get("Base")
        if base:
            tok = base.split()[0]
            if not repo.is_commit(tok):
                findings.append((label, "BASE-UNRESOLVED", clean(base)))
            elif tok == freeze or not repo.is_ancestor(tok, freeze):
                findings.append((label, "BASE-NOT-ANCESTOR", "%s is not a strict ancestor of %s" % (tok[:12], freeze[:12])))
        for key, pop in (("Counter", False), ("Population", True)):
            value = fields.get(key)
            if not value:
                continue
            path, at_freeze = check_blob_field(repo, freeze, label, key, value, findings, None, pop)
            if at_freeze is not None:
                now = repo.blob(rev, path)
                if now != at_freeze:
                    findings.append((label, "FROZEN-EDITED", "%s at %s differs from %s" % (
                        clean(path), rev[:12], freeze[:12])))
        control = fields.get("Control")
        if control:
            path = control.split()[0]
            cdata = repo.blob(freeze, path)
            if cdata is None:
                findings.append((label, "CONTROL-MISSING", "%s has no blob at %s" % (clean(path), freeze[:12])))
            else:
                last = [ln.strip() for ln in text_lines(cdata) if ln.strip()]
                m = EXIT_LINE.match(last[-1]) if last else None
                if not m or int(m.group(1)) == 0:
                    findings.append((label, "CONTROL-NOT-RED", "%s last non-blank line %r is not EXIT=<nonzero>" % (
                        clean(path), clean(last[-1]) if last else "")))
    if round_no is not None:
        pat = re.compile(r"^\.ufo/waves/round-%s/(?:.*/)?(?:[^/]*-dispatch\.json|[^/]*\.ready)$" % re.escape(round_no))
        out = repo.log("--diff-filter=A", "--name-only", "--format=@%H", rev)
        cur = None
        early = {}
        for ln in out.split("\n"):
            if ln.startswith("@"):
                cur = ln[1:]
            elif ln and cur and pat.match(ln):
                if cur == freeze or repo.is_ancestor(cur, freeze):
                    early.setdefault(ln, cur)
        if early:
            first = sorted(early)[0]
            findings.append(("C0", "DISPATCH-BEFORE-FREEZE", "%d file(s) added at or before %s, e.g. %s (%s)" % (
                len(early), freeze[:12], first, early[first][:12])))
    return len(blocks), sorted(findings)


def main(argv):
    ap = argparse.ArgumentParser(description="pre-dispatch freeze check of a preregistration at a revision")
    ap.add_argument("--root", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--rev", required=True)
    args = ap.parse_args(argv)
    try:
        if not os.path.isdir(args.root):
            raise CouldNotEvaluate("--root %s is not a directory" % args.root)
        repo = Repo(args.root)
        if not repo.is_commit(args.rev):
            raise CouldNotEvaluate("--rev must name a resolvable full40 commit")
        claims, findings = evaluate(repo, args.prereg, args.rev)
    except CouldNotEvaluate as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2
    for label, cls, detail in findings:
        print("FINDING %s %s %s" % (label, cls, detail))
    print("SUMMARY claims=%d findings=%d" % (claims, len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
