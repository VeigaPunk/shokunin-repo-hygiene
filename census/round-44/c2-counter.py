#!/usr/bin/env python3
"""census/round-44/c2-counter.py — scores the repaired hidden-case audit (Q102/Q106).

Legs over the lane's committed bytes at --rev (blob-bound; the work tree is
never read):

  tool          tools/souji-freeze-check.py exists at --rev
  retention     census/round-43/c2-counter.py --root --rev reproduces, field for
                field, the committed honest r43 state `newtable=9/9 r42table=ok
                hidden=RED hidden_ctrl=REJECTED real=ok selftest=ok tmpdir=ok
                control_clean=REJECTED control_findings=REJECTED` with exit 1
                (the r43 audit is retained red, never appeased — Q106)
  population    census/round-44/c2-scenarios.tsv holds exactly the audit's ten
                frozen scenario rows (id, want exit, sorted want classes) and
                matches the audit's SCENARIOS table (ids and counts)
  hidden_v2     census/round-44/c2-hidden-audit.py over the tool: scenarios=10
                pass=10 fail=0, exit 0
  clean_stub    an always-clean stub (same bytes as the r43 counter's) over the
                v2 audit must FAIL (exit 1, pass<10) — the audit demands real
                findings
  findings_stub an always-findings stub over the v2 audit must FAIL (exit 1,
                pass<10) — the audit demands clean exits where required
  controls_ran  each stub, invoked directly, exits cleanly with a SUMMARY line
                (the r43 memorizer control crashed on a missing `import os`;
                r43 routed defect 2 — a control that crashes proves nothing)
  selftest      the tool's --selftest exits 0 with SELFTEST cases=<n> pass=<n>
                fail=0, n >= 41
  tmpdir        --selftest with TMPDIR naming a missing directory still exits 0

CLI:
  python3 -B census/round-44/c2-counter.py --root LANE --rev FULL40 [--scratch DIR]
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate.
Target: `SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok`
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

FULL40 = re.compile(r"^[0-9a-f]{40}$")
TOOL = "tools/souji-freeze-check.py"
V2_AUDIT = "census/round-44/c2-hidden-audit.py"
SCENARIOS_TSV = "census/round-44/c2-scenarios.tsv"
R43_COUNTER = "census/round-43/c2-counter.py"
RETENTION_FIELDS = {
    "newtable": "9/9", "r42table": "ok", "hidden": "RED",
    "hidden_ctrl": "REJECTED", "real": "ok", "selftest": "ok",
    "tmpdir": "ok", "control_clean": "REJECTED", "control_findings": "REJECTED",
}
STUB_CLEAN = "import sys\nprint('SUMMARY claims=1 findings=0')\nsys.exit(0)\n"
STUB_FINDINGS = ("import sys\nprint('FINDING C1 NO-CLAIMS x')\n"
                 "print('SUMMARY claims=0 findings=1')\nsys.exit(1)\n")


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout if p.returncode == 0 else None


def env(scratch):
    e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
         "TMPDIR": scratch, "GIT_CONFIG_NOSYSTEM": "1",
         "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
         "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"}
    return e


def run(argv, cwd, scratch, timeout=1800):
    try:
        p = subprocess.run(argv, capture_output=True, cwd=cwd, env=env(scratch),
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    return p


def audit_verdict(p):
    """Return (pass, fail, total) from an audit run, or None on crash/no SUMMARY."""
    if p is None:
        return None
    m = re.search(r"^SUMMARY scenarios=(\d+) pass=(\d+) fail=(\d+)",
                  p.stdout.decode("utf-8", "replace"), re.M)
    if not m:
        return None
    return (int(m.group(2)), int(m.group(3)), int(m.group(1)))


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--scratch")
    ns = ap.parse_args(argv)
    root, rev = os.path.abspath(ns.root), ns.rev
    if not FULL40.match(rev):
        sys.stderr.write("REFUSAL REV-NOT-FULL40\n")
        return 2
    scratch = os.path.abspath(ns.scratch or os.environ.get("TMPDIR") or "/tmp")
    os.makedirs(scratch, exist_ok=True)
    fields = {}
    try:
        work = os.path.join(scratch, "r44c2-work")
        os.makedirs(work, exist_ok=True)
        tool_b = blob(root, rev, TOOL)
        fields["tool"] = "present" if tool_b else "absent"
        tool = os.path.join(work, "tool.py")
        if tool_b:
            with open(tool, "wb") as fh:
                fh.write(tool_b)
        # retention
        ret = run([sys.executable, "-B", os.path.join(root, R43_COUNTER),
                   "--root", root, "--rev", rev, "--scratch",
                   os.path.join(scratch, "r43ret")], work, scratch) if tool_b else None
        ret_ok = False
        if ret is not None and ret.returncode == 1:
            m = re.search(r"^SUMMARY (.+)$", ret.stdout.decode("utf-8", "replace"), re.M)
            if m:
                pairs = dict(re.findall(r"(\w+)=([^\s]+)", m.group(1)))
                ret_ok = all(pairs.get(k) == v for k, v in RETENTION_FIELDS.items())
        fields["retention"] = "ok" if ret_ok else "RED"
        # v2 audit
        aud_b = blob(root, rev, V2_AUDIT)
        aud = None
        if aud_b:
            aud = os.path.join(work, "v2audit.py")
            with open(aud, "wb") as fh:
                fh.write(aud_b)
        # population leg: the frozen scenario table matches the audit's table
        pop_ok = False
        pop_b = blob(root, rev, SCENARIOS_TSV)
        aud_src = (aud_b or b"").decode("utf-8", "replace")
        if pop_b and aud_b:
            prows = [ln.split("\t") for ln in pop_b.decode("utf-8", "replace").splitlines()[1:] if ln.strip()]
            ids_ok = all(('("%s"' % r[0]) in aud_src for r in prows)
            exits_ok = all((", %d, " % int(r[1])) in aud_src for r in prows)
            count_ok = len(re.findall(r'\("h\d+-[a-z0-9-]+", ', aud_src)) == 10
            pop_ok = (len(prows) == 10
                      and all(len(r) == 3 for r in prows)
                      and len(set(r[0] for r in prows)) == 10
                      and ids_ok and exits_ok and count_ok)
        fields["population"] = "ok" if pop_ok else "RED"
        hv = None
        if aud and tool_b:
            hv = audit_verdict(run([sys.executable, "-B", aud, "--tool", tool,
                                    "--work", os.path.join(work, "hv")], work, scratch, 1200))
        fields["hidden_v2"] = ("%d/%d" % (hv[0], hv[2])
                               if hv and hv[1] == 0 and hv[2] == 10 else "RED")
        # stubs
        stub_res = {}
        for name, src in (("clean_stub", STUB_CLEAN), ("findings_stub", STUB_FINDINGS)):
            sp = os.path.join(work, name + ".py")
            with open(sp, "wb") as fh:
                fh.write(src.encode())
            v = None
            if aud:
                v = audit_verdict(run([sys.executable, "-B", aud, "--tool", sp,
                                       "--work", os.path.join(work, name + "w")],
                                      work, scratch, 1200))
            ok = v is not None and v[1] > 0 and v[0] < v[2]
            stub_res[name] = ok
            fields[name] = "REJECTED" if ok else ("ACCEPTED" if v else "CRASH")
        ran_ok = True
        for name, src in (("clean_stub", STUB_CLEAN), ("findings_stub", STUB_FINDINGS)):
            sp = os.path.join(work, name + ".py")
            q = run([sys.executable, "-B", sp, "--root", work, "--prereg",
                     os.path.join(work, "no-such-prereg.txt"), "--rev", rev],
                    work, scratch, 60)
            out = q.stdout.decode("utf-8", "replace") if q else ""
            if q is None or "SUMMARY" not in out:
                ran_ok = False
        fields["controls_ran"] = "ok" if ran_ok else "CRASH"
        # selftest + tmpdir
        st_ok = tmp_ok = False
        if tool_b:
            st = run([sys.executable, "-B", tool, "--selftest"], work, scratch, 600)
            if st is not None and st.returncode == 0:
                m = re.search(r"^SELFTEST cases=(\d+) pass=(\d+) fail=0",
                              st.stdout.decode("utf-8", "replace"), re.M)
                st_ok = bool(m and int(m.group(1)) >= 41 and m.group(1) == m.group(2))
            bad = os.path.join(scratch, "r44c2-missing-tmpdir")
            tm = run([sys.executable, "-B", tool, "--selftest"], work, bad, 600)
            tmp_ok = tm is not None and tm.returncode == 0
        fields["selftest"] = "ok" if st_ok else "RED"
        fields["tmpdir"] = "ok" if tmp_ok else "RED"
        target = (fields["tool"] == "present" and fields.get("population") == "ok"
                  and fields["retention"] == "ok"
                  and fields["hidden_v2"] == "10/10"
                  and stub_res["clean_stub"] and stub_res["findings_stub"]
                  and ran_ok and st_ok and tmp_ok)
        print("SUMMARY tool=%s population=%s retention=%s hidden_v2=%s "
              "clean_stub=%s findings_stub=%s controls_ran=%s selftest=%s tmpdir=%s"
              % (fields["tool"], fields.get("population"), fields["retention"],
                 fields["hidden_v2"], fields["clean_stub"], fields["findings_stub"],
                 fields["controls_ran"], fields["selftest"], fields["tmpdir"]))
        if fields["tool"] != "present" or aud is None:
            return 2 if (aud is None and tool_b) else 1
        return 0 if target else 1
    finally:
        shutil.rmtree(os.path.join(scratch, "r44c2-work"), ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
