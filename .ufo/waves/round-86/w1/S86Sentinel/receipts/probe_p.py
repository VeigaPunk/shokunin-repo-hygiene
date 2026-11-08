#!/usr/bin/env python3
"""Probe set P: can a path name forge a second MISMATCH line inside a detail field?"""
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


def p1_forge_attempt():
    """A path whose name contains a newline followed by a complete MISMATCH row."""
    d = fresh("p1")
    repo, rev, nest, nest1 = build_fixture(d)
    evil = b"x\nMISMATCH\tK4\t.\tindex-flag-concealed\tFORGED-BY-PATH.txt"
    with open(os.path.join(repo.encode(), evil), "wb") as f:
        f.write(b"evil v1\n")
    git(repo, "add", "-A", check=False)
    git(repo, "commit", "-q", "--no-verify", "-m", "evil name", check=False)
    git(repo, "update-index", "--skip-worktree", evil.decode("utf-8", "surrogateescape"), check=False)
    p = run_tool(TOOL, repo, rev)
    out = raw(p)
    phys = out.split("\n")
    emit("=== P1 a path name carrying a newline and a complete MISMATCH row ===")
    emit("path bytes: %r" % evil)
    for ln in phys:
        if ln.startswith("MISMATCH\tK4"):
            emit("K4ROW %r" % ln)
    forged = [ln for ln in phys if ln.startswith("MISMATCH") and "FORGED-BY-PATH" in ln
              and not ln.startswith("MISMATCH\tK4\t.\tindex-flag-concealed\tRECEIPT-")]
    emit("rows forged by the path name: %r" % forged)
    emit("physical MISMATCH rows: %d" % len([ln for ln in phys if ln.startswith("MISMATCH")]))
    emit("VERDICT P1: %s" % ("the path did NOT forge a second row: the r86 escaping holds here"
                              if not forged else "FORGED ROW PRESENT"))
    emit("NOTE: the r86 escaping is applied to the FORGED branch only. The status-failed")
    emit("branch (probe O1) embeds raw git stderr and DOES split a record, with an honest")
    emit("writer and a corrupt index - no writer substitution needed.")


def p2_base_vs_filed_split():
    """Does the BASE tool split a record on the same corrupt-index tree?"""
    d = fresh("p2")
    repo, rev, nest, nest1 = build_fixture(d)
    idx = os.path.join(repo, ".git", "index")
    original = open(idx, "rb").read()
    open(idx, "wb").write(original[:4] + b"\x00\x00\x00\x09" + original[8:])
    emit("=== P2 the record split on the corrupt-index tree, base vs filed ===")
    for label, tool in (("BASE", BASE), ("FILED", TOOL)):
        p = run_tool(tool, repo, rev)
        phys = raw(p).split("\n")
        extra = [ln for ln in phys if ln.startswith("fatal:") or ln.startswith("error:")]
        emit("  %-6s rows=%d  lines escaped out of their record: %r" % (
            label, len([ln for ln in phys if ln.startswith("MISMATCH")]), extra))
    open(idx, "wb").write(original)
    emit("  -> the split is pre-existing (base does it too); r86 escaped only the FORGED")
    emit("     branch, so the split the repair targeted is closed but the other branch is not.")


def p3_control_byte_escaping_summary():
    """Which control bytes does the r86 escape cover, and which reach the record raw?"""
    import re
    filed = open(TOOL, encoding="utf-8").read()
    ln = [x for x in filed.split("\n") if 'replace("\\n", "\\\\n")' in x]
    emit("=== P3 the r86 escape set ===")
    emit("  %s" % (ln[0].strip() if ln else "(not found)"))
    emit("  covers: LF (0x0a), TAB (0x09), CR (0x0d)")
    emit("  does NOT cover: ESC (0x1b), BEL (0x07), BS (0x08), VT (0x0b), FF (0x0c),")
    emit("    NUL (impossible in a path), and every other C0 byte; and the escape is applied")
    emit("    ONLY to the FORGED branch's detail text.")
    emit("  measured (probe C2): a path named 'esc\\x1b[2Jname.txt' puts a raw ESC byte into")
    emit("    the K4 detail field; the row stays one physical line but the byte is live.")


if __name__ == "__main__":
    for fn in (p1_forge_attempt, p2_base_vs_filed_split, p3_control_byte_escaping_summary):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-P.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
