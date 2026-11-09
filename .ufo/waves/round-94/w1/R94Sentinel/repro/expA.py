import importlib.util, os, subprocess, sys, textwrap, shutil

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEARCH = os.path.join(LANE, "census/round-94/c1-survivor-search.py")
spec = importlib.util.spec_from_file_location("c1search", SEARCH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
HOOK = mod.HOOK
CRASH_RC = mod.CRASH_RC
verdict = mod.verdict

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKDIR = os.path.join(S, "hook")
os.makedirs(HOOKDIR, exist_ok=True)
with open(os.path.join(HOOKDIR, "sitecustomize.py"), "w") as f:
    f.write(HOOK)

MICRO = os.path.join(S, "micro", "micro-harness.py")
with open(MICRO, "w") as f:
    f.write(textwrap.dedent('''\
        #!/usr/bin/env python3
        """micro-harness: mimics census/round-93/c1-false-row-harness.py's counter spawn and ROW/SUMMARY output."""
        import argparse, os, subprocess, sys
        ap = argparse.ArgumentParser()
        ap.add_argument("--counter", required=True)
        ap.add_argument("--work", required=True)
        ap.add_argument("--lane", default=".")
        ap.add_argument("--fleet-root", default=".")
        ap.add_argument("--population", default="x")
        ns = ap.parse_args()
        os.makedirs(ns.work, exist_ok=True)
        p = subprocess.run([sys.executable, "-B", ns.counter, "--root", ns.lane, "--rev", "HEAD",
                            "--fleet-root", ns.fleet_root, "--population", ns.population,
                            "--ledger", ns.population],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ns.lane)
        out = p.stdout.decode("utf-8", "replace")
        err = p.stderr.decode("utf-8", "replace")
        got = "RESOLVED" if "ITEM I1" in out else "-"
        print(f"ROW R1 where=lane rev=BASE item=I1 class=ABSENT expect=RESOLVED/- got={got} rc={p.returncode} "
              f"match={'yes' if got == 'RESOLVED' else 'no'}")
        print(f"SUMMARY rows=1 mismatches={0 if got == 'RESOLVED' else 1} accepted=0 refused_true=0 errors=0")
        sys.stderr.write(err)
        sys.exit(0 if got == "RESOLVED" else 1)
        '''))

CASES = {
 "raise-main":      'raise RuntimeError("boom")\n',
 "raise-thread":    'import threading\ndef b():\n    raise RuntimeError("boom-thread")\nthreading.Thread(target=b).start()\nimport time; time.sleep(0.3)\nprint("ITEM I1 RESOLVED")\n',
 "os._exit(1)":     'import os\nprint("ITEM I1 RESOLVED")\nos._exit(1)\n',
 "os._exit(70)":    'import os\nprint("ITEM I1 RESOLVED")\nos._exit(70)\n',
 "sys.exit(70)":    'import sys\nprint("ITEM I1 RESOLVED")\nsys.exit(70)\n',
 "sigsegv":         'import os, signal\nos.kill(os.getpid(), signal.SIGSEGV)\n',
 "sigkill":         'import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n',
 "exc-in-del":      'class C:\n    def __del__(self):\n        raise RuntimeError("boom-del")\nC()\nprint("ITEM I1 RESOLVED")\nimport gc; gc.collect()\n',
 "exc-in-atexit":   'import atexit\ndef h():\n    raise RuntimeError("boom-atexit")\natexit.register(h)\nprint("ITEM I1 RESOLVED")\n',
 "buffered-stdout": 'import sys\nprint("ITEM I1 RESOLVED")\nsys.stdout.write("PARTIAL-NO-NEWLINE")\nraise RuntimeError("boom-flush")\n',
 "exc-in-except":   'try:\n    raise RuntimeError("boom-caught")\nexcept RuntimeError:\n    print("ITEM I1 RESOLVED")\n',
}

env = dict(os.environ)
env["PYTHONPATH"] = HOOKDIR
rows = []
for name, body in CASES.items():
    cpath = os.path.join(S, "micro", f"counter-{name}.py")
    with open(cpath, "w") as f:
        f.write(body)
    w = os.path.join(S, "micro", f"w-{name}")
    shutil.rmtree(w, ignore_errors=True)
    p = subprocess.run([sys.executable, "-B", MICRO, "--counter", cpath, "--work", w, "--lane", S],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out = p.stdout.decode("utf-8", "replace")
    v = verdict(p.returncode, p.stdout)
    partial = "PARTIAL-NO-NEWLINE" in out
    item = "ITEM I1 RESOLVED" in out
    rows.append((name, p.returncode, v, item, partial))
    print(f"CASE {name:16s} harness_rc={p.returncode:4d} r94_verdict={v:8s} stdout_has_ITEM={item} stdout_has_partial={partial}")
print()
print("SUMMARY: cases=", len(rows))
# direct child checks (the counter run alone, no harness)
print("--- direct child rc (no harness) ---")
for name, body in CASES.items():
    cpath = os.path.join(S, "micro", f"counter-{name}.py")
    p = subprocess.run([sys.executable, "-B", cpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    print(f"DIRECT {name:16s} rc={p.returncode:4d} stdout={p.stdout.decode()[:40]!r} stderr_tail={p.stderr.decode().strip().splitlines()[-1][:70] if p.stderr.decode().strip() else ''!r}")
