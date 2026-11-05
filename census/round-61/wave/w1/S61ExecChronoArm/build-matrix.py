#!/usr/bin/env python3
"""build-matrix.py - round-61 C1 frozen 11-case control-chronology fixture builder (seat S61ExecChronoArm).

Builds each case's synthetic git repository from scratch with a fixed identity, fixed dates and fixed
tree bytes, so every commit hash baked into the case files reproduces byte-for-byte on rebuild. The
runner (c1-counter.py) rebuilds the same repositories from the DELIVERED case files and verifies the
hashes pinned in each case's expected.txt before measuring anything.

Usage:
  python3 -B build-matrix.py --out DELIVERY_DIR --scratch SCRATCH_DIR

Writes DELIVERY_DIR/c1-matrix.tsv (header `case<TAB>expect<TAB>control_receipt<TAB>expected_class`,
exactly 11 data rows), DELIVERY_DIR/matrix/<case>/ (the case files plus expected.txt) and
DELIVERY_DIR/matrix/stubs/{stub-accept.py,stub-refuse.py}, then prints `pin <relpath> <sha256>` per file.

Each case is a `layout`: an ordered list of commit GROUPS, each a list of file names. `freeze` is the
index of the group that carries the preregistration; `base` is the group the claims name in Base:.
A receipt names its `rev=` as the commit of group `rev_group` (or the orphan commit for rev-orphan).
Groups after `freeze` exist only in the chrono-after case.

expected_class is the observed finding-id set of the substance arm (candidate-freeze-check.py
--substance) on that case, sorted and comma-joined; `-` for accept rows. It was MEASURED by running the
candidate on each rebuilt case repository, not derived from the code. Every refuse row must name at
least one class.

Disclosed limits:
- chrono-after: the Control receipt is added by a CHILD of the freeze, so it is absent at FREEZE. The
  tool reads the Control blob at FREEZE and reports CONTROL-MISSING before any chronology check runs;
  the chronology arm only checks receipts that are present at FREEZE. The base tool refuses this shape
  too, so it is a do-nothing refusal, not a chronology catch.
- git log for the chronology arm is bounded to FREEZE, so the non-ancestor branches of that arm are
  defensive; the reachable refusal is the add by the freeze commit itself.
- The binding is BYTES, not execution (round-57 recorder doctrine): counter.py is never run.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

FIX_DATE = "2026-11-05T00:00:00+00:00"
IDENT_NAME = "S61ExecChronoArm Fixture"
IDENT_EMAIL = "s61execchronoarm.fixture@example.invalid"
COMMIT_MSG = "fixture"
PREREG = "pre.txt"
COUNTER = "counter.py"
POP = "pop.tsv"
NOTES = "notes.txt"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
HEADER = "case\texpect\tcontrol_receipt\texpected_class"

COUNTER_BYTES = (
    b"#!/usr/bin/env python3\n"
    b'"""round-61 C1 fixture counter (synthetic instrument, not a lane tool)."""\n'
    b"import sys\n"
    b'print("SUMMARY counter=1 rows=2 findings=0")\n'
    b"sys.exit(0)\n"
)
POP_BYTES = b"row-a\tvalue-a\nrow-b\tvalue-b\n"
NOTES_BYTES = b"round-61 fixture filler commit: no claim reads this file.\n"
COUNTER_CMD = b"python3 -B counter.py --selfcheck"
OTHER_CMD = b"python3 -B tools/souji-verify.sh --quick"
HONEST_OUT = b"SUMMARY counter=1 rows=2 findings=0"
SHA_C = hashlib.sha256(COUNTER_BYTES).hexdigest()
SHA_P = hashlib.sha256(POP_BYTES).hexdigest()

# Observed (not derived) substance-arm finding-id sets; filled from a candidate run over the staged repos.
EXPECTED_CLASS = {
    "honest-1": "-",
    "honest-2": "-",
    "honest-3": "-",
    "forgery-kind-only": "CONTROL-COMMAND-MISSING,CONTROL-INSTRUMENT-MISSING,CONTROL-REV-MISSING",
    "forgery-digest": "CONTROL-INSTRUMENT-MISMATCH",
    "forgery-rev-missing": "CONTROL-REV-MISSING",
    "forgery-command-other": "CONTROL-COMMAND-MISMATCH",
    "forgery-rev-orphan": "CONTROL-REV-NOT-BEFORE-FREEZE",
    "chrono-at-freeze": "CONTROL-ADDED-NOT-BEFORE-FREEZE",
    "chrono-after": "CONTROL-MISSING",
    "chrono-ancestor": "-",
}

ORDER = ["honest-1", "honest-2", "honest-3", "forgery-kind-only", "forgery-digest",
         "forgery-rev-missing", "forgery-command-other", "forgery-rev-orphan",
         "chrono-at-freeze", "chrono-after", "chrono-ancestor"]

# receipts: file -> (kind, rev_group). kinds: honest, honest-block-c2, kind-only, digest, rev-missing,
# command-other, rev-orphan. (rev_group is None for kind-only and rev-orphan.)
CASES = {
    "honest-1": {"layout": [[COUNTER, POP], ["ctl.txt"], [PREREG]], "freeze": 2, "base": 0,
                 "receipts": {"ctl.txt": ("honest", 0)}, "orphan": False, "expect": "accept"},
    "honest-2": {"layout": [[COUNTER, POP], ["ctl-c1.txt", "ctl-c2.txt"], [PREREG]], "freeze": 2, "base": 0,
                 "receipts": {"ctl-c1.txt": ("honest", 0), "ctl-c2.txt": ("honest-block-c2", 0)},
                 "orphan": False, "expect": "accept"},
    "honest-3": {"layout": [[COUNTER], [POP], ["ctl.txt"], [PREREG]], "freeze": 3, "base": 0,
                 "receipts": {"ctl.txt": ("honest", 1)}, "orphan": False, "expect": "accept"},
    "forgery-kind-only": {"layout": [[COUNTER, POP], ["ctl.txt"], [PREREG]], "freeze": 2, "base": 0,
                          "receipts": {"ctl.txt": ("kind-only", None)}, "orphan": False, "expect": "refuse"},
    "forgery-digest": {"layout": [[COUNTER, POP], ["ctl.txt"], [PREREG]], "freeze": 2, "base": 0,
                       "receipts": {"ctl.txt": ("digest", 0)}, "orphan": False, "expect": "refuse"},
    "forgery-rev-missing": {"layout": [[COUNTER, POP], ["ctl.txt"], [PREREG]], "freeze": 2, "base": 0,
                            "receipts": {"ctl.txt": ("rev-missing", 0)}, "orphan": False, "expect": "refuse"},
    "forgery-command-other": {"layout": [[COUNTER, POP], ["ctl.txt"], [PREREG]], "freeze": 2, "base": 0,
                              "receipts": {"ctl.txt": ("command-other", 0)}, "orphan": False,
                              "expect": "refuse"},
    "forgery-rev-orphan": {"layout": [[COUNTER, POP], ["ctl.txt"], [PREREG]], "freeze": 2, "base": 0,
                           "receipts": {"ctl.txt": ("rev-orphan", None)}, "orphan": True, "expect": "refuse"},
    "chrono-at-freeze": {"layout": [[COUNTER, POP], [PREREG, "ctl.txt"]], "freeze": 1, "base": 0,
                         "receipts": {"ctl.txt": ("honest", 0)}, "orphan": False, "expect": "refuse"},
    "chrono-after": {"layout": [[COUNTER, POP], [PREREG], ["ctl.txt"]], "freeze": 1, "base": 0,
                     "receipts": {"ctl.txt": ("honest", 0)}, "orphan": False, "expect": "refuse"},
    "chrono-ancestor": {"layout": [[COUNTER, POP], ["ctl.txt"], [NOTES], [PREREG]], "freeze": 3, "base": 0,
                        "receipts": {"ctl.txt": ("honest", 0)}, "orphan": False, "expect": "accept"},
}


def build_env(home):
    """Whitelisted environment: caller GIT_* variables cannot leak into a verdict."""
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "LC_ALL": "C",
        "HOME": home,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_AUTHOR_NAME": IDENT_NAME,
        "GIT_AUTHOR_EMAIL": IDENT_EMAIL,
        "GIT_COMMITTER_NAME": IDENT_NAME,
        "GIT_COMMITTER_EMAIL": IDENT_EMAIL,
        "GIT_AUTHOR_DATE": FIX_DATE,
        "GIT_COMMITTER_DATE": FIX_DATE,
    }


def _git(dest, env, *args):
    p = subprocess.run(["git", "-C", dest] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env, check=False)
    if p.returncode != 0:
        raise RuntimeError("git %s failed in %s: %s" % (args[0], dest, p.stderr.decode("utf-8", "replace").strip()))
    return p.stdout


def _init_repo(dest, env):
    if os.path.lexists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    _git(dest, env, "init", "-q", "-b", "matrix")
    top = _git(dest, env, "rev-parse", "--show-toplevel").decode("utf-8", "replace").strip()
    if os.path.realpath(top) != os.path.realpath(dest):
        raise RuntimeError("fixture toplevel %r is not %r" % (top, dest))


def _orphan(dest, env):
    """A parentless commit on the empty tree, referenced by no branch or tag."""
    return _git(dest, env, "commit-tree", EMPTY_TREE, "-m", "orphan").decode("utf-8", "replace").strip()


def _commit_group(dest, env, payload):
    for name, data in payload:
        fp = os.path.join(dest, name)
        with open(fp, "wb") as fh:
            fh.write(data)
        os.chmod(fp, 0o644)
    _git(dest, env, "add", "-A")
    _git(dest, env, "-c", "commit.gpgsign=false", "commit", "-q", "-m", COMMIT_MSG)
    return _git(dest, env, "rev-parse", "HEAD").decode("utf-8", "replace").strip()


def receipt_bytes(instrument, sha, rev, command, out, exitcode=1):
    lines = []
    if instrument is not None:
        lines.append(b"instrument=" + instrument)
    if sha is not None:
        lines.append(b"instrument_sha256=" + sha)
    if rev is not None:
        lines.append(b"rev=" + rev)
    if command is not None:
        lines.append(b"command=" + command)
    lines.append(out)
    lines.append(b"EXIT=%d" % exitcode)
    return b"\n".join(lines) + b"\n"


def prereg_bytes(base40, ctl_names):
    parts = ["Round: 61\n"]
    for i, ctl in enumerate(ctl_names, 1):
        parts.append("## C%d\n" % i)
        parts.append("Base: %s\n" % base40)
        parts.append("Counter: counter.py sha256=%s\n" % SHA_C)
        parts.append("Population: pop.tsv sha256=%s\n" % SHA_P)
        parts.append("Control: %s\n" % ctl)
        parts.append("Target: t%d\n" % i)
        parts.append("Kill: k%d\n" % i)
    return "".join(parts).encode("utf-8")


def receipt_for(kind, h, orphan, rg):
    counter = b"counter.py"
    if kind == "rev-orphan":
        rev = orphan.encode("ascii")
    elif rg is not None:
        rev = h[rg].encode("ascii")
    else:
        rev = None
    if kind == "honest":
        return receipt_bytes(counter, SHA_C.encode(), rev, COUNTER_CMD, HONEST_OUT)
    if kind == "honest-block-c2":
        return receipt_bytes(counter, SHA_C.encode(), rev, COUNTER_CMD + b" --block C2", HONEST_OUT)
    if kind == "kind-only":
        return b"EXIT=1\n"
    if kind == "digest":
        return receipt_bytes(counter, SHA_P.encode(), rev, COUNTER_CMD, HONEST_OUT)
    if kind == "rev-missing":
        return receipt_bytes(counter, SHA_C.encode(), None, COUNTER_CMD, HONEST_OUT)
    if kind == "command-other":
        return receipt_bytes(counter, SHA_C.encode(), rev, OTHER_CMD, HONEST_OUT)
    if kind == "rev-orphan":
        return receipt_bytes(counter, SHA_C.encode(), rev, COUNTER_CMD, HONEST_OUT)
    raise ValueError("unknown receipt kind %r" % kind)


def render(name, fname, h, orphan):
    """Bytes of one case file; h = commit ids of the groups already built."""
    spec = CASES[name]
    if fname == COUNTER:
        return COUNTER_BYTES
    if fname == POP:
        return POP_BYTES
    if fname == NOTES:
        return NOTES_BYTES
    if fname == PREREG:
        return prereg_bytes(h[spec["base"]], sorted(spec["receipts"]))
    kind, rg = spec["receipts"][fname]
    return receipt_for(kind, h, orphan, rg)


def build_case(name, scratch_root):
    """Build one case repo from constants; return (dest, group commit ids, orphan or None)."""
    spec = CASES[name]
    env = build_env(scratch_root)
    dest = os.path.join(scratch_root, name)
    _init_repo(dest, env)
    orphan = _orphan(dest, env) if spec["orphan"] else None
    h = []
    for group in spec["layout"]:
        payload = [(f, render(name, f, h, orphan)) for f in group]
        h.append(_commit_group(dest, env, payload))
    return dest, h, orphan


def rebuild_case(name, dest, case_dir):
    """Rebuild the case repo from the DELIVERED case files; return the pinned commit ids."""
    spec = CASES[name]
    env = build_env(os.path.dirname(os.path.abspath(dest)) or ".")
    _init_repo(dest, env)
    orphan = _orphan(dest, env) if spec["orphan"] else None
    h = []
    for group in spec["layout"]:
        payload = []
        for f in group:
            with open(os.path.join(case_dir, f), "rb") as fh:
                payload.append((f, fh.read()))
        h.append(_commit_group(dest, env, payload))
    return {"base": h[spec["base"]], "freeze": h[spec["freeze"]], "orphan": orphan or "-"}


STUB_ACCEPT = b"""#!/usr/bin/env python3
\"\"\"stub-always-accept - round-61 C1 matrix control tool. MUST fail the runner's
expectation check (it accepts the refuse rows); stubs=REJECTED requires it.\"\"\"
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--root")
parser.add_argument("--prereg")
parser.add_argument("--rev")
parser.add_argument("--substance", action="store_true")
parser.parse_known_args()
print("SUMMARY claims=1 findings=0")
sys.exit(0)
"""

STUB_REFUSE = b"""#!/usr/bin/env python3
\"\"\"stub-always-refuse - round-61 C1 matrix control tool. MUST fail the runner's
expectation check (it refuses the accept rows); stubs=REJECTED requires it.\"\"\"
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--root")
parser.add_argument("--prereg")
parser.add_argument("--rev")
parser.add_argument("--substance", action="store_true")
parser.parse_known_args()
print("FINDING C1 STUB always-refuse")
print("SUMMARY claims=1 findings=1")
sys.exit(1)
"""


def emit(path, data):
    with open(path, "wb") as fh:
        fh.write(data)
    os.chmod(path, 0o644)


def materialize(out, scratch):
    build_root = os.path.join(scratch, "repos")
    verify_root = os.path.join(scratch, "verify")
    os.makedirs(build_root)
    os.makedirs(verify_root)
    rows = []
    for name in ORDER:
        spec = CASES[name]
        dest, h, orphan = build_case(name, build_root)
        pins = {"base": h[spec["base"]], "freeze": h[spec["freeze"]], "orphan": orphan or "-"}
        case_dir = os.path.join(out, "matrix", name)
        os.makedirs(case_dir)
        for f in sorted({f for group in spec["layout"] for f in group}):
            emit(os.path.join(case_dir, f), render(name, f, h, orphan))
        cls = EXPECTED_CLASS[name]
        if cls is None:
            raise SystemExit("build-matrix: expected_class for %s is not pinned" % name)
        if (spec["expect"] == "accept") != (cls == "-"):
            raise SystemExit("build-matrix: %s expect=%s but expected_class=%s" % (name, spec["expect"], cls))
        lines = ["case=%s" % name, "expect=%s" % spec["expect"], "expected_class=%s" % cls,
                 "ancestor=%s" % pins["base"], "freeze=%s" % pins["freeze"], "orphan=%s" % pins["orphan"],
                 "prereg=%s" % PREREG]
        emit(os.path.join(case_dir, "expected.txt"), ("\n".join(lines) + "\n").encode("utf-8"))
        ctl = sorted(spec["receipts"])[0]
        rows.append((name, spec["expect"], "matrix/%s/%s" % (name, ctl), cls))
        got = rebuild_case(name, os.path.join(verify_root, name), case_dir)
        if got != pins:
            raise SystemExit("build-matrix: rebuild of %s does not reproduce the pinned hashes" % name)
    stub_dir = os.path.join(out, "matrix", "stubs")
    os.makedirs(stub_dir)
    emit(os.path.join(stub_dir, "stub-accept.py"), STUB_ACCEPT)
    emit(os.path.join(stub_dir, "stub-refuse.py"), STUB_REFUSE)
    tsv = "\n".join([HEADER] + ["\t".join(r) for r in rows]) + "\n"
    emit(os.path.join(out, "c1-matrix.tsv"), tsv.encode("utf-8"))


def main(argv):
    ap = argparse.ArgumentParser(description="Build the frozen round-61 C1 11-case chronology matrix.")
    ap.add_argument("--out", required=True, help="delivery dir for c1-matrix.tsv and matrix/")
    ap.add_argument("--scratch", required=True, help="persistent scratch dir for fixture repos")
    args = ap.parse_args(argv)
    out = os.path.abspath(args.out)
    scratch = os.path.abspath(args.scratch)
    os.makedirs(out, exist_ok=True)
    os.makedirs(scratch, exist_ok=True)
    materialize(out, scratch)
    for root, dirs, files in os.walk(out):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            with open(p, "rb") as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
            print("pin %s %s" % (os.path.relpath(p, out), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
