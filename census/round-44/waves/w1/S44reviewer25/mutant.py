#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40
  python3 -B tools/souji-freeze-check.py --selftest

Reads the preregistration PATH as the blob at --rev (git object store only, never the work tree) and
prints `FINDING <claim> <CLASS> <detail>` per finding, sorted, then `SUMMARY claims=<n> findings=<m>`.
Exit 0 no findings, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...` on stderr).

Grammar: a claim block starts at `## C<digits>` (then a space or end of line) and runs to the next `## `
line; inside it a key line is `Key: value` at column 0 for Base, Counter, Population, Control, Target,
Kill. Counter and Population values are `<repo path> sha256=<64 hex>`. FREEZE-REV is the oldest commit
reachable from --rev that adds PATH. Finding classes: NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY, KEY-DUPLICATE,
HEADING-MALFORMED, BASE-UNRESOLVED, BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-DIGEST, COUNTER-SYMLINK,
POPULATION-MISSING, POPULATION-DIGEST, POPULATION-SYMLINK, POPULATION-EMPTY, CONTROL-MISSING,
CONTROL-NOT-RED, FROZEN-EDITED, DISPATCH-BEFORE-FREEZE. Prereg-wide findings carry claim label C0.
A missing `Round:` line is `FIELD-MISSING C0 Round`; an empty key value is FIELD-EMPTY; repo paths may
contain spaces (r41 wave-2 hardening).

r43: duplicated keys are first-wins; every further occurrence is KEY-DUPLICATE. A malformed
claim heading closes the current block; following keys are C0 UNATTACHED-KEY until a valid
claim heading. ROUND-MALFORMED rejects present Round values outside ASCII [1-9][0-9]* and
suppresses dispatch scanning. CONTROL-SYMLINK refuses a Control symlink at FREEZE without
reading its link text as a control. FROZEN-EDITED covers Control and preregistration blobs too.
CRLF lines parse through splitlines(). DISPATCH-BEFORE-FREEZE covers any file under
.ufo/waves/round-<N>/ named `*-dispatch*`, `*.ready*`, `*-spec.json`, `*-results.json`.

--selftest builds synthetic git repositories under $TMPDIR, runs this tool's own digest, freeze-detection
(`git log --diff-filter=A`) and ancestry (`git merge-base --is-ancestor`) code over them in-process and
prints `SELFTEST cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0. Python stdlib only; read-only on --root.
"""
import argparse
import contextlib
import hashlib
import io
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile

FULL40 = re.compile(r"^[0-9a-f]{40}$")
HEADER = re.compile(r"^## C(\d+)(?: |$)")
BADHEAD = re.compile(r"^##(?!#) *[Cc] *\d")
KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")
PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")
ROUND = re.compile(r"^\ufeff?Round:[ \t]*([1-9][0-9]*)[ \t]*$")
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
        p = self.run("ls-tree", "-z", "--full-tree", rev, "--", posixpath.normpath(path))
        return p.returncode == 0 and p.stdout.startswith(b"120000 ")

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b).returncode == 0


def parse_claims(text):
    """Return claim blocks, malformed heading lines and unattached key lines."""
    claims, bad, unattached, cur = [], [], [], None
    malformed_block = False
    for n, line in enumerate(text.splitlines(), 1):
        m = HEADER.match(line)
        if m:
            cur = ("C" + m.group(1), {}, [])
            claims.append(cur)
            malformed_block = False
        elif line.startswith("## ") or BADHEAD.match(line):
            cur = None
            malformed_block = bool(BADHEAD.match(line))
            if malformed_block:
                bad.append(n)
        else:
            m = KEYLINE.match(line)
            if m and cur is not None:
                if m.group(1) in cur[1]:
                    cur[2].append(m.group(1))
                else:
                    cur[1][m.group(1)] = m.group(2)
            elif m and malformed_block:
                unattached.append(n)
    return claims, bad, unattached


def freeze_rev(repo, rev, prereg):
    p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--reverse",
                 "--format=%H", rev, "--", prereg)
    ids = [x for x in p.stdout.decode("utf-8", "replace").split() if FULL40.match(x)]
    return ids[0] if p.returncode == 0 and ids else None


def dispatch_findings(repo, rev, freeze, text):
    lines = [line for line in text.splitlines() if line.lstrip("\ufeff").startswith("Round:")]
    if not lines:
        return [("C0", "FIELD-MISSING", "Round")]
    malformed = [line for line in lines if not ROUND.fullmatch(line)]
    if malformed:
        return [("C0", "ROUND-MALFORMED", "detail=%s" % line) for line in malformed]
    m = ROUND.fullmatch(lines[0])
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
                if line[len(tree):].count("/") < 2: first[line] = commit
    out = []
    for path, c in sorted(first.items()):
        if c == freeze or repo.is_ancestor(c, freeze):
            out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"
                        % (path, c[:12], freeze[:12])))
    return out


def check_path_sha(repo, rev, freeze, label, key, value, missing, digest, found):
    """Counter/Population: returns (freeze blob, path) or None."""
    m = PATH_SHA.match(value)
    path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)
    if not path:
        return None
    at_freeze = repo.blob(freeze, path)
    if at_freeze is None:
        found.append((label, missing, "%s not present at freeze %s" % (path, freeze[:12])))
        return None
    if repo.is_symlink(freeze, path):
        found.append((label, key.upper() + "-SYMLINK", "%s is a symlink at freeze %s" % (path, freeze[:12])))
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
    claims, bad, unattached = parse_claims(text)
    found.extend(("C0", "HEADING-MALFORMED", "line=%d" % n) for n in bad)
    found.extend(("C0", "UNATTACHED-KEY", "line=%d" % n) for n in unattached)
    at_freeze = repo.blob(freeze, prereg)
    at_rev = repo.blob(rev, prereg)
    if at_freeze != at_rev:
        found.append(("C0", "FROZEN-EDITED", "%s differs between freeze and revision" % prereg))
    if not claims:
        found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    for label, f, dups in claims:
        found.extend((label, "KEY-DUPLICATE", key) for key in sorted(dups))
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
            elif repo.is_symlink(freeze, path):
                found.append((label, "CONTROL-SYMLINK", "%s is a symlink at freeze" % path))
            else:
                lines = [x.strip() for x in blob.decode("utf-8", "replace").splitlines() if x.strip()]
                m = EXIT_LINE.match(lines[-1]) if lines else None
                if not (m and int(m.group(1)) != 0):
                    found.append((label, "CONTROL-NOT-RED", "%s last line %r is not EXIT=<nonzero>"
                                  % (path, lines[-1] if lines else "")))
            if repo.blob(rev, path) != blob:
                found.append((label, "FROZEN-EDITED", "%s differs between freeze and revision" % path))
    found.extend(dispatch_findings(repo, rev, freeze, text))
    return len(claims), found


# --selftest: fixture digests are literals, so a broken digest function cannot agree with itself
SHA_C = "a3a5e715f0cc574a73c3f9bebb6bc24f32ffd5b67b387244c2c909da779a1478"  # "c\n"
SHA_P = "bc0405cffdbb957b8790ce8d5ced0091b4d0b2f32bee8f8a5ffc143032bda4f8"  # "h\nr\n"
SHA_P1 = "91ee5e9f42ba3d34e414443b36a27b797a56a47aad6bb1e4c1769e69c77ce0ca"  # "h\n"
SPEC = ".ufo/waves/round-7/w1-spec.json"


def prereg(head="## C1", tail="", **over):
    """Synthetic preregistration; `@` = base commit, `%` = a commit that is not an ancestor."""
    k = dict(Base="@", Counter="c.py sha256=" + SHA_C, Population="p.tsv sha256=" + SHA_P,
             Control="ctl.txt", Target="t", Kill="k")
    k.update(over)
    return "Round: 7\n%s\n%s%s" % (head, "".join("%s: %s\n" % i for i in k.items() if i[1] is not None), tail)


CASES = [  # (name, exit, "C1:CLASS,...", prereg text, options)
    ("clean", 0, "", prereg(), {}),
    ("dispatch-after", 0, "", prereg(), {"post": {SPEC: "x"}}),
    ("notes-before", 0, "", prereg(), {"pre": {".ufo/waves/round-7/notes.md": "x"}}),
    ("sub-heading", 0, "", prereg(tail="### C 9\n"), {}),
    ("no-claims", 1, "C0:NO-CLAIMS", "Round: 7\n", {}),
    ("field-missing", 1, "C1:FIELD-MISSING", prereg(Kill=None), {}),
    ("field-empty", 1, "C1:FIELD-EMPTY", prereg(Target=""), {}),
    ("base-unresolved", 1, "C1:BASE-UNRESOLVED", prereg(Base="0" * 40), {}),
    ("base-not-ancestor", 1, "C1:BASE-NOT-ANCESTOR", prereg(Base="%"), {}),
    ("counter-missing", 1, "C1:COUNTER-MISSING", prereg(Counter="n.py sha256=" + SHA_C), {}),
    ("counter-digest", 1, "C1:COUNTER-DIGEST", prereg(Counter="c.py sha256=" + SHA_P), {}),
    ("population-missing", 1, "C1:POPULATION-MISSING", prereg(Population="n.tsv sha256=" + SHA_P), {}),
    ("population-digest", 1, "C1:POPULATION-DIGEST", prereg(Population="p.tsv sha256=" + SHA_C), {}),
    ("population-empty", 1, "C1:POPULATION-EMPTY", prereg(Population="p.tsv sha256=" + SHA_P1),
     {"fz": {"p.tsv": "h\n"}}),
    ("control-missing", 1, "C1:CONTROL-MISSING", prereg(Control="n.txt"), {}),
    ("control-not-red", 1, "C1:CONTROL-NOT-RED", prereg(), {"fz": {"ctl.txt": "x\nEXIT=0\n"}}),
    ("frozen-edited", 1, "C1:FROZEN-EDITED", prereg(), {"post": {"c.py": "d\n"}}),
    ("dispatch-before", 1, "C0:DISPATCH-BEFORE-FREEZE", prereg(), {"pre": {SPEC: "x"}}),
    ("dispatch-attempts", 1, "C0:DISPATCH-BEFORE-FREEZE", prereg(),
     {"pre": {".ufo/waves/round-7/w1-dispatch-attempts.txt": "x"}}),
    ("dispatch-ready", 1, "C0:DISPATCH-BEFORE-FREEZE", prereg(),
     {"pre": {".ufo/waves/round-7/a/w1.ready.dispatched": "x"}}),
    ("dispatch-results", 1, "C0:DISPATCH-BEFORE-FREEZE", prereg(),
     {"pre": {".ufo/waves/round-7/w1-results.json": "x"}}),
    ("key-duplicate", 1, "C1:KEY-DUPLICATE", prereg(tail="Target: u\n"), {}),
    ("heading-nospace", 1, "C0:HEADING-MALFORMED", prereg(tail="##C2\n"), {}),
    ("heading-lowercase", 1, "C0:HEADING-MALFORMED", prereg(tail="## c2\n"), {}),
    ("heading-spaced", 1, "C0:HEADING-MALFORMED", prereg(tail="## C 2\n"), {}),
    ("heading-suffix", 1, "C0:HEADING-MALFORMED", prereg(tail="## C2x\n"), {}),
    ("heading-valid-tail", 1, ",".join(["C2:FIELD-MISSING"] * 6), prereg(tail="## C2 tail\n"), {}),
    ("counter-symlink", 1, "C1:COUNTER-SYMLINK", prereg(), {"fz": {"c.py": ("x",)}}),
    ("population-symlink", 1, "C1:POPULATION-SYMLINK", prereg(), {"fz": {"p.tsv": ("x",)}}),
    ("rev-unresolved", 2, "", prereg(), {"rev": "1" * 40}),
    ("duplicate-first-bad", 1, "C1:BASE-UNRESOLVED,C1:KEY-DUPLICATE",
     prereg(Base="0" * 40, tail="Base: @\n"), {}),
    ("duplicate-three", 1, "C1:KEY-DUPLICATE,C1:KEY-DUPLICATE",
     prereg(tail="Target: u\nTarget: v\n"), {}),
    ("unattached-key", 1, "C0:HEADING-MALFORMED,C0:UNATTACHED-KEY",
     prereg(tail="##C2\nTarget: unattached\n"), {}),
    ("round-zero-padded", 1, "C0:ROUND-MALFORMED",
     prereg().replace("Round: 7", "Round: 07"), {}),
    ("round-fullwidth", 1, "C0:ROUND-MALFORMED",
     prereg().replace("Round: 7", "Round: ７"), {}),
    ("control-symlink", 1, "C1:CONTROL-SYMLINK",
     prereg(), {"fz": {"ctl.txt": ("EXIT=1",)}}),
    ("control-edited", 1, "C1:FROZEN-EDITED",
     prereg(), {"post": {"ctl.txt": "different\nEXIT=1\n"}}),
    ("prereg-edited", 1, "C0:FROZEN-EDITED,C0:NO-CLAIMS",
     prereg(), {"post": {"pre.txt": "Round: 7\n"}}),
    ("round-missing", 1, "C0:FIELD-MISSING",
     prereg().replace("Round: 7\n", ""), {}),
    ("crlf-prereg", 0, "", prereg().replace("\n", "\r\n"), {}),
    ("prereg-absent", 2, "", prereg(), {"path": "nope.txt"}),
]


def selftest_case(tmp, n, code, want, text, pre=None, fz=None, post=None, rev=None, path="pre.txt"):
    d = os.path.join(tmp, "r%d" % n)
    os.mkdir(d)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_AUTHOR_NAME": "st", "GIT_AUTHOR_EMAIL": "st@example.invalid",
           "GIT_COMMITTER_NAME": "st", "GIT_COMMITTER_EMAIL": "st@example.invalid"}

    def git(*a):
        return subprocess.run(["git", "-C", d] + list(a), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=env, check=True).stdout.decode().strip()

    def commit(files):
        for p, c in files.items():
            fp = os.path.join(d, p)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            if isinstance(c, tuple):
                os.symlink(c[0], fp)
            else:
                with open(fp, "w") as fh:
                    fh.write(c)
        git("add", "-A")
        git("commit", "-q", "-m", "c")
        return git("rev-parse", "HEAD")

    git("init", "-q")
    base = commit({"a": "a", **(pre or {})})
    orphan = git("commit-tree", "HEAD^{tree}", "-m", "o")
    text = text.replace("@", base).replace("%", orphan)
    commit({"pre.txt": text, "c.py": "c\n", "p.tsv": "h\nr\n", "ctl.txt": "x\nEXIT=1\n", **(fz or {})})
    if post:
        commit(post)
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        rc = main(["--root", d, "--prereg", path, "--rev", rev or git("rev-parse", "HEAD")])
    got = sorted("%s:%s" % tuple(x.split()[1:3]) for x in out.getvalue().splitlines() if x.startswith("FINDING "))
    return rc == code and got == sorted(want.split(",") if want else [])


def selftest():
    tmp = tempfile.mkdtemp(prefix="freeze-selftest-")
    passed = 0
    try:
        for n, (name, code, want, text, opts) in enumerate(CASES):
            try:
                ok = selftest_case(tmp, n, code, want, text, **opts)
            except Exception as exc:  # a case that cannot run is a failed case
                ok = False
                sys.stderr.write("selftest %s: %s: %s\n" % (name, type(exc).__name__, exc))
            if not ok:
                sys.stderr.write("selftest FAIL %s\n" % name)
            passed += ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST cases=%d pass=%d fail=%d" % (len(CASES), passed, len(CASES) - passed))
    return 0 if passed == len(CASES) else 1


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
        if not os.path.isdir(args.root):
            raise Refusal("--root %s is not a directory" % args.root)
        if not FULL40.match(args.rev):
            raise Refusal("--rev must be a full 40-hex commit id")
        repo = Repo(args.root)
        rev = repo.commit(args.rev)
        if rev is None:
            raise Refusal("--rev %s does not resolve to a commit in %s" % (args.rev, args.root))
        raw = repo.blob(rev, args.prereg)
        if raw is None:
            raise Refusal("%s is absent at %s" % (args.prereg, rev))
        freeze = freeze_rev(repo, rev, args.prereg)
        if freeze is None:
            raise Refusal("no commit reachable from %s adds %s" % (rev, args.prereg))
        n, found = evaluate(repo, rev, args.prereg, raw.decode("utf-8", "replace"), freeze)
    except Refusal as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2
    lines = sorted("FINDING %s %s %s" % f for f in found)
    for line in lines:
        print(line)
    print("SUMMARY claims=%d findings=%d" % (n, len(lines)))
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
