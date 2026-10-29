#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40
  python3 -B tools/souji-freeze-check.py --selftest

Reads the preregistration PATH as the blob at --rev (git object store only, never the work tree) and
prints `FINDING <claim> <CLASS> <detail>` per finding, sorted, then `SUMMARY claims=<n> findings=<m>`.
Exit 0 no findings, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...` on stderr).

Grammar: a claim block starts at `## C<digits>` (followed by a space or end of line) and runs to the next
`## ` line; inside it a key line is `Key: value` at column 0 for Base, Counter, Population, Control,
Target, Kill. Counter and Population values are `<repo path> sha256=<64 hex>`. FREEZE-REV is the oldest
commit reachable from --rev that adds PATH. Finding classes: NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY,
BASE-UNRESOLVED, BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-DIGEST, POPULATION-MISSING,
POPULATION-DIGEST, POPULATION-EMPTY, CONTROL-MISSING, CONTROL-NOT-RED, FROZEN-EDITED,
DISPATCH-BEFORE-FREEZE and, new in r42, KEY-DUPLICATE, HEADING-MALFORMED, COUNTER-SYMLINK,
POPULATION-SYMLINK. Prereg-wide findings carry claim label C0. A missing `Round:` line is reported as
`FIELD-MISSING C0 Round` (the dispatch check cannot run without it), an empty value of any key is
`FIELD-EMPTY`, and repo paths may contain spaces (r41 wave-2 hardening, R41w2critic01).

r42 rules (exactly these):
  KEY-DUPLICATE        a key appears on more than one line of one claim block (identical value or not);
                       one finding per duplicated key (detail: the key); the first line is still the
                       value the other checks read.
  HEADING-MALFORMED    a column-0 line starting `##` (not `###`), optional spaces, `C` or `c`, optional
                       spaces, a digit, that is not `## C<digits>` followed by a space or end of line
                       (`##C1`, `## c1`, `## C 1`, `## C1x`): claim C0, detail line=<n>; it opens no
                       claim and closes the open one.
  COUNTER-SYMLINK / POPULATION-SYMLINK
                       the path is a symlink (git mode 120000) at FREEZE-REV: that finding alone, the
                       link text is not read as the counter / population.
  DISPATCH-BEFORE-FREEZE
                       any file under `.ufo/waves/round-<N>/` (any depth) whose basename contains
                       `-dispatch` or `.ready`, or ends `-spec.json` or `-results.json`, first added by
                       FREEZE-REV or an ancestor of it.

`--selftest` builds its own synthetic repositories under $TMPDIR, runs this tool's own digest,
freeze-detection (`git log --diff-filter=A`) and ancestry (`git merge-base --is-ancestor`) code over them
in-process and prints `SELFTEST cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0. Python stdlib only;
read-only on --root.
"""
import argparse
import contextlib
import hashlib
import io
import os
import re
import shutil
import subprocess
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
SYMLINK_MODE = "120000"


class Refusal(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


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

    def mode(self, rev, path):
        """Git file mode of path at rev (e.g. '100644', '120000'), or None."""
        if "\x00" in path:
            return None
        p = self.run("ls-tree", "-z", "--full-tree", rev, "--", path)
        if p.returncode != 0:
            return None
        for rec in p.stdout.decode("utf-8", "replace").split("\x00"):
            meta, _, name = rec.partition("\t")
            if name == path and meta:
                return meta.split(" ", 1)[0]
        return None

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b).returncode == 0


def parse_claims(text):
    """Returns (claims, malformed): claims [(label, {key: first value}, [duplicated keys])], malformed
    [line numbers of heading-like lines that open no claim]."""
    claims = []
    malformed = []
    cur = None
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("##") and not line.startswith("###"):
            m = HEADER.match(line)
            if m:
                cur = ("C" + m.group(1), {}, [])
                claims.append(cur)
            else:
                cur = None
                if HEADING_LIKE.match(line):
                    malformed.append(n)
            continue
        if cur is not None:
            m = KEYLINE.match(line)
            if m:
                if m.group(1) not in cur[1]:
                    cur[1][m.group(1)] = m.group(2)
                elif m.group(1) not in cur[2]:
                    cur[2].append(m.group(1))
    return claims, malformed


def freeze_rev(repo, rev, prereg):
    p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--reverse",
                 "--format=%H", rev, "--", prereg)
    ids = [x for x in p.stdout.decode("utf-8", "replace").split() if FULL40.match(x)]
    return ids[0] if p.returncode == 0 and ids else None


def dispatch_name(base):
    return "-dispatch" in base or ".ready" in base or base.endswith("-spec.json") \
        or base.endswith("-results.json")


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
            if dispatch_name(line.rsplit("/", 1)[-1]):
                first[line] = commit
    out = []
    for path, c in sorted(first.items()):
        if c == freeze or repo.is_ancestor(c, freeze):
            out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"
                        % (path, c[:12], freeze[:12])))
    return out


def check_path_sha(repo, rev, freeze, label, key, value, missing, digest_class, found):
    """Counter/Population: returns (freeze blob, path) or None."""
    m = PATH_SHA.match(value)
    path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)
    if not path:
        return None
    if repo.mode(freeze, path) == SYMLINK_MODE:
        found.append((label, key.upper() + "-SYMLINK", "%s is a symlink at freeze %s" % (path, freeze[:12])))
        return None
    at_freeze = repo.blob(freeze, path)
    if at_freeze is None:
        found.append((label, missing, "%s not present at freeze %s" % (path, freeze[:12])))
        return None
    if want is None:
        found.append((label, digest_class, "%s has no sha256=<64 hex> in %r" % (path, value)))
    elif digest(at_freeze) != want:
        found.append((label, digest_class, "%s at freeze hashes %s, stated %s"
                      % (path, digest(at_freeze), want)))
    at_rev = repo.blob(rev, path)
    if at_rev != at_freeze:
        found.append((label, "FROZEN-EDITED", "%s differs between freeze %s and %s"
                      % (path, freeze[:12], rev[:12])))
    return at_freeze, path


def evaluate(repo, rev, prereg, text, freeze):
    found = []
    claims, malformed = parse_claims(text)
    if not claims:
        found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    for n in malformed:
        found.append(("C0", "HEADING-MALFORMED", "line=%d" % n))
    for label, f, dups in claims:
        for key in dups:
            found.append((label, "KEY-DUPLICATE", key))
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


def check(root, prereg, rev_arg):
    """One full check; returns (exit code, finding lines, claim count). Raises Refusal."""
    if not os.path.isdir(root):
        raise Refusal("--root %s is not a directory" % root)
    if not FULL40.match(rev_arg):
        raise Refusal("--rev must be a full 40-hex commit id")
    repo = Repo(root)
    rev = repo.commit(rev_arg)
    if rev is None:
        raise Refusal("--rev %s does not resolve to a commit in %s" % (rev_arg, root))
    raw = repo.blob(rev, prereg)
    if raw is None:
        raise Refusal("%s is absent at %s" % (prereg, rev))
    freeze = freeze_rev(repo, rev, prereg)
    if freeze is None:
        raise Refusal("no commit reachable from %s adds %s" % (rev, prereg))
    n, found = evaluate(repo, rev, prereg, raw.decode("utf-8", "replace"), freeze)
    return n, sorted("FINDING %s %s %s" % f for f in found)


# ---------------------------------------------------------------- --selftest

# Digests are literals on purpose: a self-test that derived them with the code under test could not
# notice that code going wrong.
ST_COUNTER = "counter\n"
ST_COUNTER_SHA = "503fd72399326f90ecddf5660b4d2c90d6c3da0d2bbc2dead1f0ca926d9f8f3d"
ST_POP = "id\tname\n1\ta\n2\tb\n"
ST_POP_SHA = "33e4771e1b8afa673d0c9740d6ee9f1038fea417d79581573adb8ddc06e55256"
ST_ABC_SHA = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
ST_PREREG = ("# prereg\nRound: 42\n\n## C1 - claim\nBase: {base}\n"
             "Counter: census/c.py sha256=" + ST_COUNTER_SHA + "\n"
             "Population: census/p.tsv sha256=" + ST_POP_SHA + "\n"
             "Control: census/ctl.txt\nTarget: t\nKill: k\n")
ST_WAVE = ".ufo/waves/round-42/"
ST_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
          "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
          "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "selftest@example.invalid",
          "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "selftest@example.invalid"}

# name -> (scenario options, expected exit, expected sorted (claim, class) list)
ST_CASES = [
    ("clean", {}, 0, []),
    ("counter-digest-wrong", {"sub": ("c.py sha256=" + ST_COUNTER_SHA, "c.py sha256=" + "0" * 64)},
     1, [("C1", "COUNTER-DIGEST")]),
    ("population-digest", {"sub": ("p.tsv sha256=" + ST_POP_SHA, "p.tsv sha256=" + "1" * 64)},
     1, [("C1", "POPULATION-DIGEST")]),
    ("base-not-ancestor", {"side": True}, 1, [("C1", "BASE-NOT-ANCESTOR")]),
    ("base-unresolved", {"sub": ("Base: {base}", "Base: " + "0" * 40)}, 1, [("C1", "BASE-UNRESOLVED")]),
    ("field-missing", {"sub": ("Kill: k\n", "")}, 1, [("C1", "FIELD-MISSING")]),
    ("control-not-red", {"control": "EXIT=0\n"}, 1, [("C1", "CONTROL-NOT-RED")]),
    ("control-missing", {"no_control": True}, 1, [("C1", "CONTROL-MISSING")]),
    ("frozen-edited", {"edit": ("census/c.py", ST_COUNTER + "# edited\n")}, 1, [("C1", "FROZEN-EDITED")]),
    ("dispatch-before", {"pre": [ST_WAVE + "w1-dispatch.json"]}, 1, [("C0", "DISPATCH-BEFORE-FREEZE")]),
    ("dispatch-after", {"post": [ST_WAVE + "w1-dispatch.json"]}, 0, []),
    ("dispatch-widened", {"pre": [ST_WAVE + "w1-dispatch-attempts.txt", ST_WAVE + "w1.ready.dispatched",
                                  ST_WAVE + "d/w1-spec.json", ST_WAVE + "w1-results.json",
                                  ST_WAVE + "notes.md"]},
     1, [("C0", "DISPATCH-BEFORE-FREEZE")] * 4),
    ("key-duplicate", {"tail": "Kill: again\n"}, 1, [("C1", "KEY-DUPLICATE")]),
    ("heading-malformed", {"sub": ("## C1 - claim", "##C1 - claim")}, 1,
     [("C0", "HEADING-MALFORMED"), ("C0", "NO-CLAIMS")]),
    ("counter-symlink", {"counter_link": True}, 1, [("C1", "COUNTER-SYMLINK")]),
    ("population-symlink", {"population_link": True}, 1, [("C1", "POPULATION-SYMLINK")]),
]


def st_git(d, *args):
    p = subprocess.run(["git", "-C", d, "-c", "core.hooksPath=" + os.devnull, "-c", "commit.gpgsign=false"]
                       + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ST_ENV,
                       check=False, text=True)
    if p.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr.strip()))
    return p.stdout.strip()


def st_build(d, opt):
    """Builds one synthetic repository; returns (tip commit id, prereg path)."""
    os.makedirs(d)
    st_git(d, "init", "-q")
    st_git(d, "symbolic-ref", "HEAD", "refs/heads/main")
    if os.path.realpath(st_git(d, "rev-parse", "--show-toplevel")) != os.path.realpath(d):
        raise RuntimeError("fixture repository root mismatch")

    def put(rel, text):
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)

    def commit(msg):
        st_git(d, "add", "-A")
        st_git(d, "commit", "-q", "-m", msg)
        return st_git(d, "rev-parse", "HEAD")

    put("README", "base\n")
    base = commit("base")
    if opt.get("side"):
        st_git(d, "checkout", "-q", "-b", "side")
        put("side.txt", "side\n")
        base = commit("side")
        st_git(d, "checkout", "-q", "main")
    if opt.get("pre"):
        for rel in opt["pre"]:
            put(rel, "x\n")
        commit("early wave files")
    if opt.get("counter_link"):
        put("census/real-c.py", ST_COUNTER)
        os.symlink("real-c.py", os.path.join(d, "census/c.py"))
    else:
        put("census/c.py", ST_COUNTER)
    if opt.get("population_link"):
        put("census/real-p.tsv", ST_POP)
        os.symlink("real-p.tsv", os.path.join(d, "census/p.tsv"))
    else:
        put("census/p.tsv", ST_POP)
    if not opt.get("no_control"):
        put("census/ctl.txt", opt.get("control", "SUMMARY x\nEXIT=1\n"))
    text = ST_PREREG
    if "sub" in opt:
        text = text.replace(*opt["sub"])
    put("prereg.txt", text.replace("{base}", base) + opt.get("tail", ""))
    commit("freeze")
    for rel in opt.get("post", []):
        put(rel, "x\n")
    if opt.get("post"):
        commit("wave files after freeze")
    if opt.get("edit"):
        put(*opt["edit"])
        commit("edit after freeze")
    return st_git(d, "rev-parse", "HEAD"), "prereg.txt"


def st_run(d, tip, prereg):
    """Runs this tool's own main() in-process; returns (exit code, sorted [(claim, class)])."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(["--root", d, "--prereg", prereg, "--rev", tip])
    got = []
    for line in out.getvalue().splitlines():
        parts = line.split(" ", 3)
        if parts[0] == "FINDING" and len(parts) >= 3:
            got.append((parts[1], parts[2]))
    return code, sorted(got)


def selftest():
    results = []  # (name, ok, detail)
    scratch = tempfile.mkdtemp(prefix="souji-freeze-selftest-")
    try:
        results.append(("digest-known-answer", digest(b"abc") == ST_ABC_SHA, "sha256(abc)=" + digest(b"abc")))
        for n, (name, opt, want_exit, want) in enumerate(ST_CASES):
            try:
                d = os.path.join(scratch, "r%d" % n)
                tip, prereg = st_build(d, opt)
                code, got = st_run(d, tip, prereg)
                # the symlink / duplicate / malformed cases name their classes exactly; other cases too
                ok = code == want_exit and got == sorted(want)
                results.append((name, ok, "exit=%d findings=%s want exit=%d %s" % (code, got, want_exit, sorted(want))))
            except Exception as exc:  # a broken fixture or a broken tool is a failed case, not a crash
                results.append((name, False, "error: %s" % exc))
        try:
            d = os.path.join(scratch, "refuse")
            tip, prereg = st_build(d, {})
            with contextlib.redirect_stderr(io.StringIO()):
                code = main(["--root", d, "--prereg", "absent.txt", "--rev", tip])
            results.append(("refusal-absent-prereg", code == 2, "exit=%d want 2" % code))
        except Exception as exc:
            results.append(("refusal-absent-prereg", False, "error: %s" % exc))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    for name, ok, detail in results:
        if not ok:
            sys.stderr.write("SELFTEST FAIL %s: %s\n" % (name, detail))
    passed = sum(1 for r in results if r[1])
    print("SELFTEST cases=%d pass=%d fail=%d" % (len(results), passed, len(results) - passed))
    return 0 if passed == len(results) else 1


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
        n, lines = check(args.root, args.prereg, args.rev)
    except Refusal as exc:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % exc)
        return 2
    for line in lines:
        print(line)
    print("SUMMARY claims=%d findings=%d" % (n, len(lines)))
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
