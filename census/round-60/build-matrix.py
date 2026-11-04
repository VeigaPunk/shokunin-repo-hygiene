#!/usr/bin/env python3
"""build-matrix.py - round-60 C1 frozen 8-case fixture builder (seat S60ExecMatrix).

Builds each case's synthetic git repository from scratch with a fixed identity,
fixed dates and fixed tree bytes, so every commit hash baked into the case
files reproduces byte-for-byte on rebuild. The runner (c1-counter.py) rebuilds
the same repositories from the DELIVERED case files and verifies the hashes
pinned in each case's expected.txt before measuring anything.

Fixture repositories live only under --scratch (never delivered); each
delivered case dir carries at most 6 small files: pre.txt (preregistration),
counter.py (the instrument bytes), pop.tsv (population), the control receipt
file(s) and expected.txt (the pinned hashes + expected verdict row).

Usage:
  python3 -B build-matrix.py --out DELIVERY_DIR --scratch SCRATCH_DIR

Writes DELIVERY_DIR/c1-matrix.tsv (header `case<TAB>expect<TAB>control_receipt<TAB>class`,
exactly 8 data rows), DELIVERY_DIR/matrix/<case>/... and DELIVERY_DIR/matrix/stubs/
{stub-accept.py,stub-refuse.py}, then prints `pin <relpath> <sha256>` per file.

Construction notes (disclosed limits):
- A commit tree cannot contain its own hash, so the forgery-rev-at-freeze case
  names the freeze commit through the lightweight tag `freezemark` placed on
  the freeze commit; the receipt's `rev=freezemark` resolves to the freeze
  commit itself, which is not a strict ancestor of anything. The expected
  verdict (refuse) holds whether the substance arm resolves the tag or refuses
  a non-full40 rev.
- The substance binding is BYTES, not execution (round-57 recorder doctrine):
  instrument_sha256 pins the counter blob bytes; the counter is never run.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

FIX_DATE = "2026-11-04T00:00:00+00:00"
IDENT_NAME = "S60ExecMatrix Fixture"
IDENT_EMAIL = "s60execmatrix.fixture@example.invalid"
COMMIT_MSG = "fixture"
PREREG = "pre.txt"
COUNTER = "counter.py"
POP = "pop.tsv"
TAG = "freezemark"

COUNTER_BYTES = (
    b"#!/usr/bin/env python3\n"
    b'"""round-60 C1 fixture counter (synthetic instrument, not a lane tool)."""\n'
    b"import sys\n"
    b'print("SUMMARY counter=1 rows=2 findings=0")\n'
    b"sys.exit(0)\n"
)
POP_BYTES = b"row-a\tvalue-a\nrow-b\tvalue-b\n"
COUNTER_CMD = b"python3 -B counter.py --selfcheck"
OTHER_CMD = b"python3 -B tools/souji-verify.sh --quick"
HONEST_OUT = b"SUMMARY counter=1 rows=2 findings=0"


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


def prereg_bytes(base40, shaC, shaP, ctl_names):
    parts = ["Round: 60\n"]
    for i, ctl in enumerate(ctl_names, 1):
        parts.append("## C%d\n" % i)
        parts.append("Base: %s\n" % base40)
        parts.append("Counter: counter.py sha256=%s\n" % shaC)
        parts.append("Population: pop.tsv sha256=%s\n" % shaP)
        parts.append("Control: %s\n" % ctl)
        parts.append("Target: t%d\n" % i)
        parts.append("Kill: k%d\n" % i)
    return "".join(parts).encode("utf-8")


def expected_bytes(name, expect, cls, anc40, freeze40, control_rev40):
    crev = control_rev40 if control_rev40 else TAG + " (tags the freeze commit)"
    lines = ["case=%s" % name, "expect=%s" % expect, "class=%s" % cls,
             "ancestor=%s" % anc40, "freeze=%s" % freeze40, "prereg=" + PREREG,
             "control_rev=%s" % crev]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _gen_honest(base40, shaC, shaP, crev40):
    return receipt_bytes(b"counter.py", shaC.encode(), crev40.encode(), COUNTER_CMD, HONEST_OUT)


def _gen_honest_c2(base40, shaC, shaP, crev40):
    return receipt_bytes(b"counter.py", shaC.encode(), crev40.encode(), COUNTER_CMD + b" --block C2", HONEST_OUT)


def _gen_kind_only(base40, shaC, shaP, crev40):
    return b"EXIT=1\n"


def _gen_digest(base40, shaC, shaP, crev40):
    # instrument_sha256 is the digest of a DIFFERENT real blob (pop.tsv)
    return receipt_bytes(b"counter.py", shaP.encode(), crev40.encode(), COUNTER_CMD, HONEST_OUT)


def _gen_rev_at_freeze(base40, shaC, shaP, crev40):
    # rev names the freeze commit itself (via the freezemark tag)
    return receipt_bytes(b"counter.py", shaC.encode(), TAG.encode(), COUNTER_CMD, HONEST_OUT)


def _gen_rev_missing(base40, shaC, shaP, crev40):
    return receipt_bytes(b"counter.py", shaC.encode(), None, COUNTER_CMD, HONEST_OUT)


def _gen_command_other(base40, shaC, shaP, crev40):
    return receipt_bytes(b"counter.py", shaC.encode(), crev40.encode(), OTHER_CMD, HONEST_OUT)


ORDER = ["honest-1", "honest-2", "honest-3", "forgery-kind-only",
         "forgery-digest", "forgery-rev-at-freeze", "forgery-rev-missing",
         "forgery-command-other"]

CASES = {
    "honest-1": {"pre": [[COUNTER, POP]], "base_commit": 0, "control_rev": 0,
                 "ctls": {"ctl.txt": _gen_honest}, "expect": "accept", "class": "honest"},
    "honest-2": {"pre": [[COUNTER, POP]], "base_commit": 0, "control_rev": 0,
                 "ctls": {"ctl-c1.txt": _gen_honest, "ctl-c2.txt": _gen_honest_c2},
                 "expect": "accept", "class": "honest"},
    "honest-3": {"pre": [[COUNTER], [POP]], "base_commit": 0, "control_rev": 1,
                 "ctls": {"ctl.txt": _gen_honest}, "expect": "accept", "class": "honest"},
    "forgery-kind-only": {"pre": [[COUNTER, POP]], "base_commit": 0, "control_rev": 0,
                          "ctls": {"ctl.txt": _gen_kind_only}, "expect": "refuse", "class": "forgery"},
    "forgery-digest": {"pre": [[COUNTER, POP]], "base_commit": 0, "control_rev": 0,
                       "ctls": {"ctl.txt": _gen_digest}, "expect": "refuse", "class": "forgery"},
    "forgery-rev-at-freeze": {"pre": [[COUNTER, POP]], "base_commit": 0, "control_rev": 0,
                              "ctls": {"ctl.txt": _gen_rev_at_freeze}, "expect": "refuse",
                              "class": "forgery", "tag": True},
    "forgery-rev-missing": {"pre": [[COUNTER, POP]], "base_commit": 0, "control_rev": 0,
                            "ctls": {"ctl.txt": _gen_rev_missing}, "expect": "refuse", "class": "forgery"},
    "forgery-command-other": {"pre": [[COUNTER, POP]], "base_commit": 0, "control_rev": 0,
                              "ctls": {"ctl.txt": _gen_command_other}, "expect": "refuse", "class": "forgery"},
}


def build_case(name, scratch_root):
    """Build one case repo from constants; return (dest, hashes, prereg bytes, ctl bytes)."""
    spec = CASES[name]
    env = build_env(scratch_root)
    dest = os.path.join(scratch_root, name)
    _init_repo(dest, env)
    hashes = []
    for files in spec["pre"]:
        payload = [(f, COUNTER_BYTES if f == COUNTER else POP_BYTES) for f in files]
        hashes.append(_commit_group(dest, env, payload))
    shaC = hashlib.sha256(COUNTER_BYTES).hexdigest()
    shaP = hashlib.sha256(POP_BYTES).hexdigest()
    base40 = hashes[spec["base_commit"]]
    crev = spec.get("control_rev")
    crev40 = hashes[crev] if crev is not None else None
    ctls = {cn: gen(base40, shaC, shaP, crev40) for cn, gen in spec["ctls"].items()}
    preb = prereg_bytes(base40, shaC, shaP, sorted(ctls))
    freeze_payload = [(PREREG, preb)] + sorted(ctls.items())
    freeze = _commit_group(dest, env, freeze_payload)
    if spec.get("tag"):
        _git(dest, env, "tag", TAG, freeze)
    return dest, hashes + [freeze], preb, ctls


def rebuild_case(name, dest, case_dir):
    """Rebuild the case repo from the DELIVERED case files; return (ancestor, freeze) hashes."""
    spec = CASES[name]
    env = build_env(os.path.dirname(os.path.abspath(dest)) or ".")

    def rd(fn):
        with open(os.path.join(case_dir, fn), "rb") as fh:
            return fh.read()

    _init_repo(dest, env)
    hashes = []
    for files in spec["pre"]:
        hashes.append(_commit_group(dest, env, [(f, rd(f)) for f in files]))
    freeze_payload = [(f, rd(f)) for f in [PREREG] + sorted(spec["ctls"])]
    freeze = _commit_group(dest, env, freeze_payload)
    if spec.get("tag"):
        _git(dest, env, "tag", TAG, freeze)
    return hashes[spec["base_commit"]], freeze


STUB_ACCEPT = b"""#!/usr/bin/env python3
\"\"\"stub-always-accept - round-60 C1 matrix control tool. MUST fail the runner's
expectation check (it accepts the forgery cases); stubs=REJECTED requires it.\"\"\"
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
\"\"\"stub-always-refuse - round-60 C1 matrix control tool. MUST fail the runner's
expectation check (it refuses the honest cases); stubs=REJECTED requires it.\"\"\"
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
    rows = []
    for name in ORDER:
        spec = CASES[name]
        dest, hashes, preb, ctls = build_case(name, build_root)
        anc40 = hashes[spec["base_commit"]]
        freeze40 = hashes[-1]
        crev = spec.get("control_rev")
        crev40 = hashes[crev] if crev is not None else None
        case_dir = os.path.join(out, "matrix", name)
        os.makedirs(case_dir)
        emit(os.path.join(case_dir, PREREG), preb)
        emit(os.path.join(case_dir, COUNTER), COUNTER_BYTES)
        emit(os.path.join(case_dir, POP), POP_BYTES)
        for cn in sorted(ctls):
            emit(os.path.join(case_dir, cn), ctls[cn])
        emit(os.path.join(case_dir, "expected.txt"),
             expected_bytes(name, spec["expect"], spec["class"], anc40, freeze40, crev40))
        rows.append((name, spec["expect"], "matrix/%s/%s" % (name, sorted(ctls)[0]), spec["class"]))
        anc2, freeze2 = rebuild_case(name, os.path.join(verify_root, name), case_dir)
        if (anc2, freeze2) != (anc40, freeze40):
            raise SystemExit("build-matrix: rebuild of %s does not reproduce the pinned hashes" % name)
    stub_dir = os.path.join(out, "matrix", "stubs")
    os.makedirs(stub_dir)
    emit(os.path.join(stub_dir, "stub-accept.py"), STUB_ACCEPT)
    emit(os.path.join(stub_dir, "stub-refuse.py"), STUB_REFUSE)
    tsv = "\n".join(["case\texpect\tcontrol_receipt\tclass"] + ["\t".join(r) for r in rows]) + "\n"
    emit(os.path.join(out, "c1-matrix.tsv"), tsv.encode("utf-8"))


def main(argv):
    ap = argparse.ArgumentParser(description="Build the frozen round-60 C1 8-case matrix fixture.")
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
