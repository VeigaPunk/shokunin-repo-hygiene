#!/usr/bin/env python3
"""c1-counter.py - round-61 C1 matrix runner (seat S61ExecChronoArm).

  python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv \
      --base-tool-rev c7228424c3919ecf142bab1aec8181722d86467b --rev FULL40 --work DIR \
      [--new-tool PATH] [--new-arm candidate|plain]

Rebuilds each frozen case repository under --work from the delivered matrix fixture (bytes from
matrix/<case>/, commit structure from build-matrix.py next to this script), verifies the rebuilt
ancestor / freeze / orphan hashes against the case's expected.txt, then measures two arms over every
case. BOTH arms run with --substance; they differ only in the tool bytes:

  BASE  the tool bytes at --base-tool-rev, read from the lane's git object store
        (`git show REV:tools/souji-freeze-check.py`);
  NEW   the candidate bytes: --new-tool, default candidate-freeze-check.py beside this script.
        --new-arm plain runs the BASE bytes in the NEW slot (the do-nothing control);
  STUBS matrix/stubs/{stub-accept,stub-refuse}.py, invoked like NEW.

A tool run's verdict is accept (exit 0) or refuse (exit 1); any other exit is an error. A refuse row
passes only when the verdict is refuse AND the sorted set of FINDING classes equals the row's
expected_class (comma-joined in the matrix). Per row it prints

  CASE <name> expect=<e> base=<v> base_findings=<ids|-> new=<v> new_findings=<ids|-> expected_class=<cls|->

then

  SUMMARY matrix=<n> base_forgeries=<a> base_honest=<b> new_forgeries=<c> new_honest=<d> class_mismatches=<e> stubs=REJECTED|ACCEPTED

and EXIT=<rc>. new_forgeries = NEW accepts on refuse rows; new_honest = NEW accepts on accept rows;
class_mismatches = refuse rows whose NEW finding-class set differs from expected_class (an accepted
refuse row counts, its set is empty). stubs=REJECTED iff BOTH stubs' verdict patterns differ from the
expectations.

Exit 0 iff every NEW verdict equals expect, class_mismatches=0 and stubs=REJECTED; 1 otherwise;
2 on could-not-evaluate: an unresolved --rev or --base-tool-rev, a missing or malformed matrix, a
missing or volatile (/tmp- or TMPDIR-backed) --work, an expected.txt that disagrees with its matrix
row, a fixture hash mismatch, a missing fixture part, or a BASE/NEW/STUB run that exits with neither
0 nor 1.

Read-only on --root (git object store only); writes only under --work.
Python stdlib only.
"""
import argparse
import importlib.util
import os
import re
import subprocess
import sys

FULL40 = re.compile(r"^[0-9a-f]{40}$")
CLASS_LIST = re.compile(r"^[A-Z][A-Z0-9-]*(,[A-Z][A-Z0-9-]*)*$")
TOOL_REL = "tools/souji-freeze-check.py"
STUB_NAMES = ("stub-accept.py", "stub-refuse.py")
HEADER = "case\texpect\tcontrol_receipt\texpected_class"
ROWS = 11
EXTRA = ["--substance"]


def die(msg):
    sys.stderr.write("COULD-NOT-EVALUATE: %s\n" % msg)
    sys.exit(2)


def sanitize_env(home):
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
    }


def git_run(lane, env, *args):
    return subprocess.run(["git", "-C", lane] + list(args), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=env, check=False)


def resolve_commit(lane, rev, env):
    p = git_run(lane, env, "rev-parse", "--verify", "-q", rev + "^{commit}")
    out = p.stdout.decode("utf-8", "replace").strip()
    return out if p.returncode == 0 and FULL40.match(out) else None


def persistent_work_problem(path):
    if not path:
        return "no --work given"
    if not os.path.isdir(path):
        return "--work %s is not an existing directory" % path
    if not os.access(path, os.W_OK):
        return "--work %s is not writable" % path
    real = os.path.realpath(path)
    volatile = [os.path.realpath("/tmp")]
    for var in ("TMPDIR", "TEMP", "TMP"):
        v = os.environ.get(var)
        if v:
            volatile.append(os.path.realpath(v))
    for v in volatile:
        if real == v or real.startswith(v.rstrip(os.sep) + os.sep):
            return ("--work %s resolves under volatile directory %s; a persistent "
                    "work dir is required" % (path, v))
    return None


def expected_set(cls):
    return sorted(set(x for x in cls.split(",") if x)) if cls != "-" else []


def load_matrix(path):
    if not os.path.isfile(path):
        die("matrix file %s not found" % path)
    with open(path, "rb") as fh:
        raw = fh.read().decode("utf-8", "replace")
    lines = raw.splitlines()
    if not lines or lines[0] != HEADER:
        die("matrix header must be exactly %r" % HEADER)
    rows = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            die("matrix line %d: expected 4 tab-separated fields" % n)
        case, expect, ctl, cls = parts
        if expect not in ("accept", "refuse"):
            die("matrix line %d: expect must be accept|refuse" % n)
        if expect == "accept" and cls != "-":
            die("matrix line %d: accept rows carry expected_class '-'" % n)
        if expect == "refuse" and not CLASS_LIST.match(cls):
            die("matrix line %d: refuse rows need a comma-joined finding-id list, found %r" % (n, cls))
        if not re.match(r"^[A-Za-z0-9._-]+$", case):
            die("matrix line %d: bad case name %r" % (n, case))
        rows.append({"case": case, "expect": expect, "ctl": ctl, "cls": cls, "line": n})
    if len(rows) != ROWS:
        die("matrix must hold exactly %d data rows, found %d" % (ROWS, len(rows)))
    if len(set(r["case"] for r in rows)) != ROWS:
        die("matrix case names are not unique")
    return rows


def load_builder(script_dir):
    path = os.path.join(script_dir, "build-matrix.py")
    if not os.path.isfile(path):
        die("fixture builder build-matrix.py not found next to c1-counter.py (%s)" % path)
    spec = importlib.util.spec_from_file_location("build_matrix", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        die("cannot load build-matrix.py: %s" % exc)
    if not hasattr(mod, "rebuild_case") or not hasattr(mod, "CASES"):
        die("build-matrix.py lacks rebuild_case/CASES")
    return mod


def parse_expected(path):
    out = {}
    if not os.path.isfile(path):
        die("%s missing" % path)
    with open(path, "rb") as fh:
        for line in fh.read().decode("utf-8", "replace").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    for k in ("case", "expect", "expected_class", "ancestor", "freeze", "orphan", "prereg"):
        if k not in out:
            die("%s: missing %s=" % (path, k))
    return out


def run_arm(tool, repo, prereg, rev, env, cwd):
    cmd = [sys.executable, "-B", tool, "--root", repo, "--prereg", prereg, "--rev", rev] + EXTRA
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=cwd, check=False)
    if p.returncode == 0:
        verdict = "accept"
    elif p.returncode == 1:
        verdict = "refuse"
    else:
        verdict = "error"
    return verdict, p


def finding_ids(proc):
    ids = set()
    for line in proc.stdout.decode("utf-8", "replace").splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "FINDING":
            ids.add(parts[2])
    return sorted(ids)


def fmt_ids(ids):
    return ",".join(ids) if ids else "-"


def main(argv):
    ap = argparse.ArgumentParser(description="Run the frozen round-61 C1 11-case matrix (base vs candidate arm).")
    ap.add_argument("--root", required=True, help="lane root (git object store; read-only)")
    ap.add_argument("--matrix", required=True, help="path to c1-matrix.tsv")
    ap.add_argument("--base-tool-rev", required=True, help="rev of the base tool bytes in --root")
    ap.add_argument("--rev", required=True, help="measurement revision in --root (full 40-hex)")
    ap.add_argument("--work", required=True, help="persistent work dir (case repos are rebuilt here)")
    ap.add_argument("--new-tool", help="candidate tool (default candidate-freeze-check.py beside this script)")
    ap.add_argument("--new-arm", choices=("candidate", "plain"), default="candidate",
                    help="candidate: NEW slot runs the candidate bytes; plain: runs the BASE bytes")
    args = ap.parse_args(argv)

    lane = os.path.abspath(args.root)
    matrix_path = os.path.abspath(args.matrix)
    matrix_dir = os.path.dirname(matrix_path)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    work = os.path.abspath(args.work)
    env = sanitize_env(work)
    if not os.path.isdir(lane):
        die("--root %s is not a directory" % lane)
    base_rev = resolve_commit(lane, args.base_tool_rev, env)
    if base_rev is None:
        die("--base-tool-rev %s does not resolve to a commit in %s" % (args.base_tool_rev, lane))
    meas_rev = resolve_commit(lane, args.rev, env)
    if meas_rev is None:
        die("--rev %s does not resolve to a commit in %s" % (args.rev, lane))
    why = persistent_work_problem(work)
    if why:
        die(why)
    rows = load_matrix(matrix_path)
    builder = load_builder(script_dir)

    base_blob = git_run(lane, env, "show", "%s:%s" % (base_rev, TOOL_REL))
    if base_blob.returncode != 0:
        die("%s is not present at %s in %s" % (TOOL_REL, base_rev, lane))
    base_tool = os.path.join(work, "base-tool.py")
    with open(base_tool, "wb") as fh:
        fh.write(base_blob.stdout)
    os.chmod(base_tool, 0o644)

    if args.new_arm == "plain":
        new_tool = base_tool
    else:
        new_tool = os.path.abspath(args.new_tool) if args.new_tool else os.path.join(script_dir, "candidate-freeze-check.py")
    if not os.path.isfile(new_tool):
        die("new tool %s not found" % new_tool)
    stubs = [os.path.join(matrix_dir, "matrix", "stubs", s) for s in STUB_NAMES]
    for s in stubs:
        if not os.path.isfile(s):
            die("stub control %s not found (part of the frozen fixture)" % s)

    sys.stderr.write("matrix lane=%s base-tool=%s@%s new-tool=%s rev=%s new-arm=%s\n"
                     % (lane, TOOL_REL, base_rev[:12], new_tool, meas_rev[:12], args.new_arm))

    base_forg = base_hon = new_forg = new_hon = class_mis = 0
    new_verdicts, stub_rows, had_error = [], [], False
    for row in rows:
        case_dir = os.path.join(matrix_dir, "matrix", row["case"])
        ctl_path = os.path.join(matrix_dir, row["ctl"])
        if os.path.realpath(os.path.dirname(ctl_path)) != os.path.realpath(case_dir):
            die("matrix line %d: control_receipt %s escapes the case fixture dir" % (row["line"], row["ctl"]))
        if not os.path.isfile(ctl_path):
            die("matrix line %d: control receipt %s missing" % (row["line"], row["ctl"]))
        exp = parse_expected(os.path.join(case_dir, "expected.txt"))
        if (exp["case"], exp["expect"], exp["expected_class"]) != (row["case"], row["expect"], row["cls"]):
            die("%s: expected.txt disagrees with the matrix row" % row["case"])
        repo_dir = os.path.join(work, row["case"])
        try:
            got = builder.rebuild_case(row["case"], repo_dir, case_dir)
        except Exception as exc:
            die("rebuilding case %s failed: %s" % (row["case"], exc))
        if (got["base"], got["freeze"], got["orphan"]) != (exp["ancestor"], exp["freeze"], exp["orphan"]):
            die("%s: rebuilt hashes base=%s freeze=%s orphan=%s do not match the pinned values"
                % (row["case"], got["base"], got["freeze"], got["orphan"]))
        base_v, base_p = run_arm(base_tool, repo_dir, exp["prereg"], exp["freeze"], env, work)
        new_v, new_p = run_arm(new_tool, repo_dir, exp["prereg"], exp["freeze"], env, work)
        for label, v, p in (("BASE", base_v, base_p), ("NEW", new_v, new_p)):
            if v == "error":
                had_error = True
                detail = p.stderr.decode("utf-8", "replace").strip().splitlines()
                sys.stderr.write("%s: %s arm failed: %s\n" % (row["case"], label,
                                                              detail[0] if detail else "exit %d" % p.returncode))
        base_ids = finding_ids(base_p)
        new_ids = finding_ids(new_p)
        if row["expect"] == "refuse":
            if base_v == "accept":
                base_forg += 1
            if new_v == "accept":
                new_forg += 1
            if new_ids != expected_set(row["cls"]):
                class_mis += 1
        else:
            if base_v == "accept":
                base_hon += 1
            if new_v == "accept":
                new_hon += 1
        new_verdicts.append(new_v)
        stub_vs = []
        for s in stubs:
            sv, _sp = run_arm(s, repo_dir, exp["prereg"], exp["freeze"], env, work)
            stub_vs.append(sv)
        stub_rows.append(stub_vs)
        print("CASE %s expect=%s base=%s base_findings=%s new=%s new_findings=%s expected_class=%s"
              % (row["case"], row["expect"], base_v, fmt_ids(base_ids), new_v, fmt_ids(new_ids), row["cls"]))
    sys.stdout.flush()

    expects = [r["expect"] for r in rows]
    stub_lists = [list(v) for v in zip(*stub_rows)] if stub_rows else []
    rejected = [v != expects for v in stub_lists]
    stubs_state = "REJECTED" if (len(rejected) == len(STUB_NAMES) and all(rejected)) else "ACCEPTED"
    print("SUMMARY matrix=%d base_forgeries=%d base_honest=%d new_forgeries=%d new_honest=%d "
          "class_mismatches=%d stubs=%s"
          % (len(rows), base_forg, base_hon, new_forg, new_hon, class_mis, stubs_state))
    sys.stdout.flush()
    if had_error:
        sys.stderr.write("COULD-NOT-EVALUATE: a BASE, NEW or stub tool run exited with neither 0 (accept) nor 1 (refuse)\n")
        return 2
    ok = new_verdicts == expects and class_mis == 0 and stubs_state == "REJECTED"
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        rc = main(sys.argv[1:])
    except SystemExit as exc:
        rc = exc.code if isinstance(exc.code, int) else 2
    print("EXIT=%d" % rc)
    sys.exit(rc)
