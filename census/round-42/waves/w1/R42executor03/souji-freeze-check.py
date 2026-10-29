#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40
  python3 -B tools/souji-freeze-check.py --selftest

Reads the preregistration PATH as the blob at --rev (git object store only, never the work tree) and
prints `FINDING <claim> <CLASS> <detail>` per finding, sorted, then `SUMMARY claims=<n> findings=<m>`.
Exit 0 no findings, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...` on stderr).

Grammar: a claim block starts at `## C<digits>` (followed by a space or end of line) and runs to the next
`## ` line; inside it a key line is `Key: value` at column 0 for Base, Counter, Population, Control, Target,
Kill. Counter and Population values are `<repo path> sha256=<64 hex>`. FREEZE-REV is the oldest commit
reachable from --rev that adds PATH. Finding classes: NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY, BASE-UNRESOLVED,
BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-DIGEST, POPULATION-MISSING, POPULATION-DIGEST, POPULATION-EMPTY,
CONTROL-MISSING, CONTROL-NOT-RED, FROZEN-EDITED, DISPATCH-BEFORE-FREEZE (r41) and, new in r42, KEY-DUPLICATE,
HEADING-MALFORMED, COUNTER-SYMLINK, POPULATION-SYMLINK. Prereg-wide findings carry claim label C0. A missing
`Round:` line is reported as `FIELD-MISSING C0 Round` (the dispatch check cannot run without it), an empty
value of any key is `FIELD-EMPTY`, and repo paths may contain spaces (r41 wave-2 hardening, R41w2critic01).

r42 rules (exactly these, on top of r41):
  KEY-DUPLICATE        a key line seen more than once in one claim block (identical value or not): one
                       finding per duplicated key, detail = the key. The value of a duplicated key is
                       ambiguous, so no other check reads it (no first-wins reading).
  HEADING-MALFORMED    a column-0 line that starts `##` (not `###`), optional spaces, `C`/`c`, optional
                       spaces, a digit, and is not `## C<digits>` + space/end of line: `##C1`, `## c1`,
                       `## C 1`, `## C1x`. Claim label C0, one finding per line (detail `line=<n>`); the
                       line opens no claim and closes the block it interrupts.
  COUNTER-SYMLINK /    the Counter / Population path is a symlink (git mode 120000) at FREEZE-REV: that
  POPULATION-SYMLINK   finding alone, no digest comparison (the link text is not the counter).
  DISPATCH-BEFORE-FREEZE covers every file under `.ufo/waves/round-<N>/` (any depth) whose basename contains
                       `-dispatch` or `.ready`, or ends `-spec.json` or `-results.json`, first added by
                       FREEZE-REV or an ancestor of it.

Robustness (r41 E1 and r42): git runs with a whitelisted environment (no GIT_DIR, no replace refs, no
mailmap, no user config), `core.quotePath=false`, `--literal-pathspecs`, NUL-separated plumbing output
(spaces, quotes, backslashes, non-ASCII bytes in paths); paths are resolved with `ls-tree` and an exact
name match, so a directory, submodule, glob or `./`-prefixed path reads as missing; a leading BOM and CRLF
line ends are tolerated; a NUL inside a path reads as missing. git failures are COULD-NOT-EVALUATE, never
a silent clean.

`--selftest` builds synthetic repositories under $TMPDIR (every git call names `-C`, identity through the
environment, nothing outside the temp dir is read or written), drives this file's own digest, freeze
detection (`git log --diff-filter=A`) and ancestry (`git merge-base --is-ancestor`) code over them and
prints `SELFTEST cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0. The digest cases compare against
hard-coded SHA-256 constants, so a broken digest cannot agree with itself.
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
HEADER = re.compile(r"^## C([0-9]+)(?: |$)")
HEADLIKE = re.compile(r"^##(?!#) *[Cc] *[0-9]")
KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")
PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")
ROUND = re.compile(r"^\ufeff?Round:[ \t]*([0-9]+)[ \t]*\r?$", re.M)
EXIT_LINE = re.compile(r"^EXIT=(\d+)$")
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")


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
            return subprocess.run(["git", "--literal-pathspecs", "-c", "core.quotePath=false", "-c",
                                   "log.mailmap=false", "-C", self.root] + list(args),
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env, check=False)
        except (OSError, ValueError) as exc:
            raise Refusal("cannot run git: %s" % exc)

    def commit(self, rev):
        """Full commit id for rev, or None."""
        p = self.run("rev-parse", "--verify", "-q", rev + "^{commit}")
        out = p.stdout.decode("utf-8", "replace").strip()
        return out if p.returncode == 0 and FULL40.match(out) else None

    def entry(self, rev, path):
        """(kind, data) of the tree entry named exactly `path` at rev: ('blob'|'symlink', bytes), or
        (None, None) for a missing path, a directory, a submodule, a path with NUL, or a non-exact name."""
        if not path or "\x00" in path:
            return None, None
        pb = path.encode("utf-8", "surrogateescape")
        p = self.run("ls-tree", "-z", rev, "--", pb)
        if p.returncode != 0:
            return None, None
        for rec in p.stdout.split(b"\x00"):
            meta, tab, name = rec.partition(b"\t")
            if not tab or name != pb:
                continue
            parts = meta.split(b" ")
            if len(parts) != 3 or parts[1] != b"blob":
                return None, None
            kind = {b"100644": "blob", b"100755": "blob", b"120000": "symlink"}.get(parts[0])
            if kind is None:
                return None, None
            q = self.run("cat-file", "blob", parts[2].decode("ascii", "replace"))
            return (kind, q.stdout) if q.returncode == 0 else (None, None)
        return None, None

    def blob(self, rev, path):
        return self.entry(rev, path)[1]

    def is_ancestor(self, a, b):
        rc = self.run("merge-base", "--is-ancestor", a, b).returncode
        if rc in (0, 1):
            return rc == 0
        raise Refusal("git merge-base --is-ancestor %s %s failed (exit %d)" % (a[:12], b[:12], rc))


def parse_claims(text):
    """-> (claims [(label, {key: [values...]})], malformed heading line numbers)"""
    claims = []
    bad = []
    cur = None
    for n, line in enumerate(text.splitlines(), 1):
        m = HEADER.match(line)
        if m:
            cur = ("C" + m.group(1), {})
            claims.append(cur)
            continue
        if HEADLIKE.match(line):
            bad.append(n)
            cur = None
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur is not None:
            m = KEYLINE.match(line)
            if m:
                cur[1].setdefault(m.group(1), []).append(m.group(2))
    return claims, bad


def freeze_rev(repo, rev, prereg):
    p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--reverse",
                 "--format=%H", rev, "--", prereg)
    ids = [x for x in p.stdout.decode("utf-8", "replace").split() if FULL40.match(x)]
    return ids[0] if p.returncode == 0 and ids else None


def is_dispatch_name(base):
    return "-dispatch" in base or ".ready" in base or base.endswith("-spec.json") or base.endswith("-results.json")


def dispatch_findings(repo, rev, freeze, text):
    m = ROUND.search(text)
    if not m:
        # r41 wave-2 hardening (R41w2critic01 D1/D10): without a Round line the dispatch
        # check cannot run; say so instead of reading clean.
        return [("C0", "FIELD-MISSING", "Round")]
    tree = ".ufo/waves/round-%s/" % m.group(1)
    p = repo.run("log", "-z", "--diff-filter=A", "--no-renames", "--full-history", "--name-only",
                 "--format=%x01%H", rev, "--", tree)
    if p.returncode != 0:
        raise Refusal("git log over %s failed (exit %d)" % (tree, p.returncode))
    first = {}  # path -> oldest adding commit (log is newest first, so later entries overwrite)
    commit = None
    tb = tree.encode("ascii")
    for tok in p.stdout.split(b"\x00"):
        if tok.startswith(b"\x01"):
            commit = tok[1:].decode("ascii", "replace").strip()
        elif commit and tok.lstrip(b"\n").startswith(tb):
            path = tok.lstrip(b"\n").decode("utf-8", "replace")
            if is_dispatch_name(path.rsplit("/", 1)[-1]) and FULL40.match(commit):
                first[path] = commit
    out = []
    for path, c in sorted(first.items()):
        if c == freeze or repo.is_ancestor(c, freeze):
            out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"
                        % (path, c[:12], freeze[:12])))
    return out


def check_path_sha(repo, rev, freeze, label, value, missing, digest_class, symlink, found):
    """Counter/Population: returns (freeze blob, path) or None."""
    m = PATH_SHA.match(value)
    path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)
    if not path:
        return None
    kind, at_freeze = repo.entry(freeze, path)
    if kind == "symlink":
        found.append((label, symlink, "%s is a symlink at freeze %s" % (path, freeze[:12])))
        return None
    if at_freeze is None:
        found.append((label, missing, "%s not present at freeze %s" % (path, freeze[:12])))
        return None
    got = digest(at_freeze)
    if want is None:
        found.append((label, digest_class, "%s has no sha256=<64 hex> in %r" % (path, value)))
    elif got != want:
        found.append((label, digest_class, "%s at freeze hashes %s, stated %s" % (path, got, want)))
    if repo.entry(rev, path) != (kind, at_freeze):
        found.append((label, "FROZEN-EDITED", "%s differs between freeze %s and %s"
                      % (path, freeze[:12], rev[:12])))
    return at_freeze, path


def evaluate(repo, rev, prereg, text, freeze):
    found = []
    claims, bad = parse_claims(text)
    for n in bad:
        found.append(("C0", "HEADING-MALFORMED", "line=%d" % n))
    if not claims:
        found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    for label, fields in claims:
        for key in KEYS:
            if key not in fields:
                found.append((label, "FIELD-MISSING", key))
            elif len(fields[key]) > 1:
                found.append((label, "KEY-DUPLICATE", key))
        f = {k: v[0] for k, v in fields.items() if len(v) == 1}
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
            check_path_sha(repo, rev, freeze, label, f["Counter"],
                           "COUNTER-MISSING", "COUNTER-DIGEST", "COUNTER-SYMLINK", found)
        if f.get("Population"):
            got = check_path_sha(repo, rev, freeze, label, f["Population"],
                                 "POPULATION-MISSING", "POPULATION-DIGEST", "POPULATION-SYMLINK", found)
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


def run_check(root, prereg, rev):
    """-> (exit code, [FINDING line...], SUMMARY line or None, refusal text or None)"""
    try:
        if not os.path.isdir(root):
            raise Refusal("--root %s is not a directory" % root)
        if not FULL40.match(rev):
            raise Refusal("--rev must be a full 40-hex commit id")
        repo = Repo(root)
        full = repo.commit(rev)
        if full is None:
            raise Refusal("--rev %s does not resolve to a commit in %s" % (rev, root))
        raw = repo.blob(full, prereg)
        if raw is None:
            raise Refusal("%s is absent at %s" % (prereg, full))
        freeze = freeze_rev(repo, full, prereg)
        if freeze is None:
            raise Refusal("no commit reachable from %s adds %s" % (full, prereg))
        text = raw.decode("utf-8", "replace").lstrip("\ufeff")
        n, found = evaluate(repo, full, prereg, text, freeze)
    except Refusal as exc:
        return 2, [], None, str(exc)
    lines = sorted("FINDING %s %s %s" % f for f in found)
    return (1 if lines else 0), lines, "SUMMARY claims=%d findings=%d" % (n, len(lines)), None


# ---------------------------------------------------------------------------------------------------
# --selftest: synthetic repositories, this file's own checks.

DIG_COUNTER = "d93aae255efa51fbf4ffeffd55cb6307b2719ac0bec50a5277cf968caa2ce486"  # sha256(COUNTER)
DIG_POP = "1e4760070565b4a15d2486243582fbfd3fddb786b71b9a8aa62699052da08817"      # sha256(POP)
DIG_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"      # sha256(b"abc")
COUNTER = b"counter body\n"
POP = b"id\tvalue\nm1\t1\n"
CONTROL = b"run\nEXIT=1\n"
PREREG = "census/round-7/preregistration.txt"
WAVES = ".ufo/waves/round-7/"
DEFAULT_FILES = {"census/c.py": COUNTER, "census/p.tsv": POP, "census/ctl.txt": CONTROL}


def _keys(ctx, over):
    vals = [("Base", ctx["base"]), ("Counter", "census/c.py sha256=" + DIG_COUNTER),
            ("Population", "census/p.tsv sha256=" + DIG_POP), ("Control", "census/ctl.txt"),
            ("Target", "target"), ("Kill", "kill")]
    out = []
    for k, v in vals:
        if k in over:
            v = over[k]
        for x in (v if isinstance(v, list) else [v]):
            if callable(x):
                x = x(ctx)
            if x is not None:
                out.append("%s: %s" % (k, x))
    return "\n".join(out) + "\n"


def std(head="## C1 - one", after="", prefix="Round: 7\nLane: synthetic\n\n", **over):
    def build(ctx):
        a = after(ctx) if callable(after) else after
        return prefix + head + "\n" + _keys(ctx, over) + a
    return build


def second(head="## C2 - two", **over):
    return lambda ctx: "\n" + head + "\n" + _keys(ctx, over)


def _case(name, code, finds, **kw):
    kw.update(name=name, code=code, finds=finds)
    return kw


def _dispatch(name, code, finds, path, where="pre"):
    return _case(name, code, finds, **{where: [{WAVES + path: b"{}\n"}]} if where != "files" else
                 {"files": {WAVES + path: b"{}\n"}})


def _cases():
    base = lambda c: c["base"]
    orphan = lambda c: c["orphan"]
    DBF = ["C0:DISPATCH-BEFORE-FREEZE"]
    cs = [
        _case("digest-known-answer", None, None),
        _case("clean", 0, []),
        _case("clean-dispatch-after", 0, [], post=[{WAVES + "w1-dispatch.json": b"{}\n"}]),
        _case("clean-crlf", 0, [], text=lambda t: t.replace("\n", "\r\n")),
        _case("clean-bom", 0, [], text=lambda t: "\ufeff" + t),
        _case("clean-bom-crlf", 0, [], text=lambda t: "\ufeff" + t.replace("\n", "\r\n")),
        _case("clean-key-trailing-space", 0, [], text=lambda t: t.replace("\n", " \t\n")),
        _case("clean-heading-trailing-space", 0, [], text=lambda t: t.replace("## C1 - one", "## C1 - one  ")),
        _case("clean-invalid-utf8", 0, [], body=lambda c: std()(c).encode() + b"note \xff\xfe\n"),
        _case("clean-h3-and-h4", 0, [], body=std(after="### C9 sub\n#### C8 sub\n")),
        _case("clean-prose-heading", 0, [], body=std(after="## Conclusion\n## Cats\n")),
        _case("clean-hostile-env", 0, [], env={"GIT_DIR": "/nonexistent/x", "GIT_WORK_TREE": "/nonexistent",
                                               "GIT_INDEX_FILE": "/nonexistent/i", "GIT_NO_REPLACE_OBJECTS": "0"}),
        _case("no-claims", 1, ["C0:NO-CLAIMS"], body=lambda c: "Round: 7\nnothing here\n"),
        _case("no-round", 1, ["C0:FIELD-MISSING"], body=std(prefix="Lane: synthetic\n\n")),
        _case("field-missing-base", 1, ["C1:FIELD-MISSING"], body=std(Base=None)),
        _case("field-missing-kill", 1, ["C1:FIELD-MISSING"], body=std(Kill=None)),
        _case("field-empty-target", 1, ["C1:FIELD-EMPTY"], body=std(Target="")),
        _case("base-unresolved", 1, ["C1:BASE-UNRESOLVED"], body=std(Base="0" * 40)),
        _case("base-short", 1, ["C1:BASE-UNRESOLVED"], body=std(Base=lambda c: c["base"][:12])),
        _case("base-not-ancestor", 1, ["C1:BASE-NOT-ANCESTOR"], body=std(Base=orphan)),
        _case("counter-missing", 1, ["C1:COUNTER-MISSING"],
              body=std(Counter="census/nope.py sha256=" + DIG_COUNTER)),
        _case("counter-digest", 1, ["C1:COUNTER-DIGEST"], body=std(Counter="census/c.py sha256=" + "a" * 64)),
        _case("counter-no-sha", 1, ["C1:COUNTER-DIGEST"], body=std(Counter="census/c.py")),
        _case("counter-directory", 1, ["C1:COUNTER-MISSING"], body=std(Counter="census sha256=" + DIG_COUNTER)),
        _case("counter-dot-slash", 1, ["C1:COUNTER-MISSING"],
              body=std(Counter="./census/c.py sha256=" + DIG_COUNTER)),
        _case("counter-glob-literal", 1, ["C1:COUNTER-MISSING"],
              body=std(Counter="census/c*.py sha256=" + DIG_COUNTER)),
        _case("counter-nul-path", 1, ["C1:COUNTER-MISSING"],
              body=lambda c: std()(c).encode().replace(b"census/c.py", b"census/c\x00.py")),
        _case("population-missing", 1, ["C1:POPULATION-MISSING"],
              body=std(Population="census/nope.tsv sha256=" + DIG_POP)),
        _case("population-digest", 1, ["C1:POPULATION-DIGEST"],
              body=std(Population="census/p.tsv sha256=" + "b" * 64)),
        _case("population-empty", 1, ["C1:POPULATION-EMPTY"], files={"census/p.tsv": b"header-only\n\n"},
              body=std(Population=lambda c: "census/p.tsv sha256=" + digest(b"header-only\n\n"))),
        _case("control-missing", 1, ["C1:CONTROL-MISSING"], body=std(Control="census/none.txt")),
        _case("control-not-red", 1, ["C1:CONTROL-NOT-RED"], files={"census/ctl.txt": b"EXIT=0\n"}),
        _case("control-crlf-red", 0, [], files={"census/ctl.txt": b"log\r\nEXIT=3\r\n\r\n"}),
        _case("frozen-edited-counter", 1, ["C1:FROZEN-EDITED"], post=[{"census/c.py": b"changed\n"}]),
        _case("frozen-edited-population", 1, ["C1:FROZEN-EDITED"], post=[{"census/p.tsv": POP + b"x\t2\n"}]),
        _case("frozen-deleted-counter", 1, ["C1:FROZEN-EDITED"], post=[{"census/c.py": None}]),
        _case("frozen-counter-became-symlink", 1, ["C1:FROZEN-EDITED"],
              post=[{"census/c.py": None}], postlinks={"census/c.py": "p.tsv"}),
        _case("dispatch-before-freeze", 1, DBF, pre=[{WAVES + "w1-dispatch.json": b"{}\n"}]),
        _dispatch("dispatch-spec-before", 1, DBF, "w1-spec.json"),
        _dispatch("dispatch-attempts-before", 1, DBF, "w1-dispatch-attempts.txt"),
        _dispatch("dispatch-dispatched-before", 1, DBF, "w1.ready.dispatched"),
        _dispatch("dispatch-ready-before", 1, DBF, "w1.ready"),
        _dispatch("dispatch-results-before", 1, DBF, "w1-results.json"),
        _dispatch("dispatch-nested-before", 1, DBF, "w1/seat/deep/x.ready"),
        _dispatch("dispatch-spaced-quoted-before", 1, DBF, 'w 1/"q"\\b x-dispatch.json'),
        _dispatch("dispatch-nonascii-before", 1, DBF, "w1/\u00e9\u4e2d.ready"),
        _dispatch("dispatch-same-commit-as-freeze", 1, DBF, "w1-dispatch.json", where="files"),
        _dispatch("dispatch-notes-before", 0, [], "notes.md"),
        _dispatch("dispatch-contains-before", 1, DBF, "w1-dispatcher-notes.md"),
        _dispatch("dispatch-near-name-before", 0, [], "w1-dispatc.md"),
        _dispatch("dispatch-ready-substring-no", 0, [], "w1-already.md"),
        _case("dispatch-other-round-before", 0, [], pre=[{".ufo/waves/round-8/w1-dispatch.json": b"{}\n",
                                                          ".ufo/waves/round-70/x.ready": b"x\n"}]),
        _case("dispatch-two-before", 1, DBF * 2,
              pre=[{WAVES + "w1-dispatch.json": b"{}\n"}, {WAVES + "w1-spec.json": b"{}\n"}]),
        _case("dispatch-names-after", 0, [],
              post=[{WAVES + "w1-spec.json": b"{}\n", WAVES + "w1.ready.dispatched": b"x\n",
                     WAVES + "w1-results.json": b"{}\n", WAVES + "w1/a b.ready": b"x\n"}]),
        _case("two-claims-one-bad", 1, ["C2:FIELD-MISSING"], body=std(after=second(Kill=None))),
        _case("two-claims-clean", 0, [], body=std(after=second())),
        _case("dup-base-differs", 1, ["C1:KEY-DUPLICATE"], body=std(Base=[base, orphan])),
        _case("dup-counter-identical", 1, ["C1:KEY-DUPLICATE"],
              body=std(Counter=["census/c.py sha256=" + DIG_COUNTER] * 2)),
        _case("dup-counter-bad-second", 1, ["C1:KEY-DUPLICATE"],
              body=std(Counter=["census/c.py sha256=" + DIG_COUNTER, "census/x.py sha256=" + "c" * 64])),
        _case("dup-target", 1, ["C1:KEY-DUPLICATE"], body=std(Target=["t1", "t2"])),
        _case("dup-empty-then-value", 1, ["C1:KEY-DUPLICATE"], body=std(Target=["", "t"])),
        _case("dup-two-keys", 1, ["C1:KEY-DUPLICATE"] * 2, body=std(Kill=["a", "b"], Target=["a", "b", "c"])),
        _case("dup-only-in-second-claim", 1, ["C2:KEY-DUPLICATE"], body=std(after=second(Kill=["a", "b"]))),
        _case("same-key-two-claims-ok", 0, [], body=std(after=second())),
        _case("heading-nospace", 1, ["C0:HEADING-MALFORMED"], body=std(after="\n##C2 two\n")),
        _case("heading-lowercase", 1, ["C0:HEADING-MALFORMED"], body=std(after="\n## c2 two\n")),
        _case("heading-spaced-digit", 1, ["C0:HEADING-MALFORMED"], body=std(after="\n## C 2 two\n")),
        _case("heading-suffix", 1, ["C0:HEADING-MALFORMED"], body=std(after="\n## C2x two\n")),
        _case("heading-colon", 1, ["C0:HEADING-MALFORMED"], body=std(after="\n## C2: two\n")),
        _case("heading-double-space", 1, ["C0:HEADING-MALFORMED"], body=std(after="\n##  C2 two\n")),
        _case("heading-tab-tail", 1, ["C0:HEADING-MALFORMED"], body=std(after="\n## C2\ttwo\n")),
        _case("heading-two-bad", 1, ["C0:HEADING-MALFORMED"] * 2, body=std(after="\n##C2\n## c3\n")),
        _case("heading-bad-with-keys-ignored", 1, ["C0:HEADING-MALFORMED"],
              body=std(after=lambda c: "\n##C2 two\n" + _keys(c, {}))),
        _case("heading-bad-crlf", 1, ["C0:HEADING-MALFORMED"],
              body=std(after="\n##C2 two\n"), text=lambda t: t.replace("\n", "\r\n")),
        _case("heading-only-bad", 1, ["C0:HEADING-MALFORMED", "C0:NO-CLAIMS"],
              body=lambda c: "Round: 7\n\n##C1 one\n" + _keys(c, {})),
        _case("heading-valid-tail", 1, ["C2:FIELD-MISSING"] * 6,
              body=std(after="\n## C2 - tail words\n")),
        _case("heading-valid-eol", 1, ["C2:FIELD-MISSING"] * 6, body=std(after="\n## C2\n")),
        _case("heading-valid-trailing-space", 1, ["C2:FIELD-MISSING"] * 6, body=std(after="\n## C2 \n")),
        _case("heading-multi-digit", 1, ["C12:FIELD-MISSING"] * 6, body=std(after="\n## C12 tail\n")),
        _case("counter-symlink", 1, ["C1:COUNTER-SYMLINK"], links={"census/c.py": "p.tsv"},
              files={"census/c.py": None}),
        _case("population-symlink", 1, ["C1:POPULATION-SYMLINK"], links={"census/p.tsv": "c.py"},
              files={"census/p.tsv": None}),
        _case("counter-symlink-dangling", 1, ["C1:COUNTER-SYMLINK"], links={"census/c.py": "/nonexistent/zz"},
              files={"census/c.py": None}),
        _case("counter-symlink-to-dir", 1, ["C1:COUNTER-SYMLINK"], links={"census/c.py": "."},
              files={"census/c.py": None}),
        _case("counter-symlink-tracked-digest-of-link", 1, ["C1:COUNTER-SYMLINK"],
              links={"census/c.py": "p.tsv"}, files={"census/c.py": None},
              body=std(Counter="census/c.py sha256=" + digest(b"p.tsv"))),
        _case("path-with-spaces", 0, [], files={"census/a b/c d.py": COUNTER, "census/c.py": None},
              body=std(Counter="census/a b/c d.py sha256=" + DIG_COUNTER)),
        _case("path-nonascii", 0, [], files={"census/\u00e9\u4e2d.py": COUNTER, "census/c.py": None},
              body=std(Counter="census/\u00e9\u4e2d.py sha256=" + DIG_COUNTER)),
        _case("path-quote-backslash", 0, [], files={'census/q"b\\s.py': COUNTER, "census/c.py": None},
              body=std(Counter='census/q"b\\s.py sha256=' + DIG_COUNTER)),
        _case("path-glob-char-exact", 0, [], files={"census/c*.py": COUNTER, "census/c.py": None},
              body=std(Counter="census/c*.py sha256=" + DIG_COUNTER)),
        _case("control-path-spaces", 0, [], files={"census/c t l.txt": CONTROL, "census/ctl.txt": None},
              body=std(Control="census/c t l.txt")),
        _case("unresolved-rev", 2, None, rev="0" * 40),
        _case("short-rev", 2, None, rev="short"),
        _case("absent-prereg", 2, None, preregarg="census/round-7/missing.txt"),
        _case("prereg-is-directory", 2, None, preregarg="census/round-7"),
        _case("root-not-directory", 2, None, rootarg="/nonexistent/synthetic-root"),
    ]
    return cs


def _git_env(home):
    e = Repo("").env.copy()
    e.update({"HOME": home, "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "selftest@example.invalid",
              "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "selftest@example.invalid"})
    return e


class Fixture:
    def __init__(self, parent):
        self.dir = tempfile.mkdtemp(prefix="fx.", dir=parent)
        self.env = _git_env(self.dir + ".home")
        os.makedirs(self.env["HOME"], exist_ok=True)
        self.git("init", "-q")
        top = self.git("rev-parse", "--show-toplevel").decode().strip()
        if os.path.realpath(top) != os.path.realpath(self.dir):
            raise RuntimeError("fixture toplevel %s != %s" % (top, self.dir))

    def git(self, *args, **kw):
        p = subprocess.run(["git", "-c", "core.quotePath=false", "-C", self.dir] + list(args),
                           input=kw.get("input"), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=self.env, check=False)
        if p.returncode != 0:
            raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")))
        return p.stdout

    def commit(self, files, links=None):
        top = os.fsencode(self.dir)
        for path, data in (files or {}).items():  # bytes paths: independent of the locale's file-name codec
            full = os.path.join(top, path.encode("utf-8"))
            if os.path.lexists(full):
                os.remove(full)
            if data is not None:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "wb") as fh:
                    fh.write(data)
        for path, target in (links or {}).items():
            full = os.path.join(top, path.encode("utf-8"))
            os.makedirs(os.path.dirname(full), exist_ok=True)
            if os.path.lexists(full):
                os.remove(full)
            os.symlink(target.encode("utf-8"), full)
        self.git("add", "-A", "-f")
        self.git("commit", "-q", "--allow-empty", "-m", "synthetic")
        return self.git("rev-parse", "HEAD").decode().strip()

    def orphan(self):
        tree = self.git("mktree", input=b"").decode().strip()
        return self.git("commit-tree", tree, "-m", "orphan").decode().strip()


def _run_case(parent, c):
    if c["name"] == "digest-known-answer":
        return digest(b"abc") == DIG_ABC and digest(COUNTER) == DIG_COUNTER and digest(POP) == DIG_POP, "digest"
    fx = Fixture(parent)
    ctx = {"base": fx.commit({"README": b"base\n"})}
    ctx["orphan"] = fx.orphan()
    for files in c.get("pre", []):
        fx.commit(files)
    files = dict(DEFAULT_FILES)
    files.update(c.get("files", {}))
    body = c.get("body", std())(ctx)
    if isinstance(body, str):
        body = body.encode("utf-8")
    if "text" in c:
        body = c["text"](body.decode("utf-8", "surrogateescape")).encode("utf-8", "surrogateescape")
    files[PREREG] = body
    fx.commit(files, links=c.get("links"))
    for step in c.get("post", []):
        fx.commit(step)
    if c.get("postlinks"):
        fx.commit({}, links=c["postlinks"])
    rev = c.get("rev") or fx.git("rev-parse", "HEAD").decode().strip()
    saved = {k: os.environ.get(k) for k in c.get("env", {})}
    os.environ.update(c.get("env", {}))
    try:
        code, lines, summary, refusal = run_check(c.get("rootarg", fx.dir), c.get("preregarg", PREREG), rev)
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    got = sorted("%s:%s" % tuple(x.split(" ", 3)[1:3]) for x in lines)
    want = sorted(c["finds"] or [])
    ok = code == c["code"] and got == want and (
        (refusal is not None and summary is None) if c["code"] == 2
        else summary is not None and summary.endswith("findings=%d" % len(want)))
    return ok, "exit=%s findings=%s summary=%s refusal=%s want exit=%s %s" % (code, got, summary, refusal,
                                                                           c["code"], want)


def selftest():
    parent = tempfile.mkdtemp(prefix="souji-freeze-selftest.")
    cases = _cases()
    npass = 0
    try:
        for c in cases:
            try:
                ok, why = _run_case(parent, c)
            except Exception as exc:  # a broken fixture or crashed check is a failed case
                ok, why = False, "%s: %s" % (type(exc).__name__, exc)
            if ok:
                npass += 1
            else:
                sys.stderr.write("FAIL %s: %s\n" % (c["name"], why))
    finally:
        shutil.rmtree(parent, ignore_errors=True)
    print("SELFTEST cases=%d pass=%d fail=%d" % (len(cases), npass, len(cases) - npass))
    return 0 if npass == len(cases) else 1


def main(argv):
    ap = argparse.ArgumentParser(description="Check a preregistration's freeze at a revision.")
    ap.add_argument("--root")
    ap.add_argument("--prereg")
    ap.add_argument("--rev")
    ap.add_argument("--selftest", action="store_true", help="run the built-in synthetic-repository cases")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.root and args.prereg and args.rev):
        ap.error("--root, --prereg and --rev are required (or --selftest)")
    code, lines, summary, refusal = run_check(args.root, args.prereg, args.rev)
    if refusal is not None:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % refusal)
        return 2
    for line in lines:
        print(line)
    print(summary)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
