#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist, runnable (r41 C2).

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40

Reads the preregistration blob PATH at commit --rev through git (never from the work tree) and reports,
per `## C<digits>` claim block, the grammar and freeze findings below.

  stdout  `FINDING <claim> <CLASS> <detail>` per finding (sorted), then `SUMMARY claims=<n> findings=<m>`
  exit    0 no findings | 1 findings | 2 could-not-evaluate (stderr `REFUSAL COULD-NOT-EVALUATE: <why>`,
          nothing on stdout): --rev not a full40 lowercase hex or not a commit, --root not a git
          repository top level, shallow history, PATH absent at --rev or not UTF-8, bad arguments,
          or any git failure.  The tool never prints a traceback.

Grammar. A claim block starts at a line `## C<digits>` and runs to the next `## ` line. In a block a
key line is `Key: value` at column 0 (first occurrence wins):
  Base: <full40>   Counter: <path> sha256=<64 hex>   Population: <path> sha256=<64 hex>
  Control: <path>  Target: <text>                    Kill: <text>
FREEZE-REV = the oldest commit reachable from --rev that adds PATH (`git log --diff-filter=A`).

Classes: NO-CLAIMS FIELD-MISSING FIELD-EMPTY BASE-UNRESOLVED BASE-NOT-ANCESTOR COUNTER-MISSING
COUNTER-DIGEST POPULATION-MISSING POPULATION-DIGEST POPULATION-EMPTY CONTROL-MISSING CONTROL-NOT-RED
FROZEN-EDITED DISPATCH-BEFORE-FREEZE.  Prereg-wide findings (NO-CLAIMS, DISPATCH-BEFORE-FREEZE) carry
the claim label C0.  A finding about a field that is absent or unparseable is not cascaded into the
checks that would need that field.

Hermeticity. Every git call is `git --no-optional-locks --no-pager -C <root> ...` with an absolute git
binary and an environment built from scratch (PATH, LC_ALL, GIT_CONFIG_* nulled, GIT_OPTIONAL_LOCKS=0,
GIT_NO_REPLACE_OBJECTS=1, GIT_TERMINAL_PROMPT=0, protocol.allow=never): no inherited GIT_* variable, no
user or system config, no network, stdin closed. Only read-only git subcommands are used; nothing is
ever written into --root. Python standard library only.
"""
import argparse
import fnmatch
import hashlib
import os
import re
import shutil
import subprocess
import sys

FULL40 = re.compile(r"^[0-9a-f]{40}$")
CLAIM = re.compile(r"^## C([0-9]+)(?![0-9A-Za-z_])")
KEY = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")
ROUND = re.compile(r"^Round:[ \t]*([0-9]+)[ \t]*$")
PATH_SHA = re.compile(r"^(\S+)(?:[ \t]+sha256=([0-9a-fA-F]{64}))?[ \t]*$")
EXIT_LINE = re.compile(r"^EXIT=([0-9]+)$")
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")
DISPATCH_GLOBS = ("*-dispatch.json", "*.ready")
GIT_TIMEOUT = 120


class Refusal(Exception):
    """could-not-evaluate: exit 2, stderr REFUSAL line, empty stdout."""


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Refusal("bad arguments: %s" % message)


class Git:
    def __init__(self, root):
        exe = shutil.which("git")
        if not exe:
            raise Refusal("git binary not found on PATH")
        self.exe = os.path.realpath(exe)
        self.root = root
        self.env = {
            "PATH": os.path.dirname(self.exe) + os.pathsep + "/usr/bin" + os.pathsep + "/bin",
            "LC_ALL": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_TERMINAL_PROMPT": "0",
        }

    def run(self, *args):
        cmd = [self.exe, "--no-optional-locks", "--no-pager", "-C", self.root,
               "-c", "core.quotepath=off", "-c", "protocol.allow=never",
               "-c", "log.showSignature=false", "-c", "log.mailmap=false",
               "-c", "core.fsmonitor=false"] + list(args)
        try:
            return subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=self.env, check=False,
                                  timeout=GIT_TIMEOUT)
        except (OSError, subprocess.SubprocessError) as exc:
            raise Refusal("git %s could not run: %s" % (args[0] if args else "", type(exc).__name__))

    def ok(self, *args):
        """Return stdout bytes; refuse on any nonzero exit."""
        p = self.run(*args)
        if p.returncode != 0:
            tail = p.stderr.decode("utf-8", "replace").strip().splitlines()
            raise Refusal("git %s failed (rc=%d): %s" % (args[0], p.returncode, tail[-1] if tail else ""))
        return p.stdout

    def blob(self, rev, path):
        """Blob bytes of path at rev, or None when there is no such blob (absent or not a blob)."""
        p = self.run("cat-file", "blob", "%s:%s" % (rev, path))
        return p.stdout if p.returncode == 0 else None

    def is_commit(self, rev):
        return self.run("cat-file", "-e", rev + "^{commit}").returncode == 0

    def is_ancestor(self, anc, rev):
        """True when anc is rev or an ancestor of rev."""
        rc = self.run("merge-base", "--is-ancestor", anc, rev).returncode
        if rc == 0:
            return True
        if rc == 1:
            return False
        raise Refusal("git merge-base --is-ancestor failed (rc=%d)" % rc)


def clean(text):
    return re.sub(r"[\x00-\x1f\x7f]", "?", str(text))[:200]


def parse_blocks(text):
    """Return (round_no or None, [(label, {key: value})])."""
    round_no = None
    blocks = []
    cur = None
    for raw in text.split("\n"):
        line = raw.rstrip("\r")
        if round_no is None:
            m = ROUND.match(line)
            if m:
                round_no = m.group(1)
        if line.startswith("## "):
            m = CLAIM.match(line)
            cur = ("C" + m.group(1), {}) if m else None
            if cur is not None:
                blocks.append(cur)
            continue
        if cur is not None:
            m = KEY.match(line)
            if m and m.group(1) not in cur[1]:
                cur[1][m.group(1)] = m.group(2)
    return round_no, blocks


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_blob(g, label, fields, key, freeze, rev, kind, out):
    """Counter/Population shared checks. Returns the blob at FREEZE-REV or None."""
    value = fields.get(key)
    if value is None or value == "":
        out.append((label, "FIELD-MISSING", key))
        return None
    m = PATH_SHA.match(value)
    if not m:
        out.append((label, "FIELD-MISSING", "%s (malformed: %s)" % (key, clean(value))))
        return None
    path, stated = m.group(1), m.group(2)
    at_freeze = g.blob(freeze, path)
    if at_freeze is None:
        out.append((label, kind + "-MISSING", "%s at %s" % (clean(path), freeze)))
        return None
    if stated is None:
        out.append((label, kind + "-DIGEST", "%s has no sha256 stated" % clean(path)))
    elif sha256(at_freeze) != stated.lower():
        out.append((label, kind + "-DIGEST", "%s stated %s actual %s" % (
            clean(path), stated.lower(), sha256(at_freeze))))
    if rev != freeze:
        at_rev = g.blob(rev, path)
        if at_rev != at_freeze:
            out.append((label, "FROZEN-EDITED", "%s differs at %s from %s" % (clean(path), rev, freeze)))
    return at_freeze


def check_claim(g, label, fields, freeze, rev, out):
    for key in KEYS:
        if key not in fields:
            out.append((label, "FIELD-MISSING", key))
    for key in ("Target", "Kill"):
        if key in fields and fields[key] == "":
            out.append((label, "FIELD-EMPTY", key))
    # Base
    if "Base" in fields:
        base = fields["Base"]
        if not FULL40.match(base) or not g.is_commit(base):
            out.append((label, "BASE-UNRESOLVED", clean(base) or "(blank)"))
        elif base == freeze or not g.is_ancestor(base, freeze):
            out.append((label, "BASE-NOT-ANCESTOR", "%s vs freeze %s" % (base, freeze)))
    # Counter
    if "Counter" in fields:
        check_blob(g, label, fields, "Counter", freeze, rev, "COUNTER", out)
    # Population
    if "Population" in fields:
        pop = check_blob(g, label, fields, "Population", freeze, rev, "POPULATION", out)
        if pop is not None:
            lines = [ln for ln in pop.decode("utf-8", "replace").splitlines() if ln.strip()]
            if len(lines) < 2:
                out.append((label, "POPULATION-EMPTY", "%d non-blank line(s)" % len(lines)))
    # Control
    if "Control" in fields:
        value = fields["Control"]
        m = re.match(r"^(\S+)", value)
        if not m:
            out.append((label, "FIELD-MISSING", "Control (blank)"))
        else:
            path = m.group(1)
            ctl = g.blob(freeze, path)
            if ctl is None:
                out.append((label, "CONTROL-MISSING", "%s at %s" % (clean(path), freeze)))
            else:
                lines = [ln.strip() for ln in ctl.decode("utf-8", "replace").splitlines() if ln.strip()]
                em = EXIT_LINE.match(lines[-1]) if lines else None
                if not em or int(em.group(1)) == 0:
                    out.append((label, "CONTROL-NOT-RED", "%s last line %s" % (
                        clean(path), clean(lines[-1]) if lines else "(empty)")))


def dispatch_findings(g, round_no, rev, freeze, out):
    if round_no is None:
        return
    prefix = ".ufo/waves/round-%s/" % round_no
    raw = g.ok("log", "--no-renames", "--full-history", "--diff-filter=A", "--name-only", "-z",
               "--format=%x01%H", rev, "--", prefix)
    ancestors = None
    seen = set()
    for chunk in raw.decode("utf-8", "replace").split("\x01"):
        if len(chunk) < 40:
            continue
        commit = chunk[:40]
        for name in chunk[40:].split("\x00"):
            name = name.lstrip("\n")
            if not name.startswith(prefix) or name in seen:
                continue
            if not any(fnmatch.fnmatchcase(name.rsplit("/", 1)[-1], pat) for pat in DISPATCH_GLOBS):
                continue
            if ancestors is None:
                ancestors = set(g.ok("rev-list", freeze).decode("ascii").split())
            if commit in ancestors:
                seen.add(name)
                out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added by %s (freeze %s)" % (
                    clean(name), commit, freeze)))


def evaluate(root, prereg, rev):
    if not FULL40.match(rev):
        raise Refusal("--rev must be a full 40-character lowercase hex commit id")
    if not os.path.isdir(root):
        raise Refusal("--root is not a directory")
    if not prereg or "\x00" in prereg or os.path.isabs(prereg) or prereg.startswith("-"):
        raise Refusal("--prereg must be a repository-relative path")
    g = Git(os.path.abspath(root))
    top = g.run("rev-parse", "--show-toplevel")
    if top.returncode != 0 or os.path.realpath(top.stdout.decode("utf-8", "replace").strip()) != \
            os.path.realpath(root):
        raise Refusal("--root is not a git repository top level")
    if g.ok("rev-parse", "--is-shallow-repository").strip() != b"false":
        raise Refusal("shallow repository: FREEZE-REV cannot be derived")
    if not g.is_commit(rev):
        raise Refusal("--rev does not resolve to a commit")
    data = g.blob(rev, prereg)
    if data is None:
        raise Refusal("%s is absent at %s" % (clean(prereg), rev))
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise Refusal("%s at %s is not valid UTF-8" % (clean(prereg), rev))
    adds = g.ok("log", "--no-renames", "--full-history", "--diff-filter=A", "--format=%H",
                "--topo-order", "--reverse", rev, "--", prereg).decode("ascii").split()
    if not adds:
        raise Refusal("no commit reachable from %s adds %s" % (rev, clean(prereg)))
    freeze = adds[0]
    round_no, blocks = parse_blocks(text)
    out = []
    if not blocks:
        out.append(("C0", "NO-CLAIMS", "no ## C<digits> block in %s" % clean(prereg)))
    for label, fields in blocks:
        check_claim(g, label, fields, freeze, rev, out)
    dispatch_findings(g, round_no, rev, freeze, out)
    return len(blocks), sorted("FINDING %s %s %s" % f for f in out)


def main(argv):
    try:
        ap = Parser(prog="souji-freeze-check.py", add_help=True)
        ap.add_argument("--root", required=True)
        ap.add_argument("--prereg", required=True)
        ap.add_argument("--rev", required=True)
        args = ap.parse_args(argv)
        claims, lines = evaluate(args.root, args.prereg, args.rev)
    except Refusal as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2
    except SystemExit as exc:  # --help
        return exc.code if isinstance(exc.code, int) else 0
    except Exception as exc:  # never a traceback
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: internal %s\n" % type(exc).__name__)
        return 2
    sys.stdout.write("".join(ln + "\n" for ln in lines))
    sys.stdout.write("SUMMARY claims=%d findings=%d\n" % (claims, len(lines)))
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
