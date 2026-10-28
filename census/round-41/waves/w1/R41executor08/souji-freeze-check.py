#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist, runnable.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40

Reads the preregistration blob PATH at --rev through git (never the work tree) and reports, per
claim block (`## C<digits>` up to the next `## ` line), the grammar and freeze findings:

  stdout  FINDING <claim> <CLASS> <detail>   (sorted), then  SUMMARY claims=<n> findings=<m>
  exit    0 no findings, 1 findings, 2 could-not-evaluate (REFUSAL COULD-NOT-EVALUATE: ... on stderr)

Key lines (column 0, inside a claim block): Base, Counter, Population, Control, Target, Kill.
Counter/Population carry `<repo path> sha256=<64 hex>`; Base is a full40 commit that must be a strict
ancestor of FREEZE-REV, the oldest commit reachable from --rev that adds PATH.

Classes: NO-CLAIMS FIELD-MISSING FIELD-EMPTY BASE-UNRESOLVED BASE-NOT-ANCESTOR COUNTER-MISSING
COUNTER-DIGEST POPULATION-MISSING POPULATION-DIGEST POPULATION-EMPTY CONTROL-MISSING CONTROL-NOT-RED
FROZEN-EDITED DISPATCH-BEFORE-FREEZE (claim label C0 for prereg-wide findings).

Git use: one persistent `cat-file --batch`, one `log`, one `rev-list`. Stdlib only; read-only.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

REV = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")
KEY_LINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")
HEAD = re.compile(r"^## (C\d+)\b")
EXIT_LINE = re.compile(r"^EXIT=([+-]?\d+)$")
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_TERMINAL_PROMPT": "0"}


class Refusal(Exception):
    pass


def git_env():
    env = dict(os.environ)
    env.update(GIT_ENV)
    return env


class Batch:
    """One long-lived `git cat-file --batch`; get(spec) -> (oid, bytes) or None when missing."""

    def __init__(self, root):
        self.p = subprocess.Popen(["git", "-C", root, "cat-file", "--batch"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=git_env())

    def get(self, spec):
        self.p.stdin.write(spec.encode("utf-8", "surrogateescape") + b"\n")
        self.p.stdin.flush()
        head = self.p.stdout.readline().split()
        if len(head) != 3 or not head[2].isdigit():
            return None
        body = self.p.stdout.read(int(head[2]))
        self.p.stdout.read(1)
        return head[0].decode(), head[1].decode(), body

    def close(self):
        try:
            self.p.stdin.close()
            self.p.stdout.close()
        except OSError:
            pass
        self.p.wait()


def run_git(root, *args):
    p = subprocess.run(["git", "-C", root, "-c", "core.quotePath=false"] + list(args),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=git_env(), check=False)
    if p.returncode != 0:
        raise Refusal("git %s failed: %s" % (args[0], p.stderr.decode("utf-8", "replace").strip()[:200]))
    return p.stdout.decode("utf-8", "surrogateescape")


def parse_blocks(text):
    blocks, cur = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            m = HEAD.match(line)
            cur = [m.group(1), {}] if m else None
            if cur:
                blocks.append(cur)
            continue
        if cur is None:
            continue
        m = KEY_LINE.match(line)
        if m and m.group(1) not in cur[1]:
            cur[1][m.group(1)] = m.group(2)
    return blocks


def path_sha(value):
    """(path, sha256 hex or None) from `<path> sha256=<hex>`; path None when the value is blank."""
    toks = value.split()
    if not toks:
        return None, None
    sha = None
    for t in toks[1:]:
        if t.startswith("sha256=") and HEX64.match(t[7:]):
            sha = t[7:].lower()
    return toks[0], sha


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--prereg", required=True)
    ap.add_argument("--rev", required=True)
    a = ap.parse_args(argv)
    try:
        return check(a)
    except Refusal as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2


def check(a):
    if not REV.match(a.rev):
        raise Refusal("--rev must be a full40 hex commit id")
    if not os.path.isdir(a.root):
        raise Refusal("--root is not a directory: %s" % a.root)
    batch = Batch(a.root)
    try:
        head = batch.get(a.rev + "^{commit}")
        if head is None:
            raise Refusal("--rev %s does not resolve to a commit in %s" % (a.rev, a.root))
        prereg = batch.get("%s:%s" % (a.rev, a.prereg))
        if prereg is None or prereg[1] != "blob":
            raise Refusal("%s is absent at %s" % (a.prereg, a.rev))
        text = prereg[2].decode("utf-8", "replace")
        blocks = parse_blocks(text)
        rm = re.search(r"^Round:[ \t]*(\d+)\b", text, re.M)
        rnd = rm.group(1) if rm else None

        # one log: every add of PATH (freeze) and of dispatch-class files under the round tree
        specs = [a.prereg]
        wave_dir = ".ufo/waves/round-%s/" % rnd if rnd else None
        if wave_dir:
            specs.append(wave_dir)
        out = run_git(a.root, "log", "--full-history", "--no-renames", "--diff-filter=A", "--name-only",
                      "--format=%x01%H", a.rev, "--", *specs)
        adds, cur = {}, None   # path -> [commit...] newest first
        for line in out.splitlines():
            if line.startswith("\x01"):
                cur = line[1:]
            elif line and cur:
                adds.setdefault(line, []).append(cur)
        if a.prereg not in adds:
            raise Refusal("no commit reachable from %s adds %s" % (a.rev, a.prereg))
        freeze = adds[a.prereg][-1]
        anc = set(run_git(a.root, "rev-list", freeze).split())   # includes freeze itself

        found = []

        def add(claim, cls, detail):
            found.append("FINDING %s %s %s" % (claim, cls, " ".join(str(detail).split())))

        if not blocks:
            add("C0", "NO-CLAIMS", "no `## C<digits>` block in %s" % a.prereg)
        if wave_dir:
            for path in sorted(adds):
                base = path.rsplit("/", 1)[-1]
                if path.startswith(wave_dir) and (base.endswith("-dispatch.json") or base.endswith(".ready")):
                    early = [c for c in adds[path] if c in anc]
                    if early:
                        add("C0", "DISPATCH-BEFORE-FREEZE", "%s added at %s, freeze %s"
                            % (path, early[-1][:12], freeze[:12]))

        for label, f in blocks:
            for key in KEYS:
                if key not in f:
                    add(label, "FIELD-MISSING", key)
                elif key in ("Target", "Kill") and not f[key]:
                    add(label, "FIELD-EMPTY", key)
            if "Base" in f:
                b = f["Base"].split()[0] if f["Base"].split() else ""
                if not REV.match(b):
                    add(label, "BASE-UNRESOLVED", "not a full40: %r" % f["Base"])
                else:
                    r = batch.get(b + "^{commit}")
                    if r is None:
                        add(label, "BASE-UNRESOLVED", b)
                    elif b == freeze or b not in anc:
                        add(label, "BASE-NOT-ANCESTOR", "%s vs freeze %s" % (b[:12], freeze[:12]))
            for key, up in (("Counter", "COUNTER"), ("Population", "POPULATION")):
                if key not in f:
                    continue
                path, sha = path_sha(f[key])
                at = batch.get("%s:%s" % (freeze, path)) if path else None
                if at is None or at[1] != "blob":
                    add(label, up + "-MISSING", path or "(blank)")
                    continue
                if sha is None or hashlib.sha256(at[2]).hexdigest() != sha:
                    add(label, up + "-DIGEST", "%s sha256=%s stated=%s" % (
                        path, hashlib.sha256(at[2]).hexdigest()[:12], (sha or "none")[:12]))
                if key == "Population" and sum(1 for ln in at[2].splitlines() if ln.strip()) < 2:
                    add(label, "POPULATION-EMPTY", path)
                now = batch.get("%s:%s" % (a.rev, path))
                if now is None or now[0] != at[0]:
                    add(label, "FROZEN-EDITED", "%s %s@%s differs from freeze %s" % (
                        key, path, a.rev[:12], freeze[:12]))
            if "Control" in f:
                path = f["Control"].split()[0] if f["Control"].split() else None
                at = batch.get("%s:%s" % (freeze, path)) if path else None
                if at is None or at[1] != "blob":
                    add(label, "CONTROL-MISSING", path or "(blank)")
                else:
                    lines = [ln.strip() for ln in at[2].decode("utf-8", "replace").splitlines() if ln.strip()]
                    m = EXIT_LINE.match(lines[-1]) if lines else None
                    if not m or int(m.group(1)) == 0:
                        add(label, "CONTROL-NOT-RED", "%s last line %r" % (path, lines[-1] if lines else ""))
    finally:
        batch.close()
    found.sort()
    for line in found:
        print(line)
    print("SUMMARY claims=%d findings=%d" % (len(blocks), len(found)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
