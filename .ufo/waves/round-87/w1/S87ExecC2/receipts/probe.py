#!/usr/bin/env python3
"""S87ExecC2 probe: run the r87 -z status arm and the lane-base line arm over six+ extra working-tree shapes.

Hermetic: reuses the frozen c2 counter's fixture builder (build/reset) from the lane, read-only.
Writes only under the --work scratch dir. Raw git status is captured as BYTES (no text-mode
universal-newline translation) so the CR/LF evidence is exact.
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


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def write_file(path, data):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def run_tool(tool, clone, rev, work):
    p = subprocess.run([sys.executable, "-B", tool, "--root", clone, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work, env=c2.ENV, timeout=600)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    hits = c2.K4.findall(out)
    header = [ln for ln in out.splitlines() if ln.startswith("# writer ")]
    return {"rc": p.returncode, "header": header, "k4": [list(h) for h in hits],
            "stdout_tail": out.splitlines()[-1:] if out else [], "stderr_tail": err.strip().splitlines()[-3:]}


def raw_status(clone):
    def run(*args):
        p = subprocess.run(["git", "-C", clone, "-c", "core.hooksPath=/dev/null", *args],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=c2.ENV, timeout=120)
        return p.stdout
    line = run("status", "--porcelain")
    z = run("status", "--porcelain", "-z")
    return (line.decode("utf-8", "backslashreplace"), z.decode("utf-8", "backslashreplace"))


# ---- fixture states (each runs on a freshly reset seed tree) -------------------------------------
def st_clean(clone):
    pass


def st_rename_staged(clone):
    c2.git(clone, "mv", "a.txt", "a-renamed.txt")


def st_rename_worktree(clone):
    os.rename(os.path.join(clone, "a.txt"), os.path.join(clone, "a-moved.txt"))


def st_ignored(clone):
    with open(os.path.join(clone, ".git", "info", "exclude"), "a", encoding="utf-8") as f:
        f.write("ignored-here.txt\n")
    write_file(os.path.join(clone, "ignored-here.txt"), b"ignored, must not be reported\n")


def st_submodule_nested_dirty(clone):
    # nested HEAD does not move: only the nested worktree gains an uncommitted edit
    with open(os.path.join(clone, "nest", "n.txt"), "ab") as f:
        f.write(b"nest worktree dirty\n")


def st_submodule_nested_committed(clone):
    # control: nested HEAD DOES move (no skip-worktree): should be ` M nest` too
    nest = c2.STATE["nest"]
    with open(os.path.join(nest, "n.txt"), "ab") as f:
        f.write(b"nest v2\n")
    c2.git(nest, "add", "-A")
    c2.git(nest, "commit", "-q", "--no-verify", "-m", "nest second")


def st_cr_path(clone):
    write_file(os.path.join(clone, "cr\rname.txt"), b"cr untracked\n")


def st_crlf_path(clone):
    write_file(os.path.join(clone, "crlf\r\nname.txt"), b"crlf untracked\n")


def st_delete_tracked(clone):
    os.unlink(os.path.join(clone, "sub", "b.txt"))


def st_tab_only(clone):
    write_file(os.path.join(clone, "\t"), b"tab-only untracked\n")


def st_tab_name(clone):
    write_file(os.path.join(clone, "tab\tname.txt"), b"tab untracked\n")


def st_newline_ctl(clone):
    write_file(os.path.join(clone, "ctl\nname.txt"), b"newline untracked\n")


def st_invalid_utf8(clone):
    name = os.path.join(clone.encode(), b"\xff-name.txt")
    fd = os.open(name, os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        os.write(fd, b"invalid utf8 untracked\n")
    finally:
        os.close(fd)


SHAPES = [
    ("S0-clean", st_clean, "control: seed tree"),
    ("S1-rename-staged", st_rename_staged, "rename, both ends: index-vs-HEAD rename record"),
    ("S2-rename-worktree", st_rename_worktree, "rename, unstaged: D old + ?? new"),
    ("S3-ignored", st_ignored, "gitignore'd untracked path (info/exclude)"),
    ("S4-submodule-nested-dirty", st_submodule_nested_dirty, "gitlink, nested HEAD did NOT move, nested worktree dirty"),
    ("S5-submodule-nested-committed", st_submodule_nested_committed, "gitlink, nested HEAD moved (control)"),
    ("S6-cr-path", st_cr_path, "untracked path carrying CR"),
    ("S7-delete-tracked", st_delete_tracked, "deleted tracked file"),
    ("S8-tab-only", st_tab_only, "untracked path that is exactly one TAB"),
    ("S9-tab-name", st_tab_name, "untracked path carrying TAB inside the name"),
    ("S10-newline-ctl", st_newline_ctl, "untracked path carrying LF (KN3 control)"),
    ("S11-invalid-utf8", st_invalid_utf8, "untracked path with a non-UTF-8 byte 0xff"),
    ("S12-crlf-path", st_crlf_path, "untracked path carrying CRLF"),
]


def main(argv):
    work = os.path.abspath(argv[0])
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        sys.exit("probe: --work under /tmp")
    if os.path.exists(work):
        if os.listdir(work):
            sys.exit(f"probe: {work} not empty")
    else:
        os.makedirs(work)
    clone, rev = c2.build(work)

    kits = {}
    for name, tool_src, writer_src in (
            ("z", FILED, FILED_W),
            ("line", BASE, BASE_W),
            ("absent", FILED, None)):
        kit = os.path.join(work, "kits", name)
        os.makedirs(kit, exist_ok=True)
        tool = os.path.join(kit, "souji-record-agreement.py")
        shutil.copyfile(tool_src, tool)
        if writer_src:
            shutil.copyfile(writer_src, os.path.join(kit, "souji-receipt-write.py"))
        kits[name] = tool

    meta = {"clone": clone, "rev": rev, "git": subprocess.run(["git", "--version"], capture_output=True,
                                                               text=True).stdout.strip(),
            "kits": {n: {"tool_sha": sha(t), "writer_sha": sha(os.path.join(os.path.dirname(t),
                                                                           "souji-receipt-write.py"))
                         if os.path.isfile(os.path.join(os.path.dirname(t), "souji-receipt-write.py"))
                         else "absent"}
                     for n, t in kits.items()}}
    print("# META " + json.dumps(meta, ensure_ascii=False))

    results = []
    for rid, fn, desc in SHAPES:
        c2.reset(clone, rev)
        fn(clone)
        line_txt, z_txt = raw_status(clone)
        rec = {"id": rid, "desc": desc,
               "raw_status_line": line_txt, "raw_status_z": z_txt,
               "line_tool": run_tool(kits["line"], clone, rev, work),
               "z_tool": run_tool(kits["z"], clone, rev, work)}
        results.append(rec)
        print("# REC " + json.dumps(rec, ensure_ascii=False))

    # absent-writer test on a clean tree
    c2.reset(clone, rev)
    rec = {"id": "W-absent-writer", "desc": "filed tool copy with NO writer beside it, clean tree",
           "absent_tool": run_tool(kits["absent"], clone, rev, work)}
    print("# REC " + json.dumps(rec, ensure_ascii=False))

    c2.reset(clone, rev)
    json.dump({"meta": meta, "results": results, "absent": rec},
              open(os.path.join(work, "probe-results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
