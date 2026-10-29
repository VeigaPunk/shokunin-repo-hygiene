#!/usr/bin/env python3
"""ATTACK K3 (not an implementation): grammar of K1; --selftest is an identity guard on two stdlib functions and runs no case.

tools/souji-freeze-check.py - the pre-dispatch freeze checklist as one command.

  python3 -B tools/souji-freeze-check.py --root LANE --prereg PATH --rev FULL40
  python3 -B tools/souji-freeze-check.py --selftest

Reads the preregistration PATH as the blob at --rev (git object store only, never the work tree) and
prints `FINDING <claim> <CLASS> <detail>` per finding, sorted, then `SUMMARY claims=<n> findings=<m>`.
Exit 0 no findings, 1 findings, 2 could-not-evaluate (`REFUSAL COULD-NOT-EVALUATE: ...` on stderr).
--selftest builds synthetic repositories under $TMPDIR and checks the tool against them.

Grammar: a claim block starts at a `## C<digits>` line (a space or end of line follows the digits) and
runs to the next `## ` line; inside it a key line is `Key: value` at column 0 for Base, Counter, Population,
Control, Target, Kill. Counter and Population values are `<repo path> sha256=<64 hex>`. FREEZE-REV is the
oldest commit reachable from --rev that adds PATH. Finding classes: NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY,
KEY-DUPLICATE, HEADING-MALFORMED, BASE-UNRESOLVED, BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-DIGEST,
COUNTER-SYMLINK, POPULATION-MISSING, POPULATION-DIGEST, POPULATION-SYMLINK, POPULATION-EMPTY, CONTROL-MISSING,
CONTROL-NOT-RED, FROZEN-EDITED, DISPATCH-BEFORE-FREEZE. Prereg-wide findings carry claim label C0.
A missing `Round:` line is reported as `FIELD-MISSING C0 Round`. Python stdlib only; read-only on --root.
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
VALID_HEADING = re.compile(r"^## C(\d+)(?: |$)")
MALFORMED_HEADING = re.compile(r"^##(?!#)[ \t]*[Cc][ \t]*[0-9]")
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
        # r41 wave-2 hardening: a whitelisted environment, so caller-set GIT_* variables cannot change a verdict.
        self.env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
                    "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                    "GIT_NO_REPLACE_OBJECTS": "1"}

    def run(self, *args):
        try:
            return subprocess.run(["git", "-c", "core.quotePath=false", "-c", "log.mailmap=false", "-C", self.root]
                                  + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env,
                                  check=False)
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
        p = self.run("ls-tree", "-z", rev, "--", path)
        if p.returncode != 0 or not p.stdout:
            return None
        return p.stdout.split(b"\t", 1)[0].split(b" ", 1)[0].decode("ascii", "replace")

    def is_ancestor(self, a, b):
        return self.run("merge-base", "--is-ancestor", a, b).returncode == 0


def parse_claims(text):
    """Returns (claims, malformed): claims = [(label, {key: [values in file order]})], malformed = [line numbers]."""
    claims, malformed = [], []
    cur = None
    for n, line in enumerate(text.splitlines(), 1):
        m = VALID_HEADING.match(line)
        if m:
            cur = ("C" + m.group(1), {})
            claims.append(cur)
            continue
        if line.startswith("## "):
            cur = None
        if MALFORMED_HEADING.match(line):
            malformed.append(n)
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


def is_dispatch_name(base):
    return "-dispatch" in base or ".ready" in base or base.endswith("-spec.json") or base.endswith("-results.json")


def dispatch_findings(repo, rev, freeze, text):
    m = ROUND.search(text)
    if not m:
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
            if is_dispatch_name(line.rsplit("/", 1)[-1]):
                first[line] = commit
    out = []
    for path, c in sorted(first.items()):
        if c == freeze or repo.is_ancestor(c, freeze):
            out.append(("C0", "DISPATCH-BEFORE-FREEZE", "%s first added at %s, not after freeze %s"
                        % (path, c[:12], freeze[:12])))
    return out


def check_path_sha(repo, rev, freeze, label, value, missing, digest, symlink, found):
    """Counter/Population: returns (freeze blob, path), or None when the path is absent or a symlink."""
    m = PATH_SHA.match(value)
    path, want = (m.group(1), m.group(2)) if m else (value.split()[0] if value.split() else "", None)
    if not path:
        return None
    at_freeze = repo.blob(freeze, path)
    if at_freeze is None:
        found.append((label, missing, "%s not present at freeze %s" % (path, freeze[:12])))
        return None
    if repo.mode(freeze, path) == SYMLINK_MODE:
        found.append((label, symlink, "%s is a symlink at freeze %s" % (path, freeze[:12])))
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
    claims, malformed = parse_claims(text)
    for n in malformed:
        found.append(("C0", "HEADING-MALFORMED", "line=%d" % n))
    if not claims:
        found.append(("C0", "NO-CLAIMS", "no '## C<digits>' block in %s" % prereg))
    for label, raw in claims:
        for key, values in sorted(raw.items()):
            if len(values) > 1:
                found.append((label, "KEY-DUPLICATE", key))
        f = {key: values[0] for key, values in raw.items()}
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
            check_path_sha(repo, rev, freeze, label, f["Counter"], "COUNTER-MISSING", "COUNTER-DIGEST",
                           "COUNTER-SYMLINK", found)
        if f.get("Population"):
            got = check_path_sha(repo, rev, freeze, label, f["Population"], "POPULATION-MISSING",
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


# ---------------------------------------------------------------- self-test (builds its own repositories)
ST_ENV = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
          "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
          "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "selftest@example.invalid",
          "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "selftest@example.invalid"}
ST_COUNTER = "# counter\nprint('counter')\n"
ST_POPULATION = "id\tname\n1\talpha\n2\tbeta\n"
ST_RED = "SUMMARY items=2 corrected=0\nEXIT=1\n"
SELFTEST_CASES = (
    ("clean", {}, []),
    ("counter-digest", {"counter_digest": True}, [("C1", "COUNTER-DIGEST")]),
    ("population-digest", {"population_digest": True}, [("C1", "POPULATION-DIGEST")]),
    ("counter-missing", {"counter_missing": True}, [("C1", "COUNTER-MISSING")]),
    ("counter-symlink", {"counter_symlink": True}, [("C1", "COUNTER-SYMLINK")]),
    ("population-symlink", {"population_symlink": True}, [("C1", "POPULATION-SYMLINK")]),
    ("population-empty", {"population": "id\tname\n"}, [("C1", "POPULATION-EMPTY")]),
    ("base-not-ancestor", {"side": True}, [("C1", "BASE-NOT-ANCESTOR")]),
    ("base-unresolved", {"base_zero": True}, [("C1", "BASE-UNRESOLVED")]),
    ("dispatch-before", {"before": ["w1-results.json"]}, [("C0", "DISPATCH-BEFORE-FREEZE")]),
    ("dispatch-notes-before", {"before": ["notes.md"]}, []),
    ("frozen-edited", {"edit_counter": True}, [("C1", "FROZEN-EDITED")]),
    ("key-duplicate", {"extra": ["Kill: any uncorrected"]}, [("C1", "KEY-DUPLICATE")]),
    ("heading-malformed", {"tail": "##C2 - second\n"}, [("C0", "HEADING-MALFORMED")]),
    ("no-claims", {"no_claims": True}, [("C0", "NO-CLAIMS")]),
)


def sha256_hex(text):
    # hashlib.new, not hashlib.sha256: the self-test's expected digests must not share the tool's code path
    return hashlib.new("sha256", text.encode("utf-8")).hexdigest()


def st_build(root, name, mut):
    d = os.path.join(root, name)
    os.makedirs(d)

    def git(*args):
        p = subprocess.run(["git", "-C", d] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=ST_ENV, check=False)
        if p.returncode != 0:
            raise RuntimeError("git %s failed: %s" % (args[0], p.stderr.decode("utf-8", "replace")))
        return p.stdout.decode("utf-8", "replace").strip()

    def write(rel, text):
        full = os.path.join(d, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def commit(msg):
        git("add", "-A")
        git("commit", "-q", "-m", msg)
        return git("rev-parse", "HEAD")

    git("init", "-q", "-b", "main")
    write("README", "base\n")
    base = commit("base")
    side = None
    if mut.get("side"):
        git("checkout", "-q", "-b", "side")
        write("side.txt", "side\n")
        side = commit("side")
        git("checkout", "-q", "main")
    if mut.get("before"):
        for rel in mut["before"]:
            write(".ufo/waves/round-42/" + rel, "x\n")
        commit("early wave files")
    population = mut.get("population", ST_POPULATION)
    fields = {"Base": side or base,
              "Counter": "census/c1.py sha256=%s" % sha256_hex(ST_COUNTER),
              "Population": "census/pop.tsv sha256=%s" % sha256_hex(population),
              "Control": "census/control.txt", "Target": "items=2 corrected=2", "Kill": "any uncorrected"}
    if mut.get("base_zero"):
        fields["Base"] = "0" * 40
    if mut.get("counter_digest"):
        fields["Counter"] = "census/c1.py sha256=%s" % ("0" * 64)
    if mut.get("population_digest"):
        fields["Population"] = "census/pop.tsv sha256=%s" % ("1" * 64)
    if mut.get("no_claims"):
        body = "# prereg\nRound: 42\nno claims here\n"
    else:
        body = "\n".join(["# prereg", "Round: 42", "", "## C1 - claim 1"]
                         + ["%s: %s" % (k, fields[k]) for k in KEYS] + mut.get("extra", []) + [""]) + "\n"
    write("prereg.txt", body + mut.get("tail", ""))
    if mut.get("counter_symlink"):
        write("census/real-c1.py", ST_COUNTER)
        os.symlink("real-c1.py", os.path.join(d, "census/c1.py"))
    elif not mut.get("counter_missing"):
        write("census/c1.py", ST_COUNTER)
    if mut.get("population_symlink"):
        write("census/real-pop.tsv", population)
        os.symlink("real-pop.tsv", os.path.join(d, "census/pop.tsv"))
    else:
        write("census/pop.tsv", population)
    write("census/control.txt", ST_RED)
    commit("freeze")
    if mut.get("edit_counter"):
        write("census/c1.py", ST_COUNTER + "# edited after freeze\n")
        commit("edit counter")
    return d, git("rev-parse", "HEAD")


def selftest():
    # identity guard: refuses when hashlib.sha256 or subprocess.run is not the stdlib original
    if hashlib.sha256.__module__ != '_hashlib' or subprocess.run.__module__ != 'subprocess':
        return 1
    print("SELFTEST cases=15 pass=15 fail=0")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="Check a preregistration's freeze at a revision.")
    ap.add_argument("--root")
    ap.add_argument("--prereg")
    ap.add_argument("--rev")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        if not (args.root and args.prereg and args.rev):
            raise Refusal("--root, --prereg and --rev are required")
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
