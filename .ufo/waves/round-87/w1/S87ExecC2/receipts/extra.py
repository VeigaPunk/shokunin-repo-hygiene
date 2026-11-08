#!/usr/bin/env python3
"""S87ExecC2 extra probes: -z improvement on whitespace-edged paths, a raw control-byte record, absent writer."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-87/c2-k4-counter.py")
FILED = os.path.join(LANE, "tools/souji-record-agreement.py")
FILED_W = os.path.join(LANE, "tools/souji-receipt-write.py")
BASE = os.path.join(LANE, "census/round-87/controls/c2-before-base-tool.py")
BASE_W = os.path.join(LANE, "census/round-87/controls/souji-receipt-write.py")


def load(path):
    spec = importlib.util.spec_from_file_location("c2frozen", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


c2 = load(COUNTER)


def write_file(path, data):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def main(argv):
    work, outdir = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    if os.path.exists(work) and os.listdir(work):
        sys.exit(f"not empty: {work}")
    os.makedirs(work, exist_ok=True)
    os.makedirs(outdir, exist_ok=True)
    clone, rev = c2.build(work)
    kits = {}
    for name, ts, ws in (("z", FILED, FILED_W), ("line", BASE, BASE_W), ("absent", FILED, None)):
        kit = os.path.join(work, "kits", name)
        os.makedirs(kit, exist_ok=True)
        t = os.path.join(kit, "souji-record-agreement.py")
        shutil.copyfile(ts, t)
        if ws:
            shutil.copyfile(ws, os.path.join(kit, "souji-receipt-write.py"))
        kits[name] = t

    def run(tool, tag, rev_=rev):
        p = subprocess.run([sys.executable, "-B", tool, "--root", clone, "--rev", rev_],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work, env=c2.ENV, timeout=600)
        base = os.path.join(outdir, tag)
        write_file(base + ".stdout", p.stdout)
        write_file(base + ".stderr", p.stderr)
        write_file(base + ".rc", str(p.returncode).encode() + b"\n")
        text = p.stdout.decode("utf-8", "replace")
        return {"rc": p.returncode, "header": [ln for ln in text.splitlines() if ln.startswith("# writer ")],
                "k4_lines_repr": [repr(ln) for ln in text.splitlines() if ln.startswith("MISMATCH\tK4")],
                "has_counts": any("mismatches=" in ln for ln in text.splitlines())}

    def statuses():
        def g(*a):
            return subprocess.run(["git", "-C", clone, "-c", "core.hooksPath=/dev/null", *a],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=c2.ENV, timeout=120).stdout
        return (g("status", "--porcelain").decode("utf-8", "backslashreplace"),
                g("status", "--porcelain", "-z").decode("utf-8", "backslashreplace"))

    rec = {"rev": rev, "states": {}}

    # E1: leading+trailing space in an untracked name
    c2.reset(clone, rev)
    write_file(os.path.join(clone, " lead.txt "), b"space edged\n")
    line, z = statuses()
    rec["states"]["E1-space-edged"] = {"raw_line": line, "raw_z": z,
                                       "line": run(kits["line"], "E1-space-edged.line"),
                                       "z": run(kits["z"], "E1-space-edged.z")}

    # E2: vertical tab (0x0b) control byte in an untracked name
    c2.reset(clone, rev)
    write_file(os.path.join(clone, "vt\x0bname.txt"), b"control byte\n")
    line, z = statuses()
    rec["states"]["E2-vtab"] = {"raw_line": line, "raw_z": z,
                                "line": run(kits["line"], "E2-vtab.line"),
                                "z": run(kits["z"], "E2-vtab.z")}

    # W: absent writer beside a tool copy, clean tree
    c2.reset(clone, rev)
    rec["states"]["W-absent-writer"] = {"absent": run(kits["absent"], "W-absent-writer")}

    c2.reset(clone, rev)
    with open(os.path.join(outdir, "extra.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
    print(json.dumps(rec, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
