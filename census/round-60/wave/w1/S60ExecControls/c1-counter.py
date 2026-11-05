#!/usr/bin/env python3
"""C1 counter, minimal equivalent (souji round 60 pre-freeze controls, seat S60ExecControls).

The wave's frozen runner seat (S60ExecMatrix) and substance-arm seat
(S60ExecFreezeArm) had delivered nothing into .ufo/waves/round-60/w1/ at
control time, so this runner plus build-matrix.py rebuild the frozen 8-case
design and drive BOTH arms strictly from git blob bytes:

  base arm: tools/souji-freeze-check.py at --base-tool-rev
  new arm:  tools/souji-freeze-check.py at --rev

Do-nothing control: run with --rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 so
the base tool is also the new arm; those bytes carry no --substance arm, the
Control receipt bindings are unenforced, and all five forgeries are accepted
(RED: exit 1, forgeries_accepted=5).

Output: one `CASE <name> expect=<accept|refuse> base=<accept|refuse> new=<accept|refuse>`
line per case (S60ExecMatrix format) plus evidence lines (MATRIX, ARM,
EXPECT-CLASS, BASE-OUT, NEW-OUT, WARN, STUB), then
`SUMMARY matrix=<n> forgeries_accepted=<f> honest_accepted=<h> stubs=REJECTED|ACCEPTED`.
Exit 0 iff every new-arm verdict on the selected rows equals expect AND both
stub tools are rejected; 1 otherwise; 2 on could-not-evaluate (unresolved rev,
missing matrix, unusable --work). Stubs are always scored against the FULL
matrix, never the --only selection.

Usage:
  python3 -B c1-counter.py --root LANE --matrix c1-matrix.tsv \
      --base-tool-rev 1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4 --rev FULL40 \
      --work DIR [--only REGEX]
"""
import argparse
import hashlib
import importlib.util
import os
import re
import subprocess
import sys

TOOL_PATH = "tools/souji-freeze-check.py"
FULL40 = re.compile(r"^[0-9a-f]{40}$")


def git(root, *args, check=True):
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "LC_ALL": "C",
           "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    p = subprocess.run(["git", "-C", str(root)] + list(args), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env)
    if check and p.returncode != 0:
        raise RuntimeError("git -C %s %s -> %d: %s" % (root, " ".join(args), p.returncode,
                                                       p.stderr.decode("utf-8", "replace").strip()))
    return p


def resolve(root, rev):
    p = git(root, "rev-parse", "--verify", "-q", rev + "^{commit}", check=False)
    out = p.stdout.decode("utf-8", "replace").strip()
    return out if (p.returncode == 0 and FULL40.match(out)) else None


def blob(root, rev, path):
    p = git(root, "cat-file", "blob", "%s:%s" % (rev, path), check=False)
    return p.stdout if p.returncode == 0 else None


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_builder(here):
    path = os.path.join(here, "build-matrix.py")
    spec = importlib.util.spec_from_file_location("r60_build_matrix", path)
    if spec is None:
        raise RuntimeError("cannot load builder at %s" % path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_matrix(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        if head != ["case", "expect", "control_receipt", "class"]:
            raise ValueError("matrix header must be 'case\\texpect\\tcontrol_receipt\\tclass', got %r"
                             % head)
        for ln, line in enumerate(fh, 2):
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            parts.extend([""] * (4 - len(parts)))
            if parts[1] not in ("accept", "refuse"):
                raise ValueError("matrix line %d: expect must be accept|refuse, got %r"
                                 % (ln, parts[1]))
            rows.append({"case": parts[0], "expect": parts[1],
                         "control_receipt": parts[2], "class": parts[3]})
    if not rows:
        raise ValueError("matrix has no data rows")
    names = [r["case"] for r in rows]
    if len(set(names)) != len(names):
        raise ValueError("matrix has duplicate case names")
    return rows


def run_tool(python, tool_path, case_dir, tip):
    try:
        p = subprocess.run([python, "-B", tool_path, "--root", case_dir,
                            "--prereg", "pre.txt", "--rev", tip],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
    except subprocess.TimeoutExpired:
        return "refuse", 124, ["TIMEOUT tool did not finish in 180s"]
    lines = [l for l in p.stdout.decode("utf-8", "replace").splitlines() if l.strip()]
    return ("accept" if p.returncode == 0 else "refuse"), p.returncode, lines


def die2(msg):
    sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: %s\n" % msg)
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser(description="Round-60 C1 substance matrix counter (minimal equivalent).")
    ap.add_argument("--root", required=True, help="lane repo (read-only; blob source)")
    ap.add_argument("--matrix", required=True, help="c1-matrix.tsv path")
    ap.add_argument("--base-tool-rev", required=True)
    ap.add_argument("--rev", required=True, help="revision whose tool bytes are the new arm")
    ap.add_argument("--work", required=True, help="scratch dir for case repos and arm copies")
    ap.add_argument("--only", default=None, help="regex over case names to select rows")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.root):
        return die2("--root %s is not a directory" % args.root)
    base_rev = resolve(args.root, args.base_tool_rev)
    new_rev = resolve(args.root, args.rev)
    if base_rev is None:
        return die2("--base-tool-rev %s does not resolve in %s" % (args.base_tool_rev, args.root))
    if new_rev is None:
        return die2("--rev %s does not resolve in %s" % (args.rev, args.root))
    if not os.path.isfile(args.matrix):
        return die2("matrix %s is missing" % args.matrix)
    try:
        os.makedirs(args.work, exist_ok=True)
        probe = os.path.join(args.work, ".probe")
        with open(probe, "w") as fh:
            fh.write("x")
        os.remove(probe)
    except OSError as exc:
        return die2("--work %s is not usable: %s" % (args.work, exc))
    try:
        rows = read_matrix(args.matrix)
    except ValueError as exc:
        return die2(str(exc))
    selected = rows
    if args.only:
        try:
            rx = re.compile(args.only)
        except re.error as exc:
            return die2("bad --only regex: %s" % exc)
        selected = [r for r in rows if rx.search(r["case"])]
        if not selected:
            return die2("--only %r selected 0 of %d rows" % (args.only, len(rows)))

    base_bytes = blob(args.root, base_rev, TOOL_PATH)
    new_bytes = blob(args.root, new_rev, TOOL_PATH)
    if base_bytes is None or new_bytes is None:
        return die2("%s absent at %s" % (TOOL_PATH,
                                         base_rev if base_bytes is None else new_rev))

    try:
        builder = load_builder(os.path.dirname(os.path.abspath(__file__)))
        cases, stubs = builder.build_cases(args.work)
    except Exception as exc:
        return die2("fixture build failed: %s: %s" % (type(exc).__name__, exc))

    arm_base = os.path.join(args.work, "tool-base.py")
    arm_new = os.path.join(args.work, "tool-new.py")
    with open(arm_base, "wb") as fh:
        fh.write(base_bytes)
    with open(arm_new, "wb") as fh:
        fh.write(new_bytes)

    python = sys.executable or "python3"
    print("# c1-counter minimal equivalent (souji round 60 pre-freeze control, seat S60ExecControls)")
    print("MATRIX %s rows=%d selected=%d" % (os.path.abspath(args.matrix), len(rows), len(selected)))
    print("ARM base rev=%s sha256=%s substance-arm=%s"
          % (base_rev, sha256(base_bytes), "present" if b"--substance" in base_bytes else "absent"))
    print("ARM new rev=%s sha256=%s substance-arm=%s"
          % (new_rev, sha256(new_bytes), "present" if b"--substance" in new_bytes else "absent"))

    forgeries = honest = mismatched = 0
    for r in selected:
        c = cases.get(r["case"])
        if c is None:
            return die2("matrix row %r has no built case repo" % r["case"])
        bv, brc, blines = run_tool(python, arm_base, c["dir"], c["tip"])
        nv, nrc, nlines = run_tool(python, arm_new, c["dir"], c["tip"])
        print("CASE %s expect=%s base=%s new=%s" % (r["case"], r["expect"], bv, nv))
        print("EXPECT-CLASS %s %s" % (r["case"], r["class"] or "-"))
        for l in blines:
            print("BASE-OUT %s | %s" % (r["case"], l))
        for l in nlines:
            print("NEW-OUT %s | %s" % (r["case"], l))
        if brc not in (0, 1) or nrc not in (0, 1):
            print("WARN %s arm exit outside 0/1: base=%d new=%d" % (r["case"], brc, nrc))
        if r["expect"] == "refuse" and nv == "accept":
            forgeries += 1
        if r["expect"] == "accept" and nv == "accept":
            honest += 1
        if nv != r["expect"]:
            mismatched += 1

    stub_rejected = True
    for tag in sorted(stubs):
        spath = stubs[tag]
        matched = 0
        for r in rows:  # stubs are scored against the FULL matrix, never the --only selection
            c = cases[r["case"]]
            v, _rc, _l = run_tool(python, spath, c["dir"], c["tip"])
            if v == r["expect"]:
                matched += 1
        rejected = matched < len(rows)
        print("STUB %s rows=%d matched=%d %s" % (tag, len(rows), matched,
                                                 "REJECTED" if rejected else "ACCEPTED"))
        stub_rejected = stub_rejected and rejected

    print("SUMMARY matrix=%d forgeries_accepted=%d honest_accepted=%d stubs=%s"
          % (len(selected), forgeries, honest, "REJECTED" if stub_rejected else "ACCEPTED"))
    return 0 if (mismatched == 0 and stub_rejected) else 1


if __name__ == "__main__":
    sys.exit(main())
