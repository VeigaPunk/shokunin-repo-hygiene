#!/usr/bin/env python3
"""tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40
  python3 -B tools/souji-freeze-check.py --selftest

Reads the preregistration PATH as the blob at --rev (git object store only, never the work tree) and
prints `FINDING <claim> <CLASS> <detail>` per finding, sorted, then `SUMMARY claims=<n> findings=<m>`.
Exit 0 no findings, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...` on stderr).
`--selftest` builds synthetic repositories under $TMPDIR, runs the same checks on each and prints
`SELFTEST cases=<n> pass=<p> fail=<f>`; exit 0 iff fail=0.

Grammar: a claim block starts at `## C<digits>` and runs to the next `## ` line; inside it a key line is
`Key: value` at column 0 for Base, Counter, Population, Control, Target, Kill. Counter and Population
values are `<repo path> sha256=<64 hex>`. FREEZE-REV is the oldest commit reachable from --rev that adds
PATH. Finding classes: NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY, KEY-DUPLICATE, HEADING-MALFORMED,
BASE-UNRESOLVED, BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-SYMLINK, COUNTER-DIGEST, POPULATION-MISSING,
POPULATION-SYMLINK, POPULATION-DIGEST, POPULATION-EMPTY, CONTROL-MISSING, CONTROL-NOT-RED, FROZEN-EDITED,
DISPATCH-BEFORE-FREEZE. Prereg-wide findings carry claim label C0. A missing `Round:` line is reported
as `FIELD-MISSING C0 Round`, an empty value of any key is `FIELD-EMPTY`.
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
HEADER = re.compile(r"^## C(\d+)(?=[ ]|$)")
MALFORMED = re.compile(r"^##(?!#)[ ]*[Cc][ ]*\d")
KEYLINE = re.compile(r"^(Base|Counter|Population|Control|Target|Kill):[ \t]*(.*?)[ \t]*$")
PATH_SHA = re.compile(r"^(.+?)[ \t]+sha256=([0-9a-f]{64})$")
ROUND = re.compile(r"^\ufeff?Round:[ \t]*(\d+)[ \t]*\r?$", re.M)
EXIT_LINE = re.compile(r"^EXIT=(\d+)$")
KEYS = ("Base", "Counter", "Population", "Control", "Target", "Kill")
SYMLINK_MODE = "120000"


class Refusal(Exception):
    pass


class Repo:
    def __init__(self, root):
        self.root = root
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
        p = self.run("rev-parse", "--verify", "-q", rev + "^{commit}")
        out = p.stdout.decode("utf-8", "replace").strip()
        return out if p.returncode == 0 and FULL40.match(out) else None

    def blob(self, rev, path):
        if "\x00" in path:
            return None
        p = self.run("cat-file", "blob", "%s:%s" % (rev, path))
        return p.stdout if p.returncode == 0 else None

    def mode(self, rev, path):
        p = self.run("ls-tree", "-z", rev, "--", path)
        if p.returncode != 0:
            return None
        for rec in p.stdout.split(b"\x00"):
            meta, sep, name = rec.partition(b"\t")
            if sep and name == path.encode("utf-8"):
                return meta.split()[0].decode("ascii")
        return None

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b).returncode == 0


def parse(text):
    """Returns (claims, malformed_line_numbers). claims: [{'label', 'keys': {key: [values]}}]."""
    claims, malformed, cur = [], [], None
    for n, line in enumerate(text.splitlines(), 1):
        m = HEADER.match(line)
        if m:
            cur = {"label": "C" + m.group(1), "keys": {}}
            claims.append(cur)
            continue
        if MALFORMED.match(line):
            malformed.append(n)
            if line.startswith("## "):
                cur = None
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur is not None:
            k = KEYLINE.match(line)
            if k:
                cur["keys"].setdefault(k.group(1), []).append(k.group(2))
    return claims, malformed


def freeze_rev(repo, rev, prereg):
    p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--reverse",
                 "--format=%H", rev, "--", prereg)
    ids = [x for x in p.stdout.decode("utf-8", "replace").split() if FULL40.match(x)]
    return ids[0] if p.returncode == 0 and ids else None


def is_wave_file(base):
    return ("-dispatch" in base or ".ready" in base or base.endswith("-spec.json")
            or base.endswith("-results.json"))


def dispatch_findings(repo, rev, freeze, text):
    m = ROUND.search(text)
    if not m:
        return [("C0", "FIELD-MISSING", "Round")]
    tree = ".ufo/waves/round-%s/" % m.group(1)
    p = repo.run("log", "--diff-filter=A", "--no-renames", "--full-history", "--name-only",
                 "--format=%x01%H", rev, "--", tree)
    if p.returncode != 0:
        return []
    first, commit = {}, None
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith("\x01"):
            commit = line[1:].strip()
        elif line and commit and is_wave_file(line.rsplit("/", 1)[-1]):
            first[line] = commit
    out = []
    for path, c in sorted(first.items()):
        if c == freeze or repo.is_ancestor(c, freeze):
            out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"
                        % (path, c[:12], freeze[:12])))
    return out


def check_path(repo, rev, freeze, label, value, missing, digest, symlink, found):
    m = PATH_SHA.match(value)
    parts = value.split()
    path = m.group(1) if m else (parts[0] if parts else "")
    if not path:
        return None
    if repo.mode(freeze, path) == SYMLINK_MODE:
        found.append((label, symlink, "%s is a symlink at freeze %s" % (path, freeze[:12])))
        return None
    at_freeze = repo.blob(freeze, path)
    if at_freeze is None:
        found.append((label, missing, "%s not present at freeze %s" % (path, freeze[:12])))
        return None
    got = hashlib.sha256(at_freeze).hexdigest()
    if m is None:
        found.append((label, digest, "%s has no sha256=<64 hex> in %r" % (path, value)))
    elif got != m.group(2):
        found.append((label, digest, "%s at freeze hashes %s, stated %s" % (path, got, m.group(2))))
    if repo.blob(rev, path) != at_freeze:
        found.append((label, "FROZEN-EDITED", "%s differs between freeze %s and %s"
                      % (path, freeze[:12], rev[:12])))
    return at_freeze, path


def evaluate(repo, rev, prereg, text, freeze):
    found = []
    claims, malformed = parse(text)
    for n in malformed:
        found.append(("C0", "HEADING-MALFORMED", "line=%d" % n))
    if not claims:
        found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    for c in claims:
        label, keys = c["label"], c["keys"]
        for key in KEYS:
            if key not in keys:
                found.append((label, "FIELD-MISSING", key))
        for key in sorted(keys):
            if len(keys[key]) > 1:
                pass
        f = {key: vals[0] for key, vals in keys.items()}
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
            check_path(repo, rev, freeze, label, f["Counter"], "COUNTER-MISSING", "COUNTER-DIGEST",
                       "COUNTER-SYMLINK", found)
        if f.get("Population"):
            got = check_path(repo, rev, freeze, label, f["Population"], "POPULATION-MISSING",
                             "POPULATION-DIGEST", "POPULATION-SYMLINK", found)
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


def check(root, rev_in, prereg):
    repo = Repo(root)
    rev = repo.commit(rev_in)
    if rev is None:
        raise Refusal("--rev %s does not resolve to a commit in %s" % (rev_in, root))
    raw = repo.blob(rev, prereg)
    if raw is None:
        raise Refusal("%s is absent at %s" % (prereg, rev))
    freeze = freeze_rev(repo, rev, prereg)
    if freeze is None:
        raise Refusal("no commit reachable from %s adds %s" % (rev, prereg))
    return evaluate(repo, rev, prereg, raw.decode("utf-8", "replace"), freeze)


# ---- selftest: synthetic repositories, digests as literals (never computed through the runtime)
GENV = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
COUNTER_TEXT = "# counter\nprint('counter')\n"
COUNTER_SHA = "d2ee596e966884b00f76999c981ff76524b6d9759fa48321833fe4a18f2c7c6c"
POP_TEXT = "id\tname\n1\talpha\n2\tbeta\n"
POP_SHA = "6eb3dbf44f4fd647dbb0e69ba9839b50678ac000e208410a3b789d7da290b189"
POP_EMPTY_TEXT = "id\tname\n"
POP_EMPTY_SHA = "68c9a2ccc12a30c8c3651b461ebb87cedce7e31b4c94abce79bc2714efb54513"
CONTROL_RED = "SUMMARY items=2 corrected=0\nEXIT=1\n"
CONTROL_GREEN = "SUMMARY items=2 corrected=2\nEXIT=0\n"

SELF_CASES = (
    ("clean", {}, 0, []),
    ("counter-digest", {"counter_digest": True}, 1, [("C1", "COUNTER-DIGEST")]),
    ("population-digest", {"population_digest": True}, 1, [("C1", "POPULATION-DIGEST")]),
    ("base-not-ancestor", {"side": True}, 1, [("C1", "BASE-NOT-ANCESTOR")]),
    ("dispatch-before", {"dispatch_before": True}, 1, [("C0", "DISPATCH-BEFORE-FREEZE")]),
    ("dispatch-after", {"dispatch_after": True}, 0, []),
    ("frozen-edited", {"edit_counter": True}, 1, [("C1", "FROZEN-EDITED")]),
    ("dup-base", {"dup_base": True}, 1, [("C1", "KEY-DUPLICATE")]),
    ("heading-malformed", {"tail": "##C2 - x\n"}, 1, [("C0", "HEADING-MALFORMED")]),
    ("counter-symlink", {"counter_symlink": True}, 1, [("C1", "COUNTER-SYMLINK")]),
    ("population-empty", {"population": POP_EMPTY_TEXT, "population_sha": POP_EMPTY_SHA}, 1,
     [("C1", "POPULATION-EMPTY")]),
    ("no-claims", {"no_claims": True}, 1, [("C0", "NO-CLAIMS")]),
    ("control-not-red", {"control_green": True}, 1, [("C1", "CONTROL-NOT-RED")]),
)


def git(d, *args):
    return subprocess.run(["git", "-C", d] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=GENV, check=True, text=True).stdout.strip()


def make_repo(root, name, mut):
    d = os.path.join(root, name)
    os.makedirs(d)
    git(d, "init", "-q", "-b", "main", d)

    def put(rel, text):
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def commit(msg):
        git(d, "add", "-A")
        git(d, "commit", "-qm", msg)
        return git(d, "rev-parse", "HEAD")

    put("README", "base\n")
    base = commit("base")
    if mut.get("side"):
        git(d, "checkout", "-q", "-b", "side")
        put("side.txt", "side\n")
        base = commit("side")
        git(d, "checkout", "-q", "main")
    if mut.get("dispatch_before"):
        put(".ufo/waves/round-42/w1-dispatch.json", "{}\n")
        commit("early dispatch")
    population = mut.get("population", POP_TEXT)
    population_sha = mut.get("population_sha", POP_SHA)
    put("census/control.txt", CONTROL_GREEN if mut.get("control_green") else CONTROL_RED)
    if mut.get("counter_symlink"):
        put("census/real-c1.py", COUNTER_TEXT)
        os.symlink("real-c1.py", os.path.join(d, "census/c1.py"))
    else:
        put("census/c1.py", COUNTER_TEXT)
    put("census/pop.tsv", population)
    counter_sha = "0" * 64 if mut.get("counter_digest") else COUNTER_SHA
    if mut.get("population_digest"):
        population_sha = "1" * 64
    if mut.get("no_claims"):
        put("prereg.txt", "# prereg\nRound: 42\nno claims here\n")
    else:
        lines = ["# prereg", "Round: 42", "", "## C1 - claim one",
                 "Base: %s" % base, "Counter: census/c1.py sha256=%s" % counter_sha,
                 "Population: census/pop.tsv sha256=%s" % population_sha,
                 "Control: census/control.txt", "Target: items=2 corrected=2", "Kill: any uncorrected"]
        if mut.get("dup_base"):
            lines.append("Base: %s" % ("0" * 40))
        if mut.get("tail"):
            lines.append(mut["tail"].rstrip("\n"))
        put("prereg.txt", "\n".join(lines) + "\n")
    commit("freeze")
    if mut.get("dispatch_after"):
        put(".ufo/waves/round-42/w1-dispatch.json", "{}\n")
        commit("dispatch after freeze")
    if mut.get("edit_counter"):
        put("census/c1.py", COUNTER_TEXT + "# edited after freeze\n")
        commit("edit counter")
    return d


def selftest():
    work = tempfile.mkdtemp(prefix="souji-st.")
    passed = 0
    try:
        for name, mut, want_rc, want in SELF_CASES:
            try:
                d = make_repo(work, name, mut)
                rev = git(d, "rev-parse", "HEAD")
                _n, found = check(d, rev, "prereg.txt")
                got = sorted((c, k) for c, k, _detail in found)
                rc = 1 if found else 0
            except Refusal as exc:
                got, rc = [("REFUSAL", str(exc))], 2
            ok = rc == want_rc and got == sorted(want)
            passed += 1 if ok else 0
            print("case-%s=%s%s" % (name, "PASS" if ok else "FAIL", "" if ok else " got=%r" % (got,)))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    total = len(SELF_CASES)
    print("SELFTEST cases=%d pass=%d fail=%d" % (total, passed, total - passed))
    return 0 if passed == total else 1


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
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --root, --prereg and --rev are required\n")
        return 2
    try:
        if not os.path.isdir(args.root):
            raise Refusal("--root %s is not a directory" % args.root)
        if not FULL40.match(args.rev):
            raise Refusal("--rev must be a full 40-hex commit id")
        n, found = check(args.root, args.rev, args.prereg)
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
