#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40

Reads the preregistration PATH as the blob at --rev (git object store only, never the work tree) and
prints `FINDING <claim> <CLASS> <detail>` per finding, sorted, then `SUMMARY claims=<n> findings=<m>`.
Exit 0 no findings, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...` on stderr).

  python3 -B tools/souji-freeze-check.py --selftest

builds synthetic git repositories under $TMPDIR, runs this tool's own digest, freeze-detection and ancestry
logic over them in-process and prints `SELFTEST cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0.

Grammar: a claim block starts at `## C<digits>` and runs to the next `## ` line; inside it a key line is
`Key: value` at column 0 for Base, Counter, Population, Control, Target, Kill. Counter and Population
values are `<repo path> sha256=<64 hex>`. FREEZE-REV is the oldest commit reachable from --rev that adds
PATH. Finding classes: NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY, BASE-UNRESOLVED, BASE-NOT-ANCESTOR,
COUNTER-MISSING, COUNTER-DIGEST, POPULATION-MISSING, POPULATION-DIGEST, POPULATION-EMPTY,
CONTROL-MISSING, CONTROL-NOT-RED, FROZEN-EDITED, DISPATCH-BEFORE-FREEZE, and (r42) KEY-DUPLICATE,
HEADING-MALFORMED, COUNTER-SYMLINK, POPULATION-SYMLINK. Prereg-wide findings carry
claim label C0. A missing `Round:` line is reported as `FIELD-MISSING C0 Round` (the dispatch check cannot run
without it), an empty value of any key is `FIELD-EMPTY`, and repo paths may contain spaces (r41 wave-2 hardening,
R41w2critic01). r42 rules: a key line repeated in one claim block is KEY-DUPLICATE (one finding per key, no
first-wins); a column-0 `##` line (not `###`) that reads as a claim heading (`C`/`c`, optional spaces, a digit)
but is not `## C<digits>` followed by a space or end of line is HEADING-MALFORMED (claim C0, detail line=<n>)
and opens no claim; a Counter/Population path that is a git symlink (mode 120000) at the freeze is
COUNTER-SYMLINK/POPULATION-SYMLINK alone; DISPATCH-BEFORE-FREEZE covers any file under .ufo/waves/round-<N>/
whose basename contains `-dispatch` or `.ready`, or ends `-spec.json` or `-results.json`. Python stdlib only; read-only on --root.
"""
import argparse
import hashlib
import os
import re
import subprocess
import shutil
import sys
import tempfile

FULL40 = re.compile(r"^[0-9a-f]{40}$")
HEADER = re.compile(r"^## C(\d+)(?: |$)")
HEADING_LIKE = re.compile(r"^##(?!#) *[Cc] *[0-9]")
KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")
PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")
ROUND = re.compile(r"^\ufeff?Round:[ \t]*(\d+)[ \t]*\r?$", re.M)
EXIT_LINE = re.compile(r"^EXIT=(\d+)$")
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")


class Refusal(Exception):
    pass


class Repo:
    def __init__(self, root):
        self.root = root
        # r41 wave-2 hardening (R41w2sentinel01): a whitelisted environment, so a caller-set GIT_DIR or
        # GIT_* variable cannot change a verdict, and replace refs and mailmap files are not consulted.
        self.env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
                    "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                    "GIT_NO_REPLACE_OBJECTS": "1"}

    def run(self, *args):
        try:
            return subprocess.run(["git", "-c", "core.quotePath=false", "-c", "log.mailmap=false", "-C", self.root] + list(args), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=self.env, check=False)
        except OSError as exc:
            raise Refusal("cannot run git: %s" % exc)

    def commit(self, rev):
        """Full commit id for rev, or None."""
        p = self.run("rev-parse", "--verify", "-q", rev + "^{commit}")
        out = p.stdout.decode("utf-8", "replace").strip()
        return out if p.returncode == 0 and FULL40.match(out) else None

    def blob(self, rev, path):
        if "\x00" in path:
            return None
        p = self.run("cat-file", "blob", "%s:%s" % (rev, path))
        return p.stdout if p.returncode == 0 else None

    def is_symlink(self, rev, path):
        if "\x00" in path or not path:
            return False
        p = self.run("ls-tree", "-z", rev, "--", path)
        for ent in p.stdout.split(b"\x00"):
            meta, _, name = ent.partition(b"\t")
            if meta.startswith(b"120000 ") and name.decode("utf-8", "replace") == path:
                return True
        return False

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b).returncode == 0


def parse_claims(text):
    """Returns (claims, extra): claims = [(label, {key: value})], extra = [(label, class, detail)]."""
    claims = []
    extra = []
    cur = None
    dup = None
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            m = HEADER.match(line)
            cur = ("C" + m.group(1), {}) if m else None
            dup = set()
            if cur:
                claims.append(cur)
        elif HEADING_LIKE.match(line):
            cur = None
        if HEADING_LIKE.match(line) and not HEADER.match(line):
            extra.append(("C0", "HEADING-MALFORMED", "line=%d" % n))
            continue
        if cur is not None and not line.startswith("## "):
            m = KEYLINE.match(line)
            if m:
                if m.group(1) in cur[1]:
                    if m.group(1) not in dup:
                        dup.add(m.group(1))
                        extra.append((cur[0], "KEY-DUPLICATE", m.group(1)))
                else:
                    cur[1][m.group(1)] = m.group(2)
    return claims, extra


def freeze_rev(repo, rev, prereg):
    p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--reverse",
                 "--format=%H", rev, "--", prereg)
    ids = [x for x in p.stdout.decode("utf-8", "replace").split() if FULL40.match(x)]
    return ids[0] if p.returncode == 0 and ids else None


def dispatch_findings(repo, rev, freeze, text):
    m = ROUND.search(text)
    if not m:
        # r41 wave-2 hardening (R41w2critic01 D1/D10): without a Round line the dispatch
        # check cannot run; say so instead of reading clean.
        return [("C0", "FIELD-MISSING", "Round")]
    tree = ".ufo/waves/round-%s/" % m.group(1)
    p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--name-only",
                 "--format=%x01%H", rev, "--", tree)
    if p.returncode != 0:
        return []
    first = {}  # path -> oldest adding commit (log is newest first, so later entries overwrite)
    commit = None
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith("\x01"):
            commit = line[1:].strip()
        elif line and commit:
            base = line.rsplit("/", 1)[-1]
            if "-dispatch" in base or ".ready" in base or base.endswith(("-spec.json", "-results.json")):
                first[line] = commit
    out = []
    for path, c in sorted(first.items()):
        if c == freeze or repo.is_ancestor(c, freeze):
            out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"
                        % (path, c[:12], freeze[:12])))
    return out


def check_path_sha(repo, rev, freeze, label, key, value, missing, digest, found):
    """Counter/Population: returns the freeze blob (or None)."""
    m = PATH_SHA.match(value)
    path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)
    if not path:
        return None
    if repo.is_symlink(freeze, path):
        found.append((label, key.upper() + "-SYMLINK", "%s is a symlink (120000) at freeze %s" % (path, freeze[:12])))
        return None
    at_freeze = repo.blob(freeze, path)
    if at_freeze is None:
        found.append((label, missing, "%s not present at freeze %s" % (path, freeze[:12])))
        return None
    if want is None:
        found.append((label, digest, "%s has no sha256=<64 hex> in %r" % (path, value)))
    elif hashlib.sha256(at_freeze).hexdigest() != want:
        found.append((label, digest, "%s at freeze hashes %s, stated %s"
                      % (path, hashlib.sha256(at_freeze).hexdigest(), want)))
    at_rev = repo.blob(rev, path)
    if at_rev != at_freeze:
        found.append((label, "FROZEN-EDITED", "%s differs between freeze %s and %s"
                      % (path, freeze[:12], rev[:12])))
    return at_freeze, path


def evaluate(repo, rev, prereg, text, freeze):
    found = []
    claims, extra = parse_claims(text)
    found.extend(extra)
    if not claims:
        found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    for label, f in claims:
        for key in KEYS:
            if key not in f:
                found.append((label, "FIELD-MISSING", key))
        for key in KEYS:
            if key in f and not f[key]:
                found.append((label, "FIELD-EMPTY", key))
        if f.get("Base"):
            base = f["Base"]
            resolved = repo.commit(base) if FULL40.match(base) else None
            if resolved is None:
                found.append((label, "BASE-UNRESOLVED", base))
            elif resolved == freeze or not repo.is_ancestor(resolved, freeze):
                found.append((label, "BASE-NOT-ANCESTOR", "%s is not a strict ancestor of freeze %s"
                              % (base, freeze[:12])))
        if f.get("Counter"):
            check_path_sha(repo, rev, freeze, label, "Counter", f["Counter"],
                           "COUNTER-MISSING", "COUNTER-DIGEST", found)
        if f.get("Population"):
            got = check_path_sha(repo, rev, freeze, label, "Population", f["Population"],
                                 "POPULATION-MISSING", "POPULATION-DIGEST", found)
            if got:
                lines = [x for x in got[0].decode("utf-8", "replace").splitlines() if x.strip()]
                if len(lines) < 2:
                    found.append((label, "POPULATION-EMPTY", "%s has %d non-blank line(s)"
                                  % (got[1], len(lines))))
        if f.get("Control"):
            path = f["Control"]
            blob = repo.blob(freeze, path)
            if blob is None:
                found.append((label, "CONTROL-MISSING", "%s not present at freeze %s" % (path, freeze[:12])))
            else:
                lines = [x.strip() for x in blob.decode("utf-8", "replace").splitlines() if x.strip()]
                m = EXIT_LINE.match(lines[-1]) if lines else None
                if not (m and int(m.group(1)) != 0):
                    found.append((label, "CONTROL-NOT-RED", "%s last line %r is not EXIT=<nonzero>"
                                  % (path, lines[-1] if lines else "")))
    found.extend(dispatch_findings(repo, rev, freeze, text))
    return len(claims), found


def check(root, prereg, revarg):
    """The whole check: returns (exit code, sorted FINDING lines, claim count); raises Refusal."""
    if not os.path.isdir(root):
        raise Refusal("--root %s is not a directory" % root)
    if not FULL40.match(revarg):
        raise Refusal("--rev must be a full 40-hex commit id")
    repo = Repo(root)
    rev = repo.commit(revarg)
    if rev is None:
        raise Refusal("--rev %s does not resolve to a commit in %s" % (revarg, root))
    raw = repo.blob(rev, prereg)
    if raw is None:
        raise Refusal("%s is absent at %s" % (prereg, rev))
    freeze = freeze_rev(repo, rev, prereg)
    if freeze is None:
        raise Refusal("no commit reachable from %s adds %s" % (rev, prereg))
    n, found = evaluate(repo, rev, prereg, raw.decode("utf-8", "replace"), freeze)
    lines = sorted("FINDING %s %s %s" % f for f in found)
    return (1 if lines else 0), lines, n


# --- self-test: synthetic repositories, this tool's own digest / freeze / ancestry logic, in-process ---
# Digests are literals (not computed here) so a defect in the digest routine cannot cancel itself out.
ST_COUNTER = b"counter v1\n"
ST_COUNTER_SHA = "3eaf78409585aaeed192915f75d952fd299adf34f8fb26a63fd4dff7bd06eb87"
ST_POP = b"id\tv\nr1\t1\n"
ST_POP_SHA = "b54138f93fc53205927d7a4b10b337e0f5ff3f51528b4a214b5c1557852488ec"
ST_POP_HEAD = b"id\tv\n"
ST_POP_HEAD_SHA = "9fc964a95d196d372a2cad019b8784782a02c1b2fb80dfc0a3129b8aea05fd64"
ST_PREREG = ("Round: 9\n\n## C1 - synthetic\nBase: {base}\nCounter: c.py sha256={cd}\n"
             "Population: p.tsv sha256={pd}\nControl: ctl.txt\nTarget: t\nKill: k\n")
ST_ZERO = "0" * 40
WAVE = ".ufo/waves/round-9/"


def _st_env():
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
           "GIT_TERMINAL_PROMPT": "0"}
    for who in ("AUTHOR", "COMMITTER"):
        env["GIT_%s_NAME" % who] = "selftest"
        env["GIT_%s_EMAIL" % who] = "selftest@example.invalid"
    return env


def _st_git(d, *args):
    p = subprocess.run(["git", "-c", "core.quotePath=false", "-c", "commit.gpgsign=false", "-C", d] + list(args),
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=_st_env(), check=False)
    if p.returncode != 0:
        raise Refusal("selftest git %s failed: %s" % (" ".join(args[:2]), p.stderr.decode("utf-8", "replace")))
    return p.stdout.decode("utf-8", "replace").strip()


def _st_commit(d, files, msg):
    for path, val in files.items():
        full = os.path.join(d, path)
        if os.path.lexists(full):
            os.remove(full)
        if val is None:
            continue
        os.makedirs(os.path.dirname(full), exist_ok=True)
        if isinstance(val, tuple):
            os.symlink(val[1], full)
        else:
            with open(full, "wb") as fh:
                fh.write(val)
    _st_git(d, "add", "-A")
    _st_git(d, "commit", "-q", "--allow-empty", "-m", msg)
    return _st_git(d, "rev-parse", "HEAD")


def _st_build(d, text_fn, freeze, after, base_kind):
    _st_git(d, "init", "-q")
    if _st_git(d, "rev-parse", "--show-toplevel") != os.path.realpath(d):
        raise Refusal("selftest repo root mismatch")
    c0 = _st_commit(d, {"README": b"base\n"}, "base")
    base = {"base": c0, "zero": ST_ZERO,
            "orphan": _st_git(d, "commit-tree", "-m", "side", _st_git(d, "rev-parse", "HEAD^{tree}"))}[base_kind]
    text = text_fn(ST_PREREG.format(base=base, cd=ST_COUNTER_SHA, pd=ST_POP_SHA))
    files = {"c.py": ST_COUNTER, "p.tsv": ST_POP, "ctl.txt": b"EXIT=1\n", "prereg.txt": text.encode("utf-8")}
    files.update(freeze)
    _st_commit(d, files, "freeze")
    return _st_commit(d, after, "after") if after else _st_git(d, "rev-parse", "HEAD")


def _st_cases():
    ident = lambda t: t
    def sub(a, b):
        return lambda t: t.replace(a, b)
    no_kill = sub("Kill: k\n", "")
    return [  # name, exit, findings, text fn, freeze files, after files, base kind
        ("clean", 0, [], ident, {}, {}, "base"),
        ("clean-dispatch-after", 0, [], ident, {}, {WAVE + "w1-spec.json": b"{}\n"}, "base"),
        ("clean-notes-before", 0, [], ident, {WAVE + "notes.md": b"n\n"}, {}, "base"),
        ("clean-crlf-space-path", 0, [], lambda t: t.replace("c.py", "my c.py").replace("\n", "\r\n"),
         {"c.py": None, "my c.py": ST_COUNTER}, {}, "base"),
        ("no-claims", 1, ["C0:NO-CLAIMS"], lambda t: "Round: 9\n", {}, {}, "base"),
        ("field-missing", 1, ["C1:FIELD-MISSING"], no_kill, {}, {}, "base"),
        ("base-unresolved", 1, ["C1:BASE-UNRESOLVED"], ident, {}, {}, "zero"),
        ("base-not-ancestor", 1, ["C1:BASE-NOT-ANCESTOR"], ident, {}, {}, "orphan"),
        ("counter-digest", 1, ["C1:COUNTER-DIGEST"], sub(ST_COUNTER_SHA, "0" * 64), {}, {}, "base"),
        ("counter-missing", 1, ["C1:COUNTER-MISSING"], ident, {"c.py": None}, {}, "base"),
        ("population-empty", 1, ["C1:POPULATION-EMPTY"], sub(ST_POP_SHA, ST_POP_HEAD_SHA),
         {"p.tsv": ST_POP_HEAD}, {}, "base"),
        ("control-not-red", 1, ["C1:CONTROL-NOT-RED"], ident, {"ctl.txt": b"EXIT=0\n"}, {}, "base"),
        ("frozen-edited", 1, ["C1:FROZEN-EDITED"], ident, {}, {"c.py": b"counter v2\n"}, "base"),
        ("dispatch-before", 1, ["C0:DISPATCH-BEFORE-FREEZE"], ident,
         {WAVE + "w1-dispatch-attempts.txt": b"x\n"}, {}, "base"),
        ("dispatch-ready-deep", 1, ["C0:DISPATCH-BEFORE-FREEZE"], ident,
         {WAVE + "w1/w1.ready.dispatched": b"x\n"}, {}, "base"),
        ("dispatch-results-before", 1, ["C0:DISPATCH-BEFORE-FREEZE"], ident,
         {WAVE + "w1-results.json": b"{}\n"}, {}, "base"),
        ("key-duplicate", 1, ["C1:KEY-DUPLICATE"], sub("Target: t\n", "Target: t\nTarget: t\n"), {}, {}, "base"),
        ("heading-nospace", 1, ["C0:HEADING-MALFORMED"], lambda t: t + "##C2 - x\n", {}, {}, "base"),
        ("heading-suffix", 1, ["C0:HEADING-MALFORMED"], lambda t: t + "## C2x\n", {}, {}, "base"),
        ("counter-symlink", 1, ["C1:COUNTER-SYMLINK"], ident, {"c.py": ("L", "p.tsv")}, {}, "base"),
        ("population-symlink", 1, ["C1:POPULATION-SYMLINK"], ident, {"p.tsv": ("L", "c.py")}, {}, "base"),
    ]


def selftest():
    root = tempfile.mkdtemp(prefix="souji-freeze-selftest-")
    cases = _st_cases()
    ok = 0
    try:
        for i, (name, want_exit, want, text_fn, freeze, after, kind) in enumerate(cases):
            d = os.path.join(root, "r%d" % i)
            os.mkdir(d)
            try:
                rev = _st_build(d, text_fn, freeze, after, kind)
                code, lines, _ = check(d, "prereg.txt", rev)
                got = sorted(" ".join(x.split(" ", 3)[1:3]).replace(" ", ":") for x in lines)
                good = code == want_exit and got == sorted(want)
            except Exception:
                good = False
            ok += good
            if not good:
                sys.stderr.write("SELFTEST-FAIL %s\n" % name)
        # resolution failures are exit 2 (could-not-evaluate), not findings
        d = os.path.join(root, "refusal")
        os.mkdir(d)
        rev = _st_build(d, lambda t: t, {}, {}, "base")
        try:
            check(d, "prereg.txt", "1" * 40)
            good = False
        except Refusal:
            good = True
        ok += good
        if not good:
            sys.stderr.write("SELFTEST-FAIL unresolved-rev\n")
    except Refusal as exc:
        sys.stderr.write("SELFTEST-ERROR %s\n" % exc)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    total = len(cases) + 1
    print("SELFTEST cases=%d pass=%d fail=%d" % (total, ok, total - ok))
    return 0 if ok == total else 1


def main(argv):
    ap = argparse.ArgumentParser(description="Check a preregistration's freeze at a revision.")
    ap.add_argument("--root")
    ap.add_argument("--prereg")
    ap.add_argument("--rev")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.root and args.prereg and args.rev):
        ap.error("--root, --prereg and --rev are required (or --selftest)")
    try:
        code, lines, n = check(args.root, args.prereg, args.rev)
    except Refusal as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2
    for line in lines:
        print(line)
    print("SUMMARY claims=%d findings=%d" % (n, len(lines)))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
