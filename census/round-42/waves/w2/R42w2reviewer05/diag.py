#!/usr/bin/env python3
"""R42w2reviewer05: diagnose which fixture case decides each mutant, and what changes under load.

Reproduces the frozen counter's run()/killed() exactly, but keeps the fixture's stdout,
stderr, exit code and wall time per (mutant, fixture) pair, so a case-level kill can be
attributed and a load-induced difference can be located.

Usage: diag.py <label> [workers]
Writes diag-<label>.json and diag-<label>.txt under the seat directory.
"""
import concurrent.futures
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2reviewer05"
REV = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
TOOL = "tools/souji-worktree-drift.py"
FIXTURE = "tests/fixtures/r42-drift-conditions.py"
SUMMARY_RE = re.compile(r"^SUMMARY (?:cases|probes)=(\d+) pass=(\d+) fail=(\d+)", re.M)
CASE_RE = re.compile(r"^case-(?P<name>[a-z0-9\-]+)=(?P<res>PASS|FAIL)[ \t]*(?P<detail>.*)$", re.M)
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0",
           "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin")}


def git_show(rev, path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=GIT_ENV, check=False)
    if p.returncode != 0:
        raise SystemExit("git show failed: %s" % path)
    return p.stdout


def load_counter():
    spec = importlib.util.spec_from_file_location("c3counter", os.path.join(LANE, "census/round-42/c3-counter.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(fixture, tool, scratch, tag):
    """Byte-for-byte the frozen counter's run(), plus stdout/stderr/elapsed kept."""
    work = tempfile.mkdtemp(prefix="w-%s." % tag, dir=scratch)
    try:
        e = dict(GIT_ENV)
        e["TMPDIR"] = work
        t0 = time.monotonic()
        try:
            proc = subprocess.run(["python3", "-B", fixture, "--tool", tool, "--work", work],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                  check=False, env=e, timeout=300)
        except subprocess.TimeoutExpired:
            return {"rc": 124, "cases": None, "pass": None, "fail": None, "crash": True,
                    "elapsed": round(time.monotonic() - t0, 2), "stdout": "", "stderr": "COUNTER-300s-TIMEOUT",
                    "case_detail": []}
        elapsed = round(time.monotonic() - t0, 2)
        m = SUMMARY_RE.findall(proc.stdout)
        crash = "Traceback (most recent call last)" in proc.stderr
        detail = [(mm.group("name"), mm.group("res"), mm.group("detail").strip())
                  for mm in CASE_RE.finditer(proc.stdout)]
        if not m:
            return {"rc": proc.returncode, "cases": None, "pass": None, "fail": None, "crash": crash,
                    "elapsed": elapsed, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:],
                    "case_detail": detail}
        c, p, f = (int(x) for x in m[-1])
        return {"rc": proc.returncode, "cases": c, "pass": p, "fail": f, "crash": crash,
                "elapsed": elapsed, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:],
                "case_detail": detail}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def killed(res):
    return res["cases"] is not None and res["rc"] == 1 and res["fail"] > 0 and not res["crash"]


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print("refusing to run as root")
        return 2
    scratch_root = "/fast/scratch/hyaku/souji-r42/R42w2reviewer05"
    scratch = tempfile.mkdtemp(prefix="diag-%s." % label, dir=scratch_root)
    try:
        mod = load_counter()
        tool_b = git_show(REV, TOOL)
        source = tool_b.decode("utf-8")
        fixture_b = git_show(REV, FIXTURE)
        fixture = os.path.join(scratch, "fx.py")
        with open(fixture, "wb") as h:
            h.write(fixture_b)
        os.chmod(fixture, 0o755)
        pristine = os.path.join(scratch, "pristine.py")
        with open(pristine, "wb") as h:
            h.write(tool_b)
        os.chmod(pristine, 0o755)
        rows = []
        for kind, table in (("MUTANT", mod.MUTANTS), ("EQUIV", mod.EQUIV)):
            for mid, desc, old, new in table:
                mp = os.path.join(scratch, "mut-%s.py" % mid)
                with open(mp, "wb") as h:
                    h.write(source.replace(old, new).encode("utf-8"))
                os.chmod(mp, 0o755)
                rows.append((kind, mid, desc, mp))
        out = {"label": label, "pristine": None, "results": {}}
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futs = {}
            pre = pool.submit(run, fixture, pristine, scratch, "pre")
            for kind, mid, desc, mp in rows:
                futs[mid] = pool.submit(run, fixture, mp, scratch, mid)
            out["pristine"] = pre.result()
            for mid, f in futs.items():
                out["results"][mid] = f.result()
        with open(os.path.join(SEAT, "diag-%s.json" % label), "w") as h:
            json.dump(out, h, indent=1, sort_keys=True)
        p = out["pristine"]
        lines = ["PRISTINE rc=%s cases=%s pass=%s fail=%s crash=%s elapsed=%s" % (
            p["rc"], p["cases"], p["pass"], p["fail"], p["crash"], p["elapsed"])]
        for n, r, d in p["case_detail"]:
            lines.append("  case %-46s %s %s" % (n, r, d))
        for kind, mid, desc, mp in rows:
            r = out["results"][mid]
            fails = [(n, d) for n, res, d in r["case_detail"] if res == "FAIL"]
            lines.append("%s %s killed=%s rc=%s cases=%s pass=%s fail=%s crash=%s elapsed=%s" % (
                kind, mid, killed(r), r["rc"], r["cases"], r["pass"], r["fail"], r["crash"], r["elapsed"]))
            lines.append("    failing_cases=%s" % (",".join(n for n, _ in fails) or "-"))
            for n, d in fails:
                lines.append("      %s: %s" % (n, d))
            if r["stderr"].strip():
                lines.append("    stderr: %s" % r["stderr"].strip().replace("\n", " | ")[-300:])
        text = "\n".join(lines) + "\n"
        with open(os.path.join(SEAT, "diag-%s.txt" % label), "w") as h:
            h.write(text)
        print(text)
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
