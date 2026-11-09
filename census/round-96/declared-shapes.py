#!/usr/bin/env python3
"""souji r96 C1 shape table: run each shape script plain and under the r96 HOOK (extracted from
census/round-96/c1-survivor-search.py) and print SHAPES-SUMMARY. Exit 0 iff mismatched == 0 over shapes
whose verdict the r96 hook decides (see census/round-96/records/declared-shapes.txt for the committed table:
t1/t4 now agree with plain; v3/w1/w2/a3b are crash-channel exits and stay 70 by design, counted separately).
This counter is the Q172 precondition: a claimant whose check line prints declared-shapes mismatched=0 must have
run this table through the frozen hook."""
import argparse, os, subprocess, sys

sys.dont_write_bytecode = True

SHAPES = (
    ("a1-sys-exit-helper.py", "declared"),
    ("a5-exit-builtin.py", "declared"),
    ("a5b-quit-builtin.py", "declared"),
    ("a4-caught-then-return.py", "declared"),
    ("a12-module-raise.py", "declared"),
    ("v1-module-raise.py", "declared"),
    ("v3-func-args-pattern.py", "crash"),
    ("w1-init-helper.py", "crash"),
    ("w2-main-raise-helper.py", "crash"),
    ("a3b-try-finally-sysexit.py", "crash"),
    ("t1-catch-module-falloff.py", "declared"),
    ("t4-reraise-at-module.py", "declared"),
)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--search", required=True)
    ap.add_argument("--scripts", required=True, help="directory holding the shape scripts")
    ap.add_argument("--work", required=True)
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("SHAPES-FATAL: --work under /tmp etc", file=sys.stderr)
        return 2
    if os.path.exists(work) and (not os.path.isdir(work) or os.listdir(work)):
        print("SHAPES-FATAL: --work not empty", file=sys.stderr)
        return 2
    os.makedirs(work, exist_ok=True)
    # extract HOOK from the search file
    import importlib.util
    spec = importlib.util.spec_from_file_location("search", ns.search)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    hookdir = os.path.join(work, "hook")
    os.makedirs(hookdir)
    with open(os.path.join(hookdir, "sitecustomize.py"), "w", encoding="utf-8") as f:
        f.write(mod.HOOK)
    env = dict(os.environ, PYTHONPATH=hookdir)
    mismatched = 0
    total = 0
    for name, kind in SHAPES:
        path = os.path.join(ns.scripts, name)
        if not os.path.isfile(path):
            print(f"SHAPE {name} missing", file=sys.stderr)
            return 2
        plain = subprocess.run([sys.executable, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        hooked = subprocess.run([sys.executable, "-B", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        # declared shapes must keep their plain rc (hook must not turn a declared exit into 70);
        # crash shapes must be turned into 70 (they are crash-channel exits by design).
        if kind == "declared":
            ok = plain.returncode == hooked.returncode
        else:
            ok = hooked.returncode == 70
        total += 1
        mismatched += not ok
        print(f"SHAPE {name} kind={kind} plain={plain.returncode} hooked={hooked.returncode} {'ok' if ok else 'MISMATCH'}")
    print(f"SHAPES-SUMMARY shapes={total} mismatched={mismatched}")
    return 0 if mismatched == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
