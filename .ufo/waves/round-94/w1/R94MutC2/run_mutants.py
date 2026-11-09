#!/usr/bin/env python3
"""R94MutC2: one-edit mutant runner for C2 probe + arms counter."""
import shutil, subprocess, sys, os, hashlib, time

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
SEAT = os.path.join(LANE, ".ufo/waves/round-94/w1/R94MutC2")
SCR = "/fast/scratch/hyaku/souji-r94/R94MutC2"
PRED = ["python3", "-B", "census/round-94/c2-setup-arms.py",
        "--probe", None, "--fixture-pass", "tests/fixtures/r93-k4-flagfail.py",
        "--fixture-fail", "tests/fixtures/r92-k4-flagfail.py",
        "--tool", "tools/souji-record-agreement.py",
        "--before", "census/round-92/controls/c2-before-tool.py",
        "--work", None]

def sha(p):
    with open(p, "rb") as f: return hashlib.sha256(f.read()).hexdigest()

def run_counter(counter, probe, tag, extra_jobs=4):
    w = os.path.join(SCR, f"w-{tag}")
    os.makedirs(w, exist_ok=True)
    args = [a for a in PRED]
    args[args.index("--probe")+1] = probe
    args[args.index("--work")+1] = w
    args[0] = "python3"
    if counter != "census/round-94/c2-setup-arms.py":
        args[1] = counter
    # run from lane cwd
    t0 = time.time()
    p = subprocess.run(["python3", "-B", counter, "--probe", probe,
        "--fixture-pass", "tests/fixtures/r93-k4-flagfail.py",
        "--fixture-fail", "tests/fixtures/r92-k4-flagfail.py",
        "--tool", "tools/souji-record-agreement.py",
        "--before", "census/round-92/controls/c2-before-tool.py",
        "--work", w], cwd=LANE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # save receipt
    rec = os.path.join(SEAT, f"receipt-{tag}.txt")
    with open(rec, "w") as f:
        f.write(f"counter={counter}\nprobe={probe}\nrc={p.returncode} t={time.time()-t0:.1f}\n")
        f.write("--- stdout ---\n" + p.stdout + "\n--- stderr ---\n" + p.stderr)
    return p.returncode, p.stdout, p.stderr

def probe_mutant(name, transform):
    src = open(os.path.join(LANE, "census/round-94/c2-forgery-probe.py")).read()
    out, desc = transform(src)
    if out == src:
        return None, "NOOP"
    pth = os.path.join(SCR, f"probe-{name}.py")
    with open(pth, "w") as f: f.write(out)
    return pth, desc

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "probe":  # probe mutants: score with pristine counter
        mutants = []
        def add(name, fn): mutants.append((name, fn))
        # M1: remove non-empty work check
        add("M01-remove-nonempty", lambda s: (s.replace(
            "    if os.path.isdir(work) and os.listdir(work):\n        print(f\"C2-FORGERY-FATAL: --work {work} is not empty\", file=sys.stderr)\n        return 2\n", ""), "remove non-empty check"))
        # M2: remove file check
        add("M02-remove-filecheck", lambda s: (s.replace(
            "    if os.path.lexists(work) and not os.path.isdir(work):\n        print(f\"C2-FORGERY-FATAL: --work {work} exists and is not a directory\", file=sys.stderr)\n        return 2\n", ""), "remove not-a-dir check"))
        # M3: file check returns 1 not 2
        add("M03-filecheck-rc1", lambda s: (s.replace(
            'print(f"C2-FORGERY-FATAL: --work {work} exists and is not a directory", file=sys.stderr)\n        return 2',
            'print(f"C2-FORGERY-FATAL: --work {work} exists and is not a directory", file=sys.stderr)\n        return 1'), "not-a-dir rc 2->1"))
        # M4: readable-file check rc 2->1
        add("M04-readable-rc1", lambda s: (s.replace(
            'print(f"C2-FORGERY-FATAL: --{k} {v} is not a readable regular file", file=sys.stderr)\n            return 2',
            'print(f"C2-FORGERY-FATAL: --{k} {v} is not a readable regular file", file=sys.stderr)\n            return 1'), "readable rc 2->1"))
        # M5: positive res-is-None check removed
        add("M05-remove-posNone", lambda s: (s.replace(
            "    if res is None:\n        print(f\"C2-FORGERY-FATAL: the fixture printed no SUMMARY line for the positive control (exit {rc})\",\n              file=sys.stderr)\n        return 2\n", ""), "remove positive res-is-None"))
        # M6: positive res-is-None rc 2->1
        add("M06-posNone-rc1", lambda s: (s.replace(
            "    if res is None:\n        print(f\"C2-FORGERY-FATAL: the fixture printed no SUMMARY line for the positive control (exit {rc})\",\n              file=sys.stderr)\n        return 2", 
            "    if res is None:\n        print(f\"C2-FORGERY-FATAL: the fixture printed no SUMMARY line for the positive control (exit {rc})\",\n              file=sys.stderr)\n        return 1"), "pos res-is-None rc 2->1"))
        # M7: forgery res-is-None removed (clips loop early; falls to verdict)
        add("M07-remove-forgNone", lambda s: (s.replace(
            "        if res is None:\n            with open(os.path.join(work, f\"{fid}.out\"), \"w\", encoding=\"utf-8\") as f:\n                f.write(out)\n            print(f\"C2-FORGERY-FATAL: the fixture printed no SUMMARY line for forgery {fid} (exit {rc}); \"\n                  f\"its verdict is unknown\", file=sys.stderr)\n            return 2\n", "        if res is None:\n            rej = False\n            print(f\"FORGERY {fid} sha256=none exit={rc} tool_pass=-/- rejected=no failed=-\")\n            continue\n"), "forgery res-is-None -> rejected=no continue"))
        # M8: forgery res-is-None rc 2->1
        add("M08-forgNone-rc1", lambda s: (s.replace(
            "                  f\"its verdict is unknown\", file=sys.stderr)\n            return 2",
            "                  f\"its verdict is unknown\", file=sys.stderr)\n            return 1"), "forgery res-is-None rc 2->1"))
        # M9: exist_ok True->False (r93 FileExistsError)
        add("M09-no-exist-ok", lambda s: (s.replace("os.makedirs(work, exist_ok=True)", "os.makedirs(work, exist_ok=False)"), "exist_ok True->False"))
        # M10: edit-once check rc 2->1
        add("M10-editonce-rc1", lambda s: (s.replace(
            'print(f"C2-FORGERY-FATAL: {fid} edit does not apply exactly once", file=sys.stderr)\n                return 2',
            'print(f"C2-FORGERY-FATAL: {fid} edit does not apply exactly once", file=sys.stderr)\n                return 1'), "edit-once rc 2->1"))
        # M11: /tmp check removed
        add("M11-remove-tmp", lambda s: (s.replace(
            '    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):\n        print("C2-FORGERY-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)\n        return 2\n', ""), "remove /tmp check"))
        results = {}
        for name, fn in mutants:
            pth, desc = probe_mutant(name, fn)
            if pth is None:
                print(name, "NOOP", flush=True); results[name] = ("NOOP", None, None); continue
            rc, out, err = run_counter("census/round-94/c2-setup-arms.py", pth, name)
            summ = [l for l in out.splitlines() if "ARMS-SUMMARY" in l]
            print(f"{name} {desc} rc={rc} {summ}", flush=True)
            results[name] = (rc, summ, desc)
        with open(os.path.join(SEAT, "probe-mutants-summary.txt"), "w") as f:
            for n, (rc, summ, desc) in results.items():
                f.write(f"{n}: rc={rc} summary={summ} desc={desc}\n")
        print("DONE probe mutants", flush=True)
    elif mode == "arms":  # counter mutants: score on r94 probe and r93 probe
        def arms_mutant(name, fn):
            src = open(os.path.join(LANE, "census/round-94/c2-setup-arms.py")).read()
            out, desc = fn(src)
            if out == src: return None, "NOOP"
            pth = os.path.join(SCR, f"arms-{name}.py")
            with open(pth, "w") as f: f.write(out)
            return pth, desc
        muts = [
            ("C01-S2-want0", lambda s: (s.replace('("S2", fpass, tool, before, a("S2"), 2, FATAL)', '("S2", fpass, tool, before, a("S2"), 0, PASS8)'), "S2 want 2->0")),
            ("C02-S4-want1", lambda s: (s.replace('("S4", missing, tool, before, a("S4"), 2, FATAL)', '("S4", missing, tool, before, a("S4"), 1, FATAL)'), "S4 want 2->1")),
            ("C03-conform-or", lambda s: (s.replace("ok = rc == want and has", "ok = rc == want or has"), "conform and->or")),
            ("C04-P2-want0", lambda s: (s.replace('("P2", ffail, tool, before, a("P2"), 1, FAIL5)', '("P2", ffail, tool, before, a("P2"), 0, FAIL5)'), "P2 want 1->0")),
            ("C05-stream-swap", lambda s: (s.replace("stream = p.stderr if line == FATAL else p.stdout", "stream = p.stdout if line == FATAL else p.stderr"), "stream choice swapped")),
        ]
        for name, fn in muts:
            pth, desc = arms_mutant(name, fn)
            if pth is None:
                print(name, "NOOP", flush=True); continue
            for probe, tag in [("census/round-94/c2-forgery-probe.py", "r94"), ("census/round-93/c2-forgery-probe.py", "r93")]:
                rc, out, err = run_counter(pth, probe, f"{name}-{tag}")
                summ = [l for l in out.splitlines() if "ARMS-SUMMARY" in l]
                print(f"{name} on {tag}: rc={rc} {summ} desc={desc}", flush=True)
        print("DONE arms mutants", flush=True)
