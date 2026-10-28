#!/usr/bin/env python3
"""tools/souji-freeze-check.py — the pre-dispatch freeze checklist, runnable (addendum section 9).

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40

Reads the preregistration blob PATH at commit --rev through git (never the work tree) and reports:
  stdout  `FINDING <claim> <CLASS> <detail>` per finding (sorted), then `SUMMARY claims=<n> findings=<m>`
  exit    0 no findings, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...` on stderr;
          --rev unresolved or not a full40 commit, --root not a repository, or PATH absent at --rev)

Grammar (every pattern anchored at column 0). A claim block starts at `## C<digits>` and runs to the next
`## ` line. Key lines inside a block:
  Base: <full40>                           Counter: <path> sha256=<64 hex>
  Population: <path> sha256=<64 hex>       Control: <path>
  Target: <text>                           Kill: <text>
A key line that does not match its grammar counts as the key being absent (FIELD-MISSING). `Round: <N>` at
column 0 names the round whose `.ufo/waves/round-<N>/` tree is checked for early dispatch files.

FREEZE-REV is the oldest commit reachable from --rev that adds PATH. Finding classes: NO-CLAIMS,
FIELD-MISSING, FIELD-EMPTY, BASE-UNRESOLVED, BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-DIGEST,
POPULATION-MISSING, POPULATION-DIGEST, POPULATION-EMPTY, CONTROL-MISSING, CONTROL-NOT-RED, FROZEN-EDITED,
DISPATCH-BEFORE-FREEZE (claim label C0 for prereg-wide findings). Python stdlib only; read-only on --root.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

FULL40 = re.compile(r"^[0-9a-f]{40}$")
BLOCK = re.compile(r"^## C(\d+)(?![0-9A-Za-z])")
ROUND = re.compile(r"^Round:[ \t]*([0-9]+)[ \t\r]*$")
KEY_BASE = re.compile(r"^Base:(.*)$")
KEY_COUNTER = re.compile(r"^Counter:[ \t]+(\S+)[ \t]+sha256=([0-9a-f]{64})[ \t\r]*$")
KEY_POPULATION = re.compile(r"^Population:[ \t]+(\S+)[ \t]+sha256=([0-9a-f]{64})[ \t\r]*$")
KEY_CONTROL = re.compile(r"^Control:[ \t]+(\S+)[ \t\r]*$")
KEY_TARGET = re.compile(r"^Target:(.*)$")
KEY_KILL = re.compile(r"^Kill:(.*)$")
EXIT_LINE = re.compile(rb"^EXIT=([0-9]+)$")


class Refusal(Exception):
    pass


class Repo:
    def __init__(self, root):
        self.root = root
        self.env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"}
        home = os.environ.get("HOME")
        if home:
            self.env["HOME"] = home

    def run(self, *args):
        try:
            p = subprocess.run(["git", "-C", self.root] + list(args), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=self.env, check=False)
        except OSError as exc:
            raise Refusal("cannot run git: %s" % exc)
        return p.returncode, p.stdout

    def commit_ok(self, rev):
        return FULL40.match(rev) is not None and self.run("cat-file", "-e", rev + "^{commit}")[0] == 0

    def blob(self, rev, path):
        """Bytes of the blob at rev:path, or None when absent / not a plain repo path / not a blob."""
        parts = path.split("/")
        if (not path or any(p in ("", ".", "..") for p in parts) or "\n" in path or "\x00" in path):
            return None
        rc, out = self.run("cat-file", "blob", "%s:%s" % (rev, path))
        return out if rc == 0 else None

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b)[0] == 0

    def first_add(self, rev, path):
        rc, out = self.run("log", "--topo-order", "--reverse", "--no-renames", "--diff-filter=A",
                           "--format=%H", rev, "--", path)
        if rc != 0:
            return None
        for line in out.decode("ascii", "replace").split("\n"):
            if FULL40.match(line.strip()):
                return line.strip()
        return None

    def tree_files(self, rev, prefix):
        rc, out = self.run("ls-tree", "-r", "-z", "--name-only", rev, "--", prefix)
        if rc != 0:
            return []
        return [n for n in out.decode("utf-8", "replace").split("\x00") if n]


def split_blocks(lines):
    blocks, cur = [], None
    for line in lines:
        m = BLOCK.match(line)
        if m:
            cur = (m.group(1), [])
            blocks.append(cur)
        elif line.startswith("## "):
            cur = None
        elif cur is not None:
            cur[1].append(line)
    return blocks


def first_match(rx, lines):
    for line in lines:
        m = rx.match(line)
        if m:
            return m
    return None


def clean(text):
    return " ".join(text.split())[:160]


def check_blob(repo, claim, freeze, rev, kind, path, digest, findings):
    at_freeze = repo.blob(freeze, path)
    if at_freeze is None:
        findings.append((claim, kind + "-MISSING", path))
        return None
    if hashlib.sha256(at_freeze).hexdigest() != digest:
        findings.append((claim, kind + "-DIGEST", "%s stated=%s actual=%s" % (
            path, digest, hashlib.sha256(at_freeze).hexdigest())))
    at_rev = repo.blob(rev, path)
    if at_rev != at_freeze:
        findings.append((claim, "FROZEN-EDITED", path))
    return at_freeze


def check_claim(repo, num, body, freeze, rev, findings):
    claim = "C" + num
    # Base
    m = first_match(KEY_BASE, body)
    if m is None:
        findings.append((claim, "FIELD-MISSING", "Base"))
    else:
        base = m.group(1).strip()
        if not FULL40.match(base) or not repo.commit_ok(base):
            findings.append((claim, "BASE-UNRESOLVED", clean(base)))
        elif base == freeze or not repo.is_ancestor(base, freeze):
            findings.append((claim, "BASE-NOT-ANCESTOR", base))
    # Counter / Population
    m = first_match(KEY_COUNTER, body)
    if m is None:
        findings.append((claim, "FIELD-MISSING", "Counter"))
    else:
        check_blob(repo, claim, freeze, rev, "COUNTER", m.group(1), m.group(2), findings)
    m = first_match(KEY_POPULATION, body)
    if m is None:
        findings.append((claim, "FIELD-MISSING", "Population"))
    else:
        data = check_blob(repo, claim, freeze, rev, "POPULATION", m.group(1), m.group(2), findings)
        if data is not None and sum(1 for ln in data.split(b"\n") if ln.strip()) < 2:
            findings.append((claim, "POPULATION-EMPTY", m.group(1)))
    # Control
    m = first_match(KEY_CONTROL, body)
    if m is None:
        findings.append((claim, "FIELD-MISSING", "Control"))
    else:
        data = repo.blob(freeze, m.group(1))
        if data is None:
            findings.append((claim, "CONTROL-MISSING", m.group(1)))
        else:
            last = [ln.rstrip(b"\r") for ln in data.split(b"\n") if ln.strip()]
            e = EXIT_LINE.match(last[-1].strip()) if last else None
            if e is None or int(e.group(1)) == 0:
                findings.append((claim, "CONTROL-NOT-RED", m.group(1)))
    # Target / Kill
    for key, rx in (("Target", KEY_TARGET), ("Kill", KEY_KILL)):
        m = first_match(rx, body)
        if m is None:
            findings.append((claim, "FIELD-MISSING", key))
        elif not m.group(1).strip():
            findings.append((claim, "FIELD-EMPTY", key))


def evaluate(repo, prereg, rev):
    raw = repo.blob(rev, prereg)
    if raw is None:
        raise Refusal("preregistration %s is absent at %s" % (prereg, rev))
    freeze = repo.first_add(rev, prereg)
    if freeze is None:
        raise Refusal("no commit reachable from %s adds %s" % (rev, prereg))
    lines = raw.decode("utf-8", "replace").split("\n")
    findings = []
    blocks = split_blocks(lines)
    if not blocks:
        findings.append(("C0", "NO-CLAIMS", prereg))
    for num, body in blocks:
        check_claim(repo, num, body, freeze, rev, findings)
    rnd = first_match(ROUND, lines)
    if rnd:
        prefix = ".ufo/waves/round-%s/" % rnd.group(1)
        for name in repo.tree_files(rev, prefix):
            base = name.rsplit("/", 1)[-1]
            if not base.endswith("-dispatch.json"):
                continue
            added = repo.first_add(rev, name)
            if added is not None and (added == freeze or repo.is_ancestor(added, freeze)):
                findings.append(("C0", "DISPATCH-BEFORE-FREEZE", clean(name)))
    return len(blocks), findings


def main(argv):
    ap = argparse.ArgumentParser(description="read a preregistration at a revision and report freeze findings")
    ap.add_argument("--root", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--rev", required=True)
    args = ap.parse_args(argv)
    try:
        repo = Repo(args.root)
        if not os.path.isdir(args.root) or repo.run("rev-parse", "--git-dir")[0] != 0:
            raise Refusal("--root %s is not a git repository" % args.root)
        if not repo.commit_ok(args.rev):
            raise Refusal("--rev must name a resolvable full40 commit: %s" % clean(args.rev))
        claims, findings = evaluate(repo, args.prereg, args.rev)
    except Refusal as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2
    for claim, cls, detail in sorted(set(findings)):
        print("FINDING %s %s %s" % (claim, cls, clean(detail)))
    print("SUMMARY claims=%d findings=%d" % (claims, len(set(findings))))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
