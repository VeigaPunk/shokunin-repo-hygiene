#!/usr/bin/env python3
"""c1-counter.py - round-60 C1 matrix runner (seat S60ExecMatrix).

  python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv \
      --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --rev FULL40 --work DIR
      [--new-tool PATH]

Rebuilds each frozen case repository under --work from the delivered matrix
fixture (bytes from matrix/<case>/, commit structure from build-matrix.py next
to this script), verifies the rebuilt ancestor/freeze hashes against the case's
expected.txt, then measures three arms over every case:

  BASE  the tool bytes at --base-tool-rev, read from the lane's git object
        store (`git show REV:tools/souji-freeze-check.py`), invoked without
        --substance;
  NEW   the substance arm (default LANE/tools/souji-freeze-check.py, override
        with --new-tool), invoked with --substance (--new-arm substance, the
        default) or without it (--new-arm plain, for measuring tool bytes that
        predate the substance arm on both arms);
  STUBS the two fixture control tools matrix/stubs/{stub-accept,stub-refuse}.py,
        invoked like NEW.

A tool run's verdict is accept (exit 0) or refuse (exit 1); any other exit is
an error. Per case it prints
  CASE <name> expect=<accept|refuse> base=<accept|refuse> new=<accept|refuse>
in matrix order, then
  SUMMARY matrix=8 forgeries_accepted=<n> honest_accepted=<m> stubs=REJECTED|ACCEPTED
where forgeries_accepted / honest_accepted count BASE-arm accepts over the
forgery / honest classes. stubs=REJECTED iff BOTH stubs' verdict patterns fail
the expectation check (an always-accept stub cannot satisfy the refuse rows, an
always-refuse stub cannot satisfy the accept rows).

Exit 0 iff every NEW verdict equals expect AND stubs=REJECTED; 1 otherwise;
2 on could-not-evaluate: an unresolved --rev or --base-tool-rev, a missing or
malformed matrix, a missing or volatile (non-persistent, /tmp- or TMPDIR-backed)
--work, a fixture hash mismatch against expected.txt, a missing fixture part,
or a BASE/NEW tool run that exits with neither 0 nor 1.

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
TOOL_REL = "tools/souji-freeze-check.py"
STUB_NAMES = ("stub-accept.py", "stub-refuse.py")
HEADER = "case\texpect\tcontrol_receipt\tclass"


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
        if cls not in ("honest", "forgery"):
            die("matrix line %d: class must be honest|forgery" % n)
        if not re.match(r"^[A-Za-z0-9._-]+$", case):
            die("matrix line %d: bad case name %r" % (n, case))
        rows.append({"case": case, "expect": expect, "ctl": ctl, "class": cls, "line": n})
    if len(rows) != 8:
        die("matrix must hold exactly 8 data rows, found %d" % len(rows))
    if len(set(r["case"] for r in rows)) != 8:
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
    with open(path, "rb") as fh:
        for line in fh.read().decode("utf-8", "replace").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    for k in ("case", "expect", "class", "ancestor", "freeze", "prereg"):
        if k not in out:
            die("%s: missing %s=" % (path, k))
    return out


def run_arm(tool, extra, repo, prereg, rev, env, cwd):
    cmd = [sys.executable, "-B", tool, "--root", repo, "--prereg", prereg, "--rev", rev] + extra
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=env, cwd=cwd, check=False)
    if p.returncode == 0:
        return "accept", p
    if p.returncode == 1:
        return "refuse", p
    return "error", p


def main(argv):
    ap = argparse.ArgumentParser(description="Run the frozen round-60 C1 8-case matrix (base vs substance arm).")
    ap.add_argument("--root", required=True, help="lane root (git object store; read-only)")
    ap.add_argument("--matrix", required=True, help="path to c1-matrix.tsv")
    ap.add_argument("--base-tool-rev", required=True, help="rev of the base tool bytes in --root")
    ap.add_argument("--rev", required=True, help="measurement revision in --root (full 40-hex)")
    ap.add_argument("--work", required=True, help="persistent work dir (case repos are rebuilt here)")
    ap.add_argument("--new-tool", help="substance-arm tool (default <root>/tools/souji-freeze-check.py)")
    ap.add_argument("--new-arm", choices=("substance", "plain"), default="substance",
                    help="invoke the new tool with (substance) or without (plain) --substance")
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

    new_tool = os.path.abspath(args.new_tool) if args.new_tool else os.path.join(lane, TOOL_REL)
    if not os.path.isfile(new_tool):
        die("new tool %s not found" % new_tool)
    stubs = [os.path.join(matrix_dir, "matrix", "stubs", s) for s in STUB_NAMES]
    for s in stubs:
        if not os.path.isfile(s):
            die("stub control %s not found (part of the frozen fixture)" % s)

    sys.stderr.write("matrix lane=%s base-tool=%s@%s new-tool=%s rev=%s new-arm=%s\n"
                     % (lane, TOOL_REL, base_rev[:12], new_tool, meas_rev[:12], args.new_arm))
    new_extra = ["--substance"] if args.new_arm == "substance" else []

    base_accepts = {"forgery": 0, "honest": 0}
    # r60 amendment 1 (pre-freeze, before any after-data): the summary reports BOTH arms, so the
    # claim's after-state is readable from the same line the do-nothing control prints.
    new_accepts = {"forgery": 0, "honest": 0}
    new_verdicts = []
    stub_rows = []
    had_error = False
    for row in rows:
        case_dir = os.path.join(matrix_dir, os.path.dirname(row["ctl"]))
        if os.path.realpath(case_dir) != os.path.realpath(os.path.join(matrix_dir, "matrix", row["case"])):
            die("matrix line %d: control_receipt %s escapes the case fixture dir"
                % (row["line"], row["ctl"]))
        if not os.path.isfile(os.path.join(matrix_dir, row["ctl"])):
            die("matrix line %d: control receipt %s missing" % (row["line"], row["ctl"]))
        exp = parse_expected(os.path.join(case_dir, "expected.txt"))
        if (exp["case"], exp["expect"], exp["class"]) != (row["case"], row["expect"], row["class"]):
            die("%s: expected.txt disagrees with the matrix row" % row["case"])
        repo_dir = os.path.join(work, row["case"])
        try:
            anc, freeze = builder.rebuild_case(row["case"], repo_dir, case_dir)
        except Exception as exc:
            die("rebuilding case %s failed: %s" % (row["case"], exc))
        if (anc, freeze) != (exp["ancestor"], exp["freeze"]):
            die("%s: rebuilt hashes ancestor=%s freeze=%s do not match pinned ancestor=%s freeze=%s"
                % (row["case"], anc, freeze, exp["ancestor"], exp["freeze"]))
        base_v, base_p = run_arm(base_tool, [], repo_dir, exp["prereg"], freeze, env, work)
        new_v, new_p = run_arm(new_tool, new_extra, repo_dir, exp["prereg"], freeze, env, work)
        if base_v == "error":
            had_error = True
            detail = base_p.stderr.decode("utf-8", "replace").strip().splitlines()
            sys.stderr.write("%s: base arm failed: %s\n" % (row["case"], detail[0] if detail else "exit %d" % base_p.returncode))
        if new_v == "error":
            had_error = True
            detail = new_p.stderr.decode("utf-8", "replace").strip().splitlines()
            sys.stderr.write("%s: new arm failed: %s\n" % (row["case"], detail[0] if detail else "exit %d" % new_p.returncode))
        new_verdicts.append(new_v)
        if base_v == "accept":
            base_accepts[row["class"]] += 1
        if new_v == "accept":
            new_accepts[row["class"]] += 1
        stub_vs = []
        for s in stubs:
            sv, _sp = run_arm(s, new_extra, repo_dir, exp["prereg"], freeze, env, work)
            stub_vs.append(sv)
        stub_rows.append(stub_vs)
        print("CASE %s expect=%s base=%s new=%s" % (row["case"], row["expect"], base_v, new_v))
    sys.stdout.flush()

    expects = [r["expect"] for r in rows]
    stub_lists = [list(v) for v in zip(*stub_rows)] if stub_rows else []
    rejected = [v != expects for v in stub_lists]
    stubs_state = "REJECTED" if (len(rejected) == len(STUB_NAMES) and all(rejected)) else "ACCEPTED"
    new_ok = new_verdicts == expects
    print("SUMMARY matrix=%d forgeries_accepted=%d honest_accepted=%d "
          "new_forgeries=%d new_honest=%d stubs=%s"
          % (len(rows), base_accepts["forgery"], base_accepts["honest"],
             new_accepts["forgery"], new_accepts["honest"], stubs_state))
    sys.stdout.flush()
    if had_error:
        sys.stderr.write("COULD-NOT-EVALUATE: a BASE or NEW tool run exited with neither 0 (accept) nor 1 (refuse)\n")
        return 2
    return 0 if (new_ok and stubs_state == "REJECTED") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
