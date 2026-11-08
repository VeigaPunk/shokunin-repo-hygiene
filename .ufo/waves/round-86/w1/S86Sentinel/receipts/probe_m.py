#!/usr/bin/env python3
"""Probe set M: the discriminating base-vs-filed comparison for the writer-authority delta."""
import os
import subprocess
import sys

sys.path.insert(0, "/fast/scratch/hyaku/souji-r86/S86Sentinel")
from probe import (S, TOOL, WRITER, ENV, build_fixture, git, move_nest, run_tool, show,
                   k4_rows, fresh, tool_copy, forge_index_stat)

BASE = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-86/controls/c2-before-base-tool.py"
OUT = []


def emit(s):
    OUT.append(s)
    print(s)


def raw(p):
    return p.stdout.decode("utf-8", "replace")


def m1_discriminating():
    """A tree with BOTH a stat-cache forgery (base reports it) and a skip-worktree flag
    (the filed tool's sweep sees it). With a writer whose _flag_refusal returns "", the
    FILED tool's sweep is neutralised while the BASE tool still reports the forgery."""
    d = fresh("m1")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    # also a stat-cache forgery on a.txt, so the BASE tool has something to report
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha X1\n")           # same length as "alpha v1\n"
    forge_index_stat(repo, "a.txt")

    def patch_empty(src):
        return src.replace(
            'def _flag_refusal(top: str, tag: bytes, path: bytes) -> str:',
            'def _flag_refusal(top: str, tag: bytes, path: bytes) -> str:\n'
            '    return ""  # M1: declines to refuse\n', 1)

    def patch_git_empty(src):
        return src.replace(
            'def git(root: str, *args: str, input: "bytes | None" = None) -> subprocess.CompletedProcess:',
            'def git(root: str, *args: str, input: "bytes | None" = None) -> subprocess.CompletedProcess:\n'
            '    if "ls-files" in args:\n'
            '        return subprocess.CompletedProcess(args, 0, b"", b"")  # M1: hides the index\n', 1)

    emit("=== M1 the discriminating tree ===")
    emit("a.txt: same-size byte forge with the index stat rewritten (KF1 class)")
    emit("nest: gitlink whose nested repo commit moved, index entry skip-worktree (KG1 class)")
    emit("")
    for label, tool in (("BASE (r86 lane-base bytes)", BASE), ("FILED (r86 repair)", TOOL)):
        for wlabel, patcher in (("honest writer", None),
                                ("writer whose _flag_refusal returns \"\"", patch_empty),
                                ("writer whose git() hides the index from the sweep", patch_git_empty)):
            td = os.path.join(d, "t_%s_%s" % (label.split()[0], abs(hash(wlabel)) % 10000))
            os.makedirs(td, exist_ok=True)
            wsrc = open(WRITER, encoding="utf-8").read()
            w = os.path.join(td, "souji-receipt-write.py")
            open(w, "w", encoding="utf-8").write(patcher(wsrc) if patcher else wsrc)
            os.chmod(w, 0o755)
            t = tool_copy(td, tool_src=tool)
            p = run_tool(t, repo, rev)
            rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
            emit("  %-30s %-46s k4_rows=%d %s" % (
                label, wlabel, len(rows), (rows[0].split("\t")[3] if rows else "(SILENT)")))
    emit("")
    emit("VERDICT M1: the FILED tool's index-flag verdict is routed through the writer, so a")
    emit("writer that declines to refuse (or hides the index from the sweep) silences the NEW")
    emit("check while the BASE tool's independent check still fires. The repair widens the")
    emit("blast radius of an unpinned writer from one function to three.")


def m2_empty_message_is_read_as_clean():
    """The precise code shape: `msg = mod._flag_refusal(...)` then `print('CLEAN' if not msg ...)`.
    A falsy refusal message is read as 'nothing concealed'."""
    emit("=== M2 the code shape that turns a refusal into CLEAN ===")
    import re
    filed = open(TOOL, encoding="utf-8").read()
    seg = re.search(r"if not msg:\n(.*?)\n    print\('CLEAN'.*?\n", filed, re.S).group(0)
    for ln in seg.split("\n"):
        emit("  " + ln)
    emit("")
    emit("  -> `_flag_refusal` is assigned to `msg` and `msg` is tested for TRUTH, not for")
    emit("     NON-NONE. An empty refusal string is indistinguishable from 'no concealment'.")
    emit("     The base tool's `print('CLEAN' if not msg else ...)` had the same shape, but its")
    emit("     `msg` came from `_truth_refusal`, whose contract is None-or-message. The r86")
    emit("     repair routes a SECOND function's return value through that same truth test.")


def m3_no_truthiness_guard():
    """Is there any guard that the sweep actually found a non-H record?"""
    emit("=== M3 the sweep's own control flow ===")
    import re
    filed = open(TOOL, encoding="utf-8").read()
    seg = re.search(r"    for rec in fl\.stdout\.split.*?print\('CLEAN'.*?\n", filed, re.S).group(0)
    for ln in seg.split("\n"):
        emit("  " + ln)
    emit("")
    emit("  -> the loop BREAKS on the first non-H record and assigns msg = refusal; if the")
    emit("     refusal is falsy the loop's finding is discarded and CLEAN is printed.")


if __name__ == "__main__":
    for fn in (m1_discriminating, m2_empty_message_is_read_as_clean, m3_no_truthiness_guard):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-M.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
