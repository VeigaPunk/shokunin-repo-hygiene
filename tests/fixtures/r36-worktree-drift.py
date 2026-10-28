#!/usr/bin/env python3
"""r36-worktree-drift.py — fixture for tools/souji-worktree-drift.py.

Each case builds a synthetic fleet in scratch (real `git init` repositories and
a real `git worktree add`), writes one census-record shape, and checks the
tool's exit code and drift rows. The prunable case removes a registered
worktree directory, which is what makes `git worktree prune --dry-run -v`
report a candidate on stderr (the r35 record counted stdout and so read 0).

Cases:
  match            record equals the live numerator           -> rc 0, no drift
  regs-changed     record overstates repoA's registrations    -> rc 1, REGS-CHANGED
  prunable-changed registered worktree removed                -> rc 1, PRUNABLE-CHANGED live=1
  absent           record names a repository that is gone     -> rc 1, ABSENT
  malformed        a row outside the census schema            -> rc 2, RECORD-MALFORMED
  total-mismatch   TOTAL disagrees with the REPO rows         -> rc 2, RECORD-MALFORMED
  empty            no REPO rows                               -> rc 2, RECORD-EMPTY
  unrecorded       a live repository the record omits         -> rc 1, UNRECORDED
  read-only        fleet tree unchanged by the run            -> no file/git metadata write

The control runs the discriminating cases against an always-equal stub: if the
stub reproduces every expected verdict the fixture is falsified and prints
`control=STUB-NOT-REJECTED`.

CLI:
  python3 -B tests/fixtures/r36-worktree-drift.py [--tool PATH] [--work DIR]

Exit: 0 all cases pass and the control is rejected, 1 otherwise.
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

STUB = """#!/usr/bin/env python3
import re, sys
record = sys.argv[sys.argv.index("--record") + 1]
rows = [l for l in open(record).read().splitlines() if l.startswith("REPO")]
regs = sum(int(re.search(r"regs=(\\d+)", l).group(1)) for l in rows)
prunable = sum(int(re.search(r"prunable=(\\d+)", l).group(1)) for l in rows)
print("SUMMARY record=%s record_repos=%d record_regs=%d record_prunable=%d live_repos=%d live_regs=%d live_prunable=%d drift_rows=0 unreachable=0" % (record, len(rows), regs, prunable, len(rows), regs, prunable))
sys.exit(0)
"""

ENV = dict(os.environ)
ENV.update(
    {
        "GIT_AUTHOR_NAME": "fixture",
        "GIT_COMMITTER_NAME": "fixture",
        "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    }
)


def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)


def make_repo(path, branch="main"):
    os.makedirs(path)
    sh(["git", "init", "-q", "-b", branch, path])
    with open(os.path.join(path, "file.txt"), "w", encoding="utf-8") as handle:
        handle.write("base\n")
    sh(["git", "-C", path, "add", "file.txt"])
    sh(["git", "-C", path, "commit", "-qm", "base"])
    return path


def snapshot(root):
    entries = []
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            path = os.path.join(base, name)
            try:
                st = os.lstat(path)
                digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
            except OSError:
                continue
            entries.append("%s\t%d\t%d\t%s" % (os.path.relpath(path, root), st.st_size, st.st_mtime_ns, digest))
    return entries


def write(path, text):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def build(scratch, name):
    root = os.path.join(scratch, name)
    fleet = os.path.join(root, "fleet")
    os.makedirs(fleet)
    make_repo(os.path.join(fleet, "alpha"))
    make_repo(os.path.join(fleet, "beta"))
    return root, fleet


def record(root, rows, total=None, name="record.tsv"):
    path = os.path.join(root, name)
    lines = ["REPO\t%s\tregs=%d\tprunable=%d" % (n, r, p) for n, r, p in rows]
    if total is not None:
        lines.append("TOTAL\trepos=%d\tregs=%d\tprunable=%d" % total)
    write(path, "\n".join(lines) + "\n")
    return path


def invoke(tool, fleet, rec, extra=None, env_extra=None):
    env = None
    if env_extra:
        env = dict(os.environ)
        env.update(ENV)
        env.update(env_extra)
    cmd = ["python3", "-B", tool, "--root", fleet, "--record", rec, "--timeout", "30"] + list(extra or [])
    proc = subprocess.run(cmd, env=env or ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    out = proc.stdout + proc.stderr
    summary = [l for l in proc.stdout.splitlines() if l.startswith("SUMMARY")]
    return proc.returncode, out, (summary[-1] if summary else "")


def check(name, condition, detail, results):
    results.append((name, bool(condition), detail))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool")
    ap.add_argument("--work")
    args = ap.parse_args(argv)
    lane_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    tool = args.tool or os.path.join(lane_root, "tools", "souji-worktree-drift.py")
    work = args.work or os.environ.get("TMPDIR") or "/var/tmp"
    if not os.path.isdir(work):
        sys.stderr.write("usage: --work must name an existing directory (%s)\n" % work)
        return 2
    scratch = tempfile.mkdtemp(prefix="souji-r36-drift.", dir=work)
    results = []
    try:
        # match
        root, fleet = build(scratch, "match")
        rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], total=(2, 2, 0))
        rc, out, summary = invoke(tool, fleet, rec)
        check("match", rc == 0 and "drift_rows=0" in summary, "rc=%d %s" % (rc, summary), results)

        # regs-changed
        root, fleet = build(scratch, "regs")
        rec = record(root, [("alpha", 2, 0), ("beta", 1, 0)], total=(2, 3, 0))
        rc, out, summary = invoke(tool, fleet, rec)
        check("regs-changed", rc == 1 and "REGS-CHANGED\talpha" in out, "rc=%d rows=%r" % (rc, out.splitlines()[:3]), results)

        # prunable-changed: a registered worktree whose directory is removed
        root, fleet = build(scratch, "prunable")
        wt = os.path.join(root, "alpha-wt")
        sh(["git", "-C", os.path.join(fleet, "alpha"), "worktree", "add", "-q", wt, "-b", "wt"])
        shutil.rmtree(wt)
        rec = record(root, [("alpha", 2, 0), ("beta", 1, 0)], total=(2, 3, 0))
        rc, out, summary = invoke(tool, fleet, rec)
        check(
            "prunable-changed",
            rc == 1 and "PRUNABLE-CHANGED\talpha" in out and "live=1" in out,
            "rc=%d rows=%r" % (rc, out.splitlines()[:3]),
            results,
        )

        # absent
        root, fleet = build(scratch, "absent")
        rec = record(root, [("alpha", 1, 0), ("gone", 1, 0)], total=(2, 2, 0))
        rc, out, summary = invoke(tool, fleet, rec)
        check("absent", rc == 1 and "ABSENT\tgone" in out, "rc=%d rows=%r" % (rc, out.splitlines()[:3]), results)

        # malformed
        root, fleet = build(scratch, "malformed")
        rec = os.path.join(root, "record.tsv")
        write(rec, "REPO\talpha\tregs=1\tprunable=0\njunk row\n")
        rc, out, summary = invoke(tool, fleet, rec)
        check("malformed", rc == 2 and "RECORD-MALFORMED" in out + summary, "rc=%d" % rc, results)

        # total mismatch
        root, fleet = build(scratch, "total")
        rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], total=(3, 2, 0))
        rc, out, summary = invoke(tool, fleet, rec)
        check("total-mismatch", rc == 2 and "RECORD-MALFORMED" in out + summary, "rc=%d" % rc, results)

        # empty
        root, fleet = build(scratch, "empty")
        rec = os.path.join(root, "record.tsv")
        write(rec, "TOTAL\trepos=0\tregs=0\tprunable=0\n")
        rc, out, summary = invoke(tool, fleet, rec)
        check("empty", rc == 2 and "RECORD-EMPTY" in out + summary, "rc=%d" % rc, results)

        # unrecorded
        root, fleet = build(scratch, "unrecorded")
        make_repo(os.path.join(fleet, "gamma"))
        rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], total=(2, 2, 0))
        rc, out, summary = invoke(tool, fleet, rec)
        check(
            "unrecorded",
            rc == 1
            and "UNRECORDED\tgamma" in out
            and "live_repos=2" in summary
            and "live_regs=2 " in summary + " ",
            "rc=%d rows=%r summary=%r" % (rc, out.splitlines()[:3], summary),
            results,
        )

        # read-only envelope
        root, fleet = build(scratch, "readonly")
        rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], total=(2, 2, 0))
        before = snapshot(fleet)
        invoke(tool, fleet, rec)
        after = snapshot(fleet)
        check("read-only", before == after, "changed=%d" % len(set(before) ^ set(after)), results)

        # json containment (r36 A2, wave seat SwarmSentinel24 F1)
        root, fleet = build(scratch, "json-inside")
        rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], total=(2, 2, 0))
        leak = os.path.join(fleet, "alpha", "leak.json")
        rc, out, summary = invoke(tool, fleet, rec, extra=["--json", leak])
        check(
            "json-inside-tree",
            rc == 2 and "JSON-INSIDE-MEASURED-TREE" in out and not os.path.exists(leak),
            "rc=%d exists=%s rows=%r" % (rc, os.path.exists(leak), out.splitlines()[:3]),
            results,
        )

        # trace-env scrub (r36 A2, wave seat SwarmSentinel24 F2)
        root, fleet = build(scratch, "trace-env")
        rec = record(root, [("alpha", 1, 0), ("beta", 1, 0)], total=(2, 2, 0))
        trace = os.path.join(root, "trace.log")
        rc, out, summary = invoke(tool, fleet, rec, env_extra={"GIT_TRACE2_EVENT": trace})
        check(
            "trace-env",
            rc == 0 and "drift_rows=0" in summary and not os.path.exists(trace),
            "rc=%d trace_created=%s %s" % (rc, os.path.exists(trace), summary),
            results,
        )

        # live_repos arithmetic (r36 A4, wave seat SwarmExecutor22 F1): an absent
        # recorded repo plus a discovered-but-unreachable one used to go negative.
        root, fleet = build(scratch, "live-repos")
        rec = record(root, [("alpha", 1, 0), ("gone", 1, 0)], total=(2, 2, 0))
        broken = os.path.join(fleet, "broken")
        os.makedirs(broken)
        write(os.path.join(broken, ".git"), "gitdir: /nonexistent/gitdir\n")
        rc, out, summary = invoke(tool, fleet, rec)
        value = 0
        if "live_repos=" in summary:
            value = int(summary.split("live_repos=")[1].split()[0])
        check(
            "live-repos-non-negative",
            rc == 1 and value == 1 and "ABSENT\tgone" in out and "UNREACHABLE\tbroken" in out,
            "rc=%d live_repos=%d rows=%r" % (rc, value, out.splitlines()[:4]),
            results,
        )

        stub_path = os.path.join(scratch, "stub.py")
        write(stub_path, STUB)
        os.chmod(stub_path, 0o755)
        replicated = []
        for label in ("regs", "prunable", "absent", "unrecorded"):
            root = os.path.join(scratch, "stub-" + label)
            os.makedirs(root)
            fleet = os.path.join(root, "fleet")
            os.makedirs(fleet)
            make_repo(os.path.join(fleet, "alpha"))
            if label == "unrecorded":
                make_repo(os.path.join(fleet, "beta"))
                rec = record(root, [("alpha", 1, 0)], total=(1, 1, 0))
            elif label == "absent":
                rec = record(root, [("alpha", 1, 0), ("gone", 1, 0)], total=(2, 2, 0))
            elif label == "prunable":
                wt = os.path.join(root, "alpha-wt")
                sh(["git", "-C", os.path.join(fleet, "alpha"), "worktree", "add", "-q", wt, "-b", "wt"])
                shutil.rmtree(wt)
                make_repo(os.path.join(fleet, "beta"))
                rec = record(root, [("alpha", 2, 0), ("beta", 1, 0)], total=(2, 3, 0))
            else:
                make_repo(os.path.join(fleet, "beta"))
                rec = record(root, [("alpha", 2, 0)], total=(1, 2, 0))
            rc, out, summary = invoke(stub_path, fleet, rec)
            if rc != 0:
                replicated.append(label)
        control_ok = not replicated
        print("control=%s%s" % ("STUB-REJECTED" if control_ok else "STUB-NOT-REJECTED", "" if control_ok else " replicated=" + ",".join(replicated)))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    for name, ok, detail in results:
        print("case-%s=%s %s" % (name, "PASS" if ok else "FAIL", "" if ok else detail))
    print("SUMMARY cases=%d pass=%d fail=%d control=%s" % (len(results), passed, failed, "STUB-REJECTED" if control_ok else "STUB-NOT-REJECTED"))
    return 0 if failed == 0 and control_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
