#!/usr/bin/env python3
"""S87ExecC2 follow-up probe for SoujiR87: KB3 shape against my own repro + the copy (C) case.

Uses the frozen c2 counter's seed fixture (imported read-only) and the repaired tool bytes in the lane.
Captures raw git status (line and -z, as bytes) per state and both tools' K4 rows.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
COUNTER = os.path.join(LANE, "census/round-87/c2-k4-counter.py")
REP = os.path.join(LANE, "tools/souji-record-agreement.py")
REP_W = os.path.join(LANE, "tools/souji-receipt-write.py")
LINE = os.path.join(LANE, "census/round-87/controls/c2-before-base-tool.py")
LINE_W = os.path.join(LANE, "census/round-87/controls/souji-receipt-write.py")


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
    for name, tool, writer in (("rep", REP, REP_W), ("line", LINE, LINE_W)):
        kit = os.path.join(work, "kits", name)
        os.makedirs(kit, exist_ok=True)
        t = os.path.join(kit, "souji-record-agreement.py")
        shutil.copyfile(tool, t)
        shutil.copyfile(writer, os.path.join(kit, "souji-receipt-write.py"))
        kits[name] = t

    # seed extra tracked paths at a second revision; enable copy detection in the repo config
    write_file(os.path.join(clone, "ab cd.txt"), b"seed space\n")
    write_file(os.path.join(clone, "cr\rname.txt"), b"cr v1\n")
    c2.git(clone, "add", "-A")
    c2.git(clone, "commit", "-q", "--no-verify", "-m", "S87ExecC2 follow-up seed")
    rev2 = c2.git(clone, "rev-parse", "HEAD").stdout.decode().strip()
    c2.git(clone, "config", "status.renames", "copies")

    def status_bytes(*args):
        return subprocess.run(["git", "-C", clone, "-c", "core.hooksPath=/dev/null", *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=c2.ENV, timeout=120).stdout

    def run(tool, tag, rev_):
        p = subprocess.run([sys.executable, "-B", tool, "--root", clone, "--rev", rev_],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work, env=c2.ENV, timeout=600)
        base = os.path.join(outdir, tag)
        write_file(base + ".stdout", p.stdout)
        write_file(base + ".stderr", p.stderr)
        write_file(base + ".rc", str(p.returncode).encode() + b"\n")
        text = p.stdout.decode("utf-8", "replace")
        return {"rc": p.returncode,
                "k4_lines": [ln for ln in text.splitlines() if ln.startswith("MISMATCH\tK4")],
                "counts": [ln for ln in text.splitlines() if ln.startswith("keys=")]}

    def state(rid, desc, apply_fn, rev_):
        c2.reset(clone, rev_)
        apply_fn()
        line = status_bytes("status", "--porcelain").decode("utf-8", "backslashreplace")
        z = status_bytes("status", "--porcelain", "-z").decode("utf-8", "backslashreplace")
        rec = {"id": rid, "desc": desc, "raw_line": line, "raw_z": z,
               "rep": run(kits["rep"], f"{rid}.rep", rev_),
               "line": run(kits["line"], f"{rid}.line", rev_)}
        print("# STATE " + json.dumps(rec, ensure_ascii=False))
        return rec

    def apply_rename_ab_cd():
        c2.git(clone, "mv", "ab cd.txt", "newname.txt")

    def apply_rename_ab_src():
        write_file(os.path.join(clone, "ab src.txt"), b"source\n")
        c2.git(clone, "add", "-A")
        c2.git(clone, "commit", "-q", "--no-verify", "-m", "src")
        c2.git(clone, "mv", "ab src.txt", "dst.txt")

    def apply_copy_plain():
        shutil.copyfile(os.path.join(clone, "a.txt"), os.path.join(clone, "a-copy.txt"))
        c2.git(clone, "add", "a-copy.txt")

    def apply_copy_modified():
        write_file(os.path.join(clone, "a.txt"), b"alpha v2\n")
        c2.git(clone, "add", "a.txt")
        shutil.copyfile(os.path.join(clone, "a.txt"), os.path.join(clone, "a-copy2.txt"))
        c2.git(clone, "add", "a-copy2.txt")

    def apply_copy_ab_unmodified():
        shutil.copyfile(os.path.join(clone, "ab cd.txt"), os.path.join(clone, "ab-copy.txt"))
        c2.git(clone, "add", "ab-copy.txt")

    def apply_copy_ab_modified():
        write_file(os.path.join(clone, "ab cd.txt"), b"seed space v2\n")
        c2.git(clone, "add", "ab cd.txt")
        shutil.copyfile(os.path.join(clone, "ab cd.txt"), os.path.join(clone, "ab-copy2.txt"))
        c2.git(clone, "add", "ab-copy2.txt")

    def apply_rename_plus_untracked():
        c2.git(clone, "mv", "a.txt", "b.txt")
        write_file(os.path.join(clone, "zz.txt"), b"untracked\n")

    def apply_copy_plus_untracked():
        write_file(os.path.join(clone, "a.txt"), b"alpha v2\n")
        c2.git(clone, "add", "a.txt")
        shutil.copyfile(os.path.join(clone, "a.txt"), os.path.join(clone, "a-copy3.txt"))
        c2.git(clone, "add", "a-copy3.txt")
        write_file(os.path.join(clone, "zz2.txt"), b"untracked\n")

    def apply_nonutf8():
        name = os.path.join(clone.encode(), b"\xff-name.txt")
        fd = os.open(name, os.O_CREAT | os.O_WRONLY, 0o644)
        os.write(fd, b"not utf-8\n")
        os.close(fd)

    def apply_cr():
        write_file(os.path.join(clone, "cr2\rname.txt"), b"cr untracked\n")

    def apply_trio():
        for nm in ("x\rname.txt", "x\nname.txt", "x\\nname.txt"):
            write_file(os.path.join(clone, nm), b"untracked\n")

    def apply_tab_and_newline():
        write_file(os.path.join(clone, "\t"), b"tab only\n")
        write_file(os.path.join(clone, "ctl\nname.txt"), b"newline\n")

    def apply_cr_forged():
        write_file(os.path.join(clone, "cr\rname.txt"), b"cr X1\n")
        c2.forge_index_stat(clone, "cr\rname.txt")

    states = [
        state("R1-rename-ab-cd", "my original repro: git mv 'ab cd.txt' newname.txt", apply_rename_ab_cd, rev2),
        state("R2-rename-ab-src", "KB3 shape: git mv 'ab src.txt' dst.txt", apply_rename_ab_src, rev2),
        state("C1-copy-plain", "copy of unmodified a.txt, staged, status.renames=copies", apply_copy_plain, rev2),
        state("C2-copy-modified", "copy of staged-modified a.txt", apply_copy_modified, rev2),
        state("C3-copy-ab-unmodified", "copy of unmodified 'ab cd.txt'", apply_copy_ab_unmodified, rev2),
        state("C4-copy-ab-modified", "copy of staged-modified 'ab cd.txt'", apply_copy_ab_modified, rev2),
        state("O1-rename-plus-untracked", "rename + untracked sibling (over-skip check)", apply_rename_plus_untracked, rev2),
        state("O2-copy-plus-untracked", "copy + untracked sibling (over-skip check)", apply_copy_plus_untracked, rev2),
        state("F1-nonutf8", "untracked 0xff name (HIGH-1 re-check)", apply_nonutf8, rev2),
        state("F2-cr", "untracked CR name (MEDIUM-1 re-check)", apply_cr, rev2),
        state("F2b-trio", "CR / LF / literal backslash-n side by side", apply_trio, rev2),
        state("E-tab-newline", "tab-only and newline names", apply_tab_and_newline, rev2),
        state("D-cr-forged", "tracked CR name byte-forged under the stat cache (residual detail spelling)", apply_cr_forged, rev2),
    ]
    c2.reset(clone, rev2)
    with open(os.path.join(outdir, "followup.json"), "w", encoding="utf-8") as f:
        json.dump({"rev": rev, "rev2": rev2, "states": states}, f, indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
