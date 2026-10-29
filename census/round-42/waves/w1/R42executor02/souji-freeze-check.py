#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40
  python3 -B tools/souji-freeze-check.py --selftest

Reads the preregistration PATH as the blob at --rev (git object store only, never the work tree) and
prints `FINDING <claim> <CLASS> <detail>` per finding, sorted, then `SUMMARY claims=<n> findings=<m>`.
Exit 0 no findings, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...` on stderr).

Grammar: a claim block starts at a heading `## C<digits>` followed by a space or end of line and runs to
the next `## ` line; inside it a key line is `Key: value` at column 0 for Base, Counter, Population,
Control, Target, Kill. Counter and Population values are `<repo path> sha256=<64 hex>`. FREEZE-REV is
the oldest commit reachable from --rev that adds PATH. Finding classes: NO-CLAIMS, FIELD-MISSING,
FIELD-EMPTY, BASE-UNRESOLVED, BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-DIGEST, COUNTER-SYMLINK,
POPULATION-MISSING, POPULATION-DIGEST, POPULATION-SYMLINK, POPULATION-EMPTY, CONTROL-MISSING,
CONTROL-NOT-RED, FROZEN-EDITED, DISPATCH-BEFORE-FREEZE, KEY-DUPLICATE, HEADING-MALFORMED. Prereg-wide
findings carry claim label C0. A missing `Round:` line is `FIELD-MISSING C0 Round`, an empty value of any
key is `FIELD-EMPTY`, and repo paths may contain spaces (r41 hardening).

r42 additions: KEY-DUPLICATE (a key line repeated in one claim block; the duplicated key is not value-checked,
there is no first-wins reading), HEADING-MALFORMED (`##C1`, `## c1`, `## C 1`, `## C1x`: a `##` heading
that looks like a claim heading but is not one opens no claim and ends the open block), COUNTER-SYMLINK /
POPULATION-SYMLINK (git mode 120000 at FREEZE-REV: that finding alone, no digest comparison),
DISPATCH-BEFORE-FREEZE over every file under .ufo/waves/round-<N>/ whose basename contains `-dispatch` or
`.ready` or ends `-spec.json` / `-results.json`.

--selftest builds synthetic git repositories under $TMPDIR and runs this file's own check() (digest,
`git log --diff-filter` freeze detection and `git merge-base --is-ancestor` ancestry) over them, plus
known-answer and grammar table cases; prints `SELFTEST cases=<n> pass=<p> fail=<f>`, exit 0 iff fail=0.
Python stdlib only; read-only on --root.
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

FULL40 = re.compile(r"^[0-9a-f]{40}$")
CLAIM_HEAD = re.compile(r"^## C([0-9]+)(?: |$)")
LOOKALIKE = re.compile(r"^##(?!#)[ ]*[Cc][ ]*[0-9]")
KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")
PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")
ROUND = re.compile(r"^\ufeff?Round:[ \t]*(\d+)[ \t]*\r?$", re.M)
EXIT_LINE = re.compile(r"^EXIT=(\d+)$")
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")


class Refusal(Exception):
    pass


class Repo:
    def __init__(self, root, extra=None):
        self.root = root
        # r41 hardening: a whitelisted environment, so a caller-set GIT_DIR or GIT_* variable cannot
        # change a verdict; replace refs, mailmap and user config are not consulted.
        self.env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
                    "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                    "GIT_NO_REPLACE_OBJECTS": "1", "GIT_LITERAL_PATHSPECS": "1"}
        self.env.update(extra or {})

    def run(self, *args, stdin=None):
        try:
            return subprocess.run(["git", "-c", "core.quotePath=false", "-c", "log.mailmap=false",
                                   "-C", self.root] + list(args), input=stdin, stdout=subprocess.PIPE,
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
        """Git mode string of the tree entry PATH at rev, or None."""
        if "\x00" in path:
            return None
        for ent in self.run("ls-tree", "-z", rev, "--", path).stdout.split(b"\0"):
            meta, _, name = ent.partition(b"\t")
            if name.decode("utf-8", "replace") == path and meta.split():
                return meta.split()[0].decode()
        return None

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b).returncode == 0


def digest(data):
    return hashlib.sha256(data).hexdigest()


def is_dispatch_name(base):
    return "-dispatch" in base or ".ready" in base or base.endswith(("-spec.json", "-results.json"))


def parse_claims(text):
    """-> (claims [(label, {key: [values]})], malformed heading line numbers)."""
    claims, bad, cur = [], [], None
    for n, line in enumerate(text.lstrip("\ufeff").splitlines(), 1):
        m = CLAIM_HEAD.match(line)
        if m:
            cur = ("C" + m.group(1), {})
            claims.append(cur)
        elif LOOKALIKE.match(line):
            bad.append(n)
            cur = None
        elif line.startswith("## "):
            cur = None
        elif cur is not None:
            m = KEYLINE.match(line)
            if m:
                cur[1].setdefault(m.group(1), []).append(m.group(2))
    return claims, bad


def freeze_rev(repo, rev, prereg):
    p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--reverse",
                 "--format=%H", rev, "--", prereg)
    ids = [x for x in p.stdout.decode("utf-8", "replace").split() if FULL40.match(x)]
    return ids[0] if p.returncode == 0 and ids else None


def added_dispatch_files(repo, rev, tree):
    """{path: oldest adding commit} for dispatch-named files under TREE reachable from rev."""
    p = repo.run("log", "-z", "--diff-filter=A", "--no-renames", "--full-history", "--name-only",
                 "--format=%x01%H", rev, "--", tree)
    first, commit, head = {}, None, False
    if p.returncode != 0:
        return first
    for tok in p.stdout.decode("utf-8", "replace").split("\0"):
        if tok.startswith("\x01"):
            commit, head = tok[1:].strip(), True
            continue
        if head and tok.startswith("\n"):
            tok = tok[1:]
        head = False
        if tok and commit and is_dispatch_name(tok.rsplit("/", 1)[-1]):
            first[tok] = commit  # log is newest first: later entries are older and overwrite
    return first


def dispatch_findings(repo, rev, freeze, text):
    m = ROUND.search(text)
    if not m:
        return [("C0", "FIELD-MISSING", "Round")]
    out = []
    for path, c in sorted(added_dispatch_files(repo, rev, ".ufo/waves/round-%s/" % m.group(1)).items()):
        if c == freeze or repo.is_ancestor(c, freeze):
            out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"
                        % (path, c[:12], freeze[:12])))
    return out


def check_path_sha(repo, rev, freeze, label, name, value, found):
    """Counter/Population: the freeze blob and path, or None (finding appended)."""
    m = PATH_SHA.match(value)
    path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)
    if not path:
        return None
    if repo.mode(freeze, path) == "120000":
        found.append((label, name + "-SYMLINK", "%s is a symlink at freeze %s" % (path, freeze[:12])))
        return None
    at_freeze = repo.blob(freeze, path)
    if at_freeze is None:
        found.append((label, name + "-MISSING", "%s not present at freeze %s" % (path, freeze[:12])))
        return None
    got = digest(at_freeze)
    if want is None:
        found.append((label, name + "-DIGEST", "%s has no sha256=<64 hex> in %r" % (path, value)))
    elif got != want:
        found.append((label, name + "-DIGEST", "%s at freeze hashes %s, stated %s" % (path, got, want)))
    if repo.blob(rev, path) != at_freeze:
        found.append((label, "FROZEN-EDITED", "%s differs between freeze %s and %s"
                      % (path, freeze[:12], rev[:12])))
    return at_freeze, path


def base_finding(repo, label, base, freeze):
    resolved = repo.commit(base) if FULL40.match(base) else None
    if resolved is None:
        return [(label, "BASE-UNRESOLVED", base)]
    if resolved == freeze or not repo.is_ancestor(resolved, freeze):
        return [(label, "BASE-NOT-ANCESTOR", "%s is not a strict ancestor of freeze %s" % (base, freeze[:12]))]
    return []


def control_finding(repo, label, path, freeze):
    blob = repo.blob(freeze, path)
    if blob is None:
        return [(label, "CONTROL-MISSING", "%s not present at freeze %s" % (path, freeze[:12]))]
    lines = [x.strip() for x in blob.decode("utf-8", "replace").splitlines() if x.strip()]
    m = EXIT_LINE.match(lines[-1]) if lines else None
    if m and int(m.group(1)) != 0:
        return []
    return [(label, "CONTROL-NOT-RED", "%s last line %r is not EXIT=<nonzero>" % (path, lines[-1] if lines else ""))]


def claim_findings(repo, rev, freeze, label, fields):
    found = []
    vals = {}
    for key in KEYS:
        v = fields.get(key, [])
        if not v:
            found.append((label, "FIELD-MISSING", key))
        elif len(v) > 1:
            found.append((label, "KEY-DUPLICATE", key))
        elif not v[0]:
            found.append((label, "FIELD-EMPTY", key))
        else:
            vals[key] = v[0]
    if "Base" in vals:
        found += base_finding(repo, label, vals["Base"], freeze)
    if "Counter" in vals:
        check_path_sha(repo, rev, freeze, label, "COUNTER", vals["Counter"], found)
    if "Population" in vals:
        got = check_path_sha(repo, rev, freeze, label, "POPULATION", vals["Population"], found)
        if got:
            n = len([x for x in got[0].decode("utf-8", "replace").splitlines() if x.strip()])
            if n < 2:
                found.append((label, "POPULATION-EMPTY", "%s has %d non-blank line(s)" % (got[1], n)))
    if "Control" in vals:
        found += control_finding(repo, label, vals["Control"], freeze)
    return found


def evaluate(repo, rev, prereg, text, freeze):
    claims, bad = parse_claims(text)
    found = [("C0", "HEADING-MALFORMED", "line=%d" % n) for n in bad]
    if not claims:
        found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    for label, fields in claims:
        found += claim_findings(repo, rev, freeze, label, fields)
    return len(claims), found + dispatch_findings(repo, rev, freeze, text)


def check(root, prereg, rev):
    """The whole CLI check. -> (exit code, FINDING lines, SUMMARY line or REFUSAL message)."""
    try:
        if not os.path.isdir(root):
            raise Refusal("--root %s is not a directory" % root)
        if not FULL40.match(rev):
            raise Refusal("--rev must be a full 40-hex commit id")
        repo = Repo(root)
        tip = repo.commit(rev)
        if tip is None:
            raise Refusal("--rev %s does not resolve to a commit in %s" % (rev, root))
        raw = repo.blob(tip, prereg)
        if raw is None:
            raise Refusal("%s is absent at %s" % (prereg, tip))
        freeze = freeze_rev(repo, tip, prereg)
        if freeze is None:
            raise Refusal("no commit reachable from %s adds %s" % (tip, prereg))
        n, found = evaluate(repo, tip, prereg, raw.decode("utf-8", "replace"), freeze)
    except Refusal as exc:
        return 2, [], str(exc)
    lines = sorted("FINDING %s %s %s" % f for f in found)
    return (1 if lines else 0), lines, "SUMMARY claims=%d findings=%d" % (n, len(lines))


# ---------------------------------------------------------------- self-test

ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"  # sha256 of b"abc"
POP2 = "911169ddaaf146aff539f58c26c489af3b892dff0fe283c1c264c65ae5aa59a2"  # sha256 of b"a\nb\n"
POP1 = "87428fc522803d31065e7bce3cf03fe475096631e5e07bbd7a0fde60c4cf25c7"  # sha256 of b"a\n"
WAVE = ".ufo/waves/round-9/"
PREREG = """Round: 9

## C1 - one
Base: {BASE}
Counter: c.py sha256={CSHA}
Population: pop.tsv sha256={PSHA}
Control: ctl.txt
Target: t
Kill: k
"""
IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
         "GIT_COMMITTER_EMAIL": "t@t", "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
         "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}


def build(tmp, name, spec):
    """One synthetic repo from a spec dict -> (dir, tip id). Keys: vars, drop, sub, extra, base, freeze,
    tip (path -> text; None deletes), link (path -> symlink target at freeze)."""
    d = os.path.join(tmp, name)
    os.makedirs(d)
    repo = Repo(d, IDENT)

    def git(*a, stdin=None):
        p = repo.run(*a, stdin=stdin)
        if p.returncode:
            raise RuntimeError("git %s: %s" % (a[0], p.stderr.decode("utf-8", "replace")))
        return p.stdout.decode("utf-8", "replace").strip()

    def put(files):
        for path, body in files.items():
            full = os.path.join(d, path)
            if os.path.lexists(full):
                os.remove(full)
            if body is not None:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "w", newline="") as fh:
                    fh.write(body)

    def commit(msg):
        git("add", "-A", "-f")
        git("commit", "-q", "--no-verify", "--allow-empty", "-m", msg)
        return git("rev-parse", "HEAD")

    git("init", "-q", "--template=")
    if os.path.realpath(git("rev-parse", "--show-toplevel")) != os.path.realpath(d):
        raise RuntimeError("fixture %s is not its own repository" % d)
    orphan = git("commit-tree", git("write-tree"), "-m", "orphan")
    put(dict({"README": "x\n"}, **spec.get("base", {})))
    base = commit("base")
    var = {"BASE": base, "CSHA": ABC, "PSHA": POP2}
    var.update({k: orphan if v == "@orphan" else v for k, v in spec.get("vars", {}).items()})
    text = PREREG
    for key in spec.get("drop", ()):
        text = re.sub(r"(?m)^%s:.*\n" % key, "", text)
    for old, new in spec.get("sub", ()):
        text = text.replace(old, new)
    text = (text + spec.get("extra", "")).format(**var)
    put(dict({"p.txt": text, "c.py": "abc", "pop.tsv": "a\nb\n", "ctl.txt": "x\nEXIT=1\n"}, **spec.get("freeze", {})))
    for path, target in spec.get("link", {}).items():
        os.remove(os.path.join(d, path))
        os.symlink(target, os.path.join(d, path))
    commit("freeze")
    put(dict({WAVE + "notes.md": "n\n"}, **spec.get("tip", {})))
    return d, commit("tip")


def run_case(tmp, name, spec, rc, want):
    d, tip = build(tmp, name, spec)
    got_rc, lines, tail = check(d, spec.get("prereg", "p.txt"), spec.get("rev", tip))
    got = sorted("%s:%s" % tuple(x.split(" ", 3)[1:3]) for x in lines)
    if got_rc == rc and got == sorted(want):
        return None
    return "rc=%s findings=%s tail=%s" % (got_rc, got, tail)


def d_file(name):
    return {WAVE + name: "{}"}


CASES = (
    ("clean", {}, 0, []),
    ("no-claims", {"sub": [("## C1 - one", "## one")]}, 1, ["C0:NO-CLAIMS"]),
    ("missing-key", {"drop": ["Base"]}, 1, ["C1:FIELD-MISSING"]),
    ("empty-key", {"sub": [("Target: t", "Target:")]}, 1, ["C1:FIELD-EMPTY"]),
    ("base-unresolved", {"vars": {"BASE": "0" * 40}}, 1, ["C1:BASE-UNRESOLVED"]),
    ("base-unrelated", {"vars": {"BASE": "@orphan"}}, 1, ["C1:BASE-NOT-ANCESTOR"]),
    ("counter-absent", {"freeze": {"c.py": None}}, 1, ["C1:COUNTER-MISSING"]),
    ("counter-digest", {"vars": {"CSHA": "0" * 64}}, 1, ["C1:COUNTER-DIGEST"]),
    ("population-absent", {"freeze": {"pop.tsv": None}}, 1, ["C1:POPULATION-MISSING"]),
    ("population-digest", {"vars": {"PSHA": "0" * 64}}, 1, ["C1:POPULATION-DIGEST"]),
    ("population-thin", {"freeze": {"pop.tsv": "a\n"}, "vars": {"PSHA": POP1}}, 1, ["C1:POPULATION-EMPTY"]),
    ("control-absent", {"freeze": {"ctl.txt": None}}, 1, ["C1:CONTROL-MISSING"]),
    ("control-green", {"freeze": {"ctl.txt": "x\nEXIT=0\n"}}, 1, ["C1:CONTROL-NOT-RED"]),
    ("counter-moved", {"tip": {"c.py": "abd"}}, 1, ["C1:FROZEN-EDITED"]),
    ("population-moved", {"tip": {"pop.tsv": "a\nb\nc\n"}}, 1, ["C1:FROZEN-EDITED"]),
    ("claim-two-bare", {"extra": "\n## C2 - two\nBase: {BASE}\n"}, 1, ["C2:FIELD-MISSING"] * 5),
    ("dup-key-differs", {"sub": [("Base: {BASE}", "Base: {BASE}\nBase: 0")]}, 1, ["C1:KEY-DUPLICATE"]),
    ("dup-key-same", {"sub": [("Target: t", "Target: t\nTarget: t")]}, 1, ["C1:KEY-DUPLICATE"]),
    ("heading-glued", {"extra": "\n##C2 - two\n"}, 1, ["C0:HEADING-MALFORMED"]),
    ("heading-lower", {"extra": "\n## c2\n"}, 1, ["C0:HEADING-MALFORMED"]),
    ("heading-split", {"extra": "\n## C 2\n"}, 1, ["C0:HEADING-MALFORMED"]),
    ("heading-tail", {"extra": "\n## C2x\n"}, 1, ["C0:HEADING-MALFORMED"]),
    ("heading-two-bad", {"extra": "\n## c2\n## C 3\n"}, 1, ["C0:HEADING-MALFORMED"] * 2),
    ("heading-ok-prose", {"extra": "\n### C2x\n## Cx\n## Notes\n"}, 0, []),
    ("dispatch-old", {"base": d_file("w1-dispatch.json")}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
    ("dispatch-attempts", {"base": d_file("w1-dispatch-attempts.txt")}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
    ("dispatch-ready-deep", {"base": d_file("a/w1.ready.dispatched")}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
    ("dispatch-spec", {"base": d_file("w1-spec.json")}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
    ("dispatch-results", {"freeze": d_file("w1-results.json")}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
    ("dispatch-spaced", {"base": d_file("w 1/x -dispatch.json")}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
    ("dispatch-later", {"tip": dict(d_file("w1-dispatch.json"), **d_file("w1-spec.json"))}, 0, []),
    ("dispatch-notes", {"base": d_file("notes.md")}, 0, []),
    ("counter-link", {"link": {"c.py": "pop.tsv"}}, 1, ["C1:COUNTER-SYMLINK"]),
    ("population-link", {"link": {"pop.tsv": "c.py"}}, 1, ["C1:POPULATION-SYMLINK"]),
    ("rev-unknown", {"rev": "f" * 40}, 2, []),
    ("prereg-absent", {"prereg": "nope.txt"}, 2, []),
)

# (heading line, parsed as: "claim" | "bad" | "none")
HEADINGS = (("## C1", "claim"), ("## C12 - t", "claim"), ("##C1", "bad"), ("## c1", "bad"), ("## C 1", "bad"),
            ("## C1x", "bad"), ("## C1:", "bad"), ("### C1", "none"), ("## Cx", "none"), ("# C1", "none"))


def heading_kind(line):
    claims, bad = parse_claims(line + "\nBase: z\n")
    return "claim" if claims else "bad" if bad else "none"


def selftest():
    tmp = tempfile.mkdtemp(prefix="freeze-selftest-")
    results = [("digest-known-answer", None if digest(b"abc") == ABC else "digest(b'abc')=%s" % digest(b"abc"))]
    try:
        for line, want in HEADINGS:
            got = heading_kind(line)
            results.append(("grammar %r" % line, None if got == want else "got %s want %s" % (got, want)))
        for n, (name, spec, rc, want) in enumerate(CASES):
            try:
                err = run_case(tmp, "c%d" % n, spec, rc, want)
            except Exception as exc:  # a crash is a failed case, never a pass
                err = "crash %r" % (exc,)
            results.append((name, err))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for name, err in results:
        if err:
            sys.stderr.write("SELFTEST FAIL %s: %s\n" % (name, err))
    bad = sum(1 for _, e in results if e)
    print("SELFTEST cases=%d pass=%d fail=%d" % (len(results), len(results) - bad, bad))
    return 1 if bad else 0


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
    rc, lines, tail = check(args.root, args.prereg, args.rev)
    if rc == 2:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % tail)
        return 2
    for line in lines:
        print(line)
    print(tail)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
