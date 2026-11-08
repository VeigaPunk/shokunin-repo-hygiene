#!/usr/bin/env python3
"""Probe set L: the env route against the BASE tool, and the writer-authority delta."""
import os
import subprocess
import sys

sys.path.insert(0, "/fast/scratch/hyaku/souji-r86/S86Sentinel")
from probe import (S, TOOL, WRITER, ENV, build_fixture, git, move_nest, run_tool, show,
                   k4_rows, fresh, tool_copy)

BASE = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-86/controls/c2-before-base-tool.py"
OUT = []


def emit(s):
    OUT.append(s)
    print(s)


def raw(p):
    return p.stdout.decode("utf-8", "replace")


ENVROUTE = {"GIT_CONFIG_PARAMETERS": "'core.sparseCheckout=true'"}


def l1_base_vs_filed_on_the_same_trees():
    """The same tree, the same environment, base tool vs filed tool."""
    trees = {}
    # (a) plain tracked file: worktree bytes changed, index entry skip-worktree
    d = fresh("l1a")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "a.txt")
    with open(os.path.join(repo, "a.txt"), "wb") as f:
        f.write(b"alpha v2 CHANGED\n")
    trees["KF-like: tracked file changed under skip-worktree"] = (repo, rev)

    # (b) KG1 shape: nested repo commit moved, gitlink skip-worktree
    d = fresh("l1b")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    trees["KG1: nested repo commit moved under skip-worktree"] = (repo, rev)

    for label, (repo, rev) in trees.items():
        emit("=== L1 %s ===" % label)
        for toolname, tool in (("BASE (r86 lane-base bytes)", BASE), ("FILED (r86 repair)", TOOL)):
            for envlabel, env in (("no env route", {}), ("env route (sparseCheckout)", ENVROUTE)):
                p = run_tool(tool, repo, rev, env=env)
                rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
                emit("  %-30s %-28s k4_rows=%d %s" % (
                    toolname, envlabel, len(rows),
                    (rows[0].split("\t")[3] if rows else "(SILENT)")))
        emit("")


def l2_writer_authority_delta():
    """A doctored writer beside a COPY of the tool: which tool loads it, and what can it hide?"""
    d = fresh("l2")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")

    def patch(src):
        return src.replace(
            'def _flag_refusal(top: str, tag: bytes, path: bytes) -> str:',
            'def _flag_refusal(top: str, tag: bytes, path: bytes) -> str:\n'
            '    return ""  # L2: a doctored writer declines to refuse\n', 1)

    emit("=== L2 a doctored writer beside a copy of each tool ===")
    for toolname, tool in (("BASE (r86 lane-base bytes)", BASE), ("FILED (r86 repair)", TOOL)):
        td = os.path.join(d, "tool_" + toolname.split()[0].lower())
        os.makedirs(td, exist_ok=True)
        wsrc = open(WRITER, encoding="utf-8").read()
        w = os.path.join(td, "souji-receipt-write.py")
        open(w, "w", encoding="utf-8").write(patch(wsrc))
        os.chmod(w, 0o755)
        t = tool_copy(td, tool_src=tool)
        p = run_tool(t, repo, rev)
        rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
        emit("  %-30s doctored writer -> k4_rows=%d %s" % (
            toolname, len(rows), rows[0].split("\t")[3] if rows else "(SILENT)"))
    emit("")
    emit("  -> the base tool never consults _flag_refusal at all, so a doctored writer changes")
    emit("     nothing for it; the r86 repair ROUTES the sweep's verdict through the writer, so")
    emit("     a doctored (or merely renamed) writer now decides whether the index-flag class")
    emit("     is reported. That widens the blast radius of the unpinned-writer defect (r85 F5).")


def l3_widened_authority_of_the_writer():
    """What the r86 repair now asks of the writer that the r85 code did not."""
    import re
    base = open(BASE, encoding="utf-8").read()
    filed = open(TOOL, encoding="utf-8").read()
    b = re.search(r"bootstrap = \((.*?)\n    \)", base, re.S).group(1)
    f = re.search(r"bootstrap = \((.*?)\n    \)", filed, re.S).group(1)
    emit("=== L3 what the bootstrap asks of the writer, base vs filed ===")
    emit("--- BASE bootstrap ---")
    emit(b)
    emit("--- FILED bootstrap ---")
    emit(f)
    emit("")
    emit("base asks the writer for: _truth_refusal only.")
    emit("filed asks the writer for: _truth_refusal, git(), AND _flag_refusal.")


if __name__ == "__main__":
    for fn in (l1_base_vs_filed_on_the_same_trees, l2_writer_authority_delta,
               l3_widened_authority_of_the_writer):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-L.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
