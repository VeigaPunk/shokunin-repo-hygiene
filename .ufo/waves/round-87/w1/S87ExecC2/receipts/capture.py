#!/usr/bin/env python3
"""Focused byte-level receipts for the -z arm attack (S87ExecC2).

States:
  A invalid-utf8  untracked path with byte 0xff
  B esc-collision untracked CR, LF and literal backslash-n names side by side
  C rename-space  a STAGED rename whose SOURCE path has a space at byte index 2
  D cr-concealed  a tracked CR-named file byte-forged under the index stat cache
Every tool run is captured as BYTES; K4 rows parsed from a utf-8/replace decode.
"""
import hashlib
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


def kits(work):
    out = {}
    for name, tool_src, writer_src in (("z", FILED, FILED_W), ("line", BASE, BASE_W)):
        kit = os.path.join(work, "kits", name)
        os.makedirs(kit, exist_ok=True)
        t = os.path.join(kit, "souji-record-agreement.py")
        shutil.copyfile(tool_src, t)
        shutil.copyfile(writer_src, os.path.join(kit, "souji-receipt-write.py"))
        out[name] = t
    return out


def capture(tool, clone, rev, work, outdir, tag):
    p = subprocess.run([sys.executable, "-B", tool, "--root", clone, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work, env=c2.ENV, timeout=600)
    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, tag)
    write_file(base + ".stdout", p.stdout)
    write_file(base + ".stderr", p.stderr)
    text = p.stdout.decode("utf-8", "replace")
    with open(base + ".rc", "w") as f:
        f.write(str(p.returncode) + "\n")
    return {"rc": p.returncode, "k4": [list(h) for h in c2.K4.findall(text)],
            "k4_lines": [ln for ln in text.splitlines() if ln.startswith("MISMATCH\tK4")],
            "header": [ln for ln in text.splitlines() if ln.startswith("# writer ")],
            "has_counts": any("mismatches=" in ln for ln in text.splitlines()),
            "stdout_bytes": len(p.stdout), "stderr_bytes": len(p.stderr)}


def status_bytes(clone, *args):
    p = subprocess.run(["git", "-C", clone, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=c2.ENV, timeout=120)
    return p.stdout


def main(argv):
    work = os.path.abspath(argv[0])
    outdir = os.path.abspath(argv[1])
    if os.path.exists(work):
        if os.listdir(work):
            sys.exit(f"not empty: {work}")
    else:
        os.makedirs(work)
    clone, rev = c2.build(work)
    k = kits(work)
    rec = {"rev": rev, "states": {}}

    # A: untracked path with a non-UTF-8 byte
    c2.reset(clone, rev)
    name = os.path.join(clone.encode(), b"\xff-name.txt")
    fd = os.open(name, os.O_CREAT | os.O_WRONLY, 0o644)
    os.write(fd, b"invalid utf8 untracked\n")
    os.close(fd)
    st = {"raw_line": status_bytes(clone, "status", "--porcelain").decode("utf-8", "backslashreplace"),
          "raw_z": status_bytes(clone, "status", "--porcelain", "-z").decode("utf-8", "backslashreplace"),
          "line": capture(k["line"], clone, rev, work, outdir, "A-invalid-utf8.line"),
          "z": capture(k["z"], clone, rev, work, outdir, "A-invalid-utf8.z")}
    rec["states"]["A-invalid-utf8"] = st

    # B: CR / LF / literal-backslash-n untracked names side by side
    c2.reset(clone, rev)
    for nm in ("x\rname.txt", "x\nname.txt", "x\\nname.txt"):
        write_file(os.path.join(clone, nm), b"untracked\n")
    st = {"raw_line": status_bytes(clone, "status", "--porcelain").decode("utf-8", "backslashreplace"),
          "raw_z": status_bytes(clone, "status", "--porcelain", "-z").decode("utf-8", "backslashreplace"),
          "line": capture(k["line"], clone, rev, work, outdir, "B-collision.line"),
          "z": capture(k["z"], clone, rev, work, outdir, "B-collision.z")}
    rec["states"]["B-esc-collision"] = st

    # committed seed for C and D, so both states have a record at a rev that contains them
    write_file(os.path.join(clone, "ab cd.txt"), b"seed space\n")
    write_file(os.path.join(clone, "cr\rname.txt"), b"cr v1\n")
    c2.git(clone, "add", "-A")
    c2.git(clone, "commit", "-q", "--no-verify", "-m", "S87ExecC2 probe seed")
    rev2 = c2.git(clone, "rev-parse", "HEAD").stdout.decode().strip()
    rec["rev2"] = rev2

    # C: staged rename whose SOURCE path has a space at byte index 2
    c2.reset(clone, rev2)
    c2.git(clone, "mv", "ab cd.txt", "newname.txt")
    st = {"raw_line": status_bytes(clone, "status", "--porcelain").decode("utf-8", "backslashreplace"),
          "raw_z": status_bytes(clone, "status", "--porcelain", "-z").decode("utf-8", "backslashreplace"),
          "line": capture(k["line"], clone, rev2, work, outdir, "C-rename-space.line"),
          "z": capture(k["z"], clone, rev2, work, outdir, "C-rename-space.z")}
    rec["states"]["C-rename-source-space"] = st

    # D: tracked CR-named file byte-forged (same size) + index stat rewritten from the forged bytes
    c2.reset(clone, rev2)
    with open(os.path.join(clone, "cr\rname.txt"), "wb") as f:
        f.write(b"cr X1\n")
    c2.forge_index_stat(clone, "cr\rname.txt")
    st = {"raw_line": status_bytes(clone, "status", "--porcelain").decode("utf-8", "backslashreplace"),
          "raw_z": status_bytes(clone, "status", "--porcelain", "-z").decode("utf-8", "backslashreplace"),
          "line": capture(k["line"], clone, rev2, work, outdir, "D-cr-concealed.line"),
          "z": capture(k["z"], clone, rev2, work, outdir, "D-cr-concealed.z")}
    rec["states"]["D-cr-concealed"] = st

    c2.reset(clone, rev2)
    with open(os.path.join(outdir, "capture.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
    print(json.dumps(rec, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
