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

r42 additions:
  KEY-DUPLICATE        a key line appearing more than once in one claim block: one finding per
                       duplicated key; no value of a duplicated key is read (no first-wins reading).
  HEADING-MALFORMED    a column-0 line `##` (not `###`) + optional spaces + `C`/`c` + optional spaces +
                       digit that is not `## C<digits>` followed by a space or end of line: label C0,
                       detail `line=<n>`; it opens no claim and closes the claim before it.
  COUNTER-SYMLINK /    the Counter / Population path is a symlink (git mode 120000) at FREEZE-REV: this
  POPULATION-SYMLINK   finding alone, no digest comparison (the link text is not the file).
  DISPATCH-BEFORE-FREEZE  every file under `.ufo/waves/round-<N>/` at any depth whose basename contains
                       `-dispatch` or `.ready`, or ends `-spec.json` or `-results.json`, first added by
                       FREEZE-REV or an ancestor of it.

`--selftest` builds its own throwaway git repositories under $TMPDIR (random names, fresh salts, every git
call naming -C, identity through the environment), runs this tool's own digest, freeze-detection
(`git log --diff-filter=A`) and ancestry (`git merge-base --is-ancestor`) code over them, and prints
`SELFTEST cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0. Expected digests come from an independent
pure-Python SHA-256, never from hashlib, so a broken digest cannot grade itself.
Python stdlib only; read-only on --root.
"""
import argparse
import hashlib
import math
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile

FULL40 = re.compile(r"^[0-9a-f]{40}$")
HEADER = re.compile(r"^## C([0-9]+)(?: |$)")
MALFORMED = re.compile(r"^##(?!#) *[Cc] *[0-9]")
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
            return subprocess.run(["git", "-c", "core.quotePath=false", "-c", "log.mailmap=false",
                                   "-C", self.root] + list(args), stdout=subprocess.PIPE,
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
        """Git file mode of the exact tree entry PATH at rev (e.g. '100644', '120000'), or None."""
        if "\x00" in path:
            return None
        p = self.run("ls-tree", "-z", "--full-tree", rev, "--", path)
        if p.returncode != 0:
            return None
        for rec in p.stdout.split(b"\x00"):
            meta, _, name = rec.partition(b"\t")
            if name.decode("utf-8", "replace") == path:
                return meta.split(b" ")[0].decode("ascii", "replace")
        return None

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b).returncode == 0


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def parse_claims(text):
    """-> (claims [(label, {key: [values]})], malformed [line numbers])"""
    claims = []
    malformed = []
    cur = None
    for n, line in enumerate(text.splitlines(), 1):
        m = HEADER.match(line)
        if m:
            cur = ("C" + m.group(1), {})
            claims.append(cur)
            continue
        if MALFORMED.match(line):
            malformed.append(n)
            cur = None
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur is not None:
            m = KEYLINE.match(line)
            if m:
                cur[1].setdefault(m.group(1), []).append(m.group(2))
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
    p = repo.run("log", "-z", "--diff-filter=A", "--no-renames", "--full-history", "--name-only",
                 "--format=%x01%H", rev, "--", tree)
    if p.returncode != 0:
        return []
    adds = {}  # path -> [adding commits]
    commit = None
    after_hash = False
    for chunk in p.stdout.decode("utf-8", "replace").split("\x00"):
        if chunk.startswith("\x01"):
            commit = chunk[1:].strip()
            after_hash = True
            continue
        if not chunk:
            continue
        if after_hash and chunk.startswith("\n"):
            chunk = chunk[1:]
        after_hash = False
        if commit and chunk and dispatch_name(chunk.rsplit("/", 1)[-1]):
            adds.setdefault(chunk, []).append(commit)
    out = []
    for path in sorted(adds):
        early = [c for c in adds[path] if c == freeze or repo.is_ancestor(c, freeze)]
        if early:
            out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"
                        % (path, early[-1][:12], freeze[:12])))
    return out


def check_path_sha(repo, rev, freeze, label, key, value, missing, digest, found):
    """Counter/Population: returns (freeze blob, path) or None."""
    m = PATH_SHA.match(value)
    path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)
    if not path:
        return None
    if repo.mode(freeze, path) == "120000":
        found.append((label, key.upper() + "-SYMLINK", "%s is a symlink at freeze %s"
                      % (path, freeze[:12])))
        return None
    at_freeze = repo.blob(freeze, path)
    if at_freeze is None:
        found.append((label, missing, "%s not present at freeze %s" % (path, freeze[:12])))
        return None
    got = sha256_hex(at_freeze)
    if want is None:
        found.append((label, digest, "%s has no sha256=<64 hex> in %r" % (path, value)))
    elif got != want:
        found.append((label, digest, "%s at freeze hashes %s, stated %s" % (path, got, want)))
    at_rev = repo.blob(rev, path)
    if at_rev != at_freeze:
        found.append((label, "FROZEN-EDITED", "%s differs between freeze %s and %s"
                      % (path, freeze[:12], rev[:12])))
    return at_freeze, path


def evaluate(repo, rev, prereg, text, freeze):
    found = []
    claims, malformed = parse_claims(text)
    for n in malformed:
        found.append(("C0", "HEADING-MALFORMED", "line=%d" % n))
    if not claims:
        found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    for label, vals in claims:
        f = {}
        for key in KEYS:
            if key not in vals:
                found.append((label, "FIELD-MISSING", key))
            elif len(vals[key]) > 1:
                found.append((label, "KEY-DUPLICATE", key))
            else:
                f[key] = vals[key][0]
                if not f[key]:
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


def run_check(root, prereg, rev_arg):
    """-> (exit code, claims, sorted FINDING lines, refusal text or None); never prints."""
    try:
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
    except Refusal as exc:
        return 2, 0, [], str(exc)
    lines = sorted("FINDING %s %s %s" % f for f in found)
    return (1 if lines else 0), n, lines, None


# --------------------------------------------------------------------------------------------------
# --selftest
# --------------------------------------------------------------------------------------------------

def _primes(n):
    out, k = [], 2
    while len(out) < n:
        if all(k % p for p in out):
            out.append(k)
        k += 1
    return out


def _icbrt(n):
    lo, hi = 0, 1 << (n.bit_length() // 3 + 2)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid ** 3 <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo


_SHA_CONST = []


def ref_sha256(data):
    """Independent SHA-256 (FIPS 180-4), constants derived from primes; no hashlib."""
    if not _SHA_CONST:
        pr = _primes(64)
        _SHA_CONST.append(([_icbrt(p << 96) & 0xFFFFFFFF for p in pr],
                           [math.isqrt(p << 64) & 0xFFFFFFFF for p in pr[:8]]))
    k, h = _SHA_CONST[0]
    m = 0xFFFFFFFF
    rr = lambda x, c: ((x >> c) | (x << (32 - c))) & m
    msg = bytes(data) + b"\x80"
    msg += b"\x00" * ((56 - len(msg)) % 64) + (len(data) * 8).to_bytes(8, "big")
    for off in range(0, len(msg), 64):
        w = [int.from_bytes(msg[off + 4 * i: off + 4 * i + 4], "big") for i in range(16)]
        for i in range(16, 64):
            s0 = rr(w[i - 15], 7) ^ rr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = rr(w[i - 2], 17) ^ rr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & m)
        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            t1 = (hh + (rr(e, 6) ^ rr(e, 11) ^ rr(e, 25)) + ((e & f) ^ (~e & m & g)) + k[i] + w[i]) & m
            t2 = ((rr(a, 2) ^ rr(a, 13) ^ rr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & m
            hh, g, f, e, d, c, b, a = g, f, e, (d + t1) & m, c, b, a, (t1 + t2) & m
        h = [(x + y) & m for x, y in zip(h, [a, b, c, d, e, f, g, hh])]
    return "".join("%08x" % x for x in h)


class Fx:
    """One throwaway git repository; every git call names -C, identity only through the environment."""

    def __init__(self, parent):
        self.d = os.path.join(parent, "r" + secrets.token_hex(5))
        os.makedirs(self.d)
        self.tick = 0
        self.env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
                    "GIT_AUTHOR_NAME": "st" + secrets.token_hex(2), "GIT_AUTHOR_EMAIL": "st@example.invalid",
                    "GIT_COMMITTER_NAME": "st" + secrets.token_hex(2),
                    "GIT_COMMITTER_EMAIL": "st@example.invalid"}
        self.git("-c", "init.defaultBranch=main", "init", "-q")
        top = self.git("rev-parse", "--show-toplevel").stdout.decode().strip()
        if os.path.realpath(top) != os.path.realpath(self.d):
            raise RuntimeError("fixture toplevel %s != %s" % (top, self.d))

    def git(self, *a, inp=None):
        p = subprocess.run(["git", "-c", "core.quotePath=false", "-c", "commit.gpgsign=false",
                            "-C", self.d] + list(a), input=inp, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, env=self.env, check=False)
        if p.returncode != 0:
            raise RuntimeError("fixture git %s: %s" % (a[:2], p.stderr.decode("utf-8", "replace")))
        return p

    def put(self, rel, data):
        full = os.path.join(self.d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(data)

    def link(self, rel, target):
        full = os.path.join(self.d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        os.symlink(target, full)

    def commit(self, files=(), links=()):
        for rel, data in files:
            self.put(rel, data)
        for rel, target in links:
            self.link(rel, target)
        self.tick += 1
        stamp = "@%d +0000" % (1700000000 + 60 * self.tick)
        self.env["GIT_AUTHOR_DATE"] = self.env["GIT_COMMITTER_DATE"] = stamp
        self.git("add", "-A", "--", ".")
        self.git("commit", "-q", "--allow-empty", "-m", "m" + secrets.token_hex(6))
        return self.git("rev-parse", "HEAD").stdout.decode().strip()


def _claim(n, f, drop=(), dup=None, heading=None):
    out = [heading if heading is not None else "## C%d \u2014 %s" % (n, "w" + secrets.token_hex(3))]
    for k in KEYS:
        if k in drop:
            continue
        out.append("%s: %s" % (k, f[k]))
        if dup and k in dup:
            out.append("%s: %s" % (k, dup[k]))
    out.append("")
    return out


def _scenario(parent, o):
    """Build a repository per option dict o; -> (Fx, rev, prereg path)."""
    fx = Fx(parent)
    rnd = str(secrets.randbelow(900) + 100)
    top = "census/round-%s" % rnd
    sp = " " if o.get("spaces") else ""
    salt = lambda: secrets.token_hex(8)
    cpath = "%s/c%s%sdir/counter %s.py" % (top, secrets.token_hex(2), sp, salt()) if sp else \
        "%s/counter-%s.py" % (top, salt())
    ppath = "%s/pop-%s.tsv" % (top, salt())
    kpath = "%s/controls/ctl-%s.txt" % (top, salt())
    prereg = "%s/preregistration.txt" % top
    wave = ".ufo/waves/round-%s/" % rnd
    cdata = ("# counter %s\nprint(%r)\n" % (salt(), salt())).encode()
    pdata = ("id\tname\n1\t%s\n2\t%s\n" % (salt(), salt())).encode()
    if o.get("population") == "empty":
        pdata = ("id\tname %s\n" % salt()).encode()
    kdata = ("SUMMARY items=2 corrected=0 tag=%s\nEXIT=%d\n" % (salt(), 0 if o.get("control") == "green" else 1)).encode()
    pre = [(wave + n, ("x" + salt()).encode()) for n in o.get("pre", ())]
    c0 = fx.commit([("base-%s.txt" % salt(), salt().encode())] + pre)
    base = {"unresolved": secrets.token_hex(20), "sibling": None}.get(o.get("base"), c0)
    if o.get("base") == "sibling":
        tree = fx.git("rev-parse", c0 + "^{tree}").stdout.decode().strip()
        base = fx.git("commit-tree", tree, "-p", c0, "-m", "s" + secrets.token_hex(4)).stdout.decode().strip()
    dg = lambda b: "sha256=" + ref_sha256(b)
    cval = "%s %s" % (cpath, dg(cdata if o.get("counter") != "digest" else cdata + b"x"))
    pval = "%s %s" % (ppath, dg(pdata if o.get("population") != "digest" else pdata + b"x"))
    if o.get("counter") == "symlink":
        cval = "%s %s" % (cpath, dg(cdata))
    if o.get("population") == "symlink":
        pval = "%s %s" % (ppath, dg(pdata))
    f = {"Base": base, "Counter": cval, "Population": pval, "Control": kpath,
         "Target": "SUMMARY t%s" % salt(), "Kill": "any k%s" % salt()}
    f.update(o.get("values", {}))
    lines = ["Round: %s" % rnd, "Written %s" % salt(), ""]
    if not o.get("no_claims"):
        lines += _claim(1, f, o.get("drop", ()), o.get("dup"), o.get("heading"))
    lines += o.get("tail", [])
    if o.get("second_bad"):
        lines += _claim(2, f, ("Kill",))
    nl = "\r\n" if o.get("crlf") else "\n"
    text = nl.join(lines) + nl
    if o.get("bom"):
        text = "\ufeff" + text
    files = [(prereg, text.encode("utf-8"))]
    links = []
    if o.get("counter") == "symlink":
        files.append((cpath + ".real", cdata))
        links.append((cpath, os.path.basename(cpath) + ".real"))
    elif o.get("counter") != "missing":
        files.append((cpath, cdata))
    if o.get("population") == "symlink":
        files.append((ppath + ".real", pdata))
        links.append((ppath, os.path.basename(ppath) + ".real"))
    elif o.get("population") != "missing":
        files.append((ppath, pdata))
    if o.get("control") != "missing":
        files.append((kpath, kdata))
    files += [(wave + n, ("x" + salt()).encode()) for n in o.get("at", ())]
    freeze = fx.commit(files, links)
    tip = freeze
    if o.get("post"):
        tip = fx.commit([(wave + n, ("x" + salt()).encode()) for n in o["post"]])
    if o.get("counter") == "edited":
        tip = fx.commit([(cpath, cdata + b"edit")])
    if o.get("population") == "edited":
        tip = fx.commit([(ppath, pdata + b"3\tz\n")])
    return fx, tip, prereg


def _expect(items):
    return sorted(items)


def _cases():
    r = secrets.token_hex(3)
    D = "-dispatch"
    cases = [
        ("clean", {}, 0, []),
        ("clean-spaces-in-path", {"spaces": True}, 0, []),
        ("clean-crlf", {"crlf": True}, 0, []),
        ("clean-bom", {"bom": True}, 0, []),
        ("clean-triple-hash-and-other-heading", {"tail": ["### C9 sub", "## Notes", "##Plain", ""]}, 0, []),
        ("clean-dispatch-after", {"post": [r + "-dispatch.json", r + ".ready", r + "-spec.json", r + "-results.json"]}, 0, []),
        ("clean-dispatch-unrelated-before", {"pre": [r + "-notes.md", "sub/" + r + ".txt"]}, 0, []),
        ("no-claims", {"no_claims": True}, 1, ["C0:NO-CLAIMS"]),
        ("field-missing-base", {"drop": ("Base",)}, 1, ["C1:FIELD-MISSING"]),
        ("field-missing-counter", {"drop": ("Counter",)}, 1, ["C1:FIELD-MISSING"]),
        ("field-missing-kill", {"drop": ("Kill",)}, 1, ["C1:FIELD-MISSING"]),
        ("field-empty-target", {"values": {"Target": ""}}, 1, ["C1:FIELD-EMPTY"]),
        ("field-empty-counter", {"values": {"Counter": ""}}, 1, ["C1:FIELD-EMPTY"]),
        ("base-unresolved", {"base": "unresolved"}, 1, ["C1:BASE-UNRESOLVED"]),
        ("base-not-ancestor", {"base": "sibling"}, 1, ["C1:BASE-NOT-ANCESTOR"]),
        ("counter-missing", {"counter": "missing"}, 1, ["C1:COUNTER-MISSING"]),
        ("counter-digest", {"counter": "digest"}, 1, ["C1:COUNTER-DIGEST"]),
        ("population-missing", {"population": "missing"}, 1, ["C1:POPULATION-MISSING"]),
        ("population-digest", {"population": "digest"}, 1, ["C1:POPULATION-DIGEST"]),
        ("population-empty", {"population": "empty"}, 1, ["C1:POPULATION-EMPTY"]),
        ("control-missing", {"control": "missing"}, 1, ["C1:CONTROL-MISSING"]),
        ("control-not-red", {"control": "green"}, 1, ["C1:CONTROL-NOT-RED"]),
        ("frozen-edited-counter", {"counter": "edited"}, 1, ["C1:FROZEN-EDITED"]),
        ("frozen-edited-population", {"population": "edited"}, 1, ["C1:FROZEN-EDITED"]),
        ("two-claims-one-bad", {"second_bad": True}, 1, ["C2:FIELD-MISSING"]),
        ("dispatch-before-json", {"pre": [r + D + ".json"]}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
        ("dispatch-in-freeze-commit", {"at": [r + ".ready"]}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
        ("dispatch-before-attempts", {"pre": [r + D + "-attempts.txt"]}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
        ("dispatch-before-ready-dispatched", {"pre": [r + ".ready.dispatched"]}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
        ("dispatch-before-spec", {"pre": [r + "-spec.json"]}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
        ("dispatch-before-results-deep", {"pre": ["a/b/" + r + "-results.json"]}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
        ("dispatch-before-tab-name", {"pre": ["t\t" + r + "-spec.json"]}, 1, ["C0:DISPATCH-BEFORE-FREEZE"]),
        ("dispatch-two-names-before", {"pre": [r + "-spec.json", r + ".ready"]}, 1,
         ["C0:DISPATCH-BEFORE-FREEZE", "C0:DISPATCH-BEFORE-FREEZE"]),
        ("key-dup-base-differs", {"dup": {"Base": "0" * 40}}, 1, ["C1:KEY-DUPLICATE"]),
        ("key-dup-counter-identical", {"dup": {"Counter": "SAME"}}, 1, ["C1:KEY-DUPLICATE"]),
        ("key-dup-target", {"dup": {"Target": "again"}}, 1, ["C1:KEY-DUPLICATE"]),
        ("key-dup-two-keys", {"dup": {"Kill": "k2", "Control": "c2"}}, 1, ["C1:KEY-DUPLICATE", "C1:KEY-DUPLICATE"]),
        ("heading-no-space", {"tail": ["##C7", "Base: x", ""]}, 1, ["C0:HEADING-MALFORMED"]),
        ("heading-lowercase", {"tail": ["## c7", ""]}, 1, ["C0:HEADING-MALFORMED"]),
        ("heading-spaced-digit", {"tail": ["## C 7", ""]}, 1, ["C0:HEADING-MALFORMED"]),
        ("heading-suffix-letter", {"tail": ["## C7x", ""]}, 1, ["C0:HEADING-MALFORMED"]),
        ("heading-suffix-colon", {"tail": ["## C7: x", ""]}, 1, ["C0:HEADING-MALFORMED"]),
        ("heading-two-spaces", {"tail": ["##  C7", ""]}, 1, ["C0:HEADING-MALFORMED"]),
        ("heading-valid-tail", {"tail": ["## C7 trailing words", ""]}, 1, ["C7:FIELD-MISSING"] * 6),
        ("counter-symlink", {"counter": "symlink"}, 1, ["C1:COUNTER-SYMLINK"]),
        ("population-symlink", {"population": "symlink"}, 1, ["C1:POPULATION-SYMLINK"]),
    ]
    return cases


def _classes(lines):
    out = []
    for ln in lines:
        p = ln.split(" ", 3)
        out.append("%s:%s" % (p[1], p[2]))
    return sorted(out)


def _selftest():
    parent = tempfile.mkdtemp(prefix="sfc-%s-" % secrets.token_hex(4), dir=os.environ.get("TMPDIR") or None)
    results = []  # (name, ok, why)

    def record(name, ok, why=""):
        results.append((name, bool(ok), why))

    try:
        # digest logic: this tool's sha256_hex against known answers and the independent reference
        record("digest-known-answer-abc", sha256_hex(b"abc") ==
               "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
               sha256_hex(b"abc"))
        record("digest-known-answer-empty", sha256_hex(b"") ==
               "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", sha256_hex(b""))
        probe = secrets.token_bytes(200)
        record("digest-matches-reference", sha256_hex(probe) == ref_sha256(probe),
               "%s != %s" % (sha256_hex(probe), ref_sha256(probe)))
        record("reference-known-answer", ref_sha256(b"abc") ==
               "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

        # grammar and git-backed cases, in-process through the tool's own run_check
        last = None
        for name, opts, want_exit, want in _cases():
            try:
                fx, tip, prereg = _scenario(parent, opts)
                last = (fx, tip, prereg)
                code, n, lines, refusal = run_check(fx.d, prereg, tip)
                got = _classes(lines)
                ok = code == want_exit and got == _expect(want)
                record(name, ok, "exit=%s want=%s got=%s want=%s %s" % (code, want_exit, got, _expect(want), refusal or ""))
            except Exception as exc:  # a broken case is a failed case, never a crash
                record(name, False, "exception %r" % (exc,))

        # r41 hardening: hostile ambient git environment must not change a verdict
        try:
            fx, tip, prereg = _scenario(parent, {})
            saved = {k: os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY")}
            os.environ["GIT_DIR"] = os.path.join(parent, "no-such-" + secrets.token_hex(3))
            os.environ["GIT_WORK_TREE"] = parent
            os.environ["GIT_INDEX_FILE"] = os.path.join(parent, "no-index")
            os.environ["GIT_OBJECT_DIRECTORY"] = os.path.join(parent, "no-objects")
            try:
                code, n, lines, refusal = run_check(fx.d, prereg, tip)
            finally:
                for k, v in saved.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v
            record("ambient-git-env-ignored", code == 0 and n == 1 and not lines, "%s %s %s" % (code, lines, refusal))
        except Exception as exc:
            record("ambient-git-env-ignored", False, "exception %r" % (exc,))

        # could-not-evaluate paths
        try:
            fx, tip, prereg = _scenario(parent, {})
            code, _, _, refusal = run_check(fx.d, prereg, secrets.token_hex(20))
            record("refuse-unresolved-rev", code == 2 and refusal, str(code))
            code, _, _, refusal = run_check(fx.d, "census/" + secrets.token_hex(4) + ".txt", tip)
            record("refuse-absent-prereg", code == 2 and refusal, str(code))
            code, _, _, refusal = run_check(fx.d, prereg, tip[:12])
            record("refuse-short-rev", code == 2 and refusal, str(code))
            code, _, _, refusal = run_check(os.path.join(parent, "nope" + secrets.token_hex(3)), prereg, tip)
            record("refuse-missing-root", code == 2 and refusal, str(code))
        except Exception as exc:
            record("refusals", False, "exception %r" % (exc,))

        # freeze detection and ancestry, directly
        try:
            fx = Fx(parent)
            a = fx.commit([("a" + secrets.token_hex(3), secrets.token_bytes(8))])
            pth = "census/p%s.txt" % secrets.token_hex(3)
            b = fx.commit([(pth, secrets.token_bytes(8))])
            c = fx.commit([("z" + secrets.token_hex(3), secrets.token_bytes(8))])
            repo = Repo(fx.d)
            record("freeze-rev-oldest-add", freeze_rev(repo, c, pth) == b, "%s vs %s" % (freeze_rev(repo, c, pth), b))
            record("ancestor-true", repo.is_ancestor(a, c) and repo.is_ancestor(b, c), "")
            record("ancestor-false", not repo.is_ancestor(c, a), "")
            record("symlink-mode-read", repo.mode(c, pth) == "100644", str(repo.mode(c, pth)))
        except Exception as exc:
            record("freeze-and-ancestry", False, "exception %r" % (exc,))

        # CLI plumbing: the tool as a child process over a synthetic repository
        try:
            fx, tip, prereg = _scenario(parent, {})
            args = [sys.executable, "-B", os.path.abspath(__file__), "--root", fx.d, "--prereg", prereg, "--rev", tip]
            p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            record("cli-clean", p.returncode == 0 and p.stdout.decode().strip() == "SUMMARY claims=1 findings=0",
                   "%s %r" % (p.returncode, p.stdout))
            fx, tip, prereg = _scenario(parent, {"population": "digest"})
            args[args.index("--root") + 1] = fx.d
            args[args.index("--prereg") + 1] = prereg
            args[args.index("--rev") + 1] = tip
            p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            out = p.stdout.decode().splitlines()
            record("cli-red", p.returncode == 1 and len(out) == 2 and out[0].startswith("FINDING C1 POPULATION-DIGEST ")
                   and out[1] == "SUMMARY claims=1 findings=1", "%s %r" % (p.returncode, out))
        except Exception as exc:
            record("cli", False, "exception %r" % (exc,))
    finally:
        shutil.rmtree(parent, ignore_errors=True)

    fail = [r for r in results if not r[1]]
    for name, _, why in fail:
        sys.stderr.write("SELFTEST FAIL %s: %s\n" % (name, why))
    print("SELFTEST cases=%d pass=%d fail=%d" % (len(results), len(results) - len(fail), len(fail)))
    return 1 if fail else 0


def main(argv):
    ap = argparse.ArgumentParser(description="Check a preregistration's freeze at a revision.")
    ap.add_argument("--root")
    ap.add_argument("--prereg")
    ap.add_argument("--rev")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not (args.root and args.prereg and args.rev):
        ap.error("--root, --prereg and --rev are required (or --selftest)")
    code, n, lines, refusal = run_check(args.root, args.prereg, args.rev)
    if refusal is not None:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % refusal)
        return 2
    for line in lines:
        print(line)
    print("SUMMARY claims=%d findings=%d" % (n, len(lines)))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
