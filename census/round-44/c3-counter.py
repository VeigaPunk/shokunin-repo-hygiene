#!/usr/bin/env python3
"""census/round-44/c3-counter.py — scores the r44 leaf-symlink contract cutover.

Claim C3 (coverage): the drift tool's governed surface gains the leaf-symlink
refusal class (JSON-TARGET-SYMLINK) under a decided contract — refuse the
`--json` leaf symlink outright instead of resolving and writing through it —
with its legacy consumer (tests/fixtures/r38-drift-write-envelope.py) cut over
in the same landing and every prior drift suite still green against the new
bytes. The 16 r43 drift-survivor classes are NOT this claim and stay untouched.

All legs read blobs at --rev (never the work tree) and run them inside
--scratch. Prior suites are the fixtures themselves; the pinned r41/r42
COUNTERS stay at their historical measured revisions and are not re-run (their
tool digests are historical pins; this counter scores behaviour).

Legs:
  surface        census/round-44/c3-surface.tsv parses (header + item rows) and
                 every named fixture path exists at --rev
  tool_class     the tip tool names JSON-TARGET-SYMLINK in its module docstring
                 and raises it at the guard site
  legacy         the updated r38 fixture over the tip tool: exit 0,
                 cases=12 pass=12 fail=0
  legacy_case    the tip r38 fixture names json-symlink-refused (the cutover
                 landed) and no longer carries a json-symlink-resolved case id
  legacy_base    the same fixture with --base-tool set to the r37 blob
                 (4c257b7b5d205a57deed687582ac6f25d9e02d37, from git):
                 base_fail >= 7, behavioral_fail >= 4, and the BASE-BEHAVIORAL
                 line names json-symlink-refused (the base resolves-and-writes
                 where the contract now refuses — the cutover discriminates)
  battery        tests/fixtures/r44-drift-symlink-refusal.py over the tip tool:
                 exit 0, cases >= 6, fail=0
  battery_clean  the battery against an always-clean stub must FAIL (rc 1,
                 fail > 0) — REJECTED
  battery_refuse the battery against an always-refusing stub must FAIL (rc 1,
                 fail > 0: the positive cases break) — REJECTED
  prior          five prior fixtures over the tip tool, exit 0 each, with the
                 r41 arm requiring `probes=21 pass=21 fail=0`: r36,
                 r37-drift-discrimination, r37-drift-escapes, r41-refusal-sites,
                 r42-drift-conditions -> prior=5/5

CLI:
  python3 -B census/round-44/c3-counter.py --root LANE --rev FULL40 [--scratch DIR]
Exit: 0 target met; 1 target unmet; 2 could-not-evaluate.
Target: `SUMMARY surface=ok tool_class=ok legacy=ok legacy_case=ok legacy_base=ok battery=ok battery_clean=REJECTED battery_refuse=REJECTED prior=5/5`
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

FULL40 = re.compile(r"^[0-9a-f]{40}$")
TOOL = "tools/souji-worktree-drift.py"
SURFACE = "census/round-44/c3-surface.tsv"
R37_REV = "4c257b7b5d205a57deed687582ac6f25d9e02d37"
FIX_R38 = "tests/fixtures/r38-drift-write-envelope.py"
FIX_BATTERY = "tests/fixtures/r44-drift-symlink-refusal.py"
PRIOR = (
    ("tests/fixtures/r36-worktree-drift.py", None),
    ("tests/fixtures/r37-drift-discrimination.py", None),
    ("tests/fixtures/r37-drift-escapes.py", None),
    ("tests/fixtures/r41-refusal-sites.py", ("probes=21", "pass=21", "fail=0")),
    ("tests/fixtures/r42-drift-conditions.py", None),
)
STUB_CLEAN = "import sys\nprint('SUMMARY claims=1 findings=0')\nsys.exit(0)\n"
STUB_REFUSE = ("import sys\nprint('REFUSAL JSON-TARGET-SYMLINK: stub refuses everything')\n"
               "print('SUMMARY record=stub record_repos=0 live_repos=0 drift_rows=0 unreachable=0')\n"
               "sys.exit(2)\n")


def blob(root, rev, path):
    p = subprocess.run(["git", "-C", root, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout if p.returncode == 0 else None


def env(scratch):
    return {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "TMPDIR": scratch, "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C"}


def run(argv, cwd, scratch, timeout=1200):
    try:
        return subprocess.run(argv, capture_output=True, cwd=cwd,
                              env=env(scratch), timeout=timeout)
    except subprocess.TimeoutExpired:
        return None


def summary_of(p):
    if p is None:
        return {}
    m = re.search(r"^SUMMARY (\S+) (\S+) (\S+)$",
                  p.stdout.decode("utf-8", "replace").strip().splitlines()[-1]
                  if p.stdout else "", re.M)
    out = {}
    if p.stdout:
        for line in p.stdout.decode("utf-8", "replace").splitlines():
            if line.startswith("SUMMARY "):
                out = dict(re.findall(r"(\w+)=(\S+)", line))
    return out


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
        work = os.path.join(scratch, "r44c3-work")
        os.makedirs(work, exist_ok=True)
        files = {}
        for label, path in (("tool", TOOL), ("r38", FIX_R38), ("battery", FIX_BATTERY),
                            ("surface", SURFACE)):
            b = blob(root, rev, path)
            files[label] = b
            if b is not None:
                fp = os.path.join(work, label.replace("/", "_") + os.path.basename(path))
                with open(fp, "wb") as fh:
                    fh.write(b)
                files[label + "_path"] = fp
        # surface
        surf_ok = False
        if files["surface"] is not None:
            lines = files["surface"].decode("utf-8", "replace").splitlines()
            header = lines[0].split("\t")
            rows = [ln.split("\t") for ln in lines[1:] if ln.strip()]
            surf_ok = (header[:2] == ["fixture", "role"] and len(rows) >= 5
                       and all(len(r) == len(header) for r in rows))
            for r in rows:
                if r[0] == "tools/souji-worktree-drift.py":
                    continue
                if blob(root, rev, r[0]) is None:
                    surf_ok = False
        fields["surface"] = "ok" if surf_ok else "RED"
        # tool_class
        tb = files["tool"]
        tb_text = tb.decode("utf-8", "replace") if tb else ""
        tc = ("JSON-TARGET-SYMLINK" in tb_text
              and 'raise Refusal("JSON-TARGET-SYMLINK' in tb_text)
        fields["tool_class"] = "ok" if tc else "RED"
        tool = files.get("tool_path")
        # battery + stubs
        bat = files.get("battery_path")
        bat_sum = {}
        if tool and bat:
            p = run([sys.executable, "-B", bat, "--tool", tool,
                     "--work", os.path.join(work, "batw")], work, scratch)
            bat_sum = summary_of(p)
            fields["battery"] = ("ok" if p is not None and p.returncode == 0
                                 and int(bat_sum.get("cases", "0")) >= 6
                                 and bat_sum.get("fail") == "0" else "RED")
            stub_ok = True
            for name, src in (("clean", STUB_CLEAN), ("refuse", STUB_REFUSE)):
                sp = os.path.join(work, "stub_%s.py" % name)
                with open(sp, "wb") as fh:
                    fh.write(src.encode())
                q = run([sys.executable, "-B", bat, "--tool", sp,
                         "--work", os.path.join(work, "stubw_" + name)], work, scratch)
                qsum = summary_of(q)
                if not (q is not None and q.returncode == 1 and int(qsum.get("fail", "0")) > 0):
                    stub_ok = False
                    fields["battery_" + name] = "ACCEPTED"
                else:
                    fields["battery_" + name] = "REJECTED"
            if not stub_ok:
                pass
        else:
            fields["battery"] = "RED"
            fields["battery_clean"] = fields.get("battery_clean", "RED")
            fields["battery_refuse"] = fields.get("battery_refuse", "RED")
        # legacy
        r38 = files.get("r38_path")
        leg_ok = leg_case_ok = False
        if tool and r38:
            r38_text = files["r38"].decode("utf-8", "replace")
            leg_case_ok = ('"json-symlink-refused"' in r38_text
                           and 'check("json-symlink-resolved"' not in r38_text)
            p = run([sys.executable, "-B", r38, "--tool", tool,
                     "--work", os.path.join(work, "legw")], work, scratch)
            s = summary_of(p)
            leg_ok = (p is not None and p.returncode == 0
                      and s.get("cases") == "12" and s.get("pass") == "12"
                      and s.get("fail") == "0")
        fields["legacy"] = "ok" if leg_ok else "RED"
        fields["legacy_case"] = "ok" if leg_case_ok else "RED"
        # legacy_base
        lb_ok = False
        if r38:
            r37 = os.path.join(work, "r37_tool.py")
            b37 = blob(root, R37_REV, TOOL)
            if b37:
                with open(r37, "wb") as fh:
                    fh.write(b37)
                p = run([sys.executable, "-B", r38, "--tool", tool or r38,
                         "--base-tool", r37,
                         "--work", os.path.join(work, "lbw")], work, scratch)
                out = p.stdout.decode("utf-8", "replace") if p else ""
                s = summary_of(p)
                behav = re.search(r"^BASE-BEHAVIORAL failed=(\d+) cases=(.*)$", out, re.M)
                lb_ok = (p is not None and p.returncode == 0
                         and int(s.get("base_fail", "0")) >= 7
                         and int(s.get("behavioral_fail", "0")) >= 4
                         and bool(behav) and "json-symlink-refused" in behav.group(2))
        fields["legacy_base"] = "ok" if lb_ok else "RED"
        # prior
        prior_ok = 0
        for path, want in PRIOR:
            fb = blob(root, rev, path)
            if fb is None or tool is None:
                continue
            fp = os.path.join(work, "prior_" + os.path.basename(path))
            with open(fp, "wb") as fh:
                fh.write(fb)
            p = run([sys.executable, "-B", fp, "--tool", tool,
                     "--work", os.path.join(work, "pw_" + os.path.basename(path))],
                    work, scratch)
            s = summary_of(p)
            if p is not None and p.returncode == 0:
                if want and not all(w in s for w in want):
                    continue
                prior_ok += 1
        fields["prior"] = "%d/5" % prior_ok
        target = (fields["surface"] == "ok" and fields["tool_class"] == "ok"
                  and fields["legacy"] == "ok" and fields["legacy_case"] == "ok"
                  and fields["legacy_base"] == "ok" and fields["battery"] == "ok"
                  and fields.get("battery_clean") == "REJECTED"
                  and fields.get("battery_refuse") == "REJECTED"
                  and fields["prior"] == "5/5")
        print("SUMMARY surface=%s tool_class=%s legacy=%s legacy_case=%s "
              "legacy_base=%s battery=%s battery_clean=%s battery_refuse=%s prior=%s"
              % (fields["surface"], fields["tool_class"], fields["legacy"],
                 fields["legacy_case"], fields["legacy_base"], fields["battery"],
                 fields.get("battery_clean"), fields.get("battery_refuse"),
                 fields["prior"]))
        missing = [p for p in (TOOL, SURFACE) if blob(root, rev, p) is None]
        if missing:
            return 2
        return 0 if target else 1
    finally:
        shutil.rmtree(os.path.join(scratch, "r44c3-work"), ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
