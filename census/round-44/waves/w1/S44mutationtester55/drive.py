#!/usr/bin/env python3
"""drive.py — bounded behavioral detector for the round-44 C2 discrimination property.

Runs the audit-under-test against (1) the real tool blob extracted from the
frozen wave commit, (2) the c2-counter.py STUB_CLEAN bytes, (3) the
c2-counter.py STUB_FINDINGS bytes, and applies the counter's verdict rules
verbatim (legs hidden_v2 / clean_stub / findings_stub, rule
`v is not None and v[1] > 0 and v[0] < v[2]`).

usage: drive.py AUDIT_PATH WORK_SUBDIR [EXTRA_TOOL]
  with EXTRA_TOOL: runs ONLY the audit against that tool (probe mode).
Writes nothing outside the seat scratch tree.
"""
import hashlib
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
REV = "d314fd6e85d62565344fa6c4b102f52f62297884"
SCRATCH = "/fast/scratch/hyaku/souji-r44/S44mutationtester55"
STUB_CLEAN = "import sys\nprint('SUMMARY claims=1 findings=0')\nsys.exit(0)\n"
STUB_FINDINGS = ("import sys\nprint('FINDING C1 NO-CLAIMS x')\n"
                 "print('SUMMARY claims=0 findings=1')\nsys.exit(1)\n")


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
         "TMPDIR": scratch, "GIT_CONFIG_NOSYSTEM": "1",
         "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
         "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"}
    return e


def audit_verdict(p):
    """Verbatim from c2-counter.py: (pass, fail, total) or None on crash/no SUMMARY."""
    if p is None:
        return None
    m = re.search(r"^SUMMARY scenarios=(\d+) pass=(\d+) fail=(\d+)",
                  p.stdout.decode("utf-8", "replace"), re.M)
    if not m:
        return None
    return (int(m.group(2)), int(m.group(3)), int(m.group(1)))


def run(argv, cwd, timeout=1200):
    try:
        return subprocess.run(argv, capture_output=True, cwd=cwd, env=env(SCRATCH),
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def show(p, label):
    if p is None:
        print("%s: TIMEOUT/NO-RUN" % label)
        return
    print("%s rc=%d" % (label, p.returncode))
    sys.stdout.write(p.stdout.decode("utf-8", "replace"))
    err = p.stderr.decode("utf-8", "replace").strip()
    if err:
        print("%s stderr[:400]: %s" % (label, err[:400].replace("\n", " | ")))


def main():
    audit, sub = sys.argv[1], sys.argv[2]
    extra = sys.argv[3] if len(sys.argv) > 3 else None
    work_parent = os.path.join(SCRATCH, sub)
    os.makedirs(work_parent, exist_ok=True)
    tool_py = os.path.join(work_parent, "tool.py")
    blob = subprocess.run(["git", "-C", LANE, "show", "%s:tools/souji-freeze-check.py" % REV],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if blob.returncode != 0:
        print("TOOL-BLOB-EXTRACT-FAILED: %s" % blob.stderr.decode()[:300])
        return 2
    with open(tool_py, "wb") as fh:
        fh.write(blob.stdout)
    print("AUDIT=%s sha256=%s" % (audit, hashlib.sha256(open(audit, "rb").read()).hexdigest()))
    print("TOOL blob@%s sha256=%s" % (REV, hashlib.sha256(blob.stdout).hexdigest()))
    results = {}
    if extra:
        v = audit_verdict(run([sys.executable, "-B", audit, "--tool", extra,
                               "--work", os.path.join(work_parent, "extraw")], work_parent))
        results["extra_tool"] = os.path.basename(extra)
        results["extra_verdict"] = None if v is None else list(v)
        results["extra_label"] = ("REJECTED" if (v is not None and v[1] > 0 and v[0] < v[2])
                                  else ("ACCEPTED" if v else "CRASH"))
        show(run([sys.executable, "-B", audit, "--tool", extra,
                  "--work", os.path.join(work_parent, "extraw2")], work_parent), "EXTRA-RUN")
    else:
        for name, toolpath in (("hidden_v2", tool_py),
                               ("clean_stub", None), ("findings_stub", None)):
            if toolpath is None:
                src = STUB_CLEAN if name == "clean_stub" else STUB_FINDINGS
                toolpath = os.path.join(work_parent, name + ".py")
                with open(toolpath, "wb") as fh:
                    fh.write(src.encode())
            p = run([sys.executable, "-B", audit, "--tool", toolpath,
                     "--work", os.path.join(work_parent, name + "w")], work_parent)
            v = audit_verdict(p)
            show(p, "RUN[%s]" % name)
            if name == "hidden_v2":
                results[name] = ("%d/%d" % (v[0], v[2])
                                 if v and v[1] == 0 and v[2] == 10 else "RED")
            else:
                ok = v is not None and v[1] > 0 and v[0] < v[2]
                results[name] = "REJECTED" if ok else ("ACCEPTED" if v else "CRASH")
            results[name + "_verdict"] = None if v is None else list(v)
    print("RESULT " + " ".join("%s=%s" % (k, v) for k, v in results.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
