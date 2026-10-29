#!/usr/bin/env python3
"""R42w3mutationtester02: mechanism-confirmation probes for the two redundancy findings.

Finding R1 (D12): the json-truncate case's own assertion
    `data.get("drift") == [] and "summary" in data`
is never the discriminator for M1 (ftruncate removed).  D12 replaces that assertion with
`return True` and M1 is STILL killed, so the kill must come from the earlier path in the same
case.  Probe R1 removes BOTH the assertion (D12) and the JSON-parse fallback
(`except (OSError, ValueError): return False` -> `except (OSError, ValueError): pass`).
If the mechanism is the parse fallback, M1 now SURVIVES.

Finding R2 (D13): the invalid-utf8 case's own assertion
    `[row.get("repo") for row in data.get("drift", [])] == ["a\\ufffdb"]`
is never the discriminator for D4 (backslashreplace).  D13 replaces that assertion with
`return True` and D4 is STILL killed, so the kill must come from the stdout byte check.
Probe R2 removes BOTH the assertion (D13) and the stdout byte check.  If the mechanism is the
stdout check, D4 now SURVIVES.

These probes are two-point mutants on purpose (they confirm a mechanism); they are reported
separately from the single-point catalogue.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TIP = "6a3f75941d3604e3459011d599c2c16f3a97b44c"
SCRATCH = "/fast/scratch/hyaku/souji-r42/R42w3mutationtester02"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}


def uptime():
    try:
        return open("/proc/loadavg").read().strip()
    except OSError:
        return "?"


def git_show(path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (TIP, path)], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=dict(os.environ, **GIT_ENV), check=False)
    if p.returncode != 0:
        raise SystemExit("git show failed: %s" % path)
    return p.stdout.decode("utf-8")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_fixture(fixture, tool, scratch):
    work = tempfile.mkdtemp(prefix="w.", dir=scratch)
    try:
        e = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": work}
        e.update(GIT_ENV)
        proc = subprocess.run(["python3", "-B", fixture, "--tool", tool, "--work", work],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              check=False, env=e, timeout=600)
        out = proc.stdout
        summ = [l for l in out.split("\n") if l.startswith("SUMMARY")]
        failing = [l.split("=", 1)[1] for l in out.split("\n")
                   if l.startswith("case-") and l.endswith("=FAIL")]
        return {"rc": proc.returncode, "summary": summ[-1] if summ else None,
                "failing": failing, "crash": "Traceback (most recent call last)" in proc.stderr}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    counter = load_module(os.path.join(LANE, "census/round-42/c3-counter.py"), "c3counter")
    tool_src = git_show("tools/souji-worktree-drift.py")
    fx_src = git_show("tests/fixtures/r42-drift-conditions.py")
    tools = {}
    for mid in ("M1", "D4"):
        row = [r for r in counter.MUTANTS if r[0] == mid][0]
        p = os.path.join(SCRATCH, "mech-tool-%s.py" % mid)
        open(p, "w").write(tool_src.replace(row[2], row[3]))
        os.chmod(p, 0o755)
        tools[mid] = p

    probes = {}
    # R1: drop the json-truncate assertion AND the JSON parse fallback.
    r1 = fx_src.replace('    return data.get("drift") == [] and "summary" in data',
                        '    return True', 1)
    r1 = r1.replace('    except (OSError, ValueError):\n        return False',
                    '    except (OSError, ValueError):\n        pass', 1)
    if r1 == fx_src:
        raise SystemExit("R1 probe did not apply")
    probes["R1"] = (r1, "M1")
    # R2: drop the invalid-utf8 assertion AND the stdout byte check.
    r2 = fx_src.replace('    return [row.get("repo") for row in data.get("drift", [])] == ["a\\ufffdb"]',
                        '    return True', 1)
    r2 = r2.replace('    if b"DRIFT\\tABSENT\\ta\\xef\\xbf\\xbdb\\t" not in p.stdout or b"\\\\xff" in p.stdout:\n        return False',
                     '    if False:\n        return False', 1)
    if r2 == fx_src:
        raise SystemExit("R2 probe did not apply")
    probes["R2"] = (r2, "D4")

    scratch = tempfile.mkdtemp(prefix="mech.", dir=SCRATCH)
    try:
        for name, (src, tool) in probes.items():
            fpath = os.path.join(scratch, "fx-%s.py" % name)
            open(fpath, "w").write(src)
            compile(src, name, "exec")
            print("PROBE %s against tool %s, load=%s" % (name, tool, uptime()), flush=True)
            res = run_fixture(fpath, tools[tool], scratch)
            killed = res["rc"] == 1 and res["summary"] and "fail=0" not in res["summary"]
            print("  -> rc=%s %s failing=%s killed=%s load=%s" % (
                res["rc"], res["summary"], ",".join(res["failing"]), killed, uptime()), flush=True)
            print("  VERDICT: %s" % ("the population mutant SURVIVES -> mechanism confirmed"
                                     if not killed else
                                     "the population mutant is STILL KILLED -> mechanism NOT confirmed"),
                  flush=True)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
