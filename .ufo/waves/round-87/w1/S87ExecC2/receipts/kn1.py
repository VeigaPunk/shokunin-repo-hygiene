#!/usr/bin/env python3
"""S87ExecC2: capture the KN1 no-verdict detail on the filed -z arm and the lane-base line arm."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-87/c2-k4-counter.py")
FILED = os.path.join(LANE, "tools/souji-record-agreement.py")
BASE = os.path.join(LANE, "census/round-87/controls/c2-before-base-tool.py")


def load(path):
    spec = importlib.util.spec_from_file_location("c2frozen", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


c2 = load(COUNTER)


def main(argv):
    work, outdir = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    if os.path.exists(work) and os.listdir(work):
        sys.exit(f"not empty: {work}")
    os.makedirs(work, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)
    clone, rev = c2.build(work)
    out = {"rev": rev}
    for name, src in (("z", FILED), ("line", BASE)):
        kit = os.path.join(work, "kits", name)
        os.makedirs(kit, exist_ok=True)
        t = os.path.join(kit, "souji-record-agreement.py")
        shutil.copyfile(src, t)
        with open(os.path.join(kit, "souji-receipt-write.py"), "w", encoding="utf-8") as f:
            f.write(c2.STUB_WRITER)
        c2.reset(clone, rev)
        p = subprocess.run([sys.executable, "-B", t, "--root", clone, "--rev", rev],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work, env=c2.ENV, timeout=600)
        base = os.path.join(outdir, f"KN1-{name}")
        with open(base + ".stdout", "wb") as f:
            f.write(p.stdout)
        with open(base + ".stderr", "wb") as f:
            f.write(p.stderr)
        text = p.stdout.decode("utf-8", "replace")
        out[name] = {"rc": p.returncode,
                     "k4_lines": [ln for ln in text.splitlines() if ln.startswith("MISMATCH\tK4")],
                     "has_counts": any("mismatches=" in ln for ln in text.splitlines())}
    with open(os.path.join(outdir, "kn1.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
